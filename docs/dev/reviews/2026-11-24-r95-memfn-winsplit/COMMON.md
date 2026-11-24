# COMMON brief: critic round r95 memfn-winsplit (DESIGN mode), 2026-11-24

Read this whole file before your own brief.

## 1. Mandate (binding)

- Touch ONLY the pcrec repository, and in it you are READ-ONLY: no edits, no commits, no `git` writes
  (no checkout, stash, worktree, branch, fetch). NEVER run `make` or any test suite / runner script.
  You MAY run: `python3 -I` on the design's census instruments (they only read), `git show`/`git grep`/
  `git log --format=%s` (subject lines only), `grep`, `gcc-16 -fsyntax-only` probes of single C files
  (output to your own scratch dir), and `build/pcrec` from the review tree once it exists.
- Scratch ONLY under `RD/<your-lens>/` where `RD=/var/tmp/pcrec-claude/scratch/crit-memfn-winsplit`.
  Write nothing anywhere else on this machine (no /tmp, no home dir, no repo file).
- gcc on this Mac: `gcc-16` (Homebrew). Bare `gcc` is Apple clang: do not use it.
- Budget: at most 200 `gcc-16 -fsyntax-only` probes and 100 `build/pcrec` compiles per critic, total.

## 2. The subject

- DESIGN: `docs/design/memfn/window_split.md` and its instruments `docs/design/memfn/window_split/`
  (census.py, kitgraph.py, ents.py, bucket.py, home.py, plants.py, cut.spec, CLAUDE.md), at commit
  `0719e0a4d` on the kit branch lane/memfn-wsplit. Read-only copies: `RD/R/subject/window_split.md` and
  `RD/R/subject/window_split/`. The design's own section numbers (§1..§12) are how you cite it.
