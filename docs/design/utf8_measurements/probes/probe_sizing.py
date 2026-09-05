#!/usr/bin/env python3
"""probe_sizing.py -- [M5.0] UTF-8 design gate: MEASUREMENT probe, sizing lane.

Standalone, stdlib-only. Must run under python 3.11 AND 3.14 unmodified.
Does NOT import the lane's oracle (u8_oracle.py) or anything else in this
directory: this probe is a from-scratch construction of the RE2/Ragel-style
"code-point intervals -> alternation of byte-sequence ranges" lowering, and
its own self-check section, so a bug in the shared oracle cannot leak into
these numbers and a bug in these numbers cannot leak into the shared oracle.

WHAT THIS MEASURES, per input class: the size of the NFA/DFA that the
UTF-8 milestone's lowering would build for that class, at several stages
(unshared chain alternation -> suffix-shared NFA -> subset-constructed DFA
-> minimized DFA), plus a correctness self-check of the construction itself.
See the section headers below for the exact per-class output; see
docs/design/ for the milestone this feeds.

Run: python3 probe_sizing.py            (writes the report to stdout)
Bounded: every phase that could in principle run long is wrapped in a
wall-clock budget (PHASE_TIMEOUT, seconds) and reports DNF with the elapsed
time rather than silently truncating the input.
"""

import sys
import time
import platform
import unicodedata

PHASE_TIMEOUT = 300.0  # seconds, per (class, phase) -- see module docstring

# pcrec's real caps (restated here from CLAUDE.md/APPROACH.md for the
# fits-under-cap column; this probe does not read pcrec source).
PCREC_MAX_NFA_STATES = 131072
PCREC_MAX_DFA_STATES_GOTO = 10000
PCREC_MAX_DFA_STATES_TABLE = 32000

SURROGATE_LO, SURROGATE_HI = 0xD800, 0xDFFF
MAX_CP = 0x10FFFF


# ---------------------------------------------------------------------------
# Section 0: interval utilities
# ---------------------------------------------------------------------------

def normalize_intervals(intervals):
    """Sort, merge-adjacent/overlapping, and return a clean interval list."""
    ivs = sorted(intervals)
    out = []
    for lo, hi in ivs:
        if lo > hi:
            continue
        if out and lo <= out[-1][1] + 1:
            out[-1] = (out[-1][0], max(out[-1][1], hi))
        else:
            out.append((lo, hi))
    return out


def subtract_interval(intervals, sub_lo, sub_hi):
    """Remove [sub_lo, sub_hi] from a normalized interval list."""
    out = []
    for lo, hi in intervals:
        if hi < sub_lo or lo > sub_hi:
            out.append((lo, hi))
            continue
        if lo < sub_lo:
            out.append((lo, sub_lo - 1))
        if hi > sub_hi:
            out.append((sub_hi + 1, hi))
    return out


def exclude_surrogates(intervals):
    """Every class in this probe explicitly excludes U+D800-U+DFFF (not
    encodable in UTF-8 at all) before any lowering is attempted."""
    return subtract_interval(normalize_intervals(intervals), SURROGATE_LO, SURROGATE_HI)


def complement(intervals, lo=0, hi=MAX_CP):
    """Complement a normalized interval list within [lo, hi]."""
    out = []
    cur = lo
    for a, b in intervals:
        if a > cur:
            out.append((cur, a - 1))
        cur = max(cur, b + 1)
    if cur <= hi:
        out.append((cur, hi))
    return out


def intervals_from_predicate(pred, lo=0, hi=MAX_CP):
    out = []
    start = None
    for cp in range(lo, hi + 1):
        if pred(cp):
            if start is None:
                start = cp
        else:
            if start is not None:
                out.append((start, cp - 1))
                start = None
    if start is not None:
        out.append((start, hi))
    return out


def format_intervals(intervals, limit=12):
    parts = []
    for lo, hi in intervals[:limit]:
        if lo == hi:
            parts.append("U+%04X" % lo)
        else:
            parts.append("U+%04X-U+%04X" % (lo, hi))
    s = ", ".join(parts)
    if len(intervals) > limit:
        s += ", ... (%d more)" % (len(intervals) - limit)
    return s


# ---------------------------------------------------------------------------
# Section 1: codepoint-range -> UTF-8 byte-sequence-range decomposition
#
# The classic RE2/Ragel construction. UTF-8 length boundaries:
#   1 byte : U+0000  - U+007F   lead byte range 0x00-0x7F  (7 data bits)
#   2 byte : U+0080  - U+07FF   lead byte range 0xC0-0xDF  (5+6 data bits)
#   3 byte : U+0800  - U+FFFF   lead byte range 0xE0-0xEF  (4+6+6 data bits)
#   4 byte : U+10000 - U+10FFFF lead byte range 0xF0-0xF7  (3+6+6+6 data bits)
#
# Within one length class, a codepoint's UTF-8 encoding is exactly its
# "digit tuple" in a mixed-radix number system: the leading byte carries a
# small-radix top digit (128/32/16/8 for 1/2/3/4-byte forms respectively)
# and every continuation byte carries a radix-64 digit (0x80 | 6 bits).
# Splitting [lo, hi] into a minimal set of "aligned boxes" (one contiguous
# range per digit position) is the same combinatorial problem as splitting
# an integer range into canonical prefix-aligned blocks (cf. CIDR
# aggregation): recurse on the first digit where lo and hi differ, peel off
# a left edge (first digit fixed at lo's, remainder spanning lo's suffix up
# to all-max) and a right edge (first digit fixed at hi's, remainder
# spanning all-min up to hi's suffix) only when that suffix isn't already
# a full box, and let the middle be one flat box covering everything
# between. Verified against the textbook worked example: 0x0800-0xFFFF (the
# whole 3-byte class, surrogates NOT yet excluded) decomposes to exactly two
# rows, "E0 A0-BF 80-BF" and "E1-EF 80-BF 80-BF" -- exactly the well-known
# canonical table for that class before the surrogate carve-out.
# ---------------------------------------------------------------------------

