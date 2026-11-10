# verify — docfmt
## Verdicts
Build tree: /home/pcrec/projects/pcrec/worktrees/crit-docfmt (6638e3679). Scripts: verify/w/census.py. "Doc" = subject_doc_index_format_rev1.md.

### PREMISE-1: HOLDS
Own scan (w/census.py) of lines starting `**`/`- **`/`##` with "addendum" in the first 80 chars, attributed to the enclosing `## Dn`: 17 bold `**Dn addendum k / Dn ADDENDUM (...)` addenda sit inside a LATER entry: decisions.md 4446 (D51 in D52), 5761 (D69 in D79), 5842 (D76 in D81), 5858 (D40 in D81), 9073 (D144 in D147), 9112/9125 (D148 in D149), 9134/9141/9150/9152 (D147 in D149), 9207/9209 (D148 in D150), 9226 (D148 in D151), 9331 (D147 in D155), 9417/9419 (D147 in D159). Plus the doc's 17 `###` (6590, 7727, 7747, 7799, 9388, 9393, 9547, 9584, 9779-9826) and 4 `## Dn ADDENDUM` headings outside their entry (4208, 4256, 6832, 9283; D106's three follow D106). `grep -cE '^\*\*D[0-9]+ addendum' decisions.md` = 51. Doc §1.1 lists six spellings; `**Dn addendum k (...)**` is not among them. So "17 inside a later entry" is 34 (17 `###` + 17 bold); the critic's "41" depends on whether the 4-7 `##` ones are counted (I get 38 with 4). Core claim holds.

### FAITH-1: HOLDS
decisions.md:6590 `### D89 addendum (...)` sits inside D94 (D94 heading at 6572, D95 at 6730); 6639 `**Addendum 2 (same exchange, 18:3x EDT)`, 6661 `**Addendum 3 (18:4x`, 6667 `**Addendum 4 (18:5x` name no id. Doc §2.2 gives no owner rule for id-less markers. Cites `D89 addendum k` exist in src/parse/rxt_compose.c, src/gen/emit_vm.c, tests/definitions/run_definitions_tests.sh, tests/rxtsource/run_rxtsource_tests.sh (git grep -l). Doc §5.1's multiset control is whole-file so a move between entries is invisible (by the control's text, line 426).

### FAITH-3: HOLDS
`grep -nE '^### D162 addendum 4' decisions.md` -> 9579 and 9801 (the second inside D167, 9750-). `git grep -hoE 'D162 add(endum|\.) ?4\b' | wc -l` = 31. Sub-numbers: 8462 `D123 ADDENDUM 3a`, 9350 `- **Addendum 4.1` (D155), 9743 `- **Addendum 1.1` (D166, not D165). `### D168 addendum 3 note` twice (9858, 9862). Doc §2.2/C6 say "keeps its number" and "unique and rising" with an integer `aN` grammar; no rule for these.

### READERS-8: HOLDS (one slip)
Same lines as FAITH-3: 8462, 9350, 9743 (in D166 range 9726-9749, so the critic's "D165" is wrong; `D165 add. 1.1` cites = 0, `D166 add. 1.1` = 10). `D155 add(endum|.) 4.1` cites = 12. The grammar/C6 conflict stands.

### PREMISE-3: HOLDS
decisions.md:4299 `## D49 ... (supersedes D42.3's −1 collapse)`; its body says "This SUPERSEDES D42.3's collapse ... the pre-release ABI rider, D47 SECOND" (4312-4313). D42's entry text has 0 mentions of D49 (awk over D42's entry: grep -c D49 = 0). docs/spec/tuning.md §2.10¶3 "the ladder derives `K` per pat(tern)" and :358 `<PREFIX>_UNROLL_K_WHY` stamps. Doc §5 critic reads "each details entry" only, so cross-entry currency is not in the procedure. Premise holds.

