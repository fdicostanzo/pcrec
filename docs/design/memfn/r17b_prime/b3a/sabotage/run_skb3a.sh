#!/usr/bin/env bash
# docs/design/memfn/r17b_prime/b3a/sabotage/run_skb3a.sh [OUTDIR] [ID...] --
# runs each SK-B3A-*.sh plant here SOLO, the matrix's way
# (tests/mech/run_sabotage_matrix.sh): a fresh `git archive HEAD` tree per
# plant, the edit through tests/mech/lib/replace.py (refused unless the anchor
# appears SAB_COUNT times), `make -j4`, then the row's suite: `candoracle` =
# tests/codegen/run_cand_oracle.sh (which runs tests/memfn/run_pres_picks.sh
# on its trace build), `memfnfinder` = tests/memfn/run_finder.sh. DETECTED iff
# the suite fails. PLACEHOLDER ids (SK-B3A-n): main allocates real ids and
# moves them into tests/mech/sabotages/. Each plant also runs the suite on the
# UNPLANTED tree first only once (the control), so a red control is not read
# as a detection.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"
OUT="${1:-$ROOT/build/land/skb3a}"; shift || true
mkdir -p "$OUT"
suite() { # SUITE TREE LOG
    case "$1" in
        candoracle)  (cd "$2" && TMPDIR="$OUT/tmp" gnutimeout 1800 bash tests/codegen/run_cand_oracle.sh "$2") > "$3" 2>&1 ;;
        memfnfinder) (cd "$2" && TMPDIR="$OUT/tmp" gnutimeout 1800 bash tests/memfn/run_finder.sh) > "$3" 2>&1 ;;
        *) echo "unknown suite $1" > "$3"; return 9 ;;
    esac
}
mkdir -p "$OUT/tmp"
ids=("$@"); [ "${#ids[@]}" -gt 0 ] || ids=($(cd "$HERE" && ls SK-B3A-*.sh | sed 's/\.sh$//' | sort -t- -k3 -n))
for id in "${ids[@]}"; do
    f="$HERE/$id.sh"; [ -f "$f" ] || f="$(ls "$HERE"/"$id"_*.sh 2>/dev/null | head -1)"
    id=$(basename "$f" .sh)
    t="$OUT/$id"; rm -rf "$t"; mkdir -p "$t/tree"
    git -C "$ROOT" archive HEAD | tar -x -C "$t/tree"
    ( . "$f"
      printf '%s' "$SAB_BEFORE" > "$t/before"; printf '%s' "$SAB_AFTER" > "$t/after"
      echo "$SAB_SUITES" > "$t/suite"
      python3 "$ROOT/tests/mech/lib/replace.py" "$t/tree/$SAB_FILE" "$t/before" "$t/after" "${SAB_COUNT:-1}" ) \
        > "$t/apply.log" 2>&1 || { echo "$id APPLY-FAILED"; continue; }
    if ! (cd "$t/tree" && gnutimeout 900 make -j4 > "$t/build.log" 2>&1); then echo "$id BUILD-FAILED (DETECTED by the build)"; continue; fi
    suite "$(cat "$t/suite")" "$t/tree" "$t/suite.log"; rc=$?
    nf=$(grep -E '^checks failed:' "$t/suite.log" | tail -1 | awk '{print $3+0}')
    np=$(grep -E '^checks passed:' "$t/suite.log" | tail -1 | awk '{print $3+0}')
    if [ "$rc" -ne 0 ]; then echo "$id DETECTED ($(cat "$t/suite"):${nf}fail/${np}pass, rc=$rc)"; else echo "$id NOT-DETECTED ($(cat "$t/suite"):${nf}fail/${np}pass)"; fi
    rm -rf "$t/tree"
done
echo "SKB3A_DONE"
