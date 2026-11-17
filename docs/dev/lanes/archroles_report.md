# archroles report: the architect writer skill and the critic's architecture mode ([ARCH-STEP] A4, A6 first half)

## STATE AT HANDOFF

STATE: done. Documents only; no product code, no test, no `make` beyond the doc checks.
OWED: none
RULINGS FILE: `docs/dev/lanes/archroles_rulings.md` was empty at every checkpoint (last re-read before this
report); no R-n applied.
Premise test held: `docs/dev/guide/architecture.md` has "# Part 3" and the register table; the critic skill's lens
table has D and C subject rows. STOP RULE not triggered: the critic skill took a third mode with additive edits (a
subject letter `A`, four rows, three rows widened from `D C` to `D C A`, one paragraph, three short clauses in
sections 3, 4 and 9); nothing was restructured.
Checks: `timeout 300 make -s test-plan-lint` PASS (plan.md lints clean; selftest 45 plants, 18/18 rules);
`timeout 120 scripts/check_claudemd_size.sh --all` 383 files within limits. Readers of the critic skill in
`tests/` and `scripts/`: none (`grep -rln pcrec-critic tests scripts Makefile` finds nothing; the only readers are
`.claude/skills/pcrec-manager/SKILL.md`, which this lane must not edit, and `docs/dev/guide/critics.md`). No file
enumerates the skills (no `.claude/skills/CLAUDE.md`), so no listing needed an entry.

## WHAT WAS WRITTEN

- `.claude/skills/pcrec-architect/SKILL.md` (NEW): the architecture step's WRITER. Section 1 the four steps and
  the roles (launcher, architect lane, critics; the writer never reviews its own note, a fix round is a FRESH
  architect). Section 2 the size trigger, marked PROPOSED (two or more existing decision sites, or a new mechanism;
  otherwise the paragraph form). Section 3 freeze: the tree commit `T`, every command `git grep <T>` so it re-runs
  after main moves. Section 4 the procedure: vocabulary; site map read in the CODE with six classes (`ROW`,
  `CHAIN->TABLE`, `SHARED`, `NEW-SEAM`, `WIDEN`, `AS-IS`; an aggregation is never `AS-IS`); register lookup per
  part 3's HOW TO USE IT plus D-row "Revisit when" triggers; remodels that land first (gate, size, binding checks,
  separable); general form and siblings; seams both ways; deletions; hand-offs. Section 5 the note's template
  (`docs/design/<topic>_arch.md`), each section tied to the goals or rules it answers. Section 6 the self-check,
  section 7 what it never does.
