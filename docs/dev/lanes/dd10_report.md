# dd10 — [DD-10] the compiler's C-stack budget (lane report)

Lane dd10 (opus), 2026-10-21/22, branch `lane/dd10` off main 62ca83389.
Build go: Frank 2026-10-21 ("1,2,3 go"; this row is item 2). Contract ruling:
`dd10_rulings.md` R1 (option (a)).

## 1. Summary

The row's premise held, and it was worse than the 2026-08-13 row said. On a
painted 64 MB thread, `pcrec_compile` used 62 KB for the pattern `a`, and at
PCRE2's nesting cap of 250 it used 250 KB (plain groups), 2.7 MB
(`(?:(?:a)*)*`) and 5.4 MB (`(?:a(?:a…)?)?`). A 128 KB thread died at depth
~4 for the last family. A second class was not depth-bounded at all: a flat
alternation recursed once per branch, and 200,000 capture alternatives
SIGSEGV'd an 8 MB stack (K114).

After this lane:

- every walk the measurement found recursing along an `A_CAT`/`A_ALT` spine
  iterates it: a chain of any length costs no stack per element;
- the two recursions with fat frames keep their bulk off the C stack;
- the worst measured family at depth 250 uses 634,504 B (nested
  lookarounds, parser-bound), and `docs/spec/limits.md` §3.10 states a
  768 KB budget that `tests/thread/run_compile_stack.sh` holds.

Zero emitted-byte movers expected, no abi event (section 6).

## 2. STEP 0: the premise, measured

Instrument: a driver that runs one `pcrec_compile` on a thread whose stack it
mmaps and paints, then reads the high-water mark (later hardened into
`tests/thread/compile_stack_driver.c` with a guard page). `features=all`,
engine auto, x86-64, gcc 15.2 `-O2`, the 7700X dev box.

| family (depth 250) | before | after |
|---|---|---|
| `a` alone (the floor) | 61,616 | 61,616 |
| `((((a))))` plain groups | 250,504 | 250,504 |
| `(a\|(a\|…b))` | 2,715,460 | 250,504 |
| `(?:(?:a)*)*` | 2,723,668 | 250,504 |
| `(?:a(?:a…)?)?` | 5,404,900 | 250,504 |
| `(a(a…)?)?` | 5,407,460 | 362,736 |
| `(?=(?=…a))` lookahead | 634,504 | 634,504 |
| `(?>(?>…a))` atomic | 562,504 | 562,504 |
| `(?i:(?i:…a))` | — | 606,648 |
| named groups `(?<n0>…)` | — | 566,504 |

Per level after: lookarounds 2,480 B (14,504 + 2,480·d), plain groups 944 B.
At 128 KB a lookaround nest fits to depth 47, plain groups to 123.

The CONTROL (record only, per R1): libpcre2 10.46's own `pcre2_compile` on the
same probe needs ~195 KB at depth 250 for every family (191,880-195,176 B),
and refuses 251 with its error 119. So PCRE2 does not fit 128 KB at its own
cap either.

Width (chains), before → after, same probe:

| chain | before | after |
|---|---|---|
| 10,000 capture alternatives `(0x)\|(1x)\|…` | 498,760 | 62,912 |
| 200,000 of them, `--max-nfa-states` raised, 8 MB thread | SIGSEGV (174,410 `pcrec_minw` frames) | refused cleanly, 25 KB |
| 20,000 trailing `\b` | > 786 KB (crash at the budget) | 61,616 |
| 20,000 leading `(?=ab)` | 657,368 | 62,912 |
| 20,000 leading `\A` | 655,528 | 24,068 |
| `(?:abab…){+}` 20,000-byte quantified literal, VM | > 786 KB (crash) | 61,120 |

How the culprits were found: `gcc -fstack-usage -fcallgraph-info=su` over the
library, Tarjan SCCs of the call graph (84 recursive cycles; the frame sizes
named `rb_walk` 12,896 B, `vm_rep` 2,400, `vm_cost_rep` 2,224,
`vm_count_slots_rep` 2,144), then `gdb` backtraces at an overflow on an
undersized thread for the families the static graph cannot see.

## 3. The design argument: a depth cap plus spine iteration

