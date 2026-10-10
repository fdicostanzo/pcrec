#!/usr/bin/env bash
# tests/memfn/run_arch_blind.sh -- C4, THE ARCH-BLINDNESS DETECTOR ([MEMFN],
# D146/D147, integration.md §10.4 and §17.5). `make test-memfn-arch`.
#
# pcrec carries no architecture knowledge: src/, cli/ and lib/ (code and the
# CLAUDE.md files inside them) and tests/ contain no ISA vocabulary outside
# tests/memfn/c4_allowlist.tsv, which was COUNTED AT BIRTH and only descends.
# The nine classes, the scopes, the allowlist's shape and the controls are in
# arch_blind_check.py's header. Static: reads files, runs no pcrec binary; the
# plants are derived from the compiler's own installation ($CC, default gcc).
#
# THE INDEPENDENT CONTROLS (docs/dev/learnings.md §3):
#   - C4_ALLOW_FLOOR is THIS literal, the K35 floor on the allowlist's total
#     hit count: it shares no source with the TSV, so deleting an allowlist
#     row without lowering it is red, and a change that lowers the list lowers
#     it here in the same commit.
#   - the positive controls (one per class) are planted in a scratch tree and
#     derived from the compiler, never from the regexes; a class with no plant
#     on this box is RED, not skipped; the negative control is the hex escape.
#
# Usage: bash tests/memfn/run_arch_blind.sh [ROOT]
#   ROOT defaults to the tree this script sits in (the mech driver runs the
#   sabotaged tree's own copy). Needs TMPDIR for scratch (or the system one).

set -u

C4_ALLOW_FLOOR=27

here="$(cd "$(dirname "$0")" && pwd)"
root="${1:-$(cd "$here/../.." && pwd)}"

echo "== C4: the arch-blindness detector (tests/memfn/c4_allowlist.tsv) =="
python3 "$here/arch_blind_check.py" "$root" "$root/tests/memfn/c4_allowlist.tsv" "$C4_ALLOW_FLOOR"
rc=$?
if [ "$rc" -ne 0 ] && [ "$rc" -ne 1 ]; then
    echo "FAIL: arch_blind_check.py exited $rc before reporting"
    echo "checks passed: 0"
    echo "checks failed: 1"
    exit 1
fi
exit "$rc"
