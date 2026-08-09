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
  gcc, ~4 s. Env: PCREC, CC, TRIE_N, TRIE_SEED, KEEP=1.
- **run_codegen_tests.sh** — greps ONE ENGINE'S BODY (extracted by entry name;
  see below) for each optimization's
  signature (skip tables + skip loop, `start_max = 0` for fully-anchored
  patterns and its ABSENCE for partially-anchored ones, memchr prefilter,
  a table-size ceiling that only holds if minimization ran, engine selection
  for `$` vs `^`, and the M2.12 EOL-path checks: skips present and bounded at
  n-1, reverse skip entry guard, memchr bounded at n-1, and an ORDER check
  that accept/EOL evaluation follows the skips), plus the OS-0b multi-engine
  block. Part of `make test`; env: PCREC, CC, GENCFLAGS, KEEP=1.

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
inspection. The multi-engine block builds a two-engine file by hand — one
shared span typedef, a distinct entry name per engine, every other identifier
untouched, i.e. exactly the transformation an engine finder (OS-0) will apply —
and requires a scoped grep to find the skip table in the engine that HAS one
('.*=.*') and NOT in the engine that does not ('^a|b'). A `body()` returning
the whole file fails the second; one returning nothing fails the first. The
block also compiles the fixture under GENCFLAGS, and asserts that DUPLICATING
the typedef breaks the build — the emit-once rule is verified, not folklore
(gcc: `error: conflicting types for 'rx_span'`, since each occurrence declares
a fresh anonymous struct; confirmed under -std=gnu11 and -std=c99).

Validated sabotages for run_codegen_tests.sh (22 checks pass clean). Each was
applied to a FRESH tree, with the edit asserted to have landed before the tree
was built:

| sabotage (exact edit) | result |
|---|---|
| `int nout = 0;` -> `int nout = 0; return 0;` in `pick_skip_states` (skip states off) | 7 fail — the 6 pre-OS-0b skip checks, unchanged by the scoping, plus the multi-engine control reporting its fixture can no longer discriminate |
| in `body()`, `$0 ~ "^int " fn "\\(" { inside = 1 }` -> `{ inside = 1 }` (extractor returns the whole file) | 3 fail, incl. "scoped grep attributed engine A's skip table to engine B" |
| replace only the attribution-step extraction: `&& body "$WORKDIR/multi.c" rx_search_b ...` -> `&& cp "$WORKDIR/multi.c" ...` (isolates scoping from fixture construction) | 1 fail — the attribution check alone |
| duplicate the call: `emit_span_typedef(c, p);` -> `emit_span_typedef(c, p); emit_span_typedef(c, p);` | 2 fail — typedef-count and compile |
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

These comparisons use `-o -` and strip line 1. That is not tidiness: writing
two files emits two different `#include "<name>.h"` lines, so every comparison
would differ for a reason unrelated to folding — the same trap
`run_trie_identity.sh` documents at its `gen_a`/`gen_b`. The first version of
these checks used `gen` and failed for exactly that reason.

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
stronger than the corpus (a broken disjointness guard shows up on 2 .rxt cases
and on 64 of 500 patterns here — the measured figures and the exact edits behind
them are in the sabotage table below).

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
