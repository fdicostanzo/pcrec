# varland — the identity gate's owed landing verdict (recidfix's two files)

Lane `varland`, sonnet, 2026-09-25, branch `lane/varland` from `aa9e8ed4`.
Charter: `recidfix_report.md`'s "found, not fixed" (comparison (A) red 8/4)
plus `scripts/emit_sweep.py --ref 1e90aa8a`'s three unpredicted cells on
`809aab12`.

---

## §0 — FINDINGS FIRST

1. **The 170-pattern red was TWO causes, not one, and the report's own
   "165 closely matches 170" was a coincidence of size, not of
   composition.** Reading the actual differing list (not just its count)
   found 155 backreference-rename patterns and **15 that are not
   backreferences at all** — module `vars`' own `${...}` construct, which
   `ac4917d` cannot express in any form a rewrite could repair (see §2).
2. The fourth named exception is a **mechanical rewrite**, not a manifest —
   the first of this file's four exceptions that is. `ELIDED_PATTERNS`/
   `SIZE_TERM_REGION_MOVERS`/`ISLAND_PATTERNS`/`FOLD_PATTERNS` are all
   enumerated lists; a fifth list here would have meant "every
   backreference-bearing pattern in the corpus, kept in step with it
   forever" — exactly the K35 shape those four exist to avoid stating a
   fifth time.
