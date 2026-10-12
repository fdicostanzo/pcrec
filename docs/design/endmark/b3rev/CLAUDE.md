# docs/design/endmark/b3rev/ — B3 revision 2's instruments and raw results

Lane b3rev (2026-10-12): the evidence behind `../../endmark.md` §R (B3, the
match-end mark on rev-end, tagged only where the artifact can tie). Nothing here
is built or run by `make`. Run the Python with `python3 -I` and
`PYTHONDONTWRITEBYTECODE=1`; set `TMPDIR` inside the worktree. Report:
`docs/dev/lanes/b3rev_report.md`.

- `b3rev_probe.c` — the machine probe. Links `build/libpcrec.a` plus a
  probe-local copy of `src/opt/scanedge.c` whose `acc_of` reads accept VALUES
  (the S3 fix), renamed so both passes link side by side (build lines in its
  header). Per row it reports, from pcrec's own builds: today's reverse,
  forward and anchored machines (minimized and after scan-edge); the untagged
  lowered machines (`X(?:\n)?\z`, reverse from the text, forward/anchored from
  the `\G`-patched NFA); the TAGGED reverse machine (Moore product of
  `X\z` x `X\n\z` with per-(state, context atom) distance sets, the absent atom
  included; rebuilt as a `Dfa` and run through both scan-edge passes); the tie
  fact (pairs, class-dependent, absent-atom); the tagged forward/anchored
  machines (Moore over the unminimized machine with each END view's winning
  distance from a priority closure over pcrec's NFA); and `mark_prio` over the
  unpruned anchored machine (class, cost). Its controls are listed in the header.
  `B3REV_DEBUG=1` prints build failures.
- `b3rev.py` — the driver: `census` (the 266 rev-end `$`/`\Z` artifacts, the
  form table F0-F4, controls C1-C13 against the CLI-emitted C, sizes),
  `sweep` (C2's N-sweep), `refusal` (C3's refusal-set compare on plain and the
  emit_sweep `lowsize`/`lowboth` reference builds, which it builds into `$OUT`).
  Its `rw` is census/cost.py's path-final scanner with `\z` as a second kind
  (an unmarked arm, d = 0, S5). Run line in its header.
- `results/` — `census.txt` + `census.json` (per artifact: probe row, emitted
  states, form row), `sweep.txt` + `sweep.json`, `refusal.txt` + `refusal.json`.
- `timing/` — the clock (sub-lane of b3rev): [REVEND-WALK-FORM]'s arms T/A/R/V/S/
  U/P/W/B/Q and D164 add. 4's lowered tie finishers; own CLAUDE.md, raw TSVs and
  `results/report.txt`.
