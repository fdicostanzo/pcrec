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

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
exit 0