The brief offered two general forms: explicit worklists wherever recursion is
the risk, or one parse-time nesting budget every recursive pass can rely on.
The tree already had the second: `PCREC_MAX_GROUP_DEPTH` = 250 (PCRE2's
number) bounds parser and AST depth, and coding_guide.md §2.4 already states
the rule that makes it sufficient — spines are walked iteratively, recursion
goes only into items, whose depth the cap bounds. So the general fix is not a
new mechanism. It is (a) finding and fixing the walks that broke the spine
rule, (b) keeping per-level frames small, and (c) a CHECK that makes both
properties observable, because the spine rule had been re-learned four times
(K20 three times, K114 now) with nothing to catch the next violation.

84 recursive functions make explicit worklists everywhere the wrong cost; the
check is the general mechanism. `run_compile_stack.sh` compiles chains far
longer than the budget could hold at even a 32-byte frame per element, so
any future walk that recurses per element is red the day it lands, whichever
file it is in.

R1 settled the contract: keep 250 (acceptance parity with PCRE2), state the
measured requirement, test at that size. A pcrec-own lower cap (refusing
patterns PCRE2 accepts) and an iterative parser were not built.

## 4. What changed

- **Spine iteration** (K114): `pcrec_minw`/`pcrec_cwmax`/`pcrec_cwmin`'s
  `A_ALT` arms (src/opt/mrl.c); `sa_walk`'s zero-width-prefix arm and `A_ALT`
  arm (src/facts/startanch.c); `ew_walk_marked`'s zero-width-suffix
  direction and `A_ALT` arm (src/facts/endwin.c); `rc_find_root_call`
  (src/parse/rxt_compose.c, leftmost-hit order kept); `vm_det_seq` declines
  a spine longer than its cap before recursing (src/gen/emit_vm.c).
- **Fat frames**: `rb_walk` (src/facts/req.c) now writes into caller-provided
  storage and takes its children's results from depth-indexed arena slots
  (`RbWalk.slot`, two `RbVal` per depth, allocated once per depth: bounded by
  nesting, not node count); its combining steps are small
  `PCREC_OWN_FRAME` helpers. The VM cursor rung's 2 KB of scratch moved into
  `vm_cursor_applies` (the two pre-passes) and `vm_cursor_try` (the emitter).
- **`PCREC_OWN_FRAME`** (src/core/internal.h): `__attribute__((noinline))`
  with its reason, the one home for "this helper's locals must not join a
  recursive caller's frame".
- **Contract**: `docs/spec/limits.md` §3.10 (new), [0¶1]'s anchored range,
  `PCREC_MAX_GROUP_DEPTH`'s `limits.def` anchor `3.10` (so
  `limits_check.sh` checks 250 against §3.10's text).
- **Check**: `tests/thread/run_compile_stack.sh` + `compile_stack_driver.c`,
  the second line of `make test-stackdepth` (~45 s). DEPTH arm: nine
  families at 250 compile and at 251 are refused by name on a 786,432-byte
  thread. WIDTH arm: seven chain shapes. CONTROL: a 32 KB thread must die.
  RECORD lines carry every high-water number.
- **Mech**: arm `compilestack` in tests/mech/run_sabotage_matrix.sh; rows
  S1336 (minw spine recursion), S1337 (endwin zero-width run recursion),
  S1338 (det_seq cap decline removed), S1339 (`rb_walk` values back on the C
  stack: measured 1,378,532 B at depth 250), S1340 (`PCREC_OWN_FRAME` as
  always_inline: measured 4,502,180 B). All five answer-identical, so this
  arm is their only net.
- **Records**: known_issues K114 (FIXED); tests/thread/CLAUDE.md;
  docs/testing.md; tests/ci/shards.tsv `test-stackdepth` weight 0.5 → 65
  (ESTIMATED); plan.md [DD-10] to Active, STATE:started.

## 5. Findings for the manager (not built here)

1. **memfn frames, the 62 KB floor** (R1: do not edit memfn/src; file the
   kit request): `memfn/src/formhash.c` `pcrec_mf_form_hash` 36,368 B and
   `memfn/src/terms.c` `pcrec_mf_set_terms` 36,256 B (`-fstack-usage`,
   static). They are not in a nesting recursion, so they set the floor every
   compile pays, not the slope; they are half a 128 KB thread on their own.
   `terms.c` `dfs` (1,376 B) is recursive: its bound was not surveyed here.
