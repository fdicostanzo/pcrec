#!/usr/bin/env python3
"""[OPT-REQRUN-ENC] census item 3 -- the memchr candidate-rate cost proxy.

Imports pcrec-bench's `bench/utf8/gen_throughput_subjects.py` `build()`
(a pure function: seeds a deterministic RNG and returns the seven
throughput texts in memory -- it does NOT write to pcrec-bench; only
`main()` does that, and this script never calls it) to get the exact bytes
the bench's O-60 timing cells ran against, read-only.

For each O-60 witness pattern and each candidate (L/R/S), counts
occurrences of the chosen scan byte in the witness's own throughput
subject text (occurrences/KB -- the memchr candidate rate).
"""
import os, sys, json

BENCH = os.environ.get("BENCH", "/Users/fdicostanzo/pcrec-bench")
sys.path.insert(0, os.path.join(BENCH, "bench", "utf8"))
sys.path.insert(0, BENCH)

import gen_throughput_subjects as gts  # noqa: E402

texts = {sid: body for sid, body, _desc in gts.build()}

# O-60 §3 witnesses: (pattern id, run bytes hex as compiled -e utf8, subject id)
# run_hex/req_byte read from O-60's own text (outbox_to_pcrec.md "## O-60").
WITNESSES = [
    ("lit-offset-at-tail", "é@", bytes.fromhex("c3a940"), "t-64k-lat"),
    ("lit-cyr-run",        "Москва (prefix)", bytes.fromhex("d09cd0bed181d0ba"), "t-64k-cyr"),
    ("lit-run-3",          "日本語", bytes.fromhex("e697a5e69cace8aa9e"), "t-64k-cjk"),
    ("lit-mixed-ascii",    "user@例え.jp (prefix)", bytes.fromhex("7573657240e4be8b"), "t-64k-asc"),
]

LEAD_LO, LEAD_HI = 0xC2, 0xF4
def is_lead(b): return LEAD_LO <= b <= LEAD_HI

def cand_S(run):
    for i in range(len(run) - 1, -1, -1):
        if not is_lead(run[i]):
            return i
    return 0

rows = []
for pid, label, run, subj_id in WITNESSES:
    subj = texts[subj_id]
    kb = len(subj) / 1024.0
    iL, iR, iS = 0, len(run) - 1, cand_S(run)
    for name, idx in (("L", iL), ("R", iR), ("S", iS)):
        b = run[idx]
        cnt = subj.count(bytes([b]))
        rows.append({
            "pattern": pid, "label": label, "subject": subj_id,
            "candidate": name, "byte": "%02x" % b, "count": cnt,
            "per_kb": round(cnt / kb, 3),
        })

for r in rows:
    print("%-20s %-9s cand=%s byte=0x%s count=%-8d per_kb=%s"
          % (r["pattern"], r["subject"], r["candidate"], r["byte"],
             r["count"], r["per_kb"]))

json.dump(rows, open(os.path.join(os.environ.get("OUT", "."), "reqrunenc_scanrate.json"), "w"), indent=1)
