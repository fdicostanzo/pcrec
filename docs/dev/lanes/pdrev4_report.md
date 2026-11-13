# pdrev4 — part_d.md rev 4 (the kit's design for R-38 Part D, narrow re-check review r3 memfn-partd3 as ruled)

Lane pdrev4 (opus), 2026-11-12. Branch `lane/memfn-pdesign` (worktree `worktrees/pdesign`).
Deliverable: `docs/design/memfn/part_d.md` rev 4 (commit `b62a75864`) and its pointer line in
`docs/design/memfn/CLAUDE.md`. This is DESIGN TEXT ONLY: no code, no build, no suite, no queue job.
I re-read the cites at main `5d41c1f2d` (later than `a8ae73be0`).
`git diff --stat a8ae73be0 5d41c1f2d` is empty over `memfn/`, `src/gen/`, `tests/memfn/`,
`memfn/tests/`, `tests/mech/`, `docs/spec/`, `scripts/emit_sweep.py` and `docs/design/memfn/`.
plan.md gained [SHADOW-TABLE]. I read every new code cite by function at `main` (`git show main:`).

## STATE AT HANDOFF

STATE: done. Rev 4, the CLAUDE.md line and this report are committed. No rulings file was named. I
applied the review's Rulings section through its last entry ("FIX-1 RULED (2026-11-12, kit + main
jointly)").

OWED: none. I ran no suite and queued no job. The lane made no measurements: the rev 4 text cites
code read at main, and its witnesses are rev 3's measured ones.

## Summary

Rev 4 applies all 14 FIX-NOW findings (RDY-1..6, FIX-2..9) and the joint FIX-1 ruling. It also
takes the two DOC items, FIX-S2 and FIX-S3, as the review proposed them. FIX-S4 is NOTED and folded
into FIX-7. Every change is marked `[r3pd ID]`. Every check a fix adds or changes names its control.
The new plants are p13 (P2 keeps `rs && !proof->run`), p14 (`summarize` drops the record), p15 (a
quiet-path print) and p16 (`merge` takes the verify-YES span as R). The existing controls are named
where they apply: the site-file hash, the `p2_untested == p2_refused` equality, the
`census0_cards.out`/`vcls.out` byte-equality, and `rows_check`.

RDY-1 traces the `run_part_terms` record through both feeds:
- the check's own feed: G2's trace-build capture, joined by a new `G2SITE id=N` line;
- the production feed: `r33_sim/probe.c`, then `collect.py`'s `parse`, then `summarize` (which today
  drops the record and now keeps it), then the sweep, then `vcls.py`/`census0.py`.

The production feed gets its own check: every artifact that stamps `_REQ_RUN` carries one record.
§9 is re-stated whole as items 1-9 so main's stage-3 brief can quote it. Rev 4 adds two items:
- item 6, the shadow retirements, now `dominated`/`rdom` as well, with the successor controls and
  [SHADOW-TABLE];
- item 9, the pins and floors the joint landing raises.

