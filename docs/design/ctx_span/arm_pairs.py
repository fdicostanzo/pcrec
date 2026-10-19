#!/usr/bin/env python3
"""docs/design/ctx_span/arm_pairs.py -- ctx_span.md rev 2 §4.6's extension census
instrument. For every CODE line under src/ naming one of KINDS (default A_BOL A_END
N_BOT N_END), print the line and, inside the same switch statement (found by brace
depth from the nearest enclosing `switch (`), the line that labels A_CTX / N_CTX, so a
reader can compare the two arms. Read-only; a reading aid, not a classifier: the
classification (deleted / generic / still special) is ctx_span.md §4.6's, by hand,
per site. Usage: python3 -I arm_pairs.py ROOT [KIND...]"""
import os, re, sys
root = sys.argv[1]
kinds = sys.argv[2:] or ["A_BOL", "A_END", "N_BOT", "N_END"]
kre = re.compile(r"\b(" + "|".join(kinds) + r")\b")
ctx = re.compile(r"\b(A_CTX|N_CTX)\b")
comment = re.compile(r"^\s*(/?\*|//)")
for d, _, fs in os.walk(os.path.join(root, "src")):
    for f in sorted(fs):
        if not f.endswith((".c", ".h", ".def")):
            continue
        p = os.path.join(d, f)
        L = open(p, encoding="latin-1").read().split("\n")
        for i, l in enumerate(L):
            if not kre.search(l) or comment.match(l):
                continue
            # nearest enclosing switch: walk up tracking brace depth
            depth, j = 0, i
            while j >= 0:
                depth += L[j].count("}") - L[j].count("{")
                if depth < 0 and "switch" in L[j]:
                    break
                if depth < 0:
                    depth = 0 if "switch" not in L[j] else depth
                j -= 1
            sw = j
            # scan the switch body for the A_CTX label
            k, dep, hit = sw, 0, None
            while 0 <= k < len(L):
                dep += L[k].count("{") - L[k].count("}")
                if k > sw and ctx.search(L[k]) and not comment.match(L[k]):
                    hit = k
                    break
                if k > sw and dep <= 0:
                    break
                k += 1
            rel = os.path.relpath(p, root)
            print(f"{rel}:{i+1}\t{l.strip()[:110]}")
            print(f"    switch {sw+1 if sw >= 0 else '?'}; ctx-arm "
                  + (f"{hit+1}: {L[hit].strip()[:100]}" if hit is not None else "NONE in this switch"))
