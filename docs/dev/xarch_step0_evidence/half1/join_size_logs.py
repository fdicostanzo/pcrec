#!/usr/bin/env python3
import csv
import statistics
import sys

def load(path):
    rows = {}
    header = None
    with open(path, newline="") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if line.startswith("# pattern"):
                header = line[2:].split("\t")  # strip leading "# "
                continue
            if line.startswith("#") or not line.strip():
                continue
            row = line.split("\t")
            d = dict(zip(header, row))
            # duplicate keys shouldn't happen (one row per pattern id per
            # engine/rungs/prefilter combo -- but key on pattern+engine to
            # be safe against a pattern compiled to two engines)
            key = (d["pattern"], d.get("engine", ""))
            rows[key] = d
    return rows

mac = load(sys.argv[1])
linux = load(sys.argv[2])

mac_keys = set(mac)
linux_keys = set(linux)
common = mac_keys & linux_keys
only_mac = mac_keys - linux_keys
only_linux = linux_keys - mac_keys

print("mac rows: %d, linux rows: %d, common: %d, only-mac: %d, only-linux: %d" % (
    len(mac), len(linux), len(common), len(only_mac), len(only_linux)))

print("\n--- sample only-linux (up to 15) ---")
for k in list(sorted(only_linux))[:15]:
    print(k)
print("\n--- sample only-mac (up to 15) ---")
for k in list(sorted(only_mac))[:15]:
    print(k)

# byte-identity check
movers = []
cpu_ratios = []
wall_ratios = []
by_engine = {}
for k in common:
    m = mac[k]
    l = linux[k]
    msz = int(m["size_bytes"])
    lsz = int(l["size_bytes"])
    if msz != lsz:
        movers.append((k, msz, lsz))
    try:
        mc = float(m["gcc_cpu_s"])
        lc = float(l["gcc_cpu_s"])
        mw = float(m["gcc_wall_s"])
        lw = float(l["gcc_wall_s"])
    except (ValueError, KeyError):
        continue
    if lc > 0:
        ratio = mc / lc
        cpu_ratios.append(ratio)
        eng = m.get("engine", "?")
        by_engine.setdefault(eng, []).append(ratio)
    if lw > 0:
        wall_ratios.append(mw / lw)

print("\nsize_bytes movers (should be 0 at the same commit): %d" % len(movers))
for k, msz, lsz in movers[:15]:
    print(k, msz, lsz)

def report(name, vals):
    if not vals:
        print("%s: no data" % name)
        return
    vals = sorted(vals)
    n = len(vals)
    med = statistics.median(vals)
    q1 = vals[n // 4]
    q3 = vals[(3 * n) // 4]
    p95 = vals[int(n * 0.95)]
    print("%s: n=%d median=%.3f q1=%.3f q3=%.3f p95=%.3f min=%.3f max=%.3f" % (
        name, n, med, q1, q3, p95, vals[0], vals[-1]))

print()
report("gcc_cpu_s ratio (Mac/Linux), ALL", cpu_ratios)
report("gcc_wall_s ratio (Mac/Linux), ALL [load-contaminated, caveat]", wall_ratios)
for eng, vals in sorted(by_engine.items()):
    report("gcc_cpu_s ratio, engine=%s" % eng, vals)
