# s2a: [OPT-LITSCAN] S2a, the VM's exact literal run as P4 (lane report)

Lane `s2a` (opus, engine code), 2026-09-27. Branch `lane/s2a` from main
`b0b9f0fa` (abi 40), **NOT merged**. One abi event, **40 -> 41**. Charter:
`docs/design/patfacts/design.md` §8.2 (+ §4.3), `docs/design/compare_stack.md`
§6.1 S2 / D3, `docs/design/litscan_s1.md` (P4), D122 + addenda, D94.

## 0. Summary

- **The fact**: `pcrec_lit_run(el, n, j, out)` (`src/core/cpset.c`, declared
  in `internal.h`). It is ONE pure node-grain function. It returns the
  EMISSION-contiguous run of two or more consecutive spine elements that are
  each `A_CLASS` and `pcrec_cls_single >= 0`. The `A_CLASS` guard is part of
  the definition (`lit_byte`). It reads no `A_CAP`/`A_ATOMIC`/`A_LOOK`/`A_REP`,
  keeps no memo and has no epoch. It adds no third singleton spelling (D3): it
  calls `pcrec_cls_single`.
- **Three readers, one question**:
  - `vm_cat` (emission), `vm_cost_cat` and `vm_count_slots`' `A_CAT` arm all
    ask `vm_lit_run`, a VM wrapper that applies the deny;
  - all three walk the same element array (`vm_cat_flatten`), and a run is
    skipped as one element.
- **Emission** (`vm_lit`): one label, then
  `if (scan_position + L <= subject_length && !memcmp(subject + scan_position, "<run>", L)) { scan_position += L; goto next; }`.
  The compare is written by **P4 itself**: `emit_exact_compare` became extern
  as `pcrec_emit_exact_compare`, and there is no second emitter. The P8 guard
  is one `pos + L <= n` test, so the compare never over-reads.
- **The island arm** keeps its own recognizer (the trie), sharing only P4. In
  `vm_isl_emit`, a node's single-child chain, down to the first node that
  branches or accepts, is ONE P4 compare at the node's depth. Swallowed nodes
  take no label.
- **EXACT only**. A `(?i)` letter is a two-member class and ends the run; the
  mask compare is S4's. **Untouched**: the backward walk (`vm_rev_emit`) and
  the cursor rung's fixed-length `&&` chain.
- **Budgets (the D51 sentence, `docs/spec/limits.md` §3.1)**: a run is charged
  as **ONE compare**, which is what the chain was charged:
  - **Steps** count backtracks, and forward progress is free. A mismatch
    anywhere enters the fail label once, as the chain did, so the step count
    is unchanged. Charging `n` would make steps count forward bytes, which D51
    never did.
  - **Work**: an island's die charges the depth proved before the failed
    compare, so the charge can only drop and a give-up can only move later.
  - **Node budget**: pays one node per byte, so `PCREC_MAX_VM_NODES` refuses
    the same patterns as before.
- **Axis**: `-fno-lit-run` (`PCREC_NO_LIT_RUN`, bit 33) + `<PREFIX>_VM_LIT_RUNS`.
  **ADDED DURING THE LANE, PENDING THE MANAGER'S RULING** (asked mid-lane,
  see §6). The denied program is main's byte for byte, past the one new stamp
  line (verified by `diff` on three witnesses).

## 1. Commits

| commit | what |
|---|---|
| `242cc5ef` | the fact, the three readers, `vm_lit`, the island arm, P4 extern, `<string.h>` via a new `pcrec_emit_prologue` parameter; S279 re-anchored (rename only) |
| `f9df48ab` | abi 40 -> 41, `ABI_EXPECT`, spec hunks (limits §3.1, tuning §2.31, ir_listing `compare` op, match_api §6), `tests/litscan/` corpus, S304/S305 |
| `f97c26a6` | `-fno-lit-run` + `<PREFIX>_VM_LIT_RUNS` (last `src/` commit), recursion-identity (A) third deny axis |
| `7b8873d2` | CLAUDE.md for every directory whose roles changed; `docs/dev/optloop/s2a/s2a_movers.py` |
| (after) | ir-listing baselines re-captured; recursion identity (B) re-pinned to `f97c26a6`; axes coverage, rxtsource census and cpset manifest re-pinned (§4); mech verdicts; chain + report |

