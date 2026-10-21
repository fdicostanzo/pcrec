# x0fix — kit_proof revision 2.2: R1/R2 fixed, K35 recount and X0 re-run queued (2026-10-21, opus)

Brief: the manager's LANE x0fix message. Branch `lane/x0fix` from main `63a7c3315`.
Design and instruments only: nothing under `src/`, `memfn/` or `tests/`. R-26 is unchanged.

## What changed

- **R1 (wrong answers): fixed.** The reading took an unseeded machine's entry to be row 0.
  `docs/dev/kvcensus/kvdfa.py` now reads the EMITTED entry constant (`_entry`,
  `Machine.entry`, `entry_read`) on both arms: unseeded `<m>_state = X;`, and seeded
  `<m>_state = P ? seed[..] : X;` with P either `search_from` or `handoff_position`. The
  same row-0 assumption also sat in three other places, and all three now read the entry:
  - `starts()`. Seeded, it ADDED row 0 for the absent predecessor even when `X` is dead
    (`(?<=x)cat`). It now raises when no entry constant is emitted (no silent default).
  - `whole()`.
  - `forward_path()`'s start row.

  `conj.py` C6 (`k_entry`) reads `A.entry`, and the S1140 plant `e0-row0` now applies on
  both arms.
- **R2 (under-stated hull): fixed per the true-set ruling.** The emitted loop takes the eol
  view at a subject-final `\n` and steps the VIEW state on that byte. kvdfa now models that
  edge:
  - `Machine.vnl` is the row whose `step(eol[q], '\n')` accepts at the end;
  - `acc_end` is the emitted end test, in its order: end view, then eol view, then plain;
  - liveness counts such rows (`liveness()`);
  - `lang()` adds `\n` to the row's subset set, ends a match at `d + 1`, and reports the
    depths where this happened as `view_d`.

  The plant `CONJ_PLANT=plain-walk` (`conj.machine`, also read by `x0.py`'s site reading)
  restores the old walk. It has no S-id because the S1130-S1150 range is full. No shape
  was found where the true set is unsound, so no new conjunct was added.
- **kit_proof.md revision 2.2.** The header, §R2.2 (finding → section), C6 (both arms), and
  §5.2 (the struck C8 sentence, its correction, and what `span_facts`, the extended
  `pcrec_kset_walk`, must do: pass a position-only assertion through WITH its continuation,
  neither dropping the thread nor narrowing to the position's byte). Also S1140, and
  §6.4's X0 re-run paragraph, which is marked OWED.
- **K35: the instrument is ready, the numbers are OWED.** `conj.py census` gains section F,
  the table run over EVERY census pattern at its own flags, with `in-B`/`outside-B` and a
  distinct count. Its output replaces §1.2's population.
- **U20 filed** (`docs/dev/upstream_issues.md`), with the probe
  `docs/design/kit_proof/x0/u20_probe.c` and transcript `x0/out/u20_probe.txt`. It is the
  DOCUMENTED `MATCH_INVALID_UTF` skip (pcre2unicode(3): "that sequence is skipped, and the
  match starts at the next valid UTF character"), applied before `ANCHORED`. Status is
  divergence-by-design. The one reportable point is that `\G` does NOT move with the skip
  (`\Ga` on `"\x80a"` gives no match) while `ANCHORED` does.
- **Exposure instrument**: `docs/design/kit_proof/x0/exposure.py` counts, over the census,
  the machines whose entry is not 0 or is dead (R1's reach, which also covers kvcensus's
  committed tables) and the anchored machines that gain a view byte (R2's reach). The
  results are OWED to the recount job.
- The kvcensus selftest has six new lines (the entry and the view byte, each with a
  plant). It is all PASS, and every older line is byte-identical; the probe section was
  rebuilt with `build/kv/pcrec-kv`.

## Validation done in-lane (light, no lock)

- **PREMISE TEST.** At main, `\Zx` read `cover k=1` (the defect), on both `-` and `R`. After
  the fix it reads `entry-const` on both.
- **The R1 items.** `\zx`, `\zabc`, `-{0,}?\Z-` (native and utf8) and `[ab]*\z\W` read
  `entry-const`. `\w{0,2}?$\W` reads `no-eol-view` on `-` and on `R`.
- **Witnesses** (`witnesses.txt`, 32 lines). The output is identical to `conj.txt` D except
  that `a$\n` moves from `fixed-width` to `no-eol-view`: it is now live through the view
  and reaches C9. `foobar`, `\bcat\b` and `(?<=x)cat` are unchanged.
- **Site readings.** `(a$\n)|ab` (both encodings), `ab|a$\n`, `ab|a\Z\n` and `ab|a$\n\z`
  read `S_1 = {b, \n}` with `exact` 2 and `span` 2. `a$\n` reads `[{a}, {\n}]`.
- **X0 smoke run** (9 items: the R1 items, two admitted controls, the R2 site in both
  encodings, one K1 witness; `build/x0fix/res_smoke.jsonl`): 0 differences, and every R1
  item declines. Under `--plant plain-walk` (`res_smoke_pw.jsonl`) the R2 site and the
  witness go red (`under: [10]` at d = 1).
- `make -j8` in the worktree builds. No `make test` was run: nothing that `make` builds
  changed.

## OWED (queued, not run by this lane)

Both jobs are in `scripts/boxqueue` with owner `x0fix`. When this lane ended they were
queued behind kit `500-kit-r26z1-heavy` (cap 6 h) and m0build's three jobs.

1. `300-x0fix-recount` (cap 1800 s). It writes `worktrees/x0fix/build/x0fix/{conj_census,
   conj_rarm, conj_wit, exposure}.txt`, and its completion line is `== RECOUNT COMPLETE`.
2. `530-x0fix-x0run` (cap 5400 s; x0oracle's own runs add up to about 25 min at 8 cores).
   Its outputs go to `worktrees/x0fix/build/x0fix/out/`:
   - `population.txt`;
   - `summary_admitted.txt` and `summary_sites.txt`;
   - `plant_<P>.txt` for the 8 conj.py plants and for `plain-walk`;
   - `self_<S>.txt` and `stated.txt`.

   The two utf8 site stragglers (`\b[0-9a-f]{32}\b` and the `\b` UUID) are left out again,
   as NOT RUN. The completion line is `== X0FIX RUN COMPLETE`.

**For the fresh agent that reads the verdicts** (re-read `x0fix_rulings.md` first):
- (a) `scripts/boxqueue state x0fix-recount` / `state x0fix-x0run`, then `scripts/verdict`
  on each job log.
- (b) Write `conj.txt` anew from `conj_census.txt` + `conj_rarm.txt` + `conj_wit.txt`
  (sections A, B, C, D, E, F; keep D's appended-witness headers).
- (c) kit_proof §1.2: replace the population from section F (`all-cover` /
  `all-cover distinct`), name the difference from the old 77 / 665 and 50 / 485 (the R1
  declines, the 89 clean outside-B patterns, anything else), and update §0's
  stage-1-population row, §7 B1's mover cell, the §1.2 prose that cites 1,197, and
  `docs/design/CLAUDE.md`'s kit_proof entry. All of them are found by grepping `665`,
  `485` and `1,197`.
- (d) STOP-RULE CHECK. Any red in `summary_admitted.txt` / `summary_sites.txt` that is not
  a U1 shape and not explained by R1/R2 means STOP and report. So does a site red that
  only goes away under `plain-walk`'s inverse.
- (e) Plants. Each conj.py plant must be red on its movers. `e0-row0` should now reach
  the unseeded R1 shapes too. `plain-walk` must be red on the R2 sites. Each self-plant
  must be red where it reaches.
- (f) Rewrite `kit_proof/x0/results.md`: a revision-2.2 section on top, the x0oracle
  record kept below it. Copy `build/x0fix/out/*.txt` to `kit_proof/x0/out/` (rev 2.2
  names). Replace §6.4's OWED paragraph with the result.
- (g) Exposure. Record R1's and R2's reach in §R2.2 and in the kvcensus CLAUDE.md note,
  and say whether kvcensus's committed `sites.tsv.gz`/`patterns.tsv.gz` readings move. If
  they do, file the regeneration as a follow-up; do not run it here.
- (h) Commit, then hand back to the manager.

## STATE AT HANDOFF

- Commits on `lane/x0fix`: `235767b1f` (kvdfa, conj.py C6, U20, exposure), `7aba28ac9`
  (the plain-walk plant), `f8f41332e` (rev 2.2 text, CLAUDE.md files), and the final
  commit (census section F, the §6.4 OWED paragraph, the design CLAUDE.md entry, this
  report, the lanes index line).
- Validation: the light checks above are COMPLETE. The K35 recount and the X0 re-run are
  OWED: they are queued as above, and no process of mine is running.
- Last rulings entry applied: none (`x0fix_rulings.md` reads "(none yet)" at every
  checkpoint).
- Stop rule: not triggered by anything measured so far. R-26 needs no change.
