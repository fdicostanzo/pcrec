import os,sys,io,contextlib
T="/var/tmp/pcrec-pcrec/scratch/crit-predspec22/tree/docs/dev/lanes"
os.chdir(T)
buf=io.StringIO()
g={"__file__":os.path.join(T,"predspec22_check.py"),"__name__":"x"}
with contextlib.redirect_stdout(buf):
    exec(open(os.path.join(T,"predspec22_check.py")).read(), g)
globals().update({k:v for k,v in g.items() if k not in ("__file__","__name__")})
print("POP_N", POP_N)
GT7=lambda x: int(x)>7
fM5 = Fac("h", lambda s, Dm: mk(GN[s]["h"], S5, Dm["h"]))
fM7 = Fac("h", lambda s, Dm: mk(GN[s]["h"], GT7, Dm["h"]))
# before: P & !q, q := P & (h?: <5)
b,_ = answers(POP_N,["h"],v_n,[compl(POP_N,["h"],v_n,[fM5])],RULE)
# after adding (h?: >7) to the shared binding P: P' & !q', q' := P' & (h?: <5), P' = P & (h?: >7)
qP = compl(POP_N,["h"],v_n,[fM7,fM5])
a,dm = answers(POP_N,["h"],v_n,[fM7,qP],RULE)
# after adding only outside
o,_ = answers(POP_N,["h"],v_n,[fM7,compl(POP_N,["h"],v_n,[fM5])],RULE)
for s in POP_N: print(repr(s), "before",b[s], "shared-P added",a[s], "outside-only added", o[s])
# unmarked control
fU5 = Fac("h", lambda s, Dm: GN[s]["h"] is not None and S5(GN[s]["h"]), marks="")
fU7 = Fac("h", lambda s, Dm: GN[s]["h"] is not None and GT7(GN[s]["h"]), marks="")
b2,_=answers(POP_N,["h"],v_n,[compl(POP_N,["h"],v_n,[fU5])],RULE)
a2,_=answers(POP_N,["h"],v_n,[fU7,compl(POP_N,["h"],v_n,[fU7,fU5])],RULE)
print("unmarked FAIL->HOLD:", [s for s in POP_N if not b2[s] and a2[s]])
print("marked FAIL->HOLD shared-P:", [s for s in POP_N if not b[s] and a[s]])
