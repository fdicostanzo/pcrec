#!/bin/sh
# [DD-14] §1 -- THE PREMISES, RE-VERIFIED ON HEAD RATHER THAN INHERITED.
#
# Everything this probe reports comes from THIS worktree's build/pcrec and
# from src/, not from a document. The reason is the one backrefs_design.md
# §1 states and lookaround_design.md §1 restates after two of its own
# charter premises failed: a design whose premises are quotations inherits
# every staleness in the quoted text.
#
# Axes:
#   A  every subroutine-call spelling's REFUSAL on HEAD (module attribution
#      is D26 tier 2 -- EXACT -- so the module NAME in each line is a fact
#      under test; the wording around it is tier 3 and is not)
#   B  the registry rows carrying module 'recursion' today, with engine mask
#      and D65 built column, and the row COUNT
#   C  the give-up code space as the EMITTER actually spells it, and every
#      site in the tree that would move if the floor moves -4 -> -5
#   D  the VM primitives §5 builds on, quoted from src/ by line: RX_PUSH,
#      RX_SET/RX_TRAIL, RX_CUT, the fail label
#   E  the [M6.5] reference-resolution machinery a call re-uses: the pending
#      reference, the end-of-parse pass, and the --no-captures A_CAP deletion
#      that a call must participate in
#   F  the computed-goto label machinery: is `&&label` already emitted, and
#      is there already an indirect jump other than the fail label?
set -e
PCREC=build/pcrec
test -x "$PCREC" || { echo "no $PCREC -- build first"; exit 3; }
# A pattern that COMPILES writes a .c and a .h; -o /dev/null makes the header
# /dev/null.h and the run fails for a reason that has nothing to do with the
# construct. Every cell below therefore writes to a real scratch path.
TMPC=${TMPDIR:-/tmp}/dd14_premises_$$.c

echo "pcrec binary: $PCREC ($(git rev-parse --short HEAD 2>/dev/null))"
echo

echo "=== AXIS A: every subroutine-call spelling's refusal on HEAD ========="
echo "# columns: exit-status | pattern | diagnostic"
echo "# --- default feature set (std1) ---"
for pat in \
  '(a)(?1)' '(?<n>a)(?&n)' '(a(?R)?b)' '(a)\g<1>'
do
  out=$(/usr/bin/gnutimeout 10 "$PCREC" -p rx -o "$TMPC" "$pat" 2>&1) && st=0 || st=$?
  printf 'exit=%s | %-34s | %s\n' "$st" "$pat" "$(printf '%s' "$out" | tr '\n' ' ')"
done
echo "# --- --features all (module 'recursion' ENABLED but unbuilt: D65's"
echo "#     enabled-but-not-implemented diagnostic, a DIFFERENT sentence) ---"
for pat in \
  '(a)(?1)' '(a)(?2)(b)' '(a)(?9)' \
  '(?+1)(a)' '(a)(?+1)(b)' '(a)(?-1)' '(a)(a)(?-2)' '(a)(?-01)' \
  '(?<n>a)(?&n)' '(?P<n>a)(?P>n)' \
  '(a)\g<1>' '(?<n>a)\g<n>' "(a)\\g'1'" "(?<n>a)\\g'n'" \
  '(a)\g<-1>' '(a)\g<+1>(b)' \
  '(a(?R)?b)' '(a)(?0)' \
  '(?(DEFINE)(?<x>a))(?&x)' \
  '(a)\g{1}' '(a)\1' '(a)\g1'
do
  out=$(/usr/bin/gnutimeout 10 "$PCREC" -p rx --features all -o "$TMPC" "$pat" 2>&1) && st=0 || st=$?
  test "$st" = 0 && out="COMPILES (no refusal)"
  printf 'exit=%s | %-34s | %s\n' "$st" "$pat" "$(printf '%s' "$out" | tr '\n' ' ')"
done
rm -f "$TMPC" "${TMPC%.c}.h"
echo
echo "# --- the \\g DOORWAY IS SHARED between two modules: which rows claim it? ---"
/usr/bin/gnutimeout 30 "$PCREC" --list-syntax 2>&1 \
  | awk -F'\t' '$1=="esc" && $2=="g" { printf "syntax=%-10s module=%-12s built=%s\n", $3, $4, $16 }' 
echo

