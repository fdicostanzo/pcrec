# COMMON brief: critic round memfn-sp1b (code mode)

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and, read-only, pcrec-bench (/home/pcrec/projects/pcrec-bench). No other directories, no home or system config.
- You are READ-ONLY on both repos: no edits, no commits, no `git checkout`/`switch`/`stash`/`worktree` in either. The review tree and the base tree below are read-only too (never build or write inside them).
- Scratch ONLY under your own dir /var/tmp/pcrec-pcrec/scratch/crit-memfn-sp1b/<your-lens>/ (exists). /tmp is NOT used. `export PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-memfn-sp1b/<your-lens> TMPDIR=$PCREC_TMPDIR` before running anything.
- Never `cd` chained with other commands (a hook blocks it): absolute paths, `git -C`, or a `( cd X && ... )` subshell.
- NEVER run `make`, `make test`, any suite, mech, `scripts/emit_sweep.py`, or anything that takes the box lock or box queue. Do not queue jobs. The box is running queued jobs: probes are SINGLE compiles (`pcrec ... --pattern P`, `gcc -S`/`-c` of one emitted file), single small `gcc` builds of an in-tree C checker into YOUR dir, and single runs of small in-tree checkers. Your HARD COMPILE CAP is in your prompt (a compile = one pcrec invocation). `nice` every loop; wrap anything uncertain in `timeout 60`. No timing claims (instruction counts via `perf stat -e instructions:u` are fine).
- Kill only with /home/pcrec/projects/pcrec/scripts/safekill PID (never pkill/pgrep -f).

