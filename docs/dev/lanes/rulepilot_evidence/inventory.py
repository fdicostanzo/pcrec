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

# The pick vocabulary, FIXED before any timing: the default (cand_rows as shipped) and EVERY
# distinct deny set by which the census walk first reached some default-route arm on some site
# (one flag or several: a pick is the flag set a rule adds). Derived from the walk, so it is the
# list of choices the forceable paths themselves name; every pick is then compiled on every site.
def pick_name(how):
    toks = []
    for a in how:
        if a.startswith("--memfn="):
            toks += ["k:" + x for x in a[len("--memfn="):].split(",")]
        else:
            toks.append(a.lstrip("-f") if a.startswith("-fno-") else a)
    return "+".join(toks) or "default"

def vocabulary(walked):
    seen = {}
    for r in walked:
        for a in r["arms"]:
            seen.setdefault(pick_name(a["how"]), a["how"])
    names = ["default"] + sorted(n for n in seen if n != "default")
    return [(n, seen.get(n, [])) for n in names]

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

def walk_all(out, rq):
    """phase A: the census walk per question (cached in OUT/walk.jsonl: one compile set per run)."""
    wf = os.path.join(out, "walk.jsonl")
    if os.path.exists(wf):
        return [json.loads(l) for l in open(wf)]
    res = []
    with open(wf, "w") as js:
        for r in rq:
            po, pre = cd.popts_for(r["flags"])
            pat = pre + r["pattern"]
            arms, ncomp, trunc, ref = cd.walk(out, pat, po)
            refused = ref == len(cd.SEEDS)
            dflt = {s: a for s, a in arms.items() if not a["route"]}
            base_sha = next((s for s, a in arms.items() if [] in a["how"]), None)
            ids = {}
            for s, a in sorted(dflt.items(), key=lambda kv: (kv[0] != base_sha, len(kv[1]["how"][0]), kv[0])):
                ids[s] = "a%d" % len(ids)
            rec = dict(id=r["id"], cls=r["class"], pattern=pat, popts=po, refused=refused, ncomp=ncomp, trunc=trunc,
                       nroute=sum(a["route"] for a in arms.values()), base=ids.get(base_sha),
                       arms=[dict(arm=ids[s], sha=s, stamps=a["stamps"], how=a["how"][0], pick_only=False)
                             for s, a in dflt.items()])
            js.write(json.dumps(rec) + "\n"); js.flush()
            res.append(rec)
    return res

def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    rq = list(cd.csv.DictReader(open(W + "/docs/dev/lanes/rwquest/questions.tsv", encoding="utf-8"),
                                delimiter="\t", quoting=cd.csv.QUOTE_NONE))
    rq = sorted(rq, key=lambda r: r["id"])[:int(os.environ.get("LIMIT", "100000"))]
    walked = walk_all(out, rq)
    picks_v = vocabulary([r for r in walked if not r["refused"]])
    sites, arms_rows, pick_rows, facts_rows = [], [], [], []
    js = open(os.path.join(out, "census.jsonl"), "w")
    for rec in walked:
        pat, po = rec["pattern"], rec["popts"]
        by_sha = {a["sha"]: a for a in rec["arms"]}
        picks = {}
        if not rec["refused"]:
            for name, fl in picks_v:
                res = cd.compile_(out, pat, po, list(fl))
                if res is None:
                    picks[name] = None; continue
                sha, st = res
                if sha not in by_sha:
                    by_sha[sha] = dict(arm="a%d" % len(by_sha), sha=sha, stamps=st, how=list(fl), pick_only=True)
                picks[name] = by_sha[sha]["arm"]
        f = facts_of(pat, po) if not rec["refused"] else None
        arms = list(by_sha.values())
        rec.update(arms=arms, picks=picks, narms_default=len(arms),
                   nosearch_needs_lrow=any(a["stamps"].get("RX_DFA_PREFILTER") in cd.NO_DENY_NEXT for a in arms),
                   npick_only=sum(1 for a in arms if a["pick_only"]))
        js.write(json.dumps(rec) + "\n"); js.flush()
        sites.append(rec)
        for a in arms:
            arms_rows.append((rec["id"], a["arm"], a["sha"], "pick-only" if a["pick_only"] else "census",
                              " ".join(a["how"]) or "-",
                              ",".join("%s=%s" % (k, v) for k, v in sorted(a["stamps"].items()))))
        for k, v in picks.items():
            pick_rows.append((rec["id"], k, v or "-"))
        if f:
            facts_rows.append((rec["id"], json.dumps(f, sort_keys=True)))
    js.close()
    w = lambda name, hdr, rows: open(os.path.join(out, name), "w").write(
        "\t".join(hdr) + "\n" + "".join("\t".join(map(str, x)) + "\n" for x in rows))
    w("sites.tsv", ["id", "class", "refused", "narms_default", "nroute", "nosearch_needs_lrow", "base", "flags", "pattern"],
      [(s["id"], s["cls"], int(s["refused"]), s["narms_default"], s["nroute"], int(s["nosearch_needs_lrow"]), s["base"],
        " ".join(s["popts"]) or "-", s["pattern"].replace("\t", "\\t")) for s in sites])
    w("arms.tsv", ["id", "arm", "sha", "origin", "argv", "stamps"], arms_rows)
    w("picks.tsv", ["id", "pick", "arm"], pick_rows)
    w("facts.tsv", ["id", "facts_json"], facts_rows)
    w("vocabulary.tsv", ["pick", "argv"], [(n, " ".join(fl) or "-") for n, fl in picks_v])
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
