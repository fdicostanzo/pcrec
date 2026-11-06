# COMMON brief — critic round crit-arev (DESIGN mode), 2026-11-05

Read this whole file before your per-lens prompt's question. `R=/var/tmp/pcrec-pcrec/scratch/crit-arev`
(spell it out in full in every command; your shell does not keep variables between calls).

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and, READ-ONLY, pcrec-bench
  (/home/pcrec/projects/pcrec-bench). You EDIT NEITHER repo. You write only under your own
  directory `R/<your-lens>/`. No other files anywhere (no $HOME, no /tmp, no system config).
- Read-only critic: never run `make`, any test suite, `scripts/boxqueue`, `scripts/boxlock`, or
  anything heavy. The box is busy (a full suite holds the lock; two other critic rounds run).
  Single-pattern `build/pcrec` compiles, `gcc` of one generated file, and the oracle probe are fine
  (keep total compiles under ~200; prefix with `nice`). If a script you run writes temp files, set
  `PCREC_TMPDIR=R/<your-lens>` for it.
- Bound anything that may hang: `timeout 20 <cmd>` (GNU timeout on this box).
- Kill only your own processes, by PID (never `pkill -f`).
- Do not `cd` into a `worktrees/` path in a chained command (a hook blocks it): use absolute paths,
  `git -C DIR`, or a `( cd X && ... )` subshell.
- CLEAN-ROOM WALL (D181): nobody opens the pinned PCRE2 source copy, or any PCRE2 source anywhere.
  PCRE2 facts come from public docs (`man pcre2pattern`, `man pcre2api`; pcre2.org HTML docs) and
  from the INSTALLED libpcre2-8 10.46 used as a library (the oracle probe below). A question only
  PCRE2's CODE can answer: write it under a heading "Questions for a pcre2-reader"; do not answer it.

## Subject
- Design: `docs/design/stream/arev.md` (PROPOSED rev 0) AND the A-REV area of
  `docs/design/stream/roadmap.md` (its §1 table row A-REV, its `### A-REV` section, the ratchet rows
  R03/R10 and the proposed R28 in §5), both at commit `dd89fa9bb0ed1c63e7fed35a972927887f97add4`.
  Frozen copies: `R/subject_arev.md`, `R/subject_roadmap.md` (read THESE; findings cite their §).
- A build would land on main HEAD `f15f30f25482fd07625d27b401a6c4352d88ea7e`. The review tree, built
  there: `/home/pcrec/projects/pcrec/worktrees/crit-arev` (binary `build/pcrec`, `build/libpcrec.a`).
  Read cited code IN THIS TREE. Coordinator checked: no file under src/, lib/, cli/, memfn/,
  docs/spec/ changed between arev.md's anchor (main 7cebea04e) and the build commit. Any cited code
  (file, function, field, comment, line) that does not say what the design says it says is a finding.
- NOTE for every lens: arev.md was written on a branch that did NOT contain
  `docs/design/vlookbehind.md` rev 1 (rev 1 merged to main BEFORE arev, at 7ddfbfa95). The client
  document in force at the build commit is vlookbehind.md REV 1 (read it at f15f30f25). Where arev.md
  describes the lookbehind client, its rows, stages or exits differently from rev 1, that is in scope.
- Rulings files: read `docs/dev/decisions.md` and `docs/dev/plan.md` ONLY as
  `git -C /home/pcrec/projects/pcrec show f15f30f25:docs/dev/decisions.md` (same for plan.md), never
  the live tree. Find a plan row by `grep -n '^- \[TAG\]'` on that output and read that row and its
  own indented continuation lines only (rows of interest: [STREAM], [VLOOKBEHIND], [LB-EXIST],
  [GIVEUP-DIFF], [REVBLOCK-VIEW], [VMREC], [LANDWALK-*]).

## Owner criteria and direction in force at the freeze
- `docs/design/stream/manifesto.md` (stable end state): goals F1 > F2 > F3; F4 is a CONSTRAINT, not
  a goal; D185. Principle 9: every seam designed as if serialized to text and reread by another process.
- Owner direction (Frank, 2026-11-05): the stream's payoff is CROSS-ENGINE PIECES used where needed
  (e.g. a reverse DFA inside a VM lookbehind, then a forward VM run for captures). A-REV is reshaped
  into one reverse automaton kind with declared exits, hostable in a VM body; lookbehind is its first
  client; the hand-written reverse walks migrate onto it.
- OPEN and NOT ruled: the "VM base" frame in roadmap.md A-VERDICT. Treat it as a lens, never as a
  rule; a design that leans on it as if ruled is a finding.
- Standing owner rules (memory, restated): general mechanisms, not special cases; no parallel
  mechanisms; build only under a measured need (D77); in-flight refactors outrank optimizations (D153);
  optimizations are UNIT or CHOICE changes (D186); selections are declared row tables, never
  if-chains; seams carry facts both ways; simplification counts as a benefit; caller-facing names say
  what the caller sees (D174); compatible with PCRE2 unless it is a PCRE2 bug (D26 + addendum).

## Guide and cited documents (all at f15f30f25)
- Guide: `docs/dev/guide/{architecture,coding,style,critics}.md`.
- `docs/design/stream/{manifesto,roadmap}.md` (roadmap §0a pipeline, §2 hubs esp. H-FLAGS, H-LADDER,
  H-SITES, H-ABI, H-HEADER; §4 admission table; §5 ratchet; §6 proof order; A-VERDICT).
