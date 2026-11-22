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
      A selector whose own head says `always_inline` (the vector span's,
      R-47 U3, docs/design/memfn/block_span.md §10.2) takes the -O0 RULE
      instead: no symbol of its family (`<fn>`, `<fn>__*`) is defined, and
      each function calling it holds a `pshufb` (any register width); its
      control, judged by that rule ALONE, is an in-script plant (the level
      helper's pshufb replaced, text-neutral; V_O0_CONTROL; mech row S3516
      disables the rule).
      A -O0 compile that fails or times out is an issue for EVERY selector,
      the always_inline ones included (o0_compile_issues; mech row S3517).
      Mech row S3515 plants the same `__w32` in the emitter: both the V head
      leg and this rule reject it, so it proves the suite, not either leg.
THE HEAD FAMILY (U3): a SELECTOR or HELPER head is `static inline`, an optional
`__attribute__((...))` naming always_inline and/or unused, then `size_t` or
`int`; a HELPER is `<fn>__w<VW>` or the block helper `<fn>__w<VW>_b`. The
vector span's functions (`<p>_mf<h>_vs<j>` and its parts) carry their declared
heads (`V head`: always_inline, `__body` also unused; review r75 CHECKS-8),
with one planted control (V_PLANTS) on a clean V mover at V_CONTROL_TARGETS.

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
import types

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(TREE, 'scripts'))
sys.path.insert(0, HERE)
import emit_sweep as es  # noqa: E402
import routing_shape  # noqa: E402
import span_pins  # noqa: E402
from target_text import admitted, cut, moved_headers_aside, moved_out, read_table  # noqa: E402

