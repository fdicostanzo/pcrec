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
#   [OPT-REQPOS] 2b  <PREFIX>_REQ_RUN       a literal RUN every match contains
#
# Each is an axis (`docs/spec/tuning.md` §2.25-§2.28) and each carries a
# stamp; the sections below are independent and a section is deleted with its
# own mechanism.
#
# AND ONE FACT ABOUT THE OTHERS. [OPT-PRECHECK-ADMIT] (§5) is not a fifth
# analysis — it is the ADMISSION of the two `REQ_*` pre-checks, stamped
# `<PREFIX>_REQ_WHY`, which says whether the artifact acted on what the
# analysis found and, when it did not, which of the two measured declines
# applies. The split matters to every assertion in §3 and §4: those stamps name
# what the ANALYSIS found and this one names what was EMITTED, so an arm that
# wants the emitted text must read `REQ_WHY` and an arm that wants the
# derivation must not.
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
. "$ROOT_DIR/tests/lib/cc_resolve.sh"    # [MACPORT] resolves a real GNU gcc into CC

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

# §3.1 — the derived byte AND the derived run, on witnesses covering every arm
# of the walk that can contribute one and every arm that must decline.
#
# EVERY ROW CARRIES BOTH STAMPS, because since [OPTLOOP.2] batch 2 the two
# facts are chosen together: a pattern with a run of two or more bytes emits
# the RUN check and `RX_REQ_BYTE` is then the run's own scan member, while a
# pattern with a byte and no run emits the one-byte check with the whole
# necessary SET's own pick. A row asserting only one of the two could not tell
# those apart, which is the population split the whole section turns on.
#
# THE EXPECTED VALUES ARE LITERALS, hand-derived from the shipped prior and
# from the walk's stated arms, NEVER recomputed here from
# `pcrec_byte_freq_ppm` — a check that recomputed the rule from the table
# would share a source with what it controls (docs/dev/learnings.md §3) and
# would pass under any table at all.
#
# `(?i)abc` is the arm worth naming: D23 folds a caseless literal to a
# two-member class at PARSE time, so there is no singleton left to find — an
# analysis that read the pattern text instead of the lowered tree would answer
# 99 here and emit a `memchr` for `c` that `(?i)abC` legitimately does not
# contain. `a{2,4}b` is the second: its run is one byte because nothing is
# joined across a repeat's ITERATIONS, so it does NOT report `aa`.
while IFS='%' read -r pat _sep want wantrun; do
    [ -n "$pat" ] || continue
    a="$WORKDIR/s3_$RANDOM$RANDOM.c"
    if ! emit "$a" "$pat"; then
        bad "[3.1] $pat: refused; expected RX_REQ_BYTE \"$want\""
        continue
    fi
    got="$(stamp "$a" REQ_BYTE)"
    gotrun="$(stamp "$a" REQ_RUN)"
    [ "$got" = "$want" ] \
        && ok "[3.1] $pat -> RX_REQ_BYTE \"$got\"" \
        || bad "[3.1] $pat: RX_REQ_BYTE is \"${got:-<absent>}\", expected \"$want\""
    [ "$gotrun" = "$wantrun" ] \
        && ok "[3.1r] $pat -> RX_REQ_RUN \"$gotrun\"" \
        || bad "[3.1r] $pat: RX_REQ_RUN is \"${gotrun:-<absent>}\", expected \"$wantrun\""
    # [OPT-PRECHECK-ADMIT] THE EMISSION IS `RX_REQ_WHY`'s QUESTION, NOT THIS
    # STAMP'S. `RX_REQ_BYTE` names what the ANALYSIS found, a fact about the
    # pattern; whether the artifact ACTED on it is the fourth stamp's, and an
    # artifact admitted out by G1/G2 carries a derived byte and no `memchr`.
    # The cross-check is asserted on EVERY row rather than only on the
    # declining ones — otherwise a compiler that stamped `"none"` in both
    # places together would pass it.
    gotwhy="$(stamp "$a" REQ_WHY)"
    if { [ "$got" = "none" ] && [ "$gotwhy" = "none" ]; } \
       || { [ "$got" != "none" ] && [ "$gotwhy" != "none" ]; }; then
        ok "[3.1w] $pat: RX_REQ_BYTE \"$got\" and RX_REQ_WHY \"$gotwhy\" agree about whether a byte was derived"
    else
        bad "[3.1w] $pat: RX_REQ_BYTE \"$got\" and RX_REQ_WHY \"$gotwhy\" disagree about whether a byte was derived"
    fi
    if [ "$gotwhy" != "emitted" ]; then
        grep -q 'memchr(subject + search_from,\|memchr(subject + rp_pos,' "$a" \
            && bad "[3.1b] $pat: RX_REQ_WHY \"$gotwhy\" and still emits a required-byte memchr" \
            || ok "[3.1b] $pat: RX_REQ_WHY \"$gotwhy\" — no pre-check emitted"
    elif [ "$gotrun" != "none" ]; then
        # The RUN form scans a moving position, so its memchr's second
        # argument is where the stamped byte appears; §4 asserts the loop's
        # own shape and the compare.
        grep -q "memchr(subject + rp_pos, ${got}, subject_length - rp_pos)" "$a" \
            && ok "[3.1b] $pat: the run scan's memchr carries the stamped byte $got" \
            || bad "[3.1b] $pat: stamps \"$got\" with run \"$gotrun\" but no run-scan memchr for that byte is emitted"
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
<[a-z]+>%%62%none
a=b%%61%613d62@1
abc%%98%616263@1
\w+@\w+%%64%none
x(?:yz)+%%122%797a@1
(ab|cd)e%%101%none
(a)(b)%%98%6162@1
[^x]c%%99%none
a{2,4}b%%98%none
(a)\1?b%%98%none
foo|bar%%none%none
(?i)abc%%none%none
a*%%none%none
(?:ab)*c%%99%none
(?<=xyz)ab%%98%6162@1
q%%113%none
ROWS

# §3.2 — THE DENIAL LEAVES NO TRACE, and `-fno-req-byte` denies the RUN with
# it: there is no run check without a byte to scan for, so a denied build must
# be indistinguishable from a pattern with neither fact.
if emit "$WORKDIR/s3_deny.c" 'a=b' -fno-req-byte; then
    got="$(stamp "$WORKDIR/s3_deny.c" REQ_BYTE)"
    gotrun="$(stamp "$WORKDIR/s3_deny.c" REQ_RUN)"
    if [ "$got" = "none" ] && [ "$gotrun" = "none" ] \
       && ! grep -q 'memchr(subject + search_from,\|memchr(subject + rp_pos,' "$WORKDIR/s3_deny.c"; then
        ok "[3.2] -fno-req-byte: a=b stamps \"none\" for BOTH facts and emits no pre-check"
    else
        bad "[3.2] -fno-req-byte: a=b stamps byte \"${got:-<absent>}\" / run \"${gotrun:-<absent>}\" / pre-check text still present"
    fi
else
    bad "[3.2] -fno-req-byte: a=b refused"
fi

# §3.3 — BOTH ENGINES, and the VM route is the one the mechanism exists for:
# a backreference declines the hybrid prefilter outright, so the pre-check is
# the only whole-window fact such an artifact can act on.
for e in dfa vm; do
    if emit "$WORKDIR/s3_$e.c" '(a)b\1=z' --engine=$e; then
        # `=z` is a two-byte necessary RUN — the backreference breaks
        # contiguity to its left — and of its two members `z` (498 ppm) is
        # rarer than `=` (3,323), so the scan member is `z` (122) at index 1,
        # which is ALSO what the one-byte rule picked before the run existed.
        # That coincidence is why this row still reads 122, and why the run
        # stamp is asserted beside it rather than instead of it.
        [ "$(stamp "$WORKDIR/s3_$e.c" REQ_BYTE)" = "122" ] \
            && [ "$(stamp "$WORKDIR/s3_$e.c" REQ_RUN)" = "3d7a@1" ] \
            && grep -q 'memchr(subject + rp_pos, 122, subject_length - rp_pos)' "$WORKDIR/s3_$e.c" \
            && ok "[3.3] --engine=$e: a backreference pattern stamps 122 / 3d7a@1 and emits its run scan" \
            || bad "[3.3] --engine=$e: the backreference witness does not carry the byte and run in both the stamps and the emitted scan"
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
# Asserted on BOTH emitted shapes, because the obligation is the same and the
# text is not: the one-byte check folds the empty-window arm into its own `||`,
# and the run check states it as a standalone `return 0;` above the scan loop.
if emit "$WORKDIR/s3_null1.c" '\w+@\w+'; then
    grep -q 'if (subject_length <= search_from ||' "$WORKDIR/s3_null1.c" \
        && ok "[3.4] the one-byte pre-check tests the window for emptiness before dereferencing the subject" \
        || bad "[3.4] the one-byte pre-check's empty-window arm is missing or not first — memchr(NULL, c, 0) is UB"