### FAITH-7: HOLDS
Same evidence as PREMISE-3: D42 has no pointer to D49, so writer and critic reading only D42 cannot see the override; doc §6 "read `scripts/entry`" returns D42 only. Cross-entry supersession exists in the file (D49 line 4299; critic's other lines 3202/2968/9383 not re-opened).

### PREMISE-4: HOLDS
`grep -cE '^## K[0-9]+' known_issues.md` = 139; `grep -oE '^## K[0-9]+\b' | sort -u | wc -l` = 134; duplicates K3 (2048/2074), K4 (2140/2170), K11 (2648/2677), K12 (2737/2763), K41 (5305/5426). Heading-word counts `grep -E '^## K' | grep -cw FIXED` = 71, OPEN = 42 (the doc's numbers are word counts over all 139 headings); by first heading per id (my python): FIXED 71 (word anywhere), OPEN 35, CLOSED 7, ACCEPTED 1, no state word 20 (critic's leading-state: 24; definition differs, substance same). Doc has no slot for the duplicate headings (C1 ids unique).

### SIM-5: HOLDS
(a) as PREMISE-4. (b) 20-27 headings carry none of the four states (definition-dependent). (c) upstream_issues.md: 26 `## ` headings, `grep -nE '^## ' | grep -vE '^[0-9]+:## U[0-9]'` -> 115 `## python re vs PCRE2: \v ...` has no Un id; states are a body bullet `- **Status**: suspected-bug|divergence-by-design|not-a-bug|fixed-upstream` (lines 8, 16, 33, 54 ...), shares no spelling with the doc's OPEN FILED FIXED-UPSTREAM CLOSED. Holds.

### READERS-1: HOLDS
tests/ci/shards.tsv:93 `test-plan-lint 2 4 ci-measured sections.tsv`; check_shards.sh:13-14 "every TEST_SECTIONS member has EXACTLY ONE row; every row names a real member"; Makefile:470-474 puts test-ci-shards in TEST_SECTIONS. tests/lib/san_excluded.txt:113 `tests/plan_lint/run_plan_lint.sh NO-C-RUN ...`; run_codegen_tests.sh [TT-9] (3599-3649) requires scripts in manifest XOR exclusions and exclusions non-vacuous. Doc §5 T2 row lists neither.

### READERS-2: HOLDS
scripts/hooks/pre-push-light:41 `[ -f tests/plan_lint/run_plan_lint.sh ] && run plan-lint bash tests/plan_lint/run_plan_lint.sh` (silent skip if absent); scripts/tests/hooks.test:66 greps for `run_plan_lint.sh`; pre-commit:45-46 `[ ! -x scripts/plan_lint.sh ]` -> "plan lint skipped" on stderr. Doc T2 names "pre-commit" only (line 387).

### READERS-3: HOLDS
`ls -la $(git rev-parse --git-common-dir)/hooks`: pre-commit (Oct 22) and pre-push (Oct 20), regular files, not links; installed pre-push line 41 is the same `[ -f tests/plan_lint/run_plan_lint.sh ] && ...`. pre-commit:44 glob `^(docs/dev/plan\.md|docs/dev/plan_completed\.md|docs/design/plan_row_bodies/)` names no details file; doc units 1/3 list no hook.

### READERS-4: HOLDS
`git grep -nE "(^|[^_a-z])decisions\.md:[0-9]+" | wc -l` = 153 (78 files); known_issues 27; plan_completed 18; plan_lint.py:55 CITE_ERE is plan.md-only and comments "plan_completed.md is append-only". Doc C8 (line 254) says "any profile's file anywhere in the tree" and gives no exempt list or migration.

### SIM-7: HOLDS
Same population as READERS-4 (my counts 153 + 27 lines vs critic's 161 + 26 occurrences; same order, definition differs). 14 of the decisions/known cites sit in live docs/design, plan.md, known_issues.md (my narrower path set). No C8 exemption list in the doc.

### READERS-5: HOLDS
`git grep -l plan_row_bodies | wc -l` = 46. docs/design/vlookbehind.md:593-596 and :1594: "home is a new long-form body, `docs/design/plan_row_bodies/VMREC.md` ... written by the stage-1 build commit ... adds it to ... that directory's CLAUDE.md" (an in-force design). plan_completed.md:6240 `refs: docs/design/plan_row_bodies/BOXQUEUE.md`. Doc unit 2 (line 390) names "boxqueue comment" only.

### READERS-10: HOLDS (structure)
`grep -cE '^## ' plan_completed.md` = 65, all date or "Completed <date>" headings (28 `## 20...` form, rest `## Completed ...`/`## Status lines superseded ...`); rows are `- [TAG] STATE:completed` lines. A moved details entry as `## TAG slug — ...` is itself a level-2 heading, so doc §2.2's cut rule and §4's "under the date heading" collide. PL01-PL17 exist (`"PL15"`, `"PL16"`, `"PL17"` in plan_lint.py).

### SIM-1: HOLDS
Python over plan.md + plan_completed.md: 728 distinct tags; id-shaped `^[DKU]\d`: D105-BUILD, K18-FIX, K38-FIX, K50-BNDSTART, K50-DD12AI-MANIFEST, K50-NULLGATE, K53-SELRETRY, K60-FIX, K88-HANDOFF-DENSE, U8-PICK (10). Doc line 204-206: "The id prefix picks the profile (`D`, `K`, `U`, bracketless TAG = plan)"; no fullmatch rule; slug lookup route not stated.

### SIM-2: HOLDS
Same script: live-tag lowercase kebab = 0; one-word live tags 27; dotted 8; `REVW.A1`, `DD-14.A2` exist (plan_completed). Doc §2.1: "the plan's `[TAG]` IS its slug" and slug rule kebab-case, 2-4 words, unique; C5 has no per-profile grammar (profile table §2.4 has no slug column).

### SIM-3: HOLDS
Tags in both plan.md and plan_completed.md: MEMFN, NULLABLE-ANCH, OPT-LITSCAN, OPT-REVEND, OPTLOOP, XARCH. Duplicates inside plan_completed: PC-3, OPT-5, OPT-VMSEED, SR-8. plan_completed head lines 397, of which 100 match `STATE:<s> — <title>`. Doc §2.3 says only "a finished plan tag falls through" and "exit 2 ambiguous slug".

### SIM-4: HOLDS (plan part re-run; slug part not re-run)
plan.md started+blocked rows: 38, each with a status line; 31 exceed 160 chars (max 298); 147 of all status lines exceed 160; live titles over 90: 36 (max 100). Doc §2.4 line 251 "C4 field caps (fail)"; unit 2 (line 390) sets `now` provisional = today's status, exempting only `?`. The slug-collision statistics (D 22/6/2, K 39/29) were not re-derived.

### FAITH-4: HOLDS
Doc §5.1(2) (line 425-426): "the multiset of non-heading body lines is identical before and after". Doc §2.2 (lines 159-161) adds `(was: "D26 addendum (owner, 2026-11-06)")` lines, and §2.5 shows them (lines 282, 286, 288): added non-heading lines, so the literal control fails on a correct conversion. The doc states no exclusion set.

### FAITH-5: PARTLY
Doc line 380-382 says the converter "accepts a MIXED file" and nowhere states how it recognises an already-converted addendum or requires idempotence (grep for idempot/already converted: nothing). Whether a re-run double-converts depends on whether the inline label line is consumed into the heading; §2.5 shows `### D47.a3 — 2026-08-18: RULING-5 ADDENDUM (...)` as a heading (suggesting it is consumed) while §2.2 says body "verbatim". The silence and the missing baseline for the HEAD re-run hold; the critic's concrete double-conversion is a mock of one reading, not shown to follow from the doc.

### PREMISE-2: HOLDS
D47 (decisions.md:4054-4166 + addenda 4208/4256): six rulings; the §2.5 statement covers possessify-then-rung, K constant, forward-work bound. Left out: ruling 3 (ALLOW/DENY forcing flags), 4 (third-amendment (b) struck), 5 (`$`-follow exemption, cured by RULING-5 a3/a4), 6 (lazy conjunct accepted), a1 (clamp deferred), a2 (ABI rider) = 6 distinct rulings vs "(+3 more)". D26 (1464-1592): statement has no `(+n)`; omitted: "pin your own offsets against your own convention" (l.86 of entry), tier-3 drift: demote the assertion (l.65-69), "a version bump is a deliberate re-measurement event" (l.119) = 3. "K ... named constant (8)" vs docs/spec/tuning.md §2.10¶3 (ladder derives K per pattern): see PREMISE-3.

### PREMISE-7: HOLDS
D191 (decisions.md:10119-10129). Statement covers: build units E1 R1 E2 L1 L3 (L2 after R-38), uncut span with signed offsets, repeats as copies, zero-width items. Left out (my count): census = record not gate and no-mover stops (1); scan byte from any position, kit picks position and verify extent (2); nothing about consumption crosses the seam (3); `<PREFIX>_REQ_BYTE` meaning kept, chosen by pcrec (4); agreement check retires (5); one run value never a second wider fact (6); lookbehind step-back capped (7); L3 ahead of A-POSDOM (8); [REWRITE-ADJ] design starts now (9); prefix skip stays [MATCH-KNOWN]'s, R-38 reports verified extent (10). Even grouped by the entry's four numbered rulings, 6+ remain; "(+3 more)" is too low.

### READERS-6: HOLDS (recipe text); leak itself not demonstrated
.claude/skills/pcrec-critic/SKILL.md:58-64 freezes "main's decisions.md/plan.md commit" and locates records as "file:line at the freeze"; :80 denies a plan row via `grep -n '^- \[TAG\]'` on plan.md; pcrec-memfn-manager SKILL.md:70-71 lists plan.md, decisions.md, known_issues.md as main's. Doc §2.3 has no `--rev`; doc unit 1 says "freeze both files" for decisions only, unit 2 column does not. Recipes `grep -n '^## D'` appear in 7 files (docs/dev/reviews/*/COMMON.md, process.md), not 11 by my pattern.

### READERS-7: PARTLY
Structure holds: doc §2.2 line 158-161 keeps a `(was: ...)` label only for UNNUMBERED addenda, so numbered `### Dn addendum k` headings (61 in decisions.md by `grep -hoE '### D[0-9]+ addendum [0-9]+'`, critic says 58) lose their old spelling; `git grep -hoE 'D[0-9]+ (add\.|addendum) [0-9]+' | wc -l` = 2714 cites; `D[0-9]+\.[0-9]+` dotted cites = 1091; `D.. ADDENDUM` 97. Table counts per form not individually re-derived (totals agree within a few percent); "11 recipes" is 7 by my pattern.

### SIM-6 not in list.

### PREMISE-8: HOLDS (a-d re-run; e, f not re-run, immaterial)
(a) 191 first headings: 155 end `(date, who)`, 33 are `## Dn — YYYY-MM-DD — title`, 3 other (D27, D28, D98). (b) `grep -c SUPERSEDED decisions.md` = 5, case-insensitive superseded 16, supersed* 47; none is 10. (c) plan_row_bodies: 22 files incl. CLAUDE.md; total 147,896 B (146,198 without CLAUDE.md); doc says 177 KB. (d) plan_lint.py has PL15, PL16, PL17 entries; `ROW_MAX_CHARS = 6000` (plan_lint.py:47); head lines (341 incl. 2 template heads) 35,630 chars / 36,321 B, not 35,289.

### COST-2: HOLDS (numbers); value argument is judgment
`grep '^## D' decisions.md | wc -lc` = 198 lines, 30,704 bytes (doc target central 38 KB). The titles state the first ruling (doc line 399), so the heading list is a partial substitute without slug, state or current statement; whether it suffices for recall is untested by the doc.

### COST-4: HOLDS
`git log --since=2026-10-27 --format=%h 6638e3679 -- FILE | wc -l`: plan.md 178, decisions.md 41, known_issues.md 19, plan_completed.md 7; total commits 1740; distinct commits touching plan.md or decisions.md 202. Doc lines 380-382 (mixed-file re-run) covers newly appended old-form entries, not edits to an existing row on an open branch (reading).

### READERS-11: HOLDS
`git grep -n 'pcrec-bench/docs/dev/known_issues.md:1270'` -> docs/dev/lanes/profread_report.md:31 and docs/dev/optloop/cycle1_profile.md:434; /home/pcrec/projects/pcrec-bench/docs/dev has decisions.md, known_issues.md, plan.md; plan_lint.py:55 CITE_ERE `(^|[^_a-z])plan\.md:[0-9]+` matches after a `/`, so a C8 generalized the same way matches the bench path.

### READERS-9, FAITH-2, FAITH-6, SIM-6, COST-1, COST-3: not in assigned list.

## VERIFY COMPLETE
VERIFY COMPLETE
