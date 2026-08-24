#!/usr/bin/env python3
"""tests/lookaround/expand_corpus.py — [M6.6.2] wave E2's CORPUS GENERATOR
(design `lookaround_design.md` §6.3), the text half of
`run_expansion_diff.sh`.

WHAT IT IS. Every assertion module `assertions` ships has a LOOKAROUND
DEFINITION (§6.1). Textually replacing each assertion in
`tests/assertions/`'s corpus by its definition turns a 468-block,
10,120-cell, libpcre2-verified corpus into a LOOKAROUND corpus for free —
one whose expectations are not this module's guesses, because they were
written for a module that already ships.

**IT IS A CORPUS GENERATOR, NOT A PRODUCT MECHANISM** (Frank, 2026-08-23;
the [DD-14] row's own text; design §6.4). It emits PATTERN TEXT that the
compiler then sees as an ordinary user-written lookaround. Nothing here
runs inside pcrec, and nothing here is a desugaring pass. The PRODUCT-side
substitution is [DD-14]'s subroutine-call primitive, after this module
lands — "I don't want parallel mechanisms if we can avoid it".

**THE DRIVER'S OWN FAILURE MODE, and the reason this file holds a LITERAL
table.** Every check this project has written that failed, failed by
sharing a source with the thing it controls. If the expansion table were
read out of `src/parse/mod_assertions.c` — or derived by asking the
compiler what `\\b` lowers to — then `A == B` (§6.3's self-oracle) would be
a tautology: two spellings of one source agreeing with themselves. So the
table below is TRANSCRIBED from design §6.1 / D66 / [DD-11], character for
character, and `run_expansion_diff.sh` §0 re-verifies it against libpcre2
before any of it is used. If [DD-11] later rewrites the assertions to
their definitions on the [DD-14] primitive, **this table and the
compiler's must remain two sources.**

WHAT IT WRITES. A work plan under `<outdir>`, one directory per QUALIFYING
block:

    <outdir>/report.txt            the population report (also on stdout)
    <outdir>/counts.tsv            machine-readable population counts
    <outdir>/blocks               one block id per line, in corpus order
    <outdir>/b<NNNN>/pattern      the ORIGINAL (folded) pattern, verbatim
    <outdir>/b<NNNN>/feats        the --features list both arms compile with
    <outdir>/b<NNNN>/origin       "<file>:<lineno>", for a failure message
    <outdir>/b<NNNN>/subjects/sNNN   one file per distinct subject
    <outdir>/b<NNNN>/cells        "<subject-file>\\t<startpos>", corpus order
    <outdir>/b<NNNN>/expect       the corpus's own answer for each cell
    <outdir>/b<NNNN>/gen.tsv      "<gid>\\t<policy>\\t<identical>\\t<introduces-a-lookaround>\\t<pattern>"

`gen.tsv` carries the substituted patterns: one `P1` row (all occurrences
replaced at once), one `P2` row per substitutable occurrence (that
occurrence replaced, the rest left FOLDED — the mixed form), and one
`NONE` row (the control: no occurrence replaced, so the row's pattern IS
the original and every cell must come out trivially equal).

`<identical>` is `1` when the generated pattern is TEXTUALLY the original.
That is not an error and it is not hidden: `\\A` and `\\z` are PRIMITIVES in
§6.1 — the floor of the definition chain, with no lookaround to expand to
— so an occurrence-level substitution of one of them is the identity. The
driver counts those rows, asserts their number, and EXCLUDES them from the
"cells that compared two lowerings" headline, because a row that
substituted nothing proves nothing about the lookaround path.

Usage: expand_corpus.py <corpus-root> <outdir>
       (corpus-root is `tests/assertions`; its `d27/` subdirectory is
        included, matching the population design §6.3 measured.)
"""
import os
import re
import sys