fi
if emit "$WORKDIR/s3_null2.c" 'a=b'; then
    grep -q 'if (subject_length <= search_from) return 0;' "$WORKDIR/s3_null2.c" \
        && ok "[3.4b] the run pre-check tests the window for emptiness before dereferencing the subject" \
        || bad "[3.4b] the run pre-check's empty-window arm is missing — memchr(NULL, c, 0) is UB"
fi

# §3.5 — THE POPULATION FLOOR (K35), over patterns the shipped corpus really
# contains rather than over §3.1's own sixteen.
S3_FLOOR=6
S3_RUN_FLOOR=2
s3_have=0; s3_tot=0; s3_run=0
while IFS= read -r pat; do
    [ -n "$pat" ] || continue
    s3_tot=$((s3_tot + 1))
    emit "$WORKDIR/s3_c.c" "$pat" || continue
    [ "$(stamp "$WORKDIR/s3_c.c" REQ_BYTE)" = "none" ] || s3_have=$((s3_have + 1))
    [ "$(stamp "$WORKDIR/s3_c.c" REQ_RUN)" = "none" ] || s3_run=$((s3_run + 1))
done < <(sed -n 's/^pattern //p' "$ROOT_DIR/tests/base/alternation.rxt" \
                                 "$ROOT_DIR/tests/base/classes.rxt" \
                                 "$ROOT_DIR/tests/base/bounded_repeats.rxt")
[ "$s3_tot" -ge 30 ] \
    && ok "[3.5] the floor's own population is live: $s3_tot corpus patterns read" \
    || bad "[3.5] only $s3_tot corpus patterns extracted — the floor below measures nothing"
[ "$s3_have" -ge "$S3_FLOOR" ] \
    && ok "[3.5] $s3_have of $s3_tot corpus patterns carry a required byte (floor $S3_FLOOR)" \
    || bad "[3.5] only $s3_have corpus patterns carry a required byte, floor is $S3_FLOOR — §3.1 may be vacuous"
[ "$s3_run" -ge "$S3_RUN_FLOOR" ] \
    && ok "[3.5r] $s3_run of $s3_tot corpus patterns carry a required RUN (floor $S3_RUN_FLOOR)" \
    || bad "[3.5r] only $s3_run corpus patterns carry a required run, floor is $S3_RUN_FLOOR — §4 may be vacuous"

# §3.6 — THE MULTI-BYTE SHAPE, UNDER ITS OWN ENCODING. Every §3.1 witness
# compiles under the BYTE encoding, so the derived byte's LEAD-vs-TRAILING
# choice and the caseless fold's INTERSECTION rule are exercised only by the
# identity sweep — never by this file — until now. `é` is one code point
# encoded as two bytes (0xC3 0xA9); a run of one, the analysis must still
# pick a byte, and it picks the RIGHTMOST (D23's rule for a run, unmodified,
# with no run in sight). `(?i)é` folds to {é, É} — 0xC3 0xA9 / 0xC3 0x89 —
# whose two-byte encodings share only their LEAD byte, so the derived byte is
# the INTERSECTION 0xC3 (195), not either trailing byte: an analysis that
# read pattern text instead of the lowered per-byte contribution set would
# answer "none" here, §3.1's own `(?i)abc` lesson one encoding over.
# THE VALUES MOVED AT [OPTLOOP.2] BATCH 2 AND THE REASON IS THE WHOLE POINT OF
# THE ENCODING RULE. The frequency prior is a fact about a corpus under ONE
# encoding and the shipped table is keyed to `byte` — its entire 0x80-0xFF half
# sits at the 2 ppm floor — so under `-e utf8` the pick DECLINES and falls back
# to the rightmost member, which is byte for byte the pre-[OPT-FREQPICK]
# answer. That is why `(?i)é` still reads 195 here and `-fno-req-run`
# reproduces the old value on every row: see §3.7b, which asserts it directly.
# What DOES move under `-e utf8` is the RUN, because a run of bytes is a run of
# bytes under either encoding (only the choice of which member to scan for is
# encoding-gated) — so `é` reports a two-byte run and its scan byte is the
# LEFTMOST member, 0xC3.
while IFS='%' read -r pat _sep want wantrun; do
    [ -n "$pat" ] || continue
    a="$WORKDIR/s3u_$RANDOM$RANDOM.c"
    if ! emit "$a" "$pat" -e utf8; then
        bad "[3.6] -e utf8: $pat: refused; expected RX_REQ_BYTE \"$want\""
        continue
    fi
    got="$(stamp "$a" REQ_BYTE)"
    gotrun="$(stamp "$a" REQ_RUN)"
    [ "$got" = "$want" ] \
        && ok "[3.6] -e utf8: $pat -> RX_REQ_BYTE \"$got\"" \
        || bad "[3.6] -e utf8: $pat: RX_REQ_BYTE is \"${got:-<absent>}\", expected \"$want\""
    [ "$gotrun" = "$wantrun" ] \
        && ok "[3.6r] -e utf8: $pat -> RX_REQ_RUN \"$gotrun\"" \
        || bad "[3.6r] -e utf8: $pat: RX_REQ_RUN is \"${gotrun:-<absent>}\", expected \"$wantrun\""
    # [OPT-PRECHECK-ADMIT] the same split §3.1 carries: `RX_REQ_BYTE` names
    # what the analysis found, `RX_REQ_WHY` whether the artifact acted on it,
    # and an admitted-out artifact carries a derived byte and no `memchr`.
    gotwhy="$(stamp "$a" REQ_WHY)"
    if [ "$gotwhy" != "emitted" ]; then
        grep -q 'memchr(subject + search_from,\|memchr(subject + rp_pos,' "$a" \
            && bad "[3.6b] -e utf8: $pat: RX_REQ_WHY \"$gotwhy\" and still emits a required-byte memchr" \
            || ok "[3.6b] -e utf8: $pat: RX_REQ_WHY \"$gotwhy\" — no pre-check emitted"
    elif [ "$gotrun" != "none" ]; then
        grep -q "memchr(subject + rp_pos, ${got}, subject_length - rp_pos)" "$a" \
            && ok "[3.6b] -e utf8: $pat: the run scan's memchr carries the stamped byte $got" \
            || bad "[3.6b] -e utf8: $pat: stamps \"$got\" but no run-scan memchr for that byte is emitted"
    else
        grep -q "memchr(subject + search_from, ${got}, subject_length - search_from)" "$a" \
            && ok "[3.6b] -e utf8: $pat: the memchr carries the stamped byte $got" \
            || bad "[3.6b] -e utf8: $pat: stamps \"$got\" but no memchr for that byte is emitted"
    fi
done <<'ROWS'
é%%195%c3a9@0
(?i)é%%195%none
x(é|è)y%%120%78c3@0
a\x{1F600}b%%97%61f09f988062@0
(?i)k%%none%none
é@%%195%c3a940@0
ROWS

