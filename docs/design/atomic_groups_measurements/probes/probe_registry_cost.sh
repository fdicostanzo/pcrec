#!/bin/sh
# probe_registry_cost.sh — MEASURED, in-pcrec. What §7.4's four new registry
# rows ACTUALLY cost.
#
# [M6.4.1] REVISION 2 (r31chk re-check N1). **THIS PROBE'S FIRST VERSION WAS
# THE DEFECT IT WAS WRITTEN TO PREVENT.** It carried a table headed "MEASURED
# rather than recalled" and its search population was four files —
# registry.c, syntax_dump.c, enabled.c, registry_check.c — the four the author
# already knew about. A grep over the answer you already have is a transcript,
# not a measurement. The re-check found a seventh site in a fifth file
# (tests/spec_mod0/check06_cursor.sh) that the old probe could not have seen.
#
# So this version SWEEPS. It searches ALL of src/, cli/ and tests/ for four
# kinds of consumer and prints what it finds, without a curated list:
#
#   (1) EXACT equalities on the dump's row count      -> these go RED
#   (2) FLOORS on the row count                        -> these pass
#   (3) hardcoded RegKind lists                        -> a fifth kind is invisible
#   (4) doorway-ROUTING set assertions                 -> a non-doorway row lands
#                                                          in the unrouted bucket
#
# **AND THE SWEEP FOUND MORE THAN THE FINDING DID**, which is recorded rather
# than smoothed over: the re-check named a seventh site; the sweep finds NINE
# across SIX files, three of them EXACT equalities. The lesson generalises past
# this probe — an enumeration is only as wide as its search population, at
# every level including the review's.
set -e
# r31eng final: RESOLVED FROM THIS SCRIPT'S OWN LOCATION, not from the
# caller's working directory. A bare relative `build/pcrec` makes the probe's
# answer depend on where it was invoked from — it silently measures a DIFFERENT
# compiler (or none). Every probe in this directory had the same shape; all
# were fixed together. An explicit $1 still overrides, and the archive header
# names the run directory so a reader can see which tree produced a number.
_PROBE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
_REPO_ROOT=$(CDPATH= cd -- "$_PROBE_DIR/../../../.." && pwd)
PCREC=${1:-$_REPO_ROOT/build/pcrec}
REPO=$(git rev-parse --show-toplevel)
cd "$REPO"

TREE="src cli tests"
ROWS_TODAY=$("$PCREC" --list-syntax 2>/dev/null | grep -c '^[^#]')
NEW=4
ROWS_AFTER=$((ROWS_TODAY + NEW))

echo "== the number that moves =="
echo "  --list-syntax rows today : $ROWS_TODAY"
echo "  after four new rows      : $ROWS_AFTER"
echo

echo "== (1) EXACT equalities on a dump-derived count — THESE GO RED =="
grep -rn -- "-eq $ROWS_TODAY\b\|!= $ROWS_TODAY\b\|== $ROWS_TODAY\b\|-eq 99\b\|!= 99\b" \
    $TREE --include=*.c --include=*.sh --include=*.py 2>/dev/null \
    | grep -v "^tests/bench/" | sed 's/^/  /' || echo "  (none)"
echo
echo "  Each of these is a deliberate anchor, and each says so in its own"
echo "  comment (compliance_section.py: \"Bumping it is deliberate and belongs"
echo "  in the same commit as the row\"). The non-base count is 99 rather than"
echo "  $ROWS_TODAY because \`(?:\` is the one RS_BASE row; four RS_MODULE rows"
echo "  make it 103."
echo

echo "== (2) FLOORS on the row count — these PASS at $ROWS_AFTER =="
grep -rn -- "-lt $ROWS_TODAY\b\|< $ROWS_TODAY\b" $TREE --include=*.c --include=*.sh --include=*.py 2>/dev/null \
    | grep -iv "bench\|trie\|nbr\|subj\|nn\b" | sed 's/^/  /' || echo "  (none)"
echo

echo "== (3) hardcoded RegKind lists — a fifth kind is INVISIBLE to the compiler =="
grep -rn "RegKind [a-z_]*\[\] *=\|case RK_ESC" $TREE --include=*.c 2>/dev/null | sed 's/^/  /'
echo "  and the switch whose default swallows a fifth kind:"
grep -rn 'default: *\*n = 0' src/parse/registry.c | sed 's/^/  /'
echo

echo "== (4) doorway-ROUTING set assertions — a non-doorway row lands unrouted =="
grep -rn "EXPECT_BASE_ANSWERED\|reaching no doorway" $TREE --include=*.sh 2>/dev/null | sed 's/^/  /'
echo "  This is a SET equality, not a count, so no floor absorbs it: the four"
echo "  new rows route nowhere and join the unrouted bucket."
echo "  expected set today : \"(?:...)\""
echo "  expected set after : \"(?:...) a*+ a++ a?+ a{1,2}+\""
echo

echo "== (5) the built-status derivation cannot reach a non-doorway row =="
echo "  doorway_route (src/parse/syntax_dump.c:334) recognises exactly:"
sed -n '334,380p' src/parse/syntax_dump.c | grep -n '\.kind = RK_' | sed 's/^/     /'
printf '    --explain %-8s : %s\n' "'(?>a)'" "$("$PCREC" --explain '(?>a)' 2>&1 | sed -n '2p' | sed 's/^ *//')"
printf '    --explain %-8s : %s\n' "'a*+'"   "$("$PCREC" --explain 'a*+'   2>&1 | head -1)"
echo "  -> such a row derives to BUILT_DEFECT; built_status_probe"
echo "     (syntax_dump.c:443) needs a NON-DOORWAY compile arm."
echo

