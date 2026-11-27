# 2026-11-26 r105 arenaclients (code)

Subject: lane/f2f6tri = 4ece5e9bb ([ARENA-SCOPES] F2 clskit S14 + F6 uprops_produce S29 as scope clients, on lane/f2f6
fef6e55b4, plus triage: W7/W3 floor 267 -> 264 and alloc_check --w7-only skipping the stale known_stranded loop).
BASE cd17dea82. Rulings frozen at main 92b402e28; no drift at hand-back (main, subject, decisions/plan/arena_scopes.md unchanged).
Design of record: docs/design/arena_scopes.md rev 2.1 + Deviations at build.

## Lenses as run (SMALL round, owner's slow-burn week)
| lens | model | question | why |
|---|---|---|---|
| scope lifetime (ruling check + slot tracing; sibling-of-family + general form folded in) | opus | are both scoped regions registry-sound on every arrival; did r104 REGISTRY-1's force-loop trigger fire | the one answer/crash risk; strong lens judged essential |
| check adequacy (+ trade audit, + general form of the triage fix) | sonnet | can every new/changed check fail in its declared suite; what did the re-pin give up; is --w7-only's guard a special case | 4 sabotage rows, a scanner rule, a floor re-pin, a check fix |
Coordinator inline: emitted identity, 49 BASE/SUBJECT pairs (7 patterns x 7 flag sets incl. kit-emitting --tune<0 and
`\p` decodes): 37 compiled pairs byte-identical, 12 refused identically on both sides. Plants S3613/S3615 prebuilt.

## Findings (PROPOSED dispositions)
No answer-level or speed-level finding.
- SCOPE-1 (scope) HELD: no parent registration inside either region; depth <= 1; parent always a Ctx arena; a forced
  refusal inside the kit scope unwinds exactly one scope, rc 1 clean. NOTED.
- SCOPE-2 (scope) HELD: REGISTRY-1's trigger has NOT fired (force loop reaches only pf_derive readers; 0 scope opens
  after force entry on 3 patterns hitting both clients). NOTED; trigger stands.
- SCOPE-3 (scope) doc: comments in mod_uprops.c:292 and clskit.c:1122 say "teardown" releases the child; in
  compile_driver it is the handler-top unwind (teardown only for count_groups/syntax_dump). DOC (2-line fix, ride the
  next touch or the landing).
- SCOPE-4 (scope) size, SUSPECTED: `pcrec_clskit_emit_whole` (emit_vm.c:13347, the same site's other arm) keeps its
  scratch in the attempt arena, retained to attempt end: gdb 119 KB of 2.98 MB (`x\p{L}y`), 497 KB of 4.52 MB (11%)
  (`x[\p{L}\p{N}\p{M}]y`, -e utf8 --engine=vm). COST-1 class (D-5/[ARENA-REGROW], U7). PLAN: one memgate peak
  measurement decides; if above noise it is F2's shape (3 lines), not a new mechanism. Family otherwise CLOSED: 0
  hand-kept Ctx-bound locals remain.
- SCOPE-5 (scope) design: general form + unlocks recorded (emit_whole joins F2 on SCOPE-4's trigger; L5 lift trigger
  half-fired: intern_records now reached from parent and child, opens no scope; REGISTRY-1 unchanged). NOTED (record
  the L5 half-fired state in arena_scopes.md D-2 L5: DOC).
- CHECKS-1 (checks) maintenance, CONFIRMED: D-11 rule's file/function half is untested: 4 clause mutants (rel==/fn==
  deletions in the binder and mf_art_begin tests) + the D11_SEEN floor (<1 -> <0) survive the self-test; every
  fixture is wrong on the VALUE. FIX-NOW (small, before landing): 3 MUST_FAIL fixtures (correct `&cx->arena` binder in
  the wrong file; in the wrong function of memfn_sites.c; a `pcrec_memfn_art` in another file calling mf_art_begin) +
  a floor plant. Hand the mutation harness (checks/mut/) to the fix lane as its gate.
