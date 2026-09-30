#!/usr/bin/env python3
"""lac_engine.py -- shared machinery for the [CTX-PREFILTER] and [ENG-LOOK]
step-0 censuses (lane lacens2, 2026-09-29). BYTE ENCODING ONLY (the k=2-4
population this backs is 98/98 byte, 0 caseless -- confirmed against
shapes_9399d927.tsv before writing this; a caller compiling a utf8-encoded
or caseless pattern through here gets an approximate byteset, flagged, not
a refusal).

Three independent pieces, used by both drivers:

1. ERASURE -- given a pattern's raw bytes and shape_classify.py's own
   occurrence list (offset + body + kind, the same objects
   lookaround_census.md's own S1 method produces), locate each
   occurrence's FULL construct span (the classifier records the body span
   but not the closing paren, since it never needed to) and cut it from
   the text, to build a "lookaround-erased" pattern pcrec can compile as a
   plain DFA baseline.

2. ATOM/BODY PARSING -- an independent, deliberately small recursive
   descent parser over a lookaround BODY's raw bytes, resolving each atom
   (literal char, `.`, a bracket class, a shorthand escape `\\d` etc., or a
   `(?:...)` group with an exact `{n}` quantifier) to a Python
   `frozenset` of byte values 0-255, with a `min_count` telling the
   first/last-atom walk whether the atom can be skipped (0) or is
   mandatory (>=1). Does NOT support: UTF-8 multi-byte atoms, caseless
   folding, POSIX bracket names, Unicode properties, `\\Q..\\E`, ranged
   (non-exact) quantifiers on a body used for the FIXED-WIDTH (ENG-LOOK)
   path -- these fall back to UNRESOLVED (the whole byte alphabet, 0-255),
   flagged, never silently wrong.

3. SMALL DFA CONSTRUCTION -- a from-scratch NFA-then-subset-construction
   builder (Thompson-style: a start state with a self-loop over all 256
   bytes for the "Sigma*" prefix, one linear chain per branch, subset
   construction over raw bytes) for a fixed-width body's "ends-with-L"
   recognizer, plus a byte-exact PRODUCT walk (BFS over live reachable
   pairs) against a DFA table extracted from pcrec's own generated C
   (parse_pcrec_tables below) -- REAL states from a REAL compile, not a
   model, on both sides of the product.

Kept deliberately independent of shape_classify.py's own atom-width
counting (S1's own "not derived from pcrec's AST" discipline, applied a
second time here): this module never asks shape_classify.py what an
atom's BYTES are, only reuses its OCCURRENCE LOCATION (offset, body,
kind) -- the byte-resolution is this module's own, separately checkable.
"""
import re

# ---------------------------------------------------------------------
# 1. ERASURE
# ---------------------------------------------------------------------

_ALPHA_LOOK_RE = re.compile(
    rb"\(\*(pla|nla|plb|nlb|napla|naplb|positive_lookahead|negative_lookahead|"
    rb"positive_lookbehind|negative_lookbehind|"
    rb"non_atomic_positive_look(?:ahead|behind)):"
)


def construct_span(data, offset):
    """Given the pattern bytes and an occurrence's `offset` (index of its
    opening '('), returns (start, end) covering the WHOLE construct
    (`(?...)` through its matching close paren, inclusive) -- the same
    balanced-paren walk shape_classify.py's own _group() does internally,
    replicated here because the occurrence dict does not carry it (S1
    only ever needed the body span)."""
    n = len(data)
    ma = _ALPHA_LOOK_RE.match(data[offset:])
    if ma:
        j = offset + ma.end()
    else:
        behind = (offset + 2 < n and data[offset + 2] == ord('<')
                  and offset + 3 < n and data[offset + 3] in b"=!*")
        j = offset + (4 if behind else 3)
    depth = 1
    k = j
    while k < n and depth:
        if data[k] == 0x5C:
            k += 2
            continue
        if data[k] == ord('['):
            k = _skip_class(data, k)
            continue
        if data[k] == ord('('):
            depth += 1
        elif data[k] == ord(')'):
            depth -= 1
            if depth == 0:
                break
        k += 1
    close = min(k, n)
    end = min(close + 1, n)
    return offset, _skip_trailing_quant(data, end)


