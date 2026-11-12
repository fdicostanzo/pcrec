#!/usr/bin/env python3
"""tests/ci/cloud_units_plan.py -- derive the cloud axes / sanitizer shard tables ([CLOUD-SUITE] C).

  python3 tests/ci/cloud_units_plan.py axes [--plan PLAN.txt] (--log AXES.log | --measured F..) [--shards N | --slots S] [--write]
  python3 tests/ci/cloud_units_plan.py san  [--measured F..] [--shards N | --slots S] [--write]
  python3 tests/ci/cloud_units_plan.py mech [--measured F..] [--shards N | --slots S] [--write]

REWEIGH ([CLOUD-SUITE]; tests/ci/cloud_reweight.sh runs this): --measured = the committed measured files
(tests/ci/measured_KIND.tsv, written by tests/ci/cloud_measure.py; several files = kinds sharing the table, a unit's
weight is their mean). A measured unit carries its runner seconds; a unit with no measurement keeps the old local/proxy
ESTIMATE and says so in weight_source. --slots S (the kind's max_parallel) picks the smallest shard count within 5 % of
the best the largest unit and total allow, never above S; --shards N pins it. The header gets `# predicted_shard_s=`
(heaviest shard's step, what cloud_gather.sh compares), `# predicted_wall_s=` (+ setup_s) and `# indivisible_floor_s=`.

axes: PLAN.txt is `AXES_PLAN=1 AXES_FULL=1 bash tests/axes/run_axes.sh` stdout (the plan-job / plan-pass lines);
  AXES.log a complete local run's log (the per-job `label|OK|..|NNNs` summary lines). A UNIT is the set of AXES words
  that must travel together: one word per job, except the declared GROUPS (jobs whose selection overlaps, so two
  shards would each run one -- tests/ci/cloud_axes_check.sh is the control that counts). Weight = the unit's jobs'
  local seconds x 2 (a 4-core runner is 4x slower, and run_axes pairs two jobs, so a job costs half a pair) +
  the arm passes; a job absent from the log gets the log's median, labelled. Shards are LPT-balanced.
  Table `unit<TAB>shard<TAB>weight_s<TAB>weight_source`, header `# shards=N`, `# baseline_s=`.
san: tests/lib/san_scripts.txt scripts, weighted by PROXY (the CI-measured `make test` section the script
  belongs to, split over that section's scripts; labelled), LPT-balanced. Table `script shard weight_s source`.
mech: the sabotage rows of tests/mech/sabotages/ (a UNIT is one S-id as the driver's id arguments spell it, the part of the
  file name before the first `_`), weighted by the measured per-row seconds a mech shard records (MECH_TIMES_OUT, via
  tests/ci/cloud_mech_shard.sh); a row with no measurement takes the median measured row, or MECH_DEFAULT_S if none is
  measured, labelled ESTIMATE. LPT-balanced. Table `sabotage shard weight_s source`.
"""
import argparse
import os
import re
import statistics
import subprocess
import sys

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(os.path.dirname(here))

GROUPS = [("--engine", "-fno-start-set"), ("-fno-start-width", "-fno-start-landing")]
PAIR_SCALE = 2.0     # 4-core runner (x4) shared by a pair (/2): a job costs 2x its local paired seconds
BASELINE_S = 772     # the baseline run, once per shard: 193 s on 16 cores x 4 (a measured `@baseline` replaces it)
PAIR_DIV = 2         # measured: run_axes runs two jobs at once, so a job's logged seconds cost the shard half


def read_measured(paths):
    """unit -> mean median_s over the files; unit -> basis ('apportioned' if any file says so); '@' rows included."""
    sec, basis = {}, {}
    for p in paths:
        for line in open(p):
            c = line.rstrip("\n").split("\t")
            if line.startswith("#") or len(c) < 6 or c[0] == "unit":
                continue
            sec.setdefault(c[0], []).append(float(c[1]))
            if c[5] != "measured":
                basis[c[0]] = c[5]
            else:
                basis.setdefault(c[0], "measured")
    return {k: sum(v) / len(v) for k, v in sec.items()}, basis


def word_of(label, flags):
    if "memfn arm" in label:
        return next(t for t in flags.split() if t.startswith("--memfn="))
    if flags.startswith("--engine=") and "-fno-start-set" not in flags:
        return "--engine"
    if "--engine=vm" in flags and "-fno-start-set" in flags:
        return "-fno-start-set"
    if flags == "-fno-start-width -fno-start-landing":
        return "-fno-start-width"
    if flags.startswith("--tune="):
        return "--tune"
    if "--analysis=" in flags:
        return next(t for t in flags.split() if t.startswith("--analysis="))
    return flags


