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
#
# ============================================================================
# [RECID-A] 2026-10-29 — COMPARISON (A) WAS RE-BASED; READ THIS BEFORE THE REST
# ============================================================================
# Everything below that speaks of (A) as "the program region against the
# UNCHANGED pre-module pin `ac4917d`", of named exceptions (eight of them), of
# canonicalizers and rewrites, of size-term / bref-rename / var / ctx-node /
# lazy-prefix buckets, is HISTORY of how the gate got here and is kept as such
# (the reasons the emitter moved are still true; the machinery that absorbed
# them is gone). The manager ruled RE-BASE, not a ninth exception: the
# never-moving pin had cost two triage lanes and went silently red a third
# time (it runs only in the merge battery), and a ninth exception (K128's
# label renumbering plus the counter rung's split guard/counter slot) would
# have been the same trap again.
#
# WHAT (A) IS NOW. The program region ('goto <p>_L0;' .. '<p>_accept:',
# unfiltered past the D37 stamps, comments included) of every call-FREE corpus
# pattern, on all four axes, against `$ABASEPIN`: a ruled MAIN commit that is
# post-module and already carries every change the exceptions used to absorb.
# There is no exception list and no canonicalizer: a difference is a
# REGION DIFFERS failure, and a landing that moves a call-free region on
# purpose re-pins ABASEPIN in its own commit, exactly as (B)'s FILEPIN moves at
# an abi bump. What survived: the stamp-truth converses (a stamped island /
# fold / literal run / atom table / possessify arm must differ from the SAME
# compiler's own deny build, an unstamped one must not) and their manifests —
# they compare the subject with itself, never with a pin — the elision
# control, and the per-axis POSITIVE CONTROL, which still needs a compiler
# that REFUSES the call spellings, so `$REF` (`ac4917d`) is kept for that and
# for the elision control and for nothing else.
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
# [RECID-A] (the paragraph below is now the pin of the POSITIVE CONTROL and the
# elision control only; (A) itself compares against $ABASEPIN, see above.)
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

# [ENG-ISL] THE ISLAND MANIFEST — an ENUMERATED list of corpus patterns that
# MUST stamp an alternation island, in the same shape and for the same reason
# as ELIDED_PATTERNS above (and the size-term list retired at [RECID-A]): a population RECOMPUTED
# from the emitter is not a manifest, because it agrees with a narrowed emitter
# by construction. Panel r53's F4 is the measured version of that complaint —
# the island bucket's non-vacuity floor was "at least one", so raising
# VM_ISL_MIN_BRANCHES_PREFIXED to 40, or any other narrowing that left a single
# island standing anywhere in the corpus, read GREEN.
#
# EVERY ENTRY WAS VERIFIED UNDER `--engine=vm` AGAINST THE SHIPPED COMPILER,
# and the first version of this list was NOT — it was copied from the answer
# corpus on the assumption that an island-flavoured pattern stamps one, and
# THREE of its eleven did not: `a|b|c|d|e|f|g|h` (altcls MERGES single-byte
# alternatives into a class, so no alternation survives to the emitter),
# `fo|foo|fool` and `(?:x|)y` (both prefix-bearing at widths the narrow-width
# knee declines). The list read GREEN on the default axis, where those three
# route to the DFA and are skipped, and failed only under `--engine=vm`. A
# manifest asserted from memory is the thing this file's other two manifests
# exist to avoid.
#
# They are chosen to span the predicate rather than to be numerous: prefix-free
# at widths 2/3/8, a deep shared prefix, a prefix LADDER (four alternatives on
# one root-to-leaf path, so its candidate chain has a second entry), an empty
# alternative, a cross-product, a capture around the alternation, two
# alternations in one pattern, and one under a counted repeat. A pattern that
# stops stamping an island FAILS here whichever direction the emitter moved:
# either the predicate narrowed — and this list is the record of what that
# costs — or the analysis broke.
ISLAND_PATTERNS='cat|dog|cow
foo|bar
(cat|dog)s
(cat|dog)(s|es)
thin|think|thinker|thinking
cat|cats|dog|dogs
(?:ab|cd|aqr|cst){8}z'
#
# [FORM-CHAR] THE FOLD MANIFEST, `ISLAND_PATTERNS`' shape for the second
# region-moving axis: corpus patterns MEASURED (2026-09-05, this lane's
# whole-corpus stamp census: 11 default-axis / 23 vm-axis patterns stamp
# folds > 0) to stamp `RX_VM_CLS_FOLDS > 0` on the DEFAULT axis — each is
# VM-routed there because it carries a capture, a backreference or an atomic
# group beside its caseless letters, since a capture-free caseless literal is
# a DFA artifact and carries no VM stamp (the same DFA gate the island
# manifest's own comment records the hard way). Chosen to span the
# recognizer rather than to be numerous: a whole-pattern `(?i)` over an
# atomic literal run, a scoped `(?i:...)` on one position feeding a
# backreference, a mid-pattern `(?i)` turning exactly one position into a
# pair, and a caseless possessive whose fold class sits under a quantifier.
FOLD_PATTERNS='(?i)(?>abc)
^(?i:(a))\1$
(a(?i)b)C
(?i)a*+A'
#
# [OPT-LITSCAN] S2a THE LITERAL-RUN MANIFEST, the fold manifest's shape for
# the third region-moving axis (-fno-lit-run): corpus patterns
# (tests/litscan/litrun.rxt) that MUST stamp `RX_VM_LIT_RUNS > 0` wherever
# they are VM-routed — runs on both sides of a capture, a run before a push,
# and an island whose single-child chains are runs. (`(abc){2}x` is NOT one:
# a fixed-length repeat body takes the cursor rung, whose own `&&` chain S2a
# leaves alone — tuning.md §2.31. Measured, when it was first listed here.)
# [OPT-LITSCAN] F5 (D127, 2026-09-28): `xy(a|ab)c`'s run before the push was
# TWO bytes, which is now below pcrec_lit_run's own floor -- it stamps
# RX_VM_LIT_RUNS 0 (MEASURED), and a manifest entry asserting ">0" would go
# red for a reason that has nothing to do with the manifest's own claim.
# Replaced with `xyz(a|ab)c`, the same shape at three bytes, re-verified to
# stamp RX_VM_LIT_RUNS 1 and carry the one-compare "xyz" memcmp.
LIT_PATTERNS='x(abc)defg
xyz(a|ab)c
foo(?:username|password|passphrase)bar'
#
# [ART-POSS-ARMS] (abi 66) THE FIFTH REGION-MOVING AXIS PAIR, the possessify
# ARMS (`-fno-poss-ctx-follow` / `-fno-poss-bref-first`, tuning.md §2.44/
# §2.45): a mover's possessified loop emits no retreat. Its excuse is the
# same stamp-or-deny claim as the four above, read off
# `RX_VM_POSS_ARMS` (nonzero, and denying BOTH arms restores the pin), and
# its non-vacuity arm is this NAMED manifest: the three corpus movers of
# docs/design/poss_arms.md §5.2 (A1: tests/assertions/wordb_vm.rxt,
# tests/startset/hybrid.rxt; B: tests/startset/vmhat.rxt), each of which
# must stamp a nonzero arm on every VM axis.
POSS_PATTERNS='(\b\w+\b)
\b(\w+)\s+\1\b
\B(x|ab){1,2}\b'
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
. "$ROOT_DIR/tests/lib/lib_srcs.sh"   # [MEMFN] R4a: the library's source list (src/ + memfn/src/)
. "$ROOT_DIR/tests/lib/cc_resolve.sh"   # [MACPORT] resolves a real GNU gcc when bare gcc is Apple clang
SANFLAGS="${SANFLAGS:-}"
KEEP="${KEEP:-0}"

# [recidfix->varland, tests/mech S273] THIS GATE NEEDS A REAL GIT REPOSITORY
# WITH FULL HISTORY, and it needs to SAY SO rather than report a false FAIL,
# which is a DIFFERENT claim from "the pin does not resolve" below. Both
# `$REFCOMMIT` and `$FILEPIN` are built via `git -C "$ROOT_DIR" archive
# <commit-ish>`, and `tests/mech/run_sabotage_matrix.sh`'s scratch trees are
# `git archive HEAD | tar -x` with NO `.git` directory AT ALL (its own MECH-2
# rule) -- discovered live wiring `recidentity` in as this gate's first mech
# arm: `git -C "$tree" rev-parse --verify ac4917d^{commit}` fails with "fatal:
# not a git repository" regardless of whether a sabotage is applied, so an
# earlier version of this check read `bad()`/FAIL unconditionally -- a
# FALSE DETECTED on every row, the worst kind of control (`docs/dev/
# learnings.md` §3): one that reports the same verdict whatever the tree
# contains. `atomicidentity`/`brefidentity` (this file's siblings,
# `run_atomic_identity.sh`/`run_backref_identity.sh`) build their own pinned
# reference the identical way and are "REGISTERED AND RESERVED WITH ZERO
# ROWS" in `tests/mech/CLAUDE.md` -- now explained: nobody has wired a row to
# either, so nobody has hit this.
#
# THE DISTINCTION THAT MAKES THIS A SKIP AND NOT A FAIL: "this tree has no
# git history at all" is an ENVIRONMENT LIMITATION (no oracle, `pc3`/
# `laexpand`'s own shape), never a claim about whether either pin is right.
# "$ROOT_DIR is a git repo but $REFCOMMIT/$FILEPIN do not resolve IN it" is
# still the real, load-bearing FAIL this file's later checks give it credit
# for saying loudly ("a gate that cannot build its reference must SAY so
# rather than skip") -- that sentence is right about a WRONG PIN and wrong
# about a git-archive scratch tree, which was never a case its author had in
# view.
if ! git -C "$ROOT_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "SKIP: $ROOT_DIR is not inside a git working tree at all (no .git found in any parent) -- this gate needs FULL GIT HISTORY to git-archive its two pinned commits (the pre-module reference and the current abi's file pin, both resolved further down) and cannot tell 'no history available here' from 'the pin itself is wrong' without one. Structurally unrunable inside a git-archive-only scratch tree (tests/mech/run_sabotage_matrix.sh's own MECH-2 shape); run it against a real checkout instead." >&2
    echo "checks passed: 0"
    echo "checks failed: 0"
    exit 0
