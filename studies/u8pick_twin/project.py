#!/usr/bin/env python3
"""project.py RUN.tsv BENCH_REPORTS_DIR -- READ-ONLY use of pcrec-bench's committed
reports.  For each lit cell: the bench's pooled large-subject-throughput numbers
(pcrec @c4c70f2c round1; re2 round1; rust from the 751b9c6d fullroster matrix,
ratio x best_ns_pooled), this lane's pooled numbers per arm on the Linux dev
box, and a PROJECTION of each arm onto the bench box using the cell's own
calibration factor f = bench_pcrec@c4c70f2c / P_mine (P = this lane's build of the
bench pin's compiler, same subjects, same driver loop).  A projection is not a
measurement: the bench must re-run at current main to confirm (bench-only q)."""
import csv, statistics as st, sys, collections
run, rep = sys.argv[1], sys.argv[2].rstrip('/')
g = collections.defaultdict(list)
for r in csv.DictReader(open(run), delimiter='\t'):
    g[(r['cell'], r['subj'], r['arm'])].append(float(r['ns_per_call']))
cells = list(dict.fromkeys(k[0] for k in g)); subs = list(dict.fromkeys(k[1] for k in g))
def pooled(c, a):
    if (c, subs[0], a) not in g: return None
    return sum(st.median(g[(c, s, a)]) for s in subs) / 1000.0
r1 = {}
for r in csv.reader(open(rep + '/2026-10-05-utf8-0.1-budu-ryzen1600-round1-c4c70f2c.tsv'), delimiter='\t'):
    if len(r) > 11 and r[0] == 'rank_yes' and r[1].startswith('lit-') and r[3] == 'large-subject-throughput' and r[10] == 'median_ns':
        r1[(r[1], r[6])] = float(r[11]) / 1000
rows = [r for r in csv.reader(open(rep + '/2026-09-27-utf8-0.1-budu-ryzen1600-fullroster-751b9c6d.matrix.tsv'), delimiter='\t') if r and not r[0].startswith('#')]
ix = {n: i for i, n in enumerate(rows[0])}
rust = {}
for r in rows[1:]:
    if r[1].startswith('lit-') and r[2] == 'large-subject-throughput':
        rust[r[1]] = float(r[ix['rust_1.13.1_default-caps-simdna']]) * float(r[ix['best_ns_pooled']]) / 1000
print('cell\tbench_pcrec\tbench_re2\tbench_rust\tbench_pcrec/best_peer\tmine_P\tf=bench/mine_P\tmine_A\tmine_B\tmine_C\tproj_B\tproj_B/best_peer\tproj_A/best_peer\tproj_C/best_peer\tmemmem_mine\tS_avx2pair_mine\tproj_S/best_peer')
for c in cells:
    bp = r1[(c, 'pcrec_c4c70f2c_auto-caps-simdna_utf8')]; re2 = r1[(c, 're2_11.0.0_default-caps-simdna_utf8')]; ru = rust[c]
    best = min(re2, ru)
    P, A, B, C, M, S = (pooled(c, a) for a in 'PABCMS')
    f = bp / P if P > 0.05 else float('nan')
    pr = lambda x: x * f
    print('\t'.join([c, '%.1f' % bp, '%.1f' % re2, '%.1f' % ru, '%.2f' % (bp / best), '%.1f' % P, '%.2f' % f,
                     '%.1f' % A, '%.1f' % B, '%.1f' % C, '%.1f' % pr(B), '%.2f' % (pr(B) / best), '%.2f' % (pr(A) / best),
                     '%.2f' % (pr(C) / best), ('%.1f' % M) if M else '-', ('%.1f' % S) if S else '-', ('%.2f' % (pr(S) / best)) if S else '-']))
