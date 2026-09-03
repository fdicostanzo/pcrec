# [CC-DIFF] STEP 1 — lane ccdiff1

Both emitter spellings STEP 0 measured, landed as ONE abi event (16 -> 17).
Chartered by Frank 2026-09-03. Worktree `worktrees/ccdiff1`, branch
`lane/ccdiff1`, base `580f1a0`.

## 1. THE PREDICTION TABLE — written BEFORE the census

Recorded here first, per the brief, so the census can refute it.

| prediction | basis | value |
|---|---|---|
| VM-route artifacts gaining the attribute | = `RX_VM_FRAMELESS 1`; vmfl0's census (`optvmfl_step0.md`): 1,090 `frames==1 ∧ frameless` + 198 `frames>1 ∧ frameless` of 2,603 VM-compiled corpus+bench artifacts | **1,288 (49.5 %)** |
| ...of them reached under `auto` rather than `--engine=vm` | vmfl0: 385 of the 1,090 (290 as hybrids, 95 plain) | **385** |
| FRAMED artifacts whose bytes move | none: the gate is `has_push`, and the attribute is the only change on that route | **0, the abi stamp aside** |
| DFA-route artifacts folding >= 1 table | STEP 0 §2(d): 22 of 90 `auto` artifacts across bounded/loglines/altwide/email | **~24 %** |
| the folded artifact's own shape | `cls-upto-4` measured by hand before the census: 403 -> 373 source lines, 4 folds | **-30 lines, `_DFA_UNIFORM_FOLDS 4`** |
| direction of the emitted-size books | DOWN on folded DFA artifacts (a table and its legend leave), UP by a few bytes per header on frameless VM artifacts (the attribute text) | **both, opposite signs** |
| object code, frameless VM (`dig-upto-16 --engine=vm`) | STEP 0 §3-6: frame + canary + out-of-line call go | **`sub $0x98,%rsp` gone, `%fs:0x28` gone, `rx_search_run`/`rx_match_anchored` absent from `nm`** |
| object code, folded DFA (`cls-upto-4` auto) | STEP 0 §1: the table-base `lea`s and the frame go | **0 table `lea`s, 0 pushes in `rx_search`** |

## 2. WHAT LANDED

**Continuation lane ccdiff1b (sonnet) took over at 37549a1** after ccdiff1
(opus) lost four consecutive turns to API overloads. Everything through
37549a1 (11 files, +971/−64, commits 7e22924..37549a1) is ccdiff1's; this
section records ccdiff1b's own verification and the gaps it closed.

**(a) `always_inline` on the VM entry chain**, gated on `<PREFIX>_VM_FRAMELESS`
(`src/gen/emit_vm.c`): the eight statics `<prefix>_run_state_bind`,
`_run_state_init`, `_reset_for_next_attempt`, `_match_anchored`,
`_report_captures`, `<prefix>_search_run`, `<prefix>_match_run`,
`<prefix>_match_caps_run` gain `static inline __attribute__((always_inline))`
reading the SAME `has_push` bool the stamp reads — one `ai` string, no second
predicate. A FRAMED artifact is byte-identical to abi 16, this stamp aside.

**(b) The uniform-table fold** (`src/gen/emit_dfa.c`): `tr_cell`/`acc_cell`/
`accw_cell` factored out as the one derivation both the table emitter and
`fold_tr`/`fold_acc` call; a folded `<m>_next_state`/`<m>_is_accepting` is not
emitted and its `_step`/`_accepts` accessor returns the constant, keeping the
state/class parameters (the class expression can consume a byte) and dropping
only the table pointer, via `fold_arg` at every one of the four call sites
(`acc_emit_probe`, `acc_emit_tail_scalar`, `acc_emit_tail_by_class`'s tr half,
`dir_fwd_bound_accept`, `dir_rev_bound_accept`). `<PREFIX>_DFA_UNIFORM_FOLDS`
counts the folds (0..6) over the machines the artifact actually contains,
composed by `dfa_table_name`'s own rule (forward always, reverse unless
`RX_DFA_START "pinned"`, anchored under `RX_DFA_MATCH "unwrapped"`).

