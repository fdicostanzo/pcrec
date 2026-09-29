# ucpu3 — [UCP] U2 landing: the anchored dead-entry fix, the premul-table check rewrite, the triage merges

Lane `ucpu3` (opus, engine tier), branch `lane/ucpu3` from `lane/ucpu2`
`61cbc894` (abi 46), 2026-09-29. Scope held: the pcrec repo only, this
worktree; scratch in `/tmp/ucpu3s/` (never committed). Inputs:
`ucpu2_report.md`, `triu2_report.md` (§4 the bug, §5 the premul gaps),
`tri220_report.md`.

## 0. Summary

| item | state |
|---|---|
| 1. merge `lane/triu2`, `lane/tri220` | both merged clean, each `git merge` run alone |
| 2. the anchored dead-entry bug | FIXED in `src/gen/emit_dfa.c`; not an abi event (§2.4); regression witness `tests/anchored/run_anchored_dead_entry.sh` |
| 3. the 2 DIVERGE patterns | the reporter now lists each kind separately. The 59 bad patterns are the dead-entry population, and the fix clears all of them (§3) |
| 4. `test-premul-table` gaps (i) + (ii) | check logic REWRITTEN, nothing re-pinned. 68 false reports → 0, and both sabotages fire (§4) |
| 5. delete `lane/triaxes` | the branch does not exist, so there was nothing to delete |
| 6. validation | see §6: targeted sections done; full `make test` + `make test-axes` are OWED (log paths there) |

## 1. Merges

`git merge --no-edit lane/triu2` (ort, clean: the triu2 report, the CHECK 2b
allowlist, and the §9 force-axis floor 20 → 12), then `git merge --no-edit
lane/tri220` (ort, clean: the tri220 report and S220's
`SAB_EXPECT=UNDETECTED` → DETECTED flip). Neither merge had a conflict or
left a MERGE_HEAD.

## 2. The bug: an anchored machine entered at the dead state

### 2.1 Mechanism (triu2 §4, confirmed)

`emit_scan_loop` runs the accept probe first in the loop and the dead test
last. Its three callers are the forward search, the reverse pass, and
`emit_anchored_match_def`. The anchored machine has no start-anywhere
self-loop. So when a match needs a left context, its no-context start `s0`
(used at pos 0) is the dead state, and so is any seed cell whose context byte
cannot satisfy it (`(?<=a)b`: `seed_state = {-1, 0, -1}`, and the initializer
falls back to `: -1`). The first accept probe then reads
`is_accepting[-1]`, or `is_accepting_by_class[-2..]` on the wide-accept form.
That is undefined behaviour.

### 2.2 The fix, and why this shape

The general fact is that **a machine entered at the dead state has no
match**. The loop cannot express it, because its first statement is the
accept read. So the entry expresses it, once per call and off the loop:

