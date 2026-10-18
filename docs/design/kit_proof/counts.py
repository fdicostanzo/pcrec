"""kit_proof.md's population counts, read from the kvcensus run (docs/dev/kvcensus/).

Usage: python3 -I docs/design/kit_proof/counts.py docs/dev/kvcensus/sites.tsv.gz docs/dev/kvcensus/patterns.tsv.gz
Reads the committed census data only; compiles nothing, times nothing.
"""
import collections
import gzip
import json
import sys


def rows(path):
    return [json.loads(l) for l in gzip.open(path, 'rt')]


sites = rows(sys.argv[1])
pats = rows(sys.argv[2])
by_id = {(p['pop'], p['id'], p['cfg']): p for p in pats}

print('## A. whole-cover search sites (origin start), by consumer kind and groups')
sc, pc = collections.Counter(), collections.defaultdict(set)
for s in sites:
    if s.get('whole', 0) > 0 and s.get('origin') == 'start':
        p = by_id.get((s['pop'], s['id'], s['cfg']), {})
        caps = 'groups' if int(p.get('ncaps') or 1) > 1 else 'no-groups'
        sc[(s['pop'], s['cfg'], s['kind'], s['site'], caps)] += 1
        pc[(s['pop'], s['cfg'], s['kind'], caps)].add(s['id'])
for k, v in sorted(sc.items()):
    print('sites', *k, v)
for k, v in sorted(pc.items()):
    print('patterns', *k, len(v))

print('## B. what is sent today on those sites (native)')
sh = collections.Counter((s['site'], s['sent']) for s in sites
                         if s.get('whole', 0) > 0 and s.get('origin') == 'start'
                         and s['cfg'] == 'native')
for k, v in sh.most_common(12):
    print(*k, v)

print('## C. whole-cover only with an end anchor: artifact shape')
ec = collections.Counter()
for p in pats:
    if p.get('whole_end', 0) and not p.get('whole', 0):
        ec[(p['pop'], p['cfg'], p.get('engine'),
            'kit-site' if int(p.get('sites') or 0) > 0 else 'no-kit-site')] += 1
for k, v in sorted(ec.items()):
    print(*k, v)

print('## D. whole-cover once context joins, by engine (all items expressible)')
cc = collections.Counter()
for p in pats:
    if p.get('ctx_whole', 0) and p.get('ctx_expr') == 1 and not p.get('whole', 0):
        cc[(p['pop'], p['cfg'], p.get('engine'))] += 1
for k, v in sorted(cc.items()):
    print(*k, v)

print('## E. whole-cover patterns by engine, language source and kit site')
wc = collections.Counter()
for p in pats:
    if p.get('whole', 0):
        wc[(p['pop'], p['cfg'], p.get('engine'), p.get('lang_src', '')[:6],
            'kit-site' if int(p.get('sites') or 0) > 0 else 'no-kit-site')] += 1
for k, v in sorted(wc.items()):
    print(*k, v)
