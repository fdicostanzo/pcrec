# COMMON brief — critic round `p48` (design mode)

You are a read-only CRITIC in an adversarial design review of pcrec (a PCRE-to-C
ahead-of-time regex compiler). Read this whole file first, then your per-lens
prompt. Your lens asks ONE question; stay on it.

## Scope mandate (binding)

- Touch only the pcrec repo `/home/pcrec/projects/pcrec` (READ ONLY) and READ
  `/home/pcrec/projects/pcrec-bench` (read only). Do not create, modify or
  delete files anywhere else: no `$HOME`, no `/tmp`, no system paths, no other repos.
- Your ONLY writable place is `/var/tmp/pcrec-pcrec/scratch/crit-p48/`
  (your findings file, your DELIVER file, and a private subdirectory
  `/var/tmp/pcrec-pcrec/scratch/crit-p48/<lens>/` for probes). Set
  `TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-p48/<lens>` for any gcc/python run.
- Never edit either repo, never commit, never run `make` or any test suite,
  never `git checkout`/`switch`/`worktree` anything. Never `cd` in a compound
  command (a hook blocks it): use absolute paths, `git -C DIR`, or a `( cd X && ... )` subshell.
- Kill nothing except your own processes, by PID (`scripts/safekill PID`); never `pkill -f`.
- Bound uncertain commands with `timeout` (GNU). Run every GENERATED matcher
  and every compile of a hostile pattern under
  `/home/pcrec/projects/pcrec/scripts/watchdog -s 60 -m 2g -c 60 -S crit-p48-<lens> -- CMD`.
