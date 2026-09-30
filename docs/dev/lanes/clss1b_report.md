# Lane clss1b: [CLS-TREE] S1 follow-up fixes (report)

**Lane:** clss1b, sonnet, engine tier, implementation. **Branch:** `lane/clss1`
(continued from lane `clss1`'s worktree), tip at handback `<see git log>`,
from `cc406648`. **Charter:** the manager's four rulings on
`docs/dev/lanes/clss1_report.md` §3/§7 and D131 addendum 1. **Date:**
2026-09-29.

## 1. Summary

Four items, all implemented, all validated:

1. **D131 addendum 1's fitted term.** `PLACE.kit_disp_bytes` (578 B), added
   to K's byte estimate ONLY where the SELECTION compares it against
   another form. Reproduces clsfit's ruled picks on the K53 twelve
   EXACTLY: 12/12 K at `−2`, 12/12 P3 at `0`, 12/12 P2 at `+2` — where the
   STOPPED table (unadjusted model bytes) read P3 on 2/12 at `0`.
2. **The `studies/` dependency is gone.** `tests/clskit/ref/` is a frozen,
   provenance-headed copy of the eight Python modules `tests/clskit/`
   needs (crosscheck.py's own report of the CLAUDE.md's stated six had
   two missing transitive imports, found empirically — see §3).
   `crosscheck.py`/`populations.py` import only `ref/`.
3. **The atom table left the per-class `ROWS`.** D131 item 6's atom table
   is an artifact-level choice (S2); `ROWS` no longer has an "atom-shared"
   row, `ClsPred`/`ClsDeny`/`ClsSelectIn` lost their now-dead atom fields.
   The atom FORM, its emitter and its differential are unchanged.
4. **Confirmed, no code change needed:** (a) `B1` (a whole-span bitmap) is
   right as the per-class default byte form — it already was; (b) the
   shared atom table is correctly an artifact-level concern, discharged by
   item 3.

The full `test-clskit` section is GREEN (5/5), `make strict` is clean,
`limits_check.sh` is 35/0, `make test-codegen` is 11/12 (the one red is
the standing darwin `nm` probe, reproduced identically against main's own
binary), and S360-S364 all measured DETECTED, one id per invocation.

## 2. D131 addendum 1: the fitted dispatch/prologue term

### 2.1 The fit

The addendum's own text: *"K's byte ESTIMATE, as read by the SELECTION
table, gains a fitted dispatch/prologue term: its own data cell with
provenance (sweep_k53 λ=4, measured − model)."*

Data: `clss1_report.md` §3's own twelve (K53 model bytes, K53 measured
bytes) pairs, sourced from `studies/cls_tree_study/results/sweep_k53.tsv`
at λ=4 (`n1size` policy rows). `measured − model` for each:

| set | measured − model |
|---|---:|
| L | 575 |
| ^L | 530 |
| C | 553 |
| ^C | 552 |
| Cn | 606 |
| ^Cn | 536 |
| Xan | 529 |
| ^Xan | 561 |
| Xwd | 597 |
| ^Xwd | 691 |
| Unknown | 602 |
| ^Unknown | 600 |

**Constant fit:** mean 577.67 B, residuals −49 to +113 (sample std ≈ 46 B).

**Per-section linear fit tried and rejected.** Regressing the same twelve
differences on `K`'s own section count (`sections` column, same tsv rows)
gives `diff ≈ 488.05 + 4.865·nsec` — and explains **R² = 0.06** of the
variance a bare constant does not (SS_res 23,040.6 → 21,653.0, a 6%
reduction). The scatter has no visible relationship to section count: the
two sets with the fewest sections (Cn, Unknown, 16 each) sit mid-table
while the two with the most (Xwd, ^Xwd, 22 each) sit at opposite ends of
the range. A constant is both simpler and no worse.

**Landed:** `PLACE.kit_disp_bytes = 578` (`src/gen/clskit.c`), the mean
rounded to the nearest integer.

### 2.2 Where it is read, and where it is deliberately not