# §3.7 — [OPT-FREQPICK]: WHICH member of the necessary set the check tests.
#
# The rule is "the member with the lowest `pcrec_byte_freq_ppm`, ties broken by
# the rightmost member when it is among the minima and by the largest such byte
# otherwise" (docs/spec/tuning.md §2.27). EVERY EXPECTED BYTE BELOW IS A
# LITERAL DERIVED BY HAND from the shipped table and quoted with its ppm, never
# computed here: a check that recomputed the rule from the same table it is
# checking would pass under any table and would be the shared-source defect
# docs/dev/learnings.md §3 catalogues.
#
# THE POPULATION IS BOTH-DIRECTIONS, which is what makes the arm discriminate.
# Rows 1-4 are patterns whose minimum is NOT the rightmost member, so a
# compiler that kept PCRE2's rule fails them; rows 5-7 are patterns whose
# minimum IS the rightmost, so a compiler that always returned the largest or
# the last byte passes them and must be caught by rows 1-4; row 8 is a TIE at
# the minimum where the rightmost member is among the minima, so a rule that
# broke ties by "largest byte" rather than by the threaded pick fails it.
#
# EVERY ROW IS RUN-FREE (each necessary byte sits between non-literals), so the
# arm reads the one-byte pick and never the run's own scan index — §4 owns that.
s37_run=0
while IFS='%' read -r pat _sep want why; do
    [ -n "$pat" ] || continue
    a="$WORKDIR/s37_$RANDOM$RANDOM.c"
    if ! emit "$a" "$pat"; then bad "[3.7] $pat: refused"; continue; fi
    [ "$(stamp "$a" REQ_RUN)" = "none" ] || s37_run=$((s37_run + 1))
    got="$(stamp "$a" REQ_BYTE)"
    [ "$got" = "$want" ] \
        && ok "[3.7] $pat -> RX_REQ_BYTE \"$got\" ($why)" \
        || bad "[3.7] $pat: RX_REQ_BYTE is \"${got:-<absent>}\", expected \"$want\" ($why)"
done <<'ROWS'
[0-9]+x[0-9]+e[0-9]+%%120%x 997 ppm beats e 84235 — the rightmost rule would pick e
[0-9]+a[0-9]+z[0-9]+%%122%z 498 beats a 54163 — rightmost agrees here by luck, kept as the pair to the row below
[0-9]+z[0-9]+a[0-9]+%%122%z 498 beats a 54163 and z is NOT rightmost — the discriminating direction
[a-z]+Q[a-z]+t[a-z]+%%81%Q 66 beats t 60061 — an upper-case letter is a tenth of its lower-case twin
[0-9]+a[0-9]+J[0-9]+%%74%J 108 beats a 54163 and J IS rightmost — a rule that ignored the table would also pass
[a-z]+\$[a-z]+%%36%a singleton set: nothing to choose, any rule agrees
[0-9]+Z[0-9]+%%90%Z 50 is the table's rarest printable letter and the only member
[0-9]+<[0-9]+>[0-9]+%%62%< and > BOTH read 332 ppm — the tie goes to the threaded rightmost pick, so >
ROWS
[ "$s37_run" -eq 0 ] \
    && ok "[3.7b] all §3.7 witnesses are run-free, so the arm reads the one-byte pick" \
    || bad "[3.7b] $s37_run of the §3.7 witnesses carry a RUN — the arm is reading the run's scan index, not the set's pick"

# §3.7c — THE ENCODING DECLINE, asserted rather than trusted. Under `-e utf8`
# the prior does not apply, so the pick must be today's RIGHTMOST member on a
# pattern where the two rules DISAGREE — `[0-9]+x[0-9]+e[0-9]+` reads 120 under
# `byte` (§3.7 row 1) and must read 101 (`e`) here. Without this row the
# decline could be implemented as a comment and nothing would fail.
if emit "$WORKDIR/s37u.c" '[0-9]+x[0-9]+e[0-9]+' -e utf8; then
    got="$(stamp "$WORKDIR/s37u.c" REQ_BYTE)"
    [ "$got" = "101" ] \
        && ok "[3.7c] -e utf8: the pick DECLINES and the rightmost member (101) is emitted, not the prior's 120" \
        || bad "[3.7c] -e utf8: RX_REQ_BYTE is \"${got:-<absent>}\", expected the rightmost member 101 — the prior is being read under an encoding it is not keyed to"
else
    bad "[3.7c] -e utf8: the witness was refused"
fi

# =========================================================================
# SECTION 4 — [OPT-REQPOS] tier 2b: <PREFIX>_REQ_RUN and the scan loop it names
# =========================================================================
#
# §3's one-byte check is this mechanism's `L = 1` case, so this section's first
# obligation is the SPLIT: an artifact emits one shape or the other, never both
# and never neither, and the stamp says which. Everything below is read off the
# artifact's own emitted text, §1-§3's discipline unchanged.

# §4.1 — THE EMITTED SCAN LOOP, in full, on witnesses whose run is derived by a
# different arm of the walk each. The expected run is a LITERAL here (§3.1r
# already pins the stamp; this arm pins the TEXT the stamp claims), with the
# scanned member and the compare's own offset spelled out — because the offset
# is where a sign error would live and no answer check in this tree would see
# it on a subject that happens to start the run at its own scan hit.
while IFS='%' read -r pat _sep run len idx off; do
    [ -n "$pat" ] || continue
    a="$WORKDIR/s4_$RANDOM$RANDOM.c"
    if ! emit "$a" "$pat"; then bad "[4.1] $pat: refused"; continue; fi
    # `run` is the run as the emitted STRING LITERAL reads it (escapes and all),
    # so its length in bytes is not its length in characters: `len` is the
    # compare's own third argument and is spelled per row rather than counted.
    # `grep -qF`, not a BRE: a run is arbitrary pattern bytes, and a run
    # beginning with `*` makes the preceding quote a QUANTIFIER — measured on
    # the `*/x` row, which read NOMATCH against text that was verbatim present.
    grep -qF "!memcmp(subject + rp_c${off:+ - $off}, \"$run\", $len)) break;" "$a" \
        && ok "[4.1] $pat: compares the $len-byte run \"$run\" at rp_c${off:+ - $off}" \
        || bad "[4.1] $pat: no constant-length memcmp of \"$run\" at rp_c${off:+ - $off} — the run's own compare is missing or moved"
    # THE SENSE, asserted separately from the run and from the offset, because
    # one sabotage row inverts exactly this and leaves both alone.
    grep -qF '&& !memcmp(subject + rp_c' "$a" \
        && ok "[4.1b] $pat: the compare's sense is '!memcmp(...)' — a MATCHING run breaks the scan" \
        || bad "[4.1b] $pat: the compare's sense is not '!memcmp(...)' — it may be inverted"
    grep -qF "memchr(subject + rp_pos, $idx, subject_length - rp_pos)" "$a" \
        && ok "[4.1c] $pat: the scan is on byte $idx" \
        || bad "[4.1c] $pat: the scan is not on byte $idx"
    # AND THE WHOLE ARTIFACT COMPILES UNDER THE HARNESS'S OWN -Werror FLAGS,
    # which is the only arm that can see the two emitted-text hazards this
    # mechanism introduces: a `-Wtype-limits` always-true guard at idx 0 and a
    # `-Wcomment` pair inside the run's own comment text.
    if "$CC" -O1 -Wall -Wextra -Werror -I"$(dirname "$a")" -c -o "$a.o" "$a" 2>"$a.cc"; then
        ok "[4.1d] $pat: the run artifact compiles clean under -Wall -Wextra -Werror"
    else
        bad "[4.1d] $pat: the run artifact FAILS the harness's own -Werror flags: $(sed -n '1,2p' "$a.cc" | tr '\n' ' ')"
    fi
done <<'ROWS'
\.tar%%.tar%4%46%
a=b%%a=b%3%61%1
x(?:yz)+%%yz%2%122%1
(a)b\1=z%%=z%2%122%1
(?:/user|/users)%%/user%5%47%
a"b%%a\"b%3%34%1
\*/x%%*/x%3%42%
ROWS

