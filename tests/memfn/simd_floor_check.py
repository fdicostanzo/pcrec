#!/usr/bin/env python3
"""tests/memfn/simd_floor_check.py -- C18, THE FLOOR RULE and the
scaffolding lint, plus C9-x86 ([MEMFN] R4e' batch 1, request R-13;
docs/design/memfn/integration.md §R4.9.2.3's floor rule and §R4.9.8's C18
and C9-x86 rows, as amended by D155; re-aimed for the target seam, units
U2+U3, docs/design/memfn/target_seam.md §6-§8, lane u3floor). Driven by
run_simd_floor.sh (`make test-memfn-simdfloor`).

THE TARGET SEAM. An artifact is planned for ONE target: `-fmemfn-simd=T`
renders T's admitted levels with no CPU `#if`, inside T's REGION (the kit's
`mf_target_c_of(T)` text) under T's family GUARD (`mf_family_c_of`), and
stamps `<P>_TARGETS "FAMILY:T"`. The `#if` arms, and with them the old
off-target leg (a) (the ON text preprocessed off-target IS the OFF text),
are gone: a no-vector consumer compiles the default target (match_api.md
§10.7¶4), and another family's compiler is refused by the guard
(run_targets.sh's guard cells).

THE POPULATION, counted by pcrec's own compile: every corpus pattern (plus
named witnesses, one per batch-1 route bin) at the default engine and at
--engine=vm, compiled at -fno-memfn-simd (OFF) and at -fmemfn-simd=T (ON)
for every target T whose family has a level (read from the dumper, so a new
target joins). Admission is recomputed HERE from the table's facts (a level
of T's family whose needs T's features supply), never read from the kit's
gate. Every ON artifact carries scaffolding; a MOVER is a cell whose ON text,
the scaffolding and the moved stamps aside, differs from OFF. Its SIMD FUNCs
are the selectors whose one call names a level helper `<fn>__w<VW>`. Per
target, movers, SIMD FUNCs and the selectors calling each admitted level
are printed with a literal floor (K35). On every cell:

  scaffolding lint, PLACEMENT: the TARGETS stamp reads "FAMILY:T"; the
      family guard occurs once, ahead of every `#include`; the region open
      and close occur once each, in that order, and every function body and
      initializer of the file lies between them.
  scaffolding lint, EXCLUSIVITY: with those three texts cut out (exactly the
      kit's declared spellings, from the dumper), the lines ON inserts over
      OFF hold no preprocessor line but `#include <H>` for an ADMITTED
      level's header; no helper of an unadmitted level appears.
  (c) SOURCE-LEVEL, ONE REPLACED CALL PER SIMD FUNC: the raw diff OFF -> ON
      deletes no line but the moved stamps (`<P>_TARGETS`, `<P>_MEMFN_FORMS`,
      `<P>_SIMD_GUARDED_BYTES`) and, per SIMD FUNC, its one
      `    return <fn>__body(<args>);`, replaced by the same call to
      `<fn>__w<VW>` with VW an admitted level's width; the inserted lines'
      bytes (stamps aside) equal the ON artifact's `<P>_SIMD_GUARDED_BYTES`
      exactly (pcrec's sink counts what the kit bracketed plus the guard and
      region; this script counts the diff).
  (d) NO DIRECTIVE IN A FUNCTION BODY, one call per selector: routing_shape.py
      (D155 addendum 1's rule, sharing no code with the kit) over the ON text.
A header line ahead of the region whose `#include` OFF also carries (a
compound part's own <string.h>, moved there: match_api.md §6.3.10¶15) is set
aside on every leg (target_text.moved_headers_aside), and OFF's own copy of
it, which ON no longer repeats inside the region, with it (moved_out); C9
compiles the artifact as emitted.
On every mover additionally:
  (b) PREPROCESSED: `gcc -E -P` of OFF and ON, diffed, deletes exactly the one
      `return <fn>__body(...)` line per SIMD FUNC (a macro in the inserted
      text that rewrites the scalar floor shows as more).
  C9-x86: the ON artifact compiles -Wall -Wextra -Werror with no -march and
      at x86-64, x86-64-v2, sandybridge, x86-64-v3, x86-64-v4 and
      -mgeneral-regs-only; at -O0 each SIMD FUNC's called helper is defined
      in the object (read with nm) at EVERY cell: the region, not the
      consumer's flags, supplies the ISA.

CONTROLS, on every run: each target's first mover is judged again with one
plant at a time (a stray `#pragma` outside the region, the region close
dropped, the guard moved after an `#include`, a stray `#if` around a level
include inside the region, a scalar floor call deleted); each must be
rejected by the leg it names. The lint's SPELLINGS share a source with the
emitter by design (the kit's table: the check holds placement and
exclusivity, not the text); the compiler is their control (C9 here,
run_targets.sh's stripped-region refusal). The kit's `moved`, FORMS and
trace are never read to find a mover. Prints `checks passed: N` /
`checks failed: N`.
"""
import argparse
import concurrent.futures
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(TREE, 'scripts'))
sys.path.insert(0, HERE)
import emit_sweep as es  # noqa: E402
import routing_shape  # noqa: E402
from target_text import admitted, cut, moved_headers_aside, moved_out, read_table  # noqa: E402