fi

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
# (B) THE WHOLE FILE, against a pin MOVED FORWARD to `c940551` (2026-08-26).
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
# Pin was `469a432` ([OPT-1]'s, immediately before this change) and `5991d4c`
# ([DD-13]'s) before that. Within THIS change it moved twice — the pin must
# always name the change's LAST src/lib/cli commit, and both the rx_info fields
# and the rebase onto [OPT-1] made a later one each time.
# [OPT-3], 2026-08-26 — THE FIRST RE-PIN BY A CHANGE THAT MOVES EMITTED
# PROGRAM BYTES, and that is the difference worth one paragraph. [DD-13],
# [OPT-1] and [DD-13c] were all scaffolding (the last one plus a struct
# append), and each of their notes below says so. The PRE-MULTIPLIED DFA
# TRANSITION TABLE (docs/design/premultiplied_dfa_table.md) changes the DFA
# scan's tables, its state variables, its dead test and its transition line on
# every artifact that CONTAINS such a scan — DFA artifacts and VM HYBRIDS
# alike, since the hybrid inlines `emit_unanchored`'s own output.
#
# COMPARISON (A) IS STILL EXPECTED BYTE-IDENTICAL, and here that is a real
# check rather than a formality: `prog_region` is `goto <p>_L0;` through
# `<p>_accept:`, i.e. the VM PROGRAM, and a hybrid's inlined
# `static <prefix>_prefilter` is emitted ABOVE that `goto` (verified on a
# current hybrid artifact: `rx_prefilter` at line 250, `goto rx_L0;` at 396).
# So (A) sees no DFA scan byte at all. If it ever DOES move under this change,
# the finding is that the region extractor has stopped bounding what its
# comment says it bounds — not that the transform touched the VM.
#
# `abi` 6 -> 7 and (B) re-pinned here, to `8272a15` — this change's LAST
# commit touching `src`/`lib`/`cli`. Pin was `c940551` ([DD-13c]'s). Within
# THIS change it moved THREE times, and the moves are the rule working rather
# than churn: `49356e8` first; then the MEASUREMENT deleted §7's size budget
# from `dfa_premul` (`4ff4d41`), which really does move emitted bytes on every
# machine between 16,384 and 65,535 entries — and (B) at that pin is what
# proved it caught them; then `8272a15` derived the bound FROM the sentinel,
# a change measured to move NO emitted byte (400 corpus patterns, 0
# differences) and re-pinned anyway, because D76's rule is mechanical — "the
# pin must always name the change's LAST src commit" — and a pin that is
# right only when someone judges a change harmless is not a pin. [DD-13c]'s
# own note records the same thing happening twice there.
#
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
#
# [OPT-K], 2026-08-28: `abi` 8 -> 9, (B) re-pinned to `667c615`. The
# OFFSET-k CANDIDATE-START SKIP (docs/design/offset_k_skip.md) gives every
# DFA artifact a `<PREFIX>_DFA_PREFILTER_OFFSETS` stamp line and gives an
# artifact that SELECTS the form a file-scope `<prefix>_ofsskip` block, up to
# three candidate tables and a changed prefilter body. Like [OPT-3] and
# [ENG-FORM] it moves emitted PROGRAM bytes and not scaffolding only, so (A)
# is NOT expected byte-identical for a pattern the form reaches — but this
# gate's population is the CALL-FREE bucket compared on the PROGRAM REGION,
# and the skip lives in the prefilter block ABOVE that region, so (A) is
# unmoved in fact as well as in principle.
#
# THE PIN MOVED ONCE INSIDE THIS CHANGE, which is worth recording because D76
# says "this change's LAST src-touching commit" and a multi-commit change has
# more than one candidate. It was first set to the merge that carries both this
# lane's src and main's [SEL-1] (`667c615`); MISCOMPILE-1's fix then moved
# emitted bytes again (`20383b6`, the offset-0 verify's own table), and within
# one `abi` number the emitted output must be byte-exact whole-file — so the
# pin follows the last src commit rather than the first.
#
# [ENG-ABS], 2026-08-29: `abi` 9 -> 10, (B) re-pinned to `14d1feb`. The
# ANCHORED MATCH-HERE FORM (docs/design/anchored_match_unwrapped.md) gives
# every DFA artifact a `<PREFIX>_DFA_MATCH` stamp line, every artifact of
# EITHER engine an `rx_info.match_form` member, and an artifact that SELECTS
# the form a file-scope `<prefix>_anchored_state` accessor block, a THIRD
# machine's tables inside `<prefix>_match`, and rewritten `_match`/
# `_match_caps` bodies. Like [OPT-3], [ENG-FORM] and [OPT-K] it moves emitted
# PROGRAM bytes and not scaffolding only — but every byte it writes on a VM
# artifact is that one struct member, which sits ABOVE `goto <p>_L0;`, so (A)
# is expected byte-identical against the unchanged `ac4917d` and is not merely
# unmoved in principle.
#
# [ART-SIZE], 2026-08-29: `abi` 10 -> 11, (B) re-pinned to `b3cf716`.
# **THE PIN MOVES WITH THE LAST SCAFFOLDING CHANGE OF THE `abi`, NOT THE
# FIRST — RE-RUN THIS GATE AFTER EVERY src-TOUCHING COMMIT THAT FOLLOWS A
# RE-PIN.** That sentence is here because this row broke it: the pin was set
# to `60a51ed` (the shared-sites commit) and TWO more src commits then landed
# — `5199823`, which gives every DFA artifact a `<PREFIX>_MAX_EMIT_BYTES`
# line, and `b3cf716`, the declared-capacity floor. Within one `abi` the
# emitted output is byte-exact whole-file, so the stale pin made (B) report
# EVERY DFA-selected call-free pattern as differing: measured
# `[default] (B) same=1268 differing=952`, while `[vm]` read 2225/0 because
# VM artifacts had their four stamps BEFORE the pin. Caught by the r42 panel,
# not by this gate's own run, which is the reason the rule is now written
# where the pin is set rather than left to be re-derived.
#
# [OPT-4], 2026-08-29: `abi` 11 -> 12, (B) re-pinned to `2ed6402`. THE
# PREFILTER'S LANGUAGE STAMP (K39; docs/design/prefilter_count_independence.md).
# **COMPARISON (A) IS EXPECTED BYTE-IDENTICAL AND THAT IS A REAL CHECK HERE,
# NOT A FORMALITY, because the change looks like a program change and is not
# one.** Above `PCREC_PREFILTER_EXACT_NFA_STATES` a VM hybrid's prefilter is
# built from the count-collapsed language, which drops the artifact's
# `prefilter-window` MRL ceiling — but `v.mrl_win`'s three readers all sit in
# `<prefix>_search` and its retry recompute, ABOVE `prog_region`, and the
# per-quantifier clamp reads `window_end` as a PARAMETER. So the number moves
# and the emitted PROGRAM does not; measured at 116 identical region lines on
# `((a)|b){0,4000}c`, and this gate is what says so corpus-wide. (B) moves
# because every VM hybrid gains a `<PREFIX>_VM_PREFILTER_LANG` line, its
# `<PREFIX>_VM_PREFILTER_LANG_WHY` companion (D81; added at `d4d439e`, which is
# why the pin moved off `2ed6402`), and, on the artifacts over the knee, a
# smaller inlined prefilter.
#
# THE PIN MOVED AGAIN FOR FRANK'S RULING B (2026-08-29): `c275aef`, this
# lane's last src-touching commit. Ruling B made the EXACT prefilter the
# default and turned the collapse into a ladder attempt, so (B) moves on the
# few artifacts whose `_LANG_WHY` value changed spelling and (A) does not move
# at all — the language decision has never been in `prog_region`. The pin
# before it was `82229fc` — [OPT-4]'s `<PREFIX>_ENGINE_SEL`
# commit, which is the LAST scaffolding change of this row and the one that
# matters most to (B). Unlike the two before it (the [SEL-1] rung, which moves
# WHICH artifacts have a prefilter rather than any emitted text this gate
# compares, and the `--emit-ir` ceiling-text fix, which is not emitted C at
# all), `_ENGINE_SEL` adds a line to EVERY artifact on BOTH engines, so (B)
# moves corpus-wide here and (A) still does not — the new line sits in the
# stamp block, above `prog_region`.
#
# THE PIN TRAVELS WITH THE LAST SCAFFOLDING CHANGE, NOT THE FIRST, which is the
# rule one paragraph down said in other words and is worth saying in these:
# pinning to the commit that first moved a byte leaves every later commit in
# the same change comparing against a stale reference. This row moved it four
# times (2ed6402 -> d4d439e -> fefcea1 -> 6f8e9d3 -> 82229fc) for exactly that
# reason, and the abi stayed 12 throughout — one bump per CHANGE, several pins. (No count is given
# here on purpose: how many artifacts collapse is a property of the POPULATION
# being swept, and this gate's corpus is not the size log's 1,388 hybrids nor
# `run_prefilter_collapse.sh` §5's 2,772 `pattern` lines. Each check floors its
# own.)
#
# THE PIN IS THIS CHANGE'S LAST src-TOUCHING COMMIT, [OPT-K]'s note one
# paragraph up having recorded why that matters in a multi-commit change:
# `14d1feb` moved the `match_form` member's comment ABOVE the member (a
# measured 691 B per artifact of the size log's comment classifier), which is
# emitted text, so the pin follows it rather than the commit that introduced
# the member.
# [OPT-5], 2026-08-31 — THE SECOND RE-PIN BY A CHANGE THAT MOVES EMITTED
# PROGRAM BYTES, and the FIRST by one that moves a MACHINE. The DFA scan edge
# replaces a counted class run's states with one bounded cursor loop and
# DELETES the run's interior from every per-state table, so (B) moves on every
# artifact whose machine carries such a run — `[a-z]{0,16384}`'s forward
# machine goes from 16,385 states to 2 — and EVERY artifact gains the
# `<PREFIX>_DFA_SCAN_EDGE` stamp line. `abi` 12 -> 13.
#
# (A) IS STILL EXPECTED BYTE-IDENTICAL, and here that is a real check rather
# than a formality: its `prog_region` is the VM PROGRAM, and a hybrid's
# inlined DFA prefilter is emitted ABOVE that region — so this change reaches
# no VM program byte even on the artifacts whose prefilter it rewrites.
#
# [CC-CLANG], 2026-08-31 — THE THIRD RE-PIN, AND (A) IS STRUCTURALLY
# UNTOUCHED RATHER THAN MERELY UNTOUCHED ON THIS POPULATION. `prog_region`'s
# own awk range (`/^    goto rx_L0;$/,/^rx_accept:/`) stops AT the accept
# label, inclusive — the fail label and everything after it (the resume
# dispatch this change makes conditional) sits entirely OUTSIDE that range on
# every artifact, call-free or not, so (A) cannot see this change at all. The
# `__has_attribute` guard is likewise above `goto <p>_L0;`. `abi` 13 -> 14.
#
# THE PIN IS THIS CHANGE'S LAST src/lib/cli-TOUCHING COMMIT, per the rule two
# paragraphs up: `ec6f481` (a FIFTH src commit in the same change — the
# CLANGGEN=1 sweep mechanism [CC-CLANG] step 2 built found a THIRD, distinct
# clang incompatibility on its very first small-scale run: the revdet
# rung's `iteration` counter is write-only under a bare unbounded `X*`
# (gcc's -Wunused-but-set-variable does not catch a write-only local
# reached only through `x++`; clang's does), fixed by adding it to the
# file's own existing per-loop `(void)`-cast list one line above, which
# also corrects that comment's wrong claim that `iteration` is used by
# every shape. Both the block this touches and everything from the
# previous four re-pins sit BEFORE `goto <p>_L0;` or after `<p>_accept:`,
# so (A) is unaffected by any of them; only (B) moves. Emitted bytes moved
# again, past the four earlier pin attempts at `c657ae9`, `8e0b624`,
# `353306a` and `c13fd7b`) — not the commit that first moved a byte and not
# any later test-only commit. Pin was `dc2c8ef` ([OPT-5]'s).
#
# [OPT-4.2], 2026-09-01 — RE-PIN WITHOUT A BUMP, the [OPT-4.1] precedent:
# `ESEL_DECLINED_NULLABLE_DEFAULT` moves the `RX_ENGINE_SEL` stamp VALUE on
# ~50 corpus artifacts (a value, not scaffolding — abi stays 14, D76), so
# those artifacts differ whole-file against `ec6f481` while (A) is
# 0-differing on every axis. Pin was briefly the lane/o42 merge `ff13660`.
#
# [CC-CLANG fix], 2026-09-01, same day — RE-PIN AGAIN, to `adc0f5a`: the
# has_push miscompile fix (journal 2026-09-01 part 2) RESTORES the
# pop-and-resume dispatch on unbounded-counter artifacts whose npush
# estimate had gone negative, and derives the gate from the emitted text —
# bytes move on that population (all AFTER `<p>_accept:`, so (A) is again
# untouched), abi stays 14 (which artifacts carry the conditional dispatch
# changed; the scaffolding scheme did not).

