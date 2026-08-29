#!/usr/bin/env python3
"""[r40 F1/F5] The refitted size model: FOUR terms, joint two-intercept OLS.

This is the script that produces the note's coefficients (r40 F5: the first
cut committed a single-intercept OLS that could not produce the quoted
numbers). Terms:
    N  VM nodes                    (rx_L<N>: labels)
    S  prefilter DFA states        (rx_s<N>: labels -- the computed-goto form)
    E  data-table entries          (unsigned char/short arrays)
    J  jump-table entries          (void *const arrays; J = S * ncls)
Two intercepts (vm / dfa).
"""
import sys
sys.path.insert(0,'/tmp/claude-1001/-home-duxevents-pcrec/2118fa38-0a1c-4bbd-ba29-87aee486bb5b/scratchpad/artsize3')
from fit import load, num, pct, ols

CORPUS='/tmp/claude-1001/-home-duxevents-pcrec/2118fa38-0a1c-4bbd-ba29-87aee486bb5b/scratchpad/artsize3/corpus3.tsv'

def rows_corpus():
    out=[]
    for d in load(CORPUS):
        if d.get('err','') or not d.get('bytes',''): continue
        out.append(dict(src='corpus', eng=d['engine'], b=float(num(d,'bytes')),
                        N=float(num(d,'labels')), S=float(num(d,'slabels')),
                        E=float(num(d,'table_entries')), J=float(num(d,'jump_entries')),
                        pat=d['pattern']))
    return out

def rows_jfit():
    out=[]
    p='/tmp/claude-1001/-home-duxevents-pcrec/2118fa38-0a1c-4bbd-ba29-87aee486bb5b/scratchpad/artsize3/jfit.tsv'
    hdr=None
    for i,l in enumerate(open(p)):
        f=l.rstrip('\n').split('\t')
        if i==0: hdr=f; continue
        d=dict(zip(hdr,f))
        if not d['bytes']: continue
        out.append(dict(src='jfit', eng='vm', b=float(d['bytes']), N=float(d['N']),
                        S=float(d['S']), E=float(d['E']), J=float(d['J']), pat=d['label']))
    return out

def design(rs):
    return [[1.0 if r['eng']=='vm' else 0.0, 1.0 if r['eng']=='dfa' else 0.0,
             r['N'], r['S'], r['E'], r['J']] for r in rs]

NAMES=['S_vm','S_dfa','N','S','E','J']

def fit(rs, label):
    X=design(rs); y=[r['b'] for r in rs]
    co=ols(X,y)
    err=[abs(sum(c*v for c,v in zip(co,x))-a)/a for x,a in zip(X,y)]
    print("\n%s (n=%d)"%(label,len(rs)))
    print("   "+"  ".join("%s=%.3f"%(n,c) for n,c in zip(NAMES,co)))
    print("   |rel err| median %.4f p90 %.4f p99 %.4f max %.4f"%(
        pct(err,.5),pct(err,.9),pct(err,.99),max(err)))
    return co

def predict(co,r):
    return (co[0] if r['eng']=='vm' else co[1])+co[2]*r['N']+co[3]*r['S']+co[4]*r['E']+co[5]*r['J']

if __name__=='__main__':
    c=rows_corpus(); j=rows_jfit()
    print("corpus n=%d   jfit n=%d"%(len(c),len(j)))
    co=fit(c+j,"JOINT corpus+jfit, 4 terms")
    import json
    json.dump(co,open('/tmp/claude-1001/-home-duxevents-pcrec/2118fa38-0a1c-4bbd-ba29-87aee486bb5b/scratchpad/artsize3/model4.json','w'))
    # error on the corpus alone
    ec=[abs(predict(co,r)-r['b'])/r['b'] for r in c]
    print("\n   on the CORPUS alone: median %.4f p90 %.4f p99 %.4f max %.4f"%(pct(ec,.5),pct(ec,.9),pct(ec,.99),max(ec)))
    # the selecting population (above threshold candidates)
    sel=[r for r in c if r['b']>100000]
    es=[abs(predict(co,r)-r['b'])/r['b'] for r in sel]
    print("   on the >100 KB population (n=%d): median %.4f max %.4f"%(len(sel),pct(es,.5),max(es)))
