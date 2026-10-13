# plclean — [PLAN-LINT] step 2: the plan.md cleanup (2026-10-12, session 111, lane plclean, sonnet)

Docs only: no C, no Makefile change. Branch `lane/plclean` from main `6112d16a6`, ten commits (eight numbered cleanup commits, one wedge repair, and the PLAN-LINT/report/CLAUDE.md commit). Input: `docs/dev/reviews/plan_triage_2026-10-12.md` (the triage), Frank's session-111 rulings (quoted in the brief). Item (8) of the triage's suggested order, the linter, is step 3 and is NOT done here.

## 1. Before and after

| | before (`6112d16a6`) | after |
|---|---:|---:|
| `docs/dev/plan.md` rows (anchored `- [ID]`, template excluded) | 262 | **165** |
| `docs/dev/plan.md` lines | 1,353 | **724** |
| `docs/dev/plan.md` bytes | 478,969 | **270,716** |
| `docs/dev/plan_completed.md` lines / bytes | 5,096 / 932,477 | 5,604 / 1,094,043 |
| lines over 1,000 chars | 129 | 100 |
| rows over 5 KB / over 4 KB | 17 / 22 | 0 / 6 |
| rows by state | not-started 158, started 19, completed 11, done 7, deferred 4, blocked 1, stubs/colon-less ~60 | not-started 143, started 17, deferred 4, blocked 1 |
| `STATE:completed`/`done` rows resident | 18 | 0 (`grep -c STATE:completed` finds 2 lines of Policy recipe text) |
| rows with two homes (duplicate ids) | 26 | 0 |

Row ledger (262 - 99 + 2 = 165): 60 deleted without copying (34 JUNK rows = 33 archive stubs/lead-ins + the live note row [BENCH-ASKS-PENDING] whose text IS archived; 26 index-block copies), 26 archived to plan_completed.md, 13 merged or superseded into survivors (full text kept), +2 rows filed from the dissolved shelf. Every one of the 48 rows whose text changed is an intended edit (checked by comparing every surviving row against the base, whitespace-normalised: 117 unchanged, 48 changed, all in section 3).

## 2. Per suggested-order item: what moved where

Commits are `plan.md cleanup N/8` on the branch; run `git log --oneline main..lane/plclean`.

