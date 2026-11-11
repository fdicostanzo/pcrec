#!/usr/bin/env python3
"""tests/ci/cloud_measure.py -- MEASURE: per-unit wall times of a cloud kind, from recent completed runs
([CLOUD-SUITE] reweigh, step 1).

  python3 tests/ci/cloud_measure.py KIND [--last N | --runs ID..] [--ci-runs ID..] [--write] [--repo OWNER/NAME]
                                         [--cache DIR]

KIND is a row of tests/ci/cloud_kinds.tsv; its `measured` column names the committed file this writes
(tests/ci/measured_KIND.tsv: `unit  median_s  n  min_s  max_s  basis`, a provenance header naming the run ids, dates, the
runner CPU mix). Runs come from `gh run list` (the Cloud workflow, branches cloud/OWNER/KIND/NAME, completed) or
--runs; --ci-runs adds CI runs (their `pcrec-ci-sections-*` artifacts are the same per-section shape; test-kind only
in practice). Per shard artifact the units are `units.tsv` (tests/ci/cloud_units.py, written by the shard record step)
or, for a run that predates it, parsed from the shard's log the same way. Only a shard with rc 0 counts (a red shard's
units are partial). Per run a unit's seconds is its one value (units live in one shard); `@wall` is the run's slowest
shard, `@baseline`/`@build` the median over its shards. The file's value is the MEDIAN over runs. Artifacts are cached
under --cache (default $PCREC_TMPDIR/scratch/cloud_measure), never in the tree. Without --write, prints the file.
"""
import argparse
import collections
import glob
import importlib.util
import json
import os
import statistics
import subprocess
import sys

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("cloud_units", os.path.join(here, "cloud_units.py"))
cu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cu)