# §4.2 — WHICH SHAPE, AND NEVER BOTH. A run-bearing artifact must NOT also
# carry the one-byte check's own `!memchr(subject + search_from,` text, and a
# byte-only artifact must NOT carry the scan loop. Two artifacts, asserted in
# both directions, because a refactor that emitted both would be SOUND and
# twice as slow and no answer check could see it.
if emit "$WORKDIR/s42run.c" 'a=b' && emit "$WORKDIR/s42byte.c" '\w+@\w+'; then
    grep -q '!memchr(subject + search_from,' "$WORKDIR/s42run.c" \
        && bad "[4.2] a run-bearing artifact ALSO emits the one-byte pre-check — the two shapes are not exclusive" \
        || ok "[4.2] a run-bearing artifact emits the run scan and not the one-byte pre-check"
    grep -q 'rp_pos' "$WORKDIR/s42byte.c" \
        && bad "[4.2b] a byte-only artifact emits the run scan loop" \
        || ok "[4.2b] a byte-only artifact emits the one-byte pre-check and no scan loop"
else
    bad "[4.2] one of the two shape witnesses was refused"
fi

# §4.3 — THE WINDOW GUARD, with the POSITIVE CONTROL an absence assertion
# needs (evtriage_report.md's lesson: an absence reads green when its needle
# dies). At `idx > 0` the first conjunct is REQUIRED — a hit fewer than `idx`
# bytes past `search_from` cannot be this run's own scanned member; at
# `idx == 0` it must be ABSENT rather than emitted as `>= 0`, which is a
# `-Wtype-limits` report under the harness's own -Werror (edge1_report.md's
# recorded defect class, which §4.1d is the live detector for).
if emit "$WORKDIR/s43a.c" 'a=b'; then
    grep -qF 'if (rp_c - search_from >= 1 && rp_c - 1 + 3 <= subject_length' "$WORKDIR/s43a.c" \
        && ok "[4.3] idx > 0: both window conjuncts are emitted" \
        || bad "[4.3] idx > 0: the two-conjunct window guard is missing or reshaped"
fi
if emit "$WORKDIR/s43b.c" '\.tar'; then
    if grep -qF 'if (rp_c + 4 <= subject_length' "$WORKDIR/s43b.c"; then
        grep -q 'rp_c - search_from >=' "$WORKDIR/s43b.c" \
            && bad "[4.3b] idx == 0: the always-true first conjunct is emitted — -Wtype-limits" \
            || ok "[4.3b] idx == 0: the one-conjunct form is emitted and the always-true test is omitted"
    else
        bad "[4.3b] idx == 0: the one-conjunct window guard is missing — the positive control this absence assertion needs is dead"
    fi
fi

# §4.4 — THE DENIAL LEAVES NO TRACE, AND LEAVES THE ONE-BYTE CHECK STANDING.
# This is the arm that makes "81.4% of the corpus is untouched" a checked fact:
# under `-fno-req-run` a run-bearing pattern must emit EXACTLY the one-byte
# check, and a pattern that never had a run must be BYTE-IDENTICAL to its
# default build. Both artifacts are written to the SAME basename in different
# directories, this house's four-times-recorded `-o` trap.
mkdir -p "$WORKDIR/d1" "$WORKDIR/d2"
if emit "$WORKDIR/d1/o.c" 'a=b' && emit "$WORKDIR/d2/o.c" 'a=b' -fno-req-run; then
    r1="$(stamp "$WORKDIR/d2/o.c" REQ_RUN)"; b1="$(stamp "$WORKDIR/d2/o.c" REQ_BYTE)"
    if [ "$r1" = "none" ] && [ "$b1" = "61" ] \
       && grep -q '!memchr(subject + search_from, 61, subject_length - search_from)' "$WORKDIR/d2/o.c" \
       && ! grep -q 'rp_pos' "$WORKDIR/d2/o.c"; then
        ok "[4.4] -fno-req-run: the run is gone and the one-byte check stands on the set's own pick (61)"
    else
        bad "[4.4] -fno-req-run: run \"$r1\" / byte \"$b1\" — the denial did not fall back to the one-byte check"
    fi
else
    bad "[4.4] -fno-req-run: the witness was refused"
fi
if emit "$WORKDIR/d1/o.c" '\w+@\w+' && emit "$WORKDIR/d2/o.c" '\w+@\w+' -fno-req-run; then
    cmp -s "$WORKDIR/d1/o.c" "$WORKDIR/d2/o.c" \
        && ok "[4.4b] -fno-req-run: an artifact with no run is BYTE-IDENTICAL to its default build" \
        || bad "[4.4b] -fno-req-run moved bytes on an artifact that has no run — the axis reaches outside its own population"
fi

# §4.5 — TRUNCATION, and the expected window is computed FROM THE PRIOR BY HAND
# rather than by this check. `github_pat_` is eleven bytes; the rarest member
# under the shipped table is `_` (2,492 ppm) at index 6, and of the four 8-byte
# windows containing index 6 the four sums are
#   s=0 "github_p" 203,444   s=1 "ithub_pa" 254,232
#   s=2 "thub_pat" 268,188   s=3 "hub_pat_" 200,619
# so the lowest is s=3 and the scanned member lands at index 3 of the truncated
# run. A rule that took the LEFTMOST window containing the member would answer
# s=0 and a rule that ignored the member would answer s=3 for a different
# reason, so this row discriminates both.
if emit "$WORKDIR/s45.c" 'github_pat_[A-Za-z0-9]{4}'; then
    got="$(stamp "$WORKDIR/s45.c" REQ_RUN)"
    [ "$got" = "6875625f7061745f@3" ] \
        && ok "[4.5] an 11-byte run truncates to the lowest-prior 8-byte window containing its scanned member (hub_pat_ @3)" \
        || bad "[4.5] RX_REQ_RUN is \"${got:-<absent>}\", expected 6875625f7061745f@3 — the truncation window rule moved"
    grep -qF '"hub_pat_", 8)) break;' "$WORKDIR/s45.c" \
        && ok "[4.5b] the emitted compare carries the truncated 8-byte window and no more" \
        || bad "[4.5b] the emitted compare does not carry the truncated window"
fi
# …and under an encoding the prior is not keyed to, the LEFTMOST window
# containing the member, which for a leftmost-chosen member is the run's own
# first eight bytes.
if emit "$WORKDIR/s45u.c" 'github_pat_[A-Za-z0-9]{4}' -e utf8; then
    got="$(stamp "$WORKDIR/s45u.c" REQ_RUN)"
    [ "$got" = "6769746875625f70@0" ] \
        && ok "[4.5c] -e utf8: the truncation falls back to the leftmost window containing the member (github_p @0)" \
        || bad "[4.5c] -e utf8: RX_REQ_RUN is \"${got:-<absent>}\", expected 6769746875625f70@0 — the prior is being read under an encoding it is not keyed to"
fi

# §4.6 — BOTH ENGINES, from the one emitted text. A backreference declines the
# hybrid prefilter outright, so on the VM route the run check is the only
# whole-window fact such an artifact can act on — §3.3's population at word
# grain.
for e in dfa vm; do
    if emit "$WORKDIR/s46_$e.c" '(a)b\1=z' --engine=$e; then
        [ "$(stamp "$WORKDIR/s46_$e.c" REQ_RUN)" = "3d7a@1" ] \
            && grep -qF '!memcmp(subject + rp_c - 1, "=z", 2)) break;' "$WORKDIR/s46_$e.c" \
            && ok "[4.6] --engine=$e: the run check is emitted from the one shared text" \
            || bad "[4.6] --engine=$e: the run stamp and the emitted compare do not agree"
    else
        ok "[4.6] --engine=$e: the witness is refused by this engine (do-or-die), nothing to check"
    fi
done

# §4.7 — THE DECLINES, each on the witness for its own reason rather than on a
# shared "no run here". Every row below HAS a necessary byte (so §3's check
# still fires) and must have NO run, which is what makes each a decline rather
# than a pattern with nothing to find.
while IFS='%' read -r pat _sep why; do
    [ -n "$pat" ] || continue
    a="$WORKDIR/s47_$RANDOM$RANDOM.c"
    if ! emit "$a" "$pat"; then bad "[4.7] $pat: refused"; continue; fi
    rr="$(stamp "$a" REQ_RUN)"; rb="$(stamp "$a" REQ_BYTE)"
    if [ "$rr" = "none" ] && [ "$rb" != "none" ]; then
        ok "[4.7] $pat: declines the run and keeps the byte ($why)"
    else
        bad "[4.7] $pat: run \"$rr\" / byte \"$rb\" — expected a declined run and a live byte ($why)"
    fi