echo "=== AXIS B: the registry rows for module 'recursion' today ==========="
echo "# from --list-syntax; columns per the dump's own header"
/usr/bin/gnutimeout 30 "$PCREC" --list-syntax 2>&1 \
  | awk -F'\t' '$4 == "recursion" {
        printf "kind=%-5s sel=%-2s syntax=%-34s engines=%-4s status=%-7s roadmap=%-8s quant=%-4s built=%s\n",
               $1, $2, $3, $7, $8, $13, $14, $16 }'
echo "# row count for module 'recursion':"
/usr/bin/gnutimeout 30 "$PCREC" --list-syntax 2>&1 | awk -F'\t' '$4=="recursion"' | wc -l
echo "# any 'recursion' row reading built (expect NONE before implementation):"
/usr/bin/gnutimeout 30 "$PCREC" --list-syntax 2>&1 \
  | awk -F'\t' '$4=="recursion" && $16=="built"' | wc -l
echo "# the DISTINCT selector characters the recursion rows claim at the (? doorway:"
/usr/bin/gnutimeout 30 "$PCREC" --list-syntax 2>&1 \
  | awk -F'\t' '$4=="recursion" && $1=="group" {print $2}' | sort -u | tr '\n' ' '
echo
echo "# for contrast, the rows the CONDITIONALS module owns (DEFINE lives there):"
/usr/bin/gnutimeout 30 "$PCREC" --list-syntax 2>&1 \
  | awk -F'\t' '$4 == "conditionals" { printf "sel=%-3s syntax=%-22s built=%s\n", $2, $3, $16 }'
echo "# conditionals row count:"
/usr/bin/gnutimeout 30 "$PCREC" --list-syntax 2>&1 | awk -F'\t' '$4=="conditionals"' | wc -l
echo

echo "=== AXIS C: the give-up code space, and every site the FLOOR MOVE touches ==="
echo "# --- as the DFA emitter spells the block into every artifact ---"
sed -n '/#define %s_ERR_STEPS\|PCREC_ERR_STEPS  (-2)/,+5p' src/gen/emit_dfa.c | sed 's/^/  /'
echo "# --- grep: PCREC_ERR_FLOOR, whole tree, excluding docs/dev ---"
grep -rn 'PCREC_ERR_FLOOR\|RX_ERR_FLOOR' --include='*.c' --include='*.h' --include='*.sh' \
     --include='*.md' --include='*.py' . 2>/dev/null \
  | grep -v '^\./docs/dev/' | grep -v '^\./worktrees/' | sed 's/^/  /'
echo "# --- grep: the R_* internal sentinels the VM emitter defines ---"
grep -n '_R_STEPS\|_R_FRAMES\|_R_WORK' src/gen/emit_vm.c | sed 's/^/  /'
echo "# --- the artifact-side collapse in the search entry ---"
sed -n '6244,6256p' src/gen/emit_vm.c | sed 's/^/  /'
echo "# --- what an artifact actually contains today (a VM-routed pattern) ---"
/usr/bin/gnutimeout 30 "$PCREC" -p rx --engine=vm -o "$TMPC" '(a)(b|c)+d' 2>&1 || true
grep -n 'PCREC_ERR_\|RX_R_' "$TMPC" | sed 's/^/  /'
rm -f "$TMPC" "${TMPC%.c}.h"
echo

echo "=== AXIS D: the VM primitives, quoted from src/gen/emit_vm.c ========="
echo "# --- RX_TRAIL / RX_SET / RX_PUSH / RX_CUT, the untraced forms ---"
sed -n '/^#define %s_TRAIL(slot_) do {/,/^$/p' src/gen/emit_vm.c 2>/dev/null | head -1 >/dev/null || true
awk 'NR>=5760 && NR<=5790' src/gen/emit_vm.c | sed 's/^/  /'
echo "# --- the fail label: the ONLY backtracker and the ONLY indirect jump ---"
awk 'NR>=6039 && NR<=6075' src/gen/emit_vm.c | sed 's/^/  /'
echo "# --- vm_cut(), the interface §5 reuses unchanged ---"
awk 'NR>=2110 && NR<=2135' src/gen/emit_vm.c | sed 's/^/  /'
echo "# --- the run-state struct: what a call level would have to save ---"
awk 'NR>=5657 && NR<=5670' src/gen/emit_vm.c | sed 's/^/  /'
echo

