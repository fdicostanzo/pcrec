import re,sys
S=sys.argv[1]
def norm(t): return re.sub(r'\s+',' ',t.replace('\\"','"'))
note=open(S+'/condition_kind.md').read()
srcs={k:norm(open(S+'/'+f).read()) for k,f in [('CF','COND-FAMILY.md'),('DR','predicates_draft_rev22.md'),('FU','predicates_future.md')]}
nn=norm(note)
for m in re.finditer(r'"([^"]{12,}?)"',nn):
    q=m.group(1)
    hits=[k for k,v in srcs.items() if q in v]
    if not hits:
        # try pieces split on ' ... '
        parts=[p for p in q.split(' ... ')]
        ok=all(any(p in v for v in srcs.values()) for p in parts) and len(parts)>1
        print('NOTFOUND' if not ok else 'ELLIPSIS-OK', repr(q[:160]))
    else:
        print('ok',hits,repr(q[:70]))
