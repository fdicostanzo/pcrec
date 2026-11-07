# span_cards rev 1.4 r10 drill (lane s2c14fix, review 2026-11-06 r10 REV14-2), re-derived at rev 1.5 (lane s2rev15,
# R15-3): the derivation of memfn/data/policy.tsv's r_max_e6, the cap on a delta row's resolution r (measures.md
# §3.5¶3a), from the A/A rows of BOTH windows.
# INPUTS: per window, the eight near-zero verify rows (l1, w1, c1, c2 at p0 and p50; in the first window, s2d-20261106,
# the rows it left `null` with |med(x_l)| within their uncapped r, s2d1/est_rows.txt; in the second, s2d-20261107a,
# the same eight, s2d2/est_rows.txt): each row's anchored launch values x_l and its twin's xb_l (walkbytes x 10^6),
# taken by est.py's compute() over a copy of that run directory (the cells stay in scratch; `python3 -I rmax_drill.py
# RUNDIR` re-takes them from a run directory, the window named by its record's run_id, and checks they equal the
# ones below).
# THE RULE: the twin is the same binary timed beside the arm in every launch, so d_l = x_l - xb_l carries the
# measurement's own launch noise twice (var 2 s^2) and none of the arm-vs-base difference. One arm's median then has
# the standard error sqrt(K_MED x s^2), and the resolution the method reaches on that row is three of them, drift's
# factor: r_AA = 3 x isqrt_rn(rhafz(K_MED_E6 x sp2(d), 2 x 10^6)). r_max_e6 is the LARGEST r_AA over the eight
# rows: no row may claim "zero within r" with an r wider than the worst the method showed it can resolve at zero.
# [rev1.5 R15-3] The rev 1.4 trigger (re-derive on the first window timed with rev 1.4's base) fired with the second
# window: r_max_e6 is the largest r_AA over BOTH windows' sixteen rows, a MEASUREMENT (D149), no longer a default.
# A record keeps the r_max it pinned (the second window is scored at its pinned 53751); the new value applies from
# the next window. Re-derive when a window is timed with another base or candidate loop.
#   python3 -I rmax_drill.py [RUNDIR]
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "slot"))
import est  # noqa: E402  (its primitives: med, trim, sp2, isqrt_rn, rhafz, K_MED_E6, resolution)

