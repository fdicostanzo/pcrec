#!/usr/bin/env python3
"""[OPT-REVEND] census_rows.tsv -> the numbers in revend_census.md.

    python3 analyze.py census_rows.tsv > summary.txt

Classes of a probe-end-anchored pattern (view 1 = `$`/`\\Z`, 2 = `\\z`):
  S  START-ANCHORED too (`^...$`): the search is a single attempt at 0; a
     reverse-from-end walk has nothing to find that the attempt does not.
  B  start-unanchored, BOUNDED width: `[OPT-ENDWIN]` already clamps the start
     to n - (maxw+eps) (byte encoding); under utf8 the clamp DECLINES.
  U  start-unanchored, UNBOUNDED width: the population a reverse-from-end
     walk could serve.  Split by lead_unb: L (some alternative begins with an
     unbounded repeat) vs I (unbounded only in the interior).
  G  contains \\G: excluded (the walk would move search_from).
"""
import csv, sys, collections

R = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
ok = [r for r in R if r["status"] == "ok"]


def cls(r):
    if r["view"] not in ("1", "2"):
        return None
    if r["gstart"] == "1":
        return "G"
    if not r["ew_status"]:
        return "F"          # the compile refused after the probe: no facts row
    if r["start_anchor"] == "anchored":
        return "S"
    # Boundedness: the SHIPPED fact where it speaks (byte encoding): it runs on the
    # post-resolve tree, so a subroutine call is expanded where the probe's
    # pre-resolve walk calls its width unbounded (138 rows, all disagreements of
    # that one kind).  Under utf8 the fact hides behind enc-multibyte, so the
    # probe's cwmax stands.
    if r["enc"] == "byte":
        bounded = r["ew_status"] == "derived"
    else:
        bounded = int(r["cwmax"]) >= 0
    if bounded:
        return "B"
    return "UL" if r["lead_unb"] == "1" else "UI"


def uniq(rs):
    return len({(r["enc"], r["pattern_hex"], r["icase"]) for r in rs})


print("== populations (rows / distinct (enc,pattern,icase))")
for pop in ("bench", "corpus"):
    for enc in ("byte", "utf8"):
        rs = [r for r in R if r["pop"] == pop and r["enc"] == enc]
        o = [r for r in rs if r["status"] == "ok"]
        print(f"{pop:7s} {enc:5s} rows {len(rs):5d} compiled {len(o):5d} refused {len(rs)-len(o):4d}")

print("\n== probe vs shipped end_window fact (byte encoding only; utf8 hides anchoring behind enc-multibyte)")
ok_f = [r for r in ok if r["ew_status"]]
print("rows with a facts row:", len(ok_f), "of", len(ok), "(the rest refused after the probe parsed them: size caps, gated modules)")
dis1 = [r for r in ok_f if r["enc"] == "byte" and r["view"] in ("1", "2")
        and r["ew_why"] == "decline:not-end-anchored"]
dis2 = [r for r in ok_f if r["enc"] == "byte" and r["view"] in ("0", "3")
        and r["ew_why"] != "decline:not-end-anchored"]
print("probe anchored, fact says not anchored:", len(dis1))
print("probe not anchored (view 0/3), fact says anchored:", len(dis2))
for r in (dis1 + dis2)[:20]:
    print("   DISAGREE", r["id"], r["view"], r["ew_why"], bytes.fromhex(r["pattern_hex"]).decode("latin1")[:60])
# bounded cross-check: fact value non-none iff probe bounded & anchored & no G
bb = [r for r in ok_f if r["enc"] == "byte" and r["view"] in ("1", "2")]
mism = [r for r in bb if (r["ew_why"] == "") != (int(r["cwmax"]) >= 0 and r["gstart"] == "0")]
print("probe bounded/G-free vs fact-derived mismatches:", len(mism),
      "(all fact-bounded / probe-unbounded: the fact reads the post-resolve tree where \\g<n> calls are expanded;",
      "fact-unbounded / probe-bounded:", sum(1 for r in mism if r["ew_why"] != ""), ")")