3. The fifth exception (module `vars`) is `rcallbearing`'s own shape one
   module later: a population this gate's classifier was never scoped to
   exclude (the classifier is module `recursion`'s), admitted instead of
   excluded, once the subject's own region proves the construct
   (`run->var_value[`).
4. `run_recursion_identity.sh` had **no mech arm at all** before this lane —
   unlike its three `run_*_identity.sh` siblings — because its two
   from-source reference builds make it the single most expensive row the
   vocabulary could name. `recidentity` + **S273** are new; S273 proves the
   fourth exception's admission is exact-text-equality-after-substitution
   and not "resembles the rename".
5. A pre-existing, unrelated defect: this script's `awk`/`sed` pipeline
   (`prog_region`/`stamp_strip`/the new `bref_rename_rewrite`) is not
   `errors="surrogateescape"`-safe the way the python corpus-splitting stage
   already is (vartriage's/recidfix's own fix). `tests/vars/caseless.rxt`'s
   deliberate raw `\xff` witness trips `awk: towc: multibyte conversion
   failure` / `sed: RE error: illegal byte sequence` a handful of times per
   axis. FOUND, NOT FIXED — out of this lane's time box; noted in
   `tests/codegen/CLAUDE.md`'s new section and left for a future lane. It
   does not appear to corrupt any count (the var-construct bucket's
   admitted population matches its independent text census within the
   stated band on every axis measured).
6. Part (b)'s three `emit_sweep.py` cells are ALL fully dispositioned —
   `dumps` by direct dump-surface diffing (needed no sweep run), then
   `composition`/`emit-ir-vm` by a real `python3 scripts/emit_sweep.py`
   run once the box freed. **`emit-ir-vm movers=41` turned out to be a
   completely different population from the brief's own hypothesis**
   (the backref-rename population) — every mover is a `${...}`-bearing
   `tests/vars/*.rxt` pattern whose `--emit-ir` engine-forcing reason
   improves from a generic CLI-flag citation to the specific construct
   that forces it; the number 41 is coincidental, not evidence for the
   hypothesized cause. See §5.
7. **Wiring `recidentity` found WHY its three siblings
   (`atomicidentity`/`brefidentity`/`endvaridentity`) have sat registered
   with ZERO rows since 2026-08-22.** `run_recursion_identity.sh` (like
   `run_atomic_identity.sh`/`run_backref_identity.sh`) `git archive`s its
   pinned reference commits, which needs full git history — and every
   scratch tree `tests/mech/run_sabotage_matrix.sh` builds is
   `git archive HEAD | tar -x` with NO `.git` (MECH-2's own deliberate
   rule). The FIRST wiring attempt made `recidentity` fail INSTANTLY and
   UNCONDITIONALLY inside a scratch tree — `fatal: not a git repository`,
   then a hard-coded FAIL naming the pin unresolvable, regardless of
   whether S273's sabotage was applied at all: the worst possible shape a
   control can take. Fixed with a `git rev-parse --is-inside-work-tree`
   guard routing "no git history" to a loud SKIP (`checks passed: 0` /
   `checks failed: 0`, distinct from the pre-existing "pin doesn't resolve
   in a real repo" FAIL). Consequence: `recidentity` will now ALWAYS SKIP
   inside the mech matrix, so S273's OWN bucket-admission claim has no
   mech-matrix detector and had to be validated MANUALLY instead (§3a).
   See `tests/codegen/CLAUDE.md`/`tests/mech/CLAUDE.md`'s new sections.

---

## §1 — THE FOURTH EXCEPTION: `bref_rename_rewrite()`

`d93aa931`'s [VAR] M6 ruling ("one seam entry pair serving two constructs")
renamed `<p>_bref_match[_caseless]` to `<p>_span_match[_caseless]` and
changed its reference-side arguments from two offsets to a pointer+length
pair:

```
took = <p>_bref_match(subject, subject_length,
                  (size_t)ref_start, (size_t)ref_end,
                  scan_position);
-- becomes --
took = <p>_span_match(subject, subject_length,
                  subject + (size_t)ref_start,
                  (size_t)(ref_end - ref_start),
                  scan_position);
```

Root-caused byte for byte against a from-source `ac4917d` build before
writing anything (see the commit history for the exact diff).

**The admission is derived from the diff shape, not a pattern list**:
`bref_rename_rewrite()` applies the ONE substitution above to the
pre-module region (`rb`) and compares the result (`rb_bref`) to the
subject's region (`ra`). Composes with the fold exception: a pattern
stamping both a fold and a backreference (none in today's corpus, but the
mechanism is verified against `^(?i:(a))\1$` by hand) needs the rewrite
AND the fold's own `-fno-cls-fold` restore before the two sides agree, so
the fold/island branch's restore target is `rb_bref`, not raw `rb`.

**Non-vacuity**: an independent text census (numeric `\1`..`\9` plus named
`\k<>`/`\k''`/`\k{}`/`(?P=)` spellings, masked against character classes on
the same scan the call/free classifier already uses) is compared against
the bucket's own count at a wide (±30) band, printed on every run. Measured
on this tree: text census 161 (126 numeric + 35 named, 0 overlap),
bucket count **155 on every one of the four axes** — the numeric-only
census (126) alone would have undercounted by exactly the named population,
which is why both are computed and unioned.

## §2 — THE FIFTH EXCEPTION: module `vars`

Reading the population the fourth exception did NOT explain found 15
patterns per axis, all `${...}`-shaped (`^${v}$`, `^${v:-dev}$`,
`^${a:-${b}}$`, etc.) — module `vars`' own construct. `ac4917d` predates
module `vars` by roughly a month; it has no idea `${` means anything, so it
compiles a completely different program (two end-anchors around the
literal text `{v}`) with no textual relationship to `vm_var`'s emission.
No rewrite of `rb` can explain this — the correct claim is "this
construct existed in no compiler until it shipped", `ELIDED_PATTERNS`'
sibling reasoning turned into an admission rather than a fixed count.

Admitted once the subject's own region contains `run->var_value[`
(`vm_var`'s one emitted marker, verified unique to it). Non-vacuity: an
independent `${` text census (16, masked the same way) against a ±10 band.
Measured: **15 on every axis**; the one-pattern gap is `tests/vars/
caseless.rxt`'s raw `\xff` witness (finding 5, §0).

## §3 — VALIDATION

**COMPLETE. Full 4-axis run, `CC=gcc-16`, `KEEP=1`, log `/tmp/recid_run3.log`:**

| axis | (B) same/differing | (A) same/differing | bref-rename | var-construct | island | fold | verdict |
|---|---|---|---|---|---|---|---|
| default | 2561/0 | 2164/0 | 155 | 15 | 34 | 18 | PASS/PASS |
| vm | 2562/0 | 2143/0 | 155 | 15 | 52 | 27 | PASS/PASS |
| noprefilter | 2561/0 | 2165/0 | 155 | 15 | 34 | 18 | PASS/PASS |
| nocaptures | 2561/0 | 2188/0 | 155 | 15 | 23 | 10 | PASS/PASS |

Trailer: **`checks passed: 16` / `checks failed: 0`** — fully GREEN on all
four axes. Text census (printed once, independent of any axis):
numeric `\1`..`\9` = 126, named (`\k<>`/`\k''`/`\k{}`/`(?P=)`) = 35, union
= 161 (bref); `${` var population = 16. Both non-vacuity bands (bref
±30, var ±10) satisfied on every axis — 155 sits inside [131,191], 15
sits inside [6,26].

**§3a — S273, THE MECH-MATRIX ROUTE AND THE MANUAL ROUTE.** Wiring
`recidentity` found it can NEVER produce a real verdict inside
`tests/mech/run_sabotage_matrix.sh` (finding 7, §0): every scratch tree
that driver builds is `git archive HEAD | tar -x` with no `.git`, and
`run_recursion_identity.sh` needs full git history to `git archive` its
two pinned reference commits. Before the fix this made the arm fail
UNCONDITIONALLY (`fatal: not a git repository`, then a hard FAIL) —
detected only because a first solo `S273` run walked into it directly.
Fixed with a `git rev-parse --is-inside-work-tree` guard: "no git
history" now reads `SKIP: ... exit 0`, and `run_sabotage_matrix.sh`'s
`recidentity` case routes a `^SKIP:` banner to `any_skip=1` (the
`pc3`/`laexpand` convention). A solo `bash tests/mech/run_sabotage_matrix.sh
S273` re-run against the committed fix (tree `df867383`) **COMPLETED**:

```
reach:ok(1/1), recidentity:SKIPPED-no-git-history,
brefdiff:23fail/7pass, corpus:467fail/28646pass
DETECTED ( SKIPPED -- no oracle)
== mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0,
   unreached: 0, anomalies: 0, oracle-skipped: 0) at df867383 ==
```

`recidentity` reads exactly the predicted `SKIPPED-no-git-history` — the
guard fires as designed, no crash, no false verdict. `brefdiff` (23
fail/7 pass) and `harness` (the `corpus:` cell, 467 fail/28646 pass) both
independently DETECT the plant on their own answer-level terms —
`brefdiff`'s failing cells show exactly the predicted signature
(`'(a)\1'` answering `match 0 3` where the oracle says `match 0 2`, one
byte too long, on multiple subjects and via the find-all loop). The
overall row verdict is **DETECTED (SKIPPED — no oracle)**, the
`pc3`/`laexpand` suffix convention correctly naming the one arm that
declined to measure. `unexpected: 0` confirms no `SAB_EXPECT` mismatch.

Because `recidentity` structurally can never score S273 for real, the
row's OWN claim — that the bref-rename bucket does not admit this
off-by-one — was validated MANUALLY: `src`/`lib`/`cli` copied to a
scratch tree, the exact sabotage edit applied
(`"                  (size_t)(ref_end - ref_start),\n"` →
`"                  (size_t)(ref_end - ref_start + 1),\n"` in
`src/gen/emit_vm.c`), rebuilt with `gcc-16` (clean compile), then the
identity gate's own `bref_rename_rewrite()`/`prog_region()`/
`stamp_strip()` logic run by hand against `(a)\1`'s program region from
BOTH the sabotaged compiler and the real pre-module reference binary
(`$WD/pcrec_premodule` built during the earlier real 4-axis run).
**Result: the sabotaged region DIFFERS from the rewritten reference**
(the diff shows exactly the `+ 1` token) — it lands in `rdiff`, not the
bref-rename bucket, confirming the bucket does NOT admit it. Also
confirmed via `--emit-main` that the plant is a genuine answer-level
miscompile: `(a)\1` on `"aaa"` answers `match 0 2` on the clean compiler
and `match 0 3` on the sabotaged one (reading one byte past the
referenced group's end). All temp artifacts (`/tmp/s273_manual`,
`/tmp/s273_test*`, `/tmp/clean_test*`) cleaned up afterward.

`make strict CC=gcc-16`: **DONE, CLEAN** ("strict: whole tree compiles
clean with -Werror -Wshadow") — nothing under `src/`/`cli`/`lib/` touched
by this lane, as expected.

---

## §4 — WHAT WAS BUILT

- `tests/codegen/run_recursion_identity.sh`: `bref_rename_rewrite()`, the
  `rb_bref` baseline threaded through the (A) comparison, two new named
  buckets (`rbrefrename`/`rvarnew`) with their own messages and
  non-vacuity arms, a corpus-wide backref/var text census printed at
  startup, the acceptance-line message extended to name both, and a
  `git rev-parse --is-inside-work-tree` SKIP guard (finding 7, §0)
  distinguishing "no git history at all" (environment limitation, SKIP)
  from "the pin doesn't resolve in a real repo" (the pre-existing loud
  FAIL).
- `tests/mech/run_sabotage_matrix.sh`: the `recidentity` suite word +
  case arm, plus its own `^SKIP:` detection routing to `any_skip=1`.
- `tests/mech/sabotages/S273_span_match_length_off_by_one.sh`: the new
  row (see §0 finding 4).
- `tests/codegen/CLAUDE.md`, `tests/mech/CLAUDE.md`: documentation for
  all of the above, including the git-archive/SKIP discovery and its
  consequence for S273's validation route (§0 finding 7, §3a).

## §5 — PART (b): THE THREE UNPREDICTED `emit_sweep.py` CELLS

**ALL THREE FULLY DISPOSITIONED, `dumps` from the tree directly, the other
two from a REAL SWEEP RUN.** `python3 scripts/emit_sweep.py --ref 1e90aa8a
--bin build/pcrec --tree .` run once the identity gate + `make strict` +
S273 freed the box (log `/tmp/emit_sweep_varland.log`, 266.2s): self-check
PASSED (two independent rebuilds of the reference, all five streams
identical, no asymmetry, at full reach) before the real ref-vs-tree
comparison ran. Population: `argv=3995 composition_files=310
composition_producing=33 composition_artifacts=98`.

**dumps movers=4 (predicted +1, `--list-syntax`): DISPOSITIONED, all four
legitimate.** Reading each of the seven dump surfaces for a `vars`-shaped
row:

| surface | moves? | what moved |
|---|---|---|
| `--list-syntax` | yes (predicted) | the `${name}` construct's own registry row |
| `--list-families` | yes (not predicted) | a new `${name}` / `vars` family row |
| `--list-limits` | yes (not predicted) | two new rows, `PCREC_MAX_VAR_NAME_LEN` / `PCREC_MAX_VAR_NEST_DEPTH` |
| `--list-schema` | yes (not predicted) | two new BLOCK-scope rows, `var` / `var-unset` (the `.rxt` test-authoring directives) |
| `--list-definitions` | no | — |
| `--list-verbs` | no | — |
| `--list-axes` | no (false-positive grep, "invariant" substring) | — |

Every mover is module `vars`' own registry/limit/schema addition; none is a
defect. The report's own hint ("`--list-limits` +2 and the registry dump's
`vars` row") named 3 of the 4 — `--list-schema`'s two new rows (added
2026-09-13 by [DD-13b.W23.1], after whatever draft first predicted "+1")
were not in that hint's own accounting, which is likely why the arrived
count is one MORE than the hint's own math predicted (1 + 1 + 1 = 3
named, 4 measured). **DISPOSITION: no fix owed; the emit_sweep.py witness
baseline / composition manifest that names this row should record 4, not
1, going forward.**

**composition asymmetric=4: DISPOSITIONED, all four legitimate — and the
brief's own hypothesis was right, the fourth file was just found by the
wrong grep.** The sweep's own diff prints the FOUR rows by name and by
exact cause, all four `side_a_ok=False side_b_ok=True`:

| file | side_a's refusal |
|---|---|
| `tests/rxtsource/fixtures/var_bindings_accept.rxtin` | `[unknown-token-in-scope] ...:13: 'var' is not a pattern-block directive` |
| `tests/vars/basic.rxt` | `...:16: 'var' is not a pattern-block directive` |
| `tests/vars/caseless.rxt` | `...:24: 'var' is not a pattern-block directive` |
| `tests/vars/unset.rxt` | `...:27: 'var-unset' is not a pattern-block directive` |

`caseless.rxt` line 24 **is** `var v "abc"` (`^(?i)${v}$`'s binding) — the
lane's earlier grep for a `var`/`var-unset` line missed it (a plain
`grep -n "^var"` run against the file's raw \xff byte silently returns 0
matches under BSD grep's binary-file heuristic without `-a`; the file is
readable, the grep invocation was not `-a`). The refusal is at the
**format's own HEAD-PARSER level** (`[unknown-token-in-scope]`, nothing to
do with pattern compilation at all) — module `vars`' `var`/`var-unset`
`.rxt` directives postdate the pinned reference exactly as its pattern
construct does, so all four files are refused identically at the same
layer. **DISPOSITION: no fix owed; a fully expected consequence of the
[VAR] module landing, not a defect.**

**emit-ir-vm movers=41: DISPOSITIONED, all 41 legitimate and it is a
completely different population from the hypothesis (the backref-rename
one) — the number simply coincided.** The sweep's diff shows every mover
is a `${...}`-bearing pattern from `tests/vars/{basic,caseless,unset}.rxt`
(the fixture never reaches the argv streams, only `composition`), and
every one moves the SAME one line — the `--emit-ir` listing's `engine`
reason:

```
- engine  vm  forced by: --engine=vm
+ engine  vm  forced by: ${name} at pattern offset N
```

The pre-module reference has no `${...}` construct, so this stream's own
forced `--engine=vm` (D106/w2x's rule: `emit-ir-vm` ALWAYS forces the VM
route regardless of stream 1's engine) is the only reason it can name;
the post-module compiler recognizes `${...}` as its OWN VM-forcing cause
and reports the specific one instead. **41 reconciles exactly**: `wc -l`
on the three files' `pattern` lines gives 8 (`basic.rxt`) + 13
(`caseless.rxt`, `grep -a` needed for the same \xff-byte reason) + 20
(`unset.rxt`) = 41, and the `.rxtin` fixture's one pattern is not in this
count because it is composition-only. **DISPOSITION: no fix owed; a
diagnostic-text improvement that ships with the module, correctly
attributing the VM-forcing cause to the real construct instead of to the
sweep's own forced flag.**

---

## §6 — RULINGS RECEIVED

No design rulings mid-flight. One process instruction: the manager
directed the lane to stop idle-waiting on the Monitor tool for the
in-flight background validation ("the LOG is your trigger... poll the
log tail with a bounded foreground `timeout ... bash -c 'until grep -q
... ; do sleep 30; done'`"), and to proceed directly through `make
strict`, the S273 solo run, and `emit_sweep.py` in that order while
holding heavy-suite slot #1 across all three. Followed for the remainder
of the lane; the brief's own two-part charter is restated in full at the
top of this report.
