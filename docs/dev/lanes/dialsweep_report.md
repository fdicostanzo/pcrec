# dialsweep — [OPT-DIAL] §7 SIZE SWEEP delivery report

Lane `dialsweep`, sonnet, 2026-09-15. Branch `lane/dialsweep`, worktree
`worktrees/dialsweep`, branch point `30b1f7f2`. Measurement only — nothing
under `src/` or `tests/` lands from this lane.

## Task

`docs/design/opt_dial_inventory.md` §7 names ONE sweep that would move six
UNMEASURED switches at once: emitted-size per artifact, DEFAULT build vs
each deny/force flag, over the whole corpus. Deliver the memo
`docs/dev/optdial_size_sweep.md` plus reproduction pieces, following
`docs/dev/artifact_size_census.md`'s own layout choice (report + script
directory under `docs/dev/`).

## What ran

Eight full-corpus passes through `tests/harness/run.sh` (no file/dir
arguments — the whole `tests/` tree), each with `SIZELOG`+`RXTDUMP` set,
one flag at a time, sequential (one heavy pass at a time per box
citizenship), each wrapped in `scripts/watchdog -s 3600`, each
auto-WIP-committed on completion:

| pass | rc | wall | size rows |
|---|---|---|---|
| baseline | 0 | 1,017s | 3,478 |
| `-fno-possessify` | 0 | 966s | 3,478 |
| `-fno-revdet` | 0 | 976s | 3,478 |
| `-fno-altcls-merge` | 1* | 990s | 3,477 |
| `-fno-altcls-factor` | 0 | 1,001s | 3,478 |
| `-fno-tiered-entry` | 0 | 981s | 3,478 |
| `-fno-offset-skip` | 0 | 956s | 3,478 |
| `-fno-anchored-dfa` (bonus) | 0 | 945s | 3,478 |

\* `-fno-altcls-merge`'s rc=1 and one-row-short SIZELOG is the harness's
own "cases failed: 2" for `tests/size/size_term.rxt`'s nested-repeat
tower, which refuses to compile under this flag with `pattern too large
(VM exceeds 131072 emitted nodes)` — this is `tests/axes/run_axes.sh`'s
own already-documented K45 refusal for exactly this axis on exactly this
pattern (`REFUSAL_PATTERN["-fno-altcls-merge"]="pattern too large (VM
exceeds"`), reproduced here independently, not a defect this lane
introduced or found. Every other pass is a clean 0/3,478.

**Nothing is OWED on the sweep itself — all eight passes completed** (this
matters because the lane received a mid-flight "wrap up now, session
resets shortly" instruction; by the time it arrived, `git log` already
showed all seven flag-pass WIP commits plus baseline, confirmed by
re-reading the orchestrator log rather than assumed from the commit
messages alone — `altcls_merge`'s exit code was checked against its own
`.err` file, not glossed over as a stray failure).

## Method

- Size definition: `tests/lib/size_count.sh`'s `size_count_row` — the
  same definition `docs/dev/artifact_size_log.tsv` and the `[ART-SIZE]`
  census use, cited and reused rather than reinvented.
- Corpus population: `tests/harness/run.sh`'s own full-tree walk, no
  file/dir arguments — 3,478 SIZELOG rows, matching the already-committed
  `docs/dev/artifact_size_log.tsv`'s own row count at a nearby commit (not
  a number this lane chose).
- Join key: `file:line`, the same key `tests/axes/dump_diff.awk` uses.
- The `#include`-line diffing trap (recorded three times previously in
  this house) does not apply: every pass shares the identical `gen.c`/
  `gen.h` basename by construction (same `tests/harness/run.sh`
  mechanism), and this sweep compares byte COUNTS via `SIZELOG`, never
  artifact TEXT.
- K35: every pass's `RXTDUMP` was checked for `REFUSED` rows rather than
  assuming zero — one flag (`-fno-altcls-merge`) had a real, already-
  documented one; the other six had zero.

## Findings (full detail in the memo)

1. **`-fno-tiered-entry` is the cleanest result**: 330/3,478 (9.49%)
   reach, EVERY mover shrinks under denial, tightly clustered at
   -1,953/-1,957 bytes — a near-fixed per-artifact cost, not a
   percentage. Combined with the inventory's already-measured ~5x
   per-call TIME number, this is a full MEASURED TRADE and graduates to
   the dial cleanly.
