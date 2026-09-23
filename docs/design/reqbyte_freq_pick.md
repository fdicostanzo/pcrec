# `[OPT-REQBYTE]`'s PICK — a byte-frequency prior chooses which necessary byte the pre-check tests

**`[OPTLOOP.2]` cycle-2 design note, lane `c2design`, 2026-09-22.** Design
only: nothing under `src/`, `cli/`, `lib/` or `tests/` changed in the delivery
that carries this note, no mechanism is built, and no clock was read anywhere.
Every number below is a COUNT, taken on this Mac from committed artifacts
(`docs/dev/optloop/c2/reqpos_census.tsv`, `c2/subject_freq.json`) and from the
shipped source. Ratification and a D6 panel are owed before any implementation
lane opens.

---

## 0. Read this first — three findings, of which two change the note's shape

1. **THE STATIC PRIOR ALREADY SHIPS, AND IT IS ALREADY THIS MECHANISM'S
   INTENDED HOOK.** `src/opt/prefix_k.c:91` holds a normalised 256-entry
   parts-per-million byte-frequency table behind `pcrec_byte_freq_ppm`, with
   `[OPT-OFSK]`'s selection as its first consumer, a structural check on its
   sum (`tests/codegen/run_offset_skip.sh` §1 asserts 1,000,000), and a header
   that names D83's findings file as the replacement for *this one function*
   and nothing else. So this note proposes **a second CALL to a shipped
   accessor**, not a new interface, not a new table, and not a findings-file
   dependency. `firstset_design.md` §5.2's proposed
   `double pcrec_findings_density(const Ctx *, const unsigned char[32])` is a
   parallel mechanism to it and additionally violates the tree's own stated
   integer rule; §2.3 argues the widening instead.

2. **THE SHIPPED PRIOR DELIVERS ALL THREE OF THE CENSUS'S WHOLE-CALL WINS WITH
   NO FINDINGS FILE.** Argmin over the necessary set under
   `byte_freq_ppm_tbl`, ties broken by today's rule, moves
   `nested-comment-rec` `/`→`*`, `wild-validator-email-owasp` `.`→`@` and
   `wild-waf-crs-942500-comment-obfuscation` `/`→`*` — the exact three
   `reqpos_census.md` §5 names, each going from a byte PRESENT in `t-1m` to
   one ABSENT from it. The findings file is a later widening of an already
   paying mechanism, not its precondition.

3. **AND THE PRIOR'S ORDERING AGREES WITH THE BENCH SUBJECT ON EVERY MOVER,
   12 OF 12** (§3.3): of the twelve `capability` patterns whose pick moves,
   eleven move to a byte that is STRICTLY RARER in `t-1m` and one moves
   between two bytes that are both absent. Zero move to a commoner byte. That
   is evidence worth its own sentence because the prior was deliberately NOT
   derived from the bench's text (`prefix_k.c`'s own no-shared-source
   discipline, `learnings.md` §3), so this is an out-of-sample agreement and
   not a fit.

**Recommendation, stated once.** Land the pick rule as ONE `abi` event over
the shipped prior, with no findings-file plumbing and no new axis bit. The
population is measured (§3.2: 304 of 2,236 corpus patterns with a necessary
byte, 13.60%) and the landing bar's target cells are named (§6). The findings
file, its name resolution and the static named analyses are a SEPARATE later
row this note deliberately does not open.

---

## 1. The measured need

### 1.1 What batch 1 shipped

`[OPT-REQBYTE]` (`src/opt/reqbyte.c`, merged `3aa13b6b`) derives the SET of
bytes every match must contain and emits **the rightmost member**, matching
PCRE2's `PCRE2_INFO_LASTCODEUNIT` choice. The file's own header states the
reason for the rule: so that a later multi-byte form is a WIDENING of this
mechanism and not a different one. That reason is about the SET; it says
nothing about which member serves a subject best, and the header does not
claim otherwise — `rb_intersect`'s fallback ("the largest surviving byte") is
already an admitted arbitrary tiebreak.

### 1.2 What the rightmost rule costs, measured

`reqpos_census.md` §5: of the 36 `capability` patterns with a necessary byte,
**14 have a rarer necessary byte than the one the rule picks**, and on three
of them the rarer byte is ABSENT from the bench throughput subject while the
picked byte is PRESENT:

