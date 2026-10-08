#!/usr/bin/env python3
"""[DEC-FALLBACK] STEP 0 census driver.

For every distinct (pattern, flags, features, encoding, engine) block of the
whole .rxt corpus (tests/**/*.rxt, via `pcrec --list-source`), compile it with
a scratch compiler (build_ref.py) and record:
  - the ENGINE / ENGINE_SEL / *_WHY / VM_PREFILTER stamps of the artifact
  - the DECFB probe lines (attempts per compile, failure labels, rungs taken)
Writes SCRATCH/census_<variant>.tsv (one row per case) for summarize.py.

usage: census.py REPO_ROOT SCRATCH VARIANT [STRIDE]
  STRIDE n>1 samples every nth case (stated in the summary).
"""
import glob, os, re, subprocess, sys
from multiprocessing import Pool

root, scratch, variant = sys.argv[1:4]
stride = int(sys.argv[4]) if len(sys.argv) > 4 else 1
PCREC = os.path.join(root, "build/pcrec")           # list-source only
COMP = os.path.join(scratch, "pcrec_" + variant)

def cases():
    seen, out = set(), []
    files = sorted(glob.glob(root + "/tests/**/*.rxt", recursive=True))
    for f in files:
        r = subprocess.run([PCREC, "--list-source", f], capture_output=True, text=True, errors="replace")
        if r.returncode:
            continue
        for ln in r.stdout.split("\n"):
            if not ln or ln.startswith("#"):
                continue
            c = ln.split("\t")
            if c[0] != "pattern" or len(c) < 11:
                continue
            key = (c[4], c[5], c[6], c[8], c[9])   # pattern flags features encoding engine
            if key in seen:
                continue
            seen.add(key)
            out.append(key)
    return out

def run(key):
    pat, flags, feats, enc, eng = key
    cmd = [COMP, "-p", "rx", "--pattern-esc", "-o", "-"]
    if "i" in flags: cmd.append("-i")
    if "u" in flags: cmd.append("--ucp")
    if feats: cmd += ["--features", feats]
    if enc: cmd += ["-e", enc]
    if eng: cmd += ["--engine=" + eng]
    cmd += ["--pattern", "\"" + pat.replace("\"", "\\\"") + "\""]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=120)
    except subprocess.TimeoutExpired:
        return key, "TIMEOUT", {}, []
    st = {}
    for m in re.finditer(r"^#define RX_(ENGINE|ENGINE_SEL|VM_PREFILTER|VM_PREFILTER_WHY|VM_PREFILTER_LANG|"
                         r"VM_PREFILTER_LANG_WHY|UNROLL_K_WHY|UNROLL_K|REQ_WHY|DFA_MATCH) (.*)$", r.stdout, re.M):
        st[m.group(1)] = m.group(2).strip('"')
    probes = [l[6:] for l in r.stderr.split("\n") if l.startswith("DECFB ")]
    if variant == "plain":   # byte-identity of the probed build vs build/pcrec
        r0 = subprocess.run([PCREC] + cmd[1:], capture_output=True, text=True,
                            errors="replace", timeout=120)
        if r0.stdout != r.stdout or r0.returncode != r.returncode:
            probes.append("BYTES_DIFF")
    return key, ("ok" if r.returncode == 0 else "refused"), st, probes

if __name__ == "__main__":
    cs = cases()[::stride]
    with Pool(6) as p:
        res = p.map(run, cs, chunksize=20)
    with open(os.path.join(scratch, "census_%s.tsv" % variant), "w") as o:
        for key, status, st, probes in res:
            o.write("\t".join([status, repr(key), repr(st), repr(probes)]) + "\n")
    print(variant, "cases", len(cs), "stride", stride)
