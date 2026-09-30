# pfknow — [PF-KNOW] (D140) delivery report

Lane `pfknow` (fable, high effort), 2026-09-30, branch `lane/pfknow` from
`d88374d5`, worktree `worktrees/pfknow`. RESEARCH ONLY: nothing under
`src/`, `docs/spec/`, `tests/`. Not pushed.

## Delivered

- `docs/design/pf_know.md` — the note (findings, soundness conditions,
  measurements with methods, refutations, candidate rows).
- `studies/pf_know/` — `segprobe.c` (the proven-segment probe over the
  real lowered tree), `census.py` (+ the committed `census.tsv`/
  `summary.json`, 3,746 rows / 3,347 compiled at `d88374d5`), `dyn.py`
  (gcov dynamic share), `twin.py` (answer-checked hand twins),
  `gen_dense.py`, `results/` (per-cell JSON, `dyn_sparse.tsv`,
  `twins.md`), `Makefile`, `CLAUDE.md`.
- `docs/dev/plan.md`: `[PF-KNOW] STATE:started` row under the D137
  candidates list (beside [OPT-VMLIT]), carrying the findings and the D77
  trigger. `docs/dev/lanes/CLAUDE.md`, `studies/CLAUDE.md`,
  `docs/design/CLAUDE.md` index lines.

## Answers, short

**Q1.** The VM route's only per-position prefilter is the hybrid's
capture-erased DFA pair. It proves the window START on every hybrid
(`L(P) ⊆ L(erase P)`) and the END only where `Vm.mrl_win` holds (reseed
row `exact`: 569 of 1,142 hybrids; the `RX_VM_PREFILTER_LANG "exact"`
stamp reports the count-collapse axis only). Redundant VM tests = exactly
the leading (and, under `mrl_win`, trailing) fixed-width choice-free
segment: literal/class bytes, DFA-decided `^ $ \b`, U2 ctx nodes, capture
opens — nothing past a choice point. Static: 52% of exact hybrids have a
non-empty leading segment, 29% (164) are wholly implied (the one-pass
survey's trivial subset), leading = 22% of Σminw; bench: 32 of 47 hybrids
have an EMPTY leading segment. Dynamic (gcov, bench subjects): VM = 0.3-22%
of executed tests; leading = 0-38% of VM; product ≤5%. Twins (Mac,
directional, answer-identical): sparse x1.00; dense x1.13 whole-VM skip,
x1.04 44-byte caseless prefix, x1.01 5-byte memcmp prefix. Verdict: sound,
cheap, not worth a batch on its own — a member of the one-pass /
captures-via-DFA row; trigger = a match-dense bench cell with a hybrid's
VM share ≥10% of time on Linux.

**Q2.** The DFA prefilter's byte-class partition refines 114 of 118 VM
bitmaps on the 74 hybrids carrying both (the 4 exceptions: classes inside
erased lookaround bodies) — Frank's guess refuted on representation,
upheld on benefit: 3,373 B corpus-wide, two dependent loads per VM test
instead of one, and D139 already routes the scan edge through the VM's
class-form rows. [OPT-D]'s twin dedup is the real table prize (forward ==
reverse byte-class on 59/59 hybrids carrying both; 15.1 KB).

## Validation

- No product code changed; `make -j4 CC=gcc-16` of the worktree built
  clean (the census and twins ran on that binary).
- Every twin's answers hashed identical to its base over its subject
  (6/6 cells) before timing.
- The bench checkout was read only: `git -C pcrec-bench status` clean
  after the run; its generators were run with `--out` into scratch.
- No suite was run (nothing to gate; research only). Owed: nothing.

## Findings the manager may want to route elsewhere

1. `RX_VM_PREFILTER_LANG` reads `"exact"` on lookaround/atomic/`\K`
   hybrids whose END is unproven (note §2.2, §8 item 4) — a stamp/spec
   question, D76/D94 if a line is added.
2. Caseless literal runs are emitted per byte (`(c | 0x20) == k`), not as
   one compare (`pcrec_lit_run` is exact-only) — [OPT-LITSCAN] S4 /
   [WORD-FOLD] territory (note §5.3).
3. `docs/dev/optloop/capsurvey_census.tsv` is stale on one row at this
   pin: `float-literal-bound` is on the DFA now (U2 ctx nodes), not a
   hybrid.
4. The dynamic instrument's `lead` bucket stops at any span loop, so on a
   `det_all` program it under-reports; the static probe is the reading
   there (note §5.1 says so).
