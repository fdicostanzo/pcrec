import sys
diff=open(sys.argv[1],encoding='utf-8',errors='surrogateescape').read().split('\n')
pats=open(sys.argv[2],encoding='utf-8',errors='surrogateescape').read().split('\n')
dl=[l for l in diff if l.startswith('REGION DIFFERS')]
out=[]
for l in dl:
    rest=l[len('REGION DIFFERS '):]
    best=None
    for p in pats:
        if p and (rest==p or rest.endswith(') '+p)) and (best is None or len(p)>len(best)): best=p
    out.append(best if best is not None else '??'+rest)
sys.stdout.write('\n'.join(out)+'\n')