# Floors per target, pinned AT the measure (deterministic counts of emitted
# text). History of the pre-seam single count: 44 at w16 (R-13); 33 at D172
# S3; 46 at code review r1 C1 (lane s3), both rungs under one `#if` chain.
# The target seam (lane u3floor) splits it per target and per level: 55 and
# 55 measured at both targets on the full corpus (2026-11-08, 5095 patterns;
# the corpus grew since r1 C1), every selector at its target's top level.
FLOORS = {
    # target: (movers, SIMD FUNCs, {level stamp: selectors calling it})
    'x86-64': (55, 55, {'w16': 55}),
    'x86-64-v3': (55, 55, {'w32': 55}),
}
LEVELS_FLOOR = 2       # mf_levels() rows: w16, w32 (R-13)
TARGETS_FLOOR = 2      # targets whose family has a level (U2)
NAMED = [
    # `(?i)cat` is a fixed-width `cover` artifact by default (D172 S3); since code
    # review r1 C1 its window search's SIMD FUNC is fn-pair's again, on the DEFAULT
    # path (S3 had moved the witness under `--memfn=no-window-search`)
    ('mod-i (DFA, ASSIGN)', '(?i)cat', []),
    ('union-select (DFA)', '(?i)union.*?select.*?from', []),
    ('union-select (no-DFA, ON_MISS)', '(?i)union.*?select.*?from', ['--engine=vm']),
    ('no-DFA ON_MISS', '(?i)\\d+cat', ['--engine=vm']),
    ('VM hybrid', '(?i)(a|b)+cat', []),
]
# [COMPOUND] the artifact's own stamp lines: a compound's .c also carries its
# PARTS' lines under `<prefix>__<role>` (match_api.md §3.7¶1, not contract),
# and an artifact prefix never contains `__` (cli.md §1.6¶2's `parts` row).
STAMP_MOVES = re.compile(r'^#define (?:(?!__)\w)+_(TARGETS|MEMFN_FORMS|SIMD_GUARDED_BYTES) ')
TARGETS = re.compile(r'^#define (?:(?!__)\w)+_TARGETS "([^"]*)"$', re.M)
GUARDED = re.compile(r'^#define (?:(?!__)\w)+_SIMD_GUARDED_BYTES (0x[0-9a-f]+)ULL$', re.M)
SELECTOR = re.compile(r'^static inline size_t (\w+)\([^)]*\)\n\{\n    return (\w+)__w(\d+)\(.*\);\n\}$', re.M)
HELPER = re.compile(r'^static inline size_t (\w+)__w(\d+)\(', re.M)
BODY_OPEN = re.compile(r'^(\{|\S.*= \{$)', re.M)
FLOOR_CALL = re.compile(r'^    return (\w+)__body\((.*)\);$')
LEVEL_CALL = re.compile(r'^    return (\w+)__w(\d+)\((.*)\);$')
C9_MARCH = [[], ['-march=x86-64'], ['-march=x86-64-v2'], ['-march=sandybridge'],
            ['-march=x86-64-v3'], ['-march=x86-64-v4'], ['-mgeneral-regs-only']]


