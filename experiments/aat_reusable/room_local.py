"""API-local thermal knowledge. No RDF condition/effect interpretation."""
from .profile import Candidate,Truth,evaluate

def assess(cat,goal,ctx):
    p={s.pointer:s.id for s in cat.slots};v=dict(ctx.values);out=[];t=v[p['/temperature']]
    for u in cat.usages:
        op=next(o for o in cat.operations if o.id==u.operation)
        ready,delta,lo,hi={'/heat':('/heater_ready',1,18,25),'/cool':('/cooler_ready',-1,19,26)}[op.path]
        known=t is not None and v[p[ready]] is not None and all(x is not None for x in v.values())
        pre=Truth.UNKNOWN if not known else Truth.TRUE if v[p[ready]] is True and lo<=t<=hi else Truth.FALSE
        expected=dict(v);expected[p['/temperature']]=t+delta if type(t) is int and 18<=t+delta<=26 else None
        out.append(Candidate(u.id,op.id,pre,evaluate(goal.clauses,expected),tuple(sorted(expected.items())),()))
    return tuple(out)

def ambiguous(cat,goal,ctx):
    p={s.pointer:s.id for s in cat.slots};v=dict(ctx.values);out=[]
    for u in cat.usages:
        op=next(o for o in cat.operations if o.id==u.operation);pred=dict(v)
        pred[p['/temperature']]=v[p['/temperature']]+1;pred[p['/heater_ready']]=op.path=='/heat'
        out.append(Candidate(u.id,op.id,Truth.TRUE,evaluate(goal.clauses,pred),tuple(sorted(pred.items())),('Deliberate conflicting-knowledge control',)))
    return tuple(out)
