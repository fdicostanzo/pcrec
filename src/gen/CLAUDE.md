# src/gen — C code generation

Emits self-contained gcc-dialect C from the DFA machines. Two engines (D7):
ENG_UNANCH for patterns without `^` (including `$`-bearing ones since M2.7/D8) — table-driven O(n) forward scan
(leftmost-first match end) + reverse scan (match start), with a memchr/bitmap
start-state prefilter; ENG_ATTEMPT for `^` patterns — per-start computed-goto
attempt loop with EOL-variant states. Table emission exists because gcc compile
time on huge computed-goto functions is superlinear (R1 A-3). Generated code
has zero dependency on pcrec at build or run time.

## [M6-READ] THE EMITTED VOCABULARY, and the two rules that keep it working

The generated C is a first-class deliverable: it carries an orientation block,
data-structure block comments with class and state LEGENDS, section banners,
`//` line comments, and full names for every locally-scoped identifier. The
style of record is `docs/design/m6read_samples/` (approved 2026-08-21).

WHAT IS FROZEN. Everything with linkage, plus every name inside the shared
`PCREC_RX_ABI_H` block — `rx_ctx` and its fields, `rx_matchfn`,
`rx_group_entry`, `struct rx_info`, `PCREC_*`. That block is spec §2's
verbatim quote and `emit_rx_abi_types` is EXCLUDED BY NAME from the rename
tooling (`scripts/m6read_rename_emitted.py`), because it DECLARES fields
called `pos` and `caps`: a rename that reaches it renames the ABI itself and
every artifact stops compiling. Measured, not theorised.

WHAT MOVED (emit_dfa.c): `fcls/ftr/facc/rcls/rtr/racc/first/fs/rs` ->
`forward_byte_class / forward_next_state / forward_is_accepting /
reverse_* / can_begin_match / forward_stay / reverse_stay`; locals
`pos/last/st/est/pp/rst/erst/sfound/end/cl` -> `scan_position /
last_accept_position / forward_state / forward_view_state / rewind_position /
reverse_state / reverse_view_state / match_start_position /
match_end_position / forward_class`. ENG_ATTEMPT: `cls/acc2/seed/gseed/t<N>`
-> `byte_class / is_accepting_by_class / seed_state / gstart_seed_state /
targets_<N>`.

WHAT MOVED (emit_vm.c): `rx_work` -> `rx_run_state` with fields
`slot_values / resume_stack / trail / resume_depth / trail_depth /
steps_left / work_left`; `rx_match_impl` -> `rx_match_anchored`,
`rx_unwind` -> `rx_reset_for_next_attempt`, `rx_caps_out` ->
`rx_report_captures`; `RX_NSTATE` -> `RX_NSLOTS` (it counts SLOTS),
`RX_BT_FRAMES` -> `RX_RESUME_FRAMES`, `RX_MRL_SHORT`/`RX_MRL_CAP` ->
`RX_PRUNE_TOO_SHORT`/`RX_PRUNE_CLAMP_SPAN`.

**RULE 1: A NAME CAN CARRY A PROPERTY, AND THE RENAME MUST PRESERVE IT.**
`RX_MRL_*` was a GREPPABLE FAMILY, and tests/mrl asserts an ABSENCE with
`grep -q 'RX_PRUNE_'` ("no bound under -fno-length-prune"). Renaming the two
macros to unrelated names would have made that check match nothing and pass
vacuously. The family prefix is why they are `RX_PRUNE_*` and not the shorter
names the sample first proposed.

**RULE 2: A VARIABLE SPELLED IN TWO PLACES WILL BE RENAMED IN ONE.** The
revdet rung declares `%s_rv%d_mk` and USES `%s_mk` composed from an `rv`
base. The two format strings share no substring, so a rename moved the uses,
left the declarations, and emitted C that does not compile — while pcrec
itself built fine. Nothing makes that agreement structural; the declaration
site now carries a comment saying so. **Before touching emitted names, grep
for BOTH the composed and the direct spelling.**

THE TWO GATES. `tests/codegen/run_object_neutrality.sh` (two builds, compares
.text/.rodata bytes and exported symbols) proves sameness; the existing
two-artifact differentials (tests/altcls, tests/possessify) compile emitted C
with `-Werror` and link two artifacts in one TU, which is a stronger
COMPILABILITY check and is what caught rule 2's breakage. This pass needed
both.

`emit_unanchored` handles EOL and non-EOL machines in ONE function on purpose
(M2.12): M2.7 forked a second copy for `$` patterns, and that fork is how the
prefilter and skip loops silently went missing from the `$` path for an entire
milestone. Under EOL every skip is bounded at n-1 and scan avoidance runs
BEFORE the accept/EOL evaluation — see D11, and note the ordering rule is the
subtle half.

**[M6.2 wave A] A THIRD POSITION VIEW**, `\z`'s (`DState.endvar`), on the same
machinery. Three things to know before touching it:

- **`views = eol || endv` is what every site that used to read `eol` now
  reads.** What the D11 `n-1` bound and the evaluation ORDER protect is "a
  state can accept at a position a skip would pass", and an END view creates
  exactly that situation at `pos == n`. Both flags are false for every pattern
  in the pre-wave corpus, so `views == eol` there and no byte moves.
- **`emit_view_select` is written as ONE BRANCH THAT REPRODUCES THE OLD
  STRING**, not as a general form that happens to agree with it. Byte-identity
  is a property of that function, so `has_end == false` emits the pre-wave text
  character for character rather than a re-derivation of it. Same rule in
  `emit_attempt`: a state whose `endvar < 0` takes the untouched arm.
- **`endvar == -1` means "same as the EOL VIEW"**, unlike `eolvar == -1`
  ("same as this state"), so the emitted selector walks `fendv -> fev ->
  self`. `tests/codegen/run_endvar_identity.sh` is the gate on all of it, with
  sabotage S69 as its measured failing direction.

## **[M6.2 wave B] `\b`/`\B`: a CLASS axis, not a fourth position view**

`\z` added a third POSITION view. `\b` adds a different kind of thing, and
conflating the two is the mistake to avoid here. Its accept depends on the
byte at `pos`, so the axis is the byte CLASS — which the transition lookup
already has in a register — and `src/ir/dfa.c` bakes the choice into `tr[]`
itself. Four sites in this file, and what gates each:

- **`facc2`/`racc2`/`acc2`, the class-indexed accept (§3.6)**, emitted on
  `dfa_has_wacc(d)`: does ANY state's accept actually differ between "the next
  byte is a word character" and "it is not". Deliberately NOT "the pattern
  contains `\b`" — a `\b` that is not reachable at an accepting position
  leaves every state's two bits equal and keeps the pre-wave scalar loop.
