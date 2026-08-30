#!/usr/bin/env bash
# tests/codegen/run_prefilter_collapse.sh — [OPT-4] the COUNT-COLLAPSED
# PREFILTER, held to the artifact rather than to its stamp (K39;
# docs/design/prefilter_count_independence.md, docs/spec/tuning.md §2.17).
#
# =========================================================================
# WHAT IS BEING DEFENDED
# =========================================================================
# The VM hybrid's inlined prefilter used to scale with a bounded repeat's
# COUNT: `((a)|b){0,4000}c` emitted 199,511 code bytes against 45,303 for
# `{0,400}`, while the VM body itself is count-independent at ~22,200 either
# way. Above `PCREC_PREFILTER_EXACT_NFA_STATES` the prefilter is now built
# from the count-collapsed lowering — every `A_REP` with `rmin > 1 || rmax > 1`
# as `X{min(rmin,1),}` — a superset whose proof never mentions the count.
#
# =========================================================================
# WHY THIS SCRIPT EXISTS, AND WHAT NO OTHER CHECK IN THE TREE SEES
# =========================================================================
# THE AXIS IS ANSWER-IDENTITY-PRESERVING (D46), which is exactly why it needs
# structural checks: the whole `.rxt` corpus, both oracles, `make test-axes`
# and every differential agree whether or not the emitter got any of this
# right. Six failure modes, none of which an answer comparison can reach:
#
#   (i)   THE COLLAPSE STOPS FIRING. The artifact is correct and K39 is back —
#         a size regression no answer check and no byte-identity gate that
#         compares an artifact against ITSELF can see. §1 asserts the
#         count-independence directly, on the two patterns K39 was filed on.
#   (ii)  THE STAMP DRIFTS FROM THE MACHINE. `RX_VM_PREFILTER_LANG` is written
#         by `emit_vm.c` off `job->fit.prefilter_collapsed`; the machine is
#         built by `compile.c`'s knee. §2 compares the stamp against BYTES —
#         `"exact"` iff the artifact is byte-identical to the same pattern
#         compiled with `-fno-prefilter-collapse` — which is a fact about the
#         emitted file and shares no write site with the stamp.
#   (iii) THE MRL CEILING SURVIVES A SUPERSET PREFILTER. This one is a SILENT
#         MATCH LOSS rather than a size regression: a collapsed prefilter's
#         span END is not an upper bound (match_api.md §6.3 H3), so the clamp
#         would prune real matches. It is the atomic/lookaround hazard through
#         a third door, and §3 asserts the consequence on every collapsed
#         artifact in the corpus. The two-sources defect R31 E3 found in this
#         same expression is why the assertion is on the ARTIFACT's ceiling
#         stamp and not on the predicate.
#   (iv)  THE COLLAPSE REACHES THE DFA ENGINE. There a superset IS a
#         miscompile, and the corpus WOULD catch it — but only by a wrong
#         answer somewhere, which is a bad way to learn it. §4 asserts no DFA
#         artifact carries the macro at all, in both directions.
#   (v)   THE POPULATION MOVES (K35), in EITHER direction. A knee that stopped
#         separating, or a predicate that stopped matching the builder, reads
#         as "0 collapsed, cleaner!" rather than as the mechanism not
#         happening; a knee that started collapsing everything — a budget of 0,
#         a flipped comparison — reads as "more optimisation!" rather than as
#         the sharper filter being thrown away corpus-wide. §5 PRINTS the
#         census and BANDS it on both sides, and separately asserts the
#         property the budget was chosen for (that it fires only where a COUNT
#         made the machine big) against a replication factor re-derived from
#         the pattern TEXT, which shares no source with
#         `pcrec_has_collapsible_rep`.
#   (vi)  THE REASON DRIFTS FROM THE OUTCOME. `RX_VM_PREFILTER_LANG_WHY`'s
#         five values partition into `_LANG`'s two, and `internal.h` makes
#         that structural rather than agreed — but only in the source. §2 and
#         §5 assert the partition on the ARTIFACT, and §1 holds the WHY's
#         measured NFA count to the pattern text (a tenfold bound must move it
#         tenfold), which is what catches the number being read off the
#         COLLAPSED machine instead of the exact one — a bug that leaves every
#         other check in this file green.
#
# =========================================================================
# THE CONTROLS DO NOT SHARE A SOURCE WITH WHAT THEY CONTROL
# =========================================================================
# docs/dev/learnings.md §3. The obvious wrong version of this check reads
# `RX_VM_PREFILTER_LANG` and checks it is one of two strings: that asserts the
# emitter can print. So every verdict below is derived from something else —
# emitted BYTES against a denied-axis build (§1, §2), a DIFFERENT stamp
# written by a different expression (§3), the presence of the macro at all
# against the engine stamp (§4), and the PATTERN TEXT, parsed here and not by
# the compiler, for both the replication factor §5 bands on and the count
# ratio §1 holds the WHY stamp to — and the stamp is compared against that.
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
# [K37] every compiler invocation is BOUNDED. Not a formality here: §1
# compiles `((a)|b){0,4000}c` under `-fno-prefilter-collapse`, which is the
# 4,002-state machine this row exists to stop building by default.
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export LC_ALL=C     # K35: `sort -u` over regexes drops `a{0,0}b` vs `(a){0,0}b`
                    # under a UTF-8 locale. Guarded per site per CLAUDE.md.

