#!/usr/bin/env bash
# tests/axes/giveup1_key_check.sh -- GIVEUP1_ALLOWANCE's text identity
# (fsfix 4). run_axes.sh admits a one-sided give-up by its manifest key; the
# sr_depth.rxt entries are keyed `<file>@<pattern line> :: <case line>` so a
# comment edit above them cannot unname them (trailgc's 8-line header moved
# eleven line keys and turned test-axes red). This check loads the real table
# and lookup out of run_axes.sh and holds:
#   1. every sr_depth text key resolves at its CURRENT line (the table is
#      reachable, not merely present);
#   2. the same file with comment lines inserted above still resolves
#      (the property the key exists for);
#   3. a case whose subject text changed does NOT resolve (admission is by
#      the case, not by the file or the line number alone).
# Sabotage S1853 plants a line-number lookup and loses (2).
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
RUN="${RUN_AXES:-$ROOT_DIR/tests/axes/run_axes.sh}"   # RUN_AXES: sabotage hook
TMP="$(mktemp -d "${TMPDIR:-/var/tmp}/giveup1_key.XXXXXX")" || exit 1
trap 'rm -rf "$TMP"' EXIT
pass=0 fail=0
ok()  { pass=$((pass + 1)); echo "PASS: $1"; }
bad() { fail=$((fail + 1)); echo "FAIL: $1"; }

# the table and the two lookup functions, verbatim, under a scratch ROOT_DIR
eval "$(sed -n '/^declare -A GIVEUP1_ALLOWANCE=(/,/^giveup1_named() {/p' "$RUN" | sed '$d')"
eval "$(sed -n '/^giveup1_named() {/,/^}/p' "$RUN")"
REL=tests/recursion/d27/sr_depth.rxt
FLAG=-fno-req-byte
mapfile -t KEYS < <(printf '%s\n' "${!GIVEUP1_ALLOWANCE[@]}" | grep -F -- "$FLAG|$REL@" | sort)
[ "${#KEYS[@]}" -eq 11 ] && ok "the table holds 11 text-keyed sr_depth entries" \
    || bad "the table holds ${#KEYS[@]} text-keyed sr_depth entries, want 11"

# 1. the real file: the cases at the lines the full suite reported
n=0
for l in 91 165 166 167 168 169 187 188 189 190 191; do
    giveup1_named "$FLAG" "$ROOT_DIR/$REL:$l" && n=$((n + 1))
done
[ "$n" = 11 ] && ok "all 11 sr_depth cases resolve in the real file" \
    || bad "only $n of 11 sr_depth cases resolve in the real file (is the table stale?)"

# 2. a comment edit above them
mkdir -p "$TMP/tests/recursion/d27"
{ for i in 1 2 3 4 5 6 7 8 9; do echo "# inserted comment $i"; done; cat "$ROOT_DIR/$REL"; } > "$TMP/$REL"
ROOT_DIR="$TMP"; n=0
for l in 100 174 175 176 177 178 196 197 198 199 200; do
    giveup1_named "$FLAG" "$TMP/$REL:$l" && n=$((n + 1))
done
[ "$n" = 11 ] && ok "all 11 still resolve after 9 comment lines are inserted above them" \
    || bad "only $n of 11 resolve after a comment edit above them"

# 3. a changed case is not named
sed 's/^n "bbb"$/n "bbbb"/' "$ROOT_DIR/$REL" > "$TMP/$REL.x" && mv "$TMP/$REL.x" "$TMP/$REL"
if giveup1_named "$FLAG" "$TMP/$REL:100"; then
    bad "a case whose subject changed (n \"bbbb\") is still named"
else
    ok "a case whose subject changed is not named"
fi
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" = 0 ]
