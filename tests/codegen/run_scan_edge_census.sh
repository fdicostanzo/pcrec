#!/usr/bin/env bash
# tests/codegen/run_scan_edge_census.sh — [OPT-EDGE] STEP 1.1: precondition
# (8)'s population, held to the artifact.
#
# =========================================================================
# WHAT IS BEING DEFENDED
# =========================================================================
# `src/opt/scanedge.c`'s precondition (8) refuses a scan-edge head that a SEED
# family names, on a machine whose candidate-start prefilter WRITES the state
# variable. Two facts have to hold together for the emitted loop to be sound,
# and each is invisible to every answer check in the tree until it is not:
#
#   (A) the loop's ONE PER-SEARCH entry test recognises a head the START SEED
#       installed. `seed_emit_seeded` initialises the state variable from
#       `seed_state[byte_class[subject[search_from - 1]]]` -- ANY member of the
#       family -- so a test that asks "is this exactly the start state" misses
#       every other head-valued seed, the generic path then runs at a head, and
#       the step reads the transition cell the pass KILLED. That was the shape
#       until STEP 1.1; the test is now `is_stop && !is_dead`, the same
#       question the loop body asks.
#
#   (B) precondition (8) still refuses on the machines where the hazard is
#       real -- the `offset-set` prefilter's RESEED, which writes the state
#       variable MID-BODY, after the stop test has already been passed.
#
# THE CENSUS IS THE INSTRUMENT FOR (A) AND THE MANIFEST BELOW IS ITS
# EXPECTATION, SPELLED HERE RATHER THAN HARVESTED. STEP 1 cost these eleven
# artifacts their scan edge; STEP 1.1 gives all eleven back, and WHICH MACHINE
# each one lands on is the fact worth pinning, because it is what the STEP 1
# census got wrong: it read the artifact-level `RX_DFA_PREFILTER` stamp and
# concluded two of the eleven carried the hazard, when the edge those two lost
# is on the REVERSE machine -- which has no prefilter at all.
#
# =========================================================================
# WHAT THIS FILE DOES NOT CHECK, AND WHY THAT IS SAID OUT LOUD
# =========================================================================
# It is NOT a control on (B). The narrowed (8) has an EMPTY population on
# today's corpus (measured: an artifact built with the precondition deleted is
# byte-identical), so nothing here can go red if (8) is removed. A check with
# no failing direction is what `docs/dev/learnings.md` §3 warns about, so this
# file does not pretend to be one. (B)'s failing direction belongs to
# `tests/mech`, aimed at the emitter's own read-back check in
# `dfa_form_derive` -- which fires on the AGREEMENT between the pass's answer
# and the emitted form, and is therefore the one reading of (8) that does not
# share a source with the pass's decision.
#
# WHAT IT DOES INSTEAD IS COUNT THAT POPULATION OUT LOUD (K35). "(8) refused
# nothing today" is the kind of fact this tree has twice been wrong about by
# never counting it: `docs/dev/learnings.md` §3's K35 shape is a population
# nobody counts, and a precondition whose population is silently zero is
# indistinguishable from one that has quietly stopped being evaluated. §4
# sweeps the corpus and prints the three nested populations as FINDING lines,
# which are informational today and are what a reader compares against the
# next time this file runs.
#
# =========================================================================
# STALENESS
# =========================================================================
# The manifest is a list of patterns and an expectation per pattern. Two ways
# it can rot, and both are failures rather than silent passes:
#
#   * a listed pattern no longer appears as a `pattern` line under `tests/` --
#     the corpus moved and the census is measuring something nobody tests;
#   * a listed pattern's artifact carries a scan edge on a machine the
#     manifest does not name, or none at all.
#
# Plus a non-vacuity floor: fewer than FLOOR rows reaching their check means
# the enumeration stopped matching artifacts and the file is passing on air.

