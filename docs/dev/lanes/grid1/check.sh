#!/bin/bash
# grid1/check.sh -- the MANDATORY correctness gate before any slot. Every arm
# of every (cell, subject, mode) group must answer exactly as its cell's base
# arm, every own cell's base must answer exactly as the python `re` oracle,
# and the generated arms must run clean under the deep legs. Any (cell, arm)
# that fails anything is listed in $OUT/excluded and time.sh does not time it.
#
#   OUT=... bash check.sh            (after build.sh)  -> $OUT/check.log, $OUT/excluded
#
# Legs, per group (arms.py groups all: the timed tables, ext sets included,
# and F2's), each output compared with cmp, never summarized first:
#   O  own cells: the base's `GRID_FIXED=0 run` answer == oracle.tsv's line
#      (grid.py oracles: python `re` over the bytes, independent of pcrec);
#   R  every arm: its `GRID_FIXED=0 run` answer == the base's (ext arms too;
#      this is the contract's matches+hash);
#   L  arms with a `chk`: the full match list (`chk SUBJ list MODE`; a
#      streamed subject lists per-buffer answers) == the base's;
#   C  streamed subjects: `GRID_FIXED=<nbuf> run` -> cycle == cycleexp: the
#      content fingerprints of the buffers the timed loop's cursor hands its
#      passes equal every buffer's, in order (gdrv.c's header says why an
#      answer cannot show this);
# and, per own GENERATED arm (DEEP_SUBJ below, vecspike check.sh's legs):
#   E  `every` startpos sweep, N `rand` startpos (both directions), F `fuzz`
#      slices x base offsets 0..63, A chka (ASan+UBSan + mkvar's VS_DEBUG
#      re-probe of every candidate) on list first|all at (OFF,CUT) in
#      {(0,0) (1,1) (13,29) (31,7)} and on rand.
# and, last, the REACH leg U (no clock): time.sh --counts runs every counting
# twin; an own (cell, subject, mode) whose site counters (G1's cnt) read
# uses=0 never reaches the site (an upstream gate answered), so timing it
# would time the gate: it is listed in $OUT/unreached and time.sh skips it.
# U does not exclude arms (it is a fact about the subject, not an arm).
# Leg G (landing fidelity, no clock): for every own `all`-mode group, the
# site's uses must equal the subject's planted landings + matches within
# +-10% (+1 per buffer for the final call; less the landings past a
# buffer's last match, which the pre-check gates): a row whose landings the site
# does not see is a row whose g label is false. A G failure is a DESIGN
# error: it fails the check (exit 1) without excluding an arm.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${OUT:-/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid1}
CPUS=${CPUS:-12-15}
JOBS=${JOBS:-4}
T=${TO:-gnutimeout}
export OUT T HERE
export ASAN_OPTIONS=detect_leaks=1 UBSAN_OPTIONS=print_stacktrace=1
mkdir -p "$OUT/res" "$OUT/tmp" "$OUT/ans"
TMPDIR=$OUT/tmp; export TMPDIR
rm -f "$OUT"/res/*
start=$(date +%s)

python3 -I "$HERE/arms.py" "$OUT" validate all > "$OUT/tmp/validate.out" 2>&1 || { cat "$OUT/tmp/validate.out"; echo "check: ARM TABLES INVALID"; exit 1; }
tail -1 "$OUT/tmp/validate.out"
taskset -c "$CPUS" python3 -I "$HERE/grid.py" oracles "$OUT" -j "$JOBS" || { echo "check: ORACLE FAILED"; exit 1; }

. "$HERE/checklib.sh"

if [ "${DEEP_ONLY:-0}" != 1 ]; then
  python3 -I "$HERE/arms.py" "$OUT" groups all > "$OUT/tmp/groups.all"
  echo "groups: $(wc -l < "$OUT/tmp/groups.all")"
  taskset -c "$CPUS" xargs -P "$JOBS" -L1 -a "$OUT/tmp/groups.all" bash -c 'group "$0" "$1" "$2" "$3"'
fi
if [ "${SKIP_DEEP:-0}" != 1 ]; then
  OWN_CELLS="dig bounded dfa-hat hex-run word-eq quad"
  printf '%s\n' $OWN_CELLS | taskset -c "$CPUS" xargs -P "$JOBS" -I{} bash -c 'deep_ref {}'
  for c in $OWN_CELLS; do for V in walk $DEEP_ARMS; do echo "$c $V"; done; done |
    taskset -c "$CPUS" xargs -P "$JOBS" -L1 bash -c 'deep_one "$0" "$1"'
fi
rm -f "$OUT/counts.tsv"
OUT=$OUT bash "$HERE/time.sh" --counts
awk -F'\t' '$2=="site(G1)" && $5 ~ /(^| )uses=0 / {print $1"\t"$3"\t"$4}' "$OUT/counts.tsv" | sort -u > "$OUT/unreached"
nsite=$(awk -F'\t' '$2=="site(G1)"' "$OUT/counts.tsv" | wc -l)
python3 -I - "$OUT" > "$OUT/landing_fidelity" <<'PYEOF'
import os, sys
out = sys.argv[1]
facts = {}
for l in open(os.path.join(out, "subj_facts.tsv")).read().splitlines()[1:]:
    f = l.split("\t"); facts[f[0]] = (int(f[7]), int(f[8]), int(f[9]), int(f[2]), int(f[3]), int(f[4]))
for l in open(os.path.join(out, "counts.tsv")).read().splitlines()[1:]:
    c, a, s, m, line = l.split("\t")
    if a != "site(G1)" or m != "all": continue
    nm = s.split("@")[0]
    if nm not in facts: continue
    nbuf, pm, pl, n, g, L = facts[nm]
    kv = dict(x.split("=") for x in line.split())
    uses = int(kv["uses"]); want = pm + pl
    # landings past a buffer's LAST match are never visited: the whole-window
    # pre-check (a required byte, e.g. dig's `x`) answers first. Allowed per buffer.
    tail = (n % L + 1) if L and L < n else 1
    short = nbuf * (tail // g + 1) if g else 0
    ok = want - short - 0.10 * want - nbuf <= uses <= want + 0.10 * want + nbuf
    print(f"{'OK  ' if ok else 'FAIL'} {c} {s} uses={uses} planted_landings+matches={want}")
PYEOF
gfail=$(grep -c '^FAIL' "$OUT/landing_fidelity")
echo "landing fidelity (G): $(grep -c '^OK' "$OUT/landing_fidelity") ok, $gfail FAIL"; grep '^FAIL' "$OUT/landing_fidelity" | head -20
echo "reach (U): $nsite site rows, $(wc -l < "$OUT/unreached") unreached"; sed 's/^/  UNREACHED /' "$OUT/unreached"
{
  echo "# grid1 check $(date -u) $(uname -n) wall=$(( $(date +%s) - start ))s"
  cat "$OUT"/res/*
} > "$OUT/check.log"
grep -h ' FAIL\| RC=' "$OUT"/res/* | awk '{print $1, $2}' | sort -u > "$OUT/excluded"
echo "legs OK:   $(cat "$OUT"/res/* | grep -c ' OK$')"
for leg in O R L C E N F A; do printf '  %s %s' "$leg" "$(cat "$OUT"/res/* | awk -v l="$leg" '$3==l' | grep -c ' OK$')"; done; echo
echo "legs FAIL: $(grep -h ' FAIL\| RC=' "$OUT"/res/* | wc -l)"
echo "excluded (cell arm): $(wc -l < "$OUT/excluded")"; cat "$OUT/excluded"
echo "check: done wall=$(( $(date +%s) - start ))s"
[ "$gfail" -gt 0 ] && { echo "check: LANDING FIDELITY FAILED ($OUT/landing_fidelity)"; exit 1; }
[ -s "$OUT/excluded" ] && exit 1 || exit 0