def sh(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode:
        sys.exit("cloud_measure: %s failed: %s" % (" ".join(cmd[:4]), r.stderr.strip()[:300]))
    return r.stdout


def kinds_get(kind, field):
    return sh(["bash", os.path.join(here, "cloud_kinds.sh"), "get", kind, field]).strip()


def kv(path):
    d = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        if "=" in line:
            k, v = line.rstrip("\n").split("=", 1)
            d.setdefault(k, v)
    return d


def discover(kind, repo, last):
    j = json.loads(sh(["gh", "run", "list", "-R", repo, "-w", "Cloud", "-L", "200", "--json",
                       "databaseId,headBranch,status,conclusion,createdAt"]))
    runs = [r for r in j if r["status"] == "completed" and r["conclusion"] in ("success", "failure")
            and len(r["headBranch"].split("/")) >= 3 and r["headBranch"].split("/")[2] == kind]
    runs.sort(key=lambda r: r["createdAt"], reverse=True)
    return runs[:last]


def fetch(run, repo, cache, pattern):
    d = os.path.join(cache, str(run))
    if not (os.path.isdir(d) and os.listdir(d)):
        os.makedirs(d, exist_ok=True)
        r = subprocess.run(["gh", "run", "download", str(run), "-R", repo, "-D", d, "-p", pattern],
                           capture_output=True, text=True)
        if r.returncode:
            print("cloud_measure: run %s: download: %s" % (run, r.stderr.strip()[:200]), file=sys.stderr)
    return d


def apportion(res, selector):
    """A shard with no per-unit record (a run that predates cloud_units.py, and not a sections run): its measured step
    wall split over its units in proportion to the weights of the table that run used (`git show SHA:selector`).
    A labelled ESTIMATE of the shard's units -- the shard total is measured, the split inside it is not."""
    r = kv(res)
    try:
        wall = float(r["wall_s"]) if r.get("wall_s", "?") != "?" else cu.parse(os.path.join(os.path.dirname(res), "test.log"), None)["@wall"]
        k = r["shard"].split("/")[0]
    except (KeyError, ValueError):
        return {}
    root = os.path.join(here, "..", "..")
    t = subprocess.run(["git", "-C", root, "show", "%s:%s" % (r.get("sha", "?"), selector)], capture_output=True, text=True)
    if t.returncode:
        return {}
    rows = [l.split("\t") for l in t.stdout.splitlines() if l and not l.startswith("#") and l.count("\t") >= 2]
    mine = [(c[0], float(c[2])) for c in rows[1:] if c[1] == k]     # rows[0] is the column-name line
    tot = sum(w for _, w in mine)
    return {u: wall * w / tot for u, w in mine} if tot else {}


def run_samples(d, selector=None, appo=False, estimated=None):
    """-> (units {name: seconds}, cpus Counter, shards_used) of one run's cloud-shard-* artifacts."""
    units, fixed, cpus, used, walls = {}, collections.defaultdict(list), collections.Counter(), 0, []
    for sd in sorted(glob.glob(os.path.join(d, "cloud-shard-*"))):
        res = os.path.join(sd, "result.txt")
        if not os.path.exists(res) or kv(res).get("rc") != "0":
            continue
        used += 1
        cpus[kv(res).get("cpu_model", "unknown")] += 1
        ut = os.path.join(sd, "units.tsv")
        if os.path.exists(ut):
            rows = {l.split("\t")[0]: float(l.split("\t")[1]) for l in open(ut) if l.count("\t") == 1}
        else:
            rows = cu.parse(os.path.join(sd, "test.log"), os.path.join(sd, "sections.tsv"))
        if not [k for k in rows if not k.startswith("@")] and appo and selector:
            ap = apportion(res, selector)
            if estimated is not None:
                estimated.update(ap)
            rows = dict(ap, **rows)
        for k, v in rows.items():
            if k == "@wall":
                walls.append(v)
            elif k.startswith("@"):
                fixed[k].append(v)
            else:
                units[k] = max(units.get(k, 0), v)
    if walls:
        units["@wall"] = max(walls)
    for k, v in fixed.items():
        units[k] = statistics.median(v)
    return units, cpus, used


def ci_samples(d):
    units = {}
    for f in sorted(glob.glob(os.path.join(d, "pcrec-ci-sections-*", "sections.tsv"))):
        units.update(cu.parse(None, f))
    return units


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kind")
    ap.add_argument("--last", type=int, default=6)
    ap.add_argument("--runs", nargs="*", default=None)
    ap.add_argument("--ci-runs", nargs="*", default=[])
    ap.add_argument("--repo", default=None)
    ap.add_argument("--cache", default=None)
    ap.add_argument("--apportion", action="store_true",
                    help="a shard with no per-unit record gets its measured wall split over its units by the table weights "
                         "(labelled `apportioned`): for runs that predate the per-unit record")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    out = os.path.join(here, "..", "..", kinds_get(a.kind, "measured"))
    repo = a.repo or sh(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"]).strip()
    cache = a.cache or os.path.join(os.environ.get("PCREC_TMPDIR") or "/var/tmp/pcrec-%s" % os.environ.get("USER", "x"),
                                    "scratch", "cloud_measure")
    meta = {}
    if a.runs is None:
        for r in discover(a.kind, repo, a.last):
            meta[str(r["databaseId"])] = (r["createdAt"][:10], r["headBranch"], r["conclusion"])
    else:
        for r in a.runs:
            meta[r] = ("?", "(given)", "?")
    samples, cpus, prov, est = [], collections.Counter(), [], set()
    selector = kinds_get(a.kind, "selector")
    for run, (date, branch, concl) in meta.items():
        e = {}
        u, c, used = run_samples(fetch(run, repo, cache, "cloud-shard-*"), selector, a.apportion, e)
        est.update(e)
        if not used or not [k for k in u if not k.startswith("@")]:
            print("cloud_measure: run %s: no usable (rc 0, per-unit) shard result -- skipped (use --apportion for a run "
                  "that predates the per-unit record)" % run, file=sys.stderr)
            continue
        samples.append(u)
        cpus.update(c)
        prov.append("%s (%s, %s, %s, %d shards counted)" % (run, date, branch, concl, used))
    for run in a.ci_runs:
        u = ci_samples(fetch(run, repo, cache, "pcrec-ci-sections-*"))
        if u:
            samples.append(u)
            prov.append("%s (CI run, pcrec-ci-sections-*)" % run)
    if not samples:
        sys.exit("cloud_measure: no usable run for kind %s" % a.kind)
    names = sorted({k for s in samples for k in s}, key=lambda k: (not k.startswith("@"), k))
    rows = []
    for k in names:
        v = [s[k] for s in samples if k in s]
        rows.append("%s\t%.1f\t%d\t%.1f\t%.1f\t%s" % (k, statistics.median(v), len(v), min(v), max(v),
                                                        "apportioned" if k in est else "measured"))
    head = ["# %s -- MEASURED per-unit seconds of the `%s` kind, GENERATED by tests/ci/cloud_measure.py (median over runs;"
            % (kinds_get(a.kind, "measured"), a.kind),
            "# units: tests/ci/cloud_units.py; `@wall` = a run's slowest shard step, `@baseline`/`@build` = per-shard fixed cost;",
            "# basis `apportioned` = a shard total split over its units by the table weights, an ESTIMATE until a run records the unit).",
            "# runs (%d): %s" % (len(prov), "; ".join(prov)),
            ("# runner cpus (shards counted): " + ", ".join("%s x%d" % (m, n) for m, n in cpus.most_common()))
            if cpus else "# runner cpus: (CI runs only; not recorded)",
            "unit\tmedian_s\tn\tmin_s\tmax_s\tbasis"]
    text = "\n".join(head + rows) + "\n"
    if a.write:
        open(out, "w").write(text)
        print("cloud_measure: wrote %s (%d units from %d runs)" % (os.path.normpath(out), len(rows), len(samples)),
              file=sys.stderr)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
