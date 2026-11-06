# Review 2026-11-05 r7 — alt_normal_form rev 2 (design, readiness)

DRAFT by the coordinator (crit-altnf3). Dispositions are PROPOSED; the manager rules.

## RULING (manager, 2026-11-05)

Every PROPOSED disposition is ACCEPTED (FIX-NOW list, all text). Verdict accepted: READY WITH LISTED TEXT FIXES for stages 1, 2p and 2b; no answer-level hole. Rev 3 (text only) applies them; no further round — the build go is the owner's after span_pick 1e lands, and the build's CODE critic round re-checks the gates against real output. Process change adopted: COMMON tells critics to create their findings file with its headings as their FIRST action, with the relayed-text fallback if the harness refuses the Write (critic skill §5).

## Subject

- `docs/design/alt_normal_form.md` REV 2 at `129b61a678b53b3881823d9615d6fc9dedcaf759` (merged
  on main as `08eef8b4b`). A build would land on main HEAD; the review tree
  `worktrees/crit-altnf3` was built at `08eef8b4b` (`nice make -j2`, unlocked, rc 0).
- Scope (r4 ruling): readiness of stages **1, 2p, 2b**; fix-induced on rev 2's new mechanisms
  (§3.2 adjacency test, §3.3 procedure, FIX-7 description, SND-2 island set reading, bits
  10/11/44 + the harness-only lever); soundness by literal hand-execution on side-effect
  witnesses. 2a and 3 only where 1/2p/2b text depends on them. Stage 3's covering cube (§13 q5)
  OPEN for the owner, not ruled; no finding depends on its answer.
- Rulings frozen at `08eef8b4b`. **FREEZE DRIFT** (main is now `64ab880aa`): `plan.md`
  [DEC-RUNG] was widened (review 2026-11-05 r6 V17) to a "fact-selected emission + total
  fallback" family whose members include the VM rung ladder and the **alt island/chain**: both
  are stage-1 movers here (RDY-1, SND-1, the rung flips). No finding changes; the island fixes
  below are new members of that family's surface. `docs/design/vlookbehind.md` moved to rev 2
  (`4a0fcc859`); critics read rev 2: nothing in it changes stage 2b's SND-5 (r4) text beyond
  the stale "rev 1" label (RDY-9). No `src/`, `docs/spec/`, `decisions.md` change.

## Lenses as run

| lens | model | question | why chosen |
|---|---|---|---|
| readiness (+ goals, + cost/overlap) | opus | per unit 1/2p/2b: cites hold, gates and witnesses can fail, separable (1e, the shared module), complete readers; overall verdict | the LAST re-check before a build go |
| fix-induced (+ ruling check, + standing: sibling of a family, general form + unlocks) | opus | what each rev 2 mechanism adds (reads, fields, rows, levers), traced in today's code; sibling fields unstated | a re-check of a revised design |
| soundness | opus | hand-execute §3.2/§3.3 literally on side-effect witnesses vs libpcre2 10.46; can each 1/2p/2b sabotage witness fail in both builds | answer identity by proof (a rewrite) |
| simulate | sonnet | implement §3.3/§3.2 from text before reading `altnf_proc.py`; quoted cells; confluence drill; U1b pins; never-picked drill; cost bound | a rule run to a fixpoint and a "reproducible reduction" claim |

