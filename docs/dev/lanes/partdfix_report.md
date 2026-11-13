# partdfix — the fixes for job 597's (kit-partdland-gate) four reds

STATE: delivered (validation numbers below; the re-run gate 598-kit-partdfix-gate, the cloud test and the mechrows OWED)

## Summary

Lane partdfix (opus, 2026-11-13) fixed what the kit's Part D box gate (597-kit-partdland-gate, lane/memfn-partd
e33ab2de8) found red, at the cause, on lane/memfn-partd. No emitted byte moves: nothing under `src/`, `cli/`,
`lib/` or `memfn/src/` changed, so the re-run is the REDUCED gate (598), not the full one.

1. **c01877 is not a kit bug.** The check's join was wrong. The kit prints one record per define, as D3
   says. The compile of `(?i)(?:^|[\x5c/])\.{2,3}[\x5c/]` (tests/compound/split.rxt) begins THREE arts:
   the compound walk's trial parts (arts 1 and 2), then the plain artifact that ships (art 3; `RX_COMPOUND
   none`, `RX_DFA_SCAN attempt`). Art 1's DFA_SCAN define and art 3's DFA_ATTEMPT define each derive the run
   part, so each prints its record. The shipped text holds ONE rendering (one `rx_reqrun__body`, one
   `memcmp`). `runpart_prod.py` summed the records over every art. It now joins on the SHIPPED art, the
   compile's last (`collect.py` records `arts`). Earlier arts' records are counted and reported, never
   joined. A compound shell with an emitted stamp is a loud FAIL, since the join names no single art there.
   Over the 9 corpus compiles that begin more than one art and print a record, the record sits on the last
   art in all 9.
2. **A real probe defect found on the way.** `probe.c`'s `mf_art_begin` wrapper still carried the policy
   word that u2rev retired (MF_SITE_ABI 26). Every argument after `prefix` was shifted. `denies` was cut to
   32 bits, `an` was read from a garbage register, and every sweep's `R33RATE` line was junk. The c01877
   compile segfaulted outside `timeout` (register contents). The wrapper is fixed, and a `_Static_assert`
   now ties each wrapper to memfn.h's prototype. With the old prototype it fails the build.
   **FINDING for the kit manager:** job 597's `prod.jsonl.rates.json` holds ONE rate entry, `present=-1
   rate=none`. Any sweep this probe collected after u2rev (9c1f0db4a) therefore carries no byte-rate table.
   sim.py prices those sweeps by uniform cardinality, and `census0.py` reads `.rates.json`. Any golden or
   decision taken from such a sweep's rates should be re-checked against a re-collected sweep. This lane
   did not re-derive any of them (out of scope).
3. **S3113's detector is the family's COVER check.** COVER is not the oracle. COVER is G2's own positive
   check (a whole occurrence IS yielded). The plant's scan-less part searches for byte 0, so it misses every
   occurrence without it. Re-run alone, the plant reds COVER on 60 sites in each of the six passes, and
   nothing else in the family. The row's old patterns could not see it: the scanless_match FLOOR counts
   generator facts the plant leaves alone, and SOUND/EXTENT check that nothing false is yielded.
4. **The gate's `base` and `start` arms** now declare exactly the new axis. Both pass
   `--dumps-declared-new=--list-axes:run-verify-wide`, an existing option judged both ways: one row new,
   every other line byte-identical. `start` also passes `--arms-ref-predates=--memfn=no-run-verify-wide`,
   a new emit_sweep option. It skips that flag's table arms and names and counts them on one line. A flag
   that names no table arm fails the run. The job asserts `rows=1` and `2 table arms skipped (byte, utf8)`.

## c01877

Reproduced with one compile of the gate's own probe build: `PCREC_MF_ROUTE_TRACE=1 pcrec-r33 --features all
-p rx -o - --pattern '(?i)(?:^|[\x5c/])\.{2,3}[\x5c/]'`. Two `MFTRACE run_part_terms` lines appear:
`art=1 site=2` (PRE DFA_SCAN) and `art=3 site=1` (PRE DFA_ATTEMPT). The artifact stamps `REQ_RUN "2e2e@1"`
and `REQ_WHY "emitted"`, and holds one run compare. gdb puts art 2's begin inside `pcrec_compound_walk ->
walk_part(i=1) -> part_compile(unrendered=true)`. compile.c runs the walk before the main emit, and a
failed attempt's retry is sequential, so the art that ships is the last one begun.

**Which side was wrong.** The check, not the kit and not D3's text. D3 says every site whose ARTIFACT
stamps a run carries exactly one record. The check counted every art of the compile. No duplicate print
happened, and no re-asked define under MF_TRACE: each record belongs to a distinct define on a distinct art.

**Fix** (commit a063ff454):
- `docs/dev/lanes/r33_sim/collect.py`: `parse` returns `(sites, arts)`, and each line carries `arts`.
- `docs/dev/lanes/r33_sim/runpart_prod.py`: the shipped-art join. It reports `records_on_unshipped_arts`.
  It FAILs on a sweep without `arts`, and on an emitted stamp whose artifact has more than one REQ_RUN
  stamp. It also has a `--self-test FIXTURE` mode.
- `docs/dev/lanes/r33_sim/fixtures/runpart_c01877.jsonl`: one REAL collect.py line for c01877 (fixed
  probe), with a record on each side of the join.
- `docs/dev/lanes/r33_sim/probe.c`: the wrapper's prototype fixed, plus `_Static_assert`s for all three
  wrapped entries.
- `docs/design/memfn/part_d.md` D3: the production path names the shipped art (the last), and states that
  earlier arts' records are counted, never joined.

**Witness that fails before the fix.** The pre-fix `runpart_prod.py` (HEAD e33ab2de8) on the fixture gives
`FAIL: corpus c01877: ... 2 run_part_terms records, not 1`, rc=1. The fixed check gives `one_record=1
records_on_unshipped_arts=1 failed=0`, rc=0. `--self-test` checks four cases: the fixture GREEN, the shipped
record doubled RED, the shipped record moved to art 1 RED, and `arts` missing RED (`cases=4 wrong=0`). The
fixture's own shape is checked first: a fixture that loses its earlier-art record fails the self-test. The
probe guard: the HEAD probe.c with the asserts added fails to compile, `static assertion failed: "stale
mf_art_begin wrapper"`.

