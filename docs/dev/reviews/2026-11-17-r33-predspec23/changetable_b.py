import re,sys
L=open('../R/subject/predicates_draft_rev23.md').read().split('\n')
pats={'mark':r'[a-z_]\?:|\bh\?|\bm\?|\bk\?|optional mark|never-absent|marked (label|pair|condition)|the mark\b|a mark\b|mark-in|mark-narrows|mark-domain',
 'all':r'\ball\(|\ball\(c\)',
 'DOM':r'\bDOM\b|value set',
 'src':r'source row|result row|per subject|per-subject',
 'bang':r'`!\(|!some|!\(\w+:'}
hist=re.compile(r'rev 22|rev 21|rev 20|\[REV|REV 2\d|retire|RETIRE|\bwas\b|formerly|moved|§16|old|SUPERSEDED|superseded|history|reversed|REVERSED|gone|removed|no longer',re.I)
which=sys.argv[1]
p=re.compile(pats[which])
for i,l in enumerate(L,1):
    if 1020<=i<5854 and p.search(l):
        tag='H' if hist.search(l) else 'L'
        print(i,tag,l[:230])
