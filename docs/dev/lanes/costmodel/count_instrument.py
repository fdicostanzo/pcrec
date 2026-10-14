#!/usr/bin/env python3
"""r17loss: count, never time. Patch an R17-b `new` artifact so its one
pf_terms_mask site reports uses, skipped bytes, block (mask) evaluations
and cold (first-in-activation) uses.  usage: instrument.py in.c out.c"""
import re, sys
src = open(sys.argv[1]).read().split("\n")
out = []
i = 0
stem = None
def body_end(k):
    while src[k] != "}":
        k += 1
    return k
while i < len(src):
    line = src[i]
    m = re.match(r"static inline unsigned long long (\w+)__mask\(const unsigned char \*p\)", line)
    if m:
        stem = m.group(1)
        e = body_end(i)
        out += src[i:e + 1]
        out += ["unsigned long long r17l_masks;",
                f"static inline unsigned long long r17l_mask(const unsigned char *p) {{ r17l_masks++; return {stem}__mask(p); }}",
                f"#define {stem}__mask r17l_mask"]
        i = e + 1
        continue
    m = re.match(r"static inline size_t (\w+)__next_candidate\(struct \w+ \*c, size_t lo\)", line)
    if m:
        e = body_end(i)
        out += src[i:e + 1]
        out += ["unsigned long long r17l_uses, r17l_skip, r17l_zero, r17l_cold, r17l_cached, r17l_skip_cold;",
                f"static inline size_t r17l_nc(struct {stem}__c *c, size_t lo) {{",
                "    unsigned long long m0 = r17l_masks; int cold = c->top == 0;",
                f"    size_t r = {stem}__next_candidate(c, lo);",
                "    r17l_uses++; r17l_skip += r - lo; r17l_zero += r == lo; r17l_cold += cold;",
                "    if (cold) r17l_skip_cold += r - lo;",
                "    r17l_cached += r17l_masks == m0; return r; }",
                f"#define {stem}__next_candidate r17l_nc"]
        i = e + 1
        continue
    out.append(line)
    i += 1
assert stem, "no site"
open(sys.argv[2], "w").write("\n".join(out))
