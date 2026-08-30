# docs/reviews — compiled checkpoint critic reviews

One file per checkpoint (D6): the adversarial critic panel's findings, the
triage decision on each, and a reflection. These are the densest source of
"why is it like this" in the project — most of the non-obvious code in src/ and
most of the odd-looking test cases trace to a finding recorded here.

## Files

- **2026-08-09-m1.md** — R1, end of M0/M1.
- **2026-08-09-m2.md** — R2, mid-M2.
- **2026-08-09-m2-close.md** — R3, M2 close. The largest: a live stack
  regression, a 56x compile-time cliff, two holes in guards written the same
  day, and five refuted claims.
- **2026-08-09-sr1-registry.md** — R4, SR-1 (the syntax construct registry).
  Nine rows asserting a PCRE2 semantic that does not exist, a row deletion that
  was invisible to a 116-check suite, a sweep covering two of the four doorways
  it claimed, and a citation of a guard (TS-1) that does not guard what was
  claimed — already copied into two source files before it was caught.
- **2026-08-10-r5-sr2-sr4.md** — R5, the SR-2/SR-3/SR-4 arc. SR-2's
  byte-identity claim HELD under a stronger instrument than the one that made
  it; everything else found was pre-existing, and there was a lot of it. Four
  confirmed bugs (K3–K6), **two of them miscompiles of the exact class the
  charter forbids**, plus a false "this fails the build" claim in three of my
  own comments and a silent hole in my own harness where byte 0x0A became the
  empty string. Two critics converged independently on the class-bracket bugs.
  The most productive question was "which of the branches I just added can no
  test see?" — asked because a sabotage returned zero, and every other bug came
  from pointing it somewhere else.

- **2026-08-10-r7-fix1.md** — R7, FIX-1 (K5/K6, the two brace miscompiles).
  The panel found a THIRD miscompile of the same class in the same function
  (K8, whitespace in `{m,n}`), one space away from all 49 forms the fix had
  been certified against — invisible because those probes compared VERDICTS and
  the bug lives where both engines accept. Also: nothing in the repo asserted an
  error offset, though the code kept per-number state for no other purpose; the
  over-reach guard was tested on one half of a two-sided rule; `{k,k}` did not
  exist anywhere in the suite; the exact-count hazard was measured disarming the
  one row the commit called irreplaceable, in a two-line diff, which is what the
  new MANIFEST answers. Four of my claims were false, one of them a number I had
  inferred from an error message and copied into four files.

- **2026-08-10-r8-pc3-q1.md** — R8, PC-3 and Q1 (the first EXTERNAL check).
  Three of the new instrument's four headline claims failed the same way — a
  control sharing a source with the thing it controls: the "external" candidate
  pool could contribute zero names with nothing failing, the fabrication check
  was defeated by hiding a row's syntax in a PCRE2 comment, and the row check
  never ran pcrec at all. Two real bugs on axes the sweep held fixed (a missing
  magnitude rule, a name-length boundary the candidate cap sat below), a fix
  whose guard scored ZERO until two probe forms were added, and the headline:
  the over-promise Q1 removed at the doorway with ONE row is still open at the
  doorways with 24 and 3, which are 217x and 900x wider. The panel's closing
  report then found a LIVE wrong-module bug — `(?*...)` is the non-atomic
  positive lookahead and was answered "requires module 'modifiers'" — with the
  registry the only one of its three homes that had it wrong.

- **2026-08-10-r9-fix2.md** — R9, FIX-2 (K3/K4 and the class-bracket doorway).
  **The panel that ran a session late**, because FIX-2 was committed before its
  critics could be convened. The split is the point: both critics who attacked
  the RULE confirmed it — one over 1,239,480 generated patterns, one over ~2.4
  billion POSIX-name probes against libpcre2, with the 16-name table
  independently regenerated and found exactly right — while both critics who
  attacked the CHECKS found defects. Undefined behaviour in the new
  differential's one nested-opener shape (a `const char *` read as `%c`), so the
  construct it existed to sweep appeared ZERO times for two of three delimiters
  while the header printed 1680; a `size_t` underflow held safe only by an
  unrelated function's length-check-before-memcmp; a MANIFEST entry hollowed by
  a duplicated row, plus two more duplicates the critic's own inventory missed;
  and three of four counts in a CLAUDE.md contradicting the commit that wrote
  them. The liveness guard added for the first finding **was wrong in the same
  way the finding was** and passed its sabotage until the positive control was
  run.

