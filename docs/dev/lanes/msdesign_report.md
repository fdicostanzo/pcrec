# msdesign — [MATCH-SPLIT] 4a design note (2026-10-12, lane msdesign, opus)

Branch `lane/msdesign` from main `33c2eb7a` (abi 76). The lane was design only. Nothing under
`src/` changed. Evidence came from single compiles on this branch (`build/ms/`, not committed),
which were used to read stamps and emitted code. The deliverable is
`docs/design/match_split_pinonly.md`.

## Read

- `docs/design/match_split_requirements.md` in full, including the §5.1 rulings: Q1, Q2, Q5
  and the 4a scope.
- `docs/dev/lanes/mssurvey_report.md`, `docs/dev/optloop/matchsplit/{summary,qwork}.txt`, and
  the instruments' CLAUDE.md.
- `docs/dev/chunks_2026-10-11.md`, plan rows [MATCH-SPLIT], [OPT-ATTEMPT-SPLIT],
  [ENG-ABS-CARET] and [FINDALL-NEXT], and K106 / K103 / K104.
- D156 (+ addenda 1-4), D157, D158, and D151 addendum 6.
- From `src/gen/emit_dfa.c`:
  - `cand_rows[]` and `cand_nodes[]` (the LOCATE, BOUND, RECOVER and FINISH blocks);
  - `locate_rev_end_applies`, `emit_rev_end`, `revend_nl_last` and `emit_reverse_block`;
  - `emit_attempt` (BOUND selection, MLINE skip, start dispatch) and `anch_start`.
- From `src/core/compile.c`: the ENG_UNANCH/ENG_ATTEMPT arms, `build_anchored_dfa` and
  `fit_rungs[]`.
- `src/ir/nfa.c` (`pcrec_nfa_has_bot`, anchor lowering), `src/facts/endwin.c` (`end_pin`,
  `ew_walk`) and `src/facts/facts.def`.
- Spec: `docs/spec/match_api.md` §6¶1 and §6.3.4 (`RX_DFA_SCAN`/`_DFA_START` value sets);
  `tuning.md` section numbering; `lib/pcrec.h` flag bits (0-54 used, 9 free).

## Decided (the note's choices; answer-free or following rulings)

1. **Floor/racing decomposition.** Floor classes are S and G: one candidate, the minimum
   start. Racing classes are E, LS, LE and F. With floor classes plus at most one racing class,
   the split wastes nothing and needs no state. 4a therefore admits S+E / G+E / S+G+E: 22 of
   the 35 pin-only patterns, including 9 of K106's 11 counted trim shapes, the utf8 outage form,
   and the wrapper strip with its captured hybrid form.
2. **Mixes left unchanged** (already linear today):
   - S+LS and G+LS are served by the MLINE `memchr` skip (stamp `memchr`, read here).
   - E+LE is served by the unanchored composite.
3. **Locator.**
   - The floor is one iteration of today's ATTEMPT loop, bounded by two new BOUND rows
     (`floor-bot`, `floor-gstart`, `.one = NONE`). These read LOCATE's selection through a new
     declared edge.
   - The END class is `emit_rev_end`'s walk, factored into `emit_end_walk`, run over Q: the
     reverse NFA with the BOT-family kinds killed (`pcrec_nfa_kill_bot`). Q is built in the
     ATTEMPT arm as an optional machine, following `build_anchored_dfa`'s pattern.
   - A tie is resolved inside the locator by one attempt at `s*`, so FINISH is untouched and
     `_match` does not move.
4. **One fact, `pin_split`** (`src/facts/pins.c`, E2, a port of msclass.py's path summary). It
   carries a one-way machine agreement assertion, following [OPT-ANCHOR-VM]'s pattern.
5. **Table placement.**
   - LOCATE row `split`: CR_ATTEMPT, `whole`, hands SPAN/NOMATCH.
   - RECOVER `reverse-pass` gains the CR_ATTEMPT WINDOW cell.
   - `fit_rungs[]` gains `drop-split`.
   - Stamp `RX_DFA_SCAN "split"`. `RX_DFA_START` changes to `reverse-pass` by the generated
     rule.
6. **Cost.** Derived by counted loads (§5): K106's trim drops from 128,040,002 to 2 loads at
   k = 16k, and the wrapper strip from n+3 attempts per call to at most 1. The admission follows
   from dominance (split ≤ today + 2 loads per call, on every subject). No prior is read and no
   hand-set constant is used. The design needs no hand twin.

## Open (for Frank, discussion form in the note's §9)

- **Q1.** Should the deny take a new bit now (`-fno-match-split`, bit 55, one for the whole
  combinator) or reuse `-fno-rev-end`? Leaning: new bit, because reusing it confounds a bisect
  and 4b needs a combinator deny anyway.
- **Q2.** K106's two `(?m)` trim shapes (LS+LE, two racing classes) stay quadratic after 4a.
  A sound design exists: an UPPER-bounded forward scan, never worse than today per call. It
  belongs with 4b's composite-of-Q. Leaning: 4b.2, with K106 re-worded.
- **Q3.** The short-call fixed term: admit unconditionally (loads dominance), with a
  scratch-tier short-call landing cell and a K row if it shows (D144).

## Findings (note §11)

- **F-1.** E+LE and S+LS/G+LS are already linear today, so 4a's real population is the 22
  floor+E patterns.
- **F-2.** On ATTEMPT artifacts `_match` is `_search(pos)` filtered, so a failing match-here is
  O(n). Unlock U8.
- **F-3.** `end_pin`'s `\G` decline belongs to the WINDOW clamp, and rev-end's R1 inherits it.
- **F-4.** The `RX_DFA_SCAN_EDGE "none"` spec sentence needs an exception for split artifacts.

## Not done

- No build, no timing, no hand twin, no `make test`. A design lane owes no validation run.
- The sabotage ids (MS-1..MS-11) are unallocated and left to the manager. Check the memfn
  reserved ranges first.
- The bench relay (the `RX_DFA_SCAN` closed enum gains `"split"`) was drafted in one line and
  not sent.
