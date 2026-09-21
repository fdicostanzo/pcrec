#!/usr/bin/env bash
# tests/rxtsource/run_rxtsource_tests.sh — [DD-13b.W1.1] INV-COMPAT.
#
# The question this section answers: does growing the `.rxt` format change
# what any EXISTING corpus file means? The corpus is 191 files, 3,325
# pattern blocks and 26,894 expectation lines, and none of them uses one
# byte of the new grammar — so the answer must be "no" in a way that a
# check can fail, not in a way a reader can believe.
#
# Design: docs/design/dd13_format/w1_impl.md §3 (and format_design.md
# §1.1, which states INV-COMPAT). Contract: docs/spec/rxt_format.md,
# docs/spec/table_contract.md.
#
# [DD-13b.W1.2], 2026-08-31 — WHAT THIS SECTION COSTS, RE-ADVERTISED.
# W1.1's header said "three parses of the corpus and no compiles at all",
# which is what kept it cheap enough to run beside `test-corpus`. That is
# no longer literally true: this file now COMPILES A HANDFUL OF TARGET
# FIXTURES (single digits — the three-config file's three targets, a few
# one-target files, and `run.sh` building the same three again through the
# H11 path, which also invokes the C compiler for their drivers).
#
# THE CORPUS HALF IS UNCHANGED and still compiles nothing: the three-way
# parse differential, C3's oracle re-run, C0a, the arm-block hash pin and
# the keyword census all still read the 191 files and compile none of
# them. The new cost is bounded by the FIXTURE count, not by the corpus,
# so it does not grow as the corpus does. docs/testing.md's tiered-testing
# entry for this section says the same thing.
#
# ---------------------------------------------------------------------
# WHAT IS HERE, AND WHAT IS DELIBERATELY NOT
#
# C1 (the parse differential), C3 (the oracle re-run), C0a (the composer
# was never invoked), the arm-block hash pin and the keyword census live
# here. **C2 — the ANSWER re-run — does not**: it is `run.sh` over the
# whole corpus reporting its own four summary numbers, which is exactly
# what `make test-corpus` already is. Re-running it here would double the
# most expensive section in the suite to assert numbers that section
# already asserts. What this file does instead is assert C2's
# DENOMINATORS, so a corpus that silently shrank cannot make either
# section's counts agree by both being small.
#
# ---------------------------------------------------------------------
# THE TWO DENOMINATORS DIFFER ON PURPOSE (w1_impl §3.0)
#
#   census (all files)         191 files / 3,325 blocks / 26,894 lines
#   tests/known_fail/k34...      1 file  /     3 blocks /     11 lines
#                              ---------------------------------------
#   run.sh's own population    178 files / 3,262 blocks / 26,680 lines
#
# [landing, 2026-09-02] The subtraction line above (178/3,262/26,680) does
# not equal census minus known_fail (which is 190/3,322/26,883) and was
# already wrong before this pin move — RUNSH_FILES/BLOCKS/LINES below are
# the values the code actually checks against, and they DO reconcile
# (see the reconciliation check's own PASS line). Left as found: fixing
# this prose mismatch is outside this pin move's scope and is flagged to
# the manager separately.
#
# `run.sh`'s no-argument branch discovers with `-not -path "*/known_fail/*"`,
# so the known-fail ratchet's own file is never dispatched. C1 is a PARSE
# differential and can and should read every file, so it asserts 191 and
# invokes leg B through the ARGUMENT branch (which applies no exclusion).
# C2 asserts 190. Asserting 191 in both would make the second one wrong.
#
# C3 asserts **verify_rxt's OWN discovery** and never either of the above:
# that script has no known_fail exclusion and its own skip rules, so
# carrying a denominator across from another check would be a number that
# looks authoritative because it came from somewhere else.
#
# ---------------------------------------------------------------------
# EVERY DENOMINATOR HERE IS ASSERTED, NOT ASSUMED
#
# The [DD-13c] lesson: without the denominators, the value comparison is
# vacuously true — three parsers agreeing about zero files agree
# perfectly. So the pinned census below is compared against a derivation
# that does not go through any of the three parsers under test (an awk
# pass over the raw bytes), and each leg's own row counts are compared
# against the pins.

set -u
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOT_DIR="$(cd "$ROOT_DIR/.." && pwd)"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"

PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
RUNSH="$ROOT_DIR/tests/harness/run.sh"
VERIFY="$ROOT_DIR/tests/harness/verify_rxt.py"

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-rxtsource.XXXXXX")"
trap 'rm -rf "$WORKDIR"' EXIT

checks_passed=0
checks_failed=0

pass() { checks_passed=$((checks_passed + 1)); echo "PASS: $*"; }
fail() { checks_failed=$((checks_failed + 1)); echo "FAIL: $*" >&2; }
# [DD-13b.W23.4] section_count SECTION FILE -> stdout: the number of DATA
# rows in a `--list-source` dump belonging to SECTION, where "" means the
# main table (before the first `#section` line). Every check in this file
# that used to count rows over a whole dump — sound only while no
# `#section` block existed at all — routes through this rather than
# growing its own copy of the same section-boundary tracking R5/R6 (above)
# already need.
section_count() {
    local want="$1" file="$2"
    awk -F'\t' -v want="$want" '
        /^#section /{ s=$0; sub(/^#section /,"",s); cur=s; next }
        $1 ~ /^#/ { next }
        cur == want { n++ }
        END { print n+0 }' "$file"
}
# record() — the tests/thread/run_stackdepth_tests.sh RECORD shape
# (2026-09-10): ran, outcome printed and COUNTED, but neither PASS nor
# FAIL claims anything about it. Used for comparisons whose pinned values
# are another box's numbers (the C3 population pins are the Linux
# reference's, per the BOX SENSITIVITY notes) — on that box they assert,
# here they are recorded so the population stays visible without
# fabricating a verdict from a pin that was never this box's to hold.
checks_recorded=0
record() { checks_recorded=$((checks_recorded + 1)); echo "RECORD: $*"; }

# ---------------------------------------------------------------------
# THE PINNED CENSUS.
#
# Provenance: docs/design/dd13_format/format_design.md §1.1 and
# w1_impl.md §1.7/§3.0, each derived independently (that note's own
# census, r44-grammar G1's recognizer, and an awk written from run.sh's
# arm list) and agreeing to the digit.
#
# THESE ARE PINS, NOT DERIVATIONS. They are compared below against a
# fresh awk pass, and the two must agree. When a corpus file is legitimately
# added or removed, THIS is what changes — deliberately, in a reviewed
# commit — and the failure message says so. A check that re-derived its
# own expectation would agree with a shrunk corpus by construction, which
# is this project's signature check-design failure (learnings §3).
# [ENG-ISL] 2026-09-03: +2/+21/+114 for tests/island/ (island.rxt 20 blocks
# 108 cells, island_caseless.rxt 1 block 6 cells) — the VM alternation
# island's answer corpus, every expectation produced by python3 `re`, so all
# 114 land in C3_PASS and NO skip bucket moves. That is the file's own claim
# rather than an accident: the axis is answer-identity-preserving, so a cell
# python cannot express would be a cell testing the wrong thing.
# [ART-SIZE] 2026-09-03: +0/+1/+10 for the class-leading witness-pool member
# appended to tests/counterk/counterk.rxt ((?:[ab]a|[ab]){8,12}+b, 4 m + 6 n).
# It is a CORPUS pattern because run_size_term.sh §9's pool must be corpus
# patterns; all 10 cells are python-expressible, so C3_PASS moves and no skip
# bucket does.
# 2026-09-05 (the manager, at the fifty-fourth session's three merges) —
# moved for: tests/base/cls_fold.rxt ([FORM-CHAR] STEP 1), the 13-file D27
# utf8 corpus under tests/utf8/ ([M5.0] stage 2, lane utfprom), and
# tests/known_fail/k49_utf8_lookbehind_retry.rxt (K49): +15 files. The SAME
# commit also fixes this script's own census derivation, which had been
# silently 0/0/0 on darwin (`xargs -a` has no BSD spelling — the identical
# bug utf8s2 fixed in run_mrl_tests.sh the same night), so the previous pin
# had been failing on this box for macport-era reasons, not corpus ones.
# 2026-09-05 (lane k49fix, K49 FIXED) — -1 file, +-0 blocks, +-0 lines. The
# ratchet file tests/known_fail/k49_utf8_lookbehind_retry.rxt is DELETED and
# its one block / one `ns` line is restored to its authored position in
# tests/utf8/axis09_nextpos_findall.rxt, an existing file. So the corpus loses
# a FILE and keeps the block and the expectation line: the two totals below are
# unchanged, and a reader who expects a fix to shrink the corpus should read
# the reconciliation below instead — what moved is which POPULATION the cell
# belongs to (known_fail -> run.sh's), not how many cells exist.
# 2026-09-05 (lane k49fix, K50 FILED) — +1/+1/+1 for
# tests/known_fail/k50_utf8_dfa_midchar_start.rxt, the DFA-side sibling K49's
# fix exposed (one `m` line). It lands under known_fail, so the census moves
# and RUNSH_* below does NOT — the opposite of the K49 movement one comment up,
# and the two together are why these pins are kept as a pair rather than one
# derived from the other.
# 2026-09-06 (lane k50bnd, K50 FIXED) — +-0 files, +4 blocks, +5 lines, and
# the arithmetic is worth writing out because THREE movements cancel into it.
# tests/known_fail/k50_utf8_dfa_midchar_start.rxt is DELETED (-1 file, -1
# block, -1 line) now that the DFA half is fixed and the ratchet fired on it;
# tests/utf8/axis11_startpos_boundary.rxt is NEW (+1 file, +7 blocks, +8
# lines); and tests/utf8/axis09_nextpos_findall.rxt loses its two
# mid-character-`startpos` blocks (+-0 files, -2 blocks, -2 lines), which move
# to tests/utf8/run_startbnd_diff.sh Sec 6 because no `.rxt` directive spells
# a compile flag. So the FILE count is unchanged for a reason — a retirement
# and an addition happening to cancel — and a reader who reads "no file
# movement" as "no corpus movement" has the wrong picture. RUNSH_* below moves
# by a DIFFERENT amount (+1 file, +5 blocks, +6 lines): the deleted file was
# under known_fail and the new one is not, which is exactly the
# opposite-directions case the k49fix comment above records.
# 2026-09-09 ([M5.0] stage 5, lane utf8s5) — +1 file, +30 blocks, +72 lines,
# and the SPLIT between the two pins is the informative part this time. The
# new file is `tests/utf8/axis12_scripts.rxt` (26 blocks, the SCRIPT
# properties, oracled from the 10.46 reference); the other +4 blocks are four
# `\p{Unknown}` spellings appended to `tests/known_fail/
# k53_uprops_oversize.rxt`, which is under known_fail and therefore moves
# CENSUS_* and NOT RUNSH_*. So RUNSH_* moves +1/+26/+66 where CENSUS_* moves
# +1/+30/+72 (axis12 is 26 blocks / 60 lines, the K53 addition 4 / 12) — the
# two are not the same delta and copying one into the other
# is how this pin has gone stale before.
# 2026-09-10 ([K53-SELRETRY], lane utf8k53) — -1 file, +0 blocks, +0 lines,
# and the TWO ZEROS are the informative part. K53 was fixed, so
# `tests/known_fail/k53_uprops_oversize.rxt` was DELETED and its sixteen
# blocks went back to their authored positions (twelve to
# tests/utf8/axis04_p_categories.rxt, four to tests/utf8/axis12_scripts.rxt).
# A block that MOVES between files moves neither pin; only the file count
# sees it. RUNSH_* below moves by a COMPLETELY DIFFERENT amount for exactly
# that reason (+0 files, +16 blocks, +56 lines): the sixteen ENTERED run.sh's
# population from known_fail's, while the file that left was never in it.
# **THIS PIN CAUGHT A REAL DEFECT IN THE MOVE ITSELF**, which is worth
# recording as the pin earning its keep: the lane's first attempt reported
# +4 blocks where the arithmetic said 0, because the splitter that cut the
# known_fail file into groups let its LAST group run to end-of-file and
# dragged the four `\p{Unknown}` script blocks into axis04 as duplicates.
# No test failed — the duplicates compiled and answered correctly. Only the
# census could see it.
# 2026-09-17 (lane cmtfix, [O-31 F1] the comment-escape fix) — +1 file, +2
# blocks, +6 lines for the new tests/base/comment_escape.rxt (two pattern
# blocks, three m/n lines each). Not under tests/known_fail/, so RUNSH_*
# below moves by the SAME +1/+2/+6.
# 2026-09-19 (lane adm71, item 4 -- [OPT-4.1] no-nullable-collapsed
# reachability witness) -- +1 file, +1 block, +6 lines for the new
# tests/base/opt41_rung_nullable_decline.rxt (one pattern block, six m
# lines). Not under tests/known_fail/, so RUNSH_* below moves by the SAME
# +1/+1/+6, and every one of the six cases is a plain python-expressible
# regex (`(?:ab){0,16000}`, nothing PCRE2-only), so C3_PASS below moves by
# the SAME +6 with no skip bucket moving.
# 2026-09-21 (lane adm0921, [K62] regression pins) — +1 file, +5 blocks,
# +16 lines for the new tests/quoting/k62_class_range_e.rxt (4 `pattern`
# blocks + 1 negative-control `pattern` block with a `perr`, 15 m/n case
# lines + 1 perr line, 0 g/gp lines). Not under tests/known_fail/, so
# RUNSH_* below moves by the SAME +1/+5/+16. Isolated verify_rxt.py run on
# the file alone (`python3 tests/harness/verify_rxt.py --file-timeout 10
# tests/quoting/k62_class_range_e.rxt`) reports PASS=1 (the one `perr`
# line — verified the same way any `perr` is, D26 provenance-only) and
# SKIP=15, all fifteen under `no-python-expression` (the class-range `\E`/
# `\Q\E` dissolution these blocks pin has no python `re` translation) —
# so C3_PASS below moves by +1 and C3_SKIP_NOPYTHON by +15, with every
# other C3_SKIP_* reason and C3_INFO/C3_STOREUNCOVERED/C3_TIMEOUT
# untouched (this file times out nothing and is not composed/pcre2-only/
# giveup/perr-accept/own-oracle/under-convention).
CENSUS_FILES=213
CENSUS_BLOCKS=3944
CENSUS_LINES=28971
# 2026-09-08 (bat4triage, [M5.0] stage 4 battery triage) — +1 file, +18
# blocks, +57 lines for tests/utf8/fold.rxt, NEW at the stage-4 merge
# (83f7175b, lane utf8s4/foldhunks) and never re-pinned there — the lane's
# own report (docs/dev/lanes/utf8s4_report.md) measures the file at 18
# blocks / 45 cells and does not mention this census. This pin's silent
# drift is what made the first post-merge full battery's test-rxtsource
# section red: `found 210/3906/28871, pinned 209/3888/28814` matches this
# file's addition exactly (verified by hand against the awk census, not
# re-derived from it). RUNSH_* below moves by the SAME amount: fold.rxt is
# not under tests/known_fail/.
# 2026-09-06 (lane utf8s3, [M5.0] stage 3) — +1 file, +0 blocks, +358 lines.
# THE BLOCK COUNT NOT MOVING IS THE INFORMATIVE PART: the D27-blinded
# `tests/utf8/axis04_p_categories.rxt` was PROMOTED (148 `perr` blocks became
# 136 live ones) and its twelve oversized blocks MOVED to a new file,
# `tests/known_fail/k53_uprops_oversize.rxt` — so blocks net zero while the
# file count and the line count both rise, the latter because a promoted
# block carries four `m`/`n` lines where a `perr` block carried one. RUNSH_*
# below moves by a DIFFERENT amount again (+0 files, -12 blocks, +314 lines):
# the twelve blocks left run.sh's population for known_fail's.
# 2026-09-02 — moved for [OPT-5] STEP 2's two corpus files
# (tests/base/start_pinned_startpos.rxt, tests/assertions/
# start_pinned_startpos.rxt): +2 files, +5 blocks, +95 lines.

# run.sh's own population: the census minus tests/known_fail/ (§3.0).
# Recorded here because C1 and C2 differ by exactly this file and a
# reader who assumes one population finds the 191/190 split inexplicable.
# 2026-09-17 (lane cmtfix, [O-31 F1]) — +1/+2/+6, the SAME delta as
# CENSUS_* above (comment_escape.rxt is not under tests/known_fail/).
# 2026-09-21 (lane adm0921, [K62]) — +1/+5/+16, the SAME delta as
# CENSUS_* above (tests/quoting/k62_class_range_e.rxt is not under
# tests/known_fail/).
RUNSH_FILES=212
RUNSH_BLOCKS=3941
RUNSH_LINES=28960
# 2026-09-10 ([K53-SELRETRY]) — +0/+16/+56 where CENSUS_* moved -1/+0/+0, the
# widest divergence this pair has shown. A known_fail file being RETIRED moves
# the two in different directions on every column: the census loses a file
# run.sh never counted, and run.sh gains the blocks and lines that file was
# holding. Deriving either from the other would have hidden both halves.
# 2026-09-08 (bat4triage) — moved alongside CENSUS_* above, same cause:
# +1/+18/+57, fold.rxt lands under tests/utf8/, not tests/known_fail/.
# 2026-09-06 (lane utf8s3) — see CENSUS_* above: the promotion moved twelve
# blocks OUT of run.sh's population and into known_fail's, so the file count
# is unchanged here while the census's rose.
# 2026-09-02 — moved alongside CENSUS_* above, same cause: +2/+5/+95,
# neither new file lands under tests/known_fail/.
# 2026-09-05 — moved alongside CENSUS_* above (the three-merge night);
# k49_utf8_lookbehind_retry.rxt lands under known_fail, hence the census
# and run.sh populations diverge by 2 files / 4 blocks / 12 lines now.
# 2026-09-05 (lane k49fix) — moved alongside CENSUS_* above, and this is the
# pair that MOVES when a known_fail file is retired: the census loses the file
# while run.sh GAINS its block and its line, so the two pins move in opposite
# directions and the divergence falls back to 1 file / 3 blocks / 11 lines
# (k34_leftrec_giveup.rxt alone). Deriving one of these from the other would
# have hidden exactly that.

echo "== [DD-13b.W1.1] .rxt source / INV-COMPAT =="

if [ ! -x "$PCREC" ]; then
    echo "FAIL: pcrec binary not found at $PCREC (run make first)" >&2
    exit 1
fi

# ---------------------------------------------------------------------
# THE FILE LIST — one `find`, used by every leg, so no two legs can
# disagree about the population by discovering it differently. LC_ALL=C
# on the sort is K35: under the ambient locale `sort` treats punctuation
# as ignorable and silently drops entries.
FILES="$WORKDIR/files.txt"
find "$ROOT_DIR/tests" -name '*.rxt' | LC_ALL=C sort > "$FILES"
nfiles=$(wc -l < "$FILES" | tr -d ' ')

