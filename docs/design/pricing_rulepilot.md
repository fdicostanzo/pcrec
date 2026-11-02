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

- **Site N20** (pattern on ) is excluded. Lane rwfix removed that file from the
  corpus cache as mojibake; N20 targets the mojibake itself, so no replacement has the property. The
  manager ruled: no refetch, no substitute. A check over all 139 sites found N20 the only one whose
  subject file is missing under .
- **Declared in** , read by ,
   and .
- **Population:** 139 -> **138** sites (590 -> 586 arms, 810 -> 804 groups). The rest of this document's
  139 figures describe the inventory as committed.
- **Split unchanged:**  passes N20 to  as a stub (id and stratum only), the split
  is computed over all 139, and the stub is then dropped. Every other site keeps the half it had. (A
  plain drop would have moved 3 other sites between halves.)
- **Held-out effect:** N20 fell in TRAIN (72 -> 71 training sites; held-out stays 67). The stratum was
  read from the census arms (all arms), as the timed arms are not known yet; if a gate-excluded arm
  changes N20's stratum signature this could differ, and the stub then follows the timed data.
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
