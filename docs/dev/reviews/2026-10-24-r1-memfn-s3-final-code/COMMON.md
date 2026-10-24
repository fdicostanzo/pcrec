# COMMON brief — critic round memfn-s3-final (code mode)

Read all of this before your own lens prompt.

## 1. Scope mandate (binding; restate it to any agent you launch — you should launch none)

- Work touches ONLY the pcrec repo (/home/pcrec/projects/pcrec) and its sibling pcrec-bench. Do not create,
  modify or delete files anywhere else on this machine (no home/system config, no other repos).
- You are READ-ONLY on both repos. No edits, no commits, no `git checkout`/`stash`/`worktree` commands, no
  `make`, no suite or battery (`make test`, mech, run_*.sh harness sections, G2 runners). A heavy correctness
  job holds the box right now.
- Scratch goes ONLY under `/tmp/claude-1001/crit-memfn-s3-final/<your-lens>/` (create it). Your findings file
  goes where your lens prompt says.
- Never `cd` (a hook blocks `cd X && ...`); use absolute paths and `git -C`. A `(cd X && ...)` subshell is fine.
- Wrap any command that might hang (a generated matcher, a compile of a hostile pattern) in GNU timeout:
  `/usr/bin/gnutimeout 20 ...` (bare `timeout` on this box is uutils). Keep each batch under ~50 compiles;
  you may run single-pattern compiles, `gcc -O2 -S`/`-c` of single artifacts, `size`, small drivers and small
  python3 scripts. No timing measurements (the box is loaded; timing is the verifier's, by instruction count).

## 2. The subject (frozen)

- SUBJECT = `cc4f54eb296f035e0e5d9863c680a69721a64875` (branch lane/memfn-s3pair). BASE =
  `0d3765c87ae412f9a99dc0df1ea56250d6943a55` (git merge-base with main). Diff: `git -C
  /home/pcrec/projects/pcrec diff 0d3765c87 cc4f54eb2 -- <paths>`. Read files at SUBJECT in the review tree
  `/home/pcrec/projects/pcrec/worktrees/crit-memfn-s3-final/` (a clean detached checkout); BASE files via
  `git -C /home/pcrec/projects/pcrec show 0d3765c87:<path>`.
- What it is: the memfn kit's D172 stage S3. The window site's REPORT step is ROUTED BY DEFAULT: the `cover`
  LOCATE row (`src/gen/emit_dfa.c` `locate_cover_applies`, `src/gen/known.c` `cover_conj[]`) now admits on
  every build; where it admits, `RX_DFA_SCAN "cover"`, the artifact's search is the kit's window search (no
  automaton run to find or recover the start). The kit's window family (`memfn/src/window.c`) gained E-find
  (find-then-verify text), Table B asked through the finder's FIND slot (`memfn/src/finder.c` `fd_find`,
  rows incl. PAIR widened to ANY two-byte stop), B's renderers (`wf_brows`), Table D as a kit_table with the
  Horspool row D-hors (`wf_dtable`, deny `wf-hors`). Deny `--memfn=no-wf-find` = the OFF arm (claimed: the
  default build before S3, but for its abi digits). abi 84 -> 85. Merged with main 0d3765c87.
- Product diff (the code under review): `src/ cli/ lib/ memfn/src/ memfn/include/` (~2.9k diff lines,
  window.c +1185). Test/check diff: `tests/`, `memfn/tests/`, `scripts/emit_sweep.py`. Spec diff:
  `docs/spec/match_api.md`, `registry.md`, `tuning.md`, `facts_listing.md`.