# [DD-13b.W1.2], 2026-09-01 — abi 14 -> 15 at the w12 MERGE (6dbdf41): the
# appended rx_info.name/.nentries members move two initializer lines and two
# shared-block declarations on EVERY artifact of both engines (whole-file
# bytes, so (B) re-pins to the merge commit); no struct offset and no program
# byte moves, so (A) is untouched — the branch's own gate run measured (A)
# 0-differing on all four axes, and the final number 15 was assigned at the
# merge behind [CC-CLANG]'s 14 (D76 merge-order rule; site list per D94,
# every reader found by grep).
REFCOMMIT="${RECURSION_IDENTITY_REF:-ac4917d}"
# [OPT-5] STEP 2, 2026-09-02 — abi 15 -> 16 at the opt5i MERGE (da4fe60): the
# start-pinned search elision (axis J, RX_DFA_START, rx_info.search_form
# appended after nentries) + RX_VM_FRAMELESS (ruling R1) move dispatch bytes
# on the 175 pinned artifacts and stamp lines on every VM artifact; re-pinned
# to the merge per D76/D94 (readers of the old pin found by grep).
# [CC-DIFF] STEP 1, 2026-09-03 — abi 16 -> 17: the always_inline attribute on
# a FRAMELESS VM artifact's eight entry-chain statics (function headers only;
# a FRAMED artifact is byte-identical), and the uniform-table fold, which
# deletes `<m>_next_state` / `<m>_is_accepting` and rewrites their accessors
# and call sites on any machine whose table is all-equal, plus a
# `<PREFIX>_DFA_UNIFORM_FOLDS` stamp line on every artifact containing a DFA
# scan. Whole-file bytes move on both populations, so (B) re-pins.
#
# (A) IS UNTOUCHED BY BOTH HALVES, AND THIS IS A STRUCTURAL FACT CHECKED BY
# READING THE EMITTER, NOT AN ASSUMPTION. `prog_region()` below extracts only
# the span from `goto <p>_L0;` to `<p>_accept:` -- the VM's own program body.
# Spelling (a)'s eight statics are all DEFINED above that span (the last,
# `<prefix>_run_state_bind`, at src/gen/emit_vm.c:9309, well before "the
# program" begins at :9425); a FRAMED artifact carries none of the attribute
# at all. Spelling (b)'s fold lives inside `pcrec_emit_dfa_engine`, which for
# a HYBRID is called from emit_vm.c's own prefilter block (:9421) -- ALSO
# before the program marker -- and a non-hybrid DFA artifact has no `goto
# <p>_L0;` at all, so `prog_region()` returns empty on both sides of the
# comparison regardless of what the DFA scan emits. So this population's
# `rdiff` stays 0 on this change on both counts, and a NONZERO one would mean
# something else moved, not that this change reached the region: verified by
# byte offset on a hand-built hybrid (`(x)[a-z]{0,4}\z --engine=vm
# -fprefilter`) before trusting the corpus run to confirm it at scale.
#
# [ENG-ISL] STEP 1, 2026-09-03 — abi 17 -> 18. THE VM'S ALTERNATION ISLAND,
# AND IT IS THE FIRST CHANGE IN THIS FILE'S HISTORY THAT MOVES COMPARISON (A)
# ON PURPOSE. Every bump above says "(A) is still expected byte-identical, and
# here that is a real check rather than a formality"; each of them was a change
# ABOVE the `goto <p>_L0;` marker — stamps, entry chains, DFA tables, a
# prefilter. This one is the VM PROGRAM ITSELF: a flat alternation whose whole
# subtree matches a finite set of literal byte strings is emitted as a TRIE
# (a byte compare per single-child node, a switch per fan-out node, one try
# site per node where an alternative ends) instead of `vm_alt`'s serial resume
# chain. `prog_region` is exactly where that happens, so of course it moves.
#
# THE EXEMPTION IS A CLAIM ABOUT THE DENY AXIS, NOT A PER-ARTIFACT ALLOWANCE.
# The first version of this bucket excused any byte difference anywhere in an
# artifact whose `RX_VM_ALT_ISLANDS` read > 0 — and `prog_region` extracts the
# WHOLE program, so an unrelated emitter regression inside an island-bearing
# artifact read green (panel r53, F3). What is asserted now: a moved region is
# excused IFF building the SAME pattern with the SUBJECT compiler under
# `-fno-alt-island` restores the PINNED region byte for byte. Denying the new
# axis has to put the artifact back where the pin left it; anything else that
# moved is not the island's to excuse and lands in `rdiff`.
#
# THE CONVERSE IS SELF-CONTAINED AGAINST THAT SAME AXIS (F5), because the
# obvious spelling decays. "Stamped but byte-identical to the August pin"
# stops being able to fail as soon as any other change lands — the two differ
# for that reason instead, and the converse passes for the wrong one. Both
# directions are about THIS compiler: an artifact that STAMPS an island must
# differ from its own `-fno-alt-island` build, and one that does NOT must be
# byte-identical to it, which is also what makes the denied build a usable
# reference for every other check that leans on it.
#
# THE NON-VACUITY FLOOR IS AN ENUMERATED MANIFEST (`ISLAND_PATTERNS`), NOT A
# COUNT (F4). "At least one island moved" was argued rather than measured and
# read GREEN under any narrowing that left a single island standing anywhere —
# raising `VM_ISL_MIN_BRANCHES_PREFIXED` to 40 passes it. The manifest is the
# same staleness assertion `ELIDED_PATTERNS` and (until [RECID-A]) `SIZE_TERM_REGION_MOVERS`
# already carry, and for the same reason: a population recomputed from the
# emitter agrees with a narrowed emitter by construction.
#
# AND THIS IS A BYTE-INEQUALITY GATE, NOT A CORRECTNESS GATE. Nothing here
# says the island ANSWERS correctly; it says which bytes moved and licenses
# exactly one reason for them to have moved. Correctness is the answer corpus
# (`tests/island/`, oracle-verified against python3 `re`) and `make test-axes`
# (`-fno-alt-island` answer-identical over 22,407 corpus cells). A reader who
# takes a green run here as evidence the island matches correctly is reading
# the wrong instrument.
#
# WHAT IS **NOT** EXEMPT, and this is what the bucket buys: a call-free
# pattern whose region moved while its artifact stamps ZERO islands still
# lands in `rdiff` and still fails. That is the pre-module pin doing exactly
# the job it has always done, on the population this change does not touch.
#
# (B) re-pins as usual: every VM artifact gains a `<PREFIX>_VM_ALT_ISLANDS`
# line whatever its value, so whole-file bytes move on the whole VM
# population, island or not.
#
# THE PIN VALUE BELOW IS THE MANAGER'S AT MERGE, NOT THIS LANE'S: it must be
# the last src commit of the change as it lands, and a lane branch cannot know
# that commit. (The lane left it at da4fe60 (abi 16); the manager re-pinned it
# to the merge a3f40b1 below.) The lane's build compared
# against the PRE-change reference and its (A)/(B) numbers are readable as the
# change's own footprint. Re-pin to the merge before the merge is called done
# (D76/D94).
# [DD-13b.W1.3], 2026-09-04 — abi 17 -> 20 at this step's LAST src-touching
# commit (d794a8d8, the abi bump itself). THE LAST AND NOT THE FIRST: this
# file's own rule at :394-406 binds, and getting it backwards cost 952
# falsely-differing artifacts once. Composition moves NO byte of any artifact
# built without `--source` — MEASURED at 176 artifacts / 0 differing against a
# compiler built from main — so comparison (B) is expected to be 0-differing
# across the whole call-free corpus at this pin, exactly as it was at the last.
#
# [CC-DIFF] STEP 1, 2026-09-03 — abi 16 -> 17 at the ccdiff1b MERGE (a3f40b1): the
# always_inline attribute on frameless VM helpers and the uniform-table fold
# (RX_DFA_UNIFORM_FOLDS) move bytes on 1,090+ VM artifacts and ~370 DFA
# artifacts; re-pinned to the merge per D76/D94 (readers of the old pin by grep).
#
# [ENG-ISL] STEP 1, 2026-09-03 — abi 17 -> 18: the VM's ALTERNATION ISLAND.
# EVERY VM artifact gains a `<PREFIX>_VM_ALT_ISLANDS` line whatever its value,
# so whole-file bytes move on the entire VM population — island or not — and
# (B) re-pins for that alone. MEASURED against the previous pin before the
# re-pin, so the change's own footprint is on the record: 1,274 (default),
# 2,284 (vm), 1,274 (noprefilter) and 857 (nocaptures) call-free patterns
# differ whole-file, and the [vm] axis's `same` fell to 0, below the sweep's
# own 700 floor — which is the stamp being unconditional working as designed.
# Comparison (A) is a different matter entirely and has its own entry above:
# it moves ON PURPOSE for the first time in this file's history, under an IFF
# rather than an allowance.
#
# THE PIN IS THIS LANE'S OWN LAST src COMMIT (cee7c741, the MERGE of lane/isl1 — re-pinned by the manager at landing; the lane's own last src commit was cf95944, panel r53's SEMANTICS
# lens: the island-vs-chain size rule AND its cap guard, which together decline
# a population the earlier pins were built with — it moved past 9bc7723, the abi ritual, when the Q4 width knee landed
# after it and moved 96-141 artifacts per axis), set in a follow-up commit that
# touches no src — which is what keeps the rule two
# paragraphs up ("the pin must always name the change's LAST src commit")
# true of a lane that writes its own bump. The manager re-pins to the MERGE
# when it lands, exactly as at every bump before this one.
#
# [OPT-EDGE] STEP 1, 2026-09-04 — abi 17 -> 19 (18 is [ENG-ISL] STEP 1's, which
# merges first): the SHARED-SENTINEL SCAN-EDGE DISPATCH. On any DFA machine
# carrying a scan edge the edge heads are renumbered to the machine's TOP rows,
# one extra accessor `<prefix>_<m>_is_stop` is emitted, the loop's one
# per-iteration state test answers dead-or-head, and the per-edge blocks move
# off the generic path — so whole-file bytes move on every edge-bearing
# artifact and (B) re-pins. An artifact with NO scan edge is byte-identical to
# abi 17.
#
# (A) IS UNTOUCHED BY THIS ONE TOO, and for the same structural reason the
# paragraph above gives about spelling (b): `prog_region()` extracts only
# `goto <p>_L0;` through `<p>_accept:`, the VM's own program, and everything
# [OPT-EDGE] emits lives inside `pcrec_emit_dfa_engine` — which for a HYBRID is
# called from emit_vm.c's prefilter block ABOVE that marker, and which a
# non-hybrid DFA artifact reaches with no `goto <p>_L0;` in the file at all, so
# `prog_region()` returns empty on both sides. K43 (b) would have moved
# `<prefix>_run_state_init`, also above the marker; it was DROPPED from this
# event on measurement and moves nothing now.
#
# THE PIN VALUE BELOW IS THE MANAGER'S AT MERGE (386abf94, the merge of lane/edge1), not this lane's — the lane
# leaves it at the previous pin, because a pin must name a commit reachable
# after the merge and a lane branch's is not (opt5i's and ccdiff1's precedent).
#
# [FORM-CHAR] STEP 1, 2026-09-05 — abi 22 -> 23 (or later if a concurrent
# lane's event serializes ahead; the merging session renumbers, D94): the
# VM's ASCII-FOLD CLASS TEST. A two-member pool class that is an ASCII fold
# pair (differing only in bit 0x20, both letters — what D23's parse-time
# caseless folding produces) tests as `(byte | 0x20) == lower` and its
# 32-byte `<prefix>_class_bitmap<N>` table is NOT emitted; EVERY VM artifact
# gains a `<PREFIX>_VM_CLS_FOLDS` activity-count line whatever its value, so
# (B) re-pins on the whole VM population. The VM PROGRAM REGION moves on
# exactly the fold-bearing population — the SECOND change in this file's
# history to move comparison (A) on purpose — so (A)'s excuse machinery
# gains the fold as a second deny axis on the island's own terms: a moved
# region is excused IFF denying exactly the stamped region-moving axes
# (`-fno-alt-island` and/or `-fno-cls-fold`, per the artifact's own stamps)
# restores the PINNED region byte for byte, both converse directions are
# asserted against the deny axis, and `FOLD_PATTERNS` is the enumerated
# non-vacuity manifest (11 default-axis / 23 vm-axis corpus patterns stamp
# folds > 0, measured 2026-09-05).
#
# THE PIN IS THIS LANE'S OWN LAST src COMMIT (set in a follow-up commit that
# touches no src, [ENG-ISL]'s precedent for a lane that writes its own
# bump); the manager re-pins to the MERGE when it lands.
#
# MANAGER RE-PIN AT MERGE, 2026-09-05 (05b2fe8a — the merge of lane/utf8s2,
# the SECOND lane of the same night): the pin names the first commit whose
# tree carries BOTH the fold form (abi 23, the entry above) and [M5.0]
# STAGE 2's utf8 backend. Stage 2 moved NO byte-encoding artifact byte —
# its own gate ran 14/14 with `.abi = 22` unchanged pre-merge, and its
# confirmatory size-log diff was column-identical on all 2,962 rows — so
# the abi number stays 23 and this re-pin is the ordinary merge-serialization
# move, not a second event. Later same-night commits touch tests/docs only.
#
# [K50], 2026-09-06 — abi 23 -> 24 (or later if a concurrent lane's event
# serializes ahead; the merging session renumbers, D94): CANDIDATE MATCH
# STARTS ARE THE ENCODING'S CHARACTER BOUNDARIES, plus the caller-startpos
# guard. EVERY artifact of both engines gains two lines — the
# `PCREC_ERR_STARTPOS (-7)` define in the shared ABI block and a
# `<PREFIX>_STARTPOS_GUARD` selection stamp in the shared prologue — so (B)
# re-pins on the whole population, `byte` artifacts included.
#
# **COMPARISON (A) IS EXPECTED BYTE-IDENTICAL AND THAT IS THIS ROW'S OWN
# ACCEPTANCE CONDITION, not a formality.** K50's whole risk is that a fix for
# a `utf8` defect moves the encoding that has no defect. Nothing here is
# `byte`-conditional: the `byte` backend supplies no character-start set, so
# `pcrec_nfa_wrap_unanchored` builds its pre-K50 two states, the class axis never
# produces `UPC_NOSTART`, `eqclasses` performs no fourth refinement,
# `ENG_ATTEMPT`'s loop gains no boundary `continue`, and the entries emit no
# guard. A red (A) on this corpus — which is entirely `byte`-compiled — means
# a `byte` path acquired the gate, and is the finding, not a re-pin.
#
# **NO NEW DENY-AXIS EXCUSE RIDES THIS EVENT**, unlike [ENG-ISL]'s and
# [FORM-CHAR]'s. Those two move (A)'s region on a population a `-fno-` flag
# can restore, so each had to teach (A) an IFF. `-fno-startpos-guard` restores
# nothing on this corpus, because nothing on this corpus was moved: the flag
# addresses the CALLER-side half and this corpus compiles for `byte`.
#
# THE PIN IS THIS LANE'S OWN LAST src COMMIT (set in a follow-up commit that
# touches no src, [ENG-ISL]'s precedent); the manager re-pins to the MERGE
# when it lands.
#
# [PORTFIX], 2026-09-14 — abi 24 -> 25 (or later if a concurrent lane's event
# serializes ahead; the merging session renumbers, D94): A CLANG-COMPATIBILITY
# LABEL FIX. Every scan-edge-bearing DFA machine (or VM-hybrid inlined
# prefilter) gains a trailing `;` on its `scan_views` and `scan_edge` labels
# (`<p>_<m>_scan_views:` -> `<p>_<m>_scan_views:;`, same for `scan_edge`),
# closing a label-immediately-followed-by-a-declaration shape (`view_decl`'s
# `<dir>_view_state` assignment) that gcc accepts as a `-std=gnu11` extension
# and clang 21 rejects as `-Wc23-extensions` under `-Werror`
# (docs/dev/lanes/anchtriage_report.md §1) — so (B) re-pins on the whole
# scan-edge-bearing population; an artifact with NO scan edge at all gains
# nothing.
#
# **(A) IS UNTOUCHED BY THIS ONE TOO, and for the same structural reason
# [OPT-EDGE] STEP 1's abi-18-19 entry above gives**: `prog_region()` extracts
# only `goto <p>_L0;` through `<p>_accept:`, the VM's own program, and both
# labels this row touches live inside `pcrec_emit_dfa_engine` — called from
# `emit_vm.c`'s prefilter block ABOVE that marker for a HYBRID, and reached
# with no `goto <p>_L0;` in the file at all for a non-hybrid DFA artifact, so
# `prog_region()` returns empty on both sides either way.
#
# THE PIN IS THE MERGE COMMIT (re-pinned by the manager at the lane/portfix
# merge, 2026-09-15, per D76 and the opt5i/ccdiff1 precedent the lane's own
# note here anticipated: a pin must name a commit reachable after the merge,
# and the lane deliberately left it unset for the manager to set — see
# docs/dev/lanes/portfix_report.md).
#
# [OPT-DIAL], 2026-09-16 — abi 25 -> 26 (or later if a concurrent lane's
# event serializes ahead; the merging session renumbers, D94): THE
# SPEED-VS-SIZE DIAL. Every artifact of both engines gains exactly ONE line
# in the shared prologue, `#define <PREFIX>_TUNE "<token>"` — a closed
# five-token selection stamp, 23-28 bytes by token — so (B) re-pins on the
# WHOLE population, `byte` and `utf8`, DFA and VM alike.
#
# **(A) IS UNTOUCHED, for the plainest reason any row in this list has
# given.** The stamp line sits in the shared prologue, above `goto
# <p>_L0;`, so `prog_region()` reads neither side of it. Nothing else moves
# at the DEFAULT dial position `balanced` either: every cell of that row in
# `src/core/tune.c` is the em-dash sentinel and its deny mask is empty, so a
# `balanced` build cannot differ from a build with no `--tune` flag at all
# on any axis this file or any other checks — a non-default `--tune`
# position is a separate population this corpus never reaches (this script
# passes no `--tune` flag anywhere), so a red here from this change would
# mean the DEFAULT position itself moved, which is the finding, not a
# re-pin exemption.
#
# [EMIT-VERB], 2026-09-19 — abi 26 -> 27. THE EMITTED-COMMENT AXIS (D112).
# A default artifact no longer carries its NON-ESSENTIAL prose: every comment
# LINE leaves every artifact of both engines except the generated-by/
# pattern-echo provenance line and the shared PCREC_RX_ABI_H type block's
# doc-comments. `-fcomments` restores the rest. Measured 44.2% of a default
# artifact's source bytes over the 3,517 compiling corpus patterns.
#
# **(A) IS TOUCHED BY THIS ONE, and not marginally** — `prog_region()` reads
# the VM program between `goto <p>_L0;` and the accept label, and every label
# in that region carries a `// <role>` line the default no longer emits. So
# comparison (A)'s reference artifacts move for the FIRST TIME on a change
# that adds no code: the region shrinks by its role comments and by nothing
# else. That is why this bump re-pins (B) rather than claiming an exemption,
# and why `make test-codegen` is the suite that had to run before delivery.
#
# **WHAT DOES NOT MOVE, and it is the bump's own acceptance criterion**: the
# OBJECT FILE (byte-identical under both settings on 3,517 of 3,517 corpus
# artifacts), the comment-EXCLUDED source size, and every emitted `#define`.
# No cap, no refusal and no answer moves — see docs/spec/tuning.md §2.24.
#
# THE PIN IS THIS LANE'S OWN LAST src COMMIT ([ENG-ISL]'s precedent,
# restated above); the manager re-pins to the MERGE when it lands.
#
# [EMIT-VERB]: LEFT AT THE PRE-BUMP VALUE AND **OWED TO THE MANAGER**, on
# opt5i's and ccdiff1's recorded precedent: D76's pin must name a commit
# REACHABLE AFTER THE MERGE, which a lane branch's own commit is not. This
# gate is therefore RED on the lane branch BY CONSTRUCTION, with the exact
# message "the emitted scaffolding changed: bump `abi` ... and re-pin
# comparison (B)" -- which is the gate working, not a defect.
#
# [REL-1.4], 2026-09-21 — abi 27 -> 28. THE VERSION STAMP (D115). The
# ESSENTIAL generated-by line — already the one line D112's comment axis
# keeps under every `-fcomments` setting — now also names `PCREC_VERSION`
# (lib/pcrec.h) beside the abi digit: `/* Generated by pcrec 0.1.0-beta
# (abi 28). Pattern: ... */`. No struct offset moves, no `rx_info` member
# is added or changed, and no answer moves at all — the comment TEXT is
# the only thing that changed, on every artifact of both engines
# regardless of `-fcomments`.
#
# [OPTLOOP.1] batch 1, 2026-09-22 — abi 28 -> 29. THE THREE WHOLE-WINDOW
# PRE-CHECKS (D119). Every artifact of both engines gains the
# `<PREFIX>_END_WINDOW` and `<PREFIX>_REQ_BYTE` stamp lines in the SHARED
# PROLOGUE, every VM artifact gains `<PREFIX>_VM_START` beside its own
# stamps, and the three analyses' populations gain the emitted bound, clamp
# and `memchr` those stamps name.
#
# **(A) IS UNTOUCHED, and unlike [REL-1.4]'s entry below that is a claim
# about WHERE the new text goes rather than about how little of it there
# is.** All three stamps are `#define` lines in the prologue, above
# `goto <p>_L0;` and therefore outside `prog_region()`. The two emitted
# PROGRAM additions likewise sit in the SEARCH ENTRY (the clamp and the
# `memchr`, both above the scan/attempt machinery), and
# [OPT-ANCHOR-VM]'s `attempt_max` declaration and rewritten continue test
# sit in `<prefix>_search_run`, which is not the VM PROGRAM region either.
# MEASURED, not argued: comparison (A) reads zero movers on every label.
#
# **(B) IS LEFT AT THE PRE-BUMP VALUE AND IS OWED TO THE MANAGER**, on
# opt5i's, ccdiff1's and [EMIT-VERB]'s recorded precedent one paragraph up:
# D76's pin must name a commit REACHABLE AFTER THE MERGE, which a lane
# branch's own commit is not. This gate is therefore RED on `lane/optimpl1`
# BY CONSTRUCTION, with the exact message "the emitted scaffolding changed:
# bump `abi` ... and re-pin comparison (B)" — the gate working, not a defect.
#
# **(A) IS UNTOUCHED, for the plainest reason any row in this list has
# given.** The generated-by line sits at the very TOP of the file, above
# the shared prologue and above `goto <p>_L0;` — `prog_region()` reads
# neither side of it, unlike [EMIT-VERB]'s per-label `// <role>` lines
# which sat INSIDE the region it reads. So this bump is scaffolding-only
# in the sense (A) cares about, even though (B) still re-pins (D76: any
# emitted byte moving is a bump, whole-file comparison included).
#
# THE PIN IS THIS LANE'S OWN LAST src COMMIT ([ENG-ISL]'s precedent,
# restated above); the manager re-pins to the MERGE when it lands.
#
# [REL-1.4]: LEFT AT THE PRE-BUMP VALUE AND **OWED TO THE MANAGER**, same
# precedent as [EMIT-VERB] immediately above: D76's pin must name a commit
# REACHABLE AFTER THE MERGE, which a lane branch's own commit is not. This
# gate is therefore RED on the lane branch BY CONSTRUCTION, with the exact
# message "the emitted scaffolding changed: bump `abi` ... and re-pin
# comparison (B)" -- which is the gate working, not a defect.
#
# [OPTLOOP.2] batch 2, 2026-09-22 — abi 29 -> 30. THE NECESSARY LITERAL RUN
# AND ITS SCAN PICK (D119). Every artifact of both engines gains the
# `<PREFIX>_REQ_RUN` stamp line in the SHARED PROLOGUE; on the run analysis's
# own population the search entry's three-line `memchr` pre-check becomes a
# ~ten-line scan loop, and on the disjoint byte-only population the decimal
# inside that `memchr` moves where [OPT-FREQPICK] chooses a rarer member of
# the same necessary set.
#
# **(A) IS UNTOUCHED, and for batch 1's own reason rather than a new one.**
# The stamp is a `#define` in the prologue, above `goto <p>_L0;` and therefore
# outside `prog_region()`; the scan loop replaces text that already sat in the
# SEARCH ENTRY, above the scan/attempt machinery, so nothing the region reads
# moves. MEASURED, not argued: comparison (A) reads zero movers on every
# label.
#
# **(B) WAS LEFT AT THE PRE-BUMP VALUE AND OWED TO THE MANAGER**, on the
# recorded precedent of opt5i, ccdiff1, [EMIT-VERB], [REL-1.4] and batch 1
# itself: D76's pin must name a commit REACHABLE AFTER THE MERGE, which a lane
# branch's own commit is not. **RE-PINNED by the manager (lane repin2,
# 2026-09-23) to `8e4e9c6c`, the batch-2 merge commit** — the first commit
# reachable from main that carries abi 30, closing the gate's own RED-BY-
# CONSTRUCTION state on `lane/optimpl2` with the exact message "the emitted
# scaffolding changed: bump `abi` ... and re-pin comparison (B)".
# **(B) RE-PINNED AGAIN — [OPT-PRECHECK-ADMIT], 2026-09-23: `abi` 30 -> 31,
# to `6ef76820`, the admitimpl merge commit.** `admitimpl_report.md` §3 left
# this FILEPIN explicitly OWED to the manager, on the same precedent as
# every prior re-pin: D76's pin must name a commit REACHABLE AFTER THE
# MERGE, which `lane/admitimpl`'s own tip is not. **RE-PINNED (lane repin3,
# 2026-09-23) to `6ef76820`** — the first commit reachable from main that
# carries abi 31 (the `<PREFIX>_REQ_WHY` stamp), closing the gate's own
# RED-BY-CONSTRUCTION state with the exact message "the emitted scaffolding
# changed: bump `abi` ... and re-pin comparison (B)".
# **(B) RE-PINNED AGAIN — [VAR] MVP pattern half, 2026-09-23: abi 31 -> 32,
# to `809aab12`, the varmvp merge commit.** `${name}` in a pattern (module
# `vars`) adds no scaffolding of its own to a var-free artifact, but the
# module's own D76 ritual bumped `PCREC_ARTIFACT_ABI` (`src/gen/emit_dfa.c`,
# via `41e9aa38` on `lane/varmvp`) as every abi event does, closing the
# gate's own RED-BY-CONSTRUCTION state with the exact message "the emitted
# scaffolding changed: bump `abi` ... and re-pin comparison (B)". Re-pinned
# per D76 at merge.
# **(B) RE-PINNED AGAIN — [K64] fix A, 2026-09-25: abi 32 -> 33, to
# `1e6a90b0`, this lane's own tip (`lane/k64fix`).** G2's VM one-attempt
# admission rule (`req_route_one_attempt`, [OPT-PRECHECK-ADMIT]'s own abi
# 30->31 predicate) declined the necessary-byte pre-check wherever the VM
# route tries at most one start position, arguing the attempt reads no more
# than the check would scan — true of a DFA and false of a backtracking VM
# program, where the pre-check is the NO-MATCH PROOF bounding the call: a
# framed, unguarded, `^`-anchored forced-VM one-attempt program gave up on
# its step budget where PCRE2 answers NOMATCH (K64). The predicate now also
# requires the one attempt to be LINEAR — an exact hybrid DFA in front, or a
# frameless VM program that cannot backtrack at all (`Job.vm_frameless`,
# published beside `emit_vm.c`'s own `has_push` derivation). No new stamp,
# no declaration and no layout change: the bump moves a STAMP VALUE
# (`<PREFIX>_REQ_WHY` "one-attempt" -> "emitted") and the search-entry
# PROGRAM TEXT it names, on 176 of 6,634 measured artifact-configs.
#
# **(A) IS UNTOUCHED, for [OPT-PRECHECK-ADMIT]'s own reason one narrowing
# over.** The re-admitted text (the byte check or the run check, plus
# `#include <string.h>`) sits in the SEARCH ENTRY, above the scan/attempt
# machinery, never inside `prog_region()` — the same site batch 1's
# [OPT-REQBYTE] and batch 2's [OPT-REQPOS] pre-checks already occupy, whose
# own admission/decline moves this gate's (A) has already measured
# untouched twice. MEASURED, not argued: comparison (A) reads zero movers
# on every label after this re-pin (see the run below).
# **(B) RE-PINNED AGAIN — [K65] fix (a), 2026-09-25: abi 33 -> 34, to
# `3b3c06f0`, the `lane/k65fix` commit carrying the bump.** On a VM artifact
# with no DFA scan in front (`<PREFIX>_VM_PREFILTER "none"`) an emitted
# pre-check now also `memchr`s every remaining member of the necessary set
# (a 6-line `rq_set[]` block after the byte or run check), so the no-match
# proof no longer rests on the pick (K65). No stamp and no stamp value moves;
# 452 of 6,642 census artifact-configs gain the block, each a pure insertion.
# (A) is untouched for the reason above: the block sits in the SEARCH ENTRY
# beside the check it extends, never inside `prog_region()`.
# **(B) RE-PINNED AGAIN — [K66], 2026-09-25: abi 34 -> 35, to `a446a99e`,
# the `lane/k66fix` commit carrying the bump.** On the same route a necessary
# run longer than its 8-byte window is also compared whole (a 13-line scan
# loop after the window's), and the `rq_set[]` block drops the whole run's
# bytes; 12 of 6,642 census artifact-configs move. (A) is untouched for the
# same reason: the loop sits in the SEARCH ENTRY, never inside
# `prog_region()`.
# **(B) RE-PINNED AGAIN — [OPT-LITSCAN] S1, 2026-09-25: abi 35 -> 36, to
# `6d92764d`, the `lane/s1build` commit carrying the last `src/` change (the
# run-pinned row pair; the bump itself rode `6be904f7`, G1's widening).**
# A pinned necessary run is verified inside the DFA prefilter's offset-skip
# block and a pre-check the selected test dominates is not emitted: 505 of
# 3,583 census corpus artifacts move, by id exactly litscan_s1.md §6's
# classes. (A) is untouched: the prefilter block and the pre-check sit
# outside `prog_region()`. Measured: 16/0 against this pin.
# **(B) RE-PINNED AGAIN — [OPT-LITSCAN] S1 step 6, 2026-09-26: abi 36 -> 37,
# to `c9dec3e4`, the `lane/s1step6` commit carrying the bump (the last `src/`
# change).** The run pre-check's scan loop(s) become calls of file-scope
# `<p>_reqrun`/`<p>_reqrun_whole` blocks written by the offset-skip block's
# emitter: exactly the artifacts that emit a run pre-check move
# (`docs/dev/optloop/s1/s1step6_movers.py`). (A) is untouched: the blocks and
# the calls sit outside `prog_region()`.
# **(B) RE-PINNED AGAIN — [OPT-REQRUN-ENC], 2026-09-26: abi 37 -> 38, to
# `fe5a0bbc`, the `lane/reqrunenc2` commit carrying the bump (the last
# `src/` change).** `rn_scan_index`'s `!bytekey` fallback moves from the
# run's leftmost member to its rightmost (`docs/dev/optloop/
# reqrunenc_census.md`, pcrec-bench's O-60 finding): the emitted
# `memchr`/`memcmp` target byte and `<PREFIX>_REQ_RUN`'s `@offset` VALUE move
# on `-e utf8` artifact-configs only (236 of 1,167 bench, 763 of 10,818
# corpus) — `byte`-encoding artifacts are untouched by construction. (A) is
# untouched: `rn_scan_index` sits in the ANALYSIS (`src/opt/reqbyte.c`; since
# [FINDINGS] B1 `pcrec_find_run_scan_index` in `src/core/findings.c`), not
# `prog_region()`, and this gate's call-free-corpus population is compiled
# at the default (`byte`) encoding.
# **(B) RE-PINNED AGAIN — [K68], 2026-09-26: abi 38 -> 39, to `b255027f`,
# the `lane/k68fix` commit carrying the bump (the last `src/` change).**
# `emit_info_def`'s `strategy_denials` mask (this file) gains the three
# [OPTLOOP.1] batch-1 whole-window pre-check bits
# (`PCREC_NO_VM_ANCHOR_BOUND`/`PCREC_NO_END_WINDOW`/`PCREC_NO_REQ_BYTE`),
# shipped OUTSIDE it since that batch (`docs/dev/known_issues.md` K68).
# `.abi` and the essential provenance-line digit are the ONLY bytes that
# move on `prog_region()`'s own subject population: the mask states a
# REFLECTION-SURFACE property of `rx_info.flags`, which sits ABOVE
# `prog_region()`'s `goto <p>_L0;` start, so (A) is untouched. No answer
# moves on any artifact.
# **(B) RE-PINNED AGAIN — [FINDINGS] B1, 2026-09-27: abi 39 -> 40, to
# `93e80da7`, the `lane/findb1` commit that is its last `src/` change.** Every
# artifact gains the `<PREFIX>_FINDINGS` stamp line beside the `rx_info`
# definition and an APPENDED `rx_info.findings` member and initializer; the
# byte-frequency prior became data that normalizes to the same table, so under
# the `byte` encoding this gate's population is compiled at, nothing else
# moves. Both new lines sit OUTSIDE `prog_region()`, so (A) is untouched.
# **(B) RE-PINNED AGAIN — [OPT-LITSCAN] S2a, 2026-09-27: abi 40 -> 41, to
# `f97c26a6`, the `lane/s2a` commit that is its last `src/` change.** A VM
# literal run is one P4 compare (`tuning.md` §2.31) and every VM artifact gains
# the `<PREFIX>_VM_LIT_RUNS` stamp. THIS ONE MOVES (A) ON PURPOSE, the THIRD
# change in this file's history to do so after the island and the fold, and it
# gets their machinery: the axis's deny `-fno-lit-run` restores the abi-40
# program, so a moved region is excused IFF the deny set (built from the
# stamps, `-fno-lit-run` always in it — see the excuse) restores the pin;
# both converse directions are asserted; `LIT_PATTERNS` is the manifest.
# THE MANAGER RE-PINS TO THE MERGE, the precedent above.
# **(B) RE-PINNED AGAIN — K69, 2026-09-27: abi 41 -> 42, to `bcffbd42`, the
# `lane/k69fix` commit that is its last `src/` change.** A call's nullability
# is the least call-graph fixpoint (`minw != 0`, published by
# src/opt/callgraph.c). This gate's population is CALL-FREE, where the fix
# cannot reach (no call graph is built), so (A) is untouched and (B) moves by
# the abi digit alone. The self-pin convention: the manager re-pins to the merge.
# **(B) RE-PINNED AGAIN — [OPT-LITSCAN] F5, 2026-09-28 (D127): abi 42 -> 43,
# to `51e10961`, the `lane/litf5` commit that is its last `src/` change.**
# `pcrec_lit_run`'s own floor moves from two consecutive one-byte literals
# to three, so a two-byte-only VM literal run falls through to the
# pre-S2a per-byte byte chain instead of S2a's one-compare form. THIS ONE
# MOVES (A) TOO, on whatever population of this gate's CALL-BEARING corpus
# has a two-byte-only lit-run site — the fourth change in this file's
# history to do so (after the island, the fold and S2a itself), excused
# the same way: `-fno-lit-run` still restores the abi-42 program on every
# artifact, so a moved region is excused IFF the deny set restores the pin;
# both converse directions are asserted; `LIT_PATTERNS` is S2a's own
# manifest and unaffected (every S2a mover was three bytes or longer to
# begin with, since the whole population it built from was L >= 2 and this
# lane's movers are the L == 2 subset of it, disjoint from L >= 3).
# **(B) RE-PINNED AGAIN — [K73], 2026-09-29: abi 46 -> 47, to `40c56343`, the
# `lane/k73utf` merge commit that is its last `src/` change (the abi 46 -> 47 bump rode the U2 merge).** The offset-0 start
# rule is emitted only under an encoding that restricts where a match may
# begin, and this gate's population compiles under `byte`, so (A) is
# untouched and (B) moves by the abi digit alone.
# **(B) RE-PINNED AGAIN — [OPT-HYB-RESEED], 2026-09-30: abi 48 -> 49 (land5), pin = the land5 merge commit,
# its last `src/` change (the k73utf convention).** The adaptive retry is emitted only on a VM hybrid whose
# prefilter over-approximates and every hybrid gains a `<PREFIX>_VM_RESEED` line; this gate's population
# is call-free `byte` artifacts, so (A) is untouched and (B) moves by the abi digit alone.
# **(B) RE-PINNED AGAIN — [UTF-VALID], 2026-09-30: abi 49 -> 50 (lane uvbuild), pin = the lane's
# last `src/` commit (self-pin, the k73utf convention).** Every artifact gains `PCREC_ERR_UTF` in the
# ABI block, the `<PREFIX>_UTF_CHECK` stamp, and the `<prefix>_valid_upto` entry with its `.c`-only
# `<prefix>_VALID_LB` macro; this gate's population is call-free `byte` artifacts without the flag, so
# (A) is untouched and (B) moves by exactly those lines and the digit.
# **(B) RE-PINNED AGAIN — [CLS-TREE] S2, 2026-09-30: abi 50 -> 51 (lane/clss2, on top of uvbuild's 50;
# the manager re-pins at merge), pin = `22d150a8`, the lane commit that is its last `src/` change.**
# The kit's byte forms fire at --tune=-2/-1 only and this gate compiles at the default position; its
# population is call-bearing `byte` artifacts, so no wide class is formed and (A) is untouched: (B) moves
# by the abi digit alone.
# **(B) RE-PINNED AGAIN — [CLS-TREE] S2's second event, 2026-09-30: abi 51 -> 52, pin = `979b0b62`.** The
# scan edge's kit body applies at --tune=-2/-1 only; this gate compiles at the default position, so (A)
# is untouched and (B) moves by the abi digit alone.
# **(B) RE-PINNED AGAIN — [CLS-TREE] S2's review fixes (D139), 2026-09-30: abi 52 -> 53, pin = `2c45260a`,
# the lane/clss2 commit that is its last `src/` change.** A DFA scan edge's range test takes the VM's
# spelling at every position and a VM range from 0 reads `b <= hi`; this gate's call-bearing `byte`
# population is VM-routed at the default position, and the gate's own run on the lane decides whether
# (A) moves (docs/dev/lanes/clss2_report.md "Review fixes (clss2fix)").
# **(B) RE-PINNED AGAIN — K79+K80 (lane k7980), 2026-09-30: abi 53 -> 54, pin = `79ebcfd7`, the lane
# commit that is its last `src/` change.** The shared block gains its valued guard and `#error` prelude
# on every artifact; the prefix render changes no byte at `-p rx` (this gate's prefix), so (A) is
# untouched and (B) moves by the prelude lines and the digit.
# **(B) RE-PINNED AGAIN — K78 (lane k78), 2026-09-30: abi 54 -> 55, pin = `6b86a29b`, the lane commit
# that is its last `src/` change.** A DFA artifact with `<PREFIX>_NCAPS >= 2` writes its dead-group fill
# on each success path instead of at the search entry; no VM program region moves, so (A) is untouched,
# and (B) moves by the digit plus that fill's position on the dead-group DFA artifacts.
# Re-pinned at the lane/k7980 merge (2026-10-03) to `1a9d4eed`, the merge commit: it brings a111a150
# (the `--emit-ir` caps cell, output-only, no artifact byte), so it is the combined tree's last `src/`
# change; abi stays 55.
# Re-pinned at [K82] (lane k82fix, 2026-10-04), abi 59 -> 60, to `bdb6d556`, the
# lane's last `src/` commit: the admission's set-leads row and PICK's NONE answer
# move the abi digit everywhere and the movers' pre-check text (k82_movers.log).
# Re-pinned at [K82] (B) (lane k82hbuild, 2026-10-05), abi 60 -> 61, to
# `b55d5554`, the lane's last `src/` commit: the handoff moves the abi digit
# everywhere, adds `<PREFIX>_REQ_HANDOFF` to every artifact and moves the
# movers' gate and start site (docs/dev/optloop/s4/k82hbuild/k82h_movers.log).
# Re-pinned at [START-SET] stage 2 (lane ssbuild2, 2026-10-05), abi 61 -> 62,
# to `82370766`, the lane's last `src/` commit: the VM hat moves the abi digit
# everywhere, adds `<PREFIX>_VM_START_SCAN` to every artifact, and gives the
# movers a start-set table and two seeks in `<prefix>_search_run`.
# [ART-POSS-ARMS] SELF-PIN (lane possbuild, 2026-10-07), abi 65->66: every VM
# artifact gains `RX_VM_POSS_ARMS`, and an arm mover's program moves (its (A)
# excuse is the poss-arms bucket). `615eb811` (the merge of main 8cada7b9) is the lane's last src commit;
# the manager re-pins to the merge (the self-pin convention).
# [NULLABLE-ANCH] SELF-PIN (lane nullanch2, 2026-10-08), abi 67->68: the
# nullability decline reads `empty_admits`, so the five movers (two of them
# call-bearing: `^(a?)(?1)*$`, `^(?:(?<g>a?)){0}(?&g)*+$`) gain the hybrid
# prefilter and read `ENGINE_SEL "selected"`; every other artifact moves by the
# abi digit alone. `9a0cf78e` is the lane's last src commit; the manager
# re-pins to the merge (the self-pin convention).
# [MEMFN] R4e'.0b SELF-PIN (lane r4e0b, 2026-10-09), abi 69 -> 70 (69 is
# decattr's event, landed first): every offset-skip/pre-check function keeps its loop under
# `<fn>__body` and becomes one call to it; every other artifact moves by the
# abi digits alone. `74f941dc` is the lane's src commit; the manager re-pins
# to the merge (the self-pin convention).
# [MEMFN] RQ-3 SELF-PIN (lane rq3, landed by lane rq3land, 2026-10-09), abi
# 70 -> 71: every artifact gains `<PREFIX>_SIMD_GUARDED_BYTES`; no other byte
# moves. `3b7d7b69` (the merge of main 47842ee3, R4e'.0b's 70) is the lane's
# last src commit; the manager re-pins to the merge (the self-pin convention).
# [MEMFN] R-12 VMLAZY SELF-PIN (lane vmlazy, landed by lane vmlmerge,
# 2026-10-09), abi 71 -> 72 (71 is RQ-3's, landed first): the VM cursor
# rung's lazy rmin prefix is spelled as a span scan capped at rmin plus the
# reach test; only lazy-cursor-prefix artifacts move beyond the abi digits.
# [COMPOUND] B4 SELF-PIN (lane cpb4, 2026-10-12), abi 76 -> 77: every artifact
# gains `<PREFIX>_COMPOUND`; the admitted compounds (tests/compound/admitted.tsv)
# move whole. `cd1d2d8f9` was the lane's last src commit.
# D164 B3 SELF-PIN (lane b3build, landed after B4 by lane b3land, 2026-10-13),
# abi 77 -> 78: the match-end mark on rev-end (forms F0-F4, the distance-set
# accept, prio-const); `cb4174451` (the merge with B4) is the lane's last src commit, and the
# manager re-pins to the merge (the self-pin convention).
# [WINDOW-E1] the knowledge-stamp union SELF-PIN (lane rpunion, 2026-10-17),
# abi 78 -> 79: `<PREFIX>_FINDINGS`/`.findings` list a query any attempt (or
# compound part) asked, rendered after `mf_art_end`; beyond the abi digits
# only compiles whose asking attempt was discarded move (F-5). `c10643bbb` is
# the lane's last src commit; the manager re-pins to the merge (the self-pin
# convention).
# [ENTRY-TABLE] E1 SELF-PIN (lane e1, 2026-10-18), abi 79 -> 80: the stamp
# vocabulary gains `<PREFIX>_PART_LAYOUT`/`_PART_LAYOUT_WHY`, written only
# under a part-layout control, so every default artifact moves by the abi
# digits alone. `fc67299b5` is the lane's last src commit; the manager
# re-pins to the merge (the self-pin convention).
# [DD-11.5] P2c SELF-PIN (lane ctxbuild, 2026-10-19), abi 80 -> 81: (?m)^/(?m)$
# are A_CTX rows, so only a DFA machine with a (?m) anchor before another
# context set moves beyond the abi digits (its context list order). `9f7cb74e3`
# is the lane's last src commit; the manager re-pins to the merge (the
# self-pin convention).
# [MEASURE-SET] M0 SELF-PIN (lane m0build, 2026-10-21), abi 81 -> 82: every
# artifact gains the `measures` member of the shared ABI block, its
# `<PREFIX>_MEASURES ""` stamp and `.measures = ""`; the VM's `^` role text
# changes (K112). `9e4b87e90` is the lane's last src commit; the manager
# re-pins to the merge (the self-pin convention).
# [FINDALL-NEXT] I4 SELF-PIN (lane i2build, 2026-10-21), abi 83 -> 84: every
# artifact gains rx_nextnfn, the RX_FOREACH block and rx_info.next_n in the
# shared block, `.next_n =`, <prefix>__one with <prefix>_next/_next_n over it,
# and the STEP's past-the-end line. `881eac3cf` is the lane's last src commit;
# the manager re-pins to the merge (the self-pin convention).
# lane nomacro (2026-10-23): RX_FOREACH dropped (D175) from the unlanded 84 event; the (B) pin moves to the lane's src commit, the manager re-pins to the merge.
# lane iterland (2026-10-22): the stack lands as one 83 -> 84 event; re-pinned to its merge 934f8bed1.
# [EMIT-BIDI] SELF-PIN (lane emitbidi, 2026-10-25), abi 84 -> 86 (85 is the kit S3 branch's): one C-text escaper; artifacts whose pattern holds a tab, newline, CR or byte >= 0x80 move in their comments, every artifact moves in the abi digits. `dba52b4b4` is the lane's last src commit; the manager re-pins to the merge (the self-pin convention).
# [INLINE-C] 1b SELF-PIN (lane ic1b, 2026-10-26), abi 87 -> 89 (provisional): module `callouts` gains its call site; callout-free artifacts move in the abi digits only. `cfdf8f5fd` is the lane's last src commit; the manager re-pins to the merge commit.
# [INLINE-C] 1b SELF-PIN (lane ic1bfix, 2026-10-26), abi 88 -> 89 after main's stage 0 (abi 88) was merged into the lane: `e3c92158c` is the lane's last src commit (review r2's fixes); the manager re-pins to the merge commit.
# [SCANEDGE-SET] SELF-PIN (lane scanset, 2026-10-26), abi 86 -> 87: a scan edge advances on a byte-class set; machines whose run the pattern splits into several classes gain an edge, every artifact moves in the abi digits. `ddd18d3df` is the lane's last src commit; re-pinned by the manager to the merge commit 002810cac.
# [REQRUN-VM] SELF-PIN (lane reqvm1m, 2026-10-29), abi 90 -> 91: the required-run handoff reaches the VM attempt loop and the VM hybrid's prefilter re-entry; artifacts without those sites move in the abi digits only. `88d3c5209` is the merge of main 78627dbca into the lane (its last src commit); the manager re-pins to the landing merge (the self-pin convention).
# [INLINE-C] 2 SELF-PIN (lane ic2, 2026-10-27), abi 89 -> 90: module `code-c` (embedded C); every callout artifact gains the span helpers, callout-free artifacts move in the abi digits only. `94568296a` is the lane's last src commit; the manager re-pins to the merge commit.
# [MEMFN] D172 S3 SELF-PIN (lane s3m, 2026-10-29), abi 91 -> 92 over main b05ccfc0b: the cover LOCATE row routed by default; artifacts it does not take move in the abi digits only. `342723cba` is the lane's last src commit (the renumber over the merge afe9ee325); the manager re-pins to the landing merge (the self-pin convention).
# [K134] SELF-PIN (lane trailgc3, 2026-10-29), abi 91 -> 93 (provisional; the next number at landing): VM artifacts whose program writes the trail on a cycle gain the trail checkpoints, the compaction and the run state's `trail_gc_floor`; every other artifact moves in the abi digits only. `fcd0c4925` is the lane's last src commit (the review r2 fixes); the manager re-pins to the merge commit (the self-pin convention).
# [MEMFN] R-30 SELF-PIN (lane r30b, 2026-10-29; renumbered over main 5c60e118c by lane r30bfix, 2026-10-31), abi 93 -> 94 (provisional; the next number at landing): a pre-check run window implied by its whole run is not asked; artifacts without one move in the abi digits only. The pin `975ed3a9c` is the merge of main 5c60e118c into the lane (the lane's src now; the lane's own src commit was 38d3143d5, over main 1f5574fac at abi 94 before 93 landed); the manager re-pins to the landing merge (the self-pin convention).
# [LANDWALK] stage 1 SELF-PIN (lane p1build 2026-10-29, re-based by lane p1tri 2026-10-30), abi 93 -> 95 (provisional): the landmark-walk LOCATE row; artifacts it does not take move in the abi digits only. `379b84fac` is the lane's last src commit (over `d5c031454`, the merge of main 5796317e9 into lane/p1build; lane p1build self-pinned 8936a8156 over main ae1d53859); the manager re-pins to the landing merge (the self-pin convention).
# [RUN-POS-SET] stage 1 SELF-PIN (lane altbuild, 2026-11-06), abi 95 -> 96 (provisional; the next number at landing): the UTF-8 lowering merges a wide class's boxes through the alternation owner and the VM island reads a wide class's set; utf8 artifacts whose classes merge move in their tables/program, every other artifact moves in the abi digits only. `e3df76804` is the lane's last src commit (re-pinned per later stage); the manager re-pins to the landing merge (the self-pin convention).
# [RUN-POS-SET] stages 2p/2b + K139 + review r5 altcode fixes SELF-PIN (lane altfix, 2026-11-06), still abi 96 (provisional): rule M's sibling merge and P/S factoring in the owner (byte artifacts too), the drop-islands rung, and the island reading a class as its member words with the size row counting the chain before M's folds move VM programs and the island census. `ce68bcf5d` is the lane's last src commit; the landing re-pins FILEPIN AND ABASEPIN to the landing merge (review r5 TRD-7).
# [RUN-POS-SET] catch-up SELF-PIN (lane altcatch, 2026-11-07), abi 96 -> 97: the alternation branch merged main c44649a69 ([VLOOKBEHIND] stage 1, abi 96) and renumbered; `c9dca3c84` is that merge (the branch's last src change, carrying both sides); the landing re-pins both pins to its merge on main.
# [XARCH-DEV] U2+U3 SELF-PIN (lane u3tgt, 2026-11-08), abi 97 -> 98: the art's CPU target stated to the kit; every artifact gains `<PREFIX>_TARGETS`, a SIMD target's artifact the kit's guard and region (its levels #if-free). `c6d73f302` is the lane's last src-moving commit (the merge of lane/memfn-u2's tip, which moves memfn/src; the lane's own src commits are a6f88a689 and before); the manager re-pins to the landing merge.
# [XARCH-DEV] U2+U3 SELF-PIN moved (lane u3fix, 2026-11-08), abi 98 unchanged: the kit's finished U2 (7fb1fa153) merged and its switch MF_TARGET_REQUIRED set to 1; 1,500 sampled corpus patterns x 6 cells emit byte-identically to 59846b211, so (B) moves only to name the tip that carries every code change. The manager re-pins to the landing merge.
# [PFFIX] SELF-PIN (lane pffix, 2026-11-11), abi 99 -> 100: an accept-free DFA machine is the empty engine on both routes; never-matching patterns' search bodies (the hybrid prefilter of ab\Gcd) become one return 0, every other artifact moves in the abi digits only. `f1304934d` is the lane's last src commit; the manager re-pins to the landing merge (the self-pin convention).
# [NEVER-MATCH] SELF-PIN (lane nevermatch, 2026-11-12), abi 100 -> 102: under --engine=auto a VM hybrid whose prefilter machines admit no match is the DFA empty artifact (16 corpus patterns, none call-bearing); every other artifact moves in the abi digits only. `a60681ae2` is the lane's last src commit; the manager re-pins to the landing merge (101 is the kit's K38-2: re-pin the number too if it lands first).
# [REQ-PAST-LAST] SELF-PIN (lane reqpast, re-pinned by lane rpfix 2026-11-12, PORTED onto K38-2 by lane rpport 2026-11-13), abi 104 -> 105: the attempt-loop row `handoff-attempts-unbounded`; VM artifacts with no DFA scan whose required whole run has no finite maximum offset gain the handoff (stamp "unbounded", the keep, the re-ask), every other artifact moves in the abi digits only. `@SELFPIN@` is the lane's last src commit; the manager re-pins to the landing merge (the self-pin convention). (A) moves with it: call-free artifacts that take the row move. The rpfix self-pin 7ddf68c71 (abi 105 over 103) never landed.
FILEPIN="${RECURSION_IDENTITY_FILEPIN:-@SELFPIN@}"   # [REQ-PAST-LAST] SELF-PIN (lane rpport, 2026-11-13): @SELFPIN@, abi 105 (see the line above); before it 7c16349d7: [MEMFN] R-38 K38-2 landing re-pin (lane k382land, 2026-11-12), abi 104: 7c16349d7, the merge of lane/memfn-k382 into main, re-pinned from the lane self-pin ff1885b16; before it [MEMFN] R-38 K38-2 re-bump SELF-PIN (lane k382n, 2026-11-12), abi 103 -> 104: ff1885b16 is the merge of main 51481d1b3 into lane/memfn-k382, the lane's last src commit (K38-2 lands over [S1] 103); the manager re-pins to the landing merge; before it 5880ecb2c, the k382m re-bump self-pin (abi 100 -> 101 over main e889ba64c, never landed); before it bda562f50, the K38-2 self-pin (lane k382, abi 99 -> 100 over main d81ebd294, never landed); before it 06699f615: [S1] landing re-pin (s1land, 2026-11-12): 06699f615, the merge of lane/minw onto lane/nevermatch onto main 3b52b096d, abi 103; before it a60681ae2: [NEVER-MATCH] self-pin (lane nevermatch, abi 102, see the line above); before it e41ac3534: [PFFIX] landing re-pin (manager, 2026-11-11): e41ac3534, the merge of lane/pffix into main, abi 100 (pffix2 changed tests only; recid job 311 GREEN at the self-pin); before it f1304934d: [PFFIX] self-pin (lane pffix, abi 100, see the line above); before it 7ed856dde: [FEAT-FAMILIES] landing re-pin (lane famland, 2026-11-11): 7ed856dde, the merge of lane/famfix onto main ae1ded8e8 (U3 + cloudmon), abi 99 (main was 98, U3 did not bump); before it 7767af9206, [FEAT-FAMILIES] SELF-PIN (lane famfix, 2026-11-11), abi 98 -> 99 (famdef2 2a36eb5ce: module match-start-reset joins PCREC_FEATURE_MODULES, every artifact gains 18 bytes): 7767af9206 is the merge of lane/famdef3 onto main f7eb10528+; the manager re-pins to the landing merge; before it f7eb10528: span-arms R1 landing re-pin (lane ridtri, 2026-11-11): f7eb10528, the merge of lane/sar1mrg into main, abi 98 (no bump), (B) moved because sar1fix 001c0faf5 derives req_whole_run, so call-free artifacts gain a longer RX_REQ_RUN define (the program region did not move); before it cf578177ed, U2+U3 landing (lane landu3, 2026-11-09): cf578177ed, the merge of lane/u3mech edf78bcbf into main, abi 98, MF_SITE_ABI 26, review r5, re-pinned from the lane self-pin; before it 2567ce447, u3fix self-pin (above): 2567ce447, the merge of main 550e23364 over the merge of lane/memfn-u2 7fb1fa153 (ccaef16a2) and MF_TARGET_REQUIRED 1 (fe34fe1c3), abi 98; before it c6d73f302, u3tgt self-pin; before it f77ed1130   # [ALT-NF] landing (lane altland, 2026-11-07): f77ed1130, the merge of lane/altbuild into main, abi 97, re-pinned from the lane self-pin c9dca3c84; before it c9dca3c84, lane altcatch catch-up self-pin (above); before it c44649a69, [VLOOKBEHIND] stage 1 landing (lane vlbland, 2026-11-07): c44649a69, the merge of lane/vlbbuild into main, abi 96, re-pinned from the lane self-pin 97eadaca4; before it 97eadaca4, [VLOOKBEHIND] stage 1 SELF-PIN (lane vlbbuild, 2026-11-06), abi 95 -> 96: 97eadaca4 is the lane's last src commit; 22 distinct call-free corpus patterns (plus the lane's witness cells) flip from refused to compiled, which (B) hard-fails as refusal mismatches against an older pin, so the pin moves on purpose (vlookbehind.md §6 gate 2); run 1 (a 3b9754edf subject, abi 95, against f5de088bf/4bd002e20) is the identity evidence (vlbbuild_report.md); the manager re-pins to the merge; before it f5de088bf, [LANDWALK] stage 1 landing (lane p1land, 2026-11-02): f5de088bf, the merge of main 0da7ab3bb into lane/p1build (the landing merge; main takes the branch), abi 95, the landmark-walk LOCATE row (D184), re-pinned from the lane self-pin 379b84fac; (B) 0 differing at 379b84fac (job 709), and the later src commits e766f6b15 (p1kind) and d6e03a594 (p1mech) byte-identical (job 762, 0 differing vs 8aedc62ee); before it cd4c36b92, [MEMFN] R-30 landing (lane landr30, 2026-11-01): cd4c36b92, the lane/memfn-r30b merge commit, abi 94, re-pinned from the lane self-pin 975ed3a9c; before it 975ed3a9c, the merge of main 5c60e118c into lane/memfn-r30b, R-30 at abi 94 (provisional); before it ebcc10aa1, lane/trailgc merge commit (lane landtgc landing, 2026-10-29): abi 93, K134 trail compaction, re-pinned from self-pin fcd0c4925; before it 0f425c2d0, lane/memfn-s3m merge commit (lane lands3 landing, 2026-10-29): abi 92, re-pinned from the lane self-pin 342723cba; before it 342723cba, lane s3m self-pin (2026-10-29), D172 S3 at abi 92 over main b05ccfc0b; before it 02229045e, [REQRUN-VM] merge commit (lane reqvm1land landing, 2026-10-29): abi 91, re-pinned from the lane self-pin 88d3c5209; before it 88d3c5209, the [REQRUN-VM] self-pin (lane reqvm1m, 2026-10-29): abi 91; before it c6707bb5a, [INLINE-C] stage 2 merge commit (lane ic2fix landing, 2026-10-28): abi 90, re-pinned from the lane self-pin 94568296a; before it [INLINE-C] stage 2 lane self-pin (lane ic2, 2026-10-27): abi 90; the manager re-pins to the merge commit; before it 719a17ccb, the [INLINE-C] stage 1b merge commit (2026-10-27): abi 89, re-pinned from the lane self-pin e3c92158c (ic1bfix); before it cfdf8f5fd, the lane ic1b self-pin (abi 89 provisional, pre-merge); before it 81454bbf4, the [INLINE-C] stage 0 merge commit (2026-10-26): abi 88, re-pinned from the lane self-pin c1dd695bc; before it 002810cac, the [SCANEDGE-SET] merge commit (2026-10-26): abi 87, re-pinned from the lane self-pin ddd18d3df; before it 7234c2e86, the [EMIT-BIDI] merge commit (2026-10-26, landing lane emitbidiland): abi 86, re-pinned from the lane self-pin dba52b4b4; before it 4f39644d8 (lane iterfix2 (2026-10-23): the r2 review's fixes, the 84 event amended, src identical to this commit (was 24d2888f5, lane nomacro, RX_FOREACH dropped; before it 934f8bed1, the lane/iterland stack pre-nomacro; before it 881eac3cf, the I4 lane self-pin; before it 8d5536143, the I1 lane self-pin, abi 83; before it 813f43ec8, the [MEASURE-SET] M0 merge, abi 82)
# [RECID-A] (2026-10-29, manager ruling: RE-BASE, not a ninth exception) THE (A) BASE.
# Comparison (A) used to defend "no unruled change to a call-free region" against
# the never-moving pre-module pin ac4917d, absorbing every later ruled emission
# change as a named canonicalizing exception (eight of them) and going silently
# red a third time. It now compares against ABASEPIN: a ruled MAIN commit, post-
# module, that already carries every one of those changes (the eight exceptions,
# K128's guard/label renumbering, the nine (?U)-possessive movers). The claim is
# the same shape as (B)'s and moves the same way: a change that moves a call-free
# region on purpose re-pins ABASEPIN in its own commit. 4bd002e20 is the commit
# the 2026-11-04 full suite froze (every stage dispositioned); it re-bases the
# first pin 7234c2e86 (the [EMIT-BIDI] merge, abi 86) after later ruled landings
# moved call-free regions (docs/dev/lanes/recida_report.md "Re-base 2").
# lane altfix (2026-11-06, the 303 triage): the branch moves call-free regions
# on purpose (stage 2b, K139, the island fixes; ruled by the alt_normal_form
# design and review r5 altcode), so (A) is SELF-PINNED to the lane's last src
# commit `ce68bcf5d` in the same change, as the rule above asks; the landing
# re-pins it to the landing merge on main (a ruled main commit again).
ABASEPIN="${RECURSION_IDENTITY_ABASE:-@SELFPIN@}"   # [REQ-PAST-LAST] SELF-PIN (lane rpport, 2026-11-13): @SELFPIN@, abi 105 (with FILEPIN above; the rpfix self-pin 7ddf68c71 never landed); before it 06699f615: [S1] landing re-pin (s1land, 2026-11-12): the merge 06699f615, abi 103 (with FILEPIN above); before it a60681ae2: [NEVER-MATCH] self-pin (lane nevermatch, abi 102, with FILEPIN above); before it e41ac3534: [PFFIX] landing re-pin (manager, 2026-11-11): the merge e41ac3534, abi 100 (with FILEPIN above); before it f1304934d: [PFFIX] self-pin (lane pffix, abi 100, with FILEPIN above); before it 7ed856dde: [FEAT-FAMILIES] landing re-pin (lane famland, 2026-11-11): the merge 7ed856dde, abi 99 (with FILEPIN above); before it 7767af9206: [FEAT-FAMILIES] self-pin (lane famfix, abi 99, with FILEPIN above); before it f7eb10528: span-arms R1 landing re-pin (lane ridtri, with FILEPIN above); before it cf578177ed: U2+U3 landing re-pin (lane landu3, 2026-11-09): the merge cf578177ed, abi 98 (with FILEPIN above); before it f77ed1130: [ALT-NF] landing re-pin (lane altland): the merge f77ed1130, abi 97; before it c9dca3c84: lane altcatch catch-up self-pin (with FILEPIN above): the merge of main into lane/altbuild, so (A) carries both the branch's ruled call-free moves and lookbehind's; before it c44649a69, [VLOOKBEHIND] stage 1 landing merge (lane vlbland, 2026-11-07), with FILEPIN above; before it 97eadaca4, [VLOOKBEHIND] stage 1 self-pin (lane vlbbuild, 2026-11-06), with FILEPIN above; before it 4bd002e20
# [MEMFN] D172 S3 SELF-PIN (lane s3pair, 2026-10-24), abi 84 -> 85: the cover
# LOCATE row routed by default (the kit's window family); every other artifact
# moves only the abi digits. `450dca216` is the lane's last src commit; the
# manager re-pins to the merge (the self-pin convention).
# lane s3fix (2026-10-24): the S3 final review's fixes move bytes inside 85
# (the two-stream look-ahead, E-find's hoisted raise, D-hors's bound); the (B)
# pin moves to the lane's last src commit `d0d81e4e8`; the manager re-pins to the merge.

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
# [MEMFN] R4a: a pin at or after R4a links the kit (memfn/), so the archive
# carries it whenever the pinned commit has it; FILEPIN moves forward at every
# abi event, and the first move past R4a would otherwise fail to link.
FILEPIN_DIRS="src lib cli"
git -C "$ROOT_DIR" cat-file -e "$FILEPIN:memfn" 2>/dev/null && FILEPIN_DIRS="$FILEPIN_DIRS memfn"
# shared/ (the SHA-256 leaf) the same way: a pin past its arrival includes it.
git -C "$ROOT_DIR" cat-file -e "$FILEPIN:shared" 2>/dev/null && FILEPIN_DIRS="$FILEPIN_DIRS shared"
# shellcheck disable=SC2086
if ! git -C "$ROOT_DIR" archive "$FILEPIN" $FILEPIN_DIRS \
        | tar -x -C "$FILEREFSRC" 2>"$WORKDIR/filearch.log"; then
    bad "could not git-archive $FILEPIN: $(head -3 "$WORKDIR/filearch.log")"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