def lpt(items, n):
    tot = [0.0] * n
    for it in sorted(items, key=lambda r: -r[1]):
        k = tot.index(min(tot))
        it[2] = k + 1
        tot[k] += it[1]
    return tot


def plan_axes(a):
    times, meas = {}, {}
    if a.log:
        for line in open(a.log, encoding="utf-8", errors="replace"):
            f = line.rstrip("\n").split("|")
            if len(f) >= 4 and re.fullmatch(r"\d+s", f[-1]):
                times[f[0].strip()] = int(f[-1][:-1])
    mbasis = {}
    if a.measured:
        meas, mbasis = read_measured(a.measured)
    global BASELINE_S
    if "@baseline" in meas:
        BASELINE_S = round(meas["@baseline"])
    if not times and not [k for k in meas if not k.startswith("@")]:
        sys.exit("cloud_units_plan: axes needs --log or a --measured file with job rows")
    # a job with no measurement takes the median job, in the weight's own unit (shard seconds): the log's local seconds
    # x PAIR_SCALE, or the measured runner seconds / PAIR_DIV
    med = statistics.median(times.values()) * PAIR_SCALE if times else statistics.median(
        v / PAIR_DIV for k, v in meas.items() if not k.startswith("@"))
    units = {}   # word -> [weight, source-notes]
    n_def = 0
    for line in open(a.plan):
        f = line.rstrip("\n").split("\t")
        if f[0] == "plan-job":
            w = word_of(f[1], f[2])
            u = units.setdefault(w, [0.0, set()])
            if f[1] in meas:     # runner seconds of a paired job; the shard pays half
                u[0] += meas[f[1]] / PAIR_DIV; u[1].add(mbasis.get(f[1], "measured"))
                continue
            t = times.get(f[1])
            note = "log"
            if t is None:
                u[0] += med; u[1].add("ESTIMATE-median-default"); n_def += 1
                continue
            u[0] += t * PAIR_SCALE; u[1].add("ESTIMATE-" + note)
        elif f[0] == "plan-pass" and f[1] == "-futf-check arm":
            u = units.setdefault("-futf-check", [0.0, set()])
            u[0] += med * PAIR_SCALE; u[1].add("median-default(pass)")
    for g in GROUPS:   # merge a group's words into one unit named by the words joined
        have = [w for w in g if w in units]
        if len(have) > 1:
            merged = [sum(units[w][0] for w in have), set().union(*[units[w][1] for w in have])]
            for w in have:
                del units[w]
            units[" ".join(have)] = merged
    items = [[w, u[0], 0, ("runner " if u[1] <= {"measured"} else "") + "+".join(sorted(u[1]))
              + ("" if u[1] <= {"measured"} else " (local x%g where ESTIMATE)" % PAIR_SCALE)] for w, u in units.items()]
    tot = lpt(items, a.shards)
    return items, tot, ["%d job(s) with no measurement took the median %gs (shard seconds)" % (n_def, med)] if n_def else []