- `docs/design/vlookbehind.md` rev 1 (its candidate-source rows incl. `reverse-dfa`, §5.4; staging §6).
- `docs/dev/reviews/2026-11-05-r3-vlookbehind.md` (and its dir) — the review of vlookbehind rev 0.
- `docs/design/locate_finish.md` (D156: LOCATE/FINISH rows).
- `docs/design/CLAUDE.md` (the standing questions).
- D-rows cited by arev: D27 D76 D77 D80 D94 D142 D151 D156 D157 D161 D164 D182 D184 D186 (+ D185, D153, D181).
- Code cited: `src/gen/emit_dfa.c` (`emit_reverse_block`, `emit_scan_loop`, `emit_landmark_walk`,
  `dfa_dir_reverse`, `dfa_dir_landmark`, `dfa_dir_lmverify`), `src/gen/lmwalk.c`, `src/core/compile.c`
  (`revend_build_one`, `lmwalk_build`), `src/core/internal.h` (`Job`, `CAND_ML`, `Nfa.erased`,
  `NFA_ERASED_*`, `DfaDir`, `DfaForm`), `src/ir/nfa.c`, `src/opt/revdet.c` (`Rev`, `vm_revdet_rep`,
  `vm_rev_emit`), `src/gen/emit_vm.c`, `src/gen/vm_stmt.{c,h}` (`VmKind`, `vm_r_consume_back`, `vm_charge`).

## Tools
- Oracle (libpcre2-8 10.46 as a library): `R/tools/oracle_probe` (source `R/tools/oracle_probe.c`).
  Compile: `printf '%s\n' 'PATTERN' | R/tools/oracle_probe c [u]` -> `ACCEPT maxlookbehind=N caps=N` or
  `REJECT ...`. Match: `printf '%s\t%s\n' 'PATTERN' 'SUBJECT' | R/tools/oracle_probe m [u]` -> every
  match (global iteration) as `[s-e,g1s-g1e,...]` or `nomatch`. Checked: `(?<=(?>a|ab)b)x` on `abbx`
  -> nomatch. For other settings write your own small C probe in `R/<your-lens>/` (link `-lpcre2-8`).
- pcrec (review tree): `build/pcrec --help`; e.g. `build/pcrec --features all -p rx --emit-main -o
  R/<lens>/x.c --pattern 'a(b|c)+d'` then `gcc -O1 -o R/<lens>/x R/<lens>/x.c` and run `R/<lens>/x
  SUBJECT` (prints e.g. `Match 2 3`; without `--features all` lookaround is refused as "requires
  module 'lookaround'" — coordinator checked). Lookbehinds whose alternatives are each fixed-length
  (`(?<=a|bc)x`) compile TODAY; one with a variable-width alternative (`(?<=a+)x`, `(?<=a{1,3})x`) is
  REFUSED at compile time, so
  the lookbehind client can only be studied on the reverse machinery that exists (RECOVER's reverse
  pass, `rev-end`, the landmark walk, revdet) and by hand. To see a pattern's reverse walks, grep the
  emitted C for the renderer's comments/labels.

## DENYLIST (PATHS EXCLUDED from every read, git diff, git log -p and grep)
- `docs/dev/lanes/arevdesign_report.md`, `docs/dev/lanes/arevdesign_rulings.md` (and any other
  `docs/dev/lanes/arevdesign*`)
- `docs/dev/wake.md`, `docs/dev/owner.md`, `docs/dev/dev_journal.md` (do not read it at all)
- any `docs/dev/reviews/` file about arev / A-REV (none should exist; if you find one, stop reading)
- `git log` bodies beyond subject lines; job logs; the box queue; any worktree under `worktrees/`
  except `worktrees/crit-arev`
- `R/.coord/` and every other critic's directory under R
For git commands add pathspec exclusions, e.g.
`git -C /home/pcrec/projects/pcrec grep -n PATTERN f15f30f25 -- . ':!docs/dev/lanes/arevdesign_report.md' ':!docs/dev/lanes/arevdesign_rulings.md' ':!docs/dev/wake.md' ':!docs/dev/owner.md' ':!docs/dev/dev_journal.md'`.
For PLAIN grep -r add `--exclude=arevdesign_report.md --exclude=arevdesign_rulings.md --exclude=wake.md --exclude=owner.md --exclude=dev_journal.md --exclude-dir=.coord --exclude-dir=worktrees`
(when grepping inside the review tree itself, grep `worktrees/crit-arev/src` etc. directly).

## Output format
- Your findings file `R/<lens>/findings.md` DOES NOT EXIST YET: create it at once and write it
  INCREMENTALLY (one finding at a time, as you go).
- Sections (exact `##` headings): `## Findings`, `## PROBED-AND-HELD`, and optionally
  `## Questions for a pcre2-reader`, `## Standing questions` (the lens that is assigned them).
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command or file:line quote, observed
  vs expected) or SUSPECTED (what would confirm it); severity (answer / speed / size / maintenance /
  doc / design); effort; blast radius; the design § (and file:line in the review tree for code).
  A finding against a ruled D-row or an owner ruling cites it and argues, or is dropped.
- PROBED-AND-HELD: what you checked that held, with case counts.
- Your DELIVER file `R/<lens>/DELIVER` exists (the coordinator wrote it). When done run
  `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-arev --deliver /var/tmp/pcrec-pcrec/scratch/crit-arev/<lens>/DELIVER crit-<lens>`
  and fix what it reports until it prints `lanecheck: DONE rc=0`. Then END.
- Final reply at most 150 words.
