# compref report — compliance-page refresh (2026-11-06, lane compref, sonnet)

Docs only; nothing under src/ cli/ lib/ memfn/ tests/ touched. No compiler defect found, so no K-entry filed.
Method: `compliance-refresh` skill. Premise test first: all six disagreements reproduced as the scoreboard recorded them, with `build/pcrec` (default set and `--features all`) and a 10-line libpcre2 10.46 harness (scratch `$PCREC_TMPDIR/scratch/compref/p.c`, byte and UTF).

## Per disagreement

1. `\v` — TRUTH: built (module `classes`, default `std1`); compiles by default; libpcre2 accepts. The Character-types survey row (`REJECTED`/`PLANNED`) was stale, and the `\v` annotation carried a mangled sentence ("Now `REJECTED` to module `classes`"). CHANGED: survey row -> `OK` `—`; annotation sentence corrected (annotations.txt, rendered into the page).
2. `\p{..}` `\P{..}` — TRUTH: `OK-GATED`: refused "requires module 'unicode-props'" by default, compiles under `--features all`; libpcre2 accepts. The Unicode-properties section and the registry were right; the Character-types row (`REJECTED`) was wrong. CHANGED: that row -> `OK-GATED` `—`.
3. `(?C..)` — TRUTH: built by [INLINE-C] stages 1b-3 (2026-10-26..29): `(?C1)a` refused by name by default, compiles with `--features all`; the compliance Callouts section was already right. STALE: plan.md [M4-CALLOUTS] `not-started`. CHANGED: row moved verbatim to plan_completed.md as `STATE:completed` with a `completed:` line and a status line (its step-2 body, a pcre2_callout_block mirror, was amended by the 2026-10-26 D38 ruling; shipped ABI is `rx_callout_ref`). `scripts/plan_lint.sh`: 299 rows, 0 violations. Not changed (not mine): [MATCH-EVENTS] names "module `callouts` building" as a trigger; that trigger has now fired, the manager may want to re-read that row.
4. `\cX` `\o{}` `\N{U+..}` `(*script_run:)` `(?(R)` — TRUTH: refused with every module on ("not implemented yet" / "requires module 'verbs'"); libpcre2 accepts all (`\N{U+41}` only under UTF, error 193 in byte mode, which is why that registry row says recognition). The registry says `planned`; the page said `becomes —` (= no plan). CHANGED: `becomes` -> `PLANNED` for `\cx`, `\o{}`, `\N{U+..}`, `(*script_run:..)` family, `(?(R)` family, and `(?(assert)` (same conditionals row, same stale `—`); `\N{U+0041}` annotation extended with the 2026-11-06 measurement.
5. `(*atomic:..)` — NOT a disagreement: page (`REJECTED`/`PLANNED`, annotation `base:verbs-module-attribution-gap`, "Still a naming gap") and registry (module `verbs`, unbuilt) say the same; measured refusal "requires module 'verbs'" with all modules on. No change.
6. `(?|..)` — TRUTH: registry row module `branch-reset`, unbuilt; refused by name by default and "not implemented yet" under all; libpcre2 accepts. The page had no survey row (the only mention was a historical diagnostics table). CHANGED: new row `(?|...)` `REJECTED` `PLANNED` in Alternation, plus a keyed annotation.

## Also reflected
- [VLOOKBEHIND]: annotation on `(?<=...)`: designed (rev 2, pieces study, critic rounds), NOT built, awaiting build go.
- [CONDITIONALS]: annotation on `(?(1)a|b)`: PARKED, not built, one registry row for the whole family.
- K74 / [UTF-END-ASSERT]: annotation on `$` (`base:anchor-dollar`) naming it a known divergence under `-e utf8` at an ill-formed end (K74 widening: `\z \Z (?m)$ (?<!.)`). The status-table line for `DIVERGENCE` ("Currently none") was reworded to say no survey row carries it and open divergences live in annotations/K-list (K74, K34). No new `base:` key was needed (tests/ is out of scope), so all additions ride existing or registry keys.

## Checks
`--write-annotations`, then `--check` (144 rows), `--check-annotations` (93 keys, 21 blocks), `--names`, `--tension`: PASS. `make test-registry`: rc=0, no failing `test-` line (log in scratch `reg.log`). `plan_lint`: 0 violations.

## Left open (owner call, not a fact)
- `(?(R)`, `(?(assert)` are now `PLANNED`; the sibling `(?(n)` row is `PLANNED-HARD`. The registry does not grade difficulty, so I took the literal `planned` and did not guess `-HARD`. Same for `\cx`/`\o{}`/`(*script_run)`: `PLANNED` is the registry's word, difficulty not assessed.
- PC-2 survey (component 2) was not re-run: PCRE2 did not move.

STATE AT HANDOFF: committed on lane/compref; rulings file compref_rulings.md did not exist at any check (none applied).
