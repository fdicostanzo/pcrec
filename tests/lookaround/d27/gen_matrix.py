#!/usr/bin/env python3
"""gen_matrix.py -- the systematic CONSTRUCT x BODY-SHAPE x CONTEXT matrix,
per la_d27_extract.md sec 10.1's population table:
  6 distinct constructs x 9 body shapes x 7 contexts.

For each cell this script builds a pattern from templates, runs it through
BOTH oracles (la_oracle's libpcre2 10.46 binding, python3 `re`), mines a
small set of DISCRIMINATING subjects from a short brute-force search over a
tiny alphabet (rather than hand-guessing subjects -- every subject's
expectation is the oracle's own answer, and the mining step is what makes
the corpus adversarial: it prefers subjects where match/no-match or capture
outcomes actually distinguish behaviour, e.g. it will not settle for "always
matches at 0..0" when a subject producing a real span exists).

Divergence handling per la_d27_extract.md sec 7:
  - G4/G5: the alpha spellings and non-atomic forms do not exist in python
    at all -- handled by gen_spellings.py, not here (this file only uses
    the canonical `(?...)` spellings for the 6 constructs).
  - G1/G2/G3: lookbehind width-rule divergences -- this file's lookbehind
    cells route non-fixed-per-branch body shapes to a `perr` cell instead
    of a match cell (pcrec refuses; PCRE2 in many of those cases still
    accepts, which is exactly G2, and is marked `# pcre2-only` on the one
    comment line explaining why since python's error is a DIFFERENT rule
    -- see G10).
  - G7: `\\A`/`\\Z`/`\\z` inside lookaround bodies -- avoided in this file
    entirely (the assertion-family expansions file handles \\Z/\\z on
    purpose, matching G7's own probe).
"""
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import Block, RxtFile, pcre2_search, py_search, pcre2_ok, py_ok

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "matrix.rxt")

# ---------------------------------------------------------------------------
# The six constructs, canonical `(?...)` spelling only (the 18-spelling
# equivalence check lives in gen_spellings.py).
# ---------------------------------------------------------------------------
CONSTRUCTS = [
    # name, open, close, is_lookbehind, is_negative, needs_features
    ("PLA",   "(?=",  ")", False, False, "lookaround"),
    ("NLA",   "(?!",  ")", False, True,  "lookaround"),
    ("PLB",   "(?<=", ")", True,  False, "lookaround"),
    ("NLB",   "(?<!", ")", True,  True,  "lookaround"),
    ("NAPLA", "(?*",  ")", False, False, "lookaround"),
    ("NAPLB", "(?<*", ")", True,  False, "lookaround"),
]

# ---------------------------------------------------------------------------
# Body shapes. Each entry is (name, kind, builder(construct)->X_or_None).
# `kind` drives width-rule handling for lookbehind constructs:
#   "fixed"        -- always a fixed width, ships under every construct
#   "variable"     -- variable width; under a lookbehind construct this is
#                     a REFUSAL cell (pcrec) though PCRE2/python may accept
#                     or reject on their own separate grounds
#   "diffwidth"    -- alternation of DIFFERENT fixed widths per branch:
#                     ships under lookbehind (the sec 2.5 headline cell)
# ---------------------------------------------------------------------------
def body_shapes():
    return [
        ("empty",       "fixed",    lambda c: ""),
        ("literal",     "fixed",    lambda c: "a"),
        ("class",       "fixed",    lambda c: "[ab]"),
        ("fixedmulti",  "fixed",    lambda c: "abc"),
        ("samelen_alt", "fixed",    lambda c: "ab|cd"),
        ("diffwidth",   "diffwidth", lambda c: "a|bc"),
        ("capture",     "fixed",    lambda c: "(a)"),
        # matches la_d27_extract.md sec 2.5's own example row verbatim
        # ("(?<=a(?!b))x -- ship: nested lookaround contributes 0 width").
        ("nested_la",   "fixed",    lambda c: "a(?!b)"),
        ("backref",     "variable", lambda c: "\\1"),   # needs prefix "(a)"
    ]

CONTEXTS = ["start", "end", "mid", "branch", "quant_star", "capture", "atomic"]


