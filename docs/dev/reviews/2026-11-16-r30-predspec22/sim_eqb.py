import sys,itertools; sys.path.insert(0,'/var/tmp/pcrec-pcrec/scratch/crit-predspec22/simulate/w')
from eng import Prog
P=r'(?P<h>\d)?x'; pop=['x']+[d+'x' for d in '0123456789']
n=0;bad=[]
for mk in ['plain','mark']:
    qc=Prog(P,pop,[('c',{'h':mk},lambda v:int(v['h'])<5)])
    qr=Prog(r'(?P<h>[0-4])x' if mk=='plain' else r'(?P<h>[0-4])?x',pop,[])
    for tn,(tm,tf) in {'(h?: <3)':('mark',lambda v:int(v['h'])<3),'(h?: >6)':('mark',lambda v:int(v['h'])>6),'(h: >6)':('plain',lambda v:int(v['h'])>6),'(h?: <9)':('mark',lambda v:int(v['h'])<9)}.items():
        a=Prog(P,pop,[('not',qc),('c',{'h':tm},tf)]); b=Prog(P,pop,[('not',qr),('c',{'h':tm},tf)])
        for t in pop:
            n+=1
            if a.holds(t)!=b.holds(t): bad.append((mk,tn,t))
print('q by condition vs q by narrowed regex, with a second & operand:',n,'cases, differ',len(bad),bad[:3])
