#!/usr/bin/env python3
"""run_compare.py -- for every subject, get:
   - PCRE2 answer on orig.rx and on factored.rx (must agree with each other)
   - pcrec MAIN on orig.rx
   - pcrec BC on orig.rx
   - pcrec BC on factored.rx
 and report every disagreement.
"""
import importlib.util
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SUBJ_DIR = os.path.join(HERE, "subjects")
ART_DIR = os.path.join(HERE, "artifacts")

_spec = importlib.util.spec_from_file_location(
    "sr_oracle",
    os.path.join(HERE, "oracle", "docs", "design",
                 "subroutines_measurements", "probes", "sr_oracle.py"))
sr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sr)

with open(os.path.join(HERE, "orig.rx"), "rb") as f:
    ORIG_PAT = f.read()
with open(os.path.join(HERE, "factored.rx"), "rb") as f:
    FACTORED_PAT = f.read()

orig_code = sr.br.compile(ORIG_PAT, 0)
factored_code = sr.br.compile(FACTORED_PAT, 0)


def run_pcrec(binpath, subjfile):
    r = subprocess.run([binpath, subjfile], capture_output=True, timeout=30)
    out = r.stdout.decode("latin-1").strip()
    if out.startswith("match"):
        parts = out.split()
        return ("match", int(parts[1]), int(parts[2]))
    if out == "nomatch":
        return ("nomatch",)
    return ("giveup", out, r.returncode)


def oracle_answer(code, subj_bytes):
    r = code.search(subj_bytes, 0)
    if r is None:
        return ("nomatch",)
    span, groups = r
    return ("match", span[0], span[1])


manifest = []
with open(os.path.join(SUBJ_DIR, "manifest.tsv"), encoding="latin-1") as f:
    next(f)
    for line in f:
        sid, slen, desc = line.rstrip("\n").split("\t", 2)
        manifest.append((sid, int(slen), desc))

RUN_MAIN_ORIG = os.path.join(ART_DIR, "run_main_orig")
RUN_BC_ORIG = os.path.join(ART_DIR, "run_bc_orig")
RUN_BC_FACTORED = os.path.join(ART_DIR, "run_bc_factored")

disagreements = []
factoring_bugs = []
recursion_findings = []
rows = []

for sid, slen, desc in manifest:
    subjfile = os.path.join(SUBJ_DIR, "%s.bin" % sid)
    with open(subjfile, "rb") as f:
        subj = f.read()

    oa_orig = oracle_answer(orig_code, subj)
    oa_factored = oracle_answer(factored_code, subj)
    pm_orig = run_pcrec(RUN_MAIN_ORIG, subjfile)
    pb_orig = run_pcrec(RUN_BC_ORIG, subjfile)
    pb_factored = run_pcrec(RUN_BC_FACTORED, subjfile)

    row = dict(id=sid, desc=desc, len=slen,
               oa_orig=oa_orig, oa_factored=oa_factored,
               pm_orig=pm_orig, pb_orig=pb_orig, pb_factored=pb_factored)
    rows.append(row)

    if oa_orig != oa_factored:
        factoring_bugs.append(row)
    if pm_orig != oa_orig:
        disagreements.append(("MAIN/orig", row))
    if pb_orig != oa_orig:
        disagreements.append(("BC/orig", row))
    if pb_factored != oa_factored:
        disagreements.append(("BC/factored", row))
        recursion_findings.append(row)

# ---------------------------------------------------------------------
print("=" * 100)
print("ORACLE SELF-CONSISTENCY: orig.rx vs factored.rx (libpcre2 only)")
print("=" * 100)
if not factoring_bugs:
    print("OK: %d/%d subjects -- orig.rx and factored.rx agree under libpcre2 on every subject."
          % (len(rows), len(rows)))
else:
    print("FACTORING BUG: %d subjects disagree between orig.rx and factored.rx under libpcre2:"
          % len(factoring_bugs))
    for row in factoring_bugs:
        print("  [%s] %-60s orig=%s factored=%s" % (
            row["id"], row["desc"], row["oa_orig"], row["oa_factored"]))

print()
print("=" * 100)
print("DISAGREEMENT TABLE (pcrec vs its own oracle column)")
print("=" * 100)
if not disagreements:
    print("EMPTY: every pcrec artifact agrees with libpcre2 on every subject (%d subjects x 3 artifacts = %d checks)."
          % (len(rows), len(rows) * 3))
else:
    print("%-14s %-6s %-60s %-30s %-30s" % ("artifact", "id", "description", "oracle", "pcrec"))
    for which, row in disagreements:
        oracle = row["oa_orig"] if which != "BC/factored" else row["oa_factored"]
        pcrec = {"MAIN/orig": row["pm_orig"], "BC/orig": row["pb_orig"],
                 "BC/factored": row["pb_factored"]}[which]
        print("%-14s %-6s %-60s %-30s %-30s" % (which, row["id"], row["desc"][:58], str(oracle), str(pcrec)))

print()
print("RECURSION-MODULE FINDINGS (BC/factored vs libpcre2 disagreements): %d" % len(recursion_findings))
for row in recursion_findings:
    print("  [%s] %-60s oracle(factored)=%s pcrec(BC/factored)=%s" % (
        row["id"], row["desc"], row["oa_factored"], row["pb_factored"]))

# Also cross-check the three pcrec artifacts against EACH OTHER for
# informational purposes (MAIN/orig should equal BC/orig always, since
# same pattern; BC/factored should equal them too since same language).
print()
print("=" * 100)
print("CROSS-ARTIFACT CHECK (informational): MAIN/orig vs BC/orig vs BC/factored")
print("=" * 100)
cross_mismatch = 0
for row in rows:
    a, b, c = row["pm_orig"], row["pb_orig"], row["pb_factored"]
    if not (a == b == c):
        cross_mismatch += 1
        print("  [%s] %-60s MAIN/orig=%s BC/orig=%s BC/factored=%s" % (
            row["id"], row["desc"][:58], a, b, c))
if cross_mismatch == 0:
    print("EMPTY: all three pcrec artifacts agree with each other on every subject.")

print()
print("total subjects: %d" % len(rows))
