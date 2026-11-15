# DRAFTSETS findings

## Q2 answer

A set mixing ISA levels is refused ONLY when the two est.py tables disagree with each other: P1-P3 were REFUSED with `DRAFT-ISA-LEVEL MIXED`, but a consistent table edit (P4) or a row whose label hides AVX2 code (P5) were silently accepted into the x86_64/zen4 set (DRAFTSETS-1, -2). Identical generic/x86-64 text shares one cell, but only by construction (a key names a form with one instance and one target), and nothing checks it; different text under one key is silently collapsed too, though distinct forms from generic and x86-64 correctly land as separate rows in one set (DRAFTSETS-4).

## Findings

### DRAFTSETS-1 — the ISA-level guard checks the table against itself, never the code (CONFIRMED)
- CONFIRMED. est.py:794-796 + :919-925. The guard compares `TARGET_SET[t].class` with `TARGET_LEVEL[t]`, two hand-written tables in the same file keyed by the same label `t` (cell_text.tsv's `target`). It never reads the kit's target facts (`arm_fixtures --target-facts`: generic `-`, x86-64 `fxsr,mmx,sse,sse2`, x86-64-v3 `avx,avx2,...`) nor the `target_isa` column link.py wrote from the object's instructions. learnings §3: the control shares a source with what it controls.
- Repro: draftsets/plants.py on est's synthetic mfcard window (`SLOT_TREE=<review tree> python3 -I draftsets/plants.py draftsets/runs P4 P5`). Outcomes:
  - P1 x86-64-v3 -> ("", x86_64/zen4) in TARGET_SET only: REFUSED, "DRAFT-ISA-LEVEL MIXED ver 6's set baseline (class x86_64/zen4) would hold row kit.find_byte.mfind-w32 built for ISA level x86_64-v3".
  - P2 generic -> v3 set: REFUSED (ver 3's set -v3, row kit.find_byte.libc).
  - P3 x86-64 -> v3 set: REFUSED (row kit.find_byte.mfind-w16).
  - P4 the same edit made to BOTH tables (TARGET_LEVEL["x86-64-v3"]="x86_64"): WRITTEN, SILENT. A single zen4-grid6 x86_64/zen4 set holds 88 rows including every mfind-w32 (AVX2) row; no v3 set.
  - P5 label lies (cell_text target `generic`, target_isa `avx,avx2` for mfind-w32): WRITTEN, SILENT. The AVX2 rows land in the x86_64/zen4 set.
- Expected (the ruling): "the guard refuses a set mixing ISA levels". P4 and P5 mix levels and are not refused. The selftest's mf_mixed plants only one half of the table (P1's shape), so it cannot see this.
- Mitigation: in a real run link.py's isa_check (link.py:189-201) holds each object to its keyed target, so P5 needs a post-run edit (see DRAFTSETS-2). P4 is a plain source edit of est.py and is caught by nothing.
- Fix (small): derive each row's level instead of declaring it. Level = baseline iff the row's target features (the kit's `--target-facts`, or the run-time `target_isa` column) are a subset of the floor's (link.floor_features). Then hold the set's class to the derived level. TARGET_LEVEL is deleted.
- severity: design (check validity). effort: S. blast radius: draft sets of every ver-6+ window, est selftest.

### DRAFTSETS-2 — est reads the set-deciding `target` from cell_text.tsv without checking it against the manifest pin, and collapses duplicate keys silently (CONFIRMED)
- CONFIRMED. est.py:769-789 (cell_texts) + :353-376 (manifest_check).
  - run.py:171 pins `cell_text` sha-256 in each job's manifest. est never compares it. manifest_check reads only `run_id`, `plan` and `L*`.
  - manifest_check is called only from fused_facts, so only for jobs holding kit.verify_cmp rows. JMB and JMH (the ver-6 jobs) are never manifest-checked at all.
  - cell_texts keeps the LAST line per arm key. It never reads the `instance_hash` or `target_isa` columns, and it refuses only on a fold-hash disagreement per form.
- Repro (draftsets/plants.py):
  - P11: after the run, every `x86-64-v3` in JMB/JMH cell_text.tsv is rewritten to `generic`, and the manifest's cell_text sha is replaced by zeros. Result: WRITTEN, SILENT. One x86_64/zen4 set holds the mfind-w32 rows; no v3 set.
  - P10: a second line for kit.find_byte.mfind-w32 labelled `generic` in JMH's cell_text. Result: WRITTEN, SILENT. 21 v3 rows in the v3 set, 1 AVX2 row moved into the baseline set (67 rows).
  - P8: the same key twice, IDENTICAL instance hash, targets generic + x86-64. Result: WRITTEN, one row, no duplicate.
  - P9: the same key twice, DIFFERENT instance hashes (h1 generic, h2 x86-64). Result: WRITTEN, SILENT, one row; the last line wins.
- Expected: a cell_text.tsv that differs from its pin, or a key whose lines disagree on target or text, is REFUSED. The draft's set split depends on this column, so it is input the record must vouch for (r9 G3: "THE RECORD IS THE INPUT").
- Reachability: link.py writes one line per arm per job, so P8-P10 need a hand-edited or stale rundir (for example a later dry/link pass rewriting cell_text.tsv in place under another kit). P11 is exactly that shape.
- Fix (S): (1) check every ran job's manifest (not only verify jobs), including `cell_text` against the file; (2) refuse a key seen twice; (3) hold `target_isa` to the level the set's class names (also covers DRAFTSETS-1 P5).
- severity: design (check gap). effort: S. blast radius: est draft/rows on any window.

### DRAFTSETS-3 — an unknown kit target crashes est with a KeyError traceback instead of a refusal (CONFIRMED)
- CONFIRMED. est.py:920 `TARGET_SET[tgt_of[r[0]]]`. main() (est.py:852-860) catches only InputError.
- Repro: draftsets/plants.py P6 (mfind-w32's cell_text target `x86-64-v4`) -> `CRASH(KeyError): 'x86-64-v4'`. That is LOUD (rc != 0) but has no message naming the table or §2.7.
- Trigger: plan.py UNPLANNED6 already names the OWED `mfind-w64` (AVX-512BW) arm. Its kit target (a v4 or avx512 target, not in the kit table today: `--target-facts x86-64-v4` -> "no target") will reach this line the day it is planned.
- Fix (XS): `if t not in TARGET_SET: raise InputError("DRAFT-ISA-LEVEL: target %s has no draft set (span_cards.md §2.7)")`. Or, with DRAFTSETS-1's derived level, map any level to a set suffix by rule rather than by row.
- severity: maintenance. effort: XS. blast radius: est draft.

### DRAFTSETS-4 — "identical text shares one cell" is true only by construction, nothing checks it, and §2.7 still says "a set is one target" (CONFIRMED, doc/test)
- CONFIRMED by reading the code and the P7/P8/P9 plants.
  - A row key carries no target token. A form has ONE kit instance with ONE target (`--frame`: mfind-swar/fn-memchr `generic`, mfind-w16 `x86-64`, mfind-w32 `x86-64-v3`). So the harness has no way to time the same text under generic AND x86-64 as two cells.
  - The ruling's "shares a cell" holds VACUOUSLY. No code compares site text across targets. P8 (identical text twice) gives one row, but only because a dict keeps the last line, and P9 shows DIFFERENT text is collapsed the same way.
  - The ruling's implication for DIFFERENT text from generic and x86-64 is two distinct cells in the SAME set: same ISA level, different code. The harness can express that only as two forms. It holds today (P7: mfind-swar relabelled x86-64 with fn-memchr generic gives one set, one row per form), and nothing refuses the bad shape (DRAFTSETS-2).
- Doc conflicts (span_cards.md §2.7):
  - ~line 791: "The card keys carry no target dim, because a set is one target." zen4-grid6@1 now holds two targets (generic + x86-64).
  - ~line 797: "(b) the built fixtures contain exactly the declared target's variant ... Every other target: absent, by the one-target rule". The new paragraph at :803 never amends these.
  - :803-807 states "shares one cell" as if est enforced it.
- Selftest: mf_levels (est.py:1446-1461) ends `and base_tg`, a non-empty literal set that is always true (dead conjunct). No MF case covers the identical-text clause or a generic+x86-64 pair of the same text.
- Fix (doc S): state that a key names a form whose instance has one target, so identical text cannot reach two cells. Restate the one-target rule as one ISA LEVEL per set (generic + x86-64 = one level). Drop `base_tg`, and add the P9 shape as a refusal case once DRAFTSETS-2 lands.
- severity: doc. effort: S. blast radius: span_cards.md §2.7, est selftest.

### DRAFTSETS-5 — D197's consequences not carried: several sites still describe a future pick, and the card calls the split cells "owed" (CONFIRMED, doc/design)
- CONFIRMED by grep at 1e3d4a17b. The code obeys D197: no selection table, policy row or default path reaches the rows (see PROBED-AND-HELD). The prose and statuses still describe the fused rows as a pick-in-waiting.
- Status and comments that frame a future pick of THIS row:
  - tests/memfn/rows.tsv:153-155: fn-mfind, mfind-w16 and mfind-w32 carry reach `pending-site:span_pick-row-1`. rows.tsv:29-30 defines that as "built ahead of the pcrec site that WILL reach it". Under D197 no site ever reaches these rows: a fused win builds a DIFFERENT, split shape. The comment at rows.tsv:56 ("pending-site: a measuring instrument only ... never picked") contradicts its own status token.
  - Fix: a reason token that says instrument (for example `contract-reach:g2_mfind`, or a new `instrument:D197` that rows_check.py REASONS accepts).
  - memfn/src/kit.h:674-675: "a reply under the lever reports MF_WSEARCH_NONE, until a selection table picks the form (then a kit-contract change)".
  - memfn/src/ofsskip.c:463-467 (mfind_holds): "a selection that picks the form replaces this predicate".
  - "a form no selection table picks YET" appears at memfn/src/compose.c:1474, src/core/internal.h:~203, cli/CLAUDE.md item (11) and tests/axes/run_axes.sh's mfind arm comment.
- Card text (memfn/data/cards/kit-grid.tsv ver-6 comment):
  - It says "the ruled single-piece cells (SEARCH vs the walk, STREAM RESTART vs MASK, D190) are not built and are OWED". D197 makes them CONDITIONAL: built only on a fused WIN, under their own owner go.
  - It also opens with "D190's search piece with the MASK stream", which reads as the D190 piece itself.
  - It never states D197's reading of the result: a ONE-SIDED test, where the fused per-hit cost is a lower bound for the split shape, a loss settles span_pick row 1 against the finder, and a win only triggers a build.
  - The set carries no tag for that reading. A future pricing reader of zen4-grid6 rows would take fn-mfind's value as a price of a pickable form.
- Citations: every site cites "F5, Frank 2026-11-15 ... see review r2-memfn-mfind" and none cites D197, the decision row a reader can find.
- Fix (doc XS-S): reword the six "yet/until/replaces" sites to "never picked (D197); a fused win builds the split shape under its own go". Change "owed" to "built only on a fused win (D197)". Add D197's one-sided reading to the ver-6 card comment and to span_cards.md where JMB/JMH are described. Re-token rows.tsv.
- severity: doc/design. effort: S. blast radius: comments, rows.tsv reason column (rows_check), card comment (no card row moves, no abi).

## Ruling check (part b)

- **D197 (instrument only): AGREES in code, NOT in prose.**
  - fn-mfind's predicate (ofsskip.c:468-471 `mfind_holds`) needs KIT_LEVER_MFIND.
  - mfind-w16/-w32 are PREFIX rows whose OVER is fn-mfind only (vrun.c:688; prefix_holds ofsskip.c:490-493), so they cannot hold without it.
  - The bit is set only by mf_lever (compose.c:1478-1488). pcrec calls that only under `cx->emit_in->harness->mfind` (memfn_sites.c:220-225), which only `--harness=mfind` under `#ifdef PCREC_HARNESS` sets (cli/main.c:1541).
  - formhash.c:455 sets it on a private art (`mf_art_begin` inside mf_form_hash). No T-FIND or window.c renderer row names FF_MFIND (kit.h:669-677).
  - Consequences not carried: DRAFTSETS-5 (rows.tsv `pending-site:span_pick-row-1`; "picks yet / until a selection table picks / replaces this predicate" in six places; card "owed"; no one-sided reading recorded; D197 never cited).
- **Draft-set ruling: PARTLY.** Ids and classes are as ruled (P0: zen4-grid6 x86_64/zen4 = mfind-swar + mfind-w16 + fn-memchr; zen4-grid6-v3 x86_64-v3/zen4 = mfind-w32). The guard is weaker than "refuses a set mixing ISA levels" (DRAFTSETS-1/2/3), and §2.7 keeps contradicting one-target sentences (DRAFTSETS-4).
- **§7.2 card binding: AGREES.** kit-grid.tsv has 0 ver-6 rows at BASE 04fe41c92 and at main 4ccd97ca7, and 2 at SUBJECT. No set holds one: measure_store has only zen4-grid1 and zen4-grid3. `run.py dry` writes no run record (record.py's `window` does, at timing). So the ver-6 rows are still drafts and the `reject` dim respell is allowed. There is no ver-7 row (0 at all three commits). The measure_sets.md hunk carries the ruling's wording verbatim. One unpinned word: "record" is undefined there. Reading it as the slot's run_record.tsv (`record.py window`) would make it precise.

## Standing: sibling of a family

The same fact, "which ISA level does this code/box belong to", is spelled THREE times by hand:
- est.py's TARGET_SET/TARGET_LEVEL (this subject);
- record.py:127-129's cpuid -> level ladder (avx512*/avx2+bmi1+bmi2+fma+movbe/sse4_2...);
- the kit's own target table (`arm_fixtures --target-facts`, targets.def: x86-64 = fxsr,mmx,sse,sse2; x86-64-v3 = avx,avx2,...).

link.py already does it right: isa_table_check/isa_check read the kit's facts. est.py does not. Sibling check gap: DRAFTSETS-2's unread manifest pin is the same family as manifest_check being run only for verify jobs. Every file the draft reads (cell_text.tsv, and placement.tsv, pinned and never re-checked) should be vouched for by the record.

## Standing: general form + unlocks

- **General form:** a draft set is keyed by the LEVEL the kit's target facts imply. Level = the least declared level whose feature set contains the target's features (one level table, shared with record.py's box ladder). Each row's level is derived from the kit's target facts and held to `target_isa` (link's measured needs). The box's level must contain the set's. No per-target rows in est.
- **Unlocks, each with its trigger:**
  1. mfind-w64 / AVX-512BW gets its own `-v4` set with no code edit. Trigger: UNPLANNED6's w64 arm is planned (today a KeyError, DRAFTSETS-3).
  2. J6/vrun-w16/-w32 under [XARCH-DEV] reuse the split. Trigger: XARCH-DEV go.
  3. A non-x86 kit target (an arm64 family on the Mac) maps by the same rule. Trigger: the first non-x86 target in the kit table.
  4. The box-admits-set check ((a) of D188) becomes one subset test against the same table. Trigger: a draft written on a box below a set's level.

## PROBED-AND-HELD

- P0 control (`plants.py P0`): the ruled split as declared. WRITTEN: draft.tsv zen4-grid3 (11 rows), draft.v6.tsv zen4-grid6 x86_64/zen4 (66 rows: fn-memchr, mfind-swar, mfind-w16), draft.v6-v3.tsv zen4-grid6-v3 x86_64-v3/zen4 (22 rows: mfind-w32). No row in two sets.
- P1/P2/P3 (one-half table edits: v3 into baseline, generic into v3, x86-64 into v3): all REFUSED, `DRAFT-ISA-LEVEL MIXED`, no draft file written.
- P7: mfind-swar relabelled x86-64 next to fn-memchr generic. One baseline set, one row per form, no duplicate, no refusal (the ruling's generic + x86-64 = one level holds).
- P8: identical text under generic + x86-64 for one key. One row, no duplicate. It holds only by dict collapse (DRAFTSETS-4).
- D197 code reach: every route to KIT_LEVER_MFIND was traced (4 setters: mf_lever via pcrec harness flag, arm_fixtures/G2 tests, formhash private art). No default reach.
- §7.2: ver-6 row counts at BASE/main/SUBJECT = 0/0/2; ver-7 = 0/0/0; measure_store sets = grid1, grid3 only.
- Total: 12 plants (P0-P11), 5 SILENT (P4, P5, P9, P10, P11), 3 REFUSED as ruled (P1-P3), 1 LOUD crash (P6), 3 SAME-as-ruled (P0, P7, P8).

