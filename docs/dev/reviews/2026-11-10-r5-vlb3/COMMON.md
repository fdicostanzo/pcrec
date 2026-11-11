# COMMON brief — critic round vlb3 (design RE-CHECK): variable lookbehind STAGE 2, rev 5

Read this whole file before anything else. Your per-lens prompt names your ONE question.

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and pcrec-bench (/home/pcrec/projects/pcrec-bench; you should not need it).
- You are READ-ONLY on both repos. Write files ONLY under your own dir
  `/var/tmp/pcrec-pcrec/scratch/crit-vlb3/critics/<LENS>/` (never /tmp, never the repo).
  Export `PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-vlb3/critics/<LENS>` before compiling.
- NEVER run `make`, `make test`, any suite, sweep or battery, and never `scripts/boxlock`/`boxqueue`.
  A FULL SUITE is running on this box until ~06:30: run SINGLE compiles only (`build/pcrec` on one pattern,
  `gcc -c`/`-S` on one generated file, one artifact run), prefixed with `nice`, sequentially, at most ~300
  pcrec compiles total. libpcre2 cells through the ctypes binding are cheap and unlimited within reason.
- Never kill a process. Never read PCRE2 source code (D181: only a pcre2-reader agent may); running the
  INSTALLED libpcre2 runtime through the ctypes binding below is fine and is the oracle.
- `cd` only inside a `( ... )` subshell; prefer absolute paths.

## The subject (frozen)
- Design: `docs/design/vlookbehind.md` **rev 5** and `docs/design/vlb_d27_extract.md`, on branch `lane/vlbrev5`
  at commit `5a2595601bcada9c54fb15c9a0a43a50c3e3a673` (copies, identical to that commit:
  `/var/tmp/pcrec-pcrec/scratch/crit-vlb3/vlookbehind_rev5.md`, `.../vlb_d27_extract.md`; or
  `git -C /home/pcrec/projects/pcrec show 5a2595601:docs/design/vlookbehind.md`).
  The branch also re-cuts `docs/design/la_d27_extract.md` and `docs/design/lookaround_design.md`'s backreference
  lines: `git -C /home/pcrec/projects/pcrec diff main...5a2595601 -- docs/design/la_d27_extract.md docs/design/lookaround_design.md docs/design/CLAUDE.md`.
- SCOPE: **stage 2 only**: the "REVISION 5" block (lines 23-90 of the copy), §6.2 and its subsections
  6.2.1-6.2.9 (lines ~1925-2432), and every section rev 5 changed for stage 2 (marked `[vlb2 ...]`: §0 G1 notes,
  §5.2's shipped-refusal note, §8 recount, §9 D27 charter, §10 banner, §11 stage 2, §13 Q3, §15 evidence, §16e).
  `grep -n 'vlb2' ` on the copy lists every marked site. Stage 1 is BUILT; stage 3 is HELD and out of scope.
- What rev 5 answers: the RULED review `docs/dev/reviews/2026-11-10-r3-vlb2.md` (and its dir
  `docs/dev/reviews/2026-11-10-r3-vlb2/`). You MAY read both: its findings F1-F16 and the RULINGS block at its end
  are the input the revision answers.
- BUILD TREE (where the stage-2 build lands) = main HEAD `1856e973f919bd7233aacd7663775486d30d34bc`, checked out
  read-only at `/home/pcrec/projects/pcrec/worktrees/crit-vlb3/` and ALREADY BUILT:
  `/home/pcrec/projects/pcrec/worktrees/crit-vlb3/build/pcrec`. Read code THERE (not the live main tree).
  The doc's reader lists were grepped at main `eb83f0902` (the branch's base); main moved one commit since
  (`1856e973f`, a review filing). Any cited code that differs between them is a finding.