| pattern | picked (rightmost) | hits in `t-1m` | rarest necessary | hits |
|---|---|---|---|---|
| `nested-comment-rec` | `/` | 30,000 | `*` | **0** |
| `wild-validator-email-owasp` | `.` | 14,826 | `@` | **0** |
| `wild-waf-crs-942500-comment-obfuscation` | `/` | 30,000 | `*` | **0** |

On those three the shipped pre-check **cannot fire at all**: its `memchr`
succeeds, the pre-check falls through, and the whole find-all call runs the
attempt loop it was built to skip. A pick that chose the absent member would
answer the entire call in one `memchr`-class pass at the
0.0168 ns/byte floor three engines share and pcrec already reaches
(`cycle1_analysis.md` §2.2, its own `floor-byte` control).

### 1.3 The need is smaller than "three rows", and the note says so

Only **one** of the three is a cycle-1 LOSING cell. Joined against
`cycle1_rows.tsv`:

| pattern | regime | rank | score | ratio to its algorithmic target |
|---|---|---|---|---|
| `nested-comment-rec` | throughput | 9 | 0.2972 | 5.1981 |
| `nested-comment-rec` | search | 20 | 0.1322 | 2.0815 |
| `wild-waf-crs-942500-comment-obfuscation` | throughput | 53 | 0.0000 | 0.5605 |
| `wild-validator-email-owasp` | throughput | 75 | 0.0000 | 0.3674 |

`email-owasp` and `crs-942500` are rows pcrec already WINS. They get faster
and they move no bar. **The D119 improve population is `nested-comment-rec`'s
two cells, 0.4294 of the losing matrix's 10.284** — and that is the honest
figure this mechanism is priced at, not the census's "three whole-call
answers", which counted wins and losses together. §6 is built on it.

### 1.4 A second measured need the census did not frame as one

`reqpos_census.md` §4's own counter-example is also a pick-rule customer.
`logparse-atomic`'s necessary run is `": "`, whose gain as a PAIR filter is
**1.00×** — the space always follows the colon in this text. But its picked
byte today is the SPACE (121,963 hits in 1 MiB), and the prior picks the COLON
(9,070 hits): a **13.4× reduction in the pre-check's own first-hit distance**
from the pick rule alone, on a pattern where the pair extension buys nothing.
This matters beyond the row: §2 of `reqpos_2b.md` shows the run form's
per-candidate cost is bounded by A's density, so **the pick rule is a
precondition for tier 2b's cost story**, not an independent nicety.

---

## 2. Where the frequency comes from

### 2.1 It comes from `pcrec_byte_freq_ppm`, which ships

```
src/opt/prefix_k.c:91    static const unsigned byte_freq_ppm_tbl[256]
src/opt/prefix_k.c:125   unsigned pcrec_byte_freq_ppm(int b)
src/opt/prefix_k.c:135   unsigned pcrec_byte_freq_total_ppm(void)
src/core/internal.h:1488 the two declarations
```

The table's own header states its provenance and its discipline, and all of it
binds this note:

* **The mass is assigned from two independent, citable priors** — the
  classical English letter-frequency ordering, and the structural punctuation
  of machine-written lines raised above its prose frequency — **deliberately
  NOT from the comparative bench's own log text**, because that would be a
  control sharing a source with what it controls (`learnings.md` §3). This is
  what makes §3.3's 12-of-12 agreement out-of-sample.
* **Every byte has a floor of 2 ppm rather than zero**, so the model can never
  believe a byte is impossible. The pick rule inherits that: it can select a
  byte the subject never contains, which is the WIN case, but it can never
  conclude that a byte cannot occur.
* **Integers in ppm, not doubles**, "because the selection must be
  bit-reproducible across boxes, which is the same reason nothing else in this
  compiler computes in floating point."
* **The sum is a checkable fact** (1,000,000), asserted by
  `run_offset_skip.sh` §1, which this note re-verified by parsing the shipped
  array and summing it.
