#!/usr/bin/env python3
"""Judge identity run 1 (a 3b9754edf subject against the pre-landing pins).
GREEN iff every axis reads (B) differing=0 and (A) differing=0, and every
refusal mismatch is subject=compiled reference=refused on a pattern libpcre2
accepts at max_varlookbehind 255 and refuses at 0 (stage 1's class, judged by
the oracle, never by either pcrec). Prints the manifest overlap for the
report (vlbinv_evidence/population.tsv; 22 distinct call-free expected)."""
import glob, os, re, sys
log, workroot, root = sys.argv[1:4]
sys.path.insert(0, os.path.join(root, "docs/design/eng_brep_measurements/probes"))
import pcre2_ctypes as P
txt = open(log, encoding="utf-8", errors="replace").read()
ok = True
B = re.findall(r"recursion-identity\[([^\]]+)\] \(B\) whole-file vs \S+: same=(\d+) differing=(\d+)", txt)
A = re.findall(r"recursion-identity\[([^\]]+)\] \(A\) program-region vs \S+: same=(\d+) differing=(\d+)", txt)
print("id1: (B) axes:", B); print("id1: (A) axes:", A)
if not B or not A:
    print("id1: RED no summary lines"); ok = False
for lab, same, d in B + A:
    if int(d) != 0:
        print("id1: RED differing=%s on %s" % (d, lab)); ok = False
mism = {}
for f in glob.glob(os.path.join(workroot, "*", "diff.*")):
    for line in open(f, encoding="utf-8", errors="surrogateescape"):
        m = re.match(r"REFUSAL MISMATCH (.*): subject=(\w+) reference=(\w+)$", line.rstrip("\n"))
        if m:
            mism.setdefault(m.group(1), set()).add((m.group(2), m.group(3), os.path.basename(f)))
def acc(p, mv):
    try:
        P.compile(p.encode("utf-8", "surrogateescape"), 0, mv); return True
    except P.Pcre2Error:
        return False
man = set()
for line in open(os.path.join(root, "docs/dev/lanes/vlbinv_evidence/population.tsv")):
    f = line.rstrip("\n").split("\t")
    if f[0] != "rows": man.add(f[1])
wit = open(os.path.join(root, "tests/lookaround/lookbehind_variable_witness.rxt"), encoding="utf-8").read()
allowed = {p for p in mism if p in man or ("\npattern " + p + "\n") in wit}
for p, how in sorted(mism.items()):
    dirs = {(a, b) for a, b, _ in how}
    if dirs == {("refused", "compiled")}:
        # the 65535 ceiling (vlookbehind 5.2): the old pin compiled it, libpcre2 refuses it even at 65535
        good = (not acc(p, 65535)); kind = "ceiling"
    else:
        good = dirs == {("compiled", "refused")} and acc(p, 255) and not acc(p, 0); kind = "stage1"
    if good and p not in allowed: good = False; kind = "NOT-IN-MANIFEST-OR-WITNESS"
    ok &= good
    print("id1: %s %r %s labels=%s" % (kind if good else "UNEXPECTED:"+kind, p, sorted(dirs),
                                         sorted({l for _, _, l in how})))
man = set()
for line in open(os.path.join(root, "docs/dev/lanes/vlbinv_evidence/population.tsv")):
    f = line.rstrip("\n").split("\t")
    if f[0] != "rows": man.add(f[1])
print("id1: mismatches=%d manifest=%d in-both=%d" % (len(mism), len(man), len(man & set(mism))))
print("id1: manifest-not-mismatched:", sorted(man - set(mism)))
print("id1: mismatched-not-in-manifest:", sorted(set(mism) - man))
print("id1: VERDICT", "GREEN" if ok else "RED")
sys.exit(0 if ok else 1)
