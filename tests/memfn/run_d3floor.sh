#!/usr/bin/env bash
# tests/memfn/run_d3floor.sh -- R-44: THE D3 PCREC-ARTIFACT FLOOR as a gate (part_d.md §5.1 D3 "ARMED at the joint
# landing"; R-43 wrote the check, R-44 wired it). `make test-memfn-d3floor`; also the last step of `make test-axes`
# (so the battery's axes stage runs it). NOT in `make test`: MEASURED about 120 s at -j4 (four traced corpus sweeps
# of ~5,000 compiles each), over the 60 s a `make test` section is allowed (lane d3wire, R-44's ruling table).
#
# Builds the traced probe compiler (docs/dev/lanes/r33_sim/build.sh: libpcrec with -DMF_TRACE -DPCREC_CAND_TRACE
# into a scratch dir, no source edit), runs collect.py's corpus sweep once per emit_sweep (base, stream) cell, and
# hands the four sweeps to d3_floor.py, which counts them against d3_floor.tsv (the floors' one home) and runs its
# own plants (S3228-S3230) so a gate that cannot fail shows. Compile-only, no timing.
#
# Usage: bash tests/memfn/run_d3floor.sh [TREE]
# Env: PROCS (collect workers AND the probe build's make -j; default: half of tests/lib/procs_default.sh, at least 1),
#      D3FLOOR_KEEP=1 (keep the scratch dir, printed, for a re-count). Scratch lives under $PCREC_TMPDIR (scripts/tmpdir.sh), never /tmp.
set -u
export LC_ALL=C
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TREE="$(cd "${1:-$here/../..}" && pwd)"
. "$TREE/tests/lib/timeout_bin.sh"
SIM="$TREE/docs/dev/lanes/r33_sim"
. "$TREE/scripts/tmpdir.sh"
mkdir -p "$TMPDIR/scratch" || exit 2   # scripts/tmpdir.sh forced TMPDIR to the temp root
WORK="$(mktemp -d "$TMPDIR/scratch/d3floor.XXXXXX")" || exit 2
if [ "${D3FLOOR_KEEP:-0}" = 1 ]; then echo "d3floor: scratch kept at $WORK"; else trap 'rm -rf "$WORK"' EXIT; fi
JOBS="${PROCS:-$(( $(sh "$TREE/tests/lib/procs_default.sh") / 2 ))}"
[ "$JOBS" -ge 1 ] 2>/dev/null || JOBS=1
export BUILD_JOBS="$JOBS"

fail() { echo "FAIL: [d3floor] $*"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1; }

[ -x "$TREE/build/pcrec" ] || fail "no $TREE/build/pcrec (collect.py's corpus enumeration needs it; run make)"
"$TIMEOUT_BIN" 900 bash "$SIM/build.sh" "$TREE" "$WORK/tb" > "$WORK/tb.log" 2>&1 || { tail -20 "$WORK/tb.log"; fail "the traced probe build failed"; }

args=()
for c in "byte/c-default|" "byte/c-vm|--engine=vm" "utf8/c-default|-e utf8" "utf8/c-vm|-e utf8 --engine=vm"; do
    cell=${c%%|*}; flags=${c#*|}; t=${cell/\//_}
    "$TIMEOUT_BIN" 1200 python3 -I "$SIM/collect.py" --probe "$WORK/tb/pcrec-r33" --tree "$TREE" --sources corpus \
        --jobs "$JOBS" --flags="$flags" --out "$WORK/$t.jsonl" > "$WORK/$t.log" 2>&1 \
        || { tail -5 "$WORK/$t.log"; fail "collect.py failed on cell $cell"; }
    args+=("$cell=$WORK/$t.jsonl")
done

"$TIMEOUT_BIN" 600 python3 -I "$TREE/tests/memfn/d3_floor.py" --tree "$TREE" "${args[@]}" | tee "$WORK/floor.out"
rc=${PIPESTATUS[0]}
n=$(grep -c '^D3-FLOOR-PLANT .* ok$' "$WORK/floor.out")
# the plants are counted: PLANTS per cell x 4 cells; they are skipped by design on a red cell (d3_floor.py says so),
# so a short count is only a second failure when every cell was green
skipped=$(grep -c '^D3-FLOOR-PLANTS-SKIPPED ' "$WORK/floor.out")
want=$(( (4 - skipped) * 8 ))
if [ "$skipped" -gt 0 ]; then echo "d3floor: plants skipped on $skipped red cell(s); the red cell is the failure"
elif [ "$n" -lt "$want" ]; then echo "FAIL: [d3floor] only $n of $want plants ran and went as expected"; rc=1; fi
if [ "$rc" -eq 0 ]; then echo "checks passed: 1"; echo "checks failed: 0"; else echo "checks passed: 0"; echo "checks failed: 1"; fi
exit "$rc"
