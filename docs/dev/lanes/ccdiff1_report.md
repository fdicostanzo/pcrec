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

**`.lift` appeared 2026-09-03 ~11:1x; validation resumed. `make -j4 && make
strict` clean. `make test-codegen` went 3/5 (four `FAIL:` lines named below)
on its first post-lift run — none of them a defect in what shipped, all four
structural checks holding a fixed-text assumption the always_inline
attribute or the uniform-table fold moved:**

- **`[M6.2-KRESET rule 1]`/`rule 1b`/`rule 3`** (`run_codegen_tests.sh`):
  three `awk` extractors anchored on `^static void rx_report_captures(` /
  `^static ptrdiff_t rx_match_run(const rx_ctx *ctx`. Both `'a\Kb'` and the
  `\K`-free VM fixture are frameless, so spelling (a) prepends
  `inline __attribute__((always_inline)) ` before the return type and the
  rigid anchors stopped matching. Widened to accept the optional prefix.
- **`[agreement]`** (`run_dfa_stamps.sh`): the `unanch` (unanchored-scan)
  discriminator read `/rx_forward_next_state\[/` — the forward table's own
  declaration — which a folded machine no longer emits (31 corpus artifacts
  at the time this ran). Re-anchored on `forward_state = rx_forward_step\(`,
  the call site, which spelling (b) never removes (only the table argument
  drops) and which is unique to the unanchored shape (`attempt` dispatches
  by `goto *`, never a `_step(` call).
- **`[SABANCHOR]`**: `S74_reverse_termination_blind.sh`'s `SAB_BEFORE`
  pinned `dir_rev_bound_accept`'s literal text from before spelling (b)'s
  `fold_arg` refactor touched that same function. Re-derived from the live
  source (never `git show HEAD:<path>`, per that directory's own
  Conventions) and verified with `scripts/m6read_check_sab_anchors.py`
  (222 sabotages, all anchors resolve).

One self-inflicted bash syntax error along the way (an apostrophe inside the
single-quoted `awk` program broke `run_dfa_stamps.sh`'s own shell parse,
caught by the team lead's log read and fixed with `bash -n` on all four
touched files before the next re-run). **`make test-codegen` is now 5/5, 0
failures** (commits 973f048, 0c908c2). Re-derivation notes: none of these
four checks needed a moved BAR (a floor, a count, a byte figure) — each
needed a wider ANCHOR for text the emitter still writes, in the same shape,
just with an optional prefix or at a different (but equally exact) call
site. No check's actual claim weakened.

1. `tests/codegen/run_dfa_uniform_fold.sh`'s own corpus sweep — DONE, part of
   the green `make test-codegen` above (5/5 includes this section's checks
   via `make test`'s wider run; the K35 floor and both axes are asserted in
   that script itself, see §1/§2/§3 of its own header).
2. `make -j4 && make strict` — DONE, clean.
3. `make test-codegen` — DONE, 5/5 after the three fixes above.
4. `make -k -j4 test PROCS=3` (the manager's measured shape for this box,
   not `-j12`) — IN PROGRESS.
5. `make test-axes`.
6. The clang COMPILE gate over the whole corpus (refusal set must stay
   empty) — ccdiff1's `clanggate.sh`, `ROOT` repointed at this worktree.
