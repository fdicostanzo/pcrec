# COMMON brief: critic round archlook (2026-11-18), ARCHITECTURE mode

Read this whole file first, then your own one-question prompt. R0 = /var/tmp/pcrec-pcrec/scratch/crit-archlook.

## Scope mandate (binding)

- Touch ONLY the pcrec repository (/home/pcrec/projects/pcrec) and, if ever needed, its sibling pcrec-bench; you need
  only pcrec, READ-ONLY. You edit NOTHING in either repo. No commits, no worktrees, no checkouts.
- Scratch ONLY under your own lens directory `R0/<lens>/` (already created). Never /tmp, never $HOME.
- Never run `make`, a suite, the box queue, `scripts/boxlock`, or anything heavy. Allowed: `git -C ... grep/show/log
  (subject lines only)/diff`, plain `grep` over R0, and single light compiles with the existing binary (below), at most
  40 compiles per critic, each under `timeout 30`.
- Never `cd X && cmd` (a hook blocks it): use absolute paths, `git -C`, or a subshell `(cd X && cmd)`.
- A PCRE2 fact is never read from a PCRE2 source copy (D181). You should not need one: say "needs a pcre2-reader" instead.
- Aim for 20-40 minutes. The round must be done well before 20:00 today.

## The subject (frozen)

- SUBJECT: the ARCHITECTURE NOTE `docs/design/req_lookaround_arch.md` at commit 0abc1e961 on branch lane/archlook
  (STATUS: DRAFT), written by the `pcrec-architect` skill for the feature [REQ-LOOKAROUND] (required runs and span
  checks see through POSITIVE lookarounds into their fixed part). READ-ONLY COPY: `R0/R/subject/req_lookaround_arch.md`
  (404 lines). Cite it by line of that copy (`note:NN`) or by section.
- TREE: the note's header names `T=57fcb5737dff37bd97429fb1e889ca0233d12e10` (main, 2026-11-18). Read ALL code at T:
  `git -C /home/pcrec/projects/pcrec grep -n -E 'PAT' $T -- <paths>` and `git -C /home/pcrec/projects/pcrec show $T:<path>`.
  Never read code from the live working tree (it may hold untracked edits).
- FREEZE: main HEAD at the freeze is b22285a36. The coordinator checked: NO change between T and main HEAD under src/,
  memfn/src, memfn/include, lib/, cli/, tests/mech/sabotages, docs/spec, docs/dev/guide, docs/dev/decisions.md,
  docs/dev/plan.md or docs/design/span_arms.md (the five commits after T are predicates-draft documents). So T is also
  the tree a design and build would start from; no moved-site check is needed.
- What an architecture note is, its section template and its site classes (AS-IS, ROW, WIDEN, SHARED, NEW-SEAM,
  ACCESSOR, ...): the architect skill, copy at `R0/R/subject/pcrec-architect_SKILL.md`. Architecture mode reviews
  WHERE the feature lives in today's tree and what must change shape first; it does NOT review the algorithm, the
  code, the measurements or the build cost (those belong to the later design and code rounds).

## Requirements and record (read-only copies, all at T unless named)

