# docs/dev/lanes/seambuild_movers.py (lane seambuild, [LOSS-REVIEW] candidate 1): the
# mover census for abi 75 -> 76. Every distinct corpus pattern (emit_sweep's own
# enumeration) is compiled by a REFERENCE pcrec (argv 2) and the tree's (argv 1)
# under --features all on four arms: byte default, byte --engine=vm, utf8 default,
# utf8 --engine=vm. With the abi digit normalized on lines that name the abi, an
# artifact may differ ONLY if the reference defines one of the three seam entries
# (`ptrdiff_t rx_span_match(`, `..._caseless(`, `size_t rx_back_step(`) and the
# tree's defines them `static inline` instead; every other artifact must be
# identical. Prints the population, the movers, and anything outside the rule.
# usage: python3 seambuild_movers.py TREE REF_PCREC [JOBS]
import re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
W, REF = sys.argv[1], sys.argv[2]
JOBS = int(sys.argv[3]) if len(sys.argv) > 3 else 12
sys.path.insert(0, W + '/scripts')
import emit_sweep as es
NEW = W + '/build/pcrec'
pats = es.distinct_patterns(es.enumerate_corpus(NEW, W, 30), every=1)
ARMS = [('byte', []), ('byte-vm', ['--engine=vm']),
        ('utf8', ['-e', 'utf8']), ('utf8-vm', ['-e', 'utf8', '--engine=vm'])]
EXPORTED = re.compile(rb'^(ptrdiff_t rx_span_match(_caseless)?|size_t rx_back_step)\(', re.M)
INLINE = re.compile(rb'^static inline (ptrdiff_t rx_span_match(_caseless)?|size_t rx_back_step)\(', re.M)
ABI = re.compile(rb'(?i)abi')

def comp(b, p, extra):
    r = subprocess.run([b, '-p', 'rx', '--features', 'all'] + extra + ['-o', '-', '--pattern', p],
                       capture_output=True, timeout=120)
    return r.stdout if r.returncode == 0 else None

def norm(t):
    return b'\n'.join(re.sub(rb'\b75\b', b'76', l) if ABI.search(l) else l
                      for l in t.split(b'\n'))

def task(item):
    p, (arm, extra) = item
    try:
        a, b = comp(REF, p, extra), comp(NEW, p, extra)
    except subprocess.TimeoutExpired:
        return (arm, p, 'timeout')
    if a is None or b is None:
        return (arm, p, 'both-refuse' if a is None and b is None else 'refusal-moved')
    carries = bool(EXPORTED.search(a))
    if norm(a) == b:
        return (arm, p, 'BAD-carrier-identical' if carries else 'identical')
    if not carries:
        return (arm, p, 'BAD-mover-without-entry')
    if EXPORTED.search(b) or not INLINE.search(b):
        return (arm, p, 'BAD-entry-still-exported')
    return (arm, p, 'mover')

items = [((p[2] if isinstance(p, tuple) else p), arm) for p in pats for arm in ARMS]
with ThreadPoolExecutor(JOBS) as ex:
    res = list(ex.map(task, items))
tally = {}
for arm, p, v in res:
    tally.setdefault(arm, {}).setdefault(v, 0)
    tally[arm][v] += 1
    if v.startswith('BAD') or v in ('refusal-moved', 'timeout'):
        print('%-8s %-24s %r' % (arm, v, p))
print('patterns', len(pats))
for arm, _ in ARMS:
    print(arm, dict(sorted(tally.get(arm, {}).items())))
