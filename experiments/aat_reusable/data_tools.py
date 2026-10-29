"""Offline RDF authoring helper; never imported by the agent worker."""
from pathlib import Path
from rdflib import Graph,URIRef,Literal,RDF
from .profile import A,U,canonical

def write(spec,path):
    g=Graph();a=URIRef(spec['artifact']);t=URIRef(spec['thing'])
    def add(s,p,v):g.add((s,p,v))
    add(t,RDF.type,A.Thing);add(a,RDF.type,A.Artifact);add(a,A.represents,t)
    for p,v in ((U.profile,'finite-usage/1'),(A.reviewed,True),(U.sourceHash,spec['source_hash']),(U.reviewHash,spec['review_hash']),
                (U.observationPath,spec['observation']),(U.identityPointer,spec['identity']),(U.timestampPointer,spec['timestamp']),
                (U.revisionPointer,spec['revision']),(U.mutationPointer,spec['mutations'])):add(a,p,Literal(v))
    for s in spec['slots']:
        n=URIRef(s['id']);add(a,U.slot,n);add(n,RDF.type,U.Slot);add(n,A.subject,t);add(n,U.property,URIRef(s['property']))
        for key in ('kind','pointer','minimum','maximum'):
            if key in s:add(n,U[key],Literal(s[key]))
        if 'unit' in s:add(n,U.unit,URIRef(s['unit']))
    for o in spec['operations']:
        n=URIRef(o['id']);add(a,A.hasOperation,n);add(n,RDF.type,A.Operation)
        for p,key in ((A.method,'method'),(A.path,'path'),(U.requestRevisionPointer,'request_revision'),(U.replyRevisionPointer,'response_revision'),(U.successStatus,'status')):add(n,p,Literal(o[key]))
        add(n,U.mediaType,Literal('application/json'));add(n,U.bodyTemplate,Literal(canonical(o['body'])))
        for i,(ptr,slot) in enumerate(o['echoes']):
            e=URIRef(o['id']+':echo'+str(i));add(n,U.echo,e);add(e,RDF.type,U.Echo);add(e,U.pointer,Literal(ptr));add(e,U.onSlot,URIRef(slot))
    for u in spec['usages']:
        n=URIRef(u['id']);pre=URIRef(u['id']+':pre');post=URIRef(u['id']+':post')
        for p,v in ((RDF.type,A.Usage),(A.forArtifact,a),(A.forOperation,URIRef(u['operation'])),(A.hasPrecond,pre),(A.hasPostcond,post)):add(n,p,v)
        add(a,U.usage,n)
        for c in (pre,post):add(c,RDF.type,A.ContextTemplate);add(c,A.subject,t)
        for label,items,context,predicate in (('condition',u['pre'],pre,U.all),('effect',u['effects'],post,U.effect)):
            for i,item in enumerate(items):
                e=URIRef(u['id']+':'+label+str(i));add(context,predicate,e);add(e,RDF.type,U[item['kind']]);add(e,U.onSlot,URIRef(item['slot']))
                for key in ('value','lower','upper'):
                    if key in item:add(e,U[key],Literal(item[key]))
                if 'unit' in item:add(e,U.unit,URIRef(item['unit']))
        for s in u['frame']:add(n,U.frameSlot,URIRef(s))
    Path(path).write_text('\n'.join(sorted(' '.join(v.n3() for v in triple)+' .' for triple in g))+'\n')