- `DfaDir` gains a field, `dead_entry`: the direction's own "no match"
  statement. It is `"return -1;"` on the anchored direction, `"return 0;"`
  on the forward search (its `range_guard`'s value), and NULL on the reverse
  direction.
- `emit_scan_loop` emits `if (<p>_<m>_is_dead(<state>)) <dead_entry>`
  immediately after `emit_init`, but only where
  `dfa_entry_can_be_dead(d)` holds. That predicate is true when `s0` is dead
  or when the emitted seed table has a dead cell.
- `dfa_seed_has_dead` is the seed half of that predicate. It is factored out
  of `dfa_premul`'s seed precondition, which asked exactly this question to
  avoid the same hazard in the premultiplied form (its 2026-08-26 comment
  called the `[-1]` read "not [OPT-3]'s to answer"). Both readers now share
  one derivation.

**Why (b), a check at entry, and not (a), a dead guard before every accept
probe.** Shape (a) taxes the per-byte loop of every machine to answer a
question that only exists at entry: after the first step, the loop's own
dead test at the bottom already guarantees that the state at the top is
live. Shape (b) is the general fact placed where it is decidable. It is
gated by a static machine property, not by a construct: no `lookbehind`
clause, and no anchored-only branch in the loop. It is also a direction
field in the same style as `range_guard`, so a fourth direction states its
own "no match" as data.

**Why the reverse direction is NULL, and why that is not a special case.**
The reverse walk starts at an end that the forward pass accepted. That
acceptance read the same right-hand context that the reverse seed reads, so
the reverse entry is live by construction. (U2's own `dfa_s0_cell` comment
makes the same argument for `z(?=a)`'s dead reverse `s0`.) The ASan sweep in
§2.5 tested this empirically: no reverse or forward read failed. A reverse
`dead_entry` would add one guard to every lookahead's reverse machine for a
state that the caller proved unreachable.

### 2.3 The other entries share nothing

- **`_match_caps`** delegates to `_match`, so the fix covers it.
- **The `_in` siblings** are exactly calls to their un-suffixed siblings
  (verified in the emitted text).
- **The forward search**: `dfa_entry_can_be_dead` is false on every forward
  machine in the corpus. The unanchored wrap's self-loop thread keeps every
  seed and `s0` live. The byte-diff in §2.4 shows no forward line emitted
  anywhere.
- **The reverse pass**: see above.
- **ENG_ATTEMPT**: dispatches through `&&<p>_dead` labels, so it never
  indexes an accept table with a dead state.

Measured over the ASan sweep (§2.5): every pre-fix failure was in `on_match`.

### 2.4 Not an abi event

Only emitted code logic changes, and only on the affected population. Every
changed artifact gains exactly ONE line and nothing else:
`    if (<p>_anchored_is_dead(anchored_state)) return -1;`. There is no
comment, no declaration, and no layout change.

Measured by a pre/post byte diff of every corpus pattern
(`--features all`, `/tmp/ucpu3s/bdiff.sh`, log `/tmp/ucpu3s/bd_all.log`):
of 3,489 patterns, 3,037 are byte-identical in `.c` and
`.h`, 398 are refused by both compilers, and **54 change, each by exactly one
added line, and every one of those lines is the anchored `dead_entry` guard**
(the forward search's guard never fires). The 54 are the one-character
lookbehind family: `(?<=…)`, `(?<!…)`, `(?<*…)`, and their `(*plb:`,
`(*nlb:`, `(*naplb:`, `(*positive_lookbehind:`… spellings, plus
`(*UCP)(?<=\w)x`.

The changed population is the one that had undefined behaviour at abi 46,
and abi 46 itself is not on main: it is U2's bump, landing in the same merge
as this fix. So no shipped abi-46 artifact moves. No scaffolding changed,
which means no D76/D94 bump and no re-pin.
`make test-codegen` (which holds the identity gate) is the confirmation:
see §6.

### 2.5 Measured before and after

An ASan+UBSan probe (`/tmp/ucpu3s/probe.c`, `sweep.sh`) ran over every
corpus pattern with a context construct: 1,722 patterns (lookaround, `\b`,
`\B`, anchors), `--no-captures`, default engine. It called `_search` and
`_match` at every position of every subject over `{a,b,z,space,\n,x}` up to
length 3.

| compiler | OK | DFA failures | VM failures |
|---|---|---|---|
| `lane/ucpu2` + merges (pre-fix) | 1,445 | **59** (56 ASan global-buffer-overflow in `on_match`, 3 UBSan out-of-bounds load in the inlined wide-accept probe) | 16 |
| `lane/ucpu3` (fixed) | 1,504 | **0** | 16 |

The 16 VM failures are identical before and after, and they are not
findings. They are `${var}` patterns, and the probe passes `ctx.vars ==
NULL` to an artifact that dereferences its bound variables (a probe misuse,
out of scope).

### 2.6 The regression witness

`tests/anchored/run_anchored_dead_entry.sh` plus `dead_entry_driver.c`, run
in `make test-anchored-match` and listed in `tests/lib/san_scripts.txt`.

- **Witnesses**: `(?<=a)b`, `(?<*a)b` and `(?<!a)b`. Each is asserted to
  select the DFA engine and the unwrapped form.
- **[reach]**: each witness must start dead, read off its own emitted seed
  table and initializer. `(?<=a)b` and `(?<*a)b` start dead both at `s0` and
  at a seed cell; `(?<!a)b` starts dead at a seed cell only.
- **[answer]**: `_match` and `_match_caps` (span included) are checked
  against python3 `re` on 23 cells per witness (every position of 8 subjects,
  pos 0 included).
- **[asan]**: the same cells under `-fsanitize=address`. This arm SKIPS
  LOUDLY where the compiler cannot build ASan.

Both directions were measured:

- **fixed**: 7/0.
- **unfixed compiler** (`/tmp/ucpu3s/pcrec.pre`): 1/6. [answer] fails on all
  3 witnesses (SIGSEGV, rc 139) and [asan] fails on all 3
  (global-buffer-overflow, 1 byte before `on_anchored_is_accepting`).

## 3. The two DIVERGE patterns

**The check fix.** `run_anchored_diff.sh` gave four kinds of failure detail
line one shared `BAD: ` prefix, and read them back with `grep -m6`, so 57
crash lines filled all six slots. Each kind now carries its own tag
(`BAD_DIVERGE:`, `BAD_INFRA:`, `BAD_CC:`, `BAD_ASYM:`), each reporter greps
only its own, and the DIVERGE list is uncapped.

**What the two were.** The ASan sweep's pre-fix DFA population is exactly
**59 = 57 + 2**, which is the count triu2 logged (57 crashes + 2 DIVERGE).
I re-ran the diff driver (`anchdiff_driver.c`, the script's own grid) over
those 59 patterns on the pre-fix compiler. 57 exit 139. The other two,
**`(?<=\d)(?=\d)`** and **`(?<=x)(a|b)(?1)`**, exit 0 in that standalone
run, but ASan flags both as the same out-of-bounds accept read
(`(?<=\d)(?=\d)` through the wide-accept probe).

So they are the same undefined behaviour. Whether a read one element before
the table crashes, silently diverges, or happens to agree depends on
whatever byte precedes the table. That explains why the full-suite run saw a
divergence and this run did not. The attribution is by population identity
(59 = 57 + 2, the same set) plus ASan's direct report on both patterns. It
is not a transcript of the original run naming them: that run's log never
printed their names.

After the fix, `run_anchored_diff.sh` reads 0 DIVERGE and 0 INFRA (§6), with
the new reporter in place.

## 4. `test-premul-table`: the check logic rewritten

**(i) Three machines.** `read_artifact` now reads the anchored machine
(`rx_anchored_next_state` type and length, its accept table, its token
typedef and step accessor) off the emitted text, and never off the
`RX_DFA_MATCH` stamp. `implied_stamp` is now a fold over a SET of machine
forms, not a two-machine case table: it answers none, premultiplied,
indexed, or mixed over whatever machines are passed. The `[bound]`,
`[accept]`, `[shape]` and token-leak arms cover the anchored machine too.

**(ii) The seed clause.** `[bound]`'s rule is now: premultiplied IFF
`states*classes <= PREMUL_MAX_ENTRIES` AND the seed table holds no dead
cell. The dead-cell fact is read from the emitted seed cells in BOTH
spellings: `-1` in the indexed form and `PREMUL_DEAD` in the premultiplied
form. Reading both spellings means a premultiplied machine that should have
declined is SEEN, not hidden by its own encoding. That fact comes from the
artifact, not from `dfa_premul` or `dfa_seed_has_dead`, so the control does
not share a source with the choice (learnings §3). Every `[bound]` failure
now prints a per-machine `BOUND` line that names the direction and which
clause failed.

**Results** (`tests/codegen/run_premul_table.sh` run directly; logs in
`/tmp/ucpu3s/premul_*.log`):

| compiler | result |
|---|---|
| fixed | **16/0**. `[agreement]` 2,674 artifacts, `[bound]` clean with 68 machines indexed by the seed clause, 1,263 anchored machines read. (Before: `[agreement]` 51 + `[bound]` 17 = **68 false reports**) |
| SABOTAGE A: `dfa_table_name` drops its anchored clause (`0 &&`) | **15/1**. `[agreement]` red on 51, e.g. `(*nlb:a)b` stamps "premultiplied", tables imply "mixed" |
| SABOTAGE B: `dfa_premul` drops the seed clause | **15/1**. `[bound]` red on 68, e.g. `(*nlb:a)b dir=a: premultiplied at 6 entries, seed-dead=1` |

The sabotages were built in scratch copies (`/tmp/ucpu3s/sabA`, `sabB`) and
never touched the tree.

**Spec hunk** (`docs/spec/match_api.md`, the `_DFA_TABLE` value table): the
`"mixed"` row said "the forward and reverse machines", which has been stale
since [ENG-ABS]. It now names all three machines and the seed clause. This
is a correction to match existing behaviour, not a behaviour change.

## 5. `lane/triaxes`

`git branch --list lane/triaxes` is empty and no worktree has that name, so
there was nothing to delete.

## 6. Validation

VALIDATION_TABLE

## 7. For a follow-up

- **Optional mech row.** A mech sabotage row for the `dead_entry` emission
  (plant: skip the `if (f->dir->dead_entry && …)` emission; expected red:
  `test-anchored-match`). It would re-measure what §2.6 already measured by
  hand. It is not added here; the highest S-id on main must be checked
  before numbering it.
- **Not attempted: re-deriving S220's population.** tri220's owed item
  (re-derive S220's "exactly N" P2 population) is untouched by this lane.
