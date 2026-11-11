# COMMON brief — critic round vlb2 (design): variable lookbehind STAGE 2

Read this whole file before anything else. Your per-lens prompt names your ONE question.

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and pcrec-bench (/home/pcrec/projects/pcrec-bench, you should not need it).
- You are READ-ONLY on both repos. Write files ONLY under your own dir
  `/var/tmp/pcrec-pcrec/scratch/crit-vlb2/critics/<LENS>/` (never /tmp, never the repo).
  Run scratch compiles with `PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-vlb2/critics/<LENS>` exported.
- NEVER run `make`, `make test`, any suite, sweep or battery, and never `scripts/boxlock`/`boxqueue`.
  A FULL SUITE is running on this box: run SINGLE compiles only (`build/pcrec` on one pattern, `gcc -c`/`-S`
  on one generated file, one artifact run), prefixed with `nice`, sequentially, at most ~300 compiles total.
- Never kill a process. Never read PCRE2 source code (D181: only a pcre2-reader agent may); running the
  INSTALLED libpcre2 runtime through the ctypes binding below is fine and is the oracle.
- `cd` only inside a `( ... )` subshell; prefer absolute paths.

## The subject (frozen)
- Design document: `docs/design/vlookbehind.md` at commit `63250b5cb15ed41da9c10b2e065db3c4b6161ce0`
  (read it with `git -C /home/pcrec/projects/pcrec show 63250b5cb:docs/design/vlookbehind.md`; the file is unchanged at main HEAD).
- SCOPE: **stage 2 only** = §6 "Stage 2: backreferences in a lookbehind (B+)" (search for that heading)
  and every section it cites (§5.2 width rule and its "exact" paragraph and refusal shapes, §0 G1 incl. the
  zero-width divergence, §5.1a's "stage-2 backreferences" bullet, §6 gates 1-3 as they apply to stage 2,
  §8 population, §9 D27 extract, §10 spec hunks marked stage 2, §13 Q3, the §3 backref row).
  Stage 1 is BUILT; review it only where stage 2 builds on it.
- BUILD TREE (where a stage-2 build would land) = main HEAD `dc198806932da1bb9b30a9425ce91b7daacb843e`,
  checked out read-only at `/home/pcrec/projects/pcrec/worktrees/crit-vlb2/` and ALREADY BUILT:
  `/home/pcrec/projects/pcrec/worktrees/crit-vlb2/build/pcrec`. Read code THERE (not the live main tree).
- The design doc predates the build tree: stage 1 landed at merge `c44649a69` (2026-11-07, abi 96, decision D189)
  WITH post-review fixes, and other work landed after (e.g. alternation normal form abi 97, span-arms units).
  Any code the stage-2 text cites that moved between `63250b5cb` and `dc1988069` is a finding.
- Context you may rely on: the owner answered §13 Q1 (A) and Q2 (stage 1) on 2026-11-06 and gave stage 2 a
  build go on 2026-11-10 SUBJECT TO THIS ROUND. The round's question: does stage 2's design still hold against
  the tree stage 1 left, and is it ready to build?
