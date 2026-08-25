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
. "${ROOT_DIR}/tests/lib/gen_timeout.sh"  # [K37] pcrec_run
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
        out="$(pcrec_run "$PCREC" -p rx -o "$WORKDIR/out.c" -- "$pat" 2>&1 >/dev/null)"; rc=$?
    else
        out="$(pcrec_run "$PCREC" --features "$feats" -p rx -o "$WORKDIR/out.c" -- "$pat" 2>&1 >/dev/null)"; rc=$?
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
#
# [M6.2 wave C] `(?m)` JOINS on the same move, and it needs `modifiers` as
# well as `assertions` — the letter is produced by module `modifiers`' option
# run and ATTRIBUTED to `assertions`, so a control naming only one of them
# would not compile for a reason that has nothing to do with the wave. Four
# spellings, because they take four different paths: the bare run `(?m)`, the
# scoping form `(?m:...)`, the unset `(?-m)` (which was accepted before this
# wave and must stay accepted), and a `(?m)^` — the one that ROUTES to
# ENG_ATTEMPT, where a build failure would otherwise show up only as a slow
# pattern.
#
# [M6.2 wave D] `\G` JOINS on the same move, and its two spellings are chosen
# for a reason its siblings' were not. `\Gx` is the FULLY-ANCHORED shape,
# where `start_max` becomes the third string `startpos`; `\Gx|y` is the
# PARTIAL one, where `start_max` stays `n` and the start dispatch goes
# three-way. Those are DIFFERENT emitted shapes out of the same wave, and a
# control that only ever compiled the anchored form would not notice the
# three-way dispatch failing to build. (A mid-pattern `a\Gb` is deliberately
# NOT here: it is a K28 spelling — see tests/assertions/gpos.rxt's own header
# — and this loop's `-o` write is not the thing K28 breaks, but a control that
# quietly depended on an open known issue would go red the day K28 is fixed
# for reasons unrelated to `\G`.)
#
# [M6.2 wave E] `\K` JOINS AND CLOSES THE LIST — every one of the module's
# eight constructs is now on it, and tests/reject's whole `reject_gated
# assertions` paragraph retired in the same change. Three spellings, chosen
# for what each reaches rather than for coverage: `a\Kb` is the ordinary
# shape; `a\Kb|c` is the one where the `\K` sits on ONE BRANCH, so the
# trailed write has to survive an alternation whose other branch never
# performs it; and `(?:a\K)*b` puts it inside a quantifier, which is the only
# spelling where the write is performed MORE THAN ONCE per attempt and the
# capacity analysis has to have counted a trail entry per iteration
# (src/gen/emit_vm.c's vm_cost A_KRESET arm). A control that only compiled
# `a\Kb` would not notice the third failing to BUILD — it would fail at
# runtime as PCREC_ERR_FRAMES, which no compile-only control can see.
for p in '\Aa' 'a\z' 'a\Z' '\ba' 'a\b' '\Ba' 'x\Bx' '\Gx' '\Gx|y' \
         'a\Kb' 'a\Kb|c' '(?:a\K)*b'; do
    rm -f "$WORKDIR/out.c" "$WORKDIR/out.h"
    if pcrec_run "$PCREC" --features assertions -p rx -o "$WORKDIR/out.c" -- "$p" 2>"$WORKDIR/e.txt"; then
        ok "[assertions] '$p' COMPILES — the module's built constructs are BUILT, so tests/reject's 'is not implemented yet' rows are about the unbuilt ones rather than about an empty module"
    else
        bad "[assertions] '$p' should compile with the module enabled: $(cat "$WORKDIR/e.txt")"
    fi
done
for p in '(?m)a$' '(?m:a$)' '(?-m)a$' '(?m)^a'; do
    rm -f "$WORKDIR/out.c" "$WORKDIR/out.h"
    if pcrec_run "$PCREC" --features assertions,modifiers -p rx -o "$WORKDIR/out.c" -- "$p" 2>"$WORKDIR/e.txt"; then
        ok "[assertions] '$p' COMPILES — wave C's letter is BUILT, which is what takes over from the two 'inline option m is not implemented yet' rows tests/reject just retired"
    else
        bad "[assertions] '$p' should compile with assertions+modifiers enabled: $(cat "$WORKDIR/e.txt")"
    fi
