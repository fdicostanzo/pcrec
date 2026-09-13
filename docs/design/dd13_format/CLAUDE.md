# docs/design/dd13_format/ — the [DD-13] unified file format design

Design material for plan row [DD-13]: the unified pattern-source / test
file format (compilation manifest + test carrier + pcrec-bench set
format). Process is staged — [DD-13a] requirements, [DD-13b] design,
[DD-13c] adversarial panel — and no parser is written before (c) closes.

## Files

- `frank_inputs.md` — append-only dated log of Frank's requirements,
  rulings-in-direction, and flagged open decisions (the OD-n ledger),
  accumulated ahead of [DD-13a]; the requirements note consumes it.
- `requirements.md` — **[DD-13a] REQUIREMENTS note (2026-08-17, dd13a
  lane), read-only fact-gathering, no grammar proposed.** Enumerates every
  consumer's needs (`.rxt` harness/corpus, [V-E] manifest+finder, [V-F]
  transformer, [V-G] user testing, pcrec-bench sets, D27 machine
  generation, [M4-SUBST] templates) as ID'd requirements (R-RXT-*,
  R-VE-*, R-VF-*, R-VG-*, R-BENCH-*, R-GEN-*, R-SUBST-*), each cited to
  its source. Corpus survey: 54 `.rxt` files, 1,100 pattern blocks,
  9,977 expectation lines across `tests/`, all oracle-verified — the
  evidence behind its "DIALECT, not subset or migration" answer to the
  compatibility question (§9): existing `.rxt` files stay valid and
  unchanged under the new format (R-COMPAT-1), which grows a strict
  superset around them. Carries `frank_inputs.md`'s OD-1..OD-5 ledger
  forward as requirements-with-open-decisions (§11, none resolved), states
  five cross-consumer tensions (§10, notably T-1's interface-vs-
  reference-only-pattern testability question and T-3's pcrec-specific-
  numbering-vs-engine-neutral-bench-expectations question), seven
  anti-requirements (§12, headed by AR-1 — must not force re-verification
  of the existing corpus — and AR-2 — must not add dispatch to the
  D20-protected single-pattern common case), and a five-item "for the
  panel" list (§13) naming its own weakest evidence. Confirms
  `subst_template_design.md` intersects narrowly — one deferred
  template-text field owed to the manifest (D38 Q7), no other coupling.
  Consumed by [DD-13b]; no parser exists yet (D6 panel gate at [DD-13c]
  still applies). **PANELED R27 (2026-08-17,
  `../../dev/reviews/2026-08-17-r27-dd13a.md`): one BLOCKER, all
  dispositions FIX-NOW (one deferred half).** F1 (both critics, both
  three-way confirmed): the note's §7 claimed a `.rxt`/manifest grep over
  `subst_template_design.md` returned three hits when the true count is
  six — the miscount hid §5.5 (a second manifest hook) and, more
  seriously, an unsurveyed §8 "Testing sketch" that works out a full
  `.rxt` substitution-testing extension (`repl`/`s`/`sg`/`serr`), the
  most concrete format-extension prior art in the repo. Fixed: §7
  rewritten with the corrected grep, R-SUBST-3 records the prior art.
  Five majors fixed: R-VE-12 (encoding field, plan.md's own manifest
  field list), R-RXT-10 (`tests/reject/`'s documented perr-can't-say-WHY
  limitation, a previously unsurveyed consumer), Appendix additions for
  [M3.1] chunk-boundary tests and [DD-11]'s newline axis (neither
  forecloseable, neither with a proposed directive), T-6 (per-file
  population accounting vs FILE INCLUDES), and §9's compatibility answer
  reargued with softened confidence (DIALECT still stands — r27b's own
  steelman against it failed — but "import" is shown not to disambiguate
  dialect from migration on its own, with APPROACH.md §8 Q1's "grown
  from .rxt" added as a second, independent corroboration, and the g/gp
  precedent marked categorically flatter than what DD-13 actually needs).
  Six minors/nits fixed: the D26/D27 "gold-plate" citation reworded to
  the brief's own do-not-design instruction (D27 had zero textual
  support anywhere in the repo, raised to MAJOR on a same-day addendum
  after a third sub-review); a footnote on `tests/base/CLAUDE.md`'s
  drifted case-line count (676 quoted vs 679 recounted — the quoted file
  drifted, not this note's arithmetic; left unedited to avoid a conflict
  with a held branch); OD-2's semantic-vs-compile-option tweak split
  marked as this note's own derived distinction, not Frank's; a
  keyword-collision-risk appendix bullet; three citation-location
  corrections (R-VE-1's quote lives in the [DD-13] row, not [V-E]'s;
  R-BENCH-6's is APPROACH §2, not §3; R-VE-8's "measured, never read
  from docs" restored in full); and R-BENCH-1's four-tag grouping
  attributed as the note's own synthesis. One correction IN the note's
  favor: §13's self-critique of R-GEN-1 as "one generator" was itself
  wrong — the panel found four more independent no-forcing-function
  instances (the R22 D27-blinded capture author, plus the possessify/
  rungselect/counterk generated corpora), all using only existing
  directive vocabulary — n=5, not n=1, now recorded in §6 with the
  residual honestly narrowed (all five are flat corpora; none has
  exercised cross-references, config sections, or includes). Fix pass
  landed by the dd13afix lane same day; census and ~45/50 sampled
  citations were independently re-verified and held throughout.

- `format_design.md` — **[DD-13b] DESIGN note, REVISION 3.4
  (2026-09-13, lane w23aux, [DD-13b.W23] STEP 1.4): D99, and it is a
  NARROWING OF WHAT THE FORMAT MEANS rather than a fix round.**
  Frank's ruling (`../../dev/decisions.md` D99) is that the `.rxt`
  file's purpose is DEFINING RX, primarily for pcrec, and that the
  bench being able to use it must not distract from that. **Two
  mechanisms are WITHDRAWN** — `configs describe` (§2.20) and
  `provides` (§2.16) — marked in place with their reasoning rather
  than deleted, taking W23-F1 and W23-F2 out of the Frank queue and
  leaving W23-F4 alone in it; `config … testee`/`option` (N-42, a
  bench SHOULD) leave the wave plan with them. **One production is
  added: §2.27, the AUX production `ext <consumer>`** —
  consumer-namespaced, structurally parsed under S0-S3 so a malformed
  aux block cannot corrupt what follows, and semantically
  UNINTERPRETED: dumped faithfully in a new `#section aux` and read by
  no build, no check and no config resolution, with **the GRADUATION
  RULE stated normatively** (the day pcrec must ACT on something in an
  aux block it graduates to a real production; aux never grows
  semantics in place) and a falsifiable four-clause test for "act on".
  **§0.9 is the revision record and carries THE SECOND-ORDER IMPACT
  TABLE**, which is the deliverable Frank asked to see: 23 rows, 13
  from the manager's seed list and 10 found by the sweep, each
  confirmed or refuted with a citation. **Read four of them first.**
  **S2** is the sharpest: `cross-scope`, a constraint kind admitted at
  3.2, had `provides` as its ONLY customer, so §2.25.3 goes back from
  EIGHT kinds to SEVEN under its own membership rule — the rule cuts
  both ways, and a vocabulary that only ever grows is one whose
  membership rule has stopped being applied. **F2** is the most
  load-bearing re-home: §2.20 rule 4's *"`lib` contributes DEFINITIONS
  ONLY"* clause is INDEPENDENT of describe mode and moves to §2.5's
  include model, because deleting it with its section would have
  silently re-opened a closure question in a different production.
  **F1** is a stale echo the lane FOUND rather than inherited — §8's
  P-Q9 still listed the `pattern`/`pattern-esc` refusal that revision
  3.2 dropped as an empty population, two sections from anywhere the
  3.2 sweep looked, which is §1.6.4's own sixth clause recurring inside
  the revision that wrote it. And **S12 is the one seed row that was
  REFUTED**: `configs` appears nowhere in §1.6's reserved-keyword
  material, so no edit was needed and none was made. Also: §1.6.1a's
  narrowing census is re-derived candidate by candidate and **NO ROW
  MOVES**, on the general rule that *a production that has never
  shipped cannot be narrowed by being removed*; §6.2's worked bench
  file is rewritten with one `ext bench` block replacing three `config`
  blocks; §2.23 states the RESOLUTION RULE CHANGE (a variant's testee
  name is now a free identifier pcrec does not resolve — cross-checking
  is the consumer's tooling's job); §2.25.2 gains `children: tree` as a
  fourth value rather than a carve-out in the unknown-token rule; and
  **Appendix A drafts the bench outbox message** (NOT sent, NOT written
  to the bench repo — the manager owns timing and D78's single-writer
  rule), whose headline for them is that their sixteen-config matrix
  stays theirs and their key names inside `ext` are theirs to choose.
  §7.3 records D99's standing PROCESS lesson: both withdrawn mechanisms
  were presented ready-to-ratify while the needs underneath were marked
  tentative at SOURCE, and a ratification ask must say so.
  **Revision 3.3**
  (2026-09-12, lane w23fix2, [DD-13b.W23] STEP 1.3): the r57 ROUND-2
  FIX ROUND, the last before merge. The round-2 critic found 3.2's
  two schema blockers HOLDING OUTRIGHT and the S3 blocker fix holding
  in DIRECTION while failing end to end on its own axis. **Four of the
  seven findings are one section — §1.2.1 — and each is a rule that
  was stated in prose and pinned by nothing**: S3's trigger gains the
  prose-region-opening kind condition and the TRIMMED value (without
  it, `pattern |`, a legal pattern, becomes a refusal); the COMMENT
  line's structural effect is stated in S1 and S3 — it TERMINATES, as a
  blank does — repairing two measured reject→accept widenings that
  falsified §1.6.1's claim 2, one of which produced an opener with two
  disjoint prose regions that S3's extent rule cannot express; S0's
  BLANK narrows to the EMPTY line and a WHITESPACE-ONLY line is
  declared INERT (dissolving two narrowings and saving the format's
  ONLY paragraph break, the indented whitespace-only separator, since
  r46sem-10 closed the empty-line one); and the structure layer's
  second parameter is stated ONCE as the `value`/`children` PAIR, on
  S-R5's detectability — reading `value` alone would leave a `children`
  corruption with no detector anywhere. Alongside: the NARROWING CENSUS
  is re-scoped to the FORMAT rather than the lane's diff and runs to
  **eleven candidates, seven taken**, two of them marked as landed by
  STEP 0 (lane `rxtnul`); the `cardinality` values for the settings
  kinds are DECIDED in §2.25.2 after measuring each population, which
  is what caught **`budget`** — its one duplicate-line use
  (`tests/harness/giveup.rxt:19-23`) is two different FIELDS and
  deliberate, so it is `accumulate` and not `at-most-one`, while
  `flags`, which the finding's list did not name, joins the six that
  refuse; and §1.1's floor gains the definition that makes 28,943
  re-derivable (eight first-token kinds, `perr` INCLUDED; 28,488
  without it). §9.1 gains four fixtures for the rules that moved.
  **Read §0.8's ROUND 2 block first**, then the 3.2 record below it.
  **Revision 3.2**
  (lane w23fix, [DD-13b.W23] STEP 1.2) was the r57 FIX
  ROUND, and §0.8's main table is its finding-by-finding record for the
  three-critic panel (`../../dev/reviews/2026-09-12-r57-w23-format.md`:
  3 blockers, 14 must-fixes, 12 shoulds, 4 nits, all FIX-NOW). Five
  structural outcomes. **(1) The BLOCK SCALAR was a second, undeclared
  structural device and is now S3 OPAQUE REGIONS** (§1.2.1) — three
  critics converged on it, and the measurement is that inside a
  `description |` body an indented `#` is PROSE and ragged indentation
  is legal (both rc 0 on the shipped binary), neither recoverable from
  S0/S1 as revision 3.1 wrote them. With it, **the structure layer
  states TWO schema parameters** (`opens_group`, `value = prose`), the
  second open-ended by construction, and §1.2.4's marker comparison is
  re-run against that baseline — the marker still loses, on a count-1
  argument corrected from "the error class disappears" to "it
  RELOCATES to the schema layer". **(2) §1.6.1a is THE NARROWING
  CENSUS, a closed list of five, three taken** (the ragged head body,
  TAB indentation refused by name, and the `x_y`-beside-`x-y` collision
  in §2.22's semantics) **and two AVOIDED by S3** — each taken row
  with population / forced-vs-chosen / spec sentence, and §1.6.4 grows
  a FOURTH case for a CHOSEN narrowing plus the duty to sweep the whole
  delivery. Revision 3.1 wrote that standing rule from one finding and
  did not run it. **(3) §2.25.3 goes from five constraint kinds to
  EIGHT** — `cross-scope` (whose deferral in §2.25.4 contradicted a
  production one section earlier), `forbidden-if` (`authored`'s
  must-be-absent half), and `functional-binding` (the subject-`as` id,
  which `unique-by` would have REFUSED on its documented normal
  spelling) — plus `under`'s key tuple given an honest home as parser
  code with its reason, and the completeness claim withdrawn.
  **(4) §2.19's `pattern`/`pattern-esc` both-in-one-block refusal is
  DROPPED**: empty population, because both are block openers and a
  second opener starts a new block (MEASURED). **(5) §2.22 gains the
  `rxt_compose.c:854-864` precedent, the `def_by_name` misname fixed,
  a refuse-before-mapping LENGTH rule (`pcrec_rxt_prefix_from_name`
  truncates silently) and the 128-byte callability bound inherited
  from PCRE2 under D26.** New Frank queue item **W23-F4** (§7.3,
  ready-to-ratify, manager recommends ACCEPT): the repair removes the
  ability to declare a deliberately non-callable definition. Filed
  alongside: **`../../dev/known_issues.md` K57**, the block scalar's
  dedent strip silently deleting content. Revision 3.1's own text
  stands where 3.2 does not touch it, and §5.2a is re-aimed with a
  fifth attack for S3.
  **REVISION 3.1 (2026-09-12,
  lane w23recon, [DD-13b.W23] STEP 1.1): the RECONCILIATION against
  Frank's two 2026-09-12 rulings**, which were issued mid-flight and
  never reached the authoring lane. **§0.7 is its own revision
  record.** The
  internal-consistency ruling rewrites **§1.2 as TWO LAYERS**: a
  context-free STRUCTURE layer (S0 line classes, S1 indentation
  attaches a line to the line above it, S2 a declared two-member
  BLOCK-OPENER set) and a declared SCHEMA layer on top — which
  **DELETES the head/body indentation asymmetry** rather than
  narrowing it (the answer revision 3 gave, and the one the ruling
  names as wrong "because that answer requires a keyword table to find
  structure"). **§1.6 prices the `version` break and DECLINES it**:
  the re-factoring is additive (0 indented lines; every rule change
  moves a hard error between arms; the one widening only accepts
  more), so "if needed" is NO — with the change that WOULD need it
  named and priced (making block grouping structural = re-indenting
  28,943 case lines across 210 files and forking every `.rxt`
  producer), and the keyword RESERVED as one-line insurance. **§1.2.3
  states plainly where today's shipped grammar fails structural
  parseability** — block grouping needs one keyword fact, and the
  alternative is refuted by measurement (only 26% of `pattern` lines
  are blank-preceded). **§1.2.4 designs the visible-marker
  alternative and declines it** on three counts, naming `|` and
  `tag-prose`'s `"` as VALUE-form discriminators — **the `|` half of
  which revision 3.2 WITHDREW: a discriminator that selects a
  multi-line form is also a structure device, and `|` is now S3.**
  **§2.25 designs the SCHEMA** (one `.def` table, the parser
  as its reader through one exhaustive switch, `--list-schema` as the
  registry dump (**3.1 said the sixth; it is the SEVENTH**), five
  constraint kinds each with a named W23
  customer under §2.10's own membership rule (**3.2: EIGHT, and the
  completeness claim withdrawn**), `vocabulary` nested as
  the FILE-declared rows via a `source` column, §2.24's
  VALIDATES-vs-RECOGNISES upgraded from prose to a rendered
  `validated_by` column, four D77 deferrals with triggers (**3.2:
  split into DEFERRED and DECLINED, since one of them had no possible
  trigger**), and the honest limit that legs B and C stay independent
  ON PURPOSE.
  **§2.26 is the OWNERSHIP AUDIT** the second ruling forces — all
  thirteen W23 spellings swept, nine confirmed, **THREE moved**
  (3.1 counted four; the fourth, `description` → `prose-value`, is
  §1.2.5's consequence of the structure-layer re-factoring and not an
  audit move):
  `capable` → `provides` (the pattern side is `tag requires=`, so the
  two ends of one relation must read as a pair), `licence`/
  `licence-note` → `license`/`license-note` (SPDX's own key), the
  `freq` data block's five one-off provenance fields → **the same
  `provenance` record a pattern block uses** (the audit's biggest
  finding: revision 3 shipped TWO provenance vocabularies for one
  idea, `exemplar`≡`source` and `date`≡`retrieved`). Alongside them, a
  pattern block's `description` → `prose-value`, superseding the W1.1
  carve-out (§1.2.5's, not the audit's). Revision 3.1 adds NO
  production, no abi event, and no question to the Frank queue; W23-F3
  is RESOLVED. §3.2 gains H16 and sabotage rows S-R1..S-R4 (**3.2:
  six rows — S-R2 re-homed to a pcrec-side detector, S-R3 re-spelled
  so it fails NOW, S-R4 split into two, and S-R5 added for S3**);
  §3.4 gains SW16/SW17; §5.2a is the panel's shortest attack path
  (**3.2: re-aimed, five items**). **Revision 3 (lane w23design, same
  day, [DD-13b.W23] STEP 1) is the base text: the [B42] absorption.**
  Under Frank's F-Q1 (Tier 1 + Tier 2 as ONE W23 delivery — §1.4 restructured;
  W1 is BUILT) and F-Q2 (multi-line patterns MUST — `pattern-esc`,
  §2.19), absorbs the bench's fifty needs: records with attached
  children (§1.2.6; customers `provenance` §2.14 and the reshaped
  `variant` §2.23),
  `vocabulary` closed sets (§2.15), `provides` fail-closed (§2.16, Frank
  ratifies), `under` convention-scoped expectations (§2.17), subject
  `as`/`sha256` (§2.18), `configs describe` closing the D93 roadblock
  (§2.20, Frank ratifies), the `mc` counting rule MEASURED three ways —
  the pre-ruled bench formula double-counts an empty match found beyond
  the scan position; the spec states `match_api.md` §3.1's protocol
  instead (§2.21) — the §4.5-item-4 regime repair via the composer's
  derived-identifier lookup (§2.22, `pcrec_rxt_prefix_from_name`'s one
  home, collision refused at use), and `--list-source` sections +
  case rows + the normative VALIDATES-vs-RECOGNISES table (§2.24). §0.6
  is the need-keyed revision record, §3.4's SW1-SW15 the D80 spec-delta
  plan (no abi event anywhere in W23), §7.3 the Frank queue (W23-F1/F2/
  F3), §8 the nine P-Q dispositions, §9 the 41-check acceptance mapping
  (G3: M1/M5/M10 change, everything else's FACTS unchanged, one named
  header-column precision). Revision 2 (2026-08-29, dd13b lane,
  post-r44, post-D87) is the base text and stands where W23 does not
  touch it. Grammar +
  semantics of the grown format, under Frank's 2026-08-28 rulings
  (`usecases_and_outline.md` §5/§6.1-§6.5) and **D87**. §0.5 is a
  finding-by-finding disposition table for all of r44
  (`../../dev/reviews/2026-08-29-r44-dd13b-format.md`: 2 blockers, 2
  blocker-leaning, 12 majors) — read it first. §1 grammar: a HEAD
  (seven file-level declarations, `config` and data blocks) above the
  BODY of pattern blocks; **in the head, indentation means
  CONTINUATION** (measured free: 0 leading-whitespace lines in 179
  files), which is what carries Frank's `description` field and its
  YAML-style `|` block scalar — the one exception to one-line-one-value.
  §1.5 the three PATTERN-level extensions D87 needs, each with its
  free-ness measured. §2 semantics, §2.3 rewritten: **composition is an
  AST-level operation INSIDE pcrec** (D87) over ASSIGNED group numbers,
  lexical scope wins in both directions, injected definitions are
  name-qualified, and the harness's textual EXPAND is demoted to the
  **oracle control** on the population where it is valid. §2.13 the
  struct view (D87 rules 5/6; consumer is **[V-I]**, plan.md:737). §3
  migration (H1-H11, S1-S11). §4 the seams. §5 the attack list, six
  tensions, seven anti-requirements, OD-1..OD-6. §6 five worked files.
  §7 six questions, one of them new.
  **MEASURED THIS REVISION, on BOTH oracles (libpcre2 10.46 via ctypes
  AND pcrec + driver.c; they agreed on every cell):** the naive textual
  append INVERTS a library piece — `(\d)\1` matches `77`/rejects `75`
  alone, and composed into `^(\d)-(?&dd)$` rejects `5-77` and matches
  `5-75` — and **re-basing `\1` to `\3` per D87 rule 7(i) restores the
  piece's own meaning**; the `(?J)` name collision likewise inverts and
  **internal name qualification restores it**; and of ten candidate
  spellings for the three new constructs, nine are refused by PCRE2 today
  while **`(?<from>&email)` — the leading shape offered for the
  delivering-call declaration — COMPILES**, matching the literal
  `&email`, so it is DISQUALIFIED and §1.5 recommends `(?&from=email)` /
  `(?&=email)` instead. Also re-measured: 177 of 179 files have several
  blocks and exactly two have one (M11); the 26,691 expectation lines
  partition 22,125 + 4,182 + 384 (G2). Syntax recommendations (the
  manager's call per Frank's 14:5x ruling): `(?<3>…)` / `(?<name=3>…)`
  for numbered groups, `(?&^.name)` for the caller scope, `(?&site=name)`
  / `(?&=name)` for a delivering call, `--emit-composed` for the
  serialization. Panel gate satisfied for this round; NO PARSER IS
  WRITTEN.
- `w1_impl.md` — **[DD-13b.W1] IMPLEMENTATION note, REVISION 2.4 — DESIGN PHASE COMPLETE (2026-08-30,
  lane w1): post-panel (r45), post-all three re-checks, post-rulings and post-correction. NO CODE IS WRITTEN.** How
  wave 1 of `format_design.md` lands: file by file, the composer, the
  check and sabotage plan, the D80 spec deltas, four lane-sized steps with
  a merge after each, and the open questions. It marks a fourth claim kind
  beside MEASURED/CITED/ARGUED — **DECIDED**, eight points the format note
  left to the implementer or where the tree contradicts it.
  **§0.4 is the finding-by-finding revision record for r45
  (`../../dev/reviews/2026-08-30-r45-w1-impl.md`: 4 blockers, 6 must-fix)
  — read it first.** The panel's verdict was that the SPINE stands (the
  sub-parse on one `Ctx`, `A_REP{0,0}(A_CAP)` injection, re-basing by a
  walk, and §2.9's provenance argument — r45sem: "the best section; its
  PARSE-1 argument against format_design §2.12 should be adopted") and
  that §2 was NOT buildable as written while §3 "would go green without
  proving the composer". What revision 2 changed, mechanism by mechanism:
  **B1 — delivery is a NAMED DEVIATION from PCRE2, not a free ride.**
  `pcrec_has_live_capture`'s `A_CALL` arm returns false ("a subroutine
  call is CAPTURE-TRANSPARENT") and its `A_REP` arm prunes
  `rmin==rmax==0` — exactly the injection wrapper — so a composed pattern
  whose captures all live in definitions looks capture-DEAD, the DFA takes
  it, and every delivered slot reads `-1,-1`; and even on the VM the `W`
  restore set puts the callee's captures back on return
  (`internal.h:826-849`). PCRE2 agrees — `(?(DEFINE)(?<g>a))(?&g)` is
  CAPTURECOUNT 1 with g1 UNSET — which is why delivery needs TWO named
  mechanisms (a delivering-call live-capture arm, keyed on the CALL and
  never on the wrapper's shape since `atomic.c`'s header forbids the
  DEFINE-shaped special case; and exclusion of the callee's CAPTURE
  indices alone from `W`, the capture-only version of which was refuted
  twice). The two non-deliverable shapes become CALL-GRAPH activation
  bounds rather than lexical repeat depth, which had refused every
  delivering call.
  **B2 — the re-basing walk corrupted caller-scope references**
  (`(?&^.w)` in a definition targets a CALLER group; adding `base` sent it
  into the definition's own space). The walk is keyed on the `PendingRef`,
  caller-scope refs carry a discriminator written at `rc_name_call`, and
  they resolve AFTER the walk. The same fix deletes revision 1's
  `target == 0` carve-out, which was undecidable: the arena zeroes it,
  `(?R)` sets 0 with no pending record, and a deferred cross-definition
  call also reads 0.
  **B3 — `--emit-composed` did not round-trip NAME binding**: explicit
  numbers do not stop `pcrec_bref_resolve`'s name arm re-binding an
  injected `(?&w)` over the whole composed text, which is M2's collision
  reintroduced by the serializer. Injected by-name references now render
  NUMERICALLY; the round-trip claim is restated in its weaker true form
  (modifier leakage across a splice is live — a bare `(?i)` is never
  restored — so each spliced wrapper carries an explicit modifier reset).
  **B4 — `nnames` counting only the primary while `groups[]` held every
  row broke a SHIPPED ABI contract** (`match_api.md:1349` documents
  `nnames` as "entries in groups[]", and §6's caller bsearch walks a name
  run): the sort key becomes (ref-is-NULL, name, number) so the primary's
  rows are a genuine PREFIX, `nnames` keeps its meaning, and a NEW
  `nentries` rides the abi bump.
  On the CHECK side the blocker was that **C0 was empty-vs-empty and its
  validating sabotage row had been silently replaced** — on the corpus the
  composer is never invoked at all, so "closure size 0" is satisfied by a
  composer that is absent. C0 splits into C0a (the invocation count is
  itself asserted) and C0b (the composer's reported closure vs the
  control's RE-DERIVED one — the control now re-derives, reversing
  revision 1); format_design's S-C7 is restored; C1 becomes THREE-WAY via
  `verify_rxt.py --dump`, since the seam ruling leaves the HEAD with only
  one parser and the note now says so plainly; and a new W-8 takes its
  expectation from libpcre2's CAPTURECOUNT/ovector, because W-2/W-5/W-7
  compare the composer to itself and structurally cannot catch a wrong
  assignment.
  **MEASURED for revision 2:** the corpus is 179 files but run.sh
  dispatches 178 — the odd one is `tests/known_fail/k34_leftrec_giveup.rxt`,
  excluded by `run.sh:184-186`'s `-not -path "*/known_fail/*"` — and
  **26,691 − its 11 expectation lines = 26,680, exactly the pinned clean
  baseline**, so C1's and C2's denominators differ on purpose and the
  relationship is derivable rather than a discrepancy. Also: 0 of 26,691
  case lines precede a `pattern` line (so the `have_block` guard the
  manager ruled is free, and its denominators reproduce the format note's
  census to the digit from a third direction), and 3 corpus blocks carry a
  literal tab in their pattern text — all three where the tab IS the thing
  under test, which is what makes `--list-source`'s escape rule a
  correctness constraint rather than plumbing.
  **Its three departures from `format_design.md` are the sections to read
  first, because each is forced by code the note did not cite:**
  (1) **the abi is 12, not 11** — the note's §2.7 says 11 at
  `emit_dfa.c:1310`; `emit_dfa.c:1375`, `run_codegen_tests.sh:2707` and
  `match_api.md:159` all say 12 ([OPT-4] bumped it after the note was
  written), so W1's bump is 12 → 13 and the four D76 sites are re-cited
  exactly, including the (B) pin at `run_recursion_identity.sh:456`.
  (2) **the definition's wrapper TAKES an assigned number, so the oracle
  control's derived offset is ZERO** — reversing the note's §2.3.3
  RECOMMENDED and deleting §2.3.4's offset `j`. `A_CALL.target` is a
  group number and `callgraph.c:162,178` binds by matching
  `A_CAP.u.cap.no`, so a callable body must hold a number in the same
  space every other group is in; a separate id space would be a second
  key in the binder. The composer and the textual control then spend one
  number per definition alike and compare slot for slot, which is a
  better answer to the very hazard §2.3.4 names. It changes a number the
  note publishes (`dd`'s composed group 1 is 3, not 2) and goes to Frank.
  (3) **provenance is NOT a field on the node** — the note's §2.12 says
  it is, and `internal.h:3247` states the opposite as an invariant
  (*"`Ast` carries no position of any kind (PARSE-1)"*, restated at
  `internal.h:729-746` where `A_LOOK.u.look.at` exists BECAUSE of it).
  Provenance is instead a property of the SUB-PARSE (whose offsets are
  already local to the definition's own text) and of the assignment
  table (which is where rule 7(c)'s two sites are known) — strictly less
  machinery and strictly more capable.
  Its central mechanism claim is that **composition adds no new AST
  shape**: a bound definition is injected as `A_REP{0,0}(A_CAP{no}(body))`,
  which is what `(?(DEFINE)…)` already desugars to
  (`mod_recursion.c:418`), so `callgraph.c`'s number-to-`A_CAP` bind, the
  splice/linkage choice, the slot layout and `rx_group_entry.ref` (a
  column that already exists, emitted `NULL` at `emit_dfa.c:1190-1191`) are all
  reused unchanged. The composer itself is a SUB-PARSE on one `Ctx` — save
  and restore `pat`/`patlen`/`pos` plus the numbering scope, so a
  definition is parsed in its own number space and then re-based by a
  walk, which is D87 rule 7(i) executed literally; §2.2 tabulates why each
  saved field is load-bearing (`ncap` most of all: it is read DURING the
  parse for PCRE2's octal-vs-backref rule, `internal.h:1603`).
  `--emit-composed` is a **text splice driven by a position list**, not an
  AST serializer, so no second "AST → PCRE2 text" mechanism is created.
  **MEASURED for this note** (three single compiles under the manager's
  HOLD, `build/pcrec` at main `3372e1e`): all three of §1.5's spellings
  are still refused after [DD-11] landed — `(?<3>a)` and `(?&^.w)` by the
  name-start validator, `(?&from=email)` by "invalid subpattern name" —
  so B1/B2/B3 remain free and each extension displaces exactly one known
  refusal site. Also re-confirmed: 0 corpus lines begin with whitespace.
  §3 re-homes one of the note's own sabotage rows (S-C5 cannot be caught
  by the dump differential, because pcrec never parses `frames-buffer=`)
  and states plainly that S-C8 is caught by nothing on the corpus, since
  no corpus file composes. §6 carries three questions: the wrapper's
  number (above), `(?R)`/`(?0)` inside a bound definition as a SIXTH
  member of §6.0's piece-rule class (recommendation: refuse), and that
  [DD-11]'s table is W1's LISTING interface and not its BINDING one —
  `DefTextFn` splices at the occurrence, i.e. INLINES, and composition
  must produce a call.
  **REVISION 2.1 folds in the r45chk RE-CHECK (F1-F13 all CLOSED; go =
  charter .1 and .2 with ONE condition), and its N1 is the sharpest thing
  in the round.** `tests/harness/verify_rxt.py` — the python-`re` oracle
  that C3 and C1's third leg are specified against — **is executed by
  nothing in `make test`**: the only Makefile mention is a COMMENT
  (`Makefile:528`), and its one real consumer,
  `tests/assertions/verify_pcre2.py` (which imports it as a MODULE so
  "there is exactly one" `.rxt` reader), **has zero Makefile hits either**.
  And its discovery is a ONE-LEVEL glob (`:191`/`:195`, `BASE_DIR` at
  `:20`), which makes the obvious wiring the catastrophic one: MEASURED,
  `verify_rxt.py tests` covers **0 files** and exits reporting success (no
  `.rxt` sits directly in `tests/`), while today's default covers **40 of
  179 files / 3,603 of 26,691 expectation lines — 13.5%**. C3 is the SOLE
  detector for S-C2 and S-C4, and their populations sit mostly outside
  that scope: `# pcre2-only` marks are **571 corpus-wide vs 44 in
  `tests/base`** (7.7% reached), `\x`-bearing lines 171 vs 90. So W1.1
  must WIRE it over a `find`-derived list with a SHORT-LIST HARD FAIL
  ([M5-SEAM]'s shape), pin its verified/skip totals, and derive C3's
  denominator from verify_rxt's OWN discovery rather than carrying
  run.sh's across. **A precision that resolves two disagreeing numbers in
  our own documents**: r44-grammar G1 counts 636 `# pcre2-only` marks and
  the exact count is 571, because G1 matched the line PREFIX while the
  mechanism matches the stripped line EXACTLY (`verify_rxt.py:121`) — so
  the 65 lines with trailing text are ordinary comments to the parser, and
  S-C4's population is the mechanism's 571, not the census's 636. Also in
  2.1: leg B is invoked through run.sh's `$@` branch (the no-arg branch
  yields 178, not 179); the arm-block hash pin becomes BEGIN/END marker
  comments rather than a line range, since W1.1 edits inside `:811-1015`
  and a line-range hash would be broken by the very change it protects;
  and C0a's two assertions are named separately (W1's own invocation
  counter, which shares a source with what it counts, and the independent
  head-bearing-file census, which cannot see a spurious invocation).
  **REVISION 2.2 folds in the r45sem RE-CHECK, whose one open item
  refuted B1's REMEDY while confirming its diagnosis — a scoping
  mismatch, and the sharpest correction of the round.** Revision 2 said
  "exclude the callee's capture indices from `W`". But **`W` is a
  per-REGION property and "delivering" is per CALL SITE** (D87 rule 5):
  `vm_publish_saves` (`emit_vm.c:5716-5735`) indexes `rgn_w[]` by the
  call's TARGET, so every site of one region is handed the SAME save
  array — the exclusion would therefore have applied to non-delivering
  sites of the same definition too, which is precisely the
  called-twice-delivering-once case §2.13 exists for. RULED (manager,
  architecture): **a delivering call is FORCED to `CALL_SPLICE`**, since
  `vm_splice` (`:5915-5985`) allocates `base = v->nsplice` FRESH PER SITE
  — so the exclusion becomes per-site by construction, `cg_eligibility`
  gains one input, and §2.4's table gains a fourth CHANGED row. The two
  non-deliverable refusals (recursion; activation > 1), written for the
  struct's sake, turn out to be the forcing's precondition. Also: the
  restore's index space is the CALLEE REGION's own (`vm_region`,
  `:6036-6046`) with `vm_publish_saves`' *"three readers, one write"* and
  `vm_splice`'s overflow `ctx_fail` (`:5924-5932`, K27's class) as the
  loud detector, and the omission is TRAIL-COHERENT — `vm_set` is
  trailed, so a dropped restore keeps the callee's value and a backtrack
  undoes it, meaning delivery needs one FEWER restore rather than a second
  undo mechanism; the delivering bit lives ON the `A_CALL` node and is
  written explicitly on every call, because the arena zero is the unsound
  direction (`link`'s own situation, `callgraph.c:246`/`:337`); the
  sub-parse's pending list is CAPTURED into the scope record rather than
  overwritten by the restore, making the re-basing TWO passes (a tree walk
  for `A_CAP`, a pass over the captured list); and `match_api.md:1504`
  joins §1.6's `nnames` sentence as a SECOND instance of the same
  staleness shape in one struct's documentation. **NEW §7 is the
  [DD-13b.W1.1] STEP BRIEF** — a seven-item build order with the reason
  each item sits where it does, the acceptance numbers pinned in advance
  with their three different denominators, an eight-point definition of
  green, and two named risks (C1's unmeasured runtime; that wiring a
  previously-dead oracle over 139 never-checked files may surface
  PRE-EXISTING failures, which are a discovery to triage and not a
  regression to fix inside W1.1).
  **NEW: §8 IS THE [DD-13b.W1.3] STEP BRIEF** (2026-09-03, lane w13),
  written under the evening box hold. It is the section to read against
  §2, because **D89 made §2 unbuildable as written**: Frank's Q-W1 ruling
  replaced the one-tier "the definition's groups are injected" with a
  THREE-TIER rule (delivered / hidden / **erased**), and the erased tier —
  a lib group referenced by nothing inside the lib, rewritten to `(?:…)`
  and spending NO number — is not expressible by §2.5's "add `base` to
  every `A_CAP`" walk. §8.0 replaces the offset with a **MAP**
  (`local -> final, or 0`), which is the assignment table §2.7 already
  names as the one derivation with three readers, and which degenerates
  to `+base` exactly when nothing is erased — so §2.5's MEASURED cell
  (`dd` = `(\d)\1`, `\1` -> `\3`) is still the expected answer. §8.0
  also DECIDES the one rule W1.3 invents: **a definition's group is
  delivered exactly when the definition NAMES it**, since D89 point 4
  leaves delivery to "the lib's own names" and every alternative either
  builds W1.4's syntax early or adds a second place an interface is
  declared. §8.2 carries the manager's name-grammar ruling with its one
  real boundary — a `-`/`.` name is buildable as a target but **NOT
  callable from a pattern**, because `(?&some-id)` goes through PCRE2's
  own name grammar and D26 makes that PCRE2's rule; §8.1 records that the
  name grammar has THREE readers found by grep (`rxt_source.c`'s
  `ident_ok`, `run.sh:1492`, `verify_rxt.py`'s `IDENT_RE`) and that C1 is
  what makes them agree. §8.4 is the check plan with the column that
  matters — what each check must NOT share a source with — and seven
  sabotage rows, of which S-W13c and S-W13d are the pair worth keeping
  because they fail in OPPOSITE directions on the same number. §8.5 is
  the six-row D80 delta, including **S9b as D89 revised it** (r45sem's
  "first delivered group at `ngroups+2`" is WITHDRAWN: a caller never
  authors a delivered number, so the spec states delivery in NAMES).
  §8.6/§8.7 are the abi event and its D94 grep. §8.8 carries three
  questions for Frank (Q-W3 every-named-group-is-delivered, Q-W4 a
  definition does not inherit the target's config, Q-W5 `target = <name>`
  rather than an implicit target per named block).
  **REVISION 2.3 CORRECTS THIS NOTE'S OWN ERROR, and the error is worth
  more than the fact it got wrong.** Revision 2.1 reported — truly — that
  `tests/assertions/verify_pcre2.py` has zero Makefile hits, and concluded
  the assertions oracle does not run. **It runs**:
  `tests/assertions/run_assertions_tests.sh:60` invokes it,
  `test-assertions` is in `TEST_SECTIONS` (`Makefile:120`), its discovery
  is a recursive `os.walk` (`verify_pcre2.py:189`), and battery 3's log
  shows it gating the section at 10,120 cells against libpcre2 — because
  **every module's oracle in this tree is invoked one layer down**, from
  its own section script rather than from the Makefile. The grep was a
  sound MEASUREMENT; "therefore dead" was an inference riding on it under
  the same mark. §0.1 now carries the general rule (**a grep count is
  MEASURED; "therefore dead" is BELIEVED until an invocation trace says
  otherwise**) and ties it to the `nnames` staleness as the same failure
  one level over — a true observation with an untested inference welded to
  it. §3.1.1 gains a three-mechanism coverage table (verify_pcre2 over
  `tests/assertions/`, 17 files / 10,274 expectation lines; the
  `# pcre2-only` sweep at `tests/lookaround/run_lookaround_diff.sh:281` as
  a genuine THIRD mechanism; verify_rxt's unwired 40-file default) and a
  new W1.1 step 1b: **the coverage map is established by INVOCATION TRACE
  and is an OUTPUT of W1.1**, never assumed by this note. What still
  stands: verify_rxt's own `main()` is invoked nowhere, its discovery is a
  one-level glob, `verify_rxt.py tests` covers 0 files and exits 0, and
  S-C4's population is the mechanism's 571.
  **REVISION 2.4 closes the §2.8 re-check — verdict STEP .4 IS BUILDABLE,
  the forced `CALL_SPLICE` being the shape the tree explicitly RESERVES —
  and supplies the ACCOUNTING the mechanism needs.** Three corrections
  worth reading: (a) revision 2.2 cited the wrong coupled sites — the
  *"three readers, one write"* triple is the LINKAGE one and **a spliced
  site never reaches it**; the SPLICE triple is `vm_cost:2466`,
  `vm_splice`'s park `:5940` / restore `:5972` loops and the `:7966`
  cross-check. (b) `base` is per-site but `nsave` and the block-SIZING
  pass are per-TARGET, so the capture exclusion must be threaded into
  BOTH as a per-site quantity — under-reservation is loud
  (`vm_splice:5924-5932`, K27's class), over-reservation merely wasteful,
  and `:7966` compares per-REGION totals so it does NOT see a per-site
  divergence. (c) **R3: `exp` is NOT the activation count** — its own
  field comment (`callgraph.c:104`) defines it as expansion *"in AST
  nodes"*, a SIZE, so `exp == 1` would refuse and admit the wrong sites in
  both directions; the activation bound is named as step .4's ONE
  genuinely new mechanism, with the existing data it composes (`site[][]`,
  `reach`, S1's `rmax > 1 || rmax == -1`). The MUST-FIX is that
  `callgraph.c:402-412` ("WHY THE DECISION IS PER TARGET AND NOT PER
  SITE") declined per-site splicing ON PURPOSE and RESERVED it — *"Per-site
  remains available and costs nothing structural: `link` is already a
  per-NODE field"* — so the forced splice is the reserved option being
  taken, and the mixed state that section warns about (one callee with an
  inlined delivering site AND a shared region for its linkage sites) is
  now reachable; the note answers its three named readers
  (`<PREFIX>_VM_CALLS` can no longer give one answer per callee, the
  splice sabotage rows gain two populations, §9.2's `A == B` control must
  accept a mixed target) and records that `rgn_emit[i]` (`:7673`) must
  stay TRUE for the linkage sites, with `vm_call`'s "no emitted region"
  refusal (`:5794-5797`) as the existing loud detector. S2c gains R4's
  semantics sentence: `_SET` is trailed and `_CUT` deliberately is not, so
  a delivering call under an atomic group or possessive quantifier leaves
  the delivered value live after the cut — the same rule ordinary captures
  under a cut already follow.
- `usecases_and_outline.md` — the manager's position paper for Frank (2026-08-28, forty-fourth session): use cases U1-U11, a ten-line-kind outline in three demand-staged waves, three worked files, the directory-vs-grown-file evaluation (verdict: directory = convention, sidecar dropped), and the six rulings the [DD-13b] design note would build under.
- `bench_rxt_needs_v1.md` — **[RECEIVED INPUT, 2026-09-12]**: verbatim
  copy of pcrec-bench's `rxt_needs_v1.md` (their [B42] capability-survey
  lane's feedback note, announced by outbox O-26), under a provenance
  header carrying Frank's two attached rulings (F-Q1 no W2-only first
  sample — Tier 1 AND Tier 2 in one delivery; F-Q2 multi-line patterns
  are a MUST, pattern-esc + the NUL refusal first-delivery scope). Fifty
  needs N-1..N-53, six roadblocks, twelve proposed productions, thirteen
  MEASURED facts at pin d34c9131, a 41-check acceptance checklist the
  bench will run at the restart, and nine P-Q design questions for pcrec.
  The [DD-13b.W23] revision builds against THIS copy; never edit the
  verbatim half — re-fetch and diff on any doubt.

Maintenance: update this file when files are added/removed or change
roles.
