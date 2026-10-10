# sltri — triage of lane/slbuild's landing red

Lane sltri, 2026-10-10, opus. Branch `lane/sltri` from `lane/slbuild`
`be57ab25` ([START-LANDING] SL1-SL3, abi 74), with main `04b83ddf` merged
first (`eebac1e9`: lane/sweepfloor's start-sweep floors plus a plan commit;
one conflict, the `docs/dev/lanes/CLAUDE.md` index tail, both lines kept).
Input: the landing chain's `make test` log
(`worktrees/slbuild/build/land/test.log`), red in test-anchored-match,
test-codegen, test-fallback-table, test-findings, test-prefilter,
test-prefilter-collapse and test-tune-dial (perfrun `class=RED-REAL`).

## 0. The answer-level statement

**No answer regression.** No pcrec answer differs from libpcre2 in any of
the seven sections, and no `src/` change was needed. Every red is one of
these:

- a size-rung witness that SL2 moved off its rung (a FIT mover, which
  slbuild's report predicts in §2);
- a syntax error slbuild introduced into a check script;
- a structural scanner whose existing blind spot SL2's edits moved onto a
  known reader.

All are class (b). None is pre-existing on main, since each section is green
on main. The one class (c) item is in the sweep (§2), and on inspection it
is also (b).

The FIT-mover mechanism: with landing, `(\p{Xwd})`, `\p{L}`,
`(*UCP)(?i)[\dk]`, `[^\p{C}\p{M}\p{P}]` (all `-e utf8`) and `(a|b){1,30000}`
`-fno-scan-edge` take RECOVER's `landing` row. That drops the reverse
machine, so they fit under the cap with no rung. The fixed-width K53
witnesses (`foobarbazqux`, `abcdefghij[0-9]+`, `a[bc]d[ef]g[hi]j[kl]m`) take
`end-minus-width` and shrink under the calibrated 21,500-byte window. Each
witness was re-aimed with the masked, answer-neutral deny that puts it back
on the reverse pass. Example, K59's witness at `--tune=0`:

| build | artifact | stamps |
|---|---|---|
| default | 708,814 B | `selected`/`unwrapped`/`premultiplied`/`landing` |
| `-fno-start-landing` | 449,338 B | `size-cap-retry`/`search-filter`/`indexed`/`reverse-pass`, both drop notes |

The second row is exactly what the check expected before SL2.

## 1. Fix by fix

| section | check | class | evidence | fix | commit |
|---|---|---|---|---|---|
| test-codegen | `run_dfa_stamps.sh` exits 2: `line 296: syntax error near unexpected token '('` | (b) slbuild's own edit | `bfe30c75`'s new awk comment "the NEXT block's record" puts an apostrophe inside the single-quoted awk program, which closes the quote. The whole script never ran on slbuild, including slbuild's new `[start]` recogniser (S787/S791's detector) | Comment reworded, no apostrophe. `[start]` now PASSES on all 4,237 artifacts (it reads the width subtraction and the landing write); codegen 15/15 | bdc2a2c0 |
| test-findings | `structural_check.py` S1: "the scan no longer reaches reader(s) req_byte_dominated_by" | (b) instrument blind spot | `req_byte_dominated_by` is unchanged. The function finder counts braces after `strip_comments`. That function strips `/* ... */` inside STRING literals (`tr_comment_premul`'s emitted comment text) and leaves `"...)\n{\n"` braces in, so on main `emit_search_head` already swallowed 4,637 lines (228 functions found in emit_dfa.c). SL2's edits moved the stray closer past `req_byte_dominated_by` (9,350 lines swallowed, 73 functions) | S1 blanks comments AND string/char literals in one left-to-right pass (`code_only`). emit_dfa.c now yields 347 functions with no false swallow; main still reads 32 readers / PASS; S301's plant is still caught (verified on a planted copy) | bdc2a2c0 |
| test-tune-dial | §6 K59: at `--tune=-1/0/1/2` ESEL `selected`, DFA_MATCH `unwrapped`, `premultiplied`, no drop notes | (b) FIT mover | The K59 witness `[^\p{C}\p{M}\p{P}]` takes `landing` and fits (table above) | `K59_DENY='-fno-start-landing'` on the §6 compiles, with the cause commented. §6's control cell `-2` still reads `selected`/`unwrapped`/`indexed` | bdc2a2c0 |
| test-anchored-match | §6a "1 of 3 expected patterns took [the drop rung]" | (b) FIT mover | The three fixed-width K53 witnesses take `end-minus-width` and fall under the 21,500 B window calibrated on the reverse-pass artifacts | `K53_DENY='-fno-start-width -fno-start-landing'` on every §6 compile (HI and LO, default and `-fno-anchored-dfa` arms), so the window and the rung stay the reverse-pass ones | bdc2a2c0 |
| test-fallback-table | 22 FAILs: sequences seq-pfcdrop/pfdrop/anch/premul/premuls/refsize, records adm-sizedrop/att-scanch/att-scpf/gate-sizecap, witness sel-sizecap, the `size-cap-retry` floor, three shape cells, three drop-note cells | (b) FIT movers | Every utf8 size-rung witness in the file (`(\p{Xwd})`, `(\p{Xwd}{1,3})`, `\p{L}`, `(*UCP)(?i)[\dk]`, `[^\p{C}\p{M}\p{P}]`) takes `landing` and fits; the anchored ones (`^(\p{Xwd}{1,3})?$`) were already green | `-fno-start-landing` appended to the 17 failing witness lines, one cause comment at the T1 rows 6-9 header | bdc2a2c0 |
| test-prefilter | "T2 size-dropped/NONE: --emit-ir's prefilter value is 'yes', expected 'no-size-cap'" | (b) FIT mover | `(\p{Xwd})` fits with its prefilter | `-fno-start-landing` on that row, with the cause commented (the forced-off control row unchanged) | bdc2a2c0 |
| test-prefilter-collapse | "[sel] the 'size-cap-retry' witness stamps RX_ENGINE_SEL 'selected'" | (b) FIT mover | slbuild §2 names `(a|b){1,30000}` `-fno-scan-edge` as a FIT mover (672,758 B) | `-fno-start-landing` added to the witness (re-checked: `size-cap-retry`, `reverse-pass`) | bdc2a2c0 |

All seven sections were re-run solo on this tree (`make test-<section>`,
logs in `build/tri/`), and all are rc 0. The first codegen and
anchored-match runs overlapped my edits and were discarded; both were
re-run clean after the commit.

Two things this table settles about slbuild's own report:

- **slbuild's `[start]` claim was never tested.** Its §2 says
  "`run_dfa_stamps.sh` [start] now reads the two new mechanisms off the
  text". On slbuild the script did not parse, so that check never ran. It
  now passes.
- **S787 and S791 have no valid verdict yet.** Their only detector arm
  (`dfastamps`) cannot have produced one on slbuild's tip: the chain's mech
  run scores them against a script that exits 2. They are re-run on this
  tree by the owed chain (§4).

## 2. The start sweep

`python3 scripts/emit_sweep.py --ref-bin <sltri pcrec> --bin <same> --arms
start` was run on this tree, with one binary on both sides, so it measures
floors rather than identity.

**First run** (`build/tri/sweep.log`): rc 1, 240 s.
- Self-check: PASSED.
- Every arm's DIFFER floor HELD. SL2 moved none of sweepfloor's floors below
  its pin; this was checked line by line against the `floor=` column.
- The one red was `COMPOSITION PRODUCING FLOOR VIOLATION: 37 < 38`.

**Investigation of the composition red.**
- Main's binary on this tree also reads 37, so the binary is not the cause.
- Main's binary on main's tree reads 38 (383 files).
- A per-file A/B names the leaver: `tests/uprops/size_ladder_prefilter_drop.rxt`.
- Cause: slbuild added a second `pattern` block to that file (the PF-DROP
  rung's new witness `(\p{Xwd})x`). A two-block file with no `target` line
  is a definitions library that builds nothing ("1 input file declared no
  target"). The one-block file built itself (2 artifacts).
- This is class (b), a population pin moved by SL2's corpus edit.

**Fix and re-run.** `composition_producing_floor` re-pinned 38 -> 37, with
the cause commented (242aba6b). The re-run is `build/tri/sweep2.log`; its
verdict is in the handback.

## 3. The chain's axes and mech verdicts

The slbuild chain was still running `make test-axes` when these fixes were
done, and its 50-row mech run follows. Neither verdict was readable at
hand-off. A fresh agent reads them:
- axes: `worktrees/slbuild/build/land/axes.log`, chain line `test-axes FAIL
  lines: N`;
- mech: `worktrees/slbuild/build/land/mech.log`, trailer
  `== mech run COMPLETE`.

The mech run uses slbuild's tip (`git archive HEAD` of that worktree), so
expect these artifacts of the unfixed tree, not new findings:
- S787 and S791 (detector `dfastamps`, the syntax error) will not score
  cleanly;
- any row whose arm runs fallback-table, prefilter, tune-dial,
  anchored-match or the findings structural check sees a red baseline.

## 4. Owed: the full `make test` (armed detached)

`build/land/chain.sh` is armed with `nohup setsid ... & disown`. It does the
following, in order:
1. Waits for `CHAIN COMPLETE` in slbuild's chain.log.
2. Runs `make -j16`.
3. Runs `scripts/perfrun --label sltri -- build/land/test.log`.
4. Runs mech rows S787 and S791 on this tree's HEAD.

Its log is `worktrees/sltri/build/land/chain.log`, with completion line
`SLTRI CHAIN COMPLETE`. Read the verdict from `make test red sections:`,
which comes from make's `*** [(Makefile:N: )?test-X] Error` lines, together
with perfrun's class. The mech trailer is `mech.log`'s
`== mech run COMPLETE`.
