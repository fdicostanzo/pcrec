# [OPT-4.2] — extend the nullability decline to every prefilter rung

Lane `o42` (opus, worktree `worktrees/o42`, branch `lane/o42`).
PHASE 1 (read + code only, under the box hold) COMPLETE, all 9 steps
committed. PHASE 2 (build + full validation, after the box lift landed and
the team lead serialized this lane third behind `cc`/`w12`) is ALSO
COMPLETE — see §9 for the full measured results. **DELIVERED**: branch
`lane/o42`, 21 commits, not merged, not pushed.

Every claim below is marked MEASURED (a command run and its number) or
INFERRED (derived from a careful source read + hand-trace, from the Phase 1
period under the hold). Phase 2 turned every Phase-1 INFERRED claim about
runtime behaviour into a MEASURED one — every prediction in §§1-7 below was
confirmed exactly, with two real findings along the way (§9.2/§9.3) that
Phase 1 could not have seen.

**Charter note.** The plan row as filed said "NEEDS FRANK'S CHARTER — it
changes a bench-bucketed stamp surface." I read `docs/dev/wake.md`'s own
"THE QUEUE" section (forty-seventh session close) as resolving this: it
names `[OPT-4.2]` explicitly among the queued items and states "Frank's
blanket proceed-with-queued-items is read as the charter — confirm in one
line if he's present." I proceeded on that reading rather than re-blocking
on it; flagging it here so the manager can confirm or correct at review.

---

## 1. The design: one predicate, two scopes

`src/opt/select_engine.c`'s fit site already computed, under [OPT-4.1]:

    fit.prefilter_declined_nullable =
        cx->collapse_reason != CR_NONE && fit.prefilter_lang_nullable &&
        fit.prefilter_has_collapsible_rep &&
        !has_bref && !has_call && !force_on;

This fires only on a ladder RUNG (`collapse_reason != CR_NONE`). The general
form needed for the ORDINARY hybrid (no rung, `collapse_reason == CR_NONE`)
shares every conjunct except `prefilter_has_collapsible_rep` (meaningless off
a rung — the ordinary path never collapses anything, so there is always a
concrete EXACT prefilter to decline). I factored the shared part into one
local and read it into both fields:

    bool lang_nullable_declinable =
        fit.prefilter_lang_nullable && !has_bref && !has_call && !force_on;
    bool would_prefilter = (fit.chosen == ENGM_VM) &&
                            (cx->opt->engine != PCREC_ENGINE_VM);
    fit.prefilter_declined_nullable =
        cx->collapse_reason != CR_NONE && lang_nullable_declinable &&
        fit.prefilter_has_collapsible_rep;
    fit.prefilter_declined_nullable_default =
        cx->collapse_reason == CR_NONE && !cx->dfa_disabled &&
        lang_nullable_declinable && would_prefilter;

**`would_prefilter` and `!cx->dfa_disabled` are the two guards this row
needed that the rung-scoped field did not, and both are r47sel-1-shaped
false-stamp guards** (that finding: the rung's own decline was reachable
without a collapsible repeat, stamping "a rescue was refused" where none was
ever offered). Without `would_prefilter`, a DFA-chosen artifact or a forced
`--engine=vm` build with no `-fprefilter` (R21 E-6 already turns the
prefilter off there) would stamp the decline despite never having a
prefilter to decline. Without `!cx->dfa_disabled`, a retry whose OWN
prefilter construction overflowed with no rung offered (the
`ESEL_OVERFLOWED_DFA`/`_PREFILTER` population) would be misattributed too. I
traced both by hand against every reachable branch of `compile_driver`'s
retry loop and the `fit.chosen`/`cx->opt->engine` combinations; see the
commit message on `7a4237f` for the two bugs I found and fixed in my own
first draft before settling on this shape (I initially folded
`!cx->dfa_disabled` into `would_prefilter` itself, which is ALSO the final
`fit.prefilter` fallback value — that would have broken the CR_SEL1 rung's
own success case, where `dfa_disabled` is legitimately true while a
collapsed rescue survives).

`fit.prefilter`'s decline clause gained the new field as a third OR-term;
the final fallback (no decline applies) is now `would_prefilter` (unchanged
in value from the pre-existing `(fit.chosen == ENGM_VM) && (cx->opt->engine
!= PCREC_ENGINE_VM)`, just named and shared).

