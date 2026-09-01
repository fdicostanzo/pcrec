# [OPT-4.2] — extend the nullability decline to every prefilter rung

Lane `o42` (opus, worktree `worktrees/o42`, branch `lane/o42`).
PHASE 1 (read + code only, under the box hold) COMPLETE, all 9 steps
committed. Phase 2 (build, the corpus stamp-movement sweep, the mech
matrix run for S216, `make test-registry`/`test-codegen`/`test-prefilter`/
`test-resource`) PENDING `worktrees/o42.lift`, which never appeared during
this lane's run.

Every claim below is marked MEASURED (a command run and its number) or
INFERRED (derived from a careful source read + hand-trace under the hold,
following `opt41_report.md`'s own precedent for this shape of lane). Under
Phase 1 nothing was compiled or run, so **every claim about the compiler's
runtime behaviour is INFERRED** — the hand-traces are recorded in enough
detail (variable-by-variable) that a reviewer can re-derive them without
running anything, and Phase 2 is what turns each into MEASURED.

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
NOT yet run through the mech matrix (the box hold); the row's own header
records the predicted detection per `S213`'s precedent of recording the
argument before the battery confirms it. Next free sabotage id after this
lands: **S217**.

## 8. What is NOT done — all blocked on the box hold

- **The build itself.** Nothing in this branch has been compiled. Every
  claim above is a hand-trace, however careful, and Phase 2 must run
  `make -j4 && make strict` first.
- **The corpus stamp-movement sweep.** I cannot enumerate which corpus
  patterns move stamps without compiling the corpus. `docs/dev/
  artifact_size_log.tsv` will move (per CLAUDE.md's own standing note,
  `git checkout` it after any corpus run — not this lane's to reset before
  the manager reviews the diff).
- **`make test-registry`** (the three `RX_ENGINE_SEL` legs — §4 above),
  **`make test-codegen`**, **`make test-prefilter`**, **`make
  test-resource`** — all traced by hand, none run.
- **`bash tests/mech/run_sabotage_matrix.sh S216`** — the row's own
  DETECTED confirmation.
- **The bench-side re-measurement** ("the bench re-measures its cls-*
  hybrid cells after this lands") — the plan row's own note says the
  manager sends that inbox item; not this lane's to trigger.

## 9. Branch state

`lane/o42`, 10 commits (the hold-ack plus 9 numbered steps), not merged, not
pushed. `git log --oneline 14f7c44..HEAD` in the worktree lists them in
order. One process note: my first attempt at step 1 landed in the MAIN repo
tree by mistake (an absolute-path slip past the worktree prefix) — caught
before any commit there, the diff was moved into the worktree via `git
apply` + `git checkout --` on the main tree's two touched files, and the
worktree's own first real commit (`7a4237f`) records the incident so it is
not silently lost from the history. `git status` on both trees confirms
main is clean and the worktree carries the intended diff.