FILEREF="$WORKDIR/pcrec_filepin"
FILEREF_SRCS="$(pcrec_lib_srcs "$FILEREFSRC")"
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
# [OPTLOOP.1.impl] batch 1 (2026-09-22): the (B) pin is POST-D118 for the first
# time, so the reference compiler may speak the gcc-shaped grammar (`--pattern`)
# rather than the retired `-- PATTERN`. Probe its OWN --help once, the way
# scripts/emit_sweep.py does (pcrec_speaks_pattern_flag) — never assume one
# grammar for both sides; (A)'s pre-module reference $REF keeps `--`.
if "$FILEREF" --help 2>&1 | grep -qE -- '--pattern([^-]|$)'; then FILEREF_PAT='--pattern'; else FILEREF_PAT='--'; fi
ABI_SUBJ_ART="$(pcrec_run "$PCREC"   --features all -p rx -o - --pattern 'a' 2>/dev/null)"   # [K37] bounded
ABI_PIN_ART="$(pcrec_run "$FILEREF" --features all -p rx -o - $FILEREF_PAT 'a' 2>/dev/null)"   # [K37] bounded
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

# ---- the (A) BASE compiler, from the re-based pin -------------------------
# [RECID-A] Built exactly like the file-pin compiler above. It must be POST-module
# (the opposite of $REF): a base that predates the producers would refuse the
# call-bearing half and compare far too small a population, so the module file's
# PRESENCE is asserted, and so is that the base compiles a call-bearing pattern.
ABASESRC="$WORKDIR/abase"
mkdir -p "$ABASESRC"
if ! git -C "$ROOT_DIR" rev-parse --verify --quiet "$ABASEPIN^{commit}" >/dev/null; then
    bad "the (A) base $ABASEPIN does not resolve in this repository — the (A) reference cannot be built, and a gate that cannot build its reference must SAY so rather than skip"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