# ---------------------------------------------------------------------
# CHECK 1 — the census, derived independently of all three parsers.
#
# This awk reads raw bytes and knows nothing about any parser under test.
# It is written from the FORMAT (docs/spec/rxt_format.md's line kinds),
# not from any of the three implementations, which is what makes it a
# control for all of them rather than a fourth voice agreeing with
# whichever it was copied from.
# xargs MAY split a long list across several awk invocations, and each
# would print its own END line. Summing the partials is what makes this
# safe: taking the first line would silently count a fraction of the
# corpus and then compare it against the pin, which is the "populations
# nobody counts" failure wearing a denominator.
read -r awk_files awk_blocks awk_lines <<EOF
$(xargs awk < "$FILES" '
    FNR == 1 { files++ }
    /^pattern[ \t]/ { blocks++; next }
    /^(m|n|ms|ns|gu|perr|g|gp)([ \t]|$)/ { lines++ }
    END { printf "%d %d %d\n", files+0, blocks+0, lines+0 }' \
  | awk '{ f += $1; b += $2; l += $3 } END { printf "%d %d %d\n", f, b, l }')
EOF

if [ "$awk_files" = "$CENSUS_FILES" ] && \
   [ "$awk_blocks" = "$CENSUS_BLOCKS" ] && \
   [ "$awk_lines" = "$CENSUS_LINES" ]; then
    pass "census: $awk_files files / $awk_blocks blocks / $awk_lines expectation lines (matches the pin)"
else
    fail "census MOVED: found $awk_files/$awk_blocks/$awk_lines, pinned $CENSUS_FILES/$CENSUS_BLOCKS/$CENSUS_LINES.
  If a corpus file was legitimately added or removed, update CENSUS_FILES /
  CENSUS_BLOCKS / CENSUS_LINES in this file AND the RUNSH_* values below
  (run.sh's population is the census minus tests/known_fail/), in a
  reviewed commit that says which file moved and why. Do NOT re-derive
  these numbers from the corpus: a pin that recomputes itself agrees with
  a shrunk corpus by construction."
fi

if [ "$nfiles" = "$CENSUS_FILES" ]; then
    pass "file list: $nfiles files (the population every leg below reads)"
else
    fail "file list: found $nfiles .rxt files, pinned $CENSUS_FILES"
fi

# ---------------------------------------------------------------------
# CHECK — §3.0's RECONCILIATION, which is what makes the two denominators
# a derivable relationship rather than an inconsistency somebody has to
# remember. run.sh's own population is the census minus tests/known_fail/,
# and 26,691 - 11 = 26,680 exactly. Asserting the SUBTRACTION rather than
# just the two totals is the point: if a known_fail file is added, both
# numbers move and only the relationship notices.
read -r kf_files kf_blocks kf_lines <<EOF
$(grep '/known_fail/' "$FILES" | tr '\n' '\0' | xargs -0 --no-run-if-empty awk '
    FNR == 1 { files++ }
    /^pattern[ \t]/ { blocks++; next }
    /^(m|n|ms|ns|gu|perr|g|gp)([ \t]|$)/ { lines++ }
    END { printf "%d %d %d\n", files+0, blocks+0, lines+0 }' \
  | awk '{ f += $1; b += $2; l += $3 } END { printf "%d %d %d\n", f+0, b+0, l+0 }')
EOF
kf_files=${kf_files:-0}; kf_blocks=${kf_blocks:-0}; kf_lines=${kf_lines:-0}

if [ "$((CENSUS_FILES - kf_files))" = "$RUNSH_FILES" ] && \
   [ "$((CENSUS_BLOCKS - kf_blocks))" = "$RUNSH_BLOCKS" ] && \
   [ "$((CENSUS_LINES - kf_lines))" = "$RUNSH_LINES" ]; then
    pass "denominators reconcile: census $CENSUS_FILES/$CENSUS_BLOCKS/$CENSUS_LINES minus known_fail's $kf_files/$kf_blocks/$kf_lines = run.sh's $RUNSH_FILES/$RUNSH_BLOCKS/$RUNSH_LINES"
else
    fail "denominators DO NOT reconcile: census $CENSUS_FILES/$CENSUS_BLOCKS/$CENSUS_LINES
  minus tests/known_fail/'s $kf_files/$kf_blocks/$kf_lines gives
  $((CENSUS_FILES - kf_files))/$((CENSUS_BLOCKS - kf_blocks))/$((CENSUS_LINES - kf_lines)),
  but run.sh's population is pinned at $RUNSH_FILES/$RUNSH_BLOCKS/$RUNSH_LINES.
  C1 reads all $CENSUS_FILES files and C2 reads run.sh's $RUNSH_FILES; the two
  differ by exactly the known-fail ratchet's own file, which run.sh's
  no-argument branch excludes. If that stopped being true, one of the two
  checks is now asserting a population it does not read."
fi

# ---------------------------------------------------------------------
# CHECK 2 — C0a, and it is TWO assertions from TWO SOURCES (§3.1's N4).
#
# The claim is "the composer was never invoked on the corpus". Revision 1
# of the design asserted a single 0 that an ABSENT composer would satisfy
# just as well as a correct one — empty-vs-empty. The two halves below are
# not the same kind of fact and neither alone is enough:
#
#   (a) an EXTERNAL count of how pcrec was actually invoked during a full
#       harness pass. This catches the machinery calling out when it
#       should not. It is taken by a WRAPPER around the binary rather than
#       by a counter inside run.sh, deliberately: a counter maintained by
#       the same script that decides whether to call cannot see a call
#       path that was never written, and shares a source with what it
#       counts.
#
#   (b) an INDEPENDENT CENSUS of head-bearing files in the corpus, by
#       scanning the raw bytes rather than by asking the harness. This is
#       what catches a future file growing a head without the rest of the
#       machinery, and it holds even if (a) is broken.
#
# A DISAGREEMENT BETWEEN THEM IS ITSELF A FAILURE: a head-bearing file
# with no invocation means the harness stopped making the call, and an
# invocation with no head-bearing file means it started making one it
# should not.
WRAPDIR="$WORKDIR/wrap"
mkdir -p "$WRAPDIR"
CALLLOG="$WORKDIR/pcrec-calls.log"
: > "$CALLLOG"
cat > "$WRAPDIR/pcrec" <<WRAP
#!/usr/bin/env bash
printf '%s\n' "\$*" >> "$CALLLOG"
exec "$PCREC" "\$@"
WRAP
chmod +x "$WRAPDIR/pcrec"

# ---------------------------------------------------------------------
# LEG B — run.sh --dump, through the ARGUMENT branch (§3.1's N2).
#
# The no-argument branch excludes tests/known_fail/ and yields 178; C1's
# population is 179. Leg B and C2 run the SAME script over DIFFERENT
# populations, deliberately. The row-count assertions below are the
# backstop: if this were ever invoked the default way its counts would
# fall short of the census and C1 goes red on the count, before anyone
# reads a diff.
DUMP_B="$WORKDIR/legB.tsv"
tB0=$(date +%s.%N)
if ! xargs "$TIMEOUT_BIN" 900 bash "$RUNSH" --dump \
        < "$FILES" > "$DUMP_B" 2> "$WORKDIR/legB.err"; then
    fail "leg B: run.sh --dump failed
$(head -20 "$WORKDIR/legB.err")"
fi
tB1=$(date +%s.%N)

# the same pass again, this time with the counting wrapper in PCREC, so
# (a) above measures a run that exercised the real head-detection path
: > "$CALLLOG"
PCREC="$WRAPDIR/pcrec" xargs "$TIMEOUT_BIN" 900 bash "$RUNSH" --dump \
    < "$FILES" > /dev/null 2>&1
ls_calls=$(grep -c -- '--list-source' "$CALLLOG" || true)

# (b) the independent census: a head-bearing file is one whose first
# non-blank, non-comment line's first token is not `pattern`. Derived
# here by awk over the raw bytes — no parser, no harness, no pcrec.
# (xargs -a has no BSD spelling; < "$FILES" is the portable form this
# script's own census derivation above already uses.)
head_files=$(xargs awk < "$FILES" '
    FNR == 1 { done = 0 }
    done { next }
    /^[ \t]*$/ { next }
    /^#/ { next }
    { done = 1; if ($1 != "pattern") { print FILENAME } }' | wc -l | tr -d ' ')

if [ "$ls_calls" = "0" ] && [ "$head_files" = "0" ]; then
    pass "C0a: --list-source invoked 0 times over the corpus, and 0 head-bearing files exist (two sources, agreeing)"
elif [ "$ls_calls" != "$head_files" ]; then
    fail "C0a: THE TWO SOURCES DISAGREE — pcrec was invoked with --list-source
  $ls_calls time(s), but the independent census finds $head_files head-bearing
  file(s). Either the harness stopped making a call it owes, or it started
  making one it does not. This disagreement is a failure in its own right,
  not merely a count being wrong."
else
    fail "C0a: expected 0 and 0, got $ls_calls invocation(s) / $head_files head-bearing file(s).
  A corpus file grew a head. That is not forbidden — but INV-COMPAT's
  argument is that the 179 files take a byte-identical code path, and it
  no longer holds unchanged."
fi

# ---------------------------------------------------------------------
# LEG A — pcrec --list-source, one invocation per file.
#
# ITS RUNTIME IS RECORDED, not assumed (w1_impl §7.4 risk 1). Each call
# is a parse with no compile, so it is bounded by parse cost — but the
# number was unmeasured until this check existed, and a differential that
# lands slowly becomes one a lane skips, which is worse than a slow check.
DUMP_A_RAW="$WORKDIR/legA.raw.tsv"
DUMP_A="$WORKDIR/legA.tsv"
: > "$DUMP_A_RAW"
tA0=$(date +%s.%N)
a_rc=0
while IFS= read -r f; do
    # the file name is prefixed as its own field by awk, not by sed: `\t`
    # in a sed replacement is a GNU extension, and a literal tab in the
    # script would be invisible to the next person to edit this line.
    if ! "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$f" \
            | awk -v f="$f" 'BEGIN { OFS = "\t" } { print f, $0 }' \
            >> "$DUMP_A_RAW"; then
        fail "leg A: pcrec --list-source failed on $f"
        a_rc=1
        break
    fi
done < "$FILES"
tA1=$(date +%s.%N)

# ---------------------------------------------------------------------
# THE FIELD MANIFEST (r45chk F3), because a differential can silently
# stop comparing.
#
# Both dumps are new code by one author. A change that dropped one
# directive key from BOTH emitters would leave C1 byte-identical while
# the differential quietly stopped covering that directive. So C1 asserts
# three things beyond byte-identity: the exact column NAMES pcrec emits,
# the exact field COUNT of every data row (the table contract's HEADER
# TRUTHFULNESS check), and the exact TOTAL row counts against the census.
MANIFEST='kind	line	name	value	pattern	flags	features	features_only	encoding	engine	budget_steps	budget_frames	with	from	pcrec	export	tags	oracle	esc	tune'
hdr="$("$TIMEOUT_BIN" 30 "$PCREC" --list-source "$(head -1 "$FILES")" | grep '^#kind')"
# [DD-13b.W23.4] MATCHES `^#kind` EXPLICITLY, never "the last `#` line":
# the main table's header used to be exactly that (`tail -1` over every
# `#` line), which stops working the moment a file's dump can carry
# `#section` blocks after it, each with its OWN `#col1\tcol2...` header —
# a `tail -1` would read a SECTION's header instead of the main table's,
# a false-positive MANIFEST failure. `#kind` is the one line this dump
# ever emits whose first field is that literal token.
hdr="${hdr#\#}"
if [ "$hdr" = "$MANIFEST" ]; then
    pass "C1 manifest: --list-source emits exactly the 20 pinned columns, in order"
else
    fail "C1 manifest: --list-source's header MOVED.
  expected: $MANIFEST
  got:      $hdr
  Columns are APPEND-ONLY under docs/spec/table_contract.md. If a column
  was legitimately appended, add it to MANIFEST here AND to the spec's
  column table in the same change — that is what keeps the producer and
  its checker from disagreeing silently (GENERATOR AGREEMENT)."
fi

ncols=$(printf '%s' "$MANIFEST" | awk -F'\t' '{print NF}')
# [DD-13b.W23.4] R5's REPAIR (w23_impl.md §1.5/§6.4 item 3). THE DEFECT:
# this assertion used to be "every non-comment row has exactly ncols+1
# fields", unconditionally of KIND — which the four `#section` blocks
# violate on every row, since a section's own width is never the main
# table's. THE REPAIR: the MAIN TABLE's rows are identified by the
# section boundary the STREAM ITSELF declares (`#section NAME` opens one,
# the file's own `#kind` header line — printed once per file — closes
# back to the main table), never by "every non-`#` row"; an unrecognised
# section name HARD-FAILS naming it rather than silently defaulting to
# the main table's width, because a detection helper that defaults on
# missing input fails in the silent direction ([ABI-NS]).
badfields=$(awk -F'\t' -v want="$ncols" '
    $2 == "#kind" { sect = ""; next }
    $2 ~ /^#section / { sect = $2; sub(/^#section /, "", sect); next }
    $2 ~ /^#/ { next }
    {
        expect = want
        if (sect == "provenance")     expect = 14
        else if (sect == "variants")  expect = 9
        else if (sect == "cases")     expect = 16
        else if (sect == "aux")       expect = 8
        else if (sect != "") {
            print FILENAME ": unknown #section '\''" sect "'\'' at: " $0
            n++
            next
        }
        if (NF != expect + 1) { print FILENAME ": " $0; n++ }
    }
    END { print "COUNT " n+0 }' "$DUMP_A_RAW" | tail -1 | awk '{print $2}')
if [ "$badfields" = "0" ]; then
    pass "C1 manifest: every --list-source row (main table and every section) has its own section's exact field count (header truthfulness)"
else
    fail "C1 manifest: $badfields --list-source row(s) do not have their section's expected field count.
  Either a field contained a TAB (the rxt-escape on the main table's
  columns 4, 5 and 15, and on the section columns escaped in
  docs/spec/rxt_format.md, exists to prevent this — three corpus blocks
  carry a literal tab in their pattern text, tests/base/bounded_repeats.rxt
  twice and tests/modifiers/xxmode.rxt once, and in every one the tab is
  the thing under test) or a row belongs to a section this check does not
  recognise."

fi

# leg A is one row per DECLARATION and per BLOCK. On this corpus there
# are no head declarations at all, so every MAIN-TABLE row must be a
# `pattern` row — a THIRD view of C0a's zero, from pcrec's own output
# this time. [DD-13b.W23.4] R6's REPAIR (w23_impl.md §1.5, r59-A1): this
# used to count EVERY non-comment row whose field 2 is not `pattern` —
# an INEQUALITY reader, which every `#section cases` row satisfies (its
# own field 2 is `block_line`, an integer, never the string `pattern`),
# so a green W23-S4 (below) would PROVE this counter broken. The repair
# is the SAME section-boundary tracking R5 now uses: count only rows
# inside the main table (`sect == ""`).
a_head_rows=$(awk -F'\t' '
    $2 == "#kind" { sect = ""; next }
    $2 ~ /^#section / { sect = $2; sub(/^#section /, "", sect); next }
    $2 ~ /^#/ { next }
    sect == "" && $2 != "pattern" { n++ }
    END { print n+0 }' "$DUMP_A_RAW")
a_blocks=$(awk -F'\t' '
    $2 == "#kind" { sect = ""; next }
    $2 ~ /^#section / { sect = $2; sub(/^#section /, "", sect); next }
    $2 ~ /^#/ { next }
    sect == "" && $2 == "pattern" { n++ }
    END { print n+0 }' "$DUMP_A_RAW")
if [ "$a_head_rows" = "0" ]; then
    pass "C1: leg A emitted 0 head-declaration rows (pcrec's own view of C0a)"
else
    fail "C1: leg A emitted $a_head_rows head-declaration row(s); the corpus has no head"
fi
if [ "$a_blocks" = "$CENSUS_BLOCKS" ]; then
    pass "C1: leg A emitted $a_blocks block rows (matches the census)"
else
    fail "C1: leg A emitted $a_blocks block rows, census is $CENSUS_BLOCKS —
  the differential is comparing a population that is not the corpus"
fi

# ---------------------------------------------------------------------
# [DD-13b.W23.4] item 3b: A SYNTHETIC STREAM EXERCISING BOTH REPAIRED
# ARMS (r59-A-M3, w23_impl.md §6.4). At THIS commit's own pin no real
# corpus file carries a W23 production (census unchanged, $CENSUS_BLOCKS
# above), so the two repairs above land UNEXERCISED by the corpus
# itself — a check nobody can distinguish from a check that was not
# written. This is a hand-written `--list-source`-shaped stream (never
# real `pcrec` output) through the SAME two awk scripts, at a section
# width that DIFFERS FROM 16 (`#section cases` is ALSO 16 — a
# width-blind repair would pass a `cases`-only control by coincidence;
# `#section aux` is 8 and is the control here).
SYNTH="$WORKDIR/synth_a_raw.tsv"
{
    printf 'f.rxt\t#kind\tline\tname\tvalue\tpattern\tflags\tfeatures\tfeatures_only\tencoding\tengine\tbudget_steps\tbudget_frames\twith\tfrom\tpcrec\texport\ttags\toracle\tesc\n'
    # 20 fields: the file prefix + all 19 main-table columns (kind..esc).
    awk 'BEGIN {
        OFS = "\t"
        $1 = "f.rxt"; $2 = "pattern"; $3 = "1"; $6 = "a"; $20 = ""
        print
    }'
    printf 'f.rxt\t#section aux\n'
    printf 'f.rxt\t#line\tblock_line\tblock_name\tconsumer\tdepth\tkey\tvalue\tparent_line\n'
    # 9 fields: the file prefix + all 8 aux columns.
    awk 'BEGIN {
        OFS = "\t"
        $1 = "f.rxt"; $2 = "2"; $3 = "1"; $5 = "bench"; $6 = "0"
        $7 = "ext"; $8 = "bench"; $9 = ""
        print
    }'
} > "$SYNTH"
synth_bad=$(awk -F'\t' -v want=19 '
    $2 == "#kind" { sect = ""; next }
    $2 ~ /^#section / { sect = $2; sub(/^#section /, "", sect); next }
    $2 ~ /^#/ { next }
    {
        expect = want
        if (sect == "aux") expect = 8
        if (NF != expect + 1) n++
    }
    END { print n+0 }' "$SYNTH")
synth_head=$(awk -F'\t' '
    $2 == "#kind" { sect = ""; next }
    $2 ~ /^#section / { sect = $2; sub(/^#section /, "", sect); next }
    $2 ~ /^#/ { next }
    sect == "" && $2 != "pattern" { n++ }
    END { print n+0 }' "$SYNTH")
if [ "$synth_bad" = "0" ] && [ "$synth_head" = "0" ]; then
    pass "C1 synthetic control: R5/R6's repaired arms both read this section-bearing stream correctly (0 bad-width rows, 0 spurious head rows)"
else
    fail "C1 synthetic control: the repaired arms misread a section-bearing stream —
  bad-width rows: $synth_bad (want 0), spurious head rows: $synth_head (want 0).
  This is a HAND-WRITTEN stream, not real pcrec output — if it fails, the
  repair above is wrong, not the corpus."
fi

# ---------------------------------------------------------------------
# LEG C — verify_rxt.py --dump, the third parser: python, a different
# author, already in the tree before any of this was designed. It is what
# makes C1 a control for the BODY rather than a comparison of pcrec
# against itself. (The HEAD has exactly one parser by the seam ruling, and
# §3.1 says plainly that it therefore has no differential control; what
# covers it is the grammar's refusals, the manifest above, and the fact —
# asserted twice — that on this corpus the head is empty.)
DUMP_C="$WORKDIR/legC.tsv"
tC0=$(date +%s.%N)
if ! xargs "$TIMEOUT_BIN" 900 python3 "$VERIFY" --dump \
        < "$FILES" > "$DUMP_C" 2> "$WORKDIR/legC.err"; then
    fail "leg C: verify_rxt.py --dump failed
$(head -20 "$WORKDIR/legC.err")"
fi
tC1=$(date +%s.%N)

# ---------------------------------------------------------------------
# THE PROJECTIONS, stated rather than implied.
#
# The three legs do not know the same things, and pretending they do
# would either weaken the comparison to the intersection of everything or
# make it fail on facts one leg cannot have. So each pairwise comparison
# names its own projection:
#
#   A knows head declarations and every block directive. It does NOT read
#     expectation lines at all — a compiler that started scoring `m` lines
#     would be a second harness.
#   B knows blocks, directives, expectations, and `perr`.
#   C knows blocks, directives, expectations, and `perr`.
#
#   A vs B: block rows, columns 1..12 (drop `perr`, which A cannot know).
#   B vs C: block rows in full, plus every case row.
PROJ_A="$WORKDIR/projA.tsv"
PROJ_B12="$WORKDIR/projB12.tsv"
PROJ_B="$WORKDIR/projB.tsv"
PROJ_C="$WORKDIR/projC.tsv"

# A: <file>\t<16 cols> -> block <file> <line> <name> <desc> <pat> <flags>
#    <features> <only> <encoding> <engine> <steps> <frames> <export>
#
# [DD-13b.W1.3] BOTH SIDES NOW SELECT FIELDS EXPLICITLY rather than one of
# them truncating with `NF = 13`. `export` was APPENDED to leg B's row (after
# `perr`, which leg A cannot know and which this comparison has always
# dropped), so a truncation would have dropped `export` too — and a directive
# absent from both sides of a differential leaves it byte-identical while it
# quietly stops covering that directive, which is the hazard this file's own
# manifest comment names. Selecting is one line longer and cannot do that.
awk -F'\t' -v OFS='\t' '$2 == "pattern" {
    print "block", $1, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $17 }' \
    "$DUMP_A_RAW" > "$PROJ_A"

awk -F'\t' '$1 == "block" {
    printf "%s", $1
    for (i = 2; i <= 13; i++) printf "\t%s", $i
    printf "\t%s\n", $15 }' "$DUMP_B" > "$PROJ_B12"
cp "$DUMP_B" "$PROJ_B"
cp "$DUMP_C" "$PROJ_C"

if [ "$a_rc" = "0" ] && diff -u "$PROJ_A" "$PROJ_B12" > "$WORKDIR/ab.diff"; then
    pass "C1 leg A == leg B: pcrec --list-source and run.sh --dump agree byte for byte on $a_blocks blocks"
else
    fail "C1 leg A != leg B — pcrec's parser and run.sh's disagree about what the corpus says:
$(head -40 "$WORKDIR/ab.diff")"
fi

if diff -u "$PROJ_B" "$PROJ_C" > "$WORKDIR/bc.diff"; then
    pass "C1 leg B == leg C: run.sh --dump and verify_rxt.py --dump agree byte for byte"
else
    fail "C1 leg B != leg C — run.sh's parser and verify_rxt.py's disagree:
$(head -40 "$WORKDIR/bc.diff")"
fi

b_blocks=$(awk -F'\t' '$1 == "block" { n++ } END { print n+0 }' "$DUMP_B")
b_cases=$(awk -F'\t' '$1 == "case" { n++ } END { print n+0 }' "$DUMP_B")
c_blocks=$(awk -F'\t' '$1 == "block" { n++ } END { print n+0 }' "$DUMP_C")
c_cases=$(awk -F'\t' '$1 == "case" { n++ } END { print n+0 }' "$DUMP_C")

# HOW MANY `case` ROWS THE DUMPS OWE, and it is a DERIVATION rather than
# a fourth pin, because two pins that must differ by a third quantity are
# two chances to be wrong about it.
#
# Not every expectation line is a case row, and the two ways it can fail
# to be one are different:
#   `perr`      is a BLOCK field in both dumps — a perr block has no
#               m/n lines and the pattern text is the whole test;
#   `g` / `gp`  are FOLDED into the preceding m/ms case's gspec, which is
#               how run.sh models them (they attach to a case, they are
#               not cases).
# So the case rows are the five kinds that carry a subject. This awk is
# the same independent pass the census uses, and the RECONCILIATION below
# is what makes it a check rather than a restatement: if the five kinds,
# the perr lines and the g/gp lines do not add back up to the census, one
# of the two counts is wrong and neither is trusted.
read -r kind_cases kind_perr kind_group <<EOF
$(xargs awk < "$FILES" '
    /^(m|n|ms|ns|gu)([ \t]|$)/ { c++; next }
    /^perr([ \t]|$)/           { p++; next }
    /^(g|gp)([ \t]|$)/         { g++ }
    END { printf "%d %d %d\n", c+0, p+0, g+0 }' \
  | awk '{ c += $1; p += $2; g += $3 } END { printf "%d %d %d\n", c, p, g }')
EOF
want_cases=$kind_cases
perr_lines=$kind_perr

if [ "$((kind_cases + kind_perr + kind_group))" = "$CENSUS_LINES" ]; then
    pass "case-row derivation reconciles: $kind_cases subject-bearing + $kind_perr perr + $kind_group g/gp = $CENSUS_LINES expectation lines"
else
    fail "case-row derivation DOES NOT reconcile: $kind_cases + $kind_perr + $kind_group
  = $((kind_cases + kind_perr + kind_group)), but the census is $CENSUS_LINES.
  These are two passes over the same bytes with different line-kind
  patterns; a disagreement means one of them has stopped describing the
  format, and the case-row count below cannot be trusted either way."
fi

check_counts() {
    local leg=$1 bl=$2 ca=$3
    if [ "$bl" = "$CENSUS_BLOCKS" ]; then
        pass "C1: leg $leg emitted $bl block rows (matches the census)"
    else
        fail "C1: leg $leg emitted $bl block rows, census is $CENSUS_BLOCKS"
    fi
    if [ "$ca" = "$want_cases" ]; then
        pass "C1: leg $leg emitted $ca case rows (the subject-bearing kinds; census $CENSUS_LINES minus $perr_lines perr and $kind_group g/gp)"
    else
        fail "C1: leg $leg emitted $ca case rows, expected $want_cases
  (the five subject-bearing kinds: the census's $CENSUS_LINES expectation
  lines minus $perr_lines \`perr\` — a BLOCK field in both dumps — and minus
  $kind_group \`g\`/\`gp\`, which FOLD into the preceding case's gspec)"
    fi
}
check_counts B "$b_blocks" "$b_cases"
check_counts C "$c_blocks" "$c_cases"

# ---------------------------------------------------------------------
# C1's RUNTIME — an OUTPUT of this check, not an assumption about it.
tA=$(awk -v a="$tA0" -v b="$tA1" 'BEGIN { printf "%.1f", b - a }')
tB=$(awk -v a="$tB0" -v b="$tB1" 'BEGIN { printf "%.1f", b - a }')
tC=$(awk -v a="$tC0" -v b="$tC1" 'BEGIN { printf "%.1f", b - a }')
echo "C1 runtime: leg A (${CENSUS_FILES}x pcrec --list-source) ${tA}s; leg B (run.sh --dump) ${tB}s; leg C (verify_rxt.py --dump) ${tC}s"

# ---------------------------------------------------------------------
# CHECK — C3, the oracle re-run, over verify_rxt's OWN discovery.
#
# Until this step, `verify_rxt.py`'s `main()` was invoked by NOTHING in
# the tree: its only Makefile mention is a comment, and its directory
# discovery was a ONE-LEVEL glob, so the obvious wiring
# (`verify_rxt.py tests`) matched `tests/*.rxt` — of which there are none
# — verified ZERO files and exited reporting success. That is the shape
# this call refuses to have.
#
# The list comes from `find` and the FLOOR is the pinned census, passed
# in from here. The two do not share a source: a discovery that narrows
# is measured against a number that did not come from the discovery.
# THE ORACLE'S OWN TOTALS, PINNED. Provenance: the first corpus-wide run
# of this script, 2026-08-30 (W1.1). Every number below is a POPULATION,
# and each one is here because a population nobody counts is not a
# population — a skip reason that silently grows is coverage silently
# lost.
C3_FILES=179
# [M4-QUOTING] 2026-08-31: +7/+88/+88 for tests/quoting/d27/ (95 cells).
# The 88 new no-python-expression skips are the POINT, not lost coverage:
# python `re` has no \Q at all, so the module's cells are inexpressible
# here by nature — their oracle is libpcre2 via tests/quoting/d27/
# checker.py (95/95 at landing), and the 7 python-expressible cells are
# the corpus's own (?x)/plain controls, verified here like any other.
# [OPT-5]/S215 2026-08-31: +8 for tests/classes/multi_chain.rxt — all eight
# cells are python-expressible and verified here like any other.
# [landing, 2026-09-02] +95 for [OPT-5] STEP 2's two corpus files
# (tests/rxtsource header note above has the file names). The split is NOT
# even: tests/base/start_pinned_startpos.rxt's 79 lines are ordinary
# python-expressible patterns and land in PASS; tests/assertions/
# start_pinned_startpos.rxt's 16 lines (a \b pattern) land in
# own-oracle — not because \b itself is python-inexpressible (tests/
# assertions/CLAUDE.md says \b IS python-verified cell for cell), but
# because `declares_own_oracle` (tests/harness/verify_rxt.py) skips EVERY
# file under a directory that carries its own verify_*.py, and
# tests/assertions/ has verify_pcre2.py. So +79 PASS, +16 SKIP, all +16
# landing in own-oracle; every other reason is unchanged.
# [M5.0 utfprom re-pin, 2026-09-05] +435 PASS / +959 SKIP for the promoted
# D27 utf8 corpus (tests/utf8/, 523 blocks, merge 698eea61) — caught by
# the first full battery after the merge, not at the merge itself (the
# light local tier never ran this section). The skip growth decomposes
# exactly: +909 pcre2-only (U14 — verify_rxt.py's subject decoder is
# byte-oriented, so the corpus's non-ASCII-subject blocks carry
# `# pcre2-only` and their oracle is the libpcre2 differential owed as a
# corpus follow-up) and +50 no-python-expression; every other reason
# is unchanged. NOT lost coverage: the pcre2-only marks were COMPUTED by
# the blinded author's oracle run, and the 435 python-expressible cells
# are verified here like any other.
# BOX SENSITIVITY, FIRST SEEN AT THIS RE-PIN: C3_SKIP_NOPYTHON is now
# python-VERSION-sensitive — the utf8 corpus holds 16 expectations that
# python 3.14 (ubuntubudu, the reference box) can express and python 3.11
# (the Mac's) cannot, so the Mac reads PASS 13861 / SKIP 14500 /
# no-python-expression 1907 against the pins below. The pins are the
# REFERENCE BOX's numbers (Linux, where the battery must be green); the
# local delta is catalogued in the darwin admin slice (wake.md) beside
# this section's other known local reds.
# [K49/K50 re-pin, 2026-09-05 evening] -1 PASS / +2 SKIP (+2 pcre2-only):
# the K49 merge restored its cell into tests/utf8/axis09 and filed K50's
# new known_fail regression (verify_rxt has NO known_fail exclusion, so
# both count here). The lane re-pinned the census pair and could not see
# C3 move — C3 is deliberately red on its own box (the delta above) — so
# the reference-box re-pin lands here, from the Linux re-run's own
# numbers at the merge commit.
# [ntriage re-pin, 2026-09-08] -148 PASS / +511 SKIP (+511 pcre2-only), from
# EVERY corpus edit landed since the 0c34f5e0 pin above through the
# [M5.0] stage 3 merge (819ec889) -- the [K50-BNDSTART]/[K50-NULLGATE] lane
# merges sit chronologically BETWEEN those two commits (K50 was fixed and
# stage 3 launched only after), so this is the pin's first re-run since
# BOTH landed, not stage 3 alone. Derived per-file, not copied from the
# battery log, and confirmed to sum to the Linux run's exact "got" numbers
# (PASS 13728, SKIP 14997, pcre2-only 2779):
#   axis04_p_categories.rxt (stage 3 promotion, 6798b9ec): 148 `perr` blocks
#     (each an agreeing "both engines refuse \p" PASS, since python also
#     raises re.error on \p{...} with no gate to open) became 136 live
#     `# pcre2-only` blocks (462 m/n lines) plus 12 blocks moved verbatim to
#     tests/known_fail/k53_uprops_oversize.rxt (44 m/n lines, also
#     `# pcre2-only`, counted here because verify_rxt.py has no known_fail
#     exclusion) -> -148 PASS, +506 pcre2-only/SKIP.
#   axis09_nextpos_findall.rxt (K50 fix, 8e0fe77f): the two now-invalid
#     mid-character `ms` cells (`(?<!.)`/`(?!.)` at startpos=1, both
#     `# pcre2-only`) were REMOVED -- the boundary guard refuses that
#     startpos now, so the cells assert nothing reachable -- with a comment
#     pointing at their replacement, run_startbnd_diff.sh Sec 6, which
#     sweeps the same positions under `-fno-startpos-guard` -> -2
#     pcre2-only/SKIP, RELOCATED not lost.
#   tests/known_fail/k50_utf8_dfa_midchar_start.rxt (K50 fix): DELETED -- its
#     one `# pcre2-only` cell was K50's own bug witness, obsolete once fixed
#     -> -1 pcre2-only/SKIP.
#   axis11_startpos_boundary.rxt (K50 fix, NEW file): K50's regression proof,
#     7 pattern blocks / 8 cases, all `# pcre2-only` (libpcre2-oracle-backed,
#     this directory's standing reason -- U14) -> +8 pcre2-only/SKIP.
#   Net: -148 PASS; 506-2-1+8 = +511 SKIP, all of it in the pcre2-only
#   bucket; every other C3_SKIP_* reason is unchanged (no `gu`/composed/
#   own-oracle/no-python-expression population moved by any of these edits
#   -- pcre2-only is checked before kind dispatch, so it swallows perr/ms/ns
#   lines identically to m/n).
#   NOT LOST COVERAGE: axis04's -148 PASS were trivial refusal-agreements
#   (the module wasn't wired; both sides merely declined \p); the 506
#   replacing them are real membership assertions checked by a STRONGER
#   oracle this python run cannot run at all (tests/uprops/'s whole-code-
#   point-space libpcre2 differential, 0 divergences at landing). The
#   axis09/known_fail movement is a relocation to a purpose-built
#   differential (run_startbnd_diff.sh), not a deletion of a checked claim.
#   axis11 is net new coverage (K50's own regression proof). VERIFIED
#   LOCALLY (darwin): CENSUS_FILES/BLOCKS/LINES and RUNSH_* already correct
#   (re-pinned by lane utf8s3, 0b314761) -- this commit's own C3 arithmetic
#   is confirmed by hand against the file diffs above, not by a local C3
#   run (C3 is deliberately red on this box, see the BOX SENSITIVITY note
#   above); the Linux re-validation OWED is the manager's, see
#   docs/dev/lanes/ntriage_report.md.
# 2026-09-08 (bat4triage): C3_PASS/C3_SKIP/etc. below are NOT re-pinned for
# tests/utf8/fold.rxt (stage 4, 18 blocks / 45 cells, 19 `# pcre2-only`
# comment lines counted in the file -- not all 45 cells are necessarily
# python-PASS). Every prior re-pin of this block was taken from a Linux
# reference run, never derived by hand on this box (C3 is deliberately red
# here -- see above), and this lane could not run one. OWED to whoever runs
# the 10.46/Linux arm next: re-pin C3_PASS/C3_SKIP/C3_SKIP_* from that run
# at a commit including fold.rxt, alongside CENSUS_FILES=210 above.
# [arm61fix re-pin, 2026-09-09] -20 PASS / +77 SKIP (+93 pcre2-only, -16
# no-python-expression), from the I-61 Linux executor run's authoritative
# numbers (PASS 13708, SKIP 15074, pcre2-only 2872), discharging the OWED
# note above. Derived per file against the two stage-4 commits bat4triage's
# note names (83f7175b, lane utf8s4/foldhunks), NOT copied from the Linux
# log -- confirmed by running verify_rxt.py in isolation against a
# pre-image/post-image pair of each touched file on this box (python
# version affects EXPRESSIBILITY counts elsewhere in the corpus, per the
# BOX SENSITIVITY note above, but every construct this re-pin turns on is a
# fixed compile-or-not fact under any python 3.x, so the isolated-file
# deltas measured here equal the Linux run's):
#
#   tests/utf8/fold.rxt (ab5c9715's sibling commit a3ba7de7, NEW file,
#   every one of its 18 blocks authored `# pcre2-only` from the start --
#   the file's own header says why, U14): all 45 lines land in SKIP, all
#   45 as pcre2-only, 0 as PASS, 0 moved out of any other reason.
#   Measured in isolation (verify_rxt.py on the file alone):
#   PASS=0, SKIP=45 (pcre2-only=45, all others 0).
#   -> +0 PASS / +45 SKIP / +45 pcre2-only / +0 no-python-expression.
#
#   tests/utf8/axis06_caseless_fold.rxt (commit ab5c9715, "PROMOTED to its
#   recorded oracle", 48 blocks both before and after -- no block count
#   movement, so every line below is a RECLASSIFICATION or a same-block
#   line-count change, never a new/removed block). Twelve of its 48 blocks
#   were NOT marked `# pcre2-only` before this commit and ALL TWELVE
#   gained the marker here (measured: `grep -c '^# pcre2-only'` 36 -> 48);
#   the other 36 blocks were already marked and their value edits (the
#   KELVIN/MICRO/LONGS/FINALSIGMA/closure-class families restoring the
#   recorded PCRE2_UTF|PCRE2_CASELESS answers) move zero C3 lines, because
#   a block already in the pcre2-only bucket stays there regardless of
#   what its m/n lines say. Of the twelve newly-marked blocks:
#     - 4 are `[^k]`/`[^K]`/`[^s]`/`[^S]` (bare-literal negated singleton,
#       4 lines each = 16 lines): python's `re` compiles these fine (a
#       plain ASCII class under IGNORECASE|ASCII), so pre-promotion they
#       were PASS. Now pcre2-only. -16 PASS, +16 pcre2-only.
#     - 4 are `[^\x{6b}]`/`[^\x{4b}]`/`[^\x{73}]`/`[^\x{53}]` (the SAME
#       four codepoints spelled with PCRE's `\x{NN}` brace escape, 4 lines
#       each = 16 lines): python's `re` has no brace form of `\x` (it wants
#       exactly `\xHH`) and raises `bad escape` at compile time, so
#       pre-promotion these were no-python-expression, not PASS. Now
#       pcre2-only. -16 no-python-expression, +16 pcre2-only.
#     - 4 are the `negate-neg-Ll{,-dup1,-dup2,-dup3}` blocks: `[^\p{Ll}]`,
#       pre-promotion a single `perr` line each (4 lines total) that
#       PASSED as an agreeing refusal (python's `re` also raises on `\p`,
#       same reasoning as axis04's stage-3 `\p` `perr` population). The
#       commit promotes each to 4 real m/n lines (16 lines total) and
#       marks the block pcre2-only in the same edit (the recorded oracle
#       was wrong on 2 of the 4 cells -- see the file's own inline
#       correction -- which is irrelevant to this census/skip arithmetic
#       since the whole block lands in pcre2-only either way). -4 PASS,
#       +16 pcre2-only, and +12 net NEW lines (16 - 4), which is exactly
#       this file's own line-count growth (180 -> 192, matches the
#       existing CENSUS_LINES pin's derivation -- unaffected by this
#       re-pin, see the [M5.0 utfprom]/[bat4triage] notes above).
#   Net for this file, reason by reason: PASS loses the 16 bare-literal
#   lines and the 4 perr lines (-20); no-python-expression loses its whole
#   pre-existing population, the 16 brace-escape lines (-16); pcre2-only
#   gains all of it back plus the Ll blocks' 12 net-new lines
#   (16+16+16+12 = +48). SKIP is pcre2-only plus no-python-expression
#   together, so its net is +48-16 = +32 -- the no-python-expression loss
#   stays inside SKIP (it moves to a different SKIP reason, it does not
#   leave SKIP), and only the PASS-to-SKIP crossing (-20 PASS) plus the
#   Ll blocks' brand-new lines (+12) actually change the SKIP total,
#   which is the same +32. Measured in isolation (verify_rxt.py on a
#   pre-image/post-image pair of the file alone, at the two commits
#   either side of ab5c9715) rather than trusted from the hand count:
#   PASS 20 -> 0 (-20), SKIP 160 -> 192 (+32: pcre2-only 144 -> 192 = +48,
#   no-python-expression 16 -> 0 = -16, every other reason unchanged at 0)
#   -- agrees with the hand derivation above exactly.
#
#   Sum across both files: -20-0 = -20 PASS; +32+45 = +77 SKIP;
#   +48+45 = +93 pcre2-only; -16+0 = -16 no-python-expression. Exactly the
#   deltas below, and C3_PASS+C3_SKIP+C3_TIMEOUT_FILE_LINES =
#   13708+15074+89 = 28871 = CENSUS_LINES, so the whole corpus still
#   reconciles. giveup/composed/perr-python-accepts/own-oracle are
#   untouched by either commit (measured 0 movement in both isolated
#   runs) and are NOT re-pinned here.
# [pyrole re-pin, 2026-09-10/11] +0 PASS / +0 SKIP (every SKIP_* reason
# unchanged) / NEW: C3_INFO=0, C3_STOREUNCOVERED=0 -- verify_rxt.py's C3
# tier gained a THIRD verdict (docs/design/c3_three_way.md): a python-vs-
# expectation disagreement the COMMITTED oracle store (`oracle_store/
# libpcre2-10.48/`, `tests/rxtsource/build_c3_store.py`) CONFIRMS is right
# is counted INFO, never FAIL. This box's default `python3` (3.9.6) found
# SEVEN cells red before this change (tests/backrefs/d27/caseless.rxt:39,
# tests/counterk/counterk.rxt:568/626/644/702, tests/lookaround/
# captures.rxt:59/67) -- all seven CONFIRMED by the store (PCRE2 agrees
# with the expectation; python alone was wrong), all seven now INFO, so
# THIS BOX's own C3 run moves FAIL 7 -> 0, INFO 0 -> 7, with PASS/SKIP/
# every SKIP_* reason UNCHANGED (measured: identical PASS=12729/
# SKIP=16107 before and after, isolated per-file runs on the three touched
# files agree with the whole-corpus run).
#
# THE PINS BELOW ARE UNCHANGED FROM THEIR PRIOR VALUES, and C3_INFO/
# C3_STOREUNCOVERED are pinned at 0 -- NOT this box's own 7/0, and this is
# a DERIVATION, not a guess: two of the three divergence mechanisms
# (lazy-counted-alternation capture timing, negative-lookahead capture
# retention) are CPython `re`-engine behaviour that changed between 3.9 and
# 3.11 -- MEASURED directly on this box with `python3.10`/`python3.11`
# installs also present here (miniconda's 3.11, homebrew's 3.10): under
# EITHER, all six counterk/lookaround cells already agree with the
# expectation with NO store consultation needed, and the seventh
# (caseless.rxt:39, a non-leading global `(?i)`) compiles under 3.9's
# DeprecationWarning-and-proceed behaviour but RAISES `re.error` under
# 3.10/3.11 (`re.compile` treats it as a syntax error, "global flags not at
# the start of the expression"), landing in skipped_no_python instead of a
# comparison at all. This section's own BOX SENSITIVITY note above already
# establishes the reference box runs python 3.14, strictly newer than
# 3.11 -- so on the reference box this lane's whole seven-cell population
# was NEVER a divergence to begin with: C3_INFO=0 there is the honest
# reference-box number, and this box's own INFO=7 is a LOCAL, older-python
# artifact the mechanism exists to absorb WITHOUT pinning a python version.
# VERIFIED LOCALLY (darwin, all three python versions cited above); the
# Linux/reference re-run to CONFIRM C3_INFO=0/C3_STOREUNCOVERED=0 there is
# OWED to whoever runs it next (this section's own established pattern for
# a box this lane cannot reach without a suite-scale run).
#
# A SEPARATE, PRE-EXISTING GAP THIS RE-PIN NEWLY EXPOSES RATHER THAN
# CAUSES: the population-pin comparison below (PASS/SKIP/SKIP_* against
# their Linux-reference pins) only RUNS when `verify_rxt.py` exits 0 (zero
# FAILURES) -- before this lane, the seven-cell FAIL kept `c3rc != 0` on
# this box, so that comparison was never reached and the box's own
# ALREADY-DOCUMENTED python-version skip-count skew (this section's own
# BOX SENSITIVITY note, PASS 12729/SKIP 16107 here against the Linux pins
# below) was invisible. Fixing the seven cells makes `c3rc` 0 on this box
# for the first time, which SURFACES that pre-existing mismatch as a new
# population-pin FAIL here -- not a regression this lane introduced, and
# not a gap this lane's brief scoped it to fix (box-sensitivity pin
# management is wake.md's darwin admin territory). Named here so the next
# reader does not mistake a newly-VISIBLE old gap for a new one.
#
# [S5-ARM re-pin, 2026-09-11, lane abifix] +0 PASS / +72 SKIP (+72
# pcre2-only, every other SKIP_* reason unchanged), from the S5-ARM Linux
# reference run (ubuntubudu, glibc, gcc-15.2, pin 13b56a12, build/
# s5_arm_20260911) reading SKIP=15146/pcre2-only=2944 against this file's
# prior I-61 pins (SKIP=15074/pcre2-only=2872) -- the tree moved past
# I-61's measuring commit (38dec0c2) and nobody re-pinned C3's own
# breakdown for it.
#
# THE MOVER IS NOT LANE PYROLE. The merge commit `db142b16` (lane pyrole,
# the C3 three-way-verdict mechanism) touches zero `.rxt` files -- verified
# directly (`git show db142b16 --stat | grep -c '\.rxt$'` = 0) -- and its
# own report and this file's [pyrole re-pin] note above both already state
# "every SKIP_* reason unchanged" for its landing. The two corpus changes
# that DID land between I-61 and this run are [K53-SELRETRY] (lane
# utf8k53, commits e638afee/880ba16d: the 16 blocks parked in
# tests/known_fail/k53_uprops_oversize.rxt move back into
# tests/utf8/axis04_p_categories.rxt at their canonical positions, that
# file removed) and [M5.0] STAGE 5 script properties (lane utf8s5, merge
# 0b21c32f: the NEW file tests/utf8/axis12_scripts.rxt, 333 lines/72
# `# pcre2-only` cells -- non-ASCII script-name subjects, U14's standing
# reason).
#
# ISOLATED, measured directly on this box (not copied from the Linux log,
# same method the prior [arm61fix]/[ntriage] re-pins above used --
# `verify_rxt.py` file-by-file, since `# pcre2-only` classification is a
# per-block marker in the corpus text and does not depend on the
# interpreter python version):
#   axis04_p_categories.rxt @38dec0c2 (pre-K53-SELRETRY): SKIP=462, all
#     pcre2-only.
#   known_fail/k53_uprops_oversize.rxt @38dec0c2 (deleted at HEAD): SKIP=44,
#     all pcre2-only.
#   axis04_p_categories.rxt @HEAD (post-K53-SELRETRY, the 44 blocks
#     restored): SKIP=506, all pcre2-only -- 462+44=506, exact wash, K53-
#     SELRETRY's own corpus move contributes ZERO net C3 movement (its
#     `[K53-SELRETRY] fix the corpus move's own defect`/`CENSUS_*` re-pin,
#     880ba16d, already accounted for this correctly at the file/block/line
#     level; it never touched C3's PASS/SKIP breakdown because there was
#     nothing here for it to move).
#   axis12_scripts.rxt @HEAD (new file, utf8s5): SKIP=72, all pcre2-only --
#     THE ENTIRE +72 delta, on its own, with nothing else contributing.
# (reproduction: `/tmp/c3repin/{old,new}/*.rxt` per the derivation above,
# `python3 tests/harness/verify_rxt.py --file-timeout 10 --allow-timeouts 1
# <file>` on each in isolation.)
#
# Reconciliation: C3_PASS + C3_SKIP + C3_TIMEOUT_FILE_LINES =
# 13708+15146+89 = 28943 = CENSUS_LINES (unchanged, tests/rxtsource/
# run_rxtsource_tests.sh:198 -- CENSUS_LINES was ALREADY re-pinned to
# 28943 for axis12_scripts.rxt at commit 9bbdc0f9, 2026-09-09, a full day
# before this file's own C3 breakdown was; that gap between the two pins
# is exactly what this re-pin closes). giveup/composed/no-python-
# expression/perr-python-accepts/own-oracle are untouched (measured 0
# movement in all four isolated runs above) and are NOT re-pinned here.
#
# [cmtfix re-pin, 2026-09-17, lane btriage] +6 PASS, nothing else moved --
# the SAME gap recurring one commit later. `e0bc115b` ([O-31 F1], the DFA
# comment-escaping fix) landed `tests/base/comment_escape.rxt` and its own
# message says "tests/rxtsource census re-pinned +1/+2/+6", which it did
# for CENSUS_*/RUNSH_* (211/3938/28949) but not for C3's own PASS/SKIP
# breakdown -- caught here because the dial+K59 train's merge battery
# (cf0962e3) is the first `make test` run after e0bc115b landed. ISOLATED
# directly: `python3 tests/harness/verify_rxt.py tests/base/
# comment_escape.rxt` reports `PASS=6 FAIL=0 ... SKIP=0`, all six cells
# (two `pattern` blocks, three m/n lines each) are plain literal-escape/
# character-class patterns with nothing PCRE2-only about them, so the
# entire delta is PASS and no C3_SKIP_* reason moves. Reconciliation:
# 13714+15146+89 = 28949 = CENSUS_LINES (matches the pin above).
#
# [k62pin re-pin, 2026-09-21, lane k62pin] +1 PASS, +15 SKIP (all fifteen
# under no-python-expression), nothing else moved. [K62]'s own new file
# (tests/quoting/k62_class_range_e.rxt, adm0921) ISOLATED directly —
# `python3 tests/harness/verify_rxt.py --file-timeout 10
# tests/quoting/k62_class_range_e.rxt` reports `PASS=1 ... SKIP=15
# (... no-python-expression=15 ...)`: the file's one `perr` block is the
# PASS (verified the same way any `perr` is, D26 provenance-only) and its
# four accepting blocks' fifteen `m`/`n` lines are every one classified
# no-python-expression — python's `re` has no translation for the
# class-range `\E`/`\Q\E` dissolution these blocks pin (unlike
# `pcre2-only`, this reason is a STRUCTURAL "no python spelling exists"
# call the classifier makes per pattern shape, not a python-version-
# sensitive divergence, so it carries across boxes the same way
# `pcre2-only` does — the prior re-pins' own stated method). Reconciliation:
# 13721+15161+89 = 28971 = CENSUS_LINES (matches the pin above).
C3_PASS=13721
C3_SKIP=15161
C3_SKIP_PCRE2ONLY=2944
C3_SKIP_GIVEUP=23
C3_SKIP_COMPOSED=0
C3_SKIP_NOPYTHON=1890
C3_SKIP_PERRACCEPT=14
C3_SKIP_OWNORACLE=10290
C3_INFO=0
C3_STOREUNCOVERED=0
C3_TIMEOUT=1
# [DD-13b.W1.1 r46chk finding 3 / r46sem finding 6] THE "89" NAMED, WITH
# ITS OWN UPDATE PROCEDURE. This is `tests/base/d27_k23_ambiguous_
# decomposition.rxt`'s own expectation-line count (MEASURED: the census
# awk above over that one file gives exactly 89) -- the ONE file
# C3_TIMEOUT pins as expected to overrun verify_rxt.py's per-file wall
# bound. It is silently COUPLED to C3_TIMEOUT: if that file ever becomes
# python-verifiable (a faster box, a python change), the reconciliation
# check below fails alongside C3_TIMEOUT and pcrec_error's own
# --allow-timeouts guard, with three different messages and none of them
# saying "the timed-out file is now verified" on its own -- reading THIS
# comment is what closes that gap. If the file's own expectation count
# ever changes (a corpus edit), update C3_TIMEOUT_FILE_LINES here in the
# same reviewed commit, beside CENSUS_LINES.
C3_TIMEOUT_FILE_LINES=89

# THE PER-FILE WALL BOUND IS NOT OPTIONAL HERE, and this is the one place
# it is armed. MEASURED: `tests/base/d27_k23_ambiguous_decomposition.rxt`
# (`(a{1,3}){65}`, subjects to 100+ characters) does not return under
# python `re` — a backtracking engine asked for a 65-group decomposition
# of an ambiguous run. 64 characters answers instantly; 70 does not
# answer. Without the bound, wiring this oracle to the corpus hangs
# `make test` forever, which is what D45 already forbids for every other
# thing the harness runs ("a loud, named FAILURE, never a hang or a
# silent skip") and what nobody had applied here because this script had
# never run.
C3OUT="$WORKDIR/c3.out"
# [DD-13b.W1.1 r46sem finding 6] `--allow-timeouts 1`: the ONE file this
# run pins as expected to overrun (tests/base/d27_k23_ambiguous_
# decomposition.rxt, C3_TIMEOUT_FILE_LINES above). verify_rxt.py itself
# now exits 1 on ANY timeout the caller does not explicitly allow, so
# without this flag a correctly-behaving run would fail on its own known,
# pinned exclusion; a SECOND file timing out would still exceed the
# allowance and fail loudly, which is the property finding 6 exists for.
"$TIMEOUT_BIN" 900 python3 "$VERIFY" --min-files "$CENSUS_FILES" \
    --file-timeout 10 --allow-timeouts 1 $(cat "$FILES") > "$C3OUT" 2>&1
c3rc=$?
c3_files=$(awk -F= '/^FILES=/ { print $2 }' "$C3OUT")
c3_pass=$(awk '/^PASS=/ { sub(/^PASS=/, "", $1); print $1 }' "$C3OUT")
c3_skip=$(awk -F'[=( ]' '/^SKIP=/ { print $2 }' "$C3OUT")
c3_timeout=$(awk -F'[=( ]' '/^TIMEOUT=/ { print $2 }' "$C3OUT")
# [C3 THREE-WAY VERDICT] the fourth, always-printed bucket
# (docs/design/c3_three_way.md): a python-vs-expectation disagreement the
# committed C3 oracle store CONFIRMS is right anyway -- never a failure,
# counted separately from PASS/SKIP so growing python's own blind spots
# (a version regression, a corpus file exercising a new construct) is
# visible rather than silently absorbed into PASS.
c3_info=$(awk -F'[=( ]' '/^INFO=/ { print $2 }' "$C3OUT")
# how many of c3's FAIL are a clean miss against the store (the mechanism
# fell back to today's python-only verdict) rather than a real
# store-confirmed disagreement -- see the design note's verdict table.
c3_storeuncovered=$(awk -F'[=( ]' '/^STOREUNCOVERED=/ { print $2 }' "$C3OUT")
c3_reason() { sed -n 's/.*[ (]'"$1"'=\([0-9]*\).*/\1/p' "$C3OUT" | head -1; }

if [ "${c3_files:-}" = "$CENSUS_FILES" ]; then
    pass "C3: verify_rxt.py discovered $c3_files files (its own discovery, floored at the census)"
else
    fail "C3: verify_rxt.py discovered ${c3_files:-<no FILES line>} files, expected $CENSUS_FILES"
fi

if [ "$c3rc" -eq 0 ]; then
    pass "C3: verify_rxt.py verified $c3_pass expectation(s) with $c3_skip skip(s) and $c3_info info (python-divergent, pcre2-confirmed), 0 failures"

    # THE TOTALS, AGAINST THEIR PINS. The verified count alone is not
    # enough: a skip predicate that WIDENS moves work out of PASS and
    # into SKIP while both totals stay explicable, so each reason is
    # pinned separately. They also reconcile — pass + info + skip + the
    # timed-out file's own lines must be the whole census — which is
    # what makes this an accounting rather than eleven loose numbers.
    c3_bad=""
    for chk in "PASS:$c3_pass:$C3_PASS" \
               "SKIP:$c3_skip:$C3_SKIP" \
               "INFO:$c3_info:$C3_INFO" \
               "STOREUNCOVERED:$c3_storeuncovered:$C3_STOREUNCOVERED" \
               "TIMEOUT:${c3_timeout:-x}:$C3_TIMEOUT" \
               "pcre2-only:$(c3_reason pcre2-only):$C3_SKIP_PCRE2ONLY" \
               "giveup:$(c3_reason giveup):$C3_SKIP_GIVEUP" \
               "composed:$(c3_reason composed):$C3_SKIP_COMPOSED" \
               "no-python-expression:$(c3_reason no-python-expression):$C3_SKIP_NOPYTHON" \
               "perr-python-accepts:$(c3_reason perr-python-accepts):$C3_SKIP_PERRACCEPT" \
               "own-oracle:$(c3_reason own-oracle):$C3_SKIP_OWNORACLE"; do
        nm=${chk%%:*}; rest=${chk#*:}; got=${rest%%:*}; want=${rest#*:}
        [ "$got" = "$want" ] || c3_bad="$c3_bad
    $nm: got ${got:-<absent>}, pinned $want"
    done
    if [ -z "$c3_bad" ]; then
        pass "C3: all eleven population pins hold (verified, informational, skips by reason, timeouts)"
    elif [ "$(uname -s)" = "Darwin" ]; then
        # The pins are the LINUX REFERENCE BOX's numbers (the BOX
        # SENSITIVITY notes above; I-61's pins, python 3.14 there vs this
        # box's older python). On darwin a delta against them is the
        # documented box skew, not a verdict — RECORDED every run so the
        # populations stay visible, asserted only where the pins are
        # native. A REAL local movement still surfaces: the reconciliation
        # check below (sums must equal the census) stays hard on every box.
        record "C3: population pins are Linux-reference numbers; this box's deltas (documented box sensitivity, not asserted here):$c3_bad"
    else
        fail "C3: population pin(s) MOVED:$c3_bad
  A skip reason that grows is coverage lost without a failing case to
  show for it; an INFO count that grows is a NEW python-vs-expectation
  divergence the store confirmed (fine, but re-pin so the population stays
  visible); a STOREUNCOVERED count that grows names cells
  tests/rxtsource/build_c3_store.py should capture next. If the move is
  legitimate — a corpus file added, a block newly marked, a module landing
  that makes patterns python-expressible, a new store capture — re-pin the
  C3_* values in this file in a reviewed commit saying which and why."
    fi

    if [ "$((c3_pass + c3_info + c3_skip + C3_TIMEOUT_FILE_LINES))" = "$CENSUS_LINES" ]; then
        pass "C3 reconciles: $c3_pass verified + $c3_info info + $c3_skip skipped + $C3_TIMEOUT_FILE_LINES in the timed-out file = $CENSUS_LINES"
    else
        fail "C3 DOES NOT RECONCILE: $c3_pass + $c3_info + $c3_skip + $C3_TIMEOUT_FILE_LINES = $((c3_pass + c3_info + c3_skip + C3_TIMEOUT_FILE_LINES)),
  census $CENSUS_LINES. Expectations are going somewhere neither counted
  nor reported, which is the one outcome a skip total exists to prevent.
  If tests/base/d27_k23_ambiguous_decomposition.rxt legitimately changed
  size, or stopped timing out, update C3_TIMEOUT_FILE_LINES (and
  C3_TIMEOUT / --allow-timeouts above) together, in a reviewed commit."
    fi
else
    # ITS FIRST RUN OVER 139 NEVER-ORACLED FILES IS A DISCOVERY, NOT A
    # REGRESSION (w1_impl §7.4 risk 2). Before this wiring, this oracle's
    # default covered 40 of 179 files and 3,603 of 26,691 expectation
    # lines — 13.5%. Anything it now finds outside tests/base/ is a
    # PRE-EXISTING expectation that was never checked against python `re`,
    # and the right response is a triage list, not a corpus edit made to
    # turn this green.
    fail "C3: verify_rxt.py reported failures. READ THIS BEFORE EDITING ANY .rxt FILE:
  this oracle was previously invoked by nothing, and its default covered
  40 of $CENSUS_FILES files. Its first run over the rest is a DISCOVERY of
  expectations that were never oracle-checked, not a regression this
  change caused. Triage the list (file, line, pattern, python-re verdict)
  before changing a single expectation — and note that python \`re\` is
  the WRONG oracle for some of them (tests/assertions/ is covered by
  libpcre2 for exactly that reason: python's \\Z is PCRE2's \\z).
$(grep -E '^(===|  line )' "$C3OUT" | head -40)"
fi

# ---------------------------------------------------------------------
# CHECK — THE ARM-BLOCK HASH PIN (r45chk F12, N3).
#
# "run.sh's existing arms are not touched" was a diff argument,
# and a diff argument is not a check. The protected region is delimited
# by MARKER COMMENTS rather than by a line range, because W1.1 itself
# edits inside it (the `have_block` guard) — a line-range hash would be
# broken by the very change it exists to protect, and the only way to
# "fix" that is to re-pin, which discards the protection entirely.
BEGIN_MARK='# --- BEGIN PINNED ARM REGION (w1 N3) ---'
END_MARK='# --- END PINNED ARM REGION ---'
# [DD-13b.W1.3] MOVED 2026-09-04, deliberately and in a reviewed change. The
# `export` ARM itself is OUTSIDE this region; what moved inside it is the
# per-block `cur_exports=""` reset, which belongs in the block-reset arm for
# the reason the comment there gives — a block-scoped directive that carried
# to the next block would compile the following pattern under something
# nobody wrote. The pin did its job: it caught an edit inside the arm chain
# and made someone say why. Previous: 3e945390... (W1.1).
#
# [DD-13b.W23.2] MOVED AGAIN, deliberately. Every `record_fail` call
# inside the region gained the DIAGNOSTIC CLASS TAG (`record_fail_class`,
# W23-S2 — format_design.md §2.25.5), and the `pattern` line's
# block-reset arm gained `cur_description_line=0` (the duplicate-
# `description` refusal's own state, §1.8 FOLD-IN 1). THE ATTACHMENT
# ARM's own new state reset and its indentation dispatch (S1,
# format_design §1.2.1) sit OUTSIDE the region, ahead of the BEGIN
# marker — an append that cannot move the pin, on the same reasoning
# W1.1's own new arms went AFTER the END marker. See this step's own
# lane report for the full list. Previous: 8ea2cd29... (W1.3).
ARM_PIN='b5a00e6142d024f2978bce13bd8debd9733818df3ab4023ce7e4075d62036356'

region="$WORKDIR/armregion.txt"
awk -v b="$BEGIN_MARK" -v e="$END_MARK" '
    index($0, b) { on = 1; next }
    index($0, e) { on = 0 }
    on { print }' "$RUNSH" > "$region"
region_lines=$(wc -l < "$region")
got_hash=$(sha256sum < "$region" | cut -d' ' -f1)

if [ "$region_lines" -lt 100 ]; then
    fail "arm pin: the region between the markers is only $region_lines lines.
  Either a marker was deleted or they were reordered. A pin over an empty
  or truncated region hashes nothing and would pass forever."
elif [ "$got_hash" = "$ARM_PIN" ]; then
    pass "arm pin: run.sh's pinned arm region ($region_lines lines) is unchanged"
else
    fail "arm pin: run.sh's PINNED ARM REGION CHANGED.
  region: between '$BEGIN_MARK'
      and '$END_MARK' in tests/harness/run.sh
  expected sha256 $ARM_PIN
  got      sha256 $got_hash

  THE UPDATE RULE. A change inside those markers is a change to the arm
  chain that R-COMPAT-1 protects — the 17 [[ =~ ]] arms plus the catch-all
  that 3,265 existing blocks and 26,691 existing expectation lines are
  parsed by. It is not forbidden,
  but it is never incidental:

    1. Say what moved and why, in the commit message.
    2. Re-pin ARM_PIN in this file in that SAME commit, as a deliberate,
       reviewed act — never as a fixup to make the suite green.
    3. New line kinds are APPENDED AFTER the END marker, not inserted
       inside the region. Appending cannot change which arm an existing
       line reaches; inserting can, because \`[[ =~ ]]\` clobbers
       BASH_REMATCH and the chain is order-sensitive.

  If you are here because you appended an arm and put it in the wrong
  place, move it below the END marker and this check goes green with no
  re-pin at all."
fi

# ---------------------------------------------------------------------
# CHECK — THE KEYWORD CENSUS, as a CHECK rather than a one-time
# measurement (r45chk F12).
#
# Appending arms to run.sh changes exactly one thing: a line that
# previously hit the catch-all (a HARD ERROR) now parses. That is safe
# only while no existing corpus line begins with one of the new words —
# and a measurement taken once can rot, which is why it runs every time.
#
# The 32 are format_design §1.1's own list, verbatim, so this check
# reproduces that note's measurement rather than a paraphrase of it.
# MORE ARE ADDED HERE, and the addition is the point rather than
# drift: `description`, `only` and `pcrec` are words THIS
# STEP appends arms for, and a census that did not cover them would not
# cover what it exists to make safe.
# `encoding` GRADUATED OUT OF THE CENSUS 2026-09-05: its arm is LANDED
# grammar (run.sh's [DD-13b.W1.1] per-pattern encoding axis) and the
# promoted utf8 corpus (merge 698eea61) legitimately begins 325+ lines
# with it as head declarations — parsed, not hard errors. This census
# protects words whose arm has NOT landed (appending it would flip an
# existing line's meaning); a landed keyword the corpus uses is the
# opposite case, and keeping it here made the check red on correct
# corpus growth (caught by the first full battery after the merge). A
# word graduates ONLY with its arm demonstrably landed and the collision
# population being that arm's own legitimate uses — say so here, dated,
# as this note does.
# [DD-13b.W23.1] `testee` AND `option` LEFT THE LIST, 32 -> 30, AND THE
# REASON IS A WITHDRAWAL RATHER THAN A GRADUATION. D99 (N-42) takes the
# `config`-body roster lines out of the format: a testee roster is engine
# DESCRIPTION, not rx definition, and it is aux content now (§2.27). A
# withdrawn production has no schema row, therefore no `wave`, therefore
# no entry in any derived "not in this build" list — which is the whole
# mechanism, and it is why this list shrinks instead of a keyword being
# marked somewhere as retired. The other direction (a word GRADUATES only
# with its arm demonstrably landed) is unchanged and is the note above.
CENSUS_WORDS_30="name target lib include config use variant oracle tag mc freq gap def with from repl s sg serr unsupported analysis question reader exemplar bytes sha256 analyzer date row groups"
CENSUS_WORDS_W1="description only pcrec"

collisions=""
ncensus=0
for w in $CENSUS_WORDS_30 $CENSUS_WORDS_W1; do
    ncensus=$((ncensus + 1))
    c=$(xargs grep -h -c "^$w\\b" < "$FILES" 2>/dev/null \
        | awk '{ n += $1 } END { print n+0 }')
    [ "$c" != "0" ] && collisions="$collisions $w=$c"
done

n30=$(printf '%s\n' $CENSUS_WORDS_30 | wc -l | tr -d ' ')
if [ "$n30" != "30" ]; then
    fail "keyword census: the pinned 30-word list has $n30 words.
  It is the format's candidate-keyword set; if it changed, say WHY here —
  a word leaves by WITHDRAWAL (no schema row, so no derived refusal list
  can name it) or by GRADUATION (its arm landed, and the note above says
  what that costs). Neither is a silent edit."
else
    pass "keyword census: the pinned list is 30 words plus W1's 3 still-candidate words (testee/option withdrawn 2026-09-13, D99/N-42; encoding graduated 2026-09-05)"
fi

if [ -z "$collisions" ]; then
    pass "keyword census: all $ncensus candidate keywords appear 0 times in first-token position"
else
    fail "keyword census: COLLISION —$collisions
  A corpus line already begins with a word the grown grammar wants as a
  keyword. Appending an arm for it would change that line's meaning from
  'hard error' to 'parsed', which is exactly what this census exists to
  refuse. Resolve before adding the arm."
fi

# =====================================================================
# THE HEAD PATH — and it exists because otherwise nothing exercises it.
#
# Everything above measures that the corpus DID NOT CHANGE, which is the
# invariant that matters most and is also, on its own, a check that would
# stay green if the entire head grammar were deleted: 0 of the 179 files
# are head-bearing, so the seam, the head productions and every refusal
# they carry have a population of ZERO on the corpus. A detector with an
# empty population is a green check measuring nothing — this project's
# most-recorded check-design failure — so the head gets its own witnesses.
#
# THE FIXTURES ARE NAMED `.rxtin`, NOT `.rxt`, and that is load-bearing:
# `find tests -name '*.rxt'` must not see them, or they would join the
# corpus, move the pinned census, and be dispatched by `run.sh`'s own
# no-argument discovery during `make test-corpus`. They are copied to a
# scratch directory under their real extension and invoked explicitly.
FIXDIR="$SCRIPT_DIR/fixtures"
FIXRUN="$WORKDIR/fix"
mkdir -p "$FIXRUN"
# [DD-13b.W23.3a] `.rxtfrag` FILES ARE COPIED VERBATIM, EXTENSION KEPT —
# NOT renamed to `.rxt` like their `.rxtin` siblings above. An `include`
# fixture's own `include "name.rxtfrag"` line resolves against ITS OWN
# directory, so the fragment must be PRESENT here; keeping the
# `.rxtfrag` extension is what keeps it OUT of `find tests -name
# '*.rxt'` and therefore out of the corpus, `tests/rxtsource/CLAUDE.md`'s
# own rule for exactly this shape.
if compgen -G "$FIXDIR"/*.rxtfrag > /dev/null; then
    for f in "$FIXDIR"/*.rxtfrag; do
        cp "$f" "$FIXRUN/$(basename "$f")"
    done
fi
for f in "$FIXDIR"/*.rxtin; do
    cp "$f" "$FIXRUN/$(basename "${f%.rxtin}").rxt"
done

# ---------------------------------------------------------------------
# [DD-13b.W23.4] W23-S4 (w23_impl.md §1.5, DECIDED (4) and (5)): TWO
# invariants over a REAL dump's own section rows, walked on
# `aux_deep_tree.rxtin` — a fixture whose whole point is COLLIDING KEYS
# (`pattern`, `m`, `provenance`, `config`, `variant` as literal `key`
# VALUES inside an `ext` body), which is exactly what makes it the
# sharpest possible witness for invariant (a). (a) no `#section` row's
# field 1 (the integer `line`) may equal any main-table `kind` token —
# the invariant that is what makes R2/R3's equality-reading consumers
# safe rather than merely lucky. (b) sections FOLLOW the main table: the
# ordinal of the last main-table row must be LESS than the ordinal of
# the first `#section` line — R2's own "first pattern row is the body
# boundary" assumption, load-bearing and, until now, untested.
S4_OUT="$WORKDIR/w23s4.tsv"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$FIXRUN/aux_deep_tree.rxt" \
        > "$S4_OUT" 2>"$WORKDIR/w23s4.err"; then
    kinds="pattern m ext freq config description provenance variant tag oracle include use lib target"
    s4a=$(awk -F'\t' -v kinds="$kinds" '
        BEGIN { n = split(kinds, ks, " "); for (i = 1; i <= n; i++) kw[ks[i]] = 1 }
        /^#section / { insect = 1; next }
        /^#/ { next }
        insect && ($1 in kw) { print; bad++ }
        END { print "BAD " bad+0 }' "$S4_OUT" | tail -1 | awk '{print $2}')
    s4b=$(awk -F'\t' '
        /^#section / { if (firstsect == 0) firstsect = NR; insect = 1; next }
        /^#/ { next }
        !insect { lastmain = NR }
        END { print (firstsect == 0 || lastmain < firstsect) ? "ok" : "bad" }' "$S4_OUT")
    if [ "$s4a" = "0" ] && [ "$s4b" = "ok" ]; then
        pass "W23-S4: no section row's field 1 equals a main-table kind token, and every section follows the main table"
    else
        fail "W23-S4: section-vs-main-table invariant broken (bad-field1 rows: $s4a, ordering: $s4b) on $S4_OUT"
    fi
else
    fail "W23-S4: --list-source failed on aux_deep_tree.rxt:
$(cat "$WORKDIR/w23s4.err")"
fi

# --- the accepting fixture -------------------------------------------
HB="$FIXRUN/head_basic.rxt"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$HB" > "$WORKDIR/hb.tsv" 2>"$WORKDIR/hb.err"; then
    pass "head: --list-source accepts a head-bearing file"

    # THE ROW ORDER IS THE CONTRACT. There is no head/body column: a head
    # row is exactly one preceding the first `pattern` row, which is a
    # property of the ORDER. So the order is what is asserted.
    # [DD-13b.W23.4] stops at the first `#section`: head_basic's own `m`/
    # `n` cases now grow a `#section cases` block, whose data rows do not
    # start with `#` either.
    got_kinds=$(awk -F'\t' '/^#section /{exit} !/^#/ { printf "%s ", $1 }' "$WORKDIR/hb.tsv")
    want_kinds="description lib config config target pattern pattern "
    if [ "$got_kinds" = "$want_kinds" ]; then
        pass "head: --list-source emits the declarations in FILE ORDER ($want_kinds)"
    else
        fail "head: --list-source row order wrong.
  expected: $want_kinds
  got:      $got_kinds"
    fi

    # THE `line` COLUMN, AGAINST AN INDEPENDENT DERIVATION. This is the
    # seam's one number — run.sh starts its loop there — so the expected
    # value comes from grep over the raw bytes, never from pcrec. A check
    # that asked pcrec what line pcrec thinks it is would be pcrec
    # agreeing with itself.
    want_body=$(grep -n '^pattern ' "$HB" | head -1 | cut -d: -f1)
    got_body=$(awk -F'\t' '$1 == "pattern" { print $2; exit }' "$WORKDIR/hb.tsv")
    if [ "$want_body" = "$got_body" ]; then
        pass "head: the first pattern row's line is $got_body (grep and pcrec agree)"
    else
        fail "head: --list-source reports the first pattern row at line $got_body,
  but grep finds it at line $want_body. This is THE number run.sh starts
  its body loop at: too early and the loop meets a head line, too late and
  blocks are silently skipped."
    fi

    # THE PATTERN COLUMN SURVIVES ITS OWN ESCAPING. `colou?r` has no
    # metacharacter the escape touches; what is asserted is that the
    # round trip is the identity where it should be, so the escape cannot
    # be "working" by mangling everything equally.
    if awk -F'\t' '$1 == "pattern" && $5 == "colou?r" { found = 1 }
                   END { exit !found }' "$WORKDIR/hb.tsv"; then
        pass "head: a block's pattern text survives the dump unchanged"
    else
        fail "head: the pattern column did not carry 'colou?r' verbatim"
    fi

    # the three new block directives and `features only` reach the dump
    if awk -F'\t' '$1 == "pattern" && $3 == "colour" && $8 == "1" && $9 == "byte" { ok = 1 }
                   END { exit !ok }' "$WORKDIR/hb.tsv"; then
        pass "head: name / encoding / features-only reach the dump on the right block"
    else
        fail "head: the second block's name/encoding/features_only columns are wrong:
$(awk -F'\t' '$1 == "pattern"' "$WORKDIR/hb.tsv")"
    fi
else
    fail "head: --list-source REJECTED the accepting fixture:
$(cat "$WORKDIR/hb.err")"
fi

# --- the seam, end to end through run.sh ------------------------------
#
# The only place in the tree where the body-start skip actually runs. It
# is checked through the counting wrapper as well, because "run.sh
# produced the right answers" would also be true of a run.sh that never
# made the call and simply happened to parse the head as comments.
: > "$CALLLOG"
if PCREC="$WRAPDIR/pcrec" "$TIMEOUT_BIN" 300 bash "$RUNSH" "$HB" \
        > "$WORKDIR/hb.run" 2>&1; then
    hb_calls=$(grep -c -- '--list-source' "$CALLLOG" || true)
    hb_pass=$(awk '/^cases passed:/ { print $3 }' "$WORKDIR/hb.run")
    hb_fail=$(awk '/^cases failed:/ { print $3 }' "$WORKDIR/hb.run")
    if [ "${hb_fail:-1}" = "0" ] && [ "${hb_pass:-0}" = "5" ]; then
        pass "head: run.sh ran the head-bearing fixture's 5 cases, 0 failures"
    else
        fail "head: run.sh on the head-bearing fixture reported ${hb_pass:-?} passed / ${hb_fail:-?} failed, expected 5 / 0:
$(tail -20 "$WORKDIR/hb.run")"
    fi
    if [ "$hb_calls" = "1" ]; then
        pass "head: run.sh made EXACTLY ONE --list-source call for the file (the seam fired)"
    else
        fail "head: run.sh made $hb_calls --list-source call(s) for one head-bearing
  file, expected exactly 1. Zero means the seam did not fire and the head
  was parsed by something else; more than one means the boundary is being
  re-derived per block."
    fi
else
    fail "head: run.sh FAILED on the head-bearing fixture:
$(tail -30 "$WORKDIR/hb.run")"
fi

# --- head and no body: two distinct observables -----------------------
HO="$FIXRUN/head_only.rxt"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$HO" > "$WORKDIR/ho.tsv" 2>&1; then
    ho_pat=$(awk -F'\t' '$1 == "pattern" { n++ } END { print n+0 }' "$WORKDIR/ho.tsv")
    ho_rows=$(awk -F'\t' '!/^#/ { n++ } END { print n+0 }' "$WORKDIR/ho.tsv")
    if [ "$ho_pat" = "0" ] && [ "$ho_rows" = "3" ]; then
        pass "head: a file with a head and no pattern blocks is ACCEPTED, 3 head rows, 0 pattern rows"
    else
        fail "head: head-only fixture gave $ho_rows row(s), $ho_pat pattern row(s); expected 3 and 0"
    fi
else
    fail "head: --list-source rejected a head-only file; a library file is exactly that shape"
fi
if "$TIMEOUT_BIN" 300 bash "$RUNSH" "$HO" > "$WORKDIR/ho.run" 2>&1; then
    fail "head: run.sh SUCCEEDED on a file with no pattern blocks; the P-C2 floor
  must fire — otherwise a file that runs nothing reads as a clean pass"
elif grep -q 'no pattern blocks parsed from file' "$WORKDIR/ho.run"; then
    pass "head: run.sh reports the P-C2 floor on a head-only file (distinct from a failed call)"
else
    fail "head: run.sh failed on the head-only file, but not with the P-C2 floor —
  'no pattern blocks parsed' and 'the --list-source call failed' must stay
  distinct observables:
$(tail -20 "$WORKDIR/ho.run")"
fi

# --- the refusals, each asserting what its message must NAME ----------
#
# D26 puts diagnostic WORDING outside the tier worth pinning, so what is
# asserted here is never a sentence — it is that the message names the
# thing the author has to act on: the boundary, the cycle's members, both
# collision sites, the wave. A refusal that says only "error" is useless
# in exactly the cases these fixtures are about.
check_refusal() {
    local fixture=$1 label=$2
    shift 2
    local out rc
    out="$("$TIMEOUT_BIN" 30 "$PCREC" --list-source "$FIXRUN/$fixture" 2>&1)"
    rc=$?
    if [ "$rc" = "0" ]; then
        fail "head/$label: --list-source ACCEPTED $fixture; it must be refused"
        return
    fi
    local missing=""
    local needle
    for needle in "$@"; do
        case $out in
            *"$needle"*) ;;
            *) missing="$missing '$needle'" ;;
        esac
    done
    if [ -z "$missing" ]; then
        pass "head/$label: refused, and the message names what the author must act on"
    else
        fail "head/$label: refused, but the message does not name:$missing
  got: $out"
    fi
}

check_refusal head_after_pattern.rxt boundary   'lib' 'head'
check_refusal from_cycle.rxt          cycle      'cycle' 'a' 'b'
# [DD-13b.W23.3] `wave2_keyword.rxt` IS GONE AND ITS REPLACEMENT ACCEPTS.
# Its keyword (`include`) is a shipped production now, so the refusal it
# pinned has no input; the NOT-IN-THIS-BUILD tier's whole population is
# empty at this pin and W23-S3 arm 4 is where that is reported. See
# `include_head.rxtin`'s own header for why the file was replaced rather
# than inverted.
IH="$FIXRUN/include_head.rxt"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$IH" > /dev/null 2>"$WORKDIR/ih.err"; then
    pass "head/include: a head 'include' line PARSES (it refused as a later-wave keyword before W23.3)"
else
    fail "head/include: leg A refused a head 'include' line, which W23.3 builds:
  $(cat "$WORKDIR/ih.err")"
fi
# [DD-13b.W23.1] RESERVED is a THIRD answer beside 'built' and 'a later
# wave builds it', and the refusal has to distinguish it: a reader told
# 'unknown' hunts a typo, and a reader told 'not in this build' waits for
# a wave that is never coming.
check_refusal version_reserved.rxt reserved 'version' 'RESERVED' 'no build parses it'
check_refusal dup_config.rxt          duplicate  'duplicate' 'dev'

# [DD-13b.W23.1] THE BLOCK SCALAR IN A PATTERN BLOCK: A SHIPPED REFUSAL
# THAT CHANGED DIRECTION, and it is asserted on the DECODED VALUE rather
# than on a verdict, because a three-way agreement on a value catches more
# than one on a rejection.
#
# Until the grammar became two layers, "a pattern block's lines are NOT
# indented" was a LEXICAL rule and the prose-value production said a
# `description` takes a `|` block scalar; the two contradicted each other
# and the body's rule won. Under S1 there is ONE attachment rule
# everywhere and a prose region's extent is S3's, so the contradiction
# DISSOLVES rather than being arbitrated: a block `description` takes the
# full prose value, at any depth, wherever the schema declares one
# (format_design §1.2.5, spec hunk SW16).
#
# LEG A ONLY AT THIS PIN, and the reason is the staging rather than the
# rule: legs B and C gain their ATTACHMENT ARM and their child
# CONSUMPTION at W23.2, so today they still refuse every indented line.
# The three-leg form of this assertion belongs to that step, and asserting
# it here would be asserting a claim about two parsers that have not been
# taught yet — §3.3's rule for `all-readers`, applied to a fixture.
bs="$FIXRUN/block_scalar_in_body.rxt"
bs_out="$("$TIMEOUT_BIN" 30 "$PCREC" --list-source "$bs" 2>&1)"; bs_rc=$?
bs_desc="$(printf '%s\n' "$bs_out" | awk -F'\t' '$1 == "pattern" { print $4; exit }')"
if [ "$bs_rc" != "0" ]; then
    fail "head/blockscalar: --list-source REFUSED a block '|' description; the
  two-layer grammar makes a prose value legal wherever the schema declares
  one (format_design §1.2.5). got: $bs_out"
elif [ "$bs_desc" = "this cannot work here" ]; then
    pass "head/blockscalar: leg A accepts a block '|' description and decodes it (the §1.2.5 widening)"
else
    fail "head/blockscalar: leg A accepted the block '|' description but decoded
  it as '$bs_desc', not the region's own text. The value is what this
  fixture asserts — a verdict would pass on a reader that opened the
  region and threw its content away."
fi

# --- the two rows that would otherwise have NO population ------------
#
# S199 and S204 both plant a silent ACCEPTANCE, and on the clean corpus
# neither has anything to accept: MEASURED, all 59 distinct `features`
# lists in the corpus are valid, and after W1.1 taught verify_rxt.py the
# other four line kinds, no corpus line reaches its unknown-kind branch.
# A detector with an empty population is a green check measuring nothing
# — both rows scored UNDETECTED on their first run, which is exactly how
# this was found. These two fixtures are their witnesses.

# S199: an invalid `features` list must be a LOUD harness failure, never
# a silently-passing `perr`. pcrec refuses an unknown module with exit 1,
# which is what `perr` asserts — so without this validation the block
# certifies the typo, not the pattern.
BF="$FIXRUN/bad_features.rxt"
if "$TIMEOUT_BIN" 300 bash "$RUNSH" "$BF" > "$WORKDIR/bf.run" 2>&1; then
    fail "S199 witness: run.sh ACCEPTED a block with an invalid features list.
  pcrec refuses an unknown module name with exit 1, which is exactly what
  a \`perr\` block expects — so this block just passed while testing the
  typo instead of the pattern."
elif grep -q "not a valid enabled-set spec" "$WORKDIR/bf.run"; then
    pass "S199 witness: run.sh fails loudly on an invalid features list, naming it"
else
    fail "S199 witness: run.sh failed on the invalid-features fixture, but not
  with the named harness failure — the message is what tells an author
  their module name is a typo rather than their pattern being wrong:
$(tail -10 "$WORKDIR/bf.run")"
fi

# S204: a line kind no parser knows must be REFUSED by all three, never
# swallowed. [DD-13b.W23.3] The token is `no-such-kind`, chosen because it
# cannot graduate into the format the way this fixture's previous token
# (`tag`) did — see the fixture's own header. "Not in this build" and
# "unparseable" stay distinguishable through this file and
# `version_reserved.rxtin` rather than through one token wearing both
# hats.
UK="$FIXRUN/unknown_kind.rxt"
if "$TIMEOUT_BIN" 60 python3 "$VERIFY" "$UK" > "$WORKDIR/uk.py" 2>&1; then
    fail "S204 witness: verify_rxt.py ACCEPTED a line kind it does not know.
  A parser that swallows an unknown kind as a comment verifies nothing
  and reports nothing, and subtracts from a total nobody compares."
else
    pass "S204 witness: verify_rxt.py refuses a line kind it does not know"
fi
if "$TIMEOUT_BIN" 300 bash "$RUNSH" --dump "$UK" > /dev/null 2>&1; then
    fail "S204 witness: run.sh ACCEPTED an unknown line kind; its catch-all is
  what makes a corrupted corpus loud instead of silently smaller"
else
    pass "S204 witness: run.sh refuses it through its catch-all"
fi
uk_out="$("$TIMEOUT_BIN" 30 "$PCREC" --list-source "$UK" 2>&1)"
if [ $? -eq 0 ]; then
    fail "S204 witness: --list-source ACCEPTED a kind it does not know"
elif printf '%s' "$uk_out" | grep -q '\[unknown-token-in-scope\]' &&
     printf '%s' "$uk_out" | grep -q 'no-such-kind'; then
    pass "S204 witness: --list-source refuses 'no-such-kind' as an unknown token IN ITS SCOPE, naming it"
else
    fail "S204 witness: --list-source refused 'no-such-kind', but not as an
  unknown token in its scope naming the token. The CLASS is what the
  three-leg differential compares and the TOKEN is what an author acts
  on; a refusal carrying neither is a refusal nobody can use:
  $uk_out"
fi

# verify_rxt refuses a HEAD-BEARING file by name rather than mis-parsing
# it: the head has one parser, and a fourth would be one more thing to
# keep in step. A loud refusal is the honest W1.1 answer.
if python3 "$VERIFY" --dump "$HB" > /dev/null 2>&1; then
    fail "head: verify_rxt.py accepted a head-bearing file; it reads the BODY only
  and must say so rather than growing a fourth head parser"
else
    pass "head: verify_rxt.py refuses a head-bearing file by name (the body-only oracle)"
fi

# =====================================================================
# [DD-13b.W1.1] THE r46 PANEL'S FIXTURES (docs/dev/reviews/
# 2026-08-30-r46-w11-impl.md, fix lane w11f) — the class of finding was
# "the three parsers agree on the CORPUS and diverge one line outside
# it", and every witness below is a `.rxtin` that makes that divergence
# REACHABLE and then asserts the fix: either three-way agreement (accept
# with identical dump, or refuse in all three naming the refusal) or, for
# the head-only constructs no body parser ever sees, leg A alone.

# --- extract_class <text> — the ONE place a class tag is pulled out of a
# leg's own output (W23-S2's instrument). Reads the LAST `[a-z-]+`
# bracketed tag rather than the first: leg C's `--dump` path has no
# top-level try/except (pre-existing, unrelated to this step), so a
# ValueError propagates as a full python TRACEBACK and the class tag is
# in its OWN final "ValueError: [class] ..." line — the first bracket in
# a long traceback is never guaranteed to be the tag, but the LAST one
# always is, because `_fail`/`rxt_fail`/`record_fail_class` all put the
# tag at the very front of the message they raise, and nothing after it
# is a second bracket in these three legs' own output.
extract_class() {
    printf '%s\n' "$1" | LC_ALL=C grep -o '\[[a-z-]\{1,\}\]' | tail -1 | tr -d '[]'
}

# --- a REFUSAL helper for a construct all three legs parse (the body) --
#
# `check_refusal` (above) already asserts leg A's message; this adds
# legs B and C's own refusal AND compares DIAGNOSTIC CLASS across all
# three (W23-S2, format_design.md §2.25.5 / w23_impl.md §3.1) — never
# exit code alone, which is satisfiable by accident on a population of
# one message since leg B used to refuse everything identically. The
# class is read off EACH LEG'S OWN OUTPUT INDEPENDENTLY (the failure
# mode this instrument is built against: a tag leg B derives from the
# same arm that produced the message, and leg A from a lookup, agreeing
# because both are reading one implementation's opinion twice — see
# `run.sh`'s `record_fail_class` and `verify_rxt.py`'s `_fail`, each its
# own site, tagging AT THE RULE THAT FIRED).
check_refusal_all3() {
    local fixture=$1 label=$2 class=$3
    shift 3
    check_refusal "$fixture" "$label" "[$class]" "$@"
    local f="$FIXRUN/$fixture"
    local b_out b_class
    b_out="$("$TIMEOUT_BIN" 300 bash "$RUNSH" --dump "$f" 2>&1)"
    if [ $? -eq 0 ]; then
        fail "head/$label: run.sh --dump ACCEPTED $fixture; it must be refused too"
    else
        b_class="$(extract_class "$b_out")"
        if [ "$b_class" = "$class" ]; then
            pass "head/$label: run.sh --dump refuses it too, class [$class] agrees with leg A"
        else
            fail "head/$label: run.sh --dump refuses $fixture but its class is '${b_class:-<none>}', not leg A's '$class':
  got: $b_out"
        fi
    fi
    local c_out c_class
    c_out="$("$TIMEOUT_BIN" 60 python3 "$VERIFY" --dump "$f" 2>&1)"
    if [ $? -eq 0 ]; then
        fail "head/$label: verify_rxt.py --dump ACCEPTED $fixture; it must be refused too"
    else
        c_class="$(extract_class "$c_out")"
        if [ "$c_class" = "$class" ]; then
            pass "head/$label: verify_rxt.py --dump refuses it too, class [$class] agrees with leg A — all three parsers agree"
        else
            fail "head/$label: verify_rxt.py --dump refuses $fixture but its class is '${c_class:-<none>}', not leg A's '$class':
  got: $c_out"
        fi
    fi
}

# ---------------------------------------------------------------------
# [DD-13b.W23.5] THE `all-readers` RECEIPTS (w23_impl.md §3.3, W23-S5).
#
# "The check reads the INVOCATION." A declared fixture NAME on a schema
# row is exactly what a witness that stopped reaching its site still
# has — the fixture file exists, the row still names it, and a check
# that only looked for the name would stay green while the three-leg
# assertion behind it had silently stopped running ([MECH-REACH]'s
# shape). So the receipt is written by the code path that DOES the
# work, not declared beside it: `check_refusal_all3_kind` and
# `check_accept_all3_kind` (its accept-side sibling, below) are the ONLY
# two writers, and each appends one line to `$RECEIPTS` only after all
# three legs actually ran and answered as expected — a leg that failed
# to run, or answered the wrong way, writes NOTHING.
RECEIPTS="$WORKDIR/all3_receipts.txt"
: > "$RECEIPTS"
record_receipt() { printf '%s\n' "$1" >> "$RECEIPTS"; }

# `check_refusal_all3`'s own positional signature (fixture label class
# [needle...]) is UNCHANGED — thirteen existing call sites pass needle
# strings positionally and must not have to renumber them. The kind is
# a NEW leading argument this wrapper strips before delegating, so a
# call site becomes one word longer rather than reshuffled.
check_refusal_all3_kind() {
    local kind=$1; shift
    check_refusal_all3 "$@"
    record_receipt "$kind"
}

# The ACCEPT-SIDE SIBLING (§3.3 property 2's own naming): all three legs
# must ACCEPT (rc 0) the named fixture, or no receipt is written — an
# unconditional receipt here would defeat the whole point, since an
# accept-side witness IS its own rc.
check_accept_all3_kind() {
    local kind=$1 fixture=$2 label=$3
    local f="$FIXRUN/$fixture"
    local a_rc b_rc c_rc
    "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$f" > /dev/null 2>"$WORKDIR/$label.aerr"; a_rc=$?
    "$TIMEOUT_BIN" 60 bash "$RUNSH" --dump "$f" > /dev/null 2>"$WORKDIR/$label.berr"; b_rc=$?
    "$TIMEOUT_BIN" 60 python3 "$VERIFY" --dump "$f" > /dev/null 2>"$WORKDIR/$label.cerr"; c_rc=$?
    if [ "$a_rc" = "0" ] && [ "$b_rc" = "0" ] && [ "$c_rc" = "0" ]; then
        pass "$label: all three legs accept the fixture carrying '$kind'"
        record_receipt "$kind"
    else
        fail "$label: at least one leg refused an ACCEPTING fixture (leg A rc=$a_rc, leg B rc=$b_rc, leg C rc=$c_rc):
  (A: $(cat "$WORKDIR/$label.aerr"))
  (B: $(tail -3 "$WORKDIR/$label.berr" 2>/dev/null))
  (C: $(tail -3 "$WORKDIR/$label.cerr" 2>/dev/null))"
    fi
}

# --- sem1 (BLOCKER): the control-byte escape, all three legs, byte for byte
CB="$FIXRUN/ctrl_bytes.rxt"
cb_a_out="$("$TIMEOUT_BIN" 30 "$PCREC" --list-source "$CB" 2>"$WORKDIR/cb.aerr")"; cb_a_rc=$?
cb_b_out="$("$TIMEOUT_BIN" 60 bash "$RUNSH" --dump "$CB" 2>"$WORKDIR/cb.berr")"; cb_b_rc=$?
cb_c_out="$("$TIMEOUT_BIN" 60 python3 "$VERIFY" --dump "$CB" 2>"$WORKDIR/cb.cerr")"; cb_c_rc=$?
if [ "$cb_a_rc" = "0" ] && [ "$cb_b_rc" = "0" ] && [ "$cb_c_rc" = "0" ]; then
    cb_a_pat=$(printf '%s\n' "$cb_a_out" | awk -F'\t' '$1 == "pattern" { print $5; exit }')
    cb_b_pat=$(printf '%s\n' "$cb_b_out" | awk -F'\t' '$1 == "block" { print $6; exit }')
    cb_c_pat=$(printf '%s\n' "$cb_c_out" | awk -F'\t' '$1 == "block" { print $6; exit }')
    cb_want='a\x0bb\x0cc\x7fd'
    if [ "$cb_a_pat" = "$cb_want" ] && [ "$cb_b_pat" = "$cb_want" ] && [ "$cb_c_pat" = "$cb_want" ]; then
        pass "sem1 (BLOCKER): all three legs escape VT/FF/DEL identically as '$cb_want'"
    else
        fail "sem1 (BLOCKER): the control-byte escape disagrees.
  want:  $cb_want
  leg A: $cb_a_pat
  leg B: $cb_b_pat
  leg C: $cb_c_pat"
    fi
else
    fail "sem1 (BLOCKER): a leg failed to parse the control-byte fixture
  (leg A rc=$cb_a_rc, leg B rc=$cb_b_rc, leg C rc=$cb_c_rc) — it must be
  ACCEPTED and escaped, not refused."
fi

# --- sem2: a tab inside a `from` config list (head-only) --------------
check_refusal tab_in_config_list.rxt tab-in-list 'comma-separated config list'

# --- sem3: 'flags xmz' — only 'i' is defined, all three legs -----------
check_refusal_all3_kind flags bad_flags.rxt bad-flags value-shape "only 'i' is defined"

# --- sem4: 'engine dfa' — only 'vm' is defined for W1.1, all three legs
check_refusal_all3_kind engine bad_engine.rxt bad-engine value-shape 'only vm is defined'

# --- sem7: 'target ... with nosuch' — with is validated too (head-only)
check_refusal with_unknown.rxt with-unknown 'nosuch' 'not a' 'config'

# --- sem8 (discretionary depth check): the too-long diagnostics NAME
# THE CAP rather than falsely claiming a name is missing. HEAD-only.
TL="$WORKDIR/toolong.rxt"
{
    printf 'config %s\n' "$(printf 'x%.0s' $(seq 1 200))"
    printf '  flags i\n'
    printf '\n'
    printf 'pattern a+\n'
    printf 'm "aaa" 0 3\n'
} > "$TL"
tl_out="$("$TIMEOUT_BIN" 30 "$PCREC" --list-source "$TL" 2>&1)"
if [ $? -eq 0 ]; then
    fail "sem8: --list-source ACCEPTED a 200-byte config name; it must be refused"
elif printf '%s' "$tl_out" | grep -q 'too long'; then
    pass "sem8: a too-long config name is refused NAMING THE CAP, not 'needs a name'"
else
    fail "sem8: a too-long config name is refused, but not with a diagnostic
  naming the cap:
  $tl_out"
fi

# --- sem12 (discretionary): budget overflow is refused, not clamped ---
check_refusal budget_overflow.rxt budget-overflow 'non-negative integer'

# --- sem11 (discretionary): the indented-# wording, config body -------
check_refusal indented_comment_in_config.rxt indented-comment 'column 1'

# --- sem13: an empty description (trailing space, no text) — ACCEPTED
# by all three, identically, matching legs B and C's pre-existing
# behaviour (leg A used to hard-error "needs its text").
DE="$FIXRUN/desc_empty_trailing_space.rxt"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$DE" > "$WORKDIR/de.tsv" 2>"$WORKDIR/de.err" && \
   "$TIMEOUT_BIN" 60 bash "$RUNSH" --dump "$DE" > "$WORKDIR/de.b" 2>"$WORKDIR/de.berr" && \
   "$TIMEOUT_BIN" 60 python3 "$VERIFY" --dump "$DE" > "$WORKDIR/de.c" 2>"$WORKDIR/de.cerr"; then
    pass "sem13: an empty description (trailing space, no text) is ACCEPTED by all three"
else
    fail "sem13: an empty description was refused by at least one leg
  (A: $(cat "$WORKDIR/de.err"))
  (B rc via exit status above)
  (C: $(tail -3 "$WORKDIR/de.cerr" 2>/dev/null))"
fi

# --- sem14: 'description | ' (trailing space) — REFUSED by all three,
# matching the exact 'description |' spelling's own refusal.
# [DD-13b.W23.1] THE REASON MOVED AND THE VERDICT DID NOT. `description |`
# with one trailing space is still refused in all three legs — the TRIM
# rule (r46sem finding 14) is untouched, so the trimmed value is the bare
# `|` and the block form is what was written. What changed is WHY: the
# block form is now legal (§1.2.5), so leg A refuses this file for the
# region being EMPTY rather than for the form being a head-only one. The
# fixture is the same three-leg agreement; the needle follows the rule.
check_refusal_all3 desc_pipe_trailing_space.rxt desc-pipe-trailing-ws structure-attachment \
    'no indented continuation'

# --- sem15: a whitespace-only line between cases is ACCEPTED (ignored)
# by all three, matching the spec's "blank lines are ignored" with no
# carve-out for a line that is not literally zero bytes.
WO="$FIXRUN/whitespace_only_line.rxt"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$WO" > /dev/null 2>"$WORKDIR/wo.aerr" && \
   "$TIMEOUT_BIN" 60 bash "$RUNSH" --dump "$WO" > /dev/null 2>"$WORKDIR/wo.berr" && \
   "$TIMEOUT_BIN" 60 python3 "$VERIFY" --dump "$WO" > /dev/null 2>"$WORKDIR/wo.cerr"; then
    pass "sem15: a whitespace-only line is ACCEPTED (ignored) by all three"
else
    fail "sem15: a whitespace-only line was refused by at least one leg
  (A: $(cat "$WORKDIR/wo.aerr"))
  (C: $(tail -3 "$WORKDIR/wo.cerr" 2>/dev/null))"
fi

# --- sem16: a directive before any pattern in a HEADLESS file — REFUSED
# by all three (legs A/B already did; leg C used to silently drop it).
# Leg A reaches this through the HEAD vocabulary ('flags' is not a
# file-level directive there is no open block yet), which is a
# DIFFERENT sentence from legs B/C's "before any pattern block" — D26
# does not pin wording across legs, only that each names something the
# author can act on, so the needle here is leg A's own text.
check_refusal_all3 directive_before_pattern.rxt directive-before-pattern unknown-token-in-scope \
    'file-level'

# --- sem19: leg C validates 'name'/'encoding' too --------------------
#
# [DD-13b.W1.3] THE NEEDLE MOVED FROM 'identifier' TO 'definition name', and
# the change is the point rather than an accommodation. A block `name` stopped
# being an identifier in this step — it admits `-` and `.` — so a refusal that
# still said "identifier" would be describing a rule the parser no longer
# applies. What the fixture tests is unchanged and is the half that matters:
# `9bad` starts with a DIGIT, which no mapping can repair, and all three legs
# still refuse it. `bad_encoding_ident` below keeps its own needle, because an
# `encoding` value IS still an identifier — the two rules genuinely parted
# company here, and these two lines are where a reader sees that.
check_refusal_all3_kind name bad_name_ident.rxt bad-name-ident value-shape 'definition name'
check_refusal_all3_kind encoding bad_encoding_ident.rxt bad-encoding-ident value-shape 'encoding name'

# --- sem20: block name uniqueness, enforced on a HEADLESS file (the
# population every corpus file is in) — all three legs now refuse it.
check_refusal_all3_kind name dup_block_name.rxt dup-block-name schema-constraint 'duplicate block name'

# --- [RXTDUP lane, sem24] a pattern block's SECOND 'description' line
# is refused, naming both lines — the same discipline as sem20's
# duplicate block name, one field over. Before this fix the second line
# silently WON (M5, bench_rxt_needs_v1.md §1.9).
#
# [DD-13b.W23.2, §1.8 FOLD-IN 1] NOW check_refusal_all3, HEADLESS: legs B
# and C each closed their own gap in this step (previously the pre-fix
# shape, silently keeping the LAST description) — the fixture is
# headless, the population every corpus file is in, matching
# `dup_block_name.rxt`'s own reason.
check_refusal_all3_kind description dup_description.rxt dup-description schema-constraint "one 'description'"
DD="$FIXRUN/single_description.rxt"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$DD" > /dev/null 2>"$WORKDIR/dd.err" && \
   "$TIMEOUT_BIN" 60 bash "$RUNSH" --dump "$DD" > /dev/null 2>"$WORKDIR/dd.berr" && \
   "$TIMEOUT_BIN" 60 python3 "$VERIFY" --dump "$DD" > /dev/null 2>"$WORKDIR/dd.cerr"; then
    pass "dup-description: the accept control (ONE description line) is ACCEPTED by all three — the refusal is isolated to the duplicate"
    record_receipt description
else
    fail "dup-description: the single-description accept control was refused by at least one leg:
  (A: $(cat "$WORKDIR/dd.err"))
  (C: $(tail -3 "$WORKDIR/dd.cerr" 2>/dev/null))"
fi

# [DD-13b.W23.5] THE ACCEPT-SIDE RECEIPTS for the remaining four
# `all-readers` rows — `name`, `flags`, `encoding`, `engine` — from ONE
# fixture (`block_kinds_accept.rxtin`) carrying all four at once, all
# three legs required to ACCEPT.
check_accept_all3_kind name     block_kinds_accept.rxt block-kinds-accept-name
check_accept_all3_kind flags    block_kinds_accept.rxt block-kinds-accept-flags
check_accept_all3_kind encoding block_kinds_accept.rxt block-kinds-accept-encoding
check_accept_all3_kind engine   block_kinds_accept.rxt block-kinds-accept-engine

# --- [RXTDUP lane, sem25] a SECOND file-level 'description' is refused
# the same way, naming the earlier line — docs/spec/rxt_format.md calls
# this "a machine-readable prose FIELD" (singular). Head-only (legs B/C
# never read the head). $HB (head_basic.rxt, sem's own earlier fixture)
# is the accept control: it carries exactly one head-level description
# and continues to pass every check above.
check_refusal dup_head_description.rxt dup-head-description "one 'description'"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$HB" > /dev/null 2>"$WORKDIR/hbdd.err"; then
    pass "dup-head-description: head_basic's single head description is still ACCEPTED"
else
    fail "dup-head-description: head_basic (one head description) was refused:
  $(cat "$WORKDIR/hbdd.err")"
fi

# --- [RXTNUL lane, sem22] an EMBEDDED NUL BYTE anywhere in the file is
# refused BY NAME (the file, the 1-based line, and that it is a NUL
# byte), naming M1's own shape (bench_rxt_needs_v1.md §1.9/§2.7): before
# this fix `pattern ab<NUL>cd` silently truncated to `ab`, exit 0, no
# diagnostic.
#
# [DD-13b.W23.2, §1.8 FOLD-IN 1] NOW check_refusal_all3, HEADLESS: legs B
# and C each closed their own gap this step (bash's own `read` used to
# drop the byte silently, verify_rxt.py's decoder used to replace it with
# a space) — both now scan the WHOLE FILE for one before any line is
# interpreted, the same single scope leg A has always used.
check_refusal_all3 nul_byte.rxt nul-byte value-shape 'NUL byte'
NB="$FIXRUN/nul_byte.rxt"
NBOK="$WORKDIR/nul_byte_free.rxt"
tr -d '\000' < "$NB" > "$NBOK"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$NBOK" > /dev/null 2>"$WORKDIR/nbok.err" && \
   "$TIMEOUT_BIN" 60 bash "$RUNSH" --dump "$NBOK" > /dev/null 2>"$WORKDIR/nbok.berr" && \
   "$TIMEOUT_BIN" 60 python3 "$VERIFY" --dump "$NBOK" > /dev/null 2>"$WORKDIR/nbok.cerr"; then
    pass "nul-byte: the SAME file with the NUL stripped is ACCEPTED by all three — the refusal is isolated to the byte, not the shape"
else
    fail "nul-byte: the NUL-free twin of the fixture was refused by at least one leg:
  (A: $(cat "$WORKDIR/nbok.err"))
  (C: $(tail -3 "$WORKDIR/nbok.cerr" 2>/dev/null))"
fi

# --- [DD-13b.W23.2, §1.8 FOLD-IN 1] nul_in_comment: the fixture that
# DISCRIMINATES between the whole-file pre-parse scan and a line-
# interpreting one. `nul_byte.rxt`'s NUL sits mid `pattern` line, which
# every candidate scope catches; this one sits inside a `#` COMMENT
# line, which only a whole-file scan reaches — a per-line or decoder-
# scoped test would skip the line as a comment and never see the byte.
check_refusal_all3 nul_in_comment.rxt nul-in-comment value-shape 'NUL byte'
NIC="$FIXRUN/nul_in_comment.rxt"
NICOK="$WORKDIR/nul_in_comment_free.rxt"
tr -d '\000' < "$NIC" > "$NICOK"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$NICOK" > /dev/null 2>"$WORKDIR/nicok.err" && \
   "$TIMEOUT_BIN" 60 bash "$RUNSH" --dump "$NICOK" > /dev/null 2>"$WORKDIR/nicok.berr" && \
   "$TIMEOUT_BIN" 60 python3 "$VERIFY" --dump "$NICOK" > /dev/null 2>"$WORKDIR/nicok.cerr"; then
    pass "nul-in-comment: the SAME file with the NUL stripped is ACCEPTED by all three"
else
    fail "nul-in-comment: the NUL-free twin was refused by at least one leg:
  (A: $(cat "$WORKDIR/nicok.err"))
  (C: $(tail -3 "$WORKDIR/nicok.cerr" 2>/dev/null))"
fi

# ======================================================================
# [DD-13b.W23.3] THE FOURTEEN PRODUCTIONS' OWN FIXTURES
# ======================================================================
#
# Every three-leg assertion below compares the diagnostic CLASS, never an
# exit code (§3.1 W23-S2). Where a fixture is LEG A ONLY the reason is
# stated at the call rather than left looking like an oversight — the
# two reasons are the seam (a FILE-scope production is a head
# declaration and the head has one parser) and the schema's own
# `validated_by` column (a row that reads `pcrec` is a row legs B and C
# are not claimed to check, §3.3's rule for this lane).

# --- `ext`: the AUX production, §2.27 -----------------------------------
#
# aux's failure mode is pcrec deciding it UNDERSTANDS something, which an
# ACCEPTANCE fixture catches and a refusal fixture structurally cannot.
AUXOK=1
for auxf in aux_arbitrary_keys aux_deep_tree aux_literal_pipe aux_subtree_extent; do
    if ! "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$FIXRUN/$auxf.rxt" \
            > "$WORKDIR/$auxf.dump" 2>"$WORKDIR/$auxf.err"; then
        fail "aux/$auxf: leg A REFUSED an aux fixture it must accept — pcrec
  parses an aux body's structure and interprets nothing (§2.27):
  $(cat "$WORKDIR/$auxf.err")"
        AUXOK=0
    fi
done
[ "$AUXOK" = "1" ] && pass "aux: all four acceptance fixtures parse (arbitrary keys, a three-deep tree of keyword-colliding keys, a literal '|', a subtree's own extent)"

# [DD-13b.W23.4] `aux_literal_pipe`'s CENTRAL ASSERTION, unobservable
# until `#section aux` existed to carry it (w233_report.md §3.2): the
# `separator` row's OWN value is the single byte `|`, and `terminator`/
# `note` below it are SIBLING rows (same `parent_line`, not each other's
# parent) rather than continuations. If S3 still opened a region inside
# an open subtree, the `separator` value would be empty and the two
# lines after it would have been swallowed into it as prose.
alp="$WORKDIR/aux_literal_pipe.dump"
alp_sep=$(awk -F'\t' '/^#section aux/{s=1;next} /^#/{next} s && $6=="separator"{print $7}' "$alp")
alp_sep_parent=$(awk -F'\t' '/^#section aux/{s=1;next} /^#/{next} s && $6=="separator"{print $8}' "$alp")
alp_term_parent=$(awk -F'\t' '/^#section aux/{s=1;next} /^#/{next} s && $6=="terminator"{print $8}' "$alp")
alp_note_parent=$(awk -F'\t' '/^#section aux/{s=1;next} /^#/{next} s && $6=="note"{print $8}' "$alp")
if [ "$alp_sep" = "|" ] && [ -n "$alp_sep_parent" ] && \
   [ "$alp_term_parent" = "$alp_sep_parent" ] && [ "$alp_note_parent" = "$alp_sep_parent" ]; then
    pass "aux/literal-pipe: 'separator |' row's value is the single byte '|', and 'terminator'/'note' are its SIBLINGS (same parent_line $alp_sep_parent), not its children"
else
    fail "aux/literal-pipe: separator value='$alp_sep' (want '|'), parent_lines: separator=$alp_sep_parent terminator=$alp_term_parent note=$alp_note_parent (want all equal and non-empty) —
  decision 3's falsification point did not falsify: a prose region opened
  where structure-layer parameter 3 says it must not."
fi

# [DD-13b.W23.4] S242 (S-R4a): `opener_pattern_esc_pair.rxtin`'s two
# `pattern-esc` blocks each own one case row, at their own block's line —
# the population `--list-source`'s `#section cases`' `block_line` column
# exists to report, and the fixture that arms S242's detector.
opep="$WORKDIR/opener_pattern_esc_pair.dump"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$FIXRUN/opener_pattern_esc_pair.rxt" \
        > "$opep" 2>"$WORKDIR/opep.err"; then
    opep_blocks="$(section_count "" "$opep")"
    opep_bl="$(awk -F'\t' '/^#section cases/{s=1;next} /^#/{next} s{printf "%s ", $2}' "$opep")"
    if [ "$opep_blocks" = "2" ] && [ "$opep_bl" = "8 10 " ]; then
        pass "S242 detector: two 'pattern-esc' blocks each own one case row at their OWN block_line (8, 10)"
    else
        fail "S242 detector: main-table blocks=$opep_blocks (want 2), case block_lines='$opep_bl' (want '8 10 ') —
  either 'pattern-esc' stopped opening a second block, or something else moved."
    fi
else
    fail "S242 detector: --list-source failed on opener_pattern_esc_pair.rxt:
$(cat "$WORKDIR/opep.err")"
fi

# [RULEFIX, 2026-09-15] S242's fixture opens with `pattern-esc`, and
# `tests/harness/verify_rxt.py`'s leg C used to refuse any file shaped
# that way (`first != 'pattern'` at its old attachment check, with no
# `pattern-esc` exemption — MEASURED, and recorded as a finding in
# w235_report.md rather than fixed there). That made this fixture leg-A
# only despite it being exactly what S242's own header describes as its
# population: `opener_pattern_esc_pair.rxtin` was never reachable by a
# three-leg comparison. Frank's ruling: FIX legs C's recognition (never
# change what R-A already rules about the VALUE column below — leg C
# still reports a `pattern-esc` block's text AS WRITTEN). Re-verifies
# S242's own claim (two blocks, not one) through legs B and C too.
opep_b_out="$("$TIMEOUT_BIN" 30 bash "$RUNSH" --dump "$FIXRUN/opener_pattern_esc_pair.rxt" 2>"$WORKDIR/opep_b.err")"; opep_b_rc=$?
opep_c_out="$("$TIMEOUT_BIN" 30 python3 "$VERIFY" --dump "$FIXRUN/opener_pattern_esc_pair.rxt" 2>"$WORKDIR/opep_c.err")"; opep_c_rc=$?
opep_b_lines="$(printf '%s\n' "$opep_b_out" | awk -F'\t' '$1 == "block" { print $3 }' | tr '\n' ' ')"
opep_c_lines="$(printf '%s\n' "$opep_c_out" | awk -F'\t' '$1 == "block" { print $3 }' | tr '\n' ' ')"
if [ "$opep_b_rc" = "0" ] && [ "$opep_c_rc" = "0" ] && \
   [ "$opep_b_lines" = "8 10 " ] && [ "$opep_c_lines" = "8 10 " ]; then
    pass "S242 detector, three-legged: a file whose FIRST block opens with 'pattern-esc' is now accepted by leg C too (legs B and C both report blocks at lines 8, 10) — the fix makes opener_pattern_esc_pair.rxt reachable by all three legs"
else
    fail "S242 detector, three-legged: leg B or leg C still refuses (or misreads) a file opening with 'pattern-esc':
  leg B rc=$opep_b_rc blocks='$opep_b_lines' (want '8 10 '): $(cat "$WORKDIR/opep_b.err")
  leg C rc=$opep_c_rc blocks='$opep_c_lines' (want '8 10 '): $(cat "$WORKDIR/opep_c.err")"
fi

# [DD-13b.W23.4] S243 (S-R4b): `opener_m_not_opener.rxtin` is one block
# with two 'm' case lines on the shipped schema.
omno="$WORKDIR/opener_m_not_opener.dump"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$FIXRUN/opener_m_not_opener.rxt" \
        > "$omno" 2>"$WORKDIR/omno.err"; then
    omno_blocks="$(section_count "" "$omno")"
    omno_cases="$(section_count "cases" "$omno")"
    if [ "$omno_blocks" = "1" ] && [ "$omno_cases" = "2" ]; then
        pass "S243 detector: one 'pattern' block owns both 'm' case lines (1 block, 2 cases)"
    else
        fail "S243 detector: main-table blocks=$omno_blocks (want 1), cases=$omno_cases (want 2) —
  an 'm' line started acting like a block opener."
    fi
else
    fail "S243 detector: --list-source failed on opener_m_not_opener.rxt:
$(cat "$WORKDIR/omno.err")"
fi

# [DD-13b.W23.4] W23-S6 — THE AUX NON-INTERPRETATION CHECK (format_design
# §2.27.3 clause 5): edit an aux body and require every pcrec output
# EXCEPT `#section aux`'s own rows to be BYTE-IDENTICAL. `aux_identity`/
# `aux_identity_edited` are the same one `pattern a+` block with the SAME
# leading line count (so no row's `line` is downstream of the edit) and
# DIFFERENT aux bodies — the edit moves line count, depth, key spellings
# AND the number of `ext` blocks at once (§3.4's own rule: "the edit must
# be chosen to move as many plausible derived quantities as it can").
#
# TWO ARMS: (1) `--list-source` with `#section aux` elided; (2) the
# COMPILED ARTIFACT (`--source`'s implicit single-unnamed-block target,
# W1.2's own compatibility default) — .c AND .h. `--list-schema` is not a
# third arm: neither fixture's aux body can move a ROW of that table (aux
# has none), so comparing it would assert something the mechanism cannot
# violate.
AIW="$WORKDIR/auxid"
mkdir -p "$AIW/a" "$AIW/b"
cp "$FIXRUN/aux_identity.rxt" "$AIW/a/aux_identity.rxt"
cp "$FIXRUN/aux_identity_edited.rxt" "$AIW/b/aux_identity_edited.rxt"
w6ok=1
if ! "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$AIW/a/aux_identity.rxt" > "$AIW/a.tsv" 2>"$AIW/a.err"; then
    fail "W23-S6: --list-source failed on aux_identity.rxt: $(cat "$AIW/a.err")"; w6ok=0
fi
if ! "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$AIW/b/aux_identity_edited.rxt" > "$AIW/b.tsv" 2>"$AIW/b.err"; then
    fail "W23-S6: --list-source failed on aux_identity_edited.rxt: $(cat "$AIW/b.err")"; w6ok=0
fi
if [ "$w6ok" = "1" ]; then
    awk '/^#section aux/{exit}{print}' "$AIW/a.tsv" > "$AIW/a_noaux.tsv"
    awk '/^#section aux/{exit}{print}' "$AIW/b.tsv" > "$AIW/b_noaux.tsv"
    if diff -u "$AIW/a_noaux.tsv" "$AIW/b_noaux.tsv" > "$AIW/noaux.diff"; then
        pass "W23-S6 arm 1: --list-source with #section aux elided is byte-identical across an aux-body edit that moves line count, depth, keys AND block count"
    else
        fail "W23-S6 arm 1: --list-source moved OUTSIDE #section aux when the aux body changed —
$(head -20 "$AIW/noaux.diff")"
    fi
fi
if ( cd "$AIW/a" && "$TIMEOUT_BIN" 30 "$PCREC" --source aux_identity.rxt -o out.c ) > "$AIW/a_build.err" 2>&1 && \
   ( cd "$AIW/b" && "$TIMEOUT_BIN" 30 "$PCREC" --source aux_identity_edited.rxt -o out.c ) > "$AIW/b_build.err" 2>&1 && \
   diff "$AIW/a/out.c" "$AIW/b/out.c" > "$AIW/c.diff" 2>&1 && \
   diff "$AIW/a/out.h" "$AIW/b/out.h" > "$AIW/h.diff" 2>&1; then
    pass "W23-S6 arm 2: the compiled artifact (.c and .h) is byte-identical across the same aux-body edit"
else
    fail "W23-S6 arm 2: the compiled artifact moved when the aux body changed (or a build failed):
$(cat "$AIW/a_build.err" "$AIW/b_build.err" "$AIW/c.diff" "$AIW/h.diff" 2>/dev/null | head -30)"
fi

# THE ABSENCE ASSERTIONS ARE THE CHECK. `aux_deep_tree.rxt`'s body uses
# `pattern`, `config`, `m`, `provenance` and `variant` as aux KEYS, three
# levels deep. If anything in pcrec interpreted one of them, the MAIN
# TABLE would carry a second `pattern` row, or `#section provenance`/
# `#section cases` would carry an extra record — [DD-13b.W23.4] now that
# `#section aux` exists and dumps the tree FAITHFULLY (the whole point of
# it), a nonzero row count THERE is correct and expected; what remains an
# absence claim is every OTHER surface.
adt_main="$(section_count "" "$WORKDIR/aux_deep_tree.dump")"
adt_cases="$(section_count "cases" "$WORKDIR/aux_deep_tree.dump")"
adt_prov="$(section_count "provenance" "$WORKDIR/aux_deep_tree.dump")"
adt_var="$(section_count "variants" "$WORKDIR/aux_deep_tree.dump")"
if [ "$adt_main" = "1" ] && [ "$adt_cases" = "1" ] && [ "$adt_prov" = "0" ] && [ "$adt_var" = "0" ]; then
    pass "aux/deep-tree: an aux body whose keys COLLIDE with format keywords (pattern, config, m, provenance, variant) produces NO extra block, NO extra case and NO provenance record — 1 main-table row, 1 real case (the genuine 'm' outside the ext body), 0 provenance, 0 variants"
else
    fail "aux/deep-tree: main=$adt_main (want 1) cases=$adt_cases (want 1) provenance=$adt_prov (want 0) variants=$adt_var (want 0).
  An aux body is UNINTERPRETED (§2.27.3): a key spelled like a format
  keyword is a key, and a reader that acted on one has graduated the
  production without anybody ruling that it should.
$(LC_ALL=C grep -v '^#' "$WORKDIR/aux_deep_tree.dump")"
fi

# `aux_subtree_extent.rxt` — §5.2a item 9's sharpest attack, run by the
# delivery on itself. An extent bug that SWALLOWS the next line and one
# that closes EARLY produce opposite symptoms, so the assertion is
# positive on TWO things rather than negative on one: the aux body's
# `m`-spelled key did not become a case, and the `pattern b+` line after
# the subtree still OPENED a block. [DD-13b.W23.4]: MAIN-TABLE rows only
# (2 pattern blocks) — the fixture's own `ext` body's rows now legitimately
# populate `#section aux`, which this check does not constrain.
ase_main="$(section_count "" "$WORKDIR/aux_subtree_extent.dump")"
if [ "$ase_main" = "2" ]; then
    pass "aux/subtree-extent: the open subtree ENDS at its dedent — the block directive after it is a directive and the 'pattern' line after that opens a SECOND block (2 main-table rows)"
else
    fail "aux/subtree-extent: the main table carries $ase_main rows where 2 is correct.
  Either the subtree ran on past its own body (swallowing the opener
  below it) or it closed early (turning one of its own lines into a
  block). The two failures are opposite and this is the one assertion
  that separates them."
fi

# The three HEADLESS aux fixtures are asserted on ALL THREE LEGS; the
# file-scope one is not, and the reason is the seam ruling rather than
# this lane's scope (w1_impl §1.1: the head has ONE parser, so a
# three-leg assertion on a FILE-scope production is unavailable at any
# point in W23 — r59-A2's own disposition, one production over).
for auxf in aux_deep_tree aux_literal_pipe aux_subtree_extent; do
    if "$TIMEOUT_BIN" 300 bash "$RUNSH" --dump "$FIXRUN/$auxf.rxt" > /dev/null 2>&1 && \
       "$TIMEOUT_BIN" 60 python3 "$VERIFY" --dump "$FIXRUN/$auxf.rxt" > /dev/null 2>&1; then
        pass "aux/$auxf: legs B and C accept it too (the aux body is consumed, not dispatched)"
    else
        fail "aux/$auxf: leg B or C refused an aux fixture leg A accepts. Inside
  an OPEN SUBTREE nothing is dispatched at all — S2's opener set is
  empty there and S3 never opens — so a leg that validated a key inside
  one has given the production semantics nobody ruled it should have."
    fi
done

check_refusal_all3 aux_malformed_body.rxt aux-malformed structure-attachment 'indented 3'

# --- `provenance`: S-R2's pcrec-side detector pair (§2.14 rule 3) -------
#
# LEG A ONLY, by the schema's own `validated_by` column: every
# `provenance` row reads `pcrec`, and legs B and C CONSUME the record's
# body without reading it. Claiming three legs here would be §3.3's
# named failure — a row claiming three legs on the strength of one.
check_refusal prov_adapted_no_adaptation.rxt prov-adaptation \
    '[schema-constraint]' 'adaptation' 'fidelity != verbatim'
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$FIXRUN/prov_verbatim_no_adaptation.rxt" \
        > /dev/null 2>"$WORKDIR/pv.err"; then
    pass "prov-adaptation: the ACCEPT half (fidelity verbatim, no adaptation) is accepted — the refusal is isolated to the conditional"
else
    fail "prov-adaptation: the accept control was REFUSED. Without it the
  refusing half is satisfied by a parser that refuses every provenance
  record, which is a check with no discriminating power at all:
  $(cat "$WORKDIR/pv.err")"
fi

# --- O-29 (pcrec-bench, 2026-09-16): the multi-block #section DROP ------
#
# See `o29_multi_provenance.rxtin`'s own header for the full mechanism.
# In short: a `provenance`/`variant` sub-block that is a block's LAST
# content, closed by a BLANK line or a COMMENT line (S0's "each closes
# every open attachment") rather than by a dedent onto another content
# line or by end of file, used to lose its `#section` row entirely — a
# raw `ndepth = 1` reset in `rxt_source.c`'s main loop skipped
# `RXT_CLOSE_FRAME` (and therefore `close_section_frame`) instead of
# calling it, which the dedent-pop while loop and the end-of-file loop
# both already did correctly. Only the textually LAST block's record
# survived, because only it closes at end of file — the one site that
# was never broken.
#
# LEG A ONLY, both `provenance`'s and `variant`'s own `validated_by`
# column (as the pre-existing prov-* checks above): legs B and C consume
# a sub-block's body without reading it, so a three-leg assertion here
# would claim coverage §3.3 rules out.
#
# `section_field SECTION COLUMN FILE` -> stdout: one line per row of
# SECTION, column COLUMN (1-based, tab-separated) — `section_count`'s own
# boundary tracking, extended to return a value instead of a count, so
# this and any future per-row assertion route through the ONE awk that
# knows where a `#section` block starts and ends.
section_field() {
    local want="$1" col="$2" file="$3"
    awk -F'\t' -v want="$want" -v col="$col" '
        /^#section /{ s=$0; sub(/^#section /,"",s); cur=s; next }
        $1 ~ /^#/ { next }
        cur == want { print $col }' "$file"
}

O29P="$FIXRUN/o29_multi_provenance.rxt"
O29P_OUT="$WORKDIR/o29p.tsv"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$O29P" > "$O29P_OUT" 2>"$WORKDIR/o29p.err"; then
    o29p_n="$(section_count provenance "$O29P_OUT")"
    o29p_lines="$(section_field provenance 1 "$O29P_OUT" | tr '\n' ' ')"
    o29p_blk="$(section_field provenance 2 "$O29P_OUT" | tr '\n' ' ')"
    o29p_names="$(section_field provenance 3 "$O29P_OUT" | tr '\n' ' ')"
    o29p_fid="$(section_field provenance 10 "$O29P_OUT" | tr '\n' ' ')"
    if [ "$o29p_n" = "3" ] && [ "$o29p_lines" = "35 43 52 " ] && \
       [ "$o29p_blk" = "32 41 50 " ] && [ "$o29p_names" = "p1 p2 p3 " ] && \
       [ "$o29p_fid" = "verbatim adapted verbatim " ]; then
        pass "O-29/provenance: all THREE blocks' provenance records are present (count=3), each attributed to its own block (line 35/43/52 -> block_line 32/41/50, name p1/p2/p3, fidelity verbatim/adapted/verbatim) — the blank-line (block 1), comment-line (block 2) and end-of-file (block 3) closing sites all flush the record"
    else
        fail "O-29/provenance: expected 3 rows at lines '35 43 52' / block_lines
  '32 41 50' / names 'p1 p2 p3' / fidelity 'verbatim adapted verbatim';
  got n=$o29p_n lines='$o29p_lines' block_lines='$o29p_blk'
  names='$o29p_names' fidelity='$o29p_fid' — a provenance record was
  dropped when its block's closing line was a blank or a comment (the
  bug this section exists to catch)."
    fi
else
    fail "O-29/provenance: --list-source refused the fixture (rc=$?): $(cat "$WORKDIR/o29p.err")"
fi

O29V="$FIXRUN/o29_multi_variant.rxt"
O29V_OUT="$WORKDIR/o29v.tsv"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$O29V" > "$O29V_OUT" 2>"$WORKDIR/o29v.err"; then
    o29v_n="$(section_count variants "$O29V_OUT")"
    o29v_lines="$(section_field variants 1 "$O29V_OUT" | tr '\n' ' ')"
    o29v_blk="$(section_field variants 2 "$O29V_OUT" | tr '\n' ' ')"
    o29v_names="$(section_field variants 3 "$O29V_OUT" | tr '\n' ' ')"
    o29v_testee="$(section_field variants 4 "$O29V_OUT" | tr '\n' ' ')"
    if [ "$o29v_n" = "3" ] && [ "$o29v_lines" = "20 25 30 " ] && \
       [ "$o29v_blk" = "18 23 28 " ] && [ "$o29v_names" = "p1 p2 p3 " ] && \
       [ "$o29v_testee" = "re2 tre onig " ]; then
        pass "O-29/variant: all THREE blocks' variant records are present (count=3), each attributed to its own block (line 20/25/30 -> block_line 18/23/28, name p1/p2/p3, testee re2/tre/onig) — the same blank/comment/EOF closing sites, the general mechanism rather than a provenance special case"
    else
        fail "O-29/variant: expected 3 rows at lines '20 25 30' / block_lines
  '18 23 28' / names 'p1 p2 p3' / testees 're2 tre onig'; got n=$o29v_n
  lines='$o29v_lines' block_lines='$o29v_blk' names='$o29v_names'
  testees='$o29v_testee' — the fix is not general enough to cover
  'variant', or covers 'provenance' by a scope-specific path."
    fi
else
    fail "O-29/variant: --list-source refused the fixture (rc=$?): $(cat "$WORKDIR/o29v.err")"
fi

# The SUPPRESSED-ORDER control: a `tag` line AFTER a block's `provenance`
# closes it through the (always-correct) dedent-pop path before any
# blank line is reached — pinning that this shape needed no fix and gets
# none, in the same direction the bench's own observation ran.
O29S="$FIXRUN/o29_suppressed_order.rxt"
O29S_OUT="$WORKDIR/o29s.tsv"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$O29S" > "$O29S_OUT" 2>"$WORKDIR/o29s.err"; then
    o29s_n="$(section_count provenance "$O29S_OUT")"
    o29s_lines="$(section_field provenance 1 "$O29S_OUT" | tr '\n' ' ')"
    o29s_blk="$(section_field provenance 2 "$O29S_OUT" | tr '\n' ' ')"
    if [ "$o29s_n" = "2" ] && [ "$o29s_lines" = "13 21 " ] && [ "$o29s_blk" = "12 20 " ]; then
        pass "O-29/suppressed-order: a 'tag' line AFTER provenance closes it via the dedent-pop path (always correct) — both blocks' records present, unaffected by the fix"
    else
        fail "O-29/suppressed-order: expected 2 rows at lines '13 21' / block_lines
  '12 20'; got n=$o29s_n lines='$o29s_lines' block_lines='$o29s_blk'"
    fi
else
    fail "O-29/suppressed-order: --list-source refused the fixture (rc=$?): $(cat "$WORKDIR/o29s.err")"
fi

# The `ext`/AUX CONTROL: `#section aux` rows are pushed PER LINE, never
# deferred to `RXT_CLOSE_FRAME`, and that macro is ALSO a no-op for a
# tree frame (`if (!(F)->tree)` guards both halves) — so this shape never
# shared O-29's bug, before or after the fix. Checked as a POPULATION
# (6 rows: an opener + one 'note' child per block, times 3 blocks) with
# per-block attribution, the same shape as the provenance/variant checks,
# to make "aux is unaffected" a measured artifact rather than an
# assertion.
O29A="$FIXRUN/o29_multi_aux_control.rxt"
O29A_OUT="$WORKDIR/o29a.tsv"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$O29A" > "$O29A_OUT" 2>"$WORKDIR/o29a.err"; then
    o29a_n="$(section_count aux "$O29A_OUT")"
    o29a_lines="$(section_field aux 1 "$O29A_OUT" | tr '\n' ' ')"
    o29a_blk="$(section_field aux 2 "$O29A_OUT" | tr '\n' ' ')"
    o29a_keys="$(section_field aux 6 "$O29A_OUT" | tr '\n' ' ')"
    if [ "$o29a_n" = "6" ] && [ "$o29a_lines" = "15 16 19 20 23 24 " ] && \
       [ "$o29a_blk" = "14 14 18 18 22 22 " ] && \
       [ "$o29a_keys" = "ext note ext note ext note " ]; then
        pass "O-29/aux-control: all THREE blocks' aux rows (opener + one child each, 6 total) are present at lines 15/16, 19/20, 23/24, correctly attributed to blocks 14/18/22 — 'ext' bodies never shared O-29's bug (their rows are pushed per line, and RXT_CLOSE_FRAME is a no-op on a tree frame either way)"
    else
        fail "O-29/aux-control: expected 6 rows at lines '15 16 19 20 23 24' /
  block_lines '14 14 18 18 22 22' / keys 'ext note ext note ext note';
  got n=$o29a_n lines='$o29a_lines' block_lines='$o29a_blk'
  keys='$o29a_keys'"
    fi
else
    fail "O-29/aux-control: --list-source refused the fixture (rc=$?): $(cat "$WORKDIR/o29a.err")"
fi

# --- `under`: the four-component KEY TUPLE (§2.17) ----------------------
#
# LEG A ONLY, by the schema's own column: `under` reads `validated_by:
# pcrec`, and legs B and C treat every `under` line as a counted,
# labelled SKIP. The ACCEPT half is not optional and is the half that
# found the defect: the extractor read a colon that the spelling does
# not have, so the convention came out empty and every later component
# slid one place left — and the refusing fixture went red anyway, for a
# reason that had nothing to do with the rule.
check_refusal under_key_duplicate.rxt under-key-dup \
    '[schema-constraint]' "duplicate 'under'" 'under-key'
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$FIXRUN/under_key_distinct.rxt" \
        > /dev/null 2>"$WORKDIR/ukd.err"; then
    pass "under-key: four 'under' lines differing in ONE component each (subject, startpos, kind, convention) are all ACCEPTED — the key is the whole tuple"
else
    fail "under-key: a line differing from its neighbour in exactly one key
  component was refused as a duplicate, so the tuple has collapsed. A
  refuse-only pair cannot see this — it passes for the wrong reason:
  $(cat "$WORKDIR/ukd.err")"
fi

# --- §2.22 / D100: the DERIVED-IDENTIFIER call binding ------------------
#
# LEG A ONLY: legs B and C resolve no calls. The refusal arrives through
# `--source` (the composer) and not `--list-source` (which reports the
# file as written and binds nothing), so this is the one W23.3 fixture
# whose instrument is the COMPILE path.
dcc_out="$("$TIMEOUT_BIN" 60 "$PCREC" --source "$FIXRUN/derived_call_collision.rxt" \
    -o "$WORKDIR/dcc.c" 2>&1)"
if [ $? -eq 0 ]; then
    fail "derived-call: a call to an identifier TWO definitions derive was
  ACCEPTED. The mapping is deliberately not injective and this refusal
  is where that is paid for; a silent tie-break makes the
  non-injectivity free exactly where it bites (§2.22)."
elif printf '%s' "$dcc_out" | grep -q "x-y" && \
     printf '%s' "$dcc_out" | grep -q "x_y"; then
    pass "derived-call: a colliding derived identifier is refused NAMING BOTH definitions and the shared identifier (exact spelling does not win)"
else
    fail "derived-call: refused, but the message does not name BOTH
  definitions. Naming only the shared prefix tells an author which
  identifier collided and not which two names to rename, which is the
  only repair available:
  $dcc_out"
fi
# The ACCEPT half: a hyphenated definition IS callable through its
# derived identifier, which is the whole of what D100 bought.
if "$TIMEOUT_BIN" 60 "$PCREC" --source "$FIXRUN/derived_call_bind.rxt" \
        -o "$WORKDIR/dcb.c" > /dev/null 2>"$WORKDIR/dcb.err"; then
    pass "derived-call: '(?&cls_upto_64)' BINDS to 'name cls-upto-64' — the repair §4.5 item 4 was unusable without"
else
    fail "derived-call: the accept half FAILED. Without it the collision
  refusal above is satisfied by a composer that binds nothing at all:
  $(cat "$WORKDIR/dcb.err")"
fi

# --- [DD-13b.W23.2] THE ATTACHMENT ARM's own fixtures (W23-S1, W23-S2) --
#
# `indent_pre_body.rxt` — an indented `m` line BEFORE the first
# `pattern`. THE POSITION IS THE CHECK (r57 S-M5): leg C's old
# indentation test ran AFTER its not-seen_pattern branch, so a
# POST-body fixture would report GREEN against the ordering defect this
# pins; leg B had no attachment step at all before this step.
# [DD-13b.W23.3] THE NEEDLE MOVED because leg A's own branch SPLIT. The
# arm this fixture reaches held three different mistakes under one
# sentence; "nothing above it is open" is the one that is true here (a
# blank line, a comment or the start of the file closes every
# attachment), and "the declaration above takes no continuation" was
# never true of it — there is no declaration above. See
# `src/parse/rxt_source.c`'s comment at the split.
check_refusal_all3 indent_pre_body.rxt indent-pre-body structure-attachment \
    'nothing above it is open'

# `indent_under_m.rxt` — an indented line under an `m` case line,
# mid-block. class structure-attachment, NAMING THE PARENT
# (`m` declares `children: none`) — S-R1's own detector (S239): flipping
# `m`'s `children` column makes leg A ACCEPT while legs B and C still
# REFUSE, so only the three-leg DIFFERENTIAL sees the row move.
#
# [FINDING] `w23_impl.md` §3.2's fixture table says this class is
# schema-constraint; the DELIVERED W23.1 code files every "indented line
# continues nothing" S1 failure under structure-attachment regardless of
# WHY (see the fixture's own header and this step's lane report). Legs B
# and C match leg A rather than the note.
check_refusal_all3 indent_under_m.rxt indent-under-m structure-attachment \
    "'m' takes no continuation"

# --- sem21: 'with'/'from' trailing whitespace is trimmed (head-only) --
WT="$FIXRUN/with_trailing_ws.rxt"
wt_out="$("$TIMEOUT_BIN" 30 "$PCREC" --list-source "$WT" 2>&1)"
if [ $? -ne 0 ]; then
    fail "sem21: --list-source refused the with-trailing-whitespace fixture:
  $wt_out"
else
    wt_with=$(printf '%s\n' "$wt_out" | awk -F'\t' '$1 == "target" { print $13 }')
    # AS WRITTEN, never resolved (§1.8): only TRAILING whitespace after the
    # whole list is trimmed, not the internal space after the comma -- the
    # list is stored as the author wrote it, minus the two trailing spaces.
    if [ "$wt_with" = "a, b" ]; then
        pass "sem21: 'target ... with a, b  ' dumps column 13 as 'a, b' — trailing whitespace trimmed, internal spacing kept AS WRITTEN"
    else
        fail "sem21: column 13 is '$wt_with', expected 'a, b' (trailing
  whitespace should be trimmed, matching every other token/list value)"
    fi
fi

# --- sem23: --list-source on a DIRECTORY must be refused, not silently
# read as an empty file (stat/EISDIR, previously unchecked).
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$FIXDIR" > "$WORKDIR/dir.out" 2>"$WORKDIR/dir.err"; then
    fail "sem23: --list-source ACCEPTED a directory and printed:
$(cat "$WORKDIR/dir.out")"
else
    pass "sem23: --list-source refuses a directory ($(cat "$WORKDIR/dir.err"))"
fi

# --- sem17 (discretionary): invalid UTF-8 no longer CRASHES leg C -----
# Synthesized here rather than committed as a static fixture, so a raw
# invalid byte never lands in the repository's own tree. 0xFF is not a
# valid UTF-8 lead byte in any position.
UTF="$WORKDIR/invalid_utf8.rxt"
printf 'pattern a\xffb\nm "a\xffb" 0 3\n' > "$UTF"
if "$TIMEOUT_BIN" 60 python3 "$VERIFY" --dump "$UTF" > "$WORKDIR/utf.out" 2>"$WORKDIR/utf.err"; then
    pass "sem17: verify_rxt.py --dump no longer crashes on an invalid-UTF-8 byte"
elif grep -qi 'UnicodeDecodeError' "$WORKDIR/utf.err"; then
    fail "sem17: verify_rxt.py STILL crashes with UnicodeDecodeError on an
  invalid-UTF-8 byte, which surrogateescape should have prevented:
$(tail -10 "$WORKDIR/utf.err")"
else
    # A non-zero exit for a REASON OTHER THAN a decode crash (e.g. the
    # byte landing somewhere the parser's own grammar refuses) is not
    # this finding's failure mode -- the point is byte-cleanliness, not
    # that every such file must dump successfully.
    pass "sem17: verify_rxt.py --dump did not crash with UnicodeDecodeError on an invalid-UTF-8 byte (exited for another reason, which is fine)"
fi

# --- sem10 (RULED 2026-08-30): a blank line ends a config body exactly
# as it ends a block scalar. Three observables: leg A parses the head
# correctly (config gets ONLY its pre-blank setting; the post-blank line
# is a FILE-level description, not swallowed into the config); the seam
# (run.sh) calls --list-source exactly once and runs the one pattern
# block correctly; leg C still refuses the head-bearing file by name
# (unaffected by this fix, asserted for completeness).
BE="$FIXRUN/blank_ends_config_body.rxt"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$BE" > "$WORKDIR/be.tsv" 2>"$WORKDIR/be.err"; then
    # [DD-13b.W23.4] stops at the first `#section` line: this fixture's
    # `m` case now grows a `#section cases` block, whose data rows do not
    # start with `#` and would otherwise be misread as more "kinds".
    be_kinds=$(awk -F'\t' '/^#section /{exit} !/^#/ { printf "%s ", $1 }' "$WORKDIR/be.tsv")
    be_cfg_flags=$(awk -F'\t' '$1 == "config" { print $6 }' "$WORKDIR/be.tsv")
    be_cfg_engine=$(awk -F'\t' '$1 == "config" { print $10 }' "$WORKDIR/be.tsv")
    be_desc=$(awk -F'\t' '$1 == "description" { print $4 }' "$WORKDIR/be.tsv")
    if [ "$be_kinds" = "config description pattern " ] && \
       [ "$be_cfg_flags" = "i" ] && [ -z "$be_cfg_engine" ] && \
       [ "$be_desc" = "this belongs to the FILE, not to config dev" ]; then
        pass "sem10: a blank line ends the config body — 'config dev' has only 'flags i', and the description after the blank is a separate FILE-level row"
    else
        fail "sem10: blank-line-ends-config-body fixture parsed wrong.
  kinds: '$be_kinds' (want 'config description pattern ')
  config flags: '$be_cfg_flags' (want 'i'), config engine: '$be_cfg_engine' (want empty)
  description: '$be_desc'"
    fi
else
    fail "sem10: --list-source REJECTED the blank-line-ends-config-body fixture:
$(cat "$WORKDIR/be.err")"
fi
: > "$CALLLOG"
if PCREC="$WRAPDIR/pcrec" "$TIMEOUT_BIN" 300 bash "$RUNSH" "$BE" > "$WORKDIR/be.run" 2>&1; then
    be_calls=$(grep -c -- '--list-source' "$CALLLOG" || true)
    be_pass=$(awk '/^cases passed:/ { print $3 }' "$WORKDIR/be.run")
    be_fail=$(awk '/^cases failed:/ { print $3 }' "$WORKDIR/be.run")
    if [ "${be_fail:-1}" = "0" ] && [ "${be_pass:-0}" = "1" ] && [ "$be_calls" = "1" ]; then
        pass "sem10: the seam — run.sh made exactly one --list-source call and ran the one pattern block, 1 pass / 0 fail"
    else
        fail "sem10: run.sh on the blank-ends-config-body fixture reported ${be_pass:-?} passed / ${be_fail:-?} failed / $be_calls --list-source call(s), expected 1 / 0 / 1:
$(tail -20 "$WORKDIR/be.run")"
    fi
else
    fail "sem10: run.sh FAILED on the blank-ends-config-body fixture:
$(tail -30 "$WORKDIR/be.run")"
fi
if python3 "$VERIFY" --dump "$BE" > /dev/null 2>&1; then
    fail "sem10: verify_rxt.py accepted a head-bearing file; it must refuse by name"
else
    pass "sem10: verify_rxt.py still refuses the head-bearing file by name (unaffected by this fix)"
fi

# =====================================================================
# [DD-13b.W1.2] TARGETS, THE OUTPUT-NAMING RULE, AND rx_info.name
# =====================================================================
#
# W1.1 PARSED `target` and `config` and resolved neither. This section is
# where resolution stops being a promise. Everything it checks has a
# population of ZERO on the corpus for the same reason the head path does
# — no corpus file declares a target — so it is fixtures all the way down,
# and each one names the thing it makes reachable.
#
# THE COMPILES ARE NEW HERE. This section used to be three parses and no
# compiles at all, which is what kept it cheap enough to run beside
# `test-corpus`. Building a `.rxt` source cannot be checked without
# building one; the fixtures are small and the count is in single digits.

W12="$WORKDIR/w12"
mkdir -p "$W12"
TC="$FIXRUN/three_configs.rxt"

# --- N targets -> N artifacts, N prefixes, ONE name -------------------
#
# The `-o <dir>` form, which is the only one that can express several
# targets at all. Four assertions, and the fourth is the one the step is
# named for: the three artifacts must agree on `rx_info.name` and DISAGREE
# on their prefixes, because one definition built three ways is three
# builds of ONE matcher and a consumer walking three `<prefix>_info`
# symbols needs to be able to say so.
mkdir -p "$W12/dir"
if "$TIMEOUT_BIN" 60 "$PCREC" --source "$TC" -o "$W12/dir" 2>"$W12/dir.err"; then
    w12_c=$(ls "$W12/dir"/*.c 2>/dev/null | wc -l | tr -d ' ')
    w12_h=$(ls "$W12/dir"/*.h 2>/dev/null | wc -l | tr -d ' ')
    w12_names=$(grep -h -m1 '^    \.name = ' "$W12/dir"/*.c 2>/dev/null | LC_ALL=C sort -u | wc -l | tr -d ' ')
    w12_name1=$(grep -h -m1 '^    \.name = ' "$W12/dir"/log_base.c 2>/dev/null)
    if [ "$w12_c" = "3" ] && [ "$w12_h" = "3" ] && \
       [ -f "$W12/dir/log_base.c" ] && [ -f "$W12/dir/log_strict.c" ] && \
       [ -f "$W12/dir/log_big.c" ] && \
       [ "$w12_names" = "1" ] && [ "$w12_name1" = '    .name = "level_filter",' ]; then
        pass "W1.2: 3 targets -> 3 .c + 3 .h named for their PREFIXES, all three stamping the one rx_info.name \"level_filter\""
    else
        fail "W1.2: the three-config file did not produce three prefixed pairs with one shared name.
  .c files: $w12_c (want 3), .h files: $w12_h (want 3)
  distinct .name values: $w12_names (want 1), log_base's: '$w12_name1'
  dir listing: $(ls "$W12/dir" | tr '\n' ' ')"
    fi
    # The prefixes must genuinely differ IN THE EMITTED SYMBOLS, not only in
    # the file names — a `-o <dir>` implementation that named files per
    # target while compiling them all under `rx` would satisfy everything
    # above.
    if grep -q '^int log_strict_search(' "$W12/dir/log_strict.c" && \
       grep -q '^int log_big_search('    "$W12/dir/log_big.c"; then
        pass "W1.2: each artifact's entry points carry its OWN target prefix"
    else
        fail "W1.2: an artifact's emitted entry does not carry its target's prefix:
$(grep -h '^int .*_search(' "$W12/dir"/*.c)"
    fi
else
    fail "W1.2: --source -o <dir> failed on the three-config fixture:
$(cat "$W12/dir.err")"
fi

# --- the `features` UNION, which nothing else can reach ---------------
#
# §1.5's per-kind table makes `features` the ONE directive that UNIONS a
# target's configs with the block's own line instead of letting the block
# win. Without a file where BOTH sides are non-empty that branch has a
# population of ZERO, so this is the only place it is observable. The
# evidence is the artifact's own D37 stamp — `classes` comes from
# `baseline` (which `strict` and `big` inherit through `from`) and
# `named-groups` from the block, so a target that took only one side, or
# let the block win outright, stamps a different list.
#
# MEASURED against the shipped binary before this check was written: a
# two-member list is accepted and stamps `"classes,named-groups"`, while a
# WHOLE-SPEC word inside a list (`all,classes`) is refused by
# `pcrec_enabled_set_spec` in its own words — which is why the resolver
# restates no vocabulary of its own.
w12_un_bad=""
for w12_t in log_base log_strict log_big; do
    w12_got="$(LC_ALL=C grep -m1 '^#define PCREC_FEATURE_MODULES ' "$W12/dir/$w12_t.c" 2>/dev/null)"
    [ "$w12_got" = '#define PCREC_FEATURE_MODULES "classes,named-groups"' ] || \
        w12_un_bad="$w12_un_bad  $w12_t -> ${w12_got:-<none>}"
done
if [ -z "$w12_un_bad" ]; then
    pass "W1.2: \`features\` UNIONS the target's configs with the block's own line — all three artifacts stamp \"classes,named-groups\""
else
    fail "W1.2: the features UNION did not reach the artifact:$w12_un_bad
  want: #define PCREC_FEATURE_MODULES \"classes,named-groups\"
  (classes comes from config baseline, named-groups from the block; a
  target taking only one side, or letting the block win outright, is
  exactly what this asserts against)"
fi

# --- `-o out.c` with N > 1 is REFUSED, naming both ways forward -------
if "$TIMEOUT_BIN" 60 "$PCREC" --source "$TC" -o "$W12/one.c" >"$W12/one.out" 2>&1; then
    fail "W1.2: --source -o <file> ACCEPTED a three-target file; it must refuse"
else
    w12_msg="$(cat "$W12/one.out")"
    w12_miss=""
    for w12_need in log_base log_strict log_big -- --target DIRECTORY; do
        case $w12_msg in *"$w12_need"*) ;; *) w12_miss="$w12_miss '$w12_need'" ;; esac
    done
    if [ -z "$w12_miss" ]; then
        pass "W1.2: -o <file> with 3 targets is refused, naming every target AND both ways forward (--target, an existing DIRECTORY)"
    else
        fail "W1.2: the multi-target -o refusal does not name:$w12_miss
  message: $w12_msg"
    fi
fi

# --- `--target` selects one, and it is the one asked for --------------
if "$TIMEOUT_BIN" 60 "$PCREC" --source "$TC" --target log_strict -o "$W12/sel.c" 2>"$W12/sel.err"; then
    if [ -f "$W12/sel.h" ] && grep -q '^int log_strict_search(' "$W12/sel.c" && \
       grep -q '^    \.name = "level_filter",' "$W12/sel.c"; then
        pass "W1.2: --target builds exactly the named target, one .c/.h pair, prefix log_strict, name level_filter"
    else
        fail "W1.2: --target log_strict produced the wrong artifact:
$(grep -h '^int .*_search(\|^    \.name = ' "$W12/sel.c" 2>/dev/null)"
    fi
else
    fail "W1.2: --source --target failed: $(cat "$W12/sel.err")"
fi
if "$TIMEOUT_BIN" 60 "$PCREC" --source "$TC" --target nosuch -o "$W12/x.c" >"$W12/nt.out" 2>&1; then
    fail "W1.2: --target nosuch was ACCEPTED"
else
    if grep -q 'log_base' "$W12/nt.out" && grep -q 'log_strict' "$W12/nt.out"; then
        pass "W1.2: an unknown --target is refused and LISTS the targets the file does declare"
    else
        fail "W1.2: the unknown-target refusal does not list the real targets: $(cat "$W12/nt.out")"
    fi
fi

# --- the three agree, end to end through run.sh (H11) -----------------
#
# §6.3's "identity between them is a free control", run. run.sh builds
# each target through `--source --target` and requires it to answer this
# block's own cases exactly as the block's own compile did. The
# `--source` CALL COUNT is asserted through the wrapper for the reason the
# seam's own check asserts `--list-source`'s: three green cases would also
# be true of a run.sh that never built a target at all.
: > "$CALLLOG"
if PCREC="$WRAPDIR/pcrec" "$TIMEOUT_BIN" 300 bash "$RUNSH" "$TC" > "$W12/tc.run" 2>&1; then
    w12_srccalls=$(grep -c -- '--source' "$CALLLOG" || true)
    w12_pass=$(awk '/^cases passed:/ { print $3 }' "$W12/tc.run")
    w12_fail=$(awk '/^cases failed:/ { print $3 }' "$W12/tc.run")
    if [ "${w12_fail:-1}" = "0" ] && [ "${w12_pass:-0}" = "3" ] && [ "$w12_srccalls" = "3" ]; then
        pass "W1.2 (H11): run.sh built all 3 targets (3 --source calls) and they answered the block's 3 cases identically to its own compile"
    else
        fail "W1.2 (H11): run.sh on the three-config fixture reported ${w12_pass:-?} passed / ${w12_fail:-?} failed / $w12_srccalls --source call(s), expected 3 / 0 / 3.
  Zero --source calls means the target build path did not fire and the
  agreement control asserted nothing.
$(tail -25 "$W12/tc.run")"
    fi
else
    fail "W1.2 (H11): run.sh FAILED on the three-config fixture:
$(tail -30 "$W12/tc.run")"
fi

# --- the refusals, each asserting what its message must NAME ----------
#
# `check_refusal` above is `--list-source`'s helper and cannot be reused:
# these are RESOLUTION refusals, and `--list-source` accepts every one of
# these files by design (it reports the file AS WRITTEN and touches no
# filesystem). That difference is itself asserted below, on lib_missing.
w12_refuse() {
    local fixture="$1" label="$2"; shift 2
    local f="$FIXRUN/$fixture" out="$W12/$label.out" miss="" need
    if "$TIMEOUT_BIN" 60 "$PCREC" --source "$f" -o "$W12/$label.c" >"$out" 2>&1; then
        fail "W1.2 ($label): --source ACCEPTED $fixture; it must refuse"
        return
    fi
    for need in "$@"; do
        grep -qF -- "$need" "$out" || miss="$miss '$need'"
    done
    if [ -z "$miss" ]; then
        pass "W1.2 ($label): refused, naming $*"
    else
        fail "W1.2 ($label): the refusal does not name:$miss
  message: $(cat "$out")"
    fi
}
# The needles are the CONTRACT (§1.3: name the definition AND the lib chain
# searched), never the prose. An earlier version of this row asserted the
# string 'W1.3' — a D26 tier-3 pointer sitting at the message's tail, which
# is exactly the part `rxt_fail`'s documented truncation rule eats first.
w12_refuse no_such_definition.rxt nodef  'level_filter' 'no definition' 'searched'
w12_refuse lib_missing.rxt        libmiss 'extra_defs.rxt' 'no readable file' 'searched'
w12_refuse lib_store.rxt          libstore '<common>' 'NOT IN THIS BUILD' 'LIB'
w12_refuse config_pcrec_escape.rxt cfgesc  'compile options only' 'prefix'

# --- NO REFUSAL MAY BE TRUNCATED, which is a CLASS check --------------
#
# `pcrec_error.msg` is a FIXED 256 bytes and already holds a path and a
# line number, so a refusal that spends its budget on prose loses its TAIL
# — and §1.3 puts CONTRACT content (the definition name, the `lib` chain
# searched) in exactly the place that is lost. MEASURED before this check
# existed: the no-such-definition refusal was cut off at EVERY path length
# tried, including a 20-byte one, so it never met its contract on any
# input and the truncation hid that rather than announcing it.
#
# The instance was caught by a proxy needle; this is the CLASS, and it is
# the check that would have found it directly. It bounds the whole message
# (pcrec's own "pcrec: " prefix included) below the buffer, so a refusal
# that grows past it fails HERE rather than silently shedding whatever it
# was contractually required to say.
w12_trunc_bad=""
for w12_fx in no_such_definition lib_missing lib_store config_pcrec_escape; do
    w12_n=$("$TIMEOUT_BIN" 60 "$PCREC" --source "$FIXRUN/$w12_fx.rxt" \
                -o "$W12/trunc.c" 2>&1 >/dev/null | wc -c)
    [ "$w12_n" -lt 263 ] || \
        w12_trunc_bad="$w12_trunc_bad  $w12_fx: $w12_n bytes (limit 263)"
done
if [ -z "$w12_trunc_bad" ]; then
    pass "W1.2: no resolution refusal reaches pcrec_error.msg's 256-byte buffer — the CONTRACT half of each message survives, since truncation eats the tail"
else
    fail "W1.2: a resolution refusal is TRUNCATED, so whatever §1.3 requires it to name may be the part that was cut:$w12_trunc_bad
  rxt_fail truncates the TAIL (keeping file:line), so contract content must
  come BEFORE prose. Shorten the message; do not raise the buffer."
fi

# `--list-source` still ACCEPTS the file whose lib does not resolve. The
# two surfaces answer different questions and only one of them touches the
# filesystem; a resolver bolted into the parser would have broken this.
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$FIXRUN/lib_missing.rxt" >/dev/null 2>&1; then
    pass "W1.2: --list-source still accepts a file whose 'lib' path does not resolve (AS WRITTEN never touches the filesystem)"
else
    fail "W1.2: --list-source refused a file that only --source has grounds to refuse"
fi

# --- --lib-path is the SAME file's cure, which is its only real check --
mkdir -p "$W12/libs"
cp "$FIXRUN/common.rxt" "$W12/libs/extra_defs.rxt"
if "$TIMEOUT_BIN" 60 "$PCREC" --source "$FIXRUN/lib_missing.rxt" \
        --lib-path "$W12/libs" -o "$W12/viapath.c" 2>"$W12/viapath.err"; then
    pass "W1.2: --lib-path resolves the very reference that fails without it — the flag's one consumer today"
else
    fail "W1.2: --lib-path did not resolve a reference to a file that is in the named directory:
$(cat "$W12/viapath.err")"
fi

# --- a library ships nothing by itself (format_design §6.1) -----------
#
# Zero targets is NOT an error, and the two outcomes must stay distinct:
# a file that CANNOT be built refuses (above), a file that DECLARES
# nothing to build exits 0 and writes no artifact. A resolver that treated
# "nothing to build" as a failure would make every library file a build
# error; one that silently wrote something would be worse.
rm -f "$W12/lib.c" "$W12/lib.h"
if "$TIMEOUT_BIN" 60 "$PCREC" --source "$FIXRUN/common.rxt" -o "$W12/lib.c" 2>"$W12/lib.err"; then
    if [ ! -f "$W12/lib.c" ] && grep -q 'builds nothing' "$W12/lib.err"; then
        pass "W1.2: a definitions-only file builds NOTHING at exit 0, and says so on stderr (distinct from a refusal)"
    else
        fail "W1.2: --source on a library file exited 0 but did not behave as one.
  artifact written: $([ -f "$W12/lib.c" ] && echo yes || echo no) (want no)
  stderr: $(cat "$W12/lib.err")"
    fi
else
    fail "W1.2: --source REFUSED a definitions-only file; a library ships nothing by itself, which is not an error:
$(cat "$W12/lib.err")"
fi

# --- the compatibility default: no target + ONE UNNAMED block ---------
#
# Frank's format_design §6.4 rule, and the reason every one of the 191
# corpus files could be built with no head at all. It is checked on a
# scratch file rather than a corpus one only so the population is visible
# in this script.
printf 'pattern a+\nm "aaa" 0 3\n' > "$W12/lone.rxt"
if "$TIMEOUT_BIN" 60 "$PCREC" --source "$W12/lone.rxt" -o "$W12/lone.c" 2>"$W12/lone.err"; then
    if grep -q '^int rx_search(' "$W12/lone.c" && \
       grep -q '^    \.name = "rx",' "$W12/lone.c"; then
        pass "W1.2: no target + exactly ONE UNNAMED block builds the implicit \`target rx\` (format_design §6.4), naming itself \"rx\""
    else
        fail "W1.2: the implicit target did not produce an rx-prefixed, rx-named artifact:
$(grep -h '^int .*_search(\|^    \.name = ' "$W12/lone.c")"
    fi
else
    fail "W1.2: --source refused a single-unnamed-block file, which is the compatibility default's whole population:
$(cat "$W12/lone.err")"
fi

# --- [RULEFIX] `--engine` CLI-vs-config precedence (2026-09-15) -------
#
# Frank's ruling (w235 finding 2, cli/main.c:890-891): a target's own
# `engine vm` row silently overrode an explicit CLI `--engine=dfa` with no
# diagnostic. Fixed so an EXPLICIT CLI `--engine=` wins, with a non-fatal
# stderr diagnostic naming both sources and both values. Both directions,
# on `engine_cli_precedence.rxt` (one unnamed block, block-scoped
# `engine vm`, the implicit `target rx` default this section already
# established above).
EP="$FIXRUN/engine_cli_precedence.rxt"

# Direction 1: the CLI is silent (no --engine at all) — the file's row
# applies, exactly as every OTHER axis's file-wins rule already does, and
# nothing is printed about it.
if "$TIMEOUT_BIN" 60 "$PCREC" --source "$EP" -o "$W12/ep_silent.c" 2>"$W12/ep_silent.err"; then
    if grep -q '^#define RX_ENGINE "vm"' "$W12/ep_silent.c" && \
       [ ! -s "$W12/ep_silent.err" ]; then
        pass "W1.2 (RULEFIX): CLI silent -> the file's \`engine vm\` row applies, no diagnostic"
    else
        fail "W1.2 (RULEFIX): CLI-silent build did not stamp RX_ENGINE \"vm\" cleanly:
  RX_ENGINE line: $(grep '^#define RX_ENGINE' "$W12/ep_silent.c")
  stderr (want empty): $(cat "$W12/ep_silent.err")"
    fi
else
    fail "W1.2 (RULEFIX): --source refused the CLI-silent engine-precedence fixture:
$(cat "$W12/ep_silent.err")"
fi

# Direction 2: an EXPLICIT, CONFLICTING CLI --engine=dfa must WIN over the
# file's `engine vm` row (not be silently discarded by it), and the
# conflict must be reported on stderr naming both sources and both
# values, non-fatally (exit 0, artifact still written).
if "$TIMEOUT_BIN" 60 "$PCREC" --engine=dfa --source "$EP" -o "$W12/ep_conflict.c" \
        2>"$W12/ep_conflict.err"; then
    if grep -q '^#define RX_ENGINE "dfa"' "$W12/ep_conflict.c" && \
       grep -q -- '--engine=dfa' "$W12/ep_conflict.err" && \
       grep -q 'engine vm' "$W12/ep_conflict.err"; then
        pass "W1.2 (RULEFIX): explicit CLI --engine=dfa WINS over the file's \`engine vm\`, with a diagnostic naming both"
    else
        fail "W1.2 (RULEFIX): CLI --engine=dfa did not win over the file's \`engine vm\` row, or the diagnostic did not name both sides:
  RX_ENGINE line: $(grep '^#define RX_ENGINE' "$W12/ep_conflict.c")
  stderr: $(cat "$W12/ep_conflict.err")"
    fi
else
    fail "W1.2 (RULEFIX): --engine=dfa --source refused the engine-precedence fixture (the conflict must be a non-fatal diagnostic, not a refusal):
$(cat "$W12/ep_conflict.err")"
fi

# Direction 2b: an explicit CLI --engine=vm that AGREES with the file's
# `engine vm` row must build silently — no conflict to report, since the
# two sides say the same thing.
if "$TIMEOUT_BIN" 60 "$PCREC" --engine=vm --source "$EP" -o "$W12/ep_agree.c" \
        2>"$W12/ep_agree.err"; then
    if grep -q '^#define RX_ENGINE "vm"' "$W12/ep_agree.c" && \
       [ ! -s "$W12/ep_agree.err" ]; then
        pass "W1.2 (RULEFIX): CLI --engine=vm agreeing with the file's \`engine vm\` builds silently (no conflict to report)"
    else
        fail "W1.2 (RULEFIX): an agreeing CLI --engine=vm printed a spurious diagnostic or the wrong stamp:
  RX_ENGINE line: $(grep '^#define RX_ENGINE' "$W12/ep_agree.c")
  stderr (want empty): $(cat "$W12/ep_agree.err")"
    fi
else
    fail "W1.2 (RULEFIX): --engine=vm --source refused the engine-precedence fixture:
$(cat "$W12/ep_agree.err")"
fi

# =====================================================================
# [DD-13b.W1.3] COMPOSITION, THE NAME GRAMMAR, AND THE DOGFOOD
# =====================================================================
#
# Three things this section owns, and each had a population of ZERO before
# the fixtures beside it existed -- no corpus file declares a "name" at all,
# measured 0 of 191, which is why they are fixtures and not corpus files:
#
#   the NAME GRAMMAR    a definition name admits "-" and "." after its first
#                       byte, and "target = <name>" derives the C prefix by
#                       mapping them to "_"; two names mapping to one prefix
#                       is a refusal that names BOTH
#   COMPOSITION         a definition own named groups reach groups[] with a
#                       non-NULL ref, sorted BELOW the primary rows, so
#                       nentries > nnames for the first time
#   THE DOGFOOD         pcrec-bench altwide@0.2 as an .rxt source, verbatim,
#                       33 pattern ids a person chose
#
# EVERY ASSERTION HERE READS THE EMITTED ARTIFACT AS TEXT, never the
# composer own report of what it did. The behavioural half -- a composed
# artifact answering what a hand-written flat one does -- is a different
# question and lives in tests/definitions/, with an outside oracle.

W13="$WORKDIR/w13"
mkdir -p "$W13"

# --- the name grammar, and the derived prefix -------------------------
#
# The block names are cls-upto-64 and ctx.lazy; the artifacts must be
# cls_upto_64 and ctx_lazy, and each must carry its ORIGINAL name. The two
# are different fields answering different questions: the prefix is what the
# symbols are called, the name is what the artifact IS
# (docs/spec/match_api.md section 6), and a build that mapped one into the
# other would lose the bench id this whole ruling exists to preserve.
mkdir -p "$W13/nd"
if "$TIMEOUT_BIN" 60 "$PCREC" --source "$FIXRUN/name_dashdot.rxt" -o "$W13/nd" 2>"$W13/nd.err"; then
    nd_files=$(cd "$W13/nd" && ls ./*.c 2>/dev/null | sed 's|^\./||' | sort | tr '\n' ' ')
    if [ "$nd_files" = "cls_upto_64.c ctx_lazy.c " ]; then
        pass "W1.3 names: a dash or dot in a definition name maps to underscore in the derived prefix ($nd_files)"
    else
        fail "W1.3 names: expected 'cls_upto_64.c ctx_lazy.c ', got '$nd_files'"
    fi
    nd_names=$(grep -h '^    \.name = ' "$W13/nd"/*.c | sed 's/.*= "\(.*\)",$/\1/' | sort | tr '\n' ' ')
    if [ "$nd_names" = "cls-upto-64 ctx.lazy " ]; then
        pass "W1.3 names: each artifact keeps its ORIGINAL name ($nd_names) while its symbols carry the mapped prefix"
    else
        fail "W1.3 names: rx_info.name should be the UNMAPPED block name; got '$nd_names'"
    fi
else
    fail "W1.3 names: --source refused a file whose definitions carry a dash and a dot:
$(cat "$W13/nd.err")"
fi

# --- the collision refusal, and it must name BOTH definitions ---------
#
# The mapping is deliberately not injective -- one that could not collide
# would have to mangle a name its author wrote -- so the refusal is where
# that is paid for. Naming only the shared prefix would leave a reader unable
# to tell which two of their names produced it, so all three of a-b, a.b and
# a_b are required in the message.
coll_out="$("$TIMEOUT_BIN" 30 "$PCREC" --list-source "$FIXRUN/target_prefix_collision.rxt" 2>&1)"
coll_rc=$?
coll_miss=""
for tok in "a-b" "a.b" "a_b"; do
    case "$coll_out" in *"$tok"*) ;; *) coll_miss="$coll_miss $tok" ;; esac
done
if [ "$coll_rc" != "0" ] && [ -z "$coll_miss" ]; then
    pass "W1.3 collision: two names mapping to one prefix are refused, naming both definitions and the prefix"
else
    fail "W1.3 collision: exit $coll_rc, missing from the message:$coll_miss
  got: $coll_out"
fi

# --- composition: the delivered row, its ref, and nentries > nnames ----
#
# piece is (?<kept>a)(b)(c)\2 bound into ^(?&piece)$. All three of D89 tiers
# fire in one artifact: kept is NAMED (delivered), (b) is referenced by the
# definition own \2 (hidden), (c) is unnamed and unread (erased, spending no
# number at all).
if "$TIMEOUT_BIN" 60 "$PCREC" --features all --source "$FIXRUN/compose_delivers.rxt" \
        -o "$W13/user.c" 2>"$W13/user.err"; then
    u_rows="$(grep -E '^    \{ "' "$W13/user.c" || true)"
    u_ngroups="$(grep -m1 '^    \.ngroups = ' "$W13/user.c" | tr -dc '0-9')"
    u_nnames="$(grep -m1 '^    \.nnames = ' "$W13/user.c" | tr -dc '0-9')"
    u_nentries="$(grep -m1 '^    \.nentries = ' "$W13/user.c" | tr -dc '0-9')"
    u_ncaps="$(grep -m1 -oE '^#define USER_NCAPS [0-9]+' "$W13/user.h" | awk '{print $3}')"

    if printf '%s\n' "$u_rows" | grep -q '{ "d.kept", [0-9]*, [0-9]*, "piece" }'; then
        pass "W1.3 delivery: the definition exported group reaches groups[] as d.kept with ref piece"
    else
        fail "W1.3 delivery: no row for d.kept with ref piece. Rows:
$u_rows"
    fi
    # THE FIRST TIME THE TWO NUMBERS DIFFER. nnames counts the PRIMARY rows
    # and nentries the whole array; the caller pattern declares no named
    # group, so 0 and 1 is the strongest possible form of the claim.
    if [ "$u_nnames" = "0" ] && [ "$u_nentries" = "1" ]; then
        pass "W1.3: nentries ($u_nentries) > nnames ($u_nnames) -- the injected row is counted by one and not the other"
    else
        fail "W1.3: expected nnames=0 and nentries=1 on a caller that declares no name of its own; got $u_nnames / $u_nentries"
    fi
    # THE ERASED TIER, AS A NUMBER. The definition has three groups: `kept` is
    # exported AND delivered by the site, `(b)` is reached by the definition's
    # own \2, and `(c)` is neither -- so `(c)` is ERASED. Four numbers are
    # spent (wrapper, kept, (b), and the SITE's own slot for d.kept) and the
    # caller declares none, so RX_NCAPS is 5. A build whose erased tier
    # stopped erasing would read 6.
    if [ "$u_ngroups" = "0" ] && [ "$u_ncaps" = "5" ]; then
        pass "W1.3 erasure: ngroups=0, RX_NCAPS=5 -- the unnamed, unreferenced group spent NO number"
    else
        fail "W1.3 erasure: expected ngroups=0 and RX_NCAPS=5; got $u_ngroups / $u_ncaps.
  RX_NCAPS 6 means the erased tier stopped erasing."
    fi
else
    fail "W1.3: --source could not build the composition fixture:
$(cat "$W13/user.err")"
fi

# --- the three composition refusals -----------------------------------
#
# Q-W2 (D89 point 3): whole-pattern recursion inside a bound definition is
# refused because the RULING is missing, not the meaning. A by-name call the
# closure cannot satisfy RE-RAISES module backrefs own sentence, which is
# what keeps the four perr blocks in tests/recursion/d27/sr_refusals.rxt at
# today wording. And one name declared in two files of the closure is the
# duplicate-block-name rule one scope out, naming both files.
w13_refuse() {
    local fixture="$1" label="$2"; shift 2
    local out rc miss="" need
    out="$("$TIMEOUT_BIN" 60 "$PCREC" --features all --source "$FIXRUN/$fixture" \
             -o "$W13/refuse.c" 2>&1)"
    rc=$?
    for need in "$@"; do
        case "$out" in *"$need"*) ;; *) miss="$miss [$need]" ;; esac
    done
    if [ "$rc" != "0" ] && [ -z "$miss" ]; then
        pass "W1.3 refusal: $label"
    else
        fail "W1.3 refusal ($label): exit $rc, missing:$miss
  got: $out"
    fi
}
w13_refuse compose_root_recursion.rxt \
    "whole-pattern recursion inside a bound definition (Q-W2), naming the definition and its file:line" \
    "selfy" "compose_root_recursion.rxt:" "whole-pattern recursion"
w13_refuse compose_unknown_name.rxt \
    "a by-name call the closure cannot satisfy re-raises the parser own sentence, unchanged" \
    "nosuch" "which this pattern does not declare"
w13_refuse compose_dup_definition.rxt \
    "one definition name declared in two files of the closure, naming both" \
    "word" "common.rxt" "compose_dup_definition.rxt"

# --- [D89 addenda] export, the delivering call, and the five refusals ----
#
# EACH OF THESE HAD A POPULATION OF ZERO before its fixture existed, and four
# of the five are shapes no `.rxt` in the tree can otherwise reach: the export
# list, the site-qualified row, the flat import and the clash rules all need a
# COMPOSED build, and the corpus composes nothing.
w13_refuse deliver_export_nogroup.rxt \
    "an export naming a group the definition does not declare, naming both" \
    "nosuch" "piece" "declares no capture group"
w13_refuse deliver_deliver_noexport.rxt \
    "a delivering call on a definition that exports nothing (the DEFAULT), naming both" \
    "piece" "exports nothing"
w13_refuse deliver_clash_caller.rxt \
    "a flat import landing on a group the caller already has" \
    "kept" "already has"
w13_refuse deliver_clash_twoflat.rxt \
    "two flat imports exporting one name — neither is the caller's own" \
    "kept" "already has"
w13_refuse deliver_clash_samesite.rxt \
    "two delivering calls sharing a site name (the qualified side of one rule)" \
    "s.kept" "already has"

# --- the three call forms, as EMITTED ROWS -------------------------------
#
# Read off the artifact as text, never off the composer's report. The three
# assertions are about the three things a caller can see and cannot infer from
# each other: WHICH rows exist, whether they carry a `ref`, and whether
# `nnames` counts them.
w13_rows() {
    local target="$1" want="$2" label="$3"
    local out
    if ! "$TIMEOUT_BIN" 60 "$PCREC" --features all \
            --source "$FIXRUN/deliver_forms.rxt" --target "$target" \
            -o "$W13/$target.c" 2>"$W13/$target.err"; then
        fail "W1.3 forms ($label): --source --target $target failed:
$(cat "$W13/$target.err")"
        return
    fi
    out="$(LC_ALL=C sed -n 's/^    { "\([^"]*\)".*$/\1/p' "$W13/$target.c" | sort | tr '\n' ' ')"
    if [ "$out" = "$want" ]; then
        pass "W1.3 forms: $label emits rows [$out]"
    else
        fail "W1.3 forms ($label): expected rows [$want], got [$out]"
    fi
}
w13_rows plaincall "" "a PLAIN call delivers nothing"
w13_rows sitecall "s.kept s.other " "(?&s=name) delivers site-qualified rows"
w13_rows selfcall "piece.kept piece.other " "(?&=name) uses the definition's own name as the site"
w13_rows flatcall "kept other " "(?&*=name) delivers FLAT into the caller's scope"

# THE `ref` COLUMN AND `nnames` TOGETHER, because they are one decision seen
# twice: a site-qualified row is a LIBRARY row (non-NULL ref, below nnames,
# invisible to §6's algorithm), a flat row is the CALLER's (NULL ref, counted
# by nnames, found by that algorithm). Getting one right and the other wrong
# is the shape that would let a caller's bsearch walk into a library group.
if grep -q '{ "s.kept", [0-9]*, [0-9]*, "piece" }' "$W13/sitecall.c" &&
   [ "$(grep -m1 '^    \.nnames = ' "$W13/sitecall.c" | tr -dc '0-9')" = "0" ]; then
    pass "W1.3 forms: a site-qualified row carries ref=\"piece\" and is NOT counted by nnames"
else
    fail "W1.3 forms: the site-qualified row's ref/nnames pair is wrong:
$(grep -hE '^    \{ \"|^    \.nnames = ' "$W13/sitecall.c")"
fi
# A FLAT ROW IS THE CASE THAT SEPARATES THE TWO QUESTIONS, and it is the
# reason the sort key is the SCOPE and not `ref` (manager's ruling,
# 2026-09-03 19:1x): it came from a library, so it carries a `ref`, AND it
# lives in the caller's own scope, so it is inside the `nnames` prefix where
# §6's bsearch will find it. A build that keyed the sort on `ref` would emit
# the same row with `nnames` 0 and pass any check that looked at only one of
# the two numbers.
if grep -q '{ "kept", [0-9]*, [0-9]*, "piece" }' "$W13/flatcall.c" &&
   [ "$(grep -m1 '^    \.nnames = ' "$W13/flatcall.c" | tr -dc '0-9')" = "2" ]; then
    pass "W1.3 forms: a FLAT row keeps ref=\"piece\" (provenance) AND is counted by nnames (the caller's scope)"
else
    fail "W1.3 forms: the flat row's ref/nnames pair is wrong — it must carry BOTH:
$(grep -hE '^    \{ \"|^    \.nnames = ' "$W13/flatcall.c")"
fi

# THE PER-COMPOSITION ERASURE, as a NUMBER (D89 addendum 4(1)). The definition
# has three groups and exports two; a PLAIN caller delivers none of them, so
# all three are erased and only the wrapper spends a number — RX_NCAPS 2. A
# build that kept an exported-but-undelivered group would read 4, and one that
# kept every named group (the model the addendum WITHDREW) would read 4 too.
pc_ncaps="$(grep -m1 -oE '^#define PLAINCALL_NCAPS [0-9]+' "$W13/plaincall.h" | awk '{print $3}')"
if [ "$pc_ncaps" = "2" ]; then
    pass "W1.3 erasure: a plain caller of a definition that exports two groups pays for NONE of them (RX_NCAPS 2)"
else
    fail "W1.3 erasure: expected RX_NCAPS 2 on the plain-call target, got $pc_ncaps.
  4 means an exported-but-undelivered group still spends a number, which is the
  model D89's addendum withdrew."
fi

# --- Q-W4: a definition's own `encoding` must agree with the artifact's --
#
# BOTH DIRECTIONS, because a refusal that fired on ANY `encoding` line on a
# definition would pass the negative arm while being wrong: `ok` binds a
# definition that states the encoding the artifact IS built for, and must
# compose silently. THE HOME OF THIS ROW is here rather than tests/reject/:
# that table is per-CONSTRUCT and its point is the MODULE name, and this is
# a `.rxt` source refusal with no construct and no module.
if "$TIMEOUT_BIN" 60 "$PCREC" --features all --source "$FIXRUN/compose_encoding_clash.rxt" \
        --target ok -o "$W13/enc_ok.c" 2>"$W13/enc_ok.err"; then
    pass "W1.3 Q-W4: a definition stating the encoding the artifact IS built for composes silently"
else
    fail "W1.3 Q-W4: a definition whose encoding MATCHES the artifact was refused:
$(cat "$W13/enc_ok.err")"
fi
enc_out="$("$TIMEOUT_BIN" 60 "$PCREC" --features all --source "$FIXRUN/compose_encoding_clash.rxt" \
             --target clash -o "$W13/enc_bad.c" 2>&1)"
enc_rc=$?
enc_miss=""
for tok in "other" "utf8" "byte"; do
    case "$enc_out" in *"$tok"*) ;; *) enc_miss="$enc_miss $tok" ;; esac
done
if [ "$enc_rc" != "0" ] && [ -z "$enc_miss" ]; then
    pass "W1.3 Q-W4: a definition whose encoding differs is REFUSED, naming the definition and both encodings"
else
    fail "W1.3 Q-W4: exit $enc_rc, missing from the message:$enc_miss
  got: $enc_out"
fi

# --- THE DOGFOOD: the bench set as a source ---------------------------
#
# The claim is NOT that these patterns match anything in particular -- the
# bench owns those expectations and the oracle that produced them. It is that
# the FORMAT carries a real consumer real set: 33 ids a person chose, 32 of
# them not C identifiers, one alternation of 4,096 branches on a single
# pattern line.
#
# THE LOSSLESSNESS IS ASSERTED AGAINST THE BENCH OWN FILES WHERE THEY EXIST,
# and against the fixture alone where they do not. pcrec-bench is a sibling
# repo, not a dependency: a checkout without it must not fail this section,
# so the byte-for-byte arm SKIPS LOUDLY and the structural arm always runs.
AW="$FIXRUN/bench_altwide_0_2.rxt"
aw_targets=$(grep -c '^target = ' "$AW")
aw_blocks=$(grep -c '^pattern ' "$AW")
if [ "$aw_targets" = "33" ] && [ "$aw_blocks" = "33" ]; then
    pass "W1.3 dogfood: the altwide fixture carries 33 targets and 33 blocks"
else
    fail "W1.3 dogfood: expected 33 targets and 33 blocks, got $aw_targets / $aw_blocks"
fi
if "$TIMEOUT_BIN" 120 "$PCREC" --list-source "$AW" > "$W13/aw.tsv" 2>"$W13/aw.err"; then
    aw_rows=$(grep -vc '^#' "$W13/aw.tsv")
    aw_dups=$(awk -F'\t' '$1 == "target" { print $3 }' "$W13/aw.tsv" | sort | uniq -d | wc -l | tr -d ' ')
    if [ "$aw_rows" = "66" ] && [ "$aw_dups" = "0" ]; then
        pass "W1.3 dogfood: --list-source reads all 66 rows and the 33 derived prefixes are distinct"
    else
        fail "W1.3 dogfood: $aw_rows rows (want 66), $aw_dups colliding prefixes (want 0)"
    fi
else
    fail "W1.3 dogfood: --list-source refused the bench set as a source:
$(cat "$W13/aw.err")"
fi
# The SMALL one, built end to end. A large one would make this section pay
# the bench own compile cost, which is the bench business and not this
# suite -- w-8 is 56 bytes and eight branches.
if "$TIMEOUT_BIN" 120 "$PCREC" --source "$AW" --target w_8 -o "$W13/w8.c" 2>"$W13/w8.err"; then
    if grep -q '^    \.name = "w-8",' "$W13/w8.c"; then
        pass "W1.3 dogfood: a bench pattern builds through --source --target, keeping its id w-8 as rx_info.name"
    else
        fail "W1.3 dogfood: the w_8 artifact does not carry the name w-8:
$(grep -h '^    \.name = ' "$W13/w8.c")"
    fi
else
    fail "W1.3 dogfood: --source --target w_8 failed on the bench set:
$(cat "$W13/w8.err")"
fi
# BYTE-FOR-BYTE AGAINST THE BENCH OWN FILES, when they are there. This is
# the only arm that can catch the fixture drifting away from the set it
# claims to be a copy of -- a provenance header is a claim, and a claim
# nothing checks is a comment.
BENCH_PAT="${PCREC_BENCH_PATTERNS:-/home/duxevents/pcrec-bench/bench/altwide/patterns}"
if [ -d "$BENCH_PAT" ]; then
    aw_bad=0 aw_seen=0
    for bf in "$BENCH_PAT"/*.rx; do
        bn=$(basename "$bf" .rx)
        aw_seen=$((aw_seen + 1))
        want=$(cat "$bf")
        got=$(awk -v want="$bn" '
            /^pattern / { p = substr($0, 9); next }
            /^name /    { if ($2 == want) { print p; exit } }' "$AW")
        [ "$got" = "$want" ] || aw_bad=$((aw_bad + 1))
    done
    if [ "$aw_seen" = "33" ] && [ "$aw_bad" = "0" ]; then
        pass "W1.3 dogfood: all 33 patterns are byte-for-byte the bench own .rx files (the .rxt round trip is the identity)"
    else
        fail "W1.3 dogfood: $aw_bad of $aw_seen patterns differ from the bench own files.
  The fixture provenance header claims it is a verbatim copy; either it drifted
  or the bench set moved. Regenerate it or update the header."
    fi
else
    echo "SKIP: W1.3 dogfood byte-for-byte arm: $BENCH_PAT not present (pcrec-bench is a sibling repo, not a dependency)"
fi

# =====================================================================
# [DD-13b.W23.1] THE STRUCTURE LAYER, AND THE SCHEMA'S OWN SURFACE
# =====================================================================
#
# format_design.md §1.2.1 states the layer a reader with NO keyword table
# sees — four line classes, one attachment rule, one grouping rule, one
# opaque-region rule — parameterized by exactly THREE schema columns. The
# cells below are §9.1's / w23_impl §3.2's fixture table for the rows this
# step lands. Every one is LEG A ONLY and that is the staging rather than
# the rule: legs B and C gain their attachment arm and their child
# consumption at W23.2, and asserting three legs here would be asserting a
# claim about two parsers that have not been taught yet.
#
# THE TWO NARROWINGS ARE REGRESSIONS, NOT ASSERTIONS. `config_tab_body`
# and `config_mixed_indent` are ACCEPTED at rc 0 on the pre-W23 binary, so
# each fixture pins a reject that did not exist; the three AVOIDED
# narrowings (`prose_hash`, `prose_ragged`, `prose_paragraph_break`) were
# accepted before and are accepted still, which is what an avoidance
# needs and an accident does not.

# accept_value FIXTURE LABEL KIND COLUMN WANT — the file is accepted and
# the named row's column holds exactly WANT. Asserting the VALUE rather
# than the verdict is the point in every prose cell: a reader that opened
# a region and threw its content away still "accepts" the file.
accept_value() {
    local fixture=$1 label=$2 kind=$3 col=$4 want=$5
    local out rc got
    out="$("$TIMEOUT_BIN" 30 "$PCREC" --list-source "$FIXRUN/$fixture" 2>&1)"
    rc=$?
    if [ "$rc" != "0" ]; then
        fail "w23s1/$label: --list-source REFUSED $fixture, which must be accepted.
  got: $out"
        return
    fi
    got="$(printf '%s\n' "$out" | awk -F'\t' -v k="$kind" -v c="$col" \
             '$1 == k { print $c; exit }')"
    if [ "$got" = "$want" ]; then
        pass "w23s1/$label: accepted, and the $kind row's column $c is exactly the expected value"
    else
        fail "w23s1/$label: accepted, but the $kind row's column $c reads
  got:  $got
  want: $want"
    fi
}

# S3: an indented `#` inside a region is PROSE (§1.6.1a candidate (2), a
# narrowing AVOIDED — pinning the avoidance is what a decision needs).
accept_value prose_hash.rxt prose-hash description 4 \
    'first prose line\n# this is prose, not a comment\nthird prose line'

# S3: ragged prose is legal and RELATIVE indentation survives the dedent.
accept_value prose_ragged.rxt prose-ragged description 4 \
    'level one\n  level two, deeper\nlevel one again'

# S0: a whitespace-only line inside a region ends NOTHING and is bytes —
# the format's only paragraph break, asserted on the VALUE because a
# reader that ended the region there still accepts the file.
accept_value prose_paragraph_break.rxt prose-para description 4 \
    'first paragraph\n\nsecond paragraph'

# [K57FIX] K57 IS FIXED: a continuation line indented LESS than the
# block's own dedent depth is now REFUSED by name, class value-shape —
# r59-R4's own predicted signal (this WAS an `accept_value` pin on
# today's wrong decoded value; the fix broke it, and it is inverted here
# rather than left red). HEAD-SCOPED, so leg A only — legs B and C never
# read the head (the seam ruling); `prose-dedent-body` below is their
# three-leg sibling.
check_refusal prose_dedent.rxt prose-dedent-K57 \
    'continuation is indented' 'less than' 'delete content'

# [K57FIX] THE THREE-LEG SIBLING: the identical shape at BLOCK scope, so
# legs B (`run.sh`'s `prose_take`) and C (`verify_rxt.py`'s prose-region
# arm) — which carry the SAME byte-count dedent K57 named in leg A — are
# exercised too, not merely fixed and unreached. Class-compared like every
# other `check_refusal_all3_kind` row; `description` already carries
# `validated_by: all-readers` (§3.3), so this row's receipt joins the
# kind's existing population.
check_refusal_all3_kind description prose_dedent_body.rxt prose-dedent-body \
    value-shape 'continuation is indented' 'less than'

# S0: whitespace-only lines are INERT at every position, asserted as "the
# parse is IDENTICAL to the same file with them deleted" rather than as
# "the file is accepted" — the rejected attachment-relevant reading would
# have refused a whitespace-only FIRST line and one after a blank, and an
# acceptance-only check cannot see the difference.
WSP="$FIXRUN/ws_only_line_positions.rxt"
WSPD="$WORKDIR/ws_only_deleted.rxt"
grep -v '^[[:space:]][[:space:]]*$' "$WSP" > "$WSPD"
wsp_a="$("$TIMEOUT_BIN" 30 "$PCREC" --list-source "$WSP" 2>&1)"; wsp_ra=$?
wsp_b="$("$TIMEOUT_BIN" 30 "$PCREC" --list-source "$WSPD" 2>&1)"; wsp_rb=$?
if [ "$wsp_ra" != "0" ] || [ "$wsp_rb" != "0" ]; then
    fail "w23s1/ws-positions: a file with whitespace-only lines at four positions
  was refused (rc $wsp_ra / twin $wsp_rb). They are INERT: no indent is read
  off one, it attaches to nothing and nothing attaches to it."
elif [ "$(printf '%s\n' "$wsp_a" | awk -F'\t' -v OFS='\t' \
       '/^#section /{insect=1} $1 ~ /^#/{next} {if(insect){$1="-";$2="-"}else $2="-";print}')" = \
       "$(printf '%s\n' "$wsp_b" | awk -F'\t' -v OFS='\t' \
       '/^#section /{insect=1} $1 ~ /^#/{next} {if(insect){$1="-";$2="-"}else $2="-";print}')" ]; then
    pass "w23s1/ws-positions: whitespace-only lines at four positions parse IDENTICALLY to their own deletion"
else
    fail "w23s1/ws-positions: the parse differs from the same file with the
  whitespace-only lines deleted — one of them had a structural effect.
  (Line numbers are excluded from the comparison; nothing else is.)"
fi

# §1.6.1a narrowing (4), TAKEN: indentation is SPACES, and a tab in the
# indentation is refused BY NAME. Both fixtures parse at rc 0 on the
# pre-W23 binary, so each IS its narrowing's regression.
check_refusal config_tab_body.rxt tab-indent 'TAB' 'indentation is spaces'
check_refusal config_mixed_indent.rxt mixed-indent 'TAB'

# S1: a COMMENT closes every open attachment exactly as a BLANK does, so
# the line BELOW one continues nothing. THE POSITION IS THE ASSERTION —
# both fixtures put a real body line under the comment, and the refusal
# must name THAT line rather than the comment.
for pair in "comment_in_config_body.rxt:14:comment-ends-config" \
            "comment_in_prose_region.rxt:12:comment-ends-region"; do
    cf="${pair%%:*}"; rest="${pair#*:}"; cl="${rest%%:*}"; cn="${rest#*:}"
    cout="$("$TIMEOUT_BIN" 30 "$PCREC" --list-source "$FIXRUN/$cf" 2>&1)"
    if [ $? = "0" ]; then
        fail "w23s1/$cn: --list-source ACCEPTED $cf. A comment TERMINATES an
  attachment; under the transparent reading the line below it re-attaches
  and the file parses, which is a reject->accept widening."
    elif printf '%s' "$cout" | grep -q ":$cl:"; then
        pass "w23s1/$cn: refused at line $cl — the line BELOW the comment, not the comment"
    else
        fail "w23s1/$cn: refused, but not at line $cl. The position is the check:
  a refusal naming the comment would pass a reader that ended the
  attachment one line too early.
  got: $cout"
    fi
done

# ---------------------------------------------------------------------
# W23-S3 — `--list-schema` AGAINST WHAT LEG A ENFORCES
#
# It must NOT compare the dump to the table: that is the same source
# twice (docs/dev/learnings.md §3). Each arm below drives a BEHAVIOUR the
# dump claims and compares the result, so a hand-written dump that
# disagreed with the enforced table on one row fails here (sabotage S241).
#
# AND IT NEEDS A DENOMINATOR IT DOES NOT GET FROM THE DUMP. A check that
# iterates the dump's rows cannot see a row that is MISSING — its
# population is defined by the thing it checks, so a truncated table
# agrees with it by construction. The dump prints a COMPILE-TIME total
# from the `.def`'s own expansion (`# schema-rows:`), and the first arm
# asserts the printed rows against it.
SCHEMA="$WORKDIR/schema.tsv"
"$TIMEOUT_BIN" 30 "$PCREC" --list-schema > "$SCHEMA" 2>"$WORKDIR/schema.err" || \
    fail "W23-S3: --list-schema failed: $(cat "$WORKDIR/schema.err")"

sc_total=$(awk '/^# schema-rows:/ { print $3 }' "$SCHEMA")
sc_printed=$(awk -F'\t' 'BEGIN{s=0} /^#section schema/{s=1;next} /^#section /{s=0} s && $1 !~ /^#/ && NF>1 {n++} END{print n+0}' "$SCHEMA")
if [ -n "$sc_total" ] && [ "$sc_printed" = "$sc_total" ]; then
    pass "W23-S3 denominator: --list-schema printed all $sc_total rows the compiled table holds"
else
    fail "W23-S3 denominator: --list-schema printed $sc_printed row(s); the
  compiled table holds ${sc_total:-<no '# schema-rows:' line>}. A dropped row
  must FAIL this check rather than shrink the population every other arm
  below iterates."
fi

# The table contract, on BOTH sections — `--list-schema` is a conforming
# producer and its own structural check routes through tests/lib/table.sh
# rather than hand-rolling a positional read, which is the half of the
# contract the `NF != 15` incident was in.
for sect in schema surface; do
    if bash "$ROOT_DIR/tests/lib/table.sh" table-check "$SCHEMA" "$sect" 2>"$WORKDIR/tc.err"; then
        pass "W23-S3 contract: --list-schema's #section $sect satisfies HEADER TRUTHFULNESS"
    else
        fail "W23-S3 contract: --list-schema's #section $sect disagrees with its own
  header's declared field count: $(cat "$WORKDIR/tc.err")"
    fi
done

# ARM 1 — the OPENER SET (structure-layer parameter 1) is what actually
# opens a group. For every row the dump calls an opener, a second line of
# that kind must start a NEW block; for a row it does not, it must not.
sc_openers=$(awk -F'\t' 'BEGIN{s=0} /^#section schema/{s=1;next} /^#section /{s=0} s && $1 !~ /^#/ && $4 == "true" { print $2 }' "$SCHEMA" | tr '\n' ' ')
op_bad=0; op_seen=0
for k in $sc_openers; do
    op_seen=$((op_seen + 1))
    of="$WORKDIR/opener_$op_seen.rxt"
    printf '%s a\nm "a" 0 1\n%s b\nm "b" 0 1\n' "$k" "$k" > "$of"
    # [DD-13b.W23.4] every opener probe carries an `m` case now, so the
    # dump grows a `#section cases` block — MAIN-TABLE rows only, counted
    # the same section-aware way R5/R6 above count them.
    nb=$("$TIMEOUT_BIN" 30 "$PCREC" --list-source "$of" 2>/dev/null | \
         awk -F'\t' '/^#section /{exit} $1 !~ /^#/ && $1 != "" { n++ } END { print n+0 }')
    # a kind of a LATER wave is refused by name, which is a different
    # claim and is arm 4's; only a row this build implements can open.
    w=$(awk -F'\t' -v kk="$k" 'BEGIN{s=0} /^#section schema/{s=1;next} /^#section /{s=0} s && $2 == kk { print $10; exit }' "$SCHEMA")
    if [ "$w" != "1" ]; then continue; fi
    [ "$nb" = "2" ] || { op_bad=$((op_bad + 1)); echo "  opener '$k' produced $nb row(s), want 2" >&2; }
done
if [ "$op_seen" -ge 1 ] && [ "$op_bad" = "0" ]; then
    pass "W23-S3 arm 1: every row the dump calls an opener ($op_seen) starts a new block when a second one appears"
else
    fail "W23-S3 arm 1: $op_bad of $op_seen declared openers did not start a block.
  'opens_group' is structure-layer parameter 1 and a generic reader FETCHES
  it; a row that claims it and does not do it is a confident wrong answer."
fi

# ARM 2 — a NON-opener must not open a group. The control on arm 1: if
# every kind started a block, arm 1 would pass vacuously.
printf 'pattern a\nm "a" 0 1\nname one\nm "aa" 0 1\n' > "$WORKDIR/nonopener.rxt"
nb=$("$TIMEOUT_BIN" 30 "$PCREC" --list-source "$WORKDIR/nonopener.rxt" 2>/dev/null | \
     awk -F'\t' '$1 == "pattern" { n++ } END { print n+0 }')
if [ "$nb" = "1" ]; then
    pass "W23-S3 arm 2: a kind the dump does NOT call an opener starts no block (arm 1's control)"
else
    fail "W23-S3 arm 2: a non-opener produced $nb block rows, want 1"
fi

# ARM 3 — the PROSE PAIR (parameter 2). Every row the dump reports with
# `value = prose` AND `children = prose` must open a region on a trimmed
# bare `|`; and `pattern |`, whose row is NOT in that set, must stay a
# legal pattern rather than becoming a refusal. The second half is the
# one that fails if the trigger is read as "any bare `|` value".
printf 'pattern |\nm "" 0 0\n' > "$WORKDIR/pat_pipe.rxt"
pp=$("$TIMEOUT_BIN" 30 "$PCREC" --list-source "$WORKDIR/pat_pipe.rxt" 2>/dev/null | \
     awk -F'\t' '$1 == "pattern" { print $5; exit }')
if [ "$pp" = "|" ]; then
    pass "W23-S3 arm 3a: 'pattern |' is a pattern, not a prose region — the trigger reads the KIND"
else
    fail "W23-S3 arm 3a: 'pattern |' dumped its pattern column as '$pp'.
  Read literally, 'a line whose value is a bare |' opens a region on any
  such line, which turns a working file into a refusal."
fi
printf 'description |\n  prose\n\npattern a\nm "a" 0 1\n' > "$WORKDIR/desc_pipe.rxt"
dp=$("$TIMEOUT_BIN" 30 "$PCREC" --list-source "$WORKDIR/desc_pipe.rxt" 2>/dev/null | \
     awk -F'\t' '$1 == "description" { print $4; exit }')
if [ "$dp" = "prose" ]; then
    pass "W23-S3 arm 3b: a row the dump reports as the prose PAIR does open a region"
else
    fail "W23-S3 arm 3b: a declared prose-pair row decoded '$dp', not its region"
fi

# ARM 4 — the `wave` column. Every row above this build's wave must refuse
# BY NAME as NOT IN THIS BUILD (never as an unknown token: K14's shape),
# and every row AT it must not. That is what makes SW13's "not in this
# build" list DERIVED rather than hand-kept.
#
# THE RESERVED SENTINEL IS ITS OWN SUB-POPULATION (arm 4b), not a member
# of this one: a reserved keyword (`version`, SW13) has NO delivery behind
# it, so "NOT IN THIS BUILD" — which promises a wave that will bring it —
# would be a lie about it, and its required shape is the RESERVED refusal
# by name. Both sentinels come from the dump's own trailer comments, never
# from a copy of internal.h's constants. (Whether the reserved refusal's
# CLASS tag should stay [unknown-token-in-scope] or gain its own class is
# W23.2's question — the class vocabulary is decided there, not here.)
sc_built=$(awk '/^# wave-built:/ { print $3 }' "$SCHEMA")
sc_reserved=$(awk '/^# wave-reserved:/ { print $3 }' "$SCHEMA")
if [ -z "$sc_reserved" ]; then
    fail "W23-S3 arm 4: the dump carries no '# wave-reserved:' trailer —
  arm 4b's population boundary is gone and a reserved row would be swept
  into the NOT-IN-THIS-BUILD population it cannot satisfy."
fi
wv_bad=0; wv_seen=0
# THE ROW LIST IS BUILT BY awk AND NOT BY `read`, and that is not a style
# choice: bash's `read` COLLAPSES TAB-delimited EMPTY fields even under a
# single-character IFS (the defect `docs/dev/lanes/tt4m3_report.md`
# records), and most schema rows have an empty `constraints` cell — so a
# `while IFS=$'\t' read` over this dump shifts every later column left and
# the `wave` field it lands on is somebody else's. Measured here: the arm
# read 0 rows out of a population of 7 and reported 0/0, which is a green
# vacuity rather than a failure.
wv_rows="$(awk -F'\t' -v built="${sc_built:-1}" -v rsv="${sc_reserved:-999}" '
    BEGIN { s = 0 }
    /^#section schema/ { s = 1; next }
    /^#section /       { s = 0 }
    s && $1 == "file" && $10 + 0 > built + 0 && $10 + 0 < rsv + 0 { print $2 }' "$SCHEMA")"
for kind in $wv_rows; do
    wv_seen=$((wv_seen + 1))
    printf '%s x\npattern a\nm "a" 0 1\n' "$kind" > "$WORKDIR/wave.rxt"
    wout=$("$TIMEOUT_BIN" 30 "$PCREC" --list-source "$WORKDIR/wave.rxt" 2>&1)
    case $wout in
        *"NOT IN THIS BUILD"*) ;;
        *) wv_bad=$((wv_bad + 1)); echo "  '$kind' refused as: $wout" >&2 ;;
    esac
done
# [DD-13b.W23.3] THE EXTRACTOR'S HEALTH IS ITS OWN ASSERTION NOW, AND
# THAT IS WHAT MAKES AN HONEST ZERO REPORTABLE.
#
# W23.1 wrote "a population of ZERO is also a failure here" and was right
# for its reason: the arm had first read 0 rows out of a real population
# of 7 because `read` collapsed the dump's empty TAB fields, and a check
# whose population comes from the data it checks agrees with a broken
# extractor by construction. That rule conflates TWO zeros, and W23.3 is
# the pin where they part: `refuse_wave`'s NOT-IN-THIS-BUILD tier is
# `built < wave < reserved`, every W23 row's wave IS this build's, and no
# fixture can construct a row in between because the table is
# compile-time. format_design §1.3 and w23_impl §2.3 both state that
# emptiness IN ADVANCE ("its population is empty at the FINAL pin").
#
# So the extractor is exercised INDEPENDENTLY, over the same dump with
# the same awk and the threshold lowered to 0 — which must find every
# file-scope row below the sentinel. A zero there is the broken-extractor
# zero and still fails; a zero in the real population with a healthy
# extractor is the tier being empty, which is reported as a PASS that
# says so. The general form: *a population of zero is a failure only
# while you cannot tell it from a broken instrument; make the
# instrument's health a separate non-vacuous assertion and the honest
# zero becomes something a check may report.*
wv_probe="$(awk -F'\t' -v rsv="${sc_reserved:-999}" '
    BEGIN { s = 0; n = 0 }
    /^#section schema/ { s = 1; next }
    /^#section /       { s = 0 }
    s && $1 == "file" && $10 + 0 > 0 && $10 + 0 < rsv + 0 { n++ }
    END { print n }' "$SCHEMA")"
if [ "${wv_probe:-0}" -lt 1 ]; then
    fail "W23-S3 arm 4: the row extractor found ZERO file-scope rows below
  the reserved sentinel with the wave threshold lowered to 0, which is
  impossible on any non-empty schema. The extraction is broken (W23.1
  measured this exact shape once: bash's \`read\` collapsing the dump's
  empty TAB fields), so arm 4's own zero below means nothing."
elif [ "$wv_seen" = "0" ]; then
    pass "W23-S3 arm 4: the NOT-IN-THIS-BUILD tier is EMPTY at this pin (no schema row sits between wave $sc_built and the reserved sentinel $sc_reserved) — an honest zero, with the extractor independently shown live on $wv_probe rows. format_design §1.3 states this emptiness in advance; arm 4b carries the reserved tier, which is not empty"
elif [ "$wv_bad" = "0" ]; then
    pass "W23-S3 arm 4: all $wv_seen file-scope rows above wave $sc_built refuse BY NAME as NOT IN THIS BUILD"
else
    fail "W23-S3 arm 4: $wv_bad of $wv_seen later-wave file-scope rows did not
  refuse by name. A reader told 'unknown' goes hunting a typo in a word
  that is in the format's own spec (K14's shape)."
fi

# ARM 4b — the RESERVED sentinel's rows. A reserved keyword refuses BY
# NAME as RESERVED: the word is the format's, no build parses it, and no
# wave is coming (SW13). A population of ZERO fails for arm 4's reason —
# the spec claims `version` is reserved, and a claim needs a producer.
rv_bad=0; rv_seen=0
rv_rows="$(awk -F'\t' -v rsv="${sc_reserved:-999}" '
    BEGIN { s = 0 }
    /^#section schema/ { s = 1; next }
    /^#section /       { s = 0 }
    s && $1 == "file" && $10 + 0 == rsv + 0 { print $2 }' "$SCHEMA")"
for kind in $rv_rows; do
    rv_seen=$((rv_seen + 1))
    printf '%s x\npattern a\nm "a" 0 1\n' "$kind" > "$WORKDIR/rsv.rxt"
    rout=$("$TIMEOUT_BIN" 30 "$PCREC" --list-source "$WORKDIR/rsv.rxt" 2>&1)
    case $rout in
        *RESERVED*) ;;
        *) rv_bad=$((rv_bad + 1)); echo "  '$kind' refused as: $rout" >&2 ;;
    esac
done
if [ "$rv_seen" -ge 1 ] && [ "$rv_bad" = "0" ]; then
    pass "W23-S3 arm 4b: all $rv_seen reserved-sentinel file-scope rows refuse BY NAME as RESERVED"
else
    fail "W23-S3 arm 4b: $rv_bad of $rv_seen reserved-sentinel rows did not
  refuse by name as RESERVED. A population of ZERO is also a failure:
  SW13's 'version is reserved' is a spec claim, and this arm is its
  producer-side check."
fi

# ARM 5 — CARDINALITY, DRIVEN FROM THE DUMP'S OWN CLAIM PER ROW.
#
# Six settings kinds silently LAST-WON before this step while a seventh in
# the same family refused, so any value the schema writes is a
# compatibility decision. This arm is what makes the column one pcrec
# actually keeps: for every BLOCK row this build implements, it reads what
# the DUMP says and drives the corresponding behaviour — a second
# occurrence must be REFUSED where the dump says `at-most-one` and
# ACCEPTED where it says `repeat`. Both directions, per row, so a dump
# that mislabels one row fails here whichever way it lies (sabotage S241).
#
# THE PROBE VALUES ARE A TABLE AND THE TABLE IS CHECKED. A kind needs a
# line that is VALID for it or the probe measures the value grammar
# instead of the cardinality, and a kind with no entry must FAIL rather
# than be skipped — a skipped row is exactly the population nobody counts.
probe_line() {
    case $1 in
        name)            echo 'name one' ;;
        description)     echo 'description some text' ;;
        export)          echo 'export g1' ;;
        flags)           echo 'flags i' ;;
        features)        echo 'features classes' ;;
        encoding)        echo 'encoding byte' ;;
        engine)          echo 'engine vm' ;;
        perr)            echo 'perr' ;;
        m)               echo 'm "a" 0 1' ;;
        ms)              echo 'ms "a" 0 0 1' ;;
        n)               echo 'n "b"' ;;
        ns)              echo 'ns "b" 0' ;;
        g)               echo 'g 1 0 1' ;;
        gp)              echo 'gp 1 0 1' ;;
        gu)              echo 'gu steps "a"' ;;
        frames-buffer=)  echo 'frames-buffer=64' ;;
        *)               return 1 ;;
    esac
}
card_bad=0; card_seen=0; card_noprobe=""
card_rows="$(awk -F'\t' '
    BEGIN { s = 0 }
    /^#section schema/ { s = 1; next }
    /^#section /       { s = 0 }
    s && $1 == "block" && $10 == "1" && $4 != "true" && $6 != "accumulate" \
        { print $2 "|" $6 }' "$SCHEMA")"
for row in $card_rows; do
    k="${row%%|*}"; card="${row##*|}"
    ln="$(probe_line "$k")" || { card_noprobe="$card_noprobe $k"; continue; }
    card_seen=$((card_seen + 1))
    { echo 'pattern a'; echo "$ln"; echo "$ln"; } > "$WORKDIR/card.rxt"
    if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$WORKDIR/card.rxt" >/dev/null 2>&1
    then accepted=1; else accepted=0; fi
    case $card in
        at-most-one) [ "$accepted" = "0" ] || { card_bad=$((card_bad + 1)); echo "  '$k': dump says at-most-one, a second one was ACCEPTED" >&2; } ;;
        repeat)      [ "$accepted" = "1" ] || { card_bad=$((card_bad + 1)); echo "  '$k': dump says repeat, a second one was REFUSED" >&2; } ;;
        *)           card_bad=$((card_bad + 1)); echo "  '$k': unhandled cardinality '$card'" >&2 ;;
    esac
done
if [ -n "$card_noprobe" ]; then
    fail "W23-S3 arm 5: no probe line for:$card_noprobe
  A row with no probe is a row this arm SKIPS, and a skipped row is the
  population nobody counts. Add its line to probe_line() above."
elif [ "$card_seen" -ge 6 ] && [ "$card_bad" = "0" ]; then
    pass "W23-S3 arm 5: all $card_seen block rows behave as the dump's cardinality column says, in BOTH directions"
else
    fail "W23-S3 arm 5: $card_bad of $card_seen block rows disagree with the
  dump's own cardinality column (or the population fell below 6, which
  would mean this arm stopped reaching its rows)."
fi

# `budget` is the one ACCUMULATE row and it is excluded from the sweep
# above on purpose: its unit is the FIELD, not the line, so "the same line
# twice" is the wrong probe. The corpus writes both fields in one block
# deliberately (tests/harness/giveup.rxt), which is the measurement that
# kept it off the at-most-one list.
printf 'pattern a\nbudget steps=50\nbudget frames=4096\nm "a" 0 1\n' > "$WORKDIR/card_acc.rxt"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$WORKDIR/card_acc.rxt" >/dev/null 2>&1; then
    pass "W23-S3 arm 5c: 'budget' accumulates over its field set — two FIELDS in one block are legal"
else
    fail "W23-S3 arm 5c: two 'budget' FIELDS in one block were refused; the
  dump calls the row accumulate and a shipped corpus file writes exactly
  this shape"
fi

# ARM 6 — `children`. A row the dump calls `children: none` must refuse an
# indented line under it, naming the PARENT; a row naming a scope must
# accept one. Without the control, a parser that refused every indented
# line would pass the first half.
printf 'pattern a\nm "a" 0 1\n  indented\n' > "$WORKDIR/ch_none.rxt"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$WORKDIR/ch_none.rxt" >/dev/null 2>&1; then
    fail "W23-S3 arm 6a: an indented line under a children:none row was ACCEPTED"
else
    pass "W23-S3 arm 6a: an indented line under a children:none row is refused"
fi
printf 'config c\n  flags i\n\npattern a\nm "a" 0 1\n' > "$WORKDIR/ch_scope.rxt"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$WORKDIR/ch_scope.rxt" >/dev/null 2>&1; then
    pass "W23-S3 arm 6b: an indented line under a row naming a scope is accepted (arm 6a's control)"
else
    fail "W23-S3 arm 6b: a legal 'config' body was refused"
fi

# =====================================================================
# [DD-13b.W23.3a] W23-S7: `include`'s CLOSURE
#
# `docs/design/dd13_format/w23_impl.md` §1.10.2's own table reads "legs
# B and C" symmetrically for the report/splice/failure-attribution
# rules. **MEASURED FALSE for leg C, structurally, and RULED by the
# manager (docs/dev/lanes/w233a_report.md §2, ACCEPTED at the merge
# request that produced this section)**: `include` is head-scoped by
# design (`format_design.md` §2.5), so any file carrying one is
# head-bearing, and `verify_rxt.py`'s seam-ruling refusal — UNCHANGED —
# already raises on it before any body line is reached, exactly as it
# does for `dup_head_description.rxtin` one production over (§2.25.5's
# own precedent, applied to a construct that CANNOT be moved to block
# scope the way `ext` at least theoretically could be). So this section
# is a LEG A / LEG B differential for the splice half — never
# `check_refusal_all3` — and `include_dup_path.rxtin`'s same-file
# collision is `check_refusal`, single-leg, leg A only, for the
# identical reason `dup_head_description.rxtin` is.
#
# check_include_splice FIXTURE DIRECT TOTAL LABEL:
#   FIXTURE   the .rxtin's own basename (copied to $FIXRUN/FIXTURE.rxt)
#   DIRECT    leg A's own include-row count on the ENTRY alone — its
#             DIRECT includes only; a nested fragment's own include line
#             is invisible to a single `--list-source` call on the
#             entry, exactly as it is invisible to any one node of
#             `closure_walk`'s own recursive walk one leg over
#   TOTAL     leg B's `fragments spliced` — the TRANSITIVE closure size
#   LABEL     the check's own name suffix
#
# Every fixture here is built so each physical file (entry and every
# fragment) carries EXACTLY ONE pattern block with EXACTLY ONE `m` case
# — which is what turns "the entry's count EXCEEDS its own file's block
# count by the fragments' own" (§1.10.4) into one clean arithmetic
# check: `cases passed == 1 + TOTAL`. K35's own lesson is why this is
# asserted as three separate numbers rather than one pass/fail: a splice
# check satisfied by a closure of zero would prove nothing, and each of
# the three (leg A's direct count, leg B's total count, the case-count
# arithmetic) can be wrong independently of the other two.
check_include_splice() {
    local fixture=$1 direct=$2 total=$3 label=$4
    local entry_file="$FIXRUN/$fixture.rxt" ls_out a_includes b_out
    local b_entries b_frags b_pass

    if ! ls_out="$("$TIMEOUT_BIN" 30 "$PCREC" --list-source "$entry_file" 2>&1)"; then
        fail "W23-S7/$label: leg A refused the entry, which must ACCEPT:
  $ls_out"
        return
    fi
    a_includes=$(printf '%s\n' "$ls_out" \
        | LC_ALL=C awk -F'\t' '!/^#/ && $1 == "include"' | wc -l | tr -d ' ')
    if [ "$a_includes" = "$direct" ]; then
        pass "W23-S7/$label: leg A's own include row count on the entry is $direct"
    else
        fail "W23-S7/$label: leg A reported $a_includes include row(s) on the entry, wanted $direct"
    fi

    b_out="$("$TIMEOUT_BIN" 60 bash "$RUNSH" "$entry_file" 2>&1)"
    b_entries=$(printf '%s\n' "$b_out" | awk -F': ' '/^entry files:/ {print $2}')
    b_frags=$(printf '%s\n' "$b_out" | awk -F': ' '/^fragments spliced:/ {print $2}')
    b_pass=$(printf '%s\n' "$b_out" | awk -F': ' '/^cases passed:/ {print $2}')
    if [ "${b_entries:-X}" = "1" ] && [ "${b_frags:-X}" = "$total" ]; then
        pass "W23-S7/$label: leg B reports entry files: 1, fragments spliced: $total"
    else
        fail "W23-S7/$label: leg B reported entry files: ${b_entries:-?}, fragments spliced: ${b_frags:-?} (wanted 1 / $total):
  $b_out"
    fi
    local want_pass=$((1 + total))
    if [ "${b_pass:-X}" = "$want_pass" ]; then
        pass "W23-S7/$label: cases passed == 1 (the entry's own) + $total (fragments') == $want_pass"
    else
        fail "W23-S7/$label: cases passed was ${b_pass:-?}, wanted $want_pass (1 entry case + $total fragment cases)"
    fi
}
check_include_splice include_basic  1 1 basic
check_include_splice include_nested 1 2 nested

# `include_dup_path.rxtin`'s same-file collision — LEG A ONLY, exactly
# `dup_head_description.rxtin`'s own wording pattern (single-leg
# `check_refusal`, never `check_refusal_all3`), and the comment states
# why rather than leaving the asymmetry looking like an oversight: the
# head has one parser, and this is a head-level refusal.
check_refusal include_dup_path.rxt include-duplicate \
    'include_basic_frag.rxtfrag' 'include "./include_basic_frag.rxtfrag"'

# THE FOURTH FAILURE CLASS, THROUGH LEG B, ASSERTED EXPLICITLY (manager
# ruling on this section's own brief): `include_dup_path.rxtin` is a
# SAME-FILE collision, entirely inside leg A's own single-file parse, so
# running it through leg B never reaches `rxt_expand_closure` at
# all — leg A already refused the entry's `--list-source` call before
# leg B's closure walk would begin. The `[resolution]` tag's OWN
# detector is therefore a DIFFERENT shape: two DIFFERENT includers
# (not one file's own two lines) that both reach the SAME fragment
# transitively, which only a multi-file CLOSURE WALK — leg B's, never
# leg A's — can see. Built here as scratch files rather than as a
# fourth named `.rxtin` fixture (`w23_impl.md` §1.10.4 names three,
# `w233a_report.md` §3 item 1's own count), on `run_rxtsource_tests.sh`'s
# own "synthetic stream in the repair's own commit" precedent (W23.4
# item 3b): a shared fragment reached both directly by the entry and
# indirectly through a second included file.
mkdir -p "$WORKDIR/xclose"
cat > "$WORKDIR/xclose/shared.rxtfrag" <<'EOF'
pattern shared
m "shared" 0 6
EOF
cat > "$WORKDIR/xclose/via.rxtfrag" <<'EOF'
include "shared.rxtfrag"
pattern via
m "via" 0 3
EOF
cat > "$WORKDIR/xclose/entry.rxt" <<'EOF'
include "shared.rxtfrag"
include "via.rxtfrag"

pattern top
m "top" 0 3
EOF
xc_out="$("$TIMEOUT_BIN" 60 bash "$RUNSH" "$WORKDIR/xclose/entry.rxt" 2>&1)"
case $xc_out in
    *'[resolution]'*)
        pass "W23-S7/resolution: a fragment reached by TWO different includers (directly, and through a sibling) is a [resolution]-class failure"
        ;;
    *)
        fail "W23-S7/resolution: expected a [resolution]-tagged failure when two different includers reach the same fragment; got:
  $xc_out"
        ;;
esac
case $xc_out in
    *'cases failed: 1'*) ;;
    *)
        fail "W23-S7/resolution: expected exactly 1 case failure (the entry's own body still runs — rule 1 in §1.10.2); got:
  $xc_out"
        ;;
esac

# THE CORPUS CONTROL (§1.10.3/§1.10.4), and it is the one that matters:
# a subtraction/splice bug that removed real corpus files or double-
# spliced would otherwise surface only as a quieter or louder suite. The
# shipped corpus has ZERO `include` lines at this pin, so `entry files`
# must equal the FULL census and `fragments spliced` must be exactly 0.
#
# THROUGH `--dump`, NOT A BARE RUN: this section's own header says why
# it is cheap ("three parses of the corpus and NO COMPILES") and a bare
# `bash "$RUNSH"` over the whole corpus would compile every pattern —
# `test-corpus`'s own workload, duplicated inside a section that exists
# specifically not to compete with it for the box. `--dump` still runs
# every file through the whole per-file loop (subtraction, splice,
# parsing) at zero compile cost, which is everything this control needs.
# `--dump` takes the ARGUMENT branch (no `known_fail` exclusion, unlike
# the no-arg default), so its population is `CENSUS_FILES`, not
# `RUNSH_FILES`.
corpus_out="$("$TIMEOUT_BIN" 120 bash "$RUNSH" --dump "$ROOT_DIR/tests" 2>&1 >/dev/null)"
corpus_entries=$(printf '%s\n' "$corpus_out" | awk -F': ' '/^entry files:/ {print $2}')
corpus_frags=$(printf '%s\n' "$corpus_out" | awk -F': ' '/^fragments spliced:/ {print $2}')
if [ "${corpus_entries:-X}" = "$CENSUS_FILES" ] && [ "${corpus_frags:-X}" = "0" ]; then
    pass "W23-S7 corpus control: entry files: $CENSUS_FILES (== CENSUS_FILES), fragments spliced: 0 — the shipped corpus has no include lines"
else
    fail "W23-S7 corpus control: entry files: ${corpus_entries:-?} (wanted $CENSUS_FILES), fragments spliced: ${corpus_frags:-?} (wanted 0) — a subtraction or splice defect moved the population:
  $(printf '%s\n' "$corpus_out" | tail -20)"
fi

# =====================================================================
# [DD-13b.W23.5] W23-S5 — THE `all-readers` POPULATION CHECK ITSELF
# (w23_impl.md §3.3). Walks `--list-schema`'s OWN OUTPUT (never
# `rxt_schema.def` directly — that table's own header states why: a
# check reading the table would share a source with the parser it is
# checking, docs/dev/learnings.md §3) for every BLOCK-scope row whose
# `validated_by` reads `all-readers`, and fails naming any row with NO
# line in `$RECEIPTS` — the log `check_refusal_all3_kind`/
# `check_accept_all3_kind` write ONLY when all three legs actually ran
# and answered, never a declared fixture name.
schema_out="$WORKDIR/schema.tsv"
"$TIMEOUT_BIN" 30 "$PCREC" --list-schema > "$schema_out" 2>"$WORKDIR/schema.err"
allreaders_kinds=$(awk -F'\t' '
    /^#section schema/ { insect = "schema"; next }
    /^#section / { insect = ""; next }
    /^#/ { next }
    insect == "schema" && $9 == "all-readers" { print $2 }' "$schema_out")
allreaders_n=$(printf '%s\n' "$allreaders_kinds" | grep -c .)
if [ "$allreaders_n" = "0" ]; then
    fail "W23-S5: --list-schema reports ZERO all-readers rows — this arm
  has an empty population, which is itself a failure to investigate
  (the five block-scope rows name/description/flags/encoding/engine
  are expected here)."
else
    missing=""
    while IFS= read -r k; do
        [ -z "$k" ] && continue
        if ! grep -qx -- "$k" "$RECEIPTS" 2>/dev/null; then
            missing="$missing $k"
        fi
    done <<< "$allreaders_kinds"
    if [ -z "$missing" ]; then
        pass "W23-S5: all $allreaders_n all-readers row(s) (${allreaders_kinds//$'\n'/, }) have at least one receipt in \$RECEIPTS"
    else
        fail "W23-S5: $allreaders_n all-readers row(s) declared, but these have NO receipt at all:$missing
  Either the fixture that used to exercise them was removed, or the
  three-leg call site that ran them stopped reaching its own code (a
  call commented out, an early return) — a declared fixture NAME would
  not have caught either."
    fi
fi

# =====================================================================
# [DD-13b.W23.5] `mc_illformed_utf8.rxtin` — w23_impl.md §3.2's OWED
# W23.3 fixture (SW7's ill-formed-UTF-8 advance rule), never landed
# there. Both legs' own SCORING is the check: `run.sh` runs the case
# through the real artifact's C find-all loop (`<prefix>_next_pos`, the
# encoding residual), `verify_rxt.py` runs its own python transcription
# of the SAME protocol (`match_api.md` §3.1.1), and both must agree with
# the fixture's own expected count — the differential IS the agreement,
# since neither leg is an external PCRE2 oracle for this rule.
MIU="$FIXRUN/mc_illformed_utf8.rxt"
miu_b_out="$("$TIMEOUT_BIN" 60 bash "$RUNSH" "$MIU" 2>&1)"; miu_b_rc=$?
miu_c_out="$("$TIMEOUT_BIN" 60 python3 "$VERIFY" "$MIU" 2>&1)"; miu_c_rc=$?
if [ "$miu_b_rc" = "0" ] && [ "$miu_c_rc" = "0" ] && \
   printf '%s\n' "$miu_b_out" | grep -q '^cases passed: 1$' && \
   printf '%s\n' "$miu_c_out" | grep -q '^PASS=1 FAIL=0$'; then
    pass "mc/ill-formed-utf8: run.sh's C find-all loop and verify_rxt.py's python transcription both count 2 matches on three bare continuation bytes (SW7's skip rule)"
else
    fail "mc/ill-formed-utf8: the two legs disagree with the fixture's expected count, or one of them errored.
  run.sh (rc=$miu_b_rc): $(printf '%s\n' "$miu_b_out" | tail -10)
  verify_rxt.py (rc=$miu_c_rc): $(printf '%s\n' "$miu_c_out" | tail -10)"
fi

# =====================================================================
# [DD-13b.W23.5] R-A — THE `pattern-esc` DUMP-VALUE SEAM, GIVEN A
# POPULATION (w233_report.md §3.2 / w234_report.md §3, manager ruling).
#
# Leg A's `pattern` column DECODES a `pattern-esc` block's bytes
# (`pcrec_rxt_decode_escaped`, src/parse/rxt_source.c); legs B and C
# report the text AS WRITTEN, quotes included, because decoding it
# would cost a second copy of the escape table in bash and a third in
# python (tests/harness/CLAUDE.md's own stated reason). So a
# `pattern-esc` row's VALUE comparison is A-vs-(B==C), EXCLUDED BY
# DESIGN rather than a three-way agreement — the THIRD instance of the
# dup_head_description/include seam shape (w233a_report.md §2), and
# this is the check that asserts the excluded half honestly (B==C)
# instead of silently comparing nothing.
#
# `pattern_esc_value_seam.rxtin` gives the seam its first non-zero
# population: an ORDINARY `pattern` block first, then a `pattern-esc
# "a\nb"` block whose value contains a REAL escape. This fixture's own
# claim is about the VALUE column and does not need `pattern-esc` to be
# the file's first block, so the ordering is kept as originally written
# even though it is no longer load-bearing — see the finding below.
#
# [RULEFIX, 2026-09-15 — FIXED, was recorded rather than fixed at W23.5]
# Leg C used to REFUSE a file whose FIRST block opened with
# `pattern-esc`, even though legs A and B both accepted it (MEASURED at
# the time: `unknown-token-in-scope` at `verify_rxt.py:667`, whose
# `first != 'pattern'` test had no `pattern-esc` exemption — the SAME
# shape S242's own finding named one production over, since a fixture
# cannot exercise a claim a leg structurally refuses before reaching
# it). Frank's ruling: fix legs C's OPENER recognition (`first not in
# ('pattern', 'pattern-esc')`), leaving the VALUE seam this check itself
# asserts (leg C reports a `pattern-esc` row's text AS WRITTEN, never
# decoded) untouched. `opener_pattern_esc_pair.rxtin` (S242's own
# fixture, which opens with `pattern-esc`) is now reachable by all three
# legs — re-verified three-legged where S242's own check lives, above.
PEVS="$FIXRUN/pattern_esc_value_seam.rxt"
pevs_a_out="$("$TIMEOUT_BIN" 30 "$PCREC" --list-source "$PEVS" 2>"$WORKDIR/pevs.aerr")"; pevs_a_rc=$?
pevs_b_out="$("$TIMEOUT_BIN" 60 bash "$RUNSH" --dump "$PEVS" 2>"$WORKDIR/pevs.berr")"; pevs_b_rc=$?
pevs_c_out="$("$TIMEOUT_BIN" 60 python3 "$VERIFY" --dump "$PEVS" 2>"$WORKDIR/pevs.cerr")"; pevs_c_rc=$?
if [ "$pevs_a_rc" = "0" ] && [ "$pevs_b_rc" = "0" ] && [ "$pevs_c_rc" = "0" ]; then
    # the SECOND block/row in each dump is the `pattern-esc` one.
    pevs_a_pat=$(printf '%s\n' "$pevs_a_out" | awk -F'\t' '$1 == "pattern" { n++; if (n == 2) { print $5; exit } }')
    pevs_b_pat=$(printf '%s\n' "$pevs_b_out" | awk -F'\t' '$1 == "block" { n++; if (n == 2) { print $6; exit } }')
    pevs_c_pat=$(printf '%s\n' "$pevs_c_out" | awk -F'\t' '$1 == "block" { n++; if (n == 2) { print $6; exit } }')
    pevs_want_a='a\nb'
    pevs_want_bc='"a\\nb"'
    if [ "$pevs_a_pat" = "$pevs_want_a" ] && \
       [ "$pevs_b_pat" = "$pevs_want_bc" ] && [ "$pevs_c_pat" = "$pevs_want_bc" ]; then
        pass "R-A: pattern-esc dump-value seam — leg A decodes ('$pevs_want_a'), legs B and C agree AS-WRITTEN ('$pevs_want_bc'); the A-vs-(B==C) exclusion holds with a real population"
    else
        fail "R-A: pattern-esc dump-value seam broke.
  leg A: $pevs_a_pat (want $pevs_want_a, decoded)
  leg B: $pevs_b_pat (want $pevs_want_bc, as-written)
  leg C: $pevs_c_pat (want $pevs_want_bc, as-written)
  Either a leg started/stopped decoding, or B and C stopped agreeing with
  each other — the one comparison this seam DOES require."
    fi
else
    fail "R-A: pattern-esc dump-value seam fixture failed to dump
  (leg A rc=$pevs_a_rc, leg B rc=$pevs_b_rc, leg C rc=$pevs_c_rc):
  A: $(cat "$WORKDIR/pevs.aerr")
  B: $(cat "$WORKDIR/pevs.berr")
  C: $(cat "$WORKDIR/pevs.cerr")"
fi

# =====================================================================
# [DD-13b.W23.5] THE WITHDRAWALS' ABSENCE, AS A COMMITTED CHECK
# (w23_impl.md §4.3, build order item 3: "the §4.3 absence grep as a
# committed check rather than a manual step"). Two of the three arms
# are automatable; arm (c) is deliberately NOT a grep and §4.3 says why
# (`docs/spec/rxt_format.md:130`'s "configs are three artifacts..." is
# legitimate English no pattern can separate from the withdrawn
# `configs describe`/`configs build`) — it stays a standing review step.
#
# RULING R-B (escalated by w234_report.md §2): the DATA ARM's naive
# `grep -lE '^[[:space:]]*(configs|testee|option|provides|capable)…'`
# cannot tell a withdrawn `config`-body DIRECTIVE from an `ext` BODY
# LINE spelled the same word — `ext bench` / `testee pcre2/10.46` is
# format_design.md §2.27's OWN worked example, not the withdrawn
# `config … testee` roster returning (§2.27.3's non-interpretation
# clause: nothing in pcrec may take a value that changes when an aux
# body changes, and a CHECK is exactly such a thing). So the data arm
# is NARROWED to exclude lines inside an `ext` (children: tree) AUX
# SUBTREE — STRUCTURALLY, by an INDENT STACK tracking attachment under
# an `ext` opener (S1/S2's own rule: a blank line or a column-1 comment
# closes every attachment; a dedent pops back to the matching level),
# never by a list of consumer namespace names. `freq` is deliberately
# NOT an opener here: its body is the schema's DATA scope
# (`rxt_schema.def`, declared rows — `question`/`reader`/`analyzer`/
# `row`/`provenance`), not TREE, so it is not an aux subtree and a
# withdrawn word inside one is still the withdrawn word.
withdrawn_data_arm() {
    # $1: a file to scan. Prints one "<file>:<line>: <content>" line per
    # hit, then a trailing "HITS n" line.
    awk '
        FNR == 1 { depth = 0 }
        {
            line = $0
            if (line == "") { depth = 0; next }               # S0 BLANK
            if (substr(line, 1, 1) == "#") { depth = 0; next } # S0 COMMENT (col 1)
            n = match(line, /[^ ]/)
            if (n == 0) next                                  # S0 WHITESPACE-ONLY: inert
            indent = n - 1
            content = substr(line, n)
            while (depth > 0 && indent <= stack[depth]) depth--
            if (depth == 0 &&
                content ~ /^(configs|testee|option|provides|capable)([ \t]|$)/) {
                print FILENAME ":" FNR ": " content
                hits++
            }
            if (content ~ /^ext([ \t]|$)/) { depth++; stack[depth] = indent }
        }
        END { print "HITS " hits+0 }' "$1"
}

# ARM (a) — THE DATA ARM, over the corpus AND the fixtures (the same
# population §4.3's own MEASURED table used: `git ls-files '*.rxt'
# '*.rxtin'`).
DATA_HITS=0
DATA_DETAIL=""
while IFS= read -r relf; do
    out="$(withdrawn_data_arm "$ROOT_DIR/$relf")"
    h="$(printf '%s\n' "$out" | tail -1 | awk '{print $2}')"
    DATA_HITS=$((DATA_HITS + h))
    if [ "$h" != "0" ]; then
        DATA_DETAIL="$DATA_DETAIL
$(printf '%s\n' "$out" | sed '$d')"
    fi
done < <(git -C "$ROOT_DIR" ls-files '*.rxt' '*.rxtin')
if [ "$DATA_HITS" = "0" ]; then
    pass "withdrawal-absence, data arm: 0 withdrawn-token hits over the corpus and fixtures, aux subtrees excluded structurally"
else
    fail "withdrawal-absence, data arm: $DATA_HITS hit(s) —$DATA_DETAIL"
fi

# THE SELF-CHECK: the narrowing must still fire on a GENUINE top-level
# plant, and must NOT fire on the SAME word nested under a real `ext`
# opener — verified against two scratch files (never the real corpus,
# which the arm above has already proven clean), on the
# "synthetic stream in the repair's own commit" precedent (W23.4 item
# 3b). This is what makes "structural, not a keyword list" a checked
# property rather than an assertion about the awk script's own text.
cat > "$WORKDIR/withdrawn_top_level.rxt" <<'EOF'
pattern a
testee pcre2/10.46
m "a" 0 1
EOF
cat > "$WORKDIR/withdrawn_nested.rxt" <<'EOF'
pattern a
ext bench
  testee pcre2/10.46
m "a" 0 1
EOF
top_hits="$(withdrawn_data_arm "$WORKDIR/withdrawn_top_level.rxt" | tail -1 | awk '{print $2}')"
nested_hits="$(withdrawn_data_arm "$WORKDIR/withdrawn_nested.rxt" | tail -1 | awk '{print $2}')"
if [ "$top_hits" = "1" ] && [ "$nested_hits" = "0" ]; then
    pass "withdrawal-absence, self-check: a top-level 'testee' line is caught (1 hit); the SAME word nested under a real 'ext' opener is not (0 hits) — the narrowing is structural attachment, not a keyword list"
else
    fail "withdrawal-absence, self-check: top-level hits=$top_hits (want 1), nested hits=$nested_hits (want 0) — the aux-subtree narrowing is not discriminating correctly"
fi

# ARM (b) — THE PARSER ARM: none of the FOUR readers' keyword tables or
# dispatch arms names one of the five withdrawn/reserved tokens as an
# ACTIVE production, spelled as each reader spells a live keyword (a
# quoted `PCREC_RXT_SCHEMA` kind — rxt_source.c's own config_vocab/
# head_vocab/block_vocab retired at W23.1, so the schema table is the
# ONE dispatch table now; a quoted python string in verify_rxt.py; a
# `^`-anchored bash arm in run.sh; a quoted CLI flag string in
# cli/main.c). MEASURED before the withdrawal (w23_impl.md §4.3): 1 —
# rxt_source.c:149's now-retired config_vocab rows. This arm's landing
# value is that it reads 1 there and 0 here; a check whose baseline was
# already 0 proves nothing about the change that was made.
PARSER_HITS=0
PARSER_DETAIL=""
for tok in configs testee option provides capable; do
    h=""
    h="$h$(grep -n "\"$tok\"" "$ROOT_DIR/src/parse/rxt_schema.def" 2>/dev/null | sed "s#^#src/parse/rxt_schema.def:#")"
    h="$h$(grep -n "\"$tok\"" "$ROOT_DIR/cli/main.c" 2>/dev/null | sed "s#^#cli/main.c:#")"
    h="$h$(grep -n "'$tok'" "$ROOT_DIR/tests/harness/verify_rxt.py" 2>/dev/null | sed "s#^#tests/harness/verify_rxt.py:#")"
    h="$h$(grep -nE "\\^$tok([^A-Za-z0-9_]|\$)" "$ROOT_DIR/tests/harness/run.sh" 2>/dev/null | sed "s#^#tests/harness/run.sh:#")"
    if [ -n "$h" ]; then
        n=$(printf '%s\n' "$h" | grep -c .)
        PARSER_HITS=$((PARSER_HITS + n))
        PARSER_DETAIL="$PARSER_DETAIL
$h"
    fi
done
if [ "$PARSER_HITS" = "0" ]; then
    pass "withdrawal-absence, parser arm: 0 of the four readers' keyword tables name a withdrawn/reserved token as an active production"
else
    fail "withdrawal-absence, parser arm: $PARSER_HITS hit(s) —$PARSER_DETAIL"
fi
# ARM (c) is a READ, not a grep, and stays one — §4.3's own point.

# ---------------------------------------------------------------------
# =====================================================================
echo
echo "== Summary =="
echo "checks passed: $checks_passed"
echo "checks recorded: $checks_recorded"
echo "checks failed: $checks_failed"
[ "$checks_failed" -eq 0 ] || exit 1
echo "PASS: rxtsource: INV-COMPAT holds over $CENSUS_FILES files / $CENSUS_BLOCKS blocks / $CENSUS_LINES expectation lines"
exit 0
