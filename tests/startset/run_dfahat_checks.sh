#!/usr/bin/env bash
# tests/startset/run_dfahat_checks.sh — [START-SET] stage 3, THE DFA HAT's
# checks (D148 + addenda 1-2; `make test-startset`, mech arm `dfahat`): the
# corpus fixtures `dfahat.rxt`/`reseed.rxt`/`hybrid.rxt`/`dfahat_paths.rxt`
# through the harness (every answer libpcre2's or python's), `dfahat_checks.py`
# (the stamp's IFF, the route, the conditional re-seed, T == S ⊊ E, the deny
# arm is today's emitter, the mover manifest by ID, witnesses) and
# `vmhat_diff.py` under `HAT=dfa` (the every-startpos differential against
# the deny arm and the start-byte oracle, own options / `--no-captures` /
# `-fprefilter-collapse`). Each script's header carries its independence
# argument and floors. One trailer pair for the whole run (the mech arm reads
# the first `checks passed:`/`checks failed:`).
#
# Env: PCREC (default <root>/build/pcrec), JOBS, TMPDIR.
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
export PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
p=0; f=0
tally() {  # tally <log>: add a script's own trailer to the run's
    local a b
    a="$(sed -n 's/^checks passed: //p' "$1" | tail -1)"
    b="$(sed -n 's/^checks failed: //p' "$1" | tail -1)"
    if [ -z "$a" ] || [ -z "$b" ]; then f=$((f + 1)); echo "FAIL: $1 printed no trailer"; return; fi
    p=$((p + a)); f=$((f + b))
}
W="$(mktemp -d "${TMPDIR:-/tmp}/dfahat.XXXXXX")"
trap 'rm -rf "$W"' EXIT

# The fixtures, through the corpus harness. Floor: half the landing count.
bash "$ROOT_DIR/tests/harness/run.sh" "$SCRIPT_DIR/dfahat.rxt" "$SCRIPT_DIR/reseed.rxt" \
    "$SCRIPT_DIR/hybrid.rxt" "$SCRIPT_DIR/dfahat_paths.rxt" > "$W/fix.log" 2>&1
cp_="$(sed -n 's/^cases passed: //p' "$W/fix.log" | tail -1)"
cf_="$(sed -n 's/^cases failed: //p' "$W/fix.log" | tail -1)"
if [ -n "$cp_" ] && [ "${cf_:-1}" = 0 ] && [ "$cp_" -ge 884 ]; then
    p=$((p + 1)); echo "PASS: [dfa-fix] tests/startset/{dfahat,reseed,hybrid,dfahat_paths}.rxt: $cp_ cases, 0 failed (floor 884, half the landing 1,769)"
else
    f=$((f + 1)); echo "FAIL: [dfa-fix] tests/startset/{dfahat,reseed,hybrid,dfahat_paths}.rxt: passed=${cp_:-?} failed=${cf_:-?}"
    grep -E "FAIL|GAVE UP|expected" "$W/fix.log" | head -10
fi

python3 "$SCRIPT_DIR/dfahat_checks.py" > "$W/checks.log" 2>&1; grep -v '^checks ' "$W/checks.log"; tally "$W/checks.log"
HAT=dfa python3 "$SCRIPT_DIR/vmhat_diff.py" > "$W/diff.log" 2>&1; grep -v '^checks ' "$W/diff.log"; tally "$W/diff.log"

echo "checks passed: $p"
echo "checks failed: $f"
[ "$f" -eq 0 ]
