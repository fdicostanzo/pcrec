#!/usr/bin/env python3
"""census_analyze.py CENSUS.tsv -- the tables §A, §C and §D of ucp_study.md
quote, read off census.py's output.  Unique-pattern counts (a pattern used by
several blocks counts once per (pattern, encoding, caseless))."""
import sys, re, collections as C
rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[1])][1:]
R = [dict(zip("src n enc ci feats eng sel why b8 brw brwwhy pat".split(), r)) for r in rows]
for r in R: r["F"] = set(r["feats"].split())
ok = [r for r in R if r["eng"] in ("dfa", "vm", "")]
print("unique rows %d, compiled %d, refused %d" % (len(R), len(ok), sum(r["eng"] == "REFUSED" for r in R)))
UCPSENS = lambda F: {x for x in F if x in ("w", "d", "s", "b", "B") or x.startswith("posix:")}
def demand(label, pop):
    n = len(pop); sens = [r for r in pop if UCPSENS(r["F"])]
    print("\n== A. DEMAND: %s (n=%d)" % (label, n))
    print("  UCP-sensitive (any of \\w \\d \\s \\b \\B [:posix:]): %d (%.1f%%)" % (len(sens), 100.0 * len(sens) / max(n, 1)))
    cnt = C.Counter()
    for r in sens:
        for x in UCPSENS(r["F"]): cnt[x if not x.startswith("posix:") else "posix"] += 1
    for k in ("w", "d", "s", "b", "B", "posix"): print("    %-6s %5d  (%.1f%% of sensitive)" % (k, cnt[k], 100.0 * cnt[k] / max(len(sens), 1)))
    nb = [r for r in sens if r["F"] & {"b", "B"}]
    print("  needs \\b or \\B: %d of %d sensitive = %.1f%%" % (len(nb), len(sens), 100.0 * len(nb) / max(len(sens), 1)))
    only_b = [r for r in nb if not (UCPSENS(r["F"]) - {"b", "B"})]
    print("  \\b/\\B is the ONLY sensitive construct: %d" % len(only_b))
    px = C.Counter(x for r in sens for x in r["F"] if x.startswith("posix:"))
    print("  posix names:", dict(px))
    ci = [r for r in sens if r["ci"] or "i" in r["F"]]
    cilu = [r for r in ci if r["F"] & {"posix:lower", "posix:upper"}]
    print("  caseless AND sensitive: %d; of which caseless [:lower:]/[:upper:] (the one UCP x CASELESS cell): %d" % (len(ci), len(cilu)))
    na = [r for r in sens if "nonascii" in r["F"]]
    print("  sensitive AND non-ASCII pattern bytes: %d" % len(na))
    verbs = C.Counter(x for r in pop for x in r["F"] if x.startswith("verb:"))
    print("  start-of-pattern verbs:", dict(verbs))
for label, f in (("corpus, all encodings", lambda r: "corpus" in r["src"]),
                 ("corpus, utf8 blocks", lambda r: "corpus" in r["src"] and r["enc"] == "utf8"),
                 ("bench, all sets", lambda r: "bench" in r["src"]),
                 ("bench/utf8 only", lambda r: "bench" in r["src"] and r["enc"] == "utf8")):
    demand(label, [r for r in R if f(r)])
print("\n== bench (*UCP) patterns")
for r in R:
    if "verb:UCP" in r["F"]: print("  ", r["pat"][:80], "|", r["eng"], r["why"][:60])
print("\n== C. \\b/\\B POPULATION ROUTES (compiled rows only)")
bp = [r for r in R if r["F"] & {"b", "B"} and r["eng"] in ("dfa", "vm")]
for label, f in (("corpus", lambda r: "corpus" in r["src"]), ("bench", lambda r: "bench" in r["src"]), ("all", lambda r: True)):
    s = [r for r in bp if f(r)]
    t = C.Counter(r["eng"] for r in s); t8 = C.Counter(r["b8"] for r in s); tr = C.Counter(r["brw"] for r in s)
    print("  %-7s n=%d  own-enc engine %s | under -e utf8 %s | lookaround rewrite %s" % (label, len(s), dict(t), dict(t8), dict(tr)))
    mv = [r for r in s if r["b8"] == "dfa" and r["brw"] == "vm"]
    print("          DFA under utf8 -> VM after rewrite: %d (%.1f%%)" % (len(mv), 100.0 * len(mv) / max(len(s), 1)))
    rwref = [r for r in s if r["brw"] == "REFUSED"]
    if rwref: print("          rewrite REFUSED: %d e.g. %s" % (len(rwref), rwref[0]["brwwhy"][:100]))
