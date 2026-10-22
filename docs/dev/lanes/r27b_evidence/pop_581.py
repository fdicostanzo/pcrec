#!/usr/bin/env python3
# docs/dev/lanes/r27b_evidence/pop_581.py — job 581: the POPULATION counts and the PREDICTOR.
#
# usage: python3 -I pop_581.py SUBJDIR DEFAULT_PPM.TSV > pop.tsv
#
# MEASURED, per cell and subject class (real / none / dense), over the throughput subject
# (<cell>.<class>.raw, the same bytes the timing reads), at every window position c in [0, n - K]:
#   stop hits per KiB   positions where the PRO stop (the cell's span-0 position of least default
#                       mass, tie LEFTMOST) holds; the verify chain starts there
#   verify-fail frac    of those stops, the fraction where the chain (the other span-0 positions
#                       ascending, then the ctx items under their absent rule) fails
#   mean survival       over the stops, the number of chain tests PASSED before the first failure
#                       (a full pass counts every test)
# PREDICTED (the class-independent default prior, NAMED: pcrec's default byte-rate prior
# tests/findings/default_ppm.tsv, summed per set exactly as memfn/src/presence.c set_mass does,
# cap 1e6 ppm; the 580/581 sites state the default prior, not an exemplar's):
#   pred stop mass      mass of the stop's set (ppm)
#   pred hits/KiB       1024 * stop mass
#   pred survival       sum over j >= 1 of the product of the masses of the first j chain tests
#                       (the expected number of passed tests, as above)
#   pred fail frac      1 - the product of all chain masses
#   pred HRS advance    sum over bytes b of rate[b] * sh[b]: the expected distance Horspool-over-sets
#                       advances per window under the prior (an addition of 581's, beside the above)
import importlib.util
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("pb", os.path.join(here, "proto_bodies_581.py"))
pb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pb)


def load_rate(path):
    rate = [0] * 256
    for line in open(path):
        if line.strip():
            b, r = line.split()
            rate[int(b)] = int(r)
    return rate


def mass(rate, ss):
    return min(sum(rate[b] for b in ss), 1000000) / 1e6


def plan(cell, rate):
    """(K, stop offset, chain) with chain = [(offset, set)] in PRO's order."""
    k = pb.CELLS[cell][0]
    ss = pb.span_sets(cell)
    d = min(range(k), key=lambda j: (mass(rate, ss[j]), j))     # least mass, tie leftmost
    chain = [(j, ss[j]) for j in range(k) if j != d] + pb.ctx_items(cell)
    return k, d, ss, chain


def table_of(ss):
    t = bytearray(256)
    for b in ss:
        t[b] = 1
    return bytes(t)


def main():
    subj, ppm = sys.argv[1], sys.argv[2]
    rate = load_rate(ppm)
    print("cell\tclass\tK\tstop\twindows\tstops\thits_per_KiB\tverify_fail\tmean_survival\t"
          "pred_stop_mass_ppm\tpred_hits_per_KiB\tpred_survival\tpred_fail\tpred_hrs_advance\tstop_matches_pro")
    for cell in pb.CELLS:
        k, d, ss, chain = plan(cell, rate)
        pm = mass(rate, ss[d])
        surv, prod = 0.0, 1.0
        for _o, s in chain:
            prod *= mass(rate, s)
            surv += prod
        pfail = 1 - prod
        sh = [next((t for t in range(1, k) if b in ss[k - 1 - t]), k) for b in range(256)]
        adv = sum(rate[b] * sh[b] for b in range(256)) / sum(rate)
        proto_stop = pb.CELLS[cell][1][1]
        for cls in ("real", "none", "dense"):
            buf = open(os.path.join(subj, "%s.%s.raw" % (cell, cls)), "rb").read()
            n = len(buf)
            tabs = {}
            def T(ss_):
                key = tuple(sorted(ss_))
                if key not in tabs:
                    tabs[key] = buf.translate(table_of(ss_))
                return tabs[key]
            tstop = T(ss[d])
            tests = [(o, T(s_)) for o, s_ in chain]
            windows = max(n - k + 1, 0)
            stops = fail = passed = 0
            # stop positions: c with c + d in range and the stop byte in S_d, c + K <= n
            i = tstop.find(1, d)
            while i != -1 and i - d <= n - k:
                c = i - d
                stops += 1
                ok = 0
                for o, tt in tests:
                    p = c + o
                    if p < 0 or p >= n or tt[p]:
                        ok += 1
                    else:
                        break
                passed += ok
                fail += ok < len(tests)
                i = tstop.find(1, i + 1)
            print("\t".join(str(x) for x in (
                cell, cls, k, d, windows, stops, "%.2f" % (stops * 1024.0 / n),
                "%.4f" % (fail / stops if stops else 0), "%.3f" % (passed / stops if stops else 0),
                "%.0f" % (pm * 1e6), "%.2f" % (pm * 1024), "%.4f" % surv, "%.4f" % pfail, "%.3f" % adv,
                "yes" if d == proto_stop else "NO(%d)" % proto_stop)))


main()
