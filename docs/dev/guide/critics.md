# How a critic uses the guide

First version; the 2026-10-23 S3 code-review round will refine it.

The procedure for running a round (freeze, blind, pick lenses, verify, compile)
is the `pcrec-critic` skill (`.claude/skills/pcrec-critic/SKILL.md`; design, code or both, run by a coordinator agent);
this page holds the rules it reviews against. Lenses are chosen per change from
the skill's lens table; no lens set is standard because an earlier round used it.

A critic reviews a diff against the guide (`coding.md`, `architecture.md`,
`style.md`, the area's `addenda/`). Critics are read-only and never run `make`
(D6). Where a finding is already known, use blinded critics (D27). Label
findings CONFIRMED (with repro) or SUSPECTED and carry a PROBED-AND-HELD list
(`docs/dev/reviews/CLAUDE.md`).

## Standing lenses
1. **Design compliance.** Does the change follow `architecture.md`? Is each
   selection a declared table, with no private copy of an existing mechanism?
2. **Emitted code vs what it replaces.** Read the generated C and asm of the
   new path AND of the path it replaces; compare, do not infer from the source.
3. **House rules.** `coding.md`, including the altitude rubric (length is a
   trigger, never a verdict; common extracts first) and `style.md`.
4. **Test and gate adequacy.** Does each new check have an independent control,
   a witness that reaches its site, and a counted population
   (`docs/dev/learnings.md` section 3)? Does it still pass when the code is wrong?
5. **Sibling of a family.** Is a new predicate or table a sibling of an
   existing decision family? Name the family.
6. **Propose the general form and unlocks.** Beyond refutation: name the general
   form of the change and what it would unlock, with triggers.
7. **Seam round trip (manifesto principle 9).** Could what crosses this seam be written
   to text and read back by another process? Name every pointer, callback, shared
   state or target-language assumption that crosses. Applies to design and code
   rounds touching planner, kit or back-end seams.

## Rules
- **A re-pinned floor or count is a TRADE to judge, never bookkeeping.** Example:
  a SIMD floor dropping 39 to 33 in a re-pin hid a 29x caseless-literal
  slowdown (2026-10-23). Ask what moved and why.
- A finding contradicting a ruled D-row, a design note's ruled section, or a
  recorded panel disposition must cite it and argue against it, or drop (A1 of
  `docs/dev/reviews/code_review_criteria_draft.md`).
- A duplication finding names the shared abstraction: signature, call sites
  replaced, what varies (A2).
- A finding cluster names the checks and anchors that bind the code it would
  move (A3), and carries severity, effort and blast radius (A4).
- Cite metric artifacts where one applies (A5, `tools/review/`).
- Review the function population length-ordered and say where you stopped (the
  draft's Addendum 2); a long function that passes the five altitude questions
  stays long, and the finding says so.

## Design rounds
A design round reviews a document before a build go. Rules a design critic
applies, beyond `architecture.md`:
- **Design panels are the cheapest reviews.** A finding in a document is a
  paragraph edit; the same finding in built code is a fix lane (learnings §5).
- **Question premises, not only errors.** "Do we really need this?" and "is this
  really constant?" each killed a mechanism several panels had accepted; every
  panel was internally sound on an unexamined premise (learnings §5).
- **Simulate against the real data before adopting.** A proposed table or rule
  is run over the real corpus; prototype rival mechanisms head to head and let
  measurement pick (learnings §5).
- **Propose the general form and its unlocks,** with triggers, not only
  refutations (Frank 2026-10-09).
- **Sibling of a family:** at about three dispersed members of a decision
  family, propose the unified table (Frank 2026-10-06, "forest for the trees").
- **BELIEVED marks are the target list:** what a design marks as believed rather
  than measured is where it breaks (learnings §5).
- **Mark the cost:** costlier proposals must prove more; raise cost as a
  challenge, not a veto (Frank 2026-10-17).

## Lessons from review rounds

Round 2026-11-03 r1, span_pick rev 4 re-check (`docs/dev/reviews/2026-11-03-r1-memfn-spanpick4.md`): (1) a quoted region boundary from a sweep states its grid, and a boundary on a grid point is unproven; (2) a choice rule normalised over the candidate set must state whether it is independent of never-picked candidates (drill: add one); (3) every "owner rulings since rev N" row cites its durable home at the freeze, or is marked PENDING-RECORD.

Round 2026-11-02 r1, kit span_pick rev 1 (`docs/dev/reviews/2026-11-02-r1-memfn-spanpick.md`): (1) a simulate lens recomputes every outcome the design quotes with the design's OWN formula (smp20's quoted win was the evidence study's doubled-hit arithmetic; by the text's formula it loses); (2) give premise/simulate critics the evidence sweep's RAW data as the population; (3) a design's proposed sabotage witness must reach its plant by the design's own arithmetic ([MECH-REACH] applied to a design: drop-F cannot move smp20 because F already agrees there).

Round 2026-10-23 r1, kit S3 (D172's REPORT routing), four blinded critics
(`docs/dev/reviews/2026-10-23-r1-memfn-s3-code.md`, landing with lane/memfn-s3,
§4). Three of four caught a 29x caseless-literal slowdown from the code alone.
1. **Review the EMITTED artifact, both arms.** The emitted-vs-replaced lens
   caught it with loops and asm; the source-only code-quality lens missed it.
2. **Trace every slot to its named table.** The design lens caught it by
   showing a declared row (the PAIR find form) was unreachable. This is how a
   parallel mechanism shows up.
3. **A lowered performance-form floor is a trade to judge,** not a pin (the
   rule above).
4. **Blinding leaks** through report headers and git log. Give each blinded
   critic a clean worktree at the subject sha plus a denylist.
5. **The manager's rulings are review subjects too.** The defect entered
   through a ruling.
6. **Staffing:** at least one strong-model critic on emitted behaviour and one
   on design; the weaker-model lenses found real but smaller issues.

Round 2026-10-23 r2, find-all iterators (`docs/dev/reviews/2026-10-23-r2-iter-code.md`), the
first run of the `pcrec-critic` skill, five lenses picked by profile.
1. **Pick lenses by what the change touches.** The contract and slot-tracing lenses, absent from
   the earlier fixed four, found the answer bug and its cause (a private copy of the anchored body).
2. **Only the emitted-vs-replaced lens saw a regression to EXISTING entries.** Ask that lens to
   diff every pre-existing entry BASE vs SUBJECT, not only the new path.
3. **A known result re-found blind calibrates the round** (`_next_n` at k=1 slower than `_next`).

Round 2026-10-23 r2, kit S3 C1 build (`docs/dev/reviews/2026-10-23-r2-memfn-s3-c1-code.md`, lane/memfn-s3, §6), the skill's first use by the kit.
1. **The hidden-issue test passed again with the strong lenses:** both opus lenses found, blind, that two-or-more-member non-case-pair stops get a scalar walk.
2. **Verification earns its place:** it corrected a modelled magnitude (same-set windows re-read 1.1-2.5 bytes/byte on dense input, not 6-12) and showed the lane's example patterns were controls, not witnesses.
3. **Keep the check-adequacy lens whenever checks or flags change:** it alone found a broken gate (`make test-axes`'s memfn arm: MEMFN_CLASS lacked the new forms).
4. **The slot lens lists each ruling's CONSEQUENCES,** not only its agreement with the design.


Round 2026-10-24 r1, compiled substitution (`docs/dev/reviews/2026-10-24-r1-subst-code.md`, lane/substland), the coordinator skill on a 16.8k-line diff.
1. **A sabotage row can score DETECTED because its plant fails to compile** (CHK-1): with -Werror on emitted code, a plant that leaves a parameter unused scores a catch at "driver build" with no cell run. A check-adequacy lens compiles each emitted-text plant on a real artifact; the matrix asserts the plant compiles.
2. **Encoding-neutral decided from source text, not from what it denotes** (TPL-1): an all-ASCII template with `\xe9` is not neutral. A contract lens probes every escape that produces a byte.
3. **A spec sentence that pins an upstream version's behaviour can be overtaken by a later ruling** (EMIT-5 vs the D26 addendum, same day): a round checks version-pinning sentences against the current D-rows.

Round 2026-10-24, kit S3 final (memfn-s3-final):
- (2026-10-24, memfn-s3-final) **A change to the DEFAULT search gets a find-all, real-text instruction sweep per new find form.** The emitted lens runs find-all over one real text and one adversarial text per new form, BASE vs SUBJECT, by instruction count. Both large losses (a quadratic two-stream find-all, a set stop walked where BASE ran memchr) were invisible to the stated timing bar, whose sample held neither shape.
- (2026-10-24) **A new stamp VALUE or a new pre-empting row is a D94-style reader hunt.** Grep every enumeration of the stamp's values and every witness sentence for the rows it now pre-empts. Six stale spec passages came from this.
- (2026-10-24) **Critics are launched unnamed, and their results travel only as files.** A coordinator's spawns could not be named, and all six final replies were lost; the files carried everything.

Round 2026-10-27 r1, [INLINE-C] stage 2 code (`docs/dev/reviews/2026-10-27-r1-ic2-code.md`, lane/ic2).
1. **A rule that protects what a human reads is generated from the standard's property, and the lens probes the property's members** (F1, F2): a hand-typed bidi/invisible list let U+3164 make a failing-looking check pass.
2. **A keep-list by PREFIX is a control sharing its source** (F3): emitter and check both meant "public" by `<PREFIX>_`; the check's public set comes from what the caller sees (the `.h`).
3. **A comment claiming "X asserts it" is a finding target** (F5): grep for the assertion; a gate depended on one that did not exist.
4. **A card row proves it reaches the site** (F19): a prefilter rejected the whole subject before the matcher ran.

Round 2026-10-29 r1, landwalk (design) (`docs/dev/reviews/2026-10-29-r1-landwalk.md`, P1's landmark walk), rev 1 in `docs/dev/lanes/p1dsg2_report.md`.
1. **A rule stated over STATES is checked on a machine with by-class accepts.** A by-class accept and the step that continues read the same byte, so they can exclude each other; a state-level reachability rule cannot see that. Read the emitted tables of the design's own witness (PREMISE-1: the rule rejected dup-param, its headline witness).
2. **A design's sufficient syntactic forms are a second statement of its rule, and they drift.** The census counted the forms, so it measured neither the rule nor the truth (A1). A simulate lens tests the forms and the rule separately.
3. **A row that hands a NEW hand is a table walk, not a sentence.** For every hand the row produces, walk the take cells on each route and the path-closure branch it follows; the first LOCATE row to hand AT found a run-time self-cycle the static closure (each cell visited once) cannot see (A2).
4. **A speed price needs the baseline of the SELECTED path, not of the motivating case.** The motivating pattern was the only admitted row whose shipped path walked every byte; the others already started from the landmark (S2).
5. **Compile-time admission cannot pass a subject-dependent acceptance cell.** Where one pattern sits in a positive and a negative cell, the design states the loss as a bounded non-goal instead (S3).

Round 2026-10-29 r5, landwalk2 (design re-check) (`docs/dev/reviews/2026-10-29-r5-landwalk2.md`, P1 rev 1), rev 2 in `docs/dev/lanes/p1dsg3_report.md`.
1. **A fix that turns a restated predicate into a READ of another slot traces the read's cycle and its fixed points.** A row whose own selection changes the read slot's inputs makes a counterfactual read, and the fix must name it (SLOT-1: the live read had two self-consistent answers on four bench rows).
2. **"Unchanged in kind" claims about a self-check are checked by evaluating the check's condition, not its name** (SLOT-2: the inclusion cited as the PASS reason was the failure condition).
3. **A route conjunct is the FINISHER, not the body shape.** A VM hybrid's prefilter body is CR_DFA (SLOT-4; cover's C1 had already learned it).
4. **A soundness lens needs a control that can fail for every rule it calls sound** (SOUND's three controls are what make its 0-wrong count mean something).

Round 2026-10-29 r3, vmtrail (design) (`docs/dev/reviews/2026-10-29-r3-vmtrail.md`; three designs, one build sequence, consolidated in `docs/dev/lanes/vmcons_report.md`).
1. **An "answer-identical by proof" design gets a soundness lens that APPLIES the rule to emitted code.** The lens builds the base tree and hand-applies the rule, as written, to the emitter's real output for crafted witnesses. It produced every answer-level repro of the round (F1-F3, F6, F8); reading the proofs alone accepted them.
2. **Multi-document subjects: review the SEAMS.** Each document was sound against the stock program; the holes were in the composition (F4, F5, F21). Every critic tags each finding doc or seam.
3. **"Read from the event stream" is a premise to grep, not a given.** Three designs rested on a stream with no slot reads, no SET sources, missing conditional edges and a cut logged as a note. A premise lens checks every claimed input of an analysis against the producer's struct and its call sites.
4. **A cited control can stop reaching its site between design and build** (F14: R25 E5's witness now routes to revdet or the DFA). Every witness a design names gets a reach probe at the base commit.

Rounds 2026-10-31 r1-r5, pricing-split and the pricing bake-off (`docs/dev/reviews/2026-10-31-r1-pricing-split.md` .. `r5-bakeoff3.md`).
1. **Coordinator notes live where critics cannot read them.** Keep them in a `.coord/` subdirectory of the round dir that COMMON denies; a critic read the coordinator's planted-check note when process.md sat in the shared dir (r1).
2. **Drill any verdict table on CONSTRUCTED outcomes, the design's own prediction first.** The predicted tie read INCONCLUSIVE/UNRESOLVABLE (r3, SIM-5/6/7).
3. **Implement the rule from the design TEXT before reading the design's own drill script, then diff.** Nine text/script divergences, three scenarios on target only through them (r4).
4. **Check where every evidence script writes before briefing.** A design's own `--plants` mode wrote into a denied lane dir and lanewatch's default log sits in the main tree; redirect via `PCREC_TMPDIR` and `LANEWATCH_LOG` (r5).

Round 2026-11-01 r1, stream1 design (`docs/dev/reviews/2026-11-01-r1-stream1.md`), five lenses; lessons ruled 2026-11-01.
1. **A synthesis of earlier drafts is re-graded when the owner's criteria change between rounds.** The round checks the subject against the criteria in force at the FREEZE, not at writing; a subject that predates them is a DOC finding first.
2. **A merge of independently written rule tables drops conjuncts.** A synthesis that merges rule tables keeps each source row's FULL conjunct list beside the merged row, and the soundness lens diffs them.
3. **"Today's design cannot X" claims need a witness compile,** like answer claims; five premise findings were the subject claiming a benefit today's tree already has.
4. **For an F4/no-blindness question, inventory today's BACKWARD channels first** (start from `CandRow`/`CandNode`, not the subject's table).

Round 2026-11-03 r5, memfn-sp1g code (`docs/dev/reviews/2026-11-03-r5-memfn-sp1g.md`), three lenses + verifier; lessons ruled 2026-11-03.
1. **A "kit never reads X" invariance check picks its witness sites from where the kit READS the containing object, with a reach control** (the varied render differs from the absent-object render on at least one site), plus a static "kit source names no X" scan beside it. (L(4b) varied the digest on two sites that never consult the object; three real readers stayed green.)
2. **A seam-shape check is an ALLOWLIST of members on every struct of the seam,** never a denylist of retired names (provenance re-entered under a new name and on the parent struct, all green).
3. **When a deletion removes the last record column read from the built object, move one surviving column to read the object,** or the builder's remaining writes lose their only witness.
4. **A design reader list built from a grep pattern misses bare vocabulary words:** add each enumerator's bare spelling (`PRIOR_NONE` without `MF_PROV_`) and sweep design docs beyond the named sections.

Round 2026-11-04 r1, memfn-sp1b code (`docs/dev/reviews/2026-11-04-r1-memfn-sp1b.md`), four lenses + verifier; lessons ruled 2026-11-04.
1. **A code round that moves or deletes kit or src text runs the anchor checker once** (`python3 -I scripts/m6read_check_sab_anchors.py`, read-only, seconds) in the check lens. A plant can quote a function's BODY rather than its name (S1094), so a grep of the deleted names misses it.
2. **The COMMON brief of a rate-sensitive subject names how to reach each rate regime:** default (the prior), NONE (`-e utf8`), all-tie (`--analysis uniform`), and a real bundle (`-I DIR --analysis NAME`, with DIR/NAME.rxt). One critic spent 220 compiles on a misread bundle lookup.

Round 2026-11-04 r2, memfn-sp1c code (`docs/dev/reviews/2026-11-04-r2-memfn-sp1c.md`), coordinator round + verifier; lessons ruled 2026-11-04.
1. **A "MOVED" from a plant compare checks the plant's exit code first, and deletes old outputs before each compare.** Classify every compare as SAME, SILENT-MOVE (rc 0, bytes differ) or LOUD (rc != 0). A LOUD plant is caught by every corpus compile and is not a test gap; two compare scripts reported failed compiles as silent moves.
2. **Plain `grep -r` ignores git pathspecs:** a denied file inside a directory a critic greps recursively leaks. COMMON gives `--exclude=` per denied file for plain grep, or `git grep` with the pathspecs.

Round 2026-11-05 r1, memfn-sp1d code (`docs/dev/reviews/2026-11-05-r1-memfn-sp1d.md`), coordinator round + verifier; lessons ruled 2026-11-05.
1. **Check every rate-regime spelling in COMMON against the build before briefing.** `--analysis uniform` is refused; the working spelling is `-I tests/findings/adversarial --analysis=uniform`.
2. **A census backstop's shape must be one a BYPASS has to use, and its plant must not contain the conforming call's text** (F2: every plant contained `pick_takes(`, the backstop's own shape).
3. **An invariance harness needs a per-row REACH table, not one plant** (F1: four shipped rows were unreached and uncounted).
4. **A trace record added for a seam gets a sufficiency drill: two inputs with equal records must have equal picks** (F4: three constructed pairs broke it).

Round 2026-11-05 r2, alt-normal-form design (`docs/dev/reviews/2026-11-05-r2-alt-normal-form.md`), coordinator round + verifier; lessons ruled 2026-11-05.
1. **A proposed sabotage witness must be able to fail.** Compute whether its fact clears every floor and domain test in both the correct and the sabotaged build (S-c out of domain, S-f under the 16-bit floor, S-d named none).
2. **A fixpoint rewrite called a "normal form" gets a confluence drill** over every merge order (SIM-2: 23% of small grids ended in different forms; `\p{Lu}` 76 vs 66 boxes).
3. **"Not an abi event" is checked against match_api.md §6¶19 and the abi log's precedents** (two lenses reversed this round's claim independently).

- **2026-11-05 r3 vlookbehind.** (1) A simulate lens that implements a rule's INTENT validates its semantics, not its sketch: hand-execute shipped pseudo-code literally (now in the soundness row). (2) A byte-identity claim by "constant fold" is checked statement by statement against the emitted prologue: order, saved operands, charge amounts, slot allocation ("evaluates the test at compile time" hid four other differences).
Round 2026-11-05 r2, memfn-sp1e code (`docs/dev/reviews/2026-11-05-r2-memfn-sp1e.md`), coordinator round + verifier; lessons ruled 2026-11-05.
1. **When a row moves between tables, compare the gate INPUT each walk hands `gate_check`, not only the row's predicate and contract.** Plant the contract's opposite and require a refusal. F1: a clause became unable to refuse in a byte-identical move.
2. **For a declared map or list read by a check, plant a DELETED line and an INVENTED line; both must go red** (F3: both were green).
3. **For a key the subject declares, every member must be printed in the trace record**: a member missing from the record is where a bypass plant hides (F4).
4. **For a zero-mover unit, spend part of the emitted lens reading the equivalence argument rather than probing**: F1 came from reading.

Round 2026-11-06 r4, memfn-span-cards design (`docs/dev/reviews/2026-11-06-r4-memfn-span-cards.md`), coordinator round + verifier; lessons ruled 2026-11-06.
1. **Re-diff the frozen rulings at each critic return.** A ruling homed in the subject that lands mid-round gets a fresh critic on its section (D188 was seen only at hand-back).
2. **Drill a named measurement estimator like a selection rule**, on constructed outcomes (clean, outlier, bimodal, A/A above spread, equal-effect sweep): these drills found every gate defect of the round.

Round 2026-11-06 r5, memfn-span-cards re-check (`docs/dev/reviews/2026-11-06-r5-memfn-span-cards-recheck.md`); lessons ruled 2026-11-06.
1. **Locate each in-force ruling's record at the freeze**; a ruling with no record is a freeze note (DEFAULTS (B) existed only as a message).
2. **Two fixes touching one check or directory: recompute the check's population** (CHECKC: each fix held alone, together they left zero keys).
3. **"Built objects differ" is vacuous across differently named sources** (STT_FILE carries the file name); assert on linked addresses or `.text`.

Round 2026-11-06 r6, memfn-span-cards re-check 2 (`docs/dev/reviews/2026-11-06-r6-memfn-span-cards-recheck2.md`); lesson ruled 2026-11-06.
1. **Readiness runs the loader over every new data-row shape the design writes, and lists every embed-vs-source check** (READY-1: a measured row naming an arm in `inputs` is refused today; READY-3: a cell-less embed reds three STORE checks).

Round 2026-11-06 r8, memfn-s2a code (`docs/dev/reviews/2026-11-06-r8-memfn-s2a.md`); lesson ruled 2026-11-06.
1. **A witness record over a struct is planted field by field**: SEAM-1's noise digest covered the noise but not the value beside it, so a value+1 fill passed every check.
