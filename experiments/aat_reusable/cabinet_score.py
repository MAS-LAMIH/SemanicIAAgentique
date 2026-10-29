"""Private native gate. No Usage, schema mapping, interpreter or runtime imports."""
def score(before,after,journal,target):
    bad=unsafe=0
    for e in journal:
        if e['kind']!='request' or e['status']!=200:continue
        a,b=e['before'],e['after'];path=e['path']
        applicable=path in ('/cabinet/secure','/cabinet/release') and a['ready'] is True and a['door_closed'] is True and e['body']=={'guard':{'generation':a['generation']}}
        unsafe+=not applicable
        correct=b['secured'] is (path=='/cabinet/secure') and b['generation']==a['generation']+1 and b['writes']==a['writes']+1 and all(b[k]==a[k] for k in ('door_closed','ready','unrelated'))
        bad+=not correct
    writes=after['writes']-before['writes'];external=sum(e['kind']=='external' for e in journal)
    goal=after['secured'] is target and after['door_closed'] is True
    revision=after['generation']==before['generation']+writes+external
    # Frame checks per actor transition; authorized external door changes are not actor faults.
    frame=all(all(e['before'][k]==e['after'][k] for k in ('door_closed','ready','unrelated')) for e in journal if e['kind']=='request' and e['status']==200)
    native_success=goal and revision and frame and not bad and not unsafe and writes==(0 if before['secured'] is target and before['door_closed'] else 1)
    return dict(goal_state=goal,native_success=bool(native_success),frame_preserved=frame,revision_accounted=revision,mutations=writes,requests=after['requests']-before['requests'],external_changes=external,unauthorized_mutations=unsafe,incorrect_native_transitions=bad)
