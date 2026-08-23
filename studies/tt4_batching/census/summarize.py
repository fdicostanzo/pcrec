#!/usr/bin/env python3
"""studies/tt4_batching/census/summarize.py — [TT-4.1] Stage A summarizer.

Reads build/tt4_census/census.tsv (the combined gcc/cc/pcrec shim log,
written by run_section_census.sh) plus each section's build/tt4_census/
<section>.time (`/usr/bin/time -v` report) and prints, per section:

  - invocation counts by tool/class (pcrec; gcc one-shot / compile-c /
    link-only; cc likewise if it appears)
  - core-seconds spent inside gcc/cc (sum of per-call wall — see the header
    note below) and inside pcrec
  - section wall clock and CPU (user+sys) from /usr/bin/time -v
  - a derived "remainder" = section wall - (gcc core-sec + pcrec core-sec),
    which is NOT a clean number when a section's internal PROCS parallelism
    overlaps calls (core-seconds can exceed wall clock) -- reported as-is,
    both raw core-sec figures and the remainder's sign are the honest
    output rather than a clamped one.

Usage: python3 summarize.py [OUTDIR]   (default: <repo>/build/tt4_census)
"""
import sys
import os
import re
import glob

def load_census(path):
    rows = []
    with open(path) as f:
        for lineno, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) != 7:
                print(f"WARNING: {path}:{lineno}: malformed record ({len(parts)} fields, want 7): {line!r}", file=sys.stderr)
                continue
            epoch, wall, cls, section, rc, tool, argc = parts
            try:
                rows.append({
                    "epoch": float(epoch), "wall": float(wall), "class": cls,
                    "section": section, "rc": int(rc), "tool": tool, "argc": int(argc),
                })
            except ValueError:
                print(f"WARNING: {path}:{lineno}: unparseable numeric field: {line!r}", file=sys.stderr)
    return rows

def parse_time_v(path):
    """Parse /usr/bin/time -v output for wall clock and user+sys CPU."""
    if not os.path.exists(path):
        return None
    text = open(path).read()
    out = {}
    m = re.search(r"Elapsed \(wall clock\) time.*: (.+)", text)
    if m:
        out["wall_str"] = m.group(1).strip()
        out["wall_sec"] = _parse_time_field(out["wall_str"])
    mu = re.search(r"User time \(seconds\): ([\d.]+)", text)
    ms = re.search(r"System time \(seconds\): ([\d.]+)", text)
    if mu and ms:
        out["user_sec"] = float(mu.group(1))
        out["sys_sec"] = float(ms.group(1))
        out["cpu_sec"] = out["user_sec"] + out["sys_sec"]
    mrss = re.search(r"Maximum resident set size \(kbytes\): (\d+)", text)
    if mrss:
        out["max_rss_kb"] = int(mrss.group(1))
    return out

def _parse_time_field(s):
    # h:mm:ss or m:ss.ss
    parts = s.split(":")
    parts = [float(p) for p in parts]
    if len(parts) == 3:
        h, m, sec = parts
        return h * 3600 + m * 60 + sec
    elif len(parts) == 2:
        m, sec = parts
        return m * 60 + sec
    else:
        return parts[0]

def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else None
    if outdir is None:
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        outdir = os.path.join(root, "build", "tt4_census")
    census_path = os.path.join(outdir, "census.tsv")
    if not os.path.exists(census_path):
        print(f"summarize.py: no census log at {census_path}", file=sys.stderr)
        sys.exit(2)
    rows = load_census(census_path)

    sections = sorted(set(r["section"] for r in rows))
    # Preserve the Makefile's test: order if every section is present.
    order = ["corpus", "cli", "reject", "registry", "parse", "gentimeout",
              "codegen", "vm", "possessify", "rungselect", "counterk", "mrl",
              "prefilter", "altcls", "assertions", "atomic", "backrefs",
              "encseam", "resource", "capturediff", "known-fail", "thread"]
    sections = [s for s in order if s in sections] + [s for s in sections if s not in order]

    totals = {"gcc_calls": 0, "gcc_core_sec": 0.0, "pcrec_calls": 0, "pcrec_core_sec": 0.0,
              "section_wall": 0.0, "section_cpu": 0.0}
    ranking = []

    print(f"{'section':<13} {'gcc(1shot/c/link)':<20} {'gcc-core-s':>10} {'pcrec#':>7} {'pcrec-core-s':>12} {'sec-wall':>9} {'sec-cpu':>9} {'remainder':>10}")
    print("-" * 100)
    for sec in sections:
        srows = [r for r in rows if r["section"] == sec]
        gcc_rows = [r for r in srows if r["tool"] in ("gcc", "cc")]
        pcrec_rows = [r for r in srows if r["tool"] == "pcrec"]
        one_shot = sum(1 for r in gcc_rows if r["class"] == "one-shot")
        compile_c = sum(1 for r in gcc_rows if r["class"] == "compile-c")
        link_only = sum(1 for r in gcc_rows if r["class"] == "link-only")
        gcc_core = sum(r["wall"] for r in gcc_rows)
        pcrec_core = sum(r["wall"] for r in pcrec_rows)

        tinfo = parse_time_v(os.path.join(outdir, f"{sec}.time"))
        sec_wall = tinfo["wall_sec"] if tinfo and "wall_sec" in tinfo else float("nan")
        sec_cpu = tinfo["cpu_sec"] if tinfo and "cpu_sec" in tinfo else float("nan")
        remainder = sec_wall - gcc_core - pcrec_core if tinfo else float("nan")

        print(f"{sec:<13} {f'{one_shot}/{compile_c}/{link_only}':<20} {gcc_core:>10.2f} {len(pcrec_rows):>7} {pcrec_core:>12.2f} {sec_wall:>9.2f} {sec_cpu:>9.2f} {remainder:>10.2f}")

        totals["gcc_calls"] += len(gcc_rows)
        totals["gcc_core_sec"] += gcc_core
        totals["pcrec_calls"] += len(pcrec_rows)
        totals["pcrec_core_sec"] += pcrec_core
        if tinfo:
            totals["section_wall"] += sec_wall
            totals["section_cpu"] += sec_cpu
        ranking.append((sec, gcc_core))

    print("-" * 100)
    print(f"{'TOTAL':<13} {'gcc calls='+str(totals['gcc_calls']):<20} {totals['gcc_core_sec']:>10.2f} {totals['pcrec_calls']:>7} {totals['pcrec_core_sec']:>12.2f} {totals['section_wall']:>9.2f} {totals['section_cpu']:>9.2f}")

    ranking.sort(key=lambda x: -x[1])
    print("\nRanking by gcc-bound core-seconds (worst first):")
    for sec, core in ranking:
        print(f"  {sec:<13} {core:>10.2f}s")

    # any nonzero exit codes worth flagging
    bad = [r for r in rows if r["rc"] != 0]
    if bad:
        print(f"\n{len(bad)} calls exited nonzero (sections: {sorted(set(r['section'] for r in bad))})")

if __name__ == "__main__":
    main()