pass=0; fail=0
ok()  { printf 'PASS: %s\n' "$1"; pass=$((pass+1)); }
bad() { printf 'FAIL: %s\n' "$1"; fail=$((fail+1)); }
stamp() { grep -oE "^#define RX_$1 .*" "$2" 2>/dev/null | head -1 | sed "s/^#define RX_$1 //" | tr -d '"'; }

# `-o -` writes a self-contained artifact to stdout, so every comparison below
# is over ONE file and no `.h` sidecar can differ unnoticed.
emit() {  # emit OUTFILE FLAGS... -- PATTERN
    local out="$1"; shift
    pcrec_run "$PCREC" --features all -p rx -o - "$@" > "$out" 2>"$out.err"
}

# ---------------------------------------------------------------------------
# §1 COUNT-INDEPENDENCE (the FORCE flag) and COUNT-BOUNDEDNESS (the default)
# ---------------------------------------------------------------------------
# FRANK'S RULING B (2026-08-29) SPLIT THIS SECTION IN TWO, and the split IS the
# ruling. K39 was filed on `((a)|b){0,4000}c` emitting 1,994 lines against 869
# for `{0,400}`. Two different things can answer it and only one is the
# default now:
#
#   COUNT-INDEPENDENT — the emitted size does not move with the count at all.
#   Reachable only under `-fprefilter-collapse`, which collapses wherever a
#   collapsible repeat exists. Asserted below on K39's own two patterns, with
#   its failing-direction control.
#
#   COUNT-BOUNDED — the size may move with the count, but the emitted-size CAPS
#   bound it: a pattern whose EXACT artifact the caps refuse is compiled via
#   the size rung rather than refused. That is what a user gets by default, and
#   it is a weaker claim than the row above on purpose (docs/design/
#   prefilter_count_independence.md §10; the knee was removed on a measured
#   regression, `(a{1,3}){65}` going from 0.00 s to a 13.34 s step-budget
#   exhaustion).
#
# ASSERTING ONLY THE FIRST WOULD BE A CLAIM ABOUT A FLAG NOBODY PASSES;
# asserting only the second would let the force flag rot.
c_small="$WORK/f_small.c"; c_big="$WORK/f_big.c"
if emit "$c_small" -fprefilter-collapse -- '((a)|b){0,400}c' \
   && emit "$c_big" -fprefilter-collapse -- '((a)|b){0,4000}c'; then
    n_small=$(wc -l < "$c_small"); n_big=$(wc -l < "$c_big")
    d=$(( n_big > n_small ? n_big - n_small : n_small - n_big ))
    if [ "$d" -le 2 ]; then
        ok "[K39/force] -fprefilter-collapse is COUNT-INDEPENDENT: '((a)|b){0,400}c' $n_small lines, '((a)|b){0,4000}c' $n_big (delta $d <= 2)"
    else
        bad "[K39/force] under -fprefilter-collapse '((a)|b){0,4000}c' emitted $n_big lines against $n_small for {0,400} (delta $d > 2) — the forced collapse is scaling with the count"
    fi
    # THE MEASURED NUMBER IN `_LANG_WHY` cannot be checked here any more: the
    # forced route stamps `"forced"` and names no count, by design (there is no
    # budget left to compare against). The exact machine's size is still the
    # thing that would drift, and §6's `dfa overflow retry, exact nfa N` row is
    # where it is now held to a pattern.
    e_small="$WORK/d_small.c"; e_big="$WORK/d_big.c"
    if emit "$e_small" -- '((a)|b){0,400}c' && emit "$e_big" -- '((a)|b){0,4000}c'; then
        m_small=$(wc -l < "$e_small"); m_big=$(wc -l < "$e_big")
        if [ "$m_big" -gt "$((m_small * 2))" ]; then
            ok "[K39/force] the control holds: at the DEFAULT the same pair is $m_small vs $m_big lines, so §1's equality is the forced collapse and not an artefact"
        else
            bad "[K39/force] CONTROL VACUOUS: at the default '{0,400}' is $m_small lines and '{0,4000}' is $m_big — the exact prefilter is no longer count-proportional, so the row above proves nothing"
        fi
    else
        bad "[K39/force] the default-build control did not compile — §1 has no control"
    fi
else
    bad "[K39/force] '((a)|b){0,400}c' or '((a)|b){0,4000}c' does not compile under -fprefilter-collapse"
fi