def _skip_trailing_quant(data, i):
    """A lookaround construct itself may carry a trailing quantifier
    (`(?<=abc)*z` -- meaningless semantically, since an assertion is
    zero-width, but `tests/lookaround/d27/matrix.rxt` exercises the
    spelling as a boundary case). Erasure must consume it too, or the
    cut leaves a DANGLING quantifier with nothing before it (found live:
    erasing just the parens left `*z`, refused by pcrec as "quantifier
    does not follow a repeatable item" -- 12 of this census's original
    98 candidates, all from matrix.rxt). Mirrors shape_classify.py's
    own _quant() enough to find the END index; does not need the
    min/max it also computes."""
    n = len(data)
    if i >= n:
        return i
    c = data[i]

    def lazy_possessive(j):
        return j + 1 if j < n and data[j] in b"?+" else j

    if c in b"?*+":
        return lazy_possessive(i + 1)
    if c == ord('{'):
        m = re.match(rb"\{(\d*)(,?)(\d*)\}", data[i:])
        if m and (m.group(1) or m.group(3)):
            return lazy_possessive(i + m.end())
    return i


def _skip_class(data, i):
    n = len(data)
    j = i + 1
    if j < n and data[j] == 0x5E:
        j += 1
    if j < n and data[j] == ord(']'):
        j += 1
    while j < n:
        c = data[j]
        if c == 0x5C:
            j += 2
            continue
        if c == ord(']'):
            return j + 1
        j += 1
    return n


def erase_occurrences(data, occs):
    """Removes every occurrence's full construct span from `data`, offsets
    resolved against the ORIGINAL text (deletions applied outside-in by
    sorting spans in reverse offset order, since occurrence offsets never
    move as later ones are cut). Returns the erased bytes."""
    spans = sorted((construct_span(data, o['offset']) for o in occs),
                   key=lambda s: -s[0])
    out = bytearray(data)
    for start, end in spans:
        del out[start:end]
    return bytes(out)


# ---------------------------------------------------------------------
# 2. ATOM / BODY PARSING -> branches of (byteset, min_count, exact_count)
# ---------------------------------------------------------------------

ALL_BYTES = frozenset(range(256))
UNRESOLVED = None  # sentinel: caller must treat as ALL_BYTES and flag it

_SHORTHAND = {
    ord('d'): frozenset(range(0x30, 0x3A)),
    ord('h'): frozenset({0x09, 0x20}),
    ord('s'): frozenset({0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x20}),
    ord('v'): frozenset({0x0A, 0x0B, 0x0C, 0x0D, 0x85}),
    ord('w'): frozenset(range(0x30, 0x3A)) | frozenset(range(0x41, 0x5B))
              | frozenset(range(0x61, 0x7B)) | frozenset({0x5F}),
}


def _shorthand_set(c):
    lc = c | 0x20  # lowercase
    base = _SHORTHAND.get(lc)
    if base is None:
        return None
    return base if chr(c).islower() else (ALL_BYTES - base)


class Unresolvable(Exception):
    pass


def _parse_class(data, i):
    """i at '['. Returns (byteset, next_i)."""
    n = len(data)
    j = i + 1
    neg = False
    if j < n and data[j] == 0x5E:
        neg = True
        j += 1
    members = set()
    first = True
    while j < n:
        c = data[j]
        if c == ord(']') and not first:
            j += 1
            break
        first = False
        if c == 0x5C and j + 1 < n:
            e = data[j + 1]
            sh = _shorthand_set(e)
            if sh is not None:
                members |= sh
                j += 2
                continue
            lit = _escape_literal(data, j)
            if lit is None:
                raise Unresolvable("class escape")
            b, j = lit
            c = b
        else:
            j += 1
        # range?
        if j + 1 < n and data[j] == ord('-') and data[j + 1] != ord(']'):
            j += 1
            if data[j] == 0x5C:
                lit = _escape_literal(data, j)
                if lit is None:
                    raise Unresolvable("class range escape")
                hi, j = lit
            else:
                hi = data[j]
                j += 1
            if hi < c:
                raise Unresolvable("bad range")
            members |= set(range(c, hi + 1))
        else:
            members.add(c)
    else:
        raise Unresolvable("unterminated class")
    bs = frozenset(members)
    return (ALL_BYTES - bs if neg else bs), j