def sh(cmd, timeout=120, **kw):
    try:
        return subprocess.run(cmd, capture_output=True, timeout=timeout, **kw)
    except subprocess.TimeoutExpired:
        return None


def diff_lines(a, b):
    """(deleted, inserted) lines of a -> b, by `diff` (an outside tool)."""
    with tempfile.NamedTemporaryFile('w', delete=False, dir=os.environ.get('TMPDIR')) as fa, \
         tempfile.NamedTemporaryFile('w', delete=False, dir=os.environ.get('TMPDIR')) as fb:
        fa.write(a)
        fb.write(b)
    r = subprocess.run(['diff', '--unchanged-line-format=', '--old-line-format=-%L',
                        '--new-line-format=+%L', fa.name, fb.name], capture_output=True)
    os.unlink(fa.name)
    os.unlink(fb.name)
    out = r.stdout.decode('utf-8', 'surrogateescape').split('\n')
    dele = [l[1:] for l in out if l.startswith('-')]
    ins = [l[1:] for l in out if l.startswith('+')]
    return dele, ins


def text_legs(toff, ton, t, adm, aside=0):
    """The text-only legs on one cell: (mover, {fn: vw}, [issue])."""
    issues = []
    fam_target = '%s:%s' % (t['family'], t['name'])
    vws = {l['vw'] for l in adm}
    headers = {l['header'] for l in adm}
    # PLACEMENT
    tg = TARGETS.findall(ton)
    if tg != [fam_target]:
        issues.append('placement: TARGETS stamp(s) %r, expected [%r]' % (tg, fam_target))
    spans = {}
    for what in ('guard', 'open', 'close'):
        n = ton.count(t[what])
        if n != 1:
            issues.append('placement: the %s text occurs %d times, expected once' % (what, n))
        elif not ton.startswith(t[what]) and ton[ton.index(t[what]) - 1] != '\n':
            issues.append('placement: the %s text does not start a line' % what)
        else:
            spans[what] = (ton.index(t[what]), ton.index(t[what]) + len(t[what]))
    if 'guard' in spans:
        inc = re.search(r'^#\s*include\b', ton, re.M)
        if inc and inc.start() < spans['guard'][0]:
            issues.append('placement: an #include precedes the family guard: %r' % inc.group(0))
    if 'open' in spans and 'close' in spans:
        if spans['open'][1] > spans['close'][0]:
            issues.append('placement: the region closes before it opens')
        for m in BODY_OPEN.finditer(ton):
            if not spans['open'][1] <= m.start() < spans['close'][0]:
                line = ton[ton.rfind('\n', 0, m.start()) + 1:m.end()]
                issues.append('placement: a body outside the region: %r' % line[:80])
                break
    # EXCLUSIVITY: cut the three declared texts (target_text.cut), then only
    # admitted includes
    dele, ins = diff_lines(toff, cut(ton, t))
    ins_code = [l for l in ins if not STAMP_MOVES.match(l)]
    for l in ins_code:
        if re.match(r'^\s*#', l):
            mi = re.match(r'^#include <([^>]*)>$', l)
            if not mi or mi.group(1) not in headers:
                issues.append('guard lint: %r inserted' % l[:100])
    for fn, vw in HELPER.findall(ton):
        if vw not in vws:
            issues.append('guard lint: helper %s__w%s is no admitted level' % (fn, vw))
    # (c) the deletions: stamps, and one floor call per SIMD FUNC, replaced
    sel = {m.group(1): m.group(3) for m in SELECTOR.finditer(ton) if m.group(2) == m.group(1)}
    calls = [l for l in dele if not STAMP_MOVES.match(l)]
    replaced = {}
    for l in calls:
        m = FLOOR_CALL.match(l)
        if not m or m.group(1) not in sel:
            issues.append('(c) a deleted line that is no SIMD FUNC\'s floor call: %r' % l[:80])
            continue
        replaced[m.group(1)] = m.group(2)
    for fn, vw in sorted(sel.items()):
        if vw not in vws:
            issues.append('(c) %s calls __w%s, no admitted level' % (fn, vw))
        if fn not in replaced:
            issues.append('(c) SIMD FUNC %s replaced no floor call' % fn)
        elif '    return %s__w%s(%s);' % (fn, vw, replaced[fn]) not in ins_code:
            issues.append('(c) %s\'s level call does not forward its floor call\'s arguments' % fn)
    rdele, rins = diff_lines(toff, ton)
    # `aside`: the moved header lines' bytes (moved_headers_aside), guarded text too
    nbytes = aside + sum(len(l.encode('utf-8', 'surrogateescape')) + 1
                         for l in rins if not STAMP_MOVES.match(l))
    m = GUARDED.search(ton)
    if not m or int(m.group(1), 16) != nbytes:
        issues.append('(c) inserted %d bytes, SIMD_GUARDED_BYTES %s' % (nbytes, m.group(1) if m else 'absent'))
    # (d) the routing rule over the ON text
    _, why = routing_shape.check(ton)
    issues += ['(d) ' + w for w in why]
    mover = [l for l in dele if not STAMP_MOVES.match(l)] != [] or ins_code != []
    if mover and not sel:
        issues.append('a mover with no SIMD FUNC selector')
    return mover, sel, issues