print("\n== D. WHY A PATTERN IS OFF THE DFA (auto, compiled rows; VM rows by WHY kind)")
vm = [r for r in ok if r["eng"] == "vm"]
print("  compiled %d: dfa %d, vm %d" % (len(ok), sum(r["eng"] == "dfa" for r in ok), len(vm)))
print("  VM by ENGINE_SEL:", dict(C.Counter(r["sel"] for r in vm)))
kind = C.Counter()
for r in vm:
    w = re.sub(r" at pattern offset \d+", "", r["why"]).replace("\\?", "?") or "(no WHY: sel=%s)" % r["sel"]
    if w.startswith("dfa overflowed") or "states" in w: w = "dfa overflow (" + w[:40] + "...)"
    kind[w] += 1
for k, v in kind.most_common(): print("    %5d  %s" % (v, k))
for label, f in (("corpus", lambda r: "corpus" in r["src"]), ("bench", lambda r: "bench" in r["src"])):
    s = [r for r in vm if f(r)]
    k2 = C.Counter(re.sub(r" at pattern offset \d+", "", r["why"]).replace("\\?", "?") or "(none:%s)" % r["sel"] for r in s)
    print("  %s VM n=%d:" % (label, len(s)), dict(k2.most_common(12)))

# ---- D2: every DFA-excluding construct per VM row (lexical, approximate),
# so "could ALL of this pattern's exclusions be inserted checks" is a count
# rather than a reading of WHY's first-row-wins text.
FAM = [("lookahead", rb"\(\?[=!]|\(\*(pla|nla|positive_lookahead|negative_lookahead):"),
       ("lookbehind", rb"\(\?<[=!]|\(\*(plb|nlb|positive_lookbehind|negative_lookbehind):"),
       ("nonatomic-look", rb"\(\?<?\*|\(\*(napla|naplb|non_atomic_positive_look(ahead|behind)):"),
       ("atomic", rb"\(\?>|\(\*atomic:"),
       ("possessive", rb"(?<!\\)[*+?}]\+"),
       ("backref", rb"\\[1-9]|\\k[<{']|\\g\{?-?\d|\(\?P=|\\g\{[A-Za-z_]"),
       ("\\K", rb"\\K"),
       ("call", rb"\(\?R\)|\(\?[+-]?\d+\)|\(\?&|\(\?P>|\\g<|\\g'"),
       ("var", rb"\$\{"),
       ("cond", rb"\(\?\(")]
def fams(p):
    b = p.split(" ", 1)[1].encode("utf-8", "surrogateescape") if " " in p else b""
    return {n for n, rx in FAM if re.search(rx, b)}
if "nocap" in sys.argv[1]:
    vm = [r for r in ok if r["eng"] == "vm"]
    print("\n== D2. VM rows (no-captures) by the SET of excluding families present (lexical)")
    sets = C.Counter()
    for r in vm:
        f = fams(r["pat"])
        if not f and r["why"].startswith("dfa overflowed"): f = {"dfa-overflow"}
        sets[" + ".join(sorted(f)) or "(none found: sel=%s why=%s)" % (r["sel"], r["why"][:30])] += 1
    for k, v in sets.most_common(25): print("    %5d  %s" % (v, k))
    look = {"lookahead", "lookbehind", "nonatomic-look"}
    only_look = [r for r in vm if fams(r["pat"]) and fams(r["pat"]) <= look]
    print("  VM rows whose ONLY excluding families are lookarounds: %d of %d (%.1f%%)" % (len(only_look), len(vm), 100.0 * len(only_look) / len(vm)))
    only_lb = [r for r in vm if fams(r["pat"]) and fams(r["pat"]) <= {"lookbehind"}]
    print("    ... of which lookbehind only: %d" % len(only_lb))
    for lab, f in (("corpus", lambda r: "corpus" in r["src"]), ("bench", lambda r: "bench" in r["src"])):
        print("    %s: %d of %d" % (lab, sum(1 for r in only_look if f(r)), sum(1 for r in vm if f(r))))

# ---- A2: partial-UCP split -- which sensitive patterns need ONLY the small
# sets (\d = Nd 71 intervals, \s = Xsp 11, the small POSIX names), and which
# need a \p{Xwd}/\p{L}-sized set (\w, \b, \B, and the letter/print POSIX names).
CHEAP = {"d", "s", "posix:digit", "posix:space", "posix:blank", "posix:cntrl", "posix:xdigit"}
print("\n== A2. PARTIAL-UCP SPLIT (sensitive patterns, unique)")
for label, f in (("corpus", lambda r: "corpus" in r["src"]), ("bench", lambda r: "bench" in r["src"])):
    sens = [r for r in R if f(r) and UCPSENS(r["F"])]
    cheap = [r for r in sens if UCPSENS(r["F"]) <= CHEAP]
    wonly = [r for r in sens if not (UCPSENS(r["F"]) <= CHEAP) and not (r["F"] & {"b", "B"})]
    print("  %-7s sensitive %d: small-sets-only %d | needs a big set but no \\b %d | needs \\b/\\B %d" % (
        label, len(sens), len(cheap), len(wonly), len([r for r in sens if r["F"] & {"b", "B"}])))