#
# [EMIT-VERB] 2026-09-19 — THIS CHECK'S INSTRUMENT IS AN EMITTED COMMENT, so
# every compile below passes `-fcomments`. That is not a workaround, and the
# licence for it is a measured identity rather than convenience: the emitted
# CODE is byte-identical between `-fcomments` and the default on 3,517 of
# 3,517 corpus artifacts, with the object files identical too
# (docs/dev/lanes/emitverb_report.md §2.2), so a STRUCTURAL census taken with
# comments on is a true statement about the default artifact's machine. The
# alternative — minting a code-level marker for the mechanism — would be new
# emitted scaffolding, i.e. another abi event, for a need nothing has
# measured (D77).
set -uo pipefail
cd "$(dirname "$0")/../.."
PCREC=${PCREC:-build/pcrec}
# D172 S3: every compile below carries the `cover` row's deny (registry.md
# §6¶8a): this census's witnesses and population are the scan machines' edges,
# and a fixed-width pattern is a `cover` artifact by default, running no
# machine; the deny renders the default build before S3.
COVER_DENY=--memfn=no-window-search
# [K37] pcrec_run: every compiler invocation below runs under a bound. The
# check that enforces this is tests/codegen/run_codegen_tests.sh's K37 leg,
# and it caught this file's three unbounded calls on the first battery run.
. "$(pwd)/tests/lib/gen_timeout.sh"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
fail=0; pass=0; checked=0
FLOOR=11
# [SCANEDGE-SET] section (7)'s non-vacuity floors: HALF of what the landing
# tree measured (1,371 unbounded edges checked, 243 counting more than one
# class, 2026-10-26), so a corpus edit does not read as a regression while a
# sweep that stopped reaching the edges, or a set rule that lost its sets
# (the one-class rule measures 0 multi-class edges), still does.
SET_FLOOR_U=685; SET_FLOOR_M=121

say()  { printf '%s\n' "$*"; }
ok()   { pass=$((pass+1)); }
bad()  { fail=$((fail+1)); printf 'FAIL [scan-edge-census] %s\n' "$*"; }

# ---- the manifest: pattern -> the machines that must carry an edge ---------
# `f` forward, `r` reverse, `a` anchored; a leading count is the number of
# edge blocks that machine must carry. Written from the measured artifact and
# NOT harvested at run time -- an expectation a script computes from the thing
# it is checking is not an expectation.
#
# [OPT-VEDGE] (lane vedge, 2026-10-03) moved two rows: `\b\w+\b\z` 1 -> 2 and
# `\b\w+\z` 1 -> 3 forward edges, the view-tolerant edge admitting their
# END-view-only `\w` chains (section (6) below has that row's own witnesses).
MANIFEST=(
  '(\b\w+\b)|f=1'
  '(foo\B)|r=1'
  '\b\w+\b|f=1'
  '\b\w+\b$|f=1'
  '\b\w+\b\z|f=2'
  '\b\w+\z|f=3'
  '\b\w\b|f=1'
  'foo\B|r=1'
  '\b\K\w+|f=2'
  '\Bfoo\B|r=1'
  '\bfoo\B|r=1'
)

# Count the edge blocks a machine carries, from the artifact's own `[OPT-5]
# SCAN EDGE` markers attributed by the STATE VARIABLE the block tests. The
# marker is the instrument and the stamp is not: `RX_DFA_SCAN_EDGE` names axis
# I's BODY form, so a machine going from two edges to one reads identical.
edges_on() {   # $1 artifact, $2 machine
    awk -v m="$2" '
        /\[OPT-5\] SCAN EDGE/ { pend = 1; next }
        pend && $0 ~ ("if \\(" m "_state ==") { n++; pend = 0 }
        END { print n + 0 }
    ' "$1"
}

