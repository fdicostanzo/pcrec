#!/usr/bin/env python3
"""R4c's zero-mover verdict over an emit_sweep.py log (no allowlist input
exists in emit_sweep; main's C0 owns that file). PASS (exit 0) iff:
  - the self-check passed;
  - in the REAL RUN, streams c-default, c-vm, emit-ir-vm and composition
    each read movers=0 asymmetric=0, with reach at or above their floors;
  - the dumps stream reads movers=1 asymmetric=0, the mover is --list-axes,
    and its diff's added/removed lines are EXACTLY the two declared
    memfn-simd rows (EXPECTED_ADDED below; nothing removed).
Anything else is FAIL (exit 1), with the reason printed."""
import re, sys

FLOORS = {'c-default': 4165, 'c-vm': 4166, 'emit-ir-vm': 4166, 'composition': 38}
EXPECTED_ADDED = [
    "memfn-simd\t1\tportable\tpredicate\tRX_MEMFN_FORMS\tnone\tPCREC_NO_MEMFN_SIMD\t48\t\t\t-fno-memfn-simd\t",
    "memfn-simd\t2\tsimd\tpredicate\tRX_MEMFN_FORMS\t\t\t\tPCREC_FORCE_MEMFN_SIMD\t49\t-fmemfn-simd\t",
]

def main(path):
    text = open(path, encoding='utf-8', errors='replace').read()
    bad = []
    if 'SELF-CHECK PASSED' not in text:
        bad.append('self-check did not pass')
    real = text.split('===== REAL RUN', 1)
    if len(real) != 2:
        return fail(['no REAL RUN section'])
    real = real[1]
    streams = dict(re.findall(r'-- stream: (\S+) --\n\s*(population=.*)', real))
    for s, floor in FLOORS.items():
        line = streams.get(s)
        if line is None:
            bad.append(f'stream {s} missing'); continue
        m = re.search(r'both_ok\(reach\)=(\d+).*movers=(\d+) asymmetric=(\d+)', line)
        reach, mv, asym = map(int, m.groups())
        if mv or asym:
            bad.append(f'stream {s}: movers={mv} asymmetric={asym}')
        if reach < floor:
            bad.append(f'stream {s}: reach {reach} < floor {floor}')
    d = streams.get('dumps')
    if d is None or not re.search(r'movers=1 asymmetric=0', d):
        bad.append(f'dumps stream not exactly one mover: {d}')
    sec = real.split('-- stream: dumps --', 1)[-1]
    names = re.findall(r'^    (--\S+):$', sec, re.M)
    if names != ['--list-axes']:
        bad.append(f'dumps movers {names} != [--list-axes]')
    added = [l[7:] for l in sec.splitlines() if l.startswith('      +') and not l.startswith('      +++')]
    removed = [l[7:] for l in sec.splitlines() if l.startswith('      -') and not l.startswith('      ---')]
    if removed:
        bad.append(f'{len(removed)} removed --list-axes line(s)')
    if len(added) != len(EXPECTED_ADDED) or not all(a.startswith(e) for a, e in zip(added, EXPECTED_ADDED)):
        bad.append(f'--list-axes added lines != the two declared memfn-simd rows: {[a[:60] for a in added]}')
    return fail(bad) if bad else ok()

def ok():
    print('R4C-GATE PASS: 0 artifact movers; the only dump mover is --list-axes, exactly the two declared memfn-simd rows')
    return 0

def fail(bad):
    for b in bad:
        print('R4C-GATE FAIL:', b)
    return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
