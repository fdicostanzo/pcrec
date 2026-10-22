#!/usr/bin/env bash
# tests/claudemd_size/run_claudemd_size.sh -- `make test-claudemd-size`:
# (1) the real tree is within the limits; (2) a sabotage self-test in a temp
# tree: a 13 KB directory CLAUDE.md and a 21 KB root one FAIL, a 1 KB one passes.
set -u
ROOT_DIR=${ROOT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}
CHK="$ROOT_DIR/scripts/check_claudemd_size.sh"
fail=0; ok=0
check() { if [ "$1" = "$2" ]; then ok=$((ok + 1)); else echo "FAIL: $3" >&2; fail=$((fail + 1)); fi; }

CLAUDEMD_ROOT="$ROOT_DIR" bash "$CHK" --all; check $? 0 "real tree over a limit"

T=$(mktemp -d "${TMPDIR:-/tmp}/claudemd_size.XXXXXX") || exit 1
trap 'rm -rf "$T"' EXIT
mkdir -p "$T/a" "$T/worktrees/old" "$T/docs/dev/history/claude_md"
head -c 1024 /dev/zero | tr '\0' x > "$T/CLAUDE.md"
head -c 1024 /dev/zero | tr '\0' x > "$T/a/CLAUDE.md"
CLAUDEMD_ROOT="$T" bash "$CHK" --all >/dev/null 2>&1; check $? 0 "1 KB files must pass"

head -c 13000 /dev/zero | tr '\0' x > "$T/a/CLAUDE.md"
CLAUDEMD_ROOT="$T" bash "$CHK" --all >"$T/out" 2>&1; check $? 1 "13 KB directory file must fail"
grep -q 'a/CLAUDE.md is 13000 bytes, limit 12288: move history/notes to NOTES.md' "$T/out"; check $? 0 "message names file, size, limit"
head -c 1024 /dev/zero | tr '\0' x > "$T/a/CLAUDE.md"

head -c 13000 /dev/zero | tr '\0' x > "$T/CLAUDE.md"
CLAUDEMD_ROOT="$T" bash "$CHK" --all >/dev/null 2>&1; check $? 0 "13 KB root file must pass (limit 20 KB)"
head -c 21000 /dev/zero | tr '\0' x > "$T/CLAUDE.md"
CLAUDEMD_ROOT="$T" bash "$CHK" --all >/dev/null 2>&1; check $? 1 "21 KB root file must fail"
head -c 1024 /dev/zero | tr '\0' x > "$T/CLAUDE.md"

head -c 99999 /dev/zero | tr '\0' x > "$T/worktrees/old/CLAUDE.md"
head -c 99999 /dev/zero | tr '\0' x > "$T/docs/dev/history/claude_md/CLAUDE.md"
CLAUDEMD_ROOT="$T" bash "$CHK" --all >/dev/null 2>&1; check $? 0 "worktrees/ and the history archive are skipped"

# hot-path row: docs/dev/CLAUDE.md is held to 4 KB (5 KB fails, 3 KB passes)
mkdir -p "$T/docs/dev"
head -c 5000 /dev/zero | tr '\0' x > "$T/docs/dev/CLAUDE.md"
CLAUDEMD_ROOT="$T" bash "$CHK" --all >"$T/out" 2>&1; check $? 1 "5 KB docs/dev/CLAUDE.md must fail"
grep -q 'docs/dev/CLAUDE.md is 5000 bytes, limit 4096' "$T/out"; check $? 0 "hot-path message names the 4096 limit"
head -c 3000 /dev/zero | tr '\0' x > "$T/docs/dev/CLAUDE.md"
CLAUDEMD_ROOT="$T" bash "$CHK" --all >/dev/null 2>&1; check $? 0 "3 KB docs/dev/CLAUDE.md must pass"
rm "$T/docs/dev/CLAUDE.md"

# --staged judges the staged content
git -C "$T" init -q && git -C "$T" config user.email t@t && git -C "$T" config user.name t
head -c 13000 /dev/zero | tr '\0' x > "$T/a/CLAUDE.md"
git -C "$T" add a/CLAUDE.md
CLAUDEMD_ROOT="$T" bash "$CHK" --staged >/dev/null 2>&1; check $? 1 "staged 13 KB file must fail"
head -c 1024 /dev/zero | tr '\0' x > "$T/a/CLAUDE.md"
CLAUDEMD_ROOT="$T" bash "$CHK" --staged >/dev/null 2>&1; check $? 1 "--staged reads the index, not the working file"
git -C "$T" add a/CLAUDE.md
CLAUDEMD_ROOT="$T" bash "$CHK" --staged >/dev/null 2>&1; check $? 0 "staged 1 KB file must pass"

if [ $fail -eq 0 ]; then echo "checks passed: $ok"; else echo "checks failed: $fail (passed $ok)" >&2; exit 1; fi
