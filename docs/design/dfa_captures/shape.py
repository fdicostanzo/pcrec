#!/usr/bin/env python3
"""[dfacap] Shape counts over the captures-only rows (memo section 3.2). TEXT heuristics over
the pattern bytes: a capture inside or under a quantifier, a counted repeat. Usage: python3 shape.py census.tsv"""
import csv,sys,collections,re
rows=list(csv.DictReader(open(sys.argv[1]),delimiter='\t'))
co=[r for r in rows if r['engine']=='vm' and r['why'].startswith('capture') and r['engine_nc']=='dfa']
def unesc(s): return s.encode().decode('unicode_escape').encode('latin-1')
def capquant(p):
    """capture group repeated (itself quantified, or inside a quantified group)"""
    st=[];i=0;caps_q=False;groups=[]  # stack of (is_cap, contains_cap)
    while i<len(p):
        c=p[i:i+1]
        if c==b'\\': i+=2; continue
        if c==b'[':
            j=i+1
            if p[j:j+1]==b'^': j+=1
            if p[j:j+1]==b']': j+=1
            while j<len(p) and p[j:j+1]!=b']': j+=2 if p[j:j+1]==b'\\' else 1
            i=j+1; continue
        if c==b'(':
            iscap = p[i+1:i+2]!=b'?' or p[i+1:i+3] in (b'?<',b"?'",b'?P') and p[i+1:i+4] not in (b'?<=',b'?<!')
            if p[i+1:i+2]==b'*': iscap=False
            st.append([iscap, iscap])
        elif c==b')' and st:
            iscap,cont=st.pop()
            if st and cont: st[-1][1]=True
            q=p[i+1:i+2]
            if cont and q and q in b'*+?{':
                if q!=b'{' or re.match(rb'\{\d+(,\d*)?\}',p[i+1:]): caps_q=True
        i+=1
    return caps_q
C=collections.Counter()
for r in co:
    p=unesc(r['pattern_esc'])
    C['capture repeated']+=capquant(p)
    C['counted repeat {n,m}']+= bool(re.search(rb'\{\d+(,\d*)?\}',p))
    C['ncaps>=3 (2+ groups)']+= int(r['ncaps'] or 0)>=3
    C['prefilter none']+= r['prefilter']=='none'
print(len(co),dict(C))
for r in co:
    if r['prefilter']=='none': pass
print([r['pattern_esc'][:40] for r in co if r['prefilter']=='none'][:20])
