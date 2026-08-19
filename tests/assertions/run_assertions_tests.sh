#!/usr/bin/env bash
# tests/assertions/run_assertions_tests.sh — module `assertions`, [M6.2] wave
# A: the checks a `.rxt` file structurally CANNOT make.
#
# Three of them, and each is here because the corpus is blind to it:
#
#  1. THE ORACLE. tests/assertions/verify_pcre2.py re-verifies every cell in
#     this directory against libpcre2, because python3 `re` — the project's
#     base-tier oracle — is measurably WRONG about `\Z` (its `\Z` is PCRE2's
#     `\z`, and it disagrees in the silent direction: no match where PCRE2
#     matches, and a shorter span where PCRE2 reports a longer one). A
#     python-derived `\Z` expectation would encode `\z` and the corpus would
#     go green on a miscompile. SKIPS LOUDLY without libpcre2, PC-3's pattern.
#
#  2. THE CONTROL UNDER tests/reject's TWO-ANSWER PINS. `\b` refuses one way
#     with the module OFF ("requires module 'assertions'") and a DIFFERENT way
#     with it ON ("module 'assertions' is enabled but \b is not implemented
#     yet"), because the first sentence becomes a lie the moment the module is
#     enabled. Those two sentences are pinned in tests/reject/ — its `==
#     assertions ==` section, both gate states adjacent — because that is the
#     house home for a refusal's text. What CANNOT live there is the control
#     that stops the second row being vacuous: the three constructs this wave
#     actually builds must COMPILE with the gate open, or "not implemented
#     yet" is merely the module being empty.
#
#  3. THE D47.5 EXEMPTION ACTUALLY FIRING. A possessified quantifier and a
#     backtracking one match identically BY CONSTRUCTION — that is the claim —
#     so tests/assertions/gate.rxt stays green whichever way the analysis
#     went. The artifact's own `<PREFIX>_VM_STRATS` stamp is what can see it,
#     and it is checked here in BOTH directions: `\z`/`\Z`/`$` in the follow
#     must possessify, `\A`/`^` in the follow must NOT. Without the second
#     half this would be a check with no failing direction.
#
# Usage: bash tests/assertions/run_assertions_tests.sh
# Env: PCREC (default <root>/build/pcrec), KEEP=1

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
KEEP="${KEEP:-0}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "assertions: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---------------------------------------------------------------------------
# 1. THE LIBPCRE2 ORACLE OVER THIS DIRECTORY'S CORPUS
# ---------------------------------------------------------------------------
echo "== [M6.2] libpcre2 re-verification of tests/assertions/ =="
if python3 "$SCRIPT_DIR/verify_pcre2.py" > "$WORKDIR/oracle.log" 2>&1; then
    if grep -q "SKIP" "$WORKDIR/oracle.log"; then
        echo "SKIP: $(grep SKIP "$WORKDIR/oracle.log")"
        ok "libpcre2 oracle: skipped loudly (libpcre2-8 absent), not silently"
    else
        tail -3 "$WORKDIR/oracle.log"
        ok "libpcre2 oracle: every cell in tests/assertions/ agrees with libpcre2 (the \\Z expectations python cannot verify)"
    fi
else
    cat "$WORKDIR/oracle.log" >&2
    bad "libpcre2 oracle: tests/assertions/ cells disagree with libpcre2"
fi

# ---------------------------------------------------------------------------
# 2. THE CONTROL UNDER tests/reject's TWO-ANSWER PINS
# ---------------------------------------------------------------------------
echo
echo "== [M6.2] §9.2 the module's built constructs COMPILE, unbuilt ones refuse =="

# refuses <features-or-'bare'> <pattern> <expected substring>
refuses() {
    local feats="$1" pat="$2" want="$3" out rc
    rm -f "$WORKDIR/out.c" "$WORKDIR/out.h"
    if [ "$feats" = bare ]; then
        out="$("$PCREC" -p rx -o "$WORKDIR/out.c" -- "$pat" 2>&1 >/dev/null)"; rc=$?
    else
        out="$("$PCREC" --features "$feats" -p rx -o "$WORKDIR/out.c" -- "$pat" 2>&1 >/dev/null)"; rc=$?
    fi
    if [ "$rc" -ne 1 ]; then
        bad "[$feats] '$pat': exit $rc, not a clean exit-1 rejection (got: $out)"
        return
    fi
    case "$out" in
        *"$want"*) ;;
        *) bad "[$feats] '$pat': wrong diagnostic. want substring: $want ; got: $out"
           return ;;
    esac
    if [ -f "$WORKDIR/out.c" ] || [ -f "$WORKDIR/out.h" ]; then
        bad "[$feats] '$pat': rejected but still wrote an output file"
        return
    fi
    ok "[$feats] '$pat' -> $want"
}

