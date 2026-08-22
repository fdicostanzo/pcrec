# docs/design/atomic_groups_measurements/out — archived probe output

Verbatim output of `../probes/`. **Every file here is written by
`../probes/archive.sh`**, so the provenance header cannot drift between them:
probe path and args, the commit the probe was last changed at, the commit and
branch the run was made from, whether the working tree was clean at run time,
the date, and the python3, libpcre2 and gcc versions. Same intent as
`scripts/measure.sh` / `docs/measurements/` (D35), scoped to this lane.

**Evidence for the [M6.4.1] panel, never an oracle.** No check in `make test`
reads anything here; re-run the probe to re-measure.

**EVERY HEADER HERE SAYS `working tree at run time: DIRTY`, and the header
itself says why.** The archiver stamps `git status --porcelain` and then writes
its output INTO the tree it just stamped, so the one dirty entry listed under
each stamp is that output file: `?? docs/design/atomic_groups_measurements/out/
<thisfile>`. Read the listed entries, not the word. A header whose dirt list
contains anything OTHER than its own output file is reporting a real
uncommitted change and the number should be re-taken. (The same is structurally
true of `../../assertions_measurements/out/`; it is written down here because a
panel reading `DIRTY` on eight files in a row deserves the explanation in the
directory rather than in a commit message.)

## Files

- `atomic_semantics.txt` — `probe_atomic_semantics.py`, 95 cells. Headline:
  **13 of 95 diverge** between libpcre2 10.46 and python3 3.14 — 8 are `\K`,
  `\G` or a scoped `(?i)` python cannot express or parse, 2 are **U9**, and the
  remaining 3 were the probe's own group-padding defect, now fixed. Also the
  source of §6's whole table: `(?>)` is legal and matches `(0,0)`; `(?>a*?)b`
  on `"aaab"` is `(3,4)`; `(?>a|ab)c|abcd` on `"abcd"` is `(0,4)` where the
  uncut twin is `(0,3)`.
- `uncut_superset.txt` — `probe_uncut_superset.py`, 1,260 patterns × 14
  subjects = **17,640 cells**, 8,237 of them with both spellings matching.
  Headline: R1 (sound rejection) **0 violations**, R2 (start is a lower bound)
  **0**, **R3a (end is an upper bound) 122 — REFUTED**, R3b (harmless
  overshoot) 133, and **180 cells where the emitted search loop's
  `attempt_position++` retry is actually reached**.
- `ceiling_shape.txt` — `probe_ceiling_shape.sh`. Headline: the DEFAULT arm
  emits `window_end = (size_t)window[0][1] < subject_length ? … : …` at two
  sites (the entry and the retry recompute) and stamps
  `RX_VM_PRUNE_CEILING "prefilter-window"`; `-fno-prefilter` and `--engine=vm`
  both emit `window_end = subject_length` and stamp `"subject-end"`;
  `--no-captures` emits no `window_end` at all.
- `cut_trail_proto.txt` — `probe_cut_trail.py` over `cut_proto.c`. Headline:
  **14 rows, 0 disagreeing with libpcre2, 9 NON-VACUOUS.** The two rows the
  no-trail-rewind question turns on are in it by name — `(?>(a)|ab)` on `"ab"`
  (group 1 RETAINED across the cut) and `((?>(a)|ab))c|(abc)` on `"abc"`
  (groups 1 and 2 UNDONE by an outer frame below the mark, group 3 set).
- `free_discharge.txt` — `probe_free_discharge.py`. Headline: **1,764 patterns
  × 16 subjects = 28,224 cells; 532 with a POSITIVE possessify verdict; 0
  violations.** 16 of the positive-verdict patterns are U9-shaped (so the
  subtraction had something to subtract) and contributed 0. 834 of the 1,232
  negative-verdict patterns never changed their answer — declined rescues. All
  four controls behaved as required.
- `possessify_under_cut.txt` — `probe_possessify_under_cut.py`. Headline:
  **48,000 cells, 0 violations** across all four quantifier positions relative
  to the cut (positive verdicts 275 / 75 / 72 / 220), with a **non-vacuity
  counter of 202**.
- `premises.txt` — `probe_premises.sh`. Headline: `(?>a)` refuses at offset 0;
  `a*+`/`a++`/`a?+` at offset 2, `a{2}+` at 4, `a{,2}+b` at 5, `a{1,2}+` at 6 —
  the `+`'s own offset in every case. **`a{,2}b` COMPILES and matches `"aab"` at
  `0 3`** (the quantifier reading, agreeing with libpcre2 10.46 and python
  3.14). `a*?+` and `a**` refuse with `multiple quantifiers on the same item`;
  `a*++` refuses with the possessive message TODAY and will refuse with the
  multiple-quantifiers one after the module lands. A `--no-captures` DFA
  artifact carries **0** `RX_ENGINE` defines; the default artifact carries
  `RX_ENGINE "vm"` and `RX_ENGINE_WHY "capture group at pattern offset 0"`.
- `rk_alarm.txt` — `probe_rk_alarm.sh`. Headline: **28 files offered, 28
  compiled clean, 0 `-Wswitch` diagnostics** naming a new `RegKind`. A fifth
  row kind's incompleteness is invisible to the compiler, which is why §7.4
  makes `registry_check.c` supply the check instead.
- `wswitch_alarm_rerun.txt` — the RE-RUN of
  `../../assertions_measurements/probes/probe_wswitch_alarm.sh`, not a rebuild.
  Headline: a new `AKind` produces **15 `-Wswitch` diagnostics across 6 files**,
  including `src/opt/revdet.c:93` and `:185` — the two sites an `A_ATOMIC`
  decline must land at (§6.5). Header restored and verified.

Maintenance: update this file when outputs are added/removed.
