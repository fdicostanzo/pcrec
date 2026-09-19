#!/usr/bin/env bash
# tests/codegen/run_ir_listing.sh — [M4.5c] the VM program listing (DD-8) is
# held to the ARTIFACT it describes.
#
# WHY THIS EXISTS, and why it is not optional. engine_m4.md §10's one
# constraint on this tool is that "the dump must be derived from the same
# structure the emitter walks, never a parallel description — a second source
# of truth for what the VM does is worse than no dump." The emitter satisfies
# that structurally (every listing event is appended by the same call that
# writes the corresponding C — src/gen/emit_vm.c's VEvent stream), but a
# structural argument is exactly the kind of claim this project has learned to
# check rather than assert: it holds only as long as nobody adds a second way
# to emit a label, a push, or a slot write.
#
# So each SECTION of the listing is pinned to a fact DERIVABLE FROM THE .c:
#
#   PROGRAM        the label SET matches, both directions and without
#                  duplicates. A listing missing a label describes a program
#                  that is not the one emitted; a listing inventing one is
#                  worse.
#   CHOICE POINTS  every RX_PUSH in the .c appears once, and its resume TARGET
#                  matches the `&&<prefix>_L<n>` the push actually jumps to.
#   SLOTS          the set of slot_values slots the .c writes equals the
#                  set the listing shows written, and the layout covers
#                  RX_NSLOTS.
#   ISLANDS        the count is 0 AND the .c contains no island table — the
#                  honest-empty claim is checked against the artifact, not
#                  taken on trust, so the section starts working the day a
#                  producer exists.
#   CALLOUTS       same shape.
#   header         RX_NCAPS / step budget / frame + trail capacities agree
#                  with the macros in the .c.
#
# And the TRACE (§10's other half) is held to the property its own source
# comment claims: an instrumented artifact must take the SAME path as the
# untraced one. A debug build that changes the answer is a tool that lies.
#
# [REVW.2] WAVE 2 STAGE 3, 2026-09-18 (lane w2b): the PATTERNS array is 16
# rows, not the original 11, and each row declares its `--features` in the
# positionally parallel PATTERN_FEATURES array. Both arrays' own comments
# carry the reasoning; the short version is that four of the families whose
# role TEXT this file's BYTE-NEUTRALITY block pins are MODULE-GATED, and
# neither invocation below used to pass `--features`, so they refused to
# compile and read as "the corpus has no such shape". Measured reach of the
# `vm_rolef` call sites went 30 of 44 -> 42 of 44; the residual 2 are
# instrument-blind, not a population gap (see the array comment).
#
# Usage: bash tests/codegen/run_ir_listing.sh
# Env: PCREC (default <root>/build/pcrec), CC, GENCFLAGS, KEEP=1,
#      CLANGGEN=1 ([CC-CLANG]: default CC to clang, opt-in, explicit CC wins)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
# [CC-CLANG] CLANGGEN=1 defaults the COMPILEE axis to clang; an explicit CC
# always wins. Same shape as LINTGEN's -fanalyzer append, one compiler over.
CC="${CC:-}"
if [ -z "$CC" ]; then
    if [ "${CLANGGEN:-0}" = "1" ]; then CC="clang"; else CC="gcc"; fi
fi
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
if [ "${LINTGEN:-0}" = "1" ]; then GENCFLAGS="$GENCFLAGS -fanalyzer"; fi
KEEP="${KEEP:-0}"

# D45 (docs/dev/decisions.md): every compile of GENERATED C in this file runs
# under the shared budget -- a timeout is a FAILURE naming the case, never a
# hang. One implementation for the whole tree.
#
# EXECUTION of the trace-check plain/traced binaries below is bounded too
# (gen_run, same file): a handful of runs per pattern, not an inner loop.
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export WATCHDOG_SECTION="codegen"

# [DD-8] THE LISTING IS docs/spec/table_contract.md TSV NOW, so every
# extraction below resolves its SECTION and its COLUMN BY NAME through the
# contract's one implementation. D106's own diagnosis of this file is why:
# its extractors were fixed-position greps against a remembered shape and
# they went stale once already. A renamed section or column is now a LOUD
# failure from table.sh naming what it could not resolve, never an empty
# string that reads like a population with no rows.
. "$ROOT_DIR/tests/lib/table.sh"

# ir_labels FILE -> the PROGRAM section's numeric labels, spelled as the
# artifact spells them (`rx_L7`), sorted. The two TERMINAL labels (`accept`,
# `fail`) are labels in the listing and are NOT `rx_L<n>:` in the .c, so the
# numeric filter is a real part of the comparison and not tidying.
ir_labels() {
    local f="$1" pfx="${2:-rx}" v
    v="$(table_field "$f" program label)" || return 1
    printf '%s\n' "$v" | grep -E '^L[0-9]+$' | sed "s/^L/${pfx}_L/" | LC_ALL=C sort
}

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "ir-listing: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# Aggregated across the whole pattern sweep, for the CHOICE POINTS block's own
# non-vacuity guard. That block cannot assert non-emptiness per pattern the way
# SLOTS can -- a pattern whose quantifiers all possessify legitimately pushes
# no resume frame -- but across a sweep containing an alternation chain and a
# backtracking rung, ZERO pushes on either side means the extraction stopped
# matching rather than that the population vanished.
tot_cpush=0; tot_ipush=0

# The shapes, chosen so every emission path that can produce a listing event is
# represented: an alternation chain, both cursor rungs, the frames rung with
# and without the empty-iteration guard, nested captures, bounded replication,
# and the anchors.
#
# [REVW.2] WAVE 2 STAGE 3, 2026-09-18 (lane w2b) -- THE REACH WIDENING, and it
# is a REACH repair rather than a population preference. w1stage0.md sections 2-3
# measured this sweep reaching 27 of the 41 `vm_rolef` call sites whose role
# TEXT is the listing this arm pins, with lookbehind, subroutine-call, counter
# and possessive-chain emission reached by NOTHING; w2census_report.md's TASK 2
# then found the cause, and it is the INSTRUMENT, not the corpus: the two
# invocations below never passed `--features`, so every module-gated family
# (`lookaround`, `recursion`, `atomic-groups`, `backrefs`) refused to compile
# at all and read as "the corpus has no such shape" when the corpus is full of
# them. The five rows appended below are all EXISTING CORPUS PATTERNS (their
# home file named on each), each with the `--features` its module requires,
# and they take the measured reach to 39 of 41.
#
# THE REMAINING 2 OF 41 ARE INSTRUMENT-BLIND, NOT A POPULATION GAP, and no
# pattern added here or later changes that: `vm_counter_phase`'s two role
# texts (`src/gen/emit_vm.c`, the `"%lld * ((ptrdiff_t) %d - slot_values[%d]"`
# family) begin with a `%` conversion, so the reach census's own
# literal-prefix hit test has an EMPTY needle and is false by construction
# whatever compiles. Reaching them needs a census that can name a call site by
# something other than its own literal text -- a different instrument, not a
# longer array. Stated here so a later lane does not spend a session hunting
# for the two patterns that would close it.
PATTERNS=(
    'a(b|c)+d'
    '(a*)b'
    '(a*?)b'
    '(ab){2,3}c'
    '((a)|b)+c'
    '(a*)*'
    '(|a)+'
    '((a)(b))*'
    '(^a$)'
    '(\d+)-(\d+)'
    '(a|ab)(c|bcd)'
    '(?<=a|bc)x'
    '^(?:(a{2,5}(?1)?b)((?1)c)){0}(?2)$'
    '^(a)\1$'
    '((a)|ab){0,12}?c'
    '(?:a|ab){2,3}+'
)