# THE DIAGNOSTIC TEXT ITSELF IS PINNED IN tests/reject/, not here — that is
# the house home for "which module does a refusal name", it already carries
# both gate states for these constructs side by side, and a second copy of the
# same strings is the two-homes shape the construct registry exists to
# prevent.
#
# WHAT LIVES HERE IS THE CONTROL THOSE ROWS CANNOT BE WITHOUT: the three
# constructs wave A DOES build must COMPILE with the gate open. Without this,
# every "not implemented yet" row over there would still pass on a build where
# the module produces nothing at all — the row would be measuring the module's
# absence and reporting it as the module's partial presence.
#
# [M6.2 wave B] `\b` and `\B` JOIN THIS LIST as they LEAVE tests/reject's
# enabled-but-unbuilt list, and the two edits are one move: the day a
# construct is built, the row asserting it is NOT built has to become the row
# asserting it IS. A wave that only deleted the first half would shrink the
# reject table with nothing taking over what that row was saying. Both a
# LEADING and a TRAILING spelling of each, because the two reach different
# machinery (the forward seed and the reverse one, assertions_design.md §3.8)
# and a control that only ever compiled the leading form would not notice the
# reverse half failing to build at all.
for p in '\Aa' 'a\z' 'a\Z' '\ba' 'a\b' '\Ba' 'x\Bx'; do
    rm -f "$WORKDIR/out.c" "$WORKDIR/out.h"
    if "$PCREC" --features assertions -p rx -o "$WORKDIR/out.c" -- "$p" 2>"$WORKDIR/e.txt"; then
        ok "[assertions] '$p' COMPILES — the module's built constructs are BUILT, so tests/reject's 'is not implemented yet' rows are about the unbuilt ones rather than about an empty module"
    else
        bad "[assertions] '$p' should compile with the module enabled: $(cat "$WORKDIR/e.txt")"
    fi
done
# ...and the same ones must still REFUSE with the gate closed, which is what
# makes the line above a statement about the gate rather than about the build.
for p in '\Aa' 'a\z' 'a\Z' '\ba' 'a\b' '\Ba' 'x\Bx'; do
    refuses bare "$p" "requires module 'assertions'"
done

# ---------------------------------------------------------------------------
# 3. THE D47.5 EXEMPTION, THROUGH THE ARTIFACT'S OWN STAMP
# ---------------------------------------------------------------------------
echo
echo "== [M6.2] §8 the \$-follow exemption, in both directions =="

# PCREC_VM_STRAT_POSSESSIVE is 0x1 and PCREC_VM_STRAT_BACKTRACKING is 0x2
# (src/gen/CLAUDE.md, the shared PCREC_RX_ABI_H block since [ABI-NS]). The
# patterns are capture-bearing so they route to the VM, which is the only
# engine that stamps this.
strats() { "$PCREC" --features assertions -p rx -o - -- "$1" 2>/dev/null \
             | sed -n 's/^#define RX_VM_STRATS \(0x[0-9a-f]*\)u$/\1/p' | head -1; }

want_strat() { # want_strat <pattern> <expected> <why>
    local got; got="$(strats "$1")"
    if [ "$got" = "$2" ]; then
        ok "STRATS '$1' = $2 — $3"
    else
        bad "STRATS '$1' = '${got:-<none>}', want $2 — $3"
    fi
}