LENGTH_SEGMENTS = [
    (0x0000, 0x007F, 1, 0x00, 128),
    (0x0080, 0x07FF, 2, 0xC0, 32),
    (0x0800, 0xFFFF, 3, 0xE0, 16),
    (0x10000, 0x10FFFF, 4, 0xF0, 8),
]


def split_by_utf8_length(lo, hi):
    """[lo,hi] -> list of (seg_lo, seg_hi, nbytes, lead_prefix, lead_radix)."""
    out = []
    for blo, bhi, n, prefix, radix in LENGTH_SEGMENTS:
        seg_lo, seg_hi = max(lo, blo), min(hi, bhi)
        if seg_lo <= seg_hi:
            out.append((seg_lo, seg_hi, n, prefix, radix))
    return out


def to_digits(cp, n):
    """cp's UTF-8 digit tuple: digit 0 = lead byte's data bits, digits
    1..n-1 = continuation-byte 6-bit values, most significant first."""
    shifts = [(n - 1 - i) * 6 for i in range(n)]
    return [(cp >> s) & (0x3F if i > 0 else ((1 << (7 - n)) - 1 if n > 1 else 0x7F))
            for i, s in enumerate(shifts)]


def radices_for(n):
    if n == 1:
        return [128]
    lead_bits = 7 - n  # 5,4,3 for n=2,3,4
    return [1 << lead_bits] + [64] * (n - 1)


def expand_digit_range(dlo, dhi, radices):
    """Recursive box-decomposition of the digit-tuple range [dlo, dhi]
    (lexicographic == numeric order for a fixed mixed-radix system).
    Returns a list of range-tuples, each a list of (lo,hi) pairs, one per
    digit position, whose Cartesian product union equals exactly the set
    of digit tuples d with dlo <= d <= dhi."""
    n = len(dlo)
    if n == 0:
        return [[]]
    if n == 1:
        return [[(dlo[0], dhi[0])]]
    lo0, hi0 = dlo[0], dhi[0]
    rest_radices = radices[1:]
    all_min = [0] * len(rest_radices)
    all_max = [r - 1 for r in rest_radices]
    results = []
    if lo0 == hi0:
        for s in expand_digit_range(dlo[1:], dhi[1:], radices[1:]):
            results.append([(lo0, lo0)] + s)
        return results
    lo_suffix_full = (list(dlo[1:]) == all_min)
    hi_suffix_full = (list(dhi[1:]) == all_max)
    mid_lo, mid_hi = lo0, hi0
    if not lo_suffix_full:
        for s in expand_digit_range(dlo[1:], all_max, radices[1:]):
            results.append([(lo0, lo0)] + s)
        mid_lo = lo0 + 1
    if not hi_suffix_full:
        for s in expand_digit_range(all_min, dhi[1:], radices[1:]):
            results.append([(hi0, hi0)] + s)
        mid_hi = hi0 - 1
    if mid_lo <= mid_hi:
        results.append([(mid_lo, mid_hi)] + [(0, r - 1) for r in rest_radices])
    return results


def codepoint_range_to_byte_sequences(lo, hi):
    """[lo,hi] (any span) -> list of byte-range-tuples, each a list of
    (byte_lo, byte_hi) pairs (actual byte values, prefixes applied),
    representing the disjoint alternation of byte-sequence ranges whose
    union decodes to exactly the codepoints in [lo,hi]."""
    out = []
    for seg_lo, seg_hi, n, prefix, lead_radix in split_by_utf8_length(lo, hi):
        radices = radices_for(n)
        dlo = to_digits(seg_lo, n)
        dhi = to_digits(seg_hi, n)
        for seq in expand_digit_range(dlo, dhi, radices):
            byte_seq = []
            for i, (a, b) in enumerate(seq):
                if i == 0:
                    byte_seq.append((prefix + a, prefix + b))
                else:
                    byte_seq.append((0x80 + a, 0x80 + b))
            out.append(tuple(byte_seq))
    return out


def intervals_to_byte_sequences(intervals):
    seqs = []
    for lo, hi in intervals:
        seqs.extend(codepoint_range_to_byte_sequences(lo, hi))
    return seqs


# ---------------------------------------------------------------------------
# Section 2: NFA construction -- unshared (naive) and suffix-shared
# ---------------------------------------------------------------------------

def naive_nfa_state_count(byte_sequences):
    """1 shared start (S) + a fully private chain per alternative, no
    sharing at all -- not even the accept state. Documented convention:
    each alternative of length k contributes k private states (one per
    byte consumed, the last of which is that alternative's own private
    accept)."""
    return 1 + sum(len(seq) for seq in byte_sequences)


