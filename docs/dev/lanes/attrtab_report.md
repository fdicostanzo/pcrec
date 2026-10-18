# attrtab — [ATTR-TABLE] one value-to-guarded-text table (2026-10-18)

Lane attrtab (opus), an opportunity lane, branch `lane/attrtab` from main
65dd423ee. Frank gave the build GO on 2026-10-18. Scope (the manager's
ruling): migrate the three other GNU-attribute writers onto E1's table so all
four read it; the plain `static inline` writers A4-A7 are out of scope. Hard
bar: zero movers, no abi event.

## 1. The table and its rows

The table moved out of `part_layout.c` (`layout_texts[]`) to its own file,
`src/gen/attr_text.c` (`attr_texts[]`), because four writers now read it and
it is no longer the part layout's. Its values are `PcrecAttr`
(`src/core/internal.h`, beside the part-layout block); the accessors are
`pcrec_attr_text`, `pcrec_attr_tok` and `pcrec_attr_writes`.

| value | text | read by |
|---|---|---|
| `PCREC_ATTR_AS_EMITTED` | "" | the part layout (P1/P2, T0 records) |
| `PCREC_ATTR_AUTO` | "" | the part layout (`auto`) |
| `PCREC_ATTR_SHARED` | `\n` + guarded `noipa`, `noinline` under `#else` | the part layout (`shared`, P4/P8) |
| `PCREC_ATTR_INLINE` | `inline __attribute__((always_inline)) ` | the part layout (`inline`); A1's `ai` and `ai_body` on the copying rungs |
| `PCREC_ATTR_NONE` | "" | A1 on the `plain` rung (both strings), `ai_body` on `shared`'s helpers' side |
| `PCREC_ATTR_NOINLINE` | `__attribute__((noinline)) ` | A1's `ai_body` on the `shared` rung; A2's `_deep` |
| `PCREC_ATTR_NOCLONE` | guarded `noclone`, nothing under `#else` | A3, every DFA search head |

A row is a VALUE, not a writer. A1's `always_inline` and the layout's `inline`
are the same bytes, so they share a row; so do A1's and A2's `noinline`. The
three empty texts are three rows because their tokens and descriptions differ
(the layout's listings print `as-emitted` and `auto`; `none` is A1's). No
writer needed bytes another writer with "the same" value did not already
write, so no value had to be split, and no spelling was harmonized.

The guard shape is stated once, as two macros: `ATTR_GUARD_PROLOGUE` (the
`#ifndef __has_attribute` fallback) and `ATTR_GUARDED(attr, alt)`, which
asks `#if __has_attribute(attr)` and takes the `#else` arm's text. The
`shared` and `noclone` rows are both built from it, and the bytes are the
writers' old literals exactly (checked by the sweeps, §3).

## 2. The writers migrated

Each keeps its own DECISION and asks the table only for TEXT.

| writer | site | was |
|---|---|---|
| A1 `en->ai` | `src/gen/emit_vm.c:10838` (`vm_plan_entry`) | `shape == PLAIN ? "" : "inline __attribute__((always_inline)) "` |
| A1 `en->ai_body` | `src/gen/emit_vm.c:10844` | the three-way ternary over `always_inline` / `noinline` / "" |
| A2 `_deep` | `src/gen/emit_comb.c:214`, `:222` | `"static __attribute__((noinline)) %s %s_deep(%s)"` in the format |
| A3 K24 | `src/gen/emit_dfa.c:1934` (`emit_search_head`) | the six-line guarded `noclone` literal |
| layout | `src/gen/part_layout.c:524` (`layout_attr`), `:657`, `:730`, `:751` | `layout_texts[p->layout].text/.tok/.writes` |

`layout_attr` maps the part rows' `PCREC_PART_*` value (0 = as-emitted) onto
the table's value; the render, the `--emit-facts` row and the `--list-axes`
row read through it.

The census (`tests/partlayout/writers.tsv`) gained a `text` column: A1, A2,
A3 and the three layout rows name their `PCREC_ATTR_*` value, A4-A7 say
`own`. `run_partlayout.py` checks that every named value is a row of
`src/gen/attr_text.c` (a new PASS line; the suite reads 49 checks, was 48).

`src/gen/CLAUDE.md` (Files: `attr_text.c`; the E1 section's "not migrated"
sentence), `tests/partlayout/CLAUDE.md` (writers.tsv) updated. The plan row
moved to `docs/dev/plan_completed.md` as `STATE:completed`
(`make test-plan-lint` 2/0).

## 3. Zero-mover evidence

Reference: a copy of main 65dd423ee's `build/pcrec`, built in this worktree
before the first edit, at `worktrees/attrtab/ref/pcrec-65dd423ee` (outside
`build/`, untracked). Tree: `build/pcrec` at the lane tip.

Light check done before the slot (same `-o` basename both sides): eleven
spot artifacts byte-identical, covering a DFA search head (noclone), the VM
entry rungs 1-4 (`--vm-entry-shape`, both `ai` strings), a capture and a
backreference program, `--part-residual=shared` and
`--part-layout=prefilter:inline` (the layout rows), `-fcomments`, and a
tiered artifact with `_deep` (`([a-z]+)+@`, `--engine=vm`).

