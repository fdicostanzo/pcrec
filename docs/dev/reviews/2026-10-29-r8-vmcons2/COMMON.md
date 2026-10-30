# COMMON brief: critic round vmcons2 (design SHORT re-check), 2026-10-29

You are a READ-ONLY critic in an adversarial review of a DESIGN document before a build go.
Read this whole file first, then your per-lens prompt.

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec), and READ pcrec-bench only if you must.
- Write ONLY under your scratch dir /var/tmp/pcrec-pcrec/scratch/crit-vmcons2/<lens>/ (never /tmp, $HOME,
  any other repo or directory). No edits, commits, branches or worktrees in either repo.
- NEVER run `make` or any suite (tests/harness/run.sh, battery, mech, axes, run_*.sh). Single-pattern probes
  only: run the built compiler, gcc on emitted C, small drivers you write in your scratch dir.
- Never `cd` in a compound command (a hook blocks it): use absolute paths, `git -C`, or a `( cd X && ... )` subshell.
- Bound every run: generated matchers and drivers run under
  `/home/pcrec/projects/pcrec/scripts/watchdog -s 20 -m 1g -S <label> -- <cmd>`; any other uncertain
  command under `timeout 60`. Kill only your own processes, by PID (`scripts/safekill PID`), never pkill -f.
- BOX: NO compiles or probe batches from 18:45 (bench window, then the full suite, 19:00-00:00). If you are
  not finished by 18:45, stop probing, write up what you have (SUSPECTED where unconfirmed) and finish.
- Keep probes light (the box is shared): one gcc at a time, -O1/-O2, never more than ~20 compiles in a batch,
  never more than 50 in total without asking the coordinator.

## Subject (frozen)
- The design: docs/dev/lanes/vmcons2_report.md at commit 2227faf5a0874ff1141cf93922e118488e5c6def ("rev 2").
  Snapshot (identical): /var/tmp/pcrec-pcrec/scratch/crit-vmcons2/subject_vmcons2_report.md.
  Its evidence dir docs/dev/lanes/vmcons2_evidence/ (site_kinds.tsv, body_print_sites.tsv, census.tsv,
  sites.py, calls.py, census.py, cells.sh/log, premise.sh/log) is part of the subject: read it freely.
- It REPLACES rev 1 (docs/dev/lanes/vmcons_report.md, which you may read to see what changed). Rev 2 applies
  review r6 (docs/dev/reviews/2026-10-29-r6-vmcons.md) and keeps rev 1's dispositions of review r3
  (docs/dev/reviews/2026-10-29-r3-vmtrail.md). The MANAGER RULINGS at the end of both reviews BIND. The
  central one (r6 ROOT-CAUSE RULING): "printing is recording": every statement a matcher's emitter prints goes
  through ONE recording primitive, each statement kind is a declared table row (event or declared no-effect
  form), an unknown kind refuses the function, and the corpus token count becomes a STRUCTURAL check.
- The design proposes three landings: (a) the printing-is-recording refactor (byte-identical, no abi bump),
  (b) R (cursor locals), (c) the analysis build (walks, D first-byte dispatch stage 1, C-move, slot-flow
  verdicts DEAD/COPY/UNTRAIL in rounds). It claims ANSWER IDENTITY BY PROOF (G1).

## Base code (what the build would be written against)
- The build lands on main ffb9254cbbae56a2b581bf329c62f58354dbbf0e PLUS lane/trailgc (D183, trail compaction,
  frozen at ffd1f578e25aa0efe32ee124de08b792cd871914), which lands first. The design's survey read
  lane/trailgc 06aa5ab87 merged with main's emitter; src/cli/lib/memfn are identical between 06aa5ab87 and
  ffd1f578e, and main's src is unchanged since the design's branch point 7596d4881. So the review tree IS the
  code the design surveyed. Any cited code that does not match the review tree is a finding.
