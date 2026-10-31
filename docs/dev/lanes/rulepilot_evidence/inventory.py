#!/usr/bin/env python3
"""rulepilot step 1, the INVENTORY (docs/design/pricing_rulepilot.md §2).

COMPILE-ONLY. Re-runs the bake-off's dry census walk (census_dry.py, copied verbatim from
lane/bakeoff2 b8a321ae3, sha256 b115709e...) on THIS worktree's build/pcrec over the 177 J1
questions (docs/dev/lanes/rwquest/questions.tsv), then adds what the pilot needs:

  - every PICK of the pilot's vocabulary (a flag set, PICKS below) compiled on every site and
    mapped to an arm by byte identity (census_dry's rule); a pick whose bytes no census arm has
    adds a `pick-only` arm, so every pick on every site lands on a TIMED arm;
  - the pattern facts of the DEFAULT compile (`--emit-facts`, docs/spec/facts_listing.md §4.1) and
    its decision stamps (§4.2): the inputs of the rule pieces (pieces.py);
  - the forceability marks: every census arm is forced by public flags by construction; the paths
    that CANNOT be forced today are counted per site (the no-search NEXT arm, which needs L-ROW;
    the kit's within-site options beyond no-fd-d1/no-window-skip, which need L-KIT).

The pilot scores DEFAULT-ROUTE arms only: route-seed arms (--engine=, -f[no-]prefilter) are the
engine choice, [SEL-COST]'s, not a cand_rows choice; they are counted, never timed.

usage: inventory.py OUTDIR        (writes OUTDIR/{census.jsonl,sites.tsv,arms.tsv,picks.tsv,facts.tsv,summary.txt})
Run it as a heavy sweep: scripts/boxlock run --label rulepilot-census -- python3 -I inventory.py OUT
"""
import collections, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
import census_dry as cd  # noqa: E402

cd.P = W
cd.PCREC = os.environ.get("PCREC", W + "/build/pcrec")

# The pick vocabulary, FIXED before any timing: the default (cand_rows as shipped) and every
# single public deny the census walks. A multi-deny path is reached by the oracle (every census
# arm is timed) but is not a pick: a pick is one flag a rule adds.
PICKS = [("default", [])] + [(fl.replace("memfn:", "k:").lstrip("-"), [fl]) for _, fl in cd.DENIES]

def facts_of(pat, popts):
    argv = ["gnutimeout", "30", "nice", cd.PCREC, "--emit-facts", "--features", "all"] + popts + ["--pattern", pat]
    p = subprocess.run(argv, capture_output=True)
    if p.returncode != 0:
        return None
    f, sec = {}, None
    for line in p.stdout.decode("utf-8", "surrogateescape").splitlines():
        if line.startswith("#section"):
            sec = line.split()[1]; continue
        if line.startswith("#") or not line.strip():
            continue
        x = line.split("\t")
        if sec == "facts" and len(x) >= 7:
            f["F." + x[1]] = x[6]
            f["S." + x[1]] = x[4]
        elif sec == "decisions" and len(x) >= 3:
            f["D." + x[1]] = x[2].strip('"')
    return f