ABASE_DIRS="src lib cli"
git -C "$ROOT_DIR" cat-file -e "$ABASEPIN:memfn" 2>/dev/null && ABASE_DIRS="$ABASE_DIRS memfn"
# shared/ (the SHA-256 leaf): a base past its arrival needs it (src/parse/rxt_source.c includes it).
git -C "$ROOT_DIR" cat-file -e "$ABASEPIN:shared" 2>/dev/null && ABASE_DIRS="$ABASE_DIRS shared"
# shellcheck disable=SC2086
if ! git -C "$ROOT_DIR" archive "$ABASEPIN" $ABASE_DIRS \
        | tar -x -C "$ABASESRC" 2>"$WORKDIR/abasearch.log"; then
    bad "could not git-archive $ABASEPIN: $(head -3 "$WORKDIR/abasearch.log")"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
if [ ! -f "$ABASESRC/src/parse/mod_recursion.c" ]; then
    bad "the (A) base $ABASEPIN carries no src/parse/mod_recursion.c — it predates module recursion, so (A) would compare against a compiler that refuses the call-bearing half"
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
ABASE="$WORKDIR/pcrec_abase"
ABASE_SRCS="$(pcrec_lib_srcs "$ABASESRC")"
# shellcheck disable=SC2086
if ! $CC -O0 -std=gnu11 -Wall -Wextra -I"$ABASESRC/lib" -I"$ABASESRC/src" $SANFLAGS \
        -o "$ABASE" "$ABASESRC"/cli/main.c $ABASE_SRCS 2>"$WORKDIR/abasebuild.log"; then
    bad "could not build the (A) base compiler from $ABASEPIN: $(grep -m3 -E 'error|undefined' "$WORKDIR/abasebuild.log" | tr '\n' ' ' | cut -c1-300)"
    head -20 "$WORKDIR/abasebuild.log" >&2
    echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi
