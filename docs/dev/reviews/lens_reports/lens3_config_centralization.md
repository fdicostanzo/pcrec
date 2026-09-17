# LENS 3 — magic numbers, inline strings, config centralization

Lane `lens3cfg` (opus, REVIEW). Read-only to `src/`, `cli/`, `lib/`,
`tests/`; nothing built, no `make` run. Charter:
`docs/dev/reviews/code_review_criteria_draft.md`, lens 3 (Frank's #3).

Scope: the PRIMARY tier only (`src/`, `cli/`, `lib/`), per the
ratification's open-item disposition.

Metric artifacts read (A5): `tools/review/out/literal_value_freq.tsv`
(5,149 rollup rows over 12,617 occurrences) and
`tools/review/out/literal_census.tsv`, both at commit `1edd6c5e`.

---

## 0. THE RULED RECORD THIS LENS IS ANCHORED TO (A1)

Read before any finding below, because three of the four candidate
classes a naive sweep produces are already ruled and are in the
PROBED-AND-HELD list rather than the findings list.

**D90** (`docs/dev/decisions.md:6313`) is the central-config ruling:
*every numeric limit lives in one table, `src/core/limits.def`, that
`--list-limits` dumps and the spec derives from; a new number is a table
row, never a bare `#define`.* It also commissions the enforcement:
*"a sabotage row catches a bare numeric `#define` outside the table."*

The enforcement as built is `tests/registry/limits_check.sh` §3
(`:212-296`). Its shape matters to everything below and is stated here
once:

- It greps `src/`, `cli/`, `lib/` for numeric `#define`s and enum
  members, then **filters by the IDENTIFIER's spelling**:
  `MAX | _MIN_ | _MIN\b | CAP | LIMIT | BUDGET | THRESHOLD | _LEN\b |
  DEPTH | NEST` (`:277`).
- Anything surviving the filter must be either a `limits.def` row or on
  a **12-name allowlist** whose stated admission criterion is that the
  number is *"EXCLUDED from limits.def BY RULE, named and argued at its
  own site — never silently, and never because nobody looked"*
  (`:214-216`).

D90's companion rulings that bound this lens: **D26** (diagnostic
WORDING is the lowest-effort tier — do not gold-plate it) and the
registry's own `RegDiag`/`PCREC_UNBUILT_MARKER` mechanism
(`src/core/internal.h:2700-2714`), which already centralizes the
`requires module 'X'` phrase for the doorway path *as data* —
*"one define, not two copies of the sentence."*

---

## 1. WHERE THE SWEEP STOPPED (ADDENDUM 2 — no silent caps)

Worked top-down over the frequency rollup and, separately, over the
census sorted by numeric magnitude.

**Strings — covered:** every rollup row with `count >= 3` AND literal
length > 8 (131 rows, all read in context), plus every row with
`count >= 4` at any length (a further ~50 rows, mostly single
characters).

**Strings — NOT individually adjudicated, held as a class:** the
single- and two-character literals at the head of the rollup (`""` 260,
`'\t'` 131, `'%s'` 130, `' '` 59, `'\n'` 44, `'-'` 43, and ~40 more).
These are the parser's and emitter's *alphabet* — `'('`, `'{'`, `'^'`
in `parse.c`/`registry.c` ARE the grammar being recognised, and naming
them would move the grammar away from the text a reader compares
against PCRE2's own syntax page. No finding is available here that does
not make the code worse.

**Numbers — covered:** every rollup row with `count >= 3` (62 rows) and
every census occurrence of magnitude >= 1000 (the full sorted list; the
top 45 are in the working notes).

