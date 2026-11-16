import re,sys,json
p='/var/tmp/pcrec-pcrec/scratch/crit-predspec20/subject/predicates_draft_rev20.md'
L=open(p).read().split('\n')
spans=[]
# body = lines 312..5006 (1-based)
inblock=False
for i in range(311,5006):
    ln=L[i]
    if ln.startswith('    ') and (i==0 or L[i-1].strip()=='' or inblock):
        if ln.strip():
            inblock=True; spans.append((i+1,'B',ln.strip())); continue
    if ln.strip()=='' : 
        # block continues across blank lines only if next is indented
        pass
    else: inblock=False
    for m in re.finditer(r'`([^`]+)`',ln):
        spans.append((i+1,'I',m.group(1)))
json.dump(spans,open('/var/tmp/pcrec-pcrec/scratch/crit-predspec20/census/work/spans.json','w'))
print(len(spans), sum(1 for s in spans if s[1]=='B'))
