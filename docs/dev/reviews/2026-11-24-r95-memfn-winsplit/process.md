# process.md (coordinator, r95 memfn-winsplit)
- 14:47 launched; freeze 0719e0a4d (subject), build-on 4d26eef02 code; mac-suite.lock HELD (plantfix) from setup on.
- 14:49-14:52 premise re-runs of instruments (verdicts in premise_verdicts.md). Round dir created 14:48 (was absent).
- 14:53 launched 5 critics, all opus, background, unnamed: owner, premise, slot (+ruling), rdchecks, rdcode. Pre-created findings files + DELIVER.
- All 5 returned in the launch turn (final replies undeliverable as expected); files complete with CRITIC COMPLETE:
  slot 9.7 min, owner 11.4 min, rdcode 16.0 min, premise 19.7 min, rdchecks 21.3 min.
- Findings raised: owner 8 (incl. recs), premise 20, slot 12 (+recs), rdchecks 11, rdcode 8 = 59 raw.
- No critic needed build/pcrec (design is a move; all probes were gcc-16 -fsyntax-only; 63+4+... probes). Build still waiting on lock at 15:16.
- 15:17 verifier (sonnet) launched over V1-V19 (grouped overlaps; one CONTRADICTION item V17); returned in launch turn, 6.4 min: 18 HOLDS, 1 PARTLY (V12 S452), V17 settled (5/4 line counts = design's command; 6/5 occurrences).
- 15:23 lock cleared; review tree built (gcc-16, -j2, nice, unlocked) rc=0 in <1 min; build log WARNING targets-check rc=1 (aarch64 host compares no target): pre-existing env fact, noted in draft.
- Freeze drift at hand-back: none (origin/main still 4d26eef02).
- Draft written 15:30; ~43 min from launch to draft.
- Per lens: owner 8 raised / all verified items HOLD; premise 20 / verified items HOLD (S452 PARTLY); slot 12 / V9,V10 HOLD; rdchecks 11 / all HOLD; rdcode 8 / all HOLD. Overlaps: run_member x4 lenses, census counts x2, plan_ix x2, use_nothing x3.
- Blinding: no leak noticed; critics cited no denied file. Delivery: all final replies undeliverable (expected); all files complete; lanecheck DONE rc=0 x6.

## Process observations
- The build was not needed by any critic: a no-mover MOVE design is reviewed by reading, instrument re-runs and -fsyntax-only probes. Waiting for the lock before launching would have cost ~30 min for nothing; launching first was right.
- The most productive probes were trial compiles (rdcode, premise): name censuses missed type completeness, prototypes, sizeof, comment boundaries. No lens was given a cut assembler; two critics wrote their own.
- Overlap on run_member (4 lenses) came from four lenses reading the same census list; acceptable (cheap, confirming) but the topic could have been assigned.
- Lens table had no row for a "file split / move" design; readiness + premise covered it.

## Proposed changes
- Skill §5 (design mode): "For a MOVE design (a file split, a re-home), the run kit holds a cut ASSEMBLER (the design's cut spec -> one file per target in the round dir) and ONE readiness lens `-fsyntax-only`s every assembled file with and without each trace define (r95: plan_ix, use_nothing's sizeof, renderer-row and wf_rc completeness and a mid-comment cut were all found by hand-built probes; the design's name census saw none)."
- Lens table, check adequacy / readiness: "For each binder the subject RE-POINTS, name the gate that EXECUTES it after the move; a re-pointed binder no gate runs is a finding (r95 W22: G2 plant tables run only under --plants, which no gate calls)."
- Skill §3 design mode: "When the subject is a no-mover with no new runtime path, launch critics before the review build; the build is for probes only (r95: no critic used it)."

## Framework notes
- Five opus critics + one sonnet verifier, all returning within 21 min in the launch turn; the coordinator spent most time on consolidation (59 raw -> 37 consolidated). The pattern fits large mechanical refactor designs well: the narrow lenses (code vs checks readiness split) produced almost no duplication except one census artifact.
