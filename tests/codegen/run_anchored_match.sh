#!/usr/bin/env bash
# tests/codegen/run_anchored_match.sh — [ENG-ABS]: the ANCHORED MATCH-HERE
# form, held to the artifact rather than to its stamp.
#
# =========================================================================
# WHAT IS BEING DEFENDED
# =========================================================================
# `<prefix>_match` promises a match at exactly `ctx->pos`
# (docs/spec/match_api.md §3.2). A DFA artifact reaches that answer one of two
# ways, and names which in one stamp and one `rx_info` field:
#
#     #define RX_DFA_MATCH "unwrapped"      /* its own anchored machine */
#     #define RX_DFA_MATCH "search-filter"  /* the search, starts filtered */
#     rx_info.match_form = "unwrapped" | "search-filter" | NULL
#
# `"unwrapped"` is the form [OPT-2] STEP 2's measurement opened: the artifact
# carries a THIRD machine — the same subset construction over the same NFA,
# rooted at the pattern's own first state rather than at the start-anywhere
# self-loop — and runs it forward from `ctx->pos`, with no reverse pass and no
# candidate-start skip. `docs/design/anchored_match_unwrapped.md` is the note;
# §3 there is the argument that the two forms report the same length on every
# input, and `make test-axes`'s `-fno-anchored-dfa` sweep is what tests THAT.
#
# THIS FILE TESTS THE OTHER THING: that the artifact is the shape the stamp
# says it is. Five claims, each read out of the emitted C:
#
#   §1  the named witnesses: one pattern per documented value, expectation
#       spelled HERE rather than harvested from the artifact.
#   §2  the anchored body is prefilter-free. A candidate-start skip CHOOSES
#       WHERE THE SCAN BEGINS; under a match-here the start is the caller's,
#       so a `memchr`, a `can_begin_match` walk or an `rx_ofsskip` call inside
#       `<prefix>_match` is a MISCOMPILE, not an optimization. This is r39's
#       MISCOMPILE-1 one row over — a set derived for the SCAN role reused
#       where it does not hold — and it is the reason this section exists.
#   §3  `<prefix>_match_caps` writes the dead groups itself. Under
#       `"search-filter"` those come from `emit_search_head`, which fills
#       slots 1..NCAPS-1 with PCREC_UNSET at entry to `<prefix>_search`; the
#       unwrapped form never calls that function, so the fill has to be in
#       `_match_caps` or a DFA artifact with `RX_NCAPS > 1` returns whatever
#       the caller's array held.
#   §4  the OVERFLOW ARM IS LIVE, in TWO ways since the r41 close. §4a pins
#       the shipped ceiling `PCREC_ANCHORED_MAX_STATES` (4,096) from BOTH
#       sides with cheap 4,001- and 4,201-state machines, from which
#       `tests/resource`'s four 20,001-30,001-state shapes — the arm's real
#       population, and one no `.rxt` corpus or size-log row contains —
#       follow arithmetically. §4b keeps the lowered-cap reference compiler as
#       the control that the arm behaves the same way at a cap no real shape
#       reaches. Before r41's S1 the arm had ZERO reachable population; that
#       is what the ceiling changed.
#   §5  the corpus census, with every population PINNED. The vacuity this
#       row is most exposed to is the form silently ceasing to be selected:
#       every answer in the tree would stay right, `make test-axes` would stay
#       green (its claim is that the denied and default builds AGREE, and with
#       nothing to deny they are the same build), and the row's measured gain
#       would simply be gone. Only a COUNT catches that.
#
# =========================================================================
# THE CONTROL DOES NOT SHARE A SOURCE WITH WHAT IT CONTROLS
# =========================================================================
# docs/dev/learnings.md §3. Every verdict below is derived from the EMITTED
# MATCHER TEXT — the anchored tables, the scan loop, the entry bodies — and
# compared against the stamp. The two come out of different write sites in the
# emitter (`emit_dfa_stamps` writes the macro, `emit_anchored_entries` writes
# the body), so a stamp that drifts from the mechanism it names is a RED here.
#
# The DISCRIMINATOR for "this artifact carries the anchored machine" is the
# emitted table `<prefix>_anchored_next_state[` — matcher text — never the
# stamp. Reading the stamp to decide which artifacts to check the stamp on is
# the circularity `run_dfa_stamps.sh`'s own note refuses.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-cc}"
KEEP="${KEEP:-0}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # [K37] pcrec_run / gen_cc / gen_run

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "anchored-match: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

[ -x "$PCREC" ] || { echo "FAIL: anchored-match: no compiler at $PCREC — run \`make\` first" >&2; exit 1; }

# THE DOCUMENTED VALUE SET, spelled here so this file states the contract it
# checks rather than accepting whatever the emitter says
# (docs/spec/match_api.md §6.3). A new value needs a spec hunk and a line here,
# in the same change.
MATCH_VALUES="unwrapped search-filter"

