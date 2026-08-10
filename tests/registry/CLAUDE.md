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
- **run_registry_tests.sh** — builds and runs both, plus compliance_section.py;
  part of `make test`. Env: CC, KEEP=1

## What it asserts

1. **Well-formedness** — no two rows claim one byte, catch-all rows come last,
   each row's `syntax` example really contains its selector byte, and the
   status/module/feature/engines/diagnostic fields are mutually consistent.
   Plus an EXACT row count (68 today) so rows cannot be deleted silently — the
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
3. **The verb NAME differential**, and this is the part that scales. Candidate
   names are generated from **libpcre2's own shared object** — its compiled-in
   name tables, read via `dlinfo`, expanded to every prefix and suffix — plus
   single-character mutations of the names pcrec claims, plus all 255 bytes.
   ~75,000 candidates in 11 forms, ~823,000 probes, about 3 seconds. libpcre2's
   verdict on each decides what pcrec owes.

The prefix/suffix expansion is not decoration: `ANYCRLF`, `CRLF` and `LF` are
real PCRE2 option names that appear in the binary only INSIDE `BSR_ANYCRLF`, so
a pool of whole runs would have missed three names this check exists to notice.

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
- **Only the `(*` doorway gets a name differential.** The other three are
  byte-keyed and their rows are checked one probe each. `(?P=` versus `(?P<`,
  and `\N{U+hhhh}` versus `\N`, are still unswept — that is SR-9's `tail`.
- **A compiling probe is not a semantic check.** `\v` compiles in libpcre2 and
  in python `re`, and they mean different things by it. PC-3 proves the row
  names a construct PCRE2 has; the corpus and the fuzzer are what test meaning.

### Sabotage validation

20 edits, each reverted after measuring, each caught. Record the EDIT, not just
the count. The last six exist because the R8 panel proved the first fourteen
could all pass while the check was doing much less than it claimed.

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
| delete the `at != 0` start-of-pattern check in ext.c | 20 (capped) |
| **restore pre-Q1 behaviour: the doorway ignores the name** | 21 (capped) |
| swap the two tables' "not recognized" messages | 21 (capped) |
| **`pool_from_library` succeeds and yields ZERO names** (R8/C1-F4) | **51** |
| wrapper hides its syntax inside `(?#...)` (R8/C1-F3) | 1 |
| fabricate an `ESC('y', "\\y", ...)` row (R8/C1-F3) | 1 |
| revert the `=digits` magnitude rule (R8/C2-3) | 4 |
| revert the 128-byte name-length rule (R8/C2-4) | 20 (capped) |
| `case 'K': return 0x4b;` in `esc_char_value` — a real miscompile (R8/C1-F5) | 1 |

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

**One of the two rows above is now closed, and by the differential rather than
by a sweep.** `(*NO_S…` — a branch four bytes into a verb name — is caught by
`pcre2_check.c`, because names are compared whole against libpcre2 over ~75,000
candidates. `(?P=` versus `(?P<` is NOT: the `(?` doorway has no name
differential and is still keyed by one byte. That asymmetry is the honest
statement of where PC-3 reached and where SR-9's `tail` still has to.

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
