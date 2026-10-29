#!/usr/bin/env bash
# tests/memfn/run_handoff_reach.sh -- THE VM HYBRID HANDOFF ROUTE's REACH FLOOR
# ([MEMFN] R4c, integration.md §15.5; scope.md §4, Q9; [MECH-REACH]).
# `make test-memfn-reach`.
#
# The composite PRE site's third caller is the VM engine with a DFA prefilter
# in front (`vm_emit_search_body`): `req_handoff_applies` admits ENGM_VM with
# `fit.prefilter`, so the run pre-check's answer becomes the FIRST prefilter
# call's start. The design found no witness artifact for it (§15.5), so a
# migration's identity sweep (I2) could pass without ever rendering this
# route. This check closes that: three witness patterns, each compiled by
# build/pcrec and required to carry, in its ARTIFACT,
#     RX_ENGINE "vm", RX_VM_PREFILTER "hybrid", RX_REQ_HANDOFF "<k>" and
#     `handoff_position = rx_reqrun(` followed by an `rx_prefilter(` call
# (and, for the pair-arm witness, the pair arm's locals), AND to be a pattern
# of the oracle-verified corpus (tests/litscan/handoff.rxt, written by
# gen_handoff.py), so the sweep over the corpus reaches the route and the
# corpus answers on it. [REQRUN-VM] the two `RX_DFA_PREFILTER "handoff"`
# rows are the prefilter's own RE-ENTRY (tuning.md §2.41¶8a), bench subst
# case 2's pattern among them (a pattern of tests/litscan/handoff_vm.rxt).
# HANDOFF_REACH_FLOOR is the number of witnesses that
# must be reached, a literal sharing no source with the pattern list.
#
# Usage: bash tests/memfn/run_handoff_reach.sh [ROOT]
#   PCREC defaults to ROOT/build/pcrec; TMPDIR is the scratch (or the system's).

set -u

HANDOFF_REACH_FLOOR=4

here="$(cd "$(dirname "$0")" && pwd)"
root="${1:-$(cd "$here/../.." && pwd)}"
pcrec="${PCREC:-$root/build/pcrec}"
corpus="$root/tests/litscan/handoff.rxt"
work="$(mktemp -d "${TMPDIR:-/tmp}/handoffreach.XXXXXX")" || exit 2
trap 'rm -rf "$work"' EXIT

passed=0
failed=0
ok()  { passed=$((passed + 1)); echo "PASS: $*"; }
bad() { failed=$((failed + 1)); echo "FAIL: $*"; }

echo "== VM hybrid handoff route: reach floor =="
if [ ! -x "$pcrec" ]; then
    bad "no compiler at $pcrec (run make first)"
fi

reached=0
# pattern <TAB> RX_REQ_HANDOFF <TAB> extra fixed string the artifact must carry ('-' = none)
while IFS=$'\t' read -r pat want extra; do
    [ -z "$pat" ] && continue
    out="$work/w.c"
    rm -f "$out"
    if ! "$pcrec" --features all -p rx -o "$out" --pattern "$pat" 2>"$work/err"; then
        bad "$pat: compile failed: $(head -c 200 "$work/err")"
        continue
    fi
    miss=""
    grep -qF '#define RX_ENGINE "vm"' "$out"            || miss="$miss RX_ENGINE=vm"
    grep -qF '#define RX_VM_PREFILTER "hybrid"' "$out"  || miss="$miss RX_VM_PREFILTER=hybrid"
    grep -qF "#define RX_REQ_HANDOFF \"$want\"" "$out"   || miss="$miss RX_REQ_HANDOFF=$want"
    grep -qF 'handoff_position = rx_reqrun(' "$out"      || miss="$miss handoff_position"
    grep -qE 'rx_prefilter\(subject, subject_length, handoff_position' "$out" \
                                                         || miss="$miss prefilter-at-handoff"
    if [ "$extra" != "-" ]; then
        grep -qF "$extra" "$out" || miss="$miss [$extra]"
    fi
    if [ -n "$miss" ]; then
        bad "$pat: the artifact does not reach the route; missing:$miss"
        continue
    fi
    if grep -qxF "pattern $pat" "$corpus" "$root/tests/litscan/handoff_vm.rxt" 2>/dev/null; then
        ok "$pat: reaches the VM hybrid handoff (RX_REQ_HANDOFF $want) and is a corpus pattern"
        reached=$((reached + 1))
    else
        bad "$pat: reaches the route but is not a pattern of tests/litscan/handoff.rxt or handoff_vm.rxt (the sweep would not render it)"
    fi
done <<'WITNESSES'
(ab)c?userpass	3	-
(x)?userz	1	#define RX_DFA_PREFILTER "handoff"
/(phpmyadmin|wp-admin)/[a-z]+\.php	6	#define RX_DFA_PREFILTER "handoff"
(?i)(cat)s?dog	4	size_t ha = 0, hb = 0;
WITNESSES

