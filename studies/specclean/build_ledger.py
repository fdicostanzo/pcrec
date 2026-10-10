#!/usr/bin/env python3
"""Assemble studies/specclean/claims.tsv: every normative claim of the old
match_api.md (claims_C*.tsv), its mapping (map_*.tsv, made against the draft
at commit 848e6564), the lane's resolutions of UNMAPPED rows
(resolutions.tsv), and each mapped claim's line + anchor in the FINAL doc.
Draft line numbers are carried to the final doc by a difflib line alignment.
Run from the worktree root: python3 studies/specclean/build_ledger.py"""
import difflib, re, subprocess, sys
D = "studies/specclean/"
draft = subprocess.run(["git", "show", "848e6564:docs/spec/match_api.md"],
                       capture_output=True, text=True, check=True).stdout.split("\n")
final = open("docs/spec/match_api.md").read().split("\n")
sm = difflib.SequenceMatcher(None, draft, final, autojunk=False)
lmap = {}
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    for k in range(i1, i2):
        lmap[k + 1] = (j1 + (k - i1) + 1) if tag == "equal" else min(j1 + (k - i1), max(j2 - 1, j1)) + 1
anchors = [(i + 1, m.group(1)) for i, l in enumerate(final)
           for m in [re.match(r'<a id="([^"]+)"></a>', l)] if m]
def anchor_of(line):
    best = ""
    for n, a in anchors:
        if n <= line: best = a
    return best
claims = []
for p in ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]:
    claims += [l.rstrip("\n").split("\t") for l in open(D + "claims_%s.tsv" % p) if l.strip()]
maps = {}
for p in ["C1", "C2", "C3", "C4", "C5", "C6a", "C6b", "C7"]:
    for l in open(D + "map_%s.tsv" % p):
        if l.strip():
            c = l.rstrip("\n").split("\t")
            maps[c[0]] = c[1:]
res = {}
for l in open(D + "resolutions.tsv"):
    if l.strip():
        c = l.rstrip("\n").split("\t")
        res[c[0]] = c[1:]
out = ["id\told_line\tkind\tclaim\tstatus\tnew_line\tnew_anchor\tnote"]
counts = {}; bad = []
ftext = "\n".join(final)
for c in claims:
    cid, oline, kind, claim = c[0], c[1], c[2], c[3]
    st, nl, note = (maps.get(cid) + ["", "", ""])[:3] if cid in maps else ("", "", "")
    if not st:
        bad.append(cid + " has no mapping row"); continue
    if cid in res:
        st, loc, note = res[cid][0], res[cid][1], res[cid][2]
        nl = ""
        if loc:
            pat = r"\s+".join(re.escape(w) for w in loc.split())
            m = re.search(pat, ftext)
            if not m: bad.append("%s locator not found: %s" % (cid, loc)); continue
            nl = str(ftext[: m.start()].count("\n") + 1)
    elif nl.strip():
        try:
            first = int(re.findall(r"\d+", nl)[0])
            nl = str(lmap.get(first, first))
        except IndexError:
            nl = ""
    if st in ("UNMAPPED",):
        bad.append(cid + " is still UNMAPPED")
    anc = anchor_of(int(nl)) if nl else ""
    counts[st] = counts.get(st, 0) + 1
    out.append("\t".join([cid, oline, kind, claim, st, nl, anc, note.replace("\t", " ")]))
open(D + "claims.tsv", "w").write("\n".join(out) + "\n")
print("claims:", len(out) - 1, " ".join("%s=%d" % kv for kv in sorted(counts.items())))
if bad:
    print("PROBLEMS:"); print("\n".join(bad)); sys.exit(1)