## S3113

The plant was re-run alone: `G2P_KEEP=1 bash memfn/tests/run_g2_pres.sh --plant S3113`, log
`/var/tmp/pcrec-pcrec/scratch/memfn/partdfix/plant.S3113.log`, fails file `.../tmp/g2pres.OjZumt/fails.S3113`.
That file has 360 FAIL lines, and every one is `COVER` (60 per pass x {x86-64-v3, x86-64, generic} x
{default, lever}). There is no FLOOR, SOUND, EXTENT or PRESENCE line. The oracle also reds (792 violations);
that is the backstop. The triage called the red "by the oracle", but its quoted line `FAIL x86-64-v3.default
site 440 (precheck): COVER: ...` is a FAMILY line (`g2_pres_run.c`'s `classify`).

**Ruling taken: re-aim the row at the detector that sees it** (commit 3c838a0e0). `plant_expect S3113` is
now `': COVER: part at [0-9]+ len [0-9]+: member '`, and its comment carries the measurement. The design
text (part_d.md p10) records it as MEASURED. Why the old patterns cannot see it:
- the `scanless_match` floor counts `pres_check` calls on sites the GENERATOR made scan-less, so it is
  blind to what the kit renders;
- SOUND and EXTENT ask that nothing false is yielded, but the plant only loses true occurrences;
- PRESENCE goes through the site's entry, and those answers held.

The mech row file `tests/mech/sabotages/S3113_every_pos_reads_byte_zero.sh` is unchanged (SAB_EXPECT
DETECTED, suite g2pres). Its detector expectation lives in `plant_expect`, and that changed, so S3113 is
OWED to mechrows.

## Gate script

The job is `/var/tmp/pcrec-pcrec/scratch/memfn/partdfix/jobs/gate.sh`, queued as 598-kit-partdfix-gate,
cap 7200, est 3600, BASE dd5143e8d built fresh by the job. It runs only:
- (1) identity arms `base` and `start`, with the declaration;
- (2) the deny's two cells (green in 597, re-run because emit_sweep.py changed);
- (3) plant S3113;
- (4) the production path: build.sh with the fixed probe, collect over the corpus, runpart_prod GREEN
  (floor 100), the join's `--self-test` GREEN, c01877 asserted in the sweep (record on art `arts` = 1,
  earlier >= 1), and p14 RED.

The declaration is narrow on purpose. On the dumps stream, `--dumps-declared-new` admits exactly the
`run-verify-wide` row of `--list-axes`: any other dumps difference, or a second new row, still fails. The
job also asserts the `DECLARED MOVES ... patterns=1 rows=1` line. `--arms-ref-predates` removes only the
named flag's table arms, and the job asserts exactly one `arms: REF predates` line, reading `2 table arms
skipped (byte, utf8)`. Every other arm, stream, floor and witness of `start` runs as before.

emit_sweep.py's new option (commit e9bc192e8) was smoke-tested against job 597's REF build:
- `--limit 40 --arms start` with both options: rc=0, `arms: REF predates --memfn=no-run-verify-wide: 2
  table arms skipped (byte, utf8)`, dumps `movers=0`, `rows=1`;
- a stale second flag (`--memfn=no-bogus`): rc=1, `names no table arm (a stale declaration)`;
- without the option: rc=1, 4 ASYMMETRIC cells.

Dry run: `would run ... production path over 5489 corpus compiles`, rc=0.

## Checks

Validation chain `/var/tmp/pcrec-pcrec/scratch/memfn/partdfix/val/chain.sh` (box lock, one step at a time,
index `val/val.log`, a log per step):

| check | result |
|---|---|
| make -j16 | rc 0 |
| make strict | rc 0 (20 s) |
| make test-codegen | rc 0, run_group 21/21 scripts passed (207 s) |
| make test-memfn-finder / rows / link / targets / arch / forms | rc 0 each |
| anchors (scripts/m6read_check_sab_anchors.py) | 1,294 sabotages, 1,345 anchor sites, all resolve |
| run_g2_pres.sh --plant S3113 (the file the gate runs) | `PLANT S3113 RED   (family; oracle RED ...)`: red by its own detector, COVER; rc 0 (96 s) |
| make test-memfn-d27frame | PASS: 6,937,301 checks passed, 0 failed (floor 6,500,000) |
| make test-memfn-g2 (the quick tier) | rc 0: 70,358,671 passed / 0 failed (712 s) |
| runpart_prod.py --self-test fixtures/runpart_c01877.jsonl | cases=4 wrong=0 |
| runpart_prod.py over the 9 multi-art record compiles, re-collected with the fixed probe | emitted=9 one_record=9 failed=0 |

## Owed runs

OWED: kit-partdfix-gate (598-kit-partdfix-gate, script /var/tmp/pcrec-pcrec/scratch/memfn/partdfix/jobs/gate.sh,
completion line `partdfix-gate: DONE bad=0`); cloud test on the lane tip; mechrows S3113 (its detector
expectation changed). No other row id changed.
