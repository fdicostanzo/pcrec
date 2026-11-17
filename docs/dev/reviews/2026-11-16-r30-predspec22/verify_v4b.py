# variant check: while a DOM is computed, an absent marked label ranges over the REGEX's values (order-free, per label)
import sys; W=sys.argv[1]
exec(open(W+'/v4.py').read().split('# ---- RULING-2')[0])
def doms_rx(pop, labels, vals, facs):
    RX={h:{v for s in pop for v in vals(s,h)} for h in labels}
    return {h:{v for s in pop if vals(s,h) and all(f.fn(s,RX) for f in facs) for v in vals(s,h)} for h in labels}
def answer(M, facs):
    vals=lambda s,h: [M[s][h]] if M[s][h] is not None else []
    Dm=doms_rx(list(M),'hkj',vals,facs); return Dm,{s: all(f.fn(s,Dm) for f in facs) for s in M}
exec('# ---- RULING-2'+open(W+'/v4.py').read().split('# ---- RULING-2')[1])
