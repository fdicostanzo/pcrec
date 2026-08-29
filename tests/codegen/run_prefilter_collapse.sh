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
# right. Five failure modes, none of which an answer comparison can reach:
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
#   (v)   THE POPULATION EVAPORATES (K35). A knee that stopped separating, or
#         a predicate that stopped matching the builder, reads as "0 collapsed,
#         cleaner!" rather than as the mechanism not happening. §5 floors the
#         measured corpus population.
#
# =========================================================================
# THE CONTROLS DO NOT SHARE A SOURCE WITH WHAT THEY CONTROL
# =========================================================================
# docs/dev/learnings.md §3. The obvious wrong version of this check reads
# `RX_VM_PREFILTER_LANG` and checks it is one of two strings: that asserts the
# emitter can print. So every verdict below is derived from something else —
# emitted BYTES against a denied-axis build (§1, §2), a DIFFERENT stamp
# written by a different expression (§3), the presence of the macro at all
# against the engine stamp (§4) — and the stamp is compared against that.
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
# §1 COUNT-INDEPENDENCE, ASSERTED — K39's own two patterns
# ---------------------------------------------------------------------------
# K39 was filed with these two and the checks that carried it (tests/vm,
# run_ir_listing.sh) could only PRINT the auto sizes beside a claim about the
# prefilter-denied ones. This asserts the claim the row exists to make, and it
# asserts it on the DEFAULT artifact — the one a user gets.
#
# THE UNIT IS LINES, THE SAME 2-LINE BAR the prefilter-denied comparison
# beside it already uses, and the unit is the point rather than a convenience:
# the count appears in the VM body and in the emitted prose as a LITERAL (`400`
# against `4000`), so the two artifacts differ by those DIGITS however
# count-independent their structure is. Bytes would therefore never be equal
# and the bar would have to be a fudge factor; lines are equal exactly when the
# emitted SHAPE stops depending on the count, which is the claim.
c_small="$WORK/auto_small.c"; c_big="$WORK/auto_big.c"
if emit "$c_small" -- '((a)|b){0,400}c' && emit "$c_big" -- '((a)|b){0,4000}c'; then
    n_small=$(wc -l < "$c_small"); n_big=$(wc -l < "$c_big")
    d=$(( n_big > n_small ? n_big - n_small : n_small - n_big ))
    if [ "$d" -le 2 ]; then
        ok "[K39] the DEFAULT artifact is count-independent: '((a)|b){0,400}c' $n_small lines, '((a)|b){0,4000}c' $n_big (delta $d <= 2)"
    else
        bad "[K39] '((a)|b){0,4000}c' emitted $n_big lines against $n_small for {0,400} (delta $d > 2) — the hybrid's prefilter is scaling with the count again"
    fi
    # AND THE CONTROL, in the failing direction: under -fno-prefilter-collapse
    # the two MUST diverge. Without it §1 would pass on a compiler that had
    # stopped emitting a prefilter at all, or on one where the exact machine
    # had never been count-proportional in the first place — the check would
    # be asserting something no mechanism produces.
    e_small="$WORK/deny_small.c"; e_big="$WORK/deny_big.c"
    if emit "$e_small" -fno-prefilter-collapse -- '((a)|b){0,400}c' && \
       emit "$e_big"   -fno-prefilter-collapse -- '((a)|b){0,4000}c'; then
        m_small=$(wc -l < "$e_small"); m_big=$(wc -l < "$e_big")
        if [ "$m_big" -gt "$((m_small * 2))" ]; then
            ok "[K39] the control holds: with -fno-prefilter-collapse the same pair is $m_small vs $m_big lines, so §1's equality is the collapse and not an artefact"
        else
            bad "[K39] CONTROL VACUOUS: with -fno-prefilter-collapse '{0,400}' is $m_small lines and '{0,4000}' is $m_big — the exact prefilter is no longer count-proportional, so §1 proves nothing"
        fi
    else
        bad "[K39] the -fno-prefilter-collapse control did not compile — §1 has no control"
    fi
