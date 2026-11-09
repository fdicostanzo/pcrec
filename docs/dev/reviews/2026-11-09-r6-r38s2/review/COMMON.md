# COMMON brief — critic round r38s2 (design RE-CHECK before a build go)

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and pcrec-bench, READ-ONLY. No edits to either repo,
  no commits, no worktrees of your own. Never `make`, never a suite, never `scripts/boxqueue`/`boxlock`.
- Scratch ONLY under your own dir /var/tmp/pcrec-pcrec/scratch/crit-r38s2/<lens>/ (create it). Never /tmp.
  Set `PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-r38s2/<lens>` for any script you run.
- Work in the main tree only through `git show <commit>:<path>` / `git -C`; never `cd` into worktrees/ (a hook
  blocks it; a `(cd X && ...)` subshell is fine). Bound uncertain commands with `timeout 120`.
- Compile budget: about 150 `build/pcrec` compiles per critic (a BASE/other compare pair counts 2). You may
  compile single matchers with gcc into your scratch dir and run them. libpcre2 oracle: python3 `re` is not PCRE
  and `pcre2test` is absent; libpcre2 is installed (`/usr/lib/x86_64-linux-gnu/libpcre2-8.so.0`): call it via
  a small `python3 -I` ctypes script in your scratch dir, or state the answer as UNVERIFIED.

## Subject (frozen)
- `docs/design/memfn/span_runs_sheet.md` **rev 1** at commit `e0c9bf109` (branch `lane/memfn-r38s`, head
  `0135bc89a`). Read it ONLY as `git -C /home/pcrec/projects/pcrec show e0c9bf109:docs/design/memfn/span_runs_sheet.md`.
  Rev 0 (for the diff of what changed) is `0de3cadec`:
  `git -C /home/pcrec/projects/pcrec diff 0de3cadec e0c9bf109 -- docs/design/memfn/span_runs_sheet.md`.
- It is the memfn kit's interface sheet answering pcrec's request R-38 (the necessary run crosses the pcrec->kit
  seam as ONE uncut span; the kit replies one decision: scan position + verified extent; signed `omin`/`head_max`;
  the earned skip as pcrec's decision). Rev 1 applies review r2 r38s AS RULED.
- **The claims you re-check**: the RULED previous review on main, `docs/dev/reviews/2026-11-09-r2-r38s.md`:
  its findings F1-F11 and its "Manager rulings (2026-11-09)" section (line ~209). The sheet's Revision log (top)
  says where each was applied. (You MAY read that review's sibling dir `docs/dev/reviews/2026-11-09-r2-r38s/`.)

## Build tree (code cites)
- **`lane/u3mech` `404cff6ea`** (the joint U2+U3 tree about to land on main; the sheet's own base). A clean
  review tree is built there ONCE: `/home/pcrec/projects/pcrec/worktrees/crit-r38s2/` with
  `build/pcrec` (and `build/libpcrec.a`). Read code there (absolute paths) and run that binary.
- Main HEAD at the freeze: `90ab55fd3` (main is NOT an ancestor of u3mech; u3mech lands on main next).
- Parallel kit unit 3.0a: `lane/memfn-s30a` `e95cd7aef`, unmerged, base `73075a9d1`; its own diff is
  `git diff 73075a9d1 e95cd7aef`. It changes the same pick/verify path (`memfn/src/compose.c`, `window.c` ...).
  Note any cite that differs there. `docs/design/memfn/plan_frame.md` exists ONLY on s30a
  (`git show e95cd7aef:docs/design/memfn/plan_frame.md`).

## Rulings and client designs in force (read via `git show 90ab55fd3:<path>`, never the live tree)
- `docs/dev/decisions.md` D191 (line 10119), D187 (+ add. 1), D172, D157, D124, D80, D76/D94 (abi ritual).
- `docs/design/span_arms.md` (main `2f0ea0b69`): §5.2-§5.5, §8, §8.1, §8.2, rulings §12a (:1182), §12c (:1194),
  §12b (:1198).
- `memfn/docs/requests.md` "## R-38" (line 859) on main.
- Spec tier: `docs/spec/match_api.md`, `docs/spec/tuning.md`, `docs/spec/facts_listing.md`, `docs/spec/findings.md`
  (at the build tree or main; say which).
- Guide: `docs/dev/guide/critics.md`, `docs/dev/learnings.md` §3 (controls sharing a source).

## Regimes (spellings checked with one compile each)
- default: `W/build/pcrec -p rx -o OUT.c --pattern 'P'` (W = the review tree). Stamps: `grep 'REQ_RUN\|REQ_BYTE\|REQ_WHY\|REQ_HANDOFF' OUT.c`.
- facts listing: `W/build/pcrec --emit-facts --pattern 'P'` (rows `req_run`, `req_whole_run`, `req_run_maxoff`, `run_pin`).
- VM route: add `--engine=vm`. Deny arms: `--memfn=no-X`.
- all-tie: run FROM the review tree: `(cd W && ./build/pcrec -I tests/findings/adversarial --analysis=uniform -p rx -o OUT.c --pattern 'P')`.
- Example at the build tree: `xabcdefghijkq` -> `RX_REQ_RUN "65666768696a6b71@7"`, `RX_REQ_WHY "dominated"`;
  `--emit-facts`: `req_whole_run 786162636465666768696a6b71`, `req_run 65666768696a6b71@7`, `req_run_maxoff 5`, `run_pin 5`.

## Denylist (never read, diff or grep these)
`docs/dev/lanes/r38s*`, `memfn/docs/lanes/r38s*`, `memfn/docs/journal.md`, `memfn/docs/responses.md`,
`docs/dev/full_suite_ledger.md`, `worktrees/.boxqueue/`, every worktree other than `worktrees/crit-r38s2`,
`/var/tmp/pcrec-pcrec/scratch/memfn/`, `/var/tmp/pcrec-pcrec/scratch/crit-r38s/` (the previous round's RAW dir;
its RULED review on main is allowed), this round's `.coord/` dir, other critics' dirs in this round, `git log`
bodies beyond subject lines, job logs. In EVERY git diff/grep exclude them as pathspecs, e.g.
`git grep ... -- . ':!docs/dev/lanes/r38s*' ':!memfn/docs/lanes/r38s*' ':!memfn/docs/journal.md' ':!memfn/docs/responses.md' ':!docs/dev/full_suite_ledger.md'`;
for plain `grep -r` use `--exclude=journal.md --exclude=responses.md --exclude='r38s*' --exclude=full_suite_ledger.md --exclude-dir=.boxqueue`.

## Output format
- Your findings file DOES NOT EXIST YET: CREATE it as your FIRST action with these headings:
  `# <LENS> — r38s2`, `## Findings`, `## Answers to the round's questions` (if your brief has any),
  `## PROBED-AND-HELD`. Then APPEND each finding the moment you have it, one append per finding.
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command, observed vs expected, or the quoted
  file:line) or SUSPECTED (what would confirm it); severity (answer / speed / size / maintenance / doc /
  design / check); effort; blast radius; sheet § and file:line. A finding against a ruled D-row or a ruled
  r2 r38s disposition cites it and argues, or drops.
- PROBED-AND-HELD: what you checked that holds, with case counts.
- If your file Write is refused, SendMessage your findings to the coordinator at once, marked relayed; never
  route around a refusal.
- END: run `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-r38s2 --deliver
  /var/tmp/pcrec-pcrec/scratch/crit-r38s2/<lens>_deliver.txt <lens>` until it prints DONE; then a final reply of
  at most 150 words.
