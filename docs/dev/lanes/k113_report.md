# Lane k113 (sonnet), 2026-10-21 -- K113: a compound part inherits the parent's analysis chain

Branch `lane/k113` from main 0e8fca96e. Build go: Frank 2026-10-21 ("you have a go for 1,2").
Rulings file read: empty (no entries).

## Premise (confirmed on main)
`compile_driver` (src/core/compile.c:2524) calls `pcrec_find_resolve` and (2536)
`pcrec_memfn_analysis_build` once per attempt; a part's `pcrec_compile_driver` is the same
function, so each part re-ran both from the parent's copied options.

## The change: ONE channel, extended
`PcrecMeasInherit` (the `PcrecEmitIn.meas` channel of lane partmeas) now also carries
`chain` (`&Job.find.chain`) and `analysis` (`Job.analysis`). Extended rather than paralleled
because both are "the walking attempt's resolved knowledge sources" with the same lifetime
(the walking attempt's arena) and the same consumer (`walk_part`); the struct name and the
`emit_in->meas` field keep their spelling so sabotage S1291/S1294 anchors stay valid, the
comments say what it now carries.
- `src/core/compound.c` `walk_part`: fills the two new fields.
- `src/parse/rxt_find.c` `pcrec_find_resolve`: on an inherited channel copies the chain, returns
  (resolves nothing, prints no notes; the walk printed them once).
- `src/gen/memfn_sites.c` `pcrec_memfn_analysis_build`: on an inherited channel takes the
  walk's object, builds none (the walk's invariant check stands).
- `src/core/internal.h`: struct + comment. `pcrec_compile_part` (NULL meas) is unchanged.
A part's own findings memo/ask record stays its own (consumption is per attempt; the union
stamp is untouched); a part derives the same table from the same chain.

## Check and sabotage
`tests/compound/run_part_analysis.sh` (in `run_compound_unit.sh`): -DPCREC_KS_TRACE build; the
split witness must write as many `KSTRACE ... resolve` and `KSRCTRACE object` lines as a
non-compound control, in two arms (default chain, `--analysis default`); floor 4. Rows:
S1331 (part re-resolves the chain, rxt_find.c), S1332 (part rebuilds the object,
memfn_sites.c). Ids used: S1331, S1332 (S1333-S1335 free).
A limit of the check: the counts are compared to a control, so a retry-ladder difference
between witness and control would read red; none is expected.

## Spec
No caller-observable change in answers or stamps, so no docs/spec hunk. The only observable
difference: a part no longer repeats the resolution NOTES on stderr (a note printed per part
before, once now). Not spec'd text; flagged.

## STATE AT HANDOFF
NOT built or run by the lane: a quiet-gated kit timing job (580-kit-r27-cover) held the box and
BOILERPLATE forbids any run outside the queue, so even `make` is OWED. The edit is untested.
Queued as one batch, owner k113, prio 700 (stages: build, strict, sweep, compound, test, mech;
build/STAGES): the sweep is `emit_sweep --ref 0e8fca96e` and must read 0 movers (if any byte
moves: STOP, abi event). Verdicts: `scripts/boxqueue status`; mech completion line
`== mech run COMPLETE`. Rulings read through: none.

## Triage: §14 C-E1-4 compound witness (lane k113tri)
Cause: stale expectation, not a defect. The check counted compiles as `KSTRACE ... resolve`
groups (want >= 3); K113 removes exactly those per-part records, so it read 1. The
compound still compiles its parts: the per-attempt reader records
(`KSTRACE analysis byte-rate pcrec_req_pick <bundle>`) still appear once per attempt (3 for
`^\s+|\s+$`). Fixed in tests/findings/e1_object_check.py: compiles = `pcrec_req_pick`
records (floor 3), AND exactly one resolve group whose object set is whole, AND every reader
record names the shell object's bundle (parts carry the one object). Not vacuous: a part that
re-resolves adds resolve groups (fails "1 resolve"); a part that drops out fails the floor.
Run standalone against a fresh -DPCREC_KS_TRACE build: the new check PASSES (3 compiles).
The full §14 section was not rerun by the lane (the queue retry does it); the standalone
"multi" row failed only because RES (the suite's res dir) was absent in the ad hoc run.