## 2. Movers manifest (what moves, and why)

Instrument: `docs/dev/optloop/s1/s1_identity.py`, reused unchanged:
- BASE = main `b0b9f0fa` (built from `git archive` in scratch), NEW = `242cc5ef`
  + the abi bump;
- abi normalized 40 -> 41;
- populations: pcrec-bench's capability patterns × 4 configs (256), and every
  corpus pattern × {auto, `--engine=vm`} (6,438).

| population | identical | changed | refused (both) | refusal-mismatch |
|---|---|---|---|---|
| bench | 186 | 63 | 5 | 2 |
| corpus | 4,705 | 1,018 | 715 | 0 |

**The movers are exactly the run population.** `docs/dev/optloop/s2a/s2a_movers.py`
recompiles every record with NEW and checks the biconditional "moved IFF the VM
program writes a run compare":

| | writes a run compare | writes none |
|---|---|---|
| **changed** | 1,081 | **0** |
| **identical** | **0** | 4,891 |

Stamps that moved, over the 1,081:
- `RX_VM_PROGRAM_BYTES`: all 1,081. It is the program's size.
- `RX_VM_ENTRY_SHAPE`: 3 corpus artifacts under `--engine=vm`
  (`frank|fred|brad|bobby|janet`, `foo(?:username|password|passphrase)bar`,
  `^(?(DEFINE)(?<g>ab))(?&g)(?&g)(?&g)$`). The smaller program now fits the
  inline rung, "shared" -> "forward", which is the entry-shape axis's own
  answer-identical choice.
- `RX_VM_PREFILTER_LANG_WHY`: 1 bench pattern
  (`wild-logparse-syslogbase-expanded`). The quoted byte count of the failed
  exact attempt moved: 1,464,588 -> 1,462,063.

No other stamp moved, so no size-term K choice and no island decision moved.
The island estimates are deliberately left as fitted on per-byte chains
(D77: refit on a measured need).

**The refusal-mismatch is an ACCEPTANCE mover.**
`wild-datetime-datefinder-alternation` under `--engine=vm` (caps and nocaps)
was refused at abi 40 (666,632 B of code against the 500,000 cap). It compiles
at abi 41 with 482,736 B. Its answers are checked against the same compiler's
auto artifact (§5, OWED).

With the axis (after `f97c26a6`), every VM artifact additionally gains the
`<PREFIX>_VM_LIT_RUNS` line. So the whole-file mover set becomes every VM
artifact, and the PROGRAM movers stay exactly the 1,081 above.
`run_recursion_identity.sh` (A) holds this per artifact against the deny axis
(§4).

## 3. Sabotage rows (S304, S305; next free id was S304 on main)

- **S304** `lit-run-one-byte-too-long` (`src/core/cpset.c`): the fact claims
  the element after a run. The emitted compare gains a 0xFF byte and the
  swallowed element is never emitted. Arm: `harness` on
  `tests/litscan/litrun.rxt`. Expectation: DETECTED.
