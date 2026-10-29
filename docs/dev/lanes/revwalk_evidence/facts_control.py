#!/usr/bin/env python3
"""Lane revwalk (2026-10-29): control C3 for tiers.py, read off pcrec's OWN facts layer ([PATFACTS],
`--emit-facts`), which shares no code with tiers.py's reader.  One `--emit-facts` compile per pattern
that tiers.py gives an inner landmark (no gcc, no subject): run it under scripts/boxlock (> 50 compiles).

  C3a  start_anchor: every row tiers.py calls unanchored is `unanchored` in the facts.
  C3b  necessity: every single-byte member of the chosen landmark L is in `req_set`.
  C3c  move-back: for a T2/T3 row, the first byte of L that P cannot consume has a `req_set_maxoff` of
       `unbounded` in the facts iff tiers.py says P's width is unbounded (pmax None).
  and the ROUTE (RX_ENGINE stamp) per tier, for the report.

Usage: scripts/boxlock run --label revwalk-facts -- env PCREC=build/pcrec CORPUS=. python3 facts_control.py
"""
import collections, concurrent.futures as cf, importlib.util, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("tiers", os.path.join(HERE, "tiers.py"))
T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
G = T.G
G.PCREC = os.environ["PCREC"]


def one(r):
    o = T.row_of(r, keep=True)
    if o.get("stage") != "landmark":
        return None
    fd, err = G.facts(dict(r, pat=r["pat"]))
    out = dict(id=r["id"], pop=r["pop"], tier=o["tier"], excl=o["excl"], strong=o["strong"], comp=o["comp"],
               ratio=o["ratio"], err=err)
    if fd is None:
        return out
    f, d = fd
    out["anch"] = f.get("start_anchor", "")
    out["engine"] = d.get("ENGINE", "?")
    rs = f.get("req_set", "")
    req = set(int(x) for x in rs.split(",") if x.isdigit()) if rs and rs[0].isdigit() else None
    single = [min(x) for x in o["_run"] if len(x) == 1]
    out["nec"] = None if req is None else all(b in req for b in single)
    mo = {}
    for kv in f.get("req_set_maxoff", "").split(","):
        if ":" in kv:
            k, v = kv.split(":", 1)
            if k.isdigit():
                mo[int(k)] = v
    pit = o.get("_pit")
    if o["tier"] in ("T2", "T3") and pit is not None and o["excl"]:
        _lo, pmax, alph, _f = T.R.seq_props(pit)
        ex = [min(x) for x in o["_run"] if len(x) == 1 and not (x & alph)]   # an L byte P cannot consume
        if ex and ex[0] in mo:
            out["unb_agree"] = (mo[ex[0]] == "unbounded") == (pmax is None)
    return out


def main():
    pop = T.corpus_pop() + T.bench_pop()
    with cf.ProcessPoolExecutor(max_workers=8) as ex:
        rows = [x for x in ex.map(one, pop, chunksize=16) if x]
    for pop_ in ("corpus", "bench"):
        rs = [r for r in rows if r["pop"] == pop_]
        ok = [r for r in rs if r["err"] is None]
        print("## %s: %d landmark rows, %d compiled (facts read), %d refused/failed" % (pop_, len(rs), len(ok), len(rs) - len(ok)))
        bad_a = [r["id"] for r in ok if r["anch"] != "unanchored"]
        print("C3a start_anchor not 'unanchored': %d %s" % (len(bad_a), bad_a[:6]))
        nec = collections.Counter(r["nec"] for r in ok)
        print("C3b landmark bytes in req_set: agree %d, VIOLATE %d, req_set absent %d %s"
              % (nec[True], nec[False], nec[None], [r["id"] for r in ok if r["nec"] is False][:6]))
        ua = collections.Counter(r.get("unb_agree") for r in ok if "unb_agree" in r)
        print("C3c unbounded move-back agrees with req_set_maxoff: agree %d, DISAGREE %d %s"
              % (ua[True], ua[False], [r["id"] for r in ok if r.get("unb_agree") is False][:6]))
        print("route by tier (admitted rows: composes, T2/T3 excluded / strong, F>=2):")
        for t in ("T1", "T2", "T3", "T4", "G1"):
            adm = [r for r in ok if r["tier"] == t and r["comp"] and (r["excl"] if t in ("T2", "T3") else r["strong"])
                   and r["ratio"] >= 2]
            print("  %s: %s" % (t, dict(collections.Counter(r["engine"] for r in adm))))
        print()


if __name__ == "__main__":
    main()
