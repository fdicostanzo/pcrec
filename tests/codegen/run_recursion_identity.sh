#!/usr/bin/env bash
# tests/codegen/run_recursion_identity.sh — [DD-14]'s BYTE-IDENTITY GATE,
# GROWN TO ITS FOUR AXES at wave E (design subroutines_design.md §9.1, §11
# wave E). Wave D landed the DEFAULT-axis seed with the note that wave E was
# expected to GROW this file rather than replace it; this is that growth —
# the seed's reference, pin, classifier and positive control are unchanged in
# kind, and what wave E added is the other three axes, the D37 stamp strip,
# the per-axis positive control, and the classifier's own self-test.
#
# THE SECOND CONTROL (§9.2's SPLICE-vs-LINKAGE `A == B` over the corpus) is
# NOT here: it compares ANSWERS rather than bytes, so it lives in
# `tests/recursion/run_recursion_diff.sh` §5, which has the subject grid. What
# wave G added HERE is the FIFTH AXIS — `-fno-splice-calls` — for the reason
# every other axis exists: the flag reaches `select_engine.c`, which every
# pattern goes through, and an axis that pins the linkage constant is the one
# that localises a wrong eligibility rule.
#
# THE CLAIM. A CALL-FREE pattern's emitted C is byte-identical before and
# after module `recursion`'s two doorways (the `(?` family, wave B+C; the
# `\g<`/`\g'` family, wave D) — `run_atomic_identity.sh`'s shape and its
# reasoning transfers exactly: the module adds a node kind (`A_CALL`)
# nothing constructs for a call-free pattern, a call graph pass that returns
# immediately when `pcrec_has_call` is false, and emitter machinery gated on
# the same predicate. There is no refined alphabet and no interned state for
# a call-free pattern to pay for.
#
# WHY THE REFERENCE IS A PINNED COMMIT AND NOT A `-D` KNOB: this module has
# no stage a knob could sit on (`run_atomic_identity.sh`'s own argument,
# verbatim) — the whole surface is "is there an `A_CALL` in the tree", which
# is FALSE for every pre-module pattern, so a knob would gate code that never
# runs on the population under test and the sweep would report 100%
# identical no matter what was sabotaged. The reference is therefore built
# from a PINNED PRE-MODULE COMMIT via `git archive`, sharing NO SOURCES with
# the subject.
#
# THE PIN IS `ac4917d` (docs/dev/dev_journal.md: "WAVE A2 MERGED"), NOT a
# commit before [DD-14] existed at all: it is the last commit whose `src/`
# carries `A_CALL` the KIND with NO PRODUCER anywhere reachable — wave A2
# landed the tagged-union member and the walker arms, wave B+C's ports and
# wave D's `\g` wiring both come after it. Verified below (no registry row
# in that tree has a wired `aport` for any of the nine call spellings) rather
# than merely asserted.
#
# NO RETIREMENT GUARD, DELIBERATELY, UNLIKE ITS THREE SIBLINGS
# (`run_backref_identity.sh`, `run_lookaround_identity.sh`, and the guard's
# own comment in each). Those three predate [DD-14] wave A's ABI event
# (`PCREC_ERR_RECURSE`/`ERR_FLOOR` -4->-5/`PCREC_ERR_INTERNAL`, main 0c75c96)
# and cannot be moved past it — no pin before that commit can ever again be
# byte-identical to a subject tree that carries it, because the event changed
# every artifact's `#define` block unconditionally. THIS gate's pin is POST
# that event BY CONSTRUCTION: `ac4917d` already contains `PCREC_ERR_INTERNAL`
# (0c75c96 is its own ancestor, verified below), so the ABI event is already
# baked into both sides of every comparison this script makes and cannot be
# the thing that retires it. A future ABI-breaking event past `ac4917d` would
# need its own guard; this one does not need one yet.
#
# THE POSITIVE CONTROL IS THE REFUSAL-MISMATCH COLUMN, `run_atomic_identity.
# sh`'s shape exactly: the reference compiler cannot compile ANY of the nine
# call spellings — it refuses with "requires module 'recursion'" for every
# one, `\g<`/`\g'` included, since neither doorway has a producer in that
# tree — so a run reporting zero differing AND zero refusal mismatches has
# either lost its call-bearing population or is comparing two builds of the
# same tree. Both populations are asserted EXACT, from a run.
#
# FOUR AXES (§9.1, mirroring the [M6.6.2] ASK 4 ruling because the reasoning
# transfers exactly):
#
#   default          the standard first.
#   --engine=vm      the standard second.
#   -fno-prefilter   §8.2 forces the prefilter OFF for a CALL-BEARING pattern,
#                    and that is a touch on `select_engine.c`, which EVERY
#                    pattern goes through. The axis that pins the prefilter
#                    constant is the one that localises a wrong predicate: a
#                    conjunct that over-fires (forcing the prefilter off for
#                    call-FREE patterns too) moves bytes on the default axis
#                    and moves NOTHING here, and the pair of readings names
#                    the failure where either alone would only report it.
#   --no-captures    §4.3 edits `pcrec_bref_mark`'s union, which is
#                    `--no-captures`' own machinery (P10) — the
#                    backrefs-precedent axis, and here it is not ceremonial:
#                    a mark-set edit that OVER-marks makes `--no-captures`
#                    keep slots it used to delete, and only this axis sees it.
#   -fno-splice-calls  [DD-14 wave G]. §6.3's eligibility rule sets
#                    `Ast.u.call.link`, and `select_engine.c` reads it twice —
#                    for the VM-only verdict and for the prefilter. Both reads
#                    are on the path EVERY pattern takes, so a rule that
#                    answered SPLICE for something it should not would move
#                    bytes on the default axis and move nothing here, and the
#                    pair of readings names the failure where either alone
#                    would only report it. It is also the axis that pins the
#                    ELISION population below: the four patterns move on
#                    `default` and on `--engine=vm` (where the WHY stamp
#                    changes) and are asserted on every axis.
#
# ============================================================================
# THE ONE POPULATION WAVE G IS ALLOWED TO MOVE, NAMED HERE AND ASSERTED EXACT
# ============================================================================
# THE CLAIM ABOVE — "a call-free pattern's emitted C is byte-identical" — IS NO
# LONGER TRUE FOR FOUR PATTERNS, and that is a ruling, not a leak.
#
# Wave G's DEAD-CAPTURE ELISION (`pcrec_has_live_capture`, src/opt/atomic.c)
# says a capture group NO EMITTED CODE CAN WRITE does not force the
# capture-recording engine. The structural fact is `A_REP{0,0}` emitting
# nothing, and `(?(DEFINE)...)`, `(?:...){0}` and `(a){0}b` are that same fact
# three times — so the rule is stated over the fact and NOT over the module,
# which means it fires on patterns carrying no call at all. Those patterns move
# from the VM to the DFA. Their ANSWERS and their CAPTURES do not move: `(a){0}`
# on "a" is `rc=1 ncaps=2 g0=(0,0) g1=(-1,-1)` on both compilers, which is what
# libpcre2 10.46 reports.
#
# GATING THE ELISION ON `pcrec_has_call` WOULD HAVE KEPT THIS FILE AT ZERO and
# was rejected: it would make a `recursion` special case out of a fact that is
# not about `recursion` (Frank's 2026-08-23 general-mechanism rule).
#
# SO THE EXCEPTION IS NAMED, NOT FILTERED, AND IT IS ASSERTED IN BOTH
# DIRECTIONS — every pattern in the list MUST differ (a stale list is a list
# that has stopped defending anything) and nothing outside it may. That is the
# difference between an exception and the check-design failure this project has
# recorded twice: a filter hides whatever else lands in it.
ELIDED_PATTERNS='(a){0}
(a){0,0}b
(()|$){0}b
(()|^){0}[b]'
#
# THE D37 FEATURE STAMP IS COMPARED PAST, `run_backref_identity.sh`'s
# treatment and `tests/cli` case10's precedent before it. THE FILTER IS
# ASSERTED, NOT TRUSTED: exactly three stamp lines must be removed from each
# side, so a filter that silently matched nothing (leaving a difference in) or
# matched too much (hiding a real one) is a named failure rather than a
# quieter sweep. AND THE STRIP IS NOT A BLIND SPOT HERE: the comparison is
# made TWICE — raw and stripped — and `stamp-moved` counts the pairs that
# differ RAW and agree STRIPPED, i.e. exactly the artifacts whose only
# difference is the stamp. It is 0 today (MEASURED at wave E) because module
# `recursion`'s registry rows PREDATE the module — P4 measured all 26 as
# VM_ONLY before any producer existed — so `render_modules`' first-row walk
# never moved the name, unlike `backrefs`, whose two new `RK_ESC 'g'` rows DID
# move it and whose gate therefore had to drop the stamp entirely. A wave that
# legitimately moves the stamp (wave F adds registry rows) will see this
# number go nonzero and must say so in its commit; it is a FAILURE here rather
# than a note, because "the stamp moved" is a claim that deserves a reader.
#
# THE POSITIVE CONTROL RUNS ON EVERY AXIS, not once. §9.2's control is that
# the pre-module reference REFUSES every call-bearing pattern, and "refuses"
# is an answer the axis flags could in principle change — `--no-captures` and
# `-fno-prefilter` both reach `select_engine.c`, where a refusal lives.
# Running it once would pin the default axis and assume the other three.
#
# THE CLASSIFIER MASKS CHARACTER CLASSES (design §9.1's own rule:
# `tests/backrefs/octal_class.rxt`'s `^[\g<1>]$` is not a call) and covers
# BOTH doorways: `\g<`/`\g'` outside a class, and a `(?` construct whose tail
# is NOT one of the twelve NAMED non-call shapes — `(?:`, `(?=`, `(?!`,
# `(?*`, `(?<=`/`(?<!`/`(?<*` (lookbehind), `(?<name>` (named group), `(?'`
# (named group, quoted), `(?P<` (named group), `(?P=` (backref by name),
# `(?>` (atomic group, module `atomic-groups`' doorway), `(?#` (comment),
# `(?(` (conditional) EXCEPT `(?(DEFINE)`, which is this module's since
# wave F, and an inline-option run (leading letter, `^` or
# `-`). FAILS SAFE TOWARD THE CALL BUCKET, `run_atomic_
# identity.sh`'s and `lookaround_classify.py`'s shared rule: an unrecognised
# `(?` tail is classified call-bearing, which only costs a pattern from the
# identity population rather than silently admitting one that should have
# been excluded.
#
# Usage: bash tests/codegen/run_recursion_identity.sh
# Env: PCREC (default <root>/build/pcrec), CC, KEEP=1, SANFLAGS,
#      RECURSION_IDENTITY_REF=<sha> to move the base.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "${ROOT_DIR}/tests/lib/gen_timeout.sh"  # [K37] pcrec_run
CC="${CC:-gcc}"
SANFLAGS="${SANFLAGS:-}"
KEEP="${KEEP:-0}"