- **S305** `lit-run-slot-walk-overskips` (`src/gen/emit_vm.c`,
  `vm_count_slots`): the slot walk skips one element past each run, so its
  view disagrees with emission (R5's defect). Arm: `irlisting`. Its witness is
  `xy(a|ab)c`, added to `run_ir_listing.sh`'s sweep: the pre-pass counts 0
  resume points against 1 emitted, which the check reads as an under-count.
- There is no cost-walk twin: a run costs nothing, and the element after it
  was not seen to move any stamp on the witnesses tried. This is recorded in
  S305's header.
- **MEASURED, single-row mech at `b04e7ab3`: both DETECTED and REACHED.**
  - S304: `reach:ok(1/1)`, `corpus:4fail/83pass`.
  - S305: `reach:ok(1/1)`, `irlist:2fail/153pass`.
- S267 (P4's sense inverted) and S279 (P4's offset) now also plant into the
  VM's compares. Re-running them is OWED in the chain.

## 4. Suites that count (D94), run by the lane

- `run_recursion_identity.sh` with (B) pinned to `f97c26a6`: **16/0**.
  - (A) moves on purpose, excused by the deny axis. The deny set is built from
    the stamps, and `-fno-lit-run` is always in it: a denied island is emitted
    as `vm_alt`'s chain, whose literal branches become runs the island artifact
    never had (`(?!ab|cd)z`, measured red on the first run).
  - `litrun-moved`: default 335, vm 534. Both converse directions read 0.
  - `LIT_PATTERNS` is the manifest. `(abc){2}x` was dropped because it takes
    the cursor rung.
- `run_ir_listing.sh`:
  - 4 baselines moved and 1 is new (`xy(a|ab)c`). All were re-captured and
    reviewed as diffs.
  - Each change is a consume chain -> one `compare` row, plus the label
    renumbering and one island die's work-charge note that a swallowed node no
    longer writes.
- `make test-codegen`: **all green except the one accepted red** ("FAIL: nm
  could not read arm_a.o"). This includes `run_codegen_tests.sh` (the abi pin
  at 41, with its narrative extended), `run_size_term.sh` (the cap-rescue
  reference did not need to move) and `run_facts_checks.sh`.
- `make test-registry`: red on ONE pin, `axes_registry_check` coverage
  135 -> 138. That is `-fno-lit-run`'s (macro, bit, flag) triple, verified
  line by line. Re-pinned; the verdict is owed in `make test`.
- `make test-rxtsource`: the census moved by exactly the new corpus file,
  +1 file / +19 blocks / +87 lines. Re-pinned (CENSUS_* and RUNSH_*), then
  re-run: **0 failed**.
- `make test-resource`: **green**. The `a{5,25000}` rescue pin did not move,
  because the pattern is DFA-routed.
- `make test-cpset-structure`: the manifest drifted on 5 VM rows, and each was
  reviewed by a same-basename diff against main:
  - 4 moved +25, which is the `RX_VM_LIT_RUNS 0` line;
  - `(?<=foo)bar` moved -569, from its stamp plus `foo`/`bar` collapsing to
    two compares.
  - Re-recorded, then **28/0**.

## 5. Answer/give-up identity and read safety

- Before the abi bump, `tests/harness/run.sh` passed **6,713/0** over island, vm,
  base, captures, utf8 and backrefs. `tests/litscan` passes **87/0**.
- OWED (chain):
  - `tests/findings/b1_mover_answers.py` (reused) over all 1,081 movers:
    span, every capture and the give-up surface, at every startpos,
    base vs new;
  - the same run under `-fsanitize=address,undefined` with
    `-DDIFF_EXACT_SUBJECT` (a subject in a block of exactly its length) and
    `PREFIXES=1` (subjects ending inside a run). This is the S1-1 guard
    lesson;
  - the acceptance mover's differential;
  - `make test-axes AXES=-fno-lit-run`.

## 6. Open ruling

The brief said "no deny". My reading: design §8.2's "no deny" is the
pattern-facts record's deny (§0 item 9, [r1 A6]), not an optimization axis.
D122 addendum 2 (4) makes every kit form choice a row with a deny flag.

Without the axis, recursion identity (A) has no honest excuse for S2a's region
moves. The axis is its own commit (`f97c26a6`), and the manager was asked. If
the ruling is NO, the alternative is a mechanical-rewrite normalizer in (A)
(the `bref_rename_rewrite` precedent), which is fragile.

## 7. D77: the owed bench pass, predictions for relay

Not measured here. These are the cells and the direction expected:

- **ctx-lazy-*/ctx-greedy-* (bounded), level-context (loglines)**: the row's
  own named population. All are VM, with 2 islands and 7/7/9 run compares.
  - The verify path steps the context words per byte today. Each island's
    single-child chains become one word compare.
  - Expect **faster**, largest on the no-context-word worst case, where the
    full `.{0,N}` gap is walked and every position re-verifies.
  - Bound the claim by the prior 1.5-2.9× residual vs pcre2-jit: some of it is
    this.
- **wild-secrets-username-password-pair** (auto-caps, VM hybrid, 2 islands, 9
  runs) and **wild-secrets-aws-access-key-id** (1 island, 7 runs): expect
  faster throughput. The per-attempt verify is the island dispatch, and it now
  compares 3-8 byte tails in one load.
- **wild-secrets-github-pat** and **slack-webhook-url** (1 run each): expect a
  small gain at most. The hybrid prefilter hands the VM an exact window, so it
  does one verify per match.
- **email-local-nodup, tag-pair-match, nested-comment-rec,
  logparse-atomic(-removed), tag-depth3-bound, wild-logparse-quotedstring-grok,
  wild-logparse-syslogbase-expanded** (auto configs move): expect flat to
  slightly faster.
  - `nested-comment-rec` (4 runs, no prefilter, recursion) is the most likely
    to show it.
  - Watch for a **regression on 2-byte runs**. A 2-byte `memcmp` lowers to a
    halfword load plus a compare where the chain did two byte compares with an
    early exit, so on subjects that fail at the FIRST byte the new form reads
    one byte more. That is the one plausible loss.
- **`--engine=vm` only** cells (file-ext-order, keyword/router-prefix-order,
  the three wild-waf, semdiv): not in the auto ledger. Informational.
- **Null expectation**: every DFA-routed cell. S2a writes no DFA byte.

### 7.1 FACTORING × LIT-RUN, the 2×2 (added by lane s2afix for the manager)

Four configs per cell: {default, `-fno-altcls-factor`} × {default,
`-fno-lit-run`}. Factoring decides what S2a's runs ARE, so a lit-run gain
measured at one factoring setting does not transfer to the other. Stamps
measured on the lane compiler (islands / runs / program bytes):

| cell | default | `-fno-altcls-factor` | `-fno-lit-run` | both denied |
|---|---|---|---|---|
| (a) `foo.x\|foobar\|foo.` (`tests/base/alternation_trie.rxt`), `--engine=vm` | 0 / 2 / 1,357 | 0 / 3 / 1,537 | 0 / 0 / 1,955 | 0 / 0 / 2,915 |
| (a′) `wild-secrets-aws-access-key-id` (bench), auto (hybrid) and `--engine=vm` | 1 / 7 / 5,475 | 0 / 9 / 4,519 | 1 / 0 / 7,403 | 0 / 0 / 8,465 |
| (b) `wild-semdiv-dollar-trailing-newline-pcre2` = `abc$`, `--engine=vm` | 0 / 1 / 434 | 0 / 1 / 434 | 0 / 0 / 728 | 0 / 0 / 728 |
| (b′) `wild-secrets-github-pat` (bench), auto (hybrid) | 0 / 1 / 1,770 | 0 / 1 / 1,770 | 0 / 0 / 3,330 | 0 / 0 / 3,330 |

- **(a)**: the tails are not all literal (`.`), so no island takes it.
  Factoring pulls out `foo`, which leaves the runs `foo` + `bar`; unfactored,
  each branch carries its own `foo`/`foobar` run. Expect lit-run to gain
  MORE with factoring denied (3 runs, longer, each re-compared per branch
  retry) than with it on (2 runs, the shared `foo` compared once). Expect
  factoring to gain LESS with lit-run on than off: S2a already collapses the
  per-branch chains factoring used to save.
- **(a′)**: factoring does not shorten runs here. It exposes the shared `A`
  and an island takes the alternation (1 island, 7 single-child-chain
  compares). Unfactored, `vm_alt`'s chain carries nine 4-byte branch runs.
  Denying factoring gives a SMALLER program (4,519 against 5,475), so this
  cell may show factoring losing under lit-run: nine one-load 4-byte
  compares against an island's first-byte dispatch plus 3-byte tails.
  This is the cell most likely to flip the sign of `-fno-altcls-factor`.
- **(b)/(b′)** are the controls: no alternation, so `-fno-altcls-factor` is
  byte-identical (the stamps confirm it) and must read null. Only the
  lit-run column moves. (b′) is the 11-byte `github_pat_` run behind an
  exact hybrid window: one verify per match, so expect a small gain at most
  (as §7 says).

### 7.2 L-SWEEP, forced VM, each length against `-fno-lit-run` (added by lane s2afix)

The purpose is to catch a PER-CALL CONSTANT in P4's compare (LITSCAN F1):
the P8 guard and a whole-piece load are paid on every call, where the chain
exits at the first mismatching byte.

- **Cells**: `--engine=vm` on the plain literal of length L = 2, 3, 4, 7, 8,
  10, 16, 31 and 40 (for example the first L bytes of `a..zA..Z`). Each cell
  is measured against the same pattern under `-fno-lit-run`.
- **Subjects**, `rx_match` and search, each of length L:
  - the literal itself (matching);
  - byte 0 flipped (first-byte mismatch);
  - byte L−1 flipped (last-byte mismatch);
  - plus one of length L−1 (P8's guard fails).
- **Pre-checks must be denied for the failing subjects**: build with
  `-fno-req-run -fno-req-byte` as well. Under default flags, a NECESSARY run's
  failing subject is answered by the whole-window pre-check (itself a P4
  memcmp, measured: `rx_reqrun` + `memchr` present at every L) and never
  reaches the VM compare. So the default-flags row measures the pre-check,
  not S2a. Measure both rows and label them.
- **Expectations**, with the lowering facts from `docs/dev/memcmp_lowering_study.md`
  (merged on main): gcc splits a non-power-of-two L into a greedy msb-first
  chain of power-of-two pieces, each with its own load, compare and branch.
  - **Matching and last-byte mismatch**: faster from L=4 up, growing with L.
    L one-byte compares become ⌈pieces⌉ loads: L=7 is 3 pieces, L=10 is 2,
    L=16 is 2 (or one NEON), L=40 is 32+8.
  - **First-byte mismatch**: flat. The first piece fails, which is one load
    against the chain's one byte. **A small REGRESSION is plausible at L=2
    and L=3** (a halfword load and the P8 test against one byte compare),
    and that is the per-call constant this sweep exists to catch.
  - **L=31 is a named watch cell**: gcc -O1/-O2/-O3 calls `memcmp()` out of
    line there, and at no other length from 1 to 64. Expect a REGRESSION
    against `-fno-lit-run` on every subject kind, largest on first-byte
    mismatch. It is a gcc lowering cliff, not a P4 property (clang inlines
    it). If the bench confirms it, the remedy is to split a 31-byte run
    (16+15), not to bound P4.
  - **L−1 subject**: both forms fail on one bounds test. Expect null.

## TRIAGE (lane s2afix, 2026-09-27): the detached chain's reds

The chain's logs are in `worktrees/s2a-scratch/chain/`. **The brief's premise
about rcs was partly wrong.** `answers` and `asan` exited rc=1, not rc=0.
`asan-control` exited rc=0, and that is itself a RED: the control must fail.
Every finding is below, with the fix commit and the re-run verdict.

| stage | read as | cause | fix | re-run verdict |
|---|---|---|---|---|
| `answers` rc=1 | `movers 1081: identical 1077, diverged 4, skipped 0; cells compared 1119219` | INSTRUMENT: all 4 are `driver did not build`. `^${v:-}-x$` and `^a(?=${v})bc$` (auto+vm) carry `${name}`, and `possdiff_driver.c` binds no variables | `88a27f25`: the tool SKIPs a var-bearing artifact by name (`_NVARS` in the header) | 5-record probe: `movers 5: identical 1, diverged 0, skipped 4`. The two patterns answer through `tests/harness/run.sh tests/vars/{unset,basic}.rxt`: **58 passed / 0 failed** at default and under `RXTFLAGS=--engine=vm`. Net: **1,077 of 1,077 bindable movers identical, 0 real divergences** |
| `asan` rc=1 | `movers 211: identical 209, diverged 2` | the same vars instrument defect (2 records), AND the stage was BLIND (next row) | `88a27f25`, `a5a29403` | re-run with the interceptor: **`movers 214: identical 212, diverged 0, skipped 2; cells compared 861503`**, rc=0. The 2 skips are the vars records |
| `asan-control` rc=0 | `movers 6: identical 6, diverged 0` — **RED**: the plant was applied (no `PLANT-DID-NOT-APPLY`) and the sweep did not see it | INSTRUMENT, two causes. (1) gcc expands a constant-length `memcmp` inline with **no ASan instrumentation on its loads**, as `ldr` with no `__asan_load` (measured in the `-S` output). (2) Every control witness's run is NECESSARY, so `rx_reqrun` plus the attempt bound keep every attempt away from a subject ending inside the run. The plant is unreachable there even with a working detector | `a5a29403`: `-fno-builtin-memcmp` in both ASan stages (the call goes through ASan's strict interceptor, which checks all L bytes); the control reads the whole asan sample plus three non-necessary-run witnesses (`(?:abcdef\|x+)y`, `(?:abcd\|x+)(?:efgh\|y+)z`, `(?:abc\|x+)y`) | witnesses alone: plant **3/3 `AddressSanitizer: heap-buffer-overflow`**, lane compiler **3/3 identical**. Full re-run: control **RED as required**, `movers 214: identical 154, diverged 58, skipped 2`, and all 58 are ASan reports (55 sampled movers + the 3 witnesses) |
| `accept` rc=1 | `pattern too large: 1332799 bytes … (limit 1000000)` | INSTRUMENT: the reference was the auto artifact, and auto REFUSES the caps config on main and on the lane alike (the capability view's "never had a real auto-caps number") | `ee8ebf88`: the reference is the abi-40 VM program itself, `BASE --engine=vm --max-emit-code-bytes=1000000` (a raise-only cap refuses and never reshapes), plus auto on `--no-captures` | **3 pairs × 5,355 cells, 0 diverged**: vm40/vm41 caps, vm40/vm41 nocaps, auto(dfa)/vm41 nocaps |
| `axes` rc=0 | `all axes answer-identical to default (documented refusal populations excepted)`, 1906 s | — | — | GREEN as read |
| `mech-S267` rc=0 | `COMPLETE: 1 rows (… undetected: 0 …)`, `corpus:1513fail/27798pass,prechecks:18fail/283pass` DETECTED | — | — | GREEN as read |
| `mech-S279` rc=0 | `COMPLETE: 1 rows (… undetected: 0 …)`, `corpus:29fail/26pass,offsetskip:3fail/23pass` DETECTED | — | — | GREEN as read |
| `maketest` rc=2 | `sections ran: 44/44`. The only `*** [...] Error` lines are `test-codegen` and `test-tune-dial` | `test-codegen`: only the accepted `nm could not read arm_a.o`. **`test-registry` is GREEN**, so the 135→138 axes-coverage pin holds. `test-tune-dial`: STALE WITNESS. §3c's `(abc\|def)(ghi\|jkl)(mno)` was 4,244 program bytes of per-byte chains, just above `VM_INLINE_CHAIN_MAX_BYTES` = 4,096, and S2a's runs shrank it to 3,325. The arm said so itself ("VACUOUS and needs a new witness") | `bfd71516`: witness `(abc\|def)(ghi\|jkl)(mno\|pqr)(stu\|vwx)`, 5,727 bytes (6,965 under `-fno-lit-run`), chosen mid-band; +1 moves the entry chain 0 → 8 `always_inline` | `bash tests/codegen/run_tune_dial.sh` alone: **checks passed: 17, checks failed: 0** |

**No engine regression was found.** Every red was an instrument defect or a
stale witness. No manifest drift appeared, so there was nothing to classify
against §2.

**Two findings worth carrying forward:**
- **An inlined `memcmp` is invisible to ASan under gcc.** Any read-safety
  sweep over a P4 compare must build with `-fno-builtin-memcmp`, or its green
  certifies nothing. The positive control is what exposed this: it read green
  on a plant known to over-read.
- **A necessary run is SHIELDED from its own edge.** The whole-window
  pre-check and the attempt bound keep every attempt away from `pos + L > n`
  on a lone necessary run. That is why all four original control witnesses
  (`abcdef`, `x(abc)defg`, `xy(a|ab)c`, `a*bcd`) could not reach the plant.
  The real population is not all shielded: with the interceptor, the plant
  reaches **55 of the 211 sampled movers**. These are runs inside
  lookarounds, alternation branches and islands (`z(?!abc)`, `a|bc`,
  `(log|login|logout)$`, `foo(?:username|password|passphrase)bar`, ...).
  The lane compiler is clean on every one of them.

`answers` §5 expected `skipped` to be "only the 2 acceptance-mover records".
Those records are `refusal-mismatch`, not `changed`, so they were never in the
population. `skipped` is now exactly the 4 vars records.

## STATE AT HANDOFF

**Updated by lane s2afix, 2026-09-27.** The chain below RAN TO COMPLETION
(`CHAIN COMPLETE 2026-09-27 15:17:55`), and every red is triaged in the
section above. Branch `lane/s2a` is **not merged**. The s2afix commits are
`bfd71516`, `ee8ebf88`, `88a27f25` and `a5a29403`, plus this report.
**s2afix touched nothing under `src/`**, so `f97c26a6` is still the last `src/`
commit and recursion identity (B) is still pinned to it. **The manager re-pins
(B) to the MERGE**, as its precedent says.

No full `make test` re-run is owed. The only `make test` input s2afix changed
is `tests/codegen/run_tune_dial.sh`, re-run alone at 17/0. The rest of the
44/44 run stands, its only other red being the accepted `nm` probe. The
merge battery is the manager's.

The corrected ASan stages were re-run by s2afix and are COMPLETE. The log is
`worktrees/s2a-scratch/fix/asan2.log` (`ASAN2 COMPLETE 2026-09-27 15:37:31`).
- `fix/asan.log`: `movers 214: identical 212, diverged 0, skipped 2; cells
  compared 861503`.
- `fix/asan-control.log`: `movers 214: identical 154, diverged 58`, all 58
  from ASan, so RED as required.

The triage table above carries both results.

The table below is the ORIGINAL verdict spec. s2afix's amendments:
- `answers`' `skipped` is the 4 vars records, not "2 acceptance-mover records";
- `accept` now expects THREE `identical` lines;
- the ASan stages build with `-fno-builtin-memcmp`.

One detached chain ran every remaining heavy stage serially:
`docs/dev/optloop/s2a/s2a_chain.sh`. It was launched with:
- `BASE=worktrees/s2a-scratch/base/build/pcrec` (main `b0b9f0fa`);
- `NEW=worktrees/s2a/build/pcrec`;
- `JSON=worktrees/s2a-scratch/id/s1_identity.json`;
- `OUT=worktrees/s2a-scratch/chain`.

It is `nohup … & disown`, so it outlives the lane. `worktrees/s2a-scratch/`
is gitignored scratch inside the repo.

**The chain's own progress log is `worktrees/s2a-scratch/chain/chain.log`.** It
writes one `STAGE <name> rc=<n> <time>` line per stage, and **`CHAIN COMPLETE`**
is its final line. Each stage's verdict is in `…/chain/<stage>.log`:

| stage | owes | verdict is |
|---|---|---|
| `answers` | every one of the 1,081 movers answer- AND give-up-identical against main, all startpos (`b1_mover_answers.py`) | last line `movers N: identical N, diverged 0, skipped S; cells compared C`. Any `diverged` > 0 or a `FAIL` line is red. `skipped` must be only the 2 acceptance-mover records (base refuses) |
| `asan` | read safety: 200 sampled movers + the named run witnesses, under ASan+UBSan, exact-length subjects, every prefix | the same last line with `diverged 0`. A sanitizer report makes the driver exit non-zero, and that shows as `FAIL … ERROR: AddressSanitizer`/`runtime error` |
| `asan-control-build`, `asan-control` | the sweep's POSITIVE control: P8's guard planted one byte short | `asan-control` MUST be RED (`diverged` > 0 with an AddressSanitizer read past the subject). A green control means the sweep cannot see an over-read, and then the `asan` verdict certifies nothing. `PLANT-DID-NOT-APPLY` in chain.log is also a failure |
| `accept` | `wild-datetime-datefinder-alternation` `--engine=vm` (now compiling) agrees with the auto artifact | two `ACCEPT-MOVER [...]: identical` lines |
| `axes` | `-fno-lit-run` answer-identical over the whole corpus | `tests/axes/run_axes.sh`'s own verdict lines for `-fno-lit-run` (0 disagree) |
| `mech-S267`, `mech-S279` | the two P4 rows still detect, now that their plant also reaches the VM | each log's `== mech run COMPLETE: … undetected: 0 …` line |
| `maketest` | full `make test CC=gcc-16` | **make's `*** [test-X] Error` lines**, and only those. The one accepted red is "FAIL: nm could not read arm_a.o (no rx_search symbol)", inside `test-codegen`. Anything else is a real red, including `test-registry` if the 138 pin is wrong |

Owed beyond the chain:
- the D77 bench pass on S2a's own cells, with predictions in §7 for relay;
- **the manager's ruling on `-fno-lit-run`** (§6).
