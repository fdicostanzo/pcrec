# archdense2 report: review r49 filed; dense_hit_arch.md DRAFT rev 2 (after review r49)

## STATE AT HANDOFF

STATE: done. Lane archdense2 (opus), branch lane/archdense2, cut from lane/archdense @ 5dcc98dfc. Commits: 2a702da14
(review filed, first as r48), a7bde04dc (renumbered r48 -> r49, ruling R-1), 622707bf1 (the note's rev 2), then this
report and the lanes history index line. Tree T for the note is unchanged: 57fcb5737 (no finding needed a later
commit). Architecture only: nothing under src/, cli/, lib/, memfn/, tests/ or scripts/ was edited; the register in
docs/dev/guide/architecture.md, the skill and the guide were not edited; no make, no suite, no timing, no queue job,
no binary run (the WITNESS in the note is rev 1's, labelled). Doc checks run directly in the worktree:
`tests/plan_lint/run_plan_lint.sh` and `tests/spec_history/run_spec_history.sh`, 0 failed each after every commit.
Rulings file `docs/dev/lanes/archdense2_rulings.md`: re-read before each commit and this report; last R-n applied:
R-1 (the review number is r49: files `git mv`ed, the review header, its directory CLAUDE.md, the reviews index
line and the note's header read r49; the copied `dispositions.md` is unchanged and its directory CLAUDE.md says its
"r48" names this review). Premise test passed (the note's last commit was 5dcc98dfc; 12 groups A-L in the draft).
STOP RULE: did not fire; no ruled disposition was contradicted by the tree or the record. Process changes C-1..C-7
were HELD by the manager and not applied.
OWED: none
DELIVER FILE: its `files:` line separates the two paths with a space, and lanecheck splits on `;`, so it reads them
as one missing path. Both paths exist and are committed (`git ls-files` lists each); the deliver file was not edited
(manager-owned).

Filing (part 1): `docs/dev/reviews/2026-11-18-r49-archdense.md` is the coordinator's draft at its current text (N =
49) with a RULED line after each group's PROPOSED disposition, verbatim from the dispositions file (K and L share
one ruling), the verdict RULED line, and a pointer from the "Manager rulings needed" line. The directory
`docs/dev/reviews/2026-11-18-r49-archdense/` holds the five critic texts, SITEMAP_step1_sites.md, verify.md,
COMMON.md, process.md (the coordinator's .coord/process.md) and dispositions.md, with a CLAUDE.md. One change to a
copied file: verify.md's plan line cite became the row tag (PL14 failed on it). docs/dev/reviews/CLAUDE.md gained the
index line; to stay under 12 KB its oldest index entry (r14-predspec12) moved to that directory's NOTES.md, as
file47 did.

## FINDINGS APPLIED

| id | group | applied? | where in rev 2 |
|---|---|---|---|
| AGGREGATION-1 | B | applied | S15 (the scan's prior admission) added; S12 SHARED with S4; K105's cause stated (Requirements read, S12, S15) |
| AGGREGATION-2 | A | applied | cadence family counted as four askers; P2 PROPOSED with this feature as its event, plus the not-one-family paragraph and its rejoinder |
| AGGREGATION-3 | C | applied | S6 names the shared site, define-phase fields, `use`, DELEG_SITES PRE; U1 split into U1-k / U1-p |
| AGGREGATION-4 | G | applied | S7: pcrec branch B is a limits.def row (D90) unless the design argues the vm_reseed_cal/PLACE precedent |
| AGGREGATION-5 | A | applied | general form restated with WHAT vs WHEN (cadence); goal 1 bullet |
| SITEMAP-1 | H | applied | S16 (`emit_req_handoff_rest` declaration) |
| SITEMAP-2 | H | applied | C7 reworded (5 world reads + `req_start_set`'s forced deny); S9 names it |
| SITEMAP-3 | D | applied | C10 replaced (serves declarations, leftmost checks, renderers); hazard direction fail-closed |
| SITEMAP-4 | H | applied | C-HANDOFF: 42 files, the design reads the full output; REENTRY_* and run_handoff_reach.sh named |
| SITEMAP-5 | H | applied | C0 gives 7; C12 filled (the walk) |
| SITEMAP-6 | B | applied | S12 class SHARED with S4, "scan byte-identical or timed" as a design constraint |
| SITEMAP-7 | A | applied | S14, the built landmark walk, AS-IS; PLANNED ROWS reworded (stage 1 BUILT, tag stale) |
| SITEMAP-8 | H | applied | Seams spec row: `match_api.md` §6.3.4 `"handoff"` row, conditional; limits.md §8.5¶3a and facts_listing.md §4.1.2¶8b listed as unaffected |
| REGISTER-1 | I | applied | H-ABI (carried) and H-COUNTS (carried where it fires) rows |
| REGISTER-2 | I | applied | A-HYB, H-SITES, A-READS rows, one reason each |
| REGISTER-3 | I | applied (reason only) | A-SEAM reason restated against the tag trigger; the refuted sub-claim not used |
| REGISTER-4 | I | applied | "No other unit lands first, UNLESS ..." the per-hit lever case, tied to the gate |
| REGISTER-5 | NOTED | applied (optional line) | P1 says it is the guide's implement-then-replace open row |
| FIRSTUNIT-1 | C | applied | U1 split by lookahead-home; Seams "none new" corrected per branch |
| FIRSTUNIT-2 | C | applied | U1-p: a kit ROW event (serves coverage) plus pcrec movers, its own gate |
| FIRSTUNIT-3 | D | applied | U1 gate adds emit_sweep identity, arms.tsv, G2 quick; D157 precedent restated |
| FIRSTUNIT-4 | D | applied | 12 `[FLD_ret_pred]` declarations and the leftmost checks listed (C10); D27-blinded G2 reference as a design-step requirement |
| FIRSTUNIT-5 | E | applied | two request texts, facts and both comparators only |
| FIRSTUNIT-6 | F | applied | round-trip cell per branch; A-PLAN disposition per the manager's ruling |
| RULING-1 | E | applied | NOTE 3 quoted with "leading candidate"; reading and hand-off say "the owner's leading candidate" |
| RULING-2 | K | applied | NOTE 1's body attributed to the manager's QUEUED record; NOTE 3's owner words; skill §3.2 cited; reading grounded on NOTE 2 |
| RULING-3 | I, J, K | applied | the speed gate quoted in the owner's words with its three allowances; lever line (REGISTER-4) |
| RULING-4 | E, J | applied | no ASK about the page size; streaming a future unscheduled fact; streaming question became a reading |
| RULING-5 | J | applied | split-deny a CONDITIONAL CONFIRM under the design step, with the bench pin, audit item (c), bit 46 KEEP / row 15's mechanism |
| RULING-6 | B, J | applied | scan-reentry-too became a reading with K105's quoted lines |
| RULING-7 | E, J, K, L | applied | ¶7a quoted in full; D146 add. 1 = ISA facts; lookahead-home narrowed; no "NOTE 3 replaces NOTE 1" |
| RULING-8 | E | applied | ¶8c timings labelled pre-K38-2; the re-measure is the measurement card's baseline step |
| RULING-9 | K | applied | (a) D151/D148 Q6 + D158 cited; (b) D147 add. 10 Q53; (c) audit quote without "or re-ask"; (d) twelve rows; (e) [REQ-HANDOFF-L1] in plan_completed.md |
| RULING-10 | L | applied | Goal 2 line (held); "Traded against: none" reworded; "both rows ask the weaker fact" moved to the hand-off as an option |
| (verifier) prefilter declaration | H | applied | S16 (the hybrid prefilter's `landmark_position = search_from`) |

## WHAT MOVED IN THE NOTE

- Header: DRAFT rev 2 (after review r49); FORM count 5 -> 7 decision sites (S15, S16 added); T unchanged.
- Goals: goal 2 HELD added; "traded against" now none (tension = sparse-hit case); the gate quoted in the owner's
  words; gate-comparator restated as the record's reading (both, for two decisions).
- Requirements: the three NOTES verbatim with attributions; the reading grounded on NOTE 2 and D157 (method is the
  kit's; NOTE 3's blocks are the leading candidate; its B sentence the one owner constraint); streaming and scan
  re-entry as readings.
- Site map: S6 rewritten (shared site, define phase, use kind, PRE row, budget column, hazard population); S7 gains
  B's homes per branch; S9 gains `req_start_set`; S12 SHARED; new S14 (walk), S15 (scan admission), S16 (kept-hit
  declarations). Commands: C0 fixed, C7 reworded, C10 replaced, C12 and C18-C23 added.
- Register: A-SEAM reason restated; A-PLAN per the manager's ruling; A-HYB, H-SITES, A-READS, H-ABI, H-COUNTS added;
  row 15 "rides row 15's mechanism", not [FLAG-DEMOTE]'s set; P2 (cadence rule) PROPOSED with the not-one-family
  argument.
- Remodels: U1 split into U1-k (kit seam event) and U1-p (kit row event + pcrec movers), each with gate, checks,
  separability; two request texts; the lever condition on "No other unit lands first".
- Hand-offs: method/uses option, S6 home and budget, A-PLAN condition, B with the owner's named sources, the give-up
  cites, split-deny confirm, the measurement baseline step, the 42-file check list.
- Owner questions: five -> one (lookahead-home, narrowed).

## OPEN QUESTIONS FOR THE OWNER

- **lookahead-home**: does the owner-stated B ("B is a tuning constant: derive it from a SYSTEM constant (Frank)")
  bind the kit's method or pcrec's loop? TODAY `tuning.md` §2.41¶7a (quoted in full in the note) keeps the origin and
  the re-entry pcrec's and gives the kit the presence; NOTES 1-2 and D157 put the method with the kit. EXAMPLE:
  `[^@ ]+@x` under `--engine=vm` over 1 MB of ` @x` asks the kit about every 3 bytes. WHY: the kit's method gives
  U1-k (a seam event, B the kit's); pcrec's loop gives U1-p (a kit row event plus pcrec movers, B a limits.def row).
  LEANING: the kit's method; pcrec owns the compare and the stop.

## COMMANDS

- Premise: `git -C worktrees/archdense2 log -1 --format=%h -- docs/design/dense_hit_arch.md` printed 5dcc98dfc;
  `grep -c '^### [A-L]\. ' /var/tmp/pcrec-pcrec/scratch/crit-archdense/review.md` printed 12.
- Filing: the scratch script `$PCREC_TMPDIR/scratch/archdense2/file_review.py` (inserts each group's RULED line).
- Every site command in the note was run at T = 57fcb5737 via `git -C /home/pcrec/projects/pcrec grep|show`
  (C0 7, C7 13, C10 12 lines/9 files and 3+3 leftmost lines, C12 the walk, C19 4 and 4, C20 2, C22 81, C23 2 and 5,
  C-HANDOFF 42).
- Doc checks: `bash tests/plan_lint/run_plan_lint.sh` and `bash tests/spec_history/run_spec_history.sh` from the
  worktree (subshell), 0 failed; `scripts/check_claudemd_size.sh` via the pre-commit hook, within limits.