# ===================================================================== #
# THE EXPANSION TABLE — design §6.1, TRANSCRIBED. NEVER DERIVED.
# ===================================================================== #
#
#   | construct   | expansion                              |
#   |-------------|----------------------------------------|
#   | \b          | (?:(?<=\w)(?!\w)|(?<!\w)(?=\w))        |
#   | \B          | (?:(?<=\w)(?=\w)|(?<!\w)(?!\w))        |
#   | (?m)^       | (?:\A|(?<=\n)(?!\z))                   |
#   | (?m)$       | (?:(?=\n)|\z)                          |
#   | \Z          | (?=\n?\z)                              |
#   | $  (default)| (?=\n?\z)      -- i.e. `$` IS `\Z`      |
#   | ^  (default)| \A                                     |
#   | \A, \z      | PRIMITIVES — the floor, no expansion   |
#   | \G          | NO EXPANSION: a primitive against startpos |
#   | \K          | NO EXPANSION: a match-START operator   |
#
# Measured at design time over 18 subjects x 6 tails with both arms
# carrying the same option state: 972 cells, 0 disagreements. The zeros
# are RESULTS and not assumptions — §6.1's vacuity guard shows a WRONG
# expansion (`\A|(?<=\n)`, the `(?!\z)` term dropped) disagreeing with
# `(?m)^` on 4 of 108 cells. `run_expansion_diff.sh` §0 re-runs both
# halves of that measurement, the agreeing one and the disagreeing one,
# before it trusts a single row below.
#
# TWO ROWS ARE STATE-DEPENDENT. `^` and `$` mean different things under
# `(?m)`, which is why Q4 exists: a textual driver may only substitute
# them where the multiline state is CONSTANT and knowable.

EXPANSION_FIXED = {
    "\\b": "(?:(?<=\\w)(?!\\w)|(?<!\\w)(?=\\w))",
    "\\B": "(?:(?<=\\w)(?=\\w)|(?<!\\w)(?!\\w))",
    "\\Z": "(?=\\n?\\z)",
    "\\A": None,          # PRIMITIVE (§6.1) — the identity substitution
    "\\z": None,          # PRIMITIVE (§6.1) — the identity substitution
}
EXPANSION_MULTILINE = {
    # token -> {multiline_state: expansion}
    "^": {False: "\\A", True: "(?:\\A|(?<=\\n)(?!\\z))"},
    "$": {False: "(?=\\n?\\z)", True: "(?:(?=\\n)|\\z)"},
}

# The tokens that HAVE a definition in §6.1's table, expansion or
# primitive. Q2 asks whether a block contains one of these.
SUBSTITUTABLE = ["\\b", "\\B", "\\A", "\\z", "\\Z", "^", "$"]
# The tokens §6.1's last two rows rule out: no lookaround definition
# exists for either, so a block whose only assertions are these cannot be
# substituted at all.
NO_DEFINITION = ["\\G", "\\K"]

# ===================================================================== #
# THE BRACKETING RULE (§6.3), CHECKED RATHER THAN ASSERTED
# ===================================================================== #
# "Every multi-branch expansion is wrapped `(?:...)` before insertion, so
#  `a\bc` becomes `a(?:(?<=\w)(?!\w)|(?<!\w)(?=\w))c` and not the
#  top-level-alternation pattern a naive splice produces. `(?:` is
#  NON-CAPTURING, so group numbers are unchanged and every `g`/`gp`
#  capture-slot expectation survives untouched."
#
# The table above is written already-bracketed, which is exactly the
# shape a transcription error can silently undo. So the rule is CHECKED
# here, by a parser, on every row of the table at import time: an
# expansion may not contain a `|` at nesting depth 0.


def top_level_alternation(s):
    """True if `s` contains a `|` outside every group and every class."""
    depth = 0
    incls = False
    clspos = 0
    expect_neg = False
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\":
            i += 2
            if incls:
                clspos += 1
                expect_neg = False
            continue
        if incls:
            if expect_neg and c == "^":
                expect_neg = False
                i += 1
                continue
            expect_neg = False
            if c == "]" and clspos > 0:
                incls = False
            clspos += 1
            i += 1
            continue
        if c == "[":
            incls = True
            clspos = 0
            expect_neg = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == "|" and depth == 0:
            return True
        i += 1
    return False