**Numbers — NOT individually adjudicated, held as a class:** `0`, `1`,
`2` (3,989 of the census's 12,617 occurrences across 51 files) and the
small-integer tail `3`-`9`. These are array indices, loop bounds,
return codes, and arity — the population D90 is explicitly not about.

**Not reached at all:** the SECONDARY tier (`tests/lib/`,
`tests/harness/`), which the ratification dispositioned to the next
round; and `cli/main.c`'s option-string plumbing beyond what the rollup
surfaced (its 1,700+ lines carry an option-parsing vocabulary that is
lens 2/lens 11 territory as much as lens 3, and I did not audit it
row-by-row).

---

## 2. FINDINGS

Each carries A4 severity / effort / blast radius and an A3
check-coupling note.

---

### F1 — The D90 detector is keyed on the constant's NAME, so a tuned numeric constant whose name lacks the ceiling vocabulary is structurally invisible to it

**Severity: MAINTAINABILITY. Effort: LOCAL. Blast radius: 1 check file
(`tests/registry/limits_check.sh`), 0 source files if the fix is
allowlist-only; 0 emitted bytes; 0 sabotage anchors.**

`limits_check.sh:277` filters candidate `#define`s by whether the
IDENTIFIER contains `MAX|_MIN_|CAP|LIMIT|BUDGET|THRESHOLD|_LEN|DEPTH|NEST`.
That is a filter over *the vocabulary of ceilings*. A number that is a
tuning constant, a calibration weight, or a default — none of which are
spelled with those tokens — passes through unseen.

Measured (`grep` for numeric `#define`s in `src`/`cli`/`lib`, minus
`limits.def`, minus the filter's own vocabulary): **14 numeric `#define`s
the detector cannot see.** Classified:

| site | constant | disposition |
|---|---|---|
| `src/core/compile.c:458` | `SIZE_TERM_BAR_DEFAULT 75` | **argued at its site; belongs on the allowlist; is not on it** |
| `src/opt/prefix_k.c:260-263,280` | `C_MEMCHR 6u`, `C_BITMAP 116u`, `C_VERIFY 250u`, `C_ENTER 2000u`, `C_MISPRED 1500u` | cost-model calibration; each argued at its site; same |
| `src/opt/prefix_k.c:294-295` | `MATERIAL_NUM 2u`, `MATERIAL_DEN 1u` | ditto (the `2` carries 12 lines of derivation) |
| `src/gen/emit_dfa.c:2386` | `PREMUL_DEAD 65535` | a table SENTINEL, not a limit — correctly out |
| `src/core/internal.h:4467,4475` | `PCREC_RXT_WAVE_BUILT 23`, `..._RESERVED 999` | schema version/sentinel — correctly out |
| `src/core/internal.h:2886` | `REG_SEL_ANY (-1)` | sentinel — correctly out |
| `lib/pcrec.h:683-684` | `PCREC_ENGINE_DFA 1`, `PCREC_ENGINE_VM 2` | API enum values — correctly out |

So: **8 of 14 meet the allowlist's own stated admission criterion
("named and argued at its own site") and none of the 8 is on the
allowlist** — not because anyone ruled them out, but because the
detector never offered them for a ruling. That is the distinction D90's
allowlist comment draws in its own words ("never because nobody
looked") and it is currently false for these 8.

**This blind spot has already fired once and was patched in the wrong
dimension.** The check's own comment (`:240-256`) records `[ENG-ISL]`
(2026-09-03, panel r53): `VM_ISL_MIN_BRANCHES` and
`VM_ISL_MIN_BRANCHES_PREFIXED` sat as bare `#define`s invisible to the
scan because *"a SELECTION KNEE is just as often spelled as a FLOOR."*
The repair **added two words to the vocabulary** (`MIN`, `THRESHOLD`).
That fixes the instance and leaves the mechanism: the next knee spelled
`C_ENTER` or `SIZE_TERM_BAR_DEFAULT` or `WEIGHT` or `BIAS` is invisible
again, and this report is the second instance.

**Suggestion (judgment call, marked as such).** Do *not* widen the
vocabulary a third time. Invert the filter: scan for numeric
`#define`s/enum members in `src`/`cli`/`lib` **regardless of name**,
and require each to be a `limits.def` row, on the allowlist, or on a
new second allowlist for the non-limit kinds the table above
distinguishes (sentinels, API enum values, schema versions). The
population is small enough to make that tractable — the full
unfiltered population is 14 beyond what the filter already catches, so
the one-time cost is writing 14 allowlist lines with their reasons, and
the steady-state cost is that a new constant must be classified once.
That converts "the check happens to know the words people used" into
"every number is dispositioned," which is the property D90's text
actually claims.

**A3:** the only binding is `limits_check.sh`'s own PASS line
(`:290`), whose wording enumerates the filter vocabulary and would need
rewording with the filter. `tests/mech/sabotages/S208`/`S209` plant
against `limits.def` rows and the doc join, not against this arm — a
widened arm would want its own sabotage row (currently none plants a
name-shape-invisible `#define`).

---

### F2 — The `[ART-SIZE]` ladder's two parameters live in two different homes, and the rationale given for the split does not distinguish them

**Severity: MAINTAINABILITY. Effort: MECHANICAL (or none — see below).
Blast radius: 2 files if moved; 0 emitted bytes; re-pins
`limits_check.sh`'s manifest count and `docs/spec/limits.md` §3 if a row
is added.**

The unroll-K size-term ladder is steered by exactly two numbers, read
by one function and exposed by one accessor pair
(`pcrec_tune_size_term_bar` / `pcrec_tune_size_term_threshold`,
`src/core/internal.h:5517-5518`):

- `PCREC_SIZE_TERM_THRESHOLD = 120000` bytes — **a `limits.def` row**
  (`src/core/limits.def:161`, kind `selection knee`).
- `SIZE_TERM_BAR_DEFAULT = 75` percent — **a bare `#define`**
  (`src/core/compile.c:458`).

Both are overridden by the same `[OPT-DIAL]` rows (`src/core/tune.c:66,72`:
`min-size` → 95/40000, `size` → 85/80000), both are consumed two lines
apart (`compile.c:654,657`), and both are `PcrecTuneRow` fields
(`internal.h:5507-5508`).

**A1 — the argued placement, and why it is still worth filing.** The bar
*is* argued at its site (`compile.c:452-457`): *"the DEFAULT still lives
here, beside its one reader, which is why `src/core/tune.c` carries an
em-dash sentinel rather than a copy of it."* That argument is sound as
far as it goes — but it is equally true of the threshold, which also has
its one reader three lines away and which is nonetheless a row. The
comment explains why the bar is not duplicated into `tune.c`; it does
not explain why the bar is not in `limits.def` when its twin is.

I am **not** proposing the move, because I cannot tell from the record
whether the asymmetry is deliberate (a percentage is a different kind of
thing from a byte ceiling, and `limits.def`'s `unit` vocabulary has no
"percent") or accidental. Either resolution is cheap:

(a) **it is deliberate** → say so in one clause at `compile.c:458` and
add it to F1's allowlist, which is where the record of a deliberate
exclusion belongs; or
(b) **it is accidental** → add the row with `unit "count"` (the table's
own dimensionless spelling) or a new `"percent"` unit, and the pair is
reunited.

Today it is neither: the number is outside the table for a reason the
comment does not give, and outside the allowlist for no reason at all
(F1's mechanism).

**A3:** `docs/spec/tuning.md` §5 and `docs/spec/limits.md` §3 both carry
ladder prose; `limits_check.sh` joins §3 against the dump, so adding a
row obliges a §3 hunk in the same change (D80). `S251_tune_ladder_
threshold_dropped.sh` plants against the tune ladder and would want
checking against a moved default, though it targets the threshold arm.

---

### F3 — FNV-1a's published constants are open-coded at 9 sites in 2 files, with nothing naming the algorithm

**Severity: MAINTAINABILITY. Effort: MECHANICAL. Blast radius: 2 files,
0 checks, 0 emitted bytes (verified below).**

| constant | what it is | sites |
|---|---|---|
| `2166136261u` | FNV-1a 32-bit offset basis | `src/ir/dfa.c:852`, `src/opt/minimize.c:130` |
| `16777619u` | FNV-1a 32-bit prime | `src/ir/dfa.c:856,859,862,864`; `src/opt/minimize.c:133` |
| `1099511628211ull` | FNV 64-bit prime, used as a bare multiplicative-hash multiplier | `src/ir/dfa.c:302,383` |
| `0x9e37u`, `0x2545u` | per-view salts (golden-ratio-derived), unnamed | `src/ir/dfa.c:857` |

`dfa.c:852-866`'s `dhash` and `minimize.c:130-134`'s inline loop are the
**same algorithm written twice** — and the lens-1 loop (ADDENDUM 1)
applies: the shared abstraction is a two-function `fnv1a_init` /
`fnv1a_step` pair (or one `fnv1a_bytes(const void *, size_t)`), which is
lens 1's "missing library operation" class exactly. The A2 signature:

```c
static inline uint32_t fnv1a_32_init(void);          /* 2166136261u */
static inline uint32_t fnv1a_32_mix(uint32_t h, uint32_t v); /* h ^= v; h *= 16777619u */
```

What varies per site: `dfa.c` mixes `int` list elements plus two salted
accept terms; `minimize.c` mixes `sig[k]` over `siglen`. Both reduce to
a fold over `fnv1a_32_mix`.

**Why this is admissible rather than pedantry:** the value is not the
saved keystrokes, it is that nothing in either file says *which* hash
this is. `1099511628211ull` at `dfa.c:302` is the 64-bit FNV prime used
as a plain Knuth-style multiplier with a `>> 20` — a reader cannot tell
whether the constant's specific value is load-bearing (it is, mildly:
it is odd and well-distributed) or arbitrary, and so cannot tell whether
changing it is safe.

**A3 — the blast radius is genuinely nil, and the code says so.**
`dfa.c:836-843`'s own comment: *"this changes no state NUMBERING and
therefore no emitted byte on a machine without a class axis: a new
state's index is `d->n++`, i.e. insertion order, and the hash only picks
which probe sequence finds it."* `minimize.c`'s is a bucketing hash over
signatures compared exactly afterwards. No check binds to a hash value;
no sabotage row plants one. A byte-preserving extraction (same
arithmetic, same order) is answer-identical and emit-identical by
construction — but it must be *exactly* the same arithmetic, because
`dfa.c:857`'s salted term (`h ^= accept + 0x9e37u + u * 0x2545u`) is not
plain FNV and must not be "tidied" into the helper.

---

### F4 — `"requires module '%s'"` is spelled 20 ways outside the one place the tree already rules it should be data

**Severity: MAINTAINABILITY. Effort: LOCAL. Blast radius: 6 source files;
~80 test files bind to the rendered text (see the A3 note — the cost is
zero for a byte-preserving change and enormous for any other, which is
the point).**

The phrase is load-bearing: `CLAUDE.md`'s compatibility standard says
*"'Requires module X' discharges that obligation [D26] in full."* The
tree already knows it should be centralized — `src/core/internal.h:2707-2714`
defines `RegDiag` (`RD_MODULE`, `RD_MODULE_OCTAL`, `RD_FIXED`) and says
*"Kept as data so SR-2's dispatch is a mechanical substitution and
byte-identity is provable,"* and `PCREC_UNBUILT_MARKER` two lines above
exists so *"a reworded refusal cannot silently stop being classified —
one define, not two copies of the sentence."*

That mechanism covers the registry doorway path. **Outside it, 20 call
sites hand-spell the phrase in 8 distinct format strings:**

- `src/parse/mod_uprops.c` — 4 copies of
  `"\\%c: malformed property escape — requires module '%s'"`
  (`:351,385,411,435`), 3 of `"\\%c requires module '%s'"`
  (`:371,510,530`), 2 of `"...recognises — requires module '%s'"`
  (`:373,518`);
- `src/parse/ext.c:334,343,345,524` — four more variants;
- `src/parse/mod_modifiers.c:316,377`, `mod_recursion.c:291`,
  `mod_backrefs.c:275`, `parse.c:1760`, `syntax_dump.c:159,1674`.

Two extra hazards specific to this set: the uprops variants contain a
**non-ASCII em dash (U+2014)** repeated verbatim four times, and
`mod_recursion.c:291` / `mod_backrefs.c:275` carry the *identical*
`"%s names a capture group, which requires module "` split across a
string continuation in two different modules.

**A1 — this is not D26 gold-plating and here is why.** D26 says do not
spend effort matching *PCRE2's* wording for something pcrec does not
implement. This finding proposes no wording change at all; it proposes
that pcrec's own already-ruled-as-data sentence be spelled once. The
`RegDiag` comment is the tree's own statement of the principle, and
these 20 sites are its residue.

**A2 — the named abstraction.** A single format-template table keyed by
the *shape* of the refusal, in `parse/`:

```c
/* one home for the D26-discharging sentence */
#define PCREC_REQUIRES_MODULE_FMT   "requires module '%s'"
```

plus three composed helpers for the recurring prefixes the sites
actually use (`"\\%c %s"`, `"\\%c in a class %s"`,
`"(?%c...) %s"`), each taking the module name. What varies per site is
the construct prefix and the module; what must not vary is the tail.
This is the minimum shape that makes the tail single-homed; a fuller
table (a `RegDiag`-style enum extended to producer-side refusals) is a
DESIGN-EVENT and I am not proposing it here.

**A3 — the check coupling is the argument, not an obstacle.** `grep -rl
"requires module" tests/` returns **80 files** (`.rxt` corpora across
`backrefs`, `lookaround`, `modifiers`, `recursion`, plus
`tests/reject/run_reject_tests.sh` and `tests/cli/`). Every one of them
binds to the **rendered output**, not to the source spelling. So:

- a byte-preserving extraction costs **zero** re-aims;
- and the 80 files are precisely why nobody can afford to *reword* the
  phrase — which is the case for spelling it once, since the current
  arrangement puts 20 independent opportunities to drift in front of a
  sentence that 80 files assert.

---

### F5 — The repeated `"missing closing ) for group"` is real duplication, and the comment that licenses it claims something the tree measurably does not do

**Severity: MAINTAINABILITY (with a docs-accuracy edge).
Effort: MECHANICAL. Blast radius: 7 source files, 4 test files (rendered
text only).**

This was pre-flagged by the tools lane; the A1 check resolves *against*
the comment, with argument.

`src/parse/parse.c:1902` says: *"That last clause is what keeps 'missing
closing ) for group' single-homed: the base grammar owns that message
for its own two forms (`(` and `(?:`), and **a module owns a DIFFERENT
message for its own construct**. Different constructs, different
grammars, so this is not the D24 two-homes shape."*

**Measured — the modules do not own a different message. Eight sites
carry the identical string:**

| site | owner |
|---|---|
| `src/parse/parse.c:1404` | base grammar (the one the comment licenses) |
| `src/parse/ext.c:415`, `:447` | the extension doorway |
| `src/parse/mod_atomic_groups.c:90` | module `atomic-groups` |
| `src/parse/mod_lookaround.c:459` | module `lookaround` |
| `src/parse/mod_modifiers.c:470` | module `modifiers` |
| `src/parse/mod_named_groups.c:242` | module `named-groups` |
| `src/parse/mod_recursion.c:531` | module `recursion` |

The comment's *contract* claim is true and valuable — the caller
consumes its own `)` and raises its own diagnostic, because only it
knows which construct is unterminated. That is a statement about **who
raises**, and it holds. The sentence that does not hold is the one about
the message: the comment asserts the phrase is single-homed *because*
modules word it differently, and seven modules word it identically.
`src/parse/CLAUDE.md:1800` repeats the same claim.

So the comment is not a ruling that forbids this finding — it is a
ruling about ownership plus a factual claim about the corpus that has
gone stale (or was never true). Both halves want attention:

1. **The phrase**: seven modules spelling one sentence is F4's class at
   smaller scale, and the fix is the same — one `#define` beside the
   `REFUSE` macro, expanded at each site, rendered text unchanged.
2. **The comment**: whichever way (1) goes, the sentence *"a module owns
   a DIFFERENT message for its own construct"* should be corrected to
   what is actually true — the modules deliberately share this message
   and own only the *decision to raise it*. Leaving it is an
   inline-archaeology defect of lens 4's class: a comment that a reader
   will trust and that a `grep` refutes in one command.

**A3:** four test files bind to the rendered text
(`tests/reject/run_reject_tests.sh` ×2, `tests/parse/run_parse_tests.sh`
×2, `tests/cli/run_cli_tests.sh` ×1, `tests/registry/registry_check.c`
×1). The three shell sites compare output and cost zero re-aims under a
byte-preserving change. **`tests/registry/registry_check.c:1482` is
different and is the ninth home**: it is C, and it holds the sentence as
a compiled-in expected value (`want = "missing closing ) for group";`).
It is a check, so the scope tiers put it outside this round's PRIMARY
tier and a *deliberate* second home in a check is defensible — a check
that reads its expectation from the code it checks is the
controls-share-a-source defect this tree has recorded repeatedly. Worth
stating explicitly either way: today the duplication there is
undeclared, and a reader cannot tell whether it is the good kind.

---

### F6 — 94 fixed-size scratch buffers across 19 unnamed sizes, in a file whose own comments record being bitten by exactly this twice

**Severity: CORRECTNESS-RISK (latent; no live truncation confirmed here).
Effort: CROSS-CUTTING. Blast radius: up to 94 declaration sites; 0
emitted bytes if sizes are preserved.**

Measured over `src/` + `cli/` `.c` files:

- **94** declarations of the form `char NAME[<literal>]`, over 19
  distinct literal sizes: `32`(20), `64`(14), `48`(9), `160`(8),
  `256`(6), `128`(6), `192`(5), `512`(4), `96`/`80`/`40`/`8`(3 each),
  and singletons at `1024`, `352`, `288`, `144`, `24`, `4`, `3`.
- **11** more declarations that do the right thing and derive from a
  named bound plus an unnamed headroom term, e.g.
  `char cnt[PCREC_MAX_EMIT_NAME_LEN + 64]` (`emit_vm.c:4989,5137`) and
  `char sel1_prefilter_reason[PCREC_DFA_OVERFLOW_WHY_LEN + 160]`
  (`emit_vm.c:7800`).

`src/gen/emit_vm.c` holds the bulk (**46** of the 94), and its own
comments record the hazard having fired:

- `emit_vm.c:944-945`: *"…an artifact that names the wrong cell, and
  **this file has already been bitten once by a too-small snprintf
  buffer** (see the listing's VE_SET arm)"* — immediately above
  `char nm[48]`.
- `emit_vm.c:8165-8167`: a comment describing a live truncation
  (*"TRUNCATED it to `slot_values[2] <- scan_`"*) immediately above
  `char slot[48]`, with the added warning *"A rename that moves emitted
  names has to check the listing's column widths too."*

**A1 — what D90 does and does not cover here, and the correct reading.**
A `snprintf` scratch buffer is *not* a limit in D90's sense: it is not
"a value a pattern can be measured against," which is the exact phrase
`limits_check.sh`'s allowlist uses to exclude `SELECT_MAX_ROUNDS` and
`COMPILE_MAX_ATTEMPTS`. **Proposing 94 `limits.def` rows would
contradict the ruled boundary, and I am not proposing it.**

The admissible finding is narrower and is a question, not a verdict:
**which of these 94 buffers hold text whose length is bounded by a
`limits.def` row, and of those, which fail to derive from it?** Eleven
sites demonstrate the correct pattern. I did not audit all 94 against
their writers — that is a targeted follow-up, not a lens-3 sweep
product, and it is CORRECTNESS work (silent `snprintf` truncation in an
emitted artifact's identifier is a miscompile, which is why the file's
two recorded incidents matter more than the count does).

**Suggested disposition:** a follow-up slice that, for each of the 94,
names the longest string its writer can produce and either (a) derives
the size from the governing `limits.def` row, or (b) states in one
clause why the bound is local. The output is a table, and the sites that
cannot answer (a) or (b) are the bug list. The remaining duplication —
19 sizes chosen by taste — is then a POLISH residue, not the finding.

**A3:** none of the 94 sizes is bound by any check; the *emitted text*
they produce is bound by ~24 files (see F7's note), which is what makes
a truncation show up as a codegen-check failure rather than as silence —
but only if a check happens to exercise the truncating input, and
`emit_vm.c:8165`'s recorded incident is a listing column that nothing
asserted.

---

### F7 — The emitted matcher's own identifier names are free-floating string literals at ~50 sites (POLISH, filed with its counter-argument)

**Severity: POLISH. Effort: MECHANICAL. Blast radius: 2 files, 0 emitted
bytes, 0 check re-aims.**

`"scan_position"` appears **19** times (`emit_dfa.c:5016,5085`;
`emit_vm.c` ×17, all as an argument to `vm_mrl_test`/`vm_push_at`),
`"(ptrdiff_t)scan_position"` 12 times (`emit_vm.c`),
`"subject_length"` 6, `"subject[scan_position]"` 5, `"search_from"` 5,
`"subject"` 5.

**The counter-argument, which I think mostly wins.** Renaming an emitted
identifier is a D76/D94 event — an `abi` bump plus an identity-gate
re-pin plus a grep for every reader of the number. So the "a rename is a
50-site edit" argument is weak: a rename is already a heavyweight,
deliberately-ritualized change, and the 50 sites are the smallest part
of its cost.

What survives as a real (small) argument for naming: these strings are
passed as *positional* arguments to helpers like
`vm_mrl_test(v, "scan_position", ...)`, where the parameter is an
arbitrary C expression. A named `EMIT_SCAN_POS` would make it visible at
a glance which calls pass the canonical cursor and which pass a computed
expression (`vm_fadd(bw, v->fmin)` and friends appear in the same
position). That is a readability gain, not a safety one.

**Filed as POLISH and ranked last of the findings.** If a refactor wave
touches `emit_vm.c` for other reasons (lens 10's emission kit is the
likely one), folding this in is nearly free; on its own it does not earn
a wave.

**A3 — measured, and it is the reassuring direction.** `scan_position`
appears in **6 `tests/codegen/` scripts** (`run_dfa_stamps.sh` ×6,
`run_codegen_tests.sh` ×11, `run_anchored_match.sh` ×3,
`run_encoding_checks.sh` ×2, `run_premul_table.sh`, `run_offset_skip.sh`)
and **18 `tests/mech/sabotages/` anchors** (S68 ×7, S73 ×9, S133 ×6,
S135 ×6, S60 ×5, S57 ×4, S-U8 ×4, and eleven more). Every one of them
matches the **emitted artifact's text**, not the compiler's source. A
source-side renaming to a `#define` whose value is the same string
changes no emitted byte and therefore re-aims nothing — but it is also
why the finding is POLISH: the checks are indifferent either way.

---

## 3. PROBED-AND-HELD

Candidates examined and **rejected**, with the reason, so the ground is
not re-covered.

**H1 — Stamp value strings duplicated between the emitters and
`src/parse/axes_dump.c`.** Roughly 30 rollup rows look like textbook
duplication: `"declined-nullable"`, `"overflowed-dfa"`,
`"size-cap-retry"`, `"cap-rescue"`, `"offset-set"`, `"unwrapped"`,
`"selected"`, `"premultiplied"`, `"scan-edge"`, `"count-collapsed"` and
more, each written once in `emit_dfa.c`/`emit_vm.c`/`compile.c` and
again in `axes_dump.c`. **HELD: known, argued, and guarded
two-directionally.** `axes_dump.c:1-16` states the shared-source
boundary explicitly; `tests/registry/axes_registry_check.sh:495-525` runs
a both-directions set comparison of every dumped `stamp_value` against an
independent source (the spec's value-set table, or the emitter's own
derivation), failing in both the "dump stamps a value the source does not
list" and "the source documents a value no row names" directions; and the
check's own comment at `:708-710` names this exact risk —
*"axes_dump.c's stamp_value literals are NOT stringified from a real
symbol the way the deny/force bit values are — this check is what
catches THAT drift risk."* A lens-3 finding here would be re-filing a
solved problem.

**H1a — one note, not a finding.** `axes_dump.c:182-195`'s
`cli_flag_of()` is a hand-written `strcmp` ladder on (axis, candidate)
returning a CLI flag string. A candidate RENAME in the emitter's array
makes it silently return `""`. That *is* caught today — but by a
different arm than the one you would look for: the description table
(`AXIS_DESC`) is keyed on the same pair, so a rename also produces the
placeholder text, and `axes_registry_check.sh:323` asserts the
placeholder never appears. The coverage is therefore real but
**incidental**, and one-way: a candidate that legitimately gains a
description but no flag (which already happens — `:175-181` names the
four offset-0 forms) sits in a state the flag arm cannot distinguish
from a broken join. Not worth a change today; worth knowing if the
description placeholder check is ever relaxed.

**H2 — `src/opt/prefix_k.c`'s 256-entry byte-frequency table (lines
93-108), whose cells include `7476` ×10, `124561`, `84235`, `54163` and
~60 more large literals.** These dominate a magnitude-sorted census and
look exactly like magic numbers. **HELD: this is DATA, and it is the
best-documented data in the tree.** `prefix_k.c:55-88` derives every
region of the table from cited priors (English letter frequency, the
whitespace share of prose, a deliberate floor of 2 ppm on the whole
0x80-0xff half so *"a zero would let the model believe a byte is
IMPOSSIBLE"*), states the normalisation (*"NORMALISED to sum to exactly
1,000,000 — the residue of the rounding is added to `' '`"*), publishes
the sum through `pcrec_byte_freq_total_ppm`, and has
`tests/codegen/run_offset_skip.sh` §1 assert it. Naming these cells
would destroy the one property that makes the table readable — that it
is laid out as a 16×16 ASCII map with the character in the comment above
each column.

**H2a — the one residue, filed as a sub-point rather than a finding.**
The ppm scale itself (`1000000` / `1000000u` / `1000000ull`) is spelled
**15 times** across ten lines
(`prefix_k.c:301,309,310,321,322,323,447,503,516,567`; four of those
lines carry it twice) in three different suffixed forms. It is the denominator of every
arithmetic step in the cost model and it is the one number in the file
with no name. A `#define PPM_SCALE 1000000u` (or an inline
`ppm_mul(a, b)` helper) would be a genuinely mechanical improvement —
but it is one file, one constant, and the file's arithmetic is
`unsigned long long`-careful in a way a careless macro could break, so
it belongs in whatever wave touches `prefix_k.c` for another reason, not
on its own. Note `cli/main.c:702` also compares against a bare `1000000`
in an unrelated bound, which is coincidence, not a shared constant — do
not join them.

**H3 — `prefix_k.c`'s `C_MEMCHR`/`C_BITMAP`/`C_VERIFY`/`C_ENTER`/
`C_MISPRED`/`MATERIAL_NUM`/`MATERIAL_DEN`.** **HELD as limits.def rows,
counted under F1 as allowlist candidates.** Every one is already a named
constant with a derivation comment beside it (`MATERIAL_NUM`'s runs 12
lines and explains why it is 2 and not the draft's 1.5). They are not
"magic numbers"; the only defect is F1's — that the D90 detector never
offered them for an explicit allowlist ruling.

**H4 — the `TUNE_TABLE` policy cells in `src/core/tune.c:61-95`
(`95, 40000`, `85, 80000`, `8192`, and the em-dash sentinels).**
**HELD: ruled.** `tune.c:53-58` states the convention — *"Every
non-sentinel cell's citation is in `docs/spec/tuning.md` §5 and in the
design's §3.3, in the cell itself — a cell with no citation is an
em-dash, which is the allowlist made mechanical rather than a rule a
reader has to apply afterwards."* The literals are the table's content
and each carries its measurement citation in an adjacent comment block.
`docs/design/opt_dial_design.md` and the r60 panel
(`docs/dev/reviews/2026-09-17-r60-opt-dial-design.md`) rule this shape.

**H5 — the `requires module` phrase in `src/parse/registry.c` (roughly
14 spellings in comments and row data).** **HELD: this is the ruled
central home, not duplication.** `internal.h:2707-2714`'s `RegDiag`
makes the doorway's rendering a data dispatch, and most of `registry.c`'s
occurrences are comments *describing* what a row renders. F4 is
deliberately scoped to the 20 sites *outside* this mechanism.

**H6 — `"core/internal.h"` (47 `#include`s), `"gen/enc/enc.h"` (12),
`"parse/parse_mods.h"` (9), `"core/limits.def"` (8), `"pcrec.h"` (7).**
The rollup's highest-`distinct_files` rows. **HELD: these are include
directives.** They are the dependency graph, and they are lens 6's
deliverable, not a string-duplication finding.

**H7 — single- and two-character literals (`'('`, `'{'`, `'^'`, `'\\'`,
`'0'`, `'9'`, `'a'`, `'A'`, ~50 rows totalling well over 600
occurrences, concentrated in `parse.c`, `registry.c`, `ext.c` and the
`mod_*.c` files).** **HELD: they are the grammar.** Naming `'('` as
`GROUP_OPEN` would make the parser harder to check against PCRE2's
syntax page, which is the one comparison the compatibility standard
(D26) makes constantly. Held as a class, deliberately, per §1.

**H8 — emitted-C fragment strings (`"    }\n"` ×30, `"{\n"` ×33,
`" *\n"` ×43, `"typedef struct {\n"` ×6, and ~40 similar).** **HELD:
out of this lens's scope and arguably out of the review's.** The scope
tiers exclude emitted C as *generated text*; these are the emitter's
fragments of it. They are, however, the single clearest evidence for
**lens 2 / lens 10**'s thesis (the tree carries multiple text-emission
mechanisms and no shared kit), and I am recording them here so the
synthesis can route them there rather than dropping them: `" *\n"` at 43
occurrences across 4 files is a comment-block continuation being
hand-spelled, which a one-line `sb_comment_line()` primitive removes
entirely.

**H9 — `PREMUL_DEAD 65535` (`emit_dfa.c:2386`).** Superficially a magic
number, and it coincides with `PCREC_MAX_REPEAT`'s own 65535. **HELD:
unrelated.** It is the premultiplied table's dead-state sentinel — the
largest value a `uint16_t` cell can hold — not a limit on anything a
pattern can exceed. Joining it to the repeat ceiling would be a false
abstraction.

---

## 4. RANKING (per A4 — MECHANICAL + safe first)

| # | finding | severity | effort | recommended wave |
|---|---|---|---|---|
| F3 | FNV constants open-coded ×9 | MAINTAINABILITY | MECHANICAL | pre-tour cleanup |
| F5 | `"missing closing ) for group"` ×8 + the stale comment | MAINTAINABILITY | MECHANICAL | pre-tour cleanup |
| F2 | `[ART-SIZE]` bar/threshold split homes | MAINTAINABILITY | MECHANICAL | pre-tour cleanup (or one clause + allowlist line) |
| F4 | `requires module` ×20 outside the ruled home | MAINTAINABILITY | LOCAL | a wave of its own, or fold into F5 |
| F1 | D90 detector keyed on the name | MAINTAINABILITY | LOCAL | check-side wave; carries its own sabotage row |
| F7 | emitted identifiers as free strings | POLISH | MECHANICAL | ride lens 10's emission-kit wave |
| F6 | 94 unnamed scratch-buffer sizes | CORRECTNESS-RISK (latent) | CROSS-CUTTING | its own audit slice — it is a bug hunt, not a cleanup |

F6 is last by effort and first by severity; it is deliberately not
bundled with the others, because the product of that slice is a table of
answers and a bug list, not a diff.