# THE DEFAULT'S OWN CLAIM: count-BOUNDED. A pattern whose EXACT artifact the
# caps refuse must COMPILE, through the size rung, and say so. K41's witness 2
# is that pattern and the reason this row exists (known_issues.md K41).
K41W2='(?:(0{28,30}|[\n\t]?(?:c{1}?c{28,30}?a|1{1,}a{0,30}0|c){5,10}?\n){0,3}?b[\x6]|[^abc]b(0{2,}[\]]|(b{0,30}a??|a{0,3}?\n)[-a]|^))a?|a(\n{1,2}b{1,2}|0)??a{0,30}$'
w2="$WORK/k41w2.c"
if emit "$w2" -- "$K41W2"; then
    w2why=$(stamp VM_PREFILTER_LANG_WHY "$w2")
    case "$w2why" in
      "size cap retry, exact "*" > "*)
        ok "[K39/default] count-BOUNDED: an artifact the caps refuse under the exact language compiles via the size rung ('$w2why')" ;;
      *)
        bad "[K39/default] K41 witness 2 compiled but stamps LANG_WHY '$w2why', expected the size-cap retry — either the rung did not fire or something else made it small" ;;
    esac
    # AND THE CONTROL, which is also the only thing -fno-prefilter-collapse
    # still buys a caller under ruling B: denying the rungs restores the
    # refusal.
    if emit "$WORK/k41w2_deny.c" -fno-prefilter-collapse -- "$K41W2"; then
        bad "[K39/default] CONTROL VACUOUS: K41 witness 2 compiles under -fno-prefilter-collapse too, so the row above is not measuring the size rung"
    elif grep -q 'bytes of emitted code' "$WORK/k41w2_deny.c.err"; then
        ok "[K39/default] the control holds: -fno-prefilter-collapse restores the cap's refusal ($(head -1 "$WORK/k41w2_deny.c.err" | cut -c1-64)...)"
    else
        bad "[K39/default] under -fno-prefilter-collapse K41 witness 2 was refused, but not by a size cap: $(head -1 "$WORK/k41w2_deny.c.err")"
    fi
else
    bad "[K39/default] K41 witness 2 does not compile at the default — ruling B's size rung is not rescuing it: $(head -1 "$w2.err")"
fi

