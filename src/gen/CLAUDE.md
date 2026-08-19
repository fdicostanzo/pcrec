# src/gen — C code generation

Emits self-contained gcc-dialect C from the DFA machines. Two engines (D7):
ENG_UNANCH for patterns without `^` (including `$`-bearing ones since M2.7/D8) — table-driven O(n) forward scan
(leftmost-first match end) + reverse scan (match start), with a memchr/bitmap
start-state prefilter; ENG_ATTEMPT for `^` patterns — per-start computed-goto
attempt loop with EOL-variant states. Table emission exists because gcc compile
time on huge computed-goto functions is superlinear (R1 A-3). Generated code
has zero dependency on pcrec at build or run time.

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
  TERMINATION reads `s[startpos-1]` and is **ATTACHED TO THE `pp <= startpos`
  BREAK, not peeled below the loop** — the reverse loop has a SECOND exit
  (dead state), and an epilogue would run on it, recording `sfound` at a
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
leaves `run_wordctx_identity.sh` at 1135/1135 IDENTICAL, and that script fails
only through a side effect (an orphaned parameter warning). Moving this wave's
knob is what exposed the dead `gseed[]` table above.

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
  legitimately be -1), and `caps_out` reads one existing array element instead
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

**THIS IS THE ONLY SITE THAT READS `v.nkreset`, WHICH IS WHY THE WAVE SHIPS NO
BYTE-IDENTITY GATE.** Waves A-D each changed a construction spanning several
emitter decision points and each needed a corpus-wide comparison against a
reference build to say a construct-free pattern paid nothing. Here the claim
is about ONE predicate, so it is pinned structurally — `[M6.2-KRESET rule 1b]`
in `tests/codegen/run_codegen_tests.sh` quotes the pre-wave `caps_out` body as
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
  give-up code space (`PCREC_ERR_STEPS`/`_FRAMES`/`_WORK`/`_FLOOR`), the
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
the point worth stating: every OTHER D46 stamp in this file
(`RX_VM_RUNGS`/`RX_VM_STRATS`/`RX_VM_PRUNES`/`RX_VM_PREFILTER`) lives in
`emit_vm.c` and is VM-artifacts-only, because possessify/revdet/MRL/prefilter
are all decided or consumed only on the VM path. ALTCLS is a pure AST rewrite
that runs BEFORE either engine is built (`src/core/compile.c`, immediately
after parse), so a capture-free pattern's DFA-only artifact carries the stamp
too — the plan row's own point that the DFA tier gets a real
byte-equivalence-class win from stage 1, not merely the VM. Emitted
unconditionally (STD1's own rule), including the honest `0`/`0` a pattern
with no alternation at all stamps. `emit_info_def`'s `strategy_denials` mask
also gained `PCREC_NO_ALTCLS_MERGE`/`PCREC_NO_ALTCLS_FACTOR`, for the same
reason the D47.3 family and the prefilter force pair are both masked out of
`rx_info.flags` there: the axis changes no answer, only the emitted shape.

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

  The pieces worth knowing before editing it:

  - **`stv`, one flat array** (§2.4) holding capture pairs, empty-iteration
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
    the body's reversed AST on `Ast.revbody`; `vm_revdet_rep` emits it.

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
        is `count - stv[ctr] - j`, read from the TRAILED counter slot.
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

Maintenance: update this file when files are added/removed or their roles change.
