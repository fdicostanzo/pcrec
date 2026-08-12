# tests/registry — the syntax construct registry, checked against the parser

Guards the SR-1 table in `src/parse/registry.c` (design: docs/decisions.md
D24). The table describes every non-base PCRE construct declaratively; this
directory asserts that the description and the shipped parser actually agree.

## Files

- **registry_check.c** — links `build/libpcrec.a` and includes
  `src/core/internal.h`, so it compares the table with the parser inside one
  process rather than re-deriving either from CLI output
- **pcre2_check.c** — the same table against **libpcre2** (PC-3): the first
  check in this project that is not pcrec reading pcrec. Same link, plus a
  runtime `dlopen` through `../fuzz/pcre2_abi.h`. SKIPS LOUDLY and exits 0 when
  libpcre2-8-0 is absent, so a stranger's clone stays green. See its own
  section below
- **run_registry_tests.sh** — builds and runs both, plus compliance_section.py
  and PC-4; part of `make test`. Env: CC, KEEP=1
- **run_pc4.sh / pc4_check.c / pc4_driver.c / pc4_subjects.h** — PC-4
  (MOD-0.3e), the SEMANTIC differential R8/C4-2 asked for and PC-3
  deliberately is not: what a PRODUCED construct MATCHES, cell by cell,
  against the live oracle. 273 deterministic patterns (11 esc + 28 posix
  spellings × 6 shapes, + 39 caseless bare forms — the first time `-i` has
  met an external oracle in this repository) × 271 shared subjects (every
  single byte + curated multis, ONE header embedded by both sides so the
  probed set cannot drift). Populations are EXACT predictions stated in
  pc4_check.c before the first run and confirmed on it: 232 both-accepted,
  41 refusal agreements (both directions checked — over-acceptance and
  over-rejection each fail naming the cell), 62,872 match cells, mlimit
  asserted zero on a backtrack-free space. The pcrec side runs one process
  per PATTERN (all subjects in-process), whole sweep ~2.5 s. Skips loudly
  without libpcre2, probed BEFORE the gcc sweep is paid for; the runner
  carries a population-line needle so an unwired PC-4 fails rather than
  vanishes. LIVENESS proven in both axes before the zero was trusted: a
  one-bit bitmap sabotage fires per-pattern naming subject 0x35, and a
  dropped `-i` fold fires exactly the caseless posix cells — and the FIRST
  bitmap sabotage run returned zero failures because hand-maintained
  Makefile header deps did not include cls_bits.inc, so the sabotage never
  entered the binary (fixed in the same change; the lesson is the fuzz
  battery's one level down: prove the sabotage reached the binary before
  reading its zero)

## What it asserts

0. **Two invariants the class-bracket DOORWAY depends on and cannot assert
   itself** (R9). Both were true by accident before this, and each has a
   sabotage below. No `RK_CLASSBRACKET` row may use `]` as its selector — the
   doorway's scan treats "an unescaped `]` ends the class" and "delimiter + `]`
   closes the pair" as disjoint tests, which holds only while no delimiter is
   `]`; a critic proved the order of those two tests is otherwise arbitrary by
   swapping them for byte-identical results over 1.24M patterns. And every
   `RF_CLASS_NAMED` row must also carry `RF_CLASS_DELIM`, because the name is
   the text between the delimiters and the flag that says "this text is a name"
   has to be on the row whose extent the scan measures. Without the pairing the
   length computation underflows; it was memory-safe only because
   `pcrec_registry_posix_known` compares lengths before bytes, which is an
   implementation detail of a different function that nothing tied to this one.
   **The general rule R9 drew from both: when a dangerous operation is safe
   because of a fact that lives elsewhere, the assertion belongs where the fact
   is, not where the danger is.**
1. **Well-formedness** — no two rows claim one byte, catch-all rows come last,
   each row's `syntax` example really contains its selector byte, and the
   status/module/feature/engines/diagnostic fields are mutually consistent.
   Plus an EXACT row count (100 since Q2/SR-9; this file said 68 until
   2026-08-11, which is the drift an exact count is supposed to prevent
   happening to its own documentation) so rows cannot be deleted silently — the
   same "TABLE SHRANK" guard tests/reject/ carries. Note what R8/C4-10 measured
   about all three of these exact-count tripwires: each prints its own remedy,
   so following their instructions verbatim is how a row with a WRONG MODULE
   gets past the whole suite. They make a change VISIBLE in the diff; they do
   not make a wrong one fail. Only the hand-written rows in tests/reject/ do
   that, and only for rows someone wrote one for.
2. **table → parser** — every row's `syntax` is compiled for real, and the
   diagnostic must match the row EXACTLY. Substring matching would let a row
   name the wrong module and still pass.
