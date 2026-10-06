#!/usr/bin/env bash
# tests/startset/run_dfahat_checks.sh — [START-SET] stage 3, THE DFA HAT's
# checks (D148 + addenda 1-2; `make test-startset`), in TWO PARTS that the
# mech scores as two arms (ss3 D6 panel checks-M1: a row planting the re-seed
# must be seen by the ANSWER checks, not by a text pin on the line it edits):
#
#   answers (mech arm `dfahat`): the corpus fixtures `dfahat.rxt`/
#     `reseed.rxt`/`hybrid.rxt`/`dfahat_paths.rxt`/`dfahat_f1.rxt` through the
#     harness (every answer libpcre2's or python's), twice — as written and
#     under `RXTFLAGS=-fprefilter-collapse` (checks-M4: the count-collapsed
#     hybrids' answers against the oracle, which the import of ssedge's
#     collapse targets had dropped) — and `vmhat_diff.py` under `HAT=dfa` (the
#     every-startpos differential against the deny arm and the start-byte
#     oracle, own options / `--no-captures` / `-fprefilter-collapse` /
#     `-futf-check`).
#   struct (mech arm `dfahatstruct`): `dfahat_checks.py` (the stamp's IFF, the
#     route, the conditional re-seed, T = S ⊊ E, the deny arm is today's
#     emitter, the mover manifest by ID, witnesses) and `compile_fuzz.py` (the
#     compile-only arm: the deny arm compiles => the default compiles, the
#     panel's BLOCKER sound-F1's detector).
#
# DFAHAT_PART=answers|struct|all (default all, which `make test-startset`
# runs). Each script's header carries its independence argument and floors.
# One trailer pair per run (the mech arm reads the first `checks passed:`/
# `checks failed:`).
#
# Env: PCREC (default <root>/build/pcrec), JOBS, TMPDIR, DFAHAT_PART.
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

PART="${DFAHAT_PART:-all}"
case "$PART" in answers|struct|all) ;; *) echo "FAIL: DFAHAT_PART=$PART (answers|struct|all)"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1 ;; esac
FIX="$SCRIPT_DIR/dfahat.rxt $SCRIPT_DIR/reseed.rxt $SCRIPT_DIR/hybrid.rxt $SCRIPT_DIR/dfahat_paths.rxt $SCRIPT_DIR/dfahat_f1.rxt"

fixtures() {  # fixtures <tag> <floor> [RXTFLAGS]: the fixture files through the corpus harness
    local tag="$1" floor="$2" fl="${3:-}" cp_ cf_
    # shellcheck disable=SC2086
    RXTFLAGS="$fl" bash "$ROOT_DIR/tests/harness/run.sh" $FIX > "$W/$tag.log" 2>&1
    cp_="$(sed -n 's/^cases passed: //p' "$W/$tag.log" | tail -1)"
    cf_="$(sed -n 's/^cases failed: //p' "$W/$tag.log" | tail -1)"
    if [ -n "$cp_" ] && [ "${cf_:-1}" = 0 ] && [ "$cp_" -ge "$floor" ]; then
        p=$((p + 1)); echo "PASS: [$tag] the five fixture files${fl:+ under $fl}: $cp_ cases, 0 failed (floor $floor, half the landing 2,091)"
    else
        f=$((f + 1)); echo "FAIL: [$tag] the five fixture files${fl:+ under $fl}: passed=${cp_:-?} failed=${cf_:-?}"
        grep -E "FAIL|GAVE UP|expected" "$W/$tag.log" | head -10
    fi
}

if [ "$PART" != struct ]; then
    fixtures dfa-fix 1045
    fixtures dfa-fix-collapse 1045 -fprefilter-collapse
    HAT=dfa python3 "$SCRIPT_DIR/vmhat_diff.py" > "$W/diff.log" 2>&1; grep -v '^checks ' "$W/diff.log"; tally "$W/diff.log"
fi
if [ "$PART" != answers ]; then
    python3 "$SCRIPT_DIR/dfahat_checks.py" > "$W/checks.log" 2>&1; grep -v '^checks ' "$W/checks.log"; tally "$W/checks.log"
    python3 "$SCRIPT_DIR/compile_fuzz.py" > "$W/fuzz.log" 2>&1; grep -v '^checks ' "$W/fuzz.log"; tally "$W/fuzz.log"
fi

echo "checks passed: $p"
echo "checks failed: $f"
[ "$f" -eq 0 ]