- `.claude/skills/pcrec-critic/SKILL.md`: ARCHITECTURE mode (`arch`). Freeze: the note, its commit and its `T`, no
  review tree, moved sites are findings. Profile item for `arch`. Lens table subject `A` with four new lenses:
  aggregation (opus), site-map completeness (sonnet; derives its own list BEFORE opening the note's), register
  (sonnet), first-unit identity (opus); `goals` (with the part-1 CHECK lines and "does the note decide design"),
  `seam round trip` and `ruling check` widened to `A`. A paragraph saying when the mode runs (requirements stable,
  before design; the design round checks the design against the ACCEPTED note), what it does not review (algorithm,
  code, measurements, build cost) and its usual staffing. Section 9: an arch fix lane is a fresh architect; the
  manager marks the note ACCEPTED at close.
- `docs/dev/guide/architecture.md`: the intro's "its template is not written yet" now points at the two skills.
  `docs/dev/guide/critics.md`: the skill line names the architecture mode.
- `docs/dev/lanes/archroles_evidence/` (the retro note and its CLAUDE.md); the lanes history index entry.

Lines that depend on the owner's open answers, written the strict way and flagged in the template:
- "Register rows looked up" is a REQUIRED section, with "no row matched" written out with its greps (open: must a
  note cite the register rows it looked up?).
- Each remodel-first unit states the cells it touches and a speed gate (open: does "nothing gets slower" gate all
  product code?).
- The size trigger itself (PROPOSED in ARCH-STEP.md; not ruled).

## THE RETRO TEST

Candidate: the D70 union (archhist entry 1), because its original feature's written design is the shortest
relevant text: the lookaround charter (plan rows [M6.6] and [M6.6.1] at the tree) plus APPROACH.md; the long
lookaround_design.md was NOT used (it is the design step's output, written after `T`). Tree:
`T = 74947afd8`, main just before lookaround_design.md's first commit 33ca65562; the D70 refactor ran later the
same day as [M6.6.2] wave 0 (`9874c3076..777c31c7f`). Note:
`docs/dev/lanes/archroles_evidence/lookaround_arch_retro.md`, every command a `git grep`/`git show` at `T`.

What the note names that the refactors later did:
- D70 itself: site 1 classes `struct Ast` `WIDEN` (five per-kind field sets at top level; the feature adds a fifth
  payload with a variable-length array), and D62's own trigger ("AST-walking analyses are rare (four today)") is
  met, so remodel R1 "payload per kind" lands first as a no-mover. That is what wave 0 was: a byte-identity
  pure refactor before the module.
- D70's unanticipated costs: the 13 sabotage files binding the field spellings (`git grep -l ... T -- tests/mech`
  = 13, matching archhist's "13 stale anchors") and `rd_node`'s kind-blind writes of `revbody`/`possessive`
  (src/opt/revdet.c:212-213 at `T`), which the union turned into a clobber. BOTH ONLY BECAUSE the template was
  changed (below); the first draft asked for neither.
- Three things the built module did that are today register rows or later refactors: (a) `pcrec_maxw` was added
  in src/opt/mrl.c and called from the parser (`git grep -n pcrec_maxw bde230111 -- src`): the note's site 4
  classes width `SHARED` and flags the parse-to-opt call, which is today's register row 4 (measure library below
  parse); (b) `pcrec_has_lookaround` became the third `pcrec_has_*` walk (`git grep -n -E '^bool pcrec_has_\w+'
  bde230111 -- src`): the note's site 5 counts it as the third member; (c) the context assertions: site 10
  classes the seven NFA flavour kinds plus the one-character lookaround subset `CHAIN->TABLE`, the shape D62's
  addendum built as `A_CTX`/`ctxfn.def` two months later (archhist entry 6). And site 6 classes the prefilter
  refusal/ternary chain, the shape of [DEC-FALLBACK] and today's register row 3.

What it missed or could not say:
- The revdet corpus blind spot (S121) that wave 0's positive control found: a test-coverage gap, outside an
  architecture note's question.
- Whether the payload is a union or a pointer: correctly handed to the design step.
- It over-proposes: R2 and R3 (width library, kinds-present fact) are first units the real project did not build,
  and neither has yet cost a long refactor (row 4 is still open; the has-walks were absorbed by [PATFACTS]). The
  template's "the feature needs it now" test is the guard; whether R2/R3 pass it is exactly the call the
  first-unit identity lens must make.
- HINDSIGHT: I knew the answers (archhist's report) before writing. The note uses only facts readable at `T`, but
  WHICH facts I went looking for was steered. This retro shows the template has a slot for each thing the refactor
  did; it does not show a blind writer would fill them.

What I changed in the template because of it:
1. `WIDEN` sites list every GENERIC writer or copier of the shape (the `rd_node` lesson).
2. Each remodel-first unit names the CHECKS THAT BIND the code it moves (the 13 anchors; critics.md rule A3).
3. The register lookup also reads the "Revisit when" triggers of D-rows naming a mapped site (D62's trigger was
   the D70 union's, and most triggers predate the register).
4. The critic's first-unit identity lens asks for (1) and (2).

## QUESTIONS FOR THE MANAGER

- `retro-blind`: for A6's second half (or a stronger retro), run the architect on a DIFFERENT candidate
  ([START-TABLE] at 74379fe00 or [VMREC] at de89af4cb) as a blinded lane denied archhist, archreview and every
  document after the pre-refactor commit, then judge it against archhist entry 10 or 13. Leaning: yes, START-TABLE,
  since its family count is the template's sibling test.
- `note-path`: I chose `docs/design/<topic>_arch.md` for the note (a living design-tier document with a STATUS
  header). Alternative: a section inside the feature's design-of-record file. Leaning: a separate file, so the
  design round can cite the ACCEPTED note at a fixed commit. The choice is yours (answer-free).
- `wiring`: the A5 wiring (manager skill, BRIEF_TEMPLATE) needs a brief field "ARCHITECTURE NOTE: <path @commit,
  ACCEPTED> or below trigger"; and the manager skill's skill table should list `pcrec-architect` beside
  `pcrec-critic`. Not done here (out of scope).
