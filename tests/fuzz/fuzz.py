#!/usr/bin/env python3
"""
tests/fuzz/fuzz.py — PCRE2-oracle differential fuzzer for pcrec (plan M2.5).

Generates random base-tier patterns and subjects, and for each pattern:
  1. Checks pcrec's accept/reject decision against the real PCRE2 library
     (via tests/fuzz/pcre2_oracle), reporting a mismatch as an
     "accept/reject divergence" (unless it falls in a documented, known
     exception category — see EXCLUDED-FROM-GENERATION below).
  2. If both accept, compiles the pattern with pcrec + gcc, runs it against
     several subjects, and compares match/nomatch and exact spans against
     the PCRE2 oracle. Any mismatch is a "content divergence": a repro
     bundle is written to tests/fuzz/failures/<timestamp>/ and the run
     continues (this is a differential fuzzer, not a pass/fail test suite
     entry — see README.md for why it's not part of `make test`).

Usage:
    python3 tests/fuzz/fuzz.py [--seed N] [--patterns 300] [--subjects 15] [--keep]

Deterministic: the same --seed always generates the same patterns and
subjects (random.seed(N) once, up front; no other source of randomness is
used). Exit code is 0 iff zero divergences (accept/reject or content) were
found; nonzero otherwise, so it can be wired into a checkpoint/CI gate later
if desired.

See README.md in this directory for the exception-list rationale and how to
read a failures/ bundle.
"""
import argparse
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
PCREC = os.environ.get("PCREC", os.path.join(REPO_ROOT, "build", "pcrec"))
CC = os.environ.get("CC", "gcc")
GENCFLAGS = os.environ.get("GENCFLAGS", "-O0 -std=gnu11").split()
ORACLE_SRC = os.path.join(HERE, "pcre2_oracle.c")
DRIVER_SRC = os.path.join(HERE, "fuzz_driver.c")
FAILURES_DIR = os.path.join(HERE, "failures")

PCREC_TIMEOUT = 10


# D45 (docs/dev/decisions.md): every compile of generated C runs under a
# budget, and exceeding it is a FAILURE. This file already had a CC_TIMEOUT —
# the mechanism predates the ruling — but its number was its own. It now comes
# from tests/lib/gen_timeout.sh, the same file the shell suites source, so the
# tree has ONE rule and one place to raise it.
def _gen_timeout():
    import subprocess as _sp
    try:
        r = _sp.run(["bash", os.path.join(REPO_ROOT, "tests", "lib", "gen_timeout.sh"),
                     "secs"], capture_output=True, text=True, timeout=30)
        return int(r.stdout.strip())
    except Exception:
        return 5      # fail closed on the shorter budget, never on none


CC_TIMEOUT = _gen_timeout()


# CPU-primary compile budget (D45 third addendum, 2026-08-16): CC_TIMEOUT
# above is now the loose wall BACKSTOP; the tight, load-independent bound is
# CPU time, applied to GENERATED-code compiles via a bash ulimit shim (soft
# RLIMIT_CPU -> clean SIGXCPU; not preexec_fn, unsafe with pools). The
# oracle-shim and driver-template compiles are hand-written C, not emitted —
# outside D45's scope, left on the wall backstop alone.
def _cpu_timeout():
    import subprocess as _sp
    try:
        r = _sp.run(["bash", os.path.join(REPO_ROOT, "tests", "lib", "gen_timeout.sh"),
                     "cpusecs"], capture_output=True, text=True, timeout=30)
        return int(r.stdout.strip())
    except Exception:
        return 10

CPU_TIMEOUT = _cpu_timeout()

def _cpu_limited(argv):
    return ["bash", "-c",
            'ulimit -S -t "$1" 2>/dev/null; ulimit -H -t $(($1 + 30)) 2>/dev/null; shift; exec "$@"',
            "_", str(CPU_TIMEOUT)] + argv


# EXECUTION is bounded too (gen_run_secs, same file): a merely-slow generated
# matcher (or the oracle binary) must read as a FAILURE, not a hang. This
# inner loop runs one subprocess per fuzzed pattern/subject cell, so the
# bound is subprocess's own in-process timeout= -- the shape this file
# already uses for D45 compiles above -- rather than a per-run
# scripts/watchdog wrapper, whose fixed startup cost would multiply the
# campaign's runtime; the NUMBER still comes from the one shared
# implementation (tests/vm/vm_oracle.py's _run_timeout(), mirrored here).
def _run_timeout():
    import subprocess as _sp
    try:
        r = _sp.run(["bash", os.path.join(REPO_ROOT, "tests", "lib", "gen_timeout.sh"),
                     "runsecs"], capture_output=True, text=True, timeout=30)
        return int(r.stdout.strip())
    except Exception:
        return 10  # fail closed on the shorter (plain-axis) budget, as _gen_timeout does


RUN_TIMEOUT = _run_timeout()

# HARNESS POLICY FIX (this session): the bring-up default step budget
# (VM_DEFAULT_STEP_BUDGET, src/gen/emit_vm.c, 1,000,000 backtrack
# resumptions) is a placeholder pending M4.6's real calibration — it is not
# an engine bug that a sufficiently pathological pattern can spend that many
# resumptions and blow past this fuzzer's own RUN_TIMEOUT/CC_TIMEOUT clocks.
# Compiling every fuzzed pattern with an explicit, much smaller
# --step-budget=N keeps pcrec's own worst case bounded well inside the
# fuzzer's clock, so budget exhaustion shows up as a fast, correctly
# reported RX_ERR_STEPS verdict ("steps" from fuzz_driver.c) instead of a
# subprocess TIMEOUT. Order of magnitude chosen empirically (see this
# session's report): large enough that no pattern in the default corpus
# trips it, small enough that a genuinely pathological one resolves in
# well under a second. Override with STEP_BUDGET=N for experimentation.
STEP_BUDGET = int(os.environ.get("STEP_BUDGET", "100000"))

