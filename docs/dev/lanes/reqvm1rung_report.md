# reqvm1rung — the size-cap ladder's `drop-handoff` rung ([REQRUN-VM])

Lane reqvm1rung (opus), 2026-10-28, worktree `worktrees/reqvm1`, branch
`lane/reqvm1`, on top of d1f7be82e. Build go: Frank 2026-10-27 "Yes go both
halves." ([REQRUN-VM]); this rung completes that build.

## Summary

- **The problem.** [REQRUN-VM] made the VM-only artifact larger: its attempt
  loop now carries handoff code. So a pattern near the size cap that the ladder
  used to rescue now REFUSES. `seq-pfcd2` (`(\bcat\b){2,}[a-z]\d`, utf8, lowsize
  cap 30,000) runs `prefilter-collapse > drop-prefilter`, and the VM-only result
  is 30,710 bytes, so it refuses. Main ships it.
- **Premise test, reproduced on d1f7be82e.** The default compile refuses (rc 1,
  rows `prefilter-collapse > drop-prefilter > refuse`). With `-fno-req-handoff`
  it compiles (rc 0). Both as the brief expected.
- **The fix is ONE new row of `fit_rungs[]`, `drop-handoff`** (src/core/compile.c),
  placed between `drop-premul` and `drop-prefilter`.
  - It gives up the VM-side handoff rows this lane added: the attempt loop's
    `handoff-attempts`/`handoff-attempts-entry`, and the hybrid prefilter's
    re-entry.
  - It applies only where the refused attempt EMITTED one of those rows
    (`Job.req_handoff_vm`, written by the emitter at the text it writes).
  - When it fires, the retry declines those rows (`Ctx.req_handoff_dropped`,
    seeded from the fired record, as `drop-end-mark` does).
  - A hybrid keeps its first-start handoff. Main shipped that, and it has no rung.
  - A DFA artifact's handoff is untouched.
  - No new flag bit. abi stays 91: the rung changes emitted text only where it
    fires.
- **seq-pfcd2 compiles again**, with rows
  `prefilter-collapse > drop-prefilter > drop-handoff`. Its artifact is
  byte-identical to the caller's own `-fno-req-handoff` artifact (diff: only the
  `#include` basename).
- **The `(\p{Xwd})x` mover** (utf8, shipped caps) now runs
  `drop-handoff > drop-prefilter`. The final artifact is main's form: the VM with
  no prefilter and `RX_REQ_HANDOFF "none"`. `RX_VM_PREFILTER_WHY` quotes
  `hybrid 1041155 > 1000000`; main quotes 1041150 and the lane before this rung
  1040199.
- **New fallback-table witnesses:**
  - `seq-hodrop`: the rung before the prefilter drop.
  - `seq-horef`: `--size-cap=refuse` denies the rung.
  - `note-ho`: the rung's stderr note.
  - Re-pins: seq-pfcd2 back to `ok`, and att-scpfd's giving row.
- **Spec in the same commit:**
  - `limits.md` §8.4: table row `4a`, ¶2, a new ¶2b, and ¶3 "all eight".
  - `limits.md` §8.5: a new ¶3a, ¶5 and ¶6.
  - `tuning.md` §2.41: a new ¶9b.
- **Sabotage S1708-S1714**: seven plants, each DETECTED by plant against the
  witnesses. S238 re-aimed (SAB_COUNT 3 -> 4).

## The rung

**Position, by the table's own rule.** `fit_rungs[]` orders its rows by
measured run-time cost, cheapest first. The engine scope makes the order bind
only within one engine (limits.md §8.4¶2; the comment block above `FitSel`).
The VM's rows are:

| row | measured cost |
|---|---|
| `unroll-rescue` | ~1.03-1.06x |
| `prefilter-collapse` | ~1.03x |
| `drop-prefilter` | up to ~4x (pfdrop_report.md §2) |

What the handoff rows buy is measured in reqvm1_report.md "Measurement":

