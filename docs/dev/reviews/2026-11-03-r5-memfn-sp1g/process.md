# process.md — crit-memfn-sp1g (code)
- 13:20 freeze (see freeze.txt). Review tree built nice make -j2 unlocked, EXIT 0, ~2 min.
- Deviation: two extra scratch builds (-DPCREC_KS_TRACE of SUBJECT tree and of main tree, BUILD_DIR in round dir/bin; main tree verified clean after) + copy of main build/pcrec as BASE binary (main == BASE for all code). Reason: the promise includes KSRCTRACE records byte-identical, which needs trace binaries on both sides; cheaper to build once here than per critic.
- Lenses: readers (opus; slot tracing + ruling check + goals + standing questions), emit (opus; emitted vs replaced, identity), check (opus; check adequacy), house (sonnet; house rules). Not run: contract (no docs/spec names the removed fields per design; folded as a grep into readers), trade audit (no pin/floor moved except MF_SITE_ABI number).
- Compile budget: emit 1800, check 400 (+ <=6 run_finder.sh runs on a scratch copy), readers 200, house 100, verifier 400.
- 13:23 launched readers(opus) emit(opus) check(opus) house(sonnet), background, unnamed. All four returned IN the launch turn ("ended without SubagentHandback"), files complete with .done: house 13:24, emit 13:27, readers 13:28, check 13:29 (~5-7 min each). No resend/nudge needed.
- readers: exceeded its 200-compile cap (224; disclosed). DENYLIST LEAK (disclosed): its diff over memfn/ did not exclude memfn/docs/journal.md, saw the 2026-11-03 sp1g hunk; claims checked against code. COMMON's diff command excluded journal only for the whole-tree form; a per-dir diff dropped the exclusion.
- emit: 393 cases x4 binaries, 1614 compiles, 0 diffs; no findings.
- check: 7 plants, 2 red 5 green; ~170 compiles.
- Compiles so far ~2010.
- 13:30 verifier (sonnet) launched; returned in launch turn 13:33 with verify.md + .done. 1 scratch trace build (plant k[i].digest=0), 60 compiles, 8 plant runs; all HOLD, READERS-1 PARTLY; no REFUTED (nothing to re-run).
- 13:40 draft review.md written; critic texts + verify.md in review/. Worktree removed via wtprune --force --quiet-min 1. Freeze drift: none (decisions/plan unchanged; branch unchanged). Main tree status unchanged throughout.
- Totals: ~2.1k compiles (cap 3k); 4 builds (review tree, 2 coordinator trace builds, 1 verifier trace build). Wall time freeze->draft ~20 min.

Per lens: readers 6 findings + standing (all verified, 1 PARTLY), emit 0 (393 cases), check 7 (5 confirmed plants-green/by-construction, 1 suspected, 1 doc), house 7 (5 confirmed, 1 suspected, 1 unverified-then-read). Overlaps: READERS-6=CHECK-3, READERS-5=CHECK-5, READERS-2=CHECK-7, HOUSE-1~READERS standing(e), HOUSE-6~CHECK-3.

## Process observations
- Every agent (4 critics + verifier) returned inside its launch turn; lanewatch never needed. Files + .done reliable.
- The check lens with real plants was the productive one: the unit's only behavioural witness (L(4b)) reaches no reader. The emit lens spent ~75% of the compile budget to confirm a property a code read (kit reads only tag/present/payload) already made near-certain; for a pure layout deletion, emit could be capped at ~300 compiles and the budget moved to plants.
- Prebuilt BASE/SUBJECT trace binaries in the round dir saved each critic a build; the verifier still needed one planted build. Worth making standard when the promise includes a trace record.
- Denylist leak: readers ran a per-directory diff (memfn/) without the journal exclusion; the COMMON diff command's exclusions only protect that exact command.
- readers exceeded its compile cap by 12% (disclosed).

## Proposed changes
1. Skill §5 COMMON template: state denylisted files as PATHS to exclude from EVERY git diff/grep (`':!memfn/docs/journal.md'`), not only inside the one example diff command. (readers leak.)
2. Skill §3 step 2: "When the promise includes trace records, the coordinator builds BASE and SUBJECT -DPCREC_KS_TRACE binaries once into the round dir (BUILD_DIR=...), counting as the round's build." (this round; avoided 3 per-critic builds.)
3. Lens table, check adequacy row: add "for an INVARIANCE check (the kit never reads X), plant the reader where the containing object is CONSUMED, not only where the design's plant sits; demand a reach control (varied render differs from absent-object render on >=1 site)" (F1).
4. Lens table, emitted-vs-replaced row: "for a deletion of fields no kit .c reads (grep), cap identity probes at a few hundred and spend the rest on the check lens's plants" (budget observation).

## Framework notes
- Coordinator pattern on a small code unit: ~20 min freeze to draft, one coordinator turn chain, zero manager wakes. The verifier reproduced 8 plants from the critic's own harness copy in under 4 minutes: the "critic leaves a re-runnable harness in its dir, verifier copies it" pattern is cheap and strong — consider requiring critics that plant to leave plant.sh + .sub files.
- (late) emit critic's handback reached the coordinator by SendMessage after SubagentHandback failed 3x ('spawner no longer running'); content matches emit/findings.md, already in the draft. Nested final replies do get lost; the FILES carried the round.