- Ruling files: read them ONLY as `git -C /home/pcrec/projects/pcrec show dc1988069:docs/dev/decisions.md` /
  `...:docs/dev/plan.md` (frozen). Relevant: D189 (stage 1), D26 (+ its addendum), D181, D80, D76/D94 (abi),
  D191 (span arms: a lookbehind step back capped at the declared lookbehind length), the plan row
  `[VLOOKBEHIND]` (locate with `grep -n '^- \[VLOOKBEHIND\]'`, read that row's own indented lines only) and
  `[DD-14.LB]` (plan_completed.md).

## How to compile and run
- pcrec: `nice /home/pcrec/projects/pcrec/worktrees/crit-vlb2/build/pcrec --features all -p rx -o OUT.c --pattern 'PAT'`
  (`--features all` is REQUIRED, else lookaround/backrefs are "requires module"). `-e utf8` for UTF-8.
  `--emit-main` appends a main() taking the subject from argv[1]; `--emit-ir` prints the IR listing
  (the lookbehind label role "fixed width %d" vs "width %d..%d"). `build/pcrec --help` for the rest.
  Today every backreference inside a lookbehind is refused with the text "a lookbehind containing a
  backreference, a variable or a consuming callout is not implemented ...".
- Oracle (libpcre2 10.46 installed): run from your own dir,
  `python3 -I -c "import sys; sys.path.insert(0,'/home/pcrec/projects/pcrec/docs/design/eng_brep_measurements/probes'); import pcre2_ctypes as p; c=p.compile(r'(a|bc)(?<=\1)x'); print(c.search('bcx'))"`
  -> `((0, 3), ((0, 2),))`. `p.compile(pat, options=p.PCRE2_UTF, max_varlookbehind=N)`; errors raise
  `p.Pcre2Error` with `.code` (125 unbounded/not limited, 187 too long, 200 variable branch too long).
  Under PCRE2_UTF pass bytes (see the binding's header comment). `c.search(subject, start=K)`.
- Existing harness pieces to READ (not run as suites): `tests/lookaround/run_lookaround_diff.sh`,
  `tests/backrefs/bref_oracle.py`, `tests/lookaround/lookbehind_variable.rxt`.

## Guide files (the rules critics review against)
`docs/dev/guide/README.md`, `coding.md`, `architecture.md` (goals rule), `critics.md`, `docs/dev/learnings.md` §3,
`docs/design/CLAUDE.md` (standing questions), `docs/spec/pattern_language.md` §2.4/§7.3/§7.4/§9,
`docs/spec/match_api.md` §9.4, `docs/spec/limits.md` §3.11.

## DENYLIST (do not open, grep, diff or log these)
- `docs/dev/lanes/vlb*` (all lane reports AND evidence dirs, incl. `vlbinv_evidence/`, `vlbrev*_evidence/`;
  the design doc cites them — recompute what you need from the corpus and libpcre2 instead);
- `docs/dev/reviews/2026-11-05-r3-vlookbehind*`, `2026-11-05-r6-vlookbehind*`, `2026-11-06-r2-vlookbehind*`,
  `2026-11-06-r3-vlookbehind*`, `2026-11-06-r4-vlookbehind*` (files and dirs; the doc's "full 40-row table"
  lives in one: recompute against libpcre2);
- `git log` bodies beyond subject lines; branch logs of lane/vlbland, lane/vlbbuild; job logs; the box queue;
  other worktrees (only `worktrees/crit-vlb2/` is yours); `/var/tmp/pcrec-pcrec/scratch/crit-vlb2/.coord/`;
  other critics' dirs under `critics/`.
- For every PLAIN `grep -r` over the tree add:
  `--exclude-dir=lanes --exclude-dir=reviews --exclude-dir=worktrees --exclude-dir=.coord`
  (if you need other files under docs/dev/lanes or docs/dev/reviews, list them by name first and skip `vlb*`
  and the review names above). For `git grep`/`git diff` add pathspecs
  `':!docs/dev/lanes/vlb*' ':!docs/dev/reviews/*vlookbehind*'`.

## Output format (your findings file does NOT exist yet — you CREATE it)
Your FIRST action: create `critics/<LENS>/findings.md` with these headings:
`# <LENS> findings — vlb2`, `## Findings`, `## PROBED-AND-HELD`.
APPEND each finding the moment you have it, one append per finding. Each finding:
- id `<LENS>-n`; CONFIRMED (with a repro: input, command, observed vs expected) or SUSPECTED (what would confirm it);
- severity: answer / speed / size / maintenance / doc / design; effort; blast radius; file:line (build tree) or design §;
- a finding against a ruled D-row cites the row and argues, or drops.
PROBED-AND-HELD ends the file: what you checked that held, with case counts.
If your Write is refused, SendMessage your findings to the coordinator ("crit-vlb2") at once, marked relayed.
When done, run
`/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-vlb2/critics/<LENS> --deliver /var/tmp/pcrec-pcrec/scratch/crit-vlb2/critics/<LENS>/deliver.txt <LENS>`
and end only when it prints DONE. Final reply at most 150 words.
