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
    # THE MEASURED NUMBER IN `_LANG_WHY`, held to the PATTERN TEXT — the one
    # independent term available for it, and the one that catches the bug this
    # stamp invites. `prefilter_nfa_states` is meant to be the EXACT forward
    # NFA's size; if it were ever read off the machine actually BUILT, both
    # artifacts here would report a small, near-equal count, because that is
    # the whole point of the collapsed machine. The exact NFA is linear in the
    # count (§1 of the design note), so a tenfold bound in the pattern must
    # show as an ~tenfold N — asserted loosely at 9x, since the constant term
    # differs, and the direction is what matters.
    w_small=$(stamp VM_PREFILTER_LANG_WHY "$c_small")
    w_big=$(stamp VM_PREFILTER_LANG_WHY "$c_big")
    k_small=$(printf '%s' "$w_small" | sed -n 's/^exact nfa \([0-9]*\) .*/\1/p')
    k_big=$(printf '%s' "$w_big"     | sed -n 's/^exact nfa \([0-9]*\) .*/\1/p')
    if [ -z "$k_small" ] || [ -z "$k_big" ]; then
        bad "[K39] one of the pair reports no measured NFA count in RX_VM_PREFILTER_LANG_WHY ('$w_small' / '$w_big') — the stamp's number is the only evidence the knee was measured rather than guessed"
    elif [ "$k_big" -gt "$((k_small * 9))" ]; then
        ok "[K39] RX_VM_PREFILTER_LANG_WHY reports the EXACT machine's size, not the built one's: $k_small states at {0,400} against $k_big at {0,4000} (>9x, tracking the count as the exact lowering does)"
    else
        bad "[K39] RX_VM_PREFILTER_LANG_WHY reports $k_small states at {0,400} and $k_big at {0,4000} — a tenfold count moved the number by less than 9x, so it is not the exact NFA's size"
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
    # [OPT-4] THE `_WHY` COMPANION, and the independent term for its NUMBER.
    # `_LANG` says which language; `_LANG_WHY` says which conjunct decided and
    # on what measurement. The value is checked for SHAPE against the language
    # (the five reasons partition into the two outcomes), and then the number
    # is checked against a build that took the OTHER branch: the exact forward
    # NFA is built on both paths, so `-fno-prefilter-collapse` must report the
    # SAME N. That is what catches the one bug this stamp invites — reading the
    # count off the COLLAPSED machine, which would leave the default build
    # reporting a small N while the denied build reports the real one.
    local why dwhy
    why=$(stamp VM_PREFILTER_LANG_WHY "$a")
    dwhy=$(stamp VM_PREFILTER_LANG_WHY "$b")
    case "$want:$why" in
      count-collapsed:"exact nfa "*" > "*|count-collapsed:forced) ok "[why] '$pat' stamps LANG \"count-collapsed\" with a collapsing reason: '$why'" ;;
      exact:"exact nfa "*" <= "*|exact:"no counted repeat") ok "[why] '$pat' stamps LANG \"exact\" with a non-collapsing reason: '$why'" ;;
      *) bad "[why] '$pat' stamps LANG \"$want\" but LANG_WHY '$why' — the reason does not belong to the outcome, so the two lines disagree about the same decision" ;;
    esac
    # THE DENIED BUILD'S REASON, and the two halves are DIFFERENT assertions.
    # Where the collapse DID act, denying it changed the build and the artifact
    # must say so. Where it did NOT, denying it changed nothing, and the reason
    # must be UNCHANGED — that is the byte-for-byte recovery promise
    # (tuning.md §2.17) stated on the one field most likely to break it, and it
    # is not hypothetical: the first version of this stamp said "denied"
    # unconditionally and moved 13 bytes on '((a)|b){0,3}c'. The `cmp` below
    # would catch the bytes; this says WHICH field moved, which is the
    # difference between a diagnosis and a puzzle.
    if [ "$want" = count-collapsed ]; then
        case "$dwhy" in
          "denied, exact nfa "*) ok "[why] '$pat' under -fno-prefilter-collapse stamps '$dwhy' — the flag acted, and the artifact reports both that and what it cost" ;;
          *) bad "[why] '$pat' under -fno-prefilter-collapse stamps LANG_WHY '$dwhy' — the flag kept a machine that would have collapsed and the artifact does not say so" ;;
        esac
    elif [ "$dwhy" = "$why" ]; then
        ok "[why] '$pat' stamps the SAME reason ('$why') with the axis allowed and denied — a flag that cannot act moves no byte"
    else
        bad "[why] '$pat' stamps LANG_WHY '$why' by default and '$dwhy' under -fno-prefilter-collapse, on an artifact the collapse never acted on — the flag is leaking into an artifact it cannot change, which breaks the byte-for-byte recovery promise"
    fi
    # The BUDGET half of the value, against the one the compiler was built
    # with. `--list-axes` does not print it, so the independent term is the
    # OTHER artifacts' agreement: §5 asserts every artifact in the corpus
    # reports the same B, which a per-artifact constant cannot fail to do and a
    # per-artifact COMPUTATION could.
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

