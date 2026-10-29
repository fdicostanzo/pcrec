---
name: pcrec-critic
description: Run an adversarial critic round on a pcrec (or memfn kit) DESIGN document, CODE change, or both. The manager launches one opus COORDINATOR agent that freezes the subject, picks lenses from the declared lens table, briefs and launches blinded read-only critics, verifies their findings, drafts docs/dev/reviews/YYYY-MM-DD-rN-<topic>.md with PROPOSED dispositions, and meta-monitors the round itself; the manager then rules the dispositions and launches the fixes. Use before a build go (design) or before landing (code). Args: design|code|both, the subject (doc path, branch or commit), a topic name.
---

# pcrec critic round

A critic round reviews a DESIGN document, a CODE change, or both, against the
living guide `docs/dev/guide/` (coding, architecture, style, critics, addenda).
The guide holds the rules critics review against; this skill holds the
procedure. When the two disagree, the guide wins and you fix the skill.

Lenses are chosen per subject from the table in section 4. No lens set is
standard because an earlier round used it (Frank, 2026-10-23).

## 1. Roles

| role | who | does | never |
|---|---|---|---|
| **launcher** | the manager | names subject, mode and topic; launches the coordinator; rules every disposition; launches fix lanes; accepts or declines proposed skill/guide changes | tells the coordinator any known finding (it must stay blind) |
| **coordinator** | ONE opus agent, background | sections 2-7: freeze, profile, lenses, briefs, launch, monitor, verify, draft, meta-monitor | rules dispositions; edits code; commits; merges |
| **critics** | 2-5 agents launched BY the coordinator | one narrow question each, read-only, findings to a file | run `make` or suites; edit either repo |
| **verifier** | one agent launched by the coordinator | re-runs every CONFIRMED finding that would change code or a design | trusts a critic's consequence claim |

Why a coordinator (Frank, 2026-10-23): every critic report woke the manager's
large context (about a dozen turns per round), and the manager knew results it
had to keep out of the briefs. A fresh coordinator is cheaper per turn and is
blind by construction. Subagents can launch subagents (tested 2026-10-23), but
a nested agent's final reply may NOT reach its parent: everything that matters
travels as FILES, and a missing file gets one SendMessage asking for it.

## 2. Launch (manager)

Launch one agent: `model: opus`, background, name `crit-<topic>`, prompt =
"COORDINATOR critic round <topic> (<mode>). Read
/home/pcrec/projects/pcrec/.claude/skills/pcrec-critic/SKILL.md sections 3-8
and follow them as the coordinator." plus: mode, subject, topic, the scope
mandate (only the pcrec and pcrec-bench repos; scratch only under
`$PCREC_TMPDIR/scratch/crit-<topic>/`; no edits to either repo except creating and
removing the review worktree), and the denylist paths the coordinator cannot
know (lane report names, earlier reviews of this subject). Say NOTHING about
known results. Then go about other work; the coordinator hands back one
message when the draft is ready.

## 3. Freeze and profile (coordinator)

1. Subject:
   - code: `git rev-parse` the branch yourself (never a hash from prose); record
     `SUBJECT` and `BASE=$(git merge-base main SUBJECT)`.
   - design: the document path AND the commit that holds it (`git log -1
     --format=%H -- <doc>` on its branch); critics read that version.
   The subject stays frozen until the round compiles (learnings §6, R30).
2. Code mode: make a clean review tree, `git worktree add --detach
   worktrees/crit-<topic> SUBJECT`, and build it ONCE yourself, UNLOCKED:
   `nice make -j2` (critics run `build/pcrec` and `gcc -S` on single
   patterns, never `make`). NEVER under `scripts/boxlock`: a waiter yields to
   every ready queue job, often the subject's own validation, and a build of
   seconds waited 3h50m (round 2026-10-27 r1 ic2). Launch the probe lenses
   only once `build/pcrec` exists; a critic without a binary waits for it
   (poll every 10 min, up to 4 h) rather than ending source-only.
3. Denylist (D27 applied to review): the lane's reports
   (`docs/dev/lanes/<lane>*`), review files on this subject, `git log` bodies
   beyond the subject lines, job logs, other worktrees, the box queue, plus the
   launcher's list. Put it in every brief. To deny a plan.md row, locate it by `grep -n '^- \[TAG\]'` only; never print its
   neighbours (a `sed -n` around the tag line leaked the denied rulings, 2026-10-26 inline-c).
