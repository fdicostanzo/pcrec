# wsc6 — D172 S2 commit 6 completed: the old fields retire, the pin's placement kept, RPT until S3

Lane wsc6 (kit lane of the memfn kit manager), 2026-10-22. Worktree `worktrees/wsc6`, branch
`lane/memfn-wsc6`, cut from `lane/memfn-wsc5` @ 2c6c91e88. Build go: Frank's conditional go for D172
(request R-29), as for wsc1-wsc5. The kit manager's rulings R1-R3 (final) are this lane's brief. Commits
5 and 6-k1..6-p2 are wsc5's: `docs/dev/lanes/wsc5_report.md` §1-§3. No rulings file was named.

STATE AT HANDOFF:
- **R1 (the old fields):** done as ruled (§2).
- **R2 (the run placement):** the FALLBACK, with evidence (§3); the general form is FILED.
- **R3 (RPT):** kept until S3; the design notes and the conflict are recorded (§4).
- **Light checks:** green after one fix (6-p4; the first pass found a real regression) (§6).
- **Owed:** the heavy job `582-kit-wsc6-heavy` is QUEUED (§7). It also carries wsc5's never-run
  derived set: wsc5's job 580 was cancelled by hand before it started.

## 1. The commits (main's review: path class per commit)

| # | sha | path class | what |
|---|---|---|---|
| 6-k4 | 40d09bbb8 | KIT PATH (memfn/ + the kit's checks in tests/memfn/) | the kit stops requiring `consumer` (and REPORT's RESULT check); `wf_parts_prepare` takes a FUNC part's `need` from the translation. R1's first step, so pcrec can stop stating them before the fields go |
| 6-p3 | 76e80e89b | PCREC PATH (src/ only) | every window site (PF/MLINE/VM-hat FIND, the offset-skip block, Z2's cover) and every pre-check FUNC part states its frame and R-29's facts ONLY; `consumer` stated nowhere; `pcrec_memfn_window_is_candidate`, `_span0_stated` (with `span0_exact_len` and its SITESTATED trace record), `_context_stop`, known.c's `cover_ctx_item`, emit_dfa.c's `ofs_pred_of`/`ofs_pred_rank`/`ofs_pred_trace` and findings.c's `pcrec_find_run_rank` deleted |
| 6-k5 | f10597df9 | KIT PATH (memfn/ + the kit's checks in tests/memfn/) | the old fields DELETED from memfn.h with their site_check rules, gate fields and readers; the renderer-interface refusal (`wf_old_fields`); `MF_SITE_ABI` 20's text; G2, proof_check/proof_run, arm fixtures and pins follow |
| 6-d1 | ab03255dd | DOCS (docs/design/) | window_site.md §4 and Appendix A: R3's note, R1's outcome |
| 6-t2 | c39988f36 | TESTS (tests/, Makefile comment) | the sabotage rows (retired, re-aimed, new, declared equivalent), the site manifest's companions, the rank check inverted |
| 6-p4 | 77927192f | PCREC PATH (src/ only) | the forward scan's storage point reads the set FIND's D11 bound off the window statement (6-p3 missed this `end_back` reader; §6) |
| (r) | this commit | docs (`docs/dev/lanes/`, the lane index, the kit journal) | this report |

**Condition 1 (path classes):** each commit's file list was checked before committing; the pcrec-path
commit 6-p3 touches only `src/`. The staged `git rm`s of the retired rows were left out of 6-k5 and 6-d1
(committed by path) and land in 6-t2.

**Bisectability, transient reds, each named:**
- **6-p3 deletes `ofs_pred_of`, `ofs_pred_rank` and `pcrec_find_run_rank`.** Until 6-t2: the anchor
  tripwire is red (S460, S731-S737), test-memfn-manifest is red (the PRE/OFS/VERIFY rows name
  `ofs_pred_of` as a companion), and test-memfn-rank is red (its brute-force claim has no ranking left to
  read). 6-t2 repairs all three.
- **6-p3 through 6-t2 refuse every bounded set PF FIND** (the missed `end_back` reader, §6); 6-p4
  repairs it.
- **6-k5 deletes the fields S849, S1222, S1223 and S1226 plant in.** Their anchors are stale until 6-t2
  retires them.

## 2. R1: the old fields

### 2.1 pcrec states R-29's facts only (6-p3)

A window site's `pred` now carries its FUNC name (`fn_ref`) and nothing else; the site states its frame
and `nalt`/`alts`/`wfloor`. A pre-check FUNC part states `fn_ref` and its part window. pcrec's own readers
of its sites' old fields moved to the window statement:
- `find_use`'s D11 check reads span 0's length (2 with the `{1: any}` bound) instead of `end_back`;
- the N4 door probe (`find_door`, probe build) reads span 0's set instead of `term[0].set`;
- `find_window`'s MLINE span states its byte as a one-member cube instead of copying the old term;
- the offset-skip site's `table_name` hook names window offers only (loud on any other id).

`deleg_check` still holds each site to its DELEG_SITES row: a window site's term kinds read as none, a
subset of every row's.

### 2.2 The kit (6-k4, 6-k5)

**Deleted, each with its site_check rules, gate field and readers:**

| field(s) | the readers found by grep, and their fate |
|---|---|
| W0-W2 `window_stated`/`move_back`/`overshoot`, `MF_MOVE_UNBOUNDED`/`MF_OVER_UNBOUNDED` | compose.c `window_check` (now W4's `decl_point` rule only) and the presence rule; gate.c's three classifiers; fields.def's rows and class `D_MIN`; kit.h's `MF_SERVES_WINDOW_ONLY`; finder.c/window.c contracts; formhash.c and the translation (writers); G2, arm fixtures (writers), arm pins' nine gate cases |
| `prefix_stated`/`exact_len`/`consumable_len` (`mf_prefix`) | compose.c `kit_proof_check`/`proof_clear`; gate.c's classifiers; fields.def; kit.h `MF_SERVES_PROOF_*`; no renderer |
| `absent`/`consumable` (`mf_absent`, `mf_consumable`) | compose.c's proof (`pred_proves`'s SATISFIES arm) and `context_facts`; generic.c's `ctx_pred_test` (the only RENDERER that read `absent`, and only on a CONTEXT predicate stating SATISFIES: no site stated one after 6-p3; the translation stated FAILS, which renders as the plain conjunction); gate.c `context_classes`; the RPT contract (`absent` NO) |
| `ctx`/`nctx` (`MF_MAX_CTX`) | generic.c `site_test` (the generic row's context test, ruled deleted with it); compose.c's proof and `kit_report_exact`; gate.c `ctx_classes`; every contract's `ctx` NONE |
| `read_floor` (`mf_read_floor`) | compose.c's rules; gate.c's classifier; no renderer |
| `consumer` (`mf_consumer`) | compose.c's two refusals (6-k4); the translation and `wf_part_site` (writers); no renderer |

`MF_MAX_AHEAD` STAYS: it is half of the proof range (`MF_MAX_FWD`, `mf_class.proven[]`'s size), not only
the context reach; its comment is restated. Deleting it would move `MF_CLASS_V`.

**The renderer interface stays** (`plan_hint`, `plan_pos`, `rank_*`, `end_back`, `span_class`
BOUNDED/CONTEXT, `need`), written only by the family's translation (window.c `translate`,
`wf_parts_prepare`) and by G2. memfn.h ("A WINDOW SITE STATES NOTHING ELSE", the `mf_pred` and `mf_site`
field comments, `mf_span_class`) and memfn/include/CLAUDE.md say exactly that.

**The refusal (loud):** `wf_check` runs `wf_old_fields` on every window site and, through
`wf_parts_check`, every pre-check FUNC part: a stated term (`nterm`), `need`, `plan_hint` (other than 0 or
`MF_NO_PRED`, the two spellings of "names no term"), `plan_pos`, `rank_n`, `span_class` or `end_back` is
refused, naming the field. It runs in phase 1 (`mf_wdecide`) and phase 2 (`mf_define`, `mf_ask`).
Witnesses: proof_check family A (seven refusals plus two accept controls) and plant S1419 (run_proof.sh,
RED).

**`MF_SITE_ABI` stays 20** (one S2 event, "next at landing"): its comment and memfn/include/CLAUDE.md now
record the layout move. No `MF_VOCAB` or `MF_CLASS_V` move. Readers of the number, by grep: the
`#define` in memfn.h and memfn/include/CLAUDE.md; through the macro, the kit's fills and refusals
(compose.c, presence.c, formhash.c, window.c, gate.c, generic.c), pcrec's fill (memfn_sites.c), G2's
generators and driver, arm_fixtures.c, proof_check.c, proven_check.c, prov_check.c. `memfn/docs/wake.md`
still cites 19 (the kit manager's file; not edited). The number reaches no artifact.

### 2.3 What moved in the checks

- **G2:** the old generators state span 0's class only. The retired `consumer` was a semantic-variant
  field (`G2_V_CONSUMER`); it leaves `G2_V`, and its random draw is kept (`(void)rn(2)`) so the generated
  space does not move. Two `consumer` refusal cases leave. Quick: 70,358,651 checks passed, 0 failed
  (71,217,801 before; the difference is the variant and the two cases).
- **proof_check / proof_run (`run_proof.sh`):** the retired facts' refusals, generated context items
  and SATISFIES cells go; the generated family states a term below the candidate where it stated a
  context item; family A gains the renderer-interface refusals; family D's REPORT row control is now a
  two-offset REQUIRED term below the candidate. proof_run's K35 floor is the FAILS cell below the subject
  (341,596 reached); the SATISFIES and after-span-0 cells are printed, unfloored.
- **Plants:** S1222/S1223 (generic's SATISFIES rendering) and S1226 (an UNSTATED `absent` accepted)
  retire with their code. S1255 and S1256 leave `--plants` and are DECLARED EQUIVALENT (§5).
- **Arm pins:** the nine W0-W2 gate cases retire (`GATE_CASE_FLOOR` 98 -> 89).
- **The rank check (test-memfn-rank) is INVERTED:** pcrec states no ranking, so every predicate pcrec
  hands the kit must carry `rank_n` 0 and name no RUN term; N4's door stays on the same probe. Its floor:
  5300 predicates (rq2's landing read 5,891; this tip reads 13,221: a floor, not a pin).

### 2.4 FILED (R1's follow-up, not built)

**Move the renderer interface into a kit-internal struct.** `plan_hint`, `plan_pos`, `rank_*`,
`end_back`, `span_class` BOUNDED/CONTEXT and `need` (and the old-field `mf_term`s they index) would leave
`mf_site`/`mf_pred`: the translation would build the kit-internal shape the renderers read, and G2 would
drive it directly. Trigger: the next G2 site-builder regeneration, or a renderer change.

## 3. R2: the run placement — the FALLBACK

**Built: the fallback.** pcrec keeps `pcrec_run_pin`'s placement as a stated fact (R stated as the
pinned stretch, widened over the walk-proven window positions, at `pin.o - pin.at`); its member and
stretch READINGS were already gone at wsc5 (`pin.idx` is read nowhere; C-pin's member and stretch are
the reply's). No code moved for R2 in this lane. The general form is FILED below.

**Why not the general form: it is not zero-mover, by construction.**
1. **The facts stream moves on every listing.** `run_pin` is a listed fact (`--emit-facts`,
   facts_listing.md §4.1.2¶7, tuning.md §2.30¶4): every listing carries a `run_pin` row
   (`foobar`: `run_pin ... derived yes 0`; `[ab]/user`: `... yes 1`). "pcrec_run_pin's selection retires
   entirely" removes or redefines that row, and even keeping the fact while its emitter readers retire
   flips its `used` column (`yes` is "a pass asked"). Either is a mover on emit_sweep's `facts` stream
   on every artifact, plus a facts_listing/tuning spec hunk.
2. **Artifact movers are possible, in three classes** (not counted; a census is the general form's first
   step):
   - the window's least-mass exact position lies in a stretch the walk does not spell while another
     stretch is spelled: today no pin, the general form pins;
   - another stretch covers offset 0 at a different placement and satisfies the PARKED condition: the
     general form states it in the PARKED alternative, and C-pin can fire there where today it cannot;
   - two stretches at different placements tie on mass: "ties HIGHER" by offset can differ from today's
     "highest window index".

**FILED: the general form** (to build when its movers are measured and accepted):
- **pcrec:** state every walk-proven maximal exact stretch of length ≥ 2 of the run window as its own
  R-shaped span (verify NO), each at its smallest spelling offset and widened over adjacent walk-proven
  positions (today's widening), deduplicated; in the PARKED alternative only those meeting §1.1's pin
  fact. `pcrec_run_pin` and the `run_pin` fact retire (facts_listing §4.1.2¶7, tuning §2.30¶4, §2.39¶4,
  findings §4's run-pin row; `tests/rxtsource`, `tests/litscan`, `tests/endmark/b3_*.tsv`,
  `tests/axes/start_landing_movers.tsv`, mech S280, S285, S306, per window_site.md §4).
- **kit:** C-pin's choice as a declared TIE-table row, read per OFFSET so no list order enters: over the
  offsets some R-shaped verify-NO span covers, the R-meet (the intersection of those spans' sets there);
  the member is the least-mass offset whose R-meet has one member (`pcrec_find_pick`'s rule: mass, ties
  HIGHER); the stretch is the maximal run of consecutive such offsets around it. With one R span this is
  today's rule exactly. F-8 relaxes from "R unique" to "R chosen by the declared rule"; plant S1409
  becomes two candidate stretches where the rule must choose by mass, not by order; G2's window
  reference (`g2_win_ref.c`) and its `two_runs` floor follow.
- **Trigger:** a measured mover census over the three classes above, and main's acceptance of the facts
  listing change.

## 4. R3: RPT until S3

RPT, `kit_report_exact`, `SF_PROOF_EXACT`, `FF_PROOF` and the `"R-26.6"` preview step STAY. window_site.md
§4 (a note under the table, and the RPT row's "(at S3, ...)") and Appendix A's "kit retires" line (a
note) now say they retire at S3, when REPORT is routed.

**The conflict, recorded.** §2.7 marked RPT and its companions RETIRE (path `report` at S3), §4's table
listed them among the rows that "retire at S2 unless marked", and Appendix A (filed verbatim as R-29)
said "the kit retires RPT, kit_report_exact, SF_PROOF_EXACT, FF_PROOF, D2" with no step. §4's own last row
kept `mf_preview("R-26.6")` "until S3; then retires with RPT". The two cannot both hold: the preview step
is accepted only while RPT names it, so deleting RPT at S2 refuses every kit-proof compile. Resolution
(R3): §4's last row wins; all of them retire at S3. D2 retired at S2 (wsc5, 6-k2). `requests.md`'s R-29
text is main's and was not edited.

**A consequence of R1 for RPT (finding F-2):** with `absent` and the context spans gone, no old-field
REPORT site remains whose chosen form proves other than exactly its REQUIRED sets (every REPORT term is
REQUIRED and every row tests its REQUIRED terms). `kit_report_exact` is true on every site; its decline
arm and its comparison range are unobservable until RPT retires.

## 5. The derived sabotage table

Candidates (window_site.md §5.4): the rows on the files wsc6's commits touched, plus wsc5's derived sets.
After 6-t2 the anchor tripwire reads 892 rows / 922 sites, all resolve.

| id | change | successor / note |
|---|---|---|
| S731-S734 | RETIRED (their code, `pcrec_find_run_rank`, deleted at 6-p3) | S1420 (the rank check's new claim) |
| S735-S737 | RETIRED (their code, `ofs_pred_rank` and its call, deleted at 6-p3) | S1420 |
| S849 | RETIRED (W0 deleted at 6-k5) | S1419 |
| S1222, S1223 | RETIRED (generic's SATISFIES arm deleted at 6-k5) | none in kind: absence is a span's core now; G2 window's S1404 (a core position read as outside the core) plants the rule that replaced it |
| S1226 | RETIRED (`absent` deleted at 6-k5) | S1419 |
| S1419 | NEW (kit, `memfn/src/window.c`): a window site's renderer-interface field accepted | arm memfnfinder; run_proof.sh plant RED |
| S1420 | NEW (pcrec, `src/gen/emit_dfa.c`): a ranking stated on a pre-check FUNC part | arm rank |
| S460 | RE-AIMED: the part's statement is `p[np++].fn_ref` | intent unchanged (the lead after the run) |
| S1148 | RE-AIMED: span 0 stated verify NO in `cover_window` | the window form of "span 0 not REQUIRED" |
| S1137 | RE-AIMED: the cover's floor stated EXPR | the window form of "the cover's read floor misstated" |
| S287 | DETECTOR MOVED: `harness` -> `offsetskip` | `ofs_pred_of`'s maxk check (its detector) retired; OfsTest.maxk now reaches the OFFSETS stamp, which run_offset_skip.sh's run-pinned witnesses read |
| S1255, S1256 | DECLARED EQUIVALENT (`SAB_EXPECT=UNDETECTED`, reason in the row) | F-2 (§4); they wake when S3 retires RPT, or retire with it |

New ids come from the kit range S1400-S1429: S1419, S1420 (S1421-S1429 free).

**Run sets (the heavy job):** REACH_ONLY over 373 rows (wsc5's 246 less the retired, plus every row
on a file wsc6 touched); ONE `PROCS=4` matrix over 155 rows (wsc5's 76 less the six retired, the new,
re-aimed and declared rows, and every row whose detector wsc6 edited: memfnfinder, memfnarms,
memfnmanifest, g2simd, g2gate, rank, kitproof, offsetskip). Lists:
`worktrees/wsc6/build/wsc6/{reach_ids,full_ids}.txt`.

## 6. The witnesses

**Zero movers (spot check, not the witness):** 24 compiles over five flag sets after 6-p3, and 18 after
6-k5, against a build of 40d09bbb8: 0 differ. The witness is the heavy job's five sweeps.

**Light checks at the tip** (`build/wsc6/light.sh`, logs `build/wsc6/light/`):

| check | first pass (at c39988f36) | after 6-p4 (77927192f) |
|---|---|---|
| `make strict` | clean | clean |
| sabotage anchors | 892 rows / 922 sites resolve | (unchanged) |
| `tests/codegen/run_codegen_tests.sh` | 322 / **4 failed** | 331 / 0 |
| `make test-core` | rc 0 | (not re-run: no core path touched) |
| test-memfn-manifest | 15 / **1 failed** | 15 / 0 |
| test-memfn-deleg | 13 / **1 failed** | 14 / 0 |
| test-memfn-rows | 229 / **2 failed** | 231 / 0 |
| test-memfn-finder | 2263 / **2 failed** | 2267 / 0 |
| test-memfn-rank | 6 / 0 | 6 / 0 (13,221 predicates, none stating a ranking; floor 5300) |
| test-memfn-arch/forms/reach/link/stamps/guarded/simdfloor/arms | each rc 0 (arms 374 / 0) | (not re-run) |
| test-memfn-g2 (quick) | 70,358,651 / 0 | (not re-run: no kit path touched) |
| `memfn/tests/run_g2_win.sh` | 6032 / 0 | (not re-run) |
| `run_wreply.sh` | 106 / **6 failed** | 112 / 0 |
| `run_wreply.sh --plants` | 2 of 2 red | 2 of 2 red |
| G7 lever fence | PASS | (not re-run) |
| test-kitproof | 81 / **7 failed** | 88 / 0 |
| limits_check | 37 / 0 | (not re-run) |

**The first pass's seven reds had one cause, fixed in 6-p4.** 6-p3 missed one reader of a window site's
`end_back`: the forward scan's storage point passed `pf_find.site->end_back` to `pf_find_of`, which then
refused every bounded set PF FIND as an internal error (`\bx`, `\B(?<!a)d`, `a*b$` under some flags). It
now reads the bound off the window's first span, as `find_use` does; byte-identical to 40d09bbb8 on six
failing witnesses. The checks the reds hid (manifest rule 5, kitproof's span facts) went green with it.
Logs: `build/wsc6/light/`, `build/wsc6/light2/`.

**Plants:** run_proof.sh `--plants` 11 of 11 red (S1221, S1224, S1225, S1419, S1251-S1254, ZK6, ZK7,
S1408); S1255/S1256 read GREEN, declared (§5).

## 7. The heavy job (OWED)

`582-kit-wsc6-heavy` is QUEUED at the lane tip (kit band, `idle-ok`, cap 18000 s). Its `--ready` first
holds while main's `i2build-parity` is pending or running. Job file:
`worktrees/wsc6/build/wsc6/582-kit-wsc6-heavy`.

Steps: `make -j16`; emit_sweep `--ref 3cd809da1` on plain (dumps excluded), `--arms start`,
`-fno-run-prefilter`, `-fmemfn-simd`, `--engine=vm` with `--no-differ-floor`; `run_wreply.sh` and
`--plants`; REACH_ONLY; ONE `PROCS=4` matrix; `scripts/perfrun --label wsc6` (make test).

**Completion lines:**
- five `emit_sweep: DONE rc=0` (`expect sweeps=5`), each stream `movers=0`;
- `checks failed: 0` and the wreply plants all red;
- `mech-reach-only: DONE rc=0 ... unreached=0`;
- `== mech run COMPLETE: 155 rows (unexpected: 0, ...)`, every row DETECTED or `(EXPECTED`;
- `== wsc6 heavy: 0 step(s) failed`;
- the make verdict: `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' build/wsc6/heavy/maketest.make.log`,
  empty = green.

Logs: `worktrees/wsc6/build/wsc6/heavy/*.log`, and the queue's job.log under
`worktrees/.boxqueue/done/<ts>-582-kit-wsc6-heavy/`. OWED: every verdict above; a fresh agent reads them.
The tree is clean after queueing; do not edit `worktrees/wsc6` until the job has started.

## 8. Findings and deviations

- **F-1, wsc5's heavy job never ran.** `580-kit-wsc5-heavy` reads `cancelled_by_hand` in the queue. Its
  sweeps, mech sets and make test were never measured; 582 covers both lanes' sets at this tip.
- **F-2, RPT's exactness is unobservable** after R1 (§4); S1255/S1256 declared equivalent.
- **F-3 (wsc5's), not acted on, as briefed:** `PCREC_OFSK_MAX_SET`'s `--list-limits` description still
  names `src/opt/prefix_k.c`.
- **F-4, S287's detector moved** (§5): the compile-time maxk check it relied on was `ofs_pred_of`'s.
- **F-5, two trace records leave with their statements:** `SITESTATED` (span0_exact_len's X0 record, read
  only by `docs/design/kit_proof/z2/z2.py stated`, a design tool no make target runs; its SPANSET half
  stays) and CANDTRACE `ofs-need` (read by no test).
- **F-6, the generic row loses its context test** (ruled). The family's floor row keeps the core rule for
  window sites; an old-field site can no longer state context (G2 never generated it).
- **Deviation:** R2 is the fallback (§3), with its evidence and the general form filed.
