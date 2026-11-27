# arenabuild report: [ARENA-SCOPES] C0, R1, T1, F1

Lane arenabuild (opus), branch `lane/arenabuild`, base `cb1fb59a2`. Design of record: `docs/design/arena_scopes.md`
rev 2.1 (owner's build go 2026-11-25; manager's rulings in `docs/dev/reviews/2026-11-24-r103-arenadesign2.md`).
Scratch: `/var/tmp/pcrec-pcrec/scratch/arenabuild/`.

## Summary

R1, T1 and F1 are built and committed. Every gate is green except three STOP-class reads, all reported to the manager
and awaiting rulings:

- **The W7 budget.** The trial count runs over budget: 2,112 trials against 2,000, in 58 s against 60 s.
- **One memgate peak compile over its bound.** The read is an allocator artifact: the arena call sequence is identical.
- **One growth rung moved, plus 4 compiles over the instr max band.** The rung move is a refusal at 8 MiB RLIMIT_DATA,
  on a cell that sat 8 KB under the rung on base.

C0 matches the design's expectations on (a), (b) for S10, (c), (d) and (e). C0(b) shows S11 and S12 are not live at the
peak, so F3's bound for those two is re-based to 0, as the design asks to report. Answers are identical: the emit sweep
has 0 movers and rungs are IDENTICAL at R1.

Sabotage rows used: S3593-S3602. S3603-S3612 are unused. Design row (3) is listed UNREACHED; no row was filed for it.

## C0 census

The census used scratch builds only; nothing from it is committed. Base is `cb1fb59a2`.