7. Quiet-box acceptance re-measurement (STEP 0's paired-median method, 11
   rounds, ccdiff1's `accept.sh`): `dig-upto-16` thr/vm (target ≈0.611),
   `cls-upto-4` thr/auto (≈0.589), controls `floor` thr/vm (≈0.994),
   `level-context` search/auto (≈0.954), `stack-frame` search/vm (framed,
   ≈1.00 — no attribute) — WAITS for the manager to arrange a quiet box with
   the bench, per the brief; tell the manager before starting this one.

## 4. Handover from ccdiff1 (returned briefly, stood down again), and its
##    evidence re-verified against a FRESH build rather than trusted as-is

ccdiff1 came back once more and handed off, via the manager, ready-to-run
scripts and gathered evidence in its own scratchpad
(`.../scratchpad/ccdiff1/`), copied into this lane's own scratchpad
(`.../scratchpad/ccdiff1b/handover/`) per the scope mandate. Two artifacts:
`accept.sh` (STEP 0's interleaved-paired-median acceptance method, six cells
prebuilt under gcc/clang) and `clanggate.sh` (the corpus swept through the
bench's own shim line, not a bare compile) — both reviewed and correct in
method; `clanggate.sh`'s `ROOT` is hardcoded to `worktrees/ccdiff1` and MUST
be repointed at this lane's own worktree before running (never touch that
tree per the mandate).

**A staleness catch, before trusting the relayed byte-identity numbers.** The
handover's own `art/` snapshot (`sweep.sh`'s answer-identity artifacts,
`stack-frame-vm.{b,n}.c` etc.) shows `stack-frame-vm.b.c` and `.n.c` as
byte-identical INCLUDING `.abi = 16` on BOTH sides — which cannot be a
same-session `.abi 16` vs `.abi 17` comparison and does not match even the
weaker claim relayed ("differs only by the `.abi` line"). Traced: those
specific files were generated at a point in ccdiff1's session before its own
worktree binary had been rebuilt past the abi-bump commit — a snapshot
staleness, not a defect in what shipped (`/home/duxevents/pcrec/worktrees/
ccdiff1/build/pcrec` reads `.abi = 17` NOW, when checked directly).

**So the three "byte-identical modulo stamp" claims were RE-DERIVED here,
fresh, against this lane's own build at 885846f (abi 17) vs the pinned
pre-change reference `.../scratchpad/ccdiff1/base/build/pcrec` (abi 16),
rather than accepted from the stale snapshot:**

| cell | pattern source | result |
|---|---|---|
| `stack-frame` search/vm | `bench/loglines/patterns/stack-frame.rx`, `--engine=vm` | differs ONLY by `.abi = 16` → `17`; `RX_VM_FRAMELESS 0` both sides (framed, no attribute — matches the STEP 0 control prediction) |
| `level-context` search/auto | `bench/loglines/patterns/level-context.rx` | differs by `.abi` AND one new line, `#define RX_DFA_UNIFORM_FOLDS 0` — no fold fires on this pattern, so twin V's earlier 0.95 prediction (which attributed framed VM helpers too) is correctly superseded by the shipped, more conservative gate |
| `nest3-16` thr/vm | `bench/bounded/patterns/nest3-16.rx`, `--engine=vm` | differs ONLY by `.abi` |

**The two size-delta headline claims, also independently re-measured** (fresh
build, `gcc -O2 -fPIC -shared`, same two patterns as the CLAUDE.md doc):
`\d{1,16} --engine=vm`: `nm` confirms neither `rx_search_run` nor
`rx_match_anchored` survives as a symbol in the new build (both absorbed);
whole-`.so` `.text` **3454 → 3010 bytes** (net shrink, confirming the
"absorbing the callees shrinks the artifact" claim — the exact `rx_search`-
only figure quoted elsewhere, 1561→1417, was not reproduced byte-for-byte by
this lane's cruder `objdump`-line-count method and is left as ccdiff1's own
measurement rather than double-counted here). `[a-z]{0,4}` default engine:
`RX_DFA_UNIFORM_FOLDS 4` confirmed, `rx_search` disassembly line count
**81 → 46** (EXACT match to the CLAUDE.md figure), whole-`.so` `.text`
**3080 → 2180 bytes**.

**Answer identity spot-checked** on these same two fresh artifacts (not the
full 6,969-comparison sweep, which is `.lift`-gated): `search`/`match`/
`findall` regimes, base vs new, `dig` and `cls` cells — all six comparisons
identical.

**Scope decisions relayed as settled, not re-opened**: the fold covers only
`<m>_next_state`/`<m>_is_accepting`; the wide accept table is a named,
deliberate follow-up; `RX_VM_INLINE_CHAIN` stays rejected
(`RX_VM_FRAMELESS` carries it by construction); the bench shim's
`PB_SHIM_MIN_ABI` is 15, so abi 17 clears it with no bench-side change
needed.