if ! "$ABASE" --features all -p rx -o - --pattern '(a)(?1)' >/dev/null 2>&1; then
    bad "the (A) base $ABASEPIN REFUSES the call-bearing pattern '(a)(?1)': it is not a post-module compiler"
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
# ===========================================================================
# [D112] `-fcomments` IS PASSED EXPLICITLY, AND THE COMMENTS ARE THE
# INSTRUMENT RATHER THAN DECORATION (evtriage2's class 2).
# ===========================================================================
# [EMIT-VERB] event 2 (abi 26 -> 27) made emitted comments OFF BY DEFAULT.
# This gate reads them TWICE, and neither reading is cosmetic:
#
#   1. THE D37 STAMP FILTER's three lines are `/* Feature set: ... */` and the
#      two `#define PCREC_FEATURE_*` lines. Under the new default the comment
#      is not emitted, so `stamp_count` reads 2 and EVERY artifact lands in
#      `stampbad` -- which `continue`s before either comparison runs, so the
#      whole sweep goes vacuous while reporting a filter fault. The "exactly
#      three" assertion is CORRECT and stays; what it needs is the axis that
#      makes three lines exist.
#   2. COMPARISON (A) IS DELIBERATELY COMMENT-SENSITIVE INSIDE THE PROGRAM
#      REGION -- see the (A) block above: "NO filtering beyond the three D37
#      stamp lines, so comment sensitivity INSIDE the region is kept in full --
#      the property that caught [M6.6.2] wave E's 37-byte prose change on 54
#      artifacts". The `vm_rolef` role text IS that property. A default-axis
#      subject has no role text at all, so its region differs from the
#      pre-module reference's on EVERY VM artifact, for a reason that is the
#      axis and not the module. MEASURED (lane evtriage3, 2026-09-19): five
#      call-free VM patterns read MOVED at the default axis and four of the
#      five read SAME under `-fcomments` (the fifth, `(?:ab|cd)*x`, moves for
#      the [ENG-ISL] reason the deny-build excuse below already handles).
#
# SO THE SUBJECT-SIDE COMPILERS ASK FOR COMMENTS AND THE PRE-MODULE ONE DOES
# NOT: `ac4917d` predates the axis and REFUSES `-fcomments` ("unknown
# option"), and it emits the comments unconditionally, which is exactly the
# side of the comparison that needs no flag. `$FILEREF` is the abi-27 merge
# and takes the flag, so comparison (B) keeps its whole-file comment
# sensitivity too rather than quietly losing it at the default flip.
# shellcheck disable=SC2086
gen_a() { pcrec_run "$PCREC" --features all -p rx -fcomments $2 -o - --pattern "$1" 2>/dev/null; }
# shellcheck disable=SC2086
gen_b() { "$REF"   --features all -p rx $2 -o - -- "$1" 2>/dev/null; }
# shellcheck disable=SC2086
gen_c() { "$FILEREF" --features all -p rx -fcomments $2 -o - $FILEREF_PAT "$1" 2>/dev/null; }
# [RECID-A] the (A) base build: post-module, so it speaks -fcomments and --pattern like gen_c.
# shellcheck disable=SC2086
gen_d() { "$ABASE" --features all -p rx -fcomments $2 -o - --pattern "$1" 2>/dev/null; }
# [ENG-ISL] THE FOURTH BUILD, and the one that turns the island's excuse from a
# per-artifact exemption into a CLAIM (panel r53, F3): the SUBJECT compiler with
# the new axis DENIED. It is the only reference that ISOLATES the island — the
# August pin differs from today for a dozen landed reasons, so "this artifact's
# region moved and it stamps an island" would otherwise excuse every one of
# them at once, and an unrelated emitter regression inside an island-bearing
# artifact would read green. Denying the axis and getting the PINNED bytes back
# is what says the movement is the island's and nothing else's.
# shellcheck disable=SC2086
gen_noisl() { pcrec_run "$PCREC" --features all -p rx -fcomments $2 -fno-alt-island -o - --pattern "$1" 2>/dev/null; }
# [FORM-CHAR] THE FIFTH AND SIXTH BUILDS, the fold axis's own copies of the
# island's shape one paragraph up: the SUBJECT compiler with the ascii-fold
# class test denied, and with BOTH region-moving deny axes denied for the
# artifact that stamps both an island and a fold (each excuse build denies
# exactly the axes whose stamps read > 0, because denying an axis that did
# not fire is asserted a byte-level no-op by the converse arms below, and
# the restore claim is sharpest when the deny set names what fired).
# shellcheck disable=SC2086
gen_nofold() { pcrec_run "$PCREC" --features all -p rx -fcomments $2 -fno-cls-fold -o - --pattern "$1" 2>/dev/null; }
# shellcheck disable=SC2086
gen_denyboth() { pcrec_run "$PCREC" --features all -p rx -fcomments $2 -fno-alt-island -fno-cls-fold -o - --pattern "$1" 2>/dev/null; }
# [OPT-LITSCAN] S2a THE THIRD REGION-MOVING AXIS, -fno-lit-run, and the
# general form the two above are special cases of: the subject compiler with
# EXACTLY the deny flags in $3 (the stamped axes, see the excuse below).
# shellcheck disable=SC2086
gen_nolit() { pcrec_run "$PCREC" --features all -p rx -fcomments $2 -fno-lit-run -o - --pattern "$1" 2>/dev/null; }
# shellcheck disable=SC2086
gen_deny() { pcrec_run "$PCREC" --features all -p rx -fcomments $2 $3 -o - --pattern "$1" 2>/dev/null; }

