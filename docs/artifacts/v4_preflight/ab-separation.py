import pathlib,subprocess,json,time,shutil
P=pathlib.Path('/workspace/v4-preflight-evidence'); F=P/'visible-fixture-copy';(F/'semantic_action').mkdir(parents=True,exist_ok=True)
(F/'semantic_action/__init__.py').write_text('')
for n in ('artifact.py','provider_b.py','model.py'): shutil.copyfile(pathlib.Path('/workspace/SemanicIAAgentique/src/semantic_action')/n,F/'semantic_action'/n)
shutil.copyfile('/workspace/SemanicIAAgentique/v4_pilot/native.py',F/'native.py')
server='''import sys,json,time,pathlib
from dataclasses import asdict
from semantic_action.artifact import Scenario,serve
from semantic_action.provider_b import BookingScenario,serve_bookings
from native import capture,initial_records,adjudicate
p=sys.argv[1]; root=pathlib.Path('/private'); state=Scenario(events=initial_records('a')) if p=='a' else BookingScenario(items=initial_records('b'))
with (serve(state) if p=='a' else serve_bookings(state)) as (url,state):
 before=capture(p,state); (root/'ready.json').write_text(json.dumps({'url':url}))
 for _ in range(200):
  if pathlib.Path('/submission/done.json').exists(): break
  time.sleep(.05)
 else: raise RuntimeError('worker did not finish')
 result=json.loads(pathlib.Path('/submission/done.json').read_text()); after=capture(p,state)
 values={'start_time':'2030-01-07T10:00:00+00:00','end_time':'2030-01-07T11:00:00+00:00','title':'Synthetic preflight'}
 (root/'evidence.json').write_text(json.dumps({'before':asdict(before),'after':asdict(after),'verdict':adjudicate(before,after,values,result)}))
'''
(F/'server.py').write_text(server)
D=['env','-u','DOCKER_HOST','-u','DOCKER_CONTEXT','-u','DOCKER_TLS','-u','DOCKER_TLS_VERIFY','-u','DOCKER_CERT_PATH','docker','--host=unix:///var/run/docker.sock']; image='python@sha256:6b25cbe6577518889d553cdd5a5da97d259348d8f6e45b527dd731caaba27a07'
flags=['--read-only','--cap-drop=ALL','--security-opt=no-new-privileges','--user=1000:1000','--pids-limit=64','--memory=128m','--tmpfs=/tmp:rw,noexec,nosuid,size=16m']
results=[]
for p in ('a','b'):
 w=P/f'ab-{p}-submission';e=P/f'ab-{p}-private';w.mkdir();e.mkdir();name=f'v4-preflight-evaluator-{p}'
 cmd=D+['run','-d','--name',name,'--network=none']+flags+['--mount',f'type=bind,src={F},dst=/fixtures,readonly','--mount',f'type=bind,src={e},dst=/private','--mount',f'type=bind,src={w},dst=/submission,readonly','-w','/fixtures',image,'python','-B','server.py',p]
 started=subprocess.run(cmd,capture_output=True,text=True)
 try:
  for _ in range(100):
   if (e/'ready.json').exists(): break
   time.sleep(.05)
  url=json.loads((e/'ready.json').read_text())['url']
  body={'start_time':'2030-01-07T10:00:00+00:00','end_time':'2030-01-07T11:00:00+00:00','title':'Synthetic preflight'} if p=='a' else {'begins_ms':1894010400000,'finishes_ms':1894014000000,'label':'Synthetic preflight'}
  code="import urllib.request,json,pathlib; data=json.loads(%r); r=json.load(urllib.request.urlopen(urllib.request.Request(%r,data=json.dumps(data).encode(),headers={'Content-Type':'application/json'}))); pathlib.Path('/submission/done.json').write_text(json.dumps({'output':{'id':r[%r]}})); print(json.dumps({'private_path_visible':pathlib.Path('/private/evidence.json').exists(),'docker_socket_visible':pathlib.Path('/var/run/docker.sock').exists()}))"%(json.dumps(body),url+('/events' if p=='a' else '/bookings'),'id' if p=='a' else 'booking_ref')
  worker=subprocess.run(D+['run','--rm','--network=container:'+name]+flags+['--mount',f'type=bind,src={w},dst=/submission',image,'python','-c',code],capture_output=True,text=True)
  waited=subprocess.run(D+['wait',name],capture_output=True,text=True)
  results.append({'provider':p,'worker_exit':worker.returncode,'worker_stdout':worker.stdout,'worker_stderr':worker.stderr,'evaluator_exit':waited.stdout.strip(),'verdict':json.loads((e/'evidence.json').read_text())['verdict']})
 finally:
  subprocess.run(D+['logs',name],stdout=(e/'server.log').open('w'),stderr=subprocess.STDOUT);subprocess.run(D+['rm','-f',name],capture_output=True)
(P/'ab-separation-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
