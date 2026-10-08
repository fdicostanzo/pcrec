#!/usr/bin/env python3
"""docs/design/dec_fallback/attempt_hist.py -- [DEC-FALLBACK] B0 item 5: the
ATTEMPT HISTOGRAM, its own driver (dec_fallback.md §4.2 item 5, §4.3 item 4;
critB2 M2).

The independent control of refactor B's attempt count and order: decfb0's
probed scratch copy (`../decision_families/decfb0/build_ref.py`'s PATCHES:
stderr `DECFB` probes at the attempt header, the failure arrival, the [SEL-1]
retry and the rung taken) built at the PARENT and at the CHILD of a B commit,
both from `git archive`, and decfb0's own `census.py` run over decfb0's
population (every distinct .rxt corpus block, its own flags/features/encoding/
engine) per limit variant. The two sides are compared per compile: status,
attempt count (the `att=` probes) and the whole probe sequence (the transition
signature, state values included). It shares no code with the tables T1-T4;
its limits (§4.3 item 4, critB2 m1) are that it shares the `setjmp` site and
`rung->name` with what it watches, lumps the trial catch with other failures,
and sees no state the probes do not print.

PARENT vs CHILD, never pinned absolute counts (critB2 M2): the histogram's
tables would rot with the corpus. What IS pinned is K35's: the population per
side (a `--list-source` that stopped listing would compare two empty sets) and,
per variant, at least one compile with more than one attempt (a probe that
stopped printing would compare two empty signatures).

ANCHORS FAIL CLOSED. The probes are inserted at anchor text in compile.c; a
commit that rewrites an anchor (B3 rewrites the catch branch) makes the build
of that side stop with "anchor drifted". Re-anchoring the CHILD's probes at the
equivalent points is the B3 lane's reviewed edit (`--child-patches FILE`, a
python file defining PATCHES), with the intent re-verified: the new probes
must print the same lines at the same events.

The plain variant's probed build is also held byte-identical (stdout + rc) to
the unprobed build of the same side (census.py's BYTES_DIFF rows), so the
probes provably move nothing they watch.

usage: attempt_hist.py --ref PARENT --rev CHILD [--variants a,b,..]
                       [--out DIR] [--stride N] [--child-patches FILE]
Exit 0 identical, 1 differ or a floor/byte check failed, 2 bad input/build.
"""
import argparse, ast, collections, os, runpy, shutil, subprocess, sys, tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
DECFB0 = os.path.join(ROOT, "docs/design/decision_families/decfb0")
sys.path.insert(0, DECFB0)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import build_ref                      # noqa: E402  PATCHES (the probes)
from emit_sweep import VARIANTS       # noqa: E402  the ONE table of variant -D sets

# K35 floors, measured at B0's base (see the lane report decfbB0_report.md).
# POPULATION_FLOOR: distinct corpus blocks census.py lists, MEASURED 4,794 on
# both sides at B0's base (main ab583f6b vs itself, every variant); ~1% margin,
# emit_sweep PINS' own convention for a population that only grows.
POPULATION_FLOOR = 4746


def log(m):
    print(m, file=sys.stderr, flush=True)


