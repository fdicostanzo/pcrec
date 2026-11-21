# COMMON brief — critic round covs2d (DESIGN mode)

Read this whole file first. Then your own short prompt names your ONE question and your output file.

## Scope mandate (binding)

- Touch ONLY the two mandated repositories, /home/pcrec/projects/pcrec and /home/pcrec/projects/pcrec-bench,
  and READ them only. You edit NOTHING in either repo (no file, no branch, no worktree, no commit).
- Your scratch goes ONLY under your own lens directory `R/<lens>/` where
  `R=/var/tmp/pcrec-pcrec/scratch/crit-covs2d`. Never write anywhere else (not /tmp, not $HOME).
  Export `PCREC_TMPDIR=R/<lens>` before running any repo script.
- You are READ-ONLY: never run `make`, a test suite, a sweep over the corpus, `scripts/boxqueue`, `scripts/boxlock`,
  or any timing/perf measurement. Box rule tonight: the box is in the owner's evening hold until 01:00 box clock.
  ALLOWED: single-pattern compiles with the built compiler, `gcc -c`/`gcc -S` of one emitted file, small
  probes; cap ~300 compiles for your whole run (a pattern x mode x encoding matrix: state the PRODUCT before
  you run it). A finding that needs a timing or a full sweep is written SUSPECTED with the exact command that
  would confirm it.
- Do not launch subagents.

## The subject (frozen)

- `R/subject/cover_cap.md` — docs/design/cover_cap.md **rev 5** at commit `1408c147725315b9b306540b2b6be34dffa873d5`
  (branch lane/covs2d; NOT on main). Under review: its NEW **§11** (STAGE 2 ADDENDUM, lines 699-914) and the
  rev-5 edits elsewhere: the header status lines, the G4 note in §0, the §3.5 stage-2 bullet, §4.3, §7.
  `R/subject/rev5.diff` is exactly the rev-5 change against rev 4.1 (`R/subject/cover_cap_rev4_main.md`, the
  version on main, commit 61f8e9f88). Sections 0-10 are stage 1's design, already reviewed and BUILT; read them
  as context and as the text §11 must stay consistent with.
- This round is BOTH the first review of §11 AND the last check before the stage-2 build go.
- Two commits matter:
  - `61f8e9f88` — the commit §11 measured against (it writes `$PC` = a build at 61f8e9f88; stage 1, abi 108).
  - **BUILD = `b9b9e8635`** = main HEAD at the freeze, where a stage-2 build would land. Main moved between the
    two (mostly memfn/ and tests/memfn/, plus `src/core/internal.h` and `src/gen/memfn_sites.c`). Any code §11
    cites that MOVED between them is a finding. See: `git -C /home/pcrec/projects/pcrec diff --stat 61f8e9f88 b9b9e8635 -- src memfn lib cli tests/kitproof tests/registry`.
- The review tree (built once, do not rebuild): `/home/pcrec/projects/pcrec/worktrees/crit-covs2d` (detached at
  b9b9e8635) with `build/pcrec`, `build/pcrec-harness`. Read source there or via
  `git -C /home/pcrec/projects/pcrec show b9b9e8635:<path>`.
- §11 cites "every today-number carries its command in docs/dev/lanes/covs2d_report.md (T-n)". That report is
  DENIED to you. Judge each number on what the subject itself gives, and re-run it yourself with the kit.

## Run kit (`R/kit/`, already tested)

- `source R/kit/env.sh` gives `$PC`, `$PCH` (harness binary), `$BUILD`, `$KIT`.
- `R/kit/facts.sh PATTERN [-e utf8] [-i]` — the `--emit-facts` `cover` section rows:
  `encoding  why  k  exact_len  sets` (sets cut to 100 chars). Example: `a{40}(?:b|cc)` -> `byte statement-fits 41 41 ...`.
- `R/kit/emit.sh OUTDIR MODE PATTERN [pcrec args]` — MODE `def` (default build), `kp`
  (`pcrec-harness --harness=kit-proof`, the cover route forced as the kitproof rows do), `eng`
  (`--memfn=no-window-search`). Prints rc, `RX_DFA_SCAN`, emitted C bytes, `gcc -O2` `.text`. One call = 1 compile.
- `R/kit/ans.sh WORKDIR MODE FLAGS PATTERN SUBJECT...` — answers (every start offset + find-all) vs libpcre2
  10.46 (`R/kit/oracle`); FLAGS `-` or `u` (utf8), `i`. Use a WORKDIR under your own lens dir.
- Encodings: default = byte; `-e utf8`. Compare two emitted files only under the SAME basename in two dirs.

## Rulings and records (read the FROZEN copies)

- `R/subject/decisions.md`, `R/subject/plan.md`, `R/subject/plan_completed.md` — at b9b9e8635. Never read the live
  tree's copies. Rows: D157 (`grep -n '^## D157' ...`), D174, D198, D77, D146/D147, D80, D94; plan rows
  `[COVER-CAP]`, `[IFACE-PUSH]`, `[EARNED-SKIP]` (plan.md, `grep -n '^- \[TAG\]'`), `[OPT-DIAL]` (in
  plan_completed.md: CLOSED 2026-09-19). Also `[MATCH-KNOWN]` if you need it.
- `R/subject/memfn_requests.md` — the kit's request ledger at b9b9e8635 (R-40..R-44 show the shape of a filed request).
- `R/subject/memory/*.md` — the manager's standing-rule notes the subject cites by name (one-pass loss chasing,
  general mechanisms not special cases, apples-to-apples, measurement card, flag follows caller effect, no silent
  defaults, suspect tuning constants, iface push later, build under measurement, kit facts not methods, names
  describe behaviour). These are owner rulings recorded by the manager.