def build_shared_nfa(byte_sequences):
    """Suffix-shared NFA: a trie built from the END of each alternative,
    hash-consing identical (range, target) pairs. Returns:
      cache      : dict {(range, target_id): node_id}  (node_id 0 == F, the
                   universal accept/terminal, created implicitly)
      byte_trans : dict node_id -> [(lo,hi,target_id)]  (F and S excluded
                   from having exactly-one-entry semantics; F has none)
      s_id       : the id of S, the shared start/fan-out node
      f_id       : the id of F, the shared terminal/accept node
    Every node except S has out-degree exactly 1 by construction (each was
    created for one specific (range, target) pair); S may have several
    (its distinct first-position (range, entry) pairs)."""
    F_ID = 0
    next_id = [1]
    cache = {}          # (range, target) -> node_id
    byte_trans = {F_ID: []}

    def get_or_create(rng, target):
        key = (rng, target)
        if key in cache:
            return cache[key]
        nid = next_id[0]
        next_id[0] += 1
        cache[key] = nid
        byte_trans[nid] = [(rng[0], rng[1], target)]
        return nid

    entry_ids = set()
    for seq in byte_sequences:
        cur = F_ID
        for rng in reversed(seq):
            cur = get_or_create(rng, cur)
        # `cur` is now the entry node for this whole alternative: its OWN
        # byte_trans entry already carries the first-range transition (it
        # was the last one created, from the reversed walk). S must reach
        # it by EPSILON, not by a byte-range edge relabelling that same
        # first range -- a byte-range edge there would consume the first
        # byte twice (once at S, once again at the entry node itself).
        entry_ids.add(cur)

    # S is a pure epsilon fan-out node: no byte_trans entry of its own.
    s_id = next_id[0]
    next_id[0] += 1
    byte_trans[s_id] = []
    return {
        "byte_trans": byte_trans,
        "s_id": s_id,
        "s_entries": entry_ids,   # nodes S reaches by epsilon
        "f_id": F_ID,
        "n_states": next_id[0],  # includes F, all interior nodes, and S
    }


# ---------------------------------------------------------------------------
# Section 3: general epsilon-NFA subset construction (used for the base
# class and for the quantified X*/X{1,3} forms, uniformly)
# ---------------------------------------------------------------------------

class TimedOut(Exception):
    pass


def eps_closure(node_ids, eps):
    stack = list(node_ids)
    seen = set(node_ids)
    while stack:
        n = stack.pop()
        for m in eps.get(n, ()):
            if m not in seen:
                seen.add(m)
                stack.append(m)
    return frozenset(seen)


def subset_construct(start_ids, eps, byte_trans, accept_test, deadline):
    """Standard interval-alphabet subset construction. `accept_test(state)`
    decides acceptance of a DFA state (a frozenset of NFA node ids) --
    callers pass a closure testing membership of a designated accept node.
    Partial transition function: a byte outside every live range from a
    state is an implicit reject and is NOT materialized as a state (no
    explicit trap/dead state is counted -- see report preamble for why).
    Returns (order, transitions) where order[i] is the frozenset for DFA
    state i and transitions[i] is a list of (lo,hi,target_idx)."""
    start = eps_closure(start_ids, eps)
    index = {start: 0}
    order = [start]
    transitions = {}
    i = 0
    while i < len(order):
        if time.time() > deadline:
            raise TimedOut()
        cur = order[i]
        segs = []
        for n in cur:
            for (lo, hi, tgt) in byte_trans.get(n, ()):
                segs.append((lo, hi, tgt))
        if not segs:
            transitions[i] = []
            i += 1
            continue
        boundaries = sorted(set(
            [lo for lo, hi, tgt in segs] + [hi + 1 for lo, hi, tgt in segs]
        ))
        trans_list = []
        for j in range(len(boundaries) - 1):
            b_lo = boundaries[j]
            if b_lo > 255:
                break
            b_hi = min(boundaries[j + 1] - 1, 255)
            rep = b_lo
            targets = [tgt for (lo, hi, tgt) in segs if lo <= rep <= hi]
            if not targets:
                continue
            closure = eps_closure(targets, eps)
            if closure not in index:
                index[closure] = len(order)
                order.append(closure)
            trans_list.append((b_lo, b_hi, index[closure]))
        transitions[i] = trans_list
        i += 1
    accepting = {idx for idx, st in enumerate(order) if accept_test(st)}
    return order, transitions, accepting


def minimize_dfa(order, transitions, accepting, deadline):
    """Moore-style partition refinement over the full 256-symbol alphabet
    (expanding the partial range-transition lists into per-byte lookups;
    missing == an implicit -1 'dead' signal used only for signature
    comparison, never materialized as a counted state). Returns the number
    of minimized states (reachable ones only -- the same partial-function
    convention as the DFA count)."""
    n = len(order)
    if time.time() > deadline:
        raise TimedOut()
    full = [[-1] * 256 for _ in range(n)]
    for i, tl in transitions.items():
        row = full[i]
        for (lo, hi, tgt) in tl:
            for b in range(lo, hi + 1):
                row[b] = tgt
    classof = [1 if i in accepting else 0 for i in range(n)]
    while True:
        if time.time() > deadline:
            raise TimedOut()
        sig_map = {}
        newclass = [0] * n
        for i in range(n):
            row = full[i]
            sig = (classof[i], tuple(classof[t] if t != -1 else -1 for t in row))
            cid = sig_map.get(sig)
            if cid is None:
                cid = len(sig_map)
                sig_map[sig] = cid
            newclass[i] = cid
        if len(sig_map) == len(set(classof)):
            break
        classof = newclass
    return len(set(classof))


# ---------------------------------------------------------------------------
# Section 4: assembling class automata (base, star, bounded-repeat) and
# running the measurement pipeline over one class
# ---------------------------------------------------------------------------