# ---------------------------------------------------------------------------
# THE REPLICATION FACTOR, READ OUT OF THE PATTERN TEXT — §5's independent term
# ---------------------------------------------------------------------------
# docs/dev/learnings.md §3. §5 asserts that the knee fires only where a COUNT
# made the machine big, i.e. that no artifact over the budget has replication
# factor < 2. Asking the compiler which patterns have a collapsible repeat
# would be asking the mechanism to grade itself: `pcrec_has_collapsible_rep` is
# a conjunct OF the gate under test, so a bug in it would make the assertion
# agree with the defect. So the factor is re-derived HERE, from the pattern
# string, by a scanner that shares nothing with `src/`.
#
# ONE awk PASS over the whole file rather than one per pattern: the sweep below
# already spends a compile per pattern and this must not add 2,700 processes.
# Output is one integer per line, positionally parallel to $PATS, read in the
# loop on fd 3.
#
# WHAT IT APPROXIMATES, stated rather than hidden. It tracks backslash escapes
# and character classes (including a leading `]` or `^]`, which the corpus
# does contain — `[^]abc]`), and reads `{m}` / `{m,}` / `{m,n}` as a quantifier
# only where the braces hold digits. It does NOT understand `\Q...\E`, so a
# literal brace-count inside a quoted span would be miscounted as a
# quantifier. That direction OVER-reports the factor, which could only make
# assertion (a) vacuous, so the scanner is itself pinned on named patterns
# below before it is trusted.
FACAWK="$WORK/factor.awk"
cat > "$FACAWK" <<'AWKEOF'
{
    n = length($0); best = 1; incls = 0; clsat = 0
    for (i = 1; i <= n; i++) {
        c = substr($0, i, 1)
        if (c == "\\") { i++; continue }
        if (incls) {
            # a `]` in the first position of a class (after an optional `^`)
            # is a LITERAL, not the close
            if (c == "]" && i > clsat) incls = 0
            else if (c == "^" && i == clsat) clsat = i + 1
            continue
        }
        if (c == "[") { incls = 1; clsat = i + 1; continue }
        if (c == "{") {
            rest = substr($0, i)
            if (match(rest, /^\{[0-9]+(,[0-9]*)?\}/)) {
                body = substr(rest, 2, RLENGTH - 2)
                k = index(body, ",")
                if (k == 0) { lo = body + 0; hi = lo }
                else {
                    lo = substr(body, 1, k - 1) + 0
                    hs = substr(body, k + 1)
                    hi = (hs == "") ? lo : hs + 0
                }
                if (lo > best) best = lo
                if (hi > best) best = hi
                i += RLENGTH - 1
            }
        }
    }
    print best
}
AWKEOF
FACS="$WORK/facs.txt"
awk -f "$FACAWK" "$PATS" > "$FACS"
if [ "$(wc -l < "$FACS")" != "$npat" ]; then
    bad "[census] the replication-factor scanner produced $(wc -l < "$FACS") rows for $npat patterns — §5's independent term is not aligned with its population"
fi
# THE SCANNER IS PINNED BEFORE IT IS TRUSTED, on shapes taken from the corpus
# and from the design note: a scanner that always answered ">= 2" would make
# assertion (a) pass on any defect at all.
fac_of() { printf '%s\n' "$1" | awk -f "$FACAWK"; }
fac_bad=0
for row in 'a(b|c)+d:1' '((a)|b){0,3}c:3' '((a)|ab){4000}c:4000' \
           '(ab){300}:300' '(a{10,20}){10,50}:50' '(x(?:ab){2,4}){0,12}c:12' \
           '(1{0,30}?[^]abc][^abc]){8,8}0+|a:30' 'a\{4000\}b:1' '[a{9}]z:1'; do
    fp="${row%:*}"; fw="${row##*:}"; fg=$(fac_of "$fp")
    [ "$fg" = "$fw" ] || { bad "[census] the factor scanner reads '$fp' as $fg, expected $fw"; fac_bad=$((fac_bad+1)); }