- COMPILERS (use these, not any build/ under another worktree):
  - SUBJECT: `/tmp/claude-1001/crit-memfn-s3-final/subj/pcrec` (a copy of a clean build of SUBJECT; the review
    tree's own build `worktrees/crit-memfn-s3-final/build/pcrec` may also appear later — either is fine).
  - BASE: `/tmp/claude-1001/crit-memfn-s3-final/base/pcrec` (a copy of main's build; main's product source is
    identical to BASE's; it emits abi 84).
  - Recipe: `$PCREC -p rx --emit-main -o out.c --features all --pattern 'PAT' [flags]`, then
    `gcc -O2 -o out out.c && ./out SUBJECT_STRING` (exit 0 match / 1 no match). Without `--emit-main` you get the
    library form (`rx_search(subject, n, search_from, caps)`, `rx_match`, `rx_info`); write a small driver for
    many subjects or for `search_from > 0`. `--memfn=no-wf-find` / `--memfn=no-wf-hors` are the denies;
    `-fmemfn-simd` the SIMD layer. Assertions (`\b`, lookaround) need `--features all`.
  - Oracle: libpcre2-8 is installed (`/usr/include/pcre2.h`, link `-lpcre2-8`); python3 `re` for the base tier.

## 3. The rules you review against

- The living guide: `docs/dev/guide/README.md`, `coding.md`, `architecture.md`, `style.md`, `critics.md`,
  `addenda/kit.md` (all at SUBJECT in the review tree; they are unchanged by the subject).
- Design docs the subject cites: `docs/design/memfn/window_site.md` (rev 3.3 DRAFT at SUBJECT; rev 3.2, the
  design of record, is the BASE version), `docs/design/memfn/integration.md`, `memfn/CLAUDE.md`,
  `memfn/src/CLAUDE.md`, `docs/design/kit_proof.md` (§1.1 `cover_conj`, §7).
- Spec sections the subject changes (the contract, D80): `docs/spec/match_api.md` §3.1¶21, §6.3.4 (the
  `"cover"` scan row, ¶8, ¶9, the `"attempt-start"` row), `docs/spec/registry.md` §6 (`wf-find`, `wf-hors`,
  floor 14), `docs/spec/tuning.md` §2.43¶3d, `docs/spec/facts_listing.md` §4.1¶2.
- `docs/dev/decisions.md` D-rows are citable EXCEPT D176 (denied, below). A finding against a ruled D-row
  cites it and argues, or drops.

## 4. Denylist (do not open, grep into, or follow links to)

- `docs/dev/lanes/s3*` (incl. `s3_report.md`, `s3_job_*`), `docs/dev/lanes/s3_evidence/`, any
  `docs/dev/lanes/*s3*_report.md`; any other lane report under `docs/dev/lanes/`.
- Every review file on this subject: `docs/dev/reviews/2026-10-23-r1-memfn-s3-code*`,
  `docs/dev/reviews/2026-10-23-r2-memfn-s3-c1-code*` (and sibling dirs) — UNLESS your lens prompt says otherwise.
  window_site.md rev 3.3 names these files and finding ids (C1, R2-6, ...): read the design text, never
  the files it cites.
- `memfn/docs/journal.md`, `memfn/docs/responses.md`, `memfn/docs/wake.md`;
  `docs/design/memfn/stop_ranking_study.md`; `docs/dev/decisions.md` D176's section.
- `git log` message BODIES (subject lines are fine: `git log --format='%h %s'`); `worktrees/.boxqueue/`, every
  job log, every other worktree under `worktrees/` (only `crit-memfn-s3-final` is yours), the box queue.
- If you open a denied file by accident, say so in your file's last section and do not use what you read.

## 5. Output format

- Your findings file DOES NOT EXIST YET: you CREATE it at the path in your lens prompt, and write it
  INCREMENTALLY (append each finding as you confirm or suspect it; do not save everything for the end).
- Each finding:
  ```
  ### <LENS>-n  <one-line title>
  - status: CONFIRMED (repro: input, exact command, observed vs expected) | SUSPECTED (what would confirm it)
  - severity: answer | speed | size | maintenance | doc | design
  - effort: S | M | L      - blast radius: which artifacts/sites/callers
  - where: file:line (at SUBJECT) or doc §
  - detail: ...
  ```
  `answer` = a wrong match result or a contract the code breaks; reserve it for that.
- A finding against a ruled D-row cites the row and argues, or is dropped.
- The file ENDS with `## PROBED-AND-HELD`: what you tested that held, with case counts (e.g. "412 subjects x
  37 patterns vs libpcre2, 0 differences").
- Final reply: at most 150 words, naming your file and the count of CONFIRMED/SUSPECTED findings by severity.