* **"THE TABLE IS A PRIOR AND NOT A PROMISE. It orders bytes; it does not
  predict any particular subject. Everything downstream of it is an
  ANSWER-IDENTITY-preserving choice, so a badly-fitted prior costs speed on
  some input and can never cost a match."** That sentence is this mechanism's
  whole soundness argument, already written, one file over.

### 2.2 The D83 story, stated precisely

D83 rules that exemplar analysis happens OUTSIDE pcrec and arrives as a
FINDINGS FILE; its 2026-09-22 addendum rules that the file is a set of NAMED
ANALYSIS VALUES with `freq` as the first value, that a set of static named
analyses (`html`, `tsv`, `json`, `log`, `prose`, …) ships, and that the
consumer interface is therefore the DEFAULT path rather than an expert path.
`prefix_k.c`'s header already implements the last clause in the smallest
possible way: the static table IS the profile-less default, and "adopting a
findings file is a second implementation of THIS ONE FUNCTION and touches
nothing else."

`firstset_design.md` §5.1 is correct that the FORMAT ships
(`src/parse/rxt_schema.def:146`, a `FILE`-scope `freq <name>` TOKEN row with a
`DATA` body of `question`/`reader`/`analyzer`/`row`/`provenance`, a
`--list-schema` row and a spec section in `docs/spec/rxt_format.md`). It
understates what is open. Verified on this tree, **three things are missing,
not one**:

1. **name resolution** — `analysis <list>` at `CONFIG` scope
   (`rxt_schema.def:172`) parses and `src/parse/rxt_source.c:2756` `continue`s
   on it with the comment "resolution is §2.10's and is not this step's";
2. **a `row` reader** — nothing in the tree turns a `freq` block's `row` lines
   into a table. The schema declares the shape; no consumer exists;
3. **a CLI surface** — a `--pattern` compile never reads a `.rxt` file at all,
   so a caller outside the `--source` path has no way to name a findings file
   or a static analysis. D83 anticipates this ("`--exemplar FILE` … takes the
   FINDINGS file, never the raw text") and nothing implements it.

**None of the three is on this mechanism's critical path**, which is the
point of §0 finding 2. They belong to a findings-file row of their own, with
D83 addendum item (4)'s open design consideration (resolve a named analysis
through the `-I` library path the way `include`/`lib` resolve, rather than a
parallel lookup) as its first question.

### 2.3 The accessor: widen the shipped one, do not mint a second

`firstset_design.md` §5.2 proposes

```
    double pcrec_findings_density(const Ctx *cx, const unsigned char set[32]);
```

**This note declines that signature and recommends the existing function
instead**, for three reasons, each of which is a rule this tree already holds:

* `double` contradicts `prefix_k.c`'s stated integer rule verbatim, and
  bit-reproducibility across boxes is not negotiable for a value that selects
  an emitted byte. The unit is already `unsigned` ppm.
