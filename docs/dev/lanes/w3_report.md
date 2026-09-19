# [REVW.3] WAVE 3 (LAYERING) — lane w3 report

Branch `lane/w3` from `main` at `ed8f1098`. Five item commits plus this
report, in the brief's order. Opus. Nothing merged; nothing outside
`/Users/fdicostanzo/pcrec` touched.

| commit | item |
|---|---|
| `a4ea61e0` | 1 — the DUMP TIER moves to `src/dump/` (lens 6 L4) |
| `82060948` | 2 — `src/gen/enc/` → `src/enc/`, a layer between core and parse (L1) |
| `0b9b2e9e` | 3 — the LAYER MODEL in tool and prose (L3 / ruling M4) |
| `4145be47` | 4 — the rxt MINIMAL CUT (R1) |
| `7f16bbc0` | 5 — `internal.h`'s declaration tail grouped by defining layer (L5) |

**Nothing is owed.** Every number below was measured on this branch.

---

## 0. The three things worth reading first

**(a) The call-level back-edge census is 30, and the `driver` tier is why
it is not 19.** Lens 6 §2.3 predicted that filing `core/compile.c` in a
`driver` tier "reclassifies 20 of 39 back-edges as forward edges
truthfully, and leaves a residue of 19 that are worth looking at — which
is the number a refactor wave should actually be aimed at." It does
reclassify those 20. It also creates **22 new back-edges pointing the
other way**, so the count goes UP rather than down, and every one of the
22 is `ctx_fail` or `ctx_nomem`. `compile.c` defines the two diagnostic
primitives every layer routes failure through, and `pcrec_default_options`
besides. *The file is itself two layers — the exact shape lens 6
diagnosed one level up for the directory, recurring inside the file the
diagnosis was about.* §2 has the matrix; nothing is proposed for it here
(D77).

