# COMMON brief: critic round crit-sae2 (code), 2026-11-09

Read this whole file before your own prompt.

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and pcrec-bench. You make NO edits to either repo
  (no commits, no file writes, no worktrees). Scratch ONLY under your own dir
  `/var/tmp/pcrec-pcrec/scratch/crit-sae2/<your-lens>/` (create it). Never /tmp. Set
  `PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-sae2/<your-lens>` for any repo script you run.
- READ-ONLY critic: never run `make`, `make test`, any suite, harness, mech, emit_sweep or battery.
  You MAY run the prebuilt binaries below on single patterns, `gcc -O2` a generated matcher and run it,
  and `gcc -S`. Run probes sequentially with `nice` (the box runs queue jobs). Budget: at most ~800
  compiles of pcrec in total (a BASE/SUBJECT pair counts as 2). Bound anything uncertain with
  `timeout 60`.
- Kill nothing (no pkill/pgrep -f).

## Subject (frozen)
- SUBJECT = lane/sae2 at `8e8960cf86925d23abba05f0f46f519007227e26`.
- BASE = `c17a1272294cdb17720bd1ae8d08f38e82e0c0c3` (= merge-base with lane/sae1: E1, reviewed separately;
  later commits on lane/sae1 are NOT part of this subject).
- The diff: `git -C /home/pcrec/projects/pcrec diff c17a12722 8e8960cf8 -- . <EXCLUDES>` (EXCLUDES below; use them
  on EVERY git diff/log/grep you run).
- Unit: span arms **E2**. Every node that consumes nothing becomes CAT's width-0 unit in the necessary-run walk:
  T3 as the first-match table `rb_zero_rows` in `src/facts/req.c`; new `pcrec_pd_zero` in `src/facts/desc.c`;
  `pcrec_pd_cat`'s identity shortcut limited to exact groups; restore arms `empty` (plain `A_EMPTY`) and `zero`
  (E-4 and E-5) in `src/facts/walk_arms.def`; spec rewording of `docs/spec/match_api.md` §6.3.7¶6 and
  `docs/spec/tuning.md` §2.28¶1 ("every successful attempt contains the run", covering `\K`), and
  `docs/spec/facts_listing.md` 4.1.3 para 4a (lane/sae2); witnesses in `tests/litscan/spanarms.rxt`; sabotage rows
  `tests/mech/sabotages/S1925..S1929_*.sh`; `[facts-arm]` in `tests/codegen/run_facts_checks.sh`;
  `tests/axes/run_axes.sh` arm list; `tests/compound/run_lever_fence.sh` allowlist.