- bench subst case 2 (hybrid re-entry): x1.61 in instructions:u;
- case 7 (VM-only attempt loop): x2.53.

So giving them up costs at most ~2.5x. That is more than the collapse and less
than the prefilter drop, so the row goes after `prefilter-collapse` and before
`drop-prefilter`. It sits after the DFA-only rows `drop-anchored`/`drop-premul`
because those are engine-disjoint from it, which leaves the order between them
free. The spec label is `4a`, so every existing number is kept. Wall time was
UNMEASURED by reqvm1. The ranking uses instruction counts, as reqvm1's
measurement card does.

**Two forms, one row.**
- On a hybrid that carries the prefilter's re-entry, the row is asked before
  `drop-prefilter`, as above.
- A VM artifact with no prefilter carries the attempt-loop rows. That artifact
  exists only after `drop-prefilter` (or a [SEL-1] drop, or with no prefilter at
  all), so there the row is reached after the prefilter drop. seq-pfcd2 is that
  case.

The first-match walk needs no special arm for either. The row applies wherever
the refused attempt carried the rows.

**Spelling.** The rung is a Ctx field, not the caller's flag OR'd in (the way
`drop-premul` ORs its flag). OR-ing `PCREC_NO_REQ_HANDOFF` would also deny the
hybrid's first-start `handoff` row, which main already shipped, so the retry
would give up more than this lane added. The field follows `drop-end-mark`'s
precedent (`Ctx.end_mark_dropped`, from the fired record).

**Own deny.** The code has `.deny = 0`, and the spec column reads
`-fno-req-handoff` (the whole form). Under that flag the contributor does not
exist, so the row never applies. A deny bit on the row would guard an
unreachable case. This is the convention of `drop-end-mark` (`-fno-rev-end-onewalk`)
and `unroll-rescue` (`-fno-size-term`).

**Cells:**

| cell | value | why |
|---|---|---|
| degrading, fof | `true`, `IN` | `--size-cap=refuse` denies it |
| ENGINE_SEL cells | `size-cap-retry` | an artifact the ladder degraded says so |
| carry | none | `VM_PREFILTER_WHY` must keep quoting the HYBRID that `drop-prefilter` refused; a later VM-only attempt is no hybrid. seq-pfcd2's WHY reads `hybrid 30089 > 30000`, as before. |
| restart | `true` | the VM's figures change, so the size term restarts, as for the prefilter drop |
| repeat | once | |
| retries | 1 | |
| note | yes | |

**Attempt bound.** `COMPILE_MAX_ATTEMPTS` gains one retry and a fourth
ladder run (`3 + 4 * (N + 1) + ... + 1`). The trace build's self-check holds it
equal to `fit_attempt_bound()`.

**Legal sequences.** Six pairs are added to `fit_seq_legal[]`:

- `end-mark > handoff`
- `collapse > handoff`
- `handoff > prefilter`
- `prefilter > handoff`
- `sel1-collapse > handoff`
- `sel1-drop > handoff`

The last two are needed because a [SEL-1] retry's VM artifact can carry the
attempt-loop rows, or the collapsed hybrid's re-entry.

**Answers.** Answer-identical. The retry is the artifact without optimization
rows that are answer-identical by their own contract (tuning.md §2.41¶9a).
Like `drop-prefilter` (tuning.md §2.5¶4), it may change which budget binds
first, in ¶9a's one direction. That is precedent, not a new kind of movement,
so the STOP rule did not fire.

**Finding (not acted on; proposed for the manager).** On a hybrid the row
cannot know in advance whether dropping the re-entry shrinks the artifact.
`(\p{Xwd})x` is the measured case:

- the re-entry displaced a start-byte row and made the hybrid SMALLER
  (1,040,199 B against 1,041,150 B without it);
- so the drop grows the hybrid, and the attempt is wasted (one extra 1 MB-class
  compile);
- the prefilter drop then follows, and the VM-only artifact no longer takes the
  attempt-loop rows (the field persists).