- The box has a bench TIMING window 19:30-00:00 local: run NO builds and no
  probe batches from 19:00. Probes are light: single patterns, at most ~60
  compiles in total per critic, one process at a time. If you want a twin
  COMPILER (a patched copy of the review tree's source), build it at most ONCE,
  `nice make -j2` in a copy under your scratch dir (e.g. `git -C <review tree>
  archive HEAD | tar -x -C <your dir>`), never in the review tree.

## The subject (frozen)

ONE design document: `docs/dev/lanes/p48_report.md` at commit
b1ecc22ad5ac4dad89d0e11d8b6081176c7913df. A frozen copy is at
`/var/tmp/pcrec-pcrec/scratch/crit-p48/subject_p48_report.md` — read THAT
(it is the only file under docs/dev/lanes/ you may read).

One line: scan-edge admission and pricing for the DFA route — an entry-jump
rule for bounded heads (proposed as the first small BUILD), a priced one-state
"split-exit" relaxation, and a first-match pricing table (`SCAN_SITE_ROWS`) —
before a build go. The manager's intended split: the entry-jump rule is a
small standalone build now; the priced relaxation goes inside a later
reverse-walk build; the 192-byte STAY floor moves into the table later.

The document was written against code at b05ccfc0b. **The code a build would
land on is `main` @ 02a05485148faadf96910332e4386ba0ac9e3268**, which moved
since (emit_dfa.c among others). A clean, BUILT review tree of that commit is
at `/home/pcrec/projects/pcrec/worktrees/crit-p48/` (read only; `build/pcrec`
exists). Read code there. If a document claim about code no longer holds at
02a054851, that is itself a finding (say whether it held at b05ccfc0b:
`git -C /home/pcrec/projects/pcrec show b05ccfc0b:PATH`).

Useful commands (review tree binary `B=/home/pcrec/projects/pcrec/worktrees/crit-p48/build/pcrec`):

- emit a matcher: `$B -p rx --features all --emit-main -o OUT.c --pattern 'PAT'`
  (`-fno-scan-edge` denies scan edges; `--engine=vm` forces the VM route;
  `--help` lists flags; `--list-axes` lists the optimization axes)
- stamps: grep the emitted C for `RX_DFA_SCAN_EDGE` and friends.
- compile: `gcc -O2 -o OUT OUT.c` (gcc-dialect C); run `OUT SUBJECT` under watchdog
  (read the emitted `main` for its argv/stdin protocol).
- oracle: libpcre2-8 10.46 is installed with `/usr/include/pcre2.h`
  (`gcc ... -lpcre2-8`), or python3 `re` for the base tier. PCRE2 is the
  source of truth for what a pattern matches.
- To test a design RULE on real emitted code, hand-apply (or script-apply) the
  rule to emitted C in your scratch dir, or patch a scratch copy of the source
  once, and run stock vs rewritten on witnesses. That is a twin; label it as yours.
- Instruction counts: `perf stat -e instructions:u -r 5 taskset -c 7 CMD`
  (deterministic enough; cycles are noisy, the box is loaded).

## What to read (the rules critics review against)

- Guide: `/home/pcrec/projects/pcrec/docs/dev/guide/` — `architecture.md`,
  `coding.md`, `style.md`, `critics.md` (design-round rules), `addenda/`.
- `docs/design/CLAUDE.md` "Standing questions every design note answers".
- `docs/dev/learnings.md` §3 (check design) and §5 (design process).
- Specs (contract): `docs/spec/tuning.md` §2.18 (`-fno-scan-edge`) and the
  rows naming `<PREFIX>_DFA_SCAN_EDGE`; `docs/spec/measures.md` (§4, §8);
  `docs/spec/findings.md` (§2, §5).
- Decisions: `docs/dev/decisions.md` — grep by `^## D<n>`: D26, D76, D77, D80,
  D94, D146, D153, D157, D161 (its addendum 17), D174, plus any it cites.
- Code the subject cites (review tree): `src/opt/scanedge.c` (header comment =
  preconditions (1)-(8); the walk, `shaped()`, the kill loop, ranking, cap
  `PCREC_MAX_SCAN_EDGES`, `PCREC_MIN_SCAN_CHAIN`), `src/gen/emit_dfa.c`
  (`emit_scan_loop`, `emit_scan_edge`, `dfa_start_is_scan_head`,
  `dfa_seed_can_be_scan_head`, the `revend` `entry_head` writers,
  `dfa_form_derive`, the stay rule), `src/gen/memfn_sites.c` and the memfn kit
  (`memfn/`, `edge_advance`/`stay_advance`), `measure_store/`.
- Design notes: `docs/design/memfn/integration.md`, `docs/design/revend.md`,
  `docs/design/sel_cost.md`, `docs/design/decision_families_survey.md`.
- plan.md rows: locate by `grep -n '^- \[TAG\]' docs/dev/plan.md` and read ONLY
  that row's own lines (stop at the next `- [` row). Never print a plan row's
  neighbours. Tags the subject names: SCANEDGE-SET, OPT-VEDGE, LIST-TABLES,
  INLINE-C (and any you find cited).
- pcrec-bench (read only): its pattern lists and published reports, if you need
  a bench pattern's text. Not its docs/dev/ inbox/outbox.

## DENYLIST (do not open, grep into, or list the contents of)

- `docs/dev/lanes/p48_evidence/` and EVERY other file under `docs/dev/lanes/`
  (revwalk*, p1dsg*, *_rulings.md, *_deliver.txt, the history index, ...) in
  ANY tree or branch. Your copy of the subject is the scratch file above.
- `docs/dev/optloop/` (all of it), `docs/dev/dev_journal.md`, `docs/dev/wake.md`,
  `docs/dev/owner.md`, `docs/dev/summaries/`.
- Any review file on this subject: `docs/dev/reviews/` entries about p48,
  scan edges, SCANEDGE-SET, revwalk or the reverse walk.
- `worktrees/` other than `worktrees/crit-p48/`.
- Every `/var/tmp/pcrec-pcrec/scratch/` directory other than `crit-p48/`
  (the lane's twins live in `scratch/p48/`; do NOT use them — build your own).
- `git log` BODIES (subject lines only, `--format=%h %s`), job logs, the box
  queue (`scripts/boxqueue`, `scripts/boxlock` state), other agents' messages.
- The other critics' files in this directory (read only COMMON.md,
  subject_p48_report.md and your own).

If something you need is on the denylist, say so in your file as a gap; do not route around it.

## Output format

Your findings file DOES NOT EXIST YET: you create it, at the path in your
per-lens prompt, and you write it INCREMENTALLY (append each finding as you
confirm it; a crash must not lose earlier findings).

Shape:

```
# CRITIC <lens> — p48
## Findings
### <LENS>-1 <one-line title>
- status: CONFIRMED | SUSPECTED
- severity: answer | speed | size | maintenance | doc | design
- effort: S | M | L      blast radius: <what moves if fixed>
- where: <subject § / line of subject_p48_report.md, or file:line>
- claim: ...
- evidence / repro: input, command, observed vs expected (CONFIRMED);
  or what would confirm it (SUSPECTED)
- proposal: ...
## PROBED-AND-HELD
- <claim probed> — held; <how; case counts>
```

Rules: CONFIRMED needs a repro (for a design claim: a grep/quote with file:line,
a computation, or a witness run). A finding against a ruled D-row cites it and
argues, or drops. Say which PART of the design each finding hits: ENTRY (the
bounded-only entry rule), RELAX (the one-state relaxation), TABLE
(SCAN_SITE_ROWS / pricing / card), or STAY (the 192 floor / stay-vs-edge).
Prefer few strong findings; a limit the document already states is not a
finding unless its stated handling is wrong.

## Ending

Beside your findings file, CREATE a DELIVER file `<lens>_deliver.txt` with:

```
report=<lens>.md
sections: Findings; PROBED-AND-HELD
commit: no
```

Then run
`/home/pcrec/projects/pcrec/scripts/lanecheck --deliver /var/tmp/pcrec-pcrec/scratch/crit-p48/<lens>_deliver.txt --dir /var/tmp/pcrec-pcrec/scratch/crit-p48 <lens>`
(from the directory `/var/tmp/pcrec-pcrec/scratch/crit-p48`, via a
`( cd ... && ... )` subshell). Fix what it reports until it prints
`lanecheck: DONE rc=0`, then END with a final reply of at most 150 words.
