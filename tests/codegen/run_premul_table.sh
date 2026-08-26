#!/usr/bin/env bash
# tests/codegen/run_premul_table.sh — [OPT-3]: the PRE-MULTIPLIED DFA
# TRANSITION TABLE, held to the artifact rather than to its stamp.
#
# =========================================================================
# WHAT IS BEING DEFENDED
# =========================================================================
# `docs/design/premultiplied_dfa_table.md`. A DFA scan's transition cell holds
# `next_state * classes` rather than `next_state`, so the emitted step is
#
#     forward_state = rx_forward_next_state[forward_state + rx_forward_byte_class[subject[scan_position++]]];
#     if (forward_state == 65535) break;
#
# and the loop's carried dependency chain is `add, load` instead of
# `lea, lea, movslq, load`. [OPT-3] STEP 1 measured that chain as the WHOLE of
# the scan's per-byte cost and the transform as 1.276x on the comparative
# bench's three throughput subjects, answer-identical over 40,469 answer lines.
#
# THE FORM IS CHOSEN PER MACHINE at generation time, on that machine's own
# `states * classes` (`dfa_premul`, src/gen/emit_dfa.c), so one artifact's
# forward and reverse DFAs can differ — which is what `RX_DFA_TABLE "mixed"`
# is for. `-fno-premul-table` (docs/spec/tuning.md §2.13) denies it.
#
# =========================================================================
# WHY EACH CHECK EXISTS, AND WHAT NO OTHER CHECK IN THE TREE SEES
# =========================================================================
# THE TRANSFORM IS ANSWER-PRESERVING BY CONSTRUCTION. That is exactly why it
# needs structural checks: it changes the ENCODING of a state, not the
# machine, so the whole `.rxt` corpus, both oracles and every differential
# agree whether or not the emitter got it right in the ways that matter here.
# Three failure modes, none of which an answer comparison can reach:
#
#   (i)  THE STATE VARIABLE LEFT `int`. gcc then reinstates the `movslq` the
#        transform exists to remove. The artifact is CORRECT and the
#        optimization buys nothing — a silent performance regression, invisible
#        to every answer check and to every byte-identity gate that compares
#        the artifact against ITSELF. §4 reads the emitted declaration.
#   (ii) THE BOUND NOT SWITCHING. Above `PREMUL_MAX_ENTRIES` the artifact must
#        keep the indexed form; below it, take the premultiplied one. Both
#        directions answer identically, so only a check that reads the emitted
#        TABLE TYPE against the emitted TABLE SIZE can tell. §2 and §3.
#   (iii) A CELL THAT IS NOT PREMULTIPLIED, or a sentinel colliding with a real
#        premultiplied value. The first is a wrong answer on some input and a
#        right one on most; the second is a LOST MATCH on the large machines
#        nobody has a small reproducer for. §5 asserts the invariant directly
#        over every cell of every premultiplied table in the corpus.
#
# =========================================================================
# THE CONTROL DOES NOT SHARE A SOURCE WITH WHAT IT CONTROLS
# =========================================================================
# docs/dev/learnings.md §3. The obvious wrong version of this check reads
# `RX_DFA_TABLE` and checks it is one of four strings: that asserts the
# emitter can print. So EVERY verdict below is derived from the EMITTED
# MATCHER TEXT — the table DECLARATIONS, the table CELLS, the state variable's
# declaration and the transition line — and the stamp is compared against it.
# The two come out of different write sites (`dfa_table_name` writes the
# macro; `emit_tr_table`/`emit_acc_table`/`emit_unanchored` write the tables
# and the loop), so a stamp that drifts from the mechanism it names is RED.
#
# THE CLASS COUNT IS DERIVED INDEPENDENTLY OF THE TRANSITION TABLE. §5's whole
# invariant is "every cell is a multiple of the stride", and taking the stride
# from the transition table would make that a tautology. It is read off
# `rx_<dir>_byte_class[256]` instead — a different table, written by a
# different emitter function (`emit_u8_table`), whose largest value plus one
# IS the class count by construction.
#
# =========================================================================
# VALIDATION (the check was made to fail on purpose before it shipped)
# =========================================================================
# Recorded 2026-08-26, lane srPremul. Each plant made in src/gen/emit_dfa.c,
# rebuilt, this script run, and reverted. **The clean baseline is 15 passed /
# 0 failed**; the logs are `scratchpad/srPremul/plant{1,2,3}.log`.
#
#   PLANT 1 -- THE TABLE IS NOT PREMULTIPLIED WHILE THE LOOP ASSUMES IT IS.
#     `emit_tr_table`'s premultiplied arm emits `t` where it should emit
#     `t * d->ncls` (the sentinel and the type left alone), so every emitted
#     cell is a raw state index and the loop indexes `table[state + class]`
#     with a state that never carries the stride.
#     **MEASURED: 13 passed / 19 failed** -- SS5 red on 14,387 of 39,787 cells
#     and SS6 red on nine subject cells (`a(b|c)+d` on "abcd" answers nomatch
#     where the denied build answers 0..4). The ordinary corpus is red too, at
#     65 of 100 cases over three `.rxt` files.
#     **SS1, SS2 and SS3 STAY GREEN, and that is the check localising rather
#     than going uniformly red**: they read the table DECLARATIONS and the
#     plant changes the CELLS.
#
#   PLANT 2 -- THE SENTINEL COLLIDES. **Raising `PREMUL_MAX_ENTRIES` past the
#     range bound is NOT ENOUGH** -- the RANGE conjunct still refuses, which
#     is the measured demonstration that the emitter's (i) is not redundant
#     with its tighter (ii). Breaking BOTH (budget 100000 AND the
#     `ents > 65535` clause deleted) makes `[01]*1[01]{13}` emit a
#     73,728-entry premultiplied table whose cells overflow `unsigned short`
#     -- gcc reports 5,460 overflow warnings, so the artifact does not even
#     build clean -- and in which 65535 appears as a real cell.
#     **MEASURED: 12 passed / 5 failed** -- SS1's straddling witness, SS2's two
#     above-bound rows AND its non-vacuity guard ("the swept family did not
#     STRADDLE the bound"), and SS3's bound arm on 4 machines.
#     **SS5 STAYS GREEN, and the honest reading matters**: the corpus's largest
#     machine is 40,010 entries, so no corpus artifact CAN carry a collided
#     cell. The cell invariant cannot see this defect; what makes a collision
#     unreachable is the BOUND, and the bound arm is what goes red.
#
#   PLANT 3 -- THE STATE VARIABLE LEFT `int` (the silent regression (i)).
#     Confirmed at the instruction level before the check was run: with `int`,
#     `movslq %edx,%rdx` is back ON the loop-carried chain (at 0x57 of the
#     emitted `rx_search`, where the `unsigned` form has an eliminable
#     `mov %edx,%edx`) plus a second `movslq` off it -- and EVERY ANSWER IS
#     UNCHANGED.
#     **MEASURED: 14 passed / 1 failed** -- SS3's shape arm alone, on 1,824
#     machines. Nothing else in this file moves, and nothing else in the tree
#     can: the artifact is correct, so no corpus case, no differential and no
#     byte-identity gate that compares an artifact against itself sees it.
#
# Usage: bash tests/codegen/run_premul_table.sh
# Env: PCREC (default <root>/build/pcrec), CC, KEEP=1, PREMUL_CORPUS=0 (skip §3/§5)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-cc}"
KEEP="${KEEP:-0}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # [K37] pcrec_run / gen_cc / gen_run

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "premul-table: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

