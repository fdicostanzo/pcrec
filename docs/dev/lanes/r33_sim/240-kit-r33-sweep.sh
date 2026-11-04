#!/usr/bin/env bash
# 240-kit-r33-sweep: lane r33's ONE light sweep ([MEMFN] R-33): the probe compiler (build.sh, a
# traced scratch build, no source edit) over the .rxt corpus, the pcrec-bench pattern set (read-only)
# and job 588's patterns (RTE + DEF arms), then sim.py under each key and the sensitivity settings.
# Compile-only, no timing. Outputs: /var/tmp/pcrec-pcrec/scratch/memfn/r33/sweep/.
set -u
TREE=/home/pcrec/projects/pcrec/worktrees/r33
SIM=$TREE/docs/dev/lanes/r33_sim
S=/var/tmp/pcrec-pcrec/scratch/memfn/r33
OUT=$S/sweep
case "${1:-}" in
    --dry-run)
        [ -x "$TREE/build/pcrec" ] || { echo "no $TREE/build/pcrec (run make in the worktree)" >&2; exit 1; }
        n=$(python3 -I "$SIM/collect.py" --probe "$S/tb/pcrec-r33" --tree "$TREE" --out /dev/null --count-only |
            sed -n 's/^compiles \([0-9]*\) .*/\1/p')
        [ -n "$n" ] && [ "$n" -gt 50 ] || { echo "count-only gave no compile count" >&2; exit 1; }
        echo "would run: build.sh $TREE $S/tb; collect.py ($n compiles, --jobs 8) -> $OUT/sweep.jsonl; sim.py x6"
        echo "boxqueue: cap 2400"
        echo "boxqueue: patience none"
        echo "boxqueue: est 600"
        echo "boxqueue: expect compiles=$n last=^== r33 collect COMPLETE: "
        echo "boxqueue: witness compiles=== r33 collect COMPLETE: $n compiles"
        exit 0 ;;
    --ready)
        exit 0 ;;
esac
mkdir -p "$OUT"
bash "$SIM/build.sh" "$TREE" "$S/tb" || exit 1
python3 -I "$SIM/collect.py" --probe "$S/tb/pcrec-r33" --tree "$TREE" --out "$OUT/sweep.jsonl" --jobs 8 || exit 1
for args in "--key A" "--key B" "--key A --h-hit 10 --tag A_h10" "--key A --h-hit 40 --tag A_h40" \
            "--key B --h-hit 10 --tag B_h10" "--key B --h-hit 40 --tag B_h40"; do
    python3 -I "$SIM/sim.py" "$OUT/sweep.jsonl" "$OUT" $args || exit 1
done
echo "== r33 sweep done"
