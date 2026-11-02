# rulepilot report: the rule-list pilot, designed, drilled and queued (2026-10-31)

Lane `rulepilot`, opus. Branch `lane/rulepilot`, from main `e0d716c7d`. No compiler code changed: nothing
under `src/`, `cli/`, `lib/` or `memfn/`. Spec: `docs/design/pricing_rulepilot.md` (pre-registered).
Instruments: `docs/dev/lanes/rulepilot_evidence/` (its own CLAUDE.md lists them). The data is OWED;
the timing jobs are queued.

## 1. Inventory (MEASURED, compile-only)

`inventory.py` re-runs the bake-off's dry census walk (`census_dry.py` copied verbatim from lane/bakeoff2
`b8a321ae3`) on this worktree's `build/pcrec`, over the 177 J1 questions. It then compiles every pick on
every site: 5,363 compiles for the walk and 5,160 for the picks, both under `scripts/boxlock run`.
Output: `rulepilot_evidence/inventory/` (`summary.txt`, `slots.txt`).

- **Population.** 172 of 177 compile (N06 N11 N12 N13 N25 refused).
  - **139 sites have >= 2 FORCEABLE default-route arms**: 590 arms, median 4, max 16. 70 of the arms
    are pick-only: a deny set that reached an arm on another site lands on new bytes here.
  - 33 sites are single-path.
  - The STOP RULE (< ~40) does not fire.
- **Choices by slot** (sites with a forceable choice in that slot): NEXT 95, FIRST 83, PRESENCE 46,
  LOCATE 27, RECOVER (dependent) 27, kit-only bytes 20, RETRY 1. RETRY varies only through the
  route seeds, which are not timed.