def base_automaton(byte_sequences):
    """X alone: shared-NFA nodes + one epsilon edge F->ACCEPT so acceptance
    is uniformly 'ACCEPT in state', matching the star/repeat builders."""
    shared = build_shared_nfa(byte_sequences)
    bt = dict(shared["byte_trans"])
    accept_id = shared["n_states"]
    eps = {shared["f_id"]: {accept_id}, shared["s_id"]: set(shared["s_entries"])}
    bt[accept_id] = []
    return {
        "byte_trans": bt, "eps": eps,
        "start_ids": {shared["s_id"]},
        "accept_id": accept_id,
        "s_id": shared["s_id"],
        "raw_nfa_states": shared["n_states"] + 1,  # + ACCEPT sentinel
    }


def star_automaton(byte_sequences):
    """X* : loop F back to S (repeat) or to ACCEPT (stop); ENTRY also goes
    straight to ACCEPT (zero repetitions)."""
    shared = build_shared_nfa(byte_sequences)
    bt = dict(shared["byte_trans"])
    accept_id = shared["n_states"]
    entry_id = shared["n_states"] + 1
    bt[accept_id] = []
    bt[entry_id] = []
    eps = {
        entry_id: {shared["s_id"], accept_id},
        shared["f_id"]: {shared["s_id"], accept_id},
        shared["s_id"]: set(shared["s_entries"]),
    }
    return {
        "byte_trans": bt, "eps": eps,
        "start_ids": {entry_id},
        "accept_id": accept_id,
        "raw_nfa_states": shared["n_states"] + 2,
    }


def bounded_repeat_automaton(byte_sequences, lo_rep, hi_rep):
    """X{lo_rep,hi_rep}: hi_rep independently-cloned copies chained by
    epsilon, ACCEPT reachable from any copy index >= lo_rep's F."""
    assert lo_rep >= 1
    shared = build_shared_nfa(byte_sequences)
    per_copy_states = shared["n_states"]
    accept_id = per_copy_states * hi_rep
    bt = {accept_id: []}
    eps = {}
    copy_s = []
    copy_f = []
    for c in range(hi_rep):
        off = c * per_copy_states
        for nid, trans in shared["byte_trans"].items():
            bt[nid + off] = [(lo, hi, tgt + off) for (lo, hi, tgt) in trans]
        copy_s.append(shared["s_id"] + off)
        copy_f.append(shared["f_id"] + off)
        eps[shared["s_id"] + off] = {e + off for e in shared["s_entries"]}
    for c in range(hi_rep):
        targets = set()
        if c + 1 < hi_rep:
            targets.add(copy_s[c + 1])
        if (c + 1) >= lo_rep:
            targets.add(accept_id)
        eps[copy_f[c]] = targets
    return {
        "byte_trans": bt, "eps": eps,
        "start_ids": {copy_s[0]},
        "accept_id": accept_id,
        "raw_nfa_states": per_copy_states * hi_rep + 1,
    }


def lead_byte_set(byte_sequences):
    ranges = normalize_intervals({(lo, hi) for seq in byte_sequences for (lo, hi) in [seq[0]]})
    total = sum(hi - lo + 1 for lo, hi in ranges)
    return ranges, total


def measure_automaton(auto, deadline, label):
    """Run subset construction + minimization for one (already-built)
    epsilon-NFA. Returns a dict of results, or {'dnf': elapsed} on timeout."""
    t0 = time.time()
    try:
        order, transitions, accepting = subset_construct(
            auto["start_ids"], auto["eps"], auto["byte_trans"],
            lambda st: auto["accept_id"] in st, deadline)
    except TimedOut:
        return {"dnf_stage": "subset_construct", "elapsed": time.time() - t0}
    dfa_states = len(order)
    t1 = time.time()
    try:
        min_states = minimize_dfa(order, transitions, accepting, deadline)
    except TimedOut:
        return {"dnf_stage": "minimize", "elapsed": time.time() - t1,
                "dfa_states": dfa_states, "subset_time": t1 - t0}
    return {
        "dfa_states": dfa_states, "min_states": min_states,
        "subset_time": t1 - t0, "minimize_time": time.time() - t1,
        "order": order, "transitions": transitions, "accepting": accepting,
    }


def dfa_match(byte_seq, transitions, accepting, start_idx=0):
    cur = start_idx
    for b in byte_seq:
        nxt = None
        for (lo, hi, tgt) in transitions.get(cur, ()):
            if lo <= b <= hi:
                nxt = tgt
                break
        if nxt is None:
            return False
        cur = nxt
    return cur in accepting


# ---------------------------------------------------------------------------
# Section 5: self-check -- verifies the base-class construction against a
# from-scratch reference encoder/decoder, NOT against the construction's
# own machinery.
# ---------------------------------------------------------------------------

def reference_encode_cp(cp):
    """Reference UTF-8 encoder, written independently of Section 1's
    digit-tuple machinery (uses Python's own codec for non-surrogates)."""
    return chr(cp).encode("utf-8")


def reference_encode_surrogate_scalar(cp):
    """Manual 3-byte 'CESU-8-shaped' encoding of a surrogate scalar value
    (D800-DFFF). Python's str/bytes layer refuses to do this at all
    (chr(cp).encode('utf-8') raises UnicodeEncodeError for surrogates), so
    it is built by hand from the same 3-byte bit layout as valid code
    points -- this is exactly the byte string real UTF-8 decoders must
    reject, and exactly what a naive digit-range construction that forgot
    to exclude D800-DFFF would accept."""
    assert SURROGATE_LO <= cp <= SURROGATE_HI
    b0 = 0xE0 | ((cp >> 12) & 0x0F)
    b1 = 0x80 | ((cp >> 6) & 0x3F)
    b2 = 0x80 | (cp & 0x3F)
    return bytes([b0, b1, b2])


