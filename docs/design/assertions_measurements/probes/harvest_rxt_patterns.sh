#!/bin/sh
# [M6.1]/R30 M6 — harvest the `.rxt` corpus's pattern population.
#
# THIS SCRIPT EXISTS BECAUSE THE DEFECT IT AVOIDS RECURRED AFTER BEING NAMED
# AND FIXED ONCE. R24 M-F1 (eng_brep) found that an uncommitted `sort -u`
# pipeline under a UTF-8 locale UNDERCOUNTS a corpus of regexes: en_US.UTF-8
# collation treats strings differing only in punctuation as equal, which for
# regexes — where punctuation IS the content — is close to a worst case. That
# lane fixed it with `LC_ALL=C` and recorded the lesson. This lane then
# reproduced the identical defect in its own uncommitted one-liner: the
# [M6.1] doc's first draft reported a population of 609 where the true figure
# is 1030.
#
# The lesson R30 drew, and the reason this file is committed rather than the
# knowledge written down: **a named defect is not a fixed defect; the fix must
# travel as tooling.** `LC_ALL=C` below is load-bearing, not tidiness.
#
# Usage: harvest_rxt_patterns.sh REPO_ROOT OUTFILE
set -e
ROOT=$1; OUT=$2

# LC_ALL=C: byte-ordering, byte-equality. Do not remove; see the header.
LC_ALL=C grep -h '^pattern ' "$ROOT"/tests/*/*.rxt 2>/dev/null \
  | LC_ALL=C sed 's/^pattern //' \
  | LC_ALL=C sort -u > "$OUT"

raw=$(LC_ALL=C grep -h '^pattern ' "$ROOT"/tests/*/*.rxt 2>/dev/null | wc -l)
uniq_c=$(wc -l < "$OUT")
uniq_utf8=$(LC_ALL=C grep -h '^pattern ' "$ROOT"/tests/*/*.rxt 2>/dev/null \
  | LC_ALL=C sed 's/^pattern //' | LC_ALL=en_US.UTF-8 sort -u | wc -l)

echo "raw 'pattern' lines            : $raw"
echo "distinct under LC_ALL=C        : $uniq_c   <- the population"
echo "distinct under en_US.UTF-8     : $uniq_utf8   <- what the defect reports"
echo "patterns the UTF-8 collation would have SILENTLY MERGED AWAY: $((uniq_c - uniq_utf8))"