# Count the edge HEADS a machine carries that its seed table can INSTALL —
# precondition (8)'s own question, read off the artifact rather than the pass:
# a head cell (the `if (<m>_state == K` under an `[OPT-5] SCAN EDGE` marker)
# that is also a value of `rx_<m>_seed_state[]` other than the start cell
# (the `: K;` the entry seed falls back to — `s0` is exempt for (8)'s own
# reason, see `in_degrees` in src/opt/scanedge.c). Both are cells in the
# artifact's own representation, so no un-multiplying is needed.
seeded_heads_on() {   # $1 artifact, $2 machine
    awk -v m="$2" '
        $0 ~ ("_" m "_seed_state\\[[0-9]+\\] = \\{") { intbl = 1; next }
        intbl { if ($0 ~ /\};/) { intbl = 0; next }
                gsub(/[ ,]+/, " "); for (i = 1; i <= NF; i++) seed[$i] = 1; next }
        $0 ~ ("_" m "_seed_state\\[.*\\] : [0-9]+;") && !have0 {
            s0 = $0; sub(/.* : /, "", s0); sub(/;.*/, "", s0); have0 = 1 }
        /\[OPT-5\] SCAN EDGE/ { pend = 1; next }
        pend && $0 ~ ("if \\(" m "_state == [0-9]+") {
            h = $0; sub(".*" m "_state == ", "", h); sub(/[^0-9].*/, "", h)
            head[h] = 1; pend = 0 }
        END { for (h in head) if ((h in seed) && h != s0) n++; print n + 0 }
    ' "$1"
}

say "== [OPT-EDGE] STEP 1.1 -- precondition (8)'s census =="

for row in "${MANIFEST[@]}"; do
    pat=${row%|*}
    want=${row##*|}
    mach=${want%%=*}
    cnt=${want##*=}
    case $mach in f) mv=forward;; r) mv=reverse;; a) mv=anchored;; *) bad "bad manifest row: $row"; continue;; esac

    # (1) STALENESS: the pattern is still in the corpus.
    if ! grep -RFqx -- "pattern $pat" tests/ 2>/dev/null; then
        bad "STALE MANIFEST: '$pat' is no longer a 'pattern' line under tests/"
        continue
    fi

    # [OPT-REVEND] the rows count the FORWARD (composite) machine's edges; an
    # end-pinned row walks back from the end by default and carries no
    # forward machine, so the census compiles every row with that row denied
    # (byte-identical on a pattern it does not reach). [START-LANDING]: a
    # fixed-width or one-character row (`foo\B`, `[0-9]{3}\z`) recovers its
    # start without the REVERSE machine whose edges it counts, so both new
    # RECOVER rows are denied too (byte-identical where they do not apply).
    if ! pcrec_run "$PCREC" -p rx --features all -fcomments $COVER_DENY -fno-rev-end -fno-start-width -fno-start-landing -o "$TMP/a.c" --pattern "$pat" >"$TMP/err" 2>&1; then
        bad "'$pat' failed to compile: $(head -1 "$TMP/err")"
        continue
    fi
    checked=$((checked+1))

    got=$(edges_on "$TMP/a.c" "$mv")
    if [ "$got" != "$cnt" ]; then
        bad "'$pat': expected $cnt scan edge(s) on the $mv machine, found $got"
        continue
    fi

    # (2) The entry dispatch has to be able to SEE a seeded head. Where the
    #     machine emits a seed table AND carries an edge, the emitted entry
    #     must be the general test rather than an equality against the start
    #     state -- that regression is silent to every answer check whose
    #     subjects never seed onto a head.
    if grep -q "rx_${mv}_seed_state" "$TMP/a.c"; then
        if ! grep -q "if (rx_${mv}_is_stop(${mv}_state) && !rx_${mv}_is_dead(${mv}_state)) goto rx_${mv}_scan_edge;" "$TMP/a.c"; then
            bad "'$pat': the $mv machine has a seed table and a scan edge, but its loop entry is not the general head test"
            continue
        fi
    fi
    ok
done

