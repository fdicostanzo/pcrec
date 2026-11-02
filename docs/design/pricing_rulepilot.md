# Pricing rule-list pilot: can 1-3 simple rules pick a site's search strategy?

**Status: PRE-REGISTERED (lane `rulepilot`, opus, 2026-10-31). The design is fixed; the data is OWED
(queue key `rulepilot-time`). No compiler code changes.** Evidence and scripts:
`docs/dev/lanes/rulepilot_evidence/`. Report: `docs/dev/lanes/rulepilot_report.md`.

## 0. Goals (ranked; conflicts resolve upward)

| # | goal | who benefits | measurable form |
|---|---|---|---|
| G1 | **Answer Frank's question cheaply**: does a list of <= 3 rules reach 95 % of the measured best, with no bad tail | Frank, the pricing decision | one pre-registered verdict (PASS at k / FAIL) from about 4 h of scratch timing |
| G2 | **Honest**: rules chosen on half the sites, graded on the other half; the search drilled before any data | whoever acts on the verdict | the four drills land as intended; over-fit (train minus held-out) is printed for every k |
| G3 | **Baseline first**: `cand_rows` scored on the same footing | the arch side | its held-out score and tail are printed next to every list |

Non-goals: pricing the engine choice, the no-search arm and the kit's within-site options (none can be
forced today); a Mac or Zen 1 reading; any change to the default build.

## 1. The question

Frank (2026-10-31): "Before we go crazy, let's see what is needed. How many choices can be made with
three rules." If a short decision list ("if P1 -> pick A; elif P2 -> pick B; elif P3 -> pick C; else D")
over facts pcrec already states gets within 95 % of the measured best strategy, the pricing bake-off
(`lane/bakeoff:docs/design/pricing_bakeoff.md`) is not needed. Today's chooser, the first-match
`cand_rows` table, is itself a hand-made rule list and is the BASELINE.

## 2. The inventory (MEASURED, compile-only, main `e0d716c7d`)

`inventory.py` re-runs the bake-off's dry census walk (`census_dry.py`, copied verbatim) over the 177 J1
questions (`docs/dev/lanes/rwquest/questions.tsv`), on the default route. It then compiles every pick
(below) on every site. Arms are told apart by byte identity.

| reading | count |
|---|---|
| questions / compile / refused | 177 / 172 / 5 (N06 N11 N12 N13 N25) |
| sites with >= 2 FORCEABLE default-route arms (the population) | **139** (590 arms; median 4, max 16) |
| single-path sites | 33 |
| sites with a choice in slot: NEXT / FIRST / PRESENCE / LOCATE / RETRY / kit-only bytes | 95 / 83 / 46 / 27 / 1 / 20 |
| arms reachable only through a multi-flag deny set | 120 arms on 64 sites |
| NOT forceable today, so OUT of the pilot: the no-search NEXT arm (needs L-ROW) | 128 of 172 sites |
| NOT forceable today: the kit's within-site options beyond `no-fd-d1`/`no-window-skip` (need L-KIT) | every kit site |
| counted, not timed: route-seed arms (`--engine=`, `-f[no-]prefilter`), the engine choice ([SEL-COST]) | 503 |

Every census arm is forced by public flags by construction. A path that cannot be forced is not in
the pilot. The STOP RULE (fewer than ~40 sites with >= 2 forceable paths) does not fire.

## 3. Pieces, picks and lists

- **Pieces** (`pieces.py`): 24 yes/no questions over the `facts` and `decisions` sections of
  `--emit-facts` on the default compile (`docs/spec/facts_listing.md` §4.1, §4.2) and the compile
  options. Nothing is measured from a subject.
  - The 18 FACT/OPTION pieces are anchored, nullable, has_req_run, req_run_len, req_run_caseless,
    has_req_byte, req_byte_rare, req_set_size, start_set_size, start_set_one, min_width, fixed_width,
    end_pinned, has_kinds, land_char, kset_len, caseless and utf.
  - The 6 DECISION pieces read `cand_rows`' own stamps: the default NEXT row is literal, byte or
    first-set; presence is emitted; LOCATE is rev-end/cover; the engine is VM. A list that uses them
    corrects `cand_rows` rather than replacing it, and the report says so.
  - Five pieces are numeric and **FITTED** (req_run_len, req_set_size, start_set_size, min_width,
    kset_len): `value >= t`, with t taken only from the TRAINING half's values.
  - `req_byte_rare` uses a CHOSEN, unmeasured "common text byte" class.
  - Four pieces are constant on this population (anchored, nullable, end_pinned, land_char).