def check_table():
    """The bracketing rule, on the table itself. A FATAL, never a warning:
    an unbracketed multi-branch expansion spliced mid-pattern is a
    DIFFERENT PATTERN (the alternation escapes to top level), and every
    cell generated from it would be verified against the wrong thing."""
    rows = [(k, v) for k, v in EXPANSION_FIXED.items() if v is not None]
    for tok, per_state in EXPANSION_MULTILINE.items():
        for st, v in per_state.items():
            rows.append(("%s ml=%s" % (tok, st), v))
    for name, exp in rows:
        if top_level_alternation(exp):
            sys.stderr.write(
                "expand_corpus: FATAL: the expansion for %s has a TOP-LEVEL "
                "alternation (%r) — the bracketing rule (§6.3) is broken and "
                "every generated pattern would be a different pattern\n"
                % (name, exp))
            sys.exit(2)
    return len(rows)


# ===================================================================== #
# Q3's WALK — escape-aware and CLASS-aware, a parser and not a regex
# ===================================================================== #
# `[\b]` is the BACKSPACE byte and `[^a]` is a negation; substituting
# either produces a different pattern, not a rewritten one. The walk
# consumes ONE LITERAL `]` after `[` or `[^` (PCRE2's literal-first rule),
# so `[]\b]` is a class containing `]` and a backspace, NOT a class that
# closed immediately. A `sed`-based driver gets this wrong the first time
# a class contains one, and the backrefs lane's own `sed 's/\\1//'` defect
# is the precedent.

def occurrences(pat):
    """Every assertion occurrence in `pat`, as (token, index, in_class)."""
    out = []
    i, n = 0, len(pat)
    incls = False
    clspos = 0          # characters of CONTENT seen since `[` (or `[^`)
    expect_neg = False  # the very next char may be the negating `^`
    while i < n:
        c = pat[i]
        if c == "\\" and i + 1 < n:
            tok = pat[i:i + 2]
            if tok in SUBSTITUTABLE or tok in NO_DEFINITION:
                out.append((tok, i, incls))
            if incls:
                # An ESCAPE inside a class is CONTENT: without this,
                # `[\]]` leaves clspos at 0, the following `]` reads as
                # the literal-first `]`, the class never closes, and
                # every assertion after it is swallowed.
                clspos += 1
                expect_neg = False
            i += 2
            continue
        if incls:
            # `expect_neg` is true for exactly ONE character position,
            # which is what "the negating caret" means. Testing
            # `c == "^" and clspos == 0` instead fires for every
            # leading-position `^`, so `[^^]` consumes BOTH carets, the
            # `]` reads as literal-first, and `[^^]$` loses its `$`.
            if expect_neg and c == "^":
                expect_neg = False
                i += 1
                continue
            expect_neg = False
            if c == "]" and clspos > 0:
                incls = False
            clspos += 1
            i += 1
            continue
        if c == "[":
            incls = True
            clspos = 0
            expect_neg = True
            i += 1
            continue
        if c in ("^", "$"):
            out.append((c, i, False))
        i += 1
    return out


# ===================================================================== #
# Q4's RULE — A PARSER, NOT A SUBSTRING TEST
# ===================================================================== #
# `^` and `$` mean different things under different multiline states, so
# a textual driver must know the state at each occurrence. A BARE LEADING
# `(?m)` makes it constant and knowable; everything else does not — a
# scoped `(?im:...)`, a mid-pattern `(?-m)`, or a second `(?m)` after
# anything at all.
#
# The substring test `"(?m:" in pat` this replaced missed TWO families:
# multi-letter sets (`(?im:`, `(?xm:`, `(?i-m:`), which this corpus does
# not contain today, and — the half that was NOT inert — SEVEN NON-LEADING
# bare `(?m)` blocks, which it would have substituted under a single
# multiline assumption that is false for part of the pattern.

