# [REVW.2] EMIT_DFA.C THIRD-CATEGORY CENSUS — the stage precondition

Lane `w2census` (sonnet, 2026-09-18), against `main` at `f6474777`.
Charter: `docs/dev/reviews/lens_reports/emitvm_second_pass.md` (EP2) §4 —
the three sizing categories of fixed `char <ident>[...]` scratch buffers —
plus the `[REVW.2]` row's stated precondition, "emit_dfa.c third-category
census FIRST", before wave 2's stage-3 step runs. `docs/dev/w1stage0.md`
is this doc's format precedent (method, population, per-site table, floor,
what the instrument cannot see).

TASK 1 deliverable. TASK 2 (the listing-reach measurement) is reported
separately in `docs/dev/lanes/w2census_report.md`. Nothing under
`src/`/`cli/`/`lib/` touched; this stage is nets + measurement only.

---

## 1. The instrument

`tools/review/fragment_census.py` (new; python3 stdlib only, per
`tools/review/CLAUDE.md`'s convention — no third-party deps, no network,
no build). Unlike this directory's other five scripts it does not walk
the whole PRIMARY tier; it takes explicit file paths, per the brief
("over a named file").

Method, in order:

1. **Mask** the file with `reviewlib.mask_text()` — comments blanked,
   string-literal INTERIORS blanked, preprocessor lines blanked — so a
   `char foo[123]`-shaped byte sequence printed AS EMITTED-CODE TEXT
   inside an `pcrec_sb_printf`/`snprintf` format string (both files do this
   constantly: `src/gen/emit_dfa.c:5866`'s `"static const unsigned char
   %s_class_bitmap%d[32] = {"` is exactly this shape) is never mistaken
   for a real declaration in the reviewed file's own source. This is the
   same lexical front end `function_census.py` and `clone_candidates.py`
   use, hand-validated by that script's own module docstring against
   these two files specifically.
2. Find every word-bounded `char` token and consume forward to the
   matching top-level `;` (bracket-depth aware), which may span more
   than one source line — this is a declaration **statement**.
3. Split the statement's declarator list on top-level commas; a part
   matching `IDENT [ EXPR ] (= INIT)?` is a `char`-array **declarator**.
   A part that doesn't match this shape (a pointer declarator such as
   `char *q = pcrec_arena_alloc(...)`) contributes nothing — a statement with
   zero array declarators is not counted at all.
4. Classify **each declarator's own** size expression independently:
   (a) bare integer literal, (b) bare `PCREC_MAX_EMIT_NAME_LEN`
   (the K38 family, EP2's exact category), (c) anything else — a
   catch-all, not a fixed shape list, per the repaired criterion's own
   "ANY size expression" wording.
5. Attribute each line to its enclosing function via
   `reviewlib.iter_top_level_headers()`'s brace-depth walk (the same
   function-boundary walk `function_census.py`/`clone_candidates.py`
   build on) so a struct-field declaration — which has no enclosing
   function — reads as such rather than being silently misattributed to
   whatever function happens to precede it in the file.

A statement can mix categories across its own declarators; the script
reports this explicitly (`[MIXED STATEMENT]`) rather than forcing one
label onto the whole line — see §2 below, where exactly this happens and
is the entire source of the one number this census does not reproduce.

Validated directly against file content (not just against EP2's own
numbers): every multi-declarator statement the script found was read by
hand against the source (`sed -n`) and confirmed a real, syntactically
correct declaration — including the two `pf_emit_ofs_bounded` scoped
`{ char sub[64]; ... }` blocks at `emit_dfa.c:4867` and `:4874`, which
are two independent statements in two different `if`/`else if` arms, not
one statement double-counted.

Usage: `python3 tools/review/fragment_census.py FILE [FILE...] [--out
PATH]`. `tools/review/CLAUDE.md` and `tools/CLAUDE.md` carry the file's
row.

---

## 2. emit_vm.c — reproducing EP2, and the one place it doesn't

**Raw census, `src/gen/emit_vm.c` at `f6474777`:**

| | statements | declarators |
|---|---:|---:|
| (a) bare integer literal | — | 46 |
| (b) bare `PCREC_MAX_EMIT_NAME_LEN` | — | 16 |
| (c) anything else | — | 5 |
| **total (raw, per-declarator)** | **58** | **67** |

EP2 §4 reports **58 statements / 66 declarators** (a: 40/45, b: 13/16,
c: 5/5). Statement count reproduces EXACTLY. Declarator count is **one
higher** than EP2's — and this is **the script disagreeing, not the tree
moving**: the extra declarator is real, present, and traced to one exact
site.

**The site.** `src/gen/emit_vm.c:4894`, function `vm_revdet_rep`:

```c
char rv[PCREC_MAX_EMIT_NAME_LEN], cur[PCREC_MAX_EMIT_NAME_LEN], flr[32];
```

— a single statement with three declarators: `rv` and `cur` are category
(b) (the K38 family, exactly as the function's own adjacent comment says:
*"rv/cur widened from 80/96 to the shared emitted-name size"*), and `flr`
is category (a) — the same comment says so explicitly: *"flr carries no
prefix and is unaffected."* This is a genuinely MIXED statement.

Assigning a **pure** statement to its one category, and reporting this
one mixed statement on its own (rather than forcing it into a bucket),
this script's per-statement breakdown is:

| category | statements | declarators |
|---|---:|---:|
| (a) pure | 40 | 45 |
| (b) pure | 12 | 14 |
| (c) pure | 5 | 5 |
| MIXED (`vm_revdet_rep`'s `rv,cur,flr` line) | 1 | 3 (2×b, 1×a) |
| **total** | **58** | **67** |

EP2's 40/45 for category (a) reproduces EXACTLY against this script's
**pure**-(a) row. EP2's 13/16 for category (b) reproduces EXACTLY against
this script's pure-(b) row **plus** the mixed statement counted whole
(12+1=13 statements, 14+2=16 declarators) — i.e. EP2 folded the mixed
`rv,cur,flr` statement into category (b) (correctly, by its dominant
K38-family content) but then only carried `rv` and `cur` into the
declarator tally, and **`flr[32]` never lands anywhere in EP2's own
count**: 45(a) + 16(b) + 5(c) = 66, and `flr` is the missing 67th.

`flr[32]` is a real, live, literal-sized scratch buffer — the same shape
as every other category-(a) row — that happens to share its declaration
line with two K38-family buffers. EP2's own §4 prose already flagged
this exact site as one of the statements declaring "two or three each"
in its category-(a) reconciliation paragraph; what it did not flag is
that this particular one of those statements is not uniformly
category (a), and the non-uniformity is exactly where one declarator
fell out of the tally. **Verdict: the script disagrees with EP2 by
one declarator, and the disagreement is fully explained — not a
population that moved between EP2's measurement and this one.**

---

## 3. emit_dfa.c — the population EP2 never measured

**Raw census, `src/gen/emit_dfa.c` at `f6474777`:**

| | statements | declarators |
|---|---:|---:|
| (a) bare integer literal | 8 | 9 |
| (b) bare `PCREC_MAX_EMIT_NAME_LEN` | 10 | 10 |
| (c) anything else | 5 | 6 |
| **total** | **23** | **25** |

No mixed statements in this file. `emit_scan_loop` (`:5995`) is the one
multi-declarator line, and both its declarators (`lv`, `le`) share the
identical category-(c) expression, so it stays pure.

### Category (c), the six sites EP2 never counted

| line | function | declaration | note |
|---|---|---|---|
| `:529` | `pcrec_emit_startpos_guard` | `char t[PCREC_STARTPOS_GUARD_TEXT_MAX]` | bare OTHER limits macro, no margin — same shape as `emit_vm.c`'s `mguard` (§4 below) |
| `:3534` | `emit_stay_table` | `char name[PCREC_MAX_EMIT_NAME_LEN + 16]` | derived + margin; own comment: *"the SHARED emitted-name constant, not a hand guess"* |
| `:5596` | `scan_tables_bitmap` | `char name[PCREC_MAX_EMIT_NAME_LEN + 16]` | same shape and margin as `:3534`, different call site |
| `:5995` | `emit_scan_loop` | `char lv[PCREC_MAX_EMIT_NAME_LEN + 24], le[PCREC_MAX_EMIT_NAME_LEN + 24]` | 2 declarators, same expression — the file's only multi-declarator (c) statement |
| `:7215` | `pcrec_emit_prologue` | `char probe[PCREC_STARTPOS_GUARD_TEXT_MAX]` | bare OTHER limits macro, no margin — third site sharing this constant with `:529` and `emit_vm.c`'s `mguard` |

**Cross-file observation.** `PCREC_STARTPOS_GUARD_TEXT_MAX`
(`src/core/limits.def:360`, "[K50]... sized by the ENCODING BACKEND's
own guard text, not by the pattern") sizes **three** category-(c) sites
total across the two files — `emit_vm.c:11465`'s `mguard` (EP2's own
finding, "the ONLY buffer in the file already sized by a governing
limit") plus these two in `emit_dfa.c`. Read together, category (c) is
not "one hand-picked exception per file" — it is one recurring shape
(a bare OTHER governing-limit macro with no margin) appearing at both
emitters' own boundary-guard call sites, plus the `PCREC_MAX_EMIT_NAME_LEN
+ margin` shape appearing at three more `emit_dfa.c` sites doing the
same kind of derived-name sizing EP2 found five instances of in
`emit_vm.c`.

---

## 4. The combined floor for the repaired criterion

EP2's recommended repair: state the stage-3 acceptance criterion over
`char <ident>[` with **ANY** size expression (not literal-only), excluding
only `Vm.up` by name — the one struct field (`emit_vm.c:376`, `char
up[80]`) that lens 10's own scope note says stays in place, migrated
later or never (`lens10_emission_kit_charter.md` §3's SCOPE NOTE), and
which is therefore not one of wave 1's scratch-buffer retirement targets
even though it is syntactically identical to every category-(a) row
this census counts.

Using this script's own (more complete, per-declarator) numbers rather
than EP2's — since §2 above shows EP2's total undercounts by one real
declarator, and the repaired criterion's whole point is completeness:

| | statements | declarators |
|---|---:|---:|
| `emit_vm.c` raw (§2) | 58 | 67 |
| `emit_dfa.c` raw (§3) | 23 | 25 |
| **combined raw** | **81** | **92** |
| less `Vm.up` (`emit_vm.c:376`, category a, by name) | −1 | −1 |
| **COMBINED FLOOR** | **80** | **91** |

**80 declaration statements / 91 declarators** is the population a
stage-3 acceptance check should require to be byte-neutral (or fully
migrated behind `pcrec_sb_fragf`/the emission kit) across both emitters, with
`Vm.up` carrying its own standing exception by name rather than by any
structural rule — per lens 10's scope note, it is not "a scratch buffer
this census missed the reason for," it is a deliberately out-of-wave-1
field the check must not perpetually flag.

---

## 5. What this instrument cannot see

- **A statement matching `char <ident>[<expr>]` where `<expr>` is not a
  bare literal, a bare `PCREC_MAX_EMIT_NAME_LEN`, or one of the shapes
  actually present today** would fall into category (c) by construction
  (the catch-all), so the acceptance criterion this census supports
  ("ANY size expression") cannot be defeated by a new shape appearing —
  but this ALSO means category (c) is not a fixed, auditable list; a
  reviewer reading a future re-run's category-(c) rows must read each
  one, the same way this doc reads emit_dfa.c's six by hand above.
- **A `char` array declared through a `typedef` or a macro that expands
  to a `char [...]` member** would not be found — the scan looks for the
  literal token `char` immediately followed by a declarator list; a
  macro-generated declaration reads as whatever the macro's OWN
  definition site looks like (nothing of this shape was found in either
  file at this commit — both are hand-written declarations throughout).
- **A `char *` pointer declarator sharing a statement with array
  declarators** (none exist in these two files today, but the parser
  handles it by construction) contributes zero rows for the pointer part
  and one row per array part — silently correct, not silently dropped,
  but worth stating since it is untested against a real example.
- **Line attribution to an enclosing function** uses `reviewlib`'s
  depth-0-to-depth-0 walk, which does not distinguish a function body
  from a struct/union/initializer body at the SAME nesting level other
  than by `classify_header`'s own heuristic (documented in
  `reviewlib.py`, validated by `function_census.py`'s own transcript);
  `Vm.up`'s own row correctly reads `(struct field / file scope)`
  because it sits inside the `Vm` struct's own braces, not a function's.
- **This is a static census of declared buffer SIZES, not of any
  overflow, truncation, or migration-readiness property** — it answers
  "how many, in which category," not "which of these are safe today" or
  "which would break if migrated." EP2's own K38-adjacent comments
  (quoted throughout §2–3 above) are the load-bearing safety record for
  the sites that already had an incident; this census does not re-derive
  or re-verify any of them.

---

## Validation summary

- `make -j4 CC=gcc-16`: clean build (worktree `w2census`, branch
  `lane/w2census`, off `main` at `f6474777`).
- `tools/review/fragment_census.py src/gen/emit_vm.c src/gen/emit_dfa.c
  --out /tmp/fragment_census_check.tsv`: runs clean, 92 combined rows.
- Every multi-declarator statement the script reports was independently
  read against the source with `sed -n` (§1, §2, §3) and confirmed real.
- The one EP2-vs-script declarator discrepancy (§2) was traced to a
  specific line, read against the function's own adjacent comment, and
  confirmed to be a real, uncounted declarator rather than an artifact of
  masking or bracket-depth tracking.
- No `src/`/`cli/`/`lib/` file touched. Not an `abi` event: nothing
  emitted moved.