Not run: premise (ran in r2), owner criteria (O1-O5 folded into fix-induced's ruling check),
measurement (no new measured quantity in scope beyond U1b, which simulate recomputed).

Delivery: readiness, soundness, simulate ended on lanecheck DONE. The first fix-induced critic
returned no file after one SendMessage (STALLED); a FRESH, narrowed fix-induced critic
(`fixind2`) delivered `FIX-1..8` (the coordinator forgot its DELIVER file, so the coordinator ran
its lanecheck: DONE). Verifier (sonnet) ended DONE.

## Which lens caught what

- Readiness: the two gates a CORRECT stage-1 build turns red (RDY-1 island census, RDY-3 dumps);
  1e not landed and mis-described (RDY-4); 2p's unstated piece domain and missing identity gate
  (RDY-6, RDY-7); the MERGES stamp unit (RDY-2); incomplete reader lists incl. the factor-depth
  limit (RDY-8); P/S minimum run (RDY-10).
- Soundness: the island's set reading is BYPASSED at a spine head, so S-i/S-i2 cannot reach
  (SND-1); S-m dead and the FIX-6 "remainder re-merge" a no-op under M -> P (SND-2); callout
  give-up returns (SND-5); two latent/reading risks (SND-3, SND-4). No answer moves under the
  text read literally with "class node" positions.
- Simulate: every quoted cell and the U1b pins reproduced exactly; non-confluence as stated;
  dead duplicates (SIM-1), the P/S consecutive-only asymmetry (SIM-2), the quadratic mixed-width
  cost (SIM-3), doc points (SIM-4..7).
- Fix-induced: two heads with opposite `A_LOOK` rules in ONE module (FIX-2); width unit per level
  and the `facts -> opt` back-edge becoming a call cycle (FIX-3); the module's home vs
  `src/facts/`'s sealed-IR rule and the combinator-vs-subtree interface (FIX-4); bit 10's false
  statements at stage 1 (FIX-5, = RDY-2/RDY-8 part); the 2a lever invisible to `--emit-facts`
  (FIX-6); unstated sibling fields (FIX-7); the unnamed "alphabet is a parameter" family (FIX-8).

## Findings (consolidated) with PROPOSED dispositions

### Gate or witness wrong on a correct build (stage 1)

| id (lenses) | finding | verified | proposed |
|---|---|---|---|
| **SND-1** (soundness) | `vm_isl_words`'s `A_ALT`/`A_CAT` spine walks step `pcrec_ast_seethru`, which unwraps `A_WCLASS` (`internal.h:2322-2326`), so a class at a spine head (`[éà]1`, or the first branch) is read from its BYTE CHILD, never through the arm stage 1 moves onto the set. After the merge the child is `c3 [a0 a9]` and the island declines: `x(?:[éà]1\|q2\|r3)y` today 1, merged byte spelling 0. S-i's REACH ("1 in both builds") is false in the CORRECT build; S-i and S-i2 cannot fail (the sabotaged arm is never entered); U4's equality red | HOLDS (code + byte-spelled controls; not built) | **FIX-NOW** (text): stage 1 says WHICH walk reads the set (an island-local spine step that stops at `A_WCLASS`; `pcrec_ast_seethru` itself stays, other readers need it); S-i/S-i2 re-picked with the class at a non-head slot (`x(?:1[éà]\|q2\|r3)y`, `x(?:1[éè]\|q2\|r3)y`, measured reach 1 / 0 today) AND kept at the head as the census case |
| **RDY-1** (readiness) | the MERGE itself deletes islands: a bare wide class whose byte child is an alternation (`a[éÉ]b`, `(?i)aéb`, `(?i)xé+y` 2 islands) stops being an island once its boxes merge to one (`a\xc3[\x89\xa9]b` 0). U1's "VM islands: never" row and U4's equality are red on a correct build; the design's own `(?i)xé+y` mover is one | HOLDS (distinct from SND-1) | **FIX-NOW** (text): U1 island row predicts "moves iff lowered to bytes on that axis, the unmerged child is an island the VM admits, and the merge leaves fewer than `VM_ISL_MIN_BRANCHES` boxes"; U4 two-sided against U1; §11's merge row lists bare-class island losses as choice cells with their VM number (only the `-fno-cls-kit` VM axis moves) |
| **RDY-3** (readiness) | B0 part 1 requires `dumps` identity, but stage 1 re-specifies bit 10 and §11 requires its `--list-axes` text to move (`axes_dump.c:629-631`): a correct build is red, or the text stays false | HOLDS | **FIX-NOW**: B0 part 1 adds `--dumps-declared-rows` naming the `altcls-merge` row(s) |

### Witnesses and stamps of 2b

| id | finding | verified | proposed |
|---|---|---|---|
| **SND-2** (soundness; RDY-2 part) | §3.3 literally: `(?:abx\|aby\|abz)q` folds entirely in step M before P runs (`ab[xyz]q`, FACTORED 0, not the predicted 1). In general P's rests can never hold a fold M missed, so the "remainder re-merge" FIX-6 names is a no-op and S-m ("rests not re-run") cannot fail. The re-run DOES serve P/S recursion and M over S's heads: `(?:ab\b\|ad\b)` -> `a[bd]\b` (correct MERGES 1, sabotaged 0) | HOLDS (hand-executed twice) | **FIX-NOW** (text): S-m's witness becomes `(?:ab\b\|ad\b)` (or a nested-trie shape); the FIX-6 sentences (§2.2 (5), §3.3 step 2, 2b movers) re-worded; predicted stamps for `(?:abx\|aby\|abz)q` restated (MERGES per RDY-2's unit, FACTORED 0) |
| **RDY-2** (readiness; FIX-5 part) | `<PREFIX>_ALTCLS_MERGES`'s unit is undefined for the owner: today it counts alternation RUNS (`match_api.md` §6.3.11¶3; `x(?:a\|b\|cd\|e\|f)y` = 2); 2b says "rule-M folds"; stage 1 is silent on whether the lowering's merges count (they would move every multi-box utf8 artifact's stamp; if not, bit 10 denies an activity no stamp records, against D46 / `lib/CLAUDE.md:12`'s do-or-die rule). RDY-2's "S-m still fails" half is REFUTED by SND-2 | PARTLY | **FIX-NOW** (text, one choice): recommended: lowering merges NOT counted, stated in §2.6¶1/§6.3.11¶3 hunks, the lowering's merge observable through program bytes/tables; MERGES = "alternations in which rule M folded at least one branch" (keeps today's reading) |

### Separability, sequencing, completeness

| id | finding | verified | proposed |
|---|---|---|---|
| **RDY-4** (readiness) | span_pick **1e has NOT landed** (last: 1d `39e7b20c5`; 1e not cut). 1e is a KIT unit (T-FRAME/T-FIND renderers, no `MF_SITE_ABI` event, `span_pick.md` 1e row); §4.7's "1e rewrites the window walk in `emit_dfa.c`" is unsupported. The real reason is 1e's REACH-EQUALITY window | HOLDS | **FIX-NOW** (text): §4.7 re-states the fence ("no stage that moves `req_run` or emitted bytes lands inside 1e's window"); the stage-1 brief re-greps at its OWN base; 2p (no emitted movers) is bound only through stage 1; §15 says 1e had not landed |
| **RDY-5 = FIX-1** (readiness, fix-induced) | 2b's adjacency head needs arms §3.5 defers ([REPEAT-RUN], [REQ-LOOKAROUND]): S-h's control `(?:ab\|ax+\|ad)` "head `a x`, passes row 1" is false with today's REP arm (h = 1, row 3 refuses; answer (0,2) either way). If 2b builds a REP head arm in the SHARED module, the run walk (its reader after 2p) gains heads across repeats: run movers both 2b and 2p deny | HOLDS | **FIX-NOW** (text, a choice): recommended (a): 2b's head uses today's arms (REP rmin >= 1 contributes no head); S-h's control re-worded "refused, (0,2) either way"; a REP head waits for [REPEAT-RUN]. Alternative (b): a head-only column the run never reads (then FIX-2 applies doubly) |
| **FIX-2** (fix-induced) | ONE module carries TWO heads with opposite rules: the run's cut head (never descends `A_LOOK`: `req.c:47-52` calls that a soundness rule, a lookbehind's bytes sit before the start) and the owner's through-zero head plus WRITES (which descends lookaround bodies). §3.5 names one head; no sabotage witness plants the leak of the through-head into the run | HOLDS (the soundness sentence is `req.c:59`, not :47-52) | **FIX-NOW** (text): two named head columns (run head; adjacency head) and WRITES, each arm's rule for `A_LOOK`/`A_KRESET`/`A_CTX`/check callouts stated per column; one sabotage witness for the leak (a lookbehind whose bytes would join the run) |
| **FIX-3** (fix-induced) | width columns change UNIT by level (characters at code point, bytes at byte level); `req.c:96-102` names the confusion as a deleted match; reusing `mrl.c`'s widths from the module turns the known `facts -> opt` back-edge into an opt -> facts -> opt call cycle; at altcls's phase `A_CALL`'s cached widths are unset | HOLDS | **FIX-NOW** (text): the unit is the alphabet parameter's symbol, stated; the module computes its own widths (or names the reuse); the `A_CALL` arm is a wall and reads no cached field at code-point level |
| **FIX-4** (fix-induced) | the module's home: `src/facts/CLAUDE.md` says derivations read the SEALED IR; the code-point call is before the E1 seal. And the interface shape (arm combinators req.c's iterative spine walk calls, vs a whole-subtree pure call: O(n^2) on a 20,000-literal spine and a second walk) decides both cost and 2p's "one walk" | HOLDS (doc) | **FIX-NOW** (text): home stated (a `src/facts/` carve-out for node-grain pure functions, or `src/core/`); the module exposes arm combinators; it reads no sealed fact at code-point level |
| **RDY-6 = FIX-7 part** (readiness, fix-induced) | 2p does not state a piece POSITION's domain (exact union set vs cube hull vs cut beyond `pos_set` 2: ι's `{85,99,b9}` differs), its rendering in `facts_listing.md` §4.1.2, whether bit 44 narrows pieces, or whether EMPTY inside a piece is the unit or a cut (2a flips it later) | PARTLY | **FIX-NOW** (text): "a piece position is the exact union SET (D187's form, inert, no member bound), rendered as a set list; bit 44 does not touch pieces; EMPTY in a piece is a cut until 2a, exactly as the single run" (or the hull alternative, stated) |
| **RDY-7** (readiness) | 2p claims zero emitted movers but names no instrument that sees a run/pick/table move that keeps answers | HOLDS | **FIX-NOW**: 2p gate adds B0's emit_sweep identity (every stream, both encodings, corpus + bench) except the declared facts row and `--list-limits` row |
| **RDY-8 + FIX-5** (readiness, fix-induced) | reader lists incomplete: stage 1 re-specifies bit 10 but lists none of its readers (`axes_dump.c:625-643`, `lib/pcrec.h:194-229`, `internal.h:3510-3520`, `lib/CLAUDE.md:12`, `src/opt/CLAUDE.md`, `cli/CLAUDE.md:17`, `run_axes.sh:592-596`, `match_api.md` §6.3.11¶3); 2b misses `axes_dump.c`'s bit-11 text, `run_registry_tests.sh:447-456`, the DD-14 codegen fixture at `MERGES 1`, `scripts/alt_census.py`, `tests/altcls/altcls.rxt`; and the limit `PCREC_MAX_ALTCLS_FACTOR_DEPTH` (`limits.def:173`): THE PROCEDURE recurses on rests and heads and must keep a declared depth bound. 2p's mech list should be a GREP RULE over `req.c`-anchored rows in functions it edits (S466, S451, S456, S1339, ...) | FIX-5 part HOLDS; other lists not re-run | **FIX-NOW** (text): the listed readers per unit; the depth limit kept and re-worded for the procedure; the grep rule for mech rows |
| **SIM-3 = FIX-7 part** (simulate, fix-induced) | §3.3's O(1)-per-fold bound covers same-width writer-free spans only; mixed-width keyword lists stay quadratic (n = 1600: 209k adjacency calls); "computed once per round" goes stale as folds shift slots; code-point positions are unbounded interval lists, so set equality/intersection is O(intervals) | HOLDS | **FIX-NOW** (text): 2b states a declared work bound (a limits row whose value its census sets, over which the owner leaves the list as is: sound, today's form) and the incremental structure; the lane's measured worst case stays |