# Floors per target, pinned AT the measure (deterministic counts of emitted
# text). History of the pre-seam single count: 44 at w16 (R-13); 33 at D172
# S3; 46 at code review r1 C1 (lane s3), both rungs under one `#if` chain.
# The target seam (lane u3floor) splits it per target and per level: 55 and
# 55 measured at both targets on the full corpus (2026-11-08, 5095 patterns;
# the corpus grew since r1 C1), every selector at its target's top level.
FLOORS = {
    # target: (movers, SIMD FUNCs, {level stamp: selectors calling it})
    'x86-64': (74, 74, {'w16': 74}),
    'x86-64-v3': (105, 105, {'w32': 105}),
}
# R-47 U4 re-pin, at the measure (lane bsu4p, 2026-11-22, 5700 corpus patterns x 2 engines + the
# named witnesses): x86-64 74 (the corpus grew since the 55 above; the vector span adds none: it
# renders no mover there, block_span.md §11); x86-64-v3 105 = those 74 + the 28 vector span sites
# of tests/memfn/span_seed.rxt at the default engine + the 3 span NAMED witnesses.
LEVELS_FLOOR = 2       # mf_levels() rows: w16, w32 (R-13)
TARGETS_FLOOR = 2      # targets whose family has a level (U2)
# NAMED is (name, pattern, extra flags [, targets]): the optional fourth column names the
# targets a witness is NAMED at (None: every target). The vector span's three witnesses
# are NAMED at x86-64-v3 ONLY: x86-64 renders no V mover (§11), so a span witness there
# would read "NOT a mover" on correct text (R-47 U4, block_span.md §10.2 [R71-1]).
NAMED = [
    # `(?i)cat` is a fixed-width `cover` artifact by default (D172 S3); since code
    # review r1 C1 its window search's SIMD FUNC is fn-pair's again, on the DEFAULT
    # path (S3 had moved the witness under `--memfn=no-window-search`)
    ('mod-i (DFA, ASSIGN)', '(?i)cat', []),
    ('union-select (DFA)', '(?i)union.*?select.*?from', []),
    ('union-select (no-DFA, ON_MISS)', '(?i)union.*?select.*?from', ['--engine=vm']),
    # [RUN-POS-SET] S2 re-aim (PCREC_MAX_REQ_RUN_POS_SET 2 -> 128): `\d+` and
    # `(a|b)+` became run POSITIONS (`[30-39]`, `[41426162]` joined the
    # caseless cat run), which left both bins unreached; `.` (255 members)
    # stays outside the run, so the run is the cube pair cat again.
    ('no-DFA ON_MISS', '(?i).+cat', ['--engine=vm']),
    ('VM hybrid', '(?i)(.)+cat', []),
    # R-47 U4: the vector span's three witnesses (block_span.md §10.2): HORS k 16 at B 16,
    # R7w k 24 at B 16, and HORS k 40 at width 4095, the one B = 32 witness
    ('span HORS k16 (B16)', '[0-9a-f]{17}', [], ('x86-64-v3',)),
    ('span R7w k24 (B16)', '[0-9]{25}', [], ('x86-64-v3',)),
    ('span HORS k40 (B32)', '[0-9a-f]{41}', ['--window-search-width=4095'], ('x86-64-v3',)),
]
# the three span witnesses' LITERAL floor, written before the build: SIMD FUNCs that are
# the vector span's (always_inline selector), one `vs0` selector each, at x86-64-v3
SPAN_NAMED_FLOOR = 3
# [COMPOUND] the artifact's own stamp lines: a compound's .c also carries its
# PARTS' lines under `<prefix>__<role>` (match_api.md §3.7¶1, not contract),
# and an artifact prefix never contains `__` (cli.md §1.6¶2's `parts` row).
STAMP_MOVES = re.compile(r'^#define (?:(?!__)\w)+_(TARGETS|MEMFN_FORMS|SIMD_GUARDED_BYTES) ')
TARGETS = re.compile(r'^#define (?:(?!__)\w)+_TARGETS "([^"]*)"$', re.M)
GUARDED = re.compile(r'^#define (?:(?!__)\w)+_SIMD_GUARDED_BYTES (0x[0-9a-f]+)ULL$', re.M)
# THE HEAD FAMILY (R-47 U3, block_span.md §10.2 [R71-4]): `static inline`, then an
# optional `__attribute__((...))` naming `always_inline` and/or `unused`, then
# `size_t` (ofsskip's FUNC) or `int` (the vector span's selector `<p>_mf<h>_vs<j>`).
# A HELPER is `<fn>__w<VW>` or the level's block helper `<fn>__w<VW>_b` [R-10].
HEAD = r'^static inline (?:__attribute__\(\((?P<attr>(?:always_inline|unused)(?:, (?:always_inline|unused))?)\)\) )?(?:size_t|int) '
SELECTOR = re.compile(HEAD + r'(?P<fn>\w+)\([^)]*\)\n\{\n    return (?P<callee>\w+)__w(?P<vw>\d+)\(.*\);\n\}$', re.M)
HELPER = re.compile(HEAD + r'(\w+)__w(\d+)(?:_b)?\(', re.M)
# CHECKS-8 (review r75): the vector span's functions, by NAME (`<p>_mf<h>_vs<j>` and
# its parts), each with its declared head: `always_inline` and `int`, `__body`
# also `unused` (block_span.md §5: its OFF and ON head lines are one line).
VHEAD = re.compile(r'^static inline (?:__attribute__\(\(([^)]*)\)\) )?(\w+) (\w+_mf\d+_vs\d+)(__\w+)?\(', re.M)
# A V selector's -O0 path is fixed by ITS head (always_inline): the call site of
# the selector, its CALLER, is found in the text (a column-0 definition line).
DEF_LINE = re.compile(r'^[A-Za-z_][\w \*]*?\b(\w+)\(')
PSHUFB = re.compile(r'\bv?pshufb\b')
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
    for _, fn, vw in HELPER.findall(ton):
        if vw not in vws:
            issues.append('guard lint: helper %s__w%s is no admitted level' % (fn, vw))
    # (c) the deletions: stamps, and one floor call per SIMD FUNC, replaced
    sel = {m.group('fn'): m.group('vw') for m in SELECTOR.finditer(ton) if m.group('callee') == m.group('fn')}
    # CHECKS-8: every vector span function's head is the declared one
    for m in VHEAD.finditer(ton):
        want = 'always_inline, unused' if m.group(4) == '__body' else 'always_inline'
        if m.group(1) != want or m.group(2) != 'int':
            issues.append('V head: %s%s is `%s %s`, expected `__attribute__((%s)) int`'
                          % (m.group(3), m.group(4) or '', m.group(1), m.group(2), want))
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