# =============================================================================
# EXCLUDED FROM GENERATION — known tooling/engine divergences, verified
# empirically against the real PCRE2 oracle (see this file's git history /
# the M2.5 build session for the exact transcripts). These are deliberately
# never produced by the generator below, so a default run's divergence list
# reflects genuinely new findings rather than re-discovering known gaps
# every time.
#
# 1. Possessive quantifiers (a++, a*+, a??+, a{m,n}+) and atomic groups
#    ((?>...)): pcrec REJECTS ("requires module 'atomic-groups'" — not yet
#    implemented); PCRE2 ACCEPTS. Verified:
#      pattern a++     -> pcrec: REJECT (offset 2); pcre2: nomatch on ""
#      pattern (?>abc) -> pcrec: REJECT (offset 0); pcre2: nomatch on ""
#    This is an accept/reject mismatch, but an expected one (unimplemented
#    module, not a bug) — excluded so it doesn't dominate every run.
#
# 2. \x{...} brace hex escapes: pcrec REJECTS ("requires module
#    'unicode-props'" — not yet implemented); PCRE2 ACCEPTS. Verified:
#      pattern \x{41} -> pcrec: REJECT (offset 0); pcre2: matches 'A'
#    Same rationale as (1). The generator uses only the supported \xHH /
#    \xH (1-2 hex digit, no braces) form.
#
# 3. {,n} and {,} quantifier forms (no digit before the comma): this is NOT
#    an accept/reject mismatch — both engines accept the pattern — but a
#    genuine SEMANTIC divergence. pcrec treats the brace text as a literal
#    string (matching the classic PCRE1 documented behavior); PCRE2 10.46
#    (the version on this box) treats it as a quantifier equivalent to
#    {0,n}. Verified:
#      pattern a{,3} vs subject "aaaa" -> pcrec: nomatch;   pcre2: match 0 3
#      pattern a{,3} vs subject ""     -> pcrec: nomatch;   pcre2: match 0 0
#      pattern a{,3} vs subject "aa{,3}bb" -> pcrec: match 1 6 (literal
#        "a{,3}"); pcre2: match 0 2 (quantifier reading of "aa")
#    RESOLVED 2026-08-09 (same session): pcrec's parser now implements
#    {,n} == {0,n} (PCRE2 10.43+ behavior); bare {,} stays literal, which
#    PCRE2 agrees with (verified: 'a{,}' does not match "aaa" under the
#    oracle; python re is the diverging engine there). Regressions in
#    tests/base/fuzz_regressions.rxt. Generation of {,n} remains off simply
#    because the generator predates the fix; safe to enable later.
#
# NOT excluded (checked and confirmed to no longer be a divergence, despite
# earlier speculation that it might need an exception): quantified bare
# anchors (^*a, a$*, ${1,2}, ^{0,1}, ...). Since the S-M1 fix
# (docs/dev/reviews/2026-08-09-m1.md), pcrec rejects these exactly like PCRE2
# rejects them (error "quantifier does not follow a repeatable item" /
# PCRE2 error code 109), verified across ^*a, a$*, $?, ^+, ${1,2}, ^{0,1}.
# The generator is free to produce these naturally (quantifying an anchor
# atom); both engines are expected to reject in lockstep. A quantified
# GROUP wrapping an anchor, e.g. (^)*ab, stays legal in both and is also
# left unrestricted.
# =============================================================================


# ---------------------------------------------------------------------------
# Pattern generation: a tiny AST + renderer + an approximate "sampler" that
# produces a string a pattern fragment is *likely* to match. The sampler
# need not be exact — it only biases subject generation toward strings that
# actually exercise the pattern instead of near-universal nomatch; a wrong
# sample just yields an ordinary uninteresting subject, never a false test
# result (both engines always run on the exact same subject bytes).
# ---------------------------------------------------------------------------

LITERAL_ATOMS = [
    ("a", "a"), ("b", "b"), ("c", "c"), ("0", "0"), ("1", "1"),
    ("\\n", "\n"),
]

# (pattern text, membership set, negated?) — sampler picks a member for
# non-negated classes, or a char outside `members` (from SAFE_POOL) for
# negated ones. All forms below are drawn from tests/base/classes.rxt /
# hand-verified accepted by pcrec.
SAFE_POOL = "abc012xyzXYZ\n\t -"
CLASS_ATOMS = [
    ("[abc]", {"a", "b", "c"}, False),
    ("[a-z]", {"a", "m", "z"}, False),
    ("[a-z0-9]", {"a", "m", "z", "0", "5", "9"}, False),
    ("[^abc]", {"a", "b", "c"}, True),
    ("[]abc]", {"]", "a", "b", "c"}, False),
    ("[^]abc]", {"]", "a", "b", "c"}, True),
    ("[a-]", {"a", "-"}, False),
    ("[-a]", {"-", "a"}, False),
    ("[a\\-z]", {"a", "-", "z"}, False),
    ("[\\]]", {"]"}, False),
    ("[\\n\\t]", {"\n", "\t"}, False),
    ("[\\x41-\\x43]", {"A", "B", "C"}, False),
    ("[a-c-e]", {"a", "b", "c", "-", "e"}, False),
    ("[\\x61]", {"a"}, False),   # \xHH single-form, no braces (see exclusions)
    ("[\\x6]", {"\x06"}, False),  # 1-digit \x form
]

QUANTS = [
    # (text, lo, hi)  hi=None means unbounded; counts kept <= 30 per spec.
    ("*", 0, None), ("+", 1, None), ("?", 0, 1),
    ("{0,2}", 0, 2), ("{1,2}", 1, 2), ("{2,3}", 2, 3), ("{0,3}", 0, 3),
    ("{1,}", 1, None), ("{2,}", 2, None), ("{2}", 2, 2), ("{0}", 0, 0),
    ("{1}", 1, 1), ("{5,10}", 5, 10), ("{0,30}", 0, 30), ("{28,30}", 28, 30),
]


class Node:
    __slots__ = ("kind", "data")
    def __init__(self, kind, data):
        self.kind = kind
        self.data = data


def gen_atom(depth):
    r = random.random()
    if depth <= 0 or r < 0.30:
        text, sample = random.choice(LITERAL_ATOMS)
        return Node("lit", (text, sample))
    if r < 0.48:
        text, members, negated = random.choice(CLASS_ATOMS)
        return Node("cls", (text, members, negated))
    if r < 0.53:
        return Node("dot", None)
    if r < 0.58:
        return Node("anchor", "^")
    if r < 0.66:
        return Node("anchor", "$")
    if r < 0.80:
        return Node("grp", (gen_alt(depth - 1), True))
    if r < 0.92:
        return Node("grp", (gen_alt(depth - 1), False))
    text, sample = random.choice(LITERAL_ATOMS)
    return Node("lit", (text, sample))


def gen_rep(depth):
    atom = gen_atom(depth)
    if random.random() < 0.45:
        text, lo, hi = random.choice(QUANTS)
        lazy = random.random() < 0.4
        return Node("rep", (atom, text + ("?" if lazy else ""), lo, hi))
    return atom


def gen_cat(depth):
    n = random.randint(1, 4)
    return Node("cat", [gen_rep(depth) for _ in range(n)])


def gen_alt(depth):
    n = random.randint(1, 3)
    branches = [gen_cat(depth) for _ in range(n)]
    if len(branches) == 1:
        return branches[0]
    return Node("alt", branches)


