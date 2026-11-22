# COMMON brief: code critic round r78, topic memfn-bsu4

Read this whole file first. Then read your own one-question brief (it names your lens and your files).

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and its sibling pcrec-bench, and ONLY READ them. You are a READ-ONLY critic: no edits to either repo, no commits, no `git checkout`/`stash`/`worktree` commands.
- Write files ONLY under your own subdirectory `/var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu4/<lens>/` and append to your own findings file (named in your brief). Set `TMPDIR` to your own subdirectory for every command you run. Never write to /tmp.
- NEVER run `make`, `make test`, any `test-*` target, `tests/mech/run_sabotage_matrix.sh`, `tests/axes/run_axes.sh`, `scripts/battery.sh`, `scripts/boxlock`, `scripts/boxqueue`, or anything that takes the box lock. The box is running this work's validation jobs right now. You MAY run, under `nice` and bounded by `timeout 600`: `build/pcrec` / `build/pcrec-harness` compiles of single patterns, `gcc` on emitted C, and the subject's OWN individual check scripts directly (`python3 -I .../span_pins.py`, `python3 -I .../g2_vspan.py`, `python3 -I .../routing_shape.py`, `python3 -I .../simd_floor_check.py --every N`), one at a time, never more than one in parallel. `tests/memfn/run_simd_floor.sh` runs `make` inside it: do NOT run that script; call `simd_floor_check.py` directly with the prebuilt binaries below.
- Kill only processes you started, by PID. Never `pkill -f`.
- Pass patterns in single quotes or via a file; check the `Pattern:` header of every emitted file you cite before reporting a byte or route claim.

## The subject (frozen)
- SUBJECT = `023ab6eb897a20cff764ebde9d2d8c469e828647` (branch lane/bsu4: the merge of lane/bsu4g and lane/bsu4p).
- BASE = `ad3c8f1c23021a20ef7a1233f14f46286585cd48` (the kit-branch commit both halves were cut from; NOT main).
- Freeze points: main `92f5e77b6`, kit branch lane/memfn-k1108 `d9d53d77f`; main's decisions.md last touched at `bc22e155a`, plan.md at `0ec0a8f35`. Read rulings with `git -C /home/pcrec/projects/pcrec show <commit>:docs/dev/decisions.md`, never the live tree.
- What it is: unit U4 of the kit's request R-47, the block span at the SIMD layer. A CHECKS-ONLY unit: G2-V unit and whole with guard pages, the 20 T-table pin cells, SPAN-SEED's per-check wiring, the rest of the C18 amendment (NAMED span witnesses x86-64-v3 only, FLOORS re-pin, controls (2)-(4)), the routing leg, floors and re-pins, and sabotage rows S3525, S3526, S3530..S3536.
- Claims the round tests: (1) U4 moves no emitted byte; (2) it edits nothing under memfn/src/, src/, cli/, lib/; (3) every new check can fail; (4) every check's control shares no source with the kit's generator (memfn/src/, chiefly memfn/src/window.c); (5) every plant has a witness that reaches its site.
- Already established by the coordinator (do NOT redo; attack only if you have a reason): claim (2) by `git diff --name-only BASE SUBJECT` (0 paths under those dirs); claim (1) partly: BASE and SUBJECT compilers emit byte-identical C on all 41 SPAN-SEED patterns x {default, x86-64-v3} x {width 32, 4095} (164 pairs, 0 diffs); `scripts/m6read_check_sab_anchors.py` on the review tree: 1384 rows, all anchors resolve.
- The design of record: `docs/design/memfn/block_span.md` at SUBJECT. Read §10 (10.1 SPAN-SEED and its wiring table; 10.2 the checks table, the 20 pin cells, the C18 amendment, the sabotage table (a)-(f), re-aims) and §14's U4 row. §16 (TODAY NUMBERS) items 5, 10, 11, 13 hold the drills it cites. Quote the design's sentence with its § when you hold the subject to it; never paraphrase.
- Changed files (the diff, excluding denied paths):
  `git -C /home/pcrec/projects/pcrec diff ad3c8f1c2 023ab6eb8 -- . ':!docs/dev/lanes' ':!memfn/docs/journal.md' ':!memfn/docs/responses.md' ':!memfn/docs/wake.md'`
  New: memfn/tests/g2_vspan.py, memfn/tests/g2/g2_vspan_drv.c, g2_vspan_gen.c, g2_vwhole_drv.c, tests/memfn/span_pins.py, nine tests/mech/sabotages/S35xx_*.sh. Changed: memfn/tests/run_g2_win.sh (section V, `--v`), tests/mech/run_sabotage_matrix.sh (arm `g2v`), tests/memfn/simd_floor_check.py, run_simd_floor.sh, routing_shape.py, run_libc_census.sh, c4_allowlist.tsv, CLAUDE.md/NOTES.md files.

