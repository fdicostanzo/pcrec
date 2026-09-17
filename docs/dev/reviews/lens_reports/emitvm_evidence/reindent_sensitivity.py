raw=open("/private/tmp/claude-501/-Users-fdicostanzo-pcrec/15fa957d-51f7-4fd3-8c4c-d72a871d5530/scratchpad/ep2/anchors.tsv.raw",encoding='utf-8',errors='replace').read()
lines=raw.split('\n'); recs=[]; cur=None
for l in lines:
    p=l.split('\x01')
    if len(p)>=3 and p[0].startswith('S') and p[0].endswith('.sh'):
        if cur: recs.append(cur)
        cur=[p[0],p[1],'\x01'.join(p[2:])]
    elif cur is not None: cur[2]+='\n'+l
if cur: recs.append(cur)
single=multi=lead=0; ml_lead=0
for n,s,b in recs:
    b=b.rstrip('\n'); ls=b.split('\n')
    if len(ls)==1:
        single+=1
        if b[:1] in (' ','\t'): lead+=1
    else:
        multi+=1
        if any(x[:1] in (' ','\t') for x in ls[1:]): ml_lead+=1
print("total",len(recs))
print("single-line",single,"(of which leading-ws",lead,")")
print("multi-line",multi,"(of which >=1 continuation line has leading ws:",ml_lead,")")
