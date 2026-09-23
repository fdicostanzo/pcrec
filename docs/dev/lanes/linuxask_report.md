# linuxask — I-89 draft (2026-09-22, lane linuxask, sonnet)

Delivers `docs/dev/optloop/linux_ask_i89.md`, an exact-command executor
bundle for pcrecdev2, modeled on I-85/I-87's register (read
`inbox_from_pcrec.md` lines 2529-2567 and 2571 on for that voice). Docs
only; built pcrec on darwin (`make -j4 CC=gcc-16`) and ran small probes to
VERIFY every command in the draft, per the brief's allowance — nothing
under `src/`/`cli`/`lib/` committed.

## What was verified, not assumed

- **Pin**: `git diff --stat 8d716693..HEAD -- src lib cli` on main
  (`65bb94b7`) prints nothing — confirmed docs-only-on-top before the
  worktree was even created.
- **The three new axis flags** (`-fno-vm-anchor-bound`, `-fno-end-window`,
  `-fno-req-byte`) — grepped `src/core/axes.def:156-158` directly rather
  than trusting the brief's spellings.
- **`Makefile:1483`** is `test-axes: all` → `run_axes.sh` +
  `run_form_census.sh`, exactly as cited.
- **`run_axes.sh`'s output shape** (per-axis `agree=/budget-bound=/
  refused-documented=/lost-other=/mismatches=/gained=` line, final
  `run_axes.sh: all axes answer-identical...` line) and
  **`run_form_census.sh`'s** (`checks passed:`/`checks failed:`) — read
  directly out of both scripts, not paraphrased from `docs/testing.md`.
- **The "24,343/24,343 agree" figure** — traced to `dev_journal.md:25019`,
  confirmed it is the RESTRICTED (three-axis) run's own number at this
  exact pin, not a stale figure from an earlier corpus size.
- **The 17-pattern population for M-B** — re-derived by filtering
  `capsurvey_census.tsv` on `RX_VM_PREFILTER=="hybrid"` AND
  `RX_ENGINE_WHY` containing `"capture group"` myself; got exactly the 17
  names `onepass_census.md` §4 lists, in the same order. Confirmed all 17
  `.rx` files exist in `pcrec-bench/bench/capability/patterns/`.
- **`[OPT-FIRSTSET]`'s F1/F2 build shape**: built pcrec, compiled
  `wild-codegrammar-json-constant` with `--features all --no-captures -p
  rx`, and grepped the real emitted `.c` for `rx_can_begin_match`,
  `forward_state`, `rx_forward_seed_state`, `rx_forward_byte_class` — all
  four names match `firstset_design.md` §3/§4's illustrative code
  verbatim. Wrote and RAN both Python patchers (array rewrite for the
  twin; the two-line reseed insertion) against the real artifact; both
  succeeded with their assert guards intact.
- **Block C's build shape** — smoke-tested `codegrammar-flat`'s ARM1
  (`--features all`) and ARM2 (`--features all --no-captures`) compiles
  and links, and confirmed `expectations.tsv`'s `search_short`/`match` row
  lookup returns a real subject id (`cg-key-colon`) via the `awk` one-liner
  in the draft.

## The one finding worth the manager's attention before I-89 ships

**F2's stated EXPECT is not what this lane measured.** Built and RAN the
real `base_`/`twin_`/`reseed_` binaries for `wild-codegrammar-json-constant`
on darwin (a verification step, not the timed ask — this document does
not claim a Linux timing result). `firstset_design.md` §4.1 states
`matches=0`/`1`/`0` (base/twin/reseed) on `"atrue xnull "`, reproduced
there via `c2/scanloop_sim.py`, a Python replay of ONLY the forward-scan
tables. This lane's compiled binaries all three read `matches=0`. Reading
the real `rx_search` body explains why: it is two-pass — the forward
loop's `last_accept_position` is only a candidate end; a REVERSE walk
independently re-derives the match start from `rx_reverse_*` tables the
`rx_can_begin_match` patch never touches, and on this witness it correctly
finds `"atrue"`'s leading `\b` fails and never sets a start, vetoing the
forward pass's spurious accept. The simulator's forward-only model and
the compiled two-pass artifact disagree on this exact witness.

I did not silently correct the design note or drop F2 — the draft states
both readings, asks the Linux executor to report the raw triple exactly
as measured regardless of which way it points, and flags either outcome
(`0,0,0` confirming this lane's darwin finding, or `0,1,0` confirming the
note) as something for the manager to reconcile against
`firstset_design.md` §4 before treating F2 as settled. This may not mean
the underlying context-loss claim in §4.2 is false — only that this
particular witness, run through the REAL two-pass engine rather than the
forward-only simulator, does not demonstrate it end to end.

## `[derived — manager to confirm]` items

1. The `twin_`/`reseed_` Python patchers (array rewrite; two-line reseed
   insertion) — verified against the real artifact by this lane, not
   merely transcribed from the design note's illustrative C.
2. The mapping from `captures_via_dfa_survey.md` §3.6's "each pattern's
   own `match`-regime subject" wording to `expectations.tsv`'s
   `search_short`/`match` rows — `expectations.tsv`'s only two `regime`
   values are `search_short`/`throughput`, so this is the closest
   candidate but is not a verbatim match to the survey's phrasing.

## Open questions for the manager

1. **F2 above** — which reading does Linux confirm, and does it change
   whether F2/F3 should ship at all.
2. Confirm the `search_short`/`match` regime mapping for block (C)'s "own
   subject" (item 2 above) before treating those four-subject-per-pattern
   numbers as settled.
3. The predicted "likely O-45" numbering for I-87's done-signal in block
   (A)'s ordering note is a guess from the O-43/O-44 pattern, not a fact —
   edit freely when you know the real number or ack line.
4. `bench/capability/subjects/` (gitignored) was absent in this lane's
   read-only pcrec-bench checkout, so block (C)'s "own subject" reads
   could not be smoke-tested end to end here (only the `SID` lookup and
   the ARM1/ARM2 compile were). It should exist on ubuntubudu from the
   executor's own prior capability-set work; the draft handles the
   absent case by asking to report MISSING rather than regenerating (that
   would write into pcrec-bench).

## Validation

`make -j4 CC=gcc-16` clean on this worktree at `65bb94b7`. No suite run
(docs-only; nothing under `src/`/`cli`/`lib/`/`tests/` changed). All
commands above independently exercised on darwin as probes, not as the
timed Linux ask itself.
