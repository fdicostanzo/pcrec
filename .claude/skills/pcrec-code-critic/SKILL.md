---
name: pcrec-code-critic
description: Run an adversarial CODE critic round on a pcrec (or memfn kit) change: freeze the subject commit, pick the lenses the change needs from the lens table, brief blinded read-only critics against docs/dev/guide/, verify their findings, and compile docs/dev/reviews/YYYY-MM-DD-rN-<topic>-code.md with a disposition per finding. Use before landing a branch that changes code, emitted text, checks or a caller-facing contract. Args: the branch or commit, plus a topic name.
---

# pcrec code critic round

A code round reviews BUILT code against the living guide, `docs/dev/guide/`
(coding, architecture, style, critics, addenda). Design panels (D6) review
documents; this skill reviews a diff. The guide holds the rules; this skill
holds the procedure. When the two disagree, the guide wins, and you fix the
skill.

The lenses are chosen per change (section 3). No lens set is standard
because an earlier round used it (Frank, 2026-10-23).

## 1. Freeze the subject

1. Name the subject: branch tip → `git rev-parse` it yourself (never a hash
   from prose) and record `SUBJECT=<sha>` and `BASE=$(git merge-base main <sha>)`.
   The target stays frozen until the round compiles: batch every input,
   including your own fix items (learnings §6, R30).
2. Make a clean review tree at the subject: `git worktree add --detach
   worktrees/crit-<topic> <sha>`. Critics read THIS tree, never the lane's
   worktree (its reports, logs and uncommitted state leak the author's
   conclusions).
3. Build it ONCE yourself (`make -j16` in the review tree, under boxlock if the box is busy) so
   critics can run `build/pcrec` and `gcc -S` on single patterns.
   Critics never run `make` or any suite.
4. Blinding (D27 applied to review): write a DENYLIST into each brief: the
   lane's report files (`docs/dev/lanes/<lane>*`), review files on this
   subject, `git log` beyond `BASE..SUBJECT` subjects, job logs, and any
   known finding you want tested blind. If a finding is already known
   (a timing run, a red), say NOTHING about it, so the round measures whether
   the lenses would have caught it.

## 2. Profile the change

Read `git diff --stat BASE SUBJECT` and the commit subjects. Note which of
these the change touches (several can apply):

- emitted C (anything under `src/gen/`, memfn kernels, scaffolding, abi)
- a decision table, selector, row or admission predicate
- a caller-facing contract (`lib/pcrec.h`, `docs/spec/`, flags, stamps, CLI)
- a performance claim, timing gate, floor or re-pin
- checks, pins, sabotage rows, harness scripts
- plain C structure (new functions, moved code, shared helpers)
- a ruling made during the work (list the rulings the subject relied on)

## 3. Pick lenses (first match per profile item; union the results)

Each lens is ONE narrow question (narrow briefs beat wide ones, measured
twice). 2-5 critics per round; never a lens with nothing in scope.

| change touches | lens | its one question | model |
|---|---|---|---|
| emitted C | **emitted vs replaced** | Generate the C and asm of the new path AND the path it replaces for patterns that reach each changed site; what does the new code do worse or differently? | strong |
| a table / selector / slot | **slot tracing** | Trace every slot the change fills to the table or mechanism the design names for it; is any row unreachable, any mechanism duplicated or narrowed (architecture.md, "one table per slot")? | strong |
| a caller-facing contract | **contract** | Does the code do exactly what the spec says, for every input class the spec admits, and does each name describe behaviour (D174, D80)? Probe the edges with the built compiler. | strong |
| a performance claim / re-pin | **trade audit** | List every pin, floor or count the diff moves; for each, what speed or coverage did it give up, and who judged that trade? | sonnet+ |
| checks / pins / sabotage | **check adequacy** | For each new or changed check: what input would make it fail, who chose that input, does a witness reach the site, is the population counted (learnings §3)? | sonnet+ |
| plain C structure | **house rules** | Against `coding.md` and `style.md`: duplication (name the shared abstraction), altitude, tables used as if-chains, side effects in predicates. | sonnet |
| rulings relied on | **ruling check** | For each ruling the work relied on, does it agree with the design and the guide? A ruling is a review subject, not an axiom. Fold into slot tracing when that lens runs. | strong |

Every round also asks the **goals question**, folded into the contract or
slot-tracing lens: does the cited design state ranked, checkable goals
(`architecture.md`), and does the code serve them in that order? A design
without goals is itself a finding (DOC), and the critic reviews against the
goals the design implies, saying so.

Always add the two standing questions to one lens of your choice (say
which): **sibling of a family** (is a new predicate/table a member of an
existing decision family?) and **general form + unlocks** (what is the
general form of this change, and what would it unlock, with triggers).

Staffing: a "strong" lens gets opus; at least one strong critic on emitted
behaviour and one on design whenever both are in scope. Lower tiers find
real but smaller issues and miss behavioural gaps.

## 4. Brief each critic

Brief = title line `CRITIC <lens> (<model>): <topic>`, then:
- the scope mandate (only the pcrec and pcrec-bench repos; scratch in the
  session scratchpad; read-only: no edits, no commits, no `make`);
- the review tree path, `BASE` and `SUBJECT`, and the one question;
- inputs: `docs/dev/guide/README.md` + the files it names for the lens, the
  area's addendum, the design doc(s) and spec sections the change cites;
- the denylist (section 1.4);
- output: findings to `<scratchpad>/crit-<topic>-<lens>.md`, written
  INCREMENTALLY, each labelled CONFIRMED (with a repro: pattern, command,
  observed vs expected) or SUSPECTED, with severity (answer / speed / size /
  maintenance / doc), effort, blast radius; plus a PROBED-AND-HELD list with
  case counts; a finding that contradicts a ruled D-row cites it and argues,
  or drops (criteria draft A1);
- a word cap for the final reply (findings live in the file).

Launch all critics in one message, in the background. No addenda to a
running critic; a missed input goes to a fresh critic.

## 5. Verify, then compile

1. Read each critic's file after it idles; a critic that idles without its
   file gets one resend request.
2. VERIFY every CONFIRMED finding that would change code: rerun its repro
   (a verification lane is fine). A consequence claim is a claim (two have
   died this way). Where critics disagree, the repro decides.
3. Compile `docs/dev/reviews/YYYY-MM-DD-rN-<topic>-code.md`: subject sha,
   lens table as run (lens, model, question, why chosen), findings by id
   with disposition FIX-NOW | PLAN | DOC | REJECTED | NOTED, the
   PROBED-AND-HELD list, which lens caught what, and a by-id completeness
   line. Index it in `docs/dev/reviews/CLAUDE.md`. Critic texts go in a
   same-named sibling directory.
4. FIX-NOW items go to a fix lane on the subject branch (fresh agent, the
   review file as its brief source); re-validate; the round closes when
   every finding has a disposition and every FIX-NOW is landed or ruled.
5. Lessons: anything the round taught about lenses, blinding or staffing is
   appended to `docs/dev/guide/critics.md` "Lessons from review rounds"
   (and to this skill's table if it changes the procedure), in the same
   change as the review file.
6. Remove the review tree with `scripts/wtprune --apply crit-<topic>`; stop every critic agent.

## 6. Report

To the owner, in plain words: what was reviewed, which lenses ran and why,
what each found, what is being fixed, and whether the subject may land.
