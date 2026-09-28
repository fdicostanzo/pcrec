#!/usr/bin/env python3
"""analyze.py FILE -- set relations over a classify TSV (classify.c or
classify_remote.py output).  Prints the equalities §B of ucp_study.md cites."""
import sys
def parse(path):
    S = {}
    for ln in open(path):
        if ln.startswith("#"): continue
        f = ln.rstrip("\n").split("\t")
        s = set()
        for iv in filter(None, f[3].split(",")):
            a, b = (int(x, 16) for x in iv.split("-"))
            s.update(c for c in range(a, b + 1) if not 0xD800 <= c <= 0xDFFF)
        S[(f[0], f[1])] = s
    return S
S = parse(sys.argv[1])
U = lambda p: S[(p, "UTF|UCP")]
N = lambda p: S[(p, "UTF")]
def rel(name, a, b):
    print("%-44s %s  (|A|=%d |B|=%d, A-B=%d, B-A=%d)%s" % (name, "EQUAL " if a == b else "DIFFER", len(a), len(b),
          len(a - b), len(b - a), "" if a == b else "  A-B e.g. %s B-A e.g. %s" % (
          [hex(c) for c in sorted(a - b)[:6]], [hex(c) for c in sorted(b - a)[:6]])))
ascii_w = set(range(0x30, 0x3A)) | set(range(0x41, 0x5B)) | set(range(0x61, 0x7B)) | {0x5F}
rel("UTF  \\w == [A-Za-z0-9_]", N("\\w"), ascii_w)
rel("UTF  \\s == [\\t\\n\\v\\f\\r ]", N("\\s"), {9, 10, 11, 12, 13, 32})
rel("UCP  \\w == \\p{Xwd}", U("\\w"), U("\\p{Xwd}"))
rel("UCP  \\w == [\\p{L}\\p{N}\\p{Mn}\\p{Pc}]", U("\\w"), U("[\\p{L}\\p{N}\\p{Mn}\\p{Pc}]"))
rel("UCP  \\w == [\\p{L}\\p{N}_] (pre-10.43 def)", U("\\w"), U("[\\p{L}\\p{N}_]"))
rel("UCP  \\d == \\p{Nd}", U("\\d"), U("\\p{Nd}"))
rel("UCP  \\s == \\p{Xsp}", U("\\s"), U("\\p{Xsp}"))
rel("UCP  \\s == \\p{Xps}", U("\\s"), U("\\p{Xps}"))
rel("UCP  \\s == \\h|\\v", U("\\s"), U("\\h") | U("\\v"))
rel("UCP  \\h unchanged by UCP", U("\\h"), N("\\h"))
rel("UCP  \\v unchanged by UCP", U("\\v"), N("\\v"))
rel("UCP  [:alpha:] == \\p{L}", U("[[:alpha:]]"), U("\\p{L}"))
rel("UCP  [:digit:] == \\p{Nd}", U("[[:digit:]]"), U("\\p{Nd}"))
rel("UCP  [:alnum:] == \\p{Xan}", U("[[:alnum:]]"), U("\\p{Xan}"))
rel("UCP  [:space:] == \\p{Xps}", U("[[:space:]]"), U("\\p{Xps}"))
rel("UCP  [:word:] == \\w", U("[[:word:]]"), U("\\w"))
rel("UCP  [:lower:] == \\p{Ll}", U("[[:lower:]]"), U("\\p{Ll}"))
rel("UCP  [:upper:] == \\p{Lu}", U("[[:upper:]]"), U("\\p{Lu}"))
rel("UCP  [:blank:] == \\h", U("[[:blank:]]"), U("\\h"))
rel("UCP  [:cntrl:] == \\p{Cc}", U("[[:cntrl:]]"), U("\\p{Cc}"))
rel("UCP  [:xdigit:] vs UTF [:xdigit:]", U("[[:xdigit:]]"), N("[[:xdigit:]]"))
rel("UCP  [:punct:] == \\p{P} | (\\p{S} & ASCII)", U("[[:punct:]]"), U("\\p{P}") | {c for c in U("\\p{S}") if c < 128})
rel("UCP  (?i)[:lower:] == [:lower:]  (NO fold)", U("(?i)[[:lower:]]"), U("[[:lower:]]"))
rel("UTF  (?i)[:lower:] == [A-Za-z]  (folds)", N("(?i)[[:lower:]]"), set(range(65, 91)) | set(range(97, 123)))
rel("UCP  (?i)\\p{Ll} == (?i)\\p{Lu}", U("(?i)\\p{Ll}"), U("(?i)\\p{Lu}"))
rel("UTF  (?i)\\p{Ll} == UCP (?i)\\p{Ll}", N("(?i)\\p{Ll}"), U("(?i)\\p{Ll}"))
rel("UCP  (?i)\\p{Ll} vs \\p{Ll}|\\p{Lu}", U("(?i)\\p{Ll}"), U("\\p{Ll}") | U("\\p{Lu}"))
for p in ("\\p{Xwd}", "\\p{Nd}", "\\p{Xsp}", "\\p{L}"):
    rel("UCP-indep %s (UTF == UTF|UCP)" % p, N(p), U(p))
xwd = U("\\w")
print("UCP \\w members >= 0x80:", len({c for c in xwd if c >= 0x80}), "of", len(xwd))
print("UCP \\w intervals:", sum(1 for c in xwd if c - 1 not in xwd or c == 0xE000))
