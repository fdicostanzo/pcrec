#!/bin/sh
# probe_registry_cost.sh — MEASURED, in-pcrec. What §7.4's four new registry
# rows ACTUALLY cost.
#
# [M6.4.1] REVISION (R31 C1, C8). The first revision said D65's built-status
# derivation for a non-doorway row "is simply a compile of the syntax string".
# C1 refuted that: the derivation is `doorway_route` + `doorway_call`, and
# `doorway_route` recognises FOUR prefixes only. A row whose syntax is `a*+`
# routes nowhere and derives to PCRECT_BUILT_DEFECT. This probe enumerates
# every site a fifth `RegKind` has to reach, with the line numbers, and shows
# the two registry_check pins that move — so §7.4's cost is a measurement
# rather than a list somebody wrote from memory.
#
# It also re-measures §7.3's companion fact (a new RegKind raises no -Wswitch
# alarm) INDIRECTLY, by showing the two `default:` arms that swallow it.
set -e
PCREC=${1:-build/pcrec}
REPO=$(git rev-parse --show-toplevel)
cd "$REPO"

echo "== (a) the derivation cannot reach a non-doorway row =="
echo "  doorway_route (src/parse/syntax_dump.c:334) recognises exactly:"
sed -n '334,380p' src/parse/syntax_dump.c | grep -n '\.kind = RK_' \
    | sed 's/^/     /'
echo "  and built_status_probe (syntax_dump.c:443) is that route plus the call."
echo
echo "  the shipped compiler, asked about the two spellings:"
printf '    --explain %-8s : %s\n' "'(?>a)'" "$("$PCREC" --explain '(?>a)' 2>&1 | sed -n '2p' | sed 's/^ *//')"
printf '    --explain %-8s : %s\n' "'a*+'"   "$("$PCREC" --explain 'a*+'   2>&1 | head -1)"
echo "  -> a row spelled 'a*+' derives to BUILT_DEFECT, not to built/unbuilt."
echo
echo "== (b) every OTHER site a fifth RegKind must reach =="
echo "  1. pcrec_registry's switch — a fifth kind falls to \`default: *n = 0\`:"
grep -n 'default: *\*n = 0' src/parse/registry.c | sed 's/^/     /'
echo "  2. the dump's hardcoded kind list (ONE array, TWO use sites):"
grep -n 'all_kinds' src/parse/syntax_dump.c | sed 's/^/     /'
echo "     (C8 called these \"both all_kinds[] arrays\"; measured, it is one"
echo "      array at :145 iterated at :165 and :1080. The correction does not"
echo "      change the ruling — three places still have to be edited.)"
echo "  3. enabled.c's SEPARATE hardcoded list:"
grep -n 'static const RegKind kinds\[\]' src/parse/enabled.c | sed 's/^/     /'
echo
echo "== (c) the two registry_check pins that move =="
echo "  row total (registry_check.c:444), and what --list-syntax reports today:"
grep -n 'total != 100' tests/registry/registry_check.c | sed 's/^/     /'
printf '     --list-syntax rows today: %s   -> becomes 104 with four new rows\n' \
    "$("$PCREC" --list-syntax 2>/dev/null | grep -c '^[^#]')"
echo "  the engine-capability tripwire's qualifying count (registry_check.c:1473):"
grep -n 'qualifying != 48' tests/registry/registry_check.c | sed 's/^/     /'
echo "     -> the four new rows' \`engines\` value decides whether this becomes"
echo "        52 or stays 48. §7.4 must STATE the value; it is not derivable"
echo "        from the row count."
echo
echo "== (d) R3's source: the check must read the DUMP, not the table =="
echo "  registry_check.c:135 already catches a pcrec_registry omission:"
sed -n '135p' tests/registry/registry_check.c | sed 's/^/     /'
echo "  so §7.3's \"half-done invisibly\" is only true of the DUMP side"
echo "  (all_kinds[]), which no check reaches. A per-kind assertion that"
echo "  ITERATES RK_COUNT over registry.c shares a source with what it checks;"
echo "  it must parse \`--list-syntax\` OUTPUT instead."
