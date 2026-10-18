#!/usr/bin/env bash
# tests/spec_history/run_hook_selftest.sh -- self-test of the CONDITIONAL spec
# gate in scripts/hooks/pre-commit ([SPEC-HOOK]), wired into
# run_spec_history.sh the way plan_lint.sh --selftest is wired into
# run_plan_lint.sh. It builds a scratch git repo under build/ holding the real
# hook, the real checkers and one real numbered spec (tuning.md), plants one
# case per row below, and runs the hook itself. A gate that reads green
# because it checked nothing fails here: each BLOCK row must exit non-zero
# with the named reason, each PASS row zero, and the NONE rows must not even
# start the checker (PCREC_HOOK_TRACE witness).
# The planted line cites are assembled from pieces so this file is not itself
# a citation (tests/spec_history/ is also in cite_exclude.tsv).
set -u
ROOT_DIR="${ROOT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
mkdir -p "$ROOT_DIR/build"
W="$(mktemp -d -p "$ROOT_DIR/build" hookselftest.XXXXXX)" || exit 1
trap 'rm -rf "$W"' EXIT
pass=0; fail=0
R="$W/repo"; TRACE="$W/trace"; : > "$TRACE"
mkdir -p "$R/scripts/hooks" "$R/tests/spec_history" "$R/docs/spec" "$R/docs/dev"
cp "$ROOT_DIR/scripts/hooks/pre-commit" "$R/scripts/hooks/"
cp "$ROOT_DIR/scripts/spec_toc.py" "$R/scripts/"
cp "$ROOT_DIR"/tests/spec_history/*.py "$ROOT_DIR"/tests/spec_history/*.tsv "$R/tests/spec_history/"
cp "$ROOT_DIR/docs/spec/tuning.md" "$R/docs/spec/"
: > "$R/tests/spec_history/cite_exclude.tsv"
G() { git -C "$R" "$@"; }
G init -q . && G config user.email t@example.invalid && G config user.name t
G add -A && G -c core.hooksPath=/dev/null commit -q -m base
H="$R/scripts/hooks/pre-commit"
D=tuning; LN=123

# run NAME EXPECT(0|1) [REASON] [RAN(0|1)] -- run the hook against the index
run() {
    local name="$1" want="$2" why="${3:-}" ran="${4:-1}" out rc before after
    before=$(wc -l < "$TRACE")
    out="$(cd "$R" && PCREC_HOOK_TRACE="$TRACE" bash "$H" 2>&1)"; rc=$?
    after=$(wc -l < "$TRACE")
    local ok=1
    [ "$rc" -eq "$want" ] || ok=0
    [ -z "$why" ] || printf '%s' "$out" | grep -qF -- "$why" || ok=0
    [ $((after - before)) -eq "$ran" ] || ok=0
    if [ "$ok" -eq 1 ]; then pass=$((pass+1)); echo "PASS: $name"
    else fail=$((fail+1)); echo "FAIL: $name (rc=$rc want $want, checker ran $((after-before)) want $ran)"; printf '%s\n' "$out" | sed 's/^/    /'; fi
}
reset() { G reset -q --hard; G clean -qfd; mkdir -p "$R/docs/dev"; }

# 1. a staged report with a line cite blocks
printf 'see %s.md:%s for the entry\n' "$D" "$LN" > "$R/docs/dev/report.md"
G add docs/dev/report.md
run "staged report with a line cite blocks" 1 "line-number citation"
# 2. the same file unstaged does not (only an unrelated binary-kind file staged)
G reset -q; echo '{}' > "$R/data.json"; G add data.json
run "the same report unstaged does not block, and nothing runs" 0 "" 0
reset
# 3. a staged report with a valid section cite passes; a dangling one blocks
printf 'see %s.md §1 and §2\n' "$D" > "$R/docs/dev/report.md"; G add docs/dev/report.md
run "staged report with valid section cites passes" 0
printf 'see %s.md §99.9 gone\n' "$D" > "$R/docs/dev/report.md"; G add docs/dev/report.md
run "staged report with a dangling section cite blocks" 1 "dangling citation"
reset
# 4. a staged spec edit that breaks the contents blocks; the index is judged, not the working file
sed 's/^## 1\. What a tuning flag is/## 1. What a tuning flag really is/' "$R/docs/spec/tuning.md" > "$W/t.md"
cp "$W/t.md" "$R/docs/spec/tuning.md"; G add docs/spec/tuning.md
run "staged spec edit with a stale contents block blocks" 1 "table of contents is stale"
cp "$ROOT_DIR/docs/spec/tuning.md" "$R/docs/spec/tuning.md"     # working file now clean, index still broken
run "the index is judged, not the clean working file" 1 "table of contents is stale"
reset
# 5. a broken UNSTAGED spec is not judged: the commit records what is staged
printf 'unrelated\n' > "$R/docs/dev/note.md"; G add docs/dev/note.md
printf '\nThis revision (%s-%s-%s) edits the working copy only.\n' 2026 10 18 >> "$R/docs/spec/tuning.md"
run "a broken UNSTAGED spec is not judged" 0
reset
# 6. a numbering break (a duplicated heading number) and new build history block
python3 - "$R/docs/spec/tuning.md" <<'PY'
import sys
p = sys.argv[1]; t = open(p, encoding="utf-8").read()
t = t.replace("## 2. The axes", "## 1. The axes", 1)
open(p, "w", encoding="utf-8").write(t)
PY
G add docs/spec/tuning.md
run "staged spec with a repeated section number blocks" 1 "numbering"
reset
printf '\nThis revision (%s-%s-%s) changed the default.\n' 2026 10 18 >> "$R/docs/spec/tuning.md"
G add docs/spec/tuning.md
run "staged spec with build history blocks" 1 "history marker"
reset
# 7. a spec edit that strands a citation elsewhere in the tree blocks (wide scan on a staged spec)
printf 'see %s.md §3.1\n' "$D" > "$R/docs/dev/old.md"; G add docs/dev/old.md
G -c core.hooksPath=/dev/null commit -q -m old
python3 - "$R/docs/spec/tuning.md" <<'PY'
import sys
p = sys.argv[1]; t = open(p, encoding="utf-8").read()
t = t.replace("### 3.1 A VM hybrid", "### 3.9 A VM hybrid").replace('<a id="s3-1"></a>', '<a id="s3-9"></a>')
open(p, "w", encoding="utf-8").write(t)
PY
G add docs/spec/tuning.md
run "a staged spec edit leaving an unstaged file's citation dangling blocks" 1 "dangling"
reset
# 8. an unrelated commit runs nothing
echo '{}' > "$R/b.json"; printf 'x\n' > "$R/blob.bin"; G add b.json blob.bin
run "an unrelated commit runs nothing" 0 "" 0

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