# ===========================================================================
# [DD-14.FB] THIS GATE IS NOW **TWO COMPARISONS**, NOT ONE, AND THE SPLIT IS
# A RULING (manager, 2026-08-25) RATHER THAN A CONVENIENCE.
# ===========================================================================
#
# WHAT FORCED IT. [DD-14.FB] (D71 item 2, the caller-provided frame buffer)
# is UNCONDITIONAL emitter surgery: every artifact pcrec emits gains five
# sizing macros, three `_in` entry declarations, two element typedefs, three
# `_Static_assert`s, a `<prefix>_run_buffers` type, a `<prefix>_run_state_bind`
# helper and four `rx_info` fields at `abi` 2 -> 3, and its run state's two
# inline arrays become pointer/capacity pairs. Against a PRE-FB reference,
# EVERY artifact differs. That is an announced pre-v1 boundary (D40 regime 1),
# not a regression -- but it means a whole-file comparison against `ac4917d`
# can never be green again.
#
# WHY LINE-LEVEL STRIPPING WAS TRIED AND REJECTED -- MEASURED, so the next
# reader does not re-derive it. The obvious repair is to widen `stamp_strip`
# with named exact patterns for the FB surface. Measured across eight
# call-free patterns spanning this gate's axes: **30 distinct old-side lines
# and 180 distinct new-side lines, 200 in total** (69 of the added ones are
# comment lines, 111 code). It fails TWO ways:
#
#   1. IT OVER-STRIPS, and one over-strip is the compatibility promise
#      itself. Built from that diff, the filter necessarily contains
#      `ptrdiff_t rx_match(const rx_ctx *ctx)` and
#      `ptrdiff_t rx_match_caps(const rx_ctx *ctx, ptrdiff_t (*capture_spans_out)[2])`
#      -- the two anchored entry signatures moved when their bodies became
#      statics -- along with ` *` (14 occurrences per artifact), `}`, `{` and
#      `typedef struct {`. A gate that strips those has stopped seeing a
#      change to the very declarations `docs/spec/match_api.md` §10.8
#      promises are unchanged.
#   2. IT STILL UNDER-COVERS: with all 200 applied, a DFA artifact was still
#      5 lines apart and a VM artifact 12 -- BLANK lines, position-dependent,
#      which no whole-line pattern removes without removing every blank line
#      in the file.
#
# That is the "a gate that FILTERS its way to identity" failure this project
# has recorded twice, so it is not built.
#
# ---------------------------------------------------------------------------
# (A) THE PROGRAM REGION, against the UNCHANGED PRE-MODULE PIN `ac4917d`.
# ---------------------------------------------------------------------------
# `goto <prefix>_L0;` .. `<prefix>_accept:` -- the emitted PROGRAM, which is
# the thing this gate exists for: "module `recursion` changed no call-free
# pattern's matching code". NO filtering beyond the three D37 stamp lines, so
# comment sensitivity INSIDE the region is kept in full -- the property that
# caught [M6.6.2] wave E's 37-byte prose change on 54 artifacts.
#
# [DD-14.FB] moves TWO lines inside that region, and they are a NAMED,
# COUNTED exception: `const unsigned <p>_call_frame` -> `const size_t ...` and
# `>= <PREFIX>_RESUME_FRAMES` -> `>= run->resume_cap`, the region-exit guard,
# which is capacity site 1 of the seven §11 item 3 enumerates. **They cannot
# appear in THIS sweep's population at all**, because `vm_region` is emitted
# only for a call-BEARING artifact and this loop walks the call-FREE bucket --
# so the exception's asserted count here is ZERO, and the assertion is that
# no artifact in the population carries `RX_VM_CALL_`. Stating it as a
# measured zero rather than omitting it is what makes a future call-bearing
# pattern leaking into this bucket a failure instead of a silent widening.
#
# **AND DO NOT ADD A 4-LINE EXCEPTION HERE LATER.** The call-BEARING bucket has
# no `ac4917d` reference to compare against AT ALL — those patterns were
# REFUSED before the module existed — so there is nothing for a region
# exception to fire against on this axis. That bucket's region control is
# `tests/recursion/run_recursion_diff.sh`'s `A == B` (the SPLICE-linked and
# LINKAGE-linked artifacts must agree on every cell), which is already
# asserted there and is where those two lines are actually covered.
#
# ---------------------------------------------------------------------------
# (B) THE WHOLE FILE, against a pin MOVED FORWARD to `694902e` (2026-08-25).
# ---------------------------------------------------------------------------
# [DD-13c], 2026-08-25 — THE SECOND RE-PIN UNDER D76, and it is the same shape
# as the first (which the paragraph below records; keep both, the pair is the
# precedent). r37's D6 panel on [DD-13] found two SCOPE gaps in the stamps and
# both move emitted `#define` bytes: the four artifacts whose body is one
# `return 0` stamp `RX_DFA_SCAN "empty"` instead of naming a loop they do not
# contain, and every VM HYBRID gains `RX_DFA_SCAN`/`RX_DFA_PREFILTER` for the
# DFA scan it INLINES (1,263 of the corpus's 1,488 VM artifacts). Comparison
# [DD-13c] ALSO GREW `struct rx_info` by two fields (`scan`, `prefilter` — the
# runtime mirrors of those same two facts, Frank's D40 addendum), APPENDED at
# the END so no existing member's offset moves. So this bump is BOTH kinds of
# event at once: scaffolding (D76) and layout (D40). (A) is byte-identical
# against the unchanged `ac4917d` pin either way — every byte this change
# writes lands in the `#define` block or the `rx_info` initializer, both ABOVE
# `goto <prefix>_L0;` — which is what still makes it safe. `abi` 5 -> 6 (lane
# srTier's two-tier entry took 4 -> 5 immediately before) and (B) re-pinned here.
# Pin was `5991d4c` ([DD-13]), and `272d07c` earlier in THIS change before the
# rx_info fields were added — the pin must always name the change's LAST
# src/lib/cli commit, and adding the fields made a later one.
# [DD-13], 2026-08-25 — THE PIN'S FIRST RE-PIN UNDER D76, and it is worth one
# paragraph because it is the first time the rule below was exercised by a
# change that was NOT a struct-layout event. `[DD-13]` gave every DFA artifact
# three D46 selection stamps (`RX_ENGINE`, `RX_DFA_SCAN`,
# `RX_DFA_PREFILTER` — docs/spec/match_api.md §6.3), which moves NO struct
# offset and NO emitted program byte: comparison (A) below is byte-identical
# against the unchanged `ac4917d` pin across all five axes, which is the proof
# that the change is scaffolding only. It still bumps `abi` 3 -> 4 and re-pins
# (B) here, because (B) compares WHOLE FILES and three new `#define` lines are
# a whole-file difference on ~2,000 artifacts. That is D76 working as ruled,
# not an exception to it. Pin was `8fc1e51` ([DD-14.FB]).
#
# [OPT-1], 2026-08-25 — THE SECOND SCAFFOLDING-ONLY RE-PIN, and it is worth a
# line because it is the first at which **no DFA artifact's bytes move at
# all**. The TWO-TIER DEFAULT ENTRY (docs/design/two_tier_entry.md,
# docs/spec/match_api.md §10.9) is emitted entirely by `src/gen/emit_vm.c`: a
# DFA artifact has no resume stack and so no tier, and its only difference is
# the `.abi` digit itself. On the VM side every artifact gains two
# `<PREFIX>_FAST_*` `#define`s, and a TIERED one (272 of 2,758 corpus patterns)
# additionally gains a `<prefix>_fast_buffers` type, the `TIER_NOTE` hook block
# and three `noinline` `_deep` statics, while its three un-suffixed entries
# change body. NO struct offset moves and NO emitted PROGRAM byte moves, which
# comparison (A) below proves against the unchanged `ac4917d` pin. `abi` 4 -> 5
# and (B) re-pinned here, in the same change. Pin was `5991d4c` ([DD-13]).
# REASON, for the record: [DD-14.FB] moved the scaffolding across the
# `abi` 2 -> 3 boundary; under D40 (pre-v1) the scaffolding is not comparable
# across such a boundary, and the PROGRAM REGION is. So the whole-file half is
# re-pinned to the last commit on that wave that touches `src`/`lib`/`cli`,
# and everything after it is byte-exact whole-file again -- comment changes
# included. The pre-module reference is NOT discarded: (A) still uses it, on
# the claim it was built to defend.
#
# BOTH RESULTS ARE PRINTED WITH THEIR OWN COUNTS so the two claims never blur
# into one number.
#
# [TT-11]/D76, 2026-08-25: THE TWO PINS HAVE TWO DIFFERENT OWNERS. (A)'s pin
# is the MODULE's promise (pre-module, never moves). (B)'s pin is the emitted
# `abi` NUMBER's: it IS, by definition, the commit that introduced the
# CURRENT `abi`, and any change to emitted scaffolding — comments,
# declarations, layout — is an `abi` bump AND a re-pin of (B) to that
# change's last src-touching commit, in the SAME change. The gate enforces
# that structurally below: it builds an artifact from each compiler on a
# call-free pattern and requires their `rx_info.abi` stamps to agree, rather
# than re-deriving one wave's boundary by hand (the RESUME_FRAME_SIZE grep
# this replaced knew only [DD-14.FB]'s own boundary and would say nothing
# about the next one).
REFCOMMIT="${RECURSION_IDENTITY_REF:-ac4917d}"
FILEPIN="${RECURSION_IDENTITY_FILEPIN:-469a432}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "recursion-identity: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---- the reference compiler, from the PINNED COMMIT -----------------------
REFSRC="$WORKDIR/ref"
mkdir -p "$REFSRC"
if ! git -C "$ROOT_DIR" rev-parse --verify --quiet "$REFCOMMIT^{commit}" >/dev/null; then
    bad "the pinned pre-module commit $REFCOMMIT does not resolve in this repository — the reference cannot be built, and a gate that cannot build its reference must SAY so rather than skip"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