- **2026-08-11-r10-mod0-design.md** — R10, MOD-0's DESIGN (D29 and the MOD-0
  substeps). **The first panel run against a design rather than an
  implementation, and the cheapest review in the project's history**: comparable
  severity to R9, found before a line was written, every fix an edit to a
  paragraph. D29's spine survived — recogniser-per-row, two ports with two
  signatures, the semantic port recursing into `p_alt`, no allocation in
  recognition. Its central guard did not: "exactly one recogniser may answer"
  FIRES ON A CORRECT REGISTRY, because every tailed bucket has a tail-less
  fallback row whose honest recogniser is "always matches" and two buckets hold
  opposite verdicts; and it is a UNIQUENESS guard traded for the REACHABILITY
  guard it retired, proved on D29's own `-\d+)` collapse, which would have been a
  tier-2 regression. Both proposed controls were the defect they were meant to
  cure — `--explain` never enters a doorway, and module-shipped probes are
  co-location (the drift cure) applied to a circularity problem. The most
  serious finding is D27's own mechanism turned on the designer:
  `src/parse/registry.c:62-72`, dated the day before, says *"Do not design a
  handler signature that assumes it can"* about the exact signature D29
  specifies, and D29 neither cites nor answers it. And "17 tailed rows,
  measured" was 18 — measured by one grep for a macro NAME, missing the one
  tailed row not written through a macro, which was the centrepiece of the
  argument the number supported. The generalisation, sharper than D27 reached:
  D29's three defences were all LIVENESS arguments where every failure this
  project records is a VALUE or SET argument — ask not "does this check run" but
  **"what would have to be true for it to fail, and who chose that input".**
- **2026-08-11-r11-parse1-mod01.md** — R11, two panels in one session:
  PARSE-1's design+implementation and MOD-0.1's design. The PARSE-1 half is
  absorbed into D31; its sharpest finding arrived **after the commit** —
  `p_alt` had no linkage, so the step titled "make `p_alt` a usable module
  callback" had left the callback uncallable, and the rule "re-poll before
  compiling" was applied twice successfully and lost anyway because its
  boundary was the build, not the panel. **A checkpoint is not closed until
  every critic has IDLED.** The MOD-0.1 half REFUTES PARTS OF D30 the way R10
  refuted D29 and is deliberately left unresolved: D30 §2's non-optional check
  ("promise a module wherever libpcre2 DISPATCHES") is false — 93 counterexamples
  in 1,672 probes, ALL of them pcrec being correct, because "dispatched" does not
  imply a module is owed; D30 §3 gets that right and D30 §2 ignores it two
  sections apart. Rank is almost entirely unchecked (20 of 22 rows accept any
  value to 250; the one prefix pair is a single THRESHOLD, not an ordering) and
  two of D30's three required checks fire on identical boundaries in all 5,632
  probes. And the returning-doorway defect is FOUR call sites across three
  doorways, one of which is undefined behaviour: making `pcrec_ext_escape`
  return makes `build/pcrec` itself SIGSEGV on `[a\qb]`, while `a\qb` silently
  launders the pointer out of `%rax`. Of the group-discard class, 7 of 18
  generated patterns are byte-identical to a smaller pattern and 0 of 18 behave
  as the contract promises. Second process finding: a five-part critic brief
  delivered materially worse than a brief with one clear primary item — two of
  four produced only headers.