emit() { # emit <outfile> <pattern> [extra pcrec args...]
    local out="$1" pat="$2"
    shift 2
    pcrec_run "$PCREC" -p rx --no-captures --features all "$@" \
        -o "$out" -- "$pat" >/dev/null 2>&1
}

stamp()  { grep -m1 '^#define RX_DFA_MATCH "' "$1" | cut -d'"' -f2; }
mirror() { grep -m1 '^    \.match_form = ' "$1" \
             | sed 's/^    \.match_form = //; s/,$//; s/^"//; s/"$//'; }
# THE MECHANISM, from matcher text alone.
has_anchored_tbl() { grep -q "rx_anchored_next_state\[" "$1"; }
# The `<prefix>_match` body, from its signature to the closing brace at
# column 0 — the region every §2/§3 claim is read out of.
match_body()      { sed -n '/^ptrdiff_t rx_match(const rx_ctx \*ctx)$/,/^}$/p' "$1"; }
match_caps_body() { sed -n '/^ptrdiff_t rx_match_caps(const rx_ctx \*ctx, /,/^}$/p' "$1"; }

# =========================================================================
# §1 THE NAMED WITNESSES — one pattern per documented value
# =========================================================================
# Expectations are LITERALS from docs/design/anchored_match_unwrapped.md §5.1
# and docs/spec/match_api.md §3.2, never read back out of the artifact. Every
# row also asserts the MECHANISM, so a witness cannot pass by stamping a value
# whose machinery is absent.
witness() { # witness <label> <pattern> <expected value> <expect table: y|n> [args...]
    local lbl="$1" pat="$2" want="$3" tbl="$4"; shift 4
    local f="$WORKDIR/w.c"
    emit "$f" "$pat" "$@" || { bad "§1 [$lbl] '$pat' did not compile"; return; }
    local got; got="$(stamp "$f")"
    case " $MATCH_VALUES " in *" $got "*) ;; *)
        bad "§1 [$lbl] '$pat' stamps RX_DFA_MATCH \"$got\", which is not one of the documented values ($MATCH_VALUES) — spec §6.3 and this file must move together"
        return ;;
    esac
    [ "$got" = "$want" ] || bad "§1 [$lbl] '$pat' stamps \"$got\", expected \"$want\""
    local m; m="$(mirror "$f")"
    [ "$m" = "$got" ] || bad "§1 [$lbl] the rx_info mirror reads '$m' where the macro reads '$got' — one derivation written twice, so a disagreement is an emitter defect (spec §6.3)"
    if [ "$tbl" = y ]; then
        has_anchored_tbl "$f" \
            || bad "§1 [$lbl] stamps \"unwrapped\" but emits NO rx_anchored_next_state table — the stamp and the mechanism have come apart"
    else
        has_anchored_tbl "$f" \
            && bad "§1 [$lbl] stamps \"$got\" but emits an rx_anchored_next_state table — a machine no entry runs, paid for on every artifact"
    fi
}

witness "plain literal-led"  'foo[0-9]+bar'   unwrapped     y
witness "class-led"          '[a-z]+@[a-z]+'  unwrapped     y
witness "word boundary"      '\bfoo\b'        unwrapped     y
witness "end-anchored"       'foo\z'          unwrapped     y
witness "eol view"           'foo$'           unwrapped     y
witness "attempt engine"     '^foo'           search-filter n
witness "attempt via \\G"    '\Gfoo'          search-filter n
witness "empty engine"       '\B\b'           search-filter n
witness "deny flag"          'foo[0-9]+bar'   search-filter n -fno-anchored-dfa
[ "$fail" -eq 0 ] && ok "§1 nine named witnesses stamp the documented value, mirror it in rx_info, and carry (or do not carry) the anchored table accordingly"

# THE NEGATIVE CONTROL FOR THE WHOLE FILE. Without it every §1 row above would
# pass just as well on a compiler in which `unwrapped` is never selected —
# `search-filter` is a legitimate value and four of the nine rows expect it.
# The deny-flag row and this one differ in exactly one flag, so a build in
# which the form is dead makes them EQUAL and this goes red.
emit "$WORKDIR/on.c"  'foo[0-9]+bar'
emit "$WORKDIR/off.c" 'foo[0-9]+bar' -fno-anchored-dfa
if cmp -s "$WORKDIR/on.c" "$WORKDIR/off.c"; then
    bad "§1 the default and -fno-anchored-dfa artifacts for 'foo[0-9]+bar' are IDENTICAL — the axis has nothing to deny, so every row in this file is comparing a build against itself (docs/dev/learnings.md §3)"
else
    ok "§1 the axis has a live difference to deny (default vs -fno-anchored-dfa artifacts differ)"
