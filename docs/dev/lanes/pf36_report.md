# pf36 — [PATFACTS] step 3.6 (R3): unify mrl.c/callgraph.c saturating arithmetic

Lane pf36 (sonnet), 2026-09-28, branch `lane/pf36` off main `457eee4d`.
Commit `70e7ccd7`.

## What shipped

`pcrec_mrl_sat_add`/`pcrec_mrl_sat_mul` (`src/opt/mrl.c`) and
`pcrec_cg_sat_add`/`pcrec_cg_sat_mul` (`src/opt/callgraph.c`) were the same
four-line saturating-arithmetic algorithm typed twice —
`docs/design/patfacts/inventory.md` R3's finding. Unified into ONE shared
primitive, `pcrec_sat_add`/`pcrec_sat_mul(long long a, long long b, long
long cap)` (`src/opt/mrl.c`), taking the ceiling as a PARAMETER — exactly
the signature lens 1's X3 (the 2026-09-17 code review,
`docs/dev/reviews/2026-09-17-code-review.md` and
`tests/core/sat_arith_check.c`'s own header) already named as the
destination.

`callgraph.c`'s own `CG_EXP_INF` macro (`(long long)1 << 40`, the same
value as `PCREC_MINW_MAX` under a different name) and its extra leading
guard (`a >= cap || b >= cap`) are both retired. The guard's redundancy on
the real call-site domain (non-negative operands) is not something this
lane re-derived — `sat_arith_check.c`'s own CHECK 1 header already proves
it algebraically (`a >= 0, b >= 0: a >= cap implies a + b >= a >= cap`),
and the merge builds on that proof. Every call site in both files now
passes `MRL_MINW_MAX`/`PCREC_MINW_MAX` explicitly (same macro value, so no
call site's arithmetic changed).

**`src/gen/emit_vm.c`'s `pcrec_vm_fadd`/`pcrec_vm_fmul` are a THIRD,
independent copy of this algorithm** (lens 1's X3 names all three), and
this lane deliberately did NOT unify it — `design.md`'s step 3.6 row text
names mrl.c/callgraph.c only, and emit_vm.c sits in a higher layer (gen)
than mrl.c's home (opt). `tests/core/sat_arith_check.c`'s cross-family
check now compares TWO independent implementations (`pcrec_sat_add`
against `pcrec_vm_fadd`) instead of three, which is what keeps the check's
whole reason for existing — an agreement nothing else enforces — genuinely
tested rather than trivially true.

## Why `src/gen/emit_vm.c` and `src/core/limits.def` changed (asked directly)

Neither carries a functional edit; both are comment/prose-only, found by
the post-hoc grep sweep for every reference to the retired names (a step
the brief's file list did not anticipate, since `docs/design/patfacts/
inventory.md` R3 and the design row only name mrl.c/callgraph.c).

- **`src/gen/emit_vm.c`** (2 lines, one comment block near
  `<prefix>_search`'s root MRL check): a comment explaining why that check
  is a width COMPARISON rather than an unconditional `return 0` names
  `pcrec_mrl_sat_add`/`pcrec_mrl_sat_mul` as one of the two routes to
  `PCREC_MINW_MAX`. Renamed to `pcrec_sat_add`/`pcrec_sat_mul` (with a
  `src/opt/mrl.c` pointer) so the comment does not describe a function
  that no longer exists. No code line touched.
- **`src/core/limits.def`** (1 line): `PCREC_MINW_MAX`'s own `desc` field
  ("where"/prose column) read `"src/opt/callgraph.c: the minimum-width
  analysis' saturation ceiling..."` — already slightly wrong before this
  lane (the analysis is mrl.c's; callgraph.c was a re-declaring consumer)
  and stale after the merge (callgraph.c no longer re-declares the value
  at all). Corrected to name mrl.c and describe the new direct sharing.
  **This field IS caller-observable** — `--list-limits` prints it as the
  `desc` column (`src/dump/limits_dump.c:113`) — confirmed by a live diff:
  `diff <(ref --list-limits) <(new --list-limits)` moves exactly this one
  line, prose only, no value/unit/kind/override column touched. **No
  `docs/spec/` hunk is owed**: this row's `anchor` field is empty (`""`),
  and `limits_dump.c`'s own header states the boundary — an empty anchor
  means the row is NOT one of `docs/spec/limits.md`'s caller-facing
  promises, only this file's own internals catalogue, which is exactly
  the tier D80 exempts. `bash tests/registry/limits_check.sh` (33/0,
  includes the census that dispositions every `PCREC_LIMIT` row) confirms
  nothing else reads this row's prose text.

## Sabotage rows touched

- **S254** (the row this step's own gate names): re-anchored onto the
  unified `pcrec_sat_mul`'s boundary line. Verified DETECTED by hand
  (applied via the real `tests/mech/lib/replace.py` mechanism, rebuilt,
  re-ran `tests/core/run_core_tests.sh`, reverted): `mul:
  pcrec_sat_mul/pcrec_vm_fmul DISAGREE at (1, 549755813889):
  1099511627776 / 549755813889` — the identical numbers the pre-merge row
  recorded (`... 1099511627776 / 549755813889 / 549755813889`, the third
  number was `pcrec_cg_sat_mul`'s, now gone). `checks passed: 7 -> 6`,
  `checks failed: 0 -> 1`, matching before and after exactly.
- **S58, S59, S-U4** — NOT this step's own subject (they sabotage
  `pcrec_minw`/`pcrec_cwmax`'s own analysis arms, unrelated to the
  saturating-arithmetic primitive), but their literal `SAB_BEFORE`/
  `SAB_AFTER` anchor text embedded calls to the retired
  `pcrec_mrl_sat_add`/`pcrec_mrl_sat_mul` spellings, found only by a
  tree-wide grep for the old names AFTER the rename — not something the
  design row or the inventory's R3 entry could have named in advance.
  Each re-anchored to the renamed call (same site, same disambiguating
  context — S58/S-U4 by the preceding function signature/comment line
  that already existed to tell `pcrec_minw`'s A_CLASS arm apart from
  `pcrec_cwmax`'s identical-looking one; S59 by the inner
  `pcrec_minw(a->l)` call that already told it apart from
  `pcrec_cwmin`'s A_REP arm). All three verified: SAB_BEFORE occurs
  exactly `SAB_COUNT` time(s) in the current tree, `lib/replace.py`
  applies/reverts cleanly, and the sabotaged `mrl.c` compiles
  (`gcc-16 -c`) — direct measurements, not assumed from the rename being
  "obviously safe".
- `scripts/m6read_check_sab_anchors.py`: **326 sabotages checked (342
  anchor sites), all anchors resolve** — the tree-wide tripwire, run
  after every row touched above, confirms no OTHER row was left stale by
  this change.

## Gate: A/B diff ZERO

Reference binary built from `git archive HEAD` (main `457eee4d`, i.e. the
tree before this lane's changes — no `git stash` involved after an
earlier false start with one, caught before it cost anything) into
`/tmp/pf36_ref`, entirely outside both mandated repos' working trees.
Swept every `pattern`/`pattern-esc` row from every `tests/**/*.rxt` file
(via `--list-source --features all`, avoiding hand-parsed escaping) at
both encodings, `--emit-main -o out.c` with BOTH binaries using the
**same `-o` basename in separate directories** — the first sweep attempt
used different basenames (`ref.c`/`new.c`) and read 7,653 false movers,
this house's own documented `-o`-basename trap; caught by a two-pattern
sanity diff before trusting the number, then the whole sweep re-run
correctly.

    total pattern-config cells: 8,102
    both refuse:                  423
    identical:                  7,679
    movers (byte-differing):        0
    new-only-refuse (regression):   0
    ref-only-refuse (newly-accepts): 0

**Zero movers, zero refusal-set changes**, over the full shipped corpus
at both encodings — includes `tests/recursion/`'s 34 files, which is
where `callgraph.c`'s own fixpoints (the ones whose arithmetic actually
moved files) are exercised. Reproduction: `/tmp/pf36_ab_sweep.py` (not
committed — scratch instrument, scope mandate; reproducible from this
report's method description and the reference-binary recipe above).

## Also validated

- `make -j4 CC=gcc-16`: clean build.
- `make strict CC=gcc-16`: **clean** ("whole tree compiles clean with
  `-Werror -Wshadow`").
- `bash tests/core/run_core_tests.sh`: **all green** (sat_arith_check 7/0,
  sb_fragf_check/sb_stamp_check/features_opt_check/varexp_check
  unaffected and green).
- `bash tests/registry/limits_check.sh`: **33/0** (confirms the one
  `--list-limits` prose line that moved is disposed of correctly and
  nothing else reads it).
- `python3 scripts/m6read_check_sab_anchors.py`: **all anchors resolve**
  (326 rows / 342 sites).

## NOT run (owed)

Per BOILERPLATE box coordination: the manager's `make test` was running
in the main tree for this lane's whole working period, and lane `litf5`
holds the box lock throughout. `test-mrl` and `test-codegen`
(`run_group.sh`-based, moderate weight) and `test-recursion` (explicitly
named as needing the lock) were NOT run — the A/B corpus sweep above is a
lighter-weight, more targeted proof of the same "no emitted byte moves"
claim (it compiles every corpus pattern directly with both binaries,
which is what those harness sections ultimately check via `pcrec`+`gcc`,
minus the `gcc` compile and the runtime match assertions). Owed exact
commands, to run once the box is free:

    make test-mrl CC=gcc-16
    make test-codegen CC=gcc-16
    make test-recursion CC=gcc-16

Given the A/B sweep's zero-mover result already covers every emitted
byte these three sections would additionally check for (they add no new
*pattern population* beyond `tests/**/*.rxt`, which the sweep already
covers in full — `test-recursion`'s own `run_recursion_diff.sh` drives
additional SUBJECTS through the same artifacts, not additional
patterns), a red result on any of the three would indicate an
INFRASTRUCTURE issue (a stale reference pin, a harness assumption this
lane's rename broke) rather than a behavior change this lane introduced
— but that is a prediction, not a substitute for running them.

## Scope note

The brief named `src/ir/mrl.c` and `src/ir/callgraph.c`; both files are
actually under `src/opt/` (confirmed by grep, per the brief's own "locate
the files by grep if paths differ" instruction) — no `src/ir/mrl.c` or
`src/ir/callgraph.c` exist in this tree.

## Files touched

`src/opt/mrl.c`, `src/opt/callgraph.c`, `src/core/internal.h`,
`src/core/limits.def`, `src/gen/emit_vm.c` (comment only),
`src/opt/CLAUDE.md`, `src/gen/CLAUDE.md` (comment only), `docs/testing.md`,
`tests/core/sat_arith_check.c`, `tests/core/run_core_tests.sh` (comment
only), `tests/core/CLAUDE.md`, `tests/mech/run_sabotage_matrix.sh`
(comment only), `tests/mech/sabotages/S254_mrl_sat_mul_boundary_off_by_one.sh`,
`tests/mech/sabotages/S58_mrl_minw_underreports.sh`,
`tests/mech/sabotages/S59_mrl_minw_overreports.sh`,
`tests/mech/sabotages/S-U4_width_rule_byte_units.sh`.

No `docs/spec/` hunk (no caller-observable behavior change; the one
`--list-limits` prose line is internals-catalogue only, per its own empty
`anchor` field). No `abi` event.
