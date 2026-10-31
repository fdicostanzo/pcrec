#!/usr/bin/env bash
# tests/codegen/run_stmt_writer.sh -- [VMREC] (a) ST: the static half of the
# VM body's one-writer rule (stmt_writer_scan.py has the rules). Static and
# light (no compiles); in `make test-codegen`. The run-time half is the
# body's own tiling check (src/gen/vm_stmt.c, vm_tile), which every VM
# compile in the suite exercises.
#
# Usage: bash tests/codegen/run_stmt_writer.sh
set -u
export LC_ALL=C
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
pass=0; fail=0
# The independent population: the same files, counted by git rather than by
# the scanner's own walk (a tree outside git falls back to find).
if git -C "$ROOT_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    n=$(git -C "$ROOT_DIR" ls-files --cached --others --exclude-standard -- 'src/*.[ch]' 'cli/*.[ch]' 'lib/*.[ch]' | wc -l)
else
    n=$(find "$ROOT_DIR/src" "$ROOT_DIR/cli" "$ROOT_DIR/lib" -name '*.[ch]' | wc -l)
fi
out=$(python3 -I "$SCRIPT_DIR/stmt_writer_scan.py" "$ROOT_DIR" "$n" 2>&1); rc=$?
printf '%s\n' "$out"
pass=$(printf '%s\n' "$out" | grep -c '^PASS:')
fail=$(printf '%s\n' "$out" | grep -c '^FAIL:')
[ "$rc" -ne 0 ] && [ "$fail" -eq 0 ] && fail=1
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