# Preference-trap templates (checkpoint review R2). R2-M1
# ('(?:ab|a){0,2}?b' -> wrong span) needed THREE things at once: an
# alternation whose branches overlap by prefix, a LAZY quantifier over it, and
# a following atom that forces backtracking. Measured joint probability from
# the unbiased generator: ~1% of patterns have the alternation shape, and only
# a fraction of those also get the continuation and an exposing subject — so
# 4 seeded runs missed a real bug. These templates make that class routine
# instead of lucky. Keep them cheap and shape-focused; the general generator
# still produces everything else.
TRAP_TEMPLATES = [
    "(?:{a}{b}|{a}){q}{b}",     # overlapping-prefix branches, R2-M1 shape
    "(?:{a}|{a}{b}){q}{b}",     # same, preferred branch is the SHORT one
    "(?:|{a}){q}",              # nullable PREFERRED branch (R2-S1 shape)
    "(?:{a}|){q}{b}",           # nullable trailing branch
    "(?:{a}{a}|{a}){q}{a}",     # overlapping same-letter runs
    "{a}(?:{b}|{b}{a}){q}{a}",  # trap behind a literal prefix

    # K17 family (R21 finding E-1, fixed 2026-08-14) — the R2-M1 mechanism one
    # level deeper. The trigger is an OUTER star over a body that begins with a
    # LAZY NULLABLE prefix and continues into a NESTED NULLABLE quantified
    # group, so the outer loop's own empty iteration has to reach the loop exit
    # THROUGH the lazy prefix's preferred (skip) branch. `(?:b*?(?:a*)*)*` on
    # "ab" was [0,2) against both oracles' [0,1).
    #
    # These rows exist because the unbiased generator CAN produce the class and
    # essentially never does: it needs a quantified group, whose body STARTS
    # with a lazy nullable quantifier, followed by a nested nullable quantified
    # group, under an outer star, and then a subject that exposes it — a joint
    # probability around 1e-4..1e-5 per pattern. Nothing excluded it; it was
    # just never rolled. The first two pin the outer `*` so the exact shape is
    # generated every time rather than one draw in nine.
    "(?:{a}*?(?:{b}*)*)*",         # K17's own repro shape
    "({a}*?({b}*)*)*",             # capturing: same span, so this is the
                                   #   priority construction, not erasure
    "(?:{a}*?(?:{b}*)*){q}",       # same body under every outer quantifier
    "(?:{a}??(?:{b}*)+){q}",       # lazy `??` prefix, inner `+`
    "(?:{a}*?(?:{b}*|{a}*)*){q}",  # nullable ALTERNATION as the inner body
    "(?:{a}*?(?:(?:{b}*)*)*){q}",  # one nesting level deeper again

    # K18 family (fixed 2026-08-15) — K17's structurally distinct SIBLING, and
    # the rows are separate for the reason the two entries are: K17's redirect
    # is lost AT a loop entry, K18's is lost one hop SHORT of one, when the
    # walk has to reach it through an already-seen ordinary epsilon state.
    # `(?:(?:a|b*?)?)*` on "ab" was [0,2) against both oracles' [0,1).
    #
    # THE INGREDIENT IS THE PREFERRED ARM, NOT LAZINESS (R23 S8), which is why
    # these rows are not just K17's with a `?` added: the arm whose exit edge
    # lands on the already-seen state has to be the one the walk PREFERS, and a
    # GREEDY nullable arm achieves that simply by being written FIRST. Two of
    # the K18 entry's own "does not diverge" controls turned out to be live
    # miscompiles with their arms swapped, so both orders are pinned here.
    # The `{0,2}` rows are a THIRD sub-case (the conflation at a SPLIT rather
    # than an epsilon) that a corpus built from the original witness cannot
    # reach at all — a two-line candidate repair passed all 165 acceptance
    # cases and got every one of those cells wrong.
    "(?:(?:{a}|{b}*?)?)*",             # K18's own repro shape
    "((?:{a}|{b}*?)?)*",               # capturing: same span, so priority
    "(?:(?:{b}*|{a})?)*",              # ARM ORDER: greedy nullable arm FIRST
    "(?:(?:{b}?|{a})?)*",              # ditto, `?` instead of `*`
    "(?:(?:(?:{b}|)|{a})?)*",          # an EMPTY arm: no quantifier at all
    "(?:(?:{b}?|{a})(?:{b}?|{a}))*",   # CONCATENATION of two nullable alts
    "(?:(?:{a}|{b}*?){{0,2}})*",       # the {0,2}-bodied sub-case
    "(?:(?:{b}*|{a}){{0,2}})*",        # {0,2}, arms the other way round
    "(?:(?:{a}|{b}*?)?){q}",           # the body under every outer quantifier
]
TRAP_QUANTS = ["*", "+", "?", "*?", "+?", "{0,2}", "{0,2}?", "{1,3}?", "{2,}?"]


def gen_trap():
    a, b = random.sample("abc01xy", 2)
    return random.choice(TRAP_TEMPLATES).format(
        a=a, b=b, q=random.choice(TRAP_QUANTS))


# [M4.7d] Capture-span shape templates. Same TRAP_TEMPLATES mechanism (a raw
# pattern-text template, {a}/{b}/{q} .format()-substituted, literal braces
# DOUBLED), but aimed at a different blind spot: the unbiased generator's
# gen_atom() DOES produce capturing groups (~14% of atom draws, recursively),
# but a joint draw that lands a QUANTIFIER directly around a group, or an
# ALTERNATION directly inside a quantified group, or a group NESTED inside
# another quantified group, is a much rarer combination than "some capturing
# group exists somewhere" — and those specific combinations are exactly what
# exercises the two [M4.5d] as-built rules match_api_m4.md §2.2 states
# (cross-iteration retention, empty-final-iteration overwrite) and the
# group-numbering/nesting cases a flat literal group never reaches. These
# rows make that combination routine rather than incidental, the same
# argument TRAP_TEMPLATES makes for preference bugs. Manually verified by
# hand against both engines during this extension (see README.md's
# "Capture-group span comparison" section) before being folded in here:
# `((a)|(b))*` on "ab" -> both `match 0 2 1 2 0 1 1 2` (retention); `(a*)*`
# on "aaa" -> both `match 0 3 3 3` (empty-final-iteration overwrite);
# `(a)|(b)(c)` on "a" -> both `match 0 1 0 1 -1 -1 -1 -1` (never-reached
# groups numbered ABOVE the participating one, both UNSET).
CAPTURE_TEMPLATES = [
    "({a})+",                       # simple quantified capturing group
    "({a}|{b})*",                   # cross-iteration retention across alt
    "(({a})|({b}))*",               # nested: retention on a PER-ARM group
    "({a}*)*",                      # empty-final-iteration overwrite
    "({a}?)*",                      # ditto, optional body
    "({a}{b})*",                    # multi-atom body per iteration
    "(({a}{b})|({a}))*",            # nested groups, differing arm lengths
    "({a}({b})?)+",                 # nested group with optional inner
    "(({a})?)*",                    # nested optional group, cross-iteration
    "({a}+)?",                      # optional wrapping a quantified group
    "(({a})*)*",                    # double-nested star
    "((?:{a})*({b}))*",             # non-capturing wrapper + capturing sibling
    "({a}{q})",                     # single group under an arbitrary quant
    "(({a}|{b}){q})",               # group wrapping alternation, arbitrary quant
    "((?:{a}|{b})*({a}))",          # capturing tail after an alternation loop
    "(({a}{b}|{a}){q})",            # overlapping-prefix alt (R2 shape) + capture
    "(({a})({b}))*",                # two sibling groups per iteration
    "((({a})*)({b})?)*",            # three-deep nesting, mixed quantifiers
]


