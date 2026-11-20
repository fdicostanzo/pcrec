import sys, statistics as st, collections
d = collections.defaultdict(list)
for l in open(sys.argv[1]):
    p = l.split()
    if len(p) == 4 and p[0] == 'T': d[(p[1], p[2])].append(float(p[3]))
cells = sorted({c for c, _ in d})
print("cell\tarm\tn\tmedian_ms\tmin_ms\tmax_ms")
med = {}
for c in cells:
    for a in ('on', 'off', 'on2'):
        v = d[(c, a)]; med[(c, a)] = st.median(v)
        print(f"{c}\t{a}\t{len(v)}\t{med[(c,a)]:.4f}\t{min(v):.4f}\t{max(v):.4f}")
dense = [c for c in cells if not c.startswith('tail')]
aa = {c: abs(med[(c, 'on2')] / med[(c, 'on')] - 1) for c in cells}
floor = max(aa.values())
thr = max(0.05, 2 * floor)
print("A/A deviations: " + " ".join(f"{c}={aa[c]*100:.2f}%" for c in cells))
print(f"noise floor (max A/A) = {floor*100:.2f}%  threshold = {thr*100:.2f}%")
for c in cells:
    print(f"RATIO {c} on/off = {med[(c,'on')]/med[(c,'off')]:.3f}")
if floor > 0.05:
    print("VERDICT: INCONCLUSIVE (A/A control above 5%)")
else:
    slower = [c for c in dense if med[(c,'on')] / med[(c,'off')] > 1 + thr]
    print("VERDICT: LOSS STILL SHOWN in " + ", ".join(slower) if slower else "VERDICT: NO LOSS")
