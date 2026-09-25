#!/usr/bin/env python3
"""The [B84] pin pair's NULL BAND: the Δ% distribution, b1885a83 -> 6ef76820,
over every cell whose artifact is PROGRAM-IDENTICAL across the pin
(nullctl.json; testee -> build config: vm-in-caps shares vm-caps' build),
banded by regime and by BEFORE-median scale (the I-104 bands).  Reads
$SCR/cells.json and $SCR/nullctl.json; writes $SCR/nullband.json."""
import os, json, collections
SCR = os.environ["SCR"]
cells = json.load(open(f"{SCR}/cells.json")); ident = json.load(open(f"{SCR}/nullctl.json"))
CFG = {"auto-caps": "auto-caps", "auto-nocaps": "auto-nocaps", "vm-caps": "vm-caps", "vm-in-caps": "vm-caps"}
def scale(ns): return ">=1us" if ns >= 1000 else ("100ns-1us" if ns >= 100 else "<100ns")
bands = collections.defaultdict(list); rows = []
for k, a in cells.items():
    pin, t, pat, reg = k.split("|")
    if pin != "6ef76820": continue
    b = cells.get(f"b1885a83|{t}|{pat}|{reg}")
    v = ident.get(f"{pat}|{CFG[t]}", {})
    # wild-logparse-syslogbase-expanded's two auto artifacts differ ONLY in the
    # RX_VM_PREFILTER_LANG_WHY size figure (the new stamp line's own 29 bytes
    # in the counted C), so they are program-identical in substance.
    same = v.get("identity") == "identical" or pat == "wild-logparse-syslogbase-expanded"
    if not b or not same: continue
    if a["median"] is None or b["median"] is None: continue
    d = 100.0 * (a["median"] - b["median"]) / b["median"]
    key = f"{reg}|{scale(b['median'])}"
    bands[key].append(d); rows.append((d, pat, reg, t, b["median"], a["median"]))
out = {}
for key, ds in sorted(bands.items()):
    ds.sort(); out[key] = {"n": len(ds), "min": ds[0], "max": ds[-1], "median": ds[len(ds)//2]}
    print(f"{key:40s} n={len(ds):4d} min={ds[0]:+8.3f}% max={ds[-1]:+8.3f}% median={ds[len(ds)//2]:+7.3f}%")
allds = sorted(r[0] for r in rows)
print(f"ALL n={len(allds)} min={allds[0]:+.3f}% max={allds[-1]:+.3f}%")
rows.sort()
print("worst 8 up:"); [print("  %+8.3f%% %s %s %s %.1f->%.1f" % r) for r in rows[-8:]]
print("worst 4 down:"); [print("  %+8.3f%% %s %s %s %.1f->%.1f" % r) for r in rows[:4]]
json.dump({"bands": out, "n": len(allds), "worst": rows[-10:]}, open(f"{SCR}/nullband.json", "w"), indent=1)
