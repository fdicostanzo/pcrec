# COMMON brief: critic round xarch, CODE mode (2026-11-08)

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and pcrec-bench; in practice you READ pcrec only.
- Write ONLY under your own dir /var/tmp/pcrec-pcrec/scratch/crit-xarch/code/<your-lens>/ (create it). Never /tmp
  (set `export TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-xarch/code/<your-lens>/tmp` and `PCREC_TMPDIR` to your dir
  before running anything that writes temp files).
- READ-ONLY: no edits, commits, checkouts or worktrees in either repo. Never run `make`, `make test`, any suite,
  battery, sabotage matrix, boxqueue/boxlock/chainrun. A plant (a deliberate edit to test a check) is made in a
  PRIVATE COPY under your dir (`git -C /home/pcrec/projects/pcrec archive SUBJECT <paths> | tar -x -C <yourdir>/copy`),
  never in the review tree.
- BOX: this is the owner's evening hold (20:00-01:00). Single-pattern probes only, sequential, prefixed `nice`;
  no `-j`, no loops over a corpus beyond your stated budget. Queued test jobs start at 01:00: stop all probing
  by 00:45. Bound anything that might hang: `timeout 60 ...` (bare `timeout` is GNU on this box).
- Kill only your own processes, by PID (`scripts/safekill PID`); never pkill/pgrep -f.

