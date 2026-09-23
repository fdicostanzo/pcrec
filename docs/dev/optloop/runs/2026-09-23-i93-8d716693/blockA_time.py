#!/usr/bin/env python3
import subprocess, statistics, sys, time, os

WORK = "/tmp/optloop3/blockA/work"
SUBJECTS = [
    "/home/duxevents/pcrec-bench/bench/capability/throughput/t-64k.bin",
    "/home/duxevents/pcrec-bench/bench/capability/throughput/t-256k.bin",
    "/home/duxevents/pcrec-bench/bench/capability/throughput/t-1m.bin",
]
PATTERNS = ["router-prefix-order", "uuid-near-miss", "ipv4-near-miss",
            "wild-codegrammar-json-array-begin"]
VARIANTS = ["default", "noreqbyte", "noendwin", "noboth"]
TRIALS = 5

def run_one(binpath, subject):
    out = subprocess.run([binpath, subject, "5"], capture_output=True, text=True, timeout=60)
    line = out.stdout.strip()
    # format: "<subj> n=%ld matches=%ld best=%.9f s  %.4f ns/byte"
    parts = line.split()
    best_s = None
    matches = None
    for i, p in enumerate(parts):
        if p.startswith("best="):
            best_s = float(p.split("=")[1])
        if p.startswith("matches="):
            matches = int(p.split("=")[1])
    if best_s is None:
        raise RuntimeError(f"could not parse: {line!r} (stderr={out.stderr!r})")
    return best_s, matches, line

def main():
    print("uptime before:", subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip())
    results = {p: {v: [] for v in VARIANTS} for p in PATTERNS}
    matches_seen = {p: {v: [] for v in VARIANTS} for p in PATTERNS}
    for trial in range(1, TRIALS + 1):
        for pat in PATTERNS:
            for variant in VARIANTS:
                binpath = os.path.join(WORK, f"{pat}__{variant}")
                total_ns = 0.0
                mlist = []
                for subj in SUBJECTS:
                    best_s, matches, line = run_one(binpath, subj)
                    total_ns += best_s * 1e9
                    mlist.append(matches)
                results[pat][variant].append(total_ns)
                matches_seen[pat][variant].append(tuple(mlist))
                print(f"trial={trial} {pat:38s} {variant:10s} total_ns={total_ns:.3f} matches={mlist}")
    print("uptime after:", subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip())

    print("\n# SUMMARY (median of 5 trials, ns for the 3-subject throughput sum)")
    for pat in PATTERNS:
        base_median = statistics.median(results[pat]["default"])
        print(f"\n== {pat} ==")
        for variant in VARIANTS:
            vals = results[pat][variant]
            med = statistics.median(vals)
            iqr = sorted(vals)[3] - sorted(vals)[1]
            delta_pct = (med - base_median) / base_median * 100
            # matches consistency check
            m_sets = set(matches_seen[pat][variant])
            print(f"  {variant:10s} median={med:14.3f} ns  IQR={iqr:10.3f}  Delta_vs_default={delta_pct:+8.4f}%  matches(all trials)={m_sets}")

if __name__ == "__main__":
    main()