- The round's question: did rev 5 fix what the rulings asked without breaking anything new, and is stage 2
  READY, per build unit (§6.2.9's V1-V7), to brief a build lane?
- Ruling files: read them ONLY as `git -C /home/pcrec/projects/pcrec show 1856e973f:docs/dev/decisions.md` /
  `...:docs/dev/plan.md` (frozen). Relevant: D189 (stage 1), D26 (+ addendum), D181, D80, D76/D94 (abi), D191,
  the plan row `[VLOOKBEHIND]` (locate with `grep -n '^- \[VLOOKBEHIND\]'`, read that row's own indented lines only).
  Note: the stage-2 build go (owner, 2026-11-10) and the F2 note correction are NOT yet recorded in the plan row;
  the review's RULINGS block is their record. Do not file that as a finding.

## How to compile and run
- pcrec: `nice /home/pcrec/projects/pcrec/worktrees/crit-vlb3/build/pcrec --features all -p rx -o OUT.c --pattern 'PAT'`
  (`--features all` is REQUIRED). `-e utf8` for UTF-8. `--emit-main` adds a main() taking the subject as argv[1];
  `--emit-ir` prints the IR listing; `--emit-facts` prints facts (e.g. `RX_END_WINDOW`). `build/pcrec --help` for the rest.
  Today every backreference inside a lookbehind is refused with "a lookbehind containing a backreference, a
  variable or a consuming callout is not implemented ..." (stage 1's rule 0).
- Oracle (libpcre2 10.46 installed), run from your own dir:
  ```
  python3 -I -c "
  import sys,ctypes; sys.path.insert(0,'/home/pcrec/projects/pcrec/docs/design/eng_brep_measurements/probes'); import pcre2_ctypes as p
  c=p.compile(r'(a|bc)(?<=\1)x'); v=ctypes.c_uint32(0); p._lib.pcre2_pattern_info_8(c._code,15,ctypes.byref(v)); print('lb',v.value, c.search('bcx'))"
  ```
  -> `lb 2 ((0, 3), ((0, 2),))` (info code 15 = PCRE2_INFO_MAXLOOKBEHIND). `p.compile(pat, options=p.PCRE2_UTF,
  max_varlookbehind=N)`; errors raise `p.Pcre2Error` with `.code` (115 nonexistent group, 125 not
  bounded/not fixed, 187 too long, 200 variable branch too long) and the offset in its message.
  Under PCRE2_UTF pass bytes. `c.search(subject, start=K)`.

## Guide files (the rules critics review against)
`docs/dev/guide/README.md`, `coding.md`, `architecture.md` (goals rule), `critics.md`, `docs/dev/learnings.md` §3,
`docs/design/CLAUDE.md` (standing questions), `docs/spec/pattern_language.md` §2.4/§7.3/§7.4/§9,
`docs/spec/match_api.md` §9.4, `docs/spec/vars.md` §6, `docs/spec/limits.md`.

## DENYLIST (do not open, grep, diff or log these)
- `docs/dev/lanes/vlb*` (all lane reports AND evidence dirs, incl. `vlbrev5_report.md` and `vlbrev5_evidence/`;
  the design cites `cells*.out`/`pcrec_head.out` there: recompute against libpcre2 and the built pcrec instead);
- older review files on this subject: `docs/dev/reviews/2026-11-05-r3-vlookbehind*`, `2026-11-05-r6-vlookbehind*`,
  `2026-11-06-r2-vlookbehind*`, `2026-11-06-r3-vlookbehind*`, `2026-11-06-r4-vlookbehind*` (files and dirs).
  (`2026-11-10-r3-vlb2*` is ALLOWED.)
- `git log` bodies beyond subject lines (lane/vlbrev5's included); job logs; the box queue; other worktrees
  (only `worktrees/crit-vlb3/` is yours); `/var/tmp/pcrec-pcrec/scratch/crit-vlb3/.coord/`; other critics' dirs
  under `critics/`; `/var/tmp/pcrec-pcrec/scratch/crit-vlb2/`.
- For every PLAIN `grep -r` over a tree add:
  `--exclude-dir=lanes --exclude-dir=worktrees --exclude-dir=.coord` (and when grepping docs/dev/reviews, skip the
  older review names above by `--exclude='*vlookbehind*' --exclude-dir='*vlookbehind*'`).
  For `git grep`/`git diff` add pathspecs `':!docs/dev/lanes/vlb*' ':!docs/dev/reviews/*vlookbehind*'`.

## Output format (your findings file does NOT exist yet — you CREATE it)
Your FIRST action: create `critics/<LENS>/findings.md` with these headings:
`# <LENS> findings — vlb3`, `## Findings`, `## PROBED-AND-HELD`.
APPEND each finding the moment you have it, one append per finding (never hold them for the end). Each finding:
- id `<LENS>-n`; CONFIRMED (with a repro: input, command, observed vs expected) or SUSPECTED (what would confirm it);
- severity: answer / speed / size / maintenance / doc / design; effort; blast radius; file:line (build tree) or design §;
- a finding against a ruled item (the review's RULINGS block, a D-row) cites it and argues, or drops.
PROBED-AND-HELD ends the file: what you checked that held, with case counts.
If your Write is refused, SendMessage your findings to the coordinator at once, marked relayed.
When done, run
`/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-vlb3/critics/<LENS> --deliver /var/tmp/pcrec-pcrec/scratch/crit-vlb3/critics/<LENS>/deliver.txt <LENS>`
and end only when it prints DONE. Final reply at most 150 words.
