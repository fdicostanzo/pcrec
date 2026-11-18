# Lane archlook: the [REQ-LOOKAROUND] architecture note ([ARCH-STEP] pilot)

Lane archlook (opus, 2026-11-18). Documents only: no `src/`, `cli/`, `lib/`, `memfn/`, `tests/`,
`scripts/` edit, no `make`, no queue job. Written by following
`.claude/skills/pcrec-architect/SKILL.md` §3-§6 as written.

## STATE AT HANDOFF

- STATE: done. Branch `lane/archlook`, cut from main `57fcb5737`.
- T (the frozen tree every command in the note runs against): `57fcb5737dff37bd97429fb1e889ca0233d12e10`.
- The note: `docs/design/req_lookaround_arch.md` (STATUS DRAFT; for the `pcrec-critic` ARCHITECTURE round, never reviewed by its writer).
- Also changed: `docs/design/CLAUDE.md` (one file-list clause; the file is at 12,267 of its 12,288 bytes, so the neighbouring clause was shortened to make room), `docs/dev/history/claude_md/docs__dev__lanes.md` (the history index line).
- Rulings file `docs/dev/lanes/archlook_rulings.md`: empty at every check; last ruling applied: none.
- OWED: none.
- The register was NOT edited (rows are PROPOSED in the note, P1-P5).

## FORM AND SITE COUNT

- FORM: full. Trigger: 11 existing decision sites touched (T3's E-5 row, `rr_alt_rows`, the run choice/TOP entry, the walk-parameter table, `walk_arms.def`, `facts.def`, the K sentinel tests, `cand_rows[]`'s `handoff-attempts-entry` predicate, the landmark move, `req_byte`'s pick, the run pin); mechanisms added: the pending guards with their CAT/ALT rows (T4), the TOP stage, the ITEM combinator (D168's item half), the consumed extent, the `req_run_omin` row, two walk parameters, the dead value.
- Site map: 28 rows. Classes (sites 12 and 18 carry two): ROW 6, AS-IS 11 (several with a stated constraint), WIDEN 3, SHARED 5, ACCESSOR 3, NEW-SEAM 2.
- Remodels that land first (each answer-identical, emitted bytes identical, size S):
  - RM-1 every `RbRuns` builder starts from a stated value (`rr_cat`, `rr_alt` build `RbRuns o;` field by field today): before L1.
  - RM-2 the landmark K carries a stated/none state instead of the −1 sentinel, one "stated and bounded" predicate for its three hand tests: before L3.
  - RM-3 one emitter of the landmark move `max(pos, hit − K)` (two copies today, both assuming the hit is never behind the position): before L3.
  - RM-4 pcrec's own scan member of the run asked once (two copies of the expression today), the consumed extent through one accessor (read by the pick and the run pin): before L2 or L3.
  - RM-5 a read accessor for `Ctx.lb_max` (register row 6a, narrowed to one field): before L3.