The result is main's form, never worse than main, but it can be worse than the
lane before this rung: a hybrid-with-re-entry pattern whose VM-only form would
have kept its attempt rows. The mover census measures that population as 0 at
the shipped caps (its one `dropped-hybrid-size` cell has a one-byte landmark, so
no attempt rows). A per-form refinement would need a row that can fire once per
form (hybrid, then VM-only), which breaks the table's once-per-row record bound.
I recommend filing it unscheduled with that census as the trigger (D77).

## Spec hunk

- `docs/spec/limits.md`:
  - §8.4 table: new row `4a`, `drop-handoff`, engine VM; gives up "the jump to
    the necessary run's next occurrence; a hybrid keeps its first-start
    handoff"; own deny `-fno-req-handoff` (the whole form).
  - §8.4¶2: the VM rows are now 1, 2, 4a and 5.
  - NEW §8.4¶2b: where the rung applies, its two forms, once per compile, and
    budget movement as for rung 5.
  - §8.4¶3: "all seven" becomes "all eight".
- `docs/spec/limits.md` §8.5:
  - NEW §8.5¶3a: the stamps rung 4a leaves (`DFA_PREFILTER` off `"handoff"` in a
    hybrid's prefilter; `REQ_HANDOFF "none"` on a VM artifact with no
    prefilter).
  - ¶5: `size-cap-retry` whenever rungs 2, 3, 4, 4a or 5 fired.
  - ¶6: rung 4a prints a note.
- `docs/spec/tuning.md` §2.41: NEW ¶9b, "pcrec may give up the VM-side rows
  itself on a size-cap refusal". It is §2.13¶4's shape.
- Both contents blocks were regenerated (`scripts/spec_toc.py`). The pre-commit
  spec check passed 70/0.
- Other readers of `fit_rungs`, found by grep:
  - the `--list-axes` axis `fallback` is generated from the table
    (`pcrec_fit_table_row`), so it lists the row with its `fit_act_verb`;
  - `tests/codegen/run_fallback_table.sh` re-pinned (below);
  - no `--emit-facts` row or `_VM_PREFILTER_WHY` cell names the rungs (the row's
    `pfwhy` cell is NULL);
  - design docs (`dec_fallback.md` and its listings) are records and were not
    edited.

## Tests and sabotage

**`tests/codegen/run_fallback_table.sh`.** Before the change: 145 passed,
1 failed (seq-pfcd2). After the final edits: 150 passed, 0 failed, then
`make test-fallback-table` green (counts under Re-pins and STATE AT HANDOFF).

- seq-pfcd2: `ok 'prefilter-collapse@size > drop-prefilter@size > drop-handoff@size'`,
  plus `fstate seq-pfcd2 3 'restart=1'`.
- NEW seq-hodrop: `trplain ok 'drop-handoff@size > drop-prefilter@size'`
  `(\p{Xwd})x` utf8, plus `fstate seq-hodrop 1 'restart=1'`.
- NEW seq-horef: the same pattern under `--size-cap=refuse`, `refused 'refuse@size'`.
- NEW note-ho: the hand-written `N_HO` note line, then `N_PF`.
- att-scpfd re-pinned (see Re-pins).

**Sabotage.** Each row was validated by plant: a scratch copy of the tree, both
trace compilers (trplain, trlowsize) built, and the three witnesses run.

| row | plant | how it shows up |
|---|---|---|
| S1708 | the rung never applies | seq-pfcd2 refuses; seq-hodrop loses its first row |
| S1709 | retry not told the rung fired | CANDORACLE fit-once on seq-pfcd2 and seq-hodrop |
| S1710 | restart cell false | the trace build's self-check refuses every compile (bound drift) |
| S1711 | attempt rows not recorded by the emitter | seq-pfcd2 refuses |
| S1712 | hybrid re-entry survives the drop | fit-once on seq-hodrop |
| S1713 | attempt rows survive the drop | fit-once on seq-pfcd2 |
| S1714 | row not degrading | seq-horef reads `drop-handoff > refuse` |

