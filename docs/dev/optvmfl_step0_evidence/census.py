#!/usr/bin/env python3
"""[OPT-VMFL] STEP 0 measurement (a): has_push vs resume_frames census.

For every corpus + bench pattern, compile with --engine=vm (forced) and
--engine=auto, read the emitted artifact for:
  - RX_RESUME_FRAMES (the .h stamp, the pre-pass ESTIMATE cost.frames+1)
  - whether the fail label carries a `goto *run->resume_stack[...]` dispatch
    (has_push true) or the "NO RESUME FRAME AT ALL" comment (has_push false)
Tabulates the four cells: frames==1/frameless, frames==1/dispatch,
frames>1/frameless, frames>1/dispatch. Named list of every divergent artifact.
"""
import subprocess, sys, os, re, json, glob

PCREC = "/home/duxevents/pcrec/worktrees/vmfl0/build/pcrec"
SCRATCH = "/tmp/claude-1001/-home-duxevents-pcrec/dcce9a31-e3ae-41e3-8913-a4a918af3f32/scratchpad/vmfl0"
OUTDIR = os.path.join(SCRATCH, "census_artifacts")
os.makedirs(OUTDIR, exist_ok=True)

def corpus_patterns():
    pats = set()
    for root, dirs, files in os.walk("/home/duxevents/pcrec/worktrees/vmfl0/tests"):
        for f in files:
            if f.endswith(".rxt"):
                path = os.path.join(root, f)
                with open(path, "r", errors="replace") as fh:
                    for line in fh:
                        if line.startswith("pattern "):
                            pats.add(line[len("pattern "):].rstrip("\n"))
    return sorted(pats)

def bench_patterns():
    out = {}
    for d in ("bounded", "loglines", "email", "altwide"):
        pdir = f"/home/duxevents/pcrec-bench/bench/{d}/patterns"
        pats = []
        for fp in sorted(glob.glob(os.path.join(pdir, "*.rx"))):
            with open(fp, "r", errors="replace") as fh:
                pats.append((os.path.basename(fp), fh.read()))
        out[d] = pats
    return out

def compile_one(pattern, engine, idx, tag):
    """Return dict with compile outcome and, on success, stamp facts."""
    base = os.path.join(OUTDIR, f"{tag}_{idx}_{engine}")
    cfile = base + ".c"
    hfile = base + ".h"
    cmd = [PCREC, f"--engine={engine}", "--features", "all", "-o", cfile, "--", pattern]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        return {"ok": False, "reason": "timeout"}
    if r.returncode != 0:
        return {"ok": False, "reason": "refused", "stderr": r.stderr.strip()[:200]}
    try:
        with open(cfile, "r", errors="replace") as fh:
            ctext = fh.read()
        htext = ""
        if os.path.exists(hfile):
            with open(hfile, "r", errors="replace") as fh:
                htext = fh.read()
    except OSError as e:
        return {"ok": False, "reason": f"readfail:{e}"}

    m = re.search(r'#define\s+RX_ENGINE\s+"(\w+)"', ctext) or re.search(r'#define\s+RX_ENGINE\s+"(\w+)"', htext)
    engine_actual = m.group(1) if m else None
    vm_pref = None
    mp = re.search(r'#define\s+RX_VM_PREFILTER\s+"([\w-]+)"', ctext) or re.search(r'#define\s+RX_VM_PREFILTER\s+"([\w-]+)"', htext)
    if mp:
        vm_pref = mp.group(1)

    result = {"ok": True, "engine_actual": engine_actual, "vm_prefilter": vm_pref}

    if engine_actual == "vm":
        fm = re.search(r'#define\s+RX_RESUME_FRAMES\s+(\d+)', htext) or re.search(r'#define\s+RX_RESUME_FRAMES\s+(\d+)', ctext)
        frames = int(fm.group(1)) if fm else None
        has_goto = "goto *run->resume_stack" in ctext
        has_frameless_comment = "NO RESUME FRAME AT ALL" in ctext
        result["frames"] = frames
        result["has_push"] = bool(has_goto)
        result["frameless_comment"] = bool(has_frameless_comment)
        # sanity: exactly one of the two markers should be present
        result["marker_consistent"] = (has_goto != has_frameless_comment)
    result["cfile"] = cfile
    result["hfile"] = hfile
    return result

def main():
    cpats = corpus_patterns()
    bpats = bench_patterns()
    print(f"corpus unique patterns: {len(cpats)}", file=sys.stderr)
    total_bench = sum(len(v) for v in bpats.values())
    print(f"bench patterns: {total_bench}", file=sys.stderr)

    all_items = [("corpus", None, p) for p in cpats]
    for d, plist in bpats.items():
        for name, p in plist:
            all_items.append((f"bench-{d}", name, p))

    census = {"corpus": [], "bench": {}}
    cells = {"f1_frameless": [], "f1_dispatch": [], "fgt1_frameless": [], "fgt1_dispatch": []}
    auto_vm_count = 0
    auto_hybrid_count = 0
    auto_dfa_count = 0
    refused_vm = 0
    total_vm_ok = 0
    divergent = []
    inconsistent = []

    for i, (group, name, pattern) in enumerate(all_items):
        tag = re.sub(r'[^A-Za-z0-9]+', '_', f"{group}_{name or i}")[:60]
        vm_res = compile_one(pattern, "vm", i, tag)
        auto_res = compile_one(pattern, "auto", i, tag)

        if not vm_res.get("ok"):
            refused_vm += 1
            continue
        total_vm_ok += 1
        frames = vm_res.get("frames")
        has_push = vm_res.get("has_push")
        if not vm_res.get("marker_consistent", True):
            inconsistent.append({"pattern": pattern, "group": group, "name": name})

        rec = {
            "pattern": pattern, "group": group, "name": name,
            "frames": frames, "has_push": has_push,
        }
        if auto_res.get("ok"):
            ea = auto_res.get("engine_actual")
            if ea == "dfa":
                auto_dfa_count += 1
            elif ea == "vm":
                vp = auto_res.get("vm_prefilter")
                if vp == "hybrid":
                    auto_hybrid_count += 1
                else:
                    auto_vm_count += 1
            rec["auto_engine"] = ea
            rec["auto_vm_prefilter"] = auto_res.get("vm_prefilter")

        if frames is not None:
            if frames == 1 and has_push is False:
                cells["f1_frameless"].append(rec)
            elif frames == 1 and has_push is True:
                cells["f1_dispatch"].append(rec)
                divergent.append(rec)
            elif frames is not None and frames > 1 and has_push is False:
                cells["fgt1_frameless"].append(rec)
                divergent.append(rec)
            elif frames is not None and frames > 1 and has_push is True:
                cells["fgt1_dispatch"].append(rec)

    summary = {
        "total_items": len(all_items),
        "vm_compiled_ok": total_vm_ok,
        "vm_refused": refused_vm,
        "cell_counts": {k: len(v) for k, v in cells.items()},
        "auto_dfa": auto_dfa_count,
        "auto_vm_plain": auto_vm_count,
        "auto_vm_hybrid": auto_hybrid_count,
        "divergent_count": len(divergent),
        "inconsistent_marker_count": len(inconsistent),
    }
    print(json.dumps(summary, indent=2))

    with open(os.path.join(SCRATCH, "census_result.json"), "w") as fh:
        json.dump({"summary": summary, "divergent": divergent, "inconsistent": inconsistent,
                    "cells": {k: [{"pattern": r["pattern"], "group": r["group"], "name": r["name"]} for r in v] for k, v in cells.items()}},
                   fh, indent=2)

if __name__ == "__main__":
    main()