echo "=== AXIS E: the [M6.5] reference-resolution machinery a CALL reuses ==="
echo "# --- the four backref PORTS and the end-of-parse pass ---"
grep -n 'pcrec_brport_\|pcrec_bref_resolve\|pcrec_bref_mark\|pcrec_has_bref' src/core/internal.h | sed 's/^/  /'
echo "# --- PendingRef: the record a port leaves behind ---"
awk '/PendingRef/{found=1} found{print; n++} n>26{exit}' src/core/internal.h | sed 's/^/  /'
echo "# --- the --no-captures A_CAP deletion a CALL TARGET must survive ---"
grep -n 'no_captures\|captures' src/parse/mod_backrefs.c | head -14 | sed 's/^/  /'
echo "#   MEASURED: does a group survive --no-captures when only a BACKREF names it?"
/usr/bin/gnutimeout 20 "$PCREC" -p rx --features all --no-captures -o "$TMPC" '(a)\1' 2>&1 \
  && grep -c 'RX_SLOT_GROUP1' "$TMPC" | sed 's/^/    slots for group 1 with a backref, --no-captures: /'
/usr/bin/gnutimeout 20 "$PCREC" -p rx --features all --no-captures -o "$TMPC" '(a)b' 2>&1 \
  && grep -c 'RX_SLOT_GROUP1' "$TMPC" | sed 's/^/    slots for group 1 with NO reference,  --no-captures: /'
rm -f "$TMPC" "${TMPC%.c}.h"
echo "# --- named-group declarations: where a name maps to a number ---"
grep -n 'pcrec_ngport\|NameDecl\|name_decl' src/core/internal.h | head -20 | sed 's/^/  /'
echo

echo "=== AXIS F: computed goto -- is a label address already a VALUE? ====="
echo "# --- every emitted && (label address) site in the VM emitter ---"
grep -n '&&%s_L\|&&\\"\|"&&' src/gen/emit_vm.c | head -20 | sed 's/^/  /'
echo "# --- every INDIRECT jump the emitter can emit ---"
grep -n 'goto \*' src/gen/emit_vm.c | sed 's/^/  /'
echo "# --- in a real artifact: how many label addresses, how many goto* ---"
# NOT `(a)(b|c)+d`: possessify/revdet leave that shape frameless, so it
# emits ZERO label addresses and the axis would report that a construct this
# design depends on does not exist. `(a|ab)(c|cd)x` genuinely backtracks.
/usr/bin/gnutimeout 30 "$PCREC" -p rx --engine=vm -o "$TMPC" '(a|ab)(c|cd)x' 2>&1 || true
printf '  label-address (&&) occurrences: '; grep -c '&&rx_L' "$TMPC" || true
printf '  indirect jumps (goto *)       : '; grep -c 'goto \*' "$TMPC" || true
printf '  emitted label definitions     : '; grep -c '^rx_L[0-9]*:' "$TMPC" || true
echo '  the RX_PUSH call sites, verbatim:'
grep -n 'RX_PUSH(' "$TMPC" | grep -v define | sed 's/^/    /'
rm -f "$TMPC" "${TMPC%.c}.h" 
echo

echo "=== AXIS G: does anything in the tree already bound a CALL DEPTH? ===="
grep -rn 'recursion' src/parse/registry.c | head -5 | sed 's/^/  /'
echo "# --- the frame/trail capacities an artifact stamps ---"
/usr/bin/gnutimeout 30 "$PCREC" -p rx --engine=vm -o "$TMPC" '(a|ab)((b|c)+d)+' 2>&1 || true
grep -n '#define RX_RESUME_FRAMES\|#define RX_TRAIL_FRAMES\|#define RX_NSLOTS\|#define RX_STEP_BUDGET\|#define RX_WORK_BUDGET\|#define RX_VM_PRUNE_CEILING' "$TMPC" | sed 's/^/  /'
echo '  # and the same for a shape whose depth GROWS with the subject:'
/usr/bin/gnutimeout 30 "$PCREC" -p rx --engine=vm -o "$TMPC" '((a|ab)*)+z' 2>&1 || true
grep -n '#define RX_RESUME_FRAMES\|#define RX_TRAIL_FRAMES\|#define RX_VM_PRUNE_CEILING' "$TMPC" | sed 's/^/  /'
rm -f "$TMPC" "${TMPC%.c}.h" 