if ! git -C "$ROOT_DIR" archive "$REFCOMMIT" src lib cli \
        | tar -x -C "$REFSRC" 2>"$WORKDIR/arch.log"; then
    bad "could not git-archive $REFCOMMIT: $(head -3 "$WORKDIR/arch.log")"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
# THE REFERENCE MUST HAVE NO WIRED CALL PRODUCER, asserted rather than
# assumed: a mis-typed commit that happened to resolve to something recent
# (e.g. past wave B+C) would build a reference that agrees on the `(?` family
# and report a clean bill of health while comparing far too small a
# population. Checked by the FILE'S ABSENCE, not by grepping for the port
# names — `internal.h` at `ac4917d` already MENTIONS `pcrec_rcport_num` in a
# forward-looking comment (wave A2 anticipating wave B+C's own file), so a
# substring search over the whole tree is a false positive on prose; the
# ports live nowhere but `mod_recursion.c` and that file does not exist
# before wave B+C.
if [ -f "$REFSRC/src/parse/mod_recursion.c" ]; then
    bad "the reference tree at $REFCOMMIT already carries src/parse/mod_recursion.c — that is not a PRE-producer commit, so the (? family's half of every comparison below would be a build against itself"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

REF="$WORKDIR/pcrec_premodule"
REF_SRCS="$(find "$REFSRC/src" -name '*.c' | LC_ALL=C sort)"
if [ -z "$REF_SRCS" ]; then
    bad "found no compiler sources in the archived reference tree"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
# shellcheck disable=SC2086
if ! $CC -O0 -std=gnu11 -Wall -Wextra -I"$REFSRC/lib" -I"$REFSRC/src" $SANFLAGS \
        -o "$REF" "$REFSRC"/cli/main.c $REF_SRCS 2>"$WORKDIR/refbuild.log"; then
    bad "could not build the pre-module reference compiler from $REFCOMMIT:"
    head -20 "$WORKDIR/refbuild.log" >&2
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# ---- the FILE-PIN compiler, from the moved-forward pin --------------------
# [DD-14.FB] The second reference (see the header's (B)). Same construction as
# the pre-module one above, same refusal when the pin is absent from history:
# a gate that cannot build a reference must SAY so rather than skip.
FILEREFSRC="$WORKDIR/fileref"
mkdir -p "$FILEREFSRC"
if ! git -C "$ROOT_DIR" rev-parse --verify --quiet "$FILEPIN^{commit}" >/dev/null; then
    bad "the whole-file pin $FILEPIN does not resolve in this repository — the (B) reference cannot be built, and a gate that cannot build its reference must SAY so rather than skip"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
if ! git -C "$ROOT_DIR" archive "$FILEPIN" src lib cli \
        | tar -x -C "$FILEREFSRC" 2>"$WORKDIR/filearch.log"; then
    bad "could not git-archive $FILEPIN: $(head -3 "$WORKDIR/filearch.log")"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
FILEREF="$WORKDIR/pcrec_filepin"
FILEREF_SRCS="$(find "$FILEREFSRC/src" -name '*.c' | LC_ALL=C sort)"
# shellcheck disable=SC2086
if ! $CC -O0 -std=gnu11 -Wall -Wextra -I"$FILEREFSRC/lib" -I"$FILEREFSRC/src" $SANFLAGS \
        -o "$FILEREF" "$FILEREFSRC"/cli/main.c $FILEREF_SRCS 2>"$WORKDIR/filerefbuild.log"; then
    bad "could not build the file-pin reference compiler from $FILEPIN:"
    head -20 "$WORKDIR/filerefbuild.log" >&2
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
# THE PIN MUST BE A POST-FB PIN, and since [TT-11]/D76 that is asserted
# STRUCTURALLY rather than by an ad-hoc probe for one wave's boundary
# (the RESUME_FRAME_SIZE grep this replaced encoded [DD-14.FB] specifically
# and would say nothing about the NEXT scaffolding change). D76's ruling:
# the whole-file pin IS, by definition, the commit that introduced the
# CURRENT `abi` number, so the two compilers' emitted `rx_info.abi` stamps
# must agree — read off an actual artifact from each, on a call-free
# pattern, rather than re-derived from source text.
ABI_SUBJ_ART="$(pcrec_run "$PCREC"   --features all -p rx -o - -- 'a' 2>/dev/null)"   # [K37] bounded
ABI_PIN_ART="$(pcrec_run "$FILEREF" --features all -p rx -o - -- 'a' 2>/dev/null)"   # [K37] bounded
ABI_SUBJ="$(printf '%s\n' "$ABI_SUBJ_ART" | grep -o '\.abi = [0-9]*' | head -1)"
ABI_PIN="$(printf '%s\n' "$ABI_PIN_ART" | grep -o '\.abi = [0-9]*' | head -1)"
if [ -z "$ABI_SUBJ" ] || [ -z "$ABI_PIN" ]; then
    bad "could not read an \`.abi = N\` stamp from one of the two compilers' output on the call-free pattern 'a' — the (B) reference cannot be validated (subject stamp: '${ABI_SUBJ:-<none>}', pin stamp: '${ABI_PIN:-<none>}')"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