- **Picks** (`inventory/vocabulary.tsv`): 30. These are the default, plus every deny set by which the
  census first reached some arm (single flags and the multi-flag sets). A pick is "compile with these
  flags added"; applied to any site, it lands on one of that site's timed arms.
- **Distinct lists** (literal sequences x picks^(k+1); a literal is a BOOL piece or its negation, or a
  fitted `>= t` / `< t`; 118 literals on a training half of the drill's shape): 30 lists of length 0,
  106,200 of length 1, 3.7e8 of length 2, 1.3e12 of length 3.
- **The search is exhaustive and exact.** For a fixed literal sequence the buckets are disjoint, so each
  bucket's best pick is chosen on its own (`search.py`).

## 4. Subjects (`gen_subj.py`, reusing grid2's `streamgen.py`)

- **Source.** Each site's subjects come from its own question's first corpus file (as E8 did; never
  `sealed/`).
- **Streaming.** Every subject is streamed: `nbuf_for(L)` distinct buffers, 4 MiB of distinct data,
  16-1024 buffers.
- **Lengths.** 64 B, 8 KiB and 1 MiB, x128 apart. The x8 grid of 6 points was CUT to fit the budget.
  - The CAP is 1 MiB. There, fixed per-call costs are below 0.1 % of a find-all call for any arm
    slower than 0.1 ns/B, and 16 x 1 MiB already leaves L2. Longer subjects read as "large" (CHOSEN).
- **Two density regimes, both COUNTED per cell by the default arm's `chk`.**
  - **miss**: the least-dense nbuf of 4 x nbuf strata-spread windows. For a rare question these are
    no-match windows; for an everywhere question they are the least dense the file has.
  - **dense**: every match in the file's first 4 MiB, widened to its line (at most 120 B each side),
    alternated with an equal-length filler window. A question with no match there has no dense regime.

## 5. Scoring and the pass rule (PRE-REGISTERED, fixed before data)

- **Headline (an UNKNOWN length, manager's ruling).**
  - Per cell, take each arm's time over the cell's best arm.
  - For each regime, average those ratios over the lengths with equal weight per log-length point;
    then average over the regimes with equal weight: H(arm) >= 1.
  - The site oracle is o = argmin H. A pick's score is s = H(o) / H(pick).
  - The list score is the reach-weighted mean of s, where each J1 question is one pattern of reach 1.
  - Scores are CROSS-FIT over launches: odd rounds choose, even rounds are read, then the reverse.
- **Noise floor.** Per cell, phi = max(|base#b - base|, nu x base) / base, where nu is the median
  |base#c - base| / base over every cell (regime_eval's NULL_c). A site's floor f is the rms of phi.
- **Split.** Stratified by the site's differing-slot signature (strata under 4 are merged). Within a
  stratum, sites are ordered by sha256(`rulepilot-split-2026-10-31` || id) and assigned alternately
  TRAIN / HELD-OUT.
- **PASS at length k.** The list chosen on TRAINING (highest score, then fewer tail sites, then fewer
  non-default picks) must, on HELD-OUT:
  - (1) score >= 0.95, and
  - (2) have no site with s < 1 / (1.5 x (1 + 2f)), i.e. no site slower than 1.5x its oracle beyond
    twice the floor.
- **Verdict.** The smallest passing k in 0..3, or FAIL.
- **Also reported:** `cand_rows`' own score (default everywhere) on both halves, and over-fit (train
  minus held-out) per k. Per-length crossovers in bytes are evidence and are not scored.

## 6. The drill (`drill.py`, `drill.out`: synthetic, 139 sites, the real 30 picks, this design's cells)

| truth | must | result (seed 20261031; seeds 1-3 the same) |
|---|---|---|
| (a) planted 2-rule list, every other arm 1.3-2.5x slower | PASS at 2, the planted rules | PASS at 2: `if req_run_len >= 3 -> no-offset-skip; if dflt_presence -> k:no-fd-pres-g1; else default`, held-out 1.000 |
| (b) 4-way parity of four pieces (no 3-rule list can say it) | FAIL | FAIL: best held-out 0.66 at k=3, over-fit +0.12 |
| (c) noise: arm costs iid 1-2x, unrelated to the pieces | not pass | FAIL: held-out 0.73-0.77, over-fit up to +0.11 |
| (d) null: identical arms, noise only (a control on the tail bar) | PASS at 0 | PASS at 0, held-out 0.991 |

The drill caught one design defect before any data existed. With thresholds thinned to 6 quantiles,
(a) missed t = 3. Thresholds are now every distinct training value, thinned only above 12.

## 7. The job (scratch tier, this box)

- **Harness.** grid1's ext-arm-set shape plus grid2 `time.sh` (method `kit-grid@2`: CPU 14, 3
  launches, the base launched three times, the rerun rule, the per-group quiet gate). It is reused, not
  written: the same harness as the E8 and flat slots.
- **Jobs.** `790-rulepilot-build` re-emits every arm, checks byte identity against the inventory, builds
  the subjects, and runs grid1 `check.sh` (answers vs the default arm). Then `791`..`796
  rulepilot-time.sN` (~40 min each) and `797-rulepilot-time` (~16 min), chained with `after`. The last
  job runs `read_slot.py` + `search.py` and prints the VERDICT.
- **Constraints.** not-before 2026-11-02T05:00; cap 3600 each.
- **Cost.** 139 sites, 810 groups, about 3.6 h at 0.65 s per launch (4.2 h at 0.75), plus quiet waits
  and about 6 GB of subjects under the scratch slot.
- **Cut.** The x8 6-point length grid, the route-seed arms, the `.rxt` sample, and every unforceable path.

## 8. What each outcome means

- **PASS at k <= 3.** A short declared rule table (the k literals and picks) does the job. It belongs on
  the arch side as data (memory: decisions as first-match tables), and the bake-off is unnecessary for
  the forceable choices. A passing list that reads DECISION pieces corrects `cand_rows` rather than
  replacing it; the report keeps that apart.
- **FAIL even at 3 rules**, while the oracle sits well above `cand_rows`, is the measured case for
  pricing: the gap no short list closes is what a priced argmin must win.
- **The oracle near `cand_rows`** (the baseline already >= 0.95 with no tail): nothing on the
  forceable paths is worth pricing. The open question moves to the paths the pilot cannot see.
- **What the pilot cannot see, whatever the outcome.** No-search NEXT arms (128 sites need L-ROW), the
  kit's within-site options (L-KIT), and the engine choice. Those stay the bake-off's.
- **Leakage.** J1 is the regime evaluator's judge population. A list fitted here is fitted on J1, so
  J1 can no longer judge that list; J1b stays sealed.

## Pre-timing exclusions

Dated 2026-11-02 (after the first build job failed at 02:00, before ANY timing: no clock had run).

- **Site N20** (subject file `nonenglish/pg20175.txt`) is excluded. Lane rwfix removed that file from the
  corpus cache as mojibake; N20 targets the mojibake itself, so no replacement has the property. The
  manager ruled: no refetch, no substitute. A check over all 139 sites found N20 the only one whose
  subject file is missing under `worktrees/.corpus`.
- **Declared in** `docs/dev/lanes/rulepilot_evidence/inventory/exclusions.tsv`, read by `slot_build.py`,
  `mkjobs.py` and `read_slot.py`.
- **Population:** 139 -> **138** sites (590 -> 586 arms, 810 -> 804 groups). The rest of this document's
  139 figures describe the inventory as committed.
- **Split unchanged:** `read_slot.py` passes N20 to `search.py` as a stub (id and stratum only), the split
  is computed over all 139, and the stub is then dropped. Every other site keeps the half it had. (A
  plain drop would have moved 3 other sites between halves.)
- **Held-out effect:** N20 fell in TRAIN (72 -> 71 training sites; held-out stays 67). The stratum was
  read from the census arms (all arms), as the timed arms are not known yet; N20 is never timed, so its
  stub keeps that census-arm stratum.
- **The pass rule is unchanged** (held-out score >= 0.95 and no tail beyond 1.5 x (1 + 2 f)). Only the
  training population is one smaller.

## 9. The standing questions (`docs/design/CLAUDE.md`)

1. **Measurement regime: RELEVANT.** One box (Zen 4, CPU 14), streamed subjects, 3 lengths x 2
   COUNTED density regimes, find-all calls, SIMD-off default build. Results hold for that regime only.
2. **Independent control: RELEVANT.**
   - The oracle is a timing, independent of every rule.
   - Correctness is checked against the default arm, not libpcre2. The answer-identity of the deny
     flags is `make test-axes`' job.
   - The drill checks the search against planted truths in both directions.
   - The split is salted and stratified, and fixed before data.
3. **What moves when data is regenerated: RELEVANT, and nothing in the default build.** A new compiler
   moves arm bytes; the build job refuses a mismatch with the committed inventory, so a re-run needs a
   re-inventory first.

## Timing re-plan (2026-11-02)

- **Measured rate.** Shard 1 (791) ran 02:36-03:36, was capped at 3600 s, and finished 59 of its 123 groups with
  0 quiet-gate waits: about 1 min per group, twice the planned 0.75 s per launch. Shards 792-797 were cancelled
  before starting. The slot job 790 built (138 sites, 586 arms, 763 timed groups) is valid and is not rebuilt.
- **Resume rule.** `grid2/time.sh` takes `RESUME=1` (and `GROUPS_FILE`). A group is skipped only if the log has its
  `# group N done:` line AND the raw file holds exactly launches x arms-per-launch rows for it. Rows of any other group
  of the run's list (the one in progress at a kill) are moved to `raw_*.tsv.discarded` and the group is re-timed whole;
  the raw file is otherwise only appended to. Each group launches its own base copies (3 per round) and carries the
  quiet gate at its start, so a resumed group is methodologically identical to an uninterrupted one. Self-test:
  `bash grid2/time.sh --selftest-resume` (no clock). All 59 of shard 1's groups were checked complete against this rule.
- **Shard plan.** The remaining 704 groups (763 minus 59) are 16 chunks of at most 45 groups (15 x 45, then 29), in
  `arms.py` order (deterministic), each `est` 60 s x groups, cap 3600: jobs `805-rulepilot-time2.c01..c16`
  (`rulepilot_evidence/mkjobs2.py`, `jobs2/groups.cNN.tsv`). c01 resumes shard 1's raw file (tag RP1); the rest write
  `RP2..RP16`. The held-out/train split is by site inside `search.py` and does not see the chunking.
- **Window.** Each chunk's `--ready` refuses (exit 75, `not-ready: outside window`) unless local time is 01:00-19:05,
  after the `after` check; a chunk started at 19:05 ends by about 19:55, before the owner's 20:00-01:00 hold. Chunks are
  chained in order and not-before 2026-11-02T13:30. The reading (`806-rulepilot-verdict`) is chained after c16, has no
  window and no quiet gate (pure python over the raw rows); it refuses unless all 763 groups have rows.
- **Two days.** About 11.7 h of timing: today 13:30 to about 19:20 (7 chunks), Tuesday from 01:00 (9 chunks). Each group is
  self-contained, so the straddle changes nothing about any group's measurement; a day boundary appears only as a gap in
  the raw timestamps.

## Reading rule (owner, 2026-11-02; recorded before any verdict exists)

The pilot is the BASELINE that a pricing model must beat, not a choice of mechanism. Its held-out timings (139 sites, ideal arm
per site) are the comparison set: any later pricing model is scored against the same truth and the best rule list found here.
A passing rule list does not by itself select rules: pricing's case is extensibility (a new method, e.g. a new SIMD form, arrives
as one priced row with its card; a rule list must be searched again). The regime is SIMD-off only (§9 item 1); the SIMD-on
layer is plan row [PILOT-SIMD]. A pricing build waits until the stream unification ([STREAM]) has moved further, since its
harness would change ([PRICE-BAKEOFF]).

