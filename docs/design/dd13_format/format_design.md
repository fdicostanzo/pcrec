# [DD-13b] Design note — the grown `.rxt` format: grammar and semantics

**Status: REVISION 3 ([DD-13b.W23], 2026-09-12, lane w23design) — the
[B42] absorption.** Revision 2 was post-panel (r44) and post-ruling
(D87); revision 3 absorbs pcrec-bench's capability-set needs note
(`bench_rxt_needs_v1.md`, received via outbox O-26) under Frank's two
2026-09-12 rulings — **F-Q1**: the first delivery is Tier 1 AND Tier 2
together, one **W23** delivery, no W2-only cut (§1.4 restructured);
**F-Q2**: multi-line patterns are a MUST (`pattern-esc`, §2.19). W1 is
BUILT (steps .1/.2/.3 landed; the wave table records what remains).
§0.6 is the need-by-need revision record; §8 disposes the bench's nine
P-Q questions; §9 maps their 41 acceptance checks. The W1-era text below
is revised in place where a W23 production touches it and untouched
elsewhere.

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

A `.rxt` file gains a **HEAD** (file-level declarations and `config` /
data blocks, everything before the first `pattern` line) above the
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
  `provenance`, `pattern-esc`, `capable`, `under`, `configs`, and the
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
| **N-11..N-19** | §2.14 `provenance` — a body SUB-BLOCK (§1.2's new mechanism), nine fields, four required, `adaptation` required iff `fidelity != verbatim`, `authored`'s agreement rule. Roadblock #3 closed |
| **N-22, N-23** | §2.16 `capable` — per-config, repeatable, accumulating, **fail-closed** (absent = nothing satisfied); flagged to Frank with §2.20 (P-Q4's ratification) |
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
| **N-39, N-40, N-41** | §2.23 — `variant` becomes a body SUB-BLOCK: `kind` (closed via `vocabulary kind`), `text`, `groups`, `note` (prose), `unsupported`. The old one-line-plus-`groups`-continuation shape was a proto-sub-block; the general mechanism replaces it (house rule). N-41's three fields all have carriers |
| **N-42** | `config … testee`/`option` land in W23 as designed |
| **N-43, N-44** | §2.20 `configs describe` — the head declaration separating BUILD configs from DESCRIPTIVE ones, default `build` = today's semantics; plus the PERMANENCE sentence for a target-less, config-less file. Roadblock #6 closed; ratification flagged to Frank (D93 territory) |
| **N-46, N-47** | BUILT (W1), untouched |
| **N-49** | the regime -> subject-set mapping rides the repaired item 4 (§2.22): each regime block carries its own subject list |
| **N-50** | `include` lands in W23 as designed (§2.5, §2.11) |
| **N-52** | §2.24 — `--list-source` gains appended columns, **unconditional named sections** (`provenance`, `variants`, `cases`), and a spec-stated VALIDATES-vs-RECOGNISES table (their D4). The `m @file:… passes silently` observation is retired: case values are read |

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

### 1.2 The file shape

```ebnf
file        = head , body ;
head        = { head-item } ;
body        = { pattern-block } ;

head-item   = file-decl | config-block | data-block ;
pattern-block = pattern-line , { block-line } ;
```

**The head ends at the first `pattern` line, and nothing file-level may
appear after it.** This is AR-4 discharged mechanically: a D27-blinded
author reading any block needs to look in exactly one other place — the
top of the file — and that place is bounded. It is also what makes a
one-block file with no head behave exactly like `pcrec 'pattern'`
(AR-2/AR-7).

Lexical rules, unchanged from today and binding on every new line kind:

- Whole-line `#` comments only (R-RXT-2). A `#` anywhere but column 1 is
  data. The one comment with meaning — `# pcre2-only` immediately before
  a `pattern` line — keeps it, and is defined in §2.9 as an alias.
- Blank lines ignored.
- A line kind is its first whitespace-delimited token. An unknown first
  token is a **hard error** (R-RXT-6's discipline generalised): never a
  silent no-op, never a comment.
- **Four lexical CONTEXTS, each with a closed vocabulary.** The format
  already has two — the file's own directives and a pattern block's
  case vocabulary (`m`/`n`/`g`/…). This design adds two more (`config`
  body, data-block body). A first token unknown *in its context* is a
  hard error that names the context ("`testee` is not a pattern-block
  directive"). Nothing is a keyword everywhere.
- **IN THE HEAD, INDENTATION MEANS CONTINUATION.** A line indented by
  one or more spaces continues the head declaration or block above it: a
  `config` body, a data-block body, a `description` attached to a
  `target` or a `lib`, and a block-scalar value's own lines are all the
  same rule. A head construct therefore ends at the first non-indented
  line, and a typo inside a `config` body is a hard error naming the
  block rather than a silent block-ending.
  **MEASURED, and this is what makes it free:** **0** lines in the
  179-file corpus begin with whitespace
  (`grep -rhcE '^[[:space:]]+[^[:space:]]'` → 0; independently reproduced
  by r44-grammar's own recognizer run, G1), so no existing line's meaning
  can change. This REPLACES the first version's "leading whitespace is
  permitted and ignored"; Frank's `description` block scalar (r44, 15:1x)
  needs continuation to mean something, and one rule serving every head
  construct is better than a second mechanism beside it.
- **A PATTERN BLOCK keeps today's shape: its DIRECT lines are NOT
  indented**, and a block ends at the next `pattern` line or end of
  file. **REVISED at W23** ([B42] P-Q1; this deliberately and NARROWLY
  relaxes what revision 2 called "the only asymmetry"): a block-scoped
  line kind may be declared a **SUB-BLOCK KIND** — this revision
  declares exactly two, `provenance` (§2.14) and `variant` (§2.23) —
  whose line is followed by INDENTED attribute lines, one attribute per
  line, ending at the first non-indented line **including a blank one**
  (the head's own r46sem-10 rule, reused rather than re-decided). The
  rules that keep N-2's loud failure alive, each binding on ALL THREE
  body readers (`src/parse/rxt_source.c`, `tests/harness/run.sh`,
  `tests/harness/verify_rxt.py` — the C1 differential is what holds
  them together):
  1. **The indentation test PRECEDES token dispatch.** An indented line
     is a sub-block attribute or a hard error; it is never dispatched on
     its first token. Without this rule an indented `pattern` line would
     start a new block in one reader and continue a sub-block in
     another — the one defect this mechanism could introduce, closed by
     ordering, and the reason the sub-block attribute vocabulary avoids
     the token `pattern` anyway (`variant` carries `text`, §2.23).
  2. **An indented line NOT under a sub-block keyword line stays a HARD
     ERROR**, with today's diagnostic ("a pattern block's lines are not
     indented" — `verify_rxt.py:426`, `run.sh:2065-2088`, and
     `rxt_source.c`'s same refusal, the bench's own MEASURED M8). In
     particular an indented continuation under `pattern` is refused
     exactly as today: `pattern` is not a sub-block kind, and F-Q2 is
     answered by `pattern-esc` (§2.19), never by continuation.
  3. **A sub-block's attribute vocabulary is a fourth closed lexical
     context** (§1.2's context rule, one more member): an unknown
     attribute is a hard error naming the sub-block.
  Two customers is what makes this a mechanism rather than a special
  case: `provenance` needs a nine-field body no one-line form can hold,
  and `variant` under N-41 needs `kind`/`text`/`groups`/`note` — and
  revision 2's `variant` ALREADY had a one-off un-indented `groups`
  continuation line, which this replaces (a proto-sub-block retired by
  the general form). Regime grouping, the candidate third customer, does
  NOT ride this mechanism — §2.22 repairs the wrapper mechanism instead,
  and the reasons are recorded there.
  A generator writing an included fragment still writes pattern blocks
  only (§2.5); it indents exactly when it writes a sub-block.
  MEASURED FREE: **0** indented lines exist in the corpus (§1.1), so no
  existing file can reach any of this.
- **One line, one value — with exactly ONE exception: the BLOCK SCALAR.**
  A line kind whose value is prose may write `<kind> |` and continue on
  indented lines, YAML's `|` form; newlines are preserved and the value
  ends at the first non-indented line. The one-line form
  `<kind> <text>` stays. The exception is stated as a property of the
  VALUE production (`prose-value`) rather than of any keyword, so a
  second prose field inherits it rather than inventing it. **W23
  extends WHERE the production is legal, not what it is**: `prose-value`
  is a head form AND a sub-block-attribute form — inside a sub-block a
  `|` scalar's continuation lines are indented DEEPER than the attribute
  line, the same relative rule one level down. A pattern block's DIRECT
  lines still cannot carry it (`description` at block scope stays
  one-line; the W1.1 correction stands).

### 1.3 The productions

Each production carries its wave: **W1** composition, **W2** large and
generated sets, **W3** per-engine / per-config application. A parser may
ship W1 alone and reject W2/W3 keywords with "not in this build"; the
grammar is designed so that is a *subset*, never a *dialect of a
dialect*.

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
            | "|" , eol , { INDENT , rest-of-line , eol } ;  (* block scalar *)
INDENT      = ? one or more spaces at the start of the line ? ;
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
                                                                  (* W23 *)
    | "configs"    , ws , ( "build" | "describe" )                (* W23 *)
    | "description", ws , prose-value ;                            (* W1 *)

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
    | "capable"  , ws , tag-value , { ws , tag-value } ;
                    (* W23: the capability tags this config SATISFIES;
                       repeatable, accumulating; ABSENT means NOTHING is
                       satisfied — fail-closed (§2.16) *)

engine-ref = ident , [ "/" , version-chars ] ;      (* e.g. pcre2/10.42 *)

(* ---------- head: data block (the analysis FAMILY, §2.10) ---------- *)
data-block = data-kind , ws , ident , eol , { INDENT , data-line , eol } ;
data-kind  = "freq" ;                    (* the family's only member    W2 *)
data-line =
      "description" , ws , prose-value   (* the summarizing script's field *)
    | "question" , ws , rest-of-line     (* what this answers, required *)
    | "reader"   , ws , rest-of-line     (* the selection point, required *)
    | "exemplar" , ws , rest-of-line     (* provenance, required *)
    | "bytes"    , ws , int              (* provenance, required *)
    | "sha256"   , ws , hex64            (* provenance, required *)
    | "analyzer" , ws , rest-of-line     (* provenance, required *)
    | "date"     , ws , iso-date         (* provenance, required *)
    | "row"      , ws , int , ws , int , { ws , int } ;  (* offset, then 16 counts *)

(* ---------- body: a pattern block ---------- *)
pattern-block = pattern-line , { block-line } ;
pattern-line  = "pattern" , ws , rest-of-line , eol          (* today's *)
              | "pattern-esc" , ws , quoted-pattern , eol ;       (* W23 *)
quoted-pattern = '"' , { subject-char | escape } , '"' ;
                    (* the SAME seven escapes; §2.19's rules — one of the two
                       spellings per block, `\x00` refused by name (K9) *)
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
    | "description" , ws , rest-of-line       (* one-line form ONLY   W1 *)
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

(* ---------- body: the two SUB-BLOCK kinds (§1.2) ---------- *)
provenance-block = "provenance" , eol , { INDENT , prov-line , eol } ;
prov-line =
      "source"       , ws , defname       (* a registered slug,   REQUIRED *)
    | "url"          , ws , rest-of-line  (* the exact URL fetched         *)
    | "ref"          , ws , rest-of-line  (* file/rule/line inside it      *)
    | "licence"      , ws , token         (* an SPDX id,          REQUIRED *)
    | "licence-note" , ws , prose-value
    | "retrieved"    , ws , iso-date      (* RFC 3339 date,       REQUIRED *)
    | "fidelity"     , ws , ( "verbatim" | "adapted" | "inspired" )
                                          (*                      REQUIRED *)
    | "adaptation"   , ws , prose-value   (* REQUIRED iff fidelity is not
                                             verbatim *)
    | "attribution"  , ws , prose-value ; (* the field exists; the licence
                                             policy is the consumer's *)

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
`configs`), one config-body line (`capable`), a second block starter
(`pattern-esc`), one case-line qualifier (`under`), two body sub-block
kinds (`provenance`; `variant` reshaped from its W3 one-line form), a
`tag-item` third alternative (`tag-prose`), and two optional suffixes on
`file-subject` (`as`, `sha256`). Every addition is ADDITIVE against the
shipped corpus — a new first token measured at 0 occurrences (§0.6), an
extension of a production the shipped build refuses by name, or new
syntax at a position that is a hard error today (an indented body line;
text after an `@file:` path) — so R-COMPAT-1 holds production by
production, and §9's G1 row says how that is checked.

**CORRECTION ([DD-13b.W1.1], 2026-08-30): a pattern block's
`description` takes the ONE-LINE form only — the production above said
`prose-value`, which includes the `|` block scalar, and that cannot
hold.** §1.2's lexical rules say a block scalar IS indented continuation
and that a PATTERN BLOCK's lines are NOT indented; both cannot be true in
the body. The body's rule wins: it is the one R-COMPAT-1 and 3,265
existing blocks depend on, and §1.2 calls the head/body asymmetry "the
only one". A block scalar in the body would also need continuation
parsing inside `run.sh`'s per-line loop — head-shaped parsing back in the
harness, which is exactly what the seam ruling removed. `|` remains a
HEAD form (a file-level `description`, a `config` body) — extended at
W23 to sub-block ATTRIBUTES, whose lines are indented, which is the
precondition this correction was about (§1.2). MEASURED FREE:
**0** corpus lines are indented and **0** blocks carry a `description`,
so no existing file can reach either reading. Refused by name in all
three parsers, and `tests/rxtsource/fixtures/block_scalar_in_body.rxtin`
asserts all three agree.

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
| **W23** | the former W2: `include`, `@file:`, `mc`, `tag`, the `freq` data block + `analysis`; the former W3: `use`, `oracle`, `variant`, `config … testee`/`option`; the [B42] extensions: `pattern-esc`, `provenance`, `vocabulary`, `capable`, `under`, `configs describe`, `as`/`sha256` on `@file:`, `oracle` at a version, `tag-prose`, the §2.22 regime repair, and `--list-source` emitting ALL of it (§2.24) | **THIS revision's delivery.** Consumer: the [B42] capability survey set (Frank's ruling); [ENG-PGO]'s findings file rides the same landing (its row said "blocks on wave 2/3") |

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

**Provenance is required** — `exemplar`, `bytes`, `sha256`, `analyzer`,
`date` — because the exemplar is absent by design (proprietary, secret,
or too large). The table can then be re-derived when the exemplar is at
hand and **reads honestly when it is not**. A byte histogram is 256
counts and effectively non-reversible, so committing it leaks
essentially nothing; committing it *without* provenance would be the
population-nobody-counted hazard one file over.

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

A body SUB-BLOCK (§1.2), at most ONE per pattern block — a second is
**refused by name**, never last-wins (the shape STEP 0's
duplicate-`description` refusal closes one production over; the bench's
MEASURED M5 is why this rule is stated rather than assumed). The
precedent is the `freq` data block's own required-provenance discipline
(§2.10): a wild pattern's source is absent from the repo by exactly the
logic an exemplar is, so its origin is REQUIRED fields, not prose.

Rules, each parser-enforced:

1. `source`, `licence`, `retrieved`, `fidelity` are **REQUIRED**; a
   `provenance` block missing one is refused naming the missing line —
   the `freq` block's `question`/`reader` rule, reused.
2. `url` and `ref` are **REQUIRED unless `source` is the reserved slug
   `authored`**, and an `authored` block that writes either is refused:
   the slug and the fields must agree or `authored` stops meaning
   anything. (The bench's own rule, adopted verbatim.)
3. `adaptation` is **REQUIRED iff `fidelity` is not `verbatim`** — the
   one conditional the format enforces, and the whole value of making
   the record structural: a mechanically-changed pattern with no stated
   change is the failure a reviewer cannot catch by reading.
4. `fidelity`'s three values are CLOSED **in the grammar**, not via
   `vocabulary`: the conditional in rule 3 requires the parser to know
   them, so a declaration mechanism would be a second home for a fact
   the parser already owns.
5. `attribution` exists as a field; whether a licence demands one is a
   POLICY the format does not know (SPDX is an open set) — the consuming
   project's gate enforces it. The field must exist so a CC BY-SA
   pattern has somewhere to put what its licence requires.
6. Prose fields (`licence-note`, `adaptation`, `attribution`) take
   `prose-value` — one line, or a `|` scalar indented deeper than the
   attribute line (§1.2). ONE prose mechanism, everywhere.

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

`vocabulary <key> <v1> <v2> …`, head-only, wrapping by the head's own
indentation-continuation. Declares that `tag <key>=<value>` (and every
other production the spec names as vocabulary-checked: `under`'s
convention, `variant`'s `kind`, `capable`'s values) may only take a
listed value; a violating value is **refused by name**, naming the key,
the offending value and the declared set.

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

### 2.16 `capable` — what a config's engine satisfies ([B42] N-22/N-23)

A `config`-body line, repeatable and accumulating like `tag`: the
vocabulary values this config SATISFIES. **Absent means NOTHING is
satisfied — fail-closed, deliberately**, so a new adapter cannot claim
capabilities by omission (the bench's own rule, adopted).

- **The key name `requires` is RESERVED by one spec sentence**: when a
  `vocabulary requires …` declaration exists, every `capable` value must
  be a member of it (refused naming value and set); with no such
  declaration, `capable` values are free. The format thereby knows ONE
  NAME — that the key `requires` is where capability tags live — and
  still nothing about what any tag means. The precedent for reserving a
  name is `# pcre2-only` and the `oracle` engine names; AR-6 is about
  MEANING, not spelling.
- The pre-compile policy — `REQUIRES(pattern) ⊄ capabilities(config) ⇒
  unsupported-by-declaration`, decided before any compile — is the
  CONSUMER's rule. The format carries the declaration (`capable`), the
  per-pattern requirement (`tag requires=…`) and the outcome production
  (`variant <testee>` + `unsupported`, §2.23); the spec states the
  intended reading so two consumers cannot invent two policies, and
  R-BENCH-3/AR-3's counted-never-silent rule covers the outcome.
- pcrec's OWN harness ignores `capable` operationally (its one testee is
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

### 2.19 `pattern-esc` — the second pattern spelling ([B42] N-2, F-Q2)

`pattern-esc "<quoted>"` starts a block exactly as `pattern` does; its
pattern text is the DECODED bytes, using the format's own seven-escape
subject vocabulary and no second vocabulary. Because the escape table
already includes `\n`, `\xHH` and `\\`, a `(?x)` body authored across
lines, raw high bytes and a trailing CR all become expressible with
nothing new invented — **multi-line CAPABILITY without multi-line
SYNTAX**, which is what keeps every reader's line-oriented loop intact
and is why this form was chosen over continuation (continuation under
`pattern` would also have destroyed N-2's loud refusal, §1.2 rule 2).

- **A block carries `pattern` or `pattern-esc`, never both** — both is
  refused naming both lines.
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
4. **The declaration is the ENTRY file's** and governs the include
   closure — a fragment cannot carry head lines (§2.5), so a block's
   config semantics still depend on exactly one bounded place (AR-4).
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
  exact-`strcmp` sites at `rxt_compose.c:169` (`def_find`) and `:176`
  (`bound_by_name`), consumed by the re-resolution at `:690`/`:788`
  that binds each DEFERRED by-name call. The composer resolves a file
  reference AFTER the pattern's own groups (a call to a same-pattern
  group never defers, `:260`), so PCRE2's in-pattern semantics are
  untouched; the derived index is a second key on the SAME set, built
  with the same function, consulted by the same lookup. No new pass, no
  new namespace.
- **The collision rule is the target-prefix rule, re-used at the second
  consumer**: the mapping is deliberately not injective, and the refusal
  is where that is paid for. Two definitions in scope whose mapped names
  are equal make a call to that identifier a **refusal naming both
  definitions and the shared identifier** — including the case where one
  of them IS spelled as the identifier (`x_y` beside `x-y`): exact
  spelling does NOT win, because "exact" is only the identity case of
  the same mapping, and a silent tie-break would make the
  non-injectivity free exactly where it bites. Nothing is refused at
  DECLARATION time — two colliding definitions coexist while nothing
  calls the shared identifier, just as two hyphenated definitions
  coexist while neither is a `target =`.
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

**Why regime grouping does NOT ride §1.2's sub-block mechanism** (the
alternative the manager asked weighed): a `regime` sub-block holding
case lines would (a) be a CASE SCOPE, which Frank ruled out by name
("there is no case scope") — an attribute over a group of cases is that
ruling's own definition; (b) put case lines under indentation, forcing
all three body readers to re-parse their most load-bearing arms
(`run.sh`'s case dispatch) for a shape one consumer needs; and (c) buy
nothing the repaired wrapper does not already deliver with machinery
that SHIPPED in W1.3. The sub-block mechanism's customers are
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
`capable` (accumulated). New head ROW kinds (the existing "`kind`
carries the declaration name" rule): `vocabulary` (name = the key,
value = the escaped list), `configs` (value = `build`/`describe`),
`include`, `oracle`, `tag`, `use`.

**Three named SECTIONS, emitted UNCONDITIONALLY when non-empty**, under
`docs/spec/table_contract.md`'s `#section` mechanism — the trigger
`rxt_format.md` itself named ("a data block whose rows cannot be
columns of this table under any reading") is met by `provenance`, and
the same argument covers the other two:

- `#section provenance` — one row per provenance block: `line`,
  `block_line`, `block_name`, then the nine fields as columns, prose
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
block directives, sub-block completeness (provenance's required
fields, variant's exactly-one rule), vocabulary membership, case-line
syntax including `as`/`sha256` SPELLINGS and the subject-id binding
rules — and it does NOT (a) read any subject file (the `sha256`
CONTENT check belongs to whatever reads the subject, §2.18), (b)
compile any pattern (pattern TEXT is never validated here), or (c)
resolve configs (AS WRITTEN, unchanged; `--resolved` stays named and
unbuilt). The bench's measured observation that a case line's refused
`@file:` passed the dump silently is thereby retired — case values are
read, and an ill-formed one is a hard error naming its line.

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
| H12 | **the body SUB-BLOCK arms** in all three readers: indentation test before dispatch, skip-into-sub-block for `provenance`/`variant`, the bare-indented refusal kept verbatim (§1.2) | W23 | `run.sh`, `verify_rxt.py` (pcrec's own arm rides SW2/SW3/SW10) |
| H13 | **`pattern-esc`**: the pass-through arm + the CLI decode flag; `verify_rxt.py` decodes python-side; `\x00`'s K9 refusal surfaces through pcrec (§2.19) | W23 | `run.sh`, `verify_rxt.py`, `cli/` |
| H14 | **`under` as a counted, labelled skip** in `run.sh` and `verify_rxt.py` (scoring is the consumer's, §2.17); `mc` verified by the PROTOCOL loop in python, never `finditer` (§2.21) | W23 | `run.sh`, `verify_rxt.py` |
| H15 | **subject ids + hashes**: the per-file binding table, the read-time sha256 refusal on the driver path (§2.18); `configs describe`'s one-cell rule and its summary line (§2.20) | W23 | `run.sh`, `driver.c` |

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
| SW2 | `docs/spec/rxt_format.md` | the LEXICAL RULES section: the body SUB-BLOCK mechanism — declared kinds (`provenance`, `variant`), indentation-precedes-dispatch, blank-line termination, the bare-indented-line refusal UNCHANGED, `prose-value` legal inside a sub-block; the "only asymmetry" sentence rewritten to the narrow relaxation (§1.2) | W23 |
| SW3 | `docs/spec/rxt_format.md` | `provenance`: the nine fields, the four required, the `authored` agreement rule, adaptation-iff-not-verbatim, one-per-block (§2.14) | W23 |
| SW4 | `docs/spec/rxt_format.md` | `vocabulary` + `tag-prose` + `capable`: declaration, enforcement points (tag both scopes, `under`'s convention, `variant`'s kind, `capable`), the RESERVED-KEY sentence for `requires`, fail-closed `capable` (§2.15, §2.16) | W23 |
| SW5 | `docs/spec/rxt_format.md` | `configs build`/`describe`: the four describe rules, the `target … with` refusal, `use` inert-and-counted, entry-file scope — and the PERMANENCE sentence for a target-less config-less file (§2.20) | W23 |
| SW6 | `docs/spec/rxt_format.md` | the subject subsection (S4's row extended): `as <id>`/`sha256 <hex64>`, the per-file id namespace and functional-binding rules, WHO checks the hash (§2.18) | W23 |
| SW7 | `docs/spec/rxt_format.md` + `docs/spec/match_api.md` | `mc` and its COUNTING RULE — one normative paragraph citing `match_api.md` §3.1 as the rule's single home, the empty-advance-from-reported-start clause, the finditer-divergence class named; match_api.md §3.1 gains one sentence naming `mc` as a consumer of the protocol | W23 |
| SW8 | `docs/spec/rxt_format.md` | `under`: qualifier semantics, fallback, duplicate refusal, the no-`g`/`gp` rule, the harness's counted-skip treatment (§2.17) | W23 |
| SW9 | `docs/spec/rxt_format.md` | `oracle` widened to `engine-ref [/version]`; `python`/`pcre2` meanings unchanged; absent-oracle = labelled skip (§2.9) | W23 |
| SW10 | `docs/spec/rxt_format.md` | `variant` as a sub-block: the five attributes, exactly-one-of-text/unsupported, kind's vocabulary hook (§2.23); supersedes S8's one-line shape | W23 |
| SW11 | `docs/spec/rxt_format.md` | `--list-source`: the appended columns, the three `#section`s with their column lists, the **VALIDATES vs RECOGNISES table as normative text**, and the SECTIONLESS paragraph rewritten — its own named trigger fired (§2.24). `table_contract.md` needs NO hunk (sections were already its mechanism) | W23 |
| SW12 | `docs/spec/rxt_format.md` | the `name` grammar section's "cannot be called from a pattern" paragraph AMENDED: still true of the hyphenated SPELLING (PCRE2's grammar, D26), and the definition is now reachable through its DERIVED identifier — the mapping, the at-use collision refusal naming both definitions, exact-spelling-does-not-win (§2.22). **The three-reader note**: legs A/B/C's shared name grammar is UNCHANGED; the derivation lives only in the composer's lookup, so no reader gains an arm | W23 |
| SW13 | `docs/spec/rxt_format.md` | the "NOT IN THIS BUILD" recognised-keyword list grows the W23 keywords, so any future partial build refuses them by name rather than as unknown (MEASURED gap, §0.6: `vocabulary` is "not a file-level directive" today) | W23 |
| SW14 | `docs/spec/cli.md` | the `pattern-esc` decode flag; `--list-source`'s section output named in its entry | W23 |
| SW15 | `docs/spec/rxt_format.md` | the driver protocol: the find-all mode H7 lands (the §3.1 loop in C), the `@<path>` subject form's byte-exactness (S5's row, unchanged, referenced), the sha256 mismatch refusal | W23 |

**No `docs/spec/match_api.md` struct hunk and no abi bump anywhere in
W23** (§1.4) — SW7's match_api sentence is prose naming a new consumer
of an existing contract.

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
Its plan row says it blocks on "wave 2/3"; on this design it blocks on
**W2** alone.

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
| **[B42]** per-config capabilities (their §5.3) | `capable` lines in the testee's `config` (§2.16, Frank ratifies) |
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

### 5.3 The anti-requirements

| | how it is honoured |
|---|---|
| **AR-1** no re-verification of the corpus | INV-COMPAT (§1.1) with three independent checks, six sabotage rows and asserted denominators. MEASURED: 0 keyword collisions over 32 candidates, 0 head lines in 179 files, and no file reference to bind in any non-`perr` block. r44-grammar reproduced all three with its own recognizer (G1, G5, G6) |
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
under D93, roadblock #6), `vocabulary`, `capable`, subject ids + hashes,
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
  capable backrefs lookaround atomic-possessive recursion conditionals
  capable k-reset control-verbs unicode-properties named-groups
  capable free-spacing callouts span-reporting captures true-end-anchor
config re2
  testee re2/2024-07-02
  capable unicode-properties named-groups captures
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
  licence   CC0-1.0
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
`requires` line wraps by head continuation); the two `capable` stanzas
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
  exemplar prod-web-01 nginx access log, 2026-08 (not committed)
  bytes 4187336614
  sha256 9f2c0b1e7a4d38c5be6109f7d2a4c83b5e0d7f61a9c2b48e35d7061fa8c3b92d
  analyzer scripts/exemplar_freq.py 0.1
  date 2026-08-29
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

**Hand-trace.** The findings file's head is one data block, its body
lines indented under it (§1.2); the file's body is empty — a legal file
with zero pattern blocks, which the grammar admits
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

**W23-F2 — `capable` lives IN the format (§2.16).** The manager
recommends IN (a `config … testee` already carries engine knowledge;
the reason a pattern has no result for a testee belongs in the file a
reader has); fail-closed; the one reserved key name `requires`. The
alternative — bench-side capability files — is a partial return of the
hybrid the 2026-09-12 ruling removed, and §8's P-Q4 records why it was
considered and declined rather than defaulted. Recommended: ratify.

**W23-F3 — the `mc` counting rule's home (§2.21).** The manager
pre-ruled the bench's formula; measurement found it double-counts an
empty match found beyond the scan position, so the design states
`match_api.md` §3.1's shipped protocol instead and hands the bench one
adapter edit. No semantics change to any shipped surface — flagged
because a pre-ruling was deviated from on evidence, and because the
outbox message to the bench should carry Frank's (or the manager's)
confirmation.

**Recorded as RULED, not asked again**: F-Q1 (Tier 1 + Tier 2, one W23
delivery — §1.4), F-Q2 (`pattern-esc` — §2.19), Option A (the set's
truth lives in `.rxt` — nothing in this revision answers a need
bench-side; the one candidate, P-Q4, went in-format), and STEP 0's two
refusals (lane rxtnul; designed against, not restated).

---

## 8. The [B42] P-Q dispositions (revision 3)

All nine of `bench_rxt_needs_v1.md` §5.1, answered with the rationale
beside each; the manager's pre-rulings verified where they asserted a
checkable fact, and the two leanings worked to a confirmed answer.

**P-Q1 — the head/body indentation asymmetry.** ANSWERED: a GENERAL
declared body-sub-block mechanism (§1.2), the manager's leaning
CONFIRMED. Two genuine customers (`provenance`; `variant`, whose
revision-2 shape already carried a one-off un-indented `groups`
continuation the general form retires), the relaxation narrow (only
under declared sub-block kinds; the bare-indented-line refusal and its
diagnostic survive verbatim — their M8 stays loud), and the one parser
hazard it could introduce (an indented `pattern` starting a block in
one reader and continuing a sub-block in another) closed by the
indentation-test-precedes-dispatch rule binding all three body readers.
The fallback (nine flat `prov-*` lines) was examined and declined: it
answers provenance only, leaves `variant`'s continuation hack standing,
and gives regime grouping no answer — whereas the confirmed design
gives regimes a BETTER answer that is not this mechanism at all
(§2.22). Moving provenance to the head keyed by block name was declined
for the bench's own reason (a pattern's truth split across two places).

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

**P-Q4 — does `capable` live in the format?** YES (§2.16, W23-F2 to
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
explicitly admits ("the check records the CHOICE"); D1/D5/G3 carry a
PRECISION about appended header columns (below); E5's harness half is
the bench's own, as their row itself states.

| # | disposition |
|---|---|
| A1, A2 | SATISFIED — every named keyword lands in the one W23 delivery (F-Q1), so both probes exit 0 at the delivered pin. The BEFORE (refused by name with a wave) holds at today's pin, M10 |
| A3, A4 | SATISFIED, unchanged mechanism — unknown tokens stay hard errors naming their context; the sub-block contexts join the context list (§1.2 rule 3); SW13 keeps the recognised-refusal list honest for partial builds |
| A5 | SATISFIED — `tag` accumulation and mixed labels/pairs are unchanged W2 design; `tag-prose` adds the third item kind (§1.3) |
| B1, B2 | SATISFIED (regression guard) — `pattern` verbatim untouched (§2.19); the dump's escape round trip unchanged |
| B3, B4 | SATISFIED BY STEP 0 (lane rxtnul) — the raw-NUL refusal with its control; independent of W23, as their P-Q7 asked |
| B5 | **PARTIAL, stated**: `pattern-esc` round-trips `\n` and a trailing `\r`; **`\x00` is REFUSED BY NAME naming K9** (the compile entry takes no pattern length — a decoded NUL pattern would silently compile as its prefix, the very trap B3 closes). Lifts when `rx_info.pattern_len`'s API half lands; §2.19 |
| B6 | SATISFIED — both spellings in one block refused naming both lines (§2.19) |
| B7 | SATISFIED BY DESIGN, and this delivery is where it gets its first live verification (their row: "nothing has ever verified it") — the driver's `@<path>` form reads bytes raw, NUL included (H6/S5) |
| C1, C2, C3 | SATISFIED — `vocabulary` enforcement with its accept control and the free-key compatibility control (§2.15). C3 doubles as the R-COMPAT-1 guard for the corpus's zero tags |
| C4, C5, C6 | SATISFIED — provenance's required-line and conditional-adaptation refusals with their controls (§2.14 rules 1-3) |
| C7 | SATISFIED — a second `provenance` refused by name, never last-wins (§2.14) |
| C8, C9 | SATISFIED — the sha256 mismatch refusal (checked by the subject's READER, §2.18) and its matching control |
| C10 | RESOLVED AS REFUSAL — STEP 0's duplicate-`description` refusal; the check records that choice, and G3's M5 row changes accordingly |
| D1 | SATISFIED — every listed production appears in the dump: `tag`/`oracle` as columns or rows, provenance's nine keys in `#section provenance`, `variant` in `#section variants`, `mc`/`under`/subject id + hash in `#section cases` (§2.24) |
| D2 | SATISFIED — the loader reads only the dump; the cases section is what makes that possible under Option A (expectations are in the file, so they must be at the seam) |
| D3 | SATISFIED — one escape vocabulary, documented; NOTE for their loader: the dump escapes the FIVE TSV-framing escapes (`rxt_format.md`'s r46sem-22 paragraph), with `\f`/`\v` arriving as `\xNN` and a literal `"` unescaped — decode against the dump's table, not the subject table |
| D4 | SATISFIED — the VALIDATES vs RECOGNISES table becomes NORMATIVE spec text (SW11; substance in §2.24), and the case-line silent-pass observation is retired |
| D5 | SATISFIED WITH A PRECISION — a no-new-production file emits no `#section` line; its stream differs from the current pin ONLY in the header row's appended columns, which is `table_contract.md`'s own compatible evolution. Their pass criterion "output unchanged" should read "unchanged under name-resolved comparison"; a byte-diff will show the header. Same precision applies to G3 below |
| E1, E2 | BENCH-SIDE (their id/slug containment; their M11 finding is theirs to fix) — the format's half is the wide name grammar, BUILT |
| E3 | SATISFIED — `as <id>` gives every expectation and report row a line-number-independent key (§2.18) |
| E4 | SATISFIED (regression guard) — duplicate block names stay refused |
| E5 | FORMAT HALF SATISFIED (`under`, §2.17); the harness half is the bench's own, exactly as their row states (R5 B1); pcrec's harness counts `under` lines as labelled skips and their runner scores them |
| E6, E7 | BENCH-SIDE — `make check-harness` enumeration and `content_hash` coverage are their gates; the format contributes the closure being enumerable (`--list-source` + include resolution) and nothing else is asked of it |
| F1 | SATISFIED — the permanence SENTENCE lands (SW5); the parse already worked (their M12) |
| F2 | SATISFIED — under `configs describe` a set's config cannot reach any pcrec build (refused for `target … with`, inert for everything else, §2.20): "the command line wins, or the file is refused" — the design delivers BOTH arms, by construction rather than by precedence |
| F3, F4 | BENCH-SIDE gates (their no-build-directives `make check`, their AR-6 review); the format's contribution is that a planted `engine vm` in a `describe` file is still a legal line the gate must catch — their gate, unchanged |
| G1 | SATISFIED — R-COMPAT-1 production by production (§1.3's closing paragraph): every addition is a fresh token (census 0, §0.6), an extension of a refused production, or new syntax at a today-hard-error position. pcrec's own `make test` green is the delivery bar as always |
| G2 | SATISFIED — the five committed exports round-trip unchanged (no existing production moved); whether the exporter ADOPTS `as`/`sha256` is the bench's call |
| G3 | AS THE CHARTER PREDICTS, WITH THE D5 PRECISION: **M1 changes** (STEP 0's refusal — their first-ranked item), **M5 changes** (STEP 0's refusal), **M10 changes** (the W23 keywords stop being refused). M2-M4, M6-M9, M11-M13: the FACTS are unchanged (byte-exactness, trims, acceptance, refusals, exit codes) — but any probe that archives a successful dump verbatim will show the header row's appended columns and, for case-bearing fixtures, the new `#section cases` rows. The probe script should diff name-resolved (or the archive is re-baselined once, at the delivery, with this paragraph as the cited reason). Any OTHER movement is a finding, exactly as they wrote |