- **2026-08-11-r12-d32-comparative.md** — R12, a COMPARATIVE design panel on two
  candidate MOD-0 interfaces. **(Listed late: this entry was omitted when the
  file was committed.)** Nothing built. Four lenses, one primary question each —
  and 4 of 4 delivered, against R11's 2 of 4 with five-part briefs, which is the
  measurement that made narrow briefs the standard. The ordered-list design was
  killed on the SHIPPED TABLE with no edit required, trial mode was refuted by
  building it, and a third shape emerged that neither author had proposed. Five
  of the author's claims were refuted.

- **2026-08-11-r13-extension-design.md** — R13, five lenses on the extension
  mechanism design. **The design was partly refuted: eight load-bearing claims
  fell, four to independent measurement by more than one critic.** Selection is
  NOT position-independent (`(a)x12\12` is a backreference, `(a)x12[\12]` is
  still OCTAL); the endpoint rule is decided by the DOORWAY not a shape column
  (`[0-\p{Foo}]` is 147, not 150); `\Q...\E` fits none of the five outcomes and
  the natural reading is a tier-1 miscompile (`^\Qab\E*$` matches "abbb", not
  "ababab"); a NULL class port has at least three meanings. **The checks did
  worst**: 26 findings against ten, two of them the K10 shape the design cites
  as its own template — check 4 is vacuous for ~90 of 100 rows because the
  shared handler IS its own definition, and `RK_VERB`'s single row is
  `REG_SEL_ANY`, so that bucket's coverage is permanently zero. One live bug
  found and recorded (K13, twelve rows). **Two method lessons, both from the
  same session and both about measurement rather than code:** the design's
  position-independence claim was evidenced on the only bucket that could not
  falsify it; and two CORRECT sweeps of `PCRE2_UTF` reached opposite conclusions
  because one generator could not express a ten-character construct — which
  corrected a committed R10 result in D30 §4. *Counting a population by a
  generator that cannot produce it counts the generator.* Third session running
  in which critics delivered substantial material AFTER the commit.

## Conventions

Findings are labelled CONFIRMED (reproduced, with the repro) or SUSPECTED, and
triaged FIX-NOW | PLAN | DOC | REJECTED | NOTED. Every review also carries a
PROBED-AND-HELD list with case counts, because a negative result with evidence
behind it is worth as much as a finding and stops the same ground being
re-covered next time.

Two rules earned the hard way and enforced here:

- **Do not declare a milestone reviewed until the reports are in hand.** R3 was
  compiled as self-audit-only because the panel had not reported; the panel
  then found a live segfault, a hole in a freshly-built guard, and a regression
  five independent nets had missed.
- **Review the artifact a stranger would get, not the working tree.** R1 and R2
  both missed that `.gitignore`'s unanchored `core` had excluded `src/core/`
  from every commit since M0, so a fresh clone did not build. Cloning and
  building is now step 5 of the process critic's brief.

- **2026-08-11-r14-part2.md** — R14, three lenses on the design's PART II
  (the post-ruling redesign), run the same session it was written, ~5,400
  probes. **Part II's two central factual claims were refuted**: §16.2's
  "exactly ONE deviating cell" (the second cell, `[:<:]` low-side 130, was
  printed in the design's own table and read as confirmation; 5,041-pair
  generated differential, 71 disagreements all one item, plus a FIVE-step
  evaluation order the 33 curated cells were blind to) and §14.2's digit
  rule (`\81` is err 115 at any count — the probe set had no run beginning
  8/9). "backrefs can land alone" withdrawn (the count-scan is a
  group-header sub-parser; `(?|` needs the nesting-aware branch scan R13
  used to kill TERMINAL); quote mode is scoped to atom/class-item positions
  (`(\Q?\E:a)` is a CAPTURING group); quantifiability found as a third
  unmodelled per-row axis (`a\b*` is 109 — R13's `\Qab\E*` mechanism on 22+
  rows); three critics independently saved `pcrec_ext_class_pair_opens`
  from its own deletion. C3's verdict on the first §17.3: "an invariant
  with no population, no oracle and no sabotage is not a weaker check — it
  is a sentence." All corrections applied inline marked R14; five decisions
  left for Frank in §18. Method lesson, third instance: the falsifying
  bucket was one probe away, and the fix that worked was feeding the
  predictor from the oracle, never from the row.