if [ "$ABI_SUBJ" != "$ABI_PIN" ]; then
    bad "the emitted scaffolding changed: bump \`abi\` in src/gen/emit_dfa.c and re-pin comparison (B) to this change's last src commit, in the same change (D76) — subject stamps '$ABI_SUBJ', pin $FILEPIN stamps '$ABI_PIN'"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# Both builds emit SELF-CONTAINED C to stdout: writing to two different paths
# would put a different `#include "<name>.h"` line in each and every
# comparison would "differ" for a reason unrelated to this module.
#
# THE D37 STAMP FILTER, and it is ASSERTED rather than trusted — see the
# header. `stamp_count` must report exactly 3 on BOTH sides of every
# comparison; `stamp_strip` removes exactly those lines.
stamp_strip() {
    grep -vE '^/\* Feature set: |^#define PCREC_FEATURE_SET |^#define PCREC_FEATURE_MODULES '
}
stamp_count() {
    grep -cE '^/\* Feature set: |^#define PCREC_FEATURE_SET |^#define PCREC_FEATURE_MODULES ' \
        || true
}
# shellcheck disable=SC2086
gen_a() { pcrec_run "$PCREC" --features all -p rx $2 -o - -- "$1" 2>/dev/null; }
# shellcheck disable=SC2086
gen_b() { "$REF"   --features all -p rx $2 -o - -- "$1" 2>/dev/null; }
# shellcheck disable=SC2086
gen_c() { "$FILEREF" --features all -p rx $2 -o - -- "$1" 2>/dev/null; }

# [DD-14.FB] THE PROGRAM REGION: `goto <p>_L0;` through the accept label. An
# artifact with no VM program (a DFA-selected pattern) yields the EMPTY region,
# and empty-vs-empty compares equal — which is correct and is why the
# dead-capture elision's four patterns still show up as differing here: on the
# pre-module reference they were VM-selected and HAVE a region, and today they
# are DFA-selected and do not.
prog_region() { awk '/^    goto rx_L0;$/,/^rx_accept:/'; }
# The two [DD-14.FB] lines that move INSIDE the region, on a call-BEARING
# artifact only. Counted, never stripped.
FB_REGION_LINES='^        const (unsigned|size_t) rx_call_frame = run->call_top;$|^        if \(rx_call_frame >= (RX_RESUME_FRAMES|run->resume_cap)\) return RX_R_INTERNAL;$'

# ---- the corpus ------------------------------------------------------------
PATFILE="$WORKDIR/patterns"
find "$ROOT_DIR/tests" -name '*.rxt' -print0 \
    | xargs -0 grep -h '^pattern ' \
    | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$PATFILE"

python3 - "$PATFILE" "$WORKDIR/call" "$WORKDIR/free" <<'PY'
import sys, re
src, cout, fout = sys.argv[1], sys.argv[2], sys.argv[3]

def mask_classes(pat):
    out = []; i = 0; n = len(pat); in_class = False
    while i < n:
        c = pat[i]
        if c == "\\" and i + 1 < n:
            out.append("XX" if in_class else c + pat[i+1]); i += 2; continue
        if not in_class and c == "[":
            in_class = True; out.append(c); i += 1; continue
        if in_class and c == "]":
            in_class = False; out.append(c); i += 1; continue
        out.append("X" if in_class else c); i += 1
    return "".join(out)

G_RE = re.compile(r"\\g[<']")

# Every `(?` occurrence, on the MASKED text (a class-interior `(?` is not a
# doorway at all, but masking is cheap insurance and matches the \g rule's
# own logic). FAILS SAFE TOWARD THE CALL BUCKET: the NON-call tails are
# enumerated by name, and anything NOT matching one of them is classified a
# call, on `run_atomic_identity.sh`'s and `lookaround_classify.py`'s shared
# rule — an unrecognised tail costs a pattern from the identity population
# rather than silently admitting one that should have been excluded.
GROUP_OPEN = re.compile(r"\(\?")
NOT_CALL = re.compile(
    r"^(?::"                       # (?:  non-capturing
    r"|[=!*]"                      # (?=  (?!  (?*  lookaround
    r"|<[=!*]"                     # (?<= (?<! (?<* lookbehind
    r"|<[A-Za-z_]"                 # (?<name>  named group
    r"|'"                          # (?'name'  named group, quoted
    r"|P<"                         # (?P<name> named group
    r"|P="                         # (?P=name) backref by name
    r"|>"                          # (?>...)   atomic group (module
                                    # atomic-groups' doorway, NOT a call --
                                    # the one this classifier's first draft
                                    # got wrong, measured against the
                                    # positive control below)
    r"|#"                          # (?#...)   comment
    r"|\((?!DEFINE\))"            # (?(...)   conditional -- module
                                    # `conditionals`', NOT this module's --
                                    # EXCEPT `(?(DEFINE)`, which [DD-14] wave
                                    # F moved to module `recursion` as a
                                    # tailed row (D71 item 4). The negative
                                    # lookahead is what keeps this gate HONEST
                                    # rather than convenient: a DEFINE-bearing
                                    # pattern with NO CALL in it --
                                    # `(?(DEFINE)abc)^x$` -- really is a
                                    # pattern this module changed, so it
                                    # belongs in the population the reference
                                    # is EXPECTED to refuse and not in the one
                                    # required to be byte-identical. THE GATE
                                    # FOUND THIS ITSELF: four such cells
                                    # arrived with wave F's own corpus and it
                                    # reported them as refusal mismatches
                                    # before the classifier had been told.
    r"|[)^JUainmrsx]"              # (?imsx...) (?) (?^)  inline option run
                                    # -- the EXACT letter set GROUP_OPT rows
                                    # in registry.c carry, not a blanket
                                    # A-Za-z: `R` is NOT one of them and
                                    # must fall through to the call branch
    r"|-(?![0-9])"                 # (?imsx-J:...)  option run's unset half
                                    # -- NOT `-` followed by a digit, which
                                    # is `(?-N)`, a RELATIVE CALL, the one
                                    # place the two grammars share a byte
    r")"
)

def is_call(pat):
    m = mask_classes(pat)
    if G_RE.search(m):
        return True
    for mo in GROUP_OPEN.finditer(m):
        tail = m[mo.end():]
        if not NOT_CALL.match(tail):
            return True
    return False

