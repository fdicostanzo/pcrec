# Lane `revdes` — [OPT-REVEND] design + hand-twin (2026-10-09)

Branch `lane/revdes` off main `de6acf09` (abi 70). Opus, DESIGN + hand-twin;
nothing under `src/`, `cli/`, `lib/` or `tests/`, and no plan or journal edits.

**Deliverables:**
- `docs/design/revend.md`, the note;
- `studies/revend_twin/`, with its own CLAUDE.md, the scripts and verbatim
  `results/`;
- entries in `docs/design/CLAUDE.md` and `studies/CLAUDE.md`;
- this report.

## Summary (resume from here)

- **Route:** ONE new WINDOW-slot row `rev-end` ahead of W1 `window` in
  `cand_rows[]`. It hands `LOWER = s*` (written into `search_from`, exactly
  where W1 writes `n - W`) or a NOMATCH VERDICT. Every later slot runs
  unchanged over `[s*, n)`.
  - This is the twin's **form B**.
  - `start_table.md` §4.4 had REVEND handing `CAND`. That type needs a new
    edge and a row-selected skeleton; `LOWER` reuses E2.
  - The walk is the artifact's OWN reverse machine and reverse block
    (`emit_scan_loop`, `emit_dfa.c:9528`), seeded at `n`, and at `n-1` when
    `$`/`\Z` and `s[n-1]=='\n'`. It needs no new machine.
- **Admission** has three conjuncts:
  - R1: a new fact `end_pin`. It is `endwin.c`'s `ew_walk` view plus the
    `\G` and multiline declines, with NO width and NO encoding conjunct.
    `end_window` becomes its reader.
  - R2: the DFA route, with RECOVER selecting `reverse-pass`, read through
    `cand_read`.
  - R3: the caller-facing entry (`fit.chosen == ENGM_DFA`).
  - Deny: the row deny `-fno-rev-end`, one new bit. No force flag.
- **Exactness:** every match ends in `{n, n-1}`. So `s*` (the minimum
  accepting position over both seeds) is the leftmost start, and the end is
  found by the unchanged forward pass from `s*`.
  - **utf8: the walk discharges K49/K50 by construction.** It accepts only
    at character starts, so it serves exactly the cells W1 declines.
- **Interaction:** REVEND subsumes W1 on the DFA route (Q1). W1 stays for
  the VM route, for hybrids until stage 2, and as the deny arm.
  - No [MEMFN] request. The walk is a DFA step (never delegated), and its
    skip loops are the existing STAY `dir_rev_skip` site, emitted a second
    time.
- **Family:** the seeded reverse walk (RECOVER, REVEND, D151 rev-inner).
  - The three share one helper: `emit_scan_loop`'s reverse arm,
    parameterized by seed, result, lower bound and label.
  - They share one mapping, `EXACTREV`.
  - **Build REVEND first.**
- **Build plan** (§9):
  - S0: the `end_pin` split (no mover);
  - S1: the helper parameterization (no mover);
  - S2: the row (the abi event, with readers by grep, §5.3);
  - S3: the bench AFTER window.
  - Stage 2 (the VM hybrid) and the lockstep two-seed walk are filed with
    their triggers.
  - 7 sabotage ids are needed (5 answer-level, 2 structural); the manager
    allocates them.

## Validation (complete; scratch tier)

| run | result |
|---|---|
| form A identity, byte, 35 patterns (`results/check.txt`) | 0 twin diffs / 742,945 cells; find-all 0 / 42,164; 0 / 659,925 vs libpcre2 10.46 |
| form A identity, utf8, 8 patterns (`check_utf8.txt`) | 0 / 12,440; find-all 0 / 2,969; libpcre2 0 except K74's 55 ill-formed-end cells on `\B\w*\z` (artifact identical) |
| form B identity, all 43 (`check_lower.txt`) | 0 / 755,385; find-all 0 / 45,133 |
| control `noeol` (`control_noeol.txt`) | red as required: `\d+$` 80, `a*$` 907, `.*$` 907 diffs |
| control `firstseed` (`control_firstseed.txt`) | red as required on `a*$`/`.*$` (907 each); NOT detected by `\d+$`/`\s+$` (recorded: the sabotage row needs a nullable newline-consuming witness) |
| timing (`timing.txt`, `timing_lower.txt`) | 3 repeats each. 7700X pinned to cpu 7, governor performance, load1 3.4-4.1 (a concurrent chain); stated as contamination |