**(b) Lens 6 priced the dump move at "0 anchors" and left its own
coupling grep unrun** ("`grep -rn "syntax_dump\.c\|axes_dump\.c" tests/`
should be run by the wave… it is outside the enc/rxt populations this
lane priced," §2.4). Run here: **two sabotage rows**, S18 on
`syntax_dump.c` and S241 on `schema_dump.c`, plus 62 path-qualified
citations across live surfaces. Both rows re-aimed and both DETECTED
solo. *A cost stated by the lane that did not measure it is a guess, and
this one was the "cheap, 0-anchor rider".*

**(c) One sweep site needed a fix, not a substitution, and the general
form is worth keeping.** `run_cpset_structure.sh`'s CHECK 1R re-runs
every CHECK 1 needle against a `git archive` of a HISTORICAL pin and
requires each to go RED there. One reads `enc.h`. Re-spelled to the new
path it would still be red — because the FILE does not exist at that path
in the old tree, not because the `max_cp` field is absent, which is the
only thing the row claims. *A relocation can convert a check's red from
"the property is absent" into "the file is absent" with no test failing
and no reviewer seeing it.* Fixed by having the reference side FIND the
header by name, with a loud failure if the old tree carries none.

---

## 1. Per item: what moved, what was re-aimed, what the sweep said

`scripts/emit_sweep.py` is committed as of this morning and this lane is
its first customer. §3 reports how it behaved. Every row below is the
REAL run against ref `ed8f1098`; the self-check ran once, at item 1,
and passed.

| item | c-default | c-vm | emit-ir-vm | composition | movers / asym |
|---|---|---|---|---|---|
| 1 | 3517 | 3518 | 3518 | 32 producing / 96 artifacts | **0 / 0** |
| 2 | 3517 | 3518 | 3518 | 32 / 96 | **0 / 0** |
| 3 | 3517 | 3518 | 3518 | 32 / 96 | **0 / 0** |
| 4 | 3517 | 3518 | 3518 | 32 / 96 | **0 / 0** |
| 5 | 3517 | 3518 | 3518 | 32 / 96 | **0 / 0** |

Population: 3,938 argv rows, 304 composition files, every run. DELIVER
witness OK on all five. Reach never moved by a single row across the
whole wave, which is the strongest statement available that nothing
started or stopped compiling.

Per item also: `make -j4 CC=gcc-16` clean, `make strict` clean,
`make test-codegen` **8/9** (the sole FAIL is the standing darwin
`nm could not read arm_a.o (no rx_search symbol)` red, reproduced not
introduced), and anchor integrity **284 records / 268 rows / 0
mismatches** — identical to the branch point's, re-measured after every
item.

### Item 1 — the dump tier

`src/parse/{syntax,axes,schema,limits}_dump.c` → `src/dump/`. Every
include in the four files is `-Isrc`-rooted, so not one `#include`
spelling moves; `Makefile`'s `LIBSRCS` gains `$(wildcard src/dump/*.c)`
and the generic object rule already handled a new directory.

Re-aimed: 62 path-qualified citations — `src/core/internal.h` (7),
`tests/registry/` (13, across `axes_registry_check.sh`,
`registry_check.c`, `CLAUDE.md`), `docs/spec/registry.md` (6),
`src/core/{CLAUDE.md,limits.def}` (4), the four moved files' own headers
(5), `src/parse/` (4), `src/gen/` (2), `cli/main.c`, `src/opt/atomic.c`,
`tools/review/{clone_candidates.py,CLAUDE.md}`,
`docs/{pcre2_compliance.md,design/CLAUDE.md,dev/known_issues.md}`,
`docs/testing.md` — plus the two `SAB_FILE` rows.

New `src/dump/CLAUDE.md` carries the four file entries moved verbatim out
of `src/parse/CLAUDE.md`, the tier's charter and the leaf rule that keeps
its link-cleanness structural. `limits_dump.c` had no entry in any
`CLAUDE.md` and gains one, written from its own header rather than
invented.

**Historical records were deliberately NOT edited** — lane reports, lens
reports, `plan_completed.md`, the 2026-09-17 census TSV pins. One site
needed care rather than a rule: `docs/testing.md`'s F1 entry, whose prose
and repro command are re-aimed while its fenced block is a verbatim
2026-08-13 compiler transcript, so it keeps the old path and gains a
sentence saying so.

**Item 4 carries a late fix belonging to this item**: three citations in
`tests/registry/axes_registry_check.sh` where the directory and the
filename sit on different lines of one comment. A one-regex path sweep
cannot see them; they were found by re-grepping for the bare directory.

### Item 2 — the enc move

All six include back-edges the 2026-09-17 review found were one directory:
`core/compile.c:14`, `ir/dfa.c:111`, `ir/nfa.c:35`, `opt/lower_enc.c:134`,
`parse/parse.c:36`, `parse/rxt_compose.c:75`, each reading only the DATA
half of `PcrecEnc`. At `src/enc/` all six are forward edges.

Fourteen `#include "gen/enc/enc.h"` sites re-spelled (the six back-edges,
both emitters, `cli/main.c`, the three inside the directory, and the two
test `.c` files); `PCREC_GEN_ENC_H` → `PCREC_ENC_H`; `Makefile`'s
wildcard and its `GEN_TABLES` `.inc` prerequisite.

**`third_party/ucd-16.0.0/generate.py`, which no review source prices**,
hardcodes the destination in three places — the module docstring's
derived-artifact list, `FOLD_TEXT_OUT`, and a self-describing sentence
inside the generated file's own header text. All three re-aimed, then
`make gen-tables` RUN: it writes `src/enc/utf8_fold_pairs.inc` (nothing
is left at the old path) and the regenerated file differs from the
committed one in **exactly one line**, that self-describing comment's own
path. The table data is byte-identical. That comment is a C comment in
the INCLUDING translation unit, sitting above the string literals, so it
reaches no artifact — checked at the include site in `enc_utf8.c` rather
than assumed. `uprops_tables.inc` and `fold_tables.inc` were untouched by
the same run.

Prose that travels with the directory got both simpler and WIDER. `enc.h`
and `enc/CLAUDE.md` both said "Nothing in `src/core`, `src/gen`, `cli/` or
`lib/` is touched". As `src/gen/enc/` that could say `src/gen` and mean
"everything above me"; at `src/enc/` there are four layers above, and
they are now named one by one.

### Item 3 — the layer model

`include_graph.py` gains `enc` and `dump` as ordinary directory additions
and `driver` through `FILE_LAYER`, a per-file tier override table. A table
and not an `if` on one path: any file may be given a tier its directory
does not imply, the mechanism is the same for the second entry as the
first, and the table is the one place to read what the exceptions are. It
has one entry today, which is a fact about the tree and not about the
mechanism.

**`driver` sits BELOW `dump` on a measurement.** Exactly one symbol
reference runs between the two tiers in either direction:
`dump/syntax_dump.o` calls `pcrec_default_options`, defined in
`core/compile.o`. `driver → dump` is zero.

`tools/review/out/include_*.tsv` regenerated, the other census snapshots
left at the 09-17 pin. **`include_backedges.tsv` is 0 rows**, from 6 — and
the tool's own docstring now says at length why that is a statement about
INCLUDES and not a clean bill of health, which is the review's Method
Finding #2 written where a reader of the output will meet it.

### Item 4 — the rxt cut

`Ctx` gains `compose`, a `PcrecComposeFn`, set beside `cx.defs` from the
same entry; the call site becomes `if (cx.compose) root = cx.compose(...)`
at the same position on the same inputs. `src/core/compile_defs.c` is new
and holds `pcrec_compile_defs`, which passes `pcrec_rxt_compose`.

**Proven by `nm`, in both directions.** At `ed8f1098`,
`nm -u build/obj/core/compile.o` names `_pcrec_rxt_compose`. Here, `nm`
over the same object finds NO `rxt` symbol at all, defined or undefined,
and `compile_defs.o` names exactly two: `_pcrec_rxt_compose` and
`_pcrec_compile_driver`.

**0 anchors, verified rather than assumed**: `grep -rn rxt_compose tests/`
is empty, and none of the **twelve** rows anchored
`SAB_FILE="src/core/compile.c"` (ten at report time — the count is a
floor) quotes the composer call, `ncap_primary`, or a `compile_driver(`
call line.

**One deviation from lens 6's "2 files edited, 1 added" and its reason.**
`compile_defs.c` must reach the driver, so something in `compile.c` must
be non-`static`. Making `compile_driver` itself non-`static` would put a
bare, unprefixed `compile_driver` in the library's symbol table — the
namespace hazard lens 9's P5 is about — and RENAMING it would stale about
thirty comments across thirty files that cite the driver by name, four of
them `--list-axes` description strings a caller reads. So the driver stays
`static` and keeps its name, and `pcrec_compile_driver` is its one
exported FACE, a pure forward. It is an export boundary, not a second
pipeline: one `setjmp`, one retry ladder, one compile.

The byte saving is stated honestly at the new file's own head rather than
overstated: lens 6's four-arm measurement shows `-Wl,-dead_strip` /
`-Wl,--gc-sections` ALONE already recovers 43,968 of 44,448 bytes; the
source cut removes ~480 further bytes and two symbols. It is done for the
structure.

### Item 5 — the internal.h grouping

Group sizes by declaration unit: core 10, enc 0, parse 5, ir 6, opt 24,
gen 32, driver 4, dump 10. The `enc` group is kept EMPTY rather than
omitted — the seam publishes through its own header, the empty group says
so, and a future `enc` declaration has a place.

**It is a reordering and nothing else, checked mechanically.** With
comments stripped and whitespace collapsed the declaration multiset is
identical: 740 units before, 740 after, 0 missing, 0 extra. Of 661
comment blocks, every one survives; exactly ONE was dropped, the bare
`/* ---- stage entry points ---- */` label the new headers replace, with
nine headers and a banner added. Nothing moved to another file.

Four declarations needed a judgement rather than a lookup, each recorded
at its group header: `pcrec_startgate_needed` is a `static inline` defined
in the header itself (filed core, not with its ir/gen callers);
`pcrec_compile_defs` is under `src/core/` by path but is the driver's
second entry (filed driver); and the interleaved type islands each
travelled with the group that uses them, with `PCREC_DFA_DEAD` sent to ir
(`src/ir/dfa.c` is what returns it) rather than forward to the opt
declaration that happened to follow it.

**A finding against my own first draft.** The group headers first read
`defined in src/core/*.c`, and `/*` inside a C comment is gcc's
`-Wcomment`, which the harness's own `GENCFLAGS` promotes to an error
(coding guide §3.2, lane `cmtfix`'s incident). Seven headers fired it on
the first build. Spelled `defined under src/core/` instead. *The rule was
written down and read this morning and still cost a build.*

---

## 2. The call-level back-edge census

Method: lens 6 §2.2's, re-run — `nm -g` over the built objects for
definitions, `nm -u` for references, joined on symbol, bucketed by the
defining object's directory. **48 objects** (47 at lens 6's measurement;
`compile_defs.o` is item 4's). Reproduce with the script preserved at
`/private/tmp/.../scratchpad/w3/callcensus.py`; it takes the object
directory and the comma-separated layer order.

```
CALL-LEVEL cross-layer edges (rows = caller layer, cols = callee layer)
from\to   lib  core   enc parse    ir   opt   gen driver  dump   cli
lib         0     0     0     0     0     0     0      0     0     0
core        0     0     0     0     0     0     0      4     0     0
enc         0     4     0     2     0     0     0      0     0     0
parse       0    22     2     0     0     5     0      5     0     0
ir          0     3     3     2     0     1     0      4     0     0
opt         0    20     1     4     0     0     0      7     0     0
gen         0    22     7     6     0    15     0      2     0     0
driver      0     7     2     3     4     8     3      0     0     0
dump        0    19     0    24     0     1    10      1     0     0
cli         0     0     0     0     0     0     0      0     0     0
```

**30 back-edge symbol references**, against this tool's include-level 0:

```
opt -> driver : 7      core -> driver : 4      gen -> driver : 2
parse -> driver: 5     ir   -> driver : 4      enc -> parse  : 2
parse -> opt  : 5                              ir  -> opt    : 1
```

The three numbers that matter, and they separate cleanly:

| tree | back-edges |
|---|---|
| lens 6's measurement, pre-wave | 39 |
| after items 1+2, **before** any `driver` override | **28** |
| after items 1+2+3, with the override | **30** |

**The whole 39 → 28 is item 1.** `parse → gen` goes 10 → 0 (`axes_dump.o`'s
ten `pcrec_dfa_axis_*_cands` calls) and `parse → opt` 6 → 5
(`syntax_dump.o`'s `pcrec_ast_stamped_by`) — exactly the two rows lens 6
tagged L4, now forward edges from a tier above `gen`. Nothing else moved:
the enc move takes six INCLUDE edges forward and no call edge, because
`core → enc` was already a back-edge under lens 6's own proposed order.

**The 28 → 30 is the `driver` override, and it is the finding.** It
reclassifies `core → {parse, ir, opt, gen, enc}` = 20 as forward, and
introduces `{core, enc, parse, ir, opt, gen} → driver` = 22. Every one of
the 22 is `ctx_fail` or `ctx_nomem`, plus `dump → driver`'s single
`pcrec_default_options`. Those are base-tier primitives living in a
driver's file.

This also settles lens 6's own 33-vs-31 disagreement about the "invisible"
subset by making it moot: the pre-wave number this lane can attest to is
39 total, and the post-wave number is 30 with 0 include-visible, so **all
30 are invisible to every instrument in the tree**. A future wave aiming
at the residue should aim at a FILE that is two layers, not at a model
that is still wrong.

---

## 3. `scripts/emit_sweep.py` as a first customer

It worked as documented and needed no change. Notes for the next lane:

- **The self-check is worth its four minutes exactly once.** Two
  independent builds of `ed8f1098`, all four streams, all identical at
  full reach — after which `--no-self-check` is the right flag for every
  later item, and the real run alone is ~137 s.
- **Its pinned floors never fired** and every stream came back at or above
  its measured value: 3517/3518/3518 against floors of 3480, 32 producing
  / 96 artifacts against a 300-file floor. The populations proved
  perfectly stable across five items, which is the behaviour the PINS
  comment predicts for this shape of count.
- **The reach figure is the load-bearing output, not the pass count** —
  w2x's own lesson, and it held here in a way worth recording: for wave 3
  the expected answer was "0 movers" on every stream, and a sweep that had
  silently lost reach would have printed exactly the same "0 movers". The
  five identical reach rows are what make the zeros evidence.
- One convenience it does not have: no way to say "the working side is a
  commit on this branch" without a build. Not needed here (`--bin
  build/pcrec` is the lane's own build) and not worth building (D77).

---

## 4. Anchors

**284 records / 268 rows / 0 mismatches** at the branch point and after
every one of the five items — the population did not move, because every
re-aim in this wave is a `SAB_FILE` PATH change over text that relocated
verbatim. `replace.py` matches whole-file and line-agnostically, so a
verbatim relocation costs zero anchor-text edits (coding guide §3.4) and
this wave is the clean case that rule describes.

| row | item | anchor file | re-aim | solo verdict |
|---|---|---|---|---|
| S18 | 1 | `syntax_dump.c` | `SAB_FILE` path | **DETECTED** |
| S241 | 1 | `schema_dump.c` | `SAB_FILE` path | **DETECTED** |
| S-U5 | 2 | `enc_utf8.c` | `SAB_FILE` path | **DETECTED** |
| S-U6 | 2 | `enc_utf8.c` | `SAB_FILE` path | UNDETECTED **as declared** |
| S-U9 | 2 | `enc_utf8.c` | `SAB_FILE` path | UNDETECTED **as declared** |
| S116 | 2 | `enc_byte.c` | `SAB_FILE` path | **DETECTED** |
| S229 | 2 | `enc_utf8.c` | `SAB_FILE` path | **DETECTED** |
| S233 | 2 | `enc_byte.c` | `SAB_FILE` path | **DETECTED** |
| S236 | 5 | `internal.h` | none needed | **DETECTED** |

Zero unexpected verdicts across all nine runs. S-U6 and S-U9 carry
`SAB_EXPECT=UNDETECTED` on `main` — pre-existing and documented at their
own rows, not a consequence of the move; the runner scores them correct
and both runs report `unexpected: 0`.

Three further rows cite the enc directory only in PROSE or
`SAB_DOC_FIGURE` — S68, S109, S133 — and were re-pointed. Prose is not an
anchor and nothing in the tree checks it, which is why it has to be swept
by hand (w2x §6's class).

---

## 5. The APPROACH.md and coding-guide hunks, for Frank

**`APPROACH.md` §8 (Repository Layout) is rewritten and is his document,
so it is flagged rather than buried.** The section conflated base and
driver in one breath — *"core/ — driver, options, arena, diagnostics, AST
defs"* — which is precisely what item 3 fixes. Its ASCII tree was also
independently stale long before this review: it showed
`engine_dfa.c`/`engine_vm.c`/`enc_ascii.c` and an `src/rt/` directory that
does not exist, and described `third_party/` as an imported test corpus.
The new section states the layer order first, then a tree that matches
`ls`, then two short notes saying which parts were wrong and why. **The
staleness pre-dates the review and no source mandated this edit**; it was
taken because wave 3's own model change is the natural place and leaving a
freshly-corrected model beside a stale tree would be worse than either.
§4's two `src/gen/enc/` path citations are re-aimed and are mandated.

**`docs/dev/coding_guide.md` gains §1.9**, "Know which LAYER you are
writing in, and depend only leftward": the order, the two tiers that are
not directories, the override table as the home for a second exception,
and one sentence that is the operative one — *a new cross-layer call is
invisible to every check in the tree, so decide its direction yourself, at
the point you write it.* The guide is what every C writer reads first,
which is why the measured 30-against-0 gap is stated there and not only in
the tool.

`src/CLAUDE.md` gains the order, the base/driver split, the measured
driver residue and the instrument's blind spot; `tools/review/CLAUDE.md`
re-states the layers and re-dates its own 6-row finding as acted on.

---

## 6. What waves 4 and 5 need to know

- **Wave 4's brief must cite `src/dump/axes_dump.c`.** The code review's
  own X9 / `axes.def` citations (`2026-09-17-code-review.md:167-171`) say
  `src/parse/axes_dump.c:375-668`, written before this wave. The file is
  747 lines live, not the 731 the review recorded, so the line range is
  stale independently of the move.
- **Item 5 is wave 5's survey, already done.** The `L9-P5` namespace split
  and the deferred `internal.h` header split share a root cause, and the
  grouping is the survey either would otherwise start with: parse 54.2%,
  opt 16.9%, core 14.2%, gen 12.4%, ir 2.2% of 225 declarations. The
  groups are the cut lines.
- **The `driver` residue is a standing item for whoever wants the
  call-level number down**: 22 of 30 back-edges are `ctx_fail`/`ctx_nomem`
  in `compile.c`. Moving those two primitives (and
  `pcrec_default_options`) into a base-tier file would take the census to
  8 with no behaviour change. Not proposed here — D77, and it is an
  emitted-byte-neutral but real code move that deserves its own row.
- **`FILE_LAYER` is where a second per-file exception goes.** It is a
  table precisely so the second entry costs nothing the first did not.

---

## 7. What the sources got wrong about the tree

1. **Lens 6 §2.3's "leaves a residue of 19"** — refuted, see §0(a)/§2. The
   driver reclassification raises the count, and the reason is inside
   `compile.c`.
2. **Lens 6 §2.4's "0 anchors" for the dump move** — there are two, and
   the report says in the same section that it did not run the grep.
3. **Lens 6's 33-vs-31 internal disagreement** about the invisible subset
   is superseded by §2's measurement rather than reconciled.
4. **`limits_dump.c` had no `CLAUDE.md` entry anywhere.** Four dump files,
   three entries — the directory rule had been quietly short by one since
   [LIM-1].
5. **`APPROACH.md` §8's tree** named three files and a directory that do
   not exist (§5).
6. **The fact sheet's open question 4** (is item F built or proposed) was
   ruled BUILT by the brief and is built; question 5 (`src/dump/` vs
   `cli/dump/`) was ruled `src/dump/`; question 6 (the override mechanism)
   is answered by `FILE_LAYER`; question 3 (what the rider "rides") is
   answered by building it as its own commit, first, because the call-level
   census in item 3 depends on it having happened.

---

## 8. Validation: complete vs owed

**Complete.** Per item: `make -j4 CC=gcc-16`, `make strict`,
`scripts/emit_sweep.py` (four streams, reach reported), `make
test-codegen` 8/9, anchor integrity 284/268/0. Plus, once each where the
item touched them: `tests/registry/axes_registry_check.sh` 102/0,
`tests/uprops/run_uprops_tests.sh` 47/0 (the `gen-tables` staleness
check's own suite, item 2's), `tests/resource/run_resource_tests.sh`
27/0/0 with one platform skip (item 4's — its Section 0 raw-allocation
FILE-SET census is unmoved, `compile_defs.c` allocating nothing),
`tests/codegen/run_cpset_structure.sh` 28/0 (items 2 and 4), and the nine
solo sabotage drives in §4.

`tests/thread/run_thread_tests.sh` SKIPs on this box — gcc-16 has no
arm64 TSan runtime — so the comment edited there is correct but unrun
here. Pre-existing and unrelated to the edit.

**Not run, by instruction**: the full `make test` (the manager's merge
gate) and `make mech` in full. **Owed: nothing.**

**Not an abi event.** No emitted byte moves on any of 3,938 corpus rows
at three argv shapes or 96 composition artifacts, across all five items.
**No `docs/spec/` hunk is owed** — nothing `lib/pcrec.h` exposes changes,
`pcrec_compile_defs` is internal and keeps its signature, and the
composer runs at the same point on the same inputs. `docs/spec/registry.md`
and `docs/spec/cli.md` carry path re-aims only.

---

## 9. Rulings received

The brief itself ruled the fact sheet's open questions: `src/dump/` as the
dump tier's home and its own tier at the top beside driver; item F built
this wave; the per-file tier override table as the `driver` mechanism, as
a general mechanism with one entry; `driver` vs `dump` placed by measured
call edges. No mid-flight ruling was requested or received, and nothing
was blocked.
