import re,sys
R='/var/tmp/pcrec-pcrec/scratch/crit-predspec20/subject/'
cf=open(R+'COND-FAMILY.md').read().split('\n')
blk=' '.join(l for l in cf[1303:])
blk=re.sub(r'\s+',' ',blk)
r20=open(R+'predicates_draft_rev20.md').read()
r20n=re.sub(r'\s+',' ',r20)
# normalize markdown line break joins: also remove leading '> ' quote markers
r20n2=re.sub(r' ?> ',' ',r20n)
qs=re.findall(r'“([^”]+)”|"([^"]{12,})"',blk)
for a,b in qs:
    q=a or b
    q=q.strip()
    found=q in r20n or q in r20n2
    # partial: longest prefix found
    n=0
    for k in range(len(q),10,-5):
        if q[:k] in r20n: n=k;break
    print(('FULL ' if found else 'PART%d/%d '%(n,len(q)))+repr(q[:110]))
