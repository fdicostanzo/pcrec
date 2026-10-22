# dd10fix — [DD-10] pre-merge review fixes (lane report)

Lane dd10fix (opus), 2026-10-22, on `lane/dd10b` (which contains `lane/dd10`)
from d11814f49. Build go: manager, under Frank's "keep busy ... park on
branches" (2026-10-21). Standing ruling: dd10 R1 (keep the 250 cap, measured
budget). Rulings file `dd10b_rulings.md`: R2 (all review findings accepted)
is the last entry, applied here. The review's ten items, in order, then the
validation.

## 1. The items

| # | item | done |
|---|---|---|
| 1 | death = rc>=128; any other nonzero rc FAILS | `run()` sorts each case into `ran` / `died` / `error`. `error` (driver setup failure, or the timeout's 124) fails in every arm, the CONTROL included. 124 is below 128, so it needs no separate test. |
| 2 | guard >= 64 KB | `GUARD` is 64 KB of PROT_NONE below the stack. The comment says why (a ~9.3 KB `compile_driver` frame jumps one page without -fstack-clash-protection). Not exercised in the failing direction: on this box gcc probes by default. |
| 3 | §3.10¶2 worded as MEASURED; new families; CFLAGS skip | ¶2 now reads MEASURED on the named families at the default flags, enforced by nothing. ¶3 adds the call, compound and unbuilt figures. The budget did not move (§2), so the STOP rule did not fire. The script SKIPS, naming the flags, when make's `$(origin CFLAGS)` is not `file` (the Makefile passes it). |
| 4 | no-movers proof | queued as `686-dd10fix-sweep` (§3), OWED. |
| 5 | WIDTH cases assert rc=0 | done, and it found one: **"alternation of 20000 captures" had been refused** (`pattern too large (VM exceeds 131072 emitted nodes)`) before any walk ran, so it passed while testing nothing. Now 10,000 captures, which compiles and still needs 480,000 B at 48 B/frame if a walk recursed per branch. |
| 6 | 442368 as a limits.def row | `PCREC_COMPILE_STACK_BUDGET` (bytes, compile budget, override none, anchor 3.10, home LIMITS_H). The script reads it and `PCREC_MAX_GROUP_DEPTH` from `--list-limits`, and FAILS if either is missing. Re-pinned: limits_check manifest 75 -> 76, and run_registry_tests' coverage guard 37 -> 39. **dd10's §3.10 anchor on PCREC_MAX_GROUP_DEPTH had already moved the guard to 38 without a re-pin**, so the queued dd10/dd10b `make test` would have gone red on test-registry. It is the seventh reader of that shape, and is noted at the guard. |
| 7 | rc_find_root_call asserts non-NULL children | `assert(e && "...")` on every spine element (right children and head). A missing LEFT child ends the iteration after its node's right child, which is the old `!a` guard's answer for that subtree. |
| 8 | (?r) refusal cut 112 -> 256 bytes | dd10b moved the `(?r)` refusal from a `buf[112]` to `REFUSE`, whose arena text is cut at 256 bytes. A name long enough to be cut at 112 now reads in full up to 256. Real names are identical: PCREC_MAX_GROUP_NAME is 128 and the text around the name is short. |
| 9 | K130 | **FIXED** (small and equivalent, so not left open). Repro and timings are in known_issues.md K130: 40,000-byte literal 4.05 s -> 0.36 s (CLI), 8.67 s -> 0.37 s (driver, `features=all`). The compile-stack script fell from ~45 s to 5.1 s; the Makefile comment, testing.md and the shards.tsv estimate (65 -> 8) follow. |
| 10 | one spine iterator | `PCREC_SPINE_EACH(e, root, kind)` in `src/core/internal.h` yields each element right to left, head last. Nine loops are converted: the minw/cwmax/cwmin ALT arms, `sa_walk` CAT and ALT, `ew_walk_marked` CAT and ALT, `rb_walk_at` ALT and `rc_find_root_call`. `vm_det_seq`'s counter stays a hand loop because it counts nodes and never uses an element. coding_guide.md §2.4 names the macro. **The lint part is NOT done** (§4). |

Equivalence of item 10 by construction (the sweep is the proof):
- min/max/intersection over the same element set, with identities `LLONG_MAX`/`LLONG_MIN`/`~0u`/`EW_Z`. A spine has at least two elements, so an identity never survives.
- `ew_walk_marked`'s CAT arm handles the head with the same body. `EW_Z` is the enum's top, so "return `EW_Z`" and "return max" coincide.
- `rb_walk_at` keeps its call and combine order. `rc_find_root_call`'s "last hit wins" is unchanged.
- K130's arm continues at the leftmost consuming factor (the rightmost factor if none consumes) and ORs in every factor to its left, which is exactly what the top-down `cwmax(prefix) == 0` descent reached. A prefix is zero-width iff each factor is, because no `pcrec_cwmax` arm returns a negative value. `sa_walk` is tail-shaped (every arm continues or returns `acc | ...`), so continuing at a node equals OR-ing its walk.

The high-water marks at depth 250 are byte-identical before and after the conversion on every DEPTH family (the §2 table equals dd10b's).

## 2. Measurements (x86-64, gcc 15.2 -O2 -g, the 7700X, painted driver)

New families at the nesting cap. Conditionals and branch reset are refused
as "not implemented yet" at their first construct, so they have no nest to
measure. A `(?N)` call's own parentheses count as a nesting level, so a
call inside the deepest group is a 251st level and refused; the script's
call families put the call after the nest.

| family | d=250 | 251 |
|---|---|---|
| `((…a…))(?1)` callouter | 118,760 | refused (parse) 120,360 |
| `((…a…))(?250)` callinner | 118,760 | 120,360 |
| `(x)(?1)(?:(?1)(?:…a))` (probe only, not in the script) | 127,208 | 120,360 |
| `(a(?1)?` per level, depth 249 (probe only) | 120,264 | — |
| compound `^(?i:(?i:…a…))\|b$` (route verified by its `"compound"` stamps) | 221,656 | 212,360 |
| compound over `(?:`, `(?:…)*`, `(?:a\|` nests | 129,512 | — |
| compound over `(?:a(?:a…)?)?` | 201,784 (plain 215,472) | — |
| capture nests under `^…\|b$` (the route declines: no `"compound"` stamp) | as plain | — |
| conditionals `(a)(?(1)(?(1)…a))`, branch reset `(?\|(?\|…a))` | refused, 16,792 | — |

The worst is still `(a(a…)?)?` at 362,736 B. The new worst outside it is
the compound route at 221,656 (+10,752 over the same nest compiled plainly:
one nested `compile_driver`), which is 0.61x the worst. The budget stays
432 KB (1.22x the worst).

## 3. Validation

Done in the lane:
- `nice make -j2` and `make strict` are clean ("whole tree compiles clean
  with -Werror -Wshadow").
- `tests/thread/run_compile_stack.sh`: 39 passed, 0 failed, 5.06 s wall.
- Failing directions, each run on a scratch copy of the script:
  - control on a missing pattern file -> `FAIL: control: the driver did not run to completion (exit 2 ...)`;
  - 20,000 captures -> `FAIL: ... was REFUSED (pattern too large ...)`;
  - `PCREC=/bin/true` -> `FAIL: could not read PCREC_COMPILE_STACK_BUDGET...`;
  - `COMPILE_STACK_CFLAGS_ORIGIN='command line' COMPILE_STACK_CFLAGS=-O0` -> `SKIP: ...` (rc 0).
- `tests/registry/limits_check.sh`: 39 passed, 0 failed.
- Mech VALIDATE_ONLY: all 29 rows anchored in the edited C files and 7 in
  `internal.h`/`limits.def` are valid, S1480 included.

OWED, queued as ONE held chain on this worktree (owner dd10fix). Each
`--ready` exits 75 while `i2build-parity` is pending or running (tested on a
copy with the state forced to `pending`: rc 75, "held until i2build-parity
ends"). It is green now, so the chain starts when the box frees:
1. `686-dd10fix-build` (`make -j16`).
2. `686-dd10fix-strict`.
3. `686-dd10fix-test` (`scripts/perfrun --label dd10fix`). This validates
   lanes dd10, dd10b and dd10fix together; the cancelled 680-683 dd10 and 685
   dd10b keys are not re-queued.
4. `686-dd10fix-mech`: S1336 S1337 S1338 S1339 S1340 S1440 on the
   compilestack arm, and S1480 on mrl+harness. All are expected DETECTED.
   S1336/S1337 are re-aimed onto the iterator; S1337 now plants the arm as it
   was before dd10.
5. `686-dd10fix-sweep`: item 4. `scripts/emit_sweep.py --ref 62ca83389`
   (branch point with main) `--tree-rev bdefeba55` (this lane's source
   commit), `--no-self-check`, streams c-default, c-vm, emit-ir, composition,
   facts, emit-ir-auto and stderr, over the whole corpus. Identity is
   required. The dumps stream is excluded because `--list-limits` gains a row
   by design. Output goes to `worktrees/dd10b/build/dd10fix-sweep/`.

Read each verdict with `scripts/boxqueue state dd10fix-<stage>` and
`scripts/verdict LOG`; the logs are under `worktrees/.boxqueue/done/`.

## 4. Not done, and findings

1. **`make lint` frame ceiling (item 10, second half): not built.** It needs
   the call graph's cycles, i.e. `-fcallgraph-info=su` output (VCG) parsed
   into SCCs, plus a frame threshold per cycle member and an allowlist. That
   is a new instrument rather than a small change. The rule "do the iterator
   only and list the lint part" applied. The `PCREC_OWN_FRAME` marking stays
   checked only by its effect (S1340 on the compilestack arm).
2. 67 other hand-rolled spine loops remain in the tree (13 `for` and 54
   `while` by grep, `for (...k == A_CAT|A_ALT; ... = x->l)` and
   `while (x->k == A_CAT|A_ALT)`). They are L1-X1's staged sweep (coding_guide
   §2.4), not converted here. The macro is now there to convert onto.
3. Unlock, recorded only (no build): with the nesting cap the single bound
   on the stack, a caller-set nesting limit (`pcre2_set_parens_nest_limit`'s
   analogue) is a one-field change on the parser's existing depth test. It is
   already an [IFACE-PUSH] candidate.
4. The mech arm `compilestack` now passes `PCREC=$tree/build/pcrec`
   explicitly. The default would have resolved to the same file.

## 5. STATE AT HANDOFF

- Branch `lane/dd10b` @ the report commit, all committed. Source commit
  bdefeba55. Rulings file: R2 is the last entry, applied.
- No abi event and no emitted-byte change intended. `--list-limits` gains one
  row (spec hunk limits.md §3.10¶2). K130 FIXED. S-ids used: S1480 (S1481-S1489
  unused). K-id: K130.
- OWED: chain `686-dd10fix-{build,strict,test,mech,sweep}` (§3). A fresh
  agent or the manager reads the five verdicts. A red sweep stream names its
  movers in its log; any mover there contradicts §1's equivalence argument and
  is a finding against this lane.