- Each row's detector is arm `fallbacktable`.
- Each row's `SAB_REACH` checks that the unplanted tree prints the rung's note
  on `(\p{Xwd})x`.
- Every sabotage anchor in the tree was re-counted against its `SAB_COUNT`
  (a scratch script over all rows):
  - S238's anchor (`.cells = { { ESEL_SIZE_CAP_RETRY, ESEL_SIZE_CAP_RETRY }...`)
    now matches 4 rows; re-aimed to SAB_COUNT=4, intent unchanged.
  - S1707's anchor was kept intact by placing the new decline AFTER the
    `req_use_read` line, so no re-aim.
  - Every other anchor resolves once.
- The full mech run of these rows (and a REACH_ONLY pass over the widened
  handoff/fallback family) is OWED: queue job 651.

## Re-pins

- `tests/codegen/run_fallback_table.sh`:
  - seq-pfcd2 is back to the compiling form, with the new rung in its row
    sequence. This reverts 9e8066578's `refused` re-pin.
  - att-scpfd now reads `size-cap-retry from=drop-handoff` (its last attempt
    now follows the third fired row; the witness refuses on main too). S626's
    plant (`fit_seq[0]`, prefilter-collapse) is still detected by it.
- `tests/mech/sabotages/S238_size_drop_unstamped.sh`: SAB_COUNT 3 -> 4.
- No abi move (91 stays, provisional). Nothing changes where the rung does not
  fire: the predicates read a field that is false unless the row fired. The
  owed census (job 650) checks this against main.
- No corpus file was changed, so there is no rxtsource census move.

## STATE AT HANDOFF

- Branch `lane/reqvm1`. Commits on top of d1f7be82e: 6e1eada8f (the rung,
  spec, tests, sabotage) and the report commit.
- Rulings file `reqvm1rung_rulings.md`: empty at every checkpoint, so no entry
  was applied.
- Local validation, COMPLETE for these sections (this box, nice, unlocked,
  on 6e1eada8f; logs /tmp/claude-1001/reqvm1rung/v_<target>.log, verdict
  from make's `*** [test-` lines, none):

  | section | result |
  |---|---|
  | `make test-fallback-table` | 151 passed / 0 failed |
  | `make test-codegen` | 19/19 scripts, 0 failed |
  | `make test-registry` | 79 passed / 0 failed in its last group |
  | `make test-memfn-arch` | 17 / 0 |
  | `make test-rxtsource` | 298 / 0 |
  | `make test-spec-history` | 11 / 0 |
  | `make test-claudemd-size` | 13 / 0 |
  | `make strict` | clean |

  The suites left the tree clean. The size_ladder_prefilter_drop.rxt
  witnesses' sections (test-uprops-utf8 §5, test-resource [PF-DROP]) are in
  job 650's make test. Their `(\p{Xwd})\b` resource witness was checked by
  hand: the rung does not fire there, and the artifact is still `-fno-prefilter`'s
  but for the two stamps.
- OWED (queued 2026-10-28, not run):
  - `650-reqvm1-test`: build, strict, the movers census vs main 490bc2baf
    (trailer `movers: DONE cells=... unexpected=0`), then the full make test.
  - `651-reqvm1-mech`: S1700-S1714, S238, the fallback-table rows S423 S626
    S630 S633 S638 S648 S696, and reqvm1's re-aimed and handoff-family rows;
    first a REACH_ONLY pass (176 rows). Cap 21600.
  - `652-reqvm1-axes`: the axes sweep plus the form census. Cap 18000.

  Each job's `--dry-run` passed before `scripts/boxqueue add`, which queued
  all three (`boxqueue status`: pending). The job scripts
  are copies of 630/631/632 with the ids, caps and descriptions updated.
- For the manager:
  - the per-form refinement finding (The rung, last paragraph);
  - the D/K numbers proposed: none needed.
