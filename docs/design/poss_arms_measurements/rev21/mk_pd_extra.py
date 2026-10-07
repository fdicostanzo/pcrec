#!/usr/bin/env python3
"""Turn CLAIM-vs-MARK's EXTRA marks into an exhaustive-possdiff population.

eqcheck.py checks only the TARGET quantifier's possessive spelling against
libpcre2.  A mark the arms make on ANOTHER quantifier (claimmark's `extra`
count, and the rows whose target is unresolved but some quantifier flipped)
is a claim the predicate never made, so nothing has checked it.  This writes
every such pattern into possdiff files (one per flag set: `# features: all`
plus `# flags:`), so possdiff_exh.sh can compare the ARMED artifact with the
denied one over exhaustive subjects -- which checks every mark at once.

Usage: mk_pd_extra.py claimmark.out OUTDIR   (writes OUTDIR/pd_extra_*.txt)"""
import sys, os, collections
cm, outd = sys.argv[1], sys.argv[2]
os.makedirs(outd, exist_ok=True)
hdr = None
groups = collections.defaultdict(list)
for ln in open(cm, encoding="utf8"):
    f = ln.rstrip("\n").split("\t")
    if f[0] == "id": hdr = f; continue
    if ln.startswith("#") or hdr is None: continue
    r = dict(zip(hdr, f))
    if r["status"] != "ok" or not r["AB"].isdigit(): continue
    v = int(r["AB"])
    extra = v // 10 > 0 or (r["tgt"] == "unresolved" and v % 10 == 1)
    if not extra: continue
    mods = [m for m in r["mods"].split(",") if m and m != "no_auto_possess"]
    pre = "(?J)" if "dupnames" in mods else ""
    fl = []
    if "utf" in mods: fl += ["-e", "utf8"]
    if "i" in mods: fl.append("-i")
    if "ucp" in mods: fl.append("--ucp")
    groups[" ".join(fl)].append(pre + r["pat"])
for k, (fl, pats) in enumerate(sorted(groups.items())):
    with open(os.path.join(outd, "pd_extra_%d.txt" % k), "w", encoding="utf8") as o:
        o.write("# CLAIM-vs-MARK extra marks (mk_pd_extra.py)\n# features: all\n")
        if fl: o.write("# flags: %s\n" % fl)
        for p in sorted(set(pats)): o.write(p + "\n")
    print("pd_extra_%d.txt\t%s\t%d" % (k, fl or "-", len(set(pats))))
