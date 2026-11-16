# predspec14: census of anchor* words in predicates_draft.md by meaning (heuristic classes; usage: python3 -I THIS OLD NEW)
import re,sys
def classify(path):
    L=open(path).read().split('\n')
    cut=[i for i,l in enumerate(L,1) if l.startswith('## 0. Status')][0]
    c={}
    for i,l in enumerate(L,1):
        for m in re.finditer(r'(?i)\b(un)?anchor[a-z]*(\.[a-z]+)?', l):
            w=m.group(0); pre=l[max(0,m.start()-1):m.start()]; post=l[m.end():m.end()+1]
            if i<cut: k='history: changelog'
            elif re.match(r'anchor\.(operand|whole)',w): k='the warning name'
            elif w.lower()=='anchored' and (pre=='`' or post=='('): k='the macro anchored'
            elif w.lower() in ('anchor','anchors') and re.search(r'param\(isodate\)|of = anchor|anchor \+-|three anchor|anchor := ', l): k='other: E-NEAR date'
            elif re.search(r'(?i)unanchored search|PCRE2_ANCHORED|own anchored match|anchored/whole-string MODE|none when anchored|make the anchor a constant', l): k='other: PCRE/API mode'
            elif w.lower() in ('anchor','anchors'): k='real assertion (noun)'
            else: k='whole-match / & tie (incl. history, quotes)'
            c[k]=c.get(k,0)+1
    return c
a=classify(sys.argv[1]); b=classify(sys.argv[2])
for k in sorted(set(a)|set(b)): print("%-45s before %4d  after %4d"%(k,a.get(k,0),b.get(k,0)))
print("%-45s before %4d  after %4d"%("TOTAL",sum(a.values()),sum(b.values())))
