# stream2 report: "one instruction stream", round 2 revision

Lane stream2 (opus), 2026-11-01. Brief: revise the round-1 synthesis per the crit-stream1 rulings
and the owner's criteria F1-F4, commit it as a design document, and keep the round-1 inputs
beside it. Design text only: no build, no suite, no queue job.

## Deliverables (branch lane/stream2)

- `docs/design/stream/approach.md`: REVISION 2, PROPOSED (about 68 KB, mostly tables).
- `docs/design/stream/round1/`: `COMMON.md`, `clean.md`, `today.md`, `prior.md`, `synth.md`,
  copied verbatim from `$PCREC_TMPDIR/scratch/stream/`, with their own CLAUDE.md.
- `docs/design/stream/CLAUDE.md`, and one index line in `docs/design/CLAUDE.md`.
- This report, plus its entry in the lanes history index.

## What changed from rev 1

- **Goals first** (§0): F1 focus, F2 flexibility, F3 division of labour, F4 no blindness, in the
  owner's order, each with a measurable form that can fail. Speed is a gate (G0), not a benefit.
  The verified two-engine cost is in §0.1: 66 of 207 code-bearing merges since 2026-09-01 (32%)
  touched both emitters, 70% touched the pair; 30,209 emitter lines (31%); the engine taxonomy sits
  in the kit's public header.
- **Part table** (§2): seven parts, each with a contract, a test boundary, its OWN oracle and an
  owner. Each admission row is a sub-part. The F1 claim is a two-part check: the diff touches no file
  of P3/P4/P5, and the stream listing of every pattern the row does not admit is unchanged. PART vs
  controller resolved: one composition home (P5), no `PART` kind.
- **Record level** (§3): no record carries target text. The D182 records' C-level spellings are
  named as a migration item, with the stream interpreter (PLAN) as the rule's test.
- **Two-way seam** (§4): the run-time hand (`pos` typed per coordinate, `slots`, `proof`, `reentry`
  = none or a frame, `effects`, `codes`), and the plan-time CARD (accepts, demands, proves, fixed
  span, consumer class, give-up contract, reads), each field mapped to today's backward channel by
  file:line. [LANDWALK-PRES] and [CAND-SPAN] are worked as card reads.
- **Admission table** (§6): the definitions every row uses (ambiguous, polarity, the backref
  superset, the capture conjunct, the fold, the one superset owner `Nfa.erased`); each row with its
  full conjunct list, source rows, argument, witnesses and status; then profitability, give-up
  contract (D158), lever class and kind per row; maximality with forced and declared departures only.
  Rows 15 and 16 are marked UNSOUND AS STATED; row 17 is struck into G.
- **Premises corrected** (§7): X1-X17 recounted (7 pairs, 2 analysis-only halves, 1 family, 7
  already single), the 28 engine-verdict readers, and a correction row for each of C2-C14.
- **Kinds** (§5): `TAGGED` restored to the mark distance; STATE, ONEPASS, THREADS, GUIDED, MEMO as
  HELD kinds with triggers; one `RX_ENGINE` rule (no choice or barrier record reachable) that keeps
  today's values, with its three spec readers.
- **Consumer kind** (§8): kept and re-expressed by behaviour (proposed names, the kit confirms); a kit
  abi event; a one-to-one re-key of the measured rows.
- **Non-goals** (§9): other dialects and set APIs, each with its general form and trigger; the
  losses; the two fully built end states head to head on F1-F4.
- **Census** (§10): the scensus numbers, bench before corpus, used where a claim needs a population.
- **Measurements and proofs** (§11): every proof after lane/p1build merges, against a post-p1build
  baseline; one comparator (`scripts/emit_sweep.py` with the `IDENT_*` arm set and a frozen manifest);
  order P-c, P-b, P-d (P-a folded in, one renderer body, after [VMREC] (b)); P-e, P-f and P-g held
  (P-f a consumer of [CAND-SPAN]). The D182 (c) timing note is declined, keeping only the
  host-neutral constraint.
- **Changes map** (§14): every finding id, its ruling and the section that carries it.

## Findings not fully fixed, and why

- **A2, A13 (row 14), A4 (duplicate names, `(?|`):** these need PCRE2 facts that only its code has.
  The rows are marked UNSOUND AS STATED or HELD, and the questions are asks below (D181).
- **A7, the counter half:** the extra state exists (counter rungs, guard slots), but no conflation
  witness was built. That needs a prototype memo, which is a build. Row 16 is HELD with the key
  stated.
- **B6 (the interpreter), D3 (the comparator), C13 (per-entry demand):** these were ruled PLAN, so the
  document names each with its trigger and builds nothing.
- **§8's behaviour names:** the names are proposals. The kit confirms them, and the request is the
  manager's to file when the first proof moves a kit byte.
- **Length:** about 15 pages of mostly tables, a little over the 10-14 aimed for. §0-§2 hold the end
  state; the rest is reference.

## Asks for the manager

1. pcre2-reader note (A2, A13): "After an iteration of an unbounded repeated group that matched the
   empty string, does PCRE2's interpreter ever start a further iteration (including when it is the
   m-th mandatory iteration of X{m,}), and are captures set inside that empty iteration kept in the
   reported match?"
2. pcre2-reader note (A4): "For a backreference to a duplicate group name, or to a group number
   inside a `(?|` branch reset, which group's capture does PCRE2 compare against when several are set
   or some are unset; and under PCRE2_MATCH_UNSET_BACKREF does an unset referent match the empty
   string in every case?"
3. Land the four review lessons in `docs/dev/guide/critics.md` and the owner-criteria lens row in the
   critic skill (ruled; outside this lane's scope).

## Validation

- Design text only. No compile was needed: every code claim is a crit-stream1 verifier result or a
  file:line I re-read at f574eab2d (CandRow fields, `cand_nodes` asks and reads, the
  `table-read-cycle`/`table-ask-unread` checks, the `mf_ask` calls, `cand_project`, the consumer-kind
  enum and finder gate, the callout erasure, the D164 tagged machine, `iter_retry_rows`,
  `callsite_rows.c`, `pcrec_vm_prefilter_window`, possessify's rule header, the CG contract enum).
- `tests/spec_history/run_spec_history.sh` with ROOT_DIR = the worktree, after staging the new
  files: checks passed 187, failed 0; hook self-test 11/0. Every docs/spec cite in the new files
  resolves, and none is a line cite.
- Pre-commit: staged checks 52/0 and claudemd size within limits on each commit.

## STATE AT HANDOFF

STATE: delivered. Branch lane/stream2, commits 6f0bbf7a8 (round-1 copies), c8c2bf716 (WIP §0-§4),
44c512807 (rev 2 complete), plus this report's commit. Rulings file `stream2_rulings.md`: no entries
(last read just before this report: "(none yet)"). Nothing is owed: no run was launched. A fresh
agent resuming this work starts from `docs/design/stream/approach.md` §14 and the asks above.
