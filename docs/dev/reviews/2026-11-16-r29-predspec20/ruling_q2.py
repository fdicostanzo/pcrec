import re
R='/var/tmp/pcrec-pcrec/scratch/crit-predspec20/subject/'
cf=open(R+'COND-FAMILY.md').read().split('\n')
blk=re.sub(r'\s+',' ',' '.join(cf[1303:]))
r20=open(R+'predicates_draft_rev20.md').read()
lines=r20.split('\n')
# build normalized text with map to line numbers
norm=[];lmap=[]
for i,l in enumerate(lines):
    t=re.sub(r'^\s*>\s?','',l)
    for ch in (t+' '):
        norm.append(ch);lmap.append(i+1)
s=''.join(norm)
# collapse whitespace with map
out=[];m2=[];prev=False
for ch,ln in zip(s,lmap):
    if ch.isspace():
        if prev: continue
        prev=True;out.append(' ');m2.append(ln)
    else:
        prev=False;out.append(ch);m2.append(ln)
S=''.join(out)
qs=[]
for m in re.finditer(r'(his words?(?:, first)?|then|his remarks|words):\s*"',blk):
    st=m.end()
    e=blk.find('"',st)
    # handle quotes inside: owner quotes contain no '"' presumably except 'or epsilon' style single quotes
    qs.append(blk[st:e])
for m in re.finditer(r'his remarks "([^"]+)" and "([^"]+)"',blk):
    qs+= [m.group(1),m.group(2)]
qs.append('simplifying semantics');qs.append('saving people from themselves')
seen=set()
for q in qs:
    if q in seen: continue
    seen.add(q)
    hits=[m2[x.start()] for x in re.finditer(re.escape(q),S)]
    # find longest prefix match and longest suffix
    best=0
    for k in range(len(q),5,-1):
        if q[:k] in S: best=k;break
    print('Q:',repr(q[:90]),'| full hits lines:',hits[:12],'| prefix',best,'/',len(q))
