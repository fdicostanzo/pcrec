#!/bin/bash
# bakeoff.sh PACKDIR [CORE] — [OPT-HYB-RESEED-FORM] A2's form bake-off
# (docs/design/xcall.md §4 A2 / §6), run on the LINUX box by the manager.
#
# Builds every variant of every cell in PACKDIR (prep.sh's output) with gcc
# AND clang at -O2, checks each variant's answers against the deny, then
# times them pinned to one core and prints ONE table.
#
#   variants  a    the shipped adaptive retry (the A1 cell: main's artifact)
#             ai f1 f2 f3 f3i f4   the hand-rewritten forms (mkforms.py)
#             d    -fno-hyb-reseed, the fixed retry: every ratio's denominator
#             d2   d's binary again   } THE NOISE FLOOR: the same program
#             dL   d, link order swapped } (d2: launch noise; dL: + layout)
#             aL   a, link order swapped: the keep rows' floor (a keep row
#                  compares a form against `a`, so `a`'s own layout spread
#                  is its allowance; lane a2build, after round 1's clang
#                  lkapos/f read dL/d 31.5% at d2/d 0.1%)
#   timing    LAUNCHES fresh launches per binary (default 15, I-114's
#             bimodal per-process state), round-robin with the order
#             rotated each round, every launch `taskset -c CORE`; one launch
#             = the median of PASSES passes (default 7), each pass >= MINMS
#             ms (default 50, the bench's pinned-record rule) by calibrating
#             the iteration count on d first.
#   output    per (cell, regime, compiler): d's ns, then every variant's
#             median / d's median, the launch floor |d2/d-1| and the layout
#             floor max(|dL/d-1|, |aL/a-1|), and `ans` = same/DIFF (table.py,
#             which also lists every cells.tsv row NOT timed). Then per
#             compiler, for each
#             form: the geometric mean and the worst ratio over the
#             IMPROVE rows, and the worst KEEP row measured against `a`
#             (a form must keep the shipped win within the floor).
#   accept    xcall.md §6: answers same on every row; an improve row reads
#             form/d at or under 1 + floor on BOTH compilers; no keep row
#             loses more than its floor against `a`.
# Env: CCS ("gcc clang"), LAUNCHES, PASSES, MINMS, OPT (-O2), FORMS (the
# forms to build and time; default below, any subset of mkforms.py's),
# ROWCAP (wall seconds per (row, compiler), default 900: a row over it is
# killed and listed, never left to run for hours), ONLY (space-separated
# cell ids: rerun just those into an EXISTING work dir, keeping every other
# id's raw.tsv lines and binaries; the ids' own lines are replaced).
#
# Round 2 (2026-10-03): lpatom's calibration read per = 0.0 and chose
# 50,000,000 iterations (~3 min per timed run). Cause: sdrv.c's caps was
# caps[1][2] and lpatom's pattern has a capture group, so a MATCHING subject
# overran it and clobbered the timer's accumulator (tot printed 0.0). Fixed
# in shape/sdrv.c; and a per below 1 ns now stops the row instead of being
# floored to 1.0.
#
# Round 1 (2026-10-03) died under `set -e` after timing 20 of 40 rows: the
# label's `$([ N -gt 1 ] && echo ...)` returns 1 on the first single-subject
# row (lbvar), which fails the assignment. The label is now computed without
# a failing substitution, an ERR trap names the line that stops a run, and
# an EXIT trap renders whatever raw.tsv holds, with the NOT TIMED rows.
set -euo pipefail
trap 'echo "bakeoff: STOPPED at line $LINENO (rc $?): $BASH_COMMAND" >&2' ERR
PACK=$(cd "$1" && pwd); CORE=${2:-2}
CCS=${CCS:-"gcc clang"} LAUNCHES=${LAUNCHES:-15} PASSES=${PASSES:-7} MINMS=${MINMS:-50} OPT=${OPT:--O2}
TO=$(command -v gnutimeout || command -v timeout)   # ubuntubudu: bare timeout is uutils (~105 ms/call)
PIN=(); if command -v taskset >/dev/null; then PIN=(taskset -c "$CORE"); else echo "bakeoff: WARNING no taskset, launches are NOT pinned" >&2; fi
FORMS=${FORMS:-"ai f1 f1i f3 f3i"}
ROWCAP=${ROWCAP:-900} ONLY=${ONLY:-}
W="$PACK/work"; RAW="$W/raw.tsv"
if [ -n "$ONLY" ]; then
    [ -s "$RAW" ] || { echo "bakeoff: ONLY needs an existing $RAW" >&2; exit 2; }
    cp "$RAW" "$W/raw.before_only.tsv"
    for o in $ONLY; do awk -F'\t' -v id="$o/" 'index($1, id) != 1' "$RAW" > "$RAW.new" && mv "$RAW.new" "$RAW"; done
else
    rm -rf "$W"; mkdir -p "$W"; : > "$RAW"
