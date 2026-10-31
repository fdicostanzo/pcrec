# docs/dev/lanes/r30b2_jobs/common.sh -- shared by the r30b2 one-stage jobs (lane r30bfix,
# 2026-10-31): [MEMFN] R-30 re-validated on the merge of main 5c60e118c (abi 93 -> 94,
# provisional). Sourced by ABSOLUTE path (boxqueue runs a COPY of each job from its queue dir).
# The re-run plan is docs/dev/lanes/r30btri_report.md "Re-run plan"; README.md here lists the order.
TREE=/home/pcrec/projects/pcrec/worktrees/r30b
BASE=5c60e118c                       # main's tip merged into the lane (the census reference)
OUT=$TREE/build/r30b2
E=$TREE/docs/dev/lanes/r30b_evidence
BQ=/home/pcrec/projects/pcrec/scripts/boxqueue   # the MAIN tree's copy (boxqueue --help)
# The mech rows: every row on a file R-30 touches (tests/mech/rows_for.sh over the kit files and
# src/gen/memfn_sites.c on the merged tree), plus S278 (re-aimed), S449, S693 (the abi row) and the
# cli/main.c rows job 697 ran; job 697's 76 plus S526 (memfn.h, named by rows_for.sh on the merged
# tree). Split in two halves (job 697's 76 rows took 86 min). Half A leads with the six new plants,
# S278, S693, S449 and the re-planted S678.
IDS_A="S1543 S1544 S1545 S1546 S1547 S1548 S278 S693 S449 S678 S185 S265 S267 S279 S285 S443 S444 S445 S447 S450 S454 S455 S464 S570 S571 S573 S681 S682 S686 S687 S688 S689 S690 S691 S692 S694 S695 S724"
IDS_B="S728 S729 S730 S754 S793 S797 S800 S801 S802 S803 S804 S846 S847 S848 S921 S994 S1018 S1031 S1080 S1081 S1083 S1084 S1089 S1092 S1104 S1106 S1107 S1109 S1221 S1224 S1228 S1245 S1294 S1332 S1380 S1421 S1582 S1740 S526"
NIDS_A=38
NIDS_B=39

# The checks every job's --dry-run makes: the tree, BASE merged, abi 94, a clean tree (the two
# files the brief leaves dirty excluded), and the named make targets. No side effects.
r30b2_dry() {
    [ -e "$TREE/.git" ] || { echo "no tree $TREE" >&2; return 1; }
    git -C "$TREE" rev-parse --verify -q "$BASE^{commit}" >/dev/null || { echo "BASE $BASE unknown" >&2; return 1; }
    git -C "$TREE" merge-base --is-ancestor "$BASE" HEAD || { echo "BASE $BASE is not merged into the tip" >&2; return 1; }
    grep -q '^#define PCREC_ARTIFACT_ABI 94$' "$TREE/src/gen/emit_dfa.c" || { echo "tree is not at abi 94" >&2; return 1; }
    git -C "$TREE" diff --quiet HEAD -- . ':(exclude)docs/dev/artifact_size_log.tsv' ':(exclude)r30b_rulings.md' ||
        { echo "worktree dirty" >&2; return 1; }
    local t
    for t in "$@"; do
        grep -q "^$t:" "$TREE/Makefile" || { echo "no make target $t" >&2; return 1; }
    done
}

# --ready: 0 once every KEY is green; else the first not-green answer (75 wait, 77 never).
r30b2_after() {
    local k rc
    for k in "$@"; do
        "$BQ" after "$k" >/dev/null 2>&1
        rc=$?
        [ "$rc" -eq 0 ] && continue
        echo "waiting on $k (boxqueue after: $rc)"
        [ "$rc" -eq 77 ] && return 77
        return 75
    done
    return 0
}

# The work's preamble: cwd = the tree, TMPDIR under build/, and the tip must be the one job 1
# (kit-r30b2-build) built and recorded, so every stage judges the SAME commit.
r30b2_enter() {
    cd "$TREE" || exit 1
    export TMPDIR=$TREE/build/tmp
    mkdir -p "$TMPDIR" "$OUT"
    TIP=$(git rev-parse HEAD)
    if [ "${1:-}" != "--record" ]; then
        [ "$(cat "$OUT/TIP" 2>/dev/null)" = "$TIP" ] ||
            { echo "tip $TIP is not the one kit-r30b2-build recorded ($(cat "$OUT/TIP" 2>/dev/null || echo none))"; exit 1; }
    fi
    echo "== r30b2 tip $TIP vs $BASE"
}

# One named step: its log under $OUT, a digest of its verdict lines, and `== r30b2 step NAME
# rc=N` (the jobs' declared population counts the rc=0 lines). Returns the step's rc.
step() {
    local name=$1; shift
    echo "== r30b2 step $name start $(date +%T): $*"
    "$@" > "$OUT/$name.log" 2>&1
    local rc=$?
    grep -E 'strict:|== arm|UNEXPECTED|COMPLETE|DONE rc=|\*\*\* \[|checks (passed|failed)|ANOMALY|mech run COMPLETE|REACH|FAILED|lost|LOST|^FAIL' "$OUT/$name.log" | tail -40
    echo "== r30b2 step $name rc=$rc"
    return "$rc"
}
