# Lane s2rev11 report: span_cards.md revision 1.1

Branch `lane/memfn-s2rev11`, worktree `worktrees/s2rev11`. Design only: no C, no make, no timing, no box
job. Input: review `docs/dev/reviews/2026-11-06-r5-memfn-span-cards-recheck.md` as ruled, and R-35 (c)-(e)
at main 78e7da573.

## What was done

- `docs/design/memfn/span_cards.md` revised to rev 1.1. Every changed passage is marked `[rev1.1 <id>]`.
  The new §R1.1 table maps each r5 id to the section that answers it, or to PLAN/NOTED with its home.
- Drills under `docs/design/memfn/span_cards/` (all `python3 -I`, and each prints its inputs):
  - `drill.py` was rewritten for the rev 1.1 estimator.
  - Four drills are new: `place_drill.py`, `floor_drill.py`, `tree_drill.py`, and `coverage_drill.py`, which now includes the aa term.
  - `j1_drill.py` was extended to cover placement.
  - Every figure the note quotes comes from one of these drills. `place_drill.py` was re-run before the final commit and its output matches the note.
- Both CLAUDE.md files were updated: the span_cards line in `docs/design/memfn/CLAUDE.md` and the drills list in `span_cards/CLAUDE.md`. Both are within the size limits (the staged check passed).
- No `docs/dev/lanes/s2rev11_deliver.txt` exists in the worktree or in the main tree, so `scripts/lanecheck` was not run.

## Decisions taken (the lane's, inside the ruling)

- **PLACE: placement is NOISE.**
  - Each arm and each twin gets a fresh placement for every launch, and every launch is its own executable.
  - The constraints are asserted on the linked addresses (`nm`), never on object bytes.
  - The control is one fixed executable, sha-asserted.
  - A second refusal with the same cause makes the set HELD, and the kit manager rules.
  - S2c's dry run includes a placement screen.
  - The unit gate's behaviour under this choice is shown in §3.2, from `place_drill.py` A.
- **FLOOR:** the delta rows use their own paired A/A (`med D > aa_D`, and every D_l > 0). FRG is dropped because it no longer has a reader.
- **Z:** z stays at 3.0, labelled UNMEASURED DEFAULT. It covers ONE event: a new draw against the stored value. In the re-drill (estimator as written, aa included), the rate stays at or below 2.25 % for every within-launch share f.
- **DRIFT:** the threshold is kept. It is argued as a proxy for a change in box state, and its power table is in §3.5.
- **CENSUS:** S2a-S2d are checked with emit_sweep's two-build sweep. S2e uses `span_cards/slot/movers.py`, which applies m0build's census method with nothing normalized. `movers/0002.tsv` takes the same shape as 0001.
- **CHECKC:** the deps guard moves onto card rows. S2e adds a counted measure_store pass with a floor of 40, recomputed over the build tree by `tree_drill.py` C.
- **EMBED:** the embed is cell-less for every set. The listing gains a `file_cells` column. The digest never covered the cells, so the identity does not change. `tree_drill.py` D supplies the figures: 260 KB avoided, about 16 KB projected. It also shows that measure_sets' "ten sets below one fold_tables.inc" sentence was already false by about 10x, so the sentence is replaced.
- **BOUND:** there are two literals and one `_Static_assert` test TU, because the dependency rule forbids sharing a header. K138's form is amended for main.

## Charter vs committed