def archive(rev, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    p = subprocess.Popen(["git", "-C", ROOT, "archive", rev], stdout=subprocess.PIPE)
    with tarfile.open(fileobj=p.stdout, mode="r|") as tf:
        tf.extractall(dst)
    if p.wait() != 0:
        sys.exit(f"attempt_hist: git archive {rev} failed")


def build_side(rev, side_dir, patches, variants, jobs):
    """git archive REV -> side_dir/tree (built: census.py's --list-source and
    byte-check binary), side_dir/probe/tree = the patched copy, one probed
    compiler per variant at side_dir/probe/pcrec_<variant>."""
    tree = os.path.join(side_dir, "tree")
    archive(rev, tree)
    r = subprocess.run(["make", f"-j{jobs}"], cwd=tree, capture_output=True)
    if r.returncode:
        sys.stderr.write(r.stderr.decode(errors="replace")[-2000:])
        sys.exit(f"attempt_hist: make failed for {rev}")
    probe = os.path.join(side_dir, "probe")
    ptree = os.path.join(probe, "tree")
    if os.path.exists(probe):
        shutil.rmtree(probe)
    for d in ("src", "lib", "cli", "memfn"):
        shutil.copytree(os.path.join(tree, d), os.path.join(ptree, d),
                        ignore=shutil.ignore_patterns("*.o"))
    cp = os.path.join(ptree, "src/core/compile.c")
    s = open(cp).read()
    for a, rep in patches:
        if s.count(a) != 1:
            sys.exit(f"attempt_hist: {rev}: anchor drifted ({s.count(a)} matches): {a[:60]!r}"
                     " -- re-anchor with --child-patches (see the header)")
        s = s.replace(a, rep)
    open(cp, "w").write(s)
    srcs = sorted(os.path.join(dp, f) for top in ("src", "memfn/src")
                  for dp, _, fs in os.walk(os.path.join(ptree, top)) for f in fs if f.endswith(".c"))
    procs = []
    for v in variants:
        cmd = (["gcc", "-O1", "-std=gnu11", "-I" + ptree + "/lib", "-I" + ptree + "/src"]
               + VARIANTS[v].split() + ["-o", os.path.join(probe, "pcrec_" + v),
                                        ptree + "/cli/main.c"] + srcs)
        procs.append((v, subprocess.Popen(cmd, stderr=subprocess.PIPE)))
    for v, p in procs:
        _, err = p.communicate()
        if p.returncode:
            sys.stderr.write(err.decode(errors="replace")[-2000:])
            sys.exit(f"attempt_hist: probed build {v} failed for {rev}")
    return tree, probe


def census(tree, probe, variant, stride):
    r = subprocess.run([sys.executable, os.path.join(DECFB0, "census.py"), tree, probe,
                        variant, str(stride)], capture_output=True, text=True)
    if r.returncode:
        sys.stderr.write(r.stderr[-2000:])
        sys.exit(f"attempt_hist: census.py failed ({variant})")
    rows = {}
    with open(os.path.join(probe, f"census_{variant}.tsv")) as fh:
        for ln in fh:
            status, key, st, probes = ln.rstrip("\n").split("\t")
            rows[key] = (status, ast.literal_eval(probes))
    return rows


def attempts(probes):
    return sum(1 for p in probes if p.startswith("att="))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", required=True, help="the PARENT revision")
    ap.add_argument("--rev", required=True, help="the CHILD revision")
    ap.add_argument("--variants", default=",".join(VARIANTS))
    ap.add_argument("--out", default=os.path.join(ROOT, "build", "attempt_hist"))
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--child-patches")
    args = ap.parse_args()
    variants = [v for v in args.variants.split(",") if v]
    bad = [v for v in variants if v not in VARIANTS]
    if bad or not variants:
        ap.error(f"--variants: unknown {bad} (known: {','.join(VARIANTS)})")
    child_patches = (runpy.run_path(args.child_patches)["PATCHES"] if args.child_patches
                     else build_ref.PATCHES)
    sides = {}
    for side, rev, patches in (("parent", args.ref, build_ref.PATCHES),
                               ("child", args.rev, child_patches)):
        log(f"[attempt_hist] building {side} {rev} ...")
        sides[side] = build_side(rev, os.path.join(args.out, side), patches, variants, args.jobs)
    ok = True
    full = args.stride == 1
    print(f"attempt histogram: parent {args.ref} vs child {args.rev}, variants {','.join(variants)}"
          + ("" if full else f", stride {args.stride} (floors NOT applied)"))
    for v in variants:
        log(f"[attempt_hist] census {v} ...")
        a = census(*sides["parent"], v, args.stride)
        b = census(*sides["child"], v, args.stride)
        common = sorted(set(a) & set(b))
        only = (len(set(a) - set(b)), len(set(b) - set(a)))
        diff = [k for k in common if a[k] != b[k]]
        hist = [collections.Counter(attempts(s[k][1]) for k in common) for s in (a, b)]
        multi = [sum(n for c, n in h.items() if c > 1) for h in hist]
        bytes_diff = [sum("BYTES_DIFF" in s[k][1] for k in s) for s in (a, b)]
        print(f"-- {v}: population {len(a)}/{len(b)} common {len(common)} only-parent {only[0]} "
              f"only-child {only[1]}; histogram (attempts: compiles) "
              + " ".join(f"{c}:{hist[0][c]}/{hist[1][c]}" for c in sorted(set(hist[0]) | set(hist[1]))))
        bad = []
        if diff:
            bad.append(f"{len(diff)} compiles differ")
            for k in diff[:10]:
                print(f"   {k}\n     parent {a[k][0]} {a[k][1]}\n     child  {b[k][0]} {b[k][1]}")
        if only != (0, 0):
            bad.append(f"population differs ({only[0]} parent-only, {only[1]} child-only)")
        if full and min(len(a), len(b)) < POPULATION_FLOOR:
            bad.append(f"population {min(len(a), len(b))} < floor {POPULATION_FLOOR} (K35)")
        if full and min(multi) < 1:
            bad.append("no compile took more than one attempt: the probes stopped printing (K35)")
        if v == "plain" and any(bytes_diff):
            bad.append(f"probed build's bytes differ from the unprobed build ({bytes_diff[0]}/{bytes_diff[1]})")
        print(f"   {'DIFFERS: ' + '; '.join(bad) if bad else 'identical'}; multi-attempt compiles "
              f"{multi[0]}/{multi[1]}" + (f"; BYTES_DIFF {bytes_diff[0]}/{bytes_diff[1]}" if v == "plain" else ""))
        ok = ok and not bad
    print("ATTEMPT HISTOGRAM: " + ("IDENTICAL" if ok else "DIFFERS"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
