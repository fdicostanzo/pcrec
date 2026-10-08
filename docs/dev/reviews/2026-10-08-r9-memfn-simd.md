# 2026-10-08 r9 — D6 panel on the memfn SIMD layer design (R-9, integration.md rev 4.9 §R4.9)

Subject: `lane/memfn-r9` @ ea327c21 (lane r9d). The panel had three
read-only critics with distinct lenses. Their full findings files are beside
this one in `2026-10-08-r9-memfn-simd/`:

| critic | lens | file | BLOCKER | MAJOR | MINOR |
|---|---|---|---|---|---|
| r9c-correct (opus) | correctness, over-read, the floor rule, cascade | `correctness.md` (+ probes left in scratch) | 0 | 5 | 7 |
| r9c-measure (sonnet) | measurement regime, acceptance | `measurement.md` | 1 | 10 | 5 |
| r9c-fit (sonnet) | fit to the kit as built, siblings, staleness | `fit.md` | 1 | 5 | 9 |

## Rulings that postdate the design (binding on the revision)

- **D147 addendum 11** (Frank): SIMD is a parallel thread, 2:1 behind
  migration until M5′.
- **D144 addendum 4** (Frank via main, main 04733583):
  - OFFICIAL SIMD verdicts are pcrec-bench runs ON THE HARDWARE EACH FORM
    TARGETS.
  - The bench runs on several boxes: ubuntubudu (Ryzen 5 1600, Zen 1:
    AVX2 executed as 2x128, no AVX-512, slow PDEP/PEXT), this dev box
    (Ryzen 7 7700X, Zen 4: AVX2 and full AVX-512) and the Mac.
  - Informal timings anywhere are directional only. Main coordinates
    every run on the dev box and carries acceptance requests to the
    bench inbox (D78).
  - AVX-512 is NOT filed for lack of hardware. SSE comes first (widest
    reach); the AVX2/AVX-512 order is argued on evidence.
- **D147 addendum 12** (Frank): N6 is retired as not a search site.
- **M6 = VMSTRIDE** (R-10): MF_SITE_ABI 8 (multi-term ADVANCE,
  MF_MAX_TERM 32, span_hi as an iteration count), building on the kit
  branch now.

## Dispositions (manager)

Every finding is ACCEPTED unless marked. The revision lane applies each
fix, and the completeness table at the end is its checklist.

### The two BLOCKERs

- **F-1 (fit), ACCEPTED: batch 1 must go through a real selection seam.**
  PRE's FUNC text is rendered by `ofs_fn_define`, which `precheck_define`
  and `ofsskip_arm` call directly, not through `arms[]`. The fix is the
  general one (house rule: no parallel mechanism):
  - first a kit-only, ZERO-MOVER step that makes the FUNC body's form a
    selected row table (the scalar body as its one row; OFS's run-pinned
    sites included and enumerated);
  - then the SIMD rows are rows in that table, under the floor rule;
  - no "decorator over the floor row".
  The revision designs the seam and states which sites it reaches (OFS
  run-pinned included). R-1 never timed the OFS sites, so they need their
  own cell, or a structural exclusion, before a SIMD row may apply to
  them.
- **M-1 (measurement) and F-4 (fit), ACCEPTED, as REFRAMED by D144
  addendum 4.**
  - Q-R9-1 ("the dev box is the verdict box") is withdrawn. A form's
    official verdict is a bench run on each piece of hardware it
    targets:
    - 16 B SSE rows on ubuntubudu (Zen 1) AND the dev box;
    - AVX2 rows on both, since Zen 1's 2x128 execution is exactly what
      the bench must show;
    - AVX-512 rows on the dev box;
    - aarch64 on the Mac (addendum 8).
  - The critic's "UNOFFICIAL-ONLY" label for v4/w64 rows is SUPERSEDED:
    the dev box is a bench box.
  - Bench testees (RQ-5) come BEFORE acceptance, not after it.

### MAJORs

- **C-1** ACCEPTED: T is defined once as L−1; add a G2 plant for "reach
  one short".
- **C-2** ACCEPTED: compute the floor first, add an `over` column naming
  the floors a row may decorate, and collect only same-form rows. This
  folds into the F-1 seam.
- **C-3** ACCEPTED in part:
  - compare stamps as keys with sizes normalised;
  - selection readers ignore guarded SIMD bytes by construction.
  The D84 code-bytes refusal cap becomes **Q-R9-9 for Frank**.
  Recommendation: guarded bytes are EXCLUDED from the cap, so SIMD-on can
  never change a refusal (C-SEL). The compile-time bound the cap protects
  holds instead by a per-row constant bound on the guarded text, which
  the kit states and checks.
- **C-4** ACCEPTED:
  - the guard gains `defined(__SSE2__)` (and `__x86_64__`, C-8);
  - the cascade sits above the full ladder;
  - Q-R9-8 states the libgcc link dependency.
