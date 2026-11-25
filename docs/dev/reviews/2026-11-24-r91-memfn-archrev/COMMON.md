# COMMON brief — critic round r91, topic memfn-archrev (mode: arch)

Read this whole file before your lens prompt.

## Mandate (binding)

- Touch ONLY the pcrec repository at /Users/claude/pcrec, and only READ it. pcrec-bench is out of scope. Do not
  create, modify or delete any file anywhere except under YOUR OWN scratch dir
  `/var/tmp/pcrec-claude/scratch/crit-memfn-archrev/<lens>/` and your pre-created findings file (below).
- You are a READ-ONLY critic: never run `make`, never build, never compile, never run a test suite, never edit,
  commit, checkout, stash or branch in the repo. Read-only `git -C /Users/claude/pcrec show|grep|log --format=%s|diff`
  and plain grep/awk/python3 over the read-only copies below are fine. Use absolute paths; never `cd X && ...`
  (a hook blocks it; a `(cd X && ...)` subshell is fine).
- The box is the Mac (M1 Max, arm64). Bare `timeout` is GNU.

## Subject

- The note: `memfn/docs/arch_review_2026-11.md` at commit S = 30abd87065b4173baaac596b5bfacf4606b7120f
  (branch lane/memfn-arch). READ-ONLY COPY: `R/subject/arch_review_2026-11.md` (485 lines). It is the kit's overall
  ARCHITECTURE REVIEW of its four sections (planner/basic units; emitter/form tables; measurement cards; the seam
  with pcrec). It proposes 15 suggestions ARV-1..ARV-15, smaller first, FILED not built, plus register rows (§6)
  and one owner question `window-file-split` (§8).
- Its REQUIREMENTS: request R-49 (copy `R/subject/R-49.md`) and the owner's ruling kit-arch-step
  (`R/subject/KIT-ARCH-STEP.md`). R-49 is the charter: read it as the requirements.
- The tree the note reviews: T = a0f13ad83a2432f14341831ba4d1ff68964b79d9. A READ-ONLY EXPORT of T is at
  `R/tree/` (denied files removed). main HEAD at the freeze is e11c5f4efca812ecb98e0893cb78e21a253b19b9; T differs
  from main only in memfn/docs ledgers and docs/dev/lanes/BOILERPLATE.md, so EVERY code cite is the same at T and
  at main (the coordinator checked: no cited site moved).
- `R/` means `/var/tmp/pcrec-claude/scratch/crit-memfn-archrev/R/`.
- The note's §10 commands use `G() { git -C <worktree> "$@"; }`. Do NOT use any worktree. Use
  `G() { git -C /Users/claude/pcrec "$@"; }; T=a0f13ad83` — the commit is in the main repo. Under zsh write
  `${T}:path`, not `$T:path` (`:t` is a zsh modifier). Or just run the equivalent over `R/tree/` with plain tools.

## The rules you review against (read at T, i.e. in R/tree/)

- `docs/dev/guide/architecture.md` (654 lines): tier 1 the four goals (l.24), Judgement and noted deviations
  (l.139), tier 2 sub-rules (l.167; "Decisions are declared tables" l.178, "One question, one primitive" l.209,
  accessors l.231, "A shape states the inputs it covers" l.244, module seam l.259, "Layering holds at the call
  level" l.270, "facts, not methods" l.283, "Build under measurement" l.297, "Pre-release ABI changes" l.335,
  "Product first, harness minimal" l.362), tier 3 corollaries (l.377; "One table per slot" l.392), tier 4 (l.460;
  "directory of parts" l.483), and the ride-along register (`# The ride-along register`, near the end).
- `.claude/skills/pcrec-architect/SKILL.md` (live repo; the method and the site classes ROW, CHAIN->TABLE, SHARED,
  NEW-SEAM, ACCESSOR, WIDEN, AS-IS).