- WHAT IT IS: the design for splitting `memfn/src/window.c` (4,672 lines) plus the kit's position
  primitives (and presence.c's `kit_mass`) into small files, ONCE, as one answer-identical unit
  before NEON V (R-48). It is a MOVE: no emitted byte may change, and its gates must prove that.
- ITS ACCEPTED ARCHITECTURE NOTE: `memfn/docs/arch_review_2026-11.md` rev 4 (copy:
  `RD/R/subject/arch_review_2026-11.md`). The design answers that note's §8 hand-offs H1, H2, H3 and
  H8 (placement half). The note's site rows: A-s2 (ARV-9, the split), A-s5 (ARV-16, the primitives),
  B-s1 (ARV-5, the set family), and ARV-7 (the layer order / H8). STANDING RULE: a design that LEAVES
  the note's site map, or SKIPS a first unit the note orders, is a finding.
- THE REVIEW TREE (read code here): `T=/Users/claude/pcrec/worktrees/crit-memfn-winsplit`, a detached
  checkout of `0719e0a4d`. Run the instruments from `$T` exactly as the design writes them, e.g.
  `cd $T && python3 -I docs/design/memfn/window_split/census.py memfn/src docs/design/memfn/window_split/cut.spec --calls`
  (use a `( cd $T && ... )` subshell). A build of `$T/build/pcrec` (gcc-16) is being made by the
  coordinator; if you need the binary and `$T/build/pcrec` is absent, poll every 5 min (up to 2 h).
- WHERE THE BUILD WOULD LAND: on lane/memfn-wsplit, whose code equals `origin/main` `4d26eef02`
  (checked: `git diff 4d26eef02 0719e0a4d -- src memfn tests lib cli Makefile` is empty). The design
  measures at T = `a0f13ad83`; between T and `0719e0a4d`/`4d26eef02` the only code-side difference is
  `tools/review/anchor_map.py` (+ its CLAUDE.md line) ADDED after T. So every `window.c:N` cite in the
  design holds in `$T`. A cite that does NOT hold in `$T` is a finding.
- RULINGS IN FORCE at the freeze (read them with `git show 4d26eef02:<path>`, never the live tree):
  - D204 `[KIT-WINSPLIT]` (decisions.md line 10366 at `4d26eef02`; NOT present on the kit branch).
    Copy: `RD/R/subject/D204.md`. The owner's words, verbatim (2026-11-24):
    (1) "Split: how do you plan to split? If you anticipate this file growing, splitting out once
    rather then multiple times would be best. I'd rather have many small concisely defined files
    than larger sprawling ones".
    (2) "Split: yes on trigger but once you do split, make it count. Consider where reasonable the
    interface of the file. If there is a table and functions that search it specifically, they belong
    together in that file. Then the public names are just those functions."
    The readings main ACCEPTED (D204 Decision): split at NEON V's trigger, BEFORE NEON V, as its own
    answer-identical unit (byte identity over the corpus, G2 as control); the cut is fine-grained and
    made once; the primitives (ARV-5, ARV-16) move ONCE, in the split, to their final file, which takes
    `kit_mass`, so the presence<->window call cycle goes; THE FILE INTERFACE RULE (general, "where
    reasonable" kept): a table and the functions that search it live in one file; the table is
    file-static; the file's public names are only those functions. "Yes on trigger" is the DIRECTION;
    the build GO comes from the owner after this round.
  - Main's R-1 (quoted in the arch note's header, RULINGS THIS NOTE CROSSES): formhash.c and k1_ref.c
    stay as they are.
  - `docs/dev/plan.md` row `[KIT-WINSPLIT]` at `4d26eef02` (locate with
    `git show 4d26eef02:docs/dev/plan.md | grep -n -e '- \[KIT-WINSPLIT\] STATE'`, then read that
    row's own indented lines only, until the next `  - [` row; do not print its neighbours).
- GUIDE (the rules you review against): `docs/dev/guide/architecture.md` (goals, tier rules, the
  ride-along register), `docs/dev/guide/coding.md`, `docs/dev/guide/style.md`; `memfn/CLAUDE.md`,
  `memfn/src/CLAUDE.md`; `docs/design/CLAUDE.md` (the three standing design questions).

## 3. Denylist (do not open; exclude from EVERY grep and diff)

- `docs/dev/lanes/wsplitd_*` (the author's report/deliver/rulings), `docs/dev/lanes/archrev*`,
  `docs/dev/lanes/plantfix*`, `docs/dev/lanes/plantri*` (and `plantri_evidence/`).
- `memfn/docs/journal.md` and `memfn/docs/responses.md` (whole files, for this round).
- Review files on this subject (none exist yet), `git log` bodies (subject lines only), job logs,
  the box queue, every worktree other than `$T`, and `RD/.coord/` (the coordinator's notes).
- Ready exclude strings. git: `-- . ':!docs/dev/lanes/wsplitd_*' ':!docs/dev/lanes/archrev*'
  ':!docs/dev/lanes/plantfix*' ':!docs/dev/lanes/plantri*' ':!memfn/docs/journal.md'
  ':!memfn/docs/responses.md'`. Plain grep: `--exclude='wsplitd_*' --exclude='archrev*'
  --exclude='plantfix*' --exclude='plantri*' --exclude-dir='plantri_evidence' --exclude=journal.md
  --exclude=responses.md --exclude-dir=.coord`.
- The design says some evidence is "listed in the lane report" or "in the lane scratch" (the C-39
  comparison's 10 names, `fields.py`, `spec_v4`). You may NOT read it; a claim whose only evidence is
  outside the subject is something you may report as such.

## 4. The kit

- `RD/R/kit/anchor_map.txt`: `python3 -I tools/review/anchor_map.py .` run over `$T` (every mech
  sabotage row's anchor: row, file, line, enclosing function). This is the binding-check-by-location
  input: every function the design moves is in window.c or is presence.c's `kit_mass`.
- `RD/R/kit/plants.txt`: `python3 -I docs/design/memfn/window_split/plants.py .` over `$T` (every
  window.c/presence.c G2 plant and the line its FROM text matches; 0 = stale).
- Re-run any instrument yourself if a claim rests on it. An instrument's exit code is not evidence;
  read what it PRINTS.
- Pass shell patterns in single quotes or via a file.

## 5. Drill / topic assignment (one lens each; do not do another lens's topic)

- The design's OPEN CHOICES O1-O7 (§11): O1 frame's grain, O2 the planner's grain, O5 MARGIN's own
  file, O7 find->frame -> lens OWNER. O3 kit_tie_rule's shape, O6 U2b in or out -> lens SLOT.
  O4 the name window.c -> lens RDCHECKS. Each lens RECOMMENDS on its O-items, with reasons.
- Owner quotes word-for-word against the record (D204 at 4d26eef02): lens SLOT only.
- Sabotage rows, G2 plants, census rows, purity, rows_check plants, C15/C16, PROVENANCE, Makefile:
  lens RDCHECKS only. Byte-identity of each commit's CODE move, accessors, header, MF_NS collisions,
  commit order: lens RDCODE only.
- Every "today the tree does X" number and every "the existing X already does Y": lens PREMISE.
- The standing questions "sibling of a family" and "general form + unlocks (with triggers)": lens SLOT.

## 6. Output (YOUR FILE ALREADY EXISTS; append to it)

- Your findings file `RD/<lens>.md` is PRE-CREATED with headings `## Findings` and
  `## PROBED-AND-HELD`. APPEND to it (Edit, or a shell `>>`/heredoc append). Never overwrite it with
  Write (the harness refuses a subagent's whole-file Write and the file stays empty).
- Append each finding THE MOMENT you have it, one append per finding, under `## Findings`:
  id `<LENS>-n`; CONFIRMED (with repro: command, observed vs expected) or SUSPECTED (what would
  confirm it); severity (answer / speed / size / maintenance / doc / design); effort; blast radius;
  the design § (and `file:line` in `$T`). A finding against a ruled D-row cites the row and argues,
  or is dropped.
- Under `## PROBED-AND-HELD`: what you checked that held, with counts (names, rows, files).
- State the population each check covered (e.g. "all 59 anchors", "all 20 files"); a check over a
  partial population says so.
- Your LAST action on the file: append a line `CRITIC COMPLETE <lens> <time>`.
- Then run `/Users/claude/pcrec/scripts/lanecheck --dir RD --deliver RD/<lens>.deliver <lens>`; it
  PASSES only on `lanecheck: DONE rc=0` (it prints `DONE rc=1` on a failure: fix and re-run).
- Final reply at most 150 words. A failed final reply is EXPECTED for a nested agent and needs no
  escalation: the CRITIC COMPLETE line in your file is the delivery. If your file append is REFUSED
  by the harness, SendMessage your findings to "crit-memfn-winsplit" (the coordinator) at once, marked relayed.
