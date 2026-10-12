# Lane wingame: report

Lane `wingame` (2026-10-11, branch `lane/wingame` from main `aa2ddb1d`). Brief:
game out memfn's "search for the window" category (D161) before any request is
written. Design study: nothing under `src/`, `memfn/` or `tests/` is touched. COUNTS ONLY.

## Deliverables

- `docs/design/memfn/window_search_game.md`: the note. §0 is the answer, §1 the
  span list and which pcrec facts supply each piece, §2 what the contract cannot
  express, §3 the kit policies, §4 the results, §5 Frank's concern, §6 the
  standing questions, §7 three discussion points for Frank.
- `docs/design/memfn/window_search_game/`: the instruments (`spans.py`, `game.py`,
  `gen_subjects.py`, `run_game.py`, `summarize.py`, `chain.sh`, `wait_lift.sh`,
  with their own CLAUDE.md).
- `docs/design/memfn/CLAUDE.md`: an entry for the note.

## What was run, and under which constraint

The box was under HOLD (twintime's timing slot) for the whole lane. Within the
hold's "a handful of single compiles":
- a parse-only census of 327 patterns (177 bench + 150 corpus; no compile);
- the four bench subjects regenerated from a `git archive` copy of pcrec-bench
  `d359564f`, all four sha256-matching the bench manifests;
- 8 hand-picked bench patterns run through the whole game (8 `--emit-facts`
  compiles using the main tree's `build/pcrec`). These give the note's §4.1 table and
  every §5 number.

## OWED: the population run (§4.2 of the note)

The full run (it builds this worktree's pcrec, compiles 327 patterns, and simulates
every policy over the subjects) is ARMED DETACHED behind the hold:

    nohup setsid bash docs/design/memfn/window_search_game/wait_lift.sh <worktree> &

The waiter polls `worktrees/wingame/.lift` every 60 s for up to 8 h, then runs
`chain.sh` once. Log: `worktrees/wingame/build/wg/chain.log`. Completion line:
`== wingame chain COMPLETE`. The chain COMMITS `window_search_game/data/`
(5 TSVs + `summary.md`) on `lane/wingame` itself.

**For the fresh agent that completes delivery**, after the completion line:
1. Read `data/summary.md`. Check §A3 (the k-set control) first: any `differ` row
   means the extractor and pcrec disagree on a prefix class, so look at those patterns
   before citing anything else.
2. Check that §A's census matches the note's §2.1 table (the parse-only numbers).
   If it differs, the facts compile changed `anch_start`/`status` nowhere, so a
   difference means a bug.
3. Fill the note's §4.2 status line and §5.4's "population frequency" sentence from
   §B2/§D/§D2. If the scan-only-vs-vm-priced flip count is large, add one or two
   §D2 rows to §5.2.
4. Keep every claim in §0 unless §D contradicts it: the survivor-ratio
   distribution should look like §5.3's (p50 >> 1).

Expected runtime: a few minutes (327 compiles at <= 30 s cap each, numpy sims on
256 KiB subjects). Smoke runs of every stage passed, including `summarize.py` on
the 8-pattern run.

## Findings (all in the note)

1. The kit can rank STOPS from D161's inputs. It cannot rank spans whose windows
   differ, because the per-survivor cost depends on the consumer's SHAPE: a DFA
   pays per window byte, a backtracker per possible start.
   `wild-logparse-syslogbase-expanded` ranks its two spans in opposite orders
   under the two shapes. pcrec's shipped VM-hybrid choice (the prefix) is the
   VM-priced one, and the consumer-blind pick costs 2.3x under it.
2. The decline ("is any window search worth it") also flips with the consumer, and it
   needs the consumer's no-search cost, which D161 does not carry.
3. The independence survivor estimate is off by 21x-1,750x on multi-position spans,
   while one-position stop counts land within 0.3x-6.8x. The table prices the scan
   and not the window.
4. pcrec's req facts carry MAXIMUM offsets only, so overshoot is underivable
   from them today. The handoff is used with `ov = K`.
5. The unbounded move-back is the contract's biggest miss: 15-22 % of unanchored
   patterns with a span have their rarest position behind one. Span-vs-span among
   bounded spans is rare (18 of 327 patterns have >= 2).
6. Minor, not filed: `syntax/msc-r-uc` (`item\Rdone`) is refused by pcrec's
   `--features all` compile (`\R`). That is expected D26 behaviour, noted only
   because SHIPPED reads `compile-refused` there.

## Answer to Frank's concern, in five lines

The kit can weigh spans by their scan stops alone. That is D161-complete, but it is
the wrong ranking whenever windows differ. Spans with similar stops differ by 3x-26x
in window bytes and by up to 100x in possible starts. Whether that matters depends
on the consumer: a DFA pays per byte and a VM per start, and syslogbase flips between
them. Per-span overshoot is necessary (pcrec must add MINIMUM offsets to produce it)
but not sufficient. pcrec should also state a per-route consumer price (cost per
candidate, per window byte, per start, and per byte of no search), and optionally a
joint survival rate. The kit should not own the look-forward.
