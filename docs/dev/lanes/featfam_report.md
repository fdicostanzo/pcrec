# featfam report: feature families design, graduation table, bench effect (lane featfam, sonnet, 2026-11-06)

Docs and measurement only. Deliverable: `docs/design/feature_families.md` (PROPOSED rev 0).
Nothing under `src/ cli/ lib/ memfn/ tests/` touched; no named set changed; D37 addendum
text below is a draft, NOT in `decisions.md`. Branch `lane/featfam` off main `cc7edf500`.

## For the owner, in plain words

1. The 150-of-392 figure reproduces exactly: the bare default refuses 163 of the bench's 392
   patterns, and 150 of those say "requires module" (assertions 58, lookaround 21,
   unicode-props 14, atomic-groups 11, ...). The other 13 are limits no family changes.
2. If `extended` were the bare default, 333 of 392 compile instead of 229 (85% vs 58%). Of
   the 34 still refused for a gated module, 17 are recursion (the `pcre2` family), 12
   callouts and 4 vars (opt-in by your ruling); 10 more need modules pcrec has not built.
   On the 34 bench patterns that came from real sources ("wild"): 17 compile today, 30
   under extended, 24 under basic, 33 under pcre2 or all.
3. `basic` CAN be derived from the registry (its engine column is usable), but the
   mechanical rule drops `assertions`, because the single construct `\K` is VM-only.
   `assertions` is the biggest bench refuser (58 patterns); keeping it in basic needs a
   choice (question A).
4. Five modules in the definitions have no producer: `conditionals` and `branch-reset`
   (in extended), `verbs` (in pcre2), and `comments`, `misc`, `extended-classes` (basic).
   A frozen set that names an unbuilt module changes what it accepts the day the producer
   lands, which D37's "compiles identically forever" does not obviously allow (question B).
5. The graduation evidence is thinner than the plan assumes for exactly the modules `basic`
   is made of: `quoting` and `named-groups` have no D6 panel I could find and no match
   differential against libpcre2. The big modules (assertions, atomic-groups, backrefs,
   lookaround, recursion) have design panels and per-module libpcre2 differential scripts,
   but I found no implementation CLOSE panel for them (question D).
6. `all` today holds all 19 modules including the six unbuilt ones, `callouts` and `vars`;
   `code-c` is not in it. `${x}` and `(?C1)` both compile under `all`. PC-3 cannot test
   `vars` at all (libpcre2 reads `${name}` as `$` plus literal text).

### Questions (plain words, with a leaning)

A. **Where does `assertions` go?** (`\b`, `^`, `$`, `\A`, `\z` are plain; `\K` is the
   odd one out because it needs the backtracking engine.) Choices: basic with `\K` refused
   under basic; extended only; or split `\K` into its own small module so the rule stays
   exact. Leaning: split `\K` out if that is cheap, otherwise extended-only with a note;
   cost of extended-only is 43 bench patterns that basic users could not compile.
B. **What does "frozen" promise?** The list of modules, or the language accepted? Leaning:
   freeze the list but name only BUILT modules in a frozen member (P2), so unbuilt ones
   join the next version when they ship. Cost: `extended1` is smaller than your
   definition until conditionals and branch-reset exist; P3 (wait for them) delays the
   default move on builds nothing schedules.
C. **Do moving names (`--features extended`) move only at announced boundaries, like the
   bare default?** Leaning: yes; the frozen `extended1` is the unconditional pin.
D. **Does a design-time panel count as D37's "checkpoint panel"?** If yes, 8 of 10 built
   modules meet the criterion today; if only a close panel counts, only `classes`,
   `modifiers` and `unicode-props` do (plus whichever panel I could not find). A light
   panel plus one libpcre2 differential each would close `quoting` and `named-groups`.
E. **Say "no construct that needs backtracking", not "linear time", for basic?** Any
   capture group already puts a pattern on the VM engine and I did not measure the VM's
   worst case. Leaning: yes, drop "linear".

## What was measured, what was read

MEASURED (this box, `build/pcrec` of the worktree at `cc7edf500`, `make -j4` niced, no gcc
compile of the emitted C): registry engine column per module (`--list-syntax`); the
`all`/`std1`/`none` stamps; `(?C1)a`, `${x}a`, `\K` under `--engine=dfa`; the 392 bench
patterns under 8 feature sets (script and raw TSV: `$PCREC_TMPDIR/scratch/featfam/run.py`,
`results.tsv`, not committed); the wild subset (34 rows with a `source_url` across
four `provenance.tsv` files; the scoreboard counted 32 over two directories).

READ, not re-run: PC-3, PC-4, every module differential script and `make test-X`
target membership (checked by grep of the Makefile target list and file headers, not run;
the kit's gate jobs hold the box lock and I never took it); the panel files (opened
first lines/headers, not audited); D37, spec text.

INFERRED: PC-3 vacuity for `vars`; that no close panel exists for the modules I list as
"design only" (I searched `docs/dev/reviews/` file names and grep hits, `plan_completed.md`
panel lines; a panel recorded elsewhere would be missed).

## D37 ADDENDUM DRAFT (text for a later `decisions.md` entry; not applied)

