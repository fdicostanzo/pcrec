# CHK -- check adequacy (lens CHK), subject 1222b31be

Method: read every new/changed check and all 50 new sabotage rows; verified each SAB_BEFORE count against the source at SUBJECT (49 x1, S1368 x2: all match); transplanted the emitted-text mutations onto real emitted artifacts and compiled them with the suite's own GENCFLAGS (scratch only); probed the compiler by hand. Nothing run: no make, suite or matrix.

### CHK-1  S1354 and S1374 are "DETECTED" by a -Werror compile failure, not by the witness the row names
- status: CONFIRMED (repro: emit `pcrec -p t0 --subst '[$1|$n|$2]'` and `--subst '[${!v}-$1-$0]'`; apply each row's SAB_BEFORE->SAB_AFTER to the emitted .c; `gcc -O1 -std=gnu11 -Wall -Wextra -Werror -include r0.h -c`)
- severity: maintenance
- effort: S ; blast radius: two matrix rows, the credibility of their DETECTED
- where: tests/mech/sabotages/S1354_unset_error_renders_empty.sh, S1374_element_vars_one_short.sh; run_subst_tests.py "driver build" check
- body: S1354 (`if (sl == -2) return 0;`) leaves `flags` unused in `<p>_subst_group`: `error: unused parameter 'flags' [-Werror=unused-parameter]`. S1374 (`ctx->nvars < 1 - 1`, every one-variable template) fails `-Wtype-limits`. Either way run_subst_tests.py dies at "driver build" (failed=1) and the matrix scores DETECTED; the `unseterr` cell / the `vmis` arm never run. The cells would catch the plant if it compiled, but the row proves nothing about them (K35 / [MECH-REACH]: a witness that stopped reaching its site). Fix: plant in a form that stays warning-clean (e.g. `(void)flags;` / `< (size_t)(1) - 1u` is also flagged, so use `ctx->nvars + 1 < 1`), or add the plant-compiles check to the row. Other emitted-text rows I transplanted (S1346-48, 51, 53, 55-58, 63, 67-69, 78, 1500-03, 32-34, 37-38, 70, 71, 75, 1504) compile clean, so their detection is by cell.

### CHK-2  The d27 verdict has no population floor: REFUSED / REF_ONLY / "template refused" all pass
- status: SUSPECTED (current state healthy: 40 random d_fz patterns, 0 refused by pcrec); would confirm by seeding a regression that makes the parser refuse the d_grp patterns
- severity: maintenance
- effort: S ; blast radius: make test-subst-d27 (~1,500 cases), not in the mech arm
- where: tests/subst/run_d27.sh (family loop), tests/subst/d27/lib/run_diff.py verdict()
- body: a family passes with `FAIL=FINDING=FIXED?=0` and `PASS>=1`. PCREC_REFUSED (pattern refused), REF_ONLY and KNOWN are unbounded and uncounted, so a pattern-side regression that turns 95% of a family into PCREC_REFUSED stays green (K35: population nobody counts). Also verdict() passes any pcrec template refusal when pcre2 errs with -35/-58/-59/-49, whatever the reason (a pcrec compile-time refusal of `$9` would read as PASS because pcre2 says -49). Add per-family PASS floors (or PASS == total - declared exceptions).

### CHK-3  PCREC_MAX_TEMPLATE_GROUP (65535 / 65536) boundary is pinned by no behavioural check
- status: CONFIRMED by absence (`$65535` compiles, `$65536`/`${65536}` refused at offset 0, verified by hand; grep finds no 65535/65536 in tests/subst or subst-extended)
- severity: maintenance (contract: subst_api.md §2, "a group number above 65535")
- effort: S
- where: src/parse/subst_template.c:184; run_subst_tests.sh refusal table (`x$99999` only)
- body: mutant `v > 65536` (or `>=`) survives tests/subst. d27 d_tpl rows `$65535`/`$65536` do not catch it: pcrec accepting `$65536` gives BIND -16 and the d27 rule maps pcre2 -49 to "BIND -16 = PASS", so accept and refuse both pass. limits_check only checks the row exists. Compare the 128/129 name rows and 10/11 nesting rows, which do pin both sides. Add `$65535` (accept) and `$65536` (offset) rows.

### CHK-4  d27 oracle loads libpcre2 by SONAME, not the library the section resolved
- status: CONFIRMED by reading
- severity: maintenance
- effort: S
- where: tests/subst/d27/lib/ref_pcre2.py:16 (`C.CDLL('libpcre2-8.so.0')`) vs tests/lib/resolve_pcre2.sh (D98, PCREC_PCRE2_PATH "for the python one-resolution-point consumers")
- body: run_d27.sh gates on PCRE2_AVAILABLE from the resolver, then the python reference dlopens a bare SONAME. On macOS (no .so.0) it is an OSError (red, not a skip); on a box with a custom-prefix pcre2 (CI builds 10.46) it can bind a different version from the one diff_driver/subst_drv link. This is exactly the skew resolve_pcre2.sh's header says it exists to prevent.

### CHK-5  Cells hard-code libpcre2 10.46 answers; no version gate
- status: SUSPECTED (this box is 10.46; resolve_pcre2.sh's own comments cite 10.42 system and 10.48 Homebrew boxes)
- severity: maintenance
- effort: S
- where: tests/subst-extended/cells.tsv (77 of 79 cells P2 `same`), tests/subst/cells.tsv (43 `same`), run_subst_tests.py
- body: PCRE2_VERSION is available from the resolver but never consulted. On a different version any `same` cell whose answer moved reads as a pcrec FAIL, a loud false red; there is no "skip on other version" or "record the version" line. Print PCRE2_VERSION in the section and either gate or label.

### CHK-6  Several contract promises are guarded only by d27, and no sabotage row measures them
- status: CONFIRMED (cell-level `room` arm prints `rc,need,n==0&&prev==0` but run_subst_tests.py checks only rm[0] and rm[2]; need is never read)
- severity: maintenance
- effort: M
- where: subst_api.md §4¶14 (need = n + k*P, sneed sum overflow -> SIZE_MAX, sn unchanged), §10¶3 (`*support != support_id`), §10¶6a (batch = least of 64, cap/P, BATCH_PAIRS/ncap)
- body: mutant `o->need = k * P` (emit_subst.c:1054) passes the whole subst arm; only d27 t_element (`el.nospace.after.n`) catches it, and d27 is outside the mech arm (SAB_SUITES=subst only), so the matrix cannot show it. The `support_id` clause of the check has no row (S1356 removes only the abi compare; the `pcrec_subst_check` support clause is exercised in d27 t_bind only). The sneed overflow line (emit_subst.c:1111) and the 64 batch cap likewise. Either add `need`/`sn` to the cell-level room arm and two rows, or add a d27 mech arm.

### CHK-7  "Every pattern-compile option is refused with --subst": 8 sampled, default values slip through
- status: CONFIRMED (repro: `pcrec --engine=auto -p s -o o.c --subst x`, `--tune=0`, `--size-cap=degrade` all exit 0; 22 other pattern options I tried were refused)
- severity: doc (spec/code disagree on explicit-default values; tests sample only)
- effort: S
- where: cli/main.c (S1380's `memcmp(&d, &st->opt, ...)`), run_subst_tests.sh option loop, cli.md §1.19¶1, subst_api.md §5¶1
- body: refusal is a struct compare against defaults, so an option spelled with its default value is "ignored" (accepted), against the stated "never ignored". The test loop names 8 of ~30 options and does not count the population (K35). Either state the exception in the spec or refuse by presence; derive the loop from the option table.

### CHK-8  REACH tokens are shared, so one row's named witness can vanish unnoticed; one token is stale
- status: CONFIRMED (token counts from the two cells.tsv: S1348 x2, S1347 x2, S1534 x2, S1535 x4, agree x2)
- severity: maintenance
- effort: S
- where: run_subst_tests.py REACH_NEED, cells.tsv REACH column; S1357 (names duprun3 but reaches via token S1348, also carried by duprun), S1352
- body: a token needs "at least one passing cell", so deleting `duprun3` (S1357's only run-head-walk witness: bsearch must land mid-run) leaves S1348 satisfied by `duprun`; likewise S1347/`backward2`. Token S1352 remains in REACH_NEED although S1352 is now an equivalent mutant (its dirty arm is retired), so it guards nothing. Also, the p2 floor is 30 against 55 (core) / 79 (extended) compared cells: a loss of ~25 oracle cells is invisible.

## PROBED-AND-HELD
- SAB_BEFORE counts: 50/50 rows match their SAB_COUNT in the SUBJECT source.
- S1352 UNDETECTED/equivalent: held. The plant `1 ||` reads it->vars/nvars unconditionally; RX_ITER_INIT writes every field (match_api.md 3.8p5, emit `{FRESH,...,NULL,0,NULL}`), setters never change vars, so every contract-admitted state gives the same (v,nv). No other row is marked equivalent/UNDETECTED.
- Emitted-text rows listed in CHK-1 (about 25) compile clean, so their detection is by cells.
- Name length 128/129 (name128 cell + refusal rows) and nesting 10/11 both sides pinned; utf8 template refusal offsets, reserved prefixes (both compile paths), `--unset=` unknown, header #error, one-TU, sq/sQ, support unit bytes identical x3, ASCII, IMPLEMENTATION/STATIC builds: all pin a negative AND a positive.
- pcre2 comparison is real: SKIP is a loud line at the top of run_subst_tests.sh and run_d27.sh (d27 exits 0 on skip but says so); the driver compiles -DSUBST_PCRE2 from the same PCRE2_CFLAGS/LIBS; `same` cells compare pcre2 output to the cell's independent EXPECT; oracle absence does not weaken the other arms (S1370 etc. have cell-stated answers). Missing log or count is "unmeasured", not "detected" (score_arm).
- Makefile/TEST_SECTIONS/.PHONY/shards.tsv rows present and consistent; limits_check 76->78 matches the two new rows; examples hunk compares to expected.txt with cmp.

## NOT COVERED
- Parse-side and cli rows (S1359-S1362, S1372-73, S1376-77, S1379-82, S1536) and emitter table/helper rows (S1530-31, S1535, S1539, S1365-66): their effect needs the sabotaged compiler built; judged by reading only. S1500 ASan-only claim not reproduced.
- cite_floors.tsv subst_api=4 (floor vs the checker's own count) and c4_allowlist rows: read, not measured.
- d27 corpus content beyond sampling; the other families' PCREC_REFUSED counts.

## DONE