## The review tree and binaries (prebuilt; never rebuild)
- Review tree (SUBJECT, built): `W=/home/pcrec/projects/pcrec/worktrees/crit-memfn-bsu4` (build/pcrec, build/pcrec-harness, build/libpcrec.a). Read subject files THERE, or with `git -C /home/pcrec/projects/pcrec show 023ab6eb8:PATH`.
- BASE tree (built clean): `/var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu4/base`.
- Planted trees, one per new row, built from the SUBJECT with the row's SAB_BEFORE->SAB_AFTER applied (exact SAB_COUNT), build/pcrec and build/pcrec-harness and build/libpcrec.a rebuilt: `/var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu4/plants/<SNNNN>/tree` for S3525 S3526 S3530 S3531 S3532 S3533 S3534 S3535 S3536.
- Traced compilers (the kit's memfn/src swapped for its -DMF_TRACE copy, harness build; what `--trace` of span_pins.py / simd_floor_check.py wants): `/var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu4/trace/<subject|SNNNN>/pcrec-trace`.
- Run kit, `K=/var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu4/kit`:
  - `$K/tree.sh TREE [pcrec|harness|root] ARGS...` with TREE = `base` | `subject` | `plant:SNNNN`: runs that tree's binary (`root` prints the tree path).
  - `$K/run1.sh TREE LAYER PATTERNFILE SUBJECT OUTDIR [pcrec flags]`: LAYER `scalar` or `v3`; compiles the pattern (read from a FILE, no quoting issues) with `--emit-main` as OUTDIR/m.c (fixed basename), builds with gcc (-march=x86-64-v3 at v3), prints the matcher's first match, then `ORACLE <first span>` from libpcre2.
  - `$K/pcre2_oracle PATTERNFILE SUBJECTFILE`: libpcre2 find-all spans, byte mode.
- Measured costs on this box (subject tree): `span_pins.py` alone ~1 s, 65 checks; `g2_vspan.py both` ~31 s, 2830 checks. Examples:
  `TMPDIR=$MY nice python3 -I $W/tests/memfn/span_pins.py --pcrec $T/build/pcrec --harness $T/build/pcrec-harness --trace $TR/pcrec-trace --tree $T`
  `CC=gcc TMPDIR=$MY nice timeout 600 python3 -I $T/memfn/tests/g2_vspan.py both --root $T --lib $T/build/libpcrec.a --work $MY/w`
  (T = a tree root from `$K/tree.sh TREE root`; run each script FROM the tree it belongs to, `$T/...`, so a plant runs its own copy.)
- Plant assignment: lens PLANTSA owns S3530 S3531 S3532 S3533; lens PLANTSB owns S3525 S3526 S3534 S3535 S3536. No other lens runs a planted tree; other lenses may read the row files.

## Denylist (do not open, grep, diff or list; exclude from every git diff and plain grep)
- `docs/dev/lanes/bsu4g*`, `docs/dev/lanes/bsu4p*`, `docs/dev/lanes/bsu3*` (git pathspec `':!docs/dev/lanes'` covers them; plain grep: `--exclude-dir=lanes`).
- Every file under `docs/dev/reviews/` whose name contains `memfn-bsu` or `memfn-bspan` (plain grep: `--exclude='*memfn-bsu*' --exclude='*memfn-bspan*'`).
- `memfn/docs/journal.md`, `memfn/docs/responses.md`, `memfn/docs/wake.md` (plain grep: `--exclude=journal.md --exclude=responses.md --exclude=wake.md`).
- The worktrees `worktrees/bsu4g`, `bsu4p`, `bsu4`, `bsu3fix`, `memfn` (read the subject only via the review tree above or `git show`), and every other worktree except `worktrees/crit-memfn-bsu4`.
- `$PCREC_TMPDIR/scratch/bsu4g/`, `bsu4p/`, `bsu3fix2/`, and the round's own `.coord/` directory.
- `git log` bodies beyond subject lines; job logs; the box queue (`scripts/boxqueue`, queue logs); `SAB_DOC_FIGURE` pointers into the lane reports.
- The sabotage rows' comment headers quote the lane's claims ("Caught by ..."): a CLAIM to test, not evidence.

## Guide
Rules for checks: `docs/dev/learnings.md` §3 and the memory note on check design (controls that share a source with what they control; populations nobody counts, K35; witnesses that stop reaching their site, [MECH-REACH]). House rules: `docs/dev/guide/coding.md`, `style.md`. Mech row format: `tests/mech/CLAUDE.md`.

## Output format
- Your findings file (named in your brief) EXISTS already, pre-created with headings. APPEND to it (Edit, or a shell `>>` append). NEVER overwrite it with Write: the harness refuses a subagent's whole-file Write and the file stays empty. If an append is refused, SendMessage your findings to the coordinator at once, marked relayed.
- Append each finding the MOMENT you have it, one append per finding, under `## Findings`.
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, exact command, observed vs expected) or SUSPECTED (what would confirm it); severity (answer / speed / size / maintenance / doc / design); effort; blast radius; file:line or §. A finding against a ruled D-row or a design ruling (R-n, R71-n) cites it and argues, or drops.
- For every plant or mutation: say whether it was SAME (rc 0, bytes equal), SILENT-MOVE (rc 0, bytes differ) or LOUD (rc != 0); delete old outputs before each compare.
- State the MINIMUM witness length / population your probes reached: a 0/0/0 below a witness's length is not evidence.
- End with `## PROBED-AND-HELD` (what you tested that held, with case counts), then a final line `CRITIC COMPLETE`.
- Then run `scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu4 --deliver /var/tmp/pcrec-pcrec/scratch/crit-memfn-bsu4/<lens>.deliver <lens>` (from /home/pcrec/projects/pcrec, `bash -c` with absolute paths) and end only when it prints DONE.
- Your final reply: at most 150 words. A nested agent's final reply often fails to arrive; that is EXPECTED and needs no escalation to the manager: the `CRITIC COMPLETE` line in your file is the delivery.
- Standing questions (only the lens your brief names answers them): sibling of a family; general form + unlocks (with triggers).