* A second function over the same table is a parallel mechanism (memory
  `pcrec-general-mechanisms-not-special-cases`); `prefix_k.c` already carries
  a private set-summing helper, `set_ppm` (`prefix_k.c:302`, "Sums
  `pcrec_byte_freq_ppm` over every set byte in `set`, capped at 1,000,000").
  If a set-grain accessor is wanted, the change is to **publish `set_ppm`**,
  not to write a second one with a different type and a different bound.
* This mechanism does not want a set-grain density at all. It wants an
  ARGMIN over the members of a set, which is a per-byte question:
  `pcrec_byte_freq_ppm(b)` called once per member, over a set of measured
  median size 2. The `Ctx *` parameter buys nothing today and is exactly the
  parameter a later findings file would add — so it is added THEN, in the one
  function D83's hook already names, with one call site to update.

**When a findings file lands, the change is `pcrec_byte_freq_ppm`'s body plus
a `Ctx` (or a findings handle) parameter, and every consumer — `[OPT-OFSK]`'s
selection, this pick, `[OPT-4]`'s collapse decision — moves with it in one
edit.** That is the property D83's header claims and this note preserves.

---

## 3. The pick rule

### 3.1 The rule

> **Among the members of the necessary set, choose the one with the lowest
> `pcrec_byte_freq_ppm`. On a tie, choose the member today's rule would have
> picked if it is among the minima; otherwise the largest such byte value.**

Three properties, and the second is why it is safe to land:

* **It is one function's return value.** `rb_walk`, `rb_union`,
  `rb_intersect` and every node arm are untouched: the set and its threaded
  `pick` are computed exactly as today, and the choice happens once, at
  `pcrec_req_byte`'s single `return` (`reqbyte.c:206-209`). Nothing in the
  walk moves, so no arm's soundness argument is re-opened.
* **UNDER A UNIFORM TABLE IT IS TODAY'S RULE, BYTE FOR BYTE.** Every member
  ties, the tiebreak returns the threaded `pick`, and the emitted byte is
  unchanged on every pattern. So the rule's identity behaviour is a property
  of the TABLE and not of the rule, which is what makes "keep today's answer"
  an available configuration rather than a second code path.
* **Answer identity is preserved by construction, in the strongest sense
  available.** Every member of the set is a byte every match must contain, so
  the `memchr` the emitter writes is sound for any member. The choice cannot
  move an answer; it can only move a speed. This is `prefix_k.c`'s own
  sentence applied here.

The tiebreak's second clause exists because today's `pick` is not always a
member of the minima, and a rule that silently fell back to "whichever bit a
loop found first" is the thing `reqbyte.c`'s header already refuses for
`rb_intersect`.

### 3.2 The population, measured

Computed over `reqpos_census.tsv`'s `set_hex` column (the whole necessary set
per pattern, from a probe cross-checked against batch 1's own landed
`RX_REQ_BYTE` stamp on 63 of 64 bench patterns, 0 disagreements) against the
shipped `byte_freq_ppm_tbl`:

| population | with a necessary byte | with \|S\| ≥ 2 | **pick MOVES** |
|---|---|---|---|
| shipped corpus | 2,236 | 903 (40.4%) | **304 — 13.60%** |
| bench (6 sets) | 131 | 89 (67.9%) | **51 — 38.93%** |

Among movers, the ratio of the old byte's ppm to the new byte's: corpus
median **3.4×**, range 1.11× to 2,492×; bench median 3.3×, range 1.11× to
101×. A pattern with a singleton necessary set can never move, which is
59.6% of the corpus's own population — so the mechanism's reach is bounded
by the alternation/concatenation shapes that produce a set at all.

### 3.3 The direction, on the one subject where it can be checked

For the 12 `capability` movers, both bytes' counts in the bench's 1 MiB
throughput subject (`c2/subject_freq.json`, `t-1m`, 1,048,576 bytes):

| pattern | old → new | old hits | new hits |
|---|---|---|---|
| `nested-comment-rec` | `/` → `*` | 30,000 | **0** |
| `wild-validator-email-owasp` | `.` → `@` | 14,826 | **0** |
| `wild-waf-crs-942500-comment-obfuscation` | `/` → `*` | 30,000 | **0** |
| `logparse-atomic` | ` ` → `:` | 121,963 | 9,070 |
| `logparse-atomic-removed` | ` ` → `:` | 121,963 | 9,070 |
| `file-ext-order` | `r` → `.` | 54,781 | 14,826 |
| `router-prefix-order` | `r` → `/` | 54,781 | 30,000 |
| `wild-semdiv-altorder-foo-foobar-rustregex` | `o` → `f` | 38,684 | 18,853 |
| `wild-semdiv-dollar-trailing-newline-pcre2` | `c` → `b` | 22,334 | 4,973 |
| `codegrammar-flat` | `:` → `"` | 9,070 | 5,950 |
| `codegrammar-xflag` | `:` → `"` | 9,070 | 5,950 |
| `dup-param-detect` | `=` → `&` | 0 | 0 |

**Eleven strictly rarer, one absent→absent, zero commoner.** The last row is
the one that could have gone wrong and did not: `dup-param-detect` is a named
D119 improve cell for batch 1 whose picked `=` is ABSENT from `t-1m`, so a
pick that moved it to a PRESENT byte would have destroyed that cell's
whole-call answer. `&` is absent too, so the cell is unharmed — and that is a
measurement, not a property: **the prior is subject-blind, so an
absent→present move is possible in general and is the mechanism's one real
hazard.** §6.2 makes it a carve-out with a named control rather than an
assumption.

### 3.4 What the rule does NOT do

