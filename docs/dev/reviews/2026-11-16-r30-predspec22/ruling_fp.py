exec(open('/var/tmp/pcrec-pcrec/scratch/crit-predspec22/ruling/w/split.py').read().split('for name,rx in')[0])
def fp(rx,conds,start):
    M={s:labs(rx,s) for s in pop}; M={s:L for s,L in M.items() if L}
    cur={x:(set(L[x] for L in M.values() if L[x]) if start=='G' else set()) for x in 'hkj'}
    for _ in range(50):
        acc=[L for L in M.values() if all(c(L,cur) for _,c in conds)]
        nxt={x:{L[x] for L in acc if L[x]} for x in 'hkj'}
        if nxt==cur: break
        cur=nxt
    return {s:all(c(L,cur) for _,c in conds) for s,L in M.items()}
for st in 'GL':
    a=fp(P,conds,st); b=fp(Q,conds,st)
    print(st,'differ',sum(a.get(s,False)!=b.get(s,False) for s in set(a)|set(b)), 'P on -1',a['-1'],'Q on -1',b['-1'])
