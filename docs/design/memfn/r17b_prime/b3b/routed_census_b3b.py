#!/usr/bin/env python3
"""docs/design/memfn/r17b_prime/b3b/routed_census_b3b.py -- R17-b' B3b's
ROUTED-RECORD COUNT (lane b3b; r17b_prime.md rev 3 §1.6 [rev3 B5] item 1,
§8.1 "the routed-record floors per (kind, row) from B2", §8.3 SN-1).

    routed_census_b3b.py <fdb2/routed_census.py's own arguments>

B2's census (../fdb2/routed_census.py) IMPORTED, never copied, with the rows
routed at B3b added to its ROUTED set: D2 and slot PRES's P0, P2, P3, P4, P9.
pcrec prints one `MFROUTED<TAB>PRE<TAB>kind<TAB>row` record per presence span
the kit's routed PRES rows decided (src/gen/memfn_sites.c
`pcrec_memfn_pres_routed`: the DECIDING row the kit's class carries,
`mf_class.pres_row`, never inferred from the link's shape (b3brev U5); a
pre-check P2 drops is never defined and prints `MFPRESDROP` from the
admission's ask, counted here too), so a PRES row
that stops routing (SN-1) shows as a cell under its floor, and a row routing
early (a B4 row) as a record of a row outside ROUTED. Floors:
routed_floors_B3b.tsv, floor(0.9 x measured) per (site, kind, row). Each PRES
record also carries the link its row decided and the row's template (the
listing's pick): a row deciding a link outside its own kind (S1103: P0 given
P3's narrowing) is a FAIL. Every compile timeout is counted and fails the run.
"""
import collections
import importlib.util
import os
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("routed_census", os.path.join(HERE, "..", "fdb2", "routed_census.py"))
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)
rc.ROUTED = set(rc.ROUTED) | {"D2", "P0", "P2", "P3", "P4", "P9"}

# a pre-check P2 drops is never defined: pcrec prints its spans as
# `MFPRESDROP<TAB>PRE<TAB>kind<TAB>P2` (not MFROUTED, which C10's fixtures read
# as the defined sites'); counted here as the routed cells they are
_one = rc.one
# b3brev U10: a compile that times out has no records, so its cells read LOW
# (or a row routes 0 and reads as one that stopped routing); every timeout is
# counted, printed, and fails the run
_timeouts = [0]
_tlock = threading.Lock()
_shape = collections.Counter()   # records whose decided link is not their row's kind


def one(binp, tmp, pat, arm, k):
    import subprocess
    d = os.path.join(tmp, "c%d" % k)
    os.makedirs(d, exist_ok=True)
    env = dict(os.environ, PCREC_MF_ROUTE_TRACE="1")
    argv = [binp, "-p", "rx", "--features", "all"] + arm + ["-o", os.path.join(d, "o.c"),
                                                            "--pattern", pat]
    try:
        r = subprocess.run(argv, capture_output=True, timeout=60, env=env)
    except subprocess.TimeoutExpired:
        with _tlock:
            _timeouts[0] += 1
        return []
    out = []
    for ln in r.stderr.decode("utf-8", "replace").splitlines():
        if not ln.startswith(("MFROUTED\t", "MFPRESDROP\t")):
            continue
        c = ln.split("\t")
        out.append(tuple(c[1:4]))
        # b3brev U5: a PRES record carries the link its deciding row decided
        # and the row's template (the listing's pick); the row must decide a
        # link of its own kind: proven_by as the template's, and a chosen
        # member/window (m != 0) exactly where the template's member is
        if len(c) >= 6 and c[4] != "-" and c[5] != "-":
            got, tpl = _link(c[4]), _link(c[5])
            if got is None or tpl is None or got["p"] != tpl["p"] or (got["m"] != 0) != (tpl["m"] != 0):
                with _tlock:
                    _shape[(c[1], c[2], c[3], c[4], c[5])] += 1
    return out


def _link(s):
    import re
    m = re.match(r"^v(\d+)p(\d+)m(\d+)o(\d+)$", s)
    return dict(zip("vpmo", map(int, m.groups()))) if m else None


rc.one = one


def main():
    r = rc.main()
    for (site, kind, row, got, tpl), n in sorted(_shape.items()):
        print("FAIL: %s/%s row %s decided link %s outside its template %s (%d record(s)): a row "
              "deciding another row's link shape" % (site, kind, row, got, tpl, n))
    print("link-shape violations %d" % sum(_shape.values()))
    if _shape:
        r = 1
    print("timeouts %d" % _timeouts[0])
    if _timeouts[0]:
        print("FAIL: %d compile(s) timed out (60 s each): their routed records are missing"
              % _timeouts[0])
        return 1
    return r


sys.exit(main())
