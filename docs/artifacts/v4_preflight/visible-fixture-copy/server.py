import sys,json,time,pathlib
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