2. **The next parser lever**: `ExtResult` carries `char msg[256]` by value
   (312 B) through `pcrec_ext_group` (368 B frame), `group_answer` (448 B)
   and `pcrec_laport_group` (736 B), which is most of the module-doorway
   level's 2,480 B. An arena-text `msg` (`pcrec_sb_fragf`) would take the
   lookaround/atomic/inline-option nests to roughly the plain-group slope
   (estimate ~1.3 KB/level, ~330 KB at 250; not measured). Touches ~44
   refusal sites; not done (R1 asks for the measured statement, not this).
3. **Caller-settable nesting limit**: PCRE2 has
   `pcre2_set_parens_nest_limit`; pcrec exposes none (`pcrec_options` has no
   such field). Not added, per R1: a candidate for [IFACE-PUSH]. It would let
   a small-thread caller trade depth for a clean refusal.
4. **Possessify** `first_of` (448 B) with `text_first` (336 B) is the
   next-largest analysis slope (`(a(a…)?)?` at 362,736 B), under the
   parser's lookaround slope, so not the worst; noted.
5. **Time, not stack** (no promise per limits.md §3.3.5; noted only):
   `sa_walk` calls `pcrec_cwmax(a->l)` at every step down a non-zero-width
   spine, which is quadratic in the concatenation's length; and
   `(a)((?1))((?2))…` chained subroutine groups took >120 s to compile at
   1,000 groups (timeout fired; 100 groups is refused at 101 MB emitted).
6. `eol_tail_plain` (src/parse/definitions.c) still recurses both spine
   children, deliberately unchanged: it reads the registry's own `\Z`
   definition row, never a caller's pattern.
7. `compile_driver` (9,408 B frame) sits in a cycle with the compound walk
   (`pcrec_compound_walk` → `part_compile` → `compile_driver`); its depth is
   the compound nesting, not the pattern's, and was not surveyed further.

## 6. abi / stamps

No emitted byte is expected to move: every change is a stack-shape change
inside an analysis or a pre-pass with identical results. Spot check, old
(pre-change library) vs new CLI, 25 patterns chosen to reach every touched
walk (alternations with captures, lookbehinds, `\b`/`$`/`\z` ends, cursor-rung
quantifiers, literal runs) × engines auto and vm: the emitted `.c` and the
`--emit-facts` listing byte-identical in all 50 compiles. The identity gates
in `make test` are the full check (owed, section 8). No stamp, no `rx_info`
field, no new error: the 251 refusal is the existing one.

## 7. Validation done in the lane

- `make test-stackdepth` in the worktree: run_stackdepth_tests.sh 5 passed
  (its KNOWN K33 line as before); run_compile_stack.sh 26 passed, 0 failed.
- Failing direction: the same script against the PRE-change library
  (`LIBPCREC=`): 7 red — four depth families at 250 and three width chains
  (20,000 capture alternatives, 20,000 trailing `\b`, the quantified VM
  literal); the leading-`\A` chain red standalone (SIGSEGV at 768 KB).
- `tests/registry/limits_check.sh`: 38 passed, 0 failed (the new §3.10
  anchor included). `make test-ci-shards`: 9/0. `scripts/plan_lint.sh`: 0
  violations. Mech field validation (VALIDATE_ONLY) of S1336-S1340: 5 valid.
- S1339 and S1340 measured by hand on scratch builds (numbers in section 4).

## 8. STATE AT HANDOFF

- Branch `lane/dd10`, all work committed. Rulings file: R1 applied (last
  entry).
- OWED (queued as detached boxqueue jobs, owner `dd10`, prio 680, from
  `build/dd10_stages`): build, `make strict`, `perfrun make test`, mech
  S1336-S1340 (expect 5 rows DETECTED on arm `compilestack`). Verdicts:
  `scripts/boxqueue state dd10-<stage>` and each job's log under
  `worktrees/.boxqueue/done/`; read with `scripts/verdict LOG`.
- Not run: `make asan`/`ubsan` (the depth families under ASan will exceed
  768 KB — the test is plain-build only, as run_stackdepth_tests.sh is; the
  san battery excludes tests/thread already).
- Mac: not run. The budget carries ~20% over the x86-64 measurement for that
  reason; an arm64 red would mean re-measuring, not a defect.
