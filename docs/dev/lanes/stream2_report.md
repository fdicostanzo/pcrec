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

## State at the rev 2 handoff (superseded by the rev 3 section below)

STATE: delivered. Branch lane/stream2, commits 6f0bbf7a8 (round-1 copies), c8c2bf716 (WIP §0-§4),
44c512807 (rev 2 complete), plus this report's commit. Rulings file `stream2_rulings.md`: no entries
(last read just before this report: "(none yet)"). Nothing is owed: no run was launched. A fresh
agent resuming this work starts from `docs/design/stream/approach.md` §14 and the asks above.

---

# Rev 3 (lane stream3, opus, 2026-11-01): the crit-stream2 fixes

## Deliverables (branch lane/stream2, continued)

- `docs/design/stream/approach.md` REVISION 3. Every crit-stream2 FIX-NOW fixed, every DOC carried;
  §14.1 maps each round-2 id to its section (§14.2 keeps the round-1 map).
- The review records: `docs/dev/reviews/2026-11-01-r2-stream2.md` (the coordinator's review.md
  plus "## Rulings (manager, 2026-11-01)" appended from RULINGS.md) and
  `docs/dev/reviews/2026-11-01-r2-stream2/` (COMMON, card, fixind, owner, sound, verify, and
  `.coord/process.md` as process.md). Plan line cites stripped with the PL14 sed (0 left).
  Indexed in `docs/dev/reviews/CLAUDE.md` after the r1-stream1 entry.
- The accepted process change: `.claude/skills/pcrec-critic/SKILL.md` §4, the fix-induced row, now
  ends "Quote the DEFINITION, and trace every reader, of any existing record a fix names as a
  fact's home (2026-11-01 r2 stream2: `Nfa.erased` gaining `\K`/`\G` flipped exact windows)".
- `docs/design/stream/CLAUDE.md` and `docs/design/CLAUDE.md` name rev 3 and the review records.
- main merged into the branch first (841cbc65f; docs only), so the reviews index and the critic
  skill take main's r1-stream1 state. One append-only conflict in
  `docs/dev/history/claude_md/docs__dev__lanes.md`, resolved by keeping both entries.

## D1, the centrepiece: F1's check, run (approach.md §2.2-§2.4)

- **The map** (§2.3): a declared file-to-part table for main f574eab2d (lane/p1build where named),
  from file headers and function names. Four files straddle parts: `emit_dfa.c` (P2, P3, the kit
  seam, the abi number), `emit_vm.c` (P2, P3), `compile.c` (P2, P5) and `internal.h` (every part),
  43,273 lines together.
- **The restated claim** (§2.2): a new row changes P2's files plus a declared satellite set S
  (S1 lever row and bit, S2 spec hunk, S3 abi line, S4 its pins and the re-aim of displaced
  witnesses, S5 a Makefile line), each an append of a declared shape. Cross-part list extended
  with a new IR fact (P1+P2) and a new kit-site id. Check (b)'s byte form can never pass for a
  byte-moving row (S3 moves every provenance line), so (b) is on the stream listing.
- **The replay** (§2.4), from `git show --stat` and `git diff -U0` hunk contexts:

