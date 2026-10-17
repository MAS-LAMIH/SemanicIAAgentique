"""Audit retained outputs without rewriting historical files."""
from collections import Counter
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
from .driver import ROOT,save
from .guard import sha,MANIFEST_SHA,CANDIDATE
AREA=ROOT/'docs/artifacts/milestone4_5'
def main():
    start=json.loads((AREA/'start-state.json').read_text())
    changed=[p for p,h in start['preserved_files'].items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    attempts=[]
    for p in sorted(AREA.rglob('evaluation.json')):
        d=json.loads(p.read_text()); summary=d.get('summary',{}); process=d.get('process',{})
        phase=p.relative_to(AREA).parts[0]
        attempts.append(dict(path=str(p.relative_to(ROOT)),phase=phase,task_id=d['task_id'],provider=d['provider'],condition=d['condition'],
            summary=summary,process_status=process.get('status'),pid=process.get('pid'),
            state_uncertain=d.get('recovery',{}).get('state_uncertain',False),
            reset_rejected=d.get('status')=='RESET_REJECTED',subject_launched=d.get('subject_launched',bool(process)),
            diagnostic_passed=d.get('diagnostic_passed',d.get('case_passed')),classification=d.get('classification',d.get('status')),
            files={str(f.relative_to(p.parent)):sha(f) for f in sorted(p.parent.rglob('*')) if f.is_file()}))
    rehearsal=[r for r in attempts if r['phase']=='rehearsal']; refs={ (r['task_id'],r['provider'],r['condition']):r for r in attempts if r['phase']=='reference'}
    differences=[]
    for row in rehearsal:
        key=(row['task_id'],row['provider'],row['condition'])
        if key[0].startswith('D'): expected=refs[key]['summary']
        else: expected=json.loads((ROOT/'docs/artifacts/milestone4_3/pilot-final'/('-'.join(key))/'evaluation.json').read_text())['summary']
        if row['summary']!=expected: differences.append(dict(key=key,actual=row['summary'],expected=expected))
    approvals=json.loads((ROOT/'docs/SCIENTIFIC_FREEZE_DECISION_V3.json').read_text())
    pending=all(g['status']=='pending' and g['signature'] is None for g in approvals['gates'].values())
    commands={p.stem:json.loads(p.read_text()) for p in AREA.glob('*.json') if isinstance(json.loads(p.read_text()),dict) and 'command' in json.loads(p.read_text())}
    regressions={k:commands['regression-'+k] for k in ('source','wheel','restored')}
    controls=[r for r in attempts if r['phase'] in ('focused','focused-final')]
    safety=dict(reset_rejected=sum(r['reset_rejected'] for r in controls),timeouts=sum(r['process_status']=='TIMEOUT' for r in controls),
                uncertain=sum(r['state_uncertain'] for r in controls),timeout_verified=[r['path'] for r in attempts if (r['process_status']=='TIMEOUT' or r['state_uncertain']) and r['summary'].get('verified')])
    completeness=[]
    for r in rehearsal:
        directory=(ROOT/r['path']).parent
        for name in ('reset.json','supervision.json','subject-input.json','subject.stdout','subject.stderr'):
            if not (directory/name).is_file(): completeness.append(r['path']+': missing '+name)
        reset=json.loads((directory/'reset.json').read_text())
        supervisor=json.loads((directory/'supervision.json').read_text())
        if not reset['passed'] or supervisor['budget_seconds']!=60 or supervisor['process_alive_after_stop']:
            completeness.append(r['path']+': lifecycle check failed')
        if r['summary']['mutation_calls'] and not (directory/'native-transitions.json').is_file(): completeness.append(r['path']+': missing native journal')
    pids=[r['pid'] for r in rehearsal]
    if len(set(pids))!=len(pids): completeness.append('reused subject PID')
    parity=[]
    for t in sorted({r['task_id'] for r in rehearsal}):
        for provider in ('a','b'):
            rows=[r['summary'] for r in rehearsal if r['task_id']==t and r['provider']==provider]
            if len(rows)!=3 or any(x!=rows[0] for x in rows): parity.append([t,provider])
    good=not completeness and not parity and not changed and not differences and len(rehearsal)==180 and all(r['diagnostic_passed'] for r in rehearsal) and pending and not safety['timeout_verified'] and all(r['exit_code']==0 and r['tests_run']==87 for r in regressions.values()) and commands['focused']['exit_code']==0 and commands['focused-final']['exit_code']==0
    result=dict(recorded_at=datetime.now(timezone.utc).isoformat(),started_at=start['started_at'],verdict='PASS' if good else 'BLOCKED',candidate_commit=CANDIDATE,manifest_sha256=MANIFEST_SHA,
        preserved_file_count=len(start['preserved_files']),changed_existing_files=changed,all_approval_gates_pending=pending,
        rehearsal=dict(planned=180,executed=len(rehearsal),rejected_before_launch=sum(r['reset_rejected'] for r in rehearsal),incomplete=180-len(rehearsal),diagnostic_passed=sum(bool(r['diagnostic_passed']) for r in rehearsal),task_kind_counts=dict(Counter('single' if r['task_id'].startswith('D') else 'multi' for r in rehearsal))),
        output_completeness_failures=completeness,condition_parity_differences=parity,fresh_subject_pids=len(set(pids)),
        rehearsal_status_counts=dict(Counter(r['summary'].get('status','single_action') for r in rehearsal)),
        native_runtime_disagreements=[r['path'] for r in rehearsal if r['summary']['native_verified']!=r['summary']['runtime_verified']],
        phase_counts=dict(Counter(r['phase'] for r in attempts)),normalized_differences=differences,safety=safety,
        regressions=regressions,commands=commands,engineering_validation_only=True,human_active_minutes=None,ai_supervision_minutes=None,tool_model_wait_minutes=None,
        independent_provider_units=2,confirmatory_results=False,provider_c_accessed=False,freeze_approved=False,unseal_authorized=False)
    save(AREA/'attempt-inventory.json',dict(attempts=attempts,non_execution_controls=['provider z rejected before directory creation','existing fresh-1 path rejected without overwrite'],missing_evaluation_directories=[str(p.relative_to(ROOT)) for p in AREA.rglob('subject-input.json') if not (p.parent/'evaluation.json').exists()]))
    save(AREA/'verification-results.json',result)
    print(json.dumps({k:result[k] for k in ('verdict','preserved_file_count','rehearsal','phase_counts','safety','normalized_differences')},indent=2))
    if not good: raise SystemExit(1)
if __name__=='__main__':main()
