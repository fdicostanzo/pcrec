# tests/codegen — structural assertions on generated code

Asserts that behavior-preserving optimizations are actually PRESENT in the
emitted C. These are not correctness tests (the .rxt corpus owns correctness);
they exist because checkpoint review R2 (finding R2-PR3) showed that three M2
optimizations — self-loop skip states, the anchored fast path, and DFA
minimization — could each be COMPLETELY disabled with zero signal from
`make test` or `make bench`. Behavior-preserving work needs structural tests
or it has no regression net at all.

## Files

- **run_trie_identity.sh** — DIFFERENTIAL codegen check for the M2.8
  alternation trie (R3.3). Builds a reference compiler from the same sources
  with `-DPCREC_NO_TRIE` (which forces `elig[j] = false` in nfa.c's A_ALT path)
  and diffs the emitted C over 500 generated alternation patterns. The trie is
  required to be OUTPUT-PRESERVING — subset construction plus minimization must
  erase it — so any difference is a rule-1/rule-2 soundness bug. No subjects, no
  gcc, ~4 s. Env: PCREC, CC, TRIE_N, TRIE_SEED, KEEP=1, SANFLAGS (SAN-1:
  extra flags appended to the from-source `$REF` reference build only —
  `$PCREC` is already overridable and carries the PRIMARY compiler-axis
  sanitizer coverage for free; see docs/testing.md "Sanitizer + lint
  battery" for a real finding (F1) this SANFLAGS wiring surfaced).
- **run_vm_identity.sh** — [M4.5b] THE ZERO-REGRESSION GATE (engine_m4.md
  §5.4, §13 P-7: "this one should be a GATE, not a prediction"). Its claim is
  that a capture-free pattern does not touch any new code — same AST, same
  NFA, same DFA, same emitter, same bytes — now that a second emitter and a
  capture AST node exist.

  It does NOT pin a historical commit, which is what §5.4's literal wording
  ("byte-identical to the pre-M4 emitter's output") would require: a check
  written that way fails the first time anyone legitimately changes the DFA
  emitter, which is a built-in expiry date and worse than no check because it
  teaches people to edit the pin. The permanent formulation compares the
  DEFAULT compile against `--no-captures` over every `pattern` line in every
  .rxt under tests/ (so the population grows with the corpus, not with the
  script), plus: `--no-captures` yields a DFA artifact for EVERY pattern, and
  `RX_NCAPS > 1 ⇒ VM` now holds NON-VACUOUSLY — that check had no population
  at all before [M4.5b] and this file's own [M4.4] note said so.

  ONE normalization, and it is ARITHMETIC rather than a filter: `rx_info.flags`
  legitimately differs by exactly the `PCREC_NO_CAPTURES` bit, so that bit is
  subtracted from the `--no-captures` side and every other byte must still
  match. Deliberately not a `grep -v` of "the stamp lines" — this project's
  recorded check-design failure is controls sharing a source with what they
  control, and its close cousin is a comparison loosened until it stops
  discriminating. Both compiles also use the SAME BASENAME in different
  directories, or the `#include "<name>.h"` line alone would differ (the exact
  trap run_trie_identity.sh documents at its own gen_a/gen_b — the first
  version of this script reported all 260 capture-free patterns divergent for
  precisely that reason).

  Also asserts the §5.6 override's refusals: `--engine=dfa` on a
  captures-default group-bearing pattern refuses AND names `--no-captures`,
  that named escape actually works, `--engine=vm` emits NO prefilter (D44/R21
  E-6 — without which tests/vm's differential is near-tautological), and the
  default hybrid DOES emit one (§4.7's cliff guard). 8 checks; sabotage S40.

- **run_codegen_tests.sh** — greps ONE ENGINE'S BODY (extracted by entry name;
  see below) for each optimization's
  signature (skip tables + skip loop, `start_max = 0` for fully-anchored
  patterns and its ABSENCE for partially-anchored ones, memchr prefilter,
  a table-size ceiling that only holds if minimization ran, engine selection
  for `$` vs `^`, and the M2.12 EOL-path checks: skips present and bounded at
  n-1, reverse skip entry guard, memchr bounded at n-1, and an ORDER check
  that accept/EOL evaluation follows the skips), plus the OS-0b multi-engine
  block. **Since [STD1] phase A (D37, 2026-08-13)** also a WHOLE-FILE check
  (the stamp sits above any engine function, so `body()` does not apply):
  `--features std1` stamps `/* Feature set: std1 (modules: classes,modifiers) */`
  plus the `PCREC_FEATURE_SET`/`PCREC_FEATURE_MODULES` macros in the .c, the
  paired `.h` carries the comment but never the macros, and a bare
  invocation still stamps something rather than nothing. **[STD1b]
  (2026-08-13) re-baseline:** phase A's bare invocation stamped `"none"`
  (the pre-flip default constant); the bare default is `std1` now, so the
  bare-invocation check flipped to expect
  `/* Feature set: std1 (modules: classes,modifiers) */`, and a second
  check was added for `--features none` stamping `"none"` explicitly (the
  escape hatch, unaffected by the flip) — 33 checks before, 34 at [STD1b].
  **[M4.4] (D44.2/D44.5, 2026-08-14) re-baseline: 37 checks.** The
  `<prefix>_span` out-struct retires (D44.2) for a caps-array
  `<prefix>_search` parameter, so the OS-1 entry-point-signature grep and
  the multi-engine fixture's hand-written second-engine declaration both
  update to the new signature; the multi-engine block's "exactly once per
  file" assertion now targets the fixed ABI-types block's
  `#define PCREC_RX_ABI_H` line instead of the retired span typedef, and
  its duplicate-emission assertion INVERTS (see below); a new check builds
  two DIFFERENTLY-PREFIXED generated headers together in one TU (D44/A-2's
  own positive control); and two new structural checks assert
  `rx_info.ncaps == RX_NCAPS` and `RX_NCAPS > 1 => VM` (D42.2/D44.5, §11
  item 9 of docs/design/match_api_m4.md), both live from this commit and
  trivially green pre-[M4.5] since `RX_NCAPS` is 1 on every artifact this
  DFA-only emitter produces. Part
  of `make test`;
  env: PCREC, CC, GENCFLAGS, KEEP=1, LINTGEN=1
  (SAN-1: rides this GENCFLAGS compile with `gcc -fanalyzer`, opt-in).

## [M4.5b] re-baseline: 38 checks, and three narrowings worth reading

Three checks in `run_codegen_tests.sh` had to move when the VM engine landed,
and in each case the fix is a NARROWING that adds coverage rather than a
loosening that removes it. Read them together, because they are the same
lesson three times: a check written when only one shape existed can encode
that shape by accident.

1. **The minimization check's group is now `(?:...)`.** It was
   `(get|post|put|delete|patch)`, and the group was incidental to what the
   check measures (a DFA table's size) — until D42.1 made captures the
   default, at which point the capturing spelling routes to a VM artifact
   where the table lives in `rx_prefilter`, not in the `rx_search` body
   `body()` extracts. A NEW companion check then asserts the same alternation
   in its CAPTURING spelling gets a minimized table inside the prefilter,
   which is coverage that did not exist before: the hybrid runs the same
   forward+reverse pair through the same passes, so a minimization bug scoped
   to that path was previously invisible.

2. **`body()`'s anchor accepts an optional `static`.** The VM's prefilter is
   the same emitter's output under a private name and a different storage
   class, and it must be per-engine extractable for exactly the reason every
   other body is.

3. **TS-1 now distinguishes a static FUNCTION from a static OBJECT.** D19's
   property is "no mutable file/function-scope STATE", and a function has no
   storage to race on — but while every emitted `static` was a table, "static
   and not const" and "mutable state" were the same set and the check could
   not tell them apart. A VM artifact emits five static functions and keeps its
   whole mutable working set in a LOCAL of the search entry, which is what D19
   asks for. The discriminator is C's declarator syntax (a `(` with no `=`,
   `;` or `[` before it), not a list of known function names, so
   `static unsigned char rx_tbl[256] = {` — S06's sabotage, a table with its
   `const` dropped — still has no `(` at all and is still caught, and so is
   anything of the shape `static int rx_counter = f(0);`.

   S02 and S06 were RE-RUN through `tests/mech` after these edits, because a
   narrowed check whose sabotage was validated against the wide version has
   not been validated at all.

## Engine-scoped greps, and why a whole-file grep stopped being enough (OS-0b)

Every symbol these checks look for is a function-local static or a statement
inside the engine function — that is the measured finding OS-0b rests on, and
it is what lets several engines share one file under D18/D20. It is also what
makes a whole-file grep wrong as soon as there IS more than one engine:
`rx_fs[0-9]+\[256\]` would be satisfied by ANY engine present, so a check
reading "this pattern emits a skip table" degrades to "some engine in here
does" while still passing. All 19 grep sites across 11 generated files now run
against a body extracted by entry name (`body()`).

An extractor is itself a thing that can silently break, so it is not trusted on
inspection. The multi-engine block builds a two-engine file by hand — the
fixed ABI-types block once for the file, a distinct entry name per engine,
every other identifier
untouched, i.e. exactly the transformation an engine finder (OS-0) will apply —
and requires a scoped grep to find the skip table in the engine that HAS one
('.*=.*') and NOT in the engine that does not ('^a|b'). A `body()` returning
the whole file fails the second; one returning nothing fails the first. The
block also compiles the fixture under GENCFLAGS.

**[M4.4] (D44.2/D44/A-2) INVERTS the duplicate-emission assertion, on
purpose.** Before the API break, duplicating `emit_span_typedef`'s call
broke the build (gcc: `error: conflicting types for 'rx_span'`, since each
occurrence declared a fresh anonymous struct; confirmed under -std=gnu11
and -std=c99) — the emit-once rule was load-bearing because nothing guarded
re-inclusion. The fixed ABI types (`rx_ctx`, `rx_matchfn`, `rx_group_entry`,
`rx_info`, ...) are wrapped in a PREFIX-INDEPENDENT `#ifndef PCREC_RX_ABI_H`
guard instead (the R21 panel MEASURED that a per-prefix guard fails the
exact case it exists for: two differently-prefixed generated headers in one
TU, each deriving a DIFFERENT guard name, both bodies re-defining the fixed
types), so the property worth asserting flipped: duplicating the WHOLE
guarded block (guard included) must NOT break the build anymore, and the
codegen suite's own positive control for the guard's necessity is instead
the two-differently-prefixed-headers check below.

Validated sabotages for run_codegen_tests.sh (37 checks pass clean, as of
[M4.4] — read the current count from a run rather than this line, which has
already drifted at least once). Each was
applied to a FRESH tree, with the edit asserted to have landed before the tree
was built:

| sabotage (exact edit) | result |
|---|---|
| `int nout = 0;` -> `int nout = 0; return 0;` in `pick_skip_states` (skip states off) | 7 fail — the 6 pre-OS-0b skip checks, unchanged by the scoping, plus the multi-engine control reporting its fixture can no longer discriminate |
| in `body()`, `$0 ~ "^int " fn "\\(" { inside = 1 }` -> `{ inside = 1 }` (extractor returns the whole file) | 3 fail, incl. "scoped grep attributed engine A's skip table to engine B" |
| replace only the attribution-step extraction: `&& body "$WORKDIR/multi.c" rx_search_b ...` -> `&& cp "$WORKDIR/multi.c" ...` (isolates scoping from fixture construction) | 1 fail — the attribution check alone |
| [M4.4] `tests/mech/sabotages/S04_duplicate_typedef.sh`, RETARGETED: neuter the `PCREC_RX_ABI_H` guard (`#ifndef PCREC_RX_ABI_H` -> an unconditional `#if 1`) | 2 fail — the D44/A-2 cross-prefix compile check and the OS-0b duplicated-block compile check; a single-prefix artifact still compiles, so nothing else regresses |
| in the fixture's rename, `s/\brx_search\b/rx_search_b/g` -> `.../rx_search/g` (engines keep one name) | 1 fail — compile, `error: redefinition of 'rx_search'` |

## The OS-1 checks assert an ABSENCE, which the corpus cannot

Case folding (D23) is behaviour-preserving in the direction that matters here:
a corpus can prove `-i abc` matches `ABC`, but nothing in it can prove the
match cost nothing. The OS-1 checks assert the emitted shape instead — that
`-i 'aBc'` is byte-identical to `'[aA][bB][cC]'`, that a letter-free pattern is
untouched by `-i`, that no `tolower`/`0x20`-style conversion appears anywhere,
and that the entry-point signature is unchanged (a compiled-away option must
not surface at run time, D18). Implement caselessness as a runtime check and
every one of them fails while the corpus stays green.

These comparisons use `-o -` and, since [M4.4], compare the `rx_search`
ENGINE BODY (`body()`-extracted) rather than the whole file. That is not
tidiness: writing two files emits two different `#include "<name>.h"`
lines, so a whole-file comparison would differ for a reason unrelated to
folding — the same trap `run_trie_identity.sh` documents at its
`gen_a`/`gen_b`, and the reason the first version of these checks used
`gen` and failed. **[M4.4] added a second, structurally similar reason to
scope down to the engine body specifically**: `rx_info` (D43.1) embeds the
source pattern text and the compiled `flags` word unconditionally, and
both legitimately differ between two different pattern spellings (or
between `-i` and no `-i`, even on a pattern `-i` has no folding effect on —
the flag is still set as compiled) — the same "the stamp differs by
design" shape D37's [STD1] case9/case10 already established in
`tests/cli/`. D18's zero-cost claim was always about the AUTOMATON
specifically, which is exactly what `body()` extracts; comparing the whole
file would now fail these checks for a reason that has nothing to do with
whether folding leaked into the runtime.

`run_trie_identity.sh` also sweeps its 500-pattern corpus TWICE, once
case-sensitive and once with `-i`. Folding rewrites the bitmaps the trie keys
on — `Cat|CAT|cat` goes from three unrelated branches to three identical ones —
so the folded sweep drives rule 1's accept split and rule 2's disjoint-run
logic down paths the unfolded corpus never reaches.

| sabotage (exact edit) | result |
|---|---|
| move the `cls_casefold` call in `p_class` from before the negation to after it | 1 codegen check (`-i '[^a]'` is not `'[^aA]'`) + 6 caseless.rxt cases |
| delete the `cls_casefold` call in `char_node` (classes still fold, literals do not) | 1 codegen check + 14 caseless.rxt cases |
| `if (cls_has(b, c) \|\| cls_has(b, c + 32))` -> `if (cls_has(b, c + 32))` (fold one direction only) | 1 codegen check + 8 caseless.rxt cases |
| in run.sh, drop the `-i` mapping so `flags i` becomes a no-op | 21 of 56 caseless.rxt cases |

## TS-1 guards a property NOTHING else in the repo can see

D19's rule is "usable FROM threads, never threaded". For generated code that
reduces to two mechanical facts — every emitted `static` is `const` (so it is
.rodata with a constant initialiser: no lazy init, nothing to race on) and the
output references no non-reentrant or allocating libc. Both hold today by
construction, and both are invisible to correctness testing.

The sabotage numbers make the point better than the prose. Making every emitted
table a NON-CONST static fails 8 TS-1 checks and **zero** corpus cases: the code
compiles, matches identically, and passes the entire suite while being
thread-hostile. That is the memoisation-cache / hoisted-scratch-buffer /
diagnostics-counter failure mode, and under D18 also a selector that caches its
choice in a global.

The sweep covers 18 emitted files across 9 emission shapes (both engines, EOL
and non-EOL, both prefilter kinds, skip states, the never-matches path,
case-folded, and `--emit-main`), plus the paired `.h`. The file count is itself
asserted, so a sweep that quietly stops generating stops passing.

| sabotage (exact edit) | result |
|---|---|
| `static const unsigned char %s_%s[%d]` -> `static unsigned char %s_%s[%d]` in `emit_u8_table` | 8 TS-1 checks, **0 corpus cases** |
| `size_t pos = startpos;` -> `size_t pos = startpos; (void)errno;` in `emit_unanchored` | 6 TS-1 checks (+ the OS-0b compile check, incidentally, because `errno` also needs a header it does not get) |

Line 1 of each file is stripped before scanning — it echoes the user's pattern
verbatim, so a pattern named `malloc` would otherwise fail its own denylist.
The scan does not strip C comments, so an emitted comment that merely mentions
a denylisted symbol will trip it; that is deliberate, and the fix is to reword
the comment rather than to weaken the list.

The M2.12 additions are the sharpest illustration of why this directory
exists: reverting the EOL path to its M2.7 state (no prefilter, no skips —
~76x slower on `$` patterns) fails 6 checks here while the .rxt corpus still
passes 53/53, because the change is behavior-preserving by construction.

## Two kinds of check live here

`run_codegen_tests.sh` asserts a SIGNATURE is present in the output — cheap,
but it only ever proves the optimization ran, never that it was right.
`run_trie_identity.sh` asserts EQUIVALENCE against a reference build with the
optimization off, which proves soundness across hundreds of patterns at once.
Prefer the second shape whenever an optimization is supposed to be
output-preserving; the M2 journal wrongly concluded M2.8 was not structurally
testable, and the equivalence check turned out to be both possible and far
stronger than the corpus (a broken disjointness guard shows up on a handful of
.rxt cases and on 64 of 500 patterns here — the measured figures and the exact
edits behind them are in the sabotage table below). The ".rxt cases" half of
that figure was measured at 2 when this was written and is 6 today
(alternation_trie.rxt grew) — which is MECH-1's founding example of a
hand-copied count going stale silently. Current figures for EVERY sabotage in
this file come from `bash tests/mech/run_sabotage_matrix.sh` (S01..S14 cover
this directory); the tables below keep the exact edits and the lessons, and
the generator owns the numbers.

An equivalence check has its own trap, and the fix for it is not optional: if
BOTH builds had the optimization off, every comparison would agree and the
script would certify a deleted optimization. `run_trie_identity.sh` therefore
carries POSITIVE CONTROLS — patterns whose NFA fits the cap only when factored,
so the two builds fail at different stages — and they are sabotage-validated.

**There are three of them, at 4, 8 and 256 branches, and the small ones are the
important ones.** The first version had only the 256-branch control while every
generated pattern had 3..8 branches, and a critic broke it in one clause:
`elig[j] = TRIE_ENABLED && nbr >= 100 && trie_key(...)` left all three checks
green, `make bench`'s KEYWORD-SCALE green, and the whole `make test` suite green
with the trie deleted for every hand-written pattern. A control that only proves
the optimization fires OUTSIDE the corpus's own range proves nothing about the
corpus. When adding an equivalence check, put a control inside the range of the
inputs it actually compares.

## Conventions

Every check must be validated against a deliberate sabotage: disable the
optimization in a scratchpad build and confirm the check FAILS. A structural
test that passes under sabotage is worse than no test — it certifies nothing
while looking like coverage. Sabotage the SPECIFIC branch under test, not the
feature containing it. When adding an optimization to src/gen or src/opt, add
its check here in the same change.

Validated sabotages for run_trie_identity.sh. **Record the exact edit, not just
the count** — the first version of this table carried a number produced by a
contaminated tree (two sabotages stacked, because a `git checkout` revert
silently failed inside a non-git tarball copy) and another that was never
measured at all:

| sabotage (exact edit) | .rxt | @200 | @500 |
|---|---|---|---|
| `return n;` as the first statement of `disjoint_run_len` | 2 | 21 | 64 |
| in rule 1, hoist every accept to the front instead of partitioning the list around each (keep removing them from the list) | 16 | 38 | 94 |
| `TRIE_ENABLED = 0` in the shipped build | 0 | 0 | 0 — only the CONTROLS fire |
| `elig[j] = TRIE_ENABLED && nbr >= 100 && trie_key(...)` | 0 | 0 | 0 — only the 4- and 8-branch controls fire |

Do NOT use the naive rule-1 sabotage (skip the accept split, change nothing
else): it leaves items with `len == depth` in the list for rule 2, which then
reads `seq + depth*32` past the allocated key — a 32-byte arena over-read, so
the count is unstable between builds (171 and 176 observed for the same edit).
The hoist form above is memory-safe by construction.

Maintenance: update this file when checks are added/removed.
