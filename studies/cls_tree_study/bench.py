#!/usr/bin/env python3
"""bench.py — ns/char for each policy's matcher, on a quiet box.

Protocol copied from `docs/dev/lanes/isl1_report.md` §12 by way of
`studies/form_char_twins/time_twins.sh` §8, because a house protocol that
changes per study cannot be compared across studies:

  * N rounds (default 11), ARMS INTERLEAVED round by round — never arm A's
    eleven rounds then arm B's.
  * the 1-minute load average gated (`loadgate.wait_for_quiet`) BEFORE every
    timed unit (one regime run), waiting up to `--max-load-wait` seconds for
    a quiet box rather than refusing on the first over-threshold reading —
    the harness's OWN compiles and timing runs are sustained CPU work with
    no idle gaps, so a gate checked once per SET was measuring itself (lane
    clsgate, 2026-09-29; see loadgate.py's header). The threshold itself is
    UNCHANGED (still 0.5 by default) and a box that stays loaded past the
    bound still gets an honest refusal with its readings — never a caveat.
  * ALL arms for ALL sets are built before ANY timing starts, so a set's
    compile never straddles a gate check.
  * median ns/char reported with the per-round range.
  * every round's answer CHECKSUMMED (the hit count and a positional sum)
    and compared against the reference arm — a timing run that stops
    measuring the right answer reports nothing.

ARMS, per set:
  refbs    flat binary search over the WHOLE interval list.  This is
           [CLS-TREE]'s own seed representation ("a binary tree of ranges")
           measured as an arm rather than assumed as a baseline, so the memo
           can say what the kit buys OVER the seed and not merely over
           today's automaton.
  bitmap1  ONE bitmap over the set's whole span.  The naive "class as data"
           a reader would reach for first; it is here to be beaten on size.
  lam=...  the kit at each policy.
"""

import argparse
import os
import subprocess
import sys
import time

import emit
import kit
import loadgate
import section

HERE = os.path.dirname(os.path.abspath(__file__))
CC = os.environ.get("CC", "gcc-16")

DRIVER = r"""
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define NCP (1u << 20)
static unsigned subj[NCP];

static unsigned long long rnd_s = 88172645463325252ULL;
static unsigned long long rnd(void)
{ rnd_s ^= rnd_s << 13; rnd_s ^= rnd_s >> 7; rnd_s ^= rnd_s << 17; return rnd_s; }

static unsigned pick_member(const unsigned *mlo, const unsigned *mhi,
                            int mn, unsigned long nmem)
{
    unsigned long r = rnd() % nmem, acc = 0; int k = 0;
    for (k = 0; k < mn; k++) {
        unsigned long c = mhi[k] - mlo[k] + 1;
        if (r < acc + c) break;
        acc += c;
    }
    if (k == mn) k = mn - 1;
    return mlo[k] + (unsigned)(r - acc);
}

static void build_subject(const char *regime, const unsigned *mlo,
                          const unsigned *mhi, int mn, unsigned long nmem)
{
    /* `runs` (added 2026-09-28, lane clsdes88): a crude model of TEXT —
     * runs of 1..32 code points drawn uniformly from the 256-code-point
     * block around one random member, so consecutive probes land in the
     * same region the way a script run does and the dispatch tree's
     * branches become predictable.  Members and non-members both occur. */
    if (!strcmp(regime, "runs")) {
        unsigned i = 0;
        while (i < NCP) {
            unsigned blk = pick_member(mlo, mhi, mn, nmem) & ~0xFFu;
            unsigned len = 1u + (unsigned)(rnd() % 32);
            for (unsigned j = 0; j < len && i < NCP; j++, i++) {
                unsigned cp = blk + (unsigned)(rnd() & 0xFF);
                subj[i] = cp > 0x10FFFFu ? 0x10FFFFu : cp;
            }
        }
        return;
    }
    for (unsigned i = 0; i < NCP; i++) {
        unsigned cp;
        if (!strcmp(regime, "member") ||
            (!strcmp(regime, "mixed") && (rnd() & 1))) {
            unsigned long r = rnd() % nmem, acc = 0; int k = 0;
            for (k = 0; k < mn; k++) {
                unsigned long c = mhi[k] - mlo[k] + 1;
                if (r < acc + c) break;
                acc += c;
            }
            if (k == mn) k = mn - 1;
            cp = mlo[k] + (unsigned)(r - acc);
        } else if (!strcmp(regime, "ascii")) {
            cp = (unsigned)(rnd() % 128);
        } else {
            cp = (unsigned)(rnd() % 0x110000u);
        }
        subj[i] = cp;
    }
}

typedef int (*armfn)(unsigned);

static double now_s(void)
{ struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
  return t.tv_sec + 1e-9 * t.tv_nsec; }

int main(int argc, char **argv)
{
    const char *regime = argc > 1 ? argv[1] : "mixed";
    int rounds = argc > 2 ? atoi(argv[2]) : 11;
    build_subject(regime, ref_lo, ref_hi, REF_N, REF_NMEM);

    for (int r = 0; r < rounds; r++) {
        for (int a = 0; a < NARMS; a++) {
            unsigned long hits = 0, chk = 0;
            double t0 = now_s();
            for (unsigned i = 0; i < NCP; i++) {
                int v = arms[a](subj[i]);
                hits += (unsigned long)v;
                chk += (unsigned long)v * (i + 1u);
            }
            double el = now_s() - t0;
            printf("ROUND %d ARM %s ns_per_char %.4f hits %lu chk %lu\n",
                   r, armnames[a], 1e9 * el / (double)NCP, hits, chk);
            fflush(stdout);
        }
    }
    return 0;
}
"""


