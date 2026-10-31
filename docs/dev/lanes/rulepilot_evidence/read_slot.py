#!/usr/bin/env python3
"""rulepilot: the timing slot's raw launches -> search.py's dataset (pricing_rulepilot.md §5).

Reads every OUT/time/raw_RP*.tsv (grid2 time.sh's raw file: phase cell subject mode round pos arm
ns answer load1 ts; a re-queued group's later launches replace its earlier ones), OUT/excluded
(arms the correctness gate failed: dropped, and a pick that lands on one falls back to the
default, counted), OUT/subj_rp.tsv (the COUNTED density of every subject), and the committed
inventory (census.jsonl: picks, stamps; facts.tsv: the pieces). Stratum = the site's
differing-slot signature among its timed arms (census_dry.py's stamp-to-slot map).

usage: read_slot.py OUT DATASET.json      then: search.py DATASET.json
"""
import csv, glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import census_dry as cd  # noqa: E402
import pieces as pc      # noqa: E402

INV = os.environ.get("RP_INV", os.path.join(HERE, "inventory"))

def main():
    out, dst = sys.argv[1], sys.argv[2]
    raw = {}
    for f in sorted(glob.glob(os.path.join(out, "time", "raw_RP*.tsv"))):
        for r in csv.DictReader(open(f), delimiter="\t"):
            k = (r["cell"], r["subject"], r["arm"], int(r["round"]))
            if k not in raw or float(r["ts"]) >= raw[k][1]:
                raw[k] = (float(r["ns"]), float(r["ts"]))
    excl = set()
    if os.path.exists(os.path.join(out, "excluded")):
        excl = {tuple(l.split()) for l in open(os.path.join(out, "excluded")) if l.strip()}
    facts = {}
    for r in csv.DictReader(open(os.path.join(INV, "facts.tsv")), delimiter="\t", quoting=csv.QUOTE_NONE):
        facts[r["id"]] = json.loads(r["facts_json"])
    sites, fell_back, dropped = [], 0, 0
    for line in open(os.path.join(INV, "census.jsonl")):
        c = json.loads(line)
        cell = "rp-" + c["id"]
        cells = {}
        for (ce, subj, arm, rnd), (ns, _) in raw.items():
            if ce != cell or (cell, arm.split("#")[0]) in excl:
                continue
            reg, L = subj.split("_")[-1][0], subj.split("_")[-1][1:-2]
            key = f"{'miss' if reg == 'm' else 'dense'}/{L}"
            v = cells.setdefault(key, {}).setdefault(arm, {})
            v[rnd] = ns
        if not cells:
            continue
        cells = {k: {a: [v[r] for r in sorted(v)] for a, v in av.items()} for k, av in cells.items()}
        timed = {a for av in cells.values() for a in av if "#" not in a}
        dropped += sum(1 for a in c["arms"] if a["arm"] not in timed)
        picks = {}
        for p, a in c["picks"].items():
            if a in timed:
                picks[p] = a
            else:
                picks[p] = "a0"; fell_back += a is not None and a != "a0"
        st = {a["arm"]: a["stamps"] for a in c["arms"] if a["arm"] in timed}
        keys = {k for s in st.values() for k in s}
        sig = sorted({cd.STAMP_SLOT[k] for k in keys if len({s.get(k) for s in st.values()}) > 1})
        sites.append(dict(id=c["id"], stratum="+".join(sig) or "(bytes only)",
                          pieces=pc.values(facts.get(c["id"], {}), " ".join(c["popts"])),
                          picks=picks, cells=cells))
    names = [l.split("\t")[0] for l in open(os.path.join(INV, "vocabulary.tsv")).read().splitlines()[1:]]
    json.dump(dict(picks=names, sites=sites), open(dst, "w"))
    print(f"read_slot: sites {len(sites)}, raw launches {len(raw)}, excluded arms {len(excl)}, "
          f"census arms not timed {dropped}, picks fallen back to default {fell_back}")

if __name__ == "__main__":
    main()