# (3) The two `offset-set` artifacts must keep a FORWARD machine with no edge:
#     that is where precondition (8) still applies, and it is the half of the
#     STEP 1 census that was misread.
for pat in '\Bfoo\B' '\bfoo\B'; do
    pcrec_run "$PCREC" -p rx --features all -fcomments $COVER_DENY -o "$TMP/a.c" --pattern "$pat" >/dev/null 2>&1 || { bad "'$pat' failed to compile"; continue; }
    if [ "$(grep -c 'RX_DFA_PREFILTER "offset-set-bounded"' "$TMP/a.c")" -ne 1 ]; then
        bad "'$pat' no longer takes an offset-set prefilter -- the census's own hazard witness moved"
        continue
    fi
    if [ "$(edges_on "$TMP/a.c" forward)" != "0" ]; then
        bad "'$pat': its forward machine took a scan edge while its prefilter reseeds -- precondition (8) did not fire"
        continue
    fi
    ok
done

# ---------------------------------------------------------------------------
# (4) [K35] THE RESEED-HAZARD POPULATION, COUNTED RATHER THAN ASSUMED ZERO.
#
# Three NESTED populations over every distinct `pattern` line under tests/:
#
#   P1  artifacts whose FORWARD prefilter is one of the two `offset-set`
#       forms or ([OPT-LITSCAN] S1) the two `run-pinned` forms, which emit
#       the same block -- the only forms that WRITE the state variable;
#   P2  of those, the ones that also emit a forward SEED table, which is the
#       set on which precondition (8) is evaluated non-trivially at all;
#   P3  of those, the ones whose forward machine carries a scan edge whose
#       HEAD the seed table can install (a seed value other than the start
#       cell) -- which must be 0, because that is exactly the state (8)
#       refuses, and exactly `dfa_form_derive`'s read-back condition.
#
# [cgtri] 2026-10-07: P3 USED TO BE "carries ANY scan edge", which is STEP 1's
# un-narrowed (8), not STEP 1.1's. It held only while P2's edge-carrying
# population was empty; tests/possessify/composition_d27.rxt's
# `(?:\b(?1)|x)(a+)` is the first P2 member with an edge, on the `aa` state
# (cell 12), while its seed table installs only cells 0 and 4 -- an edge (8)
# correctly does NOT refuse (answers checked against libpcre2 10.46 over 1,500
# random subjects, 0 differences; docs/dev/lanes/cgtri_report.md). Such
# machines are now counted as P2e, a FINDING, so the population (8) is narrowed
# away from stays visible rather than silently absorbed.
#
# P3 IS A RED AND THE OTHER TWO ARE FINDINGS, and the asymmetry is the point.
# P3 restates `dfa_form_derive`'s own read-back check at corpus scale and is
# cheap, so it is asserted. P1 and P2 cannot be asserted against a number:
# they are properties of the CORPUS, they will move when a pattern is added,
# and pinning them would make a corpus edit look like a regression. What they
# are for is the reader -- P2 == 0 means (8) has stopped being reachable at
# all, which is a fact worth seeing rather than discovering.
#
# WHAT THE SWEEP CANNOT SEE, said here rather than implied: whether (8)
# actually COST any of P2 an edge. That needs a compiler built without the
# precondition, which is a mech row's job (S227's neighbour), not a codegen
# check's. Measured once by hand at this landing: 0.
#
# `POP_PATTERNS` overrides the corpus enumeration with a file of patterns, one
# per line -- how this section was validated under a box hold that forbids
# corpus sweeps.
if [ -n "${POP_PATTERNS:-}" ]; then
    cp "$POP_PATTERNS" "$TMP/pats"
else
    # [K35] LC_ALL=C on the sort, run_dfa_stamps.sh's own lesson: under the
    # ambient collation punctuation folds and distinct patterns are dropped.
    grep -rhE '^pattern ' tests 2>/dev/null | sed 's/^pattern //' \
        | LC_ALL=C sort -u > "$TMP/pats"