fi

# =========================================================================
# §2 THE ANCHORED BODY IS PREFILTER-FREE
# =========================================================================
# The claim, from the note's §3.7: a candidate-start skip is sound for a SEARCH
# (a skipped position is one no match can begin at) and WRONG for a match-here,
# where the start is given. `<prefix>_search` may and does carry one; the
# anchored body must not. Read from the BODY REGION, so a `memchr` in the
# search 200 lines above cannot make this pass or fail.
#
# The three markers are the three prefilter mechanisms the emitter has:
# `memchr(subject + scan_position` (the memchr arms), `rx_can_begin_match[`
# (the bitmap arms) and `rx_ofsskip(` ([OPT-K]'s offset-set arms).
pf_scan() { # pf_scan <label> <pattern>
    local lbl="$1" pat="$2" f="$WORKDIR/p.c" body
    emit "$f" "$pat" || { bad "§2 [$lbl] '$pat' did not compile"; return; }
    has_anchored_tbl "$f" || { bad "§2 [$lbl] '$pat' has no anchored machine to check — pick a witness that selects the form"; return; }
    body="$(match_body "$f")"
    [ -n "$body" ] || { bad "§2 [$lbl] could not extract the rx_match body — the entry's signature moved and this section is now vacuous"; return; }
    printf '%s\n' "$body" | grep -q 'memchr(subject + scan_position' \
        && bad "§2 [$lbl] '$pat' emits a memchr candidate-start skip INSIDE rx_match — the skip chooses where the scan begins, and under a match-here the start is the caller's (docs/design/anchored_match_unwrapped.md §3.7)"
    printf '%s\n' "$body" | grep -q 'rx_can_begin_match\[' \
        && bad "§2 [$lbl] '$pat' emits the can_begin_match bitmap walk INSIDE rx_match — same defect, bitmap arm"
    printf '%s\n' "$body" | grep -q 'rx_ofsskip(' \
        && bad "§2 [$lbl] '$pat' calls the [OPT-K] offset-k skip INSIDE rx_match — same defect, offset-set arm"
    # ...and the POSITIVE half: the search this artifact carries DOES have one,
    # so the absence above is a property of the anchored body and not of a
    # compiler that emits no prefilters at all.
    sed -n '/^int rx_search(const unsigned char \*subject/,/^}$/p' "$f" \
        | grep -qE 'memchr\(subject \+ scan_position|rx_can_begin_match\[|rx_ofsskip\(' \
        || bad "§2 [$lbl] '$pat' has NO prefilter in rx_search either — this witness cannot tell 'the anchored body declines one' from 'this compiler emits none', so the negative above is vacuous"
}
pf_scan "memchr arm"    'foo[0-9]+bar'
pf_scan "bitmap arm"    '[fgh]oo[0-9]+bar'
pf_scan "offset-k arm"  '\d{4}-\d{2}-\d{2}'
[ "$fail" -eq 0 ] && ok "§2 the anchored body carries none of the three candidate-start mechanisms, on artifacts whose search carries each of them"

# The same claim ONE LEVEL DOWN: the anchored machine must not even have a
# stay-skip out of a state the SEARCH excludes for the prefilter's sake. This
# is the [ENG-ABS] bug the differential sweep found — the stay tables are named
# per machine, and a body referring to another machine's table does not even
# compile. Asserting it here makes the next direction's version of that
# mistake a named red rather than a build error in someone's harness.
badname=0
for pat in 'foo[0-9]+bar' '\bfoo\b' 'a.*=.*b' '[01]*1[01]{8}'; do
    emit "$WORKDIR/n.c" "$pat" || continue
    has_anchored_tbl "$WORKDIR/n.c" || continue
    if match_body "$WORKDIR/n.c" | grep -qE 'rx_(forward|reverse)_(next_state|is_accepting|byte_class|stay|eol_view|end_view|seed_state)'; then
        bad "§2 '$pat' — rx_match's body references a rx_forward_*/rx_reverse_* table; those are declared inside rx_search and this body is a different function (the [ENG-ABS] hardcoded-name defect)"
        badname=1
    fi
done
[ "$badname" -eq 0 ] && ok "§2 no anchored body references a forward/reverse table name"

