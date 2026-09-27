# pf30 — [PATFACTS] steps 3.0a + 3.0 (lane report)

Lane pf30, 2026-09-26, opus, branch `lane/pf30` off main `d978a604`.
Brief: build `docs/design/patfacts/design.md` (revision 2) §9 steps 3.0a and
3.0 under D126 (Q1-Q11 yes; the §11.6 non-perturbation check HELD). Nothing
from 3.1 (B1), 3.2, 3.3 (S2a) or 3.4 was built. **Not merged.**

**Status: BUILT; the zero-movers gate is GREEN on every commit that moves
code; the heavy validation (`make test-codegen`, `make test`,
`make test-recursion-identity`, the solo mech rows) is OWED — queued in one
detached chain behind the K68 lane's box hold, logs below.**

## 1. What landed, commit by commit

| commit | what | gate (A/B emit diff vs main `d978a604`) |
|---|---|---|
| `02c4be29` | **3.0a** — `src/facts/` with `facts.h` (empty) and `facts_derive.h`; `pcrec_start_anchor`/`pcrec_end_window`/`pcrec_req_byte` declarations leave `core/internal.h`; owners + `compile.c` include it; Makefile (`LIBSRCS`, header prereqs), `include_graph.py` layer `facts` between `ir` and `opt`, CLAUDE.md files | 0 movers |
| `38585d8d` | **3.0 skeleton** — `facts.def` (6 rows), `facts.h` (ReqRun/ReqSet/`PCREC_SANCH_*` moved in, `PatFacts`), `facts.c` (epoch guard, memo, fact deny, derivation); `compile.c`'s three deny ternaries become `pcrec_facts_seal_e2`; `Job.start_anchor/end_window/req_byte/req_run/req_set` become `Job.pf` and every reader moves to its accessor in the same commit; the include-graph + link-symbol check (`tests/codegen/run_facts_checks.sh`, in `test-codegen`) with S295/S296 and mech arm `facts`; S269/S274/S276/S286/S288 re-anchored | 0 movers |
| `6f8b8a28` | check skips a STALE object whose source moved (test-only) | n/a |
| `40fdb182` | **relocation** `git mv src/opt/startanch.c src/facts/` | 0 movers |
| `dfe5bde2` | **relocation** `git mv src/opt/endwin.c src/facts/` + carve-out (d): `pcrec_end_window(const PcrecEnc *, const Ast *)`, descriptor resolved once in `facts.c` | 0 movers |
| `3a58818c` | **relocation** `rb_walk` + lattice lifted into `src/facts/req.c` (core facts `req_set`, `req_whole_run`); picks stay in `reqbyte.c` verbatim behind `pcrec_req_window`/`pcrec_req_pick` (derived facts) until B1; `ReqSet.rightmost`; S268 re-pointed | 0 movers |
| `5cbf819f` | fact-valued stamps (`REQ_BYTE`, `REQ_RUN`, `END_WINDOW`, `VM_START`) render through the facts' one renderer (Q9) | 0 movers |
| `3a9fe7a9` | **`--emit-facts`** (`src/dump/facts_dump.c`, CLI mode, `PcrecFactsHook`), the guarded force loop (Q10/A11), derivations report their `why`, decision capture (Q9), spec (`facts_listing.md` new, `cli.md` §2 + history, `table_contract.md` scope, `tuning.md` §2.25-§2.28 consumer lists + "Facts emptied" lines), checks 3-6, S297-S299 | see §2 (OWED at hand-off) |
| `f721e1fe` | `run_facts_checks.sh` bounds every compiler call ([K37] guard found 7 sites) | n/a (test-only) |

One relocation per commit (carve-out (e)): each of `startanch.c`, `endwin.c`
and the `req.c` lift is its own commit and its own gate run.

## 2. The zero-movers gate

The design's A/B emit diff, built by REUSE: `docs/dev/optloop/s1/s1_identity.py`
unchanged, driven over `{-e byte, -e utf8} × {default, -fno-req-byte,
-fno-req-run, -fno-end-window, -fno-vm-anchor-bound, -fno-run-prefilter}`
(12 runs); each run covers pcrec-bench's 64 `capability` patterns × 4 configs
(auto/vm × caps/nocaps, read-only) and every distinct corpus `pattern` line ×
2 configs (`--features all`, and with `--engine=vm`) — i.e. the design's
`--engine=vm` column is inside every run. Driver (scratch, not committed):

```
for enc in byte utf8; for deny in none <5 flags>:
  BASE=<main d978a604 build> NEW=<commit build> SCR=... EXTRA="-e $enc $deny" \
    PROCS=6 python3 docs/dev/optloop/s1/s1_identity.py
```