# ---------------------------------------------------------------------------
# §2 THE STAMP AGAINST BYTES — `"exact"` IFF the deny flag changes nothing
# ---------------------------------------------------------------------------
# The stamp claims which language was built. The independent term is the
# artifact compiled with the axis DENIED: if the stamp says `"exact"`, the
# compiler is claiming the collapse did not act, and an artifact where it did
# not act is byte-for-byte the artifact you get when it cannot. The two facts
# are written by different code (`emit_vm.c`'s `sb_printf` against
# `compile.c`'s build gate), so a stamp that drifts is RED here.
#
# Each row is a pattern chosen to land on a named side of the knee.
lang_witness() {  # lang_witness EXPECTED PATTERN
    local want="$1" pat="$2" a="$WORK/w_force.c" b="$WORK/w_def.c"
    # [OPT-4] RULING B PIVOTED THIS SECTION ONTO THE FORCE FLAG. It used to
    # compare the DEFAULT against `-fno-prefilter-collapse`, because the
    # default was where the collapse happened. It is not any more: the default
    # is the exact language, so the deny flag is a no-op on almost everything
    # and the comparison would have been vacuous on every row. The independent
    # axis is now `-fprefilter-collapse` against the default, which asks the
    # same question — does the STAMP agree with the BYTES — through the flag
    # that actually moves them.
    if ! emit "$a" -fprefilter-collapse -- "$pat"; then
        bad "[lang] '$pat' does not compile under -fprefilter-collapse — this row has no subject"; return
    fi
    local vmpf; vmpf=$(stamp VM_PREFILTER "$a")
    if [ "$vmpf" != "hybrid" ]; then
        bad "[lang] '$pat' is not a hybrid (RX_VM_PREFILTER '$vmpf') — this row has stopped testing what it names"; return
    fi
    local got; got=$(stamp VM_PREFILTER_LANG "$a")
    if [ "$got" != "$want" ]; then
        bad "[lang] '$pat' under -fprefilter-collapse stamps RX_VM_PREFILTER_LANG '$got', expected '$want'"; return
    fi
    if ! emit "$b" -- "$pat"; then
        bad "[lang] '$pat' does not compile at the default — the row has no independent term"; return
    fi
    # THE REASON, and the two outcomes have DIFFERENT ones under ruling B: a
    # forced collapse says `forced`, a forced NON-collapse says why it could
    # not (`no counted repeat`). Both are checked, because "the flag was
    # honoured" and "the flag had something to act on" are two facts.
    local why dwhy
    why=$(stamp VM_PREFILTER_LANG_WHY "$a")
    dwhy=$(stamp VM_PREFILTER_LANG_WHY "$b")
    if [ "$want" = count-collapsed ]; then
        [ "$why" = forced ] \
            && ok "[why] '$pat' under -fprefilter-collapse stamps 'forced' — the flag is the reason, and the artifact says so" \
            || bad "[why] '$pat' collapsed under -fprefilter-collapse but stamps LANG_WHY '$why', expected 'forced'"
        [ "$dwhy" = exact ] \
            && ok "[why] ...and at the DEFAULT the same pattern stamps 'exact' — ruling B's default is the pattern's own language" \
            || bad "[why] '$pat' at the DEFAULT stamps LANG_WHY '$dwhy', expected 'exact' — something other than the force flag is collapsing it"
    else
        [ "$why" = "no counted repeat" ] \
            && ok "[why] '$pat' is HONOURED but vacuous under -fprefilter-collapse ('no counted repeat')" \
            || bad "[why] '$pat' stamps LANG_WHY '$why' under -fprefilter-collapse, expected 'no counted repeat' — the flag reached a conjunct that is vacuity, not policy"
    fi
    # H3, ON THE ARTIFACT THAT ACTUALLY COLLAPSED. This was a corpus-wide
    # sweep until ruling B emptied its population (nothing collapses at the
    # default any more), so it moved here, where every `count-collapsed` row
    # supplies a real subject at no extra compile. The claim is unchanged and
    # it is the SILENT MATCH LOSS one: a superset prefilter's span END is not
    # a bound on the match end (match_api.md §6.3 H3), so a collapsed artifact
    # must not carry the `prefilter-window` clamp. The two stamps come out of
    # different expressions — `v.mrl_win`'s conjuncts against
    # `job->fit.prefilter_collapsed` — so this is a cross-check, not a
    # restatement. ONE-DIRECTIONAL by construction: an EXACT artifact may also
    # lack the ceiling (an atomic group or a lookaround drops it), so only the
    # collapsed => no-ceiling implication is asserted.
    if [ "$want" = count-collapsed ]; then
        local ceil; ceil=$(stamp VM_PRUNE_CEILING "$a")
        [ "$ceil" != "prefilter-window" ] \
            && ok "[H3] '$pat' collapsed and dropped the prefilter-window ceiling (reads '$ceil')" \
            || bad "[H3] '$pat' is count-collapsed and STILL carries RX_VM_PRUNE_CEILING \"prefilter-window\" — the clamp prunes real matches on a superset prefilter"
    fi
    # THE STAMP AGAINST BYTES. A forced build that collapsed must DIFFER from
    # the default; one that could not collapse must be byte-IDENTICAL to it —
    # a flag with nothing to act on moves no byte, which is the same promise
    # `-fno-prefilter-collapse` carries from the other side.
    if cmp -s "$a" "$b"; then
        if [ "$want" = exact ]; then
            ok "[lang] '$pat' stamps \"exact\" under -fprefilter-collapse and is byte-identical to its default build — the stamp agrees with the artifact"
        else
            bad "[lang] '$pat' stamps \"count-collapsed\" but is byte-identical to its default build — the stamp names a collapse that did not happen"
        fi
    else
        local na nb; na=$(wc -c < "$a"); nb=$(wc -c < "$b")
        if [ "$want" = count-collapsed ]; then
            ok "[lang] '$pat' stamps \"count-collapsed\" and differs from its default build ($na vs $nb bytes) — the stamp agrees with the artifact"
        else
            bad "[lang] '$pat' stamps \"exact\" but differs from its default build ($na vs $nb bytes) — the flag acted on an artifact that says it did not"
        fi
    fi
}
# NOTHING TO COLLAPSE: the flag is honoured and vacuous. This is the row that
# fails if `-fprefilter-collapse` ever starts reaching the has-collapsible
# conjunct, which would be vacuity dressed as policy.
lang_witness exact           'a(b|c)+d'
# WITH something to collapse, four shapes that carry the count in DIFFERENT
# machines — `{0,4000}` in the reverse one only (the `Sigma*` wrap absorbs the
# bound forward), the literal-prefixed form in BOTH, the exact-count form in
# both, and a small one (`{0,3}`) that the OLD knee would have left alone. That
# last row is ruling B's own: the force flag has no budget conjunct to drop any
# more, so it must collapse a counted repeat of ANY size.
lang_witness count-collapsed '((a)|b){0,3}c'
lang_witness count-collapsed '((a)|b){0,4000}c'
lang_witness count-collapsed 'foo((a)|b){0,1000}bar'
lang_witness count-collapsed '((a)|ab){4000}c'
# A LAZY bound and a NESTED one: the same `A_REP` arm, which is the whole
# claim that this covers the family rather than one spelling.
lang_witness count-collapsed '((a)|b){0,4000}?c'
lang_witness count-collapsed '((a{10,20}){10,50})z'

# THE CONFLICT PAIR is REFUSED, by name (tuning.md §2.17). The two
# force/vacuity rows that used to sit here are now `lang_witness`'s own — under
# ruling B every `count-collapsed` row IS a force row, so keeping separate ones
# would have been the same assertion written twice.
f="$WORK/force.c"
if emit "$f" -fprefilter-collapse -fno-prefilter-collapse -- 'a(b|c)+d'; then
    bad "[force] -fprefilter-collapse and -fno-prefilter-collapse together were ACCEPTED — a request with two contradictory halves must be refused, never silently resolved"
