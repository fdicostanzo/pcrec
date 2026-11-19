import sys; sys.path.insert(0,'/var/tmp/pcrec-pcrec/scratch/crit-predspec22/simulate/w')
from eng import Prog
A=r'a(?P<h>\d)|b(?P<k>\d)|c'; pop=['a'+d for d in '0123456789']+['b'+d for d in '0123456789']+['c']
c=('c',{'h':'mark'},lambda v:int(v['h'])<5); d=('c',{'k':'plain'},lambda v:int(v['k'])<5)
q=Prog(A,pop,[c]); notq=Prog(A,pop,[('not',q)])
flat=Prog(A,pop,[c,d])                      # q & d, q := A & c, expanded: A & c & d
dbl=Prog(A,pop,[('not',notq),d])            # A & !(A & !q) & d
print('L(q) == L(A & !(A & !q)):', [t for t in pop if q.holds(t)]==[t for t in pop if Prog(A,pop,[('not',notq)]).holds(t)])
diff=[t for t in pop if flat.holds(t)!=dbl.holds(t)]
print('q & d (flattened A & c & d) vs A & !(A & !q) & d: differ',len(diff),'of',len(pop),diff, '| on b0:',flat.holds('b0'),dbl.holds('b0'))
# unmarked control
cu=('c',{'h':'plain'},lambda v:int(v['h'])<5)
qu=Prog(A,pop,[cu]); nqu=Prog(A,pop,[('not',qu)])
print('unmarked control differ', sum(Prog(A,pop,[cu,d]).holds(t)!=Prog(A,pop,[('not',nqu),d]).holds(t) for t in pop))
# a second population: B = (?<h>\d)?-(?<k>\d)?, c=(h?:<5), d=(k:<5) and d=(h?:>2)
B=r'(?P<h>\d)?-(?P<k>\d)?'; popB=[a+'-'+b for a in ['']+list('0123456789') for b in ['']+list('0123456789')]
for dn,dd in [('(k: <5)',('c',{'k':'plain'},lambda v:int(v['k'])<5)),('(h?: >7)',('c',{'h':'mark'},lambda v:int(v['h'])>7)),('((h?, k): h > k)',('c',{'h':'mark','k':'plain'},lambda v:int(v['h'])>int(v['k'])))]:
    qB=Prog(B,popB,[c]); n=Prog(B,popB,[('not',qB)])
    f=Prog(B,popB,[c,dd]); g=Prog(B,popB,[('not',n),dd])
    df=[t for t in popB if f.holds(t)!=g.holds(t)]
    print('B',dn,'differ',len(df),'of',len(popB),df[:3])
