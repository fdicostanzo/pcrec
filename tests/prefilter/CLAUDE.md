# tests/prefilter — [M4.6f] the D46 close-out for the PREFILTER axis

D46 (docs/dev/decisions.md) requires every strategy-selection point to be
OBSERVABLE (a stamp in the emitted artifact) and FORCEABLE (a flag that
overrides the selection, do-or-die where the forced strategy is impossible).
The `RX_VM_RUNGS`/`RX_VM_STRATS`/`RX_VM_PRUNES` family already has both
halves for their own axes (tests/rungselect/, tests/possessify/,
tests/mrl/); this directory gives `fit.prefilter`
(src/opt/select_engine.c, engine_m4.md §6.1/§4.7 — the DFA-erasure
forward+reverse pair the VM hybrid uses as its exact anchored-window
prefilter) the same pair: the `RX_VM_PREFILTER` stamp (`"hybrid"`/`"none"`,
src/gen/emit_vm.c) and the `-fprefilter`/`-fno-prefilter` force pair
(`PCREC_FORCE_PREFILTER`/`PCREC_NO_PREFILTER`, lib/pcrec.h,
src/opt/select_engine.c).

## Why a FORCE pair, not a deny-only flag

Every other member of D47.3's family (`-fno-possessify`, `-fno-revdet`,
`-fno-counter`, `-fno-length-prune`) is deny-only, and D47.3 rules that
deliberate: each denies a PER-QUANTIFIER strategy, so "force possessify on
THIS quantifier" has no addressing problem to solve because a quantifier
that wants it already gets it and a denial simply skips that ladder step
everywhere. `fit.prefilter` is not per-quantifier — it is ONE verdict for
the whole artifact, decided jointly with `--engine` (auto+captures turns it
on, `--engine=vm` turns it off as a side effect, R21 E-6). Before this
substep there was no way to ask for the OFF state under an otherwise-auto
selection without also forcing `--engine=vm`, and no way to ask for the ON
state under `--engine=vm` at all — exactly the coupling D46's own motivating
scenario warns about (a test built to pin one axis silently moves on
another). So both directions are independently reachable here.

## Why there is no `run_prefilterdiff.sh`

