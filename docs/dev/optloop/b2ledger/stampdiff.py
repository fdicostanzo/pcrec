#!/usr/bin/env python3
"""Compile every capability pattern with the ledger pin (b1885a83) and the
admission fix (cb437f26) under the bench's three distinct build configs, and
report the REQ_BYTE / REQ_RUN / REQ_WHY stamps plus whether the emitted
pre-check text is present."""
import os, re, subprocess, sys, json

SCR = os.environ["SCR"]
PATDIR = "/Users/fdicostanzo/pcrec-bench/bench/capability/patterns"
LEDGER = f"{SCR}/src_ledger/build/pcrec"
FIX    = f"{SCR}/src_fix/build/pcrec"

CONFIGS = {
    "auto-caps":   ["--features", "all"],
    "auto-nocaps": ["--features", "all", "--no-captures"],
    "vm-caps":     ["--features", "all", "--engine=vm"],
}

STAMPS = ["RX_REQ_BYTE", "RX_REQ_RUN", "RX_REQ_WHY", "RX_ENGINE",
          "RX_DFA_PREFILTER", "RX_VM_PREFILTER", "RX_VM_START",
          "RX_END_WINDOW", "RX_ENGINE_WHY", "RX_DFA_START"]

def emit(binpath, pattern, flags, outdir):
    """Compile to the SAME -o basename in a per-binary directory (the
    -o-basename trap: two different output NAMES are two different artifacts)."""
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "a.c")
    r = subprocess.run([binpath, "-p", "rx", "-o", out, "--pattern", pattern] + flags,
                       capture_output=True, timeout=120)
    if r.returncode != 0:
        return None, r.stderr.decode(errors="replace").strip()[:200]
    with open(out, "r", errors="replace") as f:
        return f.read(), None

def stamps_of(text):
    d = {}
    for s in STAMPS:
        m = re.search(r'^#define\s+%s\s+(.*)$' % s, text, re.M)
        d[s] = m.group(1).strip() if m else None
    return d

def precheck_of(text):
    """Structural read of the emitted pre-check: the memchr the necessary-byte
    check runs, and tier 2b's run scan loop."""
    memchrs = re.findall(r'memchr\(\s*subject\s*\+\s*([A-Za-z_0-9]+)\s*,\s*(\d+)\s*,', text)
    has_run_loop = "rp_c" in text or "req_run" in text.lower()
    return {"memchr_sites": memchrs, "run_loop": has_run_loop,
            "string_h": "#include <string.h>" in text}

def main():
    pats = sorted(p[:-3] for p in os.listdir(PATDIR) if p.endswith(".rx"))
    rows = []
    for name in pats:
        with open(os.path.join(PATDIR, name + ".rx"), "rb") as f:
            pat = f.read().rstrip(b"\n").decode("utf-8", errors="surrogateescape")
        for cfg, flags in CONFIGS.items():
            lt, lerr = emit(LEDGER, pat, flags, f"{SCR}/stamps/led")
            ft, ferr = emit(FIX,    pat, flags, f"{SCR}/stamps/fix")
            row = {"pattern": name, "config": cfg,
                   "ledger_err": lerr, "fix_err": ferr}
            if lt is not None:
                row["ledger"] = stamps_of(lt); row["ledger_pc"] = precheck_of(lt)
            if ft is not None:
                row["fix"] = stamps_of(ft); row["fix_pc"] = precheck_of(ft)
            rows.append(row)
        sys.stderr.write(".")
        sys.stderr.flush()
    sys.stderr.write("\n")
    with open(f"{SCR}/stampdiff.json", "w") as f:
        json.dump(rows, f, indent=1)
    print(f"{len(rows)} rows -> {SCR}/stampdiff.json")

main()
