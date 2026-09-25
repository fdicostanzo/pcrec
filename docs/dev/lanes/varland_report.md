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
6. Part (b), the `emit_sweep.py` unpredicted cells, was read from the tree
   directly (dump-surface diffing) rather than from a fresh sweep run,
   because the box's one-heavy-suite rule kept it queued behind the
   identity gate's four-axis validation for this lane's whole working
   period. See §5 for the dispositions and what is OWED.

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

Ran fresh, foreground-then-backgrounded, `CC=gcc-16`, `KEEP=1`:

| axis | (B) same/differing | (A) same/differing | bref-rename | var-construct | verdict |
|---|---|---|---|---|---|
| default | 2561/0 | 2164/0 | 155 | 15 | PASS/PASS |
| vm | 2562/0 | 2143/0 | 155 | 15 | PASS/PASS |
| noprefilter | OWED | OWED | OWED | OWED | OWED |
| nocaptures | OWED | OWED | OWED | OWED | OWED |

**OWED AT HAND-OFF**: the noprefilter/nocaptures axes and the script's own
`checks passed:`/`checks failed:` trailer. Log: `/tmp/recid_run3.log`
(this box; not under the repo, KEEP=1 workdir printed at the log's own
tail on completion). Exact command already running detached
(`nohup ... & disown`); poll for the line `checks failed: 0` — the
`elision`/`linkage` axes note in the script's own header does not apply
here (this gate only sweeps `default`/`vm`/`noprefilter`/`nocaptures`).
If `noprefilter`/`nocaptures` do not also read `differing=0`, that is a
NEW finding (this lane's two exceptions were validated only on `default`
and `vm` at hand-off) — read the axis's own diff file's `REGION DIFFERS`
lines before assuming they need a third exception.

`make strict CC=gcc-16`: OWED (not yet run — nothing under `src/`/`cli`/
`lib/` touched by this lane, so it is not expected to move, but per
BOILERPLATE it must still be run before delivery is called complete).

**S273 solo sabotage run**: OWED
(`bash tests/mech/run_sabotage_matrix.sh S273`) — held behind the
identity-gate validation by the one-heavy-suite rule.

---

## §4 — WHAT WAS BUILT

- `tests/codegen/run_recursion_identity.sh`: `bref_rename_rewrite()`, the
  `rb_bref` baseline threaded through the (A) comparison, two new named
  buckets (`rbrefrename`/`rvarnew`) with their own messages and
  non-vacuity arms, a corpus-wide backref/var text census printed at
  startup, and the acceptance-line message extended to name both.
- `tests/mech/run_sabotage_matrix.sh`: the `recidentity` suite word +
  case arm.
- `tests/mech/sabotages/S273_span_match_length_off_by_one.sh`: the new
  row (see §0 finding 4).
- `tests/codegen/CLAUDE.md`, `tests/mech/CLAUDE.md`: documentation for
  both of the above.

## §5 — PART (b): THE THREE UNPREDICTED `emit_sweep.py` CELLS

Read from the tree directly (dump-surface diffing on `build/pcrec`, which
at this lane's HEAD is byte-for-byte 809aab12's emitted output — nothing
under `src/`/`cli`/`lib` touched), not from a fresh sweep run: the box's
one-heavy-suite rule kept the identity-gate validation running for this
lane's whole remaining time.

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

**composition asymmetric=4 and emit-ir-vm movers=41: OWED, NOT YET
DISPOSITIONED FROM A REAL SWEEP RUN.** The hypothesis in the brief
(the 1e90aa8a reference refuses `.rxt`/`.rxtin` sources carrying a `var`/
`var-unset` line) matches exactly THREE files by direct grep
(`tests/vars/basic.rxt`, `tests/vars/unset.rxt`,
`tests/rxtsource/fixtures/var_bindings_accept.rxtin`) — one short of the
measured 4, and `tests/vars/caseless.rxt` (no `var`/`var-unset` line, only
inline `${...}` patterns) is the most likely fourth, but WHETHER it
actually reads asymmetric (a refusal-vs-success split, or a differing
artifact NAME SET — `sweep_composition`'s two distinct triggers) versus
merely a byte-content mover needs the real sweep's diff hunk to say, not a
guess. The emit-ir-vm figure (41 vs the corpus's own union backref/var
population of ~176) likewise needs the actual `sweep_argv_stream`
population and mover list — plausibly the backref-rename population
restricted to patterns that both (a) reach `--engine=vm --emit-ir`
successfully on both sides and (b) show a listing-text (not just
program-region) difference, which is a narrower filter than comparison
(A)'s. **OWED**: `python3 scripts/emit_sweep.py --ref 1e90aa8a --bin
build/pcrec --tree .` (backgrounded once the box frees), then read
`composition`'s and `emit-ir-vm`'s printed mover/asymmetric lists against
these two hypotheses before disposing either cell.

---

## §6 — RULINGS RECEIVED

None mid-flight; the brief's own two-part charter is restated in full at
the top of this report.
