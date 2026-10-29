"""Same-author virtual cabinet, implementing the separately committed native specification."""
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
from threading import Lock,Thread
import time

def stamp():return datetime.now(timezone.utc).isoformat()
class Cabinet:
    def __init__(self,secured=False,ready=True,mode='normal'):
        self.lock=Lock();self.secured=secured;self.door_closed=True;self.ready=ready;self.mode=mode
        self.generation=self.writes=self.requests=self.pending_requests=0
        self.unrelated={'asset':'manual','marker':{'untouched':True}};self.journal=[]
    def snapshot(self):return deepcopy(dict(secured=self.secured,door_closed=self.door_closed,ready=self.ready,generation=self.generation,writes=self.writes,requests=self.requests,pending_requests=self.pending_requests,unrelated=self.unrelated))
    def intervene(self,revision_only=False):
        with self.lock:
            before=self.snapshot();self.generation+=1
            if not revision_only:self.door_closed=False
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
            if self.path!='/cabinet/status':self.reply(404,{});return
            with state.lock:
                b=dict(identity='urn:example:cabinet:thing',evidence={'time':'2000-01-01T00:00:00+00:00' if state.mode=='stale' else stamp()},latch={'secured':state.secured},interlocks={'door_closed':state.door_closed,'ready':state.ready},audit={'generation':state.generation,'writes':state.writes,'unrelated':deepcopy(state.unrelated)})
                if state.mode=='unknown':b['interlocks'].pop('ready')
            self.reply(200,b)
        def do_PUT(self):
            with state.lock:state.requests+=1;state.pending_requests+=1
            try:
                try:
                    n=int(self.headers.get('Content-Length','0'))
                    if not 0<n<1000:raise ValueError('size')
                    body=json.loads(self.rfile.read(n))
                    if set(body)!={'guard'} or not isinstance(body['guard'],dict) or set(body['guard'])!={'generation'} or type(body['guard']['generation']) is not int:raise ValueError('body')
                except (ValueError,TypeError):self.reply(400,{});return
                if state.mode=='timeout':time.sleep(5.5)
                with state.lock:
                    before=state.snapshot();status=200
                    if self.path not in ('/cabinet/secure','/cabinet/release'):status=404
                    elif body['guard']['generation']!=state.generation:status=409
                    elif state.ready is not True or state.door_closed is not True:status=422
                    if status==200:
                        if state.mode!='wrong':state.secured=self.path=='/cabinet/secure'
                        state.generation+=1;state.writes+=1
                        if state.mode=='frame':state.unrelated['marker']={'untouched':False}
                    state.journal.append(dict(kind='request',path=self.path,body=body,status=status,at=stamp(),before=before,after=state.snapshot()))
                    response=dict(receipt={'generation':state.generation},latch={'secured':state.secured})
                self.reply(status,response)
            finally:
                with state.lock:state.pending_requests-=1
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    try:yield f'http://127.0.0.1:{server.server_port}'
    finally:server.shutdown();server.server_close();thread.join()