elif grep -q 'cannot both be requested' "$f.err"; then
    ok "[force] -fprefilter-collapse with -fno-prefilter-collapse is refused by name"
else
    bad "[force] the conflicting pair was refused, but not with the documented diagnostic: $(head -1 "$f.err")"
fi

# ---------------------------------------------------------------------------
# §3 THE MRL CEILING, on every collapsed artifact — the SILENT MATCH LOSS row
# ---------------------------------------------------------------------------
# A superset prefilter's span END is not an upper bound (match_api.md §6.3,
# H3; the recorded witness of the shape is `(?>a|ab)c|abcd` on "abcd"), so an
# artifact built from the collapsed language must NOT carry the
# `"prefilter-window"` clamp. The two stamps come out of different
# expressions — `v.mrl_win`'s three conjuncts against
# `job->fit.prefilter_collapsed` alone — so this is a real cross-check and not
# a restatement.
#
# ONE-DIRECTIONAL BY CONSTRUCTION, and the note says so rather than
# over-claiming: an EXACT prefilter may also lack the ceiling (an atomic group
# or a lookaround drops it through the other two conjuncts), so only the
# collapsed => no-ceiling implication is asserted.
#
# §4 and §5 share this sweep's compile pass; the corpus is every `pattern`
# line under tests/, which is the population `run_dfa_stamps.sh` uses.
PATS="$WORK/pats.txt"
grep -rhE '^pattern ' "$ROOT_DIR/tests" --include='*.rxt' 2>/dev/null \
    | sed 's/^pattern //' | sort -u > "$PATS"
npat=$(wc -l < "$PATS")


if [ "$npat" -lt 1000 ]; then
    bad "[sweep] the corpus extraction found only $npat patterns — the sweep below would be vacuous"
