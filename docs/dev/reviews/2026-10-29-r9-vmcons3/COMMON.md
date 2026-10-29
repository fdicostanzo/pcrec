# COMMON brief: critic round vmcons3 (design SHORT re-check), 2026-10-29

You are a READ-ONLY critic in an adversarial review of a DESIGN document before a build go for its step (a).
Read this whole file first, then your per-lens prompt.

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec), and READ pcrec-bench only if you must.
- Write ONLY under your scratch dir /var/tmp/pcrec-pcrec/scratch/crit-vmcons3/<lens>/ (never /tmp, $HOME,
  any other repo or directory). No edits, commits, branches or worktrees in either repo.
- NEVER run `make` or any suite (tests/harness/run.sh, battery, mech, axes, run_*.sh). Single-pattern probes
  only: run the built compiler, gcc on emitted C, small drivers and scripts you write in your scratch dir.
- Never `cd` in a compound command (a hook blocks it): use absolute paths, `git -C`, or a `( cd X && ... )` subshell.
- Bound every run: generated matchers and drivers run under
  `/home/pcrec/projects/pcrec/scripts/watchdog -s 20 -m 1g -S <label> -- <cmd>`; any other uncertain
  command under `timeout 60`. Kill only your own processes, by PID (`scripts/safekill PID`), never pkill -f.
- Raw-byte patterns never go through `nice` or `env` (uutils rejects non-UTF-8 argv; docs/testing.md).
- BOX: NO compiles or probe batches from 18:45 (bench window, then the full suite, 19:00-00:00). If you are
  not finished by 18:45, stop probing, write up what you have (SUSPECTED where unconfirmed) and finish.
- Keep probes light (the box is shared): one gcc at a time, -O1/-O2, never more than ~20 compiles in a batch,
  never more than 50 in total without asking the coordinator.
- To read files under docs/dev/lanes/ use shell tools (cat/sed/grep), not the Read tool: Read there
  auto-injects that directory's CLAUDE.md (orientation only; harmless, but disclose it if it happens).