- **C-5** ACCEPTED: G2 adds the axes multiple hits, near-misses, a `pos`
  sweep and the exact returned position; plants per path; per-path
  execution counters with floors; `-mgeneral-regs-only` as w16's
  compiled-out level.
- **M-2** ACCEPTED: `simd_accept.tsv` gains columns for state
  (CANDIDATE / ACCEPTED / STALE / REJECTED), tier (unofficial/bench),
  hardware/CPU class, and the bench and toolchain pins.
- **M-3** ACCEPTED as reframed:
  - a form is judged on every bench box its level runs on;
  - a loss on ANY official box it targets blocks ACCEPTED there, and the
    row's applicability is then narrowed per level, or it is not
    accepted;
  - levels only one box runs are judged on that box (not "unofficial").
- **M-4** ACCEPTED: the bench-submission spec (the critic's two-tier
  section), with recipes naming `-march=<level> -mtune=generic`, never
  `native`.
- **M-5** ACCEPTED: the bar gains a magnitude, pre-registered bins
  (declared before the numbers), interleaved arms, repeats, and
  multiple-comparison control.
- **M-6** ACCEPTED: the placement band is replaced by the bench's
  non-mover population as the noise band (no alignment-flag constants).
- **M-7** ACCEPTED: no "< 8 movers" exclusion that can overfit. Bins come
  from the pre-registered population, and dropped bins are recounted at
  each reading (K35).
- **M-8** ACCEPTED: C19 flips records to STALE (never red, so it never
  blocks a scalar change, per Q-R9-5); it digests the real site
  population, not fixtures, and carries the bench version.
- **M-9** ACCEPTED: VW+T is a CORRECTNESS bound. The performance cut-over
  above it is swept (unofficial tier picks, bench confirms). Every regime
  constant is labelled (D149), and dev-box-chosen constants are labelled
  "measured-unofficial" until a bench run.
- **M-10** ACCEPTED: a hit-density witness; dense text is in the
  pre-registered population.
- **M-11** ACCEPTED: covered by per-hardware official verdicts (M-3). Also
  a `levels.def` note forbidding PDEP/PEXT and gathers in x86 kernels
  unless a bench run on Zen 1 shows no loss.
- **F-2/F-3** ACCEPTED, the general form:
  - ONE deny carrier (options.def / `--memfn=`), retiring the MF_D_ bits
    into it or naming why they stay;
  - `policy` as a fields.def field using the existing DECLINED verdict;
  - ONE selection walk shared by `select_arm` and `rc_row_of` (no clone).
  The H1 trigger question is answered in the revision.
- **F-5** ACCEPTED:
  - ONE emit_sweep `simd` arm (the paired ON/OFF compile) with named
    projections: G1 movers, C-SEL, C11 FORMS, C18, I2;
  - `c9_floor` folds into row_floors.tsv;
  - run_rows.sh checks `simd_accept.tsv`'s row set.
- **F-6** DECIDED by the manager: M6's MF_SITE_ABI 8 does NOT carry a
  SIMD ADVANCE bound. No SIMD ADVANCE row has a cell (D77). The bound
  comes in its own bump when one does; it is filed with that trigger.

### MINORs (all ACCEPTED, applied as written in the findings files)

- From correctness.md: C-6..C-12.
- From measurement.md:
  - M-12/M-13: wording;
  - M-14: the sibling comes from `thread_siblings_list`;
  - M-15: C18 gets a stamp filter and a negative control; C-SEL gets a
    literal floor;
  - M-16: the named-benefit path for SIMD rows is size-free.
    **Q-R9-4 is revised:** a SIMD row's named benefits exclude code space,
    since its text is always longer.
- From fit.md: F-7..F-15 (F-9: rebase onto the kit tip; keep "4.9" for
  this revision; M6 does not bump the rev).

## For Frank (via main), AFTER the revision

| id | question | status / recommendation |
|---|---|---|
| Q-R9-1 | which box gives the verdict | RESOLVED by D144 add. 4: bench runs on the targeted hardware |
| Q-R9-2 | acceptance levels | revise: each row at each level it targets, judged on every bench box running that level |
| Q-R9-3 | KB second filter position | (a) as recommended |
| Q-R9-4 | named benefit | revised per M-16 |
| Q-R9-5 | a SIMD loss never blocks a scalar change | yes, with C19 → STALE (M-8) |
| Q-R9-6 | the floor rule | yes |
| Q-R9-7 | deny granularity | per (form, width) row, through the ONE carrier (F-2) |
| Q-R9-8 | cascade libgcc dependency | yes, x86-64 Linux/ELF, spec-stated, with C-4's guard |
| Q-R9-9 (new) | D84 cap and guarded bytes | recommend EXCLUDE plus a per-row bound (C-3) |

## Completeness (by id)

- correctness: C-1..C-12 (12/12 dispositioned)
- measurement: M-1..M-16 (16/16)
- fit: F-1..F-15 (15/15)
- Total 43 findings: 2 BLOCKER (both accepted, M-1 reframed), 20 MAJOR, 21
  MINOR.