The full sweep arms are **OWED** to the slot, run by the detached chain
`build/land/chain2.sh` (armed detached; it found main's `GO attrtab` line
in `worktrees/attrtab/attrtab_rulings.md` at 10:02 and is running; the
first waiter, `chain.sh`, matched only a line-initial `GO` and was stopped
with `scripts/safekill`). It re-reads that file before every
heavy step, stops on a `HOLD attrtab` line, and starts no step after
00:30). Each arm is
`scripts/emit_sweep.py --ref-bin ref/pcrec-65dd423ee --bin build/pcrec --jobs 8`
plus:

| arm | extra | log |
|---|---|---|
| plain, every stream | — | `build/land/sweep-plain.log` |
| start arms | `--arms start` (incl. `-e utf8`, `-i`, `-fmemfn-simd`, `-fcomments`, the null arm) | `build/land/sweep-arms-start.log` |
| utf8 | `--extra="-e utf8"` | `build/land/sweep-utf8.log` |
| VM | `--extra="--engine=vm" --no-differ-floor` | `build/land/sweep-vm.log` |
| comments | `--extra="-fcomments"` | `build/land/sweep-comments.log` |
| SIMD | `--extra="-fmemfn-simd"` | `build/land/sweep-simd.log` |
| part layout, all auto | `--extra="--part-layout=prefilter:auto,compound:auto,find:auto,wrap:auto --part-residual=auto" --no-differ-floor` | `build/land/sweep-part-auto.log` |
| part layout, controlled | `--extra="--part-residual=shared" --no-differ-floor` | `build/land/sweep-part-shared.log` |

**Plain arm, MEASURED** (chain started 10:02 on main's `GO attrtab`; rc 0,
73 s, self-check passed): 0 movers and 0 asymmetric on all eleven streams
(c-default, c-vm, emit-ir-vm, facts, emit-ir-auto and its three arms,
stderr, composition, dumps); argv population 5,790 at full reach,
composition 37 producing files / 106 artifacts, every tag floor held. The
other seven arms are OWED to the running chain.

The two part-layout arms and the VM arm have no DIFFER_PINS floor (their
DIFFER count against the base is expected nonzero and is not the claim);
identity between the reference and the tree is required on every stream.
The verdict of each arm is its log's rc, recorded in `build/land/chain.log`
as `sweep-ARM rc=N`. The completion line is `CHAIN COMPLETE`.

## 4. Sabotage rows

Derived with `docs/design/start_table/sabotage_anchors.py build/land/base
build/land/cg.tsv docs/design/start_table/refactor_edit_set.tsv --step
attrtab=65dd423ee..e13382b97` (base = `git archive 65dd423ee`, call graph from
`docs/design/start_table/call_graph.py`; exit 2 is the five pre-existing
UNRESOLVED sites S571, S640, S897, S906, S995, none in this lane's edits),
plus `scripts/m6read_check_sab_anchors.py`, which found three stale anchors.

RE-AIMED (their anchor was the moved text; intent unchanged, re-anchored on
the table row, `SAB_FILE` now `src/gen/attr_text.c`):

- **S1113** `shared` writes the inline text: the `shared` row's text becomes
  `inline __attribute__((always_inline)) `.
- **S1124** `noipa` unguarded: the `shared` row's text becomes a bare
  `__attribute__((noipa)) `.
- **S1119** K24's noclone dropped: the `noclone` row's text becomes "". Its
  `SAB_EXPECT=UNDETECTED` (the part-layout suite cannot see it) is unchanged.

RE-RUN (owner definition touched by the step's hunks): S1071, S1072, S217,
S439, S699, S902, S903.

NEW: **S1123** — one writer's guard altered in the table. The `noclone` row
keeps the prologue but asks `#if 1` instead of `#if __has_attribute(noclone)`,
so every DFA search head carries a bare noclone; the `shared` row is
untouched. Detector: the part-layout suite's `-Werror` leg's clang compiles
(clang: `unknown attribute 'noclone' ignored [-Werror,-Wunknown-attributes]`,
checked by hand on a one-line file). `SAB_DOC_FIGURE` is OWED to its run.

All eleven rows run SOLO in the chain after the sweeps
(`build/land/mech-S<id>.log`; each row's verdict is its own
`== mech run COMPLETE` trailer, summarized in `build/land/chain.log`). **OWED.**

`scripts/m6read_check_sab_anchors.py`: 814 sabotages / 841 sites, all
anchors resolve.

## 5. Validation run in the lane

- `make strict`: clean (whole tree, `-Werror -Wshadow`), at the tip.
- `make test-partlayout` (`tests/partlayout/run_partlayout_tests.sh`,
  JOBS=8, taskset 0-7): **49 passed / 0 failed**, 40 s, including the census
  over 3,483 artifacts, the new text check, and the `-Werror` leg with both
  clang legs (658 controlled texts).
- `make test-plan-lint`: 2/0.

## 6. make test

**OWED**: the chain's last step, `scripts/perfrun --label attrtab --
build/land/test.log`, after the sweeps and the mech rows. Verdict: `grep -E
'\*\*\* \[(Makefile:[0-9]+: )?test-' build/land/test.log` (empty = green)
read with `build/land/test.log.perfrun`; the chain log's `make test rc=`
line.

## 7. Notes

- No abi event and no spec hunk: no emitted byte is meant to move, and the
  table is internal. If any sweep arm reports a mover, the lane's claim is
  false and the row must be reopened, not re-pinned.
- The `ai`/`ai_body` gate comments in `emit_vm.c` (the `has_push`
  derivation, the `shared` rung's load-bearing `noinline`) stay at the
  decision; only the literal moved.
