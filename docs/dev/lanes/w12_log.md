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

## Oracle verification of the new fixture cells (python3 `re`, one invocation)

```
OK  [a-z]+ 'abc' (0, 3) (0, 3)
OK  [a-z]+ '123' None None
OK  [0-9]+ '42'  (0, 2) (0, 2)
OK  [0-9]+ 'xy'  None None
OK  error|warn|fatal 'an error here' (3, 8) (3, 8)
OK  error|warn|fatal 'a fatal one'   (2, 7) (2, 7)
OK  error|warn|fatal 'nothing here'  None None
OK  a+ 'aaa' (0, 3) (0, 3)
```

## Build order actually taken

1. resolver (`rxt_source.c` + `internal.h`)
2. `rx_info.name` / `nentries` / abi sites 1-3
3. `cli/main.c` — the option-parser factoring, then the three flags and
   the output-naming rule
4. `driver.c` (F13), then `run.sh` (H11)
5. tests + fixtures
6. spec hunks (D80) + every owning CLAUDE.md
7. the lane report

Site 4 of the abi ritual (the FILEPIN) is deliberately last and is still
OWED — the pin must name this step's final src commit.

## Self-review performed under the hold, in place of a build

`bash -n` on all three edited shell scripts; a read-through of `main.c`'s
new definition ORDER (`base_name`/`write_file` at 197/203 precede the new
block at 644+; `cli_parse` at 269 precedes `apply_target` at 687); a check
that every new `"$PCREC"` call carries `"$TIMEOUT_BIN"` on its own line
([K37]); that both new `sort` sites carry `LC_ALL=C` ([K35]); and that
every `run.sh` edit lies outside the BEGIN/END pinned arm region
(1184-1437 — edits at 764, 843, 1088, 1124, 1559).

Two defects were found and fixed by that review rather than by a run: a
`--source`/query conflict tested BELOW the query dispatch, where each
query returns from `main` first and would have won silently
(`--source f.rxt --count-groups -- a` counted the pattern and ignored the
file); and a backtick inside a double-quoted `pass "..."` message, which
bash would have run as a command.

## PROBE WINDOW, 2026-08-31 21:23-21:27 EDT (manager's hold amendment)

Single-pattern `build/pcrec` probes against the **MAIN tree's** binary
(`/home/duxevents/pcrec/build/pcrec`, built from main at 14:55, i.e. WITHOUT
this branch's code). `date` before each; no make, no gcc, no test script.

**What a main-tree binary can and cannot answer.** It cannot exercise one
line of this lane's code. What it CAN do is settle the things this lane
INFERRED about the surfaces it builds on — the `--list-source` column
layout its new run.sh reader indexes, the emitted-text shapes its new
greps pin, and whether its own fixtures parse at all. Every one of those
was an assumption until this window.

| probe | answer |
|---|---|
| `--list-source three_configs.rxtin` | parses; `target` rows are (col3 = PREFIX, col4 = DEFINITION), which is what `run.sh`'s new `read -r _k _l _n _v _rest` indexes |
| `--list-source head_basic.rxtin` (after this lane's correction) | parses; kind order still `description lib config config target pattern pattern`, so W1.1's existing check is unmoved; `lib` value keeps its quotes (`"common.rxt"`), which is why the resolver unquotes |
| `--list-source` on the five other new fixtures | all parse. **`lib <common>` PARSES and keeps its angle brackets**, so the `<store>` refusal is reachable and its needle matches; `config sneaky`'s `pcrec -p notmyprefix` survives to column 15 as raw text |
| `-o -` on a named-groups pattern | **`.abi = 13`** on main (site 1's before-value, confirmed rather than read from a doc); `    .nnames = 2,` — the 4-space initializer shape both new greps assume |
| `-o -` with `-p level_filter` | `    .pattern = "error\|warn\|fatal",` — the escaper's exact shape, so `^    \.name = ` and run.sh's `sed 's/.*= "\(.*\)",$/\1/'` are right; `int level_filter_search(` at column 0, which the rxtsource prefix check greps |
| `--features classes,named-groups` | ACCEPTED, stamps `PCREC_FEATURE_MODULES "classes,named-groups"` |
| `--features all,classes` | REFUSED: *"unknown module 'all' (names are --list-syntax's module column; also 'all', 'none', or a named set: std1)"* |

**The last two turned a report FINDING into a measurement and then found a
gap in this lane's own work.** §3.3 argued that a whole-spec word cannot
join a `features` UNION and that the resolver should restate no vocabulary
— now measured true. But checking it exposed that **the UNION branch had a
population of ZERO across every fixture**: `head_basic`'s union is
config-only (its block writes no `features`), and `three_configs` wrote
none at all. A branch nothing reaches is a green check measuring nothing —
this project's most-recorded check-design failure, committed by this lane
in its own new code. Closed: `three_configs` now carries `features
classes` on `baseline` and `features named-groups` on the block, and the
rxtsource section asserts all three artifacts stamp
`PCREC_FEATURE_MODULES "classes,named-groups"`. Neither module is
reachable from `error|warn|fatal`, so no answer moves and the agreement
control stays strict.

## Validation order, as RULED by the manager (2026-08-31 ~23:2x)

Re-pin FIRST, run the gate ONCE. The predicted-red (B) run would have been
a positive control of a gate whose detection ability is not in question
tonight (it fired correctly at the opt5s1 re-pin days ago), and that gate's
reference-compiler build is the long pole — paying it twice near midnight
buys nothing.

1. `make strict`
2. `make test-codegen` (PROCS=4, async)
3. `bash tests/rxtsource/run_rxtsource_tests.sh`, WALL-TIMED — the §5.5
   section-runtime delta the manager asked for
4. abi SITE 4: `tests/codegen/run_recursion_identity.sh`'s `FILEPIN`,
   `dc2c8ef` -> **`359fc99`**
5. the identity gate, ONCE
6. acceptance table filled with measured values, commit, DONE

If any red forces a src-touching fix, the FILEPIN moves to THAT fix's
commit and the gate re-runs — the normal ritual, not a deviation.

## The FILEPIN candidate, computed under the hold

The gate archives `src lib cli` from its pin, so "src-touching" means
those three trees. MEASURED on this branch:

- commits on `lane/w12` touching them: six, newest `359fc99`;
- `git diff --stat 359fc99..HEAD -- src lib cli` is **EMPTY**, so the
  subject tree and the pin share IDENTICAL compiler sources.

Two consequences worth having written down before the run:

- **(B) is expected byte-identical everywhere**, and for a stronger reason
  than "the change is scaffolding": subject and reference are built from
  the same `src`/`lib`/`cli`. A difference would mean the gate is not
  comparing what it believes it is.
- **The re-pin commit cannot move its own target.** It edits
  `tests/codegen/run_recursion_identity.sh`, which is not in `src`, `lib`
  or `cli`, so it does not become a newer "last src-touching commit" —
  there is no chicken-and-egg here.

**(A)'s pin is a DIFFERENT and UNMOVED one** — `REFCOMMIT` `ac4917d`, the
pre-`A_CALL`-producer commit — and this step does not touch it. (A) is
expected byte-identical because the two lines this change writes are
`rx_info` initializer lines, emitted BELOW `prog_region`
(`goto <p>_L0;` .. `<p>_accept:`) on every artifact.
