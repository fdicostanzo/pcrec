# COMMON brief — critic round dpcompact (CODE mode), review r97, 2026-11-24

You are a read-only CRITIC in an adversarial code review of pcrec (a PCRE-to-C
ahead-of-time regex compiler). Read this whole file first, then your own lens brief.

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and pcrec-bench (read-only).
  Do not create, modify or delete files anywhere else on this machine.
- You are READ-ONLY on both repos. Never edit, commit, stash or checkout anything.
  Never run `make`, `make test`, or any suite runner (run_*_tests.sh, run_sabotage_matrix.sh, battery).
  You MAY run: the built binaries below, `gcc` on single files (including linking a small C
  probe against a tree's `build/libpcrec.a`), `python3 -I` scripts, `git show/diff/grep`,
  and `tests/core/ucd_wall_check.sh ROOT WORKDIR` (a read-only scan) with WORKDIR under YOUR dir.
- Scratch ONLY under your own dir `/var/tmp/pcrec-pcrec/scratch/crit-dpcompact/<lens>/`
  (never /tmp). Set `PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-dpcompact/<lens>` for anything you run.
- Bound uncertain commands: `timeout 120 ...` (GNU timeout is bare `timeout` on this box).
- Pass patterns in SINGLE QUOTES or via a file; check the `Pattern:` header comment of any
  emitted file before citing a byte-identity or route claim (shell quoting eats `\b`, `\p`).

## Subject
- Branch `lane/dpcompact`, SUBJECT = 24126f78cb6511f275088b2f8593f8277296ded5,
  BASE = merge-base with main = 2fdbcad3897c235efe41e147b9835e0698c560a0.
  The diff: `git -C /home/pcrec/projects/pcrec diff BASE SUBJECT -- . ':!docs/dev/lanes/dpcompact_*' ':!docs/dev/dev_journal.md'`
- What it does: replaces the Unicode property table `src/parse/uprops_tables.inc`
  (C arrays of interval pairs + a name/row struct array, read directly in mod_uprops.c, and via
  pcrec_uprops_span by mod_code.c, mod_named_groups.c, mod_ucp.c, pcre2_check.c, and regex-parsed by
  Python tools) with `src/parse/ucd_tables.inc` (delta-LEB128-varint interval blob + a name blob +
  parallel row arrays), written by `third_party/ucd-16.0.0/generate.py`, and decoded by ONE new module
  `src/parse/ucd_tables.{h,c}` (interface: pcrec_ucd_find, pcrec_ucd_contains, pcrec_ucd_row_*,
  pcrec_ucd_unicode_version). Python tools now read a TSV written by `tests/uprops/ucd_dump.c` through
  the interface. A text-scan "wall" check `tests/core/ucd_wall_check.sh` (run by
  tests/core/run_core_tests.sh) and mech sabotage rows S3575..S3579 police that no other file names the
  generated file or its private symbols; S-U12, S1389, S1583 were re-anchored.
- THE PROMISES under review:
  1. The owner's constraint, verbatim (2026-11-24): "data-plan-compact: yes. Have it be modular so the
     format is only understood to the module which provides an interface".
  2. The charter, docs/design/data_plan.md §4 row "A1-compact" (read it at SUBJECT:
     `git show SUBJECT:docs/design/data_plan.md`): "Byte-identical artifacts (the compiler's output
     does not change)". The row also quotes measured sizes and "compile time unchanged".
