#!/usr/bin/env bash
# tests/clskit/run_clskit_tests.sh — [CLS-TREE] S1: THE CLASS-MATCHER KIT
# (src/gen/clskit.c) held to a reference and to the study, before any emitter
# calls it (docs/design/cls_tree_design.md §6's S1 row; D129, D131).
#
# Nothing in the tree calls the kit yet, so no `.rxt` cell, identity gate or
# corpus answer can see it. This section is the only net, in three parts:
#
#   1. THE DIFFERENTIAL. Every set of four populations — the 312 `uprops`
#      sets, the K53 twelve, the 41 corpus byte classes, and the study's
#      proptest compositions (populations.py) — gets every kit form the
#      driver can build (K at four λ, six leaf-restricted sectionings, P3,
#      P2, B1, and the atom matcher for byte sets). The EMITTED C is compiled
#      under GENCFLAGS and every variant is compared against a reference the
#      kit did not write, on all 1,114,112 code points plus three beyond the
#      code space. The composition law `kit(A op B) == kit(A) op kit(B)` is
#      checked for K4 and P3 on every proptest case.
#   2. THE POPULATION COUNT (learnings.md §3, K35): every leaf form and every
#      whole-set form must have been EMITTED at least once, or a form nothing
#      reached would read as a form nothing broke.
#   3. THE CROSS-CHECK against the study (crosscheck.py): sectionings at
#      λ 0/4/16/256, whole-set bytes, the atom count, and every --tune
#      position's table choice with each row denied in turn.
#
# Usage: bash tests/clskit/run_clskit_tests.sh
# Env: CC, GENCFLAGS (default -O1 -std=gnu11 -Wall -Wextra -Werror), PROCS,
#   LIBPCREC (default build/libpcrec.a), KEEP=1, CLSKIT_RUN_WALL (checker
#   run wall backstop, default gen_timeout_secs).

set -u
export LC_ALL=C
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/unit_cc.sh"          # unit_build; sources cc_resolve.sh
. "$ROOT_DIR/tests/lib/gen_timeout.sh"      # gen_cc / gen_run (D45)
. "$ROOT_DIR/tests/lib/procs_default.sh"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
PROCS="${PROCS:-$PROCS_DEFAULT}"
KEEP="${KEEP:-0}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "clskit: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }
finish() {
    echo "checks passed: $pass"
    echo "checks failed: $fail"
    [ "$fail" -eq 0 ]
    exit $?
}

DRV="$WORKDIR/clskit_driver"
if ! unit_build "$DRV" "$SCRIPT_DIR/clskit_driver.c"; then
    bad "clskit_driver.c did not build"
    finish
fi
POP="$WORKDIR/pop.txt"
if ! python3 "$SCRIPT_DIR/populations.py" "$POP"; then
    bad "populations.py failed"
    finish
fi

# ---- 1+2. emit, census, compile, run -------------------------------------
mkdir -p "$WORKDIR/chk"
"$DRV" emit "$POP" "$WORKDIR/chk" > "$WORKDIR/emit.out"
if [ $? -ne 0 ]; then
    bad "clskit_driver emit failed"
    finish
fi
cat "$WORKDIR/emit.out"
empty=""
while read -r kind name count _rest; do
    [ "$kind" = LEAF ] || [ "$kind" = FORM ] || continue
    [ "$count" -gt 0 ] || empty="$empty $name"
done < "$WORKDIR/emit.out"
if [ -z "$empty" ]; then
    ok "census: every leaf form and every whole-set form was emitted at least once"
else
    bad "census: never emitted, so never checked:$empty"
fi

# One chunk: compile under the D45 budget, run under the run budget, keep
# the output for the tally below.
check_chunk() {
    local c="$1" b="${1%.c}"
    if ! gen_cc "clskit $(basename "$c")" "$CC" $GENCFLAGS -I"$SCRIPT_DIR" "$c" -o "$b.bin"; then
        printf '%s\n' "$GEN_CC_LOG" > "$b.log"
        echo "BUILDFAIL $(basename "$c")" >> "$b.log"
        return
    fi
    # RUSAGE_CHILDREN of this subshell so far = the compile alone (user+sys,
    # the RLIMIT_CPU clock D45 budgets), recorded so every run states its
    # headroom rather than only its failures.
    times > "$b.times"        # not piped: a pipeline's `times` is a subshell with no children
    sed -n 2p "$b.times" > "$b.cpu"
    # The checker is CPU-bound for ~1 s by construction (CHUNK_VARS /
    # CHUNK_BYTES cap a unit's work), unlike the sub-millisecond matcher runs
    # gen_run's TIGHT 10 s wall (gen_run_secs) is sized for. MEASURED
    # 2026-10-07 on the Linux dev box: 331 units, run wall median 0.14 s, max
    # 1.58 s with all 16 threads busy; the worst unit solo 0.94-1.10 s CPU. A
    # 10 s wall is then only ~6-10x, and wall (unlike the gen_cpu_secs CPU
    # budget, which stays the PRIMARY bound at its D45 default) stretches
    # with load: under `make test`'s -j16 mix plus another heavy suite it
    # can fire without any defect. So the wall BACKSTOP here is the compile
    # backstop's value (gen_timeout_secs: 60 s plain / 180 s sanitizer, D45's
    # "CPU budget x worst contention" sizing), still stuck-process detection,
    # no longer a load gauge. CLSKIT_RUN_WALL overrides.
    local rw="${CLSKIT_RUN_WALL:-$(gen_timeout_secs)}"
    GENRUNTIMEOUT="$rw" GENRUNTIMEOUT_SAN="$rw" \
        gen_run "clskit $(basename "$c")" "$b.bin" > "$b.log" 2>&1 || echo "RUNFAIL $(basename "$c") rc=$?" >> "$b.log"
}
nchunk=0
for c in "$WORKDIR"/chk/chunk_*.c; do
    check_chunk "$c" &
    nchunk=$((nchunk + 1))
    while [ "$(jobs -rp | wc -l)" -ge "$PROCS" ]; do wait -n; done
