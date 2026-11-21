# COMMON brief — critic round covs2e (DESIGN mode, short re-check)

Read this whole file first. Then your own short prompt names your ONE question and your output file.
`R=/var/tmp/pcrec-pcrec/scratch/crit-covs2e`.

## Scope mandate (binding)

- Touch ONLY the two mandated repositories, /home/pcrec/projects/pcrec and /home/pcrec/projects/pcrec-bench,
  and READ them only. You edit NOTHING in either repo (no file, no branch, no worktree, no commit).
- Your scratch goes ONLY under your own lens directory `R/<lens>/`. Never write anywhere else (not /tmp, not $HOME).
  Export `PCREC_TMPDIR=R/<lens>` before running any repo script.
- READ-ONLY: never run `make`, a test suite, a sweep over the corpus, `scripts/boxqueue`, `scripts/boxlock`, or
  any timing/perf measurement. The box is in the owner's evening hold until 01:00 box clock. ALLOWED:
  single-pattern compiles with the built compiler, `gcc -c`/`gcc -S` of one emitted file, small probes; cap ~300
  compiles for your whole run (state the PRODUCT of any pattern x mode x encoding matrix before you run it; a
  BASE/SUBJECT pair counts 2). A finding that needs a timing, a suite or a full sweep is SUSPECTED with the exact
  command that would confirm it.
- Do not launch subagents. Pass patterns in SINGLE QUOTES or via a file, and check the `Pattern:` header of any
  emitted file you cite before reporting a byte-identity or route claim (shell quoting eats backslashes).

## The subject (frozen)

- `R/subject/cover_cap.md` — docs/design/cover_cap.md **rev 5.1** at commit
  `342ae6586d9ac85611829df54b6af070da518806` (branch lane/covs2e; NOT on main).
