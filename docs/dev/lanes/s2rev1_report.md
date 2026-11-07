# s2rev1 — span_pick stage 2, the design, revision 1 (lane report)

Lane `s2rev1`, branch `lane/memfn-s2rev1` (rev 0's `lane/memfn-s2design` with the kit branch
`lane/memfn-k1102` merged in, so review r4 is present), 2026-11-06. DESIGN ONLY: no C, no make, no timing,
no box job. Deliverable: `docs/design/memfn/span_cards.md` REVISION 1 from the ruled review
`docs/dev/reviews/2026-11-06-r4-memfn-span-cards.md` (findings table + "## Rulings"), main's DEFAULTS
ruling (B), D188 and the pending owner ruling on the SIMD model; its line in `docs/design/memfn/CLAUDE.md`;
drill evidence under `docs/design/memfn/span_cards/`.

## Summary (what a fresh agent resumes from)

1. **Every review id is answered** in the note's new §R1 table (finding id -> section, or PLAN/NOTED with its
   home). Rev-1 text is marked `[rev1 <id>]`; unmarked text is rev 0's, still valid.
2. **Scalar only; SIMD HELD.** Row 1 prices the SCALAR layer, SIMD forms ride as rungs (span_pick §The pick
   6's else-branch), with the cost stated (§2.5: a scalar-priced departure can lose a vrun rung at
   `-fmemfn-simd`; seen at row 1's two-layer acceptance reading; the C9 row is the fix). J6 = unit S2g
   (vrun only; vany dropped), SEPARABLE and HELD on the owner's SIMD model; nothing in S2a-S2f depends on it;
   its rows join the NEXT set id (a set is one run).
3. **D188** (§2.7), model-neutral: fact (b) is "the built artifact contains code for level L", never "the
   macro selected L". zen4-grid3@1 is scalar-only: (a) in the header's `isa`, (b) absent for every level in
   PROVENANCE.md, (c) none; the in-format spelling of (b)/(c) is J6's.
4. **Producer split along `measure_sets.md` §7.1's seam** (§3.1): the kit supplies probes (G2 generators'
   `--cards` mode) and card rows; the estimator, gates and NULL rule are SPEC text (`measures.md`'s new
   sections 3.4-3.5, S2c) that M3 later implements; this run uses a slot harness (§7.1 (d)) in
   `docs/design/memfn/span_cards/slot/` (evidence, never built); the writer is pcrec's canonical writer.
   Per-launch cells go in the set's own `cells` section; no `raw.tsv`, no `cells.tsv`, no
   `memfn/measure/`. D176 Q3 misquote fixed.
5. **Executable estimator** (§3.4): cells = per-call medians over 7 rounds; `slope` (LS over 3 lengths, exact
   integers) or `delta` (arm minus base in one group, per event); each launch normalized by its own job's
   walk control (MEAS-11/SLOT-9 fold in); lower median over 7 fixed launches; A/A per arm on the value
   with a PERTURBED twin (40-byte pad + link order, the driver asserts objects differ, texts equal); spread
   = trimmed s.d. (drop the launch farthest from the median) times a derived consistency factor
   K_TRIM_E6 1723000; one root. Gates (§3.5): cost rows only, `noise x 10^6 <= gate x value`, value > 0;
   delta rows take §7.4's NULL rule (one-sided: a negative cost is NULL), never refuse a group; drift per
   JOB against a between-launch threshold, floored at the unit's half gate; unit bimodal = an interior gap
   above the half gate. Drill table on the review's constructed outcomes in §3.5 (`span_cards/drill.py`).
6. **J1 rule** (§3.6): paired per-launch sign + 2-noise margin, (b) only for one width winning >= 5 of 8 cells
   and losing none: (b) 0 of 20,000 with no effect (rev 0: 50-55 %); 82 % at a 4-sigma true effect.
7. **Coverage** (§6): z re-derived as 3.0 (`COVER_Z_E3 3000`) for the noise §3.4 defines against a new run's
   draw (simulated 2.3 % one-card equal-price departure; z = 2 gives 6.7 %); home [KIT-POLICY-TABLE].
8. **DEFAULTS (B), RULED**: S2e flips `idk` to zen4-grid3@1, zero movers; amends R-35 items 1/3, span_pick
   (stage 2, row 1 rev3 C6, §Defaults) and `measure_sets.md` §3.6 (abi event exactly when a consulting
   reader exists); Goal 1 restated (two `--list-measurements` rows move at S2e); S1229 re-aimed; the other
   anchors re-read.
9. **Noise channel** (§4): derived rows `-` (strong form, no engine); loader refuses noise past 10^15 and a
   numeric noise on null/derived/fitted rows (format 2); test levers hand UNMEASURED always; MFMEAS gains a
   text digest of the handed triples; ksgen/`measures_table.inc`/KsKind role listed; MF_SITE_ABI the next
   free number at landing. The value half of CONTRACT-5 is pcrec's K138 (main's).
