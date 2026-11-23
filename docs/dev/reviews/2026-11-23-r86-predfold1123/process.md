# process.md — crit-predfold1123 (r86), coordinator notes

- 16:00 coordinator start. FREEZE lane/pred-rev28 = 026090af87cfe73b8c3a0c0d9baed1c660cca4ea. Base (last reviewed, r84) 014ebc42f.
  Lane start commit STARTF e420369c5: no predicate-doc diff vs 014ebc42f (checked).
- main HEAD at freeze 4ca2b82cf; main decisions.md/plan.md last commit 7d8a216d6.
- Record at freeze: docs/design/plan_row_bodies/COND-FAMILY.md (9545 lines); in-scope entries lines 8008..9420
  (transform-export question .. zero-open). After 9421: call-forms play-out, OUT of scope.
- Mirror: R/tree = git clone --shared at freeze, local lane/pred-rev28 pinned to the freeze (the model's QUOTES reads
  that branch by name: on the live repo it would read a MOVING branch). Denied files removed from the mirror's work tree.
- Lint at freeze: pass 7896 / fail 0 (L7 soft-cap WARNs only).
- Evidence full run started 16:05 in background (.coord/evidence_full.out).
- 16:08 evidence full run done in ~2 min: byte-identical to committed .out, 18/0. Copied to R/evidence_run_at_freeze.out. COMMON written.
- 16:09 launched 5 opus critics (ruling, examples, fixind, names, check), background, unnamed. All five returned in the
  launch turn (the Agent calls blocked ~7-15 min each despite run_in_background): ruling 8.0 min, examples 15.4 min,
  fixind 8.8 min, names 6.9 min, check 10.7 min. Every final reply undeliverable (expected); every file complete with
  CRITIC COMPLETE; lanecheck .done for all five. No resends, no nudges.
  Findings raised: RULING 12 (+ruling table, 49 entries), EXAMPLES 4, FIXIND 19, NAMES 9, CHECK 10 = 54.
  Overlaps: RULING-4=FIXIND-2; RULING-6~FIXIND-3; RULING-12=EXAMPLES-2; EXAMPLES-4=FIXIND-19; NAMES-1=CHECK-2;
  NAMES-3~FIXIND-8~FIXIND-13 (closing body vs caller's own label).
- 16:20 rulings re-diff at critic return: see below.
- 16:22 FREEZE DRIFT: lane/pred-rev28 moved 026090af8 -> 254b23aa0: 4 commits, record only, 3 OWNER entries after zero-open (call-forms play-out comments; 'label holes must be full and not partial'; repeat head / _ in a count hole). No ruling. main decisions/plan unchanged (7d8a216d6).
- 16:22 verifier (opus) launched over 19 grouped items; returned 16:31 (8.8 min), file complete (VERIFY COMPLETE):
  16 HOLDS, 3 PARTLY, 0 REFUTED, 1 NEW evidence defect (V19 -> B3). No REFUTED to re-run.
- 16:29 FREEZE DRIFT re-check: branch at a942d6f22; a RULING landed mid-round (label-hole-full), NOT homed in the
  subject -> hand mapping in the draft (no fresh critic, per section 3.1).
- 16:35 draft review.md written; critic texts + verify.md in review/. Time to draft: ~35 min from start.
- Per lens: RULING 12 raised / 12 verified-or-consolidated (all HOLD); EXAMPLES 4 / 4; FIXIND 19 / 19 (V9 PARTLY);
  NAMES 9 / 9; CHECK 10 / 10 (V18 PARTLY). Severity, consolidated: answer/design in documents 15 (A1-A15), evidence
  13 (B1-B13), marking 11 (C1-C11), doc 3, general form 4.
- Blinding: no leaks noticed. Denied files were removed from the R/tree mirror's work tree; critics used R/subject.

## Process observations
- The Agent calls with run_in_background returned in the launch turn (blocking 7-15 min); harmless here, the files
  were the delivery. All six final replies undeliverable, as expected.
- The evidence model reads the record via `git show lane/pred-rev28:...` (a branch NAME). A scratch `git clone
  --shared` with the branch pinned to the freeze made the re-run reproducible and kept critics out of the live repo;
  ~30 s to build, 271 MB.
- Two lenses (NAMES, CHECK) found the same `_` lowering defect from opposite sides (grid vs mutation). The lens
  table has no drill that targets "sugar vs its written-out expansion" directly.
- The verifier found a new defect (B3) while confirming a SUSPECTED gap: the advised idiom is accepted and empty.
- Five opus critics + opus verifier for a fold of ~50 record entries: all productive; none over-staffed. FIXIND was
  the widest (19) and carried the general-form questions well.

## Proposed changes
- Skill section 5 (design mode, COMMON): "When the evidence reads a git ref BY NAME, run it in a scratch `git clone
  --shared` inside the round dir with that ref pinned to the freeze, and remove the denied files from its work tree"
  (r86: QUOTES reads lane/pred-rev28).
- Lens table, mode closure row: add "EXPANSION drill: every new sugar form (a parameter mark, a placeholder) run
  against its documented written-out expansion; legality and answers must agree" (r86 NAMES-1/CHECK-2).
- Section 6.2 verifier brief: "a verifier that finds the evidence silent or empty on a shape it was asked to confirm
  files it as a NEW item" (r86 V19).
- RULING lens brief: "diff the ASKED statement (the question put), not only the Class restatement, against the
  documents: conservative edges live there" (r86 A1).

## Framework notes
- Coordinator pattern worked end to end in ~40 min wall for a 1,834-line diff: freeze + mirror + evidence re-run
  (~8 min), five critics in parallel (~15 min), one verifier (~9 min), draft (~10 min). The verifier grouping by
  root (19 items from 54 findings) kept it to one agent.