done <<'ROWS'
a{2,4}b%%nothing is joined across a repeat's iterations, so no aa
(?:xabcy|zabcw)q%%an alternation contributes only its common affixes, so abc is not claimed
a(?i)bc%%d%%a caselessly folded literal is two-member classes, so bc contributes nothing
(?:ab)*c%%a min-0 repeat breaks contiguity in the one direction that would delete a match
a[0-9]b[0-9]=%%a multi-member class breaks contiguity around it
ROWS

# §4.8 — THE POPULATION FLOOR (K35), over the corpus rather than over §4.1's
# own seven, and with its own extractor health asserted first.
S4_FLOOR=4
s4_run=0; s4_tot=0
while IFS= read -r pat; do
    [ -n "$pat" ] || continue
    s4_tot=$((s4_tot + 1))
    emit "$WORKDIR/s4_c.c" "$pat" || continue
    [ "$(stamp "$WORKDIR/s4_c.c" REQ_RUN)" = "none" ] || s4_run=$((s4_run + 1))
done < <(sed -n 's/^pattern //p' "$ROOT_DIR/tests/base/literals.rxt" \
                                 "$ROOT_DIR/tests/base/alternation.rxt" \
                                 "$ROOT_DIR/tests/base/bounded_repeats.rxt" 2>/dev/null)
[ "$s4_tot" -ge 30 ] \
    && ok "[4.8] the floor's own population is live: $s4_tot corpus patterns read" \
    || bad "[4.8] only $s4_tot corpus patterns extracted — the floor below measures nothing"
[ "$s4_run" -ge "$S4_FLOOR" ] \
    && ok "[4.8] $s4_run of $s4_tot corpus patterns carry a required run (floor $S4_FLOOR)" \
    || bad "[4.8] only $s4_run corpus patterns carry a required run, floor is $S4_FLOOR — §4.1 may be vacuous"

# =========================================================================
# SECTION 5 — [OPT-PRECHECK-ADMIT]: <PREFIX>_REQ_WHY and the text it explains
# =========================================================================
#
# §3 and §4 assert what the pre-check tests. This section asserts WHETHER it is
# there, which since [OPT-PRECHECK-ADMIT] (docs/dev/optloop/
# cycle1_ledger_reading.md §6, ratified G1+G2) is a separate question with four
# answers. The two declines are the bench's own measured regressions:
#
#   G2 ADMISSION  the route answers in ONE attempt, so a whole-window pass in
#                 front of it can only be cost — `<PREFIX>_REQ_WHY
#                 "one-attempt"`. 29 ledger cells.
#   G1 DOMINANCE  the artifact ALREADY scans a byte at least as rare, so the
#                 pre-check dismisses no window that pass would not dismiss
#                 sooner — `"dominated"`. 4 ledger cells.
#
# THE ASSERTION IS THE BICONDITIONAL, in this file's standing shape: the stamp
# on one side and the artifact's own EMITTED TEXT on the other. This section
# never reads the predicate that decided; it reads whether a `memchr` is in the
# file, whether `<string.h>` is included, and what the route's own emitted bound
# says.
#
# THE DECLINES ARE NOT ANSWER-DETECTABLE, which is why they need this section
# at all: the pre-check only ever returned the answer the engine below it then
# returns anyway, so removing it moves no cell of any `.rxt` corpus. The
# movement it DOES produce is emitted text, and that is what is asserted here.

# §5.1 — the four values, on witnesses that name their route, plus the
# biconditional against the emitted text in both directions.
#
# THE WITNESSES ARE THE LEDGER'S OWN SHAPES, so that a reader can put each row
# beside the cell it came from. `^[A-Za-z]:` is `winpath-near-miss`'s anchor
# (DFA route, `start_max` the literal 0, ledger §5: 20 ns -> 23 µs);
# `^([a-z]+)+@` is `email-nested-plus`'s (VM route, `RX_VM_START "anchored"`,
# same table); `\[` IS `wild-codegrammar-json-array-begin` (§4.3: `memchr(91)`
# at the pre-check and `memchr(91)` at the prefilter, every call); and
# `x[0-9]+Q` is the CONTROL that must keep its check — its necessary byte `Q`
# (66 ppm) is strictly rarer than the byte its own prefilter scans, `x`
# (997 ppm), which is the direction G1 must not decline.
s5_emitted=0
while IFS='%' read -r pat _sep want why; do
    [ -n "$pat" ] || continue
    a="$WORKDIR/s5_$RANDOM$RANDOM.c"
    if ! emit "$a" "$pat"; then
        bad "[5.1] $pat: refused; expected RX_REQ_WHY \"$want\""
        continue
    fi
    got="$(stamp "$a" REQ_WHY)"
    [ "$got" = "$want" ] \
        && ok "[5.1] $pat -> RX_REQ_WHY \"$got\" ($why)" \
        || bad "[5.1] $pat: RX_REQ_WHY is \"${got:-<absent>}\", expected \"$want\" ($why)"
    # THE TEXT, not the stamp: `emitted` must put a required-byte `memchr` in
    # the file and every other value must leave none. `head -1` is deliberate —
    # the candidate-start prefilter's own `memchr` is a DIFFERENT call on a
    # different position variable, and counting all of them would make this arm
    # green on a dominated artifact for the wrong reason.
    n="$(grep -c 'memchr(subject + search_from,\|memchr(subject + rp_pos,' "$a")"
    if [ "$got" = "emitted" ]; then
        s5_emitted=$((s5_emitted + 1))
        [ "$n" -ge 1 ] \
            && ok "[5.1b] $pat: \"emitted\" and the pre-check is in the file" \
            || bad "[5.1b] $pat: RX_REQ_WHY \"emitted\" and NO required-byte memchr is emitted"
    else
        [ "$n" -eq 0 ] \
            && ok "[5.1b] $pat: \"$got\" and no pre-check is in the file" \
            || bad "[5.1b] $pat: RX_REQ_WHY \"$got\" but $n required-byte memchr call(s) are still emitted"
    fi
done <<'ROWS'
^[A-Za-z]:x%%one-attempt%winpath-near-miss's anchor: a ^-anchored DFA runs one attempt
^abc$%%one-attempt%the same on the plainest possible witness
\Gfoo%%one-attempt%the \G row of the three-valued start_max: start_max = search_from, also one attempt
^([a-z]+)+@%%one-attempt%email-nested-plus's shape: the VM route, RX_VM_START "anchored", an exact hybrid in front (§5.6)
\[%%dominated%json-array-begin: the prefilter's memchr byte IS the pre-check's, 91 twice per call
q%%dominated%the same by identity on a single literal
x[0-9]+Q%%emitted%THE CONTROL: Q (66 ppm) is strictly rarer than the prefilter's x (997), so the check earns its pass
\w+@\w+%%emitted%a byte-class prefilter scans a table, not one byte — there is no byte to be dominated by
[a-z]+q%%emitted%the necessary byte is not the prefilter's table, so there is nothing to compare it against
a*%%none%no necessary byte at all: the analysis found nothing to admit or decline
ROWS
[ "$s5_emitted" -ge 3 ] \
    && ok "[5.1c] $s5_emitted of §5.1's rows still EMIT — the section is not asserting a mechanism that declines everything" \
    || bad "[5.1c] only $s5_emitted of §5.1's rows emit a pre-check; the controls have stopped controlling"

# §5.2 — G2's INHERITANCE, read off each route's own emitted bound rather than
# off the predicate. The rule `attempt_cand` already applies to the
# candidate-start prefilter is the rule the pre-check now inherits, so the
# artifact must AGREE WITH ITSELF: a `one-attempt` decline must be accompanied
# by the bound that justifies it, on whichever route it is.
#
# WITHOUT THIS ARM §5.1 WOULD PASS ON A COMPILER THAT DECLINED FOR NO REASON.
while IFS='%' read -r pat _sep route; do
    [ -n "$pat" ] || continue
    a="$WORKDIR/s52_$RANDOM$RANDOM.c"
    if ! emit "$a" "$pat"; then bad "[5.2] $pat: refused"; continue; fi
    [ "$(stamp "$a" REQ_WHY)" = "one-attempt" ] || {
        bad "[5.2] $pat: RX_REQ_WHY is not \"one-attempt\" — the witness no longer reaches the rule"
        continue
    }
    case "$route" in
      dfa)
        if grep -q 'const size_t start_max = 0 /\* fully \^-anchored \*/;' "$a" \
           || grep -q 'const size_t start_max = search_from' "$a"; then
            ok "[5.2] $pat: the DFA's own start_max bound is the one-attempt row the decline claims"
        else
            bad "[5.2] $pat: declined \"one-attempt\" but its emitted start_max is neither 0 nor search_from"
        fi
        ;;
      vm)
        if grep -q 'const size_t attempt_max = search_from;' "$a"; then
            ok "[5.2] $pat: the VM's own attempt_max bound is the one-attempt bound the decline claims"
        else
            bad "[5.2] $pat: declined \"one-attempt\" but emits no 'attempt_max = search_from' bound"
        fi
        ;;
    esac