- **2026-08-11-r15-mod02.md** — R15, three narrow-brief read-only critics on
  the LANDED MOD-0.2 migration (the design had R10/R11/R12; this attacked
  the implementation). No behavioural divergence found (systematic bucket
  enumeration + live probes). Three findings fixed same-session: the
  registry_check suite had no count/manifest guard in the directory whose
  own docs record why that matters (now mirrored from PC-3, plus a NEGATIVE
  needle — the retired check's PASS line must not reappear); nothing probed
  the `ambiguous` flag over a swept space after the D32 §9.5 scaffold's
  deletion (now the no-ambiguity sweep, 261,193 probes, validated in the
  failing direction); tails-only-at-esc/group was prose discipline (now an
  assertion). One stale-as-current doc fixed (K10's "four nets" named a
  deleted check; the successors' shared blindness is now stated). **The
  sharpest lesson runs the other way**: the checks critic proved two new
  checks blind to winner-swaps and concluded `make test` would pass one —
  measured FALSE in one sabotage build; `check_table_to_parser` (D32 §9.1's
  primary instrument) catches it twice. Verify a critic's consequence claim
  the way you verify your own: run it.

- **2026-08-12-r16-mod03.md** — R16, MOD-0.3 close (module `classes`, the
  first producers). Three narrow-brief critics; every lens landed. The
  checks critic proved the corpus blind to a lower/upper bitmap swap on a
  box without libpcre2 (measured: 43/43 green with the swap live; ten
  discriminating pins added — "a caseless pin is not a pin of the two sets
  it folds together"). The engine critic found a LIVE tier-2 divergence
  the milestone itself made reachable — \N{2,3} refused where PCRE2
  parses a quantifier — fixed with the table's first custom recogniser
  sharing ONE brace-shape scan with try_quant; boundary measured first
  (probe_nbrace.c, 22 cells), floors moved with predictions. The docs
  critic filed seven stale-as-current-fact findings, all fixed, including
  the compliance survey gaining OK-GATED. Also: an engine-critic
  self-reported-and-reverted overreach (the brief discipline working),
  and two wrong cells in critics' own reports corrected by measurement.

- **2026-08-12-r17-mod05.md** — R17, MOD-0.5 close (module `modifiers`).
  Three narrow-brief critics, and a panel first: zero wrong cells in any
  report (every brief demanded both-sides measurement per claim). The
  checks critic found three correct-today-unguarded port corners (the
  a-sub two-homes rule, x-level adjacency/downgrade, unset-wins) — all
  pinned + sabotage rows S24-26, with the failing direction measured by
  running the rows against the unpinned HEAD first. The engine critic
  found bare `(?`-at-EOF answering in the 111 family where PCRE2 gives
  the same 114 bare `(` gets — fixed in ext.c; the Q2-era pin whose prose
  claimed PCRE2 agreement moved with its third measured answer in three
  eras. The docs critic caught tests/modifiers/CLAUDE.md still in the
  pre-landing voice (the R16 failure mode, one module later) + four more,
  all fixed. First adversarial read of the option-run grammar (the
  MOD-0.8 note discharged early).

- **2026-08-12-r18-mod04.md** — R18, MOD-0.4 close (module `verbs`, the
  migration test). Second consecutive clean panel; zero tier-1 divergences.
  Checks → S27's offset-blindness generalized to five more REFUSE families,
  closed with per-family offset pins + S30; engine → the offset-divergence
  inventory (tier 2, no action, with the two counter-cells that DO match the
  oracle now measured) and K15 (the too-long category divergence, a linked
  pair with PC-3's identifier-only length generator); docs → two live-doc
  staleness fixes (the §5.3 location claim had aged through TWO moves) and
  the SR-6 as-built naming correction.

- **2026-08-12-r19-mod06.md** — R19, MOD-0.6 close (module
  `unicode-props`). One tier-2 opened (K16: the `\p{...}` body scanner
  never detects libpcre2's malformed-body-byte class — 164 of 256 body
  bytes; ruled DEFER to first producer), the sweep-template lesson's
  fourth recurrence (three instruments all stopped at the same brace
  boundary), mech's first UNDETECTED rows triaged as
  predictions-misread rather than harness failures, and the
  message-only-pin lesson recurring three lines below a comment citing
  it. Session-shape note: both implementation lanes died mid-flight;
  the manager finished the landings from worktree state.
- **2026-08-12-r20-mod08.md** — R20, MOD-0.8 checkpoint (Q2+SR-9
  option-run surface, MOD-0.7 `--explain`, docs). The option-run grammar
  survived ~513M differential probes unrefuted; the tier-1 was an
  INHERITED precondition nobody re-measured — probe/explain hand ports a
  Ctx with no setjmp, safe only while no port could `ctx_fail`, and the
  first producing port had ended that (`--features modifiers --explain
  '(?i:[)'` → SIGSEGV). Both tier-1s (this and D27's `a(?i)*`
  miscompile) were reached by GENERATION, fixed same session. Origin of
  the differential-gate principle (gate-ON, focused per feature) and the
  carried-forward-comment lesson.
- **2026-08-14-r21-m4-design.md** — R21, the [M4.3] hard gate: three
  critics over BOTH M4 design docs plus the two previously-unpaneled
  ruled inputs. The panel drew blood everywhere it aimed: a LIVE shipped
  miscompile (K17 — DFA loses leftmost-first priority on lazy nullable
  prefix + nested nullable star + outer star; found by executing the
  design's own P-1 probe; 1284 corpus tests and the span-comparing
  fuzzer had missed it on joint-probability rarity), the design's
  empty-guard wrong for bounded repeats (60/225,240 vs libpcre2; 0 with
  guard iff rmax==-1), the Θ(n) frame/trail working set capping capture
  matching at ~2 KB of subject under the thread-stack budget, a measured
  silent-stack-smash hazard in the span array-typedef spelling, and the
  fixed-literal ABI types failing to compile in their own composition
  case. ASK-1's oracle-disagreement prediction REFUTED (python vs PCRE2:
  0/225,240 — the planned exclusion mechanism would have hidden K17;
  replaced by the three-way 2-1-minority rule). Dispositions ratified as
  D44 (+ the D40 working-baseline calibration); fixes applied by the
  r21-fixes lane same day; K17 fixed by its own code lane. Eleven of
  eleven STRUCTURAL citations held; what broke was what was marked
  BELIEVED.

- **2026-08-15-r22-m45d-capture-author.md** — R22, the [M4.5d] D27-blinded
  capture author's cell delivery: 85 m/ms cases + 145 group lines,
  python-derived and twice-verified, 230/230 green against the VM after a
  whole-line comment normalisation — the strongest independent
  capture-correctness evidence in the project. Two contract-text gaps
  (cross-iteration retention; empty-final-iteration overwrite) arbitrated
  three-way UNANIMOUS and recorded as match_api_m4.md §2.2. Also records
  the manager's cell-hygiene slip and the stale mk_d27_cell.sh allowlist
  (still owed). Appendix: 2026-08-15-r22-appendix-author-notes.md (the
  author's own notes, verbatim).
- **2026-08-15-r23-k18-memo.md** — R23, panel on the K18 memo design note.
  The decisive finding (S16): the prototype's `clo_visit` restores the
  open-loop stack's depth but not its entries, and that single bug WAS the
  note's entire cost residual — 44 s at the parser's nesting cap becomes
  0.419 s with a two-line fix — so §6 ruling 1 (the D=64 inexactness
  threshold) was WITHDRAWN rather than put to Frank. Also: `nonstacktop==0`
  refuted on the note's own prototype (358/4,369; the corpus could not
  reach the failure), the cost law posed on the wrong variable (context
  count, not depth — bounded repeats replicate), a fourth K18 sub-case
  (preferred-arm, not laziness; two of the K18 entry's controls are live
  miscompiles with arms swapped), and an invalid-pattern hole in the
  adversarial generator. A2 itself survived every attack: zero cells
  A2-wrong-shipped-right across ~330,000 independent span cells; every
  population count reproduced exactly. Appendix:
  2026-08-15-r23-appendix-critic-findings.md (three lanes' findings,
  verbatim); the semantics critic's toolkit archived at
  docs/design/k18_measurements/r23_semantics/.

- **2026-08-15-r24-eng-brep.md** — R24, panel on the [ENG-BREP] design
  note, run the same session the note was written and merged. The central
  result HELD and was strengthened (the repaired greedy possessification
  rule at 0 counterexamples against libpcre2 too — closing the note's own
  §8 gap from outside — and the transitive-FOLLOW line surviving a
  42,336-pair attack with failing-direction controls); the note's LAZY
  extension was REFUTED (316 cells both oracles; the note's own probe
  structurally skipped every lazy row and nothing said half the question
  was unasked), §3.4's derivation had dropped its zero-iteration clause
  (42% of its own validated population), and every rung-census "distinct"
  figure was an undercount with ONE cause found at fix time — an
  uncommitted `sort -u` under a UTF-8 locale, whose collation merges
  regexes differing only in punctuation. Fixes applied by the note's own
  author lane same session (merge 9c7a257), including the corpus census
  moving 18%→17% under the repaired rule and engine_m4.md §6.3/§6.4 —
  which still stated the refuted rule as "designed, built M4.6" —
  annotated in place both directions. One new upstream row (U9: PCRE2
  10.46 won't backtrack into a preceding item after a possessive bounded
  repeat of a group — python-possessive and PCRE2-possessive are not
  interchangeable oracles). §9 carries SIX rulings for Frank.

- **2026-08-17-r26-k23.md** — R26, panel + same-day verification pass on
  the [M4.6c] K23 design note (MRL pruning). The R25 shape again:
  the soundness ARGUMENT held and was strengthened (the engine critic
  set out to break preference-blindness and instead PROVED it; the
  closed-form step law exact out of sample), while the EMITTED FORM was
  refuted — the §4.1 clamp lands off the iteration lattice on stride>1
  cursor rungs (5/8 subjects wrong on a live-population shape) and the
  855-cell differential was structurally blind to it (single-byte
  corpora; the lane's own §11.1 lesson unapplied to its own generator).
  Lane revision same session: lattice rule in, corpus regenerated with
  stride+residue axes, 1,059 cells / 0 disagreements, and the sabotage
  arm PROVING the blindness (101 red, zero at stride 1). Verification:
  V1-V7, one PARTIAL (a stale sparse table — the carried-number defect
  in the exact cell finding 10(a) had flagged). Panel-contributed
  improvements with provenance: the lattice rule itself, the
  prefilter-window ceiling (ruling 6 to Frank), the ratio-tracking
  python argument. Critic self-disclosures recorded, including R24
  M-F1 reproduced verbatim by the critic's own `sort -u`. Two Frank
  rulings queue: adopt-MRL; prefilter-ceiling v1-vs-fallback.

- **2026-08-17-r27-dd13a.md** — R27, two critics (+ forks) on the
  [DD-13a] format requirements note. The census survived a ~50-point
  re-derivation EXACTLY; the blocker was three-way independently
  confirmed and was the note's own §13-warned failure — an unreproduced
  "grep returns 3 hits" claim (real: 6) hiding subst_template_design.md
  §8.1's repl/s/sg/serr, the most concrete format prior art in the
  repo. One finding ran in the note's FAVOR (R-GEN-1 is n=5, not the
  self-criticized n=1). The DIALECT conclusion survived its own
  steelman. Author fix pass merged same session (4b2e0b7).
- **2026-08-17-r28-mrl-landing.md** — R28, the [M4.6d] LANDING panel
  (three lenses on the delivered branch; the design had R26). Soundness:
  SOUND TO MERGE, six of six claims survived a ~285k-cell independent
  battery including a DFA-engine oracle that terminates where python
  hangs (instrument adopted). Two instrument MAJORS closed before merge:
  MRL had zero sabotage coverage (now S58-S63, all DETECTED), and the
  answer-more exemption's "2 cells" was per-PATTERN reports miscounted
  as cells (real: 22 — now counted, printed, asserted, and refereed
  22/22 by a --no-captures DFA third arm). The panel's best find, from
  two directions independently: the lattice rounding is behaviorally
  DEAD (the folded loop bound is SELF-ROUNDING; the shipped emitter
  cannot express R26 E1), its named guard grepped an argument rather
  than the property, and the actually load-bearing underflow guard's
  removal is an ASan overflow invisible to answer sweeps.

The NOTED list of the most recent review is the honest inventory of what is
still unguarded; read it before starting new work.

Maintenance: add a file per checkpoint and list it here.
- **2026-08-18-r29-match-api-spec.md** — R29, the D6 panel over
  docs/spec/match_api.md (the first spec document, [M4.7f]), riding the
  [M4.7g] close. Three lenses (artifact / ruled-corpus / adversarial
  consumer). Matching semantics held everywhere (§5, §5.1, anchoring,
  composition, §7 truncation — span-for-span vs python re, both
  engines); the blockers were all in the surrounding surface: BOTH
  shipped doc-comments (emitted rx_matchfn block + lib/pcrec.h searcher
  comment) affirmatively deny the give-up-code space §4 promises and
  the artifacts produce (−2/−3 measured); §2 quoted a corrected comment
  as if shipped; §8's calling sequence cannot compile a pattern
  (pcrec_default_options and pcrec_output/_free absent); §3.1's
  find-all instruction is an infinite loop on empty-matching patterns.
  Panel-vs-manager-read lesson: the manager's end-to-end read checked
  the spec against its own citations; the critics checked it against
  alphabets the document didn't choose. A7 adds a DOCUMENTATION
  instance to the controls-share-a-source catalogue (evidence quoted
  from the engine where the claimed branch is unreachable). Fix pass:
  lane/m47g-fix.
- `2026-08-25-r35-wave-g-panel.md` — [DD-14] WAVE G pre-merge critic panel
  (lane/srG at 2219dda): critG-engine (opus) + critG-checks (sonnet), both
  read-only. E1 BLOCKS: a spliced target reaching a LINKED target overflows
  the splice save block — two computations of |W| (`spl_nw` vs `rgn_nw`)
  from two mechanisms, and the corpus had ZERO artifacts with both linkages
  (113 spliced-only, 37 linked-only), so every bar was structurally blind;
  the lesson is a MISSING CELL, not a missing assertion. Three riders
  (false pass-reorder argument, a false `--emit-ir` diagnostic, a stale
  emit_dfa.c comment), four check fixes already landed by the lane. Held:
  the narrowed-W nesting theorem under four constructions, nfa.c exactness
  against a hand-inlined python oracle, elision partial-on-DFA impossible.
- `2026-08-25-r36-frame-buffer-code-panel.md` — [DD-14.FB] CODE-HALF pre-merge
  critic panel (lane/srFBc 79873cb → rebased 454c5b0): critFB-engine
  (opus) + critFB-checks (sonnet), read-only. Skeleton committed before
  the reports; findings and dispositions filled as they arrive.
- `2026-08-28-r39-optk-design.md` — [OPT-K] DESIGN-NOTE panel (lane/optk
  d13f5be, before the emitter side): critic-sem (opus) + critic-cost +
  critic-arch (sonnet), read-only. Skeleton with two lenses' findings
  and dispositions committed first; the semantics lens appended on arrival.
- `2026-08-30-r46-w11-impl.md` — panel on the [DD-13b.W1.1] MERGE (r46sem opus / r46chk sonnet, during battery 4): 1 BLOCKER (leg B's escape emits the table index, not the byte), 8 must-fixes, the 'agree on the corpus, diverge outside it' class; triage table → fix lane w11f.