**abi 16 → 17, ONE event for both spellings** (D76/D94). `.abi = 17` at
`src/gen/emit_dfa.c:1603`.

### 2a. The read-site audit ([CC-DIFF] STEP 1(b)'s missed-reader risk)

Every emitted reader of `<m>_next_state`/`<m>_is_accepting` (excluding the
WIDE `_is_accepting_by_class` table, deliberately out of scope — see
`emit_dfa.c`'s own comment above `tr_cell`) was grepped and traced by hand,
not assumed:

- **Emission**: `token_step`/`token_accepts` (both `token_premul` and
  `token_indexed` representations) — the ONLY two sites that write a
  `_step`/`_accepts` accessor definition. `emit_machine_tables` skips the
  table (and its comment/legend) entirely when `f->tr_fold`/`f->acc_fold` is
  folded.
- **Reads (scalar accept + step)**: `acc_emit_probe`, `acc_emit_tail_scalar`,
  `dir_fwd_bound_accept`, `dir_rev_bound_accept` — all four route their table
  argument through `fold_arg`, confirmed by grep (`grep -n '_step(\|_accepts('
  src/gen/emit_dfa.c` finds no call site outside these four plus the two
  emission sites).
- **Read (class-indexed accept + step, `acc_emit_tail_by_class`)**: the `_step`
  call routes through `fold_arg`; the class-indexed `_accepts_class` call is
  UNCHANGED (it reads the WIDE table, out of scope by design).
- **The reverse machine, the scan edge, the skip loops**: `dir_rev_bound_accept`
  covers the reverse machine's own accept read; the scan edge
  (`dfa_scan_edge_name`/`emit_dfa_scan_stamps`) and the skip loops
  (`acc_emit_tail_scalar`'s bound-accept path) share the SAME `token_step`/
  `fold_arg` call sites above them — there is no separate table-read spelling
  for either, confirmed by grep (`next_state\|is_accepting` outside the
  covered sites returns only prose comments and the `dfa_table_name`/legend
  machinery, `emit_dfa.c:295-297`'s doc-comment listing the macro NAMES).
- **VM hybrids inline the SAME emitter**: `emit_vm.c` calls
  `pcrec_emit_dfa_engine`/`pcrec_emit_dfa_scan_stamps` (the same functions a
  pure-DFA artifact uses) rather than duplicating any table/accessor text —
  confirmed by grep, `emit_vm.c` contains no `next_state`/`is_accepting`/
  `_step(`/`_accepts(` token anywhere.
- **The ENG_ATTEMPT direct-threaded emitter** (`\A`/`^`-anchored patterns)
  reads its own WIDE `_is_accepting_by_class` table by bare subscript at
  `emit_dfa.c:5947` — a different mechanism with no accessor and no
  transition table at all, which is why `dfa_uniform_folds()` returns 0 for
  `PCREC_ENG_ATTEMPT` (checked explicitly, `emit_dfa.c:2988`).

**Compile-checked** (pre-`.lift`, single artifacts, `gcc -O2 -Wall -Wextra
-Werror -std=gnu11`, `gen_cc`): `[a-z]{0,4}` (folds 4, bounded-class,
axis-J-pinned so no reverse machine), `(?:foo[a-z]{0,4}bar)\z` (whole-subject
end-anchored, no fold — the leading literal breaks uniformity), `(?m)^[a-z]
{0,4}$` (multiline, no fold — the `(?m)` class refinement breaks it) — all
three clean, zero warnings. Also `.{0,4}` (folds 4, forward+anchored) and
`x.{0,4}` (0 folds, but exercises all THREE machines — forward, reverse AND
anchored — together, since `x` breaks pinning) to widen the machine-population
coverage beyond the three brief-named shapes; also clean.
`tests/codegen/run_dfa_uniform_fold.sh` (ccdiff1's own delivery — §1 named
witnesses, §2 the VM-non-carrier and forced-hybrid IFF, §3 the corpus sweep +
K35 floor) is the exhaustive version of this same audit and is OWED at
`.lift` (a corpus sweep is a suite by the box rule); everything above is the
pre-`.lift` version of the same claim, checked by hand against the emitter's
own call graph rather than assumed from the test script's existence.

### 2b. The abi site list, BY GREP (D94)

`grep -rn '\.abi = 16\|abi 16\b' --include='*.md' --include='*.c' --include='*.sh' .`
(excluding gitignored `worktrees/`) over the whole tree. Live readers, all
updated by ccdiff1:

| site | file:line | state |
|---|---|---|
| the stamp itself | `src/gen/emit_dfa.c:1603` | `.abi = 17` |
| the identity gate's (B) pin VALUE | `tests/codegen/run_recursion_identity.sh` `FILEPIN` | left at `da4fe60` (abi 16) deliberately — the manager's to re-pin at merge (D76/D94, opt5i's precedent) |
| the identity gate's (B) pin COMMENT + the new (A) structural note | `tests/codegen/run_recursion_identity.sh:505-543` | narrates 16→17 in kind alongside every prior bump; ccdiff1b ADDED a structural correction here (§3 below) |
| the test's own `ABI_EXPECT` literal + narrative | `tests/codegen/run_codegen_tests.sh:2748-2750` | `ABI_EXPECT=17`, narrative extended with the `(16->17 -- ...)` clause |
| `docs/spec/match_api.md` §6 caller-facing `abi` paragraph | `match_api.md:159-166` | `` `17` `` |
| `docs/spec/match_api.md` §6.3's `rx_info.abi` prose paragraph | `match_api.md:1691-1725` | rewritten with the (a)/(b) split, "No answer moves on either half" |
| `docs/spec/match_api.md` §6.3's `RX_DFA_TABLE` cross-reference | `match_api.md:2018-2033` | new paragraph: the encoding stamp survives a full fold |
| `docs/spec/match_api.md` §6.3's new `RX_DFA_UNIFORM_FOLDS` entry | `match_api.md:2060-2100` | new (b)-family macro entry |
| `docs/spec/match_api.md` §6.3's `RX_VM_FRAMELESS` entry, second-fact addendum | `match_api.md:2142-2153` | records that `1` now ALSO means the entry chain is inlined; `_VM_INLINE_CHAIN` REJECTED |
| `docs/spec/tuning.md` §3's DFA-stamp catalog | `tuning.md` (after the `RX_DFA_TABLE` bullet) | **MISSING at 37549a1 — ADDED by ccdiff1b** (§3 below): every other `RX_DFA_*` stamp (`_SCAN`, `_PREFILTER`, `_TABLE`, `_MATCH`, `_SCAN_EDGE`, `_START`) has a §3 catalog bullet with its own axis/population census; `_DFA_UNIFORM_FOLDS` had none |
| `src/gen/CLAUDE.md` | new `## [CC-DIFF] STEP 1` section | present, reviewed, accurate (spot-measured, §4 below) |
| `tests/codegen/CLAUDE.md` | `run_dfa_uniform_fold.sh` entry | present, reviewed against the script — accurate |
| `docs/dev/lanes/CLAUDE.md` | `ccdiff1_report.md` row | present |

No OTHER reader of the bare token `16` in an abi-adjacent context turned up
live (the remaining grep hits are `docs/dev/dev_journal.md`,
`docs/dev/lanes/opt5i_report.md`, `docs/dev/reviews/*.md` — append-only
historical narration of the PRIOR bump event, correctly left alone).

### 2c. A finding: (A) is untouched by BOTH spellings, not just the VM one

`run_recursion_identity.sh`'s original comment (37549a1) read: "(A) is
untouched on the VM half ... and DOES move on the DFA half wherever a table
folds." **Checked by byte offset against the emitter rather than trusted**:
`prog_region()` (that script) extracts only the span from `goto <p>_L0;` to
`<p>_accept:` — the VM program body. Spelling (a)'s eight statics are all
defined ABOVE that span (`_run_state_bind` at `emit_vm.c:9309`, well before
"the program" begins at `emit_vm.c:9425`). Spelling (b)'s fold lives inside
`pcrec_emit_dfa_engine`, which for a hybrid is called from `emit_vm.c`'s own
prefilter block (`:9421`) — ALSO before the program marker — and a non-hybrid
DFA artifact has no `goto <p>_L0;` at all, so `prog_region()` reads empty on
both sides regardless of what the DFA scan emits. **Neither spelling can move
comparison (A).** Verified by hand on a built hybrid (`(x)[a-z]{0,4}\z
--engine=vm -fprefilter`, `DFA_UNIFORM_FOLDS 0` on that particular pattern,
but the table/accessor block's POSITION relative to `goto rx_L0;` is a
structural fact of the emission order, not of fold content — the DFA prefilter
block is always written before "the program" comment regardless of what it
contains). Fixed in `run_recursion_identity.sh`'s own comment; the corpus
sweep at `.lift` should confirm `rdiff=0` on all five axes as a NULL result,
which is itself worth reporting (a wrong prediction caught before it cost a
validation cycle chasing a phantom regression).

### 2d. `docs/spec/tuning.md` §3 gap closed

Every other `RX_DFA_*` stamp (`_SCAN`, `_PREFILTER`, `_PREFILTER_OFFSETS`,
`_TABLE`, `_MATCH`, `_SCAN_EDGE`, `_START`) has a tuning.md §3 catalog bullet
alongside its `docs/spec/match_api.md` §6.3 contract entry — match_api.md is
the contract (D80's minimum), tuning.md §3 is the curated stamp-by-stamp
reference with axis/population notes. `RX_DFA_UNIFORM_FOLDS` had a match_api.md
§6.3 entry but no tuning.md §3 bullet at 37549a1. Added, following the same
shape, noting explicitly that unlike its neighbors it has NO §2 tuning axis
(no pass decides the fold, no `-fno-` flag denies it — `RX_VM_FRAMELESS`'s
reasoning, not a new one).

## 3. WHAT REMAINS (owed at `.lift`, box rule: one heavy suite at a time)

1. `tests/codegen/run_dfa_uniform_fold.sh`'s own corpus sweep (§3 there — the
   K35 floor, both default and `-fprefilter` axes) — the exhaustive version
   of §2a above.
2. `make -j4 && make strict` in this worktree.
3. `make test-codegen` (re-derive every moved size/structural check with its
   cause named, per D94 — comparison (A)/(B) in `run_recursion_identity.sh`
   is the one already known to move, predictable now per §2c/§2b).
4. `make test` (K44's two cells may red under `-j12`: re-run solo, cite K44
   rather than treat as new).
5. `make test-axes`.
6. The clang COMPILE gate over the whole corpus (refusal set must stay
   empty) — a ~10-minute sweep of this lane's own.
7. Quiet-box acceptance re-measurement (STEP 0's paired-median method, 11
   rounds): `dig-upto-16` thr/vm (target ≈0.611), `cls-upto-4` thr/auto
   (≈0.589), controls `floor` thr/vm (≈0.994), `level-context` search/auto
   (≈0.954), `stack-frame` search/vm (framed, ≈1.00 — no attribute).

None of the above can run until `.lift` exists (tt12b's timed harness
measurements own the box until then) or without the manager's go-ahead on a
quiet box for item 7. This lane's own hourly cron (`47 * * * *`) polls
`.lift` and resumes automatically.