Expected shape (owner, 2026-11-02): the final decision engine COMBINES rules and pricing. Some costs are not local to a site and
are hard to price: engine-switch (crossing) costs, the DFA's multi-path tracking lost when a stretch goes to the VM, whole-artifact
effects such as one site costing the frameless entry. These enter as policy rules (e.g. "prefer DFA"), a declared first-match
table; pricing chooses within the space the rules allow. This pilot does not test engine-level rules: the engine choice is
counted, not timed (header non-goals).

## Result (2026-11-02)

The verdict job `806-rulepilot-verdict` ran after the last timing chunk (log: `rulepilot-verdict: groups complete 1 763`).
Numbers are quoted as printed.

- **Population.** `read_slot: sites 138 (pre-timing exclusions 1), raw launches 18972, excluded arms 0, census arms not timed 0,
  picks fallen back to default 0`. Split: train 71 / held-out 67 sites; literals 148, picks 30. Distinct lists by length:
  0: 30, 1: 133,200, 2: 587,412,000, 3: 2,572,864,560,000.
- **Noise.** nu (median |base#c - base| / base) = 0.42%; median site floor f = 0.69%.
- **Baseline (the default arm everywhere).** Train 0.9742, tail 1; **held-out 0.9812, tail 0, worst 1.183**.
- **Lists** (each chosen on training, read on held-out):

      k=0: else -> no-run-prefilter
           train 0.9759 tail 1 | held-out 0.9816 tail 0 worst 1.183 | over-fit -0.0056 | PASS
      k=1: if req_set_size >= 5 (FITTED) -> no-offset-skip; else -> k:no-fd-pres-pick
           train 0.9806 tail 1 | held-out 0.9838 tail 0 worst 1.183 | over-fit -0.0033 | PASS
      k=2: (2 rules + else)
           train 0.9853 tail 0 | held-out 0.9722 tail 1 worst 2.398 | over-fit +0.0131 | fail
      k=3: (3 rules + else)
           train 0.9915 tail 0 | held-out 0.9758 tail 1 worst 2.308 | over-fit +0.0157 | fail

  The k=2 and k=3 lists are in `slot/search.out` (scratch tier); they over-fit (+0.0131, +0.0157) and fail the tail test.
- **VERDICT: PASS at 0 rule(s).** The k=0 line is one non-default pick (`no-run-prefilter`) and it gains 0.0004 on
  held-out over the default (0.9816 vs 0.9812): the default itself already passes both pre-registered conditions.

### Reading (per the Reading rule above)

The pilot is the BASELINE a pricing model must beat, not a mechanism choice. Within-engine headroom over today's default is
about 2% in this regime (held-out 0.9812 means the default runs at 98.1% of the per-site ideal arm). A rule list buys at most
0.0026 (k=1, 0.9838) on held-out and none of k=2/3 generalises. So pricing's case is EXTENSIBILITY (a new method, e.g. a new
SIMD form, is one priced row with its card; a rule list must be searched again), not mean speed.

