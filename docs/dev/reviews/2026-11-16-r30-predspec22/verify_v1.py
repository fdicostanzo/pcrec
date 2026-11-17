import itertools,re
items=[(h,m) for h in ('3','12') for m in (None,'15','45','05','99')]
lists=[l for n in range(4) for l in itertools.product(items,repeat=n)]
canon=lambda v: re.fullmatch(r'0|[1-9]\d*',v) is not None
for name,lt in (('TEXT canonical',lambda v,n: canon(v) and int(v)<n),('by value',lambda v,n:int(v)<n)):
    R=lambda h,m: lt(h,10) and lt(m,30)
    I1=lambda L: all(m is not None and R(h,m) for h,m in L)
    I2a=lambda L: all(m is None or R(h,m) for h,m in L)
    I2b=lambda L: all(lt(h,10) if m is None else R(h,m) for h,m in L)
    nd=lambda d: (lambda L: not any(not R(h, m if m is not None else d) for h,m in L))
    print(name,len(lists),'I1',sum(map(I1,lists)),'I2a',sum(map(I2a,lists)),'I2b',sum(map(I2b,lists)))
    for d in ('00','0','99'):
        c=nd(d); print('  m=%s'%d,'vsI1',sum(c(L)!=I1(L) for L in lists),'vsI2b',sum(c(L)!=I2b(L) for L in lists), 'on 3,:',c([('3',None)]))