It does not change the SET, so every decline `reqbyte.c`'s header lists stays
exactly as it is (a multi-member class, a zero-admitting quantifier, a
backreference, a linked call, every assertion, and a lookaround's
un-descended body). It does not change WHERE the check is emitted, its
window, or its `<=` guard. It does not read a subject. It does not look at
positions — that is `reqpos_2b.md`'s territory and shares nothing with this
but the walk.

---

## 4. The `abi` question

**Yes, and it is a plain one.** The emitted `memchr`'s decimal argument and
the `<PREFIX>_REQ_BYTE` stamp both move on 13.60% of the corpus, so this is a
`abi` **29 → 30** bump carrying the whole D76/D94 ritual in one commit.
Three things about the ritual specifically:

* **No new scaffolding.** No line is added, removed or re-laid-out: one
  decimal inside an existing `memchr` call and one stamp value change, both
  written by `pcrec_emit_req_byte_check` (`emit_dfa.c:660`) and the stamp
  block at `emit_dfa.c:7637-7652` from the SAME `Job.req_byte` field. The
  comment above the check carries the byte too (`emit_dfa.c:667-670`) and
  moves with it. So the diff per moved artifact is three digits in three
  places, and the population is a count.
* **The site list is EVERY READER OF THE NUMBER, FOUND BY GREP** (D94),
  and this change has the SECOND READER CLASS in force
  (`battriage_report.md`; `evtriage3_report.md` §; `optimpl1_report.md` §0):
  a manifest row that cites no abi digit can still pin a byte COUNT that
  moves. `tests/codegen/run_cpset_structure.sh` CHECK 3's twelve
  `EMITTED_BYTES` rows and `tests/resource/run_resource_tests.sh`'s rescue
  pin are the two batch 1 had to re-measure, and a moved byte VALUE is
  same-length in almost every case here (a one-digit-to-three-digit move,
  e.g. `47` → `42`, is same-length; `0` → `100` is not) — so the pins must be
  **re-measured by recompiling the witnesses**, never predicted from the
  digit count. **And the witnesses must be compiled to the SAME `-o` basename
  as the check uses**, this house's four-times-recorded trap.
* **Do not name a "declined" sentinel.** `REQ_BYTE`'s `"none"` member already
  exists for the reason 0 is a legal byte, and the pick rule needs no second
  sentinel. Nothing in the stamp's vocabulary changes.

**Should the stamp name the pick SOURCE?** This note recommends **no**, for
D77's reason and one structural one. The reason to want it is a reader asking
"was this byte chosen by the rightmost rule or by a prior?" — but with the
pick rule landed, the answer is *always* "by the prior", and a stamp whose
value is constant carries no information. It becomes a real question only when
a findings file can supply a second table, and then the fact a reader wants is
**which analysis was attached**, which is that row's stamp and not this one's.
`ccdiff1_report.md`'s `RX_VM_INLINE_CHAIN` ruling is the precedent: a stamp
that would carry another stamp's value by construction does not ship.

---

## 5. The axis and the identity story

### 5.1 No new axis bit, and the reason is not frugality

`-fno-req-byte` / `PCREC_NO_REQ_BYTE` (bit 30, `src/core/axes.def:158`)
already denies the mechanism, and this change is **which member of a set the
mechanism tests** — a VALUE under an existing axis, not a second mechanism.
The tree has explicit precedent for that shape: `--unroll=K` is documented as
"the counter rung's value parameter" (`tuning.md` §2.10) and
`--vm-entry-shape=N` as an ORDINAL rung (§2.21), neither holding a deny bit of
its own.

D119 rule 5 ("EVERY MECHANISM IS AN AXIS") is satisfied by bit 30: the
mechanism it names is the pre-check, the deny flag exists, the answer-identity
sweep covers it, and S265 is its sabotage row. Minting `PCREC_NO_FREQ_PICK`
would assert that the pick is a separate mechanism, which is the special-case
shape memory `pcrec-general-mechanisms-not-special-cases` refuses.

