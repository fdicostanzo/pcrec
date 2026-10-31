#!/usr/bin/env python3
"""rulepilot step 4: plan the timing job's shards and write the boxqueue job scripts.

Per site the launch count is DERIVED, not measured: groups g = 3 miss lengths + 3 dense lengths
(dense only where the question's py_count_full > 0, the predictor available before the build),
launches = g x (arms + 3 base copies) x (3 launches + 0.2 x 2 rerun share), grid2 time.sh's own
estimate rule. SEC = 0.75 s per launch (grid2's MEASURED 0.61-0.65 s per streamed 4 MiB launch,
raised for the 16 MiB 1 MiB-point subjects: an UNMEASURED margin). Sites are packed in census
order into shards of at most BUDGET seconds of estimated wall, so every job's cap stays at 3600 s.

usage: mkjobs.py JOBDIR       writes JOBDIR/780-rulepilot-build, 781..-rulepilot-time.sN, the
                              last one 7NN-rulepilot-time, and ../shards.tsv
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
SEC, BUDGET, LAUNCH = 0.75, 2400, 3 + 0.2 * 2
OUT = "/var/tmp/pcrec-pcrec/scratch/rulepilot/slot"
NOT_BEFORE = "2026-11-02T05:00"

BUILD = r'''#!/usr/bin/env bash
# 780-rulepilot-build: lane rulepilot's timing slot, BUILD + correctness gate (no clock).
# Re-emits every forceable default-route arm of the {nsites} inventory sites with the lane's compiler
# (byte identity against the committed inventory), links grid1's gdrv.c, writes the streamed subjects
# (gen_subj.py: 3 lengths x miss/dense from each question's own corpus file), then grid1's check.sh
# (legs R and C against each site's default arm; SKIP_DEEP: no own cells). Writes ONLY under OUT
# (~{gib:.0f} GiB of subjects). Spec: docs/design/pricing_rulepilot.md; report: docs/dev/lanes/rulepilot_report.md.
set -u
W={W}
E=$W/docs/dev/lanes/rulepilot_evidence
OUT={OUT}
case "${{1:-}}" in
    --dry-run)
        for f in slot_build.py gen_subj.py inventory/census.jsonl inventory/facts.tsv; do [ -f "$E/$f" ] || {{ echo "missing $E/$f" >&2; exit 1; }}; done
        for f in grid1/gdrv.c grid1/gchk.c grid1/arms.py grid1/check.sh grid2/streamgen.py; do [ -f "$W/docs/dev/lanes/$f" ] || {{ echo "missing $f" >&2; exit 1; }}; done
        [ -x "$W/build/pcrec" ] || {{ echo "no compiler $W/build/pcrec" >&2; exit 1; }}
        want=$(cat "$E/inventory/pcrec.sha256"); have=$(sha256sum "$W/build/pcrec" | cut -d' ' -f1)
        [ "$want" = "$have" ] || {{ echo "compiler moved: $have, inventory was built with $want" >&2; exit 1; }}
        python3 -I -c 'import ast,sys; [ast.parse(open(f).read()) for f in sys.argv[1:]]' "$E/slot_build.py" "$E/gen_subj.py" || exit 1
        echo "would run: python3 -I $E/slot_build.py $OUT --jobs 4; OUT=$OUT SKIP_DEEP=1 bash grid1/check.sh"
        echo "boxqueue: cap 2400"; echo "boxqueue: patience none"
        echo "boxqueue: not-before {NOT_BEFORE}"
        echo "boxqueue: expect sites={nsites} last=^rulepilot-build: COMPLETE sites="
        echo "boxqueue: witness sites=rulepilot-build: COMPLETE sites={nsites} arms={narms} excluded=0"
        exit 0 ;;
    --ready) exit 0 ;;
esac
echo "rulepilot-build: start $(date -Is) load1=$(cut -d' ' -f1 /proc/loadavg)"
mkdir -p "$OUT"
taskset -c 12-15 nice python3 -I "$E/slot_build.py" "$OUT" --jobs 4 || {{ echo "rulepilot-build: slot_build FAILED"; exit 1; }}
OUT=$OUT SKIP_DEEP=1 CPUS=12-15 JOBS=4 bash "$W/docs/dev/lanes/grid1/check.sh" > "$OUT/check.out" 2>&1; rc=$?
tail -8 "$OUT/check.out"
# an excluded arm (answers differ from the default's) is a FINDING, never timed; the build still completes
nex=$(wc -l < "$OUT/excluded" 2>/dev/null || echo 0)
grep -q '^check: done' "$OUT/check.out" || {{ echo "rulepilot-build: the gate did not finish (rc=$rc)"; exit 1; }}
du -sh "$OUT" | cut -f1 | sed 's/^/rulepilot-build: slot size /'
echo "rulepilot-build: COMPLETE sites=$(ls "$OUT/bin" | wc -l) arms=$(ls -d "$OUT"/bin/*/* | wc -l) excluded=$nex"
'''

TIME = r'''#!/usr/bin/env bash
# {prio}-rulepilot-{rest}: lane rulepilot's timing shard {shard} of {nshards} ({nsites} sites, {ngroups} groups,
# estimated {est:.0f} min at {SEC} s per launch). grid2 time.sh (method kit-grid@2: CPU 14, 3 launches, the
# base launched three times, the rerun rule, the per-group quiet gate) over the shard's cells of the slot
# 780-rulepilot-build made. QUIET-GATED, so idle-ok. Results: OUT/time_RP{shard}.log, OUT/time/raw_RP{shard}.tsv.{last_note}
set -u
W={W}
E=$W/docs/dev/lanes/rulepilot_evidence
OUT={OUT}
RE='{regex}'
BQ=${{BOXQUEUE:-/home/pcrec/projects/pcrec/scripts/boxqueue}}
case "${{1:-}}" in
    --dry-run)
        [ -f "$W/docs/dev/lanes/grid2/time.sh" ] && [ -f "$E/read_slot.py" ] && [ -f "$E/search.py" ] || {{ echo "missing scripts" >&2; exit 1; }}
        n={ngroups}
        if [ -f "$OUT/ext/rp/arms.tsv" ]; then   # the slot exists (re-run at START): count the shard's real groups
            n=$(python3 -I "$W/docs/dev/lanes/grid1/arms.py" "$OUT" groups timed EXT | awk -F'\t' -v re="$RE" '$1 ~ re' | wc -l)
            [ "$n" -gt 0 ] || {{ echo "no groups for this shard in $OUT" >&2; exit 1; }}
        fi
        echo "would run in $OUT: PHASE=EXT CELLS_RE=$RE RAW_TAG=RP{shard} CPU=14 LAUNCHES=3 LOADWAIT=15 bash grid2/time.sh"
        echo "boxqueue: cap 3600"; echo "boxqueue: patience none"; echo "boxqueue: idle-ok"
        echo "boxqueue: not-before {NOT_BEFORE}"
        echo "boxqueue: expect groups=$n last=^time.sh: COMPLETE rows=[0-9]+ groups="
        echo "boxqueue: witness groups=time.sh: COMPLETE rows=$((n * 5)) groups=$n reruns=0 xreruns=0 requeued=0 wall=2000s"
        exit 0 ;;
    --ready) exec bash "$BQ" after {after} ;;
esac
cd "$OUT" || exit 1
w=0; while :; do l=$(cut -d' ' -f1 /proc/loadavg); awk "BEGIN{{exit !($l < 1.5)}}" && break; [ "$w" -ge 600 ] && break; sleep 30; w=$((w + 30)); done
echo "rulepilot-time {shard}: quiet load1=$(cut -d' ' -f1 /proc/loadavg) waited=${{w}}s"
env OUT="$OUT" PHASE=EXT CELLS_RE="$RE" RAW_TAG=RP{shard} PASS_STATUS="$OUT/time_RP{shard}.status" CPU=14 LAUNCHES=3 LOADWAIT=15 \
    bash "$W/docs/dev/lanes/grid2/time.sh" > "$OUT/time_RP{shard}.log" 2>&1
grep -q '# ANSWER MISMATCH' "$OUT/time_RP{shard}.log" && {{ grep '# ANSWER MISMATCH' "$OUT/time_RP{shard}.log" | head; echo "rulepilot-time {shard}: answer mismatch"; exit 1; }}
tail -1 "$OUT/time_RP{shard}.log" | grep -q 'time.sh: COMPLETE' || {{ tail -5 "$OUT/time_RP{shard}.log"; echo "rulepilot-time {shard}: timing did not complete"; exit 1; }}
{reading}tail -1 "$OUT/time_RP{shard}.log"
'''

READING = r'''python3 -I "$E/read_slot.py" "$OUT" "$OUT/dataset.json" && python3 -I "$E/search.py" "$OUT/dataset.json" --json "$OUT/search.json" | tee "$OUT/search.out" \
    || echo "rulepilot-time: the reading failed (the timing above is complete; re-run read_slot.py + search.py by hand)"
'''

def main():
    jd = sys.argv[1]; os.makedirs(jd, exist_ok=True)
    pyc = {r["id"]: int(r["py_count_full"] or 0) for r in csv.DictReader(
        open(os.path.join(W, "docs/dev/lanes/rwquest/questions.tsv"), encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE)}
    sites = []
    for line in open(os.path.join(HERE, "inventory", "census.jsonl")):
        r = json.loads(line)
        if r["refused"] or len(r["arms"]) < 2:
            continue
        g = 3 + (3 if pyc.get(r["id"], 0) > 0 else 0)
        sites.append((r["id"], len(r["arms"]), g, g * (len(r["arms"]) + 3) * LAUNCH * SEC))
    shards, cur = [], []
    for s in sites:
        if cur and sum(x[3] for x in cur) + s[3] > BUDGET:
            shards.append(cur); cur = []
        cur.append(s)
    if cur:
        shards.append(cur)
    total = sum(s[3] for s in sites)
    narms = sum(s[1] for s in sites)
    open(os.path.join(jd, "780-rulepilot-build"), "w").write(BUILD.format(
        W=W, OUT=OUT, NOT_BEFORE=NOT_BEFORE, nsites=len(sites), narms=narms, gib=len(sites) * 0.05))
    rows = []
    for k, sh in enumerate(shards, 1):
        last = k == len(shards)
        rest = "time" if last else f"time.s{k}"
        prio = 780 + k
        after = "rulepilot-build" if k == 1 else f"rulepilot-time.s{k - 1}"
        regex = "^rp-(" + "|".join(s[0] for s in sh) + ")$"
        est = sum(s[3] for s in sh) / 60
        fn = os.path.join(jd, f"{prio}-rulepilot-{rest}")
        open(fn, "w").write(TIME.format(
            prio=prio, rest=rest, shard=k, nshards=len(shards), nsites=len(sh), ngroups=sum(s[2] for s in sh),
            est=est, SEC=SEC, W=W, OUT=OUT, regex=regex, NOT_BEFORE=NOT_BEFORE, after=after,
            last_note=("\n# The LAST shard: after timing, read_slot.py + search.py print the pilot's VERDICT "
                       "(OUT/search.out)." if last else ""),
            reading=READING if last else ""))
        os.chmod(fn, 0o755)
        rows.append((k, f"rulepilot-{rest}", len(sh), sum(s[2] for s in sh), f"{est:.1f}", ",".join(s[0] for s in sh)))
    os.chmod(os.path.join(jd, "780-rulepilot-build"), 0o755)
    with open(os.path.join(HERE, "shards.tsv"), "w") as f:
        f.write("shard\tkey\tsites\tgroups\test_min\tids\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    print(f"sites {len(sites)}, arms {narms}, groups {sum(s[2] for s in sites)}, shards {len(shards)}, "
          f"estimated wall {total / 3600:.2f} h at {SEC} s per launch (+ build and quiet-gate waits)")
    for r in rows:
        print("  shard %s %s: %s sites %s groups ~%s min" % r[:5])

if __name__ == "__main__":
    main()
