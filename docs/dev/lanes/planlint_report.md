# planlint — [PLAN-LINT] step 3: the strict plan.md linter (2026-10-12, session 111, lane planlint, sonnet)

Docs and scripts only: no C, nothing under `src/`/`cli/`/`lib/`. Branch `lane/planlint` from main `e8ae2e4f4` (plclean merged), four commits: `a03052d23` (the row normalisation, plan.md + plan_completed.md only, so the identity check has a clean before/after), `4d4936f2b` (status polish), `4d4306adf` (linter, section, hook, docs) and this report. Input: Frank's rulings A-D (session 111), `docs/dev/reviews/plan_triage_2026-10-12.md` §6-§8, `plclean_report.md`.

## 1. The format as built (ruling A)

Defined in docs/dev/plan.md's Policy section (rewritten; it no longer says "status goes in the head parenthetical"). One row, a head and indented attribute lines:

    - [ID] STATE:<not-started|started|blocked|deferred> — <title, 1-100 chars>
      filed: <ISO date> <who>
      status (<ISO date>): <ONE line, <= 300 chars, rewritten in place>
      next: <step>   |   trigger: <the D77 measurement>      (required unless started)
      refs: <paths, D and K numbers>                            (optional)
      <charter: <= 6 lines of <= 1000 chars>
      - [CHILD] ...                                             (nested by 2 spaces)

Result on the 162 rows: largest row 4,938 chars and 11 lines; charters of 0/1/2/3/4/5/6 lines = 1/65/45/30/10/8/3 rows; longest line 1,013 BYTES (1,000 characters is the rule; em dashes are 3 bytes); plan.md 286 KB (was 271 KB: the added attribute lines). The section intro lines (5) were folded into Policy (P1 allows free text only there); the preamble keeps the title and one line.