else
    bad "[K39] '((a)|b){0,400}c' or '((a)|b){0,4000}c' does not compile at the default"
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
    local want="$1" pat="$2" a="$WORK/w_auto.c" b="$WORK/w_deny.c"
    if ! emit "$a" -- "$pat"; then
        bad "[lang] '$pat' does not compile — this row has no subject"; return
    fi
    local vmpf; vmpf=$(stamp VM_PREFILTER "$a")
    if [ "$vmpf" != "hybrid" ]; then
        bad "[lang] '$pat' is not a hybrid (RX_VM_PREFILTER '$vmpf') — this row has stopped testing what it names"; return
    fi
    local got; got=$(stamp VM_PREFILTER_LANG "$a")
    if [ "$got" != "$want" ]; then
        bad "[lang] '$pat' stamps RX_VM_PREFILTER_LANG '$got', expected '$want'"; return
    fi
    if ! emit "$b" -fno-prefilter-collapse -- "$pat"; then
        bad "[lang] '$pat' does not compile under -fno-prefilter-collapse — the row has no independent term"; return
    fi
    # The denied build carries the SAME stamp line reading `"exact"` when the
    # collapse did not act, so on the `exact` rows the files must be identical
    # including that line; on the `count-collapsed` rows they must differ, and
    # by far more than the stamp's own 15-character value change.
    if cmp -s "$a" "$b"; then
        if [ "$want" = exact ]; then
            ok "[lang] '$pat' stamps \"exact\" and is byte-identical to its -fno-prefilter-collapse build — the stamp agrees with the artifact"
        else
            bad "[lang] '$pat' stamps \"count-collapsed\" but is byte-identical to its -fno-prefilter-collapse build — the stamp names a collapse that did not happen"
        fi
    else
        local na nb; na=$(wc -c < "$a"); nb=$(wc -c < "$b")
        if [ "$want" = count-collapsed ]; then
            ok "[lang] '$pat' stamps \"count-collapsed\" and differs from its -fno-prefilter-collapse build ($na vs $nb bytes) — the stamp agrees with the artifact"
        else
            bad "[lang] '$pat' stamps \"exact\" but differs from its -fno-prefilter-collapse build ($na vs $nb bytes) — the collapse acted on an artifact that says it did not"
        fi
    fi
}
# BELOW the knee: a counted repeat exists but its exact machine is small, so
# the sharper language is kept. This is the majority of the corpus's
# counted-repeat hybrids and the row that fails if the knee ever goes to zero.
lang_witness exact           '((a)|b){0,3}c'
# NOTHING TO COLLAPSE: no counted repeat at all. The collapsed lowering of
# this pattern IS its exact lowering, which is why the `applies` has a
# has-collapsible conjunct rather than relying on the budget alone.
lang_witness exact           'a(b|c)+d'
# ABOVE the knee, three shapes that carry the count in DIFFERENT machines —
# `{0,4000}` in the reverse one only (the `Sigma*` wrap absorbs the bound
# forward), the literal-prefixed form in BOTH, and the exact-count form in
# both. A fix confined to one direction passes the first and fails the others.
lang_witness count-collapsed '((a)|b){0,4000}c'
lang_witness count-collapsed 'foo((a)|b){0,1000}bar'
lang_witness count-collapsed '((a)|ab){4000}c'
# A LAZY bound and a NESTED one: the same `A_REP` arm, which is the whole
# claim that this covers the family rather than one spelling.
lang_witness count-collapsed '((a)|b){0,4000}?c'
lang_witness count-collapsed '((a{10,20}){10,50})z'

# THE FORCE HALF, and it is a different assertion from the deny half: it drops
# the state budget alone, so a BELOW-the-knee pattern must collapse under it
# while a pattern with nothing to collapse must still stamp `"exact"`.
f="$WORK/force.c"
if emit "$f" -fprefilter-collapse -- '((a)|b){0,3}c'; then
    got=$(stamp VM_PREFILTER_LANG "$f")
    if [ "$got" = count-collapsed ]; then
        ok "[force] -fprefilter-collapse drops the state budget: '((a)|b){0,3}c' collapses where the default keeps it exact"
    else
        bad "[force] -fprefilter-collapse left '((a)|b){0,3}c' at '$got' — the force half reaches no conjunct"
    fi
