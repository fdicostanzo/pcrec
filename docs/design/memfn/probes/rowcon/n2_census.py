#!/usr/bin/env python3
"""[MEMFN-ROWCON] N2 driver: compile the whole .rxt corpus under EVERY axis
arm with an MF_TRACE pcrec and aggregate the MFTRACE records.

  n2_census.py --bin TRACED_PCREC --tree TREE --out DIR [--jobs N] [--limit N]
               [--arms REGEX] [--smoke-patterns FILE]

Reuses scripts/emit_sweep.py (corpus enumeration, the stream compile argv,
`run`, `distinct_patterns`), so the populations are emit_sweep's own. Per arm,
three streams: corpus argv `.c` at the default engine, at --engine=vm, and the
composition files (`<rxt> -o <dir>`). emit-ir and facts emit no C, so they
reach no kit site. An arm's Agg is saved to DIR/arm_NNN.json when the arm is
done (a re-run skips finished arms: crash-proof, resumable).

ARMS, from `--list-axes` (the registry the identity gates enumerate):
  * the null arm, then every cli_flag (deny AND force spelling, `a|b` and
    `a / b` split) except the -fcomments pair (that is the tier), then
    --tune=min-size|size|speed|max-speed, then every `--memfn=` spelling of
    the memfn section (none until the kit has option rows);
  * each of those at BOTH comment tiers (base "" and -fcomments);
  * plus, at base `-e utf8`: the null arm and the denies the I2 run scopes to
    utf8 (deny bits 16/30/31/32/44/45/46 and -fno-lit-run), tier "" only.
-fmemfn-simd / -fno-memfn-simd are arms here (they change the kit's input).
"""
import argparse
import concurrent.futures
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import n2_report  # noqa: E402


def load_emit_sweep(tree):
    sys.path.insert(0, os.path.join(tree, "scripts"))
    import emit_sweep
    return emit_sweep


FLAG_RE = re.compile(r"^--?[a-z][a-z0-9=-]*$")
UTF8_DENY_BITS = {"16", "30", "31", "32", "44", "45", "46"}
TUNES = ["--tune=min-size", "--tune=size", "--tune=speed", "--tune=max-speed"]
TIER_FLAGS = {"-fcomments", "-fno-comments"}


def list_axes(bin_path):
    p = subprocess.run([bin_path, "--list-axes"], capture_output=True, text=True, timeout=30)
    flags, utf8_denies, memfn = [], [], []
    section = ""
    for ln in p.stdout.splitlines():
        if ln.startswith("#section"):
            section = ln.split()[1]
            continue
        if ln.startswith("#") or not ln.strip():
            continue
        c = ln.split("\t")
        if section == "memfn":
            if len(c) >= 5:
                for s in re.split(r"\s*(?:\||/|,)\s*", c[4]):
                    if s.startswith("--memfn="):
                        memfn.append(s)
            continue
        if section or len(c) < 11:
            continue
        toks = [t for t in re.split(r"\s*(?:\||/)\s*", c[10]) if FLAG_RE.match(t)]
        for t in toks:
            if t not in TIER_FLAGS and t not in flags:
                flags.append(t)
        deny_bits = set(c[7].split("|")) if c[7] else set()
        deny_flags = [t for t in toks if t.startswith("-fno-")]
        if deny_bits & UTF8_DENY_BITS or "-fno-lit-run" in deny_flags:
            utf8_denies += [t for t in deny_flags if t not in utf8_denies]
    if "-fno-lit-run" not in utf8_denies and "-fno-lit-run" in flags:
        utf8_denies.append("-fno-lit-run")
    return flags, utf8_denies, memfn


def build_arms(bin_path):
    flags, utf8_denies, memfn = list_axes(bin_path)
    body = [("null", [])] + [(f, [f]) for f in flags] + [(t, [t]) for t in TUNES] \
        + [(m, [m]) for m in memfn]
    arms = []
    for tier, tflags in (("", []), ("+comments", ["-fcomments"])):
        for lab, fl in body:
            arms.append(("%s%s" % (lab, tier), tflags + fl))
    arms.append(("null@utf8", ["-e", "utf8"]))
    for f in utf8_denies:
        arms.append(("%s@utf8" % f, ["-e", "utf8", f]))
    return arms


