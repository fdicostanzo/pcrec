# COMMON brief: critic round s1 (code), post-landing review

You are a READ-ONLY critic in an adversarial review. Read this whole file before your own brief.

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and pcrec-bench (/home/pcrec/projects/pcrec-bench), both READ-ONLY for you. Never edit, commit, merge, checkout or stash in either.
- Write ONLY under your own dir `/var/tmp/pcrec-pcrec/scratch/crit-s1/<lens>/` (named in your brief). Never /tmp, never $HOME, never the repo tree. Export `PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-s1/<lens>` for any script you run.
- Never `cd` into a worktrees/ path in a compound command (a hook blocks it); use absolute paths or a `( cd X && ... )` subshell.
- Kill nothing (no pkill/pgrep -f). Bound any run that may hang: `timeout 20 ./prog ...`.

## BOX RULES (owner's evening hold, until 01:00)
- NO `make`, no suites, no harness scripts, no mech, no sweeps. Run single compiles only: `nice -n 19 $P ...` and `nice -n 19 gcc -O2 ...` on single generated files.
- Budget: at most ~100 pcrec compiles per critic (a BASE/SUBJECT pair counts 2), single-threaded, never in parallel.

## Subject (frozen)
- SUBJECT = `3da0d446bfe5e73002109bb6ccf64b230b185140` (branch lane/s1land, already merged to main as 51481d1b3; this is a post-landing review, findings become fix lanes).
- BASE = `3b52b096db90f066e42c18126e101942e71f5e55` (main at the lane's fork point).
- Review the diff `git -C /home/pcrec/projects/pcrec diff BASE SUBJECT -- . ':!docs/dev/lanes' ':!docs/dev/history/claude_md'`.
- Two features:
  1. **NEVER-MATCH**: under `--engine=auto`, a VM HYBRID (VM engine behind a DFA prefilter) whose prefilter machines admit no match is emitted as the DFA engine's EMPTY artifact (`RX_ENGINE "dfa"`, `RX_DFA_SCAN "empty"`) instead; new fact `never_matches` (`--emit-facts`), values `empty-machine` / `no`. Code: src/core/compile.c (the switch after `machines_final`), src/facts/kset.c `pcrec_never_matches`, src/ir/dfa.c (two predicates moved out of emit_dfa.c), src/facts/facts.*.
  2. **FIND-MINW**: searches stop where fewer bytes remain than the proven minimum match width W (W >= 2): (a) DFA unanchored route's search entry (`pcrec_emit_min_width_check`, after the end-window clamp, before the pre-check), (b) the DFA forward scan's candidate-start filter: `pf_close` in src/gen/emit_dfa.c ends the search when `subject_length - pos < W` after the filter lands, (c) VM entry check + VM attempt loop bound `attempt_max = subject_length - W` (src/gen/emit_vm.c `vm_emit_search_body`). W = the `width` fact's `bmin` on DFA routes, the VM's `root_minw` on the VM route (`cand_min_width`). WIDTH table rows: `ceiling`, `min-width` (new), `width-none` (now on all routes). Test-only inverse lever `--harness=no-min-width` (only in `build/pcrec-harness`).
- Contract text: the spec hunks in the diff: docs/spec/tuning.md §2.55, docs/spec/match_api.md §6.3.4 (`"empty"`, `"selected"`), docs/spec/facts_listing.md §4.1.2¶12. Goals (what the owner asked for): the two plan rows AS FILED, read at BASE only: `git -C /home/pcrec/projects/pcrec show BASE:docs/dev/plan.md | grep -n -A6 '^- \[NEVER-MATCH\]'` and the same for `\[FIND-MINW\]`, plus `git show BASE:docs/design/plan_row_bodies/NEVER-MATCH.md`. Ruling files (decisions.md, plan.md) are read ONLY via `git show e066d8ef5:<path>` (the rulings freeze), never the live tree.
- Rules to review against: docs/dev/guide/ (coding.md, architecture.md, style.md, critics.md), docs/spec/match_api.md (entries §3, error codes §4, UTF §9), D26 (decisions.md: compatible with PCRE2 on what matches).

## Tools
- There is NO BASE binary (do not build one). SUBJECT binaries are prebuilt in the review tree `W=/home/pcrec/projects/pcrec/worktrees/crit-s1`: `P=$W/build/pcrec`, `PH=$W/build/pcrec-harness` (accepts `--harness=...`). The BEFORE behaviour of FIND-MINW is reproduced with `$PH --harness=no-min-width ...` (the lever declines the min-width row). The BEFORE behaviour of NEVER-MATCH is reproduced with `--engine=vm -fprefilter` ONLY where that gives the old hybrid; better: compare against PCRE2 (the oracle) and against the spec.
- Enable all syntax with `--features all` (else `\b` etc. are refused with "requires module"). Compile: `nice -n 19 $P --features all -p rx -o DIR/x.c --pattern 'PAT'` (`-e utf8` for UTF-8; `-i`-style options per docs/spec/cli.md; `-fcomments` to keep comments). `--emit-main` appends a main taking the subject as argv[1] (exit 0 match, 1 no match). For a nonzero start offset or captures, write a tiny C driver calling `int rx_search(const unsigned char *s, size_t n, size_t startpos, ptrdiff_t (*caps)[2])` (match_api.md §3; `rx_match(const rx_ctx*)` is the other entry family). `--emit-facts` prints the facts listing; `--emit-ir` the VM program listing.
- Oracle: libpcre2-8 is installed (`libpcre2-8.so.0`); a ctypes wrapper exists at tests/subst/d27/lib/ref_pcre2.py (read it; copy what you need into your dir; run python with `-I`). python3 `re` is a weaker fallback.
- To compare BASE vs SUBJECT emitted C under the lever, use the SAME basename (`-p rx`) in two dirs and `diff`.

## Denylist (D27 applied to review): do NOT open, grep, diff or `git show` these
- `docs/dev/lanes/` (every file: lane reports, deliver and rulings files; e.g. nevermatch_report.md, nmfix_report.md, minw_report.md, minwfix_report.md, s1land_report.md, reqlast_report.md, reqpast_*). A code comment citing one of them is NOT an invitation to open it.
- `docs/dev/history/claude_md/` , `docs/dev/dev_journal.md`, `docs/dev/wake.md`, `docs/dev/owner.md`, `docs/dev/reviews/`, `memfn/docs/journal.md`, `memfn/docs/responses.md`.
- every `worktrees/` directory except `worktrees/crit-s1`; the box queue and job logs (`scripts/boxqueue`, `$PCREC_TMPDIR/queue*`, any `*.log` outside your dir); `git log` message BODIES (subject lines OK).
- the coordinator's dir `/var/tmp/pcrec-pcrec/scratch/crit-s1/.coord/` and other critics' dirs.
- Exclude them from every search: git: `':!docs/dev/lanes' ':!docs/dev/history/claude_md' ':!docs/dev/dev_journal.md' ':!docs/dev/wake.md' ':!docs/dev/owner.md' ':!docs/dev/reviews' ':!memfn/docs/journal.md' ':!memfn/docs/responses.md' ':!worktrees'`; plain grep: `--exclude-dir=lanes --exclude-dir=reviews --exclude-dir=worktrees --exclude-dir=claude_md --exclude=dev_journal.md --exclude=wake.md --exclude=owner.md --exclude=journal.md --exclude=responses.md`. Prefer `grep -rn ... /home/pcrec/projects/pcrec/worktrees/crit-s1/src` (the review tree IS the subject).

## Output (mandatory shape)
1. Your findings file `findings.md` in your dir DOES NOT EXIST YET. CREATE it as your FIRST action, with headings `# <lens> findings`, `## Findings`, `## PROBED-AND-HELD`.
2. APPEND each finding the moment you have it, one append per finding. Each finding: id `<LENS>-n`; CONFIRMED (with repro: pattern, flags, subject, start offset, command, observed vs expected/oracle) or SUSPECTED (what would confirm it); severity (answer / speed / size / maintenance / doc / design); effort; blast radius; file:line or spec §. A finding against a ruled D-row cites it and argues, or drops.
3. End the file with PROBED-AND-HELD: what you probed that held, with case counts.
4. Before ending, run `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-s1 --deliver /var/tmp/pcrec-pcrec/scratch/crit-s1/<lens>/deliver.txt <lens>` and fix until it prints DONE. Then end; final reply at most 150 words.
5. If a Write to your findings file is REFUSED, do not route around it: SendMessage your findings to the coordinator (crit-s1) at once (marked relayed), or return them as your final text.
