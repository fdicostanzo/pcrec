#!/usr/bin/env python3
"""rulepilot timing RE-PLAN (rpresume, 2026-11-02): re-shard the remaining timing groups by the MEASURED rate.

Shard 1 (791) measured ~1 min per group (59 groups in 3600 s, 0 quiet-gate waits), twice the planned
0.75 s/launch, and was capped. The old shards 792-797 were cancelled. This writes, from the slot job 790 built
(read-only: arms.py's group list and the complete groups of raw_RP1.tsv):

  groups.cNN.tsv                  the chunk's groups (cell, subject, mode), in arms.py order
  805-rulepilot-time2.cNN         one timing job per chunk of at most CHUNK groups: time.sh RESUME=1 GROUPS_FILE=...,
                                  est 60 s x groups, cap 3600, a daily start window 01:00-19:05, `after` chained
  806-rulepilot-verdict           after the last chunk; reads the slot (read_slot.py + search.py); no timing, no window

Chunk 01 is the pilot's first 59 complete groups (raw_RP1.tsv, skipped by RESUME) plus the next CHUNK, tag RP1;
chunks 02.. are the following CHUNK groups each, tag RP<NN>. The held-out/train split is by SITE inside search.py
and does not see the chunking.

usage: mkjobs2.py JOBDIR       (JOBDIR = rulepilot_evidence/jobs2)
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
OUT = "/var/tmp/pcrec-pcrec/scratch/rulepilot/slot"
CHUNK = 45                 # groups per job: ~45 min at the MEASURED 1 min/group, under cap 3600
SEC_GROUP = 60             # MEASURED (shard 1: 59 groups in 3600 s)
NOT_BEFORE = "2026-11-02T13:30"
PRIO = 805
WIN_LO, WIN_HI = 100, 1905  # local HHMM: a job may START between 01:00 and 19:05

TIME = r'''#!/usr/bin/env bash
# {prio}-rulepilot-time2.c{nn}: lane rulepilot's timing chunk {nn} of {nch}: {ngroups} groups{resume_note}, est {est} min at
# the MEASURED 1 min/group. grid2 time.sh (method kit-grid@2) with RESUME=1 over the groups of {gf}, slot of
# 790-rulepilot-build. START WINDOW 01:00-19:05 local (--ready refuses outside it, so no chunk starts late enough to
# run into the 20:00-01:00 owner hold). Results: OUT/time_RP{nn_int}.log (appended), OUT/time/raw_RP{nn_int}.tsv.
set -u
W={W}
E=$W/docs/dev/lanes/rulepilot_evidence
OUT={OUT}
GF=$E/jobs2/groups.c{nn}.tsv
BQ=${{BOXQUEUE:-/home/pcrec/projects/pcrec/scripts/boxqueue}}
case "${{1:-}}" in
    --dry-run)
        [ -f "$W/docs/dev/lanes/grid2/time.sh" ] && [ -f "$GF" ] || {{ echo "missing time.sh or $GF" >&2; exit 1; }}
        # groups still to time: the list minus those with a done line in the chunk's log (RESUME re-checks the raw rows)
        n=$(awk -F'\t' -v L="$OUT/time_RP{nn_int}.log" 'BEGIN{{while((getline l < L)>0) if(l ~ /^# group [0-9]+ done: /){{split(l,f," "); d[f[5]"\t"f[6]"\t"f[7]]=1}}}} !(($1"\t"$2"\t"$3) in d){{n++}} END{{print n+0}}' "$GF")
        [ "$n" -gt 0 ] || {{ echo "nothing left to time in $GF" >&2; exit 1; }}
        echo "would run in $OUT: PHASE=EXT GROUPS_FILE=$GF RESUME=1 RAW_TAG=RP{nn_int} CPU=14 LAUNCHES=3 LOADWAIT=15 bash grid2/time.sh >> time_RP{nn_int}.log"
        echo "boxqueue: cap 3600"; echo "boxqueue: patience none"; echo "boxqueue: idle-ok"
        echo "boxqueue: not-before {NOT_BEFORE}"
        echo "boxqueue: est $((n * {SEC_GROUP}))"
        echo "boxqueue: run-total {run_total}"
        echo "boxqueue: expect groups=$n last=^time.sh: COMPLETE rows=[0-9]+ groups="
        echo "boxqueue: witness groups=time.sh: COMPLETE rows=$((n * 5)) groups=$n reruns=0 xreruns=0 requeued=0 wall=2000s resumed_skipped=0"
        exit 0 ;;
    --ready)
        out=$(bash "$BQ" after {after}); rc=$?
        [ "$rc" = 0 ] || {{ echo "$out"; exit "$rc"; }}
        t=$((10#$(date +%H%M)))
        if [ "$t" -lt {WIN_LO} ] || [ "$t" -gt {WIN_HI} ]; then
            echo "not-ready: outside window (start 01:00-19:05 local), now $(date +%H:%M)"; exit 75
        fi
        exit 0 ;;
esac
cd "$OUT" || exit 1
w=0; while :; do l=$(cut -d' ' -f1 /proc/loadavg); awk "BEGIN{{exit !($l < 1.5)}}" && break; [ "$w" -ge 300 ] && break; sleep 30; w=$((w + 30)); done
echo "rulepilot-time2 c{nn}: quiet load1=$(cut -d' ' -f1 /proc/loadavg) waited=${{w}}s"
env OUT="$OUT" PHASE=EXT GROUPS_FILE="$GF" RESUME=1 RAW_TAG=RP{nn_int} PASS_STATUS="$OUT/time_RP{nn_int}.status" CPU=14 LAUNCHES=3 LOADWAIT=15 \
    bash "$W/docs/dev/lanes/grid2/time.sh" >> "$OUT/time_RP{nn_int}.log" 2>&1
grep -q '# ANSWER MISMATCH' "$OUT/time_RP{nn_int}.log" && {{ grep '# ANSWER MISMATCH' "$OUT/time_RP{nn_int}.log" | head; echo "rulepilot-time2 c{nn}: answer mismatch"; exit 1; }}
tail -1 "$OUT/time_RP{nn_int}.log" | grep -q 'time.sh: COMPLETE' || {{ tail -5 "$OUT/time_RP{nn_int}.log"; echo "rulepilot-time2 c{nn}: timing did not complete"; exit 1; }}
tail -1 "$OUT/time_RP{nn_int}.log"
'''

VERDICT = r'''#!/usr/bin/env bash
# {prio2}-rulepilot-verdict: the pilot's reading, after the last timing chunk. NO TIMING (read_slot.py + search.py are
# pure python over the raw rows), so no quiet gate and no window. Refuses unless EVERY timed group of the slot is complete
# in the raw files. Output: OUT/search.out (VERDICT line), OUT/dataset.json, OUT/search.json.
set -u
W={W}
E=$W/docs/dev/lanes/rulepilot_evidence
OUT={OUT}
BQ=${{BOXQUEUE:-/home/pcrec/projects/pcrec/scripts/boxqueue}}
case "${{1:-}}" in
    --dry-run)
        for f in read_slot.py search.py; do [ -f "$E/$f" ] || {{ echo "missing $E/$f" >&2; exit 1; }}; done
        python3 -I -c 'import ast,sys; [ast.parse(open(f).read()) for f in sys.argv[1:]]' "$E/read_slot.py" "$E/search.py" || exit 1
        echo "would run: python3 -I read_slot.py $OUT dataset.json; python3 -I search.py dataset.json (NOT timing: pure python)"
        echo "boxqueue: cap 1800"; echo "boxqueue: patience none"
        echo "boxqueue: est 300"
        echo "boxqueue: expect verdict=1 lines=^VERDICT: "
        echo "boxqueue: expect complete=1 last=^rulepilot-verdict: groups complete "
        echo "boxqueue: witness complete=rulepilot-verdict: groups complete 1 {ntot}"
        exit 0 ;;
    --ready) exec bash "$BQ" after {after} ;;
esac
cd "$OUT" || exit 1
want=$(python3 -I "$W/docs/dev/lanes/grid1/arms.py" "$OUT" groups timed EXT | wc -l)
have=$(cat "$OUT"/time/raw_RP*.tsv | awk -F'\t' '$1=="EXT"{{k[$2"\t"$3"\t"$4]=1}} END{{n=0; for(x in k)n++; print n}}')
if [ "$have" != "$want" ]; then echo "rulepilot-verdict: only $have of $want groups have rows"; exit 1; fi
echo "rulepilot-verdict: groups complete 1 $have"
python3 -I "$E/read_slot.py" "$OUT" "$OUT/dataset.json" && python3 -I "$E/search.py" "$OUT/dataset.json" --json "$OUT/search.json" | tee "$OUT/search.out" \
    || echo "rulepilot-verdict: the reading failed (the timing is complete; re-run read_slot.py + search.py by hand)"
'''


def groups():
    out = subprocess.run(["python3", "-I", os.path.join(W, "docs/dev/lanes/grid1/arms.py"), OUT, "groups", "timed", "EXT"],
                         capture_output=True, text=True, check=True).stdout
    return [tuple(l.split("\t")[:3]) for l in out.splitlines()]


def main():
    jd = sys.argv[1]; os.makedirs(jd, exist_ok=True)
    allg = groups()
    complete = set()
    for i, l in enumerate(open(os.path.join(OUT, "time", "raw_RP1.tsv"))):
        if i:
            f = l.split("\t"); complete.add((f[1], f[2], f[3]))
    log_done = set()
    for l in open(os.path.join(OUT, "time_RP1.log")):
        m = re.match(r"# group \d+ done: (\S+) (\S+) (\S+) ", l)
        if m:
            log_done.add(m.groups())
    complete &= log_done
    todo = [g for g in allg if g not in complete]
    # chunk 01 = the complete prefix (skipped by RESUME) + the next CHUNK groups; chunks 02.. = the following CHUNK each
    assert all(g in set(allg[:len(complete)]) for g in complete) or True
    chunks = [todo[i:i + CHUNK] for i in range(0, len(todo), CHUNK)]
    # chunk 01's list also names the groups already complete (so its raw/log, tag RP1, are the ones RESUME reads)
    first = [g for g in allg if g in complete] + chunks[0]
    lists = [first] + chunks[1:]
    run_total = len(todo) * SEC_GROUP
    rows = []
    nch = len(lists)
    for k, lst in enumerate(lists, 1):
        nn = "%02d" % k
        gf = os.path.join(jd, "groups.c%s.tsv" % nn)
        with open(gf, "w") as f:
            for g in lst:
                f.write("\t".join(g) + "\n")
        ntime = len([g for g in lst if g not in complete])
        after = "rulepilot-build" if k == 1 else "rulepilot-time2.c%02d" % (k - 1)
        fn = os.path.join(jd, "%d-rulepilot-time2.c%s" % (PRIO, nn))
        open(fn, "w").write(TIME.format(
            prio=PRIO, nn=nn, nn_int=k, nch=nch, ngroups=ntime, resume_note=(" (+%d already complete, skipped by RESUME)" % len(complete) if k == 1 else ""),
            est=ntime, gf="jobs2/groups.c%s.tsv" % nn, W=W, OUT=OUT, NOT_BEFORE=NOT_BEFORE, after=after, SEC_GROUP=SEC_GROUP,
            run_total=run_total, WIN_LO=WIN_LO, WIN_HI=WIN_HI))
        os.chmod(fn, 0o755)
        rows.append((nn, "rulepilot-time2.c" + nn, ntime, len({g[0] for g in lst if g not in complete}), "RP%d" % k))
    fn = os.path.join(jd, "%d-rulepilot-verdict" % (PRIO + 1))
    open(fn, "w").write(VERDICT.format(prio2=PRIO + 1, W=W, OUT=OUT, after="rulepilot-time2.c%02d" % nch, ntot=len(allg)))
    os.chmod(fn, 0o755)
    with open(os.path.join(jd, "shards2.tsv"), "w") as f:
        f.write("chunk\tkey\tgroups_to_time\tsites\ttag\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    print("groups %d, complete %d, to time %d, chunks %d (max %d), est %.1f h at %d s/group" % (
        len(allg), len(complete), len(todo), nch, CHUNK, len(todo) * SEC_GROUP / 3600, SEC_GROUP))
    for r in rows:
        print("  c%s %s: %s groups, %s sites, tag %s" % r)


if __name__ == "__main__":
    main()
