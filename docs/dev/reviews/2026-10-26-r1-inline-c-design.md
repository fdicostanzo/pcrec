# 2026-10-26 rN: inline-c (design), docs/design/inline_c.md rev 0

This is a DRAFT by the round coordinator. Every disposition is PROPOSED; the manager rules them.
In a design round, FIX-NOW means "edit the note (rev 1) before any build go", not a code fix lane.

## Subject
- docs/design/inline_c.md rev 0 (PROPOSED, lane inlinecdes), frozen at c7522390e (blob 89d919bc; the
  same blob at e84db280c, 362edc976 and main 8f4fd7631). Pattern side of [INLINE-C]: one callout call
  site, two code spellings, the generated function, `verify` mode, the trust gate (opt-in and pins),
  artifact-as-callout, the PCRE2 wrapper, and a staged build plan (6 stages, 4 abi events).
- Inputs (not denied): inline_c_requirements.md (its §8 Q1-Q8 are binding), design_callout_abi.md
  (D38), the spec, src at main. The critics read src and spec at main 8f4fd7631. They ran
  `build/pcrec` on single patterns and wrote their own libpcre2 10.46 / gcc probes in scratch. Nobody
  ran make or a suite. No review worktree was needed.
- Profile: new mechanisms and tables (binding rows, return-table rows, verify eligibility, trust rules,
  tag grammar and end scanner); a caller-facing contract (match_api/rxt_format/cli hunks, the trust
  gate); rulings relied on (Q1-Q8, D38, D36/F7, D26 addendum, D163); a build proposal; measurement
  cards.

## Lenses as run
| lens | model | question | why chosen |
|---|---|---|---|
| premise (PREM) + goals | opus | name every assumption and test it; are the goals ranked and checkable? | new mechanisms resting on claims about today's tree and PCRE2 |
| simulate (SIM) | opus | run the proposed rules against real behaviour (libpcre2 probes, an independent naive backtracker, a scan-end simulator) | the §1.7 reference, the §4.4 proof, the §1.3 view and the §2.3 end rules are all simulable |
| slot tracing (SLOT) + ruling check + sibling of a family + general form/unlocks | opus | trace every slot to its one table; check each ruling's consequences | many tables and slots; heavy reliance on rulings |
| contract + trust (CON) | opus | does the design do what its contract promises for every admitted input class? Attack the trust gate as a pattern-file author | caller-facing contract; trust is goal 1 |
| cost and overlap (COST) + measurement | sonnet | cost, benefit, D77 trigger and D153 overlap for each stage; the measurement standing questions | 6-stage build proposal with measurement cards |
| verifier | sonnet | re-check 25 load-bearing claims (V1-V25) | skill §6 |

## Which lens caught what
- **Answer tier:** six clusters, every one found independently by two or three lenses: reference
  flags, site `ncap`, erasure exactness, slot 0 vs `\K`, `--no-captures`, `verify`+`consume`. SIM
  found each with a probe and PREM by reading the code. SLOT caught the mechanism behind them.
- **Trust tier:** CON alone found the harness laundering (CON-2), the `ext harness` link path (CON-9)
  and Trojan Source in the reviewer's view (CON-5). Three lenses found the `features all` door.
- **Design/family:** SLOT alone named FINISH (D156) and compound U6 as `verify`'s family. It also alone
  found the missed D163 add. 6 Q1 budget ruling, the module-owner split, the INTERNAL comment
  contradiction and the FRAMES escalation. COST independently found the compound overlap and the
  existing `callsite_rows[]`.
- **Cost/need:** COST alone produced the remodel-overlap census, the stage-3/stage-4 D77 challenges and
  the measurement-card critiques. PREM found the pre-registered S475/S496 obligations.
- **Calibration (PROBED-AND-HELD):** SIM's naive backtracker found 0 answer differences over 4,455
  random callout patterns against the reference flags. Its scan-end simulator found 0 counterexamples in
  120,000 cases for `W_PRED` tails, and its sabotage twin found 709 diffs. The §4.4 proof logic holds;
  its premises (clusters 3 and 6) do not.

## Findings (verifier status in brackets)

### Answer tier