_MODLETTERS = "imnsxUJa"       # the letters src/parse/mod_modifiers.c accepts
_MODRE = re.compile(r"\(\?([a-zA-Z]*)(?:-([a-zA-Z]*))?([:\)])")


def modifier_groups(pat):
    """Every inline modifier group, as (start, on, off, terminator)."""
    out = []
    for m in _MODRE.finditer(pat):
        on, off, term = m.group(1) or "", m.group(2) or "", m.group(3)
        if not any(ch in _MODLETTERS for ch in on + off):
            continue                      # not a modifier group at all
        out.append((m.start(), on, off, term))
    return out


def is_bare_leading_m(start, on, off, term):
    return term == ")" and start == 0 and not off and on == "m"


def scoped_m_state(pat):
    """(varies, multiline_on).

    `varies` is True when `m` is turned on or off anywhere except by a
    bare leading `(?m)` — Q4's disqualification. When it is False,
    `multiline_on` is the pattern's single, constant multiline state and
    the `^`/`$` rows of the table can be resolved textually."""
    ml = False
    for (start, on, off, term) in modifier_groups(pat):
        touches_m = ("m" in on) or ("m" in off)
        if not touches_m:
            continue
        if is_bare_leading_m(start, on, off, term):
            ml = True
            continue
        return True, False
    return False, ml


# ===================================================================== #
# The `.rxt` reader, and the subject decoder tests/harness/verify_rxt.py
# uses. Kept here rather than imported: the harness's parser raises on
# constructs this generator wants to SKIP, and a generator that died on
# the corpus's own syntax would be a driver that silently shrank.
# ===================================================================== #

def decode_subject(s):
    out = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == "\\":
            if i + 1 >= n:
                raise ValueError("trailing backslash in subject")
            nc = s[i + 1]
            simple = {'"': '"', "\\": "\\", "n": "\n", "t": "\t",
                      "r": "\r", "f": "\f", "v": "\v"}
            if nc in simple:
                out.append(simple[nc])
                i += 2
            elif nc == "x":
                if i + 3 >= n:
                    raise ValueError("bad \\xHH escape")
                out.append(chr(int(s[i + 2:i + 4], 16)))
                i += 4
            else:
                raise ValueError("unknown subject escape \\%s" % nc)
        else:
            out.append(c)
            i += 1
    return "".join(out)


def parse_quoted(line):
    assert line[0] == '"'
    i, raw, n = 1, [], len(line)
    while i < n:
        c = line[i]
        if c == "\\":
            if i + 1 >= n:
                raise ValueError("trailing backslash before end of line")
            raw.append(line[i:i + 2])
            i += 2
        elif c == '"':
            return decode_subject("".join(raw)), line[i + 1:]
        else:
            raw.append(c)
            i += 1
    raise ValueError("unterminated quoted subject: " + line)


CELL_RE = re.compile(r"^(m|n|ms|ns) ")


def parse_cell(line):
    """-> (startpos, subject, expect) or None. `expect` is spelled the way
    tests/backrefs/bref_batch.c spells it, so the corpus's own answer can
    be compared to an artifact's output without a second convention."""
    kind = line.split(" ", 1)[0]
    rest = line[len(kind) + 1:].lstrip()
    sp = 0
    if kind in ("ms", "ns"):
        i = 0
        while i < len(rest) and rest[i].isdigit():
            i += 1
        if i == 0:
            raise ValueError("missing startpos: %r" % line)
        sp = int(rest[:i])
        rest = rest[i:].lstrip()
    if not rest.startswith('"'):
        raise ValueError("expected a quoted subject: %r" % line)
    subj, tail = parse_quoted(rest)
    if kind in ("n", "ns"):
        return sp, subj, "nomatch"
    parts = tail.split()
    if len(parts) < 2:
        raise ValueError("missing span: %r" % line)
    return sp, subj, "match %d %d" % (int(parts[0]), int(parts[1]))


