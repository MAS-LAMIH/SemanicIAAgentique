"""Condition A: explicitly selected provider-local operations, no semantic registry.

Source provenance: authored with the controlled fixture specifications and prior
shared manuals visible. This is a functional baseline, not blind independent
annotation. Provider validators/encoders are deliberately local implementations.
"""
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from uuid import uuid4

from .model import Observation, Truth, instant, now
from .oracle import current, verify
from .transport import HTTPTransport


def _object(pairs):
    result = {}
    for key,value in pairs:
        if key in result:
            raise ValueError('Duplicate local contract key')
        result[key]=value
    return result


def _bad_number(value):
    raise ValueError('Nonfinite local contract number '+value)


class CalendarLocal:
    provider = 'calendar'
    operation = 'create_event'
    encoding = 'iso'
    create_path = '/events'
    permission_path = '/calendar'
    state_path = '/events'
    item_path = '/events/{id}'

    def __init__(self,path):
        self.path=Path(path)
        self.description=json.loads(self.path.read_text(),object_pairs_hook=_object,parse_constant=_bad_number)
        data=self.description
        keys={'version','provider','operation','effect','encoding','preserves_others',
              'max_evidence_age_seconds','output_fields','authoring_provenance'}
        if not isinstance(data,dict) or set(data)!=keys:
            raise ValueError('Incomplete/unsupported provider-local description')
        age=data['max_evidence_age_seconds']
        if (type(data['version']) is not int or data['version']!=1 or data['provider']!=self.provider
            or type(data['preserves_others']) is not bool or type(age) not in (int,float)
            or not math.isfinite(age) or not 0<age<=300):
            raise ValueError('Invalid provider-local contract values')
        fields=data['output_fields']
        if not isinstance(fields,dict) or set(fields)!={'id','start_time','end_time','title'}:
            raise ValueError('Incomplete provider-local observation map')
        if any(not isinstance(v,str) or not v.isidentifier() for v in fields.values()):
            raise ValueError('Unsupported provider-native output field')
        if any(not isinstance(data[k],str) or not data[k] for k in ('operation','effect','encoding','authoring_provenance')):
            raise ValueError('Invalid local operation description')

    def validate(self,goal,inputs):
        errors=[]
        if self.description['operation']!=self.operation:
            errors.append('Unsupported local operation')
        if self.description['effect']!='stores_requested_event':
            errors.append('Local effect cannot meet event goal')
        if self.description['encoding']!=self.encoding:
            errors.append('Unsupported local input encoding')
        if goal.forbid_other_changes and not self.description['preserves_others']:
            errors.append('Local operation cannot guarantee preservation')
        if not isinstance(inputs,dict) or set(inputs)!={'start_time','end_time','title'}:
            return errors+['Exactly three event inputs required']
        if not isinstance(inputs['title'],str) or not 0<len(inputs['title'].strip())<=500:
            errors.append('Invalid event title')
        try:
            if instant(inputs['end_time'])<=instant(inputs['start_time']):
                errors.append('Invalid event interval')
        except (ValueError,TypeError):
            errors.append('Timezone-aware input times required')
        return errors

    def encode(self,inputs):
        return dict(inputs)

    def event(self,item):
        return {target:item[source] for target,source in self.description['output_fields'].items()}

    def state(self,body):
        return {'writable':body.get('writable'),'events':{k:self.event(v) for k,v in body['events'].items()},
                'revision':body.get('revision'),'observed_at':body.get('observed_at')}

    def observation(self,body):
        return {'event':self.event(body['event']) if body.get('event') else None,
                'revision':body.get('revision'),'observed_at':body.get('observed_at')}

    def response_id(self,body):
        return body.get('id')


class BookingLocal(CalendarLocal):
    provider = 'booking'
    operation = 'reserveAppointment'
    encoding = 'integer_milliseconds'
    create_path = '/bookings'
    permission_path = '/availability'
    state_path = '/bookings'
    item_path = '/booking/{id}'

    @staticmethod
    def milliseconds(value):
        delta=instant(value)-datetime(1970,1,1,tzinfo=timezone.utc)
        microseconds=(delta.days*86400+delta.seconds)*1000000+delta.microseconds
        if microseconds%1000:
            raise ValueError('Local booking conversion would lose submillisecond precision')
        return microseconds//1000

    def validate(self,goal,inputs):
        errors=super().validate(goal,inputs)
        if errors:
            return errors
        try:
            start,end=self.milliseconds(inputs['start_time']),self.milliseconds(inputs['end_time'])
            if start%900000 or end%900000:
                errors.append('Booking requires UTC quarter-hour boundaries')
            if end-start>7200000:
                errors.append('Booking exceeds two-hour duration')
        except (ValueError,TypeError,OverflowError) as error:
            errors.append(str(error))
        return errors

    def encode(self,inputs):
        return {'begins_ms':self.milliseconds(inputs['start_time']),
                'finishes_ms':self.milliseconds(inputs['end_time']),'label':inputs['title']}

    def event(self,item):
        from datetime import timedelta
        values=super().event(item)
        for key in ('start_time','end_time'):
            if type(values[key]) is not int:
                raise ValueError('Booking observation requires integer milliseconds')
            values[key]=(datetime(1970,1,1,tzinfo=timezone.utc)+timedelta(milliseconds=values[key])).isoformat()
        return values

    def state(self,body):
        return {'writable':body.get('can_book'),'events':{k:self.event(v) for k,v in body['items'].items()},
                'revision':body.get('version'),'observed_at':body.get('sampled_at')}

    def observation(self,body):
        return {'event':self.event(body['booking']) if body.get('booking') else None,
                'revision':body.get('version'),'observed_at':body.get('sampled_at')}

    def response_id(self,body):
        return body.get('booking_ref')