# =========================================================================
# §3 `_match_caps` DELIVERS THE SPAN AND THE DEAD GROUPS
# =========================================================================
# `caps_out[0] == [ctx->pos, ctx->pos + length)` is spec §3.3's sentence, and
# under this form it is written rather than filtered. `RX_NCAPS > 1` on a DFA
# artifact means every group above 0 is PERMANENTLY unset (wave G's
# dead-capture elision) and the fill used to come from `emit_search_head`,
# which this form never calls.
f="$WORKDIR/c.c"
if emit "$f" 'foo[0-9]+bar'; then
    b="$(match_caps_body "$f")"
    [ -n "$b" ] || bad "§3 could not extract the rx_match_caps body"
    printf '%s\n' "$b" | grep -q 'capture_spans_out\[0\]\[0\] = (ptrdiff_t)ctx->pos;' \
        || bad "§3 rx_match_caps does not write caps_out[0][0] = ctx->pos — spec §3.3's own sentence"
    printf '%s\n' "$b" | grep -q 'capture_spans_out\[0\]\[1\] = (ptrdiff_t)ctx->pos + rx_len;' \
        || bad "§3 rx_match_caps does not write caps_out[0][1] = ctx->pos + length"
    printf '%s\n' "$b" | grep -q 'capture_spans_out\[rx_g\]\[0\] = PCREC_UNSET;' \
        || bad "§3 rx_match_caps does not fill the dead groups with PCREC_UNSET — under this form nothing else does, and a DFA artifact with RX_NCAPS > 1 would return the caller's own array contents (wave G)"
    # UNTOUCHED ON FAILURE (A-8): every write is below the early return.
    printf '%s\n' "$b" | grep -q 'if (rx_len < 0) return rx_len;' \
        || bad "§3 rx_match_caps does not return before writing on a negative result — 'caps_out is untouched on every negative return, give-up included' (spec §3.3)"
    [ "$fail" -eq 0 ] && ok "§3 rx_match_caps writes the span from ctx->pos, fills the dead groups, and returns before any write on failure"
else
    bad "§3 the witness pattern did not compile"
fi

# A DFA ARTIFACT THAT ACTUALLY HAS DEAD GROUPS, so the loop above is checked on
# the population it exists for rather than only where RX_NCAPS is 1.
# `-o -` RATHER THAN `-o FILE`, and it is not a style choice: `RX_NCAPS` is a
# HEADER macro, so on a split output it lands in the `.h` and every grep below
# would read an empty string and report "?" — which is exactly what the first
# draft of this row did, passing its own guard for the wrong reason.
f="$WORKDIR/g.c"
if pcrec_run "$PCREC" -p rx --features all -o - \
        -- '(?(DEFINE)(?<g>a))(?&g)b' > "$f" 2>/dev/null \
   && [ "$(stamp "$f")" = unwrapped ]; then
    ncaps="$(grep -m1 '^#define RX_NCAPS ' "$f" | awk '{print $3}')"
    if [ "${ncaps:-1}" -gt 1 ]; then
        match_caps_body "$f" | grep -q 'PCREC_UNSET' \
            && ok "§3 the dead-group fill is present on a DFA artifact that really has dead groups (RX_NCAPS=$ncaps)" \
            || bad "§3 a DFA artifact with RX_NCAPS=$ncaps emits NO PCREC_UNSET fill in rx_match_caps — this is the population the fill exists for"
    else
        bad "§3 the dead-capture witness compiled with RX_NCAPS=${ncaps:-?} — it no longer exercises wave G's population, so the row above is only tested where the loop is empty"
    fi
else
    bad "§3 the dead-capture witness '(?(DEFINE)(?<g>a))(?&g)b' did not compile as an unwrapped DFA artifact — the population §3's loop exists for is untested"
fi