echo "== (6) the engine-capability tripwire's qualifying count =="
grep -rn "qualifying != 48" tests/registry/registry_check.c | sed 's/^/  /'
echo "  VM_ONLY on the four new rows makes this 52. Under M-1 the tripwire is"
echo "  REPLACED by SR-8 in the same substep, so expect to touch it once and"
echo "  then delete it."
echo

echo "== (7) the REGMANIFEST's prose pins, which no grep for a literal finds =="
grep -n "of 48 engine-restricted\|100 rows classified" tests/registry/run_registry_tests.sh \
    | cut -c1-90 | sed 's/^/  /'
echo "  These are the suite's own manifest lines. They carry the same two"
echo "  numbers as sites (1) and (6) in PROSE, so a change that updates the"
echo "  assertions and not these leaves the manifest describing a suite that"
echo "  no longer exists."
echo

echo "== (8) per-row field requirements the new rows must satisfy =="
grep -rn "no quantifiable value" tests/registry/registry_check.c | sed 's/^/  /'
echo "  -> \`quant\` must not be QF_NONE. The value is QF_NO: \`a*++\` is an"
echo "     ERROR in libpcre2 and in pcrec (§6.3), so a possessive suffix is"
echo "     not itself quantifiable."
echo
echo "== (9) per-row FIELD requirements — an EXTRACTION SHAPE, not a file =="
echo "  r31chk final T1. The two sites below are in files already in the sweep;"
echo "  what the sweep could not see was the SHAPE. It searched for row COUNTS,"
echo "  KIND LISTS and ROUTING SETS. A row also has to satisfy per-FIELD"
echo "  assertions, and those are a fourth shape:"
grep -n 'empty note\|empty syntax\|no quantifiable value' tests/registry/registry_check.c | sed 's/^/    /'
grep -n '\$syntax == "" || \$expect == ""' tests/reject/run_reject_tests.sh | sed 's/^/    /'
echo
echo "  So the new rows need \`note\` and \`expect\` NON-EMPTY as well as"
echo "  \`quant\`. \`expect\` is load-bearing: run_reject_tests.sh iterates every"
echo "  NON-BASE dump row and calls row_reject, which requires the row's own"
echo "  syntax to be a CLEAN EXIT-1 REJECTION whose stderr CONTAINS the"
echo "  \`expect\` text and which writes NO output file. Measured on the four:"
T2=$(mktemp -d)
for q in 'a*+' 'a++' 'a?+' 'a{1,2}+'; do
    rm -f "$T2/o.c" "$T2/o.h"
    # `|| true`: THIS DIRECTORY'S RECURRING DEFECT, hit for the THIRD time
    # while writing the very section about it. `set -e` plus an assignment
    # from a failing command substitution aborts the script, and every
    # invocation here is SUPPOSED to fail (exit 1 is the thing being
    # measured). probe_rk_alarm.sh's header records the same trap, and
    # assertions_measurements/CLAUDE.md records it for probe_kreset_identity.sh.
    # TWO traps in one line, and the second was this probe's own second
    # attempt at the first. (1) `set -e` plus an assignment from a failing
    # command substitution aborts the script, and every invocation here is
    # SUPPOSED to fail — exit 1 is the thing being measured. (2) The obvious
    # `|| true` fix SWALLOWS the exit code, so `r=$?` then reports 0 and the
    # probe cheerfully prints "exit=0" for a clean exit-1 rejection. Redirect
    # to a file and capture rc from the command itself.
    "$PCREC" -p rx -o "$T2/o.c" -- "$q" 2>"$T2/err" >/dev/null && r=0 || r=$?
    m=$(cat "$T2/err")
    w=no; { [ -f "$T2/o.c" ] || [ -f "$T2/o.h" ]; } && w=YES
    printf '    %-10s exit=%s wrote=%s  %s\n' "$q" "$r" "$w" "$m"
done
rm -rf "$T2"
echo "    -> exit 1, no file written, and \"requires module 'atomic-groups'\" is"
echo "       a substring of every one. \`expect\` = that text is SATISFIABLE."
echo

echo "== (10) enumeration by CALL — silent NON-COVERAGE =="
echo "  r31chk final T2, and it is §7.3's \"half-done invisibly\" shape in the"
echo "  very file R3 strengthens. check_table_to_parser does not iterate a kind"
echo "  list at all; it names each kind in an explicit CALL:"
grep -n 'pcrec_registry(RK_' tests/registry/registry_check.c | sed 's/^/    /'
echo "  A fifth kind is therefore SILENTLY UNCOVERED by the table->parser"
echo "  diagnostic-agreement check: nothing fails, the rows are simply never"
echo "  compared. R3's per-kind assertion has to cover this check too, or the"
echo "  check must iterate RK_COUNT."
echo

echo "== summary =="
echo "  SITES (9) AND (10) WERE FOUND BY DEFECT SHAPE, NOT BY FILE. Both live in"
echo "  files this sweep already read; what was missing was the QUESTION. The"
echo "  sweep now extracts five shapes -- row counts, kind lists, routing sets,"
echo "  per-row FIELD assertions, and enumeration by CALL -- and the next"
echo "  correction to it will most likely be a sixth shape rather than a"
echo "  seventh directory."
echo "  This sweep is over $(echo $TREE | tr ' ' ',') with no curated file list,"
echo "  and it now reports ELEVEN sites where the first version reported six."
echo "  A future reader who finds a twelfth should treat it as this probe's next"
echo "  correction, not as a surprise -- and should suspect a new SHAPE before a"
echo "  new directory."