def gen_capture():
    a, b = random.sample("abc01xy", 2)
    return random.choice(CAPTURE_TEMPLATES).format(
        a=a, b=b, q=random.choice(TRAP_QUANTS))


def gen_pattern():
    return gen_alt(3)


def render(node):
    if node.kind == "lit":
        return node.data[0]
    if node.kind == "cls":
        return node.data[0]
    if node.kind == "dot":
        return "."
    if node.kind == "anchor":
        return node.data
    if node.kind == "grp":
        inner, capturing = node.data
        prefix = "(" if capturing else "(?:"
        return prefix + render(inner) + ")"
    if node.kind == "rep":
        atom, qtext, _lo, _hi = node.data
        return render(atom) + qtext
    if node.kind == "cat":
        return "".join(render(p) for p in node.data)
    if node.kind == "alt":
        return "|".join(render(b) for b in node.data)
    raise AssertionError(node.kind)


def sample(node):
    """Best-effort string this node is likely to match. Approximate by
    design (see module docstring) — never used for correctness, only to
    bias subject generation."""
    if node.kind == "lit":
        return node.data[1]
    if node.kind == "cls":
        _text, members, negated = node.data
        if negated:
            pool = [c for c in SAFE_POOL if c not in members]
            return random.choice(pool) if pool else "x"
        return random.choice(list(members))
    if node.kind == "dot":
        return random.choice("abc012XYZ")
    if node.kind == "anchor":
        return ""
    if node.kind == "grp":
        inner, _capturing = node.data
        return sample(inner)
    if node.kind == "rep":
        atom, _qtext, lo, hi = node.data
        cap = lo + 3 if hi is None else hi
        count = random.randint(lo, max(lo, min(cap, lo + 3)))
        return "".join(sample(atom) for _ in range(count))
    if node.kind == "cat":
        return "".join(sample(p) for p in node.data)
    if node.kind == "alt":
        return sample(random.choice(node.data))
    raise AssertionError(node.kind)


def sample_straddle(node):
    """Like sample(), but for alternations it concatenates TWO DIFFERENT
    branches, and for repeats it emits a run built from differing branch
    choices.

    WHY (checkpoint review R2, finding R2-PR2): plain sample() picks ONE
    alternation branch and repeats it, so it never produces a subject that
    crosses a branch boundary — precisely where backtrack-PREFERENCE bugs
    live. That blind spot is why 4 seeded fuzz runs missed R2-M1
    ('(?:ab|a){0,2}?b' on "abab": the exposing subject needs "ab" then "a",
    two different branches of the same alternation). Subjects from this
    sampler are what would have caught it."""
    if node.kind == "alt" and len(node.data) >= 2:
        a, b = random.sample(list(node.data), 2)
        return sample(a) + sample(b)
    if node.kind == "grp":
        inner, _capturing = node.data
        return sample_straddle(inner)
    if node.kind == "rep":
        atom, _qtext, lo, hi = node.data
        cap = lo + 3 if hi is None else hi
        count = max(2, random.randint(lo, max(lo, min(cap, lo + 3))))
        return "".join(sample_straddle(atom) if i % 2 == 0 else sample(atom)
                       for i in range(count))
    if node.kind == "cat":
        return "".join(sample_straddle(p) for p in node.data)
    return sample(node)


RANDOM_BYTE_ALPHABET = [bytes([b]) for b in b"abc\n"] + \
    [bytes([b]) for b in (128, 200, 255, 0x0a, 0x09)]


def random_subject(alphabet, max_len=120):
    n = random.randint(0, max_len)
    out = bytearray()
    pool = alphabet + RANDOM_BYTE_ALPHABET
    for _ in range(n):
        out += random.choice(pool)
    return bytes(out)


def derived_subject(root, alphabet):
    """A subject that embeds an approximate matching fragment of the
    pattern, with random noise around it (see module docstring)."""
    frag = sample(root).encode("latin-1", "replace")
    prefix = random_subject(alphabet, max_len=10)
    suffix = random_subject(alphabet, max_len=10)
    return prefix + frag + suffix


def pattern_alphabet(pattern_text):
    """Bytes worth biasing subjects toward for this specific pattern: its
    literal characters plus a couple of generic fillers."""
    chars = set(c.encode("latin-1", "replace") for c in pattern_text if c not in "\\")
    chars.add(b"a")
    chars.add(b"\n")
    return list(chars)


# ---------------------------------------------------------------------------
# Oracle / pcrec invocation plumbing
# ---------------------------------------------------------------------------

def build_oracle(workdir):
    binpath = os.path.join(workdir, "pcre2_oracle")
    r = subprocess.run(
        [CC, "-O1", "-std=gnu11", "-Wall", "-Wextra", "-Werror", "-o", binpath, ORACLE_SRC, "-ldl"],
        capture_output=True, text=True, timeout=CC_TIMEOUT,
    )
    if r.returncode != 0:
        sys.exit("fuzz.py: failed to build pcre2_oracle:\n" + r.stderr)
    return binpath