# =========================================================================
# §4a THE CEILING'S BOUNDARY, PINNED FROM BOTH SIDES
# =========================================================================
# `PCREC_ANCHORED_MAX_STATES` is 4,096 — the optional machine's OWN ceiling,
# derived at the r41 close from the corpus (largest anchored machine 2,001
# states, `a{1,2000}`) and sitting in the empty interval (2,001, 20,001)
# below `tests/resource`'s 20,001-30,001-state giant-repeat shapes.
#
# **THE PIN IS THE BOUNDARY, NOT THE CONSEQUENCE, and that is a deliberate
# change from this section's first form.** The obvious check names the four
# resource shapes and asserts each takes the fallback — but those are the
# tree's most expensive compiles (11-25 s of pcrec CPU each, which is WHY the
# ceiling exists), and putting four of them inside `make test` under
# `pcrec_run`'s 60 s WALL is exactly [TT-10]'s load-sensitivity: measured, one
# of them timed out under two concurrent invocations and the section reported
# a REFUSAL that had not happened. `a{1,4000}` and `a{1,4200}` bracket 4,096
# to within 5 %, cost under a second each, and pin the ceiling's VALUE — from
# which every one of those four shapes' membership follows arithmetically,
# since 20,001 > 4,201. A check that pins the number is stronger than one that
# pins four expensive consequences of it, and it cannot be flaky.
#
# THE FOUR SHAPES ARE STILL THE POPULATION, and they are named here because
# nothing else in the tree counts them: they live in
# `tests/resource/run_resource_tests.sh`'s bash array, no `.rxt` block holds
# them, and `SIZELOG` writes no row for them — which is exactly how r41's S1
# (+46 % compiler CPU) and S2 (an artifact over the size pin) escaped every
# instrument here. `[a-z]{0,30000}`, `a{0,25000}`, `a{0,20000}`,
# `(a|b){0,30000}`: 30,001 / 25,001 / 20,001 / 30,001 anchored states, all
# above the upper bracket below. The design note's §7.2 carries their measured
# CPU and size both ways.
#
# BOTH SIDES ASSERT `RX_DFA_SCAN "unanchored"`, which is the non-vacuity: a
# witness that fell to the attempt or empty engine would reach `search-filter`
# for a DIFFERENT reason and would say nothing about the ceiling.
ceil_case() {   # ceil_case <pattern> <expected form> <expect table: y|n>
    local pat="$1" want="$2" tbl="$3" f="$WORKDIR/ceil.c"
    if ! emit "$f" "$pat"; then
        bad "§4a '$pat' did NOT COMPILE — a machine over its ceiling is a selection outcome, never a refusal"
        return 1
    fi
    local gs sc; gs="$(stamp "$f")"; sc="$(grep -m1 '^#define RX_DFA_SCAN "' "$f" | cut -d'"' -f2)"
    [ "$sc" = unanchored ] \
        || { bad "§4a '$pat' has RX_DFA_SCAN \"$sc\", not \"unanchored\" — it is not on the engine this ceiling governs, so it says nothing about the boundary"; return 1; }
    [ "$gs" = "$want" ] \
        || { bad "§4a '$pat' stamps RX_DFA_MATCH \"$gs\", expected \"$want\". Its anchored machine straddles PCREC_ANCHORED_MAX_STATES (4,096) on the '$want' side; if the ceiling moved, re-derive it from the corpus maximum rather than re-pinning this line"; return 1; }
    if [ "$tbl" = y ]; then
        has_anchored_tbl "$f" || { bad "§4a '$pat' stamps unwrapped with no anchored table"; return 1; }
    else
        has_anchored_tbl "$f" && { bad "§4a '$pat' took the fallback but still emitted an anchored table"; return 1; }
    fi
    return 0
}
ceil_ok=0
# 4,001 anchored states — UNDER the ceiling, keeps the form.
ceil_case 'a{1,4000}'     unwrapped     y && ceil_ok=$((ceil_ok + 1))
ceil_case '[a-c]{1,4000}' unwrapped     y && ceil_ok=$((ceil_ok + 1))
# 4,201 anchored states — OVER it, takes the stamped fallback.
ceil_case 'a{1,4200}'     search-filter n && ceil_ok=$((ceil_ok + 1))
ceil_case '[a-c]{1,4200}' search-filter n && ceil_ok=$((ceil_ok + 1))
[ "$ceil_ok" -eq 4 ] \
    && ok "§4a the ceiling is bracketed from BOTH sides on the ordinary build: 4,001-state machines keep the unwrapped form, 4,201-state machines take the stamped search-filter fallback with no diagnostic and no anchored table. tests/resource's four shapes (20,001-30,001 states) are above the upper bracket and are the arm's real population" \
    || bad "§4a only $ceil_ok of the 4 boundary cases held — the ceiling has moved outside (4,001, 4,201) or the fallback stopped being a selection outcome. Before the ceiling existed the overflow arm's population was ZERO and the arm was dead code"

# =========================================================================
# §4b THE SAME ARM AT A CAP NO REAL SHAPE REACHES
# =========================================================================
# §4a's four witnesses are heavy (20-30 s of compile each is why the ceiling
# exists at all), so the arm is ALSO driven on small fast patterns through a
# reference compiler with the ceiling lowered to 6 — which additionally proves
# the arm is a property of the CEILING rather than of those four shapes.
#
# WHAT THIS PROVES, and what it deliberately does not. It proves that when the
# optional build reports an overflow the compile CONTINUES, the selection sees
# it, the stamp says so, no diagnostic is produced and the ANSWERS are
# unchanged — with the fallen-back artifact byte-compared against the
# `-fno-anchored-dfa` build's, which is that form by construction.
REF="$WORKDIR/pcrec_capped"
REF_SRCS="$(find "$ROOT_DIR/src" -name '*.c' | LC_ALL=C sort)"
if [ -z "$REF_SRCS" ]; then
    bad "§4b found no compiler sources under $ROOT_DIR/src for the reference build"
elif ! $CC -O0 -std=gnu11 -Wall -Wextra -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
        -DPCREC_ANCHORED_MAX_STATES=6 \
        -o "$REF" "$ROOT_DIR"/cli/main.c $REF_SRCS 2>"$WORKDIR/refbuild.log"; then
    bad "§4b could not build the -DPCREC_ANCHORED_MAX_STATES=6 reference compiler: $(head -3 "$WORKDIR/refbuild.log")"
