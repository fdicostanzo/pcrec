# o64read: reading [B108] / O-64 (`[OPT-LITSCAN]` S2a at `a32bc86e`) — lane report

Lane `o64read` (opus), 2026-09-28. Branch `lane/o64read` from main
`768247dd`. The lane is docs only: no timing runs, and nothing under
`src/`/`tests/`/`docs/spec/` changed. Only compile-side probes were run:

- pcrec `a32bc86e`, built from a `git archive` in scratch;
- artifacts assembled by the bench box's x86 gcc-15, with the source piped
  over ssh stdin and nothing written there.

## Deliverables

1. `docs/dev/optloop/b108_reading.md` contains:
   - the per-prediction verdicts (18 rows);
   - the compile-side mechanism attribution (§1);
   - the D119 bar (NOT met on the named population);
   - the recommendation (KEEP, and FILE F5/F6);
   - the dense-match pre-check finding with the F6 draft (§5);
   - seven bench questions (§6).

   Its instruments are in `docs/dev/optloop/b108/`.
2. The pre-check ×2-×9 finding is placed in the existing `[OPT-LITSCAN]` row
   as tail F6, beside F1. Draft text is in the memo's §5; `plan.md` was not
   edited.
3. `docs/dev/memcmp_lowering_study.md` §12 adds the dated x86 gcc-15 column,
   from the bench's measurement file.
4. `docs/dev/summaries/2026-09-28-b108-exec-summary.md` is written, and the
   `summaries/CLAUDE.md` and `optloop/CLAUDE.md` entries are added.
5. The bench questions are in the memo's §6.

## STATE AT HANDOFF

- The deliverables are committed on `lane/o64read`, in four commits:
  memo+instruments, memcmp §12, summary+CLAUDE.md, and the F5 wording plus
  this report.
- Validation is not applicable (docs only). The probes' outputs are
  archived in `b108/transcript.txt`.
- **OWED by the bench** (not this lane): capability × `pcrec-auto-nolitrun`
  with the roster fixed. The seven P2 FLAT cells stay OWED until it lands;
  revisit the keep/deny recommendation then.
- For the manager's hand at the stock-take:
  - record F5 (the named population's codegen/placement-only effect, and the
    `L ≥ 3` narrowing candidate with its twin trigger);
  - record F6 (the pre-check per-call price) in the `[OPT-LITSCAN]` row;
  - relay the §6 questions via pcrecdev2.
