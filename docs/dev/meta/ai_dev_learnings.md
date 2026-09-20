# Developing with models — learnings from pcrec (living document)

Started 2026-09-20 (seventy-second session). Frank's framing: pcrec was begun
for several reasons, one of them to learn whether a different operating model
— Fable as technical manager, sonnet/opus as the developers — holds up at a
scale where a single Opus session had spent half its time on bookkeeping to
stay oriented. It does (this repo is the evidence). The open question is
COGNITIVE LOAD: is the required information too much, the subject too
complicated, the code too large for the models doing the work — and do the
tricks a person uses (short guessable names, small functions, related things
nearby) apply to them at all? Each entry below names its measurement.

## 1. What helps (measured)

**1.1 Function names carry meaning; field names do not.** A model reading a
bare signature guessed 68% of emit_vm.c's 129 static functions right; a bare
field declaration, 15% of 72 fields. (reviews/2026-09-20-readability-
experiments.md §1, condition A.) Rule: name length proportional to the
distance between definition and use — struct fields and file-scope names
complete; locals inside a short function fine short. The `vm_<subsystem>_
<verb>` and `n<family>` / `_total` conventions were guessed right almost
without exception: consistent affix conventions do real work for a reader
who sees one hunk at a time.

**1.2 A header's FIRST SENTENCE is what a context-free reader gets.** Headers
that opened with an invariant, a bracketed tag or a cross-reference LOWERED
function comprehension (68% → 57%); rewriting 93 of them to open with what
the function does raised it to 83% on the same instrument (same file §1 +
addendum; lanes hdr1/hdr2). Field comments tripled field comprehension
(15% → 42%). Rule (now coding_guide.md §4.2): plain "what it does" first;
invariant, why-not-the-alternative, tags and citations after.

**1.3 Only the code gets past the mid-fifties.** With the whole (comment-
stripped) file in view the guesser reached 89%; nothing short of that
cleared 55%. The gap is the load the ORGANIZATION imposes: a reader must have
the uses in view. No naming or commenting fix closes it — the island-trie
family, the region/splice fields and the listing-row functions were wrong
under the header and right only under the code.

**1.4 Small functions help a model for EDIT LOCALITY more than for
understanding.** A model holds a 500-line function in view; what it cannot
do cheaply is verify a change inside one. Every wave-2 extraction in the
code-review refactor was provable byte-identical because seams existed
(plan.md [REVW.2]); the sabotage anchors and the brief could name the
function. OPINION, consistent with the record: the human argument for small
functions ("understand it in isolation") transfers weakly; the tooling
argument (small hunks, exact proofs) transfers strongly.

**1.5 Organize by how the code is EDITED, measured from history — not by the
type hierarchy.** 182 commits to emit_vm.c: edits touched the emitter arms
alone 61% of the time and all three walks (cost/count/emit) together 24%.
A by-kind reorganization (each AST node kind owning its cost+count+emit, the
OO instinct) would have fought the grain. (§2.)

**1.6 File grain: the author's own section banners are the best estimate of
the co-change unit.** Splitting emit_vm.c at its 17 banners would have cut
the mean lines a developer had to read per real commit to 35% of the
monolith, versus 45% by pass and 56% by kind — even though the banner split
keeps FEWER commits inside one file (two 700-line files beat one 4,000-line
file). One function (pcrec_emit_vm, 2,809 lines) was in the closure of 122 of
182 commits: the dominant term is the giant function, not the file. (§3.)

**1.7 History comments are durable memory AND context cost.** emit_vm.c is
half comments; emit_dfa.c 1.3 comment lines per code line. They are the
memory the models do not have across sessions (correction-of-record
narratives), and every lane that opens the file pays for them. The split
that works: invariant + why-not-the-alternative inline; history in docs with
a pointer (coding_guide §4.2; [REVW.A1] moved a 449-line change log out of
emit_dfa.c; [TOUR-1] prunes the essays in pcrec_emit_vm).

**1.8 Where the models actually fail at scale: INCOMPLETE ENUMERATION, not
confusion inside a function.** The record's real breakdowns: a hand-listed
"four abi sites" that missed a fifth reader (D94); three lanes rebuilding the
same driver and disagreeing on its population; a lane's stated cause being a
claim. Mitigations that worked, all one shape: bound a lane to one file, one
invariant, one proof; make every population something a SCRIPT counts (the
K35 lesson); byte-identity and grep-derived floors so correctness does not
depend on comprehension. Two header lanes on 2026-09-20 were the pattern
working: hdrgen re-measured the brief's population (137 → 131) and reported
its method.

