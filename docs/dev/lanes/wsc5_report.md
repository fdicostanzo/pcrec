# wsc5 — D172 S2 commits 5 and 6: the lever flipped, then the old path deleted

Lane wsc5 (kit lane of the memfn kit manager), 2026-10-22. Worktree `worktrees/wsc5`, branch
`lane/memfn-wsc5`, cut from `lane/memfn-wsc4` @ 2595ac302. Build go: Frank's conditional go for D172
(critics GO, main agreed; request R-29), as for wsc1-wsc4. Design: `docs/design/memfn/window_site.md`
rev 3.2 §3.4, §4, §5.1 (commits 5 and 6). No rulings file was named.

STATE AT HANDOFF:
- **Commit 5:** done, witnessed: emit_sweep at zero movers on every arm, and the derived mech set
  green (§3).
- **Commit 6:** done in part (§2). The rest waits on three rulings asked of the kit manager (§6: R1
  the old fields, R2 the pin's placement, R3 RPT). Each part not built is named, with its reason.
- **Light checks:** green at the tip (§4).
- **Owed:** the heavy job `580-kit-wsc5-heavy` is QUEUED (§7).

## 1. The commits (main's review: path class per commit)

The branch was REBUILT once before handoff (plumbing, `git commit-tree`; no tree changed): two
`git rm` deletions of sabotage rows had been swept into the pcrec-path commits 5a and 6-p1, breaking
main's condition 1. The rebuilt commits carry the deletions in their test commits. The tip's tree is
byte-identical to the pre-rebuild tip (5c2fa4be1); evidence taken on the old shas maps by tree: old
12c07ea90 = new a6d7634aa, old ecf1159d2 = new 4cc748fa1 (`build/wsc5/rewrite_map.txt`).

| # | sha | path class | what |
|---|---|---|---|
| 5a | acf9f438d | PCREC PATH (cli/, src/) | the window family is the DEFAULT: every art previews it, NEXT reads the phase-1 reply; the old path behind the inverse harness lever `window-legacy`; a kit-proof art keeps the old path |
| 5b | 5b625ddfe | KIT PATH (memfn/) | docs: the preview's default use; `wshadow.py` under the inverse lever |
| 5c | a6d7634aa | TESTS (tests/) | `run_wreply.sh` inverted; S281/S289 retired, successors S1415/S1416 |
| 6-k1 | 708cc21ee | KIT PATH (memfn/) | the family is every art's (no preview needed); the old path (a window site rendered from its own old fields) and the trace shadow `wf_shadow`/`wshadow.py` deleted; `mf_wdecide` on any art; G2's lever controls inverted |
| 6-p1 | 32f9b1781 | PCREC PATH (cli/, src/) | the inverse lever and pcrec's preview call deleted; NEXT reads the reply only (`next_keys[]` loses its pick column); `ofs_test_of` derives the offset rows' candidate test from the reply; `src/opt/prefix_k.c` deleted (the builder asks the byte-rate, B5); ONE run-member resolver `req_run_member` (main's R-29 condition (a)) |
| 6-t1 | 4cc748fa1 | TESTS (tests/) | `run_wreply.sh` reduced; S187/S188 retired, successors S1417/S1418; S287/S448/S449/S522 re-aimed; limits and C4 allowlists descend; the G7 lever fence's red (since commit 4) cleared |
| 6-k2 | c4ae6d832 | KIT PATH (memfn/ + the kit's checks in tests/memfn/) | the `"window-family"` preview step retired; finder row D2 retired (window_site.md §2.2) with FF_RUN and SF_RUN_TERM |
| 6-c | 41f4a12eb | SPEC (docs/spec/) | match_api §6.3.1¶5a, tuning §2.14¶2-¶3 and §2.30¶2, findings §4 |
| 6-k3 | 0c6498a39 | KIT PATH (memfn/include/) | `MF_SITE_ABI` 19 -> 20 |
| 6-p2 | 5bdeafe83 | PCREC PATH (src/) | `PCREC_OFSK_MAX_SET`'s listed description restored (a `--list-limits` mover, §3) |
| (d) | this commit | docs (`docs/dev/lanes/`, the lane index, the kit journal) | this report |

**Bisectability, two transient reds.** These are inherent to the path-class split, and each is
named here:
- **6-p1 deletes `src/opt/prefix_k.c`.** S187/S188 still anchor there, and the C4/limits allowlists
  still list it. At that commit alone the sabotage-anchor check and test-memfn-arch are red; 6-t1
  repairs both.
- **5a is red on test-compound.** It still carries wsc4's `run_wreply.sh`, which spells the harness
  option: the lever fence finding (§5, F-1). 6-t1 clears it.

## 2. What commit 6 does, and what it does not (yet)

### 2.1 Done

**The family is the only route.**
- A site stating alternatives is the window family's on EVERY art (6-k1). The kit's old path for
  window sites is deleted, and with it the shadow that compared the two (`wf_shadow`, `wshadow.py`):
  **the trace shadow RETIRES with the old path.**
- The preview step `"window-family"` is retired (6-k2).
- pcrec never previews it and has no inverse lever (6-p1).

**NEXT reads the reply only.**
- `next_keys[]` holds the declared reply field values per row (run-pinned: C-pin + RE-SEED;
  offset-set: RESEED). The rows below read no key. The RE-SEED refusal stays.
- `nk_pick_run_pinned`/`nk_pick_offset_set` are deleted, and so are wsc4's offset-set guard and
  `ofs_test_model`.

**The stamps read the reply (§3.4's table).**
- `ofs_test_of` builds the offset rows' OfsTest from the reply:
  - the scan is the reply's STOP;
  - the terms are the PLAN, ascending;
  - C-pin's stretch is one run term at `run_lo`;
  - `maxk` is the largest tested offset.
- So `<PREFIX>_DFA_PREFILTER_OFFSETS`, the block, its tables, its comment and G1 read the reply.
- `<PREFIX>_DFA_PREFILTER`'s offset values are the NEXT row the reply's keys chose.
- Before the pick was deleted, a transitional build held reply-OfsTest == pick-OfsTest field by
  field (loud otherwise). The witnesses read equal; the corpus-wide proof is the sweeps (§3).

**The run member's ONE resolver (main's condition (a)).**
- `req_run_member(cx, r)` (src/gen/emit_dfa.c) states the run WINDOW as every pre-check part states
  it: one span, each position its byte or cube, core all, verify YES. It asks `mf_wdecide` and
  returns the reply's member. W3-3 read: `@idx` reads the part's reply.
- Every reader calls it, with no branch of its own:
  - the part's scan (`req_run_tests`, window and [K66] whole run);
  - `<PREFIX>_REQ_RUN`'s `@idx` and `<PREFIX>_REQ_BYTE`, through the facts layer's new
    `pcrec_fact_stamp_req_run`/`_req_byte` (the fact asked as `pcrec_fact_stamp` asks it, rendered
    with the given member);
  - the [OPT-REQPOS] note;
  - `req_set_leads_own`;
  - the pick shadow.
- The truncation window keeps pcrec's index (`r->idx`). The resolver is LOUD if the reply's member
  differs from it: one rule over one statement (§3.4's "a trace build asserts it", here in every
  build).
- **Layering reading (for main).** The `req_byte`/`req_run` FACTS, in the facts layer and the
  `--emit-facts` listing, keep pcrec's index. The facts layer cannot ask the kit (gen is to its
  right), and the assertion makes the two one value. The STAMPS read the resolver.
  - This reads "artifacts where no site states R keep pcrec's index" as: the resolver asks the run
    window's statement wherever a window exists (`len >= 2`), whether or not this artifact emits a
    run pre-check.
  - The answer is identical by the assertion. The alternative, asking only where a part is defined,
    would make the stamp depend on emission order.

**prefix_k's selection is deleted** (`src/opt/prefix_k.c`, `PrefixKSets`, `pcrec_prefix_ksets`).
- The walk (`kset_walk`) stays as a fact.
- **B5:** `unanch_start`, the builder that states frequencies, asks `pcrec_find_byte_rate` for
  exactly the population prefix_k asked it (every offset-0 prefilter). So `_FINDINGS`' consulted
  line and the UNDERIVABLE/BROKEN diagnostics do not move (sweeps: 0 movers on stamps and stderr).
- The `prefix-k` trace record keeps its key and now prints the reply's path. It is trace-only: the
  `--trace` family, which is not one of the arms.

**D2 retired** (finder row, its pick FF_RUN, its fact SF_RUN_TERM).
- No pcrec site ever stated a RUN span 0. Such a site now takes the composer's own walk with no
  routed row, which is D2's pick's text.
- The finder listing is 16 rows. finder_history.md is updated.

**`MF_SITE_ABI` 20** (6-k3, "next at landing" — main numbers it at landing; I took 20 as briefed).
- No layout, `MF_VOCAB` or `MF_CLASS_V` move: `mf_wreply` is not part of `mf_class`, so the design's
  "MF_CLASS_V for the reply" has nothing to move.

### 2.2 Not done (each named; §6 has the rulings asked)

| item (brief / §4) | state | why |
|---|---|---|
| pcrec stops stating the old fields (`plan_hint`, `plan_pos`, `rank_*`, W0-W2, prefix facts, `absent`/`consumable`, `ctx`, `read_floor`, `end_back`, per-term `need`, `consumer`, `span_class` BOUNDED/CONTEXT) and the kit retires them from `mf_site` | NOT DONE; R1 | the family's E rows render by TRANSLATING the plan into an old-field site that ofsskip/pffind/precheck/vrun read, and G2 (71M cases) builds old-field sites directly; deleting the fields means rewriting G2 and every renderer's input. Since 6-k1 the kit READS none of them on a window site (only `pred.fn_ref`), so pcrec's statements of them are dead; pcrec's own readers of its sites' old fields (`end_back`, `term[0].set`, the rank trace records S735-S737 detect) must move with them |
| `pcrec_run_pin`'s selection | NOT DONE; R2 | its member and stretch readings are gone from pcrec (`pin.idx` unread; C-pin's member/stretch are the reply's), but R's PLACEMENT (`w = pin.o - pin.at`, the walk offset spelling the stretch around a rate PICK) still comes from it, and the `run_pin` fact's listing text (`o`/`o:at+len`) is caller-visible (facts_listing §4.1.2¶7, tuning §2.30¶4, §2.39¶4: unchanged, so not edited) |
| RPT, `kit_report_exact`, `SF_PROOF_EXACT`, `FF_PROOF` | NOT DONE; R3 | window_site.md §4's last row keeps `mf_preview("R-26.6")` "until S3; then retires with RPT", and finder.c accepts "R-26.6" only while RPT names it: deleting RPT now refuses every kit-proof compile. Since 6-k1 every window REPORT site (pcrec's `cover`) is the family's; RPT serves only old-field REPORT sites (proof_check.c, G2) |
| registry §6 hunk | NOT NEEDED | no `--memfn=` options row moved (the memfn floor stays 12); D2 is a finder row, not an options row |
| spec hunks for the pin (tuning §2.30¶4, §2.39¶4, facts_listing §4.1.2¶7, findings' run-pin row) | NOT NEEDED YET | the pin's text and placement did not move (R2) |

## 3. The witnesses

### 3.1 Commit 5 (the flip): zero movers

emit_sweep against pre-S2 main 3cd809da1, at the commit-5 tip (old 12c07ea90, tree = a6d7634aa),
from a snapshot clone (`build/wsc5/snap-12c07ea90`) under the box lock. Logs are in
`build/wsc5/sw5/`.

| arm | movers | asymmetric |
|---|---|---|
| plain (c-default, c-vm, emit-ir, composition, facts, emit-ir-auto, stderr; dumps excluded) | 0 | 0 |
| `--arms start` | 0 | 0 |
| `-fno-run-prefilter` | 0 | 0 |
| `-fmemfn-simd` | 0 | 0 |
| `--engine=vm` | 0 | 0 (rc 1 is emit_sweep's "no differ floor pinned" on an unpinned `--extra` arm, plumbing, not a mover; the heavy job waives it with `--no-differ-floor`) |

**Commit 5's other evidence:**
- **Hand sample:** 13 witnesses × 5 flag sets, default vs the inverse lever: 0 of 65 differ.
- **The lever check:** `run_wreply.sh` (inverted) 125 passed, 0 failed; `--plants` 3 of 3 red.

**Reach floors per old row (§5.3).**
- The shadow's `arm` column compares the old row and the family's row per window site. It read 0
  over the whole corpus at wsc4's tip: job 579, `== wsc4 wshadow: 7 of 7 columns at 0, G2 clean 1`.
- Commit 5 changes neither side's decision, so each old row's site count equals its family path's
  site count. That meets every floor with equality.
- No separate per-row counter was built. After 6-k1 the old side no longer exists to count.

### 3.2 Commit 6 (the deletion): zero movers

At 6-t1 (old ecf1159d2, tree = 4cc748fa1), logs `build/wsc5/sw6p1/`:
- **plain:** 0 movers on every stream.
- **`--arms start`, `-fno-run-prefilter`, `-fmemfn-simd`, `--engine=vm`:** 0 on every ARTIFACT
  stream, but ONE mover on the `dumps` stream. That is `--list-limits`: 6-p1 had reworded
  `PCREC_OFSK_MAX_SET`'s description, which named the deleted `src/opt/prefix_k.c`. 6-p2 restores the
  text, so the row still names prefix_k.c; rewording it is filed for main (§5 F-3).
- **The tip (5bdeafe83):** the heavy job re-runs all five arms (§7).

**No pcrec abi event.**
- No emitted byte moved: the sweeps above, and the heavy job's at the tip.
- The `MF_SITE_ABI` number reaches no artifact (rR8). Its readers, by grep: the literal in
  `memfn/include/memfn.h` and `memfn/include/CLAUDE.md`, and through the macro in compose.c,
  presence.c, formhash.c, gate.c, generic.c, memfn_sites.c, g2_gen.c, g2_simd_gen.c, g2_driver.c and
  arm_fixtures.c.
- `tests/memfn/pins/arms.tsv` and `pins/m6_target/*` pin rendered TEXT and carry no number;
  test-memfn-arms is green after the bump.
- `memfn/docs/wake.md` cites "`MF_SITE_ABI` 19". That file is the kit manager's, so I did not edit it.

### 3.3 The derived sabotage table (§5.4's rule plus the suite rule)

**Commit 5.**
- Candidates: the 173 rows on the files 5a/5b/5c touched (emit_dfa.c, memfn_sites.c, internal.h,
  cli/main.c, window.c).
- Every anchor resolves. None lies in a changed hunk.
- Semantic risk: rows planting code the default path stopped reading. Their full run is below.

| set | rows | result |
|---|---|---|
| REACH_ONLY=1, the 173 | 173 | reached 127, unreached 0, declared-unreached 5, no-probe 41 (`build/wsc5/mech5/reach.log`) |
| full, PROCS=4 | 30 | 27 DETECTED (S1415, S1416 included); 3 UNDETECTED (EXPECTED: S487, S489, S490, pre-declared equivalent mutants); 0 unexpected, 0 anomalies (`build/wsc5/mech5/full.log`) |

**Commit 6.**
- Candidates: the 246 rows on the files commit 6 touched.
- Full run: the new and re-aimed rows, plus every row whose detector commit 6 edited (arms
  memfnfinder, memfnarch, memfnrows, registry): 76 rows. Both run in the heavy job (§7).

| id | change | successor / note |
|---|---|---|
| S281 | RETIRED (5c) | S1415: C-pin's clause 4 dropped in window.c `c_pin` (in\|instanceof takes run-pinned); DETECTED |
| S289 | RETIRED (5c) | S1416: C-pin's identity (stop = member) dropped (\Bfoo\B takes run-pinned); DETECTED |
| S187 | RETIRED (6-t1, with prefix_k.c) | S1417: the family's MARGIN never adopts RESEED (no offset-k form) |
| S188 | RETIRED (6-t1, with prefix_k.c) | S1418: pcrec states RESEED's F0 as k0 with no offer (MISCOMPILE-1 in the statement) |
| S287 | RE-AIMED (6-t1) | the guard not widened over the pinned stretch, in the reply-derived `ofs_test_of` |
| S448 | RE-AIMED (6-t1) | the run term takes the whole masked window, in the reply-derived `ofs_test_of` |
| S449 | RE-ANCHORED (6-t1) | the K66 whole run loses its mask (the scan member now the resolver's `m`) |
| S522 | RE-AIMED (6-t1) | the C4 row inflated is src/gen/CLAUDE.md's (prefix_k.c's row left) |
| S1412 | RETIRED (run_wreply plant; 6-t1) | NEXT reading the pick: the pick is gone (no successor needed: no code left to plant) |
| S1414 | RE-ANCHORED (run_wreply plant) | on `next_keys[]`; RED |

New ids are taken from the kit range S1400-S1429: S1415-S1418 (S1419-S1429 free).

## 4. Light checks

| check | commit-5 tip | 6-t1 | tip (5bdeafe83) |
|---|---|---|---|
| `make strict` | clean | clean | clean |
| sabotage anchors | 901 rows / 932 sites resolve | 901 / 932 resolve (after the re-aims) | all resolve |
| `tests/codegen/run_codegen_tests.sh` | 331 / 0 | 331 / 0 | 331 / 0 |
| `make test-core` | rc 0 | rc 0 | rc 0 |
| `make test-memfn-*` (14 sections) | each rc 0 (g2 quick 71,217,801 / 0) | each rc 0 | each rc 0 (g2 quick 71,217,801 / 0) |
| `memfn/tests/run_g2_win.sh` | 6032 / 0 | 6032 / 0 (also at 6-k1 and 6-k2) | 6032 / 0 |
| `run_wreply.sh` | 125 / 0, plants 3/3 (inverted) | 112 / 0, plants 2/2 (reduced) | — |
| the sampled wshadow | retired with the old path (6-k1); no old side remains | — | — |
| also | — | limits_check 37/0; G7 lever fence PASS; test-kitproof, test-memfn-manifest/deleg rc 0 (at 6-k2) | test-memfn-arms/link/stamps/forms rc 0 (at 6-k3) |

## 5. Findings and deviations

**F-1, job 579 (wsc4's heavy) was RED, for a real reason.**
- The failing check is the [COMPOUND] G7 lever fence (test-compound): `run_wreply.sh` and
  `tests/memfn/CLAUDE.md` spelled the harness option outside the fence's allowlist.
- 579's other steps were green, including all five sweeps at 0 movers, the lever sweep, and wshadow
  7/7 at 0.
- 5a/5b/5c inherit the red; 6-t1 clears it (the lever and its mentions are gone).
- Reported to the kit manager.

**F-2, the design conflict on RPT (R3).** §4 vs Appendix A, as above.

**F-3, a listing mover filed rather than made.** `PCREC_OFSK_MAX_SET`'s `--list-limits` description
still names `src/opt/prefix_k.c`, which no longer exists. Rewording it moves the dumps stream. That
is a caller-visible listing change for main to approve (no spec paragraph restates it).

**F-4, the resolver asserts in every build** (§2.1), not only in a trace build. It is cheap: one
kit query per reader call.

**Deviations from the brief:**
- **Commit 6 is partial.** R1, R2 and R3 are asked, not ruled (§2.2, §6).
- **The heavy job's mech is two calls,** REACH_ONLY and the full set; the brief asks for ONE full
  call.
- **The branch was rebuilt once** (§1). The tree is unchanged; the shas changed.
- **Process slips:**
  - (a) Two hand loops of about 130 compiles ran outside the box lock: the 13 × 5 spot check, twice
    with the lever.
  - (b) A no-argument `run_sabotage_matrix.sh` (the full matrix) was started by mistake. It waited
    on the lock and never ran a row; it was killed with `scripts/safekill` 130457.
  - (c) While wsc4's job 579 ran, my light checks ran beside it (its perfrun note: contaminated=YES).
    No timing was involved.
- **Reach floors** are witnessed through the shadow's per-site `arm` column at 0 (wsc4's job 579),
  not through a per-row counter (§3.1).

## 6. Rulings needed (asked of the kit manager)

- **R1: what "retire" means for the old fields.** My proposal:
  - A window site stating any old decision field is REFUSED.
  - pcrec's builders stop filling them.
  - The fields no renderer reads are DELETED with their checks: W0-W2, the prefix facts,
    `absent`/`consumable`, `ctx`/`nctx` (generic's ctx test included), `read_floor`, `consumer` and
    REPORT's kind meaning.
  - `plan_hint`, `plan_pos`, `rank_*`, `end_back`, `span_class` BOUNDED/CONTEXT and `need` stay as
    the RENDERER INTERFACE the translation writes and G2 drives, never a host statement.
  - ofsskip and pffind stay arms; G2 reaches them directly.
- **R2: R's placement once the pin's selection retires.** The options:
  - a rate-free placement fact;
  - state no R where the stretches disagree;
  - keep the pin's placement as a fact for now.
- **R3: RPT and kit_report_exact.**
  - (a) Keep them, with the R-26.6 step, until S3. This is my leaning, per §4.
  - (b) Delete them now, keep "R-26.6" as a row-less step, and rewrite proof_check.c family D.

## 7. The heavy job (OWED)

`580-kit-wsc5-heavy` is QUEUED at the lane tip (kit band, `idle-ok`, cap 18000 s). Its `--ready`
first holds while main's `i2build-parity` is pending or running. Job file:
`worktrees/wsc5/build/wsc5/580-kit-wsc5-heavy`.

Steps:
1. `make -j16`.
2. emit_sweep `--ref 3cd809da1` on five arms: plain (dumps excluded), `--arms start`,
   `-fno-run-prefilter`, `-fmemfn-simd`, `--engine=vm` with `--no-differ-floor`.
3. `run_wreply.sh` and `--plants`.
4. REACH_ONLY over the 246 derived rows.
5. ONE `PROCS=4` matrix over the 76 derived rows.
6. `scripts/perfrun --label wsc5` (make test).

**Completion lines:**
- five `emit_sweep: DONE rc=0` (`expect sweeps=5`), each stream `movers=0`;
- `checks failed: 0` and `plants: 2 of 2 red`;
- `mech-reach-only: DONE rc=0 ... unreached=0`;
- `== mech run COMPLETE: 76 rows (unexpected: 0, ...)`, every row DETECTED or `(EXPECTED`;
- `== wsc5 heavy: 0 step(s) failed`;
- the make verdict: `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' build/wsc5/heavy/maketest.make.log`,
  empty = green.

Logs: `worktrees/wsc5/build/wsc5/heavy/*.log`, and the queue's job.log under
`worktrees/.boxqueue/done/<ts>-580-kit-wsc5-heavy/`. OWED: every verdict above; a fresh agent reads
them. The tree is clean after queueing; do not edit `worktrees/wsc5` until the job has started.

## 8. Checklist

| item | state |
|---|---|
| commit 5: the reply path is the default for every family site; the old path behind an inverse lever | done (5a); lever `window-legacy` (harness build) |
| commit 5's witness: emit_sweep vs 3cd809da1, every arm, zero movers; reach floors | done (§3.1) |
| `run_wreply.sh`'s identity half inverted | done (5c) |
| S281/S289 successors that reach the reply path | S1415/S1416, both DETECTED |
| commit 6: prefix_k's selection deleted | done (6-p1) |
| plan_hint/plan_pos/rank_*, old window fields, R-29's "stops stating" fields | NOT DONE (R1) |
| the kit's retired identifiers: RPT, kit_report_exact, SF_PROOF_EXACT, FF_PROOF | NOT DONE (R3); D2 retired (6-k2); ofsskip/pffind folded behind the family for every pcrec site (6-k1), still arms for G2 (R1) |
| pcrec_run_pin's selection | member/stretch readings gone; placement NOT DONE (R2) |
| stamps read the reply: _DFA_PREFILTER, _OFFSETS, REQ_RUN @idx (the part's reply) | done (6-p1) |
| ONE resolver; every reader calls it; the truncation window keeps pcrec's index | done (`req_run_member`; §2.1's layering reading) |
| byte-rate ask moved to the builder (B5) | done (`unanch_start`) |
| spec hunks | match_api §6.3.1¶5a, tuning §2.14¶2-¶3, §2.30¶2, findings §4 (6-c); the pin's and registry §6 not needed (§2.2) |
| MF_SITE_ABI 20, readers by grep, pins | done (6-k3; §3.2) |
| no pcrec abi event, proven | sweeps 0 movers on every artifact stream (§3.2); tip re-proven in the heavy job |
| the derived sabotage list | commit 5 run (§3.3); commit 6 in the heavy job |
| pcrec-path and kit-path commits separate | done (after the rebuild, §1) |
| light checks after each commit | green (§4); two named transients (§1) |
| heavy job queued, idle-ok, main's hold line, tree clean | `580-kit-wsc5-heavy`; OWED |
| report, lane index entry, kit journal | this commit |
