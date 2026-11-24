# COMMON brief: critic round r93 memfn-archrev3 (ARCHITECTURE mode, a ONE-CRITIC RE-CHECK)

Round dir: RD = /var/tmp/pcrec-claude/scratch/crit-memfn-archrev3

## Mandate (read first; binding)

- Touch ONLY the pcrec repository, and that READ-ONLY. pcrec-bench is out of scope. No edits to any repo, no commits,
  no worktrees, no checkouts.
- Write ONLY under RD/fixind/ (your scratch) and your pre-created findings file RD/fixind/findings.md. Nowhere else on
  this machine (not /tmp, not $HOME).
- Never run `make`, a test suite or a build. Grep, read, awk, and `python3 -I` one-liners over the RD/R/ copies are fine.
- Pass patterns to grep in single quotes or via a file. Under zsh write `${T}:path`, never `$T:path` (`:t` is a zsh
  modifier and silently eats the path).

## The subject

- SUBJECT: `RD/R/subject/arch_review_rev3.md` = `memfn/docs/arch_review_2026-11.md` rev 3, at commit
  968b107f595797d2ae568d0a67e8a60757a31eb9 on lane/memfn-arch (the note is unchanged after it; branch tip at freeze
  c282575c1, a journal line after the 1d70f562b merge). It is the memfn kit's overall ARCHITECTURE REVIEW of its four
  sections (chartered by R-49), filing suggestions ARV-n, smaller first.
- Rev 3 is a third, fresh architect's revision answering review r92. r92 is an INPUT you may read:
  `RD/R/subject/r92/review.md` (its RULING section is the input: G1-G12 and G14 FIX-NOW; G13 ruled to the OWNER as a
  §9 sub-part) and the r92 critic texts beside it (fuwindow.md, fuseam.md, ruling.md, aggfix.md, COMMON.md, process.md).
- THE DIFF TO CHECK: `RD/R/subject/rev2_to_rev3.diff` (rev 2 at e3f3b5a12 -> rev 3 at 968b107f5). Rev 2 is
  `RD/R/subject/arch_review_rev2.md`. Scope from the diff; read the whole note only where a fix needs context.
