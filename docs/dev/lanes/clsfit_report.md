# Lane clsfit — [CLS-TREE] S0 calibration: report

Lane `clsfit` (opus), branch `lane/clsfit` off `main` at `608bd094`,
2026-09-29. Analysis and design proposal only: nothing under `src/`,
`cli/`, `lib/`, `tests/` or `docs/spec/` changed. The full write-up is
`docs/design/cls_tree_design.md` §1.7. Every number below is cited there
to its file and column.

## What landed on the branch

- `studies/cls_tree_study/results/bench2_ubuntubudu_20260929.tsv` (4,620
  rows), `bench2_bytes_ubuntubudu_20260929.tsv` (132),
  `capC_isolated_ubuntubudu_20260929.tsv` (205). Each is the bench file
  copied verbatim (checked with `diff`) under a `# provenance:` first line
  naming pcrec-bench `scratch/clstree-s0` `81f0982` (the first two) and
  `d6e0106` (capC, which landed during this lane). The run was on
  ubuntubudu with gcc 15.2.0 at pin `dd3be4e4`.
- `studies/cls_tree_study/timefit_s0.py` is the analysis. It needs no
  timing and runs anywhere, about 90 s on the Mac. Its output is
  `results/timefit_s0_20260929.txt`.
- `studies/cls_tree_study/bench_bytes.py --dispatch switch` is the fair
  CLSPACK shape (default unchanged). A Mac smoke checked answers only: 24
  rows, 0 mismatches.
- `docs/design/cls_tree_design.md`: new §1.7, a status line, and §7(b)
  marked DONE, with one re-run OWED.
- `studies/cls_tree_study/CLAUDE.md` and `README.md` updated.

**Validation.** `python3 timefit_s0.py` ran clean (rc 0). The replay
reproduces all 60 of the harness's subject streams exactly (hits and
positional checksum, all 2^20 probes). The replayed kit sectionings match
`sweep_k53.tsv`'s section counts on 36 of 36. The 09-11 run's streams are
identical to bench2's (48/48), so the held-out test is exact. The proposed
λ diff below passes `git apply --check` against `608bd094`.

## Headline findings

1. **The refitted per-probe model predicts time, and the old term still
   does not.** The old `λ·Σops` term on the fresh run gives member r =
   +0.08 and 19/36 correct orderings. It replicates the refutation in every
   random regime. It tracks time only on `runs` (32/36), where branches
   predict. The new fit is one OLS over all 420 medians:
   `ns = 2.095 + 3.892·mispredicts + 0.189·branches − 0.090·loads + 0.095·deploads`.
   It gives r = +0.96 to +0.98 per regime over all arms, with the same
   values leave-one-set-out. On member subjects the kit policies get r
   +0.90 and 30/36 orderings. Applied unrefitted to the 09-11 run it never
   saw, it still gets 30/36 (the old term got 17/36). Results with and
   without `^C` agree.
   **Per-probe time is branch mispredicts, about 3.9 ns each.** The model
   does not separate one table from another: it puts `page3w` vs `page2w`
   at 0.095 ns, but the measured gap is 0.35-0.63 ns. It also cannot order
   the kit policies under `ascii`, where all three sit within 0.5 ns of
   each other.
2. **`page3w` comes close to `bitmap1`, and `page2w` matches it.** On
   member subjects `page3w` runs at 1.20-1.31× `bitmap1`, 0.44-0.63 ns
   above the 1.69 ns harness floor. It is 1.26-4.50× faster than the
   fastest kit policy, and faster in 57 of 60 set×regime cells. One cell
   ties at the floor and two go to the kit, each by 0.25 ns or less.
   `page2w` times the same as `bitmap1` in every cell at 2.9-3.8× fewer
   bytes, so `bitmap1` is dominated on both axes. Compared with today's
   pinned middle (kit λ16), `page3w` is 3.2× faster on member subjects
   (7.04 → 2.23 ns geomean) for +11% bytes.
3. **The DP with a time term does no better than a first-match rule here.
   This meets Frank's option-2 trigger.** Scanned over λ, the DP picks `K`
   at 0 and `page3w` on all 12 sets from 500 to 100,000 B/ns. It never
   picks a multi-section kit at λ > 4: λ256 loses to `page3w` on both
   bytes and time on all twelve sets. At `+2` the DP does worse than the
   table, picking `page2w` on only 2 of 12 even at 10⁶ B/ns, because of
   the resolution limit in finding 1.
4. **`^C` [r1 MEAS-2] is closed.** Over 41 isolated rounds every arm's
   max/min is ≤ 1.13, and the medians are within 3% of bench2's. The 09-11
   bimodality did not recur.
5. **CLSPACK: `atom` and `bitmap` tie at the floor, and the kit's reading
   is confounded.** The ns/call are 2.070 and 2.070 at N = 4, 16 and 32. The
   kit reads 4.7-5.9× slower, but the harness gives only the kit arm a
   per-site function-pointer call (bitmap and atom index data), so that
   gap is not the kit's test. On bytes, `atom` (256+8N) beats `bitmap`
   (32N) above N ≈ 11. It also beats the kit's `.text` at N = 16 and 32
   (384 vs 596 B, 512 vs 1,276 B).