How each field was made (all mechanical, then reviewed): `title` = 108 hand-written (ov table, from the row's own words) + 54 the charter's first clause; `filed:` = the first `FILED/CHARTERED/OPENED/...` clause with an ISO date (who from the words around it, else "filer not recorded"), else `Frank, <date>`, else the date of the row's first appearance in plan.md by `git log -S` (25 rows, labelled as such); `status` = the text after `STATUS <date>:` in the old head parenthetical, else the whole parenthetical, cut at 300 chars at a clause boundary (34 rows end in an ellipsis; the full text is in plan_completed.md), with "not started;" leading it for the 91 not-started rows whose parenthetical was only filing provenance and the bare words "not started" for the 33 that had no parenthetical at all; `next:/trigger:` = the first sentence beginning TRIGGER (56 rows), else a section default (91 rows: Candidates "selected by measurement when an [OPTLOOP] cycle opens (D119/D137)", Backlog/Boonies "starts on Frank's word"), else authored (below); `refs:` = every docs/studies/tests/src path plus D and K numbers in the row; `charter` = everything after the em dash, verbatim, reflowed at sentence boundaries. The `(under [OPTLOOP] candidates per D137)` pointer (10 rows) is not copied: the Candidates section says it.

Old head parentheticals, verbatim, are in plan_completed.md under "Row history moved out of live plan.md rows, format A normalisation" (126 `### [ID]` entries; headings, never `- [ID]` heads, so no row has a second home). Content check (independent of the converter): every whitespace-token of every old row is present in its new row or its history entry, case- and punctuation-insensitively: 162 rows compared, 13 with missing tokens, all explained: the 10 `(under [OPTLOOP] ...)` pointers, FIND-DOMAIN-CHECK's moved tail note, PCRE2-UP's moved body, FINDALL-NEXT's embedded duplicate head.

## 2. The rules (ruling B)

17 rules, PL01-PL17, each of which FAILS; no warning severity, no baseline file, no generated index. Full table with the counts below in tests/plan_lint/CLAUDE.md. "Caught" = what each rule reported on the pre-normalisation file (main `e8ae2e4f4`, 165 rows): 692 violations.

| id | rule | caught on the old file |
|---|---|---|
| PL01 | title + the six sections in order, no other heading | 0 |
| PL02 | no free text outside Policy; a blank line ends a row | 5 |
| PL03 | head `- [ID] STATE:<state> — <title 1-100>` | 152 |
| PL04 | finished rows leave (completed/done/HOLD/stub heads) | 0 (plclean had removed them) |
| PL05 | ids unique | 0 |
| PL06 | no live id has a completed row in plan_completed.md | 0 |
| PL07 | id syntax; dotted id's parent is a row somewhere (`Mx.y` exempt) | 0 |
| PL08 | nesting: parent indent + 2, no jumps | 0 |
| PL09 | head: balanced parentheses, even backticks | 15 |
| PL10 | attribute lines: presence, order, once, valid dates, <= 300 chars, next xor trigger, none after charter text | 356 |
| PL11 | line <= 1000 chars; charter <= 6 lines; row <= 12 lines and 6000 chars | 134 |
| PL12 | no bold in head/attribute lines | 30 |
| PL13 | section membership (top-level state per section; started/blocked only in Active) | 0 |
| PL14 | no `plan.md:<line>` citation in the tracked tree (`plan_completed.md` is append-only and exempt) | 0 |
| PL15 | `docs/design/plan_row_bodies/`: pointers resolve, every body file named by a row (ruling B's new rule, both directions, link checks only) | 0 |
| PL16 | Policy has no hand-typed state counts | 0 |
| PL17 | non-vacuity: >= 150 rows parsed (162 at adoption) | 0 |

Non-vacuity (P19): `--selftest` plants 32 violations (at least one per rule, 17 of 17 rules covered) in an in-memory copy of the real file and requires each to be reported by its own rule; it also requires the unplanted file to be clean and runs the citation scanner over a planted file under `build/plan_lint_selftest/`. `make test-plan-lint` fails if either half fails. Informational checks (ruling B) are `scripts/plan_lint.sh --stale`: P13 started rows with a status older than 30 days (none today), P14 not-started rows whose status says MERGED/BUILT/LANDED/DONE (3: ART-CTX-TRIO, START-DENSE, OPT-SETS, all of which describe a gate that opened), P15 unresolved `[ID]` references (17). Run by hand at wake, exit 0, not in `make test`. Skipped as ruled: the generated index (`scripts/plan_index`), P18's generated header (Policy carries no counts, PL16 holds that).

## 3. The commit gate (ruling C)

`scripts/hooks/pre-commit`, opt-in, never auto-installed, NOT installed by this lane. It does nothing unless `docs/dev/plan.md`, `docs/dev/plan_completed.md` or something under `docs/design/plan_row_bodies/` is staged; then it runs `scripts/plan_lint.sh --staged`, which reads the INDEX (`git show :path`, `git ls-files --cached` for the bodies), never the working file, and skips PL14's tree-wide `git grep` (that rule stays in `make test`). Install: `make hooks HOOKS=pre-commit` (new `HOOKS` variable, default `pre-push`, so plain `make hooks` is unchanged; `HOOKS="pre-push pre-commit"` installs both). Bypass `git commit --no-verify`.

Timing (Linux dev box, 3 runs each, `/usr/bin/time`): **0.06 s** on a clean staged plan, 0.08 s on a rejected one (one run, `time`), 0.006 s when no plan file is staged. The full working-tree lint is ~0.9 s wall, nearly all of it PL14's `git grep` (4.7 s CPU over threads); `--selftest` ~1 s; `--stale` 0.05 s.

Run directly from the lane worktree against its own index (not installed): staged-bad (a `STATE:completed` head plus stray prose) with a good working copy: blocked, rc 1, both violations named; staged-good with a deliberately bad working copy: passes (the gate judges the index); an orphan body file staged: blocked by PL15; nothing relevant staged: silent rc 0. The index was restored after each case.

## 4. The (ID, STATE) identity check (dispositions only)

`build/pl/idstate.sh a03052d23^` (grep/sed over `^ *- \[ID\] STATE:...` heads in both files; independent of the converter's parser):

    before: 165 pairs, after: 162 pairs
    55d54  < FORM-CHAR2 not-started
    57d55  < GUARD-MODULE-SWAP not-started
    107d104 < PC4-MISSING-SHAPES not-started
    unique-id check (after): 0 duplicate ids

Exactly the three listed dispositions; no other state changed. SR-8 stays `deferred`, BENCH-UTF8 and DOC-BM only changed format.

## 5. Dispositions and rows whose meaning I had to judge

- **[GUARD-MODULE-SWAP], [PC4-MISSING-SHAPES]**: deleted as ruled; verbatim text in plan_completed.md ("Deleted rows, 2026-10-12").
- **[FORM-CHAR2]**: archived as COMPLETED (row text verbatim, retagged, closure note citing decisions.md D138's addendum of 2026-09-30: Q1 ruled, the fold stays the default, `formchar2_report.md` §4a/§5 merged 59748d54; `-fno-cls-fold`, bit 24, `RX_VM_CLS_FOLDS` permanent per Q3). **Consequence to rule on: the absorbed [CLS-FOLD-WAF744] research item (boonies, unscheduled, why the caseless fold loses on waf744 on x86) now lives only in that archived text.** I did not file a row (ruling: no state changes beyond the dispositions); re-file it as a Boonies row if wanted.
- **[SR-8]**: kept `deferred`, rewritten with D55 as the settled premise. **The brief's trigger names `check_engine_capability_tripwire`, which no longer exists**: D67 (2026-08-22, [M6.4.2]) BUILT SR-8 as `forces_registry` in src/opt/select_engine.c and retired the tripwire into `check_engine_capability` (registry_check.c:2113, demands a witness per wired VM_ONLY row). The trigger now reads "`check_engine_capability` fails without a named exception", with the correction stated in the row. The row is arguably COMPLETED; recommend archiving it. Original text kept in plan_completed.md.
- **[BENCH-UTF8], [DOC-BM]**: format only. DOC-BM's `trigger:` is its own stated constraint (the document must exist before design section 7.1's five escape rows land), status "deferred; format normalised". BENCH-UTF8's old audit text became its status.
- **Two more wedged fragments** (the brief and plclean knew of four): [PC-2]'s head ended "re-read pcre2syntax.html," and its two continuation lines sat under [PCRE2-UP]'s head; reunited. [FIND-DOMAIN-CHECK] carried a second line, "BUILT 2026-09-28 (lane findtie ...)", which is the tail note [FIND-TIE]'s archived row points at ("see this row's own tail note") and which was never archived; moved verbatim to plan_completed.md.
- **Authored (not extractable) `next:/status`**: [XARCH] trigger = Frank's "a round in the future for architecture specific opt"; [SR-7] trigger = a second flavour-varying row earns the axis (its own text); [FINDINGS.B4] status/trigger (lands with OPT-LITSCAN S4); [COMPOUND] trigger = per client in the charter; [ENG-DIRECT] trigger = its own MEASURED TRIGGER sentence; [ENG-TACTICS] trigger = "see the charter"; [UCP]'s auto trigger (it was another row's re-sweep trigger) suppressed; [FINDALL-NEXT] status (the row was a plclean merge with a second embedded head; its two parentheticals are both kept in history).
- **Statuses that are provenance, not a current status**: 91 not-started rows never had a status sentence; `status` repeats the filing note led by "not started;", and 33 more say only "not started". The 34 cut at 300 characters end in an ellipsis. Both are honest excerpts; the full text is in the history section.
- Smaller: [PFX-1] lost a stray ". " between its parenthetical and charter; [M4-SUBST] and [DD-11.5] had hard-wrapped heads (joined); the 4 section-intro lines and the preamble moved or were reworded; [PLAN-LINT]'s own row status now says steps 1-3 done pending merge.

## 6. Checks run and verdicts

| check | verdict |
|---|---|
| `make test-plan-lint` (the new section) | rc 0, `checks passed: 2`, `checks failed: 0`; no `*** [...test-X] Error` line (`build/pl/pl.log`) |
| same section with `[OPT-C]` retagged `STATE:completed` in the working copy | rc 2, `make: *** [Makefile:1531: test-plan-lint] Error 1`, PL04 named (red proven; file restored) |
| `scripts/plan_lint.sh --selftest` | 32 plants, 17 of 17 rules covered, 0 failures |
| `make test-spec-history` (the closest section, and the one that scans the tree for citations) | rc 0, `checks passed: 145`, `checks failed: 0` |
| `make strict` (Makefile wiring) | rc 0, "whole tree compiles clean with -Werror -Wshadow" |
| `make -n test` | includes `test-plan-lint`; `TEST_SECTIONS` count +1 |
| (ID, STATE) identity | section 4 |
| token-level content fidelity old -> new | section 1 (13 expected exceptions) |
| the hook, four staged-content cases and timing | section 3 |
| full `make test` | NOT run (no C; the brief said not needed) |

## 7. Findings against the brief's premises and against my own first draft

1. SR-8 was built by D67 (section 5).
2. FORM-CHAR2's archive drops WAF744 (section 5).
3. PL14 first went GREEN on a tree full of hits: I wrote the pattern with `(?:` and passed it to `git grep -E`, which rejects it and prints nothing; the first run said 0 violations. Caught by cross-checking `git grep` by hand. Fixed with an ERE pattern, a hard failure on any grep rc other than 0/1, and a scanner self-test over a planted file (the rule's plant bypasses the scanner, so it alone would not have caught this). K35, again.
4. My first PL04 fired on any head containing "archived to" / "HOLD" in prose, mislabelling old-format rows; it now keys on the state word only.
5. plclean's report says no line-number citation remains tree-wide; `plan_completed.md:<line>` citations (13 across 10 files) do remain. I scoped PL14 to `plan.md:<line>` on purpose: plan_completed.md is append-only, so its line numbers do not rot. Say so if you want them converted anyway (they sit in frozen reports).
6. P15 lists 17 `[ID]` references that resolve nowhere (OS-3, TS-4, EMIT-SET, DD-5, VM-READABLE, K50-HARVEST ... are rows plclean merged into survivors; M4.0, DD-11.6, DEC-STAMPS, OPT-OFSK, SABANCHOR, GIVEUP-DIFF, START-LANDING-EXC, ART-HYB-COUNTED, ART-LAZY-FRAMELESS are mentions of ids that never had, or no longer have, a row). For a decision, not fixed.
7. No `tests/mech` row was added (S-ids are the manager's to allocate; the brief gave no range). The self-test is the detection proof; PL17's floor and PL15's direction would be the first mech rows.

## 8. For the merge and after

- Main had not moved when this lane finished. Expect conflicts in docs/dev/plan.md if any lane edits a row first: every row changed shape. The recipe: take THIS branch's plan.md wholesale, then re-apply main's post-branch plan.md hunks as `status` (and `next:`) edits on the row they name. The converter (build/pl in the worktree, gitignored) is not committed; ask for a re-run if main's plan.md changes a lot.
- Install the gate after merge: `make hooks HOOKS=pre-commit`. Run `scripts/plan_lint.sh --stale` at wake.
- A lane that edits plan.md now edits `status (date):` in place and keeps its charter to 6 lines; the linter says exactly which line is wrong, with the row id.
- docs/dev/CLAUDE.md, scripts/CLAUDE.md, tests/CLAUDE.md, tests/plan_lint/CLAUDE.md, docs/testing.md ("Plan lint", and the hooks paragraph) and docs/dev/lanes/CLAUDE.md are updated in the branch. The root CLAUDE.md's Build & test block does not yet mention `HOOKS=` (manager-owned file).
