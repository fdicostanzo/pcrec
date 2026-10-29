import sys,statistics as S,math
L=open(sys.argv[1]).read().split('\n')
def rows(start,hdrstart):
    i=[k for k,l in enumerate(L) if l.startswith(hdrstart)][0]+2
    out=[]
    while L[i].startswith('|'):
        out.append([c.strip() for c in L[i].strip('|').split('|')]);i+=1
    return out
def cls(r,f):
    return 'FASTER' if r<1-f else 'SLOWER' if r>1+f else 'within'
bar=rows(0,'| cell | regime')
for lay,ci in(('scalar',4),('simd',9)):
    g={'FASTER':[],'within':[],'SLOWER':[]}
    aa=[]
    for r in bar:
        v=float(r[ci]);f=float(r[5]);g[cls(v,f)].append((v,r[0],r[1],r[2]))
    print(lay,{k:len(v) for k,v in g.items()})
    for k in('FASTER','SLOWER'):
        s=sorted(g[k]);print(k,'lowest5',s[:5],'highest5',s[-5:])
    print('SLOWER all',g['SLOWER'])
aa=[float(r[8]) for r in bar]
print('AA min max',min(aa),max(aa),'maxdev',max(abs(a-1) for a in aa),'gmean',math.exp(S.mean(map(math.log,aa))))
print('AA within 2%',sum(abs(a-1)<=.02 for a in aa),'within 1%',sum(abs(a-1)<=.01 for a in aa),'>.02',[(r[0],r[1],r[2],r[8]) for r in bar if abs(float(r[8])-1)>.02])
print('match regime:',[(r[0],r[2],r[4],r[9]) for r in bar if r[1]=='match'])
sm0=rows(0,'| row | stratum')
sm=[[r[0],r[1],'|'.join(r[2:-8])]+r[-8:] for r in sm0]
# cols now: 0 row 1 stratum 2 pat 3 regime 4 class 5 DEF 6 RTE 7 floor 8 reading 9 simd 10 simdread
from collections import defaultdict
for lay,ci in(('scalar',6),('simd',9)):
    st=defaultdict(lambda:{'FASTER':0,'within':0,'SLOWER':0});sl=[];allr=[]
    for r in sm:
        v=float(r[ci]);f=float(r[7]);c=cls(v,f);st[r[1]][c]+=1;allr.append(v)
        if c=='SLOWER':sl.append((r[0],r[2],r[3],r[4],v))
    print(lay,len(sm),'median',S.median(allr),'gmean',math.exp(S.mean(map(math.log,allr))))
    tot={'FASTER':0,'within':0,'SLOWER':0}
    for k,v in sorted(st.items()):
        print(' ',k,v)
        for q in tot:tot[q]+=v[q]
    print(' total',tot)
    if lay=='scalar' or True:
        d=defaultdict(list)
        for x in sl:d[(x[0],x[1])].append('%s/%s %.3f'%(x[2],x[3],x[4]))
        for k,v in d.items():print('  ',k,v)
d={}
for r in sm:d[(r[0],r[1],r[2])]=1
for k in d:print(k)
