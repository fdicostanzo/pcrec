# CHECKHAR findings (crit-covs2code)

Lens: check adequacy of the subject's non-sabotage test/harness checks (kitproof loader/cases/answers/run_cover/reach/width_opt + floors, axes width arm, san lists, cloud shard tables, run_anchored_match §4c, registry limits, cli, codegen/recid pins, endmark). Review tree = SUBJECT ad6f4cb56.

## Findings

### CHECKHAR-1 — the W arm's sub-populations are uncounted (K35) — CONFIRMED (by count + reading)
- Severity: maintenance (a check-strength gap; no answer is wrong today). Effort: small. Blast radius: tests/kitproof/run_cover.sh only.
- Where: tests/kitproof/run_cover.sh, the K35 block at its end (`[ "$nv" -ge 60 ]`, `[ "$nf" -ge 21 ]`, `[ "$na" -ge 140 ]`).
- The floors count row KINDS, not ARMS. Today: verdict = 48 default + 1 N + 11 W = 60; facts = 19 + 2 W = 21; answers = 108 default + 32 W = 140 (counted with awk over cases.tsv/answers.tsv). The block's own comment names the split ("verdict 50 + 10 W twins", "answer 105 + 32 n >= 33 rows on W") but no code checks it, and the comment's verdict arithmetic does not match the table (48/1/11, not 50/10).
- Failure input: delete the 11 W verdict rows and add 11 default-arm verdict rows (or delete the 32 W answer rows and add 32 default-arm answer rows): every floor stays met and the run is green with ZERO W-arm verdicts or answers, i.e. the stage-2 long-span answers past 32 are no longer tested by kitproof at all. (A single W row whose FLAGS lose the W does go red, via REACH for answer rows or the verdict for cover rows; the gap is delete+add, which a re-generation or a table tidy produces.)
- Fix: count W (and N) rows per kind and floor them (W verdict >= 11, W facts >= 2, W answers >= 32, N verdict >= 1), the same literal-floor shape.

### CHECKHAR-2 — cases.tsv `answer` rows are not read by the check; their sync with answers.tsv is unchecked — CONFIRMED
- Severity: maintenance (pre-existing mechanism; stage 2 adds 35 rows through it). Effort: small. Blast radius: kitproof.
- Where: tests/kitproof/run_cover.sh verdict/facts loop, `answer) ;;` (the cases.tsv answer rows are skipped); the answers loop reads answers.tsv only; gen_answers.sh is "NOT run by make test".
- Repro (copy of run_cover.sh + loader.sh + drv.c + width_opt.c in CHECKHAR/rc/, root = review tree): cases.tsv = one verdict row + one INVENTED answer row `answer - (?:zz|q)+ zz` (a pattern that is not even a cover); answers.tsv = one real a{5} row. `bash CHECKHAR/rc/run_cover.sh $REVIEW`: the invented answer row produces NO failure of its own (the only FAILs are the planted verdict row and the floors). A deleted cases.tsv answer row is equally invisible (answers.tsv still holds it). So the population the floor counts (answers.tsv) and the population an author edits (cases.tsv) can drift silently until someone with libpcre2 10.46 re-runs gen_answers.sh.
- Today in sync: cases.tsv's 140 answer rows, hex-encoded as gen_answers.sh does, equal answers.tsv's first three columns exactly (cmp, 140/140).
- Fix: run_cover.sh compares cases.tsv's (FLAGS, hex(PATTERN), SUBJECT) triples with answers.tsv's first three columns (no libpcre2 needed); a mismatch is a FAIL naming the row.

