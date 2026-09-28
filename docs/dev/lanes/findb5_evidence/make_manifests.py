#!/usr/bin/env python3
"""[FINDINGS] B5 (lane findb5): writes design §11.3's named mover manifests,
tests/findings/manifests/ship_<name>_movers.txt, from one or more
ship_census.json files (ship_census.py) — one row per moved ARTIFACT-CONFIG
(population, config, encoding, pattern key), naming every RX_* stamp that
moved (`program` = a non-stamp line moved too), with the REACH and
population counts in the header. An EMPTY manifest is reported as empty,
never as "no hazard" (K59); R31: a bundle whose census is empty does not ship.

  python3 make_manifests.py OUTDIR census.json [census.json ...]
"""
import collections, json, sys

out, files = sys.argv[1], sys.argv[2:]
res = [r for f in files for r in json.load(open(f))]
for n in ("weblog", "log"):
    rows, head = [], []
    for enc in ("byte", "utf8"):
        rs = [r for r in res if r["enc"] == enc]
        ch = [r for r in rs if r.get("ship_" + n) == "changed"]
        reach = sum(1 for r in rs if (r.get("findings_" + n) or "").startswith(f"byte-rate={n}:"))
        pops = dict(collections.Counter(r["pop"] for r in rs))
        head.append(f"#   -e {enc}: {len(rs)} artifact-configs {pops}, "
                    f"{reach} consumed byte-rate={n}, MOVERS {len(ch)}")
        for r in sorted(ch, key=lambda r: (r["pop"], r["src"], r["key"], r["cfg"])):
            key = r["key"].encode("unicode_escape").decode("ascii")
            rows.append(f"{enc}\t{r['pop']}:{r['src']}\t{r['cfg']}\t"
                        f"{','.join(r['moved_' + n])}\t{key}")
    with open(f"{out}/ship_{n}_movers.txt", "w") as fh:
        fh.write(f"""# tests/findings/manifests/ship_{n}_movers.txt — [FINDINGS] B5's R35
# census for the shipped `{n}` analysis (design §11.3 `ship_<name>_movers`):
# every artifact-config whose emitted C moves between `pcrec` (no analysis
# named) and `pcrec --analysis {n}`, after deleting §7's named lines (the
# RX_FINDINGS stamp, the `.findings =` initializer, the rx_info member) by
# name and nothing else. Produced by
# docs/dev/lanes/findb5_evidence/ship_census.py + make_manifests.py (lane
# findb5) over: {", ".join(files)}.
# Per encoding:
""" + "\n".join(head) + """
# Columns: encoding, population:source, config, stamps moved, pattern
# (python unicode_escape).
""")
        fh.write("\n".join(rows) + ("\n" if rows else ""))
    print(f"ship_{n}_movers.txt: {len(rows)} rows")