# ---- THE CLASSIFIER'S OWN SELF-TEST, run before it classifies anything.
# design §0.3 item 9 is the census's OWN measured instrument defect: a naive
# `\g<` scan counts tests/backrefs/octal_class.rxt's `^[\g<1>]$`, where the
# class doorway makes those four bytes literal escapes, as a call. The
# classifier inherits the defect unless it masks classes, and "it masks
# classes" is a claim about code that must be exercised rather than read. The
# `(?&x)`-inside-a-class row is the SECOND doorway's version of the same
# defect, which the first draft of this list did not have.
#
# The FAIL-SAFE rows are here for the opposite reason: they assert that an
# unrecognised `(?` tail lands in the CALL bucket, so a future spelling this
# classifier has never seen costs a pattern from the identity population
# rather than being admitted to it wrongly.
_SELFTEST = [
    # (pattern, expected is_call, why)
    (r"^[\g<1>]$",      False, "class doorway: four literal escapes, NOT a call (design §0.3 item 9, the census's own defect)"),
    (r"^[(?&x)]$",       False, "a `(?&x)` INSIDE a class is five class members, not a call"),
    (r"^[\g'1']$",      False, "the quoted backslash-g spelling is literal inside a class too"),
    (r"a[b]\g<1>",       True,  "a REAL backslash-g call after a class has closed — masking must not swallow the rest of the pattern"),
    (r"(a)(?1)",         True,  "the numeric call"),
    (r"(?R)",            True,  "the whole-pattern call: `R` is NOT in the inline-option letter set"),
    (r"(?<n>a)(?&n)",    True,  "the by-name call"),
    (r"(?P<n>a)(?P>n)",  True,  "the alpha by-name call"),
    (r"(a)(?-1)",        True,  "the relative call — `-` followed by a DIGIT is not an option run's unset half"),
    (r"(a)\g<1>",        True,  "the backslash-g numeric tail"),
    (r"(?i-x:a)",        False, "an inline option run WITH an unset half is not a call"),
    (r"(?:a)",           False, "non-capturing"),
    (r"(?>a)",           False, "atomic group — module atomic-groups' doorway, the one this classifier's first draft got wrong"),
    (r"(?=a)(?!b)(?<=c)(?<!d)", False, "the four lookaround doorways"),
    (r"(?<name>a)(?'q'b)", False, "named groups, both spellings"),
    (r"(?P=n)",          False, "backref by name — module backrefs' doorway"),
    (r"(?#comment)",     False, "a comment"),
    (r"(?(1)a|b)",       False, "an ordinary conditional -- module `conditionals`', not this module's"),
    (r"(?(DEFINE)abc)^x$", True, "[wave F] `(?(DEFINE)` is module recursion's (D71 item 4), so a DEFINE-bearing pattern with NO CALL in it still belongs in the bucket the reference must REFUSE -- the negative lookahead's whole point, and the row that pins it"),
    (r"(?(DEFINE)(?<g>a))(?&g)", True, "[wave F] DEFINE plus a real call: call-bearing twice over, and it must not be rescued into the call-free bucket by the conditional arm"),
    (r"(?(DEFINE)(?<g>a))b", True, "[wave F] THE SHARP ONE: a DEFINE whose body holds a NAMED GROUP, and nothing outside it. This pattern scans TWO `(?` occurrences -- the DEFINE tail, which the negative lookahead sends to the call bucket, and `(?<g>`, which the named-group arm recognises as NOT a call -- so it is the row that pins the ANY-occurrence rule: one unrecognised tail is enough, and a classifier that took the LAST occurrence's verdict, or that let a recognised inner construct rescue the pattern, files it call-FREE and the gate then demands byte-identity from a pattern this module changed"),
    (r"^[(?(DEFINE)a)]$", False, "a `(?(DEFINE)` INSIDE a class is class members -- the class mask has to reach wave F's arm too, or the newest doorway reintroduces the census's oldest defect"),
    (r"(?~x)",           True,  "FAIL SAFE: an unrecognised `(?` tail is classified call-bearing"),
]
_bad = []
for _pat, _want, _why in _SELFTEST:
    _got = is_call(_pat)
    if _got != _want:
        _bad.append("  %-24r classified %s, want %s -- %s"
                    % (_pat, "CALL" if _got else "call-free",
                       "CALL" if _want else "call-free", _why))
if _bad:
    sys.stderr.write("classifier self-test FAILED on %d of %d rows:\n%s\n"
                     % (len(_bad), len(_SELFTEST), "\n".join(_bad)))
    sys.exit(2)
print("recursion-identity: classifier self-test %d/%d rows"
      % (len(_SELFTEST), len(_SELFTEST)))

call, free = [], []
for line in open(src):
    p = line.rstrip("\n")
    if not p:
        continue
    (call if is_call(p) else free).append(p)
open(cout, "w").write("\n".join(call) + ("\n" if call else ""))
open(fout, "w").write("\n".join(free) + ("\n" if free else ""))
PY

nc=$(grep -c . "$WORKDIR/call" || true)
nf=$(grep -c . "$WORKDIR/free" || true)
echo "recursion-identity: corpus $(grep -c . "$PATFILE") patterns; call-bearing: $nc; call-free: $nf"

if [ "$nf" -lt 700 ]; then
    bad "corpus extraction found only $nf call-free patterns — the gate has no population"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
if [ "$nc" -lt 60 ]; then
    bad "corpus extraction found only $nc call-bearing patterns — the POSITIVE CONTROL has no population, so an identical result below would prove nothing"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

# ---- THE POSITIVE CONTROL and THE SWEEP, ONE AXIS AT A TIME ---------------
#
# The control and the sweep are ONE function because they are one claim per
# axis: "on THIS invocation the reference is a different compiler (it refuses
# every call-bearing pattern) AND the two agree byte for byte on every
# call-free one". Splitting them would let a run report identity on an axis
# whose control was never taken.
control() { # control <label> <extra pcrec args>
    local label="$1" args="$2"
    local ctl_ok=0 ctl_bad=0
    while IFS= read -r pat; do
        [ -n "$pat" ] || continue
        # shellcheck disable=SC2086
        if "$REF" --features all -p rx $args -o - -- "$pat" >/dev/null 2>&1; then
            ctl_bad=$((ctl_bad + 1))
            [ "$ctl_bad" -le 5 ] && echo "  CONTROL[$label]: the PRE-MODULE compiler ACCEPTED '$pat'" >&2
        else
            ctl_ok=$((ctl_ok + 1))
        fi
    done < "$WORKDIR/call"
    if [ "$ctl_bad" -eq 0 ] && [ "$ctl_ok" -eq "$nc" ]; then
        ok "[$label] positive control: the pre-module reference REFUSES all $ctl_ok call-bearing patterns — so it really is a different compiler, and a zero-difference result below is a measurement rather than a build compared against itself"
    else
        bad "[$label] positive control: the pre-module reference compiled $ctl_bad of $nc call-bearing patterns (ctl_ok=$ctl_ok). Either the pin is wrong or the corpus split is misclassifying — in both cases the identity sweep below is comparing two builds that agree because they are the same"
    fi
}

