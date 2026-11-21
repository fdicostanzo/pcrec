import sys
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-memfn-forms8/work")
import cards as C
print("POOL_SIZE", C.POOL_SIZE)
pv = C.pool_variants("t0")
for v, pre, fl in pv: print(v, pre, (pre//16)%4, len(fl))
# emulate a real pool: one hot loop at base offset B within the TU, shifted by the prelude; flags change rel (odd: -4)
B = 1000
lay = {}
for v, pre, fl in pv:
    rel = (48,) if v % 2 == 0 else (44,)
    x = B + pre + rel[0] + (0 if v % 2 == 0 else 3)
    lay[v] = ((x % 64,), (x % 32,), rel)
print(lay); print("refusal:", C.pool_refusal(lay))