Per run: byte `bench {identical 249, refused 7}`, `corpus {identical 5689,
refused 715}`; utf8 `bench {identical 245, refused 11}`, `corpus {identical
5721, refused 683}` — **24 of 24 identity lines "identical/refused" on every
gated commit (3.0a, skeleton, startanch, endwin, req, renderer), zero
`changed`, zero refusal-mismatch, zero timeout.** REACH: every compiled
artifact carries the unconditional `REQ_BYTE`/`REQ_RUN`/`END_WINDOW` stamps,
so every one of the 5,938 (byte) / 5,966 (utf8) compiled artifacts per run
asked the migrated accessors. The listing commit's gate (`3a9fe7a9`'s binary,
`/tmp/pf30_scratch/pcrec_30list`) was still running at hand-off: log
`/tmp/pf30_gate_30list.log`, completion line `GATE 30list DONE`; the pass
condition is the same 24 lines with no `changed`.

**No mover of either class (§9.1) was found; no K-row filed; no abi bump.**

Also run (single scripts, allowed during the hold) on the listing build:
`run_prechecks.sh` 292/0, `run_dfa_stamps.sh` 33/0, `run_offset_skip.sh`
25/0, `run_codegen_tests.sh` 109/0 (after `f721e1fe`; it was 108/1 on the
[K37] finding below), `run_facts_checks.sh` 6/0, `make strict` clean at every
commit, `scripts/m6read_check_sab_anchors.py` all anchors resolve (306 rows).

## 3. The checks and their sabotage rows

`tests/codegen/run_facts_checks.sh` (in `make test-codegen`; mech arm
`facts`), six checks, every one with a REACH line and an empty-population
failure:

| check | oracle it does not share | sabotage | hand-verified failing direction |
|---|---|---|---|
| [facts-include] includers of `facts_derive.h` == owner list generated from `facts.def` (plain text) | the include lines vs the table's text | **S295** consumer includes the private header | facts 1 fail (this check only) |
| [facts-link] no non-owner object references an owner-defined, `facts.h`-undeclared symbol (`nm`) | the objects vs `nm` | **S296** hand `extern` + call | facts 1 fail (this check only) |
| [facts-complete] one `facts` row per `facts.def` row per encoding | the table's plain-text row count | **S297** printer skips `req_set` | facts 2 fail (+ why, see row) |
| [facts-why] every `axes.def` deny flag lists `deny:<flag>` on exactly the facts `tuning.md`'s "Facts emptied" line names | the hand-written spec (D80), not `facts.def`'s deny column | **S298** `req_run`'s deny bit flipped | facts 1 fail |
| [facts-decisions] `decisions` == the emitted file's value `#define`s (DFA, hybrid, VM witnesses; 134 stamps) | a second parser (machinery excluded by NAME here, by `(` in the printer) | **S299** `REQ_WHY` rows dropped | facts 1 fail |
| [facts-cli] 8 refusals (-o, no pattern, bad/empty encoding, other modes, refused pattern) | — | — | — |

The solo mech runs of S295-S299 (and of the six re-anchored/re-pointed rows)
are OWED in the chain (§5). The hand verification applied each row's own
`SAB_BEFORE`/`SAB_AFTER` through `tests/mech/lib/replace.py`, rebuilt, ran
the check, and reverted.

