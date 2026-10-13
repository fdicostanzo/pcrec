#!/usr/bin/env python3
"""regimefacts: join pcrec-bench subject-grain reports (read-only) with the
bench's subject manifests (read-only) -> per (subbench, pattern, subject,
regime) pcrec median ns/call and subject length.  Usage:
  python3 -I bench_population.py BENCH_ROOT > population.tsv
No timing, no pcrec build.  Which report is read per subbench is the SPEC table."""
import csv, sys, os, glob
B = sys.argv[1]
SPEC = [  # subbench, report glob, testee, manifest dir
 ("altwide",   "2026-10-13-altwide-0.3-*handoff-6b2dbd3e",   "pcrec_6b2dbd3e_auto-caps-simdna", "altwide"),
 ("bounded",   "2026-10-13-bounded-0.3-*handoff-6b2dbd3e",   "pcrec_b8337c33_auto-caps-simdna", "bounded"),
 ("capability","2026-10-13-capability-0.2-*handoff-6b2dbd3e","pcrec_6b2dbd3e_auto-caps-simdna", "capability"),
 ("email",     "2026-10-11-email-specimen-0.2-*landing-b8337c33","pcrec_b8337c33_auto-caps-simdna","email"),
 ("litrun",    "2026-10-13-litrun-0.1-*handoff-6b2dbd3e",    "pcrec_6b2dbd3e_auto-caps-simdna", "litrun"),
 ("loglines",  "2026-10-13-loglines-0.1-*handoff-6b2dbd3e",  "pcrec_6b2dbd3e_auto-caps-simdna", "loglines"),
 ("syntax",    "2026-10-13-syntax-0.1-*handoff-6b2dbd3e",    "pcrec_6b2dbd3e_auto-caps-simdna", "syntax"),
 ("utf8",      "2026-10-13-utf8-0.1-*handoff-6b2dbd3e",      "pcrec_6b2dbd3e_auto-caps-simdna_utf8","utf8"),
]
def man(d, name):
    p = f"{B}/bench/{d}/{name}"
    out = {}
    if os.path.exists(p):
        for r in csv.DictReader(open(p), delimiter="\t"):
            out[r["id"]] = int(r["len"])
    return out
print("subbench\tpattern\tsubject\tregime\tlen\tmedian_ns\ttestee")
for sb, g, testee, d in SPEC:
    short, thr = man(d, "manifest.tsv"), man(d, "manifest_throughput.tsv")
    fs = glob.glob(f"{B}/reports/{g}.subject-grain.tsv")
    assert len(fs) == 1, (sb, fs)
    for l in open(fs[0]):
        f = l.rstrip("\n").split("\t")
        if f[0] != "rank" or len(f) < 12 or f[6] != testee or f[7] != "measured" or f[10] != "median_ns":
            continue
        reg = f[3]
        n = (thr if reg == "large-subject-throughput" else short).get(f[2])
        print("\t".join([sb, f[1], f[2], reg, "" if n is None else str(n), f[11], testee]))
