# lanecheck report ([LANECHECK] v1)

## Summary
`scripts/lanecheck` lets an agent check its own deliverable against the brief's
DELIVER block and prints numbered prose issues or `lanecheck: DONE rc=0`; only a
pass writes `NAME.done`. `scripts/lanewatch` is the zero-model-call manager side:
one line per missing, stale or hand-written marker, misses logged. Self-test
`scripts/tests/lanecheck.test`: 35 passed, 0 failed (run directly, about 15 s).
Not touched: the critic skill (the manager adopts it), `make test`.

## Format
The DELIVER block is written to `docs/dev/lanes/NAME_deliver.txt` (or any path
via `--deliver FILE`). Fields, one per line or `;`-separated:
`report: PATH`, `sections: A; B; ..` (## or ### headings, case-insensitive),
`nonempty: all|LIST`, `cites: RE in X -> Y` (may repeat), `commit: yes|no`,
`files:` and `dirty-ok:` (extra committed paths, paths allowed dirty),
`owed: none|KEY ..`. The grammar lives in the header of `scripts/lanecheck`;
BRIEF_TEMPLATE.md carries a DELIVER field and BOILERPLATE.md one paragraph
("Before ending: scripts/lanecheck"). This lane's own block is
`docs/dev/lanes/lanecheck_deliver.txt`.

## Tools
- `scripts/lanecheck [--deliver FILE] [--dir D] [NAME]` (python3). Exit 0 pass,
  1 issues, 2 stopped, 64 usage, 65 bad DELIVER file. Marker `NAME.done` in
  `build/lanecheck/` (gitignored) for the lane layout, else beside the DELIVER
  file: report and DELIVER sha256, commit, owed keys, UTC time, and a seal.
- `scripts/lanewatch [--dir D] NAME...` (bash). Kinds: missing, stale (report or
  DELIVER changed after the marker), hand-written (seal mismatch). Appends to
  `worktrees/.mgr/lanecheck_misses.log` as `UTC name kind`, skipping a repeat of
  the last kind for that name so the file counts misses, not polls.
- A report with `STATE: stopped` makes lanecheck write `NAME.stopped` (rc 2) and
  lanewatch show it without counting a miss.
- Docs: scripts/CLAUDE.md (one line, kept under its 4 KB cap), scripts/NOTES.md,
  scripts/tests/CLAUDE.md, scripts/Makefile (lanewatch dependency).

## Self-test results
`TMPDIR=build/tmp bash scripts/tests/lanecheck.test`: 35 passed, 0 failed. Cases:
clean pass and its marker; the one-line DELIVER form; missing section, empty
section, uncited finding id, owed text missing, uncommitted change, dirty tree
(and the `dirty-ok` twin), untracked report, missing report; owed key present and
absent in a scratch queue; lanewatch missing, hand-written, edited, stale,
restored, stopped; the no-git critic form; exit codes 64 and 65. Plants: an
always-passing lanecheck (issue list discarded) writes a marker for a report
without Findings, which the missing-section case catches; a lanewatch without its
seal check accepts the forged marker, which the hand-written case catches.
`make check_claudemd_size --all`: 331 files within limits.

## Limits
- Form only. Whether a section's content is good or true is the reader's job; a
  non-empty body is any non-blank line that is not a bare TODO/TBD/XXX.
- Dropped as judgement a script cannot make: none from the brief's list, but
  `owed` is a text heuristic (STATE AT HANDOFF must contain `OWED ... none`, or
  name each key) and `cites` supports one rule form only.
- The seal is tamper-evidence for a lazy hand-written marker, not security: it
  is a hash anyone reading the script can recompute. The marker also does not
  prove the agent ran lanecheck last, only that the report matched at that time.
- A wrong `commit: yes` in an agent with no git tree is an issue, not a skip.
- The critic skill section 5 is not edited; its output files fit with
  `commit: no`, a DELIVER file beside the output, and `--deliver`.
- The test is not in `make test` (D48); not yet run via `make -C scripts test`.

## STATE AT HANDOFF
OWED: none. Rulings file `lanecheck_rulings.md` read before this report: no
entries (`(none yet)`). Branch lane/lanecheck, all committed. Next, for the
manager: adopt a DELIVER block in the critic skill and in briefs; decide whether
lanewatch joins an existing poller (it is deliberately standalone).
