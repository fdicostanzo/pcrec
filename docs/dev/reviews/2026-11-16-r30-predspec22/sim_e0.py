import sys; sys.path.insert(0,'/var/tmp/pcrec-pcrec/scratch/crit-predspec22/simulate/w')
from eng import Prog
import itertools
class Prog21(Prog):
    # rev 21 N1: ('negc', labs, pred): in DOM computation a filter "not pred" where marked labels present; on subject: not cond
    def dom(s,lab):
        if lab in s._dom: return s._dom[lab]
        out=set()
        for t,g in s.matches():
            ok=True
            for it in s.items:
                kind,labs,pred=it
                if any(g[l] is None for l,k in labs.items() if k=='mark'): continue
                if any(g[l] is None for l,k in labs.items() if k=='plain'):
                    ok = (kind=='negc');  # unmarked absent: c fails, so !c holds
                    if not ok: break
                    continue
                r=pred({l:g[l] for l in labs})
                if (kind=='c' and not r) or (kind=='negc' and r): ok=False; break
            if ok and g[lab] is not None: out.add(g[lab])
        s._dom[lab]=out; return out
    def holds(s,t):
        g=__import__('re').fullmatch(s.rx,t)
        if g is None: return False
        g=g.groupdict()
        for it in s.items:
            r=s.cond(('c',it[1],it[2]),g)
            if (it[0]=='c' and not r) or (it[0]=='negc' and r): return False
        return True
pools={
 'A':(r'a(?P<h>\d)|b(?P<k>\d)|c',['a'+d for d in '0123456789']+['b'+d for d in '0123456789']+['c']),
 'B':(r'(?P<h>\d)?-(?P<k>\d)?',[a+'-'+b for a in ['']+list('0123456789') for b in ['']+list('0123456789')]),
}
lt5h=lambda v:int(v['h'])<5; lt5k=lambda v:int(v['k'])<5; hk=lambda v:int(v['h'])<int(v['k']); hk_ge=lambda v:int(v['h'])>=int(v['k'])
for pn,(rx,pop) in pools.items():
    for name,labs,pred,setc in [('!(h?: <5)',{'h':'mark'},lt5h,lambda v:not lt5h(v)),('!(k?: <5)',{'k':'mark'},lt5k,lambda v:not lt5k(v)),('!((h?, k): h < k)',{'h':'mark','k':'plain'},hk,hk_ge)]:
        r21=Prog21(rx,pop,[('negc',labs,pred)])
        q=Prog(rx,pop,[('c',labs,pred)]); r22=Prog(rx,pop,[('not',q)])
        sc=Prog(rx,pop,[('c',labs,setc)])
        a=[t for t in pop if r21.holds(t)!=r22.holds(t)]; b=[t for t in pop if r21.holds(t)!=sc.holds(t)]
        print(pn,len(pop),name,'complemented differ',len(a),sorted(a,key=lambda x:(len(x),x))[:2],'| set differ',len(b),sorted(b,key=lambda x:(len(x),x))[:2], '| b1:',r21.holds('b1') if pn=='A' else '', r22.holds('b1') if pn=='A' else '')