done <<'ROWS'
^[A-Za-z]:x%%dfa
^abc$%%dfa
\Gfoo%%dfa
^([a-z]+)+@%%vm
ROWS

# §5.3 — G1's DIRECTION and its ENCODING RULE, the two places the dominance
# comparison can be got wrong.
#
# THE DIRECTION. `Q[0-9]+x` and `x[0-9]+Q` are the SAME two bytes in the two
# orders, and under `byte` the pick is the argmin either way (`Q`, 66 ppm).
# `Q[0-9]+x` therefore has its own prefilter scanning the byte the pre-check
# would test and must DECLINE; `x[0-9]+Q` has a prefilter on `x` (997 ppm) and
# must EMIT. A compiler that compared the two densities backwards, or that
# declined on the mere PRESENCE of a memchr prefilter, fails one of the pair.
#
# THE ENCODING RULE. `pcrec_byte_freq_ppm` is keyed to `byte` by its own
# contents (docs/design/reqbyte_freq_pick.md §3), so under any other encoding
# the comparison is IDENTITY ONLY. `Q[0-9]+x` is the discriminating witness a
# second time: under `-e utf8` the pick reverts to the RIGHTMOST member (`x`,
# 120), which is not the prefilter's byte, so the same pattern must EMIT there.
# Without this row the encoding decline could be implemented as a comment.
while IFS='%' read -r pat _sep enc want why; do
    [ -n "$pat" ] || continue
    a="$WORKDIR/s53_$RANDOM$RANDOM.c"
    if [ "$enc" = "utf8" ]; then set -- -e utf8; else set -- ; fi
    if ! emit "$a" "$pat" "$@"; then bad "[5.3] $pat ($enc): refused"; continue; fi
    got="$(stamp "$a" REQ_WHY)"
    [ "$got" = "$want" ] \
        && ok "[5.3] $pat ($enc) -> RX_REQ_WHY \"$got\" ($why)" \
        || bad "[5.3] $pat ($enc): RX_REQ_WHY is \"${got:-<absent>}\", expected \"$want\" ($why)"
    # and the prefilter really is the single-byte form on every row here, or
    # the comparison the row is about never happened
    [ "$(stamp "$a" DFA_PREFILTER)" = "memchr" ] \
        && ok "[5.3b] $pat ($enc): the artifact really carries a single-byte candidate-start memchr" \
        || bad "[5.3b] $pat ($enc): RX_DFA_PREFILTER is \"$(stamp "$a" DFA_PREFILTER)\" — this row's dominance comparison has no second byte to make"
done <<'ROWS'
Q[0-9]+x%%byte%dominated%the pick is Q (66 ppm) and the prefilter scans Q: identity
x[0-9]+Q%%byte%emitted%the pick is still Q but the prefilter scans x (997 ppm), so the check is strictly rarer
Q[0-9]+x%%utf8%emitted%under utf8 the pick is the RIGHTMOST member (x), which is not the prefilter's byte — identity only
ROWS

# §5.4 — THE `<string.h>` FOLLOW-THROUGH. The include is declared from the
# admission and not from `Job.req_byte`, so an artifact declined by G2 whose
# body calls no other `memchr` must not carry the header. This is the one
# emitted consequence of the decline that is not a `memchr` line, and it is
# where reading the raw field instead of the admission would show.
if emit "$WORKDIR/s54.c" '^abc$'; then
    grep -q '#include <string.h>' "$WORKDIR/s54.c" \
        && bad "[5.4] a one-attempt-declined artifact with no other memchr customer still includes <string.h>" \
        || ok "[5.4] a one-attempt-declined artifact with no other memchr customer includes no <string.h>"
fi
# ... and the other direction: a DOMINATED artifact still needs it, because the
# prefilter that dominated the pre-check is itself a `memchr` caller.
if emit "$WORKDIR/s54b.c" '\['; then
    grep -q '#include <string.h>' "$WORKDIR/s54b.c" \
        && ok "[5.4b] a dominated artifact keeps <string.h> — its own prefilter is the memchr caller" \
        || bad "[5.4b] a dominated artifact lost <string.h> and its prefilter still calls memchr"
fi

# §5.5 — THE POPULATION FLOORS (K35), over the shipped corpus rather than over
# §5.1's own nine, and with the extractor's own health asserted first. Both
# declines get a floor: an assertion that declining artifacts emit no
# pre-check is vacuous when nothing declines, and this mechanism's whole
# measured value IS the declining population.
S5_ONE_FLOOR=2   # D110: half the measured 4
S5_DOM_FLOOR=6   # D110: half the measured 12
s5_tot=0; s5_one=0; s5_dom=0; s5_emit=0
while IFS= read -r pat; do
    [ -n "$pat" ] || continue
    s5_tot=$((s5_tot + 1))
    emit "$WORKDIR/s5_c.c" "$pat" || continue
    case "$(stamp "$WORKDIR/s5_c.c" REQ_WHY)" in
      one-attempt) s5_one=$((s5_one + 1)) ;;
      dominated)   s5_dom=$((s5_dom + 1)) ;;
      emitted)     s5_emit=$((s5_emit + 1)) ;;
    esac
done < <(sed -n 's/^pattern //p' "$ROOT_DIR/tests/base/literals.rxt" \
                                 "$ROOT_DIR/tests/base/alternation.rxt" \
                                 "$ROOT_DIR/tests/base/anchors.rxt" \
                                 "$ROOT_DIR/tests/base/classes.rxt" 2>/dev/null)
[ "$s5_tot" -ge 40 ] \
    && ok "[5.5] the floors' own population is live: $s5_tot corpus patterns read" \
    || bad "[5.5] only $s5_tot corpus patterns extracted — the floors below measure nothing"
[ "$s5_one" -ge "$S5_ONE_FLOOR" ] \
    && ok "[5.5] $s5_one of $s5_tot corpus patterns decline on G2 ADMISSION (floor $S5_ONE_FLOOR)" \
    || bad "[5.5] only $s5_one corpus patterns decline on G2, floor is $S5_ONE_FLOOR — §5.1's one-attempt rows may be the only population"
[ "$s5_dom" -ge "$S5_DOM_FLOOR" ] \
    && ok "[5.5] $s5_dom of $s5_tot corpus patterns decline on G1 DOMINANCE (floor $S5_DOM_FLOOR)" \
    || bad "[5.5] only $s5_dom corpus patterns decline on G1, floor is $S5_DOM_FLOOR — §5.3's dominance rows may be the only population"
# D110's floor convention, the other two floors' own: half the measured 8
[ "$s5_emit" -ge 4 ] \
    && ok "[5.5] $s5_emit of $s5_tot corpus patterns still EMIT the pre-check — the admission has not swallowed the mechanism" \
    || bad "[5.5] only $s5_emit corpus patterns still emit a pre-check — G1/G2 may be declining a population they were never measured on"