_ESCAPE_CHARS = {ord('n'): 0x0A, ord('t'): 0x09, ord('r'): 0x0D,
                 ord('f'): 0x0C, ord('a'): 0x07, ord('e'): 0x1B}


def _escape_literal(data, i):
    """i at the backslash. Returns (byte_value, next_i) for a LITERAL
    single-byte escape, or None if it's a shorthand/unsupported escape
    (\\Q..\\E, \\x{...}, \\p{...}, backrefs -- none expected in this
    population's bodies, since those all carry a capture/backref/nested
    look and would already be shape 'e', out of scope)."""
    n = len(data)
    if i + 1 >= n:
        return None
    e = data[i + 1]
    if e in _ESCAPE_CHARS:
        return _ESCAPE_CHARS[e], i + 2
    if e == ord('x'):
        if i + 2 < n and data[i + 2] == ord('{'):
            return None
        hexpart = data[i + 2:i + 4]
        try:
            return int(hexpart, 16), i + 4
        except ValueError:
            return None
    if chr(e).isalnum():
        return None  # an unhandled shorthand/backref-ish escape
    return e, i + 2  # escaped punctuation: literal


def _parse_atom(data, i, end):
    """Returns (byteset_or_UNRESOLVED, next_i, is_group_flag,
    group_branches_or_None). A plain atom's byteset may be UNRESOLVED."""
    c = data[i]
    if c == ord('('):
        # only "(?:" non-capturing groups are handled (the one case in
        # this population, `(?<=(?:ab){2})x`); anything else unresolved.
        if not (i + 2 < end and data[i + 1] == ord('?') and data[i + 2] == ord(':')):
            raise Unresolvable("unsupported group")
        depth = 1
        j = i + 3
        while j < end and depth:
            if data[j] == 0x5C:
                j += 2
                continue
            if data[j] == ord('['):
                j = _skip_class(data, j)
                continue
            if data[j] == ord('('):
                depth += 1
            elif data[j] == ord(')'):
                depth -= 1
            j += 1
        inner_end = j - 1
        branches = parse_alt(data, i + 3, inner_end)
        return None, j, True, branches
    if c == ord('['):
        bs, j = _parse_class(data, i)
        return bs, j, False, None
    if c == ord('.'):
        return (ALL_BYTES - {0x0A}), i + 1, False, None
    if c == 0x5C:
        if i + 1 >= end:
            raise Unresolvable("trailing backslash")
        e = data[i + 1]
        sh = _shorthand_set(e)
        if sh is not None:
            return sh, i + 2, False, None
        lit = _escape_literal(data, i)
        if lit is None:
            raise Unresolvable("unsupported escape %r" % chr(e))
        b, j = lit
        return frozenset({b}), j, False, None
    # plain literal byte
    return frozenset({c}), i + 1, False, None


def _read_quant(data, i, end):
    """Reads an EXACT `{n}` quantifier only (this population never needs
    ranged repeats on a fixed-width body). Returns (n, next_i) or (1, i)
    if none present."""
    if i < end and data[i] == ord('{'):
        m = re.match(rb"\{(\d+)\}", data[i:end])
        if m:
            return int(m.group(1)), i + m.end()
        raise Unresolvable("non-exact quantifier")
    return 1, i