else
    [ -s "$WORKDIR/refbuild.log" ] && bad "§4b the reference build produced warnings: $(head -3 "$WORKDIR/refbuild.log")"
    ovf=0; kept=0; diags=0; answers_moved=0
    # Patterns whose anchored machine needs MORE than 6 states, and one that
    # needs fewer — the second is the control that says the lowered cap did not
    # simply switch the form off for everything.
    for pat in 'foobarbazqux' 'abcdefghij[0-9]+' 'a[bc]d[ef]g[hi]j[kl]m' 'ab'; do
        pcrec_run "$REF" -p rx --no-captures --features all -o "$WORKDIR/r.c" \
            -- "$pat" > "$WORKDIR/r.err" 2>&1 || { bad "§4b the capped compiler REFUSED '$pat' — an optional machine over a cap must be a selection outcome, never a diagnostic: $(head -2 "$WORKDIR/r.err")"; continue; }
        [ -s "$WORKDIR/r.err" ] && { bad "§4b the capped compiler printed a diagnostic on '$pat': $(head -2 "$WORKDIR/r.err")"; diags=$((diags + 1)); }
        emit "$WORKDIR/d.c" "$pat" || { bad "§4b the shipped compiler did not compile '$pat'"; continue; }
        rs="$(stamp "$WORKDIR/r.c")"; ds="$(stamp "$WORKDIR/d.c")"
        if [ "$rs" = search-filter ] && [ "$ds" = unwrapped ]; then
            ovf=$((ovf + 1))
            has_anchored_tbl "$WORKDIR/r.c" && bad "§4b '$pat' fell back to search-filter but still emitted an anchored table"
            # The fallen-back artifact must be the search-and-filter artifact,
            # not a third thing: compare it against the DENIED build, which is
            # that form by construction.
            # THE `#include "<basename>.h"` LINE IS THE OUTPUT FILE'S NAME,
            # not a property of the form, so it is normalised away — comparing
            # it would make this row fail on a filename. Everything else must
            # match to the byte.
            emit "$WORKDIR/o.c" "$pat" -fno-anchored-dfa
            sed 's/^#include "[^"]*\.h"$/#include "ART.h"/' "$WORKDIR/r.c" > "$WORKDIR/r.norm"
            sed 's/^#include "[^"]*\.h"$/#include "ART.h"/' "$WORKDIR/o.c" > "$WORKDIR/o.norm"
            cmp -s "$WORKDIR/r.norm" "$WORKDIR/o.norm" \
                || { bad "§4b '$pat' over the cap produced an artifact that differs from the -fno-anchored-dfa build's — the fallback is not the form it claims to be: $(diff "$WORKDIR/o.norm" "$WORKDIR/r.norm" | head -4 | tr '\n' ' ')"; answers_moved=$((answers_moved + 1)); }
        elif [ "$rs" = unwrapped ]; then
            kept=$((kept + 1))
        fi
    done
    [ "$ovf" -ge 2 ] && [ "$answers_moved" -eq 0 ] \
        && ok "§4b $ovf patterns drove the overflow arm under a 6-state cap: no diagnostic, the stamp flipped to search-filter, and the artifact is the -fno-anchored-dfa build's to the byte (modulo the output filename)" \
        || bad "§4b the overflow arm's rows did not all hold: $ovf patterns reached it under a 6-state cap (expected at least 2) and $answers_moved produced the wrong fallback artifact — either the arm is unreachable or the witnesses' machines shrank; the arm's real population is already zero (§5), so this is the only place it is exercised at all"
    [ "$kept" -ge 1 ] \
        && ok "§4b the control held: at least one pattern still selects unwrapped under the lowered cap, so the cap narrows rather than disables" \
        || bad "§4b NO pattern selects unwrapped under the 6-state cap — the reference build has the form switched off wholesale, so the rows above compare a dead axis"
fi

# =========================================================================
# §5 THE CORPUS CENSUS, WITH EVERY POPULATION PINNED
# =========================================================================
# The population is every `pattern` line in every .rxt under tests/, so it
# grows with the corpus rather than with this script. `LC_ALL=C` on the
# `sort -u` is [K35]'s: under the ambient collation punctuation is ignorable
# and structured patterns are silently dropped.
#
# THE PINS ARE FLOORS AND A CEILING, not equalities, because the corpus grows.
# What each one catches:
#   - unwrapped FLOOR: the form silently stopping being selected. Nothing else
#     in the tree would notice — every answer stays right and the axis sweep
#     stays green, because with nothing to deny the two builds are one build.
#   - attempt/empty FLOORS: the two fallback populations that DO exist losing
#     their witnesses, i.e. the fallback going untested from the other side.
#   - overflow CEILING at 0: the arm's population is zero TODAY and §4 is what
#     tests it. If a pattern ever lands here the ceiling fires and the right
#     answer is to move the pin and give §4 a real witness — a red that says
#     "your assumption expired", which is the only honest kind.
grep -rhE '^pattern ' "$ROOT_DIR/tests" 2>/dev/null | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$WORKDIR/pats"
npat="$(wc -l < "$WORKDIR/pats")"
if [ "$npat" -lt 2640 ]; then
    bad "anchored-match: corpus extraction found only $npat patterns, below the 2640 floor (~95% of the 2786 this tree measures 2026-08-29). Either the corpus shrank (re-pin, deliberately) or the extraction is dropping patterns again (K35)"
