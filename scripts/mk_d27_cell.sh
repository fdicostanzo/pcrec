#!/usr/bin/env bash
# mk_d27_cell.sh — a D27 test writer's environment: a git worktree for
# DELIVERY plus a parallel, allowlist-filtered, non-git CELL for the WORK.
#
# WHY (Frank's ruling, 2026-08-11 eighth session, amending the worktree
# convention). The harness auto-injects CLAUDE.md files from directories an
# agent touches — five recorded instances of D27 authors receiving DENIED
# files that way — and a git worktree additionally hands the author the
# whole history (`git show HEAD:src/...` defeats the blindness by
# instruction alone). The cell fixes both BY CONSTRUCTION: files that do
# not exist cannot be injected, and there is no .git to ask.
#
# ALLOWLIST, NEVER DENYLIST. The cell is built by copying what IS permitted.
# Deleting what is denied fails in the silent direction (a missed file
# reproduces the leak and nothing notices); an allowlist miss fails loudly
# (the author reports a missing file). Do not "improve" this into a delete.
#
# THE BUILD IS PREBUILT. The author must not run make (make needs src/,
# which the cell does not have). This script builds INSIDE the worktree —
# so the binary matches the delivery branch exactly — and copies build/
# (pcrec, libpcrec.a, obj/ — check01's nm oracle reads the objects; nm
# reveals symbol names only, which is that check's permitted oracle).
#
# FLOW:
#   scripts/mk_d27_cell.sh NAME allowed-path...   # create worktrees/NAME
#                                                 # (+branch) and
#                                                 # worktrees/NAME-cell
#   ... author works ONLY in worktrees/NAME-cell ...
#   # diff back (this script prints the exact commands on creation):
#   rsync -ai --delete NAME-cell/<dir>/ NAME/<dir>/   per allowed dir
#   git -C worktrees/NAME diff             # review; then commit + merge
#
# The residual, spawn-time leak this CANNOT remove: the session project
# root's CLAUDE.md and the memory index are injected before any tool runs,
# wherever the agent works. Briefs keep the disclosure requirement.

set -euo pipefail

usage() {
    echo "usage: scripts/mk_d27_cell.sh NAME allowed-path [allowed-path...]" >&2
    echo "  The allowlist is REQUIRED and is a per-lane decision: curate it" >&2
    echo "  against the lane's brief (R22 found the old hardcoded default was" >&2
    echo "  stale for post-M4.5 authors and would have leaked the K17/K18 fuzz" >&2
    echo "  alphabet). Example (the R22 capture-author cell):" >&2
    echo "    scripts/mk_d27_cell.sh capauthor docs/design/match_api_m4.md docs/testing.md" >&2
    exit 2
}

# No default allowlist (manager ruling, 2026-08-16, discharging R22 item 5):
# a hardcoded default goes stale silently and staleness fails in the LEAK
# direction; requiring the list makes cell contents an explicit per-lane
# decision, which is the only version that stays correct by construction.
[ $# -ge 2 ] || usage
NAME="$1"; shift
case "$NAME" in */*|.*) echo "mk_d27_cell: NAME must be a bare name" >&2; exit 2;; esac

ALLOW=("$@")

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WT="$ROOT/worktrees/$NAME"
CELL="$ROOT/worktrees/$NAME-cell"

[ ! -e "$WT" ]   || { echo "mk_d27_cell: $WT already exists" >&2; exit 1; }
[ ! -e "$CELL" ] || { echo "mk_d27_cell: $CELL already exists" >&2; exit 1; }
# validate the allowlist BEFORE creating anything, so a typo leaves no debris
for p in "${ALLOW[@]}"; do
    [ -e "$ROOT/$p" ] || { echo "mk_d27_cell: allowlisted path '$p' does not exist" >&2; exit 1; }
done

echo "== worktree (delivery target) =="
git -C "$ROOT" worktree add "$WT" -b "$NAME" HEAD

echo "== build inside the worktree (the cell's binary matches the branch) =="
make -C "$WT" >/dev/null

echo "== cell (allowlist copy, non-git) =="
mkdir -p "$CELL"
for p in "${ALLOW[@]}"; do
    [ -e "$WT/$p" ] || { echo "mk_d27_cell: '$p' exists at HEAD's root but not in the worktree" >&2; exit 1; }
    # Run rsync FROM the worktree with a relative source: macOS's openrsync
    # does not honor GNU rsync's "/./" insertion-point spelling of --relative
    # (an absolute source reproduced the full /Users/... path inside the cell,
    # caught by the hygiene check below, 2026-09-05); a relative source means
    # the same thing to both implementations.
    ( cd "$WT" && rsync -a --relative "./$p" "$CELL/" )
done
( cd "$WT" && rsync -a --relative "./build" "$CELL/" )

echo "== hygiene verification (the point of the cell) =="
BAD=0
if find "$CELL" -name '.git*' | grep -q .; then
    echo "FAIL: git metadata leaked into the cell:"; find "$CELL" -name '.git*'; BAD=1
fi
# every top-level entry must be explained by the allowlist or build/
while IFS= read -r top; do
    rel="${top#"$CELL"/}"
    ok=0
    [ "$rel" = build ] && ok=1
    for p in "${ALLOW[@]}"; do
        case "$p/" in "$rel"/*) ok=1;; esac
        case "$rel/" in "$p"/*|"${p%%/*}"/) ok=1;; esac
    done
    if [ "$ok" -eq 0 ]; then
        echo "FAIL: unexplained top-level entry in cell: $rel"; BAD=1
    fi
done < <(find "$CELL" -mindepth 1 -maxdepth 1)
echo "CLAUDE.md files present (must all lie inside allowlisted dirs):"
find "$CELL" -name CLAUDE.md | sed "s|$CELL/|  |"
[ "$BAD" -eq 0 ] || { echo "mk_d27_cell: HYGIENE FAILED — do not hand this cell to an author" >&2; exit 1; }

cat <<DONE

CELL READY.
  author works in:  $CELL   (and NOWHERE else; non-git, allowlist-only)
  delivery target:  $WT   (branch $NAME — the author never touches it)

WHEN THE AUTHOR FINISHES, diff the cell back and review:
DONE
for p in "${ALLOW[@]}"; do
    if [ -d "$CELL/$p" ]; then
        echo "  rsync -ai --delete '$CELL/$p/' '$WT/$p/'"
    else
        echo "  rsync -ai '$CELL/$p' '$WT/$p'"
    fi
done
cat <<DONE
  git -C '$WT' status --short && git -C '$WT' diff   # review
  # then commit on the branch (note authorship), merge --no-ff, and:
  git -C '$ROOT' worktree remove '$WT' && git -C '$ROOT' branch -d '$NAME'
  rm -rf '$CELL'
DONE