- Main findings beyond the shape (the note's "Findings for the manager"): span_arms is rev 2.2, not rev 1 as the plan row and brief say; D191 already gave the build go for L1 and L3 (2026-11-09); span_arms §8.2's kit request is DELIVERED (R-38 K38-2, MF_SITE_ABI 27) in §12a's end-state form; the margin fix READY3-2 is already in the tree; D168's ruled home (the span slice) was deleted by [COVER-CAP] stage 1, so the lookaround item becomes the first AST-level context producer; span_arms' `dead` why token would be a second answer to the existing `never_matches` fact.

## REGISTER ROWS PROPOSED

| # | remodel | carried by |
|---|---|---|
| P1 | Every `RbRuns` builder starts from a stated value | RM-1, L1 |
| P2 | K as a stated value with one "stated and bounded" predicate | RM-2, L3 |
| P3 | One emitter of the landmark move | RM-3, L3 (A-POSDOM inherits one site) |
| P4 | pcrec's own scan member of the run asked once; the consumed extent through one accessor | RM-4, L2 or L3 |
| P5 | One per-offset-head primitive for the description (the adjacency head `PdHead` vs the lookahead item), or the reason for two | open; trigger: a third reader ([REWRITE-ADJ]'s first build or [LOOK-LOCATE]) |

Existing rows: 6a RIDES FIRST (narrowed to `lb_max`, RM-5); 14 is DONE (stage 3 landed 2026-11-14; its status line is stale); 1, 2, 4, 5, 6b, 6c (noted deviation, `req_handoff_vm`), 7a, 7b, 9, 10, 12 (A-POSDOM not carried by the owner's ruling D191.3), 13, 15, 16, 19 are NOT CARRIED, each with its reason in the note. Register corrections for the manager: row 14's status; row 14's cite (`case A_LOOK` is `rb_walk_at`'s, not `rr_cat`'s); row 7a's trigger wording; row 19's WHERE omits `RB_ROW_SCAN`; row 10's note (the kit's window spans stop at −8, `MF_MAX_BACK`).

## OPEN QUESTIONS FOR THE OWNER

1. **context-producer-home** — D168 (owner, 2026-10-18) says the fixed bytes of a lookbehind and similar context facts come from ONE producer, in the span slice. [COVER-CAP] stage 1 deleted that slice; the cover now gets its context from the anchored machine. Current behaviour: `(?<=foo)bar` states nothing about `foo` at −3..−1; its required run is `bar` (`626172@0`). Is the lookaround item (built by L1 from the lookaround body's fixed-width description) D168's producer for every AST-level reader, with the cover keeping the machine's context (two producers by layer), or must the cover read the item too? Leaning: by layer, recorded as the D168 addendum L1 files.
2. **remodel-go** — Does the build go of 2026-11-09 (D191: L1, L3) cover the five small no-change refactors that land first, or does each need its own go? Example: after RM-3, `(?<=foo)bar(\w)\1` compiles to identical C; today the two copies of the move both assume the landmark is never before the search position, which a lookbehind run breaks. Leaning: they ride as the needing lane's first commits, each gated by byte identity.

## SKILL FRICTION

Places where `.claude/skills/pcrec-architect/SKILL.md` or `docs/dev/guide/architecture.md` was unclear, wrong or missing something, met while following them (neither edited):

1. NEWER RULINGS SUPERSEDE THE DESIGN-OF-RECORD, AND THE SKILL HAS NO STEP FOR IT. §3.2 says to record each requirement's commit, and the brief named "rev 1"; the file is rev 2.2, and D191 (a decisions-log row the brief did not name) plus span_arms §12a overturn parts of rev 2.2's own text (A13's "the kit picks inside `cons`"). Missing: "find the newest owner rulings on the feature (the D-rows that cite it, `scripts/entry -g TAG`), read them FIRST, and mark the design text they supersede".
2. THE TREE MOVED UNDER THE DESIGN, AND THE SKILL HAS NO DRIFT STEP. Between the design's base (1ffcce0c1) and T, 154 commits touched `src`/`memfn`; the kit delivered the design's request, a fix it lists was built, and the producer it names was deleted. The procedure asks for a site map of today's code but not for a "what of the design is already built or obsolete" pass. Proposed: §4 step 0, `git log <design base>..T -- <the design's cited files>`, each cited fix marked built/obsolete/owed.
3. NO CLASS FOR A NEW DECLARED TABLE INSIDE AN EXISTING FUNCTION. T4's guard rows live in `rr_cat`; they are not ROW (no existing table), not CHAIN->TABLE (no chain yet), not NEW-SEAM (no crossing). §6 says a zero-hit term "is a NEW-SEAM or a new shape", which does not fit a decision unit. I wrote "AS-IS + a NEW declared table". A `NEW-TABLE` class (the table, its executor, its restore column) would make that explicit and countable.
4. "EXACTLY ONE" CLASS IS TOO STRICT. Site 18 (the scan-member pick) is both a second answer to a question (SHARED) and a new cross-file read of a field (ACCESSOR); site 12 (K) is both a shape that cannot hold the new values (WIDEN) and a question asked by hand three times (SHARED). I wrote two classes. Either allow a primary + secondary class or say which wins.
5. THE SIZE TRIGGER'S "DECISION SITE" IS AMBIGUOUS FOR A HAND TEST OF A SENTINEL VALUE. Is `if (k < 0 || k >= UNBOUNDED) return false;` a decision site (an `if` on a value) or a read? The count (11 here) depends on it; for this feature the form is full either way, but for a smaller feature the paragraph/full split would turn on it.
6. DECLARED RECORDS UNDER RULE 2. The guide's tier 5 says the facts layer "already meets" goal 2, and the 2026-11-18 ruling allows declared field reads; yet `ReqRun` is read field by field 39 times from `emit_dfa.c`. The skill gives no test for "is this record's field read a declared interface or an undeclared reach". I treated the facts record as declared (it is documented field by field in `facts.h`) and added an accessor only where a field read would answer a question wrongly (the consumed extent). A one-line test in the skill would help: e.g. "a field documented in its owner's header as a fact is an interface; a reader that must combine two fields to answer one question gets an accessor".
7. THE REGISTER'S WHERE COLUMN IS STALE BY DESIGN, AND THE SKILL DOES NOT SAY TO RE-VERIFY IT. WHERE was "checked at fed0b4886"; row 14 cites `rr_cat (case A_LOOK :1204)`, which at T is `rb_walk_at`'s case. HOW TO USE IT (1) greps the register for file and function names, which still matched; a line-number match would have missed. Add: "re-verify each matched row's WHERE at T; report a moved or stale WHERE as a register correction".
8. THE D-ROW TRIGGER LOOKUP COMMAND DOES NOT WORK. §4.3 says to read D-row "Revisit when" triggers with `scripts/entry -g` on the file or function; `scripts/entry D168` prints "profile decisions dormant". I read `decisions.md` at T directly. The skill should name a working command (or the entry profile should be live).
9. REGISTER-ROW TRIGGERS WORDED WIDER THAN THEIR SHAPES. Row 7a fires on "the next change to the facts listing", but its remodel concerns the `decisions` section's `#define` parse; row 19 fires on "the next new declared table" but lists only three of four walkers. The HOW TO USE IT has no step for "the trigger fired but the shape is not touched"; I wrote NOT CARRIED with that reason. A sentence saying that is legitimate (and that the note reports the wording) would settle it.
10. THE BUILD GO EXISTS BEFORE THE ARCHITECTURE STEP. D191 gave L1 and L3 their go on 2026-11-09; the skill (§1's table) assumes architecture precedes the build go. It does not say whether remodels that "land first" need their own go when the feature already has one. Raised as the owner question **remodel-go**; the skill should state the rule once decided.
11. THE TEMPLATE'S OWNER-QUESTION LINE LACKS TWO FIELDS THE BRIEF REQUIRED. §5's template: "a word slug, the question in plain words, why it matters to the shape, the architect's leaning". The brief also asked for the current behaviour and a concrete regex example; the owner's standing preferences (plain words, slugs, examples) suggest the template should carry both.
12. THE FEATURE'S OWN GATE EXPOSURE HAS NO HOME IN THE TEMPLATE. Each REMODEL lists "the cells it touches and the speed gate", but the feature itself (L3's earlier scan start, paid per find-all call) is a speed-gate trade with no section. I put it under "Goals served" as the gate trade-off. A line under "Goals served" ("the gate: which allowance the feature relies on") would make it standard.
13. "TODAY" NUMBERS FROM A BINARY NOT BUILT AT T. The brief allowed the main tree's `build/pcrec`; its build predates T by one commit touching `src`/`memfn` (a kit-instrument merge). The skill says every "today" line runs at T but gives no rule for a binary at another commit. I recorded the gap with its command (C30). A rule ("name the binary's commit; list the `src` commits between it and T") would make this routine.
14. BOUNDING THE READ. The design-of-record was 159 KB with four review rounds folded in. The skill gives no guidance on what to read in full vs by section. I read its header, §0-§2, §5, §6-§8, §10, §12-§13 and the disposition tables' headers, and the code in full at each site. A sentence such as "read the design's rulings and unit table in full; its witness and evidence sections only where a site needs them" would save the next architect time.
15. REMODEL UNITS VS PROPOSED ROWS. §4.4 says each needed remodel "becomes one unit", and §4.3 says a classified site "with no row PROPOSES a row". It is not said whether a unit that lands first ALSO gets a proposed register row (for the manager to open and close at landing). I did both (P1-P4 with status "riding").

## COMMANDS

Every command is in the note's "Commands" section (C1-C32), run against `T=57fcb5737`; the outputs were kept in the lane scratch directory (`$PCREC_TMPDIR/scratch/archlook/cmds.out`, `probes.txt`; not committed). The lane's own commands beyond those:

- `git -C <worktree> rev-parse --show-toplevel` (first command; printed the worktree path).
- `scripts/entry REQ-LOOKAROUND -l 2`; `scripts/entry RUN-POS-SET -l 1`; `scripts/entry <tag> -l 0` for LOOK-LOCATE, DESC-DEAD, CTX-SIDES-PRODUCER, PRES-OMIN-TRUE, EARNED-SKIP, DEC-POSDOM, VLOOKBEHIND, DD-11.5, REWRITE-ADJ, CTX-PREFILTER, MATCH-KNOWN, STREAM, ENG-LOOK; `scripts/entry DESC-DEAD -l 1`.
- `git log --oneline 1ffcce0c1..$T -- src/facts/req.c src/facts/facts.c src/facts/facts.h src/facts/desc.c src/facts/kset.c` (the design's base to T: E1, E2, R1, stage 3, K38-2, [COVER-CAP] stage 1); `git log --oneline 1ffcce0c1..$T -- src memfn/src memfn/include | wc -l` (154).
- `git -C <worktree> log -1 --format=%h $T -- <file>` for each requirement file (the commits in the note's "Requirements read").
- `git show $T:docs/dev/decisions.md` read at D168 (and addenda), D161, D191, D193.
- The probe (C30): `timeout 60 /home/pcrec/projects/pcrec/build/pcrec -p rx --features all --emit-facts --pattern P` on seven patterns, output to the scratch directory only.
- `wc -c docs/design/CLAUDE.md` (12,267 after the edit; limit 12,288 by `scripts/check_claudemd_size.sh`'s table); the commit's pre-commit checks: "staged checks passed: 52, failed: 0".
