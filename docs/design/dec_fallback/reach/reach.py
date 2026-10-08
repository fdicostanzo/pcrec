#!/usr/bin/env python3
"""[DEC-FALLBACK] rev 2: the row-reach PROTOTYPE (dec_fallback.md §4.3a).

For every distinct (pattern, flags, features, encoding, engine) block of the
.rxt corpus (decfb0's population, via `build/pcrec --list-source`), plus the
constructed witnesses in witnesses.tsv, compile with a probed scratch
compiler (build_reach.py) under one limit VARIANT and one flag ARM, and
record per compile:

  - the artifact's stamps (ENGINE, ENGINE_SEL, UNROLL_K_WHY, VM_PREFILTER*)
  - the DECFB probe lines (arrivals, the row each took, every attempt's
    admission inputs and the collapse gate's verdict)
  - for a VM artifact, `--emit-ir`'s summary `prefilter` value (the listing
    token), from a SECOND compile with the same argv plus --emit-ir

Writes SCRATCH/reach_<variant>_<arm>.jsonl. analyse.py turns those into the
row x variant x arm reach table and checks the design's tables against the
probes and stamps. Read-only on the tree. usage:
  reach.py ROOT SCRATCH VARIANT ARM [--stride N] [--jobs N]
ARM is one of ARMS below; `base` is no flag.
"""
import glob, importlib.util, json, os, re, subprocess, sys
from multiprocessing import Pool

# THE CORPUS PATTERN IS DECODED HERE, with emit_sweep.py's own decoder, and
# handed over as raw `--pattern` bytes: `--pattern-esc` is IGNORED by
# `--emit-ir` (cli/main.c returns from the listing branch before the decode
# at :2359), so decfb0's `--pattern-esc` argv would list a different pattern
# than it compiles (rev 2 F-B5).
_spec = importlib.util.spec_from_file_location(
    "emit_sweep", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "../../../../scripts/emit_sweep.py"))
_es = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_es)

ARMS = {
    "base": [],
    "no-pf": ["-fno-prefilter"],
    "pf": ["-fprefilter"],
    "no-pfc": ["-fno-prefilter-collapse"],
    "pfc": ["-fprefilter-collapse"],
    "fof": ["--fast-or-fail"],
    "no-st": ["-fno-size-term"],
    "unroll4": ["--unroll=4"],
    "no-premul": ["-fno-premul-table"],
    "no-anch": ["-fno-anchored-dfa"],
    "vm": ["--engine=vm"],
    "dfa": ["--engine=dfa"],
    "minsize": ["--tune=min-size"],
    "facts": ["--emit-facts=byte"],
}
STAMPS = re.compile(r"^#define RX_(ENGINE|ENGINE_SEL|VM_PREFILTER|VM_PREFILTER_WHY|VM_PREFILTER_LANG|"
                    r"VM_PREFILTER_LANG_WHY|UNROLL_K_WHY) (.*)$", re.M)

def corpus_cases(root):
    seen, out = set(), []
    pcrec = os.path.join(root, "build/pcrec")
    for f in sorted(glob.glob(root + "/tests/**/*.rxt", recursive=True)):
        r = subprocess.run([pcrec, "--list-source", f], capture_output=True, text=True, errors="replace")
        if r.returncode:
            continue
        for ln in r.stdout.split("\n"):
            if not ln or ln.startswith("#"):
                continue
            c = ln.split("\t")
            if c[0] != "pattern" or len(c) < 11:
                continue
            key = (c[4], c[5], c[6], c[8], c[9])
            if key not in seen:
                seen.add(key); out.append(("corpus", key))
    return out

def witness_cases(root):
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "witnesses.tsv")
    out = []
    for ln in open(p):
        if not ln.strip() or ln.startswith("#"):
            continue
        name, pat, flags, feats, enc = (ln.rstrip("\n").split("\t") + ["", "", ""])[:5]
        out.append(("witness:" + name, (pat, flags, feats, enc, "")))
    return out

def argv(comp, key, arm, esc):
    pat, flags, feats, enc, eng = key
    cmd = [comp, "-p", "rx", "-o", "-"]
    if "i" in flags: cmd.append("-i")
    if "u" in flags: cmd.append("--ucp")
    cmd += ["--features", feats or "all"] if not esc else (["--features", feats] if feats else [])
    if enc: cmd += ["-e", enc]
    if eng and arm not in ("vm", "dfa"): cmd += ["--engine=" + eng]
    cmd += ARMS[arm]
    raw = bytes(_es.decode_escape(pat)) if esc else os.fsencode(pat)
    return [os.fsencode(x) for x in cmd] + [b"--pattern", raw]

def run(job):
    root, comp, arm, check, (src, key) = job
    esc = src == "corpus"
    cmd = argv(comp, key, arm, esc)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=120)
    except subprocess.TimeoutExpired:
        return {"src": src, "key": key, "status": "TIMEOUT"}
    st = {m.group(1): m.group(2).strip('"') for m in STAMPS.finditer(r.stdout)}
    probes = [l[6:] for l in r.stderr.split("\n") if l.startswith("DECFB ")]
    notes = [l for l in r.stderr.split("\n") if l.startswith("pcrec: note:")]
    errs = [l for l in r.stderr.split("\n") if l and not l.startswith("DECFB ")]
    rec = {"src": src, "key": key, "status": "ok" if r.returncode == 0 else "refused",
           "rc": r.returncode, "st": st, "pr": probes, "notes": notes,
           "err": errs[-1][:160] if r.returncode and errs else ""}
    if r.returncode == 0 and st.get("ENGINE") == "vm":
        c2 = [x for x in cmd if x not in (b"-o", b"-")]
        c2.insert(1, b"--emit-ir")
        try:
            r2 = subprocess.run(c2, capture_output=True, text=True, errors="replace", timeout=120)
            m = re.search(r"^prefilter\t([^\t\n]*)", r2.stdout, re.M)
            rec["ir_pf"] = m.group(1) if m else ("<rc%d>" % r2.returncode)
        except subprocess.TimeoutExpired:
            rec["ir_pf"] = "<timeout>"
    if check:
        r0 = subprocess.run([os.fsencode(os.path.join(root, "build/pcrec"))] + cmd[1:], capture_output=True,
                            text=True, errors="replace", timeout=120)
        if r0.stdout != r.stdout or r0.returncode != r.returncode:
            rec["bytes_diff"] = 1
    return rec

def main():
    root, scratch, variant, arm = sys.argv[1:5]
    stride, jobs = 1, 6
    a = sys.argv[5:]
    if "--stride" in a: stride = int(a[a.index("--stride") + 1])
    if "--jobs" in a: jobs = int(a[a.index("--jobs") + 1])
    comp = os.path.join(scratch, "pcrec_" + variant)
    cases = corpus_cases(root)[::stride] + witness_cases(root)
    check = variant == "plain" and arm == "base"
    with Pool(jobs) as p:
        res = p.map(run, [(root, comp, arm, check, c) for c in cases], chunksize=16)
    out = os.path.join(scratch, "reach_%s_%s.jsonl" % (variant, arm))
    with open(out, "w") as o:
        for rec in res:
            o.write(json.dumps(rec) + "\n")
    print(variant, arm, "cases", len(cases), "stride", stride, "->", out)

if __name__ == "__main__":
    main()