Form B per-call medians on 1 MiB, against today's 0.1-2.4 ms on this box:
- `\d+$` 5-28 ns;
- `\w+\z` 17-36 ns;
- `\s+$` 13-27 ns (3.5 ns on the 16 KiB near-miss);
- `[a-z]+\.txt$` 22-69 ns;
- `.*\.txt$` 9-33 ns.

Per cell this is x10^3-x10^5.

## Predictions table, ready to relay (bench O-91 ask 2)

Ryzen 1600 bench box, auto-caps, fixed driver ([B133]). The point estimate is
the Linux form-B median x 1.6 + 5 ns (both UNMEASURED transfer terms). The
range is [Linux min, 2.5x point]. The **falsifiable claims are: every cell ≤
250 ns (≤ 300 ns if the grown driver is still in place), and size
independence.**

| cell | t-tail-digits-1m | t-tail-txt-1m | t-tail-space-1m |
|---|---:|---:|---:|
| tail-digits-eol `\d+$` | 50 ns (20-125), match | 15 (4-40) | 15 (4-40) |
| tail-word-eoz `\w+\z` | 65 (25-165), match | 50 (20-125), match | 30 (7-75) |
| tail-space-eol `\s+$` | 25 (4-65) | 25 (4-65) | 50 (15-125), match |
| tail-ext-lower-txt `[a-z]+\.txt$` | 40 (12-100) | 115 (50-290), match | 40 (12-100) |
| tail-dotstar-txt `.*\.txt$` | 20 (8-50) | 55 (30-140), match | 20 (8-50) |

Plus:
- `\s+$` x t-trim-nearmiss-16k: **10 ns** (3-25); today 29.1 us.
- `\d+$` x t-1m: **30 ns** (12-75).
- Do-not-regress cells, expected flat within noise: `anc-dollar`,
  `anc-z-lc`, `anc-z-uc`, `ctrl-abc-dollar`,
  `wild-semdiv-dollar-trailing-newline-pcre2` and `letters-bounded-tail-z`.

## Open questions for Frank (discussion; full text in revend.md §10)

1. **Should REVEND take the bounded (class B) patterns from W1?** The table's
   EXACT-before-WINDOW order says yes. The cost is about 120 corpus movers
   and 6 bench floor cells, at predicted parity. The alternative needs a
   "W1 declined" conjunct, which is the special-case smell. Leaning: REVEND
   first, with the 6 cells named as do-not-regress.
2. **Form B over form A.** Form B is measured equal or faster on 15 of 17
   cells, fits edge E2, keeps the stamps truthful and needs no anchored
   entry. Leaning: B, with A filed for a long-matched-tail cell.
3. **Stage 2, the VM hybrid route.** No captures-bearing cell exists in the
   family. Leaning: file it with its trigger (D77).

## Bench-only questions (for the manager to relay)

1. Will the AFTER window run the fixed driver ([B133])? The predictions
   assume it.
2. Can it add a 64 KiB `t-tail-*` variant, to show size independence?
3. Keep the 5 class B cells and `letters-bounded-tail-z` in the window as
   do-not-regress cells.

## Manager-level items (not Frank's)

- **Stamp spelling:** the `"reverse"` token for `<PREFIX>_END_WINDOW` and the
  listing row name `rev-end` (memory dd13b: spelling is the manager's).
- **`start_table.md` §4.4** needs a one-line correction (`hands CAND` →
  `LOWER | VERDICT`, pointing at revend.md) at merge.
- **Sabotage ids:** 7 (§9.2).
- **No live finding against main.** The one oracle divergence is K74
  (known, open, deferred). One note for later readers: `-e utf8` implies the
  `ucp` MODULE, not UCP semantics (`cli.md (old line 219)`). This lane's
  first utf8 oracle got that wrong and was superseded; it was not a pcrec
  issue.