sweep() { # sweep <label> <extra pcrec args>
    local label="$1" args="$2"
    local same=0 diff=0 refused=0 mism=0 stampbad=0 stampmoved=0 elided=0
    # [DD-14.FB] the SECOND tally: the program region against the unchanged
    # pre-module pin. Kept in its own variables and printed on its own line so
    # the two claims never blur into one number.
    local rsame=0 rdiff=0 relided=0 rcallbearing=0
    : > "$WORKDIR/diff.$label"
    while IFS= read -r pat; do
        [ -n "$pat" ] || continue
        local a b na nb sa sb
        local r ra rb
        a="$(gen_a "$pat" "$args")"
        # [DD-14.FB] `b` is now the FILE-PIN build (comparison (B)); `r` is the
        # PRE-MODULE build, used for the program-region comparison (A).
        b="$(gen_c "$pat" "$args")"
        r="$(gen_b "$pat" "$args")"
        if [ -z "$a" ] && [ -z "$b" ]; then refused=$((refused + 1)); continue; fi
        if [ -z "$a" ] || [ -z "$b" ]; then
            mism=$((mism + 1))
            printf 'REFUSAL MISMATCH %s: subject=%s reference=%s\n' "$pat" \
                "$([ -n "$a" ] && echo compiled || echo refused)" \
                "$([ -n "$b" ] && echo compiled || echo refused)" \
                >> "$WORKDIR/diff.$label"
            continue
        fi
        na="$(printf '%s\n' "$a" | stamp_count)"
        nb="$(printf '%s\n' "$b" | stamp_count)"
        if [ "$na" -ne 3 ] || [ "$nb" -ne 3 ]; then
            stampbad=$((stampbad + 1))
            printf 'STAMP FILTER %s: subject %s lines, reference %s lines, want 3 each\n' \
                "$pat" "$na" "$nb" >> "$WORKDIR/diff.$label"
            continue
        fi
        # ---- (A) THE PROGRAM REGION, against the PRE-MODULE pin -----------
        # No filtering beyond the three D37 stamp lines, so a comment change
        # inside the region is still a difference. The two [DD-14.FB] lines
        # that CAN move in here belong to `vm_region`, which is emitted only on
        # a call-BEARING artifact -- this population is the call-FREE bucket,
        # so the asserted count is ZERO and a non-zero one means a call-bearing
        # pattern has leaked into the bucket, not that the exception fired.
        if [ -n "$r" ]; then
            ra="$(printf '%s\n' "$a" | stamp_strip | prog_region)"
            rb="$(printf '%s\n' "$r" | stamp_strip | prog_region)"
            case "$a" in *RX_VM_CALL_*) rcallbearing=$((rcallbearing + 1)) ;; esac
            if [ "$ra" = "$rb" ]; then
                rsame=$((rsame + 1))
            elif printf '%s\n' "$ELIDED_PATTERNS" | grep -qxF -- "$pat"; then
                relided=$((relided + 1))
            else
                rdiff=$((rdiff + 1))
                printf 'REGION DIFFERS %s\n' "$pat" >> "$WORKDIR/diff.$label"
            fi
        fi

        # ---- (B) THE WHOLE FILE, against the moved-forward pin -------------
        if [ "$a" = "$b" ]; then
            # Identical RAW, so identical stripped: the strongest reading, and
            # the one every pattern in the tree gives today.
            same=$((same + 1))
            continue
        fi
        sa="$(printf '%s\n' "$a" | stamp_strip)"
        sb="$(printf '%s\n' "$b" | stamp_strip)"
        if [ "$sa" = "$sb" ]; then
            # Differs RAW, agrees STRIPPED: the difference is the D37 stamp and
            # nothing else. That is the RULED comparison's pass, and it is
            # counted separately rather than folded into `same`, because "the
            # stamp moved" is a claim a reader has to see (header).
            stampmoved=$((stampmoved + 1))
            printf 'STAMP MOVED %s\n' "$pat" >> "$WORKDIR/diff.$label"
        elif printf '%s\n' "$ELIDED_PATTERNS" | grep -qxF -- "$pat"; then
            # THE NAMED EXCEPTION (see the header). Counted, not skipped, and
            # the direction that matters is checked below: every listed pattern
            # must land HERE on every axis, so a list that has gone stale — the
            # elision narrowed, or somebody gated it on `has_call` after all —
            # is a failure and not a quieter sweep.
            elided=$((elided + 1))
            printf 'ELIDED (ruled, wave G) %s\n' "$pat" >> "$WORKDIR/diff.$label"
        else
            diff=$((diff + 1))
            printf 'DIFFERS %s\n' "$pat" >> "$WORKDIR/diff.$label"
        fi
    done < "$WORKDIR/free"
    echo "recursion-identity[$label] (B) whole-file vs $FILEPIN: same=$same differing=$diff elided=$elided refused-by-both=$refused refusal-mismatch=$mism stamp-filter-bad=$stampbad stamp-moved=$stampmoved"
    echo "recursion-identity[$label] (A) program-region vs $REFCOMMIT: same=$rsame differing=$rdiff elided=$relided call-bearing-in-population=$rcallbearing"
    # BOTH DIRECTIONS ON THE NAMED EXCEPTION. `elided` counts the patterns that
    # differed AND are on the list; `nelide` is the list's own length. Equality
    # is what says the list is neither stale nor a filter: a listed pattern that
    # went back to identical (the elision narrowed) fails here, and a pattern
    # that differs without being listed is already `diff` above.
    local nelide
    nelide=$(printf '%s\n' "$ELIDED_PATTERNS" | grep -c .)
    # AND THE `--no-captures` AXIS EXPECTS **ZERO**, WHICH IS A SHARPER CLAIM
    # THAN THE OTHER FOUR AND NOT AN EXEMPTION FROM THEM. The elision says a
    # group NO EMITTED CODE CAN WRITE does not force the capture-recording
    # engine. Under `--no-captures` the artifact promises NO group at all, so
    # `forces_captures` returns `DFA | VM` in BOTH compilers for its own
    # earlier reason and there is nothing left for this rule to decide: the
    # four patterns must be byte-IDENTICAL there. So the list's real assertion
    # is a PAIR — the four move on every axis that promises a capture, and
    # vanish on the one that does not — and a run where they moved on
    # `--no-captures` too would mean the elision was firing for some reason
    # OTHER than the one written down. MEASURED at the wave: 4 / 4 / 4 / 0 / 4
    # over default, vm, noprefilter, nocaptures, nosplice.
    [ "$label" = "nocaptures" ] && nelide=0
    # [DD-14.FB] AND THE REGION EXPECTATION IS NOT THE WHOLE-FILE ONE, on two
    # of the four axes. MEASURED (2026-08-25), and the rule falls straight out
    # of what the dead-capture elision DOES: its entire effect is on ENGINE
    # SELECTION — a group no emitted code can write stops forcing the
    # capture-recording engine — so a program REGION can only move on an axis
    # where selection is free to change.
    #
    #   default, -fno-prefilter : reference selects the VM (region 8 and 11
    #                             lines), today selects the DFA (region empty)
    #                             -> all 4 differ. Expect `nelide`.
    #   --engine=vm             : the engine is FORCED to the VM on BOTH
    #                             sides, so the elision has nothing to select
    #                             and the two programs are byte-identical
    #                             -> expect 0. This is a STRONGER reading than
    #                             the whole-file one, not an exemption from
    #                             it: with the engine held fixed, wave G's
    #                             elision moves no emitted program at all.
    #   --no-captures           : neither side promises a group, so both are
    #                             DFA and both regions are empty -> expect 0,
    #                             for the reason the line above already gives.
    #
    # The two zeros have DIFFERENT reasons and are written down separately;
    # collapsing them into "some axes are exempt" is how a real regression on
    # one of them would later be waved through as expected.
    local nelide_region="$nelide"
    [ "$label" = "vm" ] && nelide_region=0
    # [DD-14.FB] THE ELISION LIST NOW BELONGS TO COMPARISON (A). The
    # dead-capture elision is what moved those four patterns from the VM to the
    # DFA, so against the PRE-MODULE reference they still differ (there, they
    # have a program region; here they do not) -- and against the moved-forward
    # FILE PIN, which is post-wave-G, they must NOT differ at all, because the
    # elision is on both sides of that comparison. Two different expectations
    # for one list, each asserted against the comparison it belongs to; folding
    # them would have meant one of the two going unchecked.
    if [ "$relided" -ne "$nelide_region" ]; then
        bad "[$label] (A) the wave-G ELISION list expects $nelide_region of its patterns' PROGRAM REGIONS to differ from $REFCOMMIT on this axis and $relided did. The elision acts on ENGINE SELECTION, so a region moves only where selection is free: on default and -fno-prefilter all four must differ (VM-selected then, DFA-selected now); on --engine=vm none may, because the engine is forced on both sides and the two programs are byte-identical; on --no-captures none may, because neither side promises a group:"
        printf '%s\n' "$ELIDED_PATTERNS" | sed 's/^/    listed: /' >&2
    fi
    if [ "$rcallbearing" -ne 0 ]; then
        bad "[$label] (A) $rcallbearing artifacts in the CALL-FREE population carry RX_VM_CALL_ macros. The two [DD-14.FB] region lines (the region-exit guard's type and capacity operand) are emitted only for a call-BEARING artifact, so this population's asserted count for them is ZERO; a non-zero one means the call-free classifier has leaked, not that the named exception fired"
    fi
    if [ "$rdiff" -ne 0 ]; then
        bad "[$label] (A) $rdiff call-free patterns emit a DIFFERENT PROGRAM REGION than $REFCOMMIT for a reason no ruling has recorded — this is the claim the pre-module pin exists to defend:"
        grep '^REGION DIFFERS' "$WORKDIR/diff.$label" | head -10 >&2
    fi
    if [ "$elided" -ne 0 ]; then
        bad "[$label] (B) $elided of the wave-G elision patterns differ WHOLE-FILE against $FILEPIN, which is post-wave-G — the elision is on both sides of that comparison, so none of them may differ there:"
        grep '^ELIDED' "$WORKDIR/diff.$label" | sed 's/^/    /' >&2
    fi
    if [ "$stampbad" -ne 0 ]; then
        bad "[$label] the D37 stamp filter matched the wrong number of lines on $stampbad artifacts — it must remove EXACTLY three, so a filter that stopped matching (leaving a difference in) or started over-matching (hiding one) says so"
        head -5 "$WORKDIR/diff.$label" >&2
    fi
    if [ "$stampmoved" -ne 0 ]; then
        bad "[$label] $stampmoved call-free patterns differ ONLY in D37's three feature-stamp lines. The RULED comparison (§9.1: byte-identical past the stamp) still passes on them, but module \`recursion\`'s registry rows PREDATE the module, so nothing in this module has any business moving \`render_modules\`' first-row walk — a wave that legitimately moves it (wave F adds rows) must say so in its commit and update this check's header:"
        head -10 "$WORKDIR/diff.$label" >&2
    fi
    if [ "$mism" -ne 0 ]; then
        bad "[$label] $mism call-FREE patterns are accepted by one build and refused by the other. Module recursion must not change what pcrec ACCEPTS on a pattern with no call construct in it:"
        head -10 "$WORKDIR/diff.$label" >&2
    fi
    if [ "$diff" -ne 0 ]; then
        bad "[$label] $diff call-free patterns emit DIFFERENT bytes for a reason no ruling has recorded:"
        head -20 "$WORKDIR/diff.$label" >&2
    fi
    if [ "$same" -lt 700 ]; then
        bad "[$label] only $same patterns compared identical (floor 700) — the sweep is not populated"
    fi
    if [ "$mism" -eq 0 ] && [ "$diff" -eq 0 ] && [ "$stampbad" -eq 0 ] \
       && [ "$stampmoved" -eq 0 ] && [ "$same" -ge 700 ] \
       && [ "$elided" -eq 0 ] && [ "$rdiff" -eq 0 ] && [ "$rcallbearing" -eq 0 ] \
       && [ "$relided" -eq "$nelide_region" ]; then
        ok "[$label] (B) WHOLE-FILE byte identity: ALL $same call-free corpus patterns emit IDENTICAL C (raw, and therefore also past D37's three stamp lines, each verified present on both sides) against a compiler built from the pin $FILEPIN — zero differing, zero refusal mismatches, and zero elision movement, which is what a post-wave-G pin must show"
        ok "[$label] (A) PROGRAM-REGION identity: $rsame call-free patterns emit an IDENTICAL program region ('goto <p>_L0;' .. '<p>_accept:', unfiltered past the D37 stamps, comment changes included) against the UNCHANGED PRE-MODULE pin $REFCOMMIT — the claim this gate was built for, still measured against the reference it was built against; exactly the $nelide_region NAMED wave-G elision patterns moved (the elision acts on engine selection, so a region moves only where selection is free — 4 on default and -fno-prefilter, 0 on --engine=vm where the engine is forced on both sides, 0 on --no-captures where neither side promises a group), and 0 artifacts in this call-free population carry the call machinery whose two [DD-14.FB] region lines are the counted exception"
    fi
}

