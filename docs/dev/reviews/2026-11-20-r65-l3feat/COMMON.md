# COMMON brief — critic round r65 `l3feat` (CODE mode)

Read this whole file first. Then do the ONE question your own prompt names.

## Scope mandate (binding)

- Touch ONLY the pcrec and pcrec-bench repositories (/home/pcrec/projects/{pcrec,pcrec-bench}) — and you
  edit NEITHER: you are READ-ONLY on both. Your only writes go under YOUR OWN lens directory
  `/var/tmp/pcrec-pcrec/scratch/crit-l3feat/<lens>/` (already created for you, with your findings file).
  Never /tmp, never $HOME, never anything else on this machine.
- NEVER run `make`, `make test`, a suite (other than the ONE-.rxt harness run below), `scripts/boxlock`/`boxqueue`,
  or the mech matrix. Allowed: the kit below, the built binaries, `gcc`/`gcc -S` on single files, `perf stat`,
  `git show`/`git grep`/`git diff`, python3 `-I` scripts that only read (or write only under your lens dir).
- GNU `timeout` on every command of uncertain run length (the kit's scripts already bound their compiles and
  runs). A deep or hostile pattern (nesting > 50, a repeat count > 1000) only under
  `/home/pcrec/projects/pcrec/scripts/watchdog -s 120 -m 2g -c 120 -S <label> -- <cmd>`.
- Never `cd` into a worktree in a chained command (a hook blocks it): use absolute paths, `git -C`, or a
  `( cd X && ... )` subshell. Run everything under `nice`. Never more than 2 processes at once.
- Pass patterns in SINGLE quotes or via a file; before reporting any byte-identity or route claim, check the
  `Pattern:` header of each emitted file you cite.
- HARD TIME LIMIT (the box has timing jobs tonight): stop all probing by **20:15** box time (`date`), and have your
  file finished with `CRITIC COMPLETE` and lanecheck run by **20:25**. Append findings as you go, so a stop
  loses nothing.

## The subject (frozen)

- SUBJECT = branch `lane/l3feat` = `3f02ca8ab3af595d369709d9a42794584c9d8415`.
  BASE = merge-base with main = `694d91dc42140934dc7f00e631d3987d9e8ea0c3`. The last three subject commits are
  report/evidence (denied, below); review the CODE as `git diff 694d91dc4 3f02ca8ab`.
  Ready diff command (denied paths excluded):
  `git -C /home/pcrec/projects/pcrec diff 694d91dc4 3f02ca8ab -- . ':!docs/dev/lanes' ':!docs/dev/history/claude_md/docs__dev__lanes.md'`
  Code: `src/facts/{req.c,kset.c,facts.c,facts.h,facts_derive.h}`, `src/enc/{enc.h,enc_byte.c,enc_utf8.c}`,
  `src/gen/emit_dfa.c`. Contract: `docs/spec/{match_api.md,tuning.md,facts_listing.md}`, `docs/dev/history/abi_changelog.md`
  (abi 109 -> 110). Tests: `tests/litscan/{spanarms.rxt,presence_deny.rxt,gen_presence_deny.py}`, `tests/codegen/*`,
  `tests/rxtsource/run_rxtsource_tests.sh`, `tests/startset/{vmhat_checks.py,manifests/*}`, 16 sabotage rows under
  `tests/mech/sabotages/` (S3405-S3413 new; S453, S693, S1706, S1887, S1956, S3075, S3383 changed).
- WHAT THE UNIT IS (lookaround unit L3, "BACK"): a POSITIVE LOOKBEHIND's fixed bytes join the required run, so
  the run can begin BEFORE the match start; K (`req_landmark_maxoff`, `RX_REQ_HANDOFF`) becomes SIGNED
  (K = -B, B the lookbehind bytes in the run). The run has a CONSUMED EXTENT `[cons_lo, cons_hi)`; `req_byte` and
  the run pin read only that extent. The handoff moves (entry and re-entry) get a K < 0 row: an end clamp
  (`if (len - hit < B) return 0;`) and a move to `hit + B`; the re-entry's re-ask condition is per sign. The kit is
  told the run's signed `omin` (`req_pres_spans`). abi 109 -> 110.
