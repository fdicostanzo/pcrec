#!/usr/bin/env bash
# tests/rxtsource/run_rxtsource_tests.sh — [DD-13b.W1.1] INV-COMPAT.
#
# The question this section answers: does growing the `.rxt` format change
# what any EXISTING corpus file means? The corpus is 179 files, 3,265
# pattern blocks and 26,691 expectation lines, and none of them uses one
# byte of the new grammar — so the answer must be "no" in a way that a
# check can fail, not in a way a reader can believe.
#
# Design: docs/design/dd13_format/w1_impl.md §3 (and format_design.md
# §1.1, which states INV-COMPAT). Contract: docs/spec/rxt_format.md,
# docs/spec/table_contract.md.
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
#   census (all files)         179 files / 3,265 blocks / 26,691 lines
#   tests/known_fail/k34...      1 file  /     3 blocks /     11 lines
#                              ---------------------------------------
#   run.sh's own population    178 files / 3,262 blocks / 26,680 lines
#
# `run.sh`'s no-argument branch discovers with `-not -path "*/known_fail/*"`,
# so the known-fail ratchet's own file is never dispatched. C1 is a PARSE
# differential and can and should read every file, so it asserts 179 and
# invokes leg B through the ARGUMENT branch (which applies no exclusion).
# C2 asserts 178. Asserting 179 in both would make the second one wrong.
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
CENSUS_FILES=179
CENSUS_BLOCKS=3265
CENSUS_LINES=26691

