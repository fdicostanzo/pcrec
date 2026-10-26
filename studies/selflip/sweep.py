# sweep.py: per bench pattern, (a) auto-caps vs vm-caps timing join from the 2026-10-26 reports,
# (b) the auto artifact's decision stamps + facts (--emit-facts), (c) the kit-proof (cover) reason.
# usage: sweep.py OUTDIR   (compile-only; run under scripts/boxlock run: ~1000 compiles)
import csv, os, subprocess, sys, collections, re, glob
W = '/home/pcrec/projects/pcrec/worktrees/selflip'
BENCH = '/home/pcrec/projects/pcrec-bench/bench'
REP = '/home/pcrec/projects/pcrec-bench/worktrees/b138rep/reports/2026-10-26-'
SETS = {  # set -> (report stem(s) for auto, report for vm)
    'litrun': ('litrun-0.1-ryzen7700x-rebaseline-6b2dbd3e', 'pcrec_6b2dbd3e_auto-caps', 'litrun-0.1-ryzen7700x-rebaseline-6b2dbd3e'),
    'bounded': ('bounded-0.3-ryzen7700x-rebaseline-6b2dbd3e', 'pcrec_6b2dbd3e_auto-caps', 'bounded-0.3-ryzen7700x-rebaseline-6b2dbd3e'),
    'syntax': ('syntax-0.1-ryzen7700x-rebaseline-6b2dbd3e', 'pcrec_6b2dbd3e_auto-caps', 'syntax-0.1-ryzen7700x-rebaseline-6b2dbd3e'),
    'loglines': ('loglines-0.1-ryzen7700x-rebaseline-6b2dbd3e', 'pcrec_6b2dbd3e_auto-caps', 'loglines-0.1-ryzen7700x-rebaseline-6b2dbd3e'),
    'capability': ('capability-0.2-ryzen7700x-first-9ae59f5d4', 'pcrec_9ae59f5d4_auto-caps', 'capability-0.2-ryzen7700x-rebaseline-6b2dbd3e'),
}
def load(stem, testee):
    d = {}
    for row in csv.reader(open(REP + stem + '.subject-grain.tsv'), delimiter='\t'):
        if len(row) > 11 and row[10] == 'median_ns' and testee in row[6]:
            d[(row[1], row[2], row[3])] = float(row[11])
    return d
def run(cmd, env=None):
    e = dict(os.environ); e.update(env or {})
    return subprocess.run(cmd, capture_output=True, text=True, errors='replace', timeout=120, env=e)
out = csv.writer(open(sys.argv[1] + '/sweep.tsv', 'w'), delimiter='\t')
out.writerow(['set', 'pattern', 'large_auto_ns', 'large_vm_ns', 'large_ratio', 'large_nsubj', 'large_vm_wins', 'large_auto_wins',
              'short_ratio', 'engine', 'engine_sel', 'ncaps', 'dfa_scan', 'dfa_prefilter', 'vm_prefilter', 'req_byte', 'req_run',
              'req_why', 'end_window', 'width', 'nullable', 'start_anchor', 'end_pin', 'kitproof'])
for st, (sa, ta, sv) in SETS.items():
    a = load(sa, ta); v = load(sv, 'pcrec_6b2dbd3e_vm-caps')
    pats = collections.defaultdict(lambda: {'large': [0, 0, 0, 0, 0], 'short': [0, 0]})
    for (p, s, r), av in a.items():
        if (p, s, r) not in v: continue
        vv = v[(p, s, r)]
        if r == 'large-subject-throughput':
            g = pats[p]['large']; g[0] += av; g[1] += vv; g[2] += 1; g[3] += vv * 1.3 < av; g[4] += av * 1.3 < vv
        elif r == 'short-subject-search':
            g = pats[p]['short']; g[0] += av; g[1] += vv
    for p in sorted(pats):
        f = f'{BENCH}/{st}/patterns/{p}.rx'
        if not os.path.exists(f): continue
        pat = open(f, 'rb').read()
        facts = run([W + '/build/pcrec', '-p', 'rx', '--features', 'all', '--emit-facts', '--pattern', pat]).stdout
        stamp = {}; fact = {}
        for line in facts.splitlines():
            t = line.split('\t')
            if len(t) == 3 and t[0] == 'byte': stamp[t[1].replace('RX_', '')] = t[2].strip('"')
            if len(t) >= 7 and t[0] == 'byte': fact[t[1]] = t[6]
        kp = run([W + '/build/trace/pcrec-harness', '-p', 'rx', '--features', 'all', '--harness=kit-proof', '-o', W + '/studies/selflip/out/sw.c', '--pattern', pat], {'PCREC_KIT_PROOF_TRACE': '1'}).stderr
        m = re.search(r'KITPROOF\t(\S+)\tk=(\d+)', kp)
        kit = (m.group(1) + (f'/k={m.group(2)}' if m.group(1) == 'cover' else '')) if m else '-'
        L = pats[p]['large']; S = pats[p]['short']
        out.writerow([st, p, f'{L[0]:.0f}', f'{L[1]:.0f}', f'{L[0]/L[1]:.3f}' if L[1] else '', L[2], L[3], L[4],
                      f'{S[0]/S[1]:.3f}' if S[1] else '',
                      stamp.get('ENGINE', ''), stamp.get('ENGINE_SEL', ''), stamp.get('NCAPS', ''), stamp.get('DFA_SCAN', ''),
                      stamp.get('DFA_PREFILTER', ''), stamp.get('VM_PREFILTER', ''), stamp.get('REQ_BYTE', ''), stamp.get('REQ_RUN', ''),
                      stamp.get('REQ_WHY', ''), stamp.get('END_WINDOW', ''), fact.get('width', ''), fact.get('nullable', ''),
                      fact.get('start_anchor', ''), fact.get('end_pin', ''), kit])
