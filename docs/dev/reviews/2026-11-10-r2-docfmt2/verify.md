## Verdicts

### READYU1-1 — HOLDS
Ran awk over the build-tree decisions.md for each cite's line, finding the last `^## D` heading at/before it. Of 7 checked cites, 6 fall in the entry PRECEDING the cited id, each off by 6-30 lines: spec_survey:30 D46@4005 is in D45 (D46 starts 4012); :31 D49@4292 is in "D47 SECOND ADDENDUM" (D49 starts 4299); :36 D37@3318 is in D36 (D37 starts 3324); variables_pattern:317 D120@8171 is in D119 (D120 starts 8183); compare_stack:318 D122@8288 is in D121 (D122 starts 8318); prior_cost_unify:44 D126@8655 is in D125 (D126 starts 8663). The only correct one is spec_survey:31's second cite, D51@4383, which is inside D51 (starts 4367). The 16/22 total was not recounted; the spot checks support the claim.

### READYU1-4 — HOLDS
Python -I over decisions.md at the build tree: `^## D\d+` headings with title (text after the id and the dash) > 200 chars = 33; max = D119 at 401. My heading total is 198, not 191, because I also counted the `## Dn ADDENDUM` headings, which does not change the title count.

### READYT1-1 — HOLDS
`wc -c scripts/CLAUDE.md` at the build tree = 4084. check_claudemd_size.sh:23 gives `echo 4096` as the hot-path limit (comment "every manager/lane session loads these"). Headroom is 12 B. I did not check the "list new scripts" rule text.

### READYT1-2 / FIXIND-3 — HOLDS
Read the ROWS block (scripts/gestalt:307-324). There are 12 kinds. The `--all` loop skips idle-held when `$idleheld` is empty (line 322), so 11 lines print, plus the trap's `gestalt: DONE rc=0` (line 46) = 12. That equals gestalt.test:25 `[ "$n" -le 12 ]`, so there is zero headroom. If idle-held is active, or any L_ variable is multi-line, --all prints 13 and the test fails. I did not run gestalt. The L_ci/L_unread/L_idleheld definitions are listed above this section; I did not check their line counts.

### READYT1-4 — HOLDS
Python -I over plan_completed.md with `^ *- \[TAG\]` (403 tag lines): tags on 2+ lines = 7 (FIX-2 at 153 and 190, M6.4.1 at 3521 and 3589, M6.5.1 at 3560 and 3651, OPT-5, OPT-VMSEED, PC-3, SR-8). Tags where every occurrence has `STATE:` near the head = 4 (FIX-2 is mixed, so it is not in the all-STATE set). The set {PC-3, OPT-5, OPT-VMSEED, SR-8} has STATE on both lines, so the two counts are 7 and 4 as claimed. With the column-0-only regex `^- \[` I get 4, so the 7 depends on the indented pattern.

### READYT1-8a / FIXIND-11 — HOLDS
Makefile:502-504 comment: the marker `$(TEST_TRAILER_DIR)/<name>.ran` is touched "as the FIRST line of its OWN recipe". Each recipe has this shape, e.g. Makefile:598 `@if [ -n "$(TEST_TRAILER_DIR)" ]; then mkdir -p "$(TEST_TRAILER_DIR)" && touch "$(TEST_TRAILER_DIR)/test-corpus.ran"; fi`. Same at 583, 622, 638, 642, ..., 976. TEST_SECTIONS is defined at Makefile:452. I did not check that every section in the list has one.

### FIXIND-2 — HOLDS
Makefile:2270-2277: `hookdir="$$(git rev-parse --git-path hooks)"` then `install -m 0755 scripts/hooks/$$h "$$hookdir/$$dest"`. In the crit-docfmt2 linked worktree, `git rev-parse --git-path hooks` prints /home/pcrec/projects/pcrec/.git/hooks, the COMMON git dir, so linked worktrees share one hook. scripts/hooks/pre-commit:45-46 prints "scripts/plan_lint.sh is missing in this tree; plan lint skipped" and carries on, and rc stays 0, so a missing linter is skipped. The spec-history check at lines 55-57 does the same.

### FIXIND-4 — HOLDS
docs/design/engine_m4.md:601 contains `` `../dev/decisions.md:358` ``. plan_completed.md:5816 contains `known_issues.md:188`. Both are line-number cites to a ruling file.

### FIXIND-5 / READYU1-9 — HOLDS
`D155 addendum 6` appears in docs/design/memfn/target_seam.md:362 (`> **D155 addendum 6 / [MEMFN-RTDISPATCH] (PROPOSED)`), `D155 add. 6` at :492, and `D155 addendum 6` in target_seam_units.md:133. In decisions.md, D155 addendum markers run 1 (:9319), 2 (:9325), 3 (:9338), 4 (:9345), 5 (:9352), then `## D156` starts 8 lines after :9352. `grep "D155 addendum 6\|D155 add. 6"` on decisions.md returned nothing. The cites point to a PROPOSED addendum that was never filed.

