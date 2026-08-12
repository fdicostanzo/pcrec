# tests/cli — CLI surface and library-API tests

Covers what the .rxt corpus cannot: argument parsing, output-file behavior,
error text and exit codes, and library-level properties such as stack usage.
Part of `make test` since M2.

## Files

- **run_cli_tests.sh** — nine cases: (1) `-o -` self-contained C that compiles
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