**Not built, as ruled:** the §11.6-1 non-perturbation check (A10 HELD by the
manager; the `rate` section and check 1 are B1's). No sabotage row for the
force-loop guard: no forced ask can fail today (no E2 derivation allocates),
so a row would be UNREACHED; the guard was verified by a temporary plant
(`pcrec_ctx_fail` inside the start-anchor derivation when `forcing`):
`--emit-facts` exited 0 with that row `absent`/`decline:force-failed` and every
other row intact, and an ordinary compile was unaffected. The plant was
reverted before commit.

## 4. Findings

1. **A sabotage plant that spells a signature is a reader of that
   signature.** S296 (committed with the skeleton) hand-declared
   `pcrec_end_window(Ctx *, const Ast *)`; the endwin relocation two commits
   later changed the signature (carve-out (d)), and the committed plant became
   a wild call that SEGFAULTED the compiler on VM routes rather than planting
   the defect. Caught when the listing commit re-verified every row; re-spelled
   to the current signature (NULL descriptor, so it returns at its first test).
   Recorded in `tests/mech/CLAUDE.md`.
2. **My own plant harness raced make's 1-second mtime.** A plant applied in
   the same second as the previous revert's rebuild was not recompiled, and
   S299 first read UNDETECTED. Fixed in the (scratch) harness with a `sleep 1`
   on both sides; re-verified all five rows. The mech driver builds a fresh
   tree per row and is not exposed to this.
3. **The [K37] bare-compiler-call guard fired on the new check's first run**
   (7 sites, two of them path computations the regex reads as calls). Every
   call now goes through `$TIMEOUT_BIN`; the refusal arm asserts exit 1 exactly.
4. **`used` is honest and informative today.** On a DFA route `start_anchor`
   reads `used no` (only VM routes and `ENG_ATTEMPT` ask it) and `req_set`
   reads `used no` except on the no-DFA-scan VM route (K65's), because
   `emit_req_set_rest` now asks the set only after its own route test. The
   derived facts' internal asks never set `used`.
5. **Decisions capture reads the whole final `.c` buffer.** Stamps sit in two
   blocks around the `#include` lines and, on VM artifacts, beside the slot
   legend and the `R_*` give-up stamps, so the "byte range" is the buffer; the
   printer keeps object-like `#define <PREFIX>_…`/`PCREC_FEATURE_…` lines.
   `DFA_PREFILTER_OFFSETS` needed no conversion: it is an ordinary one-line
   object-like `#define` in the emitted text, captured like the rest.
   `--emit-facts` compiles header-less (`--emit-ir`'s rule), so the six ABI
   stamps a paired header would hold (`RX_NCAPS`…) are in the section.
6. **`--emit-facts` on an `.rxt` target is not built** (the design mentions
   it parenthetically); it mirrors `--emit-ir`, which takes `--pattern` only.
   Trigger: a request to list a `.rxt` target's facts (D77).
7. **`docs/dev/lanes/w4_modesweep.py` is stale** (it drives the retired
   `--source` and `--`-positional patterns), so it could not serve as the
   CLI acceptance instrument; `--emit-facts` adds refusals only (its own mask,
   and its bit in `CLI_MODES_VS_PATTERN_QUERY`), and `--help`'s text grew by
   the new entry, which moves every usage-printing diagnostic's stderr.
8. **Sabotage ids S295-S299** were numbered from main's highest (S294) at
   lane start; the K68 lane may also be numbering — check for a collision at
   merge.

## 5. OWED — the detached chain

One script, `/tmp/pf30_scratch/chain.sh`, launched `nohup … & disown`, log
`/tmp/pf30_chain.log`. It waits for `K68FIX CHAIN: ALL DONE` in
`/tmp/k68fix_chain.log`, then runs serially on this worktree's HEAD:

| step | log | completion |
|---|---|---|
| build | `/tmp/pf30_chain_build.log` | `PF30 CHAIN: build rc=` |
| `make strict` | `/tmp/pf30_strict_final.log` | `PF30 CHAIN: strict rc=` |
| `make test-codegen` | `/tmp/pf30_test_codegen.log` | `PF30 CHAIN: test-codegen rc=` |
| `make test` (timeout 9000) | `/tmp/pf30_make_test.log` | `PF30 CHAIN: make test rc=` — verdict is make's `*** [test-X] Error` lines |
| `make test-recursion-identity` (timeout 3600) | `/tmp/pf30_recid.log` | `PF30 CHAIN: test-recursion-identity rc=`; the (B) pin must NOT move (a re-pin is disqualifying) |
| mech solo: S295-S299, S268, S269, S274, S276, S286, S288 | `/tmp/pf30_mech_S<id>.log` | one `PF30 CHAIN: mech S<id>` line each |
| — | — | `PF30 CHAIN: ALL DONE` |

Plus the listing commit's gate, `/tmp/pf30_gate_30list.log`
(`GATE 30list DONE`).

Known darwin reds to discount (per wake-era notes): `nm could not read
arm_a.o` in `test-codegen`; PC-3 (U13).

## 6. For the next step / a fresh agent

- B1 (3.1) edits through `facts.c`: the derived accessors' `pf_derive` arms
  for `PF_REQ_RUN`/`PF_REQ_BYTE` are where `pcrec_find_*` replace
  `pcrec_req_window`/`pcrec_req_pick`'s `bytekey`; the `why` codes
  `PF_WHY_RATE_*` are already the listing's `rate:` tokens; `reqbyte.c` is
  then deleted and its owner rows in `facts.def` repoint.
- 3.2 adds E1 rows and `pcrec_facts_seal_e1`; the force loop already skips an
  unsealed epoch. 3.4 adds the E3 seal inside the `ENG_UNANCH` arm and the
  two decline tokens (`PfWhyCode` gains them).
- Not touched: `docs/dev/plan.md` STATE tags, the journal (manager's).
