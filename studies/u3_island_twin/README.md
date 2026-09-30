# u3_island_twin -- run recipe

    make -C ../.. CC=gcc-16                    # build/pcrec
    python3 gen_bases.py all                   # today's artifacts (l/xwd take ~1 min each)
    python3 gen_bases.py l,xwd bigcap          # size-cap-raised arm
    python3 gen_bases.py x1,x2 basec           # null-control copies
    python3 subjects.py                        # correctness + bench subjects
    python3 build_twins.py c1 c3 nd l xwd x1 x2 x3
    ORACLE=remote python3 check.py CASE        # 10.46 over ssh (light)
    SAN=1 python3 check.py CASE                # ASan+UBSan
    python3 controls.py; python3 reach.py
    ./bundle.sh                                # -> out/u3twin_bundle.tgz for the timing box

Timing (quiet box only): unpack the bundle, `python3 run_bench.py --cc gcc
--rounds 11 --out results/bench_ubuntubudu.tsv`, then `python3 summarize.py`.
The load gate refuses rather than caveats.

Cases: c1/c3 (`[\x{100}-\x{2000}]+`, `[\x{100}-\x{FFFF}]+`), nd, l, xwd
(consuming wide classes; all-byte artifact exists), x1 (lookbehind, wide
class context), x2 (`(?<!W)W+(?!W)`, W wide), x3 (`\b\w+\b` under UCP, refused
by pcrec today). Arms: bb today's artifact, bc null control, bd size cap
raised, bv forced VM, ia/ib/ic island + kit4/page3w/bitmap1.
