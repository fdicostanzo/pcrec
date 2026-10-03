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
#   timing    LAUNCHES fresh launches per binary (default 15, I-114's
#             bimodal per-process state), round-robin with the order
#             rotated each round, every launch `taskset -c CORE`; one launch
#             = the median of PASSES passes (default 7), each pass >= MINMS
#             ms (default 50, the bench's pinned-record rule) by calibrating
#             the iteration count on d first.
#   output    per (cell, regime, compiler): d's ns, then every variant's
#             median / d's median, `floor` = the larger of |d2/d-1| and
#             |dL/d-1|, and `ans` = same/DIFF. Then per compiler, for each
#             form: the geometric mean and the worst ratio over the
#             IMPROVE rows, and the worst KEEP row measured against `a`
#             (a form must keep the shipped win within the floor).
#   accept    xcall.md §6: answers same on every row; an improve row reads
#             form/d at or under 1 + floor on BOTH compilers; no keep row
#             loses more than its floor against `a`.
# Env: CCS ("gcc clang"), LAUNCHES, PASSES, MINMS, OPT (-O2).
set -euo pipefail
PACK=$(cd "$1" && pwd); CORE=${2:-2}
CCS=${CCS:-"gcc clang"} LAUNCHES=${LAUNCHES:-15} PASSES=${PASSES:-7} MINMS=${MINMS:-50} OPT=${OPT:--O2}
TO=$(command -v gnutimeout || command -v timeout)   # ubuntubudu: bare timeout is uutils (~105 ms/call)
PIN=(); if command -v taskset >/dev/null; then PIN=(taskset -c "$CORE"); else echo "bakeoff: WARNING no taskset, launches are NOT pinned" >&2; fi
FORMS="ai f1 f2 f3 f3i f4"
W="$PACK/work"; rm -rf "$W"; mkdir -p "$W"
RAW="$W/raw.tsv"; : > "$RAW"
echo "bakeoff: pack $PACK, core $CORE, $LAUNCHES launches x $PASSES passes >= ${MINMS} ms, $(date -u +%FT%TZ), load $(cut -d' ' -f1-3 /proc/loadavg 2>/dev/null || uptime)" | tee "$W/header"
head -3 "$PACK/MANIFEST" | tee -a "$W/header"
for cc in $CCS; do echo "  $cc: $($cc --version | head -1)" | tee -a "$W/header"; done

# rows: id pattern flags role mode subjects
ROWS=(); while IFS= read -r l; do ROWS+=("$l"); done < <(grep -v '^#' "$PACK/cells.tsv")
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
    done <<<"$ids"
done
echo "bakeoff: built $(find "$W" -type f -perm -u+x | wc -l | tr -d ' ') binaries"

# ---- answers, calibration, timing ----------------------------------------
for row in "${ROWS[@]}"; do
    IFS=$'\t' read -r id _pat _fl role mode globs <<<"$row"
    # shellcheck disable=SC2206
    files=($(cd "$PACK" && ls $globs)); files=("${files[@]/#/$PACK/}")
    label="$id/$mode:$(basename "${files[0]}" .bin)$([ ${#files[@]} -gt 1 ] && echo "+$((${#files[@]} - 1))" || true)"
    vs="a d d2 dL"; [ "$role" != a1 ] && vs="a $FORMS d d2 dL"
    for cc in $CCS; do
        B="$W/$cc/$id"
        hd=$("$TO" 120 "$B.d" "$mode" 1 1 "${files[@]}" | cut -d' ' -f3)
        ans=same
        for v in $vs; do
            h=$("$TO" 120 "$B.$v" "$mode" 1 1 "${files[@]}" | cut -d' ' -f3)
            [ "$h" = "$hd" ] || { ans="DIFF:$v"; echo "bakeoff: ANSWER DIFF $label $cc $v" >&2; }
        done
        per=$(${PIN[@]+"${PIN[@]}"} "$TO" 120 "$B.d" "$mode" 1 3 "${files[@]}" | cut -d' ' -f1)   # ns per iteration
        it=$(python3 -c "import math; print(max(1, math.ceil($MINMS * 1e6 / max($per, 1.0))))")
        set -- $vs
        for ((r = 0; r < LAUNCHES; r++)); do
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

# ---- the table -----------------------------------------------------------
python3 - "$RAW" "$FORMS" <<'PY' | tee "$W/table.txt"
import math, statistics as st, sys
raw, forms = sys.argv[1], sys.argv[2].split()
cells = {}
order = []
for ln in open(raw):
    label, role, cc, v, t, ans, it = ln.rstrip("\n").split("\t")
    k = (label, cc)
    if k not in cells: cells[k] = {"role": role, "ans": ans, "t": {}}; order.append(k)
    cells[k]["t"].setdefault(v, []).append(float(t))
cols = ["a"] + forms
print("%-30s %-5s %-7s %10s  %s  %6s  %s" % ("cell/regime:subjects", "cc", "role", "d ns", " ".join("%6s" % c for c in cols), "floor", "ans"))
summ = {}
for k in order:
    c = cells[k]; med = {v: st.median(x) for v, x in c["t"].items()}; d = med["d"]
    floor = max(abs(med["d2"] / d - 1), abs(med["dL"] / d - 1))
    r = {v: med[v] / d for v in med}
    print("%-30s %-5s %-7s %10.0f  %s  %5.1f%%  %s" % (k[0], k[1], c["role"], d,
          " ".join("%6.3f" % r[v] if v in r else "%6s" % "-" for v in cols), 100 * floor, c["ans"]))
    for v in forms:
        if v not in r: continue
        s = summ.setdefault((k[1], v), {"imp": [], "worst_imp": (0, ""), "worst_keep": (-9, ""), "imp_over": 0})
        if c["role"] == "improve":
            s["imp"].append(r[v])
            if r[v] > s["worst_imp"][0]: s["worst_imp"] = (r[v], k[0])
            if r[v] > 1 + floor: s["imp_over"] += 1
        elif c["role"] == "keep":
            loss = r[v] / r["a"] - 1 - floor
            if loss > s["worst_keep"][0]: s["worst_keep"] = (loss, k[0])
print()
print("per compiler and form: improve rows (geomean of form/d, worst, rows above 1+floor); keep rows (worst loss vs a beyond the floor; <= 0 passes)")
for (cc, v), s in sorted(summ.items()):
    gm = math.exp(sum(map(math.log, s["imp"])) / len(s["imp"])) if s["imp"] else float("nan")
    print("  %-5s %-4s improve geomean x%.3f  worst x%.3f (%s)  above-floor %d/%d   keep worst %+.1f%% (%s)" % (
        cc, v, gm, s["worst_imp"][0], s["worst_imp"][1], s["imp_over"], len(s["imp"]),
        100 * s["worst_keep"][0], s["worst_keep"][1] or "-"))
bad = [k for k in order if cells[k]["ans"] != "same"]
print("\nanswers: %s" % ("same on every row" if not bad else "DIFF on %d row(s): %s" % (len(bad), bad)))
PY
echo "bakeoff: done $(date -u +%FT%TZ); raw $RAW, table $W/table.txt"
