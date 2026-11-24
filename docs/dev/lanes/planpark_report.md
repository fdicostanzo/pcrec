# planpark report

STATE: done

## Summary
Owner ruling 2026-11-24 "stale-rows-park: agree" applied to docs/dev/plan.md and docs/dev/plan_completed.md only. `make -s test-plan-lint`: 419 rows, 0 violations, selftest 45 plants 0 failures.

## Parked
[XARCH-DEV], [MEASURE-SET], [VMREC], [FINDALL-NEXT]: STATE:started to STATE:deferred, each moved with its children to the end of Deferred. Each carries a "parked 2026-11-24 (owner, stale-rows-park): no activity since <status date>" status that compresses the old status (the old line is in git history), and a `trigger:`. The plan linter forbids next: beside trigger:, so each old `next:` text was folded into the trigger after "then:" (the [VMREC] one lightly shortened to fit 300 chars). Triggers: XARCH-DEV the next non-x86 box session or the kit's Mac move; MEASURE-SET a second measured machine, the install-time tool's go, or a kit priced choice needing its own set; VMREC a VM emitter change needing records or the stream roadmap reaching A-REC; FINDALL-NEXT the kit's `st` delivery.

## Housekeeping
- [UPROP-MORE]: its only remaining step was the not-started size follow-up, which [DATA-PLAN] steps A and B already name. Closed verbatim into plan_completed.md (section Completed 2026-11-24). [DATA-PLAN] stays blocked, but its `waits:` now reads owner go for lane A (the old wait on [UPROP-MORE] is gone) and its status says so.
- [MEMFN-RTDISPATCH]: NOT mis-pasted. It has no `next:` line, only a `trigger:` (more than one architecture selected for runtime support plus a hot-loop SIMD form). The "re-check critic round, then build stage 2" line the brief saw is [VLOOKBEHIND]'s own. No commit, journal entry or memfn journal entry shows any work on it. Left unchanged. Possibly worth the manager's look: [XARCH-DEV]'s ruled end state (variants plus a once-per-process CPU dispatch) overlaps this trigger.
- [DOC-INDEX]: landed part archived as [DOC-INDEX-T1] (STATE:done, old status kept) in plan_completed.md; [DOC-INDEX] stays started with a corrected status (open: T2, [CITE-FORMS]) and its `next:` unchanged.

## STATE AT HANDOFF
Committed on lane/planpark. Rulings file read: empty. Owed: nothing.