def gen(setname, iv, lams, outdir, whole_arms=False):
    arms, names, srcs = [], [], []

    srcs.append(emit.reference("a_refbs", iv))
    names.append("refbs")

    whole = [(iv[0][0], iv[-1][1])]
    bm = kit.FormBitmap(iv)
    srcs.append(bm.tables("a_bm1_t"))
    x = "(cp - %uu)" % bm.base if bm.base else "cp"
    srcs.append("static int a_bm1(unsigned cp)\n{\n"
                "    if ((unsigned)(cp - %uu) > %uu) return 0;\n"
                "    return (int)%s;\n}\n"
                % (bm.base, bm.w - 1, bm.expr(x, "a_bm1_t")))
    names.append("bitmap1")
    del whole

    for lam in lams:
        sc, _, _, fo = section.partition_c(iv, lam)
        fn = "a_l%s" % str(lam).replace(".", "_")
        s, _ = emit.emit(fn, iv, sc, fo, static=False)
        srcs.append(s)
        names.append("lam%g" % lam)

    arms = ["a_refbs", "a_bm1"] + \
           ["a_l%s" % str(l).replace(".", "_") for l in lams]

    # WHOLE-SET indexed tables (wholeset.py), OFF by default so the
    # committed 2026-09-11 arm set reproduces unchanged.
    if whole_arms:
        import wholeset
        srcs.append(wholeset.PageW2(iv).c("a_pw2"))
        srcs.append(wholeset.PageW3(iv).c("a_pw3"))
        names += ["page2w", "page3w"]
        arms += ["a_pw2", "a_pw3"]

    nmem = sum(h - l + 1 for l, h in iv)
    tbl = ("static const unsigned ref_lo[%d] = { %s };\n"
           "static const unsigned ref_hi[%d] = { %s };\n"
           "#define REF_N %d\n#define REF_NMEM %luUL\n"
           % (len(iv), ", ".join("%uu" % l for l, _ in iv),
              len(iv), ", ".join("%uu" % h for _, h in iv),
              len(iv), nmem))
    armtbl = ("#define NARMS %d\n"
              "static int (*const arms[NARMS])(unsigned) = { %s };\n"
              "static const char *const armnames[NARMS] = { %s };\n"
              % (len(arms), ", ".join(arms),
                 ", ".join('"%s"' % n for n in names)))

    path = os.path.join(outdir, setname + "_bench.c")
    with open(path, "w") as f:
        f.write(emit.PRELUDE)
        f.write("".join(srcs))
        f.write(tbl)
        f.write(armtbl)
        f.write(DRIVER)
    return path, names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--population", default="k53")
    ap.add_argument("--sets", default="")
    ap.add_argument("--lams", default="0,16,256")
    ap.add_argument("--rounds", type=int, default=11)
    ap.add_argument("--regimes", default="member,mixed,ascii,full")
    ap.add_argument("--max-load", type=float, default=0.5)
    ap.add_argument("--max-load-wait", type=float, default=600.0,
                    help="bounded wait (seconds) for a quiet box before a "
                         "timed unit refuses (default 600 = 10 min)")
    ap.add_argument("--max-load-poll", type=float, default=10.0,
                    help="poll interval (seconds) while waiting for quiet")
    ap.add_argument("--out", default="bench.tsv")
    ap.add_argument("--whole", action="store_true",
                    help="add the whole-set page2w/page3w arms (wholeset.py)")
    args = ap.parse_args()

    import clsets
    pop = clsets.population(args.population)
    if args.sets:
        want = set(args.sets.split(","))
        pop = [(n, iv) for n, iv in pop if n in want]
    lams = [float(x) for x in args.lams.split(",")]

    la0 = loadgate.wait_for_quiet(args.max_load, args.max_load_wait,
                                  args.max_load_poll, tag="bench")

    outdir = os.path.join(HERE, "build", "bench")
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    path = os.path.join(HERE, "results", args.out)

    # --- BUILD PHASE: every arm for every set, compiled BEFORE any timing
    # starts, so a set's gcc invocation never straddles a load-gate check
    # (lane clsgate, 2026-09-29 — see loadgate.py's header). ---
    built = []
    for name, iv in pop:
        tag = "".join(c if c.isalnum() else "_" for c in name)
        cpath, names = gen(tag, iv, lams, outdir, args.whole)
        bpath = os.path.join(outdir, tag + "_bench")
        r = subprocess.run([CC, "-O2", "-std=gnu11", "-w", cpath,
                            "-o", bpath], capture_output=True, text=True)
        if r.returncode:
            sys.stderr.write("BUILD FAIL %s: %s\n"
                             % (name, r.stderr.strip()[:200]))
            continue
        built.append((name, bpath))

    # --- TIMING PHASE: gate-and-wait immediately before EACH timed unit
    # (one regime run), not once per set. ---
    with open(path, "w") as out:
        out.write("# cc=%s rounds=%d load1_at_start=%.2f date=%s\n"
                  % (CC, args.rounds, la0, time.strftime("%Y-%m-%dT%H:%M:%S")))
        out.write("set\tregime\tarm\tround\tns_per_char\thits\tchk\n")
        for name, bpath in built:
            for regime in args.regimes.split(","):
                loadgate.wait_for_quiet(args.max_load, args.max_load_wait,
                                        args.max_load_poll,
                                        tag="bench %s/%s" % (name, regime))
                r = subprocess.run([bpath, regime, str(args.rounds)],
                                   capture_output=True, text=True)
                ref = {}
                for ln in r.stdout.splitlines():
                    p = ln.split()
                    if len(p) != 10 or p[0] != "ROUND":
                        continue
                    rd, arm, ns, hits, chk = p[1], p[3], p[5], p[7], p[9]
                    key = (regime, rd)
                    if arm == "refbs":
                        ref[key] = (hits, chk)
                    elif key in ref and ref[key] != (hits, chk):
                        sys.exit("bench: ANSWER MISMATCH %s %s arm=%s round=%s"
                                 % (name, regime, arm, rd))
                    out.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n"
                              % (name, regime, arm, rd, ns, hits, chk))
                out.flush()
    print("wrote", path)


if __name__ == "__main__":
    main()