> **Addendum (date, [FEAT-FAMILIES]).** The frozen-named-set mechanism gains three
> FAMILIES, each a moving name over versioned frozen members: `basic` -> `basic1`,
> `extended` -> `extended1`, `pcre2` -> `pcre2-1`. A member is an explicit module list
> (never a reference to another member) and obeys D37 unchanged: its contents never change
> after it ships, a graduate or a new module forms the NEXT member of its family, and an
> artifact stamps the frozen member's name and expanded list. A moving family name, like
> the bare default, moves to a newer member only at an announced version boundary.
> `basic` = the modules none of whose registry rows is VM-only (checked against the
> registry's engine column when a member is cut); `extended` = `basic` plus `backrefs`,
> `lookaround`, `atomic-groups`, `conditionals`, `branch-reset`; `pcre2` = `extended`
> plus `recursion`, `verbs`. `callouts` is in no family. The pcrec-only modules (`vars`,
> any future extension) are in `all` and in no named family (Frank 2026-11-06). `std1`
> stays resolvable forever, is no longer advertised, and is not a family member. `all` and
> `none` stay the unfrozen ends. [If question B is ruled P2: a frozen member lists only
> modules with a producer at the cut.] [If question D is ruled "design panel counts":
> the criterion's "checkpoint panel" is read as a D6 panel on the module's design OR its
> landing, recorded in `docs/dev/reviews/`.] Moving the BARE default from `std1` to
> `extended` is the next announced boundary after the criterion holds for its modules and
> travels with the suite re-baseline D37 lists (reject_gated rows, corpus `features`
> directives, check07, the PC-3 gate state) and an abi event for the changed stamp text.
> The name `pcre2` claims compatibility, not equality (D26): some PCRE2 syntax is out of
> scope for good.

## Spec hunks the default move owes, and what rides [IFACE-PUSH]

Split in two, because only the second changes emitted bytes:

Step A, add the names (no default move, no new CLI option or field, no stamp field):
- `docs/spec/cli.md` §1.17¶1: vocabulary sentence gains the family and frozen-member names;
  the `unknown module 'X'` diagnostic's hint text ("also 'all', 'none', or a named set:
  std1") lists them (a `src/parse/enabled.c` text change, so a `tests/cli` expectation moves).
- `docs/spec/pattern_language.md` §2.3¶2 (named sets do not combine with module names,
  now for the new names too) and §2.3¶4 (utf8 adds `unicode-props`, `ucp` to a family).
- `docs/spec/cli.md` §1.17¶3 or a new paragraph: what the families contain, `all`'s
  contents including `callouts`/`vars`, and that `code-c` is in none.
- No emitted byte changes for any existing compile, so no abi bump for step A (the
  stamp string only differs when a new name is used; MEASURED nothing, INFERRED from
  the stamp being the set name the caller gave).

Step B, move the bare default (waits for a version tag; [IFACE-PUSH]):
- `docs/spec/cli.md` §1.17¶1: "the bare default ... is `std1`" -> the new frozen member;
  `--features none` sentence stays.
- `docs/spec/pattern_language.md` §2.3¶3: "With no `--features`, the set is `std1` =
  {classes, modifiers}" and its `--features named-groups` example (still valid: explicit
  lists replace the default).
- `docs/spec/match_api.md` §6.3.11 (`PCREC_FEATURE_SET` / `PCREC_FEATURE_MODULES` example
  values) and §8.2 (`pcrec_options.features` NULL means "no request", not the default:
  D37's 2026-08-13 addendum says this reopens WITH the library channel promotion, so
  the library default is a decision to take at [IFACE-PUSH], not here).
- abi event (D76/D94): every default-compiled artifact's stamp text changes; grep the
  `.abi` stamp readers, the identity gate's (B) pin, `tests/` expectations, and
  `make test-codegen`/registry/rxtsource before delivery.
- The D37 re-baseline list, now in the opposite direction: reject_gated rows and any
  gate-equivalence check that assume `std1` as the default; the PC-3 gate state;
  `tests/fuzz` (it passes no `--features`, so its default becomes the larger set, which
  widens what the fixed-seed gate generates only if the generator is widened too).
- Rides [IFACE-PUSH] ONLY if a new stamp field (`PCREC_FEATURE_FAMILY`), a new option field
  or a new CLI listing option (`--list-families` already names a different thing: the
  registry's construct families, `registry.md` §5, so a feature-family listing needs a
  different name) is wanted. Names alone, and the default move itself, need none of those;
  the default move needs only the version tag.

## STATE AT HANDOFF

- Branch `lane/featfam`, committed (see git log); worktree clean after commit.
- Files: `docs/design/feature_families.md` (new), `docs/design/CLAUDE.md` (one line),
  `docs/dev/plan.md` ([FEAT-FAMILIES] status line only), this report.
- `plan_lint` passes (299 rows, 0 violations); `check_claudemd_size --all` passes.
- Rulings file `featfam_rulings.md` re-read before the report: empty, nothing applied.
- No run owed. Not done: no panel on the note; PC-3/PC-4/module differentials not re-run;
  the VM's worst case on basic constructs not measured; bench measured byte-encoding only.
- Scratch: `$PCREC_TMPDIR/scratch/featfam/` (run.py, results.tsv, emitted .c probes).