Every sibling directory in the D47.3 family pairs its structural script with
a differential (`run_possdiff.sh`, `run_rungdiff.sh`, `run_counterkdiff.sh`,
`run_mrldiff.sh`) because each introduces a new ALGORITHM whose correctness
needs a pcrec-vs-pcrec sweep. The prefilter is not new: its correctness (that
the hybrid's DFA-erasure window agrees with a prefilter-free VM run) is
already `tests/vm/run_vm_tests.sh`'s §3.7 differential, and its ceiling-form
interaction is `tests/mrl/run_mrl_tests.sh`'s territory. This substep adds
only the OBSERVABILITY and CONTROLLABILITY layer on top of an axis that
already existed and was already validated, so one structural script is the
whole of what the row owes.

## Files

- **run_prefilter_tests.sh** — the structural checks: the derived default
  both directions (auto+captures on, `--engine=vm` off); the force pair
  overriding it both directions; DO-OR-DIE refusal when `-fprefilter` is
  asked for a pattern with no VM artifact to attach to (`--engine=dfa`, or
  auto routing to the DFA because the pattern requests no captures) and when
  both force flags are given together; that `-fno-prefilter` never refuses
  on any engine choice; that a REDUNDANT force flag (one that agrees with
  the derived default) leaves the artifact BYTE-IDENTICAL to the same build
  without it (the same rule `emit_dfa.c`'s strategy-denial mask states for
  every D47.3 sibling); that `rx_info.flags` never carries either new bit
  numerically; that `--emit-ir`'s `; prefilter` listing line names the
  reason that actually fired (explicit deny vs. the `--engine=vm` side
  effect vs. forced back on); and a functional sanity check that a
  forced-on and a forced-off build still answer identically on a live
  subject — the axis changes MECHANISM, never the answer.

  **THE INDEPENDENT CONTROL**: every stamp assertion is paired with a read
  of the actual emitted `_prefilter(` FUNCTION DEFINITIONS (the private
  forward+reverse DFA pair `pcrec_emit_dfa_engine` writes), never the stamp
  text alone — a check that only re-read the macro would pass even if the
  stamp and the emitter's real behavior had drifted apart, which is the
  controls-sharing-a-source failure this project's memory records. **Per
  R28-1** (`docs/dev/reviews/2026-08-17-r28-mrl-landing.md`: ad-hoc,
  reverted sabotages do not count as validation — MRL shipped without
  permanent sabotage coverage the same way and had to add S58-S63
  retroactively), the two directions verified during this lane's own
  development are PERMANENT rows, `tests/mech/sabotages/S64_*.sh` and
  `S65_*.sh` (their own arm, `prefilter`, in
  `tests/mech/run_sabotage_matrix.sh`; see `tests/mech/CLAUDE.md`'s
  "[M4.6f] S64-S65" section for the measured fail counts) — removing the
  do-or-die refusal in `src/opt/select_engine.c` (S64) turns the two
  refusal checks red; dropping `PCREC_NO_PREFILTER`/`PCREC_FORCE_PREFILTER`
  from `emit_dfa.c`'s `strategy_denials` mask (S65) turns the mask check
  AND (as a bonus) both byte-identity checks red, because the leaking bit
  changed the emitted `.flags` value. Both confirmed DETECTED via
  `bash tests/mech/run_sabotage_matrix.sh S64`/`S65` before landing.

Maintenance: update this file when the check vocabulary grows (a new
prefilter form, e.g. islands' own D46 pair per plan row [ENG-ISL], would be
a DIFFERENT axis and belongs in its own directory the way this one is
separate from tests/rungselect/ and tests/possessify/, not folded in here).

## [DD-14 wave G] the LINKED-call witness, and the second control

The listing-reason rows moved to a RECURSIVE callee,
`(?:(?<g>x(?&g)?y)){0}a(?&g)b`, keeping the `{0}`-callee idiom. The old witness
`(?:(x)){0}a(?1)b` names an ACYCLIC callee whose group is also DEAD, so after
wave G it reaches the DFA engine and `--emit-ir` refuses it outright — there is
no `; prefilter` line to read, which is exactly how these went red.

**AND THE OLD WITNESS CAME BACK AS A SECOND CONTROL**, which is the row the
narrowing needs: under `--engine=vm` a SPLICED call must NOT claim the credit,
and the listing must name the FLAG. It exists because this section's original
defect arrived from the other side — the listing named a FLAG the caller had not
passed — and wave G briefly created its mirror image: `select_engine.c` narrowed
the prefilter VERDICT to `pcrec_has_linked_call` while `emit_vm.c` still computed
the REASON from `pcrec_has_call`, so a fully spliced call read
"NO (subroutine call)" where the honest answer is "NO (--engine=vm)". MEASURED,
fixed, and this row is what stops it drifting back. The reason text now reads
"NO (LINKED subroutine call)" and says why a spliced call is not one.

## [SEL-1] a FIFTH "off" route: the auto-selected prefilter's own DFA overflow

`auto`'s DFA-cap-overflow contract (plan row [SEL-1], Frank 2026-08-28): a
DFA build that overflows a cap (state count, table entries, K7's element
budget) is a SELECTION OUTCOME under `auto`, not a refusal, and when the
overflowing build was the auto-selected PREFILTER (rather than the engine
itself), the prefilter is DROPPED — `fit.prefilter` comes out `false`,
`RX_VM_PREFILTER` stamps `"none"`, exactly as `has_bref`/`has_call` above.
`--engine=dfa` and `-fprefilter` stay do-or-die with today's diagnostic,
UNCHANGED (`src/opt/select_engine.c`, `src/core/compile.c`'s retry).

**IT REPEATS THE SAME DEFECT SHAPE the backreference and call routes were
each fixed for, and it needed the identical fix**: with no arm of its own,
`vm_render_listing` (src/gen/emit_vm.c) fell through to `"NO (--engine=vm)"`
for a pattern compiled under plain `auto` — a diagnostic naming a flag the
caller had not passed. Fixed the same way, tested in the same place (ahead
of both flag routes, since this is a THIRD thing no flag explains): the
reason text embeds `cx->dfa_overflow_why`'s own cap name, e.g.
`"NO (dfa overflowed: >32000 states) -- ..."`, computed into a local buffer
(`sel1_prefilter_reason`) before the ternary because — unlike the static
arms — it has to interpolate the runtime cap text.

**THE WITNESS IS THE SAME PATTERN [SEL-1]'s OTHER TESTS USE** (`tests/vm/
run_vm_tests.sh` §3b, `docs/spec/tuning.md` §2.11/§2.5):
`\b(?:ERROR|FATAL|CRIT)\b.{0,200}?\b(?:timeout|timed out|refused|denied|
unreachable)\b` under `--features all`, whose capture-erased forward DFA
overflows `PCREC_MAX_DFA_STATES_TABLE` (32000 states). The force-on control
uses `--engine=vm -fprefilter` rather than the generic `check_refuse` helper:
bare `-fprefilter` (no `--engine`) hits a DIFFERENT, earlier refusal on this
witness ("-fprefilter requires the VM engine...", since the pattern has no
capture and would otherwise select the DFA outright), which also contains
the word "prefilter" and would make `check_refuse`'s generic control pass
for the wrong reason; forcing `--engine=vm` routes past that so the actual
DFA-cap refusal (whose text does not contain "prefilter" at all) is the one
reached and checked verbatim.

**NOT YET SABOTAGE-COVERED**, unlike S64/S65 above for the backref/call
routes' own do-or-die and stamp-mask properties — flagged rather than added
silently; a future lane should give this arm the same permanent-row
treatment R28-1 asks for.

## [OPT-4.2] the nullability decline, off the rung entirely (2026-08-31)

[OPT-4.1] declined a ladder RUNG's count-collapsed rescue when the collapsed
language was nullable; [OPT-4.2] generalizes the SAME predicate to the
ORDINARY hybrid path (`collapse_reason == CR_NONE`, no rung ever ran), where
the pattern's own EXACT language admits the empty string and the
unconditionally-built exact prefilter could never dismiss a position. Four
new rows: `'(a)*'` (a PRE-EXISTING population — captures force the VM, the
pattern's own language is nullable with no [OPT-5] growth needed to reach
it, distinct from tests/resource's `'(a|b){0,30000}'` witness for the
population [OPT-5]'s scan edge grew) declines and stamps `RX_ENGINE_SEL
"declined-nullable-default"` with zero `_prefilter(` symbols; the existing
`'(a)b'` non-nullable control (check 1's own witness) is asserted UNCHANGED
(`"selected"`, not the new value); `-fprefilter` overrides the decline on
`'(a)*'`, [OPT-4.1]'s own asymmetry carried over; and the `--emit-ir`
listing gets its own worded arm (`"NO (nullable exact language)"`, no
"offered and declined" language since there is no rung to have offered
anything).

**NOT YET SABOTAGE-COVERED**, same flag as the [SEL-1] section above.