2. **`-fno-anchored-dfa` (the bonus switch) has by far the largest reach
   of anything in the whole inventory**: 1,509/3,478 (43.39%), monotone
   (every mover shrinks), median -3,075 B, worst case -266,794 B on a
   `\p{...}`-property pattern. The inventory's existing entry explicitly
   scoped its size number to "a pathological 30,000-count shape, not from
   the corpus" — this sweep replaces that caveat with a real,
   corpus-general number an order of magnitude broader in reach than any
   other switch measured.
3. **`-fno-altcls-merge`/`-fno-altcls-factor`** mostly confirm the
   inventory's own "likely a PURE WIN" hypothesis on size (median moves
   favor keeping each switch ON), but each has one real, measured
   non-monotone counter-example on the same corpus — the same shape
   `--unroll=K`'s own non-monotone byte curve already warns about — so
   neither qualifies as a strict PURE WIN under §1's "never worse on any
   measured input" bar. Their existing TIME number (-7.61%) is shared
   between the two flags (both denied together), which is flagged as a
   follow-on gap rather than glossed over.
4. **`-fno-offset-skip`** graduates to a clean MEASURED TRADE: 491/3,478
   (14.12%) reach, mostly favoring ON on size (median -332 B under
   denial) with a real ~13% minority trading the other way.
5. **`-fno-possessify` and `-fno-revdet` stay fully UNMEASURED** — the
   two switches that had no TIME number before this sweep either. This
   sweep discharges only their size half (possessify: mixed, median
   favors ON; revdet: near-zero median, wide two-directional spread, no
   clean lean). A matching throughput sweep is the natural next lane,
   named explicitly as owed in the memo rather than silently left absent.

## Deliverables

- `docs/dev/optdial_size_sweep.md` — the memo, filled with real measured
  numbers (no placeholder text remains).
- `docs/dev/optdial_size_sweep/run_sweep.sh` — orchestrator.
- `docs/dev/optdial_size_sweep/join_sweep.py` — join/analysis script.
- `docs/dev/optdial_size_sweep/CLAUDE.md` — directory doc.
- `docs/dev/optdial_size_sweep/runs/` — raw per-pass tables (`*_size.tsv`,
  `*_dump.tsv`, `*.out`/`*.err`, `orchestrator.log`, `summary.tsv`), 26 MB
  committed, incrementally via the orchestrator's own WIP commits.
- `docs/dev/CLAUDE.md` — new bullet for `optdial_size_sweep.md`.

## What is NOT done

- `docs/design/opt_dial_inventory.md` itself is unedited — it is a design
  document (D80's contract: a design doc's own revision is its own
  change), and this memo is the evidence a follow-on revision to it would
  cite. The manager or a follow-on lane should fold this memo's findings
  into the inventory's §2.1/2.2/2.6/2.7/2.12/2.14/2.15 entries and §3's
  policy table.
- No throughput/TIME sweep for `-fno-possessify`/`-fno-revdet` (owed,
  named in the memo §5).
- No per-flag isolation of the shared -7.61% TIME number for
  `-fno-altcls-merge`/`-fno-altcls-factor` (owed, named in the memo §5).
- No characterization of WHICH pattern shapes produce the two flags'
  non-monotone counter-examples beyond the one measured cell each (owed,
  named in the memo §5).

## Validation

This is a measurement-only lane; no `src/`/`tests/` code changed, so
`make test`/`make strict` are not applicable to this lane's own diff.
`make -j4 CC=gcc-16` built clean at the branch point before the sweep
started. The sweep's own harness runs (`tests/harness/run.sh`) reported
0 unexpected failures on every pass except the one already-documented K45
refusal above; every pass's own summary line is preserved verbatim in
`docs/dev/optdial_size_sweep/runs/<slug>.out`.

## Handback

PARKED on `lane/dialsweep`. The manager merges. Validation: COMPLETE for
this lane's own scope (all eight sweep passes ran, the memo is filled
with real numbers, nothing is silently left as a placeholder) — the three
follow-on items above are explicitly OWED, not implied to be done.