- **Out of the pilot, because they cannot be forced today:**
  - **The no-search NEXT arm.** L-ROW is missing, which affects 128 of 172 sites; the bake-off's dry
    census counted 112 over all arms. What this can hide: on those sites "skip no search at all" is a
    choice the pilot never times. So a rule-list PASS holds **on the forceable arms only**. A site
    where no-search is the real best reads as already at its oracle, and the pilot cannot see that
    loss.
  - **The kit's within-site options** beyond `no-fd-d1`/`no-window-skip` (L-KIT).
  - **The route-seed arms** (503: the engine choice, [SEL-COST]'s). These are counted and not timed.
- **Multi-flag paths.** 120 arms on 64 sites are reached only through a multi-flag deny set. They are
  TIMED through those deny sets, and the pick vocabulary includes every such set (below), so a rule can
  pick them.

## 2. Pieces, picks, list counts

- **Pieces.** 24 (`pieces.py`): 18 FACT/OPTION pieces over `--emit-facts` (`docs/spec/facts_listing.md`
  §4.1) and the compile options, plus 6 DECISION pieces over `cand_rows`' own stamps (§4.2).
  - Five are FITTED numeric pieces: req_run_len, req_set_size, start_set_size, min_width, kset_len.
    Their thresholds come only from the training half.
  - One is a CHOSEN class: req_byte_rare.
  - Four are constant on the 139 sites: anchored, nullable, end_pinned, land_char.
  - The per-site values are reproducible with `pieces.py inventory/facts.tsv inventory/sites.tsv`.
- **Picks.** 30 (`inventory/vocabulary.tsv`): the default plus every deny set by which the census first
  reached some arm. With single flags only, 64 sites could not reach their multi-flag arms.
- **Distinct lists.** These counts are for the drill's training half (118 literals): 30 of length 0,
  106,200 of length 1, 3.7e8 of length 2, and 1.3e12 of length 3. The real count is printed by the run.
  The search is exhaustive and exact, about 2 s on 139 sites.

## 3. Subjects, scoring, the drill

- **Subjects.** Detail is in spec §4.
  - Each question's own corpus file, streamed through grid2's `streamgen.py`.
  - Lengths are 64 B, 8 KiB and 1 MiB, x128 apart. The cap is 1 MiB and its reason is in spec §4.
  - Two density regimes are COUNTED per cell: miss = the least-dense windows; dense = matching lines
    alternated with filler.
  - **The 3-point grid locates a crossover only to within x128.** So per-length crossovers are reported
    as BRACKETS ("between 64 B and 8 KiB"), never as byte values. The x8, 6-point grid was cut to fit
    the time.
- **Scoring and PASS.** Spec §5, fixed before data.
  - The headline is an unknown length: equal weight per log-length point and per regime.
  - Scores are cross-fit over launches; the noise floor is regime_eval's NULL_c.
  - The split is seeded and stratified by slot signature.
  - PASS = held-out score >= 0.95 AND no held-out site slower than 1.5x its oracle beyond twice its floor.
  - `cand_rows` is the baseline, and over-fit is printed per k.
- **Drill** (`drill.py`, `drill.out`; seed 20261031 plus seeds 1-3, all as intended):

| truth | result |
|---|---|
| (a) planted 2 rules | PASS at 2, with the planted list itself (`if req_run_len >= 3 -> no-offset-skip; if dflt_presence -> k:no-fd-pres-g1; else default`), held-out 1.000. k=1 reads 0.945 with 5 tail sites: FAIL |
| (b) 4-way parity (unreachable by 3 rules) | FAIL; best held-out 0.66, over-fit +0.12 |
| (c) noise (costs unrelated to pieces) | FAIL; held-out 0.73-0.77, over-fit up to +0.11 |
| (d) null (identical arms, noise only) | PASS at 0; held-out 0.991, no tail site |

- **A defect the drill caught before data.** Thinning the fitted thresholds to 6 quantiles made (a) pick
  t = 2 and fail. Every distinct training value is now a candidate (thinned only above 12).

## 4. The timing job (scratch tier, this box)

- **Harness.** Reused, not written: grid1's ext-arm-set shape (`slot_build.py`, `gen_subj.py`) plus grid1
  `check.sh` plus grid2 `time.sh`, method `kit-grid@2`. This is the E8/flat slot's shape: CPU 14, 3
  launches, base launched three times, the rerun rule, a per-group quiet gate (LOADWAIT 15).
- **Smoke.** A 3-site smoke build took 1.7 s, and the gate passed 54 R + 72 C legs with 0 FAIL. A
  NOCLOCK time.sh pass of one site completed, and `read_slot.py` + `search.py` ran end to end on its
  raw file.
- **Jobs.** Numbers per ruling 17:05, all queued (`scripts/boxqueue add`, dry-run clean), every one
  not-before 2026-11-02T05:00:
  - `790-rulepilot-build`: cap 2400, expect sites=139. It re-emits all 590 arms and checks byte identity
    against the committed inventory. It REFUSES if `build/pcrec` changed since the inventory
    (`inventory/pcrec.sha256`). It builds about 6 GB of subjects under
    `/var/tmp/pcrec-pcrec/scratch/rulepilot/slot` and runs the gate.
  - `791`..`796-rulepilot-time.s1..s6` (about 38-40 min each) and `797-rulepilot-time` (about 16 min).
    Each has cap 3600 and idle-ok, and they are chained with `after`. The expected group count is
    re-read from the built slot at START.
  - `797` then runs `read_slot.py` + `search.py` and writes `OUT/search.out` / `search.json`.
- **Cost.** 139 sites, 810 groups, 3.6 h at grid2's measured 0.65 s per launch (4.2 h at 0.75), plus
  quiet waits.
- **Cut.** The x8 grid (6 lengths); the route-seed arms; the `.rxt` sample; every unforceable path.
- **Not cleared yet.** Frank has NOT yet cleared the Monday 05:00-09:30 window. The manager is asking
  him and moves or cancels the jobs if he says no (ruling 17:05).
- **Keep in place until 797 has been read:** the worktree `worktrees/rulepilot`, its `build/pcrec`, and
  the scratch slot. The jobs run the worktree's scripts and its compiler.

## 5. What each outcome means

This is spec §8.
- **PASS at k.** A short declared rule table is enough for the FORCEABLE choices, and the bake-off is
  unnecessary for them. It does not cover no-search, the kit's internal options or the engine choice.
- **FAIL at 3** with the oracle well above `cand_rows`: the measured case for pricing.
- **Baseline already >= 0.95 with no tail:** nothing on the forceable paths is worth pricing.

Two caveats apply to every outcome:
- **J1 is spent.** It is the regime evaluator's judge population; a list fitted here cannot be judged
  on J1.
- **Correctness is checked against the default arm, not libpcre2.** The deny flags' answer identity is
  `make test-axes`' job.

## STATE AT HANDOFF

- **Commits.** All work is committed on lane/rulepilot: spec, scripts, inventory, drill output, jobs,
  this report and the history-index line.
- **Rulings.** The rulings file was read before the job and before this report. The last entry applied
  is **2026-10-31 17:05** (renumber to 790-797; full design; enqueue; report items). All of it is
  applied.
- **Scratch.** `/var/tmp/pcrec-pcrec/scratch/rulepilot/`: `inv/` (inventory working copy), `slot_smoke/`
  (130 MB, deletable), and `slot/` (created by job 790; about 6 GB; delete after the reading).
- **OWED: `rulepilot-time`**, the last of the chain `rulepilot-build` -> `rulepilot-time.s1..s6` ->
  `rulepilot-time`, not-before 2026-11-02T05:00.
  - Completion line in the job log: `time.sh: COMPLETE rows=N groups=51 ...` for the last shard, after
    the pilot's `VERDICT: PASS at k rule(s)` or `VERDICT: FAIL (no list of <= 3 rules passes
    held-out)` line.
  - The full reading is in `/var/tmp/pcrec-pcrec/scratch/rulepilot/slot/search.out`.
  - **A fresh agent completes the delivery:**
    - read `search.out`;
    - report the per-length crossovers as x128 brackets;
    - report the excluded arms (`slot/excluded`, counted by `read_slot.py`);
    - report the density table (`slot/subj_rp.tsv`);
    - add a short results section to this report.
  - If a shard fails, run `scripts/boxqueue retry <key>`; the later shards wait on it.

## rpfix (2026-11-02): pre-timing exclusion of N20

- **Cause.** Job 790-rulepilot-build failed at 02:00:53 ( on N20: 
  missing; lane rwfix removed it as mojibake). No timing had run.
- **Check.** All 139 sites checked against : N20 is the only missing subject file.
- **Excluded: N20** (ruling 2026-11-02 02:15). Mechanism: , read by
  , , ;  computes the split over the original 139
  (excluded sites as stubs) and drops the stubs, so no other site changes half.
- **Held-out effect.** N20 was a TRAIN site (72 -> 71 training; held-out 67 unchanged). The pre-registered
  rule is unchanged; the population is 138 sites, 586 arms, 804 groups. The drill still passes all four
  truths ( re-run).
- **Jobs.**  regenerated them (NOT_BEFORE set to the queued 02:00). Changed in the queue:
   (N20 and P11 moved: 22 sites, 132 groups) and 
  (27 sites, 153 groups), edited in place; 790 re-added as  (expect sites=138,
  witness arms=586); 791-794 and 797 are byte-identical to the queued ones. Every job passes .
   re-reads the failed run's stored copy, so  from the
  lane's fixed source was used instead.
- **Design note:**  "Pre-timing exclusions".

### STATE AT HANDOFF (rpfix)

- Rulings read: last entry applied **2026-11-02 02:15**.
- Queue: 790 pending (not-before passed; waits for the running 799-landr30-test), 791-797 chained behind
  it (their "waiting on rulepilot-build, which FAILED" line clears once 790 is pending/done).
- OWED unchanged: the timing chain and the reading (see the first STATE AT HANDOFF above); the site
  count to expect is 138.
