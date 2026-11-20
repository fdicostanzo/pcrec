import re,sys
W='/home/pcrec/projects/pcrec/worktrees/growsurv/'
rows=[l.rstrip('\n').split('\t') for l in open('$S/scc.tsv')]
seen=set()
for r in rows:
    kind,name,loc=r[0],r[1],r[2]
    f,ln,_=loc.split(':')[0],int(loc.split(':')[1]),0
    if f.endswith('internal.h') : continue
    key=(f,ln)
    if key in seen: continue
    seen.add(key)
    L=open(W+f,errors='replace').read().split('\n')
    # body: from ln-1 to first line == '}'
    i=ln-1; j=i
    while j<len(L) and L[j]!='}': j+=1
    body='\n'.join(L[i:j+1])
    fn=name.split('.')[0]
    has_cat='A_CAT' in body
    spine='PCREC_SPINE_EACH' in body or 'pcrec_spine' in body
    loop=bool(re.search(r'\bcontinue;|for \(;;\)|while \(1\)|while \(true\)',body))
    own='PCREC_OWN_FRAME' in '\n'.join(L[max(0,i-3):i+1])
    print('\t'.join([f+':'+str(ln),fn,r[3],'CAT' if has_cat else '-','SPINE' if spine else '-','LOOP' if loop else '-','OWNFRAME' if own else '-',str(j-i+1)+'L']))