| charter item | committed where |
|---|---|
| r5 CELLS-1 (a)-(e) | §3.3, §3.4 step 1-2 (events column, round `med`, group/arm naming, one base rule, launch = (job, l)) |
| r5 CELLS-2 | §3.5 "What the recompute covers", outcomes |
| r5 CELLS-3 | §2.4 grammar, §4.4 hunks, §10.2 kit-grid.tsv comment |
| r5 CHECKC | §2.4, §9 S2c (n), S2e (u), `tree_drill.py` C |
| r5 HASH | §3.2 entry-table renderer and site-shape table |
| r5 TWIN | §3.2 (nm on linked executables, STT_FILE named), §9 (j), (j2) |
| r5 PLACE | §3.2, §3.5 HELD, §9 S2c placement screen; `place_drill.py` |
| r5 DRIFT | §3.5 Drift (proxy argument, power table, D149 label) |
| r5 Z | §3.4 step 7, §6 table; `coverage_drill.py`; §10.2 span_pick band sentence |
| r5 FLOOR | §3.5, §2.3; `floor_drill.py`; §10.2 measure_sets §7.4 |
| r5 CENSUS | §5 (tool named, 0002 shape), §8.3, §10.2 (emit_sweep misattribution) |
| r5 KSGEN | §4.5 raw-row compare, §9 S2a (r) |
| r5 BOUND | §4.1, §10 item 11, §10.3, §9 S2a (t) |
| r5 MFMEAS | §4.2 filter and field position, §5 and §8.2 readers |
| r5 EMBED | §3.8, §4.4, §8.2, §9 S2e (v), §10 item 6, §10.2 sizing sentence |
| r5 GOAL2 | §1 Goal 2, §3.5 outcomes |
| r5 D188A1 | §0, §2.5, §2.7, §5 (class in the digest), §9 S2g, §10, STATE; grep finds no "until the SIMD model" |
| r5 SIMD-READ | §2.5 interim + consequences, §10 item 4 |
| r5 TARGET | §2.7, §3.8 step 1, §5, §9 S2a (s), §11 |
| r5 POLICY | §6, §10 item 7, §12 row 2 |
| r5 R35 | §10 items 8-10 |
| r5 D149 | §3.2, §3.5, §3.6 labels with triggers |
| r5 J1-WIN | §3.6, §3.7 (J2p) |
| r5 LOCK | §9 Separability |
| r5 ANCHORS | §8.2, §9 S2a witness |
| r5 SMP20 | §7, §10.2 |
| r5 J3 | §3.5 table (inputs), §3.7 (`tree_drill.py` B) |
| r5 XREF | §4.4, §4.6, §0 row 9, §10 numbered |
| r5 INDEX | §3.8 step 3 |
| r5 CITE | §2.1, §10.2 |
| r5 FAM-A/B/C | §12 rows 4-6 with triggers |
| r5 FAM-D | §7 |
| r5 FREEZE NOTE | §8.3 cites R-35 (c) |
| ruling: DEFAULTS (B) = R-35 (c), cite | §8.3 |
| ruling: EMBED R-35 (d), identity + listing state cell-less, no embed reader needs cells, arithmetic re-checked, sizing sentence amended | §3.8, §10.2 |
| ruling: POLICY R-35 (e), z/gate/MATERIAL in one table labelled, HORS_MIN/MAX_SET out | §6 |
| ruling: §10 lists derived noise dropped, verify_cmp by census, S2g held moving C9 | §10 items 8-10 |
| ruling: SIMD interim, generic target only, SIMD-on judged as today; consequences | §2.5, §10 item 4 |
| ruling: zen4-grid3 declares target (-march) and class | §2.7, §3.8 |
| quality: every figure from a committed drill with inputs | drills listed above; §R1.1 drills paragraph |
| quality: TWIN on linked addresses, never object bytes | §3.2 |
| quality: PLACE decided, unit gate shown | §3.2 |
| quality: CENSUS tool and 0002 shape | §5 |
| quality: CHECKC recomputed at the build tree | §2.4, `tree_drill.py` C |
| quality: D149 labels | §3.2, §3.5, §3.6, §6 |
| CLAUDE.md lines | `docs/design/memfn/CLAUDE.md`, `span_cards/CLAUDE.md` |
| lanecheck | no deliver file; not run |

## Owed by main

- Acknowledge the R-35 narrowings in §10 items 8-10.
- Rule on the policy table (item 7) and the plan-row text in it, `COVER_Z_E3` "in plan_cost.def": no code contains it.
- Settle the spelling of the embed (item 6).
- Settle K138's form (item 11).