def always_inline_sel(ton):
    """The SIMD FUNC selectors whose own head says `always_inline` (the -O0
    rule's path, R-7/R-8: fixed by the SELECTOR's head, never the helper's)."""
    return {m.group('fn') for m in SELECTOR.finditer(ton)
            if m.group('callee') == m.group('fn') and 'always_inline' in (m.group('attr') or '')}


def callers_of(ton, fn):
    """The functions whose bodies call `fn`, read from the text: each line
    belongs to the nearest column-0 definition line above it."""
    call = re.compile(r'\b%s\(' % re.escape(fn))
    out, cur = set(), None
    for ln in ton.split('\n'):
        m = DEF_LINE.match(ln)
        if m and not ln.rstrip().endswith(';'):
            cur = m.group(1)
            continue
        if cur and cur != fn and not cur.startswith(fn + '__') and call.search(ln):
            out.add(cur)
    return out


def o0_inline_issues(ton, sel, obj, cell):
    """The -O0 rule for a selector whose head says always_inline (block_span.md
    §10.2 [R-7, R-8]): in the -O0 object (1) NO symbol of the selector's family
    (`<fn>`, `<fn>__*`) is defined, and (2) each function calling the selector
    holds at least one `pshufb` (`pshufb` or `vpshufb`, any register width: the
    B = 16 rung is xmm only). Its control, a level helper holding no
    shuffle (leg 2), is the in-script V_O0_CONTROL (mech row S3516)."""
    issues = []
    syms = subprocess.run(['nm', obj], capture_output=True, text=True).stdout
    defined = set(re.findall(r' [tT] (\w+)$', syms, re.M))
    for fn in sorted(always_inline_sel(ton) & set(sel)):
        fam = sorted(s for s in defined if s == fn or s.startswith(fn + '__'))
        if fam:
            issues.append('C9 %s -O0: %s is always_inline, yet its family defines %s' % (cell, fn, ', '.join(fam)))
        who = sorted(callers_of(ton, fn) & defined)
        if not who:
            issues.append('C9 %s -O0: no defined function calls %s' % (cell, fn))
        for c in who:
            d = subprocess.run(['objdump', '-d', '--no-show-raw-insn', '--disassemble=' + c, obj],
                               capture_output=True, text=True).stdout
            if not PSHUFB.search(d):
                issues.append('C9 %s -O0: %s, which calls %s, holds no pshufb' % (cell, c, fn))
    return issues


def o0_compile_issues(r, sel, cell, obj, ton):
    """The -O0 leg of C9 for one cell, from its compile result `r` (None: timed
    out). A compile that did not succeed is an issue for EVERY selector, the
    always_inline ones too (their symbols are never defined at -O0, so the
    object cannot vouch for them; r76 CHECKS-2: the failed compile was once
    green for every V selector); a successful one is the -O0 rule's."""
    if r is None or r.returncode:
        why = 'timeout' if r is None else 'rc %d: %s' % (r.returncode, r.stderr.decode(errors='replace')[-200:])
        return ['C9 %s: %s: the -O0 compile failed (%s)' % (cell, fn, why) for fn in sorted(sel)] \
            or ['C9 %s: the -O0 compile failed (%s)' % (cell, why)]
    return o0_inline_issues(ton, sel, obj, cell)


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