# THE FIVE AXES (§9.1, plus wave G's). Each takes its own positive control
# first: "refuses" is an answer the axis flags could in principle change, since
# `--no-captures`, `-fno-prefilter` and `-fno-splice-calls` all reach
# `select_engine.c` where a refusal lives — and the last of them changes which
# ENGINE a call-bearing pattern gets, which is the sharpest version of that
# worry rather than a theoretical one.
#
# **AND THE FIFTH AXIS IS NOT AN AXIS OF THIS SWEEP, WHICH IS A MEASURED
# FINDING AND NOT A CORNER CUT.** `-fno-splice-calls` was tried in the loop
# above twice and is structurally incompatible with a PINNED PRE-MODULE
# reference, in two different ways:
#
#   1. HANDED TO THE REFERENCE it is an unknown flag, so the reference refuses
#      EVERY pattern — MEASURED at 2,196 refusal mismatches.
#   2. HANDED TO THE SUBJECT ONLY it still moves every artifact, because the
#      flag is deliberately NOT in `emit_info_def`'s `strategy_denials` mask
#      (lib/pcrec.h: it can change which ENGINE a pattern gets, which is
#      `PCREC_NO_ATOMIC_DISCHARGE`'s shape and not `-fno-possessify`'s), so
#      `rx_info.flags` reads `8192ULL` on one side and `0ULL` on the other —
#      MEASURED at 2,196 differing.
#
# There is no third spelling: **a flag that honestly records itself cannot be
# compared against a compiler that does not have it.**
#
# **AND THE OBVIOUS REPAIR IS THE WRONG ONE — DO NOT RESTORE THE AXIS
# LITERALLY** (ruled 2026-08-24, and written here because the next reader will
# propose it). Putting `PCREC_NO_SPLICE_CALLS` into `emit_info_def`'s
# `strategy_denials` mask would mask reason 2 away and let the flag ride the
# loop above. That mask is for knobs with NO OBSERVABLE EFFECT — the whole
# argument for it (src/gen/emit_dfa.c) is that two artifacts which behave
# identically must not differ in their reflection surface. This flag SELECTS AN
# ENGINE: `--engine=dfa -fno-splice-calls '(a)(?1)'` refuses where
# `--engine=dfa '(a)(?1)'` compiles. `rx_info.flags` records it for the same
# reason it records `PCREC_NO_ATOMIC_DISCHARGE`, which is the one other member
# of the deny family with that property. **Masking it to make this sweep
# comparable would be falsifying the artifact's own record of itself to satisfy
# a check** — the check-design failure this file exists to be an instance of the
# opposite of.
#
# So the linkage axis is a SEPARATE SECTION below, `linkage_axis`, comparing the
# SUBJECT AGAINST ITSELF — which is the comparison the claim was always about —
# and the OTHER half, what the flag does to a CALL-BEARING pattern, lives where
# it can: `tests/recursion/run_recursion_diff.sh` §5 (`A == B` over 156 patterns
# and 15,912 cells, span and every group span) and §4's three-cell
# `--engine=dfa` family. Between them the linkage claim is covered on both
# populations; what is NOT available, and is not worth buying at that price, is
# a byte comparison against a compiler from before the flag existed.
# ============================================================================
# THE LINKAGE AXIS — THE SUBJECT AGAINST ITSELF ([DD-14] wave G)
# ============================================================================
# WHAT IT ASSERTS: **forcing the CALL LINKAGE changes nothing for a CALL-FREE
# pattern.** Both arms are THIS compiler, so the pinned reference's two
# incompatibilities (see the axis block above) do not arise, and the one line
# the flag legitimately moves — `rx_info.flags`, which records it because it can
# change which engine a pattern gets — is a NAMED, ASSERTED exclusion of exactly
# one line per side rather than a filter.
#
# IT IS NOT VACUOUS THE WAY A `-D` KNOB WOULD BE, and the reason is the four
# ELIDED patterns: they are CALL-FREE and they DO move under the dead-capture
# elision, so this section can ask whether they move the SAME WAY with the
# splice denied. They must, because `A_REP{0,0}` emitting nothing has nothing
# to do with how a call reaches its callee — and "must" is the kind of claim
# this file exists to check rather than state.
linkage_axis() {
    local same=0 diff=0 refused=0 mism=0 stripbad=0
    : > "$WORKDIR/diff.linkage"
    while IFS= read -r pat; do
        [ -n "$pat" ] || continue
        local a b sa sb na nb
        a="$(gen_a "$pat" "")"
        b="$(gen_a "$pat" "-fno-splice-calls")"
        if [ -z "$a" ] && [ -z "$b" ]; then refused=$((refused + 1)); continue; fi
        if [ -z "$a" ] || [ -z "$b" ]; then
            mism=$((mism + 1))
            printf 'REFUSAL MISMATCH %s\n' "$pat" >> "$WORKDIR/diff.linkage"
            continue
        fi
        # THE ONE NAMED EXCLUSION, ASSERTED IN BOTH DIRECTIONS: exactly one
        # `.flags` line on each side, or the exclusion has stopped describing
        # what it removes.
        na="$(printf '%s\n' "$a" | grep -c '^    \.flags = ')"
        nb="$(printf '%s\n' "$b" | grep -c '^    \.flags = ')"
        if [ "$na" -ne 1 ] || [ "$nb" -ne 1 ]; then
            stripbad=$((stripbad + 1))
            printf 'FLAGS FILTER %s: %s / %s lines, want 1 each\n' \
                "$pat" "$na" "$nb" >> "$WORKDIR/diff.linkage"
            continue
        fi
        sa="$(printf '%s\n' "$a" | grep -v '^    \.flags = ')"
        sb="$(printf '%s\n' "$b" | grep -v '^    \.flags = ')"
        if [ "$sa" = "$sb" ]; then
            same=$((same + 1))
        else
            diff=$((diff + 1))
            printf 'DIFFERS %s\n' "$pat" >> "$WORKDIR/diff.linkage"
        fi
    done < "$WORKDIR/free"
    echo "recursion-identity[linkage]: same=$same differing=$diff refused-by-both=$refused refusal-mismatch=$mism flags-filter-bad=$stripbad"
    if [ "$stripbad" -ne 0 ]; then
        bad "[linkage] the \`.flags\` exclusion matched the wrong number of lines on $stripbad artifacts — it must remove EXACTLY one per side, so an exclusion that stopped matching (leaving a difference in) or started over-matching (hiding one) says so"
        head -5 "$WORKDIR/diff.linkage" >&2
    fi
    if [ "$mism" -ne 0 ]; then
        bad "[linkage] $mism call-free patterns are accepted with the splice and refused without it, or the reverse. Denying the splice must not change what pcrec ACCEPTS on a pattern with no call in it:"
        head -10 "$WORKDIR/diff.linkage" >&2
    fi
    if [ "$diff" -ne 0 ]; then
        bad "[linkage] $diff call-free patterns emit DIFFERENT bytes with the splice denied. A pattern with no call has no call graph — \`pcrec_callgraph_build\` returns at its first scan — so \`-fno-splice-calls\` cannot reach it:"
        head -20 "$WORKDIR/diff.linkage" >&2
    fi
    if [ "$same" -lt 700 ]; then
        bad "[linkage] only $same patterns compared identical (floor 700) — the sweep is not populated"
    fi
    [ "$diff" -eq 0 ] && [ "$mism" -eq 0 ] && [ "$stripbad" -eq 0 ] \
        && [ "$same" -ge 700 ] \
        && ok "[linkage] ALL $same call-free corpus patterns emit IDENTICAL C with and without \`-fno-splice-calls\`, past exactly one \`rx_info.flags\` line per side (verified present on both) — so forcing the call linkage reaches nothing a call-free pattern compiles through"

    # AND THE FOUR ELIDED PATTERNS MOVE THE SAME WAY ON BOTH ARMS. This is the
    # half that makes the section more than a restatement of "the flag is
    # gated": the elision fires on these four, and it must fire IDENTICALLY
    # with the splice denied.
    local ebad=0 n=0
    while IFS= read -r pat; do
        [ -n "$pat" ] || continue
        n=$((n + 1))
        local ea eb
        ea="$(gen_a "$pat" "" | grep -m1 '^    \.engine = ')"
        eb="$(gen_a "$pat" "-fno-splice-calls" | grep -m1 '^    \.engine = ')"
        case "$ea" in *PCREC_ENGINE_DFA*) ;; *)
            bad "[linkage] the elided pattern '$pat' is not on the DFA engine: $ea"
            ebad=$((ebad + 1)) ;;
        esac
        if [ "$ea" != "$eb" ]; then
            bad "[linkage] the elided pattern '$pat' chooses a DIFFERENT engine with the splice denied ('$ea' vs '$eb') — the dead-capture elision is supposed to be independent of the linkage"
            ebad=$((ebad + 1))
        fi
    done <<< "$ELIDED_PATTERNS"
    [ "$ebad" -eq 0 ] && ok "[linkage] all $n NAMED elision patterns reach the DFA engine on BOTH linkage arms — the dead-capture elision is a fact about \`A_REP{0,0}\` emitting nothing, and does not depend on how a call reaches its callee"
}

