"""Direct CalDAV feasibility probe; no V4 integration or translation layer."""
import argparse,hashlib,json,pathlib,socket,subprocess,tempfile,time,urllib.request,urllib.error,shutil,sys
from datetime import datetime,timezone


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--python',required=True);parser.add_argument('--output',type=pathlib.Path,required=True);args=parser.parse_args()
 out=args.output;out.mkdir(parents=True,exist_ok=False)
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({})) # loopback only
 records=[]
 uid='radicale-native-preflight-001'
 ics=('BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//V4 Native Feasibility//EN\r\nBEGIN:VEVENT\r\nUID:'+uid+'\r\nDTSTAMP:20300101T000000Z\r\nDTSTART:20300107T100000Z\r\nDTEND:20300107T110000Z\r\nSUMMARY:Native CalDAV event\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n').encode()
 xml=b'<?xml version="1.0" encoding="utf-8"?><C:mkcalendar xmlns:C="urn:ietf:params:xml:ns:caldav" xmlns:D="DAV:"><D:set><D:prop><D:displayname>Native probe</D:displayname><C:supported-calendar-component-set><C:comp name="VEVENT"/></C:supported-calendar-component-set></D:prop></D:set></C:mkcalendar>'
 def request(origin,method,path,body=None,headers=None):
  start=time.monotonic();req=urllib.request.Request(origin+path,data=body,headers=headers or {},method=method)
  try:response=opener.open(req,timeout=5)
  except urllib.error.HTTPError as e:response=e
  with response:status=response.status;data=response.read();h=dict(response.headers)
  records.append(dict(method=method,path=path,request_headers=headers or {},request_body=body.decode() if body else None,status=status,response_headers=h,response_body=data.decode(),elapsed_seconds=time.monotonic()-start))
  return status,data,h
 with tempfile.TemporaryDirectory(prefix='radicale-native-') as tmp:
  tmp=pathlib.Path(tmp);storage=tmp/'storage';rights=tmp/'rights';rights.write_text('[preflight]\nuser: .*\ncollection: .*\npermissions: RrWw\n')
  for cycle in range(2):
   area=out/f'cycle-{cycle+1}';area.mkdir()
   with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
   config=f'[server]\nhosts = 127.0.0.1:{port}\n[auth]\ntype = none\n[rights]\ntype = from_file\nfile = {rights}\n[storage]\nfilesystem_folder = {storage}\n[web]\ntype = none\n[logging]\nlevel = info\n'
   cfg=tmp/'config';cfg.write_text(config);(area/'config.txt').write_text(config)
   origin=f'http://127.0.0.1:{port}';log=(area/'server.log').open('w');cmd=[args.python,'-m','radicale','--config',str(cfg)];p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);start=time.monotonic()
   try:
    for i in range(100):
     if p.poll() is not None:raise RuntimeError('Radicale exited; see server.log')
     try:
      with socket.create_connection(('127.0.0.1',port),timeout=.1):break
     except OSError:time.sleep(.05)
    else:raise RuntimeError('Radicale did not start')
    status,_,_=request(origin,'GET','/calendar/native-event.ics');assert status==404,status
    status,_,_=request(origin,'MKCALENDAR','/calendar/',xml,{'Content-Type':'application/xml; charset=utf-8'});assert status==201,status
    status,data,h=request(origin,'PUT','/calendar/native-event.ics',ics,{'Content-Type':'text/calendar; charset=utf-8','If-None-Match':'*'});assert status==201,status;assert not data;assert h.get('ETag')
    status,body,h=request(origin,'GET','/calendar/native-event.ics');assert status==200,status;assert 'text/calendar' in h.get('Content-Type','')
    text=body.decode().replace('\r\n ','').replace('\r\n\t','')
    for line in ('UID:'+uid,'DTSTART:20300107T100000Z','DTEND:20300107T110000Z','SUMMARY:Native CalDAV event'):assert line in text.splitlines(),line
    assert text.count('BEGIN:VEVENT')==1
    # Original native storage, not V4 mappings; ignore Radicale caches/metadata.
    native=[]
    for f in storage.rglob('*'):
     if f.is_file() and f.suffix=='.ics':
      content=f.read_text();native.append(str(f.relative_to(storage)))
      assert content.count('BEGIN:VEVENT')==1 and 'UID:'+uid in content
      for item in ('DTSTART:20300107T100000Z','DTEND:20300107T110000Z','SUMMARY:Native CalDAV event'):assert item in content.splitlines()
    assert len(native)==1,native
    # Conditional create on occupied resource must reject without mutation.
    before={str(f.relative_to(storage)):hashlib.sha256(f.read_bytes()).hexdigest() for f in storage.rglob('*.ics')}
    status,_,_=request(origin,'PUT','/calendar/native-event.ics',ics,{'Content-Type':'text/calendar','If-None-Match':'*'});assert status==412,status
    after={str(f.relative_to(storage)):hashlib.sha256(f.read_bytes()).hexdigest() for f in storage.rglob('*.ics')};assert before==after
    shutil.copytree(storage,area/'native-storage')
    (area/'verdict.json').write_text(json.dumps({'cycle':cycle+1,'fresh_GET_status':404,'calendar_creation':201,'event_creation':201,'retrieval':200,'native_events':1,'native_title_start_end_uid_match':True,'conditional_duplicate':412,'duplicate_left_native_event_unchanged':True,'native_paths':native,'put_response_body_empty':True,'put_returns_ETag':True,'new_storage_before_each_cycle':True},indent=2)+'\n')
   finally:
    p.terminate()
    try:p.wait(timeout=5)
    except subprocess.TimeoutExpired:p.kill();p.wait()
    log.close();(area/'process.json').write_text(json.dumps({'command':cmd,'exit_code':p.returncode,'elapsed_seconds':time.monotonic()-start},indent=2)+'\n')
   shutil.rmtree(storage)
 (out/'http-trace.json').write_text(json.dumps(records,indent=2)+'\n')
 (out/'summary.json').write_text(json.dumps({'status':'PASS','native_cycles':2,'reset_verified':True,'heldout_condition_attempts':0,'purpose':'native CalDAV feasibility, not an integration experiment'},indent=2)+'\n')
 print('PASS: two fresh native CalDAV create/retrieve/rejection cycles')

if __name__=='__main__':main()
