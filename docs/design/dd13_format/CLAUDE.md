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

- `format_design.md` — **[DD-13b] DESIGN note, REVISION 2 (2026-08-29,
  dd13b lane): post-panel (r44) and post-ruling (D87).** Grammar +
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
- `w1_impl.md` — **[DD-13b.W1] IMPLEMENTATION note, DESIGN-FIRST
  deliverable 1 (2026-08-30, lane w1): NO CODE IS WRITTEN.** How wave 1 of
  `format_design.md` lands: file by file, the composer, the check and
  sabotage plan, the D80 spec deltas, four lane-sized steps with a merge
  after each, and the manager's open questions. It marks a fourth claim
  kind beside MEASURED/CITED/ARGUED — **DECIDED**, six points the format
  note left to the implementer or where the tree contradicts it — and
  four of the six make W1 smaller.
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
  column that already exists, emitted `NULL` at `emit_dfa.c:1192`) are all
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
- `usecases_and_outline.md` — the manager's position paper for Frank (2026-08-28, forty-fourth session): use cases U1-U11, a ten-line-kind outline in three demand-staged waves, three worked files, the directory-vs-grown-file evaluation (verdict: directory = convention, sidecar dropped), and the six rulings the [DD-13b] design note would build under.

Maintenance: update this file when files are added/removed or change
roles.
