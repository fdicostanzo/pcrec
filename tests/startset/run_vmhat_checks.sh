#!/usr/bin/env bash
# tests/startset/run_vmhat_checks.sh — [START-SET] stage 2, THE VM HAT's
# checks (D148; `make test-startset`, mech arm `vmhat`): the corpus fixtures
# `vmhat.rxt`/`giveup.rxt` through the harness (every answer libpcre2's),
# `vmhat_checks.py` (the stamp's IFF, route/anchor/handoff, the deny arm is
# today's emitter, table == fact, the mover manifest by ID, witnesses) and
# `vmhat_diff.py` (the every-startpos differential against the deny arm and
# the start-byte oracle). Each script's header carries its independence
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
W="$(mktemp -d "${TMPDIR:-/tmp}/vmhat.XXXXXX")"
trap 'rm -rf "$W"' EXIT

# The fixtures, through the corpus harness (its own oracle: libpcre2's
# answers written into the cells by docs/design/startset/edge/gen_rxt.py).
bash "$ROOT_DIR/tests/harness/run.sh" "$SCRIPT_DIR/vmhat.rxt" "$SCRIPT_DIR/giveup.rxt" "$SCRIPT_DIR/vmhat_walk.rxt" > "$W/fix.log" 2>&1
cp_="$(sed -n 's/^cases passed: //p' "$W/fix.log" | tail -1)"
cf_="$(sed -n 's/^cases failed: //p' "$W/fix.log" | tail -1)"
if [ -n "$cp_" ] && [ "${cf_:-1}" = 0 ] && [ "$cp_" -ge 240 ]; then
    p=$((p + 1)); echo "PASS: [vm-fix] tests/startset/{vmhat,giveup,vmhat_walk}.rxt: $cp_ cases, 0 failed (floor 240, half the landing 480)"
else
    f=$((f + 1)); echo "FAIL: [vm-fix] tests/startset/{vmhat,giveup,vmhat_walk}.rxt: passed=${cp_:-?} failed=${cf_:-?}"
    grep -E "FAIL|GAVE UP|expected" "$W/fix.log" | head -10
fi

python3 "$SCRIPT_DIR/vmhat_checks.py" > "$W/checks.log" 2>&1; cat "$W/checks.log" | grep -v '^checks '; tally "$W/checks.log"
python3 "$SCRIPT_DIR/vmhat_diff.py" > "$W/diff.log" 2>&1; cat "$W/diff.log" | grep -v '^checks '; tally "$W/diff.log"

echo "checks passed: $p"
echo "checks failed: $f"
[ "$f" -eq 0 ]