def build_pattern(construct, la_token, ctx, needs_backref_prefix):
    """Wrap la_token (the full open+X+close lookaround) per context. Returns
    (pattern, features_needed_beyond_lookaround)."""
    extra_feat = set()
    prefix = "(a)" if needs_backref_prefix else ""
    if ctx == "start":
        pat = prefix + la_token + "z"
    elif ctx == "end":
        pat = prefix + "z" + la_token
    elif ctx == "mid":
        pat = prefix + "y" + la_token + "z"
    elif ctx == "branch":
        pat = prefix + "(?:" + la_token + "z|w)"
    elif ctx == "quant_star":
        pat = prefix + la_token + "*z"
    elif ctx == "capture":
        pat = prefix + "(" + la_token + "z)"
    elif ctx == "atomic":
        pat = prefix + "(?>" + la_token + "z)"
        extra_feat.add("atomic-groups")
    else:
        raise ValueError(ctx)
    return pat, extra_feat


# Small alphabet for subject mining. Kept tiny and shared across every cell
# so mined subjects stay short and legible.
ALPHA = "abcdwyz"


def candidate_subjects(maxlen=6):
    seen = set()
    subs = []
    for n in range(0, maxlen + 1):
        for tup in itertools.product(ALPHA, repeat=n):
            s = "".join(tup)
            if s not in seen:
                seen.add(s)
                subs.append(s)
    return subs


# A fixed, deterministically-ordered candidate pool. n up to 4 keeps the
# brute force fast (7^0+7^1+...+7^4 ~= 2800) while still reaching every
# 2-3 character shape this matrix's patterns care about; longer subjects
# are added ad hoc per cell where a template needs them (quant_star wants
# a repeated hit, branch wants both arms exercised).
POOL = candidate_subjects(4)


def mine_subjects(pat, want=3, startpos=0, extra_pool=()):
    """Pick up to `want` subjects from POOL (+ extra_pool) that are
    DISCRIMINATING for `pat` under the libpcre2 oracle: prefer a mix of
    real matches (start!=end when possible) and no-matches, dedup by
    outcome shape so we do not return three subjects that all say the same
    thing. Returns list of (subject, pcre2_result)."""
    results = []
    matches, nomatches = [], []
    for s in list(extra_pool) + POOL:
        r = pcre2_search(pat, s, startpos)
        if r == "ERR":
            continue
        if r is None:
            nomatches.append((s, r))
        else:
            matches.append((s, r))
    # Prefer variety: try to get at least one match and one no-match, plus
    # one more match with a DIFFERENT span/groups shape than the first if
    # available (that is what actually exercises capture-slot correctness
    # under quantified/branch contexts).
    out = []
    if matches:
        out.append(matches[0])
        for m in matches[1:]:
            if len(out) >= want:
                break
            if m[1] != out[0][1]:
                out.append(m)
    if nomatches and len(out) < want:
        out.append(nomatches[0])
    # top up
    for pool in (matches, nomatches):
        for cand in pool:
            if len(out) >= want:
                break
            if cand not in out:
                out.append(cand)
    return out[:want]


