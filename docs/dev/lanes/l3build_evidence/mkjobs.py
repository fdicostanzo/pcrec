#!/usr/bin/env python3
"""Write lane l3build's box-queue job scripts (identity per remodel commit, trace, mech, make test)."""
import os
S = "/var/tmp/pcrec-pcrec/scratch/l3build"; J = S + "/jobs"
W = "/home/pcrec/projects/pcrec/worktrees/l3build"
EV1 = W + "/docs/dev/lanes/sae1_evidence"
COMMITS = [("rm2", "f52b6d6aa", "RM-2 (K's three states, D-7)"),
           ("rm3", "c921cf980", "RM-3 (one move emitter, D-8)"),
           ("rm5", "9bd570b16", "RM-5 (lb_max accessor)"),
           ("rm4", "f9c3c88b0", "RM-4 (pcrec_run_scan_index, D-6)"),
           ("cmp", "f15dc9876", "remodel 5 (rn_cmp, D-4)")]

IDENT = r'''#!/usr/bin/env bash
# NAME: span_arms L3 remodel identity gate for DESC at SHA: build the commit's tree (git archive)
# if absent, then emit_sweep every stream (.c streams, emit-ir, composition, dumps, facts) over the
# SUBJECT tree's corpus + bench_patterns.txt with the base cfa0c2b1a binary as reference; verdict
# ident_check.py against an EMPTY census (a remodel has no mover). emit_sweep's rc is not the verdict.
set -u
S=@S@; T=$S/trees; EV1=@EV1@; W=@W@
REF=$T/base/build/pcrec SUB=$T/TAG BIN=$T/TAG/build/pcrec OUT=$S/ident-TAG
case "${1:-}" in
    --dry-run)
        [ -x "$REF" ] && [ -f "$EV1/ident_check.py" ] && [ -f "$EV1/bench_patterns.txt" ] && [ -f "$S/empty_census.tsv" ] || { echo "missing input" >&2; exit 1; }
        git -C "$W" cat-file -e SHA^{commit} || { echo "no commit SHA" >&2; exit 1; }
        echo "would: build $SUB from git archive SHA; env -C $SUB python3 scripts/emit_sweep.py --ref-bin $REF --bin $BIN --no-self-check --patterns-file $EV1/bench_patterns.txt --out $OUT --movers-out $OUT/movers.tsv; ident_check.py"
        echo "boxqueue: cap 3600"; echo "boxqueue: est 1500"; echo "boxqueue: patience none"
        echo "boxqueue: expect ident=1 lines=^== ident_check COMPLETE: 0 unexplained"
        exit 0 ;;
    --ready) exit 0 ;;
esac
if [ ! -x "$BIN" ]; then
    rm -rf "$SUB"; mkdir -p "$SUB"
    git -C "$W" archive SHA | tar -x -C "$SUB" || { echo "archive failed"; exit 1; }
    make -C "$SUB" -j8 > "$S/TAG.build.log" 2>&1 || { echo "build failed"; tail -5 "$S/TAG.build.log"; exit 1; }
fi
mkdir -p "$OUT"
env -C "$SUB" python3 scripts/emit_sweep.py --ref-bin "$REF" --bin "$BIN" --no-self-check \
    --patterns-file "$EV1/bench_patterns.txt" --out "$OUT" --movers-out "$OUT/movers.tsv" > "$OUT/sweep.log" 2>&1
src=$?; echo "emit_sweep exit code $src"
grep -E 'VIOLATION|WITNESS FAILURE|ASYMMETRIC|population=|emit_sweep: DONE' "$OUT/sweep.log"
[ -f "$OUT/movers.tsv" ] || { echo "no movers.tsv"; exit 1; }
if grep -qE 'VIOLATION|WITNESS FAILURE' "$OUT/sweep.log"; then echo "emit_sweep floor/witness RED"; exit 1; fi
python3 -I "$EV1/ident_check.py" "$S/empty_census.tsv" "$SUB" "$REF" "$OUT/movers.tsv"
'''