fi
p1=0; p2=0; p2e=0; p3=0; npat=0
# (7) [SCANEDGE-SET] rides this sweep's compile: every edge-bearing artifact
# goes to tests/codegen/scan_set_check.py (one interpreter, a coprocess),
# which holds each edge's run-test byte set to the machine's own transition
# row read off the same artifact. Its header says what each half proves.
coproc SETCHK { python3 tests/codegen/scan_set_check.py --serve; }
su=0; sb=0; ss=0; sm=0; sart=0
while IFS= read -r pat; do
    [ -n "$pat" ] || continue
    npat=$((npat+1))
    pcrec_run "$PCREC" -p rx --features all -fcomments $COVER_DENY -o "$TMP/p.c" --pattern "$pat" >/dev/null 2>&1 || continue
    if grep -q '\[OPT-5\] SCAN EDGE' "$TMP/p.c"; then
        printf '%s\n' "$TMP/p.c" >&"${SETCHK[1]}"
        IFS=' ' read -r v a b c d e <&"${SETCHK[0]}"
        if [ "$v" = ok ]; then
            sart=$((sart+1)); su=$((su+a)); sb=$((sb+b)); ss=$((ss+c)); sm=$((sm+d))
            [ "$c" = 0 ] || say "FINDING [SCANEDGE-SET]   $c edge(s) not evaluated ($e): '$pat'"
        else
            bad "[SCANEDGE-SET] '$pat': $a $b $c $d $e"
        fi
    fi
    grep -qE 'RX_DFA_PREFILTER "(offset-set|run-pinned)' "$TMP/p.c" || continue
    p1=$((p1+1))
    grep -q 'rx_forward_seed_state' "$TMP/p.c" || continue
    p2=$((p2+1))
    [ "$(edges_on "$TMP/p.c" forward)" != "0" ] || continue
    p2e=$((p2e+1))
    if [ "$(seeded_heads_on "$TMP/p.c" forward)" = "0" ]; then
        say "FINDING [K35]   edge on a reseeding seeded machine, head not seedable: '$pat'"
        continue
    fi
    p3=$((p3+1))
    bad "'$pat': a forward machine with a RESEEDING prefilter carries a scan edge on a head its seed table installs -- precondition (8) did not fire"
done < "$TMP/pats"

say "FINDING [K35] reseed-hazard population over $npat corpus patterns:"
say "FINDING [K35]   P1 forward prefilter reseeds ............. $p1"
say "FINDING [K35]   P2   ... and the machine has a seed ...... $p2   <- where (8) is live"
say "FINDING [K35]   P2e    ... and it carries a scan edge .... $p2e"
say "FINDING [K35]   P3       ... on a seedable head ........... $p3   <- must be 0"
say "FINDING [SCANEDGE-SET] edge-bearing artifacts $sart: edges checked unbounded $su, bounded $sb, skipped $ss (a form not evaluable); $sm count more than one class"
# A set rule whose multi-class edges vanished, or a checker that stopped
# reading edges, would pass every comparison above on air (K35).
if [ -z "${POP_PATTERNS:-}" ] && { [ "$su" -lt "$SET_FLOOR_U" ] || [ "$sm" -lt "$SET_FLOOR_M" ]; }; then
    bad "[SCANEDGE-SET] only $su unbounded / $sm multi-class edges checked (floors $SET_FLOOR_U / $SET_FLOOR_M) -- the sweep is not reaching the edges"
else
    ok
fi
[ "$p3" -eq 0 ] && ok
if [ "$p2" -eq 0 ]; then
    say "FINDING [K35] precondition (8) is UNREACHABLE on this corpus -- no machine"
    say "FINDING [K35] pairs a reseeding prefilter with a seed table. It is kept"
    say "FINDING [K35] because the mechanism is real, not because it was witnessed."
fi

