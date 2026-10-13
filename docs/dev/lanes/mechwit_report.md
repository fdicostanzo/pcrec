# mechwit: nine UNREACHED mech rows re-pointed at default-path witnesses (2026-10-13)

Lane mechwit (sonnet), branch `lane/mechwit` off main 52c2c3917. No `src/`,
`lib/`, `cli/` change, no `docs/spec/` hunk, no abi event. Everything is a
mech row, a test script, or a CLAUDE.md note.

Input: `docs/dev/lanes/s25mech_report.md` (on `lane/s25mech`, commit
67fa98b36), which found nine rows UNREACHED on main because two default-path
optimizations moved their witnesses off the sabotaged site. The sabotaged code
is still live behind `-fno-start-landing` / `-fno-rev-end`; the fix here is to
make each row, and the suite that detects it, reach the site under DEFAULT
flags, so a sabotage is detectable by what a caller gets.

## Verdict

All nine rows now score `DETECTED, unexpected 0, unreached 0` in a solo
`tests/mech/run_sabotage_matrix.sh S###` run at 8c642a941 (S264: also at
f75813555's tree, same sources). Before the fix every one was UNREACHED at
main's tip. A deny-flag witness is used for NO reach probe; the one deny-flag
cell that remains is pre-existing and not a reach witness (the `[PF-DROP/ff]`
collapse cell, below).

## Before: every old probe is UNREACHED at main's tip

I replayed each row's committed (old) `SAB_REACH` command against a
`build/pcrec` built from main 52c2c3917 (the worktree's `src/` is unchanged),
checking its `SAB_REACH_EXPECT`. This is exactly what the runner's reach step
does, and an unreached row's tree is never built, so it is the whole "before"
verdict:

| row | old probe's output at the tip |
|---|---|
| S237, S238 | no `size-cap-retry` (`\p{L}` -e utf8 fits at 588,486 B) |
| S252, S253 | no `size-cap-retry` (`[^\p{C}\p{M}\p{P}]` fits at 715,766 B) |
| S421, S423 | no `pattern too large` under `--size-cap=refuse` (`(\p{Xwd})` fits) |
| S422 | no `VM_PREFILTER_WHY` |
| S264 | no `RX_END_WINDOW "4"` / clamp (`abc$` is `rev-end`) |
| S614 | no `rx_forward_stay` loop (`[^c]{1,3}$` is `rev-end`) |

## Per-row table

"Verdict after" is the row's own solo run. Reach is the runner's
`reach:ok(n/n)`.

| row | old witness | why unreached | new witness (default flags) | reach evidence | verdict before / after |
|---|---|---|---|---|---|
| S237 size-drop-rung-deleted | `\p{L}` -e utf8 | [START-LANDING] drops the reverse machine, so it fits (593 KB) WITH its anchored machine; the drop rung never fires | `\p{L}\p{N}\p{Lu}`, `\p{N}\p{L}\p{Lu}`, `\p{L}\p{N}\p{Ll}` -e utf8 (1.30-1.38 MB with the machine, 0.76-0.84 MB after the drop: 17%+ margin on both sides) | probe asserts `RX_ENGINE_SEL "size-cap-retry"` and `RX_DFA_MATCH "search-filter"`; `reach:ok(2/2)` | UNREACHED / DETECTED, `anchoredmatch:10fail/18pass` |
| S238 size-drop-unstamped | same | same | same | `reach:ok(2/2)` | UNREACHED / DETECTED, `anchoredmatch:10fail/18pass` |
| S252 premul-drop-rung-deleted | `[^\p{C}\p{M}\p{P}]` -e utf8 | on `landing`, fits premultiplied (720 KB) | `[^\p{C}\p{M}\p{P}]xy` -e utf8: 1,441,473 B with the machine, 1,046,700 B after rung 1 (4.7% over the cap, so rung 2 is needed), 458,919 B after rung 2; `RX_START "reverse-pass"` | probe asserts `size-cap-retry`, `DFA_TABLE "indexed"` and the stderr note `dropped the premultiplied DFA transition table`; `reach:ok(3/3)` | UNREACHED / DETECTED, `tunedial:4fail/112pass` |
| S253 premul-drop-note-unstamped | same | same | same | `reach:ok(3/3)` | UNREACHED / DETECTED, `tunedial:4fail/112pass` |
| S421 fast-or-fail-inert | `(\p{Xwd})` -e utf8 | on `landing`, hybrid 370 KB keeps its prefilter | `(\p{Xwd})\b` -e utf8 `--features assertions`: hybrid 1,173,222 B, 17% over the cap | refuses `pattern too large` under `--size-cap=refuse`; `reach:ok(1/1)` | UNREACHED / DETECTED, `resource:4fail/38pass, pfcollapse:1fail/70pass` |
| S422 prefilter-drop-unstamped | same | same | same | probe asserts `RX_VM_PREFILTER_WHY "size cap retry, hybrid `; `reach:ok(1/1)` | UNREACHED / DETECTED, `resource:2fail/40pass, pfcollapse:1fail/70pass` |
| S423 prefilter-drop-not-degrading | same | same | same | `reach:ok(1/1)` | UNREACHED / DETECTED, `resource:2fail/40pass` |
| S264 end-window-one-byte-narrow | `abc$` | [OPT-REVEND] makes it a `rev-end` DFA artifact, which asks no window | `(ab)(c)$` and `([^c]{1,3})$` (capture-bearing, so the VM route; window 4, clamp `search_from = subject_length - 4ULL;`) | probe asserts both stamp and clamp for each pattern; `reach:ok(2/2)` | UNREACHED / DETECTED, `corpus:31fail/56365pass, prechecks:11fail/384pass` |
| S614 r4h-stay-view-bound-dropped | `[^c]{1,3}$` | same: no forward scan, no STAY loop | `X(?:$\|[^abc])+` and `(?:$\|[^abc]){2,}` (a view-bound forward STAY loop at the default) | probe asserts the `while ((scan_position + 1 < subject_length) && (rx_forward_stay` text for both; `reach:ok(2/2)` | UNREACHED / DETECTED, `corpus:2fail/14pass` (harness target `tests/base/review_r2.rxt`) |

## What detects each row now, and why none of it is a deny-flag witness

Reach and detection are separate in the runner: a probe only proves the site is
reached; the suite proves the plant is seen. So each row needed both checked.

- **S237/S238** (`anchoredmatch`). The old detectors, §6a/§6b (a lowered-cap
  reference compiler with the `K53_DENY` pair) and §5's corpus floor
  (`n_drop` >= 6), still fire and always did; only the reach probe was stale.
  Added §6d to `tests/codegen/run_anchored_match.sh`: the three chains above at
  the default cap and flags must compile, stamp `search-filter` +
  `size-cap-retry`, carry no anchored table, and be byte-equal to the
  caller's own `-fno-anchored-dfa` build modulo the output name and that stamp;
  control `\p{L}` -e utf8 still keeps `unwrapped`. Attribution under a hand
  plant (S237 tree, suite alone): §6a x4, §6b, §6d x4, §5 floor (1 of 6) red.
  The §6d reds are the default-path half.
- **S252/S253** (`tunedial`). `tests/codegen/run_tune_dial.sh` §6 is the K59
  witness walked over the five `--tune` positions. Its pattern is now
  `[^\p{C}\p{M}\p{P}]xy` with no deny flag; it reproduces the same stamp and
  note table as the one-class witness had before landing (113/0).
- **S421/S422/S423** (`resource`, `pfcollapse`). `[PF-DROP]` in
  `tests/resource/run_resource_tests.sh` already existed, re-aimed by lane
  sltri with `-fno-start-landing`. Now the prefilter-drop, anchored-drop and
  premul-drop witnesses are `(\p{Xwd})\b` / `\p{L}\p{N}\p{Lu}` /
  `[^\p{C}\p{M}\p{P}]xy`, all default path. The `(a|b){1,30000}
  -fno-scan-edge -fno-start-landing` collapse cell keeps its deny: at the
  default it fits (680,965 B, hybrid kept) and I found no default-path
  collapse witness. It is a pre-existing cell, not a reach witness of any of
  these rows, so S421's detection no longer depends on it (S421 reads
  `resource:4fail`, three of which are the default-path cells).
  Note S423 measures TWO red cells (the prefilter-drop witness and the collapse
  witness), not the one the old figure predicted.
- **S264** (`harness`, `prechecks`). `tests/assertions/end_window.rxt` now
  reads 0 failures under the plant (its 13 blocks are DFA-route, so `rev-end`,
  except `(ab)(c)$`, which has no trailing-newline cell), so the answer-level
  detector is the rest of the corpus: `kreset.rxt:714-715` (`a\Kb\z`),
  `multiline.rxt:1701` (`([^c]{1,3})$`), `rev_end.rxt:352/386/450` among the
  31 reds. The structural detector is `run_prechecks.sh` §2.1b, whose
  `-fno-rev-end` rows are a deny-flag set by revbuild's design, but the row
  `(ab)(c)$` is the default-path one (the VM route ignores `-fno-rev-end`).
  I added no corpus cell: a case line in `end_window.rxt` moves
  `CENSUS_LINES`/`RUNSH_LINES`/`C3_PASS`/`C3_VERIFIABLE` and the
  expansion-diff §6.3 cell counts, and the existing detectors already cover
  the default path.
- **S614** (`harness`). `gate.rxt` reads 0 failures under the plant. The
  default-path detectors are `tests/base/review_r2.rxt` (2 reds:
  `(?:$|[^abc]){2,}` and `X(?:$|[^abc])+` on `XY$\n`, expected `match 0 3`
  got `match 0 4`) and `tests/base/eol_engine.rxt` (1 red). The row's
  `SAB_HARNESS_TARGET` is now `review_r2.rxt`, whose two patterns are the
  reach probe's.

## Margins and risks (read before trusting these in a year)

Each size witness is a three-sided window and I recorded the sides in the
script comments (tune_dial §6, resource [PF-DROP], anchored_match §6d):

- the tightest side is S252/S253's `[^\p{C}\p{M}\p{P}]xy`: after rung 1 it is
  1,046,700 B, 4.7% over the 1,000,000 B cap. A change that shaves ~5% off that
  artifact would make rung 2 unneeded and S252/S253 would go UNREACHED again;
  the probe asserts the premul note and `DFA_TABLE "indexed"`, so it would say
  so loudly. I searched 14 variants for a wider side; `xyz`/`xyzw` have more
  room on the first side but fit after rung 1 (rung 2 never needed), so none
  is better.
- `\p{L}\p{N}\p{Lu}` (S237/S238): 1,360,906 B with the machine, 828,646 B
  after; both far from the cap.
- `(\p{Xwd})\b` (S421-S423): 17% over the cap, and needs `--features assertions`
  (`\b` is an assertions-module construct; the rest need no feature).

## Not done / left alone

- No full `make test`, no full mech, no `make test-axes` (box held). Light
  validation, each run standalone and named below.
- The deny-flag sections that remain (anchored_match §6a-c with
  `K53_DENY`, the resource collapse cell, prechecks §2.1/§2.5/§2.6 with
  `-fno-rev-end`) are unchanged: they are calibrated measurements of the
  denied path and are still correct.
- `tests/mech/CLAUDE.md`'s older S264 prose and `178fail/28848pass` figure are
  historical and left as written; the new `[MECH-REACH] nine rows re-pointed`
  paragraph at the end of that file carries the current witnesses.

## Validation (all on this box, light, cores 0-9, nothing else heavy running)

| what | command | result |
|---|---|---|
| anchored_match | `bash tests/codegen/run_anchored_match.sh` | 22 passed / 0 failed (was 20; +§6d's two) |
| tune_dial | `bash tests/codegen/run_tune_dial.sh` | 113 passed / 0 failed |
| resource | `bash tests/resource/run_resource_tests.sh` | rc 0, every `[PF-DROP]` cell PASS |
| the nine rows | `bash tests/mech/run_sabotage_matrix.sh S237` ... one id at a time, `PROCS=1 JOBS=2` | each `unexpected: 0, undetected: 0, unreached: 0, anomalies: 0` |
| neighbours | `S249 S420 S636 S697` (rows whose suites I edited) | see handback |
| field validation | `VALIDATE_ONLY=1` on each of the nine | valid |

## Pins

None moved. The three edited scripts are not corpus files (rxtsource census,
start-set manifests and axes allowances unaffected); `run_anchored_match.sh`'s
own pass count is not pinned anywhere (grepped `tests/registry`, `tests/mech`,
`Makefile`). The full `make test` is the manager's at merge.