**Two costs of minting one, recorded because they are real.** Bit 30 is the
LAST member of `lib/pcrec.h`'s flags enum and the constants are spelled
`1u << N`; bit 31 is the only remaining bit spellable that way, and `1u << 32`
is undefined behaviour, so the next axis after one more forces a move to
`1ull <<` — which reaches `tests/registry/axes_registry_check.sh`, whose bit
table is DERIVED by grepping the header's `PCREC_(NO|FORCE)_` spellings
(`evtriage`/`emitverb` found that convention encoded in a check). The storage
is fine (`pcrec_options.flags` is `uint64_t`); the SPELLING is what moves.
Spending the second-to-last cheap bit on a tiebreak is worth stating, not
worth hiding.

### 5.2 How `make test-axes` and the identity gates cover it

* **`make test-axes`** sweeps `-fno-req-byte` denied/forced for
  answer-identity over the whole corpus. The pick rule is answer-identity
  preserving by construction (§3.1), so the sweep's verdict on the changed
  arm must be IDENTICAL to its verdict today — a test whose passing is
  evidence of nothing new, and the note says so rather than claiming coverage
  it does not get. On darwin sweep only this axis (`AXES="-fno-req-byte"`),
  verified against `tests/axes/run_axes.sh`'s own spelling before citing it;
  the whole table is multi-hour.
* **The four `.c` byte-identity gates and `scripts/emit_sweep.py`** are the
  instruments that DO see this: 304 corpus artifacts move, which is a
  positive control the abi bump owes anyway. Run the sweep against the branch
  point and confirm the mover set equals the predicted set — not just its
  size. §7 names it as the acceptance measurement.
* **`tests/codegen/run_prechecks.sh` §3** is batch 1's gate and already holds
  the right shape: it asserts the `memchr`'s SENSE separately from its
  ARGUMENT, because S265 inverts the sense and leaves the byte alone. The
  pick rule moves the ARGUMENT, so **the two assertions stay independent and
  §3's sense arm needs no change** — which is the gate's own design paying
  off. What it owes is one new arm.

### 5.3 The new arm, and its sabotage row

**The arm.** Assert, on a fixture whose necessary set has ≥ 2 members of
known differing ppm, that the emitted `memchr` argument is the MINIMUM-ppm
member — with the expected byte written as a LITERAL in the check, derived by
hand from the shipped table and not by calling `pcrec_byte_freq_ppm`. A check
that recomputed the rule from the table would share a source with what it
controls (`learnings.md` §3) and would pass under any table at all. The
fixture set must include at least one pattern where the minimum is NOT the
rightmost (so the arm discriminates) and one where it IS (so a rule that
always returned the largest byte fails too) — a both-directions population,
`w231_report.md`'s two-directional lesson.

**The sabotage row (S266 or the next free id on main at the time).** Plant
`argmax` where the rule says `argmin`. Detected by the arm above; NOT detected
by any answer check anywhere, because every member is sound. That is worth
stating in `SAB_DESC`: this row's whole detector is one structural arm, and if
that arm goes vacuous the plant is invisible. `optimpl1_report.md` §0's
observation — two of batch 1's three mechanisms have no answer-level detector
in the tree — extends to this one, and for the same structural reason.

