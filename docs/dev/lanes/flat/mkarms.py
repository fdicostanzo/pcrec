#!/usr/bin/env python3
"""flat/mkarms.py -- hand twins of V1's candidate producer (lane flat, measurement only).

  mkarms.py V1_ART_C ARM [PLANT] > art.c      ARM in F8 F64 M64

Takes the kit compiler's V1 artifact (R17-b's `<stem>__next_candidate`: an 8-byte SWAR mask, a cached lane mask,
ctz per stop) and replaces ONLY the cursor struct, the producer and the cursor's initialisation line. Everything
else (the member mask `<stem>__mask`, `<stem>__member`, the DFA, the call site) is byte-identical to V1. The
producer contract is V1's: next_candidate(c, lo) returns the smallest member position p in [lo, n-1), else n-1;
the call site only asks with lo < n-1, and lo never decreases within one rx_search call.

  F8   per 8-byte block: the 8-bit mask is flattened through a 256-entry table of packed lane indexes into ONE word
       (one load, count from a 256-entry popcount table; no data-dependent branch); the consumer shifts entries out
       in order and skips stale ones (< lo). Tail: V1's own (the overlapping last block, lanes before the scan start cleared; bytewise below 8).
  F64  a 64-bit mask over a 64-byte stretch (eight SWAR blocks), flattened the same way, eight table stores.
       Tail (< 64 bytes left): V1's own byte tail widened: 8-byte blocks, then the overlapping last block shifted
       into place, bytewise below 8 bytes. No copy, no read past n.
  M64  F64's mask and tail, consumed with ctz/blsr instead of flattening (the control: width without flattening).

PLANT (the off-by-one sabotage the battery must catch): `stale` in F8 and F64 (the drain test p > lo instead of
p >= lo: a candidate exactly at the scan position is skipped); F64 `tail` (the bounded tail drops its last lane).
"""
import re
import sys

LANES = ",\n".join(
    "    " + ", ".join("0x%016xULL" % sum(l << (8 * k) for k, l in enumerate([b for b in range(8) if m >> b & 1]))
                       for m in range(r, r + 4)) for r in range(0, 256, 4))

CNT = ",\n".join("    " + ", ".join("%d" % bin(m).count("1") for m in range(r, r + 16)) for r in range(0, 256, 16))

# popcount and the stretch loops are spelled out, not left to the target: the baseline x86-64 has no popcnt
# (__builtin_popcountll became a libgcc call) and -O2 kept the 8-step loops rolled
COMMON = """static const unsigned long long rx_search_pf__lanes[256] = {   /* flat: lane indexes of m, ascending, packed */
%s
};
static const unsigned char rx_search_pf__cnt[256] = {   /* flat: popcount of m */
%s
};
""" % (LANES, CNT)

INIT = ("struct rx_search_pf__c rx_search_pf__c; rx_search_pf__c.s = subject; rx_search_pf__c.n = subject_length; "
        "rx_search_pf__c.base = rx_search_pf__c.top = 0; rx_search_pf__c.%s;")

F8 = COMMON + """struct rx_search_pf__c {
    const unsigned char *s;
    size_t n;
    size_t base, top;
    unsigned long long off;   /* the block's candidate lanes, packed one per byte, next one lowest */
    unsigned k;               /* entries left in off */
};
static inline void rx_search_pf__flat8(struct rx_search_pf__c *c, size_t b, unsigned long long m)
{
    c->off = rx_search_pf__lanes[m];
    c->k = rx_search_pf__cnt[m];
    c->base = b;
}
static inline size_t rx_search_pf__next_candidate(struct rx_search_pf__c *c, size_t lo)
{
    const unsigned char *s = c->s;
    size_t hi = c->n - 1;
    for (;;) {
        if (lo < c->top)
            while (c->k) {
                size_t p = c->base + (c->off & 0xff);
                c->off >>= 8;
                c->k--;
                if (p @GE@ lo) return p;
            }
        size_t i = c->top > lo ? c->top : lo;
        unsigned long long m = 0;
        for (; i + 8 <= hi; i += 8)
            if ((m = rx_search_pf__mask(s + i))) break;
        if (i >= hi) return hi;
        if (i + 8 <= hi) {
            rx_search_pf__flat8(c, i, m);
            c->top = i + 8;
        } else if (hi >= 8) {
            size_t b = hi - 8;
            rx_search_pf__flat8(c, b, rx_search_pf__mask(s + b) & (0xffULL << (i - b)) & 0xff);
            c->top = hi;
        } else {
            m = 0;
            for (size_t k = i; k < hi; k++)
                m |= (unsigned long long)rx_search_pf__member(s[k]) << k;
            rx_search_pf__flat8(c, 0, m);
            c->top = hi;
        }
    }
}
"""

