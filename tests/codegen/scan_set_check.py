#!/usr/bin/env python3
"""tests/codegen/scan_set_check.py -- [SCANEDGE-SET] every emitted scan edge's
byte set, held to the machine's own TRANSITION TABLE, read off the artifact.

WHAT IS CHECKED. A scan edge (src/opt/scanedge.c) counts the bytes of a class
SET S at a head state h. Its emitted run test is built from the pass's
`DState.scan_set`; the transition table is built by subset construction and
only EDITED by the pass (a bounded edge's set cells are set dead). So the two
are different sources, and the check reads both from the emitted `.c`:

  unbounded edge (a self-loop, the table row is intact):
      the run test's byte set == { b : step(h, class(b)) == h }
      and every byte outside it steps to ONE target (the uniform exit);
  bounded edge (the pass killed the set's cells):
      every byte in the run test's set steps to dead,
      and every byte outside it steps to ONE target.

A set the pass got wrong (a class missing, a class of the exit included) is a
mismatch here on every unbounded edge, which is where all of the set rule's
measured gains are (docs/dev/lanes/rwsurvey_report.md Q4). The bounded half is
weaker (an exit that is itself dead hides the set) and says so in its count.

WHAT IT READS. `-fcomments` artifacts (the `[OPT-5] SCAN EDGE` marker names
the edge block; the code is byte-identical to the default artifact,
run_scan_edge_census.sh's header says why that is licensed). The run test is
evaluated per byte as an expression over the emitted tables; a form it cannot
evaluate (a kit matcher call) is a SKIP, counted and reported, never a pass.

MODES. `scan_set_check.py FILE...` prints one line per file; `--serve` reads
one path per stdin line and answers one line each (the census sweep's
coprocess, so the corpus pays one interpreter start). Answer line:
    ok U B SKIPS MULTI WHY  (edges checked unbounded / bounded / skipped, how
                        many of the checked ones count more than one class,
                        and the skip reasons, comma-separated, or `-`)
    bad <reason>        (the first mismatch, with machine, head and bytes)
"""
import re
import sys

TABLE = re.compile(r'static const [a-z ]+? (\w+)\[(\d+)\] = \{')
STEP = re.compile(r'static inline \w+ (\w+)_step\(')
DEAD = re.compile(r'static inline int (\w+)_is_dead\(\w+ s\) \{ return s == (\d+); \}')
GUARD = re.compile(r'^\s*if \((\w+)_state == (\d+) && ([^&]+?) && (.+)\) \{$')
PEEK = re.compile(r'subject\[[^\]]*\]')
TABREF = re.compile(r'\b([A-Za-z_]\w*)\[b\]')


def run_set(test, tables):
    """The run test's byte set, or None when the form is not an expression
    over bytes and tables (a kit matcher call)."""
    e = PEEK.sub('b', test.strip())
    e = re.sub(r'\(unsigned\)\(([^()]*)\)', r'((\1) & 0xffffffff)', e)
    e = re.sub(r'\b(\d+)u\b', r'\1', e)
    for name in set(TABREF.findall(e)):
        if name not in tables:
            return None
    if re.search(r'\b[A-Za-z_]\w*\(', e):
        return None
    e = e.replace('||', ' or ').replace('&&', ' and ')
    e = re.sub(r'!(?!=)', ' not ', e)
    e = TABREF.sub(r'T["\1"][b]', e)
    try:
        code = compile(e, '<test>', 'eval')
        return {b for b in range(256) if eval(code, {'T': tables, 'b': b})}
    except Exception:
        return None


def check(path):
    tables, steps, dead = {}, {}, {}
    lines = open(path, encoding='latin-1').read().split('\n')
    nu = nb = ns = nm = 0
    why = []
    i = 0
    pend = False
    cur = None
    while i < len(lines):
        ln = lines[i]
        m = TABLE.search(ln)
        if m:
            cur, vals = m.group(1), []
            i += 1
            while i < len(lines) and '};' not in lines[i]:
                vals += [int(x) for x in re.findall(r'-?\d+', lines[i])]
                i += 1
            tables[cur] = vals
            i += 1
            continue
        m = STEP.search(ln)
        if m and i + 1 < len(lines):
            body = lines[i + 1]
            if re.search(r'return transitions\[s \+ cl\];', body):
                steps[m.group(1)] = ('premul', None)
            else:
                k = re.search(r'return (\d+); \}$', body)
                steps[m.group(1)] = ('const', int(k.group(1))) if k else ('other', body.strip())
        m = DEAD.search(ln)
        if m:
            dead[m.group(1)] = int(m.group(2))
        if '[OPT-5] SCAN EDGE' in ln:
            pend = True
        m = GUARD.match(ln) if pend else None
        if m:
            pend = False
            mach, k, test = m.group(1), int(m.group(2)), m.group(4)
            bounded = i + 1 < len(lines) and 'scan_run_length = 1' in lines[i + 1]
            pre = None
            for name in steps:
                if name.endswith('_' + mach):
                    pre = name
            if pre is None or pre not in dead:
                ns += 1; why.append('no-state-block'); i += 1; continue
            kind, val = steps[pre]
            cls = tables.get(pre + '_byte_class')
            sset = run_set(test, tables)
            if kind == 'other' or cls is None or sset is None:
                ns += 1
                why.append('step-form' if kind == 'other' else 'no-class-table' if cls is None
                           else 'run-test-form')
                i += 1; continue
            if kind == 'premul':
                tr = tables.get(pre + '_next_state')
                if tr is None:
                    ns += 1; why.append('no-transition-table'); i += 1; continue
                step = lambda b: tr[k + cls[b]]
            else:
                step = lambda b: val
            where = '%s head cell %d' % (mach, k)
            if bounded:
                inside = {step(b) for b in sset}
                if inside and inside != {dead[pre]}:
                    return 'bad %s: bounded edge, a set byte steps to %s, not dead' % (where, sorted(inside))
                nb += 1
            else:
                stay = {b for b in range(256) if step(b) == k}
                if stay != sset:
                    return ('bad %s: unbounded edge, run test bytes %s but table stays on %s'
                            % (where, sorted(sset - stay) or '-', sorted(stay - sset) or '-'))
                nu += 1
            exits = {step(b) for b in range(256) if b not in sset}
            if len(exits) > 1:
                return 'bad %s: bytes outside the set leave to %d targets %s' % (where, len(exits), sorted(exits))
            if len({cls[b] for b in sset}) > 1:
                nm += 1
        i += 1
    return 'ok %d %d %d %d %s' % (nu, nb, ns, nm, ','.join(sorted(set(why))) or '-')


if __name__ == '__main__':
    if sys.argv[1:] == ['--serve']:
        for path in sys.stdin:
            print(check(path.rstrip('\n')), flush=True)
    else:
        for path in sys.argv[1:]:
            print(path, check(path))