done
# ...and the same ones must still REFUSE with the gate closed, which is what
# makes the line above a statement about the gate rather than about the build.
for p in '\Aa' 'a\z' 'a\Z' '\ba' 'a\b' '\Ba' 'x\Bx' '\Gx' '\Gx|y' \
         'a\Kb' 'a\Kb|c' '(?:a\K)*b'; do
    refuses bare "$p" "requires module 'assertions'"
done
# `(?m)`'s gate-closed twin is `modifiers` WITHOUT `assertions`: bare would
# refuse for the wrong module (`modifiers` is in std1, `assertions` is not),
# so the refusal that proves the ATTRIBUTION is the one taken with the option
# run's own module already on. `(?-m)` is deliberately not here — it is
# accepted with no module at all, which is the claim beside it.
for p in '(?m)a$' '(?m:a$)' '(?m)^a'; do
    refuses modifiers "$p" "inline option 'm' (multiline) requires module 'assertions'"
done

# ---------------------------------------------------------------------------
# 2b. [M6.2 wave D] THE BARE-ANCHOR RULE'S `--no-captures` HALF
# ---------------------------------------------------------------------------
# PCRE2 refuses a quantified BARE zero-width assertion (`\b*` is error 109)
# and accepts a quantified GROUP around one (`(\b)*` compiles to (0,0)).
# pcrec drove that from FOUR hand copies of one node-kind set and wave B added
# `\b`/`\B` to two of them; wave D made it ONE predicate
# (`pcrec_is_bare_anchor`, src/parse/parse.c) with four readers.
#
# **THIS BLOCK EXISTS FOR THE HALF NO `.rxt` FILE CAN REACH.**
# tests/assertions/gpos.rxt section 8 carries the `(?i:...)` spellings, which
# are over-rejected on the DEFAULT path and are that fix's failing direction.
# mod_named_groups.c's stale copy is reachable only under `--no-captures`, and
# the reason is worth knowing rather than working around: a named group wraps
# its body in `A_CAP`, an `A_CAP` is not a bare anchor, so at default captures
# the quantifier lands on the wrapper and the stale copy never decides
# anything. MEASURED on a pre-fix build: `(?<n>\b)*` COMPILES at default
# captures and REFUSES under `--no-captures`. The `.rxt` format has no way to
# pass that flag (`flags` maps `i` and nothing else), so the assertion lives
# here.
#
# The `\A` row is the CONTROL: it was accepted before this wave under BOTH
# capture modes, so a "fix" that widened the wrong way moves it.
for p in '(?<n>\b)*' '(?<n>\B)*' '(?<n>\G)*' '(?<n>\K)*' '(?<n>\A)*'; do
    rm -f "$WORKDIR/out.c" "$WORKDIR/out.h"
    if pcrec_run "$PCREC" --features assertions,named-groups --no-captures -p rx \
                -o "$WORKDIR/out.c" -- "$p" 2>"$WORKDIR/e.txt"; then
        ok "[assertions] '$p' COMPILES under --no-captures — the bare-anchor rule has ONE home, and this is the only path that reaches mod_named_groups.c's former copy of it"
    else
        bad "[assertions] '$p' should compile under --no-captures (libpcre2 gives (0,0)): $(cat "$WORKDIR/e.txt")"
    fi
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
strats() { pcrec_run "$PCREC" --features assertions -p rx -o - -- "$1" 2>/dev/null \
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
# [M6.2 wave D] `\G` MUST DECLINE TOO, and it takes `\A`'s arm rather than
# `\b`'s — a third reason for the same verdict, which is why it gets its own
# row instead of riding one of the two above. `\b` is closed in NEITHER
# direction; `\G` is closed DOWNWARD, exactly like `\A`: it holds at the one
# position `startpos`, and every retreat moves TOWARD that position rather
# than away from it. The witness is `a{0,4}\G` at startpos 0 on "aaaa" —
# the maximal exit is 4 where `\G` is false, and the retreat to 0 is the only
# route to the correct (0,0). Possessified, that pattern answers NO MATCH at
# every start.
want_strat '(x)a{0,4}\G' 0x2 "\\G is DOWNWARD-closed like \\A — every retreat moves TOWARD startpos, so a retreat CAN reach a position satisfying it and the analysis must decline"

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
    if err="$(pcrec_run "$PCREC" --features assertions -p rx -o "$WORKDIR/out.c" -- "$1" 2>&1)"; then
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
    if pcrec_run "$PCREC" --features assertions -p rx -o "$WORKDIR/out.c" -- "$p" 2>"$WORKDIR/e.txt"; then
        ok "[budget] CONTROL '$p' compiles — the two refusals above are about the CAP and not about the shape"
    else
        bad "[budget] CONTROL '$p' should compile: $(cat "$WORKDIR/e.txt")"
    fi
done

# ---------------------------------------------------------------------------
# 5. [M6.2 wave E] THE ENGINE STAMP ON A `\K` ARTIFACT
# ---------------------------------------------------------------------------
# `\K` is module `assertions`' only VM_ONLY construct, and D46's rule is that
# a selection point must be OBSERVABLE. Three surfaces carry the same fact and
# all three are asserted here, because they are produced at different places
# and a build could get one right while another says nothing:
#
#   RX_ENGINE       the compile-time macro (emit_dfa.c's shared prologue)
#   RX_ENGINE_WHY   the same, with the REASON — and the reason must name the
#                   CONSTRUCT, not "capture group", because a capture-free
#                   `\K` pattern has no other explanation available and a
#                   user reading "capture group" would reach for
#                   --no-captures, which cannot help
#   rx_info.engine  the link/runtime reflection struct (D43), which is the
#                   CANONICAL record; the macros serve compile-time consumers
#
# The CONTROL is a `\K`-free capture pattern, which is also VM-forced but for
# the OTHER reason: without it, a build that stamped "\K" on everything, or
# that had simply hardcoded the VM, would pass every row above.
kstamp() { # kstamp <label> <pattern> <want-why-substring>
    local label="$1" pat="$2" want="$3"
    rm -f "$WORKDIR/out.c"
    if ! pcrec_run "$PCREC" --features assertions -p rx -o "$WORKDIR/out.c" -- "$pat" 2>"$WORKDIR/e.txt"; then
        bad "[engine stamp] '$pat' should compile: $(cat "$WORKDIR/e.txt")"
        return
    fi
    local eng why info
    eng=$(grep -m1 '#define RX_ENGINE ' "$WORKDIR/out.c" | sed 's/.*"\(.*\)".*/\1/')
    why=$(grep -m1 '#define RX_ENGINE_WHY ' "$WORKDIR/out.c" | sed 's/.*"\(.*\)".*/\1/')
    # The emitted line is `.engine = 2, /* PCREC_ENGINE_VM */`, so the value
    # is taken by FIELD rather than by squeezing whitespace out of the whole
    # line — the trailing comment is part of the artifact's readability and a
    # check that depended on its absence would break the day it is reworded.
    info=$(grep -m1 '\.engine = ' "$WORKDIR/out.c" | sed 's/.*\.engine = \([0-9-]*\).*/\1/')
    if [ "$eng" != "vm" ]; then
        bad "[engine stamp] $label: RX_ENGINE is '$eng', want 'vm'"
    elif ! printf '%s' "$why" | grep -qF -- "$want"; then
        bad "[engine stamp] $label: RX_ENGINE_WHY is \"$why\", which does not name $want"
    elif [ "$info" != "2" ]; then
        bad "[engine stamp] $label: rx_info.engine is '$info', want 2 (PCREC_ENGINE_VM). The macro and the struct are produced at different places and D43 makes the STRUCT canonical"
    else
        ok "[engine stamp] $label: RX_ENGINE \"vm\", RX_ENGINE_WHY \"$why\", rx_info.engine PCREC_ENGINE_VM — all three surfaces agree"
    fi
}
kstamp "a \\K pattern names the CONSTRUCT" 'a\Kb' '\K'
kstamp "a \\K pattern with captures names the CAPTURE (first forcing row wins, and it is the reason a user can act on)" '(a)\Kb' 'capture group'
kstamp "CONTROL: a \\K-free capture pattern is VM-forced for the OTHER reason" '(a)b' 'capture group'

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