# [DD-14.FB] THE PROGRAM REGION: `goto <p>_L0;` through the accept label. An
# artifact with no VM program (a DFA-selected pattern) yields the EMPTY region,
# and empty-vs-empty compares equal — which is correct and is why the
# dead-capture elision's four patterns still show up as differing here: on the
# pre-module reference they were VM-selected and HAVE a region, and today they
# are DFA-selected and do not.
# The FIRST region only: a VM artifact whose iterator retries an empty match
# carries the matcher's guarded copy `<p>__match_notempty` after it, a second
# `goto rx_L0;` .. `rx_accept:` (iterfix2, review 2026-10-23-r2 EMIT-1).
prog_region_raw() { awk '/^    goto rx_L0;$/{on=1} on{print} on&&/^rx_accept:/{exit}'; }
# [RECID-A] (2026-10-29) EVERY region this file extracts, from the subject, the (A) base and
# every deny-axis build alike, is the RAW region: the base carries every ruled
# emission change, so there is no canonicalizer between the two sides.
prog_region() { prog_region_raw; }

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
            # An escaped "(" is masked too: kept as "\\(", its "(?" in "\\(?"
            # (an optional literal paren) reads as a group doorway, and that
            # call-bucket misfile was the one pattern the positive control
            # found the pre-module reference ACCEPTING (tests/compound/split.rxt).
            out.append("XX" if in_class else c + ("X" if pat[i+1] == "(" else pat[i+1])); i += 2; continue
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
    (r"a\(?b",           False, "an ESCAPED paren before `?` is a literal optional paren, not a group doorway (the SQL-keyword pattern in tests/compound/split.rxt, the one pattern the positive control saw the reference ACCEPT)"),
    (r"a\\(?:b)",        False, "an escaped BACKSLASH before a real `(?:` leaves the group open a doorway, and a non-call one"),
    (r"a\\(?1)",         True,  "an escaped backslash before a real call: the escape pair consumed, the call still found"),
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
# [VAR] `errors="surrogateescape"` ON BOTH READ AND WRITE: module `vars`'
# corpus deliberately carries a raw non-UTF-8 byte in a pattern line
# (`^${v:-\xff}$`, the default-value operand's own byte-literal cell), which
# plain `open(src)` cannot read at all -- `UnicodeDecodeError` on that one
# line kills the whole script before it classifies a single pattern. This is
# a defect in the SCRIPT's reading, not in pcrec: the classifier below only
# asks whether a `(?` tail or a `\g` spelling is present in the pattern
# TEXT, never decodes it as a string, so round-tripping the byte through a
# surrogate escape (verified: writes back out as the SAME byte, not a
# re-encoding of it) costs nothing and fixes every future raw-byte pattern
# this class of script meets, not just this one -- vartriage's fix to the
# three [M6.2] identity scripts, same shape, one gate over.
for line in open(src, encoding="utf-8", errors="surrogateescape"):
    p = line.rstrip("\n")
    if not p:
        continue
    (call if is_call(p) else free).append(p)
open(cout, "w", encoding="utf-8", errors="surrogateescape").write("\n".join(call) + ("\n" if call else ""))
open(fout, "w", encoding="utf-8", errors="surrogateescape").write("\n".join(free) + ("\n" if free else ""))
PY

nc=$(grep -c . "$WORKDIR/call" || true)
nf=$(grep -c . "$WORKDIR/free" || true)
echo "recursion-identity: corpus $(grep -c . "$PATFILE") patterns; call-bearing: $nc; call-free: $nf"

# [RECID-A] THE ONE TEXT CENSUS THAT SURVIVES the exception buckets (the
# bref-rename, var-construct, ctx-node and lazy censuses went with them): the
# source-possessive/atomic population, derived from PATTERN TEXT and not from
# the artifact (learnings.md §3: a control sharing a source with what it
# controls proves nothing). The possessify arms' stamped-direction converse in
# sweep() may excuse an unchanged region ONLY for a pattern in it.
python3 - "$WORKDIR/free" "$WORKDIR/possrc_pop" <<'PY'
import sys, re

def mask_classes(pat):
    out = []; i = 0; n = len(pat); in_class = False
    while i < n:
        c = pat[i]
        if c == "\\" and i + 1 < n:
            # An escaped "(" is masked too: kept as "\\(", its "(?" in "\\(?"
            # (an optional literal paren) reads as a group doorway, and that
            # call-bucket misfile was the one pattern the positive control
            # found the pre-module reference ACCEPTING (tests/compound/split.rxt).
            out.append("XX" if in_class else c + ("X" if pat[i+1] == "(" else pat[i+1])); i += 2; continue
        if not in_class and c == "[":
            in_class = True; out.append(c); i += 1; continue
        if in_class and c == "]":
            in_class = False; out.append(c); i += 1; continue
        out.append("X" if in_class else c); i += 1
    return "".join(out)

# [recidtri] the SOURCE-POSSESSIVE / ATOMIC census: a pattern that SAYS a
# possessive quantifier (`x++`, `x*+`, `x?+`, `x{n,m}+`) or an atomic group
# (`(?>`, `(*atomic:`). Read on the masked text with every escape pair
# collapsed to one letter first, so `\++` (a greedy plus on a literal plus)
# is not a possessive. [ART-POSS-ARMS]'s stamp counts a verdict on such a
# loop, whose only consumer is the free discharge, so the stamped-direction
# converse may excuse an unchanged region ONLY for these patterns.
POSSRC_RE = re.compile(r"[+*?}]\+|\(\?>|\(\*atomic:")
src, possrcout = sys.argv[1], sys.argv[2]
possrchits = []
for line in open(src, encoding="utf-8", errors="surrogateescape"):
    p = line.rstrip("\n")
    if not p:
        continue
    m = mask_classes(p)
    if POSSRC_RE.search(re.sub(r"\\.", "E", m)):
        possrchits.append(p)
open(possrcout, "w", encoding="utf-8", errors="surrogateescape").write(
    "\n".join(possrchits) + ("\n" if possrchits else ""))
print("recursion-identity: source-possessive/atomic population in the call-free bucket "
      "(text census, independent of the artifact): %d" % len(possrchits))
PY
POSSRC_POP="$(cat "$WORKDIR/possrc_pop")"
NPOSSSRC=$(grep -c . "$WORKDIR/possrc_pop" || true)

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
    # [DD-14.FB] the SECOND tally: the program region against the (A) BASE
    # ($ABASEPIN, see the header's [RECID-A] block). Kept in its own variables
    # and printed on its own line so the two claims never blur into one number.
    local rsame=0 rdiff=0 rcallbearing=0 rbaserefused=0
    # The stamp-truth converses' counters (island, fold, literal run, atom
    # table, possessify arms): each compares an artifact with its OWN deny
    # build, never with a pin, so none of them depends on (A)'s base.
    local rislsame=0 rnoislmoved=0
    local rfoldsame=0 rnofoldmoved=0
    local rlitsame=0 rnolitmoved=0
    local rpacksame=0
    local rposssame=0 rnopossmoved=0 rpossverdict=0
    : > "$WORKDIR/diff.$label"
    while IFS= read -r pat; do
        [ -n "$pat" ] || continue
        local a b na nb sa sb
        local r ra rb
        a="$(gen_a "$pat" "$args")"
        # `b` is the FILE-PIN build (comparison (B)); `r` is the (A) BASE build,
        # used for the program-region comparison (A). Both speak -fcomments.
        b="$(gen_c "$pat" "$args")"
        r="$(gen_d "$pat" "$args")"
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
        # ---- (A) THE PROGRAM REGION, against the (A) BASE ------------------
        # No filtering beyond the three D37 stamp lines, so a comment change
        # inside the region is still a difference. The base is a post-module
        # commit with every ruled emission change since August already in it
        # ([RECID-A]), so a difference here is a change nobody has re-pinned:
        # there is no exception list to absorb it.
        if [ -n "$r" ]; then
            ra="$(printf '%s\n' "$a" | stamp_strip | prog_region)"
            rb="$(printf '%s\n' "$r" | stamp_strip | prog_region)"
            case "$a" in *RX_VM_CALL_*) rcallbearing=$((rcallbearing + 1)) ;; esac
            # The artifact's OWN account of what it contains, read from the
            # subject side only, for the converses below. Empty on a DFA
            # artifact (the stamps are VM-route-only), which the arithmetic
            # treats as 0.
            isl_a="$(printf '%s\n' "$a" | sed -n 's/^#define RX_VM_ALT_ISLANDS \([0-9]*\)$/\1/p' | head -1)"
            fold_a="$(printf '%s\n' "$a" | sed -n 's/^#define RX_VM_CLS_FOLDS \([0-9]*\)$/\1/p' | head -1)"
            lit_a="$(printf '%s\n' "$a" | sed -n 's/^#define RX_VM_LIT_RUNS \([0-9]*\)$/\1/p' | head -1)"
            pack_a="$(printf '%s\n' "$a" | sed -n 's/^#define RX_VM_CLS_ATOMS \([0-9]*\)$/\1/p' | head -1)"
            # [ART-POSS-ARMS] the arms' stamp is a HEX mask; read as a number.
            poss_a="$(printf '%s\n' "$a" | sed -n 's/^#define RX_VM_POSS_ARMS 0x\([0-9a-f]*\)u$/\1/p' | head -1)"
            [ -n "$poss_a" ] && poss_a=$((16#$poss_a))
            if [ "$ra" = "$rb" ]; then
                rsame=$((rsame + 1))
            else
                rdiff=$((rdiff + 1))
                printf 'REGION DIFFERS %s\n' "$pat" >> "$WORKDIR/diff.$label"
            fi
            # THE CONVERSE, AND IT IS SELF-CONTAINED AGAINST THE DENY AXIS
            # RATHER THAN AGAINST THE AUGUST PIN (panel r53, F5). Comparing a
            # stamped artifact to the pre-island reference goes VACUOUS as the
            # emitter moves — any other landed change makes the two differ and
            # the converse passes for the wrong reason. The claim that does not
            # decay: an artifact that STAMPS an island must differ from ITS OWN
            # `-fno-alt-island` build, and one that does not must be byte-
            # identical to it. Both directions are about THIS compiler.
            if [ "${isl_a:-0}" -gt 0 ]; then
                rn2="$(printf '%s\n' "$(gen_noisl "$pat" "$args")" | stamp_strip | prog_region)"
                if [ "$ra" = "$rn2" ]; then
                    rislsame=$((rislsame + 1))
                    printf 'ISLAND STAMPED BUT DENYING IT CHANGES NOTHING %s\n' "$pat" >> "$WORKDIR/diff.$label"
                fi
            elif [ -n "$a" ]; then
                rn3="$(printf '%s\n' "$(gen_noisl "$pat" "$args")" | stamp_strip | prog_region)"
                if [ "$ra" != "$rn3" ]; then
                    rnoislmoved=$((rnoislmoved + 1))
                    printf 'NO ISLAND STAMPED YET -fno-alt-island MOVES THE REGION %s\n' "$pat" >> "$WORKDIR/diff.$label"
                fi
            fi
            # [FORM-CHAR] THE FOLD CONVERSE, the island pair's shape exactly
            # and SCOPED TO ARTIFACTS THAT CARRY THE STAMP (i.e. VM
            # artifacts): at the default position the flag's one consumer is
            # the VM's fold row (clskit.c `byte-fold-default`, D138 Q1), so a DFA artifact is byte-identical under it BY
            # CONSTRUCTION rather than by sweep — running the deny build
            # there would double this gate's compile count to re-derive a
            # structural fact. An artifact that STAMPS folds must differ from
            # its own `-fno-cls-fold` build; a VM artifact that stamps 0 must
            # be byte-identical to it, which is what makes the denied build a
            # usable reference for every other check that leans on it.
            if [ -n "${fold_a:-}" ]; then
                if [ "$fold_a" -gt 0 ]; then
                    rn4="$(printf '%s\n' "$(gen_nofold "$pat" "$args")" | stamp_strip | prog_region)"
                    if [ "$ra" = "$rn4" ]; then
                        rfoldsame=$((rfoldsame + 1))
                        printf 'FOLDS STAMPED BUT DENYING THEM CHANGES NOTHING %s\n' "$pat" >> "$WORKDIR/diff.$label"
                    fi
                else
                    rn5="$(printf '%s\n' "$(gen_nofold "$pat" "$args")" | stamp_strip | prog_region)"
                    if [ "$ra" != "$rn5" ]; then
                        rnofoldmoved=$((rnofoldmoved + 1))
                        printf 'NO FOLD STAMPED YET -fno-cls-fold MOVES THE REGION %s\n' "$pat" >> "$WORKDIR/diff.$label"
                    fi
                fi
            fi
            # [OPT-CLSPACK] THE ATOM-TABLE CONVERSE, STAMPED DIRECTION ONLY: an
            # artifact stamping atoms must differ from its own -fno-cls-pack
            # build. The unstamped direction is structural rather than swept:
            # the flag's one reader is the table selection's deny mask, which
            # is consulted only for the atom row, and a zero stamp says that
            # row did not fire — so there is nothing for the deny to remove
            # (the fold axis's "by construction" argument, one axis over).
            if [ "${pack_a:-0}" -gt 0 ]; then
                rn7="$(printf '%s\n' "$(gen_deny "$pat" "$args" -fno-cls-pack)" | stamp_strip | prog_region)"
                if [ "$ra" = "$rn7" ]; then
                    rpacksame=$((rpacksame + 1))
                    printf 'ATOMS STAMPED BUT DENYING THEM CHANGES NOTHING %s\n' "$pat" >> "$WORKDIR/diff.$label"
                fi
            fi
            # [ART-POSS-ARMS] THE ARMS' CONVERSE, the literal-run pair's shape
            # and scope (VM artifacts, the stamp's carriers): a nonzero stamp
            # must differ from its own both-arms-denied build, and a zero
            # stamp must not (D47.3's do-or-die, read off the artifact).
            if [ -n "${poss_a:-}" ]; then
                rn8="$(printf '%s\n' "$(gen_deny "$pat" "$args" "-fno-poss-ctx-follow -fno-poss-bref-first")" | stamp_strip | prog_region)"
                if [ "$poss_a" -gt 0 ] && [ "$ra" = "$rn8" ]; then
                    # [recidtri] THE STAMP'S OWN DEFINITION, not a stronger
                    # one (match_api.md §6.3: an arm NEEDED for some positive
                    # possessify VERDICT). A verdict on a loop the SOURCE
                    # already made possessive/atomic marks nothing: its one
                    # consumer is the free discharge, which can move the
                    # route only where the route is free, so on a VM-forced
                    # pattern the stamp is true and the program is the same.
                    # Excused ONLY for a pattern whose TEXT says a
                    # possessive/atomic construct (`POSSRC_POP`, derived
                    # without the artifact); any other pattern's marks are
                    # the program, and an unchanged region there is the
                    # stamp lying.
                    if printf '%s\n' "$POSSRC_POP" | grep -qxF -- "$pat"; then
                        rpossverdict=$((rpossverdict + 1))
                        printf 'POSS ARMS STAMPED ON A SOURCE-POSSESSIVE/ATOMIC PATTERN (a verdict that marks nothing; excused) %s\n' "$pat" >> "$WORKDIR/diff.$label"
                    else
                        rposssame=$((rposssame + 1))
                        printf 'POSS ARMS STAMPED BUT DENYING THEM CHANGES NOTHING %s\n' "$pat" >> "$WORKDIR/diff.$label"
                    fi
                elif [ "$poss_a" -eq 0 ] && [ "$ra" != "$rn8" ]; then
                    rnopossmoved=$((rnopossmoved + 1))
                    printf 'NO POSS ARM STAMPED YET DENYING THE ARMS MOVES THE REGION %s\n' "$pat" >> "$WORKDIR/diff.$label"
                fi
            fi
            # [OPT-LITSCAN] S2a THE LITERAL-RUN CONVERSE, the fold pair's
            # shape and scope exactly (VM artifacts, the stamp's carriers).
            if [ -n "${lit_a:-}" ]; then
                rn6="$(printf '%s\n' "$(gen_nolit "$pat" "$args")" | stamp_strip | prog_region)"
                if [ "$lit_a" -gt 0 ] && [ "$ra" = "$rn6" ]; then
                    rlitsame=$((rlitsame + 1))
                    printf 'LIT RUNS STAMPED BUT DENYING THEM CHANGES NOTHING %s\n' "$pat" >> "$WORKDIR/diff.$label"
                elif [ "$lit_a" -eq 0 ] && [ "$ra" != "$rn6" ]; then
                    rnolitmoved=$((rnolitmoved + 1))
                    printf 'NO LIT RUN STAMPED YET -fno-lit-run MOVES THE REGION %s\n' "$pat" >> "$WORKDIR/diff.$label"
                fi
            fi
        else
            # The base REFUSED a pattern the subject accepts: the (A) base is
            # a post-module commit, so every pattern the corpus holds should be
            # in its grammar. A skip here would be a quieter sweep.
            rbaserefused=$((rbaserefused + 1))
            printf 'BASE REFUSED %s\n' "$pat" >> "$WORKDIR/diff.$label"
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
    echo "recursion-identity[$label] (A) program-region vs $ABASEPIN: same=$rsame differing=$rdiff base-refused=$rbaserefused island-stamped-but-deny-is-a-noop=$rislsame unstamped-but-deny-moves=$rnoislmoved fold-stamped-but-deny-is-a-noop=$rfoldsame unstamped-but-fold-deny-moves=$rnofoldmoved litrun-stamped-but-deny-is-a-noop=$rlitsame unstamped-but-litrun-deny-moves=$rnolitmoved atoms-stamped-but-deny-is-a-noop=$rpacksame poss-arms-stamped-but-deny-is-a-noop=$rposssame poss-arms-stamped-on-source-possessive=$rpossverdict unstamped-but-poss-deny-moves=$rnopossmoved call-bearing-in-population=$rcallbearing"
    if [ "$rcallbearing" -ne 0 ]; then
        bad "[$label] (A) $rcallbearing artifacts in the CALL-FREE population carry RX_VM_CALL_ macros. The two [DD-14.FB] region lines (the region-exit guard's type and capacity operand) are emitted only for a call-BEARING artifact, so this population's asserted count for them is ZERO; a non-zero one means the call-free classifier has leaked"
    fi
    if [ "$rbaserefused" -ne 0 ]; then
        bad "[$label] (A) the base $ABASEPIN REFUSED $rbaserefused pattern(s) this build accepts, so the region comparison did not cover them (the base is post-module: a refusal is a grammar the base predates, and the pin has to move past it):"
        grep '^BASE REFUSED' "$WORKDIR/diff.$label" | head -10 >&2
    fi
    if [ "$rislsame" -ne 0 ]; then
        bad "[$label] (A) $rislsame artifacts stamp RX_VM_ALT_ISLANDS > 0 and yet are BYTE-IDENTICAL to their own -fno-alt-island build. The stamp claims a trie the program does not contain — the direction a merely decorative count fails in, and the reason this is a biconditional against the DENY AXIS rather than against a pin that decays:"
        grep '^ISLAND STAMPED BUT DENYING IT CHANGES NOTHING' "$WORKDIR/diff.$label" | head -10 >&2
    fi
    if [ "$rnoislmoved" -ne 0 ]; then
        bad "[$label] $rnoislmoved artifacts stamp NO island and yet -fno-alt-island MOVES their program region. Denying an axis that did not fire must change nothing — that byte-identity is what makes the denied build a usable reference for every other check that leans on it:"
        grep '^NO ISLAND STAMPED YET' "$WORKDIR/diff.$label" | head -10 >&2
    fi
    # [FORM-CHAR] the fold axis's two converse directions, the island pair's
    # wording and reasons one axis over.
    if [ "$rfoldsame" -ne 0 ]; then
        bad "[$label] (A) $rfoldsame artifacts stamp RX_VM_CLS_FOLDS > 0 and yet are BYTE-IDENTICAL to their own -fno-cls-fold build. The stamp claims a fold compare the program does not contain — the direction a merely decorative count fails in:"
        grep '^FOLDS STAMPED BUT DENYING THEM CHANGES NOTHING' "$WORKDIR/diff.$label" | head -10 >&2
    fi
    if [ "$rlitsame" -ne 0 ]; then
        bad "[$label] (A) $rlitsame artifacts stamp RX_VM_LIT_RUNS > 0 and yet are BYTE-IDENTICAL to their own -fno-lit-run build. The stamp claims a run compare the program does not contain:"
        grep '^LIT RUNS STAMPED BUT DENYING THEM CHANGES NOTHING' "$WORKDIR/diff.$label" | head -10 >&2
    fi
    if [ "$rpacksame" -ne 0 ]; then
        bad "[$label] (A) $rpacksame artifacts stamp RX_VM_CLS_ATOMS > 0 and yet are BYTE-IDENTICAL to their own -fno-cls-pack build. The stamp claims an atom table the program does not read:"
        grep '^ATOMS STAMPED BUT DENYING THEM CHANGES NOTHING' "$WORKDIR/diff.$label" | head -10 >&2
    fi
    if [ "$rnolitmoved" -ne 0 ]; then
        bad "[$label] $rnolitmoved VM artifacts stamp ZERO literal runs and yet -fno-lit-run MOVES their program region. Denying an axis that did not fire must change nothing:"
        grep '^NO LIT RUN STAMPED YET' "$WORKDIR/diff.$label" | head -10 >&2
    fi
    if [ "$rnofoldmoved" -ne 0 ]; then
        bad "[$label] $rnofoldmoved VM artifacts stamp ZERO folds and yet -fno-cls-fold MOVES their program region. Denying an axis that did not fire must change nothing:"
        grep '^NO FOLD STAMPED YET' "$WORKDIR/diff.$label" | head -10 >&2
    fi
    # THE NON-VACUITY FLOOR IS AN ENUMERATED MANIFEST, NOT A NUMBER (panel r53,
    # F4). "At least one island moved" was argued rather than measured, and it
    # read GREEN under any narrowing that left a single island standing —
    # raising VM_ISL_MIN_BRANCHES_PREFIXED to 40 passes that floor. The check
    # is now the same staleness assertion ELIDED_PATTERNS and
    # SIZE_TERM_REGION_MOVERS carried (retired at [RECID-A]): every NAMED pattern must still stamp one.
    isl_manifest_missing=0
    while IFS= read -r ipat; do
        [ -n "$ipat" ] || continue
        ia="$(gen_a "$ipat" "$args")"
        [ -n "$ia" ] || continue          # refused on this axis; not this check's claim
        # THE STAMP IS VM-ROUTE-ONLY (docs/spec/match_api.md §6.3), so a
        # pattern this axis routes to the DFA carries none and is not this
        # manifest's claim either. Measured the hard way: without this gate the
        # list failed 9 of 11 on the default axis, where a capture-free literal
        # alternation is a DFA artifact — which is the DFA determinizing the
        # same trie for free, i.e. the island working as designed, not missing.
        case "$ia" in *'#define RX_ENGINE "vm"'*) ;; *) continue ;; esac
        in="$(printf '%s\n' "$ia" | sed -n 's/^#define RX_VM_ALT_ISLANDS \([0-9]*\)$/\1/p' | head -1)"
        if [ "${in:-0}" -lt 1 ]; then
            isl_manifest_missing=$((isl_manifest_missing + 1))
            [ "$isl_manifest_missing" -le 6 ] && echo "  ISLAND MANIFEST[$label]: '$ipat' no longer stamps an island" >&2
        fi
    done <<ISL_EOF