done
wait

nlog=$(ls "$WORKDIR"/chk/chunk_*.log 2>/dev/null | wc -l | tr -d ' ')
failed_chunks=$(grep -l -e '^BUILDFAIL' -e '^RUNFAIL' "$WORKDIR"/chk/chunk_*.log 2>/dev/null)
if [ "$nlog" -ne "$nchunk" ] || [ "$nchunk" -eq 0 ]; then
    bad "differential: $nlog logs for $nchunk chunks"
elif [ -n "$failed_chunks" ]; then
    for f in $failed_chunks; do sed -n '1,20p' "$f" >&2; done
    bad "differential: chunk(s) failed to build or run: $(echo $failed_chunks | xargs -n1 basename | tr '\n' ' ')"
else
    ok "differential: all $nchunk checker chunks built under GENCFLAGS and ran"
fi
grep -h 'MISMATCH' "$WORKDIR"/chk/chunk_*.log 2>/dev/null | head -20 >&2
# A set's variants may be spread over several units (the driver packs by
# bytes), so its CHECKED lines are counted by set INDEX (names repeat) and the variants by SUM
# against the driver's own emitted total: a variant that landed in no unit,
# or a set in none, shows here.
nsets=$(grep -h '^CHECKED' "$WORKDIR"/chk/chunk_*.log | sed -e 's/.* idx=//' | sort -u | wc -l | tr -d ' ')
nvars=$(grep -h '^CHECKED' "$WORKDIR"/chk/chunk_*.log | sed -e 's/.* variants=\([0-9]*\) .*/\1/' | awk '{s+=$1} END{print s+0}')
want_vars=$(sed -n 's/^CHUNKS .* VARIANTS \([0-9]*\)$/\1/p' "$WORKDIR/emit.out")
want_sets=$(grep -c '^SET ' "$POP")
read -r checks laws mism <<EOF
$(grep -h '^TOTAL' "$WORKDIR"/chk/chunk_*.log | awk '{split($2,a,"=");split($3,b,"=");split($4,c,"="); A+=a[2];B+=b[2];C+=c[2]} END{print A+0, B+0, C+0}')
EOF
ncomp=$(grep -c '^COMP ' "$POP")
nlaw=$(grep -h '^LAW' "$WORKDIR"/chk/chunk_*.log | wc -l | tr -d ' ')
if [ "$nsets" -ne "$want_sets" ] || [ "$nsets" -eq 0 ]; then
    bad "differential: $nsets sets checked of $want_sets in the population"
elif [ "$nvars" != "$want_vars" ]; then
    bad "differential: $nvars variants checked of $want_vars emitted"
elif [ "$mism" -ne 0 ]; then
    bad "differential: $mism mismatches over $checks code-point checks and $laws law checks"
else
    ok "differential: $nsets sets, $nvars variants, $checks code-point checks, 0 mismatches"
fi
# Compile-CPU headroom against the D45 budget, from the per-unit records.
cpu_line=$(cat "$WORKDIR"/chk/chunk_*.cpu 2>/dev/null | awk '{ split($1, u, /[ms]/); split($2, v, /[ms]/); t = u[1]*60 + u[2] + v[1]*60 + v[2]; if (t > m) m = t; s += t; n++ } END { printf "%d units, max %.2f s, total %.1f s", n, m, s }')
echo "clskit: compile CPU per unit (D45 budget $(gen_cpu_secs)s): $cpu_line"
if [ "$nlaw" -ne $((ncomp * 2)) ] || [ "$ncomp" -eq 0 ]; then
    bad "composition law: $nlaw law runs for $ncomp compositions x 2 variants"
elif [ "$mism" -eq 0 ]; then
    ok "composition law: $ncomp compositions x {K4, P3}, $laws code-point checks, 0 mismatches"
fi

# ---- 3. the cross-check against the study ---------------------------------
"$DRV" dump "$POP" > "$WORKDIR/dump.txt"
if python3 "$SCRIPT_DIR/crosscheck.py" "$POP" "$WORKDIR/dump.txt" --procs "$PROCS" \
        > "$WORKDIR/cross.out" 2>&1; then
    ok "crosscheck: $(tail -1 "$WORKDIR/cross.out")"
else
    grep -e '^DIFFER' -e 'Error' -e 'EMPTY' "$WORKDIR/cross.out" | head -20 >&2
    bad "crosscheck: $(tail -1 "$WORKDIR/cross.out")"
fi
grep '^TIE' "$WORKDIR/cross.out"

finish