- **A1 Reference flags** (PREM-1, SIM-1) [V1 HOLDS]. libpcre2 with `NO_AUTO_POSSESS|NO_START_OPTIMIZE`
  still auto-anchors a leading `(?s).*`. With a start-vetoing callout, `(?s).*(?C)x` on `axbx` gives no
  match, while adding `PCRE2_NO_DOTSTAR_ANCHOR` gives `[1,4)`, which is pcrec's VM answer. §1.7, Goal 2,
  §9.2 and §10 Q1 all name the wrong configuration. **PROPOSED: FIX-NOW.** Use the three flags and
  reword Q1's plain-words text. State how the set was established (a survey of every `PCRE2_NO_*`
  option, not two probes), and add the start-veto case to stage 1's differential. Effort: a paragraph.
  It must land before Q1 goes to Frank, because the question's wording changes.
- **A2 The site's `ncap` hides groups PCRE2 shows** (PREM-2, SIM-2, SLOT-12) [V2 HOLDS].
  `(?:(?C1)(a))+` on `aa`: the second fire shows `capture_top=2, g1=[0,1)`. §1.3's textual rule gives
  `ncap=1`, so a group-1-reading predicate answers differently, and Goal 2's differential is red on a
  supported position. engine_m4.md §3.4 is a design text, not a ruling; D38 item 6 rules a WATERMARK,
  which the lexical constant under-approximates. **PROPOSED: FIX-NOW.** Set `ncap = ngroups + 1` at every
  site (unset pairs read -1, as `capture_top` hides them in PCRE2), and make the readable set
  publish-at-close in callout artifacts only. This also gives A5 one refs definition. Add both SLOT-12
  probe shapes to stage 1. Effort: a paragraph. Cost: more groups publish-at-close, in callout artifacts
  only.
- **A3 Erasure exactness: one stamp read for two languages** (PREM-3, SIM-4, SLOT-3) [V3 HOLDS].
  `mrl_win` = `fit.prefilter && !nfa.erased`. It drives `VM_RESEED "exact"` AND the `prefilter-window`
  prune ceiling, and the emitted hybrid clamps `rx_match_anchored` to `window[0][1]`. A callout erasure
  must be recorded (a vetoing site makes the erased language a strict superset). If it is recorded, §4.3
  row 6 fires always and `scan-end` is dead. If it is not, the ceiling loses vetoed matches: `(?:a|ab)`
  plus a veto at pos 1 on `ab` gives "no match" against the reference `[0,2)`, and this applies to every
  inline callout hybrid stage 4 admits. **PROPOSED: FIX-NOW.** §1.8: every site erasure sets
  `Nfa.erased` (the existing ceiling and reseed stay sound with no edit). `scan-end` gets its own
  exactness fact computed on R (the tail removed). §4.2 step 3's fallback runs with no window ceiling.
  Add a sabotage row "the callout lowering does not set `erased`". Effort: a section edit across
  §1.8/§4.2-§4.4.
- **A4 Slot 0 is `\K`'s live register** (PREM-5, CON-4; SIM-6 for the doc half) [V5, V22 HOLD]. `\K`
  writes `RX_SLOT_WHOLE_START`, and the report reads slot 0 as the `\K` start. §1.2's untrailed
  "stv[0] = attempt start" turns `a\Kb(?C1)c` into `[0,3)` where the answer is `[1,3)`. §1.3's sentence
  "the entry overwrites slot 0 as today" is false: the entry READS slot 0. Separately, pcre2callout(3)
  says `start_match` is `\K`-moved, but 10.46 never moves it. The note matches the binary and says
  neither. **PROPOSED: FIX-NOW.** At the site, save, store, call and restore (still no `rx_ctx` field),
  or refuse `\K`+callout in v1 as a §1.9 row. Add `a\Kb(?C"see")c` to stage 1 with a sabotage row. Add
  one sentence on the manual vs the binary (a D26 addendum case). Effort: a paragraph.
- **A5 `--no-captures`: the marked set is also the KEEP set** (PREM-7, SLOT-2, CON-8) [V7 HOLDS].
  `pcrec_bref_mark`'s set is `--no-captures`' keep set (`br_strip_caps`), so a group the site reads but
  does not enclose is stripped. §4.3 row 5 keys on `NCAPS > 1`, which is 1 under `--no-captures`, so
  `scan-end` builds `ncap=1` while the inline reference sees the group. **PROPOSED: FIX-NOW.** An
  `A_CALLOUT`'s refs are recorded on the node and unioned by `pcrec_bref_mark` like A_BREF/A_VAR/A_CALL
  (with A2: all groups). Row 5 reads the site's fact (some tail site has `ncap > 1`), not the stamp. Add
  a `--no-captures` case to stages 1 and 4 and a sabotage row "callout refs omitted from the marked set".