- Freeze: main was 4d26eef02 at freeze; rulings files (docs/dev/decisions.md, docs/dev/plan.md) read
  via `git show SUBJECT:path` (or main's 4d26eef02), never the live tree.

## Guide and context to read (at SUBJECT)
- docs/dev/guide/coding.md, docs/dev/guide/architecture.md, docs/dev/guide/style.md (house rules).
- docs/design/data_plan.md (the charter; §4 A1-compact row; A1..A4 goals near "Priority: A1 > A4").
- src/parse/ucd_tables.h, src/parse/ucd_tables.c (the module; its header comment IS the format spec).
- third_party/ucd-16.0.0/generate.py (the writer), third_party/ucd-16.0.0/PROVENANCE.md.
- docs/dev/learnings.md §3 (check design) for check lenses.

## Built trees and the run kit (do NOT rebuild; do not run make)
- SUBJECT review tree (built): /home/pcrec/projects/pcrec/worktrees/crit-dpcompact (build/pcrec, build/libpcrec.a, build/pcrec-harness)
- BASE tree (built, git archive of BASE): /var/tmp/pcrec-pcrec/scratch/crit-dpcompact/base
- Plant trees (built; only the check-adequacy lens uses them): /var/tmp/pcrec-pcrec/scratch/crit-dpcompact/plants/{S-U12,S1389}/tree
  (S1583's edit is identical to S1389's.) Plant applier: kit/apply_plant.sh ROWFILE TREE (exact SAB_COUNT).
- kit/pc.sh TREE ARGS... — runs build/pcrec of TREE = base | subject | plant:S-U12 | plant:S1389.
- kit/cmp.sh OUTDIR PATTERNFILE [pcrec flags] — compiles each line on BASE and SUBJECT under the SAME
  basename into OUTDIR/base and OUTDIR/subject, prints SAME/DIFF per pattern (C + rc + stderr). Each line = 2 compiles.
  Working regime spelling (checked): `--features unicode-props -e utf8` (also `-e byte`; add `,named-groups`, `ucp` etc. as needed).
- kit/ucd_dump_subject — tests/uprops/ucd_dump.c built against the SUBJECT library; kit/sets_subject.tsv its output.
- kit/base_sets.py BASE_INC — prints BASE's uprops_tables.inc rows in the same TSV shape; kit/sets_base.tsv its output.
- Oracle for this subject: BASE is the reference (the promise is "unchanged"). libpcre2 is not needed.
- Kit path: /var/tmp/pcrec-pcrec/scratch/crit-dpcompact/kit/

## Budget
TOTAL cap: 2,000 compiles per critic (a cmp.sh line = 2). State any matrix as a product inside it.

## Denylist (D27 applied to review) — never read
- docs/dev/lanes/dpcompact_* (the lane's report), and the dpcompact entries of docs/dev/dev_journal.md
  (do not read dev_journal.md at all). Exclude from EVERY git diff/grep:
  `':!docs/dev/lanes/dpcompact_*' ':!docs/dev/dev_journal.md'`; for plain grep use
  `--exclude=dev_journal.md --exclude='dpcompact_*'`.
- `git log` bodies beyond subject lines; job logs; the box queue; other worktrees under worktrees/
  (except crit-dpcompact); the round dir's `.coord/` and other critics' subdirectories.
- Any review file about this subject (none exists yet).

## Output format
- Your findings file is pre-created (path in your lens brief). APPEND to it (Edit or a shell `>>`
  append); NEVER overwrite it with Write (the harness refuses a subagent's whole-file Write).
- Append each finding THE MOMENT you have it, one append per finding.
- Each finding: id `<LENS>-n`; CONFIRMED (repro: input, command, observed vs expected) or SUSPECTED
  (what would confirm it); severity (answer / speed / size / maintenance / doc / design); effort; blast
  radius; file:line or §. A finding against a ruled D-row cites it and argues, or drops.
- State the minimum/maximum witness sizes your probes reached (a 0-finding sweep below the witness's size is not evidence).
- End the file with `## PROBED-AND-HELD` (what you probed that held, with case counts), then a line `CRITIC COMPLETE`.
- Then run `scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-dpcompact --deliver <your deliver file> <lens>`
  from /home/pcrec/projects/pcrec; it PASSES only on "lanecheck: DONE rc=0" ("DONE rc=1" is a failure: fix and re-run).
- Final reply at most 150 words. A failed final reply is EXPECTED for a nested agent and needs no escalation:
  the findings file with its CRITIC COMPLETE line is the delivery.
