# R13 — 2026-08-11 — a five-lens DESIGN panel on the extension mechanism (docs/extension_design.md)

**Nothing was built.** Five lenses, one primary question each — the narrow-brief
format R11 measured and R12 confirmed. **All five delivered, all five after a
second prod, and the second prods are where most of the value was:** C4 went
168 → 1003 lines, C5 87 → 721, C2 57 → 454. Budget for two rounds; the first
round is not the panel.

**Outcome: the design was partly refuted.** Eight load-bearing claims fell,
four of them to independent measurement by more than one critic. One live
shipped bug was found (K13). The document was corrected in place rather than
rewritten, and the holes the refutations left are marked `[OPEN]` rather than
filled — filling them at the desk, unreviewed, is the mistake the panel had
just caught.

Read alongside `docs/extension_design.md` (which now carries the corrections
inline) and D33.

## The panel

| | lens | primary question |
|---|---|---|
| C1 | the seam | does the three-level ASK contract hold at all four doorways? |
| C2 | toggles | is "recognition never depends on what is enabled" achievable for all 16 features? |
| C3 | shape/endpoint | is the range-endpoint rule correct over the whole construct space? |
| C4 | the checks | which of the ten checks takes its scope/oracle/input from what it checks? |
| C5 | spec-first (D27) | where does the design fail its own §1 obligations? |

Roughly 61 findings across ~3,370 lines. The author verified every live-defect
claim and every load-bearing measurement independently before acting on it.

---

## The four refutations that more than one critic reached independently

**1. Selection is NOT position-independent** — C1/F1, C3/F5+F9, C4/F19, C5/F2.
Four critics, three different routes. The measurement:

    (a)x12 \12     matches "a"x12 + "a"     -> BACKREFERENCE 12
    (a)x12 [\12]   matches "a"x12 + "\n"    -> STILL OCTAL 012

Same capture count, same bytes, different construct — so the winning row differs
by position, and recognition must be per-port. C3 widened it to **114 of 168
(digit-run, capture-count) cells, with the split starting at k = 0**.

**The methodological lesson is sharper than the finding.** The design's evidence
for position-independence was three `\N` probes — and all three are REFUSALS at
class position, so "same row, then the port refuses" and "a different row wins"
are indistinguishable on that data. *The claim was measured on the only bucket
that could not test it.*

**2. `\Q...\E` is representable by nothing in the design** — C1/F3, C3/F3,
C2/F5, C5/F3. Four critics. It is transparent at a range endpoint
(`[0-\Q\Ea]` compiles, endpoint `a`), it contributes an endpoint AND further
members (`[0-\Qzz\E]`), and the natural `EXT_NODE` reading is a **tier-1
miscompile**:

    ^\Qab\E*$  vs "abbb"    MATCHES
    ^\Qab\E*$  vs "ababab"  does NOT match

A quantifier binds the LAST character of a quoted run. `\Q` and `\E` are shipped
registry rows, not future constructs.

**3. The endpoint rule is decided by the DOORWAY, not by a shape column** —
C3/F1. Hold shape fixed at SET and vary the doorway:

    [0-[:foo:]]   150      [0-\p{Foo}]   147      [0-\p]   146      [0-\p{L}]  150

The design predicted 150 for all four. The escape doorway decodes in full first
and any decoding error wins; the bracket doorway never validates the name. **The
design's justifying contrast varied two things at once and credited the wrong
one.**

**4. `\b`'s two facets have different owners** — the author (C0/S1) and C5/F1,
independently. `\b`'s row carries feature `assertions`, but inside a class `\b`
is base grammar (backspace). Gating the row gates both facets and breaks `[\b]`,
which pcrec compiles correctly today. **C5 found the worse half the author had
missed:** the shared generic wrapper would make `a\bb` compile to a matcher for
`a\x08b` — a tier-1 miscompile invisible to the byte-identity run, and check 8
*certifies* it rather than catching it.

---

## The single most useful finding