def parse_seq(data, i, end):
    """One concatenation branch (no top-level '|'). Returns list of
    (byteset_or_UNRESOLVED, min_count>=1_bool) atoms, exact width only."""
    atoms = []
    while i < end:
        if data[i] == ord('|'):
            break
        bs, j, is_group, group_branches = _parse_atom(data, i, end)
        n, k = _read_quant(data, j, end)
        if is_group:
            if group_branches is None or len(group_branches) != 1:
                raise Unresolvable("quantified alternation group")
            for _ in range(n):
                atoms.extend(group_branches[0])
        else:
            for _ in range(n):
                atoms.append((bs, True))
        i = k
    return atoms


def parse_alt(data, start, end):
    """Full body: top-level '|' alternation of parse_seq branches. Returns
    list of branches (each a list of (byteset, mandatory) atoms). Raises
    Unresolvable if any branch cannot be resolved -- the caller decides
    whether to fall back to ALL_BYTES for the whole occurrence or skip it."""
    branches = []
    i = start
    while True:
        seq = parse_seq(data, i, end)
        branches.append(seq)
        # find where parse_seq stopped: re-scan is wasteful but bodies are
        # tiny (<=5 atoms); recompute end-of-branch by re-walking with the
        # same loop instead of threading index back out of parse_seq.
        i = _branch_end(data, i, end)
        if i < end and data[i] == ord('|'):
            i += 1
            continue
        break
    return branches


def _branch_end(data, i, end):
    j = i
    while j < end and data[j] != ord('|'):
        if data[j] == 0x5C:
            j += 2
            continue
        if data[j] == ord('['):
            j = _skip_class(data, j)
            continue
        if data[j] == ord('('):
            depth = 1
            j += 1
            while j < end and depth:
                if data[j] == 0x5C:
                    j += 2
                    continue
                if data[j] == ord('['):
                    j = _skip_class(data, j)
                    continue
                if data[j] == ord('('):
                    depth += 1
                elif data[j] == ord(')'):
                    depth -= 1
                j += 1
            continue
        j += 1
    return j


def try_parse_body(body_bytes):
    """Returns (branches, resolved: bool). branches is always a best-effort
    list-of-branches (UNRESOLVED atoms present iff resolved is False)."""
    try:
        branches = parse_alt(body_bytes, 0, len(body_bytes))
        resolved = all(bs is not None for br in branches for bs, _ in br)
        return branches, resolved
    except Unresolvable:
        return None, False


# ---------------------------------------------------------------------
# first-atom / last-atom sets (census A, [CTX-PREFILTER]) -- a SEPARATE,
# LOOSER parser from the ENG-LOOK one above: shape c/d bodies (the
# population census A needs, e.g. `.*[a-z]`, `a+b`, `a|bc|def`) carry real
# ranged/unbounded quantifiers the exact-width parser deliberately
# refuses. This one never needs an exact width -- only, per atom,
# "mandatory (min>=1) or skippable (min==0)" and its byteset -- so it
# accepts the full PCRE quantifier grammar (`?` `*` `+` `{m}` `{m,}`
# `{m,n}`) and represents each position as (first_bs, last_bs, mandatory):
# for a simple atom first_bs is last_bs (one byte/class has no direction);
# for a `(?:...)` GROUP, first_bs/last_bs are the UNION of the group's own
# branches' first/last sets -- correct for a first/last-atom WALK (which
# only ever needs "what could this position start/end with", never the
# group's internal structure) without flattening or expanding branches.
# ---------------------------------------------------------------------

def _read_quant_loose(data, i, end):
    """General quantifier reader; returns (min_count, next_i). Unlike
    ENG-LOOK's `_read_quant`, accepts ranged/unbounded forms -- only
    min_count (0 or >=1) is ever consumed by a caller here."""
    if i >= end:
        return 1, i
    c = data[i]

    def lazy_possessive(j):
        return j + 1 if j < end and data[j] in b"?+" else j

    if c == ord('?'):
        return 0, lazy_possessive(i + 1)
    if c == ord('*'):
        return 0, lazy_possessive(i + 1)
    if c == ord('+'):
        return 1, lazy_possessive(i + 1)
    if c == ord('{'):
        m = re.match(rb"\{(\d*)(,?)(\d*)\}", data[i:end])
        if m and (m.group(1) or m.group(3)):
            lo = int(m.group(1)) if m.group(1) else 0
            return lo, lazy_possessive(i + m.end())
    return 1, i


