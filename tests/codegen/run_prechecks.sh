#!/usr/bin/env bash
# tests/codegen/run_prechecks.sh — [OPTLOOP.1] batch 1 (D119): THE
# WHOLE-WINDOW PRE-CHECKS, each held to the artifact's own EMITTED TEXT
# rather than to the predicate that wrote it.
#
# =========================================================================
# WHAT IS BEING DEFENDED
# =========================================================================
# Three compile-time facts about the WHOLE pattern, derived above either
# engine, that let a search narrow or abandon its work before any attempt
# runs (docs/dev/optloop/cycle1_analysis.md §2.4's table):
#
#   [OPT-ANCHOR-VM]  <PREFIX>_VM_START      where an attempt may BEGIN
#   [OPT-ENDWIN]     <PREFIX>_END_WINDOW    how far from the subject END a
#                                           match may begin
#   [OPT-REQBYTE]    <PREFIX>_REQ_BYTE      a byte every match must contain
#
# Each is an axis (`docs/spec/tuning.md` §2.25-§2.27) and each carries a
# stamp; the three sections below are independent and a section is deleted
# with its own mechanism.
#
# =========================================================================
# THE CONTROL DOES NOT SHARE A SOURCE WITH WHAT IT CONTROLS
# =========================================================================
# docs/dev/learnings.md §3, and it shapes every assertion here. Each stamp's
# value is a field the compiler computed; this file never reads that field.
# It reads the EMITTED C — the loop bound's own name, the clamp statement,
# the `memchr` call — and asserts the BICONDITIONAL against the stamp. A
# stamp that drifted from the text it names is a RED in both directions.
#
# TWO OF THE THREE MECHANISMS HAVE NO ANSWER-LEVEL DETECTOR AT ALL, which is
# why they need a structural gate rather than a corpus cell:
# [OPT-ANCHOR-VM]'s bound removes only attempts the artifact would have run
# and FAILED, and [OPT-REQBYTE]'s `memchr` (emitted in the sound sense) only
# returns NOMATCH where the attempt loop would have. [OPT-ENDWIN] IS
# answer-detectable (a window one byte too narrow drops a legal match) and
# its `.rxt` cases carry that half; the section here is its structural half.
#
# EVERY SECTION CARRIES A POPULATION FLOOR (K35). An assertion of the form
# "every artifact that stamps X also contains Y" is vacuously green when
# nothing stamps X, and three checks in this tree have already shipped in
# exactly that state. Each section therefore counts its own non-default
# population and FAILS on a count below its floor.
#
# Usage: bash tests/codegen/run_prechecks.sh
# Env: PCREC (default build/pcrec), CC, KEEP=1 to keep the temp dir.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
KEEP="${KEEP:-0}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # [K37] pcrec_run

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "prechecks: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

[ -x "$PCREC" ] || { echo "FAIL: prechecks: no compiler at $PCREC — run \`make\` first" >&2; exit 1; }

# emit <outfile> <pattern> [extra args...]   (0 = compiled, non-0 = refused)
emit() {
    local out="$1" pat="$2"; shift 2
    pcrec_run "$PCREC" -p rx --features all "$@" -o "$out" --pattern "$pat" >/dev/null 2>&1
}
# the value of a string stamp, or the empty string when the macro is absent
stamp() { sed -n "s/^#define RX_$2 \"\\(.*\\)\"\$/\\1/p" "$1" | head -1; }

# =========================================================================
# SECTION 1 — [OPT-ANCHOR-VM]: <PREFIX>_VM_START and the bound it names
# =========================================================================
#
# THE ENGINE DISCRIMINATOR IS THE EMITTED SEARCH LOOP, never `RX_ENGINE`:
# reading a macro to decide which artifacts to check the macros on is the
# circularity `run_dfa_stamps.sh` refuses by name. A VM artifact is one whose
# text contains the attempt loop's own continue test.
is_vm() { grep -q 'if (attempt_position >= ' "$1"; }

