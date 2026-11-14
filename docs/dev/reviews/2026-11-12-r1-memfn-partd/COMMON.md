# COMMON brief: critic round partd (design), 2026-11-12

## Scope mandate (binding)

- Work ONLY inside the pcrec repo (/home/pcrec/projects/pcrec) and, read-only, pcrec-bench.
  Scratch ONLY under /var/tmp/pcrec-pcrec/scratch/crit-partd/<your-lens>/ (create it). NEVER /tmp
  (export TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-partd/<your-lens> before any gcc).
  Do not create, modify or delete files anywhere else; do not edit either repo; no commits.
- READ-ONLY critic. NEVER run `make`, any suite or runner script (run_g2*.sh, run_finder.sh,
  run_presence.sh, mech, emit_sweep, make test-*), `scripts/monread`, `scripts/boxqueue`, or anything
  over the whole corpus. You may run `build/pcrec` / `build/pcrec-harness` single compiles,
  `gcc -S`/`gcc -c` on single files, run a single generated matcher on a few subjects, and build
  small single-file drivers with one gcc call. BUDGET: at most ~150 compiles total, run
  sequentially (never parallel), every compile `nice`d. It is the owner's evening hold
  (20:00-01:00) on a shared box: light probes only.
- Kill only with `scripts/safekill PID`. Never `pkill -f`/`pgrep -f`.
- Do not `cd` into worktrees/ (a hook blocks it): use absolute paths, `git -C`, or a
  `( cd X && ... )` subshell.
- Never open the PCRE2 reference source. Oracle for answers: python3 `re`, or `pcre2test` if
  `command -v pcre2test` finds it.
- If you launch a subagent (you should not need to), restate this mandate and the denylist.

## Subject (DESIGN mode)

- The document: `docs/design/memfn/part_d.md` at commit 5999409e311a3c66532661c199a8c7b22283cbe4
  (branch lane/memfn-pdesign). Read it with
  `git -C /home/pcrec/projects/pcrec show 5999409e3:docs/design/memfn/part_d.md`
  (a copy: /var/tmp/pcrec-pcrec/scratch/crit-partd/part_d.md). It is the kit's DESIGN answer to the
  request "R-38 Part D, SCHEDULED (2026-11-12)" in memfn/docs/requests.md (line 886 at main).
  This round is the LAST before a BUILD GO.
- BUILD TREE = main 35bee4da94de622d4e7bf66097e059310c0be63b (the design's own base; K38-2 landed,
  `MF_SITE_ABI` 27, `MF_CLASS_V` 9). Every code cite in the design is to be checked AT THIS COMMIT.
- CLIENT design (in force at the freeze, identical on main and the subject branch, commit
  14570db62): `docs/design/run_pos_set_stage3_readiness.md` — pcrec's side of the same landing
  ([RUN-POS-SET] stage 3). Its §2.2 names the kit sites K-1/K-2/K-3, §2.3 the abi event and spec
  hunks, §3 the witness patterns, §5 the request text, §6 its questions. NOTE: it cites code at
  `lane/memfn-k382:` line numbers; that branch is merged into main, line numbers may have moved.
- Design of record for the run's seam: `docs/design/memfn/span_runs_sheet.md` rev 1.3 at
  35bee4da9 (§1 goals, §2.1-§2.5, §3.3, §4, §5, §5.1 numbers + the `[k382]` addendum).
- Kit code: `memfn/src/{window.c, presence.c, finder.c, precheck.c, ofsskip.c, runcmp.c,
  compose.c, gate.c, vrun.c, options.def, kit.h}`, `memfn/include/memfn.h`; pcrec's side:
  `src/gen/emit_dfa.c` (`req_site_define`, `pcrec_cover_site` / `cover_window` in src/gen/known.c),
  `src/gen/memfn_sites.c`, `src/facts/req.c`. Kit tests: `memfn/tests/` (g2/, run_g2*.sh),
  `tests/memfn/` (occurrence_oracle.py, row_floors.tsv, decider_census.tsv), `memfn/data/cards/`.
- The design cites code BY FUNCTION NAME. Find each with `git -C /home/pcrec/projects/pcrec grep -n -p`.

## Trees and binaries (built by the coordinator; do NOT rebuild)

- Review tree: /home/pcrec/projects/pcrec/worktrees/crit-partd (detached at 35bee4da9):
  `build/pcrec`, `build/pcrec-harness`, `build/libpcrec.a`, objects in `build/obj/`.
- Spellings checked by the coordinator (one compile each):
  `build/pcrec -p rx -e utf8 -o DIR/out.c --pattern '[α-ω]foo'` (C to a file);
  `build/pcrec -p rx -e utf8 --emit-facts --pattern 'PAT'` (listing to stdout, NO -o);
  `--emit-main` for a runnable matcher; all-tie regime = run from INSIDE the tree via a subshell
  `( cd /home/pcrec/projects/pcrec/worktrees/crit-partd && build/pcrec -p rx -I tests/findings/adversarial --analysis=uniform -o DIR/out.c --pattern PAT )`;
  the probe lever = `build/pcrec-harness --harness=run-tie-left ...`; deny arms `--memfn=no-NAME`
  (unknown names are refused: list them with `build/pcrec --list-axes`); `-fmemfn-simd`; `-fcomments`.
  Useful stamps in the emitted C: `RX_REQ_RUN`, `RX_REQ_WHY`, `RX_MEMFN_FORMS`.
