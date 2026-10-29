"""Native API-local Boolean knowledge, not RDF effects/precondition interpretation."""
from .profile import Candidate,Truth,evaluate

def assess(cat,goal,ctx):
    p={s.pointer:s.id for s in cat.slots};v=dict(ctx.values);out=[]
    for u in cat.usages:
        op=next(o for o in cat.operations if o.id==u.operation);value={'/cabinet/secure':True,'/cabinet/release':False}[op.path]
        ready=v[p['/interlocks/ready']];closed=v[p['/interlocks/door_closed']]
        pre=Truth.UNKNOWN if any(x is None for x in v.values()) else Truth.TRUE if ready is True and closed is True else Truth.FALSE
        pred=dict(v);pred[p['/latch/secured']]=value
        out.append(Candidate(u.id,op.id,pre,evaluate(goal.clauses,pred),tuple(sorted(pred.items())),()))
    return tuple(out)

def ambiguous(cat,goal,ctx):
    p={s.pointer:s.id for s in cat.slots};v=dict(ctx.values);out=[]
    for u in cat.usages:
        op=next(o for o in cat.operations if o.id==u.operation);pred=dict(v);pred[p['/latch/secured']]=True;pred[p['/interlocks/ready']]=op.path=='/cabinet/secure'
        out.append(Candidate(u.id,op.id,Truth.TRUE,evaluate(goal.clauses,pred),tuple(sorted(pred.items())),('Deliberate conflicting-knowledge control',)))
    return tuple(out)