## Subject (frozen)
- The design: docs/dev/lanes/vmcons3_report.md at commit 62980551baa7df23ff0fadeb7699a9780c0d81fc ("rev 3",
  merged to main 3963ee728, unchanged on main 362f8e2e1).
  Snapshot (identical): /var/tmp/pcrec-pcrec/scratch/crit-vmcons3/subject_vmcons3_report.md.
  Its evidence dir docs/dev/lanes/vmcons3_evidence/ (calls.tsv, calls3.py, render_check.py/.log,
  frag_lex.py, kit_census.py/.sh/.log, kit_census_run1.log, census_pats.tsv, cscan.pat, cells.sh/.log,
  premise.sh/.log, sig_rev2.py, drv.c, p2.c, run.sh) is part of the subject: read and RE-RUN it freely
  (copy scripts into your scratch dir first; point them at the review tree's build).
- It REPLACES rev 2 (docs/dev/lanes/vmcons2_report.md, which you may read to see what changed). Rev 3 applies
  review r8 (docs/dev/reviews/2026-10-29-r8-vmcons2.md) and keeps rev 2's dispositions of r6
  (2026-10-29-r6-vmcons.md) and of r3 (2026-10-29-r3-vmtrail.md). The MANAGER RULINGS at the end of all three
  reviews BIND. The central one, r8's second-pass ROOT-CAUSE RULING: "the record is the source": each emitter
  site BUILDS a typed record, each kind has ONE renderer that prints it, text is rendered from the record.
- Rev 3 proposes landings (a) the record-first refactor (BYTE-IDENTICAL, no abi bump, lands first and alone;
  evidence plan E1-E7), (b) R (cursor locals), (c) the analysis build (walks, D first-byte dispatch,
  C-move, slot-flow verdicts). It claims ANSWER IDENTITY BY PROOF (G1). The build go being asked for is (a).
  Where rev 3 still LEXES text (not renders it) is the kit's delegated windows, the clskit inline class test,
  the SIMD witness block, and pcrec's own VM_LIT pieces: checked by four lexer rules R1-R4.

## Base code (what the build would be written against)
- The build lands on main 362f8e2e182e97b025e21753a07eef3f02d8af9a PLUS lane/trailgc (D183, trail
  compaction, frozen at ffd1f578e25aa0efe32ee124de08b792cd871914), which lands first. Main's src/cli/lib/memfn
  are identical to the design's base 26804bd46; so the review tree IS the code the design surveyed. Any cited
  code (file:line) that does not match the review tree is a finding.
- BUILT review tree: /home/pcrec/projects/pcrec/worktrees/crit-vmcons3 (main + lane/trailgc merged, not
  committed; non-src conflicts taken from lane/trailgc's side, abi = 93). Binaries: build/pcrec,
  build/pcrec-harness, build/libpcrec.a. Read its source freely (src/gen/emit_vm.c is the VM emitter; also
  src/gen/memfn_sites.c, clskit.c, callsite_rows.c, emit_code.c, emit_dfa.c, src/core/compile.c,
  src/core/internal.h, src/core/strbuf*, cli/main.c, memfn/). Do NOT modify it.
- Compiler commands (B=/home/pcrec/projects/pcrec/worktrees/crit-vmcons3/build/pcrec):
  - `$B -p rx -o OUT.c --pattern 'PAT'` (add `--engine=vm` to force the VM route; `-fno-splice-calls` for
    linked calls; `--no-captures`; `-e utf8`; `--features all`; `--allow-code=c` for embedded-code callouts;
    `-fcomments`, `-fmemfn-simd`, `--trace` axes);
  - `$B -p rx --emit-ir --pattern 'PAT'` prints the VM program listing (today's event stream);
  - `--emit-main` appends a main() printing only the overall span; for CAPTURES use the evidence dir's
    drv.c/p2.c drivers or write your own against docs/spec/match_api.md.
  - `$B --help` / `build/pcrec-harness --help` for flags.
- Oracle: libpcre2-8 is installed (/usr/include/pcre2.h, -lpcre2-8); write a tiny C driver for libpcre2's
  answer (rc + every capture span), or reuse p2.c.

## Reading list
- The guide: docs/dev/guide/critics.md ("Lessons from review rounds"), docs/dev/guide/architecture.md,
  docs/dev/guide/coding.md (emission primitives).
- Spec sections the design cites: docs/spec/ir_listing.md, docs/spec/limits.md (§1, §4-§8),
  docs/spec/match_api.md, docs/spec/tuning.md.
- docs/dev/decisions.md rows it cites (D183, D174, D76/D94, D77, D153, D146/D147). memfn/CLAUDE.md.

## DENYLIST (do not open, grep, list or cat; D27 blinding)
- Every file under docs/dev/lanes/ EXCEPT vmcons3_report.md, vmcons3_evidence/, vmcons2_report.md and
  vmcons_report.md. In particular NOT vmcons3_rulings.md, vmcons2_evidence/, vmcons_evidence/, trailgc*,
  trailgen*, vmbc*, altd*, *_deliver.txt.
- docs/dev/reviews/ files other than 2026-10-29-r3-vmtrail.md, 2026-10-29-r6-vmcons.md and
  2026-10-29-r8-vmcons2.md (and NOT their sibling directories of critic texts).
- worktrees/ other than worktrees/crit-vmcons3; /var/tmp/pcrec-pcrec/scratch/ other than your own dir and the
  crit-vmcons3 files named here (in particular NOT scratch/vmcons3/, scratch/vmcons2/, scratch/crit-vmcons2/,
  scratch/trailgc*/).
- git log BODIES (subject lines are fine), job logs, the box queue (scripts/boxqueue, worktrees/.mgr),
  docs/dev/optloop/, docs/dev/plan.md rows beyond a single `grep -n '^- \[TAG\]'` line.
If you open a denied file by accident, say so in your findings file.

## Method for "apply the rule as written"
1. Emit the base C (and the --emit-ir listing) for a crafted witness.
2. Apply rev 3's rule, AS WRITTEN in the snapshot, to that program: build the record stream by hand or by
   script (which builder each printed statement goes through; its operands; its fragments), apply the kind
   table's columns, the lexer rules R1-R4, the tiling invariant, and any verdict/dispatch rule exactly as
   stated (not as you think the author meant); where it changes text, hand-edit a copy of the emitted C into
   the "rule-as-written twin".
3. Compile base and twin, run both on chosen subjects, compare rc and EVERY capture span; check libpcre2.
4. A changed answer where stock answered = an answer-level finding (G1). Every answer-level finding needs its
   libpcre2 twin result. Where the rule is ambiguous, say which reading you applied and whether another
   reading is safe.
For every check the design names (tiling, the lexer, render_check, RT, K2-K4, E1-E7), ask what NON-trivial
input makes it fail, which text domain it reads, and try one input per axis that reaches it (comments
on/off, -fmemfn-simd, --trace, pattern bytes in literals, -e utf8, --engine=vm vs default). A check whose
population was chosen by the author inherits the author's alphabet.

## Output format
- Your findings file does NOT exist yet: CREATE it at the path in your prompt and write it INCREMENTALLY
  (append each finding as you confirm it; do not hold everything to the end).
- Sections, as markdown `##` headings: `## Findings`, then `## PROBED-AND-HELD`, then `## STATE AT HANDOFF`.
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: pattern, flags, subject, exact commands, the edit you
  made to the twin, observed vs expected, libpcre2's answer; or for a structural claim, the file:line quoted)
  or SUSPECTED (what would confirm it); severity (answer / speed / size / maintenance / doc / design);
  effort; blast radius; the design's § or table row (and review-tree file:line). Say whether it blocks the
  build go for (a) or only (b)/(c). A finding against a ruled row (r3/r6/r8 MANAGER RULINGS) cites it and
  argues, or drops.
- PROBED-AND-HELD: what you tried that held, with case counts (patterns x subjects, sites checked).
- STATE AT HANDOFF: `STATE: complete` (or `STATE: stopped` with why), and `OWED: none`.
- Keep scratch artifacts (C files, drivers, twin diffs) in your dir; cite them by path.

## Finishing
- Your DELIVER file is already written beside your findings file (see your prompt).
- When your file is complete, run:
  `/home/pcrec/projects/pcrec/scripts/lanecheck --deliver <your DELIVER file> --dir /var/tmp/pcrec-pcrec/scratch/crit-vmcons3 <NAME>`
  Fix every issue it prints and re-run until it prints `lanecheck: DONE rc=0`. Then END.
- Final reply: at most 150 words (it may be lost; the FILE is what counts).