3. **parser → table** — a 255-byte sweep of **all four** doorways. If the
   parser says "requires module" for a byte, a row must exist and name the same
   module; if a row claims a byte needs a module, the parser must really route
   it there; and a row whose diagnostic is fixed text (the collating rows) must
   match that text exactly. **This is the direction that catches a construct
   added to parse.c with no row** — the drift that produced the `\v` bug.
   Direction 2 alone is blind to it.
   *R4 correction:* the first version swept only two of the four doorways while
   this file already claimed all of them, and validated 1 of 3 class-bracket
   rows because fixed-text rejections carry no "requires module" marker.
   *Q1 correction (2026-08-10):* the `(*` doorway has its own `sweep_verb()`
   now, and the reason is a measured near-miss. The generic sweep asks "did the
   parser say *requires module*"; before Q1 all 255 bytes after `(*` said
   exactly that, so it exercised 255. Q1 made most of them say "not recognized"
   — correctly — and the generic sweep dropped from **255 bytes asserted to
   ONE** while still printing `PASS: sweep ... all 255 bytes agree`. A check
   that narrows to nothing without failing is this directory's own warning, one
   level down. `sweep_verb()` asserts instead that every byte REACHES the
   doorway, that its answer is one the registry can account for, and that
   PCRE2's two name tables are selected by CASE and nothing else — with
   liveness counters, because "one answer for everything" is exactly what the
   old sweep was reduced to.
4. **feature/module bijection** — a row carrying `FEAT_CLASSES` while printing
   "assertions" passed everything until a critic tried it. `registry.c`'s
   `M_<module>` macros now emit the pair together so a macro-built row cannot
   mismatch, but a LONGHAND row still can, and "correct by construction" is the
   kind of claim this project keeps losing when nothing tests it. Checked
   without an external module list (which would be a second home): across the
   table, mask and name must be a bijection, so one mismatched row necessarily
   collides with both the rows using its mask and those using its name.
5. **required rows** — a small hand-written manifest of constructs whose
   ABSENCE would silently regress a specific past incident (both collating
   rows, `\v`, `\b`, `(?:`, the two catch-alls). Everything above iterates the
   rows that exist and is therefore structurally blind to deletion: a critic
   removed both collating rows and all 116 checks stayed green. A coverage
   floor cannot fix this — it answers "did someone delete a lot", never "did
   someone delete the right ones".