else
    bad "[force] '((a)|b){0,3}c' does not compile under -fprefilter-collapse"
fi
if emit "$f" -fprefilter-collapse -- 'a(b|c)+d'; then
    got=$(stamp VM_PREFILTER_LANG "$f")
    if [ "$got" = exact ]; then
        ok "[force] -fprefilter-collapse on a pattern with no counted repeat is HONOURED and stamps \"exact\" — the artifact reports what was built, not what was asked"
    else
        bad "[force] 'a(b|c)+d' stamps '$got' under -fprefilter-collapse — the force flag reached the has-collapsible conjunct, which is vacuity and not policy"
    fi
else
    bad "[force] 'a(b|c)+d' does not compile under -fprefilter-collapse"
fi
# The conflict pair is REFUSED, by name (tuning.md §2.17).
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
    n_ceiling_bad=0; n_lang_missing=0; bad_ex=""
    art="$WORK/sweep.c"
    while IFS= read -r p; do
        emit "$art" -- "$p" || continue
        eng=$(stamp ENGINE "$art")
        vmpf=$(stamp VM_PREFILTER "$art")
        lang=$(stamp VM_PREFILTER_LANG "$art")
        if [ "$eng" = dfa ]; then
            [ -n "$lang" ] && { n_dfa_macro=$((n_dfa_macro+1)); [ -z "$bad_ex" ] && bad_ex="$p"; }
            continue
        fi
        if [ "$vmpf" != hybrid ]; then
            [ -n "$lang" ] && { n_novm_macro=$((n_novm_macro+1)); [ -z "$bad_ex" ] && bad_ex="$p"; }
            continue
        fi
        n_hybrid=$((n_hybrid+1))
        case "$lang" in
            count-collapsed)
                n_coll=$((n_coll+1))
                if [ "$(stamp VM_PRUNE_CEILING "$art")" = "prefilter-window" ]; then
                    n_ceiling_bad=$((n_ceiling_bad+1))
                    [ -z "$bad_ex" ] && bad_ex="$p"
                fi ;;
            exact) n_exact=$((n_exact+1)) ;;
            *)     n_lang_missing=$((n_lang_missing+1)); [ -z "$bad_ex" ] && bad_ex="$p" ;;
        esac
    done < "$PATS"

    if [ "$n_ceiling_bad" -eq 0 ]; then
        ok "[H3] all $n_coll count-collapsed artifact(s) dropped the prefilter-window ceiling — a superset's span END is not a bound on the match end"
    else
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
    # §5 THE K35 FLOOR: the mechanism is still REACHING a population
    # ----------------------------------------------------------------------
    # MEASURED on this tree at the landing (docs/design/
    # prefilter_count_independence.md §4): 23 of the corpus's hybrid artifacts
    # are over `PCREC_PREFILTER_EXACT_NFA_STATES`. The floor is rounded DOWN
    # generously, because the population is a property of the corpus and a
    # pattern may legitimately be added or removed — what it must never do is
    # go to zero, which is what "the knee stopped separating" reads as.
    COLLAPSE_FLOOR=15
    if [ "$n_coll" -ge "$COLLAPSE_FLOOR" ]; then
        ok "[K35] $n_coll of $n_hybrid hybrid artifact(s) took the count-collapsed language (floor $COLLAPSE_FLOOR); $n_exact kept the exact one"
    else
        bad "[K35] only $n_coll of $n_hybrid hybrid artifact(s) collapsed, below the floor of $COLLAPSE_FLOOR — find out why before lowering it; a knee that stopped separating reads exactly like this"
    fi
fi

printf '\nprefilter-collapse: %d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
