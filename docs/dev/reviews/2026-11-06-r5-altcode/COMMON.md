# COMMON brief — critic round altcode (CODE mode), 2026-11-06

Read this whole file first. Then do the ONE question in your per-lens prompt.

## Scope mandate (binding)

- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and, READ-ONLY,
  pcrec-bench (/home/pcrec/projects/pcrec-bench). Nothing else on the machine.
- You are READ-ONLY on both repos. No edits, no commits, no `git checkout`,
  no `git worktree`, no `git stash`. You never run `make`, any test suite,
  `scripts/emit_sweep.py`, a census script, a mech/sabotage runner or any
  sweep over the corpus. You never take or query the box lock or box queue.
- Scratch ONLY under your own dir `$R/<lens>/` where
  `R=/var/tmp/pcrec-pcrec/scratch/crit-altcode`. Never /tmp. Export
  `PCREC_TMPDIR=$R/<lens>` in every shell that runs a repo script.
- Never open, grep or copy any PCRE2 SOURCE copy (D181). The libpcre2 SHARED
  LIBRARY (`libpcre2-8.so.0`, ctypes) is the answer oracle and is fine.
- Kill a process only via `scripts/safekill PID`. Never pkill/pgrep -f.
- Run probes `nice`, one at a time (the box is shared; it is the owner's
  evening hold: light interruptible work only, NO wall-clock timing; an
  instruction COUNT via `perf stat -e instructions:u` pinned with
  `taskset -c 7` is allowed, a few runs, never a loop of hundreds).
- Budget: about 1,500 compiles per critic (a BASE/SUBJECT pair counts 2).
  Wall-clock target: findings file complete within ~100 minutes.
- Use absolute paths. Never `cd` into worktrees/ in a chained command
  (a hook blocks it); `( cd X && ... )` subshells are fine.

## Subject (frozen)

- SUBJECT = `4cc8164468f823434e515de779e1697c578bc677` (branch lane/altbuild:
  the alternation normal form, stages 1, 2p, 2b, plus a follow-up fix lane's
  commits, the K139 drop-islands retry row among them).
- BASE = `80341284e0895815867e202ac74437d694c98f67` (merge base with main).
  The branch is NOT merged with current main; review it against BASE.
- Rulings frozen at main `eeff8964089ab994f73f24811d774d4b92756ffe`.
- Review tree (SUBJECT, built): `/home/pcrec/projects/pcrec/worktrees/crit-altcode`
  — binary `.../worktrees/crit-altcode/build/pcrec`.
- BASE export (built): `$R/base` — binary `$R/base/build/pcrec`.
  Read BASE files there or via `git show BASE:path`.
- The design the code implements: `git show SUBJECT:docs/design/alt_normal_form.md`
  (1971 lines). Most relevant: §1 goals G1-G5, §2.2-2.3 ledger, §3.2
  (preference / adjacency test, side effects), §3.3 (the rewrite owner, rules
  M/P/S, the procedure), §3.4-3.6 (per-length pieces, the description), §4.4,
  §4.7, §5 Stage 1, Stage 2p, Stage 2b (gates, predicted movers, sabotage
  witnesses), §6, §11 deny levers. Stage 2a and Stage 3 are NOT built.
  The design cites lane reports and review files; those are DENIED (below):
  judge the code against the design's TEXT and the spec, not against them.

The diff (always use these exclusions, in every git diff / log -p / grep):

    git -C /home/pcrec/projects/pcrec diff BASE SUBJECT -- . \
      ':!docs/dev/lanes' ':!docs/dev/reviews' ':!.coord'

`git log --format='%h %s' BASE..SUBJECT` (subject lines only) is allowed;
never read commit BODIES. For PLAIN grep over the review tree use
`--exclude-dir=lanes --exclude-dir=reviews --exclude-dir=worktrees`.

