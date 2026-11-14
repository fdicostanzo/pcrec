# pdesign — the kit's design for R-38 Part D (wide run positions)

Lane pdesign (opus), 2026-11-12. Branch `lane/memfn-pdesign`, cut from main `35bee4da9`.
Deliverable: `docs/design/memfn/part_d.md` (rev 1), plus a pointer line in `docs/design/memfn/CLAUDE.md`.
DESIGN ONLY. Nothing was built or run (Frank's evening hold); every code statement is a read at
`35bee4da9`, cited by function name.

## STATE AT HANDOFF

- STATE: done. part_d.md rev 1 and the CLAUDE.md pointer are committed on `lane/memfn-pdesign`.
- OWED: none. Nothing was queued and no suite was run; the build's checks are listed in part_d.md §5.
- No rulings file named in the brief.

## Summary

The minimal correct form needs no seam field and no `MF_SITE_ABI` event. It needs ONE
`MF_CLASS_V` event and four kit units (D0-D3). The approach in one sentence: the kit scans only a
position its existing finds can read (one member or a two-member cube), verifies wide positions
with its own exact membership test (`kit_set_test`), and states a decline when a run has no
findable position.

Two findings come from reading the code:
- **A latent miscompile.** `c_run`'s pinned join has no shape test, and `run_bytes` writes an
  uninitialized byte for a non-cube position. It is unreachable today and becomes reachable once
  the derived extent can hold a wide position.
- **Unguarded scan reads.** `kit_pres_picks` reads `rr.scan` without checking `has_scan`.

R on window sites stays identified by shape. Both ways of widening it move today's cover-site bytes.

## The request's facts

The four facts are restated in part_d.md §1, as the kit reads them:
- **The statement form does not change.** The run span already admits any non-empty set
  (`pres_span0_clear`).
- **A joint superset is invisible to the kit's per-position promise.** `ver_len` means "each
  position held in its set", never exactness.
- **Every encoding brings wide byte sets.** Digits, hex, `[a-z]` and `\w` arrive, and runs appear
  where none was stated before (`[a-z]{8}`, `cat|dog`).
- **pcrec needs a reply or a stated decline per run.** A refusal fails the compile.

The request's "read on your K38-2 tip" points are all CONFIRMED (part_d.md §2).

## The three K38-2 sites

- **K-1, `derive_run_part`/`wf_parts_prepare`** (with precheck.c `run_part` and ofsskip.c
  `ofs_fn_applies`/`verify_chain`). Today a wide position refuses the compile loudly. It must
  become:
  - the findable scan;
  - the derived extent as R by the kit's own flag;
  - one RUN term for the member's findable stretch only (`run_len` 1 kept);
  - every other position its own term, with `kit_set_test` for a tableless wide SET term;
  - a loud `run_bytes` guard;
  - the `wf_parts_prepare` check generalised to "the terms tile the extent and the scan is
    `rr.scan`";
  - `a_mass_choose` excluding all of R but `rs`.

  Details: part_d.md §2.1.
- **K-2, `run_shaped`.** KEPT. A wide position in R gives `mf_wreply.run_stated` 0, which is a
  stated decline. Both widenings move today's cover bytes: a shape-free test makes every cover span
  R, and a label un-Rs cover spans that are shape-only today. The label is candidate C6, with a
  trigger. Details: part_d.md §2.2.
- **K-3, runcmp `(T, K)`.** UNCHANGED. RUN terms stay findable-only, and their one builder now has
  a guard. Details: part_d.md §2.3.

## Readers of a wide or superset position

The full table is part_d.md §3.1 (grep over `memfn/src` at the base, each hit read in its
function). The readers that assume <= 2 members:
- `kit_run_decide`/`kit_run_member`, implicitly: every position is a scan candidate. Through them,
  `run_member`'s verify-YES case is affected too.
- `fd_pres`'s P3 member rule (`run < 0`).
- `kit_pres_picks`' P4/P2 reads of `rr.scan` with no guard.
- `c_run`'s pinned join, `run_bytes`, `a_mass_choose`.
- `derive_run_part`/`wf_parts_prepare`, `run_part`, `ofs_fn_applies`, `vrun_applies`.
- runcmp/`kit_run_set`/`cl_run`/`term_prove`. These are safe once `run_bytes` is guarded.

The readers that do NOT assume it:
- `fd_run_modes[]`;
- `stretch_window`/`stretch_exact`;
- the twin admission's mass (conservative on a superset);
- the coverage rule;
- the run span's input check.

Superset correctness (part_d.md §3.3) rests on three things: verified positions are tested against
the FULL set (cube = set for RUN terms, exact ranges for `kit_set_test`); no hull test ever counts
as verified; and C2 probes every non-member byte.

## MF_SITE_ABI

No event in the minimal form (part_d.md §4). Statement layout and meaning are unchanged. The OFS
admission of a tableless wide SET term is a rendering admission; whether it moves today's OFS sites
is measured at D2's first `emit_sweep` (open question 3). Only candidate C6 (the R label) would
need an event.

`MF_CLASS_V` moves once. A stated run may come back untested and unproven (the decline), and
`has_scan` now names a one-member or cube position. The pcrec abi rides stage 3's one event, and
the new deny row raises the `--list-axes` memfn floor in `docs/spec/`.

## New reply fields for pcrec

NONE. What pcrec reads, from existing fields:
1. **The decline.** `cls.pres[run].verify` 0 with `proven_by` 0; `cls.run` zero and unread;
   `cls.pres_row[run]` names the row. Where no member is tested either, the site has nothing to
   render. Today `req_site_define` treats that as an internal error; the admission is pcrec's.
2. **The extent may span wide positions.** It still means "held in its set".
3. **`@scan`** is always a one-member or cube position.
4. **`mf_wreply.run_stated` 0** on a window site whose R holds a wide position.

## Build units

The table is in part_d.md §5.1, in span_runs_sheet §5's shape:
- **D0 (M):** G2 first. The presence generator moves from (run, mask) to sets, C2 probes all 256
  bytes, and the window and OFS families gain wide cases. Run at the base, it records today's
  refusals.
- **D1 (M):** the decision. The findable column, the decline row first in `fd_rows[]`, P3's "no
  tested run", the `has_scan` guards, and `MF_CLASS_V`. Zero movers.
- **D2 (L):** the rendering, as in §2.1, plus a deny row whose OFF arm verifies only the findable
  stretch. Plants p3-p6; S3012 is re-aimed.
- **D3 (S):** the `verify_cmp`/`settest` census over the stage-3 corpus. There is no new card,
  because there is no new method.

G2 coverage (part_d.md §5.2):
- member-count strata 1, 2-cube, 2-non-cube, 3-8, 9-32, 33-128 and 128;
- range, union, scattered, class and UTF-8 shapes;
- wide positions next to the scan, at the edges, and between stretches;
- decline witnesses and joint supersets;
- both layers, every admitted level, the lever and the deny;
- K35 floors.

Faster forms are candidates C1-C6 with triggers (part_d.md §6): set-find on a wide scan, non-cube
pair scan, several RUN terms, vrun with set verifies, a hull prefilter, and the R label.

## Open questions

part_d.md §7, each with a leaning:
1. Keep R shape-identified (leaning yes).
2. The deny's name (leaning `run-verify-wide`).
3. Does the tableless-set OFS admission move today's OFS sites? UNMEASURED; the general rule,
   decided by D2's `emit_sweep`.
4. pcrec's admission spelling for the decline (pcrec's, stage 3).
5. A direct translation of the reply into the derived part's terms (leaning: not now; noted as a
   simplification).