def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    rq = list(cd.csv.DictReader(open(W + "/docs/dev/lanes/rwquest/questions.tsv", encoding="utf-8"),
                                delimiter="\t", quoting=cd.csv.QUOTE_NONE))
    sites, arms_rows, pick_rows, facts_rows = [], [], [], []
    js = open(os.path.join(out, "census.jsonl"), "w")
    for r in sorted(rq, key=lambda r: r["id"])[:int(os.environ.get("LIMIT", "100000"))]:
        po, pre = cd.popts_for(r["flags"])
        pat = pre + r["pattern"]
        arms, ncomp, trunc, ref = cd.walk(out, pat, po)
        refused = ref == len(cd.SEEDS)
        rec = dict(id=r["id"], cls=r["class"], pattern=pat, popts=po, refused=refused, ncomp=ncomp, trunc=trunc)
        dflt = {s: a for s, a in arms.items() if not a["route"]}
        # the default compile's own sha: the arm of the seed [] with no deny
        base_sha = next((s for s, a in arms.items() if [] in a["how"]), None)
        ids = {}
        for s, a in sorted(dflt.items(), key=lambda kv: (kv[0] != base_sha, len(kv[1]["how"][0]), kv[0])):
            ids[s] = "a%d" % len(ids)
        picks = {}
        if not refused:
            for name, fl in PICKS:
                res = cd.compile_(out, pat, po, cd.argv_for([], fl))
                if res is None:
                    picks[name] = None; continue
                sha, st = res
                if sha not in dflt:
                    dflt[sha] = dict(stamps=st, how=[cd.argv_for([], fl)], route=False, pick_only=True)
                    ids[sha] = "a%d" % len(ids)
                picks[name] = sha
        f = facts_of(pat, po) if not refused else None
        nos = any(a["stamps"].get("RX_DFA_PREFILTER") in cd.NO_DENY_NEXT for a in dflt.values())
        rec.update(narms_default=len(dflt), nroute=sum(a["route"] for a in arms.values()),
                   nosearch_needs_lrow=nos, base=ids.get(base_sha),
                   npick_only=sum(1 for a in dflt.values() if a.get("pick_only")))
        js.write(json.dumps(dict(rec, arms=[dict(arm=ids[s], sha=s, stamps=a["stamps"], how=a["how"][0],
                                                 pick_only=a.get("pick_only", False)) for s, a in dflt.items()],
                                 picks={k: ids.get(v) for k, v in picks.items()})) + "\n"); js.flush()
        sites.append(rec)
        for s, a in dflt.items():
            arms_rows.append((r["id"], ids[s], s, "pick-only" if a.get("pick_only") else "census",
                              " ".join(a["how"][0]) or "-",
                              ",".join("%s=%s" % (k, v) for k, v in sorted(a["stamps"].items()))))
        for k, v in picks.items():
            pick_rows.append((r["id"], k, ids.get(v, "-")))
        if f:
            facts_rows.append((r["id"], json.dumps(f, sort_keys=True)))
    js.close()
    w = lambda name, hdr, rows: open(os.path.join(out, name), "w").write(
        "\t".join(hdr) + "\n" + "".join("\t".join(map(str, x)) + "\n" for x in rows))
    w("sites.tsv", ["id", "class", "refused", "narms_default", "nroute", "nosearch_needs_lrow", "base", "flags", "pattern"],
      [(s["id"], s["cls"], int(s["refused"]), s["narms_default"], s["nroute"], int(s["nosearch_needs_lrow"]), s["base"],
        " ".join(s["popts"]) or "-", s["pattern"].replace("\t", "\\t")) for s in sites])
    w("arms.tsv", ["id", "arm", "sha", "origin", "argv", "stamps"], arms_rows)
    w("picks.tsv", ["id", "pick", "arm"], pick_rows)
    w("facts.tsv", ["id", "facts_json"], facts_rows)
    summarize(out, sites, pick_rows)

def summarize(out, sites, pick_rows):
    comp = [s for s in sites if not s["refused"]]
    q2 = [s for s in comp if s["narms_default"] >= 2]
    na = sorted(s["narms_default"] for s in q2)
    med = na[len(na) // 2] if na else 0
    pk = collections.defaultdict(set)
    for i, p, a in pick_rows:
        pk[i].add(a)
    np2 = sum(1 for s in comp if len(pk[s["id"]] - {"-"}) >= 2)
    moved = collections.Counter(p for i, p, a in pick_rows if a not in ("a0", "-"))
    L = [f"questions {len(sites)}, compile {len(comp)}, refused {len(sites) - len(comp)} "
         f"({' '.join(s['id'] for s in sites if s['refused'])})",
         f"sites with >=2 FORCEABLE default-route arms: {len(q2)} (arms per such site median {med}, max {na[-1] if na else 0}, "
         f"total {sum(na)}; of them pick-only arms {sum(s.get('npick_only', 0) for s in comp)})",
         f"sites whose picks reach >=2 distinct arms: {np2}",
         f"sites with an UNFORCEABLE no-search NEXT arm (needs L-ROW): {sum(s['nosearch_needs_lrow'] for s in comp)}",
         f"route-seed arms (counted, not timed): {sum(s['nroute'] for s in comp)}",
         "picks that move the bytes, by site count: " + "; ".join(f"{k} {v}" for k, v in moved.most_common()),
         f"compiles {cd.NCOMP[0]}"]
    open(os.path.join(out, "summary.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))

if __name__ == "__main__":
    main()