# (6) [OPT-VEDGE] THE VIEW-TOLERANT EDGE, held per machine and per direction.
#
# `src/opt/scanedge.c` admits two chains precondition (3)/(6) used to refuse:
# END-view-only members on a machine whose walk ENDS at `n` (forward and
# anchored, never reverse), and a chain whose head is a view target, trimmed
# one link. Each row below is `pattern|forward reverse anchored` edge counts,
# measured on the landing tree; under `-fno-view-edge` every count must be 0
# (none of these machines has a view-free chain); every row is compiled under
# `-fno-rev-end` ([OPT-REVEND]: an end-pinned pattern's default artifact has
# no forward machine). What each row pins:
#   `(?:[a-z]{0,4})\z` forward = the END-view chain; reverse = the TRIM (its
#                      start state reaches the chain only through its END
#                      view); the row's own customer shape.
#   `[0-9]{3}\z`       the anchored machine's END-view chain (an exact count).
#   `a{0,4}$`          an EOL view: the forward members carry `eolvar` and
#                      stay refused (forward 0), while the reverse trim fires.
# The direction half (the reverse walk never takes END-view members) has no
# structural witness here, since no corpus reverse machine has a scan-shaped
# END-viewed state; its detector is tests/assertions/view_edge.rxt's answers
# (mech row S440 plants exactly that).
VEDGE=(
  '(?:[a-z]{0,4})\z|1 1 0'
  '[0-9]{3}\z|2 1 1'
  'a{0,4}$|0 1 0'
)
for row in "${VEDGE[@]}"; do
    pat=${row%|*}
    want=${row##*|}
    if ! grep -RFqx -- "pattern $pat" tests/ 2>/dev/null; then
        bad "STALE [OPT-VEDGE] ROW: '$pat' is no longer a 'pattern' line under tests/"
        continue
    fi
    for deny in "" -fno-view-edge; do
        if ! pcrec_run "$PCREC" -p rx --features all -fcomments $COVER_DENY -fno-rev-end -fno-start-width -fno-start-landing $deny -o "$TMP/v.c" --pattern "$pat" >"$TMP/err" 2>&1; then
            bad "'$pat' $deny failed to compile: $(head -1 "$TMP/err")"
            continue
        fi
        got="$(edges_on "$TMP/v.c" forward) $(edges_on "$TMP/v.c" reverse) $(edges_on "$TMP/v.c" anchored)"
        exp=$want; [ -n "$deny" ] && exp="0 0 0"
        if [ "$got" != "$exp" ]; then
            bad "[OPT-VEDGE] '$pat' ${deny:-default}: edges forward/reverse/anchored $got, expected $exp"
            continue
        fi
        ok
    done
done

# (8) [SCANEDGE-SET] THE SET RULE'S WITNESSES, per machine. Each row is
# `pattern;;flags;;machine=edges/multi ...` (`;;`, because `|` is pattern text): every machine that carries an edge,
# how many, and how many of those count a SET of more than one class (the
# edge comment names `classes a, b`), sorted by machine name; an empty list is
# "no edge on any machine". Measured on the landing tree; before it every
# multi-class count was absent (the one-class rule found none of these runs).
#   `\S+@\S+`       the after-`x@y` run: `@` is its own class inside `\S`.
#   `\s+$`          the trimreg case: the reverse walk's run states and the
#                   `$`-lowered machine's; under -fno-rev-end the plain
#                   reverse machine keeps its one-class edge and the forward
#                   machine none (its run states carry an EOL view, (3)).
#   `0x[0-9a-fA-F]+` the literal `0` splits the hex digits.
#   `[a-z]+\.txt$`  reverse: `t`, `x` split `[a-z]`.
#   `[a-z]+$`       the ONE-CLASS CONTROL: one edge, one class, and its
#                   pcrec-side text pinned below (it must not move).
#   `(?:[a-z]|[0-9]X){0,8}`, `(?:a|bc)*` the NEGATIVE controls: two live
#                   classes going to DIFFERENT successors (`(?:a|bc)*`'s start
#                   state: `a` stays, `b` leaves, the rest die), so no state
#                   is scan-shaped. Non-capturing, so the artifact IS a DFA.
SETW=(
  '\S+@\S+;;;;anchored=1/1 forward=1/1 reverse=1/1'
  '\s+$;;;;anchored=1/1 reverse=2/2'
  '\s+$;;-fno-rev-end;;reverse=1/0'
  '0x[0-9a-fA-F]+;;;;anchored=1/1 forward=1/1'
  '[a-z]+\.txt$;;;;reverse=1/1'
  '[a-z]+$;;;;reverse=1/0'
  '(?:[a-z]|[0-9]X){0,8};;;;'
  '(?:a|bc)*;;;;'
)
set_edges_on() {   # $1 artifact -> "machine=edges/multi ..." sorted
    awk '
        /\[OPT-5\] SCAN EDGE/ { pend = 1; ms = ($0 ~ /classes [0-9]/); next }
        pend && /if \([a-z_]+_state ==/ {
            m = $0; sub(/^[ \t]*if \(/, "", m); sub(/_state ==.*/, "", m)
            n[m]++; if (ms) mm[m]++; pend = 0 }
        END { for (k in n) printf "%s=%d/%d\n", k, n[k], mm[k] + 0 }
    ' "$1" | LC_ALL=C sort | tr '\n' ' ' | sed 's/ $//'
}
for row in "${SETW[@]}"; do
    pat=${row%%;;*}; rest=${row#*;;}; flg=${rest%%;;*}; want=${rest#*;;}
    if ! grep -RFqx -- "pattern $pat" tests/ 2>/dev/null; then
        bad "STALE [SCANEDGE-SET] ROW: '$pat' is no longer a 'pattern' line under tests/"
        continue
    fi
    # shellcheck disable=SC2086
    if ! pcrec_run "$PCREC" -p rx --features all -fcomments $flg -o "$TMP/w.c" --pattern "$pat" >"$TMP/err" 2>&1; then
        bad "'$pat' $flg failed to compile: $(head -1 "$TMP/err")"
        continue
    fi
    got=$(set_edges_on "$TMP/w.c")
    if [ "$got" != "$want" ]; then
        bad "[SCANEDGE-SET] '$pat' ${flg:-default}: edges '$got', expected '$want'"
        continue
    fi
    ok
done
# The one-class control's pcrec-side edge text (the comment and the guard;
# the run loop inside is the kit's), byte for byte as the one-class rule
# emitted it before [SCANEDGE-SET].
SETCTL='// [OPT-5] SCAN EDGE: every state a run of class 1
// would pass IS this state, so count them here rather
// than stepping the table once per byte.
if (reverse_state == 4 && rewind_position > search_from && (unsigned)(subject[rewind_position - 1] - 97) <= 25u) {'
if pcrec_run "$PCREC" -p rx --features all -fcomments -o "$TMP/w.c" --pattern '[a-z]+$' >/dev/null 2>&1; then
    got=$(awk '/\[OPT-5\] SCAN EDGE/ { p = 1 } p { sub(/^[ \t]+/, ""); print; if (++k == 4) exit }' "$TMP/w.c")
    if [ "$got" = "$SETCTL" ]; then ok
    else bad "[SCANEDGE-SET] the one-class control '[a-z]+\$' moved its edge text: $(printf '%s' "$got" | tr '\n' '|')"
    fi
else
    bad "the one-class control '[a-z]+\$' failed to compile"
fi

# (5) NON-VACUITY.
if [ "$checked" -lt "$FLOOR" ]; then
    bad "only $checked of $FLOOR manifest rows reached their check -- the enumeration is not matching artifacts"
fi

# The two lines `tests/mech/run_sabotage_matrix.sh`'s `scanedge` arm greps.
# Spelled exactly as every other suite this tree drives from mech spells them,
# because that arm parses them with a fixed `^checks passed:` / `^checks
# failed:` pattern and a row naming a suite whose output it cannot read scores
# ERR rather than "not detected".
say "checks passed: $pass"
say "checks failed: $fail"
say "scan-edge census: $pass passed, $fail failed ($checked manifest rows compiled)"
[ "$fail" -eq 0 ]