def pattern_argv(bin_path, extra, engine, pat):
    argv = [bin_path, "-p", "rx", "--features", "all"]
    if engine:
        argv.append("--engine=%s" % engine)
    return argv + extra + ["-o", "-", "--pattern", pat]


def run_arm(es, bin_path, label, extra, pats, comp_files, tmp, jobs, timeout, comp_timeout):
    agg = n2_report.Agg()

    def one(job):
        kind, src, pat, stream, argv = job
        if kind == "comp":
            outdir = argv[-1]
            os.makedirs(outdir, exist_ok=True)
        rc, _out, err = es.run(argv, comp_timeout if kind == "comp" else timeout)
        if kind == "comp":
            shutil.rmtree(outdir, ignore_errors=True)
        return job, rc, err

    jobs_l = []
    for pat in pats:
        for stream, eng in (("c-default", None), ("c-vm", "vm")):
            jobs_l.append(("pat", "corpus", pat, stream, pattern_argv(bin_path, extra, eng, pat)))
    for i, f in enumerate(comp_files):
        od = os.path.join(tmp, "comp_%s_%d" % (re.sub(r"\W", "_", label), i))
        jobs_l.append(("comp", os.path.basename(f), f, "composition",
                       [bin_path, "--features", "all"] + extra + [f, "-o", od]))
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        for job, rc, err in ex.map(one, jobs_l):
            _kind, src, pat, stream, _argv = job
            agg.count(label, "attempted")
            if rc is None:
                agg.count(label, "timeout")
                continue
            agg.count(label, "ok" if rc == 0 else "refused")
            agg.add(label, stream, src, pat, n2_report.parse_trace(err))
    return agg


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=min(8, os.cpu_count() or 4))
    ap.add_argument("--limit", type=int, default=0, help="first N distinct patterns / N composition files")
    ap.add_argument("--arms", default="", help="ERE on the arm label (smoke / subset)")
    ap.add_argument("--pattern", action="append", default=[], help="smoke: use these patterns, not the corpus")
    ap.add_argument("--timeout", type=int, default=30)
    a = ap.parse_args()

    es = load_emit_sweep(os.path.abspath(a.tree))
    bin_path = os.path.abspath(a.bin)
    os.makedirs(a.out, exist_ok=True)
    tmp = os.path.join(a.out, "tmp")
    os.makedirs(tmp, exist_ok=True)

    corpus = es.enumerate_corpus(bin_path, a.tree, a.timeout)
    pats = es.distinct_patterns(corpus)
    comp_files = es.find_files(a.tree, (".rxt", ".rxtin"))
    if a.pattern:
        pats = a.pattern
    if a.limit:
        pats, comp_files = pats[:a.limit], comp_files[:1]
    arms = build_arms(bin_path)
    todo = [(i, l, e) for i, (l, e) in enumerate(arms) if not a.arms or re.search(a.arms, l)]
    meta = {"corpus rows": len(corpus), "distinct patterns": len(pats),
            "composition files": len(comp_files), "arms in table": len(arms),
            "arms run": len(todo), "bin": bin_path}
    json.dump(meta, open(os.path.join(a.out, "meta.json"), "w"))
    print("n2_census: %s" % meta, flush=True)
    t0 = time.time()
    for i, label, extra in todo:
        path = os.path.join(a.out, "arm_%03d.json" % i)
        if os.path.exists(path):
            print("n2_census: arm %03d %-40s SKIP (done)" % (i, label), flush=True)
            continue
        t1 = time.time()
        agg = run_arm(es, bin_path, label, extra, pats, comp_files, tmp, a.jobs,
                      a.timeout, max(3 * a.timeout, 90))
        agg.save(path)
        print("n2_census: arm %03d %-40s %6.1fs would_decline=%d (elapsed %.0fs)" %
              (i, label, time.time() - t1, agg.would_decline_total(), time.time() - t0), flush=True)
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