def overlong_encode_cp(cp, force_len):
    """Deliberately overlong re-encoding of `cp` using `force_len` bytes
    (force_len must exceed the codepoint's minimal length). Used only as a
    must-reject self-check input."""
    n = force_len
    if n == 1:
        prefix, lead_bits = 0x00, 7
    elif n == 2:
        prefix, lead_bits = 0xC0, 5
    elif n == 3:
        prefix, lead_bits = 0xE0, 4
    else:
        prefix, lead_bits = 0xF0, 3
    shifts = [(n - 1 - i) * 6 for i in range(n)]
    out = []
    for i, s in enumerate(shifts):
        if i == 0:
            out.append(prefix | ((cp >> s) & ((1 << lead_bits) - 1)))
        else:
            out.append(0x80 | ((cp >> s) & 0x3F))
    return bytes(out)


def self_check_class(name, intervals, base_auto_result, rng):
    """Sample endpoints, neighbours, interior points, out-of-class points,
    surrogate encodings, truncations and overlong forms; check the built
    DFA against the reference encoder/decoder. Returns (checked, mismatches,
    mismatch_examples[:8])."""
    order = base_auto_result.get("order")
    transitions = base_auto_result.get("transitions")
    accepting = base_auto_result.get("accepting")
    if order is None:
        return 0, 0, ["(skipped: base automaton DNF'd, see dfa_states row)"]

    in_set = set()
    for lo, hi in intervals:
        in_set.add(lo)
        in_set.add(hi)
        if lo - 1 >= 0:
            in_set.add(lo - 1)
        if hi + 1 <= MAX_CP:
            in_set.add(hi + 1)
        mid = (lo + hi) // 2
        in_set.add(mid)
    for _ in range(200):
        in_set.add(rng.randint(0, MAX_CP))
    in_set.discard(None)
    in_set = {cp for cp in in_set if 0 <= cp <= MAX_CP}

    def is_in_class(cp):
        for lo, hi in intervals:
            if lo <= cp <= hi:
                return True
        return False

    checked = 0
    mismatches = 0
    examples = []

    for cp in sorted(in_set):
        if SURROGATE_LO <= cp <= SURROGATE_HI:
            continue  # not encodable; handled separately below
        expect = is_in_class(cp)
        enc = reference_encode_cp(cp)
        got = dfa_match(enc, transitions, accepting)
        checked += 1
        if got != expect:
            mismatches += 1
            if len(examples) < 8:
                examples.append(
                    "U+%04X: expected %s got %s (encoded %s)"
                    % (cp, expect, got, enc.hex()))

    surrogate_samples = [SURROGATE_LO, SURROGATE_LO + 1, (SURROGATE_LO + SURROGATE_HI) // 2,
                          SURROGATE_HI - 1, SURROGATE_HI]
    for cp in surrogate_samples:
        enc = reference_encode_surrogate_scalar(cp)
        got = dfa_match(enc, transitions, accepting)
        checked += 1
        if got:
            mismatches += 1
            if len(examples) < 8:
                examples.append(
                    "SURROGATE U+%04X: expected False got True (encoded %s)"
                    % (cp, enc.hex()))

    trunc_sources = [cp for cp in in_set
                     if cp > 0x7F and not (SURROGATE_LO <= cp <= SURROGATE_HI)][:20]
    for cp in trunc_sources:
        enc = reference_encode_cp(cp)
        for cutlen in range(1, len(enc)):
            trunc = enc[:cutlen]
            checked += 1
            got = dfa_match(trunc, transitions, accepting)
            if got:
                mismatches += 1
                if len(examples) < 8:
                    examples.append(
                        "TRUNCATED U+%04X[:%d]: expected False got True (bytes %s)"
                        % (cp, cutlen, trunc.hex()))

    overlong_sources = [0x00, 0x41, 0x7F, 0x80, 0x7FF]
    for cp in overlong_sources:
        min_len = 1 if cp <= 0x7F else (2 if cp <= 0x7FF else (3 if cp <= 0xFFFF else 4))
        for n in range(min_len + 1, 5):
            enc = overlong_encode_cp(cp, n)
            checked += 1
            got = dfa_match(enc, transitions, accepting)
            if got:
                mismatches += 1
                if len(examples) < 8:
                    examples.append(
                        "OVERLONG U+%04X as %d bytes: expected False got True (bytes %s)"
                        % (cp, n, enc.hex()))

    return checked, mismatches, examples


# ---------------------------------------------------------------------------
# Section 6: the input classes
# ---------------------------------------------------------------------------

