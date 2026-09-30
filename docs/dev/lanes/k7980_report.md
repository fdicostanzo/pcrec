# Lane k7980 — K79 (prefix-invariant selection) and K80 (mixed-abi TU), one abi event 53 -> 54

Branch `lane/k7980`, from `lane/s2tri` at `9cf5034b` (abi 53). Worktree
`worktrees/k7980`. Decision D143. Sabotage rows S437 and S438.

## Summary (resume from here)

- **K79 cause.** `vm_plan_entry` (src/gen/emit_vm.c) chose the VM entry
  shape by comparing `pcrec_sb_len_uncut(&job->vmsb)` against the
  4,096-byte knee. That length is the emitted program TEXT, and the prefix
  occurs in it many times (57 times in the witness `(foo|bar)[0-9]{2,5}(x)`:
  2517 + 57 x 21 = 3714, 2517 + 57 x 58 = 5823, the pfx0 numbers exactly).
  The size term's trigger, its ladder and both emitted-size caps
  (src/core/compile.c) measured prefixed text the same way.
- **K79 fix (the general form).** The emitters never see the caller's
  prefix. `compile_driver` gives them a two-byte placeholder `\x01q` as
  `opt->prefix` (upper `\x01Q`, by the ordinary `toupper`), and
  `pcrec_sb_render_prefix` (src/core/sb.c) writes the real spelling onto the
  finished `.c`, `.h` and `--emit-ir` listing after every decision.
  Diagnostics render in `pcrec_ctx_fail`, and the facts hook sees a
  real-prefix view. Every length decision is prefix-free by construction,
  including ones added later. `-p rx` output is byte-identical to before.
- **K80 fix.** The guard is `#define PCREC_RX_ABI_H 54`, and the block opens
  with `#if defined(PCREC_RX_ABI_H) && (PCREC_RX_ABI_H + 0) != 54` /
  `#error "pcrec: this artifact (abi 54) shares a translation unit with an
  artifact of a different abi; regenerate both with one pcrec"`.
- **Checks.** `tests/codegen/run_prefix_invariance.sh` (new, in
  `test-codegen`, mech arm `prefixinv`, row S437). K80-a/b/c cells in
  `run_codegen_tests.sh` (row S438 on `codegen`).
- **Validation:** light targets only, as briefed; the full suite is the
  manager's. Results are in the "Validation" section below.

## K79 — the cause, measured

Pre-fix compiler (branch point, built from `git archive 9cf5034b`), the
pfx0 witness at `-p rx` / 23 / 60 characters:

| prefix | `VM_PROGRAM_BYTES` | `VM_ENTRY_SHAPE` |
|---|---|---|
| `rx` | 2517 | inline |
| 23 chars | 3714 | inline |
| 60 chars | 5823 | plain |

The growth is exactly 57 x (prefix length - 2): the measure is the program
text, and the program spells the prefix 57 times.

**Population census on the pre-fix compiler** (500 randomly sampled distinct
corpus `pattern` lines, seed 7, `--features all`, `-p rx` against a
60-character prefix, comparing ENGINE, ENGINE_SEL, VM_PREFILTER,
DFA_MATCH, UNROLL_K, UNROLL_K_WHY and VM_ENTRY_SHAPE):

- 16 patterns (default route) and 19 (`--engine=vm`) took a different
  entry shape: `inline` -> `plain`, or `forward` -> `shared`.
- No other stamp in that list flipped in the sample. The size term's
  trigger and caps read prefixed text too. They sit far from every corpus
  artifact (the caps are failsafes, D84 addendum 3), so the sample shows no
  flip there. They are fixed by the same mechanism anyway.

## K79 — the fix