## Subject (frozen)
- SUBJECT = 424ddc742378f58aa9ffb48d489815714c591bbc (branch lane/u3tgt). BASE = 550e233648b57dab006bed98cf45981126be522d
  (its merge-base with main). It is the joint landing of the memfn kit's unit U2 (merged in from lane/memfn-u2) and
  pcrec's unit U3: one abi event (97 -> 98). What it claims to do: pcrec states the compile's ONE CPU target to the kit
  on every art (`mf_art_target`); the kit admits SIMD levels by `family && needs ⊆ features` and renders level blocks
  with NO CPU `#if`, its selector being ONE call to the top admitted level (else `<fn>__body`); pcrec places the kit's
  family GUARD (file scope, ahead of every #include) and the target's REGION (around the part) and stamps
  `<PREFIX>_TARGETS`; `MF_P_PORTABLE_ONLY` is retired; `MF_TARGET_REQUIRED` = 1 makes the kit refuse an art with no
  target and any unnamed policy bit.
- Secondary (already on main, lightly reviewed): merge d9df92c0d (kit K0, the target table; diff `d9df92c0d^1 d9df92c0d`)
  and merge bfecd6143 (pcrec P1: `-fmemfn-simd[=TOKEN,..]`, `--list-cpu-targets`; diff `bfecd6143^1 bfecd6143`).
- Review tree (built at SUBJECT): /home/pcrec/projects/pcrec/worktrees/crit-xarch (`build/pcrec`, `build/libpcrec.a`).
  Read it with absolute paths or `git -C`; NEVER `cd` into it (a hook blocks it; `(cd X && cmd)` subshells are fine).
- BASE build (git archive of BASE, built): /var/tmp/pcrec-pcrec/scratch/crit-xarch/code/base (`build/pcrec`).
- The diff, with the denylist excluded (use THESE pathspecs on every git diff / git grep / git log -p you run):

      git -C /home/pcrec/projects/pcrec diff BASE SUBJECT -- . ':!docs/dev/lanes/' ':!memfn/docs/lanes/' \
        ':!memfn/docs/journal.md' ':!docs/dev/history/claude_md/' ':!docs/dev/full_suite_ledger.md'

  For plain `grep -r` over a tree, add `--exclude-dir=lanes --exclude=journal.md --exclude-dir=claude_md`.

## Probing (regimes checked by one compile each, 2026-11-08)
- `build/pcrec -p rx [FLAGS] -o OUT.c --pattern 'PAT'` (add `--emit-main` for a runnable driver; see docs/spec/cli.md).
- Regimes: default (no flag) = target `generic`; `-fmemfn-simd` = the host family default (`x86-64` on this box);
  `-fmemfn-simd=x86-64-v3`; `-fmemfn-simd=generic`; arm tokens are family `arm64`, target `armv8-a`;
  `--list-cpu-targets` lists them. A pattern that reaches the SIMD rows: `(?i)hello`
  (BASE `-fmemfn-simd` reads `RX_MEMFN_FORMS "vrun@w32+w16"`, SUBJECT `"vrun@w16"`; at `=x86-64-v3` both `vrun@w32+w16`).
- BASE vs SUBJECT compares: write the two outputs under the SAME basename in two dirs (`b/out.c`, `s/out.c`; the C
  names its basename). A pair counts as 2 compiles in your budget. Delete old outputs before each compile (a refused
  compile leaves the previous out.c in place).
- Compilers on this box: gcc 15.2 (`gcc`), clang 21.1 (`clang`). CPU: Zen 4 7700X (AVX2 + AVX-512).

## Read (the contract and rules)
- Rulings, read at the FREEZE commit only: `git -C /home/pcrec/projects/pcrec show c857164fe:docs/dev/decisions.md`
  (D146 and its Addendum 1, D147, D155, D157, D174, D76/D94 abi ritual, D80), and
  `git show c857164fe:docs/design/memfn/target_seam_units.md` (rev 1: §2 the units table, rows U2/U3; §3 the seam;
  §4 the spec hunks owed; §6 the manager's rulings), `docs/design/memfn/target_seam.md`,
  `docs/dev/reviews/2026-11-07-xarch1-rulings.md` (R1-R4, the rulings file). The plan row is `[XARCH-DEV]`
  (`git show c857164fe:docs/dev/plan.md | grep -n '^- \[XARCH-DEV\]'`; do not read its neighbours).
- The kit's interface sheet for U3 (the U2/U3 contract, extracted for you):
  /var/tmp/pcrec-pcrec/scratch/crit-xarch/code/u3_interface_sheet.md
- The kit's request: R-37 in memfn/docs/requests.md.
- Spec hunks in the diff: docs/spec/match_api.md §6.3.10¶3-¶4, ¶8-¶9,  para 14 (lane/u3tgt)- para 15 (lane/u3tgt), §6.3.12 table, §10.7 para 4 (lane/u3tgt), §1 and §6¶17
  (abi); docs/spec/tuning.md §2.43; docs/spec/cli.md §1.24, §2.16; lib/pcrec.h.
- Guide: docs/dev/guide/README.md, coding.md, architecture.md, style.md, critics.md; docs/dev/learnings.md §3
  (check design); memfn/CLAUDE.md, src/gen/CLAUDE.md, tests/memfn/CLAUDE.md.

## Denylist (D27 applied to review: do not open, grep, diff or list these)
- docs/dev/lanes/ files named u3tgt*, u3fix*, u3floor*, u3mov*, p1cpu*, p1tri*, citri3*, mechtri*, u2*, k0*, memfn-u2*,
  and every docs/dev/lanes/*_rulings.md (simplest: exclude docs/dev/lanes/ entirely); memfn/docs/lanes/ (all);
  memfn/docs/journal.md; docs/dev/history/claude_md/; docs/dev/full_suite_ledger.md; worktrees/.boxqueue/ and every
  other worktree but worktrees/crit-xarch; job logs; `git log` bodies beyond subject lines.
- Earlier reviews of this subject: docs/dev/reviews/2026-11-07-r1-xarch.md and docs/dev/reviews/2026-11-07-r1-xarch/.
- Under /var/tmp/pcrec-pcrec/scratch/: u3tgt, u3fix, u3floor, u3mov, critgap, citri3, xarch1, xarchrev1, xarchseam;
  and inside crit-xarch/ EVERYTHING except crit-xarch/code/ (an earlier round's files), and crit-xarch/code/.coord/.
- Other critics' dirs under crit-xarch/code/ (work independently).

## Output (your findings file does NOT exist yet: CREATE it as your FIRST action)
- File: /var/tmp/pcrec-pcrec/scratch/crit-xarch/code/<lens>/findings.md, headings `# <LENS> findings`, `## Findings`,
  `## PROBED-AND-HELD`. Append each finding the MOMENT you have it, one append per finding (never write it all at the end).
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, exact command, observed vs expected) or SUSPECTED (what
  would confirm it); severity (answer / speed / size / maintenance / doc / design); effort; blast radius; file:line or §.
  A finding against a ruled D-row or §6 ruling cites it and argues, or drops.
- PROBED-AND-HELD: what you tried that held, with case counts.
- If your findings-file Write is REFUSED by a harness rule, do not route around it: SendMessage the findings to
  the coordinator (whoever launched you; your parent) at once marked "relayed", and return them as your final text.
- End: run `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-xarch/code --deliver
  /var/tmp/pcrec-pcrec/scratch/crit-xarch/code/<lens>.deliver <lens>` and finish only when it prints DONE. Final reply
  at most 150 words.
