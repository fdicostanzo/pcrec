# COMMON brief — critic round r66 `l3fix` (CODE mode, light round, 3 critics)

## Scope mandate (binding)
- You touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and pcrec-bench, and you WRITE nothing in either.
  You are READ-ONLY: no edits, no commits, no `make`, no test suites, no `scripts/boxlock`/`boxqueue`.
- Your scratch is ONLY your own dir `/var/tmp/pcrec-pcrec/scratch/crit-l3fix/<lens>/` (never /tmp, never the repo).
  Set `OUT=/var/tmp/pcrec-pcrec/scratch/crit-l3fix/<lens>` for the kit scripts and `export PCREC_TMPDIR=$OUT`.
- You may run `build/pcrec` (any tree below), `gcc` / `gcc -S` on single emitted files, the kit scripts, and python3 -I.
  The box is SHARED (the owner works on it until 01:00; a census runs in the queue): run probes one at a time, `nice`.
- Your COMPILE BUDGET is stated in your own brief (a cmp.sh pair = 2 compiles). Stay under it and report the count.
- Never `cd` into a worktree in a compound command; use absolute paths.

## The subject
- SUBJECT = `dad0275802cc7589e0c0388769c62606ace6a709` (branch lane/l3chk), frozen.
- The delta under review = `git -C /home/pcrec/projects/pcrec log --oneline 3f02ca8ab..dad027580` (REVIEWED = `3f02ca8ab`,
  the state an earlier full round already reviewed). Review ONLY that delta. Three fix lanes' work:
  (1) a PICK RULE: TOP's BACK row (a required run that begins inside a lookbehind, K < 0) may displace the consumed
      run only under a `displaces` condition, keyed on `fwd_reentry` (`src/facts/req.c` `rb_top_back_displaces`,
      `src/facts/facts.c` `pf_derive_req_walk`, `src/facts/facts_derive.h` `ReqWalkParams.fwd_reentry`);
      dead K < 0 forward-scan texts deleted and replaced with internal errors (`src/gen/emit_dfa.c`
      `pf_emit_handoff`, `emit_unanchored`), one `omin` writer (`req_pres_spans`), `pcrec_bound_negative` (facts.h);
  (2) records/doc: `docs/design/span_arms.md` (§14.2 REV 3.4 note at ~line 1427, §14.4 L3 REV 3.4 addenda from
      ~line 2058, the main one "THE LOSS AGAINST BASE, AND THE PICK RULE" at ~line 2125), spec hunks
      (`docs/spec/facts_listing.md` §4.1.2¶8, `docs/spec/tuning.md` §2.41¶1/¶7a/¶8b, `docs/spec/match_api.md`),
      plan rows [L3-CONS-REENTRY] [L3-BACK-CLIP] [REQ-CAND-STRUCT] [LB-NEST-CAP] [L3-BOUNDED-RUN-REFINE],
      guide/critic-skill edits;
  (3) checks/pins: `tests/codegen/run_encoding_checks.sh` (DD12a(i)), `run_facts_checks.sh` ([facts-look]),
      `run_prechecks.sh`, `reqcube_check.py`, `run_cpset_structure.sh`, `run_recursion_identity.sh` (FILEPIN),
      `tests/codegen/manifests/k50_gate_refinement.txt`, `tests/memfn/d3_census.tsv`, `d3_floor.tsv`, and sabotage rows
      S1887 S3381 S3405 S3406 S3408 S3409 S3410 S3411 S3412 S3413 (re-aimed) and S3450 S3455 (new), under
      `tests/mech/sabotages/`.
- BASE (the answer/speed reference) = `694d91dc42140934dc7f00e631d3987d9e8ea0c3` = `git merge-base main lane/l3chk`.
- The whole branch vs BASE adds span_arms unit L3 (already reviewed). Only the delta is in scope, but an answer or
  speed loss against BASE that the delta leaves or creates IS in scope.

## Trees (all built)
| name | what | compiler |
|---|---|---|
| subject | review worktree at SUBJECT | /home/pcrec/projects/pcrec/worktrees/crit-l3fix/build/pcrec (and pcrec-harness) |
| reviewed | git archive of 3f02ca8ab | /var/tmp/pcrec-pcrec/scratch/crit-l3fix/reviewed/build/pcrec |
| base | git archive of BASE | /var/tmp/pcrec-pcrec/scratch/crit-l3fix/base/build/pcrec |
| plant:ROW | SUBJECT with sabotage ROW applied (ONLY the CHECK lens uses these) | /var/tmp/pcrec-pcrec/scratch/crit-l3fix/plants/ROW/tree/build/pcrec |
Read source with `git -C /home/pcrec/projects/pcrec show <commit>:path` or in the review worktree (read-only).

