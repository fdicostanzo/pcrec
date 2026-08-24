#!/usr/bin/env python3
"""tests/recursion/gen_corpus.py -- the GENERATOR that wrote every expectation
in tests/recursion/*.rxt, and the reason none of them was typed by hand.

THE RULE IT ENFORCES (tests/CLAUDE.md's oracle discipline): every match/nomatch
expectation, INCLUDING every per-group `g` line, is produced by libpcre2 10.46
BEFORE it is written -- via docs/design/subroutines_measurements/probes/
sr_oracle.py, which borrows la_oracle.py, which borrows br_oracle.py, which
borrows pcre2_ctypes.py (three levels of borrowing, no fourth copy of the
binding). The generator never asks pcrec anything: an expectation derived from
the compiler under test is not an expectation.

WHY THERE IS NO PYTHON ARM, UNLIKE EVERY EARLIER GENERATED CORPUS. Design
docs/design/subroutines_design.md SS10.1 MEASURED it: python3's `re` has no
subroutine-call construct AT ALL -- not "different semantics", an ABSENCE.
Every one of the nine call spellings plus both zero spellings raises a python
`re.error` at compile time. So there is nothing to compare against and no
`# pcre2-only` marking to compute; every block's sole oracle is libpcre2, and
that is stated once here rather than argued per block. D27's own note (design
SS10.1 item 2) singles out `\\1` and `(?P=n)` as a trap -- they compile in
python and mean the DIFFERENT construct `backrefs` owns -- so this generator
never touches python at all, rather than touching it and mismarking those two
spellings' population as if it were this module's.

THE {0}-CALLEE IDIOM STANDS IN FOR `(?(DEFINE)...)` THROUGHOUT. Module
`conditionals` owns the `(?(` doorway until D71 decision 4's registry row
lands (docs/dev/decisions.md D71, item 4; [DD-14] wave F, not started at the
time this corpus was written) -- so a `(?(DEFINE)...)` cell in THIS module's
corpus would need a module this module does not ship. Design SS2.5 measured
the exact substitute: `(?:(?<g>BODY)){0}` is a REPEAT of a GROUP, base syntax,
needing no module beyond `recursion` (plus `named-groups` for a named callee)
-- "MEASURED working on 10.46 for plain, recursive, atomic and rung-bearing
callees" (SS4.4c). Every cell below that the design describes via DEFINE is
rendered with `{0}` instead, oracle-verified identical to the DEFINE form
where the design gives one to compare against (see the header comment on each
file for the specific comparison run).

RE-RUN IT after changing a cell list:  python3 tests/recursion/gen_corpus.py
It rewrites the .rxt files in place and prints a per-file census. A second run
with no source change must be a no-op (`git diff` empty) -- that is one of the
lane's own checks, not asserted by this script.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "docs", "design",
                                "subroutines_measurements", "probes"))
try:
    import sr_oracle as O
except Exception as e:                                      # noqa: BLE001
    sys.stderr.write("gen_corpus: libpcre2 unavailable: %s\n" % e)
    sys.exit(3)
if O.SELFCHECK:
    sys.stderr.write("gen_corpus: oracle self-check failed: %r\n" % (O.SELFCHECK,))
    sys.exit(3)

PCREC = os.path.join(ROOT, "build", "pcrec")
SCRATCH_OUT = os.environ.get(
    "SR_GEN_SCRATCH",
    "/tmp/claude-1001/-home-duxevents-pcrec/57edc75c-76aa-4052-bcd0-9f13379119a3"
    "/scratchpad/srCorpus/probe_out.c")
os.makedirs(os.path.dirname(SCRATCH_OUT), exist_ok=True)


def esc(s):
    """A subject as the .rxt format spells it: double-quoted, with exactly the
    escapes docs/testing.md lists and no others."""
    out = ['"']
    for ch in s:
        b = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == '\\':
            out.append('\\\\')
        elif ch == '\n':
            out.append('\\n')
        elif ch == '\t':
            out.append('\\t')
        elif ch == '\r':
            out.append('\\r')
        elif 0x20 <= b < 0x7f:
            out.append(ch)
        else:
            out.append('\\x%02x' % b)
    out.append('"')
    return ''.join(out)


def pad(groups, n):
    """PAD TO `n` WITH UNSET (None here), oracle-side only -- see
    tests/backrefs/gen_corpus.py's identical helper for why: pcre2_match's
    ovector truncates trailing unset pairs, and comparing an unpadded tuple
    against a fixed `groups=` count would silently mis-render group lines
    for any cell whose LAST group happens not to participate."""
    g = list(groups[:n])
    while len(g) < n:
        g.append(None)
    return tuple(g)


def pcre2_answer(pat, subj, sp):
    """('m', start, end, groups) | ('n',) | ('ERR', msg) | ('rc', code, msg)."""
    try:
        c = O.compile(pat)
    except Exception as e:                                  # noqa: BLE001
        return ('ERR', str(e))
    try:
        r = c.search(subj, sp)
    except O.pcre2.Pcre2Error as e:
        # A give-up code (e.g. rc -52 "nested recursion at the same subject
        # position") rather than a compile error or an ordinary NOMATCH --
        # Compiled.search raises for any negative rc other than NOMATCH.
        return ('rc', str(e))
    if r is None:
        return ('n',)
    groups = tuple((-1, -1) if g is None else g for g in r[1])
    return ('m', r[0][0], r[0][1], groups)


def pcrec_refuses(pat, features=None):
    """Run today's built `build/pcrec` (this worktree, off main -- no
    subroutine-call producer exists) on `pat` and return (nonzero, message).
    NEVER pass -o /dev/null: docs/design/subroutines_measurements/out/
    CLAUDE.md's own instrument-defect log records that doing exactly this
    makes every COMPILING cell read 'Permission denied' instead of the
    diagnostic under test -- a real scratch file is used instead."""
    cmd = [PCREC, "-p", "rx"]
    if features:
        cmd += ["--features", features]
    cmd += ["--emit-main", "-o", SCRATCH_OUT, pat]
    r = subprocess.run(cmd, capture_output=True, text=True)
    msg = (r.stderr.strip() or r.stdout.strip())
    return r.returncode != 0, msg


class B:
    """One `pattern` block. `cells` is a list of case specs:
      ('m', subj)            -- assert a match at startpos 0
      ('n', subj)            -- assert no match at startpos 0
      ('ms', subj, sp)       -- assert a match at startpos `sp`
      ('ns', subj, sp)       -- assert no match at startpos `sp`
    Every one is resolved against libpcre2 HERE -- the tuple's own 'm'/'n'
    tag is only a hint about what the author expected; render() always
    queries the oracle and writes what it actually says, so a wrong hint
    shows up as a visibly wrong .rxt line rather than a silently accepted
    typo."""

    def __init__(self, pat, cells, features, groups=0, note=None, wave=None,
                 parked=None):
        self.pat = pat
        self.cells = cells
        self.features = features
        self.groups = groups
        self.note = note
        # [DD-14 wave B+C, code lane] `wave` NAMES THE WAVE THAT WILL MAKE THIS
        # BLOCK COMPILE, and until then the block is rendered as a `perr` with
        # its ORACLE ANSWER CARRIED IN A COMMENT.
        #
        # THIS IS APPROACH.md SS7's `expected-unsupported` POLICY, not a
        # weakening of the corpus (docs/testing.md, "adding a per-component
        # directory", step 2: "pin the compile error via `perr` ... this keeps
        # the suite green at every milestone rather than red until the
        # component lands", step 3: "once the component is implemented,
        # replace or extend those `perr` blocks with real cases").
        #
        # IT COSTS NOTHING AND IS RECOVERED MECHANICALLY. The oracle is still
        # driven for every cell on every run — the answer is written into the
        # block as `# WAVE <w>: libpcre2 says ...` — so wave D's edit is to
        # delete one keyword argument and re-run this generator, and the
        # `m`/`n`/`g` lines that come back are the ones libpcre2 gives THEN,
        # not a transcription of what it gave now. A block whose refusal STOPS
        # EXISTING fails the same guard `PERR` carries, so the marker cannot
        # outlive the wave it names.
        #
        # WHY THE `\g` FAMILY IS THE ONLY USER TODAY: design SS8.1 requires
        # the two `\g` registry rows to stay `unbuilt` until wave D wires
        # their port, because D65 flips `built` from the PORT's answer and a
        # wave that flipped them while the emitter could not compile the
        # spelling would ship a compliance index that lies. Wave B+C's own
        # landing bar pins that state.
        self.wave = wave
        # [DD-14 wave B+C, code lane] `parked` MOVES THE BLOCK OUT OF THE LIVE
        # CORPUS AND INTO tests/known_fail/, leaving a comment stanza here that
        # says where it went and why.
        #
        # It is the mechanism this project already uses for a cell where a
        # RULING IS OWED rather than a bug is open (tests/known_fail/'s own
        # CLAUDE.md, on U9: "the cells stay, they stay loud, and if pcrec is
        # ever changed to reproduce it this file FIRES"). known_fail is
        # excluded from `make test` and RUN by the ratchet, so a parked cell
        # that starts passing is a loud failure rather than a silent one.
        #
        # It is NOT for a construct that has not landed — that is `wave` above,
        # and the two are deliberately different renderings: `wave` pins a
        # REFUSAL that must exist, `parked` pins an ANSWER that pcrec currently
        # disagrees with.
        self.parked = parked


class GU:
    """A give-up block (design SS10.3's `gu <code> "<subject>"` directive --
    MEASURED against the landed wave A grammar, worktrees/srA's
    tests/harness/run.sh: `^gu[[:space:]]+(steps|frames|work|recurse)
    [[:space:]]+\"(.*)\"[[:space:]]*$`, no startpos variant. `gu` REQUIRES a
    subject; a bare `gu <code>` with no subject is a hard parse error under
    that grammar -- an earlier draft of this generator omitted it entirely,
    caught by the manager's review before merge). Not oracle-checked
    against a libpcre2 MATCH -- pcrec's give-up is its own artifact
    property (the depth capacity, D71.1), not something libpcre2 has an
    equivalent code for. `oracle_note` records what libpcre2 itself does on
    the same cell (almost always its OWN give-up, rc -52) as a cross-check
    that the shape is genuinely non-terminating and not merely slow, and
    the same `subj` field is now ALSO what gets written into the directive
    line -- one field, one meaning, the PERR `gate_features` lesson applied
    before it could recur here too."""

    def __init__(self, pat, subj, code, features, note, oracle_note=True,
                 parked=None):
        self.parked = parked      # see B.__init__'s own `parked`
        self.pat = pat
        self.subj = subj
        self.code = code
        self.features = features
        self.note = note
        self.oracle_note = oracle_note


class PERR:
    """A block asserting `pcrec` refuses to compile -- either because
    libpcre2 ALSO refuses (a real syntax error, `kind='pcre2'`) or because
    pcrec's registry gate is closed / the module has no producer yet
    (`kind='pcrec'`, checked against build/pcrec directly). `.rxt`'s `perr`
    only asserts a nonzero exit (docs/testing.md); the message is recorded
    as a comment for a human reader, never checked by the harness.

    `features`, when given, is used for BOTH the verification call to
    build/pcrec AND the `.rxt` file's own `features` line -- they must be
    the SAME string, or the corpus would verify one gate and pin another.
    (An earlier draft of this generator kept them as two separate fields,
    `features` and `gate_features`, and only the second reached
    build/pcrec -- so gated.rxt's 'enabled but not implemented' cells were
    verified under `--features recursion` but WRITTEN with no `features`
    line at all, meaning the harness would actually have exercised the
    CLOSED-gate wording while the comment claimed the enabled one. Caught
    by this lane's own independent features check, fixed by collapsing to
    one field.)"""

    def __init__(self, pat, kind, features=None, note=None):
        self.pat = pat
        self.kind = kind
        self.features = features
        self.note = note


def render_m_cells(pat, cells, groups, lines, census):
    for c in cells:
        tag = c[0]
        subj = c[1]
        sp = c[2] if len(c) > 2 else 0
        a = pcre2_answer(pat, subj, sp)
        if a[0] == 'ERR':
            raise SystemExit("gen_corpus: %r refuses to compile in libpcre2: %s"
                             % (pat, a[1]))
        if a[0] == 'rc':
            raise SystemExit("gen_corpus: %r on %r gave libpcre2 a give-up "
                             "(%s) where a match/nomatch cell was wanted -- "
                             "use GU instead" % (pat, subj, a[1]))
        if a[0] == 'n':
            lines.append(('ns %d %s' % (sp, esc(subj))) if sp
                         else ('n %s' % esc(subj)))
            if tag == 'm' or tag == 'ms':
                lines.append('# NOTE: author expected a match here; libpcre2 says '
                             'nomatch -- the ORACLE rules, not the hint')
        else:
            lines.append(('ms %d %s %d %d' % (sp, esc(subj), a[1], a[2])) if sp
                         else ('m %s %d %d' % (esc(subj), a[1], a[2])))
            if tag == 'n' or tag == 'ns':
                lines.append('# NOTE: author expected nomatch here; libpcre2 '
                             'MATCHES -- the ORACLE rules, not the hint')
            for g, gv in enumerate(pad(a[3], groups), 1):
                lo, hi = (-1, -1) if gv is None else gv
                lines.append('g %d %d %d' % (g, lo, hi))
        census['cells'] += 1


def render(block, census):
    lines = []
    if getattr(block, 'parked', None):
        return ['# ' + ln for ln in
                ('PARKED IN tests/known_fail/ -- NOT A CELL IN THIS FILE.\n'
                 'pattern: %s\n%s' % (block.pat, block.parked)).split('\n')]
    if isinstance(block, PERR):
        census['perr'] += 1
        if block.note:
            lines.append('# ' + block.note)
        if block.kind == 'pcre2':
            a = pcre2_answer(block.pat, "", 0)
            if a[0] != 'ERR':
                raise SystemExit('gen_corpus: %r marked kind=pcre2 but '
                                 'libpcre2 compiles it (%r)' % (block.pat, a))
            lines.append('# libpcre2 ALSO refuses to compile this: %s' % a[1])
        else:
            bad, msg = pcrec_refuses(block.pat, block.features)
            if not bad:
                raise SystemExit('gen_corpus: %r marked kind=pcrec but '
                                 'build/pcrec (main, no producer) COMPILES '
                                 'it -- the refusal this cell pins does not '
                                 'exist' % block.pat)
            feat_note = (' under --features %s' % block.features
                        if block.features else ' under std1 (no --features)')
            lines.append("# MEASURED, build/pcrec off main%s: %s" % (feat_note, msg))
        lines.append('pattern ' + block.pat)
        if block.features:
            lines.append('features ' + block.features)
        lines.append('perr')
        return lines

    if isinstance(block, GU):
        census['gu'] += 1
        if block.note:
            lines.append('# ' + block.note)
        if block.oracle_note:
            a = pcre2_answer(block.pat, block.subj, 0)
            if a[0] == 'rc':
                lines.append('# libpcre2 10.46 on the SAME cell: %s '
                             '(its own guard, not pcrec\'s -- cross-checked '
                             'for shape only)' % a[1])
            elif a[0] == 'm':
                lines.append('# libpcre2 10.46 on the SAME cell: MATCHES %r -- '
                             'a give-up for pcrec is not necessarily a give-up '
                             'for 10.46; the depth CAPACITY is the artifact '
                             'fact being pinned, not libpcre2 agreement'
                             % (a[1], a[2]))
            elif a[0] == 'n':
                lines.append('# libpcre2 10.46 on the SAME cell: nomatch')
        lines.append('pattern ' + block.pat)
        if block.features:
            lines.append('features ' + block.features)
        lines.append('gu %s %s' % (block.code, esc(block.subj)))
        if block.code == 'frames':
            lines.append('# D71.1 (docs/dev/decisions.md): the DEFAULT '
                         'artifact reports a deep/runaway call as '
                         'PCREC_ERR_FRAMES -- the depth counter '
                         '(PCREC_ERR_RECURSE) is a diagnostic-generation-'
                         'axis-only build, never the default one. If Frank '
                         'revisits D71.1, the diagnostic-axis expectation '
                         'for THIS cell is: gu recurse')
        return lines

    # ordinary B block
    if block.wave:
        # The expected-unsupported rendering — see B.__init__'s `wave`.
        census['perr'] += 1
        if block.note:
            lines.append('# ' + block.note)
        lines.append('# EXPECTED-UNSUPPORTED, WAVE %s (APPROACH.md SS7, '
                     'docs/testing.md step 2). The construct is REAL and this '
                     'cell is oracle-verified below; pcrec cannot compile it '
                     'until wave %s wires the port, so the block pins the '
                     'REFUSAL and carries the answer. Wave %s deletes the '
                     '`wave=` argument in gen_corpus.py and re-runs it.'
                     % (block.wave, block.wave, block.wave))
        for c in block.cells:
            tag, subj = c[0], c[1]
            sp = c[2] if len(c) > 2 else 0
            a = pcre2_answer(block.pat, subj, sp)
            if a[0] == 'ERR':
                raise SystemExit("gen_corpus: %r refuses to compile in "
                                 "libpcre2: %s" % (block.pat, a[1]))
            if a[0] == 'n':
                lines.append('# WAVE %s ORACLE: %r at startpos %d -> nomatch'
                             % (block.wave, subj, sp))
            elif a[0] == 'm':
                lines.append('# WAVE %s ORACLE: %r at startpos %d -> (%d,%d)%s'
                             % (block.wave, subj, sp, a[1], a[2],
                                ''.join(' g%d=%s' % (g, '(unset)' if gv is None
                                                     else '(%d,%d)' % gv)
                                        for g, gv in
                                        enumerate(pad(a[3], block.groups), 1))))
            else:
                lines.append('# WAVE %s ORACLE: %r at startpos %d -> %s'
                             % (block.wave, subj, sp, a[1]))
        bad, msg = pcrec_refuses(block.pat, block.features)
        if not bad:
            raise SystemExit('gen_corpus: %r is marked wave=%s but '
                             'build/pcrec COMPILES it -- the wave has landed '
                             'and the marker must go' % (block.pat, block.wave))
        lines.append('# MEASURED, this build: %s' % msg)
        lines.append('pattern ' + block.pat)
        if block.features:
            lines.append('features ' + block.features)
        lines.append('perr')
        return lines

    census['blocks'] += 1
    if block.note:
        lines.append('# ' + block.note)
    lines.append('pattern ' + block.pat)
    if block.features:
        lines.append('features ' + block.features)
    render_m_cells(block.pat, block.cells, block.groups, lines, census)
    return lines


def write(fname, header, sections):
    census = {'cells': 0, 'blocks': 0, 'perr': 0, 'gu': 0}
    out = [header.rstrip('\n'), '']
    for title, blocks in sections:
        out.append('# ' + '=' * 68)
        out.append('# ' + title)
        out.append('# ' + '=' * 68)
        out.append('')
        for b in blocks:
            out.extend(render(b, census))
            out.append('')
    path = os.path.join(HERE, fname)
    with open(path, 'w') as f:
        f.write('\n'.join(out).rstrip('\n') + '\n')
    print('%-20s %4d blocks  %4d m/n cells  %2d perr  %2d gu'
          % (fname, census['blocks'], census['cells'], census['perr'], census['gu']))
    return census


HDR = """# tests/recursion/%s -- module `recursion` ([DD-14]): %s
#
# GENERATED BY tests/recursion/gen_corpus.py, and that is a property rather
# than a convenience: every expectation below -- including every `g` line --
# was produced by driving the cell through libpcre2 10.46 (via the committed
# ctypes binding at docs/design/subroutines_measurements/probes/sr_oracle.py,
# which borrows la_oracle.py -> br_oracle.py -> pcre2_ctypes.py) BEFORE it was
# written. The generator never asks pcrec anything.
#
# THE SOLE ORACLE IS LIBPCRE2 -- THERE IS NO PYTHON ARM, AND THAT IS AN
# ABSENCE RATHER THAN A DIVERGENCE (design SS10.1). python3 `re` has no
# subroutine-call construct at all: every one of the nine call spellings plus
# both zero spellings raises `re.error` at compile time. `\\\\1` and `(?P=n)`
# DO compile in python, but they are `backrefs`' reference construct, not this
# module's call construct (design SS2.1's one-cell discriminator is why
# `spellings.rxt` opens with it) -- so marking this corpus python-verifiable
# on the strength of those two spellings would be checking the wrong module.
#
# `(?(DEFINE)...)` DOES NOT APPEAR ANYWHERE IN THIS CORPUS. It is module
# `conditionals`'s construct until D71 decision 4's registry row lands
# ([DD-14] wave F, not started when this corpus was written); every callee-
# only body below uses the oracle-verified `{0}`-callee idiom instead
# (design SS2.5/SS4.4c).
#
# NOTHING IN src/ IMPLEMENTS A SUBROUTINE CALL YET. Every ordinary `m`/`n`
# block in this corpus is therefore EXPECTED to report a pattern-compile
# failure under today's harness (`requires module 'recursion'`) -- that is
# the correct, documented state before [DD-14] wave B+C lands (docs/
# testing.md's "expected-unsupported" policy), not a corpus defect.
#
# Design: docs/design/subroutines_design.md. Decisions: docs/dev/decisions.md
# D71 (the give-up-code axis, D71.1) and D72 (PCREC_ERR_INTERNAL).
"""


# ---------------------------------------------------------------------------
# shared feature strings
# ---------------------------------------------------------------------------
RC = "recursion"
RCN = "recursion,named-groups"
RCB = "recursion,backrefs"
RCA = "recursion,atomic-groups"
RCL = "recursion,lookaround"
RCLA = "recursion,lookaround,atomic-groups"
# [DD-14 wave B+C, code lane] `backrefs` JOINED, and it is a CORRECTION to a
# feature line rather than to an expectation. `(?J)` is dispatched by module
# `modifiers`' option-run port and its LETTER is module `backrefs`' — the
# [M6.5] split the compliance page records (DECLARING a duplicate name is
# `named-groups`; the letter and RESOLVING a reference to one are `backrefs`)
# — so without it every DUPNAMES cell refused with "inline option 'J'
# (dupnames) requires module 'backrefs'" and the whole file was red for a
# reason that is not about subroutine calls. Design SS9.3 lists S-SR14's cell
# as needing `features named-groups,recursion` and `(?J)`, and did not follow
# the letter to its own module; this line is that follow-through. No m/n/g
# expectation moved.
RCNM = "recursion,named-groups,modifiers,backrefs"
RCK = "recursion,assertions"


# ===========================================================================
# refused.rxt
# ===========================================================================
REFUSED = [
    ("THE `conditionals` REFUSALS THIS MODULE DOES NOT UNLOCK (design SS2.5, "
     "SS13). `(?(` is module `conditionals`'s doorway; `(?(DEFINE)...)`, "
     "`(?(R)` and `(?(1)` all name it, never `recursion` -- REGARDLESS of "
     "whether `recursion` itself is enabled, which the last cell pins.", [
        PERR(r"(?(DEFINE)(?<w>a))(?&w)b", 'pcrec',
             note="the classic library idiom -- still refused today by the "
                  "doorway, not by the name."),
        PERR(r"(a)(?(R)b|c)", 'pcrec',
             note="`(?(R)` -- the whole-pattern-recursion CONDITION, not a "
                  "call. A different construct at the same doorway."),
        PERR(r"(a)(?(1)b|c)", 'pcrec',
             note="`(?(1)` -- the numbered-group CONDITION."),
        PERR(r"(?(DEFINE)(?<w>a))(?&w)b", 'pcrec', features=RC,
             note="THE SAME PATTERN WITH `recursion` ENABLED. D71 decision 4 "
                  "rules `(?(DEFINE)...)` a FUTURE `recursion` row ([DD-14] "
                  "wave F, not started at the time this corpus was written) "
                  "-- design SS2.5's own 'RULED: no DEFINE' conclusion is "
                  "SUPERSEDED by that later ruling. TODAY, enabling "
                  "`recursion` changes nothing: the doorway is still "
                  "`conditionals`'s until wave F lands. This cell is the "
                  "one to re-home (out of refused.rxt, into a DEFINE-idiom "
                  "accept cell) the day it does."),
    ]),
]


# ===========================================================================
# gated.rxt
# ===========================================================================
GATED = [
    ("THE GATE, CLOSED (std1: no --features at all). D26 tier 2's promise: "
     "name the construct and the module that owns it.", [
        PERR(r"(a)(?1)", 'pcrec',
             note="numeric call, closed."),
        PERR(r"(?&n)(?<n>a)", 'pcrec',
             note="by-name call, closed -- the doorway refuses before it "
                  "ever asks whether `named-groups` is available."),
        PERR(r"(a)(?1)", 'pcrec', features="backrefs",
             note="THE WRONG MODULE ENABLED BUYS NOTHING: the gate is "
                  "per-row, not per-pattern. `backrefs` alone does not "
                  "unlock a call."),
    ]),
    # [DD-14 wave B+C, code lane] THE ENABLED-BUT-UNBUILT SECTION IS GONE, AND
    # ITS DISAPPEARANCE IS THIS WAVE'S OWN DELIVERABLE rather than a corpus
    # defect. D65 derives a row's `built` column from the PORT's answer at
    # WANT_RESULT and never runs the emitter, so the wave that WIRES the port
    # is the wave that flips the column — and the numeric cell that pinned
    # "module 'recursion' is enabled but (?1...) is not implemented yet" pins a
    # diagnostic that must stop existing on the same commit. This generator's
    # own guard is what said so, unprompted, on the first run against the new
    # binary: "'(a)(?1)' marked kind=pcrec but build/pcrec COMPILES it -- the
    # refusal this cell pins does not exist".
    #
    # THE POSITIVE HALF REPLACES IT, and it is the stronger check: the same two
    # spellings must now COMPILE with the module enabled. A section that merely
    # deleted the refusals would leave the flip unasserted from either side.
    ("THE GATE, ENABLED AND NOW BUILT (`--features recursion`). [DD-14] wave "
     "B+C wired the ports, so D65's `built` column flips for the `(?` rows and "
     "the enabled-but-unbuilt diagnostic these cells used to pin no longer "
     "exists for them.", [
        B(r"^(a|b)(?1)$", [('m', "ab"), ('n', "ac")], RC, groups=1,
          note="numeric call, enabled and BUILT -- SS2.1's own "
               "call-vs-reference discriminator, used here as the gate's "
               "positive control: a compiler that merely stopped REFUSING "
               "would answer nomatch on \"ab\"."),
        B(r"^(?<n>a|b)(?&n)$", [('m', "ab"), ('n', "ac")], RCN, groups=1,
          note="by-name call, enabled and BUILT -- verified separately "
               "because the by-name doorway is a DIFFERENT registry row from "
               "the numeric one, and it needs `named-groups` for the "
               "DECLARATION (P2)."),
    ]),
    ("P2's CELL (design SS9.3): `(?&n)` should refuse for `named-groups` "
     "FIRST once the call itself parses, not for `recursion`.", [
        PERR(r"(?&n)(?<n>a)", 'pcrec', features=RC,
             note="**NOT OBSERVABLE IN ITS TRUE FORM TODAY.** MEASURED: "
                  "with `recursion` enabled and `named-groups` NOT enabled, "
                  "this pattern refuses today naming 'recursion' (module "
                  "`recursion` has no producer at all yet, so the parser "
                  "never gets far enough to ask about `named-groups`). Once "
                  "[DD-14] wave B+C lands the `(?&` PARSE, the design's "
                  "claim is that this SAME cell must then refuse naming "
                  "'named-groups' instead -- because the declaration "
                  "`(?<n>a)` is what needs that module, and a call can "
                  "reach it lexically before the resolver ever runs. This "
                  "row passes VACUOUSLY today (nonzero exit, wrong reason) "
                  "-- S108's masking shape, named by the design itself. "
                  "THE CODE LANE MUST RE-CHECK THIS CELL'S MESSAGE ONCE "
                  "WAVE B+C LANDS, not just its exit code. "
                  "**DISCHARGED, [DD-14] wave B+C**: MEASURED on the landed "
                  "binary, `--features recursion -- '(?&n)(?<n>a)'` now "
                  "answers `(?&n) names a capture group, which requires "
                  "module 'named-groups'` -- the design's prediction, from "
                  "the port's own gate check, which sits BEFORE the name "
                  "grammar for `br_name_ref`'s reason (without that module "
                  "there is no such thing as a group NAME). The row is no "
                  "longer vacuous."),
    ]),
    ("THE POSITIVE CONTROL: module `recursion` ON, must MATCH (design SS9.2 "
     "-- 'no subroutine call exists today, so this changes nothing' is "
     "trivially true and worth nothing; the control that can go red is this "
     "one). EXPECTED TO FAIL TO COMPILE TODAY (no producer) -- this is an "
     "ordinary `m` block, not a `perr`, so today's harness run reports it as "
     "a pattern-compile failure, never a format error.", [
        B(r"(a|b)(?1)", [('m', "ab")], RC, groups=1,
          note="design SS2.1's own discriminator: a CALL re-runs the "
               "alternation, so this matches \"ab\" where the equivalent "
               "backreference `(a|b)\\1` does not (see spellings.rxt)."),
    ]),
]


# ===========================================================================
# spellings.rxt -- design SS2.1's one-cell discriminator, over every spelling
# ===========================================================================
SPELLINGS = [
    ("THE ONE CELL THAT SEPARATES A CALL FROM A REFERENCE (design SS2.1). "
     "`(a|b)\\1` wants the same TEXT (a reference); `(a|b)(?1)` re-RUNS the "
     "alternation (a call). Both compile, both look like 'group 1 again'.", [
        B(r"(a|b)\1", [('n', "ab"), ('m', "aa")], RCB, groups=1,
          note="the REFERENCE control: nomatch on \"ab\", match on \"aa\" -- "
               "both possible answers, so a reader can tell this from a "
               "compile-status difference."),
        B(r"(a|b)(?1)", [('m', "ab"), ('m', "aa")], RC, groups=1,
          note="the CALL: matches BOTH -- \"ab\" is the cell no reference "
               "can produce."),
    ]),
    ("EVERY SHIPPED SPELLING (design SS2.2), each carrying the SAME "
     "discriminator: match \"ab\", the answer a reference could not give.", [
        B(r"(a|b)(?1)", [('m', "ab")], RC, groups=1, note="`(?N)`"),
        B(r"(a|b)(?-1)", [('m', "ab")], RC, groups=1, note="`(?-N)`"),
        B(r"(?<g>a|b)(?&g)", [('m', "ab")], RCN, groups=1, note="`(?&name)`"),
        B(r"(?<g>a|b)(?P>g)", [('m', "ab")], RCN, groups=1, note="`(?P>name)`"),
        B(r"(a|b)\g<1>", [('m', "ab")], RC, groups=1, note="`\\g<N>`", wave='D'),
        B(r"(a|b)\g'1'", [('m', "ab")], RC, groups=1, note="`\\g'N'`", wave='D'),
        B(r"(?<g>a|b)\g<g>", [('m', "ab")], RCN, groups=1, note="`\\g<name>`", wave='D'),
        B(r"(?<g>a|b)\g'g'", [('m', "ab")], RCN, groups=1, note="`\\g'name'`", wave='D'),
    ]),
    ("THE `\\g` DOORWAY'S OTHER CONSTRUCT IS `backrefs`'S, NOT THIS "
     "MODULE'S -- the split runs exactly along the delimiter (`<`/`'` here "
     "vs bare-digit/`{n}` there). Cross-reference only, not a cell this "
     "file owns: tests/backrefs/spellings.rxt already pins `\\g1`/`\\g{1}` "
     "as `pcrec_refuses=\"recursion\"` -- see that file for the "
     "libpcre2-measured 'THIS matches, THAT compares text' pair.", []),
]

# ===========================================================================
# relative.rxt -- SS2.3: the relative and forward forms, at four distances
# ===========================================================================
RELATIVE = [
    ("BACKWARD `(?-N)`, at distances 1..4", [
        B(r"^(a)(b)(?-1)$", [('m', "abb")], RC, groups=2,
          note="R1. nearest group to the left = group 2."),
        B(r"^(a)(b)(?-2)$", [('m', "aba")], RC, groups=2, note="R2. = group 1."),
        B(r"^(a)(b)(c)(?-3)$", [('m', "abca")], RC, groups=3, note="R3. = group 1."),
        B(r"^(a)(b)(c)(d)(?-4)$", [('m', "abcda")], RC, groups=4,
          note="R4. = group 1."),
    ]),
    ("FORWARD `(?+N)`, at distances 1..4 -- THE SHAPE THAT MAKES A CALL "
     "UNLIKE A REFERENCE (design SS2.3): the target's pattern runs BEFORE "
     "the target group does.", [
        B(r"^(?+1)(a)$", [('m', "aa")], RC, groups=1,
          note="F1. group 1's own pattern runs via the call first."),
        B(r"^(?+2)(a)(b)$", [('m', "bab")], RC, groups=2,
          note="F2. counts forward past one group to reach the second."),
        B(r"^(?+3)(a)(b)(c)$", [('m', "cabc")], RC, groups=3, note="F3."),
        B(r"^(?+4)(a)(b)(c)(d)$", [('m', "dabcd")], RC, groups=4, note="F4."),
    ]),
    ("LEADING ZEROS ON A RELATIVE VALUE (design SS2.4a) -- accepted, same "
     "target as without the zero.", [
        B(r"^(a)(b)\g<-01>$", [('m', "abb")], RC, groups=2, wave='D'),
        B(r"^(a)(b)(?-01)$", [('m', "abb")], RC, groups=2),
        B(r"^(a)(b)\g<-02>$", [('m', "aba")], RC, groups=2, wave='D'),
    ]),
    ("`\\g<+-N>` OBEYS THE SAME RELATIVE RULE the `(?` doorway does.", [
        B(r"^\g<+1>(a)$", [('m', "aa")], RC, groups=1, wave='D'),
        B(r"^(a)(b)\g<-1>$", [('m', "abb")], RC, groups=2, wave='D'),
    ]),
    ("A RELATIVE VALUE OF ZERO IS ALWAYS ERROR 126 (design SS2.4a) -- in "
     "every spelling, leading zero or not.", [
        PERR(r"(a)(?-00)", 'pcre2', features=RC, note="`(?-00)`"),
        PERR(r"(a)(?+00)", 'pcre2', features=RC, note="`(?+00)`"),
        PERR(r"(a)(?-0)", 'pcre2', features=RC, note="`(?-0)`"),
        PERR(r"(a)\g<-0>", 'pcre2', features=RC, note="`\\g<-0>`"),
    ]),
]

# ===========================================================================
# whole.rxt -- SS2.4: the whole-pattern call and the anchors it re-runs
# ===========================================================================
WHOLE = [
    ("ONE CELL SETTLES WHAT 'THE WHOLE PATTERN' MEANS (design SS2.4): "
     "`(?1)` calls GROUP 1, whose `^`/`$` live OUTSIDE it; `(?R)`/`(?0)`/"
     "`\\g<0>`/`\\g'0'` re-run the WHOLE PATTERN, anchors included, so the "
     "inner `^` fails at offset 1.", [
        B(r"^(a(?1)?b)$", [('m', "aabb")], RC, groups=1,
          note="the CONTRAST: a call to group 1 sees no anchor."),
        B(r"^(a(?R)?b)$", [('n', "aabb")], RC, groups=1,
          note="`(?R)`: the anchors travel with it."),
        B(r"^(a(?0)?b)$", [('n', "aabb")], RC, groups=1, note="`(?0)` is `(?R)`."),
        B(r"^(a\g<0>?b)$", [('n', "aabb")], RC, groups=1,
          note="`\\g<0>` -- a spelling the charter's list did not have "
               "(design SS2.4) -- is `(?R)` too.", wave='D'),
        B(r"^(a\g'0'?b)$", [('n', "aabb")], RC, groups=1, note="and so is `\\g'0'`.", wave='D'),
        B(r"(a(?R)?b)", [('m', "aabb")], RC, groups=1,
          note="UNANCHORED: with the anchors gone, `(?R)` reaches depth 2."),
    ]),
]

# ===========================================================================
# captures.rxt -- SS3.1: written-by-the-callee, restored-by-the-return
# ===========================================================================
CAPTURES = [
    ("AFTER RETURN, AT DEPTH 1: the callee's own write does not survive "
     "the return (design SS3.1, H-RESTORE not H-NEVER).", [
        B(r"^((a)(?1)?(b))$", [('m', "ab")], RC, groups=3,
          note="no recursion actually taken here (control: depth 0)."),
    ]),
    ("AT DEPTH 3, PER LEVEL: the OUTERMOST level's values are the answer "
     "(design SS3.1, C3).", [
        B(r"^((a)(?1)?(b))$", [('m', "aabb")], RC, groups=3,
          note="depth 2 -- group 2/3 read the OUTER level's a/b, not the "
               "inner call's."),
        B(r"^((a)(?1)?(b))$", [('m', "aaabbb")], RC, groups=3,
          note="depth 3."),
    ]),
    ("AFTER A FAILED CALL, NOTHING SURVIVES (design SS3.1, C4): the first "
     "branch's call runs and dies; the second branch's call runs and "
     "succeeds; neither leaves a trace in the OTHER branch's groups.", [
        B(r"^(?:((a))(?1)x|(?1)y)$", [('m', "ay")], RC, groups=2,
          note="both g1 and g2 read UNSET -- the first alternative's call "
               "wrote them and then the whole alternative failed."),
    ]),
    ("THE INHERITANCE CELL (design SS3.1, C5): a call is NOT a fresh "
     "capture environment -- `\\1` inside the called body still sees the "
     "CALLER's group.", [
        B(r"^(a)(b\1)(?2)$", [('m', "ababa")], RCB, groups=2,
          note="group 2's body is `b\\1`; the call re-ran it and `\\1` was "
               "still \"a\"."),
        B(r"^(a)(b\1)(?2)$", [('n', "abab")], RCB, groups=2,
          note="the control: an UNSET-and-empty `\\1` would have matched "
               "this; it does not, so the call did inherit."),
    ]),
    ("EACH LEVEL'S REFERENCE READS THAT LEVEL'S OWN CAPTURE (design SS3.1, "
     "C5's second cell).", [
        B(r"^((a|b)(?1)?\2)$", [('m', "abba")], RCB, groups=2,
          note="each level's `\\2` refers to THAT level's group 2."),
        B(r"^((a|b)(?1)?\2)$", [('n', "abab")], RCB, groups=2,
          note="the control: the cross-level reading this would need does "
               "not exist."),
    ]),
]

# ===========================================================================
# atomicity.rxt -- SS3.2: BACKTRACKABLE on 10.46, isolated via the {0} idiom
# ===========================================================================
ATOMICITY = [
    ("THE ISOLATED DISCRIMINATOR (design SS3.2): a body reachable ONLY by "
     "the call, so the lexical group cannot be what retries.", [
        B(r"^(?:(?<g>a|ab)){0}(?&g)c$", [('m', "abc")], RCN, groups=1,
          note="BACKTRACKABLE: atomic would answer nomatch here."),
        B(r"^(?:(?<g>a+)){0}(?&g)ab$", [('m', "aaab")], RCN, groups=1,
          note="a QUANTIFIER, not an alternation, as the callee's choice "
               "point."),
        B(r"^(?:(?<g>a{1,3})){0}(?&g)aa$", [('m', "aaa")], RCN, groups=1,
          note="a bounded repeat."),
    ]),
    ("IT RETRIES ACROSS A RETURN, AT DEPTH (design SS3.2, T3): the retreat "
     "must re-enter the INNER call after the outer one returned.", [
        B(r"^(?:(?<g>a(?&g)?b|x|xy)){0}(?&g)$", [('m', "axyb")], RCN, groups=1),
    ]),
    ("FOUR ATOMIC CONTROLS, all nomatch (design SS3.2, T4) -- what makes "
     "the rows above evidence rather than a coincidence.", [
        B(r"^(?:(?<g>(?>a|ab))){0}(?&g)c$", [('n', "abc")],
          RCN + ",atomic-groups", groups=1, note="an ATOMIC callee body."),
        B(r"^(?:(?<g>a|ab)){0}(?>(?&g))c$", [('n', "abc")],
          RCN + ",atomic-groups", groups=1,
          note="an ATOMIC WRAPPER on the call site."),
        B(r"^(?:(?<g>a|ab)){0}(?&g)++c$", [('n', "abc")],
          RCN + ",atomic-groups", groups=1,
          note="a POSSESSIVE quantifier on the call."),
        B(r"^(?:(?<g>(?>a|ab))){0}(?>(?&g))c$", [('n', "abc")],
          RCN + ",atomic-groups", groups=1,
          note="an atomic wrapper around a GIVING-BACK callee."),
    ]),
]

# ===========================================================================
# leftrec.rxt -- SS3.3: no compile-time refusal; the depth capacity gives up
# ===========================================================================
LEFTREC = [
    ("THE GIVE-UP CELLS: direct, indirect and nullable-prefix left "
     "recursion, each with no non-recursive branch reachable on the given "
     "subject (design SS3.3/SS5.6/SS9.3 S-SR8). `gu frames` per D71.1 -- "
     "the default artifact's give-up for a deep/runaway call is "
     "PCREC_ERR_FRAMES; PCREC_ERR_RECURSE only exists under the diagnostic "
     "generation axis, unbuilt here.", [
        GU(r"^((?1)a)$", "a", "frames", RC,
           note="DIRECT: group 1's body is `(?1)a` with no alternative -- "
                "the call is unconditional, so no subject terminates it. "
                "SUBJECT CHOICE: the shortest legal one, \"a\" -- the "
                "runaway is reachable at ANY length, so there is nothing "
                "to gain from a longer one."),
        GU(r"^(?:(?<p>(?&q)a)){0}(?:(?<q>(?&p)b)){0}(?&p)$", "ab", "frames", RCN,
           note="INDIRECT: p calls q calls p, a two-node cycle with no "
                "non-recursive branch on either side. SUBJECT CHOICE: "
                "\"ab\" -- design SS3.3's own L2 measurement (`out/"
                "leftrec.txt`) uses this exact subject for the DEFINE form "
                "of the same cycle, cross-checked here via the {0} idiom."),
        GU(r"^(a?(?1)b)$", "ab", "frames", RC,
           parked="tests/known_fail/dd14_bc_open.rxt, cell 1. pcrec answers "
                  "NOMATCH here, not a give-up, and BOTH are refusals of the "
                  "same subject. Design SS4.4b's minw fixpoint gives this "
                  "callee minw = INFINITY (its language IS empty: X = a? X b "
                  "has no base case), and SS12 P-12 RULES that the MRL prune "
                  "then reads it as 'no position can match' -- which is what "
                  "the `a?` quantifier's own bound does, in constant time, "
                  "where 10.46 spends its rc -52 finding out. The two "
                  "SIBLING cells in this section still give up, because they "
                  "carry no quantifier for a bound to hang on, so the class "
                  "answers two ways depending on a shape that is not about "
                  "recursion. WHICH ANSWER THIS CELL SHOULD PIN IS A RULING "
                  "NOBODY HAS MADE.",
           note="NULLABLE PREFIX: an optional literal precedes the call, "
                "but the call itself is still unconditional -- "
                "design SS3.3/L3's own point is that 'is the call the "
                "FIRST item' misses this shape. SUBJECT CHOICE: \"ab\" -- "
                "design SS3.3's own L3 measurement uses this exact "
                "subject for the identical pattern."),
    ]),
    ("THE CELL THAT MUST MATCH (design SS3.3, L5b): 199 nested "
     "recursions, every one entered at offset 0 -- refusing this would be "
     "a MISCOMPILE, not a conservative approximation. Whether pcrec's "
     "DEFAULT frame capacity reaches depth 200 is a code-lane capacity "
     "question, not this cell's.", [
        B(r"^(a|(?1)a)$", [('m', "a" * 200)], RC, groups=1),
    ]),
    ("THE CONTRAST: what is NOT refused (design SS3.3, L4) -- ordinary "
     "right recursion with a base case is not a give-up at all.", [
        B(r"^(a(?1)?b)$", [('m', "aabb")], RC, groups=1),
    ]),
]

# ===========================================================================
# dupnames.rxt -- SS3.4(c): a CALL and a REFERENCE resolve DIFFERENTLY
# ===========================================================================
DUPNAMES = [
    ("THE SPLIT (design SS3.4c): a call by name to a duplicated name runs "
     "the FIRST DECLARATION's pattern, STATICALLY, whether or not it is "
     "set; a backreference (tests/backrefs/dupnames.rxt) reads the first "
     "SET member, DYNAMICALLY. Same subjects, opposite verdicts.", [
        B(r"^(?J)(?:(?<a>x)|q)(?<a>y)(?&a)$", [('m', "qyx"), ('n', "qyy")],
          RCNM, groups=2,
          note="a CALL: matches \"qyx\" (first declaration is `x`), not "
               "\"qyy\"."),
    ]),
    ("A CALL DOES NOT RETRY INTO THE LATER MEMBERS OF THE NAME RUN.", [
        B(r"^(?J)(?<a>x)(q)(?<a>y)(?&a)z$",
          [('m', "xqyxz"), ('n', "xqyyz")], RCNM, groups=3,
          note="the call always re-runs the FIRST `a` (\"x\"): "
               "\"xqyxz\" matches, \"xqyyz\" does not."),
    ]),
    ("THE UNSET-FIRST-DECLARATION DISCRIMINATOR: the first declaration's "
     "pattern runs even when that declaration never PARTICIPATED -- a "
     "call resolves at PARSE time to one number, not at match time to "
     "'the first one that is set'.", [
        B(r"^(?J)(?<a>x?)(?<a>y)(?&a)$", [('m', "y"), ('n', "yy"), ('m', "yx")],
          RCNM, groups=2,
          note="on \"yx\": g1=(0,0) (x? matched empty, unset-vs-empty does "
               "not matter to a CALL), g2 matches \"y\", the trailing call "
               "re-runs `x?` and consumes the \"x\". \"yy\" fails because "
               "the FIRST declaration's `x?` cannot consume a second 'y'."),
    ]),
    ("THE RULE IS UNIFORM ACROSS ALL FOUR BY-NAME SPELLINGS (design "
     "SS3.4c) -- `(?&a)`, `(?P>a)`, `\\g<a>` and `\\g'a'` all resolve to "
     "the SAME first declaration.", [
        B(r"^(?J)(?:(?<a>x)|q)(?<a>y)(?P>a)$", [('m', "qyx"), ('n', "qyy")],
          RCNM, groups=2),
        B(r"^(?J)(?:(?<a>x)|q)(?<a>y)\g<a>$", [('m', "qyx"), ('n', "qyy")],
          RCNM, groups=2, wave='D'),
        B(r"^(?J)(?:(?<a>x)|q)(?<a>y)\g'a'$", [('m', "qyx"), ('n', "qyy")],
          RCNM, groups=2, wave='D'),
    ]),
]

# ===========================================================================
# kreset.rxt -- SS3.4(b): \K is NOT restored by a return
# ===========================================================================
KRESET = [
    ("THREE CELLS (design SS3.4b, C7): `\\K` inside a called body MOVES "
     "the reported match start and SURVIVES the return -- it is a PATH "
     "fact, not capture state. pcrec spells `\\K` as a write to "
     "RX_SLOT_WHOLE_START, the same slot as group 0's start, which is "
     "exactly why W (SS5.3a) must exclude slots 0 and 1.", [
        B(r"^(a\Kb)(?1)$", [('m', "abab")], RCK, groups=1,
          note="the last `\\K` on the successful path wins -- the OUTER "
               "level's, firing after the inner level's already has."),
        B(r"^(?:(?<g>a\Kb)){0}(?&g)$", [('m', "ab")], RCK + ",named-groups", groups=1,
          note="the {0}-callee form of the same fact."),
        B(r"^(a(?1)?\Kb)$", [('m', "aabb")], RCK, groups=1,
          note="`\\K` inside a body that ALSO recurses."),
    ]),
]

# ===========================================================================
# zerodef.rxt -- SS4.4c: the slot layout must count each EMITTED region,
# including a callee parked under X{0} -- {1} is each family's non-{0} twin
# ===========================================================================
ZERODEF = [
    ("PLAIN: a callee with only CAPTURE slots -- the CONTROL. `{0}` does "
     "not prune anything a plain callee needs, so this row is not "
     "load-bearing on its own (design SS4.4c/SS9.3 S-SR19).", [
        B(r"^(?:(?<g>a|ab)){0}(?&g)c$", [('m', "abc")], RCN, groups=1,
          note="the classic pre-DEFINE idiom, parked under `{0}`."),
        B(r"^(?:(?<g>a|ab)){1}(?&g)c$", [('m', "aabc"), ('n', "abc")], RCN,
          groups=1,
          note="the NON-{0} CONTROL: the SAME callee, emitted lexically "
               "once (`{1}`) as well as called -- \"abc\" now fails "
               "because the LEXICAL copy must also consume."),
    ]),
    ("RECURSIVE: a callee whose own body calls itself, parked under `{0}` "
     "(design SS4.4c, axis Z0).", [
        B(r"^(x)?(?:(?<h>a(?2)?b)){0}(?2)$", [('m', "aabb")], RCN, groups=2),
        B(r"^(x)?(?:(?<h>a(?2)?b)){1}(?2)$", [('m', "aabbaabb")], RCN,
          groups=2,
          note="the NON-{0} CONTROL: the lexical copy runs once (matching "
               "the first \"aabb\"), then the call re-runs it."),
    ]),
    ("ATOMIC -- LOAD-BEARING (design SS4.4c/SS9.3 S-SR19): an atomic "
     "callee allocates a CUT_MARK slot family that a lexical-only count "
     "would miss entirely once the callee sits under `{0}`.", [
        B(r"^(?:((?>a|ab))){0}(?1)z$", [('m', "az"), ('n', "abz")],
          RCN.replace("named-groups", "") + ",atomic-groups" if False
          else RC + ",atomic-groups", groups=1),
        B(r"^(?:((?>a|ab))){1}(?1)z$", [('m', "aaz"), ('n', "aabz")],
          RC + ",atomic-groups", groups=1,
          note="the NON-{0} CONTROL."),
    ]),
    ("RUNG-BEARING -- LOAD-BEARING (design SS4.4c/SS9.3 S-SR19): a "
     "callee whose OWN quantifier needs rung state (an empty-iteration "
     "guard family here), parked under `{0}`.", [
        B(r"^(?:(a?)){0}(?1)*b$", [('m', "b")], RC, groups=1),
        B(r"^(?:(a?)){1}(?1)*b$", [('m', "ab"), ('m', "aaab")], RC, groups=1,
          note="the NON-{0} CONTROL."),
    ]),
]

# ===========================================================================
# leadingzero.rxt -- SS2.4a: the whole digit run is decimal; 0 is the root
# ===========================================================================
LEADINGZERO = [
    ("THE PAIR THAT IS THE SPECIFICATION (design SS2.4a), on the ANCHORED "
     "discriminator -- unanchored, both answers are (0,4) and this file "
     "would pin nothing; SS2.4a says so and this corpus uses the anchored "
     "form throughout.", [
        B(r"^(a(?1)?b)$", [('m', "aabb")], RC, groups=1,
          note="the CONTRAST: `(?1)`, no leading zero, targets group 1."),
        B(r"^(a(?01)?b)$", [('m', "aabb")], RC, groups=1,
          note="`(?01)` -- ONE leading zero -- STILL targets group 1: the "
               "whole digit run is read as decimal, not the first "
               "character after `(?`."),
        B(r"^(a(?001)?b)$", [('m', "aabb")], RC, groups=1, note="two leading zeros."),
        B(r"^(a(?0001)?b)$", [('m', "aabb")], RC, groups=1, note="three."),
        B(r"^(a(?R)?b)$", [('n', "aabb")], RC, groups=1,
          note="the CONTRAST: `(?R)` targets the root."),
        B(r"^(a(?00)?b)$", [('n', "aabb")], RC, groups=1,
          note="`(?00)` -- the digit run is `00`, value 0 -- targets the "
               "root, exactly like `(?R)`. The naive one-character-after-"
               "`(?` doorway reading would compile this as group 1 (design "
               "SS2.4a's own miscompile warning)."),
    ]),
    ("THE `\\g` DOORWAY TAKES THE SAME RULE.", [
        B(r"^(a\g<1>?b)$", [('m', "aabb")], RC, groups=1, wave='D'),
        B(r"^(a\g<01>?b)$", [('m', "aabb")], RC, groups=1, wave='D'),
        B(r"^(a\g'01'?b)$", [('m', "aabb")], RC, groups=1, wave='D'),
        B(r"^(a\g<0>?b)$", [('n', "aabb")], RC, groups=1, wave='D'),
        B(r"^(a\g<00>?b)$", [('n', "aabb")], RC, groups=1, wave='D'),
        B(r"^(a\g'00'?b)$", [('n', "aabb")], RC, groups=1, wave='D'),
    ]),
    ("THE RELATIVE FORMS TAKE A LEADING ZERO TOO (design SS2.4a) -- "
     "already exercised in relative.rxt; cross-referenced here rather "
     "than duplicated, EXCEPT the one cell that pairs relative leading-"
     "zero against the SAME anchored discriminator this file is about.", [
        B(r"^(a)(b)(?-01)$", [('m', "abb")], RC, groups=2),
    ]),
]

# ===========================================================================
# mrl.rxt -- SS4.4b: pcrec_minw's fixpoint for a recursive callee
# ===========================================================================
MRL = [
    ("THE SPECIFICATION IS THE PAIR (design SS4.4b): `minw` = Kleene "
     "iteration from infinity DOWNWARD over the SCC-condensed call graph. "
     "This first cell is the WITNESS that refuted the withdrawn gloss "
     "('the least fixpoint over the non-recursive branches') -- group `g`'s "
     "ONLY branch is `(?&h)b`, so there is no non-recursive branch to "
     "minimise over at all, and the withdrawn gloss gives infinity where "
     "the true fixpoint (minw(h)=1 via h's `x` branch, minw(g)=2) is "
     "right and the pattern MATCHES.", [
        B(r"^(?:(?<g>(?&h)b)){0}(?:(?<h>x|(?&g))){0}(?&g)$",
          [('m', "xb"), ('m', "xbb"), ('m', "xbbb"), ('m', "xbbbb")],
          RCN, groups=0,
          note="mutual recursion, g calls h calls g -- MUST MATCH at "
               "every length in this sweep."),
    ]),
    ("THE CONTROL CELL (design SS4.4b): a DIFFERENT recursive callee "
     "where infinity IS the correct fixpoint -- the pair together are the "
     "specification, not either alone.", [
        B(r"^(?:(?<g>a(?&g)b)){0}(?&g)$",
          [('n', ""), ('n', "ab"), ('n', "aabb"), ('n', "aaabbb")],
          RCN, groups=0,
          note="`g`'s only branch always calls itself again -- no base "
               "case exists, so nothing matches at ANY length, and a fix "
               "that 'never answers infinity' would get this wrong."),
    ]),
]

# ===========================================================================
# slotfamilies.rxt -- SS5.3b: the two MEASURED slot families
# ===========================================================================
SLOTFAMILIES = [
    ("AXIS P -- SLOT_GROUP<n>_PENDING (design SS5.3b): a backreference "
     "MARKS the called group, so publish-at-close needs a pending slot; "
     "without it the inner activation's open position clobbers the "
     "outer's and the outer LOSES ITS MATCH.", [
        B(r"^(a(?1)?b)\1$", [('m', "aabbaabb"), ('m', "aaabbbaaabbb")],
          RCB, groups=1,
          note="MEASURED 11/2 disagree without the pending slot "
               "(design SS5.3b); WITH it, 13/0."),
    ]),
    ("AXIS C -- SLOT_CUT_MARK<n> (design SS5.3b): an atomic group LIVE AT "
     "TWO DEPTHS needs one mark instance per emitted copy; without it the "
     "inner activation's mark clobbers the outer's `RX_CUT` into a no-op "
     "and the atomic group stops being atomic -- a FALSE MATCH, and the "
     "false-match set is EXACTLY the non-atomic control's language.", [
        B(r"^((?>a(?1)?))a$",
          [('n', "aa"), ('n', "aaa"), ('n', "aaaa"), ('n', "aaaaa"),
           ('n', "aaaaaa"), ('n', "aaaaaaa"), ('n', "aaaaaaaa")],
          RCA, groups=1,
          note="10.46 matches NOTHING at any of these lengths -- MEASURED "
               "4/6 disagree without the mark-per-activation family "
               "(design SS5.3b)."),
        B(r"^((?:a(?1)?))a$", [('m', "aa"), ('m', "aaa")], RC, groups=1,
          note="THE NON-ATOMIC CONTROL -- the exact language the false "
               "matches above would reproduce on a broken compiler."),
    ]),
]

# ===========================================================================
# quantified.rxt -- SS2.6: a call is an ordinary repeatable item
# ===========================================================================
QUANTIFIED = [
    ("A CALL IS A REPEATABLE ITEM, twelve spellings (design SS2.6).", [
        B(r"^(a)(?1){2}b$", [('m', "aaab")], RC, groups=1, note="`(?N){n}`"),
        B(r"^(a)(?1)+b$", [('m', "aaab")], RC, groups=1, note="`(?N)+`"),
        B(r"^(a)(?1)*b$", [('m', "aaab"), ('m', "b")], RC, groups=1,
          note="`(?N)*` -- with its zero-repetition control."),
        B(r"^(a)(?1){1,3}b$", [('m', "aab")], RC, groups=1, note="`(?N){n,m}`"),
        B(r"^(a)(?-1){2}b$", [('m', "aaab")], RC, groups=1, note="`(?-N){n}`"),
        B(r"^(?<g>a)(?&g){2}b$", [('m', "aaab")], RCN, groups=1,
          note="`(?&name){n}`"),
        B(r"^(?<g>a)(?P>g){2}b$", [('m', "aaab")], RCN, groups=1,
          note="`(?P>name){n}`"),
        B(r"^(a)\g<1>{2}b$", [('m', "aaab")], RC, groups=1, note="`\\g<N>{n}`", wave='D'),
        B(r"^(a)\g'1'{2}b$", [('m', "aaab")], RC, groups=1, note="`\\g'N'{n}`", wave='D'),
        B(r"^(?<g>a)\g<g>{2}b$", [('m', "aaab")], RCN, groups=1,
          note="`\\g<name>{n}`", wave='D'),
        B(r"^(?<g>a)\g'g'{2}b$", [('m', "aaab")], RCN, groups=1,
          note="`\\g'name'{n}`", wave='D'),
        B(r"(a(?R)*b)", [('m', "aabb")], RC, groups=1, note="`(?R)*`"),
    ]),
    ("THE EMPTY-BODY GUARD (design SS2.6): a NULLABLE or EMPTY callee "
     "under `*` TERMINATES -- `vm_nullable` needs an A_CALL arm.", [
        B(r"^(?:(?<g>a?)){0}(?&g)*$", [('m', "aaa")], RCN, groups=0,
          note="a nullable callee under `*` still terminates."),
        B(r"^(?:(?<g>)){0}(?&g)*$", [('m', "")], RCN, groups=0,
          note="an EMPTY callee under `*` terminates too."),
        B(r"^(a?)(?1)*$", [('m', "aaa")], RC, groups=1,
          note="the numbered-group spelling of the same fact."),
    ]),
    ("`(?R)` UNDER A QUANTIFIER, UNCONDITIONAL -- a give-up, not a "
     "termination (design SS2.6, L6): no non-recursive branch exists, so "
     "the empty-iteration guard alone cannot save it.", [
        GU(r"^(?R)*$", "", "frames", RC,
           note="`(?R)*` at the top level re-runs the WHOLE PATTERN "
                "(anchors included) on every iteration, with no base "
                "case -- design SS2.6's own L6 row, which uses the empty "
                "subject for this exact pattern. SUBJECT CHOICE: \"\" -- "
                "the runaway needs no input at all, since `(?R)` re-enters "
                "at the same position on every iteration regardless of "
                "what is left to consume."),
    ]),
]

# ===========================================================================
# inlookaround.rxt -- SS3.4(d)/(e) and SS3.5's mirror image
# ===========================================================================
# [DD-14 wave B+C, code lane] THE TWO CELLS BELOW ARE PARKED, AND THE REASON
# IS A TIMING GAP THE DESIGN DOES NOT ADDRESS rather than a wrong answer.
LBWIDTH = (
    "tests/known_fail/dd14_bc_open.rxt, %s. pcrec REFUSES this "
    "(\"variable-length lookbehind is not implemented ... this one is "
    "unbounded\") where 10.46 accepts it -- a tier-2 OVER-rejection, never a "
    "miscompile. `pcrec_maxw`'s A_CALL arm answers PCREC_W_UNBOUNDED, which "
    "design SS3.4(d) says is EXACT for a recursive callee and a sound "
    "over-estimate for any other; tightening it for an ACYCLIC callee needs "
    "the call graph, and the LOOKBEHIND WIDTH RULE (`la_widths`, "
    "src/parse/mod_lookaround.c) runs INSIDE THE PARSE HOOK -- where it must, "
    "to raise its refusal with a pattern offset -- while the graph does not "
    "exist until every call is resolved at end of parse and every rewriting "
    "pass has run. So no A_CALL arm of `pcrec_maxw` can make this compile: "
    "the width is decided before the callee is known. THE FIX IS A DEFERRED "
    "WIDTH RE-CHECK (the parse hook records the lookbehind instead of "
    "refusing when its body carries a call; a post-graph pass recomputes and "
    "refuses), which is a change to a landed module's core and a diagnostic "
    "offset this wave did not take on.")

INLOOKAROUND = [
    ("A CALL INSIDE A LOOKBEHIND NEEDS A WIDTH (design SS3.4d) -- pcrec's "
     "own lookbehind subset is fixed-PER-BRANCH, so this composes without "
     "new machinery: a recursive callee has no bounded width and refuses.", [
        B(r"^(?:(?<g>ab)){0}ab(?<=(?&g))$", [('m', "ab")], RCLA + ",named-groups", groups=0,
          parked=LBWIDTH % "cell 2", note="fixed width 2."),
        B(r"^(?:(?<g>a|ab)){0}ab(?<=(?&g))$", [('m', "ab")], RCLA + ",named-groups", groups=0,
          parked=LBWIDTH % "cell 3",
          note="widths 1 and 2, the fixed-PER-BRANCH form pcrec ships "
               "(lookaround_design.md SS2.5)."),
        PERR(r"^(?:(?<g>a(?&g)?b)){0}aabb(?<=(?&g))$", 'pcre2',
             features=RCLA + ",named-groups",
             note="a RECURSIVE callee inside a lookbehind has no bounded "
                  "width -- libpcre2 itself refuses this (err 125), which "
                  "is the same answer pcrec's fixed-per-branch rule must "
                  "give once `pcrec_maxw`'s A_CALL arm exists (design "
                  "SS3.4d: infinity for any callee in a cycle)."),
    ]),
    ("A CALL INSIDE A LOOKAHEAD OR AN ATOMIC GROUP IS ORDINARY (design "
     "SS3.4e) -- nothing in this module is special-cased for them.", [
        B(r"^(?:(?<g>ab)){0}(?=(?&g))ab$", [('m', "ab")], RCL + ",named-groups", groups=0,
          note="positive lookahead."),
        B(r"^(?:(?<g>ab)){0}(?!(?&g))ac$", [('m', "ac")], RCL + ",named-groups", groups=0,
          note="negative lookahead."),
        B(r"^(?:(?<g>ab)){0}(?>(?&g))$", [('m', "ab")], RCA + ",named-groups", groups=0,
          note="atomic group."),
    ]),
    ("SS3.5's MIRROR IMAGE: a call TO A GROUP WHOSE LEXICAL HOME lives "
     "inside a lookaround or an atomic group -- the sharpest finding of "
     "the design. The callee runs as its OWN region, forward, consuming, "
     "cut-free -- whatever its lexical wrapper does -- and each wrapper "
     "shape needs its own control that isolates the wrapper.", [
        B(r"^ab(?<=(ab))(?1)$", [('m', "abab"), ('n', "ab")], RCL, groups=1,
          note="W1: the callee leaves through ITS OWN exit, not the "
               "lookbehind's end-check-cut-and-restore. \"ab\" alone is "
               "the CONTROL -- the call must consume."),
        B(r"^(?!(z|zy))x(?1)c$", [('m', "xzyc"), ('m', "xzc")], RCL, groups=1,
          note="W2: the call RETRIES into \"zy\" -- a region whose "
               "lexical home is CUT on the assertion's own success. "
               "\"xzc\" is the control (the first alternative suffices)."),
        B(r"^(?>(a|ab))z(?1)c$", [('m', "azabc")], RCA, groups=1,
          note="W3: the call GIVES BACK \"a\" and takes \"ab\", though its "
               "lexical home is ATOMIC."),
        B(r"^(?>(a|ab))z(?:a|ab)c$", [('m', "azabc")], RCA.replace(
            "recursion,", ""), groups=1,
          note="W3's CONTROL: the same language written INLINE, atomic "
               "wrapper kept, no call at all -- same answer, so the call "
               "did not change what the atomic wrapper permits, only WHO "
               "gets to retry into it."),
        B(r"^(?=(a|ab))..(?1)$", [('m', "abab")], RCL, groups=1,
          note="W5: positive lookahead."),
        B(r"^((?=(b))|a)+(?2)$", [('m', "ab")], RCL, groups=2,
          note="W5: a lookahead nested inside a quantified group."),
    ]),
]

# ===========================================================================
# nocaptures.rxt -- SS4.3: a call target joins the marked set
# ===========================================================================
NOCAPTURES_NOTE = """
#
# THIS FILE DOES NOT (AND CANNOT TODAY) ASSERT THE --no-captures AXIS ITSELF.
# MEASURED: `grep -rn "no-captures\\|nocaps" tests/harness/run.sh
# docs/testing.md tests/*/CLAUDE.md` finds no `.rxt` directive for it anywhere
# in the tree -- tests/backrefs/CLAUDE.md says so explicitly ("The `.rxt`
# format has no `--no-captures` directive"), and every module that needs this
# axis today (backrefs' run_backref_diff.sh SS4, atomic-groups' three-axis
# gate) carries a SEPARATE shell/C instrument that compiles with
# `--no-captures` and inspects the artifact directly (RX_NCAPS, slot
# allocation) -- never an `.rxt` block. THIS IS A REPORTED GAP, not an
# invented directive (the lane brief's own instruction: "if none exists,
# write the cells with the flag you would need and report the gap instead of
# inventing harness syntax").
#
# So this file pins the ORDINARY (captures-on) behaviour of the two marked-
# set cells design SS4.3/SS9.3 (S-SR10, S-SR11a) name -- a call target must
# join `pcrec_bref_mark`'s union or `--no-captures` deletes its slots. A
# future `run_recursion_diff.sh`-shaped instrument (tests/backrefs/
# run_backref_diff.sh SS4 is the precedent to copy) is what the code lane
# owes to actually compile these under `--no-captures` and assert RX_NCAPS /
# slot survival -- flagged in this lane's report as a gap for that lane,
# not invented here.
"""
NOCAPTURES = [
    ("THE ONE-HOP CELL (design SS4.3, S-SR10): `(a)(?1)` -- group 1 is "
     "both the lexical group AND the call's target, so it is trivially "
     "marked already under the ordinary reference-marking rule. Recorded "
     "here as the ORDINARY-axis pin the --no-captures instrument must "
     "reproduce under that flag once it exists.", [
        B(r"^(a)(?1)?$", [('m', "aa")], RC, groups=1),
    ]),
    ("THE TWO-HOP CELL (design SS4.3, S-SR11a): a call target THREE "
     "groups away from the call site -- the one-line marking arm's own "
     "cell, not a transitivity claim (SS4.3 withdrew that).", [
        B(r"^(a(?3)?)(b)((c)?)$", [('m', "acbc")], RC, groups=4,
          note="`(?3)` inside group 1 is a FORWARD call, two groups past "
               "group 2, to group 3 (itself containing group 4). Under "
               "--no-captures the FUTURE instrument must show group 3's "
               "(and group 4's) slots survive because of this call."),
    ]),
]

# ===========================================================================
HDR_EXTRA_REFUSED = """
#
# refused.rxt pins refusals that OUTLIVE this module -- constructs at the
# `(?(` doorway that stay `conditionals`'s no matter what `recursion` does.
# gated.rxt pins the two D65 diagnostics this module's OWN doorways give
# (closed vs enabled-not-implemented), P2's cell, and the positive control.
"""


def main():
    tot = {'cells': 0, 'blocks': 0, 'perr': 0, 'gu': 0}
    files = [
        ("refused.rxt",
         "the `conditionals` refusals `(?(DEFINE)`/`(?(R)`/`(?(1)` this "
         "module does not unlock (SS2.5, SS13)",
         REFUSED),
        ("gated.rxt",
         "the module gate: closed vs enabled-not-implemented (D65), P2's "
         "masking cell, and the positive control (SS9.2, SS10.2)",
         GATED),
        ("spellings.rxt",
         "SS2.1's one-cell call-vs-reference discriminator, over every "
         "shipped spelling (SS2.2)",
         SPELLINGS),
        ("relative.rxt",
         "SS2.3: `(?±N)`/`\\g<±N>` at four distances, forward and "
         "backward, the leading-zero and relative-zero cells",
         RELATIVE),
        ("whole.rxt",
         "SS2.4: `(?R)`/`(?0)`/`\\g<0>`/`\\g'0'` and the anchor cells -- "
         "'the whole pattern' includes `^`/`$`",
         WHOLE),
        ("captures.rxt",
         "SS3.1: the callee WRITES and the RETURN restores -- after "
         "return, at depth 3, after a failed call, and inheritance",
         CAPTURES),
        ("atomicity.rxt",
         "SS3.2: BACKTRACKABLE on 10.46, isolated via the {0} idiom, plus "
         "the four atomic controls",
         ATOMICITY),
        ("leftrec.rxt",
         "SS3.3: no compile-time refusal; PCREC_ERR_FRAMES gives up on a "
         "runaway, and the 199-deep same-position cell MUST match",
         LEFTREC),
        ("dupnames.rxt",
         "SS3.4(c): a CALL resolves a duplicated name STATICALLY to the "
         "first declaration; a REFERENCE resolves it dynamically",
         DUPNAMES),
        ("kreset.rxt",
         "SS3.4(b): `\\K` is a PATH fact, not capture state -- it survives "
         "the return that undoes everything else",
         KRESET),
        ("zerodef.rxt",
         "SS4.4c: the slot layout must count every EMITTED callee region, "
         "including one parked under `X{0}` -- plain/recursive/atomic/"
         "rung-bearing, each against its `{1}` non-{0} twin",
         ZERODEF),
        ("leadingzero.rxt",
         "SS2.4a: the whole digit run after `(?` or inside `\\g<>` is "
         "decimal; 0 is the root, not 'group 0'",
         LEADINGZERO),
        ("mrl.rxt",
         "SS4.4b: `pcrec_minw`'s Kleene-from-infinity fixpoint over the "
         "call graph -- the withdrawn-gloss witness and its infinity control",
         MRL),
        ("slotfamilies.rxt",
         "SS5.3b: the two MEASURED slot families a naive `W` loses -- "
         "PENDING (a lost match) and CUT_MARK (a false match)",
         SLOTFAMILIES),
        ("quantified.rxt",
         "SS2.6: a call is an ordinary repeatable item, twelve spellings, "
         "the empty-body guard, and `(?R)*`'s unconditional give-up",
         QUANTIFIED),
        ("inlookaround.rxt",
         "SS3.4(d)/(e) (a call INSIDE a lookaround) and SS3.5's mirror "
         "image (a call TO a group whose lexical home is one)",
         INLOOKAROUND),
        ("nocaptures.rxt",
         "SS4.3: a call target joins the marked set -- one-hop and "
         "two-hop, ordinary-axis pins (the --no-captures axis itself is a "
         "reported gap, see the file header)",
         NOCAPTURES),
    ]
    for fname, blurb, sections in files:
        extra = NOCAPTURES_NOTE if fname == "nocaptures.rxt" else ""
        c = write(fname, HDR % (fname, blurb) + extra, sections)
        for k in tot:
            tot[k] += c[k]
    print("-" * 72)
    print("TOTAL %d blocks, %d m/n cells, %d perr, %d gu"
          % (tot['blocks'], tot['cells'], tot['perr'], tot['gu']))


if __name__ == "__main__":
    main()
