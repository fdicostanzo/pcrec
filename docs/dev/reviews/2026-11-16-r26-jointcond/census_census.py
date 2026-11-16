#!/usr/bin/env python3
"""Census of marks over every code span of joint_condition.md (lens census).
Extracts backtick spans and 4-space indented code blocks; classifies each `(` and
each `,` `:` `=` `$` occurrence by position. Writes spans.tsv and paren.tsv; prints counts."""
import re, sys, collections, os

SRC = sys.argv[1]
OUT = sys.argv[2]
lines = open(SRC, encoding="utf-8").read().split("\n")

spans = []  # (lineno, kind, text)
for i, ln in enumerate(lines, 1):
    if ln.startswith("    ") and not ln.lstrip().startswith(("|", "-")) and (i == 1 or lines[i-2].strip() == "" or lines[i-2].startswith("    ")):
        txt = ln.strip()
        if txt:
            # strip trailing comment
            code = re.split(r"\s#\s", txt, maxsplit=1)[0]
            spans.append((i, "block", code))
        continue
    for m in re.finditer(r"`([^`]+)`", ln):
        spans.append((i, "tick", m.group(1)))

IDENT = r"[A-Za-z_][A-Za-z0-9_.]*"

def strip_rx(s):
    # replace /.../ regex literals with RX
    return re.sub(r"/(?:\\.|[^/])+/", "RX", s)

def match_close(s, i):
    d = 0
    for j in range(i, len(s)):
        if s[j] in "([":
            d += 1
        elif s[j] in ")]":
            d -= 1
            if d == 0:
                return j
    return -1

def top_split(inner):
    parts, d, cur = [], 0, ""
    for ch in inner:
        if ch in "([":
            d += 1
        elif ch in ")]":
            d -= 1
        if ch == "," and d == 0:
            parts.append(cur); cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts]

def classify(s, i):
    j = match_close(s, i)
    if j < 0:
        return "UNBALANCED", ""
    inner = s[i+1:j]
    before = s[:i].rstrip()
    after = s[j+1:].lstrip()
    entries = top_split(inner)
    prev_ident = re.search(IDENT + r"$", s[:i])  # call: name immediately before
    has_colon = [bool(re.search(r"(?<![:=<>!])\:(?!=)", re.sub(r"\([^()]*\)|\[[^\[\]]*\]", "", e))) for e in entries]
    has_eq = [bool(re.search(r"(?<![=<>!:])=(?!=)", re.sub(r"\([^()]*\)|\[[^\[\]]*\]", "", e))) for e in entries]
    foll_colon = after.startswith(":") and not after.startswith(":=")
    foll_bind = after.startswith(":=")
    prev_op = re.search(r"(<=|>=|==|<|>)\s*$", before)
    if prev_ident and not before.endswith(" "):
        if foll_bind:
            return "HEAD", inner
        return "CALL", inner
    if inner.strip() == "":
        return "EMPTY", inner
    if inner.strip().startswith("&"):
        return "SECTION", inner
    if foll_colon:
        if len(entries) >= 2:
            return ("REFTUPLE_DEFAULT" if any(has_eq) else "REFTUPLE"), inner
        return "REFGROUP", inner
    if foll_bind:
        return "DESTRUCT", inner
    if prev_op:
        if len(entries) >= 2:
            return "CMP_TUPLE_ATOM", inner
        return "CMP_GROUP", inner
    if any(has_colon):
        if all(has_colon):
            if any(has_eq):
                return "CONDITION_WITH_DEFAULT", inner
            if any(e.startswith("(") for e in entries):
                return "CONDITION_JOINTENTRY", inner
            return "CONDITION", inner
        return "MIXED_COLON", inner
    if any(has_eq):
        return "LABELLED_VALUE(L43)", inner
    if len(entries) >= 2:
        if entries[-1] == "":
            return "ONE_TUPLE_ERR", inner
        return "TUPLE_SET", inner
    return "GROUP", inner

pc = collections.Counter()
rows = []
mark = collections.Counter()
for (ln, kind, raw) in spans:
    s = strip_rx(raw)
    for k, ch in enumerate(s):
        if ch == "(":
            c, inner = classify(s, k)
            pc[c] += 1
            rows.append((ln, kind, c, s[max(0,k-12):k+1+len(inner)+4], raw))
    mark["comma"] += s.count(",")
    mark["colon(not :=)"] += len(re.findall(r":(?!=)", s))
    mark[":="] += s.count(":=")
    mark["= (lone)"] += len(re.findall(r"(?<![=<>!:])=(?!=)", s))
    mark["$"] += s.count("$")
    mark["cmp before ("] += len(re.findall(r"(<=|>=|==|<|>)\s*\(", s))
    mark["[ ]"] += s.count("[")
    mark["padded("] += s.count("padded(")

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "paren.tsv"), "w") as f:
    for r in rows:
        f.write("\t".join(map(str, r)) + "\n")
print("spans", len(spans), "tick", sum(1 for s in spans if s[1]=="tick"), "block", sum(1 for s in spans if s[1]=="block"))
print("paren classes:")
for k, v in pc.most_common():
    print(f"  {k}\t{v}")
print("marks:", dict(mark))