- THE DESIGN OF RECORD: `docs/design/span_arms.md` at the SUBJECT (`git -C /home/pcrec/projects/pcrec show
  3f02ca8ab:docs/design/span_arms.md`): §14.4 "L3 — BACK" (from the line `#### L3 — BACK`) INCLUDING its
  `[REV 3.3, lanes l3feat/l3feat2, ruling R-1 ...]` addendum at that section's end, and the §14.3 decisions it cites
  (D-4 TOP's rows, D-5/D-6 the consumed extent, D-7 K's states and `omin`, D-8 the move table, D-11 `lb_bytes`,
  D-13 the spec hunk list, D-16 the K comments); §14.2 (predicted movers); §5.7 (witnesses W-L*, W-T3a, W-S4c).
  The accepted architecture note: `docs/design/req_lookaround_arch.md` (at the subject).
- ACCEPTED INTERIM STATE (do not report these as findings; they are ruled): (1) L2 (AHEAD) is NOT built: a
  pattern with both a lookbehind and a lookahead does not join the lookahead side at L3 — §14.4 L3: "No row with both
  a lookbehind and a lookahead moves at L3 (`(?<=foo)bar(?=baz)` stays `foobar` at −3: the `++ rg` clause is L2's)".
  (2) Ruling R-1 (its only record is the REV 3.3 addendum quoted above): "the forward scan's re-entry is DECLINED at
  K < 0" — the prefilter `handoff` row refuses at K < 0 (`req_k_reentry_sound`), so the start-byte row takes it;
  that SPEED loss is ruled. Whether the DECLINE is COMPLETE (every route on which the refuted argument is still
  used) is in scope.
- A ruling "R-2" (a three-build measurement) is cited by the lane but has NO record you may read; treat it as
  unknown, do not hunt for it.
- Guide: `docs/dev/guide/README.md`, `coding.md`, `style.md`, `architecture.md`, `critics.md`;
  `docs/dev/learnings.md` §3 (check design). Read guide files from the review tree.
- Rulings: read `docs/dev/decisions.md` and `docs/dev/plan.md` ONLY as
  `git -C /home/pcrec/projects/pcrec show adea38104:<path>` (main's last commit to them at the freeze; never the
  live tree). In play: D80 (spec in the same change), D76/D94 (emitted text change = abi event + every reader of
  the number), D191.2 (the kit may scan any run position; `req_byte` is a consumed byte), D26, D77. Plan row:
  `git -C /home/pcrec/projects/pcrec show adea38104:docs/dev/plan.md | grep -n '^- \[REQ-LOOKAROUND\]'` (that line only).
  The CONTRACT lens is the ONE lens that checks ruling/design quotes word for word against their record; others cite.

## DENYLIST (do not open, grep or diff these; exclude them from EVERY command)

- Everything under `docs/dev/lanes/` whose name starts `l3feat` (the lanes' report, deliver and rulings files, and
  the directory `docs/dev/lanes/l3feat_evidence/`); simplest: exclude all of `docs/dev/lanes/`.
- `docs/dev/history/claude_md/docs__dev__lanes.md` (it summarises the lane reports).
- `docs/dev/reviews/2026-11-20-r63-l3remodel*` (file and directory) and `/var/tmp/pcrec-pcrec/scratch/crit-l3remodel/`.
- Every scratch dir `/var/tmp/pcrec-pcrec/scratch/l3feat*` and `/var/tmp/pcrec-pcrec/scratch/l3build*`; every
  other scratch dir except this round's.
- `git log`/`git show` commit BODIES: use `git log --format='%h %s'` and `git show --format= <commit> -- <paths>`.
- The box queue and its job records/logs (jobs 301/302 of this subject above all); any cloud branch or run named
  l3feat; every worktree under `/home/pcrec/projects/pcrec/worktrees/` except the review tree `crit-l3feat`; the
  live `docs/dev/dev_journal.md`, `wake.md`, `owner.md`.
- `/var/tmp/pcrec-pcrec/scratch/crit-l3feat/.coord/` (the coordinator's notes) and OTHER critics' lens dirs.
- Ready pathspec excludes for git diff/grep:
  `-- . ':!docs/dev/lanes' ':!docs/dev/history/claude_md/docs__dev__lanes.md' ':!docs/dev/reviews/2026-11-20-r63-l3remodel*'`
  For PLAIN `grep -r`: `--exclude-dir=lanes --exclude=docs__dev__lanes.md --exclude='2026-11-20-r63-l3remodel*' --exclude-dir='2026-11-20-r63-l3remodel*' --exclude-dir=.coord`.

## The review tree and the run kit (all built; do not rebuild)

- Review tree (SUBJECT, built): `W=/home/pcrec/projects/pcrec/worktrees/crit-l3feat` (`build/pcrec`,
  `build/pcrec-harness`). BASE tree (git archive of 694d91dc4, built clean): `/var/tmp/pcrec-pcrec/scratch/crit-l3feat/base`.
- Kit dir `K=/var/tmp/pcrec-pcrec/scratch/crit-l3feat/kit`. Scripts that write need `OUT=<your lens dir>/<sub>`
  EXPORTED. TREE everywhere = `base | subject | plant:<ID>`, or `base-h | subject-h | plant-h:<ID>` for the
  `pcrec-harness` binary (needed for `--harness=restore=look`, the test-only lever that restores the walk's
  lookaround arm to its pre-L1 form).
  - `$K/pc TREE ARGS...` — TREE's compiler. Lookaround needs `--features all`. `--emit-facts` prints the facts
    listing (`req_whole_run`, `req_landmark_maxoff` = K, `req_byte`, the `RX_*` stamps).
  - `OUT=... $K/cmp.sh 'PATTERN' [pcrec args]` — BASE vs SUBJECT `-p rx --features all` C under the SAME basename
    (`$OUT/cmp/A/rx.c` base, `$OUT/cmp/B/rx.c` subject); prints `c=SAME|ABI-ONLY|DIFF stderr=... rcA rcB`
    (ABI-ONLY = differs only in 109 vs 110). 2 compiles.
  - `OUT=... $K/match.sh TREE 'PATTERN' 'SUBJECT' [pcrec args]` — compiles, links `kit/drv.c`, and calls
    `rx_search(subject, n, start, caps)` for EVERY start 0..n: `start: M s e` | `start: N` | `start: E rc`.
    `SUBJECT_HEX=...` env for arbitrary bytes. 1 compile + 1 gcc.
  - `$K/oracle.sh 'PATTERN' 'SUBJECT' [OPTS]` — libpcre2-8 (10.46) for every start 0..n, same line shape, after
    an `OK ncaps` line. OPTS = p2probe letters (`u` UTF for `-e utf8`, `i` caseless for `-i`, `m`, `s`, `x`).
  - `OUT=... $K/diff3.sh 'PATTERN' 'SUBJECT' OPTS [-- pcrec args]` — oracle | base | subject per start, then
    `VERDICT subject=OK|WRONG(n) base=OK|WRONG(n)` (a pcrec `E -7`, the contract's refusal of a mid-character
    start under utf8, is not counted). 2 compiles + 2 gcc. CHECKED: `(?<=foobar)\d*x` on `xfoobar9xfoobarx`
    → both OK; under `plant:S3405`, `foobar12x` from 0 answers `N` (oracle M 6 9).
  - ROUTES: default (auto: a lookbehind selects the VM; the VM hybrid's inlined DFA prefilter fronts it,
    `RX_VM_PREFILTER "hybrid"`); `--engine=vm` (no DFA prefilter: the VM attempt loop, its pre-check and its
    re-entry); `-fno-prefilter`; `-fno-req-handoff` (removes every handoff row). `--engine=dfa` REFUSES a lookbehind.
    Encodings: default `byte`; `-e utf8`. Find-all: per-start answers from `match.sh` determine the non-empty
    find-all sequence; if you need the artifact's own iterator, `rx_next` is in the header (`$OUT/match/rx.h`).
  - PLANTS (CHECK lens only): `/var/tmp/pcrec-pcrec/scratch/crit-l3feat/plants/<ID>/tree/` = the SUBJECT tree with
    that sabotage row's every SAB_BEFORE -> SAB_AFTER edit applied (`apply.log`) and `build/pcrec` +
    `build/pcrec-harness` rebuilt (`plants/STATUS`: all 16 built). IDs: S453 S693 S1706 S1887 S1956 S3075 S3383
    S3405 S3406 S3407 S3408 S3409 S3410 S3411 S3412 S3413.
  - ONE-`.rxt` HARNESS RUN (~30 s for spanarms.rxt):
    `( cd <your lens dir> && PCREC=<tree>/build/pcrec CC=gcc PROCS=2 PCREC_TMPDIR=<your lens dir> timeout 600 nice bash $W/tests/harness/run.sh <path to the .rxt> 2>&1 | grep -E 'cases (passed|failed)' )`.
    CHECKED controls: `tests/litscan/spanarms.rxt` on the review tree = 2130 passed, 0 failed; under plant S3405 =
    2115 passed, 15 failed. At most 20 harness runs per critic.
  - SCOPED IDENTITY SWEEP (EMITTED lens only):
    `( cd <lens dir> && python3 -I $W/scripts/emit_sweep.py --ref-bin /var/tmp/pcrec-pcrec/scratch/crit-l3feat/base/build/pcrec --bin $W/build/pcrec --tree $W --no-corpus --patterns-file <file> --out <lens dir>/sw_<name> --jobs 2 --streams c-default,c-vm )`
    (read its `--help` first). CAP: 2 sweeps, N <= 400 patterns each.
- Budgets per critic: compiles at most ~1,000 in total (cmp.sh = 2, match.sh = 1, diff3.sh = 2, a sweep = N x 2
  streams x 2 trees). State the PRODUCT of any matrix next to the cap before you run it.
- Callers of the changed EMITTING functions (assigned to the MOVE lens alone): `emit_req_move_open`
  (emit_dfa.c:1191 entry `emit_req_handoff_rest`, :8066 `emit_req_landmark_move`); `emit_req_landmark_move`
  (:8026 `pf_emit_handoff`, the forward scan; :8105 `pcrec_emit_req_attempt_reentry`, the VM attempt loop, called
  from emit_vm.c:13971); `emit_req_reentry_use` (:8058, and the NEW :14199 landmark init in `emit_unanchored`);
  `emit_req_handoff_rest` (:1820).

## Output format (binding)

- Your findings file ALREADY EXISTS (pre-created, with headings): `<lens dir>/findings.md`. APPEND into it (Edit, or
  a shell `>>` / heredoc append) — NEVER overwrite it with a whole-file Write (the harness refuses a subagent's
  whole-file Write and the file stays empty). Append each finding the moment you have it, one append per finding,
  under `## Findings` (above `## PROBED-AND-HELD`).
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, exact command, observed vs expected) or SUSPECTED
  (what would confirm it); severity (answer / speed / size / maintenance / doc / design); effort; blast radius;
  file:line (at SUBJECT) or spec §/¶. A finding against a ruled D-row or ruling cites it and argues, or drops.
- State the MINIMUM WITNESS LENGTH / population your probes reached (patterns, subjects, starts); a clean result
  below a witness's size is not evidence.
- The file ends with a `## PROBED-AND-HELD` section (what you tried that held, with case counts), then the line
  `CRITIC COMPLETE`.
- Then run `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-l3feat --deliver <lens dir>/deliver.txt <lens>`
  and end only when it prints `DONE rc=0` (on `DONE rc=1` it lists what is missing: fix and re-run). A lens with no
  findings writes `No findings.` and one line saying why under `## Findings`.
- Final reply: at most 150 words. A failed final reply is EXPECTED for a nested agent and needs no escalation: the
  `CRITIC COMPLETE` line in your file is the delivery. If an append to your findings file is REFUSED, SendMessage
  the findings to `crit-l3feat` at once, marked relayed; do not route around the refusal.