# the planted controls: (name, the leg that must reject it, plant(ton, t))
def _move_guard(ton, t):
    rest = ton.replace(t['guard'], '', 1)
    m = re.search(r'^#\s*include\b.*\n', rest, re.M)
    return rest[:m.end()] + t['guard'] + rest[m.end():]


def _stray_if(ton, t):
    m = re.search(r'^#include <[^>]*>\n', ton, re.M)
    return ton[:m.start()] + '#if 1\n' + m.group(0) + '#endif\n' + ton[m.end():]


PLANTS = [
    ('a stray #pragma outside the region', 'guard lint',
     lambda ton, t: ton.replace(t['open'], '#pragma GCC optimize("O3")\n' + t['open'], 1)),
    ('the region close dropped', 'placement', lambda ton, t: ton.replace(t['close'], '', 1)),
    ('the guard after an #include', 'placement', _move_guard),
    ('a stray #if around a level include', 'guard lint', _stray_if),
    ('a line of a scalar floor deleted', '(c)',
     lambda ton, t: re.sub(r'^(static inline size_t \w+__body\(.*\)\n\{\n).*\n', r'\1', ton,
                           count=1, flags=re.M)),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pcrec', required=True)
    ap.add_argument('--levels', required=True, help='the simd_levels binary')
    ap.add_argument('--every', type=int, default=1)
    ap.add_argument('--jobs', type=int, default=4)
    a = ap.parse_args()
    passed, failed = [0], []

    def ok(msg=None):
        passed[0] += 1
        if msg:
            print('PASS: ' + msg)

    def bad(msg):
        failed.append(msg)
        print('FAIL: ' + msg)

    levels, alltargets = read_table(a.levels)
    print('levels: %s' % ', '.join('%s (%s, vw %s, needs %s)' % (l['stamp'], l['family'], l['vw'], l['needs'])
                                   for l in levels))
    if len(levels) >= LEVELS_FLOOR:
        ok('mf_levels(): %d levels (floor %d)' % (len(levels), LEVELS_FLOOR))
    else:
        bad('mf_levels(): %d levels < floor %d' % (len(levels), LEVELS_FLOOR))
    targets = [t for t in alltargets if t['family'] != '-' and admitted(t, levels)]
    print('targets: %s' % ', '.join('%s (admits %s)' % (t['name'], '+'.join(l['stamp'] for l in admitted(t, levels)))
                                    for t in targets))
    if len(targets) >= TARGETS_FLOOR:
        ok('targets with a level: %d (floor %d)' % (len(targets), TARGETS_FLOOR))
    else:
        bad('targets with a level: %d < floor %d' % (len(targets), TARGETS_FLOOR))
    for t in targets:
        if not (t['open'] and t['close'] and t['guard']):
            bad('target %s: the kit declares an empty region or guard text' % t['name'])

    corpus = es.enumerate_corpus(a.pcrec, TREE, 30)
    pats = sorted({p for _, _, p in corpus})
    pats = [p for i, p in enumerate(pats) if i % a.every == 0]
    pop = [('named:' + n, p, x) for n, p, x in NAMED]
    pop += [('corpus', p, x) for p in pats for x in ([], ['--engine=vm'])]
    print('== C18/C9: %d population cells (%d corpus patterns x 2 engines, %d named) x %d targets'
          % (len(pop), len(pats), len(NAMED), len(targets)))
    work = tempfile.mkdtemp(prefix='simdfloor.', dir=os.environ.get('TMPDIR'))

    def emit(p, extra, flag, d):
        os.makedirs(d, exist_ok=True)
        out = os.path.join(d, 'a.c')
        r = sh([a.pcrec, '-p', 'rx', '--features', 'all', flag] + extra + ['-o', out]
               + es._pattern_argv(a.pcrec, p), 60)
        if r is None or r.returncode:
            return None
        return out

    def pp(path):
        r = sh(['gcc', '-E', '-P', path], 60, cwd=os.path.dirname(path))
        return r.stdout.decode('utf-8', 'surrogateescape') if r and r.returncode == 0 else None

    def one(job):
        idx, (key, p, extra) = job
        base = os.path.join(work, str(idx))
        off = emit(p, extra, '-fno-memfn-simd', base + '/off')
        recs = []
        if off is not None:
            toff = open(off, encoding='utf-8', errors='surrogateescape').read()
            hoff = open(off[:-1] + 'h', 'rb').read()
        for ti, t in enumerate(targets):
            rec = {'key': key, 'p': p, 'extra': extra, 'target': t['name'], 'issues': [],
                   'mover': False, 'sel': {}}
            recs.append(rec)
            d = '%s/on%d' % (base, ti)
            on = emit(p, extra, '-fmemfn-simd=' + t['name'], d)
            if off is None or on is None:
                if (off is None) != (on is None):
                    rec['issues'].append('ON and OFF disagree on refusing')
                continue
            # a header line OFF also carries, moved ahead of the region, is no
            # new text: set aside for every leg; C9 compiles the artifact itself
            raw = open(on, encoding='utf-8', errors='surrogateescape').read()
            ton = moved_headers_aside(raw, toff, t)
            aside = len(raw.encode('utf-8', 'surrogateescape')) - len(ton.encode('utf-8', 'surrogateescape'))
            # and the OFF copies of a header ON moved out of its region (a
            # compound part's own lines, F1) set aside on OFF's side
            toffm = moved_out(toff, raw, t)
            if open(on[:-1] + 'h', 'rb').read() != hoff:
                rec['issues'].append('the .h moved under -fmemfn-simd (scaffolding in the header?)')
            adm = admitted(t, levels)
            mover, sel, issues = text_legs(toffm, ton, t, adm, aside)
            rec['issues'] += issues
            rec['mover'], rec['sel'] = mover, sel
            if not mover:
                continue
            rec['toff'], rec['ton'] = toffm, ton
            # (b) by the preprocessor: only the floor calls change
            onpp = on[:-2] + '_pp.c'
            with open(onpp, 'w', encoding='utf-8', errors='surrogateescape') as f:
                f.write(ton)
            offpp = off
            if toffm != toff:
                offpp = off[:-2] + '_moved.c'
                with open(offpp, 'w', encoding='utf-8', errors='surrogateescape') as f:
                    f.write(toffm)
            x, y = pp(offpp), pp(onpp)
            if x is None or y is None:
                rec['issues'].append('(b) preprocessing failed')
            else:
                dele, _ = diff_lines(x, y)
                okdel = [l for l in dele if FLOOR_CALL.match(l) and FLOOR_CALL.match(l).group(1) in sel]
                if len(dele) != len(sel) or len(okdel) != len(dele):
                    rec['issues'].append('(b) %d deleted line(s) for %d SIMD FUNC(s): %r'
                                         % (len(dele), len(sel), dele[:3]))
            # C9-x86: compile clean at every cell; the called helper by nm at -O0
            for march in C9_MARCH:
                cell = ' '.join(march) or '(no -march)'
                r = sh(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', '-c'] + march + ['-o', d + '/c9.o', on],
                       120, cwd=d)
                if r is None or r.returncode:
                    rec['issues'].append('C9 %s: does not compile -Werror: %s'
                                         % (cell, (r.stderr.decode()[-300:] if r else 'timeout')))
                    continue
                r = sh(['gcc', '-O0', '-c'] + march + ['-o', d + '/c9o0.o', on], 120, cwd=d)
                syms = subprocess.run(['nm', d + '/c9o0.o'], capture_output=True,
                                      text=True).stdout if r and r.returncode == 0 else ''
                defined = set(re.findall(r' t (\w+)$', syms, re.M))
                for fn, vw in sorted(sel.items()):
                    if '%s__w%s' % (fn, vw) not in defined:
                        rec['issues'].append('C9 %s: %s__w%s is not defined in the -O0 object' % (cell, fn, vw))
        subprocess.run(['rm', '-rf', base])
        return recs

    stats = {t['name']: {'movers': 0, 'funcs': 0, 'levels': {}} for t in targets}
    named_movers = set()
    first = {}
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        for recs in ex.map(one, enumerate(pop)):
            for rec in recs:
                for i in rec['issues']:
                    bad('%s %s %r %s: %s' % (rec['target'], rec['key'], rec['p'][:50], ' '.join(rec['extra']), i))
                if not rec['issues']:
                    ok()
                if rec['mover']:
                    s = stats[rec['target']]
                    s['movers'] += 1
                    s['funcs'] += len(rec['sel'])
                    for vw in rec['sel'].values():
                        st = next(l['stamp'] for l in levels if l['vw'] == vw)
                        s['levels'][st] = s['levels'].get(st, 0) + 1
                    if rec['key'].startswith('named:'):
                        named_movers.add((rec['target'], rec['key']))
                    if rec['target'] not in first and not rec['issues'] and 'ton' in rec:
                        first[rec['target']] = rec
    subprocess.run(['rm', '-rf', work])
    for t in targets:
        tn = t['name']
        s = stats[tn]
        print('%s: movers %d, SIMD FUNCs %d, selectors per level %s'
              % (tn, s['movers'], s['funcs'], ' '.join('%s=%d' % kv for kv in sorted(s['levels'].items()))))
        for n, _, _ in NAMED:
            if (tn, 'named:' + n) in named_movers:
                ok('%s: named witness %s is a mover' % (tn, n))
            else:
                bad('%s: named witness %s is NOT a mover (its bin is unreached)' % (tn, n))
        if tn not in FLOORS:
            bad('%s: a target with a level and no floor row (pin its measure)' % tn)
            continue
        fm, ff, fl = FLOORS[tn]
        lows = ['movers %d < %d' % (s['movers'], fm)] if s['movers'] < fm else []
        lows += ['SIMD FUNCs %d < %d' % (s['funcs'], ff)] if s['funcs'] < ff else []
        lows += ['%s selectors %d < %d' % (st, s['levels'].get(st, 0), v)
                 for st, v in sorted(fl.items()) if s['levels'].get(st, 0) < v]
        if lows:
            bad('%s: floor dropped (K35): %s' % (tn, '; '.join(lows)))
        else:
            ok('%s: population at or above its floors %r' % (tn, FLOORS[tn]))
        # the planted controls on this target's first clean mover
        rec = first.get(tn)
        if rec is None:
            bad('%s: no clean mover to plant the controls on' % tn)
            continue
        adm = admitted(t, levels)
        for name, leg, plant in PLANTS:
            planted = plant(rec['ton'], t)
            if planted == rec['ton']:
                bad('%s: control %s did not apply' % (tn, name))
                continue
            _, _, why = text_legs(rec['toff'], planted, t, adm)
            if any(w.startswith(leg) for w in why):
                ok('%s: control %s rejected by %s' % (tn, name, leg))
            else:
                bad('%s: control %s NOT rejected by %s (%r)' % (tn, name, leg, why[:2]))
    print('checks passed: %d' % passed[0])
    print('checks failed: %d' % len(failed))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