- NOTE: no build with wide run positions exists (pcrec's stage 3 is not built). Where the design's
  claim is about what WILL happen, reason from the code at 35bee4da9 and say "INFERRED"; where you
  can make the code reach the state (a crafted pcrec pattern, a single-file driver calling the kit
  through memfn.h with a hand-built `mf_site`/statement, or a plant), do so and say "MEASURED".
- PLANTS / DRIVERS: never edit the tree. Copy a source file into your scratch dir, edit it there,
  compile with the Makefile's CFLAGS (read the Makefile; `make -n` is FORBIDDEN), `ar` replace the
  member in a COPY of `libpcrec.a` in your scratch dir, re-link a copy of the binary (`cli/main.c` +
  the copied archive, one gcc call). At most ~8 plants. Record each plant compile's exit code.

## Rulings (frozen; read via git show at main 35bee4da9, never the live tree)

- `git -C /home/pcrec/projects/pcrec show 35bee4da9:docs/dev/decisions.md` (also copied to
  /var/tmp/pcrec-pcrec/scratch/crit-partd/decisions.md): D76 line 5600, D77 5675, D94 6572, D144
  8968 (item 4: a byte-moving kit change carries its own deny), D147 9016, D153 9266, D157 9389
  (facts not methods), D174 9920 (names describe behaviour), D187 10068 + addendum 1 (positions as
  sets; a COVERING cube is a reader's private test, never a verified claim), D195 10187 (public
  option bits follow caller effect; dated 2026-11-12).
- plan.md at 35bee4da9: locate a row ONLY by `grep -n '^- \[TAG\]'` (e.g. RUN-POS-SET); never print
  its neighbours.
- The "F-8 ruling" (R recognized by shape, window.c `run_shaped`'s comment) is the kit manager's;
  its record is in the kit's (denied) ledgers. Treat window.c's comment text as its statement.
- The memory rule "a correctness fix gets no deny" (the design cites `pcrec-flag-follows-caller-effect`)
  is recorded in decisions as D195's context (the 2026-10-29 rule). The memfn deny rule:
  memfn/CLAUDE.md ("Every kit change that moves bytes carries its own deny (D144 item 4)").
- Allowed review context: docs/dev/reviews/2026-11-10-r1-k381.md, 2026-11-10-r2-k382a.md,
  2026-11-11-r1-k382.md (rulings of the preceding K38 units).

## Guide (review against these)

- docs/dev/guide/README.md, architecture.md (goals), coding.md, style.md, critics.md,
  docs/dev/learnings.md §3 (check design), docs/design/CLAUDE.md (standing questions),
  memfn/CLAUDE.md, memfn/src/CLAUDE.md, memfn/tests/CLAUDE.md, tests/memfn/CLAUDE.md,
  tests/mech/CLAUDE.md, docs/spec/ (the contract, D80; match_api.md, tuning.md).

## DENYLIST (do not open, grep, diff or print, by any means)

- docs/dev/lanes/ entirely (in particular pdesign_report.md, pdesign_deliver.txt)
- /var/tmp/pcrec-pcrec/scratch/memfn/ (in particular memfn/pdesign/), /var/tmp/pcrec-pcrec/scratch/s2prep/,
  any job log, the box queue, worktrees under worktrees/ other than crit-partd
- memfn/docs/journal.md, memfn/docs/responses.md, memfn/docs/wake.md, docs/dev/wake.md,
  docs/dev/owner.md, docs/dev/dev_journal.md (entirely)
- docs/dev/reviews/ other than the three files allowed above
- `git log` BODIES beyond subject lines (use `git log --format=%s`)
- /var/tmp/pcrec-pcrec/scratch/crit-partd/.coord/ and other critics' directories in the round dir
- Exclude these in EVERY git diff/grep, pathspec:
  `':!docs/dev/lanes' ':!memfn/docs/journal.md' ':!memfn/docs/responses.md' ':!memfn/docs/wake.md' ':!docs/dev/reviews' ':!docs/dev/wake.md' ':!docs/dev/owner.md' ':!docs/dev/dev_journal.md'`
  For PLAIN grep -r add:
  `--exclude-dir=lanes --exclude=journal.md --exclude=responses.md --exclude=wake.md --exclude=owner.md --exclude=dev_journal.md --exclude-dir=reviews --exclude-dir=worktrees --exclude-dir=.coord`

## Output format

- Your findings file DOES NOT EXIST YET: CREATE it as your FIRST action, with these headings:
  `# <lens> findings: partd`, `## Findings`, `## PROBED-AND-HELD`. Append each finding the moment
  you have it, ONE APPEND PER FINDING; never hold findings for the end.
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command or file:line, observed vs
  expected) or SUSPECTED (what would confirm it); severity (answer / speed / size / maintenance /
  doc / design); effort; blast radius; file:line at 35bee4da9 or part_d.md §. A finding against a
  ruled D-row cites it and argues, or is dropped.
- PROBED-AND-HELD: what you checked that held, with counts.
- Then run, from /home/pcrec/projects/pcrec,
  `scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-partd --deliver /var/tmp/pcrec-pcrec/scratch/crit-partd/<lens>.deliver <lens>`
  (the deliver file exists already); end only after it prints DONE. Fix and re-run if it does not.
- Final reply at most 150 words. If the Write of your findings file is REFUSED, SendMessage your
  findings to "crit-partd" at once (marked relayed); do not route around a refusal.
