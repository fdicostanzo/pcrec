# COMMON brief — critic round crit-vlb2 (DESIGN mode, RE-CHECK), 2026-11-05

Read this whole file before your per-lens prompt's question. `R` below means
`/var/tmp/pcrec-pcrec/scratch/crit-vlb2` (spell it out in commands).

## What this round is
A RE-CHECK of a revised design, and the LAST re-check before a build go of its stage 1. The previous
round (r3) reviewed rev 0 and was ruled; rev 1 claims to apply that ruling. You MAY read the previous
round: `docs/dev/reviews/2026-11-05-r3-vlookbehind.md` (including its RULING block) and its directory
`docs/dev/reviews/2026-11-05-r3-vlookbehind/` (critic texts, verify.md, COMMON, process.md). Do not
assume rev 1's claims about what it fixed are true: that is what you are checking.

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and, READ-ONLY, pcrec-bench
  (/home/pcrec/projects/pcrec-bench). You EDIT NEITHER repo. You write only under your own
  directory `R/<your-lens>/`. No other files anywhere (no $HOME, no /tmp, no system config).
- Read-only critic: never run `make`, any test suite, `scripts/boxqueue`, `scripts/boxlock`,
  `scripts/battery.sh`, or anything heavy. The box is shared tonight (a full mech job holds the
  box lock; another critic round runs concurrently): run every compile and probe under `nice -n 19`.
  Single-pattern `build/pcrec` compiles, `gcc` of one generated file, the oracle probe and small
  C/python programs of your own are fine (keep pcrec compiles under ~300 total). If a script you run
  writes temp files, set `PCREC_TMPDIR=R/<your-lens>` for it.
- Bound anything that may hang: `timeout 60 <cmd>` (GNU timeout on this box).
- Kill only your own processes, by PID (never `pkill -f`/`pgrep -f`).
- CLEAN-ROOM WALL (D181): nobody opens the pinned PCRE2 source copy, or any PCRE2 source anywhere.
  PCRE2 facts come from public docs (`man pcre2pattern`, `man pcre2api`, the pcre2.org HTML docs) and
  from the INSTALLED libpcre2-8 10.46 used as a library. A question only PCRE2's CODE can answer:
  write it under a heading "Questions for a pcre2-reader"; do not answer it.

## Subject (frozen)
- Design: `docs/design/vlookbehind.md` REV 1 (PROPOSED) at commit
  `bc9d1eb8f5ec013972d76ee8b0d26e84a045e393` (byte-identical on main `7ddfbfa95`). Frozen copy:
  `R/subject_vlookbehind.md` — READ THIS COPY; cite its § numbers and line numbers.
- A build would land on main HEAD `7ddfbfa95833b60f193c563cfdb820c5532b61af`. The review tree, built
  there: `/home/pcrec/projects/pcrec/worktrees/crit-vlb2` (`build/pcrec`, `build/libpcrec.a`). Read
  every piece of code the design cites IN THIS TREE (never the live main tree: main is moving
  tonight). No file under src/, lib/, cli/, tests/, docs/spec/ differs between the two commits.
  Cited code (file, function, field, operand, comment) that does not say what the design says is a
  finding.
- Rulings files: read `docs/dev/decisions.md` and `docs/dev/plan.md` ONLY as
  `git -C /home/pcrec/projects/pcrec show 7ddfbfa95:docs/dev/decisions.md` (same for plan.md, and for
  any other doc you want at the freeze). Find a plan row by `grep -n '^- \[TAG\]'` on that output and
  read that row and its own indented continuation lines only.

## Owner rulings in force at the freeze (Frank, 2026-11-05)
1. The 255 cap is accept-set POLICY (correctness needs none); default 255; exposure as a setting
   waits for [IFACE-PUSH].
2. PCRE2's absolute 65535-character branch ceiling is added.
3. Backreferences in a lookbehind are stage 2 (not stage 1); the range loop ships first.
4. The reverse-DFA row stays HELD; its home is the stream roadmap's A-REV area; lookbehind is its
   first client.