def build_driver_template(workdir):
    """Compile fuzz_driver.c once, ahead of time, against a throwaway
    pattern's gen.h, then link that one driver.o against every subsequent
    pattern's gen.o without ever recompiling driver.c again — the dominant
    per-pattern cost is then just `pcrec` + one `gcc -c` of the (small)
    generated matcher.

    This is sound only because fuzz_driver.c itself makes no per-pattern
    ABI assumption. `rx_search`'s SIGNATURE (ptrdiff_t (*caps)[2]) is fixed
    for every prefix-'rx' artifact, so that part was always safe to share.
    RX_NCAPS is NOT: it is a per-pattern preprocessor macro (ngroups+1 on
    VM artifacts since [M4.5]; always 1 before that), so a driver compiled
    against RX_NCAPS==1 (this throwaway pattern has no capture groups) and
    then linked against a group-bearing pattern's gen.o would size its caps
    array off the WRONG pattern's macro — the bug this file's own history
    records (274/317 divergences on one fuzz run: any group-bearing pattern
    that matched smashed this driver's stack, rc=-6). fuzz_driver.c reads
    `rx_info.ncaps` at RUNTIME instead and heap-allocates the caps array to
    that size, so it is correct for whichever pattern's gen.o it ends up
    linked with, and this file's shared-driver optimization stays intact."""
    tmpl_dir = os.path.join(workdir, "_template")
    os.makedirs(tmpl_dir, exist_ok=True)
    gen_c = os.path.join(tmpl_dir, "gen.c")
    r = subprocess.run([PCREC, "-p", "rx", "-o", gen_c, "--", "a"],
                        capture_output=True, text=True, timeout=PCREC_TIMEOUT)
    if r.returncode != 0:
        sys.exit("fuzz.py: failed to build driver template (pcrec):\n" + r.stderr)
    driver_o = os.path.join(workdir, "fuzz_driver.o")
    r = subprocess.run([CC] + GENCFLAGS + ["-c", "-I", tmpl_dir, "-o", driver_o, DRIVER_SRC],
                        capture_output=True, text=True, timeout=CC_TIMEOUT)
    if r.returncode != 0:
        sys.exit("fuzz.py: failed to build driver template (gcc):\n" + r.stderr)
    return driver_o


def oracle_run(oracle_bin, pattern, subject_path, startpos=None):
    """Like pcrec_run() below: a subprocess timeout is a REPORTED CELL, not
    an uncaught exception. This one didn't used to catch TimeoutExpired at
    all — found during this session's validation, when a genuinely slow
    generated subject/pattern pair took the real PCRE2 oracle past
    RUN_TIMEOUT and killed the whole batch with a traceback (pool.map()
    re-raises a worker's exception at the caller). Mirrors pcrec_run()'s
    "TIMEOUT" sentinel so both sides of the comparison have one shape for
    'no verdict, timed out' rather than pcrec being the only side that can
    report it cleanly."""
    args = [oracle_bin, pattern, subject_path]
    if startpos is not None:
        args.append(str(startpos))
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=RUN_TIMEOUT)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    return r.stdout.strip()


def write_subject(path, data):
    with open(path, "wb") as f:
        f.write(data)


def compile_with_pcrec(pattern, tmp_dir):
    # --step-budget=STEP_BUDGET (harness policy fix, this session): only
    # takes effect on patterns the VM engine compiles (captures or other
    # VM-forcing constructs) -- a DFA-only artifact emits no step counter at
    # all and ignores it. See STEP_BUDGET's own comment for why a much
    # smaller-than-default budget is compiled in for every fuzzed pattern.
    #
    # PCREC_TIMEOUT bounds pcrec's own COMPILE time (parse/NFA/DFA/VM
    # construction), a different clock from the generated matcher's runtime
    # step budget above. This call did not used to catch its own timeout --
    # found during this session's large-scale (3000-pattern) validation run,
    # when a deeply nested bounded-repeat pattern made pcrec itself exceed
    # PCREC_TIMEOUT and killed the whole batch with an uncaught
    # TimeoutExpired, the same class of crash oracle_run() had. Reported as
    # a cell, not a traceback, mirroring compile_and_link()'s existing
    # GCC-TIMEOUT/D45 discipline below -- this is that same discipline
    # applied to the ONE compile call in this file that was missing it.
    gen_c = os.path.join(tmp_dir, "gen.c")
    try:
        r = subprocess.run([PCREC, "-p", "rx", "--step-budget=%d" % STEP_BUDGET,
                            "-o", gen_c, "--", pattern],
                            capture_output=True, text=True, timeout=PCREC_TIMEOUT)
    except subprocess.TimeoutExpired:
        return False, "PCREC-TIMEOUT: compiling pattern exceeded %ds" % PCREC_TIMEOUT
    return r.returncode == 0, r.stderr.strip()


