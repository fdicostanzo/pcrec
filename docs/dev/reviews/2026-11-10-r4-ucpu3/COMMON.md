# COMMON brief: critic round ucpu3 (CODE review)

## Scope mandate
Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and, read-only if ever needed, pcrec-bench
(/home/pcrec/projects/pcrec-bench). You are READ-ONLY on both: no edits, no commits, no `make`, no
`make test`, no suites, no box lock, no box queue, no worktrees. Scratch ONLY under YOUR dir
/var/tmp/pcrec-pcrec/scratch/crit-ucpu3/<lens>/ (it exists). Never /tmp. Set
PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-ucpu3/<lens> for anything you run. Kill only your own
processes, by PID (never pkill -f). Bound every uncertain command with `timeout 120`. Absolute paths;
never `cd` into a worktree in a chained command (a hook blocks it; use `( cd X && ... )` or `git -C`).
A FULL SUITE is running on this box: you run SINGLE compiles, `gcc -O2`/`gcc -S` of single files and
small probe loops ONLY, at most ~50 pcrec compiles per critic in total (a BASE/SUBJECT pair = 2),
under `nice`. No sweeps over the corpus.

## Subject (frozen)
- Branch lane/ucpu3b, SUBJECT = 2b5adbff1010aa042b0a62e96752e8f62774c039,
  BASE = merge-base with main = 7d74499bc717a5c8f3c6a6bbc7c6f106e50c8a58 (main's src/ has not moved since).
  Diff: `git -C /home/pcrec/projects/pcrec diff 7d74499bc 2b5adbff1 -- . ':!docs/dev/lanes' ':!docs/dev/history'`
- What it builds: [UCP] stage U3, the ISLAND DFA (the character-stepped DFA) for UCP contexts under
  `-e utf8` (UCP `\b`/`\B`, whose Unicode word set is not byte-expressible). ASCII bytes step the
  table; a non-ASCII character steps as one "character atom"; an ill-formed byte is its own atom.
  It also lifts the U1 refusal of WIDE UCP sets under utf8. Stamp: `RX_DFA_SCAN "island"`.
- SUBJECT tree, BUILT, read-only: /home/pcrec/projects/pcrec/worktrees/crit-ucpu3 (build/pcrec, build/libpcrec.a)
- BASE compiler, BUILT: /var/tmp/pcrec-pcrec/scratch/crit-ucpu3/base/build/pcrec (a git-archive export of
  7d74499bc; its source is beside it under .../base/). Read-only.
- Spelling (checked): `build/pcrec -p rx -e utf8 --features all --emit-main -o F.c --pattern '(*UCP)\b\w+\b'`
  then `gcc -O2 -o F F.c && ./F 'subject'` prints `match S E` (stamps RX_ENGINE "dfa", RX_DFA_SCAN "island").
  `--engine=dfa|vm|auto`, `--no-captures`, `-fstartpos-guard=`, `-futf-check=` exist (see `build/pcrec --help`).
  Without `--features all`, `\b` is refused ("requires module 'assertions'"). When comparing BASE vs
  SUBJECT emitted C, emit under the SAME basename in two dirs (the C names its basename).
  For the C entry points (search from a startpos, find-all, next_pos) read docs/spec/match_api.md and write a
  tiny driver against the emitted .c (no --emit-main) when you need more than `match S E`.
- ORACLE: system libpcre2-8 10.46 (2025-08-27), via python ctypes (`ctypes.CDLL("libpcre2-8.so.0")`).
  The ruled utf8 semantics are PCRE2_UTF|PCRE2_UCP|PCRE2_MATCH_INVALID_UTF for ill-formed subjects
  (UTF=0x00080000, UCP=0x00020000, MATCH_INVALID_UTF=0x04000000). A working ctypes setup is in
  docs/dev/lanes/ucpu3b_evidence/gen_island_rxt.py (readable; it is the generator of the new tests,
  so do not trust its choices: write your own oracle calls). Python with `-I`.
- Tests the branch adds/changes: tests/ucp/island.rxt, tests/utf8/island_illformed.rxt, tests/ucp/refusals.rxt,
  tests/ucp/ucp_compare.py, tests/ucp/ucp_sets.py, tests/reject/run_reject_tests.sh, tests/registry/*.
  Format: docs/spec/rxt_format.md.

## Rulings (read at the FREEZE, never the live tree)
`git -C /home/pcrec/projects/pcrec show eb83f0902:docs/dev/decisions.md` (and plan.md). Relevant: D134
(the charter: island ONLY where no all-byte DFA form exists; chosen over the VM hybrid only by a MEASURED
selection row; after [UTF-VALID]), D130 (UCP design rulings, esp. item 3), D133 ([UTF-VALID]), D129 Q4/Q6,
D26, D80 (spec in the same change), D76/D94 (emitted scaffolding = abi event), D174 (names describe
behaviour). Plan row: locate with `grep -n '^- \[UCP\]'` and read only that row; its long body is
docs/design/plan_row_bodies/UCP.md.

## Docs you will need (at the SUBJECT tree)
docs/dev/guide/{README,coding,style,architecture,critics}.md; docs/design/ucp_design.md (esp. §0.1 T4,
§3, §3.8 hazards H1-H4); docs/design/ucp_measurements/u3_island_twin.md; docs/spec/cli.md §1.9,
limits.md §3.8/§3.9, match_api.md §6.3.2 + the stamps table, pattern_language.md §7.1/§7.8, §9.5 of
match_api.md (empty-match divergence beside ill-formed bytes); docs/testing.md (mech / sabotage rows).
Code: src/ir/nfa.c, src/ir/dfa.c, src/gen/emit_dfa.c, src/opt/select_engine.c, src/core/compile.c,
src/core/internal.h, src/parse/mod_ucp.c, src/parse/mod_assertions.c, src/facts/kset.c, src/opt/dfamemo.c.

## DENYLIST (do not open, grep, diff or list; exclude from every git diff/grep)
docs/dev/lanes/ucpu3b_report.md, docs/dev/lanes/ucpu3b_evidence/*.tsv, docs/dev/lanes/u3twin*,
docs/dev/lanes/ucpu2*, docs/dev/history/ (all), docs/dev/reviews/2026-09-28-r1-ucp-design.md,
git log BODIES (subject lines OK), box-queue job logs (jobs 430-433 and all others), the box queue,
other worktrees (only worktrees/crit-ucpu3 is yours), /var/tmp/pcrec-pcrec/scratch/crit-ucpu3/.coord/
and other critics' dirs. For git diff/grep add `':!docs/dev/lanes' ':!docs/dev/history'`; for plain grep
`--exclude-dir=lanes --exclude-dir=history --exclude-dir=worktrees --exclude-dir=.coord`.

## Output format
Your findings file DOES NOT EXIST YET: CREATE it as your FIRST action at
/var/tmp/pcrec-pcrec/scratch/crit-ucpu3/<lens>/findings.md with headings
(`# <LENS> findings`, `## Findings`, `## PROBED-AND-HELD`), and APPEND each finding the moment you have
it, one append per finding. Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command,
observed vs expected; for a text claim the quoted lines file:line) or SUSPECTED (what would confirm it);
severity (answer / speed / size / maintenance / doc / design); effort; blast radius; file:line or spec §.
A finding against a ruled D-row cites it and argues, or drops. End with PROBED-AND-HELD (what held, with
case counts). If your Write is REFUSED, do not route around it: return the findings as your final text.
Then run `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-ucpu3 --deliver /var/tmp/pcrec-pcrec/scratch/crit-ucpu3/<lens>.deliver <lens>`
and end only after it prints DONE. Final reply at most 150 words.