10. **Box time** (§3.7): J1-J5 ~196 points x 7 launches, ~22 min timed; the window to ask for: **35 minutes**.

## Findings while revising (for main)

- **F1 (D188 fact (b) vs the stamp).** `MEMFN_FORMS` names the levels the emitted TEXT carries
  (`match_api.md` §6.3.10¶4, `ID@LEVEL+LEVEL`), not what a fixture's compile built; under today's `#if`
  arms a stamp can name a level the compile excluded. D188's "read off the artifact's MEMFN_FORMS stamp"
  therefore holds for the BUILT code only where the stamp is per-built-code. Recorded as J6's design item
  (§2.7, §10.5); relay to Frank with the SIMD-model question if useful.
- **F2 (the two-member walk needs no force, probably).** `kit.h:546-555`: PAIR holds only for an asker that
  renders PAIR, "which the composer's renderers do not", so a composer FIND site on `{X,x}` takes R7w as its
  own first match: a site FACT, not a deny. S2c confirms the composer's R7w text equals the window's; the
  fallback is a `kit.h`-only test entry (§3.2). This answers PREMISE-5 with less than its proposed fix.
- **F3 (new spec sections are not citable before they exist).** The pre-commit cite check refused
  cites of the PROPOSED `measures.md` sections 3.4 and 3.5 in the section-sign form; the note spells them "`measures.md`'s new sections
  3.4-3.5". The build lane that adds them may cite them normally.
- **F4 (cells embed size, UNMEASURED).** ~1,370 cells (~96 KB) join `set.tsv` and are embedded twice
  (`measures.md` §8¶2); S2e reports the growth; an embed rule omitting cells from the pre-parse is a spec
  event only if main finds it material (§3.8).

## Evidence

- Drills (python only, no timing; `python3 -I <file>` from `docs/design/memfn/span_cards/`):
  `drill.py` (§3.4-§3.5 implemented from the text; every row of §3.5's table), `j1_drill.py` (no effect:
  a 0.9981 / b 0.0 / c 0.0019 over 20,000; effects 2/3/4/6 sd: b 0.0002 / 0.1202 / 0.8184 / 1.0 over 5,000),
  `coverage_drill.py` (trimmed s.d. rms 0.7618 sigma; with K_TRIM the one-card departure is 0.0673 at z 2,
  0.0386 at 2.5, 0.0252 at 2.9, 0.0226 at 3.0, 200,000 draws).
- Facts re-read at this branch: R-35 (`memfn/docs/requests.md:805-838`), D188 (`decisions.md:10064`), D176 Q3
  (`decisions.md`, D176), D186 add. 2 C9 (`decisions.md:10046`), K138 (`known_issues.md`), [KIT-POLICY-TABLE]
  and [XARCH-DEV] (plan.md), `measure_sets.md` §1.4-§1.7, §3.6, §7.1-§7.4, `measures.md` §2-§8,
  `kit.h:540-556`, `finder.c:656`, `window.c:1840`, kit-grid.tsv's header, `r33_report.md` "Sources".

## Charter vs committed