**Why a placeholder and not a per-decision correction.** Several hundred
sites put the prefix into text (`%s` with `v->p`/`v->up`, `vm_rolef` and
`dfa_fragf` fragments, `derived_name`, the encoding seam's decls). Counting
the prefix back out at each decision would be a second spelling of the
emission, which a new site silently escapes. The file's own comments condemn
that shape: "a needle is a second spelling of the emission". A text scan for
`<p>_` tokens is not exact either: prefixes like `size` or `uint8` collide
with `size_t`/`uint8_t`. The other general form is a second compile at
`-p rx`. It doubles every non-`rx` compile, and some corpus patterns take 23
seconds to compile.

**Why these bytes.** Two bytes, so a `-p rx` artifact is unchanged. The lead
byte `\x01` never reaches emitted text by any other route: every pattern- or
caller-derived byte outside printable ASCII is escaped at its site
(`emit_comment_safe_byte`, `emit_c_string_literal`, `pcrec_sb_cstr`,
`vm_var_word_bytes`, the class renderers). The second byte is a letter, so
`pcrec_sb_upper` maps the lower spelling onto the upper one with no special
case.

**The two sites that had to change.**

- The header guard was `isalnum ? toupper : '_'` per byte. That mapped the
  lead byte to `_`, so the render could not see it. It is now `upper`, the
  one derivation. The two agree on every validated prefix, because a C
  identifier holds only alnum and `_`.
- `rx_info.name`'s default went through `emit_c_string_literal`, which would
  octal-escape the placeholder. It is now written raw. A validated prefix
  needs no escaping.

These are the seam the mechanism creates: prefix-derived text must not pass
through an escaper, or through a case transform other than `pcrec_sb_upper`.
Both rules are stated in `internal.h` and `src/gen/CLAUDE.md`. A raw stray
`\x01` at render time is an internal error, never a silent corruption.

**Validation of the refactor itself.** A 300-pattern sample (seed 1,
`--features all`, `-p rx`) compared the new and branch-point compilers on
the `.c`, the `.h`, stderr and the exit code: **300 same, 0 different**
(measured before the abi bump). That is the byte-identity claim at `-p rx`.

**Which stamps may differ between two prefixes: none by value.** Every
stamp's NAME carries the prefix, and `rx_info.name`'s default is the prefix.
No stamp's VALUE counts prefixed text. `<PREFIX>_VM_PROGRAM_BYTES`, the one
stamp that counts emitted bytes, now reports the canonical length: the
program as it reads at `-p rx`. That is honest, because it is the exact
quantity the knee compared. The spec says so in match_api.md §6.3, tuning.md
§2.21 and limits.md §8.

**The caps.** They now bound the canonical length. So an artifact at a long
prefix can exceed a cap's number in real bytes, by up to
(len - 2) x occurrences, which is under a third at the 60-byte maximum
(pfx0 measured 17-30%). This is deliberate: a name should not decide whether
a pattern compiles, and the caps are failsafes against pathological
emission, which a prefix cannot cause. Stated in limits.md §8 "Size limits
and the prefix" and D143.

**Same class, not fixed (named, D77).** `header_name` (the `#include "…"`
line in the `.c`) and a caller-set `rx_info.name` are caller-chosen text.
Each still enters the measured length once. The measure is a few tens of
bytes, and no case is measured. The mechanism takes each with one more tag
byte if a case appears. The invariance check uses one output basename for
every prefix, so it isolates the prefix.

## K79 — the invariance check

`tests/codegen/run_prefix_invariance.sh`, in `make test-codegen` (~20 s),
mech arm `prefixinv`.

**What counts as selection: everything.**

- **PART 1.** Each pattern is compiled at `-p rx` and at `kpz` (3 chars),
  `kpz9…` (23) and `kpz9…` (60). The long-prefix artifact is back-mapped to
  `rx`/`RX` and must equal the `-p rx` one byte for byte: the `.c`, the
  `.h`, or on a refusal the diagnostic. No stamp is exempt. The back-map is
  exact because `kpz` occurs in no fixed emitted text, and the population
  drops any pattern that spells it.
- **PART 2.** The same comparison at `-p q` (one character, which cannot be
  back-mapped), on the value-stamp list with the prefix stripped at its
  known position.
- **PART 3, the reach.**
  - A population floor: at least 100 route x pattern pairs and 250 compared
    compiles.
  - Six witnesses that each FLIPPED entry shape on the pre-fix compiler,
    asserted to take one shape at every prefix length (1..60).
- **Population.** The six witnesses plus every 40th distinct corpus
  pattern, each on the default route and under `--engine=vm`: 176 pairs,
  528 long-prefix compiles.

**Results.**

- **Fixed tree: 9 of 9 pass.** 480 identical artifacts and 48 identical
  refusals in PART 1. 160 identical value-stamp lists in PART 2.
- **Failing direction.** The same script against the branch-point compiler
  (`PCREC=/tmp/…/base/build/pcrec`): **0 passed, 9 failed.** PART 1: 360 of
  528 differ. PART 2: 120 differ. All six witnesses flip.
- **Sabotage S437.** It puts `defo.prefix = user_prefix;` back, which is the
  pre-fix behaviour. Its detector is this script, and the branch-point run
  above is its measured shape. A solo `make mech` run of the row is OWED to
  the manager's battery: mech is not a light target.

## K80 — the fix and why this shape

**Why one valued guard.** An abi-keyed guard NAME (`PCREC_RX_ABI_54_H`)
would let both blocks through. The second `struct rx_ctx` is then a
redefinition error that names a type, not the cause. For a block whose
members happened to agree there would be no error at all. One guard with a
value keeps "the first block wins" for the same-abi case, and names the
cause for the mixed one.

**The `+ 0`.** Pre-54 artifacts define the guard EMPTY. `( + 0)` evaluates
to 0, so old-then-new is refused too. New-then-old is the one order no
emission can reach, because the old block's `#ifndef` was written before
this rule existed. The spec says so (match_api.md §2).

**Checked:**

- clean under `-Wall -Wextra -Wundef -Werror` (gcc-16)
- the digit comes from `PCREC_ARTIFACT_ABI`, not a second literal
- S04's anchor (`"#ifndef PCREC_RX_ABI_H\n"`) is unchanged and still resolves

**Check (run_codegen_tests.sh, after the D44/A-2 two-prefix TU).** A second
abi is SIMULATED from a real artifact by rewriting the three digits the rule
reads. No other emitter exists in this tree.

- **K80-a.** The real `dprx.h`, then an abi-53 `dpqq.h`, in one TU. It must
  fail, and fail on the `#error` text.
- **K80-b.** A pre-54 header (empty guard, no prelude) first, then the real
  one. It must fail on the `#error` text.
- **K80-c.** Each rewritten header compiles alone, so a red is the mix and
  not the rewrite.
- **Same-abi case.** The existing D44/A-2 two-prefix TU and the OS-0b
  duplicated-block compile stay the clean case. The OS-0b greps now match
  `^#define PCREC_RX_ABI_H [0-9]+$`.

Sabotage **S438** emits the test as `#if 0 && …`. The fence is then off,
and K80-a and K80-b must go red.

## The abi 53 -> 54 readers, found by grep

A grep for `53` near `abi`/`ABI` across the tree (excluding the journal,
the archived plan and lane reports) finds:

| reader | action |
|---|---|
| `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI` | 53 -> 54 |
| `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT` + its failure narrative | 54, `53->54` transition appended |
| `docs/spec/match_api.md` §6 (the change log, "is `53`") | new "is `54`" entry; the 53 entry now reads "was" |
| `tests/codegen/run_recursion_identity.sh` (B) `FILEPIN` | re-pinned to `79ebcfd7` (last `src/` commit of this lane; the manager re-pins if the merge rewrites it) |

All other hits are historical ("since abi 53", "abi 52->53") and stay.

**Readers that never cite the number (D94 addendum).**

- Every artifact gains the prelude, the guard value and the digit, about
  200 bytes in the ABI block. That block is in the `.h` under `-o FILE.c`,
  or in the `.c` under `-o -`.
- The size term's code-bytes measure moves by that constant:
  `run_size_term.sh`'s cap-rescue witness calibration, and
  `run_cpset_structure.sh`'s `manifests/m5_stage1_stamps.tsv` EMITTED_BYTES
  rows. The results are in "Validation".
- `docs/dev/artifact_size_log.tsv` moves too. By its own rule it is
  re-recorded only at a gate re-archive.

## Validation

OWED-NUMBERS-BELOW (filled from the light chain's logs).

## Files

- src/core/internal.h: the placeholder, the render API, `Ctx.user_prefix`
- src/core/sb.c: `pcrec_sb_render_prefix`, `pcrec_render_prefix_msg`
- src/core/compile.c: the placeholder, validation of the real prefix, the
  render at `facts_force`, the hook view, the diagnostic render
- src/gen/emit_dfa.c: the guard prelude and value, abi 54, the header guard
  as `upper`, the raw `.name` default
- tests/codegen/run_prefix_invariance.sh (new)
- tests/codegen/run_codegen_tests.sh: K80 cells, `ABI_EXPECT`, OS-0b greps
- tests/codegen/run_recursion_identity.sh: (B) re-pin
- tests/mech/run_sabotage_matrix.sh: arm `prefixinv`
- tests/mech/sabotages/S437_*.sh and S438_*.sh
- Makefile: `test-codegen` group
- docs/spec/limits.md §8, match_api.md §2/§6/§6.3, tuning.md §2.21
- docs/dev/known_issues.md (K79 and K80 FIXED), docs/dev/decisions.md (D143)
- CLAUDE.md: src/core, src/gen, tests/codegen, tests/mech