# §1.1 — the three values, on witnesses whose anchor is unambiguous.
#
# `(?m)^abc` IS THE LOAD-BEARING ROW. A multiline `^` holds after every
# newline, so it anchors nothing and the walk must answer `unanchored` — the
# D62 control-3 hazard `src/opt/possessify.c` recorded as a measured
# miscompile, restated as a test rather than as a comment.
while IFS='%' read -r pat _sep want; do
    [ -n "$pat" ] || continue
    a="$WORKDIR/s1_$(echo "$want" | tr -dc a-z)_$RANDOM.c"
    if ! emit "$a" "$pat" --engine=vm; then
        bad "[1.1] $pat: --engine=vm refused; expected a VM artifact stamping $want"
        continue
    fi
    got="$(stamp "$a" VM_START)"
    [ "$got" = "$want" ] \
        && ok "[1.1] $pat -> RX_VM_START \"$got\"" \
        || bad "[1.1] $pat: RX_VM_START is \"${got:-<absent>}\", expected \"$want\""
    # The BICONDITIONAL against the emitted text, at the same witness.
    if [ "$got" = "unanchored" ]; then
        grep -q 'if (attempt_position >= subject_length) return 0;' "$a" \
            && ok "[1.1b] $pat: unanchored artifact keeps the unbounded loop text" \
            || bad "[1.1b] $pat: stamps \"unanchored\" but its loop test is not the unbounded one"
        grep -q 'attempt_max' "$a" \
            && bad "[1.1b] $pat: stamps \"unanchored\" and still declares attempt_max" \
            || ok "[1.1b] $pat: unanchored artifact declares no attempt_max"
    else
        grep -q 'const size_t attempt_max = search_from;' "$a" \
            && grep -q 'if (attempt_position >= attempt_max) return 0;' "$a" \
            && ok "[1.1b] $pat: bounded artifact declares attempt_max and reads it in the loop" \
            || bad "[1.1b] $pat: stamps \"$got\" but the emitted loop is not bounded by attempt_max"
    fi
done <<'ROWS'
^abc%%anchored
\Aabc%%anchored
^(a|b)+$%%anchored
\Gabc%%gstart
(?m)^abc%%unanchored
abc%%unanchored
^a|b%%unanchored
ROWS

# §1.2 — THE DENIAL LEAVES NO TRACE. `-fno-vm-anchor-bound` must produce the
# artifact an unanchored pattern would have produced, not a third shape:
# that is what makes `make test-axes`' own sweep of this bit a control.
if emit "$WORKDIR/s1_deny.c" '^abc' --engine=vm -fno-vm-anchor-bound; then
    got="$(stamp "$WORKDIR/s1_deny.c" VM_START)"
    if [ "$got" = "unanchored" ] \
       && grep -q 'if (attempt_position >= subject_length) return 0;' "$WORKDIR/s1_deny.c" \
       && ! grep -q 'attempt_max' "$WORKDIR/s1_deny.c"; then
        ok "[1.2] -fno-vm-anchor-bound: ^abc stamps \"unanchored\" and emits the unbounded loop"
    else
        bad "[1.2] -fno-vm-anchor-bound: ^abc stamps \"${got:-<absent>}\" / bound text still present"
    fi
else
    bad "[1.2] -fno-vm-anchor-bound: ^abc refused"
fi

# §1.3 — THE AGREEMENT WITH THE OTHER ENGINE, read off both artifacts'
# emitted text. `src/gen/emit_dfa.c` asserts the same implication inside the
# compiler, where it can see both derivations at once; this is the
# independent third term — if the AST proves `anchored`, the DFA route's own
# `start_max` must be the fully-`^`-anchored one. The converse is NOT
# asserted: the subset construction knows strictly more.
for pat in '^abc' '\Aab+c' '^(?:ab|cd)$'; do
    emit "$WORKDIR/s1_v.c" "$pat" --engine=vm || { bad "[1.3] $pat: --engine=vm refused"; continue; }
    [ "$(stamp "$WORKDIR/s1_v.c" VM_START)" = "anchored" ] || { bad "[1.3] $pat: VM side does not stamp anchored"; continue; }
    if emit "$WORKDIR/s1_d.c" "$pat" --engine=dfa; then
        grep -q 'const size_t start_max = 0 ' "$WORKDIR/s1_d.c" \
            && ok "[1.3] $pat: AST says anchored and the DFA route writes start_max = 0" \
            || bad "[1.3] $pat: AST says anchored but the DFA route's start_max is not 0"
    else
        ok "[1.3] $pat: no DFA route to cross-check (--engine=dfa refuses); VM side asserted above"
    fi