# the vector span's planted control (CHECKS-8), on a target's first clean V mover:
# `__body`'s head loses always_inline, answer-identical and invisible to (c),
# whose OFF and ON head lines both lose it
V_PLANTS = [
    ("__body's always_inline dropped", 'V head',
     lambda ton, t: re.sub(r'(?m)^(static inline __attribute__\(\()always_inline, (unused\)\) int \w+_mf\d+_vs\d+__body\()',
                           r'\1\2', ton, count=1)),
]
# the -O0 rule's own control (CHECKS-1), judged by o0_inline_issues ALONE, on the
# same clean V mover: every head stays as emitted, but the level helper's
# `_mm_shuffle_epi8` becomes `_mm_packus_epi16` (same arity, same 16 characters),
# so at -O0 the function calling the selector holds no pshufb (rule leg 2) while
# the text legs, (c)'s byte count included, see nothing. Applied to the artifact
# as emitted (it is compiled) and to the preprocessed text the text legs read,
# at the V_CONTROL_TARGETS' own -march.
V_O0_CONTROL = ("the level helper's pshufb replaced by a packuswb",
                lambda raw: raw.replace('_mm_shuffle_epi8(', '_mm_packus_epi16('))
# the targets whose population must hold a clean V mover for V_PLANTS (K35): the
# 32-byte one; at x86-64 (w16 only) the V selector calls `__body` (no mover)
V_CONTROL_TARGETS = ('x86-64-v3',)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pcrec', required=True)
    ap.add_argument('--levels', required=True, help='the simd_levels binary')
    ap.add_argument('--harness', required=True, help='the pcrec-harness binary (the span pins\' k source)')
    ap.add_argument('--trace', required=True, help='the harness build linked against the traced kit')
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
    pop = [('named:' + e[0], e[1], e[2]) for e in NAMED]
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
            rec['toff'], rec['ton'], rec['raw'] = toffm, ton, raw
            rec['hdr'] = hoff   # the artifact's own a.h: it #includes it
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
                rec['issues'] += o0_compile_issues(r, sel, cell, d + '/c9o0.o', ton)
                if r is None or r.returncode:
                    continue
                syms = subprocess.run(['nm', d + '/c9o0.o'], capture_output=True, text=True).stdout
                defined = set(re.findall(r' t (\w+)$', syms, re.M))
                inl = always_inline_sel(ton)
                for fn, vw in sorted(sel.items()):
                    if fn in inl:
                        continue
                    if '%s__w%s' % (fn, vw) not in defined:
                        rec['issues'].append('C9 %s: %s__w%s is not defined in the -O0 object' % (cell, fn, vw))
        subprocess.run(['rm', '-rf', base])
        return recs

    stats = {t['name']: {'movers': 0, 'funcs': 0, 'levels': {}} for t in targets}
    named_movers = set()
    span_named = {}        # (target, key) -> the vector span's selectors the witness renders
    first, first_v = {}, {}
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
                        st = next((l['stamp'] for l in levels if l['vw'] == vw), 'w' + vw)   # an unadmitted width is the lint's to name, never a crash (S3535)
                        s['levels'][st] = s['levels'].get(st, 0) + 1
                    if rec['key'].startswith('named:'):
                        named_movers.add((rec['target'], rec['key']))
                        if rec['key'].startswith('named:span') and 'ton' in rec:
                            span_named[(rec['target'], rec['key'])] = sorted(always_inline_sel(rec['ton']) & set(rec['sel']))
                    if rec['target'] not in first and not rec['issues'] and 'ton' in rec:
                        first[rec['target']] = rec
                    if rec['target'] not in first_v and not rec['issues'] and 'ton' in rec \
                            and always_inline_sel(rec['ton']) & set(rec['sel']):
                        first_v[rec['target']] = rec
    subprocess.run(['rm', '-rf', work])
    for t in targets:
        tn = t['name']
        s = stats[tn]
        print('%s: movers %d, SIMD FUNCs %d, selectors per level %s'
              % (tn, s['movers'], s['funcs'], ' '.join('%s=%d' % kv for kv in sorted(s['levels'].items()))))
        for e in NAMED:
            n = e[0]
            if len(e) > 3 and tn not in e[3]:
                continue
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
        vrec = first_v.get(tn)
        if vrec is None:
            if tn in V_CONTROL_TARGETS:
                bad('%s: no clean vector span mover to plant the V controls on' % tn)
            continue
        for name, leg, plant in V_PLANTS:
            planted = plant(vrec['ton'], t)
            if planted == vrec['ton']:
                bad('%s: control %s did not apply' % (tn, name))
                continue
            _, _, why = text_legs(vrec['toff'], planted, t, adm)
            if any(w.startswith(leg) for w in why):
                ok('%s: control %s rejected by %s' % (tn, name, leg))
            else:
                bad('%s: control %s NOT rejected by %s (%r)' % (tn, name, leg, why[:2]))
        # CHECKS-1: the -O0 rule alone rejects a selector that does not reach its vector helper
        name, plant = V_O0_CONTROL
        planted = plant(vrec['raw'])
        planted_ton = plant(vrec['ton'])
        if planted == vrec['raw'] or planted_ton == vrec['ton']:
            bad('%s: control %s did not apply' % (tn, name))
        elif text_legs(vrec['toff'], planted_ton, t, adm)[2]:
            bad('%s: control %s is seen by the text legs (%r)'
                % (tn, name, text_legs(vrec['toff'], planted_ton, t, adm)[2][:2]))
        else:
            ok('%s: control %s is invisible to the text legs' % (tn, name))
            cd = tempfile.mkdtemp(prefix='o0ctl.', dir=os.environ.get('TMPDIR'))
            with open(cd + '/a.c', 'w', encoding='utf-8', errors='surrogateescape') as f:
                f.write(planted)
            with open(cd + '/a.h', 'wb') as f:
                f.write(vrec['hdr'])
            r = sh(['gcc', '-O0', '-c', '-march=' + tn, '-o', cd + '/a.o', cd + '/a.c'], 120, cwd=cd)
            if r is None or r.returncode:
                bad('%s: control %s did not compile at -O0' % (tn, name))
            else:
                why = o0_inline_issues(planted, vrec['sel'], cd + '/a.o', tn)
                if any(' -O0: ' in w and 'holds no pshufb' in w for w in why):
                    ok('%s: control %s rejected by the -O0 rule alone' % (tn, name))
                else:
                    bad('%s: control %s NOT rejected by the -O0 rule (%r)' % (tn, name, why[:2]))
            subprocess.run(['rm', '-rf', cd])
        # CHECKS-2: a failed or timed-out -O0 compile is an issue for every selector, V included
        for what, fake in (('failed', types.SimpleNamespace(returncode=1, stderr=b'x')), ('timed-out', None)):
            why = o0_compile_issues(fake, vrec['sel'], tn, '/nonexistent.o', vrec['ton'])
            miss = [fn for fn in sorted(vrec['sel']) if not any(': %s: ' % fn in w for w in why)]
            if miss or not why:
                bad('%s: a %s -O0 compile leaves selector(s) %s without an issue' % (tn, what, miss))
            else:
                ok('%s: a %s -O0 compile is an issue for each of %d selector(s)' % (tn, what, len(vrec['sel'])))
    # R-47 U4: the vector span's three NAMED witnesses carry one `vs0` selector each at
    # x86-64-v3, and 3 span SIMD FUNCs in all (the literal floor, written before the build)
    for tn in sorted({t for t, _ in span_named} | {t['name'] for t in targets if t['name'] == 'x86-64-v3'}):
        got = {k: v for (t, k), v in span_named.items() if t == tn}
        funcs = sum(len(v) for v in got.values())
        odd = [k for k, v in sorted(got.items()) if len(v) != 1 or not re.search(r'_mf\d+_vs0$', v[0])]
        if odd or funcs < SPAN_NAMED_FLOOR:
            bad('%s: the span witnesses hold %d span SIMD FUNCs (floor %d); not one `vs0` selector: %r'
                % (tn, funcs, SPAN_NAMED_FLOOR, odd))
        else:
            ok('%s: the three span witnesses render %d span SIMD FUNCs, one `vs0` selector each (floor %d)'
               % (tn, funcs, SPAN_NAMED_FLOOR))
    # R-47 U4: the T-table pin cells and SPAN-SEED's V-site census (tests/memfn/span_pins.py)
    span_pins.run(a.pcrec, a.harness, a.trace, ok, bad, a.jobs)
    print('checks passed: %d' % passed[0])
    print('checks failed: %d' % len(failed))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
