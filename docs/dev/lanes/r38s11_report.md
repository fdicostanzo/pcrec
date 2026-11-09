# r38s11 report — span_runs_sheet rev 1.1 (doc only)

STATE: complete. Branch lane/memfn-r38s. No code, no builds, no queue jobs.

## Summary

`docs/design/memfn/span_runs_sheet.md` rev 1 -> rev 1.1, applying re-check review 2026-11-09 r6 r38s2 as
ruled by main: F-A..F-O as text fixes (F-G recorded as a PLAN item instead), Q7 and the run pin RULED
in §6, a rev 1.1 revision-log table. Each edit is marked `[r1.1 F-<x>]` in the sheet. Nothing beyond the
review and the rulings was changed.

## Item by item

- F-A: §4.1 (first-match table for `@`), §4.3 (four `@`/`req_run` readers with fates; `req_run` and `req_run_maxoff` retire), §5.1 (population 2 split into 2a/2b, `emitted` example `a.*xabcdefghijkq`), §6 Q7.
- F-B: §4.2 (clip to the walk; why; the two cited artifacts).
- F-C: §2.5 (rate pick named as third decider, "picks nothing" withdrawn, counted in `decider_census`), §7 Q2, §6 P6 (placement-only pin).
- F-D: §1 Goal 2 (three callers with counts), §5 K38-1 check, §4.3 row.
- F-E: §2.2 (inputs restated as invariance, `site_kind` added; Job keeps the DEFINE's class via `pcrec_memfn_defined`; trace memcmp).
- F-F: §4.3 (four shadow records, witness rows and PICKS retire; C2/C4 successors).
- F-G: NOT a fix, per ruling; §6 P5 with its trigger.
- F-H: §1 Goal 2 and §4.1 REQ_BYTE row (stamp rendered from the fact; scan-index call moves into `pcrec_req_pick`).
- F-I: §2.4 C1, C2, C4; §3.5 W-K3; §5 K38-1 (plant observation, twin witness, S1107 deferred), K38-2a (plant C), K38-2 (S1107).
- F-K: §5.1 (`nterm` 0 and `need` 0 admitted on the derived run part only).
- F-L: §5 K38-2 column (S1700, S448, S1548, S280, S1546 suspected).
- F-M: §4.3 (checks/goldens/readers table, run recognizer, MFPRES re-record with K35 floor), §5.1 (`-fcomments` population 5).
- F-N: §2.1 (`_Static_assert(PCREC_MAX_REQ_RUN_SCAN <= MF_WSPAN_POS)`; `verify` removed from the `mf_pred` field list; `pres_pred_clear`'s refusals named, not a partial list).
- F-O: header (−23 scope), §2.2 (`req_pres_ask` callers), §2.5 (`ofs_window_of` cite), §2.4 and §3.4 (`--features all`).
- NOTED/DOC/PLAN: header and §4.4 (§12d, E2 neighbour paragraphs, R1 rule), §2.2 (round-trip implicit inputs), §5.1 (movers per (artifact, population) with overlap column), §6 P7 (`mf_class.run` as the shared reply type).

## Rulings applied

- Q7: `@` of `<PREFIX>_REQ_RUN` is a first-match table (pre-check reply's scan, else the window site's member, else no `@`); `req_run` retires into `req_whole_run` (§6 Q7, §4.1, §4.3).
- Run pin: whole run CLIPPED to the k-set walk's reach; `pcrec_run_pin`'s rate pick named the third decider; placement-only pin is PLAN P6 (§6 Q8, §4.2, §2.5).
- F-G as a PLAN item (§6 P5). Process change for the critic skill: not a sheet matter.

## Charter-vs-committed checklist

- Sheet edited and committed in the worktree: yes (one sheet commit with this report and the history-index line).
- Nothing applied-not: every F-id applied; F-G recorded as a PLAN item as ruled. Where the review left a fate to the build (e.g. `.whole` column and `keep`, refusal texts, post-change stamp values) the sheet says "stated/measured at K38-2/the build" rather than inventing it.
- Cites not re-verified against the build tree (doc lane, no builds): the review's file:line cites are carried as the review gave them.
- Final hand-back: SendMessage to main.