## The CLSPACK recommendation

**Keep [OPT-CLSPACK] open as a SIZE-PRIORITIZED row. Build nothing yet.
One re-run of about a minute settles whether it can be the default.**
Proposed first-match rows for a byte-class site:

- **`−2`/`−1`:**
  1. `atom` if the artifact has ≥ 11 byte-class sites and ≤ 64 atoms.
  2. Otherwise the kit.
- **`0`..`+2`:**
  1. `atom` under the same condition, but only if the `--dispatch switch`
     re-run times it ≤ the kit at N = 16 and 32, beyond the round range.
  2. Otherwise the kit.

The owed command, verbatim for the executor (from an archive of this
branch's merge commit):

    CC=gcc gnutimeout 600 python3 studies/cls_tree_study/bench_bytes.py \
        --ns 4,16,32 --lam 16 --rounds 11 --dispatch switch \
        --out bench2_bytes_switch.tsv

It needs `make -C studies/cls_tree_study discover CC=gcc` first in a fresh
tree. Expect 132 data rows, with `dispatch=switch` in the header line.

## The λ re-proposal — PROPOSED (the manager takes it to Frank; NOT applied)

There are three distinct programs, not five. `K` is the kit DP at λ = 4.
`P3`, `P2` and `B1` are the whole-set 3-stage table, 2-stage table and
bitmap. One diff, in D103 shape ("the rubric proposes, placement is art"),
with `D<next>` as the placeholder for the ruling's number:

```diff
--- a/docs/design/opt_dial_design.md	2026-09-29 05:42:43
+++ b/docs/design/opt_dial_design.md	2026-09-29 05:43:04
@@ -965,9 +965,50 @@
 ARITHMETIC — the verified frontier table, the caps, and the worked
 selection on `\p{L}` all survive exactly as revision 2 derived them — and
 they are reframed as what they now are: **THE RUBRIC that chose the five
-constants once, not a live per-class mechanism the compiler runs.** The
-five values, pinned:
+constants once, not a live per-class mechanism the compiler runs.**
+
+**RE-PROPOSED AFTER [CLS-TREE] S0's CALIBRATION (D<next>, ruling D129
+Q1; evidence `docs/design/cls_tree_design.md` §1.7).** The ubuntubudu
+calibration re-confirmed that the pinned constants priced a term that
+predicts nothing (member r = +0.08, 19/36 on the fresh run) and fitted
+the per-probe model that does (r = +0.98 over all arms, kit orderings
+30/36, 30/36 again on the 09-11 run it was never fitted on): per-probe
+time is branch MISPREDICTS. On all twelve timed sets no multi-section
+sectioning at λ > 4 is selected at any price of time against bytes,
+because the whole-set three-stage table (`P3`) is faster than every kit
+policy in 57 of 60 set×regime cells at 1.01-1.23× the kit's size-minimal
+bytes. So the dial's class row is ONE kit constant and a FIRST-MATCH
+table over whole-set forms, with three distinct programs, not five:
 
+| position | the class matcher — first match wins | kit λ |
+|---|---|---:|
+| `−2` | the smaller of {`K`, `P3`} | **4** |
+| `−1` | = `−2` | **4** |
+| `0` | (1) `P3` if `K` has ≥ 16 sections and bytes(`P3`) ≤ 1.26 × bytes(`K`); (2) `K` | **4** |
+| `+1` | = `0` | **4** |
+| `+2` | (1) where `0` chose `P3`: the smaller of {`P2`, `B1`}; (2) as `0` | **4** |
+
+`K` is the kit sectioning DP's answer at λ = 4 (the size-minimal swept
+point, §4.3's own `−2`); `P3`/`P2`/`B1` are the whole-set three-stage
+table, two-stage table and single bitmap (`cls_tree_design.md` §1.3).
+Each row is a first-match rule; the DP is the optimizer INSIDE `K`, and
+"the smaller of" is an argmin inside one row. **The rubric proposes,
+placement is art** (D103 addendum): the 1.26 is §3.2's `z_mid`
+unchanged (every timed set's `P3`/`K` is 1.01-1.23, so `z_mid` = 20%
+would move six of the twelve back to `K`); the 16-section gate is a
+PLACEMENT at the bottom of the timed range (the twelve `K`s have 16-22
+sections) — below it the kit's tree is shallow and no timing exists, and
+a `bench2` arm over 2-16-section sets is the measurement that would move
+it. `+1` = `0` because `P2` costs 1.9-7.2× `P3`'s bytes for 1.20-1.37×
+member speed, outside `Z₁` = 1.30 on every set; `+2` takes it anyway, by
+Frank's 2026-09-16 direction that the huge-table forms are `+2`'s
+content priced at their measured rate, not excluded by `Z₂`. `B1` is in
+the `+2` row only as `P2`'s size tie-break: they time identically and
+`P2` is 2.9-3.8× smaller on all twelve sets.
+
+The superseded pins (−2 → 4, −1 → 16, 0 → 16, +1 → 64, +2 → 256),
+kept for the record:
+
 | position | λ | condition |
 |---|---:|---|
 | `−2` | **4** | unconditional — λ=0 is dominated at every `φ_cls` (§4.3) |
--- a/docs/spec/tuning.md	2026-09-29 05:42:43
+++ b/docs/spec/tuning.md	2026-09-29 05:42:43
@@ -3211,7 +3211,7 @@
 
 | axis | −2 `min-size` | −1 `size` | 0 `balanced` | +1 `speed` | +2 `max-speed` | why |
 |---|---|---|---|---|---|---|
-| λ (class-matcher kit) | reservation | reservation | reservation | reservation | reservation | `[CLS-TREE]` unbuilt; `docs/design/opt_dial_design.md` §4 states the five pinned frontier constants (4/16/16/64/256) it will read the day it lands |
+| λ (class-matcher kit) | smaller of `K`, `P3` | = `−2` | **`P3`** if `K` ≥ 16 sections and `P3` ≤ 1.26×`K`, else `K` | — | smaller of `P2`, `B1` where `0` chose `P3`, else as `0` | `[CLS-TREE]` unbuilt; `docs/design/opt_dial_design.md` §4 (D<next>): ONE kit constant (λ = 4, the sectioning DP's size end, `K`) at every position plus a first-match row over the whole-set tables `P3`/`P2`/`B1`; three distinct programs. Calibration: `cls_tree_design.md` §1.7 (ubuntubudu, per-probe model r = +0.98; `P3` 3.2× faster than today's pinned middle for +11% bytes) |
 | `[ART-SIZE]` ladder — bar | **0.95** | **0.85** | **0.75** | — | — | §2.16; `artifact_size_term.md` §3.3. Speed side em-dashed (**M13**): the speed it would buy is ≤3%, below `s` = 1.10 |
 | `[ART-SIZE]` ladder — threshold | **40,000** | **80,000** | **120,000** | — | — | §2.16; `limits.def:161`, `PCREC_SIZE_TERM_THRESHOLD` |
 | `-fno-premul-table` | **deny** | — `†` | **allow** | — | — | §2.13; `σ` = 22…25% ≥ `y`; `m` ≤ `x₂` = 2.00 for every `φ_scan` ≤ 1, so `−2` needs no measurement; `−1` iff `φ_scan` ≤ 0.126 (unmeasured) |
```

## Questions for Frank, each with a recommendation

**Q1. Rule the λ diff above: ONE kit constant (λ = 4) plus a first-match
row over whole-set tables, giving three programs (`−2`=`−1`, `0`=`+1`,
`+2`)?** *Recommend YES.* It follows the measured ordering at every
position. The five-constant DP picks the same programs at `−2`/`0` and
worse ones at `+2` (§1.7.4). The placements are yours to move: `z_mid`
1.26 (at 1.20, six of the twelve fall back to `K`), and the 16-section
gate, which sits at the bottom of the timed range.

**Q2. The option-2 consequence for CT-2: does the sectioning DP drop its
speed term and stay only as `K`'s exact size optimizer, with the per-probe
model kept as the RUBRIC's instrument rather than a compiler term?**
*Recommend YES.* No measured set has a customer for a time term inside
the DP. A time-aware DP would also need tree-shape state, since the
mispredict term is not additive per section (§1.7.1 reading 4). The
trigger to revisit is a timed 2-16-section population where a λ > 4
sectioning beats both `K` and `P3`.

**Q3. Should `+1` take `P2` where it costs ≤ 2× `P3`?** This applies to
two of the twelve sets, `L` (2.04×) and `Xan` (1.92×). *Recommend NO.*
Keep `+1` = `0`. The `Z₁` = 1.30 budget excludes `P2` on every set, and a
per-set exception is placement for its own sake. The gain would be 0.5
ns a probe.

**Q4. Is D129 Q5's premise ("the kit's byte tier answers CLSPACK's size
question") amended?** *Recommend YES, as a note, not a re-ruling.* The
premise holds for `.rodata` only. Counting `.text + .rodata`, `atom` is
smaller than the kit at N ≥ 16 on this population. That is why the
recommendation above keeps the row open as size-prioritized rather than
closing it.

**Q5. Run the one-minute `--dispatch switch` CLSPACK re-run on the next
bench slot?** *Recommend YES.* It is the only thing standing between the
CLSPACK row and a disposition, and its outcome already maps to a
pre-stated row above.

## For a fresh agent resuming this

Read `docs/design/cls_tree_design.md` §1.7, then
`studies/cls_tree_study/results/timefit_s0_20260929.txt`. To reproduce,
run `python3 timefit_s0.py` in `studies/cls_tree_study` (it needs
`discover` built, via `make discover`). The diff above is kept in this
report only. The scratch copy under the study's gitignored `build/` is not
committed.
