#!/usr/bin/env python3
"""Lane p1dsg (2026-10-29): population per row of the landmark-walk ADMISSION table
(docs/dev/lanes/p1dsg_report.md "Admission table").  PARSE-ONLY: the reader, flatten, landmark
choice, arms and tiers are lane revwalk's (revwalk_evidence/tiers.py, imported by path, which in
turn imports where_to_start/rincensus.py); pcrec runs only as `--list-source` (a lister, no compile).

The admission rows (first match):
  no-split      no common inner landmark with a non-empty prefix P (or start-anchored)
  g1            P not regular-faithful (backreference, call, atomic/possessive, lookaround)
  fixed         P has one fixed byte width: served by the EXACT-k rows (offset-set / run-pinned)
  branches      more than one top-level branch (stage 1 admits one branch; D151 add. 6/7 later)
  rarity        the landmark is not >= F x rarer than the pattern's first-byte set (F = 2, UNMEASURED)
  excl-cand     bytes(L) not all in alphabet(P)  AND  (S reads no group of P  OR  starts(j) has one member)
  excl-lower    bytes(L) not all in alphabet(P)  AND  S reads a group of P  AND  starts(j) may hold several
  factor-free   the third G2 arm only (L no factor of P, border-free): HELD
  plain-shared  P one plain run that can consume L (exact, not linear): HELD
  fallback      no strong arm: decline
"unique starts" (one member per landmark hit) is decided here by a SUFFICIENT rule on the reader's
items: P fixed width, or P opens with \\b and every byte P consumes is a word byte, or P opens with
a multiline ^ and P cannot consume \\n.  The build decides it on rev(P) itself (no accepting position
reachable from another, by-class accepts included); this rule undercounts.
Env as tiers.py (PCREC, CORPUS); P1_F sets the rarity factor (default 2, UNMEASURED).  --selftest runs the hand rows; --sabotage unique must FAIL them."""
import argparse, collections, importlib.util, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("tiers", os.path.join(HERE, "..", "revwalk_evidence", "tiers.py"))
T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
R = T.R
WORD = set(b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz")
SABOTAGE = None
F = float(os.environ.get("P1_F", "2"))


def unique_starts(pit):
    if pit is None:
        return False
    lo, hi, al, fl = R.seq_props(pit)
    if hi is not None and lo == hi:
        return True
    if SABOTAGE == "unique":
        return True
    body = list(pit)
    if not body or body[0][0] != "zw" or len(body[0]) < 3:
        return False
    ctx = body[0][2]
    _lo, _hi, al, _fl = R.seq_props([x for x in body[1:] if x[0] != "zw"])
    if ctx == "\\b":
        return bool(al) and al <= WORD
    if ctx == "^m":
        return 10 not in al
    return False


def admission(d):
    if d.get("stage") != "landmark":
        return "no-split"
    if d["tier"] == "G1":
        return "g1"
    if d["tier"] == "T1" and d["comp"]:
        return "fixed"
    if d["nbr"] > 1:
        return "branches"
    if d["ratio"] < F:
        return "rarity"
    if d["excl"]:
        if d["srefs"] and not unique_starts(d.get("_pit")):
            return "excl-lower"
        return "excl-cand"
    if d["strong"]:
        return "factor-free"
    if d["tier"] == "T2":
        return "plain-shared"
    return "fallback"


def classify(r):
    pat = r["pat"]
    try:
        rd = T.Reader(pat, r["icase"], r["enc"] == "utf8", r["mline"])
        tree = rd.parse()
    except (R.Unparsed, IndexError, ValueError, RecursionError):
        return "uncounted", {}
    if T.anchored(T.strip_one_group(tree)):
        return "no-split", {}
    if rd.approx:
        return "uncounted", {}
    try:
        d = T.decide(tree, r["enc"] == "utf8", r["icase"])
    except (R.Cap, RecursionError):
        return "uncounted", {}
    return admission(d), d


HAND = [  # (pattern, flags, expected admission row)
    (rb"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "", "excl-cand"),
    (rb"\b(\w+)=[^&]*&(?:[^&]*&)*\1=", "", "excl-cand"),          # unique by \b: CAND despite \1
    (rb"(\w+)=[^&]*&(?:[^&]*&)*\1=", "", "excl-lower"),            # no \b: LOWER
    (rb"(a+)X\1", "", "excl-lower"),                                # LF-E1's witness
    (rb"\b[a-z_][a-z0-9_]{0,31}=\"", "", "excl-cand"),             # kv-quoted: revwalk's T4 'outer'
    (rb"\bat (?:[A-Za-z_$][A-Za-z0-9_$]*\.){2,}[A-Za-z_$][A-Za-z0-9_$]*\(", "", "excl-cand"),  # stack-frame
    (rb"\S+@\S+", "", "plain-shared"),
    (rb"[a-z]+xy", "", "plain-shared"),
    (rb"(?>a+)@", "", "g1"),
    (rb"ab[0-9]@x", "", "fixed"),
    (rb"^\w+@", "", "no-split"),
    (rb"\w+\b-x", "", "excl-cand"),                                 # a view inside P is the DFA's own
]


def selftest():
    bad = 0
    for p, fl, want in HAND:
        got, _d = classify(dict(pat=p, icase="i" in fl, enc="byte", mline="m" in fl))
        ok = got == want
        bad += not ok
        print("%-4s %-60s want %-12s got %s" % ("ok" if ok else "FAIL", p.decode()[:60], want, got))
    print("selftest: %d/%d" % (len(HAND) - bad, len(HAND)))
    return bad == 0


def main():
    global SABOTAGE
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--sabotage", choices=["unique"])
    a = ap.parse_args()
    SABOTAGE = a.sabotage
    if a.selftest or a.sabotage:
        ok = selftest()
        if a.sabotage:
            print("sabotage %s: selftest %s (it must FAIL)" % (a.sabotage, "PASSED: UNDETECTED" if ok else "failed: detected"))
            sys.exit(1 if ok else 0)
        sys.exit(0 if ok else 1)
    pops = {"corpus": T.corpus_pop(), "bench": T.bench_pop()}
    order = ["no-split", "g1", "fixed", "branches", "rarity", "excl-cand", "excl-lower", "factor-free",
             "plain-shared", "fallback", "uncounted"]
    for name, pop in pops.items():
        cnt = collections.Counter(); ex = collections.defaultdict(list); sub = collections.Counter()
        for r in pop:
            row, d = classify(r)
            cnt[row] += 1
            if row in ("excl-cand", "excl-lower"):
                sub[(row, d["tier"], "unbounded" if d.get("unb") else "bounded",
                     "S-reads-P" if d["srefs"] else "-")] += 1
            if row not in ("no-split", "uncounted") and len(ex[row]) < 10:
                ex[row].append("%s L=%s" % (r["id"], d.get("L", "")))
        print("## %s: %d patterns" % (name, len(pop)))
        print("| row | patterns |")
        print("|---|---|")
        for o in order:
            print("| %s | %d |" % (o, cnt[o]))
        print("admitted rows by revwalk tier / run bound / S reads P's groups:")
        for k, v in sorted(sub.items()):
            print("  %s %s %s %s: %d" % (k + (v,)))
        for o in order:
            if ex[o]:
                print("examples %s: %s" % (o, "; ".join(ex[o])))
        print()


if __name__ == "__main__":
    main()
