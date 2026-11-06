# COMMON brief — critic round crit-vlookbehind (DESIGN mode), 2026-11-05

Read this whole file before your per-lens prompt's question.

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and, READ-ONLY, pcrec-bench
  (/home/pcrec/projects/pcrec-bench). You EDIT NEITHER repo. You write only under your own
  directory `R/<your-lens>/` where `R=/var/tmp/pcrec-pcrec/scratch/crit-vlookbehind`.
  No other files anywhere (no $HOME, no /tmp, no system config).
- Read-only critic: never run `make`, any test suite, `scripts/boxqueue`, `scripts/boxlock`,
  or anything heavy. Single-pattern `build/pcrec` compiles, `gcc` of one generated file, and the
  oracle probe below are fine (keep total compiles under ~300). If a script you run writes
  temp files, set `PCREC_TMPDIR=R/<your-lens>` for it.
- Bound anything that may hang: `timeout 20 <cmd>` (GNU timeout on this box).
- Kill only your own processes, by PID (never `pkill -f`).
- CLEAN-ROOM WALL (D181, docs/dev/decisions.md): nobody opens the pinned PCRE2 source copy, or
  any PCRE2 source anywhere. PCRE2 facts come from the public docs (`man pcre2pattern`,
  `man pcre2api`, `man pcre2compat` if installed; the pcre2.org HTML docs) and from the INSTALLED
  libpcre2-8 10.46 used as a library (the oracle probe below). A question only PCRE2's CODE can
  answer: write it in your file under a heading "Questions for a pcre2-reader"; do not answer it.

## Subject
- Design document: `docs/design/vlookbehind.md` at commit
  `9f3aaaee1abff0cc761f170da2e08db7fc8ffcd3` (rev 0, PROPOSED). Frozen copy: `R/subject_vlookbehind.md`
  (read this copy; section numbers in findings refer to it).
- A build would land on main HEAD `9f077685a095be9923fe825e4bd09760effc989f`. The review tree,
  built there: `/home/pcrec/projects/pcrec/worktrees/crit-vlookbehind` (binary
  `build/pcrec`, library `build/libpcrec.a`). Read code cited by the design IN THIS TREE. The
  coordinator checked: no file under src/, lib/, cli/, docs/spec/ changed between the two commits.
  Any cited code (file, function, field, comment) that does not say what the design says it says
  is a finding.
- Rulings files: read `docs/dev/decisions.md` and `docs/dev/plan.md` ONLY as
  `git -C /home/pcrec/projects/pcrec show 9f077685a:docs/dev/decisions.md` (same for plan.md),
  never the live tree. Find a plan row by `grep -n '^- \[TAG\]'` on that output and read that row
  and its own indented continuation lines only.

## Owner rulings in force at the freeze (Frank, 2026-11-05)
1. The 255-character variable-lookbehind cap is pcrec's DEFAULT only; exposing it as a setting is
   deferred to [IFACE-PUSH].
2. Backreferences inside a lookbehind are a SECOND step (stage 2), not stage 1.
3. Candidate D (reverse DFA, then a forward VM run for captures) is the owner's idea, TO BE VETTED;
   NO reverse VM ("I'm certainly not going to try a reverse vm just for this").
Owner's standing project rules that bear here (memory; restated): general mechanisms, not special
cases; no parallel mechanisms; build only under a measured need (D77); in-flight refactors outrank
optimizations (D153); optimizations are UNIT or CHOICE changes with their own bar (D186);
compatible with PCRE2 unless it is a PCRE2 bug (D26 + addendum); simplification is a benefit; a
public deny flag only for a choice that can be slower.

## Guide and cited documents
- Guide: `docs/dev/guide/{architecture,coding,style,critics}.md`.
- Design docs cited: `docs/design/lookaround_design.md` (§2.5, §3.7), `docs/design/alt_dispatch_study.md`,
  `docs/design/stream/{manifesto,roadmap}.md` (roadmap §5 inventory, A-REV), `docs/design/CLAUDE.md`
  (standing questions).
- Spec: `docs/spec/pattern_language.md` §7.3, §7.4 and the refusal-shape table; `docs/spec/limits.md` §3;
  `docs/spec/match_api.md` §4, §6, §9.4.
- D-rows: D26, D42, D58, D77, D153, D181, D182, D184, D185, D186 (via the frozen decisions.md).
- Code the design cites: `src/parse/mod_lookaround.c` (`la_widths`, `la_lb_raise`), `src/gen/emit_vm.c`
  (`vm_look`, `vm_look_behind`, `vm_look_behind_branch`), `src/gen/vm_stmt.h` (`VmKind`), `src/ir/nfa.c`
  (`compile_ast`), `src/core/compile.c` (`revend_build_one`, `lmwalk_build`), `src/gen/emit_dfa.c`
  (`emit_reverse_block`, `emit_landmark_walk`), the limits table (`limits.def`), `pcrec_cwmin`/`pcrec_cwmax`.