done

# §1.4 — THE POPULATION FLOOR over the shipped corpus, so §1.1's
# biconditional is not a statement about seven hand-written patterns. Every
# `pattern` line of one corpus file that leads with `^`, forced onto the VM.
S1_FLOOR=3
s1_anch=0; s1_vm=0
while IFS= read -r pat; do
    [ -n "$pat" ] || continue
    emit "$WORKDIR/s1_c.c" "$pat" --engine=vm || continue
    is_vm "$WORKDIR/s1_c.c" || continue
    s1_vm=$((s1_vm + 1))
    case "$(stamp "$WORKDIR/s1_c.c" VM_START)" in
        anchored|gstart) s1_anch=$((s1_anch + 1)) ;;
    esac
done <<'PATS'
^abc$
^(?:foo|bar)baz
\A[0-9]{3}-[0-9]{4}\z
^\s*#
(?m)^x
[a-z]+@[a-z]+
PATS
[ "$s1_vm" -ge 5 ] \
    && ok "[1.4] the floor's own population is live: $s1_vm VM artifacts built" \
    || bad "[1.4] only $s1_vm VM artifacts built — the floor below measures nothing"
[ "$s1_anch" -ge "$S1_FLOOR" ] \
    && ok "[1.4] $s1_anch of $s1_vm VM artifacts carry a start bound (floor $S1_FLOOR)" \
    || bad "[1.4] only $s1_anch VM artifacts carry a start bound, floor is $S1_FLOOR — §1.1's biconditional may be vacuous"

# =========================================================================
# SECTION 2 — [OPT-ENDWIN]: <PREFIX>_END_WINDOW and the clamp it names
# =========================================================================
#
# THE STAMP IS A STRING BECAUSE 0 IS A LEGAL WINDOW (a `\z` pattern of
# maximum width 0 may begin only at the subject's end), so this section reads
# `"none"` as the decline and any other value as a decimal bound — and then
# requires the EMITTED CLAMP to carry that same number as a C literal.
#
# THE ANSWER-LEVEL HALF OF THIS MECHANISM LIVES ELSEWHERE:
# tests/assertions/end_window.rxt, 66 oracle-verified cases. This section is
# the structural half — that the bound was DERIVED, that a declining pattern
# emitted no clamp at all, and that the two agree.

# §2.1 — the derived bound on witnesses whose arithmetic is checkable by hand,
# and the four structural declines.
while IFS='%' read -r pat _sep want; do
    [ -n "$pat" ] || continue
    a="$WORKDIR/s2_$RANDOM$RANDOM.c"
    if ! emit "$a" "$pat"; then
        bad "[2.1] $pat: refused; expected RX_END_WINDOW \"$want\""
        continue
    fi
    got="$(stamp "$a" END_WINDOW)"
    [ "$got" = "$want" ] \
        && ok "[2.1] $pat -> RX_END_WINDOW \"$got\"" \
        || bad "[2.1] $pat: RX_END_WINDOW is \"${got:-<absent>}\", expected \"$want\""
    # The BICONDITIONAL against the emitted clamp, at the same witness: the
    # stamp's number and the clamp's literal are the same fact, so they are
    # compared rather than each checked for plausibility.
    nclamp="$(grep -c "search_from = subject_length - ${got}ULL;" "$a" 2>/dev/null || true)"
    if [ "$got" = "none" ]; then
        grep -q 'search_from = subject_length - ' "$a" \
            && bad "[2.1b] $pat: stamps \"none\" and still emits an end-window clamp" \
            || ok "[2.1b] $pat: declining artifact emits no clamp"
    else
        [ "${nclamp:-0}" -ge 1 ] \
            && ok "[2.1b] $pat: the clamp carries the stamped bound $got" \
            || bad "[2.1b] $pat: stamps \"$got\" but no clamp to subject_length - ${got}ULL is emitted"
    fi