Verdict per the review: D0-D3 READY with these text fixes applied (part_d §5.1.1, "Readiness after
rev 4").

## Per-finding changes

| id | disposition | where in part_d rev 4 | change | control named |
|---|---|---|---|---|
| RDY-1 | FIX-NOW | §5.1 D3 row (content, check, plants); §8 item 2; §9 item 9 | `collect.py`'s `summarize` keeps `run_part_terms` raw (a `parts` list); re-collect the sweep; re-pin the goldens; a production-path check (every artifact stamping `_REQ_RUN` has one record) | p14: `summarize` drops the record, so the production check reds while the G2-fed checks stay green |
| RDY-2 | FIX-NOW | §5.1 D3 row; §5.1.1 D3 witness paragraph | print only where `wf_parts_prepare`'s `quiet` is 0 (`ask_sel`'s house rule); the population is sites whose define chose ofsskip's FUNC row; generic-pass sites are counted apart; (c) dropped | p15: a quiet-path print doubles the records of a site G2 asks before define (reach confirmed by REACH, else re-aimed) |
| RDY-3 | FIX-NOW | §5.1 D3 row; §5.1.1 D3 witness paragraph | `probe.c` writes `alts` only `if (p->nalt)`, and a derived part is `nalt` 0, so the census adds a NEW population branch; the "priced from its RUN term" text is corrected; r33_sim `sim.py` is listed for the build to read | p11 (unchanged) reds on the new branch |
| RDY-4 | FIX-NOW | §5.1 D2 and D3 rows; §5.1.1 D3 | the `G2SITE id=N` join line; G2's count from C2's MEASURED extent (K35); the print listed in D2; floors recorded at D3's first green run | p11, p12 on the joined per-site equality |
| RDY-5 | FIX-NOW | §5.1 D3 row; §9 item 9 | cell = `emit_sweep` `DIFFER_PINS` for `--memfn=no-run-verify-wide` at the landing, per (base, flag, stream); the census quantity over `--sources corpus` at the same base and stream; census >= movers, with the reason (INFERRED direction) | the literal raised in the landing commit; the DIFFER cell itself (it cannot be ASSERT_ZERO at landing) |
| RDY-6 | FIX-NOW | §5.1 D3 row | readers vcls.py, census0.py, slot/link.py, slot/plan.py (does not plan `cn+`), slot/est.py; goldens vcls.out, census0_cards.out, census0.out; both `settest_cls` copies change in one commit | the `census0_cards.out`/`vcls.out` data-line byte-equality; plant: one copy changed alone |
| FIX-1 | RULED JOINT, then FIX-NOW | §2.4 item 4; §7 Q8; §8 item 2; §9 item 6 | the shadow's `dominated`/`rdom` retire on non-cube runs; "`rdom` stays" dropped; [SHADOW-TABLE] cited | successors: C2; G2's decline equality; P3's floor on `run` 0 (FIX-4, p13); witness F3 |
| FIX-2 | FIX-NOW | §2.1 item 6; §5.1.1 D0 floors | P23's plant is detected by C2 (and the occurrence oracle), not p7; F24's floor gets a 3+ member stratum | C2 / occurrence oracle at D2; the 3+ stratum floor at D1 |
| FIX-3 | FIX-NOW | §5.1.1 D0 | P18 scoped to positions of 3+ members on the wide stream; 1-2 member positions keep one draw on `run[j]`; byte identity of today's sites becomes a D0 check (sha-256 of the generated site file, a literal) | plant "P18 applied to cubes": the hash reds |
| FIX-4 | FIX-NOW | §5.1.1 D1 | G2 states `pres_proof.run` 0 on its no-findable sites; P3's floor counts only those | p13 (P2 keeps `rs && !proof->run`): the floor reds |
| FIX-5 | FIX-NOW (+ small kit design step) | §5.3; §5.1.1 D2 | a fifth formhash shape (`MF_FH_RUNPART`, the builder names it): a REQUIRED run span of two wide positions; two SET terms minimum (`pres_run_check`: 2..`MF_WSPAN_POS`); a second asserted row (the BODY row); the fold rule (fold into an id: no card row; fold into the id-less generic loop: refused, kit ruling) | `fh_render`'s refusal of an instance that reaches another row |
| FIX-6 | FIX-NOW | §5.1 D1 existing-sabotages cell | REACH on every presence.c/finder.c row; S286, S288, S1098 re-aimed; S278, S3045 re-anchored; new plant p13 | p13; REACH |
| FIX-7 | FIX-NOW | §5.1.1 D1 | the decline route gets its own `g_dec_untested`/`g_dec_refused` and a `FLOOR_DEC_REFUSED`; `p2_untested == p2_refused` asserted (FIX-S4's array form NOTED) | restoring the route-unconditional increment reds the equality |
| FIX-8 | FIX-NOW | §2.4 item 2 | the full `fd_rows[]` literal plus its `FD_CT` line: `KN_P`, `SF_RUN_NOSCAN`, link `{0,0,0,0}`, `opt` NULL, `FB_DERIVED`, step, evidence, refuted_by, `CM(N_OPTIONAL)`, `KD_ALL`, `LY_ALL` | `rows_check.py` against `rows.tsv`; a basis left `FB_UNSTATED` is refused by `mf_finder_rows`' self-check |
| FIX-9 | FIX-NOW | §5.1.1 D0 and D2 | D0 counts alternatives with spelled R plus a spelled verify-YES span (FAM_MASS, FAM_REPORT); D2 floors "R the member" against `run_of` | p16: `merge` takes the YES span as `m->run`, so DECIDE reds and the floor falls to 0 |
| FIX-S1 | PLAN (main's) | §9 item 6 | cited as [SHADOW-TABLE]; nothing built here | n/a |
| FIX-S2 | DOC | §2.1 item 6 | `in_stretch` and `one_member` named; the {one, cube, wide} class accessor as the general form | n/a |
| FIX-S3 | DOC | §6 C8 | the threshold is recorded as met and the deferral as chosen; it builds at the trigger or at a fourth special case | n/a |
| FIX-S4 | NOTED | §5.1.1 D1 (FIX-7) | folded into FIX-7 | n/a |

## Facts for pcrec's stage 3

part_d §9 (rev 4) is the complete, final list for the stage-3 brief to quote:
- the one predicate "the pre-check TESTS the run";
- item 1: R by role in a window site's alternative;
- item 2: the decline and its readers, `gate_need` among them;
- item 3: nothing to render;
- item 4: the scan-less REQUIRED run and its two comments;
- item 5: `mf_pres_picks` on a no-scan run, and the lead reader;
- item 6: the shadow retirements on non-cube runs, `leads`/`rlead` AND `dominated`/`rdom`, with the
  successor controls and [SHADOW-TABLE];
- item 7: the version events;
- item 8: the spec hunks by section;
- item 9: the joint-landing pins: the `DIFFER_PINS` cell for the deny arm, D3's pcrec-artifact
  floor, the production-path check, and the D27 witnesses.

## Charter-vs-committed checklist

- [x] Read BOILERPLATE.md, then memfn/CLAUDE.md. First command was `rev-parse --show-toplevel` (it
  printed the worktree).
- [x] DO 1: every FIX-NOW finding (RDY-1..6, FIX-2..9) applied and marked `[r3pd ID]`, each check
  with its control. RDY-1 is traced through G2's feed AND `collect.py`'s `summarize`.
- [x] DO 2: FIX-1. P8's retirement now covers `dominated`/`rdom` on non-cube runs. "rdom stays" is
  dropped. The successor controls are named and [SHADOW-TABLE] is cited (verified on main, plan.md).
- [x] DO 3: §9 re-stated, complete and final.
- [x] New cites verified at main `5d41c1f2d` (>= `a8ae73be0`). The spec and plan are cited by
  section/[TAG]. No line-number cites appear in new text (a grep for `file:NNN` finds none).
- [x] A "rev 4" line sits at the top of part_d.md. The CLAUDE.md pointer line is updated.
- [x] Scope: writes only in `worktrees/pdesign` plus scratch `/var/tmp/pcrec-pcrec/scratch/memfn/pdrev4/`.
  No code, suite, queue job, merge, push or monread.
- [x] Named-path commits only.
