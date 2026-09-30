# The U2 mover census (ucp_design.md §7 a1): every lookaround-census pattern
# compiled by the base and the U2 binary; report RX_ENGINE before/after.
import csv, subprocess, sys
base, new, tsv = sys.argv[1:4]
def eng(binp, pat, enc, ci, extra=()):
    args = [binp, '--features', 'all', '-e', enc or 'byte', '-p', 'rx', '-o', '-'] + (['-i'] if ci else []) + list(extra) + ['--pattern', pat]
    try:
        out = subprocess.run(args, capture_output=True, timeout=120).stdout.decode('latin-1')
    except subprocess.TimeoutExpired:
        return 'TIMEOUT'
    for ln in out.split('\n'):
        if ln.startswith('#define RX_ENGINE '): return ln.split('"')[1]
    return 'REFUSED'
rows = list(csv.DictReader(open(tsv), delimiter='\t'))
res = []
for r in rows:
    a = eng(base, r['pattern'], r['enc'], r['ci'])
    b = eng(new, r['pattern'], r['enc'], r['ci'])
    d = eng(new, r['pattern'], r['enc'], r['ci'], ['-fno-ctx-node'])
    res.append((r['id'], r['enc'], r['ci'], r['all_a'], a, b, d, r['pattern']))
    print('\t'.join(res[-1]), flush=True)