| change | today | end state |
|---|---|---|
| 02229045e [REQRUN-VM] | FAILS: P3 in `emit_dfa.c` and `emit_vm.c`, ladder rung `drop-handoff`, `Job.req_handoff_vm`, abi 90→91 in a P3 file | PASSES after X-0..X-3 and X-5, IF FIND takes the K-back `LOWER` position as an operand |
| 00c97769e [REQ-HANDOFF-L1] | FAILS: two new IR facts (P1), P3 text writers, abi 74→75 in a P3 file | a CROSS-PART event (new IR fact), correctly classified, not passed |
| lane/p1build walk | FAILS: `emit_landmark_walk` (P3), `DELEG_SITE(LMHIT)`, rung `drop-landmark-walk`, `internal.h` +77, abi, Makefile | PASSES after X-0..X-5, IF the walk renders as existing kinds (P-d's own criterion) |

- **Honest summary:** 0 of 3 pass today. F1 is met only after the stream's own split (X-0) and five
  satellite splits: X-1 the abi number to a P6 file, X-2 the size-cap ladder as a row field
  (no rung per row), X-3 the emitter-to-driver `Job` flags as P3 card facts (`size`), X-4 the
  kit-site key by (operation, `row`) (the kit's to confirm; a kit abi event), X-5 population pins
  keyed by `row`. Check (b) was NOT replayed (a corpus sweep, not allowed in the evening hold).
  Control case: [SCANEDGE-SET] 002810cac is a contract event by the list (as OWNER found).

## The other named rulings

- **C1:** §4.3 closes [LANDWALK-PRES] through [CAND-SPAN]: the walk reads FIND's `proves` at +1
  (the byte 'x' after '@') before its rewind, no pricing. The rarity-of-both form is dropped, with
  the reason (unigram rarity is mass('@') twice); the priced PRESENT form is a held unlock
  (trigger: a joint-rate fact AND rulepilot's verdict).
- **D3:** §0 F3, §2 (each part's oracle cell says "none of its own yet" where it is so, and a
  paragraph "F3, stated plainly"), §3 and §9.2 state that F3 is NOT met until the interpreter and
  an IR-level executor exist; F3 is added to their triggers.

## The PCRE2 notes, as used

- `backref-referent-choice.md` §2-§4 → §6.0's backref superset: the referent's CAPTURED language
  under the referent's fold, closed under the backref's fold when the backref is caseless (A5,
  witness `(?i:(a))\1` "AA" (0,2)); duplicates = union (first set group wins); branch reset = one
  slot; ε only when every referent may be unset and MATCH_UNSET_BACKREF is on; a circular referent
  widens to Σ* (A8).
- `empty-iteration-captures.md` → §6.0's empty-iteration rule, rows 14 and 15 (A2/A13): mandatory
  copies run; an empty iteration beyond them ends the loop on that path and keeps its captures.
- §13's two asks are marked ANSWERED.

## Judgement calls a reviewer should check

- **B1's second fact.** The report/position shift is a P1 fact read by the consumer's `demands`
  (rev 3 §4.1); rev 2's "one source" is gone. Today it exists only as lmwalk `g1`'s kind tests.
- **B2's budget rule** keeps D49's one existence gate rather than per-kind stamping; kind rows say
  only where a counter is charged (CUT and a frameless SKIP charge WORK).
- **The F1 satellite set S** is a design choice (the alternative was "P2 only", which none of the
  three passes even in the end state, because every byte-moving row bumps the abi). A reviewer may
  prefer a narrower S.
- **X-4** (kit-site key by row) touches Q-R10-6's per-site countability; the design keeps
  countability through the key, but it is the kit's to confirm.
- **§8's rename** of `HYB_PF` became `GATE_THEN_BUDGETED` (rev 2's `PREFILTER_BUDGETED` named a
  method, C12); the case for the rename is now F2, not D174.

## Validation

- Design text only; no `make`, no suite, no queue job (the owner's evening hold). No compile was
  run in this rev: every witness the text adds is one the crit-stream2 verifier re-ran (pcrec and
  python `re`, `review/verify.md`), or one the two notes record as confirmed against libpcre2 10.46.
- The replay's facts were read with `git show --stat`, `git diff --stat` and `git diff -U0` hunk
  headers on 02229045e, 00c97769e and `main...lane/p1build`; line counts with `git show main:F | wc -l`.
- Pre-commit staged checks passed on every commit (52 checks); `check_claudemd_size` within limits.
  `grep -E 'plan\.md:[0-9]'` over the copied review files: 0. No `docs/spec` line cite in the
  design (`grep -E '(match_api|tuning|limits|cli|measures)\.md:[0-9]'`: 0).

## STATE AT HANDOFF

STATE: delivered. Branch lane/stream2: 841cbc65f (merge main, docs only), 66de059f4 (review r2
records, reviews index, critic skill row), d2cb8c163 / a41b25954 / ac7ae3e80 (rev 3 WIP),
b1ad33cf5 (rev 3 complete, CLAUDE.md indexes), plus this report's commit. Rulings file
`stream2_rulings.md`: no entries (last read just before this report: "(none yet)"). Nothing is
owed: no run was launched. Next per the rulings: round 3, two critics (soundness + fix-induced) on
rev 3. A fresh agent resuming starts from `docs/design/stream/approach.md` §14.1 and the
judgement calls above.