$ISLAND_PATTERNS
ISL_EOF
    if [ "$isl_manifest_missing" -ne 0 ]; then
        bad "[$label] $isl_manifest_missing of the ISLAND_PATTERNS manifest no longer stamp an alternation island. Either the predicate narrowed — in which case this list is the record of what that costs and the narrowing must be argued against it — or the analysis broke. Do not silently shorten the list"
    fi
    # [FORM-CHAR] the fold manifest, ISLAND_PATTERNS' check verbatim one axis
    # over (same VM-route gate, same do-not-silently-shorten rule).
    fold_manifest_missing=0
    while IFS= read -r fpat; do
        [ -n "$fpat" ] || continue
        fa="$(gen_a "$fpat" "$args")"
        [ -n "$fa" ] || continue          # refused on this axis; not this check's claim
        case "$fa" in *'#define RX_ENGINE "vm"'*) ;; *) continue ;; esac
        fn="$(printf '%s\n' "$fa" | sed -n 's/^#define RX_VM_CLS_FOLDS \([0-9]*\)$/\1/p' | head -1)"
        if [ "${fn:-0}" -lt 1 ]; then
            fold_manifest_missing=$((fold_manifest_missing + 1))
            [ "$fold_manifest_missing" -le 6 ] && echo "  FOLD MANIFEST[$label]: '$fpat' no longer stamps a fold" >&2
        fi
    done <<FOLD_EOF
$FOLD_PATTERNS
FOLD_EOF
    # [OPT-LITSCAN] S2a the literal-run manifest, the fold check verbatim.
    lit_manifest_missing=0
    while IFS= read -r lpat; do
        [ -n "$lpat" ] || continue
        la="$(gen_a "$lpat" "$args")"
        [ -n "$la" ] || continue
        case "$la" in *'#define RX_ENGINE "vm"'*) ;; *) continue ;; esac
        ln="$(printf '%s\n' "$la" | sed -n 's/^#define RX_VM_LIT_RUNS \([0-9]*\)$/\1/p' | head -1)"
        if [ "${ln:-0}" -lt 1 ]; then
            lit_manifest_missing=$((lit_manifest_missing + 1))
            [ "$lit_manifest_missing" -le 6 ] && echo "  LIT MANIFEST[$label]: '$lpat' no longer stamps a literal run" >&2
        fi
    done <<LIT_EOF
$LIT_PATTERNS
LIT_EOF
    # [ART-POSS-ARMS] the arms' manifest, the lit-run check verbatim (VM
    # artifacts only: --no-captures routes two of the three to the DFA).
    poss_manifest_missing=0
    while IFS= read -r ppat; do
        [ -n "$ppat" ] || continue
        pa="$(gen_a "$ppat" "$args")"
        [ -n "$pa" ] || continue
        case "$pa" in *'#define RX_ENGINE "vm"'*) ;; *) continue ;; esac
        pn="$(printf '%s\n' "$pa" | sed -n 's/^#define RX_VM_POSS_ARMS 0x\([0-9a-f]*\)u$/\1/p' | head -1)"
        if [ "$((16#${pn:-0}))" -lt 1 ]; then
            poss_manifest_missing=$((poss_manifest_missing + 1))
            [ "$poss_manifest_missing" -le 6 ] && echo "  POSS MANIFEST[$label]: '$ppat' no longer stamps a possessify arm" >&2
        fi
    done <<POSS_EOF
$POSS_PATTERNS
POSS_EOF
    if [ "$poss_manifest_missing" -ne 0 ]; then
        bad "[$label] $poss_manifest_missing of the POSS_PATTERNS manifest (docs/design/poss_arms.md §5.2's corpus movers) no longer stamp a possessify arm. Either an arm narrowed or the stamp broke. Do not silently shorten the list"
    fi
    if [ "$label" = "default" ]; then
        # the strict half of the converse keeps its named witnesses: no
        # POSS_PATTERNS member may be a source-possessive/atomic pattern, or the
        # excuse below would reach the very patterns that prove the stamp.
        while IFS= read -r ppat; do
            [ -n "$ppat" ] || continue
            if printf '%s\n' "$POSSRC_POP" | grep -qxF -- "$ppat"; then
                bad "[$label] POSS_PATTERNS member '$ppat' is a source-possessive/atomic pattern, so the stamped-direction converse would excuse it: the manifest's strict witnesses must be patterns whose arms MARK"
            fi
        done <<PSRC_EOF
$POSS_PATTERNS
PSRC_EOF
    fi
    # The excuse for a verdict that marks nothing is itself a counted
    # population (K35): bounded above by its own text census, and floored on
    # the axis that reaches it most (measured 16 on --engine=vm, 5 on default),
    # because an excuse nothing uses is a stale excuse -- the day the stamp
    # becomes consequence-aware this goes red and the excuse is deleted.
    if [ "$rpossverdict" -gt "$NPOSSSRC" ]; then
        bad "[$label] (A) $rpossverdict artifacts were excused as 'stamp on a source-possessive/atomic pattern' against a text census of only $NPOSSSRC such call-free patterns -- the excuse is reaching patterns it was not drawn from"
    fi
    if [ "$label" = "vm" ] && [ "$rpossverdict" -lt 8 ]; then
        bad "[vm] only $rpossverdict artifacts used the source-possessive excuse (measured 16 at landing, floor 8): the stamp may have become consequence-aware, in which case delete the excuse; or the population moved. Re-derive, do not lower the floor"
    fi
    if [ "$rposssame" -ne 0 ]; then
        bad "[$label] (A) $rposssame artifacts stamp RX_VM_POSS_ARMS nonzero and yet are BYTE-IDENTICAL to their own both-arms-denied build. The stamp claims an arm the program does not show:"
        grep '^POSS ARMS STAMPED BUT DENYING THEM CHANGES NOTHING' "$WORKDIR/diff.$label" | head -10 >&2
    fi
    if [ "$rnopossmoved" -ne 0 ]; then
        bad "[$label] $rnopossmoved VM artifacts stamp RX_VM_POSS_ARMS 0x0u and yet denying both arms MOVES their program region. A denied arm's bit must be 0 and an unneeded arm must change nothing (D47.3):"
        grep '^NO POSS ARM STAMPED YET' "$WORKDIR/diff.$label" | head -10 >&2
    fi
    if [ "$lit_manifest_missing" -ne 0 ]; then
        bad "[$label] $lit_manifest_missing of the LIT_PATTERNS manifest no longer stamp a literal-run compare. Either pcrec_lit_run narrowed or the island run arm broke. Do not silently shorten the list"
    fi
    if [ "$fold_manifest_missing" -ne 0 ]; then
        bad "[$label] $fold_manifest_missing of the FOLD_PATTERNS manifest no longer stamp an ascii-fold class test. Either clskit.c's is_ascii_fold_pair (the fold rows' predicate) narrowed — in which case this list is the record of what that costs — or the classification broke. Do not silently shorten the list"
    fi
    if [ "$rdiff" -ne 0 ]; then
        bad "[$label] (A) $rdiff call-free patterns emit a DIFFERENT PROGRAM REGION than the base $ABASEPIN. The base is a ruled main commit and carries no exception list ([RECID-A]): a landing that moves a call-free region on purpose re-pins ABASEPIN in the same change, the way (B)'s FILEPIN moves at an abi bump; one that did not mean to is the finding:"
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
       && [ "$rbaserefused" -eq 0 ]; then
        ok "[$label] (B) WHOLE-FILE byte identity: ALL $same call-free corpus patterns emit IDENTICAL C (raw, and therefore also past D37's three stamp lines, each verified present on both sides) against a compiler built from the pin $FILEPIN — zero differing, zero refusal mismatches, and zero elision movement, which is what a post-wave-G pin must show"
        ok "[$label] (A) PROGRAM-REGION identity: $rsame call-free patterns emit an IDENTICAL program region ('goto <p>_L0;' .. '<p>_accept:', unfiltered past the D37 stamps, comment changes included) against the (A) base $ABASEPIN — no exception list, no canonicalizer, 0 artifacts in this call-free population carry the call machinery, and the base accepted every pattern"
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
        eng_a="$(pcrec_run "$PCREC" --features all -p rx -o - --pattern "$pat" 2>/dev/null | grep -m1 '^    \.engine = ')"
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
        pcrec_run "$PCREC" --features all -p q -o "$d/a/q.c" --pattern "$pat" >/dev/null 2>&1 || ok_build=0
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