def plan_san(a):
    # PROXY: CI-measured `make test` section seconds (tests/ci/cloud_test_shards.tsv) per script; a section with
    # several scripts is split evenly; a script with no section is the default and says so.
    sect = {}
    for line in open(os.path.join(here, "cloud_test_shards.tsv")):
        f = line.rstrip("\n").split("\t")
        if len(f) >= 3 and f[0].startswith("test-"):
            sect[f[0]] = float(f[2])
    owner = {
        "tests/harness/run.sh": "test-corpus", "tests/cli/run_cli_tests.sh": "test-cli",
        "tests/reject/run_reject_tests.sh": "test-reject", "tests/registry/run_registry_tests.sh": "test-registry",
        "tests/parse/run_parse_tests.sh": "test-parse", "tests/codegen/run_codegen_tests.sh": "test-codegen",
        "tests/vm/run_vm_tests.sh": "test-vm", "tests/mrl/run_mrl_tests.sh": "test-mrl",
        "tests/encseam/run_encseam_tests.sh": "test-encseam", "tests/possessify/run_possdiff.sh": "test-possessify",
        "tests/possessify/run_possessify_tests.sh": "test-possessify", "tests/rungselect/run_rungdiff.sh": "test-rungselect",
        "tests/rungselect/run_rungselect_tests.sh": "test-rungselect", "tests/altcls/run_altdiff.sh": "test-altcls",
        "tests/altcls/run_altcls_tests.sh": "test-altcls", "tests/assertions/run_assertions_tests.sh": "test-assertions",
        "tests/assertions/run_gstart_diff.sh": "test-assertions", "tests/assertions/run_kreset_diff.sh": "test-assertions",
        "tests/assertions/run_mline_diff.sh": "test-assertions", "tests/atomic_groups/run_atomic_diff.sh": "test-atomic",
        "tests/backrefs/run_backref_diff.sh": "test-backrefs", "tests/backrefs/run_dupnames_diff.sh": "test-backrefs",
        "tests/lookaround/run_lookaround_diff.sh": "test-lookaround", "tests/lookaround/run_expansion_diff.sh": "test-lookaround",
        "tests/recursion/run_recursion_diff.sh": "test-recursion", "tests/anchored/run_anchored_diff.sh": "test-anchored-match",
        "tests/anchored/run_anchored_dead_entry.sh": "test-anchored-match", "tests/utf8/run_startbnd_diff.sh": "test-startbnd",
        "tests/lib/run_gen_timeout_tests.sh": "test-gentimeout", "tests/known_fail/run_known_fail.sh": "test-known-fail",
        "tests/core/run_core_tests.sh": "test-core", "tests/vars/run_vars_tests.sh": "test-vars",
        "tests/findall/run_iter_diff.sh": "test-findall", "tests/callouts/run_callouts_tests.sh": "test-callouts",
        "tests/code/run_code_tests.sh": "test-code", "tests/codegen/run_cpset_structure.sh": "test-cpset-structure",
    }
    scripts = [l.strip() for l in open(os.path.join(root, "tests/lib/san_scripts.txt"))
               if l.strip() and not l.lstrip().startswith("#")]
    share = {}
    for s in scripts:
        share[owner.get(s)] = share.get(owner.get(s), 0) + 1
    default = 30.0
    items, n_def = [], 0
    meas, mbasis = read_measured(a.measured) if a.measured else ({}, {})
    for s in scripts:
        sec = owner.get(s)
        if s in meas:
            items.append([s, meas[s], 0, "runner %s" % mbasis[s]])
        elif sec and sec in sect:
            items.append([s, sect[sec] / share[sec], 0, "ESTIMATE proxy: %s %gs / %d script(s)" % (sec, sect[sec], share[sec])])
        else:
            items.append([s, default, 0, "ESTIMATE unmeasured default %gs" % default]); n_def += 1
    tot = lpt(items, a.shards)
    return items, tot, ["%d script(s) have no proxy and carry the default %gs" % (n_def, default)] if n_def else []


MECH_DEFAULT_S = 45.0   # UNMEASURED: the local battery's 7 h 6 min at PROCS=6 over 1225 rows, per row, scaled to a 4-core runner at 2 rows at once
# A mech shard runs MECH_CONC rows at once (cloud_mech_shard.sh: PROCS = cores/2), so a row's recorded wall is ~MECH_CONC
# shard-seconds' worth of the shard's wall: run 43108213213, 17 finished shards: sum(row seconds)/shard wall = 1.76-1.95.
MECH_CONC = 2.0