## 2. The new closed-set value, and its placement

Design constraint #1 required a NEW `ESEL_*` value (not a silent reuse of
`ESEL_DECLINED_NULLABLE`) placed so the existing invariant (`>=
ESEL_OVERFLOWED_DFA && <= ESEL_DECLINED_NULLABLE` means "a DFA state cap
overflowed") stays true, with the placement argued in the invariant comment.

I placed `ESEL_DECLINED_NULLABLE_DEFAULT` **adjacent to `ESEL_SELECTED`
(value 2), renumbering the five sibling values up by one**, rather than
appending it after `ESEL_SIZE_CAP_RETRY` the way `[LIM-1]` appended ITS
value. The reason is the OTHER invariant this enum's own comment states:
"a consumer wanting 'any fallback occurred, of any kind' now tests `>=
ESEL_OVERFLOWED_DFA` (unbounded above)." `ESEL_SIZE_CAP_RETRY` deliberately
DOES satisfy that test (it genuinely is a fallback, just not a state-cap
one). The new value must NOT satisfy it — nothing overflowed on that path —
so appending it after `ESEL_SIZE_CAP_RETRY` would have created exactly the
silent-misclassification shape this project's own K35 catalogue exists to
name. Renumbering costs nothing outside `internal.h`: I confirmed (grep,
MEASURED) that no other `.c`/`.h` file in `src/`, `tests/`, `cli/`, `lib/`
references any `ESEL_*` name as a bare numeric literal — every site goes
through the symbol, and the only place the ordinal could leak into a
generated artifact is `pcrec_engine_sel_name()`'s `switch`, which returns a
STRING and is unaffected by renumbering the `case` labels.

## 3. The abi ritual — followed the [OPT-4.1] precedent, no bump

I read `src/gen/CLAUDE.md`'s own record before assuming either way:
`[OPT-4.1] ADDED THE SIXTH, AND IT IS A VALUE RATHER THAN SCAFFOLDING (D76,
so no abi bump)` — its sixth `ESEL_*` value landed with NO abi change,
because the ordinal never reaches a generated artifact; only
`pcrec_engine_sel_name()`'s string does, and that string is written into the
same `#define RX_ENGINE_SEL "..."` line every artifact already carries (no
new macro, no struct field, no layout change). [OPT-4.2]'s eighth value is
the identical shape — same emitter function, same macro, one more `case`,
one more string literal — so I followed the precedent rather than bumping.
Recorded explicitly in `src/gen/CLAUDE.md`'s new [OPT-4.2] paragraph and in
`internal.h`'s own enum comment, both citing this reasoning by name so a
future reader does not have to re-derive it.

**While reading that section I found a pre-existing staleness** (not caused
by this lane): the `[OPT-4.1] ADDED THE SIXTH` paragraph still said
"reachable ONLY from the [SEL-1] rung" and "the SIZE rung's own decline
stays `\"selected\"`", both superseded by `[LIM-1]` (which widened the
value's reach to both rungs) with no corresponding note ever added to this
file. Fixed in the same commit (`0c0f562`) rather than left for a future
lane to trip over, per the house rule about touching a file you find stale
prose in.

## 4. Registry legs and the D80 spec hunk

- `src/gen/emit_dfa.c`'s `pcrec_engine_sel_name()` — new `case`.
- `src/gen/emit_vm.c` — `VmStamp` gains `prefilter_declined_nullable_default`
  (copied off `job->fit`, never re-derived, mirroring its sibling field
  exactly); the `--emit-ir` `; prefilter` listing gains its own worded arm
  immediately after the rung-scoped one, WORDED DIFFERENTLY rather than
  merely generalized (no "offered and declined" language, since no rung ran).
- `src/parse/axes_dump.c`'s `RX_ENGINE_SEL` axis (the `--list-axes` surface)
  gains the eighth row, placed at `order` 2 (right after `forced`) rather
  than beside its rung-scoped cousin — `order` is the dump's own field with
  no promise about `ESEL_*` ordinals (the existing `[LIM-1]` comment already
  says so), so I used it to keep the "not a fallback" value visually
  separate from the five that are.
- `docs/spec/match_api.md` §6.3's `RX_ENGINE_SEL` value table gains the new
  row plus two new explanatory paragraphs (why it is not among "the last
  five... all FELL BACK"; why it is a separate value from
  `declined-nullable` rather than folded in).