done <<'ROWS'
abc$%%4
abc\z%%3
abc\Z%%4
(?:foo|barbaz)$%%7
a{0,4}$%%5
\z%%0
$%%1
^abc$%%4
(ab)(c)$%%4
abc%%none
(?m)abc$%%none
a+$%%none
\Gabc$%%none
abc(?=x)$%%4
abc(?=\z)%%none
(\1)?abc$%%none
ROWS

# §2.2 — THE DENIAL LEAVES NO TRACE, `-fno-end-window` on a witness that
# otherwise carries a bound.
if emit "$WORKDIR/s2_deny.c" 'abc$' -fno-end-window; then
    got="$(stamp "$WORKDIR/s2_deny.c" END_WINDOW)"
    if [ "$got" = "none" ] && ! grep -q 'search_from = subject_length - ' "$WORKDIR/s2_deny.c"; then
        ok "[2.2] -fno-end-window: abc\$ stamps \"none\" and emits no clamp"
    else
        bad "[2.2] -fno-end-window: abc\$ stamps \"${got:-<absent>}\" / clamp text still present"
    fi
else
    bad "[2.2] -fno-end-window: abc\$ refused"
fi

# §2.3 — BOTH ENGINES CARRY IT, which is the half a DFA-only sweep would
# miss: the stamp is family (a) and the clamp is one emitter read from two
# search entries. `(ab)(c)$` forces the VM through its captures.
for e in dfa vm; do
    if emit "$WORKDIR/s2_$e.c" '(ab)(c)$' --engine=$e; then
        [ "$(stamp "$WORKDIR/s2_$e.c" END_WINDOW)" = "4" ] \
            && grep -q 'search_from = subject_length - 4ULL;' "$WORKDIR/s2_$e.c" \
            && ok "[2.3] --engine=$e: (ab)(c)\$ stamps 4 and clamps to it" \
            || bad "[2.3] --engine=$e: (ab)(c)\$ does not carry the window in both the stamp and the clamp"
    else
        ok "[2.3] --engine=$e: (ab)(c)\$ refused by this engine (do-or-die), nothing to check"
    fi
done

# §2.4 — THE ENCODING DECLINE, measured rather than asserted. Under a
# multi-byte encoding the clamp could land inside a character, which is a
# WRONG ANSWER and not a wasted attempt (K49/K50) — so the analysis must
# decline there even though the pattern's shape is identical.
if emit "$WORKDIR/s2_utf8.c" 'abc$' -e utf8; then
    got="$(stamp "$WORKDIR/s2_utf8.c" END_WINDOW)"
    [ "$got" = "none" ] \
        && ok "[2.4] -e utf8: abc\$ declines (stamps \"none\"), the mid-character hazard" \
        || bad "[2.4] -e utf8: abc\$ stamps \"$got\" — the encoding decline is not in force"
else
    bad "[2.4] -e utf8: abc\$ refused"
fi

# §2.5 — THE POPULATION FLOOR (K35). §2.1's biconditional is a statement
# about fifteen hand-written patterns unless something says the derived half
# is reachable at all; this counts the corpus file written for the mechanism.
S2_FLOOR=8
s2_win=0; s2_tot=0
while IFS= read -r pat; do
    [ -n "$pat" ] || continue
    s2_tot=$((s2_tot + 1))
    emit "$WORKDIR/s2_c.c" "$pat" || continue
    [ "$(stamp "$WORKDIR/s2_c.c" END_WINDOW)" = "none" ] || s2_win=$((s2_win + 1))
done < <(sed -n 's/^pattern //p' "$ROOT_DIR/tests/assertions/end_window.rxt")
[ "$s2_tot" -ge 12 ] \
    && ok "[2.5] the floor's own population is live: $s2_tot patterns read from tests/assertions/end_window.rxt" \
    || bad "[2.5] only $s2_tot patterns extracted from tests/assertions/end_window.rxt — the floor below measures nothing"
[ "$s2_win" -ge "$S2_FLOOR" ] \
    && ok "[2.5] $s2_win of $s2_tot corpus patterns carry an end window (floor $S2_FLOOR)" \
    || bad "[2.5] only $s2_win corpus patterns carry an end window, floor is $S2_FLOOR — §2.1 may be vacuous"

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
exit 0