want_strat '(x)a{0,4}\z' 0x1 "\\z in the follow is exempt: its satisfying set is the singleton {n}, so no retreat can reach it"
want_strat '(x)a{0,4}\Z' 0x1 "\\Z is A_EOL, the same node \$ builds, so it takes the same exemption"
want_strat '(x)a{0,4}$'  0x1 "the shipped non-multiline \$ exemption, unmoved by the parse-time refactor"
want_strat '(x)a{0,4}\A' 0x2 "the FAILING DIRECTION: \\A is DOWNWARD-closed (a retreat CAN reach offset 0), so the analysis must decline"
want_strat '(x)a{0,4}^'  0x2 "the same, spelled ^ — \\A and ^ are one node and must answer alike"
# [M6.2 wave B] `\b`/`\B` MUST DECLINE, and this is the wave's own row in this
# check rather than an inherited one. The exemption above rests on UPWARD
# CLOSURE: if `$` fails at a quantifier's maximal exit it fails at every
# smaller retreat position too, so the retreat cannot rescue a match. A word
# boundary is closed in NEITHER direction — its truth is a property of the two
# bytes around the position, not of the position's rank — so it belongs with
# `^`, which widens and declines.
#
# The witness, in one direction: `\w{0,4}\b` on "abcd" is a boundary at the
# maximal exit 4 (end of subject) and NOT one at the retreat position 3, so
# `\b` holding at the top says nothing about the retreat. `\B` inverts it.
# A wave that let `\b` inherit `$`'s arm would possessify a quantifier whose
# retreat is the only route to the match, which is D47.5's own failure mode
# one construct over.
want_strat '(x)a{0,4}\b' 0x2 "\\b is closed in NEITHER direction (\\w{0,4}\\b on \"abcd\" is a boundary at the maximal exit and not at the retreat), so the analysis must decline"
want_strat '(x)a{0,4}\B' 0x2 "\\B is \\b's complement and equally unclosed — a construct must not inherit \$'s exemption merely by being an assertion"

# ---------------------------------------------------------------------------
# 4. [M6.2 wave B] THE COMPOSED STATE BUDGET REFUSES CLEANLY
# ---------------------------------------------------------------------------
#
# assertions_design.md §3.5.1 forecasts that `\b` MOVES the state budget and
# that some patterns compiling today will refuse with it — a CAPABILITY
# regression, accepted, and §3.5.1's own qualification 2 says so. What is not
# accepted is a MISCOMPILE at the boundary, and the difference between the two
# is entirely in what the compiler does when it runs out of states.
#
# The standing check is therefore not "the boundary is at N" (a number that
# moves with every legitimate change to the construction, and a pin someone
# would edit rather than think about). It is the property that survives:
# **on both engines, a word-context pattern past the cap refuses with the
# states-cap diagnostic and writes no output file.** The located boundary
# itself is a MEASUREMENT and lives in
# docs/design/assertions_measurements/out/wordctx_budget.txt, taken by
# probes/probe_wordctx_budget.py against both caps.
echo
echo "== [M6.2 wave B] the composed state budget refuses, never miscompiles =="

refuses_at_cap() { # refuses_at_cap <pattern> <why>
    rm -f "$WORKDIR/out.c" "$WORKDIR/out.h"
    local err
    if err="$("$PCREC" --features assertions -p rx -o "$WORKDIR/out.c" -- "$1" 2>&1)"; then
        bad "[budget] '$1' COMPILED — expected the states-cap refusal ($2)"
        return
    fi
    if [ -f "$WORKDIR/out.c" ] || [ -f "$WORKDIR/out.h" ]; then
        bad "[budget] '$1' refused but still wrote an output file"
        return
    fi
    case "$err" in
        *"too complex for the DFA engine"*)
            ok "[budget] '$1' refuses with the states-cap diagnostic and writes nothing — $2" ;;
        *)  bad "[budget] '$1' refused with something OTHER than the states cap, which is the failure this check exists to tell apart: $err" ;;
    esac
}

# ENG_UNANCH, cap PCREC_MAX_DFA_STATES_TABLE (32,000). The bare form of this
# family is §3.5.1's own worst-state-count shape.
refuses_at_cap '\b((a)|ab){20000}c\b' \
    "ENG_UNANCH past PCREC_MAX_DFA_STATES_TABLE"
# ENG_ATTEMPT, cap PCREC_MAX_DFA_STATES_GOTO (10,000) — 3.2x TIGHTER, and
# §3.4.1's disclosure is that the design's whole corpus measurement was taken
# on the engine `^` patterns do NOT use. A wave that checked only the roomier
# cap would be repeating that gap.
refuses_at_cap '^\b((a)|ab){20000}c\b' \
    "ENG_ATTEMPT past PCREC_MAX_DFA_STATES_GOTO, the 3.2x tighter cap §3.4.1 says the corpus never measured"
# THE CONTROL, and without it the two rows above would pass on a compiler that
# refused everything: the same family one order of magnitude smaller must
# COMPILE, with the word context live.
for p in '\b((a)|ab){40}c\b' '^\b((a)|ab){40}c\b'; do
    rm -f "$WORKDIR/out.c"
    if "$PCREC" --features assertions -p rx -o "$WORKDIR/out.c" -- "$p" 2>"$WORKDIR/e.txt"; then
        ok "[budget] CONTROL '$p' compiles — the two refusals above are about the CAP and not about the shape"
    else
        bad "[budget] CONTROL '$p' should compile: $(cat "$WORKDIR/e.txt")"
    fi
done

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