else
    NSHARD="${PROCS:-$(nproc)}"
    [ "$NSHARD" -ge 1 ] 2>/dev/null || NSHARD=1
    mkdir -p "$WORKDIR/sh"
    split -n "l/$NSHARD" -d "$WORKDIR/pats" "$WORKDIR/sh/p" 2>/dev/null \
        || { cp "$WORKDIR/pats" "$WORKDIR/sh/p00"; NSHARD=1; }
    # The shards are LINE CHUNKS of one pattern file, not an `xargs` over
    # pattern text: a pattern is arbitrary bytes and every quoting scheme for
    # passing it as an argument is a bug waiting to be found by the corpus.
    cat > "$WORKDIR/worker.sh" <<'WORKER'
set -u
. "$ROOT_DIR/tests/lib/gen_timeout.sh" >/dev/null 2>&1
command -v pcrec_run >/dev/null || { echo "BAD: worker could not load pcrec_run"; exit 1; }
art="$WORKDIR/w.$$.c"
trap 'rm -f "$art"' EXIT
while IFS= read -r pat; do
    pcrec_run "$PCREC" --features all -p rx -o - -- "$pat" > "$art" 2>/dev/null \
        || { echo REFUSED; continue; }
    # THE ARTIFACT KIND FROM MATCHER TEXT, never from RX_ENGINE: `goto rx_L0;`
    # is the VM program's entry (run_dfa_stamps.sh's own discriminator).
    if grep -q '^    goto rx_L0;$' "$art"; then
        # a VM artifact, hybrid or not, must mirror NULL and stamp nothing
        grep -q '^#define RX_DFA_MATCH ' "$art" && { echo IFFBAD; echo "BAD: a VM artifact stamps RX_DFA_MATCH: $pat"; }
        grep -q '^    \.match_form = NULL,$' "$art" || { echo IFFBAD; echo "BAD: a VM artifact does not mirror .match_form = NULL: $pat"; }
        echo VM; continue
    fi
    mf="$(grep -m1 '^#define RX_DFA_MATCH "' "$art" | cut -d'"' -f2)"
    sc="$(grep -m1 '^#define RX_DFA_SCAN "' "$art" | cut -d'"' -f2)"
    [ -n "$mf" ] || { echo IFFBAD; echo "BAD: a DFA artifact stamps no RX_DFA_MATCH: $pat"; }
    # THE MECHANISM AND THE STAMP, on every artifact of the corpus.
    if grep -q 'rx_anchored_next_state\[' "$art"; then
        [ "$mf" = unwrapped ] || { echo MISMATCH; echo "BAD: carries an anchored table but stamps \"$mf\": $pat"; }
    else
        [ "$mf" = search-filter ] || { echo MISMATCH; echo "BAD: stamps \"$mf\" with no anchored table: $pat"; }
    fi
    echo "DFA $mf $sc"
