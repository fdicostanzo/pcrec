#!/usr/bin/env python3
"""docs/design/memfn/r17b_prime/b3a/pick_census.py -- R17-b' B3a's KW-8
AGREEMENT CENSUS (lane b3a; r17b_prime.md rev 3 §3.1 row B3a, §8.1 B3a
"the five-pick shadow: 100% agreement, reported per pick, with per-pick
floors on non-trivial sites" [rev3 D10]).

    pick_census.py --bin TRACE_PCREC --ls-bin PCREC [--pop corpus,bench,rwquest]
                   [--bench-dir DIR] [--every N] [--jobs J] [--arm FLAGS]...
                   [--floors FILE] [--write FILE] [--tmp DIR]

WHAT IT COUNTS. Every pattern of each population compiled by a pcrec built
with -DPCREC_CAND_TRACE, under each arm (default: no flag, `-e utf8`,
`--engine=vm`), and that build's OWN `MFPICK` records (src/gen/emit_dfa.c
`req_pick_shadow`): per pick (set, scan, window, leads, dominated, landmark)
the records, those that AGREE (the kit's port answers what pcrec's own
function answers), the NON-TRIVIAL ones (two or more live alternatives) and
those agreeing, and the ones whose pick is not its family default; and per
`MFPICKSITE` state (stated, withheld-one-attempt, withheld-whole,
port-refused) the shadows. The records are pcrec's: the comparator is
pcrec's code, the subject the kit's port.

THE POPULATIONS (r17b_prime.md §8.1 [rev3 B17]: corpus, bench, rwquest):
  corpus   emit_sweep's own (`--list-source` over tests/**/*.rxt, imported
           from scripts/emit_sweep.py, never re-derived);
  bench    every `bench/*/patterns/*.rx` of the sibling pcrec-bench checkout
           (READ ONLY), one raw pattern per file;
  rwquest  docs/dev/lanes/rwquest/questions.tsv's `pattern` column, its
           `flags` as inline (?ims) and `-e utf8` / `--ucp` arguments.

WHAT IT CHECKS (exit 1 on any):
  - every record agrees (KW-8's 100%); the first disagreements are printed;
  - no shadow was refused by the port (`port-refused`);
  - with --floors FILE: every (population, pick) non-trivial-agree count
    holds at least its floor ([rev3 D10]; a count that FALLS is a pick the
    shadow stopped reaching), and for the boolean picks (scan, leads,
    dominated, landmark) both values of `differs` hold theirs (a row's
    fourth column names the counter: `differs`, or `same` = records -
    differs);
  - K35: every population is non-empty and every pick is reached somewhere.
--write FILE writes floor(0.9 x measured) per (population, pick) for a
reviewed pin.
"""
import argparse
import collections
import concurrent.futures
import glob
import os
import subprocess
import sys

PICKS = ("set", "scan", "window", "leads", "dominated", "landmark")
# the picks whose answer is a family default or not (MFPICK `differs`):
# floored on BOTH values (lane b3afix, MINOR-4), so a port that answers one
# constant cannot agree, and neither can a pcrec side that stopped varying
BOOLEAN_PICKS = ("scan", "leads", "dominated", "landmark")


def tree_default():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))


def corpus(ls_bin, tree):
    import importlib.util
    spec = importlib.util.spec_from_file_location("emit_sweep", os.path.join(tree, "scripts/emit_sweep.py"))
    es = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(es)
    return [([], pat) for pat in sorted({pat for _, _, pat in es.enumerate_corpus(ls_bin, tree, 120)})]


def bench(bench_dir):
    out = []
    for f in sorted(glob.glob(os.path.join(bench_dir, "bench", "*", "patterns", "*.rx"))):
        with open(f, "rb") as fh:
            b = fh.read()
        if b.endswith(b"\n"):
            b = b[:-1]
        if b:
            out.append(([], os.fsdecode(b)))
    return out


def rwquest(tree):
    out = []
    path = os.path.join(tree, "docs/dev/lanes/rwquest/questions.tsv")
    with open(path, encoding="utf-8", errors="surrogateescape") as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        ip, iflag = hdr.index("pattern"), hdr.index("flags")
        for ln in fh:
            c = ln.rstrip("\n").split("\t")
            if len(c) <= max(ip, iflag) or not c[ip]:
                continue
            pat, flags = c[ip], [] if c[iflag] in ("", "-") else c[iflag].split(",")
            args = []
            ims = "".join(f for f in flags if f in ("i", "m", "s"))
            if ims:
                pat = "(?%s)%s" % (ims, pat)
            if "utf" in flags:
                args += ["-e", "utf8"]
            if "ucp" in flags:
                args += ["--ucp"]
            out.append((args, pat))
    return out


