"""S1141's population (lane z2fix): every census item whose own decision is C1
(`finisher-dfa`), re-decided by a trace harness built with S1141's plant (HT, the
planted build_dir's pcrec-harness). Prints the planted first failing row per item
and the number of planted `cover` admissions (decision or RX_DFA_SCAN "cover");
0 admissions over a non-empty population is the equivalence measurement.

  python3 -I s1141pop.py CENSUS.jsonl      (env HT = the planted trace harness)
"""
import collections, json, os, sys
from multiprocessing.pool import ThreadPool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import z2  # noqa: E402

HT = os.environ["HT"]


def one(it):
    fl, ph = it
    env = dict(os.environ, PCREC_KIT_PROOF_TRACE="1")
    p = z2.run_c(z2.hargs(HT, fl) + ["-o", "-", "--pattern"], bytes.fromhex(ph), env)
    kp, _, _ = z2.records(p.stderr)
    d = z2.decision(kp)
    cover = (d and d[0] == "cover") or b'#define RX_DFA_SCAN "cover"' in p.stdout
    return fl, ph, p.returncode, d[0] if d else "not-asked", cover


def main(path):
    items = []
    for ln in open(path):
        r = json.loads(ln)
        d = z2.decision(r["kp"]) if not r["rc"] else None
        if d and d[0].startswith("finisher-dfa"):
            items.append((r["fl"], r["pat"]))
    why, covers = collections.Counter(), []
    with ThreadPool(8) as pool:
        for fl, ph, rc, w, cover in pool.imap_unordered(one, items):
            why["rc!=0" if rc else w.split("/")[0]] += 1
            if cover:
                covers.append((fl, bytes.fromhex(ph).decode("latin-1")))
    print("s1141 population (census items C1 declines) = %d" % len(items))
    for k, v in sorted(why.items(), key=lambda kv: -kv[1]):
        print("planted-why", k, v)
    print("planted cover admissions = %d" % len(covers))
    for x in covers[:20]:
        print("COVER", *x)
    rc = 1 if covers or not items else 0
    print("z2 s1141pop: DONE rc=%d" % rc)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