def emit_cell(rf, construct, shape_name, shape_kind, x_builder, ctx):
    cname, copen, cclose, is_lb, is_neg, base_feat = construct
    needs_backref = (shape_name == "backref")
    x = x_builder(construct)
    if needs_backref and x is None:
        return
    la_token = copen + x + cclose
    pat, extra_feat = build_pattern(construct, la_token, ctx, needs_backref)
    feats = set([base_feat]) | extra_feat
    if needs_backref:
        feats.add("backrefs")
    feat_str = ",".join(sorted(feats))

    refuse = is_lb and shape_kind == "variable"
    label = "%s/%s/%s: %s" % (cname, shape_name, ctx, pat)

    if refuse:
        # This is a pcrec-side capability refusal (sec 2.5). Existence
        # checked against the prebuilt pcrec binary at authoring time (see
        # gen_matrix.py's own probe log); PCRE2 itself may well ACCEPT this
        # body (G2) -- that fact belongs in refusals.rxt's divergence
        # commentary, not asserted incorrectly here as a shared oracle
        # refusal. matrix.rxt does not carry perr cells at all -- routed to
        # refusals.rxt's systematic sibling instead, so skip here.
        return

    pcre2_okay = pcre2_ok(pat)
    if not pcre2_okay:
        # Should not happen for any "fixed"/"diffwidth" shape cell; if it
        # does, surface loudly rather than silently drop coverage.
        raise AssertionError("unexpected PCRE2 refusal for %r: %s" %
                              (pat, common.la.compile_err(pat)))

    py_okay = py_ok(pat)
    pcre2_only = not py_okay

    extra_pool = []
    if ctx == "quant_star":
        extra_pool += ["z", "aaz", "abcz", "ababz", "zzz"]
    if ctx == "branch":
        extra_pool += ["zz", "waz", "wz"]
    if shape_name == "backref":
        extra_pool += ["aaz", "abz", "aaaz"]

    startpos = 0
    subj_start = 0
    picks = mine_subjects(pat, want=3, startpos=startpos, extra_pool=extra_pool)
    # Also mine one ms/ns (non-zero startpos) cell whenever this is a
    # lookbehind construct -- sec 10.1 population requirement 2 ("the
    # corpus MUST contain ms/ns startpos cells over a lookbehind").
    ms_pick = None
    if is_lb:
        # Build a longer subject with a prefix before the intended start,
        # so startpos > 0 and the lookbehind body must read bytes strictly
        # before startpos to succeed -- the exact shape sec 3.8's contract
        # claim needs.
        for prefix_len in (1, 2, 3):
            for base_s, base_r in picks:
                s2 = ("q" * prefix_len) + base_s
                p2 = prefix_len
                r2 = pcre2_search(pat, s2, p2)
                if r2 is not None and r2 != "ERR":
                    ms_pick = (s2, p2, r2)
                    break
            if ms_pick:
                break
        if ms_pick is None:
            # fall back: mine directly for a startpos hit
            for s in POOL:
                for p2 in (1, 2):
                    s2 = "q" * p2 + s
                    r2 = pcre2_search(pat, s2, p2)
                    if r2 is not None and r2 != "ERR":
                        ms_pick = (s2, p2, r2)
                        break
                if ms_pick:
                    break

    if not picks and ms_pick is None:
        return  # nothing discriminating found (rare/degenerate cell)

    b = Block(pat, feat_str)
    for s, r in picks:
        if r is None:
            b.n(s)
        else:
            span, groups = r
            b.m(s, span[0], span[1])
            for i, g in enumerate(groups, start=1):
                if g is None:
                    b.gunset(i)
                else:
                    b.g(i, g[0], g[1])
    if ms_pick is not None:
        s2, p2, r2 = ms_pick
        if r2 is None:
            b.ns(p2, s2)
        else:
            span, groups = r2
            b.ms(p2, s2, span[0], span[1])
            for i, g in enumerate(groups, start=1):
                if g is None:
                    b.gunset(i)
                else:
                    b.g(i, g[0], g[1])

    rf.add(b, comment=label, pcre2_only=pcre2_only)


def main():
    rf = RxtFile(OUT)
    shapes = body_shapes()
    n_cells = 0
    for construct in CONSTRUCTS:
        for shape_name, shape_kind, x_builder in shapes:
            for ctx in CONTEXTS:
                before = rf.block_count()
                emit_cell(rf, construct, shape_name, shape_kind, x_builder, ctx)
                if rf.block_count() > before:
                    n_cells += 1
    header = (
        "# matrix.rxt -- [M6.6.3] D27 systematic construct x body-shape x\n"
        "# context matrix (la_d27_extract.md sec 10.1). 6 constructs x 9 body\n"
        "# shapes x 7 contexts, canonical `(?...)` spellings; alpha-spelling\n"
        "# equivalence lives in spellings.rxt, lookbehind-refusal cells for\n"
        "# variable-width bodies live in refusals.rxt (this file skips those\n"
        "# combinations rather than asserting a match expectation pcrec would\n"
        "# never produce). Every m/n/ms/ns/g expectation is a direct oracle\n"
        "# read from docs/design/lookaround_measurements/probes/la_oracle.py\n"
        "# (libpcre2 10.46) and, where python re can take the pattern, python3\n"
        "# `re` too -- generated by gen_matrix.py, never hand-typed.\n"
    )
    rf.write(header)
    print("matrix.rxt: %d blocks, %d cells, pcre2-only=%d python-verified=%d"
          % (rf.block_count(), rf.cell_count(), rf.pcre2only_count,
             rf.python_count))


if __name__ == "__main__":
    main()