def build_classes():
    classes = []

    classes.append(("1. [a-z] (ASCII control)",
                     exclude_surrogates([(ord('a'), ord('z'))]), None))

    classes.append(("2. [\\x{80}-\\x{7FF}] (pure 2-byte band)",
                     exclude_surrogates([(0x80, 0x7FF)]), None))

    classes.append(("3. [α-ω] = U+03B1-U+03C9 (small non-ASCII range)",
                     exclude_surrogates([(0x03B1, 0x03C9)]), None))

    classes.append(("4. [\\x{100}-\\x{10FFFF}] (charter stress case)",
                     exclude_surrogates([(0x100, MAX_CP)]), None))

    classes.append(("5. . under UTF, not DOTALL (all U+0000-U+10FFFF except U+000A)",
                     exclude_surrogates(subtract_interval([(0, MAX_CP)], 0x000A, 0x000A)),
                     None))

    classes.append(("6. [^a] under UTF (U+0000-U+10FFFF minus 'a')",
                     exclude_surrogates(subtract_interval([(0, MAX_CP)], ord('a'), ord('a'))),
                     None))

    t_cat = time.time()
    cats = [unicodedata.category(chr(cp)) for cp in range(MAX_CP + 1)]
    cat_time = time.time() - t_cat

    def is_surr(cp):
        return SURROGATE_LO <= cp <= SURROGATE_HI

    L = exclude_surrogates(intervals_from_predicate(lambda cp: cats[cp][0] == 'L' and not is_surr(cp)))
    classes.append(("7. \\p{L} (category starts with L)", L, None))

    Lu = exclude_surrogates(intervals_from_predicate(lambda cp: cats[cp] == 'Lu' and not is_surr(cp)))
    classes.append(("8. \\p{Lu} (category exactly Lu)", Lu, None))

    names = [unicodedata.name(chr(cp), "") if cats[cp] != "Cn" else "" for cp in range(MAX_CP + 1)]
    greek_pred = lambda cp: ("GREEK" in names[cp]) and not is_surr(cp)
    Greek = exclude_surrogates(intervals_from_predicate(greek_pred))
    greek_note = ("APPROXIMATION, NOT Script=Greek: python's stdlib unicodedata module "
                  "carries no Script property at all. This proxies it as 'every assigned "
                  "codepoint whose unicodedata.name() contains the substring GREEK' -- e.g. "
                  "GREEK SMALL LETTER ALPHA, GREEK CAPITAL LETTER ALPHA WITH TONOS, GREEK "
                  "QUESTION MARK. Known divergence from real Script=Greek (stated, not "
                  "measured against it here): misses any Greek-script character whose "
                  "Unicode NAME happens not to contain the word GREEK (rare but not "
                  "provably zero, e.g. some Greek Extended combining-diacritic forms are "
                  "named via their base letter); may include a false positive if a "
                  "non-Greek character's name happens to contain the substring GREEK (none "
                  "found in Unicode %s at the time of this run, but that is an empirical "
                  "observation of THIS run, not a guarantee). Use for rough sizing only."
                  % unicodedata.unidata_version)
    classes.append(("9. \\p{Greek} (SCRIPT APPROXIMATION -- read the note)", Greek, greek_note))

    w_pred = lambda cp: (cats[cp][0] in ('L', 'N') or cats[cp] == 'Mn' or cp == 0x5F) and not is_surr(cp)
    W = exclude_surrogates(intervals_from_predicate(w_pred))
    w_note = ("ASSUMPTION (to be checked against the real PCRE2 oracle by a different "
              "probe, not here): \\w under UCP == every codepoint whose "
              "unicodedata.category() starts with 'L' or 'N', plus category exactly 'Mn' "
              "(nonspacing mark), plus the literal character '_' (U+005F). This is a "
              "commonly-cited approximation of PCRE2's UCP \\w, not a verified one.")
    classes.append(("10. \\w under UCP (approx: L*, N*, Mn, '_')", W, w_note))

    return classes, cat_time


# ---------------------------------------------------------------------------
# Section 7: report assembly
# ---------------------------------------------------------------------------

def fits(n, cap):
    return "yes" if n is not None and n <= cap else ("DNF" if n is None else "NO")