def one(binp, tmp, args, pat, arm, k):
    d = os.path.join(tmp, "c%d" % k)
    os.makedirs(d, exist_ok=True)
    argv = [binp, "-p", "rx", "--features", "all"] + args + arm + ["-o", os.path.join(d, "o.c"),
                                                                 "--pattern", pat]
    try:
        r = subprocess.run(argv, capture_output=True, timeout=120)
    except subprocess.TimeoutExpired:
        return None, []
    recs = []
    for ln in r.stderr.decode("utf-8", "replace").splitlines():
        if ln.startswith("MFPICK\t") or ln.startswith("MFPICKSITE\t"):
            recs.append(ln.split("\t"))
    return r.returncode, recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--ls-bin", required=True)
    ap.add_argument("--tree", default=tree_default())
    ap.add_argument("--pop", default="corpus,bench,rwquest")
    ap.add_argument("--bench-dir", default=os.path.abspath(os.path.join(tree_default(), "../pcrec-bench"))
                    if os.path.isdir(os.path.join(tree_default(), "../pcrec-bench"))
                    else "/home/pcrec/projects/pcrec-bench")
    ap.add_argument("--every", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--arm", action="append")
    ap.add_argument("--floors")
    ap.add_argument("--write")
    ap.add_argument("--tmp", default=os.environ.get("TMPDIR", "/tmp"))
    a = ap.parse_args()
    arms = [x.split() for x in (a.arm or ["", "-e utf8", "--engine=vm"])]
    pops = {}
    for p in a.pop.split(","):
        if p == "corpus":
            pops[p] = corpus(a.ls_bin, a.tree)
        elif p == "bench":
            pops[p] = bench(a.bench_dir)
        elif p == "rwquest":
            pops[p] = rwquest(a.tree)
        else:
            raise SystemExit("unknown population %r" % p)
        pops[p] = pops[p][::a.every]
    cnt = collections.Counter()
    sites = collections.Counter()
    bad = []
    timeouts = collections.Counter()
    jobs = [(pop, args, pat, arm) for pop, items in pops.items() for args, pat in items for arm in arms]
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(one, a.bin, a.tmp, args, pat, arm, k % (a.jobs * 4)): (pop, args, pat, arm)
                for k, (pop, args, pat, arm) in enumerate(jobs)}
        for f in concurrent.futures.as_completed(futs):
            pop, args, pat, arm = futs[f]
            rc, recs = f.result()
            if rc is None:
                timeouts[pop] += 1
            for r in recs:
                if r[0] == "MFPICKSITE":
                    sites[(pop, r[1])] += 1
                    if r[1] == "port-refused":
                        bad.append("%s port-refused %s %s" % (pop, " ".join(args + arm), pat))
                    continue
                _, pick, agree, nt, differs, pc, kit, kind = r[:8]
                key = (pop, pick)
                cnt[key + ("records",)] += 1
                cnt[key + ("agree",)] += agree == "1"
                cnt[key + ("nontrivial",)] += nt == "1"
                cnt[key + ("nt_agree",)] += nt == "1" and agree == "1"
                cnt[key + ("differs",)] += differs == "1"
                if agree != "1" and len(bad) < 200:
                    bad.append("%s %s disagree pcrec=%s kit=%s kind=%s arm=[%s] %s" %
                               (pop, pick, pc, kit, kind, " ".join(args + arm), pat))
    print("# pick census: populations %s, arms %s, every %d" %
          ({p: len(v) for p, v in pops.items()}, [" ".join(x) or "-" for x in arms], a.every))
    print("pop\tpick\trecords\tagree\tnontrivial\tnt_agree\tdiffers")
    fails = 0
    for pop in pops:
        for pick in PICKS:
            k = (pop, pick)
            print("%s\t%s\t%d\t%d\t%d\t%d\t%d" % (pop, pick, cnt[k + ("records",)], cnt[k + ("agree",)],
                                                 cnt[k + ("nontrivial",)], cnt[k + ("nt_agree",)],
                                                 cnt[k + ("differs",)]))
    print("pop\tsite-state\tshadows")
    for (pop, st), n in sorted(sites.items()):
        print("%s\t%s\t%d" % (pop, st, n))
    for pop in pops:
        if timeouts[pop]:
            print("TIMEOUTS %s %d" % (pop, timeouts[pop]))
    for pop, items in pops.items():
        if not items:
            print("FAIL: population %s is empty (K35)" % pop)
            fails += 1
    for pick in PICKS:
        if not any(cnt[(pop, pick, "records")] for pop in pops):
            print("FAIL: pick %s is reached nowhere (K35)" % pick)
            fails += 1
    for b in bad:
        print("FAIL: " + b)
    fails += len(bad)
    if a.floors:
        with open(a.floors) as fh:
            for ln in fh:
                if ln.startswith("#") or not ln.strip():
                    continue
                f = ln.rstrip("\n").split("\t")
                pop, pick, fl = f[:3]
                what = f[3] if len(f) > 3 and f[3] else "nt_agree"
                if pop not in pops:
                    continue
                if what == "same":       # records whose pick IS its family default
                    got = cnt[(pop, pick, "records")] - cnt[(pop, pick, "differs")]
                elif what in ("nt_agree", "differs"):
                    got = cnt[(pop, pick, what)]
                else:
                    raise SystemExit("unknown floor counter %r" % what)
                if got < int(fl):
                    print("FAIL: floor %s %s %s %d < %s" % (pop, pick, what, got, fl))
                    fails += 1
                else:
                    print("PASS: floor %s %s %s %d >= %s" % (pop, pick, what, got, fl))
    if a.write:
        with open(a.write, "w") as fh:
            fh.write("# pop\tpick\tfloor (floor(0.9 x measured))\tcounter (nt_agree when empty)\n")
            for pop in pops:
                for pick in PICKS:
                    fh.write("%s\t%s\t%d\n" % (pop, pick, int(cnt[(pop, pick, "nt_agree")] * 9 // 10)))
                for pick in BOOLEAN_PICKS:
                    d = cnt[(pop, pick, "differs")]
                    fh.write("%s\t%s\t%d\tdiffers\n" % (pop, pick, d * 9 // 10))
                    fh.write("%s\t%s\t%d\tsame\n" % (pop, pick, (cnt[(pop, pick, "records")] - d) * 9 // 10))
    print("PICK_CENSUS_DONE fails=%d" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
