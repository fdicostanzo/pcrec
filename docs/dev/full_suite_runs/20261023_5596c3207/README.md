# Full-suite run 20261023_5596c3207 (frozen 5596c3207): triage

The run was RED (stages axes and mech; the others green or not red). Counters in
`../../full_suite_ledger.md` do NOT reset. Retained logs: `build/full_suite/20261023_5596c3207/`
(gitignored, main tree only).

- `triage_axes.md` - axes stage. Four findings, no answer mismatch: five stale give-up allowance keys
  (fixed by lane fsfix, [AXES-GIVEUP-KEYS]) and 2 LOST under `-fcomments` (bidi marks echoed into
  emitted C, filed as [EMIT-BIDI], not fixed).
- `triage_mech.md` - mech stage. 8 unexpected rows in groups A (stale witnesses), B (stale plants),
  C (stale expectation), D (undetected, needing a decision). Dispositions: lane fsfix report.

Both files are the triage agents' verbatim output (tri-axes, tri-mech).