- **A6 `verify` + `consume` tail** (PREM-13, SIM-3, CON-7) [not run by the verifier: a design reading,
  found independently by three lenses; SIM showed the language fact with a libpcre2 stand-in].
  `c,verify,consume:` is legal, and width-class erasure makes the scan language `R·Σ*`, so `e` is not R's
  end. **PROPOSED: FIX-NOW.** `scan-end`'s scan is R with the tail REMOVED (one rule, which also serves
  A3), or add a `consuming-tail` downgrade row. §4.4 step 2 states its premise. Effort: a paragraph.
- **A7 `RX_G_<name>` under duplicate and non-ASCII names** (SLOT-6, PREM-16b, CON-15) [not verified;
  spec reading of match_api §5.4]. A `(?J)` duplicate name has no single number, and `(?<café>)` makes a
  non-ASCII identifier. **PROPOSED: FIX-NOW** (a row edit). Use an accessor over the existing run-walk
  resolution (`\k<name>`'s), or no macro for duplicate or non-ASCII names, said in §3.2.
- **A8 `code-header` includes precede the matcher** (CON-6, PREM-16d) [not verified; CON quoted the
  emitted identifiers]. A user header's macros or pragmas can rewrite pcrec's own code, and the §3.2
  disjointness check covers stamps only. **PROPOSED: FIX-NOW.** Emit the includes immediately before the
  first segment definition (segments are already last), and widen the check to every macro still live
  at that point, over a corpus. Effort: a sentence.
- **A9 Return rows 9-10 ordering and signedness** (CON-14) [SUSPECTED; the C semantics are certain].
  "Checked before row 1", spelled literally with `ptrdiff_t` against `size_t`, traps on every -1.
  **PROPOSED: FIX-NOW.** Rows 9-10 apply to `ret >= 0` only; give the order and the cast.

### Trust tier

- **T1 `features all` grants code** (PREM-4, SLOT-5, CON-1) [V4 HOLDS]. `all` is the union of every
  registry row's feature, and today `--features all --pattern '(?C)'` already reaches "enabled but not
  implemented". A file's `features all`, a config, or a library caller's `features = "all"` would enable
  `code-c` with no `--allow-code`. Adding `code-c` to the roster would also move `PCREC_FEATURE_MODULES`
  on every `all` artifact (CON-1, D178 add. (a)), which contradicts §8.1's zero movers. **PROPOSED:
  FIX-NOW.** `code-*` modules belong to no feature vocabulary. One GRANT column (`invoker-only`) makes
  `--allow-code` and the options member the only setters. Disclose through `<PREFIX>_CODE`, not the
  module list. Add refusal tests for `all` in a block, a config, a `pcrec` line, the CLI and the library.
- **T2 The harness launders reached code into LOCAL** (CON-2) [V11 HOLDS]. run.sh compiles every block,
  fragment blocks included, as `--pattern` text, which §5.2 calls LOCAL. Under the callouts runner's
  `--allow-code=c`, an unpinned fragment's code compiles, and a stage-3 "unpinned include refused" test
  run through the harness would agree with itself. **PROPOSED: FIX-NOW.** §5.2/§5.7 rule how the harness
  keeps provenance (compile fragment blocks through the FILE path, or pass provenance), or rule that the
  harness refuses code in non-entry files.
- **T3 `ext harness` + `link c` runs C from a pattern file with no opt-in** (CON-9) [V18 HOLDS the rule
  text]. It also contradicts rxt_format §1.12's graduation rule (aux is never acted on). **PROPOSED:
  FIX-NOW.** Either graduate `link` to a real production gated by the same visible opt-in (entry file
  only, a path under the entry's directory), or keep stub linking in the callouts section's runner
  rather than in `.rxt` text.
- **T4 The reviewer's view and the ASCII promise** (CON-5) [V19 HOLDS]. match_api promises an ASCII,
  `-Wbidi-chars`-clean artifact "for any pattern". Verbatim segments break that, `--list-source` passes
  U+202E raw, and §5.6's `--list-callouts` prints decoded code with no escaping rule (the
  CVE-2021-42574 shape). **PROPOSED: FIX-NOW.** Add a spec hunk scoping the ASCII promise, and make
  `--list-callouts` escape or flag non-ASCII and bidi/format characters. Whether to refuse bidi controls
  in segments by default is the manager's call (leaning: refuse, with an opt-in on need).
- **T5 The entry-point population** (PREM-11, CON-12) [PREM probed `--help`: no `--list-*` compiles
  today]. Goal 1's "every `--list-*` that compiles" is the empty set, and read literally it makes
  `--list-callouts` refuse what it exists to show. **PROPOSED: FIX-NOW.** One table with a row per
  pattern-taking mode (writes C: refuses without the opt-in; describes only: parses, emits no C;
  `--list-callouts`: works without the opt-in, escaped). Derive the tests from the CLI's mode list.
- **T6 test-axes reach** (PREM-9) [V9 PARTLY: a compile-REFUSED callouts section turns test-axes RED
  ("UNDOCUMENTED refusal"), not green; a LINK failure gives no dump line on either side and is silent].
  **PROPOSED: FIX-NOW (narrowed).** State how test-axes carries the opt-in and the stub link for the
  callouts section, and require a counted floor of built (non-refused, linked) callouts cases per axis.
- **T7 The same file by two chains; hash the parsed buffer** (CON-17) [SUSPECTED]. **PROPOSED: DOC**
  (two sentences in §5.4/§5.5, or with stage 3 whenever it is scheduled; see D5).

### Design tier

- **D1 `verify` re-derives FINISH and the compound's U6** (SLOT-11, SLOT-16, COST-3; COST-10 adds
  [BREF-SPAN] as a further member) [V13 HOLDS the quoted texts; the duplication argument is the critics'].
  `scan-end` is a FINISH row in D156's vocabulary: veto → FIN3 `verify-at` with an `AT` hand (which is
  A3's no-ceiling requirement), and none-at-s → FIN4. Rows 4 and 6 restate availability and the hand
  kind. compound.md §A.2 already type-checks an external `verify-at` callee as the finisher of
  `locate-then-finish(Q; external verifier)` (U6). This is the third "DFA locates, check at e, VM
  finishes" member (compound clients 7/8). §10a conflict 4 weighs hybrid-row against new-artifact-class
  but not this. **PROPOSED: FIX-NOW in the note** (add reading (c) to conflict 4 and cite D156/U6),
  **then a MANAGER RULING before stage 4 is briefed.** Coordinator leaning: specify `scan-end` as a
  FINISH row on `CR_VM`, so "verify a candidate" keeps one home, and file the compound controller as the
  end state.
- **D2 A second call site** (PREM-14, SLOT-13). §4.2's attempt-loop call contradicts §1.2 and Q2's one
  emitter. **PROPOSED: FIX-NOW.** One emitter parameterised by binding row and view source, with edges
  supplied by the caller, and stage-1 sabotage witnesses reaching both callers. This folds into D1.
- **D3 §1.8 "one rule, every pass"** (PREM-8, SLOT-1, COST-1) [V8 PARTLY: `pcrec_has_bref`/`PF_KIND_BREF`
  and `pcrec_bref_mark` are shared whole-tree facts, but about 65 `case A_BREF` arms in 24 files each
  decide locally; possessify's `bref_first` dereferences the bref's groups]. A_BREF is the wrong analog.
  A `W_PRED` site is a gate (`A_LOOK`-like) and a `W_ANY` site an opaque consumer (`A_VAR`-like), each
  plus capture reading. The width fact has two readers with opposite needs: text/language readers may
  read `W_PRED` as empty, but path-pruning readers (possessify follow, P7) must read every site as
  opaque. **PROPOSED: FIX-NOW** (rewrite §1.8 as a per-kind attribute row with `text_width` and `path`
  columns, A_VAR/A_LOOK as the analogs, and a sabotage row per pass family). A **MANAGER RULING** is also
  needed: A_CALLOUT is [POSS-CTX-TABLE]'s recorded trigger (decision families 8/14). Either build that
  table first, or split stage 1 into 1a (the attribute row, zero-mover, on existing kinds) and 1b (the
  callout), or rule an exemption.
- **D4 Pre-registered callout obligations** (PREM-12) [V10 HOLDS]. emit_dfa.c's conjunct (g) and the
  start-set seek require that "the kind that adds a callout" adds a `PF_KIND_*` bit and declines. S475 and
  S496 ship UNREACHED, and run_ir_listing asserts 0 callouts. **PROPOSED: FIX-NOW** (a stage-1 bullet:
  `PF_KIND_CALLOUT`, decline or retire with the purity argument, re-scope S475/S496, flip the ir_listing
  expectation).
- **D5 Return-table home** (COST-2) [V12 HOLDS]. `callsite_rows[]` already exists in
  src/gen/emit_compound.c ("shared by parts and (when they build) callouts"). Its nomatch row is
  `r == 0` and its reserved row traps `r < 0`, so a callout's -1 would trap. **PROPOSED: FIX-NOW.** §1.6
  names that table as the one home, says where it moves (the shared emit layer) and reconciles the 0/-1
  convention. Add the lift to stage 1's scope with a zero-mover check against the compound's artifacts.
- **D6 The INTERNAL comment** (SLOT-8) [V14 HOLDS]. Every artifact's shared block says a call site
  "traps on" `PCREC_ERR_INTERNAL`, while §4¶10 row 4 and D163 add. 6 Q3 say it propagates. The comment is
  stale against a ruling, which is a PRE-EXISTING defect. **PROPOSED: PLAN** (fix it as its own abi
  event, ahead of or with stage 1) **+ FIX-NOW** (§8.1's "zero movers" says which). Correcting the comment
  is an every-artifact abi event.
- **D7 The module owner has two homes** (SLOT-10) [V17 HOLDS the facts]. There is one `(?C` row (module
  `callouts`), ports may carry no module fact, and the tag decides `code-c`. §2.4's "embedded code alone
  needs no `features callouts`" cannot hold through one row's gate. **PROPOSED: FIX-NOW.** Use ownership
  rows: a second `(?C` row owned by `code-c` with a `recognise` hook on the tag, and `(?{` rows generated
  from §2.2's language table, so the language table is the single source.
- **D8 A callee's FRAMES and the outer tier** (SLOT-4) [V16 HOLDS the wording]. A propagated callee
  FRAMES trips the outer's §10.9 escalation, and §10.9¶6/§4¶4 name an owner. **PROPOSED: FIX-NOW.** Decide
  in §1.6 whether a callee give-up does not escalate, or amend the wording, and add a FRAMES test on a
  tiered outer artifact.
- **D9 The budget ruling is missed** (SLOT-15) [V15 PARTLY: the omission HOLDS]. D163 add. 6 Q1 is "one
  budget meter per exported call; every pcrec-matcher callee charges the caller's meter". The note is
  silent, and §8.1's "rx_ctx unchanged" is silently incompatible with the alignment note's carrier.
  **PROPOSED: FIX-NOW.** Add a §10a entry stating the v1 interim (a fresh budget per fire, fires × budget
  in the spec) and when the meter lands ([IFACE-PUSH]'s session member), or make stage 1 wait for it.
- **D10 The D26 addendum points the other way for Q1** (SLOT-17) [V21 HOLDS]. "A PCRE2 choice the
  standard leaves open is not a bug and pcrec follows PCRE2." **PROPOSED: FIX-NOW.** §1.7 says the
  addendum does not decide this (PCRE2 has two non-bug answers), and §10 Q1 lists it as the force for the
  default-flags alternative. This must land before Q1 goes to Frank.
- **D11 Stage 3 (pins)** (CON-3, COST-7, PREM-6) [V6, V20 HOLD]. In v1, §1.9 refuses every reached
  segment through the CLI, and through the harness reached code is laundered (T2). Row 4 of §5.4 has no
  input that reaches it. The pin spelling duplicates rxt_format §1.6¶7's `sha256 <hex64>`
  (case-insensitive), and §1.6¶8 says "pcrec checks neither". analyze/sha256.c exists, and src/ has no
  hasher. **PROPOSED: FIX-NOW** (reuse §1.6¶7's spelling and case rule, add ¶8 to the hunk list, say where
  the one SHA-256 lives). Also a **MANAGER RULING**: Q5 rules the pin design, not its timing; leaning to
  mark stage 3 "designed, trigger: the first case that lifts §1.9 rows 3/4" (D77).
- **D12 Stage 4 is ahead of need; UC-1b is ineligible** (COST-4, SIM-5; COST-10 [POSTFACT]). UC-1b reads
  four groups, so row 5 downgrades it, and stage 4's flagship test and goal 3b would measure the downgrade.
  [POSTFACT] tier 1 covers the octet case without C. **PROPOSED: MANAGER RULING.** Q4 rules the mode
  ("verify first, before post"), not the schedule. Leaning: keep stage 4 designed and brief it only after
  the D1 ruling and a census of eligible shapes. Name a capture-free UC-1b' as the `scan-end` case and
  keep UC-1b as the row-5 downgrade case.
- **D13 Goals and measurement cards** (PREM-15, COST-5, COST-6, COST-9). Goal 3b has no named twin
  (DFA vs `--engine=vm`), no margin, no A/A source and no consequence of a miss. The inline mode's cost
  has no goal. The stage-2 card compares unlike programs and "decides nothing". Goal 2's population has
  no floor. **PROPOSED: FIX-NOW** (paragraph edits: the twin, an empty-predicate control, a margin, the
  consequence; give the stage-2 card a `--engine=vm` twin with counted fires, or drop it; add a corpus
  floor and the P7-P10 and A1/A2/A4 shapes to goal 2).
- **D14 Remodel overlap and flag bits** (COST-8, SLOT-19) [V23 PARTLY: 7 free bits, not 8, since bit 55
  is the kit's; [IFACE-PUSH] fires at 4 or fewer]. There is no D153 overlap column, and stages 1 and 4
  touch [COMPOUND]/[ENTRY-TABLE], [OPT-REVEND], [DD-11.5], memfn migration and the VM emitter. A
  deny+force axis spends 2 of 7 bits. **PROPOSED: FIX-NOW** (an overlap table in §9 with wait/ride/none;
  make the axis deny-only, as 23 of 44 axes are; state the bit count; say which stages share an abi
  bump).
- **D15 Spec hunks missing** (SLOT-14, CON-11). pattern_language.md, registry.md roster/PC-3,
  ir_listing.md §3.7¶1, match_api §2¶6 (`ncap = 0` everywhere), §1¶6, cli.md roster/namespace row,
  rxt_format §1.1 `lib` row, §1.6¶8, §1.12 and the ASCII paragraph are all missing. `--list-callouts` and
  `_CALLOUTS` duplicate the IR listing's reserved `callouts` section. **PROPOSED: FIX-NOW** (derive §8.2's
  list by grep, D94-style; name the IR `callouts` section as the row source and `--list-callouts` as its
  trust-facing projection).
- **D16 Names and namespace** (SLOT-9, CON-16). `RX_PASS`/`RX_FAIL` are defined only inside segments, so
  bindings cannot use them. A binding named `pcre2__x` collides with the wrapper's helper (CON compiled
  it: a redeclaration error). The wrapper has no home under `-o -`. These are new fixed literals outside
  match_api §1's families. **PROPOSED: FIX-NOW** (a §1 family for callout-artifact fixed literals, define
  RX_PASS/RX_FAIL once, refuse `__` in binding names as a namespace-table row).
- **D17 Malformed `(?C`** (SIM-7) [V25 HOLDS]. Today `(?C256)`, `(?Cx)` and `(?C1x)` answer "requires
  module 'callouts'", a reality-tier misstatement (D26 exact tier). **PROPOSED: FIX-NOW** (a §2.4 row and
  stage-1 tests) **+ PLAN**: the misstatement exists today, so a small parser fix can land independently.