def _parse_atom_loose(data, i, end):
    """Returns (first_bs, last_bs, mandatory, next_i) for one quantified
    atom or `(?:...)` group. first_bs/last_bs are None if unresolvable."""
    c = data[i]
    if c == ord('('):
        if not (i + 2 < end and data[i + 1] == ord('?') and data[i + 2] == ord(':')):
            raise Unresolvable("unsupported group")
        depth = 1
        j = i + 3
        while j < end and depth:
            if data[j] == 0x5C:
                j += 2
                continue
            if data[j] == ord('['):
                j = _skip_class(data, j)
                continue
            if data[j] == ord('('):
                depth += 1
            elif data[j] == ord(')'):
                depth -= 1
            j += 1
        inner_end = j - 1
        branches = parse_loose(data, i + 3, inner_end)
        first_u, last_u = set(), set()
        ok = True
        for br in branches:
            fs, ls = first_set_loose(br), last_set_loose(br)
            if fs is None or ls is None:
                ok = False
                break
            first_u |= fs
            last_u |= ls
        first_bs = frozenset(first_u) if ok else None
        last_bs = frozenset(last_u) if ok else None
        n, k = _read_quant_loose(data, j, end)
        return first_bs, last_bs, n >= 1, k
    if c == ord('['):
        bs, j = _parse_class(data, i)
        n, k = _read_quant_loose(data, j, end)
        return bs, bs, n >= 1, k
    if c == ord('.'):
        bs = ALL_BYTES - {0x0A}
        n, k = _read_quant_loose(data, i + 1, end)
        return bs, bs, n >= 1, k
    if c in b"^$":
        return frozenset(), frozenset(), False, i + 1  # zero-width: contributes nothing
    if c == 0x5C:
        if i + 1 >= end:
            raise Unresolvable("trailing backslash")
        e = data[i + 1]
        if chr(e) in "bBAZzGK":
            return frozenset(), frozenset(), False, i + 2  # zero-width assertion
        sh = _shorthand_set(e)
        if sh is not None:
            n, k = _read_quant_loose(data, i + 2, end)
            return sh, sh, n >= 1, k
        lit = _escape_literal(data, i)
        if lit is None:
            raise Unresolvable("unsupported escape %r" % chr(e))
        b, j = lit
        n, k = _read_quant_loose(data, j, end)
        return frozenset({b}), frozenset({b}), n >= 1, k
    n, k = _read_quant_loose(data, i + 1, end)
    return frozenset({c}), frozenset({c}), n >= 1, k


def parse_seq_loose(data, i, end):
    atoms = []
    while i < end and data[i] != ord('|'):
        fbs, lbs, mand, j = _parse_atom_loose(data, i, end)
        atoms.append((fbs, lbs, mand))
        i = j
    return atoms, i


def parse_loose(data, start, end):
    """Top-level `|`-alternation of parse_seq_loose branches. Returns a
    list of branches, each a list of (first_bs, last_bs, mandatory)."""
    branches = []
    i = start
    while True:
        seq, i = parse_seq_loose(data, i, end)
        branches.append(seq)
        if i < end and data[i] == ord('|'):
            i += 1
            continue
        break
    return branches


def try_parse_body_loose(body_bytes):
    """Returns (branches, resolved: bool), the loose-parser counterpart to
    try_parse_body."""
    try:
        branches = parse_loose(body_bytes, 0, len(body_bytes))
        resolved = all(fbs is not None and lbs is not None
                        for br in branches for fbs, lbs, _ in br)
        return branches, resolved
    except Unresolvable:
        return None, False