**1.9 A model does not notice it is confused; a person does.** The naming
experiment's two failure modes are the same defect seen from both sides:
CONFIDENT INVENTION (six confident-and-wrong guesses on the first run) and
REFUSAL TO INFER (a second run answered "Local variable nd" for 23 of 25
locals whose names carried the meaning). Both are calibration, both steered
by prompt wording, neither is what a person does with `nbr` beside `int`.
Consequence: design checks and proofs that are independent of the model's
reading — and never accept a model's self-reported confidence as evidence
(1.10).

**1.10 Self-reported confidence is noise; renames INFLATE it.** 96 "high"
guesses at 90% precision became 197 "high" at 60% precision after 12 of 226
names were lengthened. Longer names also import a word's other meanings:
2 of 12 renames got WORSE under fuller evidence (`nd → nodes`, `cap →
out_cap`).

## 2. Instruments that worked (reusable)

- **Strip → guess → grade.** Strip a file's comments; a haiku guesses each
  name's meaning under a BOUNDED evidence condition (A: identifier+type;
  B: +declaration comment/header; C: whole stripped file); a sonnet grades
  correct/partial/wrong/vacuous against a truth column derived once from the
  commented source. Builder + names list + protocol prompt:
  reviews/2026-09-20-readability-data/build_conditions.py. PROTOCOL: one
  committed guesser prompt that forbids templated non-answers; THREE runs,
  report the median — a single run's spread is ~30 points on small n, and
  it is DISPOSITION variance (willingness to guess), not comprehension.
- **Edit closure from git hunk headers.** `git show -U0` names the enclosing
  function per hunk; per-commit function sets → co-change counts, and the
  READ closure (lines of the files a commit touched under a candidate split)
  scores a file grain on the history's own edits. Scripts: reviews/2026-09-
  20-readability-data/{parse,analyze}.py, commits.tsv.
- **Census before charter.** function_census.py (+ its `header` column),
  the switch-arm census (87 switches, 3 arms ≥ 20 code lines → "not worth it
  tree-wide"), the kind-switch census (46, 1 pure kind→constant → "wait for a
  second row"). A cheap count turned three plausible reorganizations into
  measured no-gos in one afternoon (reviews/2026-09-20-code-org.md).

## 3. Ideas for future tests

- **Task-based, not guess-based.** Give a sonnet lane the SAME small edit in
  (a) the file as is, (b) the file with long names, (c) the file split at
  banners; measure tokens consumed, tool calls, wall time, and whether the
  byte sweep stays clean. The guess experiment is a proxy; this is the
  quantity itself. Needs ~3 runs per arm.
- **Header first-sentence A/B at scale.** Now that hdr2's rule exists, run
  condition B over every src/ file three times and rank files by function
  comprehension; the bottom of the list is where the next header pass goes.
- **Does the model READ the header?** Condition B' = header only, no
  signature. If B' ≈ B the header is doing the work; if B' ≪ B the signature
  is, and long headers are cost without benefit for the model reader.
- **Comment cost.** Same lane task with the file's history comments pruned to
  invariant+pointer vs intact: tokens and correctness. Prices [TOUR-1]'s
  pruning before it is done.
- **Confidence steering.** Vary one sentence of the guesser prompt ("say
  no-idea when unsure" vs "always guess") across three runs each; quantify
  how much of the instrument's variance is prompt-set disposition.
- **Cross-model.** Same conditions with opus as guesser: does comprehension
  from names alone rise, or only the confidence?
- **The manager tier.** Log the manager session's context growth per hour
  against the number of live lanes and open questions; the model that
  organizes is also a reader, and the delegation rules in the memory files
  (`pcrec-subagent-cache-warmth`) were written from cost, not measured load.

## 4. Open questions

- Is there a name-length OPTIMUM for a model reader (long enough to carry
  the meaning, short enough not to import a word's other senses)? The two
  backfired renames say yes; n=12 says nothing about where.
- Does by-pass organization stay cheaper as modules multiply, or does the
  by-kind instinct win once a fourth walk arrives? Re-run §1.5 after the
  next module lands.
- How much of "the code is what carries meaning" is emit_vm.c-specific? Run
  the instrument on parse.c and a small module file before generalizing.