4. Profile: what does the subject touch? Several can apply:
   - design: a new mechanism or table; a measured quantity, check or data file;
     a caller-facing contract; a build proposal (cost, scope); rulings it rests on
   - code: emitted C; a decision table/selector/row; a caller-facing contract;
     a performance claim, floor or re-pin; checks/pins/sabotage rows; plain C
     structure; rulings relied on

## 4. Pick lenses (coordinator)

First match per profile item, union the results; 2-5 critics; never a lens
with nothing in scope. Each lens is ONE question (narrow briefs beat wide ones,
measured twice). Subject column: D = design document, C = code diff.

| subject | profile item | lens | its one question | model |
|---|---|---|---|---|
| D C | always | **goals** (fold into another lens if needed) | Does the design state ranked, checkable goals (architecture.md)? Does the subject serve them in that order? No goals = a DOC finding; review against the goals the design implies, saying so. | strong |
| D | a new mechanism or table | **premise** | Name every assumption the design rests on and test each (grep, measure, read the data): is it true? ("do we really need this?", "is this really constant?" are this lens; so is every sentence of the form "the existing X already does Y": find X by file:line.) | strong |
| D C | a trust boundary (opt-in, gate, untrusted input becomes code or a file read) | **adversary** | As the author of an untrusted input, find every path from your bytes to code, a file read or a terminal escape that bypasses the gate, including the test harness and tooling as entry points; and what an ADMITTED input can do to the rest of the output | strong |
| D | a table, rule or selection | **simulate** | Run the proposed rule over the real corpus or data: does it pick what the design claims, and where does it mispick? | sonnet+ |
| D | a claim of answer identity BY PROOF (a rewrite, an elision, a dropped record) | **soundness** | Build the base tree and APPLY the documented rule, as written, to the emitter's real output for crafted witnesses (and to every seam where two documents' rules compose): does any answer move? (2026-10-29 r3 vmtrail: produced every answer-level repro) | opus |
| D C | a table / slot / mechanism | **slot tracing** | Trace every slot to the table or mechanism the design names for it: is anything duplicated, narrowed or unreachable ("one table per slot")? Is it the third member of a family? | strong |
| D C | rulings relied on | **ruling check** | For each ruling, does it agree with the design and the guide, and what are its CONSEQUENCES? Fold into slot tracing when that runs. | strong |
| D | a measured quantity, check or data file | **measurement** | The docs/design/CLAUDE.md standing questions: the regime, the independent control, what moves when the data is regenerated. | sonnet+ |
| D | a build proposal | **cost and overlap** | What does it cost, what does it buy, what measurement triggers it (D77), and does it overlap an in-flight refactor (D153)? Costlier must prove more. | sonnet+ |
| C | emitted C | **emitted vs replaced** | Generate C and asm of the new path AND the path it replaces, and diff every PRE-EXISTING entry BASE vs SUBJECT: what does the new code do worse or differently? | strong |
| D C | a caller-facing contract | **contract** | Does the code (or the design) do exactly what the spec says for every admitted input class; do names describe behaviour (D174, D80)? Code mode probes edges with the built compiler. | strong |
| C | a performance claim / re-pin | **trade audit** | Every pin, floor or count moved: what speed, size or coverage did it give up, and who judged that trade? | sonnet+ |
| C | checks / pins / sabotage / flags | **check adequacy** | Per new or changed check: what input makes it fail, who chose it, does a witness reach the site, is the population counted (learnings §3)? | sonnet+ |
| C | plain C structure | **house rules** | coding.md + style.md: duplication (name the shared abstraction), altitude, tables used as if-chains, side effects in predicates. | sonnet |

Always add the two standing questions to one lens (say which): **sibling of a
family** and **general form + unlocks** (with triggers).

Staffing: a "strong" lens gets opus; with both in scope, at least one strong
critic on behaviour (emitted code or simulation) and one on design.

A D27 spec-first test author (tests written from the promise, denied src/ and
tests/, in a `scripts/mk_d27_cell.sh` cell) is not a critic: for a design with
a contract, RECOMMEND one in the draft; the launcher decides.

## 5. Brief and launch the critics (coordinator)

Write one COMMON brief file under `$PCREC_TMPDIR/scratch/crit-<topic>/` (scope
mandate, read-only rules, subject and paths, the guide files, design docs and
spec sections the subject cites, the denylist, the output format), then one
short per-lens prompt: title `CRITIC <lens> (<model>): <topic>`, "read COMMON
first", the one question, the output file path.

