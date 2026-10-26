# capjoin.py: join window-A pcrec auto-caps with window-B pcrec vm-caps on the bench's capability
# subject-grain tsv (large and short regimes), per pattern. usage: capjoin.py > out/capjoin.tsv
import csv, collections, sys
R = '/home/pcrec/projects/pcrec-bench/worktrees/b138rep/reports/2026-10-26-capability-0.2-ryzen7700x-'
A = R + 'first-9ae59f5d4.subject-grain.tsv'
B = R + 'rebaseline-6b2dbd3e.subject-grain.tsv'
def load(path, testee_sub):
    d = {}
    for row in csv.reader(open(path), delimiter='\t'):
        if len(row) < 12 or row[10] != 'median_ns' or testee_sub not in row[6]: continue
        d[(row[1], row[2], row[3])] = float(row[11])
    return d
a = load(A, 'pcrec_9ae59f5d4_auto-caps')
b = load(B, 'pcrec_6b2dbd3e_vm-caps')
agg = collections.defaultdict(lambda: [0.0, 0.0, 0])
for k, av in a.items():
    if k in b:
        g = agg[(k[0], k[2])]; g[0] += av; g[1] += b[k]; g[2] += 1
print('pattern\tregime\tn\tauto_sum_ns\tvm_sum_ns\tauto_over_vm')
for (p, r), (x, y, n) in sorted(agg.items()):
    print(f'{p}\t{r}\t{n}\t{x:.0f}\t{y:.0f}\t{x/y:.3f}')