STRETCH = """static inline unsigned long long rx_search_pf__mask64(const unsigned char *p)
{
    return rx_search_pf__mask(p) | rx_search_pf__mask(p + 8) << 8 | rx_search_pf__mask(p + 16) << 16
           | rx_search_pf__mask(p + 24) << 24 | rx_search_pf__mask(p + 32) << 32 | rx_search_pf__mask(p + 40) << 40
           | rx_search_pf__mask(p + 48) << 48 | rx_search_pf__mask(p + 56) << 56;
}
static inline unsigned long long rx_search_pf__tail64(const unsigned char *s, size_t i, size_t hi)   /* hi - i < 64 */
{
    unsigned long long m = 0;
    size_t k = i;
    for (; k + 8 <= hi; k += 8)
        m |= rx_search_pf__mask(s + k) << (k - i);
    if (k < hi) {
        if (hi >= 8) {
            m |= (rx_search_pf__mask(s + hi - 8) >> (8 - (hi - k))) << (k - i);
        } else {
            for (; k < hi; k++)
                m |= (unsigned long long)rx_search_pf__member(s[k]) << (k - i);
        }
    }
    return m@TAIL@;
}
"""

F64 = COMMON + STRETCH + """struct rx_search_pf__c {
    const unsigned char *s;
    size_t n;
    size_t base, top;
    unsigned h, k;
    unsigned char off[64];
};
static inline void rx_search_pf__flat64(struct rx_search_pf__c *c, size_t b, unsigned long long m)
{
    unsigned k = 0;
#define FLAT_STEP(j) { unsigned char mj = (unsigned char)(m >> (8 * j)); \
        unsigned long long w = rx_search_pf__lanes[mj] + 0x0101010101010101ULL * (8 * j); \
        __builtin_memcpy(c->off + k, &w, 8); k += rx_search_pf__cnt[mj]; }
    FLAT_STEP(0) FLAT_STEP(1) FLAT_STEP(2) FLAT_STEP(3) FLAT_STEP(4) FLAT_STEP(5) FLAT_STEP(6) FLAT_STEP(7)
#undef FLAT_STEP
    c->base = b;
    c->h = 0;
    c->k = k;
}
static inline size_t rx_search_pf__next_candidate(struct rx_search_pf__c *c, size_t lo)
{
    const unsigned char *s = c->s;
    size_t hi = c->n - 1;
    for (;;) {
        if (lo < c->top)
            while (c->h < c->k) {
                size_t p = c->base + c->off[c->h++];
                if (p @GE@ lo) return p;
            }
        size_t i = c->top > lo ? c->top : lo;
        unsigned long long m = 0;
        for (; i + 64 <= hi; i += 64)
            if ((m = rx_search_pf__mask64(s + i))) break;
        if (i >= hi) return hi;
        if (i + 64 <= hi) {
            c->top = i + 64;
        } else {
            m = rx_search_pf__tail64(s, i, hi);
            c->top = hi;
        }
        rx_search_pf__flat64(c, i, m);
    }
}
"""

M64 = STRETCH + """struct rx_search_pf__c {
    const unsigned char *s;
    size_t n;
    size_t base, top;
    unsigned long long m;
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
    c->m = m & (m - 1);
    return i + (unsigned)__builtin_ctzll(m);
}
"""

ARMS = {"F8": (F8, "k = 0"), "F64": (F64, "h = rx_search_pf__c.k = 0"),
        "M64": (M64, "m = 0")}


def main():
    src, arm = open(sys.argv[1]).read(), sys.argv[2]
    plant = sys.argv[3] if len(sys.argv) > 3 else ""
    body, init = ARMS[arm]
    body = body.replace("@GE@", ">" if plant == "stale" else ">=").replace("@TAIL@", " & ~(1ULL << (hi - 1 - i))" if plant == "tail" else "")
    if (arm, plant) not in (("F8", ""), ("F8", "stale"), ("F64", ""), ("F64", "tail"), ("F64", "stale"), ("M64", "")):
        sys.exit("mkarms: no plant %r for %s" % (plant, arm))
    # the V1 producer: from the cursor struct to the end of next_candidate (the next line that is exactly "}")
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
    # the templates are written for stem rx_search_pf and hi = n - 1 (the DFA site); the VM hybrid's site has its
    # own stem and hi = n (the last byte is a candidate too): both are V1's own values, copied
    body = body.replace("c->n - 1;", hi.group(1) + ";").replace("rx_search_pf", stem)
    init = init.replace("rx_search_pf", stem)
    helpers = "".join(k.group(0) for k in keep.finditer(m.group(0)))
    if helpers.count("static inline") != 2:
        sys.exit("mkarms: mask/member helpers not found inside the V1 producer block")
    out = src[:m.start()] + helpers + body + src[m.end():]
    old = "struct %s__c %s__c = { subject, subject_length, 0, 0, 0 };" % (stem, stem)
    if out.count(old) != 1:
        sys.exit("mkarms: cursor init line not found exactly once")
    sys.stdout.write(out.replace(old, (INIT % init).replace("rx_search_pf", stem)))


if __name__ == "__main__":
    main()