**Do NOT give the row a population FLOOR derived from the same table**; pin
the fixture set by NAME, with an assertion that each named fixture's set has
≥ 2 members, so an extraction that stopped finding sets fails rather than
reading green on an empty population (`w233_report.md`'s wave-tier zero).

---

## 6. The landing bar and its cells

### 6.1 Improve

D119 rule 4: the target cells' median improvement must exceed their IQR.
**The target cells are `nested-comment-rec`'s two, and they are the only ones
in the losing matrix (§1.3).**

| cell | rank | score | ratio to algorithmic target | expected effect |
|---|---|---|---|---|
| `nested-comment-rec`, `large-subject-throughput` | 9 | 0.2972 | 5.1981 vs `onig` | `/` (30,000 hits) → `*` (0): the whole find-all call becomes one `memchr` pass |
| `nested-comment-rec`, `short-subject-search` | 20 | 0.1322 | 2.0815 vs `onig` | one `memchr` over each of 75 short subjects |

`nested-comment-rec` is `(/\*(?:[^*/]|\*(?!/)|/(?!\*)|(?1))*\*/)` — a
`recursion`-module pattern, engine `vm`, `RX_VM_PREFILTER "none"`, so the VM
walks every start position today and the pre-check is its only whole-window
filter. The throughput cell's expected gain is the largest this note can
claim and it is a STEP, not a percentage: an absent byte answers the call
without entering the attempt loop at all.

Two effects are gains and are NOT bar cells, because both rows already win:
`wild-validator-email-owasp` throughput (`.`→`@`, 14,826→0) and
`wild-waf-crs-942500-comment-obfuscation` throughput (`/`→`*`, 30,000→0).

### 6.2 Do not regress — and the carve-out that matters

| cell | why it is a carve-out |
|---|---|
| `dup-param-detect`, throughput | **THE ONE THAT COULD BREAK.** A batch-1 improve cell whose picked `=` is ABSENT from `t-1m`; the rule moves it to `&`, also absent, so the whole-call answer survives. MEASURED (§3.3), not assumed |
| `tag-depth3-bound`, `tag-pair-match`, `wild-secrets-username-password-pair`, `wild-logparse-winpath-grok` | batch 1's other four improve cells. **None moves** — `tag-depth3-bound`'s set `{<, >, /}` ties at 332 ppm between `<` and `>` and the tiebreak keeps `>`; the others are singletons or already minimal |
| `floor-byte`, throughput and search | the floor control. Single literal `~`, singleton set, cannot move. Its emitted text must be byte-identical |
| `router-prefix-order`, throughput | rank 12, score 0.2258. MOVES `r`→`/` (54,781→30,000): fewer candidate hits, both present. **This cell has already lost its byte-identity control status** (`optimpl1_report.md` §0: batch 1 falsified the plan row's claim that it is byte-identical), so it is a speed carve-out only |
| `wild-secrets-github-pat`, `wild-validator-uuid-grok`, `float-literal-bound` | batch 1's remaining "byte present, pre-check is pure cost" carve-outs. None appears in the mover set |

**The general hazard, stated once so an implementation lane cannot miss it.**
The prior is subject-blind. On a subject whose distribution differs from
`byte_freq_ppm_tbl`'s, the rule can move a pick from a byte that is ABSENT to
one that is PRESENT, turning a one-pass answer into a full attempt loop. The
`capability` set contains zero instances (§3.3) and that is luck plus a
well-ordered prior, not a theorem. **The acceptance measurement is therefore
not just "the target cells improve" but "no cell's picked byte goes from
absent to present"**, which is a COUNT over the bench's own subjects and is
checkable before any timing run (§7 item 2).

### 6.3 Size

Zero. No line is added or removed on any artifact; the emitted decimal changes
width by at most two characters per occurrence, three occurrences per
artifact. The size ratchet
(`docs/dev/artifact_size_log.tsv`, `tests/size/check_size_tripwire.sh`) will
see sub-byte-scale movement and its unpinned-max guard is not at risk — but
the log regenerates on any full `test-corpus` run and its diff should be read
rather than assumed, `scripts/size_diff` being the reader.

---

## 7. The D77 measurements this note's landing rests on

Named, in the order they must happen, because D77 requires each build to name
the measurement that triggers it:

1. **The corpus mover set, by identity sweep, not by prediction** (darwin,
   free). `scripts/emit_sweep.py --ref <branch point>` over all five streams.
   ACCEPTANCE: the mover set is exactly the 304 patterns §3.2 predicts —
   compared as a SET of pattern ids, never as a count, because two errors in
   opposite directions cancel in a count (`dialdesign_report.md` §3's K45
   lesson). A disagreement here is a probe/compiler divergence and must be
   resolved before anything else.
2. **The absent→present sweep over the bench's own subjects** (darwin, free).
   For every `capability`, `syntax`, `altwide`, `loglines`, `email` and
   `bounded` pattern, count the old and new picked byte in that set's OWN
   subjects — `reqpos_census.md` §7 already records that §4's `syntax` and
   `altwide` numbers were taken against the wrong text, so this sweep must
   pair each set with its own manifest. ACCEPTANCE: zero absent→present
   moves. A non-zero result is not a blocker but it names the carve-out cells
   before the bench measures them.
3. **The bench cells, on Linux, through the executor** (D119's landing bar).
   `nested-comment-rec` throughput and search, plus every §6.2 carve-out,
   at the shipped default `auto-caps` and at the variants `cycle1_caps_view.md`
   ranks. ACCEPTANCE: median gain on the two target cells exceeds their IQR;
   no carve-out regresses by more than its IQR.
4. **NOT owed, and named so nobody waits for it**: nothing here needs a
   findings file, a name resolution, a static named analysis, or
   `firstset_design.md` §7's `json-constant` re-run. This mechanism is
   independent of `[OPT-FIRSTSET]`'s verdict in both directions.

---

## 8. The four design lenses

**Specific vs general.** General, and it removes a special case rather than
adding one. The necessary SET is what the analysis already produces; today's
emitter picks a member by a positional accident of the walk, and this replaces
that with a stated cost criterion. It introduces no per-pattern clause, no
construct-specific arm and no new mechanism — `reqbyte.c`'s node switch is
untouched.

**Core vs derived.** It changes only the derived half. The core fact is "these
bytes are necessary"; the pick is a selection over it, and the selection's
input (`byte_freq_ppm_tbl`) is itself a shipped core datum with an existing
consumer. The one core-adjacent thing it touches is a DOCUMENTED PROPERTY: two
documents state that the emitted byte IS PCRE2's `LASTCODEUNIT`
(`reqbyte.c:39-46`, `tuning.md` §2.27), and after this change the emitted byte
is a member of a set PCRE2's rule also draws from but no longer PCRE2's own
choice. That is a spec hunk (D80), and the reason the old rule was chosen — a
later multi-byte form is a widening — is preserved intact, because the widening
is about the SET.

**Applicable vs assumption-changing.** Applicable. Answer identity holds by
construction, every existing decline stands, the emitter's shape and window
are unchanged, and `prefix_k.c`'s own sentence ("a badly-fitted prior costs
speed on some input and can never cost a match") is already the tree's ruling
on exactly this trade. The one assumption that does move is a PERFORMANCE
assumption in the unsound-for-speed direction — §6.2's absent→present
hazard — and it is made a measured carve-out rather than an argued one.

**Fits the architecture vs needs a refactor.** Fits, at the smallest scale
this cycle has produced: one function's return statement, one second call to
an existing accessor, one new check arm, one sabotage row, one `abi` bump, one
spec hunk. No new file, no new field in `Job`, no new stamp, no new axis, no
emitter change. If a findings file later replaces the table, that is one
function's body and the consumers move with it — the property D83's hook was
designed to give and this note does not spend.

---

## 9. Open questions for Frank

1. **Does the pick rule ship over the SHIPPED static prior now, or wait for a
   findings file?** (This note recommends now: §0 finding 2 — the prior
   already delivers all three whole-call wins, and waiting buys nothing.)
2. **Is `13.60% of the corpus moving its emitted byte` an acceptable `abi`
   29 → 30 event for a mechanism whose measured bar population is two cells?**
   (Recommend yes: memory `pcrec-abi-changes-pre-release`, and the bump's
   ritual cost is the same at 1 artifact as at 304.)
3. **`PCREC_NO_FREQ_PICK` — mint the bit, or keep the pick a value under
   `-fno-req-byte`?** (Recommend the latter: §5.1, plus bit 31 is the last
   `1u <<` bit.)
4. **Should `tuning.md` §2.27's "matching PCRE2's own choice" sentence be
   replaced or kept with an exception?** (Recommend replaced: after this
   change the rightmost rule survives only as a TIEBREAK, and a spec sentence
   that describes a tiebreak as the rule is the drift D80 exists to prevent.)
5. **Does the findings-file row get opened as its own plan row now**, carrying
   name resolution, the `row` reader, the CLI surface and D83 addendum (4)'s
   `-I` question — or does it wait for a second consumer to ask? (Recommend
   waiting: D77, and this mechanism is the second consumer already served by
   the fallback.)
6. **Is the absent→present hazard (§6.2) acceptable as a measured carve-out**,
   or does it want a guard — e.g. "never move a pick whose ppm is already
   below a floor"? (Recommend no guard: a guard would be a threshold with no
   measurement behind it, D77, and the sweep in §7 item 2 answers the question
   the guard would be insuring against.)