- Spec and guide (in the review tree): `docs/spec/limits.md`, `docs/spec/facts_listing.md`, `docs/spec/tuning.md`,
  `docs/spec/cli.md`, `docs/spec/match_api.md`; `docs/dev/guide/{README,architecture,coding,style,critics}.md`;
  `docs/design/CLAUDE.md` (the standing questions for designs); `src/core/limits.def`, `src/core/limits.h`,
  `cli/CLAUDE.md` (harness lever rules), `tests/registry/limits_check.sh`, `tests/kitproof/`, `src/gen/known.c`,
  `src/gen/known.h`, `src/gen/memfn_sites.c`, `src/gen/emit_dfa.c`, `memfn/include/memfn.h`.

### The owner's words the subject rests on (VERBATIM; their only record, the journal, is DENIED to you)

From docs/dev/dev_journal.md, 2026-11-15 (quoted sentences only):
- 14:10, Frank verbatim: "1. reading dfa for the span is fine. In my goal of partial span proofs that means either
  rebuilding the dfa on the remainder or editing out the proven span states. 2. set in limits. If it's a user setting
  it could be shorter then adjusted by the user per artifact."
- 14:35, Frank verbatim: "2. stage 2 is fine. 3. we have a performance dial for pcrec. it could include some options
  for the kit. Also, I would default to sub span loops (excepting the measured head inline ) then measure if inline
  was faster than the other way around. Measure three: all inline, all loops, header inline then loops. Then the speed
  dial option can be always inline should it prove that is faster".
- 14:50, BUILD GO, Frank verbatim: "Go on all stages" ([COVER-CAP] stage 1 and stage 2, design rev 4.1). The
  manager's record of the same entry: "Stage 2: kit request to file (span up to 4095; owner's rendering direction;
  per-artifact span limit) + a short stage-2 design addendum and its critic round before the stage-2 build lanes."
- 15:00, Frank verbatim: "I predict most all rx will only have a short span and will inline due to being under the
  inline head portion of the prover. Therefore, this issue is mostly moot".
- Session-132 evening record (manager, on review r9 EMITTED-2): "with Frank, LAND then time; the remedy if slower is
  the class-run cover length (old exact length 24)."

From review r9 (DENIED to you), finding EMITTED-2, the sentences the subject cites, verbatim:
"EMITTED-2: the class-run cover form advances one byte on a failed verify, which is O(k) per byte on dense near
misses." / "`dig-exact-32` on (31 digits + `g`) repeated, `perf stat -e instructions:u` `taskset -c 7`, 3 repeats:
BASE 230.7 M, SUBJECT 1,534.8 M (×6.65). On `z`*n: +14 %."

## DENYLIST (never read, never grep into)

- `docs/dev/lanes/covs2d*`, `docs/dev/lanes/covs1*`, `docs/dev/lanes/covcap*`, `docs/dev/lanes/land1115*`
- `docs/dev/reviews/2026-11-15-r2-covcap0*`, `2026-11-15-r5-covcap-r2*`, `2026-11-15-r6-covcap-r3*`,
  `2026-11-15-r7-covcap-r4*`, `2026-11-15-r9-covs1*`, `2026-11-15-r11-covs1f*` (files AND same-named dirs)
- `docs/dev/dev_journal.md`, `docs/dev/wake.md`, `docs/dev/owner.md`, `memfn/docs/journal.md`,
  `memfn/docs/responses.md`
- the worktree `worktrees/covs2d` and every other worktree except `worktrees/crit-covs2d`; job logs; the box queue;
  `git log` bodies beyond subject lines; other `crit-*` round dirs under /var/tmp/pcrec-pcrec/scratch/
- `R/.coord/` and other critics' lens directories.
- Every git diff/grep you run EXCLUDES the denied paths. Git pathspec form:
  `':!docs/dev/lanes' ':!docs/dev/reviews' ':!docs/dev/dev_journal.md' ':!docs/dev/wake.md' ':!docs/dev/owner.md' ':!memfn/docs/journal.md' ':!memfn/docs/responses.md'`.
  Plain grep -r form (git pathspecs do not apply to it):
  `--exclude-dir=lanes --exclude-dir=reviews --exclude=dev_journal.md --exclude=wake.md --exclude=owner.md --exclude=journal.md --exclude=responses.md --exclude-dir=worktrees`.

## Output (your findings file)

- Your file DOES NOT EXIST YET: CREATE it as your FIRST action with these headings:
  `# <LENS> — covs2d`, `## Findings`, `## PROBED-AND-HELD`, and write it INCREMENTALLY: **append each finding to
  your file the moment you have it, one append per finding.**
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command, observed vs expected) or SUSPECTED (what
  would confirm it); severity (answer / speed / size / maintenance / doc / design); effort; blast radius; the
  subject's § (and line) and any file:line. A finding against a ruled D-row cites the row and argues, or is dropped.
- The file ends with `## PROBED-AND-HELD` (what you checked that held, with case counts).
- If your Write of the findings file is REFUSED, SendMessage your findings to the coordinator at once, marked
  "relayed"; if a harness rule refuses it, do not route around it: return the findings as your final text.
- Before ending, run
  `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-covs2d --deliver /var/tmp/pcrec-pcrec/scratch/crit-covs2d/<lens>_deliver.txt <lens>` (your findings file is `R/<lens>/findings.md`)
  and fix until it prints DONE. Final reply: at most 150 words.