TRACE = r'''#!/usr/bin/env bash
# NAME: span_arms L3 RM-4's trace-build gate: tests/memfn/run_pres_picks.sh (it builds its own
# -DPCREC_CAND_TRACE pcrec) over the RM-4 commit's tree f9c3c88b0 (exported here if absent).
set -u
S=@S@; SUB=$S/trees/rm4t; W=@W@
case "${1:-}" in
    --dry-run)
        git -C "$W" cat-file -e f9c3c88b0^{commit} || { echo "no commit" >&2; exit 1; }
        echo "would run: TMPDIR=$S/tmp bash $SUB/tests/memfn/run_pres_picks.sh $SUB"
        echo "boxqueue: cap 1800"; echo "boxqueue: est 400"; echo "boxqueue: patience none"
        echo "boxqueue: expect none reason=exec'd the check; its rc is the job's rc"
        exit 0 ;;
    --ready) exit 0 ;;
esac
if [ ! -f "$SUB/tests/memfn/run_pres_picks.sh" ]; then
    rm -rf "$SUB"; mkdir -p "$SUB"; git -C "$W" archive f9c3c88b0 | tar -x -C "$SUB" || exit 1
fi
mkdir -p "$S/tmp"
TMPDIR=$S/tmp exec bash "$SUB/tests/memfn/run_pres_picks.sh" "$SUB"
'''

MECH = r'''#!/usr/bin/env bash
# NAME: span_arms L3 remodel binding sabotages on lane/l3build's tip (@IDS@)
set -u
TREE=@W@ IDS="@IDS@"
case "${1:-}" in
    --dry-run)
        out=$(env -C "$TREE" VALIDATE_ONLY=1 bash tests/mech/run_sabotage_matrix.sh $IDS 2>&1) ||
            { printf '%s\n' "$out" | tail -3 >&2; exit 1; }
        n=$(printf '%s\n' "$out" | sed -n 's/^== mech FIELD VALIDATION COMPLETE: \([0-9]*\) def.*/\1/p')
        [ -n "$n" ] || { echo "no field-validation line" >&2; exit 1; }
        echo "would run in $TREE: bash tests/mech/run_sabotage_matrix.sh $IDS"
        echo "boxqueue: cap 3600"; echo "boxqueue: patience none"; echo "boxqueue: est @EST@"
        echo "boxqueue: expect rows=$n last=^== mech run COMPLETE: "
        echo "boxqueue: witness rows=== mech run COMPLETE: $n rows (a sample of the line)"
        exit 0 ;;
    --ready) exit 0 ;;
esac
exec env -C "$TREE" bash tests/mech/run_sabotage_matrix.sh $IDS
'''

TEST = r'''#!/usr/bin/env bash
# NAME: full make test on worktrees/l3build (span_arms L3's five remodel commits)
set -u
TREE=@W@
case "${1:-}" in
    --dry-run)
        [ -d "$TREE" ] || { echo "no tree $TREE" >&2; exit 1; }
        echo "boxqueue: cap 5400"; echo "boxqueue: patience none"; echo "boxqueue: est 3000"
        echo "boxqueue: expect none reason=exec'd perfrun: the stage command's rc is the job's rc"
        echo "would run in $TREE: scripts/perfrun --label l3build -- \$BQ_LOG.make"; exit 0 ;;
    --ready) exit 0 ;;
esac
STAGE_NAME=test STAGE_LOG=$BQ_LOG CHAIN_DIR=$BQ_RUNDIR CHAIN_TREE=$TREE exec env -C "$TREE" bash -c 'scripts/perfrun --label l3build -- "$STAGE_LOG.make"'
'''


def put(name, text, **kw):
    for k, v in kw.items():
        text = text.replace(k, v)
    text = text.replace("@S@", S).replace("@EV1@", EV1).replace("@W@", W).replace("NAME", name)
    p = os.path.join(J, name)
    open(p, "w").write(text)
    os.chmod(p, 0o755)


os.makedirs(J, exist_ok=True)
for tag, sha, desc in COMMITS:
    put("l3build-ident-" + tag, IDENT, TAG=tag, SHA=sha, DESC=desc)
put("l3build-trace-rm4", TRACE)
put("l3build-mech-reaimed", MECH, **{"@IDS@": "S463 S467 S1957 S3075 S470 S809 S453 S474 S901", "@EST@": "1800"})
put("l3build-mech-bound", MECH, **{"@IDS@": "S476 S529 S811 S1707 S1712 S1711 S1955 S471 S813 S814 S1701 S280 S461 S1930", "@EST@": "2400"})
put("l3build-test", TEST)
