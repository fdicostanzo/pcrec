#!/usr/bin/env python3
import subprocess, statistics, os

WORK = "/tmp/optloop3/blockD"
SUBJECTS = [
    "/home/duxevents/pcrec-bench/bench/capability/throughput/t-64k.bin",
    "/home/duxevents/pcrec-bench/bench/capability/throughput/t-256k.bin",
    "/home/duxevents/pcrec-bench/bench/capability/throughput/t-1m.bin",
]
VARIANTS = ["bin_a_asis", "bin_b_deleted", "bin_c_moved", "bin_d_nopartial"]
TRIALS = 5

def run_one(binpath, subject):
    out = subprocess.run([binpath, subject, "5"], capture_output=True, text=True, timeout=60)
    line = out.stdout.strip()
    parts = line.split()
    best_s = None
    matches = None
    for p in parts:
        if p.startswith("best="):
            best_s = float(p.split("=")[1])
        if p.startswith("matches="):
            matches = int(p.split("=")[1])
    if best_s is None:
        raise RuntimeError(f"could not parse: {line!r} stderr={out.stderr!r}")
    return best_s, matches

def main():
    print("uptime before:", subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip())
    results = {v: [] for v in VARIANTS}
    matches_seen = {v: [] for v in VARIANTS}
    for trial in range(1, TRIALS + 1):
        for variant in VARIANTS:
            binpath = os.path.join(WORK, variant)
            total_ns = 0.0
            mlist = []
            for subj in SUBJECTS:
                best_s, matches = run_one(binpath, subj)
                total_ns += best_s * 1e9
                mlist.append(matches)
            results[variant].append(total_ns)
            matches_seen[variant].append(tuple(mlist))
            print(f"trial={trial} {variant:16s} total_ns={total_ns:.3f} matches={mlist}")
    print("uptime after:", subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip())

    print("\n# SUMMARY (median of 5 trials, ns for the 3-subject throughput sum)")
    base_median = statistics.median(results["bin_a_asis"])
    for variant in VARIANTS:
        vals = results[variant]
        med = statistics.median(vals)
        iqr = sorted(vals)[3] - sorted(vals)[1]
        delta_pct = (med - base_median) / base_median * 100
        m_sets = set(matches_seen[variant])
        print(f"  {variant:16s} median={med:14.3f} ns  IQR={iqr:10.3f}  Delta_vs_a={delta_pct:+8.4f}%  matches(all trials)={m_sets}")

if __name__ == "__main__":
    main()
