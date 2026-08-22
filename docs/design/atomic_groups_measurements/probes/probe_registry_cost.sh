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
PCREC=${1:-build/pcrec}
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
echo "== summary =="
echo "  This sweep is over $(echo $TREE | tr ' ' ',') with no curated file list."
echo "  A future reader who widens it further and finds a tenth site should"
echo "  treat that as this probe's next correction, not as a surprise."