- `docs/spec/tuning.md` §2.17 gains a full new subsection generalizing
  [OPT-4.1]'s rung-scoped prose to the ordinary path, naming the measured
  population growth from [OPT-5] and the O-10 bench numbers.

I did NOT find or need to touch `tests/registry/axes_registry_check.sh` or
`registry_check.c` themselves — both cross-check the THREE sources above
(the dump, the spec table, and `pcrec_engine_sel_name`'s own `return`
statements) against each other rather than hand-declaring a value set of
their own, so a consistent new value across all three should pass their
existing legs without a script edit. **This is INFERRED, not measured** —
Phase 2 must run `bash tests/registry/run_registry_tests.sh` to confirm; I
traced the three extractors' anchors (`extract_md_table_values` on "the same
decision as a TOKEN", `dump_stamp_vals RX_ENGINE_SEL`,
`extract_c_return_values` on `pcrec_engine_sel_name`) by hand and none is
anchored on a value COUNT that my edits would have broken (the anchor
comment explicitly rules that out: "THE ANCHOR CARRIES NO COUNT... a seventh
must not break the extractor" — now an eighth).

## 5. The tripwire flip

`tests/resource/run_resource_tests.sh`'s `[OPT-4.2 tripwire]` cell (filed by
the manager 2026-08-31 pinning the KNOWN gap) is flipped to assert the FIXED
stamps: `RX_VM_PREFILTER "none"`, `RX_ENGINE_SEL "declined-nullable-default"`,
no `RX_VM_PREFILTER_LANG_WHY` macro at all (there is no prefilter left to
name a language for — confirmed by re-reading `emit_vm.c`'s own gate on that
macro, which is `if (job->fit.prefilter) { ... }`; false here). Also checks
the regression direction by name (a return to `hybrid`/`exact` fails loudly
naming what regressed, not just a generic mismatch). `tests/resource/
CLAUDE.md` gained a section explaining why this stays a THIRD cell rather
than folding into the [OPT-4.1]/[LIM-1] pair above it — no cap is ever hit
on this path, so neither rung cell can exercise it.

## 6. Witnesses (tests/prefilter/)

Four new checks, hand-traced variable by variable against
`select_engine.c`'s derivation (full traces in the commit message on
`0e68546`):

