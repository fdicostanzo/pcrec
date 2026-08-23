#!/bin/sh
# [M6.6.1] §1 -- THE PREMISES, RE-VERIFIED ON HEAD RATHER THAN INHERITED.
#
# Everything this probe reports comes from THIS worktree's build/pcrec, not
# from a document. The reason is the one backrefs_design.md §1 states: a
# design whose premises are quotations inherits every staleness in the quoted
# text. Two of this lane's premises turned out to be false as the charter
# states them, and only a run could say so.
#
# Axes:
#   A  every lookaround spelling's REFUSAL on HEAD (module attribution is
#      D26 tier 2 -- EXACT -- so the module NAME in each line is a fact
#      under test, while the wording around it is tier 3 and is not)
#   B  the registry rows that exist for lookaround spellings today, straight
#      from `--list-syntax`, with their engine mask and D65 built column
#   C  the `(*` alpha-spelling doorway, which axis A shows answering a
#      DIFFERENT module -- reported separately because it is a defect this
#      module owns rather than a premise it consumes
#   D  vm_cut's and the atomic lowering's actual interface in src/, quoted
#      by line so §3 cites code rather than a design document's account of it
#   E  what the assertions module actually built for alphabet context, since
#      §5's DFA-eligible subset lowers onto it
set -e
PCREC=build/pcrec
test -x "$PCREC" || { echo "no $PCREC -- build first"; exit 3; }

echo "pcrec binary: $PCREC ($(git rev-parse --short HEAD 2>/dev/null))"
echo

echo "=== AXIS A: every lookaround spelling's refusal on HEAD ==============="
echo "# columns: exit-status | pattern | diagnostic"
for pat in \
  '(?=a)b' '(?!a)b' '(?<=a)b' '(?<!a)b' \
  '(?*a)b' '(?<*a)b' \
  '(*pla:a)b' '(*positive_lookahead:a)b' \
  '(*nla:a)b' '(*negative_lookahead:a)b' \
  '(*plb:a)b' '(*positive_lookbehind:a)b' \
  '(*nlb:a)b' '(*negative_lookbehind:a)b' \
  '(*napla:a)b' '(*non_atomic_positive_lookahead:a)b' \
  '(*naplb:a)b' '(*non_atomic_positive_lookbehind:a)b' \
  '(?=)' '(?!)' '(?<=)' '(?<!)' \
  '(?=a)*' '(?=a)+' '(?=a){2}' '(?!a)?' \
  'a(?=b)' 'a(?<=b)' '(?=(a))b' '(?<=a|bc)x' '(?<=a*)x' \
  '(?=a)(?=b)' '(?=(?<=a)b)c' '(?<=(?=a)b)c'
do
  out=$(/usr/bin/gnutimeout 10 "$PCREC" -p rx -o /dev/null "$pat" 2>&1) && st=0 || st=$?
  printf 'exit=%s | %-42s | %s\n' "$st" "$pat" "$(printf '%s' "$out" | tr '\n' ' ')"
done
echo

echo "=== AXIS B: the registry rows for module 'lookaround' today =========="
echo "# from --list-syntax; columns per the dump's own header"
/usr/bin/gnutimeout 30 "$PCREC" --list-syntax 2>&1 \
  | awk -F'\t' '$4 == "lookaround" {
        printf "kind=%s sel=%s syntax=%-12s engines=%-4s status=%s roadmap=%s quant=%s built=%s\n",
               $1, $2, $3, $7, $8, $13, $14, $16 }'
echo "# row count for module 'lookaround':"
/usr/bin/gnutimeout 30 "$PCREC" --list-syntax 2>&1 | awk -F'\t' '$4=="lookaround"' | wc -l
echo "# any lookaround row reading 'built'? (expect NONE before [M6.6.2])"
/usr/bin/gnutimeout 30 "$PCREC" --list-syntax 2>&1 \
  | awk -F'\t' '$4=="lookaround" && $16=="built" {print}' | wc -l
echo

echo "=== AXIS C: the (* alpha-spelling doorway ============================"
echo "# The twelve lookaround verb names below are in the VERB NAME table"
echo "# (src/parse/mod_verbs.c) but the (* DOORWAY row is a single FIXED row"
echo "# naming module 'verbs' (src/parse/registry.c verb_rows). D26 makes the"
echo "# MODULE a tier-2 (exact) fact, so an answer of 'verbs' for a construct"
echo "# module 'lookaround' owns is the same defect class registry.c:692"
echo "# already records for (?*...). Reported as a MEASUREMENT, not inferred:"
for n in pla plb nla nlb napla naplb \
         positive_lookahead positive_lookbehind \
         negative_lookahead negative_lookbehind \
         non_atomic_positive_lookahead non_atomic_positive_lookbehind
do
  out=$(/usr/bin/gnutimeout 10 "$PCREC" -p rx -o /dev/null "(*$n:a)b" 2>&1) || true
  printf '%-40s -> %s\n' "(*$n:a)b" "$(printf '%s' "$out" | tr '\n' ' ')"
done
echo "# the verb NAME table's own lookaround entries (grep, for provenance):"
grep -n 'lookahead\|lookbehind\|^{"pla"\|^{"plb"\|^{"nla"\|^{"nlb"\|^{"napla"\|^{"naplb"' src/parse/mod_verbs.c | grep '^[0-9]*:{' || true
echo "# the (* doorway row that answers for all of them:"
grep -n 'FIXED(RK_VERB' src/parse/registry.c || true
echo

echo "=== AXIS D: vm_cut and the atomic lowering, as they are in src/ ======"
echo "# vm_cut's definition (the substrate §3 reuses):"
sed -n '/^static void vm_cut(Vm \*v, int slot, const char \*role)$/,/^}$/p' \
    src/gen/emit_vm.c | sed 's/^/    /'
echo "# vm_cut's line number:"
grep -n '^static void vm_cut' src/gen/emit_vm.c
echo "# vm_atomic's body (the shape §3.1 mirrors), from its signature:"
sed -n '/^static void vm_atomic(Vm \*v, int entry, const Ast \*a, int next)$/,/^}$/p' \
    src/gen/emit_vm.c | sed 's/^/    /'
echo "# the five primitives' signatures:"
grep -n '^static void vm_lbl\|^static void vm_goto\|^static void vm_fail\|^static void vm_push_at\|^static void vm_push(\|^static void vm_set\|^static void vm_work' src/gen/emit_vm.c
echo "# the A_BREF arm's seam call, which §4's back-step mirrors:"
grep -n 'pcrec_enc_entry_engine_callable\|_bref_match' src/gen/emit_vm.c
echo

echo "=== AXIS E: the assertions module's alphabet-context machinery ======="
echo "# the AST kinds that exist today (src/core/internal.h):"
grep -n '^    A_[A-Z_]*,' src/core/internal.h
echo "# the seam's entries today (src/gen/enc/enc.h):"
grep -n 'PCREC_ENCE_[A-Z_]* *=' src/gen/enc/enc.h
echo "# the seam's entry table (src/gen/enc/enc_byte.c):"
sed -n '/^static const PcrecEncEntry entries_byte\[\]/,/^};$/p' src/gen/enc/enc_byte.c \
    | sed 's/^/    /'
echo "# select_engine's forcing rules (which ones a lookaround would join):"
grep -n 'static bool forces_\|forces_captures\|forces_kreset\|forces_bref' src/opt/select_engine.c
echo "# mrl.c's written-down inheritance for lookaround (P: it says ZERO):"
sed -n '25,45p' src/opt/mrl.c | sed 's/^/    /'
