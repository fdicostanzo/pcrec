#!/usr/bin/env python3
"""wordwait.py ART.c SUBJ... — per-state step counts for a DFA artifact's FORWARD
machine over the subjects, plus the stay-run (consecutive steps held in one
state) statistics of every state that self-loops on >= 32 byte values.
Same table parsing as ../vm/stayprobe.py (which prints only the top five
states); this adds the totals, the run-length mean and the share of steps. It
steps EVERY byte (no start-skip block): it counts what a plain walk does, and
a `\\b` word-wait state is the one that self-loops on the 63 word bytes.
COUNTS ONLY; no clock."""
import re, sys, collections
art, subs = sys.argv[1], sys.argv[2:]
t = open(art).read()
def arr(name):
    m = re.search(r'%s\[\d+\] = \{(.*?)\};' % re.escape(name), t, re.S)
    return [int(x) for x in re.findall(r'-?\d+', m.group(1))] if m else None
pre = re.search(r'static const unsigned char (\w+?)_forward_byte_class\[256\]', t) or \
      re.search(r'static const unsigned char (\w+?)_byte_class\[256\]', t)
fwd = pre.group(0).split()[4].split('[')[0].replace('byte_class', '')
bc, ns = arr(fwd + 'byte_class'), arr(fwd + 'next_state')
ncls = max(bc) + 1
premul = len(ns) % ncls == 0 and max(ns) >= ncls
stays = sorted(set(int(x) for x in re.findall(re.escape(fwd) + r'stay(\d+)\[', t)))
csz = collections.Counter(bc)
def row(st):
    b = st if premul else st * ncls
    return [ns[b + k] if b + k < len(ns) else -1 for k in range(ncls)]
selfb = {}
visits = collections.Counter(); runs = collections.defaultdict(list); total = 0
for f in subs:
    s = open(f, 'rb').read(); st = 0; run = 0
    for b in s:
        visits[st] += 1; total += 1
        i = st + bc[b] if premul else st * ncls + bc[b]
        nx = ns[i] if i < len(ns) else 0
        nx = nx if nx >= 0 else 0
        if nx == st: run += 1
        else:
            if run: runs[st].append(run)
            run = 0
        st = nx
    if run: runs[st].append(run)
print('machine', fwd, 'classes', ncls, 'premul', premul, 'stay tables', stays, 'steps', total)
def idx(st): return st // ncls if premul else st
print('state\tvisits\tshare\tselfloop_bytes\tstay_table\tstay_runs\tmean_run\tsteps_in_runs')
for st, c in visits.most_common():
    r = row(st); sb = sum(csz[k] for k in range(ncls) if r[k] == st)
    if sb < 32 and c < 0.02 * total: continue
    rl = runs[st]
    print('%d\t%d\t%.2f%%\t%d\t%s\t%d\t%.2f\t%d' % (st, c, 100 * c / total, sb,
          'yes' if (st in stays or idx(st) in stays) else 'no',
          len(rl), (sum(rl) / len(rl) if rl else 0), sum(rl)))

# the SHIPPED stay tables (M2.1's >= 192-byte rule): visits and mean run per such state
for sid in stays:
    st = sid * ncls if premul else sid
    rl = runs[st]
    print('shipped stay%d: state %d visits %d stay_runs %d mean_run %.2f' % (sid, st, visits[st], len(rl), (sum(rl) / len(rl) if rl else 0)))