# POSITIONALLY PARALLEL to PATTERNS: the `--features` value each row needs, ''
# for base grammar. Two arrays rather than one packed field because a pattern
# may contain any delimiter that would be chosen (these rows carry `|`, `:`
# and TAB-free but arbitrary regex text), and because bash's own `read`
# collapses empty delimited fields even under a single-character IFS
# (tt4m3_report.md's trap). The lengths are asserted equal below: a row added
# to one array and not the other would otherwise silently run at the WRONG
# features and the reach this widening bought would evaporate with no red.
#
# Source file per widening row, so a reviewer can re-derive that these are
# corpus shapes and not hand-written ones:
#   (?<=a|bc)x                           tests/lookaround/lookbehind_widths.rxt
#   ^(?:(a{2,5}(?1)?b)((?1)c)){0}(?2)$   tests/recursion/bothlinkage.rxt
#   ^(a)\1$                              tests/backrefs/gated.rxt
#   ((a)|ab){0,12}?c                     tests/counterk/counterk.rxt
#   (?:a|ab){2,3}+                       tests/atomic_groups/possessive.rxt
PATTERN_FEATURES=(
    '' '' '' '' '' '' '' '' '' '' ''
    'lookaround'
    'recursion'
    'backrefs'
    ''
    'atomic-groups'
)

if [ "${#PATTERNS[@]}" -ne "${#PATTERN_FEATURES[@]}" ]; then
    bad "ir-listing: PATTERNS (${#PATTERNS[@]}) and PATTERN_FEATURES (${#PATTERN_FEATURES[@]}) have different lengths; every pattern must declare its features (or '')"
    echo "ir-listing: $pass passed, $fail failed"
    exit 1
fi

