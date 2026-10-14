# r17d — R17-b's owed checks: S820-S843, T2, T4, Q8, Q10, A-N2 (lane report)

Lane r17d (opus), 2026-10-12, for the memfn kit manager. Branch `lane/r17d`,
cut from the kit branch `lane/memfn-r17` @ 9da519862 (R17-b, abi 77, with
r17b2's pruned search and r17c's fixes). **No emitted byte moved: no abi
change.** The one header addition is the test-only entry `mf_set_terms_text`
(memfn.h), listed under the unmerged `MF_SITE_ABI` 12 as r17b2's
`mf_set_terms_probe` was; it writes no artifact text. Box: the Linux dev box,
mech and the light chain on cores 8-11.

**Headline.** 20 rows DETECTED solo and 3 at their declared UNREACHED (S823, S838,
S839 RESERVED), each by the detector setfind.md §12.5's rev 2.3 table names
or its stated substitute. One equivalent mutant was found and replaced
(S828's first plant, objective 4 dropped, moved no cover on T2's population).
T2 pins 2,158 covers, each re-expanded by the checker's own arithmetic, and
holds today's kit to them. T4 agrees with `pcrec_cube_of` on 8,758 sets.
Q8, a shadow-hook batch and Q10 are in G2's setfind family. A-N2 is
documented: U1 already holds `__member` to the deny table. New detectors
built for rows that had none: arm `g2setfind`, the `init` C-check, and the
gcov dynamic reach. Light validation is green after one fix (C4 caught ISA
words in S823's prose).

## 1. The sabotage rows (setfind.md §12.5, the rev 2.3 table)

Every row is a file under `tests/mech/sabotages/S8xx_r17d_*.sh`, verified by
a SOLO mech run (`tests/mech/run_sabotage_matrix.sh S8xx`, one invocation per
row, `KEEP=1`), at the tree SHA each log names. Logs:
`build/r17d/mech/mech_S8xx.log` (the matrix row and trailer) and
`build/r17d/mech/logs_S8xx/` (each arm's own log). Cover-search plants sit in
the CURRENT pruned search (`memfn/src/terms.c` after r17b2). The cache-path
rows (S822, S830-S834) prove DYNAMIC reach on the clean tree first
(`tests/memfn/setfind_reach.sh`: gcov's count of the planted line on
corpus-shaped movers, floor the literal 1).

| S-id | plant | file | detector | solo verdict | SHA | log |
|---|---|---|---|---|---|---|
| S820 | the W8 `range` primitive adds 127 - w (admits l + w) | `mfk.c` | G2 sequences; U1 `__mask` | g2setfind 6fail/24pass, setfind 196fail/47pass DETECTED | ad0fcdb09 | `build/r17d/mech/mech_S820.log` |
| S821 | a prime cube candidate offered with mask bit 0 flipped (`cands_of`) | `terms.c` (pruned search) | §10 refusal; T2 live/equal | setfind 14fail/35pass DETECTED | ad0fcdb09 | `build/r17d/mech/mech_S821.log` |
| S822 | the byte tail stops at `k + 1 < hi` | `pffind.c` | G2 Q1/Q5 at hi < 8; reach: tail-fill line (gcov) | reach ok, g2setfind 7fail/23pass DETECTED | ad0fcdb09 | `build/r17d/mech/mech_S822.log` |
| S823 | (marked anchor) the SIMD overlapped block shifted | `pffind.c` | Q10 on the SIMD family, at the arms | UNREACHED (expected; REACH greps mfk.c for V16/V32; re-run after its text dropped ISA names, v1 `mech_S823_v1.log` the same) | c1a33e3dd | `build/r17d/mech/mech_S823.log` |
| S824 | the end_back-1 guard spelled `<stem>__c.n - 1 > lo` | `pffind.c` | G2 Q7 (NULL at n = 0), ASan | g2setfind 20fail/10pass DETECTED | ad0fcdb09 | `build/r17d/mech/mech_S824.log` |
| S826 | the answer's first cube widened by its lowest cared bit | `terms.c` (`mf_set_terms`) | §10 refusal | setfind 15fail/34pass DETECTED | ad0fcdb09 | `build/r17d/mech/mech_S826.log` |
| S827 | S826's plant + the define's round trip removed | `terms.c` + `pffind.c` | T2 live (its own expansion), U1 | setfind 378fail/44pass DETECTED | ad0fcdb09 | `build/r17d/mech/mech_S827.log` |
| S828 | objective 4 reversed (canonical greatest wins); REPLACED, see §1.1 | `terms.c` (`cover_better`) | T2 equal | setfind 1fail/47pass DETECTED (v1: 0fail/48pass UNDETECTED, `mech_S828_v1.log`) | d19aecc55 | `build/r17d/mech/mech_S828.log` |
| S829 | every cover recorded as direct (`c.complement = 0`) | `terms.c` (`dfs`) | §10 refusal; T2 | setfind 6fail/43pass DETECTED | ad0fcdb09 | `build/r17d/mech/mech_S829.log` |
| S830 | cache test `lo < c->top` only | `pffind.c` | G2 Q3/Q4; reach: cache-hit line | reach ok, g2setfind 12fail/18pass DETECTED | ad0fcdb09 | `build/r17d/mech/mech_S830.log` |
| S831 | the word refill's `c->base = i;` dropped | `pffind.c` | G2 Q2, cache invariant; reach: word-fill line | reach ok, g2setfind 10fail/20pass DETECTED | ad0fcdb09 | `build/r17d/mech/mech_S831.log` |
| S832 | storage declared with no initializer (s, n assigned) | `pffind.c` | G2 O0dirty (Q9) + setfind `init` C-check; reach: cache-hit | reach ok, g2setfind 6fail/10pass, setfind 20fail/38pass DETECTED | d19aecc55 | `build/r17d/mech/mech_S832.log` |
| S833 | the pop shifts by `lo` | `pffind.c` | G2 Q1, UBSan; reach: cache-hit | reach ok, g2setfind 8fail/22pass DETECTED | d19aecc55 | `build/r17d/mech/mech_S833.log` |
| S834 | the overlapped word at `hi - 7` | `pffind.c` | G2 guard page (SIGSEGV), ASan, cache invariant; reach: overlap-fill | reach ok, g2setfind 20fail/10pass DETECTED | d19aecc55 | `build/r17d/mech/mech_S834.log` |
| S835 | storage named `pcrec_mfk_c` whatever the stem (two edits) | `pffind.c` | G2 Q8 (`g2s_q8.c` among the failing units) | g2setfind 7fail/9pass DETECTED | d19aecc55 | `build/r17d/mech/mech_S835.log` |
| S836 | `load_vector` swaps on little-endian | `mfk.c` | G2 sequences, U1 | g2setfind 11fail/19pass, setfind 488fail/44pass DETECTED | d19aecc55 | `build/r17d/mech/mech_S836.log` |
| S837 | storage named `c` (two edits) | `pffind.c` | G2 shadow-hook batch (`g2s_b11.c` among the failing units) | g2setfind 7fail/9pass DETECTED | d19aecc55 | `build/r17d/mech/mech_S837.log` |
| S838 | W8's guard renamed `PCREC_MFK_H` | `mfk.c` | mixed-layer TU check, at the arms | UNREACHED (expected) | d19aecc55 | `build/r17d/mech/mech_S838.log` |
| S839 | (marked anchor) the decline arm declines on ABSENT density | `pffind.c` | an arm-pin case, at §9.2's arm | UNREACHED, RESERVED (expected; REACH greps for `cand_ppm`) | d19aecc55 | `build/r17d/mech/mech_S839.log` |
| S840 | the byte-class prefilter's `reads_table` return dropped | `src/gen/emit_dfa.c` | setfind `table` + `-Werror` | setfind 15fail/43pass DETECTED | d19aecc55 | `build/r17d/mech/mech_S840.log` |
| S841 | the DFA hat's kit set taken from the forward search's `can_begin_match` (two edits) | `src/gen/emit_dfa.c` | N4 door (setfind §3, rank) + U1 | setfind 12fail/46pass, rank 2fail/13pass DETECTED | d19aecc55 | `build/r17d/mech/mech_S841.log` |
| S842 | W8 written without `range` when the art's first cover has no arc | `mfk.c` (`mfk_block`) | setfind sub-block identity | setfind 373fail/44pass DETECTED | d19aecc55 | `build/r17d/mech/mech_S842.log` |
| S843 | `pf_define` (memchr and walk rows) writes W8 | `pffind.c` | setfind sub-block presence | setfind 13fail/44pass DETECTED | d19aecc55 | `build/r17d/mech/mech_S843.log` |

Every log ends `== mech run COMPLETE: 1 rows (unexpected: 0, ...)`; the
three UNREACHED rows read `unreached: 1, unexpected: 0`. Per-arm logs are
in `build/r17d/mech/logs_<id>/`.

S825 is seambuild's, not R-17's (§12.5's renumbering note); no row here.

### 1.1 Deviations from the table, each the smallest sound reading

- **T1 and T5 are not built.** The rev 2.3 table names T1's independent
  expansion (S827) and T5's per-term kernel test (S820, S821, S829). T1 is a
  D27-blinded family the design schedules for later, and T5 was not in the
  brief's list. The rows are held instead by T2's `live` leg (its own
  expansion of every live cover), U1 (each mover's `__mask`/`__member`
  against the deny table) and G2's sequences. Each row's header says which.
- **Cover-search rows trip the refusal.** S821 and S829 are planted in the
  pruned search, as the brief requires. A wrong cover there is refused by
  §10's round trip before any rendering, so their first detector is the
  refusal: the setfind witnesses do not compile. T2 is the second line.
  With the check on, no expansion downstream ever sees such a cover; S827
  is the row that turns the check off.
- **S828: an equivalent mutant, replaced.** The first plant dropped
  objective 4 (the first equal-cost cover found wins). Its solo run read
  `setfind:0fail/48pass` UNDETECTED (`mech_S828_v1.log`). On all 2,158 sets
  of T2's population the search meets the canonical least first, so no cover
  moves. The replacement reverses the key, which moves exactly the 3 tie
  sets the population holds (two bench letter classes, one corpus set;
  measured with a scratch kit before the run). The pin's tie population is
  therefore thin (3); a larger generated tie family is a possible widening,
  not done.
- **S832's promised C-check did not exist.** setfind_check's `DECL` regex
  matched only the initialized spelling, and a declaration with no
  `= {` slipped past the `decl` check. The new `init` check reads the
  struct definition and every storage declaration off the artifact. On the
  plant it fires on every mover, and G2's O0dirty leg fires as well
  (2,187,469 failed checks).
- **S834's trace trap cannot fire.** The plant keeps `top = hi`, so
  `top <= hi` holds. The row's arm (g2setfind) carries the guard page,
  ASan and the cache invariant, and the guard page caught it (SIGSEGV).
- **S835 and S837 break G2's own batches too.** G2's ordinary run functions
  read the cache through `<stem>__c`, so a storage name without the stem
  stops them compiling. The named detectors still show on their own units:
  compile failures now name every failing unit, and S835's list includes
  `g2s_q8.c` while S837's includes the shadow batch `g2s_b11.c`. For S835
  the shadow batch compiles (one site per function, no cache read), which
  isolates Q8 as the detector of the cross-site collision.
- **S841 re-aimed.** On the DFA hat, pcrec's FIND set and the table it
  names both come from `f->cand`, so no single-site plant can make the door
  differ. The plant hands the kit the forward search's own candidate set
  (`us->cand`, the `can_begin_match` analysis the hat replaced), while the
  emitted and named table stays the start bytes: "the wrong table" in the
  only form the site offers. It takes two edits (the second sets a
  file-scope pointer where `f->cand` is computed). N4's door fired on 78
  compiles.
- **S839's arm.** It names `memfnarms` (where an arm-pin case would live),
  but it never runs while UNREACHED.
- **The dynamic reach witnesses** are corpus-shaped patterns compiled with
  `--emit-main` (VM hat `[ab]+c`, DFA `[0-9]+x`) and run over chosen
  subjects, not the patterns' own `.rxt` subjects. Every count is at least 1
  (cache-hit 27/8, word-fill 8/6, overlap-fill 1/4, tail-fill 12).

## 2. T2, the golden pin (setfind.md §12.1)

- `tests/memfn/pins/setfind_terms.tsv`: the cover of every set of a FIXED
  population: T3's 558 corpus and bench FIND sets (pins/setfind_t3_sets.txt),
  then a seeded sample (setfind_t2.py `gen_sample`, seed 20261012: 300 unions
  of 2-8 terms, 200 near-cubes, 150 scattered sets, 100 ranges, 50 wrapping
  arcs, each with its complement): **2,158 sets, 1,525 covered (552 by their
  complement; 995 arc terms, 2,132 cube terms), 633 declined.** RECORDED from
  today's kit (`--record`).
- The checker (`tests/memfn/setfind_t2.py`, run_setfind.sh section 7) never
  calls the kit for its verdicts. `pin`: every pinned cover's round trip by its
  own arithmetic (each term well formed, inside the target, the union exactly
  the target, 1..4 terms; a decline only where neither the set nor its
  complement is one cube or one arc). `live`: the same over the kit's live
  covers (read through `tests/memfn/setfind_terms.c`). `equal`: live ==
  pinned, text for text. Floors are the recorded counts (literals; the
  population is the pin itself).
- First run: `pin` 2,158/2,158, `live` 2,158/2,158, `equal` 2,158/2,158.
- It is S828's detector (the tie-break) and a second line for S821, S826,
  S827, S829.

## 3. T4, the `pcrec_cube_of` cross-check (setfind.md §3.6, D122)

`tests/memfn/setfind_t4.c` (run_setfind.sh section 8) links both analyses
from libpcrec.a: `pcrec_cube_of(iv, 0, n-1, 0, 256, …)` against the kit's
one-term cover (`mf_set_terms_text(set, 1, …)`). Population: the pin's 2,158
sets, the 41 corpus byte classes (`tests/clskit/ref/results/byteclasses.tsv`)
and every cube but the full set (6,560): **8,758 sets; pcrec_cube_of says one
cube on 6,700, and the kit's cover is exactly `D c:care:val` on all of them;
on the 2,058 others the kit returns an arc 183 times, a complement cube 33
times and declines 1,684 times, never a direct cube. 0 disagreements.** Floors
(literals): pin 2,158, byteclasses 41, cubes 6,560, one-cube 6,700, not 2,058.

## 4. Q8 and Q10 (setfind.md §12.2)

- **Q8** (`g2s_q8.c`, generated by `g2_setfind_gen.c`'s `render_q8`, driven by
  `g2_setfind_driver.c`'s `run_q8`): 40 pairs (quick; 200 full) of MUSTRENDER
  sets, site A at end_back 0 and site B at end_back 1, defined in ONE art and
  held in ONE function with three use statements (A, B, and a second use
  statement of A sharing its storage: the VM hat's entry/retry shape); the
  driver picks a statement and a lo move (per-site find-all, random, repeat,
  backward) per use, every answer against its own site's byte loop. Quick
  population, first run: 222,967 / 222,826 / 223,327 uses per statement,
  295,337 cross-site successions, 562,826 live uses, 0 failed; floors
  floor(0.9 x).
- **The shadow-hook batch** (§7.6, S837's detector, added beside Q8): 24
  MUSTRENDER sets rendered with hook texts `c`/`m`/`i`, body locals
  `base`/`top`/`w`/`q`, and a stem holding the prefix placeholder `\x01q`,
  rendered to `g2` after the kit wrote it. Floor 21.
- **Q10** (`run_g2_setfind.py` `q10_leg`): the widths the kit has a sub-block
  for are read through `mf_shared_block` (1..64); each must be a width the leg
  runs. Today that is W8 alone, whose sequences ARE the O2 leg; the leg
  prints `UNREACHED: [Q10] the SSE2/AVX2 widths (16, 32) have no
  next_candidate definition` and goes RED the day a new width appears, until
  it is extended. Q5's per-width edges (7, 8, 9, 15, 16, 17, hi - 9 .. hi - 7)
  were already in the driver.
- G2 setfind quick, after: 30 checks, 0 failed (53,833,783 O2 checks).

## 5. A-N2: the trace re-probe (review 2026-10-12-r1)

Documented, not extended (setfind.md §12.4a `[r17d]`, tests/memfn/CLAUDE.md).
The re-probe compares a cache answer with `__first`, a byte loop over
`__member`; `__member` and `__mask` are both spelled from the cover
(`mf_cover_member`, `mf_cover_mask_w8`), so a wrong cover passes it. U1
(`setfind_cover.py`) already holds `__member` on all 256 bytes, and `__mask`
at every lane, to the deny arm's table, which shares no source with the
cover; on every mover U1 reads, the re-probe's loop is therefore a loop over
pcrec's own table. T2 adds the covers of every corpus and bench FIND set held
to their sets by plain arithmetic. Extending the trace form instead would have
it read a table the stateful form does not emit (a trace-only table in the
artifact), for no population U1 at `SETFIND_COVER_EVERY=1` does not already
reach. The residual gap is U1's default sample (every 10th distinct pattern).

## 6. Other changes

- `tests/memfn/setfind_check.py`: the `init` check (§12.2 Q9's C-check, S832's
  promised half): every `struct <stem>__c` storage declared with a brace
  initializer of at most its field count, every `c->F` the helper reads a
  field of the struct, both read off the artifact.
- `tests/mech/run_sabotage_matrix.sh`: the arm `g2setfind`
  (`memfn/tests/run_g2_setfind.py --quick` against the sabotaged tree's
  `build/libpcrec.a`, ~60 s).
- `memfn/tests/run_g2_setfind.py`: a compile failure names every failing unit
  (so the shadow batch's and `g2s_q8.c`'s own failures show in a row's log).
- CLAUDE.md: `tests/mech/`, `tests/memfn/`, `memfn/tests/`, `memfn/src/`,
  `memfn/include/`. setfind.md: §12.1 (T2/T4 built), §12.2 (Q8/Q10 built),
  §12.4a (A-N2), §12.5's rev 2.3 table's status column.

## 7. Light validation (Linux dev box, cores 12-15; logs `build/r17d/light/`)

All on cores 8-11 (12-15 were held by another light chain until 16:30),
`build/r17d/light/<target>.log`, the verdict read from make's `***` lines
(none at the end).

| target | verdict |
|---|---|
| `make -j4` | rc 0 |
| `make strict` | rc 0 |
| `make test-codegen` | 16/16 scripts passed (SABANCHOR resolves every new row) |
| `test-memfn-setfind` | 48 passed / 0 failed (T2 8/0, T4 OK, `init` on every witness and the sample) |
| `test-memfn-arms` | 387 / 0 |
| `test-memfn-link` | 8 / 0 |
| `test-memfn-rows` | 162 / 0 |
| `test-memfn-stamps` | 25 / 0 |
| `test-memfn-manifest` | 11 / 0 |
| `test-memfn-forms` | 5 / 0 |
| `test-memfn-deleg` | 5 / 0 |
| `test-memfn-reach` | 4 / 0 |
| `test-memfn-arch` | first run RED (C4: S823's text named the ISA words of §11.4's arms); fixed (c1a33e3dd), re-run 15 / 0 (`test-memfn-arch2.log`) |
| `test-memfn-guarded` | 10 / 0 |
| `test-memfn-simdfloor` | 51 / 0 |
| `test-memfn-rank` | 15 / 0 |
| `test-memfn-g2` (G2 quick) | rc 0; the setfind family 30 checks, 0 failed (O2 53,833,783 checks), Q10 UNREACHED for the SIMD widths as designed |
| solo mech, 23 rows + 2 re-runs | every row at its declared expectation (§1) |

NOT run (the brief's light-only rule): the full `make test`, the full mech,
sweeps, timing, G2 full. The new arm `g2setfind` and the new run_setfind.sh
sections ride `make test` and the full mech at the manager's merge.

## 8. Charter vs committed

| brief item | committed |
|---|---|
| S820-S843 per §12.5 (rev 2.3 table), house format, detector named | yes: 23 rows (S825 is not R-17's), each with the detector it states |
| missing detectors built unless a later step's | T2, T4, Q8, the shadow-hook batch, Q10, the `init` C-check, the dynamic reach, arm `g2setfind`; T1 (blinded) and T5 not built (§1.1) |
| S823 / S839 UNREACHED / RESERVED with SAB_EXPECT | yes (S838 too, per the rev 2.3 table) |
| cover-search rows in the CURRENT pruned search | yes (S821, S826-S829 in terms.c after r17b2) |
| S834: hi - 7, a guard page / ASan / trace trap in the row's arm | yes: g2setfind (guard pages, ASan); the trace trap cannot fire (top stays hi), stated |
| every row verified by a solo mech run, logs kept, equivalent mutants replaced | yes: 23 solo runs plus 2 re-runs, logs under `build/r17d/mech/`; S828's equivalent mutant replaced (§1.1) |
| T2 golden pin + independent validity check + test section | yes (run_setfind.sh section 7) |
| T4 cross-check | yes (section 8) |
| Q8, Q10 in G2's setfind family | yes |
| A-N2 trace extension or documentation | documented (§5) |
| tests/mech/CLAUDE.md, tests/memfn/CLAUDE.md, §12.5 status column | yes |
| light validation only, no full make test/mech/sweeps/timing | yes |
| no emitted byte moved | yes (the kit's rendering code is untouched; terms.c gains a test-only entry) |
