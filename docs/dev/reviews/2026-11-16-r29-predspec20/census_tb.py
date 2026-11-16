import re
L=open('/var/tmp/pcrec-pcrec/scratch/crit-predspec20/subject/predicates_draft_rev20.md').read().split('\n')
n=0
for i,l in enumerate(L[311:5006],312):
    if not l.startswith('|'): continue
    for m in re.finditer(r'`([^`]+)`',l):
        if re.search(r'(?<!\\)\|',m.group(1)):
            n+=1; print(i,m.group(1)[:80])
print('total',n)