else
    n_hybrid=0; n_coll=0; n_exact=0; n_dfa_macro=0; n_novm_macro=0
    n_ceiling_bad=0; n_lang_missing=0; bad_ex=""; coll_ex=""
    # §5's census terms, all keyed on the TEXTUAL factor (see the scanner
    # above), never on the compiler's own has-collapsible predicate.
    n_why_bad=0; n_rung=0
    why_ex=""
    # [OPT-4] `<PREFIX>_ENGINE_SEL`'s accounting (§7). Counted over EVERY
    # artifact, not just the hybrids, because the stamp is unconditional.
    n_art=0; n_sel_bad=0; n_sel_forced=0; n_sel_cross=0; sel_ex=""
    art="$WORK/sweep.c"
    while IFS= read -r p; do
        emit "$art" -- "$p" || continue
        eng=$(stamp ENGINE "$art")
        vmpf=$(stamp VM_PREFILTER "$art")
        lang=$(stamp VM_PREFILTER_LANG "$art")
        # ---- §7 ENGINE_SEL, read BEFORE the engine/hybrid `continue`s below,
        # because this stamp is on every artifact and those skip most of them.
        n_art=$((n_art+1))
        sel=$(stamp ENGINE_SEL "$art")
        case "$sel" in
          selected|forced|overflowed-dfa|overflowed-prefilter|collapsed-prefilter) ;;
          *) n_sel_bad=$((n_sel_bad+1)); [ -z "$sel_ex" ] && sel_ex="$p (SEL '$sel')" ;;
        esac
        [ "$sel" = forced ] && { n_sel_forced=$((n_sel_forced+1)); [ -z "$sel_ex" ] && sel_ex="$p (forced at the default)"; }
        # The cross-checks, each against a DIFFERENT macro than the one under
        # test: a route that says a prefilter survived must have one, and a
        # route that says one was dropped must not.
        case "$sel" in
          collapsed-prefilter)
            { [ "$vmpf" = hybrid ] && [ "$lang" = count-collapsed ]; } || {
                n_sel_cross=$((n_sel_cross+1)); [ -z "$sel_ex" ] && sel_ex="$p (SEL collapsed-prefilter but PREFILTER '$vmpf' / LANG '$lang')"; } ;;
          overflowed-dfa|overflowed-prefilter)
            [ "$vmpf" = none ] || {
                n_sel_cross=$((n_sel_cross+1)); [ -z "$sel_ex" ] && sel_ex="$p (SEL '$sel' but PREFILTER '$vmpf')"; } ;;
        esac
        if [ "$eng" = dfa ]; then
            [ -n "$lang" ] && { n_dfa_macro=$((n_dfa_macro+1)); [ -z "$bad_ex" ] && bad_ex="$p"; }
            continue
        fi
        if [ "$vmpf" != hybrid ]; then
            [ -n "$lang" ] && { n_novm_macro=$((n_novm_macro+1)); [ -z "$bad_ex" ] && bad_ex="$p"; }
            continue
        fi
        n_hybrid=$((n_hybrid+1))
        # THE `_WHY` COMPANION, over the whole population rather than over §2's
        # seven witnesses: the five reasons partition into the two outcomes,
        # and `internal.h` makes that structural (`>= PFLW_FORCED` iff
        # collapsed). Asserted here on the ARTIFACT, where a regression that
        # broke the structure would show.
        why=$(stamp VM_PREFILTER_LANG_WHY "$art")
        # `denied` is not among the accepted values here and that is deliberate:
        # this sweep compiles at the DEFAULT, where the deny flag is not passed,
        # so an artifact reporting it would mean the reason had come from
        # somewhere other than the build.
        # [OPT-4] RULING B's value set. The two RUNG values are the only ways
        # an artifact collapses at the default, and `forced` is unreachable
        # here because this sweep passes no flag — which is itself asserted
        # below rather than assumed.
        case "$lang:$why" in
          count-collapsed:"dfa overflow retry, "*) n_rung=$((n_rung+1)) ;;
          count-collapsed:"size cap retry, "*)     n_rung=$((n_rung+1)) ;;
          exact:exact|exact:"no counted repeat")   : ;;
          *) n_why_bad=$((n_why_bad+1)); [ -z "$why_ex" ] && why_ex="$p ($lang / $why)" ;;
        esac
        case "$lang" in
            count-collapsed)
                n_coll=$((n_coll+1))
                [ -z "$coll_ex" ] && coll_ex="$p ($why)"
                if [ "$(stamp VM_PRUNE_CEILING "$art")" = "prefilter-window" ]; then
                    n_ceiling_bad=$((n_ceiling_bad+1))
                    [ -z "$bad_ex" ] && bad_ex="$p"
                fi ;;
            exact) n_exact=$((n_exact+1)) ;;
            *)     n_lang_missing=$((n_lang_missing+1)); [ -z "$bad_ex" ] && bad_ex="$p" ;;
        esac
    done < "$PATS"

    # [OPT-4] RULING B, ASSERTED CORPUS-WIDE, and this is what §3 measures now.
    # The old assertion here swept for collapsed artifacts and checked their
    # ceilings; its population is legitimately ZERO under ruling B, so it moved
    # onto the forced witnesses in §2 (where a subject exists) and this loop
    # asserts the ruling itself instead: at the DEFAULT, over the whole corpus,
    # NOTHING collapses. If a knee ever returns — by design or by accident —
    # this is the line that says so, and it is a far stronger statement than
    # the vacuous ceiling sweep it replaces.
    #
    # The two rungs are invisible here by construction: no corpus pattern
    # overflows a DFA state cap or is refused by an emitted-size cap at the
    # default, which is exactly why they need named witnesses (§1, §6) rather
    # than a population.
    # THE ASSERTION IS "ONLY A RUNG", NOT "NEVER". A corpus pattern MAY reach
    # a rung at the default — that is what the rungs are for — so the check
    # that catches a returning knee is that every collapsed artifact names a
    # RUNG as its reason. `n_coll - n_rung` is the number that collapsed for
    # some other reason, and it is what a knee would grow.
    if [ "$((n_coll - n_rung))" -eq 0 ]; then
        ok "[rulingB] all $n_coll collapsed artifact(s) of $n_hybrid hybrids over $npat corpus patterns collapsed via a LADDER RUNG${coll_ex:+ (e.g. $coll_ex)} — the collapse is never a measurement of the pattern"
    else
        bad "[rulingB] $((n_coll - n_rung)) of $n_hybrid hybrid artifact(s) collapsed at the DEFAULT for a reason that is not a ladder rung (first: '$coll_ex') — under Frank's ruling B only a failed attempt may collapse; a knee has come back"
    fi
    if [ "$n_ceiling_bad" -ne 0 ]; then
        bad "[H3] $n_ceiling_bad count-collapsed artifact(s) still carry RX_VM_PRUNE_CEILING \"prefilter-window\" — the clamp prunes real matches on a superset prefilter (first: '$bad_ex')"
    fi

    # ----------------------------------------------------------------------
    # §4 THE IFF: the macro is on every hybrid and on NOTHING else
    # ----------------------------------------------------------------------
    # Narrower than the `_DFA_*` family's iff (match_api.md §6.3): a plain DFA
    # artifact CONTAINS a DFA scan and still takes no VM prefilter decision,
    # so it must carry no language macro. The DFA half is also the (iv)
    # failure mode's detector — the collapse reaching the engine's own machine
    # would show up as a DFA artifact with a language to report.
    if [ "$n_dfa_macro" -eq 0 ] && [ "$n_novm_macro" -eq 0 ]; then
        ok "[iff] RX_VM_PREFILTER_LANG appears on no DFA artifact and no non-hybrid VM artifact over $npat corpus patterns"
    else
        bad "[iff] RX_VM_PREFILTER_LANG on $n_dfa_macro DFA artifact(s) and $n_novm_macro non-hybrid VM artifact(s) — the macro names a decision those artifacts do not take (first: '$bad_ex')"
    fi
    if [ "$n_lang_missing" -eq 0 ]; then
        ok "[iff] every one of the $n_hybrid hybrid artifact(s) carries RX_VM_PREFILTER_LANG with a documented value"
    else
        bad "[iff] $n_lang_missing hybrid artifact(s) carry no RX_VM_PREFILTER_LANG, or an undocumented value (first: '$bad_ex')"
    fi

    # ----------------------------------------------------------------------
    # §5 IS RETIRED (Frank's ruling B, 2026-08-29). Its quantity no longer
    # exists.
    # ----------------------------------------------------------------------
    # This section was a form census over the knee's population: it printed how
    # many corpus artifacts sat above `PCREC_PREFILTER_EXACT_NFA_STATES`,
    # banded that count, and asserted that none of them had a replication
    # factor below 2. Under ruling B there is no knee and no such population —
    # the collapse acts only on the two ladder rungs, whose corpus population
    # is legitimately ZERO — so every one of those assertions would now be
    # measuring nothing.
    #
    # DELETED RATHER THAN LEFT WITH A BAND OF `0..0`, which is the manager's
    # instruction and the right one: a check whose subject has gone is a
    # VACUOUS check, and a vacuous check is worse than no check because it
    # reads like coverage. The replication-factor scanner it used went with it.
    # What the rungs do is asserted where the rungs are — §1's size-cap row,
    # §6's [SEL-1] row — on named witnesses rather than on a population.
    #
    # The bar sweep this section pinned (the 117..160 plateau) is kept in
    # docs/design/prefilter_count_independence.md §4 as the RECORD OF A
    # DECISION THAT WAS REVERSED, not as a live claim; §10 carries the ruling
    # chain that reversed it.
    if [ "$n_why_bad" -eq 0 ]; then
        ok "[why] all $n_hybrid hybrid artifact(s) carry a RX_VM_PREFILTER_LANG_WHY whose reason belongs to the language it stamps"
    else
        bad "[why] $n_why_bad hybrid artifact(s) stamp a LANG_WHY reason that does not belong to their LANG (first: '$why_ex') — the two lines disagree about one decision"
    fi
    # ----------------------------------------------------------------------
    # §7 `RX_ENGINE_SEL`: the value set is CLOSED, and it agrees with the
    #    stamps that would contradict it
    # ----------------------------------------------------------------------
    if [ "$n_sel_bad" -eq 0 ]; then
        ok "[sel] all $n_art artifact(s) carry RX_ENGINE_SEL with one of the five documented values — the set is closed and the stamp is unconditional (D81)"
    else
        bad "[sel] $n_sel_bad artifact(s) carry no RX_ENGINE_SEL or an undocumented value (first: '$sel_ex') — a closed value set a consumer buckets on cannot grow a sixth value silently"
    fi
    # `forced` is the one value the COMMAND LINE decides, and this sweep never
    # passes --engine=, so its population here must be zero. That is a real
    # cross-check and not a formality: it is what fails if the route were ever
    # derived from something other than the caller's own request.
    if [ "$n_sel_forced" -eq 0 ]; then
        ok "[sel] no artifact stamps \"forced\" over $n_art emits at the DEFAULT — the route reports the caller's request, and this sweep makes none"
    else
        bad "[sel] $n_sel_forced artifact(s) stamp RX_ENGINE_SEL \"forced\" with no --engine= on the command line (first: '$sel_ex')"
    fi
    if [ "$n_sel_cross" -eq 0 ]; then
        ok "[sel] every route naming a prefilter outcome agrees with RX_VM_PREFILTER and RX_VM_PREFILTER_LANG — different macros, different write sites, same verdict"
    else
        bad "[sel] $n_sel_cross artifact(s) stamp a route contradicted by their own prefilter stamps (first: '$sel_ex') — the route names an outcome the artifact does not show"
    fi
