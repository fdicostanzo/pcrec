# closing example from rev 22 TEXT: R = (<10, <30) as a PRODUCT of two integer comparison sets (§2.4: canonical
# numerals only, "no compares-by-value reading"); vs the script's int() reading
import itertools,re
items=[h+(':'+m if m else '') for h in ['3','12'] for m in [None,'15','45','05','99']]
subs=['']
for n in (1,2,3):
    for t in itertools.product(items,repeat=n): subs.append(''.join(x+',' for x in t))
assert len(subs)==1111
P=r'(?:(?P<h>\d+)(?::(?P<m>\d\d))?,)*'
def passes(s): return [(x.split(':')[0], x.split(':')[1] if ':' in x else None) for x in s.split(',') if x]
for s in subs: assert re.fullmatch(P,s)
canon=lambda v: re.fullmatch(r'0|[1-9]\d*',v) is not None
def lt(v,n,spec): return (canon(v) and int(v)<n) if spec else int(v)<n
for spec in (True,False):
    inR=lambda h,m: lt(h,10,spec) and lt(m,30,spec)
    DOMm={m for s in subs for h,m in passes(s) if m is not None}
    DOMv={d for d in DOMm if lt(d,30,spec)}
    I={'I1':lambda ps: all(m is not None and inR(h,m) for h,m in ps),
       'I2a':lambda ps: all(m is None or inR(h,m) for h,m in ps),
       'I2b':lambda ps: all(lt(h,10,spec) if m is None else inR(h,m) for h,m in ps)}
    C={'none((h,m):!R)':lambda ps: not any(m is not None and not inR(h,m) for h,m in ps),
       'none((h,m=99):!R)':lambda ps: not any(not inR(h,m if m else '99') for h,m in ps),
       'none((h,m=00):!R)':lambda ps: not any(not inR(h,m if m else '00') for h,m in ps),
       'none((h,m=0):!R)':lambda ps: not any(not inR(h,m if m else '0') for h,m in ps),
       'none((h,m?):!R)':lambda ps: not any((not inR(h,m)) if m else any(not inR(h,d) for d in DOMv) for h,m in ps),
       '((h,m?):R)':lambda ps: bool(ps) and all(inR(h,m) if m else any(inR(h,d) for d in DOMv) for h,m in ps)}
    print('SPEC (canonical) R' if spec else 'SCRIPT int() R', 'DOMv', sorted(DOMv))
    for iname,f in I.items():
        want={s:f(passes(s)) for s in subs}
        print(' ',iname,'holds',sum(want.values()))
        for cn,cf in C.items():
            d=[s for s in subs if cf(passes(s))!=want[s]]
            print('    %-22s differ %4d %s'%(cn,len(d),sorted(d,key=lambda x:(len(x),x))[:2]))
    print('  on `3,`:', {cn:cf(passes('3,')) for cn,cf in C.items()}, ' on `3:05,` I1', I['I1'](passes('3:05,')))