- **D18 `#line` for `pattern-esc`** (PREM-10, CON-10). The value is one source line, so every decoded
  line after the first is mis-attributed, and column padding is wrong for tabs, multibyte characters and
  escapes. **PROPOSED: FIX-NOW** (emit `#line N` before every decoded line, use gcc display columns or no
  padding for escaped text).
- **D19 Unbound binding and bench outcome** (CON-13) [V24 HOLDS the bench row]. An undefined
  `rx_callout_<n>` is a link error by design (D38) and is unstated. `--emit-main` cannot link a binding
  site, and pcrec-bench's `grp-callout` (`ca(?C1)t`) moves from did-not-compile to a link failure.
  **PROPOSED: DOC** (one spec sentence, and `--emit-main` refuses binding sites by name) **+ PLAN** (an
  `[inbox]` note to pcrec-bench at stage-1 landing).
- **D20 Option-scope family** (SLOT-7). `--analysis`, `--measures`, `-p` and now `--allow-code` and the
  module grant are answered by a by-name chain, a span containment and a tail flag. **PROPOSED: PLAN**
  (file a per-option SCOPE row `any | not-config | invoker-only`; T1's GRANT column is its first use).
  Stage 2 may land on today's shape if the note says so.
- **D21 Related rows not cited** (COST-10). [POSTFACT], [BREF-SPAN], [MATCH-EVENTS] (whose trigger asks
  for joint design of the binding surface). **PROPOSED: DOC.**

### Doc tier (one line each; all PROPOSED: DOC)
- PREM-16a: the cost of rows 9-10 is "a few compares, folded for inlined W_PRED", not "one compare".
- PREM-16c: `--list-source` is "as pure as today" (it already resolves include real paths).
- PREM-16f: the artifact's bytes depend on the input path as typed (`#line`), so pin the invocation
  spelling.
- CON-15: the accessors evaluate `n` more than once (use statement expressions); `RX_START` vs
  `RX_CAP_S(0)`; the headline example passes `NULL, -1` when the group is unset (test `RX_CAP_SET`
  first).
- CON-18: composed artifacts must share the encoding, and a mismatch traps.
- CON-19 / SLOT-18a (D174): `_CALLOUT_VERIFY` values name mechanisms; use behaviour names. `_CODE` →
  `_CODE_LANGS`.
- SLOT-18b: a link-level stamp listing the binding names an artifact needs (alignment §3), or say it is
  [IFACE-PUSH]'s.
- SLOT-18c: §5.1 is stricter than Q5's endorsed text on config `pcrec` lines (defensible); list it in
  §10a.
- SLOT-18d: reserve the abort VALUE (-17) in §4¶1 now, as Q6 asked ("reserve a code").
- SLOT-18e: the tagged `(?C` is a PCRE2-accepted spelling with a pcrec meaning; the "pcrec-only = PCRE2
  rejects" rule does not cover it, and the compliance row should say so.
- SIM-6 (with A4): the 10.46 binary vs pcre2callout(3) on `start_match`.

### REJECTED / narrowed
- PREM-9's "agrees vacuously (green)" consequence is REFUTED for the compile-refusal path (V9) and kept
  for the link path (T6).
- SLOT-19's "8 free bits" corrected to 7 (V23). This strengthens the finding.
- SLOT-15's citation of "budget" in §1.6 row 3 was a slip (V15); the omission stands.

## Recommendation: a D27 spec-first test author
The design carries a contract with a high trust stake (goal 1) and a view contract (§1.3/§3.2) that
three lenses broke from reading alone. Recommend a D27 cell author once rev 1 lands, denied src/ and
tests/ and writing from the spec hunks and the requirements' use cases. Probe shapes: the trust gate's
entry-point table, the site view, the return rows. The launcher decides.

## Can the subject proceed?
Not to a build go as rev 0. Proposed path:
1. Rev 1 takes the FIX-NOW edits. Most are paragraph-sized; A3, D1, D3 and the D5/D7 ownership changes
   are section rewrites.
2. Four MANAGER RULINGS before stage briefs: D1 (verify's home), D3 ([POSS-CTX-TABLE] first, a stage-1
   split, or an exemption), D11 (stage 3 timing), D12 (stage 4 timing).
3. Frank's §10 Q1 is asked only after A1 and D10 rewrite it. Q2 (W_PRED default) was not challenged by
   any lens.
Stage 1 (the extern-bound call site) carries most answer-tier items (A2-A5, D3-D8). Stage 2 carries
T1-T5 and A7-A8.

## PROBED-AND-HELD (summary; details in each critic file)
- Opening measured facts: 11/11 (SIM) and 4+3 (PREM) hold.
- §2.3 PCRE2-spelling end rule: 12/12 delimiter cases hold.
- §1.7 against an independent naive backtracker: 4,455 random callout patterns × 2 flag sets, 0 answer
  differences (28 fire-log-only differences per mode, all `^`-auto-anchoring, answer-neutral; the
  stage-1 differential must not compare fire logs).
- §4.4 scan-end, `W_PRED` tails: 0 counterexamples in 120,000 cases (half UTF), with a sabotage twin at
  709 diffs.
- §1.3 site view: 13 shapes hold (publish-at-close, retention, lookaround and atomic cases), with A2 as
  the exception.
- P7, P10 and DT-1.1-1.6 re-oracled as drafted; the §9.3 population arithmetic holds.
- Registry, emitter and spec facts: about 60 checks across PREM/SLOT/COST hold (the `(?C` row,
  `forces_registry`, `VE_CALLOUT` reserved, namespace row 2, `rx_ctx` fields, publish-at-close
  byte-identity for callout-free patterns, `pf_admits` shape, gcc inlining a later-defined static,
  trigraphs under gnu11, macro set disjoint from 85 emitted `RX_*` names, the `RX_CALLOUT_PCRE2` macro
  compiling clean, `#line` with escaped filenames, binding-name path held without the opt-in).

## By-id completeness
- PREM-1 A1, -2 A2, -3 A3, -4 T1, -5 A4, -6 D11, -7 A5, -8 D3, -9 T6, -10 D18, -11 T5, -12 D4, -13 A6,
  -14 D2, -15 D13, -16 a/c/f doc, b A7, d A8, e A4.
- SIM-1 A1, -2 A2, -3 A6, -4 A3, -5 D12, -6 A4/doc, -7 D17.
- SLOT-1 D3, -2 A5, -3 A3, -4 D8, -5 T1, -6 A7, -7 D20, -8 D6, -9 D16, -10 D7, -11 D1, -12 A2, -13 D2,
  -14 D15, -15 D9, -16 D1, -17 D10, -18 a-e doc, -19 D14.
- CON-1 T1, -2 T2, -3 D11, -4 A4, -5 T4, -6 A8, -7 A6, -8 A5, -9 T3, -10 D18, -11 D15, -12 T5, -13 D19,
  -14 A9, -15 A7/doc, -16 D16, -17 T7, -18 doc, -19 doc.
- COST-1 D3, -2 D5, -3 D1, -4 D12, -5 D13, -6 D13, -7 D11, -8 D14, -9 D13, -10 D1/D12/D21.
All 71 critic findings are mapped.

## Lessons for the guide (proposed)
1. **A design sentence of the form "the existing X already does Y" is a premise; grep for X.** Three
   such sentences failed here: "each pass already answers for A_BREF through one predicate" (D3), "the
   return table of §4¶10" (it lives in emit_compound.c with another convention, D5), and "the stamp
   proves the end" (one stamp, two languages, A3). The premise lens caught all three. A design lane
   should name the file and line of every existing mechanism it extends.
2. **A design that adds a node kind inherits pre-registered obligations.** Grep the tree for the
   construct's name in "must decline"/"UNREACHED" comments and sabotage rows (D4: S475/S496).
3. **The simulate lens earns its place on a design whose proof or reference can be run.** An independent
   naive backtracker plus a scan-end simulator turned "the proof is sound" into a counted
   PROBED-AND-HELD, and they isolated the defects to the premises.
4. **Trust designs need a lens that attacks the harness as an entry point,** not only the CLI and
   library (T2, T3).

## MANAGER RULINGS (2026-10-26)

- Every PROPOSED FIX-NOW is ACCEPTED (A1-A9, T1-T6, D1-D5, D7-D11, D13-D18); D6 PLAN + FIX-NOW as proposed; the rest as proposed.
- **A1 / D10 superseded by Frank (2026-10-26):** do NOT match PCRE2 callout behaviour under its optimizations; it is "undocumented". Fire count/order is unspecified; no reference flags (NO_AUTO_POSSESS / NO_START_OPTIMIZE / NO_DOTSTAR_ANCHOR) define pcrec's answer; §1.7 and §10 Q1 rewritten to that ruling (Q1 is answered, not re-asked).
- **D1:** the coordinator's leaning: `scan-end` is a FINISH row on `CR_VM` (D156 vocabulary: veto -> FIN3 `verify-at`, none-at-s -> FIN4), so "verify a candidate" has one home; the compound controller (U6) is filed as the end state. D2 folds in (one emitter).
- **D3:** SPLIT stage 1: 1a = the per-kind attribute row (`text_width`, `path` columns; A_LOOK/A_VAR analogs), zero movers on existing kinds, a sabotage row per pass family; 1b = the callout. This is [POSS-CTX-TABLE]'s trigger met by a general row, not an exemption.
- **D9:** Frank 2026-10-26: each fire counts as a step against the match budget; code cannot read/spend it. Follow D163 add. 6 Q1 (one meter per exported call; callees charge the caller's meter). Rev 1 states whether that needs the meter carrier first; if so, the v1 interim (fresh budget per fire, stated in the spec) is acceptable only as an explicitly temporary row.
- **D11:** stage 3 STAYS a scheduled stage (not trigger-deferred). Frank's Q5 is that code from an included file runs when its include line carries a matching sha; rev 0's §1.9 refusing every reached segment contradicts it. Stage 2 = local only; stage 3 lifts §1.9 rows 3/4 for pinned includes. Reuse rxt_format §1.6¶7's `sha256 <hex64>` spelling and case rule; rev 1 names the ONE SHA-256 home (analyze/ must not link src/: say how the code is shared or why a second copy is acceptable).
- **D12:** stage 4 stays designed; its brief follows the D1 ruling (now made) plus a census of eligible shapes; UC-1b' (capture-free) is the scan-end case, UC-1b the downgrade case.
- **Frank's further rulings for rev 1 (2026-10-26):** default check / `consume` opt-in for ALL callouts incl. named/numbered (`(?C"name,consume")`; numbered declares it in the .rxt); context read-only; FIRING CLASS reported per site in --list-callouts and an optional compiler-checked `once` attribute.
- Process changes 1-4 ACCEPTED (applied to .claude/skills/pcrec-critic/SKILL.md in this commit).