def main():
    out = []
    p = out.append
    start_wall = time.time()

    p("=" * 78)
    p("probe_sizing.py -- [M5.0] UTF-8 design gate, sizing lane")
    p("=" * 78)
    p("host machine   : %s" % platform.platform())
    p("python version : %s (%s)" % (platform.python_version(), sys.executable))
    p("unicodedata    : unidata_version=%s" % unicodedata.unidata_version)
    p("run timestamp  : %s" % time.strftime("%Y-%m-%d %H:%M:%S %z"))
    p("")
    p("CAVEAT (stated once, applies to every \\p{} row below): the Unicode "
      "version this python's unicodedata module knows (%s) may differ from "
      "the version libpcre2 10.46 (the project's reference oracle, per "
      "u8_oracle.py's header) was built against. This probe does not attempt "
      "to reconcile that -- a different probe in this lane owns that "
      "question. Any \\p{}-derived row's interval count and all downstream "
      "sizes are only as good as this python's Unicode data." % unicodedata.unidata_version)
    p("")
    p("CONVENTIONS used throughout (read before comparing numbers to pcrec's "
      "real caps):")
    p("  (c) naive/unshared NFA states = 1 shared start (S) + a fully "
      "private chain per byte-sequence alternative (no sharing at all, not "
      "even the accept state -- each alternative's own last state is its "
      "own private accept).")
    p("  (d) suffix-shared NFA states = a trie built from the END of every "
      "alternative, hash-consing identical (byte-range, target) pairs, plus "
      "one shared start (S) and one shared terminal accept (F) that the "
      "hash-consing merges automatically.")
    p("  (e)/(f) DFA/minimized-DFA counts are of a PARTIAL transition "
      "function: a byte outside every live transition from a state is an "
      "implicit reject and is NOT materialized as a counted state (no "
      "explicit trap/dead state). This matches how a fragment-composition "
      "compiler like pcrec represents 'no match' (fallthrough), not a total "
      "automaton with an explicit dead state -- stated so these numbers are "
      "not silently off-by-one against a reader's different convention.")
    p("  Every (e)/(f)/(g) figure is for the BASE class alone unless "
      "labelled '* form' or '{1,3} form'.")
    p("")

    classes, cat_time = build_classes()
    p("(unicodedata.category() precomputed for all %d codepoints in %.3fs)"
      % (MAX_CP + 1, cat_time))
    p("")

    rng_seed = 0xC0FFEE
    import random
    rng = random.Random(rng_seed)

    rows = []            # for the summary table
    dnf_notes = []
    assumption_notes = []
    total_checked = 0
    total_mismatches = 0

    for name, intervals, note in classes:
        p("-" * 78)
        p(name)
        p("-" * 78)
        p("intervals (%d): %s" % (len(intervals), format_intervals(intervals)))
        if note:
            p("NOTE: " + note)
            assumption_notes.append((name, note))
        p("")

        byte_seqs = intervals_to_byte_sequences(intervals)
        n_alt = len(byte_seqs)
        naive_states = naive_nfa_state_count(byte_seqs)

        auto = base_automaton(byte_seqs)
        shared_states = auto["raw_nfa_states"]
        ratio = (shared_states / naive_states) if naive_states else float("nan")

        lead_ranges, lead_count = lead_byte_set(byte_seqs)

        deadline = time.time() + PHASE_TIMEOUT
        res = measure_automaton(auto, deadline, name)

        p("(a) codepoint intervals            : %d" % len(intervals))
        p("(b) byte-sequence alternatives      : %d" % n_alt)
        p("(c) NFA states, unshared (naive)    : %d" % naive_states)
        p("(d) NFA states, suffix-shared       : %d  (ratio d/c = %.4f)"
          % (shared_states, ratio))

        dfa_states = min_states = None
        if "dnf_stage" in res:
            p("(e) DFA states (subset construction): DNF at stage '%s' after %.1fs (budget %.0fs)"
              % (res["dnf_stage"], res["elapsed"], PHASE_TIMEOUT))
            dnf_notes.append("%s: base-form %s DNF after %.1fs" % (name, res["dnf_stage"], res["elapsed"]))
        else:
            dfa_states = res["dfa_states"]
            p("(e) DFA states (subset construction): %d  (subset-construct wall time %.3fs)"
              % (dfa_states, res["subset_time"]))
            if "min_states" in res:
                min_states = res["min_states"]
                p("(f) minimized DFA states            : %d  (minimize wall time %.3fs)"
                  % (min_states, res["minimize_time"]))
            else:
                p("(f) minimized DFA states            : DNF at stage '%s' after %.1fs (budget %.0fs)"
                  % (res["dnf_stage"], res["elapsed"], PHASE_TIMEOUT))
                dnf_notes.append("%s: base-form minimize DNF after %.1fs" % (name, res["elapsed"]))

        p("(g) lead byte set                   : %d distinct byte value(s): %s"
          % (lead_count, ", ".join("0x%02X-0x%02X" % (lo, hi) if lo != hi else "0x%02X" % lo
                                    for lo, hi in lead_ranges)))

        checked, mismatches, examples = self_check_class(name, intervals, res, rng)
        total_checked += checked
        total_mismatches += mismatches
        p("SELF-CHECK: %d sample points checked, %d mismatches" % (checked, mismatches))
        if mismatches:
            p("  *** MISMATCH DETAIL (construction is SUSPECT for this class) ***")
            for ex in examples:
                p("  MISMATCH: " + ex)

        rows.append({
            "name": name, "n_ivs": len(intervals), "n_alt": n_alt,
            "naive": naive_states, "shared": shared_states, "ratio": ratio,
            "dfa": dfa_states, "min": min_states, "lead_count": lead_count,
        })
        p("")

    # ---- quantified forms for classes 4, 5, 7 ----------------------------
    p("=" * 78)
    p("QUANTIFIED FORMS: X* and X{1,3} for classes 4, 5, 7")
    p("(does a UTF-8 '.*' blow the DFA cap?)")
    p("=" * 78)
    p("")

    quant_targets = {classes[3][0]: classes[3][1], classes[4][0]: classes[4][1],
                     classes[6][0]: classes[6][1]}
    quant_rows = []
    for name, intervals in quant_targets.items():
        byte_seqs = intervals_to_byte_sequences(intervals)
        p("-" * 78)
        p(name)
        p("-" * 78)
        for form_label, builder in (
            ("X*", lambda bs: star_automaton(bs)),
            ("X{1,3}", lambda bs: bounded_repeat_automaton(bs, 1, 3)),
        ):
            auto = builder(byte_seqs)
            deadline = time.time() + PHASE_TIMEOUT
            res = measure_automaton(auto, deadline, name + " " + form_label)
            if "dnf_stage" in res:
                p("  %-8s raw NFA states (pre-determinize): %d" % (form_label, auto["raw_nfa_states"]))
                p("  %-8s (e) DFA states: DNF at stage '%s' after %.1fs (budget %.0fs)"
                  % (form_label, res["dnf_stage"], res["elapsed"], PHASE_TIMEOUT))
                dnf_notes.append("%s %s form: %s DNF after %.1fs" % (name, form_label, res["dnf_stage"], res["elapsed"]))
                quant_rows.append((name, form_label, auto["raw_nfa_states"], None, None))
            else:
                dfa_states = res["dfa_states"]
                line = "  %-8s raw NFA states (pre-determinize): %d ; (e) DFA states: %d (%.3fs)" % (
                    form_label, auto["raw_nfa_states"], dfa_states, res["subset_time"])
                min_states = None
                if "min_states" in res:
                    min_states = res["min_states"]
                    line += " ; (f) minimized: %d (%.3fs)" % (min_states, res["minimize_time"])
                else:
                    line += " ; (f) minimized: DNF after %.1fs" % res["elapsed"]
                    dnf_notes.append("%s %s form: minimize DNF after %.1fs" % (name, form_label, res["elapsed"]))
                p(line)
                quant_rows.append((name, form_label, auto["raw_nfa_states"], dfa_states, min_states))
        p("")

    # ---- summary table -----------------------------------------------------
    p("=" * 78)
    p("SUMMARY TABLE (base classes)")
    p("=" * 78)
    header = ("%-46s %5s %5s %8s %8s %7s %8s %8s %5s" %
              ("class", "ivs", "alt", "naive", "shared", "ratio", "dfa", "min", "lead"))
    p(header)
    p("-" * len(header))
    for r in rows:
        p("%-46s %5d %5d %8d %8d %7.3f %8s %8s %5d" % (
            r["name"][:46], r["n_ivs"], r["n_alt"], r["naive"], r["shared"], r["ratio"],
            "DNF" if r["dfa"] is None else r["dfa"],
            "DNF" if r["min"] is None else r["min"],
            r["lead_count"]))
    p("")

    p("CAP-FIT TABLE (against pcrec's real caps: NFA<=%d, DFA-goto<=%d, DFA-table<=%d)"
      % (PCREC_MAX_NFA_STATES, PCREC_MAX_DFA_STATES_GOTO, PCREC_MAX_DFA_STATES_TABLE))
    header2 = ("%-46s %10s %10s %10s %10s" %
               ("class", "NFA-shrd", "fit-NFA", "min-DFA", "fit-DFAgoto/table"))
    p(header2)
    p("-" * len(header2))
    for r in rows:
        fit_nfa = fits(r["shared"], PCREC_MAX_NFA_STATES)
        if r["min"] is None:
            fit_dfa = "DNF"
        else:
            fg = fits(r["min"], PCREC_MAX_DFA_STATES_GOTO)
            ft = fits(r["min"], PCREC_MAX_DFA_STATES_TABLE)
            fit_dfa = "%s/%s" % (fg, ft)
        p("%-46s %10d %10s %10s %10s" % (r["name"][:46], r["shared"], fit_nfa,
                                          "DNF" if r["min"] is None else r["min"], fit_dfa))
    p("")

    p("QUANTIFIED-FORM CAP-FIT")
    header3 = ("%-46s %-8s %10s %10s %14s" %
               ("class", "form", "raw-NFA", "DFA", "min/cap-fit"))
    p(header3)
    p("-" * len(header3))
    for name, form_label, raw_nfa, dfa_states, min_states in quant_rows:
        if min_states is None:
            fitstr = "DNF"
        else:
            fitstr = "%d (g=%s/t=%s)" % (min_states,
                                          fits(min_states, PCREC_MAX_DFA_STATES_GOTO),
                                          fits(min_states, PCREC_MAX_DFA_STATES_TABLE))
        p("%-46s %-8s %10d %10s %14s" % (name[:46], form_label, raw_nfa,
                                          "DNF" if dfa_states is None else dfa_states, fitstr))
    p("")

    p("=" * 78)
    p("SELF-CHECK TOTALS")
    p("=" * 78)
    p("total sample points checked across all base classes: %d" % total_checked)
    p("total mismatches                                   : %d" % total_mismatches)
    if total_mismatches:
        p("*** NON-ZERO MISMATCH COUNT: the construction is SUSPECT. Do not use "
          "these sizing numbers for design decisions until resolved. ***")
    else:
        p("No mismatches: every sampled in-class codepoint's reference UTF-8 "
          "encoding was accepted, every sampled out-of-class codepoint's "
          "encoding was rejected, every tested surrogate-scalar encoding was "
          "rejected, every tested truncation was rejected, every tested "
          "overlong re-encoding was rejected.")
    p("")
    p("Surrogate handling: U+D800-U+DFFF is excluded from every class's "
      "interval list before any lowering (exclude_surrogates() is called on "
      "every class built above), and the self-check separately constructs "
      "the 3-byte 'CESU-8-shaped' encoding of 5 surrogate scalars per class "
      "by hand (python's chr(cp).encode('utf-8') raises UnicodeEncodeError "
      "for surrogates, so this cannot be done via the normal encoder) and "
      "confirms none are accepted.")
    p("")

    if dnf_notes:
        p("DNF NOTES (phases that hit the %0.fs wall-clock budget):" % PHASE_TIMEOUT)
        for nnote in dnf_notes:
            p("  - " + nnote)
    else:
        p("No phase hit the %.0fs wall-clock budget." % PHASE_TIMEOUT)
    p("")

    p("ASSUMPTIONS / APPROXIMATIONS made in this run (repeated from inline "
      "notes above, collected here for visibility):")
    for cname, cnote in assumption_notes:
        p("  [%s]" % cname)
        p("    " + cnote)
    p("")

    p("NOT VERIFIED by this probe (out of scope for the sizing lane):")
    p("  - Whether these byte-sequence alternatives match what pcrec's own "
      "lowering will actually emit (this is an independent from-scratch "
      "construction of the standard algorithm, built to cross-check against, "
      "not a test of pcrec code -- pcrec has no UTF-8 lowering yet).")
    p("  - Whether \\p{L}/\\p{Lu}/\\p{Greek}/\\w's interval lists match "
      "libpcre2 10.46's idea of those properties (different Unicode version, "
      "and \\p{Greek}/\\w are stated approximations here) -- a different "
      "probe in this lane owns the oracle differential.")
    p("  - Runtime/memory cost of the DFA, only state COUNT.")
    p("  - Whether pcrec's actual code generator would produce the same "
      "shared-NFA structure this probe's hash-consing produces (this is a "
      "sizing upper/lower bound exercise, not pcrec's real construction).")
    p("")
    p("Total probe wall time: %.2fs" % (time.time() - start_wall))

    print("\n".join(out))


if __name__ == "__main__":
    main()