1. **Delete junk (commit 1/8).** 29 archive stubs, the [DD-13] five-id stub, the two reflowed [OPT-HYB-RESEED-FORM]/[OPT-VEDGE] stubs, the [STD1] bullet (all full rows verified present in plan_completed.md before deletion). The 30-entry duplicate index block under [OPTLOOP]: 26 copies deleted; 4 real rows hiding in it kept and relocated ([MEMFN-ENTRYSINK], [MEMFN-CI-ASCII], [MEMFN-RTDISPATCH] under [MEMFN]; [BREF-FOLD-ONCE] to Boonies); the two copies that were NEWER than their full row were merged first ([OPT-SIMD]: RQ-3/RQ-2 merged; [OPT-VMLIT]: "largely delivered as [OPT-LITSCAN] S2a", which is the "reconcile" the triage asked for). 30 free-text blocks (D125 banner, Lane structure, Development order, Next: M4, M4 and M6 sections, the two design notes, the POSITIONING NOTE, the Optimization-waves motto, the Process-mechanization retrospective, the CLS-TREE orphan paragraph, the small-debt shelf bullets, the code-review "guided tour" section, ...) copied **verbatim** to a new "Retired free text, 2026-10-12" section of plan_completed.md (nothing was only deleted; the positioning note lives there rather than in APPROACH.md, which I did not touch). The "guided tour" is dropped with no row, as ruled.
2. **Archive completed (commit 2/8).** 23 rows to a "Completed 2026-10-12" section of plan_completed.md, children included ([SIZE-CAP-FLAG]'s four bullets): [SEL-SIZE], [REL-0.2], [FLAG-ACCESS], [REVEND-WALK-FORM], [CAND-PATH-READS], [GUIDE-OPT-LEVEL], [REQ-HANDOFF-L1], [CLS-TREE], the seven `STATE:done` rows ([TT-MECHPAR], [AXES-DENY-MASK], [SIZE-CAP-FLAG], [DEC-VAR-ATTRIB], [DEC-FALLBACK], [DEC-COLLAPSE-WASTE], [START-TABLE]; retagged `completed`, closure note says so), [OPT-GAPREPORT], [START-D2], and Frank's rulings: [DD-6], [DD-2] (completed), [OS-2] (answered by M5's architecture), [TT-13], [TT-15], [MECH-3] (superseded). Carry-over sentences moved into [IFACE-PUSH] (FLAG-ACCESS residue), [OPT-REVEND] (the walk-form answer) and [OPTLOOP] (the gap-report duty).
3. **Merge duplicates, retire superseded (commit 3/8).** Absorbed in full into the survivor: [VM-READABLE] into [READ-BYTES] (one emitted-readability row, one abi event; the `!= 123` vs `'{'` conflict noted), [EMIT-SET] into [EMIT-ENTRIES] (B0 of [COMPOUND] noted), [K50-HARVEST] into [K50-DD12AI-MANIFEST], [OS-3] into [M3.0], [TS-4] into [DD-10], [DD-5] into [FREESTANDING], [CLS-FOLD-WAF744] into [FORM-CHAR2] (and its status contradiction with the closed [CLS-TREE] fixed), [OPT-HYB-RESEED-POLICY] into [START-DENSE] (its disarm rule carried). Superseded, full text in a "Superseded and merged rows" section of plan_completed.md with a pointer in the survivor: [OS-4] and [OPT-ATTEMPT-SPLIT] (into [MATCH-SPLIT]), [FEAT-VAR] (into [VAR]), [GUIDE-1], [DEC-ROUTE].
4. **Wedges (commits 4/8 and 4b/8).** [M4-CALLOUTS] is whole again ([MATCH-EVENTS] had been inserted after its first line); [SIMD-SIZE-PARITY] moved below [MEMFN]'s children; the [DD-13] stub wedge disappeared with the stub. **A fourth wedge the triage did not list: [ART-MGR] had been inserted after [V-E]'s long first line, stranding [V-E]'s 58 wrapped lines (the CROSS-PATTERN FINDER body) under [ART-MGR]; repaired.**
5. **STALE rows (commits 4/8, 5/8, 7/8).** See section 3 for each. Archived delivered: [OPT-FIRSTSET], [WORD-FOLD], [SR-6] (converted to a "Convention: module handlers" section at the end of `src/parse/CLAUDE.md`). Status stacks replaced by charter + one dated status, old text kept verbatim in a "Row history moved out of live plan.md rows" section of plan_completed.md: [OPTLOOP], [MEMFN], [OPT-LITSCAN], [OPT-REVEND], [NULLABLE-ANCH], [XARCH], [OPT-VMSEED]. Smaller text fixes: [UTF-PAT], [UTF-RW], [UCP], [SEL-COST], [LIB], [M7.0], [V-H], [DOC-BM], [OPT-SETS], [START-DENSE] (gate now open), [ART-CTX-TRIO] (STATE tag added), [M4-CALLOUTS], [M4-SUBST].
6. **Split rows over 5 KB (commit 6/8).** Nine rows ([VAR], [UCP], [V-E], [ENG-TACTICS], [K50-DD12AI-MANIFEST], [OPT-SIMD], [OPT-A], [ENG-PGO], [OPT-VMLIT]) now carry a compact charter + dated status + pointer; the verbatim row is `docs/design/plan_row_bodies/<ID>.md` (new directory with its own CLAUDE.md; `docs/design/CLAUDE.md` indexes it). The other 8 of the triage's 17 were archived or restated above ([DEC-FALLBACK], [CLS-TREE], [START-TABLE], [REQ-HANDOFF-L1], [OPT-FIRSTSET], [OPT-LITSCAN], [MEMFN], [OPTLOOP]/[OPT-REVEND] heads). Largest remaining row: 4,678 chars.
7. **Re-section (commit 7/8).** The 16 historical headings are gone; the file is Policy, Active (started/blocked; [OPTLOOP] and [MEMFN] carry their children), Candidates ([OPTLOOP], D137; 43 rows), Backlog (65), Boonies (31), Deferred (4). The step-state header became the Policy section (no hard-coded counts, completed rows leave the file, cite by `[ID]`, grep recipes anchored). The D18 and D19 section intros are folded into [OS-0] and [DD-10]; the stray O-78 witness bullet is folded into [OPT-LITSCAN]. No row text changed in this commit except indentation.
8. **Line cites (commit 8/8).** 109 `plan.md:<line>` citations in 36 files converted to `plan.md [ID]` or `plan_completed.md [ID]` (ranges to `[A]..[B]`); none remains tree-wide outside the triage report (which quotes them as the thing it counts). Method: each line number was resolved against the `plan.md` of the commit that introduced the citation (`git log -S`), then cross-checked against the `[ID]` the surrounding text names. 76 of 109 agreed with an ID named in the text; the rest were derived from the historical file, and 12 were hand-corrected where text and history disagreed ([LIB]/[V-E] in cli_record/iface_digest/speclim, [POSS-CTX-TABLE] in memfn customers.md, [DD-1]/[DD-13]/[REL-META]/[DD-14] in spec_survey, [OS-4]/[OPT-ENDWIN] in map_C3.tsv, [DD-14.G] in r44, [START-DENSE] in critic_fit). The two "plan.md:9" cites to the old template line now say "plan.md's step-state header". Reports under `docs/dev/lanes/` and `docs/dev/reviews/` are "never edited afterwards" by house rule; the brief overrode that for these one-token edits.

## 3. Frank's rulings applied, and the STALE rows

| ruling / row | done |
|---|---|
| [DD-6], [DD-2] archive (completed) | archived with closure notes |
| [OS-2] close, answered by M5's architecture | archived |
| [TT-13], [TT-15], [MECH-3] close, superseded | archived |
| [LIB] keep, Boonies, strike stale "BLOCKS on [DD-13b]" | struck in place (DD-13b completed 2026-08-29), row is under Boonies |
| [M4-CALLOUTS] keep, restate trigger, repair wedge | done (M4 shipped 2026-08-18; wedge repaired) |
| [M4-SUBST] keep, restate as replace_design.md's implementation row | done; note that variables_roadmap.md gates [VAR] M9 on THIS row's core |
| [M7.0] rewrite to the testdata-import residue | done (fuzzing is done, freestanding is [FREESTANDING]) |
| [OPT-VMSEED] close as delivered unless a stated remainder exists | **A stated remainder exists** (planaudit 2026-10-10: "this row's own framing ... NOT shown built; its D77 census/trigger stands"), so the row is restated to only that remainder (a start-position seed for VM runs with NO DFA in front), old stack in plan_completed.md. Not closed. |
| code-review "guided tour" | dropped, no row |

## 4. Rows left for a judgement (listed, not guessed)

- **[BENCH-UTF8]**: STALE (build done; growth families (g)-(k) "not verifiable from this repo"). The triage says archive the build part and ask the bench dev; I cannot ask, and the charter text is the commitment, so the row is unchanged. Ask pcrecdev2 for (g)-(k), or drop them.
- **[SR-8]**: the triage offers "close as superseded by D55/D59 or rewrite the trigger"; two options, no basis to choose. Unchanged.
- **[DOC-BM]**: the struck-through historical fragment is removed (kept in plan_completed.md history); its constraint ("must exist BEFORE section 7.1's five escape rows land") is unverified, as the triage said. Unchanged beyond that.
- **[FORM-CHAR2] + [CLS-FOLD-WAF744]**: merged; the new status sentence is derived from the triage's account of D138 Q1 ("measure first - the fold default stays pending FORM-CHAR2"). Frank should confirm the merged row says what he ruled.
- **[GUARD-MODULE-SWAP], [PC4-MISSING-SHAPES]**: the two undated "owed, unruled" shelf bullets were filed as rows (undated, unowned) rather than deleted, because the triage allowed either and deleting loses the idea. Delete if Frank agrees they are dead.
- **[BENCH-ASKS-PENDING]**: deleted as a relay note, text archived. Any still-open ask must be re-issued through pcrec-bench `inbox_from_pcrec.md` by the manager (I may not write there).
- **[MEMFN]**: the new status line says R-14/R-15/R-16 are BUILT, taken from the lane reports (r14b, r14p, r15b, r16b); whether they have merged is the kit manager's to state. The old status stack went to plan_completed.md, not to `memfn/docs/journal.md` (that file is the kit session's).
- **[NULLABLE-ANCH]**: "F1 closed by [DEC-VAR-ATTRIB]" is inferred from decattr_report.md (T2 `var-nullable` deleted); the original target (evil-alt-nested / trim-nested-star) is still not re-measured, K97 open.
- Classified by adjacency, not by text: [ENG-TDFA] (Candidates), [SIMD-SIZE-PARITY] (Backlog), [OPT-VMSEED] (Candidates), [ART-CTX-TRIO] (Candidates).
- Triage items I did not do because they are LIVE-class polish: [OPT-3-RUNEND] "update with O-82 A1 subject", [ARTREV] "mark waiting", [PRIOR-COST-UNIFY] "move SHARED VOCABULARY to its design note", [XART-TABLES] cross-link to [V-E], [SIMD-META] "merge into [OPT-SIMD]", [EMIT-ALIGN] "close as not triggered".
- Not converted to the triage's section 7 per-field format (`filed:` / `status:` / `next:` lines): the 165 rows keep the head-parenthetical style; the Policy section says so. That is step 3's ratchet.

## 5. Lint debt for step 3 (the baseline the ratchet should start from)

Measured on the cleaned file: rows matching the triage's P2 head regex (title 1-100 chars after the em dash): 13 of 165; no em-dash separator in the first 400 chars: 17; bold blob after STATE: 1; rows over 1,500 chars: 85 (over 4,000: 6); lines over 1,000 chars: 100; hard-wrapped multi-line rows: 21; rows with no ISO date: 8. Dotted ids whose parent row is not in plan.md (P6): M3.0, M3.1, M7.0 (milestone ids; the rule should whitelist `Mx.y`), FINDINGS.B4, DD-13b.W1.3.1, DD-13b.W1.4, DD-11.5, SPEC-1.11 (parents archived). Not measured: `[ID]` references resolving nowhere (P15, the triage counted 34). The Policy section contains a code-block template row `[Mx.y]` that the linter must skip, and two `STATE:completed` mentions that are recipe text.

## 6. Checks run and verdicts

- `make test-spec-history` (the only check that scans the tree for line-number citations; `gnutimeout 900`, background): **checks passed: 145, checks failed: 0, rc=0** (`build/plclean/spec_history.log`, uncommitted scratch). Verdict read from make's rc and the `checks failed:` line; no `*** [...test-X] Error` line.
- No other check reads plan.md or plan_completed.md as data (grep of Makefile, scripts, tests: every hit is a comment citing a row by id). The directory-structure edits touch no check input. `make` / `make strict` / full `make test` were NOT run (no C or Makefile change, per the brief); the manager's merge battery is the owner of the full suite.
- Identity checks I ran by script: id-set diff base vs tip (only the intended removals and the two filed rows), no duplicate ids, every row placed exactly once in the re-section, parentheses balanced in every rewritten row, base-vs-tip text comparison of all surviving rows (section 1).

## 7. For the merge

Main's `plan.md` moves under this lane (cpb4 was rewriting [COMPOUND], other lanes touch their own rows). Expect conflicts in `docs/dev/plan.md` and `docs/dev/plan_completed.md` (append-only, so take both sides). The resolution recipe that preserves a concurrent row edit: take main's row text for the id, then re-apply this lane's placement (the row's section is in the Active/Candidates/Backlog/Boonies/Deferred table in section 2 item 7; ids are unique across the file now). The archive sections added to plan_completed.md are at its end, headed `## Retired free text, 2026-10-12`, `## Completed 2026-10-12`, `## Superseded and merged rows, 2026-10-12`, and `## Row history moved out of live plan.md rows, 2026-10-12` (the last also holds the DOC-BM fragment).