## Subject (frozen)
- SUBJECT = cca35ffd1f7756cc3a0c719bacea34631c087933 (branch lane/memfn-sp1b)
- BASE    = b0f3d033902198f5228022d61bf2b9ab54b6c48b (merge-base with main = main HEAD at the freeze).
- Review tree at SUBJECT, BUILT: /home/pcrec/projects/pcrec/worktrees/crit-memfn-sp1b (build/pcrec, build/pcrec-harness, build/libpcrec.a).
- BASE source tree, BUILT (a plain export, no .git): /var/tmp/pcrec-pcrec/scratch/crit-memfn-sp1b/base/ (build/...). Or `git -C /home/pcrec/projects/pcrec show BASE:path`.
- Prebuilt binaries (run them; never write into bin/): /var/tmp/pcrec-pcrec/scratch/crit-memfn-sp1b/bin/
  - base/pcrec, subj/pcrec (+ pcrec-harness): the plain compilers.
  - base-mftrace/pcrec, subj-mftrace/pcrec: the same with the kit compiled -DMF_TRACE (tests/memfn/mk_mftrace_lib.sh's recipe); they print `MFTRACE ...` lines on stderr, including the exit `MFTRACE REACH table=.. row=.. chosen=.. asked=..` lines (memfn/docs/trace_format.md). Libraries beside them (libpcrec_mftrace.a) if you need to link a checker.
- NOTE: the emitted C names its own output file (`#include "<name>.h"`). To compare BASE vs SUBJECT, write both outputs under the SAME basename in two directories (e.g. `$D/base/o.c`, `$D/subj/o.c`), then `cmp`.
- Diff: `git -C /home/pcrec/projects/pcrec diff BASE SUBJECT -- . ':!docs/dev/lanes' ':!docs/dev/history' ':!memfn/docs/journal.md' ':!memfn/docs/responses.md' ':!docs/dev/reviews'`. Use THESE EXCLUSIONS on EVERY git diff / git grep / grep you run over either tree. `git log` SUBJECT LINES only (`--format=%s`), never bodies.
- Files the subject changes (code): memfn/src/presence.c, memfn/src/window.c, memfn/src/kit.h; tests/memfn/mass_check.c (new), tests/memfn/run_finder.sh, tests/memfn/decider_census.py, tests/memfn/decider_census.tsv; tests/mech/sabotages/S1097_leads-not-strict.sh, S458_set_leads_tie_leads.sh; docs: memfn/src/CLAUDE.md, tests/memfn/CLAUDE.md.
- What it claims to be: span_pick stage 1, UNIT 1b, "primitives". (U4) the kit's mass variants (`cube_mass`, `kit_set_mass`, `kit_set_sum`, `window_mass`, `uniform_mass` in presence.c) become ONE primitive `kit_mass(rate, kit_pos *pos, n, cap)` over a POSITION MULTISET (each position a byte set or a cube t/mask; a byte repeated across positions counted at each), with a capped/uncapped argument and the NONE-mode (no rates) total taken once over the member count; the DECLARED NONE ROW (no rates handed: a set's mass is its member count's uniform ppm). (U5) presence.c's private tie spelling `tie_over` goes; presence's set pick and its run window read the window family's TIE table `wf_ties[]` through `kit_tie_takes` (new row T_PRES_MEMBER; T_WINDOW gains a reader). Golden-value test `tests/memfn/mass_check.c` (part `mass` of test-memfn-finder, floor 20); decider census map and MEMBER_COUNT updated; two sabotage rows re-anchored.
- THE PROMISE (stage 1's bar, D186): NO emitted byte moves on any arm (default, every `--memfn=no-X` deny, `--engine=vm`, both SIMD layers, every encoding, with and without `--analysis` byte rates, stamps included); no pcrec abi change; MFTRACE REACH equality (chosen/asked per row equal at BASE and SUBJECT); the census green.
- Design of record (rev 5.2; unchanged by the subject): `git -C /home/pcrec/projects/pcrec show b0f3d033902198f5228022d61bf2b9ab54b6c48b:docs/design/memfn/span_pick.md`: Goals (~line 11), §The pick (~161, the NONE row ~170), §The tables (~103), §Staging (~339-406: landing order ~350, the 1b row ~361, its witness row ~374, per-unit witness and RATCHET ~388-397), §What stage 1 deletes (~407-420: U2/U5 and U4 rows), dispositions R2, C7 (~491-520). The ratchet's counting recipes: docs/design/stream/roadmap.md §5 rows R22 (mass variants) and R23 (tie-rule tables) (~line 641-642). Also docs/design/memfn/window_site.md §2.1 (the TIE table) and §9, units_inventory.md U4/U5.

## Rulings and the guide
- Read rulings ONLY at the freeze: `git -C /home/pcrec/projects/pcrec show 7ac40695ef11f07d4e8afe410f43964f8908d531:docs/dev/decisions.md` (and `...:docs/dev/plan.md`), never the live files. Relevant: D186 and its addenda 1-2 (`grep -n '^## D186'`, read through its addenda; add. 2 has the NONE / member-count ruling), D157 (pcrec->kit carries facts only; pcrec's findings.c copy of the mass stays), D153 (remodel first), D76/D94 (abi), D174 (names describe behaviour). To read a plan.md row, locate it by `grep -n '^- \[TAG\]'` and read only that row.
- Guide: docs/dev/guide/README.md, coding.md, architecture.md ("One table per slot"), style.md, critics.md; docs/dev/learnings.md §3 (check design); memfn/CLAUDE.md, memfn/src/CLAUDE.md, tests/memfn/CLAUDE.md, tests/mech/CLAUDE.md.

## Denylist (do NOT read, list, grep or open; exclude from every diff and grep)
- docs/dev/lanes/sp1b* (the lane's report and deliver file) and every other docs/dev/lanes/*_report.md / *_deliver.txt; docs/dev/history/ (lane index history).
- docs/dev/reviews/ files about sp1b / span_pick / memfn-sp1* / memfn-spanpick* (earlier rounds).
- memfn/docs/journal.md and memfn/docs/responses.md (entries about 1b; skip both files).
- /var/tmp/pcrec-pcrec/scratch/memfn/ (the lane's scratch and job scripts, incl. memfn/sp1b/), worktrees/.boxqueue/, the box queue itself, every other worktree under worktrees/ except crit-memfn-sp1b, job logs anywhere, other crit-* scratch dirs.
- /var/tmp/pcrec-pcrec/scratch/crit-memfn-sp1b/.coord/ and the OTHER critics' dirs in this round.
- `git log` bodies (subject lines only).

## Output format
- Your findings file DOES NOT EXIST YET: you CREATE /var/tmp/pcrec-pcrec/scratch/crit-memfn-sp1b/<your-lens>/findings.md and write it INCREMENTALLY (append each finding as you confirm it; do not hold it all to the end).
- Headings required: `## Findings` and `## PROBED-AND-HELD`.
- Each finding: id `<LENS>-n` (lens upper-case); CONFIRMED (with repro: input, exact command, observed vs expected) or SUSPECTED (what would confirm it); severity (answer / speed / size / maintenance / doc / design / contract); effort; blast radius; file:line or §.
- A finding against a ruled D-row or a design row cites the row and argues, or drops.
- PROBED-AND-HELD: what you probed that held, with case counts and the compile count you spent.
- When done, run `/home/pcrec/projects/pcrec/scripts/lanecheck --deliver /var/tmp/pcrec-pcrec/scratch/crit-memfn-sp1b/<lens>/DELIVER.txt --dir /var/tmp/pcrec-pcrec/scratch/crit-memfn-sp1b <lens>` (the --dir is REQUIRED) and end only after it prints DONE (fix and rerun otherwise). Final reply at most 150 words.
