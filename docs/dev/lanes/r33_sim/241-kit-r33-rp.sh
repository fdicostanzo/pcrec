#!/usr/bin/env bash
# 241-kit-r33-rp: lane r33's second light sweep ([MEMFN] R-33): the probe compiler over the rule-list
# pilot's census arms (rulepilot_evidence/inventory: every arm of every compiled site, its deny set),
# then sim.py under keys A and B, so each arm's kit decisions can be read beside its timing on file.
# Compile-only, no timing. Outputs: /var/tmp/pcrec-pcrec/scratch/memfn/r33/rp/.
set -u
TREE=/home/pcrec/projects/pcrec/worktrees/r33
SIM=$TREE/docs/dev/lanes/r33_sim
S=/var/tmp/pcrec-pcrec/scratch/memfn/r33
OUT=$S/rp
case "${1:-}" in
    --dry-run)
        [ -x "$TREE/build/pcrec" ] || { echo "no $TREE/build/pcrec (run make in the worktree)" >&2; exit 1; }
        n=$(python3 -I "$SIM/collect.py" --probe "$S/tb/pcrec-r33" --tree "$TREE" --out /dev/null --sources rp --count-only |
            sed -n 's/^compiles \([0-9]*\) .*/\1/p')
        [ -n "$n" ] && [ "$n" -gt 0 ] || { echo "count-only gave no compile count" >&2; exit 1; }
        echo "would run: build.sh $TREE $S/tb; collect.py ($n compiles, --jobs 8) -> $OUT/sweep.jsonl; sim.py x2"
        echo "boxqueue: cap 900"
        echo "boxqueue: patience none"
        echo "boxqueue: est 120"
        echo "boxqueue: expect compiles=$n last=^== r33 collect COMPLETE: "
        echo "boxqueue: witness compiles=== r33 collect COMPLETE: $n compiles"
        exit 0 ;;
    --ready)
        exit 0 ;;
esac
mkdir -p "$OUT"
bash "$SIM/build.sh" "$TREE" "$S/tb" || exit 1
python3 -I "$SIM/collect.py" --probe "$S/tb/pcrec-r33" --tree "$TREE" --out "$OUT/sweep.jsonl" --sources rp --jobs 8 || exit 1
for args in "--key A" "--key B"; do
    python3 -I "$SIM/sim.py" "$OUT/sweep.jsonl" "$OUT" $args || exit 1
done
echo "== r33 rp sweep done"