Not mine, seen in passing: none beyond the two code findings in the Summary, both carried into D2
and D1.

## Charter-vs-committed checklist

| brief item | where |
|---|---|
| read BOILERPLATE.md and memfn/CLAUDE.md first; worktree first command | done; first command printed `/home/pcrec/projects/pcrec/worktrees/pdesign` |
| inputs: both R-38 Part D entries, readiness memo §3/§5/K-1..K-3, span_runs_sheet §2/§4/§5.1, D146/D147/D157/D190, ideas/walk record | read; set-find (walk) knowledge used in §6 C1 |
| Q1 the three K38-2 sites, quoted by function name, with their target form | part_d.md §2.1-§2.3 |
| Q2 every other kit reader by grep (run decision, twin mass, ranking, presence family, fd_run_modes), and which assume <= 2 | part_d.md §3.1-§3.2 |
| Q3 a superset position's verified extent never overclaims | part_d.md §3.3 |
| Q4 MF_SITE_ABI event? new reply field? | part_d.md §4: no `MF_SITE_ABI` event, one `MF_CLASS_V` event, no new field; what pcrec reads |
| Q5 build units with check, plant, sabotage fates; G2 coverage; measurement card; minimal default; faster forms as triggered candidates | part_d.md §5.1, §5.2, §5.3, §6 |
| goals ranked first | part_d.md §0 |
| the three standing questions | part_d.md §8 |
| spec/plan cited by section or tag, no line numbers | held (code by function name) |
| pointer line in docs/design/memfn/CLAUDE.md | committed |
| no code, no build, no suites, no queue jobs, no monread; scope (worktree + scratch only) | held (no scratch used) |
