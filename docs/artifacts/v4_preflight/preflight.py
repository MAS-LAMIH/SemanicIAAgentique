import json,pathlib,subprocess,time,threading,http.server,sys,hashlib
P=pathlib.Path('/workspace/v4-preflight-evidence'); W=P/'worker';S=P/'sibling';E=P/'evaluator-private'
for d in (W,S,E): d.mkdir(exist_ok=True)
(W/'submission.json').write_text('{"answer":42}')
(S/'canary').write_text('SIBLING_SYNTHETIC')
(E/'canary').write_text('PRIVATE_SYNTHETIC')
(W/'outside-link').symlink_to(E/'canary') if not (W/'outside-link').is_symlink() else None
D=['env','-u','DOCKER_HOST','-u','DOCKER_CONTEXT','-u','DOCKER_TLS','-u','DOCKER_TLS_VERIFY','-u','DOCKER_CERT_PATH','docker','--host=unix:///var/run/docker.sock']
image='python@sha256:6b25cbe6577518889d553cdd5a5da97d259348d8f6e45b527dd731caaba27a07'
common=['run','--rm','--network=none','--read-only','--cap-drop=ALL','--security-opt=no-new-privileges','--user=1000:1000','--pids-limit=64','--memory=128m','--cpus=1','--tmpfs=/tmp:rw,noexec,nosuid,size=16m']
code='''import pathlib,json,socket
paths=%r
out={}
for p in paths:
 try: out[p]={'readable':True,'value':pathlib.Path(p).read_text()}
 except OSError as e: out[p]={'readable':False,'error':type(e).__name__}
s=socket.socket(socket.AF_UNIX)
try: s.connect('/var/run/docker.sock'); out['socket_connect']=True
except OSError as e: out['socket_connect']=type(e).__name__
pathlib.Path('/submission/worker-result.json').write_text(json.dumps({'status':'synthetic_ok'}))
print(json.dumps(out))
''' % ['/submission/submission.json',str(S/'canary'),str(E/'canary'),str(W/'submission.json'),'/submission/outside-link','/var/run/docker.sock','/proc/1/root'+str(E/'canary')]
cmd=D+common+['--mount',f'type=bind,src={W},dst=/submission',image,'python','-c',code]
t=time.monotonic();r=subprocess.run(cmd,capture_output=True,text=True)
(P/'container-test.json').write_text(json.dumps({'command':cmd,'exit_code':r.returncode,'elapsed_seconds':time.monotonic()-t,'stdout':r.stdout,'stderr':r.stderr},indent=2))
# Separate evaluator receives submission read-only; private artifacts never mounted to worker.
code2="import pathlib,json; p=pathlib.Path('/private'); a=json.loads(pathlib.Path('/submission/submission.json').read_text()); (p/'native-evidence.json').write_text(json.dumps({'synthetic_correct':a['answer']==42})); print('evaluation completed')"
r2=subprocess.run(D+common+['--mount',f'type=bind,src={W},dst=/submission,readonly','--mount',f'type=bind,src={E},dst=/private',image,'python','-c',code2],capture_output=True,text=True)
(P/'evaluator-test.json').write_text(json.dumps({'exit_code':r2.returncode,'stdout':r2.stdout,'stderr':r2.stderr,'private_artifact_exists':(E/'native-evidence.json').exists()},indent=2))
# Retry same worker probe after private artifact creation.
r3=subprocess.run(cmd,capture_output=True,text=True)
(P/'worker-recheck.json').write_text(json.dumps({'exit_code':r3.returncode,'stdout':r3.stdout,'stderr':r3.stderr},indent=2))
# Independent synthetic HTTP service demonstrates mutation surviving caller termination.
class H(http.server.BaseHTTPRequestHandler):
 def do_POST(self):
  time.sleep(.6);(E/'late-mutation.json').write_text('{"mutated":true}')
  self.send_response(200);self.end_headers()
 def log_message(self,*a): pass
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=srv.serve_forever,daemon=True).start()
client="import urllib.request; urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:%d',data=b'x'))"%srv.server_port
t=time.monotonic();rr=subprocess.run(['timeout','--kill-after=1s','0.2s',sys.executable,'-c',client],capture_output=True,text=True);elapsed=time.monotonic()-t
time.sleep(.8);srv.shutdown();srv.server_close()
(P/'timeout-test.json').write_text(json.dumps({'client_exit_code':rr.returncode,'client_elapsed_seconds':elapsed,'server_mutated_after_timeout':(E/'late-mutation.json').exists(),'scope':'synthetic HTTP; not a model cancellation test'},indent=2))
print((P/'container-test.json').read_text());print((P/'evaluator-test.json').read_text());print((P/'timeout-test.json').read_text())