- CHECKS-2 (checks) maintenance, CONFIRMED: L4 allow match survives deletion of its file clause; SCOPE_CALL narrowed
  to open-only survives; scan dropping cli/lib survives; MIN_SCOPE_OPENS still 1 (coordinator checked:
  scratch_builder_check.py:508) with 3 sites at SUBJECT, not re-derived (D110); SCOPE_PARSE_ALLOW has no stale-row
  check. FIX-NOW for the floor re-pin (2) and the file-clause fixture; PLAN for the stale-row check and per-tree floor.
- CHECKS-3 (checks) HELD with a trade: S3613/S3615 LOUD in harness (S3613 on tests/utf8: 460 cases failed; witness
  `[^a-z]+x -e utf8 --engine=vm` at DEFAULT tune, refining the coordinator's --tune<0 fact), scanner LOUD; S3614
  LOUD (core, sole net, as declared); S3602 LOUD by the planted control only (read, not run: needs make alloc).
  Trade: after F6 no real compile exercises W7's hand-kept window; the control is its only net. DOC: say so in the
  SEEN-gate text (arena_scopes.md). clskit_driver never runs check_closed, so the clskit arm is silent on S3613 (not
  assigned to it): NOTED.
- CHECKS-4 (checks) doc: 267 -> 264 follows D110 (half of 528) but was not forced (528 >= 267), and 528 is cited to a
  job log, not a command in the tree. DOC: cite the command (`alloc_check --w7-only` under make alloc) beside the number.
- CHECKS-5 (checks) maintenance, CONFIRMED (coordinator re-read alloc_check.c:1268-1280): the --w7-only guard is one
  of three whole-run statements: the stale loop (guarded), K60 table (implicitly safe), `if (do_single) w5_run();`
  (line 1280, UNGUARDED: W5 runs and can fail in a W7-only measurement). `--w7-only` is in no usage text and no suite.
  FIX-NOW (one predicate `whole_run = !w7_only` gating every post-loop whole-run statement; add it to the usage line).

## PROBED-AND-HELD
scope: 3 openers + 1 hold in src, none nested; 6 natural refusal arrivals (0 with a scope open); 1 forced refusal in
the kit scope; 2 forged FIT_FORCE_NEXT arrivals (not realizable); 3 --emit-facts runs; 5 Ctx constructors set arena.cx.
checks: 4 sabotage rows classified; 35 scanner mutants (survivors listed above; the rest caught rc=2); tests/utf8
harness run on plant S3613; 48 plant probes. Coordinator: 49 identity pairs.

## By-id completeness
SCOPE-1..5, CHECKS-1..5: all dispositioned. Verifier: none (inline; every CONFIRMED is a quote or a mutation the
critic's harness reproduces; coordinator re-read CHECKS-2's floor and CHECKS-5's lines).

## Lessons for the guide
- The coordinator's reach fact for S3613 was too narrow (tried only a P3-routed pattern at default tune); the critic
  found a default-tune witness. Prebuilt plants paid for themselves: both critics used them with no build time.
- A plant tree made from a SUBJECT `git archive` carries the denied lane reports: delete denylisted paths from plant
  trees before briefing (done this round by hand).

## Manager's rulings (2026-11-26)
All proposed dispositions ACCEPTED. FIX-NOW CHECKS-1, CHECKS-2 (floor re-pin to 2 + file-clause fixture), CHECKS-5, plus
the DOC items SCOPE-3, SCOPE-5 (D-2 L5 half-fired state), CHECKS-3 (SEEN-gate text), CHECKS-4 (cite the command) go to
fix lane f2f6fix before landing. CHECKS-2's stale-row check and per-tree floor: PLAN (with [ARENA-SCOPES] F3). SCOPE-4:
PLAN, decided by one memgate peak measurement in the F3 lane (if above noise, emit_whole takes F2's shape). Process
change ACCEPTED (pcrec-critic §3: plant/BASE trees from a SUBJECT archive have denylisted paths deleted before briefing).
