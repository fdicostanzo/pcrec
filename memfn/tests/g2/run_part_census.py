#!/usr/bin/env python3
# SPDX-License-Identifier: 0BSD
# Provenance: original pcrec-memory-functions text (R-38 Part D D3, lane partd2).
"""memfn/tests/g2/run_part_census.py -- R-38 Part D D3's CHECK (docs/design/memfn/part_d.md rev 4 §5.1 D3, §5.1.1).

    python3 -I run_part_census.py --census0 CENSUS0_PY TRACE.err RUN.log [--tag T]

TRACE.err is the presence generator's stderr run against the TRACE kit (MF_TRACE) with G2P_G2SITE set: the kit's
MFTRACE records and G2's `G2SITE id=N` join lines (every record between two G2SITE lines is site N's). RUN.log is
the recording driver's output over the SAME site file: one `G2PRP id=N unspelled=U scanless=S measured=M` line per
classified run part, G2's own counts from its own sets and C2's measured extent (g2_pres_run.c rp_line).

THE POPULATION: the sites whose define CHOSE an ofsskip FUNC BODY row for the derived part (an `END table=fn
phase=define chosen=fn-...` record in the site's block). Per site in it:
  RECORDS   exactly ONE `run_part_terms` record (a doubled print, e.g. the record printed on the quiet path, reds);
  UNSPELLED the census's count of unspelled SET terms (census0.py's ONE parser of the record) EQUALS G2's
            `unspelled` (on a site with a measured extent; a no-background site is counted, outside the equality);
  EVERY-POS the census's `every-pos` (a scan-less record, `hint=-`) EQUALS G2's `scanless`;
  JOIN      the site has its G2PRP line, and every G2PRP line's site is in the population.
NO FN ROW: blocks whose define chose no fn row (a declined run; every site of the generic pass, which C2's
classifier skips) are counted apart, outside the equalities; a G2 run part line on one is a JOIN failure.
Prints FAIL lines and one `RPCENSUS` line of totals (the runner floors them). Exit 0 always on a readable input
(the runner counts FAIL lines); 2 when an input cannot be read.
"""
import argparse
import importlib.util
import re
import sys

FN_ROW = re.compile(r"^MFTRACE END table=fn .*\bphase=define chosen=(fn-[^ ]+)")


def load_census0(path):
    spec = importlib.util.spec_from_file_location("census0", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def blocks(path):
    """{site id: (records, fn rows)}: each site's block, the lines since the previous G2SITE line"""
    out, recs, rows = {}, [], []
    for ln in open(path, errors="replace"):
        ln = ln.rstrip("\n")
        if ln.startswith("G2SITE id="):
            out[int(ln.split("=", 1)[1])] = (recs, rows)
            recs, rows = [], []
        elif ln.startswith("MFTRACE run_part_terms "):
            recs.append(ln)
        else:
            m = FN_ROW.match(ln)
            if m:
                rows.append(m.group(1))
    return out


def g2_lines(path):
    out = {}
    for ln in open(path, errors="replace"):
        if ln.startswith("G2PRP "):
            kv = dict(x.split("=", 1) for x in ln.split()[1:])
            out[int(kv["id"])] = {k: int(v) for k, v in kv.items() if k != "id"}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--census0", required=True)
    ap.add_argument("--tag", default="")
    ap.add_argument("trace")
    ap.add_argument("runlog")
    a = ap.parse_args()
    try:
        c0 = load_census0(a.census0)
        bl = blocks(a.trace)
        g2 = g2_lines(a.runlog)
    except (OSError, ValueError, KeyError) as e:
        print("FAIL: run_part_census: an input could not be read: %s" % e)
        sys.exit(2)
    tag = a.tag + ": " if a.tag else ""
    fails = []
    pop = un_c = un_g = ep_c = ep_g = nobg = nofn_sites = nofn_recs = 0
    for sid in sorted(bl):
        recs, rows = bl[sid]
        if not rows:
            nofn_sites += 1
            nofn_recs += len(recs)
            if sid in g2:
                fails.append("JOIN: site %d has G2's run part line and its define chose no fn row" % sid)
            continue
        pop += 1
        if len(recs) != 1:
            fails.append("RECORDS: site %d (fn row %s) carries %d run_part_terms records, not 1"
                         % (sid, ",".join(rows), len(recs)))
        # the census's counts over every record the block carries (none: 0), so a missing or doubled record
        # also reds the equality it moves
        parsed = [c0.run_part_record(x) for x in recs]
        cu = sum(c0.run_part_unspelled(r) for r in parsed)
        ce = sum(1 for r in parsed for f, _c in c0.run_part_classes(r) if f == "every-pos")
        g = g2.get(sid)
        if g is None:
            fails.append("JOIN: site %d (fn row %s) has no G2 run part line" % (sid, ",".join(rows)))
            continue
        un_c += cu
        ep_c += ce
        un_g += g["unspelled"]
        ep_g += g["scanless"]
        if not g["measured"]:
            nobg += 1
        elif cu != g["unspelled"]:
            fails.append("UNSPELLED: site %d: the census counts %d unspelled SET terms, G2's measured extent "
                         "holds %d unspelled positions" % (sid, cu, g["unspelled"]))
        if ce != g["scanless"]:
            fails.append("EVERY-POS: site %d: the census counts %d every-pos part(s), G2 rendered %d scan-less "
                         "run(s)" % (sid, ce, g["scanless"]))
    for sid in sorted(set(g2) - set(bl)):
        fails.append("JOIN: G2's run part line for site %d has no G2SITE block" % sid)
    for f in fails[:30]:
        print("FAIL: %sD3 %s" % (tag, f))
    if len(fails) > 30:
        print("FAIL: %sD3 ... %d more" % (tag, len(fails) - 30))
    print("RPCENSUS %spop=%d unspelled=%d g2_unspelled=%d everypos=%d g2_scanless=%d nobg=%d nofn_sites=%d nofn_"
          "records=%d failed=%d" % (tag, pop, un_c, un_g, ep_c, ep_g, nobg, nofn_sites, nofn_recs, len(fails)))


if __name__ == "__main__":
    main()