class LocalExecutor(HTTPTransport):
    """Neutral transport/oracle reuse only; provider is explicitly chosen by caller."""
    def run(self,local,goal,inputs,trace_path):
        target=Path(trace_path)
        target.parent.mkdir(parents=True,exist_ok=True)
        # Reserve evidence before mutation; callers must use new run directories.
        with target.open('x',encoding='utf-8') as stream:
            trace={'schema_version':1,'condition':'A','run_id':str(uuid4()),'timestamp':now(),
                   'operation_id':local.description['operation'],'formal_goal':goal.to_dict(),'inputs':inputs,
                   'description_sha256':hashlib.sha256(local.path.read_bytes()).hexdigest(),
                   'compatible':False,'applicability':Truth.UNKNOWN,'execution_decision':'REJECT',
                   'api_call_success':False,'api_response':None,'oracle_verdict':None,
                   'observed_state_change':None,'preconditions':[],'wire_evidence':[],'reason':None}
            def request(method,path,body=None):
                response=self._http_request(method,path,body)
                trace['wire_evidence'].append({'method':method,'path':path,'request_body':body,**asdict(response)})
                return response
            try:
                errors=local.validate(goal,inputs)
                if errors:
                    trace['reason']='; '.join(errors)
                    return trace
                trace['compatible']=True
                baseline=request('GET',local.permission_path)
                try:
                    evidence=local.state(baseline.body) if baseline.success else None
                except (KeyError,TypeError,ValueError,OverflowError):
                    evidence=None
                age=local.description['max_evidence_age_seconds']
                if not current(evidence,age):
                    verdict=Truth.UNKNOWN
                elif evidence.get('writable') is True:
                    verdict=Truth.TRUE
                elif evidence.get('writable') is False:
                    verdict=Truth.FALSE
                else:
                    verdict=Truth.UNKNOWN
                trace['preconditions']=[{'name':'positive_interval','verdict':Truth.TRUE},
                                        {'name':'local_write_permission','verdict':verdict,'evidence':evidence}]
                trace['applicability']=verdict
                if verdict!=Truth.TRUE:
                    trace['execution_decision']='BLOCK' if verdict==Truth.UNKNOWN else 'REJECT'
                    trace['reason']='Local write permission not established TRUE'
                    return trace
                trace['execution_decision']='EXECUTE'
                trace['execution_started']=now()
                response=request('POST',local.create_path,local.encode(inputs))
                trace['api_response']=asdict(response)
                trace['api_call_success']=response.success
                event_id=local.response_id(response.body)
                if not isinstance(event_id,str) or not event_id or not all(c.isascii() and (c.isalnum() or c in '-_') for c in event_id):
                    event= None
                    error='No valid returned identifier'
                else:
                    result=request('GET',local.item_path.replace('{id}',event_id))
                    event=local.observation(result.body) if result.success else None
                    error=result.error
                result=request('GET',local.state_path)
                state=local.state(result.body) if result.success else None
                if not all(current(item,age,trace['execution_started']) for item in (event,state)):
                    error=error or 'Insufficient local observation evidence'
                observation=Observation(event,state,error or result.error)
                trace['observed_effects']=asdict(observation)
                trace['observed_state_change']=(evidence['events']!=state['events'] if current(state,goal.max_evidence_age_seconds,trace['execution_started']) else None)
                trace['oracle_verdict']=asdict(verify(goal,evidence,observation,event_id,trace['execution_started']))
                return trace
            except (ValueError,TypeError,KeyError,OSError,OverflowError) as error:
                trace['reason']=str(error)
                return trace
            finally:
                trace['completed_at']=now()
                json.dump(trace,stream,indent=2,sort_keys=True)
                stream.write('\n')