5. The r3 dispositions were all accepted as drafted (see the r3 review's RULING block).
OPEN, NOT RULED (do not treat either answer as decided): owner question 1 — keep today's fixed-width
bytes via the declared two-row selection (A), or the loop everywhere with an abi event (B). Review the
design under BOTH answers where it matters, and say where a finding depends on which.
OPEN too: owner question 2 (does the 65535 ceiling ride stage 1 or get its own row).
Standing project rules that bear here: general mechanisms, not special cases; no parallel mechanisms;
build only under a measured need (D77); in-flight refactors outrank optimizations (D153); selections
are declared first-match tables, never if-chains; compatible with PCRE2 unless it is a PCRE2 bug (D26
+ addendum); a public deny flag only for a choice that can be slower; a contract change carries its
spec hunk in the same change (D80); emitted-scaffolding changes are an abi event with every reader
found by grep (D76/D94).

## Guide and cited documents (read at the freeze commit)
- Guide: `docs/dev/guide/{architecture,coding,style,critics}.md`, `docs/dev/learnings.md` §3.
- Design docs cited: `docs/design/lookaround_design.md` (§2.5, §3.7), `docs/design/locate_finish.md`
  (D156), `docs/design/stream/{manifesto,roadmap}.md` (A-REV, A-VERDICT), `docs/design/CLAUDE.md`
  (standing questions). NOTE: `docs/design/stream/arev.md` does NOT exist at the freeze commit; do not
  read it from the live tree.
- Spec: `docs/spec/pattern_language.md` §2.4, §7.3, §7.4, §7.11, §9; `docs/spec/limits.md` §3;
  `docs/spec/match_api.md` §4, §6, §9.4.
- D-rows: D26, D42, D58, D76, D80, D94, D142, D153, D156, D181, D182, D186 (frozen decisions.md).
- Code the design cites (in the review tree): `src/parse/mod_lookaround.c` (`la_widths`,
  `la_lb_raise`, `pcrec_has_call`, `pcrec_lookaround_fix_widths`), `src/opt/mrl.c`
  (`pcrec_cwmin`/`pcrec_cwmax` and header), `src/gen/emit_vm.c` (`vm_look`, `vm_look_behind`,
  `vm_look_behind_branch`, `vm_count_slots_look`, `vm_rolef`, `vm_cut`), `src/gen/vm_stmt.h`
  (`VmKind`: `VK_SET`, `VK_PUSH`, `VK_WORK`, `VK_SEEK`/`VSK_BACKSTEP`/`VSK_RESTORE`, `slotx`,
  `VK_CONSUME_BACK`), the renderer (`vm_r_seek`), the encoding seam's `$_back_step` /
  `$_BACK_STEP_NONE` (src/enc/), `limits.def`, `pcrec_postresolve`, the AST `u.look.widths` field.
  Use grep to locate; the design's file names may be wrong (that is a finding).

## Evidence population (copies, read-only; count from these, not from the prose)
- `R/population/vlbrev1_evidence/` (rev 1's `probe.c`, `cells.out`, `premise.out`),
  `R/population/vlbdesign_evidence/` (rev 0's probes), `R/population/vlbinv_evidence/` (the
  investigation's raw probes, `population.tsv`, `corpus76_vs_pcre2.tsv`), and
  `R/population/vlbinv_report.md`.

## Tools
- Oracle (libpcre2-8 10.46 as a library): `R/tools/oracle_probe` (source:
  `R/population/vlbinv_evidence/oracle_probe.c`).
  Compile: `printf '%s\n' 'PATTERN' | R/tools/oracle_probe c [u]` -> `ACCEPT maxlookbehind=N caps=N`
  or `REJECT err-code ...`. Match: `printf '%s\t%s\n' 'PATTERN' 'SUBJECT' | R/tools/oracle_probe m [u]`
  -> every match (global iteration) as `[s-e,g1s-g1e,...]` or `nomatch`. `u` = PCRE2_UTF.
  Checked: `(?<=a|bc)x` on `bcx` -> `[2-3]`. For a start offset, a negative-arm-specific option, or
  `max_varlookbehind`, write your OWN small C probe in your dir (shape:
  `R/population/vlbrev1_evidence/probe.c`; link `-lpcre2-8`).
- pcrec (review tree), checked spellings:
  `nice -n 19 /home/pcrec/projects/pcrec/worktrees/crit-vlb2/build/pcrec --features all -p rx --emit-main -o R/<lens>/x.c --pattern '(?<=a|bc)x'`
  then `gcc -O1 -o R/<lens>/x R/<lens>/x.c` and `R/<lens>/x SUBJECT` (prints `match S E` or nomatch).
  UTF-8: add `-e utf8`. The VM program listing: `build/pcrec --features all --emit-ir --pattern P`.
  TODAY a varying lookbehind is REFUSED ("variable-length lookbehind is not implemented"), so pcrec
  runs only fixed-width lookbehinds; read today's emitted C for those to see the prologue the design
  claims to keep or extend.

## DENYLIST (PATHS EXCLUDED from every read, git diff, git log -p and grep)
- `docs/dev/lanes/vlbrev1_report.md`, `docs/dev/lanes/vlbrev1_rulings.md`,
  `docs/dev/lanes/vlbdesign_report.md`, `docs/dev/lanes/vlbdesign_rulings.md`, and any other
  `docs/dev/lanes/vlbrev1*` / `vlbdesign*` file except the `*_evidence/` copies above
- `docs/dev/wake.md`, `docs/dev/owner.md`, `docs/dev/dev_journal.md` (do not read it at all)
- `/var/tmp/pcrec-pcrec/scratch/crit-vlookbehind/` (the previous round's scratch dir; its committed
  texts in `docs/dev/reviews/2026-11-05-r3-vlookbehind/` ARE allowed)
- `git log` bodies beyond subject lines; job logs; the box queue; any worktree under `worktrees/`
  except `worktrees/crit-vlb2`
- `R/.coord/` and every other critic's directory under R
For git commands add pathspec exclusions, e.g.
`git -C /home/pcrec/projects/pcrec grep -n PATTERN 7ddfbfa95 -- . ':!docs/dev/lanes/vlbrev1_report.md' ':!docs/dev/lanes/vlbrev1_rulings.md' ':!docs/dev/lanes/vlbdesign_report.md' ':!docs/dev/lanes/vlbdesign_rulings.md' ':!docs/dev/wake.md' ':!docs/dev/owner.md' ':!docs/dev/dev_journal.md'`.
For PLAIN grep -r (e.g. in the review tree) add `--exclude=vlbrev1_report.md --exclude=vlbrev1_rulings.md --exclude=vlbdesign_report.md --exclude=vlbdesign_rulings.md --exclude=wake.md --exclude=owner.md --exclude=dev_journal.md --exclude-dir=.coord`.

## Output format
- Your findings file `R/<lens>/findings.md` DOES NOT EXIST YET: create it at once and write it
  INCREMENTALLY (one finding at a time, as you go).
- Sections (exact `##` headings): `## Findings`, `## PROBED-AND-HELD`, optionally
  `## Questions for a pcre2-reader`.
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command or hand-execution trace,
  observed vs expected) or SUSPECTED (what would confirm it); severity (answer / speed / size /
  maintenance / doc / design); effort; blast radius; the design § and line in the frozen copy (and
  file:line in the review tree where code is cited); and which owner-Q1 answer (A/B/both) it bears on.
  A finding against a ruled D-row or an owner ruling cites it and argues, or is dropped.
- PROBED-AND-HELD: what you checked that held, with case counts.
- Your DELIVER file `R/<lens>/DELIVER` exists (the coordinator wrote it). When done run
  `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-vlb2 --deliver /var/tmp/pcrec-pcrec/scratch/crit-vlb2/<lens>/DELIVER crit-<lens>`
  and fix what it reports until it prints `lanecheck: DONE rc=0`. Then END.
- Final reply at most 150 words.