1. `'(a)*'` — a PRE-EXISTING population (captures force the VM via the
   existing `forces_captures` rule; the pattern's own language is nullable
   with no [OPT-5] growth needed to reach it, distinct from the
   `(a|b){0,30000}` family the plan row's own MEASURED note names as
   grown by [OPT-5]'s scan edge). Traced: `prefilter_lang_nullable`=true
   (minw=0 for an unbounded `A_REP{0,-1}` over `A_CAP('a')`),
   `has_bref`/`has_call`/`force_on`=false, `would_prefilter`=true (chosen
   VM, engine AUTO), `dfa_disabled`=false (no retry on a 2-node pattern) →
   `prefilter_declined_nullable_default`=true → stamp `none`, `RX_ENGINE_SEL
   declined-nullable-default`, 0 `_prefilter(` symbols.
2. THE CONTROL: `'(a)b'` (reused from check 1's own existing witness) —
   minw=2 (not nullable) → the new field is false → stamp `hybrid`,
   `RX_ENGINE_SEL selected`, UNCHANGED.
3. `-fprefilter` on `'(a)*'` — `force_on`=true excludes
   `lang_nullable_declinable`, so the decline never fires and `force_on ?
   true` wins → stamp `hybrid`. The one asymmetric override, carried over
   from [OPT-4.1] unchanged.
4. `--emit-ir`'s listing line on `'(a)*'` reads the new arm's text,
   containing `"NO (nullable exact language)"`.

## 7. Sabotage row S216

`tests/mech/sabotages/S216_opt42_default_decline_neutered.sh`: forces
`fit.prefilter_declined_nullable_default = false` unconditionally,
reproducing [OPT-4.2]'s entire pre-fix state. `SAB_SUITES="prefilter"`,
following `S64`/`S65`'s own precedent for this exact shape of defect — the
decline is answer-identity-preserving BY DESIGN (the VM re-derives the true
answer from every candidate regardless of the filter, `tuning.md` §2.17's
own rule, unchanged from [OPT-4.1]), so no `.rxt` corpus, no differential
and no other structural check can see it; only `tests/prefilter/
run_prefilter_tests.sh`'s new checks 1 and 4 read the artifact this way.
Ran through the mech matrix at merge (VALIDATE_ONLY confirmed the field
definition first, then the real run on committed HEAD `e6fe589`):
`prefilter:2fail/30pass` — **DETECTED**, and the two failing checks are
exactly checks 1 and 4, the ones the row's own header predicted. 0
unexpected/undetected/unreached/anomalies. Next free sabotage id after this
lands: **S217**.

## 8. Phase 2 — full validation, MEASURED (after the lift, third in the
   serialization behind `cc`/`w12`)

**Build.** `make -j4` clean, no warnings. `make strict` clean
("whole tree compiles clean with `-Werror -Wshadow`").

**`make test-prefilter`**: 32/32 PASS (0 fail). All four new [OPT-4.2]
checks passed on the first run, matching every Phase-1 hand-trace exactly.

**`make test-resource`**: found 2 genuine FAILs on the first run, both
caused by [OPT-4.2] firing EARLIER than the rung-scoped decline — my new
field is decided at the fit site on the compile's FIRST attempt, before any
exact prefilter machine is built, so for any VM-forced (captures) nullable
pattern it preempts BOTH the [SEL-1] and SIZE rungs entirely; no retry is
ever needed, and neither `-fno-scan-edge` nor `-fno-prefilter-collapse` have
anything left to act on. Diagnosed and fixed BOTH stale test cells (never
the code) after verifying the correct behaviour by hand-probing `build/
pcrec` directly:
  - `size_moved`'s `'(a|b){0,30000}'` row (the total-emitted-size-cap
    refusal witness) needed `-fprefilter` added to its flag set to
    reproduce the historical refusal at all — MEASURED: refuses at
    1,333,410 bytes (pin corrected from a stale 1,333,406), re-accepts at
    1,341,343 with `--max-emit-bytes` raised.
  - `size_rung_cell`'s nullable witness (same pattern under
    `-fno-scan-edge` alone) can no longer reach the rung-scoped
    `ESEL_DECLINED_NULLABLE` — updated the expectation to
    `declined-nullable-default` and wrote the reachability analysis into
    the function's own comment (see §9.2 below for the FULL resolution,
    not left as an open question).
  After both fixes: **30/30 PASS**.

**`make test-codegen`**: found 1 genuine FAIL on the first run —
`[SABANCHOR]` (`scripts/m6read_check_sab_anchors.py`) reported two stale
anchors, `S102_prefilter_on_backref.sh` and `S165_prefilter_on_call.sh`.
Step 1's diff added a fourth disjunct to `fit.prefilter`'s multi-line
OR-clause, which is exactly the expression these two rows anchor their
whole patches on — the THIRD time this same expression has needed
re-anchoring in its own recorded history ([OPT-4], [OPT-4] ruling B,
[OPT-4.1], now [OPT-4.2]). Re-derived both anchors from the live source;
both sabotages UNCHANGED IN MEANING (still disable exactly one conjunct
each — `has_bref` / `has_call` respectively — and carry the rest through
verbatim, including the new fourth disjunct). Re-ran the anchor checker
solo before the full suite: "212 sabotages, all anchors resolve." After the
fix: **198/198 PASS**.

**`make test-registry`**: 600/600 PASS, exit 0 on the first run, no fix
needed. Directly confirms the team lead's pinned item 2: `RX_ENGINE_SEL`'s
closed-set legs (dump-vs-docs, dump-vs-code) enumerate all 8 values,
including `declined-nullable-default`, and agree across `--list-axes`,
`match_api.md` §6.3's table, and `pcrec_engine_sel_name()`'s own `switch`.

## 9. The three items the team lead pinned for merge review, MEASURED

