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

## What was run

The box was under HOLD (twintime's timing slot) when the lane started. During the
hold the lane ran only light work: a parse-only census, the four bench subjects
regenerated from a `git archive` copy of pcrec-bench `d359564f` (all four
sha256-matching the bench manifests), and 8 hand-picked patterns through the whole
game (8 `--emit-facts` compiles).

`.lift` appeared at 23:18. The armed waiter (`wait_lift.sh`) ran `chain.sh`, which
built this worktree's pcrec (`make -j16`, rc 0), compiled the 327-pattern population
(177 bench + 150 corpus) once each with `--emit-facts`, simulated every policy, and
committed `window_search_game/data/`. The run takes about 30 s and reads no clock.
Log: `build/wg/chain.log`, completion line `== wingame chain COMPLETE`.

The chain was re-run three times after fixes its own controls forced:
1. The k-set control first read 6 differing prefix positions. The causes were the
   extractor's handling of POSIX classes, `\v` (Python's VT byte, PCRE2's
   vertical-space class) and `(*UCP)` (wider byte classes, which the extractor does
   not model). The first two were fixed with a class-aware escape pass and the third
   is now declined as unparsed. Final control: **582 of 582 positions agree**, over
   166 patterns.
2. `summarize.py` read the TSVs with Python's default csv quoting, so a span
   containing `"` merged rows (`QUOTE_NONE` now).
3. The kit's form prices were rescaled to units of one DFA step (a memchr pass is
   far cheaper than a DFA step; the first constants priced them equal, which inflated
   P5-dfa's declines). The prices remain UNMEASURED (D149) and are parameters.

Final commit of the data: see the branch tip. No `make test` is relevant: nothing
under `src/`, `tests/` or `memfn/` changed, and nothing the compiler reads moved.

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
   bounded spans is rare (18 of 327 patterns have >= 2), and the span argmin flips
   between the DFA and VM prices on 3 of the 22 multi-span cells. The consumer flips
   WHETHER to search far more often (18 patterns).
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