def read_blocks(path):
    """[(pattern, dirs, cells, gcells, lead, lineno)] per file."""
    out = []
    cur = None
    lead = []
    for lineno, raw in enumerate(open(path, encoding="utf-8",
                                      errors="replace"), 1):
        line = raw.rstrip("\n")
        if line.startswith("pattern "):
            if cur:
                out.append(cur)
            cur = {"pattern": line[len("pattern "):], "dirs": [], "cells": [],
                   "gcells": [], "lead": lead, "lineno": lineno,
                   "feats": None, "flags": None}
            lead = []
            continue
        if cur is None:
            if line.startswith("#"):
                lead.append(line)
            continue
        if CELL_RE.match(line):
            cur["cells"].append(line)
        elif re.match(r"^(g|gp) ", line):
            cur["gcells"].append(line)
        elif line.startswith("features "):
            cur["feats"] = line[len("features "):].strip()
            cur["dirs"].append(line)
        elif line.startswith("flags "):
            cur["flags"] = line[len("flags "):].strip()
            cur["dirs"].append(line)
        elif line.startswith("perr"):
            cur["dirs"].append(line)
        elif line.startswith("#"):
            cur["dirs"].append(line)
    if cur:
        out.append(cur)
    return out


# ===================================================================== #
# THE SUBSTITUTION
# ===================================================================== #

def expansion_for(tok, ml):
    if tok in EXPANSION_FIXED:
        return EXPANSION_FIXED[tok]
    return EXPANSION_MULTILINE[tok][ml]


def introduces_lookaround(occs, ml, which):
    """True when at least one of the expansions this substitution inserts
    IS a lookaround.

    Computed from the TABLE and from the occurrences replaced, never by
    looking for `(?=` in the result: two of §6.1's rows expand an
    assertion to another PRIMITIVE (`^` under default flags is `\A`, and
    `\A`/`\z` are the floor and expand to themselves), and a source
    pattern may already contain a lookaround of its own — so a substring
    test on the OUTPUT answers a different question from "did this
    substitution put a lookaround there"."""
    for k in which:
        tok, _idx, _c = occs[k]
        exp = expansion_for(tok, ml)
        if exp is None:
            continue
        if "(?=" in exp or "(?!" in exp or "(?<" in exp:
            return True
    return False


def substitute(pat, occs, ml, which):
    """Replace the occurrences named by `which` (a set of indices into
    `occs`). Right to left, so earlier indices stay valid."""
    out = pat
    for k in sorted(which, reverse=True):
        tok, idx, _ = occs[k]
        exp = expansion_for(tok, ml)
        if exp is None:            # a PRIMITIVE: the identity substitution
            continue
        out = out[:idx] + exp + out[idx + len(tok):]
    return out


# ===================================================================== #
# MAIN
# ===================================================================== #

