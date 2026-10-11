#!/usr/bin/env python3
"""mk_split.py PATTERN.rx OUTDIR — [OPT-ATTEMPT-SPLIT]'s EXACT hand-twin input
for a pattern whose LAST top-level arm is the only one with `^` (concat-sqli).
Writes OUTDIR/u.rx (the other arms, unanchored) and OUTDIR/a.rx (`(?i)` +
the `^` arm). split_rx.c composes them: leftmost-first, the `^` arm has the
lowest priority and can only start at offset 0 (no (?m)), so the answer is
u's match unless u has none starting at 0 and a matches at 0."""
import sys, os
p = open(sys.argv[1], "rb").read().rstrip(b"\n")
assert p.startswith(b"(?i)")
body = p[4:]
# split the body at top-level '|' (depth 0, outside [...] and escapes)
arms, depth, cls, esc, cur = [], 0, False, False, b""
for c in body:
    ch = bytes([c])
    if esc: cur += ch; esc = False; continue
    if ch == b"\\": cur += ch; esc = True; continue
    if cls:
        cur += ch
        if ch == b"]": cls = False
        continue
    if ch == b"[": cls = True
    elif ch == b"(": depth += 1
    elif ch == b")": depth -= 1
    if ch == b"|" and depth == 0: arms.append(cur); cur = b""; continue
    cur += ch
arms.append(cur)
caret = [i for i, a in enumerate(arms) if a.startswith(b"^")]
assert caret == [len(arms) - 1], ("the ^ arm must be the last and only one", caret, len(arms))
assert all(b"^" not in a.replace(b"[^", b"") for a in arms[:-1]), "a ^ outside the last arm"
os.makedirs(sys.argv[2], exist_ok=True)
open(os.path.join(sys.argv[2], "u.rx"), "wb").write(b"(?i)" + b"|".join(arms[:-1]))
open(os.path.join(sys.argv[2], "a.rx"), "wb").write(b"(?i)" + arms[-1])
print("arms", len(arms), "u", len(b"|".join(arms[:-1])), "a", len(arms[-1]))