done
WORKER
    export ROOT_DIR WORKDIR PCREC
    for f in "$WORKDIR"/sh/p*; do
        [ -e "$f" ] || continue
        bash "$WORKDIR/worker.sh" < "$f" > "$f.out" 2>&1 &
    done
    wait
    cat "$WORKDIR"/sh/*.out > "$WORKDIR/all.out"
    cnt() { grep -cxF "$1" "$WORKDIR/all.out" || true; }
    n_unwrapped="$(cnt 'DFA unwrapped unanchored')"
    n_attempt="$(cnt 'DFA search-filter attempt')"
    n_empty="$(cnt 'DFA search-filter empty')"
    n_ovf="$(cnt 'DFA search-filter unanchored')"
    n_vm="$(cnt 'VM')"; n_ref="$(cnt 'REFUSED')"
    n_mis="$(grep -c '^MISMATCH$' "$WORKDIR/all.out" || true)"
    n_iff="$(grep -c '^IFFBAD$' "$WORKDIR/all.out" || true)"
    echo "population: $npat corpus patterns — $n_vm vm, $n_ref refused, unwrapped $n_unwrapped, search-filter(attempt) $n_attempt, search-filter(empty) $n_empty, search-filter(overflow) $n_ovf"
    [ "$n_mis" -eq 0 ] && ok "§5 stamp and mechanism agree on all $((n_unwrapped + n_attempt + n_empty + n_ovf)) DFA artifacts" \
        || { bad "§5 $n_mis DFA artifacts stamp a value their emitted body contradicts"; grep -m5 '^BAD: ' "$WORKDIR/all.out" >&2; }
    [ "$n_iff" -eq 0 ] && ok "§5 the iff holds over the corpus: RX_DFA_MATCH on exactly the DFA artifacts, .match_form NULL on every VM artifact (hybrids included)" \
        || { bad "§5 $n_iff artifacts break the RX_DFA_MATCH iff (spec §6.3)"; grep -m5 '^BAD: ' "$WORKDIR/all.out" >&2; }
    [ "$n_unwrapped" -ge 780 ] && ok "§5 the unwrapped population is $n_unwrapped (floor 780; 825 measured 2026-08-29)" \
        || bad "§5 only $n_unwrapped corpus artifacts select the unwrapped form, below the 780 floor (825 measured 2026-08-29). Every answer in the tree can stay right while this number falls to zero — that is what this pin is for"
    [ "$n_attempt" -ge 170 ] && ok "§5 the attempt-engine fallback population is $n_attempt (floor 170; 180 measured 2026-08-29)" \
        || bad "§5 the attempt-engine fallback population is $n_attempt, below the 170 floor — the fallback's largest witness set is disappearing"
    [ "$n_empty" -ge 4 ] && ok "§5 the empty-engine fallback population is $n_empty (floor 4, measured 2026-08-29)" \
        || bad "§5 the empty-engine fallback population is $n_empty, below the floor of 4 — \`\\B\\b\` and its siblings are in the corpus and must land here"
    # THE CORPUS's OVERFLOW POPULATION IS STILL 0 AND THAT IS THE POINT OF THE
    # CEILING'S VALUE. 4,096 sits above the corpus's largest anchored machine
    # (2,001 states, `a{1,2000}`) by 2.05x, so NO `.rxt` artifact loses the
    # form to it — the ceiling's population is §4a's four out-of-corpus shapes
    # and nothing else. A nonzero count here means a corpus pattern grew past
    # 4,096 states: re-derive the ceiling against the new maximum rather than
    # re-pinning this line.
    [ "$n_ovf" -eq 0 ] && ok "§5 the corpus's overflow fallback population is 0 — the 4,096 ceiling is above the corpus's largest anchored machine (2,001 states) by 2.05x, so no .rxt artifact loses the form to it; §4a's four NAMED out-of-corpus shapes are the arm's real population" \
        || bad "§5 $n_ovf corpus artifacts now reach the OVERFLOW fallback, where the pin says 0 (measured 2026-08-29 against a corpus maximum of 2,001 anchored states). A corpus pattern has grown past the 4,096 ceiling: re-derive the ceiling from the new maximum, do not simply re-pin this line"
fi

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
exit 0

# =========================================================================
# SABOTAGE TRANSCRIPTS — what each plant does to this file
# =========================================================================
# Recorded at landing, 2026-08-29, on this tree. A check with no measured
# failing direction is the defect this project keeps recording.
#
#   PLANT 1 -- THE ACCEPT DISCIPLINE INVERTED (`emit_scan_loop`'s recorded
#     position becomes the FIRST accept rather than the LAST, on the anchored
#     direction only). This file: GREEN — every structural claim still holds,
#     which is the point of `tests/mech`'s S189 existing beside it. The corpus
#     harness and `make test-axes` are what go red. Recorded here so nobody
#     reads §1-§5 as covering the accept rule.
#
#   PLANT 2 -- THE SELECTION NEVER FIRES (`match_unwrapped_applies` returns
#     false). MEASURED: this file 6 / 8 — §1's five unwrapped witnesses, §1's
#     negative control, §2's three sections and §5's unwrapped floor — while
#     the corpus stays GREEN and `make test-axes` stays green, because with
#     nothing to deny the two builds are one build. That green everywhere else
#     is the whole reason §5's floor is a pin and not a comment.
#
#   PLANT 3 -- THE ANCHORED BODY KEEPS THE PREFILTER (`anch_start` no longer
#     zeroes `kind`/`ofsk`). MEASURED: this file 2 red in §2 (memchr and
#     offset-k arms) — and the corpus goes red too, on false NO-MATCHES, which
#     is the failure direction that matters: a skip past `ctx->pos` reports no
#     match at a position where one begins.
#
#   PLANT 4 -- THE DEAD-GROUP FILL DELETED from `emit_anchored_match_caps_def`.
#     MEASURED: this file 2 red in §3. No `.rxt` row moves: the corpus driver
#     does not read capture slots above 0 on a DFA artifact, which is exactly
#     the gap §3's second witness exists to cover.
