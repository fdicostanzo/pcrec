#!/usr/bin/env python3
"""[K82] (B) the HANDOFF's predicted mover census (docs/design/litscan_k82h.md
§3). Compile-only: no artifact is run and no clock is read.

  PROTO=<pcrec built with proto_maxoff.diff> SCR=<scratch> [PROCS=4] \\
      python3 k82h_census.py > k82h_census.out

PROTO is a pcrec whose `src/facts/req.c` walk carries each run's maximum
byte offset from the attempt start (`proto_maxoff.diff`, this directory) and
prints it to stderr under K82H=1 (`K82H off=<k|-1> n=<len>` from the whole
run, `K82H at=<s>` from the window cut). Everything else is read off one
`--emit-facts` call per job: the decision stamps RX_REQ_WHY / RX_REQ_RUN /
RX_ENGINE / RX_VM_PREFILTER / RX_DFA_SCAN.

Populations: `../c3_movers.py`'s own (imported): every pcrec-bench export x
{auto, vm} x {caps, nocaps}, and every corpus `pattern` row x {auto, vm}.

THE PREDICATE (design §1.4), per artifact:
  emitted  RX_REQ_WHY "emitted" and RX_REQ_RUN not "none" (a run pre-check
           is emitted; set-leads reads "emitted" too);
  route    a DFA scan is in front: RX_ENGINE "dfa" with RX_DFA_SCAN
           "unanchored" or "attempt", or RX_ENGINE "vm" with
           RX_VM_PREFILTER "hybrid";
  bounded  the window's max offset K = off + at is finite.
A job meeting all three is a predicted PROGRAM mover; emitted+route but
unbounded is the handoff-unreachable population (the cost model's parked
trigger, known_issues.md K82 REVISED).
"""
import collections, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

PROTO, SCR = os.environ["PROTO"], os.environ["SCR"]
os.environ.setdefault("BASE", PROTO); os.environ.setdefault("NEW", PROTO)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import c3_movers as c3   # noqa: E402

CELLS = {  # the K82 cells and C3's customers, by bench export name
    "mod-i", "mod-r", "cls-fold-pair", "cls-pair-ctl", "ci-strasse",
    "wild-secrets-username-password-pair", "alt-shared-char", "alt-shared-lead",
    "wild-waf-crs-942270-union-select", "ci-ascii-control",
    "wild-secrets-slack-webhook-url", "http-5xx", "stack-frame"}


def one(job):
    i, pop, pat, args, cfg = job
    env = dict(os.environ, K82H="1")
    try:
        r = subprocess.run([PROTO.encode(), b"--features", b"all", b"-p", b"rx", b"--emit-facts",
                            *[a.encode() for a in args], b"--pattern", pat],
                           capture_output=True, timeout=300, env=env)
    except subprocess.TimeoutExpired:
        return {"i": i, "id": "timeout"}
    st, off, at = {}, None, 0
    for ln in r.stderr.decode("latin-1").split("\n"):
        if ln.startswith("K82H off="):
            off = int(ln.split()[1][4:])
        elif ln.startswith("K82H at="):
            at = int(ln[8:])
    for ln in r.stdout.decode("latin-1").split("\n"):
        f = ln.split("\t")
        if len(f) == 3 and f[1].startswith("RX_"):
            st[f[1]] = f[2].strip('"')
    rec = {"i": i, "pop": pop, "cfg": cfg, "pat": pat.decode("latin-1"), "args": args}
    if r.returncode or not st:
        rec["id"] = "refused"; return rec
    rec["id"] = "ok"
    eng, why, run = st.get("RX_ENGINE"), st.get("RX_REQ_WHY"), st.get("RX_REQ_RUN", "none")
    rec.update(eng=eng, why=why, run=run, scan=st.get("RX_DFA_SCAN"), vmpf=st.get("RX_VM_PREFILTER"),
               pf=st.get("RX_DFA_PREFILTER"))
    rec["emitted"] = why == "emitted" and run != "none"
    rec["route"] = ((eng == "dfa" and rec["scan"] in ("unanchored", "attempt")) or
                    (eng == "vm" and rec["vmpf"] == "hybrid"))
    rec["K"] = None if off is None or off < 0 else off + at
    rec["bounded"] = rec["K"] is not None
    rec["mover"] = rec["emitted"] and rec["route"] and rec["bounded"]
    return rec