### Regime limits (what this result does not say)

Zen 4 (the Ryzen 7 7700X dev box) only; SIMD-off only ([PILOT-SIMD] is the SIMD-on layer); find-all mode; forceable arms only
(an arm the flags cannot force is not in the census); the ENGINE choice (DFA vs VM) is counted, not timed, so engine-level rules
(the expected-shape policy rules) are untested here.

### Run facts

- **c03's expect miscount.** One group (`rp-C14 rp_C14_m64-S`, load1 2.20 to 3.39 during bench renders) breached the load ceiling
  and was requeued, so 46 done lines covered 45 groups and the expect read `groups=46`: the job was recorded FAILED with its timing
  complete. The data is complete (45 distinct groups); the rulings file (2026-11-02 15:10) has the ruling, and c04 was gated on c03's
  log (45/45).
- **LOADMAX raised to 2.5** for c02-c16 (from 1.5; c01 kept 1.5), with the pre-start quiet loop at 2.5, because bench light
  renders (cores 0-5, nice 19, at most 2) were allowed during the pilot. Counted from the groups' `load1-at-start` fields in
  `time_RP2..RP16.log`: 663 group-done lines (659 distinct groups plus 4 requeued repeats); **659 of the 663 started at load1
  >= 1.5** (452 at >= 2.0; maximum 2.48). By chunk header, 13 of the 15 chunks began their first group at >= 1.5. **Requeued: 4**
  (c03: 1, c07: 2, c11: 1; c01 none). Method note: the per-group base controls (#b/#c) absorb drift and the noise figures
  above are measured from them, but the groups with load in [1.5, 2.5) are identifiable from the log if a later reading needs
  to exclude them.

### The worst sites (input to ONE bounded look later; nothing proposed here)

Ratio r = 1 / s of the default arm (`a0`) against the site's ideal arm, cross-fit as `search.py` computes it (loaded through
`read_slot.py`'s dataset and `site_scores`; the held-out worst reproduces 1.183). The pattern is from the census.

| site | split | default | ideal | ratio | pattern |
|---|---|---|---|---|---|
| P05 | train | a0 | a2 (`-fno-start-set`) | 1.581 | `\b(?:Mr\|Mrs\|Miss\|Dr)\.\s+[A-Z][a-z]+` |
| B12 | train | a0 | a1 (`--memfn=no-fd-d1`) | 1.280 | `[0-7]{11}\x00` |
| B05 | train | a0 | a2 (`--memfn=no-fd-d1`) | 1.240 | `ustar\x0000` |
| C11 | train | a0 | a6 (`-fno-offset-skip --memfn=no-pres-set-lead`) | 1.214 | `\bfunction\s+(\w+)\s*\(` |
| C25 | held-out | a0 | a1 (`-fno-offset-skip`) | 1.183 | `\bf"[^"]*\{[^}]+\}[^"]*"` |

C25 is the held-out worst (1.183). The next two by distance are P23 (1.175, `\bwas\s+\w+ing\b`, ideal a1 `-fno-offset-skip`) and
S03 (1.141, held-out, ideal a1 `--memfn=no-fd-pres-pick`). P05 and the C25/P23/C11 group are all offset-skip or start-set prefilter
choices (the default's `RX_DFA_PREFILTER` is `first-class-bounded` / `offset-set-bounded`; the ideal is `handoff` or `first-memchr-bounded`).