done
[ "$fac_bad" -eq 0 ] && ok "[census] the replication-factor scanner agrees with 9 hand-checked patterns, including an ESCAPED brace and one inside a class — §5's control is not vacuous"

if [ "$npat" -lt 1000 ]; then
    bad "[sweep] the corpus extraction found only $npat patterns — the sweep below would be vacuous"
else
    n_hybrid=0; n_coll=0; n_exact=0; n_dfa_macro=0; n_novm_macro=0
    n_ceiling_bad=0; n_lang_missing=0; bad_ex=""
    # §5's census terms, all keyed on the TEXTUAL factor (see the scanner
    # above), never on the compiler's own has-collapsible predicate.
    n_lowfac=0; n_hifac=0; n_coll_lowfac=0; n_why_bad=0; n_budget_bad=0
    lowfac_ex=""; why_ex=""; budget=""
    art="$WORK/sweep.c"
    exec 3< "$FACS"
    while IFS= read -r p; do
        read -r fac <&3 || fac=1
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
        if [ "$fac" -ge 2 ]; then n_hifac=$((n_hifac+1)); else n_lowfac=$((n_lowfac+1)); fi
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
        case "$lang:$why" in
          count-collapsed:"exact nfa "*" > "*|count-collapsed:forced) : ;;
          exact:"exact nfa "*" <= "*|exact:"no counted repeat") : ;;
          *) n_why_bad=$((n_why_bad+1)); [ -z "$why_ex" ] && why_ex="$p ($lang / $why)" ;;
        esac
        # The BUDGET the artifact reports, which must be ONE number across the
        # corpus — a per-artifact constant cannot vary and a per-artifact
        # computation could.
        b=$(printf '%s' "$why" | sed -n 's/^exact nfa [0-9]* [<>]*=* \([0-9]*\)$/\1/p')
        if [ -n "$b" ]; then
            if [ -z "$budget" ]; then budget="$b"
            elif [ "$b" != "$budget" ]; then
                n_budget_bad=$((n_budget_bad+1)); [ -z "$why_ex" ] && why_ex="$p (budget $b vs $budget)"
            fi
        fi
        case "$lang" in
            count-collapsed)
                n_coll=$((n_coll+1))
                if [ "$fac" -lt 2 ]; then
                    n_coll_lowfac=$((n_coll_lowfac+1))
                    [ -z "$lowfac_ex" ] && lowfac_ex="$p"
                fi
                if [ "$(stamp VM_PRUNE_CEILING "$art")" = "prefilter-window" ]; then
                    n_ceiling_bad=$((n_ceiling_bad+1))
                    [ -z "$bad_ex" ] && bad_ex="$p"
                fi ;;
            exact) n_exact=$((n_exact+1)) ;;
            *)     n_lang_missing=$((n_lang_missing+1)); [ -z "$bad_ex" ] && bad_ex="$p" ;;
        esac
    done < "$PATS"
    exec 3<&-

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
    # §5 THE FORM CENSUS: the knee's population, PRINTED and BANDED
    # ----------------------------------------------------------------------
    # docs/testing.md "Answer-identity sweep" shape. The census is PRINTED
    # unconditionally, because a number nobody prints is a number nobody
    # notices moving (K35), and then two things are asserted about it.
    #
    # (a) THE KNEE FIRES ONLY WHERE A COUNT MADE THE MACHINE BIG. This is the
    #     claim `PCREC_PREFILTER_EXACT_NFA_STATES = 128` is set on — the whole
    #     population with nothing to collapse tops out at 20 NFA states, so no
    #     budget in range can touch it — and it is the one that would fail
    #     silently if the budget were lowered, if the lowering changed, or if
    #     the exact NFA grew for an unrelated reason. The term is the TEXTUAL
    #     replication factor (scanner above), which shares nothing with
    #     `pcrec_has_collapsible_rep`.
    #
    # (b) THE POPULATION IS IN A BAND, not merely above a floor. A floor
    #     catches the knee that stopped separating; it does not catch the knee
    #     that started collapsing everything, which is the failure a
    #     mis-typed comparison or a budget of 0 produces and which reads as
    #     "more optimisation!" rather than as a defect. The band is measured
    #     on this tree and deliberately loose in both directions, because the
    #     population is a property of the CORPUS and patterns come and go.
    #
    # THE BAND IS THIS AXIS'S PIN. The bar was swept at 64/96/112/120/128/
    # 144/160/192/256/512 over the 1,388 hybrid rows of
    # docs/dev/artifact_size_log.tsv and the over-budget count is FLAT at 23
    # for every bar in 117..160 — a 44-wide plateau with 128 near its middle,
    # and zero factor-< 2 artifacts over EVERY bar in the sweep, not only over
    # this one (docs/design/prefilter_count_independence.md §4).
    #
    # WHY THE NUMBER HERE IS NOT THAT 23. This sweep's population is every
    # `pattern` line under tests/ (`sort -u`), which is not the size log's set
    # of built artifacts: the log has 23 ROWS over the budget but only 19
    # distinct patterns among them, and this sweep sees one pattern the log
    # has no row for. Measured here: 20. Two counts, two populations, both
    # right — which is exactly why each check floors its OWN and no number is
    # copied between them.
    COLLAPSE_BAND_LO=15
    COLLAPSE_BAND_HI=28
    printf 'census: %d corpus patterns -> %d hybrid artifact(s): %d count-collapsed, %d exact\n' \
           "$npat" "$n_hybrid" "$n_coll" "$n_exact"
    printf 'census: by TEXTUAL replication factor: %d with factor >= 2, %d with factor < 2\n' \
           "$n_hifac" "$n_lowfac"
    printf 'census: budget reported by the artifacts: %s\n' "${budget:-<none seen>}"

    if [ "$n_coll_lowfac" -eq 0 ]; then
        ok "[census] (a) none of the $n_coll collapsed artifact(s) has textual replication factor < 2 — the knee is firing only where a COUNT made the machine big"
    else
        bad "[census] (a) $n_coll_lowfac collapsed artifact(s) carry NO counted repeat of factor >= 2 (first: '$lowfac_ex') — the budget is catching machines that are big for some other reason, which is not what 128 was measured to separate"
    fi
    # AND (a)'s OWN CONTROL. If the scanner reported ">= 2" for everything,
    # (a) would pass on any defect whatever. It cannot: a large factor-< 2
    # hybrid population is the thing that makes the assertion say something.
    if [ "$n_lowfac" -ge 100 ]; then
        ok "[census] (a) is not vacuous: $n_lowfac of the $n_hybrid hybrid artifact(s) have textual factor < 2 and every one of them kept the exact language"
    else
        bad "[census] (a) IS VACUOUS: only $n_lowfac hybrid artifact(s) were read as factor < 2, so 'no collapsed artifact has factor < 2' is close to a tautology — check the scanner before believing (a)"
    fi
    if [ "$n_coll" -ge "$COLLAPSE_BAND_LO" ] && [ "$n_coll" -le "$COLLAPSE_BAND_HI" ]; then
        ok "[census] (b) $n_coll of $n_hybrid hybrid artifact(s) took the count-collapsed language, inside the pinned band $COLLAPSE_BAND_LO..$COLLAPSE_BAND_HI (measured 20 at the landing)"
    elif [ "$n_coll" -lt "$COLLAPSE_BAND_LO" ]; then
        bad "[census] (b) only $n_coll of $n_hybrid collapsed, below the band's floor of $COLLAPSE_BAND_LO — find out why before lowering it; a knee that stopped separating reads exactly like this"
    else
        bad "[census] (b) $n_coll of $n_hybrid collapsed, ABOVE the band's ceiling of $COLLAPSE_BAND_HI — the knee is separating far more than the 20 it was measured at, which is what a lowered or mis-compared budget looks like, and it reads like an improvement rather than like a defect"
    fi
    if [ "$n_why_bad" -eq 0 ]; then
        ok "[why] all $n_hybrid hybrid artifact(s) carry a RX_VM_PREFILTER_LANG_WHY whose reason belongs to the language it stamps"
    else
        bad "[why] $n_why_bad hybrid artifact(s) stamp a LANG_WHY reason that does not belong to their LANG (first: '$why_ex') — the two lines disagree about one decision"
    fi
    if [ "$n_budget_bad" -eq 0 ]; then
        ok "[why] every artifact reporting a budget reports the SAME one (${budget:-none}) — it is a constant, not a per-artifact computation"
    else
        bad "[why] $n_budget_bad artifact(s) report a different budget from the first one seen (first: '$why_ex')"
    fi
fi

printf '\nprefilter-collapse: %d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