for i in $(seq 0 $(( ${#PATTERNS[@]} - 1 )) ); do
    pat="${PATTERNS[$i]}"
    # An empty features value must expand to ZERO arguments, and a bare
    # "${arr[@]}" on an empty array is an "unbound variable" error under
    # `set -u` in this box's bash 3.2 (macport_report.md's platform). The
    # `${arr[@]+...}` guard is the spelling that gives 0 args when empty and
    # N args when not, verified on bash 3.2 itself.
    featflag=()
    if [ -n "${PATTERN_FEATURES[$i]}" ]; then
        featflag=(--features "${PATTERN_FEATURES[$i]}")
    fi
    d="$WORKDIR/$(printf '%s' "$pat" | md5sum | cut -c1-8)"
    mkdir -p "$d"
    # [ENG-ISL / panel r53 F11] `--engine=vm` ON BOTH, and it is a correctness
    # fix rather than tidiness: this block asserts below that the artifact
    # carries RX_VM_ALT_ISLANDS, which docs/spec/match_api.md §6.3 makes
    # VM-route-only. Compiled at the DEFAULT engine, a pattern that routes to
    # the DFA has no such stamp and the assertion fails for a reason that has
    # nothing to do with the listing. The listing itself is a VM program dump,
    # so the two invocations must agree about the engine anyway.
    if ! pcrec_run "$PCREC" -p rx --engine=vm ${featflag[@]+"${featflag[@]}"} \
            -o "$d/gen.c" -- "$pat" >/dev/null 2>&1; then
        bad "ir-listing: pcrec could not compile '$pat' (features: '${PATTERN_FEATURES[$i]}')"
        continue
    fi
    if ! pcrec_run "$PCREC" -p rx --engine=vm ${featflag[@]+"${featflag[@]}"} \
            --emit-ir -- "$pat" > "$d/ir" 2>"$d/ir.err"; then
        bad "ir-listing: --emit-ir failed for '$pat' (features: '${PATTERN_FEATURES[$i]}'): $(head -1 "$d/ir.err")"
        continue
    fi

    # ---- PROGRAM: the label set, both directions, no duplicates ----------
    grep -oE '^rx_L[0-9]+:' "$d/gen.c" | tr -d ':' | LC_ALL=C sort > "$d/c.labels"
    if ! ir_labels "$d/ir" > "$d/ir.labels"; then
        bad "ir-listing[$pat]: could not read the listing's program/label column (section or column renamed?)"
        continue
    fi
    # BSD wc -l right-justifies/pads its count with leading spaces even
    # through a pipe (docs/dev/lanes/macport_report.md S8); stripped so the
    # string comparisons below don't compare "0" against "       0".
    cdup="$(uniq -d < "$d/c.labels" | wc -l | tr -d ' ')"
    idup="$(uniq -d < "$d/ir.labels" | wc -l | tr -d ' ')"
    if [ ! -s "$d/c.labels" ]; then
        bad "ir-listing[$pat]: no labels found in the emitted C — the extraction is vacuous"
    elif [ "$idup" != "0" ]; then
        bad "ir-listing[$pat]: the listing shows a label more than once"
    elif [ "$cdup" != "0" ]; then
        bad "ir-listing[$pat]: the emitted C defines a label more than once (an emitter bug, caught here)"
    elif ! diff -q "$d/c.labels" "$d/ir.labels" >/dev/null; then
        bad "ir-listing[$pat]: label SETS differ between the .c and the listing: $(diff "$d/c.labels" "$d/ir.labels" | tr '\n' ' ' | cut -c1-200)"
    else
        nlab="$(wc -l < "$d/c.labels")"
        ok "ir-listing[$pat]: PROGRAM — all $nlab emitted labels appear exactly once in the listing, and the listing invents none"
    fi

    # ---- CHOICE POINTS: count and resume target --------------------------
    grep -oE 'RX_PUSH\(&&rx_L[0-9]+' "$d/gen.c" | grep -oE 'rx_L[0-9]+' \
        | LC_ALL=C sort > "$d/c.push"
    if ! ir_resume="$(table_field "$d/ir" choicepoints resume)"; then
        bad "ir-listing[$pat]: could not read the listing's choicepoints/resume column"
        continue
    fi
    printf '%s\n' "$ir_resume" | grep -E '^L[0-9]+$' | sed 's/^L/rx_L/' \
        | LC_ALL=C sort > "$d/ir.push"
    if ! diff -q "$d/c.push" "$d/ir.push" >/dev/null; then
        bad "ir-listing[$pat]: CHOICE POINTS disagree with the emitted RX_PUSH sites: $(diff "$d/c.push" "$d/ir.push" | tr '\n' ' ' | cut -c1-200)"
    else
        ok "ir-listing[$pat]: CHOICE POINTS — $(wc -l < "$d/c.push") emitted RX_PUSH site(s), each with its resume target, match the listing"
    fi

    # ---- SLOTS: the written set ------------------------------------------
    #
    # NON-VACUITY IS ASSERTED HERE, and it is the whole reason this block is
    # shaped the way it is. Both sides of this comparison are extracted by
    # pattern-matching a SPELLING: `RX_SET(<slot>` in the .c, `set <array>[n]`
    # in the listing. The emitter writes both. So a rename that moves the
    # emitter and the listing together — which is the only way to rename them
    # CORRECTLY — makes both extractions match nothing, and a bare `diff -q`
    # of two empty files PASSES. The check would then certify a listing it had
    # stopped reading.
    #
    # That is this project's recorded check-design failure (a control sharing
    # a source with the thing it controls), and [M6-READ]'s emitted-identifier
    # rename is a live occasion for it. Every pattern in PATTERNS above MUST
    # write at least one slot, so an empty extraction on either side is a
    # failure, never a pass.
    #
    # WHY "writes a slot" AND NOT "has a capturing group" (corrected 2026-09-18,
    # lane w2b, when the reach widening added the first two rows without one).
    # Slots are not only capture slots: `(?<=a|bc)x` (RX_NCAPS 1, no capturing
    # group) writes two and `(?:a|ab){2,3}+` writes one, through their rungs'
    # own cursor/counter state. The old comment and the old failure message
    # both said "this pattern has capturing groups", which was true of the
    # original eleven and is false of two of the sixteen -- and a failure
    # message is a second, undeclared claim about the space of causes
    # (coding_guide.md section 5), so it is restated rather than left to send
    # a reader hunting for a missing capture that was never there.
    #
    # The .c side also resolves SYMBOLIC slot names. [M6-READ] emits a slot
    # legend (`#define RX_SLOT_GROUP1_START 2`) and writes `RX_SET` through it,
    # so the operand is not always a literal. Reading the artifact's own
    # `#define`s keeps this check working across that change instead of
    # requiring a flag day — and an operand that resolves to NOTHING is a hard
    # failure rather than a silently dropped row, which is the same
    # anti-vacuity rule one level down.
    # `#define` lines are excluded: RX_SET's own definition line carries the
    # macro's PARAMETER name as its operand. The old numeric-only extraction
    # skipped it silently; resolving symbolic operands makes it visible, and it
    # is not a slot write.
    grep -v '^#define' "$d/gen.c" | grep -oE 'RX_SET\([A-Za-z0-9_]+' \
        | sed 's/^RX_SET(//' > "$d/c.slotops"
    : > "$d/c.slots.raw"
    unresolved=""
    while read -r op; do
        [ -n "$op" ] || continue
        case "$op" in
            ''|*[!0-9]*)
                v="$(cat "$d/gen.c" "$d/gen.h" 2>/dev/null \
                     | grep -oE "^#define +$op +[0-9]+" | awk '{print $3}' | head -1)"
                if [ -z "$v" ]; then unresolved="$unresolved $op"; else echo "$v" >> "$d/c.slots.raw"; fi
                ;;
            *) echo "$op" >> "$d/c.slots.raw" ;;
        esac
    done < "$d/c.slotops"
    LC_ALL=C sort -n -u < "$d/c.slots.raw" > "$d/c.slots"
    # [DD-8] the LISTING side is now declaration-scoped: the `program`
    # section's rows whose `op` column is exactly `set`, and the slot number
    # out of THAT row's `args`. The old form matched the two words `set
    # slot_values[` anywhere in the whole listing.
    if ! ir_prog="$(table_section_rows "$d/ir" program)" \
       || ! ir_map="$(table_awk_map -s program "$d/ir" op args)"; then
        bad "ir-listing[$pat]: could not read the listing's program section (renamed?)"
        continue
    fi
    # shellcheck disable=SC2086
    printf '%s\n' "$ir_prog" | awk -F'\t' $ir_map '$op == "set" { print $args }' \
        | sed -n 's/^slot_values\[\([0-9]*\)\].*/\1/p' | LC_ALL=C sort -n -u > "$d/ir.slots"
    if [ -n "$unresolved" ]; then
        bad "ir-listing[$pat]: SLOTS — RX_SET operand(s)$unresolved are neither a number nor a #define in the artifact; the extraction would silently drop them"
    elif [ ! -s "$d/c.slots" ]; then
        bad "ir-listing[$pat]: SLOTS — no RX_SET sites found in the emitted C, but every pattern in PATTERNS writes at least one slot (captures, or a rung's own cursor/counter state); the .c-side extraction is vacuous (did the emitted spelling change?)"
    elif [ ! -s "$d/ir.slots" ]; then
        bad "ir-listing[$pat]: SLOTS — the .c writes $(wc -l < "$d/c.slots") slot(s) but the listing-side extraction found none; the listing's wording changed and this check had stopped reading it"
    elif ! diff -q "$d/c.slots" "$d/ir.slots" >/dev/null; then
        bad "ir-listing[$pat]: SLOTS — the slots the .c writes differ from the listing's: $(diff "$d/c.slots" "$d/ir.slots" | tr '\n' ' ' | cut -c1-200)"
    else
        ok "ir-listing[$pat]: SLOTS — the $(wc -l < "$d/c.slots") slot(s) the artifact writes are exactly the ones the listing shows, both extractions non-empty"
    fi
    tot_cpush=$((tot_cpush + $(wc -l < "$d/c.push")))
    tot_ipush=$((tot_ipush + $(wc -l < "$d/ir.push")))

    # ---- header numbers --------------------------------------------------
    # RX_NCAPS lives in the .h when a header is paired (the macros are emitted
    # once per FILE, and that file is the header). Searching only the .c reads
    # an empty string and compares it against nothing — the same vacuity this
    # project keeps re-learning, and it bit run_vm_identity.sh first.
    cn="$(cat "$d/gen.c" "$d/gen.h" | grep -oE '^#define RX_NCAPS [0-9]+' | awk '{print $3}')"
    ir_n="$(table_lookup "$d/ir" summary fact caps value)" || ir_n="<unreadable>"
    # [DD-14.FB] and the SAME correction now applies to the two capacity
    # macros, for the same reason one paragraph up: they moved .c -> .h with
    # the caller-buffer sizing surface (spec §10.4), because a caller has to
    # read them before it can size a buffer for <prefix>_search_in.
    #
    # WHAT READING ONLY THE `.c` WOULD HAVE COST, stated accurately after the
    # checks critic measured it rather than as first written: the comparison
    # below would have gone RED, not vacuous — `[ -n "$cbt" ]` guards the
    # empty case explicitly and the `=` comparison against a number fails on
    # an empty string anyway. What was actually lost was the MESSAGE: the
    # failure would have read "frames  vs 1", an empty field against a
    # number, sending a reader to look for a stamping bug instead of a moved
    # macro. Fixing the source of the read is still right; the claim that it
    # was a vacuity is not, and is corrected here.
    cbt="$(cat "$d/gen.c" "$d/gen.h" | grep -oE '^#define RX_RESUME_FRAMES [0-9]+' | awk '{print $3}')"
    ctr="$(cat "$d/gen.c" "$d/gen.h" | grep -oE '^#define RX_TRAIL_FRAMES [0-9]+' | awk '{print $3}')"
    # [DD-8] THREE SUMMARY ROWS, not one sentence sub-parsed twice: the
    # capacities were `; capacities N resume frames, M trail entries` and each
    # number had to be picked out of the prose around it.
    ir_bt="$(table_lookup "$d/ir" summary fact resume-frames value)" || ir_bt="<unreadable>"
    ir_tr="$(table_lookup "$d/ir" summary fact trail-entries value)" || ir_tr="<unreadable>"
    if [ "$cn" = "$ir_n" ] && [ "$cbt" = "$ir_bt" ] && [ "$ctr" = "$ir_tr" ] \
       && [ -n "$cn" ] && [ -n "$cbt" ]; then
        ok "ir-listing[$pat]: header — RX_NCAPS/$cn, frames/$cbt, trail/$ctr agree with the artifact's own macros"
    else
        bad "ir-listing[$pat]: header disagrees with the artifact: NCAPS $cn vs $ir_n, frames $cbt vs $ir_bt, trail $ctr vs $ir_tr"
    fi

    # ---- the CAP's own counter, against the artifact ---------------------
    # PCREC_MAX_VM_RESUME_POINTS is checked against a PRE-PASS count, before a
    # byte is emitted — so the cap is only as good as that count matching what
    # the emitter goes on to write. Under-count and an artifact the cap exists
    # to stop sails through. The listing reports the pre-pass number; this
    # compares it to the RX_PUSH sites actually emitted.
    #
    # TWO CORRECTIONS, 2026-09-18, lane w2b, both FOUND BY THE REACH WIDENING
    # above and neither reachable by the original eleven patterns.
    #
    # (1) THE .c SIDE COUNTED THE WRONG THING. It was `&&rx_L<n>` anywhere in
    # the artifact, and `RX_CALL(&&rx_L<n>, ...)` has that spelling too — a
    # CALL RETURN address, which `vm_count_slots`'s own A_CALL arm
    # deliberately does NOT charge to `npush` ("the call site itself allocates
    # nothing"). So the moment module `recursion` entered this sweep the .c
    # side read 4 against a correct pre-pass of 2. It now reuses `$d/c.push`,
    # the CHOICE POINTS block's own `RX_PUSH(&&rx_L<n>` extraction, which is
    # the spelling that denotes a resume point.
    #
    # (2) THE COMPARISON WAS EQUALITY AND THE PROPERTY IS AN INEQUALITY.
    # `v->npush` is an ESTIMATE and `src/gen/emit_vm.c:7230` says so in those
    # words — it has been measured NEGATIVE on the counter rung's unbounded
    # arm, which is why the [CC-CLANG] fix stopped deriving `has_push` from
    # it. What the CAP needs is only that the estimate never runs BELOW what
    # is emitted (the pre-pass arm's own comment: "a missed `npush` lets an
    # artifact past the resume-point cap"). Equality held for the original
    # eleven by luck of population; the widened set has two witnesses where
    # the estimate is high and the artifact is correct — `(?<=a|bc)x`
    # (2 vs 1) and, measured off-sweep, `(?<!a|bc)x` (3 vs 2), against three
    # other lookbehind shapes where it is exact. Over-count is the SAFE
    # direction (the cap refuses marginally early, never late), so the
    # assertion is `pre-pass >= emitted` and an over-count is REPORTED in the
    # PASS text rather than swallowed: a reader sees the slack, and an
    # under-count — the hazard — is still a hard FAIL.
    ir_rp="$(table_lookup "$d/ir" summary fact resume-points value)" || ir_rp=""
    c_rp="$(wc -l < "$d/c.push" | tr -d ' ')"
    if [ -z "$ir_rp" ]; then
        bad "ir-listing[$pat]: the listing carries no summary 'resume-points' row at all; this comparison had nothing to read (the section or the fact was renamed?)"
    elif [ "$ir_rp" -lt "$c_rp" ]; then
        bad "ir-listing[$pat]: the cap's pre-pass counts $ir_rp resume points but the artifact emits $c_rp RX_PUSH site(s) — an UNDER-count, so PCREC_MAX_VM_RESUME_POINTS is checked against a number smaller than the program it is bounding"
    elif [ "$ir_rp" -gt "$c_rp" ]; then
        ok "ir-listing[$pat]: the cap's pre-pass count ($ir_rp) bounds the artifact's $c_rp emitted RX_PUSH site(s), with $((ir_rp - c_rp)) of estimate slack (safe direction)"
    else
        ok "ir-listing[$pat]: the cap's pre-pass count ($ir_rp resume points) equals the artifact's emitted RX_PUSH sites"
    fi

    # ---- islands / callouts: the listing's count against the ARTIFACT ----
    #
    # [ENG-ISL] STEP 1, 2026-09-03: THE ISLANDS SECTION HAS A PRODUCER NOW, so
    # this block stopped being an honest-empty assertion and became a real
    # comparison. It was `isl == 0 && the artifact contains no 'island'`, which
    # was the right shape while nothing could produce one — and the day the
    # producer landed it failed on two patterns, which is the section working
    # rather than the section breaking.
    #
    # The two terms are INDEPENDENT EMITTER SURFACES and that is the point: the
    # listing's count comes from the VE_ISLAND event stream `vm_isl_emit`
    # appends, and `RX_VM_ALT_ISLANDS` comes from `Vm.nislands`, a counter
    # `vm_alt` bumps. Neither is computed from the other, so a lowering that
    # emitted a trie without recording it (or recorded one it did not emit)
    # parts them here. The artifact TEXT is the third term, and it stays a
    # biconditional rather than a count because "the .c mentions an island" is
    # not a number.
    #
    # CALLOUTS keep the honest-empty shape: module 'callouts' still has no
    # producer, so `cal` and `art_cal` must both be 0.
    isl="$(table_lookup "$d/ir" summary fact islands value)" || isl=""
    cal="$(table_lookup "$d/ir" summary fact callout-sites value)" || cal=""
    stamp_isl="$(sed -n 's/^#define rx_VM_ALT_ISLANDS \([0-9]*\)$/\1/Ip' "$d/gen.c")"
    art_isl=0
    grep -q 'island' "$d/gen.c" && art_isl=1
    art_cal=0
    grep -qE 'rx_callout_ref [a-z_]*\(|->fn\(' "$d/gen.c" && art_cal=1
    isl_says_some=0; [ -n "$isl" ] && [ "$isl" -gt 0 ] && isl_says_some=1
    if [ "$cal" != "0" ] || [ "$art_cal" != "0" ]; then
        bad "ir-listing[$pat]: callout accounting disagrees — listing says $cal, artifact says $art_cal (module 'callouts' has no producer, so both must be 0)"
    elif [ -z "$stamp_isl" ]; then
        bad "ir-listing[$pat]: the artifact carries no RX_VM_ALT_ISLANDS stamp — it is UNCONDITIONAL on every VM artifact (docs/spec/match_api.md 6.3)"
    elif [ "$isl" != "$stamp_isl" ]; then
        bad "ir-listing[$pat]: the listing counts $isl islands and the artifact stamps $stamp_isl — the VE_ISLAND event stream and Vm.nislands disagree about what was emitted"
    elif [ "$isl_says_some" != "$art_isl" ]; then
        if [ "$isl_says_some" = "1" ]; then
            bad "ir-listing[$pat]: the listing reports $isl island(s) but the artifact text contains no island at all — the count and the emitted C disagree"
        else
            bad "ir-listing[$pat]: the listing reports 0 islands but the artifact text DOES contain one — the count and the emitted C disagree"
        fi
    elif [ "$isl" = "0" ]; then
        ok "ir-listing[$pat]: ISLANDS/CALLOUTS — the listing reports 0 of each, the stamp agrees and the artifact contains neither (honestly empty, not blanked)"
    else
        ok "ir-listing[$pat]: the listing's $isl island(s) match the artifact's own RX_VM_ALT_ISLANDS stamp and its emitted text"
    fi

    # ---- [DD-8] THE LISTING CONFORMS TO ITS OWN CONTRACT ------------------
    #
    # `--emit-ir` is a docs/spec/table_contract.md producer now, and the
    # contract's own HEADER TRUTHFULNESS check ("every data row's field count
    # equals its section's declared count") is what stops a cell from
    # swallowing a TAB and silently re-shaping a row. Asserted PER SECTION,
    # over the full declared section set, because a section that vanished
    # entirely is the failure mode a per-file check cannot see: table.sh
    # fails loudly on an absent section, so a renamed one is RED here rather
    # than quietly unchecked. The SET is spelled out rather than discovered
    # from the file for the same reason — discovering it from the producer
    # would make this check agree with any producer, which is the
    # control-shares-a-source-with-what-it-controls shape.
    ir_contract_ok=1
    for sec in summary slots rungs strategies pruning program choicepoints islands callouts; do
        if ! table_check_truthfulness "$d/ir" "$sec" >/dev/null 2>&1; then
            bad "ir-listing[$pat]: section '$sec' is absent or has a row whose field count disagrees with its own header (docs/spec/table_contract.md, HEADER TRUTHFULNESS)"
            ir_contract_ok=0
        fi
    done
    [ "$ir_contract_ok" = "1" ] && ok "ir-listing[$pat]: all 9 declared sections present and header-truthful (docs/spec/ir_listing.md)"

    # ---- [REVW.1] wave 1 stage 0: THE irsb BYTE-NEUTRALITY ARM ------------
    #
    # WHY THIS EXISTS. emitvm_second_pass.md §1/§5 (EP2): `vm_render_listing`
    # writes `&job->irsb` (the --emit-ir listing), a DIFFERENT byte stream
    # from the `.c` artifact the four standing identity gates and the
    # full-corpus emit-diff compare — none of those gates sees `irsb`. Wave 2
    # (not built here) moves emitter interior text around; a stage-3 lane's
    # "byte-neutral" claim about `irsb` is unverifiable without a control that
    # predates the move. This arm IS that control: it pins this listing's own
    # bytes, PER PATTERN, at this wave's branch point, so a later diff is
    # against a real prior state rather than against nothing.
    #
    # PINS THE OUTPUT, NOT THE MECHANISM (D108): the comparison is the
    # listing's raw bytes end to end — no section is parsed, no call
    # structure is assumed — so it stays valid across the future
    # walk->event->render seam the kit is chartered to become.
    #
    # CAPTURE_IR_BASELINE=1 (opt-in, this lane's own use, and any future
    # DELIBERATE re-baseline — never run casually): (re)writes the baseline
    # file instead of comparing. Default: compares, and a MISSING baseline is
    # a hard FAIL naming the file to capture, never a silent skip (K35 shape
    # — a check that shrugs at an absent baseline certifies nothing).
    ir_base_dir="$ROOT_DIR/tests/codegen/manifests/ir_listing_baseline"
    ir_base_id="$(printf '%s' "$pat" | md5sum | cut -c1-8)"
    ir_base_file="$ir_base_dir/$ir_base_id.ir"
    if [ "${CAPTURE_IR_BASELINE:-0}" = "1" ]; then
        mkdir -p "$ir_base_dir"
        cp "$d/ir" "$ir_base_file"
        ok "ir-listing[$pat]: BYTE-NEUTRALITY baseline captured -> $ir_base_file"
    elif [ ! -f "$ir_base_file" ]; then
        bad "ir-listing[$pat]: BYTE-NEUTRALITY — no baseline at $ir_base_file; re-run with CAPTURE_IR_BASELINE=1 to create one deliberately (never silently)"
    elif diff -q "$ir_base_file" "$d/ir" >/dev/null; then
        ok "ir-listing[$pat]: BYTE-NEUTRALITY — the listing is byte-identical to its stage-0 baseline"
    else
        bad "ir-listing[$pat]: BYTE-NEUTRALITY — the listing MOVED against its stage-0 baseline ($ir_base_file): $(diff "$ir_base_file" "$d/ir" | head -6 | tr '\n' ' ' | cut -c1-300)"
    fi
done

# ---- CHOICE POINTS: the sweep-wide non-vacuity guard --------------------
# See the note at tot_cpush's declaration. Both spellings (`RX_PUSH(&&rx_L<n>`
# in the .c, `resume L<n>` in the listing) are emitter-written, so a rename
# that moves them together empties BOTH sides and every per-pattern diff -q
# above passes on two empty files.
if [ "$tot_cpush" -eq 0 ] || [ "$tot_ipush" -eq 0 ]; then
    bad "ir-listing: CHOICE POINTS — the sweep found $tot_cpush emitted RX_PUSH site(s) and $tot_ipush listing resume target(s); zero on either side means the extraction stopped matching, so every per-pattern comparison above was two empty files"
else
    ok "ir-listing: CHOICE POINTS — the sweep's extractions are non-empty ($tot_cpush emitted push sites, $tot_ipush listing resume targets), so the per-pattern comparisons above compared something"
fi

# ---- PCREC_MAX_VM_REPEAT_COPIES, at its boundary ------------------------
#
# D45's consequence 1: PCREC_MAX_VM_NODES let ((a)|b){0,4000}c emit 3.5 MB.
# The replication cap is the compiler-side bound that stops it. Checked at the
# boundary in BOTH directions, because a cap that refuses everything and a cap
# that refuses nothing both pass a one-sided test.
#
# EVERY ROW BELOW NOW PASSES `-fno-revdet`, and the reason is the endgame rather
# than an inconvenience ([ENG-BREP] rung-select, 2026-08-16). The cap bounds the
# REPLICATION STRATEGY, and `((a)|b){0,N}c` is no longer replicated: the
# reverse-deterministic rung emits it as one body copy at 293 lines whatever N
# is, so at the default it sails past a cap that has nothing to count. Denying
# the rung puts the quantifier back on the frames rung, which is where
# replication — and therefore the cap — lives. That is D46's pin-the-selection
# rule, and it keeps this block testing the cap instead of testing which rung
# won. The endgame itself is asserted separately, below.
#
# `-fno-counter` joins it (2026-08-17, the counter-K landing) by the same rule
# one rung further down: counter-K also replaces replication for this shape, so
# a cap that COUNTS REPLICATED COPIES cannot be tested by a build that does not
# replicate. Both denials are needed, not either — with only one, the other rung
# absorbs the shape and every assertion below goes quiet in the direction that
# reads as PASS for the 64-copy cell and FAIL for the two refusal cells.
if pcrec_run "$PCREC" -p rx -fno-revdet -fno-counter -o "$WORKDIR/cap_ok.c" -- '((a)|b){0,64}c' >/dev/null 2>&1; then
    ok "[M4.5c] the replication cap ADMITS the largest legal artifact (64 copies, $(stat -c %s "$WORKDIR/cap_ok.c") bytes)"
else
    bad "[M4.5c] '((a)|b){0,64}c' was refused under -fno-revdet -fno-counter; it is exactly at the cap and must compile"
fi
if out="$(pcrec_run "$PCREC" -p rx -fno-revdet -fno-counter -o "$WORKDIR/cap_no.c" -- '((a)|b){0,65}c' 2>&1)"; then
    bad "[M4.5c] '((a)|b){0,65}c' compiled under -fno-revdet -fno-counter; it is one copy over the cap and must be refused"
elif printf '%s' "$out" | grep -q 'replicate its body 65 times' \
     && printf '%s' "$out" | grep -q 'span loop'; then
    ok "[M4.5c] ...and REFUSES one copy over it, naming the count, the limit and the way out"
else
    bad "[M4.5c] refused over the cap, but the diagnostic does not name the count and the fix: $out"
fi
# the case D45 was ruled over
if pcrec_run "$PCREC" -p rx -fno-revdet -fno-counter -o "$WORKDIR/cap_d45.c" -- '((a)|b){0,4000}c' >/dev/null 2>&1; then
    bad "[M4.5c] '((a)|b){0,4000}c' still compiles under -fno-revdet -fno-counter — this is the 3.5 MB artifact that pegged cc1 for 100+ minutes (D45)"
else
    ok "[M4.5c] '((a)|b){0,4000}c' — D45's own case — is refused before emitting anything, whenever replication is the strategy"
fi
#
# ---- D47.1's ENDGAME, now that it has arrived ---------------------------
#
# D45's follow-up said the emitted-size cap was an INTERIM backstop and named
# [ENG-BREP]'s ladder as the endgame; D47.1 named this rung specifically. So the
# same pattern that must be REFUSED under replication must COMPILE at the
# default, small, and the two facts belong next to each other — a reader who
# sees only the refusal above would reasonably conclude pcrec still cannot do
# this.
# THE ASSERTION IS COUNT-INDEPENDENCE, NOT A CEILING (2026-08-26): `lines <
# 2000` was a magic number the default (auto: VM + inlined hybrid prefilter)
# artifact reached EXACTLY on the day three abi events added scaffolding
# (the tier entries, the selection stamps, two rx_info fields) — a ceiling
# measures the scaffolding's growth, not the rung's claim. The claim is that
# the rung emits ONE body copy, so `{0,4000}` must be the same size as
# `{0,400}` (a tolerance of 2 lines for a wider count literal in a comment).
# …AND the comparison is made with the PREFILTER DENIED (`-fno-prefilter`, an
# answer-identity-preserving axis), because the DEFAULT artifact's size DOES
# grow with the count: the hybrid's inlined DFA prefilter carries the bounded
# repeat (869 → 1,994 lines for {0,400} → {0,4000} at 32890e2, before any of
# today's scaffolding) — a pre-existing cost the old ceiling hid by slack
# (K39).
#
# **[OPT-4], 2026-08-29: THE AUTO SIZES ARE ASSERTED, NOT PRINTED — AND UNDER
# RULING B THE DEFAULT IS THE ONE THAT GROWS.** Frank's ruling B (2026-08-29
# evening, docs/design/prefilter_count_independence.md §10a) made the EXACT
# prefilter the default: the count-collapsed language is a ladder RESCUE only
# (a state cap or a size cap refused the exact machine), never a knee. So K39
# is RE-SCOPED, not fixed: at the default the hybrid's inlined prefilter
# carries the bounded repeat and the artifact is count-BOUNDED (by the caps),
# while `-fprefilter-collapse` is where count-INDEPENDENCE lives. Both halves
# are asserted here on the SPLIT (`-o FILE`) artifact, which is a different
# emitted shape from the self-contained one
# `tests/codegen/run_prefilter_collapse.sh` §1 asserts on — and each half is
# the other's control: a compiler that stopped emitting a prefilter at all
# would make the default pair EQUAL (caught below), and one that collapsed at
# the default (a knee coming back) would too. The first version of this block
# asserted ruling A (the default count-independent above a knee) and went red
# in union battery 3 (2026-08-30: 2,809 vs 1,009 lines) — the assertion was
# stale, not the compiler.
if pcrec_run "$PCREC" -p rx -o "$WORKDIR/endgame_auto.c" -- '((a)|b){0,4000}c' >/dev/null 2>&1 \
   && pcrec_run "$PCREC" -p rx -o "$WORKDIR/endgame_auto_small.c" -- '((a)|b){0,400}c' >/dev/null 2>&1; then
    eg_auto_big="$(wc -l < "$WORKDIR/endgame_auto.c")"
    eg_auto_small="$(wc -l < "$WORKDIR/endgame_auto_small.c")"
    eg_auto_delta=$(( eg_auto_big > eg_auto_small ? eg_auto_big - eg_auto_small : eg_auto_small - eg_auto_big ))
    [ "$eg_auto_delta" -gt 2 ] \
        && ok "[K39] the DEFAULT split artifact is count-BOUNDED, not count-independent (ruling B): {0,400} $eg_auto_small lines, {0,4000} $eg_auto_big (delta $eg_auto_delta) — the exact prefilter carries the count, as ruled" \
        || bad "[K39] the DEFAULT split artifact emitted $eg_auto_big lines for {0,4000} against $eg_auto_small for {0,400} (delta $eg_auto_delta <= 2) — either a knee is back (ruling B forbids collapsing at the default) or no prefilter is being emitted at all"
else
    bad "[K39] '((a)|b){0,400}c' or '((a)|b){0,4000}c' does not compile at the DEFAULT engine"
fi
if pcrec_run "$PCREC" -p rx -fprefilter-collapse -o "$WORKDIR/endgame_force.c" -- '((a)|b){0,4000}c' >/dev/null 2>&1 \
   && pcrec_run "$PCREC" -p rx -fprefilter-collapse -o "$WORKDIR/endgame_force_small.c" -- '((a)|b){0,400}c' >/dev/null 2>&1; then
    eg_force_big="$(wc -l < "$WORKDIR/endgame_force.c")"
    eg_force_small="$(wc -l < "$WORKDIR/endgame_force_small.c")"
    eg_force_delta=$(( eg_force_big > eg_force_small ? eg_force_big - eg_force_small : eg_force_small - eg_force_big ))
    [ "$eg_force_delta" -le 2 ] \
        && ok "[K39] the -fprefilter-collapse split artifact is count-INDEPENDENT: {0,400} $eg_force_small lines, {0,4000} $eg_force_big (delta $eg_force_delta) — the collapsed prefilter drops the count" \
        || bad "[K39] under -fprefilter-collapse the split artifact emitted $eg_force_big lines for {0,4000} against $eg_force_small for {0,400} (delta $eg_force_delta > 2) — the forced collapse is scaling with the count again"
else
    bad "[K39] '((a)|b){0,400}c' or '((a)|b){0,4000}c' does not compile under -fprefilter-collapse"
fi
if pcrec_run "$PCREC" -p rx -fno-prefilter -o "$WORKDIR/endgame.c" -- '((a)|b){0,4000}c' >/dev/null 2>&1 \
   && pcrec_run "$PCREC" -p rx -fno-prefilter -o "$WORKDIR/endgame_small.c" -- '((a)|b){0,400}c' >/dev/null 2>&1; then
    eg_lines="$(wc -l < "$WORKDIR/endgame.c")"; eg_small="$(wc -l < "$WORKDIR/endgame_small.c")"
    eg_delta=$(( eg_lines > eg_small ? eg_lines - eg_small : eg_small - eg_lines ))
    if [ "$eg_delta" -le 2 ]; then
        ok "[ENG-BREP] D45's endgame: {0,4000} compiles (prefilter denied) in $eg_lines lines and {0,400} in $eg_small (delta $eg_delta) — the reverse-deterministic rung emits one body copy, so the count stops driving the size)"
    else
        bad "[ENG-BREP] '((a)|b){0,4000}c' emitted $eg_lines lines vs $eg_small for {0,400} (delta $eg_delta > 2) — the rung is meant to make the count irrelevant to the emitted size"
    fi
else
    bad "[ENG-BREP] '((a)|b){0,4000}c' does not compile at the default; D47.1 names this rung's arrival as when D45's refuse-cap endgame lands"
fi
#
# ...and the cap must NOT refuse a pattern whose size is PROPORTIONATE to what
# its author wrote. A first draft capped TOTAL resume points instead of
# replication and refused a 200-branch capture-bearing keyword alternation —
# 199 resume points, and MEASURED 0.50 s at -O2 for the 100-branch version, so
# nothing about it is pathological. The defect is disproportion, not size, and
# a cap that cannot tell them apart refuses the wrong patterns.
wide="($(python3 -c "print('|'.join('kw%d' % i for i in range(500)))"))"
if pcrec_run "$PCREC" -p rx -o "$WORKDIR/wide.c" -- "$wide" >/dev/null 2>&1; then
    ok "[M4.5c] a 500-branch capture-bearing alternation still compiles — the cap targets REPLICATION, not size"
else
    bad "[M4.5c] a 500-branch capture-bearing alternation was refused; its size is proportionate to the pattern and the cap must not bite it"
fi
# a single-path body never replicates, whatever the count (S2.5's cursor rung)
if pcrec_run "$PCREC" -p rx -o "$WORKDIR/span.c" -- '(ab){0,4000}c' >/dev/null 2>&1; then
    ok "[M4.5c] '(ab){0,4000}c' compiles: a single-path body takes the span-loop rung and replicates nothing"
else
    bad "[M4.5c] '(ab){0,4000}c' was refused; it has no choice point, so the cap must not see it"
fi

# ---- a NON-DEFAULT --prefix ---------------------------------------------
#
# Every check above uses the default `rx`, which cannot see a hardcoded `RX_`
# in the listing's own text — and there was one: the header named RX_NCAPS
# whatever --prefix said, pointing a reader of a `-p myrx` listing at a macro
# the artifact does not contain. Cheap to check, invisible without it.
mkdir -p "$WORKDIR/pfx"
if pcrec_run "$PCREC" -p myrx -o "$WORKDIR/pfx/gen.c" -- '(a)b' >/dev/null 2>&1    && pcrec_run "$PCREC" -p myrx --emit-ir -- '(a)b' > "$WORKDIR/pfx/ir" 2>&1; then
    if grep -qE '(^|[^A-Z_])RX_' "$WORKDIR/pfx/ir"; then
        bad "[M4.5c] a -p myrx listing still names RX_* macros: $(grep -m1 'RX_' "$WORKDIR/pfx/ir")"
    elif grep -q 'MYRX_NCAPS' "$WORKDIR/pfx/ir"          && grep -q '^#define MYRX_NCAPS' "$WORKDIR/pfx/gen.c" "$WORKDIR/pfx/gen.h"; then
        ok "[M4.5c] the listing names the artifact's OWN macros under a non-default --prefix"
    else
        bad "[M4.5c] a -p myrx listing does not name MYRX_NCAPS, or the artifact does not define it"
    fi
    # the label set must still line up under a different prefix
    grep -oE '^myrx_L[0-9]+:' "$WORKDIR/pfx/gen.c" | tr -d ':' | LC_ALL=C sort > "$WORKDIR/pfx/c.l"
    ir_labels "$WORKDIR/pfx/ir" myrx > "$WORKDIR/pfx/i.l" || : > "$WORKDIR/pfx/i.l"
    if [ -s "$WORKDIR/pfx/c.l" ] && diff -q "$WORKDIR/pfx/c.l" "$WORKDIR/pfx/i.l" >/dev/null; then
        ok "[M4.5c] ...and its label set matches the artifact's too"
    else
        bad "[M4.5c] -p myrx: label sets differ between the .c and the listing"
    fi
else
    bad "[M4.5c] could not produce a -p myrx artifact and listing"
fi

# ---- the DFA refusal (an as-built decision, so it is pinned) -------------
if out="$(pcrec_run "$PCREC" -p rx --emit-ir -- 'abc' 2>&1)"; then
    bad "[M4.5c] --emit-ir on a pure-DFA artifact PRINTED a listing; there is no VM program to list"
elif printf '%s' "$out" | grep -q -- '--engine=vm'; then
    ok "[M4.5c] --emit-ir on a capture-free pattern refuses cleanly and names --engine=vm as the way to see a VM program"
else
    bad "[M4.5c] --emit-ir refused a capture-free pattern but the message names no way forward: $out"
fi
if pcrec_run "$PCREC" -p rx --emit-ir --engine=vm -- 'abc' >/dev/null 2>&1; then
    ok "[M4.5c] ...and that named way forward works"
else
    bad "[M4.5c] --emit-ir --engine=vm was refused too — the diagnostic's advice does not work"
fi
if pcrec_run "$PCREC" -p rx --emit-ir -o "$WORKDIR/x.c" -- '(a)' >/dev/null 2>&1; then
    bad "[M4.5c] --emit-ir accepted -o; it is a query and emits no C"
else
    ok "[M4.5c] --emit-ir takes no -o (a query, not a compile)"
fi

# ---- the TRACE takes the same path as the untraced build ----------------
#
# The traced artifact's own source comment claims it does. That claim is the
# whole value of the tool — a debug build that changes the answer is worse
# than no debug build — so it is checked rather than asserted, over subjects
# that exercise both a match and a no-match with real backtracking.
trace_ok=1
for pat in '(a|ab)(c|bcd)' '((a)|b)+c' '(a*)b'; do
    d="$WORKDIR/tr$(printf '%s' "$pat" | md5sum | cut -c1-6)"
    mkdir -p "$d/plain" "$d/traced"
    pcrec_run "$PCREC" -p rx --emit-main -o "$d/plain/gen.c" -- "$pat" >/dev/null 2>&1 || { trace_ok=0; break; }
    pcrec_run "$PCREC" -p rx --trace --emit-main -o "$d/traced/gen.c" -- "$pat" >/dev/null 2>&1 || { trace_ok=0; break; }
    # shellcheck disable=SC2086
    gen_cc "trace plain '$pat'" "$CC" $GENCFLAGS -I "$d/plain" -o "$d/plain/t" "$d/plain/gen.c" \
        || { trace_ok=0; echo "  trace: plain build failed: $(printf '%s' "$GEN_CC_LOG" | head -3)" >&2; break; }
    # shellcheck disable=SC2086
    gen_cc "trace TRACED '$pat'" "$CC" $GENCFLAGS -I "$d/traced" -o "$d/traced/t" "$d/traced/gen.c" \
        || { trace_ok=0; echo "  trace: TRACED build failed: $(printf '%s' "$GEN_CC_LOG" | head -3)" >&2; break; }
    for subj in abcd xxabcd aab bbb '' a aaa; do
        p_out="$(gen_run "ir-listing trace plain '$pat' '$subj'" "$d/plain/t" "$subj" 2>/dev/null)"
        t_out="$(gen_run "ir-listing trace TRACED '$pat' '$subj'" "$d/traced/t" "$subj" 2>/dev/null)"
        if [ "$p_out" != "$t_out" ]; then
            bad "[M4.5c] --trace CHANGED THE ANSWER for '$pat' on \"$subj\": plain '$p_out' vs traced '$t_out'"
            trace_ok=0
        fi
    done
    # ...and it must actually trace: a silent "instrumented" build is the
    # vacuous-check shape (the trace fires on stderr, the result on stdout).
    if ! gen_run "ir-listing trace stderr TRACED '$pat'" "$d/traced/t" abcd 2>&1 >/dev/null | grep -q '^\[rx\] '; then
        bad "[M4.5c] --trace produced no trace output for '$pat' — the instrumentation is not live"
        trace_ok=0
    fi
    if gen_run "ir-listing trace stderr plain '$pat'" "$d/plain/t" abcd 2>&1 >/dev/null | grep -q '^\[rx\] '; then
        bad "[M4.5c] the PLAIN artifact for '$pat' emitted trace output — --trace is not opt-in"
        trace_ok=0
    fi
done
[ "$trace_ok" = "1" ] && ok "[M4.5c] --trace: 3 patterns x 7 subjects — the instrumented artifact agrees with the plain one on every answer, traces on stderr, and the plain artifact traces nothing"

# A traced artifact must SAY it is traced (the D37 artifact-stamp principle:
# no artifact is ambiguous about what it was built with).
if pcrec_run "$PCREC" -p rx --trace -o "$WORKDIR/st.c" -- '(a)b' >/dev/null 2>&1; then
    if grep -q '^#define RX_TRACE 1$' "$WORKDIR/st.c" \
       && grep -q 'TRACED ARTIFACT' "$WORKDIR/st.c"; then
        ok "[M4.5c] a traced artifact stamps RX_TRACE and says so in prose (D37: no artifact is ambiguous about what it was built with)"
    else
        bad "[M4.5c] a traced artifact carries no stamp saying so"
    fi
else
    bad "[M4.5c] could not compile a traced artifact"
fi

echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
if [ $((pass + fail)) -eq 0 ]; then
    echo "ir-listing: NO CHECKS RAN" >&2; exit 1
fi
[ "$fail" -eq 0 ] && exit 0
exit 1