### Text precision (DOC)

| id | finding | verified | proposed |
|---|---|---|---|
| SND-3 (soundness) | "position" means a class NODE for M/P but the description's head reads through zero-width nodes; a lane borrowing the latter for P's key crosses `\K`/lookaheads and moves answers (`(?:x\Kac\|xab)`, 57/1365) | PARTLY (the literal "class node" text already excludes it) | DOC: one sentence: M/P/S positions are class nodes on the CAT spine; only row 1 reads through zero-width nodes |
| SND-4 (soundness) | row 2 equates group width with consumption; the planned positive-lookaround arm breaks it (`(?:ab\|(?=ad)a\|ad)`: (0,1) vs merged (0,2)) | PARTLY (latent, not reachable at 1/2p/2b) | DOC: row 2 reads CONSUMED min/max width; row 1 reads non-consuming positions only at their offsets |
| SND-5 (soundness) | §3.2's callout argument cites the PURE-callee guarantee, but a give-up return on a fire the merge skips changes the answer (libpcre2: rc -50 vs (0,2)); pcrec already skips fires a backtracking order would make (critic's measurement; not re-run) | HOLDS (libpcre2 half) | DOC: §3.2 states the give-up case; the `match_api.md` §11.6¶1 clarification travels as 2b's spec hunk (D80) |
| SIM-1 (simulate) | an exact duplicate of an earlier effect-free branch is dead whatever lies between, but M absorbs it only when it reaches its head; survivors pollute P/S (`bba\|bb\|bba\|bb` -> `bb(?:a\|\|a\|)`) | HOLDS (answers equal) | DOC: step M gains "identical to an EARLIER effect-free branch: drop" (no reach needed) |
| SIM-2 (simulate) | P/S factor CONSECUTIVE branches only, so a branch that passes the adjacency test still blocks factoring (`frank\|xyz\|fred` unchanged); the never-picked drill holds for M (0/6000) and fails for P/S (~1300/6000) | HOLDS | DOC + PLAN: state the asymmetry now; a move-then-factor rule is a later row with a trigger (a corpus/bench keyword list that loses its trie) |
| RDY-10 (readiness) | P and S on "maximal runs" without a minimum: a run of one gives `K(?:)` and the re-run loops; termination text false for it | HOLDS (text) | DOC: "runs of at least two branches" |
| RDY-9 (readiness) | cite drifts: `vm_det_seq` :1883; `emit_dfa.c:3214` is not the emitter (`emit_altcls_macros` :470); `kindrow.def` is `src/core/`; `pcrec_cube_of` takes an interval list; "flag follows caller effect" has no D-row (home: review 2026-10-29 r3 vmtrail F11); `shapes2.py` path; [VLOOKBEHIND] is rev 2 | not verified (cites) | DOC |
| SIM-4..7 (simulate) | quoted §3.3 arrows mix M-only and {M,P,S} results; width-0 branches never absorbed; "confluent under every order" true of COUNTS only (one fold class differs in FORM), `\p{Nd}`'s 39 is not the best order (38 under 5 orders); S's suffix C and run cut unspecified | not verified (doc) | DOC |
| FIX-6 (fix-induced) | the 2a harness-only lever would be the first harness lever on a CORE FACT; `--emit-facts` never carries harness options (`cli/main.c:3110` with `pin`, no `.harness`), so the lever's effect is invisible where facts are listed | HOLDS | PLAN (2a, out of scope): carried to 2a's census-first brief; §11's count unaffected |
| FIX-7 rest (fix-induced) | the island predicate's budget charges (does the set's canonical split charge the same counter, stop early on `\p{..}`?); WRITES has an "unknown" third state for `A_CALL` | PARTLY (budget item not verified) | DOC (stage 1 / 2b text) |
| FIX-8 (fix-induced) | the description with its alphabet a parameter is the third member of an unnamed "the alphabet/relation is a parameter, every caller states it" family (parse's fold parameter, the exposed `u8_ranges`/`u8_box`, the description); general form: ONE alphabet descriptor (set ops, info, cube_of) beside the encoding descriptor; unlocks [DFA-ALPHA-MERGE] and G-1 on their own triggers; the 2a lever is the first "test-only FACT lever" (general form: `facts.def`'s deny admits a harness source; trigger: a second such change) | n/a (judgment) | NOTED (§3.5 names the family; no row) |