echo "witnesses reached: $reached (floor $HANDOFF_REACH_FLOOR)"
if [ "$reached" -lt "$HANDOFF_REACH_FLOOR" ]; then
    bad "only $reached of the VM hybrid handoff witnesses are reached, below the floor of $HANDOFF_REACH_FLOOR"
else
    ok "reach floor: $reached >= $HANDOFF_REACH_FLOOR"
fi

# [REQRUN-VM] (lane reqvm1; tuning.md §2.41¶8b) THE VM ATTEMPT LOOP's ROWS.
# A VM artifact with no DFA scan (`--engine=vm`) hands off to the whole run's
# first hit less K (`attempt_position = handoff_position`) and, on
# `handoff-attempts`, re-enters after each failed attempt (the retry's
# `landmark_position < attempt_position` re-ask). Each witness pins the row
# the admission must reach: `re` (re-entered), `entry` (entry only: a
# set-rest byte the run does not hold) or `none` (declined: one attempt, an
# unbounded K). The declines move no answer (a skipped attempt on them would
# be sound or be no skip at all), so this pin is their only detector; an
# admitted witness must also be a pattern of tests/litscan/handoff_vm.rxt,
# whose answers the corpus checks on the route. VM_ATTEMPT_FLOOR counts the
# admitted witnesses reached, a literal sharing no source with the list.
VM_ATTEMPT_FLOOR=4
vmcorpus="$root/tests/litscan/handoff_vm.rxt"
echo "== VM attempt loop handoff rows: reach floor and declines =="
vmreached=0
# pattern <TAB> encoding <TAB> RX_REQ_HANDOFF <TAB> re|entry|none <TAB> extra
# fixed string the artifact must carry ('-' = none)
while IFS=$'\t' read -r pat enc want row extra; do
    [ -z "$pat" ] && continue
    out="$work/v.c"
    rm -f "$out"
    if ! "$pcrec" --features all -p rx --engine=vm -e "$enc" -o "$out" --pattern "$pat" 2>"$work/err"; then
        bad "$pat: compile failed: $(head -c 200 "$work/err")"
        continue
    fi
    miss=""
    grep -qF '#define RX_VM_PREFILTER "none"' "$out"   || miss="$miss RX_VM_PREFILTER=none"
    grep -qF "#define RX_REQ_HANDOFF \"$want\"" "$out" || miss="$miss RX_REQ_HANDOFF=$want"
    entry=0; re=0
    grep -qF 'attempt_position = handoff_position;' "$out" && entry=1
    grep -qF 'if (landmark_position < attempt_position) {' "$out" && re=1
    case "$row" in
        re)    [ "$entry$re" = 11 ] || miss="$miss entry+re-entry(have $entry$re)" ;;
        entry) [ "$entry$re" = 10 ] || miss="$miss entry-only(have $entry$re)" ;;
        none)  [ "$entry$re" = 00 ] || miss="$miss no-handoff(have $entry$re)" ;;
    esac
    if [ "${extra:--}" != "-" ]; then
        grep -qF "$extra" "$out" || miss="$miss [$extra]"
    fi
    if [ -n "$miss" ]; then
        bad "$pat ($enc): not the $row row; missing:$miss"
        continue
    fi
    if [ "$row" = none ]; then
        ok "$pat ($enc): declined (RX_REQ_HANDOFF none)"
    elif [ -r "$vmcorpus" ] && grep -qxF "pattern $pat" "$vmcorpus"; then
        ok "$pat ($enc): reaches the attempt loop's $row row (RX_REQ_HANDOFF $want) and is a corpus pattern"
        vmreached=$((vmreached + 1))
    else
        bad "$pat ($enc): reaches the $row row but is not a pattern of tests/litscan/handoff_vm.rxt"
    fi
done <<'VMWITNESSES'
(?:xx|y)abc	byte	1	re	-
(a|aa){0,10}cxyz	byte	20	re	-
.{1,3}cd	utf8	12	re	while (!(attempt_position >= subject_length || (subject[attempt_position] & 0xC0) != 0x80)) attempt_position++;
x{2,5}(?i:cat)	byte	5	entry	-
^abcd	byte	none	none	-
^(?:ab|x)cdef	byte	none	none	#define RX_REQ_WHY "emitted"
\Gabcd	byte	none	none	-
a+xyz	byte	none	none	-
(a)\1xyz	byte	none	none	-
VMWITNESSES

echo "attempt-loop witnesses reached: $vmreached (floor $VM_ATTEMPT_FLOOR)"
if [ "$vmreached" -lt "$VM_ATTEMPT_FLOOR" ]; then
    bad "only $vmreached of the VM attempt loop witnesses are reached, below the floor of $VM_ATTEMPT_FLOOR"
else
    ok "attempt-loop reach floor: $vmreached >= $VM_ATTEMPT_FLOOR"
fi

echo "checks passed: $passed"
echo "checks failed: $failed"
[ "$failed" -eq 0 ]