### CHECKHAR-3 — `width=N` verdict is computed against the default whatever the row's arm; the self-test blesses `iuRWN:width=24` — CONFIRMED
- Severity: maintenance (fails LOUD, a false red, never a false green). Effort: trivial. Blast radius: kitproof loader.
- Where: tests/kitproof/loader.sh `kp_width_verdict` (reads KP_D only), `kp_row_check` (accepts width= on any FLAGS), run_cover.sh self-test row "iuRWN:width=24" listed as LEGAL.
- Repro (same copy run): row `verdict W abcdefghijklmnopqrstuvwxyzabcdefghijklmn width=40` -> `FAIL: verdict W ...: RX_DFA_SCAN "cover", expected a decline`. The compile at W (4095) correctly reads cover; the loader expected the default-arm answer. Also `WN` together passes the row check and emits two `--window-search-width=` flags (last wins, 31), an arm no doc defines.
- Fix: kp_row_check refuses `width=` on a W or N row (and refuses W+N together), or kp_width_verdict takes the arm's width.

### CHECKHAR-4 — the axes width arm counts no reach: a dropped option would be answer-identical by vacuity — SUSPECTED
- Severity: maintenance/check vacuity (answer risk only if the long-span path regresses AND the option stops reaching the batch path). Effort: small. Blast radius: tests/axes/run_axes.sh width arm.
- Where: run_axes.sh, the `[COVER-CAP] stage 2 B7` block (job_label/job_flags/job_lost_ok only). Its comment claims "every cover the default declines for width alone becomes a cover here", but nothing counts covers or route moves for this job (no floor like the kitproof REACH). cover_cap.md §6 names the movers (counterk.rxt:1919, spanarms.rxt:96, d27_large_counts.rxt:6 and :37, x2 encodings), so a floor exists to pin.
- The arm reaches the compiler through RXTFLAGS with HARNESS_BATCH=64 (the batched dispatch path); the kitproof W rows prove the option only through the single-pattern `pcrec-harness --harness=kit-proof` lever. If the batched path ever ignored or re-defaulted the option, the arm would compile the default routes and stay green.
- What would confirm: one rxt holding counterk.rxt:1919's pattern through tests/harness/run.sh with RXTFLAGS=--window-search-width=4095 HARNESS_BATCH=64, reading the artifact's RX_DFA_SCAN (NOT RUN: a suite runner, outside this lens's rules). Fix: a per-arm count of artifacts whose RX_DFA_SCAN moves to cover, floored at the §6 mover count.

### CHECKHAR-5 — no check pins the option's admission boundary at a width past the default — CONFIRMED (by reading; the code holds)
- Severity: maintenance (route only; a cover admitted one position wide still answers right while <= the ceiling). Effort: trivial. Blast radius: kitproof.
- Every width the checks use is the default (32, @LD/@LD1), below it (N = 31; width_opt 24/23) or the top (W = 4095, where n = w + 1 = 4096 cannot be built). The CLI accept rows (1, 2047) check rc and an artifact only, no route. So a width comparison that is exact at <= 32 but off by one (or clamped to the ceiling) only above 32 — the new counted-statement territory — has no witness. Probed: harness lever at w=33 ({33} cover, {34} unanchored) and w=40 ({40} cover, {41} unanchored): correct today.
- Fix: two verdict rows at one intermediate width (e.g. a letter `M` = --window-search-width=40 with {40} cover / {41} decline), or two width_opt route() lines.

### CHECKHAR-6 — run_cli_tests.sh width rows hard-code 4096/2047 and check refusal by exit code only — CONFIRMED (by reading)
- Severity: maintenance, low. Effort: trivial. Blast radius: tests/cli.
- Where: tests/cli/run_cli_tests.sh, the `[COVER-CAP] stage 2, review r18 CHECKS-2` block. The ceiling is a literal 4096 (refused) and 2047 (accepted) while loader.sh, width_opt (via run_cover) and the axes arm all read --list-limits; the CLI's own edge (ceiling - 1 = 4095 accepted) is not tested here (it is reached only by the kitproof W rows through pcrec-harness). The refusals of `x` and `` are by nonzero rc + no artifact only: an unknown-option refusal would pass them (the accept rows do catch a removed option, so this is weak, not vacuous).
- Fix: read the ceiling from --list-limits; accept ceiling - 1; grep the refusal for "window-search-width" / "invalid".

## PROBED-AND-HELD
- answers.tsv independence: ALL 140 rows re-derived through the round's kit oracle (libpcre2 10.46, tests/kitproof/oracle.c) from answers.tsv's FLAGS/PATTERN/SUBJECT columns: byte-identical to the committed ANSWER column (140/140, incl. the 32 W and 3 Wu rows; the oracle reads `u`/`i` by memchr so `Wu` gets UTF). cases.tsv answer rows == answers.tsv first three columns (140/140).
- Loader arithmetic from --list-limits (subject build): KP_D = 32, KP_CEIL = 4096; W -> --window-search-width=4095, N -> 31; @LD1 = 33 letters, {@D1} = {33}, {@D} = {32}; kp_width_verdict 32 cover / 33 decline.
- W rows really run past 32: reach.sh W '[0-9a-f]{@D1}' -> REACH-COVER why [cover]; reach.sh - same -> REACH-DECLINE why [width-limit]; harness lever at 4095 on [0-9a-f]{1000} -> cover; reach.sh N '[0-9a-f]{@D}' -> REACH-DECLINE [width-limit] (the N row's decline is the width, not some other conjunct).
- facts values: reach.sh --facts W 'a{4095}' and - 'a{600}(?:b|cc)' -> REACH-FACTS-EQUAL (2 compiles, watchdog-bounded).
- Floors are EXACT: counts 60/21/140 equal the floors and width_opt prints exactly its floor of 8 ok lines, so deleting any one row/line goes red. The copy run with a 1-row table went red on all three floors.
- run_anchored_match §4c: gcc -c known.c at -DPCREC_ANCHORED_MAX_STATES=4097 fails with "the cover seam: PCREC_ANCHORED_MAX_STATES exceeds the memfn kit's declared window bounds ..."; at 4096 compiles (rc 0). Bound read from memfn.h (MF_WSPAN_POS 4095), independent of pcrec.
- width_opt.c (built against the review tree's libpcrec.a): all 8 ok with CEILING 4096; with a WRONG ceiling argument it goes red in both directions (5000: legal 4999 refused; 4000 and 33: the refusals at 4000/4001 and 33/34 fail). Library 0 = the built-in default is exercised by every default-arm verdict row (the CLI leaves the field 0).
- Invented verdict row with a wrong value -> red (copy run); unknown FLAGS letter / non-decimal width= -> refused (the script's own self-tests, read).
- Shard/list populations: run_cover.sh moved from san_excluded.txt to san_scripts.txt and appears in cloud_san_shards.tsv (shard 3, ESTIMATE weight); all 14 new sabotage ids (S3234, S3250-S3254, S3258, S3260-S3266) appear once in cloud_mech_shards.tsv; mech shard rows 1322 = sabotage files 1322. The axes unit word `--window-search-width` matches axes_has's whole-word test.
- Registry: limits_check manifest +PCREC_DEFAULT_WINDOW_SEARCH_WIDTH (count 82), bespoke-flag arm for --window-search-width= (own ok/bad pair), PCREC_WSTMT_POS/REACH on the non-limit allowlist; run_registry_tests pins 44 passing checks (read).
- Codegen ABI_EXPECT 109: the subject's artifacts carry "abi 109" in their header (seen on 5 compiles).
- Intermediate widths (harness lever): w=33 {33} cover / {34} unanchored; w=40 {40} cover / {41} unanchored.
- Compiles used: about 18 (reach 5, harness 5, §4c 2, width_opt 1, copy run 3, plus gcc of drivers).

## NOT RUN
- CHECKHAR-4's confirmation (the width arm through tests/harness/run.sh with HARNESS_BATCH=64): a suite runner; also cloud_axes_check.sh (runs run_axes.sh in plan mode).
- run_recursion_identity.sh FILEPIN/ABASEPIN b2d73b6b1 (whole-corpus byte compare) and endmark §5's -D reference builds (whole-compiler builds): read only; the endmark -DPCREC_DEFAULT_WINDOW_SEARCH_WIDTH=2 is required by limits.h's _Static_assert (width <= ceiling - 1 = 2), consistent.
- run_cli_tests.sh rows not executed (read only).

CRITIC COMPLETE
