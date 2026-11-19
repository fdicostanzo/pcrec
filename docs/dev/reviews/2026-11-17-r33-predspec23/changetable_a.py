import re
S='../R/subject/'
rows=[l.rstrip('\n').split('\t') for l in open(S+'r31-condkind/sites.tsv')][1:]
unaff=[];allsites={}
def rng(s):
    out=[]
    for p in s.split():
        m=re.match(r'(\d+)(?:-(\d+))?$',p)
        if m: out.append((int(m[1]),int(m[2] or m[1])))
    return out
for r in rows:
    allsites[r[0]]=r
    if r[4]=='UNAFFECTED': unaff+=rng(r[1])
t=open(S+'predicates_draft_rev23.md').read().split('\n')[825:958]
tab={}
for l in t:
    m=re.match(r'\| (S\d+) \| ([^|]*)\|',l)
    if m: tab[m[1]]=rng(m[2])
print(len(tab))
for k in tab:
    if k not in allsites: print('notin sites',k)
    elif allsites[k][4]=='UNAFFECTED': print('unaff in table',k)
    elif rng(allsites[k][1])!=tab[k]: print('range mismatch',k,allsites[k][1],tab[k])
miss=[k for k,r in allsites.items() if r[4]!='UNAFFECTED' and k not in tab]
print('not in table',[(k,allsites[k][1],allsites[k][4]) for k in miss])
cover=unaff[:]
for v in tab.values(): cover+=v
for k in miss: cover+=rng(allsites[k][1])
r22=open(S+'predicates_draft_rev22.md').read().split('\n')
pat=re.compile(r'[a-z]\?:|\bh\?|all\(|\bDOM\b|value set|domain-scope|match-context|mark-narrows|zero-pass|one-witness|not-of-marked|source row|result row|per subject|default-reaches|optional mark|never-absent|marked (label|pair|condition)|the mark\b|a mark\b|not-is-complement|mark-in|mark-under|mark-domain|\$a\b',re.I)
hits=[i+1 for i,l in enumerate(r22) if pat.search(l)]
unc=[i for i in hits if not any(a<=i<=b for a,b in cover)]
print(len(hits),len(unc))
for i in unc: print(i,r22[i-1][:150])