- BUILT review tree: /home/pcrec/projects/pcrec/worktrees/crit-vmcons2 (main + lane/trailgc merged, not
  committed; non-src merge conflicts resolved by taking lane/trailgc's side, the abi line = 93). Binaries:
  build/pcrec, build/pcrec-harness, build/libpcrec.a. Read its source freely (src/gen/emit_vm.c is the VM
  emitter; also src/gen/memfn_sites.c, clskit.c, callsite_rows.c, emit_code.c, emit_dfa.c, src/compile.c or
  wherever `vmsb` lives, src/core/internal.h, cli/main.c). Do NOT modify it.
- Compiler commands (B=/home/pcrec/projects/pcrec/worktrees/crit-vmcons2/build/pcrec):
  - `$B -p rx -o OUT.c --pattern 'PAT'` (add `--engine=vm` to force the VM route; `-fno-splice-calls` for
    linked calls; `--no-captures`; `-e utf8`; `--features all`; `--allow-code=c` for embedded-code callouts);
  - `$B -p rx --emit-ir --pattern 'PAT'` prints the VM program listing (today's event stream);
  - `--emit-main` appends a main() printing only the overall span; for CAPTURES write your own small driver
    against the artifact's API (docs/spec/match_api.md; tests/harness/ drivers show the shape).
  - `$B --help` / `build/pcrec-harness --help` for flags (`--harness=` levers live on pcrec-harness).
- Oracle: libpcre2-8 is installed (/usr/include/pcre2.h, -lpcre2-8); write a tiny C driver for libpcre2's
  answer (rc + every capture span).

## Reading list
- The guide: docs/dev/guide/critics.md ("Lessons from review rounds"), docs/dev/guide/architecture.md,
  docs/dev/guide/coding.md (emission primitives).
- Spec sections the design cites: docs/spec/ir_listing.md, docs/spec/limits.md (§1, §4-§8),
  docs/spec/match_api.md, docs/spec/pattern_language.md §9, docs/spec/tuning.md.
- docs/dev/decisions.md rows it cites (D183, D174, D76/D94, D77, D153). docs/design/ notes it names.

## DENYLIST (do not open, grep, list or cat; D27 blinding)
- Every file under docs/dev/lanes/ EXCEPT vmcons2_report.md, vmcons2_evidence/ and vmcons_report.md. In
  particular NOT vmcons_evidence/ (rev 1's prototypes: apply the rules BY HAND or with your own script),
  vmcons2_rulings.md, trailgc*, trailgen*, vmbc*, altd*, *_deliver.txt.
- docs/dev/reviews/ files other than 2026-10-29-r3-vmtrail.md and 2026-10-29-r6-vmcons.md (and NOT their
  sibling directories of critic texts).
- worktrees/ other than worktrees/crit-vmcons2; /var/tmp/pcrec-pcrec/scratch/ other than your own dir and the
  crit-vmcons2 files named here (in particular NOT scratch/vmcons2/, scratch/vmcons/, scratch/trailgc*/).
- git log BODIES (subject lines are fine), job logs, the box queue (scripts/boxqueue, worktrees/.mgr),
  docs/dev/optloop/.
If you open a denied file by accident, say so in your findings file.

## Method for "apply the rule as written"
1. Emit the base C (and the --emit-ir listing) for a crafted witness.
2. Apply rev 2's rule, AS WRITTEN in the snapshot, to that program: classify each printed statement by the
   kind table, decide each verdict / dispatch from the table rows and round order exactly as stated (not as
   you think the author meant), and hand-edit a copy of the emitted C into the "rule-as-written twin".
3. Compile base and twin, run both on chosen subjects, compare rc and EVERY capture span; check libpcre2.
4. A changed answer where stock answered = an answer-level finding (G1). Every answer-level finding needs
   its libpcre2 twin result. Where the rule is ambiguous, say which reading you applied and whether another
   reading is safe.
Where the design names a check that pins a mapping, an identity or a count, ask what NON-trivial input makes
it fail (an identity map cannot reveal a keying slip; a chosen token list inherits its author's alphabet).

## Output format
- Your findings file does NOT exist yet: CREATE it at the path in your prompt and write it INCREMENTALLY
  (append each finding as you confirm it; do not hold everything to the end).
- Sections, as markdown `##` headings: `## Findings`, then `## PROBED-AND-HELD`, then `## STATE AT HANDOFF`.
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: pattern, flags, subject, exact commands, the edit you
  made to the twin, observed vs expected, libpcre2's answer; or for a structural claim, the file:line quoted)
  or SUSPECTED (what would confirm it); severity (answer / speed / size / maintenance / doc / design);
  effort; blast radius; the design's § or table row (and review-tree file:line). A finding against a ruled
  row (r3/r6 MANAGER RULINGS) cites it and argues, or drops.
- PROBED-AND-HELD: what you tried that held, with case counts (patterns x subjects, sites checked).
- STATE AT HANDOFF: `STATE: complete` (or `STATE: stopped` with why), and `OWED: none`.
- Keep scratch artifacts (C files, drivers, twin diffs) in your dir; cite them by path.

## Finishing
- Your DELIVER file is already written beside your findings file (see your prompt).
- When your file is complete, run:
  `/home/pcrec/projects/pcrec/scripts/lanecheck --deliver <your DELIVER file> --dir /var/tmp/pcrec-pcrec/scratch/crit-vmcons2 <NAME>`
  Fix every issue it prints and re-run until it prints `lanecheck: DONE rc=0`. Then END.
- Final reply: at most 150 words (it may be lost; the FILE is what counts).
