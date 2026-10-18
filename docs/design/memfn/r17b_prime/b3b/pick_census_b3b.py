#!/usr/bin/env python3
"""docs/design/memfn/r17b_prime/b3b/pick_census_b3b.py -- R17-b' B3b's KW-8
census ON THE KIT-SOURCED PROOF (lane b3b; r17b_prime.md rev 3 §3.1 row B3b,
the B3a review's binding note P2: "re-run the KW-8 shadow census on the
KIT-SOURCED proven0; every deny arm and the measured bundle stay at 100%
agreement").

    pick_census_b3b.py [--ports-only] <pick_census.py's own arguments>

B3a's census (../b3a/pick_census.py) IMPORTED, never copied: its population
readers, record parser, floors and K35 checks run unchanged, over the shadow's
records at B3b. Two things differ, both by data:
  - the PICKS gain the ROUTED decision's six records (`rdom`, `rlead`,
    `rhead`, `rwin`, `rwhole`, `rrest`; src/gen/emit_dfa.c `req_pick_shadow`):
    the links the kit's routed PRES rows answer, which the pre-check's parts
    are laid out from, against pcrec's own decision before B3b. The boolean
    ones (`rdom`, `rlead`, `rwhole`) are floored on both values of `differs`;
  - a site whose routed ask the kit refused (`MFPICKSITE route-refused`) is
    counted as B3a's `port-refused`, a failure.
At B3b the proof the kit's P2 reads is the start search's, restated by pcrec
from its kit-sourced class (`dfa_cand_scan` reads the PF site's `proven0`
through `mf_ask`): the census's `dominated`/`rdom` records are that reading.
--ports-only drops the r* records (and their K35 reach): under a `--memfn=`
deny of a PRES row the routed decision moves by design where the deny acts,
so the deny arms hold the PORTS (B3a's five picks, which no deny reaches) at
100%, and the routed records are held on the default and bundle arms.
"""
import collections
import importlib.util
import os
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("pick_census", os.path.join(HERE, "..", "b3a", "pick_census.py"))
pc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pc)

ROUTED = ("rdom", "rlead", "rhead", "rwin", "rwhole", "rrest")
ports_only = "--ports-only" in sys.argv
if ports_only:
    sys.argv.remove("--ports-only")
else:
    pc.PICKS = pc.PICKS + ROUTED
    pc.BOOLEAN_PICKS = pc.BOOLEAN_PICKS + ("rdom", "rlead", "rwhole")

_one = pc.one


def one(binp, tmp, args, pat, arm, k):
    rc, recs = _one(binp, tmp, args, pat, arm, k)
    out = []
    for r in recs:
        if r[0] == "MFPICKSITE" and r[1] == "route-refused":
            r = ["MFPICKSITE", "port-refused"] + r[2:]
        if ports_only and r[0] == "MFPICK" and r[1] in ROUTED:
            continue
        out.append(r)
    return rc, out


pc.one = one

# b3brev U11: the shadow SKIPS `rwin` where the routed run renders no window
# (`MFPICKSKIP rwin <why> <kind>`) rather than compare against a window the
# layout never used; B3a's reader keeps only MFPICK/MFPICKSITE lines, so the
# skips are counted here off the same compiles (its `subprocess.run`) and
# printed. A skip is not a failure.
_skips = collections.Counter()
_slock = threading.Lock()
_sp = pc.subprocess


class _Counting:
    def __getattr__(self, name):
        return getattr(_sp, name)

    @staticmethod
    def run(*a, **kw):
        r = _sp.run(*a, **kw)
        err = r.stderr if isinstance(r.stderr, str) else (r.stderr or b"").decode("utf-8", "replace")
        for ln in err.splitlines():
            if ln.startswith("MFPICKSKIP\t"):
                with _slock:
                    _skips[tuple(ln.split("\t")[1:4])] += 1
        return r


pc.subprocess = _Counting()


def main():
    r = pc.main()
    for (pick, why, kind), n in sorted(_skips.items()):
        print("SKIP\t%s\t%s\t%s\t%d" % (pick, why, kind, n))
    print("skips %d" % sum(_skips.values()))
    return r


sys.exit(main())