Output format (in COMMON): the critic CREATES its file (say it does not exist
yet: critics took a named file for an input) and writes it INCREMENTALLY;
each finding has an id `<LENS>-n`, CONFIRMED (with a repro: input, command,
observed vs expected) or SUSPECTED (what would confirm it), severity (answer /
speed / size / maintenance / doc / design), effort, blast radius, file:line or
§; a finding against a ruled D-row cites it and argues, or drops; the file
ends with PROBED-AND-HELD (with case counts). Final reply at most 150 words.

Each critic gets a DELIVER file beside its output (`report=` its findings file, `sections:` the
findings + PROBED-AND-HELD, `commit: no`) and ends only after `scripts/lanecheck --deliver FILE NAME`
prints DONE; the coordinator runs `scripts/lanewatch --dir $PCREC_TMPDIR/scratch/crit-<topic> NAME...`
instead of waiting for replies (nested replies are often lost).

Launch all critics in one message, background, UNNAMED (a teammate cannot name agents). No addenda to a running
critic; a missed input goes to a fresh critic.

## 6. Monitor, verify, draft (coordinator)

1. Critics may return in the launch turn even when backgrounded; then read the files at once.
   Read each critic's FILE when it idles; a critic without its file gets ONE
   SendMessage asking for it. A critic idle on its own background probes gets
   one nudge to resume. Stop each critic (TaskStop) once its file is complete.
2. Launch ONE verifier (sonnet unless a finding needs opus judgment) over all
   CONFIRMED findings that would change code or a design: answers against the
   oracle (libpcre2 / python `re`), speed with `perf stat -e instructions:u`
   pinned `taskset -c 7` and repeats, size with `size`, structural claims by
   quoting the cited lines, design claims by the simulation or grep they name.
   Give it a DELIVER block like a critic's (its file `verify.md`, one section per finding id, a closing
   `VERIFY COMPLETE` line; 2026-10-29 landwalk: without one the verifier improvised its own shape).
   It writes `verify.md` INCREMENTALLY, one finding at a time (a nested agent's final reply is often
   lost: 2026-10-26 ic1b-code): HOLDS / REFUTED / PARTLY / not verified (why).
3. Draft `$PCREC_TMPDIR/scratch/crit-<topic>/review.md` in the
   `docs/dev/reviews/` shape: subject; lenses as run (lens, model, question,
   why chosen); which lens caught what; findings by id with a PROPOSED
   disposition (FIX-NOW | PLAN | DOC | REJECTED | NOTED) and a one-line reason;
   PROBED-AND-HELD; by-id completeness; lessons for the guide. Consolidate
   overlapping findings (name every lens that found it). Copy critic texts and
   `verify.md` beside it in `review/`.
4. Remove the review worktree (`scripts/wtprune --apply --force --quiet-min 1 crit-<topic>`: the default 120-minute quiet gate keeps a freshly built tree)
   and stop the verifier.

## 7. Meta-monitor the round (coordinator)

Keep `$PCREC_TMPDIR/scratch/crit-<topic>/process.md` AS YOU GO: per agent, launch
and end time, model, final state (file complete / resent / nudged / stalled);
brief confusions; delivery failures; blinding leaks you noticed; per lens,
findings raised / verified / severity / overlaps; time to draft. At the end
add:
- **Process observations:** what slowed or confused the round, what the
  lens table missed or over-staffed.
- **Proposed changes:** concrete text for this skill, `docs/dev/guide/critics.md`
  or the COMMON template, each with the observation that motivates it.
- **Framework notes:** what this round says about the coordinator pattern
  itself (a manager launches one coordinator that runs a fan-out, verifies and
  drafts for a ruling), and where else it might fit, with the evidence.

## 8. Hand back (coordinator)

One SendMessage to the launcher, at most 15 lines: the draft path, the
answer-level and speed-level findings, proposed FIX-NOW ids, and the top
proposed process change. Then END.

## 9. Rule and close (manager)

1. Read the draft and `process.md`; rule each disposition (overrule with a
   reason); commit the review as `docs/dev/reviews/YYYY-MM-DD-rN-<topic>.md`
   (+ sibling dir of critic texts), indexed in `docs/dev/reviews/CLAUDE.md`.
2. FIX-NOW items go to fix lanes on the subject branch (fresh agents, the
   review as brief source); the round closes when every finding has a
   disposition and every FIX-NOW is landed or ruled.
3. Accept or decline each proposed process change: accepted ones go into this
   skill, `docs/dev/guide/critics.md` "Lessons from review rounds", in the same
   commit as the review. Framework notes go to
   `docs/dev/meta/coordinator_framework.md` (append, dated, with evidence).
4. Report to the owner in plain words: what was reviewed, which lenses ran and
   why, what each found, what is being fixed, whether the subject may proceed.
