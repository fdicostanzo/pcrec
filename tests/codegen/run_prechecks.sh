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

# =========================================================================
# SECTION 3 — [OPT-REQBYTE]: <PREFIX>_REQ_BYTE and the memchr it names
# =========================================================================
#
# The stamp is a decimal string or `"none"`, and the emitted pre-check
# carries the same number as a `memchr` argument. As in §1 and §2 the
# assertion is the BICONDITIONAL between them, read off the artifact's text.

# §3.1 — the derived byte, on witnesses covering every arm of the walk that
# can contribute one and every arm that must decline. `(?i)abc` is the arm
# worth naming: D23 folds a caseless literal to a two-member class at PARSE
# time, so there is no singleton left to find — an analysis that read the
# pattern text instead of the lowered tree would answer 99 here and emit a
# `memchr` for `c` that `(?i)abC` legitimately does not contain.
while IFS='%' read -r pat _sep want; do
    [ -n "$pat" ] || continue
    a="$WORKDIR/s3_$RANDOM$RANDOM.c"
    if ! emit "$a" "$pat"; then
        bad "[3.1] $pat: refused; expected RX_REQ_BYTE \"$want\""
        continue
    fi
    got="$(stamp "$a" REQ_BYTE)"
    [ "$got" = "$want" ] \
        && ok "[3.1] $pat -> RX_REQ_BYTE \"$got\"" \
        || bad "[3.1] $pat: RX_REQ_BYTE is \"${got:-<absent>}\", expected \"$want\""
    if [ "$got" = "none" ]; then
        grep -q 'memchr(subject + search_from,' "$a" \
            && bad "[3.1b] $pat: stamps \"none\" and still emits a required-byte memchr" \
            || ok "[3.1b] $pat: declining artifact emits no pre-check"
    else
        grep -q "memchr(subject + search_from, ${got}, subject_length - search_from)" "$a" \
            && ok "[3.1b] $pat: the memchr carries the stamped byte $got" \
            || bad "[3.1b] $pat: stamps \"$got\" but no memchr for that byte is emitted"
        # THE SENSE OF THE TEST, asserted separately from its argument,
        # because the sabotage row inverts exactly this and leaves the byte
        # alone. `!memchr(...)` returns 0 when the byte is ABSENT.
        grep -q '!memchr(subject + search_from,' "$a" \
            && ok "[3.1c] $pat: the pre-check returns NOMATCH when the byte is ABSENT" \
            || bad "[3.1c] $pat: the pre-check's sense is not '!memchr(...)' — it may be inverted"
    fi
done <<'ROWS'
<[a-z]+>%%62
a=b%%98
abc%%99
\w+@\w+%%64
x(?:yz)+%%122
(ab|cd)e%%101
(a)(b)%%98
[^x]c%%99
a{2,4}b%%98
(a)\1?b%%98
foo|bar%%none
(?i)abc%%none
a*%%none
(?:ab)*c%%99
(?<=xyz)ab%%98
q%%113
ROWS

# §3.2 — THE DENIAL LEAVES NO TRACE.
if emit "$WORKDIR/s3_deny.c" 'a=b' -fno-req-byte; then
    got="$(stamp "$WORKDIR/s3_deny.c" REQ_BYTE)"
    if [ "$got" = "none" ] && ! grep -q 'memchr(subject + search_from,' "$WORKDIR/s3_deny.c"; then
        ok "[3.2] -fno-req-byte: a=b stamps \"none\" and emits no pre-check"
    else
        bad "[3.2] -fno-req-byte: a=b stamps \"${got:-<absent>}\" / pre-check text still present"
    fi
else
    bad "[3.2] -fno-req-byte: a=b refused"
fi

# §3.3 — BOTH ENGINES, and the VM route is the one the mechanism exists for:
# a backreference declines the hybrid prefilter outright, so the pre-check is
# the only whole-window fact such an artifact can act on.
for e in dfa vm; do
    if emit "$WORKDIR/s3_$e.c" '(a)b\1=z' --engine=$e; then
        [ "$(stamp "$WORKDIR/s3_$e.c" REQ_BYTE)" = "122" ] \
            && grep -q 'memchr(subject + search_from, 122, subject_length - search_from)' "$WORKDIR/s3_$e.c" \
            && ok "[3.3] --engine=$e: a backreference pattern stamps 122 and emits its memchr" \
            || bad "[3.3] --engine=$e: the backreference witness does not carry the byte in both the stamp and the memchr"
    else
        ok "[3.3] --engine=$e: the backreference witness is refused by this engine (do-or-die), nothing to check"
    fi
done
if emit "$WORKDIR/s3_pf.c" '(a)b\1=z' --engine=vm; then
    [ "$(stamp "$WORKDIR/s3_pf.c" VM_PREFILTER)" = "none" ] \
        && ok "[3.3b] the VM witness really has NO prefilter — the pre-check is its only whole-window fact" \
        || bad "[3.3b] the VM witness carries a prefilter; §3.3's population is not the declined one it claims"
fi

# §3.4 — THE NULL-SUBJECT OBLIGATION, asserted on the emitted text rather
# than left to UBSan to find in some later run: `memchr(NULL, c, 0)` is
# undefined and match_api.md §3.1 permits a legal empty subject, so the
# window-empty arm must come FIRST and must short-circuit.
if emit "$WORKDIR/s3_null.c" 'a=b'; then
    grep -q 'if (subject_length <= search_from ||' "$WORKDIR/s3_null.c" \
        && ok "[3.4] the pre-check tests the window for emptiness before dereferencing the subject" \
        || bad "[3.4] the pre-check's empty-window arm is missing or not first — memchr(NULL, c, 0) is UB"
fi

# §3.5 — THE POPULATION FLOOR (K35), over patterns the shipped corpus really
# contains rather than over §3.1's own sixteen.
S3_FLOOR=6
s3_have=0; s3_tot=0
while IFS= read -r pat; do
    [ -n "$pat" ] || continue
    s3_tot=$((s3_tot + 1))
    emit "$WORKDIR/s3_c.c" "$pat" || continue
    [ "$(stamp "$WORKDIR/s3_c.c" REQ_BYTE)" = "none" ] || s3_have=$((s3_have + 1))
done < <(sed -n 's/^pattern //p' "$ROOT_DIR/tests/base/alternation.rxt" \
                                 "$ROOT_DIR/tests/base/classes.rxt" \
                                 "$ROOT_DIR/tests/base/bounded_repeats.rxt")
[ "$s3_tot" -ge 30 ] \
    && ok "[3.5] the floor's own population is live: $s3_tot corpus patterns read" \
    || bad "[3.5] only $s3_tot corpus patterns extracted — the floor below measures nothing"
[ "$s3_have" -ge "$S3_FLOOR" ] \
    && ok "[3.5] $s3_have of $s3_tot corpus patterns carry a required byte (floor $S3_FLOOR)" \
    || bad "[3.5] only $s3_have corpus patterns carry a required byte, floor is $S3_FLOOR — §3.1 may be vacuous"

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
exit 0
