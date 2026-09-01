# lane w12 — [DD-13b.W1.2] log

## hold acked: no builds until w12.lift

The box HOLD was in force at launch (`/home/duxevents/pcrec/worktrees/w12.lift`
absent). No `make`, no gcc/clang, no `build/pcrec`, no harness section, no
sweep, no background job until it appears. Reading, editing inside this
worktree and `git` are what this lane does until then.

## Orientation (reading, under the hold)

- `docs/design/dd13_format/w1_impl.md` §0.2, §1.2, §1.5-§1.8, §3.5, §4's
  spec-delta table, §5's `[DD-13b.W1.2]` charter paragraph.
- The landed W1.1 code: `src/parse/rxt_source.c` (1,279 lines — head parser,
  `parse_target`/`parse_config`/`config_walk` all PARSE and none of them
  BUILD), `src/core/internal.h`'s `RxtRow`/`RxtSource`, `cli/main.c`'s
  `--list-source` query, `tests/rxtsource/`.
- The four abi sites, re-measured in this worktree rather than read from the
  design note (which predates [OPT-5]):
  1. `src/gen/emit_dfa.c` `.abi` — **13** today.
  2. `tests/codegen/run_codegen_tests.sh:2707` `ABI_EXPECT=13`.
  3. `docs/spec/match_api.md:159` and `:1602` — "abi is 13".
  4. `tests/codegen/run_recursion_identity.sh:473` `FILEPIN="${...:-dc2c8ef}"`
     — the design note's `c275aef` is stale.
  This lane's bump is therefore **13 -> 14**; the manager assigns the final
  number at merge.
