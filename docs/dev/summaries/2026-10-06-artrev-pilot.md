# [ARTREV] pilot: bottom-up artifact review, exec summary (2026-10-06)

Frank asked (2026-10-05, D150) for generated artifacts to be read bottom-up for optimization leads, each tested by a hand-edited twin, with a report of results and suggestions. The pilot is done: three artifacts, four blind reviews, independent Linux confirmation. Full report: `docs/dev/optloop/artrev/report_pilot.md`; every number below is cited there from `confirm/verdicts.md` and `generalize.md`.

**Did it work? Yes.** Of 22 leads, 15 are confirmed wins on ubuntubudu (pad-controlled, past the null and layout noise), 6 are noise, 1 is a loss. All 22 sealed twins pass the hardened identity check and all 14 sabotage controls were caught. The pilot gate is met; I have started the full run on the terms at the end of this page.

**The headline cells.**
- `stack-frame` (DFA find-all): scanning the rarer required byte `(` instead of `a` is **-72%**. Census says 17 bench / 90 corpus artifacts share the shape.
- `level-context` (hybrid): skipping the `{0,29}` component with rare-byte streams is **-95%** (the scalar-table form, which is what START-SET stage 3 emits, is -76%).
- `doubled-word` (VM): the possessive spelling `\b(\w++)\b\s++\1\b` is **-58% with no new codegen**. The shipped emitter already makes it frameless and inline; what is missing is a possessify analysis for `\b` and backreference follows. Population is small: 1 bench / 2 corpus.

**Surprises.**
- The biggest A07 effect is a gap in an analysis, not new emitter work.
- A09's L4 is a **+23% loss on the cell with a +47% win on hit-dense text**, and the combination twin hid it (-95.4% vs L1 alone -94.9%). A cell-only gate cannot see a regime-losing member of a winning stack.
- The second blind reviewer on A07 added no confirmed win (each reviewer alone reached 6 of the 7 distinct ideas). Notebook-transferred ideas were real but regime-dependent, neither a cell win (n=2).

**Suggestions, filed not scheduled (D137), for Frank's ruling.** In order: (1) the possessify arms, cheapest and no new codegen, filed with its true population of 1/2; (2) reverse-inner on the DFA route, the biggest confirmed effect times population (17/90), a MEMFN request; (3) A09/CTX's skip, which is START-SET stage 3 itself, so re-time A09 on stage 3's output before deciding anything further; (4) the VM word-start filter (-22%), sequenced after stage 3; (5) trail elision, large upper-bound population, changes the give-up surface. The CTX trio (hybrid VM-skip, stay-set skip, frameless lazy step) is held until a hit-weighted cell exists. Tables and counters-in-locals are codegen-micro and not loop leads (D119). Several leads change a caller-observable give-up (a give-up becomes a correct answer, one-way); building any needs its spec hunk (D80) and a K65-style check.

**The experiment's own findings.** The harness never drove its caller-buffer (`_in`) entries in any early identity run (fixed, all twins re-verified). Identity was blind to give-up behaviour until the give-up rule was added. D27 cells were git-readable through the parent repo, so every earlier D27 cell had that leak (fixed; earlier results rest on brief wording). Three of four reviewers never got to time anything: the Mac was loaded and locked by the stage-3 build, and the harness correctly refused. Confirmation cost about 21 minutes of box wall.

**The full run.** Single review per artifact; pinned after START-SET stage 3 lands; batches of 3; Mac scratch timing only when the suite lock is free; single-member twins so stack increments can be attributed; a hit-weighted cell for hybrids; winning and near-tie artifacts included, which the pilot did not have. Limits to keep in mind: three losing cells, one artifact per route, and population counts that are upper bounds.