# §5.6 — [K64] G2's VM ARM NEEDS A LINEAR ATTEMPT. On the VM route "one
# attempt" is not enough: a backtracking program's one attempt can cost the
# whole step budget, and there the pre-check is the no-match proof that bounds
# the call. G2 may decline only where an EXACT-language hybrid DFA runs in
# front (it is that proof itself) or the program is frameless (it cannot
# backtrack). The rows are the same pattern shape through every arm, so each
# pair differs by exactly the fact the arm reads; the flags are the route.
# The answer-level witness is tests/base/k64_precheck_forced_vm.rxt.
while IFS='%' read -r pat flags want why; do
    [ -n "$pat" ] || continue
    a="$WORKDIR/s56_$RANDOM$RANDOM.c"
    # shellcheck disable=SC2086  # $flags is a word list on purpose
    if ! emit "$a" "$pat" $flags; then bad "[5.6] $pat [$flags]: refused"; continue; fi
    got="$(stamp "$a" REQ_WHY)"
    [ "$got" = "$want" ] \
        && ok "[5.6] $pat [$flags] -> RX_REQ_WHY \"$got\" ($why)" \
        || bad "[5.6] $pat [$flags]: RX_REQ_WHY is \"${got:-<absent>}\", expected \"$want\" ($why)"
done <<'ROWS'
^([a-z]+)+@%--engine=vm%emitted%K64's own witness: framed, no prefilter — a backtracking one attempt keeps the check
^([a-z]+)+@%%one-attempt%the same pattern on the auto route: an exact-language hybrid runs in front
^([a-z]+)+[0-9]{3}@%-fprefilter-collapse%emitted%a COUNT-COLLAPSED hybrid is a superset language, not a no-match proof — keeps the check
^([a-z]+)+[0-9]{3}@%%one-attempt%the same pattern with the exact language in front
^[a-z]+@%--engine=vm%one-attempt%frameless forced VM: the program never pushes a frame, so the attempt is linear
ROWS
# ... and each row really took the route its reason names, or the pair above
# compares nothing: the framed witness is framed and unguarded, the frameless
# one frameless, the collapsed one collapsed.
if emit "$WORKDIR/s56r.c" '^([a-z]+)+@' --engine=vm; then
    [ "$(sed -n 's/^#define RX_VM_FRAMELESS //p' "$WORKDIR/s56r.c")" = "0" ] \
      && [ "$(stamp "$WORKDIR/s56r.c" VM_PREFILTER)" = "none" ] \
        && ok "[5.6r] ^([a-z]+)+@ --engine=vm is framed with no prefilter" \
        || bad "[5.6r] ^([a-z]+)+@ --engine=vm is no longer framed+unguarded — [5.6]'s K64 row tests nothing"
fi
if emit "$WORKDIR/s56r.c" '^[a-z]+@' --engine=vm; then
    [ "$(sed -n 's/^#define RX_VM_FRAMELESS //p' "$WORKDIR/s56r.c")" = "1" ] \
      && [ "$(stamp "$WORKDIR/s56r.c" VM_PREFILTER)" = "none" ] \
        && ok "[5.6r] ^[a-z]+@ --engine=vm is frameless with no prefilter" \
        || bad "[5.6r] ^[a-z]+@ --engine=vm is no longer frameless+unguarded — [5.6]'s frameless row tests nothing"
fi
if emit "$WORKDIR/s56r.c" '^([a-z]+)+[0-9]{3}@' -fprefilter-collapse; then
    [ "$(stamp "$WORKDIR/s56r.c" VM_PREFILTER_LANG)" = "count-collapsed" ] \
      && [ "$(sed -n 's/^#define RX_VM_FRAMELESS //p' "$WORKDIR/s56r.c")" = "0" ] \
        && ok "[5.6r] the -fprefilter-collapse row is a framed count-collapsed hybrid" \
        || bad "[5.6r] the -fprefilter-collapse row is no longer a framed count-collapsed hybrid — [5.6]'s superset row tests nothing"
fi

# =========================================================================
# SECTION 5.7 — [chkgaps] 2026-09-25: G2's ANSWER, ON A FORCED-VM ROUTE
# =========================================================================
#
# §5's own header says the two declines are "not answer-detectable in either
# direction" and that is true of every witness §5.1-§5.5 use, all of which
# are either DFA-route or already correctly declined. It is NOT true in
# general: K64 (docs/dev/known_issues.md) is exactly a G2 decline that DID
# move an answer, on a forced `--engine=vm` route the corpus's own
# `admitimpl_answerdiff.py` differential never drove — that script ran
# AUTO-route arms only, and this pattern's auto route is a different
# (linear, unaffected) machine. This section closes that reach gap with a
# real compile-link-RUN check, independent of K64's own fix (§5.6 above,
# landed while this section was in flight — this section's own witness is
# UNANCHORED and is not K64's population; see the next paragraph).
#
# THE WITNESS IS UNANCHORED ON PURPOSE, so it is NOT K64's own population —
# `req_route_one_attempt`'s VM arm (src/gen/emit_dfa.c) already declines
# ONLY when `Job.start_anchor != PCREC_SANCH_NONE`, so an UNANCHORED VM
# route (this one) is admitted TODAY: REQ_WHY reads "emitted" and the
# necessary-byte pre-check runs, exactly as it should for a route that can
# restart at every position. This section is therefore a POSITIVE CONTROL
# for the admission rule on forced VM, answer-checked end to end — not
# merely stamp-checked — so a FUTURE broadening of the same defect class
# (declining the pre-check for a route that is not genuinely bounded) has a
# real detector rather than only a structural one, independent of §5.6's
# own narrower witness.
S57_PAT='([a-zA-Z0-9._%+-]+)+@'
a="$WORKDIR/s57.c"
if ! emit "$a" "$S57_PAT" --engine=vm --step-budget=5000 --emit-main; then
    bad "[5.7] $S57_PAT: --engine=vm refused it"
else
    got="$(stamp "$a" REQ_WHY)"
    [ "$got" = "emitted" ] \
        && ok "[5.7] $S57_PAT --engine=vm -> RX_REQ_WHY \"emitted\" (unanchored: G2 correctly does NOT decline)" \
        || bad "[5.7] $S57_PAT --engine=vm: RX_REQ_WHY is \"${got:-<absent>}\", expected \"emitted\" — an unanchored route was declined, which is not this rule's population"
    if grep -qF 'memchr(subject + search_from,' "$a"; then
        ok "[5.7] the required-byte pre-check is in the file, as \"emitted\" promises"
    else
        bad "[5.7] RX_REQ_WHY is \"emitted\" but no required-byte memchr is in the file"
    fi
    bin="$WORKDIR/s57_bin"
    if ! gen_cc "[5.7] emit-main link" "$CC" -O1 -std=gnu11 -Wall -Wextra -o "$bin" "$a"; then
        bad "[5.7] $S57_PAT: the --emit-main artifact did not compile: $(printf '%s' "$GEN_CC_LOG" | tail -3 | tr '\n' ' ')"
    else
        # No '@' anywhere: the necessary-byte pre-check proves NOMATCH in one
        # memchr pass, in bounded time, regardless of the step budget — the
        # ANSWER a caller-visible run must keep giving no matter what a
        # future change to this rule does. 20 bytes is comfortably past the
        # nested-quantifier's own catastrophic threshold (K64's own
        # 3*2^(L-2)-2 formula reaches ~262,000 steps at L=20, 52x this
        # witness's own --step-budget=5000), so a wrongly-declined admission
        # would give up here rather than merely run slower.
        gen_run "prechecks-5.7-nomatch" "$bin" "aaaaaaaaaaaaaaaaaaaa" >/dev/null 2>"$WORKDIR/s57.err"
        rc=$?
        [ "$rc" -eq 1 ] \
            && ok "[5.7] subject with no '@' -> exit 1 (nomatch), in bounded time" \
            || bad "[5.7] subject with no '@' -> exit $rc, expected 1 (nomatch) ($(cat "$WORKDIR/s57.err" | tr '\n' ' '))"
        gen_run "prechecks-5.7-match" "$bin" "a@" >/dev/null 2>"$WORKDIR/s57b.err"
        rc=$?
        [ "$rc" -eq 0 ] \
            && ok "[5.7] subject \"a@\" -> exit 0 (match)" \
            || bad "[5.7] subject \"a@\" -> exit $rc, expected 0 (match) ($(cat "$WORKDIR/s57b.err" | tr '\n' ' '))"
    fi
