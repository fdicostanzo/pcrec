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
#   - rule 2 (the dynamic half) keys on `\bmf_(define|emit)\s*\(` (the kit's
#     API; `mf_emit_site` was a rev-3 name that names nothing) and counts the
#     sites rendered over a corpus compile pass against the `delegated` rows
#     (tests/memfn/site_census.py), through pcrec's door(s) to the builders
#     behind them. LIVE since R4c; it was declared UNREACHED, loudly, while no
#     pcrec source called the kit and no row was delegated; the machinery is
#     also proven on a synthetic caller every run (the `selftest:` lines).
#
# Usage: bash tests/memfn/run_site_manifest.sh [ROOT]
#   ROOT defaults to the tree this script sits in (the mech driver runs the
#   sabotaged tree's own copy, so the default is what it needs).

set -u

C17_ROW_FLOOR=14   # M7 (R-8, Q-R8-1): N7U split from N7; M6 (Q-R10-7): VMLAZY listed; D147 add. 12: N6 retired (not a search site), 15 -> 14; R-12 REPLACE (Q-R12-2): VMLAZY deleted (its instances are VMSPAN/VMSTRIDE's), 14 -> 13; R-12 (Q-R12-5): VALID listed, 13 -> 14

here="$(cd "$(dirname "$0")" && pwd)"
root="${1:-$(cd "$here/../.." && pwd)}"

echo "== C17: the checked site manifest (tests/memfn/site_manifest.tsv) =="
python3 "$here/site_manifest_check.py" "$root" "$C17_ROW_FLOOR" "${CC:-gcc}"
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
