#!/usr/bin/env python3
"""Count scoreboard gap constructs in patterns.tsv and what pcrec refuses.

usage: python3 -I count_gaps.py PATTERNS_TSV PCREC_BIN

Runs PCREC_BIN --features all on every UNIQUE pattern text, serially (the
caller niced it), 20 s each under gnutimeout.  Prints the counts.  The
construct scan is lexical (escapes and bracket classes are skipped);
variable-width lookbehind is not scanned lexically: it is whatever pcrec
refuses as such.
"""
import collections
import re
import subprocess
import sys

CONSTRUCTS = ["lookbehind-any", "conditional", r"\X", "set-ops (?[", r"\R",
              "(*ACCEPT)", "(*FAIL)", r"\C", r"\cX", r"\o{}", r"\N{U+}",
              "(?#..)", "(?|..)", "[[:<:]]"]


def esc_construct(p, j, found):
    """p[j] is a backslash; record a gap escape and return the next index."""
    d = p[j + 1:j + 2]
    if d in ("X", "R", "C"):
        found.add("\\" + d)
    elif d == "c":
        found.add(r"\cX")
    elif d == "o" and p[j + 2:j + 3] == "{":
        found.add(r"\o{}")
    elif d == "N" and p[j + 2:j + 5] == "{U+":
        found.add(r"\N{U+}")
    return j + 2


def scan(p):
    found = set()
    i, n = 0, len(p)
    while i < n:
        c = p[i]
        if c == "\\":
            i = esc_construct(p, i, found)
        elif c == "[":
            if p.startswith("[[:<:]]", i) or p.startswith("[[:>:]]", i):
                found.add("[[:<:]]")
                i += 7
                continue
            j = i + 1
            if p[j:j + 1] == "^":
                j += 1
            if p[j:j + 1] == "]":
                j += 1
            while j < n and p[j] != "]":
                if p[j] == "\\":
                    sub = set()
                    j = esc_construct(p, j, sub)
                    found |= sub - {"\\X", "\\R", "\\C"}  # not class escapes
                elif p.startswith("[:", j):
                    k = p.find(":]", j + 2)
                    j = k + 2 if k > 0 else j + 1
                else:
                    j += 1
            i = j + 1
        elif c == "(":
            for pre, name in (("(?<=", "lookbehind-any"), ("(?<!", "lookbehind-any"),
                              ("(*plb:", "lookbehind-any"), ("(*nlb:", "lookbehind-any"),
                              ("(?(", "conditional"), ("(?[", "set-ops (?["),
                              ("(?#", "(?#..)"), ("(?|", "(?|..)"),
                              ("(*ACCEPT", "(*ACCEPT)"), ("(*FAIL", "(*FAIL)"),
                              ("(*F)", "(*FAIL)")):
                if p.startswith(pre, i):
                    found.add(name)
            i += 1
        else:
            i += 1
    return found


def main(tsv, pcrec):
    pats = collections.OrderedDict()
    with open(tsv, encoding="utf-8", errors="surrogateescape") as f:
        next(f)
        for line in f:
            c = line.rstrip("\n").split("\t")
            pats.setdefault(c[11], []).append(c[0])
    counts = collections.Counter()
    hist = collections.Counter()
    by_construct = collections.defaultdict(collections.Counter)
    ok = 0
    for p in pats:
        r = subprocess.run(
            ["/usr/bin/gnutimeout", "20", pcrec, "-p", "rx", "--features",
             "all", "-o", "-", "--pattern", p],
            capture_output=True)
        found = scan(p)
        for g in found:
            counts[g] += 1
        tag = None
        if r.returncode == 0:
            ok += 1
        else:
            msg = r.stderr.decode("utf-8", "replace").strip().splitlines()
            msg = [x for x in msg if not x.replace("pcrec: ", "").startswith("warning:")]
            msg = msg[0] if msg else "rc=%d" % r.returncode
            m = re.search(r"requires module '([\w-]+)'|module '([\w-]+)' is enabled", msg)
            t = re.search(r"pattern too large: \d+ bytes of emitted (code|C source) \(limit (\d+)", r.stderr.decode("utf-8", "replace"))
            if t:
                tag = "too large: emitted %s over limit %s" % (t.group(1), t.group(2))
            elif m:
                tag = "module " + (m.group(1) or m.group(2))
            else:
                tag = re.sub(r"\(pattern offset.*", "", msg.replace("pcrec: ", ""))[:70]
            hist[tag] += 1
        for g in found:
            by_construct[g][tag or "accepted"] += 1
    print("unique patterns %d  compiled-ok %d  refused %d" % (len(pats), ok, len(pats) - ok))
    print("refusal histogram:")
    for k, v in hist.most_common():
        print("  %4d  %s" % (v, k))
    print("construct counts (unique patterns using it) and their pcrec outcome:")
    for g in CONSTRUCTS:
        print("  %-16s %4d  %s" % (g, counts[g], dict(by_construct[g])))


main(sys.argv[1], sys.argv[2])
