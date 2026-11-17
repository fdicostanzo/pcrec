# own engine from rev 22 text. Joint condition = ONE condition (transparent as a whole where its marked label is
# absent, §4.2 THE RULE); record = `&` of its entries (§4.1 RECORD = `&` AT EVERY DEPTH).
import re
D='0123456789'
P=re.compile(r'(?P<h>\d)?-(?P<k>[0-4])(?:\+(?P<j>[5-9]))?|-(?P<k2>[5-9])\+(?P<j2>[0-4])')
pop=sorted({h+'-'+k+t for h in ['']+list(D) for k in D for t in ['']+['+'+j for j in D]})
def labs(s):
    m=P.fullmatch(s)
    if not m: return None
    g=m.groupdict(); return {'h':g['h'],'k':g['k'] or g['k2'],'j':g['j'] or g['j2']}
M={s:labs(s) for s in pop}; M={s:L for s,L in M.items() if L}
lt5=lambda v:int(v)<5
def mark(lab,S):          # one-label marked condition (lab?: S): (marked label, fn)
    return (lab, lambda L,Dm: S(L[lab]) if L[lab] is not None else (Dm is None or any(S(x) for x in Dm[lab])))
def plain(lab,S):
    return (None, lambda L,Dm: L[lab] is not None and S(L[lab]))
joint=('h', lambda L,Dm: lt5(L['k']) and (lt5(L['h']) if L['h'] is not None else (Dm is None or any(lt5(x) for x in Dm['h']))))
def run(conds):
    Dm={x:{L[x] for L in M.values() if L[x] is not None and
           all(f(L,None) for (ml,f) in conds if ml is None or L[ml] is not None)} for x in 'hkj'}
    return {s:all(f(L,Dm) for _,f in conds) for s,L in M.items()},Dm
a1,d1=run([joint, mark('j',lt5)])                         # P & ((h?, k): (<5, <5)) & (j?: <5)
a2,d2=run([mark('h',lt5), plain('k',lt5), mark('j',lt5)]) # P & (h?: <5, k: <5) & (j?: <5)  [record = &]
diff=[s for s in M if a1[s]!=a2[s]]
print('DOM(j) joint',sorted(d1['j']),'record',sorted(d2['j']))
print('differ',len(diff),'of',len(M),'smallest',sorted(diff,key=lambda s:(len(s),s))[:4], 'on -1:',a1['-1'],a2['-1'])
# without the third label: control (the lane's C vs J)
b1,_=run([joint]); b2,_=run([mark('h',lt5), plain('k',lt5)])
print('without (j?: <5): differ',sum(b1[s]!=b2[s] for s in M))
