#!/usr/bin/env python3
"""vlbrev3 candidate-sequence check, UTF-8, byte level, EXHAUSTIVE.

Question: on every subject (well-formed or not), every cursor and every
[lo, hi], does the cursor-rung spelling (rev 3 §5.1) try exactly the same
candidate start positions, in the same order, as rev 2's counter-rung loop?
If it does, both run the same body from the same states and the answers are
equal (the frame/trail half of the argument is in the design note).

Both loops call literal Python ports of the emitted encoding text:
  back_step  src/enc/enc_utf8.c, entry 4 (u8_defs_back_step), line by line
  advance    src/enc/enc_utf8.c, advance_utf8 (the K49 retry step), with
             @N bound to the CURSOR (rev 3) or to the subject length (the
             variant this check refutes)

Loops:
  counter    rev 2 §5.1: D = min(hi, POS); per try back_step(POS, D); NONE
             pops to L_adv; exhausted at D == lo. Work = sum of D over tries.
  cursor     rev 3 §5.1: LO = back_step(POS, lo) (NONE: branch skipped);
             K = min(hi - lo, LO); far = back_step(LO, K), retried with
             K - 1 on NONE; then from far, one advance per retry, bounded
             by POS; exhausted when the popped candidate is LO.
             Work = lo + sum of K over far tries + advances.
Variants (each expected to DIFFER somewhere, else the check could not fail):
  unbounded  cursor with the advance bounded by the subject length
  none0      cursor with a NONE far step mapped to position 0, no retry
  noretry    cursor with a NONE far step mapped to LO (no retry)

Usage: candidates.py   (prints the tallies and the first differing cells)
"""
import itertools, sys

NONE = None


def back_step(s, pos, k):
    while k > 0:
        k -= 1
        end = pos
        if pos == 0:
            return NONE
        while True:                                  # do { pos--; } while (...)
            pos -= 1
            if not (pos > 0 and (s[pos] & 0xC0) == 0x80 and end - pos < 4):
                break
        lead = s[pos]
        if lead < 0x80: want = 1
        elif (lead & 0xE0) == 0xC0: want = 2
        elif (lead & 0xF0) == 0xE0: want = 3
        elif (lead & 0xF8) == 0xF0: want = 4
        else: return NONE
        if want != end - pos:
            return NONE
    return pos


def advance(s, p, n):
    p += 1
    while p < n and (s[p] & 0xC0) == 0x80:
        p += 1
    return p


def counter(s, POS, lo, hi):
    if POS < lo: return [], 0                        # the guard (bytes)
    out, work, D = [], 0, min(hi, POS)
    while True:
        work += D
        q = back_step(s, POS, D)
        if q is not NONE: out.append(q)
        if D == lo: return out, work
        D -= 1


def cursor(s, POS, lo, hi, variant=None):
    if POS < lo: return [], 0
    work = lo
    LO = back_step(s, POS, lo)
    if LO is NONE: return [], work
    K = min(hi - lo, LO)
    while True:
        work += K
        p = back_step(s, LO, K)
        if p is not NONE: break
        if variant == "none0": p = 0; break
        if variant == "noretry": p = LO; break
        K -= 1
        assert K >= 0
    bound = len(s) if variant == "unbounded" else POS
    out, steps = [], 0
    while True:
        out.append(p)
        if p == LO: return out, work
        p = advance(s, p, bound)
        work += 1
        steps += 1
        if steps > len(s) + 8: return out + ["RUNAWAY"], work


def subjects():
    full = [0x61, 0xC3, 0xA9, 0xE2, 0x82, 0xF0, 0x9F, 0xFF]   # a, 2/3/4-byte leads, continuations, 0xFF
    small = [0x61, 0xC3, 0xA9, 0xE2, 0x82]
    for n in range(6):
        for t in itertools.product(full, repeat=n): yield bytes(t)
    for n in (6, 7):
        for t in itertools.product(small, repeat=n): yield bytes(t)


def main():
    RANGES = [(lo, hi) for lo in range(3) for hi in range(lo + 1, 5)]
    tally = {"cells": 0, "cursor": 0, "unbounded": 0, "none0": 0, "noretry": 0,
             "monotone_violations": 0, "work_cursor_gt_counter": 0}
    examples = {}
    nsubj = 0
    for s in subjects():
        nsubj += 1
        for POS in range(len(s) + 1):
            # back_step's NONE is monotone in k (the cursor loop's premise)
            seen_none = False
            for k in range(6):
                r = back_step(s, POS, k)
                if r is NONE: seen_none = True
                elif seen_none: tally["monotone_violations"] += 1
            for lo, hi in RANGES:
                tally["cells"] += 1
                ref, wref = counter(s, POS, lo, hi)
                got, wgot = cursor(s, POS, lo, hi)
                if got != ref:
                    tally["cursor"] += 1
                    examples.setdefault("cursor", (s.hex(), POS, lo, hi, ref, got))
                if wgot > wref:
                    tally["work_cursor_gt_counter"] += 1
                    examples.setdefault("work", (s.hex(), POS, lo, hi, wref, wgot))
                for v in ("unbounded", "none0", "noretry"):
                    vg, _ = cursor(s, POS, lo, hi, v)
                    if vg != ref:
                        tally[v] += 1
                        examples.setdefault(v, (s.hex(), POS, lo, hi, ref, vg))
    print("subjects: %d; cells (subject x cursor x [lo,hi] in %s): %d"
          % (nsubj, RANGES, tally["cells"]))
    print("back_step NONE monotone in k: violations %d" % tally["monotone_violations"])
    print("cursor candidate sequence differs from counter: %d" % tally["cursor"])
    print("cursor work above counter work: %d" % tally["work_cursor_gt_counter"])
    for v in ("unbounded", "none0", "noretry"):
        print("variant %-9s differs: %d" % (v, tally[v]))
    for k, e in sorted(examples.items()):
        print("first %-9s cell: subject=%s POS=%d lo=%d hi=%d counter/ref=%s got=%s" % ((k,) + e))


if __name__ == "__main__":
    main()