6. **the MOD-0.2 arbitration** (2026-08-11) — row selection is recogniser +
   rank since MOD-0.2, and two checks own the migrated rules.
   `check_row_ranks`: every tailed row (18, a measured count with the
   R8/C4-10 caveat printed beside it) must sit above the fallback tier, or
   its construct is unreachable — the successor of the retired
   `check_tail_precedence`'s tailed-beats-fallback half. `check_arbitration_
   liveness`: per multi-row bucket, a FLOORED count of generated probes where
   more than one recogniser answers (10/15/15/50, predicted from the
   generator before the first run and confirmed exactly), plus the esc-`N`
   triple-answer assertion — the pair `\N{`/`\N{U+` is the only place the
   ordering between two TAILED ranks is observable, so its disappearance
   must fail loudly rather than leave rank untested (the retired check's
   liveness clause, re-homed; R11/M3's counter, D32 §9's retirement
   precondition). The D32 §9.5 migration scaffold (new engine vs the retired
   longest-tail-wins engine, 261,193 probes, 0 mismatches, 0 ambiguous) was
   deleted WITH the retired engine in one commit — an equivalence check
   cannot outlive its oracle honestly. The ambiguity defect path (two
   answers at the winning rank → "internal error: ambiguous registry
   arbitration...") was validated live: an equal-rank sabotage on the `\N`
   pair fires it with a clean exit 1 and 2 registry failures naming the row.
   R15 hardened all of this the same session: the liveness check now ends
   with the **no-ambiguity sweep** (every kind × sel × generated text,
   261,193 probes, zero winning-rank ties — the scaffold's deletion had
   left the `ambiguous` flag probed by nothing; equal-rank sabotage fails
   it directly), check_row_ranks also asserts **tails exist only at the
   escape and group doorways** (the other two ask the tail-less question
   and discard ambiguity — scans.c's prose assumption, now an assertion),
   the answer predicate is the engine's own exported
   `pcrec_registry_row_answers` (no duplicate to drift), and
   run_registry_tests.sh carries a **count (167 since MOD-0.3b; 166 at R15)
   + manifest guard for registry_check itself**, mirroring PC-3's, with one
   NEGATIVE needle: the retired check's PASS line must not reappear. NOTE the division of
   labour R15's checks critic initially misread: these checks do NOT ask
   which row WINS — `check_table_to_parser` owns that (D32 §9.1's primary
   instrument), and a rank-value winner-swap sabotage fails it twice inside
   `make test`, measured.

7. **the MOD-0.3b port data** (2026-08-12) — `check_class_ports`, the
   unwired ports' only guard until the classes producers land. Populations
   PREDICTED before the first run and pinned (exactly 5 scalar class ports —
   `\b \g \k \8 \9` — 0 SET, 0 FN, 0 atom ports; slices 2-3 move them
   deliberately, in the same change as the producer). Values are
   oracle-tied, one rule per syntax shape: a bare-escape row's scalar must
   equal its libpcre2-fed `class_expect` byte (the port is never its own
   authority), a body-carrying row's must equal its selector letter (§14.3's
   literal-fallback law, FIX-3-measured). Sabotage-validated in three
   directions same-session: value drift on `\b` (0x08→0x09) fails the
   column tie, a zeroed `\k` scalar fails the fallback law, and deleting
   the call fires the count guard AND the manifest line.

The probe patterns come from each row's own `syntax` field, so a new row covers
itself with no edit here. That is sound because this is a conformance check
between two descriptions, not a control: it asserts the two agree, never that
the rejection is CORRECT. Correctness is tests/reject/'s job, and its
accept-controls stay hand-written for precisely the reason this file does not
need to be (SR-4, and the trie-identity lesson about controls sharing a source
with the thing they control).

**Know what that boundary costs you.** This file cannot distinguish "both
descriptions right" from "both wrong the same way" — the likelier human error,
since one person maintaining two files from one misunderstanding gets both wrong
identically. A critic confirmed it: the same wrong module name written into BOTH
parse.c and registry.c passed 116/116 here (the check count at the time of that
measurement; it is 127 now — the RESULT is what matters, not the total). It was
caught by tests/reject/, whose hand-written expectations are literals — 144 of
them as of R7, when this sentence last said 93 — so tests/reject/ is not
decoration, it is the control this file deliberately is not. Two things narrow
the gap further: `registry.c`'s `M_<module>` macros make an invented module name
a compile error, and they pair each feature bit with its diagnostic name so a
macro-built row cannot mismatch (a longhand one still can — hence the bijection
check above). **Residual risk, open:** a NEW construct given the same
wrong module in both files, with no tests/reject/ row added, is caught by
nothing.

## Sabotage validation

The check was validated by eight edits to `src/parse/registry.c`, each reverted
after measuring; every one was caught. The last three exist because a critic
proved the first five could all pass while the table lost rows or mismatched a
module:

| sabotage edit | failures |
|---|---|
| `\v` row's module `"classes"` → `"assertions"` | 4 |
| delete the `\K` row entirely | 2 (both sweeps) |
| add a row for `\n`, a BASE escape the parser compiles | 4 |
| reword the collating message to "are unsupported" | 2 |
| drop `RF_CLASS_BASE` from the `\b` row | 2 |
| delete BOTH collating rows (R4 F2 — was **invisible** before the manifest) | 2 |
| delete the `(?:` base row | 1 |
| `\b` row longhand with `FEAT_CLASSES` but module `"assertions"` (R4 E1) | many |
| `RF_CLASS_DELIM \| RF_CLASS_NAMED` → `RF_CLASS_NAMED` (R9/C3-1) | 3 (+23 in PC-3) |
| add a `]`-selector `RK_CLASSBRACKET` row (R9/C2-1) | 2 (+1 in PC-3) |

## pcre2_check.c — the external check (PC-3)

Everything else in this directory, and in tests/reject/, is **pcrec checking
pcrec**. That is not a criticism of those checks; it is their measured limit,
recorded three separate times (R4, R5, R6): a row that is plausibly WRONG in the
single home is invisible, because the wrongness is what both sides read.

`pcre2_check.c` asks libpcre2 instead. Three parts:

1. **Every row's claim.** An `RS_MODULE` row says "PCRE2 HAS this and pcrec has
   not implemented it", so libpcre2 must COMPILE the probe — a row naming a
   construct PCRE2 does not have fails there. An `RS_REJECTED` row says
   "agreement IS compliance", so libpcre2 must REJECT it *and pcrec's message
   must be PCRE2's message*, not merely some rejection. **Mind the polarity:**
   docs/plan.md had check (b) backwards until R6, and as written it would have
   passed every fabricated row it exists to catch.
2. **22 context wrappers.** A row's `syntax` reaches pcrec's DOORWAY, which is a
   weaker contract than "libpcre2 will compile this": `\3` needs three groups,
   `(?1)` needs one, `\k<name>` needs the name declared. Two guards keep the
   wrappers from becoming a way to paper over a bad row — a wrapper must CONTAIN
   the row's `syntax` verbatim, and a wrapper that is not NECESSARY is an error.
   A row with no wrapper whose syntax will not compile is a FAILURE, never a
   skip.
3. **Two more generated differentials at the CLASS-BRACKET doorway** (FIX-2):
   1680 patterns over delimiters x bodies x shapes x trailers, asserting no
   over-acceptance and no over-rejection; and ~150k POSIX class NAME probes from
   the same libpcre2-derived pool, asserting that a name libpcre2 has is
   deferred to a module and a name it lacks is not. The first found 126
   divergences on its first run where the plan had five hand-pinned cases; the
   second found two constructs a hand-written name list had missed (`[[:<:]]`
   and `[[:>:]]`) and refuted two successive wrong versions of K4's escape rule.

   **R9 found the first of those two probing less than it printed.** The shape
   written to exercise K4's nested-opener rule, `[[%ca[%cb%c]%c]]`, takes four
   `%c` and no `%s` while the call site passed the body string as its second
   argument — so a `const char *` was read as an `int`. Undefined behaviour;
   in practice the low byte of a literal's address, and at `-O0` sometimes NUL,
   truncating 21 probes to the stub `[[=a[`. Which patterns the sweep probed
   depended on `.rodata` layout while the header kept printing 1680, and
   `-Wall -Wextra` cannot see a non-literal format so `make strict` was clean.
   Net effect: 42 same-delimiter nested openers in the whole sweep, all at `:`,
   **zero at `.` and `=`** — the two rows for which rule 2 is the offset-only
   branch. Replaced with `cls_expand`, a positional expander with no argument
   list to fall out of step with; the sweep now generates 98/56/56 and still
   reports zero divergences, so the RULE was right and only the instrument was
   wrong.

   The guard is a **per-delimiter nested-opener floor**, and it is per-construct
   on purpose: "did the sweep reach a module" and "did both verdict buckets
   fill" were both green while one whole construct went ungenerated. Note what
   its own first version did — it counted ONE `[`+delimiter, which makes the
   ordinary inner bracket `[x[=a=]]` look like a nested opener, so it read
   511/504/504 and passed the sabotage. Two occurrences is the definition: the
   pair being scanned, plus the one that wins.

   **And it counts SIX buckets, delimiter x position, for a reason worth not
   re-learning.** Rule 2 has two positions, and when the 4a shapes were added
   (R9/C2-3, below) the per-delimiter floor stopped being able to detect the
   loss of the 4b shape: the 4a openers kept the counts non-zero, so the guard
   written for R9/C1-1 passed the very sabotage it was written for. Extending a
   check disarmed it. Each shape's removal now fires independently — verify that
   with a positive control if you ever add a seventh shape.

   R9/C2-3 is why the 4a shapes exist at all: turning rule 2 off at the class's
   own bracket for `.` and `=` only produces 1,416 over-rejections against
   libpcre2 — reduction `[.[.]`, five bytes, which libpcre2 compiles as a class
   of `.` and `[` — and the whole repository stayed green, including the
   nested-opener floor, because every nested opener generated was a 4b one.

   The differential also reads pcrec's MESSAGE in the both-refuse half now
   (R9/C1-8). It used to count `pc2 != 0 && rejected` as agreement without
   looking, which is 746 of the patterns and precisely where "is a module
   promised?" lives — so doorway 4a had no external check of its own
   over-promise. Distinguishing a real one from an honest one is mechanical
   rather than a hand-listed exemption: append the class's `]` and ask libpcre2
   again. `[[:alpha:]` then compiles, so pcrec deferring there is honest;
   `[:alpha:]]` still does not, so the 4a over-promise is caught.
4. **The verb NAME differential**, and this is the part that scales. Candidate
   names are generated from **libpcre2's own shared object** — its compiled-in
   name tables, read via `dlinfo`, expanded to every prefix and suffix — plus
   single-character mutations of the names pcrec claims, plus all 255 bytes,
   plus LENGTHS straddling the 126-130 boundary. ~75,000 candidates in 13
   forms, ~973,700 probes, about 3 seconds. libpcre2's verdict on each decides
   what pcrec owes.

   **`pool_from_lengths`'s alphabet is not just `A`/`a` any more** (K15,
   2026-08-12, docs/known_issues.md): the same 126-130 lengths are also
   generated from three non-identifier filler bytes (space, `*`, 0x80), so
   the "long AND non-identifier" cell — invisible to identifier-only
   lengths — is finally reachable. It diverges from libpcre2: pcrec's extent
   scan hits the 128-code-unit cap before comparing the run to a table
   entry ("too long"), libpcre2's scan stops at the first non-alnum/`_`
   byte and answers "not recognized" about the short prefix. Ruled an
   acceptable tier-2 divergence under D26 (Frank, 2026-08-12) and given
   **this file's one exclusion**, `k15_excluded()`, scoped to exactly that
   cell — everything else in this differential, including the same
   non-identifier fillers UNDER the cap and identifier runs OVER it, is
   still compared with no exclusion and still agrees. See
   docs/known_issues.md K15 and docs/pcre2_compliance.md's Backtracking
   control verbs section.

The prefix/suffix expansion is not decoration: `ANYCRLF`, `CRLF` and `LF` are
real PCRE2 option names that appear in the binary only INSIDE `BSR_ANYCRLF`, so
a pool of whole runs would have missed three names this check exists to notice.

5. **The DELIMITER byte sweep and the NAME x POSITION cross-product**, both
   added at R9 and both closing a hole the panel demonstrated with a live
   sabotage. `CLS_DELIMS` is `":.="`, hand-listed from pcrec's rows, so before
   R9 the only externally-oracled instrument at this doorway never left three
   bytes; a critic added a `!` construct with no registry row and every suite in
   the repo stayed green. The byte sweep runs 255 bytes x 5 shapes against
   libpcre2, and its liveness assertion is worth copying: it does not ask the
   table how many delimiters there are, it asks how many BYTES behave
   differently from an ordinary class member. That is a question only the parser
   can answer, so it can see a construct the registry does not know about.
   Expect `:` `.` `=` and `\` — the last is the class escape, kept in rather
   than special-cased out.
   The position sweep exists because two large honest differentials left a hole
   between them: the name sweep fixes position at `[[:NAME:]]`, the shape sweep
   never uses `<`/`>` as a body, and `<`/`>` are the two names libpcre2 accepts
   ONLY as a class's entire content. **Ask what your axes are and whether
   anything varies two of them together** — making either sweep bigger would
   never have found it.

## Coverage guard and manifest (R9/C1-7)

`run_registry_tests.sh` now asserts PC-3's exact passing-check count AND a
manifest of checks named by the finding each one closes. Until R9 this
directory had neither, while `tests/reject/` has carried both since R7 — and
this is the directory holding the expensive external checks. A critic deleted
both new differentials from `main()` plus the 4a sweep and everything stayed
green; the only trace was 129 → 128 and 81 → 76 in output nothing compared.
Two layers on purpose, for the reason tests/reject/ gives: the count makes a
deletion visible in the diff, the manifest makes it fail. Update the count
deliberately when you add a check, and add a manifest line whenever a check is
the ONLY thing standing between the repo and a specific past finding.

**This is the first mechanism in the project that can see a MISSING row.**
Everything else iterates what exists. Delete the `ACCEPT` name, misspell it
`ACCPET`, or invent a verb PCRE2 does not have, and none of that is detectable
by anything else in this repo at any effort. It works only because of Q1 (D25):
while one catch-all answered "requires module 'verbs'" for every name, pcrec's
answer did not depend on the name and the comparison was vacuous. Measured —
reverting the doorway to its pre-Q1 behaviour produces 21 failures here and,
before this file existed, produced none anywhere.

### What it does NOT establish

- **Module names are pcrec's own taxonomy** and no outside authority can check
  them. libpcre2 can say a construct exists; it cannot say `\d` belongs to a
  module called `classes`. tests/reject/'s hand-written rows remain the only
  check of that, exactly as before.
- **options = 0.** No `PCRE2_UTF`, no `PCRE2_UCP`, no `PCRE2_CASELESS`. Every
  claim is about default 8-bit mode; no UTF conformance is measured anywhere in
  this repo, and `-i` has never been run against `PCRE2_CASELESS`.
- **The `(?` doorway now gets three generated differentials of its own** (Q2),
  so the sentence that stood here — "only the `(*` doorway gets a name
  differential" — is retired. A 7650-probe BYTE sweep (libpcre2 recognises a
  byte after `(?` iff pcrec promises a module: 38 vs 217, both populations
  pinned), a 19448-probe OPTION-RUN sweep over runs of length 0-3, and 10200
  probes of TAIL sweeps for `(?P` `(?<` `(?+` `(?-`. `(?P=` versus `(?P<` and
  `\N{U+hhhh}` versus `\N` are no longer unswept.
  **Read what the tail sweeps can and cannot do.** `(?<` and `(?+` answer alike
  for every tail under libpcre2, so for those two prefixes agreement is free and
  proves nothing; only `(?P` and `(?-` have both buckets populated, which is why
  a live-prefix counter is asserted and why `(?<`'s module split is pinned by
  hand in tests/reject/ instead.
- **RECOGNITION is the bar, not compilation, and the distinction is
  load-bearing.** PCRE2's "no construct here" errors are 111 and 141; every
  other error means it DISPATCHED and is complaining about the body. `(?+x)` is
  error 129, `(?i-m-s)` is 194, `(?0J)` is 114 — all constructs pcrec owes a
  module for. Bucketing any of those with 111 makes the check demand the
  over-promise Q2 removed, in reverse: the option-run sweep was first written
  against "does it compile" and reported 967 mismatches that were entirely the
  check's error.
- **A compiling probe is not a semantic check.** `\v` compiles in libpcre2 and
  in python `re`, and they mean different things by it. PC-3 proves the row
  names a construct PCRE2 has; the corpus and the fuzzer are what test meaning.

### Sabotage validation

27 edits, each reverted after measuring, each caught — but see the tail-precedence
row, which was NOT caught on its first run and is the reason two more guards
exist. Record the EDIT, not just the count. Six exist because the R8 panel proved
the first fourteen could all pass while the check was doing much less than it
claimed; the last seven are Q2/SR-9's.

| sabotage (exact edit, in a scratch copy) | PC-3 failures |
|---|---|
| delete the `{"ACCEPT", ...}` row from `verb_upper` | 6 |
| `{"ACCEPT",` → `{"ACCPET",` | 21 (capped) |
| drop `VF_ATSTART` from the `CR` row | 10 |
| reword `"(*MARK) must have an argument"` | 20 (capped) |
| insert `{"NOTAVERB", VF_BARE, 0, NULL}` | 17 |
| verb row `syntax` `"(*ACCEPT)"` → `"(*...)"` (its pre-PC-3 value) | 1 |
| reword the collating rejection message (2 rows) | 2 |
| wrapper `"(a)\\1"` → `"(a)b"` (no longer contains its row's syntax) | 1 |
| drop `VF_GROUPARG` from `pla` | 3 |
| drop `VF_EMPTYARG` from `ACCEPT` | 4 |
| reword the lower table's "not recognized" | 20 (capped) |
| delete the `at != 0` start-of-pattern check (MOD-0.4: moved from ext.c to mod_verbs.c with the rest of `pcrec_ext_verb`; edit lands in mod_verbs.c now) | 20 (capped) — the same edit is independently mech-encoded as `tests/mech/sabotages/S29_verb_atstart_drop.sh` (MOD-0.4c), DETECTED via the `reject` suite alone (`a(*CR)`'s manifest pin), a cheaper channel than this libpcre2-backed one that still holds when PC-3 SKIPS |
| **restore pre-Q1 behaviour: the doorway ignores the name** | 21 (capped) |
| swap the two tables' "not recognized" messages | 21 (capped) |
| **`pool_from_library` succeeds and yields ZERO names** (R8/C1-F4) | **51** |
| wrapper hides its syntax inside `(?#...)` (R8/C1-F3) | 1 |
| fabricate an `ESC('y', "\\y", ...)` row (R8/C1-F3) | 1 |
| revert the `=digits` magnitude rule (R8/C2-3) | 4 |
| revert the 128-byte name-length rule (R8/C2-4) | 20 (capped) |
| `case 'K': return 0x4b;` in `esc_char_value` — a real miscompile (R8/C1-F5) | 1 |
| **shape 9 loses its nested opener** (`[[%ca[%cb%c]%c]]` → `[[%ca%cb%c]%c]]`) (R9/C1-F1) | **2** |
| `posix_whole_class_only` always returns false (R9/C3-4) | 8 |
| libpcre2 contributes ZERO POSIX class names (R9/C1-2) | 10 |
| `if (c2 == '!') ctx_fail(...)`, a construct with no registry row (R9/C1-3) | 6 |
| delete `check_class_brackets()` from `main()` (R9/C1-7) | count guard + 3 manifest lines |
| rule 2 off at doorway 4a for `.`/`=` only (R9/C2-3) | 12 |
| revert the `open_msg` branch — the 4a over-promise (R9/C1-8) | 3 |
| remove the 4b nested-opener shape, WITH the 4a shapes present (R9) | 2 |
| neutralise both 4a nested-opener shapes (R9) | 2 |
| drop the `]` from the close check, a bare delimiter closes (R9/C2-6) | 12 |
| **restore the pre-Q2 `(?` catch-all** (RS_REJECTED -> `GROUP(REG_SEL_ANY, ..., modifiers)`) | **25** (+8 reject) |
| the doorway stops reading the option run (pre-MOD-0.5b: `if (0 && (r->flags & RF_OPTION_RUN))`; MOD-0.5b retired the flag — the equivalent edit today is `if (0 && r->recognise == pcrec_registry_option_run_recognise)` in ext.c) | 23 (+4 reject) — carried forward at the move, not re-measured; `make mech` re-confirms |
| bare `(?P` promises 'named-groups' again (the 5th over-promise) | 24 (+1 reject) |
| `(?P=` back to 'named-groups' (R8/C4-7's misattribution) | 1 (+1 reject) |
| `(?+N` back to 'modifiers' | 1 (+1 reject) |
| one Q2 completion replaced by a duplicate of another (probe COUNT unchanged) | 1 (the set checksum) |
| **longest-tail-wins -> first-tail-wins in `pcrec_registry_find`** | **3** (+1 reject) — see below |
| `k15_excluded()` neutered (`return 0`) (K15, 2026-08-12) | **21** (20 capped verb-differential mismatches + the exclusion's own liveness check, which fires on the same zero) |

**The tail-precedence sabotage found a real hole and is the one to read**
(historical since MOD-0.2 — the engine it sabotaged is deleted and
`check_tail_precedence` retired with committed successors, item 6 above —
but the lesson is the reason those successors exist in the shape they do). On
its first run it produced **ZERO failures repository-wide**: every tail in the
table is one byte except `\N`'s pair, and those two were written longest-first,
so taking the FIRST matching tail gave the same answer as taking the LONGEST and
row ORDER was silently standing in for the rule. Two changes make it observable
— the `\N` rows are now written SHORTEST first, so order disagrees with the
rule, and `check_tail_precedence` asserts it for every prefix-related pair and
FAILS if no such pair is left. R9's general lesson, met again: when a dangerous
operation is safe because of a fact that lives elsewhere, the assertion belongs
where the fact is.

**And the measurement instrument lied before the check did.** Two of these
sabotages were first recorded as "0 failures" because the battery counted
`grep -c "^FAIL"`, and PC-3's stdout buffer can flush mid-line, splicing a FAIL
onto the end of a PASS line (`PASS: ...it reaches theFAIL: (? byte
differential...`). `bad()`'s `fflush(stdout)` does not prevent it — the partial
flush has already happened when the buffer fills. Count `FAIL:` unanchored, and
run a no-sabotage control first: the control is what showed the instrument was
wrong rather than the guards.

Three are load-bearing beyond the others. The pre-Q1 sabotage was detectable by
NOTHING in this repo before this change — and it also fails `sweep_verb()` now,
which is why that sweep was rewritten rather than left to narrow silently. The
empty-external-pool sabotage is the one that measures whether "external" is
still true. And the `\K` miscompile is the one proving `check_rows` looks at
pcrec at all, which it did not until R8.

**The battery lied once, and the lesson is one level down from the usual.** The
first `\K` sabotage reported 0 failures — it inserted `return;` into a function
declared `noreturn`, so nothing was sabotaged. *Prove your instrument is live
before trusting a negative result* applies to the sabotage as much as to the
check.

The SKIP path is validated the same way: pointing `PCRE2_ABI_LIBS` at a
nonexistent SONAME produces three `SKIP:` lines and exit 0, with zero failures.

### What R8 changed about this file, and why it is worth reading before editing

Four of `pcre2_check.c`'s guards exist because the panel defeated their first
versions, all in the same way — **a control sharing a source with the thing it
controls**:

- the candidate pool is tagged with the SOURCE that produced each name, and
  every name pcrec claims must come from libpcre2's binary INDEPENDENTLY.
  Without that, neutering the external source left 84% of the probes running
  (from mutations of pcrec's own table), every liveness check green, and a
  deleted verb row invisible.
- a wrapper's syntax must be LOAD-BEARING where it sits, tested by substituting
  it for `\Y` and requiring the wrapper to stop compiling. "Contains the
  syntax" was satisfied by hiding it in a PCRE2 comment.
- `check_rows` runs pcrec as well as libpcre2. It used to run only libpcre2, so
  a row that had started miscompiling passed.
- the accept and default buckets require the diagnostic's SHAPE, not pcrec's
  own catch-all STRING, which had quietly made this file the authority on which
  module owns `(*atomic:a)`.

## Known limitation: ONE BYTE of lookahead is all any sweep here has

This was previously written as "the verb doorway is weaker than its three
neighbours". R5 measured it and the statement was wrong in both directions.

**The `(*` sweep is STRONGER than was documented.** The template is `(*%c)`, so
it does vary the first name byte, and a branch keyed on it IS caught — a critic
added `if (pat[at+2] == 'N') ctx_fail(... 'misc')` and `registry` failed. The
old sentence "a name-conditional branch added to parse.c would not be caught"
is too strong.

**The real gap is any branch keyed PAST the first byte, and it is not the verb
doorway's alone.** Both of these were invisible to all seven suites:

| sabotage | what it shows |
|---|---|
| branch on `(*NO_S…` (four bytes in) | verb names past their first letter are unswept |
| branch on `(?P=` vs `(?P<` | the `(?` doorway has the same hole |

Selector byte `P` carries two PCRE2 constructs — `(?P<name>...)` and
`(?P=name)` — and the sweep varies only the byte after `(?`. The same is true of
`(?<=` vs `(?<!` vs `(?<name>`, of `(?C1` vs `(?C{...}`, and of every verb name.
registry.c's header already names one instance (`\N{U+hhhh}` sharing the `N`
selector with bare `\N`) and calls it a known outstanding second home — it is
not one instance, it is **the shape of every doorway that is keyed by one byte
while PCRE2 keys by a string.**

**BOTH rows above are now closed.** `(*NO_S…` — a branch four bytes into a verb
name — is caught by `pcre2_check.c`, because names are compared whole against
libpcre2 over ~75,000 candidates. `(?P=` versus `(?P<` was the open half, and
SR-9's `tail` plus Q2's tail sweeps closed it: `(?P` has three recognised tails
and 252 that are error 141, and the sweep asserts pcrec agrees on all 255.

The general statement still stands and is worth keeping: **a sweep that varies
one byte cannot see a branch keyed past it.** What changed is that this doorway
now has a differential rather than only a sweep. `(?C1` versus `(?C{...}` is a
live remaining instance — `(?Ca)` is error 182, "unrecognized string delimiter
follows (?C", so the callout body has a grammar nothing here reads. It belongs
to whoever builds module `callouts`, and MOD-0's syntax port is where it goes.

Per-verb MODULES still arrive with SR-6 (`(*pla:...)` is a lookahead and will
not belong to module `verbs`); Q1 gave the names an existence and a form, not a
module. Until then: do not read "all four doorways swept" as "every construct
behind them is guarded".

Maintenance: update this file when files are added/removed or their roles
change. Re-run the sabotage battery if the check's structure changes — a
conformance test that cannot fail is worse than none, because it reads as
coverage.

## compliance_section.py (SR-4)

Connects the registry to `docs/pcre2_compliance.md`. Run from
`run_registry_tests.sh` after `registry_check`, so its two results are printed
*outside* the C harness's "checks passed: N" summary — the count in that line is
registry_check.c's alone.

- `--check` — the generated construct INDEX in the compliance doc must match
  `pcrec --list-syntax`. Regenerate with `--write` after adding a row.
- `--names` — every ``module `X` `` named in the doc's hand-written prose must
  be a module the registry knows. This is the check that catches the realistic
  failure: a module renamed in registry.c leaves the prose confidently
  describing something that no longer exists, and nothing else would notice.

The document is NOT rendered wholesale, which the SR-4 plan text asked for.
Doing that would replace a survey — DFA-feasibility judgements, the
`PLANNED`/`PLANNED-HARD` reasoning, the divergence post-mortems, and every row
about BASE syntax, which the registry deliberately does not describe — with an
inventory the registry can already print. So the inventory is generated between
markers and the analysis is left to humans.

Both checks are positive-controlled: renaming a module in the prose
(`quoting` → `quotingx`) fails `--names`; editing one status cell in the
generated index fails `--check`.

**`--check` is a DRIFT detector, not a control, and the difference matters.**
Its own failure message names the remedy — `--write` — which regenerates the doc
from whatever the table now says and turns the suite green. It catches "someone
changed the table and forgot the doc". It cannot catch "someone changed the
table on purpose and regenerated". An R5 critic demonstrated exactly that:
mis-assigning `(?0)`'s module fails `--check`, and one `--write` makes it pass.
The control for a wrong module name is the hand-written table in tests/reject/,
never this.

## Two hand-written assertions that must not be tidied away (R5 N-1)

`check_table_to_parser` ends with two hand-written `expect_msg` calls for the
class-open entry to the collating rows, added because the doorway model does not
describe that position so nothing derives them.

After SR-2 they are **the only non-circular assertion about message TEXT left in
this file.** Every other message check now reads the expected string from the
row that the parser also renders from. An R5 critic predicted SR-2 had made the
documented "reword the collating message → 2 failures" sabotage stale, measured
it, and found those two calls still catch it.

If they are ever folded into the derived loop as a tidy-up, `registry` loses the
ability to see any message change at all and tests/reject/ becomes the sole
guard. That would look like a simplification. It is not one.
