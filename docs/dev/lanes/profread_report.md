# [OPTLOOP.1.profile] — profread's delivery report

Lane `profread`, 2026-09-22, sonnet, docs-only, branch `lane/profread`
from `main`. Read `docs/dev/optloop/cycle1_profile.md` for the full
reading; this report is the delivery record.

## Task

Read the 12 I-85 profile transcripts
(`docs/dev/optloop/runs/2026-09-22-i85-405668e9/`) against
`cycle1_analysis.md` §3's own EXPECT lines, block by block (M1.a-M6),
using the bench executor's own reading (outbox O-44) only as a
transcription cross-check, never as a source of numbers. No new
mechanisms, no diagnosis beyond what the EXPECT lines themselves frame.

## What was read

- All 21 short transcript logs plus the two long (b)-read logs
  (`70_b2_p2info46.log`, `71_b2_diff.log`), read in full.
- `cycle1_analysis.md` §3 in full (every EXPECT line, its exact
  `file:line`), plus §0, §2.2 (the floor row) and §3.1 for the framing
  each mechanism's EXPECT block depends on.
- `pcrec-bench/bench/capability/NOTES.md`'s R6 rule (cited by name in
  §3 but not defined there).
- Outbox O-44 (`pcrec-bench/docs/dev/outbox_to_pcrec.md:3209-3260`), read
  in full, used only to cross-check transcription — every number in the
  delivered reading was independently recomputed from the transcript
  files, not copied from O-44's own arithmetic.
- D77 and D119 (`docs/dev/decisions.md`) for the landing-bar language
  cited in the brief.
- `pcrec-bench/docs/dev/known_issues.md:1270` (KB-27) for the (b)1 read's
  cross-reference.

## Findings beyond straight transcription

1. **A provenance discrepancy, not asked for.** The run's own directory
   name and README cite pin `405668e9`, but `00_setup.log:5,11,13` shows
   the worktree built at `69172a00` — one commit later. `git
   merge-base --is-ancestor` confirms `405668e9` is `69172a00`'s parent.
   `git show --stat 69172a00` touches only `docs/dev/dev_journal.md` and
   `docs/dev/plan.md` — nothing under `src/`/`cli/`/`lib/`/`tests/` — so
   every measurement is unaffected, but the stated pin is off by one
   commit from what was actually built. Recorded in `cycle1_profile.md`'s
   opening section.
2. **M1's floor gap is confirmed NOT a set-grain artefact, by direct
   recompute both ways.** `floor-byte`'s per-1-MiB rate and its set-grain
   SUM rate agree to four significant figures (0.01680 vs 0.01679); the
   same recompute on M1.b's own twins agrees with itself just as tightly.
   The ~2.17x gap between the stated 0.017 floor and the measured ~0.037
   twin floor is real and uniform across all five M1 rows — it explains
   the entire shortfall in every predicted collapse ratio on its own,
   rather than five independent baseline misses.
3. **M6's decomposition question is answered from the same log's own
   numbers.** `ns/attempt = steps/attempt × ns/step` holds by algebraic
   identity (not an independent check); the substantive finding is that
   `ns/step` is nearly uniform across the three witnesses (8.7% spread)
   while `steps/attempt` varies far more (46.8% spread) and tracks the
   overall ns/byte spread almost exactly — so M6's bucket is a
   per-attempt work problem, not a per-step dispatch-cost problem.
4. **Two target-cell anomalies are worth flagging to the manager
   directly** (both already in the closing table, restated here): M2's
   `evil-alt-nested` hand-twin is non-constant AND inverted with subject
   size (slower on the smaller subject); M3's `json-constant` hand-twin
   REGRESSES under its own mechanism (×1.10 slower), which the EXPECT
   block's own stated criterion reads as a refutation for that row.

## Verdicts, one line each (full reasoning and tables in cycle1_profile.md)

| mechanism | verdict |
|---|---|
| M1 `[OPT-REQBYTE]` | PARTIALLY CONFIRMED — real, uniform ~2.2x floor gap; one target row's baseline is non-flat (R6) |
| M2 `[OPT-ANCHOR-VM]` | PARTIALLY CONFIRMED — two of three witnesses clean; `evil-alt-nested` anomalous |
| M3 `[OPT-FIRSTSET]` | PARTIALLY CONFIRMED — one target row (`json-constant`) REFUTED by its own criterion |
| M4 `[OPT-ENDWIN]` | CONFIRMED — clean O(1) collapse and full correctness carve-out |
| M5 `[OPT-ATTEMPT-SPLIT]` | PARTIALLY CONFIRMED — large real speedup, misses its stated numeric target, real size cost |
| M6 (measurement only) | decides its own question: a per-attempt (steps), not per-step, cost |

## Validation

Docs-only lane; no build, no `make`, nothing under `src/`/`cli/`/`lib/`/
`tests/` touched. All arithmetic in `cycle1_profile.md` was computed
directly from the transcript files during this session (not carried over
from O-44) and is reproducible from the file:line citations given
throughout.

## Handback

Committed to `lane/profread`. Deliverables:
`docs/dev/optloop/cycle1_profile.md` (+ its `docs/dev/optloop/CLAUDE.md`
line) and this report (+ its `docs/dev/lanes/CLAUDE.md` line). Nothing
owed. Ready for the manager to review and merge.