- `R0/R/subject/plan_row_REQ-LOOKAROUND.txt` — the plan row (owner's words, 2026-11-05/06, and its status line at T).
- `R0/R/subject/span_arms.md` — the design-of-record, rev 2.2 at commit 8a27e2e0b (= its version at T and at main):
  units L1-L3; §2, §5, §6, §8, §12-§13 (owner rulings §12a-§12d). Written BEFORE the architecture step existed.
- `R0/R/subject/decisions.md` (D168 at line 9839, D191 at line 10129, D186 at 10042, D161 at 9439),
  `R0/R/subject/plan.md` (to read a plan row: `grep -n '^- \[TAG\]' R0/R/subject/plan.md` and read ONLY that row's
  lines; or `(cd /home/pcrec/projects/pcrec && scripts/entry TAG -l 2)`), `R0/R/subject/ARCH-STEP.md` (the
  [ARCH-STEP] pilot record and the 2026-11-17/18 owner rulings on interface vs representation),
  `R0/R/subject/POSTFACT.md`, `R0/R/subject/cover_cap.md` (rev 5.2; stage 1 built).
- The guide the note is reviewed against: `R0/R/subject/architecture.md` (= docs/dev/guide/architecture.md at T; the
  five tiers; tier-1 high-level rules carry CHECK lines; the RIDE-ALONG REGISTER is its table near line 609-633:
  confirm the range yourself), and `/home/pcrec/projects/pcrec/docs/dev/guide/critics.md`.
- The kit's contract: `git -C /home/pcrec/projects/pcrec show $T:memfn/include/memfn.h`.
- Earlier reviews of span_arms.md (reviews of the DESIGN, not of this note) MAY be read as record:
  `/home/pcrec/projects/pcrec/docs/dev/reviews/2026-11-08-r1-spanarms*` .. `r4-spanarms*`, and the span_arms reviews
  of 2026-11-09 the note cites.

## The probe (optional, light)

`timeout 30 /home/pcrec/projects/pcrec/build/pcrec -p rx --features all --emit-facts --pattern 'P'` prints the facts
listing to stdout (binary of 2026-11-15 19:53; one src/memfn commit, a kit-instrument merge, lies between it and T).
Pass patterns in single quotes or via a file; check the listing's pattern line before citing it. At most 40 runs.

## Denylist (never open, grep or diff these; exclude them from every grep)

- `docs/dev/lanes/archlook*` (the architect lane's own report and deliver file; they exist only on lane/archlook and
  in the main tree), the lane's scratch `/var/tmp/pcrec-pcrec/scratch/archlook/` (including its `cmds.out`, which
  the note names: RE-RUN the note's commands yourself instead).
- Anything of the sibling round: `docs/design/dense_hit_arch.md`, `docs/dev/lanes/archdense*`,
  `/var/tmp/pcrec-pcrec/scratch/archdense/`, `/var/tmp/pcrec-pcrec/scratch/crit-archdense/`.
- `docs/dev/dev_journal.md`, `docs/dev/wake.md`, `docs/dev/owner.md`, git log BODIES (subject lines only), job logs,
  the box queue, every directory under `worktrees/`, and `R0/.coord/` (the coordinator's notes), and other critics'
  files and lens directories in R0 (do not read them).
- `git grep ... $T` cannot reach the denied lane files (they are not at T); ALWAYS give a path list (`-- src memfn
  tests docs/spec ...`). A PLAIN `grep -r` over the repo is FORBIDDEN (it would walk `worktrees/`); plain grep only
  over `R0/R/subject/`.

## Rules for citing

- When you state a rule of the guide, a requirement or the note, QUOTE its sentence with its line (file:line); never
  restate this brief's paraphrase.
- OWNER QUOTES: ONLY the RULING lens verifies the note's quotations of the owner and of rulings word for word against
  the record; other lenses cite them without re-checking.
- Each named check topic belongs to ONE lens (your prompt names yours). If you stumble on something in another lens's
  topic, record it in one line under "Out of my lens" at the end of your file, do not chase it.
- State the POPULATION each claim covers (how many hits a grep printed, how many sites you read).

## Output format

- Your findings file ALREADY EXISTS (the coordinator created it with its headings): `R0/<LENS>.md`. It is your output,
  not an input. Append to it INCREMENTALLY: ONE APPEND PER FINDING, the moment you have it.
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: the command or grep, observed vs what the note says) or
  SUSPECTED (what would confirm it); severity (design / doc / maintenance; `answer` only if building as the note says
  would move an answer); effort; blast radius; note line(s) or §. A finding against a RULED D-row or owner ruling
  cites it and argues, or is dropped. A deviation the guide allows with a register NOTED-DEVIATION row and judged
  small is reported as NOTED (not a finding).
- End the file with `## PROBED-AND-HELD` filled (what you checked that held, with counts), then an optional
  `## Out of my lens`, then a last line exactly `CRITIC COMPLETE`.
- Then run `/home/pcrec/projects/pcrec/scripts/lanecheck --dir R0 --deliver R0/<LENS>_deliver.txt <lens>` and end
  when it prints DONE (fix the file if it does not).
- Final reply at most 150 words. A failed final reply is EXPECTED for a nested agent and needs NO escalation to
  anyone: the CRITIC COMPLETE line in your file is the delivery. If a Write/append to your file is REFUSED,
  SendMessage your findings to the coordinator (name: crit-archlook) at once, marked relayed; never route around a
  refusal.
