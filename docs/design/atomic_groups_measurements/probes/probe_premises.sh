#!/bin/sh
# probe_premises.sh — MEASURED, in-pcrec. The design's §1 premise table and
# §6.3's error-shape table, as ONE re-runnable instrument.
#
# [M6.4.1]'s premises are supposed to be "re-verified on HEAD rather than
# inherited" (constraint (a)). A premise table whose evidence is a shell command
# quoted in prose is not re-verified, it is asserted -- R30 M8's finding about
# assertions_design.md §8.3, one document over. This is that table as a script.
#
# It also runs the SHAPES whose diagnostic CHANGES when the module lands
# (`a*++`), because a reject-suite author re-pinning after [M6.4.2] needs the
# before-picture and would otherwise have to reconstruct it.
#
# Usage: probe_premises.sh [path-to-pcrec]
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
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

run() {   # run PATTERN [flags...]
    pat=$1; shift
    out=$("$PCREC" -p rx "$@" -o "$TMP/o.c" "$pat" 2>&1) && echo "COMPILES" \
        || echo "$out" | head -1 | sed 's/^pcrec: //'
}

match() { # match PATTERN SUBJECT -- compile, link, run
    pat=$1; subj=$2
    if ! "$PCREC" -p rx --emit-main -o "$TMP/m.c" "$pat" >/dev/null 2>&1; then
        echo "REFUSED"; return
    fi
    if ! gcc -O0 -o "$TMP/m" "$TMP/m.c" >/dev/null 2>&1; then
        echo "GCC FAILED"; return
    fi
    "$TMP/m" "$subj" 2>&1 | head -1
}

echo "pcrec binary: $PCREC"
echo
echo "== P1/P2: the module's two refusal sites, and their offsets =="
printf '  %-12s %s\n' '(?>a)'    "$(run '(?>a)')"
printf '  %-12s %s\n' '(?>a|b)c' "$(run '(?>a|b)c')"
printf '  %-12s %s\n' 'a*+'      "$(run 'a*+')"
printf '  %-12s %s\n' 'a++'      "$(run 'a++')"
printf '  %-12s %s\n' 'a?+'      "$(run 'a?+')"
printf '  %-12s %s\n' 'a{1,2}+'  "$(run 'a{1,2}+')"
printf '  %-12s %s\n' 'a{2}+'    "$(run 'a{2}+')"
printf '  %-12s %s\n' 'a{,2}+b'  "$(run 'a{,2}+b')"
echo "  (P1 is a REGISTRY row -- src/parse/registry.c. P2 is HAND-WRITTEN at"
echo "   src/parse/parse.c:987-988, OUTSIDE the registry, which is §7's problem.)"
echo
echo "== P3: what the BASE tier does with {,n} TODAY -- must not change =="
printf '  %-10s compile: %-10s  subject aab -> %s\n' 'a{,2}b' "$(run 'a{,2}b')" "$(match 'a{,2}b' aab)"
printf '  %-10s compile: %-10s  subject aaa -> %s\n' 'a{,2}'  "$(run 'a{,2}')"  "$(match 'a{,2}' aaa)"
printf '  %-10s compile: %-10s  subject aaa -> %s\n' 'a{2,}'  "$(run 'a{2,}')"  "$(match 'a{2,}' aaa)"
echo "  ('match 0 3' for a{,2}b is the QUANTIFIER reading; a literal reading"
echo "   would not match \"aab\" at all. libpcre2 10.46 and python 3.14 agree.)"
echo
echo "== §6.3: the lazy-then-possessive and double-quantifier shapes =="
printf '  %-12s %s\n' 'a*?+'  "$(run 'a*?+')"
printf '  %-12s %s\n' 'a*?+b' "$(run 'a*?+b')"
printf '  %-12s %s\n' 'a*++'  "$(run 'a*++')"
printf '  %-12s %s\n' 'a**'   "$(run 'a**')"
echo "  (a*++ is the row that CHANGES when the module lands: today the FIRST"
echo "   '+' hits the possessive refusal; afterwards it is consumed as the"
echo "   possessive marker and the SECOND re-enters the quantifier loop, so the"
echo "   message becomes 'multiple quantifiers on the same item' -- still a"
echo "   refusal, still D26 tier-2 correct, and a tests/reject pin to re-take.)"
echo
echo "== §11.3 rule 4's premise: a DFA artifact carries no RX_ENGINE stamp =="
"$PCREC" -p rx --no-captures -o "$TMP/d.c" '(a|bc){1,4}d' >/dev/null 2>&1
printf '  --no-captures (a|bc){1,4}d : RX_ENGINE defines = %s\n' \
    "$(grep -c '^#define RX_ENGINE' "$TMP/d.c" || true)"
"$PCREC" -p rx -o "$TMP/v.c" '(a|bc){1,4}d' >/dev/null 2>&1
printf '  default       (a|bc){1,4}d : %s\n' \
    "$(grep '^#define RX_ENGINE\b\|^#define RX_ENGINE_WHY' "$TMP/v.c" | tr '\n' ' ')"
