# COMMON brief: critic round vmcons (design re-review), 2026-10-29

You are a READ-ONLY critic in an adversarial review of a DESIGN document before a build go.
Read this whole file first, then your per-lens prompt.

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec), and READ pcrec-bench if you need to.
- Write ONLY under your scratch dir /var/tmp/pcrec-pcrec/scratch/crit-vmcons/<lens>/ (never /tmp, $HOME,
  any other repo or directory). No edits, commits, branches or worktrees in either repo.
- NEVER run `make` or any suite (tests/harness/run.sh, battery, mech, axes). Single-pattern probes only:
  run the built compiler, gcc on emitted C, small drivers you write in your scratch dir.
- Never `cd` in a compound command (a hook blocks it): use absolute paths, `git -C`, or a `( cd X && ... )` subshell.
- Bound every run: generated matchers and drivers run under
  `/home/pcrec/projects/pcrec/scripts/watchdog -s 20 -m 1g -S <label> -- <cmd>`; any other uncertain
  command under `timeout 60`. Kill only your own processes, by PID (`scripts/safekill PID`), never pkill -f.
- Bench TIMING window 19:30-00:00: NO compiles or probe batches from 19:00. If you are not finished by 18:45,
  stop probing, write up what you have (SUSPECTED where unconfirmed) and finish.
- Keep probes light (the box is shared): one gcc at a time, -O1/-O2, no -j batches over ~20 compiles.

## Subject (frozen)
- The design: docs/dev/lanes/vmcons_report.md at commit bf9a5bb8dbca44b5588dc9ee2bf1faeada44cdd0.
  READ IT ONLY FROM THE SNAPSHOT: /var/tmp/pcrec-pcrec/scratch/crit-vmcons/subject_vmcons_report.md
  (identical to that commit). It consolidates three earlier designs (it names them TG, VB, AD) into one
  build: Stage -1 (event-stream extension), R (cursor locals), C-move/C (per-site call restore + narrowing),
  D (first-byte choice-point dispatch, stage 1), slot-flow verdicts (DEAD, COPY, UNTRAIL) in ordered rounds,
  a three-walk pipeline, and a claim of ANSWER IDENTITY BY PROOF (G1).
- It cites "[r3 Fn]" findings of a previous review round. You may NOT read that review; treat each citation
  as the design's own claim and judge the design's text on its merits.

## Base code (what the build would be written against)
- Branch lane/trailgc (D183, trail compaction at checkpoints), frozen at 06aa5ab879413169e71e169701159e6c3c22a8b8
  (the design's probes used 75ac19837; src/cli/lib are identical between the two).
- A BUILT review tree: /home/pcrec/projects/pcrec/worktrees/crit-vmcons (detached at that commit).
  Binaries: build/pcrec, build/pcrec-harness, build/libpcrec.a. Read its source freely
  (src/gen/emit_vm.c and friends are the emitter; src/core/internal.h; cli/main.c). Do not modify it.
- Useful compiler commands (B=/home/pcrec/projects/pcrec/worktrees/crit-vmcons/build/pcrec):
  - `$B -p rx -o OUT.c --pattern 'PAT'` (add `--engine=vm` to force the VM route; `-fno-splice-calls` for
    linked calls; `--no-captures`; `-e utf8`; `--allow-code=c` for embedded-code callouts);
  - `$B -p rx --emit-ir --pattern 'PAT'` prints the VM program listing (the event stream the design analyses);
  - `--emit-main` appends a main() that prints only the overall match span; for CAPTURES write your own small
    driver against the artifact's API (docs/spec/match_api.md; the .rxt harness drivers under tests/harness/
    show the shape).
- Oracle: libpcre2-8 is installed (/usr/include/pcre2.h, -lpcre2-8); write a tiny C driver to get libpcre2's
  answer (rc + every capture span). python3 `re` for the base tier where it applies.

## Reading list
- The guide: docs/dev/guide/critics.md (especially "Lessons from review rounds", round 2026-10-29 r3),
  docs/dev/guide/architecture.md.
