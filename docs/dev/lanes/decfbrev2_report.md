# decfbrev2 — [DEC-FALLBACK] refactor B design note, revision 2 (2026-10-08)

Lane `decfbrev2` (opus), branch `lane/decfbrev2` from main `42ab7c25` (abi
68; `src/` identical to rev 1's base `31a9ae4c`). Design lane: nothing under
`src/`, `cli/`, `lib/` or `tests/` changed, no `make test`. Builds: `make
-j6` of the base, plus probed scratch compilers under the worktree's
`build/decfbrev2/` (never committed).

## Deliverables

- `docs/design/dec_fallback.md` — REVISION 2, PROPOSED, panel-addressed. §R
  is the per-finding disposition table (start_table.md rev 2.1's style).
- `docs/design/dec_fallback/state_readers.sh` / `.txt` — the reader census,
  now DERIVED from the declarations (critB2 M6): 408 lines, was 164.
- `docs/design/dec_fallback/reach/` — the row-reach PROTOTYPE (own
  CLAUDE.md): `build_reach.py`, `reach.py`, `analyse.py`, `summarize.py`,
  `witnesses.tsv`, and `out/` (`reach.md`, `reach.tsv`, `sequences.tsv`,
  `analyse.txt`).
- `docs/design/dec_fallback/refactor_edit_set.tsv` (+ the forcing arm's
  line), `sabotage_anchors.tsv`/`.summary` re-derived at `42ab7c25`.
- `docs/dev/plan.md`: the [DEC-FALLBACK] row gains the rev-2 block; the new
  row [DEC-COLLAPSE-WASTE] (STATE:not-started, FILED, NOT scheduled).
- `docs/design/CLAUDE.md`, `docs/design/dec_fallback/CLAUDE.md`, this
  directory's CLAUDE.md.

## Summary (a fresh agent resumes from here)

**Status.** B is ready to build, pending Frank's Q1 ([DEC-VAR-ATTRIB] as
one later row), Q2 (`--fast-or-fail` keeps its size-only reach) and Q4(b)
(list T1/T2 as axes at B7). The manager took Q3/Q5/Q6/Q7 as recommended, and
Q8 (the panel) is done.

**Disposition, in one line each** (the note's §R has the full table):
- critB2 B1: the `emit-ir-auto` stream and 18 hand-written `check_ir_value`
  rows are designed; together they are the B4 hard gate.
- critB2 M1: stream 7 is the full stderr and rc of every compile, with
  refusals compared.
- critB2 M2: floors are re-measured in emit_sweep's own population with
  `-e utf8` bases. The histogram is compared parent-vs-child in its own
  driver.
- critB2 M3: `row_reach` is designed and prototyped, a fifth variant
  `lowthr` is added, the `-fno-prefilter` and `--tune=min-size` arms are
  added, and `make alloc` joins B3's gate.
- critB2 M4: a 34-row sabotage plan.
- critB2 M5: the post-row state tuple and a per-slot `--order` in
  `trace_diff.py`.
- critB2 M6: the census is derived.
- critB2 M7: the legs retire at B5, behind the observed-stamp leg.
- critB2 m1-m5 are folded in:
  - m1: the histogram's limits are stated;
  - m2: `call_graph.py --family fallback` is designed;
  - m3: `degrading` vs `fof` are defined, with a B2 wording hunk to
    `limits.md` §8;
  - m4: the bound is asserted on observed attempts;
  - m5: stated as an argument, now measured.
- critB1 MAJOR-1/2: moved out of B into [DEC-COLLAPSE-WASTE], with the
  three-way split measured.
- critB1 MAJOR-3: row 0 `forcing` goes ahead of `nomem`.
- critB1 m1: a `repeat` column, asserted.
- critB1 m2: a backward attribution walk, plus a legal-sequence invariant.
- critB1 m3: the fired record is `volatile`; the anchored machine's own
  fallback is declared an unhosted sibling.

**Witnesses found** (prototype, decfb0's population of 4,794 distinct
corpus blocks plus 17 constructed witnesses, × 5 limit variants × 14 flag
arms, 60 runs; full table `reach/out/reach.md`, note §4.3a). Every T1-T4
row has a witness except the UNREACHED cells below. Shipped-limit witnesses
for the thin cells:
- T1 `sel1-drop`: `x(?!a)(?!b)…(?!q)` (tests/ucp/ctxnode.rxt:410).
- T1 `refuse` × overflow: `--engine=dfa (?:ab){0,16000}`.
- T2 `overflow-drop` at SEL1 scope: `-fno-prefilter
  ^(?:(?:a|b)*a(?:a|b){20})?$`.
- T2 `forced-on` at SIZECAP: `-e utf8 -fprefilter ^(\p{Xwd}{1,3})?$`.
- T2 `nullable-collapsed` at SEL1: `(?:ab){0,16000}`.
- T3 `forced`: `-fprefilter-collapse (x)?a{0,4}\Gb`.
- T3 `nullable`: `-fprefilter-collapse ^(a{2,9})*$`, and at base the
  [DEC-COLLAPSE-WASTE] (ii) witnesses.
- T3 `rung` SIZECAP at plain only under `-fprefilter`; at base it needs
  `lowsize`, `(?:a\K){2,}b`.
- T4 `capacity-declined`: lowthr, `--engine=vm (((?:a{0,2}b)+c){0,20}d){0,20}e`.
- T4 `option` and `denied`: arms only.

**UNREACHED, each with its argument** (note §4.3a):
- T1 row 0 `forcing`: no well-formed compile fails a forced ask. The
  witness is a designed `alloc_check` W5.
- T1 row 1 `nomem`: the witness is `alloc_check` W4 (S259) via `make alloc`.
- T1 row 2 × size: structural; the caps refuse only on the default or final
  attempt.
- T1 row 2 × overflow: argued; the trial's DFA machines are built from the
  same NFA as the default attempt's.
- T1 sequence `prefilter-collapse` → `sel1-collapse`: argued, not proven.
  The attribution walk and the legal-sequence invariant cover it.
- T1 sequence `sel1-collapse` → `prefilter-collapse` (critB1 m2): needs
  F-B3's state, which was 0 in 60 runs, with an argument for why.
- T2 row 5 (`nullable-collapsed`) at SIZECAP: structural. Rev 1's sabotage #3
  is therefore re-witnessed at SEL1 scope.
- T2 row 6 (`overflow-drop`) at SIZECAP: the m2 sequence.
- T2 rows 1/2/3/9 off NONE, row 7 at SEL1, row 8 at SEL1, row 10-off off
  NONE: structural, each with its reason in the table.

**The prototype also checked the tables' content.** It computed T2's
verdict and listing, T3's PFLW and the attribution walk from the note's row
lists alone, and compared them with today's probes, stamps and `--emit-ir`
on every compile: 0 mismatches. The run-time invariants hold:
- 1,104 `has_var` admissions, none with a rung or `dd`;
- 1,303 `sel1-drop` compiles, none with a surviving prefilter;
- 1,902 compiles with a [SEL-1] row, none with a size row around it;
- no `once` row fired twice;
- at most 9 attempts, against a bound of 25.

The plain probed build's stdout and rc matched `build/pcrec` on all 4,810
first-run cases.

## Findings (beyond the brief's inputs)

- **F-B5: `--pattern-esc` is ignored by `--emit-ir` and `--emit-facts`.**
  - `cli/main.c` returns from both branches (`:1988`, `:2021`) before the
    escape decode at `:2359`.
  - So the listing describes the RAW escaped text, with rc 0. `--pattern-esc
    --emit-facts=byte --pattern '"\x28a\x29b"'` lists `RX_ENGINE "dfa"`,
    while the `.c` compile of the decoded `(a)b` is `vm`.
  - It was found because the prototype first reused decfb0's
    `--pattern-esc` argv and its listing check failed on 558 cells.
  - **Recommend a K-entry.** It is a caller-observable listing defect. This
    lane did not file it, because known_issues.md is the manager's.
  - B0's streams must hand decoded bytes. emit_sweep already decodes.
- **A trap in my own first census.** `printf … | grep -q` under `pipefail`
  dropped names silently: grep's early exit SIGPIPEs the printf. The fix is
  a here-string, and the script's comment records it.
- **The derived census's noise is structural and named.** Class 5 is the
  same member spelling on another struct (`r->engines`, `pf->why`). The
  receiver tells it apart. Matching EngineFit members only through a `fit`
  receiver would lose the VmState copies (`st->prefilter`) that the listing
  chain reads.
- **critB2's "`fit.prefilter` in ir/nfa.c" is a string, not code.** The
  derived census does not list it. Nothing is lost.
- **The trial catch's line occurs three times in `src/`.** So it cannot
  enter the edit set, because the script matches a line everywhere. No anchor
  names any of the three, so the omission moves no re-aim.

## Owed

Nothing from this lane. The build lane is the manager's to launch once
Frank answers Q1, Q2 and Q4(b), and it starts with B0's eleven deliverables.
The prototype scratch (`build/decfbrev2/`) is not committed. It regenerates
in about 12 minutes at `-j6` (see `reach/CLAUDE.md`).
