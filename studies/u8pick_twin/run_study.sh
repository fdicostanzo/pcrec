#!/bin/bash
# usage: run_study.sh [WORK_DIR] [CORE]
# Reproduces the whole u8pick0 twin from a pcrec worktree (run from its root):
#   1. regenerate pcrec-bench's 7 throughput subjects READ-ONLY (sha-checked)
#   2. build the c4c70f2c pin compiler (git archive) and the scratch u8prior analysis
#   3. compile every cell (arms A byte, B utf8, C utf8+u8prior, P pin; M, S literal arms)
#   4. time 15 interleaved passes per cell x subject on one taskset-pinned core
#   5. summarize, project onto the bench box, pick table, byte counts, stamps
# WORK_DIR defaults to build/u8 (gitignored).  Needs build/pcrec (make) first.
set -e
W=${1:-build/u8}; CORE=${2:-13}
BENCH=/home/pcrec/projects/pcrec-bench
S=studies/u8pick_twin; mkdir -p "$W"
python3 -I $S/gen_subjects.py $BENCH/bench/utf8 "$W/subj"
if [ ! -x "$W/pin/build/pcrec" ]; then
  mkdir -p "$W/pin"; git archive c4c70f2c | tar -x -C "$W/pin"; make -C "$W/pin" -j8 build/pcrec >/dev/null
fi
mkdir -p "$W/an"; python3 -I $S/gen_u8prior.py src/findings/default.rxt "$W/an"
while IFS=$'\t' read id pat; do
  [ "$id" = id ] && continue
  $S/build_cell.sh build/pcrec $S/drv.c "$W/cells" "$id" "$pat" "$PWD/$W/an" "$PWD/$W/pin/build/pcrec"
done < $S/cells.tsv
$S/run_all.sh "$W/cells" "$W/subj" "$CORE" 15 "$W/run.tsv"
python3 -I $S/summarize.py "$W/run.tsv" > "$W/summary.txt"
python3 -I $S/project.py "$W/run.tsv" $BENCH/reports > "$W/projection.tsv"
python3 -I $S/picktable.py "$W/cells" "$W/subj" > "$W/picktable.tsv"
python3 -I $S/bytecounts.py "$W/subj" $S/cells.tsv > "$W/bytecounts.tsv"
python3 -I $S/stamps.py "$W/cells" > "$W/stamps.tsv"
echo "done: $W/{summary.txt,projection.tsv,picktable.tsv,bytecounts.tsv,stamps.tsv}"
