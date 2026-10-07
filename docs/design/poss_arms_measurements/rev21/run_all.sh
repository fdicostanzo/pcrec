#!/usr/bin/env bash
# rev 2.1's measurement battery, in one place (lane possarms21).  Runs, in
# order: the generators; the libpcre2 soundness/ablation sweeps (eqcheck.py,
# every claimed, ablation-tagged or hand row; arm A families at ML=4 NR=100,
# arm B at ML=5 NR=300, as rev 2); CLAIM-vs-MARK over all three families
# under every configuration; the census (+ R-5); the exhaustive possdiff
# with every plant.  Writes into $OUT; one line per stage into $OUT/STAGES.
# Env: PROTO (rev-2.1 prototype), PROTO2 (rev-2 prototype), PCREC (for
# --list-source; the prototype with no arm is main), BENCH, JOBS (8).
set -u
export LC_ALL=C
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$HERE/../../../.." && pwd)
: "${PROTO:?}" "${PROTO2:?}" "${OUT:?}"
J=${JOBS:-8}
mkdir -p "$OUT"
stage() { echo "$(date +%T) $*" >> "$OUT/STAGES"; }
stage start
python3 -B "$HERE/gen_a21.py" > "$OUT/gen_a21.tsv"
python3 -B "$HERE/gen_a021.py" > "$OUT/gen_a021.tsv"
python3 -B "$HERE/gen_b21.py" > "$OUT/gen_b21.tsv"
stage generators $(wc -l < "$OUT/gen_a21.tsv") $(wc -l < "$OUT/gen_a021.tsv") $(wc -l < "$OUT/gen_b21.tsv")

# --- eqcheck (libpcre2 only), sharded
sweep() {  # name file ML NR
    # CHUNKED: eqcheck.py holds every row's subject list in memory, and ten
    # 2,300-row shards OOM-killed on a 15 GB box (rev 2.1's first run).
    # 200-row chunks, J at a time.
    awk -F'\t' '$5=="yes"||$7!=""||$9=="hand"' "$2" > "$OUT/$1.sel"
    rm -f "$OUT/$1".chunk.*
    awk -v o="$OUT/$1.chunk." '{ print > (o sprintf("%05d", int((NR - 1) / 200))) }' "$OUT/$1.sel"
    ls "$OUT/$1".chunk.* | ML=$3 NR=$4 xargs -P "$J" -I{} sh -c \
        'python3 -B "$0/../eqcheck.py" {} > {}.out 2> {}.err || echo "CHUNK-FAILED {} rc=$?" >&2' "$HERE"
    cat "$OUT/$1".chunk.*.out > "$OUT/$1.out"
    cat "$OUT/$1".chunk.*.err > "$OUT/$1.err"
    rm -f "$OUT/$1".chunk.*
    stage "eqcheck $1 rows=$(wc -l < "$OUT/$1.sel") out=$(wc -l < "$OUT/$1.out") errors=$(grep -c ERROR "$OUT/$1.out")"
}
SWEEPS=${SWEEPS:-a21 a021 b21}
case " $SWEEPS " in *" a21 "*) sweep eq_a21 "$OUT/gen_a21.tsv" 4 100 ;; esac
case " $SWEEPS " in *" a021 "*) sweep eq_a021 "$OUT/gen_a021.tsv" 4 100 ;; esac
case " $SWEEPS " in *" b21 "*) sweep eq_b21 "$OUT/gen_b21.tsv" 5 300 ;; esac
[ "${ONLY_SWEEPS:-0}" = 1 ] && { stage "end (sweeps only)"; exit 0; }

# --- CLAIM-vs-MARK (pcrec vs the frozen predicate), every config
PROTO="$PROTO" JOBS=$J python3 -B "$HERE/r21_claimmark.py" "$OUT/gen_a21.tsv" "$OUT/gen_a021.tsv" "$OUT/gen_b21.tsv" \
    > "$OUT/claimmark.out" 2> "$OUT/claimmark.err"
stage "claimmark rc=$?"

# --- census + R-5 + R4SUM
PROTO="$PROTO" PROTO2="$PROTO2" PCREC="${PCREC:-$PROTO}" ARTREV_GEN="$ROOT/docs/dev/optloop/artrev/gen" \
    BENCH="${BENCH:-/Users/fdicostanzo/pcrec-bench}" CORPUS="$ROOT" JOBS=$J \
    python3 -B "$HERE/r21_census.py" > "$OUT/census_r21.tsv" 2> "$OUT/census_r21.err"
stage "census rc=$?"

# --- exhaustive possdiff, arms + every plant + route-flip
PROTO="$PROTO" OUT="$OUT/pdx" "$HERE/possdiff_plants.sh" > "$OUT/pdx_verdicts.txt" 2>&1
stage "possdiff done"
stage end