`kit_sel_bytes(SelCtx *s)` returns `s->k->bytes + PLACE.kit_disp_bytes`.
Its two callers are `mid_gate()` (the `0`/`+1`/`+2` gate) and
`pred_holds()`'s `P_P3_SMALLER` case (the `−2`/`−1` gate) — every place
the selection COMPARES K's bytes against another form. `ClsKit.bytes`
itself (the DP's own sectioning objective, `pcrec_clskit_partition`'s
output) is never touched, and neither is `out->bytes` for a chosen
`CLSF_KIT` row (`pcrec_clskit_select`'s own comment now says so). That is
D131 addendum 1's own boundary: *"The DP's own sectioning model is
unchanged... the term is added after the sectioning is chosen, so the
study cross-check does not move either."*

### 2.3 Reproduction, measured

Direct driver dump, tune positions −2/0/+2, deny=0, all twelve K53 sets
(`^` = complement):

| set | −2 | 0 | +2 |
|---|---|---|---|
| every one of the twelve | `K` (row `kit`) | `P3` (row `mid-page3`) | `P2` (row `speed-page2`) |

**12/12 at every position**, matching `clsfit_report.md`'s ruled table
exactly (`−2/−1`: smaller of K/P3, i.e. K on this population; `0`/`+1`:
P3 at K ≥ 16 sections and P3 ≤ 1.26×K; `+2`: smaller of P2/B1 where `0`
chose P3, and P2 wins on all twelve). No residual cells: every one of the
twelve reproduces the ruled pick at every position tested.

The crosscheck's own independent restatement (which carries its own
`KIT_DISP_BYTES = 578`) agrees with `clskit.c`'s dump on **all 20,685
selections** (591 sets × 5 positions × 7 denies) — 0 disagreements.

## 3. The `studies/` dependency

`docs/CLAUDE.md`: `studies/` is "never built or tested by pcrec's make."
Lane clss1's `tests/clskit/crosscheck.py`/`populations.py` imported six
`studies/cls_tree_study/` modules live (`sys.path.insert(0, STUDY)`),
which is exactly that violation — `test-clskit` is part of `make test`,
so those six files were quietly a load-bearing part of the suite.

### 3.1 The true closure is eight files, not six

`studies/cls_tree_study/CLAUDE.md`'s own note (written by clss1) names six:
`clsets.py`, `proptest.py`, `kit.py`, `section.py`, `wholeset.py`,
`bench_bytes.py`. Copying only those six and pointing `sys.path` at a new
directory FAILS at import time: `bench_bytes.py` has unconditional
module-level `import loadgate` / `import emit`, and `proptest.py` has
`import emit` / `import section` — neither `loadgate.py` nor `emit.py` is
in the six, and a module-level `import` runs regardless of which function
is later called. Found empirically (`python3 -c "import bench_bytes"`
against a six-file `ref/` failed with `ModuleNotFoundError: loadgate`)
before any file was written twice. `emit.py`'s own `import kit` and
`loadgate.py`'s (stdlib-only) imports close the set — no further
transitive files are needed. **The frozen copy is eight files.**

### 3.2 What moved with the relocation, and what did not

`tests/clskit/ref/` is one level deeper than `studies/cls_tree_study/`
(three directories under the repo root instead of two). `clsets.py`'s
`REPO = os.path.abspath(os.path.join(HERE, "..", ".."))` — used to locate
`src/parse/uprops_tables.inc` — needed a third `".."`; its own header note
says so and the fix is the one behavioural line changed in any of the
eight files. `clsets.py`'s `byteclasses()` reads a HERE-relative
`results/byteclasses.tsv`; that data file (43 lines, a corpus-derived
byte-class census) is copied verbatim to `tests/clskit/ref/results/` —
diffed against the source, the data rows are byte-identical (only the
added provenance header differs). No other file in the closure reads a
file by a HERE-relative path that the driver/crosscheck path actually
exercises (`section.py`'s `discover` binary path exists only for
`partition_c()`, which nothing here calls).

### 3.3 Verified byte-identical before the switch

