#!/usr/bin/env python3
"""studies/tt4_batching/census/summarize_a2.py — [TT-4.1] Stage A2
summarizer: attributes a section's CPU across gcc, pcrec, matcher-runs
(the compiled `t` binary, timed via shim/timeout's `driver-target` class),
python3 (by script), and a residue ("everything else" -- bash itself,
fork/exec overhead, anything not invoked by a shimmed name).

IMPORTANT double-counting note: pcrec is invoked as `timeout N "$PCREC" ...`
(tests/harness/run.sh:262), so ONE logical pcrec call produces TWO log
records -- shim/timeout logs it as class=pcrec-target (the wrapping
timeout process's own total wall, a SUPERSET including fork/exec/timeout
overhead), and shim/pcrec (since PCREC= points at the pcrec shim) logs the
REAL BINARY's own wall directly (a SUBSET). This script uses the DIRECT
tool=pcrec records as the authoritative pcrec core-time (matching Stage
A's own number, so the two memos are comparable) and folds the
timeout-wrapper's own marginal overhead (pcrec-target core-s minus direct
pcrec core-s) into the residue bucket rather than double-counting it as
pcrec time.

Usage: summarize_a2.py [OUTDIR]  (default: <repo>/build/tt4_census_a2)
"""
import sys
import os
import re

def parse_time_v(path):
    if not os.path.exists(path):
        return None
    text = open(path).read()
    out = {}
    m = re.search(r"Elapsed \(wall clock\) time.*: (.+)", text)
    if m:
        out["wall_sec"] = _parse_time_field(m.group(1).strip())
    mu = re.search(r"User time \(seconds\): ([\d.]+)", text)
    ms = re.search(r"System time \(seconds\): ([\d.]+)", text)
    if mu and ms:
        out["cpu_sec"] = float(mu.group(1)) + float(ms.group(1))
    return out

def _parse_time_field(s):
    parts = [float(p) for p in s.split(":")]
    if len(parts) == 3:
        return parts[0]*3600 + parts[1]*60 + parts[2]
    elif len(parts) == 2:
        return parts[0]*60 + parts[1]
    return parts[0]

def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else None
    if outdir is None:
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        outdir = os.path.join(root, "build", "tt4_census_a2")
    census_path = os.path.join(outdir, "census.tsv")
    rows = []
    with open(census_path) as f:
        for lineno, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) != 7:
                print(f"WARNING: {census_path}:{lineno}: malformed record: {line!r}", file=sys.stderr)
                continue
            epoch, wall, cls, section, rc, tool, argc = parts
            try:
                rows.append({"wall": float(wall), "class": cls, "section": section,
                             "rc": int(rc), "tool": tool})
            except ValueError:
                continue

    sections = sorted(set(r["section"] for r in rows))
    order = ["corpus", "assertions", "rungselect", "counterk", "backrefs", "mrl", "altcls"]
    sections = [s for s in order if s in sections] + [s for s in sections if s not in order]

    print(f"{'section':<12} {'gcc-s':>9} {'pcrec#':>7} {'pcrec-s':>9} {'runs#':>7} {'runs-wallsum':>12} {'py3-s':>8} {'sec-wall':>9} {'sec-cpu':>9} {'residue*':>9} {'residue%':>9}")
    print("-" * 130)
    print("(* residue = sec-cpu - gcc-s - pcrec-s - py3-s ONLY -- runs-wallsum is NOT")
    print("   subtracted; see the note below on why it cannot be treated as core-seconds)")
    py3_by_script_total = {}
    for sec in sections:
        srows = [r for r in rows if r["section"] == sec]
        gcc_rows = [r for r in srows if r["tool"] in ("gcc", "cc")]
        gcc_core = sum(r["wall"] for r in gcc_rows)

        pcrec_rows = [r for r in srows if r["tool"] == "pcrec"]
        pcrec_core = sum(r["wall"] for r in pcrec_rows)

        run_rows = [r for r in srows if r["tool"] == "timeout" and r["class"] == "driver-target"]
        run_core = sum(r["wall"] for r in run_rows)

        py3_rows = [r for r in srows if r["tool"] == "python3"]
        py3_core = sum(r["wall"] for r in py3_rows)
        for r in py3_rows:
            script = r["class"].replace("script:", "")
            py3_by_script_total.setdefault(sec, {}).setdefault(script, 0.0)
            py3_by_script_total[sec][script] += r["wall"]

        tinfo = parse_time_v(os.path.join(outdir, f"{sec}.time"))
        sec_wall = tinfo["wall_sec"] if tinfo and "wall_sec" in tinfo else float("nan")
        sec_cpu = tinfo["cpu_sec"] if tinfo and "cpu_sec" in tinfo else float("nan")
        # residue excludes run_core deliberately -- see the module docstring
        # and the printed note: at ~19k near-instant spawns, summed WALL
        # time is inflated by scheduling queue wait, not real CPU, and can
        # (does, for `corpus`) exceed the section's own measured CPU-seconds.
        attributed = gcc_core + pcrec_core + py3_core
        residue = sec_cpu - attributed if tinfo else float("nan")
        residue_pct = (residue / sec_cpu * 100) if tinfo and sec_cpu else float("nan")

        print(f"{sec:<12} {gcc_core:>9.2f} {len(pcrec_rows):>7} {pcrec_core:>9.2f} "
              f"{len(run_rows):>7} {run_core:>12.2f} {py3_core:>8.2f} {sec_wall:>9.2f} "
              f"{sec_cpu:>9.2f} {residue:>9.2f} {residue_pct:>8.1f}%")

    print("\npython3 core-seconds by script, per section:")
    for sec, scripts in py3_by_script_total.items():
        for script, t in sorted(scripts.items(), key=lambda x: -x[1]):
            print(f"  {sec:<12} {script:<30} {t:.2f}s")

    # other/unrecognised timeout targets
    other = [r for r in rows if r["tool"] == "timeout" and r["class"] not in ("pcrec-target", "driver-target")]
    if other:
        print(f"\n{len(other)} timeout calls with an unrecognised target class:")
        classes = {}
        for r in other:
            classes.setdefault(r["class"], 0)
            classes[r["class"]] += 1
        for c, n in sorted(classes.items(), key=lambda x: -x[1]):
            print(f"  {c}: {n}")

if __name__ == "__main__":
    main()