[ -x "$PCREC" ] || { echo "FAIL: premul-table: no compiler at $PCREC — run \`make\` first" >&2; exit 1; }

# THE DOCUMENTED VALUE SET, spelled here so this file states the contract it
# checks rather than accepting whatever the emitter says (docs/spec/match_api.md
# §6.3). A new value needs a spec hunk and a line here, in the same change.
TABLE_VALUES="premultiplied indexed mixed none"

# THE BOUND, spelled here as a SECOND source. src/gen/emit_dfa.c's
# PREMUL_MAX_ENTRIES is the first; a check that read the compiler's own
# constant could not see it move. If this number and the emitter's disagree,
# §2/§3 go red and the disagreement is the finding — which is the point.
#
# It is the RANGE condition and nothing else: a cell must fit `unsigned short`
# and be distinguishable from the dead sentinel. A tighter 16,384-entry SIZE
# BUDGET stood here until 2026-08-26 and was DELETED on a measurement — the
# pre-multiplied form still wins across the whole L2-resident band (1.097x at
# 36,864 entries, 1.287x on the corpus's own 40,010-entry reverse machine;
# design note §13).
PREMUL_MAX_ENTRIES=65535
# The RANGE bound is a correctness condition, not a budget: a cell must fit
# `unsigned short` and be distinguishable from the dead sentinel.
PREMUL_DEAD=65535