def main():
    js = c3.jobs()
    wt = {j[0]: w for j, w in js}
    print("jobs:", len(js), file=sys.stderr, flush=True)
    with ThreadPoolExecutor(max_workers=int(os.environ.get("PROCS", "4"))) as ex:
        res = list(ex.map(one, [j for j, _w in js]))
    for r in res:
        r["w"] = wt[r["i"]]
    json.dump(res, open(os.path.join(SCR, "k82h_census.json"), "w"), indent=0)
    for pop in ("bench", "corpus"):
        rs = [r for r in res if r.get("pop") == pop]
        ok = [r for r in rs if r["id"] == "ok"]
        print(f"== {pop}: {len(rs)} distinct artifact-configs ({sum(r['w'] for r in rs)} rows); "
              f"ids {dict(collections.Counter(r['id'] for r in rs))}")
        for cfg in sorted({r["cfg"] for r in ok}):
            c = [r for r in ok if r["cfg"] == cfg]
            em = [r for r in c if r["emitted"]]
            rt = [r for r in em if r["route"]]
            mv = [r for r in rt if r["bounded"]]
            ub = [r for r in rt if not r["bounded"]]
            nr = [r for r in em if not r["route"]]
            print(f"  {cfg:12s} run pre-check emitted {len(em):5d} | DFA-scan route {len(rt):5d}"
                  f" -> bounded (MOVER) {len(mv):5d} ({sum(r['w'] for r in mv)} rows),"
                  f" unbounded {len(ub):5d} | no DFA scan (VM, excluded) {len(nr):5d}")
            ks = collections.Counter(min(r["K"], 64) for r in mv)
            print("      K histogram (64 = >=64):", dict(sorted(ks.items())))
            routes = collections.Counter((r["eng"], r["scan"] if r["eng"] == "dfa" else r["vmpf"]) for r in mv)
            print("      mover routes:", dict(routes))
    # the bench movers and the unbounded population, by export name
    # (bench/<set>/patterns/<name>.rx), auto config
    import glob
    byname = collections.defaultdict(list)
    for f in glob.glob(os.path.join(c3.BENCH, "bench", "*", "patterns", "*.rx")):
        byname[open(f, "rb").read().rstrip(b"\n").decode("latin-1")].append(
            f.split(os.sep)[-3] + "/" + os.path.basename(f)[:-3])
    auto = [r for r in res if r.get("pop") == "bench" and r["id"] == "ok" and r["cfg"] == "auto"]
    nm = lambda r: ",".join(sorted(byname.get(r["pat"], ["?"])))
    route = lambda r: f"{r['eng']}/{r['scan'] if r['eng'] == 'dfa' else r['vmpf']}"
    print("== bench MOVERS (auto): export K route in-loop-prefilter REQ_RUN")
    for r in sorted((r for r in auto if r["mover"]), key=nm):
        print(f"  {nm(r):48s} K={r['K']:3d} {route(r):15s} pf={r['pf']} run={r['run']}")
    print("== bench UNBOUNDED run pre-checks on a DFA-scan route (auto): handoff-unreachable")
    for r in sorted((r for r in auto if r["emitted"] and r["route"] and not r["bounded"]), key=nm):
        print(f"  {nm(r):48s} {route(r):15s} run={r['run']}")
    print("== the K82 cells and C3's customers, every config")
    for r in sorted((r for r in res if r.get("pop") == "bench" and r["id"] == "ok"
                     and set(n.split("/")[1] for n in byname.get(r["pat"], [])) & CELLS),
                    key=lambda r: (nm(r), r["cfg"])):
        print(f"  {nm(r):48s} {r['cfg']:12s} {route(r):15s} why={r['why']} K={r['K']} mover={r['mover']}")
    return res


if __name__ == "__main__":
    main()