## Per-unit readiness (readiness lens, adjusted for the other lenses)

Precondition for all: **span_pick 1e has not landed** (RDY-4).

| unit | verdict |
|---|---|
| 1 | **READY WITH TEXT FIXES**: SND-1, RDY-1, RDY-3 (each otherwise turns a gate red on a correct build or leaves a witness that cannot fail), RDY-2 (the stamp choice), RDY-8/FIX-5 (bit-10 readers), RDY-4, DOC items |
| 2p | **READY WITH TEXT FIXES**: RDY-6 (piece domain, rendering, EMPTY), RDY-7 (identity gate), FIX-2/FIX-3/FIX-4 (the module it would build first: two heads, width unit, home and combinator interface), RDY-8 (grep rule), RDY-5's choice |
| 2b | **READY WITH TEXT FIXES**: SND-2 (S-m and the FIX-6 wording), RDY-2, RDY-5, FIX-2/3/4 (if it builds the module), RDY-8 (readers + the factor-depth limit), SIM-3 (work bound), RDY-10, SND-3/4/5, SIM-1/2 DOC |

**Overall: READY WITH LISTED TEXT FIXES.** No answer-level hole in the procedure as written
(read with "class node" positions); every FIX-NOW is text. The ones that matter most: SND-1 and
RDY-1 (stage 1's island gates would go red on a correct build, and S-i/S-i2 cannot fail), SND-2
(a dead 2b witness), FIX-2 (the shared module's two heads, the one place a lookbehind's bytes
could leak into a run).

## PROBED-AND-HELD (summary; full lists in each critic file)

- Soundness: the required witnesses under THE PROCEDURE executed literally, each rewrite vs
  libpcre2 over every subject up to length 4-5 (span + every capture): `(?:ab\|a\Kd\|ad)` stays
  (1,2) (0/1365); `(?:ab\|(a)d\|ad)\1?` (0,3) (0/1365); writer deeper, after a zero-width node,
  inside a lookahead, a lookbehind, a negative lookahead: 0 mismatches each; row 1/row 2
  adversarial shapes (longer lookahead body, atomic/nested alternations of different widths,
  `\B`/`^`, lazy/`{0,2}`, empty-able m, duplicate past a writer): all held; P's rests cannot let
  M cross an outer branch; callouts with PASS/FAIL returns: fire counts only. Island set
  predicate at non-head slots equals today's child reading on 9 classes. Witnesses that CAN fail:
  S-a, S-b (name the DFA route; on the VM the class kit reads the set), S-d, S-w, S-h, S-s, S-p
  (fact); S-k only if the sabotage admits a non-class key node.
- Simulate: all ten quoted cells reproduced and exact; 8,906 (list, order, rule set) cases exact
  under every order; non-confluence as stated (15,034/24,672 width-3 lists); U1b pins reproduced
  EXACTLY (Lu 664 -> 67, 105 first-first, the 24-order set {67..105}; Nd 71 -> 39; L 827 -> 330;
  `.` 10 -> 8; python UCD 16.0.0 = `third_party/ucd-16.0.0`); fold classes 1454, count
  order-independent; termination over 54,225 lists; `altnf_proc.py` faithful to the text on M
  (60,000 lists, 0 differences) but models M only (not P/S/re-run/writers), so §3.3's claim that
  it recomputes the review's cells covers the M cells only.
- Readiness: §2.3's cites re-held (no `src/` change since `7ffbd4deb`); altcls/lower_enc/req.c/
  emit_vm/cpset/limits/bits/tuning/match_api/facts_listing cites hold within a line or two; bits:
  58 used, 6 free; mech rows exist; B0 spellings runnable except RDY-3; U1b instrument usable
  (`\p{Nd}` 71 resume frames); witness baselines S-i 1, S-i2 0, `(?i)xé+y` 0x4u/3319 B, S-d
  FACTORED 1, S-m 0/1, S-s 0, K123 (2,3), S-b (0,3), S-a nomatch, S-h (0,1), control (0,2);
  goals G1-G5 ranked and served in order.
- Fix-induced: pass order cites exact; a code-point description IS computable at altcls's phase
  (classes are interval lists, folds already classes, `A_WCLASS` not yet created); `A_LOOK` a leaf
  in altcls; layer direction holds; no axis arm assumes bit 10 leaves utf8 lowering untouched; a
  harness-lever precedent exists (`--harness=pres-window`, an internal arm of `run_axes.sh`).

## By-id completeness

| critic | ids | in this draft |
|---|---|---|
| readiness | RDY-1..10 | all (RDY-5 = FIX-1; RDY-6 with FIX-7; RDY-8 with FIX-5) |
| soundness | SND-1..5 | all |
| simulate | SIM-1..7 | SIM-1, 2, 3 own rows; SIM-4..7 one DOC row |
| fix-induced (fixind2) | FIX-1..8 | all (FIX-1 = RDY-5; FIX-5 with RDY-2/RDY-8; FIX-7 split across RDY-6, SIM-3, its own row) |
| fix-induced (first) | none | STALLED, no file |

## Lessons for the guide (proposed)

1. **A reader moved onto a new record is reached only where the walk HANDS it that node.** SND-1:
   stage 1 moved the island's `A_WCLASS` arm onto the set, but two spine walks unwrap the class
   before the arm sees it, so the design's own witness (class at a spine head) never reached the
   moved arm. Soundness/readiness lens text: "for a reader that MOVES (an arm reads a new record),
   find every path by which the walk reaches that node kind, including see-through helpers, and
   pick the witness on each path".
2. **A rewrite that DELETES a node kind deletes what other passes built on that kind.** RDY-1: the
   merge collapses an alternation into one box, so an island built on that alternation disappears,
   independently of any reader the design moved. Fix-induced lens text: "for a rewrite, list
   every pass that triggers on the node kinds the rewrite removes (an ALT gone means no island,
   no chain, no dispatch), and check the movers table predicts each".
3. **A procedure's witness for step k must be one step k-1 cannot already satisfy.** SND-2: S-m
   targeted P's rests re-run, but M runs first and already folds every such branch. Soundness lens
   text: "for each sabotage witness of a multi-step procedure, execute the CORRECT procedure on it
   and confirm the targeted step does the work".