- **§3.6.2's COMPOSITION RULE**, which is the half that is easy to get wrong:
  class-indexed at every position that HAS a next byte, SCALAR at `pos == n`,
  where out-of-subject counts as non-word — a property of the POSITION, not of
  any byte. The emitted guard is also what keeps `s[pos]` unread at `pos == n`
  (K27's class), and the class is computed ONCE into a `cl` local shared with
  the transition so the structural check has one named thing to look at.
- **`fseed`/`rseed`, MECHANISM 4 (§3.8)**, emitted only when `s1w != s1`.
  FOUR boundaries, not two, and the reverse pair is the sharp one. Forward
  init reads `s[startpos-1]`; reverse init reads `s[end]`, which cannot be a
  compile-time constant because the forward loop produces `end`; reverse
  TERMINATION reads `s[startpos-1]` and is **ATTACHED TO THE `rewind_position <= startpos`
  BREAK, not peeled below the loop** — the reverse loop has a SECOND exit
  (dead state), and an epilogue would run on it, recording `match_start_position` at a
  position the walk never reached and indexing the accept table with a
  NEGATIVE state (R30 N9). The forward range guard MOVES ABOVE `int st = ...`
  under `fseed`, because that initializer now dereferences the subject.
- **`pick_skip_states` DECLINES a state whose accept varies by class**, and
  this is a DEVIATION from `assertions_design.md` §3.6.1 that the wave
  returns. §3.6.1 argues `\b` cannot suffer the D11 skip hazard because "a
  skip set is a union of classes, so every byte in the run has the same
  next-is-word value" — the second half does not follow, since a union of
  classes may contain both word and non-word classes (a state staying put on
  both `a` and ` ` has such a stay set). Declining is always available, always
  safe, and costs nothing on any pattern without a next-byte-sensitive accept.
  `start_acc` widens to the OR over both bits for §3.6.1's own reason
  (`\bx*` on `'a x'`), and `!fseed` joins the never-matches early-out, whose
  proof is about the ONE start state `fs`.

`emit_attempt` carries the same two mechanisms in its own shapes: a per-STATE
accept split (only where that state's two bits differ, so every other state
keeps the pre-wave text) and a `seed[]` table of label addresses for the
per-ATTEMPT start dispatch — which on that engine is not once per search,
since it re-initializes at every one of its `n+1` attempts.

Gates: `tests/codegen/run_wordctx_identity.sh` (sabotage S71) for the claim
that none of this costs a `\b`-free pattern a byte, and
`run_codegen_tests.sh`'s `[M6.2-WORDB]` block (sabotages S72/S73) for the two
memory-safety rules no oracle can see.

## **[M6.2 wave C] `(?m)`: the class axis becomes THREE-VALUED, and ENG_ATTEMPT gets its first scan avoidance**

Wave B's class axis was a bool. `(?m)$` reads a DIFFERENT property of the same
byte, so it becomes the `UPC_*` partition (`src/core/internal.h`) and every
site in this file that read `waccept`, `wlist` or `s1w` reads an array index
instead. Four things changed here beyond that mechanical rewrite:

- **`upc_of_newline(d)` and the EOL-position accept.** Wave B's note at
  `emit_attempt`'s EOL arm said the class axis has nothing to add there,
  because the byte at an EOL position is `'\n'` and `'\n'` is not a word
  character. That reasoning was right for its axis and its CONCLUSION IS NOW
  WRONG: `'\n'` IS the newline definition, which is exactly what `(?m)$`
  reads. `(?m)a(?:$|\Z)` is the shape that needs both — the `\Z` half makes an
  EOL view exist and the `(?m)$` half makes that view's accept depend on the
  byte the arm's own entry test just pinned. Both indices are compile-time
  facts there (the view from the position, the class from `s[pos] == '\n'`),
  so it is a CONSTANT, not a table read.
- **The `eolvar`-only arm SPLITS when its two positions disagree.** `pos == n`
  (no next byte, §3.6.2's scalar) and `pos + 1 == n && s[pos] == '\n'` (next
  byte pinned to the newline) were one merged `if` before this wave, and could
  be: nothing could tell them apart until an EOL view's accept depended on the
  next byte. They split only when the two bits differ, so a machine with no
  newline refinement emits the pre-wave text character for character.
- **[D63] THE CANDIDATE-START DERIVATION, one site and two callers.** D63
  rules that the DERIVATION (state row -> byte set -> memchr-vs-bitmap choice
  -> table emission) is the SAME question for every engine and MUST be
  factored; the LOOP INTEGRATION differs structurally and stays per-engine.
  `CandSet`/`cand_derive`/`cand_emit_table` are that factoring, with
  `cand_from_escapes` (ENG_UNANCH's wrapped start state) and
  `cand_from_live_seeds` (ENG_ATTEMPT's `(?m)^`) as its two callers. The `(?m)^`
  twist is a FIELD, not a fork: `offset` says the candidate is the found byte's
  position PLUS ONE, because a line start is the byte after a newline.
  **The candidate set is the LIVE-SEED set, and that is stronger than the
  design's own sentence.** §3.7.2 says a `(?m)^`-anchored attempt "can only
  begin at offset 0 or immediately after a `'\n'`" — true of a FULLY-anchored
  pattern and false of `(?m)^a|b`, whose `b` branch can begin anywhere.
  Deriving from which `s1u[]` entries are LIVE gets both right: `(?m)^ERROR`
  yields the newline set and a `memchr`, `(?m)^a|b` yields all 256 and no
  prefilter at all. Sabotage S81 is the design's sentence written as code.
  D63's other named instances (D8's `^`-on-some-branches shape, partial `\G`)
  become CALLERS of these three functions rather than new copies.
  `pcrec_emit_prologue` calls `attempt_cand` too — the SAME function, never a
  restatement of its condition — because it has to decide about
  `#include <string.h>` before any body exists.
- **The postures for §3.6.1's five scan-avoidance mechanisms are all DECLINE
  or ORDERING; not one is an intersection — and only ONE of the five turns
  out to be a live hazard.** The design proposes intersections for rows 2-5;
  wave C wrote a sabotage per mechanism and MEASURED each before committing
  it, by sweeping every corpus pattern whose ARTIFACT the edit changes through
  107 subjects under the find-all loop:
  - rows 3 and 5 (the self-loop skips) DECLINE via `pick_skip_states`, and
    that is REAL: sabotage S78 turns `(?m)[^c]*$` on `"a\nb\nc"` from `(0,3)`
    into `(0,1)`.
  - rows 1 and 2 (the prefilters) share the widened `start_acc` gate, and
    **the widening is REDUNDANT**. D3's accept-pruning cuts the unanchored
    start self-loop out of every accepting closure, so a class the start state
    accepts on cannot transition back to it — it ESCAPES — so the prefilter's
    stay set never contains it. Narrowing `start_acc` changes 21 corpus
    artifacts and 0 answers over 2,247 cells. §3.6.1's `\bx*` prediction is
    false. The widening is KEPT (free, and the honest reading of "accepts on
    any class") and ships NO sabotage row; the same argument this file already
    makes for the neighbouring `last == (size_t)-1` gate.
  - row 4's compensating accept is NOT EMITTED under `views` at all, and even
    when re-emitted it can only UNDER-report (the EOL view's closure is a
    superset of the base's; a skip-eligible state's accept does not vary by
    class). 13 artifacts, 0 answers over 1,391 cells, and 0 new answers when
    combined with row 3's sabotage. No row.
  The §3.6.1 annotation carries the full table and what declining costs.

Gates: `tests/codegen/run_mlinectx_identity.sh` (sabotage S76) for the claim
that none of this costs a `(?m)`-free pattern a byte, and
`tests/assertions/run_mline_diff.sh` (sabotages S78/S81) for the
scan-avoidance cure and D63's candidate derivation on the only populations
that can break them.

## **[M6.2 wave D] `\G`: a FOURTH branch in front of the start dispatch, a THIRD `start_max` string, and one soundness bound on wave C's prefilter**

`\G` costs the ALPHABET nothing — it reads no byte — so unlike waves B and C
this one adds no axis. What it adds is a SECOND FAMILY of interior start
states (`Dfa.s1g[]`, closed with the `\G` bit set) and the emitter changes
that follow from it. Four sites, and what gates each:

- **The START DISPATCH becomes three-way**, gated on `dfa_needs_gseed` (do the
  two interior families differ at all). §4.2's three reachable rows, in this
  order and the order is load-bearing: `start == 0` first (BOTH `\A` and `\G`
  pass there, and testing `start == startpos` first would route offset 0 into
  the `\G`-only state and lose every `^`/`\A` branch), then
  `start == startpos`, then everything above it. The `\G`-free path is the
  pre-wave three-branch chain untouched — `emit_view_select`'s
  one-branch-that-reproduces-the-old-string discipline, applied to a chain
  this wave inserts a FOURTH branch ahead of.
- **`gtbl` is a REFINEMENT of `gseed`, never independent of it.** The two ask
  different questions — "do the families differ" vs "does the `\G` family vary
  by class" — and both are needed (`\G\bfoo|bar` has one live state for
  `start > startpos` and three for `start == startpos`, so a single flag emits
  a constant where a table belongs). But on a `\G`-FREE machine `s1g[] ==
  s1u[]`, so the second question answers exactly what `dfa_needs_seed` answers,
  and without the `&& gseed` conjunct every `\b` and `(?m)` artifact emits a
  `gseed[]` table no dispatch reads. That defect shipped in this wave's first
  draft and was found by MOVING THE REFERENCE KNOB (below), not by any test.
- **`start_max` IS A THIRD VALUE** (§4.1, DD-4's substantive answer): `0` when
  both interior families are dead, `startpos` when only the `\G` family is
  live, `n` otherwise. No wrap toggle and no new engine — ENG_ATTEMPT already
  emitted the un-self-looped shape, and a `\G`-anchored pattern is one attempt
  at exactly the position `\G` names. On a `\G`-free machine the middle row is
  unreachable and the two survivors are the pre-wave `anchored ? "0" : "n"`.
- **[D63] THE PREFILTER'S LOWER BOUND MOVES TO `startpos`**, and this is a
  SOUNDNESS fix rather than a new instance. `cand_from_live_seeds` derives from
  `s1u[]` — the states an attempt at `start > startpos` enters — and never
  looked at `s1g[]`, so wave C's `start > 0` guard is one attempt too wide the
  moment a pattern has both a `(?m)^` branch and a `\G` branch:
  `(?m)^a|\Gb` on `"xb"` at startpos 1 loses its match. `start > startpos`
  implies `start > 0`, so it is a strengthening of the existing guard rather
  than a second condition. Sabotage S82.

**THE REFERENCE KNOB IS AT THE EMITTER, NOT IN THE ANALYSIS, and that is this
wave's own check-design finding.** `-DPCREC_NO_GSTART` forces `gseed`/`gtbl`
false and `a_gst = a_bot` HERE, so the reference build IS the pre-wave emitter.
Waves A/B/C put their knobs in `src/ir/dfa.c`, inside the code their sabotages
edit — and the reference compiler is built from THE SAME (sabotaged) SOURCES,
so such a sabotage applies to both builds and CANCELS. Measured: wave B's S71
left `run_wordctx_identity.sh` at 1135/1135 IDENTICAL, and that script failed
only through a side effect (an orphaned parameter warning). Moving this wave's
knob is what exposed the dead `gseed[]` table above.

**[M6.2 REPAIR SLICE, 2026-08-19] THE OTHER THREE KNOBS WERE RE-PLACED ON THAT
FINDING, AND WHAT IT TOOK IS NOT WHAT THE FINDING PREDICTED.** "Put the knob
at the emitter" is sufficient for `\G` and NOT for `\z`, `\b` or `(?m)`,
and the difference is which stage decides the emitted text. `\G` refines no
alphabet and interns no state this emitter cannot neutralize, so forcing three
predicates false here reproduces the pre-wave artifact exactly. `\b` and
`(?m)` refine the ALPHABET and `\z` interns a STATE — no branch in this file
can un-refine a partition or un-intern a state, so the reference build still
emits the sabotaged class table. MEASURED: with an emitter-only knob, S71
leaves 1186/1186 `\b`-free artifacts BYTE-IDENTICAL, i.e. exactly as blind as
before. Each of the three therefore got TWO halves — this file's decision
points (`upc_emit_live`, `upc_emit_of_class`, `st_emit_endvar`, at the top of
the file with their own block comment) AND a `#ifndef` around the ANALYSIS'S
ACTION in `src/ir/dfa.c`. After both, all three rows are red on their own
gates through BYTES: S71 moves 1178 of 1186, S76 moves 1117 of 1201, and S69
(already at its action, unmoved) fails `endvaridentity` — every one with its
corpus arm fully green. The emitter half is byte-neutral in a shipped build and was measured
so — 1,261 of 1,261 corpus artifacts identical against the pre-slice
compiler — because every predicate folds to a constant.

The VM's share is one arm and one PARAMETER. `\G` is the only assertion in the
module whose truth is not a function of `(s, n, pos)`: `<prefix>_match_impl`
has `ctx->pos`, the offset THIS ATTEMPT began at, and the search entry's retry
loop moves it — so `<prefix>_startpos` is threaded in, emitted only where a
`\G` exists (`v->ngst`), on the MRL ceiling's precedent. The three entries pass
`startpos` / `ctx->pos` / `ctx->pos`, the last two being R30 E8's answer.

Gates: `tests/codegen/run_gstart_identity.sh` (sabotage S83) for the claim
that none of this costs a `\G`-free pattern a byte, and
`tests/assertions/run_gstart_diff.sh` (sabotage S82) for the find-all
contiguity, the two-entry agreement and the subject sweep — the three things
no `.rxt` corpus can express.

## **[M6.2 wave E] `\K`: ONE TERNARY, and no identity gate**

`\K` is the module's last construct and the only one with NO DFA path at all,
so unlike waves A-D this one adds nothing to `emit_dfa.c` — no view, no class
axis, no start family, no dispatch branch. Its whole footprint in this
directory is in `emit_vm.c`, and it is four things:

- **The write is a CAPTURE WRITE, spelled as one.** `vm_emit`'s `A_KRESET`
  arm calls `vm_set(v, 0, "(ptrdiff_t)pos", ...)` — the same primitive A_CAP's
  two writes go through — so `\K` inherits §3.2's write-and-undo discipline
  entire: the trail's EXACT OLD-VALUE restore (never a clear), the rewind on a
  failed attempt, and the listing event. It is the only arm in that switch
  that emits no test and cannot fail.
- **The slot is 0, and that choice IS the design.** Slot 0 is group 0's start,
  reserved by `nstate`'s `2 * ncaps` term since [M4.5b] and never written by
  anything (capture writes use `2*k` with `k >= 1`; every other family bases
  at `2 * (ngroups + 1)`). So the slot that already MEANS "the reported start"
  is the one `\K` writes: no slot is allocated, `PCREC_UNSET` becomes the "no
  `\K` was crossed on this path" signal for free (a position can never
  legitimately be -1), and `report_captures` reads one existing array element instead
  of taking a new parameter.
- **`vm_cost` charges ONE TRAIL ENTRY per emitted `\K`**, multiplied by the
  enclosing quantifier exactly as A_CAP's two are. This is the one place the
  construct is not free, and getting it wrong is not a missed optimisation —
  it under-sizes `trail_frames` and the artifact returns `PCREC_ERR_FRAMES` on
  a pattern it can match. `vm_count_slots` correctly allocates nothing.
- **`<prefix>_caps_out` derives `caps[0][0]` from slot 0 or from `start`**,
  gated on `v.nkreset`. Under the hybrid `start` is `win[0][0]` — the REVERSE
  PASS's answer, i.e. the PRE-`\K` start — which assertions_design.md §6.3
  rule 1 says may bound the search and must never be written out. Both arms
  are live: `a\Kb` on "ab" is (1,2) through the slot, `(?:a\K)?b` on "b" is
  (0,1) through the fallback, and the fallback is `\K`'s semantics rather than
  a defensive default.

**THIS IS THE ONLY SITE THAT READS `v.nkreset` INTO A DEFAULT ARTIFACT, WHICH
IS WHY THE WAVE SHIPS NO BYTE-IDENTITY GATE.** Two non-default surfaces read it
as well and neither weakens that: `--emit-ir`'s SLOTS row stops claiming slot 0
is entry-only when a `\K` exists (a listing saying otherwise would describe a
different program from the one beside it, §10's drift), and `--trace`'s ACCEPT
line reports the CONSUMED span and the REPORTED one, because on a `\K` artifact
they differ and either alone misleads. A listing writes no artifact; a traced
artifact is a different artifact by construction. Waves A-D each changed a construction spanning several
emitter decision points and each needed a corpus-wide comparison against a
reference build to say a construct-free pattern paid nothing. Here the claim
is about ONE predicate, so it is pinned structurally — `[M6.2-KRESET rule 1b]`
in `tests/codegen/run_codegen_tests.sh` quotes the pre-wave `report_captures` body as
a LITERAL, so a rewrite into some third shape fails too — and the corpus-wide
half was MEASURED ONCE against the genuine pre-wave COMPILER (1,208/1,208
identical at the default engine, 1,209/1,209 under `--engine=vm`). That
reference shares NO SOURCES with the subject, which is strictly stronger than
the `-D` knob builds the four gates use and is the direct answer to wave D's
own knob-placement finding.

**THE THREE ENTRIES NEEDED NO CHANGE, and that is R30 E8's rule 3 corrected
rather than discharged.** §6.3 derives "filter on the pre-`\K` start, return
the consumed length" from the DFA artifact's `rx_match` (`rx_search` plus
`caps[0][0] != ctx->pos`, returning `caps[0][1] - caps[0][0]`), and both lines
really do break under `\K`. But a `\K` pattern is VM-FORCED and never has that
entry: the VM's calls `<prefix>_match_impl` at `ctx->pos` directly, so the
anchoring is a property of the CALL rather than a test applied afterwards, and
the return is `pos - ctx->pos`, computed from positions and never from `caps`.
`ab\K` is the cell where those two numbers differ — reported span (2,2),
consumed length 2 — and a D38 callout advancing by the former would never
move. Evidence rather than assertion: `tests/assertions/kreset_entries.c`
drives all three entries, `run_kreset_diff.sh` §2 checks both match-here ones
against libpcre2's answer for `\G(?:PAT)` at the same startpos, and
`[M6.2-KRESET rule 3]`/`rule 3b` pin both shapes structurally.

Gates: `tests/codegen/run_codegen_tests.sh`'s `[M6.2-KRESET]` block
(sabotages S85 and S86, with disjoint symptoms) and
`tests/assertions/run_kreset_diff.sh`. No identity gate, by the argument
above.

## **[DD-14 wave B+C] THE SUBROUTINE CALL: a call IS a resume frame, and the callee region has its OWN exit**

`(?1)` runs another group's pattern here and **puts the capture state back on
the way out**. Four measurements force the lowering and the whole of this
section is their consequence; `docs/design/subroutines_design.md` §5 is the
derivation, and §5.9 BUILT and RAN it before any of this was written.

**A CALL IS A RESUME FRAME (§5.1), and §5.2 is a DERIVATION rather than a
preference.** The obvious implementation — `const void *call_stack[N]` indexed
by call depth and POPPED at the return — has a bug that needs three events to
appear: A returns, its continuation calls B (overwriting A's return label), B
fails, the backtracker resumes inside A's callee, and A's second return lands
in B's continuation. The frame's depth mark restores the DEPTH and cannot
restore the CONTENTS. §5.9 built both: the array build is wrong on 3 of 50
cells, one of them a FALSE MATCH, and agrees on the other 47 — which is what
localises the failure to the clobber sequence. So the return label lives in
the frame, which is the structure whose contents the backtracker already
restores by construction.

**THE FRAME GAINS TWO FIELDS, NOT THREE (D71.1).** §5.1 has `call_ret`,
`call_top` and `call_mark`, and a two-line fail label. D71 item 1 keeps
`PCREC_ERR_RECURSE` as a reserved ABI fact and moves the recursion-depth
COUNTER to a [V-H] diagnostic generation axis, so calls consume ORDINARY
FRAMES and a deep one answers `PCREC_ERR_FRAMES`. Two fields, ONE line.

**`call_top` IS ON EVERY FRAME AND THAT IS THE HALF A READER WILL THINK
REDUNDANT.** `RX_PUSH` stores it because the fail label restores it for EVERY
frame — and the frame a retreat pops after the innermost call frame is an
ORDINARY one pushed INSIDE the enclosing activation. **REPRODUCED before the
line was written**: without it, `^(a(?1)?b)$` on "aaabbb" loses the match and
the traced artifact shows group 1 coming back (2,5) where it must be (1,5),
one level off at every depth. `"aabb"` (depth 2) stays green, which is the
pair that names the failure. Sabotage S144.

**A CALL FRAME'S `resume_label` IS THE FAIL LABEL ITSELF**, which is not a
placeholder: when the frames inside a call are exhausted the call has no
alternatives, so popping it must continue failing — and the fail label then
needs NO knowledge of frame kinds and no branch.

**THE RETURN DOES NOT POP AND DOES NOT CUT.** §3.2 MEASURED the call
BACKTRACKABLE on 10.46 (it was atomic before 10.30), on a body reachable ONLY
by the call, with four atomic controls refusing. S145 and S146 are the two
rows, and they are two because a compiler that CUT gets the discriminator
wrong while still getting all four controls RIGHT.

**`W`: THE ACTIVATION-PRIVATE SAVE/RESTORE, AND THE TRAIL IS THE STORAGE.**
At the call site each slot in `W` gets a TRAILED SELF-WRITE — `RX_SET(s,
slot_values[s])`, which parks the value and leaves the slot alone, because
`RX_TRAIL` records the old value UNCONDITIONALLY with no same-value elision.
**The saves come AFTER the push and the order is load-bearing**: the call
frame's `trail_mark` is then exactly the index of the first save, so the
return reads `W[j]` at `trail[trail_mark + j]` with `j` a compile-time
constant. The restore is itself TRAILED, so backtracking INTO a returned call
re-establishes the callee's own values — which §3.2 requires.

**`W` IS EVERY SLOT FAMILY, NOT THE CAPTURES, AND THAT ANSWER IS MEASURED
WRONG RATHER THAN MERELY INCOMPLETE.** The capture-only set loses
`SLOT_GROUP<n>_PENDING` (a LOST MATCH: `^(a(?1)?b)\1$` on "aabbaabb" answers
nomatch where 10.46 answers (0,8), 11/2) and `SLOT_CUT_MARK<n>` (SIX FALSE
MATCHES whose language is EXACTLY the non-atomic control's — the atomic group
stopped being atomic, 4/6). Every family is written at a construct's ENTRY and
read at its EXIT, and two ACTIVATIONS of one construct are NESTED rather than
sequential. **Slots 0 and 1 are NEVER members**: `\K` writes slot 0 and §3.4(b)
MEASURED that a `\K` in a callee is NOT restored by a return. Rows S148-S153,
one per family.

**`W` IS BUILT HERE AND NOT IN `callgraph.c`, AND SO IS THE NULLABILITY
FIXPOINT** — a deviation from §4.4b's "one mechanism, and this is the only
list of its consumers". Both for the same reason: `W` is a set of SLOT
INDICES, which are assigned by `vm_count_slots`' own walk over this emitter's
rung decisions and exist nowhere else, and `vm_nullable` is `static` here and
is the emitter's own definition of the property the empty-iteration guard is
emitted on. `callgraph.c` owns the GRAPH both iterate over. The set is
assembled from the COUNTER RANGES each region's own `vm_count_slots` pass
consumed — five of the seven families replicate PER EMITTED COPY
(`^((?>a)){3}$` has ONE lexical atomic group and FOUR cut marks), so a walk
over NODES would count the wrong thing.

**THE LAYOUT COUNTS EVERY EMITTED REGION (§4.4c), AND THE SITE'S FIRST ANSWER
WAS WRONG.** `vm_count_slots` runs ONCE PER REGION in ascending target order
after the main-body walk, and `vm_emit` emits them in the same order, so the
running counters and the pre-pass agree site for site. A LEXICAL-only count is
an OUT-OF-BOUNDS SLOT WRITE, K27's class, and the reason is that **`X{0}`
emits nothing and counts nothing while a callee parked there is a REAL
IDIOM** — the classic pre-DEFINE spelling, measured matching on 10.46 for
plain, recursive, atomic and rung-bearing callees. The arm in
`vm_count_slots` is therefore EMPTY and §4.4c's proposed parameter is not
needed: the region walk starts AT the callee's own `A_CAP`, so no `{0,0}`
ancestor is on its path. Row S164, whose cell must carry a rung-bearing or
atomic callee — one with only capture slots allocates from a family `{0}`
does not prune and goes green.

**THE CALLEE REGION HAS ITS OWN EXIT, AND §3.5 MAKES THAT A RULE.** A call
reaches the GROUP, not the group's LEXICAL OCCURRENCE, and the wrapper belongs
to the occurrence: measured, a callee whose lexical home is a lookbehind must
leave through its own exit rather than the assertion's end-check-cut-and-
restore, one whose home is a negative lookahead must RETRY inside a region
that is cut on the assertion's success, and one whose home is atomic must GIVE
BACK. **It is an EXIT rule and not an entry rule** — a jump to the group's own
label lands AFTER a lookbehind's back-step, so the entry is fine. Row S163.

**THE FOLLOW IS SCOPED TO ZERO ACROSS THE REGION, FOR A THIRD REASON.**
`vm_atomic` scopes because of the CUT, `vm_look` because the follow OVERLAPS
the body, and a callee because the follow is **UNKNOWN**: a shared body has
many callers with different follows, and a rung bound baked from one caller's
follow is wrong for every other. Only the third reason survives wave G's
splice, which is why it is stated separately. Row S162, whose detector must be
a TWO-CALL-SITE cell — with one call site the baked bound is that site's own
and the artifact is correct.

**THE SECOND INDIRECT JUMP, AND THE `goto *` IS WRITTEN OUT INLINE.**
§5.8 amends this file's own one-indirect-jump decision to a RELATION —
`goto *` count == 1 (the fail label) + one per emitted SHARED CALLEE BODY —
and a CONSTANT would be wrong in both directions (three distinct callees give
four; a wave-G splice gives one). The design sketches `RX_RETURN` as a MACRO,
which would put one `goto *` in the definition and NONE at the uses, making
the relation unstateable. Emitting per region is a deliberate deviation and
`[DD-14-RECURSION rule 1]` in tests/codegen is what it buys — CONFIRMED on the
shipped emitter at 1 / 2 / 2 / 4 for call-free, one callee, three SITES to one
group, and three distinct groups. Row S168.

**EVERY BYTE OF THIS IS GATED ON ONE FLAG.** `Vm.has_calls` (i.e.
`cx->callgraph != NULL`) gates the frame's two fields, `RX_PUSH`'s extra line,
`RX_CALL`, the fail label's line and both reset functions — so §9.1's
byte-identity claim is STRUCTURAL rather than something a sweep discovers.
MEASURED anyway: 2,198 of 2,198 call-free corpus patterns byte-identical to a
`git archive` of the pre-module compiler, with the positive control
(the reference REFUSES all 98 call-bearing patterns) at `ctl_bad = 0`.
`[DD-14-RECURSION rule 2]` asserts the four names absent from a call-free
artifact and PRESENT in a call-bearing one, in the same run.

**AND `<prefix>_run_state_init` / `_reset_for_next_attempt` BOTH SET
`call_top = CALL_TOP_NONE`** (§5.6 sites 5a/5b). The first is not an
`ERR_FLOOR` site but a MISSING INITIALISER — R34's LENS2-7 found the design's
own prototype setting the sentinel by hand in `main()`, which is the kind of
scaffolding a prototype hides behind. The second is the per-START-POSITION
reset: a bump-along must not inherit the previous attempt's activation.

## The multi-engine naming surface (OS-0b)

One output file may eventually carry several engines, one per point of the
option product, behind a generated selector (D18/D20). Of the identifiers
this emitter produces, the large majority are FUNCTION-LOCAL statics, so two
engines in two functions cannot collide on them. The file-scope names are:

- `emit_rx_abi_types` — ONCE PER FILE, shared by every engine in it, and
  ([M4.4], D44/A-2) by every DIFFERENTLY-PREFIXED generated header sharing
  one TU too: `rx_ctx`, `rx_matchfn`, `rx_callout_ref`, `rx_group_entry`,
  `rx_info`, `rx_renderfn` are fixed-literal ABI types, never `<prefix>`-
  scoped (match_api_m4.md §7/§12.7 — a compiled matcher must link directly
  as a callout for another, regardless of either one's own `--prefix`).
  Wrapped in a PREFIX-INDEPENDENT `#ifndef PCREC_RX_ABI_H` guard: the R21
  panel MEASURED that a per-prefix guard fails the exact composability case
  it exists for (two differently-prefixed headers in one TU each derive a
  DIFFERENT guard name, so both bodies redefine the same types — a hard
  redefinition error). `<prefix>_span`, the one prior file-scope type,
  RETIRED at [M4.4] (D44.2) — no compatibility alias. **[ABI-NS] (D60 +
  addendum, 2026-08-18)**: the same guard now also carries every emitted
  UNIVERSAL MACRO, unprefixed and unconditional on every artifact — the
  give-up code space (`PCREC_ERR_STEPS`/`_FRAMES`/`_WORK`/`_FLOOR`; **[DD-14
  wave A, 2026-08-24, D71 item 1]: `PCREC_ERR_RECURSE` joined and `_FLOOR`
  moved −4 → −5 — reserved, no producer yet**), the BELOW-THE-FLOOR
  `PCREC_ERR_INTERNAL` (**[DD-14] wave A commit 2, same date/ruling — NOT
  a give-up; module `lookaround`'s negative-polarity lookbehind end-check
  is its one producer, `src/gen/emit_vm.c`'s `vm_look_behind`**), the
  caps-array unset sentinel (`PCREC_UNSET`), the two engine constants
  (`PCREC_ENGINE_DFA`/`PCREC_ENGINE_VM`, new — naming `rx_info.engine`'s
  formerly number-only contract), and the nine D46 stamp bit constants
  (`PCREC_VM_RUNG_CURSOR`/`_FRAMES_BOUNDED`/`_FRAMES_UNBOUNDED`/`_REVDET`/
  `_COUNTER`, `PCREC_VM_STRAT_POSSESSIVE`/`_BACKTRACKING`,
  `PCREC_VM_PRUNE_CLAMPED`/`_UNCLAMPED`). Same no-alias rule as
  `<prefix>_span`'s retirement: the old per-`<PREFIX>` spellings of all of
  these are DELETED, not aliased.
- `emit_ncaps_macros` — ONCE PER FILE, PER-PREFIX. **[ABI-NS] (D60)
  narrowed this to `<PREFIX>_NCAPS` alone** — the one member of its old
  family (`<PREFIX>_NCAPS`/`_UNSET`/`_ERR_STEPS`/`_ERR_FRAMES`/`_ERR_WORK`/
  `_ERR_FLOOR`) whose VALUE genuinely varies per artifact; the other five
  moved to `emit_rx_abi_types` above.
- `emit_search_decl` / `emit_search_head`, `emit_match_decl`,
  `emit_match_caps_decl`, `emit_info_decl` — ONCE PER ENGINE, under that
  engine's own entry name(s), kept adjacent to their definitions so
  declaration and definition cannot drift apart.

## `<prefix>_search` carries `noclone`, and it is the fix for K24 ([K24])

`emit_search_head` emits `__attribute__((noclone))` above every
`<prefix>_search` definition, with a `/* K24: ... */` comment in the artifact
saying so. **Do not delete it as decoration, and do not "simplify" it to a
`hot`/`cold` pair.** Full reasoning at the function itself; the ruling and the
measurements are in docs/dev/known_issues.md's K24 CLOSED block and
docs/design/k24bisect_impl/k24_fix_note.md. The short form:

gcc -O2's partial-inlining pass sees this function's cheap entry guard in
front of a large scan body and SPLITS it into a trampoline plus a
separately-placed `<prefix>_search.part.0` holding the loop. The split loop's
instructions are IDENTICAL — the entire cost is code placement — and it is a
MEASURED 1.33x on a scan-bound pattern (293.5 vs 391.6 MB/s, pinned, 10
trials), which is what held compare.sh case (c)'s D12 floor red for three
days. `noclone` forbids exactly the one thing that pass needs, and the emitted
assembly is then byte-identical to the same source built `-O2
-fno-partial-inlining` — the bisect's own causal control. The lever must live
in the EMITTED TEXT because pcrec cannot dictate its users' CFLAGS.

Three measured facts to know before touching it:

- **The wrapper-side fix does not work.** `noipa`/`noinline` on
  `<prefix>_match`/`<prefix>_match_caps` leave the clone and the slow number
  in place. gcc's `pass_split_functions` runs on the CALLEE and never consults
  its callers' attributes. The wrappers' arrival at `[M4.4]` is what DATED the
  regression, not what the denial has to be spelled against.
- **`hot`/`cold` layout steering recovers the number while leaving the split
  in place, and the two combined measured WORSE than doing nothing** (288.7 vs
  293.5). Placement luck in one link is not a fix; a stranger's link is not
  this one.
- One site serves both engines: `emit_search_head` is the DFA artifact's
  exported entry AND (`storage == "static "`) the VM hybrid's prefilter, so
  both engines' DFA scan code is covered by one emission point. `noclone` does
  not block inlining, so the VM's full inline of that prefilter into its own
  `<prefix>_search` still happens (verified via `nm`), and case (j) measured
  neutral.

The VM's own hot path was never at risk and still isn't — `<prefix>_match_impl`
is a computed-goto function, and gcc cannot outline a body whose labels are
address-taken. Same reason the ENG_ATTEMPT engine was the one DFA shape that
never split. That is a property of those designs rather than luck, but nothing
CHECKS it, so it is written down rather than assumed.

The entry name comes from `engine_entry_name()` / `derived_name()` and is read
nowhere else, so a finder can hand each engine a distinct name without any
emitter learning that options have a product. Today there is one engine per
file and the name is `<prefix>_search` (plus its `<prefix>_match`/
`<prefix>_match_caps`/`<prefix>_info` siblings). Both properties are enforced
by the multi-engine block in tests/codegen/run_codegen_tests.sh, which
compiles a two-engine file; the cross-prefix guard property has its own check
there too (a two-differently-prefixed-headers-in-one-TU build).

## [OPT-ALTCLS]'s stamp lives in the SHARED prologue, not in either engine ([2026-08-17])

`emit_dfa.c`'s `pcrec_emit_prologue` gains `emit_altcls_macros`
(`<PREFIX>_ALTCLS_MERGES`/`<PREFIX>_ALTCLS_FACTORED`, right beside the STD1
feature stamp), read straight off `job->altcls_merges`/`job->altcls_factored`
(`src/opt/altcls.c` increments them at the exact points it acts). Placement is
the point worth stating: the D46 ACTIVITY stamps
(`RX_VM_RUNGS`/`RX_VM_STRATS`/`RX_VM_PRUNES`/`RX_VM_PREFILTER`) live in
`emit_vm.c` and are VM-artifacts-only, because possessify/revdet/MRL/prefilter
are all decided or consumed only on the VM path. (**[DD-13], 2026-08-25:**
`RX_ENGINE` is no longer in that list — it is UNCONDITIONAL now, and the DFA
has its own two selection stamps. See the section below.) ALTCLS is a pure AST rewrite
that runs BEFORE either engine is built (`src/core/compile.c`, immediately
after parse), so a capture-free pattern's DFA-only artifact carries the stamp
too — the plan row's own point that the DFA tier gets a real
byte-equivalence-class win from stage 1, not merely the VM. Emitted
unconditionally (STD1's own rule), including the honest `0`/`0` a pattern
with no alternation at all stamps. `emit_info_def`'s `strategy_denials` mask
also gained `PCREC_NO_ALTCLS_MERGE`/`PCREC_NO_ALTCLS_FACTOR`, for the same
reason the D47.3 family and the prefilter force pair are both masked out of
`rx_info.flags` there: the axis changes no answer, only the emitted shape.

## [DD-13] THE DFA ARTIFACT'S SELECTION STAMPS, and the D46 family's (a)/(b) split ([2026-08-25])

`emit_dfa.c` stamps three macros on every DFA artifact, in the same position
of the file `emit_vm.c` writes its own — immediately after the shared
prologue, before the engine body:

    /* Engine: dfa */
    #define RX_ENGINE        "dfa"
    #define RX_DFA_SCAN      "unanchored"   /* or "attempt" */
    #define RX_DFA_PREFILTER "byte-class"   /* five values, below */

**THE RULE THIS AMENDS.** `docs/spec/match_api.md` §6.3 used to make the whole
D46 macro family VM-only, on the premise that "a DFA artifact has nothing to
report", and this file's own comment added a §5.4 byte-identity worry. Wave G
falsified the premise — the DFA's byte-class skip prefilter is the email
specimen's headline ~23x mechanism — and §6.3's own closing warning ("a
consumer that `#if`s on `RX_ENGINE` is writing code that does not compile
against half the artifacts") is an argument FOR the change: a stamp that exists
on EVERY artifact is the only shape a consumer can `#if` on. §6.3 now splits the
family into **(a) SELECTION FACTS**, unconditional and present on every
artifact with an engine-appropriate value, and **(b) CAPACITY/ACTIVITY macros**
(`_VM_RUNGS`, `_STRATS`, `_PRUNES`, `_CALL_*`, the budgets, the frame/trail
sizes), which stay VM-only exactly as before because they report what the VM
DID. `RX_ENGINE_WHY` stays VM-only too, and for a fact-shaped reason rather
than an engine-shaped one: it names what FORCED the VM, and a DFA artifact was
not forced — `rx_info.engine_why` is `NULL` there for the same reason.

**ONE EMITTER FOR THE UNCONDITIONAL MACRO.** `pcrec_emit_engine_stamp`
(`emit_dfa.c`, declared in `src/core/internal.h`) writes `<PREFIX>_ENGINE` for
BOTH engines; `emit_vm.c` calls it with `"vm"`. Two `sb_printf`s spelling the
same `#define` would be two chances for it to drift, and drift is exactly what
an unconditional stamp exists to prevent. The PREFILTER stamps are deliberately
NOT shared: their value sets are different vocabularies (`RX_VM_PREFILTER` is
`"hybrid"`/`"none"`; the DFA's five are below), and a shared emitter for two
vocabularies is only a switch. The VM name is also stamped in pcrec-bench's
adapter today, so it does not move.

**THE VALUES COME OFF THE SAME DERIVATION THE LOOP DOES.** `RX_DFA_SCAN` reads
`job->engine`, the field `src/core/compile.c` sets at its `nfa_has_bot` fork,
through `dfa_scan_name` — which asks `dfa_engine_is_empty` FIRST ([DD-13c],
below).
`RX_DFA_PREFILTER` reads `unanch_start` (ENG_UNANCH) or `attempt_cand`
(ENG_ATTEMPT) — **`unanch_start` is new and is the reason the change touched
more than the stamp block**: ENG_UNANCH's start analysis (the view flags, the
candidate set, `start_acc`, the empty-engine proof) used to be the first forty
lines of `emit_unanchored`, and a stamp written before the loop exists needs to
read it too. This file's rule for that situation is `attempt_cand`'s — ONE
derivation with TWO readers, never a restatement of the condition at the second
site — and M2.12's lesson is why ("M2.7 forked a second copy, and the fork is
exactly how the prefilter and skip loops went missing from the `$` path for a
whole milestone"). The factoring is byte-neutral, measured: 2,473 of 2,473
compiled artifacts identical over the 2,758-pattern corpus before any stamp was
added. It also collapsed `emit_unanchored`'s TWO empty-engine early returns —
which emitted the same three lines with nothing written between them — into one
`us.empty`.

**THE FIVE PREFILTER VALUES**, and the `-bounded` pair is `plan.md` [DD-13]
(b)'s finding made readable rather than a distinction invented here:

| value | mechanism |
|---|---|
| `"none"` | no candidate-start filter; three causes — every position is a candidate, the artifact provably matches nothing, or (the largest) the START STATE ACCEPTS (`start_acc`), where no skip is sound at all |
| `"memchr"` | ONE candidate byte; a `memchr()` replaces the steps |
| `"byte-class"` | several; the 256-entry `<prefix>_can_begin_match` bitmap walk |
| `"memchr-bounded"` | the same under a `$`/`\Z`/`\z` view or a word context: bounded at `n - 1`, and WITHOUT the early `return 0` |
| `"byte-class-bounded"` | the bitmap form under the same bound |

`us.views` is the flag both the stamp and the emitted `fbound` string are built
from, so the two cannot disagree. MEASURED over the corpus, 2026-08-25:
`none` 380, `memchr` 327, `byte-class` 176, `memchr-bounded` 61,
`byte-class-bounded` 51; `unanchored` 815 / `attempt` 180.

**ABI 4** (D76/[TT-11]). The stamps change the emitted SCAFFOLDING, so
`rx_info.abi` moves `3` -> `4` and `tests/codegen/run_recursion_identity.sh`'s
comparison (B) is re-pinned in the same change. NO struct offset moved and NO
emitted program byte moved — that gate's comparison (A) is byte-identical
against the unchanged `ac4917d` pin, which is the proof the change is
scaffolding only. The check that holds each stamp to the loop it names is
`tests/codegen/run_dfa_stamps.sh`.

## [DD-13c] THE TWO SCOPE GAPS r37 FOUND, and the rule they corrected ([2026-08-25])

The D6 panel on [DD-13] found no defect in the stamps' VALUES; it found that
the stamps were silent about two things. Both fixes are about WHICH UNIT OWNS
A STAMP, and the answer both times is **the mechanism the stamp names, not the
artifact kind that usually carries it**.

**(#5) `dfa_engine_is_empty` and the third scan value `"empty"`.** A pattern
proven to match nothing emits a body that is one `return 0` — no table, no
loop, no skip — and BOTH emitters have that exit (`emit_unanchored` on
`unanch_start`'s `empty`; `emit_attempt` on `d->n == 0`). Those artifacts used
to stamp `"unanchored"`/`"attempt"`: the name of the loop the emitter WOULD
have written. `RX_DFA_SCAN` read `job->engine` alone, which answers "which
emitter ran" and not "what did it write", and for every other artifact those
are the same question. `dfa_engine_is_empty` is the derivation and `emit_attempt`
calls it instead of re-spelling `d->n == 0`, so the ONE-derivation-TWO-readers
rule holds on this axis too. `RX_DFA_PREFILTER` needed no clause: both
derivations already answer `"none"` there (`attempt_cand` refuses on
`d->n == 0`, `unanch_start` returns with `kind == DFA_PF_NONE`), and adding an
`if` would have been a third statement of one fact.

**(#6) A VM HYBRID STAMPS THE SCAN IT INLINES**, through the new shared
emitter `pcrec_emit_dfa_scan_stamps` (declared in `src/core/internal.h`). A
hybrid — `fit.prefilter` on — calls `pcrec_emit_dfa_engine` for a full
ENG_UNANCH/ENG_ATTEMPT body under the private name `<prefix>_prefilter`:
tables, D11 bound, candidate-start filter, the lot. It is literally THIS
emitter's scan, and it is the mechanism the email specimen's ~23x comes from —
so the artifact kind that SHIPS the mechanism was the one kind that could not
report it, and pcrec-bench could not bucket a hybrid row at all. It now writes
the same two lines from the same derivations, ONE derivation and THREE readers
(the loop, the DFA artifact's stamp, the hybrid's stamp).

**The gate is `fit.prefilter` and nothing else, in both directions.** That flag
is also what makes `src/core/compile.c` build `job->dfa`/`job->rdfa` and set
`job->engine` at all, so on a non-hybrid VM artifact the fields these values
read were never written — which is why `pcrec_emit_dfa_scan_stamps` must not be
called there, and why the resulting relation is an IFF rather than a
convention. `docs/spec/match_api.md` §6.3 (a) states it;
`tests/codegen/run_dfa_stamps.sh` asserts it both ways with the emitted
`static <prefix>_prefilter` DEFINITION — matcher text, not either macro — as
the independent third term.

**`RX_VM_PREFILTER` IS STILL VM-ONLY AND IS NOT THE SAME AXIS.** It names a
decision only the VM path takes (run a capture-erased DFA ahead of the program
at all); `RX_DFA_PREFILTER` names what candidate-start filter that scan itself
carries. A hybrid answers both, independently. The comment in `emit_vm.c` that
used to justify `RX_VM_PREFILTER`'s VM-only scope by calling the DFA's own
prefilter "an unrelated always-on optimization, not a selection point D46
governs" was D81's retired rule and is corrected in place.

**(FRANK, D40 ADDENDUM) THE SAME TWO FACTS AS RUNTIME FIELDS.** `struct
rx_info` gains `scan` and `prefilter`, written by `emit_info_def` from
`dfa_scan_name`/`dfa_prefilter_name` — the SAME two functions
`pcrec_emit_dfa_scan_stamps` calls, and their only other callers. One
derivation, two spellings; a codegen check asserts field == macro on every
compiled artifact of both engines, which is a check of THIS EMITTER rather
than of arithmetic precisely because there is no second computation to drift.

The guard is `pcrec_artifact_has_dfa_scan`, which is `src/core/compile.c`'s own
`fit.chosen == ENGM_DFA || fit.prefilter` spelled once — the condition that
MAKES `job->dfa`/`job->engine` exist, so it is not a claim about the artifact
that happens to agree, it is the reason there is anything to read. Both the
hybrid's stamp gate and the runtime mirror ask it. Where it is false the fields
read `NULL` and `"none"`; §6 of the spec states the whole rule, including why
the string `"hybrid"` never appears in `prefilter` (an artifact that would say
it reports its inlined scan's actual mechanism instead, and `scan != NULL` is
how a consumer reads "hybrid").

**ABI 5 -> 6, AND THIS ONE IS A LAYOUT EVENT** — unlike [DD-13]'s and [OPT-1]'s, which were
scaffolding only. Two things move together: the emitted `#define` bytes (the
proven-empty DFA artifacts' scan value; two new lines on every VM hybrid) and
the struct itself (two `const char *` members APPENDED AT THE END, so no
existing offset moves — unlike abi 2's inserted `work_budget` and abi 3's
inserted sizing block). (A) is still byte-identical and (B) is still re-pinned.
**BOTH ARTIFACT KINDS ARE AFFECTED and the abi comment says so**, which is r37
A12's lesson: that finding was that abi 3 -> 4's comment argued the bump from
the DFA side alone while `emit_info_def` is SHARED, leaving a reader unable to
tell that every VM artifact's bytes moved too. This is also the MIRROR IMAGE
of [OPT-1]'s abi 4 -> 5 note ("no DFA artifact's bytes move at this bump"):
that event was VM-only, this one reaches both kinds.

## The VM engine joins ([M4.5b])

`emit_vm.c` is the second emitter. It does NOT fork emit_dfa.c: the artifact
prologue, the fixed ABI types, the string-literal escaper, `rx_info`, the
standalone `main()` and — under the hybrid — the whole DFA engine body are
SHARED through five exported entry points (`pcrec_gen_names`,
`pcrec_emit_prologue`, `pcrec_emit_dfa_engine`, `pcrec_emit_info`,
`pcrec_emit_main`). That is the M2.12 lesson applied before the fork happens
rather than after: M2.7 forked a second copy of the unanchored emitter for `$`
patterns, and the fork is exactly how the prefilter and skip loops silently
went missing from that path for an entire milestone. `pcrec_emit_dfa_engine`
takes a NAME and a STORAGE CLASS, so the VM's prefilter is the same emitter's
output under `static` — one copy, two callers.

The DFA-only path's output is unchanged BYTE FOR BYTE by this refactor, which
is not an aspiration: `tests/codegen/run_vm_identity.sh` is the permanent gate
and the landing evidence included a whole-corpus diff against a compiler built
from the pre-[M4.5b] commit (260/260 capture-free patterns identical).

## Files

- **emit_vm.c** — the backtracking VM as emitted specialized C
  (docs/design/engine_m4.md §2). ONE function per pattern, one label per
  pattern position, every continuation resolved at compile time into a
  fallthrough or a direct `goto`, and exactly one indirect jump (the `goto *`
  at the fail label). §2.7 is why D13's table-vs-computed-goto arbitration
  does not arise: the VM has no per-byte dispatch at all, so its one indirect
  jump is on the cold path by construction.

  **[M6.6.2 wave B+C] `vm_look` — THE LOOKAROUND, and it is `vm_atomic`'s
  shape with two lines added.** Wave A2 landed five inert `A_LOOK` arms, two
  of them deliberately incomplete, behind a LOUD `ctx_fail` in `vm_emit`;
  this wave replaced that arm with `vm_look` and completed the other two in
  the same edit, which is what the `ctx_fail` existed to force.

  - **THE POSITIVE ATOMIC ARM IS `vm_atomic` PLUS A SAVED CURSOR.** Record
    the resume depth AND `scan_position` before any push; emit the body; on
    its first success cut back to the mark and put the cursor back. Those
    two `RX_SET`/restore lines are the entire difference between `(?>ab)c`
    and `(?=ab)c`.
  - **THE NEGATIVE ARM NEEDS NO SNAPSHOT MACHINERY AT ALL**, and that is
    `lookaround_design.md` §3.3's finding rather than a shortcut: `RX_PUSH`
    already records the cursor and `trail_depth`, and the fail label already
    restores the first and rewinds to the second. So "on failure, succeed
    with the cursor and the captures restored" costs ONE PUSH. Its cut is
    not an optimisation — the mark is taken before the push, so the cut
    discards the body-failed continuation too; leaving it live lets a failing
    assertion be resumed later AS IF IT HAD HELD.
  **[DD-14 wave A2] FIVE INERT `A_CALL` ARMS, THREE OF THEM LOUD FAILURES.**
  Nothing produces an `A_CALL` in that wave, so `vm_emit`, `vm_cost` and
  `vm_count_slots` all `ctx_fail` by name rather than guessing — and the three
  are deliberately coupled: `vm_count_slots` must account for EVERY EMITTED
  REGION (each lexical occurrence PLUS one per emitted callee region,
  `subroutines_design.md` §4.4c, whose first version said LEXICAL ONLY and was
  measured WRONG — an out-of-bounds slot write, K27's class, because `X{0}`
  emits and counts nothing and a callee is a real idiom there), `vm_cost` must
  charge the callee's cost plus this site's own `2*|W|` of trail, and both
  need `src/opt/callgraph.c`'s SCC fixpoint, which was wave B+C's. The two
  arms that DID answer in A2 are `vm_nullable` (`true`, the sound bottom that
  keeps the empty-iteration guard; the real answer is the graph's fixpoint
  with cycle bottom `false`) and `vm_rev_caps` (decline, unreachable behind
  `rd_shape`).

  **ALL FIVE ARMS ANSWER NOW** — the graph landed in wave B+C and this
  paragraph is the A2 record, not the current state (re-read at the [DD-14]
  close, 2026-08-25). `vm_cost`'s `A_CALL` reads `v->rgn_cost[idx]` through
  `pcrec_callgraph_index` (emit_vm.c:2229), with the graph-absent branch kept
  and written in the OVER-charging direction because a cost analysis that
  reads an absent table must not under-promise; wave G then made a SPLICE cost
  no frame, the trail charge staying `2*|W|` on either linkage.
  `vm_count_slots`'s `A_CALL` (emit_vm.c:2428) counts the site's own
  `SLOT_SPLICE_SAVE` block from `spl_nw[idx]` and recurses into `u.call.body`
  for a splice only, under a `splice_depth > nregion` tripwire that would
  catch an eligibility rule admitting a cycle; a LINKED site adds nothing here
  because the callee's region is counted once at its own emission. And
  `vm_nullable` now reads the published fixpoint (`!a->u.call.nonnullable`,
  :1167) rather than the sound bottom.

  - **THE NON-ATOMIC `(?*` ARM IS THE ATOMIC SHAPE MINUS THE CUT**, and it
    allocates no mark slot, which is how a reader tells the two atomicities
    apart in the emitted C and in `--emit-ir`.
  - **[WAVE D] THE LOOKBEHIND IS `vm_look_behind`, A PER-BRANCH CHAIN IN
    FRONT OF THE SAME `L_ok`.** Per top-level branch `i` of fixed width
    `k_i`, in WRITTEN order: an ABSOLUTE `scan_position < k_i` guard, a
    next-branch push (the LAST branch pushes nothing), `RX_CHARGE_WORK(k_i)`
    with `k_i` a literal, the SEAM's `<prefix>_back_step`, the
    `<prefix>_BACK_STEP_NONE` check, the body FORWARD through `vm_emit`
    unchanged, and an END-CHECK against `SLOT_LOOK_POS`. Because every branch
    leaves through the same `L_ok` the lookahead arm uses, `vm_look` still has
    a SINGLE EXIT and §3.2.1's restore still sits on it — R33 V-8's
    requirement kept by construction rather than by a second restore.

    Four things about it are not the first thing a reader expects. THE GUARD
    READS THE ABSOLUTE POSITION, never `startpos`: a lookbehind reads subject
    bytes BEFORE the search window and that is the semantics, measured in both
    oracles (S135 clamps it and `startpos.rxt`'s 24 `ms`/`ns` cells go red,
    exactly and only those). IT IS NOT EMITTED AT ALL FOR A ZERO-WIDTH BRANCH,
    because `scan_position < 0` on a `size_t` is what `-Wtype-limits` refuses
    and `(?<=)x` is a legal pattern. THE SENTINEL ARM LEAVES BY `rx_fail`
    rather than jumping to the next branch, because the assignment has already
    clobbered the cursor with `(size_t)-1` and the pushed frame would
    otherwise retry that branch twice — the pop restores both and lands where
    the push meant. AND THE END-CHECK's FAILURE ACTION SPLITS BY POLARITY: a
    cheap `goto rx_fail` on `(?<=`, where a declined branch is the assertion
    failing, and a HARD `RX_R_*` return on `(?<!`, where a declined branch is
    the assertion SUCCEEDING and a wrong width would be a FALSE MATCH (Frank's
    ASK 2 ruling; `RX_R_INTERNAL` is used, below the give-up floor —
    **[DD-14] wave A commit 2, D71 item 1** minted `PCREC_ERR_INTERNAL`
    for exactly this shape, retiring the earlier `RX_R_FRAMES`-by-
    ELIMINATION compromise the site used before the code space had room
    for the honest answer; the site's own header comment carries the one
    line of that history).
  - **THE FOLLOW IS SCOPED ACROSS THE BODY AND NOT BECAUSE OF THE CUT**
    (§3.2.1, R33 C1-1 — the one silent miscompile in §3). `vm_atomic`'s own
    header attributes its identical save-zero-restore to the cut, and THAT
    REASON DOES NOT TRANSFER: here it is the OVERLAP — a lookahead's follow
    starts at the assertion's ENTRY position, so `body_remaining + fmin`
    double-counts the same bytes. Deleting the cut for `(?*` does not delete
    the scoping. Measured on the landed build: `(?:(a+)b)` prunes at 1 and
    `(?:(a+)b)a+b` at 3, while `(?=(a+)b)` and `(?=(a+)b)a+b` BOTH prune at 1.
    The negative form is where an unscoped body is a FALSE MATCH rather than
    a missed one; sabotage row S132 is its detector and its anchor has to
    exceed the two-line idiom, because `vm_atomic` carries the same two lines.

  **TWO NEW SLOT FAMILIES, `SLOT_LOOK_MARK<n>` and `SLOT_LOOK_POS<n>`,
  ALLOCATED PER SHAPE.** They sit at the TOP of the layout (above the pending
  block), so no lookaround-free artifact's slot numbering moves — which is
  what makes the identity gate's FREE bucket a claim rather than a tautology.
  Which of them a shape takes is read off `vm_look_needs_mark` /
  `vm_look_needs_pos`, TWO PREDICATES SHARED BY `vm_count_slots` AND
  `vm_look`, for the reason `vm_marked` and `vm_is_counter` are shared: a
  rule two sites each re-derive is a rule one of them will eventually derive
  differently, and here the failure is `vm_slot_lookmark(v, v->nlookmark++)`
  past `RX_NSLOTS` — an out-of-bounds write in EMITTED code, K27's class. It
  is at most two slots per lookaround and sometimes one: `(?=` takes both,
  `(?!` takes only the mark (the pushed frame restores the cursor), `(?*`
  takes only the cursor — and a negative LOOKBEHIND takes BOTH even though the
  restore is free, because the end-check compares against the entry position.
  `vm_count_slots` also counts the negative form's ONE extra resume point AND
  (wave D) the lookbehind's `nbranch - 1` per-branch retry frames, EXACTLY:
  that walk's under-count is the one that lets an artifact past the
  resume-point cap.

  `vm_cost`'s +1 frame / +2 trail were RE-CHECKED against `vm_look` as landed
  and stand: exact for the shape that needs most, a safe-direction over-charge
  for the others (`RX_CUT` adds no trail entry). Wave D added `+ nbranch` to
  the frame charge and read it off the WIDTH TABLE's companion count rather
  than off `.look.behind` — `nbranch` is 0 for a lookahead, so that charge is
  unchanged to the line, and the exact lookbehind figure is `m - 1`, so `+ m`
  over-charges by one in the direction this analysis is documented to err in.
  `vm_nullable` answers TRUE
  (§2.6 — the arm that stops a quantified lookaround burning its step budget)
  and `vm_rev_caps` declines. Apart from `vm_look` itself, NO arm in this file
  reads `u.look.behind`/`.neg`/`.atomic`: §3.1(a) settles one kind rather than
  four on the strength of those flags having exactly ONE reader, so an arm
  here that consulted one would be the second reader that argument denies
  exists. The two slot predicates are `vm_look`'s own helpers and read them
  on its behalf, which is why they live beside the slot accessors rather than
  in the walkers.

  **`pcrec_has_lookaround` IS CALLED AND ITS ANSWER IS DISCARDED**, beside
  `v.mrl_win`, and the site says so at length. Wave E adds the conjunct; wave
  A2 places only the CALL and its POSITION (post-discharge, on the same
  `root` as `pcrec_has_atomic`), because with no producer the predicate cannot
  be anything but false and adding the conjunct now would pre-satisfy sabotage
  row S-LA12. Do not read the call as live.

  The pieces worth knowing before editing it:

  - **`slot_values`, one flat array** (§2.4) holding capture pairs, empty-iteration
    guards and cursor low-water marks. One restore loop, one overflow bound,
    and a future slot class costs a layout row rather than a new save/restore
    path. `vm_count_slots` must mirror the emitter's own rung decisions
    EXACTLY — including the replication a bounded repeat performs — or two
    live loops share one slot.
  - **The trail** is exact old-value undo, never a clear (§3.2). The naive
    version is wrong in both directions and the three cases that pin it are in
    that section; sabotage S36 neuters it.
  - **The cursor ladder** (§2.5, `vm_det_seq`). The deterministic
    fixed-stride rung is NOT an optimization that could be deferred: without
    it an 8 MB `a*` would need 8 M resume frames in an allocation-free
    matcher. D44.1 extends it to capture-bearing bodies by deriving group
    spans from the cursor at loop exit. The rungs NOT built (disjoint-follow
    possessification, the reverse-deterministic backwards walk, the
    boundary-record rung) are named in `vm_det_seq`'s comment so they are not
    mistaken for oversights; §6.4 schedules the first at M4.6.
  - **The empty-iteration rule** (§3.3) applies IFF `rmax == -1`, and takes
    the loop's EXIT continuation rather than failing the path — the empty
    iteration's capture writes STAND. Both readings are available from the
    mechanism and only one is right; the wrong one is sabotage S38 and was
    this emitter's own first-draft bug.
  - **The two capacities** (§2.5, §4.5) are computed exactly where the
    pattern's dynamic depth is statically bounded and defaulted otherwise,
    with an honest `subject_ceiling` stamped for the residual class (D44.1).
    The defaults are BRING-UP PLACEHOLDERS — D12 rules budgets come from
    measured medians and [M4.6] takes the measurement.
  - **[M4.5c fix] the REPLICATION cap and the pre-pass's recursion.** A
    bounded repeat replicates its body (§3.3), so `{0,N}` over a
    choice-bearing body emits N copies — `((a)|b){0,4000}c` is sixteen
    characters and 3.5 MB, and gcc is superlinear in the resulting
    address-taken-label fan-out (K19). `PCREC_MAX_VM_REPEAT_COPIES` is checked
    in the PRE-PASS, before a byte is emitted; limits.h carries the
    measurement and the reason the cap is on replication rather than on size.
    Separately, the pre-pass functions (`vm_nullable`, `vm_count_slots`,
    `vm_cost`) walk `A_CAT`/`A_ALT` spines ITERATIVELY. They did not, and a
    20,000-character pattern SEGFAULTED pcrec (K20) — DD-10/D10/R1 R-2's class
    for the third time. Any new walk over those shapes needs the same
    treatment; `vm_nullable` carries the comment that says so.

    **[K22] the third bound: the REPLICATION PRODUCT, checked DURING the
    pre-pass rather than after it.** The copies cap above bounds ONE
    quantifier's factor and structurally cannot see nesting, where factors
    MULTIPLY: a depth-40 tower of `{0,2}` has a maximum factor of 2 and
    replicates its innermost body 2^40 times. `PCREC_MAX_VM_NODES` would catch
    that, and did — but it is charged during EMISSION, while `vm_count_slots`
    walks the same copy tree BEFORE emission, so the walk itself was the
    Θ(2^d) work nobody bounded and the compiler hung with no diagnostic on a
    365-character pattern. `vm_count_slots` now carries a `repl` argument (the
    product of the enclosing frames-rung factors, 1 at the root) and refuses
    above `PCREC_MAX_VM_REPLICATION_PRODUCT` before it recurses. The bound IS
    `PCREC_MAX_VM_NODES`'s value, and that identity is the check's whole
    safety argument rather than a coincidence: every replicated copy costs at
    least one `vm_charge`, so the product is a lower bound on the node count
    and the guard can only move a refusal earlier, never widen one. The REAL
    fix is [ENG-BREP]'s counter-K rung; this is the interim guard that makes
    the failure honest. Measurements: `docs/design/rungselect_impl/`.
  - **[M4.5c] the LISTING and the TRACE (DD-8, §10).** §10's one constraint —
    "the dump must be derived from the same structure the emitter walks, never
    a parallel description" — is why the listing is an EVENT STREAM (`VEvent`)
    appended by the emitter's own primitives rather than a second walk over the
    AST. `vm_lbl`, `vm_push_at` and `vm_set` each write C *and* record what
    they wrote; every listing SECTION is then a view over that one stream, so
    the sections cannot disagree with each other either. If you add a way to
    emit a label, a push or a slot write, add it THROUGH those primitives —
    the accept label was emitted by a direct `sb_printf` in the first draft and
    `tests/codegen/run_ir_listing.sh` caught it on its first run (sabotage
    S41 restores it). The `role` strings are decoration: they say WHY a choice
    point exists, never that one does, and the check pins the derivable half.

    `--trace` (`PCREC_TRACE`) emits the same program with instrumented
    macros. The traced and untraced forms keep the SAME order of operations on
    purpose — a debug build that took a different path would be a tool that
    lies — and the untraced artifact's bytes are unchanged, which
    `run_ir_listing.sh` and `run_vm_identity.sh` both depend on.

  - **[M4.5e] the D46 RUNG STAMP.** §2.5's rungs (the deterministic
    span-loop cursor, the bounded-frames rung, the unbounded-frames rung)
    are selected silently PER QUANTIFIER BODY — `vm_cursor_fits` is
    consulted once per `A_REP` node, at this file's own three call sites
    (`vm_cost_rep`, `vm_count_slots`, `vm_rep`'s real emission), so a
    pattern with two quantified bodies can and does mix rungs — until this
    close obligation (D46, docs/dev/decisions.md); now the selection is
    OBSERVABLE. **A per-artifact SCALAR summary was the first draft and was
    corrected mid-lane** (Frank's design question) precisely because it
    lies on that mixed case: a single `"cursor"`/`"frames"`/`"mixed"` value
    cannot say WHICH quantifier took which rung, and a caller pinning
    selection for one quantified body has no way to address it. The fix:
    `v->rungs`, a BITMASK (`VmRungKind`: `VM_RUNG_CURSOR`/
    `_FRAMES_BOUNDED`/`_FRAMES_UNBOUNDED`), OR'd in by `vm_rung_mark()` — a
    sixth listing primitive alongside `vm_lbl`/`vm_push_at`/`vm_set`, called
    once per `A_REP` at the same point `vm_cursor_rep` / `vm_rep`'s frames
    fallthrough already knows the rung, appending a `VE_RUNG` event AND
    setting the mask bit in one call so the two views can never drift
    apart. Emitted as the artifact's own
    OR'd `#define <PREFIX>_VM_RUNGS 0x...u` next to `RX_ENGINE`/
    `RX_ENGINE_WHY` (same VM-artifacts-only placement and §5.4
    byte-identity rationale) — **the three (now five, D46's later rungs)
    named bit constants it is built from moved to the shared, unprefixed
    `PCREC_RX_ABI_H` block at [ABI-NS] (D60, 2026-08-18): `PCREC_VM_RUNG_
    CURSOR`/`_FRAMES_BOUNDED`/`_FRAMES_UNBOUNDED`/`_REVDET`/`_COUNTER`,
    emitted once, unconditionally, on every artifact — see
    `emit_rx_abi_types` above** — and as a NEW `RUNGS` listing section in
    `--emit-ir` (one row per quantifier, `at L<label> <kind> <role>`) plus
    a header `; rungs ...` summary line — all three read off the same
    `v->rungs`/`VE_RUNG` data the real walk built, never re-derived.
    `rx_info` gains no member for this: the struct's layout is the frozen
    M4 ABI (match_api_m4.md §5, D44.5's "layout below is FINAL"), so a
    field would be an abi-version-bump event this close did not take on —
    flagged for the manager rather than done here. Rung FORCING (D46's
    controllability half) has no producer yet; only the observability half
    landed at [M4.5e]. Tests: `tests/vm/run_vm_tests.sh` §5, including a
    deliberately three-way-mixed pattern (`a*(a|b){0,3}c((x)|y)+z`) that is
    exactly the case the corrected, scalar-first design would have gotten
    wrong.

  - **[ENG-BREP] POSSESSIFICATION, the ladder's first rung** (D47.1;
    docs/design/eng_brep_design.md §2). `src/opt/possessify.c` marks an
    `A_REP` whose loop no retreat can ever profitably re-enter, and this file
    is what that mark BUYS. Two shapes, because the two rungs owe different
    machinery:

    - the CURSOR rung possessified emits the scan and nothing else: no resume
      frame, no low-water slot, no trail entry. The low-water slot exists so
      the RETREAT can tell "still above rmin" from "exhausted"; with no
      retreat there is no reader, and `pos` is still the loop's entry position
      at every point (the scan writes only `<p>_cur`), so the possessive path
      reads `pos` and allocates nothing.
    - the FRAMES rung possessified keeps ONE frame for the whole loop instead
      of one per optional copy, via the new `RX_CUT` primitive: `vm_cut`
      truncates the resume stack back to a depth recorded at loop entry, at
      each COPY BOUNDARY. Not inside a copy — a one-unambiguous body still
      needs its own frames to FIND its match (`(?:a|bc)` on "bc" tries `a`
      first and backtracks); one-unambiguity says at most one branch can
      SUCCEED, not that the emitter guesses right. The cut deliberately does
      NOT rewind the trail: the frames are dead, the capture writes they would
      have rewound are not, because a failure OUTSIDE the loop still has to
      restore the loop's groups.

    Deleting the pushes instead of restructuring is NOT available and this is
    the thing to understand before editing either shape: in this VM a frame at
    an optional copy serves TWO purposes — resume when the CONTINUATION fails
    (the retreat possessification kills) and resume when the BODY fails (this
    copy cannot run, so leave the loop), which stays completely alive.

    The PREFERENCE disappears under a positive verdict, and that is the
    analysis's conclusion rather than a shortcut: on the exact-count arm there
    is one exit, and on the disjointness arm a LAZY loop is FORCED to the same
    maximal exit a greedy one tops out at (at any non-maximal exit the body
    could iterate again, so that byte is in FIRST(X), so by disjointness the
    follow cannot begin there — and the lazy conjunct rules out the match
    simply ENDING there). One emitted shape is correct for both.

    `vm_cost_rep` and `vm_count_slots` carry the matching branches. They must:
    a slot count that under-counts makes two live loops share one slot, and a
    frame requirement that under-counts is a silent cap. The payoff is
    §7's `rx_info` prediction, and it is a GATE in
    tests/possessify/run_possessify_tests.sh rather than a promise —
    `(x)(?:a|bc)+d` stamps a 512-byte `subject_ceiling` today and stamps 0
    ("no limit") truthfully once the loop owes no frames.

    Observed through `<PREFIX>_VM_STRATS`, a bitmask beside `<PREFIX>_VM_RUNGS`
    and for the same reason (the strategy is per-A_REP; a scalar lies on a
    mixed artifact), plus a STRATEGIES section in `--emit-ir`. (Its own two
    named bits, `PCREC_VM_STRAT_POSSESSIVE`/`_BACKTRACKING`, moved to the
    shared `PCREC_RX_ABI_H` block at [ABI-NS], D60 — same move as the rung
    bits above.) Both are set by
    the SAME `vm_rung_mark()` call the emitter already makes at the point it
    knows what it is about to emit, so the stamp and the machinery cannot
    disagree. `-fno-possessify` denies the rewrite, and D47.3's do-or-die half
    is asserted against the STAMP rather than against the flag having been
    passed.

  - **[ENG-BREP] THE REVERSE-DETERMINISTIC RUNG, the ladder's second rung**
    (engine_m4.md §2.5; design sketch
    `docs/design/rungselect_impl/rungselect_design.md`). It slots between the
    cursor and the frames, and it is what makes a bounded repeat's emitted size
    independent of its COUNT: `((a)|b){0,4000}c` was refused by the replication
    cap and now compiles to 292 lines. `src/opt/revdet.c` selects it and leaves
    the body's reversed AST on `Ast.u.rep.revbody`; `vm_revdet_rep` emits it.

    Four things to understand before editing it:

    - **The forward scan CUTS at every iteration boundary.** That is what makes
      the resume stack O(1) in the iteration count instead of O(n), and it is
      licensed by forward unique-iteration: once the body has matched `[p,q)`
      there is no other way to match an iteration there. The cut is at a
      BOUNDARY and never inside a body — `vm_poss_chain`'s own recorded lesson,
      that a one-unambiguous body still needs its own frames to FIND its match.
    - **Capture writes are SUPPRESSED in the forward body** (`v->nocap`, read by
      `vm_emit`'s A_CAP arm, `vm_cursor_rep` and `vm_cost`, so the emitted code
      and the number the capacities are sized from cannot disagree). They are
      the trail growth the rung exists to remove, and they are redundant.
    - **The BACKWARD WALK does two jobs with one emission**: it finds the
      previous iteration boundary for a retreat, and it recovers §3.4's
      last-iteration captures. It has NO CHOICE POINTS — reverse
      one-unambiguity lets `vm_rev_emit` dispatch an alternation on the next
      byte — so it pushes nothing, and every failure edge goes to the walk's
      end rather than to `rx_fail`. It runs on its own cursor local and never
      touches `pos`, because it is a derivation and not a move.
    - **The captures go to LOCALS and are published AFTER the resume frame is
      pushed.** Both halves are load-bearing: publishing after the push puts the
      frame's trail mark BELOW them so a retreat rewinds the previous commit's
      values instead of accumulating them (the cursor rung's own ordering rule),
      and walking into locals costs trail entries per GROUP rather than per
      ITERATION. A group the walk never witnesses is never published, so its
      previous value stands — which is how §3.4's ZERO-ITERATION clause falls
      out as a special case rather than as an extra branch.

    Three slots per loop (`vm_slot_rev`: entry, low-water, ceiling), a uniform
    three whatever the preference, because the count has to agree across
    `vm_count_slots`, `vm_cost_rep` and the emitter and a per-preference rule
    would put that agreement in three places. All three are written ONCE per
    loop ENTRY. `vm_cost_rep`'s arm sets `pf = 0` — the headline: frames stop
    depending on the iteration count, so an artifact whose only growing
    quantifier is on this rung declares no `subject_ceiling` at all.

    The emitted working locals are per-loop SCALARS rather than an array of
    structs, and that is a constraint rather than a preference: generated code
    is built `-Wall -Wextra -Werror`, and gcc cannot see through a
    computed-goto flow well enough to prove an array element is written before
    it is read (`-Wmaybe-uninitialized`, measured on four corpus patterns).

    Observed through `<PREFIX>_VM_RUNGS`'s fourth bit
    (`<PREFIX>_VM_RUNG_REVDET`, `0x8`) and `--emit-ir`'s RUNGS section, both set
    by the same `vm_rung_mark()` call every other rung goes through.
    `-fno-revdet` denies it, and D47.3's do-or-die is asserted against the STAMP
    rather than against the flag having been passed. Tests: tests/rungselect/.

  - **[M4.6d] MINIMUM-REMAINING-LENGTH PRUNING** (K23's fix of record, D51
    ruling 1; design `docs/design/k23_impl/k23_design.md`, build outcome in
    that note's §14). `src/opt/mrl.c` supplies `pcrec_minw`; this file
    supplies everything else, and the everything else is where the soundness
    lives.

    **The threading.** `Vm.fmin` is the follow-min at the current emission
    point, mutated at ONE place (`vm_emit_f`) and inherited everywhere else,
    so a site that does not change what follows is correct by saying nothing.
    A_CAT computes its spine's follow-mins as a SUFFIX SUM in one backward
    pass; a bounded repeat's mandatory copy `i` is emitted with
    `(rmin - i - 1) * minw(body) + F`, which §4.3 calls "the whole of K23's
    fix". Everything under a node inherits, which is why `A_CAP` and
    `vm_alt`'s branches have no MRL code at all.

    **Two forms, and which applies is fixed by the rung** — the rule stated
    once at the top of the MRL block and worth knowing before touching any
    site: rounding is owed wherever the bound ASSIGNS a cursor value, and not
    owed wherever it merely TESTS one.
      - the GREEDY CURSOR rung ASSIGNS, so its clamp is
        `pos + W*floor((CEIL - minrest - pos)/W)` and is FOLDED INTO THE SCAN'S
        OWN BOUND. Two different wins from one expression: the retreat chain
        never walks the doomed suffix (10,621,636 steps -> 1), and the scan
        never READS it (the forward-work proxy drops to one pass). R26 E1
        measured the unrounded form UNSOUND at stride > 1 — it substitutes a
        position the loop can never occupy for one it can, which satisfies
        "removes only doomed candidates" and still deletes the answer.
      - a LAZY cursor TESTS (it walks up from the minimum and is on the
        lattice by construction), the FRAMES rung TESTS at each iteration
        entry, and the possessive cursor arm TESTS after its scan. **The
        possessive arm is a test rather than a clamp for a reason that is not
        "which shape the rung wants"**: clamping there would move a
        possessified loop to a smaller position and run the continuation from
        it, i.e. re-introduce the retreat possessification proved dead. Under
        a correct verdict that is harmless; under a subtly wrong one it
        manufactures a match. MRL's soundness must not come to depend on
        possessify's, so it does not.
      - the REVERSE-DETERMINISTIC rung is prediction 6's site, and the answer
        is the opposite of the one predicted: its boundaries are NOT an
        arithmetic lattice, and it therefore needs no rounding at all. Its
        FORWARD SCAN *is* the walk onto the boundary set — every value `pos`
        takes during the scan is a boundary the body matched — so the bound is
        applied by STOPPING the scan one boundary early, and the E1 class of
        bug is inexpressible there because no code path writes a boundary the
        rung did not reach by matching. The stop goes to `shortl` and not to
        `fulll`, which is not cosmetic: `fulll` is reached only where the
        iteration count is known to have met rmin.
      - the COUNTER rung is the one place the bound is NOT a compile-time
        constant. One body copy serves every trip, so the compile-time view of
        "mandatory iterations still owed" tops out at `K + residue`; the truth
        is `count - slot_values[ctr] - j`, read from the TRAILED counter slot.
        `Vm.fdyn` carries that as a C expression alongside `fmin`. **Leaving
        it out leaves K23 alive**, measured on `(a{1,3}){65}` (9 bytes of
        visible follow against a real 65) by the D27-blinded test author, not
        by anything derived from this file.

    **The CEILING is a PARAMETER of `<prefix>_match_impl`, not a member of
    `<prefix>_work`** as the design note's own sketch had it. D51 ruling 2 (a)
    requires every entry that runs no prefilter to default it to the subject
    end; the way to discharge an obligation of the form "every caller must
    remember to set X" is to make forgetting a compile error. Its value is
    `min(n, win[0][1])` — the prefilter's match-end window, ruling 2 — on the
    search entry, and `ctx->len` on the two match-here entries. **The retry
    loop RECOMPUTES it** (ruling 2 (b)): a structural argument that the retry
    cannot fire at all is available and is written at the site, but it rests
    on span-equality between the VM and the prefilter, which R21 split to
    BELIEVED-WITH-GATE after two live priority miscompiles — and a stale
    window is too SMALL, the unsound direction.

    Observed through `<PREFIX>_VM_PRUNES` (a bitmask beside `_VM_RUNGS` and
    `_VM_STRATS`, per-quantifier for the same reason: `(a{2,4}){3,9}b` clamps
    at every replica and `(a{2,4}){3,9}` at none — its two named bits,
    `PCREC_VM_PRUNE_CLAMPED`/`_UNCLAMPED`, moved to the shared
    `PCREC_RX_ABI_H` block at [ABI-NS], D60, same move as the rung/strategy
    bits above) plus
    `<PREFIX>_VM_PRUNE_CEILING`, which names the ACTIVE ceiling form —
    ruling 2 (c), so `--engine=vm`'s weaker subject-end form is disclosed
    rather than discovered. The ceiling stamps `"none"` when the artifact
    carries no bound, and stamps the same `"none"` under
    `-fno-length-prune`: the denial must leave NO TRACE or the byte-identity
    property that makes the denied build a ground truth dies at the stamp,
    which is emit_dfa.c's strategy-denial rule one stamp over. Tests:
    tests/mrl/.

  - **[M4.6f] THE PREFILTER STAMP + FORCE PAIR** (D46 close-out for
    `fit.prefilter`, engine_m4.md §6.1/§4.7; src/opt/select_engine.c does
    the selecting, this file does the reporting). `<PREFIX>_VM_PREFILTER`
    is stamped `"hybrid"`/`"none"`, in the SAME PLACEMENT as
    `RX_ENGINE`/`RX_ENGINE_WHY` and read straight off `job->fit.prefilter`
    — the SAME value `prefn` (the private forward+reverse DFA pair, "the
    prefilter (S6.1, S4.7)" below) is built from, never a second
    computation of it. A SCALAR string, unlike `_VM_RUNGS`/`_VM_STRATS`/
    `_VM_PRUNES`: those are bitmasks because the rung/strategy/clamp is
    selected per `A_REP` and a scalar would lie on a mixed artifact
    ([M4.5e]'s own corrected design note); `fit.prefilter` is ONE verdict
    for the whole artifact, so there is no per-quantifier axis to mix and
    a scalar is the honest shape, the same reason `RX_VM_PRUNE_CEILING`
    (above) is a string rather than a mask. `-fprefilter`/`-fno-prefilter`
    (`PCREC_FORCE_PREFILTER`/`PCREC_NO_PREFILTER`) are the controllability
    half, applied in select_engine.c (its own CLAUDE.md carries the
    do-or-die detail) — a FORCE pair rather than D47.3's DENY-only shape,
    because there is no per-quantifier addressing problem to avoid here.
    `--emit-ir`'s `; prefilter` listing line (`vm_render_listing`) also
    names WHICH off-route fired (`-fno-prefilter` vs. the `--engine=vm`
    side effect), since D46's observability extends to the debug listing
    too. Tests: tests/prefilter/.

    **[DD-14 wave E] A FOURTH OFF-ROUTE, AND IT IS TESTED BEFORE THE TWO
    FLAG ROUTES** for the reason `[M6.5.2]`'s backreference route is: no
    flag explains it, so naming one is a diagnostic lie. A CALL-BEARING
    pattern has no prefilter under ANY invocation — erasing a call is not a
    loose superset but a DIFFERENT language (`subroutines_design.md` §8.2:
    `a(?1)b` with group 1 = `x` matches `"axb"`, and the erased `ab` does
    not) — and `-fprefilter` REFUSES rather than overriding. MEASURED on
    this branch before the arm existed: every call-bearing pattern compiled
    under `auto` listed `NO (--engine=vm)`, naming a flag the caller had not
    passed. `VmStamp.has_call` is read from `pcrec_has_call(root)` and NOT
    from `enc_mask` like its `has_bref` neighbour, because a call leaves no
    residual encoding entry — the AST predicate is the one source
    `select_engine.c` forces the prefilter off from, so the listing reports
    the same fact rather than a second derivation of it.
    Tests: tests/recursion/prefilter.rxt, sabotage row S165.

  - **[DD-14.EMPTY] THE ROOT MINIMUM-WIDTH CHECK AND ITS STAMP**
    (`pcrec_emit_vm`; sabotage row S169). When `pcrec_minw(root)` is at the
    analysis ceiling (`PCREC_MINW_MAX`, 2^40) the emitted `<prefix>_search`
    gains ONE line before it touches a frame: `if ((unsigned long
    long)(subject_length - search_from) < <PREFIX>_VM_ROOT_MINW) return 0;`,
    and the artifact stamps `<PREFIX>_VM_ROOT_MINW` (a NUMBER, because the
    guard READS it — a stamp the artifact only talks about can drift from
    what the artifact does) under an SR-8-shaped comment saying "root minw
    unbounded: matches nothing". `--emit-ir` carries the same fact as a
    `; root minw` line off the same value.

    **THE READ ORDER IS THE WHOLE MECHANISM.** `pcrec_minw` reads a call's
    contribution off `u.call.minw`, the fixpoint `pcrec_callgraph_build`
    caches on the node — and that pass runs AFTER `pcrec_select_engine` and
    BEFORE this emitter (`src/core/compile.c`). Asked at engine selection
    the three empty-language cells of `tests/recursion/leftrec.rxt` answer
    1, 1 and 0 (the arena's zero: sound, since this analysis's safe
    direction is under-estimating, but useless — it never reaches the
    ceiling, so a root check there can never fire). Asked here they answer
    `PCREC_MINW_MAX`. The `[DD-14.EMPTY]` plan row named engine selection as
    the site and was wrong about it.

    **IT IS A WIDTH COMPARISON AND NOT AN UNCONDITIONAL `return 0`**, and
    the difference is a correctness one. The ceiling is reached by TWO
    routes — the call fixpoint's genuine infinity, and `mrl_sat_add`/
    `mrl_sat_mul` SATURATION on a pattern whose true minimum is merely
    enormous — and the value cannot distinguish them. The comparison is
    exactly right on both and needs no distinction; an unconditional return
    would be a miscompile on the second for a subject of 2^40 bytes, which
    `size_t` can represent.

    **IT IS EMITTED CONDITIONALLY, AND THE CONDITION IS A BENEFIT GATE
    RATHER THAN A SEMANTIC ONE.** Emitting it for every artifact is
    strictly more general and would move bytes on every pattern in the
    tree, which the four standing byte-identity gates forbid. MEASURED: of
    the 2,568 distinct `pattern` lines under `tests/` at the time it landed,
    exactly four reach the ceiling and all four are call-bearing — so no
    call-free artifact gains a byte, and `emit_dfa.c` needs no arm at all
    (`A_CALL` is structurally VM_ONLY, so a pattern that can reach the
    ceiling can only reach this emitter).

- **emit_dfa.c** — both engine emitters (emit_unanchored, emit_attempt), the file-scope/per-engine naming helpers, shared table/label helpers, header/comment/prologue emission. **[STD1] phase A (D37, 2026-08-13)** added the ARTIFACT STAMP: `emit_feature_comment` (a `/* Feature set: NAME (modules: LIST) */` line, in both the .c and, when paired, the .h — mirroring the existing pattern-comment convention) and `emit_feature_macros` (`#define PCREC_FEATURE_SET`/`PCREC_FEATURE_MODULES`, .c ONLY, so a .c that `#include`s its own .h never sees them twice). Both read `pcrec_enabled_set_label`/`pcrec_enabled_set_modules` (src/parse/enabled.c) — the one source for "what does the currently-installed mask mean as names" — rather than recomputing anything here. Emitted unconditionally, including for a bare invocation (which stamps `"none"`, the phase-A default): the point of D37 is that NO artifact is ambiguous about what it was built with, and case10's old `--features all` byte-identity pin (tests/cli/) was updated to compare past these 4 stamp lines rather than the whole file, since the stamp differing IS the fix, not a regression, for a base-tier pattern that never engages the gate at all. **[M4.4] (docs/design/match_api_m4.md, the MATCH-API FREEZE, 2026-08-14)** landed the announced API break mechanically: `emit_span_typedef` is DELETED (`<prefix>_span` retires, D44.2) in favor of `<prefix>_search`'s FINAL `ptrdiff_t (*caps)[2]` fourth-parameter shape; `emit_rx_abi_types` emits the six fixed ABI types once per file under the prefix-independent guard above; `<prefix>_match` and `<prefix>_match_caps` (new, unconditional) are thin wrappers that call through the existing `<prefix>_search` rather than a second, genuinely-anchored automaton — correct by construction, since `<prefix>_search`'s own leftmost-first priority makes "the reported start equals the requested position" exactly equivalent to anchored matching, not an approximation of it; `<prefix>_info` (new, one `.rodata` `struct rx_info` instance per artifact — see the deviation note below) reflects the compiled `pcrec_options.flags`, encoding, pattern text (via a new genuine C-string-literal escaper, `emit_c_string_literal` — NOT `emit_pattern_comment`, which is a comment escaper only, unsafe for a string literal), group counts, and engine choice. **[DEVIATION, REPORTED]**: `struct rx_info` is emitted WITHOUT a bare `typedef` alias, unlike the other five ABI types — `<prefix>_info` under the DEFAULT prefix `"rx"` is the literal identifier `rx_info`, and a bare typedef of that name cannot coexist with a variable of that same name in one C scope (verified directly against gcc: "redeclared as different kind of symbol"). Struct TAGS live in a separate C namespace from ordinary identifiers, so `struct rx_info { ... };` (a tag, no typedef) and a variable named `rx_info` coexist with no conflict; every reference to the type (`emit_info_decl`, `emit_info_def`) spells it `struct rx_info`, never the bare form match_api_m4.md §5's literal C snippet shows. This is the ONE of the six ABI types where the collision is reachable, because "info" is the only per-artifact entry-point suffix that is also, verbatim, a whole fixed ABI type name — flagged for the manager/panel, not silently resolved.

  **[ENG-BREP] the STRATEGY-DENIAL mask.** `emit_info_def` masks
  `PCREC_NO_POSSESSIFY` (and every later member of D47.3's deny family) out of
  the emitted `rx_info.flags`. `rx_info.flags` is D43's record of what the
  artifact DOES, and a strategy denial changes that by exactly nothing — which
  is the claim the flag exists to test. Stamping it would make two
  identically-behaving artifacts differ in their reflection surface over a knob
  with no observable effect, and would destroy the byte-identity gate that is
  possessification's own safety argument: a gate that has to FILTER a
  known-differing line is the check-design failure this project has recorded
  twice. What the ladder's choices ARE recorded in is `<PREFIX>_VM_STRATS`,
  which reports what the emitter did rather than what it was asked.
  **[M4.6f]** `PCREC_NO_PREFILTER`/`PCREC_FORCE_PREFILTER` join the same mask
  for the identical reason, even though the axis is a FORCE pair rather than
  deny-only: the rule is about OBSERVABLE EFFECT, not about spelling, and
  forcing the hybrid prefilter changes no answer. Its own D46 record is
  `<PREFIX>_VM_PREFILTER`, above.

  Additional [M4.4] entry points in emit_dfa.c: `emit_c_string_literal` (the
  A-11 string-literal escaper — `"`, `\`, control bytes; non-printables use a
  fixed 3-digit OCTAL `\NNN` escape, never `\xNN`, because a hex escape has
  no digit-count limit and would glue onto a following literal hex digit,
  where an always-3-digit octal escape self-terminates), `prefix_upper` (the
  OS-0 uppercased-prefix spelling shared by the NCAPS/UNSET/ERR macros and
  `rx_info`'s `RX_NCAPS` reference), `derived_name` (prefix+suffix identifier
  builder, arena-owned, generalizing the old `engine_entry_name`), and
  `emit_match_def`/`emit_match_caps_def`/`emit_info_def` (the three new
  entries' definitions).

  **[M6.3] `emit_info_def` gains the named-groups reflection table.**
  When `cx->n_named_groups > 0` it first emits a file-scope `static const
  rx_group_entry <prefix>_group_names[]` (named via `derived_name`, so two
  differently-prefixed artifacts sharing a TU cannot collide on it),
  SORTED by name (`strcmp`, `ng_cmp_name` — matches PCRE2's own measured
  `PCRE2_INFO_NAMETABLE` order, docs/dev/decisions.md D59) via one `qsort`
  over an arena-allocated array of `NamedGroup*` pointers built from
  `cx->named_groups`'s declaration-order linked list (internal.h). Each
  entry's `slot` is the group's capture-slot number when `cx->want_caps`
  (a named group's presence already forces this artifact onto the VM
  through the pre-existing `forces_captures` rule, so `want_caps` alone is
  sufficient — no `st->engine` check needed) and `-1` otherwise — verified
  both directions against a real `--no-captures` build (DFA-selected,
  every entry stamps `-1`). `rx_info.nnames`/`.groups` then read straight
  off `cx->n_named_groups` and the array's own derived name (or stay
  `0`/`NULL`, unchanged, for the overwhelming majority of patterns that
  declare no name).


## [M6.4.2] the ATOMIC GROUP's lowering, and the two predicates it is built on

`(?>X)` is a CUT: at the moment the body first succeeds, every choice point the
body created is discarded. `vm_cut` — built for [ENG-BREP]'s possessification —
is REUSED UNCHANGED, and that is the design's single most load-bearing claim:
the no-trail-rewind invariant it rests on is INDEPENDENT of the §2.2 proof that
licenses today's cuts. `vm_cut`'s header gives two reasons for the rule and
only ONE is possessify's — discarding the FRAMES is what §2.2 licenses (an
atomic group has no such licence, and discards frames that are NOT dead; that
is precisely the semantics), while leaving the TRAIL alone rests on nothing but
frame arithmetic.

**`vm_atomic` is the general shape** — mark BEFORE any push, body, one cut at
the body's first success — and **`vm_lifts` / `vm_cuts` are the two predicates
everything else reads.** The LIFT routes the cut into an `A_REP` child's own
possessive rung, which cuts PER ITERATION where the general shape cuts once:
without it `(?>a*)` exhausts `RX_RESUME_FRAMES` where `a*+`, a spelling PCRE2
calls identical, costs one frame.

**THE FOLLOW DOES NOT CROSS A CUT** ([M6.4.4], and the fix for a TIER-1
MISCOMPILE THAT SHIPPED — `(?:aa|a)++ab` answered (0,4) on "aaab" against both
oracles' NO MATCH, from `69f3b93` until the fix). `vm_atomic` sets
`v->fmin`/`v->fdyn` to 0/NULL for the whole body and restores them after the
cut, on BOTH routes out — the general shape and the lift.

It is a SEMANTIC boundary, not a lost optimisation. `(?>X)` matches X's OWN
FIRST SUCCESS, and which success that is must be decided without consulting
what follows the group, because the cut makes the choice final. `v->fmin` is
exactly such a consultation: the MRL machinery turns it into a loop bound, and
every possessive rung ends its loop at the first position where "one more
iteration PLUS THE FOLLOW" does not fit. For an UNCUT loop that shortcut is
answer-preserving and `vm_opt_chain`'s own comment proves it — the body branch
has no accepting leaf there, so the skip is the only survivor, AND THE SKIP IS
STILL AVAILABLE TO RETREAT TO. Under a cut it is not.

**Scoped at the BOUNDARY rather than per rung, and the shapes that forced
that:** `(?>a(?:aa|a)+)ab` and `(?>(?:aa|a)+a)ab` put the loop one level
INSIDE the group, where `under_atomic` is FALSE and the cut comes from
possessify's own §2.2 verdict — a verdict computed against the body's EMPTY
follow while the emitter was still carrying `ab`. Two passes disagreeing about
WHICH FOLLOW THEY MEAN is the whole defect; zeroing at the boundary makes them
agree by construction for every shape. The body's INTERNAL follows survive
untouched, because the concatenation arm rebuilds its suffix sums from
`v->fmin`.

This is RULE H3 one level down, and the same sentence: the prefilter answers
for the UNCUT language, so its span end is not a bound on a cut match's end;
`v->fmin` answers for the follow, so it is not a bound on a cut body's search.
Sabotage row S101; regression family `cut2` in
tests/atomic_groups/run_atomic_diff.sh; witnesses in possessive.rxt section 10.

**THE LIFT IS NOT FREE, and the same claim was refuted TWICE the same way.**
Each possessive rung's shape is licensed by a §2.2 CONJUNCT that a
USER-WRITTEN possessive deletes: `vm_poss_star` emits no empty-iteration guard
(licensed by §2.2 refusing NULLABLE bodies — routed there, the matcher pushes
and cuts at zero consumption forever), and all four rungs are GREEDY-ONLY BY
SIGNATURE (licensed by :2053-2062's preference collapse — 7 of 8 lift-eligible
LAZY cells miscompile). A third was found by the systematic read: the RUNG'S
OWN GATE, `vm_rev_canmove`'s exact-count clause. So the lift's scope is greedy,
non-nullable `A_REP` bodies, CHECKED at each rung's entry rather than assumed —
and the licence those checks test is "greedy **OR** §2.2-proved", not "greedy",
because a lazy quantifier with a POSITIVE verdict is legitimately possessified
today on all six paths and the collapse is sound there BECAUSE the verdict
holds. Getting that wrong refuses three shipped shapes.

**`under_atomic` IS THREADED, NEVER STORED** (D67's corollary). `struct Ast`
has no parent pointer and the four pre-passes are independent descents, so a
node cannot ask whether it is under an `A_ATOMIC`; the obvious alternative is a
flag written at parse time, and it goes STALE — under `-fno-possessify` the
free discharge RUNS while `run_possessify` does not, so a flag left behind by a
deleted `A_ATOMIC` would cut a loop it was passed to leave uncut. It is a
ONE-LEVEL EDGE property: true only for the `A_REP` that is the direct child of
a lifting `A_ATOMIC`, false everywhere inside that quantifier's body.

**THE PRE-PASSES ARE NOT ADVISORY, which is why `vm_cuts` is a predicate rather
than a convention.** `vm_count_slots` allocates the cut-mark slot (a lift it
cannot see runs `vm_slot_mark(v, v->nmark++)` past `RX_NSLOTS` — an
out-of-bounds write in EMITTED code, K27's class), `vm_cost_rep` computes the
budgets, `vm_counter_copies` decides how many body copies exist, and
`vm_rev_canmove` is the sharpest: read through the raw field, a lifted
possessive is handed a RETREAT FRAME and can give back, i.e. the uncut
semantics. `vm_revdet_fits` exists for the same reason one level up, and it
exists BECAUSE a condition written at only one of the three sites produced a
measured slot collision.

**`vm_cost`'s A_ATOMIC arm charges the trailed mark** (R31 C10 — "the caps are
unchanged" was wrong). The mark is written with `vm_set`, the TRAILED writer,
which is what makes nesting and re-entry work; an uncharged trailed write sizes
the array one entry short and the artifact refuses a subject it can match.

**RULE H3 is ONE predicate read at THREE sites** — the search entry, the retry
recompute, and the stamp — because the design's first form read it at the stamp
only and its own proposed check would have AGREED WITH THE BUG. The retry
recompute STAYS on a cut-bearing artifact (it re-seeds `attempt_position`,
which is H2 and is sound); only the CEILING it also computed is dropped.

**THE STRATS STAMP READS `vm_cuts()`, not `Ast.u.rep.possessive`**, which is a
deliberate deviation from the design's §6.4(c). RULE 2 holds — this module
never writes that field — but the LIFT genuinely routes a semantic possessive
onto the possessive rungs, and a stamp saying BACKTRACKING on an artifact whose
loop cuts is the exact D46 lie K29 was opened for.


## [M6.5.2] the BACKREFERENCE's lowering, and PUBLISH-AT-CLOSE

`A_BREF` emits a chain of UNSET tests over the referenced groups' published
slots, in ASCENDING GROUP NUMBER, and one call to the encoding seam. That is
the whole of it — **the correction R32 E1 forced is entirely in `A_CAP`'s
emission, not in `A_BREF`'s.**

**WHAT E1 FOUND.** `A_CAP` wrote its start slot when control traversed the
OPENING position and its end at the CLOSING one — "write on traverse". On
iteration n > 1 of a quantified group that leaves start holding iteration n's
and end holding iteration n-1's: NEITHER is `PCREC_UNSET`, so a reference's
"is it set" test passes on a pair that IS NOT A CAPTURE. `(a|b)+` on "ab" is
libpcre2 (0,1) with group 1 = (0,1); the write-on-traverse model answers (0,2)
with group 1 = (1,2). And `^(?:(a|b)y)+` on "aybay" leaves `ref_start = 2 >
ref_end = 1`, so the emitted `(size_t)(ref_end - ref_start)` UNDERFLOWS to
`SIZE_MAX` and the compare reads out of bounds — K27's class, in emitted code.

**THE CORRECTION IS SCOPED, AND THE MEASUREMENT IS WHAT LICENSES THAT.** A
group some `A_BREF` names is MARKED: its opening position goes to a per-group
PENDING slot (a sixth slot class, above the counters, so no existing
artifact's numbering moves) and the PAIR is published together at the close.
Every unmarked group emits exactly the two writes it always did. An arm-vs-arm
sweep over 5,808 cells — same simulator, same AST, same search order, same
trail discipline, differing only in publication — found publish-at-open at 138
divergences and 40 reversed spans, publish-at-close at 0 and 0, **and the
backref-FREE control population at 0/0 in BOTH**. Publication is unobservable
without a backreference, because at match completion every group is closed.
That is what makes §11.3's byte-identity gate hold by construction.

`vm_marked` is ONE predicate read at the four sites that must agree (the cost
analysis, the slot count, `A_CAP`'s emission and the slot legend), for the
reason `vm_cursor_fits` is one predicate: a fact three sites each re-derive is
a fact one of them will eventually derive differently.

**THE SUPPRESSION COVERS BOTH HALVES OR NEITHER.** Inside a
reverse-deterministic loop's forward scan (`v->nocap`) the capture writes are
suppressed and §3.4's backward walk reconstructs them. The pending write and
the pair it feeds are ONE publication, so suppressing half would leave the
reconstructed pair beside a stale pending value from an earlier iteration —
written as one guarded block so that is structural rather than remembered.
(The backward walk and the cursor rung both write the published pair DIRECTLY,
both halves adjacent, so they are already publications in the sense a
reference needs.)

**THE COMPARE ROUTES THROUGH THE SEAM FROM BIRTH**, and `Ast.u.bref.caseless` picks
WHICH entry at emit time — never a runtime flag, D18/D23's rule. An inline
`(s[i] | 32) == (s[j] | 32)` here would be byte arithmetic that is correct
today and silently wrong under a UTF-8 backend, which is the residue class D58
scope item 3 enumerates by name. The work charge goes through `vm_work_at`,
the same primitive every other charge site uses, and is charged EITHER WAY:
`took` on success, and on failure the entry's negative encoding carries the
prefix it compared, because `(a*)` over a long subject does O(n) byte
comparisons the fail label never sees.

## Conventions

The emitter produces a self-contained .c file (or paired .c/.h if options.header_name is set). Symbols are prefixed with the user's chosen identifier (default "rx"). Emitted code must stay warning-clean under -Wall -Wextra -Werror (the harness enforces this).

**[M5-SEAM] (D58, 2026-08-18) THE ENCODING SEAM lives in `enc/`, and this
file knows almost nothing about it.** The line that used to stand here
("future encoding backends (UTF-8) coexist here as separate files, the way
emit_vm.c does") had the shape right and the location wrong: a backend is
not a second emitter. DD-12 (7) forbids encoding conditionals in the
compiler, the emitter and the artifact alike, so what a backend supplies is
the per-encoding RESIDUAL TEXT an artifact embeds, and what this file
supplies is two functions that look the backend up and copy its text:
`emit_residual_decls` (called from `pcrec_emit_prologue`, so the
declarations land in the `.h` of a split artifact and the `.c` of a
self-contained one, in the same place the four entry-point declarations go)
and `emit_residual_defs` (exported as `pcrec_emit_residual`, called by BOTH
emitters, so the definitions land in the `.c` once). There is no encoding
test in either, and adding one is a design stop rather than a patch. The
first residual entry is `<prefix>_next_pos` (docs/spec/match_api.md §3.1.1).

**[M6.5.2] BOTH FUNCTIONS TAKE A MASK NOW**, because the seam gained its
SECOND and THIRD entries (`<prefix>_bref_match` and its caseless twin) and an
artifact with no backreference must not carry them. `Job.enc_mask` starts at
`PCREC_ENCE_NEXT_POS` and the VM emitter ORs in whichever compare entries its
`A_BREF` arm actually emits calls to — which is why the prologue is written
AFTER the program body, the same "discovered by emitting" discipline the class
pool and the cursor local already follow. `pcrec_enc_ready` moved with the
change (from `decls != NULL` to "has a non-empty entries array"), and that
third site is what R32 E11 found the first design's cost list missing. See
`enc/CLAUDE.md` for D58's revisit clause and why the road not taken (two more
string fields) does not generalise.

`emit_rx_abi_types` gained a paragraph POINTING at the residual entries,
and that paragraph must stay independent of BOTH axes the block sits
across: the block is emitted once per file under a prefix-independent
guard, so `<prefix>` is a placeholder exactly as `<PREFIX>` already is, and
the text must name no particular ENCODING either — two artifacts compiled
for different encodings into one TU share this block and only the first
copy survives the guard. What is per-encoding is the residual's BODY, which
is not in that block.

Emitted text is ASCII-only, including inside generated comments: the artifact
is source someone else's toolchain compiles, and this project already
hex-escapes the pattern comment for the same reason.

## [DD-14 wave G] `vm_splice`, an eighth slot family, and a DFA that declares dead groups

**`emit_vm.c` GAINS `vm_splice`.** A `CALL_SPLICE` site emits the callee's body
INLINE at the site with its OWN exit label: park `|W|`, `goto` the body, body →
`L_done`, restore `|W|`, `goto` the continuation. No `RX_CALL`, no return label,
no `call_top`, no second `goto *`. It may share the BODY and never the EXIT
(design §3.5/§6.3): nothing reuses the lexical occurrence's label.

**AN EIGHTH SLOT FAMILY, `SLOT_SPLICE_SAVE<n>`**, `|W|` per emitted splice site,
at the TOP of the layout so every base below it is unmoved. The reason is not
bookkeeping: `vm_call` parks on the TRAIL and the region reads back at
`trail[frame.trail_mark + j]`, a compile-time offset off the ACTIVATION's own
frame — **a splice has no frame, so it has no anchor.**

**AND ITS `W` IS THE CAPTURE HALF ONLY, WHICH IS A THEOREM AND NOT AN ECONOMY.**
Two activations of ONE EMITTED splice site can nest only if the callee can reach
the site's own enclosing region, which makes callee and region mutually
reachable — the callee is then in a CYCLE, already excluded by eligibility.
§5.3b's two measured counterexamples (a lost match from
`SLOT_GROUP<n>_PENDING`, six false matches from `SLOT_CUT_MARK<n>`) are both
about NESTED activations of one SHARED copy, so the seven per-copy families,
which `vm_count_slots` gives FRESH indices to for the inlined copy, need no
restore. Sequential activations are repaired by the ordinary trail rewind,
because every slot write goes through `RX_SET` (P7: no same-value elision).

**A SPLICE-DEPTH COUNTER IN BOTH WALKS.** `vm_count_slots` charges nothing, so
`PCREC_MAX_VM_NODES` would never fire on an infinite inlining; the counter turns
"eligibility must never admit a cycle" into a diagnostic. `src/ir/nfa.c` has the
third one, and sabotage S175 SEGFAULTED there before it existed.

**REGION ELISION AND THE `has_calls` SPLIT.** A target every one of whose sites
splices gets no region: no labels, no `RX_RETURN`, no slot instances. The eight
sites that emit the LINKAGE's machinery (the frame's two fields, `RX_PUSH`'s
extra line, `RX_CALL`, `CALL_TOP_NONE`, the two resets, the fail label's line)
are gated on `has_linked_calls`, so a fully spliced artifact carries none of it.
`vm_cost` charges NO FRAME for a splice; the `2 * |W|` trail charge stays.

**`emit_dfa.c`: `RX_NCAPS > 1` NO LONGER IMPLIES THE VM.** D42.2's rule rested
on "a capture-bearing pattern forces the VM", which the dead-capture elision
broke in the direction that matters: PCRE2 COUNTS a dead group and reports it
UNSET (MEASURED, `(?(DEFINE)(?<g>a))(?&g)` has CAPTURECOUNT 1), so the artifact
must still promise it. `dfa_artifact_ncaps` is the ONE place both emitters read,
and `emit_search_head` fills groups 1..n with `PCREC_UNSET` once at entry —
gated on `fit.chosen == ENGM_DFA`, because this emitter also writes the VM
hybrid's internal DFA PREFILTER and the first version of that fill leaked into
every capture-bearing VM artifact in the corpus (558 of 2442 call-free patterns
moved; the identity gate caught it on its first run).

Maintenance: update this file when files are added/removed or their roles change.

## [DD-14.FB] THE CALLER-PROVIDED FRAME BUFFER: the run state splits, and three entries become six

D71 item 2, spec §10, design `docs/design/frame_buffer_design.md`. The whole
change is one idea with a lot of consequences: **the run state stops OWNING its
two arrays and starts POINTING at them.**

**The shape.** `<prefix>_run_state` holds `resume_stack`/`resume_cap` and
`trail`/`trail_cap`; the stamped-default storage moves into a new
`<prefix>_run_buffers`, which the three UN-SUFFIXED entries declare as an
ordinary local and the three new `_in` entries declare not at all. That
asymmetry is the feature: MEASURED, `rx_search`'s frame stays 131,216 B on a
call-bearing artifact and `rx_search_in`'s is 144 B, because an entry handed
the caller's pointers has no arrays to declare and **C has no way to declare a
local conditionally.**

**The delegation runs `_in` → un-suffixed and NEVER the reverse**, and this is
the one thing here most likely to be "simplified" into a bug. Making the old
entry a thin wrapper round `_in(..., NULL)` reads better and is wrong: `_in`
would then own the default storage and declare it unconditionally, so the
caller who supplied buffers pays the 128 KB anyway. It changes NO ANSWER, which
is why the check for it is structural (tests/codegen's `[DD-14.FB]` block reads
the emitted text) rather than behavioural.

**One implementation, two ways to point it at storage.** The search, match and
match-caps bodies moved into statics — `<prefix>_search_run`,
`<prefix>_match_run`, `<prefix>_match_caps_run` — and the six public entries
are wrappers that bind storage and call them. The alternative, a second copy of
the loop for the `_in` entries, is the parallel mechanism the house rule
forbids and is what design §12's P-2 names as the fallback it does not want.

**The SEVEN capacity sites.** Every place that tests a depth against a capacity
reads `run->resume_cap`/`run->trail_cap`: `vm_region`'s region-exit
`_R_INTERNAL` guard, the `RX_TRAIL`/`RX_PUSH` pair, their two tracing twins,
and the two `RX_CALL` variants. They are ENUMERATED rather than described
because leaving one on the stamped constant is invisible to every caller who
uses the default — sabotage row S182.

**Counters are `size_t`, not `unsigned`, and it was free.** The descriptor's
counts are `size_t`, so an `unsigned` depth counter would wrap past the guard
for a caller reserving more than `UINT_MAX` frames — the very caller this
feature targets. `trail_mark` and `call_top` widened with them. MEASURED: on
the default (untraced) axes this lands entirely in what was already padding, so
the resume frame is still 24 bytes call-free and 40 call-bearing. Only
`--trace` grows (24 → 32, 40 → 48), because the `int id;` no longer shares a
padding hole.

**The sizing surface is STAMPED LITERALS, reconciled by the artifact itself.**
`<PREFIX>_RESUME_FRAME_SIZE` and friends cannot be `sizeof` expressions,
because §5.4 keeps `<prefix>_frame`/`<prefix>_trail_entry` `.c`-private and the
header would be naming a type it does not declare. So `vm_frame_fields` /
`vm_trail_fields` build ONE member list that both EMITS the struct and FEEDS
`vm_layout`'s size arithmetic — the two cannot drift by construction — and the
artifact carries a `_Static_assert` per macro comparing the stamped number
against the real `sizeof`/`_Alignof`. A number computed for the wrong target
model, or stamped from the wrong struct (sabotage row S184), is then a loud
compile error in the artifact rather than a silent under-allocation in a
caller. **If you add a member to the resume frame, add it to the member list;
that is the whole maintenance rule.**

MEASURED, and it is the check that shows the rule working: `--trace` puts an
`int id;` on the frame, so a traced artifact stamps **32** (call-free) and
**48** (call-bearing) where the untraced ones stamp 24 and 40 — the tracing
member no longer shares a padding hole with the two `size_t` counters. The
stamp follows because the list that EMITS the traced struct is the list that
computes the size. A drift THROUGH the list is not even representable: an
emitter patched to build the list without the tracing axis emits a struct with
no `id` member, and the artifact fails on the missing member rather than on a
wrong number. The remaining route — a SECOND computation of the size, blind to
an axis the struct sees — is what the `_Static_assert` catches, and that was
validated in the failing direction (a scratch emitter stamping from a
trace-blind second list stamps 40 and the traced artifact then fails to compile
naming `RX_RESUME_FRAME_SIZE`). `tests/codegen`'s `[DD-14.FB]` `--trace` check
pins both numbers and compiles both artifacts.

**The surface is emitted on a DFA artifact too, INERT** (`emit_in_entry_defs`
and `emit_buffers_surface`, both in emit_dfa.c): the three `_in` entries accept
a descriptor and ignore it, the four sizing macros read 0 and the alignment
reads 1 — never 0, because a caller rounding an arena cursor UP to it would
divide by zero. This is a deliberate departure from §6.3's VM-only rule for
capacity macros, ruled by spec §10.4: those macros report what an artifact DID,
these report what a caller needs in order to CALL it, and engine selection is
not the caller's choice.

**`<PREFIX>_RESUME_FRAMES`/`_TRAIL_FRAMES` moved `.c` → `.h`** with the rest of
the surface, because a caller has to read them before it can size a buffer.
Two in-tree scripts grepped them out of the `.c` and were fixed to read the
`.h` too; a third consumer would have gone VACUOUS rather than red.

## [OPT-1] THE TWO-TIER DEFAULT ENTRY: the storage moves off the entry's frame

`docs/design/two_tier_entry.md`, `docs/spec/match_api.md` §10.9, `abi` 4 → 5.
One idea again: **the stamped default storage stops being a local of the
function every call enters.**

**The measured cause.** `gcc -fstack-clash-protection` probes every page of a
frame on EVERY call, and `<prefix>_search`'s `<prefix>_run_buffers` local is 24
pages on the email specimen. MEASURED ([OPT-1] STEP 1, N=100k, median of 5,
`taskset`): 233.8 ns/call against 46.3 for `<prefix>_search_in` and 46.2 for
the same entry under `-fno-stack-clash-protection`. The tax is proportional to
the STAMPED DEFAULT, so a pattern with a small statically-derived requirement
pays nothing — which is why the fix is a shape change and not a smaller number
(D73 keeps 2048/3072).

**The shape.** `vm_emit_default_entry` emits all three un-suffixed entries and
is the ONE place the storage decision is made. On a TIERED artifact it writes a
`noinline` `<name>_deep` owning the stamped default, plus an entry that binds a
page-budgeted `<prefix>_fast_buffers` and calls `_deep` on `PCREC_ERR_FRAMES`
and nothing else. **`noinline` is load-bearing**: inlined, the 98 KB is back on
the entry's frame and the change does nothing. MEASURED: `rx_search` 131,216 →
**3,184 B** call-bearing, 98,432 → **3,184 B** call-free; `_in` unchanged at
144/128.

**IT IS ONE FUNCTION BECAUSE THE THREE ENTRIES WERE ALREADY THREE NEAR-COPIES.**
They differ in return type, parameters, the arguments threaded to their `_run`,
and how the FRAMES give-up is spelled at their layer — `<prefix>_search` sits
above the search loop and compares `PCREC_ERR_FRAMES`, the two anchored entries
sit on `match_anchored` and compare `<PREFIX>_R_FRAMES` (§4.4's three layers).
Adding the tier in place would have made them three near-copies of twelve lines
with the escalation pasted three times, which is S-FB2's shape.

**ONE TIER IS THE DEGENERATE CASE, NOT A SPECIAL CASE.** `tiered` is false when
the stamped default already fits the budget (the common case), when
`NSLOTS * 8` alone exceeds it, when the scaled capacities fall below
`VM_FAST_TIER_MIN`, or under `-fno-tiered-entry`. All four emit the shape that
shipped before [OPT-1], BYTE FOR BYTE — which is why the single-tier text is a
separate literal string rather than the tiered one with a substituted clause.
MEASURED: `(\w+)\s+\1` and `(?<=foo)bar` differ from the pre-change emitter
by the two FAST stamps and `.abi` and nothing else. **No DFA artifact's bytes
move at all**, a first for an `abi` bump.

**THE BUDGET IS A BYTE COUNT, AND IT IS ASSERTED RATHER THAN TRUSTED.**
`VM_FAST_TIER_BYTES` (3,072) is denominated in the unit gcc charges in — pages
— and leaves 1 KB of a 4 KB guard page for the run state's scalars, the
`rx_ctx` and whatever `_run`/`match_anchored` spill when gcc inlines them in.
The capacities are scaled from the default pair IN ITS OWN RATIO (`vm_cost`
derives that ratio from the pattern; scaling independently would give up on the
wrong axis first), computed ONCE beside the `BufSurface` and read by both the
stamps and the bind — [DD-13]'s `unanch_start` rule, because a capacity the
artifact BINDS and one it STAMPS that are computed twice can disagree
invisibly. The arithmetic is a CLAIM about gcc's frame;
`tests/codegen/run_tiered_entry.sh` §4 and `tests/thread/run_stackdepth_tests.sh`
both read the real `-fstack-usage` number.

**WHY THE ANSWERS CANNOT MOVE.** The deep run is a bit-for-bit replay of what
the single-tier entry does, from scratch: same capacities, `run_state_init`
refills both budgets, `_run` re-runs the prefilter and the same start-position
loop, one deterministic VM. Nothing carries over because §5.3 leaves nothing
that could. **Budgets RESET on escalation and must** — carrying the remainder
would report `STEPS` where a single-tier artifact matches. The fast tier may
report `FRAMES` where a single-tier run reports `STEPS`; that value is never
returned, it is the trigger.

**`R_FRAMES` IS EXACTLY "CAPACITY EXHAUSTED", WHICH IS WHY IT IS A SOUND
TRIGGER.** Four emitted sites produce it, all `depth >= cap`, and TRAIL
exhaustion reports `FRAMES` too — so the tier escalates on the CODE, never on a
depth it inspects itself. The fifth site that mentions a capacity is NOT a
capacity test: `vm_region`'s `call_frame >= run->resume_cap → R_INTERNAL` is
D72's sentinel test, `CALL_TOP_NONE` is `(size_t)-1`, out of range for every
capacity, and a live `call_top` is always `< resume_depth <= resume_cap`
because `RX_CALL`'s own guard runs before it assigns one. It fires on the same
event under both capacities. **This was the one place the identity claim could
have failed silently**, so it is checked and not assumed.

**THE STAMPS AND THE HOOK.** `<PREFIX>_FAST_FRAMES`/`_FAST_TRAIL`, VM-only and
`.c`-private beside the budget macros (§6.3(b) capacity facts, NOT §10.4's
caller-facing sizing arithmetic — nothing a caller does depends on the tier
boundary). Emitted on EVERY VM artifact: `FAST == RESUME` **is** "one tier", by
whichever of the four routes, because a fact readable by a macro's ABSENCE is
the discriminator [DD-13] had to remove from two checks. The
`<PREFIX>_TIER_NOTE()` hook is an `extern` FUNCTION under
`#ifdef <PREFIX>_TEST_TIER_HOOK`, never a counter: a mutable static in an
artifact is a TS-1 failure and a §5.3 breach, and it binds under `-D` exactly
as without one. Inert without the `-D`, so what the check reads IS the default
artifact's text.
