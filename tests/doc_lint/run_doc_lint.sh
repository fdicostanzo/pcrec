#!/usr/bin/env bash
# tests/doc_lint/run_doc_lint.sh -- `make test-doc-lint`: [DOC-INDEX] T1 (D192).
# Two checks, each of which must pass:
#   1. scripts/entry --selftest: the planted fixtures (one per routing row, the dormant profiles on the REAL
#      table, --over-cap rounding edges, --rev, the plan work view, the Policy templates).
#   2. scripts/entry --over-cap over the real tree: exits 0 and prints its trailer (the population line
#      scripts/gestalt reads; 0 pair indexes from T1 until unit 1).
#   3. scripts/entry --lint-scripts over the real tree: scripts/INDEX.md covers every script, every line names a file.
#   4. the same lint over a scratch COPY of scripts/ with a planted new script (no index line) and, separately, a
#      planted dangling index line: each must fail naming the plant (T1b, design §8.2 item 2).
# Unit 1 adds doc_lint.py's decisions profile here; T2 folds plan_lint in. Reads text only (no compiler).
# ROOT_DIR is overridable (the mech arm points it at a scratch tree).
set -u
ROOT_DIR="${ROOT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
ENTRY="$ROOT_DIR/scripts/entry"
pass=0; fail=0

out="$(python3 -I "$ENTRY" --selftest 2>&1)"; rc=$?
printf '%s\n' "$out"
if [ "$rc" -eq 0 ]; then pass=$((pass+1)); echo "PASS: entry --selftest"; else fail=$((fail+1)); echo "FAIL: entry --selftest rc=$rc"; fi

out="$(python3 -I "$ENTRY" --over-cap 2>&1)"; rc=$?
printf '%s\n' "$out"
if [ "$rc" -eq 0 ] && printf '%s\n' "$out" | grep -q '^entry: over-cap checked '; then
    pass=$((pass+1)); echo "PASS: entry --over-cap prints its trailer"
else fail=$((fail+1)); echo "FAIL: entry --over-cap rc=$rc"; fi

out="$(python3 -I "$ENTRY" --lint-scripts 2>&1)"; rc=$?
printf '%s\n' "$out"
if [ "$rc" -eq 0 ]; then pass=$((pass+1)); echo "PASS: entry --lint-scripts (real tree)"; else fail=$((fail+1)); echo "FAIL: entry --lint-scripts rc=$rc"; fi

. "$ROOT_DIR/scripts/tmpdir.sh"
tmp="$(mktemp -d -p "$PCREC_TMPDIR" doc_lint.XXXXXX)"
plant() { # label, expected text, shell snippet run in the scratch scripts/
    rm -rf "$tmp/scripts"; mkdir -p "$tmp/scripts"
    (cd "$ROOT_DIR/scripts" && find . -maxdepth 1 -type f -exec cp -p {} "$tmp/scripts/" \; && cp -rp hooks "$tmp/scripts/")
    (cd "$tmp/scripts" && eval "$3")
    out="$(python3 -I "$tmp/scripts/entry" --lint-scripts 2>&1)"; rc=$?
    if [ "$rc" -ne 0 ] && printf '%s\n' "$out" | grep -qF "$2"; then pass=$((pass+1)); echo "PASS: plant $1 is caught"
    else fail=$((fail+1)); echo "FAIL: plant $1 not caught (rc=$rc): $out"; fi
}
plant "new script without an index line" "zz_planted.sh has no line" 'printf "#!/bin/sh\n# planted\n" > zz_planted.sh'
plant "new hook without an index line" "hooks/zz_hook.sh has no line" 'printf "#!/bin/sh\n# planted\n" > hooks/zz_hook.sh'
plant "dangling index line" "zz_ghost.sh names no file" 'printf -- "- zz_ghost.sh live — when: never; does: nothing. {ghost}\n" >> INDEX.md'
plant "live script without a header" "live script has no header" 'printf "set -u\n" > tmpdir.sh'
rm -rf "$tmp"

# 5. the -g budget ([DOC-INDEX] dixpage): a broad search prints under 4 KB on every live profile unless --all; the
#    ID/slug-before-body order and the page tiling are entry --selftest's planted fixtures.
budget() { # label, args...
    local label="$1"; shift
    local bytes; bytes="$(python3 -I "$ENTRY" "$@" 2>&1 | wc -c)"
    if [ "$bytes" -lt 4096 ]; then pass=$((pass+1)); echo "PASS: -g budget $label ($bytes B)"
    else fail=$((fail+1)); echo "FAIL: -g budget $label printed $bytes B"; fi
}
for prof in plan completed scripts; do
    budget "$prof -g ." -g . -p "$prof"
    budget "$prof -g e -in 2 -l 2" -g e -in 2 -l 2 -p "$prof"
done
budget "all profiles -g span -in 2 -l 2" -g span -in 2 -l 2
budget "all profiles -g ." -g .

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
