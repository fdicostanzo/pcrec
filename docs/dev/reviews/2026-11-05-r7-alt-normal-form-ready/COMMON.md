# COMMON brief — critic round crit-altnf3 (DESIGN mode, LAST RE-CHECK before a build go), 2026-11-05

Read this whole file before your per-lens prompt's question. `R` below means
`/var/tmp/pcrec-pcrec/scratch/crit-altnf3` (spell it out in commands). `W` means the review tree
`/home/pcrec/projects/pcrec/worktrees/crit-altnf3`.

## What this round is
The LAST re-check of a revised design before the owner gives a build go. Two earlier rounds reviewed
it and were ruled; rev 2 claims to apply the second ruling. You MAY read both earlier rounds,
including their RULING blocks and critic texts:
`docs/dev/reviews/2026-11-05-r2-alt-normal-form.md` + dir `docs/dev/reviews/2026-11-05-r2-alt-normal-form/`,
`docs/dev/reviews/2026-11-05-r4-alt-normal-form-recheck.md` + dir `docs/dev/reviews/2026-11-05-r4-alt-normal-form-recheck/`.
Do not assume rev 2's claims about what it fixed are true: that is what you are checking.

SCOPE OF THE ROUND (kept small by the owner's ruling of r4): stages **1, 2p and 2b** only, and rev 2's
NEW mechanisms: the re-derived adjacency test (§3.2, its three first-match rows), the ONE merge/factor
procedure (§3.3, rounds M -> P -> S, fixpoint, order), the description as one pure function called at
code-point and byte level (FIX-7, §3.5), the island reading the class's code-point set (SND-2, stage 1),
and the re-specified flag bits 10/11/44 plus the one harness-only lever (§11). Stages 2a and 3 are OUT
of scope except where the text of 1/2p/2b depends on them. Do not spend effort on 2a/3 for their own sake.

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and, READ-ONLY, pcrec-bench
  (/home/pcrec/projects/pcrec-bench). You EDIT NEITHER repo. You write only under your own
  directory `R/<your-lens>/`. No other files anywhere (no $HOME, no /tmp, no system config).
- Read-only critic: never run `make`, any test suite, `scripts/boxqueue`, `scripts/boxlock`,
  `scripts/battery.sh`, `scripts/emit_sweep.py`, or anything heavy. The box is shared tonight (a full
  mech job holds the box lock; a design lane runs concurrently; it is the owner's evening): run every
  compile and probe under `nice -n 19`. Single-pattern `build/pcrec` compiles, `gcc` of one generated
  file, the oracle probes and small C/python programs of your own are fine (keep pcrec compiles under
  ~300 total; a base/variant compare pair counts 2).
- Never `cd` in a chained command (a hook blocks it): use absolute paths, `git -C DIR`, or a
  `( cd X && ... )` subshell.
- Bound anything that may hang: `timeout 60 <cmd>` (GNU timeout on this box).
- Kill only your own processes, by PID (never `pkill -f`/`pgrep -f`).
- CLEAN-ROOM WALL (D181): nobody opens the pinned PCRE2 source copy, or any PCRE2 source anywhere.
  PCRE2 facts come from public docs (`man pcre2pattern`, `man pcre2api`, `man pcre2callout`) and from
  the INSTALLED libpcre2-8 10.46 used as a library. A question only PCRE2's CODE can answer: write it
  under a heading "Questions for a pcre2-reader"; do not answer it.

## Subject (frozen)
- Design: `docs/design/alt_normal_form.md` REV 2 (PROPOSED) at commit
  `129b61a678b53b3881823d9615d6fc9dedcaf759` (byte-identical on main merge `08eef8b4b`). Frozen copy:
  `R/subject_alt_normal_form.md` — READ THIS COPY; cite its § numbers and line numbers.
- A build would land on main HEAD. The review tree `W` is built at main `08eef8b4b` (`W/build/pcrec`,
  `W/build/libpcrec.a`, `W/build/pcrec-harness` if built). Main has since moved to `4a0fcc859`, but
  NOTHING under src/, lib/, cli/, tests/, docs/spec/, decisions.md or plan.md differs (only
  `docs/design/vlookbehind.md` moved, to its rev 2). Read every piece of code the design cites IN `W`
  (never the live main tree). Cited code (file:line, function, field, comment, stamp, flag bit) that
  does not say what the design says is a finding.
- The design's build ORDER says every stage builds after "span_pick unit 1e" lands (§4.7). Whether 1e
  has landed on main at the freeze is a fact for you to establish (grep `git log --oneline` SUBJECT
  LINES only, and the memfn docs), not to assume.
- Client design docs (in force at the freeze; read at the commit named):
  `docs/design/vlookbehind.md` — the subject cites [VLOOKBEHIND] as "rev 1 in flight"; rev 1 was in
  force at `08eef8b4b`, and rev 2 merged at `4a0fcc859` before this round started. Read rev 2
  (`git -C /home/pcrec/projects/pcrec show 4a0fcc859:docs/design/vlookbehind.md`) and say whether
  anything in it changes what stage 2b's lookbehind text (SND-5, §3.3 "Reach") relies on.
  Others: `docs/design/stream/{manifesto,roadmap}.md`, `docs/design/cls_tree_design.md` ([CLS-TREE]
  S3), `docs/design/memfn/row_contracts.md`, `docs/design/CLAUDE.md` (standing questions).
- Rulings files: read `docs/dev/decisions.md` and `docs/dev/plan.md` ONLY as
  `git -C /home/pcrec/projects/pcrec show 08eef8b4b:docs/dev/decisions.md` (same for plan.md, and for
  any other doc you want at the freeze). Find a plan row by `grep -n '^- \[TAG\]'` on that output and
  read that row and its own indented continuation lines only.

## Owner rulings in force at the freeze (Frank, 2026-11-05)
- O1-O5 as listed in the subject §0.2 (superset sets in facts only; stage 1 = UTF-8 lowering alone with
  predicted movers; set positions ride with [POS-ONE-DETECTOR]/D187; per-length pieces now, ci-moskva
  the witness; the wider general form named, siblings staged later).
- The r2 and r4 rounds' dispositions as written in their RULING blocks.
- OPEN, NOT RULED (do not treat either answer as decided): stage 3's covering cube — (A) a named lossy
  covering-cube shape (a D187 addendum) vs (B) cube-only readers decline non-cube positions (subject
  §13 q5). It is stage 3's; flag it only where the text of 1/2p/2b depends on the answer.
- Standing project rules that bear here: general mechanisms, not special cases; no parallel mechanisms;
  build only under a measured need (D77); in-flight refactors outrank optimizations (D153); selections
  are declared first-match tables, never if-chains; compatible with PCRE2 unless it is a PCRE2 bug (D26
  + addendum); a PUBLIC deny flag only for a change that can be SLOWER, a wrongness-risk change gets a
  test-only lever, a refactor/bug fix none ("flag follows caller effect", 2026-10-29); a contract change
  carries its spec hunk in the same change (D80); emitted-byte changes are an abi event with every
  reader of the number found by grep (D76/D94); every D186 stage declares its kind per regime.

## Guide and cited documents (read at the freeze commit or in W)
- Guide: `docs/dev/guide/{architecture,coding,style,critics}.md`, `docs/dev/learnings.md` §3.
- Spec: `docs/spec/match_api.md` §6 (¶17-19), §6.3.11, §11.6; `docs/spec/tuning.md` §2 (¶4 axes table),
  §2.6, §2.7, §2.20, §2.27, §2.28, §2.39; `docs/spec/facts_listing.md` §1, §4.1.2.
- D-rows (frozen decisions.md): D26, D76, D77, D80, D94, D153, D157, D174, D181, D186, D187, and the
  2026-10-29 "flag follows caller effect" ruling (grep for it).
- Code the design cites (in W; grep to locate, the design's line numbers may have drifted — that is a
  finding): `src/opt/altcls.c` (`altcls_walk_alt`, `altcls_branch_peel`, `altcls_extend_prefix`,
  `altcls_factor_run`, the A_LOOK leaf handling), `src/opt/lower_enc.c` (`lower_class_utf8`, `u8_box`,
  `u8_ranges`, the seal), `src/facts/req.c` (`rr_alt`, `rn_common_head/tail`, `rn_hull_mask`,
  `rb_class_into`, `rb_walk_at` `case A_EMPTY`, `rr_cat`), `src/facts/kindrow.def`,
  `src/gen/emit_vm.c` (`vm_isl_words`, `vm_isl_single`, `vm_isl_build`, `vm_det_seq`,
  `vm_cursor_fits`), `src/core/cpset.c` (`pcrec_wcls_set` or wherever it lives, `pcrec_cube_of`,
  `pcrec_cls_cube`), `src/core/compile.c` (pass order), `src/core/axes.def`, `src/core/limits.def`,
  `lib/pcrec.h` (`PCREC_BIT`, `PCREC_NO_ALTCLS_MERGE`, `PCREC_NO_ALTCLS_FACTOR`, the bit-44 name),
  `cli/CLAUDE.md` (harness lever rules), `tests/axes/run_axes.sh`, `tests/codegen/run_facts_checks.sh`,
  `src/facts/facts.def`, the stamp emitters (`RX_ALTCLS_MERGES`, `RX_ALTCLS_FACTORED`), the mech rows
  the stages name (`S66`, `S67`, `S268`, `S302`, `S303`, `S366`, `S-U7`, `S-U8`; find them by name).

## Evidence population (copies, read-only; count from these, not from the prose)
- `R/population/altrev2_evidence/` (rev 2: `probe.py`, `snd1.tsv/.out`, `altnf_proc.py/.out`,
  `sh.tsv/.out`, `stamps.out`, `se2.*`, `p7_altcls.out`, its CLAUDE.md) and
  `R/population/altrev1_evidence/` (rev 1: `cmp.py`, `premise.*`, `c4*`, `wit.*`).
- These dirs are READ-ONLY. To re-run a script, copy it AND its case file into your own dir first:
  `cmp.py` writes a `bin/` beside its CASES file; `probe.py PCREC CASES.tsv [SCRATCH]` writes into
  SCRATCH (pass `R/<lens>/bin`). Run python with `-I`.

## Tools (checked spellings, one compile each, 2026-11-05)
- pcrec facts: `nice -n 19 W/build/pcrec -e utf8 --emit-facts --pattern '(?i)abcdÀefgh'` -> rows
  `utf8 req_whole_run ... c38045464748/ffdfdfdfdfdf`, `req_run`, `req_run_maxoff`.
- pcrec C + stamps: `nice -n 19 W/build/pcrec --features all -e utf8 --engine=vm -fno-cls-kit -p rx -o R/<lens>/x.c --pattern 'x(?:[éà]1|q2|r3)y'`
  -> the STAMPS are `#define`s in `x.c` (not x.h): `RX_VM_ALT_ISLANDS 1`, `RX_VM_RUNGS 0x0u`,
  `RX_ALTCLS_MERGES`, `RX_ALTCLS_FACTORED`.
- pcrec match: `nice -n 19 W/build/pcrec --features all -p rx --emit-main -o R/<lens>/z.c --pattern '(?:ab|a\Kd|ad)'`,
  `gcc -O1 -o R/<lens>/z R/<lens>/z.c`, `R/<lens>/z ad` -> `match 1 2` (start end; captures need
  `probe.py`'s counting driver).
- VM listing: `W/build/pcrec --features all --emit-ir --pattern P` (add `-e utf8`, `-fno-cls-kit`).
- Oracle: `probe.py` (libpcre2-8 10.46 by ctypes: span, every capture, callout count, mark) — its
  header documents the CASES format; or your own small C program linked `-lpcre2-8`.

## DENYLIST (PATHS EXCLUDED from every read, git diff, git log -p and grep)
- `docs/dev/lanes/altrev2_report.md`, `docs/dev/lanes/altrev2_rulings.md`,
  `docs/dev/lanes/altrev1_report.md`, `docs/dev/lanes/altrev1_rulings.md`,
  `docs/dev/lanes/altdesign_report.md`, `docs/dev/lanes/altdesign_rulings.md`, and any other
  `docs/dev/lanes/altrev2*`, `altrev1*`, `altdesign*` file EXCEPT the `*_evidence/` directories
  (use the copies under `R/population/`). (`altthink_report.md` and `rpsurvey_report.md`, which the
  subject cites as inputs, ARE allowed.)
- `docs/dev/wake.md`, `docs/dev/owner.md`, `docs/dev/dev_journal.md` (do not read it at all)
- `git log` bodies beyond subject lines; job logs; the box queue; any worktree under `worktrees/`
  except `worktrees/crit-altnf3`; other rounds' scratch dirs under `/var/tmp/pcrec-pcrec/scratch/`
  (committed review texts under `docs/dev/reviews/` ARE allowed)
- `R/.coord/` and every other critic's directory under R
For git commands add pathspec exclusions, e.g.
`git -C /home/pcrec/projects/pcrec grep -n PATTERN 08eef8b4b -- . ':!docs/dev/lanes/altrev2_report.md' ':!docs/dev/lanes/altrev2_rulings.md' ':!docs/dev/lanes/altrev1_report.md' ':!docs/dev/lanes/altrev1_rulings.md' ':!docs/dev/lanes/altdesign_report.md' ':!docs/dev/lanes/altdesign_rulings.md' ':!docs/dev/wake.md' ':!docs/dev/owner.md' ':!docs/dev/dev_journal.md'`.
For PLAIN grep -r (e.g. in W) add `--exclude=altrev2_report.md --exclude=altrev2_rulings.md --exclude=altrev1_report.md --exclude=altrev1_rulings.md --exclude=altdesign_report.md --exclude=altdesign_rulings.md --exclude=wake.md --exclude=owner.md --exclude=dev_journal.md --exclude-dir=.coord`.

## Output format
- Your findings file `R/<lens>/findings.md` DOES NOT EXIST YET: create it at once and write it
  INCREMENTALLY (one finding at a time, as you go).
- Sections (exact `##` headings): `## Findings`, `## PROBED-AND-HELD`, optionally
  `## Questions for a pcre2-reader` (the readiness lens adds `## Per-unit verdicts`).
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command or hand-execution trace,
  observed vs expected) or SUSPECTED (what would confirm it); severity (answer / speed / size /
  maintenance / doc / design); effort; blast radius; which build unit (1 / 2p / 2b / cross); the design
  § and line in the frozen copy (and file:line in W where code is cited). A finding against a ruled
  D-row or an owner ruling cites it and argues, or is dropped.
- PROBED-AND-HELD: what you checked that held, with case counts.
- If a harness rule REFUSES your findings-file Write, do not route around it: return the findings as
  your final text instead.
- Your DELIVER file `R/<lens>/DELIVER` exists (the coordinator wrote it). When done run
  `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-altnf3 --deliver /var/tmp/pcrec-pcrec/scratch/crit-altnf3/<lens>/DELIVER crit-<lens>`
  and fix what it reports until it prints `lanecheck: DONE rc=0`. Then END.
- Final reply at most 150 words.