W1 = {   # s2d-20261106 (FROZEN 508178bd2, the rev 1.3 base): key: (x_l, xb_l), launches 1..7
    "kit.verify_cmp.rc-memcmp.l1.p0": ([-20087, -59787, -307141, -112005, -266487, -99445, -90355],
                                       [-28969, -52798, -313645, -108597, -276595, -108362, -94047]),
    "kit.verify_cmp.rc-memcmp.l1.p50": ([-62876, -85810, -242432, -91382, -269150, -94280, -91753],
                                        [-101702, 59247, -241520, -97758, -285114, -92424, -86455]),
    "kit.verify_cmp.rc-words.w1.p0": ([23935, -41271, -104810, 75889, -163319, 62265, 63266],
                                      [20581, -49826, -189847, 68276, -139738, 52027, 57932]),
    "kit.verify_cmp.rc-words.w1.p50": ([26065, 24695, -197809, 36509, -129308, 77494, 60796],
                                       [50402, -42837, -177552, 32181, -170102, 76271, 66984]),
    "kit.verify_cmp.settest.c1.p0": ([85436, -96372, -297486, -99175, 48955, -133746, -97729],
                                     [30825, -92580, -362535, -102235, 40861, -125960, -81329]),
    "kit.verify_cmp.settest.c1.p50": ([29815, -93068, -338970, -104217, -34555, -106306, -87703],
                                      [67733, -104460, -361862, -101228, -29415, -132265, -72924]),
    "kit.verify_cmp.settest.c2.p0": ([94822, 34998, -299046, -71137, 89836, 49432, -342],
                                     [60691, -5593, -306014, -10286, 82199, 135524, 25763]),
    "kit.verify_cmp.settest.c2.p50": ([156598, -4623, -268419, -7133, 85530, 35632, 19088],
                                      [32481, 28886, -318029, -78235, 33156, 25585, 6318]),
}
W2 = {   # [rev1.5 R15-3] s2d-20261107a (FROZEN 1e4999d1c, rev 1.4's base): key: (x_l, xb_l), launches 1..7
    "kit.verify_cmp.rc-memcmp.l1.p0": ([-66568, -116063, -116015, -292400, -19235, -108264, -170978],
                                       [-67271, -99911, -105475, -306126, -96132, -106339, -200598]),
    "kit.verify_cmp.rc-memcmp.l1.p50": ([-67441, -98296, -105615, -157461, -64228, -112021, -198619],
                                        [74928, -48513, -115019, -163830, -12742, -130898, -185022]),
    "kit.verify_cmp.rc-words.w1.p0": ([-16730, 53274, 59850, 20652, 85752, -167293, 12198],
                                      [30555, 29188, 27618, 37431, 39860, -144357, 4812]),
    "kit.verify_cmp.rc-words.w1.p50": ([92105, 39722, 15480, 59542, 15404, -162680, 38837],
                                       [-16263, 29578, 32377, -65248, 11621, -170629, 15972]),
    "kit.verify_cmp.settest.c1.p0": ([-195626, -56384, -77441, -325510, -119301, 67081, -157330],
                                     [-101190, -47707, -72179, -288115, -120349, 61170, -165972]),
    "kit.verify_cmp.settest.c1.p50": ([-155181, -56253, -68241, -308986, -107405, 86300, -114474],
                                      [-118094, -52292, -76658, -299404, -97150, 58079, -168984]),
    "kit.verify_cmp.settest.c2.p0": ([138559, 58315, -33887, 25519, -7079, 182257, -9546],
                                     [132714, 85120, -1349, 35801, 32760, 41515, -11607]),
    "kit.verify_cmp.settest.c2.p50": ([129484, 41774, -12735, 31996, -10079, -17191, -14183],
                                      [122059, 83069, -28256, 52345, -8901, -21222, -9885]),
}
WINDOWS = {"s2d-20261106": W1, "s2d-20261107a": W2}

def r_aa(x, xb):
    d = [x[i] - xb[i] for i in range(len(x))]
    return 3 * est.isqrt_rn(est.rhafz(est.K_MED_E6 * est.sp2(d), 2 * 10**6))

if len(sys.argv) > 1:      # the inputs re-taken from a run directory (its window by the record's run_id)
    run_id = est.read_record(sys.argv[1])["run"]["run_id"]
    if run_id not in WINDOWS:
        sys.exit("rmax_drill: %s is run %s, not one of the drill's windows %s" % (sys.argv[1], run_id, sorted(WINDOWS)))
    res = est.compute(sys.argv[1])
    out, W = res[0], res[4]
    for k, (x, xb) in WINDOWS[run_id].items():
        got = (out[k]["x"], [est.rhafz(t * 10**6, W) for t in out[k]["vb"]])
        if got != (x, xb):
            sys.exit("rmax_drill: %s's values in %s differ from the drill's: %s" % (k, sys.argv[1], got))
    print("inputs: the eight rows' x_l and xb_l equal %s's (run %s)" % (sys.argv[1], run_id))

best = None
for wid, rows in WINDOWS.items():
    print("window %s" % wid)
    print("%-34s %9s %8s %8s  %s" % ("row", "med(x)", "r", "r_AA", "x_l | xb_l"))
    wbest = None
    for k, (x, xb) in rows.items():
        a = r_aa(x, xb)
        wbest = max(wbest or (0, ""), (a, k))
        print("%-34s %9d %8d %8d  %s | %s" % (k[15:], est.med(x), est.resolution(x), a, x, xb))
    print("  window max r_AA = %d (%s); range %d..%d" % (wbest[0], wbest[1], min(r_aa(*v) for v in rows.values()), wbest[0]))
    best = max(best or (0, "", ""), wbest + (wid,))
print("r_max_e6 = max r_AA over both windows = %d (%s, %s), %.4f walkbytes" % (best[0], best[1], best[2], best[0] / 1e6))
