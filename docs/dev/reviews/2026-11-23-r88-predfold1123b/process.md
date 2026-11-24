# r88 predfold1123b — coordinator process record

## Freeze (2026-11-23 20:22 EST)
- SUBJECT lane/pred-rev28 = d3ca4a5ef (git rev-parse of the branch, worktree HEAD agrees). Scope diff 7b61fd62a..d3ca4a5ef -- docs/design/predicates/ (6 files, +465/-137).
- Build tree (main HEAD at freeze): 8ce5a9b92; decisions.md/plan.md last commit on main: aa75d837e. Design-only subject (no code cited by path in the fold).
- Record: docs/design/plan_row_bodies/COND-FAMILY.md at d3ca4a5ef, in-range = lines 9421..10134 (after zero-open at 9402, through label-doors at 10107). COND-FAMILY.md is byte-identical between the model's pinned 89d26b6b3 and the freeze (git diff empty).
- Round dir copies: R/subject (6 docs, doc_format.md, COND-FAMILY.md, record_in_range.md, two diffs), read-only. R/tree = shared clone (git clone --shared --no-checkout of the main repo, sparse checkout of /docs/ + scripts/*.py with every denied path excluded), detached at d3ca4a5ef, working files chmod a-w.

## Evidence re-runs (blind to critics: .coord/)
- lint in worktree: `pred_doc_lint: checks passed 8502, failed 0` (one WARN L7 parked.md size). In R/tree: 8496 passed, 0 failed (L10 ratchet absent: docs/dev/pred/ excluded).
- model full: last line `predfold1123b_model: 18 checks, 0 failed`; WALL ~6 s (20:23:14 -> 20:23:20). Non-indented lines identical to the committed .out.
- plants (=all): last line `predfold1123b_sabotage: 25 plants, 0 not caught`; wall ~82 s; plant lines identical to committed.
- COORD NOTE C-1 (not told to critics): SUCCESSOR's 13 predecessor models ALL end in a load-time TRACEBACK (12 on the rx.digits assertion, digest b024bdc4e170; predarr and predscope on their own readers) and are all declared superseded; no predecessor check runs. The declared reason says "every check it ran is re-run here through its loaded engine". Test this claim at verification.
- COORD NOTE C-2: the launcher's premise "the full run is over ten minutes single-process" is NOT reproduced: 6 s full, 82 s plants. Likely because of C-1 (the predecessor models die at load).

## Agents
- Staffing: SIX critics, one per launcher lens (the skill's 2-5 is exceeded on the launcher's explicit six-lens list; CHECK and PARALLEL are not merged because they ask different questions). Models: RULING opus, EXAMPLES opus, FIXIND opus, NAMES opus, CHECK opus (25 plants: the >5-rows rule), PARALLEL sonnet.
- Standing questions (sibling of a family; general form + unlocks with triggers): FIXIND. Quote check: RULING only. Plants/mutations: CHECK only. Root concept "who may read a label (ownership/doors)" + its definition-completeness question: NAMES.
- Launch 20:31 EST.
| agent | model | launch | end | final state |
|---|---|---|---|---|
| RULING | opus | 20:27 | ~20:35 | file complete, lanecheck DONE rc=0; final reply undelivered (expected) |
| EXAMPLES | opus | 20:27 | ~20:39 | file complete, DONE rc=0 |
| FIXIND | opus | 20:27 | ~20:38 | file complete, DONE rc=0 |
| NAMES | opus | 20:27 | ~20:36 | file complete, DONE rc=0 |
| CHECK | opus | 20:27 | ~20:43 | file complete, DONE rc=0 |
| PARALLEL | sonnet | 20:27 | ~20:30 | file complete, DONE rc=0 |
| VERIFY | opus | ~20:47 | ~20:57 | verify.md complete (V1..V16: 14 HOLDS, 2 HOLDS-with-PARTLY parts, 0 REFUTED) |
- No resends, no nudges, no blinding leaks noticed (critics read only R/ copies and their own clones; NAMES/CHECK/VERIFY built own sparse clones). All six critics returned in the launch turn.
- Per lens raised: RULING 8, EXAMPLES 8, FIXIND 16, NAMES 11+summary, CHECK 8, PARALLEL 4 (55); consolidated to 28 items (A1-A18, B1-B10). Overlaps: A1 (2 lenses), A2 (3), A3 (2), A4 (2), A6 (3), A8 (2), A9 (3+), B1 (2 + coord).
- Coordinator timing after verification (VERIFY/tree, library.md served from 89d26b6b3, restored after): predfix86 LIGHT 1.8 s 29/2; predfix84 LIGHT 4.6 s 37/4; predfold1123 LIGHT 3.2 s 18/4; predspot 34.0 s 27/6. The revived chain is red and costs real time (input to B10).
- Freeze drift at hand-back: none in rulings (main 0e03c8f30: full_suite_ledger only; subject branch 28616b247: docs/dev/pred/ only).
- Time to draft: freeze 20:22 -> draft 20:58 (~36 min).

## Process observations
- The coordinator's freeze re-run of the evidence found the round's main evidence finding (B1) before any critic launched, because the measured wall time (6 s) contradicted the launcher's premise (>10 min). Two critics (CHECK, PARALLEL) re-found it blind.
- Six critics ran without duplication thanks to COMMON's drill-assignment list; the residual overlap (label-reference, label-omitted, the unspecified piece) is the useful kind (three routes to one sentence).
- NAMES used the model's own engine as its oracle and found engine defects (B8) that way; independent python `re` lowering was used only for the 3xx/7xx answers. Fine for legality, but an engine-as-oracle lens should state it.
- The skill's 2-5 critics cap met a launcher list of six lenses; nothing was lost by running six.

## Proposed changes
1. Skill §3 (design-mode committed evidence): "The coordinator also reads each successor/chain check's per-model last lines: a predecessor whose last line is a load-time traceback is a dead chain, recorded in .coord as a probable finding; a launcher-quoted run time is re-measured and any gap over 2x is recorded." (Observation: B1 here; the 18/0 verdict was green on a chain of 13 tracebacks.)
2. Lens table, check adequacy row: "For a STATUS TABLE check, mutate the document's header row and its column-defining sentence; a check that builds its own column map from literals survives both." (CHECK-4.)
3. COMMON template: "An evidence engine used as the oracle for a name or cell grid is itself under test: report any cell where it answers silently against a document sentence as an engine finding." (NAMES-1/B8.)

## Framework notes
- The coordinator pattern scaled to six critics plus a verifier in ~36 min of wall time with one launcher message; the blind re-run of evidence at the freeze is the cheapest high-value step (seconds of CPU, the round's top evidence finding).
