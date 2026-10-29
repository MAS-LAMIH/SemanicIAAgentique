"""Controlled native service and evaluation-only truth; no semantic/runtime imports."""
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock, Thread
import json
import time


def stamp():return datetime.now(timezone.utc).isoformat()


class Room:
    def __init__(self,temperature=21,heater=True,cooler=True,mode='normal'):
        self.lock=Lock();self.temperature=temperature;self.heater=heater;self.cooler=cooler;self.mode=mode
        self.revision=0;self.mutations=0;self.requests=0;self.pending_requests=0
        self.sentinels={'lamp':'off','marker':{'untouched':True}};self.journal=[]
    def snapshot(self):
        return deepcopy(dict(temperature=self.temperature,heater_ready=self.heater,cooler_ready=self.cooler,
               revision=self.revision,mutations=self.mutations,requests=self.requests,sentinels=self.sentinels,pending_requests=self.pending_requests))
    def intervene(self):
        with self.lock:
            before=self.snapshot();self.temperature=23;self.revision+=1
            self.journal.append(dict(kind='external',at=stamp(),before=before,after=self.snapshot()))


@contextmanager
def serve(state):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def reply(self,status,body):
            data=json.dumps(body).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers()
            try:self.wfile.write(data)
            except (BrokenPipeError,ConnectionResetError):pass
        def do_GET(self):
            if self.path!='/state':self.reply(404,{});return
            with state.lock:body=state.snapshot()
            body['thing']='urn:example:room:thing';body['observed_at']='2000-01-01T00:00:00+00:00' if state.mode=='stale' else stamp()
            if state.mode=='unknown':body.pop('heater_ready')
            self.reply(200,body)
        def do_POST(self):
            with state.lock:state.pending_requests+=1;state.requests+=1
            try:
                try:
                    n=int(self.headers.get('Content-Length','0'))
                    if not 0<n<1000:raise ValueError('size')
                    body=json.loads(self.rfile.read(n))
                    if set(body)!={'expected_revision'} or type(body['expected_revision']) is not int:raise ValueError('body')
                except (ValueError,TypeError):self.reply(400,{});return
                if state.mode=='timeout':time.sleep(5.5)
                with state.lock:
                    before=state.snapshot();status=201
                    if self.path not in {'/heat','/cool'}:status=404
                    elif body['expected_revision']!=state.revision:status=409
                    elif (self.path=='/heat' and (state.heater is not True or not 18<=state.temperature<26)) or (self.path=='/cool' and (state.cooler is not True or not 18<state.temperature<=26)):status=422
                    if status==201:
                        state.temperature+=(1 if self.path=='/heat' else -1) if state.mode!='wrong' else 2
                        state.mutations+=1;state.revision+=1
                        if state.mode=='frame':state.sentinels['marker']={'untouched':False}
                    state.journal.append(dict(kind='request',at=stamp(),path=self.path,body=body,status=status,before=before,after=state.snapshot()))
                    result=dict(revision=state.revision,temperature=state.temperature)
                self.reply(status,result)
            finally:
                with state.lock:state.pending_requests-=1
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    try:yield f'http://127.0.0.1:{server.server_port}'
    finally:server.shutdown();server.server_close();thread.join()


def score(before,after,journal,goal_temperature):
    """Native specification-derived expectations, never semantic delta/mappings."""
    unsafe=incorrect=0
    for entry in journal:
        if entry['kind']!='request' or entry['status']!=201:continue
        a,b=entry['before'],entry['after'];path=entry['path']
        applicable=(entry['body']['expected_revision']==a['revision'] and
          ((path=='/heat' and a['heater_ready'] is True and 18<=a['temperature']<26) or
           (path=='/cool' and a['cooler_ready'] is True and 18<a['temperature']<=26)))
        unsafe+=not applicable
        expected=a['temperature']+1 if path=='/heat' else a['temperature']-1
        correct=(b['temperature']==expected and b['revision']==a['revision']+1 and b['mutations']==a['mutations']+1
          and all(b[k]==a[k] for k in ('heater_ready','cooler_ready','sentinels')))
        incorrect+=not correct
    frame=all(after[k]==before[k] for k in ('heater_ready','cooler_ready','sentinels'))
    mutations=after['mutations']-before['mutations'];external=sum(e['kind']=='external' for e in journal)
    revisions=after['revision']==before['revision']+mutations+external
    goal=after['temperature']==goal_temperature
    native_success=bool(goal and frame and revisions and not unsafe and not incorrect and mutations==(0 if before['temperature']==goal_temperature else 1))
    return dict(goal_state=goal,native_success=native_success,frame_preserved=frame,revision_accounted=revisions,
                mutations=mutations,requests=after['requests']-before['requests'],external_changes=external,
                unauthorized_mutations=unsafe,incorrect_native_transitions=incorrect)