fi

# =========================================================================
# SECTION 5.8 — [K65] ON A VM ROUTE WITH NO DFA SCAN, THE PRE-CHECK TESTS THE
# WHOLE NECESSARY SET.
# =========================================================================
#
# There the pre-check is the call's only linear no-match proof, and with one
# member tested a hostile subject answered NOMATCH or gave up according to
# which member the PICK chose. The second half of the check is an `rq_set[]`
# array of every member the first half did not test; each row's expected list
# is derived BY HAND from the pattern (never from a stamp), so the row fails
# if the analysis, the pick exclusion or the route test drifts. The
# answer-level witness is tests/base/k65_precheck_whole_set.rxt.
#   rq_set lists the members in ascending byte order; "none" = no array.
rqset() { sed -n 's/^ *static const unsigned char rq_set\[\] = { \(.*\) };$/\1/p' "$1" | head -1; }
while IFS='%' read -r pat flags want why; do
    [ -n "$pat" ] || continue
    a="$WORKDIR/s58_$RANDOM$RANDOM.c"
    # shellcheck disable=SC2086  # $flags is a word list on purpose
    if ! emit "$a" "$pat" $flags; then bad "[5.8] $pat [$flags]: refused"; continue; fi
    got="$(rqset "$a")"; got="${got:-none}"
    [ "$got" = "$want" ] \
        && ok "[5.8] $pat [$flags] -> rq_set { $got } ($why)" \
        || bad "[5.8] $pat [$flags]: rq_set is { $got }, expected { $want } ($why)"
done <<'ROWS'
(x?)([a-z]+)+Z.@\1%-e byte%64%K65's witness under byte: the prior picks Z (90), so @ (64) is the rest
(x?)([a-z]+)+Z.@\1%-e utf8%90%the same under utf8: the rightmost fallback picks @ (64), so Z (90) is the rest
(x?)([a-z]+)+Z.@#\1%-e byte%90%the RUN form: the run @# (64 35) is tested whole, so Z (90) alone is the rest
[a-z]+Z.@%--engine=vm -e byte%64%a FRAMELESS unanchored forced-VM program: linear per attempt but retried at every start, so its give-up (work, on ~200 KB) followed the pick too
(Z)\1%-e byte%none%a one-member set: the pick IS the set, nothing is left to emit
(x?)([a-z]+)+Z.@%-e byte%none%no backreference: an exact hybrid DFA scans in front, so the pick alone suffices
Z.@%--no-captures -e byte%none%the DFA engine: its scan is linear whatever the pre-check tests
ROWS
# ... and the rows that expect an array really are the route the rule reads:
# a VM artifact with no DFA scan (`RX_VM_PREFILTER "none"`) that emits the
# pre-check at all — or the rest-array rows test nothing.
if emit "$WORKDIR/s58r.c" '(x?)([a-z]+)+Z.@\1' -e byte; then
    [ "$(stamp "$WORKDIR/s58r.c" VM_PREFILTER)" = "none" ] \
      && [ "$(stamp "$WORKDIR/s58r.c" REQ_WHY)" = "emitted" ] \
      && grep -q 'memchr(subject + search_from, 90, subject_length - search_from)' "$WORKDIR/s58r.c" \
        && ok "[5.8r] the K65 witness is an unguarded VM artifact whose first half memchr's the pick (90)" \
        || bad "[5.8r] the K65 witness is no longer an unguarded VM artifact memchr'ing 90 first — [5.8]'s rows test nothing"
fi
if emit "$WORKDIR/s58r.c" '(x?)([a-z]+)+Z.@' -e byte; then
    [ "$(stamp "$WORKDIR/s58r.c" VM_PREFILTER)" = "hybrid" ] \
        && ok "[5.8r] the backreference-free control is a hybrid (a DFA scans in front)" \
        || bad "[5.8r] the backreference-free control is no longer a hybrid — [5.8]'s DFA-front row tests nothing"
fi

# =========================================================================
# SECTION 5.9 — [K66] ON THE SAME ROUTE, A RUN LONGER THAN ITS 8-BYTE WINDOW
# IS COMPARED WHOLE.
# =========================================================================
#
# `RX_REQ_RUN` names the window the prior cut from the run, and with the
# window alone compared a subject holding it but not another slice of the
# run answered NOMATCH or gave up according to that pick. The whole run is a
# second scan loop whose `memcmp` is longer than 8 bytes; each row's expected
# run and rq_set are derived BY HAND from the pattern (never from a stamp).
# The answer-level witness is tests/base/k66_precheck_whole_run.rxt.
#   "none" = no memcmp longer than 8 bytes.
wholerun() { sed -n 's/^.*!memcmp(subject + rp_c[^,]*, "\(.*\)", \([0-9]*\))) break;$/\1 \2/p' "$1" | awk '$NF > 8' | head -1; }
while IFS='%' read -r pat flags want wantrq why; do
    [ -n "$pat" ] || continue
    a="$WORKDIR/s59_$RANDOM$RANDOM.c"
    # shellcheck disable=SC2086  # $flags is a word list on purpose
    if ! emit "$a" "$pat" $flags; then bad "[5.9] $pat [$flags]: refused"; continue; fi
    got="$(wholerun "$a")"; got="${got:-none}"
    gotrq="$(rqset "$a")"; gotrq="${gotrq:-none}"
    [ "$got" = "$want" ] && [ "$gotrq" = "$wantrq" ] \
        && ok "[5.9] $pat [$flags] -> whole run { $got }, rq_set { $gotrq } ($why)" \
        || bad "[5.9] $pat [$flags]: whole run is { $got } / rq_set { $gotrq }, expected { $want } / { $wantrq } ($why)"
done <<'ROWS'
(x?)([a-z]+)+eeeeeeee~#~#~#~#\1%-e byte%eeeeeeee~#~#~#~# 16%none%K66's witness under byte: the window is ~#~#~#~#, the run is 16 bytes, and every set byte is in it
(x?)([a-z]+)+eeeeeeee~#~#~#~#\1%-e utf8%eeeeeeee~#~#~#~# 16%none%the same under utf8, whose window is eeeeeeee: both encodings now compare the same run
(x?)([a-z]+)+Q.abcdefghij\1%-e byte%abcdefghij 10%81%a 10-byte run beside a set member outside it: the rest is Q (81) alone, never the two run bytes outside the window
(x?)([a-z]+)+abcdefgh\1%-e byte%none%none%a run of exactly 8: the window IS the run, nothing more is emitted
(x?)([a-z]+)+eeeeeeee~#~#~#~#%-e byte%none%none%no backreference: an exact hybrid DFA scans in front, so the window alone suffices
(x?)([a-z]+)+eeeeeeee~#~#~#~#\1%-e byte -fno-req-run%none%35, 101%-fno-req-run: no run at all, so the one-byte pick (126) and the K65 rest (# and e) stand
ROWS
# ... and the witness really is the route the rule reads, with a run longer
# than its window — or the whole-run rows test nothing.
if emit "$WORKDIR/s59r.c" '(x?)([a-z]+)+eeeeeeee~#~#~#~#\1' -e byte; then
    [ "$(stamp "$WORKDIR/s59r.c" VM_PREFILTER)" = "none" ] \
      && [ "$(stamp "$WORKDIR/s59r.c" REQ_WHY)" = "emitted" ] \
      && [ "$(stamp "$WORKDIR/s59r.c" REQ_RUN)" = "7e237e237e237e23@0" ] \
        && ok "[5.9r] the K66 witness is an unguarded VM artifact whose REQ_RUN names an 8-byte window of a longer run" \
        || bad "[5.9r] the K66 witness is no longer an unguarded VM artifact with an 8-byte window — [5.9]'s rows test nothing"
fi

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
exit 0