# ============================================================================
# THE ELISION CONTROL — THE SEMANTIC HALF ([DD-14] wave G)
# ============================================================================
# The sweep above proves the four NAMED patterns emit different BYTES from the
# pre-module reference. That is a fact about the artifact and says nothing about
# what it ANSWERS, and "the engine changed" is exactly the claim that would be
# most damaging if it also changed a span. So this section compares the two
# COMPILED MATCHERS: the reference's (VM) and this build's (DFA), on the same
# subjects, on the whole-match span AND EVERY GROUP PAIR.
#
# THE GROUP PAIRS ARE THE POINT. A dead group must come back UNSET on both
# compilers and at the same NUMBER — which is what libpcre2 10.46 reports for
# the same shapes (`(?(DEFINE)(?<g>a))(x)(?&g)` on "xa": g1 UNSET, g2 (0,1)) —
# and an `m`/`n` comparison could not see a lost one at all.
ELISION_SUBJECTS='
a
b
ab
ba
xa
abc
bb
aab
 b
x'

elision_control() {
    local d="$WORKDIR/elide"
    mkdir -p "$d"
    cat > "$d/drv.c" <<'CEOF'
#include <stdio.h>
#include <string.h>
#include "q.h"
int main(int argc, char **argv) {
    ptrdiff_t caps[Q_NCAPS][2];
    memset(caps, 0x5a, sizeof caps);
    int rc = q_search((const unsigned char *)argv[1], strlen(argv[1]), 0, caps);
    printf("rc=%d ncaps=%d", rc, Q_NCAPS);
    if (rc == 1)
        for (int g = 0; g < Q_NCAPS; g++)
            printf(" g%d=(%td,%td)", g, caps[g][0], caps[g][1]);
    printf("\n");
    (void)argc;
    return 0;
}
CEOF
    local cells=0 bads=0 npat=0
    while IFS= read -r pat; do
        [ -n "$pat" ] || continue
        npat=$((npat + 1))
        local eng_a eng_b
        eng_a="$(pcrec_run "$PCREC" --features all -p rx -o - -- "$pat" 2>/dev/null | grep -m1 '^    \.engine = ')"
        eng_b="$("$REF"   --features all -p rx -o - -- "$pat" 2>/dev/null | grep -m1 '^    \.engine = ')"
        case "$eng_b" in *PCREC_ENGINE_VM*) ;; *)
            bad "[elision] the pre-module reference does NOT choose the VM for '$pat' ($eng_b), so this pattern is not an instance of the change the list names"
            bads=$((bads + 1)); continue ;;
        esac
        case "$eng_a" in *PCREC_ENGINE_DFA*) ;; *)
            bad "[elision] this build does NOT choose the DFA for '$pat' ($eng_a), so the list names a pattern the elision no longer moves"
            bads=$((bads + 1)); continue ;;
        esac
        local ok_build=1
        rm -rf "$d/a" "$d/b"; mkdir -p "$d/a" "$d/b"
        pcrec_run "$PCREC" --features all -p q -o "$d/a/q.c" -- "$pat" >/dev/null 2>&1 || ok_build=0
        "$REF"   --features all -p q -o "$d/b/q.c" -- "$pat" >/dev/null 2>&1 || ok_build=0
        if [ "$ok_build" -eq 0 ]; then
            bad "[elision] '$pat' did not compile on both builds"
            bads=$((bads + 1)); continue
        fi
        # shellcheck disable=SC2086
        $CC -O1 -std=gnu11 -I"$d/a" -o "$d/ta" "$d/drv.c" "$d/a/q.c" 2>/dev/null || ok_build=0
        # shellcheck disable=SC2086
        $CC -O1 -std=gnu11 -I"$d/b" -o "$d/tb" "$d/drv.c" "$d/b/q.c" 2>/dev/null || ok_build=0
        if [ "$ok_build" -eq 0 ]; then
            bad "[elision] a matcher for '$pat' did not build"
            bads=$((bads + 1)); continue
        fi
        while IFS= read -r subj; do
            # THE LEADING BLANK LINE OF `ELISION_SUBJECTS` IS NOT A SUBJECT.
            # Without this guard the count read 44 for 4 patterns x 10 subjects,
            # and a cell count nobody can reproduce from the list above it is a
            # number a reader has to be told about rather than one they can
            # check. (The empty subject is a legitimate thing to test; it is
            # just not what this heredoc's formatting was providing.)
            [ -n "$subj" ] || continue
            cells=$((cells + 1))
            local ra rb
            ra="$("$d/ta" "$subj")"
            rb="$("$d/tb" "$subj")"
            if [ "$ra" != "$rb" ]; then
                bad "[elision] '$pat' on '$subj': this build (DFA) says '$ra', the pre-module reference (VM) says '$rb' — the elision changed an ANSWER, which it must never do"
                bads=$((bads + 1))
            fi
        done <<< "$ELISION_SUBJECTS"
    done <<< "$ELIDED_PATTERNS"
    if [ "$bads" -eq 0 ] && [ "$cells" -ge 40 ]; then
        ok "[elision] all $npat NAMED elision patterns: the pre-module reference chose the VM, this build chooses the DFA, and the two matchers agree on the whole-match span AND EVERY GROUP PAIR over $cells cells — the engine moved and the answer did not"
    elif [ "$cells" -lt 40 ]; then
        bad "[elision] only $cells cells were compared (want at least 40 — 4 named patterns x 10 subjects) — the semantic control is not populated"
    fi
}

for axis in "default:" "vm:--engine=vm" "noprefilter:-fno-prefilter" \
            "nocaptures:--no-captures"; do
    label="${axis%%:*}"; flags="${axis#*:}"
    control "$label" "$flags"
    sweep   "$label" "$flags"
done

linkage_axis
elision_control

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