Before repointing `sys.path`, `populations.py` was run against BOTH the
frozen `ref/` copy and the live `studies/cls_tree_study/` (via a scratch
substitution of the one `sys.path` line) and the two 591-set population
files diffed **byte-identical** (`populations: 591 sets written to
...` both times, `diff` empty). That is the load-bearing check for a
"frozen copy" claim — not merely that it imports, but that it answers the
same as its source.

### 3.4 Each file's provenance header

Every one of the eight carries a header (after the shebang, before the
module docstring) naming its source path and the exact commit its content
was copied from (`git log -1 --format=%H -- studies/cls_tree_study/<f>`),
and the one behavioural deviation each file has (none, except `clsets.py`
and the tsv file). `studies/cls_tree_study/CLAUDE.md`'s "one consumer"
paragraph is REVERTED to its pre-clss1 text (nothing there imports it any
more); `tests/clskit/CLAUDE.md` carries the new `ref/` entry instead.

## 4. The atom table leaves the per-class `ROWS`

The ruling: *"D131 item 6's 'N ≈ 11 live class sites' counts sites across
an artifact, which a per-class selection cannot see. So the atom row must
NOT sit in the per-class table at every position. Remove it from the
per-class ROWS. Keep the atom-table FORM + emitter + differential, and
state in the report and in the code comment that its selection is an
artifact-level table built at S2."*

**Removed:** the `"atom-shared"` row from `ROWS[]`; `ClsPred::P_BYTE_ATOM`
and its `pred_holds` case; `ClsDeny::CLSD_ATOM` (the enum's other members
shift down, `CLSD_NDENY` 8 → 7); `ClsSelectIn`'s `nsites`/`atoms`/
`atom_index` fields (dead the moment no predicate reads them —
`pcrec_clskit_select` never touched them beyond the removed predicate).
`ClsChoice.bytes`'s ternary in `pcrec_clskit_select` dropped its now-dead
`CLSF_ATOM` branch (unreachable: no `ROWS` row answers that form any
more).