for r in mism[:10]:
    print("   MISMATCH", r["id"], r["cwmax"], r["gstart"], r["ew_why"])

print("\n== end-anchor classes (view 1/2), rows / distinct")
print(f"{'pop':7s} {'enc':5s} {'anch':>5s} {'S':>5s} {'B':>5s} {'UL':>5s} {'UI':>5s} {'G':>3s} {'F':>3s} | ML($ under (?m)) | lookaround-tail near-miss")
for pop in ("bench", "corpus"):
    for enc in ("byte", "utf8"):
        rs = [r for r in ok if r["pop"] == pop and r["enc"] == enc]
        c = collections.Counter(cls(r) for r in rs if cls(r))
        tot = sum(c.values())
        ml = sum(1 for r in rs if r["view"] == "3")
        lt = sum(1 for r in rs if r["view"] == "0" and r["look_tail"] == "1")
        print(f"{pop:7s} {enc:5s} {tot:5d} {c['S']:5d} {c['B']:5d} {c['UL']:5d} {c['UI']:5d} {c['G']:3d} {c['F']:3d} | {ml:4d} | {lt:4d}")
print("-- distinct patterns:")
for pop in ("bench", "corpus"):
    for enc in ("byte", "utf8"):
        rs = [r for r in ok if r["pop"] == pop and r["enc"] == enc]
        out = []
        for k in ("S", "B", "UL", "UI", "G", "F"):
            out.append(f"{k}={uniq([r for r in rs if cls(r) == k])}")
        print(f"{pop:7s} {enc:5s}", " ".join(out), f"anchored={uniq([r for r in rs if cls(r)])} of {uniq(rs)}")

print("\n== suites carrying the start-unanchored end-anchored classes (B/UL/UI), rows")
cs = collections.Counter()
for r in ok:
    k = cls(r)
    if k in ("B", "UL", "UI"):
        cs[(r["pop"], r["enc"], r["suite"], k)] += 1
for k, v in sorted(cs.items()):
    print("  ", *k, v)

print("\n== what the start-unanchored end-anchored patterns get today (stamps), rows")
for k in ("B", "UL", "UI"):
    for enc in ("byte", "utf8"):
        rs = [r for r in ok if cls(r) == k and r["enc"] == enc]
        if not rs:
            continue
        c = collections.Counter((r["ENGINE"], r["DFA_SCAN"], r["DFA_PREFILTER"], r["DFA_START"], r["DFA_MATCH"], r["REQ_BYTE"] != "none") for r in rs)
        print(f"-- class {k} {enc}: {len(rs)} rows")
        for kk, v in c.most_common():
            print("    ", v, "engine=%s scan=%s prefilter=%s start=%s match=%s reqbyte=%s" % kk)

print("\n== class UL/UI/B(utf8) patterns, bench rows listed")
for r in ok:
    k = cls(r)
    if r["pop"] == "bench" and (k in ("UL", "UI") or (k == "B" and r["enc"] == "utf8")):
        print(" ", k, r["id"], r["enc"], "cw", r["cwmax"], "engine", r["ENGINE"], r["DFA_SCAN"], r["DFA_PREFILTER"],
              bytes.fromhex(r["pattern_hex"]).decode("latin1")[:80].replace("\n", "\\n"))

print("\n== the bench rows of class S (start-anchored too), for the record")
for r in ok:
    if r["pop"] == "bench" and cls(r) == "S":
        print(" ", r["id"], r["enc"], "cw", r["cwmax"], "engine", r["ENGINE"], r["DFA_SCAN"], r["DFA_PREFILTER"])
print("\n== bench ML rows (view 3)")
for r in ok:
    if r["pop"] == "bench" and r["view"] == "3":
        print(" ", r["id"], r["enc"], bytes.fromhex(r["pattern_hex"]).decode("latin1")[:60])