- Requirements: R-49 in `RD/R/tree/memfn/docs/requests.md` (grep `^## R-49`) and `RD/R/subject/KIT-ARCH-STEP.md`.
- TREE T = a0f13ad83a2432f14341831ba4d1ff68964b79d9 (the note's header). `RD/R/tree/` is a `git archive` of T with the
  denied ledger tails removed (read-only). READ CODE AND RULINGS THERE. Code under memfn/src, memfn/include,
  memfn/tests, src, tests, Makefile, and decisions.md, plan.md, docs/design and docs/dev/guide are IDENTICAL at T and
  at the subject commit; main HEAD at the freeze (e11c5f4ef) differs from T only in BOILERPLATE.md and three
  memfn/docs ledgers. So RD/R/tree IS the code and ruling record at the freeze; no cited site moved.
- Guide: `RD/R/tree/docs/dev/guide/architecture.md` (goals 1-4, judgement (a)-(e), HOW TO USE IT, KINDS OF ROW, the
  ride-along register rows 1-30). Architect method: `RD/R/tree/.claude/skills/pcrec-architect/SKILL.md`.
- Re-running the note's §11 commands: set `R=RD/R/tree` (spelled out), make `S=RD/fixind/s` and fill it as §11 says.
  Where §11 uses `G show ${T}:...` / `G grep ... $T`, you may use `G() { git -C /Users/claude/pcrec "$@"; }` with
  `show`/`grep`/`archive` AT T ONLY (read-only object reads; never the live working tree, never `git log` bodies).
  `tools/review/anchor_map.py` is NOT in T: use `RD/R/kit/anchor_map.py` (run `python3 -I RD/R/kit/anchor_map.py
  RD/R/tree [PREFIX]`); its output at T is already in `RD/R/kit/anchor_map_memfn.tsv` (266 lines incl. header, 0
  STALE rows printed) and `anchor_map_all.tsv` (every file).

## Rulings the note must follow (quoted verbatim; their only record is a DENIED ledger)

Main's R-1 of 2026-11-24 (main's ruling of r91's RUL-13), verbatim:
"Q36's extraction trigger is NOT superseded. The 11-04 manifesto and plan-as-text seam split the kit internally
(planner vs emitter); they don't extract it from the repo. ARV-14 may still propose moving formhash.c/k1_ref.c out of
the product library on its OWN trigger, e.g. a measured library-size or link cost. Write it that way, not as "Q36
extraction"."

r92's RULING on G13 (record: `RD/R/subject/r92/review.md`, section RULING, second bullet) - read it there and quote it
from there.

Owner quotes the note relies on have their records in RD/R/tree (KIT-ARCH-STEP.md also at
RD/R/subject/KIT-ARCH-STEP.md; plan.md rows [IR-FORM] and [SP1D-KITSPLIT-SEAMS] - locate by `grep -n '^- \[TAG\]'`;
decisions.md D187 and others; docs/design/stream/manifesto.md). The owner's standing kit memories named by R-49 are
not readable on this box: rely on R-49's wording and the committed records that quote them.

## YOUR QUESTION (you are the round's only critic, so you verify every quote yourself)

(1) FIX-INDUCED. For each of r92's G1-G12 and G14: does rev 3's fix hold, and did it introduce a new error (a new
    read, a hand, a row, a check, a layout decided outside §8, a contradiction with another section, a count that is
    wrong)? Check through the first-unit counts C-40 and C-60..C-71, RE-RUN at T: for each, does it print what the
    note says, and is the count FLOOR (name list), SHAPE (regex over a construct) or CEILING (also matches comments)?
    What spelling does each regex miss? Do sizes agree between §7, §8 and each section?
(2) RULING. Every sentence of §9. Part 2 (ARV-16, options C/D, applying r92's G13 ruling) must be NEUTRAL: the ruling
    says the note "says what ARV-16 costs and what it buys, and keeps the leaning neutral", and the owner's words are
    not argued away. Every owner and main quote in the note (all sections, not only §9) must be WORD FOR WORD against
    its record; name the record file:line for each, and list drifts.
(3) ROW KINDS for ARV-1, ARV-14 and ARV-18: is each register row the note proposes of the right KIND (architecture.md
    KINDS OF ROW), in the register's columns, with an event that can fire, and - for a noted deviation - "small" in
    judgement (e)'s sense (one site)? Does ARV-14's trigger follow R-1 above?

Arch mode does NOT review algorithms, code, measurements or build cost. Outside the question's scope, report only
what a scoped item makes wrong.

MINIMUM: a finding is CONFIRMED only with the COMMAND (or the quoted record line with file:line) that shows it,
observed vs expected. Anything else is SUSPECTED with what would confirm it.

## DENYLIST (do not open, grep or list)

- `docs/dev/lanes/archrev_*`, `archrev2_*`, `archrev3_*` (the architect lanes' reports) anywhere, in any tree or
  commit.
- `memfn/docs/journal.md` entries dated 2026-11-24, and `memfn/docs/responses.md` items about R-48/R-49 (RD/R/tree's
  copies are already truncated before them; never read the repo's copies at any other commit).
- `git log` bodies beyond subject lines; job logs; the box queue; any worktree (`/Users/claude/pcrec/worktrees/*`);
  the live repo working tree generally (use RD/R/). `RD/.coord/` (the coordinator's notes).
- If you grep anything beyond RD/R for any reason, use
  `--exclude=journal.md --exclude=responses.md --exclude='archrev_*' --exclude='archrev2_*' --exclude='archrev3_*'`
  (plain grep ignores git pathspecs); for `git grep`, add `':!memfn/docs/journal.md' ':!memfn/docs/responses.md'
  ':!docs/dev/lanes/archrev*'`.

## Output format

- Your findings file RD/fixind/findings.md is PRE-CREATED (it exists, with headings). APPEND to it (Edit, or a
  shell `>>`); NEVER overwrite it with Write (the harness refuses a subagent's whole-file Write; the file stays empty).
- Append each finding the moment you have it, one append per finding: id `FIX-n` (part 1), `RUL-n` (part 2),
  `ROW-n` (part 3); CONFIRMED (the command or quoted lines, observed vs expected) or SUSPECTED (what would confirm
  it); severity (answer / speed / size / maintenance / doc / design); effort; blast radius; note § / file:line at T;
  the r92 G-id it relates to. A finding against a ruled D-row cites it and argues, or drops.
- Also append, under `## G map`, one line per G1-G12, G14: HOLDS / PART (what is left) / NEW ERROR (finding id).
- End with `## PROBED-AND-HELD` (what you checked that holds, with counts: commands re-run, quotes checked), then
  the line `CRITIC COMPLETE` last.
- Then run: `/Users/claude/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-claude/scratch/crit-memfn-archrev3 --deliver
  /var/tmp/pcrec-claude/scratch/crit-memfn-archrev3/fixind/DELIVER.txt fixind` and fix what it reports until it prints
  `lanecheck: DONE rc=0` ("DONE rc=1" is a failure).
- A failed final reply is EXPECTED for a nested agent and needs no escalation: the CRITIC COMPLETE line is the
  delivery. Final reply at most 150 words. If your findings-file append is REFUSED, SendMessage your findings to the
  coordinator at once, marked relayed.
