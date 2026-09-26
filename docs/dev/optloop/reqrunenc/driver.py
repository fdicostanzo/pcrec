#!/usr/bin/env python3
"""[OPT-REQRUN-ENC] D77 census driver, lane reqrunenc, 2026-09-26.

Reuses `_shared_pop.py` (a verbatim copy of the c2/reqpos_census.py census
populations + probe runner — `bench_pop`, `corpus_pop`, `run_probe`) rather
than re-deriving the corpus/bench walk. `reqrunenc_probe` is the SAME
c2/reqpos_probe.c, unmodified, built against this worktree's libpcrec.a
(it already reports `run_hex`, the necessary literal RUN `reqbyte.c`'s own
walk computes, and already takes `-e utf8`).

This driver's OWN job is downstream of that: for every row with a run of
length >= 2, compute the three candidate scan-index rules (L/R/S) directly
off `run_hex`, and report population + mover counts. No clock is read here.
"""
import os, sys, json, collections
import _shared_pop as pop

E = os.environ
OUT = E.get("OUT", ".")

LEAD_LO, LEAD_HI = 0xC2, 0xF4   # valid UTF-8 multi-byte LEAD byte range

def is_lead(b):
    return LEAD_LO <= b <= LEAD_HI

def cand_L(run):
    return 0

def cand_R(run):
    return len(run) - 1

def cand_S(run):
    """Rightmost member that is ASCII (0x00-0x7F) or a CONTINUATION byte
    (0x80-0xBF) -- i.e. the rightmost member that is NOT a lead byte.
    Falls back to leftmost (index 0) when the whole run is lead bytes,
    matching L/`rn_scan_index`'s own universal-fallback shape."""
    for i in range(len(run) - 1, -1, -1):
        if not is_lead(run[i]):
            return i
    return 0

def analyze(rows, enc):
    pop_run = 0          # rows with a run >= 2 bytes
    pop_lead0 = 0         # of those, L's chosen byte (index 0) is a lead byte
    moves = {"R": 0, "S": 0}
    rs_disagree = []
    detail = []
    for r in rows:
        if r["status"] != "ok":
            continue
        rh = r["run_hex"]
        if rh in ("-", "") :
            continue
        run = bytes.fromhex(rh)
        if len(run) < 2:
            continue
        pop_run += 1
        iL, iR, iS = cand_L(run), cand_R(run), cand_S(run)
        bL, bR, bS = run[iL], run[iR], run[iS]
        if is_lead(bL):
            pop_lead0 += 1
        if bR != bL:
            moves["R"] += 1
        if bS != bL:
            moves["S"] += 1
        if bR != bS:
            rs_disagree.append({
                "id": r["id"], "enc": enc, "run_hex": rh,
                "R_idx": iR, "R_byte": "%02x" % bR,
                "S_idx": iS, "S_byte": "%02x" % bS,
            })
        detail.append({
            "id": r["id"], "enc": enc, "run_len": len(run), "run_hex": rh,
            "L_byte": "%02x" % bL, "R_byte": "%02x" % bR, "S_byte": "%02x" % bS,
            "L_lead": is_lead(bL), "R_lead": is_lead(bR), "S_lead": is_lead(bS),
        })
    return {
        "pop_run": pop_run, "pop_lead0": pop_lead0, "moves": moves,
        "rs_disagree": rs_disagree, "detail": detail,
    }

def main():
    result = {}
    for popname, rows in (("bench", pop.bench_pop()), ("corpus", pop.corpus_pop())):
        for enc in ("byte", "utf8"):
            recs = pop.run_probe(rows, enc)
            by = {r["id"]: r for r in recs}
            for i, p in rows:
                if i in by:
                    by[i]["pattern_hex"] = p.hex()
            key = "%s_%s" % (popname, enc)
            result[key] = analyze(list(by.values()), enc)
            print("%s: %d patterns, %d probed, run>=2: %d, lead0: %d, moves R=%d S=%d"
                  % (key, len(rows), len(recs), result[key]["pop_run"],
                     result[key]["pop_lead0"], result[key]["moves"]["R"],
                     result[key]["moves"]["S"]), file=sys.stderr)

    json.dump(result, open(os.path.join(OUT, "reqrunenc_census.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