| charter item | committed | where |
|---|---|---|
| Read BOILERPLATE.md and memfn/CLAUDE.md first; first command `rev-parse` | done | — |
| Write only in the worktree; design only; named-path WIP commits | done (no C, no make, no timing, no box job; drills are python in the design evidence dir) | commits on `lane/memfn-s2rev1` |
| Apply every FIX-NOW and DOC disposition as ruled | done | span_cards.md §R1 + the sections below |
| Disposition table mapping every finding id | done | span_cards.md §R1 |
| DRIFT-1 | §2.7, §3.2, §9 S2g | ✓ |
| PREMISE-1 + SLOT-5 | §2.5 (scalar-only row 1, cost stated), §2.7 | ✓ |
| PREMISE-2 | §3.2 (builders per family), §2.7 (vrun's RUN-term regime with S2g) | ✓ |
| PREMISE-3 | §3.2 (formhash entry table), §9 S2c | ✓ |
| PREMISE-4 + SLOT-3 + CONTRACT-4 | §8.3 (RULED (B), three amendments), §1 Goal 1, §8.2 (S1229 and readers) | ✓ |
| PREMISE-5 | §3.2 (composer-site fact; kit.h test entry fallback) | ✓ |
| PREMISE-6 | §10.2 | ✓ |
| PREMISE-7 | §2.5, §2.7 (vany dropped; kit-kernels@1 unchanged) | ✓ |
| PREMISE-8 + CONTRACT-2 + SLOT-6 | §4.2 | ✓ |
| PREMISE-9 + SLOT-12 + CONTRACT-9 | §4.1, §8.2, §2.1, §4.4, §4.5 | ✓ |
| PREMISE-10 | §7 | ✓ |
| PREMISE-11 | §3.7, §2.1 | ✓ |
| PREMISE-12 | §3.7 | ✓ |
| PREMISE-13 | §3.6 | ✓ |
| MEAS-1 | §3.2, §9 (j) | ✓ |
| MEAS-2 | §3.5 | ✓ |
| MEAS-3 | §3.5 | ✓ |
| MEAS-4 | §3.4 step 5, §2.2, §3.5 | ✓ |
| MEAS-5 | §3.4 | ✓ |
| MEAS-6 | §2.3, §3.4 | ✓ |
| MEAS-7 | §3.3, §3.5 | ✓ |
| MEAS-8 | §3.6 (drilled) | ✓ |
| MEAS-9 | §6 (drilled) | ✓ |
| MEAS-10 | §3.4 step 6, §3.5 table | ✓ |
| MEAS-11 + SLOT-9 | §3.4 step 3 | ✓ |
| MEAS-12 | §2.3, §2.6 | ✓ |
| MEAS-13 + CONTRACT-6 + COST-1 + SLOT-10 | §4.3, §12.1 | ✓ |
| MEAS-14 | §3.7 | ✓ |
| SLOT-1 | §3.8, §4.4 | ✓ |
| SLOT-2 | §3.1 (seam split; misquote fixed) | ✓ |
| SLOT-4 | §2.4 | ✓ |
| SLOT-7 | §6; PLAN [KIT-POLICY-TABLE] (main's) | ✓ |
| SLOT-8 | §7 | ✓ |
| SLOT-11 | §9 | ✓ |
| CONTRACT-1 | §3.8, §5, §9 (o) | ✓ |
| CONTRACT-3 | §4.5, §8.2 | ✓ |
| CONTRACT-5 | §4.1, §4.4 (noise half, S2a); value half = K138 (main) | ✓ |
| CONTRACT-7 | §4.5 | ✓ |
| CONTRACT-8 | §4.2, §9 (e), (f) | ✓ |
| COST-2 | §7, §9 S2b | ✓ |
| COST-3 | §2.5, §2.7 (NOTED for main) | ✓ |
| COST-4 | §4.1, §8.1, §9 (bases), §2.6 | ✓ |
| COST-5 | §9 (why-red per row), §7 (control diffs the incumbent) | ✓ |
| COST-6 | §8.2 | ✓ |
| COST-7 | §9 (separability) | ✓ |
| D27 spec-first author for S2a | DEFERRED to S2a's build brief (ruled); not in this note | — |
| DEFAULTS (B): flip at S2e, zero movers, amends R-35 item 1 + span_pick rev3 C6 + measure_sets §3.6; Goal 1 restated; S1229 re-aim | done | §8.3, §1, §8.2, §9 S2e, §10.2 |
| D188 three facts per level; a set never grants | done, model-neutral | §2.7 |
| SIMD facts and J6 written without #if fall-through ("the built artifact contains code for level L") | done | §2.7 |
| J6 (vrun only) a separable unit marked HELD; scalar units independent | done (S2g) | §2.7, §9 |
| Row 1's position stated (recommend scalar-only, say what it costs) | done | §2.5, §10.4 |
| Derived noise DROPPED: `-` until a format-2 derived row has producer AND reader; no §3.2 column, no engine, sabotage (6) removed; general form an unlock with trigger | done | §4.3, §12.1 |
| Raw data in the spec's `cells` section; producer split along §7.1; D176 misquote fixed | done | §3.1, §3.8 |
| Estimator and gates an executable spec; literal integer recipe; drill table on clean / outlier / bimodal / A/A above spread / equal-effect sweep | done | §3.4, §3.5 table, §3.6 |
| MF_SITE_ABI "the next free number at landing"; each unit names its base and re-baselines after a lander | done | §4.1, §8.2, §9 |
| Sabotage ids the kit's from the top of the free range (R-35); each row states why it can go red | done (rows (a)-(q)) | §9 |
| CONTRACT-5 value half is pcrec's K138; S2a refuses noise past the bound | done | §4.1, §4.4 |
| Keep rev 0's valid content; mark `[rev1 <id>]` | done | span_cards.md |
| Update the CLAUDE.md line in docs/design/memfn/CLAUDE.md | done (+ `span_cards/` line and its own CLAUDE.md) | docs/design/memfn/CLAUDE.md |
| Lane report with this checklist; history index entry | done | this file; `docs/dev/history/claude_md/docs__dev__lanes.md` |

## STATE AT HANDOFF

Rev 1 committed on `lane/memfn-s2rev1`. OWED: nothing of the charter. Not a build go: the review's verdict
asks for a short re-check (fix-induced + readiness) before any build. No rulings file was named in the brief.