## Run kit: /var/tmp/pcrec-pcrec/scratch/crit-l3fix/kit/
- `pc TREE ARGS...` — run TREE's build/pcrec (TREE = base | reviewed | subject | plant:ROW).
- `cmp.sh 'PATTERN' [pcrec args]` — emitted C of TA (default base) vs TB (default subject) under the SAME basename in
  `$OUT/cmp/A` and `$OUT/cmp/B`; prints `c=SAME|DIFF stderr=...`. `TA=reviewed TB=subject kit/cmp.sh ...` to compare
  against the reviewed state. 2 compiles.
- `match.sh TREE 'PATTERN' 'SUBJECT' [pcrec args, e.g. --engine=vm]` — the emitted main's answer. 1 compile + gcc.
- `oracle.sh 'PATTERN' 'SUBJECT' [START]` — libpcre2-8's answer (`M start end [caps]` | `N`).
- Facts listing: `kit/pc subject --features all --emit-facts --pattern 'P'` (rows `req_whole_run`, `req_landmark_maxoff`).
- Routes: default, `--engine=vm`, `--engine=dfa` (where admitted), `-fno-req-handoff`; encodings `-e utf8`.
- Pass patterns in SINGLE QUOTES or via a file; check the `Pattern:` header of every emitted file you cite before
  claiming byte identity or a route.

## Rule text (quote the SUBJECT, never a paraphrase)
The pick rule's statement of record is span_arms.md §14.4 L3 "THE LOSS AGAINST BASE, AND THE PICK RULE" (SUBJECT,
~line 2125) and facts_listing.md §4.1.2¶8; the code comment on `rb_top_back_displaces` (req.c) restates it. The
manager's rulings R-1 and R-2 are quoted in span_arms.md ~lines 2169-2171. Read decisions.md / plan.md via
`git -C /home/pcrec/projects/pcrec show dad027580:docs/dev/decisions.md` (never the live tree).
Witness spellings the subject itself names (seed, not a limit): `(?<=qz)x?a:`, `(?<=foo)bar`, `-i (?<=foo)bar`,
`(?<=item )done`, `(?<=a)\Kb`, `(?>(?<=a)b)`, `(?<=x)qzjv[a-z]*\d`, `(?<=foobar)\d*x`, `(?<=qz)ab`, `(?<=ab)ab(\w)\1`,
`(?<=a)(b)\1x`, `ab(c)\1x`, `(?<=xyz)a+xyz`.

## Guide (the rules you review against)
docs/dev/guide/coding.md, architecture.md, style.md, critics.md; docs/dev/learnings.md §3 (checks).

## DENYLIST (do not open, grep, diff or list)
- `docs/dev/lanes/l3feat*`, `l3tri*`, `l3r65*`, `l3r65tri*`, `l3enc*`, `l3chk*` (lane reports/rulings, in ANY tree;
  they ARE inside the subject's diff — exclude them).
- `docs/dev/reviews/2026-11-20-r65-l3feat.md` and `docs/dev/reviews/2026-11-20-r65-l3feat/`.
- `/var/tmp/pcrec-pcrec/scratch/crit-l3feat/`, this round's `.coord/` dir, other critics' lens dirs.
- every worktree other than `worktrees/crit-l3fix`; the box queue and its logs; job logs; `git log` bodies (subject
  lines only: `git log --format=%s`).
- Git diff pathspec excludes (use on EVERY diff/grep):
  `':!docs/dev/lanes/l3*' ':!docs/dev/reviews/2026-11-20-r65-l3feat*'`
- Plain grep excludes: `--exclude='l3feat*' --exclude='l3tri*' --exclude='l3r65*' --exclude='l3enc*' --exclude='l3chk*' --exclude='2026-11-20-r65-l3feat.md' --exclude-dir='2026-11-20-r65-l3feat' --exclude-dir=.coord`
- Commit subject lines name findings of the earlier round by letter ("review r65 A"); that is the subject's own
  text and fine to read; do not seek the earlier round's file.

## Output format
- Your findings file `<lens>/findings.md` is PRE-CREATED with headings. APPEND to it (Edit, or `>>`); NEVER overwrite
  it with Write (the harness refuses a subagent's whole-file Write and the file stays empty).
- Append each finding THE MOMENT you have it, one append per finding.
- Each finding: id `<LENS>-n`; CONFIRMED (repro: input, exact command, observed vs expected) or SUSPECTED (what would
  confirm it); severity (answer / speed / size / maintenance / doc / design); effort; blast radius; file:line or §.
  A finding against a ruled D-row or R-ruling cites it and argues, or drops.
- End with `## PROBED-AND-HELD` (with case counts), your compile count, the MINIMUM/LONGEST witness you probed, then
  the line `CRITIC COMPLETE`.
- Then run `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-l3fix --deliver
  /var/tmp/pcrec-pcrec/scratch/crit-l3fix/<lens>/deliver.txt <lens>` and end when it prints DONE.
- Final reply at most 150 words. A failed final reply is EXPECTED for a nested agent; the findings file is the
  delivery, no escalation needed. If your findings append is refused, SendMessage the findings to the coordinator at
  once, marked relayed.