# run.sh's own population: the census minus tests/known_fail/ (§3.0).
# Recorded here because C1 and C2 differ by exactly this file and a
# reader who assumes one population finds the 179/178 split inexplicable.
RUNSH_FILES=178
RUNSH_BLOCKS=3262
RUNSH_LINES=26680

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
nfiles=$(wc -l < "$FILES")

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
$(xargs -a "$FILES" awk '
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
if ! xargs -a "$FILES" "$TIMEOUT_BIN" 900 bash "$RUNSH" --dump \
        > "$DUMP_B" 2> "$WORKDIR/legB.err"; then
    fail "leg B: run.sh --dump failed
$(head -20 "$WORKDIR/legB.err")"
fi
tB1=$(date +%s.%N)

# the same pass again, this time with the counting wrapper in PCREC, so
# (a) above measures a run that exercised the real head-detection path
: > "$CALLLOG"
PCREC="$WRAPDIR/pcrec" xargs -a "$FILES" "$TIMEOUT_BIN" 900 bash "$RUNSH" --dump \
    > /dev/null 2>&1
ls_calls=$(grep -c -- '--list-source' "$CALLLOG" || true)

# (b) the independent census: a head-bearing file is one whose first
# non-blank, non-comment line's first token is not `pattern`. Derived
# here by awk over the raw bytes — no parser, no harness, no pcrec.
head_files=$(xargs -a "$FILES" awk '
    FNR == 1 { done = 0 }
    done { next }
    /^[ \t]*$/ { next }
    /^#/ { next }
    { done = 1; if ($1 != "pattern") { print FILENAME } }' | wc -l)

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
MANIFEST='kind	line	name	value	pattern	flags	features	features_only	encoding	engine	budget_steps	budget_frames	with	from	pcrec'
hdr="$("$PCREC" --list-source "$(head -1 "$FILES")" | grep '^#' | tail -1)"
hdr="${hdr#\#}"
if [ "$hdr" = "$MANIFEST" ]; then
    pass "C1 manifest: --list-source emits exactly the 15 pinned columns, in order"
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
badfields=$(awk -F'\t' -v want="$ncols" '
    $2 ~ /^#/ { next }
    NF != want + 1 { print FILENAME ": " $0; n++ }
    END { print "COUNT " n+0 }' "$DUMP_A_RAW" | tail -1 | awk '{print $2}')
if [ "$badfields" = "0" ]; then
    pass "C1 manifest: every --list-source data row has exactly $ncols fields (header truthfulness)"
else
    fail "C1 manifest: $badfields --list-source row(s) do not have $ncols fields.
  A field contained a TAB, which is what the rxt-escape on columns 4, 5
  and 15 exists to prevent — three corpus blocks carry a literal tab in
  their pattern text (tests/base/bounded_repeats.rxt twice,
  tests/modifiers/xxmode.rxt once) and in every one the tab is the thing
  under test."

fi

# leg A is one row per DECLARATION and per BLOCK. On this corpus there
# are no head declarations at all, so every row must be a `pattern` row —
# a THIRD view of C0a's zero, from pcrec's own output this time.
a_head_rows=$(awk -F'\t' '$2 !~ /^#/ && $2 != "pattern" { n++ } END { print n+0 }' "$DUMP_A_RAW")
a_blocks=$(awk -F'\t' '$2 == "pattern" { n++ } END { print n+0 }' "$DUMP_A_RAW")
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
# LEG C — verify_rxt.py --dump, the third parser: python, a different
# author, already in the tree before any of this was designed. It is what
# makes C1 a control for the BODY rather than a comparison of pcrec
# against itself. (The HEAD has exactly one parser by the seam ruling, and
# §3.1 says plainly that it therefore has no differential control; what
# covers it is the grammar's refusals, the manifest above, and the fact —
# asserted twice — that on this corpus the head is empty.)
DUMP_C="$WORKDIR/legC.tsv"
tC0=$(date +%s.%N)
if ! xargs -a "$FILES" "$TIMEOUT_BIN" 900 python3 "$VERIFY" --dump \
        > "$DUMP_C" 2> "$WORKDIR/legC.err"; then
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

# A: <file>\t<15 cols> -> block <file> <line> <name> <desc> <pat> <flags>
#    <features> <only> <encoding> <engine> <steps> <frames>
awk -F'\t' -v OFS='\t' '$2 == "pattern" {
    print "block", $1, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13 }' \
    "$DUMP_A_RAW" > "$PROJ_A"

awk -F'\t' -v OFS='\t' '$1 == "block" {
    NF = 13; print }' "$DUMP_B" > "$PROJ_B12"
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
$(xargs -a "$FILES" awk '
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
        pass "C1: leg $leg emitted $ca case rows (census $CENSUS_LINES minus $perr_lines perr lines)"
    else
        fail "C1: leg $leg emitted $ca case rows, expected $want_cases
  (= the census's $CENSUS_LINES expectation lines minus the $perr_lines
  \`perr\` lines, which both dumps carry as a BLOCK field rather than as a
  case row)"
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
C3_PASS=13181
C3_SKIP=13421
C3_SKIP_PCRE2ONLY=1357
C3_SKIP_GIVEUP=23
C3_SKIP_COMPOSED=0
C3_SKIP_NOPYTHON=1753
C3_SKIP_PERRACCEPT=14
C3_SKIP_OWNORACLE=10274
C3_TIMEOUT=1

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
"$TIMEOUT_BIN" 900 python3 "$VERIFY" --min-files "$CENSUS_FILES" \
    --file-timeout 10 $(cat "$FILES") > "$C3OUT" 2>&1
c3rc=$?
c3_files=$(awk -F= '/^FILES=/ { print $2 }' "$C3OUT")
c3_pass=$(awk '/^PASS=/ { sub(/^PASS=/, "", $1); print $1 }' "$C3OUT")
c3_skip=$(awk -F'[=( ]' '/^SKIP=/ { print $2 }' "$C3OUT")
c3_timeout=$(awk -F'[=( ]' '/^TIMEOUT=/ { print $2 }' "$C3OUT")
c3_reason() { sed -n 's/.*[ (]'"$1"'=\([0-9]*\).*/\1/p' "$C3OUT" | head -1; }

if [ "${c3_files:-}" = "$CENSUS_FILES" ]; then
    pass "C3: verify_rxt.py discovered $c3_files files (its own discovery, floored at the census)"
else
    fail "C3: verify_rxt.py discovered ${c3_files:-<no FILES line>} files, expected $CENSUS_FILES"
fi

if [ "$c3rc" -eq 0 ]; then
    pass "C3: verify_rxt.py verified $c3_pass expectation(s) with $c3_skip skip(s), 0 failures"

    # THE TOTALS, AGAINST THEIR PINS. The verified count alone is not
    # enough: a skip predicate that WIDENS moves work out of PASS and
    # into SKIP while both totals stay explicable, so each reason is
    # pinned separately. They also reconcile — pass + skip + the
    # timed-out file's own lines must be the whole census — which is
    # what makes this an accounting rather than nine loose numbers.
    c3_bad=""
    for chk in "PASS:$c3_pass:$C3_PASS" \
               "SKIP:$c3_skip:$C3_SKIP" \
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
        pass "C3: all nine population pins hold (verified, skips by reason, timeouts)"
    else
        fail "C3: population pin(s) MOVED:$c3_bad
  A skip reason that grows is coverage lost without a failing case to
  show for it. If the move is legitimate — a corpus file added, a block
  newly marked, a module landing that makes patterns python-expressible
  — re-pin the C3_* values in this file in a reviewed commit saying which
  and why."
    fi

    if [ "$((c3_pass + c3_skip + 89))" = "$CENSUS_LINES" ]; then
        pass "C3 reconciles: $c3_pass verified + $c3_skip skipped + 89 in the timed-out file = $CENSUS_LINES"
    else
        fail "C3 DOES NOT RECONCILE: $c3_pass + $c3_skip + 89 = $((c3_pass + c3_skip + 89)),
  census $CENSUS_LINES. Expectations are going somewhere neither counted
  nor reported, which is the one outcome a skip total exists to prevent."
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
# "run.sh's thirteen existing arms are not touched" was a diff argument,
# and a diff argument is not a check. The protected region is delimited
# by MARKER COMMENTS rather than by a line range, because W1.1 itself
# edits inside it (the `have_block` guard) — a line-range hash would be
# broken by the very change it exists to protect, and the only way to
# "fix" that is to re-pin, which discards the protection entirely.
BEGIN_MARK='# --- BEGIN PINNED 13-ARM REGION (w1 N3) ---'
END_MARK='# --- END PINNED 13-ARM REGION ---'
ARM_PIN='3e9453908bd3d8d8ea06da6a3008dbe4bef42848c57ea1ab06a1f0b4c6db5001'

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
  chain that R-COMPAT-1 protects — the chain 3,265 existing blocks and
  26,691 existing expectation lines are parsed by. It is not forbidden,
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
# FOUR MORE ARE ADDED HERE, and the addition is the point rather than
# drift: `description`, `encoding`, `only` and `pcrec` are words THIS
# STEP appends arms for, and a census that did not cover them would not
# cover what it exists to make safe.
CENSUS_WORDS_32="name target lib include config use variant oracle tag mc freq gap def with from testee option repl s sg serr unsupported analysis question reader exemplar bytes sha256 analyzer date row groups"
CENSUS_WORDS_W1="description encoding only pcrec"

collisions=""
ncensus=0
for w in $CENSUS_WORDS_32 $CENSUS_WORDS_W1; do
    ncensus=$((ncensus + 1))
    c=$(xargs -a "$FILES" grep -h -c "^$w\\b" 2>/dev/null \
        | awk '{ n += $1 } END { print n+0 }')
    [ "$c" != "0" ] && collisions="$collisions $w=$c"
done

n32=$(printf '%s\n' $CENSUS_WORDS_32 | wc -l)
if [ "$n32" != "32" ]; then
    fail "keyword census: the pinned 32-word list has $n32 words.
  It is format_design §1.1's list verbatim; if it changed, say so there too."
else
    pass "keyword census: the pinned list is 32 words (format_design §1.1) plus W1's 4"
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
for f in "$FIXDIR"/*.rxtin; do
    cp "$f" "$FIXRUN/$(basename "${f%.rxtin}").rxt"
done

# --- the accepting fixture -------------------------------------------
HB="$FIXRUN/head_basic.rxt"
if "$TIMEOUT_BIN" 30 "$PCREC" --list-source "$HB" > "$WORKDIR/hb.tsv" 2>"$WORKDIR/hb.err"; then
    pass "head: --list-source accepts a head-bearing file"

    # THE ROW ORDER IS THE CONTRACT. There is no head/body column: a head
    # row is exactly one preceding the first `pattern` row, which is a
    # property of the ORDER. So the order is what is asserted.
    got_kinds=$(awk -F'\t' '!/^#/ { printf "%s ", $1 }' "$WORKDIR/hb.tsv")
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
check_refusal wave2_keyword.rxt       wave       'include' 'NOT IN THIS BUILD'
check_refusal dup_config.rxt          duplicate  'duplicate' 'dev'
check_refusal block_scalar_in_body.rxt blockscalar 'one-line form'

# THE BLOCK-SCALAR REFUSAL IS THE ONE ALL THREE PARSERS MUST SHARE.
# It is where format_design's prose-value production and the body's
# no-indent rule contradict each other, so it is resolved the same way in
# every parser or the differential finds it later and calls it a bug.
bs="$FIXRUN/block_scalar_in_body.rxt"
if "$TIMEOUT_BIN" 300 bash "$RUNSH" --dump "$bs" > /dev/null 2>&1; then
    fail "head/blockscalar: run.sh ACCEPTED a '|' block scalar in a pattern block"
else
    pass "head/blockscalar: run.sh refuses it too"
fi
if "$TIMEOUT_BIN" 60 python3 "$VERIFY" --dump "$bs" > /dev/null 2>&1; then
    fail "head/blockscalar: verify_rxt.py ACCEPTED a '|' block scalar in a pattern block"
else
    pass "head/blockscalar: verify_rxt.py refuses it too — all three parsers agree"
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

# ---------------------------------------------------------------------
echo
echo "== Summary =="
echo "checks passed: $checks_passed"
echo "checks failed: $checks_failed"
[ "$checks_failed" -eq 0 ] || exit 1
echo "PASS: rxtsource: INV-COMPAT holds over $CENSUS_FILES files / $CENSUS_BLOCKS blocks / $CENSUS_LINES expectation lines"
exit 0
