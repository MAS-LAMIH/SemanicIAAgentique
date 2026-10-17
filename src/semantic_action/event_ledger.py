"""Prospective append-only resource ledger. Historical WorkEntry logs stay untouched.

Advisory file locks serialize cooperating Linux writers; hash chaining detects
accidental edits, not an attacker rewriting an unsigned entire ledger.
"""
from dataclasses import asdict, dataclass, field
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
from uuid import uuid4
from .model import instant

METRICS=('human_active_minutes','ai_supervision_minutes','automated_runtime_minutes',
         'tool_wait_minutes','model_wait_minutes','elapsed_wall_minutes')
ACTIVITIES={'setup','documentation','manual_authoring','mapping','adapter','generic_engine',
            'testing','debugging','maintenance','review','execution'}
SCOPES={'shared_setup','provider_onboarding','task_execution','maintenance','mixed_unallocated'}


@dataclass(frozen=True)
class Event:
    contributor_id: str
    activity: str
    scope: str
    resource_kind: str
    event_id: str = field(default_factory=lambda:str(uuid4()))
    provider_id: str | None = None
    condition_id: str | None = None
    task_id: str | None = None
    started_at: str | None = None
    ended_at: str | None = None
    elapsed_wall_minutes: float | None = None
    human_active_minutes: float | None = None
    ai_supervision_minutes: float | None = None
    automated_runtime_minutes: float | None = None
    tool_wait_minutes: float | None = None
    model_wait_minutes: float | None = None
    attempt_id: str | None = None
    outcome: str | None = None
    rework_of: str | None = None
    supersedes: str | None = None
    correction_reason: str | None = None
    concurrency_group: str | None = None
    ai_model_and_version: str | None = None
    artifact_references: tuple = ()
    mapping_rule_test_counts: dict | None = None
    measurement_source: str | None = None
    missingness_reason: str | None = None


def _digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def _validate(event):
    if not isinstance(event.contributor_id,str) or not event.contributor_id or not event.event_id:
        raise ValueError('Contributor and event IDs required')
    if event.activity not in ACTIVITIES or event.scope not in SCOPES:
        raise ValueError('Unknown activity or scope')
    if event.resource_kind not in {'human','automation','wait','elapsed','note'}:
        raise ValueError('Unknown resource kind')
    if event.condition_id not in {None,'A','B','C'}:
        raise ValueError('Unknown experimental condition')
    for name in METRICS:
        value=getattr(event,name)
        if value is not None and (type(value) not in (int,float) or not math.isfinite(value) or value<0):
            raise ValueError('Invalid measured '+name)
    if event.ai_supervision_minutes is not None and (event.human_active_minutes is None or event.ai_supervision_minutes>event.human_active_minutes):
        raise ValueError('Supervision must be a measured subset of human activity')
    if event.resource_kind!='human' and (event.human_active_minutes is not None or event.ai_supervision_minutes is not None):
        raise ValueError('Automation/wait/elapsed events cannot record human labor')
    if event.resource_kind=='human' and any(getattr(event,k) is not None for k in ('automated_runtime_minutes','tool_wait_minutes','model_wait_minutes')):
        raise ValueError('Record automated/wait resources in separate linked events')
    if (event.started_at is None)!=(event.ended_at is None):
        raise ValueError('Supply both interval endpoints or neither')
    if event.started_at is not None:
        duration=(instant(event.ended_at)-instant(event.started_at)).total_seconds()/60
        if duration<0:
            raise ValueError('Reversed interval')
        if event.human_active_minutes is not None and event.human_active_minutes>duration+1e-8:
            raise ValueError('Active labor exceeds interval')
    elif event.human_active_minutes is not None and event.human_active_minutes>0:
        raise ValueError('Measured active labor requires a timed interval')
    if event.supersedes and not event.correction_reason:
        raise ValueError('Corrections require an explicit reason')
    if not event.measurement_source:
        raise ValueError('Measurement provenance required')


class Ledger:
    def __init__(self,path):
        self.path=Path(path)

    @staticmethod
    def _read(stream):
        stream.seek(0)
        rows=[]
        previous=None
        for line in stream:
            row=json.loads(line)
            record=row['event']
            if row['previous_sha256']!=previous or row['sha256']!=_digest({'event':record,'previous_sha256':previous}):
                raise ValueError('Ledger hash chain is invalid')
            rows.append(row)
            previous=row['sha256']
        return rows

    def records(self):
        if not self.path.exists():
            return []
        with self.path.open() as stream:
            fcntl.flock(stream,fcntl.LOCK_SH)
            return self._read(stream)

    def append(self,event):
        _validate(event)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open('a+',encoding='utf-8') as stream:
            fcntl.flock(stream,fcntl.LOCK_EX)
            rows=self._read(stream)
            events=[r['event'] for r in rows]
            known={e['event_id']:e for e in events}
            if event.event_id in known:
                raise ValueError('Event ID already exists')
            replaced={e['supersedes'] for e in events if e['supersedes']}
            if event.supersedes:
                if event.supersedes not in known or event.supersedes in replaced:
                    raise ValueError('Correction must supersede a current existing record')
                if known[event.supersedes]['contributor_id']!=event.contributor_id:
                    raise ValueError('Correction changes contributor identity')
            if event.rework_of and event.rework_of not in known:
                raise ValueError('Rework must link an existing attempt')
            active=[e for e in events if e['event_id'] not in replaced and e['event_id']!=event.supersedes]
            if event.resource_kind=='human' and (event.human_active_minutes or 0)>0:
                start,end=instant(event.started_at),instant(event.ended_at)
                for other in active:
                    if other['contributor_id']==event.contributor_id and (other['human_active_minutes'] or 0)>0:
                        if max(start,instant(other['started_at']))<min(end,instant(other['ended_at'])):
                            raise ValueError('Overlapping active intervals for the same person')
            previous=rows[-1]['sha256'] if rows else None
            payload={'event':asdict(event),'previous_sha256':previous}
            payload['sha256']=_digest(payload)
            stream.seek(0,2)
            stream.write(json.dumps(payload,sort_keys=True,allow_nan=False)+'\n')
            stream.flush()
            os.fsync(stream.fileno())
            return payload

    def summary(self):
        events=[row['event'] for row in self.records()]
        replaced={e['supersedes'] for e in events if e['supersedes']}
        current=[e for e in events if e['event_id'] not in replaced]
        totals={}
        for metric in METRICS:
            values=[e[metric] for e in current if e[metric] is not None]
            totals[metric]={'measured_total':sum(values) if values else None,
                            'unmeasured_records':sum(e[metric] is None for e in current)}
        return {'record_count':len(events),'current_record_count':len(current),'resources':totals,
                'warning':'Supervision is a subset of human active time; resources overlap wall clock. Missing records do not imply zero.'}
