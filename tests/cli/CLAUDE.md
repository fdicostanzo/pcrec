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
  Env: PCREC, CC, LIBA, LIBDIR, KEEP=1. EXECUTION of every emitted
  `--emit-main`/driver binary a case runs (a handful of runs per case, not
  an inner loop) goes through `gen_run` (`tests/lib/gen_timeout.sh`,
  `WATCHDOG_SECTION=cli`) — the shared run budget plus a 512m RSS ceiling
  and a `build/watchdog.log` line per run; the library-API smoke case's own
  binary stays unwrapped for the same compiler-axis reason its build is.
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
  88 assertions (63 at MOD-0.7, +25 at R20; read the number from a run —
  `grep -c '^PASS: case11'` — this file's own history with hand-copied counts
  is in the paragraph below): D29's worked example `(?i-m:` end to end (it exited 1 before
  MOD-0.7); the six C4-1/C4-1b module pins that ARE the swap net; `\N{U+0041}`'s
  third bucket row as a candidate the prefix rule cannot see; the five query
  cells whose live answer legitimately differs from the row's declaration
  (`(?iZ)`, `(*NOTAVERB)`, `[[:foo:]]`, `[[:<:]]`, `\p{Foo}`), pinned as
  CORRECT so a later reader does not "fix" them; the verb name block; the gate
  axis (`--features classes` flips `\d` to `produces an AST node`, answered at
  `result`); and the `(?C1)` K14 pins, written first and recorded failing
  before the fix (the FIX-3 pattern — slice 4's commit carries the FAIL text).
  Floored sweeps: 19 queries answered, 81 row blocks, all agree, 79 elect
  their own row and **exactly 2** are the one RS_BASE row exempt.
  **R20 added five groups of pins and rewrote one** (findings in
  `docs/dev/reviews/2026-08-12-r20-mod08.md`):
  the CLAUSE SCOPE (`(?J)`/`(?m)` under `--features modifiers` agree and exit
  0, where they dissented on attribution about a tree tests/reject:664 pins as
  correct — with the per-LETTER module still SHOWN, which is the pin that stops
  the fix being "make the two sides agree by dropping the interesting one";
  **`(?J)`'s per-letter module became `backrefs` at [M6.5.2], 2026-08-22 — the
  FOURTH wording that letter has carried, and case11's assertion moved with
  it. The pin's POINT is unchanged and is why it survived four moves: the
  displayed answer must keep naming the letter's own module rather than the
  dispatching row's**);
  the NULL CONTRACT (`(?` at end of pattern elects `none` and the catch-all is
  tagged `listed` rather than `fallback`; the `[[:alpha]` delimiter-scan
  decline elects `none` too); `rows 0` (the branch the design note called
  "impossible today" while 87 of 127 `\<byte>` queries display it — it had
  ZERO assertions); CONTROL-BYTE ESCAPING (a query containing a newline used
  to inject a synthetic header line that `explain_field` read as real,
  reporting `rows 99`); and `\d`'s open-gate cell, whose STRING changed
  because what it asserts did — see its annotation in the case.
  **The rewritten one is the election sweep** (MOD07-7): its first conjunct
  was `selfel == blocks - exempt`, a TAUTOLOGY — the loop increments exactly
  one of the two per block — sitting beside an unexplained `exempt <= 3`.
  Self-election was never actually unasserted (the agreement sweep's clause 1
  dissents on it, and that sweep requires every block to agree); what was
  unchecked was the size of the EXCEPTION set, so `exempt` is now pinned at
  exactly 2, with the reason written down: one RS_BASE row, appearing in two
  of the 19 queries.
  **WHAT THIS CASE CANNOT REACH** (docs/design/design_notes_mod07.md §9.4, recorded
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
  the phase-2 commit messages rather than as mech rows. **The mech `cli` arm
  exists since MOD-0.8c slice 1** and the cost it was waiting on is measured:
  5.46s per sabotage tree, against the `reject` arm's 54.75s. Whether V1-V7
  become mech rows is still open and is a manager decision; the arm's first
  user is `S18-tsv-empty`, whose net is case10.
- **case 12 (R20/MOD07-1)** — A PRODUCING PORT THAT FAILS, on both query
  surfaces. The tier-1 the R20 panel found: `--explain` and `--probe-ask`
  each hand a doorway a `Ctx` they `memset` and never `setjmp`, which was
  safe only while no port could `ctx_fail`. The first result-producing port
  ended that at MOD-0.3c/0.5c, two milestones before MOD-0.7 extracted
  `doorway_call` and carried its own "the first producing port must revisit
  here" comment along unexamined — so `--features modifiers --explain
  '(?i:['` SIGSEGVed (139), as did `--features all --probe-ask result --
  '(?i:['`. **What is pinned is the SHAPE, not the wording** (D26 tier 3):
  nonzero AND below 128, because bash reports 128+N for a signal and that
  bound is the whole difference between diagnosed and died — plus a
  non-empty stderr naming the port's own error rather than `--probe-ask`'s
  usage sentence (a NEGATIVE pin: reusing the misuse text would tell an
  operator to fix a command line that is fine). **Both gate states are in
  the case because the gate is the axis**: closed, the same text stays an
  ordinary exit-0 refusal; open, a WELL-FORMED body must still PRODUCE —
  that last one is the positive control, since a guard that swallowed every
  open-gate answer would satisfy the two crash pins on its own. Written
  first and watched crashing; the verbatim FAIL block is in the slice's
  commit message, and the sweep behind it (10 query templates × ASCII bytes
  × both gate states × both surfaces = 5,080 probes) went 18 crashes → 0.

- **case 13 (MOD-0.8c slice 3)** — THE ENCODING GATE (`-e`), which nothing in
  this repository covered before: `grep -rn '\-e utf8' tests/` found nothing,
  so the CLI's only gate besides `--features` was entirely unpinned. It landed
  with the fix for K14's shape ON that gate (R20, the D27 writer's divergence
  5): `-e utf8` answered "requires module 'utf8'" and the module namespace has
  no `utf8` — `--features utf8` says "unknown module" itself, so the
  diagnostic's one actionable noun pointed at a dead end. The fix promises the
  MILESTONE instead of a module, because M5 delivers byte-wise UTF-8 automata
  and OS-2 commits ASCII and UTF-8 to ONE DFA emitter: UTF-8 is an engine axis,
  not a drop-in construct, so registering a name would have meant inventing a
  module with no construct to describe. **What is pinned is not the sentence**
  (D26 tiers that out): a NEGATIVE pin that no module is named, a positive one
  that the milestone is, that a refused encoding writes no C, and the
  CROSS-CHECK that makes it stick — `--features` must still reject `utf8` by
  name, so if M5 ever registers it, this flips and the pin is revisited rather
  than quietly deleted. Written failing-first against the pre-fix binary; the
  verbatim FAIL block is in the slice's commit message.

  **[M5-SEAM] (D58, 2026-08-18) extends case13 rather than adding a case:
  this IS the encoding case.** New assertions, in the order they matter:
  `byte` is the encoding's name in BOTH spellings (`-e byte`,
  `--encoding=byte`); the DEFAULT artifact is BYTE-IDENTICAL to the
  explicitly `-e byte` one (compared through `-o -`, the self-contained
  idiom case9/case10 established for exactly this — two artifacts written
  to different basenames differ in their emitted `#include` line), which
  says the default and the explicit request are the SAME request rather
  than two that happen to work; the artifact stamps `.encoding = 0`
  (`PCREC_ENC_BYTE`) about itself; `-e ascii` is now an UNKNOWN encoding
  (D58 renamed it; one namespace member, one spelling, [SR-10]) and its
  refusal offers the menu the registry actually holds; `--encoding=utf8`
  refuses identically to `-e utf8`, so the two spellings cannot drift into
  two answers. Plus one property that is not about the CLI at all and has
  nowhere better to live: two SEPARATELY-COMPILED artifacts, each carrying
  its own residual block, are compiled and LINKED into one TU and run —
  the concrete form of D58's "mixed encodings in one compilation unit are
  supported by construction", checkable today with one encoding because
  what it really asserts is that nothing about the residual embed is file-
  or process-scoped.

- **case 14 ([STD1] phase A, D37, 2026-08-13)** — the frozen named set
  `std1` = {classes, modifiers}, artifact stamping, and the bare-default
  mapping point, WITHOUT the bare default itself flipping (that is a
  separate later commit carrying the full suite re-baseline). Since
  `classes`/`modifiers` both carry real producers (MOD-0.3c/MOD-0.5c),
  `--features std1` genuinely changes what a pattern compiles to, not just
  answered_at — pinned with an oracle-verified match cell (`(?i)cat\d+`
  against python3 `re`, two subjects) that exercises BOTH modules'
  producers in one pattern. Also: the bare default still refuses `\d`
  (phase A's hard invariant) while `--features std1` accepts it, which is
  simultaneously the "explicit wins over the bare default" proof (a
  secretly-flipped default would make the bare case succeed too);
  `--features std1` is byte-identical to `--features classes,modifiers`
  except the stamp's own SET NAME (compared via `-o -`, avoiding the
  #include-basename trap case9/case10 already document); an unknown
  named-set-shaped spec (`std2`) is refused BY NAME and writes no C; the
  stamp comment + `PCREC_FEATURE_SET`/`PCREC_FEATURE_MODULES` macros are
  present and correct for a bare invocation ("none"), `--features std1`,
  and `--features all`; and the paired `.h` carries the comment but not the
  macros (so a `.c` that includes its own `.h` never redefines them).
  **case10's pre-existing `--features all` byte-identity pin was ALSO
  updated** (not by this case, in case10 itself): it now compares past the
  4-line stamp block rather than the whole file, since the stamp
  legitimately differs by design — the fix is what makes the stamp
  trustworthy as a reproduction recipe, not a hole in the old pin, which
  still asserts what it always meant to (the MATCHER is gate-inert for a
  base-tier pattern).

  **[STD1b] (D37, 2026-08-13) re-baseline: phase A's "not flipped" premise
  is gone.** case14 was rewritten rather than just re-pointed: the bare
  default now IS std1, so the case's job flips from "bare refuses, std1
  accepts, explicit wins" to "bare == std1 byte-for-byte, including the
  stamp itself (not merely equivalent modulo the set name, the way the
  pre-existing std1-vs-`classes,modifiers` comparison still is), and the
  PRE-flip bare behaviour survives verbatim as `--features none`" — proven
  with a `diff -q` on `-o -` output for `\d`, the same trap-avoidance idiom
  the std1-vs-explicit comparison already used. The artifact-stamping
  assertions flip the same way: a bare invocation now stamps `std1
  (modules: classes,modifiers)` (D37's whole point — the stamp reports the
  REQUESTED set honestly, and the request itself changed), and
  `--features none` is what now stamps `none`. **Three OTHER cases needed
  fixes too**, all bare invocations elsewhere in this file that assumed the
  old empty default and are not case14's to fix: case10's `--probe-ask
  result` closed-gate demonstration (twice: the verdict-demotion cell and
  the "closed gate keeps the refusal verbatim" cell) and its `--features
  all` byte-identity pin's `fa` generation (used to rely on bare to get the
  "none" stamp); case11's D29 worked example (`--explain '(?i-m:'` bare
  used to stop at "requires module 'modifiers'" — now it reaches the
  module's own malformed-run parse and answers something else entirely,
  which is a genuinely different worked example, not this one); case12's
  "the CLOSED gate: the same text, an ordinary answer" section (bare now
  reaches the SAME crashing-port path the case's two `--features
  modifiers`/`all` cells above it already exercise, making the section
  redundant with itself rather than testing the closed-gate case it names).
  All four got `--features none` added to keep testing exactly what they
  tested before; none needed a new bare-positive pin of their own, because
  case14's byte-identity proof already covers "bare behaves like std1"
  more strongly than any single field would.

- **case 15 (K21 fix, 2026-08-15)** — the third leg of `--emit-main`'s
  contract, which case2 could not reach: `<prefix>_search`'s return is
  THREE-valued (match/no-match/give-up), and the pre-fix `main()` tested it
  as a boolean, so C truthiness took the match branch on a negative
  give-up sentinel and printed `caps` the give-up path never wrote —
  uninitialized stack reported as a confident match
  (docs/dev/known_issues.md K21). Driven the same way
  `tests/vm/run_vm_tests.sh` §4/§4.5 drive the two bounds to their own
  limit — a tiny `--step-budget`/`--backtrack-frames` on a shape that
  burns it in a handful of resumptions — rather than the R23 fuzzer's
  witness pattern, which is a much less reliable repro to pin a test to.
  Two witnesses (`(a*)*b` under `--step-budget=50`, `((a)|b)*c` under
  `--backtrack-frames=4`), each asserting the exact give-up stdout line
  (`steps`/`frames`) and the distinct exit code (3, colliding with
  neither match=0, nomatch=1, nor this same `main()`'s own usage-error=2),
  PLUS the non-firing controls — the same two patterns under an ample
  budget/capacity still print an honest `match START END` — so a give-up
  path that fired unconditionally could not pass silently. Verified
  failing against the pre-fix emitter first (4 of 10 assertions fail,
  exactly the give-up-path ones).

- **case 16 ([M4.7c], K9's API half)** — the K9 embedded-NUL repro itself
  (docs/dev/known_issues.md K9), the one surface in this file that has to be a
  direct library-API C probe rather than a CLI or `.rxt` case: `pcrec_compile()`
  takes a NUL-terminated pattern with no length, so a pattern containing a NUL
  is silently truncated and the compile reports SUCCESS for a shorter pattern
  than the caller passed — and a NUL cannot survive argv or a line-based
  corpus to reach pcrec at all. Built on case7's shape (own small C file,
  compiled against `pcrec.h` + `libpcrec.a`, run and checked, no `gen_run`
  wrapper — same compiler-axis reasoning). The probe builds `"a\0b"` (3
  bytes) byte by byte, compiles it, and asserts two things: the compile still
  reports success for the 1-byte pattern `pcrec_compile()` can actually see
  (K9's own claim, PINNED — this case does not fix it, that is DD-3's job),
  and the emitted `rx_info.pattern_len` now reads `1`, honestly — the new
  detectability a caller gets from this field, which is the whole point of
  [M4.7c]. The general "pattern_len is the source byte count" structural
  coverage (an ordinary pattern, and a pattern whose source spelling is
  longer than what the matcher actually walks, e.g. `a\nb`) lives in
  tests/codegen/run_codegen_tests.sh instead, since those cells only need the
  emitted C text, not a library-API probe.

- **case 17 (K38 fix)** — the SPEC-FIRST witness case3 could not be: case3's
  60-char-prefix cell proves the prefix is ACCEPTED and its artifact
  COMPILES, but only for the pattern `'a'`, which never reaches the family
  of fixed buffers in `src/gen/emit_vm.c` that build an emitted name or
  sub-expression from the prefix PLUS a suffix (a lookaround slot
  expression, a span-cursor test, the reverse-deterministic rung's
  group-span/group-seen names). Before the fix `snprintf` truncated those
  silently and gcc failed on the 60-char artifact with undeclared
  identifiers and `expected ']'` — every corpus artifact was blind to it,
  since they all use the 2-char `"rx"` prefix. Two witness patterns, chosen
  to reach the whole confirmed buffer family (see `src/core/limits.h`'s
  `PCREC_MAX_EMIT_NAME_LEN` comment for the derivation) in ONE compile
  each: a VM pattern (`(?<=abc)(?=def)(a)(?:b)*+\1(?:(cd)){0,50}(?:(x)|y){0,10}`
  — lookbehind AND lookahead slot expressions, a possessive quantifier
  feeding a backreference, a capturing bounded span loop, a captured
  alternation under a bounded repeat) and a DFA pattern (an email-shaped
  class/quantifier pattern with no captures, exercising `emit_dfa.c`'s one
  prefix-carrying buffer, the encoding residual's `<prefix>_next_pos`).
  Both run at the 60-char maximum AND at a 1-char prefix, on
  `--engine=vm`/`--engine=dfa` respectively (four cells total), through
  `pcrec_run`/`gen_cc` like every other generated-code case in this file.
  **Verified DETECTING**: run against a binary built before the K38 fix,
  the `prefix len 60, engine=vm` cell goes red with exactly the truncated-
  identifier errors K38 describes, while the DFA and 1-char-prefix cells
  stay green — the fix's binary passes all four. See
  docs/dev/known_issues.md K38 for the full mechanism and the buffer list.

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

**[SR-11] (2026-08-21): case10's field-count pin is now the contract's own
HEADER TRUTHFULNESS check.** `table_check_truthfulness` (tests/lib/table.sh)
replaces the `NF != 16` literal: every data row's field count is compared
against the HEADER's own declared count, never a hardcoded number, so the
next appended column changes nothing here — this is the "correct final
form of case10" docs/spec/table_contract.md names it as. Sabotage-validated
against a real `pcrec` wrapper that injects an extra tab into one data row:
the assertion fails naming the exact count mismatch, not a silent pass.

Case 10's load-bearing assertion is the FIELD COUNT, not the content. SR-4 makes
tests/reject/ iterate `--list-syntax` and renders docs/pcre2_compliance.md from
it, so the TSV is an interface with consumers. The dump forbids tabs and
newlines inside a field rather than escaping them, and a `note` that acquired
one would hand every consumer a silently shifted column — nothing else in the
suite would notice. The other cases there are ordinary surface checks: a query
takes no pattern and no `-o`, an unknown flavour is an error rather than a
silently-unfiltered dump, and both flags appear in `--help`.

**The field count itself is now 16, not 15** (D65, 2026-08-21 —
docs/design/registry_built_status_memo.md's `built` column, appended as the
16th field per SR-4's own "columns are APPENDED, never reordered" rule).
Case10's own `NF != 15` pin did not update in the same change and broke the
moment the column landed — it is a FORMAT consumer (asserts the dump's exact
SHAPE) that a survey scoped to CONTENT consumers (who reads which field's
VALUE) missed; fixed to `NF != 16` by the tail lane that found it via the
merge battery. See the memo's own "Correction" section for the full
consumer survey and tests/reject/CLAUDE.md's matching entry — that
directory's row iterator carried the identical hard-coded `15` and broke
the same way.

Note that case 8 SKIPS itself when python3 is absent (it uses python3 only to
build the 9000-branch pattern string). python3 is therefore not a hard
dependency of `make test`, but on a box without it this case silently stops
guarding anything — the skip goes to stderr and the suite still exits 0.

Maintenance: update this file when cases or covered surfaces change.