# ---------------------------------------------------------------------------
# The per-artifact derivation: read an artifact on stdin and print one line
#
#   scan=<0|1> fpm=<-1|0|1> rpm=<-1|0|1> fent=<N> rent=<N> fcls=<N> rcls=<N>
#   facc=<N> racc=<N> fvar=<int|unsigned|-> rvar=<...> fix=<mul|add|-> rix=<...>
#   stamp=<value|->
#
# derived ENTIRELY from the emitted matcher text, except `stamp`, which is the
# `#define` line and is kept visibly separate so the two cannot become one
# source. `-1` means "this machine has no numeric transition table here".
# ---------------------------------------------------------------------------
read_artifact() {
    awk '
        # ---- (i) DERIVED: emitted matcher text, and nothing else -----------
        # The transition table DECLARATIONS. The TYPE is the form and the
        # SUBSCRIPT is states*classes; emit_tr_table writes both in one line.
        /^    static const short rx_forward_next_state\[/          { fpm = 0; fent = ent($0) }
        /^    static const unsigned short rx_forward_next_state\[/ { fpm = 1; fent = ent($0) }
        /^    static const short rx_reverse_next_state\[/          { rpm = 0; rent = ent($0) }
        /^    static const unsigned short rx_reverse_next_state\[/ { rpm = 1; rent = ent($0) }
        # The ACCEPT tables. Under the premultiplied form these are indexed by
        # the premultiplied value and are therefore states*classes long; under
        # the indexed form they are states long. A DERIVED cross-check on the
        # form, from a different emitter function than the one above.
        /^    static const unsigned char rx_forward_is_accepting\[/ { facc = ent($0) }
        /^    static const unsigned char rx_reverse_is_accepting\[/ { racc = ent($0) }
        # The STATE VARIABLE declarations — the only witness of failure mode (i).
        /^    (int|unsigned) forward_state = /                     { fvar = $1 }
        /^        (int|unsigned) reverse_state = /                 { rvar = $1 }
        # The TRANSITION LINES: does the emitted index still multiply?
        /forward_state = rx_forward_next_state\[/ {
            fix = ($0 ~ /\* [0-9]+ \+/) ? "mul" : "add" }
        /reverse_state = rx_reverse_next_state\[/ {
            rix = ($0 ~ /\* [0-9]+ \+/) ? "mul" : "add" }
        # Does this artifact contain a DFA scan at all? The [DD-13c] iff, with
        # the markers run_dfa_stamps.sh uses: matcher text written by
        # emit_dfa.c, never a stamp. The EMPTY engine COUNTS -- its body is one
        # `return 0` and it emits no table, yet it is a DFA scan and stamps
        # `"none"`. A check discriminating on "has a table" would call those
        # four corpus artifacts stamp-without-a-scan, which is r37 finding #5
        # read backwards.
        /^    \(void\)subject; \(void\)subject_length; \(void\)search_from; \(void\)capture_spans;$/ \
                                                                   { scan = 1 }  # the empty engine
        /^    const size_t start_max = /                           { scan = 1 }  # ENG_ATTEMPT
        /rx_forward_next_state\[/                                  { scan = 1 }  # ENG_UNANCH
        /^static int rx_prefilter\(const unsigned char \*subject, / { scan = 1 }  # the inlined hybrid
        # ---- (ii) STAMPED: the `#define` line, and nothing else ------------
        /^#define RX_DFA_TABLE "/ { s = $0; sub(/^#define RX_DFA_TABLE "/, "", s);
                                    sub(/"$/, "", s); stamp = s }
        function ent(l,   t) { t = l; sub(/^[^[]*\[/, "", t); sub(/\].*$/, "", t); return t + 0 }
        END {
            printf "scan=%d fpm=%d rpm=%d fent=%d rent=%d facc=%d racc=%d fvar=%s rvar=%s fix=%s rix=%s stamp=%s\n",
                   (scan ? 1 : 0),
                   (fent ? fpm : -1), (rent ? rpm : -1),
                   fent + 0, rent + 0, facc + 0, racc + 0,
                   (fvar == "" ? "-" : fvar), (rvar == "" ? "-" : rvar),
                   (fix == "" ? "-" : fix), (rix == "" ? "-" : rix),
                   (stamp == "" ? "-" : stamp)
        }
    '
}

# The CLASS COUNT of a machine, from `rx_<dir>_byte_class[256]` — a DIFFERENT
# table written by a DIFFERENT emitter function than the transition table
# whose cells §5 checks against it. Largest class value + 1.
class_count() {   # <file> <forward|reverse>
    awk -v dir="$2" '
        $0 ~ ("^    static const unsigned char rx_" dir "_byte_class\\[256\\]") { inb = 1; next }
        inb && /\};/ { exit }
        inb { n = split($0, a, ","); for (i = 1; i <= n; i++) {
                  gsub(/[ \t]/, "", a[i]); if (a[i] ~ /^[0-9]+$/ && a[i] + 0 > m) m = a[i] + 0 } }
        END { print m + 1 }
    ' "$1"
}

# Every CELL of one transition table, one per line.
table_cells() {   # <file> <forward|reverse>
    awk -v dir="$2" '
        $0 ~ ("^    static const (unsigned )?short rx_" dir "_next_state\\[") { inb = 1; next }
        inb && /\};/ { exit }
        inb { n = split($0, a, ","); for (i = 1; i <= n; i++) {
                  gsub(/[ \t]/, "", a[i]); if (a[i] != "") print a[i] } }
    ' "$1"
}

# The artifact-level stamp value the per-machine facts imply. This is the
# check's OWN statement of the rule (match_api.md §6.3's value set), never a
# call into the compiler.
implied_stamp() {   # <fpm> <rpm>
    case "$1:$2" in
        -1:-1) echo none ;;
        1:1)   echo premultiplied ;;
        0:0)   echo indexed ;;
        # A machine that has no numeric table at all cannot disagree with one
        # that does; ENG_ATTEMPT is `-1:-1` above, so this arm is a genuinely
        # mixed pair and nothing else.
        *)     echo mixed ;;
    esac
}

echo "== [OPT-3] §1 witnesses: the rule switches on BOTH sides =="

# THE WITNESSES ARE CHOSEN FOR THEIR DIMENSIONS, not for their prose. The
# state-explosion family `[01]*1[01]{k}` is R1 A-3's, and it is the only family
# in reach of the bound: k=12 is 12,288 states x 3 classes = 36,864 entries
# (BELOW the 65,535 range bound), k=13 is 24,576 x 3 = 73,728 (ABOVE). The
# reverse machine of both is tiny, which is why k=13 stamps `"mixed"` and not
# `"indexed"` — the per-machine rule visible in one artifact.
#
# Format: <pattern>~<expected stamp>~<why>  (`~` because `|` is a pattern byte)
WITNESSES='
(?:[a-z]+)@(?:[a-z]+)~premultiplied~an ordinary pattern, far below the bound
a(b|c)+d~premultiplied~the tree-wide fixture, 4 states x 4 classes
[01]*1[01]{12}~premultiplied~36,864 entries — inside the range bound, and the size budget this used to fail is gone (measured, §13)
[01]*1[01]{13}~mixed~73,728 entries forward (ABOVE the range bound) and a small reverse machine (below)
^abc~none~ENG_ATTEMPT: states are labels, there is no numeric transition table
\B\b~none~the empty engine: one `return 0`, no loop of either shape
'

wit_n=0
while IFS='~' read -r pat want why; do
    [ -n "${pat:-}" ] || continue
    wit_n=$((wit_n + 1))
    f="$WORKDIR/w$wit_n.c"
    if ! pcrec_run "$PCREC" -p rx --features all --no-captures -o "$f" -- "$pat" >/dev/null 2>&1; then
        bad "[witness] '$pat' did not compile — this row has stopped testing what it names"
        continue
    fi
    eval "$(read_artifact < "$f")"
    imp="$(implied_stamp "$fpm" "$rpm")"
    case " $TABLE_VALUES " in *" $stamp "*) ;; *)
        bad "[witness] '$pat' stamps RX_DFA_TABLE \"$stamp\", which is not in the documented value set ($TABLE_VALUES) — a new value needs a docs/spec/match_api.md §6.3 hunk and a line in this file, in the same change" ;;
    esac
    if [ "$stamp" != "$want" ]; then
        bad "[witness] '$pat' ($why): stamps RX_DFA_TABLE \"$stamp\", expected \"$want\" — forward table $fent entries (form $fpm), reverse $rent (form $rpm)"
    elif [ "$imp" != "$stamp" ]; then
        bad "[witness] '$pat': stamps \"$stamp\" but its emitted tables imply \"$imp\" (forward form $fpm over $fent entries, reverse form $rpm over $rent) — the stamp has drifted from the loop it describes"
    else
        ok "[witness] '$pat' stamps RX_DFA_TABLE \"$stamp\" and its emitted tables agree (fwd $fent entries form=$fpm, rev $rent form=$rpm) — $why"
    fi
done <<EOF
$WITNESSES
EOF

echo "== [OPT-3] §2 the BOUND, read off the artifact on both sides =="

# The rule under test: a machine takes the premultiplied form IFF its
# states*classes is at or below PREMUL_MAX_ENTRIES. Asserted on the two
# adjacent members of the state-explosion family, whose entry counts are read
# out of the emitted declarations rather than computed here.
bound_bad=0; bound_seen=0
for k in 11 12 13; do
    f="$WORKDIR/b$k.c"
    pcrec_run "$PCREC" -p rx --features all --no-captures -o "$f" -- "[01]*1[01]{$k}" >/dev/null 2>&1 || continue
    eval "$(read_artifact < "$f")"
    [ "$fent" -gt 0 ] || continue
    bound_seen=$((bound_seen + 1))
    if [ "$fent" -le "$PREMUL_MAX_ENTRIES" ] && [ "$fpm" != "1" ]; then
        bad "[bound] '[01]*1[01]{$k}': forward table is $fent entries (<= $PREMUL_MAX_ENTRIES) but was emitted in the INDEXED form"
        bound_bad=$((bound_bad + 1))
    elif [ "$fent" -gt "$PREMUL_MAX_ENTRIES" ] && [ "$fpm" != "0" ]; then
        bad "[bound] '[01]*1[01]{$k}': forward table is $fent entries (> $PREMUL_MAX_ENTRIES) but was emitted in the PRE-MULTIPLIED form — above the bound the accept table's growth buys nothing and the range condition loses its margin"
        bound_bad=$((bound_bad + 1))
    fi
    echo "    [01]*1[01]{$k}: forward $fent entries, form=$fpm; reverse $rent, form=$rpm; stamp=$stamp"
done
# NON-VACUITY: the family must actually STRADDLE the bound in this run, or
# this section is asserting a rule nothing exercises.
straddle_lo=0; straddle_hi=0
for k in 11 12 13; do
    f="$WORKDIR/b$k.c"; [ -f "$f" ] || continue
    eval "$(read_artifact < "$f")"
    [ "$fent" -gt 0 ] || continue
    if [ "$fpm" = "1" ]; then straddle_lo=1; else straddle_hi=1; fi
done
if [ "$bound_seen" -lt 2 ]; then
    bad "[bound] only $bound_seen member(s) of the state-explosion family compiled — the bound cannot be exercised on both sides"
elif [ "$straddle_lo" != "1" ] || [ "$straddle_hi" != "1" ]; then
    bad "[bound] the swept family did not STRADDLE the bound (below-bound seen: $straddle_lo, above-bound seen: $straddle_hi) — this section would pass vacuously; widen the k range or re-check PREMUL_MAX_ENTRIES ($PREMUL_MAX_ENTRIES)"
elif [ "$bound_bad" -eq 0 ]; then
    ok "[bound] the generation-time rule switches in BOTH directions across $bound_seen members of the state-explosion family, at $PREMUL_MAX_ENTRIES entries, with the counts read off the emitted table declarations"
fi

echo "== [OPT-3] §3 the corpus sweep: stamp vs emitted tables, every artifact =="

if [ "${PREMUL_CORPUS:-1}" = "0" ]; then
    echo "    PREMUL_CORPUS=0: §3 and §5 skipped"
else
    PATFILE="$WORKDIR/patterns"
    find "$ROOT_DIR/tests" -name '*.rxt' -print0 \
        | xargs -0 grep -h '^pattern ' 2>/dev/null \
        | sed 's/^pattern //' | LC_ALL=C sort -u > "$PATFILE"
    npat=$(grep -c . "$PATFILE" || true)

    swept=0; cmp_n=0; drift=0; boundviol=0; accviol=0; shapeviol=0
    prem=0; idx=0; mix=0; non=0
    : > "$WORKDIR/premul_artifacts"
    while IFS= read -r pat; do
        f="$WORKDIR/c.c"
        pcrec_run "$PCREC" -p rx --features all -o "$f" -- "$pat" >/dev/null 2>&1 || continue
        swept=$((swept + 1))
        eval "$(read_artifact < "$f")"
        [ "$scan" = "1" ] || { [ "$stamp" = "-" ] || {
            bad "[iff] '$pat' carries RX_DFA_TABLE \"$stamp\" with no DFA scan in the artifact to describe"; drift=$((drift+1)); }
            continue; }
        if [ "$stamp" = "-" ]; then
            bad "[iff] '$pat' contains a DFA scan and stamps no RX_DFA_TABLE at all"
            drift=$((drift + 1)); continue
        fi
        cmp_n=$((cmp_n + 1))
        imp="$(implied_stamp "$fpm" "$rpm")"
        [ "$imp" = "$stamp" ] || { drift=$((drift + 1));
            echo "    DRIFT '$pat': stamps \"$stamp\", tables imply \"$imp\" (fwd $fent/$fpm rev $rent/$rpm)" >&2; }
        case "$stamp" in premultiplied) prem=$((prem+1)) ;; indexed) idx=$((idx+1)) ;;
                         mixed) mix=$((mix+1)) ;; none) non=$((non+1)) ;; esac
        # The BOUND, on every machine of every artifact.
        for pair in "f:$fpm:$fent:$facc" "r:$rpm:$rent:$racc"; do
            d=${pair%%:*}; rest=${pair#*:}; pm=${rest%%:*}; rest=${rest#*:}
            ent=${rest%%:*}; acc=${rest#*:}
            [ "$ent" -gt 0 ] || continue
            if [ "$pm" = "1" ] && [ "$ent" -gt "$PREMUL_MAX_ENTRIES" ]; then
                boundviol=$((boundviol + 1)); fi
            if [ "$pm" = "0" ] && [ "$ent" -le "$PREMUL_MAX_ENTRIES" ]; then
                boundviol=$((boundviol + 1)); fi
            # THE ACCEPT TABLE'S LENGTH IS A SECOND, INDEPENDENT WITNESS of the
            # form: premultiplied-indexed means states*classes cells, indexed
            # means states. It comes from a different emitter function than the
            # transition table's type, so the two agreeing is evidence.
            if [ "$pm" = "1" ] && [ "$acc" != "$ent" ]; then accviol=$((accviol + 1)); fi
            if [ "$pm" = "0" ] && [ "$acc" -ge "$ent" ]; then accviol=$((accviol + 1)); fi
        done
        # THE SHAPE, failure mode (i): a premultiplied machine must declare an
        # `unsigned` state variable and a transition line with no multiply; an
        # indexed one must declare `int` and keep the multiply.
        [ "$fent" -gt 0 ] && {
            want_var=int; want_ix=mul
            [ "$fpm" = "1" ] && { want_var=unsigned; want_ix=add; }
            { [ "$fvar" = "$want_var" ] && [ "$fix" = "$want_ix" ]; } || shapeviol=$((shapeviol + 1))
        }
        [ "$rent" -gt 0 ] && {
            want_var=int; want_ix=mul
            [ "$rpm" = "1" ] && { want_var=unsigned; want_ix=add; }
            { [ "$rvar" = "$want_var" ] && [ "$rix" = "$want_ix" ]; } || shapeviol=$((shapeviol + 1))
        }
        # Keep ONE premultiplied artifact per distinct forward-table size for
        # §5's cell sweep, so that section runs on a real population without
        # re-compiling the corpus.
        if [ "$fpm" = "1" ] && [ ! -f "$WORKDIR/pm_$fent.c" ]; then
            cp "$f" "$WORKDIR/pm_$fent.c"; echo "$fent" >> "$WORKDIR/premul_artifacts"
        fi
    done < "$PATFILE"

    echo "    corpus: $npat pattern(s), $swept compiled, $cmp_n contain a DFA scan"
    echo "    stamp distribution: premultiplied=$prem indexed=$idx mixed=$mix none=$non"

    # K35's remedy: a population nobody counts is a check nobody can trust.
    if [ "$cmp_n" -lt 500 ]; then
        bad "[population] only $cmp_n artifact(s) with a DFA scan reached the comparison, out of $swept compiled — the sweep has lost its population and every verdict below is about a fraction of it"
    else
        ok "[population] $cmp_n of $swept compiled artifacts contain a DFA scan and were compared (premultiplied=$prem indexed=$idx mixed=$mix none=$non)"
    fi
    if [ "$prem" -lt 1 ] || [ "$non" -lt 1 ]; then
        bad "[population] the corpus produced premultiplied=$prem and none=$non — at least one of each is needed or the agreement verdict is about one bucket"
    else
        ok "[population] both the premultiplied and the table-free buckets are non-empty ($prem / $non)"
    fi
    # WHERE THE ABOVE-BOUND SIDE IS ACTUALLY COVERED, said out loud rather than
    # left for a reader to assume. Since the bound became the RANGE condition
    # (65,535) every corpus machine fits inside it, so this sweep's `indexed`
    # and `mixed` buckets are legitimately EMPTY — and a check whose population
    # silently lost a value is the shape K35 is about. The above-bound side is
    # carried by §1's `[01]*1[01]{13}` witness and by §2's family sweep, whose
    # own straddle guard is what makes that a claim rather than a hope; this
    # line REQUIRES that guard to have seen an above-bound member.
    if [ "$((idx + mix))" -eq 0 ]; then
        if [ "$straddle_hi" = "1" ]; then
            ok "[population] the corpus is ENTIRELY inside the bound (indexed=0 mixed=0, largest machine 40,010 entries), so the above-bound side is not exercised here — it is carried by §1's [01]*1[01]{13} witness and §2's family sweep, which DID see an above-bound member"
        else
            bad "[population] the corpus has no indexed or mixed artifact AND §2 saw no above-bound member either — nothing in this file exercises the above-bound side of the rule"
        fi
    else
        ok "[population] the corpus itself still carries above-bound machines (indexed=$idx mixed=$mix), so §3 exercises both sides of the rule directly"
    fi
    if [ "$drift" -ne 0 ]; then
        bad "[agreement] $drift artifact(s) stamp a table form their emitted tables do not have"
    else
        ok "[agreement] all $cmp_n artifacts stamp the table form their emitted declarations imply"
    fi
    if [ "$boundviol" -ne 0 ]; then
        bad "[bound] $boundviol machine(s) took a form the generation-time rule forbids at their size (bound $PREMUL_MAX_ENTRIES entries)"
    else
        ok "[bound] every machine in the corpus took the form its own states*classes calls for"
    fi
    if [ "$accviol" -ne 0 ]; then
        bad "[accept] $accviol accept table(s) have a length inconsistent with their machine's table form — a premultiplied machine's accept table is states*classes long, an indexed one's is states"
    else
        ok "[accept] every accept table's LENGTH agrees with its machine's form, derived from a different emitter function than the transition table's type"
    fi
    if [ "$shapeviol" -ne 0 ]; then
        bad "[shape] $shapeviol machine(s) declare a state variable or emit a transition index inconsistent with their table form. An 'int' state variable under the premultiplied form is CORRECT and reinstates the movslq the transform exists to remove — a silent performance regression no answer check can see"
    else
        ok "[shape] every premultiplied machine declares 'unsigned' and emits an add-only index; every indexed one declares 'int' and keeps its multiply"
    fi

    echo "== [OPT-3] §5 the CELL invariant on every premultiplied table =="
    cellbad=0; celln=0; tabn=0
    for ent in $(LC_ALL=C sort -un "$WORKDIR/premul_artifacts" 2>/dev/null); do
        f="$WORKDIR/pm_$ent.c"; [ -f "$f" ] || continue
        for dir in forward reverse; do
            ncls="$(class_count "$f" "$dir")"
            [ "${ncls:-0}" -gt 0 ] || continue
            cells="$(table_cells "$f" "$dir")"
            [ -n "$cells" ] || continue
            tabn=$((tabn + 1))
            n=$(printf '%s\n' "$cells" | grep -c . || true)
            celln=$((celln + n))
            b=$(printf '%s\n' "$cells" | awk -v m="$ncls" -v dead="$PREMUL_DEAD" -v len="$n" '
                $1 == dead { next }                       # the reserved dead cell
                ($1 % m) != 0 || $1 + 0 >= len { c++ }    # not a premultiplied state of this machine
                END { print c + 0 }')
            cellbad=$((cellbad + b))
        done
    done
    if [ "$tabn" -lt 2 ]; then
        bad "[cells] only $tabn premultiplied table(s) reached the cell sweep — the invariant is asserted over nothing"
    elif [ "$cellbad" -ne 0 ]; then
        bad "[cells] $cellbad of $celln cells across $tabn premultiplied table(s) are neither the dead sentinel ($PREMUL_DEAD) nor a multiple of their machine's class count below the table's own length — the table is not premultiplied, or a real cell has collided with the sentinel"
    else
        ok "[cells] all $celln cells across $tabn premultiplied table(s) are either $PREMUL_DEAD or a multiple of the class count (read from rx_*_byte_class, a different table) strictly inside the table"
    fi
fi

echo "== [OPT-3] §6 the deny flag: answer-identical, form flipped =="

# `-fno-premul-table` is ANSWER-IDENTITY-preserving (docs/spec/tuning.md
# §2.13) and is the control the premultiplied build is compared against. This
# is the smallest honest version of that comparison: the SAME pattern in both
# forms, over a subject set that reaches both machines (the reverse pass runs
# only after the forward pass finds an end).
ID_PATTERNS='(?:[a-z]+)@(?:[a-z]+)
a(b|c)+d
[a-z]+[0-9]*\.[a-z]+
(?:foo|foobar)\z
a*b
\bword\b
(?m)^ERROR
[01]*1[01]{4}'
ID_SUBJECTS='|a|abcd|xxabbccd|user@example|user.name@sub.example.com |foo|foobar|a.b|zz9.qq|word here word| word |ERROR: x
ERROR: y|0110110110|aaaaab|no match at all|.|@'

# The per-run wrapper here is `$TIMEOUT_BIN`, not `gen_run`: this is a
# per-case loop of a few hundred short runs, and gen_timeout.sh's own header
# rules the watchdog out of one (its per-call overhead is the harness's
# recorded reason for the same split).
idfail=0; idcells=0; idpat=0; idtried=0
while IFS= read -r pat; do
    [ -n "$pat" ] || continue
    d="$WORKDIR/id$idtried"; mkdir -p "$d"; idtried=$((idtried + 1))
    pcrec_run "$PCREC" -p rx --features all --no-captures --emit-main -o "$d/pm.c" -- "$pat" >/dev/null 2>&1 || continue
    pcrec_run "$PCREC" -p rx --features all --no-captures --emit-main -fno-premul-table -o "$d/ix.c" -- "$pat" >/dev/null 2>&1 || continue
    pmform=$(grep -m1 '^#define RX_DFA_TABLE' "$d/pm.c" | sed 's/.*"\(.*\)".*/\1/')
    ixform=$(grep -m1 '^#define RX_DFA_TABLE' "$d/ix.c" | sed 's/.*"\(.*\)".*/\1/')
    # A pattern whose scan carries no numeric transition table (ENG_ATTEMPT,
    # the empty engine) has no form for the flag to deny, so it cannot be a
    # row here. It is EXCLUDED rather than tolerated as an equal pair — the
    # equality below is the non-vacuity assertion for the rows that remain.
    if [ "$pmform" = "none" ]; then
        echo "    (skipped '$pat': RX_DFA_TABLE \"none\" — no numeric table for the flag to deny)"
        continue
    fi
    if [ "$pmform" = "$ixform" ]; then
        bad "[flag] '$pat': the default and -fno-premul-table builds both stamp \"$pmform\" — this row compares one form with itself"
        idfail=$((idfail + 1)); continue
    fi
    gen_cc "premul '$pat'" "$CC" -O2 -Wall -Wextra -Werror -o "$d/pm" "$d/pm.c" || {
        bad "[flag] '$pat': the premultiplied artifact did not compile clean"; idfail=$((idfail+1)); continue; }
    gen_cc "indexed '$pat'" "$CC" -O2 -Wall -Wextra -Werror -o "$d/ix" "$d/ix.c" || {
        bad "[flag] '$pat': the -fno-premul-table artifact did not compile clean"; idfail=$((idfail+1)); continue; }
    while IFS= read -r subj; do
        a="$("$TIMEOUT_BIN" "$(gen_run_secs)" "$d/pm" "$subj" 2>&1; echo "rc=$?")"
        b="$("$TIMEOUT_BIN" "$(gen_run_secs)" "$d/ix" "$subj" 2>&1; echo "rc=$?")"
        idcells=$((idcells + 1))
        if [ "$a" != "$b" ]; then
            bad "[flag] '$pat' on '$subj': premultiplied says [$a], -fno-premul-table says [$b]"
            idfail=$((idfail + 1))
        fi
    done <<EOF
$(printf '%s' "$ID_SUBJECTS" | tr '|' '\n')
EOF
    idpat=$((idpat + 1))
done <<EOF
$ID_PATTERNS
EOF

if [ "$idcells" -lt 100 ] || [ "$idpat" -lt 5 ]; then
    bad "[flag] only $idcells identity cell(s) across $idpat comparable pattern(s) (of $idtried tried) — the comparison has no population"
elif [ "$idfail" -eq 0 ]; then
    ok "[flag] $idcells cells across $idpat comparable pattern(s) (of $idtried tried; the rest carry no numeric table): the premultiplied and -fno-premul-table artifacts agree exactly, and every pair genuinely differs in RX_DFA_TABLE"
fi

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