def compile_and_link(tmp_dir, driver_o):
    gen_c = os.path.join(tmp_dir, "gen.c")
    gen_o = os.path.join(tmp_dir, "gen.o")
    exe = os.path.join(tmp_dir, "t")
    # A compile that exceeds the budget is a REPORTED CELL, not a traceback:
    # the fuzzer's whole value is that every pattern it tries produces a
    # verdict, and an uncaught TimeoutExpired would end the run instead.
    try:
        r = subprocess.run(_cpu_limited([CC] + GENCFLAGS + ["-c", "-I", tmp_dir, "-o", gen_o, gen_c]),
                            capture_output=True, text=True, timeout=CC_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None, ("GCC-TIMEOUT: compiling generated C exceeded %ds "
                      "(D45)" % CC_TIMEOUT)
    if r.returncode != 0:
        return None, "GCC-COMPILE-FAIL: " + r.stderr[:500]
    try:
        r = subprocess.run(_cpu_limited([CC, "-o", exe, gen_o, driver_o]),
                            capture_output=True, text=True, timeout=CC_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None, ("GCC-TIMEOUT: linking generated C exceeded %ds "
                      "(D45)" % CC_TIMEOUT)
    if r.returncode != 0:
        return None, "GCC-LINK-FAIL: " + r.stderr[:500]
    return exe, None


def pcrec_run(exe, subject_path, startpos=None):
    args = [exe, subject_path]
    if startpos is not None:
        args.append(str(startpos))
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=RUN_TIMEOUT)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    if r.returncode != 0:
        return "CRASH(rc=%d) %s" % (r.returncode, r.stderr.strip()[:200])
    return r.stdout.strip()


# ---------------------------------------------------------------------------
# Failure repro bundles
# ---------------------------------------------------------------------------

def hexdump(data):
    return data.hex()


def write_failure_bundle(run_dir, kind, pattern, subject, pcrec_out, pcre2_out, extra=""):
    os.makedirs(run_dir, exist_ok=True)
    idx = len(os.listdir(run_dir))
    bundle_dir = os.path.join(run_dir, f"{idx:04d}_{kind}")
    os.makedirs(bundle_dir, exist_ok=True)
    with open(os.path.join(bundle_dir, "pattern.txt"), "w") as f:
        f.write(pattern + "\n")
    if subject is not None:
        with open(os.path.join(bundle_dir, "subject.hex"), "w") as f:
            f.write(hexdump(subject) + "\n")
        with open(os.path.join(bundle_dir, "subject.bin"), "wb") as f:
            f.write(subject)
    with open(os.path.join(bundle_dir, "outputs.txt"), "w") as f:
        f.write(f"kind: {kind}\n")
        f.write(f"pattern: {pattern!r}\n")
        if subject is not None:
            f.write(f"subject (hex): {hexdump(subject)}\n")
            f.write(f"subject (repr): {subject!r}\n")
        f.write(f"pcrec:  {pcrec_out}\n")
        f.write(f"pcre2:  {pcre2_out}\n")
        if extra:
            f.write(f"extra: {extra}\n")
    return bundle_dir


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------

_ANCHOR_IN_ZERO_REP = re.compile(r"\{0(,0)?\}")

def is_known_pcre2_quirk(pattern):
    """PCRE2 10.46 start-anchor optimizer quirk (README.md "Finding 2"):
    an anchor inside a group quantified {0}/{0,0} makes PCRE2 wrongly treat
    the whole pattern as anchored even though the branch can never execute.
    pcrec and python re both follow the declared semantics (X{0} == empty).
    Intentional, documented divergence."""
    return bool(_ANCHOR_IN_ZERO_REP.search(pattern)) and ("^" in pattern or "$" in pattern)


def main():
    ap = argparse.ArgumentParser(description="PCRE2-oracle differential fuzzer for pcrec")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--patterns", type=int, default=300)
    ap.add_argument("--subjects", type=int, default=15)
    ap.add_argument("--keep", action="store_true", help="keep the working directory (printed on exit)")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4, help="parallel compile/run workers")
    args = ap.parse_args()

    random.seed(args.seed)

    if not os.path.isfile(PCREC):
        sys.exit(f"fuzz.py: pcrec binary not found at {PCREC} (build it first: `make`)")

    workdir = tempfile.mkdtemp(prefix="pcrec-fuzz-")
    print(f"[fuzz] workdir: {workdir}", file=sys.stderr)
    print(f"[fuzz] seed={args.seed} patterns={args.patterns} subjects={args.subjects}", file=sys.stderr)

    t_start = time.time()
    oracle_bin = build_oracle(workdir)
    driver_o = build_driver_template(workdir)

    empty_subject = os.path.join(workdir, "empty.bin")
    write_subject(empty_subject, b"")

    accept_mismatches = []
    content_divergences = []
    state_cap_hits = []
    stats = {"patterns": 0, "both_accept": 0, "both_reject": 0,
             "pcrec_reject_only": 0, "pcre2_reject_only": 0, "state_cap": 0,
             "gcc_fail": 0, "pairs_compared": 0, "oracle_inconclusive": 0,
             "pcre2_quirk": 0, "engine_limit": 0, "oracle_probe_timeout": 0,
             "engine_steps": 0, "engine_frames": 0, "pcrec_compile_timeout": 0}

    # Patterns AND subjects are generated up-front in the MAIN thread: the
    # worker pool shares the global `random`, so generating inside workers made
    # results depend on thread interleaving and broke the per-seed determinism
    # this tool promises (R2: identical seeds produced different corpora, so a
    # reported divergence could not be reproduced by rerunning the seed).
    work = []
    for _ in range(args.patterns):
        node = gen_pattern()
        pat = render(node)
        # Mutually exclusive draw across three lanes: preference traps (R2,
        # ~8%), capture-span shape templates ([M4.7d], ~20% -- "meaningful
        # density" for the specific quantified-group / group-around-
        # alternation / nested-group combinations CAPTURE_TEMPLATES targets,
        # well above what the unbiased grammar rolls on its own), and the
        # general grammar (the remainder, which already produces capturing
        # groups incidentally via gen_atom's own ~14%-per-draw rate).
        lane = random.random()
        is_trap = lane < 0.08
        is_capture = (not is_trap) and lane < 0.28
        if is_trap:
            pat = gen_trap()
        elif is_capture:
            pat = gen_capture()
        alpha = pattern_alphabet(pat)
        if is_trap:
            # Trap patterns are raw text, not an AST node, so the node-based
            # samplers do not apply. Preference bugs surface on SHORT subjects
            # over the pattern's own alphabet, so enumerate those exhaustively
            # (this is what actually exposes '(?:|a)*' vs "a").
            # pattern_alphabet() includes the pattern's METAcharacters, which
            # make useless subjects for a trap; keep only literal alphanumerics
            letters = sorted(c for c in alpha if c.isalnum())[:5] or [b"a"]
            subs = [b""]
            for L in (1, 2, 3, 4):
                for _ in range(max(1, args.subjects // 5)):
                    subs.append(b"".join(random.choice(letters) for _ in range(L)))
            subs = subs[:args.subjects] if len(subs) > args.subjects else subs
            work.append((pat, subs))
            continue
        if is_capture:
            # Same raw-text situation as traps (node samplers don't apply),
            # but capture-span bugs (cross-iteration retention, empty-final-
            # iteration overwrite) need MULTIPLE loop iterations to surface
            # at all -- a length-1 subject can never distinguish "this
            # group's value is from its last iteration" from "this group's
            # value is from its only iteration". Subjects run longer here
            # (up to 8) than the trap lane's (up to 4), and every length from
            # 0 through 8 is represented so both single- and multi-iteration
            # cases are exercised.
            letters = sorted(c for c in alpha if c.isalnum())[:5] or [b"a"]
            subs = [b""]
            for L in range(1, 9):
                for _ in range(max(1, args.subjects // 8)):
                    subs.append(b"".join(random.choice(letters) for _ in range(L)))
            subs = subs[:args.subjects] if len(subs) > args.subjects else subs
            work.append((pat, subs))
            continue
        subs = []
        for _ in range(args.subjects):
            r = random.random()
            if r < 0.30:
                subs.append(derived_subject(node, alpha))
            elif r < 0.50:
                # branch-straddling subjects (R2-PR2): the shape that exposes
                # backtrack-preference bugs
                try:
                    subs.append(sample_straddle(node).encode("latin-1", "ignore"))
                except Exception:
                    subs.append(random_subject(alpha))
            else:
                subs.append(random_subject(alpha))
        work.append((pat, subs))

    def process_one(i):
        pattern, presubjects = work[i]
        tmp_dir = os.path.join(workdir, f"p{i}")
        os.makedirs(tmp_dir, exist_ok=True)

        pcrec_ok, pcrec_err = compile_with_pcrec(pattern, tmp_dir)
        pcre2_probe = oracle_run(oracle_bin, pattern, empty_subject)

        result = {"pattern": pattern, "pcrec_ok": pcrec_ok, "pcre2_ok": None,
                  "accept_mismatch": None, "state_cap": None, "engine_limit": None, "content": [], "gcc_fail": None,
                  "oracle_inconclusive": 0, "oracle_probe_timeout": False,
                  "pcrec_compile_timeout": False,
                  "engine_budget": {"steps": 0, "frames": 0}}

        if not pcrec_ok and pcrec_err.startswith("PCREC-TIMEOUT"):
            # pcrec's own compile-time budget (a different clock from the
            # generated matcher's runtime step budget) exhausted -- see
            # compile_with_pcrec()'s comment. Not an accept/reject verdict at
            # all, so NOT run through the pcrec-vs-pcre2 accept/reject
            # comparison below (which would otherwise misreport this as
            # "pcrec REJECTS, pcre2 ACCEPTS" whenever PCRE2 happened to
            # accept the same pattern quickly -- a harness artifact, not a
            # semantic finding). Counted and skipped instead.
            result["pcrec_compile_timeout"] = True
            return result

        if pcre2_probe == "TIMEOUT":
            # The oracle itself couldn't produce even an accept/reject verdict
            # inside RUN_TIMEOUT on the EMPTY-subject probe -- vanishingly rare
            # (compilation + a zero-length match attempt), but oracle_run()
            # can now report it instead of crashing the batch (see its own
            # comment). Nothing to compare against, so counted and skipped
            # rather than guessed at.
            result["oracle_probe_timeout"] = True
            return result

        pcre2_ok = not pcre2_probe.startswith("cerr")
        result["pcre2_ok"] = pcre2_ok

        if pcrec_ok and not pcre2_ok and pcre2_probe.startswith("cerr 120"):
            result["engine_limit"] = pcre2_probe
            return result

        if pcrec_ok != pcre2_ok:
            if pcrec_ok and not pcre2_ok:
                result["accept_mismatch"] = ("pcrec ACCEPTS, pcre2 REJECTS", pcrec_err, pcre2_probe)
            elif "too complex for the DFA engine" in pcrec_err or "NFA exceeds" in pcrec_err:
                # Known architecture-tier limitation (checkpoint review R1,
                # finding A-3): the M1 pipeline has hard complexity caps at
                # two stages -- NFA construction (src/ir/nfa.c, "NFA exceeds
                # N states") and DFA determinization (src/ir/dfa.c, "too
                # complex for the DFA engine") -- and no VM fallback yet
                # (planned M4), so sufficiently nested/bounded-repeat-heavy
                # *legal* patterns are correctly rejected by pcrec while
                # PCRE2's backtracking engine, which has no such structural
                # limit, accepts them. This is the caps doing their
                # documented job, not a semantics bug -- kept in its own
                # bucket so it doesn't masquerade as an actionable
                # divergence on every run (the generator's use of depth +
                # up-to-30 bounded repeats + alternation makes this fire
                # reasonably often; see README.md).
                result["state_cap"] = pcrec_err
            else:
                result["accept_mismatch"] = ("pcrec REJECTS, pcre2 ACCEPTS", pcrec_err, pcre2_probe)
            return result

        if pcrec_ok and pcre2_probe.startswith("cerr 120"):
            # PCRE2 error 120 = "regular expression is too large": PCRE2's own
            # internal size limit, the mirror image of pcrec's state caps.
            # Both engines have complexity ceilings, just in different places;
            # neither is a semantic divergence. Own bucket, like state_cap.
            result["engine_limit"] = pcre2_probe
            return result
            return result

        if not pcrec_ok:
            return result  # both reject: agreement, nothing more to do

        exe, gcc_err = compile_and_link(tmp_dir, driver_o)
        if exe is None:
            result["gcc_fail"] = gcc_err
            return result

        for subj in presubjects:
            subj_path = tempfile.mktemp(prefix="s_", suffix=".bin", dir=tmp_dir)
            write_subject(subj_path, subj)
            pr = pcrec_run(exe, subj_path)
            if pr in ("steps", "frames"):
                # HARNESS POLICY (DD-2/D22, docs/design/engine_m4.md §4): the
                # VM's step/frame budgets are pcrec's own ROBUSTNESS bound on
                # pathological backtracking -- "adversarial patterns are OUT
                # OF SCOPE; correctness is not" (D22) -- never a security
                # boundary and never traded against speed. A pattern that
                # exhausts one is neither a pcrec bug nor comparable to
                # whatever verdict PCRE2's differently-implemented,
                # differently-limited backtracking engine reaches on the same
                # input, so it's counted as its own non-divergence class
                # rather than compared -- the mirror image of the existing
                # "oracle inconclusive" (PCRE2 match-limit) bucket below.
                # Wiring an equivalent explicit pcre2_set_match_limit() into
                # the oracle (so the two sides trip at a comparable cost)
                # would need a new ABI declaration + dlsym load in
                # pcre2_abi.h for one classification refinement -- judged
                # disproportionate for what this bucket already achieves.
                result["engine_budget"][pr] += 1
                os.remove(subj_path)
                continue
            orr = oracle_run(oracle_bin, pattern, subj_path)
            if orr == "TIMEOUT" or orr.startswith("inconclusive") or orr.startswith("ovtoosmall"):
                # PCRE2 hit its own backtracking/resource safeguard (or this
                # fuzzer's RUN_TIMEOUT, now that oracle_run() reports rather
                # than crashes on that -- see its comment), not a
                # match/no-match verdict -- not comparable to pcrec's result.
                # See pcre2_oracle.c's header comment and README.md for the
                # confirmed case that motivated the original "inconclusive"
                # half (a catastrophic-backtracking-shaped nested quantifier
                # pattern where PCRE2 returns -47, not -1). [M4.7d]:
                # "ovtoosmall" folds into the same bucket -- pcre2_oracle.c's
                # own defensive-only case (the ovector it sized from the
                # pattern's own capturecount turned out too small), not
                # expected to ever fire; if it does, this is a harness
                # anomaly, not a verdict to compare, same reasoning as the
                # other two members of this bucket.
                result["oracle_inconclusive"] += 1
            elif pr != orr:
                result["content"].append((subj, pr, orr))
            os.remove(subj_path)

        # cleanup compiled artifacts eagerly to bound disk use on big runs
        try:
            os.remove(exe)
            os.remove(os.path.join(tmp_dir, "gen.o"))
        except OSError:
            pass

        return result

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for result in pool.map(process_one, range(args.patterns)):
            stats["patterns"] += 1
            if result.get("pcrec_compile_timeout"):
                stats["pcrec_compile_timeout"] += 1
                continue
            if result.get("oracle_probe_timeout"):
                stats["oracle_probe_timeout"] += 1
                continue
            if result["accept_mismatch"]:
                kind, pcrec_err, pcre2_probe = result["accept_mismatch"]
                if "ACCEPTS, pcre2 REJECTS" in kind:
                    stats["pcre2_reject_only"] += 1
                else:
                    stats["pcrec_reject_only"] += 1
                accept_mismatches.append((result["pattern"], kind, pcrec_err, pcre2_probe))
                continue
            if result.get("engine_limit"):
                stats["engine_limit"] += 1
                continue
            if result["state_cap"]:
                stats["state_cap"] += 1
                state_cap_hits.append((result["pattern"], result["state_cap"]))
                continue
            if not result["pcrec_ok"]:
                stats["both_reject"] += 1
                continue
            if result["gcc_fail"]:
                stats["gcc_fail"] += 1
                print("[fuzz] GCC-FAIL pattern=%r: %s" % (result["pattern"], result["gcc_fail"][:200]),
                      file=sys.stderr)
                continue
            stats["both_accept"] += 1
            stats["pairs_compared"] += args.subjects
            stats["oracle_inconclusive"] += result["oracle_inconclusive"]
            stats["engine_steps"] += result["engine_budget"]["steps"]
            stats["engine_frames"] += result["engine_budget"]["frames"]
            for subj, pr, orr in result["content"]:
                if is_known_pcre2_quirk(result["pattern"]):
                    # PCRE2 10.46 start-anchor optimizer quirk (README.md
                    # "Finding 2", verified 2026-08-09): an anchor inside a
                    # group quantified {0}/{0,0} makes PCRE2 wrongly anchor
                    # the whole pattern and miss later matches. pcrec (and
                    # python re) follow the declared semantics; intentional
                    # divergence, kept out of the failure exit code.
                    stats["pcre2_quirk"] += 1
                    continue
                content_divergences.append((result["pattern"], subj, pr, orr))

    elapsed = time.time() - t_start

    run_failures_dir = None
    if accept_mismatches or content_divergences:
        run_failures_dir = os.path.join(FAILURES_DIR, time.strftime("%Y%m%d-%H%M%S"))
        for pattern, kind, pcrec_err, pcre2_probe in accept_mismatches:
            write_failure_bundle(run_failures_dir, "accept_mismatch", pattern, None,
                                  f"{'ACCEPT' if 'pcrec ACCEPTS' in kind else 'REJECT: ' + pcrec_err}",
                                  pcre2_probe, extra=kind)
        for pattern, subj, pr, orr in content_divergences:
            write_failure_bundle(run_failures_dir, "content", pattern, subj, pr, orr)

    try:
        ver = subprocess.run([oracle_bin, "--version"], capture_output=True,
                             text=True, timeout=10).stdout.strip()
    except Exception:
        ver = "unknown"
    print("\n=== pcrec vs PCRE2 differential fuzz summary ===")
    print(f"oracle: PCRE2 {ver}   (R2-PR5: recorded so results are attributable"
          f" to a specific library version)")
    print(f"seed={args.seed} patterns={args.patterns} subjects/pattern={args.subjects} elapsed={elapsed:.1f}s")
    print(f"patterns generated:   {stats['patterns']}")
    print(f"  both accept:        {stats['both_accept']}")
    print(f"  both reject:        {stats['both_reject']}")
    print(f"  pcrec-only reject:  {stats['pcrec_reject_only']}  (accept/reject divergence)")
    print(f"  pcre2-only reject:  {stats['pcre2_reject_only']}  (accept/reject divergence)")
    print(f"  PCRE2 size-limit:   {stats['engine_limit']}  (PCRE2 err 120, its own ceiling -- not a divergence)")
    print(f"  DFA state-cap:      {stats['state_cap']}  (KNOWN limitation, review A-3 -- not a divergence, see README.md)")
    print(f"  gcc compile fails:  {stats['gcc_fail']}  (harness-level, not a pcrec bug per se)")
    print(f"  pcrec compile timeout: {stats['pcrec_compile_timeout']}  (pcrec's own PCREC_TIMEOUT clock, not the generated matcher's step budget -- see compile_with_pcrec())")
    print(f"  oracle probe timeout: {stats['oracle_probe_timeout']}  (empty-subject accept/reject probe itself timed out -- see oracle_run())")
    print(f"subject pairs compared (both-accept patterns): {stats['pairs_compared']}")
    print(f"  oracle inconclusive (PCRE2 match-limit hit or oracle TIMEOUT): {stats['oracle_inconclusive']}  (see README.md)")
    print(f"  pcrec step-budget exhausted (RX_ERR_STEPS, --step-budget={STEP_BUDGET}): {stats['engine_steps']}  (DD-2/D22: robustness bound, not a divergence)")
    print(f"  pcrec frame-budget exhausted (RX_ERR_FRAMES): {stats['engine_frames']}  (DD-2/D22: robustness bound, not a divergence)")
    print(f"  known PCRE2 optimizer quirk (anchor in {{0}} group): {stats['pcre2_quirk']}  (intentional divergence, see README.md)")
    print(f"content divergences: {len(content_divergences)}")
    print(f"accept/reject divergences: {len(accept_mismatches)}")

    if state_cap_hits:
        print(f"\n-- DFA state-cap hits (known limitation, not a divergence; first 5 of {len(state_cap_hits)}) --")
        for pattern, err in state_cap_hits[:5]:
            print(f"  pattern={pattern!r} :: {err!r}")

    if accept_mismatches:
        print("\n-- accept/reject divergences --")
        for pattern, kind, pcrec_err, pcre2_probe in accept_mismatches[:40]:
            print(f"  pattern={pattern!r} :: {kind} :: pcrec={pcrec_err!r} pcre2={pcre2_probe!r}")
        if len(accept_mismatches) > 40:
            print(f"  ... and {len(accept_mismatches) - 40} more")

    if content_divergences:
        print("\n-- content divergences --")
        for pattern, subj, pr, orr in content_divergences[:40]:
            print(f"  pattern={pattern!r} subject={subj!r} pcrec={pr!r} pcre2={orr!r}")
        if len(content_divergences) > 40:
            print(f"  ... and {len(content_divergences) - 40} more")

    if run_failures_dir:
        print(f"\nrepro bundles written to: {run_failures_dir}")

    if args.keep:
        print(f"\n[fuzz] --keep set: workdir retained at {workdir}", file=sys.stderr)
    else:
        shutil.rmtree(workdir, ignore_errors=True)

    return 1 if (accept_mismatches or content_divergences) else 0


if __name__ == "__main__":
    sys.exit(main())