- `R/subject/rev5_to_rev5.1.diff` — exactly the change under re-check (rev 5 -> rev 5.1);
  `R/subject/cover_cap_rev5.md` is rev 5 (commit 1408c1477). Under re-check: §11 (the stage-2 addendum), its new
  §11.2.1 (the per-compile valued option `--window-search-width=N`), the kit request draft §11.5, and the sentences
  rev 5.1 changed in sections 0-10. Stage 1 (sections 1-10's design) is BUILT and on main; read it as context.
- The rev 5.1 header paragraph "REVISION 5.1" lists the fix ids F1..F31 with one-line descriptions, and the body
  tags each fix site `(F<n>)`. That list is the ONLY list of claimed fixes; the review that raised them is DENIED.
- **BUILD = main `e0c4c3816c3817a95f1c21b52a24e37409016229`** = main HEAD at the freeze, where a stage-2 build would
  land (stage 1 built, abi 108, the kit's finder unit merged). The subject cites code at main `469d4205c` and at
  review r13's tree `b9b9e8635`; `git -C /home/pcrec/projects/pcrec diff --stat b9b9e8635 e0c4c3816 -- src lib cli memfn tests`
  prints nothing, so the subject's file:line cites should hold at BUILD verbatim. A cite that does not is a finding.
- Review tree (built once, do NOT rebuild): `/home/pcrec/projects/pcrec/worktrees/crit-covs2e` (detached at
  e0c4c3816) with `build/pcrec`, `build/pcrec-harness`. Read source there.
- Main's cloud CI on the kit merge is red and under triage by another lane: NOT a finding, do not investigate it.
- The subject cites `docs/dev/lanes/covs2d_report.md` (T-n today numbers) and `covs2e_report.md` (the by-id map):
  both DENIED. Re-run any number yourself from the command the subject gives beside it (a number with no command is
  a finding).
- One reading is marked **LEAN, OWNER QUESTION OPEN** (§9 Q7: does the limit bound the cover ROUTE or the proof).
  Judge the document UNDER that lean. Do NOT raise the open question itself as a finding. Likewise §11.2.1's
  "stamp: NONE (MANAGER DECISION OPEN, lean none)" — judge under the lean.

## Run kit (`R/kit/`, tested at BUILD)

- `source R/kit/env.sh` gives `$PC`, `$PCH` (harness binary), `$BUILD` (the review tree), `$KIT`.
- `R/kit/facts.sh PATTERN [-e utf8] [-i]` — the `--emit-facts` `cover` section rows: `encoding why k exact_len sets`.
  Checked: `a{40}(?:b|cc)` -> `byte statement-fits 41 41 ...`; `a{33}` -> `statement-fits 33 33`.
- `R/kit/emit.sh OUTDIR MODE PATTERN [pcrec args]` — MODE `def` (build/pcrec), `kp` (`pcrec-harness
  --harness=kit-proof`, cover route forced as kitproof rows do), `eng` (`--memfn=no-window-search`). Prints rc,
  `RX_DFA_SCAN`, emitted C bytes, `gcc -O2` `.text`. One call = 1 compile. Checked: `[0-9a-f]{33}` def ->
  `scan=unanchored`.
- `R/kit/ans.sh WORKDIR MODE FLAGS PATTERN SUBJECT...` — answers (every start offset + find-all) vs libpcre2 10.46
  (`R/kit/oracle`); FLAGS `-`, `u` (utf8), `i`. Checked: `[0-9a-f]{32}` def -> cover, OK vs libpcre2.
- The option `--window-search-width` does NOT exist at BUILD (it is what the design proposes). To see what a
  wider width WOULD do you can only reason from the code; `kp` mode forces the cover where the stage-1 seam allows.

## Rulings and records (read the FROZEN copies, at e0c4c3816)

- `R/subject/docs_dev_decisions.md`: D76 (line 5600, addenda 5641/5671), D77 (5675), D80 (5775), D94 (6572,
  addenda 6686/7747), D157 (9389), D174 (9920), D198 (10227). Read by line; never the live tree's copy.
- `R/subject/docs_dev_plan.md`: `[COVER-CAP]` (290), `[EARNED-SKIP]` (523), `[SIZE-KNEE]` (608), `[IFACE-PUSH]`
  (1570). Locate rows with `grep -n '^- \[TAG\]'` only. `R/subject/docs_dev_plan_completed.md`: `[OPT-DIAL]` (4548).
- `R/subject/memfn_docs_requests.md` — the kit's request ledger at the freeze; R-40..R-44 (lines 925-955) show the
  shape of a filed request.
- `R/subject/memory/*.md` — the manager's standing-rule notes the subject cites by name.
- Spec and guide (review tree): `docs/spec/{limits,tuning,cli,match_api,facts_listing}.md`;
  `docs/dev/guide/{README,architecture,coding,style,critics}.md`; `docs/design/CLAUDE.md`; `docs/design/kit_proof.md`;
  `src/core/limits.def`, `src/core/limits.h`, `src/core/compile.c`, `src/core/compound.c`, `src/dump/limits_dump.c`,
  `cli/main.c`, `cli/CLAUDE.md`, `lib/pcrec.h`, `lib/CLAUDE.md`, `tests/registry/limits_check.sh`, `tests/kitproof/`,
  `tests/axes/run_axes.sh`, `tests/mech/sabotages/`, `src/gen/known.{c,h}`, `src/gen/memfn_sites.c`,
  `src/gen/emit_dfa.c`, `src/gen/emit_vm.c`, `memfn/include/memfn.h`.
- The owner's words: the subject QUOTES them verbatim (§11 head, §11.3, §11.5, §9 Q8); their record (the journal) is
  DENIED and the subject's quotes are all you get. Same for review r9's EMITTED-2 numbers the subject quotes.

## DENYLIST (never read, never grep into)

- `docs/dev/lanes/covs2d*`, `covs2e*`, `covs1*`, `covcap*`, `land1115*`, `tri1115*`
- `docs/dev/reviews/2026-11-15-r13-covs2d*`, `2026-11-15-r2-covcap0*`, `2026-11-15-r5-covcap-r2*`,
  `2026-11-15-r6-covcap-r3*`, `2026-11-15-r7-covcap-r4*`, `2026-11-15-r9-covs1*`, `2026-11-15-r11-covs1f*`
  (files AND same-named dirs)
- `docs/dev/dev_journal.md`, `docs/dev/wake.md`, `docs/dev/owner.md`, `memfn/docs/journal.md`,
  `memfn/docs/responses.md`
- `worktrees/covs2d`, `worktrees/covs2e`, and every worktree except `worktrees/crit-covs2e`; job logs; the box queue;
  `git log` bodies beyond subject lines; every other round dir under /var/tmp/pcrec-pcrec/scratch/ (crit-covs2d
  included)
- `R/.coord/` and other critics' lens directories.
- Every git diff/grep you run EXCLUDES the denied paths. Git pathspec form:
  `':!docs/dev/lanes' ':!docs/dev/reviews' ':!docs/dev/dev_journal.md' ':!docs/dev/wake.md' ':!docs/dev/owner.md' ':!memfn/docs/journal.md' ':!memfn/docs/responses.md'`.
  Plain grep -r form: `--exclude-dir=lanes --exclude-dir=reviews --exclude=dev_journal.md --exclude=wake.md --exclude=owner.md --exclude=journal.md --exclude=responses.md --exclude-dir=worktrees --exclude-dir=build`.
  `docs/dev/lanes/covs1_evidence/predict.py` is named by the subject (A6) and IS readable; nothing else under lanes/.

## Output (your findings file)

- Your file `R/<lens>/findings.md` DOES NOT EXIST YET: CREATE it as your FIRST action with headings
  `# <LENS> — covs2e`, `## Findings`, `## PROBED-AND-HELD`, and write it INCREMENTALLY: **append each finding the
  moment you have it, one append per finding.**
- Each finding: id `<LENS>-n`; CONFIRMED (repro: input, command, observed vs expected; or the quoted lines) or
  SUSPECTED (what would confirm it); severity (answer / speed / size / maintenance / doc / design); effort; blast
  radius; the subject's § (and line) and any file:line at BUILD. For the readiness lenses, also name the BUILD UNIT
  (A-item or B-item) it blocks and whether it is a TEXT fix or needs redesign. A finding against a ruled D-row cites
  the row and argues, or is dropped.
- The file ends with `## PROBED-AND-HELD` (what you checked that held, with case counts), and a final line
  `VERDICT: ready | ready with listed text fixes | not ready` for what your question covers.
- If your Write is REFUSED, SendMessage your findings to the coordinator at once, marked "relayed"; if a harness rule
  refuses it, do not route around it: return the findings as your final text.
- Before ending run
  `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-covs2e --deliver /var/tmp/pcrec-pcrec/scratch/crit-covs2e/<lens>_deliver.txt <lens>`
  and fix until it prints DONE. Final reply: at most 150 words.