Main code touched: src/opt/altnf.c (new, the owner), src/opt/altcls.c,
src/opt/lower_enc.c, src/facts/desc.{c,h} (new, the description),
src/facts/req.c, src/facts/facts.{c,h,def}, src/gen/emit_vm.c (island),
src/gen/emit_dfa.c, src/core/compile.c (size-cap retry table `fit_rungs[]`,
the drop-islands row), src/core/limits.{def,h}, src/core/internal.h,
src/dump/*, lib/pcrec.h. Spec hunks: docs/spec/tuning.md, match_api.md,
limits.md, facts_listing.md. Tests and checks: tests/altcls/, tests/utf8/
altnf_lowering.rxt, tests/island/run_island_tests.sh, tests/codegen/*,
tests/axes/run_axes.sh, tests/mech/sabotages/S1880-S1894 and re-anchored
S66/S303/S366/S-U8/S693, scripts/emit_sweep.py, scripts/alt_census.py.
docs/dev/known_issues.md K139 describes the retry-row fix (read it; its
evidence pointers into docs/dev/lanes/ are denied).

## The guide and rulings

- Guide: `docs/dev/guide/README.md`, `coding.md`, `architecture.md`,
  `style.md`, `critics.md`, `addenda/` (read at SUBJECT).
- Rulings: read via `git show eeff8964:docs/dev/decisions.md` (never the
  live tree). Relevant: D26 (+ addenda), D76/D94 (abi ritual), D77, D80
  (spec in the same change), D153, D174 (names), D186 (unit vs choice
  change), D187, D146/D147/D157 (kit seam). plan.md rows: locate ONLY by
  `git show eeff8964:docs/dev/plan.md | grep -n '^- \[TAG\]'` and read that
  row's own lines; never print neighbours. Tags: [RUN-POS-SET],
  [LOWERENC-SEAL], [ENG-ISL-S2], [ISL-PRICE].
- Spec (contract): `docs/spec/tuning.md` §2.6, §2.7, §2.20, §2.27, §2.28,
  §2.33; `docs/spec/match_api.md` §6.3.11; `docs/spec/limits.md` §8.4-8.5;
  `docs/spec/facts_listing.md` §4.1.2.

## Denylist (never open, grep, diff or list)

- `docs/dev/lanes/` — entirely (lane reports, rulings, evidence; in
  particular altbuild*, altbuild2*, altd*, altdesign*, altrev*, altthink*).
- every `docs/dev/reviews/` file or directory (in particular any name
  containing "alt-normal-form" or "alt-island").
- every other worktree under /home/pcrec/projects/pcrec/worktrees/ except
  crit-altcode; the box queue, its logs, job logs.
- `$R/.coord/` and other critics' dirs under `$R/`.
- git commit BODIES (`git log` beyond subject lines, `git show <commit>`
  without a path).

## Regimes and how to probe

- Encoding: byte (default), `-e utf8`. Engines: `--engine=auto|dfa|vm`.
- Module-gated patterns (lookbehind, backrefs, recursion) need
  `--features all`.
- Deny levers in play: `-fno-altcls-merge` (bit 10, rule M, both callers),
  `-fno-altcls-factor` (bit 11, rules P and S), `-fno-alt-island`,
  `-fno-cls-kit`. `--list-limits`, `--emit-facts[=ENC]` are dumps.
- Analysis regimes: default prior; `-I tests/findings/adversarial
  --analysis=uniform` (all-tie) — run that one from the review tree:
  `( cd /home/pcrec/projects/pcrec/worktrees/crit-altcode && build/pcrec ... )`.
- Checked spellings (coordinator, one compile each):
  `build/pcrec -p rx -e utf8 --engine=vm -o OUT/x.c --pattern 'x(?:[éà]1|q2|r3)y'`
  (stamps `RX_VM_ALT_ISLANDS`, `RX_ALTCLS_MERGES`, `RX_ALTCLS_FACTORED` as
  `#define`s in the C); `build/pcrec -p rx --emit-facts -e utf8 --pattern
  '(?i)москва'` (one TSV row per fact; the new one is `req_pieces`).
- Compare BASE vs SUBJECT emitted C under the SAME basename in two dirs
  (`$R/<lens>/base/x.c` vs `$R/<lens>/subj/x.c`): the C names its basename.
- Running a matcher: `--emit-main` then `gcc -O1 -o m x.c`; `./m SUBJECT`
  (see `build/pcrec --help` for the output shape).
- Answer oracle: libpcre2-8 via ctypes (system `libpcre2-8.so.0`); a worked
  binding is `tests/subst/d27/lib/ref_pcre2.py` (copy the pattern, not the
  file; utf8 = UTF|UCP, add MATCH_INVALID_UTF if you test ill-formed
  input). Report span AND every capture group, and `\K` start.
- Corpus: `tests/**/*.rxt` and `*.rxtin` in the review tree. Bench patterns:
  pcrec-bench (read-only).

## Output format

Your findings file `$R/<lens>/findings.md` DOES NOT EXIST YET. CREATE it as
your FIRST action, with these headings, then write it INCREMENTALLY as each
finding firms up (a critic that writes last may write nothing):

    # <lens> findings — altcode
    STATE: working
    ## Findings
    ## PROBED-AND-HELD
    ## Notes

Each finding under `## Findings`:

    ### <LENS>-n: one-line title
    - status: CONFIRMED (repro: input, exact command, observed vs expected)
      | SUSPECTED (what would confirm it)
    - severity: answer | speed | size | maintenance | doc | design
    - effort: S | M | L ; blast radius: who/what is affected
    - where: file:line at SUBJECT, or design §
    - argument (a finding against a ruled D-row cites the row and argues, or drops)

`## PROBED-AND-HELD`: what you probed that held, with case counts.
When done, set `STATE: done` and run
`PCREC_TMPDIR=$R/<lens> /home/pcrec/projects/pcrec/worktrees/crit-altcode/scripts/lanecheck --dir $R --deliver $R/<lens>/DELIVER <lens>`
and END only after it prints DONE (fix the file and re-run if it does not).

If your findings-file Write is REFUSED, SendMessage the findings to
`crit-altcode` AT ONCE marked "relayed"; do not route around a refusal.
Final reply: at most 150 words.

If a check needs a PLANTED build (a source edit + rebuild) you cannot do
read-only, write the exact plant under `## Notes` as `PLANT-REQUEST:` (file,
edit, the witness command, expected SAME / SILENT-MOVE / LOUD) and record the
finding SUSPECTED; the coordinator may build up to three.