fi

# ---------------------------------------------------------------------------
# §6 THE [SEL-1] RUNG — a prefilter where there was none
# ---------------------------------------------------------------------------
# [OPT-4]'s second commit. Under `auto`, a pattern whose DFA overflows a cap AS
# THE ENGINE used to fall to a VM artifact with `RX_VM_PREFILTER "none"`, on
# the stated ground that rebuilding the prefilter would be the IDENTICAL
# machine that just overflowed. That is true of the exact language and false of
# the count-collapsed one, so `compile_driver`'s retry gains a middle rung.
#
# WHY THIS IS ITS OWN SECTION AND NOT A ROW IN §2. Every other cell in this
# file compares two languages for ONE artifact. This one is about an artifact
# that did not previously EXIST — the question is not "which language" but
# "a prefilter at all" — and its evidence is a different stamp
# (`RX_VM_PREFILTER`) plus the fact that the deny flag returns the old outcome.
#
# THE WITNESS is [SEL-1]/K40's own, the one docs/spec/tuning.md §4 pins the
# fallback's behaviour on, so this section and that spec cannot drift.
SEL1='\b(?:ERROR|FATAL|CRIT)\b.{0,200}?\b(?:timeout|timed out|refused|denied|unreachable)\b'
a="$WORK/sel1_auto.c"; b="$WORK/sel1_deny.c"
if emit "$a" -- "$SEL1" && emit "$b" -fno-prefilter-collapse -- "$SEL1"; then
    eng=$(stamp ENGINE "$a"); ewhy=$(stamp ENGINE_WHY "$a")
    pf=$(stamp VM_PREFILTER "$a"); lang=$(stamp VM_PREFILTER_LANG "$a")
    why=$(stamp VM_PREFILTER_LANG_WHY "$a")
    pf_deny=$(stamp VM_PREFILTER "$b")
    # (1) THE RUNG FIRED. The engine stamp must still report the overflow —
    # that is what says WHICH rung won, and an artifact that had simply never
    # overflowed would look identical without it.
    case "$eng:$ewhy:$pf:$lang" in
      vm:"dfa overflowed"*:hybrid:count-collapsed)
        ok "[sel1] the overflow witness keeps a prefilter: RX_ENGINE_WHY '$ewhy' beside RX_VM_PREFILTER \"hybrid\" / \"count-collapsed\" — the rung ran and the artifact says so" ;;
      vm:"dfa overflowed"*:none:*)
        bad "[sel1] the overflow witness still stamps RX_VM_PREFILTER \"none\" — the collapse retry rung did not fire, or selection dropped the prefilter before it could" ;;
      *)
        bad "[sel1] the overflow witness stamps ENGINE '$eng' / WHY '$ewhy' / PREFILTER '$pf' / LANG '$lang' — this row has stopped testing the fallback it names" ;;
    esac
    # (2) THE REASON NAMES THE RUNG, not the knee. Both collapse, and a reader
    # of "dfa overflowed" beside a hybrid needs to know which one explains it.
    case "$why" in
      "dfa overflow retry, "*)
        ok "[sel1] RX_VM_PREFILTER_LANG_WHY names the rung rather than the budget: '$why'" ;;
      *)
        bad "[sel1] the overflow witness stamps LANG_WHY '$why'; the rung has its own value and the knee's must not stand in for it — a reader cannot otherwise tell an artifact that gained a prefilter from one that merely shrank" ;;
    esac
    # (3) THE DENY FLAG RETURNS THE OLD OUTCOME, which is this rung's control:
    # without it, (1) would pass on a compiler that had stopped overflowing at
    # all (a cap raised, the pattern lowered differently), and the section
    # would be asserting something no fallback produces.
    if [ "$pf_deny" = none ]; then
        ok "[sel1] -fno-prefilter-collapse returns the pre-[OPT-4] outcome (RX_VM_PREFILTER \"none\") — so (1) is the rung acting, and the DFA really does still overflow here"
    else
        bad "[sel1] under -fno-prefilter-collapse the witness stamps RX_VM_PREFILTER '$pf_deny', expected 'none' — either the deny flag no longer reaches the rung, or this pattern's DFA no longer overflows and the whole section is vacuous"
    fi