def first_set_loose(branch):
    """Union of first-byte sets a matcher must see scanning this branch
    forward, stopping at (and including) the first MANDATORY position.
    Returns None (unresolvable) if any visited atom is unresolved, OR if
    the branch never reaches a mandatory atom at all (every atom is
    optional/zero-width, e.g. `\\n?\\z` -- the branch can match ZERO
    characters, so asserting ANY byte is necessary there would be
    UNSOUND; found live in this population,
    tests/lookaround/d27/expansions.rxt:33's `(?=\\n?\\z)`)."""
    out = set()
    for fbs, lbs, mandatory in branch:
        if fbs is None:
            return None
        out |= fbs
        if mandatory:
            return frozenset(out)
    return None  # no mandatory atom: branch may match zero-width


def last_set_loose(branch):
    """Mirror of first_set_loose, walking the branch from its END."""
    out = set()
    for fbs, lbs, mandatory in reversed(branch):
        if lbs is None:
            return None
        out |= lbs
        if mandatory:
            return frozenset(out)
    return None


def body_first_set(branches):
    """Whole-body (all alternation branches) necessary FIRST-byte set for
    a lookAHEAD body -- None if any branch is unresolved."""
    out = set()
    for br in branches:
        fs = first_set_loose(br)
        if fs is None:
            return None
        out |= fs
    return frozenset(out)


def body_last_set(branches):
    """Whole-body necessary LAST-byte set for a lookBEHIND body."""
    out = set()
    for br in branches:
        ls = last_set_loose(br)
        if ls is None:
            return None
        out |= ls
    return frozenset(out)


# ---------------------------------------------------------------------
# 3. SMALL DFA CONSTRUCTION -- Sigma*.L via NFA + subset construction
# ---------------------------------------------------------------------

def build_ends_with_dfa(branches):
    """branches: list of atom-lists (byteset, mandatory), all atoms
    resolved (byteset frozensets), of possibly-unequal per-branch length
    (this population's shape-b branches are equal-length by construction,
    but the builder does not require it). NFA: state 0 has a self-loop on
    ALL_BYTES (the Sigma* prefix) plus an epsilon "restart" edge folded
    into every state below via the same self-loop trick (Aho-Corasick's
    own idiom: the ONLY way to lose progress on a mismatch, byte-set based
    matching, is to fall back to state 0 and re-test the SAME byte there
    -- sound because state 0 accepts every byte back into itself, so a
    byte that fails branch progress still advances the automaton via
    state 0's self-loop in the same step). Returns
    (transitions: {state: {byte: state}}, start=0, accept: set(states)).
    Determinism is BY CONSTRUCTION here (no separate subset-construction
    step needed) because each state has exactly one outgoing edge per
    byte: state 0's self-loop is the fallback, and a branch-progress edge
    OVERRIDES it for the specific byte(s) in that branch position's
    byteset -- this is precisely the KMP/Aho-Corasick failure-function
    automaton, built directly rather than via NFA epsilon-closure, and
    it IS the minimal ends-with-L automaton for prefix-overlap-free small
    pattern sets (branches with a shared prefix collapse onto the same
    state chain, since node identity is the tuple of atoms matched)."""
    # states: 0 = root; states keyed by the tuple of atoms matched so far
    # from the START of some branch (trie-node identity).
    trie = {(): 0}
    next_id = 1
    accept = set()
    for branch in branches:
        atoms = tuple(bs for bs, _ in branch)
        for depth in range(1, len(atoms) + 1):
            key = atoms[:depth]
            if key not in trie:
                trie[key] = next_id
                next_id += 1
        accept.add(trie[atoms])
    # transitions[s][byte] -> state, via explicit byte expansion (bytesets
    # are small; the state count is what we report, not raw byte-table
    # size, so no need for a byte-class compression pass here).
    transitions = {s: {} for s in trie.values()}
    for tup, s in trie.items():
        # candidate next atoms from every branch that has `tup` as a
        # prefix (their atom at position len(tup))
        for branch in branches:
            atoms = tuple(bs for bs, _ in branch)
            if atoms[:len(tup)] != tup or len(atoms) <= len(tup):
                continue
            nxt_bs = atoms[len(tup)]
            nxt_state = trie[tup + (nxt_bs,)]
            for b in nxt_bs:
                transitions[s][b] = nxt_state
        for b in range(256):
            if b in transitions[s]:
                continue
            # fallback: longest proper SUFFIX of tup+[b] that is itself a
            # trie prefix (classic failure-function walk); tup is short
            # (<=5) so the linear walk is cheap.
            suf = tup
            while True:
                # try shrinking suf until (suf-with-b-appended-as-literal)
                # matches some prefix; since atoms are bytesets not single
                # bytes, walk by dropping the first atom of tup at a time
                # and re-testing whether the dropped-prefix + a real atom
                # containing b lands on a real trie node.
                matched = False
                for branch in branches:
                    atoms2 = tuple(bs for bs, _ in branch)
                    L = len(suf)
                    if L <= len(atoms2) and atoms2[:L] == suf and L < len(atoms2) and b in atoms2[L]:
                        transitions[s][b] = trie[suf + (atoms2[L],)]
                        matched = True
                        break
                if matched:
                    break
                if not suf:
                    transitions[s][b] = 0
                    break
                suf = suf[1:]
    return transitions, 0, accept