fi
render() { [ -s "$RAW" ] && python3 "$PACK/table.py" "$RAW" "$PACK/cells.tsv" "$FORMS" | tee "$W/table.txt"; echo "bakeoff: end $(date -u +%FT%TZ); raw $RAW, table $W/table.txt"; }
trap render EXIT
echo "bakeoff: pack $PACK, core $CORE, $LAUNCHES launches x $PASSES passes >= ${MINMS} ms, $(date -u +%FT%TZ), load $(cut -d' ' -f1-3 /proc/loadavg 2>/dev/null || uptime)" | tee "$W/header"
head -4 "$PACK/MANIFEST" | tee -a "$W/header"
for cc in $CCS; do echo "  $cc: $($cc --version | head -1)" | tee -a "$W/header"; done

# rows: id pattern flags role mode subjects
ROWS=(); while IFS= read -r l; do ROWS+=("$l"); done < <(grep -v '^#' "$PACK/cells.tsv")
if [ -n "$ONLY" ]; then
    SEL=(); for l in "${ROWS[@]}"; do
        for o in $ONLY; do [ "$(cut -f1 <<<"$l")" = "$o" ] && SEL+=("$l"); done
    done; ROWS=("${SEL[@]}")
fi
ids=$(printf '%s\n' "${ROWS[@]}" | cut -f1,4 | sort -u)

# ---- build --------------------------------------------------------------
for cc in $CCS; do
    mkdir -p "$W/$cc"
    while IFS=$'\t' read -r id role; do
        vs="a d"; [ "$role" != a1 ] && vs="a $FORMS d"
        for v in $vs; do
            hdr="$PACK/src/$id.a.h"; [ "$v" = d ] && hdr="$PACK/src/$id.d.h"
            (cd "$PACK/src" && $cc $OPT -w -include "$hdr" -o "$W/$cc/$id.$v" ../sdrv.c "$id.$v.c")
        done
        cp "$W/$cc/$id.d" "$W/$cc/$id.d2"
        (cd "$PACK/src" && $cc $OPT -w -include "$PACK/src/$id.d.h" -o "$W/$cc/$id.dL" "$id.d.c" ../sdrv.c)
        (cd "$PACK/src" && $cc $OPT -w -include "$PACK/src/$id.a.h" -o "$W/$cc/$id.aL" "$id.a.c" ../sdrv.c)
    done <<<"$ids"
done
echo "bakeoff: built $(find "$W" -type f -perm -u+x | wc -l | tr -d ' ') binaries"

# ---- answers, calibration, timing ----------------------------------------
for row in "${ROWS[@]}"; do
    IFS=$'\t' read -r id _pat _fl role mode globs <<<"$row"
    # shellcheck disable=SC2206
    files=($(cd "$PACK" && ls $globs)); files=("${files[@]/#/$PACK/}")
    label="$id/$mode:$(basename "${files[0]}" .bin)"
    if [ ${#files[@]} -gt 1 ]; then label="$label+$((${#files[@]} - 1))"; fi
    vs="a aL d d2 dL"; [ "$role" != a1 ] && vs="a aL $FORMS d d2 dL"
    for cc in $CCS; do
        B="$W/$cc/$id"
        hd=$("$TO" 120 "$B.d" "$mode" 1 1 "${files[@]}" | cut -d' ' -f3)
        ans=same
        for v in $vs; do
            h=$("$TO" 120 "$B.$v" "$mode" 1 1 "${files[@]}" | cut -d' ' -f3)
            [ "$h" = "$hd" ] || { ans="DIFF:$v"; echo "bakeoff: ANSWER DIFF $label $cc $v" >&2; }
        done
        per=$(${PIN[@]+"${PIN[@]}"} "$TO" 120 "$B.d" "$mode" 1 3 "${files[@]}" | cut -d' ' -f1)   # ns per iteration
        # a per under 1 ns is a broken measurement (round 2: 0.0 from a
        # smashed accumulator), never a fast cell: stop this row, go on
        if ! python3 -c "import sys; sys.exit(0 if float('$per') >= 1.0 else 1)" 2>/dev/null; then
            echo "bakeoff: CALIBRATION per='$per' < 1 ns, row SKIPPED: $label $cc" >&2; continue
        fi
        it=$(python3 -c "import math; print(max(1, math.ceil($MINMS * 1e6 / max($per, 1.0))))")
        set -- $vs
        rowend=$((SECONDS + ROWCAP))
        for ((r = 0; r < LAUNCHES; r++)); do
            if [ "$SECONDS" -ge "$rowend" ]; then
                echo "bakeoff: ROWCAP ${ROWCAP}s hit, row cut at launch $r/$LAUNCHES: $label $cc" >&2; break
            fi
            order=("$@"); n=${#order[@]}
            for ((k = 0; k < n; k++)); do
                v=${order[$(((k + r) % n))]}
                t=$(${PIN[@]+"${PIN[@]}"} "$TO" 600 "$B.$v" "$mode" "$it" "$PASSES" "${files[@]}" | cut -d' ' -f1)
                printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$label" "$role" "$cc" "$v" "$t" "$ans" "$it" >> "$RAW"
            done
        done
        echo "bakeoff: timed $label $cc (iters $it, answers $ans)" >&2
    done
done

# ---- the table: the EXIT trap (render) prints it -------------------------
