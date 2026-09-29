#!/usr/bin/env python3
"""automaton.py — the UTF-8 BYTE AUTOMATON of a code-point set, three ways,
for the [CLS-TREE] design note's DFA seam (docs/design/cls_tree_design.md §3;
lane clsdes88, 2026-09-28).

  flat      what `src/opt/lower_enc.c` builds TODAY: one alternation branch
            per `u8_box` box, each branch a chain of byte-range classes.
            `u8_box`/`u8_ranges` are transcribed here line for line.
  fwd       the MINIMAL acyclic automaton of the set's encodings, forward:
            a trie over the same boxes, hash-consed bottom-up, parallel
            edges to one target merged into one byte-SET edge (an NFA class
            state holds a set, not a range).
  rev       the same for the REVERSED encodings, built EXACTLY over bytes
            (every member enumerated): reversed box labels overlap without
            being equal, so a range-labelled reverse trie is not minimal.

"root fan-out" is how many class states an epsilon-closure reaches on
ENTERING the class — the quantity K67's per-loop-boundary closure re-walk
multiplies (docs/dev/known_issues.md K67 cause 2).

    python3 automaton.py [population] [--exact-rev]   (default k53)
"""
import sys

import clsets

BANDS = [(0x0, 0x7F, 1), (0x80, 0x7FF, 2), (0x800, 0xD7FF, 3),
         (0xE000, 0xFFFF, 3), (0x10000, 0x10FFFF, 4)]


def enc(c):
    if c < 0x80:
        return [c]
    if c < 0x800:
        return [0xC0 | c >> 6, 0x80 | c & 63]
    if c < 0x10000:
        return [0xE0 | c >> 12, 0x80 | (c >> 6) & 63, 0x80 | c & 63]
    return [0xF0 | c >> 18, 0x80 | (c >> 12) & 63, 0x80 | (c >> 6) & 63,
            0x80 | c & 63]


def u8_box(out, lo, hi, n):
    lb, hb = enc(lo), enc(hi)
    p = 0
    while p < n and lb[p] == hb[p]:
        p += 1
    if p == n:
        out.append(tuple((b, b) for b in lb))
        return
    lo_min = all(lb[i] == 0x80 for i in range(p + 1, n))
    hi_max = all(hb[i] == 0xBF for i in range(p + 1, n))
    if not lo_min:
        m = lo | ((1 << (6 * (n - 1 - p))) - 1)
        u8_box(out, lo, m, n)
        u8_box(out, m + 1, hi, n)
        return
    if not hi_max:
        m = hi & ~((1 << (6 * (n - 1 - p))) - 1)
        u8_box(out, lo, m - 1, n)
        u8_box(out, m, hi, n)
        return
    out.append(tuple([(lb[i], lb[i]) for i in range(p)] + [(lb[p], hb[p])]
                     + [(0x80, 0xBF)] * (n - 1 - p)))


def branches(iv):
    out = []
    for lo, hi in iv:
        for bl, bh, n in BANDS:
            l, h = max(lo, bl), min(hi, bh)
            if l <= h:
                u8_box(out, l, h, n)
    return out


def minimal(seqs):
    """(states, set-edges, root fan-out) of the hash-consed trie."""
    root = {}
    for seq in seqs:
        node = root
        for lab in seq:
            node = node.setdefault(lab, {})
    memo, nedges = {}, [0]

    def canon(node):
        tg = {}
        for lab, ch in node.items():
            tg.setdefault(canon(ch), []).append(lab)
        key = tuple(sorted((t, tuple(sorted(ls))) for t, ls in tg.items()))
        if key not in memo:
            memo[key] = len(memo)
            nedges[0] += len(key)
        return memo[key]

    r = canon(root)
    rootkey = next(k for k, v in memo.items() if v == r)
    return len(memo), nedges[0], len(rootkey)


def sink_indegree(seqs):
    """Root fan-out of the forward automaton walked BACKWARDS: the number of
    set-edges into its accepting sink (the design note's "reversed forward
    automaton" contrast row)."""
    root = {}
    for seq in seqs:
        node = root
        for lab in seq:
            node = node.setdefault(lab, {})
    memo, ind = {}, {}

    def canon(node):
        tg = {}
        for lab, ch in node.items():
            tg.setdefault(canon(ch), []).append(lab)
        key = tuple(sorted((t, tuple(sorted(ls))) for t, ls in tg.items()))
        if key not in memo:
            memo[key] = len(memo)
            for t, _ in key:
                ind[t] = ind.get(t, 0) + 1
        return memo[key]

    canon(root)
    return ind[memo[()]]


def exact_rev(iv):
    seqs = (enc(c)[::-1] for lo, hi in iv for c in range(lo, hi + 1)
            if not 0xD800 <= c <= 0xDFFF)
    return minimal(seqs)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    which = args[0] if args else "k53"
    print("set\tintervals\tflat_branches\tflat_class_nodes"
          "\tfwd_states\tfwd_set_edges\tfwd_root_fanout"
          "\trev_states\trev_set_edges\trev_root_fanout"
          "\trevfwd_root_fanout")
    for name, iv in clsets.population(which):
        br = branches(iv)
        f = minimal(br)
        r = exact_rev(iv) if "--exact-rev" in sys.argv else ("-",) * 3
        print("\t".join(map(str, (name, len(iv), len(br),
                                  sum(len(b) for b in br)) + f + tuple(r)
                             + (sink_indegree(br),))))


if __name__ == "__main__":
    main()
