#!/usr/bin/env python3
"""R4c's I2 judge (lane r4clx): one I2 arm's emit_sweep.py log, judged.

Usage: memfn_r4c_i2.py LABEL LOG      (LABEL is memfn_r4c.sh's arm label)
       memfn_r4c_i2.py --selftest LOGDIR

emit_sweep exits 1 on ANY floor or witness miss, and some arms remove, BY
CONSTRUCTION, the one composition file a floor counts (ubuntubudu at
91f5b607: 13 arms red with movers=0 asymmetric=0 everywhere). So the rc is
not the verdict; this is. PASS (exit 0) iff:
  - the log is complete (its `population: argv=` and `elapsed:` lines);
  - the REAL RUN holds every stream the arm runs (EXPECT_STREAMS) and EVERY
    stream line reads movers=0 asymmetric=0 (the I2 claim: zero movers);
  - every FAILURE LINE (FAILURE_RX: a floor violation, a witness failure, an
    arms-family `<--` verdict, a traceback) is DECLARED for this arm in
    DECLARED below, verbatim, with its reason;
  - every declaration for this arm OCCURS in the log (a declaration that no
    longer fires is STALE and fails, so the table cannot outlive its cause).
Anything else is FAIL (exit 1), with the reasons printed.

The declarations were MEASURED (docs/dev/lanes/r4clx_report.md item 6): the
named file produces at base and stops under the arm's flags on BOTH the ref
(e6e6d6eb) and the tip, same artifacts, so the drop is the flag's, not R4c's.
"""
import os
import re
import sys

FLOOR_37 = 'COMPOSITION PRODUCING FLOOR VIOLATION: 37 < 38'
DELIVER_FIX = "DELIVER WITNESS FAILURE: fixture(s) did not produce: ['compose_delivers.rxtin']"
DELIVER_SHAPE = ('DELIVER WITNESS FAILURE: no composition artifact anywhere in the sweep '
                 "carries the cross-group SET-pair shape (see DELIVER_RE's header comment) "
                 "-- the composition arm may not be reaching vm_splice's DELIVER block.")

# (label regex, [(failure line, reason)]): first match wins.
DECLARED = [
    (r'^base=(none|-fcomments) -fno-cls-kit$', [
        (FLOOR_37, 'tests/uprops/size_ladder_prefilter_drop.rxt: without the class kit its '
                   'artifact is 608484 bytes of emitted code, over the 500000 limit '
                   '(--max-emit-code-bytes), so the file is refused on both sides')]),
    (r'^base=(none|-fcomments) -fno-splice-calls$', [
        (FLOOR_37, 'tests/rxtsource/fixtures/compose_delivers.rxtin: a delivering call needs '
                   'its definition inlined at the site, which -fno-splice-calls denies by '
                   'construction; refused on both sides'),
        (DELIVER_FIX, 'the same file is one of the two named DELIVER fixtures'),
        (DELIVER_SHAPE, 'the DELIVER block is reached only through a splice; with splices '
                        'denied no artifact can carry the SET-pair shape')]),
    (r'^base=utf8 ', [
        (FLOOR_37, "tests/rxtsource/fixtures/compose_encoding_clash.rxtin: its 'ok' target's "
                   "definition declares `encoding byte`; under -e utf8 the artifact is utf8, "
                   "and one artifact has one encoding, so 'ok' is refused too (the fixture's "
                   "own D58 refusal); both sides")]),
]

EXPECT_STREAMS = {'c-default', 'c-vm', 'emit-ir-vm', 'composition'}
FAILURE_RX = re.compile(r'VIOLATION|FAILURE|FAILED|<--|Traceback|^\s*MOVERS|ASYMMETRIC')


def judge(label, text):
    bad = []
    if 'population: argv=' not in text or not re.search(r'^elapsed: ', text, re.M):
        bad.append('log incomplete (no population/elapsed trailer)')
    real = text.split('===== REAL RUN', 1)
    if len(real) != 2:
        return bad + ['no REAL RUN section']
    streams = re.findall(r'-- stream: (\S+) --\n\s*(population=.*)', real[1])
    seen = {s for s, _ in streams}
    for s in sorted(EXPECT_STREAMS - seen):
        bad.append('stream %s missing' % s)
    if 'dumps' in seen:
        bad.append('stream dumps ran: its declared --list-axes mover is the gate\'s '
                   '(memfn_r4c_gate.py), never an I2 arm\'s')
    for s, line in streams:
        m = re.search(r'movers=(\d+) asymmetric=(\d+)', line)
        if not m:
            bad.append('stream %s: unreadable line %r' % (s, line))
        elif m.groups() != ('0', '0'):
            bad.append('stream %s: movers=%s asymmetric=%s' % (s, m.group(1), m.group(2)))
    decl = next((d for rx, d in DECLARED if re.search(rx, label)), [])
    want = {line for line, _ in decl}
    got = [l.strip() for l in text.split('\n') if FAILURE_RX.search(l)]
    for l in got:
        if l not in want:
            bad.append('UNDECLARED failure line: %s' % l[:200])
    for line, why in decl:
        if line not in got:
            bad.append('STALE declaration (does not occur): %s [%s]' % (line[:80], why[:60]))
    return bad


def run(label, path):
    with open(path, encoding='utf-8', errors='replace') as fh:
        bad = judge(label, fh.read())
    for b in bad:
        print('I2 FAIL [%s]: %s' % (label, b))
    if not bad:
        print('I2 PASS [%s] (%s)' % (label, os.path.basename(path)))
    return 1 if bad else 0


def selftest(logdir):
    """Planted controls over doctored copies of real logs: each must read red."""
    def rd(n):
        with open(os.path.join(logdir, 'i2_%d.log' % n), encoding='utf-8', errors='replace') as fh:
            return fh.read()
    clean, cls = rd(3), rd(9)
    plants = [
        ('an extra mover', 'base=none -fno-cls-kit',
         cls.replace('both_refuse=447 movers=0', 'both_refuse=447 movers=1', 1)),
        ('an asymmetric row', 'base=none -fno-cls-kit',
         cls.replace('movers=0 asymmetric=0', 'movers=0 asymmetric=2', 1)),
        ('an undeclared floor violation', 'base=none -fno-altcls-factor',
         clean.replace('DELIVER witness: OK', FLOOR_37 + '\nDELIVER witness: OK', 1)),
        ('a stale declaration', 'base=none -fno-cls-kit',
         cls.replace(FLOOR_37 + '\n', '', 1)),
        ('a truncated log', 'base=none -fno-altcls-factor', clean.split('elapsed:')[0]),
    ]
    fails = 0
    for what, label, text in plants:
        red = bool(judge(label, text))
        print('selftest %s: %s' % ('ok (red)' if red else 'FAIL (read green)', what))
        fails += not red
    for label, text in (('base=none -fno-cls-kit', cls), ('base=none -fno-altcls-factor', clean)):
        green = not judge(label, text)
        print('selftest %s: the undoctored log of [%s]' % ('ok (green)' if green else 'FAIL (read red)', label))
        fails += not green
    return 1 if fails else 0


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--selftest':
        sys.exit(selftest(sys.argv[2]))
    if len(sys.argv) != 3:
        print(__doc__.split('\n\n')[1], file=sys.stderr)
        sys.exit(2)
    sys.exit(run(sys.argv[1], sys.argv[2]))
