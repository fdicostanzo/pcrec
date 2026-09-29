#!/usr/bin/env python3
# tests/clskit/ref/wholeset.py — FROZEN COPY of studies/cls_tree_study/wholeset.py
# at commit 5aca6c93aa6b9ff0bd09fbbc60e4113ad798caff, copied 2026-09-29 (lane clss1b). One of the six modules tests/clskit imports.
#
# WHY A COPY. docs/CLAUDE.md: studies/ is "never built or tested by
# pcrec's make"; tests/clskit/ imports these modules as the reference
# src/gen/clskit.c is cross-checked against (design cls_tree_design.md §6's S1 row), which
# makes them a load-bearing part of `make test` and not merely study
# code any more — so `make test` cannot reach into studies/ live. This
# file is the FROZEN reference tests/clskit/ compares clskit.c against;
# edit it with the same care as a test oracle (crosscheck.py's own
# header says so). To pick up a real change from the study, re-copy from
# studies/cls_tree_study/ by hand (never patch this file to differ from
# its source) and update this header's commit.
#
# THE ONE DEVIATION FROM THE SOURCE: path arithmetic. This directory is
# one level deeper than studies/cls_tree_study/ (tests/clskit/ref/ vs.
# studies/cls_tree_study/), so any HERE-relative path this file computes
# was re-derived for its new depth — see clsets.py's own note. Nothing
# else in this file's text was touched.
"""wholeset.py — WHOLE-SET indexed tables: the forms the study's DP could not
reach, added for the [CLS-TREE] design note's owed timing arm (lane clsdes88,
2026-09-28; docs/design/cls_tree_design.md §1.3, §7).

WHY THESE EXIST.  `section.py` caps a section at MAXK = 64 intervals, so no
sectioning of a 677-931-interval set can ever be ONE table: the λ=∞ policy
for `\\p{L}` is 11 BITMAP sections behind an 11-leaf dispatch tree.  The
ubuntubudu ns/char run (results/bench_ubuntubudu_20260911.tsv) then measured
`bitmap1` — one bitmap over the whole span, NO dispatch — at 3-6x faster
than every kit policy, while the kit policies were indistinguishable from
each other.  The dispatch tree, not the leaf, is where the time goes; a
whole-set table is the form that has none.  `bitmap1` is too big for most
sets (25.7-139 KB); the indexed forms below are the same idea at kit size.

  PageW2   PCRE2's two-stage shape over the whole set: idx[cp>>6] -> a
           deduplicated 64-bit leaf.  = kit.FormPage64 over ONE section.
  PageW3   three stages: top[cp>>TS] -> a deduplicated block of 2^(TS-6)
           page indices -> a deduplicated 64-bit leaf.  TS = 10 is the
           size-minimal choice over the K53 twelve (4.2-5.6 KB rodata).

Both are BRANCH-FREE after the one global bound test, and both take a bare
interval list and nothing else (CONSTITUTIONAL CONSTRAINT 1, as kit.py).
They are deliberately NOT added to kit.KIT: the committed sweeps must stay
reproducible, and whether the DP should offer whole-set sections at all is
the design note's decision, gated on this timing.  Study code — never the
compiler.
"""


def _page_masks(iv):
    last = iv[-1][1]
    npages = (last >> 6) + 1
    masks = [0] * npages
    for lo, hi in iv:
        for p in range(lo >> 6, (hi >> 6) + 1):
            a, b = max(lo, p << 6), min(hi, (p << 6) + 63)
            masks[p] |= ((1 << (b - a + 1)) - 1) << (a - (p << 6))
    return masks


def _dedup(seq):
    uniq, idx = {}, []
    for v in seq:
        idx.append(uniq.setdefault(v, len(uniq)))
    return [k for k, _ in sorted(uniq.items(), key=lambda kv: kv[1])], idx


def _cty(n):
    return "unsigned char" if n <= 256 else "unsigned short"


class PageW2:
    def __init__(self, iv):
        self.lo, self.hi = iv[0][0], iv[-1][1]
        self.leaves, self.idx = _dedup(_page_masks(iv))

    def rodata(self):
        w = 1 if len(self.leaves) <= 256 else 2
        return len(self.idx) * w + 8 * len(self.leaves)

    def c(self, fn):
        return ("static const %s %s_i[%d] = { %s };\n"
                "static const unsigned long long %s_l[%d] = { %s };\n"
                "int %s(unsigned cp)\n{\n"
                "    if ((unsigned)(cp - %uu) > %uu) return 0;\n"
                "    return (int)((%s_l[%s_i[cp >> 6]] >> (cp & 63)) & 1u);\n"
                "}\n"
                % (_cty(len(self.leaves)), fn, len(self.idx),
                   ", ".join(map(str, self.idx)),
                   fn, len(self.leaves),
                   ", ".join("0x%016XULL" % v for v in self.leaves),
                   fn, self.lo, self.hi - self.lo, fn, fn))


class PageW3:
    def __init__(self, iv, ts=10):
        self.lo, self.hi, self.ts = iv[0][0], iv[-1][1], ts
        self.leaves, pidx = _dedup(_page_masks(iv))
        bs = 1 << (ts - 6)
        pidx = pidx + [pidx[-1]] * (-len(pidx) % bs)   # pad the last block
        blocks = [tuple(pidx[i:i + bs]) for i in range(0, len(pidx), bs)]
        self.blocks, self.top = _dedup(blocks)
        self.bs = bs

    def rodata(self):
        lw = 1 if len(self.leaves) <= 256 else 2
        bw = 1 if len(self.blocks) <= 256 else 2
        return (len(self.top) * bw + len(self.blocks) * self.bs * lw
                + 8 * len(self.leaves))

    def c(self, fn):
        mid = [v for blk in self.blocks for v in blk]
        return ("static const %s %s_t[%d] = { %s };\n"
                "static const %s %s_m[%d] = { %s };\n"
                "static const unsigned long long %s_l[%d] = { %s };\n"
                "int %s(unsigned cp)\n{\n"
                "    if ((unsigned)(cp - %uu) > %uu) return 0;\n"
                "    return (int)((%s_l[%s_m[(%s_t[cp >> %d] << %d)"
                " | ((cp >> 6) & %uu)]] >> (cp & 63)) & 1u);\n"
                "}\n"
                % (_cty(len(self.blocks)), fn, len(self.top),
                   ", ".join(map(str, self.top)),
                   _cty(len(self.leaves)), fn, len(mid),
                   ", ".join(map(str, mid)),
                   fn, len(self.leaves),
                   ", ".join("0x%016XULL" % v for v in self.leaves),
                   fn, self.lo, self.hi - self.lo,
                   fn, fn, fn, self.ts, self.ts - 6, self.bs - 1))


def main():
    """`python3 wholeset.py [population]` — the stage-width sweep behind the
    design note's TS = 10 (§1.3): PageW3 rodata at TS in {10, 12, 14} per set.
    Sizes only; exhaustive answers are verify_whole.py's (at TS = 10)."""
    import sys
    import clsets
    which = sys.argv[1] if len(sys.argv) > 1 else "k53"
    print("set\tintervals\tts10_rodata\tts12_rodata\tts14_rodata")
    for name, iv in clsets.population(which):
        print("\t".join([name, str(len(iv))] +
                        [str(PageW3(iv, ts).rodata()) for ts in (10, 12, 14)]))


if __name__ == "__main__":
    main()