## Trees and binaries (prebuilt; do not rebuild)
- SUBJECT review tree: `/home/pcrec/projects/pcrec/worktrees/crit-sae2` — `build/pcrec`, `build/pcrec-harness`.
- BASE tree (git archive export): `/var/tmp/pcrec-pcrec/scratch/crit-sae2/base` — `build/pcrec`, `build/pcrec-harness`.
- PLANTED SUBJECT builds, one per sabotage row (the row's SAB_BEFORE->SAB_AFTER applied to the subject):
  `/var/tmp/pcrec-pcrec/scratch/crit-sae2/plants/S19NN/build/pcrec` (and `pcrec-harness`), NN = 25..29.
- Spellings (checked):
  - facts: `build/pcrec --features all --emit-facts --pattern 'ab\Kcd' | grep -E '^byte\s+req_'`
    (columns: encoding, fact, ..., status, value, why). `--emit-facts=byte,utf8` for both encodings.
  - restore lever (harness build only): `build/pcrec-harness --features all --harness=restore=zero --emit-facts ...`
    (arms `empty`, `zero`).
  - matcher: `build/pcrec -p rx --features all --emit-main -o DIR/rx.c --pattern 'PAT'`; `gcc -O2 -o DIR/rx DIR/rx.c`;
    `DIR/rx SUBJECT` (subject from argv[1]). The `.c` carries `#define RX_REQ_RUN`, `RX_REQ_BYTE`, `RX_REQ_WHY`.
    Compare BASE/SUBJECT emitted C under the SAME basename in two dirs (the C names its basename).
    Flags/encodings: see `build/pcrec --help` (`-e utf8`, `--engine=vm`, multiline/caseless via inline `(?m)`, `(?i)`).
- libpcre2 oracle (match bounds): `python3 -I /var/tmp/pcrec-pcrec/scratch/crit-sae2/pcre2_bounds.py [--utf] [--multiline] PAT SUBJ...`
  prints the first match's reported (start,end) per subject, or `nomatch`. python `re` is NOT an oracle for `\K`.

## Read (ruling and design versions are FROZEN; read them via git show, never the live tree)
- Rulings at main `90ab55fd3`: `git -C /home/pcrec/projects/pcrec show 90ab55fd3:docs/dev/decisions.md`
  — D191 (grep `^## D191`), and the D168 addendum it refers to. plan.md row `[REQ-EMPTYCAT]` only: locate by
  `grep -n '^- \[REQ-EMPTYCAT\]'` and read that row alone.
- Design: `git -C /home/pcrec/projects/pcrec show 90ab55fd3:docs/design/span_arms.md` — §4 whole, §5.1 (where E2
  ends and L1 begins), §6 (tables; T3), §8 row E2 and its gates, §12 (D168 addendum, zero-width homing), §12a, §12b.
  (§12c landed on main after the lane branched; it concerns L2, not E2.)
- The guide: `docs/dev/guide/` (coding.md, style.md, critics.md, architecture.md) in the SUBJECT tree.
- Specs as changed: `docs/spec/match_api.md` §6.3.7 (all paragraphs), `docs/spec/tuning.md` §2.27-§2.28,
  `docs/spec/facts_listing.md` §4.1.3, in the SUBJECT tree; the BASE text in the BASE tree.

## Rulings in force (state them as rulings; a finding against one cites it and argues, or drops)
- R-a: E2 also takes plain `A_EMPTY` (row E-1), moved from alt_normal_form stage 2a; it restores under arm `empty`.
- R-b: the `zero` arm restores BOTH E-4 and E-5 at E2 (E-5, the positive lookaround, is the plain unit until L1).
- R-c: E2 owns the run-definition spec wording now (L2 later adds only its past-the-consumed-end clause).
- R-d: `<PREFIX>_REQ_BYTE` keeps its meaning "a byte every match contains" (D191).
- Known shared gap, OUT OF SCOPE (do not report): the restore lever does not reach compound parts (being fixed on lane/sae1).

## Denylist (never open, diff, grep or cite)
- `docs/dev/lanes/sae2*`, `docs/dev/lanes/sae1*`, `docs/dev/lanes/sar1*`, `docs/dev/full_suite_ledger.md`,
  `docs/dev/reviews/*sae*` (and their dirs), `memfn/docs/journal.md`, `memfn/docs/responses.md`,
  `worktrees/.boxqueue/`, `worktrees/sae2/`, `worktrees/sae1/`, `worktrees/sar1/`, any other worktree except
  `worktrees/crit-sae2`, `/var/tmp/pcrec-pcrec/scratch/sae2/`, `/var/tmp/pcrec-pcrec/scratch/crit-sae2/.coord/`,
  other critics' dirs in the round dir, job logs, the box queue, and `git log` BODIES (subject lines only: `git log --format=%s`).
- EXCLUDES for every git diff/grep: `':!docs/dev/lanes/sae2*' ':!docs/dev/lanes/sae1*' ':!docs/dev/lanes/sar1*'
  ':!docs/dev/full_suite_ledger.md' ':!memfn/docs/journal.md' ':!memfn/docs/responses.md' ':!docs/dev/reviews/*sae*'`.
  For PLAIN `grep -r`, pass `--exclude='sae2*' --exclude='sae1*' --exclude='sar1*' --exclude=full_suite_ledger.md
  --exclude=journal.md --exclude=responses.md --exclude-dir=.boxqueue` (plain grep ignores git pathspecs), and never
  grep under `worktrees/` other than `worktrees/crit-sae2`.

## Output format
- Your findings file DOES NOT EXIST YET: CREATE it as your FIRST action, with headings `## Findings` and
  `## PROBED-AND-HELD`, then append each finding THE MOMENT you have it, one append per finding.
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, exact command, observed vs expected) or SUSPECTED
  (what would confirm it); severity (answer / speed / size / maintenance / doc / design); effort; blast radius;
  file:line or §. A finding against a ruling above or a D-row cites it and argues, or drops.
- `## PROBED-AND-HELD`: what you probed that held, with case counts.
- If your findings-file Write is REFUSED, SendMessage your findings to the coordinator ("crit-sae2"... the agent that
  launched you) AT ONCE marked relayed; if a harness rule refuses it, return the findings as your final text. Never route
  around a refusal.
- Finish: run `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-sae2 --deliver
  /var/tmp/pcrec-pcrec/scratch/crit-sae2/deliver-<lens>.txt <lens>` until it prints DONE. Final reply at most 150 words.