- `docs/dev/guide/critics.md`. memfn/CLAUDE.md, memfn/src/CLAUDE.md, memfn/include/CLAUDE.md, memfn/tests/CLAUDE.md.
- RULINGS: read every ruling file at T (R/tree/ or `git show ${T}:path`), NEVER the live tree. decisions.md
  record lines at T: D146 l.9008, D147 l.9016 (addenda follow), D152 l.9250, D155 l.9307, D157 l.9389, D185 l.10067,
  D201 l.10300 (add. 2 at l.10308), D202 l.10314, D203 l.10358. plan.md rows: locate with
  `grep -n '^- \[TAG\]' R/tree/docs/dev/plan.md` (e.g. [IR-FORM] l.152, [KIT-ARCH-STEP] l.525,
  [SP1D-KITSPLIT-SEAMS] l.1309, [SP1E-RENDERER-TABLE] l.1320, [KIT-POLICY-TABLE] l.2292, [SEAM-READER-CENSUS] l.2334).
  Owner quotes the note relies on have records at: KIT-ARCH-STEP.md; plan.md [IR-FORM] member (4) ("do not split
  now"; also docs/design/memfn/target_seam.md:59); docs/design/plan_row_bodies/ARCH-STEP.md:202 ("it locks the
  representation"); decisions.md D201 add. 2 ("code organization"); docs/design/memfn/span_pick.md ("single set");
  docs/design/memfn/plan_frame.md R5 (l.44). The owner's memories R-49 names are NOT readable on this box; rely on
  R-49's wording and the records quoting them.
- WHICH LENS CHECKS OWNER QUOTES WORD FOR WORD: only the RULING lens. Others cite them without re-checking.

## Denylist (D27 applied to review) — never open, grep or diff these

- `docs/dev/lanes/archrev_*` (the architect lane's report/deliver/rulings) — in the live repo and at the branch tip.
- `memfn/docs/journal.md` entries dated 2026-11-24; `memfn/docs/responses.md` items about R-48 or R-49. (R/tree's
  copies are already truncated before them; in the live repo exclude both files.)
- `git log` BODIES (subject lines only, `--format=%s`); every directory under `/Users/claude/pcrec/worktrees/`
  (including worktrees/memfn and worktrees/archrev); the box queue; job logs; `docs/dev/reviews/` files about this
  subject (none exist); the round's `.coord/` dir; other critics' dirs.
- For git grep on the live repo add pathspecs: `':!docs/dev/lanes/archrev*' ':!memfn/docs/journal.md'
  ':!memfn/docs/responses.md' ':!worktrees'`. For plain grep -r on the live repo add
  `--exclude='archrev*' --exclude=journal.md --exclude=responses.md --exclude-dir=worktrees`. Simplest: grep `R/tree/`.

## The kit for this round

- `kit/anchor_map.py` + its output `kit/anchor_map.tsv`: every mech sabotage row (tests/mech/sabotages) whose
  SAB_FILE[n] is under memfn/, each anchor's line at T and its ENCLOSING FUNCTION (heuristic: last top-level
  signature before a column-0 `{`). 266 anchor hits; 0 stale. Re-run: `python3 -I kit/anchor_map.py R/tree`.
  An identifier grep is a floor; the anchor map is the location census.
- No evidence scripts or builds exist for this subject (a structure review, no timing). No compiles in this round:
  the compile budget is ZERO.

## What arch mode reviews (and does not)

The site map, its classes, the register rows, the remodel units (here: the suggestions) and the rulings. NOT the
algorithm, the code quality in general, measurements, or build cost. Because this note reviews sections rather
than one feature, read "the feature" as "each suggestion" and "site map completeness" as "per section, did the note
miss sites, and does each cited command print what it claims?".

## Output format

- Your findings file ALREADY EXISTS (pre-created with headings; it is not an input): APPEND to it (Edit, or a
  shell `>>` append). NEVER overwrite it with Write: the harness refuses a subagent's whole-file Write and the file
  stays empty. Append EACH finding the moment you have it, one append per finding.
- Each finding: id `<LENS>-n`; CONFIRMED (with repro: the command run, observed vs the note's claim) or SUSPECTED
  (what would confirm it); severity (answer / speed / size / maintenance / doc / design); effort; blast radius;
  the note's § and ARV id, and file:line at T. A finding against a ruled D-row cites it and argues, or drops.
- Under `## PROBED-AND-HELD`: what you checked that held, with counts.
- Last line of the file: `CRITIC COMPLETE`. Then run
  `/Users/claude/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-claude/scratch/crit-memfn-archrev --deliver /var/tmp/pcrec-claude/scratch/crit-memfn-archrev/<lens>.deliver <lens>`
  and fix the file until it prints `lanecheck: DONE rc=0` ("DONE rc=1" is a failure).
- Final reply at most 150 words. A failed final reply is EXPECTED for a nested agent and needs no escalation: the
  CRITIC COMPLETE line in your file is the delivery. If an append is refused, SendMessage your findings to the
  coordinator at once, marked relayed.