## Evidence population (copy, read-only)
- `R/population/vlbinv_evidence/` (the investigation's raw probes: compile/match probes vs libpcre2,
  the corpus population `population.tsv`, `corpus76_vs_pcre2.tsv`, bench expansion) and
  `R/population/vlbdesign_evidence/` (the design lane's probes: `d_match`, `d_utf`, `w_match`,
  `startpos`, `revdfa_sizes.tsv`, `premise.txt`). Count from these, not from the prose.
- You MAY also read `docs/dev/lanes/vlbinv_report.md` (the investigation) including its
  "Owner addendum" section.

## Tools
- Oracle (libpcre2-8 10.46 as a library): `R/tools/oracle_probe`.
  Compile mode: `printf '%s\n' 'PATTERN' | R/tools/oracle_probe c [u]` -> ACCEPT maxlookbehind=N caps=N
  or REJECT err-code at offset: message. Match mode: `printf '%s\t%s\n' 'PATTERN' 'SUBJECT' |
  R/tools/oracle_probe m [u]` -> every match (global iteration) as [s-e,g1s-g1e,...] or nomatch.
  Second arg `u` = PCRE2_UTF. Subjects are literal bytes (no escapes; use printf with real bytes).
  Its source: `R/population/vlbinv_evidence/oracle_probe.c`; for a start offset other than 0, or a
  setting such as max_varlookbehind, write your OWN small C probe in `R/<your-lens>/` (see
  `R/population/vlbdesign_evidence/startpos.c` for the shape; link `-lpcre2-8`).
- pcrec (review tree): `build/pcrec --help`; e.g.
  `build/pcrec --features all -p rx --emit-main -o R/<lens>/x.c --pattern '(?<=a|bc)x'` then
  `gcc -O1 -o R/<lens>/x R/<lens>/x.c` and run `R/<lens>/x SUBJECT` (subject is argv[1]; check its output format once). TODAY a bounded variable lookbehind is REFUSED at compile time (that is what the design changes), so pcrec can only be run on fixed-width lookbehinds. Write outputs under your dir.

## DENYLIST (PATHS EXCLUDED from every read, git diff, git log -p and grep)
- `docs/dev/lanes/vlbdesign_report.md`, `docs/dev/lanes/vlbdesign_rulings.md`, any other
  `docs/dev/lanes/vlbdesign*` file except the `vlbdesign_evidence/` copy above
- `docs/dev/wake.md`, `docs/dev/owner.md`, `docs/dev/dev_journal.md` (do not read it at all)
- `docs/dev/reviews/` files about lookbehind / vlookbehind (none should exist; if you find one, stop reading it)
- `git log` bodies beyond subject lines; job logs; the box queue; any other worktree under
  `worktrees/` except `worktrees/crit-vlookbehind`
- `R/.coord/` and every other critic's directory under R
For git commands add pathspec exclusions, e.g.
`git -C /home/pcrec/projects/pcrec grep -n PATTERN 9f077685a -- . ':!docs/dev/lanes/vlbdesign_report.md' ':!docs/dev/lanes/vlbdesign_rulings.md' ':!docs/dev/wake.md' ':!docs/dev/owner.md' ':!docs/dev/dev_journal.md'`.
For PLAIN grep -r add `--exclude=vlbdesign_report.md --exclude=vlbdesign_rulings.md --exclude=wake.md --exclude=owner.md --exclude=dev_journal.md --exclude-dir=.coord --exclude-dir=worktrees`.

## Output format
- Your findings file `R/<lens>/findings.md` DOES NOT EXIST YET: create it at once and write it
  INCREMENTALLY (one finding at a time, as you go).
- Sections (exact `##` headings): `## Findings`, `## PROBED-AND-HELD`, and optionally
  `## Questions for a pcre2-reader`, `## Answers to the owner's questions`.
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command, observed vs expected) or
  SUSPECTED (what would confirm it); severity (answer / speed / size / maintenance / doc / design);
  effort; blast radius; the design § (and file:line in the review tree where code is cited).
  A finding against a ruled D-row or an owner ruling cites it and argues, or is dropped.
- PROBED-AND-HELD: what you checked that held, with case counts.
- Your DELIVER file `R/<lens>/DELIVER` exists (the coordinator wrote it). When done run
  `/home/pcrec/projects/pcrec/scripts/lanecheck --dir R --deliver R/<lens>/DELIVER crit-<lens>`
  (spell R out in full) and fix what it reports until it prints `lanecheck: DONE rc=0`. Then END.
- Final reply at most 150 words.