def plan_mech(a):
    ids = sorted({os.path.basename(f).rsplit(".", 1)[0].split("_")[0]
                  for f in os.listdir(os.path.join(root, "tests/mech/sabotages")) if f.startswith("S") and f.endswith(".sh")})
    meas, mbasis = read_measured(a.measured) if a.measured else ({}, {})
    vals = [v for k, v in meas.items() if k in ids]
    # the MEAN, not the median: the row times are heavy-tailed (median 92 s, mean ~290 s in run 43108213213), so a median
    # default under-weights every unmeasured row (the failed shards' rows) by 3x and the unmeasured shards run long
    dflt = statistics.mean(vals) / MECH_CONC if vals else MECH_DEFAULT_S
    items = [[i, meas[i] / MECH_CONC, 0, "runner %s" % mbasis[i]] if i in meas else
             [i, dflt, 0, "ESTIMATE %s %gs" % ("mean measured row" if vals else "unmeasured default", dflt)] for i in ids]
    tot = lpt(items, a.shards)
    n_def = sum(1 for i in items if "ESTIMATE" in i[3])
    return items, tot, ["%d row(s) have no measurement and carry %gs" % (n_def, dflt)] if n_def else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["axes", "san", "mech"])
    ap.add_argument("--plan"); ap.add_argument("--log")
    ap.add_argument("--shards", type=int)
    ap.add_argument("--slots", type=int, help="max shards (the kind's max_parallel); picks the smallest count near the best")
    ap.add_argument("--measured", nargs="*", default=[], help="committed measured files (tests/ci/measured_KIND.tsv)")
    ap.add_argument("--setup", type=float, default=70, help="per-shard setup seconds (cloud_kinds.tsv setup_s)")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    if a.mode == "axes" and not (a.log or a.measured):
        sys.exit("cloud_units_plan: axes needs --log or --measured")
    if a.mode == "axes" and not a.plan:    # the unsplit job list, from the sweep itself (needs build/pcrec)
        r = subprocess.run(["bash", os.path.join(root, "tests/axes/run_axes.sh")], capture_output=True, text=True,
                           env=dict(os.environ, AXES_PLAN="1", AXES_FULL="1"))
        a.plan = os.path.join(os.environ.get("TMPDIR") or "/var/tmp", "cloud_units_plan.%d.txt" % os.getpid())
        open(a.plan, "w").write(r.stdout)
        if "plan-job" not in r.stdout:
            sys.exit("cloud_units_plan: run_axes.sh listed no jobs (is build/pcrec built? `make`): " + r.stderr[-200:])
    plan = {"axes": plan_axes, "san": plan_san, "mech": plan_mech}[a.mode]
    if a.shards:
        a.shards = a.shards
        items, tot, notes = plan(a)
    else:    # smallest shard count within 5 % of the best the largest unit and the total allow
        a.shards = a.slots or (12 if a.mode == "san" else 20)
        items, tot, notes = plan(a)
        best = max(max(i[1] for i in items), sum(i[1] for i in items) / a.shards)
        n = a.shards
        while n > 1:
            a.shards = n - 1
            items2, tot2, notes2 = plan(a)
            if max(tot2) > best * 1.05:
                break
            n -= 1
            items, tot, notes = items2, tot2, notes2
        a.shards = n
    base = BASELINE_S if a.mode == "axes" else 0
    big1 = max(items, key=lambda i: i[1])
    big = sorted(((i[1], i[0]) for i in items), reverse=True)[:3]
    head = ["# tests/ci/cloud_%s_shards.tsv -- the cloud %s kinds' shard table ([CLOUD-SUITE] C), GENERATED by"
            % (a.mode, {"axes": "axes", "san": "ubsan/asan", "mech": "mech"}[a.mode]),
            "# tests/ci/cloud_units_plan.py %s; weights are shard seconds on a 4-core runner: MEASURED where weight_source says runner, ESTIMATE otherwise." % a.mode,
            "# estimate: shards=%d, per-shard work min %.0fs max %.0fs%s; largest units: %s"
            % (a.shards, min(tot), max(tot), (" + baseline %ds per shard" % base) if base else "",
               "; ".join("%s %.0fs" % (n, w) for w, n in big))]
    head += ["# note: " + n for n in notes]
    est = [i[0] for i in items if "ESTIMATE" in i[3]]
    head += ["# predicted_shard_s=%d" % round(max(tot) + base),
             "# predicted_wall_s=%d" % round(max(tot) + base + a.setup),
             "# indivisible_floor_s=%d (setup %.0fs%s + largest unit %s %.0fs)" % (
                 round(a.setup + base + big1[1]), a.setup, (" + baseline %ds" % base) if base else "", big1[0], big1[1]),
             "# unmeasured: %d unit(s) keep an ESTIMATE%s" % (len(est), ": " + "; ".join(est[:6]) + ("; .." if len(est) > 6 else "") if est else "")]
    heads = None
    head += ["# shards=%d" % a.shards]
    if base:
        head += ["# baseline_s=%d" % base]
    head += ["%s\tshard\tweight_s\tweight_source" % {"axes": "unit", "san": "script", "mech": "sabotage"}[a.mode]]
    rows = ["%s\t%d\t%g\t%s" % (i[0], i[2], round(i[1], 1), i[3]) for i in sorted(items, key=lambda r: (r[2], r[0]))]
    text = "\n".join(head + rows) + "\n"
    out = os.path.join(here, "cloud_%s_shards.tsv" % a.mode)
    print("indivisible floor %.0fs (setup %.0fs + baseline %ds + largest unit %s %.0fs); predicted slowest shard %.0fs, wall %.0fs; %d unmeasured unit(s)"
          % (a.setup + base + big1[1], a.setup, base, big1[0], big1[1], max(tot) + base, max(tot) + base + a.setup, len(est)), file=sys.stderr)
    for k, t in enumerate(tot, 1):
        print("shard %d/%d work %.0fs (%.1f min)%s" % (k, a.shards, t, t / 60,
              (" + baseline = %.1f min" % ((t + base) / 60)) if base else ""), file=sys.stderr)
    for n in notes:
        print("note: " + n, file=sys.stderr)
    if a.write:
        open(out, "w").write(text); print("wrote " + out, file=sys.stderr)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
