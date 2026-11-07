# COST findings

## Findings

COST-1 (design, maintenance; CONFIRMED by grep) S2a/§4.3 derived-noise rule is built ahead of need and its sabotage (6) has no code to plant in.
 `grep -rln cross-lin src tests memfn scripts tools` hits only src/core/ks_measures.c:35-38 (name registry); NO evaluator of derived values exists in C or ks_ref.py (pcrec never recomputes a derived value; measures.md 3.2 para 2). S2a says "derived-noise rule in spec, C and ks_ref.py": that is a NEW recompute engine whose population in zen4-grid3 is zero (design says so, 4.3 end), reader none (D77; the design itself defers interim-log2 on that ground). Sabotage (6) "ratio rule sums instead of quadrature" can go red only against that new engine plus a synthetic fixture; 4.3 also cites "8.2's recompute" but 8.2 is the numbers table (3.8 step 4 is the recompute) and that recompute reads raw.tsv with no derived rows. Fix: spec the noise column, store `-` for derived rows (UNMEASURED) until the first FILE-set reader; drop sabotage (6). Saves ~1 spec table + C/py evaluators + fixtures.

COST-2 (design) S2b->S2c ordering inversion. S2b writes `cells.tsv` (row-1 population) but `memfn/measure/` is created in S2c (3.1; worktree has no memfn/measure). Either S2b writes it elsewhere and S2c adopts, or cells.tsv's reader (G2 --cards) precedes its writer. Name the file's S2b home.

COST-3 (design, speed/size) J6 SIMD (~10 of ~45 min, 6 form ids) partly ahead of need. Reader is "Frank's C9 row" which has no design (2.5 says its own design picks keys). vany2/vany3 are NOT routed (2.3), so no emitted site can use them: cards for unroutable forms plus 4 formhash ids have no reader, only a future one. D186 add.2 C9 rules SIMD cards into stage 2 (held for vrun, which is routed); vany cards should carry a named trigger (first route) or ride J6 only for vrun. memchr-back deferral (2.5) applies the same D77 standard; J6 vany does not.

COST-4 (design) Overlap with in-flight lanes (D153, R-35 Concurrency; plan 80341284e [VLOOKBEHIND] stage 1 lands first, [RUN-POS-SET] 1/2p/2b after, stage 3 waits):
 - Files: S2a touches src/gen/memfn_sites.c, cli/main.c, memfn.h; alt_normal_form.md names memfn_sites.c (pcrec_memfn_wpos_cube) and cli/main.c:3108 (2a lever) and puts stage 3's seam crossing as an MF_SITE_ABI event (alt_normal_form.md:585,1909). Stage 3 and S2a will both claim 24. Textual conflicts are small, but the abi number is a land-order race: state "next free MF_SITE_ABI at landing".
 - Goal 1 / 8.1 baselines: "PCREC_ARTIFACT_ABI stays 95" and "emit_sweep byte-identical vs base" are only meaningful against a base that includes whatever landed; both landers bump abi and move bytes. Each S2 unit must name its base commit and re-baseline after a lander.
 - S2d `enter` times WHOLE ARTIFACTS from build/pcrec at the frozen commit (3.2): lookbehind/alt stages change entry text, so `enter` rows are stale on the next lander (2.6 only owes a pcrec: dep). Freeze commit after the landers or record it as the known staleness.
 - No overlap with the stream unification (no step built) or unit 3.0 (trigger only).

COST-5 (design, doc) Sabotage rows that cannot go red as written (critics.md:177):
 (3) fill hands format-1 noise as MEASURED: red only if the format-1 fixture has a non-`-` noise text; the witness (MFMEAS count 0) is unspecified on that, and MFMEAS exists only in the PCREC_CAND_TRACE build (memfn_sites.c:107-123) so the witness needs that build variant. Name the fixture and build.
 (4) kit accepts UNSTATED: the witness column lists no test that builds an UNSTATED row (arm_fixtures/compose check). Add one or the row is undetected.
 (8) wrong-trace-field incumbent: the control compares the band-0 ARGMIN to smp20.out, and the argmin does not depend on the incumbent; smp20.out's incumbent lines (6-10) read WITNESS.out and qualifiers are "none" at P, so pick=incumbent either way. Red only if the control diffs the incumbent column too (a [MECH-REACH] risk, critics.md:75).
 (10) arm text from another method than its key: check C (finder_check.py) resolves card deps to ids/hashes; it never sees the rendered cell text, so it stays green. Needs a cell-text-hash vs dep-hash check in G2 --cards.
 (13) producer noise off by one: the recompute is red only if S2e's recompute is a separate implementation (3.8 says so); sound. (1),(2),(5),(7),(11),(12),(14) go red by computation, (7) only with a `-` noise row in the format-2 fixture.

COST-6 (maintenance, minor) Missing readers: tests/knowledge/mfixtures.py:177 holds the existing "format 2 refused" reject row (flips to format 3); S2e's `--list-measurements` re-pins are 30 hits under tests/ (tests/mech/sabotages S1228,S1229,S1237,S1241,S1245,S1246, run_measures_tests.sh, run_code_tests.sh, c4_allowlist.tsv, arch_blind_check.py), listed only as a grep recipe, not in the unit; and DEFAULTS flip (B) moves "bare compile reads latest": tests pinning the default set (S1229) move at S2e. New memfn/measure/CLAUDE.md is subject to the 12 KB gate. cells.tsv/raw.tsv: named readers exist (driver; recompute) - held.

COST-7 (answer-free cost note) Unit separability: S2a (seam+format2) lands/reverts alone only if S2e is not landed (S2e's set is format 2); S2c alone is revertible; S2d/S2e are order-locked to S2c. S2b is separable. Costliest piece is S2a (kit abi + 7 pcrec files + spec + 2 digest implementations) for a field with NO reader until row 1; cheapest-first alternative: land S2a after S2d only if the window shows noise worth storing is not possible (noise is needed to build the set), so S2a stays; just do not add COST-1's engine.

## PROBED-AND-HELD
- Sabotage (1),(2),(5),(7),(11),(12),(14) go red by the design text; correct build green (7 rows).
- raw.tsv reader (recompute check) and cells.tsv reader (G2 --cards/driver) exist; held.
- No change to stream unification / unit 3.0 files; plan rows checked: [STREAM] none built, [VLOOKBEHIND], [RUN-POS-SET] stages.
- Window time arithmetic 32/45 min consistent with table rows (sum of J1-J6 = 31.5).
- memchr-back and hors deferrals consistent with D77.
