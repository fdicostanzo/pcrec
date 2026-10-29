# emitbidiland report -- landing of lane/emitbidi ([EMIT-BIDI])

- Merge: 7234c2e86 (`--no-ff` of lane/emitbidi 54317eda8, no conflicts, not even plan.md).
- make -j16 and make strict on the merged tree: clean.
- (B) FILEPIN re-pin: tests/codegen/run_recursion_identity.sh now pins 7234c2e86 (commit f6c230e5f).
  Gate run (build/emitbidiland/ident.log, ~25 min): all (B) checks and the linkage/elision/MEMFN/ART-SIZE checks PASS;
  rc=1 from 8 FAILs, ALL in comparison (A) (pre-module pin ac4917d): the bref-rename band (328 vs census 411)
  and "167 / 381 / 167 / 111 patterns emit a different program region" on default / vm / noprefilter / nocaptures.
  (A) is the known red left pending a ruling by lane recpin (recpin_report.md: 78/126/78/54 differing, band 366 vs 411 on 10-23);
  the counts have grown since (abi 84 iterators etc. landed in between). Not attributed to emitbidi (the patterns named are
  backref/alternation program regions, not comments); NOT re-run on the pre-merge commit to prove it. Manager to confirm.
- make test-codegen on the merged tree (build/emitbidiland/codegen.log): `run_group: 19/19 scripts passed`, rc=0.
- plan: [EMIT-BIDI] moved to plan_completed.md (completed line names merge, abi 86, ASCII-only promise, guard, kit follow-up); plan_lint 0 violations.
- Ledger class: MAJOR (abi event; emitted text moves on every -fcomments artifact). Counter major 27 -> 28.
- D177 trigger: no NEW trigger fired; rows 4 and 5 were already FIRED and the next window is still pending; this adds to the pending run.
- Lanes index: docs/dev/lanes/NOTES.md lists emitbidi, emitbidifix, emitbidi2.
- Pushed: 0b740889c (pre-push light gates green).
- Prune: `scripts/wtprune --apply emitbidi` KEPT the worktree: "uncommitted changes" = only docs/dev/artifact_size_log.tsv
  (test-run output, same file dirty in main). Not forced.