def main():
    if len(sys.argv) != 3:
        sys.stderr.write("usage: expand_corpus.py <corpus-root> <outdir>\n")
        return 2
    root, outdir = sys.argv[1], sys.argv[2]
    ntable = check_table()

    dirs = [root, os.path.join(root, "d27")]
    files = []
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith(".rxt"):
                files.append(os.path.join(d, f))
    if not files:
        sys.stderr.write("expand_corpus: FATAL: no .rxt files under %s — the "
                         "corpus this driver substitutes FROM is missing, and "
                         "a run over zero blocks is a FAILURE, never a pass\n"
                         % root)
        return 2

    REJ = {
        "Q1 perr / no behavioural cell": [0, 0],
        "Q2 no substitutable assertion": [0, 0],
        "Q3 assertion inside a character class": [0, 0],
        "Q4 modifier state not constant": [0, 0],
        "Q5 \\K inside a substituted body": [0, 0],
        "Q6 block marked # pcre2-deviates (D68)": [0, 0],
    }
    tot = {"blocks": 0, "beh": 0, "g": 0}
    qual = {"blocks": 0, "beh": 0, "g": 0}
    per_token = {}
    per_file = {}
    n_p1 = n_p2 = 0
    n_p1_id = n_p2_id = 0
    n_p1_look = n_p2_look = 0
    ml_blocks = 0

    os.makedirs(outdir, exist_ok=True)
    blocks_index = []
    bid = 0

    for path in files:
        rel = os.path.relpath(path, os.path.dirname(os.path.dirname(root)))
        per_file.setdefault(rel, [0, 0, 0, 0])
        for b in read_blocks(path):
            pat = b["pattern"]
            beh = b["cells"]
            tot["blocks"] += 1
            tot["beh"] += len(beh)
            tot["g"] += len(b["gcells"])
            per_file[rel][0] += 1
            per_file[rel][2] += len(beh)

            is_perr = any(d.startswith("perr") for d in b["dirs"])
            occs = occurrences(pat)
            subs = [o for o in occs if o[0] in SUBSTITUTABLE]
            in_class = [o for o in subs if o[2]]
            varies, ml = scoped_m_state(pat)
            deviates = any(l.startswith("# pcre2-deviates")
                           for l in b["dirs"] + b["lead"])

            why = None
            if is_perr or not beh:
                why = "Q1 perr / no behavioural cell"
            elif not subs:
                why = "Q2 no substitutable assertion"
            elif in_class:
                why = "Q3 assertion inside a character class"
            elif varies:
                why = "Q4 modifier state not constant"
            elif deviates:
                why = "Q6 block marked # pcre2-deviates (D68)"
            else:
                # Q5 — `\K` must not land INSIDE a substituted body, since
                # PCRE2 refuses it there (err 199). It cannot, given the
                # bracketing rule: an expansion is inserted text and spans
                # none of the original. Counted anyway, so the claim is a
                # number rather than an argument.
                ks = [o for o in occs if o[0] == "\\K"]
                bad_k = False
                for (tok, idx, _c) in subs:
                    for (_kt, kidx, _kc) in ks:
                        if idx < kidx < idx + len(tok):
                            bad_k = True
                if bad_k:
                    why = "Q5 \\K inside a substituted body"
            if why:
                REJ[why][0] += 1
                REJ[why][1] += len(beh)
                continue

            qual["blocks"] += 1
            qual["beh"] += len(beh)
            qual["g"] += len(b["gcells"])
            per_file[rel][1] += 1
            per_file[rel][3] += len(beh)
            if ml:
                ml_blocks += 1
            for tok, _i, _c in subs:
                per_token[tok] = per_token.get(tok, 0) + 1

            # ---- write the block's work item ------------------------
            bid += 1
            name = "b%04d" % bid
            bdir = os.path.join(outdir, name)
            os.makedirs(os.path.join(bdir, "subjects"), exist_ok=True)
            with open(os.path.join(bdir, "pattern"), "w") as f:
                f.write(pat + "\n")
            # A block with no `features` line compiles under pcrec's
            # DEFAULT set, which is the frozen named set `std1` = {classes,
            # modifiers} (D37). It is spelled out here rather than passed
            # as the name `std1`, because `--features` takes a named set
            # ALONE and refuses it inside a comma list — and this driver
            # always has two modules to add.
            feats = b["feats"] or "classes,modifiers"
            if feats == "none":
                # `features none` gates every module off; the expanded
                # pattern needs `lookaround`, so the two arms could not
                # share a feature set. No qualifying block has it today
                # and the generator says so rather than guessing.
                sys.stderr.write("expand_corpus: FATAL: qualifying block %s:%d "
                                 "carries `features none`, so its two arms "
                                 "cannot share one feature set\n"
                                 % (rel, b["lineno"]))
                return 2
            # BOTH ARMS COMPILE WITH ONE FEATURE SET, and it is the block's
            # own plus the three modules the EXPANSIONS need: `lookaround`
            # for the assertions themselves, `classes` for the `\w` in
            # `\b`/`\B`'s bodies, and `assertions` for the `\z`/`\A`
            # INSIDE the expansions (`$` expands to `(?=\n?\z)`, so a
            # block that needed no module at all needs one after
            # substitution). Giving arm A a wider set than arm B would make
            # the feature list a SECOND difference between the two
            # lowerings, and then a disagreement could not be attributed to
            # the substitution — so the widening is applied to both.
            want = [x for x in feats.split(",") if x]
            for extra in ("lookaround", "classes", "assertions"):
                if extra not in want:
                    want.append(extra)
            feats = ",".join(want)
            with open(os.path.join(bdir, "feats"), "w") as f:
                f.write(feats + "\n")
            with open(os.path.join(bdir, "origin"), "w") as f:
                f.write("%s:%d\n" % (rel, b["lineno"]))

            subj_ids = {}
            cells, expects = [], []
            for line in beh:
                sp, subj, exp = parse_cell(line)
                if subj not in subj_ids:
                    sid = "s%03d" % len(subj_ids)
                    subj_ids[subj] = sid
                    with open(os.path.join(bdir, "subjects", sid), "wb") as f:
                        f.write(subj.encode("latin-1"))
                cells.append("%s\t%d" % (os.path.join(bdir, "subjects",
                                                      subj_ids[subj]), sp))
                expects.append(exp)
            with open(os.path.join(bdir, "cells"), "w") as f:
                f.write("".join(c + "\n" for c in cells))
            with open(os.path.join(bdir, "expect"), "w") as f:
                f.write("".join(e + "\n" for e in expects))

            rows = []
            # P1 ALL-AT-ONCE. A half-substituted pattern tests neither
            # form, so this is the baseline policy.
            allk = set(range(len(subs)))
            p1 = substitute(pat, subs, ml, allk)
            p1look = introduces_lookaround(subs, ml, allk)
            rows.append(("%s.P1" % name, "P1", p1, p1look))
            n_p1 += 1
            if p1 == pat:
                n_p1_id += 1
            if p1look:
                n_p1_look += 1
            # P2 ONE-AT-A-TIME — the MIXED form, where a folded assertion
            # and an expanded one must agree INSIDE ONE PATTERN.
            for k in range(len(subs)):
                p2 = substitute(pat, subs, ml, {k})
                p2look = introduces_lookaround(subs, ml, {k})
                rows.append(("%s.P2.%d" % (name, k), "P2", p2, p2look))
                n_p2 += 1
                if p2 == pat:
                    n_p2_id += 1
                if p2look:
                    n_p2_look += 1
            # NONE — the CONTROL. Same pipeline, no substitution, so every
            # cell must come out trivially equal. Without it `A == B` is
            # not known to be comparing two lowerings at all.
            rows.append(("%s.NONE" % name, "NONE", pat, False))

            with open(os.path.join(bdir, "gen.tsv"), "w") as f:
                for gid, pol, gp, hl in rows:
                    f.write("%s\t%s\t%d\t%d\t%s\n"
                            % (gid, pol, 1 if gp == pat else 0,
                               1 if hl else 0, gp))
            blocks_index.append(name)

    with open(os.path.join(outdir, "blocks"), "w") as f:
        f.write("".join(n + "\n" for n in blocks_index))

    counts = [
        ("table_rows", ntable),
        ("tot_blocks", tot["blocks"]), ("tot_beh", tot["beh"]),
        ("tot_g", tot["g"]),
        ("qual_blocks", qual["blocks"]), ("qual_beh", qual["beh"]),
        ("qual_g", qual["g"]),
        ("q1_blocks", REJ["Q1 perr / no behavioural cell"][0]),
        ("q1_cells", REJ["Q1 perr / no behavioural cell"][1]),
        ("q2_blocks", REJ["Q2 no substitutable assertion"][0]),
        ("q2_cells", REJ["Q2 no substitutable assertion"][1]),
        ("q3_blocks", REJ["Q3 assertion inside a character class"][0]),
        ("q3_cells", REJ["Q3 assertion inside a character class"][1]),
        ("q4_blocks", REJ["Q4 modifier state not constant"][0]),
        ("q4_cells", REJ["Q4 modifier state not constant"][1]),
        ("q5_blocks", REJ["Q5 \\K inside a substituted body"][0]),
        ("q5_cells", REJ["Q5 \\K inside a substituted body"][1]),
        ("q6_blocks", REJ["Q6 block marked # pcre2-deviates (D68)"][0]),
        ("q6_cells", REJ["Q6 block marked # pcre2-deviates (D68)"][1]),
        ("p1_patterns", n_p1), ("p2_patterns", n_p2),
        ("p1_identity", n_p1_id), ("p2_identity", n_p2_id),
        ("p1_lookaround", n_p1_look), ("p2_lookaround", n_p2_look),
        ("multiline_blocks", ml_blocks),
    ]
    for tok in SUBSTITUTABLE:
        counts.append(("occ_" + tok.replace("\\", "bs_")
                       .replace("^", "caret").replace("$", "dollar"),
                       per_token.get(tok, 0)))
    with open(os.path.join(outdir, "counts.tsv"), "w") as f:
        for k, v in counts:
            f.write("%s\t%d\n" % (k, v))

    lines = []
    W = lines.append
    W("=" * 74)
    W("THE SUBSTITUTION POPULATION (design §6.3), re-counted on HEAD")
    W("=" * 74)
    W("  corpus root : %s" % root)
    W("  files       : %d" % len(files))
    W("  expansion table rows checked for the bracketing rule : %d" % ntable)
    W("")
    W("  blocks (pattern lines)          : %d" % tot["blocks"])
    W("  BEHAVIOURAL cells (m/n/ms/ns)   : %d" % tot["beh"])
    W("  capture-slot cells (g/gp)       : %d" % tot["g"])
    W("")
    W("  QUALIFYING blocks               : %d of %d" % (qual["blocks"],
                                                        tot["blocks"]))
    W("  QUALIFYING behavioural cells    : %d of %d" % (qual["beh"],
                                                        tot["beh"]))
    W("  ... carrying capture-slot cells : %d" % qual["g"])
    W("  ... under a bare leading (?m)   : %d" % ml_blocks)
    W("")
    W("  DISQUALIFIED, by rule:")
    for k in sorted(REJ):
        W("    %-40s %4d blocks  %5d cells" % (k, REJ[k][0], REJ[k][1]))
    W("")
    W("  Substitutable occurrences in qualifying blocks, by token:")
    for k in sorted(per_token, key=lambda x: -per_token[x]):
        prim = "  (PRIMITIVE — the identity substitution)" \
            if EXPANSION_FIXED.get(k, "x") is None else ""
        W("    %-4s %d%s" % (k, per_token[k], prim))
    W("")
    W("  GENERATED PATTERNS:")
    W("    P1 all-at-once   : %d  (%d identical to source, %d INSERT a lookaround)"
      % (n_p1, n_p1_id, n_p1_look))
    W("    P2 one-at-a-time : %d  (%d identical to source, %d INSERT a lookaround)"
      % (n_p2, n_p2_id, n_p2_look))
    W("    NONE control     : %d  (identical to source BY CONSTRUCTION)"
      % qual["blocks"])
    W("")
    W("  THE IDENTITY ROWS ARE NOT A DEFECT AND NOT HIDDEN. `\\A` and `\\z`")
    W("  are PRIMITIVES in §6.1 — the floor of the definition chain — so an")
    W("  occurrence-level substitution of one of them IS the identity. The")
    W("  driver asserts their number and excludes them from the headline")
    W("  'cells that compared two lowerings', because a row that substituted")
    W("  nothing proves nothing about the lookaround path.")
    report = "\n".join(lines) + "\n"
    with open(os.path.join(outdir, "report.txt"), "w") as f:
        f.write(report)
    sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
