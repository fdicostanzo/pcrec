# [DD-13b] Design note — the grown `.rxt` format: grammar and semantics

**Status: REVISION 3.3 ([DD-13b.W23] STEP 1.3, 2026-09-12, lane
w23fix2) — the r57 ROUND-2 FIX ROUND, and the last one before merge.**
The round-2 critic verified 3.2's three blocker fixes: two HOLD
OUTRIGHT and the third (S3 OPAQUE REGIONS) held in DIRECTION and failed
end to end on its own axis, which is what 3.3 closes. **Four rules of
the structure layer moved and all four are in §1.2.1**: S3's trigger is
PARAMETERIZED on the prose-region-opening kinds and takes the TRIMMED
value (so `pattern |`, a legal pattern, stays one); the COMMENT line's
structural effect is stated in S1 and S3 — it terminates, as a blank
line does — which repairs two reject→accept widenings §1.6.1's claim 2
had denied; S0's BLANK narrows to the EMPTY line and a WHITESPACE-ONLY
line is declared INERT, dissolving two narrowings and saving the
format's only paragraph break; and the structure layer's second
parameter is stated ONCE as the `value`/`children` PAIR. Alongside
them: the NARROWING CENSUS is re-scoped to the FORMAT and runs to
eleven candidates, seven taken — two of them landed by STEP 0 and
marked as such (§1.6.1a); the `cardinality` values for the settings
kinds are DECIDED after measuring each population, which is what caught
`budget` (§2.25.2); and the 28,943 floor gains the definition that
makes it re-derivable (§1.1). **§0.8 is the finding-by-finding record
for both rounds and is where a reader of revision 3.1 starts.**

**Revision 3.2** ([DD-13b.W23] STEP 1.2, same day, lane w23fix) was the
r57 FIX ROUND against three read-only critics
(`docs/dev/reviews/2026-09-12-r57-w23-format.md`: 3 blockers, 14
must-fixes, 12 shoulds, 4 nits, all dispositioned FIX-NOW). Its five
structural outcomes: the BLOCK SCALAR is declared as
the structure layer's third device (S3 OPAQUE REGIONS, §1.2.1) and the
structure layer's schema parameters are stated as TWO rather than one;
the NARROWING CENSUS is re-swept with §1.6.4's own rule and published as
a CLOSED LIST (of five then; eleven at 3.3, §1.6.1a); the constraint
vocabulary grows from
five kinds to EIGHT because four W23 refusal rules did not fit the five
(§2.25.3); the `pattern`/`pattern-esc` both-in-one-block refusal is
DROPPED as an empty population (§2.19); and the derived-identifier
repair gains its length discipline and its callability bound (§2.22).

**Revision 3.1** ([DD-13b.W23] STEP 1.1, 2026-09-12, lane
w23recon) was the RECONCILIATION against Frank's internal-consistency and
ownership rulings. Revision 3 (lane w23design, same day) absorbed
pcrec-bench's capability-set needs note (`bench_rxt_needs_v1.md`,
received via outbox O-26) under **F-Q1** (Tier 1 AND Tier 2 as one
**W23** delivery, §1.4) and **F-Q2** (multi-line patterns are a MUST,
`pattern-esc`, §2.19). Two further rulings were issued while that lane
ran and never reached it; revision 3.1 works them through the delivered
text:

- **The INTERNAL-CONSISTENCY ruling** (`frank_inputs.md` 2026-09-12,
  five consequences): one structural rule, a declared schema, explicit
  sub-block syntax, a `version` header if a break is needed, and
  **structural parseability without context**. §1.2 is rewritten as an
  explicit **two-layer grammar** — a context-free STRUCTURE layer and a
  declared SCHEMA layer on top; §1.6 prices the version break and
  declines it; §2.25 designs the schema and its listable surface.
- **The OWNERSHIP ruling** (same day): the bench's sketches are
  CAPABILITY requirements, the syntax is pcrec's, and **long-term
  viability of the format outranks bench convenience and
  minimal-diff-from-today**. §2.26 is the spelling audit that criterion
  forces; THREE spellings moved under it (corrected at 3.2, r57
  C-N11 — the fourth item revision 3.1 listed, a pattern block's
  `description` taking `prose-value`, is §1.2.5's consequence of the
  structure-layer re-factoring and not an ownership-audit move).

Revision 2 was post-panel (r44) and post-ruling (D87). W1 is BUILT
(steps .1/.2/.3 landed; the wave table records what remains). §0.6 is
the need-by-need revision record, **§0.7 the 3.1 record**; §8 disposes
the bench's nine P-Q questions; §9 maps their 41 acceptance checks. The
W1-era text below is revised in place where a W23 production touches it
and untouched elsewhere.

This note designs the grammar and semantics of the unified
pattern-source / test-carrier / bench-set file format, under the rulings
Frank gave on 2026-08-28 (`usecases_and_outline.md` §5 as amended by §6.1
through §6.5) and **2026-08-29 (D87)**, against the requirements
[DD-13a] measured (`requirements.md`: R-RXT-*, R-VE-*, R-VG-*,
R-BENCH-*, R-GEN-*, R-SUBST-*, R-COMPAT-1; tensions T-1..T-6;
anti-requirements AR-1..AR-7; OD-1..OD-6), and revised against the
**r44 D6 panel** (`docs/dev/reviews/2026-08-29-r44-dd13b-format.md`).

**The rulings are not reopened.** Where this note departs from the
position paper, it departs from the paper's *own* provisional choices,
never from a ruling, and says so at the point of departure with the
measurement that forced it (§0.3).

## 0. How to read this

### 0.1 Claim marking

Every load-bearing claim in this note is one of three kinds, marked:

- **MEASURED** — a command was run in this worktree and its output is
  quoted. Semantic claims are run on **both oracles** — libpcre2 10.46
  through `docs/design/eng_brep_measurements/probes/pcre2_ctypes.py`, and
  `build/pcrec` through `tests/harness/driver.c` — and the note says when
  they agreed. Commands are given so the panel can re-run them
  (requirements.md §13 item 5 asks exactly this).
- **CITED** — quoted from a ruling, decision, or spec, with its id.
- **ARGUED** — reasoning from the above. An argued claim is the panel's
  natural target and is marked so it is not mistaken for either of the
  others.

### 0.2 The design in one paragraph

**The grammar is TWO LAYERS** (§1.2, rewritten at revision 3.1): a
context-free STRUCTURE layer — indentation attaches a line to the line
above it, and a two-member declared opener set groups pattern blocks —
and a declared SCHEMA on top (§2.25) saying which keywords are legal in
which scope, what they take, and whether a recovered tree is valid.
Nothing else lets a keyword decide where structure begins or ends.
On that footing, a `.rxt` file gains a **HEAD** (file-level declarations
and `config` / data blocks, everything before the first `pattern` line —
now a SCOPE rule rather than a structural one) above the
**BODY** it already has (pattern blocks, unchanged). Sixteen line-kind
additions live there — seven file-level declarations, two head block
kinds, seven block-scoped lines — and today's thirteen line kinds and
their semantics are untouched, so all **179 files / 3,265 blocks /
26,691 expectation lines** parse and mean exactly what they mean now
(MEASURED §1.1, independently reproduced by r44-grammar G1).
**Composition is an AST-level operation inside pcrec** (D87): the
reference spelling stays PCRE2's `(?&name)`, and what the format
contributes is a rule for BINDING a definition into a caller's AST —
group numbers are ASSIGNED rather than positional, a definition's
numbers are re-based above the caller's `ngroups` (D61's delivered-slot
region), lexical scope wins in both directions, and injected definitions
are name-qualified so a caller cannot reach them by accident (§2.3).
Three small PCRE2-dialect extensions carry what that needs — a numbered
group, a scope prefix on a call, and a delivering-call declaration —
each measured to be a spelling PCRE2 refuses, so no legal pattern changes
meaning (§1.5). A delivering call's scope path IS a struct member path,
which is how the results-into-a-struct feature falls out rather than
being designed twice (§2.13, [V-I]). The harness's TEXTUAL expansion
survives as the **oracle control** on the population where it is valid,
not as the producer (§2.3.4). Build declarations are file-level
`target <prefix> = <name> [with <config>…]` triples (Frank §6.4);
pattern blocks carry no build marker. Everything a pcrec-bench sidecar
carries today becomes lines beside the pattern (§4.5, field by field
against the live `subbench.toml`).

### 0.3 Where this note departs from the position paper

| # | the paper said | this note says | forced by |
|---|---|---|---|
| D-a | "A pattern's OWN groups keep priority over libraries" (§2 wave 1) | **the paper was right, and D87 restores it as a RULE**: a caller's own group overrides an injected definition, a library's internal reference binds to the library's own definition, and injected names are qualified so the two never contend. Revision 1 said the situation "cannot arise"; r44-sem MEASURED that false under `(?J)` | CITED D87 rule 2; MEASURED §2.3.3 M2, both oracles |
| D-b | `config` is wave 3 (§2) | a **minimal `config`** (pcrec option lines only) is **wave 1**, beside `target … with` | CITED: `docs/spec/limits.md` "Handling an oversized artifact" already tells users to put `--max-emit-bytes=N` "in the pattern-source file's `config` block"; a shipped spec has made the promise. Plus Frank §6.4's own words ("I want to specify the options for them") |
| D-c | OD-5's premise, inherited from R-VE-8: "subroutine-call semantics are ATOMIC and shift capture numbering" | **BACKTRACKABLE and capture-transparent** on 10.46; and the numbering is an ASSIGNED property (D87 rule 1), not a positional accident | CITED + MEASURED by an earlier lane: `subroutines_design.md` §3.2, §3.1. OD-5's own tag is "measured, never read from docs" |
| D-d | `include` "splices a file's blocks"; nothing said about a second include of the same file | a second `include` of the same resolved path in one closure is **REFUSED** | ARGUED from learnings §3 / K35: both alternatives (splice twice, silently ignore) change a population nobody counts |
| D-e | a `config` line `freq <name>` selects a data block (§6.5) | the selector is **`analysis freq <name>`** (disposing OD-6) | ARGUED, a grammar ambiguity — and r44-grammar G5's independent recognizer run DEMONSTRATED the ambiguity class rather than leaving it asserted |
| D-f | prose belongs in `#` comments and `NOTES.md` (revision 1's own §7 Q1 recommendation) | **`description` is a machine-readable FIELD**, with a `\|` block scalar for multi-line prose; `#` comments are operational only | CITED, Frank at r44 (15:0x, 15:1x): "we may want to summarize via script what a library or other rxt file has" |

### 0.4 What this note does not design

- The **template's internal grammar** (`$1`, `${name}`) — R-SUBST-1 says
  do not, and this note does not. §4.6 states the slot only.
- **Diagnostic wording** — D26. This note says what must be refused and
  what a refusal must name (the file, the line, the construct), never how
  the sentence reads.
- **[DD-11]'s definition table** — §4.2 states what this format needs
  from it as an interface. D85 rules its shape; the design is [DD-11]'s.
- **The struct-loading feature itself** — [V-I] (plan.md:737). §2.13
  states what this row hands it and what it still owns.
- **The bench record's schema** — the bench owns it (D78). §4.5 states
  what the format must be able to say so the record can key on it.
- **Iterated capture** — explicitly out of this row (D87 rule 5). §2.13
  says what it refuses in the meantime and why that is not a policy
  against it.

### 0.5 Revision record — r44 and D87, finding by finding

The panel (three read-only critics, both oracles on §2) raised **2
blockers, 2 blocker-leaning, 12 majors** and a set of minors. Frank
ruled the blockers as **D87**, which supersedes revision 1's §2.3
(textual EXPAND as the producer), §2.4 ("impossible by construction"),
§0.3 D-a, and the [DD-14.G] constraint. Where each finding landed:

| finding | landed |
|---|---|
| **M1** absolute numeric refs re-target on relocation (BLOCKER) | §2.3.1 rule (i) re-bases them; §2.3.3 measures the fix on both oracles; §6.0 drops them from the piece rule's refusal list |
| **M2/M7** a caller name colliding with an injected definition (BLOCKER) | §2.3.2 lexical scope + internal qualification; §2.3.3 M2 cells; §2.4 rewritten; §4.1 restated as a mechanism |
| **M3/M4/M5** D61: `ngroups`/`nnames`, `RX_NCAPS` and [DD-14.G]'s bar | §2.3.1 (D61 cited as the constraint this row inherits), §2.3.5's restated bar, §2.7's last bullet, S9b |
| **U1** the sidecar's free `tags` LIST was dropped | §1.3 `tag-item`; §4.5's table; §6.2's worked file |
| **U6** a file both named and included was double-counted | §2.11 rule 2 — counted once, reported "named, absorbed into <entry>" |
| **M6** the piece rule had 1 of 5 members | §6.0, rewritten as the five-member class with each member's fate |
| **M8** no visited/cycle rule; a block's own `name` not in L | §2.3.2 steps 3 and 4 |
| **M9** nothing built a target | §3.2 **H11**, and §1.4 puts it in W1 |
| **M10** no output-naming rule for N targets | §2.7's invocation table; S11 |
| **M11** "all 179 files have several blocks" was false | §2.7 — 177, and the two one-block files named |
| **M12** the [DD-11] interface must accept a builder; origin column | §4.2 items 1 and 3 |
| **M13** "the ONE place composition ≠ substitution" | §2.3.5 — two places, verbs named as the second |
| **M14** `features` union made narrowing unspellable | `features only` — §1.3, §2.6 |
| **M15** caps raise-only made `with c1, c2` order-sensitive | §2.6 — MAX WINS |
| **M16** no `encoding` row, no block spelling | §1.3, §2.6, §4.4's R-VE-12 |
| **M17** D61 never cited | §2.3.1, §2.3.5, §2.7, S9b |
| **U2** OUTCOME enum gaps | §4.5 item 1 — all twelve values, two named bench-side |
| **U3** method vs oracle-engine | §4.5's table — `oracle` + `tag method=…` |
| **U4/U5** `search_short`; the throughput generator/manifest | §4.5's table; §6.2 |
| **U8** R-VE-3 never addressed | §4.4 — explicit D77 deferral with its trigger |
| **U9** two resolutions conflated | §3.2's note after the H-table — sequential, and H2b is a third independent path |
| **U10** D-e disposes OD-6 | §0.3 D-e, §5.4 |
| **U11** D-e's ambiguity asserted, not demonstrated | §5.1 — G5's run cited |
| **U12** counter-cases to §7's recommendations | §7.2, beside each |
| **G2** "one of three numbers run.sh prints" | §5.1 — the three-way partition, measured |
| **G3** `from` unassigned a wave | §1.4 |
| **G4** the 256 invariant read as grammatical | §6.4 — named as a semantic check, and where |
| **Frank, description is a FIELD** | §0.3 D-f, §1.2, §1.3, §4.5, §6, §7.0 |

**What SURVIVED the panel unchanged** and is not re-argued below: the
grammar and INV-COMPAT (G1, G5, G6 — the corpus census reproduced to the
digit by an independent recognizer, four ambiguity attacks all failed);
§6.0's own correction and its controls; R-VE-5 for the primary's slots;
`(?J)` inside a DEFINE block not leaking; used-twice, self- and mutually
recursive definitions compiling and agreeing on both oracles; the
143-block reference census; and H4's python-`re` argument.

### 0.6 Revision 3 record — the [B42] absorption, need by need

The input is `bench_rxt_needs_v1.md` (50 needs N-1..N-53, six
roadblocks, twelve production sketches, thirteen MEASURED facts at pin
d34c9131, 41 acceptance checks, nine P-Q questions). The binding frame:
**F-Q1** (Tier 1 + Tier 2 land as ONE W23 delivery), **F-Q2**
(multi-line patterns are a MUST), and Option A (the set's truth lives in
`.rxt`; any bench-side answer must be argued, §8's P-Q4 is the one place
it was considered and the answer is still IN the format). The NUL and
duplicate-`description` refusals are **STEP 0, lane rxtnul, landing
now** — this revision designs against those refusals EXISTING and does
not restate them as new productions (their M1/M5).

**MEASURED for this revision** (probes run in this worktree; the census
and refusal probes against `build/pcrec` at b9572c66, read-only):

- The seventeen NEW first tokens this revision adds (`vocabulary`,
  `provenance`, `pattern-esc`, `provides`, `under`, `configs`, and the
  eleven sub-block attribute spellings) occur **0** times in first-token
  position across the corpus — §1.1's 32-keyword census extended, same
  method, same result. The sub-block attribute tokens additionally never
  enter any dispatch context at all, because they only occur INDENTED.
- `vocabulary` today is refused as **unknown** ("'vocabulary' is not a
  file-level directive"), not with the later-wave sentence `tag` gets —
  so the recognised-and-refused-by-name set (`rxt_format.md`'s "NOT IN
  THIS BUILD" list) must grow the W23 keywords in the same change that
  lands any partial build. Within one W23 delivery the interim state
  never ships, but the spec rule is stated so a stranger's partial build
  cannot regress it.
- The three find-all counting rules were run head to head (python3, the
  search-from-pos loop driven per rule): the bench's literal
  `pos = max(end, pos+1)` **DOUBLE-COUNTS an empty match found beyond
  the scan position** (`(?=a)` on `"xax"`: it reports `(1,1) (1,1)`
  where `match_api.md` §3.1's protocol and `re.finditer` both report
  one), and BOTH non-retry rules are a strict subset of `re.finditer`
  on empty-preferring patterns (`a*?` on `"aaa"`: 4 spans vs 7 — the
  NOTEMPTY class §3.1 already documents). §2.21 states the consequence:
  `mc` counts the §3.1 protocol's matches, not the bench formula's and
  not `finditer`'s.

Where each need landed (no-ask rows N-29/N-51/N-53 omitted; N-6/N-31
were BUILT already and are untouched):

| need | landed |
|---|---|
| **N-1, N-3** | BUILT (W1), untouched — `pattern` stays rest-of-line verbatim |
| **N-2** | §2.19 `pattern-esc` — the second spelling, same seven escapes, one line carrying a multi-line body (F-Q2). Roadblock #1 closed |
| **N-4** | the raw-NUL refusal is STEP 0 (rxtnul). EXPRESSING a NUL via `pattern-esc \x00` is REFUSED BY NAME with K9 as the reason — the compile entry takes no pattern length — and parks on `rx_info.pattern_len`'s API half, a named trigger, not a silence (§2.19) |
| **N-5** | `pattern-esc "\r"` expresses a trailing CR; the raw `pattern` trim is unchanged and documented |
| **N-7** | BUILT (W1.3's widened name grammar), untouched |
| **N-8** | the duplicate-`description` last-wins hazard is STEP 0's refusal (their M5); one-line rule unchanged, provenance carries the prose that never fit |
| **N-9, N-45, N-48** | `tag` lands in W23 as designed (§4.5's mapping); N-48's regime mechanism is REPAIRED, not replaced — §4.5 item 4 rewritten on the derived-identifier call binding (§2.22) |
| **N-10, N-20, N-21** | §2.15 `vocabulary` — per-key declared value sets, parser-enforced, undeclared keys stay free (compat). Roadblock #2 closed |
| **N-11..N-19** | §2.14 `provenance` — a record attached under the pattern block (§1.2.6), nine fields, four required, `adaptation` required iff `fidelity != verbatim`, `authored`'s agreement rule. Roadblock #3 closed. **Revision 3.1**: eleven fields, the same record reused at a data block, required per parent (§2.26 item 10) |
| **N-22, N-23** | §2.16 `provides` (spelled `capable` in their sketch; §2.26 item 4) — per-config, repeatable, accumulating, **fail-closed** (absent = nothing satisfied); flagged to Frank with §2.20 (P-Q4's ratification) |
| **N-24, N-28** | BUILT / as-designed; B7's raw-bytes promise gets its first verification at the delivery (§9) |
| **N-25** | `@file:` lands in W23 as designed (§2.8) |
| **N-26, N-27** | §2.18 — `@file:` gains `as <id>` (per-file subject namespace, functional binding, conflicts refused) and OPTIONAL `sha256 <hex64>` checked by whatever READS the subject. §2.8's no-hash paragraph is re-scoped: it was a default for committed subjects, not a principle (P-Q8). Roadblock #4 closed |
| **N-30** | BUILT, untouched |
| **N-32** | §2.21 — `mc`'s counting rule STATED: the `match_api.md` §3.1 protocol, with the measured three-rule comparison above and the bench formula's double-count named |
| **N-33** | unchanged (COULD; `variant`'s `groups` map is where neutral capture checking lands when the bench opens OD-B9) |
| **N-34** | `tag convention=` as designed, now closable by `vocabulary` |
| **N-35** | §2.17 `under` — a case-line QUALIFIER carrying the second correct answer per convention. Roadblock #5 closed |
| **N-36, N-38** | §2.9 widened: `oracle` takes an `engine-ref` with optional `/version`; `python`/`pcre2` keep their exact meanings; an absent oracle stays R-VG-3's labelled skip |
| **N-37** | `tag method=` as designed (W23) |
| **N-39, N-40, N-41** | §2.23 — `variant` becomes a record with attached attributes (§1.2.6): `kind` (closed via `vocabulary kind`), `text`, `groups`, `note` (prose), `unsupported`. The old one-line-plus-`groups`-continuation shape was a proto-sub-block; the general mechanism replaces it (house rule). N-41's three fields all have carriers |
| **N-42** | `config … testee`/`option` land in W23 as designed |
| **N-43, N-44** | §2.20 `configs describe` — the head declaration separating BUILD configs from DESCRIPTIVE ones, default `build` = today's semantics; plus the PERMANENCE sentence for a target-less, config-less file. Roadblock #6 closed; ratification flagged to Frank (D93 territory) |
| **N-46, N-47** | BUILT (W1), untouched |
| **N-49** | the regime -> subject-set mapping rides the repaired item 4 (§2.22): each regime block carries its own subject list |
| **N-50** | `include` lands in W23 as designed (§2.5, §2.11) |
| **N-52** | §2.24 — `--list-source` gains appended columns, **unconditional named sections** (`provenance`, `variants`, `cases`), and a spec-stated VALIDATES-vs-RECOGNISES table (their D4). The `m @file:… passes silently` observation is retired: case values are read |

### 0.7 Revision 3.1 record — the two rulings, consequence by consequence

The input is `frank_inputs.md`'s 2026-09-12 section: the
internal-consistency ruling with its five numbered consequences, and
the ownership framing that follows it. Revision 3 was written without
them (a messaging failure, recorded in `w23design_report.md`
§"Rulings received"), so this revision is a reconciliation rather than
a new wave — **no need N-nn changes its disposition, no production is
added or removed for the bench's sake, and §1.4's wave table is
untouched.** What moves is how the grammar is FACTORED and how four
things are SPELLED.

**MEASURED for this revision** (re-run in this worktree at the merge
base, read-only, so revision 3's own census is confirmed rather than
inherited — and it needed re-running: the corpus has grown by 31 files
since the number revision 3 quotes was taken):

- **The corpus is now 210 files / 3,936 blocks / 28,943 expectation
  lines**, not §1.1's 179 / 3,265 / 26,691 (those are r44-era, taken
  before [M5.0]'s `tests/utf8/` corpora landed). §1.1's three checks
  are stated against a pinned denominator, so the pin is now stale;
  §1.1 carries the correction and the rule that the denominator is
  DERIVED at check time and pinned as a FLOOR, never as a constant a
  growing corpus silently invalidates.
- **0 lines in the corpus are indented** (`grep -rhcE
  '^[[:space:]]+[^[:space:]]'` summed over all 210 files → 0). This is
  the load-bearing measurement for §1.2's unified attachment rule and
  for §1.6's answer on the version break: it is what makes the
  consistent grammar purely ADDITIVE.
- **All 52 candidate keywords are 0 in first-token position** — §1.1's
  32, revision 3's 17 W23 additions, plus `version` and `schema`, over
  the current 210 files. `version` being free is what makes §1.6's
  reservation cost one line.
- **Only 1,016 of 3,936 `pattern` lines (26%) are immediately preceded
  by a blank line.** A blank line is therefore NOT a block separator in
  this corpus, which is what closes the one alternative to the keyword
  in §1.2.3's account of where today's grammar fails structural
  parseability.
- **Leg C dispatches an indented PRE-BODY line on its first token**,
  so revision 3 §1.2's claim that "the indentation test PRECEDES token
  dispatch" holds "in all three body readers" is FALSE today.
  `tests/harness/verify_rxt.py:407-423` splits the line (which strips
  leading whitespace) and raises the head-word or
  no-open-block diagnostic before reaching its indentation check at
  `:424`; measured on three fixtures, an indented `m` line before the
  first `pattern` reports *"'m' line before any pattern block"*.
  **CORRECTED AT REVISION 3.2 (r57 C-N9) — the defect is PRE-BODY
  ONLY, and revision 3.1's wording over-read it.** `:424`'s
  indentation check is UNCONDITIONAL for every line once a block is
  open: the `if not seen_pattern:` guard at `:407` closes at `:423`,
  so an indented line INSIDE a block reaches `:424` and is refused
  with *"a pattern block's lines are not indented"* before any token
  dispatch. Leg C therefore has the ordering right for body lines and
  wrong only for the pre-body region — which is precisely why §9's
  A-group fixture must sit at the PRE-BODY position (S-M5) or it
  cannot reach the defect at all.
  **Leg B has no indentation test at all** — **22** of `run.sh`'s
  dispatch arms are anchored `^<keyword>` with no leading-whitespace
  tolerance, so an indented line reaches the catch-all *"unparseable
  .rxt line (hard error)"* by FALL-THROUGH rather than by a rule.
  **The count is 22, not revision 3.1's 24, and the derivation is
  given because the first number was a raw grep** (r57 C-S8): 24
  `^`-anchored `=~` tests occur in the file, of which **two are
  pre-loop skips** and not dispatch arms at all — `^[[:space:]]*$` at
  `run.sh:1692` and `^#` at `:1693`, both `continue`ing before any
  dispatch. The remaining 22 split **17 inside the hash-pinned arm
  region** (`:1713` BEGIN .. `:1967` END) and **5 appended after it**
  (`:1984`-`:2092`). Revision 3.1's parenthetical that the blank-line
  skip is the one tolerant regex **is correct and is kept** — it is
  `^[[:space:]]*$`, and `^#` is column-1-anchored like every arm. The
  CONCLUSION is unchanged and confirmed: no dispatch arm tolerates
  leading whitespace. Only the count moved, and it moved because a
  grep hit and a dispatch arm are different things. This is the
  stale-pinned-number shape §1.1 was corrected for, reintroduced in the
  correcting revision's own paragraph — which is why every count in
  §0.8 below carries its derivation rather than its value alone.
  Only leg A (`src/parse/rxt_source.c:992`) tests indentation before
  dispatch. Every arm is a hard error, so nothing is mis-parsed today;
  what is false is the claim that a RULE holds in three places, and
  §1.2 now states it where it can be enforced and §9's A-group says
  what pins it.

Where each consequence of the internal-consistency ruling landed:

| consequence | landed |
|---|---|
| **1. Internal consistency over accretion** | §1.2 rewritten as two layers. The head/body indentation ASYMMETRY is not narrowed — it is **DELETED**: one attachment rule serves head continuation, `config` bodies, block scalars and body sub-blocks alike, and "which scope a keyword is legal in" becomes a schema fact with no structural consequence. §2.26's audit is the same criterion applied to spellings |
| **2. A breaking `version` header is on the table** | §1.6: **the break is DECLINED and the keyword is RESERVED.** The consistent grammar is achievable additively (every rule change moves a hard error between arms; the one deliberate widening only accepts more), so "if needed" is answered NO — with the future change that WOULD trigger it named and priced (§1.2.3) |
| **3. Schema rules validation** | §2.25: the format's structural rules become a DECLARED TABLE with five constraint kinds (**EIGHT at 3.2, r57 S-BL1**), the parser its reader/enforcer, and `--list-schema` its listable surface on `--list-limits`/`--list-axes`'s one-derivation precedent. §2.15's `vocabulary` is nested as the FILE-declared half (one table, a `source` column). §2.24's VALIDATES-vs-RECOGNISES statement is upgraded from prose to a column the surface prints |
| **4. Sub-blocks get explicit syntax** | §1.2.4: the visible-marker alternative is designed and priced against bare indentation, and **bare indentation wins** — because the cure for "indentation whose meaning depends on which keyword opened the line" is the unified rule, not a second signal, and a marker would make structure depend on two signals that can disagree. The `\|` block scalar is explained as what it is: a VALUE-form discriminator, not a structure marker |
| **5. Structurally parseable without context** | §1.2.1 states the structure layer with its ONE declared parameter (the two-member block-opener set) and §1.2.3 states, without softening, the one place today's shipped grammar fails the property and what fixing it would cost |

**Where to attack revision 3.1 is §5.2a**, written before the panel
rather than after, and pointed at from here so it is not missed.

Where the ownership ruling landed: §2.26, the audit. **THREE spellings
moved** — `capable` → **`provides`**, `licence`/`licence-note` →
**`license`/`license-note`**, and the `freq` data block's five
provenance fields → **the same `provenance` sub-block a pattern block
uses** — and `variant`'s `text` was KEPT with a different reason (its
revision-3 justification expires under the new structure layer). §9's
C-group and D-group rows move with them, and the delivery's outbox
message to the bench carries the list. **CORRECTED AT 3.2 (r57
C-N11)**: revision 3.1 counted four moves by including a pattern
block's `description` taking `prose-value`. That is not a spelling
move and not the audit's — it is §1.2.5's consequence of §1.2.1's
re-factoring, arrived at from the internal-consistency ruling rather
than the ownership one, and it is a WIDENING rather than a rename. The
outbox message inherits the corrected framing (§9's correction list
keeps the row, under its true cause).

### 0.8 Revision 3.2 record — the r57 panel, finding by finding

The input is `docs/dev/reviews/2026-09-12-r57-w23-format.md`: three
read-only critics (grammar/structure, schema/checks, consumer/needs),
all opus, every measured claim a real `build/pcrec` probe. **Three
blockers, fourteen must-fixes, twelve shoulds, four nits; the manager
dispositioned every one FIX-NOW.** No ruling is reopened, no need
changes its disposition, and §1.4's wave table is untouched.

**MEASURED FOR THIS REVISION** (this worktree, `build/pcrec` built at
the lane's own merge base, read-only — every number below carries its
derivation, because §0.7's own "24 arms" was a raw grep that meant
something else):

- **The five grammar-lens probe cells all reproduce**, and they are the
  narrowing census's evidence (§1.6.1a). `description |` with an
  indented `#` in its body: **rc 0, the `#` line is PROSE**
  (`--list-source` value `line one\n# this looks like a comment\nline
  three`). Ragged prose inside a block scalar: **rc 0**, relative
  indentation preserved. A tab-indented `config` body: **rc 0**,
  `flags=i engine=vm`. A `config` body mixing a 2-space line and a TAB
  line: **rc 0**, parsed flat.
- **AND ONE OF THE FIVE IS A SHIPPED DEFECT, not a narrowing** (r57
  G-B2 N2's independent finding, reproduced here): a block scalar whose
  first continuation line is indented 4 and whose second is indented 2
  yields the value `line one\ndented-line-two` — **`parse_prose`
  (`rxt_source.c:520-533`) strips the block's indent as a BYTE COUNT
  (`skip = len < indent ? len : indent`) rather than as whitespace, so
  a dedented line silently loses two characters of CONTENT**. Filed as
  `docs/dev/known_issues.md` **K57**; it is independent of this
  revision's direction (it is wrong under revision 3's rules, revision
  3.1's, and 3.2's alike).
- **The C-M1 collision narrowing reproduces and its population is
  measured.** `x_y` beside `x-y` with the call spelled `(?&x_y)`
  compiles today and its artifact is **byte-identical** to the same
  file without the `x-y` sibling — with a methodology note that is this
  house's THIRD recorded instance of the same trap: emitting the two to
  `a.c` and `b.c` reports them as differing on the `#include` line
  alone (`opt4_impl/CLAUDE.md`'s own trap), so the comparison is run
  with equal basenames in different directories. Population of the
  general collision shape across both repos: **1** — the deliberate
  fixture `tests/rxtsource/fixtures/target_prefix_collision.rxtin`
  (`a-b` beside `a.b`), over 96 `name` lines in 26 files; **pcrec-bench
  contains no `.rxt`/`.rxtin` file at all** (0 files, read-only check).
  Population of C-M1's own `x_y`-beside-`x-y` shape: **0** in both.
- **The corpus census re-confirms at 210 / 3,936 / 28,943**, and the
  non-blank non-comment line count — the number a GENERIC reader sees,
  which is what §1.2.3's argument is about — is **35,961**, not the
  28,943 expectation lines revision 3.1 quoted there (r57 G-B6).
- **20 head declarations carry an indented body, across 13 of the 45
  `tests/rxtsource/fixtures/` files, and every indented CONTENT line is
  width 2** (r57 G-B7; revision 3.1 said 19). The apparent 21st and the
  one width-3 line are the same line: `whitespace_only_line.rxtin:9`, a
  line of pure whitespace, which S0 classifies BLANK and not CONTENT.
  Tab-indented content lines in either repo: **0**.
- **Two adjacent `pattern` lines are two blocks, rc 0** (`--list-source`
  prints two `pattern` rows) — the measurement that empties §2.19's
  both-spellings refusal (r57 S-BL2).

Where each finding landed:

| id | sev | landed |
|---|---|---|
| **G-B1** | BLOCKER | §1.2.1 gains **S3 OPAQUE REGIONS** as the structure layer's third device, and the layer's schema parameters are stated as **TWO** (`opens_group`, `value = prose`), both fetched from `--list-schema`. §1.2.4's marker comparison is re-run against the two-parameter baseline and the sentence "`\|` … neither decides where a line attaches" is WITHDRAWN and replaced. **(3.3, R2-F4: still two parameters, but the second is the `value`/`children` PAIR — three columns read, not two.)** |
| **S-BL1** | BLOCKER | §2.25.3 grows from five constraint kinds to **EIGHT** — `cross-scope` ADMITTED (its W23 customer meets the section's own membership rule; §2.25.4's deferral of it contradicted a production one section away), `forbidden-if` ADMITTED (`authored`'s must-be-absent half, which no negated `required-if` reaches), and `functional-binding` ADMITTED (subject-`as`, which `unique-by` would have REFUSED on its own documented normal spelling); `under`'s duplicate key gets an honest home as **parser code with its reason and a D77 trigger** rather than a ninth kind. §2.25.3's completeness claim is deleted |
| **S-BL2** | BLOCKER | §2.19's "one block carries `pattern` or `pattern-esc`, never both" is **DROPPED** — measured empty population; a second opener starts a new block (S2). §9's B6 row flips from SATISFIED-by-refusal to a bench CORRECTION (premise dissolved), and the correction list carries it |
| **G-B2** | MUST | The narrowing census is re-swept and published as a CLOSED LIST of five (§1.6.1a), each with population / forced-vs-chosen / spec sentence. N3 (tabs) is **REFUSED BY NAME** as the manager leaned; the lane did not overturn it and §1.6.1a records why. N2's shipped dedent corruption is K57 |
| **G-B3** | MUST | §2.25.2's `children` column gains a **`prose`** member and the precedence is stated: a `value: prose` kind's children are its VALUE, not schema-checked lines. H12 already assumed this reading and now cites it |
| **G-B4** | SHOULD | §1.2.4 count 1 reworded: the disagreement-state error class RELOCATES to the schema layer rather than disappearing, and `\|`'s own no-continuation refusal (`rxt_source.c:514`) is an instance of it. The DECISION stands; count 2 is the strongest |
| **G-B5** | SHOULD | §2.26 item 4 states which half of the `requires`/`provides` pairing it delivers; §2.16 gains the pointer sentence from `provides` to `vocabulary requires` |
| **G-B6**, **G-B7** | NIT | 35,961 (§1.2.3); 20 blocks / 13 of 45 fixtures / uniform width 2 (§1.2.1) |
| **S-M1** | MUST | Folded into G-B1's S3 + G-B2's package; §9's A-group names the ragged-prose fixture |
| **S-M2** | MUST | Every `validated_by: all-readers` row owes a three-leg fixture, NAMED in §9's A-group; "the fixture population covers every such row" becomes its own check (§9 A3/A4) |
| **S-M3** | MUST | S-R2's detector is re-named as a **pcrec-side fixture pair**; the bench's C5/C6 are corroboration (§3.2) |
| **S-M4** | MUST | S-R3 re-spelled as a hand-written dump **disagreeing on one row**, and the cross-check widened past `closed` (§3.2) |
| **S-M5** | MUST | §9's A-group fixture is pinned at the **PRE-BODY** position and asserts diagnostic CLASS, not exit code |
| **S-M6** | MUST | §9's correction list gains **D1** (nine → eleven provenance keys plus two renames) and the `provides` row's empty population citation is corrected to the checks that actually type a moved token |
| **S-M7** | MUST | SW17 gains `docs/spec/table_contract.md` — its Scope table enumerates every conforming producer and says new tables adopt AT BIRTH (D94's failure verbatim) |
| **S-S1** | SHOULD | §2.25.4's legs-B/C row is restated as a **DECLINE**, not a deferral |
| **S-S2** | SHOULD | The `wave` column is KEPT, with its real consumer stated (§2.25.2) |
| **S-S3** | SHOULD | The three `validated_by: none` items are given stated homes (§2.24) |
| **S-S4** | SHOULD | §1.1's floor re-pinned at **210 / 3,936 / 28,943** with the mover NAMED ([M5.0]'s `tests/utf8/` corpora) |
| **S-S5** | SHOULD | "structurally impossible" qualified to leg A wherever it was unconditional (§1.2.6, §2.23, §8 P-Q1) |
| **S-S6** | SHOULD | S-R4 SPLIT into two rows with two detectors (§3.2) |
| **S-S7** | SHOULD | At-most-one-per-parent is ONE mechanism — the `cardinality` column — and §9's C7 and §2.25.3 are reconciled on it |
| **S-S8** | SHOULD | C1's differential compares **diagnostic CLASS** for `all-readers` rows (§2.25.5, §9 A3/A4) |
| **S-N1** | NIT | `--list-schema` is the **SEVENTH** registry dump, corrected at all three sites (§2.25.1, §3.3, SW17) |
| **C-M1** | MUST | The `x_y`-beside-`x-y` collision is narrowing **(5)** in §1.6.1a's closed list, with its measured population and its forced-vs-CHOSEN verdict; §1.6.4 gains a **fourth case** for a chosen narrowing, and §5.2a attack 1 is re-aimed |
| **C-M2** | MUST | SW12 gains the two `rxt_source.c` comment sites (`:288`, `:1129`); the non-callable-definition loss goes to Frank as **W23-F4** (§7.3), manager recommendation ACCEPT |
| **C-M3** | MUST | §2.22 cites `rxt_compose.c:854-864` (the qualified-rowname synthesis), fixes the `def_find` misname to `def_by_name`, states the **refuse-before-mapping length rule**, and carries the **128-byte callability bound** |
| **C-S4** | SHOULD | §2.20 rule 4 gains the `lib` closure clause |
| **C-S5** | SHOULD | §2.20 rule 3 states that `use` RESOLVES in both modes |
| **C-S6** | SHOULD | SW7 states the ill-formed-UTF-8 advance rule normatively; E5 becomes utf8-bearing; the second-implementation tension is acknowledged with C1 as the paid-for answer (§2.21) |
| **C-S7** | SHOULD | §2.18 carries N-27's non-ID slice — byte length DERIVABLE, description and `periodic` refused with the D77 shape and their trigger |
| **C-S8** | NIT | 22 arms with its derivation (§0.7) |
| **C-N9** | NIT | The leg-C scoping clause (§0.7) |
| **C-N10** | NIT | §2.24's column list marks the `pattern` column's `esc` dependency |
| **C-N11** | NIT | The §2.26-four-moves framing corrected above; the outbox message inherits it |

**What SURVIVED the first-round panel** and is not re-argued below:
F6's ragged-body method and result (reproduced byte-for-byte); the census at
210/3,936/28,943 including the 25.8% blank-preceded measurement and the
inference from it; F1 in both legs; M8's refusal in both arms; the
version decline and the `version` reservation; the provenance
unification including the `analyzer` keep; the one-derivation claim for
leg A; the `vocabulary`-as-`source: file` nesting; required /
required-if / closed correctly mapped for §2.14's rules 1/3/4; the
checklist mapping behaviourally right on 39 of 41; §1.2.4's
marker-vs-indentation PRICING (as distinct from its count-1 wording);
NEEDS COVERAGE exact at 36/9/5/3; the four renames orphaning nothing;
the zero-reader-change claim at the GRAMMAR level; and roadblocks #1-#5
closed as claimed.

#### ROUND 2 — the focused re-check on revision 3.2 (revision 3.3)

The input is the ROUND 2 section of the same review file: one read-only
critic, two tasks — verify 3.2's three blocker fixes as landed, and run
Addendum 2's own new attack (walk every §2 refusal rule and ask what it
accepted yesterday). **VERDICT: S-BL1 and S-BL2 HOLD OUTRIGHT under
attack; G-B1's S3 holds in DIRECTION and fails end to end on its own
axis.** Four must-fixes, two shoulds, one nit, all FIX-NOW; no ruling
reopened, no need re-dispositioned, §1.4's wave table untouched, and
the Frank queue is UNCHANGED at W23-F1 / W23-F2 / W23-F4.

**MEASURED FOR REVISION 3.3** (this worktree, `build/pcrec` at the
lane's merge base, read-only; every probe re-run here rather than
inherited from the critic's report):

- **The COMMENT line terminates, at both sites, and both shapes are
  REFUSED today.** `config c` / `··flags i` / `# column one` /
  `··engine vm` — **rc 1, line 4**, *"indented line continues nothing
  (the declaration above it takes no continuation)"*. `description |` /
  `··line one` / `# column one` / `··line three` — **rc 1, line 4**,
  the same message. The mechanism is the same in both: a column-1 `#`
  is not `line_indented` (`rxt_source.c:109`), so it ends
  `parse_config`'s body loop (`:727`) and `parse_prose`'s region loop
  (`:511`) alike, and the indented line below reaches the file-level
  loop with nothing to continue (`:992`). Under 3.2's silence both
  become ACCEPTED — the second additionally as an opener with TWO
  disjoint prose regions, which S3's single-extent rule cannot express.
- **The WHITESPACE-ONLY line is a CONTINUATION in all four probed
  positions, not a blank.** Inside a block scalar: **rc 0**, and it is
  IN the value — `description |` / `··para one` / `···` / `··para two`
  dumps `para one\n·\npara two` (the block indent of 2 stripped from a
  3-space line leaves one space). Inside a `config` body: **rc 0**, and
  the body CONTINUES past it (`flags=i engine=vm` both present). At
  file start, and immediately after a blank line: **rc 0 in all three
  legs** (A, `run.sh --dump`, `verify_rxt.py --dump`). The
  TRULY-EMPTY line is the contrast that makes the class real: the same
  block-scalar file with a zero-byte separator is **REFUSED at line 4**
  — r46sem-10's ruling, working as ruled — so the indented
  whitespace-only line is the format's ONLY paragraph break today.
- **`pattern |` is a legal pattern**: rc 0, `--list-source` dumps the
  pattern column as `|` (the alternation of two empties). It is R2-F1's
  witness — 3.2's unparameterized S3 trigger would have opened an
  opaque region on it and turned a working file into a refusal.
- **The six settings kinds' shipped cardinality, one probe each.** A
  second `name` (`n1`→`n2`), `engine`, `encoding` (`byte`→`utf8`),
  `features` (`backrefs`→`classes`) or `flags` line: **ACCEPTED, last
  wins, no diagnostic.** A second `budget` repeating a field
  (`steps=50` then `steps=99`): **ACCEPTED, 99 wins.** A second
  `budget` naming the OTHER field (`steps=50` then `frames=4096`):
  **ACCEPTED, both kept** — two slots, not one. A second `export`:
  **REFUSED by name** (`:1184`). One surface, two answers.
- **The populations, both repos, before any narrowing was taken.** Over
  258 `.rxt`/`.rxtin` files / 4,053 pattern blocks / 19 `config`
  declarations: duplicate `name`/`engine`/`encoding`/`features`/
  `flags`/`description`/`export` in one block or one config body —
  **0 each**. Duplicate `budget` LINE in one block — **1**, and it is
  `tests/harness/giveup.rxt:19-23`, two different FIELDS, deliberate
  and depended on by `make test`. Duplicate `budget` FIELD — **0**.
  `pcrec-bench` holds **0** `.rxt`/`.rxtin` files (re-confirmed
  read-only). **The one non-zero number changed a decision**, which is
  §1.6.4's new case 5.
- **28,943 reproduces, and so does 28,488.** Re-running the census awk
  (`run_rxtsource_tests.sh:281-285`) over `find tests -name '*.rxt'`:
  **210 / 3,936 / 28,943**, of which **455** are `perr`, giving
  **28,488** without them. The eight-kind list (`m n ms ns g gp gu
  perr`) is the definition; the natural six-kind reading lands at
  **24,016**, `ms`/`ns` being 4,927 lines.

Where each ROUND 2 finding landed:

| id | sev | landed |
|---|---|---|
| **R2-F1** | MUST | §1.2.1 S3's trigger names the PROSE-REGION-OPENING kind condition and the TRIMMED value, so `pattern \|` is untouched; §1.2.5 and §1.3's `prose-value`/`opaque-region` productions carry the same two clauses. The trim is not new — it is `rxt_source.c:1222-1226` (r46sem finding 14) and leg C's `v.strip() == '\|'`, pinned by `desc_pipe_trailing_space.rxtin` |
| **R2-F2** | MUST | The COMMENT line's structural effect is stated in **S1** (it closes every open attachment, exactly as a BLANK does) and in **S3** (it ends an open region), with the two measured widenings and the reason transparency was rejected. §1.6.1 claim 2 carries the correction: the claim was FALSE as 3.2 shipped it, the cause was a line class declared in S0 with no effect stated anywhere, and it is true again with its single stated exception |
| **R2-F3** | MUST | S0 narrows BLANK to the **EMPTY line** and gains WHITESPACE-ONLY as a fourth class, declared **INERT** outside a region and BYTES inside one. §1.6.1a rows (6) and (7) are the two narrowings that dissolves; §1.2.5 records the paragraph-break consequence. S3's self-contradiction is fixed by SCOPING: S0 does not run for dispatch or attachment inside a region, and the three-predicate boundary test is named as the one thing still computed per line. **PUSHBACK, argued rather than complied with**: the manager's "attachment-relevant, value empty, schema-inert" formulation introduces a THIRD narrowing (S1's attaches-to-nothing arm fires on a whitespace-only line at file start and after a blank — both measured rc 0 in all three legs today). "Inert" dissolves the same two, takes none, and is the shorter rule |
| **R2-F4** | SHOULD | Said ONCE, in §1.2.1's parameter table: parameter 2 is the `value`/`children` **PAIR**. §1.2.2 and §2.25.2 are corrected to it; §1.3's EBNF already had it. **S-R5's detectability is the tiebreaker and is now spelled out in the row**: with `value` alone read, flipping `children` to `none` changes nothing observable anywhere — the region still opens and bytes reach no validity check — so the row gains plant (b) and the column gains a detector |
| **R2-B** | MUST | §1.6.1a states its SCOPE (the format, not the lane's diff) and **carries STEP 0's two refusals as rows (10) and (11)**, marked "landed by STEP 0 (lane `rxtnul`, `d4576c48`), not by this revision", with the NUL row FORCED and the duplicate-`description` row CHOSEN on row (8)'s reasoning. §1.6.4's duty gains the sweep-the-format clause |
| **R2-C** | SHOULD | **DECIDED in §2.25.2**, with a per-kind table and the populations measured FIRST: `at-most-one` for `name`/`engine`/`encoding`/`features`/`flags`/`description`/`export`, and **`accumulate` over `{steps, frames}` for `budget`**, whose refusal is at the FIELD. Two deviations from the leaning, both measured: `budget` is NOT a scalar kind and `at-most-one` would have refused a shipped corpus file; and `flags`, which the finding's list did not name, is in the identical state and is taken with the rest. H16 carries the choice; §1.6.1a rows (8) and (9) carry the compatibility package |
| **R2-D** | NIT | §1.1's floor block defines "expectation line" — the eight first-token kinds, `perr` INCLUDED, 28,488 without it, and the 24,016 a six-kind reading produces |

**What ROUND 2 confirmed and is not re-argued**: the eight-kind
constraint count honest at every site with each new kind's W23 customer
verified in its home section; §2.25.4's self-contradiction genuinely
fixed; every echo of the dropped `pattern`/`pattern-esc` refusal gone
(*"the schema section is now the strongest part of the note"*); all
three of Addendum 2's pushbacks endorsed; every population number from
revision 3.2 re-derived and reproducing; K57 confirmed filed with its
repro.

---

## 1. Grammar


### 1.1 The base, restated as a testable invariant

**R-COMPAT-1 (existing files valid, unmodified, semantically unchanged)
is the first-class invariant of this design.** It is stated here as
something a check can fail:

> **INV-COMPAT.** For every `.rxt` file in `tests/`, the grown parser
> produces exactly the block sequence, directive values and expectation
> list that today's `tests/harness/run.sh` parser produces;
> `tests/harness/verify_rxt.py` re-verifies the same 26,691 expectations
> to the same answers; **and the composer binds nothing in any of them**,
> so the pattern text reaching the compiler is byte-identical to today's.

The third clause is new in revision 2 and it is the one D87 makes
necessary: composition is no longer a text transformation whose identity
case is visible in the text, so "the composer did nothing" has to be
asserted rather than read off. It is cheap to assert — the composer
reports the size of the closure it bound, and for the corpus that number
must be **0** in all 3,265 blocks.

**How it is tested (three checks, not one, because one would share a
source with what it controls — learnings §3):**

1. **Re-parse differential.** A dump mode on each parser emits a
   canonical, order-preserving serialisation of what it parsed (block
   index, `file:line`, pattern text, every directive with its value,
   every expectation with its fields). The two dumps must be
   **byte-identical** over all 179 files. This is the check that catches
   a silently changed value.
2. **Answer re-run.** `run.sh` over the whole corpus under the grown
   parser must report the same pass/fail/pending counts, the same
   `pattern-compile failures (distinct)`, and the same
   `group cases pending-vm` (three numbers `run.sh` already prints —
   `tests/harness/run.sh:1030-1051`). Note those three are a DIFFERENT
   partition of the population than the 26,691 above: a `perr` block and
   a live `g` line each record independently (r44-grammar G2, and §5.1
   gives both partitions). This is the check that catches a parse that is
   faithful but routed differently.
3. **Oracle re-run.** `verify_rxt.py` over the corpus must report the
   same verified count and the same skip count. This is the check that
   catches a change in what a subject's bytes decode to.

**The counted denominator is asserted in all three** (the [DD-13c] lesson:
"without them the value comparison would have been vacuously true"): each
check fails if it saw fewer than 179 files, 3,265 blocks or 26,691
expectations. A check that runs on an empty corpus must be red.

**CORRECTED AT REVISION 3.1 — those three numbers are STALE, and the
way they went stale is the durable part.** Re-measured at this
revision's merge base by the same method, the corpus is **210 files /
3,936 blocks / 28,943 expectation lines** (§0.7); the r44-era figures
quoted throughout this section predate [M5.0]'s `tests/utf8/` corpora.
Nothing in the design depends on the values — INV-COMPAT is a
*relation* between two parses, not a count — but a check written
against a constant that a growing corpus outruns is a check whose
denominator assertion silently stops meaning what it was written to
mean, which is one step from the vacuity the assertion exists to
prevent. **So the rule, not the number, is what the spec states:** the
denominator is DERIVED at check time from the same `find` the check
dispatches over, compared against the OTHER parser's count for equality
(that is the real assertion), and pinned separately as a FLOOR that a
corpus may only grow past. The three numbers above are read as "the
floor at r44" rather than as facts about today.

> **THE FLOOR, RE-PINNED IN THIS CHANGE (revision 3.2, r57 S-S4).**
> **210 files / 3,936 blocks / 28,943 expectation lines**, re-derived in
> this worktree at the lane's merge base (§0.8), and this is the value
> the delivering change writes — **not** the r44 numbers, which
> revision 3.1 corrected in its prose while leaving the pin sentence
> pointing at them. A floor left at 179/3,265/26,691 lets a **31-file /
> 671-block / 2,252-line regression pass green**, which is the exact
> vacuity the denominator assertion exists to prevent, one level up.
> **THE MOVER IS NAMED**: [M5.0]'s `tests/utf8/` corpora (stages 3-5,
> 2026-09-06..09-11), plus `[K53-SELRETRY]`'s dedup of four duplicated
> blocks in `axis04_p_categories.rxt` — so the movement is accounted
> for rather than merely observed, and a future gap between the floor
> and the live count has a place to start. And the control that CANNOT
> rescue a stale floor is named too: check (1)'s parser-vs-parser
> equality shares the same `find` with the thing it counts, so both
> sides shrink together and the comparison stays true on a truncated
> corpus. Only the floor sees that, which is why it is a separate pin
> and not a derived one.
>
> **AND "EXPECTATION LINE" IS DEFINED HERE, because the next person
> cannot re-derive 28,943 without it (3.3, r57 ROUND 2 R2-D).** An
> expectation line is a line whose FIRST TOKEN is one of **eight**
> kinds — `m`, `n`, `ms`, `ns`, `g`, `gp`, `gu`, `perr` — counted over
> `find tests -name '*.rxt'`; that is the awk at
> `tests/rxtsource/run_rxtsource_tests.sh:281-285`, which is the pass
> this floor is compared against. **`perr` IS INCLUDED, and it is the
> whole of the ambiguity**: `perr` is a BLOCK field rather than a case
> row — the same script's own reconciliation (`:607`) separates it out
> for exactly that reason — so a reader who reasonably excludes it
> counts **28,488** and reports a 455-line drift where nothing has
> moved. Both numbers are re-derived at this revision. The eight-kind
> list is load-bearing too: the natural `m/n/g/gp/gu/perr` reading
> lands at **24,016**, because `ms` and `ns` are 4,927 lines nobody
> remembers are in it.

**Sabotage rows for INV-COMPAT** (each must turn the corresponding check
red, and the check that must catch it is named — a row no check catches is
a finding about the check set):

| row | plant | must be caught by |
|---|---|---|
| S-C1 | drop the last `g` line of one block | (1) dump differential, (2) count |
| S-C2 | decode `\x41` as the two characters `x41` | (1) dump differential, (3) oracle |
| S-C3 | let `flags` carry forward to the next block | (1) dump differential |
| S-C4 | treat `# pcre2-only` as an ordinary comment | (3) oracle skip count |
| S-C5 | make `frames-buffer=` block-scoped rather than positional | **(2) the answer re-run** — CORRECTED 2026-08-30 ([DD-13b.W1]): this row read "(1) dump differential", and under W1's parser split the dump differential **cannot** catch it, because pcrec never parses `frames-buffer=` at all (it is an expectation-routing line, no part of a compile) so the line does not appear in both dumps. What does catch it is (2): `run.sh` captures `cur_route` at each case push (`run.sh:931,941,951,961,990`), so a block-scoped version changes which route a case runs under and the counts move |
| S-C6 | accept an unknown `features` name silently | (2) — a `perr` block flips |
| S-C7 | make the composer bind a definition on a block that references none (e.g. treat a lexically-declared name as a file reference) | (1) dump differential — the closure size is reported and must be 0 for all 3,265 blocks |
| S-C8 | assign a definition's re-based numbers starting at 1 instead of `ngroups+1` | (2) — `g` slots move on any composed cell; on the corpus it is vacuous, which is itself the finding S-C7 exists to report |

**MEASURED — the base vocabulary is closed and small.** The complete set
of first tokens over all 179 corpus files, with counts:

```
$ find tests -name '*.rxt' | wc -l                      -> 179
$ (python3 census, first token of every non-blank non-# line)
m 10552  n 6780  g 3942  pattern 3265  ns 3167  features 2146
ms 1603  perr 384  gp 240  flags 36  gu 23  engine 5  budget 3
frames-buffer=<6 distinct values> 8
blank lines 3820   whole-line comments 10585
blocks 3265   expectation lines (m+n+ms+ns+g+gp+perr+gu) 26691
```

Thirteen line kinds, one of which (`frames-buffer=`) is spelled
`key=value` rather than `keyword args` and is **positional within a
block, not block-scoped** (`docs/spec/rxt_format.md`). That wart is
inherited unchanged; the new grammar does not add a second `key=value`
line kind, so `frames-buffer=` stays the sole exception rather than
becoming a precedent.

**MEASURED — every proposed new keyword is unused as a first token.** All
**32** candidates — the six file-level declarations, the two block
starters, the five new block-scoped lines, `config`'s and the data
block's own body vocabularies, and R-SUBST-3's four prior-art
spellings — over all 179 files, count **0**:

```
$ for w in name target lib include config use variant oracle tag mc freq gap \
           def with from testee option repl s sg serr unsupported analysis \
           question reader exemplar bytes sha256 analyzer date row groups; do
      c=$(grep -rh "^$w\b" tests --include='*.rxt' | wc -l)
      [ "$c" != 0 ] && echo "COLLISION $w $c"; done
  -> nothing printed: all 32 are 0
```

This retires the requirements-note appendix bullet "keyword-collision risk
between reserved directive words and named definitions is unexamined
(R27 F10)": examined, and the answer is that the risk cannot arise from
*names* at all, because a definition's name never appears in first-token
position (it is the argument of `name`, of `target … = <name>`, or the
body of a `(?&name)` inside a pattern), and it cannot arise from the new
*keywords* because none of them occurs today.

### 1.2 The file shape — TWO LAYERS

**REWRITTEN AT REVISION 3.1** (Frank's internal-consistency ruling,
consequences 1, 4 and 5). Revision 3 stated the file's shape as one
tangle of rules in which *where structure begins and ends* sometimes
depended on *which keyword opened the line* — the head/body asymmetry,
and the "an indented line is legal only under a declared sub-block
kind" rule. The ruling forbids exactly that. So the grammar is stated
as two layers with a thin, declared interface between them:

- **§1.2.1 the STRUCTURE layer** — how a reader with NO keyword table
  recovers the file's tree from syntax alone.
- **§1.2.2 the SCHEMA layer** — which keywords exist, in which scope,
  what they take, and whether a recovered tree is VALID. Designed in
  full at §2.25.

The test the split has to pass is Frank's own: *"a generic reader must
be able to recover the file's structure — blocks, sub-blocks, line
membership — from syntax alone… Keywords and the schema then say what
the structure MEANS and whether it is valid; they never decide where
structure begins or ends."* §1.2.3 states, without softening, the one
place the format does not fully pass it and what passing would cost.

#### 1.2.1 The STRUCTURE layer

A reader at this layer knows **three devices and two schema
parameters**. It knows no other keyword, no scopes, no value shapes.

**CORRECTED AT REVISION 3.2 (r57 G-B1, a BLOCKER; S-M1 and G-B2's N1/N2
converged on the same object from two other directions).** Revision
3.1 stated the layer as two devices and one parameter, and the block
scalar refutes that: inside a `description |` body an indented `#` is
PROSE and ragged indentation is LEGAL PROSE SHAPE — both measured rc 0
on the shipped binary (§0.8) — neither of which S0 or S1 as written
can produce. A reader that knew only S0-S2 would have to suspend those
rules exactly where the format needs them suspended, and the only way
to know to do so is by reading `\|` and the parent's declared value
form. So the third device is DECLARED rather than left to be
discovered, and the parameter count is stated as two.

**S0 — LINE CLASSES (lexical).** **FOUR classes at revision 3.3, not
three** (r57 ROUND 2, R2-F3): a line is BLANK (**the EMPTY line — zero
bytes — and nothing else**), WHITESPACE-ONLY (nothing but spaces and
tabs, at least one), a COMMENT (`#` in **column 1** — a `#` anywhere
else is data, R-RXT-2), or CONTENT. A line's INDENT is its count of
leading SPACES; **a leading TAB does not open an indent and is refused
by name** (§1.6.1a narrowing (4), TAKEN). An indented `#` is a
structure error naming the rule (*"comments must start in column 1"*,
`rxt_source.c`'s shipped diagnostic, unchanged) — **outside an S3
region; inside one, S0 does not run at all**, which is what keeps
§1.6.1a candidate (2) a narrowing AVOIDED rather than one taken.

> **WHY BLANK NARROWED TO THE EMPTY LINE, and it is the opposite of a
> narrowing in effect.** Revision 3.2 wrote BLANK as "empty or
> whitespace only", and S1/S3 give a BLANK line a TERMINATING effect —
> so that one parenthesis made every whitespace-only line close
> attachments and end prose regions. MEASURED on the shipped binary,
> all three legs do the opposite: `line_indented` (`rxt_source.c:109`)
> tests only whether byte 0 is a space or a tab, so a whitespace-only
> line is *indented*, stays inside a `config` body and stays inside a
> block scalar as BYTES, while `line_blank_or_comment` (`:114`) skips
> it everywhere else. The committed check `sem15`
> (`tests/rxtsource/run_rxtsource_tests.sh:1592`) pins exactly that —
> *"a whitespace-only line is ACCEPTED (ignored) by all three"* — and
> the fixture `whitespace_only_line.rxtin` exists because leg C once
> mis-classified it. Writing BLANK as the empty line restores the
> shipped reading; §1.6.1a's candidates (6) and (7) are the two
> narrowings it dissolves.

**WHITESPACE-ONLY IS INERT, AND THAT IS THE WHOLE RULE.** Outside an S3
region a whitespace-only line has **no structural effect of any kind**:
it is not CONTENT (no indent is read off it, it attaches to nothing and
nothing attaches to it, no first token is dispatched, no schema row is
consulted) and it is not BLANK (it closes no attachment). A reader steps
over it. Inside an S3 region it is BYTES like every other line there,
which is what makes it today's paragraph break (§1.2.5).

> **This is a DEVIATION from the manager's leaning and the measurement
> is why.** The leaning was that a whitespace-only line become
> *attachment-relevant* — indent = its leading whitespace, value empty,
> schema-inert. That formulation dissolves the same two narrowings, but
> it introduces a THIRD one, because S1's own "attaches to nothing" arm
> then fires on two shapes that are legal today: a whitespace-only line
> as the FIRST line of a file, and one immediately after a blank.
> MEASURED, both are accepted by all three legs today (`   \npattern
> a\nm "a" 0 1` and the same shape after an empty line: leg A rc 0, leg
> B rc 0, leg C rc 0). "Inert" is also the shorter sentence and the one
> a generic reader can implement without a special case, so it is taken
> on both grounds. §0.8's ROUND 2 block records it as pushback.

**S1 — ATTACHMENT.** A CONTENT line whose indent is GREATER than the
nearest preceding CONTENT line's **attaches to it as a CHILD**. Equal
indent makes them SIBLINGS. Lesser indent closes back to the nearest
enclosing level with that indent; an indent matching no enclosing level
is a structure error. **A BLANK line and a COMMENT line each close
every open attachment, returning to indent 0** (the head's own
r46sem-10 rule for the blank, now the general one; the comment is NEW
at 3.3, below). A WHITESPACE-ONLY line does nothing at all. A CONTENT
line at indent 0 with nothing before it, or an indented line following
a blank or a comment, attaches to nothing and is a structure error
(*"indented line attaches to nothing"*).

> **THE COMMENT LINE IS A STRUCTURAL DEVICE AND REVISION 3.2 NEVER SAID
> SO** (r57 ROUND 2, R2-F2, a MUST-FIX). S0 declared the class and
> neither S1 nor S3 stated its EFFECT, and silence there is not
> neutral — it reads as "a comment is skipped and the structure around
> it continues", which is a reject→accept WIDENING in two measured
> places and falsifies §1.6.1's claim 2. MEASURED on the shipped
> binary, both are refused today and the refusal is the same one:
> - `config c` / `  flags i` / `# column one` / `  engine vm` —
>   **REFUSED at line 4**, *"indented line continues nothing (the
>   declaration above it takes no continuation)"*. The column-1 `#` is
>   not indented, so `parse_config`'s `if (!line_indented(nx)) break;`
>   (`:727`) ENDS the body, and the `engine vm` line below reaches the
>   file-level loop as an indented line with nothing to continue.
>   Without the terminating rule, S1 would re-attach it to `config c`
>   and accept the file.
> - `description |` / `  line one` / `# column one` / `  line three` —
>   **REFUSED at line 4**, the same message, because `parse_prose`'s
>   `while (line_indented(...))` (`:511`) ends the region there. Without
>   the terminating rule, S3's extent test alone is the indent test, the
>   region would reopen below the comment, and the opener would carry
>   **two disjoint prose regions** — a shape S3's single-extent rule
>   cannot express at all, so the widening is not merely unwanted but
>   unrepresentable.
>
> One sentence in S1 and one in S3 close both. The rule is not a
> carve-out for comments: a comment and a blank line have the SAME
> structural effect, which is the one a reader can remember.

**Why a comment terminates rather than being transparent.** The
alternative — a comment is skipped and the structure around it
continues — is defensible in the abstract and is what most indented
formats do. It is rejected on two grounds, and the second is the
decisive one. (a) It is not what any shipped reader does, and §1.6.1's
claim 2 is a promise about files, not about elegance. (b) Transparency
requires the reader to hold the pre-comment attachment state across an
unbounded run of comment lines and then decide whether the next line
resumes it — which is exactly the "structure depends on what you
remember" property the two-layer split exists to remove. A terminating
comment is a local rule: the reader's state after a COMMENT line is the
same as its state after a BLANK, and neither depends on what preceded
it.

**S2 — GROUPING.** Among SIBLINGS, a line whose first token is a member
of the **BLOCK-OPENER SET** starts a group that absorbs the following
siblings until the next opener at that level or the end of the
enclosing scope. The opener set is closed, declared, and has **exactly
two members: `pattern` and `pattern-esc`** (§2.19).

**S3 — OPAQUE REGIONS (NEW at revision 3.2; its trigger and its
boundary test both CORRECTED at 3.3).** A CONTENT line **whose kind is
PROSE-REGION-OPENING** — structure-layer parameter 2 below — and whose
value, **after trailing spaces and tabs are trimmed, is exactly the
single byte `|`**, opens an OPAQUE REGION. Its EXTENT is structural and
is the only structural fact about it: the region runs from the next
line up to, and not including, **the first of**

- a CONTENT line whose indent is less than or equal to the opener's,
- a BLANK line (S0's, i.e. the empty line),
- a COMMENT line (a `#` in column 1).

A WHITESPACE-ONLY line ends nothing and is bytes. Every line inside the
region is BYTES — **S0 does not run on it, S1 does not attach it, S2
does not test it**. The region's content is the opener line's VALUE;
what it decodes to is a schema question (§1.2.5's `prose-value`), not a
structural one.

**THE TRIGGER IS PARAMETERIZED, and revision 3.2's was not** (r57 ROUND
2, R2-F1, a MUST-FIX). Read literally, 3.2's *"a CONTENT line whose
value is the single byte `|`"* opens a region on **any** such line —
and `pattern |` is a legal pattern today (the alternation of two
empties; MEASURED rc 0, `--list-source` dumps the pattern column as
`|`), so the literal reading turns a working file into a refusal. The
EBNF had the rule right all along (`prose-value`'s own production and
`opaque-region`'s side condition, §1.3) and the normative sentence
contradicted it; the sentence is what moved. The TRIM half is not new
either — it is the shipped rule at `rxt_source.c:1222-1226`, ruled at
W1.1 as r46sem finding 14 (*"a `|` with trailing whitespace is nobody's
intended literal"*), matching leg C's own `v.strip() == '|'`, and pinned
by the committed fixture `desc_pipe_trailing_space.rxtin` (`sem14`,
refused by all three). S3 states the shipped rule rather than a second
one.

**THE BOUNDARY TEST NO LONGER CONTRADICTS ITSELF.** Revision 3.2 said
the region ends at *"the first BLANK line"* while also saying its
interior is *"not classified by S0"* — and BLANK is an S0 class, so the
rule asked a classifier it had just disabled. The scoping is stated
instead of implied: **S0 does not run for DISPATCH or ATTACHMENT inside
the region; the three-way boundary test above is the ONE thing a reader
still computes per line**, and it needs exactly three predicates — is
the line empty, does it begin with a column-1 `#`, and (for a CONTENT
line) what is its indent. Nothing else about a region line is ever
asked. Stated the falsifiable way: *a reader can find a region's end
without tokenising a single line inside it.*

**The extent rule and the shipped loop coincide on today's whole
population, and the reason is worth checking rather than assuming.**
Leg A's region loop is `while (line_indented(...))` — "indented at
all", not "indented more than the opener" — so the two rules could
differ for an opener at indent > 0. They cannot today: `description` is
the only prose-valued kind that exists, and it appears at FILE scope
and (since revision 3.1) at BLOCK scope, both of which are indent 0,
where "indent ≤ 0" and "not indented" are the same test. `config_vocab`
(`rxt_source.c:145`) has no prose-valued member at all. So the general
rule is stated now, at zero cost, rather than being discovered to
disagree with the implementation the day a prose field lands inside a
sub-block.

That is the whole layer. From S0-S3 a reader recovers: every line's
parent, every group's extent, every opaque region's extent, and
therefore blocks, sub-blocks and line membership — with no knowledge of
`config`, `provenance`, `variant`, `m`, `lib` or any other keyword.

**THE STRUCTURE LAYER TAKES TWO PARAMETERS FROM THE SCHEMA, and
revision 3.2 states both rather than one.** Neither is the thing the
ruling forbids — that is a per-keyword structural EXCEPTION decided by
an open-ended table — but both are keyword facts, both are stated as
such, and §1.2.3 prices removing them:

| parameter | schema column(s) | what a generic reader does with it | today's answer |
|---|---|---|---|
| the BLOCK-OPENER set (S2) | `opens_group` | decides where a group starts | two rows: `pattern`, `pattern-esc` |
| the PROSE-REGION-OPENING kinds (S3) | **`value` AND `children`, read as a PAIR** — the kind qualifies iff `value: prose` *and* `children: prose` | decides whether a trimmed bare `\|` value opens an opaque region | today: `description`, `license-note`, `adaptation`, `attribution`, `note` — five rows, and the set GROWS whenever a prose field is added |

**PARAMETER 2 IS ONE PARAMETER READ OFF TWO COLUMNS, stated once here
and nowhere contradicted** (r57 ROUND 2, R2-F4). Revision 3.2 said
`value = prose` in §1.2.1 and §1.2.2, said the PAIR in §2.25.2's
reconciliation and in §1.3's EBNF, and left a reader to guess; three
sites disagreed about a normative fact. **The PAIR wins, and S-R5's
detectability is the tiebreaker.** If the structure layer read `value`
alone, then flipping a row's `children` from `prose` to `none` while
leaving `value: prose` would change NOTHING a reader can observe: the
region still opens, its lines are still bytes, so they never reach a
schema-validity check either — a corrupted normative column with no
detector anywhere, which is the K35 shape the sabotage row exists to
prevent. Reading the pair makes either flip a structural change that
§9's A-group fixtures see, which is why S-R5 (§3.2) now names both
plants. The count of PARAMETERS is unchanged at two; the count of
COLUMNS the structure layer reads is three.

Both parameters are **one `--list-schema` query** (§2.25), so a generic reader
FETCHES them rather than hard-coding them, and both are visible in the
same dump a validity reader already reads. The second is the more
load-bearing of the two and revision 3.1 hid it: the opener set is
closed and two-member, while the prose set is open-ended by
construction — §1.2.5's whole point is that a second prose field
inherits the block scalar rather than inventing it, which is exactly a
statement that this parameter grows.

**Why S3 is a DEVICE and not a value rule.** The obvious objection is
that `\|` is a value-form discriminator (§1.2.4 says so of `"` after
`=` in a `tag-prose` item, and that remains true of `"`), so it should
live entirely in the schema layer. It cannot, and the difference is
measurable: a `tag-prose` value is bounded by the line it is on, so a
reader that ignores the discriminator still gets the line's EXTENT
right and only mis-reads its content. A `\|` value is bounded by
SUBSEQUENT LINES, so a reader that ignores it gets the extent of
everything after it wrong — it will attach prose lines as children,
dispatch their first tokens as line kinds, and classify an indented `#`
as a structure error. **Extent is structure.** That is the test, and
`\|` passes it where `"` does not.

**What S3 costs, stated with the rest of the census.** Declaring the
region does not make its INTERIOR unconstrained by accident — it makes
it unconstrained by decision, and two things that are legal today stay
legal because of it: an indented `#` inside a block scalar (prose, not
a comment error) and ragged prose inside one. Both were on their way to
becoming narrowings under revision 3.1's silence, and §1.6.1a records
them as narrowings AVOIDED rather than as narrowings taken. The
region's own strip rule is a separate, shipped defect and is K57.

**WHAT THIS DELETES.** Three rules in revision 3 stop existing:

1. **"In the HEAD, indentation means CONTINUATION; a pattern block's
   lines are NOT indented."** There is one attachment rule now and it
   is the same rule in both places. A `config` body, a data-block body,
   a `description` attached to a `target`, a block scalar's own lines
   and a `provenance` sub-block's attributes are all S1, and none of
   them is a second mechanism.
2. **"The head ends at the first `pattern` line, and nothing file-level
   may appear after it"** as a STRUCTURAL rule. It survives as a SCHEMA
   rule with the same force and the same diagnostic: `lib`, `target`,
   `config` and friends declare scope `file`, and one appearing inside
   a group is a schema error naming the scope. **AR-4 is discharged
   exactly as before** — a D27-blinded author reading a block still
   looks in exactly one other bounded place — and it is now discharged
   by a declaration a reader can print rather than by a parser's
   control flow.
3. **"An indented line NOT under a sub-block keyword is a hard error."**
   Under S1 an indented line always attaches to something; whether its
   parent ADMITS children is a schema question (`m` declares
   `children: none`). **The loud refusal the bench's M8 measured
   survives in both arms** — a structure error when it attaches to
   nothing, a schema error naming the parent when the parent takes no
   attributes — so N-2's failure is as loud as it was, and it is now
   loud for a reason a reader can look up.

**WHAT IT COSTS: one diagnostic tier, and A CENSUS OF NARROWINGS —
§1.6.1a, five candidates, three taken.** No file changes meaning. A
file legal today is legal, byte for byte (0 corpus lines are indented,
re-measured at 210 files, §0.7). Most refusals that move only change
WHICH message they carry, which D26 puts in the tier this project does
not spend effort on.

**CORRECTED AT 3.2 (r57 G-B2, C-M1; convergence 3).** Revision 3.1 said
"ONE MEASURED NARROWING" and the sentence was wrong twice over: three
more narrowings live in the structure layer's own change and a fifth
lives in §2.22's semantics, and revision 3.1's instrument for finding
them — §1.6.4's own standing rule — was written and then not swept
across the delivery. **§1.6.1a is that sweep, published as a CLOSED
LIST**; this subsection keeps the first candidate because it is the one
the structure layer forces and the one the rule was written from. But
S1 is DEPTH-SENSITIVE and today's head continuation is not, and that
difference is real:

> **THE RAGGED-BODY NARROWING, found by probing rather than by reading
> the code.** Today's parser asks only "is this line indented?", so a
> `config` body whose lines sit at DIFFERENT depths parses as a flat
> body. MEASURED on the shipped binary — a `config c` with `flags i` at
> two spaces and `engine vm` at FOUR produces a `--list-source` row
> **byte-identical** to the evenly-indented file (`flags=i`,
> `engine=vm`, rc 0). Under S1 the four-space line attaches to the
> two-space `flags` line as a CHILD, `flags` admits no children, and
> the file is refused. **That is accept → reject on a construct that is
> legal today**, which is a narrowing and not a re-wording, and §1.6.1
> is corrected to say so rather than counting it as additive.

It is admitted deliberately, on three grounds, each measured:

1. **The population is provably empty, in both repos.** `config`
   occurs 0 times in the 210-file corpus; the **20** head declarations
   carrying an indented body in `tests/rxtsource/fixtures/` — across
   **13 of the 45** files — are every one uniformly indented, at width
   2 without exception; and `pcrec-bench` contains no `.rxt`/`.rxtin`
   file at all today (read-only check). Nothing anywhere is narrowed
   in fact. **(Corrected at 3.2, r57 G-B7: revision 3.1 said 19. The
   21st candidate a naive scan finds and the one width-3 line are the
   SAME line — `whitespace_only_line.rxtin:9`, pure whitespace, which
   S0 classifies BLANK and not CONTENT, so it is neither a body line
   nor a counter-example to uniformity. The fixture exists precisely
   because leg C once mis-classified it, which is why it is worth
   naming rather than silently excluding.)**
2. **It is FORCED by the feature, not gratuitous.** Depth has to become
   meaningful the moment a record can contain a record — which §2.10's
   `provenance`-under-a-data-block is, two levels of S1 — so a
   depth-insensitive rule is not available to choose. Ragged
   indentation cannot both be tolerated and mean something.
3. **It converts a silent authoring hazard into an error.** A body
   whose lines drift in depth reads as nesting and parses as a flat
   list; under the old rule the author is never told. This is the
   direction a tightening should go.

§1.6 is the version-break argument, and §1.6.4's standing rule is
amended to cover the narrowing case that this finding exposed as a gap
in it.

**AND IT MAKES A RULE THE THREE READERS CAN ACTUALLY BE HELD TO.**
Revision 3 asserted "the indentation test PRECEDES token dispatch" in
all three body readers. MEASURED (§0.7), that was true of ONE of them:
leg A tests indentation first (`rxt_source.c:992`), leg B has no
indentation test at all (an indented line reaches `run.sh`'s catch-all
by fall-through through 22 arms none of which tolerates leading
whitespace), and leg C dispatches an indented PRE-BODY line on its
first token before reaching its own check — **pre-body only: `:424`'s
check is unconditional once a block is open** (§0.7, r57 C-N9). Under
S1 the ordering is not an extra rule to remember — **indent determines
the parent, and only then does the parent's schema decide what the
first token may be** — so "dispatch after attachment" is the layering
itself, and §9's A-group pins it with an indented-line fixture in all
three legs, **at the PRE-BODY position**, rather than trusting three
independent implementations to have got an ordering right. The position
is load-bearing and is named in the check rather than left to whoever
writes the fixture: a post-body fixture reaches `:424` in leg C and
would report GREEN against the very defect it exists to pin
([MECH-REACH]'s shape, r57 S-M5).

#### 1.2.2 The SCHEMA layer

Everything else is schema, and §2.25 designs it. Stated here only as
the boundary:

- **Scopes.** `file` (indent-0 lines before the first group), `block`
  (indent-0 lines inside a group), and one scope per parent kind that
  admits children (`config`, `data`, `provenance`, `variant`). A scope
  is a set of legal line kinds — the "closed lexical context" rule
  revision 2 stated, now a schema column rather than a parser fact, and
  no longer capped at four: a scope is created by declaring one.
- **Per line kind**: its scope, its value shape, whether it opens a
  group, whether it admits children and in which scope, its
  cardinality, its required/conditional status, and whether its value
  is drawn from a closed set.
- **THREE of those columns are READ BY THE STRUCTURE LAYER, as TWO
  parameters**, and the rest are validity (§1.2.1's parameter table,
  which is normative): `opens_group` is parameter 1; `value` and
  `children` together are parameter 2, a kind opening a prose region
  iff it carries `value: prose` AND `children: prose`. **(3.3, r57
  ROUND 2 R2-F4: revision 3.2 wrote "two columns … `value = prose`"
  here and the PAIR in §2.25.2 — one normative fact with two
  spellings.)** The boundary between the layers is therefore not "the
  schema knows nothing structural" — it is that the structure layer
  reads exactly three columns, all closed-form, and never dispatches on
  a kind's identity.
- **A first token unknown IN ITS SCOPE is a hard error naming the
  scope** ("`testee` is not a pattern-block directive"). Nothing is a
  keyword everywhere. Unchanged in force; now derived from a table.

#### 1.2.3 Where the format does NOT pass, stated plainly

**Block GROUPING is not recoverable from syntax alone, and no wording
makes it so.** A `pattern` line and its `m`/`n`/`g` lines are all at
indent 0 and are siblings by S1; what makes the case lines BELONG to
the pattern is S2's opener set, which is a keyword fact. A reader given
nothing but the bytes sees **35,961** flat sibling lines.

**(Corrected at 3.2, r57 G-B6: revision 3.1 wrote 28,943 here, which is
the EXPECTATION-line count — a partition a generic reader cannot
compute, since computing it requires knowing which first tokens are
case kinds. The number this sentence needs is every non-blank,
non-comment line, which is 35,961 over the 210 files. The point gets
stronger, not weaker: a quarter more lines sit in the undifferentiated
heap than the first figure admitted.)**

Three things about that, each measured rather than argued:

- **It is TODAY'S SHIPPED GRAMMAR's failure, not W23's.** Version 1 of
  this format has exactly this property and always has; nothing
  revision 3 or 3.1 adds makes it worse, and §1.2.1's two devices make
  everything else pass.
- **No cheaper structural device is available in the corpus.** The
  obvious candidate — a blank line separates blocks — is refuted:
  **1,016 of 3,936 `pattern` lines (26%) are immediately preceded by a
  blank line** (§0.7). A rule the corpus obeys 26% of the time is not
  a rule.
- **The only fix is to INDENT case lines under their `pattern` line**,
  making grouping S1's job and emptying the opener set. That is a
  break, and §1.6 prices it and declines it.

Stated the other way round, so the claim is falsifiable — **and
RESTATED AT 3.2 against the two-parameter baseline, because revision
3.1's version of this sentence counted one parameter and there are
two**: *with a two-row opener table AND the prose-region-opening kind
set (the `value`/`children` pair, 3.3), structure recovery is complete
and context-free.* Both are one
`--list-schema` query, and together they are the entire residue of
"keywords decide structure" in the format. The honest reading of the
second: the opener set is closed at two and can be quoted in a
sentence; the prose set grows, so a reader who hard-codes today's five
rows will be wrong the day a sixth prose field lands, which is exactly
why the fetch is specified and the values are not.

#### 1.2.4 Bare indentation vs a visible sub-block MARKER

Frank's consequence 4 — *"if the design needs sub-blocks, it CREATES
syntax that marks them — never overloaded indentation whose meaning
depends on which keyword opened the line"* — was read two ways and both
were designed before one was chosen.

**The marker alternative, designed.** A sub-block opener carries a
trailing sigil and its children are indented as now:

```
provenance:
  source fowler
variant re2:
  text ^a{1,4}$
```

(The sibling variants — a leading sigil on each child, `- source
fowler`; or brace delimiters — were considered together with it: they
differ in spelling and not in what follows, because all three make the
parent's intent explicit at the cost below.)

**Priced against long-term viability, the marker LOSES on three
counts** — **and revision 3.2 re-runs the comparison against §1.2.1's
TWO-PARAMETER baseline rather than 3.1's one-parameter one (r57 G-B1),
because the marker's case is strongest exactly where the baseline is
weakest.** The re-run does not change the decision; it changes count 1,
which was overstated, and it names what the marker genuinely buys.

1. **It makes structure depend on two signals that can disagree** — and
   **CORRECTED AT 3.2 (r57 G-B4): the resulting error class does not
   DISAPPEAR under bare indentation, it RELOCATES to the schema
   layer.** Revision 3.1 said neither disagreement state is
   expressible; that is true of the state as a STRUCTURE error and
   false of the state itself. "Indented children under an unmarked
   line" is expressible today and is refused — as a schema error naming
   the parent (`m` declares `children: none`, §1.2.1's deletion 3). And
   "a marker with no indented children" has a live shipped analogue in
   the very construct 3.1 cited as the counter-example: `description |`
   with nothing indented under it is **refused by name today**
   (`rxt_source.c:514`, *"block scalar '\|' has no indented
   continuation lines"*), which is precisely the disagreement state
   count 1 called inexpressible. So the honest form of the count is:
   the marker moves two error classes from the schema layer to the
   structure layer and adds a third (marker-plus-wrong-depth), where
   bare indentation keeps them all in the layer that can name the
   offending PARENT. That is a smaller claim than 3.1's and it still
   points the same way, because a structure error cannot say which
   declaration the author got wrong and a schema error can.
2. **The format already ships indentation-attachment, unmarked**, in
   the head: `config` bodies and `description |` block scalars have
   been parsed that way since W1.1 by all three readers. Adding a
   marker means either a second mechanism beside the shipped one (the
   accretion consequence 1 forbids) or a breaking change to a shipped
   production for no capability.
3. **"This kind admits children" is a SCHEMA fact, and a marker spells
   it once per occurrence.** That is the schema restated in every file
   that uses the production — the duplication §2.25 exists to remove,
   and the thing that goes stale when the schema changes and old files
   do not.

**What the marker WOULD buy, stated because the two-parameter baseline
makes it real.** A trailing sigil would let a generic reader answer
"does this line admit children?" without consulting the schema — which
is a VALIDITY question for every kind except the prose ones (§1.2.2),
so it buys nothing the structure layer needs. It would NOT remove
either parameter the structure
layer actually reads: `opens_group` would still be needed for block
grouping (a marker on `pattern` would be the §1.6.2 break by another
spelling, since it changes every existing file), and the
prose-region-opening set would still be needed for S3, because `\|`'s
own region is opened by a VALUE and a sigil on the opener line does not
tell a reader where the region ENDS. **(3.3: a sigil meaning "takes
prose below" would express `children: prose` alone, which is half of
parameter 2 — the half that says a region MAY open, never the half that
says one DID; `\|`'s presence on the line is still what opens it.)** **So the marker's price is three error classes and a
per-occurrence restatement of the schema, and its yield against the
stated baseline is zero parameters removed.** That is a stronger
decision than revision 3.1 could make, because 3.1 was comparing
against a baseline that undercounted its own cost.

**DECISION: bare indentation, no new marker.** The consequence-4
obligation is met by §1.2.1's unified rule, S3's declared region, and
§2.25's printable schema: *which kinds open a scope* and *which kinds
take a prose value* are both answerable exactly, by `--list-schema`,
once, rather than by a sigil a file may or may not carry.

**The `|` block scalar IS a structural device, and revision 3.2
withdraws the sentence that said otherwise** (r57 G-B1). Revision 3.1
wrote: *"Both are value-form discriminators… neither decides where a
line attaches."* Measurably false of `|` — inside a `description |`
body an indented `#` is prose and ragged indentation is legal (§0.8),
neither of which S0/S1 can produce — so `|` decides how every line
after it is treated, which is what "decides where a line attaches"
means. It is now **S3**, declared in §1.2.1, and the distinction that
survives is narrower and true:

| | `\|` (a prose value) | `"` after `=` (a `tag-prose` item) |
|---|---|---|
| what it discriminates | the value's FORM — on this line, or on the lines below | the value's FORM — bare token, or quoted with whitespace |
| where the value ENDS | on SUBSEQUENT lines, by S3's extent rule | on THIS line, by the closing quote |
| a reader that ignores it | mis-parses the extent of everything after it | mis-reads one line's content |
| layer | **structure (S3) + schema (the `value`/`children` PAIR, 3.3)** | schema only |

"Value-form discriminator" was the right CONCEPT and the wrong
CONCLUSION: a discriminator that selects a multi-line form is a
structural device wearing a value's clothes. §2.26 item 8's pairing of
the two stands as a vocabulary observation and is re-worded there to
stop implying they live in one layer.

#### 1.2.5 The lexical rules, restated under the two layers

- Whole-line `#` comments only, column 1 (S0). The one comment with
  meaning — `# pcre2-only` immediately before a `pattern` line — keeps
  it, and is defined in §2.9 as an alias. **A comment line also CLOSES
  ATTACHMENT and ends an open prose region, exactly as a blank line
  does (3.3, S1/S3)** — the only structural effect a comment has, and
  the reason §1.6.1's claim 2 survives.
- Blank lines close attachment (S1) and carry no other meaning. **A
  BLANK line is the EMPTY line (3.3); a WHITESPACE-ONLY line is inert
  outside a prose region and bytes inside one.**
- A line kind is its first whitespace-delimited token, dispatched
  **within the scope its attachment put it in** (S1 then schema).
- **One line, one value — with exactly one exception, the BLOCK
  SCALAR.** A line kind whose schema row carries `value: prose` AND
  `children: prose` may write `<kind> |` — trailing spaces and tabs
  after the `|` are trimmed before the test, the shipped rule
  (`rxt_source.c:1222-1226`, r46sem finding 14) — and continue on lines
  indented under it; newlines are preserved and **the value ends where
  S3 says the OPAQUE REGION ends** — at the first CONTENT line indented
  no more than the opener, the first BLANK (empty) line, or the first
  column-1 COMMENT line. The one-line form `<kind> <text>` stays. The
  exception is a property of the VALUE production (`prose-value`), not
  of any keyword, so a second prose field inherits it rather than
  inventing it — and inheriting it grows the structure layer's second
  parameter (§1.2.1), which is the cost of the generality and is worth
  naming where the generality is claimed.
  **CORRECTED AT 3.2 (r57 G-B1):** revision 3.1 said the value ends
  "where S1 says the attachment ends", which put a prose region under
  the attachment rule. It is not under it — S1 does not run inside the
  region at all, which is exactly why an indented `#` there is prose
  and ragged prose there is legal (both MEASURED, §0.8). S3 is the rule
  that carries this sentence.
- **Inside the region, nothing is a line kind.** A prose line whose
  first token happens to spell `pattern`, `m` or `provenance` is prose.
  This is not a carve-out; it is S3 having no dispatch step.
- **MULTI-PARAGRAPH PROSE, and the one spelling that carries it**
  (3.3). An INDENTED WHITESPACE-ONLY line is the paragraph break: it is
  inside the region, it is bytes, and after the block's indent is
  stripped it decodes to an empty line in the value. MEASURED on the
  shipped binary — `description |` / `  para one` / three spaces /
  `  para two` dumps the value `para one\n \npara two`, rc 0. It is the
  ONLY spelling available, because r46sem-10 ruled that a truly empty
  line ENDS the continuation, and it does: the same file with a
  zero-byte separator is **REFUSED** at the line below it (*"indented
  line continues nothing"*). That is why S0's BLANK class had to narrow
  to the empty line rather than S1/S3 growing an exception — the
  whitespace-only line is not an oddity the format tolerates, it is the
  only way the format can currently say "new paragraph", and revision
  3.2's parenthesis would have deleted it.
- **`prose-value` is legal wherever the schema declares a prose value,
  at any depth** — file level, a `config` body, a sub-block attribute,
  and (NEW at 3.1, see below) a pattern block's own `description`.
  Continuation lines are indented deeper than the line they continue,
  which is S1 and not a second rule.

**REVISION 3.1 SUPERSEDES THE W1.1 `description` CORRECTION, and says
so rather than quietly widening a refusal.** That correction made a
pattern block's `description` one-line-only, and BOTH of its reasons
have expired:

- Its stated reason was *"§1.2 says a pattern block's lines are NOT
  indented and a block scalar IS indented continuation; both cannot be
  true in the body"*. Under §1.2.1 there is no such asymmetry, so the
  contradiction it resolved does not arise.
- Its implementation reason was *"a block scalar in the body would need
  continuation parsing inside `run.sh`'s per-line loop — head-shaped
  parsing back in the harness"*. **W23 requires legs B and C to consume
  indented children anyway**, for `provenance` and `variant`; a block
  scalar needs the SAME consumption and no more, because a reader that
  does not READ the value still only has to consume its children. That
  is §2.24's VALIDATES-vs-RECOGNISES split doing its job: pcrec reads
  the prose, the harness skips it.

So `description` takes `prose-value` in every scope — **one prose
mechanism, everywhere**, which is what §2.14 rule 6 already promised and
what the surviving carve-out contradicted. **This is the ONE shipped
refusal revision 3.1 changes, and it changes it in the widening
direction only**: MEASURED, 0 corpus blocks carry a `description` and 0
corpus lines are indented, so no existing file moves. The committed
fixture `tests/rxtsource/fixtures/block_scalar_in_body.rxtin` asserts
the refusal in all three legs and must be **re-aimed, not deleted** —
inverted to assert all three ACCEPT it and agree on the decoded value,
which is a strictly better fixture because a three-way agreement on a
value catches more than a three-way agreement on a rejection. §3.4
SW16 carries it and §9's A-group names it.

#### 1.2.6 Sub-blocks under the two layers

With S1 doing the structural work, a **sub-block is no longer a
mechanism** — it is a schema declaration that a kind admits children.
Revision 3's two customers are unchanged: `provenance` (§2.14) and
`variant` (§2.23), and `provenance` is now used at two different
parents (a pattern block and a data block, §2.26's unification), which
is the general form earning its keep rather than a special case with
two instances.

What survives from revision 3's rules, and where each now lives:

| revision 3 rule | revision 3.1 |
|---|---|
| indentation test precedes dispatch | **the layering itself** (S1 then schema); pinned in all three legs by §9's A-group rather than asserted of three implementations |
| a bare indented line is a hard error | **still a hard error**, in one of two arms (attaches to nothing → structure; parent takes no children → schema). M8 stays loud |
| a sub-block's vocabulary is a fourth closed context | **a scope**, declared like every other; the count is not fixed at four |
| sub-block ends at the first non-indented line including a blank one | **S1**, unchanged in effect — and S3 for a prose region, whose extent rule is the same shape stated once more (3.2). **At 3.3 both terminate on THREE things, and the same three**: a CONTENT line at or below the opener's indent, a BLANK (empty) line, and a column-1 COMMENT line; a whitespace-only line terminates neither, which is the shipped behaviour of all three legs |
| the attribute vocabulary avoids the token `pattern` | still true, for a NEW reason — §2.26 item 9. The old reason (an indented `pattern` might start a block in one reader) is **impossible in any reader that implements S1/S2**, since an opener applies among SIBLINGS and a child is not a sibling. **Qualified at 3.2 (r57 S-S5)**: "structurally impossible" is a statement about the SPECIFICATION, and legs B and C are independent implementations of it (§2.25.5) — leg B has no attachment step today at all. It is impossible by construction in leg A once H16 lands and it is a property legs B and C must be PINNED to, which is §9's A-group's job, not an inheritance |

Regime grouping is still NOT a sub-block customer — §2.22 repairs the
wrapper mechanism instead, and the reasons there are unchanged by this
revision (a case scope is ruled out by Frank by name, independently of
how indentation is spelled). A generator writing an included fragment
still writes pattern blocks only (§2.5); it indents exactly when it
writes children.

### 1.3 The productions

Each production carries its wave: **W1** composition, **W2** large and
generated sets, **W3** per-engine / per-config application. A parser may
ship W1 alone and reject W2/W3 keywords with "not in this build"; the
grammar is designed so that is a *subset*, never a *dialect of a
dialect*.

**How to read this grammar after revision 3.1.** The EBNF below is the
two layers written together, the way a reader wants them; §1.2.1 and
§2.25 are the two layers written apart, the way a parser is built from
them. Specifically: every `{ INDENT , … }` below is ONE rule, S1, not a
per-production choice — the productions show WHERE children are legal
(a schema fact) over a structure that admits them uniformly. A
production's scope (`file` / `block` / a named child scope) is likewise
a schema column here written as grammatical position. Nothing in the
EBNF grants a keyword structural power; where it looks like it does,
§2.25's table is the normative statement.

```ebnf
(* ---------- terminals ---------- *)
ident       = ( "A".."Z" | "a".."z" | "_" ) , { "A".."Z" | "a".."z" | "0".."9" | "_" } ;
                              (* a PCRE2 group name AND a C identifier *)
int         = "0".."9" , { "0".."9" } ;
rest-of-line = ? every byte to the end of the line, verbatim ? ;
subject     = quoted-subject | file-subject ;
quoted-subject = '"' , { subject-char | escape } , '"' ;    (* today's, unchanged *)
escape      = '\"' | "\\" | "\n" | "\t" | "\r" | "\f" | "\v" | "\x" , hex , hex ;
file-subject = '@file:"' , path-chars , '"' ,
               [ ws , "as" , ws , defname ] ,                     (* W23 *)
               [ ws , "sha256" , ws , hex64 ] ;                   (* W23 *)
path-ref    = '"' , path-chars , '"'                    (* local, C's "" *)
            | "<" , store-name , ">" ;                  (* library path, C's <> *)
config-list = ident , { "," , [ ws ] , ident } ;
tag-item    = tag-label | tag-pair | tag-prose ;                  (* U1; W23 *)
tag-label   = ? a bare label: no whitespace, no '=' ? ;
tag-pair    = tag-key , "=" , tag-value ;   (* tag-value: no whitespace, no '=' *)
tag-prose   = tag-key , "=" , quoted-subject ;  (* W23: the seven escapes, ONE
                 vocabulary — a value whose first byte after '=' is '"' is the
                 quoted form and must terminate; whitespace legal inside *)
prose-value = rest-of-line                        (* one-line form *)
            | "|" , { " " | tab } , eol , opaque-region ;
                 (* block scalar; §1.2.1 S3. The trailing whitespace is
                    TRIMMED before the test — rxt_source.c:1222-1226,
                    r46sem finding 14, and leg C's own v.strip() == '|' *)
opaque-region = ? every line until the FIRST of: a CONTENT line indented no
                more than the opener, a BLANK (empty) line, or a column-1
                COMMENT line — S3. A WHITESPACE-ONLY line ends nothing and is
                bytes. Its interior is BYTES: not line-classified (an
                indented '#' is prose), not attached (ragged depth is legal),
                not dispatched. The EXTENT is the only structural fact; the
                decode is `prose-value`'s.
                A kind may open one iff its schema `value` is `prose` and
                its `children` is `prose` — structure-layer parameter 2,
                read as a PAIR (§1.2.1) ? ;
INDENT      = ? one or more SPACES at the start of the line. A leading TAB
                does not open an indent and is refused by name
                (§1.6.1a narrowing (4)) ? ;
defname     = ? the wide name grammar: [A-Za-z_] then [A-Za-z0-9_.-]
                (rxt_source.c's defname_ok — one grammar, three readers) ? ;
hex64       = ? exactly 64 lowercase hex digits ? ;

(* ---------- file ---------- *)
file          = head , body ;
head          = { file-decl | config-block | data-block } ;
body          = { pattern-block } ;

(* ---------- head: file-level declarations ---------- *)
file-decl   = decl-line , { INDENT , decl-attr , eol } ;   (* indented attrs *)
decl-line =
      "lib"        , ws , path-ref                                 (* W1 *)
    | "include"    , ws , path-ref                                 (* W2 *)
    | "target"     , ws , ident , ws , "=" , ws , ident ,
                     [ ws , "with" , ws , config-list ]            (* W1 *)
    | "use"        , ws , config-list                              (* W3 *)
    | "oracle"     , ws , oracle-spec                              (* W3 *)
    | "tag"        , ws , tag-item , { ws , tag-item }             (* W2 *)
    | "vocabulary" , ws , tag-key , ws , tag-value , { ws , tag-value }
                    (* W23: the FILE-declared half of the schema (§2.25) *)
    | "configs"    , ws , ( "build" | "describe" )                (* W23 *)
    | "description", ws , prose-value ;                            (* W1 *)

(* RESERVED, not a production: `version` is refused BY NAME in every
   build (§1.6). Its absence means version 1; it exists so a future
   structural break has a spelling nobody can already have used. *)

decl-attr   = "description" , ws , prose-value ;   (* attaches to decl-line *)

oracle-spec = "none" , ws , rest-of-line                          (* W3 *)
            | engine-ref ;    (* W23 widening: ident [ "/" version ] — `python`
                 and `pcre2` are engine-refs with no version and keep their
                 exact meanings; any other engine is R-VG-3's labelled skip *)

(* ---------- head: config block ---------- *)
config-block = "config" , ws , ident , [ ws , "from" , ws , config-list ] , eol ,
               { INDENT , config-line , eol } ;   (* `from` is W1 — G3 *)
config-line =
      "pcrec"    , ws , rest-of-line          (* raw pcrec flags        W1 *)
    | "flags"    , ws , letters               (* as a pattern block's   W1 *)
    | "features" , ws , module-list           (* as a pattern block's   W1 *)
    | "encoding" , ws , ident                 (* D58's per-pattern axis M16 *)
    | "engine"   , ws , ( "vm" | "dfa" )      (* as a pattern block's   W1 *)
    | "budget"   , ws , budget-item           (* as a pattern block's   W1 *)
    | "analysis" , ws , data-kind , ws , ident  (* select a data block  W2 *)
    | "testee"   , ws , engine-ref            (* a non-pcrec engine     W3 *)
    | "option"   , ws , tag-pair              (* that engine's options  W3 *)
    | "provides" , ws , tag-value , { ws , tag-value } ;
                    (* W23: the capability tags this config SATISFIES;
                       repeatable, accumulating; ABSENT means NOTHING is
                       satisfied — fail-closed (§2.16). SPELLED `provides`
                       at revision 3.1 (was `capable`) — §2.26 item 4:
                       the pattern side's key is `requires`, and the two
                       ends of one relation must read as a pair *)

engine-ref = ident , [ "/" , version-chars ] ;      (* e.g. pcre2/10.42 *)

(* ---------- head: data block (the analysis FAMILY, §2.10) ---------- *)
data-block = data-kind , ws , ident , eol , { INDENT , data-line , eol } ;
data-kind  = "freq" ;                    (* the family's only member    W2 *)
data-line =
      "description" , ws , prose-value   (* the summarizing script's field *)
    | "question" , ws , rest-of-line     (* what this answers, required *)
    | "reader"   , ws , rest-of-line     (* the selection point, required *)
    | "analyzer" , ws , rest-of-line     (* the TOOL that produced it,
                                            required — not provenance *)
    | provenance-block                   (* WHERE it came from: the SAME
                                            sub-block a pattern block takes
                                            (§2.26 item 10). At revision 3.1
                                            this replaces the five one-off
                                            fields `exemplar`/`bytes`/
                                            `sha256`/`date` this production
                                            used to carry beside `analyzer` *)
    | "row"      , ws , int , ws , int , { ws , int } ;  (* offset, then 16 counts *)

(* ---------- body: a pattern block ---------- *)
pattern-block = pattern-line , { block-line } ;
pattern-line  = "pattern" , ws , rest-of-line , eol          (* today's *)
              | "pattern-esc" , ws , quoted-pattern , eol ;       (* W23 *)
quoted-pattern = '"' , { subject-char | escape } , '"' ;
                    (* the SAME seven escapes; §2.19's rules; `\x00` refused
                       by name (K9). A block carries exactly ONE pattern line
                       because a block IS what one opener starts — both
                       spellings are members of S2's opener set, so a second
                       one is the NEXT BLOCK, not a second line in this one.
                       Revision 3's "never both, refused naming both lines"
                       is DROPPED at 3.2: empty population, §2.19 *)
block-line =
    (* --- today's, unchanged --- *)
      "flags"    , ws , letters
    | "features" , [ ws , "only" ] , ws , module-list  (* `only` is new: M14 *)
    | "engine"   , ws , "vm"
    | "budget"   , ws , budget-item
    | "frames-buffer=" , route
    | "perr"
    | "m"  , ws , subject , ws , int , ws , int
    | "n"  , ws , subject
    | "ms" , ws , int , ws , subject , ws , int , ws , int
    | "ns" , ws , int , ws , subject
    | "g"  , ws , slot , ws , span
    | "gp" , ws , slot , ws , span
    | "gu" , ws , giveup-code , ws , subject
    (* --- new --- *)
    | "name"        , ws , defname            (* W1; widened at W1.3 *)
    | "description" , ws , prose-value        (* W1; the one-line-ONLY
                       carve-out is SUPERSEDED at revision 3.1 — §1.2.5 *)
    | "encoding"    , ws , ident        (* D58's per-pattern axis    W1 M16 *)
    | "export"      , ws , config-list                          (* W1.3 *)
    | "tag"         , ws , tag-item , { ws , tag-item }            (* W2 *)
    | "mc"          , ws , subject , ws , int                      (* W2 *)
    | "under"       , ws , tag-value , ws , under-case            (* W23 *)
    | "oracle"  , ws , oracle-spec                                 (* W3 *)
    | provenance-block                                            (* W23 *)
    | variant-block ;                              (* W3, reshaped at W23 *)

under-case  = ( "m" | "n" | "ms" | "ns" | "mc" ) -case-line-as-above ;
              (* the qualifier wraps a case line UNCHANGED; never g/gp/gu —
                 §2.17 *)

(* ---------- the two kinds that ADMIT CHILDREN (§1.2.6) ---------- *)
(* `provenance` is ONE record shape used at TWO parents — a pattern block
   and a data block (§2.26 item 10). Its REQUIRED subset differs by
   parent and is a schema row, not a second production. *)
provenance-block = "provenance" , eol , { INDENT , prov-line , eol } ;
prov-line =
      "source"       , ws , rest-of-line  (* a registered slug, or the
                                             exemplar's name — REQUIRED *)
    | "url"          , ws , rest-of-line  (* the exact URL fetched         *)
    | "ref"          , ws , rest-of-line  (* file/rule/line inside it      *)
    | "license"      , ws , token         (* an SPDX id. REQUIRED under a
                                             pattern block (§2.26 item 10) *)
    | "license-note" , ws , prose-value
    | "retrieved"    , ws , iso-date      (* RFC 3339 date,       REQUIRED *)
    | "fidelity"     , ws , ( "verbatim" | "adapted" | "inspired" )
                                          (* REQUIRED under a pattern block *)
    | "adaptation"   , ws , prose-value   (* REQUIRED iff fidelity is not
                                             verbatim *)
    | "attribution"  , ws , prose-value   (* the field exists; the license
                                             policy is the consumer's *)
    | "bytes"        , ws , int           (* integrity: the source's size  *)
    | "sha256"       , ws , hex64 ;       (* integrity: its digest         *)

variant-block = "variant" , ws , ident , eol ,
                { INDENT , variant-attr , eol } ;
variant-attr =
      "text"        , ws , rest-of-line   (* the replacement pattern text *)
    | "kind"        , ws , tag-value      (* closed via `vocabulary kind` *)
    | "groups"      , ws , group-map
    | "note"        , ws , prose-value    (* the reviewer's sentence      *)
    | "unsupported" , ws , rest-of-line ; (* a declared refusal, reason   *)
group-map    = ident , "=" , int , { "," , ident , "=" , int } ;
```

**That is the whole grammar.** Revision 2's count was sixteen additions
(seven file-level declarations, two head block kinds, seven block-scoped
lines) plus §1.5's three pattern-level extensions. Revision 3 adds, all
W23 and all for the [B42] consumer: two head declarations (`vocabulary`,
`configs`), one config-body line (`provides`), a second block starter
(`pattern-esc`), one case-line qualifier (`under`), two child-admitting
kinds (`provenance`; `variant` reshaped from its W3 one-line form), a
`tag-item` third alternative (`tag-prose`), and two optional suffixes on
`file-subject` (`as`, `sha256`). Every addition is ADDITIVE against the
shipped corpus — a new first token measured at 0 occurrences (§0.6,
re-measured at 210 files in §0.7), an extension of a production the
shipped build refuses by name, or new syntax at a position that is a
hard error today (an indented body line; text after an `@file:` path) —
so R-COMPAT-1 holds production by production, and §9's G1 row says how
that is checked.

**Revision 3.1 adds NO production.** It re-FACTORS the rules (§1.2),
reserves one keyword without giving it a production (`version`, §1.6),
and **moves THREE spellings under §2.26's ownership audit**: `capable` →
`provides`, `licence`/`licence-note` → `license`/`license-note`, and
the `freq` data block's five one-off provenance fields → the shared
`provenance` sub-block. All three were never shipped anywhere and have
zero uses in either repo, so they cost a diff and nothing else.
A FOURTH change moves in the same delivery and is **not** one of the
audit's: a pattern block's `description` goes from `rest-of-line` to
`prose-value`, which is §1.2.5's consequence of the structure-layer
re-factoring — a WIDENING of a shipped refusal, arrived at from the
internal-consistency ruling rather than the ownership one, priced at
§1.2.5. (**Corrected at 3.2, r57 C-N11**: revision 3.1 counted all four
as §2.26 moves here and as "four spellings moved" in §0.7, which
attributed a widening to an audit that changed no semantics by
construction. The outbox message to the bench inherits the corrected
framing; §9's correction list keeps the row under its true cause.)

**Revision 3.2 adds no production either, and REMOVES one refusal**:
§2.19's "a block carries `pattern` or `pattern-esc`, never both", whose
population is empty under §1.2.1's own opener rule (r57 S-BL2). It also
declares one structure-layer device that was already shipped and
undeclared (S3, §1.2.1) and makes explicit two rules the EBNF above now
carries in its `opaque-region` and `INDENT` terminals.

**CORRECTION ([DD-13b.W1.1], 2026-08-30) — SUPERSEDED AT REVISION 3.1,
kept here because a reader of the shipped tree will meet its
consequence.** It made a pattern block's `description` one-line-only,
on the ground that *"§1.2's lexical rules say a block scalar IS
indented continuation and that a PATTERN BLOCK's lines are NOT
indented; both cannot be true in the body"*, and on the ground that a
body block scalar would need continuation parsing inside `run.sh`'s
per-line loop. **Both grounds expire at revision 3.1**: §1.2.1 deletes
the asymmetry the first rests on, and W23 gives all three readers the
child-consumption the second says they must not have — for
`provenance` and `variant`, independently of `description`. §1.2.5
carries the full argument, the measurement (0 blocks carry a
`description`, 0 lines are indented, so nothing moves), and the
`block_scalar_in_body.rxtin` re-aim. Until W23 lands, the shipped
behaviour is the correction's: refused by name in all three parsers.

**`description` is a FIELD, not a comment** (Frank, r44 15:0x): *"we may
want to summarize via script what a library or other rxt file has:
therefore a description may be helpful outside of comments, which should
be operational."* So it is machine-readable, it exists at file level,
per definition block, per target and per data block, and `#` comments go
back to being operational notes only. This **overturns §7 Q1's
recommendation in the first version** — `NOTES.md` is no longer where a
library's or a sub-bench's prose lives.

### 1.4 The waves after F-Q1: W1 (built) and ONE W23 delivery

**RESTRUCTURED at revision 3** (Frank's F-Q1, 2026-09-12): there is no
W2-only cut. The former W2 and W3 rows, plus every [B42] extension,
land as **ONE delivery, W23**, whose consumer is the bench's [B42]
capability survey set — the consumer that earns it, by ruling. D77 is
still honoured at the wave granularity: W23 ships because its named
consumer is real and PARKED on it.

| wave | productions | status / consumer |
|---|---|---|
| **W1** | `name`, `description` (both forms), `lib`, `target … [with]`, `encoding`, `features only`, `export`, `config` with `pcrec`/`flags`/`features`/`encoding`/`engine`/`budget`/`from`; AST composition with §1.5's extensions, the delivering calls and `--emit-composed`; `rx_info.name`/`nentries`; H11's target build path | **BUILT** — [DD-13b.W1.1] (2026-08-30), .2 (2026-08-31), .3 (2026-09-03). Owed, NOT blockers: **W1.3.1** (run.sh's composed-block path, `w13_runsh_composed_path.patch`) and **W1.4** (the in-pattern delivery follow-ons). W23 interacts with neither — no W23 production touches the composer except §2.22's derived-identifier LOOKUP, which is additive |
| **W23** | the former W2: `include`, `@file:`, `mc`, `tag`, the `freq` data block + `analysis`; the former W3: `use`, `oracle`, `variant`, `config … testee`/`option`; the [B42] extensions: `pattern-esc`, `provenance`, `vocabulary`, `provides`, `under`, `configs describe`, `as`/`sha256` on `@file:`, `oracle` at a version, `tag-prose`, the §2.22 regime repair, and `--list-source` emitting ALL of it (§2.24) | **THIS revision's delivery.** Consumer: the [B42] capability survey set (Frank's ruling); [ENG-PGO]'s findings file rides the same landing (its row said "blocks on wave 2/3") |

**What remains after W23, named so the wave table ends honestly:** the
`gap` data-block member (unearned, D77), `--list-source --resolved`
(named and unbuilt), [V-E]'s multi-pattern unit, `(?&site.group)` (free,
measured, not built — w1_impl §9.4), iterated capture (D87 rule 5's
explicit exclusion), the [M4-SUBST] `repl`/`s`/`sg`/`serr` slots (that
row's own), expressing a NUL **in a pattern** (parked on K9's
`pattern_len` API half, §2.19), and W1.3.1/W1.4 above. After W23 the
format has no designed-but-unbuilt production a real consumer is waiting
on.

**W23 carries NO abi event.** Every W23 production is format-, harness-
or CLI-side; nothing changes emitted scaffolding, so D76's ritual is not
triggered and the identity gate's pin does not move. Stated here because
every prior wave's landing note had to answer this question late.

### 1.5 The PATTERN-level extensions, and the one constraint they all obey

D87 adds three things to the pattern language itself, not to the `.rxt`
line grammar: a **numbered group**, a **scope prefix** on a subroutine
call, and a **delivering-call declaration**. Frank ruled the semantics
and left the spellings to the manager (r44, 14:5x). This section
recommends one spelling each, names the alternatives, and gives the
measurement that admits or rejects each candidate.

**THE CONSTRAINT, and it is testable: no legal PCRE2 pattern may change
meaning.** Every candidate is therefore checked by compiling it on
libpcre2 10.46 — a candidate PCRE2 already accepts is disqualified, not
merely disfavoured, because adopting it would silently re-interpret
patterns that exist in the world.

**MEASURED** (`docs/design/eng_brep_measurements/probes/pcre2_ctypes.py`,
libpcre2 10.46; every row cross-checked on `build/pcrec --features all`,
which agreed):

| candidate | libpcre2 10.46 | verdict |
|---|---|---|
| `(?<3>a)` | refused — "subpattern name must start with a non-digit" | **free** |
| `(?<name=3>a)` | refused — "syntax error in subpattern name" | **free** |
| `(?3:a)` | refused — "missing closing parenthesis" | **free** |
| `(?<3,name>a)` | refused | **free** |
| `(?&^.w)` | refused — "subpattern name expected" | **free** |
| `(?&caller.w)` | refused — "syntax error in subpattern name" | **free** |
| `(?&from=email)` | refused — "syntax error in subpattern name" | **free** |
| `(?&=email)` | refused — "subpattern name expected" | **free** |
| `(?&&email)` | refused — "subpattern name expected" | **free** |
| **`(?<from>&email)`** | **COMPILES — matches the literal `&email`** | **DISQUALIFIED** |

**RE-MEASURED AND EXTENDED 2026-09-03 (lane w13, libpcre2 10.46
2025-08-27, the same `pcre2_ctypes.py` binding).** D89's addenda put three
NEW spellings on the table and every one of them owed this measurement
before adoption. The run reproduced the two controls above — `(?&^.w)`
refused, `(?<from>&email)` COMPILES — so the instrument is agreeing with
the record before it is trusted on anything new:

| candidate | libpcre2 10.46 | verdict |
|---|---|---|
| `(?&site=x)` | refused — *"syntax error in subpattern name (missing terminator?)"* at offset 7 | **free** — B3's delivering call, named site |
| `(?&=x)` | refused — *"subpattern name expected"* at offset 3 | **free** — B3's delivering call, default site |
| `(?&*=x)` | refused — *"subpattern name expected"* at offset 3 | **free** — addendum 4(3)'s flat import |
| `(?&site.group)` | refused — *"syntax error in subpattern name"* at offset 7 | **free** — B2's path reference to a delivered group |
| `(?&*.x)` | refused — *"subpattern name expected"* at offset 3 | free, but NOT ADOPTED (addendum 4(3) supersedes it with `*=`) |
| `(?&!.x)` | refused — *"subpattern name expected"* at offset 3 | free, but NOT ADOPTED (addendum 3: the plain call is already the no-save form) |

The last two rows are measured deliberately even though neither is
adopted. A spelling that was CONSIDERED and dropped for a design reason is
worth separating from one that was dropped because PCRE2 already means
something by it — the difference is exactly what disqualified
`(?<from>&email)`, and a table that recorded only the adopted rows could
not tell the two kinds of "no" apart.

The last row matters: `(?<from>&email)` was the leading shape for the
delivering declaration, and it is an ordinary PCRE2 named group whose
body is the two-character literal `&email`. On both oracles it matches
the subject `&email` at (0,6). **Adopting it would change the meaning of
a legal pattern**, which is the one thing the constraint forbids, so it
is rejected on a measurement rather than on taste.

#### B1 — the numbered group: **`(?<3>…)`, and `(?<name=3>…)` for both**

RECOMMENDED. Names and numbers are two halves of one thing — a group's
IDENTITY — so they belong in one bracket with one dispatch point, and the
named-and-numbered form then falls out instead of needing a second
syntax. A parser dispatches on the character after `(?<`: `=` or `!` is a
lookbehind (unchanged), a digit is a number, a name character is a name
followed by an optional `=<digits>`.

- Alternative **`(?3:…)`** — closest to Frank's own shorthand `(3:abc)`,
  and it reads as `(?:` with a number. Rejected only because it has no
  natural named-and-numbered form, which would then need a third
  spelling.
- Alternative **`(?<3,name>…)`** — same bracket, comma separator.
  Rejected because `=` reads as assignment and a comma reads as a list.

#### B2 — the scope prefix: **`(?&^.name)`**, a PATH

RECOMMENDED, with `^` as the reserved segment meaning "one scope up".
D87 rule 3 asks for "a reserved scope word for the caller"; a WORD would
occupy the name space and could collide with a call-site name, whereas
**`^` is not a name character at all, so it can never collide**. It also
makes the prefix a genuine path — `^.^.name` is two scopes up by
construction, and downward paths are the delivering call's member names
(`from.local`, §2.13), so one grammar serves both directions:

```
(?&name)          this scope's definition            (PCRE2's, unchanged)
(?&^.name)        the CALLER's group `name`
(?&from.local)    the delivered group `local` of the call site `from`
```

- Alternative **`(?&caller.name)`** — readable, and D87's own leading
  shape. Rejected because `caller` is a legal call-site name, so a file
  that names a delivering call `caller` would make the prefix ambiguous.
- Only ONE level up has a named consumer today; `^.^.` is admitted by the
  grammar rather than built for (D77).
- The objection worth recording: `^` reads as an anchor everywhere else
  in a pattern. It is unambiguous here (inside `(?&…)` there is no
  anchor position) but a reader meets it in an unfamiliar role.

#### B3 — the delivering call: **`(?&site=name)`, and `(?&=name)` for the default**

RECOMMENDED. **One rule: an `=` in the call makes it delivering; the name
to the left of it is the member, and an empty left side means the
definition's own name.**

```
(?&email)          plain call, capture-transparent   (PCRE2's, unchanged)
(?&=email)         delivering; member `email`
(?&from=email)     delivering; member `from`
```

The assignment order (`member = source`) matches C, matches the path
(`r.from.local`), and puts the site name where the struct member name
goes. Both extended forms are refused by PCRE2 today (measured above).

- Alternative **`(?<from>&email)`** — **DISQUALIFIED by measurement**: a
  legal PCRE2 pattern today (above).
- Alternative **`(?&&email)`** — free, and visually distinct, but it
  needs a second form for the named case and "a reference to a
  reference" means nothing.
- The weak point, stated: `(?&=email)` reads slightly oddly for the
  common case. The alternative — making the DEFAULT the bare `(?&email)`
  and delivering implicit — was rejected because D87 rule 5 requires an
  undeclared call to stay capture-transparent at zero cost, so delivery
  must be something a site opts into visibly.

#### The serialization: **`--emit-composed`**

RECOMMENDED name, kept from D87's own placeholder. It writes the composed
pattern with every group's number spelled explicitly in B1's form, and
pcrec accepts what it writes (D87 rule 4, §2.3.4). Alternatives
considered and not taken: `--emit-pattern` (says nothing about
composition), `--emit-flat` (suggests inlining, which this is not — the
call structure is preserved and only the numbers are made explicit).

**Wave: all four are W1**, because composition is W1 and none of them is
optional to it — B1 is what `--emit-composed` prints and what rule (c)'s
collision error is about, B2 and B3 are how a definition reaches outside
itself and how a caller reaches inside. B2's multi-level `^.^.` and B3's
refusal cases are the parts with no consumer yet, and they are grammar,
not machinery.

### 1.6 The `version` header — the break PRICED, DECLINED, the keyword RESERVED

Frank's consequence 2: *"A breaking `version` header line is ON THE
TABLE. A file declaring the new version gets the consistent grammar; a
file without one parses under today's rules byte-for-byte — R-COMPAT-1
is preserved by VERSIONING, not by freezing the grammar. Whether the
break is taken, and what exactly it unifies, is the design lane's to
work out and the panel's to attack."*

**The answer is NO, and it is not a soft no.** The version line is
DECLINED because the consistent grammar does not need it; the keyword
is RESERVED because the one change that WOULD need it is real, named
and priced below.

#### 1.6.1 Why §1.2's consistency is achievable ADDITIVELY

The version line exists to gate a change that makes an existing file
mean something different. §1.2 contains no such change. Three claims,
each falsifiable:

1. **No file that parses today parses differently.** The only rule
   whose *domain* changed is indentation, and **0 of the corpus's
   lines are indented** (re-measured at 210 files, §0.7). Beyond the
   corpus: today's grammar has no legal indented line ANYWHERE outside
   a head continuation, and S1 attaches a UNIFORMLY-indented `config`
   body, block scalar or `target` `description` to the same parent it
   continues today. **CORRECTED — the first draft of this claim said
   S1 reproduces head continuation "exactly", and a probe refuted it:**
   S1 is depth-sensitive where today's rule is not, so a RAGGED body
   (lines at differing depths) goes from accepted to refused. §1.2.1
   carries the finding, the empty population measured in both repos,
   and the three grounds for taking it. Claim 1 therefore reads: no
   file with UNIFORM indentation parses differently, and the ragged
   case is a narrowing declared under claim 2a below rather than
   counted as additive.
2. **No file that is REFUSED today is accepted, with one deliberate
   exception in the widening direction.** Deleting the head/body
   asymmetry moves some refusals from a structure arm to a schema arm
   and changes their wording; it accepts nothing new, because a parent
   that took no children still takes none (`m` declares
   `children: none`). The exception is §1.2.5's `description |` at
   block scope, which goes from refused to accepted — and an
   acceptance-widening is by definition not a compatibility break for
   any file that exists.

   **CORRECTED AT 3.3 (r57 ROUND 2, R2-F2): this claim was FALSE as
   revision 3.2 shipped it, in two measured places, and the cause was a
   SILENCE rather than a rule.** S0 declared the COMMENT class and
   neither S1 nor S3 stated its structural effect, so a reader
   implementing 3.2 literally would skip a column-1 `#` and carry the
   surrounding structure across it — accepting two files the shipped
   binary refuses at line 4 (a `config` body with a column-1 comment in
   the middle; a `description |` region with one, which additionally
   produces the two-disjoint-regions shape S3 cannot express). Both are
   reproduced in §0.8's ROUND 2 block. **The repair is one sentence in
   S1 and one in S3 — a comment terminates attachment and ends a
   region, exactly as a blank line does — after which claim 2 is true
   again with its single stated exception.** The general lesson is the
   one the panel drew twice in two rounds: *a line class declared in S0
   and given no effect in S1/S2/S3 is not a neutral line class, it is
   an undeclared structural decision*, and it will be read in whichever
   direction the reader's habits supply. S0's four classes now each
   have their effect stated where the effect lives.

2a. **THE NARROWINGS, declared, and the list is CLOSED**: §1.6.1a is
   the census. **CORRECTED AT 3.2 (r57 G-B2, C-M1; convergence 3):
   revision 3.1 wrote "ONE NARROWING" here, and the number is three
   taken out of five candidates.** The correction matters more than the
   count: revision 3.1 wrote §1.6.4's standing rule FROM the ragged-body
   finding and then did not run that rule across the rest of its own
   delivery, so three more narrowings in the structure layer and one in
   §2.22's semantics went undeclared. **An instrument built from one
   finding and not swept is the failure this revision records against
   itself**, and §1.6.1a is the sweep. **RE-SWEPT AT 3.3 (r57 ROUND 2,
   R2-B and R2-C): eleven candidates, seven taken — two of them landed
   by STEP 0 rather than by this revision, and the census says which.**
3. **Every new production is a fresh token.** All 52 candidates measure
   0 in first-token position at today's 210 files (§0.7).

Diagnostic wording is the whole residue, and D26 puts it in the tier
this project does not spend effort on. **A version line whose only
content is "refusals are worded differently now" would be a permanent
mechanism bought with a transient inconvenience.**

#### 1.6.1a THE NARROWING CENSUS — the closed list, eleven candidates

**NEW AT REVISION 3.2** (r57 G-B2 N1/N2/N3, C-M1, S-M1 — the panel's
convergence 3); **RE-SWEPT AT 3.3** (r57 ROUND 2 R2-B, R2-C, R2-F3).
The method is §1.6.4's own rule applied to the WHOLE delivery rather
than to the one case that produced it: for every rule this revision
states, ask whether some file legal on the shipped binary becomes
refused. Eleven candidates were found by PROBE (§0.8), not by reading;
**seven are TAKEN and four are AVOIDED**. Each taken row carries the
full package the rule demands — population measured in both repos,
forced-vs-chosen stated, and a spec sentence named — and each avoided
row says what avoids it, because a narrowing avoided by a DECISION
needs recording exactly as much as one taken (the decision is what a
later wave could undo without noticing).

**SCOPE — the census is the .rxt format's, not this lane's** (3.3, r57
ROUND 2 R2-B). Two of the taken rows, (10) and (11), landed in
`[DD-13b.W23]` **STEP 0** (lane `rxtnul`, commit `d4576c48`) rather
than in this design revision, and they are carried here anyway with
their provenance marked. The reason is where a reader looks: somebody
asking *"what did W23 stop accepting"* comes to this table, and a list
that calls itself CLOSED while two accept→reject changes from the same
plan row sit outside it is a list that answers the question wrongly. A
census scoped to one lane's diff is a diff; a census scoped to the
FORMAT is a compatibility story.

| # | the construct | today | under 3.2/3.3 | verdict |
|---|---|---|---|---|
| (1) | a head body whose lines sit at DIFFERING depths (`config c` / `flags i` at 2 / `engine vm` at 4) | ACCEPTED, parsed flat — `--list-source` row byte-identical to the evenly-indented file (rc 0) | REFUSED: the deeper line attaches to `flags`, which admits no children | **TAKEN, FORCED** |
| (2) | an indented `#` inside a `description \|` body | ACCEPTED as PROSE (rc 0; the value carries the `#` line verbatim) | ACCEPTED as PROSE — S3 says S0 does not run inside the region | **AVOIDED by S3** |
| (3) | ragged indentation inside a `description \|` body | ACCEPTED (rc 0), relative indentation preserved | ACCEPTED — S1 does not run inside an S3 region | **AVOIDED by S3** |
| (4) | TAB indentation (`config c` / `\tflags i`) | ACCEPTED (rc 0, `flags=i engine=vm`); `line_indented` (`rxt_source.c:109`) tests space OR tab | REFUSED by name: S0 counts leading SPACES, and a leading tab is a structure error naming the rule | **TAKEN, CHOSEN** |
| (5) | a call `(?&x_y)` where `x_y` and `x-y` are both definitions in scope | ACCEPTED — binds to the exact-spelled `x_y`, the sibling inert; artifact byte-identical to the file without the sibling | REFUSED: §2.22's collision rule, exact spelling does not win | **TAKEN, CHOSEN** |
| (6) | a WHITESPACE-ONLY line inside a `description \|` body — today's only paragraph break | ACCEPTED, and it is IN the value (rc 0; `para one\n \npara two`) | ACCEPTED — S0's BLANK is the EMPTY line, so a whitespace-only line ends nothing and is bytes | **AVOIDED at 3.3** |
| (7) | a WHITESPACE-ONLY line in a `config` body, between case lines, at file start, or after a blank | ACCEPTED (ignored) by all three legs, pinned by `sem15` | ACCEPTED — a whitespace-only line is INERT to the structure layer | **AVOIDED at 3.3** |
| (8) | a second `name` / `engine` / `encoding` / `features` / `flags` line in one block or one `config` body | ACCEPTED, SILENTLY LAST-WINS (measured on all five) | REFUSED naming both lines: `cardinality: at-most-one` (§2.25.2) | **TAKEN, CHOSEN** |
| (9) | a second `budget` line repeating the SAME field (`steps=` twice) | ACCEPTED, silently last-wins (50 then 99 dumps 99) | REFUSED naming both lines — but a second `budget` line naming the OTHER field stays legal, because `budget`'s cardinality is `accumulate` | **TAKEN, CHOSEN** |
| (10) | an embedded NUL byte anywhere in a `.rxt` file | ACCEPTED and SILENTLY TRUNCATING (`pattern ab<NUL>cd` compiled as `ab`, exit 0) | REFUSED by name | **TAKEN, FORCED — landed by STEP 0 (lane `rxtnul`), not by this revision** |
| (11) | a second `description` line in one block, or a second at file level | ACCEPTED, silently last-wins in the block case | REFUSED naming both lines | **TAKEN, CHOSEN — landed by STEP 0 (lane `rxtnul`), not by this revision** |

**(1) THE RAGGED HEAD BODY — taken, FORCED.**
*Population*: 0. `config` occurs 0 times in the 210-file corpus; the 20
fixture head bodies are uniformly indented at width 2 without
exception; pcrec-bench holds no `.rxt`/`.rxtin` file.
*Forced, not chosen*: §1.2.1's three grounds — depth must become
meaningful the moment a record can contain a record (§2.10's
`provenance` under a data block is two levels of S1), so a
depth-insensitive rule is not available to choose.
*Spec sentence*: SW16.

**(2) AN INDENTED `#` INSIDE A BLOCK SCALAR — AVOIDED, and it was one
probe away from being taken silently.** Revision 3.1's S0 said "an
indented `#` is a structure error" with no region carve-out, which
would have made this a narrowing nobody declared. It is avoided by S3,
not by luck.
*Why it matters beyond the case*: the shipped parser's own comment
(`rxt_source.c:735-747`) says the grammar decision here — whether a
column-1-relative comment is legal inside a head continuation — is
**deliberately LEFT OPEN** ("named rather than fixed… the grammar
decision is left open (sem10's sibling)"). Revision 3.1 closed an open
question by side effect, in the refusing direction, without noticing it
was open. **S3 closes it the other way and says so**: inside a prose
region a `#` is prose, because the region has no line classifier.
Outside one — in a `config` body — the indented-`#` refusal is
UNCHANGED and keeps its improved wording
(`tests/rxtsource/fixtures/indented_comment_in_config.rxtin` pins it).
*Spec sentence*: SW16 states both halves, because the pair is the rule.

**(3) RAGGED PROSE INSIDE A BLOCK SCALAR — AVOIDED by S3**, same
mechanism as (2): S1 does not run inside the region, so prose may sit
at any depth greater than the opener's and relative indentation
survives into the value. Without S3 this would have been (1)'s narrowing
applied to prose, whose population is the one place ragged indentation
is not a mistake — a paragraph with an indented example in it.
*Note, and it is NOT a narrowing*: the shipped strip rule corrupts a
DEDENTED prose line (`  ab…` under a 4-space block loses two bytes of
content, MEASURED §0.8). That is wrong today and wrong under every
revision of this note; it is filed as `docs/dev/known_issues.md` **K57**
and fixed there, not here. S3's extent rule is deliberately silent
about it: extent is structure, the strip is a value decoding, and K57
lives in the second.

**(4) TAB INDENTATION — taken, CHOSEN, and the choice is stated as
one.**
*Population*: 0 tab-indented content lines in either repo (210 corpus
files + 48 fixtures; pcrec-bench has no files of this kind).
*Chosen, not forced*: a depth rule CAN be defined over mixed tabs and
spaces — pick a tab width, or compare prefixes bytewise. Neither is
available honestly. A tab width is a convention the file cannot
declare, so two readers with different conventions would recover
different TREES from the same bytes, which is the one failure the
structure layer exists to prevent; a bytewise prefix comparison makes
`"\t"` and `"        "` incomparable, so a body mixing them has no
defined parent chain and the rule would have to refuse at the first
disagreement anyway — the same refusal, arrived at later and worded
worse. MEASURED, the shipped parser is in exactly this position today:
a `config` body whose first line is indented 2 spaces and whose second
is indented by a TAB parses FLAT (rc 0), because `line_indented` asks
only "is byte 0 a space or a tab" and never compares depths at all. The
moment depth means something, that file has no answer.
So the rule is: **indentation is SPACES; a leading tab is refused by
name**, with a diagnostic that says so rather than reporting a
mysterious attachment failure. Long-term viability is the criterion
(Frank's ownership ruling), and a format whose tree depends on an
undeclared tab width is not viable.
*What it does NOT touch*: a tab INSIDE a value is data and stays data —
`pattern` is rest-of-line verbatim and three corpus blocks carry a
literal tab in their pattern text (w1_impl's own measurement). The
narrowing is about leading whitespace only.
*Spec sentence*: SW16.

**(5) THE DERIVED-IDENTIFIER COLLISION — taken, CHOSEN, and it is the
one that is not in the grammar at all.**
This is §2.22's rule "exact spelling does NOT win", and the panel found
it by looking where revision 3.1's own instrument had not: in the
SEMANTICS, after the head. That is why §5.2a attack 1 is re-aimed (it
pointed the panel at the head).
*Population*: **0** for this exact shape in both repos — no file
anywhere holds a definition spelled `x_y` beside one spelled `x-y` or
`x.y`. The nearest neighbour is the general collision shape (two
definitions whose mapped identifiers are equal, neither of them spelled
as the identifier), whose population is **1**: the deliberate fixture
`tests/rxtsource/fixtures/target_prefix_collision.rxtin` (`a-b` beside
`a.b`), which is already a refusal fixture and whose behaviour this rule
does not change. Measured over 96 `name` lines in 26 files;
pcrec-bench contributes 0 because it holds no `.rxt`/`.rxtin` file.
*MEASURED, the accept side*: `(?&x_y)` with only `x_y` defined
compiles; with `x-y` added beside it, the artifact is **byte-identical**
(equal output basenames in separate directories — comparing `a.c`
against `b.c` reports a false difference on the `#include` line, this
house's third recorded instance of that trap). So the sibling is inert
today and the call resolves; under §2.22 the same file is refused.
*CHOSEN, not forced, and §1.6.4 gains a fourth case for it*: the
derived-identifier lookup could tie-break on exact spelling and it
would be well-defined. It is refused instead because the mapping is
deliberately non-injective and a silent tie-break makes the
non-injectivity free exactly where it bites — a file that adds a
hyphenated definition would silently change which definition an
unrelated call binds to, and nothing would say so. **The
forced-vs-chosen distinction is honest here and revision 3.1's §1.6.4
had no slot for it**, because its case 3 assumes every narrowing is
forced.
*Spec sentence*: SW12 (the `name`-grammar section's amended paragraph),
which is where the mapping and its refusal already live.

**(6) AND (7) THE WHITESPACE-ONLY LINE — AVOIDED at 3.3, and revision
3.2 was one parenthesis away from taking both.** 3.2's S0 read
*"BLANK (empty or whitespace only)"*, and S1/S3 give BLANK a
TERMINATING effect, so every whitespace-only line in the corpus would
have closed an attachment or ended a prose region. (6) is the sharp
one: it is not an oddity but **the only paragraph break the format
has**, since r46sem-10 ruled the empty line ENDS a block scalar
(MEASURED both ways — the whitespace-separated file dumps
`para one\n \npara two` at rc 0, the empty-separated one is refused at
the line below it). (7) is the wider population: a whitespace-only line
between case lines, at file start, and after a blank, each accepted by
all three legs today and pinned for the first of those by the committed
check `sem15`.
*What avoids them*: S0's BLANK narrows to the EMPTY line and a
whitespace-only line is stated INERT outside a region, bytes inside one
(§1.2.1). *This is the decision a later wave could undo without
noticing*, which is why it is a census row and not a footnote: widening
BLANK back to "empty or whitespace" is a one-word edit that silently
refuses every multi-paragraph description in the tree.

**(8) DUPLICATE SCALAR SETTINGS LINES — taken, CHOSEN, and the
inconsistency being fixed is the shipped surface's own.** R2-C's
observation is that `cardinality` is normative on every schema row
(§2.25.2), so whatever H16 assigns to a kind that silently last-wins
today IS an accept→reject decision, made implicitly if it is not made
explicitly.
*MEASURED, the shipped binary's five answers, one probe each*: a second
`name` (`n1`→`n2`), `engine`, `encoding` (`byte`→`utf8`), `features`
(`backrefs`→`classes`) or `flags` line is ACCEPTED and the LAST one
wins, with no diagnostic — while a second `export` line is REFUSED by
name (*"a block has one 'export' line; this one already declared
'yes'"*, `rxt_source.c:1184`). One surface, two answers to one
question.
*Population*: **0** in both repos — 0 blocks of 4,053 and 0 of 19
`config` bodies carry a duplicate of any of the five, over 258
`.rxt`/`.rxtin` files; pcrec-bench holds no file of either kind
(re-confirmed read-only at this revision). *`flags` is the panel's list
plus one*: R2-C named `name`/`engine`/`encoding`/`features`/`budget`,
and measuring the shipped arms found `flags` in exactly the same state.
It is taken with them rather than left as the one scalar kind that
still last-wins, which would reproduce the inconsistency one kind
smaller.
*Chosen, not forced*: last-wins is well-defined and is what most
configuration formats do. It is refused because this format's own
precedent already went the other way twice — `export` at W1.3 and
`description` at STEP 0, row (11) — and because the failure mode is
silent: a file with two `encoding` lines is a file whose author
believes something false about it, and nothing tells them. *What it
would cost to revisit*: one `cardinality` value per row, no mechanism.
*Spec sentence*: SW16, beside the structure rules, with the
`cardinality` column as the citable declaration.

**(9) A DUPLICATE `budget` FIELD — taken, CHOSEN, and it is the row
where the measurement CHANGED THE DECISION.** `budget` is the one kind
on R2-C's list whose population is NOT zero, and the non-zero member is
deliberate: `tests/harness/giveup.rxt:19-23` writes
`budget steps=50` and `budget frames=4096` as two lines of one block,
and `parse_setting` (`rxt_source.c:615-620`) routes them to two
separate slots. So `budget` is not a scalar kind at all — **it is
ACCUMULATE over a two-member field set**, and `cardinality:
at-most-one` would have refused a corpus file that the same `make test`
run depends on.
*Population*: duplicate `budget` LINE in one block: **1** (the file
above, legal and intended). Duplicate `budget` FIELD — the same
`steps=` or the same `frames=` twice, which IS silent last-wins
(MEASURED: `steps=50` then `steps=99` dumps 99): **0** in both repos.
*So the narrowing taken is the field-level one, population 0*, and the
line-level one is not taken at all.
*The general lesson, and it is the reason the brief required the
measurement first*: a cardinality is a property of the VALUE SPACE a
kind writes into, not of the kind's spelling. Four of these six kinds
own one slot and one owns two, and nothing in the line's syntax says
which — only the population did.
*Spec sentence*: SW16, with `budget`'s field set named, since
"accumulate over these two fields" is not derivable from the row's
`value` shape alone.

**(10) AND (11) STEP 0's TWO REFUSALS — taken, landed by lane
`rxtnul` (`d4576c48`), carried here for scope.** (10), the embedded
NUL, is **FORCED**: `slurp_lines` hands out NUL-terminated C strings,
so without a pre-scan a NUL mid-line truncates whatever value it falls
inside, and `pattern ab<NUL>cd` compiled as `ab` at exit 0 — a silent
wrong answer, which is not a rule the format may choose to keep. Its
population is 0 files in both repos, and pcrec-bench's own M1 is what
raised it. (11), the duplicate `description`, is **CHOSEN** on exactly
row (8)'s reasoning one kind earlier, and STEP 0 took it for the block
case (where `block->description` is a single field and the first line
silently lost) and extended it to the file case for consistency even
though the file case never lost data. Population 0 in both repos.
*Spec sentence*: `docs/spec/rxt_format.md`'s own STEP 0 hunks, already
landed — these two rows cite rather than owe.

**What the census does NOT contain, and why the absence is checked
rather than assumed.** Every other rule this revision states either
widens (§1.2.5's `description |` at block scope), re-words a refusal
that stays a refusal (the head/body asymmetry's two arms), or adds a
token measured free (the 52-candidate census). The productions were
swept one at a time against the shipped binary; the sweep's own limit
is stated in §5.2a — a critic looking for a TWELFTH should look where
this one did not, which is now the value layer rather than the head.
**And the census records what it is not**: it lists NARROWINGS. The two
WIDENINGS revision 3.2 shipped by silence — a column-1 comment carrying
structure across itself, in a `config` body and in a prose region — are
claim 2's business, not this table's, and are recorded at §1.6.1 claim
2 with their repair.

#### 1.6.2 What WOULD trigger it, and what it would cost

Exactly one thing on today's horizon: **making BLOCK GROUPING
structural** (§1.2.3), by indenting a block's case lines under their
`pattern` line and emptying S2's opener set. That is the change a
version line is for — every existing file means something different
under it (its case lines would attach to nothing), so it cannot be
additive by any spelling.

Priced honestly, because the panel will attack whichever way this goes:

| | |
|---|---|
| **What it buys** | structure recovery with a genuinely EMPTY keyword table — the literal reading of consequence 5 |
| **Corpus cost** | 210 files, 28,943 expectation lines re-indented. Mechanical, and a one-line script; but it is a diff touching every test file in the repo, and AR-1 forbids forcing re-verification of the corpus |
| **External cost** | every producer of `.rxt` text forks: pcrec-bench's five committed exports, the D27 blinded-author corpora, the possessify/rungselect/counterk generators, `--emit-composed`. Each must emit two dialects or flag-day |
| **Reader cost** | a file's most-read region (the case lines) gains a level of indentation forever, to remove one token from a table nobody reads by hand |
| **R-COMPAT-1** | survives only in the versioned sense — old files parse under old rules — which means TWO grammars in three readers, permanently, which is the thing consequence 1 is about one level up |

**DECLINED.** The benefit is a property of a hypothetical generic
reader; the cost is paid by every real one. §1.2.3 states the shortfall
plainly instead, which is the honest form of the answer.

#### 1.6.3 The reservation, and why it is cheap insurance

`version` is **refused BY NAME in every build**, with the "NOT IN THIS
BUILD" sentence SW13's list already owns — never as an unknown token
(K14's shape: sending a reader hunting a typo in a word that is in the
spec). Its absence means **version 1**, stated in the spec so the
default is a contract rather than an accident, and its position is
fixed in advance: **the first CONTENT line of the file**, so a reader
can dispatch on it before parsing anything else.

- **Cost: one row in the schema and one line in the spec.** MEASURED,
  `version` occurs 0 times in first-token position across 210 files
  (§0.7), so reserving it takes nothing away.
- **What it buys: the one thing reservation ever buys** — that the day
  a break is justified, the spelling for announcing it is not already
  in use by somebody's file. The format has no other way to say "read
  me under different rules", and inventing one under pressure is how a
  format acquires `#!`-style warts.
- **`schema` was considered and NOT reserved.** A file-declared
  format-level schema is not the design — §2.25 makes the schema
  pcrec's, and `vocabulary` is the file-declared half with its own
  spelling. Reserving a word against a future nobody has named is the
  D77 failure in its cheapest disguise, and one reservation with a
  named trigger is a different act from two on principle.

#### 1.6.4 The standing rule this leaves

For the next person who asks, in three cases rather than two — **the
third was added because revision 3.1's own change fell between the
first two and the gap was found by a probe, not by reading the rule**:

1. **No version line**: a change that only widens acceptance, only
   re-words a refusal, or only adds a token measured free.
2. **A version line, mandatory**: a change that makes an existing file
   MEAN something different. It may not ship without one.
3. **A FORCED NARROWING (accept → reject, where no other rule was
   available) needs no version line, but needs three things in the
   change that lands it**: the population MEASURED rather than assumed
   (in this repo and in pcrec-bench, since a format has two users), a
   stated argument that no alternative rule exists, and a sentence in
   the spec so a file refused tomorrow that parsed yesterday has a
   citable answer. §1.6.1a's case (1) is the worked example and the
   reason this clause exists.
4. **A CHOSEN NARROWING — the same three, PLUS the alternative named
   and priced.** NEW AT 3.2 (r57 C-M1), because revision 3.1's case 3
   assumed every narrowing is forced and two of this delivery's three
   are not. When a well-defined alternative rule exists — tolerate
   tabs under a declared width; tie-break the collision on exact
   spelling — the change must say what the alternative would be, why it
   was rejected, and what it would cost to revisit. A narrowing
   defended as "forced" when it was chosen is worse than one defended
   as chosen, because it forecloses the revisit: the next reader has no
   way to tell that a decision was made at all. §1.6.1a's cases (4),
   (5), (8), (9) and (11) are the worked examples — **five of the seven
   taken rows are CHOSEN, which is itself the measurement that made
   this case necessary.**

5. **MEASURE THE POPULATION BEFORE DECIDING, not after** (NEW at 3.3,
   from §1.6.1a case (9)). Cases 3 and 4 both require the population;
   3.3 is where that requirement earned its keep in the deciding
   direction rather than the documenting one. R2-C proposed one
   cardinality for six settings kinds on an internal-consistency
   argument, and the argument was right for five of them — the sixth,
   `budget`, has a non-zero population whose single member is a
   DELIBERATE corpus file, and taking the narrowing as proposed would
   have refused it. The population is not evidence that a decision is
   safe; **it is an input to what the decision should be.**

**And a sixth thing the census made explicit, which is not a case but a
DUTY**: the rule above is an instrument, and an instrument that is
written from one finding and then not swept across the delivery finds
exactly that one finding. Revision 3.1 wrote case 3 out of the
ragged-body probe and declared "ONE NARROWING"; there were five
candidates and the other four were one probe each. **A change landing
under this rule sweeps its whole delivery and publishes the result as a
CLOSED LIST**, including the narrowings AVOIDED and what avoids them —
so a later wave that removes the avoiding mechanism can see what it is
removing. **And the sweep is over the FORMAT, not over the lane's own
diff** (3.3): revision 3.2 swept its own sections honestly and still
published a "closed" list missing two accept→reject changes that landed
in the same plan row one step earlier, because the sweep's boundary was
a branch rather than a grammar. A census whose scope is a diff answers
a question nobody asks.

§2.25's schema is what makes all of it checkable — a schema diff
between two builds shows exactly which rows moved and in which
direction, so "additive" stops being a claim a lane makes about its own
change. **That is the concrete argument for the schema being data**:
every one of §1.6.1a's eleven candidates was found by running the
shipped binary on a hand-made file, and a machine-diffable declaration
is how the next one gets found without the hand-made file. **Cases (8)
and (9) are the argument at its strongest**: they are nothing but a
`cardinality` value, so the change from last-wins to refused IS a
one-column schema diff, and the day somebody proposes a twelfth the
diff will show it before any file is written. Note the honest limit,
though: case (5) is a SEMANTIC narrowing in the composer's name lookup,
which no schema row describes, and case (10)'s NUL refusal is a lexical
pre-scan below the schema entirely — so the schema diff would have
caught nine of eleven, and §5.2a says where the other two kinds live.

---

## 2. Semantics

### 2.1 Scope: two levels, and exactly one cascading thing

Frank's ruling 4: two scopes only (file-top, block); cascade only inside
`config … from`; `include` is pure splice. Concretely:

- **File scope** is the head. Its declarations apply to the whole file
  and to everything spliced into it by `include`.
- **Block scope** is a pattern block. Block-scoped lines **reset at each
  `pattern` line** — R-RXT-1, unchanged, and it now covers `name`,
  `tag`, `oracle` and `variant` too. `frames-buffer=` keeps its
  positional-within-the-block exception.
- **There is no section scope and no case scope.** OD-1 asked where
  options may be declared; the answer is file and block, and `include` +
  `with` supply what a section scope would have (§2.6).
- **The one cascade is `config <name> from <a>, <b>`**: `a`'s lines,
  then `b`'s, then `<name>`'s own; later wins per option. T-4 is resolved
  by construction — the resetting default and the accumulating cascade
  are *different constructs*, so neither has to become the other, and no
  existing file opts into the second (MEASURED: `config` appears 0 times
  in the corpus).

### 2.2 Names: five namespaces, and one rule for all of them

The format declares five kinds of name. Each is declared by exactly one
construct and referenced from exactly one kind of site, so a reference is
never ambiguous about which namespace it is in:

| namespace | declared by | referenced from | shape |
|---|---|---|---|
| **definition name** | `name <ident>` in a pattern block | `(?&n)` / `(?P>n)` / `\g<n>` / `\g'n'` inside a pattern; `target … = <n>` | PCRE2 group name |
| **config name** | `config <ident>` | `with <list>`, `use <list>`, `from <list>` | ident |
| **data name** | `freq <ident>` (the family, §2.10) | a `config` block's `analysis freq <ident>` line | ident |
| **target prefix** | `target <ident> = …` | `pcrec --target <ident>`; the emitted C symbols | C identifier |
| **scope-path segment** | a delivering call `(?&<site>=<name>)` (§1.5 B3) | `(?&<site>.<group>)` in a pattern; `r.<site>.<group>` in C (§2.13) | PCRE2 group name |

**A fifth: SCOPE PATHS, and they are what makes "lexical scope wins" a
rule rather than a wall.** A delivering call names a scope; `^` names the
caller's (§1.5 B2). Within one path, names resolve lexically — a
caller's own group beats an injected definition of the same name (D87
rule 2) — and either can still be reached explicitly by its path. Two
paths never merge, so a caller's `w` and a library's `w` coexist without
either being renamed in the source the author wrote.

**One rule governs all five: a duplicate declaration within the
resolution scope is REFUSED BY NAME, never shadowed** — with the single,
ruled exception that a caller's own group OVERRIDES an injected
definition rather than colliding with it (D87 rule 2, §2.3.2), because
those are two different scopes and not one. (Frank's §2 wave 1
ruling for definitions; extended to the other three because the reasons
are the same and a parallel mechanism would be exactly what memory
`pcrec-general-mechanisms-not-special-cases` forbids.) The resolution
scope is:

- definition names: the file's own blocks, then its `lib`s in declaration
  order, transitively. Two *different files* defining one name is a
  refusal; the *same file* reached twice by two paths that resolve to one
  real path is one contribution, not a duplicate.
- config, data, target: the **include closure** (§2.5), which is one
  flat space — an included fragment cannot declare any of them (§2.5), so
  in practice this is the entry file plus its `lib` chain for definitions
  and the entry file alone for the other three.
- scope-path segments: the pattern that writes the call. Two delivering
  calls in one pattern with the same site name are a duplicate and are
  refused; the same site name in two different patterns is two different
  scopes and is fine.

**The one namespace this rule does NOT govern is group NUMBERS**, and
they have their own (D87 rule 7(c), §2.3.1): a number assigned twice by
any mix of explicit and implicit assignment is a compile error naming
both sites. Same discipline — refuse, never silently renumber — reached
from the other direction.

**Two identities, deliberately kept apart** (Frank §6.3): the **prefix**
is the link-time identity (`<prefix>_search`, unique per translation
unit); `rx_info.name` is the **runtime identity** — the block's `name`,
or the prefix when the block is unnamed. They are equal by default and
differ exactly where they must: one definition built under two configs is
two artifacts with two prefixes and one `rx_info.name` (§2.7).

### 2.3 Composition — an AST-level operation inside pcrec (D87)

**This section was rewritten after the r44 panel and D87.** The first
version made composition a TEXTUAL operation: append the referenced
definitions as a `(?(DEFINE)…)` block and hand the text to pcrec.
r44-sem measured, on libpcre2 10.46 AND pcrec, that appending can
silently INVERT a library's meaning (M1, M2 below). Frank ruled the
mechanism rather than the refusal: **composition is an AST-level
operation inside pcrec, over ASSIGNED group numbers** (D87 rules 1-7).
The textual expansion survives as the ORACLE CONTROL, not as the
producer.

#### 2.3.1 What a group number is

**CITED, D87 rule 1: a group's number is an ASSIGNED property.** It
defaults to the group's position in its own pattern, and a rewrite such
as composition may assign otherwise. So an absolute reference `\1`
inside a library piece keeps meaning *"this piece's own group 1"*
wherever the piece lands — the composer RENUMBERS rather than refusing.

The assignment rules (D87 rule 7, restated here as the format's
contract because they are what `--emit-composed`, `RX_NCAPS` and the
struct view all read):

| | rule |
|---|---|
| (a) | `0` is the whole match; `(?<0>…)` is an error |
| (b) | an implicit counter `c` starts at 1; an unnumbered group takes `c` then `c += 1`; a numbered group takes its number **and restarts the counter** at `N+1` |
| (c) | a number assigned twice, by any mix of explicit and implicit assignment, is a **compile error naming both sites** — never a silent renumber |
| (d) | `ngroups` = the highest assigned number; `RX_NCAPS = ngroups+1`; numbers in `1..ngroups` held by no group are **real slots that are never set** (`-1,-1`), so a caller's `caps[N]` is always in range |
| (e) | branch reset `(?\|…)` is unchanged: the rules apply within one alternative, the same number across alternatives is the feature, explicit numbers behave like implicit ones there |
| (f) | `\N`, `\g{N}`, `(?N)`, `(?(N)…)` bind to the ASSIGNED number; a backreference or condition on an unassigned number behaves as an unset group (PCRE2's rule); a **call** to an unassigned number is an error — there is no body to call |
| (g) | relative forms `(?-1)`, `\g{-1}` keep PCRE2's textual-position meaning and survive relocation unchanged |
| (h) | names are orthogonal to numbers (§2.13) |
| (i) | **composition assigns a definition's groups a base above the caller's `ngroups`**, preserving local order and gaps; explicit local numbers are RE-BASED, never copied; **the caller's numbers are never touched** |
| (j) | `--emit-composed` prints every group in explicit form, and the serialization round-trips under (a)-(d) unchanged |

Frank's own worked examples: `(3:abc)(1:xxx)(yyy)` assigns 3, 1, 2 —
the numbered group restarts the counter, so `(yyy)` takes 2;
`(3:abc)(1:xxx)(yyy)(fff)` is an **error**, because `(fff)` would take 3
and 3 is already assigned.

Rule (i) is what makes D61 hold. **CITED, D61:** `caps[k]` is the
PRIMARY pattern's own group `k` for `1 <= k <= ngroups`, and slots above
`ngroups` are RESERVED for composition producers, which APPEND their
delivered slots and never renumber `1..ngroups`. D61's revisit-when is
"the first ref-bearing producer is designed" — **this is it**, and the
constraint is inherited as a requirement rather than chosen: `ngroups`
and `nnames` stay the PRIMARY's own (r44-sem M4/M5), the definitions'
delivered slots sit above, and a library's private internal edit can
move `RX_NCAPS` without touching any number a caller indexes by.

#### 2.3.2 Binding: lexical scope wins in both directions

**CITED, D87 rule 2.** A caller's own `(?<w>…)` overrides an injected
definition named `w` — the position paper's "own groups win", restored
as a rule rather than as an avoidance. And a library's internal `(?&w)`
binds to **the library's own** `w`, the lexical scope of the file that
defines it. The composer therefore **name-qualifies injected definitions
internally**, so a caller's `(?J)` cannot reach them.

Resolution, restated for the AST model:

1. For each pattern the compiler is given, the by-name subroutine calls
   (`(?&n)`, `(?P>n)`, `\g<n>`, `\g'n'`) whose target is not a named
   group **of that same pattern** are FILE references.
2. A file reference resolves against §2.2's definition scope: the file's
   own `name`d blocks, then its `lib`s in declaration order,
   transitively. Not found → a refusal. Found in two different files →
   refused by name (§2.2).
3. The closure is a **visited-set fixpoint with dedup** (r44-sem M8): a
   definition already in the closure is not added twice, so a definition
   used at two call sites, a self-recursive definition and a pair of
   mutually recursive definitions each contribute their body **once**.
   Cycles are ALLOWED — r44-sem verified that self- and mutual recursion
   compile and match on both oracles — so the fixpoint terminates on the
   visited set, not on an acyclicity test.
4. **A block's own `name` joins the set of names that pattern declares**
   (r44-sem M8): a block named `x` whose pattern calls `(?&x)` is calling
   itself, not requesting an injection of itself. A `name` line is not a
   named group in the pattern text, so the first version emitted such a
   body twice.
5. Each definition in the closure is bound into the caller's AST with
   its groups re-based per rule (i) and its own name scope qualified.

#### 2.3.3 MEASURED: the two defects, and the two rules that fix them

Every cell below was run on **both oracles** — libpcre2 10.46 through
`docs/design/eng_brep_measurements/probes/pcre2_ctypes.py`, and
`build/pcrec -p rx --features all` through `tests/harness/driver.c`.
**They agreed on every cell**, so the findings are the format's, not
pcrec's.

**M1 — an absolute numeric reference inside a relocated body, and
re-basing.** The library piece `dd` = `(\d)\1` ("a digit repeated"):

| pattern | `77` | `75` | |
|---|---|---|---|
| `(\d)\1` — the piece alone | match (0,2) | nomatch | the library's meaning |

composed into the caller `^(\d)-(?&dd)$`, whose own `(\d)` is group 1:

| composed form | `5-77` | `5-75` | |
|---|---|---|---|
| `…(?(DEFINE)(?<dd>(\d)\1))` — NAIVE append | **nomatch** | **match (0,4)** | **INVERTED**: `\1` re-targeted into the caller's capture space |
| `…(?(DEFINE)(?<dd>(\d)\3))` — RE-BASED per rule (i) | match (0,4) | nomatch | **the library's meaning, restored** |

The arithmetic, and it is worth being exact about: this cell is written
in the CONTROL's textual form, where `(?<dd>…)` is itself a capture
group. The caller's `ngroups` is 1, `dd`'s wrapper takes 2, and `dd`'s
own group 1 takes 3 — so `\1` re-bases to `\3`. That is rule (i)
executed by hand, and it produces the piece's own semantics at the
composed site.

**The composer's base differs from the control's by one per definition,
and that is a design choice this note makes explicitly.** A definition
in the AST model is a CALLABLE BODY, not a capture: §2.13's struct has
no member for the definition itself, a slot for it would never be read,
and the `(?<name>…)` wrapper exists in the textual form only because
PCRE2 has no other way to declare a callable body. **RECOMMENDED: the
composer assigns a definition's own groups the base `ngroups+1` and
gives the definition itself no slot** — so under the composer `dd`'s
group 1 becomes 2, not 3. §2.3.4 states what that means for the
control.
**Relative forms need no re-basing** — r44-sem verified `(?-1)` and
`\g{-1}` safe across relocation (rule (g)), because their meaning is
textual position and relocation preserves the body's internal order.

**M2 — a caller name colliding with an injected definition, and
qualification.** Library: `outer` = `(?&w)`, `w` = `[a-z]+`. The
library alone answers `^(?&outer)$`: match on `abc`, nomatch on `Q`.
A caller writes `(?J)^(?<w>Q)(?&outer)$`:

| composed form | `Qabc` | `QQ` | |
|---|---|---|---|
| NAIVE append | **nomatch** | **match (0,2)** | `(?J)` makes the duplicate legal and the by-name call binds the FIRST declaration — the CALLER's `w`. The library's helper is silently replaced |
| injected definitions NAME-QUALIFIED (rule 2) | match (0,4) | nomatch | the library's own `w`, restored — and equal to the library-alone answer |

`(?J)` is not the disease, it is the symptom: without it the duplicate
is a loud refusal, with it the duplicate compiles and binds the wrong
declaration. Qualification removes the duplicate entirely, so the
behaviour is the same whether the caller writes `(?J)` or not.

**And the numbering fact that started the design still holds** — cells
E-J of the first version, re-stated here for what they now measure:
appending the `(?(DEFINE)…)` block at the END keeps the primary's
captures at `1..N` and appends the definitions at `N+1..`, while
PREFIXING shifts the primary's own numbers:

| # | pattern | subject | `RX_NCAPS` | result |
|---|---|---|---|---|
| E | `^(\d)-([a-z]+)$` (hand-inlined control) | `12-abc` | 3 | `match 0 6  0 2  3 6` |
| **F** | `^(\d)-(?&w)$(?(DEFINE)(?<w>[a-z]+))` | `12-abc` | 3 | `match 0 6  0 2  -1 -1` |
| G | `(?(DEFINE)(?<w>[a-z]+))^(\d)-(?&w)$` | `12-abc` | 3 | `match 0 6  -1 -1  0 2` |
| H | `^(\d)-(?&w)$(?:(?<w>[a-z]+)){0}` | `12-abc` | 3 | `match 0 6  0 2  -1 -1` |
| I | `^(\d)-(([a-z])+)$` (inlined control) | `12-abc` | 4 | `match 0 6  0 2  3 6  5 6` |
| J | `^(\d)-(?&w)$(?(DEFINE)(?<w>([a-z])+))` | `12-abc` | 4 | `match 0 6  0 2  -1 -1  -1 -1` |

These are no longer evidence about how pcrec composes — pcrec composes
over the AST. **They are evidence that the ORACLE CONTROL is exact**:
on the population where the textual expansion is valid, PCRE2's own
left-to-right numbering of the append form produces the same assignment
rule (i) specifies, so the control's answer and the composer's answer are
comparable slot for slot. F is the control's shape; G is why it is
appended and not prefixed.

#### 2.3.4 Who composes, and what the harness's EXPAND is for

**CITED, D87 rules 1 and 4. PCREC COMPOSES.** `--source` / `--lib-path`
read the file, resolve names on [DD-11]'s table (D85), bind definitions
into the AST, assign numbers and emit. This is not a preference: PCRE2
numbers groups by position and has no way to say otherwise, so an
assigned-number model cannot be expressed as text PCRE2 will read — the
operation has to live where the AST is.

Three things follow, and they are the shape of the whole design:

1. **The harness's textual EXPAND is the ORACLE CONTROL, not the
   producer.** It is valid on the population where the append form means
   what the composer means — **no absolute numeric references in any
   body, and no name collisions between caller and closure** — which is
   exactly the population python `re` and libpcre2 can check. Outside it
   the control does not run and says so (a counted, named skip, AR-3),
   because a control that quietly disagrees with its subject on a shape
   neither can express is worse than no control (learnings §3).

   **And on the population where it IS valid, the two do not agree slot
   for slot — they agree up to a KNOWN OFFSET, and the control must
   compute it rather than assume it.** The control's text carries one
   extra capture group per definition (the `(?<name>…)` wrapper PCRE2
   requires to declare a callable body); the composer gives the
   definition itself no slot (§2.3.3). So a definition's group `k` is
   the composer's `ngroups + k` and the control's `ngroups + k + j`,
   where `j` is the number of definitions preceding it in the closure.
   **This is exactly the shape learnings §3 warns about** — a control
   that "obviously" compares equal, then quietly stops comparing the
   thing it names — so the offset is DERIVED from the closure the
   composer reports, never re-derived by the control from its own text,
   and a mismatch in the closure SIZE is itself a failure. Slot 0 and
   the primary's `1..ngroups` are unoffset in both, which is the part a
   caller indexes and the part D61 protects.
2. **`--emit-composed` is a serialization, not a mechanism** (D87 rule
   4). It writes the composed pattern with every group's number spelled
   out explicitly (§1.5), and pcrec ACCEPTS what it emits, so the
   `A == B` control recompiles it and compares. Frank considered and
   rejected composing OUTSIDE pcrec through this spelling: a textual
   renumberer would need a second PCRE2 parser covering every reference
   form (learnings §3's drift hazard), the oracle could not read the
   extended text, and the assigned-number concept has to exist inside
   pcrec regardless. It is the interchange format if a different front
   end ever needs composition.
3. **The composed pattern is not the same object as its serialization.**
   A composed text handed to plain `-p` is ordinary PCRE2 and counts
   every group, so `ngroups` there is the composed total; the same
   composition performed by `--source` keeps `ngroups` at the primary's
   own and puts the delivered slots above. §3.4's S9 hunk states that
   difference in `match_api.md`, because a caller can observe it.

#### 2.3.5 What composition costs, and what it is not

**A subroutine call is BACKTRACKABLE, not atomic, and
capture-transparent** — CITED and MEASURED by an earlier lane on
libpcre2 10.46 (`subroutines_design.md` §3.2, four isolated cells
against four atomic controls; §3.1, a live-ovector callout trace showing
the callee's write and the return's restore). This retires OD-5's
premise as R-VE-8 stated it ("subroutine-call semantics are ATOMIC and
shift capture numbering"): atomicity is false on the current PCRE2, and
the numbering is now an assigned property rather than a positional
accident.

**A call is not textual substitution, and there are TWO places the
difference shows** (r44-sem M13 corrected the first version's "the one
place"):

1. **Captures.** A call restores the callee's capture state on return;
   inlining leaves it set. This is the difference pcrec can reach, and
   it is what the delivering declaration (§2.13) exists to make
   available where a caller wants the callee's groups.
2. **Backtracking control verbs.** `(*PRUNE)` and its family behave
   differently inside a callee than inlined, on libpcre2. pcrec refuses
   verbs (module `verbs`, unbuilt), so this one bites only the
   `oracle pcre2` path and pcrec-bench — but it is a real second member
   and the note no longer claims there is one.

**The cost is PCRE2's, and the linkage is the compiler's.** A
call-linked search does ~2x the backtracks of the same language inlined
(CITED, `subroutines_design.md` §3.2 T7, monotone over 1..8 call sites,
measured with PCRE2's own `match_limit`). `src/opt/callgraph.c`'s
`cg_eligibility` already splices an acyclic callee under a node budget
(§6.3a), and a splice preserves capture-transparency through its own
`SLOT_SPLICE_SAVE` family. **The format pins the answer; the compiler
chooses the linkage.**

**The [DD-14.G] bar, restated** (r44-sem M3, RULED by D87's supersede
clause). The first version said "elision may change the emitted code; it
may not change `RX_NCAPS`", which contradicts plan.md:591's
"byte-identical to the hand-inlined pattern". Under D61 the two are
reconciled: **the bar is the emitted CODE byte-identical and slots
`1..ngroups` identical; the composition's delivered slots live above
`ngroups`.** r44-consumers U7 confirmed [DD-14.G]'s own archived ruling
already matches this (dead call-only groups are elided from engine
SELECTION only; the name table and unset-fill are untouched).

### 2.4 Collisions and the piece rule

**The format has a shadowing rule, and it is "lexical scope wins"**
(D87 rule 2, §2.3.2) — not the first version's "the situation cannot
arise". Three consequences, each with the measurement behind it:

1. **A caller's own named group wins over an injected definition of the
   same name**, and the injected one remains reachable to the library's
   own internal references because it is qualified. MEASURED as M2
   above: naive injection inverts the library's answer under `(?J)`;
   qualification restores it and makes `(?J)` irrelevant.
2. **A definition found in two different files is refused by name**
   (§2.2), unchanged. This is the collision the format still refuses,
   because there is no scope that could break the tie.
3. **A caller may reference a definition's groups explicitly** through
   the scope prefix (§1.5), which is what makes "lexical scope wins" a
   rule rather than a wall: the outer name wins by default, and the
   inner one is still spellable.

**MEASURED — the corpus needs none of this, and that is the point.**
Across all 179 files, **143** blocks in 23 files carry a by-name
subroutine reference, and exactly **4** reference a name their own
pattern does not declare:

```
tests/recursion/d27/sr_refusals.rxt:153  ^(?<w>a)(?&nope)$     perr
tests/recursion/d27/sr_refusals.rxt:158  ^(?<w>a)(?P>nope)$    perr
tests/recursion/d27/sr_refusals.rxt:163  ^(?<w>a)\g<nope>$     perr
tests/recursion/d27/sr_refusals.rxt:168  ^(?<w>a)\g'nope'$     perr
```

All four are `perr` blocks whose purpose is the refusal of an undefined
name, in a file that declares no `name` and no `lib` — so the file scope
is empty, `nope` stays unresolved, and the refusal is preserved. The
other 139 have no file reference and compose to themselves. That is not
a survey that might have gone otherwise: a block whose by-name reference
did not resolve within its own pattern would refuse today, and the
corpus is green.

**The one hazard is self-detecting.** If `sr_refusals.rxt` ever gained
`name nope`, those four blocks would resolve, compile, and their `perr`
assertion would go **red** at the block that changed meaning. No new
check is owed; the existing assertion is the check, and it falsifies in
the loud direction.

### 2.5 The include model

`include <path-ref>` splices the referenced file's **blocks** as if they
had been written at that point.

- **Path spelling** (Frank §6.1, C's model): `include "rel/path.rxt"` is
  resolved relative to **the directory of the file that names it** —
  including when that file is itself a fragment; `include <name>` is
  searched on the library path (pcrec's shipped store, then each
  `--lib-path DIR` in order), with `.rxt` implied, and is **never**
  relative to the including file.
- **What an included file may contain: pattern blocks and `include`
  lines. Nothing else.** No `lib`, `target`, `config`, `use`, `oracle`,
  no file-level `tag` or `description`, no data block. A block-scoped
  `tag` or `description` IS allowed, because it is a block line — which
  is what lets a generator stamp each generated block with its own regime
  and its own one-line summary (§4.5 item 4). ARGUED from AR-4: a fragment that can
  redefine file scope makes a block's meaning depend on which file
  spliced it, which is exactly the cross-file context a D27 author must
  not need. Nested `include` is allowed because a splice of a splice is
  still only blocks.
- **A second `include` of the same resolved real path in one closure is
  REFUSED**, naming both sites (§0.3 D-d). The two alternatives —
  splice twice, or silently ignore — respectively double a population
  and hide one, and learnings §3 is a catalogue of exactly that failure.
  `lib`, by contrast, **is** idempotent: it declares, it does not splice,
  and the same file reached by two paths is one contribution.
- **Cycles are refused**, naming the cycle (R-VE-7's requirement, one
  level up: the *file* graph as well as the *reference* graph must be
  statically analysable).
- **A fragment is not an entry file.** §2.11 states the rule and why it
  has to be a rule rather than a directory convention.

### 2.6 Config scoping and precedence

A **cell** is the unit that gets compiled and run: a (block, option-set)
pair. Today every block is exactly one cell. Configs multiply cells.

- **`with c1, c2` on a `target` COMPOSES**: one artifact, one option set,
  `c1` then `c2`, later wins.
- **`use c1, c2` ENUMERATES**: one cell per named config. ARGUED: `with`
  builds a single artifact and so needs a single option set, while `use`
  says "run these cases under each of these", which is plural by nature
  — and `use`'s consumer is the bench, where the point is that pcrec and
  pcre2-jit are *different testees*, not a composition.
- **`config c from a, b`** expands to `a`'s lines, then `b`'s, then `c`'s
  own. Cycles in `from` are refused.

**Composition is per option kind, not one blanket rule**, because the
kinds are not alike:

| option | how a config and a block compose | why |
|---|---|---|
| `features` | **UNION** — a config's modules are ADDED to the block's — **unless the block writes `features only <list>`**, which pins its own set against any config | enabling a module cannot change what an already-compiling pattern matches; it can only change what is refused (r44-sem probed 8 shapes: every difference was refuse→compile, never match→different-match). Union is what a testee needs: pcrec-bench's `subbench.toml` records that `--features all` "is a build/run flag of the TESTEE, not a variant of the pattern, and the pattern text handed to pcrec is byte-identical either way". **`only` exists because union alone makes NARROWING unspellable** (r44-sem M14: a block writing `features none` beside a config's `all` would silently get `all`) — a deliberate narrowing should be sayable, and spelled |
| `flags` | **more specific wins** (block over config over default) | `flags i` changes what the pattern *matches*; a block that states it has stated the test's meaning |
| `encoding` | **more specific wins**, block scope allowed | D58 makes encoding a PER-PATTERN scalar, so a block must be able to state it; the first version had no row and no block spelling (r44-sem M16) |
| `engine`, `budget` | more specific wins | as above |
| `pcrec <raw>` | config only; accumulated along the chain, later wins per flag | a block has no spelling for these, so there is nothing to conflict with |
| size-limit overrides (`--max-emit-bytes=N`, `--max-emit-code-bytes=N`) | **MAX WINS** across every scope that names one | CITED, `docs/spec/limits.md`: "raise-only (a value below the default is refused, so these can never be used to make a build fail that would have succeeded)". The first version said "raise-only at every scope, a chain that tries to lower is refused" — which made `with c1, c2` **ORDER-SENSITIVE** (r44-sem M15), since `c1` raising then `c2` lowering refuses while the reverse order does not. Max-wins is order-insensitive and the raise-only law then follows automatically rather than being enforced by a refusal |

**A `perr` block is evaluated in exactly ONE cell** — its own options
composed with the file's default — and is **never re-run under a `use`
or `target` config. ARGUED, and it is load-bearing**: `perr` asserts a
refusal *under a stated option set* (R-RXT-6: "a dropped flag would
compile a different automaton and the block's expectations would then be
verified against something nobody asked for"), so re-running it under a
testee's `--features all` would assert something nobody wrote — and
MEASURED, it would silently change the meaning of **384** blocks. Under a
non-pcrec testee a `perr` is meaningless in any case.

**The counter-case r44 put beside this** (U12 on §7 Q2): more-specific-
wins would let a block test under FEWER modules than the file intends,
which is a real way to weaken a suite silently. `features only` is the
answer to it — the narrowing exists, and it is a thing an author wrote
rather than a thing precedence did.

**W23 adds one head declaration ABOVE this whole table: `configs
describe` (§2.20).** Under it, no `config` in the file composes into any
build at all, so everything in this section describes the DEFAULT
(`configs build`) mode only. This is roadblock #6's resolution and D93
territory; §2.20 carries the mechanism and the Frank ratification flag.

### 2.7 Targets, `rx_info.name`, and how many `.c` files come out

> **D88 (2026-08-29, after this note landed):** one artifact per emitted file, ALWAYS — N targets are N files (`-o <dir>`), composition of artifacts is linking, never a multi-pattern translation unit; [V-E]/[EMIT-SET]'s "emission set" is a directory of per-artifact files plus a manifest header. This section's M10 rule is the general one.

A **target** is a file-level declaration, never a block marker (Frank
§6.4, which supersedes the paper's §2/§6.2/§6.3 block-scoped `target`):

```
target <prefix> = <name> [with <config>[,<config>…]]
```

- `<name>` is any definition in scope — this file's or a `lib`'d one. A
  library declares no targets; a user file declares the targets it wants
  from the library, under the user's own configs. This is Frank's own
  case ("there is a set of lib patterns I want to include in my compiled
  file but I want to specify the options for them").
- `<name>` may be declared **after** the `target` line (the head precedes
  the body); resolution is a whole-file pass, so forward reference is
  normal, not an exception.
- **Several targets may name one definition**: `target email_avx2 = email
  with avx2` and `target email_base = email with baseline` are two
  artifacts, two prefixes, one pattern, and `rx_info.name == "email"` in
  both. A duplicate **prefix** in the include closure is refused.
- **Compatibility default** (Frank §6.4): a file with no `target` line
  and exactly one **unnamed** block is `target rx = <that block>` —
  today's `pcrec 'pattern'`, and the CLI's `-p` still overrides the
  prefix for that case. **Every other file builds nothing unless it says
  so.** MEASURED, and the first version overstated it: **177** of the 179
  files have several blocks and would build nothing;
  **two have exactly one block** — `tests/mrl/11_motivating_shape_small.rxt`
  and `tests/base/d27_nested_min_boundary.rxt` — and would therefore
  BUILD as `target rx` under `--source` (r44-sem M11). That is harmless
  and intended: it is exactly `pcrec '<that pattern>'`, one artifact, and
  the harness already compiles both blocks as test artifacts today. No
  file declares a target, so `pcrec --source tests/base/quantifiers.rxt`
  emits **nothing** rather than 90 artifacts. Test compilation is
  untouched; target-ness and testability are independent bits
  (T-1/OD-4, §5).
- **One `.c` per target, and N targets need a DIRECTORY** (Frank's
  ruling 6; the naming rule is r44-sem M10, which found the first version
  had none). `-o` names one file and pcrec also writes its `.h`, so with
  more than one target that is not expressible:

  | invocation | result |
  |---|---|
  | `--target <prefix> -o out.c` | that one target, to `out.c` + `out.h` |
  | `-o <dir>` with N ≥ 1 targets | `<dir>/<prefix>.c` + `<dir>/<prefix>.h` per target |
  | `-o out.c` with N > 1 targets | **refused**, naming the targets and the two ways to proceed |

  A single multi-pattern **unit** stays [V-E]'s question (§4.4). Added to
  S11.
- **`rx_info` gains `const char *name`** (Frank §6.3): the block's
  `name`, or the prefix when the block is unnamed, so no artifact ever
  carries a NULL name. This is a scaffolding change and therefore **an
  `abi` bump under D76's ritual, in the same change**, at all four sites
  CLAUDE.md names: `src/gen/emit_dfa.c`'s `.abi` (~~currently **11**,
  MEASURED at `src/gen/emit_dfa.c:1310`~~ — **STALE; CORRECTED
  2026-08-30 ([DD-13b.W1]): the abi is 12, at
  `src/gen/emit_dfa.c:1375`.** [OPT-4]'s prefilter-language stamp bumped
  11 → 12 after this note was written, so W1's bump is **12 → 13**.
  Three sites in the tree agree on 12 — `emit_dfa.c:1375`,
  `tests/codegen/run_codegen_tests.sh:2707` (`ABI_EXPECT=12`), and
  `docs/spec/match_api.md:159`), `tests/codegen/run_codegen_tests.sh`'s
  [DD-14.FB] §10.4 expectation (**`ABI_EXPECT` at
  `run_codegen_tests.sh:2707`**, with the bump ledger in the `bad`
  message at `:2709`), `docs/spec/match_api.md` §6 (**the "`rx_info.abi`
  is `12`" sentence at `:159`, and the struct block at ~`:1340`**), and
  the identity gate's (B) pin (**`FILEPIN` at
  `tests/codegen/run_recursion_identity.sh:456`, currently `c275aef`** —
  and that file's own rule at `:394-406` binds: the pin moves with the
  LAST src-touching commit of the abi, not the first, which cost 952
  falsely-differing artifacts once). It rides W1's first landing, not a
  separate event (memory `pcrec-abi-changes-pre-release`).
- **`ngroups` and `nnames` stay the PRIMARY's own** (D61; r44-sem
  M4/M5). A composed artifact's `ngroups` counts the target pattern's own
  groups, not the closure's; the definitions' delivered slots sit above
  it (§2.3.1 rule (i), §2.13). This is why `--source` and plain `-p` are
  not interchangeable on a composed pattern — plain `-p` is handed text
  and counts every group in it — and §3.4's S9 hunk states the difference
  where a caller can see it.

### 2.8 Exemplar-file addressing (`@file:`)

`@file:"path"` is a subject, usable wherever a quoted subject is —
`m`, `n`, `ms`, `ns`, `mc`.

- **Local spelling only** (Frank §6.1: "`@file:` subjects are always
  local (quoted spelling only — a subject is data, never a library)").
  There is no `<>` form.
- **Relative to the file that names the subject**, so a spliced
  fragment's paths are relative to the fragment, not to the entry file.
- **The file's bytes ARE the subject.** No escape decoding, no newline or
  encoding transformation, NUL-safe — T-5's requirement, and the same
  discipline `tests/harness/driver.c` already keeps for inline subjects
  ("the decoded bytes may include `\0`, so it never uses `strlen`",
  `docs/spec/rxt_format.md`). The asymmetry is deliberate and must be
  stated in the spec: a *quoted* subject's escapes are processed, a
  *file* subject's bytes are not.
- **The format imposes no size limit.** §3 records the driver-protocol
  change this forces — today a subject travels as an `argv` string, which
  can carry neither a NUL nor a megabyte.
- **W23: a reference may carry `as <id>` and `sha256 <hex64>`** —
  §2.18's rules (the id namespace, the functional binding, who checks
  the hash).
- **No content hash on a COMMITTED subject reference — RE-SCOPED at
  W23** ([B42] P-Q8, ruled): revision 2's "no content hash" was a
  DEFAULT for the case its own argument covers — a subject file
  committed beside the `.rxt`, covered by the same review and history —
  not a principle. The argument's own premise fails for a GENERATED,
  gitignored subject tree (the bench's), which is exactly the condition
  this section says provenance IS required under. So the hash is
  OPTIONAL: pcrec's corpus writes none and changes nothing; a generated
  set writes one on every reference; neither has to argue. §2.10's
  principle ("provenance is required exactly where the source is not
  committed") is unchanged — it now cuts in both directions instead of
  one.

### 2.9 The oracle declaration

`oracle <engine-ref>` | `oracle none <reason>`, file-level or
block-scoped, block wins. **W23 widens the engine enum to an
`engine-ref` with an optional `/version`** ([B42] N-36/N-38, the
manager's pre-ruling): `oracle python` and `oracle pcre2` are
engine-refs with no version and keep their EXACT current meanings, so
nothing in pcrec's corpus moves; `oracle pcre2/10.46` pins the version a
correctness claim was checked against; `oracle tre/0.8.0` names an
engine this repository has no binding for, and that is already handled —
**an absent oracle degrades to R-VG-3's labelled skip**, counted and
printed, never a silent pass and never a hard failure, which is the rule
that makes widening the enum safe rather than a portability hazard. The
version is part of the DECLARATION, not a dispatch key: a consumer that
has the engine at another version reports the mismatch as its own
finding (the bench's re-checkable-exclusion case; `docs/testing.md`'s
"Oracle exclusions" is the pcrec-side analogue).

- **`# pcre2-only` immediately before a `pattern` line stays valid and
  means `oracle pcre2` for that block.** MEASURED: **636** occurrences
  across the corpus; not one of them changes.
- `oracle none <reason>` is a **counted, printed** skip — AR-3, and the
  same shape as `# pcre2-only`'s counted skip and PC-3's loud `SKIP:`
  lines. R-RXT-7's obligation is unchanged: an exclusion still owes a
  `docs/dev/upstream_issues.md` entry.
- **An absent oracle degrades to a labelled skip, never a silent pass and
  never a hard failure** (R-VG-3, the PC-3 discipline) — a stranger's
  clone without libpcre2 must still exit 0 with its skips named.
- **`oracle` names the ENGINE, not the METHOD** (r44-consumers U3). The
  verification METHOD — which R-BENCH-1 requires per case, and which
  includes non-oracle methods such as the K23 region's
  derived-law-plus-induction — is `tag method=<name>`, free-vocabulary
  like every other tag. Folding the two would make a method with no
  engine behind it unspellable and would put an engine enum where AR-6
  requires engine-neutrality.
- **A COMPOSED block's oracle is necessarily `pcre2`**, whether it says
  so or not: python `re` has no subroutine call at all (CITED,
  `subroutines_design.md` §10.1). And a composed block whose closure
  falls outside the textual control's valid population (§2.3.4) has no
  independent oracle at all — that is a counted, named skip and §7 Q7
  is where its residual is argued.
- **`oracle` never selects what pcrec compiles.** It selects what the
  expectation is checked against. The distinction matters for `variant`
  (§4.5): a testee's variant is checked against the *canonical*
  expectations, which the *canonical* oracle produced.

### 2.10 The data-block family, and its membership rule

Frank ruled the exemplar-analysis findings file **is** an `.rxt`, and
that the analysis block is a **family with a membership rule**: an
analysis is included only when it answers a **specific question a named
selection point asks**, with its value **measured first** (D77) — never
on plausibility.

**The rule is made structural, not editorial.** A data block's
`question` and `reader` lines are **required**; a block without them is
refused. `question` states what it answers; `reader` names the selection
point that consumes it. "A block nobody reads is not emitted" is then a
parse-time fact rather than a review convention.

**`freq <name>` is the family's only member today**, and it is earned:
it answers "which byte is rarest", which the rarest-byte candidate-scan
selection ([OPT-A]/D21) asks, and D83 already rules that analysis runs
outside pcrec and arrives as a findings file. Its body is
**16 `row` lines of 16 counts each**, offset-labelled — 256 counts.

**OD-6 is disposed of** (§5): inline values, not `@file:`; and a
**namespace of its own**, not `config`'s (§2.2). Inline, because the
findings file is the **committed artifact and the exemplar is not**
(Frank) — a table that referred out to a second file would reintroduce
exactly the uncommitted dependency the ruling removes, and 256 counts is
~2 KB of text a person can read. Its own namespace, because a `config`
block's `analysis freq <name>` line names a data block and nothing else,
so there is no ambiguity to resolve and no reason to make `config prod`
and `freq prod` collide.

**Provenance is required**, because the exemplar is absent by design
(proprietary, secret, or too large). The table can then be re-derived
when the exemplar is at hand and **reads honestly when it is not**. A
byte histogram is 256 counts and effectively non-reversible, so
committing it leaks essentially nothing; committing it *without*
provenance would be the population-nobody-counted hazard one file over.

**HOW it is required changed at revision 3.1 (§2.26 item 10): it is the
SAME `provenance` sub-block a pattern block takes**, not five one-off
fields of this block's own. Revision 3 had this production carrying
`exemplar`/`bytes`/`sha256`/`analyzer`/`date` while §2.14 carried
`source`/`url`/`ref`/`license`/`retrieved`/`fidelity`/… — **two
vocabularies for one idea**, with `exemplar`/`source` and `date`/
`retrieved` naming the same facts twice. That is precisely the
"inconsistencies would cause eventual confusion" the
internal-consistency ruling names, it was free to fix (this production
has never shipped and has 0 uses in either repo), and §1.2.1's
attachment rule is what makes it expressible — a data block admits
children, one of which itself admits children, with no new mechanism.

So a `freq` block's body is `question`, `reader`, `analyzer`, a
`provenance` child and its `row` lines. The mapping:

| revision 3 field | revision 3.1 |
|---|---|
| `exemplar <name>` | `provenance` → `source <name>` — the exemplar IS the source, named as the user wishes to name it (Frank's own 2026-08-29 wording) |
| `date <iso>` | `provenance` → `retrieved <iso>` |
| `bytes <n>`, `sha256 <hex>` | `provenance` → `bytes`/`sha256`, the two integrity fields, now available to a pattern block's provenance too |
| `analyzer <text>` | **stays on the data block.** It names the TOOL that produced the table, not where the data came from — a different fact, and folding it into provenance would be the unification overreaching |

**The REQUIRED SET differs by parent, and that is a schema row rather
than a second production** (§2.25): under a pattern block
`{source, license, retrieved, fidelity}`; under a data block
`{source, retrieved, bytes, sha256}`. A `license` is not required of an
exemplar (a user's own log file has none to state) and `fidelity` is
meaningless for a byte histogram (nothing was adapted). This is the
schema's first real question and it answers it without a carve-out —
which is the argument for having one.

§6.4's worked findings file moves with this; nothing else does.

**`gap` — the illustrated second member — is NOT specified here.** Frank
named it as an illustration ("I'm just illustrating that there may be
more than frequency, not saying what"), its question is real (how far a
`memchr` for a byte skips, and how bursty its occurrences are — which
frequency cannot answer: equal means, different shapes), and its
**value has not been measured**. D77 says wait. The family's grammar
admits it as one new `data-kind` with its own body when it is earned;
this note adds no production for it.

### 2.11 Population accounting: the summary unit once includes and cells exist

T-6 is the tension the requirements note flagged and no requirement
anticipated: today the accounting unit is the FILE, because
`tests/harness/run.sh` runs one worker per file
(`tests/harness/run.sh:184-216`) and each worker prints its own summary.
Includes break that, and configs break it a second way.

**Three rules, each stated so a check can fail:**

1. **The accounting unit is the INCLUDE CLOSURE, reported under the ENTRY
   file's name.** A failure always prints its own `file:line` — the
   fragment's, not the entry's — so a person can find it; the *tally* is
   the entry's, so a run's totals do not depend on how a set is split
   across files.
2. **An entry file is a discovered file that is not included by any entry
   in the run.** Discovery already excludes by directory
   (`find … -not -path "*/known_fail/*"`), but a *directory* rule for
   fragments would be exactly the role-by-filename convention the
   position paper's §4 rejected for the sidecar. So: resolve includes
   first, subtract the included set, and **report both numbers** —
   `entry files: N` and `fragments spliced: M` — so a set that silently
   stops being spliced is visible instead of merely smaller (K35).

   **A file both NAMED on the command line and included by another entry
   in the same run is counted ONCE, under the includer's closure**, and
   the summary says so: `named, absorbed into <entry>`. The first version
   said "a file named explicitly is always an entry, because the user
   asked for it", which **double-counts** it — the K35 shape this section
   cites for its other rules, caught by r44-consumers U6 in the note's
   own text. Counting once and REPORTING the absorption is better than
   refusing the run: the user gets what they asked for (that file's cases
   run), the population is right, and the line tells them why the file
   does not appear as an entry of its own.
3. **A cell is (block, config), and cells are counted.** Today
   cells == blocks. Once `use` and `with` exist, a summary that counts
   only cases hides its own denominator — the [DD-13c] lesson in one
   line ("the [agreement] denominators were arithmetic over bucket sizes
   … they are COUNTED at the comparison sites now").

**The failure taxonomy grows from three to four.** R-RXT-9's three
(pattern-compile failure, harness-level failure, ordinary case failure)
gain **RESOLUTION failure**: an unresolved name, a duplicate name, a
reference or include cycle, a duplicate target prefix, a config `from`
cycle, an unreadable `@file:` path.

- It is **reported separately** in the summary, so R-RXT-9's
  separate-attributability obligation holds at the new boundary.
- It is **scored as a pattern-compile failure for the block** — which is
  what preserves the four `sr_refusals.rxt` `perr` blocks (§2.4): "this
  pattern does not compile" is true whether the resolver or pcrec said
  so, and a `perr` block must not care which.

**Two accounting facts from today's format that the requirements note
recorded as gaps, and that are already closed** (both worth stating so
[DD-13b]'s design is not built on a stale premise):

- **R-RXT-8's "expected give-up" gap is closed.** `gu <code>
  "<subject>"` exists, is specified (`docs/spec/rxt_format.md`), and is
  MEASURED at **23** uses; `engine vm` (5) and `budget` (3) are the
  directives that reach the path. `subroutines_design.md` §10.3's "THE
  HARNESS GAP: there is no way to EXPECT a give-up" is likewise closed.
  pcrec-bench's `gave-up` outcome (its §4.4) therefore maps onto an
  existing directive, not a new one.
- **`gp`'s pending-VM bucket is the model R-RXT-5 asks a successor to
  keep**, and this design keeps it untouched: `g` out of range is a hard
  failure, `gp` out of range is a counted third state, `gp`
  self-activates when the artifact grows. Nothing in W1..W3 touches it.

### 2.12 Diagnostics: the offset must come home, and D87 makes that harder

pcrec reports pattern offsets into the text it was given. Once
definitions are bound in, an offset no longer indexes any text the user
wrote. MEASURED, the collision refusal §2.3.3's M2 row produces on both
oracles reads:

```
pcrec: two named subpatterns have the same name … (pattern offset 27)
```

— offset 27 of a 45-byte composed pattern the user wrote as a `pattern`
line and a `name` line in two different places, possibly in two
different files.

**The obligation** (not the wording — D26 keeps that out of scope):
every AST node that composition binds carries a **PROVENANCE** — the
(file, line, offset-within-that-line's-pattern-text) it was parsed from
— and every diagnostic carrying a position is reported through it. A
refusal that lands inside an injected definition must name **that
definition's own `file:line`**, not the referencing block's.

**Revision 1 called this a "span map" over concatenated text, and that
is no longer the right shape.** Under D87 there is no concatenated text
to map: the composer works on ASTs, so provenance is a FIELD ON THE NODE,
carried from its parse. That is both simpler (no interval arithmetic) and
strictly more capable — it survives passes that reorder or rewrite nodes,
which a text map does not — and pcrec's AST already carries per-node
data of exactly this kind (D62's parse-resolved modifier fields are the
precedent for "the parse writes it on the node").

Three diagnostics depend on it, and each is a place a composed build is
otherwise unreadable: **rule 7(c)**'s duplicate-number error must name
BOTH assigning sites, which may be in two files; a **piece-rule refusal**
(§6.0) must name the definition, not the caller; and an ordinary compile
error inside a bound definition must send the user to the library, not to
their own line. It is the one piece of machinery this design owes that
has no analogue in today's harness, and §3.2's H2 lists it as such.

### 2.13 The struct view: context naming IS struct naming (D87 rules 5, 6)

**CITED, D87 rule 5.** With the feature that loads a match's results into
a generated struct — one field per named group — **a scope prefix is a
path and a struct is a path**, so the two are one mechanism seen from two
sides. This subsection states the format's half; the feature's own row is
**[V-I]** (plan.md:737, NAMED-RESULTS COPY HELPER — "an emitted
`struct <prefix>_groups` with one span member per named group, plus a
copier from the caps array"), which already cites D61 and
`rx_group_entry.slot` as its substrate.

**A delivering call gets an inline, in-place struct member named by the
CALL SITE.**

```c
struct { rx_span local, domain; } from;    /* declared in place */
```

- **No named type per definition.** The member is declared inline at its
  position, so the artifact stays self-contained and two libraries'
  `email` cannot collide in a type namespace that does not exist.
- **The reference prefix spells the member path**: `r.from.local` in C is
  `(?&from.local)` in the pattern (§1.5 B2). One vocabulary.
- **Per CALL SITE, not per definition.** A definition called twice needs
  two site names — defaulting to the definition's own name, given
  explicitly when that would repeat.
- **Undeclared calls stay capture-transparent** (PCRE2's default, zero
  cost). Delivery is opt-in per site; a file that declares none emits
  exactly what it emits today.
- **Delivered slots live ABOVE `ngroups`** — D61's reserved region,
  §2.3.1 rule (i). `ngroups` and `nnames` remain the primary's own.

**What is not deliverable, and its refusal.** A struct member is a
finite, fixed-shape object, so what cannot be one cannot be delivered:

| shape | why | outcome |
|---|---|---|
| a **recursive** definition (self- or mutually) | the nesting depth is a runtime fact; the member type would be infinite | a delivering declaration on it is a **refusal naming the recursion** |
| a call **under a repeat** | one member, many activations; which one is delivered has no answer the format may pick | a **refusal naming the quantifier** |

Iterated capture — "give me every iteration's value" — is a separate
question and explicitly **out of this row** (D87 rule 5). The refusals
above are not a policy against it; they are the honest answer while no
mechanism for it exists.

**Duplicate names within one scope path are ONE field, populated by the
FIRST SET group of that name in number order** (D87 rule 6) — PCRE2's own
`pcre2_substring_get_byname` rule, made structural rather than
re-invented. The intended use is alternation branches populating one
field:

```
(?<num>\d+)|0x(?<num>[0-9a-f]+)        ->  one member `num`
```

Two things this does NOT do, stated because both are natural misreadings:

- **It does not merge across scope paths.** A caller's `w` and a
  library's `w` are different paths, so they are different fields — which
  is §2.3.2's lexical rule seen through the struct.
- **It does not collapse the slot table.** Every duplicate keeps its own
  assigned number and its own slot; numbering never merges. Only the
  STRUCT VIEW merges, and it is a view.

**Two call sites of one definition are DISTINCT C types.** Each member is
declared inline at its own position, so `from` and `to` over the same
`email` definition have no common type name; assigning one to the other
needs `__typeof__`. That is acceptable because the target is
gcc-dialect C by construction (CLAUDE.md: "generated code uses computed
goto and other GNU C extensions") and it is **one sentence the spec
owes**. A named typedef per definition is a later opt-in, not this row's.

**Field order is assigned-number order.** The struct is the slot table
seen through names, so there is **one derivation feeding three readers** —
`RX_NCAPS`, the struct, and `--emit-composed` — which is learnings §3's
rule applied where it matters most: three surfaces that must agree can
disagree only if they are computed twice.

**A library adding a delivered group changes the user's struct TYPE.**
This is r44-sem's M5 ("a library's private edit moves the user's
`RX_NCAPS`") in its honest, visible form: under D61 the caller's own
`1..ngroups` are untouched, and the thing that moves is a type the
compiler checks, not an index the caller computed. A recompile sees it.

**What [DD-13b] hands [V-I]**, stated as the interface so that row does
not have to re-derive it:

1. the assigned-number table for the composed pattern (§2.3.1), from
   which field order follows;
2. a scope PATH per delivered group (call-site name, then the
   definition's own name), from which the nesting follows;
3. the first-set-wins merge rule for duplicate names within a path
   (D87 rule 6);
4. the two non-deliverable shapes and their refusals;
5. the guarantee that delivered slots never intrude on `1..ngroups`.

What [V-I] still owns: the C-keyword MANGLING rule its own row already
flags (`(?<int>…)`, `(?<return>…)` are valid group names and invalid
member names), the copier's signature, and whether the struct is an
optional emission unit ([EMIT-SET] names it as one).

### 2.14 `provenance` — per-pattern origin, structural ([B42] N-11..N-19)

A kind that ADMITS CHILDREN (§1.2.6), at most ONE per parent — a second
is **refused by name**, never last-wins (the shape STEP 0's
duplicate-`description` refusal closes one production over; the bench's
MEASURED M5 is why this rule is stated rather than assumed).

**REVISION 3.1: this is ONE record shape at TWO parents**, a pattern
block and a `freq` data block. Revision 3 noted the `freq` block's
required-provenance discipline as the PRECEDENT for this section; the
audit (§2.26 item 10) found the two had grown different field names for
the same facts and unified them — a wild pattern's source is absent
from the repo by exactly the logic an exemplar is, which is an argument
for one record, not for two that rhyme. What differs by parent is the
REQUIRED SUBSET, and that is a schema row (§2.25), not a second
production.

Rules, each parser-enforced:

1. **REQUIRED fields are declared per parent.** Under a pattern block:
   `source`, `license`, `retrieved`, `fidelity`. Under a data block:
   `source`, `retrieved`, `bytes`, `sha256` (§2.10 gives the reason
   `license`/`fidelity` are not required of an exemplar). A block
   missing one is refused naming the missing line — the `freq` block's
   `question`/`reader` rule, reused and now shared.
2. `url` and `ref` are **REQUIRED unless `source` is the reserved slug
   `authored`**, and an `authored` block that writes either is refused:
   the slug and the fields must agree or `authored` stops meaning
   anything. (The bench's own rule, adopted verbatim.)
   **The rule is TWO schema rows and revision 3.1 had a kind for only
   one of them** (3.2, r57 S-BL1(b)): the first half is
   `required-if source != authored`, and the second — *refused WHEN
   `source` IS `authored`* — is `forbidden-if source == authored`, a
   kind §2.25.3 now carries. Negating `required-if`'s operator does not
   reach it: that yields "required when the condition does not hold",
   which is the first half again. The two halves govern opposite
   outcomes under complementary conditions, which is why they are two
   rows and not one.
3. `adaptation` is **REQUIRED iff `fidelity` is not `verbatim`** — the
   one conditional the format enforces, and the whole value of making
   the record structural: a mechanically-changed pattern with no stated
   change is the failure a reviewer cannot catch by reading.
4. `fidelity`'s three values are CLOSED **by the format's own schema**,
   not via `vocabulary`: the conditional in rule 3 requires the parser
   to know them, so a file-declared set would be a second home for a
   fact the parser already owns. At revision 3.1 that is no longer a
   distinction between "grammar" and "declaration" — both are schema
   rows — and the real statement is the `source` column §2.25 gives
   every row: `fidelity`'s closed set is `source: format`, a `tag`
   key's is `source: file`. Same mechanism, two origins, one table.
5. `attribution` exists as a field; whether a license demands one is a
   POLICY the format does not know (SPDX is an open set) — the consuming
   project's gate enforces it. The field must exist so a CC BY-SA
   pattern has somewhere to put what its license requires.
6. Prose fields (`license-note`, `adaptation`, `attribution`) take
   `prose-value` — one line, or a `|` scalar indented deeper than the
   attribute line (§1.2.5). ONE prose mechanism, everywhere — and at
   revision 3.1 that sentence is finally true without exception, since
   §1.2.5 retired the block-scope `description` carve-out that was the
   one place it was not.
7. **`licence`/`licence-note` are spelled `license`/`license-note`**
   (§2.26 item 10): the VALUE is an SPDX identifier and SPDX's own key
   is `License`, so the British spelling put a gratuitous translation
   step on the one field that crosses an ecosystem boundary. Free: 0
   uses anywhere.

What pcrec's own harness gets (the both-repos test §2's every
production passes): the corpus's imported material — the D27 corpora's
generator provenance, the Fowler-derived cases, `# pcre2-only`
justifications — gains a machine-readable origin, and "where did this
block come from" becomes a `--list-source` section (§2.24) rather than
a grep through comments. Nothing REQUIRES pcrec's corpus to adopt it;
the production is block-scoped and absent-by-default.

The harness readers RECOGNISE and skip it (`run.sh`, `verify_rxt.py`
consume the indented body without reading it); pcrec VALIDATES it —
§2.24's D4 table is where that split is published.

### 2.15 `vocabulary` — file-declared closed sets ([B42] N-10/N-21, pre-ruled)

`vocabulary <key> <v1> <v2> …`, file scope, wrapping by S1 attachment
(§1.2.1) like every other continuation. Declares that
`tag <key>=<value>` (and every other production the spec names as
vocabulary-checked: `under`'s convention, `variant`'s `kind`,
`provides`' values) may only take a listed value; a violating value is
**refused by name**, naming the key, the offending value and the
declared set.

**REVISION 3.1 NESTS THIS, AND IT IS THE PRODUCTION THE SCHEMA RULING
WAS ALREADY HALF-ANSWERED BY.** Frank's consequence 3 names it
directly: *"The bench's `vocabulary` production is the file-declared
half; the format-level half is pcrec's own rules, stated once and
enforced mechanically."* So `vocabulary` is not a mechanism beside
§2.25's schema — it is **one row-source within it**. Concretely
(§2.25): the schema table carries a `source` column, `format` for rows
pcrec declares and `file` for rows a `vocabulary` line declares; the
`closed <set>` constraint is ONE constraint kind whose members may come
from either; `--list-schema` prints both, with `source` distinguishing
them; and the enforcement path is one walk, not a format check plus a
vocabulary check. A reader asking "what values may this key take?" gets
one answer from one place regardless of who declared it.

That nesting is what keeps the two from drifting into two enforcement
orders — and it is why `fidelity`'s closed set (§2.14 rule 4) needs no
argument about why it is "in the grammar rather than via `vocabulary`":
both are `closed` rows, they differ in `source`, and the parser's
knowledge of `fidelity`'s three values is a consequence of the row
being `source: format` rather than a separate fact.

- **A key with NO `vocabulary` line keeps free-vocabulary behaviour
  exactly** — the compatibility rule that makes this purely additive,
  and the answer to r44's own concern that §4.5's absorption silently
  downgraded four validated record-schema enums to free strings: the
  file that carries those tags declares their sets, and the format
  enforces without knowing what any value MEANS (AR-6 held — the format
  checks membership, never meaning).
- **A second `vocabulary` line for the same key is refused** — §2.2's
  duplicate-declaration rule, fifth namespace's sibling (the key space
  is small and a split declaration is a reader hazard, not a
  convenience).
- A `vocabulary` line for a key nothing uses is legal (a declaration,
  not an assertion); `--list-source` reports it and a consumer may warn.
- BARE tag labels are keyless and therefore never vocabulary-checked;
  say it so nobody expects otherwise.
- Enforcement covers BOTH scopes (file-level and block `tag` lines) and
  the include closure: a fragment's `tag` is checked against the ENTRY
  file's declarations, which is the AR-4-compatible direction (the
  fragment cannot declare head lines, so its meaning still depends on
  exactly one bounded place).

`requires` stays a `tag` key rather than its own production, for the
bench's own stated reason (a dedicated production would make the
capability model a FORMAT concept, which AR-6 forbids); with
`vocabulary`, the closed-set discipline reaches every key at once.

### 2.16 `provides` — what a config's engine satisfies ([B42] N-22/N-23)

**SPELLED `provides` at revision 3.1; the bench's sketch and revision 3
said `capable`** (§2.26 item 4). The semantics below are unchanged, and
so is W23-F2's question to Frank, which is about WHERE the capability
model lives and not what the line is called (syntax is the manager's
under the 14:5x delegation). The reason for the move: the pattern side
of this relation is `tag requires=…`, and `requires` / `provides` is
one relation read from its two ends — the pairing every neighbouring
ecosystem uses (SPDX, pkg-config, package manifests) — where
`requires` / `capable` is a verb beside an adjective and leaves a
reader to work out that they are halves of the same thing. Free: a
`config` body is a W1 production with **0 occurrences in the corpus**,
and `provides` is 0 in every context (§0.7's 52-candidate census).

A `config`-body line, repeatable and accumulating like `tag`: the
vocabulary values this config SATISFIES. **Absent means NOTHING is
satisfied — fail-closed, deliberately**, so a new adapter cannot claim
capabilities by omission (the bench's own rule, adopted).

- **The key name `requires` is RESERVED by one spec sentence**: when a
  `vocabulary requires …` declaration exists, every `provides` value must
  be a member of it (refused naming value and set); with no such
  declaration, `provides` values are free. The format thereby knows ONE
  NAME — that the key `requires` is where capability tags live — and
  still nothing about what any tag means. The precedent for reserving a
  name is `# pcre2-only` and the `oracle` engine names; AR-6 is about
  MEANING, not spelling.
  **THE POINTER, added at 3.2 (r57 G-B5).** The sentence above is the
  ONLY syntactic path from `provides` to the set that constrains it,
  and a reader meeting a `provides` line has no way to find it: the
  governing declaration is spelled under the OTHER end's name
  (`vocabulary requires …`), in a different scope, with no occurrence
  of the token `provides` anywhere near it. The rename to `provides`
  (§2.26 item 4) buys a reading symmetry the grammar does not have, and
  pretending otherwise would be the rename doing work it cannot do. So
  the schema states the link as DATA — `provides` carries
  **`cross-scope file vocabulary requires`** (§2.25.3's new kind), which
  is exactly this pointer in a form `--list-schema` prints — and the
  spec paragraph (SW4) names `vocabulary requires` in the same sentence
  as `provides`, in both directions, so a grep for either finds the
  other.
- The pre-compile policy — `REQUIRES(pattern) ⊄ capabilities(config) ⇒
  unsupported-by-declaration`, decided before any compile — is the
  CONSUMER's rule. The format carries the declaration (`provides`), the
  per-pattern requirement (`tag requires=…`) and the outcome production
  (`variant <testee>` + `unsupported`, §2.23); the spec states the
  intended reading so two consumers cannot invent two policies, and
  R-BENCH-3/AR-3's counted-never-silent rule covers the outcome.
- pcrec's OWN harness ignores `provides` operationally (its one testee is
  pcrec); the dump carries it (§2.24), which is what a reader of the
  file needs — the reason a pattern has no result for a testee lives in
  the same file as the pattern (§8 P-Q4's argument for IN-the-format).

**Flagged for Frank's ratification beside §2.20** — the manager
recommends IN the format; a "keep it bench-side" answer is a partial
return of the hybrid and was argued against, not defaulted (§8 P-Q4).

### 2.17 `under` — the second correct answer, per convention ([B42] N-35)

`under <convention> <case-line>` where `<case-line>` is an UNCHANGED
`m`/`n`/`ms`/`ns`/`mc` line. The deepest of the bench's six roadblocks:
one pattern, one subject, two engines answering DIFFERENTLY AND
CORRECTLY (`a|ab` on `"ab"` is `0 1` leftmost-first and `0 2`
leftmost-longest), and a case line today is one answer with no
qualifier.

- An UNQUALIFIED case line means what it means today: the expectation
  under the block's (or file's) declared canonical convention
  (`tag convention=…`).
- `under <conv> m "s" a b` states the answer a testee tagged with THAT
  convention is scored against, same (pattern, subject). A testee whose
  convention has no `under` line for a case falls back to the
  unqualified line — a set declaring no conventions behaves exactly as
  today, so the production is additive.
- `<convention>` is a `tag-value`, closable by `vocabulary convention`.
  The format does not know what `posix-leftmost-longest` means — AR-6's
  line held; scoring against the right expectation is the consumer's
  act.
- Two `under` lines for one (convention, subject, kind, startpos) are
  **refused as a duplicate**, not last-wins.
  **Where that rule LIVES is stated at 3.2** (r57 S-BL1(d)): the key
  tuple ranges over fields INSIDE the `qualified-line` value — three
  of the four are components of the wrapped case line, not sibling
  lines — so `unique-by` can hold the tuple but something must extract
  it. **The extraction is PARSER CODE, by decision, with its reason
  recorded**: `value: qualified-line` already means the parser
  decomposes this value into a case line (that is what the value shape
  IS), so the components are in hand at the site that already has
  them, and a declared field extractor would be a second description of
  a decomposition the parser performs anyway. The schema row carries
  `unique-by under-key` and SW8 names the four components; the arm that
  builds the tuple is code. A SECOND `qualified-line` production with a
  different key is the D77 trigger to make the extractor declarative,
  and §2.25.4 carries it as a deferral rather than leaving this as an
  unexplained exception.
- **`under` never wraps `g`/`gp`/`gu`**, and `g`/`gp` lines attach only
  to UNQUALIFIED `m`/`ms` cases: a capture expectation under a foreign
  convention has no consumer (the bench's expectations carry no capture
  columns — MEASURED, §5.1 attack 3), so admitting it would be building
  ahead of need (D77) and would force the attachment rule to answer a
  question nobody asked. Named trigger: the bench's OD-B9.
- **pcrec's own harness treats every `under` line as a COUNTED, LABELLED
  skip** (AR-3's shape, a new summary line), because scoring one would
  require `run.sh` to know pcrec's convention BY NAME — engine knowledge
  the harness must not hold. `verify_rxt.py` the same. The bench's
  runner is the scorer; its own R5-B1 harness half is theirs and §9's E5
  row says so.
- `variant` and `under` stay orthogonal on the axis r44 already ruled:
  a variant is about SPELLING, a convention about SEMANTICS, and a
  testee's variant is still checked against the expectations its
  convention selects — first the convention picks the answer set
  (`under` or unqualified), then the variant supplies the text.

### 2.18 Subject identity and integrity ([B42] N-26/N-27, pre-ruled)

`@file:"path" as <id> sha256 <hex64>` — both suffixes optional,
independently.

- **`as <id>` names the subject.** The id is in a **per-FILE subject
  namespace** (the physical file that writes the line — a fragment's ids
  are the fragment's), spelled in the wide `defname` grammar since the
  bench's ids are hyphenated. The binding is FUNCTIONAL: one id maps to
  one (path, sha256); re-stating the same binding on many case lines is
  the normal spelling (every case line naming the subject carries it);
  a CONFLICTING re-binding — same id, different path or different hash —
  is refused naming both lines. Two ids for one path are legal
  (pointless, harmless, and refusing them would require the parser to
  canonicalise paths).
  **Its schema row is `functional-binding id -> (path, sha256)`, NOT
  `unique-by id`, and the correction is load-bearing** (3.2, r57
  S-BL1(c)). Revision 3.1's §2.25.3 mapped this rule to `unique-by`,
  which means *at most one row per key* — and would therefore **refuse
  this production's own documented normal spelling on its second
  occurrence**, since the whole point is that the binding is restated
  on every case line naming the subject. A functional dependency is not
  a uniqueness key; equal keys with equal values is the common case
  here and the refusal is only for equal keys with UNEQUAL values.
  §2.25.3 carries the kind.
- **A case is then citable as (pattern, subject-id)** — the stable key
  every bench expectation, report row and interpreter fact needs —
  and a failure line prints the id beside `file:line`, which pcrec's own
  generated corpora benefit from identically (a regenerated fragment's
  line numbers move; its ids do not). Roadblock #4 closed.
- **`sha256` is checked by whatever READS the subject** — the harness's
  driver path and the bench's loader — refusing on mismatch naming the
  path and both digests. `--list-source` validates the SYNTAX (exactly
  64 hex digits) and reports the value; it performs no file I/O on
  subjects (it is parse-only and stays so), and §2.24's D4 table states
  that split so nobody reads the dump as an integrity check.
- An INLINE quoted subject takes neither suffix — no consumer asked
  (D77), and the id's whole value is naming bytes that live elsewhere.

**N-27's NON-ID SLICE, carried or refused by name** (NEW at 3.2, r57
C-S7 — the one genuine gap in the panel's 53-row needs walk). N-27 is a
Tier 1 MUST and revision 3 answered its BLOCKING half (`as <id>`) while
its other three fields went unmentioned, which under Option A reads as
silently bench-side. Each gets an answer here:

- **A subject's BYTE LENGTH is DERIVABLE and is not carried.** The
  format already names the file (`@file:"path"`) and optionally its
  digest; length is `stat` on the same path, available to every reader
  that opens the subject at all, and a carried length is a second
  source of truth that can disagree with the bytes. If the need is
  integrity, `sha256` is the field and it is strictly stronger; if the
  need is a report column, the reader computes it. **Refused as a
  field, with the reason, rather than omitted.**
- **A per-subject DESCRIPTION and `periodic` are REFUSED, in the D77
  shape, and NAMED bench-side manifest data.** Neither is a property
  the format can check or a consumer in this repo reads: a subject's
  prose and its "generate this periodically" flag are facts about the
  bench's own corpus-production pipeline, not about the pattern, the
  expectation or the file's parse. Putting them in `.rxt` would give
  the format two fields nothing in either repo validates — the
  free-string regression §2.15 exists to prevent, arriving from the
  other side. **The trigger that would move them**: a subject
  description becomes a format field the day a `--list-source` consumer
  in THIS repo reads one (the same bar `description` itself had to
  meet, Frank's r44 summarize-via-script ruling); `periodic` becomes
  one the day regeneration is driven from the `.rxt` file rather than
  from the bench's own manifest, which is a change to who owns the
  pipeline and is theirs to propose (D78).
- **Why this is stated and not left as an omission**: Option A says the
  set's truth lives in `.rxt`, so every need answered bench-side is an
  exception to a ruling and owes its argument. Three of N-27's four
  fields are answered here; one is BUILT.

### 2.19 `pattern-esc` — the second pattern spelling ([B42] N-2, F-Q2)

`pattern-esc "<quoted>"` starts a block exactly as `pattern` does; its
pattern text is the DECODED bytes, using the format's own seven-escape
subject vocabulary and no second vocabulary. Because the escape table
already includes `\n`, `\xHH` and `\\`, a `(?x)` body authored across
lines, raw high bytes and a trailing CR all become expressible with
nothing new invented — **multi-line CAPABILITY without multi-line
SYNTAX**, which is what keeps every reader's line-oriented loop intact
and is why this form was chosen over continuation (continuation under
`pattern` would also have destroyed N-2's loud refusal — which at
revision 3.1 is §1.2.6's second table row rather than a numbered rule,
and still holds: `pattern` declares `children: none`, so an indented
line under it is a schema error naming it).

- **~~A block carries `pattern` or `pattern-esc`, never both — both is
  refused naming both lines.~~ DROPPED AT REVISION 3.2 (r57 S-BL2, a
  BLOCKER), and the reason is that the refusal has an EMPTY
  POPULATION under §1.2.1's own structure layer.** Both spellings are
  members of S2's BLOCK-OPENER set, and S2 says an opener among
  siblings STARTS A GROUP. So a `pattern-esc` line following a
  `pattern` line is not a second spelling inside one block — it is the
  next block. MEASURED on the shipped binary: two adjacent `pattern`
  lines produce **two `pattern` rows in `--list-source`, rc 0** (§0.8);
  nothing in the parser ever holds a state in which one block carries
  both, so there is no state for the refusal to fire from.
  **Recovering the refusal would cost the format its structure layer**:
  it would need a rule saying that one particular opener, following
  one particular other opener, does NOT open a group — a
  keyword-dependent structural exception, which is exactly what
  consequence 1 forbids and what §1.2.1 was rewritten to delete. The
  rule is therefore dropped rather than rescued, and the answer a
  reader gets is the plain one: **a second opener starts a new
  block.**
  *Consequence for the bench*: their acceptance check B6 is written
  against the refusal. It does not become a failure — its PREMISE
  dissolved — and §9's B6 row and the correction list carry it as a
  bench-side correction rather than as a deviation.
  *What survives*: a block still has exactly ONE pattern line, because
  a block IS what one opener starts. That is `cardinality: one` on the
  group's own opener, not a refusal anybody writes.
- **`pattern` itself is UNTOUCHED** — rest-of-line, verbatim, no
  escaping, byte-exact (the bench's M3/M4 round-trip facts must not
  move, and every existing exporter depends on the verbatim rule).
- **`\x00` inside `pattern-esc` is REFUSED BY NAME, and the reason is
  K9**: the compile entry takes no pattern length
  (`docs/dev/known_issues.md` K9), so a NUL-bearing pattern would
  compile as its prefix and report success — the exact silent-wrong
  -artifact trap the STEP 0 raw-NUL refusal closes for `pattern` lines.
  The refusal names K9 and the lifting trigger (`rx_info.pattern_len`'s
  API half landing). Expressing a NUL pattern is thereby a KNOWN LIMIT
  with a named owner, not a silence — the bench's own N-4 priority split
  ("SHOULD to express, MUST to refuse") honoured in both halves.
- **Who decodes: pcrec, once.** The CLI gains a flag (working name
  `--pattern-esc`; `cli.md`'s hunk owns the spelling) under which the
  pattern OPERAND is taken in the quoted-escape form and decoded by the
  format's own decoder — the same decoder `--source` and `--list-source`
  use on these blocks. `run.sh`'s arm passes the still-encoded text
  through with the flag; `verify_rxt.py` decodes with its existing
  python-side table. No bash decoding anywhere (a `printf %b`
  approximation would be a SECOND decoder with its own escape set — the
  drift hazard by construction).
- `--list-source` reports the block with the DECODED bytes in the
  `pattern` column (escaped back in the dump's own vocabulary — a
  byte-exact round trip by construction, same table both directions)
  plus an `esc` column marking the source spelling, so an exporter can
  reproduce the file as written.

### 2.20 `configs describe` — build configs vs descriptive configs
([B42] N-43/N-44, roadblock #6; **READY FOR FRANK'S RATIFICATION** — D93 territory)

**The collision, restated**: D93 makes a `.rxt` source's composed
config WIN over a command-line flag on the same axis. §6.2's worked
bench file carries `config pcrec` — and the bench's entire
sixteen-config pcrec testee matrix is command-line flags, so a set file
that describes its testees would silently PIN them. Both rules are
right alone and collide when the file is a bench set.

**The mechanism**: one head declaration, `configs build` (the default,
today's semantics, spellable explicitly) or `configs describe`. Under
`describe`:

1. **No `config` in the file composes into ANY build.** `pcrec
   --source` applies none of them; the harness applies none to its
   compiles; the D93 precedence question never arises because nothing
   composes. The configs are DATA — read via `--list-source` by whatever
   runs the testees (the bench's runner), applied by IT through its own
   adapters' command lines, which therefore always win because they are
   all there is.
2. **`target … with <config>` is REFUSED**, naming the target line and
   the `configs describe` line — a build declaration referencing a
   descriptive config is a contradiction the author should hear about,
   not a precedence question. A bare `target` (no `with`) stays legal:
   `describe` scopes CONFIGS, and the exporter writes bare
   `target =` rows today.
3. **`use` is legal and INERT for the harness**, which runs each block
   in exactly ONE cell (its own directives plus file defaults) and
   reports `configs: descriptive (N declared, 0 applied)` — declared
   inapplicability as a counted, printed state (AR-3), never a dropped
   directive.
   **AND ITS REFERENT STILL RESOLVES — in BOTH modes** (NEW at 3.2, r57
   C-S5). "Legal and inert" left open whether `use dev` in a `describe`
   file is checked against the file's `config` declarations at all, and
   the wrong answer is the dangerous one: a typo (`use dve`) caught in
   build mode would go SILENT in describe mode, which is AR-3's
   forbidden shape — a file that looks like it declares something and
   declares nothing. **The rule: `use` names are RESOLVED in both
   modes, and an unresolvable name is REFUSED in both.** What `describe`
   changes is whether a resolved config composes into a build, not
   whether it exists. Same for `target … with` (refused outright under
   `describe`, rule 2) and for `from` inside a `config` body, whose
   cascade is a declaration-time resolution and is unaffected by the
   mode.
4. **The declaration is the ENTRY file's** and governs the include
   closure — a fragment cannot carry head lines (§2.5), so a block's
   config semantics still depend on exactly one bounded place (AR-4).
   **AND `lib` CONTRIBUTES DEFINITIONS ONLY — the closure clause, made
   explicit** (NEW at 3.2, r57 C-S4). Roadblock #6 is closed by
   construction for `include`, because §2.5 restricts a fragment to
   pattern blocks and a fragment therefore has no head lines to
   contradict the entry's mode. `lib` is different: a `lib`'d file is
   an ORDINARY `.rxt` and may carry a full head, including its own
   `configs describe`, so "what does a build-mode file see when it
   `lib`s a describe-mode file?" had no stated answer. **The answer is
   that it sees nothing but definitions**: `lib` contributes the
   library's named definitions and its `description`s to the composer's
   lookup, and NOTHING ELSE crosses the boundary — not its `config`
   blocks, not its `configs` mode, not its `target` rows, not its
   `use`/`oracle`/`tag` lines, not its cases. This is not a new rule so
   much as the already-stated one written down at the place it is
   asked: §4.1 already says a library's TESTS do not run in a file that
   `lib`s it, and a config that cannot reach a build in the library's
   own file certainly cannot reach one through a `lib` edge. Stating it
   makes the mode question answer itself — a library's `configs` mode
   governs the library's own file when that file is under test, and is
   invisible to every file that `lib`s it — and it keeps AR-4 exact,
   since a block's meaning still depends on ONE head, its own entry's.
5. A second `configs` line is refused (duplicate declaration, §2.2).

**And the PERMANENCE sentence** ([B42] N-43, check F1): a file with no
`target` and no `config` **parses, builds nothing, and exits 0 — as a
CONTRACT, permanently**. The behaviour is shipped (`rxt_format.md`:
"No `target` and anything else builds NOTHING… It is not an error");
what the bench asked for is the sentence in the spec that it STAYS
true, and the spec hunk (§3.4 SW5) adds it.

**Why resolution 1 and not the alternatives** (the bench's §2.6): their
resolution 2 ("a config naming a foreign `testee` is descriptive")
leaves `config pcrec` in §6.2 still winning — the actual hazard; their
resolution 3 is the hybrid Frank removed, recorded as the null option.
A PER-CONFIG marking was also considered and declined: the only real
customer is a whole file that is a set (the bench's), a mixed
build/descriptive file has no named consumer (D77), and a per-config
mark would re-open the reader's question ("which configs does this
build honour?") that a single head line answers at a glance.

### 2.21 `mc` — the counting rule, stated and MEASURED ([B42] N-32,
P-Q3; **deviates from the pre-ruled formula on measured evidence**)

`mc "<subject>" <n>` / `mc @file:"…" <n>` asserts that the find-all
protocol over the subject reports exactly `<n>` matches. **The rule is
`docs/spec/match_api.md` §3.1's shipped protocol, by reference**:
non-overlapping; after a non-empty match the search resumes at its END
(`caps[0][1]`); after an EMPTY match it resumes one CHARACTER past the
match's REPORTED START (`<prefix>_next_pos(caps[0][0])` — one byte under
`-e byte`); no empty-match retry.

Three rules were measured head to head before this paragraph was
written (§0.6), because the manager's pre-ruling spelled the rule as
the bench's `pos = max(end, pos+1)` and the two are NOT the same:

| rule | `(?=a)` on `"xax"` | `a*?` on `"aaa"` |
|---|---|---|
| §3.1's protocol | 1 match | 4 |
| `pos = max(end, pos+1)` (bench `adapters.py`) | **2 — the empty match at offset 1 is found twice**, once from pos 0 and again from pos 1 | 4 |
| python `re.finditer` / PCRE2's NOTEMPTY loop | 1 | **7** |

The bench formula DOUBLE-COUNTS an empty match found beyond the scan
position (its `max` returns the match's own position when the match
lies ahead of `pos`); the protocol advances past the reported start and
cannot. And BOTH non-retry rules undercount `finditer` on
empty-preferring patterns — the NOTEMPTY class §3.1 already documents,
spans a strict subset, **which pcrec's entry points cannot express**.
So the spec paragraph states the §3.1 protocol: it is already shipped,
already suite-checked (`tests/encseam/findall_cases.txt`), and the one
rule all of pcrec's own artifacts can actually implement. The bench's
own note anticipated this outcome ("if the intended answer is 'the
harness's rule', say that") and their adapter owes one edit —
empty-match advance from the reported start, not `max` — which §9's E5
group and the outbox summary carry to them.

Consequences stated so nobody re-derives them: an `mc` over an
empty-preferring lazy pattern will NOT agree with a `finditer` count —
an author gets the number from the protocol; `verify_rxt.py` verifies
`mc` lines by RUNNING THE PROTOCOL LOOP in python (search-from-pos,
the two-arm advance), **never `finditer`**; and the driver's find-all
mode (H7) is the same loop in C, which is the loop `match_api.md` §3.1
prints. One rule, three implementations, one cross-check (C1's case
rows plus the E5 fixture).

**THE RULE IS INSUFFICIENT ON ILL-FORMED UTF-8, AND 3.2 SAYS SO
NORMATIVELY** (r57 C-S6). "One character past the reported start" is
`<prefix>_next_pos` by REFERENCE, which is exact for a byte subject and
for well-formed UTF-8 and is **underspecified for an ill-formed one** —
`match_api.md` §3.1.1 never defines "character boundary" there, and a
foreign adapter reading the prose cannot derive what pcrec's artifacts
do. That is not hypothetical: the bench's own corpora carry
hazard-tagged ill-formed subjects, and `mc` is a count they will
compare against.

So **SW7 states the shipped rule as normative text** rather than
leaving it to the reference: *from `pos + 1`, skip bytes in the range
`0x80`-`0xBF`* — i.e. advance one byte and then past any continuation
bytes, which lands on the next lead byte or on the end. It is adopted
because it is what the emitted artifacts already do (it is
`next_pos`'s own rule, the encoding seam's, `[K49]`'s advance), not
because it is the most principled reading of UTF-8; a reader who wants
the principle gets the byte rule anyway, which is the point of writing
it down. **E5's fixture becomes utf8-bearing and says so** — the
find-all cross-check runs at least one `mc` over an ill-formed subject
under `-e utf8`, because a rule stated for a case no fixture reaches is
a sentence (§9's E5 row).

**And the tension this creates is acknowledged rather than argued
away.** The python arm REIMPLEMENTS the advance — `verify_rxt.py`
cannot call `next_pos`, so it carries the skip rule in python — which
is the second-implementation shape §2.19 argues against one production
over, when it refuses a `printf %b` decoder in bash. The difference,
and it is the honest one: the bash case had no cross-check available
and would have drifted silently, while here the three implementations
are compared cell for cell by C1's case rows plus E5's fixture, on a
population that includes the ill-formed subjects the rule is about.
**A second implementation with a differential is a cost; a second
implementation without one is a defect.** This is the first kind, and
the differential is what is being paid for.

### 2.22 Regime membership: §4.5 item 4 REPAIRED, not replaced
([B42] N-48, P-Q5, roadblock in their §2.11)

§4.5 item 4's mechanism — the canonical pattern once as a `name`d
definition, one block per regime whose pattern is a subroutine call —
was MEASURED UNUSABLE for every bench pattern id: a call goes through
PCRE2's own group-name grammar, which refuses `-`/`.`, and every id in
all five bench sets is a hyphenated slug. The name grammar was widened
FOR those ids; the call grammar cannot be (D26 — it is PCRE2's).

**The repair is the DERIVED-IDENTIFIER CALL BINDING** (the bench's
option 3, confirmed): a by-name call binds to a definition whose name,
mapped through `pcrec_rxt_prefix_from_name` (`src/parse/rxt_source.c:337`
— the ONE existing home of the `-`/`.` → `_` rule, already what
`target = <name>` derives a prefix with), equals the call's identifier.
`(?&cls_upto_1024)` reaches `name cls-upto-1024`.

- **WHERE it happens, verified against the shipped composer**: the
  binding is `src/parse/rxt_compose.c`'s definition-set lookup — the
  exact-`strcmp` sites at `rxt_compose.c:169` (inside **`def_by_name`**)
  and `:176` (inside `bound_by_name`), consumed by the re-resolution at
  `:690`/`:788` that binds each DEFERRED by-name call.
  **(3.2, r57 C-M3: revision 3.1 called the first function `def_find`;
  there is no such function. It is `def_by_name`, declared at `:166`.
  A misnamed citation is worse than no citation — a reader greps, finds
  nothing, and cannot tell whether the function moved or the claim is
  wrong.)**
  The composer resolves a file reference AFTER the pattern's own groups
  (a call to a same-pattern group never defers, `:260`), so PCRE2's
  in-pattern semantics are untouched; the derived index is a second key
  on the SAME set, built with the same function, consulted by the same
  lookup. No new pass, no new namespace.
- **THE PRECEDENT IS `rxt_compose.c:854-864`, not the two `strcmp`
  sites** (3.2, r57 C-M3). The sites above are where the change LANDS;
  they are generic plumbing and they justify nothing on their own. The
  design precedent — a composed identifier SYNTHESIZED from two parts
  and then checked for collision against everything already in scope —
  is the qualified-rowname synthesis at `:854-864`: a delivering call's
  row name is `site` + `.` + the exported group's name, built into arena
  memory, and `:865-877` then refuses by name if any existing
  `cx->named_groups` entry already carries it, with the comment stating
  the reason a silent tie-break is not available (*"a row name is a
  caller's whole handle on a delivered group, so two rows sharing one
  would make `match_api.md` §6's bsearch return whichever the sort
  happened to put first"*). §2.22's rule is that shape one derivation
  over: synthesize, then refuse the tie. Citing it matters because it
  shows the refusal is the house pattern rather than this section's
  invention — and because it is the one place in the composer where the
  length question below was already faced.
- **THE COLLISION RULE, and its LENGTH DISCIPLINE** — the target-prefix
  rule re-used at the second consumer. The mapping is deliberately not
  injective, and the refusal is where that is paid for. Two definitions
  in scope whose mapped names are equal make a call to that identifier a
  **refusal naming both definitions and the shared identifier** —
  including the case where one of them IS spelled as the identifier
  (`x_y` beside `x-y`): exact spelling does NOT win, because "exact" is
  only the identity case of the same mapping, and a silent tie-break
  would make the non-injectivity free exactly where it bites. Nothing is
  refused at DECLARATION time — two colliding definitions coexist while
  nothing calls the shared identifier, just as two hyphenated
  definitions coexist while neither is a `target =`.

  **NEW AT 3.2 (r57 C-M3): REFUSE BEFORE MAPPING.**
  `pcrec_rxt_prefix_from_name` (`rxt_source.c:337`) **silently
  TRUNCATES** at `dstsz` — its loop condition is `j + 1 < dstsz` and
  there is no over-length return — so two long names differing only past
  the buffer map to the SAME identifier and would bind silently. The
  existing consumer never meets this, and the reason is an ordering
  nobody wrote down as a rule: `parse_target` refuses an over-long
  definition name FIRST (`rxt_source.c:826-830`, `dlen >= sizeof def`
  against `RXT_TARGET_DEF_MAX` = 127) and only then calls the mapping
  (`:840`). **The second consumer must reproduce that order, and this
  is where it is stated**: the composer refuses an over-long definition
  name by name before deriving anything from it, so truncation is
  unreachable rather than merely unobserved. The alternative — making
  the mapping itself report over-length — was considered and declined:
  it has one existing caller that has already handled the case, and
  changing a shipped signature to defend a caller that can defend itself
  is the wrong direction. What the format owes is the ORDER, written
  down, because "the existing consumer happens to check first" is not a
  property the next consumer inherits.

  **AND THE CALLABILITY BOUND: 128 bytes** (r57 C-M3). A definition's
  `name` has **no length cap at all** today — `rxt_source.c:1124-1137`
  validates the grammar with `defname_ok` and stores it — while a
  `(?&…)` call goes through PCRE2's own name grammar, capped at
  `PCREC_MAX_GROUP_NAME` = 128 (`src/core/limits.def:151`, measured
  against libpcre2 10.46's error 148). So a definition longer than 128
  bytes is **buildable and not callable**, which is the same boundary
  SW12's paragraph already draws for a hyphenated spelling, arriving by
  a different route. This is stated as **inherited from PCRE2 under
  D26** rather than re-declared as a pcrec limit: the number is PCRE2's,
  the format does not get to widen it, and a `name` cap of its own would
  be a second answer to a question PCRE2 already answers. The spec
  sentence is SW12's; the schema's `constraints` column carries no
  length row, and §2.25 says why (a limit whose value is another
  project's is not schema data — `--list-limits` is where it lives, and
  `PCREC_MAX_GROUP_NAME` is already a row there).

  **AND IT IS A NARROWING, declared**: `(?&x_y)` beside a definition
  `x-y` compiles today and is refused under this rule — §1.6.1a case
  (5), with its measured population (0 for this shape, 1 for the general
  collision shape, both repos), its forced-vs-**CHOSEN** verdict, and
  its spec sentence. Revision 3.1 stated this rule without noticing it
  narrows, which is what §1.6.4's new case 4 exists to stop.
- **The three-reader rule is NOT touched, and that is the design's
  cheapness**: the NAME grammar's three readers
  (`rxt_source.c:298 defname_ok`, `run.sh:2015`, `verify_rxt.py:331`)
  keep their one shared grammar unchanged — the call's spelling stays
  PCRE2's, the definition's stays the wide grammar, and only the
  composer's LOOKUP (leg A's semantics, single implementation) learns
  the map. Legs B and C never resolve calls, so there is nothing for
  them to disagree about; C1's differential covers the dump, not the
  binding, and the binding's check is W1.3-C's family with a hyphenated
  fixture (§9's A-group note).

**§4.5 item 4 is then usable AS DESIGNED**, with its surviving caveats
restated rather than lost: the wrapper is free exactly while the
expectations carry no capture columns (Q6's trigger, unchanged); a
composed block's oracle is necessarily `pcre2` (§2.9/H4) — for the
bench a non-question, since python was never their oracle; and a plain
call is capture-transparent, which is all a regime wrapper needs.

**Why regime grouping does NOT admit children** (the
alternative the manager asked weighed): a `regime` sub-block holding
case lines would (a) be a CASE SCOPE, which Frank ruled out by name
("there is no case scope") — an attribute over a group of cases is that
ruling's own definition; (b) put case lines under indentation, forcing
all three body readers to re-parse their most load-bearing arms
(`run.sh`'s case dispatch) for a shape one consumer needs; and (c) buy
nothing the repaired wrapper does not already deliver with machinery
that SHIPPED in W1.3. The child-admitting kinds are
attribute records (provenance, variant) — bounded, non-case,
skip-safe; case lines stay flat.

### 2.23 `variant` — reshaped as a sub-block, and `kind` ([B42]
N-39/N-40/N-41, pre-ruling f)

`variant <testee>` becomes a SUB-BLOCK (§1.2) with attributes `text`,
`kind`, `groups`, `note`, `unsupported`:

```
variant re2
  kind syntax-only
  text ^a{1,4}$
  groups num=1
  note |
    the possessive suffix dropped; RE2 has no backtracking for it to
    prune, so the objective (a bounded scan) is preserved.

variant tre
  unsupported no per-engine spelling preserves the objective
```

- **Exactly one of `text` / `unsupported`** — neither is a refusal
  naming the variant; both is too. `kind`/`groups`/`note` are legal only
  beside `text` (a declared refusal has no replacement text to
  classify).
- **`kind` is closed via `vocabulary kind`** when declared (§2.15) —
  the bench's two-value enum stays the bench's vocabulary, per AR-6.
- **`note` is the reviewer's objective-preserved sentence** — N-41's
  third field, previously routed to `tag variant-note=…` where a
  tag-value's no-whitespace rule made a sentence unspellable. With
  `tag-prose` (§1.3) that route now also works for OTHER descriptive
  keys; the variant's own note lives with the variant, one home.
- **Why the reshape is free and right**: the W3 one-line form shipped
  nowhere (refused by name at every pin; 0 uses in either repo), so no
  compatibility cost exists; and revision 2's `variant` already needed a
  SECOND line (`groups`, an un-indented continuation recognised by
  keyword) — a one-off proto-sub-block the general mechanism replaces,
  which is the house rule (general mechanisms, not special cases)
  applied to this note's own earlier choice.
- **`text` and not `pattern` — REVISION 3.1 REPLACES THE REASON, and
  keeps the spelling** (§2.26 item 9). Revision 3 justified it as a
  PARSER HAZARD: an indented `pattern` line might start a block in one
  reader and continue a sub-block in another. **Under §1.2.1 that
  hazard is impossible IN ANY READER THAT IMPLEMENTS S1/S2** — a block
  opener applies among SIBLINGS and a child is not a sibling, so an
  indented `pattern` can never open a block in a conforming reader,
  whatever the attribute is called. **Qualified at 3.2 (r57 S-S5)**:
  "conforming" is the load-bearing word and revision 3.1 dropped it.
  Leg A gets the property by construction once H16 lands; legs B and C
  are independent implementations and get it by being PINNED (§9's
  A-group), which is the same distinction §2.25.5 draws about every
  three-leg claim in this note. The surviving reason is a reader's,
  not a parser's, and it holds either way: this
  field holds a REPLACEMENT for the block's pattern, and calling it
  `pattern` would put the format's most load-bearing token at a second
  scope meaning something adjacent-but-different. An expired argument
  is worse than no argument, so it is replaced here rather than left
  standing.
- Everything r44/T-2 established stands: block-scoped, beside the
  pattern, checked against the block's own expectations (as selected by
  the testee's convention, §2.17), no `name`, not a target, not
  composable. `unsupported` remains the declared, counted refusal
  (R-BENCH-3; AR-3).

### 2.24 `--list-source` at W23: columns, SECTIONS, and what the dump
VALIDATES ([B42] N-52, pre-ruling g)

The dump is THE SEAM, and the bench loader reads ONLY it (their D2) —
so everything W23 adds must come out of it, case lines included, or the
bench writes the second parser the seam exists to prevent.

**Appended columns** (table_contract.md: append-only, consumers resolve
by NAME): on pattern rows `tags` (accumulated, escaped), `oracle`,
`esc` (§2.19); on config rows `testee`, `options` (accumulated),
`provides` (accumulated). New head ROW kinds (the existing "`kind`
carries the declaration name" rule): `vocabulary` (name = the key,
value = the escaped list), `configs` (value = `build`/`describe`),
`include`, `oracle`, `tag`, `use`.

> **THE EXISTING `pattern` COLUMN NOW MEANS TWO THINGS, AND THE
> DEPENDENCY IS MARKED HERE WHERE CONSUMERS LOOK** (NEW at 3.2, r57
> C-N10). For a `pattern` block the column is the line's bytes
> VERBATIM; for a `pattern-esc` block it is the DECODED bytes,
> re-escaped in the dump's own vocabulary (§2.19). Both are the
> pattern text and the round trip is byte-exact either way, so nothing
> is ambiguous once a reader knows — but §2.19 is where the fact was
> disclosed and §2.24's column list is where a consumer building a
> loader reads. **The `esc` column is what disambiguates them**, and
> the rule is stated as a pair: *read `pattern` together with `esc`; an
> exporter reproducing the source file needs both, and a consumer that
> only wants the pattern's BYTES needs neither, because both spellings
> deliver the same bytes.* Named as a documented same-column widening
> rather than a second column, because a `pattern_decoded` column
> beside `pattern` would give every consumer two fields that agree on
> every existing row — the shape that goes stale the first time one of
> them is written and the other is not.

**Three named SECTIONS, emitted UNCONDITIONALLY when non-empty**, under
`docs/spec/table_contract.md`'s `#section` mechanism — the trigger
`rxt_format.md` itself named ("a data block whose rows cannot be
columns of this table under any reading") is met by `provenance`, and
the same argument covers the other two:

- `#section provenance` — one row per provenance block: `line`,
  `block_line`, `block_name`, then the record's fields as columns
  (eleven at revision 3.1, and the section carries a data block's
  provenance on the same rows — one record, one section), prose
  escaped.
- `#section variants` — one row per variant: `line`, `block_line`,
  `block_name`, `testee`, `kind`, `text`, `groups`, `note`,
  `unsupported`.
- `#section cases` — **one row per case line, and this is the biggest
  single extension**: `line`, `block_line`, `block_name`, `kind`
  (`m`/`n`/`ms`/`ns`/`mc`/`gu`/`g`/`gp`), `under`, `startpos`,
  `subject_form` (`inline`/`file`), `subject` (escaped text or path),
  `subject_id`, `sha256`, `start`, `end`, `count`, `giveup`, `slot`,
  `route` (the positional `frames-buffer=` state the case runs under —
  the dump is complete or it is not the seam). Today the dump has no
  case column AT ALL, and the head parser's own comment says it reads
  none of their values; under Option A the expectations ARE the set's
  truth, so they must be readable at the seam.

**Emission is unconditional, not flagged and not content-conditional**,
and the compatibility story is stated rather than hoped: a section is
emitted only when it has rows, so a file using no W23 production emits
NO `#section` line and its stream differs from today's ONLY in the
header row's appended columns — which is `table_contract.md`'s own
compatible evolution, resolved by name. An existing corpus file's dump
therefore GROWS a `cases` section (its `m`/`n` lines), which moves the
`tests/rxtsource` pinned fixtures (re-pinned in the same change, the
normal ritual) and every name-resolving consumer not at all. A flagged
or content-conditional cases section was considered and declined: two
shapes of one dump is two consumer populations, and a section that
appears only when some OTHER production is present is a
population-nobody-counts trap (K35). The cost is size (a corpus file's
dump grows ~10x in rows); the dump's only harness call sites are
head-bearing files only, so `make test` pays nothing today.

**The VALIDATES vs RECOGNISES table** (their D4, pre-ruled) becomes a
NORMATIVE spec section (§3.4 SW11), production by production. The
substance: the dump VALIDATES everything it emits — head grammar,
block directives, child-record completeness (provenance's required
fields, variant's exactly-one rule), vocabulary membership, case-line
syntax including `as`/`sha256` SPELLINGS and the subject-id binding
rules — and it does NOT (a) read any subject file (the `sha256`
CONTENT check belongs to whatever reads the subject, §2.18), (b)
compile any pattern (pattern TEXT is never validated here), or (c)
resolve configs (AS WRITTEN, unchanged; `--resolved` stays named and
unbuilt). The bench's measured observation that a case line's refused
`@file:` passed the dump silently is thereby retired — case values are
read, and an ill-formed one is a hard error naming its line.

**REVISION 3.1 UPGRADES THAT TABLE FROM PROSE TO A DERIVED FACT**
(Frank's consequence 3: *"with a schema, validation coverage is a
derivable fact instead of a prose sentence"*). The paragraph above is
a claim a reader has to trust and a future wave has to remember to
update; both are the failure mode this project has recorded under
`[DOC-DRV]` one document over. So:

- **Every schema row carries a `validated_by` column** (§2.25) with a
  closed value set: `pcrec` (leg A validates it; legs B and C consume
  the line and do not check it) or `all-readers` (every leg must
  refuse a violation — the population C1's differential can actually
  compare).
- **The spec's D4 table is RENDERED from that column**, not written
  beside it, exactly as `docs/pcre2_compliance.md`'s keyed annotations
  are rendered into the page rather than maintained in it. A
  production added without a `validated_by` value is a schema-table
  error, so the table cannot go stale by omission — the one way prose
  tables always go stale.
- **`--list-schema` prints it**, so "does the dump check X?" is a
  query rather than a reading. The three NOT-validated items above
  (subject content, pattern text, config resolution) carry
  `validated_by: none` and a `reason` string, which is why they stay
  visible instead of becoming an absence nobody counts (K35).

  **WHERE THOSE THREE ROWS ACTUALLY LIVE, because two of them are not
  (scope, line-kind) pairs and the table is keyed on (scope,
  line-kind)** (NEW at 3.2, r57 S-S3 — and these are the items most
  likely to fall back to prose, which is the D4 probe's whole subject):

  | not validated | its home | why there |
  |---|---|---|
  | **subject CONTENT** (the `sha256` digest against the file's bytes) | the `m`/`n`/`ms`/`ns`/`mc` rows' own `validated_by: none` **with the reason "the dump performs no file I/O"** | it IS a (scope, line-kind) fact — the case line is where a subject reference appears, so the row exists and carries the value. The SYNTAX (64 hex digits) is validated on the same row; the two are distinguished by the reason string, not by two rows |
  | **pattern TEXT** (never compiled here) | the `pattern` and `pattern-esc` rows' `validated_by: none`, reason "the dump is parse-only; pattern text is the compiler's" | also a genuine (scope, line-kind) fact |
  | **config RESOLUTION** (the `with`/`from` cascades, composed) | **NOT a line-kind row at all** — it is the ABSENCE of `--list-source --resolved`, a surface that is named and unbuilt (§3.4 S11's neighbourhood). It gets a **named sibling surface row** in `--list-schema`'s output: a `surface` section listing the dump's declared NON-coverage, one row, reason "`--resolved` is named and unbuilt; the dump is AS-WRITTEN", with `--list-source`'s own header comment as the prose that already says it |

  The third is the one worth the paragraph: revision 3.1 called all
  three "rows with `validated_by: none`", and for config resolution
  there is no row to put the value on — the fact is about the dump's
  MODE, not about any line kind. Left as written, the D4 probe would
  look for a row, not find one, and either report a gap that is not
  there or (worse) conclude the table is incomplete. A declared
  non-coverage section is one more thing `--list-schema` prints and it
  keeps the rendered D4 table complete by construction, which is the
  whole reason the column exists.

**`all-readers` IS A CLAIM ABOUT TWO PARSERS THE SCHEMA DOES NOT
DRIVE, AND AT 3.2 IT OWES A FIXTURE PER ROW** (r57 S-M2, a MUST-FIX).
The value says *every leg must refuse a violation of this row* — but
the schema table is leg A's (§2.25.5, and deliberately so), legs B and
C never read it, and **the corpus population is EMPTY by construction**:
0 files use any W23 production, so no existing `.rxt` exercises a
single `all-readers` row in any leg. Revision 3.1's defence for the
column was that a row added without a `validated_by` value is a
schema-table error — which is true and addresses OMISSION, while the
live risk here is WRONGNESS: a row marked `all-readers` that legs B and
C do not in fact enforce, shipping as a printed, rendered, normative
claim that nothing tests.

So the obligation is stated as a rule with a check behind it:

1. **Every `validated_by: all-readers` row owes a THREE-LEG FIXTURE** —
   a `.rxtin` cell violating that row, asserted refused by leg A, leg B
   and leg C, compared on **diagnostic CLASS** and not exit code
   (§2.25.5's rule, because leg B refuses everything identically).
2. **"The fixture population covers every `all-readers` row" is ITSELF
   A CHECK**, not a discipline: it walks `--list-schema`'s own output,
   selects the `all-readers` rows, and fails naming any row with no
   fixture. That is the same one-derivation shape the dump already has
   — the check reads the table the parser enforces, so a row added
   later fails the check the day it lands rather than the day somebody
   remembers.
3. **A row whose fixture is not written yet takes `validated_by:
   pcrec`**, not `all-readers`. The honest value is the cheap one, and
   a row can be promoted later; the failure this rule exists to stop is
   a row claiming three legs on the strength of one.

§9's A3/A4 name the fixtures; §3.2's S-R1 is the sabotage row that
proves the differential can see a divergence at all.

The prose above survives as the SUBSTANCE the rows must reproduce; if
the rendered table and this paragraph ever disagree, the table is
right and this paragraph is the bug.

### 2.25 The SCHEMA — the format's rules as data (Frank's consequence 3)

*"The format's structural rules — which line kinds are legal in which
scope, required and conditional lines (provenance's REQUIRED-iff),
closed value sets — are DECLARED as a schema and VALIDATED, not
implicit in parser control flow."*

#### 2.25.1 What it is, and the house shape it takes

**One table, one reader, one dump** — `docs/spec/limits.md` /
`--list-limits`'s own shape (D90/[LIM-1]), which is the precedent this
design copies rather than a new idea:

- **The table**: a `.def`-style declaration file compiled into the
  parser (`src/parse/rxt_schema.def`, on `src/core/limits.def`'s model
  — including its Makefile-prerequisite lesson, `ccd2_report.md` §6b:
  a `.def` that is not a prerequisite lets an edit rebuild nothing).
- **The reader/enforcer**: `src/parse/rxt_source.c`'s dispatch becomes
  a walk over the table rather than a chain of arms that each remember
  their own rules. Its shape is `src/parse/definitions.c`'s
  `pcrec_def_tag_applies`: ONE exhaustive, `default:`-less switch over
  the constraint enum, so a constraint kind added later is a compile
  error at the one site that must handle it (`src/opt/mrl.c:18-24`'s
  stated rule, the house's own).
- **The surface**: `pcrec --list-schema`, a TSV, the **SEVENTH**
  registry dump beside `--list-syntax` / `--list-verbs` /
  `--list-families` / `--list-axes` / `--list-limits` /
  `--list-definitions`. It walks the same table the parser enforces —
  **one derivation, two readers** (learnings §3) — so a dump that
  disagrees with the parser is not expressible.
  **(3.2, r57 S-N1: revision 3.1 wrote SIXTH in the same sentence that
  lists six existing dumps. `docs/spec/cli.md:586` already calls
  `--list-limits` "the SIXTH"; `--list-source` makes seven producers in
  `table_contract.md`'s Scope table, of which `--list-schema` would be
  the eighth conforming table and the seventh REGISTRY dump. The
  ordinal is corrected at all three sites — here, §3.3 and SW17 — and
  `docs/spec/registry.md`, whose own numbered sequence stops at the
  FIFTH surface because it documents neither `--list-limits` nor
  `--list-source`, gains both the row and the reconciliation. An
  ordinal that is wrong in the sentence that enumerates its own
  predecessors is the cheapest possible instance of a number nobody
  re-derived.)**

#### 2.25.2 The columns

One row per (scope, line-kind):

| column | what it says |
|---|---|
| `scope` | `file`, `block`, or a named child scope (`config`, `data`, `provenance`, `variant`) |
| `kind` | the first token |
| `value` | the value shape: `none`, `token`, `int`, `line`, `prose`, `list`, `pair`, `subject`, `qualified-line`, … |
| `opens_group` | **structure-layer parameter 1** (§1.2.1 S2). True for `pattern` and `pattern-esc` and nothing else |
| `children` | `none`, `prose`, or the child scope this kind admits |
| `cardinality` | `one`, `at-most-one`, `repeat`, `accumulate` — **and its values for the settings kinds are stated below (3.3), not left to the implementer** |
| `constraints` | zero or more from §2.25.3's closed vocabulary |
| `source` | `format` (pcrec declares it) or `file` (a `vocabulary` line declares it, §2.15) |
| `validated_by` | `pcrec`, `all-readers`, or `none` + a reason (§2.24) |
| `wave` | which delivery introduced it — so a partial build's "NOT IN THIS BUILD" list (SW13) is derived rather than hand-kept |

**THE `wave` COLUMN IS KEPT, and the decision is stated rather than
assumed** (3.2, r57 S-S2). The challenge is fair: its only named
consumer is SW13's partial-build refusal list, and **at the delivered
pin that consumer has an empty population** — W23 lands as one wave, so
no shipped build ever refuses a W23 keyword for being in a later wave.
A column whose consumer is empty at delivery is normally the D77
decline.

It is kept because **the consumer is real DURING the rollout, which is
when SW13's own rule matters**. W23 is one delivery but it is not one
commit: H12, H13, H14, H15 and H16 land as separate steps behind
separate merges (§3.2's table is written as a dependency order for
exactly that reason), and every intermediate tree is a partial build in
which some W23 keywords parse and others must refuse BY NAME rather
than as unknown tokens — which is SW13's whole point, measured against
the gap §0.6 found (`vocabulary` reads "not a file-level directive"
today, the K14 shape: sending a reader hunting a typo in a word that is
in the spec). Deriving that list from a column the same table carries
is what keeps the intermediate trees honest without anyone hand-editing
a list five times.

The honest limit, so a later reader can re-decide: **after W23 lands,
the column's population is one value and its consumer is dormant until
the next wave.** It is one enum per row and it costs a column in a TSV;
if a future wave finds it has stayed a single value through two
deliveries, dropping it is a one-line change and this paragraph is the
permission.

**`value: prose` IS structure-layer parameter 2, and `children: prose`
is how the two columns are reconciled** (NEW at 3.2 — r57 G-B3, a
MUST-FIX, and it was a genuine contradiction rather than an omission).
Revision 3.1 gave `description` both `value: prose` and — by the
`children` column's only available spelling — `children: none`. Read as
written, that makes every block-scalar continuation line a schema error
against its own parent: the line attaches (S1 had no carve-out), the
parent admits no children, refusal. The construct §1.2.5 deliberately
widens would be **unrepresentable in the table §2.25 calls normative**,
which is the worst of the three available outcomes for a declared
schema.

The reconciliation, and it is one sentence with one precedence rule:

> **`children: prose` means the kind's indented lines are its VALUE,
> not lines in a scope.** A row may carry `value: prose` only together
> with `children: prose`, and the pair is what a generic reader reads
> as "this kind can open an S3 opaque region". There is no precedence
> question left, because the two columns no longer say different
> things about one row — the `none`/`prose`/`<scope>` trichotomy
> covers the three real cases: takes nothing indented, takes bytes,
> takes lines.

`--list-schema` prints both columns, so H12's assumption — the one
revision 3.1 made silently in the H-table and nowhere declared — is now
a row a reader can fetch. The alternative (keep `children: none` and
state that `value: prose` OVERRIDES it for attachment) was considered
and declined: an override is a precedence rule, precedence rules are
remembered rather than read, and this table exists to stop rules being
remembered. A three-valued column costs one enum member.

`opens_group`, `value` (for `prose`), `children` and `scope` are what a
generic reader needs; everything else is validity. **The structure
layer reads exactly THREE of them as TWO parameters** — `opens_group`
is parameter 1, and `value`+`children` READ AS A PAIR are parameter 2
— and §1.2.1's parameter table is the normative statement of which.
**(3.3, r57 ROUND 2 R2-F4: revision 3.2 said "exactly two … `value =
prose`" in this very paragraph while the reconciliation four paragraphs
above said the PAIR, and §1.2.1/§1.2.2 each picked one. The PAIR is the
answer, on S-R5's detectability: with `value` alone read, flipping a
row's `children` from `prose` to `none` changes nothing observable —
the region still opens and its lines never reach a validity check — so
a normative column would have no detector at all.)**
That they are columns of one table rather than separate mechanisms is
the two-layer split made concrete.

**THE CARDINALITY VALUES FOR THE SETTINGS KINDS, DECIDED HERE** (NEW at
3.3, r57 ROUND 2 R2-C, a SHOULD the manager escalated because leaving
it open makes it an accept→reject taken by accident). `cardinality` is
normative on every row, and six kinds silently LAST-WIN on the shipped
binary today while a seventh in the same family refuses — so any value
H16 writes is a compatibility decision, and writing none is the worst
of the three available outcomes.

| kind | scope(s) | shipped today | `cardinality` at W23 | corpus + bench population of the refusal |
|---|---|---|---|---|
| `name` | block | silent last-wins | `at-most-one` | 0 |
| `engine` | block, `config` | silent last-wins | `at-most-one` | 0 |
| `encoding` | block, `config` | silent last-wins | `at-most-one` | 0 |
| `features` | block, `config` | silent last-wins | `at-most-one` | 0 |
| `flags` | block, `config` | silent last-wins | `at-most-one` | 0 |
| `description` | file, block | silent last-wins (block) | `at-most-one` | 0 — **already landed by STEP 0**, §1.6.1a (11) |
| `export` | block | **already REFUSES** (`rxt_source.c:1184`) | `at-most-one` | 0 — no change |
| `budget` | block, `config` | silent last-wins PER FIELD | **`accumulate`** over the field set `{steps, frames}`, with a repeated FIELD refused | 1 block repeats the LINE legitimately; 0 repeat a FIELD |

Three things about that table are worth more than the values in it.

**(a) `budget` is the row the measurement changed.** R2-C's proposal
grouped it with the scalars; `tests/harness/giveup.rxt:19-23` writes
`budget steps=50` and `budget frames=4096` in one block on purpose, and
`parse_setting` (`rxt_source.c:615-620`) routes the two to separate
slots. `at-most-one` would have refused a shipped corpus file. So the
cardinality attaches to the VALUE SPACE the kind writes into, not to
its spelling, and `budget`'s refusal is at the field.

**(b) `flags` was not on the panel's list and is on this one.** R2-C
named five; measuring the shipped arms found `flags` in identical
state. Leaving it as the one scalar settings kind that still last-wins
would reproduce the inconsistency this decision exists to remove, one
kind smaller — and the point of a `cardinality` COLUMN over six
hand-written refusals is precisely that the answer is uniform where the
kinds are uniform.

**(c) The precedent is internal, twice.** `export` refuses a duplicate
today and STEP 0 made `description` do the same; the five remaining
last-wins kinds are the outliers, not the rule. §1.6.1a rows (8) and
(9) carry the population, the forced-vs-chosen verdict and the spec
sentence, per §1.6.4 case 4.

#### 2.25.3 The constraint vocabulary, and its MEMBERSHIP RULE

**EIGHT kinds at revision 3.2, and the count moved for the right
reason** (r57 S-BL1, a BLOCKER). Revision 3.1 declared five and claimed
they cover the delivery; the panel tested four W23 refusal rules
against them and **all four fail** — one needing precisely the kind
§2.25.4 deferred, one with no expressible form at all, one mapped to a
kind whose semantics would refuse the production's own normal
spelling, and one ranging over fields inside a value. **The
completeness claim is withdrawn and three kinds are admitted**, each
under the section's own membership rule — copying §2.10's discipline
for the data-block family, because the hazard is identical: **a
constraint kind is admitted only when a production in THIS delivery
needs it.** No kind is added on plausibility; each row names its
customer, and all three new rows name customers that were already in
the text.

| constraint | means | its W23 customer |
|---|---|---|
| `required` | the line must appear in its scope | `provenance`'s `source`/`retrieved` (+ `license`/`fidelity` under a pattern block); the data block's `question`/`reader`/`analyzer` |
| `required-if <field> <op> <value>` | required when a sibling holds a value | `adaptation` REQUIRED iff `fidelity != verbatim` (§2.14 rule 3) — the conditional Frank's ruling names by example |
| **`forbidden-if <field> <op> <value>`** | **refused when a sibling holds a value** (NEW at 3.2) | `provenance`'s `authored` rule (§2.14 rule 2): `url` and `ref` are required unless `source` is `authored`, **and refused when it is**. `required-if` expresses the first half and cannot express the second |
| `exactly-one-of <a> <b>` | exactly one of a sibling set | `variant`'s `text` vs `unsupported` (§2.23) |
| `closed <set>` | the value must be a member of a set declared IN THIS ROW's own scope | `fidelity`'s three (`source: format`); `kind`, `convention`, any `vocabulary`-declared key checked at its own `tag` site (`source: file`) |
| **`cross-scope <scope> <kind> <selector>`** | **the value must satisfy a declaration resolved in a DIFFERENT scope** (NEW at 3.2) | `provides` ⊆ `vocabulary requires` (§2.16): a `config`-body line whose legal values are fixed by a FILE-scope `vocabulary` declaration under a DIFFERENT key name (`requires`). Neither end can state this alone — `closed` resolves in its own scope, and the `vocabulary` row does not know `provides` exists |
| `unique-by <key…>` | at most one row per key tuple, **the tuple being the WHOLE row's identity** | `under` per (convention, subject, kind, startpos) (§2.17); a `vocabulary` key; a `configs` line |
| **`functional-binding <key…> -> <value…>`** | **equal keys must carry equal values; unequal values with equal keys are refused naming both lines** (NEW at 3.2) | a subject `as` id (§2.18): one id maps to one (path, sha256), **re-stating the same binding on many case lines is the NORMAL spelling** |

**Why `cross-scope` is admitted NOW and not deferred, and the deferral
it replaces was a CONTRADICTION rather than a judgement.** Revision
3.1's §2.25.4 deferred "constraint kinds beyond the five (ordering,
cross-scope, arithmetic)" with the trigger *"the sixth W-something
production that needs one"* — and §2.16, one section earlier in the
same revision, states exactly such a production: *"when a
`vocabulary requires …` declaration exists, every `provides` value must
be a member of it"*. A W23 production met the deferral's own trigger
before the deferral was written, so the two sentences contradict inside
one document. The membership rule's bar is met and the kind is
admitted; what stays deferred is ordering and arithmetic, which have no
customer. **The general lesson this section keeps**: a deferral with a
trigger has to be checked against the delivery it ships with, not only
against the future — the whole point of a named trigger is that
somebody looks to see whether it has already fired.

**Why `forbidden-if` is a kind and not a `required-if` with a negated
operator.** It was tried that way first and it does not type-check
against the rule it has to express: `required-if` says *a line must be
PRESENT when a condition holds*, and negating its operator gives *must
be present when the condition does NOT hold* — which is `url`'s
ordinary case, not `authored`'s refusal. The two rules govern
opposite outcomes for the same field under complementary conditions,
and the format needs to state both, so there are two kinds. They share
a condition grammar and one arm of the exhaustive switch each.

**Why `functional-binding` is a kind and not `unique-by`, and this one
is a REAL BUG revision 3.1 shipped.** §2.18's rule is that re-stating
the same `as <id>` binding on many case lines is the normal spelling —
the id travels with every case line that names the subject — and only a
CONFLICTING re-binding is refused. `unique-by <id>` says *at most one
row per id*, which would refuse §2.18's own documented normal spelling
on its second occurrence. **A functional dependency is not a uniqueness
key**, and mapping one to the other inverts the production. The new kind
states the dependency directly: the id is the key, `(path, sha256)` is
the value, equal keys with unequal values is the refusal, equal keys
with equal values is legal and unremarkable.

**What is NOT admitted, and each says where it lives instead.**

- **`under`'s duplicate key ranges over fields INSIDE a value**, not
  over sibling lines: the tuple is (convention, subject, kind,
  startpos), and three of those four are components of the
  `qualified-line` value rather than lines of their own. `unique-by`
  can hold the tuple, but something has to EXTRACT it, and a
  value-shape field extractor is a mechanism this delivery has exactly
  one customer for. **So the extraction is PARSER CODE, with its
  reason recorded here rather than left as an unexplained exception**:
  `value: qualified-line` already means the parser decomposes this
  value into a case line (that is what the value shape IS), so the
  components are in hand at the site that already has them, and a
  declared extractor would be a second description of a decomposition
  the parser performs anyway. The schema row carries
  `unique-by under-key` and the spec names the four components; the
  arm that builds the tuple is code. A SECOND `qualified-line`
  production with a different key is the trigger to make the extractor
  declarative (D77), and at that point it is one kind plus one arm.
- **Ordering and arithmetic constraints** stay deferred with their
  trigger (§2.25.4), unchanged: no W23 production needs either.

**Cardinality is a column and not a constraint** because every row has
one; the constraints are the things most rows do not have. **This is
also where §9's C7 and this section are reconciled** (r57 S-S7):
"at most one `provenance` per parent" is `cardinality: at-most-one`
and NOT a `unique-by` row, and revision 3.1 called it both — inflating
`unique-by`'s earned-ness by counting a cardinality fact as its
customer. One fact, one mechanism. The duplicate-refusal discipline
§8's P-Q9 states production by production is then TWO mechanisms rather
than six hand-written refusals — `cardinality` for "at most one of
these", `unique-by` for "at most one per key" — which is still the
clearest measure of what the schema buys, at an honest count.

**The completeness claim is WITHDRAWN.** Revision 3.1 said the five
kinds cover the delivery. Eight cover it plus one rule that is
deliberately parser code with its reason stated, and that sentence —
"eight kinds and one named exception" — is what §2.25 claims now. The
difference matters beyond the arithmetic: a schema presenting itself as
a complete declaration while a refusal rule lives in control flow is
the worst of the three outcomes §5.2a item 4 names, because a reader
consulting `--list-schema` would get a confident wrong answer about
what the parser enforces.

#### 2.25.4 What is DEFERRED (with its trigger, D77), and what is DECLINED

The schema ships at exactly the size W23's own productions enforce.
Named, so the boundary is a decision rather than an omission —
**and separated at 3.2 into two lists, because revision 3.1 put a
permanent decision in the deferral table and a deferral whose trigger
had already fired beside it** (r57 S-S1, S-BL1(a)).

**DEFERRED — a named trigger, not yet fired:**

| deferred | trigger to build it |
|---|---|
| **A file-declared SCHEMA** (a file adding line kinds, not just values) | a second project wanting its own productions. `vocabulary` is the file-declared half that exists, and it declares VALUES only — the asymmetry is deliberate: values are data, line kinds are a grammar, and a format whose grammar varies per file is not one format |
| **ORDERING and ARITHMETIC constraint kinds** | the W-something production that needs one. No W23 production does. Adding a kind is one enum value plus one arm of an exhaustive switch, so waiting costs nothing. **(3.2: `cross-scope` left this row — its trigger had already fired inside this delivery, §2.25.3.)** |
| **A declarative value-shape FIELD EXTRACTOR** (so `under`'s key tuple could be a schema row rather than parser code) | a SECOND `qualified-line` production with a different key. One customer does not pay for a declaration mechanism; two would, because at two the extraction rule stops being the parser's own decomposition and starts being a thing two sites must agree about |
| **A machine-readable schema export for the bench's loader** | their asking. `--list-schema` is a TSV today; whether they consume it is theirs (D78) |

**DECLINED — no trigger, because the reason is architectural and
permanent:**

| declined | why it is a decline and not a deferral |
|---|---|
| **Generating legs B and C's arms from the table** | The table is pcrec's; **legs B and C are independent implementations ON PURPOSE** (§1.1's three-checks rule — a generated leg B would share a source with what it controls, which is the check-design failure this project has recorded most often). The schema makes the three legs *comparable* and must not make them *the same*. **Restated as a DECLINE at 3.2 (r57 S-S1)**: revision 3.1 filed this with the trigger *"the C1 differential finding a leg-B/leg-C divergence the schema would have prevented"*, which reads as "we will do it when it pays" — but that event is precisely the differential DOING ITS JOB, and generating leg B in response would delete the instrument that found the divergence in order to fix the divergence. There is no measurement that makes this right, so there is no trigger, and calling it deferred invited a future lane to fire it |

#### 2.25.5 The honest limit

**The schema is pcrec's, and pcrec is one of three readers.** It makes
leg A's rules data; it does not make legs B and C's rules data, and
the previous subsection says why that is deliberate rather than
unfinished. What the schema adds to the three-reader problem is
precisely one thing, and it is the thing that was missing: **a written,
printable statement of what the three are supposed to agree about**, so
C1's differential compares them against a specification instead of
against each other. Revision 3's "the indentation test precedes
dispatch in all three body readers" was exactly a rule with no such
home, and it was false in two of the three (§0.7). That is the defect
class this section exists to retire, and it is worth more than the
refusals it tidies.

**AND THE DIFFERENTIAL MUST COMPARE DIAGNOSTIC CLASS, NOT VERDICT**
(NEW at 3.2, r57 S-S8, and it is the limit that makes the paragraph
above honest). Leg B refuses every unrecognised line by CATCH-ALL
fall-through — 22 arms, none tolerant of leading whitespace, then
*"unparseable .rxt line (hard error)"* — so leg B refuses a W23
production it has never heard of, an indented line, a schema violation
and a typo with **the same verdict and the same sentence**. A
verdict-only C1 differential therefore reads "all three legs refuse"
and goes green for a `validated_by: all-readers` row **while leg B has
no rule for it at all**: the one live check on the `all-readers` claim
would be satisfiable by accident, on a population of one message.

So C1 compares a DIAGNOSTIC CLASS per refusal, not an exit code: which
rule was violated (structure-attachment / unknown-token-in-scope /
schema-constraint / value-shape), carried as a stable tag beside the
D26-free wording. That is a real obligation on legs B and C — leg B
must grow the classification it does not have today, which is part of
H12 — and it is the price of the `all-readers` column meaning anything.
D26 is not in tension with this: the classification is a TAG the check
reads, not a sentence a human reads, and D26 governs wording.

**What that leaves genuinely unresolved, stated rather than tidied**:
three independent implementations of a written specification can still
all three be wrong in the same way, and nothing here fixes that. The
schema narrows the failure from "three implementations disagree and
none is authoritative" to "three implementations agree against a
printed rule", which is strictly better and is not the same as correct.

### 2.26 The OWNERSHIP AUDIT — every W23 spelling, under long-term viability

Frank's second 2026-09-12 ruling: *"these are capabilities that bench
requires but syntax is yours and you're responsible for the long term
life of the format. therefore, find the structure that is
self-consistent, clear, and long term viable."* That makes long-term
viability the criterion ABOVE bench convenience and above
minimal-diff-from-today, and it makes this the cheapest moment a
spelling will ever change. So every production revision 3 added is
swept once: **confirmed with the one line of why it is the long-term
right spelling, or moved now.**

| # | production | verdict |
|---|---|---|
| 1 | `pattern-esc` | **CONFIRMED.** It is one of the block-opener set's two members (§1.2.1 S2), so its name is structure-layer vocabulary and must read as a sibling of `pattern`; the hyphenated compound does that where a flag on `pattern` (`pattern -e …`) would put a value shape inside the one production the format promises is rest-of-line verbatim. Hyphenated keywords are already the house spelling (`frames-buffer=`, `license-note`) |
| 2 | `provenance` | **CONFIRMED.** The domain word, and it now names ONE record at two parents (item 10), which is what a general name has to earn |
| 3 | `vocabulary` | **CONFIRMED AS A SPELLING, NESTED AS A CONCEPT** (§2.15). It is the FILE-declared rows of §2.25's schema, not a mechanism beside it; a second file-declarable schema fact joins it as a sibling declaration under that heading rather than as an unrelated head keyword, and `--list-schema`'s `source` column is where the nesting is visible. Renaming it to `values` was considered and declined: the bench's note, the acceptance checks and Frank's own ruling all use this word |
| 4 | `capable` → **`provides`** | **MOVED** (§2.16). The pattern side of the relation is `tag requires=…`; `requires`/`provides` is one relation read from its two ends, and is the pairing every neighbouring ecosystem uses. `requires`/`capable` pairs a verb with an adjective and leaves the reader to infer they are halves of one thing. Free: 0 occurrences in any context. W23-F2's question to Frank is unaffected — it asks WHERE the capability model lives, not what the line is called. **AND WHAT HALF IT DELIVERS, stated at 3.2 (r57 G-B5): the rename buys a READING symmetry the GRAMMAR does not have, and that is all it buys.** The two ends are different kinds — `provides` is a line kind in a `config` body, `requires` is a tag KEY in a `tag` item — and the closed set constraining `provides` is declared under the other end's name at file scope (`vocabulary requires …`). So a reader who learns `provides` has no syntactic path to its value set. The rename makes the RELATION legible; §2.16's new pointer sentence and §2.25.3's `cross-scope` row make it FINDABLE. Neither alone is enough, and revision 3.1 claimed the first and shipped neither |
| 5 | `under <conv> <case-line>` | **CONFIRMED, and given a schema home.** The qualifier is a PREFIX so the case line after it is byte-identical to an unqualified one — which is what makes "the qualifier wraps a case line UNCHANGED" a checkable property rather than a hope, and a suffix form would not. Its one oddity — a line kind whose value CONTAINS another line kind — is now expressible as schema data (`value: qualified-line` over a closed kind set, §2.25.2) rather than as a parser special case |
| 6 | `configs build`/`describe` | **CONFIRMED.** It names the thing it governs (the file's `config` blocks) and takes a closed mode value, so a third mode is a `closed` set member and not a new keyword. `config-mode` was considered and declined as longer for no disambiguation |
| 7 | `as <id>` / `sha256 <hex64>` | **CONFIRMED, and the reason is worth stating because "why not `hash`?" is the obvious question.** Naming the ALGORITHM in the keyword means a second algorithm arrives as a sibling (`sha512 <hex>`) rather than as a re-interpretation of an existing field's value — the failure mode every `hash:`-style field eventually has. `as` is the import-idiomatic binder |
| 8 | `tag-prose` (`key="…"`) | **CONFIRMED — and the pairing with `\|` is RE-WORDED at 3.2** (r57 G-B1). The quoted form is discriminated by the first byte after `=`, as `\|` discriminates a prose value's two forms, and both are declared per line kind in the schema's `value` column. But revision 3.1's phrasing — *"value-form discriminators… never structural"* — is false of `\|`, which opens an S3 OPAQUE REGION whose EXTENT is structural (§1.2.1, §1.2.4's table). The surviving statement is the true half: **both are value-form discriminators; `"`'s value ends on its own line and `\|`'s ends on a later one, and a discriminator that selects a multi-line form is ALSO a structure device.** `tag-prose`'s own spelling is unaffected and stays confirmed — it is the single-line one |
| 9 | `variant`'s `text` | **CONFIRMED, REASON REPLACED** (§2.23). Revision 3's justification was a parser hazard §1.2.1 makes impossible in any reader implementing S1/S2 — **qualified at 3.2 (r57 S-S5): that is a property of the SPECIFICATION, and legs B and C implement it independently, so it is pinned by §9's A-group rather than inherited.** The surviving reason is a reader's and does not depend on the qualification: the field holds a replacement FOR the block's pattern, and reusing the format's most load-bearing token at a second scope for something adjacent-but-different is how a vocabulary stops being learnable |
| 10 | `provenance`'s fields, and the `freq` block's | **MOVED — the audit's biggest finding.** Revision 3 shipped **two provenance vocabularies for one idea**: `exemplar`/`date`/`bytes`/`sha256`/`analyzer` on a data block, `source`/`url`/`ref`/`licence`/`retrieved`/`fidelity`/… on a pattern block, with `exemplar`≡`source` and `date`≡`retrieved` naming the same facts twice. Unified into ONE record used at two parents, its REQUIRED subset declared per parent by the schema (§2.10, §2.14). `analyzer` deliberately stays on the data block — it names the TOOL, not the origin. And `licence`/`licence-note` → **`license`/`license-note`**, because the value is an SPDX identifier and SPDX's own key is `License`. All free: 0 uses in either repo |
| 11 | `mc` | **CONFIRMED.** Two letters, joining the `ms`/`ns` terse case-line family; a case line's kinds are the format's highest-frequency tokens and the family's brevity is deliberate |
| 12 | `oracle <engine>[/<version>]` | **CONFIRMED.** `/` separates a name from a version everywhere a reader has met the idea, and it appears nowhere else in the token grammar, so it cannot be mistaken for anything |
| 13 | inherited W2/W3 spellings (`include`, `use`, `tag`, `@file:`, `config … testee`/`option`, `freq`, `analysis`) | **CONFIRMED as a group.** Each was ruled or accepted before [B42] and none was moved by this revision's productions; the ownership ruling makes them mine to change, and sweeping them found no case where a name misleads. `@file:`'s sigil is the one worth naming: it marks a VALUE as a reference rather than literal bytes, which is a value-form discriminator in the §1.2.4 sense and therefore already has a home in the vocabulary this revision built |

**What the audit did NOT change, deliberately.** Nothing in the
SEMANTICS moved: every need's disposition, every refusal rule, every
P-Q answer and the whole wave table are revision 3's. An ownership
ruling about syntax is not a licence to reopen settled meaning, and a
sweep that re-decided semantics would be the lane spending Frank's
ruling on something it did not buy.

---

## 3. Migration

### 3.1 The existing corpus: nothing changes

**No existing line changes meaning, and no existing file changes at
all.** §1.1 states this as INV-COMPAT with three independent checks and
six sabotage rows; §2.4 shows the only construct that could have
interacted — the 143 blocks carrying a by-name subroutine reference —
is untouched, because 139 of them resolve **within their own pattern**,
so composition binds nothing and the compiler input is unchanged, and
the other four are `perr` blocks in a file with no definitions.

The corpus is **179 files / 3,265 blocks / 26,691 expectation lines**
(MEASURED 2026-08-29). The [DD-13a] census read 54 / 1,100 / 9,977 on
2026-08-17; the corpus has grown 3.3× in twelve days, which is exactly
why requirements.md §13 item 5 told the panel to re-run it rather than
trust it. **AR-1's cost of getting this wrong has tripled since the
requirement was written.**

### 3.2 What the harness must gain

In dependency order. Each item is a *change to the harness*, not to the
format, and each is named so a lane brief can be written from it.

| # | change | wave | touches |
|---|---|---|---|
| H1 | **A head parser**: parse file-level declarations and `config`/data blocks above the first `pattern`; hard-error on an unknown first token per context | W1 | `tests/harness/run.sh` |
| H2 | **PCREC's composer** (D87 rule 1): file reference detection, definition lookup on D85's table, the visited-set closure, name qualification, number assignment and re-basing, and **per-node PROVENANCE** (§2.12). This is PCREC code, not harness code — the first version put it in the harness | W1 | `src/`, reached by `--source` / `--lib-path` |
| H2b | **The harness's textual EXPAND, as the ORACLE CONTROL** (§2.3.4): the DEFINE-append form, plus the VALIDITY TEST that decides whether the control may run at all — no absolute numeric reference in any body, no name collision between caller and closure. Outside that population the control is a counted, named skip, never a silent pass | W1 | `tests/harness/` |
| H2c | **`--emit-composed` and its round trip**: pcrec writes the composed pattern with explicit numbers (§1.5), and the `A == B` control recompiles it and compares against the `--source` build | W1 | `src/`, `tests/harness/` |
| H3 | **Cells**: run a block once per resolved config; report cells in the summary; the `perr` one-cell rule | W1 | `run.sh` summary + dispatch |
| H4 | **`verify_rxt.py` reads H2b's EXPANDED text**, not the source block. python `re` has **no** subroutine call at all (CITED, `subroutines_design.md` §10.1: "not different semantics, an ABSENCE"), so **any composed block is `oracle pcre2` whether or not it says so** — a python oracle cannot check a composed pattern, and pretending otherwise would be a silent pass | W1 | `verify_rxt.py` |
| H5 | **Include resolution + entry-set subtraction + closure accounting** (§2.11) | W2 | `run.sh` discovery |
| H6 | **`@file:` subjects — and the DRIVER PROTOCOL CHANGE they force.** Today a subject travels as `argv[1]` (`t <subject> [startpos] [route]`), which can carry neither an embedded NUL nor a megabyte. The driver needs a form that names a path and reads it byte-exactly — the natural spelling is a leading sentinel on the existing argument (`t @<path> …`), which is additive and leaves every existing invocation untouched | W2 | `tests/harness/driver.c`, `run.sh` |
| H7 | **`mc` find-all counting** against `match_api.md` §3.1's restart semantics | W2 | `driver.c` |
| H8 | **`tag` well-formedness only** — the harness validates the *shape*, never the vocabulary | W2 | `run.sh` |
| H9 | **Data-block parse + `--exemplar`-shaped hand-off to pcrec** (D83's flag takes the findings file, never the raw text) | W2 | `run.sh`, pcrec CLI |
| H10 | **`use` / `variant` / `oracle` / testee configs** | W3 | `run.sh` + a non-pcrec adapter, which is pcrec-bench's, not pcrec's |
| **H11** | **THE TARGET BUILD PATH — W1 ships with it, not without it** (r44-sem M9). Nothing in H1-H10 compiled or ran a `target … with <config>`: `driver.c` hard-codes the prefix `rx` and `run.sh` passes `-p rx`, so the central new build declaration would have had no test path at all. The harness must BUILD every declared target and assert two things per target — the emitted symbols carry its **prefix**, and `rx_info.name` is the definition's `name` — with the driver taking the prefix (a `-D` prefix macro or a generated shim). It is also the only path that exercises §2.7's output naming and §2.13's struct | W1 | `tests/harness/run.sh`, `tests/harness/driver.c` |

**At revision 3 the H-table's W2/W3 labels all read W23** (§1.4 — one
delivery), H1/H2-family/H11 are BUILT with W1, and four rows join:

| # | change | wave | touches |
|---|---|---|---|
| H12 | **the ATTACHMENT arm** in all three readers (§1.2.1 S1): compute a line's parent from its indent BEFORE dispatching its first token, consume children for a kind that admits them (`provenance`, `variant`, and any `prose-value`), and raise the two refusal arms (attaches-to-nothing; parent takes no children). **REVISION 3.1 makes this bigger and simpler at once**: bigger because leg B has no indentation test at all today and leg C's is below its pre-body dispatch (MEASURED, §0.7), so this is a rule to BUILD in two legs rather than to extend in three; simpler because it is one mechanism serving children AND block scalars AND head continuation, where revision 3 had a sub-block arm beside them | W23 | `run.sh`, `verify_rxt.py` (pcrec's own arm rides SW2/SW16) |
| H13 | **`pattern-esc`**: the pass-through arm + the CLI decode flag; `verify_rxt.py` decodes python-side; `\x00`'s K9 refusal surfaces through pcrec (§2.19) | W23 | `run.sh`, `verify_rxt.py`, `cli/` |
| H14 | **`under` as a counted, labelled skip** in `run.sh` and `verify_rxt.py` (scoring is the consumer's, §2.17); `mc` verified by the PROTOCOL loop in python, never `finditer` (§2.21) | W23 | `run.sh`, `verify_rxt.py` |
| H15 | **subject ids + hashes**: the per-file binding table, the read-time sha256 refusal on the driver path (§2.18); `configs describe`'s one-cell rule and its summary line (§2.20) | W23 | `run.sh`, `driver.c` |
| H16 | **THE SCHEMA TABLE AND ITS SURFACE** (§2.25), NEW at revision 3.1: the `.def` declaration compiled into leg A, leg A's dispatch re-shaped as a walk over it with ONE exhaustive `default:`-less switch over the constraint enum, `--list-schema`, and the D4 table RENDERED from `validated_by` rather than hand-written. **It touches leg A only, deliberately** (§2.25.4): legs B and C stay independent implementations, because a generated leg B would share a source with what it controls — the check-design failure this tree has recorded most often. **H16 CARRIES THE CARDINALITY DECISION EXPLICITLY (3.3, r57 ROUND 2 R2-C)**: the `.def` writes `at-most-one` for `name`/`engine`/`encoding`/`features`/`flags`/`description`/`export` and `accumulate` (field set `{steps, frames}`) for `budget`, per §2.25.2's table, so six settings kinds stop silently last-winning in the same change that declares them. The refusal names BOTH lines, `export`'s shipped diagnostic being the wording precedent, and §1.6.1a rows (8)/(9) are its compatibility record | W23 | `src/parse/` (`rxt_schema.def`, `rxt_source.c`), `cli/`, the spec renderer |

**SIX sabotage rows** (four at revision 3.1, re-spelled and split at
3.2 per r57 S-M3/S-M4/S-S6, plus one new for S3), each naming the
check that must catch it, because a rule stated in a table is a rule a
table can be sabotaged in (`docs/dev/learnings.md` §3). **Two rules the
3.2 pass applied to every row and that a future row should inherit**:
a row's detector must live in THIS repo's matrix, and a row must fail
on the tree it is planted into rather than on a later drift.

| row | plant | must be caught by |
|---|---|---|
| S-R1 | flip one schema row's `children` from `none` to a scope (say `m` admits children) | the indented-line fixture (§9's A-group): an indented line under `m` stops being an error in leg A while legs B and C still refuse it, so the C1 differential goes red — **and the row is deliberately planted in the direction where only the DIFFERENTIAL can see it**, since leg A alone would simply accept more |
| S-R2 | drop `provenance`'s `required-if` constraint for `adaptation` | **a PCREC-SIDE fixture pair** — `tests/rxtsource/fixtures/` gains `prov_adapted_no_adaptation.rxtin` (must be refused) beside `prov_verbatim_no_adaptation.rxtin` (must be accepted), and the sabotage must flip the first to accepted. **RE-HOMED AT 3.2 (r57 S-M3)**: revision 3.1 named the bench's C5/C6 as the detector, and they live in the OTHER REPO — planting this row turns nothing red in pcrec's own battery, so `make mech` would score it UNDETECTED and be right to. The bench's C5/C6 are CORROBORATION, and valuable as an independent second reading; they cannot be the detector for a row in this repo's matrix |
| S-R3 | make `--list-schema` print a hand-written table instead of walking the enforced one — **and the hand-written copy DISAGREES on exactly one row**: it reports `provenance.fidelity` as `closed`, and the parser's own row is edited to `source: file` with no set | **a dump-vs-behaviour cross-check, widened past `closed` (r57 S-M4)**: for each row, the check exercises the BEHAVIOUR the dump claims and requires agreement — a violating value for `closed`/`cross-scope`, a missing line for `required`, a present-when-forbidden line for `forbidden-if`, a conflicting re-binding for `functional-binding`, a duplicate tuple for `unique-by`, an indented line for `children`, a second opener for `opens_group`. **REWRITTEN AT 3.2**: revision 3.1's plant was "a hand-written table" with no stated divergence, which PASSES whenever the copy is faithful — it detects DRIFT, and a sabotage row must fail NOW, on the tree the matrix runs against. The disagreeing row is what makes it fail immediately. The widening matters independently: seven of the eight columns were unchecked against behaviour, so a dump could claim any `children`, `cardinality` or `validated_by` value and nothing would notice |
| S-R4a | **remove `pattern-esc` from `opens_group`** | the structure layer's own fixture: a `pattern-esc` line stops opening a block, so its case lines attach to the PRECEDING block and `--list-source`'s `#section cases` rows move `block_line`. The symptom is the moved `block_line`, and it is visible in the dump |
| S-R4b | **add a THIRD member to `opens_group`** (say `m`) | **a different detector, and this is why the row is split (r57 S-S6)**: a case-bearing fixture whose `m` lines stop being cases of their block and become blocks of their own, caught by the block COUNT in `--list-source` and by `run.sh`'s own case totals. Revision 3.1 bundled this with S-R4a as "add `pattern` a second time, or remove `pattern-esc`" — and the first half is **silent**, because the opener set is consulted by first-match-wins membership and a duplicate `pattern` row changes no answer at all. A sabotage row that plants two things where one does nothing scores DETECTED on the strength of the other and reports the pair as covered. Two rows, two symptoms, two detectors |
| S-R5 | **break `description`'s prose PAIR — in EITHER column**: plant (a) flips its `value` from `prose` to `line`; plant (b) flips its `children` from `prose` to `none`. Either removes the kind from the structure layer's SECOND parameter (§1.2.1) | the ragged-prose and prose-`#` fixtures (§9's A-group): with `description` no longer prose-region-opening, `description \|` opens no opaque region, so its continuation lines re-enter S1 and the indented `#` becomes a structure error and the ragged line an attachment error — all three legs must report the value, and leg A's changes. **NEW at 3.2**, because S3 gave the structure layer a second parameter and §1.2.1's own argument for S-R4 applies to it verbatim: it is a column the structure layer reads, so its corruption is invisible to every schema-VALIDITY check, which is exactly the class that needs a sabotage row rather than an assertion. **BOTH PLANTS NAMED AT 3.3 (r57 ROUND 2 R2-F4), and plant (b) is why the parameter reads the PAIR**: if the structure layer read `value` alone, (b) would change nothing observable anywhere — the region still opens, its lines are bytes, and bytes reach no validity check — so a normative column would carry a corruption with NO detector. Reading the pair makes (b) fail the same fixtures (a) does |

**H4 deserves its own line in a brief**, because it is the one place a
plausible implementation is silently wrong: handing python `re` the
*unexpanded* text would make it compile the primary alone (the `(?&n)`
raises `re.error`, so it would be skipped rather than mis-verified —
but a *skip* that nobody counted is AR-3's failure mode exactly).

**H2 and H2b are SEQUENTIAL, not one derivation** (r44-consumers U9).
Two resolutions run, in order, and confusing them is how a control ends
up sharing a source with its subject:

1. the FORMAT's cross-file resolution — which definitions are bound into
   this pattern, with what numbers and what name qualification (H2, in
   pcrec);
2. pcrec's own intra-pattern `(?&name)` binding in `recursion`'s AST,
   which runs on the resulting pattern exactly as it runs on any other.

H2b's textual expansion is a THIRD, independent path to the same
intended answer, written for the oracle. Its value is precisely that it
does not share step 1's implementation — which is also why it must
declare the population where it is valid rather than silently agreeing
everywhere.

### 3.3 What `--list-*` surfaces are affected

- **`--list-syntax` GAINS ROWS, and this is a change from the first
  version.** That version said "this design adds no construct", which was
  true of textual composition and is false of D87: §1.5's numbered group,
  scope prefix and delivering call are three new PATTERN constructs, and
  the registry is where a construct's existence, its owning module and
  its `built` status are stated (D65). They are DIALECT rows — spellings
  PCRE2 refuses (measured, §1.5) — which is the same shape
  `pcre2_compliance.md` already handles for pcrec-only forms. The
  constructs composition RIDES are unchanged and already `built`:
  `(?&name)`, `(?(DEFINE)…)` and the named-group spellings (MEASURED,
  §2.3.3).
- **`--list-definitions` gains a second reason to exist.** Beyond D85's
  option-scoped replacements, a user of a library wants to see what
  `lib <rfc5322>` brought into scope. Same table, same surface (§4.2).
- **`--list-definitions` is [DD-11]'s fifth registry surface** (D85), and
  the format is one of its two readers, not its author. §4.2 states the
  interface.
- **`--list-schema` is NEW at revision 3.1 and is the SEVENTH** (§2.25;
  3.1 said SIXTH — r57 S-N1, corrected at all three sites, and
  `docs/spec/cli.md:586` already gives `--list-limits` that ordinal):
  the format's own structural rules as a TSV, walked off the same table
  the parser enforces. It is the surface Frank's consequence 3 asks
  for, and it is what makes §1.2.1's **two** keyword-dependent
  parameters — the block-opener set and the prose-valued kind set — a
  query rather than hard-coded facts. Same
  one-derivation-two-readers discipline as every dump beside it, and
  the same `table_contract.md` obligations as every table beside it
  (SW17's row there, r57 S-M7).
- **New, and owed by this row when W1 lands**: a way to ask a *file* what
  it declares — the targets, their prefixes, their configs and their
  definitions — because a build system needs it and because a person
  needs to check that a target list says what they think. It reads the
  parsed file, so it has **one derivation and two readers** (learnings
  §3): the same resolver the harness runs. It is **named here and not
  specified**, because its consumer ([V-E]'s build integration) is not
  real yet and D77 applies — the trigger is [V-E] opening, not W1
  landing. Frank's `description` ruling sharpens what it would print: a
  file's summarizing script reads `description` fields, so the surface is
  "what this file declares, with each declaration's description", not a
  bare list of names.

### 3.4 The spec delta (D80: the contract changes in the same change)

`docs/spec/rxt_format.md` is the contract, and a parser landing without
its spec hunk is rejected on sight (D80; CLAUDE.md's situation index).
The hunks, named so a reviewer can check them off:

| # | hunk | wave |
|---|---|---|
| S1 | "The `.rxt` format" gains **HEAD and BODY**: the head's six declarations, the two head block kinds, and the rule that the head ends at the first `pattern` line | W1 |
| S2 | A new section, **"Composition"**: the AST-level model, D87 rule 7's assignment rules (a)-(j), lexical-scope-wins with internal name qualification, the visited-set closure, the five namespaces, and the statement that a composed block's oracle is necessarily `pcre2` | W1 |
| S2b | `docs/spec/` gains the **pattern-language extensions** (§1.5): the numbered group, the scope prefix, the delivering call — each with the "no legal PCRE2 pattern changes meaning" constraint and the measurement that admits it. These are DIALECT constructs, so `--list-syntax`'s registry gains their rows (§3.3) | W1 |
| S2c | A **"Delivered results"** section: the inline struct, path = member path, first-set-wins for duplicate names in one path, the two non-deliverable shapes and their refusals, and the one sentence about two call sites being distinct C types needing `__typeof__` (§2.13) | W1 |
| S3 | "How the harness evaluates a block" gains the **cell** notion and the `perr` one-cell rule; the summary's reported quantities grow (entry files, fragments, cells, resolution failures) | W1 |
| S4 | The **subject** subsection gains `@file:"path"`, and states the escape asymmetry (quoted subjects decode escapes, file subjects do not) | W2 |
| S5 | "The driver protocol" gains the `@<path>` argument form and its byte-exactness guarantee | W2 |
| S6 | A new section, **"Data blocks"**: the family, the membership rule (`question`/`reader` required), `freq`'s body, and the provenance fields with the reason they are required | W2 |
| S7 | The `oracle` line and `# pcre2-only`'s status as its alias | W3 |
| S8 | `variant` and the declared-`unsupported` outcome | W3 |
| S9 | `docs/spec/match_api.md` §6: **`rx_info.name`**, and the `abi` bump sentence — one of D76's four sites, all four in the same change | W1 |
| S9b | `docs/spec/match_api.md` §2/§5: **D61 made concrete by its first producer.** `ngroups`/`nnames` are the PRIMARY's own on a composed artifact; the composition's delivered slots occupy `ngroups+1 ..`; `RX_NCAPS` is an artifact constant a caller sizes from the header and **may move across library versions** while every index in `1..ngroups` holds still (r44-sem M4/M5). Also the difference between `--source` composition and handing a composed TEXT to plain `-p`, which counts every group | W1 |
| S10 | `docs/spec/limits.md` "Handling an oversized artifact" item 1 already promises the `config` block; when W1 lands, that sentence stops being a forward reference and gains a pointer to S1 | W1 |
| S11 | `docs/spec/cli.md`: `--source`, `--target <prefix>`, `--lib-path DIR`, **`--emit-composed`**, and §2.7's **output-naming rule** (`-o <dir>` per target; `-o <file>` with N > 1 refused) | W1 |

**The W23 hunks** (revision 3; every one lands with the implementation
that makes it true, D80 — a reviewer rejects the change without them).
S1-S11's W2/W3 rows above are unchanged and land in the same W23
delivery; these are the [B42] additions:

| # | file | the hunk | wave |
|---|---|---|---|
| SW1 | `docs/spec/rxt_format.md` | `pattern-esc`: the second block starter, the seven-escape vocabulary shared with subjects, one-spelling-per-block, the `\x00` refusal naming K9 and its lifting trigger (§2.19); the CLI decode flag cross-reference | W23 |
| SW2 | `docs/spec/rxt_format.md` | **REWRITTEN AT 3.1**: the LEXICAL RULES section becomes the TWO-LAYER statement — the STRUCTURE layer (S0 line classes, S1 attachment, S2 the two-member block-opener set) and the pointer to the schema for everything else. The head/body indentation asymmetry is DELETED rather than narrowed, the "only asymmetry" sentence goes, the bare-indented-line refusal survives in its two arms (attaches-to-nothing / parent-takes-no-children), and `prose-value` becomes legal wherever the schema declares a prose value, at any depth (§1.2) | W23 |
| SW3 | `docs/spec/rxt_format.md` | `provenance`: the eleven fields, the per-parent required sets (a pattern block's four, a data block's four), the `authored` agreement rule, adaptation-iff-not-verbatim, one-per-parent, and the `license`/`license-note` spelling (§2.14). **Also the `freq` data block's body (S6's row extended)**: its five one-off provenance fields are REPLACED by this same record (§2.10, §2.26 item 10) | W23 |
| SW4 | `docs/spec/rxt_format.md` | `vocabulary` + `tag-prose` + `provides`: declaration, enforcement points (tag both scopes, `under`'s convention, `variant`'s kind, `provides`), the RESERVED-KEY sentence for `requires`, fail-closed `provides`, and `vocabulary`'s nesting as the FILE-declared rows of §2.25's schema (§2.15, §2.16). **At 3.2 (r57 G-B5) the RESERVED-KEY sentence names both ends in one sentence, in both directions**, so a reader who greps `provides` finds `vocabulary requires` and vice versa — the rename buys a reading symmetry the grammar lacks, and the spec is where the missing path is supplied | W23 |
| SW5 | `docs/spec/rxt_format.md` | `configs build`/`describe`: the four describe rules, the `target … with` refusal, `use` inert-and-counted, entry-file scope — and the PERMANENCE sentence for a target-less config-less file (§2.20) | W23 |
| SW6 | `docs/spec/rxt_format.md` | the subject subsection (S4's row extended): `as <id>`/`sha256 <hex64>`, the per-file id namespace and functional-binding rules, WHO checks the hash (§2.18) | W23 |
| SW7 | `docs/spec/rxt_format.md` + `docs/spec/match_api.md` | `mc` and its COUNTING RULE — one normative paragraph citing `match_api.md` §3.1 as the rule's single home, the empty-advance-from-reported-start clause, the finditer-divergence class named; match_api.md §3.1 gains one sentence naming `mc` as a consumer of the protocol. **PLUS, AT 3.2 (r57 C-S6): the ILL-FORMED-UTF-8 ADVANCE RULE, stated NORMATIVELY rather than left to `next_pos` by reference** — from `pos + 1`, skip bytes `0x80`-`0xBF` — because `match_api.md` §3.1.1 never defines "character boundary" on invalid input and a foreign adapter cannot derive the shipped behaviour from the prose. The hunk lands in match_api.md §3.1.1 (where the gap is) as well as in `rxt_format.md`'s `mc` paragraph (where `mc`'s consumer reads), and §9's E5 fixture becomes utf8-bearing so the rule has a cell | W23 |
| SW8 | `docs/spec/rxt_format.md` | `under`: qualifier semantics, fallback, duplicate refusal, the no-`g`/`gp` rule, the harness's counted-skip treatment (§2.17) | W23 |
| SW9 | `docs/spec/rxt_format.md` | `oracle` widened to `engine-ref [/version]`; `python`/`pcre2` meanings unchanged; absent-oracle = labelled skip (§2.9) | W23 |
| SW10 | `docs/spec/rxt_format.md` | `variant` as a sub-block: the five attributes, exactly-one-of-text/unsupported, kind's vocabulary hook (§2.23); supersedes S8's one-line shape | W23 |
| SW11 | `docs/spec/rxt_format.md` | `--list-source`: the appended columns, the three `#section`s with their column lists, the **VALIDATES vs RECOGNISES table as normative text — RENDERED from the schema's `validated_by` column at 3.1, not hand-written beside it** (§2.24, §2.25), and the SECTIONLESS paragraph rewritten — its own named trigger fired. `table_contract.md` needs NO hunk (sections were already its mechanism) | W23 |
| SW12 | `docs/spec/rxt_format.md` **+ `src/parse/rxt_source.c`'s TWO comment sites** | the `name` grammar section's "cannot be called from a pattern" paragraph AMENDED: still true of the hyphenated SPELLING (PCRE2's grammar, D26), and the definition is now reachable through its DERIVED identifier — the mapping, the at-use collision refusal naming both definitions, exact-spelling-does-not-win (§2.22). Plus the **refuse-before-mapping LENGTH rule** and the **128-byte callability bound** stated as inherited from PCRE2 under D26 (§2.22, r57 C-M3). **The three-reader note**: legs A/B/C's shared name grammar is UNCHANGED; the derivation lives only in the composer's lookup, so no reader gains an arm. **AND THE TWO SHIPPED COMMENT SITES, ADDED AT 3.2 (r57 C-M2)**: `rxt_source.c:280-291` (`defname_ok`'s header) and `:1126-1130` (the `name` arm's pointer to it) state the repealed boundary **AS A RULING** — *"A `-`/`.` definition is therefore BUILDABLE as a target and NOT CALLABLE from a pattern — exactly what a bench set needs, since its patterns never call each other"* — and the first invokes **D94 by name** two paragraphs down (*"THREE PARSERS READ THIS GRAMMAR AND THEY MOVE TOGETHER (D94's rule applied to a grammar rather than to a number)"*). A comment that records a ruling is a reader of that ruling, and D94's own lesson is that the site list is EVERY READER FOUND BY GREP. Both sites move in the same change; leaving them would put a shipped comment in direct contradiction with the shipped behaviour, which is the `nnames` staleness shape one file over | W23 |
| SW13 | `docs/spec/rxt_format.md` | the "NOT IN THIS BUILD" recognised-keyword list grows the W23 keywords, so any future partial build refuses them by name rather than as unknown (MEASURED gap, §0.6: `vocabulary` is "not a file-level directive" today). **At 3.1 the list is DERIVED from the schema's `wave` column** rather than hand-kept, and it gains one entry that is not a production at all: **`version`, RESERVED** (§1.6.3) | W23 |
| SW14 | `docs/spec/cli.md` | the `pattern-esc` decode flag; `--list-source`'s section output named in its entry | W23 |
| SW15 | `docs/spec/rxt_format.md` | the driver protocol: the find-all mode H7 lands (the §3.1 loop in C), the `@<path>` subject form's byte-exactness (S5's row, unchanged, referenced), the sha256 mismatch refusal | W23 |

**The revision-3.1 hunks**, all W23, all landing in the same delivery:

| # | file | the hunk |
|---|---|---|
| SW16 | `docs/spec/rxt_format.md` | **THE THREE-DEVICE STATEMENT AND THE VERSION RULE.** SW2 carries the structure layer; this row carries what goes with it: that a scope is a schema fact with no structural consequence (so "the head ends at the first `pattern` line" is stated as a scope rule and AR-4 is discharged by a declaration, §1.2.1), that `version` is RESERVED with absence meaning version 1 and its position fixed at the file's first content line (§1.6.3), and §1.6.4's **FOUR-CASE** standing rule for when a future change needs the line (3.2: the fourth case is a CHOSEN narrowing, r57 C-M1). **REWRITTEN AT 3.2 — it carries the WHOLE NARROWING CENSUS's spec sentences, not one** (§1.6.1a, r57 G-B2): (a) the ragged HEAD BODY, accepted and now refused because depth became meaningful; (b) **TAB indentation, accepted and now refused by name** — indentation is spaces, a leading tab is a structure error, a tab inside a VALUE is still data; (c) the two narrowings AVOIDED and the rule that avoids them — inside a `\|` prose region an indented `#` is PROSE and ragged indentation is legal, because S3's region has no line classifier, while OUTSIDE one the indented-`#` refusal is unchanged. (c) is spec text and not merely a design note because it settles a question `rxt_source.c:735-747` records as deliberately OPEN. (The fifth narrowing, the derived-identifier collision, is SW12's.) **It also carries the `description` widening**: a pattern block's `description` takes `prose-value`, superseding the W1.1 correction, with `tests/rxtsource/fixtures/block_scalar_in_body.rxtin` RE-AIMED (inverted to a three-way agreement on the decoded value) in the same change — a shipped refusal changing direction, so it is named in the spec rather than left to a fixture diff (§1.2.5) |
| SW17 | `docs/spec/rxt_format.md` + `docs/spec/cli.md` + **`docs/spec/table_contract.md`** + `docs/spec/registry.md` | **THE SCHEMA AND ITS SURFACE** (§2.25). rxt_format.md gains the schema section: the columns (including `children: prose`), the **EIGHT-kind** constraint vocabulary with its membership rule, the one named parser-code exception (`under`'s key tuple), the deferred/DECLINED split, and the statement that the parser is the table's reader. cli.md gains `--list-schema` as the **SEVENTH** registry dump, in `--list-limits`' own entry shape. `docs/spec/registry.md` gains its row in the surface list — **and, since its own numbered sequence stops at the FIFTH surface while two dumps (`--list-limits`, `--list-source`) are undocumented there, the row is added with the sequence reconciled rather than appended to a gap.** **`docs/spec/table_contract.md` GAINS ITS SCOPE ROW, ADDED AT 3.2 (r57 S-M7)**: that document's Scope section enumerates every conforming table producer (seven rows today) and states *"Future tabular surfaces adopt this contract AT BIRTH — a new table command that does not conform is a defect, not a style choice."* `--list-schema` is a TSV table command, so it is a conforming producer by that sentence and a reader found BY GREP for the surface list — **the D94 failure verbatim** (a hand-enumerated site list that missed a reader in a spec document), which this note has now had pointed out to it in the same shape twice |

**No `docs/spec/match_api.md` struct hunk and no abi bump anywhere in
W23** (§1.4), and revision 3.1 adds none — the schema is a parser-side
table and a CLI dump; nothing it touches is emitted scaffolding, so
D76's ritual is still not triggered. SW7's match_api sentence is prose
naming a new consumer of an existing contract.

`docs/guide/` is the human tier and points at these; it never restates
them (D80).

---

## 4. The seams

Each seam is stated as an **interface** — what this format needs from the
other row, or what the other row may rely on — never as that row's
implementation.

### 4.1 [LIB] — subpattern libraries

**[LIB] is what W1 exists for**, and it is `STATE:not-started` blocking
on this note ("depends on rxt format" — the row BLOCKS on [DD-13b]).
All three of its parts are covered by W1: (1) a file carrying several
patterns that reference each other is `name` + `(?&name)`; (2) a user
including a library and calling its subpatterns by name is
`lib "path"` / `lib <name>` + `(?&name)`; (3) a shipped **library store**
is the `<>` spelling's search path — pcrec's shipped store first, then
each `--lib-path DIR` in declaration order.

**What [LIB] may rely on:** a library file is an ordinary `.rxt`; it
declares definitions with `name`, carries their own tests as ordinary
cases, and carries a `description` per definition so a store index can be
generated rather than written (Frank's r44 ruling — "summarize via script
what a library has"). It declares **no targets**, and its tests **do not
run** in a file that `lib`s it (they run when the library file is itself
under test — which is what makes the store's "each entry oracle-verified"
discipline mean something).

**A library is self-contained, and after r44 that is a mechanism rather
than an assertion.** The first version said "a user cannot accidentally
satisfy a library's reference from their own file"; r44-sem M2 MEASURED
that FALSE under the textual model — a caller's `(?J)` plus a colliding
name handed the library's private helper to the caller's group, inverting
the library's answer. It is true under D87: a library's internal
references bind in the library's own lexical scope, and the composer
qualifies injected names internally, so the caller cannot name them at
all (§2.3.2, §2.3.3 M2). The caller can still reach them deliberately —
that is what the scope prefix is for — which is the difference between
"self-contained" and "sealed".

**What [LIB] must decide, not this note:** the store's location and
versioning ([DD-3]), whether `pcrec_options` gains a definitions input
and what `--lib FILE` means at the library API level, and the store's
authoring discipline (a D27-blinded author per entry). The format's
answer to "where do definitions come from" is a file; whether the C API
accepts them another way is [LIB]'s.

### 4.2 [DD-11] / D85 — the definition table

D85 rules that the replacement model is a **predicate-scanned table** on
[ENG-FORM]'s shape, and names this format as one of its readers:
"[DD-13b]'s `name`/`lib` resolution and the [LIB] store read the same
table (a library definition is a row whose predicate is the library's
presence)."

**RULED 2026-08-30 (manager, on [DD-13b.W1]'s Q-W3): this is a LISTING
interface, not a BINDING one, and the word "interface" below is read
that way throughout.** W1's implementation note found that the two
cannot be the same surface. The tree already reserves
`DEF_LIB_NAME_BOUND` (`src/core/internal.h:2536`, "NO PRODUCER YET —
[LIB]/[DD-13b]") and names `DEFK_TEXTFN` as what "[DD-13b]'s [LIB]
name-bound rows reuse later" (`internal.h:2564-2577`) — but `DefTextFn`
is `Ast *(*)(const char *operand, size_t len, Ctx *cx)` and its contract
is to return the core AST **spliced at the occurrence**, which is
INLINING. Composition must produce a **CALL**: a call restores the
callee's capture state on return and an inlining does not (§2.3.5's
first difference), and whether a call is spliced or linked is
`cg_eligibility`'s decision with its own `SLOT_SPLICE_SAVE` machinery —
"the format pins the answer; the compiler chooses the linkage". **So
W1 adds no `DEF_LIB_NAME_BOUND` producer**: the composer resolves names
itself, and `--list-definitions`'s "what did `lib` bring into scope"
surface (§3.3) READS the composer's resolved set — one derivation, two
readers. Items 1-4 below stand as the listing contract; item 1's
"BUILDER" is what the LISTING must be able to show, not a splice point.

**What this format needs from [DD-11]** — the interface, stated as this
side of the seam:

1. **A lookup**: `resolve(name, option-scope) -> a definition, or
   not-found`. The result must be able to be a **BUILDER** — an AST, or
   something that produces one — not only text (r44-consumers M12): D87
   makes composition an AST operation, so a text-only interface would
   force the composer to re-parse and would put a second parser where
   learnings §3 says not to. That is the whole surface; the format's
   resolver (§2.3.2 step 2) calls it and does not walk the table itself.
2. **Determinism and orderability**: the table's answer for a given
   (name, option scope) must be stable across a compile, and when two
   rows could apply the table's own first-applicable-wins rule decides —
   the format never breaks a tie.
3. **A duplicate report WITH ORIGIN**: the format must be able to ask
   whether a name is defined by more than one *file* in its scope,
   because that is refused by name (§2.2) and the refusal must say which
   two files. D85 frames a library definition as a row with a predicate,
   so "two libraries define `email`" is two rows with the same key — but
   a predicate tag carries no file identity (r44-consumers M12), so the
   **origin is a COLUMN on the [LIB] store entry**, not a parameter of
   the tag. The table reports both rows and their origins; the format
   refuses and names them.
4. **Nothing about the option-scoped rows.** `$` under `(?m)`, D66's
   assertion expansions, the possessive desugaring: the format neither
   sees nor spells those. They are the table's other customers.

**The reverse direction**, worth stating because D85's revisit-when
raises it: *"[DD-13b]'s wave 1 needs `name` resolution before [DD-11]
exists (then the table's first rows are library definitions and the
option-scoped rows follow)."* This note's recommendation is the
opposite order where it is free: W1's resolver is ~50 lines of name
lookup over parsed blocks, and building it *as* the table's first
consumer costs nothing extra — but if [DD-11] has not opened when W1
lands, W1 ships its own lookup behind interface (1) above, and [DD-11]
replaces the implementation without touching the format. That is
implement-then-replace, which memory
`pcrec-general-mechanisms-not-special-cases` permits explicitly, and it
keeps [LIB] from waiting on a second design.

### 4.3 [ENG-PGO] / D83 — the findings file

D83 rules the analysis runs **outside** pcrec, once per exemplar file,
delivering a **findings file pcrec accepts**, and that the file-general
and pattern-specific analyses are two files and two builds. Frank then
ruled the findings file **is** an `.rxt`.

**The interface**: the findings file is an `.rxt` whose head carries one
or more data blocks and whose body is empty. A user's file brings it in
with `include "…freq.rxt"` (or `lib`, if the same file also carries
definitions), a `config` selects a table by name (`analysis freq
loglines`), and a
`target … with <config>` builds a pattern against it. **The same pattern
built against two exemplars is two `target` lines** — which is the
property that made the target-as-declaration shape right (Frank §6.4).

**What [ENG-PGO] may rely on**: the block's shape and its required
provenance (§2.10); that the harness never interprets the table beyond
well-formedness; that the **analyzer is the only writer** of a findings
file (the R30 lesson: an archiver is the only writer of its output, and a
hand edit there is a red line — provenance imitation is worse than
absent provenance).

**What [ENG-PGO] owns**: the analyzer, D83's `--exemplar FILE`-shaped
flag, the built-in static fallback table when no findings file is given,
and — under D77 — whether any *second* family member is ever earned.
Its plan row says it blocks on "wave 2/3"; under F-Q1 there is no W2/W3
split left, so it blocks on the **one W23 delivery** and rides it
(§1.4).

### 4.4 [V-E] — the manifest, the finder, and compilation units

[V-E]'s manifest **is** the target list. Frank §6.4: "the target list IS
the manifest — one line per artifact, all at the top of the file."

- **R-VE-1** ("N named patterns → one emitted unit, perhaps several") is
  answered at the format layer by **one `.c` per target** (Frank's ruling
  6) and left open at the codegen layer: a single multi-pattern *unit* is
  [V-E]'s charter, and the format does not prejudge it — several targets
  in one file are several artifacts *by default*, which a later
  unit-emitting mode can group without any change to the declarations.
- **R-VE-2 / AR-2** (no dispatch for the statically-known single-pattern
  call) is preserved by §2.7's compatibility default: a one-unnamed-block
  file with no head has no references to bind, so the AST the compiler
  gets is the one it gets today and the output is byte-for-byte today's.
  **The format cannot add dispatch, because in that case it adds nothing
  at all.**
- **R-VE-3** (content-addressed shared-data dedup, and at what
  granularity) — **DEFERRED under D77, explicitly rather than by
  silence** (r44-consumers U8). The requirement is on the format's
  INFORMATION CONTENT: the format must expose enough per named pattern
  for a content hash to be taken at the right granularity. It does — a
  definition is a named, separately identified AST with its own assigned
  numbers — but *which* granularity is right is a codegen question with
  no consumer until multi-pattern units exist. **The trigger is [V-E]
  opening**, and the interface it will find is §4.4's own list, not a new
  one.
- **R-VE-5 / D39.2** (appended numbering) is now **D87 rule 7(i)**, and
  it is stronger than the first version claimed. That version said the
  rule "falls out of appending the DEFINE block" — true of PCRE2's
  positional numbering, and therefore true only of the textual control.
  Under D87 the composer ASSIGNS: a definition's groups are re-based
  above the caller's `ngroups`, local order and gaps preserved, the
  caller's numbers untouched. R-VE-5's actual requirement — "re-ordering
  an unrelated part of the file must not silently renumber an unrelated
  pattern's captures" — is met by the assignment being derived from
  reference structure, and D61 makes it a shipped promise rather than a
  property of where the block was written.
- **R-VE-4** (source-level vs link-level composition kept distinct) —
  the format expresses the **source-level** tier only, and expresses it
  as a PCRE2 subroutine call. Link-level composition
  ([M4-CALLOUTS]'s aligned ABI, non-regex predicates) has no spelling
  here and must not acquire one that looks the same; §7 Q4 records that
  as the open item it is.
- **R-VE-6 / D39's labelled references** (`"a:reg1"`, path composition
  `"c:a"`) — **the format DOES have the label, and D87 named it**: it is
  the delivering call's site name, and D39's "composed into a path for
  nested insertions" is §2.13's scope path exactly (`from.local`). A
  definition still appears **once** in the closure however many times it
  is called (§2.3.2's dedup); what a second call site adds is a second
  *delivery*, which is where the label was always needed. The first
  version said "the format needs no label", which was right about the
  closure and wrong about delivery.
- **R-VE-12** (a per-pattern encoding field) is an `encoding` line at
  block or config scope, more-specific-wins (§2.6) — D58 makes it a
  per-pattern scalar, so a block must be able to state it (r44-sem M16);
  the first version had only the `config` spelling.
- **R-VE-9** (CLI args and a manifest file must not need contradictory
  semantics): they do not — the CLI's single pattern is the
  `target rx` default, and `--target <prefix>` selects from a file.

### 4.5 pcrec-bench — regime, variant, outcome, objective, and the sidecar

The bench's inputs (its `docs/design/requirements.md` §3, §4.4, §4.5, §5)
were written against a **directory + sidecar** model that Frank's ruling
supersedes: the sidecar is dropped and its fields become lines beside the
pattern. The bench's *needs* are absorbed; its *shape* is not.

**MEASURED — the absorption, field by field, against the live sidecar**
(`/home/duxevents/pcrec-bench/bench/loglines/subbench.toml`, 11 patterns,
112 subjects, a 1,364-row `expectations.tsv`):

| `subbench.toml` field | becomes |
|---|---|
| `id`, `version` | `tag id=loglines` / `tag version=0.1` (file-level) |
| `objective_kind` | `tag objective=realworld` (file-level) |
| `objective`, `description` (prose) | **`description \|` block scalars** — file-level for the sub-bench, per block for a member (Frank's r44 ruling; §1.2). The first version sent this prose to `NOTES.md`; it is a FIELD, so a summarizing script can read a sub-bench's objective without a second file |
| `regimes = [...]` | `tag regime=search_short throughput` (file-level; bare labels and pairs both allowed, U1), refined per block (below) |
| `[[patterns]].name` | `name <ident>` (block-scoped) |
| `[[patterns]].file` | the `pattern` line itself — the `.rx` file disappears |
| `.feature_tier` | `features <list>` (a real directive) plus `tag tier=base` for the bench's own vocabulary |
| `.hazard_class`, `.size_class`, `.convention`, `.role` | `tag hazard=… size=… convention=… role=…` |
| **`.tags` (the free LIST — up to 6 bare labels per pattern)** | `tag` accepts **bare labels beside pairs on one line**, and repeated `tag` lines accumulate: `tag logs identifier control` then `tag regime=search_short` (r44-consumers U1; the first version's `tag-pair` required an `=` and dropped the list) |
| `[subjects].generator`, `.manifest`, **`.throughput_generator`, `.throughput_manifest`** | the directory convention — a generator beside its output, exactly as `tests/recursion/gen_corpus.py` already is. All four, not the two the first version listed (r44-consumers U5) |
| `[subjects].short_search_max_bytes` | `tag short-search-max-bytes=4096` |
| `[expectations].file` | `include "gen/expectations.rxt"` |
| `[expectations].default_method` | **TWO fields, not one** (r44-consumers U3): `oracle pcre2` names the ENGINE that checks, and `tag method=libpcre2-differential` names the VERIFICATION METHOD. R-BENCH-1's methods include non-oracle ones — "derived-law-plus-induction" is a real, already-used method (the K23 closed form) with no engine behind it — so folding method into the oracle enum would make those unspellable and would put a pcrec-shaped enum where AR-6 requires engine-neutrality. The first version conflated them |
| `[testees.pcre2].options` | `config pcre2` with `testee pcre2/10.46` + `option k=v` lines |
| `[testees.pcrec].options` | `config pcrec` with `pcrec --features all` |
| `patterns[].variant = null` | the **absence** of a `variant` sub-block |
| an `expectations.tsv` row | `m @file:"subjects/s-000.bin" as s-000 sha256 <hex64> 234 258` / `n @file:"…" as …` / `mc @file:"…" as … <n>` — the id and hash per §2.18, so the expectation key `(pattern, subject-id, regime)` survives the sidecar's death |
| **[B42]** the capability set's provenance record (their §4.1) | the `provenance` sub-block, field for field (§2.14) |
| **[B42]** `REQUIRES` tags + the closed vocabulary (their §5.1) | `tag requires=…` + `vocabulary requires …` (§2.15) |
| **[B42]** per-config capabilities (their §5.3) | `provides` lines in the testee's `config` (§2.16, Frank ratifies) |
| **[B42]** the second-convention expectation (their family 11) | `under <convention> <case-line>` (§2.17) |
| **[B42]** `variant_kind` / `objective_preserved` / `capture_map` | the variant sub-block's `kind` / `note` / `groups` (§2.23) |
| **[B42]** the testee-roster scoping hazard (D93) | `configs describe` (§2.20, Frank ratifies) |

**The four bench requirements that needed a decision, decided:**

1. **OUTCOME (§4.4), all twelve values accounted for** — the first
   version mapped 5 of 7 per-subject and 3 of 5 per-testee and was
   silent about the rest (r44-consumers U2). Per subject:
   `matched-as-expected` / `did-not-match-as-expected` /
   `wrong-span-or-captures` are what `m`/`n`/`g` already score;
   `gave-up` is `gu` (MEASURED live, 23 uses, §2.11); `crashed` /
   `timed-out` are the harness's own (exit ≥ 124 / ≥ 126, already
   distinguished by `run.sh`) and are never expectations.
   **`truncated-subject` is NOT REPRESENTABLE in this format, and that is
   deliberate**: it means the engine consumed fewer bytes than offered,
   which is a property of an ADAPTER's call, not of a pattern's answer —
   the bench records `consumed_length` where the API exposes it, and no
   `.rxt` line kind could produce that number for a foreign engine. It
   stays **bench-side**, and this note names the gap rather than leaving
   the reader to find it. Per testee: `did-not-compile` is `perr`;
   `unsupported-by-declaration` is the `variant` sub-block's
   `unsupported` attribute (§2.23 at W23) — one construct for both
   halves of the variant axis;
   `crashed` / `timed-out` are the harness's; **`compiled` is the
   ABSENCE of the other four**, a record-side default with nothing for
   the format to say. Two of twelve are bench-side by nature; ten map.
2. **VARIANT (§4.5), constraint 1** — "the results must be the same" —
   is **mechanical**: a `variant` is checked against the block's own
   expectations, and a difference invalidates the cell. Nothing new is
   needed; the variant simply supplies different pattern text for one
   testee's cell.
3. **VARIANT, constraint 2** — "the sub-bench's objective must be
   preserved" — is **a review obligation the format records and does not
   check**, and it must say so. The format's contribution is visibility
   (T-2/AR-5: a variant is beside the pattern or it is a fork), not
   verification. **REVISED at W23**: the reviewer's statement is the
   variant sub-block's own `note` attribute (§2.23), which is
   whitespace-capable where the first routing (`tag variant-note=…`)
   measurably was not ([B42] N-41); `tag-prose` now also exists for
   other descriptive keys.
4. **REGIME (§3)** — **REPLACED at W23 ([B42] N-48; the row's original
   text prescribed a mechanism MEASURED unusable for every bench
   pattern id, and §2.22 carries the repair).** Regime stays a property
   of the SUBJECT SET, not of a case, and there is still no case scope
   (Frank's ruling 4). A sub-bench writes the canonical pattern once as
   a `name`d definition — under its own hyphenated id, unmapped — and
   one block per (pattern, regime), each
   `pattern (?&<derived-identifier>)` with its own
   `tag regime=search_short` and its own subject set:
   `(?&cls_upto_1024)` binds to `name cls-upto-1024` through the
   composer's derived-identifier lookup (§2.22 — the `-`/`.` → `_` map
   `target =` already uses, with the same at-use collision refusal).
   The caveats that survive the repair, unchanged: the wrapper is free
   exactly while `expectations.tsv` carries no capture columns
   (MEASURED — none, all 1,364 rows), so when the bench adds capture
   checking (OD-B9) those blocks must carry the pattern text directly
   (§7 Q6's trigger); and a composed block's oracle is necessarily
   `pcre2` (§2.9), which for the bench changes nothing.

**What the bench must still own** (D78 — this is a durable interface
statement, not a ruling into their repo): the record and its keys, the
adapters, the reporter, and the decision of *when* to move a sub-bench
into the format. This note's contribution is that when they do, the
sidecar has somewhere to go.

### 4.6 [M4-SUBST] — the template slot only

R-SUBST-1 says the format must have somewhere for a replacement template
to live per named pattern, and R-SUBST-3 records the unpaneled prior art
(`subst_template_design.md` §8.1's `repl`/`s`/`sg`/`serr`). **This note
adds no template production**, per R-SUBST-1's own instruction ("Do not
design the template's internal syntax here") and D77.

What it does do is leave the slot obviously shaped: `repl` is a
block-scoped line in the prior art and would be a block-scoped line here,
`s`/`sg` are case lines exactly like `m` with a second quoted field, and
`serr` is `perr`'s shape one construct over. None of the four collides
with anything in §1.3 (MEASURED, §1.1: all four are 0 in the corpus).
The one thing this note asserts is that when they land they should be
**block-scoped and non-carrying**, like everything else in a pattern
block — which is what the prior art already chose independently.

---

## 5. The attack list, the tensions, the anti-requirements, the OD ledger

### 5.1 requirements.md §13 — the five claims it told the panel to attack

**Attack 1 — "the DIALECT answer is absence-of-counterexample from a note
that surveyed no generator that has tried."** The residual, in §13's own
words: *"a panel with more time could try to construct a HYPOTHETICAL
include/reference pattern and check whether it is even representable as
'existing files unchanged, new top-level constructs added'."*

**ANSWERED, and the premise has expired.** Two measurements:

1. **The corpus now exercises cross-references.** MEASURED: **143**
   blocks across 23 files carry a by-name subroutine reference, and 99
   lines use `(?(DEFINE)`. The `recursion` module landed *after* the
   requirements note was written; `(?&name)`, `(?P>name)`,
   `\g<name>`, `\g'name'` and `(?(DEFINE)…)` are all registry rows and
   all `built`. The generator that wrote them
   (`tests/recursion/gen_corpus.py`, 33 files) needed **no format
   extension** — because in-pattern composition rides `pattern`'s
   verbatim-to-end-of-line text, and only *cross-file* composition needs
   grammar. That is the actual mechanism behind R-GEN-1's finding, and it
   is why the finding generalises rather than merely not having been
   contradicted yet.
2. **The head is virgin territory.** MEASURED: across all 179 files there
   are **0** non-blank, non-comment lines before the first `pattern`
   line. So "new top-level constructs added above the first `pattern`
   line" is not merely compatible with the corpus — **it occupies space
   the corpus has never used, in any file.** R-COMPAT-1 holds
   *structurally*, not only by keyword absence (§1.1's second
   measurement).

The honest residual is narrower and is stated in §7 Q5: no *cross-file*
generator exists yet, so the include-closure accounting rules (§2.11) are
designed against a hypothetical population.

**Attack 2 — "R-GEN-1's n=5 is flat: none of the five exercised
cross-references, config sections or includes."** **PARTLY CONCEDED, and
n is now 6 with the flatness broken on one axis.** The sixth is the
`recursion` corpus above: cross-references, yes; config sections and
includes, still no. **The concession matters and is not argued away**:
`include` and `config` have no generator behind them anywhere in either
repo, which is exactly why they are W2/W3 and why §7 Q5 names the
measurement that would trigger them.

**Attack 3 — "does bench actually need engine-neutral group
identification, or does T-3 overstate it?"** (This, and attack 2's
concession, are the two residuals r44-consumers U11 asked be kept named
rather than argued away; they are.) **MEASURED, the tension is
not live today**: the live `expectations.tsv` columns are
`pattern subject regime expected start end nmatches method oracle` —
**no capture columns at all**, over all 1,364 rows. And T-3's premise is
weaker than stated for a second reason: the appended numbering is
**PCRE2's own** for the same text (§2.3 MEASURED), not a pcrec
convention, so an engine fed the same expanded pattern numbers it the
same way. The mechanism for the case where it *does* bite —
`variant … groups <name>=<n>` — exists in the grammar and is unexercised;
§7 Q6 names its trigger rather than pretending it is proven.

**Attack 4 — "check whether `--replace`'s CLI-only existence has already
created an informal convention a manifest template field would be awkward
to match."** **CHECKED DIRECTLY, and the premise is false: there is no
`--replace`.** MEASURED — `grep -rn replace cli/ lib/pcrec.h
docs/spec/cli.md` returns nothing, and `build/pcrec --help` names no
replace or subst flag. So R-SUBST-1 is the free, unconstrained field the
requirements note hoped it was, and §4.6 leaves it free.

**Attack 5 — "re-run the census rather than trust it verbatim if material
time has passed."** **RE-RUN, and independently REPRODUCED.** 2026-08-17:
54 files / 1,100 blocks / 9,977 expectation lines. 2026-08-29: **179 /
3,265 / 26,691** — 3.3× in twelve days — and r44-grammar, running its own
recognizer transcribed from `run.sh`'s 13 dispatch regexes rather than
from this note, "reproduced [them] to the digit" (G1), along with 0 head
lines, 0/32 keyword collisions and 636 `# pcre2-only` marks. **AR-1's
cost of getting compatibility wrong has tripled since AR-1 was written**,
which is an argument for the design's caution, not against it.

The 26,691 is a **three-way partition**, not one of the three numbers
`run.sh` prints (r44-grammar G2 corrected the first version's wording):
**22,125** subject cases (`m`/`n`/`ms`/`ns`/`gu`) + **4,182** group-slot
lines (`g`/`gp`) + **384** `perr` blocks. A `perr` block and a live `g`
line each record independently, so the harness's `cases passed` +
`cases failed` + `group cases pending-vm` is a different partition of
the same population.

**And two attacks the panel added.** r44-grammar tried four ambiguity
attacks on §1's grammar and **all four failed** (G5): a `pattern` line
inside a data block (the head-ender closes the block first); a
`#pattern` comment (column-1 `#` is tested before dispatch); a config
line whose value is a keyword (`rest-of-line` is never re-tokenized);
and a keyword colliding with a VALUE, which is impossible by
construction because dispatch is on the first token and values never
occupy it. **That run is what makes §2.10's `analysis freq <name>`
argument a demonstration rather than an assertion** (r44-consumers U11):
the ambiguity it avoids was checked, not asserted. r44-grammar also
confirmed (G6) that today's harness already hard-errors on any
non-comment line before the first `pattern`, so a head changes which NEW
files parse and never the meaning of the 179.

### 5.2 The tensions

| | resolution |
|---|---|
| **T-1** interface-vs-reference-only vs every-part-testable | **No new concept.** Target-ness and testability are **independent bits**: the harness compiles every block that has cases, as a **test** artifact, exactly as today; `target` is a file-level, build-only declaration that no pattern block carries. A reference-only definition with cases is therefore fully testable and ships nothing. No test-only surface is invented, so AR-2's no-dispatch rule is not even reached |
| **T-2** canonical pattern vs declared per-library tweak | `variant` (a sub-block at W23, §2.23) is block-scoped, sits **beside** the pattern, and is checked against **the block's own expectations**. Structurally it cannot become a second pattern: a variant has no `name`, so it cannot be referenced, cannot be a target, and cannot be composed into anything. Constraint 1 is mechanical; constraint 2 is a recorded review obligation the format does not pretend to check (§4.5) |
| **T-3** appended numbering vs engine-neutral expectations | see Attack 3. Not live (MEASURED: the bench's 1,364 expectation rows carry no capture column). **D87 changes the answer's basis, not the answer**: the numbering is no longer "PCRE2's own by position" but pcrec's own by ASSIGNMENT, which makes T-3's worry *more* pointed on its face — except that the assignment rule is stated, printable (`--emit-composed`) and stable, where a positional accident was neither. Group correspondence for a foreign engine stays engine-neutral and by NAME (`groups <name>=<n>`); a bench expectation still adjudicates on spans and counts, never on a pcrec slot number (AR-6) |
| **T-4** non-carrying block state vs cascading options | **Two different constructs, so neither has to become the other.** Block reset is the default and is untouched; the cascade exists only inside `config … from`. MEASURED: `config` occurs 0 times in the corpus, so no existing file opts in |
| **T-5** byte-exact subjects by reference | §2.8: bytes are the subject, no decoding, NUL-safe, local paths only. It forces a **driver-protocol change** (H6/S5) rather than being free, and this note says so rather than assuming `argv` will carry a megabyte with a NUL in it |
| **T-6** per-file accounting vs includes | §2.11's three rules: closure is the unit, entry-set subtraction with **both counts reported**, cells counted. Plus a fourth failure taxonomy (resolution) that is *reported* separately but *scored* as a compile failure, which is what preserves the 384 `perr` blocks |

### 5.2a Where to attack REVISION 3.3 (the panel's shortest path)

Revision 3's own "for the panel" list stands. **RE-AIMED AT 3.2 after
the r57 panel scored the 3.1 version**: of the four attacks below,
items 1 and 4 both HIT — and item 1 hit **in a place its own wording
pointed away from**, which is the correction worth carrying forward.
**RE-AIMED AGAIN AT 3.3**: round 2 scored item 5 three times (§0.8's
ROUND 2 block) and item 1 once more — R2-B's census-scope hole is a
narrowing sweep that swept a BRANCH instead of a GRAMMAR — and a sixth
item is added for the cardinality decision. Each is written as the
claim a critic should try to break rather than as a defence.

1. **THE NARROWING SWEEP.** The claim is that §1.6.1a's five-candidate
   census is CLOSED: no other construct legal on the shipped binary is
   refused by this revision.
   **RE-AIMED, and the re-aim is the finding.** Revision 3.1 wrote this
   attack and pointed it at *"the HEAD and the shipped implementations
   of its continuation (`parse_prose`, `parse_config`)"*. The panel
   found three more narrowings THERE (the prose-`#`, prose-ragged and
   tab cases) — so the aim was productive — **and it found a fifth
   somewhere the aim excluded by construction: §2.22's SEMANTICS, in
   the composer's name lookup, with no head line involved at all.** A
   sweep aimed at the grammar cannot find a narrowing in a binding
   rule. So the aim is now BOTH: re-probe the head continuation for a
   sixth, and — the newer and less-worked direction — **walk every
   §2 rule that says "refused" and ask what it accepted yesterday.**
   The method that worked in both places was a probe on the shipped
   binary, never a reading.
2. **§1.2.3's admission, in the other direction.** The claim is that
   block grouping is the ONLY place structure needs a keyword — now
   stated as TWO parameters rather than one (§1.2.1). A critic should
   try to find a THIRD: the candidates are `under`'s qualified line
   (does a reader need to know `under` to see where the case line
   starts?), `@file:`'s optional suffixes, and — new at 3.2 —
   **S3's extent rule**, which reads no keyword but does read a
   VALUE (`|`), so the question is whether a reader can recognise an
   opaque region without knowing which kinds may open one.
3. **§2.26 item 10, the provenance unification.** The claim is that
   two records were one record all along. The attack is a fact a
   `freq` block must state that a pattern block's provenance has no
   field for, or vice versa — in which case the union is a union and
   not a unification, and the per-parent required set is hiding a
   second record inside one production. **(r57 hunted this and it
   HELD, including the `analyzer` keep.)**
4. **§2.25's scope, and it is the attack that drew the most blood.**
   The claim is that the schema is exactly as big as W23's productions
   need. **In 3.1 that claim was FALSE in the second direction this
   item names** — four W23 refusal rules that the five kinds could not
   express, one of them needing precisely the kind §2.25.4 deferred —
   so the section is now eight kinds plus one declared parser-code
   exception. Attack it again from both ends: a kind whose only
   customer is speculative (it fails the membership rule), or a
   refusal rule still living in control flow WITHOUT being named as
   one. The second is the dangerous outcome and the reason is
   unchanged: a partial declaration presenting itself as complete
   makes `--list-schema` a confident wrong answer.
5. **NEW AT 3.2 — S3, and the structure layer's second parameter.
   RE-AIMED AT 3.3, and this item HIT three times in round 2.**
   The claim is that four line classes, three devices and two
   parameters recover the file's tree, and that S3's extent rule
   matches what the shipped parser does. In 3.2 BOTH halves were
   falsifiable and were falsified: the extent rule read *"first line
   at indent ≤ the opener's, or the first blank"* and (a) its TRIGGER
   was unparameterized, so `pattern |` opened a region; (b) the
   COMMENT class had no stated effect, so a generic reader carried
   structure across a column-1 `#` where every shipped leg terminates;
   (c) "the first BLANK line" meant whitespace-only lines too, which
   deletes the format's paragraph break. All three were found by probe
   against `--list-source`, which is exactly the method this item
   prescribes, so **the attack is unchanged and should be run again**:
   find a file whose tree a generic S0-S3 reader recovers differently
   from `--list-source`, or find a THIRD parameter the structure layer
   secretly reads. The known-weak points, restated for 3.3: the
   structure layer now reads THREE columns (`opens_group`, and
   `value`+`children` as a pair) and `cardinality` is still not one of
   them, so the claim that S2's grouping needs no cardinality
   information (a group ends at the next opener, never at a count)
   remains unprobed against a file with a malformed group; and S3's
   extent rule is stated in its GENERAL form (indent ≤ the opener's)
   while leg A implements "indented at all", the two coinciding only
   because no prose-valued kind exists at a nonzero indent today.

6. **NEW AT 3.3 — the CARDINALITY decision, §2.25.2.** The claim is
   that seven settings kinds are `at-most-one` and `budget` is
   `accumulate` over `{steps, frames}`, and that the population of
   every refusal this creates is ZERO in both repos. That is a
   counting claim over a moving corpus and it is the cheapest thing in
   this revision to falsify: re-run the duplicate-line census and look
   for a block that repeats a settings line on purpose. **One was
   found already** — `tests/harness/giveup.rxt:19-23`, which is why
   `budget` is not a scalar kind — so the honest question is whether
   there is a SECOND, in a shape the census's per-block grouping
   misses (a `config` body reached through `from`-composition, say,
   where two configs each contribute a different `encoding` and the
   duplicate exists only after resolution). **That last shape is
   deliberately out of the rule's scope** — §2.25's cardinality is a
   property of one SCOPE's lines AS WRITTEN, never of a resolved
   cascade (§1.8's as-written discipline) — and a critic who can show
   the two cannot be kept apart has found something real.

### 5.3 The anti-requirements

| | how it is honoured |
|---|---|
| **AR-1** no re-verification of the corpus | INV-COMPAT (§1.1) with three independent checks, six sabotage rows and asserted denominators. MEASURED: 0 keyword collisions over 32 candidates, 0 head lines in 179 files, and no file reference to bind in any non-`perr` block. r44-grammar reproduced all three with its own recognizer (G1, G5, G6). **REVISION 3.1 re-measured all of it at the current 210-file corpus** — 0 collisions over 52 candidates, 0 indented lines — and corrected the denominators, which had gone stale with [M5.0]'s corpora (§0.7, §1.1). The re-factoring itself is what AR-1 turns on and §1.6.1 is the argument that it is additive |
| **AR-2** no dispatch in the common case | a pattern with no file references binds nothing, so the AST is the one the compiler builds today. §2.7's default: one unnamed block, no head → `target rx`, byte-for-byte today's output. The format cannot add dispatch because in that case it adds nothing. **D87 strengthens this**: an UNDECLARED call stays capture-transparent at zero cost (rule 5), so even a composing file pays only for the deliveries it declares |
| **AR-3** declared inapplicability ≠ failure ≠ silent pass | four separate, counted, printed states: `oracle none <reason>`, `variant … unsupported <reason>`, `gp`'s pending-vm bucket, and the resolution-failure taxonomy — each reported on its own line in the summary (§2.11) |
| **AR-4** must not make D27 harder | the head is **bounded and above the first `pattern` line**, so a blinded author reading a block looks in exactly one other place; a fragment **may not declare file scope**, so a spliced block's meaning never depends on which file spliced it; and the one genuine cross-block dependency — a name a pattern references — is visible at the top of the file by construction |
| **AR-5** no silent semantic fork | T-2 |
| **AR-6** no pcrec-specific data in bench expectations | expectations stay spans and counts (`m`/`n`/`ms`/`ns`/`mc`); the verification method is a declared `oracle`, not an engine; group correspondence, when needed, is **by name** |
| **AR-7** no structural violation via the format | a file declaring no targets emits nothing; a file declaring one target emits what `pcrec 'pattern'` emits; nothing routes a single pattern through multi-pattern machinery. The generator/finder split is untouched because the format never names a finder |

### 5.4 The open-decision ledger

| | disposition |
|---|---|
| **OD-1** where per-engine options live, and composition across includes | **file and block scope only** (Frank's ruling 4). Composition is the **per-option-kind** table in §2.6 — `features` unions, everything else is more-specific-wins, size caps are raise-only at every scope. The cascade Frank asked for lives in `config … from`, ordered, last wins; `include` stays pure splice, because making an include's *position* change a later block's meaning is the cross-file context AR-4 forbids |
| **OD-2** the declared-tweak mechanism | the `variant` sub-block — `text`/`kind`/`groups`/`note`, or `unsupported <reason>` — block-scoped (§4.5, reshaped at W23 §2.23) |
| **OD-6** the data block's spelling and namespace | **inline values, own namespace** (§2.10). This is OD-6, named — the first version presented it as departure "D-e" without citing the open decision it disposes of (r44-consumers U10) |
| **OD-3** config syntax unifying testees and build variants | **one block kind.** A build variant is a `config` with `pcrec` lines; a bench testee is a `config` with `testee` + `option` lines. R-BENCH-9's "one concept, two uses" is literal here — the same `config` grammar, differing only in which of its line kinds appear |
| **OD-4** interface/reference-only marking; a test-only surface | **no marking, no surface** — T-1 |
| **OD-5** PCRE2 desugar vs own spelling | **PCRE2's `(?&name)` — and, after D87, a deliberate, minimal DIALECT around it.** The spelling stays PCRE2's; what is pcrec's own is the number ASSIGNMENT (rule 7), the scope prefix and the delivering declaration (§1.5), each measured to be a spelling PCRE2 refuses. OD-5's two feared consequences are corrected: subroutine calls are **backtrackable**, not atomic, on 10.46 (§2.3.5), and the numbering is now an assigned property, not a positional accident. The item's own tag — "measured, never read from docs" — is honoured twice over: §2.3.3's semantics and §1.5's free-ness are both runs, on both oracles |


---

## 6. Worked files, in the final grammar

Every example below parses under §1.3 and §1.5 by the hand-trace beside
it, and every composed pattern in §6.1 was **compiled by `build/pcrec`
and run through `tests/harness/driver.c`** — the cells are measured, not
asserted.

### 6.0 The PIECE RULE — five ways a definition can depend on its site

A library definition is a **piece**, and a piece can be written so that
its meaning depends on where it is called. r44-sem enumerated the class
and the first version had only one member of it. **There are five**, and
they do not all have the same fix:

| # | class | witness | fate |
|---|---|---|---|
| (i) | **absolute subject tests** — `^`, `$`, `\A`, `\z`, `\Z`, `\G` | the position paper's own §3a: `email` = `^(?&local)@(?&domain)$` called from `From: (?&email)` → **nomatch**. Controls: `x(?&e)…(?<e>a$)` on `"xa"` matches, `x(?&e)y…` on `"xay"` does not | **REFUSED at the [LIB] store by a scan** — a piece carries no subject anchor |
| (ii) | **EDGE assertions reading the caller's text** — `\b`, `\B`, a lookbehind `(?<!…)` | `(?<e>\ba)` is nomatch on `xa` and match on `-a`: the callee reads the byte before the call site | **DOCUMENTED, not refused.** A piece may legitimately be edge-sensitive — "a word-boundary-anchored token" is a piece somebody means to write. The store records it; the caller sees it in the `description` |
| (iii) | **match-span writers** — `\K` | `^x(?&g)$` with `g` = `a\Kb` on `xab` reports **(2,3)**: `\K` ESCAPES the callee and rewrites the CALLER's reported start | **REFUSED by the store scan.** A piece may not move its caller's span |
| (iv) | **width-constrained CALL SITES** — a lookbehind caller | a definition legal everywhere else is a compile error from inside a lookbehind (libpcre2 err 125, "unbounded") | **A SITE RULE, not an authoring rule** — it is the caller's lookbehind that constrains, so it cannot be checked at the store; it is a refusal at the call site with the reason |
| (v) | **absolute numeric references** — `\1`, `\g{1}`, `(?1)`, `(?(1)…)` | §2.3.3 M1: `(\d)\1` composed naively inverts | **DROPPED from the refusal list by D87.** Rule 7(i) RE-BASES them, measured to restore the piece's own meaning. The manager's recommendation to the panel was to refuse; Frank ruled the mechanism instead, and the rule is now that a piece's absolute references are LOCAL to the piece wherever it lands |

**So the [LIB] store's entry scan covers (i) and (iii) mechanically** —
both are a lexical property of the definition's own text, checkable
without knowing any caller. (ii) is documented rather than refused
because refusing it would refuse patterns people mean. (iv) belongs to
the call site. (v) needs nothing at all any more, and that is the
clearest single consequence of D87 for [LIB]: the refusal list is
**two** members long, not five, and the two that remain are the ones a
piece has no business doing.

**Whole-string matching is not what the anchors are for.** A caller who
wants the whole subject writes their own `^…$`, or better uses the
artifact's own anchored entry `<prefix>_match`
(`docs/spec/match_api.md` §3.2), which exists precisely so a pattern
need not be re-spelled to be matched whole.

**The format cannot check (i)-(iii) statically for an arbitrary
pattern** — a `$` inside a callee is legal when the callee is the whole
target — so what it does is make the failure loud in the ordinary way:
the composing block's own `m` case goes red. The store scan is the
place the rule becomes mechanical, and that is [LIB]'s to build.

### 6.1 A library and a user of it ([LIB], U4/U5, W1)

`lib/rfc5322.rxt` — definitions are pieces, no anchors, no targets:

```
# Operational note: regenerate the tests with tools/gen_rfc5322.py.
description |
  RFC 5322 address pieces. Definitions only; this file declares no
  targets, so `pcrec --source` on it emits nothing.
  Every definition here is a PIECE: no subject anchors (§6.0 (i)).
tag objective=subroutines

pattern [A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*
name local
description The dot-atom local part, unquoted forms only.
m "john.doe" 0 8
n ".john"

pattern (?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z]{2,}
name domain
description A dotted host name with a 2+ letter TLD. No IP literals.
m "example.com" 0 11

pattern (?&local)@(?&domain)
name email
description An addr-spec: local part, @, domain. Unanchored.
m "john.doe@example.com" 0 20
n "john.doe@"
```

`mail.rxt`, a user of it:

```
lib "lib/rfc5322.rxt"
target mail = from_line
  description The From:-line matcher the mail daemon links.

pattern From: (?&from=email)
name from_line
m "From: a@b.co" 0 12
```

**Hand-trace.** *`lib/rfc5322.rxt`*: head = a `description` block scalar
(three indented lines, ending at the non-indented `tag`) and one `tag`;
body = three blocks, each with its own one-line `description`. Blocks 1
and 2 declare no group and reference nothing, so composition binds
nothing and they compile exactly as written. Block 3 references `local`
and `domain`, both resolved in this file; the closure is those two, each
bound with its groups re-based above `email`'s own `ngroups` (which is
0). Being composed, the block's oracle is necessarily `pcre2` (H4). No
`target` line and more than one block, so **`pcrec --source
lib/rfc5322.rxt` emits nothing** — a library ships nothing by itself
(Frank §6.4).

*`mail.rxt`*: head = `lib`, then `target` with an indented `description`
attached to it (§1.2). `target mail = from_line` forward-references a
definition in the body — normal: the head precedes the body and
resolution is a whole-file pass. The block writes a **delivering call**,
`(?&from=email)` (§1.5 B3), so the caller gets
`struct { rx_span local, domain; } from;` and can read `r.from.domain`;
an ordinary `(?&email)` would have been capture-transparent and free.
`email` is not defined in this file, so it resolves in the `lib` chain;
its own references are then resolved in *rfc5322's* scope — the caller
could not satisfy them even by declaring `local` itself (§2.3.2).
**The library's own five cases do not run here.** `pcrec --source
mail.rxt -o mail.c` emits one artifact under prefix `mail`, with
`rx_info.name == "from_line"`, `ngroups` **0** (the primary declares no
group of its own — D61) and the three delivered slots above it.

**MEASURED — all six cells**, `build/pcrec -p rx --features all` +
`driver.c`:

| cell | expanded pattern (abbreviated) | subject | result |
|---|---|---|---|
| `local` m | `[A-Za-z0-9!#$…]+(?:\.[…]+)*` | `john.doe` | `match 0 8`, `RX_NCAPS 1` |
| `domain` m | `(?:[A-Za-z0-9](?:…)?\.)+[A-Za-z]{2,}` | `example.com` | `match 0 11`, `RX_NCAPS 1` |
| `email` m | `(?&local)@(?&domain)(?(DEFINE)…)` | `john.doe@example.com` | `match 0 20`, `RX_NCAPS 3` |
| `email` n | (same) | `john.doe@` | `nomatch` |
| `from_line` m | `From: (?&email)(?(DEFINE)(?<email>…)(?<local>…)(?<domain>…))` | `From: a@b.co` | `match 0 12`, `RX_NCAPS 4` |
| (a user's anchored form) | `^(?&email)$(?(DEFINE)…)` | `a@b.co` | `match 0 6`, `RX_NCAPS 4` |

Two things to read off the last two rows. `RX_NCAPS` is 1 + three
definition slots — but under D87/D61 those three sit **above `ngroups`**,
which stays at the primary's own count, so the numbers a caller indexes
by do not move (§2.3.1 rule (i)). And these cells are measured through
the TEXTUAL control (`(?(DEFINE)…)` appended), which is legitimate here
because this file is inside the control's valid population: no absolute
numeric reference anywhere in it, and no name collision between caller
and closure (§2.3.4). That is the control doing its job — agreeing with
the composer on the population where both are defined.

### 6.2 A bench sub-bench as one file (U7/U8, W2+W3)

The live `bench/loglines/` sub-bench, in the format. The **objective is
a field now**, not a `NOTES.md` paragraph (Frank's r44 ruling); the
generator still stays beside its output; the directory stays a directory
and no tool reads it as a schema.

**REPAIRED at revision 3** ([B42]): the file now carries the six W23
mechanisms its first version could not — `configs describe` (without
which its own `config pcrec` block would PIN the bench's testee matrix
under D93, roadblock #6), `vocabulary`, `provides`, subject ids + hashes,
a `provenance` sub-block, the variant sub-block, and an `under` case.

```
# Operational: regenerate subjects with gen_subjects.py before editing.
description |
  Log-line search over mostly-FAILING text: what an engine pays to
  establish that a chunk of log lines does NOT contain the shape an
  operator is grepping for, at the sizes a log shipper hands a matcher
  (256 B - 4 KB) and across a size sweep to 1 MB.
tag id=loglines version=0.2 objective=realworld
tag short-search-max-bytes=4096
oracle pcre2/10.46
tag method=libpcre2-differential
configs describe

vocabulary hazard   none exponential-backtracking large-count wide-alternation
vocabulary size     tiny small medium large
vocabulary role     member floor
vocabulary kind     syntax-only restructured
vocabulary convention perl-leftmost-first posix-leftmost-longest
vocabulary requires backrefs lookaround lookbehind-variable atomic-possessive
  recursion conditionals k-reset control-verbs unicode-properties
  named-groups free-spacing callouts span-reporting non-utf8-subject
  captures true-end-anchor

config pcrec
  pcrec --features all
config pcre2
  testee pcre2/10.46
  provides backrefs lookaround atomic-possessive recursion conditionals
  provides k-reset control-verbs unicode-properties named-groups
  provides free-spacing callouts span-reporting captures true-end-anchor
config re2
  testee re2/2024-07-02
  provides unicode-properties named-groups captures
use pcrec, pcre2, re2

include "gen/cases_search_short.rxt"    # 11 patterns x 112 subjects, generated
include "gen/cases_throughput.rxt"      # the 16 KB - 1 MB sweep
```

and a fragment `gen/cases_search_short.rxt`, machine-written — **blocks
only, no head** (§2.5):

```
pattern \d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d{1,6})?(?:Z|[+-]\d{2}:?\d{2})?
name iso-ts
description ISO-8601 timestamp with optional fraction and zone.
tag logs timestamp iso8601
tag regime=search_short tier=base hazard=none size=medium
tag convention=perl-leftmost-first role=member
provenance
  source    authored
  license   CC0-1.0
  retrieved 2026-09-12
  fidelity  inspired
  adaptation |
    written from the ISO-8601 grammar's own production list; no source
    regex was consulted.
variant re2
  kind restructured
  text \d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}([.,]\d{1,6})?(Z|[+-]\d{2}:?\d{2})?
  note |
    the non-capturing groups opened: RE2 prices them identically, and
    the objective (a class-heavy scan) is untouched.
m @file:"../subjects/s-000.bin" as s-000 sha256 3f2a09c1d47e58b6a2f0e9d1c8b7a6f5e4d3c2b1a0918273645546372819aabb 234 258
n @file:"../subjects/s-001.bin" as s-001 sha256 91c04e7f2a3b5c6d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d
… 110 more

pattern a|ab
name sem-alt-order
description The leftmost-first / leftmost-longest separator case.
tag semantics control
tag regime=search_short role=member hazard=none size=tiny
tag convention=perl-leftmost-first
m "ab" 0 1
under posix-leftmost-longest m "ab" 0 2

pattern :
name floor
description The floor control: one literal byte, structural in every log format here.
tag floor control one-literal
tag regime=search_short role=floor hazard=none size=tiny
m @file:"../subjects/s-000.bin" as s-000 24 25
… 111 more
```

**Hand-trace, the W23 half only** (the W1 mechanics are the previous
revision's and unchanged). `configs describe` makes every `config`
block DATA: `pcrec --source loglines.rxt` builds nothing from them, the
harness runs each block in ONE cell and prints
`configs: descriptive (3 declared, 0 applied)`, and the bench's runner
reads the roster off `--list-source` and applies it through its own
adapters — whose command lines therefore always win, closing the D93
collision by construction (§2.20). The `vocabulary` lines close six tag
keys (a typo in `hazard=` is now a refusal naming the set; the
`requires` line wraps by head continuation); the two `provides` stanzas
are checked against `vocabulary requires` and are what the bench's
pre-compile policy reads — `re2`'s short list is why a
`tag requires=backrefs` pattern would produce
`unsupported-by-declaration` there, decided before any compile (§2.16).
`iso-ts` keeps its HYPHENATED id (no name map anywhere — §2.22); its
`provenance` sub-block is the charter's requirement (1) with
`authored`'s no-url rule live; its `variant re2` sub-block carries
`kind` + `text` + the reviewer's `note` (§2.23). `sem-alt-order` is
family 11's separator case: one unqualified expectation under the
canonical convention, one `under` line carrying the second correct
answer (§2.17) — pcrec's own harness counts the `under` line as a
labelled skip; the bench scores it against its
`posix-leftmost-longest`-tagged testees. Subject references carry
`as`/`sha256` (§2.18), so every report row keys on `(pattern, s-000)`
and a regenerated tree that drifts is refused at read time naming both
digests.

**Note what this file still does NOT do: it composes nothing.** No
block references a definition, so §2.3's machinery never runs. A bench
sub-bench is a flat corpus with a rich head. (A set that DOES use the
per-regime wrapper writes `pattern (?&iso_ts)` and binds through the
derived-identifier lookup — §4.5 item 4 as repaired, §2.22.)

**What this replaces**: `subbench.toml` (183 lines),
`expectations.tsv` (1,364 rows), eleven `patterns/*.rx` files AND the
sidecar's provenance/capability/variant fields — three file kinds and
two grammars become one file kind and one grammar, with a case's
identity being `(pattern, subject-id)` plus its `file:line` (§2.18),
never a key joined across files.

### 6.3 Two build configurations from one source ([V-E], U6, W1)

```
config baseline
  pcrec --no-captures
config avx2 from baseline
  pcrec --simd=avx2
config big from baseline
  pcrec --max-emit-bytes=4000000

target log_base = level_filter with baseline
target log_avx2 = level_filter with avx2
target log_big  = level_filter with big

pattern (?i)error|warn|fatal
name level_filter
m "an ERROR here" 3 8
```

**Hand-trace.** Head: three `config` blocks (`avx2` and `big` each
inherit `baseline`'s `--no-captures` through `from`, then add their own),
three `target` lines naming one definition three times. Body: one block.
`pcrec --source log.rxt` emits **three** `.c` files;
`--target log_avx2` emits one. All three carry
`rx_info.name == "level_filter"` and three distinct prefixes (§2.7).
`big` is the D84 addendum-3 case, and it is exactly the shape
`docs/spec/limits.md` already tells callers to use. The harness runs the
block's one case in each of the three targets' configs, and identity
between them is a free control.

### 6.4 An exemplar-analysis findings file (`freq`, W2)

Written by the analyzer, committed; the exemplar is not (D83, Frank).

```
# exemplars/loglines.freq.rxt — WRITTEN BY THE ANALYZER. Do not hand-edit.
freq loglines
  description Byte histogram of one month of production nginx access logs.
  question which byte is rarest in this exemplar
  reader OPT-A rarest-byte candidate-scan selection
  analyzer scripts/exemplar_freq.py 0.1
  provenance
    source    prod-web-01 nginx access log, 2026-08 (not committed)
    retrieved 2026-08-29
    bytes     4187336614
    sha256    9f2c0b1e7a4d38c5be6109f7d2a4c83b5e0d7f61a9c2b48e35d7061fa8c3b92d
  row 0    412 0 0 0 0 0 0 0 0 118344 4192011 0 0 91 0 0
  row 16   0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
  row 32   681240119 3341 24 88190 4412 33 991 62204 41180 41180 8823 6 2201947 774310 2119883 1884420
  … 13 more rows
```

and a user of it:

```
lib <rfc5322>
include "exemplars/loglines.freq.rxt"

config prod
  analysis freq loglines
  pcrec --features all

target email_prod = email with prod
```

**Hand-trace.** The findings file's head is one data block, its lines
attached under it by S1 (§1.2.1) — **and the `provenance` record is
attached one level deeper, which is the same rule applied twice and no
new mechanism at all**; that two-level nesting is what the revision-3.1
unification buys (§2.10, §2.26 item 10), and it is the shape a reader
already knows from a pattern block's own `provenance`. The file's body
is empty — a legal file with zero pattern blocks, which the grammar
admits
(`body = { pattern-block }`, possibly none) and which is the point: this
is data, not tests. `question` and `reader` are required, which is
§2.10's membership rule made structural; `description` is the field a
summarizing script reads. The user's file `lib`s a library by its
**store** spelling (`<rfc5322>` — searched on the library path, never
relative), `include`s the findings file by its **local** spelling,
selects the table in a config, and builds one target against it. **The
same pattern built against a second exemplar is a second `target` line,
not a second file** — which is what made the target-as-declaration shape
right.

**The `row` arity is a SEMANTIC check, not a grammatical one**
(r44-grammar G4). The production admits any `row` of one offset plus one
or more counts; that 16 rows of 16 counts make exactly 256, that the
offsets are 0, 16, … 240, and that every count is non-negative are
checked **when the data block is parsed** (H9), with the refusal naming
the row. The first version's prose read as if the grammar guaranteed
it — a grammar cannot count to 256.

### 6.5 A today's-`.rxt` file, unchanged (U1, all waves)

Verbatim from `docs/spec/rxt_format.md`'s own example, which is what
one of the 179 files looks like:

```
# Literal matching and basic quantifiers.

pattern abc
m "abc" 0 3
m "xxabcxx" 2 5
n "ab"

pattern a+
m "aaa" 0 3
n "b"

# An invalid pattern: unbalanced group.
pattern (bad
perr

pattern colou?r
m "The color and colour are spelled differently." 4 9
m "colour" 0 6
m "byte \x41 then newline\n" 5 6
```

**Hand-trace.** Head: **empty** — the file's first non-comment,
non-blank line is a `pattern` line, true of all 179 corpus files
(MEASURED §5.1, independently reproduced by r44-grammar G1). Body: four
blocks. No block declares a group or references a definition, so
composition binds nothing and the compiler input is byte-for-byte
today's. No `target` line and more than one block, so the file builds
nothing. The `perr` block is evaluated in exactly one cell (§2.6).
`\x41` and `\n` decode as they do today. Every line is unindented, so
the head/continuation rule (§1.2) never engages. **Nothing in this file
is new, nothing in it means anything different, and nothing in it needed
to change.**

---

## 7. Open questions for Frank

### 7.0 What is no longer open

Six of the first version's questions and residuals are settled, and this
list is here so nobody re-answers them:

- **Q1 (where prose lives) is ANSWERED — the other way.** Frank, r44
  15:0x: *"we may want to summarize via script what a library or other
  rxt file has: therefore a description may be helpful outside of
  comments, which should be operational."* `description` is a machine-
  readable FIELD at file, definition, target and data-block level, with a
  YAML-style `|` block scalar for multi-line prose (15:1x). The note's
  recommendation — prose in `#` comments and `NOTES.md` — is **overturned**
  and gone from §1.2, §4.5 and §6.
- **Who composes, the numbering, and the collision rule** are D87 rules
  1, 2 and 7. §2.3 is rewritten around them.
- **"May a scope prefix reference CALLED groups?"** — which the first
  version could not answer — is settled by D87 rule 5: **yes, exactly
  where the call is declared as DELIVERING** (§1.5 B3, §2.13). A
  delivering call creates the scope; an undeclared one has no groups to
  name and stays capture-transparent.
- **The three spellings** (numbered group, scope prefix, delivering
  declaration) and the `.rxt`-level syntax calls are the manager's under
  Frank's 14:5x ruling, and are settled in §1.5 and §1.3 rather than
  asked here. One of them was settled by MEASUREMENT against the brief's
  own leading candidate — see the note in §7.1.
- **`analysis freq <name>`** (OD-6) is the manager's, accepted at the
  panel, and r44-grammar G5's run demonstrated the ambiguity it avoids.

### 7.1 One thing the manager should see before settling B3

The leading shape offered for the delivering-call declaration,
`(?<from>&email)`, is **DISQUALIFIED by measurement**: it is an ordinary
legal PCRE2 pattern today — a named group `from` whose body is the
literal `&email` — and it matches the subject `&email` at (0,6) on
libpcre2 10.46 AND on pcrec (§1.5). Adopting it would change the meaning
of patterns that already exist, which is the one constraint every
candidate must satisfy. §1.5 recommends `(?&from=email)` /
`(?&=email)` instead, with all candidates' free-ness measured.

### 7.2 The questions that remain

**Q2 — `features` composes by UNION, with `features only` for a
deliberate narrowing.** RECOMMENDED, and r44-sem could not refute the
union rationale (8 probes: every difference was refuse→compile, never
match→different-match). r44's counter-case (U12): more-specific-wins
would let a block test under FEWER modules than the file intends.
`features only` is the answer — the narrowing exists and is a thing an
author wrote (M14). The `perr` one-cell carve-out stands and is what
protects **384** blocks.

**Q3 — the PIECE RULE is a [LIB] store scan, and it is now a
five-member class with two mechanical members.** r44-sem found the first
version had one member of five (M6, §6.0). After D87 the store scan
refuses exactly two — subject anchors and `\K` — because absolute
numeric references are now RE-BASED rather than refused, and edge
assertions (`\b`, a lookbehind) are a legitimate thing to write and are
DOCUMENTED. r44's counter-case (U12): a static top-level `^`/`$` check
catches the bug once. Agreed, and that is what the scan is.

**Q4 — the link-level tier still has no spelling, and should not
acquire one by accident.** RECOMMENDED: confirm that [M4-CALLOUTS]'s
aligned-ABI tier gets its own construct and that `(?&name)` never means
"link to a separately compiled part". r44's counter-case (U12): reserve
a distinct sigil NOW rather than later. **This note declines to reserve
one** — D77, no consumer — but records that §1.5's constraint is what
makes reservation unnecessary: any future construct must also be a
spelling PCRE2 refuses, and that space is large.

**Q5 — W2's include-closure accounting is designed against a population
that does not exist.** No cross-file generator exists in either repo.
RECOMMENDED: ship W2 when the bench's 1,364-row expectation fragment
needs it, and treat that set as the validating measurement. r44's
counter-case (U12): build §2.11 now, because the bench row is already
blocked on it. **Both are right about different things** — the bench is
blocked on the FORMAT, not on the accounting rules, so W1's landing
unblocks the authoring and W2's landing carries the accounting with its
first real population.

**Q6 — a bench sub-bench references its canonical pattern per regime
rather than repeating it.** RECOMMENDED: reference now — MEASURED,
`expectations.tsv` has no capture columns at all, so the wrapper is
span-identical — and revisit when bench adds capture checking (its
OD-B9). r44's counter-case (U12): writing the pattern text directly
avoids a corpus-wide rewrite later. The trigger is named either way;
the choice is whether to pay now or on a known signal.

**Q7 — NEW, and it is the residual D87 creates: the oracle control no
longer covers the whole population.** Under the textual model the
control was total. Under D87 it is valid only where the append form
means what the composer means — **no absolute numeric reference in any
body, no name collision between caller and closure** (§2.3.4) — and
those are exactly the two shapes D87 added mechanism for. So the format
gains two capabilities whose answers no independent oracle checks.
**RECOMMENDED: accept it for W1 and name the trigger rather than build
a second oracle now.** Three reasons: the shapes are individually
verifiable by hand today (§2.3.3's M1 and M2 cells are that, on both
oracles); `--emit-composed`'s round trip is a real, if weaker, control
(pcrec must agree with itself across a serialization boundary); and a
second oracle means a second composer, which is the drift hazard
learnings §3 exists to name. **The trigger to revisit: the first
library entry that legitimately needs an absolute reference or a
colliding name.** If that never happens, the uncovered population is
empty and the residual costs nothing — which is itself worth measuring
at the [LIB] store's first ten entries.

### 7.3 The W23 questions for Frank (revision 3)

Syntax is settled under the 14:5x delegation; these are the genuine
semantics/scope items, each presented ready-to-ratify:

**W23-F1 — `configs describe` (§2.20).** This touches D93 (the
composed-config-beats-command-line rule), which is why it is Frank's:
the head declaration makes a file's configs DESCRIPTIVE — never
composed into any build, `target … with` refused, `use` inert and
counted, default `build` = today's semantics unchanged. The mechanism
closes the bench's roadblock #6 by construction and adds a contract
sentence (a target-less, config-less file parses and builds nothing,
PERMANENTLY — their N-43). Recommended: ratify as designed.

**W23-F2 — `provides` (revision 3's `capable`) lives IN the format (§2.16).** The manager
recommends IN (a `config … testee` already carries engine knowledge;
the reason a pattern has no result for a testee belongs in the file a
reader has); fail-closed; the one reserved key name `requires`. The
alternative — bench-side capability files — is a partial return of the
hybrid the 2026-09-12 ruling removed, and §8's P-Q4 records why it was
considered and declined rather than defaulted. Recommended: ratify.

**W23-F3 — the `mc` counting rule's home (§2.21). RESOLVED at revision
3.1; NOT a question for Frank.** The manager pre-ruled the bench's
formula; measurement found it double-counts an empty match found beyond
the scan position, so the design states `match_api.md` §3.1's shipped
protocol instead. **The manager has ACCEPTED the deviation** — it is
the only rule pcrec's own entry points can implement, the bench's note
pre-authorized exactly this answer (*"the harness's rule, whatever it
is — say that"*), and no shipped surface changes. It stays listed here
because the outbox message owes the bench their one adapter edit
(empty-match advance from the reported START, not `max`), which §9's E5
group carries. Nothing is owed to Frank.

**W23-F4 — the derived-identifier repair REMOVES the ability to declare
a deliberately NON-CALLABLE definition (§2.22). NEW at revision 3.2,
from the r57 consumer lens (C-M2); the manager recommends ACCEPT.**

*What is being lost.* Today a definition named with a `-` or `.` is
**buildable as a target and not callable from a pattern**, because
`(?&some-id)` goes through PCRE2's own group-name grammar. Under
§2.22's derived-identifier binding, `(?&some_id)` reaches it. The
shipped tree does not record that boundary as an accident — it records
it as a FEATURE, in a comment written when the wide name grammar
landed: *"A `-`/`.` definition is therefore BUILDABLE as a target and
NOT CALLABLE from a pattern — exactly what a bench set needs, since its
patterns never call each other, and exactly what a library meant to be
composed must avoid"* (`src/parse/rxt_source.c:288-291`). So this is a
design consequence with a shipped ruling behind it, not a comment edit,
and it goes to Frank rather than being absorbed in the fix round.

*Why ACCEPT is recommended, in four lines.* (1) **The replacement is
better than the thing lost**: after §2.22 a call is explicit and named,
and the collision refusal makes an ambiguous one loud — where today
"not callable" is enforced by an accident of PCRE2's name grammar that
says nothing about intent. (2) **Delivery is governed separately and
already is**: `export` (W1.3, D89 addendum) is a definition's own
statement of its interface, and a library that wants a private helper
declares it by not exporting it — which is the mechanism for this that
the format actually has. (3) **No current customer**: the bench's
patterns never call each other (the comment's own stated customer), and
no file in either repo declares a definition it wants unreachable —
D77 says wait for a measured need, and the need here is for the
CAPABILITY that is being removed, which has none. (4) **The loss is
reversible at a known price**: a `private` marker or a
`no-derived-call` schema row would restore it, one row and one arm, the
day a library wants it.

*What ACCEPT costs, stated so the ratification is informed*: a library
author who today gets non-callability for free by naming a helper
`helper-impl` will, after W23, have to say so with `export`. That is a
real change in what a spelling means, and it is why the two comment
sites move in the same change (SW12) rather than being left to
contradict the behaviour.

**Beyond W23-F4, revision 3.2 adds NO question to this queue**, and
that is deliberate: the two 2026-09-12 rulings delegate syntax to the
manager (the 14:5x delegation, restated by the ownership ruling), so
§2.26's three spelling moves, §1.6's declined version break, §1.6.1a's
narrowing choices (including the tab refusal) and §2.25's eight
constraint kinds are the manager's calls, made and defended here rather
than escalated. The panel is the check on them.

**Recorded as RULED, not asked again**: F-Q1 (Tier 1 + Tier 2, one W23
delivery — §1.4), F-Q2 (`pattern-esc` — §2.19), Option A (the set's
truth lives in `.rxt` — nothing in this revision answers a need
bench-side; the one candidate, P-Q4, went in-format), STEP 0's two
refusals (lane rxtnul; designed against, not restated), and the two
2026-09-12 rulings this revision exists to work through — internal
consistency (§1.2, §1.6, §2.25) and ownership (§2.26).

---

## 8. The [B42] P-Q dispositions (revision 3)

All nine of `bench_rxt_needs_v1.md` §5.1, answered with the rationale
beside each; the manager's pre-rulings verified where they asserted a
checkable fact, and the two leanings worked to a confirmed answer.

**P-Q1 — the head/body indentation asymmetry. RE-ANSWERED AT REVISION
3.1 ON FRANK'S RULING, which arrived after revision 3 was written and
which supersedes the manager's leaning by name.** The ruling
(`frank_inputs.md`, 2026-09-12) is explicit that the leaning — *"relax
the head/body asymmetry for a named set of body sub-block keywords"* —
is the wrong answer, *"because that answer requires a keyword table to
find structure, which is exactly the context-dependence ruled out
here"*. Revision 3's §1.2 was that answer.

So the asymmetry is not relaxed, it is **DELETED** (§1.2.1): ONE
attachment rule serves head continuation, `config` bodies, block
scalars and body child-records alike, and "which scope a keyword is
legal in" becomes a schema fact with no structural consequence. The
answer now rests on the ruling's own criteria rather than on the
two-customers argument:

- **Internal consistency (consequence 1)**: indentation means exactly
  one thing everywhere in the file, so there is no per-keyword
  structural exception left to accrete onto.
- **Structural parseability (consequence 5)**: §1.2.1's two devices
  recover blocks, sub-blocks and line membership from syntax alone,
  with one declared two-member parameter, and §1.2.3 states where that
  is not yet total without softening it.
- **Explicit sub-block syntax (consequence 4)**: designed as a visible
  marker and priced against bare indentation in §1.2.4; **indentation
  wins**, because a marker makes structure depend on two signals that
  can disagree, duplicates a schema fact per occurrence, and would
  require either a second mechanism beside the shipped head or a
  break — and the obligation is met instead by `--list-schema`
  answering "which kinds open a scope" exactly, once.
- **Schema validation (consequence 3)**: the rules the relaxation used
  to carry in parser control flow are now §2.25's declared rows.

The TWO-CUSTOMERS argument survives as corroboration rather than as the
case: `provenance` and `variant` still need children, and `provenance`
is now used at TWO PARENTS (§2.26 item 10), which is a general
mechanism earning its keep rather than a special case with two
instances. **M8 stays loud** — a bare indented line is still a hard
error, in one of two arms (attaches to nothing → structure; parent
takes no children → schema, naming the parent). The alternatives are
declined for their revision-3 reasons, unchanged: the flat `prov-*`
fallback answers provenance only and leaves `variant`'s continuation
hack standing; moving provenance to the head keyed by block name splits
a pattern's truth across two places (the bench's own reason). And the
parser hazard revision 3 closed by an ordering rule is now
**impossible in any reader that implements S1/S2** rather than closed by
discipline — a block opener applies among siblings, and a child is not
a sibling — which matters, because that ordering rule was MEASURED to
hold in only one of the three readers it was asserted of (§0.7).
**Qualified at 3.2 (r57 S-S5)**: that is a property of the
SPECIFICATION, so it is exactly as strong as the legs' conformance to
it. Leg A gets it by construction; legs B and C get it by being pinned
(§9's A-group), and saying "structurally impossible" unconditionally
would repeat the very move — asserting a rule of three implementations
— that this bullet exists to correct.

**P-Q2 — is `vocabulary` the right closed-set mechanism?** YES
(pre-ruling e, accepted): per-key declared sets, parser-enforced,
undeclared keys free (§2.15). The alternative — validation left to
consumers — silently downgrades four validated record-schema enums to
free strings at the absorption boundary, which is a regression the
format would be shipping.

**P-Q3 — `mc`'s counting rule.** Non-overlapping, and the rule is
`match_api.md` §3.1's protocol BY REFERENCE (§2.21): resume at the end
of a non-empty match, one character past the REPORTED START of an empty
one, no empty-retry. MEASURED against the pre-ruled formula and
`finditer` (§0.6): the bench's `pos = max(end, pos+1)` double-counts an
empty match found beyond the scan position; `finditer` over-counts both
(the NOTEMPTY class pcrec's entries cannot express). The bench's
adapter owes one edit; their note's own fallback ("the harness's rule,
whatever it is — say that") is exactly what the spec paragraph does.

**P-Q4 — does the capability declaration live in the format?** YES —
as `provides` (§2.16, W23-F2 to
Frank). The manager's recommendation confirmed on the bench's own
counter-argument being weighed: a capability list IS engine knowledge —
but `config … testee` already carries engine knowledge (a version
string), the file's reader needs the reason a pattern has no result for
a testee, and the bench-side alternative is one non-`.rxt` file, i.e.
the hybrid's partial return. Fail-closed; `requires` reserved by name;
the pre-compile policy stated once in the spec as the intended reading.

**P-Q5 — what replaces §4.5 item 4's regime mechanism?** Nothing
replaces it; it is REPAIRED (§2.22): the composer's definition lookup
gains a derived-identifier key through `pcrec_rxt_prefix_from_name` —
the mapping's ONE existing home — with the target-prefix collision
refusal reproduced at the call (exact spelling does not win; the
refusal names both definitions). Verified against the shipped composer
(`rxt_compose.c:169/:176/:690/:788` — the lookup and re-resolution
sites) and against the three-reader rule (the name GRAMMAR's three legs
are untouched; only leg A's composer lookup, a single implementation,
learns the map). §4.5 item 4 is then usable as designed, its two
surviving caveats restated. The sub-block alternative (a `regime` case
group) was worked and declined: it is a case scope by another name
(Frank ruled "there is no case scope"), it puts case lines under
indentation in the most load-bearing arms of all three readers, and it
buys nothing the shipped composer does not already deliver.

**P-Q6 — a W2-only first delivery?** MOOT BY RULING: F-Q1 makes the
first delivery Tier 1 AND Tier 2, one W23 wave (§1.4). Recorded so the
bench's §4.2 sequencing analysis is answered rather than orphaned.

**P-Q7 — the NUL refusal as a standalone change?** YES, and it is not
even waiting for W23: STEP 0 (lane rxtnul) lands it now, with the
duplicate-`description` refusal beside it. This revision designs
against both existing.

**P-Q8 — the `@file:` hash against §2.8's "no content hash" ruling.**
A DEFAULT, not a principle (pre-ruling b, applied): the ruling's own
premise — committed, reviewed subject files — fails for a generated,
gitignored tree, which is precisely the condition §2.8 says provenance
IS required under. `sha256` is optional; pcrec's corpus writes none;
the bench writes one per reference; §2.8 is re-scoped in place.

**P-Q9 — the two silent shipped hazards (M1 NUL truncation, M5
description last-wins).** Both become refusals at STEP 0. The design's
own contribution is not repeating the shape: every W23 production with
a duplicate case states refuse-by-name (a second `provenance`, a second
`vocabulary` for one key, a conflicting subject-id binding, a second
`configs` line, `pattern` + `pattern-esc` in one block, duplicate
`under` lines).

---

## 9. The [B42] acceptance checklist, mapped (their §3, 41 checks)

What the bench will run at the restart against the delivered pin. Each
row: the design element that satisfies it, or the stated deviation with
its reason. **Named deviations up front**: B5 is PARTIAL (NUL-in-pattern
parked on K9, §2.19); C10's outcome is REFUSAL (STEP 0), which their row
explicitly admits ("the check records the CHOICE"); **B6's PREMISE
DISSOLVED at revision 3.2** — the refusal it tests has an empty
population under §1.2.1's opener rule, so the row is REWRITTEN rather
than satisfied or deviated from (§2.19, r57 S-BL2); D1/D5/G3 carry a
PRECISION about appended header columns (below); E5's harness half is
the bench's own, as their row itself states, and at 3.2 it also
becomes utf8-bearing (r57 C-S6).

**THE CHECKS THAT HARD-CODE A SPELLING OR A COUNT, listed once so
the bench gets ONE correction list rather than a surprise per check**
(revision 3.1's list, corrected and extended at 3.2 — r57 S-M6, S-BL2).
Every check below is BEHAVIOURAL and every one still passes or is
rewritten with its reason; what moves
is the literal token some of them type. The manager's outbox message at
delivery carries exactly this list (D78):

| moved | affects |
|---|---|
| `capable` → **`provides`** (§2.26 item 4) | **NO acceptance check types this token** — MEASURED at 3.2 (r57 S-M6): `capable` occurs 0 times in their §3 checklist (7 times elsewhere in the note, all in prose and production sketches). It affects the SET FILE their C-group checks run against, and any fixture that writes a `config` body — the probes' assertions are unchanged, and none of their scripts needs an edit for this row. **Revision 3.1 cited "the C-group capability checks", which is an EMPTY POPULATION**, and a correction list that over-warns teaches its reader to skim it |
| `licence`/`licence-note` → **`license`/`license-note`** (§2.26 item 10) | **C4 — the one check that types the token** (`drop \`licence\``, their §3 row C4), plus the provenance fixture the C4-C7 group shares. 3.1 said "C4-C7's provenance fixtures"; C5/C6/C7 assert the conditional, the control and the duplicate refusal and type no license field |
| the `freq` block's `exemplar`/`date`/`bytes`/`sha256` → a **`provenance` child** (§2.10) | only fixtures that write a data block; the bench's set files carry none today, so this is a spec-side move for them |
| **D1's provenance key count: NINE → ELEVEN, plus the two renames** (§2.14, §2.24) — **ADDED AT 3.2 (r57 S-M6)** | their D1 row asserts *"a row or column for each of: … `provenance`'s **nine keys** …"*. The record is ELEVEN fields at 3.1 (`source`, `url`, `ref`, `license`, `license-note`, `retrieved`, `fidelity`, `adaptation`, `attribution`, `bytes`, `sha256`), two of them under new spellings. **§9's own D1 row below has known this since 3.1 and the CORRECTION LIST did not carry it** — which is the whole failure mode this list exists to prevent, occurring inside the list itself: a correction stated in one place and not in the place the bench reads. Their D1 probe's column enumeration needs the two renames and the two added keys |
| a pattern block's `description` accepts **`prose-value`** (§1.2.5) | C10's neighbourhood only as a widening; nothing they assert becomes false. **(3.2: this row stays in the list because the bench needs it, but its CAUSE is corrected — it is §1.2.5's consequence of the structure-layer re-factoring, not one of §2.26's spelling moves, r57 C-N11. The audit moved three spellings; this is a fourth change with a different origin, and the outbox message says so)** |
| **B6's premise DISSOLVED** (§2.19) — **ADDED AT 3.2 (r57 S-BL2)** | their B6 asserts that `pattern` and `pattern-esc` in one block are refused naming both lines. **There is no such refusal, because there is no such block**: both are block openers, so the second line starts a new block (MEASURED — two adjacent `pattern` lines produce two `--list-source` rows, rc 0). B6 is not a failure and not a deviation — the state it tests cannot be constructed. **Their row should be rewritten** to assert what is true and worth pinning: that a `pattern-esc` line following a `pattern` line opens a SECOND BLOCK, with the two blocks' own cases attached correctly. That is a better check than the one it replaces, because it pins the structure layer's own rule rather than a refusal |

And one check the bench should ADD, because revision 3.1 creates the
surface for it: `--list-schema` is the query behind D4's
VALIDATES-vs-RECOGNISES table (§2.24), so their D4 probe can compare
the rendered spec table against the dump instead of against prose.
Offered, not required — their gate, their call (D78).

**A note on how this list is now derived, because it went wrong twice
in one revision** (r57 S-M6): a moved spelling's affected checks are
found by GREPPING THEIR §3 CHECKLIST for the token, not by reasoning
about which check-group the production belongs to. Revision 3.1 did the
second and produced one row with an empty population (`capable`) and
one over-broad row (`licence` at C4-C7 where only C4 types it), while
missing a row entirely (D1's key count, which is a COUNT rather than a
spelling and so did not look like a rename). The rule that catches all
three: **sweep the checklist for every token this revision moves AND
every number it changes.**

| # | disposition |
|---|---|
| A1, A2 | SATISFIED — every named keyword lands in the one W23 delivery (F-Q1), so both probes exit 0 at the delivered pin. The BEFORE (refused by name with a wave) holds at today's pin, M10 |
| A3, A4 | SATISFIED, unchanged mechanism — unknown tokens stay hard errors naming their SCOPE; a child scope is declared like any other (§1.2.2, §2.25) and the count is no longer fixed at four; SW13 keeps the recognised-refusal list honest for partial builds and now derives it from the schema's `wave` column. **THE FIXTURE OBLIGATIONS THIS DELIVERY OWES ARE NAMED BELOW THE TABLE** (3.1 said "an INDENTED-LINE fixture in all three legs" and left the position, the assertion and the rest of the population unstated; r57 S-M2/S-M5 and the grammar lens's five pinned probe cells fix that) |
| A5 | SATISFIED — `tag` accumulation and mixed labels/pairs are unchanged W2 design; `tag-prose` adds the third item kind (§1.3) |
| B1, B2 | SATISFIED (regression guard) — `pattern` verbatim untouched (§2.19); the dump's escape round trip unchanged |
| B3, B4 | SATISFIED BY STEP 0 (lane rxtnul) — the raw-NUL refusal with its control; independent of W23, as their P-Q7 asked |
| B5 | **PARTIAL, stated**: `pattern-esc` round-trips `\n` and a trailing `\r`; **`\x00` is REFUSED BY NAME naming K9** (the compile entry takes no pattern length — a decoded NUL pattern would silently compile as its prefix, the very trap B3 closes). Lifts when `rx_info.pattern_len`'s API half lands; §2.19 |
| B6 | **PREMISE DISSOLVED — a bench CORRECTION, not a deviation** (3.2, r57 S-BL2). B6 asserts that a block carrying both `pattern` and `pattern-esc` is refused naming both lines. **No parse state holds both**: `pattern-esc` is a member of S2's block-opener set, so a second opener among siblings starts a SECOND BLOCK (MEASURED — two adjacent `pattern` lines produce two `--list-source` rows, rc 0, §0.8), and the refusal revision 3 designed had an EMPTY POPULATION from the moment §1.2.1 made both spellings openers. The rule is dropped rather than rescued — rescuing it would need a keyword-dependent structural exception, which consequence 1 forbids. Their row is rewritten to pin what IS true: a `pattern-esc` line after a `pattern` line opens a second block, and each block's cases attach to their own. **This is K35 caught at DESIGN time** — a check mapped SATISFIED by a refusal nobody had counted the population of — which is why it is listed among the corrections rather than quietly re-worded |
| B7 | SATISFIED BY DESIGN, and this delivery is where it gets its first live verification (their row: "nothing has ever verified it") — the driver's `@<path>` form reads bytes raw, NUL included (H6/S5) |
| C1, C2, C3 | SATISFIED — `vocabulary` enforcement with its accept control and the free-key compatibility control (§2.15). C3 doubles as the R-COMPAT-1 guard for the corpus's zero tags |
| C4, C5, C6 | SATISFIED — provenance's required-line and conditional-adaptation refusals with their controls (§2.14 rules 1-3). **3.1 SPELLING**: `licence`/`licence-note` are now `license`/`license-note`, and the required SET is declared per parent (a pattern block's is the four their fixtures use, unchanged) |
| C7 | SATISFIED — a second `provenance` refused by name, never last-wins (§2.14). **CORRECTED AT 3.2 (r57 S-S7): that is `cardinality: at-most-one`, not a `unique-by` row.** Revision 3.1 called it a `unique-by` row here and a CARDINALITY value in §2.25.3 — one fact claimed by two mechanisms, which inflated `unique-by`'s earned-ness under §2.25.3's own membership rule. The duplicate-refusal discipline P-Q9 lists is therefore TWO mechanisms, not one: `cardinality` for "at most one of these in this scope" (a second `provenance`, a second `configs` line), `unique-by` for "at most one per key tuple" (`under`, a `vocabulary` key), and `functional-binding` for the subject-id case that is neither. The check the bench runs is unchanged either way |
| C8, C9 | SATISFIED — the sha256 mismatch refusal (checked by the subject's READER, §2.18) and its matching control |
| C10 | RESOLVED AS REFUSAL — STEP 0's duplicate-`description` refusal; the check records that choice, and G3's M5 row changes accordingly |
| D1 | SATISFIED — every listed production appears in the dump: `tag`/`oracle` as columns or rows, provenance's fields in `#section provenance` (eleven at 3.1, and the section now also carries a data block's provenance — one section, one record shape, §2.26 item 10), `variant` in `#section variants`, `mc`/`under`/subject id + hash in `#section cases` (§2.24) |
| D2 | SATISFIED — the loader reads only the dump; the cases section is what makes that possible under Option A (expectations are in the file, so they must be at the seam) |
| D3 | SATISFIED — one escape vocabulary, documented; NOTE for their loader: the dump escapes the FIVE TSV-framing escapes (`rxt_format.md`'s r46sem-22 paragraph), with `\f`/`\v` arriving as `\xNN` and a literal `"` unescaped — decode against the dump's table, not the subject table |
| D4 | SATISFIED, AND STRENGTHENED AT 3.1 — the table is not only normative spec text (SW11) but **RENDERED from the schema's `validated_by` column** (§2.24, §2.25), so it cannot go stale by omission and their probe can compare it against `--list-schema` rather than against prose. The case-line silent-pass observation is retired |
| D5 | SATISFIED WITH A PRECISION — a no-new-production file emits no `#section` line; its stream differs from the current pin ONLY in the header row's appended columns, which is `table_contract.md`'s own compatible evolution. Their pass criterion "output unchanged" should read "unchanged under name-resolved comparison"; a byte-diff will show the header. Same precision applies to G3 below |
| E1, E2 | BENCH-SIDE (their id/slug containment; their M11 finding is theirs to fix) — the format's half is the wide name grammar, BUILT |
| E3 | SATISFIED — `as <id>` gives every expectation and report row a line-number-independent key (§2.18) |
| E4 | SATISFIED (regression guard) — duplicate block names stay refused |
| E5 | FORMAT HALF SATISFIED (`under`, §2.17); the harness half is the bench's own, exactly as their row states (R5 B1); pcrec's harness counts `under` lines as labelled skips and their runner scores them. **At 3.2 this group also carries the `mc` COUNTING cross-check and it becomes UTF8-BEARING** (r57 C-S6): the fixture runs at least one `mc` over an ILL-FORMED UTF-8 subject under `-e utf8`, because SW7 now states the empty-match advance rule for invalid input normatively (from `pos+1`, skip `0x80`-`0xBF`) and a rule whose only cell is well-formed is a rule with no cell. The three implementations compared are the driver's C loop, `verify_rxt.py`'s python loop and `match_api.md` §3.1's printed protocol — and the python arm is a deliberate SECOND implementation of the advance, paid for by exactly this differential (§2.21) |
| E6, E7 | BENCH-SIDE — `make check-harness` enumeration and `content_hash` coverage are their gates; the format contributes the closure being enumerable (`--list-source` + include resolution) and nothing else is asked of it |
| F1 | SATISFIED — the permanence SENTENCE lands (SW5); the parse already worked (their M12) |
| F2 | SATISFIED — under `configs describe` a set's config cannot reach any pcrec build (refused for `target … with`, inert for everything else, §2.20): "the command line wins, or the file is refused" — the design delivers BOTH arms, by construction rather than by precedence |
| F3, F4 | BENCH-SIDE gates (their no-build-directives `make check`, their AR-6 review); the format's contribution is that a planted `engine vm` in a `describe` file is still a legal line the gate must catch — their gate, unchanged |
| G1 | SATISFIED — R-COMPAT-1 production by production (§1.3's closing paragraph): every addition is a fresh token (census 0, §0.6), an extension of a refused production, or new syntax at a today-hard-error position. pcrec's own `make test` green is the delivery bar as always |
| G2 | SATISFIED — the five committed exports round-trip unchanged (no existing production moved); whether the exporter ADOPTS `as`/`sha256` is the bench's call |
| G3 | AS THE CHARTER PREDICTS, WITH THE D5 PRECISION: **M1 changes** (STEP 0's refusal — their first-ranked item), **M5 changes** (STEP 0's refusal), **M10 changes** (the W23 keywords stop being refused). M2-M4, M6-M9, M11-M13: the FACTS are unchanged (byte-exactness, trims, acceptance, refusals, exit codes) — but any probe that archives a successful dump verbatim will show the header row's appended columns and, for case-bearing fixtures, the new `#section cases` rows. The probe script should diff name-resolved (or the archive is re-baselined once, at the delivery, with this paragraph as the cited reason). Any OTHER movement is a finding, exactly as they wrote |

### 9.1 The A3/A4 CHECK PLAN — the named fixtures this delivery owes

**NEW AT REVISION 3.2** (r57 S-M2, S-M5, and the grammar lens's five
pinned probe cells, which arrive ready-made). Revision 3.1's A3/A4 row
owed "an indented-line fixture in all three legs" and left everything
about it unstated. A fixture obligation with no name, no position and
no stated assertion is a fixture nobody writes, so the plan is a table.

Every row lands in `tests/rxtsource/fixtures/` (the `.rxtin` shape the
three-leg differential already dispatches over); **none is built by
this lane** — these are PLANNED, and the implementation lane that lands
H12/H16 builds them.

| fixture | position | what it asserts | why it exists |
|---|---|---|---|
| `indent_pre_body.rxtin` | **an indented `m` line BEFORE the first `pattern`** | all three legs refuse, and the DIAGNOSTIC CLASS is `structure-attachment` in all three — not merely exit 1 | **THE POSITION IS THE CHECK** (r57 S-M5). Leg C's `:424` indentation test is unconditional once a block is open; its pre-body block (`:407-423`) dispatches on the first token first, and that is the only place the ordering defect is reachable. A post-body fixture reports GREEN against the defect it exists to pin — [MECH-REACH]'s shape. Leg B has no attachment step at all and must grow one |
| `indent_under_m.rxtin` | an indented line under an `m` case line, mid-block | all three refuse, class `schema-constraint`, naming the PARENT (`m` declares `children: none`) | the second arm of §1.2.1's deletion 3, and S-R1's detector: flipping `m`'s `children` makes leg A accept while B and C refuse, so only the differential sees it |
| `prose_hash.rxtin` | an indented `#` inside a `description \|` body | all three ACCEPT, and all three decode the value with the `#` line as PROSE | §1.6.1a candidate (2), a narrowing AVOIDED by S3. It pins the avoidance, which is what a decision needs and an accident does not. Grammar-lens probe cell, reproduced §0.8 |
| `prose_ragged.rxtin` | prose lines at differing depths inside a `description \|` body | all three ACCEPT and agree on the decoded value, relative indentation preserved | §1.6.1a candidate (3). Also S-M1's owed fixture — no fixture carried a ragged prose body before |
| `prose_dedent.rxtin` | a prose line indented LESS than the block's first continuation | **NOT an acceptance assertion — the K57 repro**, carried as a `known_fail`-style cell until K57 is fixed, then inverted to a three-way value agreement | the shipped strip corrupts content silently (§0.8). A fixture that asserts today's behaviour would PIN THE BUG; one that asserts the right answer is red until the bug is fixed, which is what `tests/known_fail/` is for |
| `config_tab_body.rxtin` | a TAB-indented `config` body | all three REFUSE, class `structure-attachment`, the diagnostic naming the tab | §1.6.1a narrowing (4), TAKEN. Grammar-lens probe cell; accepted today (rc 0), so this fixture is the narrowing's own regression |
| `config_mixed_indent.rxtin` | a `config` body mixing a 2-space line and a TAB line | all three REFUSE, same class | the case that shows the tab rule is not cosmetic: this file parses FLAT today (rc 0) and has no defined tree under any depth rule |
| `block_scalar_in_body.rxtin` | **EXISTING — re-aimed, not deleted** | inverted from "all three refuse" to "all three accept and agree on the decoded value" | §1.2.5's widening; SW16 carries it. A three-way agreement on a VALUE catches more than a three-way agreement on a rejection |
| `prov_adapted_no_adaptation.rxtin` + `prov_verbatim_no_adaptation.rxtin` | a `provenance` sub-block under a pattern block | the first refused (class `schema-constraint`), the second accepted | S-R2's **pcrec-side** detector (r57 S-M3) — the bench's C5/C6 test the same rule in the other repo and cannot turn this repo's matrix red |
| `derived_call_collision.rxtin` | `(?&x_y)` with `x_y` and `x-y` both defined | refused, naming BOTH definitions and the shared identifier | §1.6.1a narrowing (5); accepted today with a byte-identical artifact (§0.8), so this fixture is that narrowing's regression. Leg A only — legs B and C resolve no calls (§2.22) |
| `mc_illformed_utf8.rxtin` | an `mc` over an ill-formed UTF-8 subject under `-e utf8` | the driver's C loop, `verify_rxt.py`'s python loop and the count agree | SW7's newly-normative advance rule (r57 C-S6); §9's E5 group |

**AND THE POPULATION CHECK, which is the part that does not go stale**
(r57 S-M2): a check walks `--list-schema`'s own output, selects every
row with `validated_by: all-readers`, and **fails naming any row with
no fixture above**. Three properties make it worth more than the
fixtures it guards: it reads the same table the parser enforces, so a
row added in a later wave fails the check the day it lands rather than
the day somebody remembers; it cannot be satisfied by a fixture that
stopped reaching its site, because it counts rows against fixture
NAMES declared per row; and it makes the honest fallback cheap — a row
whose fixture is not written yet takes `validated_by: pcrec`, which is
a true statement, instead of `all-readers`, which would be a claim
about two parsers nothing tests.

**Every three-leg assertion above compares DIAGNOSTIC CLASS, never exit
code** (§2.25.5, r57 S-S8). Leg B refuses everything through one
catch-all sentence, so a verdict-only comparison reads "all three
refuse" for a rule leg B has never heard of. The classes are the four
§2.25.5 names: `structure-attachment`, `unknown-token-in-scope`,
`schema-constraint`, `value-shape`. D26 is untouched — the class is a
tag the check reads, not a sentence a human reads.