def build_starts_with_dfa_reversed(branches):
    """The lookahead-direction body automaton, built LITERALLY per this
    census's brief ("reverse(L).Sigma* in the reverse machine for
    lookahead") -- build_ends_with_dfa over each branch's atoms REVERSED,
    fed bytes in the same back-to-front order the reverse machine
    consumes them. CAVEAT this census's own run surfaced (see
    eng_look_census.md): pcrec's REVERSE machine only walks the MATCHED
    span (end back to start) -- a lookahead's body sits PAST the match
    end, a region the reverse machine never scans today, so a product
    against it measures a machine that structurally does not traverse
    the asserted text. Kept for the brief's literal instruction; treat
    its numbers as a lower bound, not the mechanism's real cost -- see
    build_delayed_accept_dfa for the construction plan.md's own ENG-LOOK
    mechanism text actually describes for bounded lookahead."""
    rev_branches = [list(reversed(br)) for br in branches]
    return build_ends_with_dfa(rev_branches)


def build_delayed_accept_dfa(branches):
    """plan.md's OWN stated mechanism for bounded lookahead: "bounded
    lookahead in the forward pass as a k-byte delayed acceptance" -- NOT
    a Sigma*L search automaton (no self-loop fallback to state 0), just
    the body's own linear/branching recognizer L, verifying the NEXT k
    bytes exactly from wherever the forward machine already is when it
    reaches the assertion point. A byte that does not continue any
    branch has NO transition at all (dead -- the assertion fails, full
    stop, never restarts elsewhere: this is verification, not search).
    Meant to be composed against the FORWARD (not reverse) erased-pattern
    machine, at the accepting states where the assertion point falls
    ("delayed" -- the base machine's own accept is deferred k bytes until
    this sub-automaton also accepts). Returns (transitions: {state:
    {byte: state}} -- byte absent means dead, start=0, accept: set());
    same trie-node identity as build_ends_with_dfa, so state COUNT is
    directly comparable (no missing self-loop edges -- exactly the trie
    node count, since there is no failure-function fallback to build)."""
    trie = {(): 0}
    next_id = 1
    accept = set()
    for branch in branches:
        atoms = tuple(bs for bs, _ in branch)
        for depth in range(1, len(atoms) + 1):
            key = atoms[:depth]
            if key not in trie:
                trie[key] = next_id
                next_id += 1
        accept.add(trie[atoms])
    transitions = {s: {} for s in trie.values()}
    for tup, s in trie.items():
        if tup in accept and len(tup) == max(len(a) for a in (tuple(bs for bs, _ in br) for br in branches)):
            continue  # a full-branch accept state has no further outgoing edges to verify
        for branch in branches:
            atoms = tuple(bs for bs, _ in branch)
            if atoms[:len(tup)] != tup or len(atoms) <= len(tup):
                continue
            nxt_bs = atoms[len(tup)]
            nxt_state = trie[tup + (nxt_bs,)]
            for b in nxt_bs:
                transitions[s][b] = nxt_state
    return transitions, 0, accept