**Kept, unchanged:** `pcrec_clskit_atoms` (the O(256) partition),
`ClsAtomTable`, `pcrec_clskit_emit_atom_table`/`pcrec_clskit_emit_atom`
(the emitters), and the differential's direct exercise of all three
(`tests/clskit/clskit_driver.c`'s `build_atoms`/`emit_chunk`, which call
the atom API directly and never went through `ROWS`/`pcrec_clskit_select`
in the first place — the atom form's census and differential coverage are
untouched: `FORM ATOM 41 skipped=0`, same as clss1's own landing).

**Code comments** (`src/gen/clskit.c` above `ROWS`, `src/gen/clskit.h`'s
top-of-file "four things" list and `ClsSelectIn`'s doc comment) now state
the artifact-level placement explicitly, with the reason (a per-set table
has no input for a fact about the whole artifact's byte-class population).

**`ClsSelectIn` shrinks to three fields** (`tune`, `deny`, `kit`). S2's own
artifact-level atom-table mechanism will carry whatever input IT needs
(most likely `pcrec_clskit_atoms`'s output directly, read at the artifact
level rather than threaded through a per-set call) — nothing here
pre-builds that; D77's own rule.

### 4.1 Confirmations (a)/(b), no code change

- **(a) `B1` as the per-class default byte-form.** `ROWS`'s `"byte-table"`
  row (positions `0`/`+1`/`+2`, predicate `is_byte_set`) already answers
  `CLSF_BITMAP1`. Unchanged by this lane; confirmed correct as clss1 built
  it.
- **(b) the atom table is artifact-level.** Discharged by removing it from
  `ROWS` (§4 above) rather than merely stated.

## 5. Validation

| check | command | result |
|---|---|---|
| build | `make -j4 CC=gcc-16` | clean |
| strict | `make strict CC=gcc-16` | **clean** |
| the section | `PROCS=4 CC=gcc-16 bash tests/clskit/run_clskit_tests.sh` | **checks passed: 5, failed: 0**. Differential 591 sets / 8,451,676,390 code-point checks / 0 mismatches; law 146 × {K4,P3} / 325,320,704 checks / 0 mismatches; crosscheck 591 sets, 1,686 sectionings, **20,685** selections (was 23,640 — 591×5×7, NDENY 8→7), **7** rows (was 8), 0 disagreements, 3 ties (proptest BSEARCH rounding ties, unrelated, unmoved from clss1's landing) |
| bare-number scan | `bash tests/registry/limits_check.sh` | **35 passed, 0 failed** |
| codegen | `make test-codegen CC=gcc-16` | **11/12 scripts** (was 11/12 at clss1's own landing too). The sole red, `run_inline_capability.sh` ("no rx_search symbol"), reproduces IDENTICALLY against main's own `build/pcrec` — pre-existing, darwin-only, unrelated |
| mech | one id per invocation, tree `c104e07c` | **S360 3fail/2pass, S361 4fail/1pass, S362 4fail/1pass, S363 1fail/4pass, S364 1fail/4pass — all DETECTED**, `unexpected: 0, undetected: 0, unreached: 0, anomalies: 0, oracle-skipped: 0` on every one |
| K53 reproduction | direct driver dump | **12/12 at −2 (K), 12/12 at 0 (P3), 12/12 at +2 (P2)** — clsfit's ruled table, exactly |

**A finding along the way, fixed in the same lane rather than left for the
manager:** the `mid_gate` edit (item 1) respelled `s->k->bytes` as
`kit_sel_bytes(s)`, which staled `S363`'s anchor — caught by `make
test-codegen`'s own `[SABANCHOR]` check going red (not by inspection).
Re-anchored per `tests/mech/sabotages/CLAUDE.md`'s Conventions (copied
from the live source, same one dropped conjunct, intent unchanged;
verified: applies at exactly 1 site, `gcc -fsyntax-only` clean on a
scratch copy) and re-run solo — 1fail/4pass DETECTED, unchanged from its
pre-fix figure. `python3 scripts/m6read_check_sab_anchors.py`: **all 342
anchors resolve** (343 after S364, checked again post-landing).

### 5.1 S364, the new sabotage row

Drops the fitted term back out of `kit_sel_bytes` (`return s->k->bytes;`
in place of `return s->k->bytes + PLACE.kit_disp_bytes;`) — the exact
pre-fix STOPPED state §2.3 reports on. Every emitted form stays a correct
matcher, so the differential/census/law stay green by construction; only
crosscheck.py's independent restatement (carrying its own
`KIT_DISP_BYTES`) can see which ROW fired — the S363 shape one predicate
over. Measured solo: `clskit:1fail/4pass` DETECTED.

## 6. Owed to the manager

The full battery, per BOILERPLATE's async-validation rule (this lane did
not launch it — the box's heavy slot was owed to a prior lane's full
`make test` at clss1's own handback, and this lane's own validation
(§5) is targeted rather than the full gate):

    cd /Users/fdicostanzo/pcrec/worktrees/clss1 && make -j4 CC=gcc-16 && nohup caffeinate -s make -k test CC=gcc-16 > build/clss1b_make_test.log 2>&1 &

## 7. For the manager

1. **Nothing open from this lane's own charter.** All four items landed
   and validated; §5's SABANCHOR finding was fixed in-lane rather than
   left for review.
2. `docs/design/cls_tree_design.md` §1.7.3 (lines ~484-488) still
   describes the atom table as PART of the per-position `−2`..`+2`
   selection order (the pre-D131-item-6 analysis draft this lane's ruling
   corrects). It is prose in an already-adopted analysis section, not the
   normative table (that is D131 item 1, quoted verbatim in
   `decisions.md` and in `clskit.c`'s own `ROWS` comment) — flagged rather
   than edited, since this lane's charter is `src/`/`tests/`, not a design
   note revision.
3. **The next stage is unchanged from clss1's own §7**: S2 (the byte
   tier, including the artifact-level atom-table selection this lane's
   item 3 scoped precisely), S3 (`A_WCLASS`, needs nothing from here), S4
   (`pcrec_clskit_select` + `pcrec_clskit_emit_*` wiring, the abi ritual).