- **(a) LEAK-ATTRIBUTION.** The 13 growth leak shards of cloud run 45492837175 (52, 58, 59, 60, 64, 75, 76, 80, 81, 83, 84,
  89, 90) were re-run under ASan+LSan with `fast_unwind_on_malloc=0` and a malloc context of 40, through `run_growth.py
  --lib`. All 13 shards reproduce: 26 direct leaks (24 x 32,768 B, 2 x 65,536 B on two shards), and EVERY one is allocated by `pcrec_memfn_stamps_render` > `target_headers_render` > `pcrec_sb_printf` > `sb_grow` (S10's `nb`). No leak lies outside S10-S15: the client set stands.
- **(b) PEAK BASE.**
  - memgate on base against itself: peak and instr noise are 0 over 7,402 compiles.
  - Peak probe: the allocation that sets the final peak was found by a two-pass index-and-backtrace run, the same
    attribution as r103's gdb probe. It ran over 170 sampled corpus compiles with `--features all`; 150 of them were
    successful with the peak reproduced.
  - 148 of the 150 peak inside `pcrec_memfn_stamps_render` > `target_headers_render` (S10's `nb`); r103 recorded 146
    of 150. The other 2 peak in `wd_alloc` (`pcrec_mf_wdecide`).
  - `splice_mark` (S11) and `render_buf` (S12) are never on the stack at the peak, so their builders are not live at it.
    **F3's bound for S11 and S12 is re-based to 0** (design C0 "fail fast" column: reported; D-1 does not move).
- **(c) REACH.** Client functions were hit by gdb breakpoints on the base CLI, one run per witness with that witness's
  options.

  | witness | clients reached |
  |---|---|
  | W1 | S10, S11, S13 |
  | W2 | S10, S11 |
  | W3 | S10, S11, S13, S15 |
  | W4 | S10, S11 |
  | W6 | S10, S11, S13 |

  - **S11** is reached by every witness.
  - **S12** (`render_buf`) is reached by no witness: it runs only under `--part-layout`. One witness is any compile with
    `--part-layout=find:inline` or `compound:inline`. It is SINGLE-CONTROL today (D-8).
  - **S14** (`clskit`) is reached by no W1-W6 witness. One witness is S430's pattern under `--engine=vm --tune=-2`
    (`([aeiou])[bcdfg][hjklm][npqrs][tvwxz][AEIOU][BCDFG][HJKLM][NPQRS][TVWXZ]`, 10 kit emits). Its `Arena a` has a `cx`,
    so W7's hand-kept window would see it once a witness runs that pattern; that belongs to F2 or later.
- **(d) K163.** Scratch `--wrap` of `pcrec_compile_driver` with a depth counter, plus a `--wrap` of `pcrec_arena_alloc`
  that fails arena allocations made at depth 1 through the outer Ctx (part compiles are the wrapped calls; the top level
  calls the static driver). It ran over `tests/compound/split.rxt`'s 105 patterns.
  - 27 patterns make lent allocations: 54 uses, all at ONE site, `compile.c` `pf->memfn_forms =
    pcrec_sb_fragf(pf->into, ...)`. The full stack is part_compile < walk_part.
  - Failing each use: 54 of 54 refuse AND strand, between 195 KB and 1.27 MB each (median 208 KB).
  - **K163 is CONFIRMED, and the copy is the only lent use**, as expected.
- **(e)** On 4 patterns under `--emit-facts`, including W5's `(?:a?){700}`, every `pcrec_minimize_dfa` call comes before
  `pcrec_facts_force_all` and none has it on the stack. No scope client is reachable under the force loop, so **sabotage
  (3) has no witness: listed UNREACHED, no row filed**.

## R1

Commit `a5e800416`. It adds `pcrec_sb_adopt` in sb.c, heap only: it refuses `.ar` on either side, through the
compile's channel or by abort when detached. The function is used at the two storage transplants,
`memfn_stamps.c` `target_headers_render` and `part_layout.c` `render_buf`, with D-10's interim sentence.

Gates:

- memgate peak against base, bound 0: 0 movers over 7,402 compiles.
- rungs: IDENTICAL over 6,344.
- strict green.

Sabotage (8) is S3601, with its unit check in `tests/core/scope_check.c` (D-6, 3 checks). The mech-arm reach for
S1897/S1899 and the partlayout arm (S1111, S1127) ride the queued `arenabuild-mech`.

## T1

Commit `97d973890`. `tests/core/memgate/` holds `memgate.py`, `mg_drv.c` and a CLAUDE.md, plus opt-in `make memgate`
(MEMGATE_BASE, MEMGATE_OUT, MEMGATE_BOUND). It is never part of `make test`.

- Noise run, base against base: peak 0 over and 0 deltas over 7,402 compiles.
- instr ratio 1.00000 at p50, p95 and max.

The T1 gate (noise 0) holds.

## F1

Commits `634ab02af` (code) and `25065242b` (tests, docs, rows), and the report commit (this report).

- **Registry (arena.c).**
  - LIFO records of four kinds (MARK, HEAP, STRBUF, ARENA), each heap-calloc'd at its kind's size.
  - Scopes are stamped marks; one `scope_check` (L1) covers all six handle-taking calls.
  - The close post-condition is `a->top == below`; L5 (no scope on a child) and L7 (no hold while a scope is open) are
    enforced.
  - `pcrec_arena_free` releases the registry first. No arena.c function calls `pcrec_arena_alloc`.
- **compile.c.** A handler-top `pcrec_scope_unwind`, and `pcrec_scope_check_closed` before the first take.
- **Holds.** `pcrec_arena_hold` replaces `own_slot`/`own`/`AOwn` (compound.c walk_part).
- **pcrec_err_chan.** A pass-through at F1, used at every arena.c/sb.c refusal; the entry counting and the lent pair are
  F4's.
- **First client: minimize.c.** All 8 tables are scope entries; `keyseen` uses an early `pcrec_scope_free`. There are 0
  bare `free(` calls and exactly 1 `pcrec_scope_free(` (G4).
- **Re-aimed rows and readers.** S255 and S256 now anchor on `pcrec_err_chan(`. S3580 is re-aimed at the hold's store,
  not retired. The readers of the deleted names were rewritten: the internal.h comments, job_cleanup, walk_part, W6's
  comment and docs/testing.md's W6 paragraph.
- **W7 and the SEEN gate** (`tests/core/alloc_check.c`, linked with `-Wl,--wrap=pcrec_arena_alloc
  -Wl,--wrap=pcrec_arena_free` in BOTH `run_alloc_tests.sh` and `run_resource_tests.sh` section 2b).
  - **The two windows.** The scope window covers arenas where a scope is open (`pcrec_arena_open_p`). The hand-kept
    window covers arenas that are Ctx-bound, not `&cx->arena`, not a child and not the DFA memo. The memo is excluded,
    see below.
  - **(i) The planted control.** "W7 control" plants a hand-kept `Arena` with a block, then makes an arena allocation
    that W7 fails, and requires every trial to read STRANDED. It reads 1 of 1 STRANDED.
  - **(ii) The filed row.** W7/W3 reads `uprops_produce`'s tmp strand. The new `known_stranded` row is REACHED on 9
    trials. minimize's row was deleted, and none of its tables strands.
  - **(iii) Sabotage (10).** This is S3602.
- **W7 measured at F1.**
  - W1, W2, W4 and W6 have EMPTY windows (their minimize merges nothing, and they hold no hand-kept arena), so they get no
    W7 row: a population-0 row would pass by emptiness (K35).
  - W3 has 2,111 trials: 9 in the tmp window and 2,102 in minimize's scope. Its floor is 1,055 (D110 half).
  - The whole W7 set adds 2,112 trials and about 58 s.
- **Deviation awaiting ratification.** The DFA memo arena (S7) is excluded from the hand-kept window in the test link
  only. compile_driver frees it on every arrival, so it cannot strand, and its window spans the whole compile: W7/W1
  alone read 2,614 trials with it.
- **W6's pin** was re-pinned UP from 982/1008 to 1010/1045 (the records' callocs are malloc trials), and docs/testing.md
  was updated.
- **Scanner** (`tests/core/scratch_builder_check.py`).
  - Rows: minimize's ALLOW row deleted; +2 registry rows (arena.c `rec_take`, `pcrec_scope_malloc`).
  - New rules: L2-static, L4 (struct-field store; src/parse calls outside `SCOPE_PARSE_ALLOW`, empty until F6), D-7
    (err_chan at every arena.c/sb.c refusal; no arena.c caller of `pcrec_arena_alloc`) and readers (`pcrec_arena_open_p`
    called by no src/cli/lib function).
  - There are 7 must-fail fixtures and 2 must-pass fixtures, and a scope-site floor.
  - The D-11 binder rule is F2's (the design files it with D-11), so it is not added here.
- **Unit tests** (`tests/core/scope_check.c`, in `run_core_tests.sh`, floor 16). There are 35 checks on a detached
  arena, with a fork per refusal:
  - the stale-handle drill (a forged handle, plus the real reopen when calloc reuses the address);
  - the free-the-mark drill, steps 1-7 including 3b for every registering call and 3c;
  - L7, L5, child and strbuf entries, unwind, L2, teardown, and D-6 adopt.
- **Docs.**
  - The D109 addendum is one paragraph in docs/dev/decisions.md.
  - The D-12 hunks are in src/core/CLAUDE.md (the builder rule and arena.c's line; the file stays under its 12 KB limit)
    and in docs/dev/guide/coding.md 1.6 (minimize is no longer a named exception; scopes are the form; `pcrec_arena_hold`
    replaces `pcrec_arena_own`).
- **Peak deltas against base** (memgate, 7,402 compiles):
  - 7,259 equal, 131 up, 12 down; median 0.
  - Largest legitimate rises: +184 B (corpus/1337) and +48 B on 7 compiles. The rest are +24 B or less, inside the
    232 B bound.
  - **STOP read:** one growth cell, `matrix/atomic.plus.sole.litalt@14`, non-compound at a 1.0 GB peak, reads +4,048 B,
    and the same +4,048 B on attempt-arena high-water. A trace of every attempt-arena allocation (609,424 calls, size
    and new-block flag) is IDENTICAL on base and F1. The delta is therefore `malloc_usable_size` of one large block
    (mmap against brk rounding), moved by heap history, not by bytes the arena asked for. One other compile was lowered
    the same way. Reported; awaiting a ruling.
- **rungs:** 1 moved of 6,344. **STOP read:** `depth/ncaltrep@250` at the 8 MiB RLIMIT_DATA rung goes from compiled to
  nomem in `target_headers_render`'s `nb` (S10).
  - It is deterministic, and the live peak is identical (7,710,896 B).
  - Bisected to 4 KB: base needs about 8,380,416 B (8 KB under the rung) and F1 about 8,392,704 B (+12 KB).
  - This is heap fragmentation from the registry records, with base at the edge. Reported; awaiting a ruling.
- **instr:** p50 1.00009 and p95 1.00089, inside the p95 band of 1.01. **STOP read:** 4 tiny corpus compiles (about 91K
  instructions each) exceed the 1.02 max band by about 2,000 instructions (worst 1.0225). That is the fixed scope cost:
  open/close and about 9 record calloc/free pairs in minimize. Reported; awaiting a ruling.

## Checks

- `make strict`: green (`strict: whole tree compiles clean with -Werror -Wshadow`).
- Anchor check `python3 scripts/m6read_check_sab_anchors.py`: rc 0.
- Emit sweep `scripts/emit_sweep.py --ref cb1fb59a2`: `DONE rc=0`, movers 0 in every stream (argv population 7,599;
  composition 88 artifacts).
- alloc_check, full single-shot run on the injected F1 tree: every witness PASS.
  - W1 2,535; W2 23; W3 2,655; W4 401; W5 PASS.
  - W6 1,045, with its pin 1010 exact.
  - W7 control 1/1 STRANDED; W7/W3 2,111.
  - Both `known_stranded` rows REACHED.
- scope_check: 35 PASS, 0 FAIL. scratch_builder_check: PASS, with 26 allowlisted sites and 1 scope site.
- memgate: noise 0 (T1); R1 peak 0 movers and rungs IDENTICAL; F1 as listed under F1 (three STOP reads).
- Sabotage rows S3593-S3602 were written; `REACH_ONLY=1` over these plus S3580, S255, S256, S1897, S1899, S1111, S1127: `DONE rc=0 rows=17 reached=12 unreached=0` (5 rows carry no probe) at 25065242b. Detection verdicts come from the queued `arenabuild-mech`.
- `make test` is queued as `arenabuild-test`.

## STATE AT HANDOFF

- Branch `lane/arenabuild` at the report commit, on base `cb1fb59a2`; worktree clean but for this report's commit. Units: C0 DONE (scratch), R1 DONE, T1 DONE, F1 BUILT with three STOP reads awaiting the manager's rulings (W7 budget 2,112 > 2,000 plus the DFA-memo exclusion; one memgate peak/ATT artifact; the 8 MiB rung move on `depth/ncaltrep@250` and 4 compiles over the instr max band). No code was changed in response to them: a ruling may change F1 (e.g. a W7 stride, or HEAP record+block in one allocation).
- OWED (queued via boxqueue, not waited on): `200-arenabuild-test` (`make test` via perfrun, log `build/arenabuild_test.log`) and `200-arenabuild-mech` (17 rows: S3593-S3602, S3580, S255, S256, S1897, S1899, S1111, S1127).
- Not done here: F2 onward; F4's lent counting in `pcrec_err_chan`; the D-11 scanner rule (F2); W7 rows for W1/W2/W4/W6 (empty windows); S12/S14 witnesses (C0(c) names them).
- Scratch evidence: `/var/tmp/pcrec-pcrec/scratch/arenabuild/` (`c0a/`, `c0b/`, `c0d/`, `c0_notes.txt`, `mg/*.log`, `att/`, `esweep.log`, `alloc2.log`, `reach.log`).
