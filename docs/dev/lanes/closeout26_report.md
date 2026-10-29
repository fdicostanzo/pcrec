# closeout26 report: Active-row close-out (2026-10-26, lane closeout26, sonnet)

Docs only; commit 83841e2b6 on lane/closeout26. Rulings file read before commit and report: no entries.
Old status/next lines of advanced rows are in plan_completed.md, "Status lines superseded 2026-10-26".

| row | action | evidence |
|---|---|---|
| [BOXQUEUE] | CLOSE | b42c0e8f1; queue runs the box (jobs 622/623/800-*), kit jobs, bench windows 710/720 via [BENCH-RESERVE] 415eade4d |
| [MONITOR-QUEUE] | CLOSE | monwatch 88d274fe3, montest, monci d5f77228e, qw* lanes; first live use job 624 (journal 2026-10-25); [MON-SCRIPT] 82abd6b87 |
| [FLAG-SPELL] | CLOSE | 187608482; jobs 615/617, 622 (main after landings) green 77/77; flag group in run_case_spelling_identity.sh compares (?i)abc vs (?i:ABC) |
| [KNOW-SRC] | CLOSE | K2+K3 168a399c7; census tool (emit_sweep --data); measures kind 813f43ec8 |
| [GATE-RUNS] | ADVANCE | first full run 2026-10-24 (5596c3207) RED, ledger line; fsfix 1de780cb7, EMIT-BIDI 7234c2e86; next = pending 600-main-fullsuite-20261027 (not before 00:05) |
| [UPROP-MORE] | ADVANCE | "first full make test" = job 622 green; remaining D27 author, review, DATA-PLAN size follow-up (none started) |
| [FINDALL-NEXT] | ADVANCE | I0+I1+I4 landed b8c66a739 (abi 84); next = I2 (waits on kit's kit-find) then I3 |
| [DD-11.5] | ADVANCE | Z2 merged aeb381c25 (2026-10-21), post-merge job 125 green; next = timing look + B1 after kit B4 |
| [ENTRY-TABLE] | ADVANCE (next only) | E1 merged 7c0a90479; next was "merge lane/e1" |
| [COMPOUND] | ADVANCE (status) | B4 merged e842fe537 (abi 77), B3 206cf0a0b (abi 78); E0/E0c/E1 landed |
| [TT-JTUNE] | ADVANCE (status) | ledger 71 rows/7 shapes, last 2026-10-18; my rough read of rule (b): best median 8,2 ~902 s vs baseline ~958 s (-6%) is at the noise bar, default unchanged; not a claim the bar is met or missed |
| [M4-SUBST] | ADVANCE, close awaits Frank | landed 9ae59f5d4; follow-up rows all exist ([SUBST-SPEED], [SUBST-CLEANUP], [SUBST-NAMECHK], [SUBST-INPLACE], [CASE-COMPAT]); NOT closed because charter (2) STREAMING mode with stamped holdback is neither built nor filed as a row |
| [INLINE-C] | KEEP | filed today, accurate |
| [MEASURE-SET], [REGIME], [REGIME-CORPUS] | KEEP | status 10-17..10-23 consistent with record |
| [OPTLOOP], [LOSS-REVIEW], [OPT-REVEND], [MATCH-SPLIT], [OPT-LITSCAN], [PRIOR-COST-UNIFY], [ARTREV], [NULLABLE-ANCH], [U8-PICK], [ENG-TACTICS], [UCP], [VAR], [BENCH-UTF8], [MEMFN] (+children), [OPT-SIMD], [DATA-PLAN] | KEEP, unverified | statuses dated 10-05..10-12 (DATA-PLAN 10-24); no main commit naming them since that contradicts the text, but I did not audit each against its lane reports |

## Needs Frank
- [M4-SUBST]: close it, and is the streaming/holdback mode to be filed as its own row (it has none)?
- [FLAG-SPELL] closed with one unbuilt, unfiled follow-up (req.c run reset on an empty mid-CAT); file or drop.
- [TT-JTUNE]: whether the measured spread justifies the follow-up lane that changes the default.
- [DD-11.5] and [FINDALL-NEXT] I2 wait on the kit (B4; kit-find row): kit status unverified by me.
- [OPT-REVEND] status (10-12, truncated with an ellipsis) predates B3 (206cf0a0b); I left its text since I could not rewrite it without the full lane record.

## Outside Active, noticed (not edited)
Backlog rows [HOOK-GUARDS], [MON-SCRIPT], [SUITE-RESUME], [BENCH-RESERVE] say LANDED yet stay STATE:not-started (their own next: says plan_lint holds Backlog at not-started; they close at "the next plan audit"; plan_completed already holds [EMIT-BIDI] the same way, so a move is due).

## Triggers / gates naming the closed rows
Only [KNOW-SRC]: a refs line in a design row (plan.md "rows [LIST-TABLES], [V-H], [DEBUG-CHECKS], [KNOW-SRC]"), a plain reference, no gate. No row names [BOXQUEUE], [MONITOR-QUEUE] or [FLAG-SPELL] as trigger. Rows gated on [M4-SUBST]'s core landing (now met): [VAR] M9 (variable side of replacement), [M4-CALLOUTS]/[INLINE-C] refs; not edited.
