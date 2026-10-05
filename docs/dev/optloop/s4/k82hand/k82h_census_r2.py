#!/usr/bin/env python3
"""[K82] (B) the HANDOFF's revision-2 census (docs/design/litscan_k82h.md
§3.1a, §4.2a; r1 panel findings C-C8 and C-C9). Compile-only: no artifact is
run and no clock is read.

  PROTO=<pcrec built with proto_maxoff.diff> SCR=<scratch> [PROCS=4] \\
      python3 k82h_census_r2.py > k82h_census_r2.out

Same prototype and the same per-artifact predicate as `k82h_census.py`
(imported: its `one()` is the classifier, so the two censuses cannot drift).
Two populations the first census did not count:

  C-C9  every corpus `pattern` row (c3_movers.py's, imported) under `auto` (a
        cross-check against k82h_census.out, and the source of the hybrid
        movers' prefilter languages) and two more
        configs: `--no-captures` (auto engine), and `--engine=vm -fprefilter`
        (the forced hybrid). The first census ran the corpus under {auto, vm}
        only, so a corpus mover reachable only without captures, and every
        hybrid the selector does not pick by itself, went uncounted.
  C-C8  every corpus pattern BLOCK that carries a step/frame budget (columns
        `budget_steps`/`budget_frames`) or a `gu` (give-up) case, compiled as
        the harness compiles it: its own `engine` column honoured (c3's
        population ignores that column, and a give-up cell is exactly where
        the engine column is set). Each block is reported with its route, K,
        and whether it is a handoff mover. A HYBRID mover here is a cell
        whose give-up surface the handoff could move (design §4.2 item 1).
"""
import collections, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import k82h_census as kc   # noqa: E402  (sets BASE/NEW := PROTO before c3 imports)
import c3_movers as c3     # noqa: E402

PROTO = kc.PROTO
EXTRA_CFG = {"auto": [], "nocaps": ["--no-captures"], "vm-pf": ["--engine=vm", "-fprefilter"]}


def prefilter_lang(r):
    p = subprocess.run([PROTO.encode(), b"--features", b"all", b"-p", b"rx", b"--emit-facts",
                        *[a.encode() for a in r["args"]], b"--pattern", r["pat"].encode("latin-1")],
                       capture_output=True, timeout=300)
    for ln in p.stdout.decode("latin-1").split("\n"):
        f = ln.split("\t")
        if len(f) == 3 and f[1] == "RX_VM_PREFILTER_LANG":
            return f[2].strip('"')
    return "?"


def budget_blocks():
    """(ident, pat, args, has_gu, budget) for every block with a budget or a gu case."""
    out = []
    files = sorted(os.path.join(r, f) for r, _d, fs in os.walk(os.path.join(c3.ROOT, "tests"))
                   for f in fs if f.endswith(".rxt"))
    for f in files:
        r = subprocess.run([PROTO, "--list-source", f], capture_output=True, timeout=120)
        if r.returncode:
            continue
        rel = os.path.relpath(f, c3.ROOT)
        blocks, gu, section = {}, set(), None
        for ln in r.stdout.split(b"\n"):
            if ln.startswith(b"#section"):
                section = ln.split()[1]; continue
            if not ln or ln.startswith(b"#"):
                continue
            fl = ln.split(b"\t")
            if section is None:
                if len(fl) < 12 or fl[0] not in (b"pattern", b"pattern-esc"):
                    continue
                pat = c3.dec_field(fl[4])
                if not pat or b"\0" in pat:
                    continue
                args = []
                if b"i" in fl[5]: args.append("-i")
                if b"u" in fl[5]: args.append("--ucp")
                if fl[8]: args += ["-e", fl[8].decode()]
                if fl[9] and fl[9] != b"auto": args.append("--engine=" + fl[9].decode())
                blocks[fl[1]] = (pat, args, (fl[10] + b"/" + fl[11]).decode())
            elif section == b"cases" and len(fl) > 3 and fl[3] == b"gu":
                gu.add(fl[1])
        for line, (pat, args, bud) in blocks.items():
            if line in gu or bud != "/":
                out.append(("%s:%s" % (rel, line.decode()), pat, args, line in gu, bud))
    return out


def main():
    corpus = sorted({(j[2], tuple(j[3])) for j, _w in c3.jobs()
                     if j[1] == "corpus" and j[4] == "auto"})
    js, n = [], 0
    for pat, args in corpus:
        for cfg, fl in EXTRA_CFG.items():
            n += 1
            js.append((n, "corpus", pat, list(args) + fl, cfg))
    bb = budget_blocks()
    for ident, pat, args, has_gu, bud in bb:
        n += 1
        js.append((n, "budget", pat, args, ident))
    print("jobs:", len(js), file=sys.stderr, flush=True)
    with ThreadPoolExecutor(max_workers=int(os.environ.get("PROCS", "4"))) as ex:
        res = list(ex.map(kc.one, js))
    route = lambda r: f"{r['eng']}/{r['scan'] if r['eng'] == 'dfa' else r['vmpf']}"
    print("== C-C9: corpus distinct (pattern, args):", len(corpus))
    for cfg in EXTRA_CFG:
        rs = [r for r in res if r.get("pop") == "corpus" and r.get("cfg") == cfg]
        ok = [r for r in rs if r["id"] == "ok"]
        em = [r for r in ok if r["emitted"]]
        rt = [r for r in em if r["route"]]
        mv = [r for r in rt if r["bounded"]]
        print(f"  {cfg:7s} ids {dict(collections.Counter(r['id'] for r in rs))} | run pre-check emitted"
              f" {len(em)} | DFA-scan route {len(rt)} -> bounded (MOVER) {len(mv)}, unbounded"
              f" {len(rt) - len(mv)} | no DFA scan {len(em) - len(rt)}")
        print("      K histogram (64 = >=64):",
              dict(sorted(collections.Counter(min(r["K"], 64) for r in mv).items())))
        print("      mover routes:", dict(collections.Counter(route(r) for r in mv)))
        # [r1 S-F2] the give-up allowance is keyed on the hybrid's prefilter
        # LANGUAGE, which kc.one() does not record: read it for the hybrid movers.
        langs = collections.Counter(prefilter_lang(r) for r in mv if r["eng"] == "vm")
        print("      hybrid movers by RX_VM_PREFILTER_LANG:", dict(langs))
    print("== C-C8: budget / gu blocks:", len(bb))
    nmv = collections.Counter()
    for k, (ident, pat, args, has_gu, bud) in enumerate(bb):
        r = res[len(res) - len(bb) + k]
        if r["id"] != "ok":
            print(f"  {ident:46s} gu={int(has_gu)} budget={bud:9s} {r['id']}")
            nmv["refused"] += 1
            continue
        tag = "MOVER" if r["mover"] else "-"
        if r["mover"]:
            nmv["hybrid-mover" if r["eng"] == "vm" else "dfa-mover"] += 1
        else:
            nmv["not-mover"] += 1
        print(f"  {ident:46s} gu={int(has_gu)} budget={bud:9s} {route(r):15s} why={r['why']}"
              f" K={r['K']} {tag}")
    print("  totals:", dict(nmv))


if __name__ == "__main__":
    main()