- Spec sections the design cites: docs/spec/ir_listing.md, docs/spec/limits.md (§1, §4-§8),
  docs/spec/match_api.md (§6.3.8, §10, §11.3), docs/spec/pattern_language.md §9, docs/spec/tuning.md.
- Design docs the subject builds on, if you need them: docs/design/engine_m4.md (S10 and the VM),
  and any docs/design/ note it names. docs/dev/decisions.md rows it cites (D106, D183, D46, D148, D174).
- Base code at the review tree, as above. `git -C /home/pcrec/projects/pcrec show lane/trailgc:PATH` is the same code.

## DENYLIST (do not open, grep, list or cat; D27 blinding)
- docs/dev/lanes/vmcons_evidence/ and EVERY other file under docs/dev/lanes/ (including trailgen_*, vmbc_*,
  altd_*, vmcons_rulings.md, *_evidence/, *_deliver.txt) — the snapshot above is your only copy of the subject.
- docs/dev/reviews/2026-10-29-r3-vmtrail* (the previous round) and any other review of this subject.
- docs/dev/optloop/primed_2026-10-29.md.
- worktrees/ other than worktrees/crit-vmcons; /var/tmp/pcrec-pcrec/scratch/ other than your own dir and
  the crit-vmcons files named here (in particular NOT scratch/vmcons/, scratch/trailgc*/, scratch/altd/ etc.).
- git log BODIES (subject lines are fine), job logs, the box queue (scripts/boxqueue, worktrees/.mgr).
- The design's prototypes (vmopt_tg.py, altd.py, variants.py, ccwrap.sh, witness.sh) live in denied
  evidence dirs: do NOT fetch them. Apply the rules BY HAND (or with your own small script) to real emitted C.
If you open a denied file by accident, say so in your findings file.

## Method for "apply the rule as written"
1. Emit the base C (and the --emit-ir listing) for a crafted witness.
2. Apply the design's rule, AS WRITTEN in the snapshot, to that program: decide each verdict / dispatch from
   the table rows and round order exactly as stated (not as you think the author meant), and hand-edit a
   copy of the emitted C into the "rule-as-written twin" (delete the write, turn _SET into a plain store,
   insert the dispatch switch, move the restore, localise the cursor, etc.).
3. Compile base and twin, run both on chosen subjects, compare rc and EVERY capture span; check libpcre2.
4. A changed answer where stock answered = an answer-level finding (G1 is "identical to stock wherever stock
   answers"). Where the rule is ambiguous, say which reading you applied and whether another reading is safe.
Tag every finding DOC (one stage/rule on its own) or SEAM (where two stages, passes, walks or documents compose).

## Output format
- Your findings file does NOT exist yet: CREATE it at the path in your prompt and write it INCREMENTALLY
  (append each finding as you confirm it; do not hold everything to the end).
- Sections, as markdown `##` headings: `## Findings`, then `## PROBED-AND-HELD`, then `## STATE AT HANDOFF`.
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: pattern, flags, subject, exact commands, the edit you
  made to the twin, observed vs expected, libpcre2's answer) or SUSPECTED (what would confirm it);
  severity (answer / speed / size / maintenance / doc / design); DOC or SEAM; effort; blast radius;
  the design's § or table row (and base file:line where relevant). A finding against a ruled D-row or a
  stated ruling (the design marks R1 as ruled) cites it and argues, or drops.
- PROBED-AND-HELD: what you tried that held, with case counts (patterns x subjects).
- STATE AT HANDOFF: `STATE: complete` (or `STATE: stopped` with why), and `OWED: none`.
- Keep your scratch artifacts (C files, drivers, twin diffs) in your dir; cite them by path.

## Finishing
- Your DELIVER file is already written beside your findings file (see your prompt).
- When your file is complete, run:
  `/home/pcrec/projects/pcrec/scripts/lanecheck --deliver <your DELIVER file> --dir /var/tmp/pcrec-pcrec/scratch/crit-vmcons <NAME>`
  Fix every issue it prints and re-run until it prints `lanecheck: DONE rc=0`. Then END.
- Final reply: at most 150 words (it may be lost; the FILE is what counts).