else
    bad "[sel1] the DFA-overflow witness does not compile — §6 has no subject"
fi

# ---------------------------------------------------------------------------
# §7b THE FIVE ROUTES ARE EACH REACHABLE — the K35 half of a closed value set
# ---------------------------------------------------------------------------
# §7 asserts nothing OUTSIDE the set appears. It cannot see a value that has
# quietly become unreachable, which reads as "cleaner!" and is how a bucket a
# consumer depends on silently empties. Each row below drives ONE route through
# the path that produces it, so a value that stops being reachable fails here.
sel_witness() {  # sel_witness EXPECTED FLAGS... -- PATTERN
    local want="$1"; shift
    local o="$WORK/sel.c"
    if ! emit "$o" "$@"; then
        bad "[sel] the '$want' witness does not compile — that route has no subject"; return
    fi
    local got; got=$(stamp ENGINE_SEL "$o")
    [ "$got" = "$want" ] \
        && ok "[sel] route '$want' is reachable ($(stamp ENGINE "$o")/$(stamp VM_PREFILTER "$o"))" \
        || bad "[sel] the '$want' witness stamps RX_ENGINE_SEL '$got' — that route is unreachable, or the ladder has been reordered"
}
SEL1_P='\b(?:ERROR|FATAL|CRIT)\b.{0,200}?\b(?:timeout|timed out|refused|denied|unreachable)\b'
sel_witness selected               -- 'abc'
sel_witness forced   --engine=dfa  -- 'abc'
# The DFA-overflow trio, all on witnesses whose overflow is a MEASURED property
# of this tree (tuning.md §4's own [SEL-1] witness, and k18_cost_gates.rxt's).
# `collapsed-prefilter` and `overflowed-dfa` are the SAME pattern with the axis
# allowed and denied, which is what makes the pair a control rather than two
# unrelated rows.
sel_witness collapsed-prefilter                          -- "$SEL1_P"
sel_witness overflowed-dfa       -fno-prefilter-collapse -- "$SEL1_P"
sel_witness overflowed-prefilter -fno-prefilter-collapse -- '(1{0,30}?[^]abc][^abc]){28,30}0+|a'

printf '\nprefilter-collapse: %d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
