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
# corpus answers on it. HANDOFF_REACH_FLOOR is the number of witnesses that
# must be reached, a literal sharing no source with the pattern list.
#
# Usage: bash tests/memfn/run_handoff_reach.sh [ROOT]
#   PCREC defaults to ROOT/build/pcrec; TMPDIR is the scratch (or the system's).

set -u

HANDOFF_REACH_FLOOR=3

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
    if [ -r "$corpus" ] && grep -qxF "pattern $pat" "$corpus"; then
        ok "$pat: reaches the VM hybrid handoff (RX_REQ_HANDOFF $want) and is a corpus pattern"
        reached=$((reached + 1))
    else
        bad "$pat: reaches the route but is not a pattern of tests/litscan/handoff.rxt (the sweep would not render it)"
    fi
done <<'WITNESSES'
(ab)c?userpass	3	-
(x)?userz	1	-
(?i)(cat)s?dog	0	size_t ha = 0, hb = 0;
WITNESSES

echo "witnesses reached: $reached (floor $HANDOFF_REACH_FLOOR)"
if [ "$reached" -lt "$HANDOFF_REACH_FLOOR" ]; then
    bad "only $reached of the VM hybrid handoff witnesses are reached, below the floor of $HANDOFF_REACH_FLOOR"
else
    ok "reach floor: $reached >= $HANDOFF_REACH_FLOOR"
fi

echo "checks passed: $passed"
echo "checks failed: $failed"
[ "$failed" -eq 0 ]
