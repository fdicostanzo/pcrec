# tests/cli — CLI surface and library-API tests

Covers what the .rxt corpus cannot: argument parsing, output-file behavior,
error text and exit codes, and library-level properties such as stack usage.
Part of `make test` since M2.

## Files

- **run_cli_tests.sh** — the cases (count deliberately not hand-copied here —
  this line has drifted twice; `grep -c '^case[0-9]*()' run_cli_tests.sh` is
  the source): (1) `-o -` self-contained C that compiles
  standalone, (2) `--emit-main` producing a runnable binary, (3) prefix boundary
  validation, (4) `-o subdir/out.c` writing and compiling both files, (5) `--`
  before a pattern starting with `-` plus missing-value diagnostics, (6) error
  cases (no pattern, two patterns, unknown option), (7) a library-API smoke test
  for NULL arguments and double free, (8) a compile-time C STACK budget,
  (9) `-i` (OS-1/D23) end to end — accepted, reaches `options.caseless`,
  composes with `--` and `--emit-main`, documented in `--help`, and does NOT
  leak into a build that did not ask for it (the case-sensitive control),
  (10) the SR-3 syntax queries — `--list-syntax`, `--explain`, `--flavour`,
  since Q1 `--list-verbs`, since MOD-0.1 `--count-groups` (the running
  capture count's external channel, §18.1 — count cells oracle-verified
  against python re and a 300-pattern generated sweep at landing; refusals
  keep the compile diagnostics), and since MOD-0.1 slice 8 `--probe-ask`
  (§18.2's cursor-rule channel: one known cell pinned byte-exact, the
  10-field count, the §5.4 gate demotion pinned as a cell — result asks
  answered at verdict in the DEFAULT state; the enabled-state cells landed
  when the revisit came due at MOD-0.3c: `--features classes` at result
  produces `node`/`members` with the cursor still unmoved, both pinned
  byte-exact (probes false the day before, D33 §9.3) — and an
  in-repo cursor sweep over every registry row at claim+verdict, population
  FLOORED at 198 probes; the spec-side comparison belongs to
  tests/spec_mod0's check06, not here. Sabotage-validated three ways:
  cursor breach 82/82 probes caught, gate unbroken pin, answered_at drop),
  and since MOD-0.1 slice 9 `--features` (gate-open observable per module
  via answered_at, per-module not blanket, unknown names refused by name,
  an open gate moves no cursor and — since MOD-0.3c replaced the expired
  changes-no-verdict-text pin, exactly as its own comment predicted —
  PRODUCES where the closed gate refuses (both directions pinned: `node` +
  emptied diagnostic open, verbatim refusal closed), and a BASE-TIER
  `--features all`
  compile is byte-identical to a bare one — same output BASENAME in two
  directories, the emitted-#include lesson, which this case's first
  version paid a third time. Sabotage: gate ignoring the set is caught by
  the answered_at pin; check01's one-reference-from-the-scans-TU sabotage
  is the spec suite's own).
  Env: PCREC, CC, LIBA, LIBDIR, KEEP=1.
- **case 11 (MOD-0.7)** — `--explain`, the CROSS-SOURCE query surface, and the
  first case in this file written under a stated assertion rule. **case10's
  eight `--explain` content assertions were DELETED, not moved**: R10/C4-1
  demonstrated and MOD-0.7a re-measured (at 26b9660, both directions) that
  every one of them stays GREEN under a module-attribution swap between two
  rows, because `assert_contains` tests the whole output blob and the
  "all four rows" count is satisfied by any four rows. **THE RULE: no
  `assert_contains` against a whole `--explain` output.** Every assertion
  names a ROW (or `@header`) and a KEY through the `explain_field` awk helper,
  which parses the format's grammar — unindented `key<2+ spaces>value` header
  lines up to the first blank line, then row blocks headed by the row's
  `syntax` with `  key<2+ spaces>value` inside. The helper passes row/key
  through the ENVIRONMENT rather than `awk -v`, because `-v` processes escape
  sequences in its value and half these rows are named `\v`, `\d`, `\N{U+0041}`.
  63 assertions: D29's worked example `(?i-m:` end to end (it exited 1 before
  MOD-0.7); the six C4-1/C4-1b module pins that ARE the swap net; `\N{U+0041}`'s
  third bucket row as a candidate the prefix rule cannot see; the five query
  cells whose live answer legitimately differs from the row's declaration
  (`(?iZ)`, `(*NOTAVERB)`, `[[:foo:]]`, `[[:<:]]`, `\p{Foo}`), pinned as
  CORRECT so a later reader does not "fix" them; the verb name block; the gate
  axis (`--features classes` flips `\d` to `produces an AST node`, answered at
  `result`); and the `(?C1)` K14 pins, written first and recorded failing
  before the fix (the FIX-3 pattern — slice 4's commit carries the FAIL text).
  Floored sweeps: 19 queries answered, 81 row blocks, all agree, 79 elect
  their own row and 2 are the one RS_BASE row exempt by construction.
  **WHAT THIS CASE CANNOT REACH** (docs/design_notes_mod07.md §9.4, recorded
  here because the sweep-template lesson has recurred four times and this is
  the signpost): **the query set is HAND-LISTED** — the generated query space
  (every byte after each doorway opener, at depth) is not swept here, so a
  routing or selection bug affecting only a byte outside that list is
  invisible; the row set comes from `--list-syntax`, the same table `--explain`
  prints, so a DELETED row disappears from both (`check_required_rows`'
  hand-written manifest is what sees that); the attribution clause CANNOT
  dissent on a module-name swap, so the module PINS and not the `agree` field
  are the C4-1 net, and 94 of 100 rows have no module pin here by design;
  class-position answers are DECLARED (the `class` column), never live.
  Failing-direction validation is V1-V7, measured at landing and recorded in
  the phase-2 commit messages rather than as mech rows — a mech `cli` suite
  arm is a MOD-0.8 candidate (the code is trivial; the runtime budget is
  unmeasured, and this project does not assert a cost).

## Conventions

Case 8 is a BUDGET, not a functional check: a 9000-duplicate-branch alternation
compiled under `ulimit -s 512`. It exists because M2.8's trie recursed once per
branch and segfaulted at a 1 MB stack — a regression against hardening this
project had already done once (R3 critic F3). pcrec is a library and musl's
default thread stack is 128 KB, so "it works on the main thread" is not the bar.
Keep the limit low enough that the recursive form fails it.

`--list-verbs` (Q1/D25) is a SECOND dump rather than new columns on the first,
and the reason is `--list-syntax`'s consumers: SR-4 generates a section of
docs/pcre2_compliance.md from it, so widening it churns a document for a table
that has nothing to do with RegRows. Its own assertions are a floor plus named
rows from BOTH tables plus the four-field count — a bare count would be
satisfied by any fifty rows, and a dump of one table would silently lose the
case distinction that is the whole point of there being two.

Case 10's load-bearing assertion is the FIELD COUNT, not the content. SR-4 makes
tests/reject/ iterate `--list-syntax` and renders docs/pcre2_compliance.md from
it, so the TSV is an interface with consumers. The dump forbids tabs and
newlines inside a field rather than escaping them, and a `note` that acquired
one would hand every consumer a silently shifted column — nothing else in the
suite would notice. The other cases there are ordinary surface checks: a query
takes no pattern and no `-o`, an unknown flavour is an error rather than a
silently-unfiltered dump, and both flags appear in `--help`.

Note that case 8 SKIPS itself when python3 is absent (it uses python3 only to
build the 9000-branch pattern string). python3 is therefore not a hard
dependency of `make test`, but on a box without it this case silently stops
guarding anything — the skip goes to stderr and the suite still exits 0.

Maintenance: update this file when cases or covered surfaces change.