def bfs_reachable(transitions, start):
    seen = {start}
    stack = [start]
    while stack:
        s = stack.pop()
        for b in range(256):
            t = transitions[s].get(b, transitions[s].get(None))
            if t is None:
                continue
            if t not in seen:
                seen.add(t)
                stack.append(t)
    return seen


def product_reachable(a_trans, a_start, a_dead, b_trans, b_start):
    """BFS over LIVE reachable pairs (sa, sb): a_trans is pcrec's own
    extracted table (dict state -> {byte: state}, a_dead sentinel value
    excluded), b_trans is EITHER build_ends_with_dfa's total
    (byte-complete) table OR build_delayed_accept_dfa's SPARSE one (a
    missing byte key means dead -- `.get` returns None either way, so
    both compose against this same BFS without a second code path). A
    pair whose body side is dead is dropped, not carried forward as
    "assertion permanently failed" -- correct for counting states a
    product WOULD need, since a dead body state contributes nothing
    further to reach. Returns the set of reachable LIVE pairs."""
    start = (a_start, b_start)
    seen = {start}
    stack = [start]
    while stack:
        sa, sb = stack.pop()
        for byte in range(256):
            na = a_trans[sa].get(byte)
            if na is None or na == a_dead:
                continue
            nb = b_trans[sb].get(byte)
            if nb is None:
                continue
            pair = (na, nb)
            if pair not in seen:
                seen.add(pair)
                stack.append(pair)
    return seen


# ---------------------------------------------------------------------
# pcrec-generated-C table extraction (real states from a real compile)
# ---------------------------------------------------------------------

_ARR_RE = re.compile(
    r"static const unsigned (?:short|char) rx_(forward|reverse)_(byte_class|next_state|is_accepting)\[(\d+)\]\s*=\s*\{([^}]*)\}")


def parse_pcrec_tables(c_source):
    """Returns {'forward': {...}, 'reverse': {...}} (only the machines
    present -- e.g. an ANCHORED-only artifact has neither) each with
    byte_class (list[256]), next_state (list[N]), is_accepting (list[N]),
    n_classes (int), n_states (N // n_classes), start=0, dead=65535, plus
    a `transitions` dict {state_id: {byte: next_state_id_or_None}} for
    product_reachable, keyed by the STATE IDS pcrec itself uses (which
    are premultiplied: 0, n_classes, 2*n_classes, ... -- RX_DFA_TABLE
    "premultiplied", confirmed against a sample compile 2026-09-29)."""
    out = {}
    for which, kind, size, body in _ARR_RE.findall(c_source):
        vals = [int(x) for x in body.replace("\n", " ").split(",") if x.strip()]
        d = out.setdefault(which, {})
        d[kind] = vals
    result = {}
    for which, d in out.items():
        if not all(k in d for k in ("byte_class", "next_state", "is_accepting")):
            continue
        n_classes = max(d["byte_class"]) + 1
        n_states_table = len(d["next_state"]) // n_classes
        state_ids = [s * n_classes for s in range(n_states_table)]
        transitions = {}
        for sid in state_ids:
            row = {}
            for byte in range(256):
                cl = d["byte_class"][byte]
                row[byte] = d["next_state"][sid + cl]
            transitions[sid] = row
        result[which] = dict(byte_class=d["byte_class"], n_classes=n_classes,
                              transitions=transitions, start=0, dead=65535,
                              is_accepting=d["is_accepting"])
    return result


def live_reachable_states(mach):
    """Reachable, non-dead states of one parse_pcrec_tables() machine."""
    seen = {mach['start']}
    stack = [mach['start']]
    while stack:
        s = stack.pop()
        for byte in range(256):
            t = mach['transitions'][s][byte]
            if t == mach['dead']:
                continue
            if t not in seen:
                seen.add(t)
                stack.append(t)
    return seen