### FIXIND-7 — HOLDS
decisions.md:9858 and :9862 are `### D168 addendum 3 note — P2d built ...` and `### D168 addendum 3 note — P2e built ...`. Doc rev 2 line 192 says a NOTE on an addendum "is a `####` sub-heading inside it, label verbatim, unnumbered". §5.2 (ii) (lines 467-470) requires every owner-table row to be "exactly one `### new_id` heading inside `## owner`". Notes are census rows (they are "addend" lines under `###`) but would be `####` with no new_id, so the control's literal text contradicts the NOTE rule.

### FIXIND-14 — HOLDS
.claude/skills/pcrec-manager/monitoring.md:22-26 says gestalt "prints ONLY the items past their threshold (load > nproc, a session gone, disk >= 85%, context > 70% of compaction, CI not green, box idle with a ready job)" and "any line it prints goes in the one-line reply (and gets acted on)". The list omits the idle-held kind, so a new soft-cap kind needs this file updated.

### FIXIND-15 — HOLDS
decisions.md D147 markers: unnumbered at :9024, then addenda 2-13 at :9026-9152, 14 at :9331 (inside D155), 15 at :9417 and 16 at :9419. Appendix A line 48 reads "D147 (one unnumbered, 2-13)", which is stale against 2-16. Appendix A line 19 ("D147 x16") and line 95 (a1 through a16) are consistent with 2-16.

### FIXIND-8 — HOLDS
scripts/plan_lint.py:6-7 and 17: `--stale` is a separate informational mode for "stale `started` rows, unresolved [ID] references, MERGED-but-open rows"; stale_report() at :560-590 also prints a P14 list of not-started rows saying MERGED/BUILT/LANDED/DONE. Rev 2 line 321-322 defines `--stale` as "prints headroom under each file cap and the count of `?` and `-`". The T2 row says "PL01-PL17 unchanged in effect" and does not mention `--stale`.

### FIXIND-10 — HOLDS
scripts/hooks/pre-commit:44 greps `^(docs/dev/plan\.md|docs/dev/plan_completed\.md|docs/design/plan_row_bodies/)`. Rev 2's profile table (lines 277-279) has no row or column naming plan_row_bodies/ or a linter per path. plan_row_bodies/ appears only in prose (:399 "ABSORBED: plan_row_bodies/ (unit 2; C12 refuses new files)", :61, :310).

### FAITH-4 — HOLDS
Scan of decisions.md at the build tree (lines opening `**`, `- **` or `##` with "addend" in the first 120 chars, any case): 195 hits. I removed the 15 non-marker lines the critic lists (3804, 9056, 9058, 9126, 9132, 9156, 9158, 9349, 9445, 9494, 9506, 9691, 9728, 10091, 10115), all of which are in the hit set, leaving 180 markers. Markers whose first following non-blank line is another marker or starts with `#`: 33 of 180. If the other hits also count as markers it is 34.

### FAITH-6 — PARTLY (20 by bytes, 19 by characters)
Of the 180 markers, 78 are heading-form (line starts with `#`). Over 160 characters: 19. The critic's 20 line numbers are all heading markers and all are over 160 bytes. Line 9682 (`### D164 addendum 4 — one lowering per artifact...`) is 159 characters but 161 bytes. The line-9839 length is 249 characters (about 251 bytes) in my count; the critic quoted 251. The substance holds: appendix B (line 67) says `old_label` is "cut at 160 chars", the heading-form markers over that exist (19-20), and the unit (chars vs bytes) is unspecified.

### FAITH-7 — HOLDS
decisions.md:6886-6888 is the D98 heading across three lines (`## D98 — THE LIBPCRE2 ORACLE BINDING ...`, `2026-09-09, "if your test/evaluation passes ...` and `linktest's P1-P5 prototype passed; lane oralink ...`), then a blank line at 6889. That is two continuation lines. Appendix A line 53 says "D98's heading wraps onto a second line", which is one line.

### FAITH-2 and FAITH-3 — HOLDS (literal control, on the critic's toy)
I copied faith/w/{control.py,plants.py,plants2.py,good.md,orig.md} to verify/w/ and ran `python3 -I plants.py` and `plants2.py` with the copy as the work dir. Output:
- P3b (non-first lines moved a2 to a1): PASSES.
- P4 (a1 line moved into the D1 body): PASSES.
- P15 (lines reordered within a body): PASSES.
- P14 (blank line dropped): PASSES.
- P8 (body heading dropped): PASSES.
- P17 (phantom `### D2.a1` heading inserted, no table row): PASSES.
- Also P7, P9, P17b: PASSES. P3 (moving the hashed first line) is CAUGHT by the hash check.

Reading §5.2 (rev 2 lines 466-480):
- (ii) iterates over owner-table rows only. It requires "exactly one `### new_id` heading" per row, and nothing in (ii) requires every heading to have a row. C6 (lines 306-307) checks only that headings lie inside `## ID` with numbers unique and rising, which P17 satisfies.
- (iii) compares per-owner multisets of non-blank lines and excludes "heading lines on both sides", so P8, P9, P14 and P15 pass. An owner's body and its own addenda are pooled into one multiset, so P3b and P4 pass.
- Caveat: control.py is the critic's reading of the prose, not the doc's code. The reading is literal and I found no clause that closes these gaps, but the verdict depends on that reading.

VERIFY COMPLETE
