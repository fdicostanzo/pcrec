#!/usr/bin/env bash
# tests/memfn/run_site_manifest.sh — C17, THE CHECKED SITE MANIFEST
# ([MEMFN], D147 addendum 5: every search site migrates into the kit, under a
# checked manifest; integration.md §R4.3.4). `make test-memfn-manifest`.
#
# WHAT IT CHECKS: tests/memfn/site_manifest.tsv (one row per search or
# span-compare site, status `pending` or `delegated`) against what pcrec's
# emitters actually spell, read through tests/memfn/search_vocab.tsv (the
# search-form vocabulary C12 will share). The four rules and the manifest's
# own shape are in site_manifest_check.py's header. Static: it reads src/ and
# never runs build/pcrec, so it needs no build and takes about a second.
#
# THE INDEPENDENT CONTROLS (docs/dev/learnings.md §3):
#   - the vocabulary names no site and no function, and the manifest names
#     no text shape; rule 1 fails a form the manifest does not list, rule 4 a
#     listed emitter whose text the vocabulary does not see, so neither file
#     can drift into agreement with the other;
#   - rule 4 is also the vocabulary's REACH witness ([MECH-REACH]): a lexer
#     or vocabulary that stopped seeing forms reads as every pending row
#     stale, never as a quiet rule-1 pass;
#   - the row count's K35 floor is THIS literal, not a count of the TSV, so
#     a deleted row is red until someone lowers the floor on purpose. A
#     change that adds a manifest row raises it in the same commit.
#   - rule 2 (the dynamic half) is declared UNREACHED while no pcrec source
#     calls mf_emit_site, and turns into a FAIL the day one does.
#
# Usage: bash tests/memfn/run_site_manifest.sh [ROOT]
#   ROOT defaults to the tree this script sits in (the mech driver runs the
#   sabotaged tree's own copy, so the default is what it needs).

set -u

C17_ROW_FLOOR=13

here="$(cd "$(dirname "$0")" && pwd)"
root="${1:-$(cd "$here/../.." && pwd)}"

echo "== C17: the checked site manifest (tests/memfn/site_manifest.tsv) =="
python3 "$here/site_manifest_check.py" "$root" "$C17_ROW_FLOOR"
rc=$?
if [ "$rc" -ne 0 ] && [ "$rc" -ne 1 ]; then
    # the checker died before its totals: say so in the scraped form, so a
    # crash is never read as a clean run
    echo "FAIL: site_manifest_check.py exited $rc before reporting"
    echo "checks passed: 0"
    echo "checks failed: 1"
    exit 1
fi
exit "$rc"