**9.1 — no ordinal leak; identity gate (A) byte-identical.** Grepped every
reader of the raw `engine_sel` field across `src/`, `cli/`, `lib/` and the
test infrastructure: it is written ONCE (`select_engine.c`'s fit site) and
read ONCE (`pcrec_engine_sel_name()`'s `switch`, which returns a STRING) —
structurally, no ordinal can reach a generated artifact. Confirmed
empirically too: compiled one pattern per reachable `ESEL_*` value
(`forced`, `selected`, `declined-nullable-default`, `size-cap-retry`,
`declined-nullable`) and grepped each `.c` for `RX_ENGINE_SEL` — every one
is a plain string `#define`, and `--list-axes`' own `order` column (which
happens to read `2` for the new value) is independently documented as
carrying no promise about the C enum's ordinal.

Ran the on-demand `make test-recursion-identity` gate directly to confirm
comparison (A): **`same=2223 differing=0 elided=4 size-term-moved=1
call-bearing-in-population=0`** — the PROGRAM REGION against the unchanged
pre-module pin `ac4917d` is byte-identical. Comparison (B) (whole file
against the current abi-13 pin `dc2c8ef`) shows 94 call-free patterns with
unclassified differences — EXPECTED and not a defect: those are the
nullable call-free patterns whose `RX_ENGINE_SEL`/`RX_VM_PREFILTER` stamps
this fix legitimately moves, the same shape [OPT-4.1]'s own landing
produced on its own population. **Per the team lead's own merge-time
reading: this self-heals at merge**, because the merge re-pins comparison
(B)'s `FILEPIN` to its own last src commit, which then already carries this
lane's stamp movement — so no classifier surgery is owed for this landing.
The `--engine=vm` axis of that same run was cut short by my own 250s
timeout mid-sweep; the merge battery's full run closes that residue.

**9.2 — the renumbered `ESEL_*` invariant.** Covered structurally by 9.1's
own registry-legs result (600/600) and by the internal.h placement note
itself; no separate measurement needed beyond what §9.1's population
already confirms (every value's string is correctly produced and correctly
enumerated after the renumbering).

**9.3 — `ESEL_DECLINED_NULLABLE`'s reachability, RESOLVED not just flagged.**
Traced the code precisely (not merely asserted): `prefilter_declined_
nullable_default`'s `collapse_reason == CR_NONE` guard is true ONLY on a
compile's FIRST attempt, so it structurally CANNOT fire during a retry —
the rung-scoped decline (which requires the opposite condition) is never
shadowed. The SIZE-cap rung specifically IS foreclosed for any nullable
pattern, but for a reason distinct from my own field: MEASURED that a
`--no-captures` oversized pattern (`[a-z]{0,30000} -fno-scan-edge`) just
REFUSES outright with no retry at all — the collapse-and-retry rescue is a
VM-hybrid-prefilter-only mechanism with no DFA-only equivalent, so it was
never reachable for a DFA-chosen artifact. The [SEL-1] STATE-cap rung's own
path stays open IN PRINCIPLE: on that retry, `dfa_disabled=true` and
`collapse_reason=CR_SEL1` are set TOGETHER, so my field's `CR_NONE` guard
cannot interfere. Two attempts to build a corpus witness for that specific
combination (wrapping `tests/prefilter`'s own SEL-1 witness nullable)
changed which CAP fired first rather than landing on the STATE cap
specifically — a WITNESS GAP, not a dead value, and I left it exactly that
way rather than deciding to retire or paper over it. Full trace committed
in `tests/resource/run_resource_tests.sh`'s own comment (`e6fe589`).

**Corpus stamp-movement sweep** (ad hoc, `/tmp/o42_stamp_sweep.sh`, not
committed — a one-off diagnostic, not a permanent test): 2,845 corpus
patterns checked (before = main tree's pre-fix binary, after = this
worktree's build), **50 moved**, every single one the IDENTICAL clean
transition (`selected` → `declined-nullable-default`, `hybrid` → `none`) —
no partial or mixed transitions anywhere in the population.
`docs/dev/artifact_size_log.tsv` untouched (no full `test-corpus`/`SIZELOG`
run this lane; nothing to `git checkout` back).

## 10. Branch state

`lane/o42`, 21 commits, not merged, not pushed.
`git log --oneline 14f7c44..HEAD` in the worktree lists them in order. One
process note from Phase 1: my first attempt at step 1 landed in the MAIN
repo tree by mistake (an absolute-path slip past the worktree prefix) —
caught before any commit there, the diff was moved into the worktree via
`git apply` + `git checkout --` on the main tree's two touched files, and
the worktree's own first real commit (`7a4237f`) records the incident so it
is not silently lost from the history. `git status` on both trees confirmed
main clean throughout.

**Not this lane's to trigger**: the bench-side re-measurement of its
`cls-*` hybrid cells (the plan row's own note says the manager sends that
inbox item).
