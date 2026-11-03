# COMMON brief: critic round memfn-sp1a (code mode)

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and, read-only, pcrec-bench (/home/pcrec/projects/pcrec-bench).
- You are READ-ONLY on both repos: no edits, no commits, no `git checkout`/`switch`/`stash`/`worktree` in either.
- Scratch ONLY under your own dir /var/tmp/pcrec-pcrec/scratch/crit-memfn-sp1a/<your-lens>/ (create it). /tmp is NOT used. Export PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-memfn-sp1a/<your-lens> before running any repo script.
- Never `cd` (a hook blocks it): absolute paths, `git -C`, `make -C` is forbidden anyway.
- NEVER run `make`, `make test`, any suite, emit_sweep.py over the corpus, or anything that takes the box lock / box queue. Do not queue jobs. Probes are SINGLE compiles: `build/pcrec ... --pattern P` and `gcc -S`/`gcc -c` of one emitted file, plus single runs of small in-tree python checkers on a handful of inputs. Wrap anything uncertain in `timeout 60`.
- Kill only with /home/pcrec/projects/pcrec/scripts/safekill PID (never pkill/pgrep -f).

## Subject (frozen)
- SUBJECT = c0c73bc2058be4b601f18cceddf68983bbe0f6e8 (branch lane/memfn-sp1a)
- BASE    = 564db08c5c68358b635fa6b6d6196febde41698d (merge-base with main; main HEAD at the freeze)
- Review tree at SUBJECT, BUILT: /home/pcrec/projects/pcrec/worktrees/crit-memfn-sp1a  (binary build/pcrec)
- Base tree at BASE, BUILT (git archive, no .git): /var/tmp/pcrec-pcrec/scratch/crit-memfn-sp1a/base (binary build/pcrec)
- Diff: `git -C /home/pcrec/projects/pcrec diff BASE SUBJECT` (read code diffs freely; `git log` SUBJECT LINES only, `--format=%s`, never bodies).
- What it claims to be: span_pick stage 1, UNIT 1a, per docs/design/memfn/span_pick.md rev 5.2 (read it at BASE: `git -C /home/pcrec/projects/pcrec show BASE:docs/design/memfn/span_pick.md`). Unit 1a = dead code removal (`mf_set_terms` / memfn/src/terms.c; finder rows R3a, R3b, R4), an MF_CLASS_V event (pres_row shift), the decider census map + its check (tests/memfn/decider_census.py/.tsv), tests/memfn/reach_equal.py (the reach-equality witness), and the frozen bench pattern list (docs/dev/lanes/spanpick_bench_patterns.txt). Relevant span_pick.md sections: Goals table (line ~18), "The tables" incl. "The decider census" (~line 140), Staging tables (~lines 344-392: the 1a rows, the "Witness, per unit" paragraph, the Ratchet).
- THE PROMISE: the unit is BYTE-IDENTICAL in every arm (default, each `--memfn=no-X` deny, `--engine=vm`, both SIMD layers), stamps included. Any unannounced emitted-byte move is answer- or contract-level.

## Rulings and the guide
- Read rulings ONLY at the freeze: `git -C /home/pcrec/projects/pcrec show BASE:docs/dev/decisions.md`, `... BASE:docs/dev/plan.md` (never the live files).
- Guide: docs/dev/guide/README.md, coding.md, architecture.md, style.md, critics.md; docs/dev/learnings.md §3 (check design); memfn/CLAUDE.md, memfn/src/CLAUDE.md, tests/memfn/CLAUDE.md.

## Denylist (do NOT read, list, grep or open)
- docs/dev/lanes/sp1a* (the lane report) and every other docs/dev/lanes/*_report.md / *_deliver.txt; docs/dev/lanes/spanpick_bench_patterns.txt IS part of the subject and is allowed.
- docs/dev/reviews/* files about span_pick / memfn-sp1a / memfn-spanpick* (earlier rounds on this design).
- memfn/docs/journal.md entries dated 2026-11-03.
- /var/tmp/pcrec-pcrec/scratch/memfn/ (the lane's job scripts and logs), worktrees/.boxqueue/, the box queue itself, every other worktree under worktrees/ except crit-memfn-sp1a, job logs anywhere.
- `git log` bodies (subject lines only).
- /var/tmp/pcrec-pcrec/scratch/crit-memfn-sp1a/.coord/ and other critics' dirs.

## Output format
- Your findings file DOES NOT EXIST YET: you CREATE it, and write it INCREMENTALLY (append each finding as you confirm it; do not hold everything to the end).
- Headings required: `## Findings` and `## PROBED-AND-HELD`.
- Each finding: id `<LENS>-n`; CONFIRMED (with repro: input, exact command, observed vs expected) or SUSPECTED (what would confirm it); severity (answer / speed / size / maintenance / doc / design / contract); effort; blast radius; file:line or §.
- A finding against a ruled D-row cites the row and argues, or drops.
- PROBED-AND-HELD: what you probed that held, with case counts.
- When done, run `/home/pcrec/projects/pcrec/scripts/lanecheck --deliver /var/tmp/pcrec-pcrec/scratch/crit-memfn-sp1a/<NAME>/DELIVER.txt --dir /var/tmp/pcrec-pcrec/scratch/crit-memfn-sp1a <NAME>` (the --dir is REQUIRED: without it the marker lands in the repo) and end only after it prints DONE (fix and rerun otherwise). Final reply at most 150 words.
