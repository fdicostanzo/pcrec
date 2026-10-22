#!/usr/bin/env python3
"""adatwin/mkarms.py -- hand twins of the ADAPTIVE per-64-byte-stretch candidate loop (lane adatwin, measurement only).

  mkarms.py V1_ART_C WALK_ART_C ARM [PLANT] > art.c      ARM in OBS ADAPT ADAPTC ADAPT1C

Built on lane flat's M64 (flat/mkarms.py, imported: its 64-byte stretch mask `mask64`, its tail `tail64`, its
V1-locating logic). Only the cursor struct, `<stem>__next_candidate`, and the cursor's init line change; the member
mask, `<stem>__member`, the DFA and the call site are V1's, byte for byte. The producer contract is V1's.

The adaptive producer holds a MODE per stretch: M (consume the stretch's 64-bit member mask with ctz/blsr, M64's
loop) or W (walk the stretch byte by byte through the walk's own start-byte table, copied here as `<stem>__walk`).
Every non-empty stretch read as a mask feeds the RULE, which sets the mode of the following stretches:
  R2 (adasim (kc, b, h) = (2, 33, 12)): M if k <= 2 or t >= 33; W if k > 14 and t < 21; else unchanged
  R1 (adasim (a, b, h) = (1, 31, 8)):   M if t <= 1 or t >= 31;  W if 9 < t < 23;       else unchanged
with k = popcount(m) (members) and t = popcount(m ^ (m >> 1)) (transitions); an empty stretch is M. In W mode
every 16th stretch entered is read as a mask instead (the SAMPLE, adasim's "every 16th W stretch"): that is the
only way back to M. popcount is SWAR (the slot builds for baseline x86-64: no popcnt instruction; the builtin
would be a libgcc call).

  OBS      M64 plus the observation: every non-empty stretch computes k, t and R2's decision, which is kept in a
           register (an empty asm) and never acted on. OBS - M64 = ob, the observation cost.
  ADAPT    R2, the mode carried WITHIN one rx_search call; a call starts in M (its first stretch is a sample).
  ADAPTC   R2, the mode CARRIED ACROSS calls in a small per-subject state (`<stem>__carry`, file scope: the
           driver's future batch/iterator state, simulated; re-bound when (s, n) change or `from` goes back).
           A call starts in the carried mode, or in W when the previous call spanned < 64 bytes (from - the
           previous call's from): adasim's short-call reset.
  ADAPT1C  R1, carried as ADAPTC.

PLANT (off-by-ones the battery must catch): `sw` = at a mode change the stretch's FIRST candidate is skipped (the
switch returns m & (m - 1)'s lowest bit); `wlo` = a W-mode re-entry inside a stretch starts its walk at lo + 1.
-DADAPT_COUNT adds counters (stretches by mode, switches each way) printed to stderr at exit.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flat"))
import mkarms as flat  # noqa: E402  (flat's STRETCH: mask64 + tail64)

POP = """static inline unsigned rx_search_pf__pop(unsigned long long x)   /* SWAR popcount (no popcnt on the target) */
{
    x -= (x >> 1) & 0x5555555555555555ULL;
    x = (x & 0x3333333333333333ULL) + ((x >> 2) & 0x3333333333333333ULL);
    x = (x + (x >> 4)) & 0x0f0f0f0f0f0f0f0fULL;
    return (unsigned)((x * 0x0101010101010101ULL) >> 56);
}
"""

RULES = {
    "R2": """static inline unsigned rx_search_pf__rule(unsigned mode, unsigned long long m)   /* R2; 0 = M, 1 = W */
{
    unsigned k = rx_search_pf__pop(m), t = rx_search_pf__pop(m ^ (m >> 1));
    if (k <= 2 || t >= 33) return 0;
    if (k > 14 && t < 21) return 1;
    return mode;
}
""",
    "R1": """static inline unsigned rx_search_pf__rule(unsigned mode, unsigned long long m)   /* R1; 0 = M, 1 = W */
{
    unsigned t = rx_search_pf__pop(m ^ (m >> 1));
    if (t <= 1 || t >= 31) return 0;
    if (t > 9 && t < 23) return 1;
    return mode;
}
""",
}

COUNT = """#ifdef ADAPT_COUNT
#include <stdio.h>
static unsigned long rx_search_pf__cnt_m, rx_search_pf__cnt_w, rx_search_pf__cnt_mw, rx_search_pf__cnt_wm;
__attribute__((destructor)) static void rx_search_pf__cnt_print(void)
{
    fprintf(stderr, "adapt: mask_stretches=%lu walk_stretches=%lu switch_mw=%lu switch_wm=%lu\\n",
            rx_search_pf__cnt_m, rx_search_pf__cnt_w, rx_search_pf__cnt_mw, rx_search_pf__cnt_wm);
}
# define ADAPT_CNT(x) (x++)
#else
# define ADAPT_CNT(x) ((void)0)
#endif
"""

CARRY = """static struct { const unsigned char *s; size_t n, from; unsigned mode; } rx_search_pf__carry;   /* ADAPTC */
"""

ADAPT = """struct rx_search_pf__c {
    const unsigned char *s;
    size_t n;
    size_t base, top;          /* the current stretch [base, top) */
    unsigned long long m;      /* M: its candidates not yet returned */
    unsigned mode, cnt;        /* mode of the following stretches (0 = M, 1 = W); W stretches entered */
};
static inline size_t rx_search_pf__next_candidate(struct rx_search_pf__c *c, size_t lo)
{
    const unsigned char *s = c->s;
    size_t hi = c->n - 1;
    size_t i = lo;
    unsigned long long m;
    if ((size_t)(lo - c->base) < (size_t)(c->top - c->base)) {
        if (!c->mode) {
            m = c->m & (~0ULL << (lo - c->base));
            if (m) {
                c->m = m & (m - 1);
                return c->base + (unsigned)__builtin_ctzll(m);
            }
        } else {
            for (i = lo@WLO@; i < c->top; i++)
                if (rx_search_pf__walk[s[i]]) return i;
        }
        i = c->top;
    }
    if (c->mode && ++c->cnt & 15) {           /* W: walk the next stretch (every 16th is a sample, below) */
        for (;;) {
            if (i >= hi) return hi;
            ADAPT_CNT(rx_search_pf__cnt_w);
            c->base = i;
            c->top = i + 64 < hi ? i + 64 : hi;
            for (; i < c->top; i++)
                if (rx_search_pf__walk[s[i]]) return i;
            if (!(++c->cnt & 15)) break;
        }
    }
    size_t i0 = i;                            /* M, or a W sample: M64's stretch */
    for (m = 0; i + 64 <= hi; i += 64)
        if ((m = rx_search_pf__mask64(s + i))) break;
    if (i >= hi) return hi;
    if (i + 64 <= hi) {
        c->top = i + 64;
    } else {
        m = rx_search_pf__tail64(s, i, hi);
        c->top = hi;
    }
    c->base = i;
    if (!m) return hi;
    ADAPT_CNT(rx_search_pf__cnt_m);
    {
        unsigned old = i != i0 ? 0 : c->mode, mode = rx_search_pf__rule(old, m);
#ifdef ADAPT_COUNT
        if (mode != c->mode) { if (mode) rx_search_pf__cnt_mw++; else rx_search_pf__cnt_wm++; }
#endif
        @SWITCH@
        c->mode = mode;
        @SAVE@
    }
    c->m = m & (m - 1);
    return i + (unsigned)__builtin_ctzll(m);
}
"""

OBS = """struct rx_search_pf__c {
    const unsigned char *s;
    size_t n;
    size_t base, top;
    unsigned long long m;
    unsigned mode;             /* R2's decision, computed and never acted on */
};
static inline size_t rx_search_pf__next_candidate(struct rx_search_pf__c *c, size_t lo)
{
    const unsigned char *s = c->s;
    size_t hi = c->n - 1;
    size_t i = lo;
    unsigned long long m;
    if ((size_t)(lo - c->base) < (size_t)(c->top - c->base)) {
        m = c->m & (~0ULL << (lo - c->base));
        if (m) {
            c->m = m & (m - 1);
            return c->base + (unsigned)__builtin_ctzll(m);
        }
        i = c->top;
    }
    size_t i0 = i;
    for (m = 0; i + 64 <= hi; i += 64)
        if ((m = rx_search_pf__mask64(s + i))) break;
    if (i >= hi) return hi;
    if (i + 64 <= hi) {
        c->top = i + 64;
    } else {
        m = rx_search_pf__tail64(s, i, hi);
        c->top = hi;
    }
    c->base = i;
    if (!m) return hi;
    c->mode = rx_search_pf__rule(i != i0 ? 0 : c->mode, m);
    __asm__ volatile("" :: "r"(c->mode));
    c->m = m & (m - 1);
    return i + (unsigned)__builtin_ctzll(m);
}
"""

INIT_OWN = ("struct rx_search_pf__c rx_search_pf__c; rx_search_pf__c.s = subject; rx_search_pf__c.n = subject_length; "
            "rx_search_pf__c.base = rx_search_pf__c.top = 0; rx_search_pf__c.m = 0; rx_search_pf__c.mode = 0; "
            "rx_search_pf__c.cnt = 0;")
INIT_OBS = ("struct rx_search_pf__c rx_search_pf__c; rx_search_pf__c.s = subject; rx_search_pf__c.n = subject_length; "
            "rx_search_pf__c.base = rx_search_pf__c.top = 0; rx_search_pf__c.m = 0; rx_search_pf__c.mode = 0;")
INIT_CARRY = ("if (rx_search_pf__carry.s != subject || rx_search_pf__carry.n != subject_length || "
              "search_from < rx_search_pf__carry.from) { rx_search_pf__carry.s = subject; "
              "rx_search_pf__carry.n = subject_length; rx_search_pf__carry.mode = 0; } "
              "else if (search_from - rx_search_pf__carry.from < 64) rx_search_pf__carry.mode = 1; "
              "rx_search_pf__carry.from = search_from; " + INIT_OWN.replace(
                  "rx_search_pf__c.mode = 0;", "rx_search_pf__c.mode = rx_search_pf__carry.mode;"))

ARMS = {"OBS": ("R2", False), "ADAPT": ("R2", False), "ADAPTC": ("R2", True), "ADAPT1C": ("R1", True)}


def walk_table(walk_src):
    tab = re.findall(r"!(\w+)\[subject\[scan_position\]\]\) scan_position\+\+;", walk_src)
    assert len(tab) == 1, tab
    m = re.search(r"%s\[256\] = \{(.*?)\};" % tab[0], walk_src, re.S)
    v = [int(x) for x in m.group(1).replace("\n", " ").split(",") if x.strip()]
    assert len(v) == 256 and set(v) <= {0, 1}
    rows = ",\n".join("    " + ", ".join(str(x) for x in v[r:r + 16]) for r in range(0, 256, 16))
    return "static const unsigned char rx_search_pf__walk[256] = {   /* the walk's start-byte table */\n%s\n};\n" % rows


def main():
    src, wsrc, arm = open(sys.argv[1]).read(), open(sys.argv[2]).read(), sys.argv[3]
    plant = sys.argv[4] if len(sys.argv) > 4 else ""
    rule, carry = ARMS[arm]
    if plant not in ("", "sw", "wlo") or (plant and arm == "OBS"):
        sys.exit("mkarms: no plant %r for %s" % (plant, arm))
    body = flat.STRETCH.replace("@TAIL@", "") + POP + RULES[rule]
    if arm == "OBS":
        body += OBS
        init = INIT_OBS
    else:
        body += walk_table(wsrc) + COUNT + (CARRY if carry else "") + ADAPT
        body = body.replace("@WLO@", " + 1" if plant == "wlo" else "")
        body = body.replace("@SWITCH@", "if (mode != c->mode) m &= m - 1;   /* PLANT sw */" if plant == "sw" else "")
        body = body.replace("@SAVE@", "rx_search_pf__carry.mode = mode;" if carry else "")
        init = INIT_CARRY if carry else INIT_OWN
    st = re.search(r"^struct (\w+)__c \{$", src, re.M)
    if not st:
        sys.exit("mkarms: no cursor struct")
    stem = st.group(1)
    pat = re.compile(r"^struct %s__c \{\n.*?^static inline size_t %s__next_candidate\(.*?^\}\n" % (stem, stem),
                     re.S | re.M)
    keep = re.compile(r"^static inline (unsigned long long %s__mask|int %s__member)\(.*?^\}\n" % (stem, stem),
                      re.S | re.M)
    m = pat.search(src)
    if not m or src.count("%s__next_candidate(" % stem) != 2:
        sys.exit("mkarms: V1 producer not found (or not exactly one call site)")
    hi = re.search(r"size_t hi = (c->n(?: - 1)?);", m.group(0))
    if not hi:
        sys.exit("mkarms: V1's top bound not found")
    body = body.replace("c->n - 1;", hi.group(1) + ";").replace("rx_search_pf", stem)
    helpers = "".join(k.group(0) for k in keep.finditer(m.group(0)))
    if helpers.count("static inline") != 2:
        sys.exit("mkarms: mask/member helpers not found inside the V1 producer block")
    out = src[:m.start()] + helpers + body + src[m.end():]
    old = "struct %s__c %s__c = { subject, subject_length, 0, 0, 0 };" % (stem, stem)
    if out.count(old) != 1:
        sys.exit("mkarms: cursor init line not found exactly once")
    sys.stdout.write(out.replace(old, init.replace("rx_search_pf", stem)))


if __name__ == "__main__":
    main()