**C2/F3.** The design condemns "the guard is the unimplemented-ness" twice — at
K12 (§6) and by citing `plan.md:577` on `(?xx)[a- ]` — and then commits the
identical error in §10.6, defending its whole-pattern pre-scan with *"pcrec
never says 'reference to non-existent subpattern' because it refuses `\1..\9`
with a module name first."* That is true only while `backrefs` is disabled, and
the mechanism's entire purpose is to enable features one at a time.

    \1(a)      OK        \1(?n)(a)   err 115     \1(?#()   err 115
    \1\Q(a)\E  err 115   \1(?|(a))   OK

`\1`'s validity at offset 0 depends on constructs owned by `modifiers`,
`comments`, `quoting` and `branch-reset` appearing LATER. So the pre-scan needs
live lexer code for DISABLED features — which contradicts the design's own
framing and means `backrefs` cannot land alone.

**Being able to name a failure mode twice in a document and then commit it in
the same document is worth more than the finding itself.**

---

## The live bug: K13

C4/F21 and C3/F6, reproduced by the author before recording. Twelve rows — the
ten digit rows plus `\g` and `\k` — answer the class position with module
`backrefs` for constructs that module can never implement:

    [\8]  matches "8" (literal)    [\k] matches "k"    [0-\k] is a range 0x30..0x6b

Three distinct wrongnesses behind one message. Recorded as K13, with K10's
warning attached: **do not re-attribute the rows without an in-class sweep that
carries a TAIL.** Every net misses it for K10's reasons, including the same
one-byte `"[\\%c]"` template.

---

## The checks did worst of all

C4 produced 26 findings against ten checks. The two that matter most are both
the K10 shape the design cites as its own template:

- **Check 4 is vacuous for ~90 of 100 rows.** Most rows' recogniser *is*
  "compare the first byte to `row->sel`"; the check asks that function whether
  it returns NOT_MINE when the byte differs from `row->sel`. It cannot fail for
  any value of `sel`, right or wrong. Real population ~10, printed population
  ~90.
- **Check 4's scope is the field it validates.** A row escapes by declaring
  `REG_SEL_ANY` — and `RK_VERB` has exactly one row, which *is* `REG_SEL_ANY`,
  so that bucket's coverage is permanently zero, at the doorway the design
  admits it cannot reason about.
- **Check 6's input set is empty today and stays empty at landing**, because the
  acceptance bar is byte-identity with every name disabled. It is the only check
  of the invariant the design calls load-bearing.

**Disposition: §8 is to be rebuilt by someone denied the design's reasoning.**
The density of scope-inheritance defects across ten checks is the signature of
one author writing both a mechanism and its controls — which is exactly what
D27 exists to break, and this panel is the second measurement that it works.

---

## What survived

Worth stating plainly, because a panel this negative reads as a rejection and it
is not:

- **one table, one row per construct** — nobody attacked it successfully, and
  the two-table alternative's K10 hazard stands;
- **names as the unit of enable/disable**, and the measured fact that they are
  already half-built (`FEAT_*` is a 16-bit mask, 100 rows carry exactly one bit
  or zero, `classes` spans 3 buckets and `backrefs` 2);
- **two ports per row**, strengthened by the refutations rather than weakened —
  per-port recognition and per-port feature names are what several findings
  converge on;
- **the shared generic wrapper and data-driven class ports** (§4.2), untouched;
- **RECOGNISE-then-PRODUCE as an idea**, though not the three levels as drawn.

## Negative results, recorded so they are not re-derived

- **`unicode-props` / `classes` coupling is exactly ZERO** (C2/F1, 8,716,400
  compile pairs). The design's own worry list named the wrong pair.
- **`PCRE2_UTF` changes 0 of 120,099 verdicts** (C2/F4), independently
  reproducing R10 with a different generator.
- **At the class-bracket doorway the endpoint rule is EXACTLY right** — 21,396
  generated patterns, zero disagreements (C3/F8). The defect is the
  generalisation to the escape doorway, not SPEC-FA's original rule.
- **`\x` is mode-dependent under ALT_BSUX** (C2/F4) — a base-grammar escape,
  so the mode-dependent set reaches into the base grammar. New information.

## Process notes

- **Second prods delivered most of the panel**, again. Naming which items to
  write first, in order, is what moved C2 from one measurement to six findings.
- **C2 caught its own control error mid-flight** — `(?:)` conflates
  quantifiability with state-setting; `(?i)` does not — and re-ran 8.7M pairs.
  That is the provenance discipline working as intended.
- **C2 and C4 established PCRE2 option bits behaviourally** rather than looking
  them up (sweeping all 32 single-bit options and disambiguating `ALT_BSUX` from
  `PCRE2_LITERAL` by a second probe). Same discipline, same value.
- **The author's own review pass found two of the eight refutations** before the
  panel ran, and got one of them (§5.4's `\b` gate) only half right — C5 found
  the miscompiling half. A self-review is worth doing and is not a substitute.

---

# ADDENDUM — material delivered AFTER the commit

**The R11 rule fired again, and this is the third session running.** Immediately
after committing, `ListAgents` reported *"No reachable agents"* while three
critics went on to deliver **another ~1,000 lines**: C1 583 → 1031, C5 721 →
1126, C2 454 → 643. The agent list is evidence, not proof. A follow-up commit is
the normal repair.

The late material contained one item that changes a COMMITTED finding.

## The one that matters: `PCRE2_UTF` DOES flip a construct verdict (C5/F14)

D30 §4 records, from R10, that `UTF`, `UCP`, `CASELESS`, `MULTILINE`, `DOTALL`,
`UNGREEDY`, `AUTO_CALLOUT` and every `EXTRA_ASCII_*` "flip NO construct verdict
at all". Verified by the author against libpcre2 10.46, with the UTF bit
established behaviourally (bit 19, the bit that makes `\xff` raise "UTF-8 error:
illegal byte"):

    \N{U+0041}     opt=0  err 193      opt=UTF  COMPILES
    [\N{U+0041}]   opt=0  err 193      opt=UTF  COMPILES

**It is K10's own construct** — the row this project uses as its worked example
in D32, D33 and the extension design. And the registry's own `note` on that row
already said *"PCRE2 error 193 outside UTF mode, which is recognition, not
rejection"*, so the table knew what the measurement denied. Two homes for one
fact, one wrong: the shape the single table exists to prevent. D30 §4 now carries
the correction inline.

**The methodological point is worth more than the correction, and it is the
second instance in one session.** C2 independently measured `PCRE2_UTF` as
changing **0 of 120,099** verdicts — and C2 was RIGHT. Its probe space was
strings of length 1..3, which cannot contain a ten-character construct. C5 swept
the registry's own `syntax` strings, which can.

> Two correct sweeps, opposite conclusions, and the difference is entirely which
> family the generator could express. **Counting a population by a generator
> that cannot produce it counts the generator.**

This is the same failure as the design's position-independence claim being
evidenced on the only bucket that could not falsify it. Twice in one session,
from two different directions.

C5's full sweep found **8 verdict-changing option bits, not two**:
`ALLOW_EMPTY_CLASS` (1 flip), `ALT_BSUX` (6), `NO_AUTO_CAPTURE` (11), `UTF` (2),
`NEVER_BACKSLASH_C` (1), `LITERAL` (143), `MATCH_INVALID_UTF` (2),
`ALT_EXTENDED_CLASS` (3); the other 24 bits flip nothing.

**And it breaks §7's framing rather than just its list.** `\x` is mode-dependent
under `ALT_BSUX` and is BASE grammar — pcrec implements `\x41` in `parse.c`, not
in the table — so `\x` must not get a row. The bound compile mode is therefore
**not expressible as a set of row statuses or a set of names**, which is what §7
is built on.

## The other late findings

- **C1/F9** independently reached the same live bug as C4/F21 and C3/F6 — that
  is now three critics on it — and added `[\k<name>]`, `[\g{1}]` and `[\9]`.
  Already recorded as **K13**, which was written before this material arrived;
  the extra probes strengthen it and change nothing.
- **C1/F11** — NINE of the 100 rows cannot express their correct terminal answer
  at TERMINAL, and they reach the VERB doorway, which C1 had earlier scored
  clean. Widens Finding 2 from one row to nine.
- **C1/F10** — §6's "set-shaped-but-invalid still yields 150" is a law of the
  BRACKET family generalised to every set-shaped row; the `\p` family obeys the
  opposite law. Corroborates C3/F1 from a second direction.
- **C2/F8, F9, F10** — `(?x)` refutes §5.4 in two reachable configurations, one
  of which the design itself introduces; the vacuity argument is carrying 28% of
  the grammar on a single longjmp; and one byte owned by a toggleable feature
  decides whether `\12` is a backreference or an octal escape.
- **C5/F12** — obligation C counted: "a row and nothing else" is **already false
  by 6x today**, and this design makes it ~10x while removing none of the
  existing cost.
- **C5/F13** — "never" and "not yet" are ALREADY indistinguishable, in the exact
  words D26 calls a defect, and §7.2's new status is not the missing one.
- **C5/F15** — the remaining §9 deletions audited: neither is subsumed, and one
  of them the design refutes in its own §2.

None of these reverse the panel's disposition; they widen it. The design's
§10 open questions stand, with §10.2 now answered and §7's framing added to the
list of things that did not survive.
