import sys; sys.path.insert(0,'/var/tmp/pcrec-pcrec/scratch/crit-predspec22/simulate/w')
from eng import Prog
P=r'(?P<h>\d)?x'; pop=['x']+[d+'x' for d in '0123456789']
canon=lambda v: v.isdigit() and (v=='0' or v[0]!='0')
notlt5=lambda v: not (canon(v['h']) and int(v['h'])<5); ge5=lambda v: canon(v['h']) and int(v['h'])>=5
n=0;bad=0
for mk in ['plain','mark']:
    qa=Prog(P,pop,[('c',{'h':mk},notlt5)]); qb=Prog(P,pop,[('c',{'h':mk},ge5)])
    for extra in [[],[('c',{'h':'mark'},lambda v:int(v['h'])<3)],[('c',{'h':'mark'},lambda v:int(v['h'])>7)]]:
        a=Prog(P,pop,[('not',qa)]+extra); b=Prog(P,pop,[('not',qb)]+extra)
        for t in pop:
            n+=1; bad+=a.holds(t)!=b.holds(t)
print('q with (h?: !(<5)) vs (h?: >=5) on digits, P & !q [& a mark]:',n,'cases, differ',bad)
