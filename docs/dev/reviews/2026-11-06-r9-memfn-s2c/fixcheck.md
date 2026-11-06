# Findings

(critic crit-memfn-s2cfix, subject lane/memfn-s2c @ 88a47cff8, diff 79c5e91e5..88a47cff8; export built rc 0)

### FIX-1 CONFIRMED (answer) — equal records + equal cells, different verdicts: est reads the CARDS and POLICY live
est.py:136 (`plan.CARD[...]["est"]`, `plan.base_of`), est.py:196/201 (`plan.CARD[...]["gate"]`), est.py:152
(`plan.LENGTHS`); record.py finalize keeps only `r[:3]` (key group job) of the frozen plan, dropping its
estimator/base columns, and nothing checks RUNDIR/plan.tsv's `inputs` section (which DOES pin kit-grid.tsv and
policy.tsv by sha) against today's files at est time.
Repro: `est._synth(D)` (selftest's synthetic finalized run), then 4 of 7 unit-twin cells x1.004 in cells.J2.tsv;
`est.compute(D)` with SLOT_TREE=export -> `('FULL', 0)`, unit noise 4000; with SLOT_TREE=a copy whose
memfn/data/policy.tsv says `gate_default_e6 300` -> `('REFUSED', 3)`. sha-256 over run_record.tsv + every
cells.J*.tsv identical (f1912d52...) across the two calls. Expected (r9 G3, the brief's drill): the record
determines the verdict, or est refuses. A card `lengths`/estimator edit is the same hole (caught only when it
happens to name a cell that is absent).
So r9 G3 (and SLOT-17's "one home") is closed for plan/floor/jobs but NOT for the card facts and the gate.
Fix (small): est and draft refuse unless RUNDIR/plan.tsv's `inputs` shas equal today's files and its `rows`
equal `rec["plan"]` (or finalize copies the frozen plan's sha into `run` and est checks it), and est takes
estimator/base from the frozen rows. Today those two frozen columns have NO reader at all: a (b) item.

### FIX-2 CONFIRMED (answer, latent) — the KEY's subject dims are never compared with the Arm (G2's general form)
link.py render/arm_entry: `plan.key_form` reads only (form, cls) off the key; landing, split, gap (find_hit),
pass (verify_cmp), events and the length come from the Arm's own fields and are never checked against the
key's tokens. Repro (python against the export's link.py, fx by fx_path):
`Arm("kit.find_hit.libc.periodic.one.256", ..., "libc", landing="random", split="alt", gap=1024, ...)` renders
(form/cls ('libc', None)) and its table entry is `LD_RANDOM, 1, 1024` under the key `periodic.one.256`; likewise
`kit.verify_cmp.settest.c2.p0` with `pas="p50"` renders. gen.c plants by the Arm's fields, so the gate agrees with
itself and every check is green while the row carries another subject's price. (S2935's own plant, libc key with
a walk Arm, IS refused: "KEY-ARM MISMATCH kit.find_byte.libc".) Today plan.py builds key and Arm from one loop
variable, so there is no live bug; it is r9 G2's seam one level down. Fix: parse every key token by the card's
`dims` (one table: dim -> Arm field) and compare in render; one sabotage row for one dim.

### FIX-3 CONFIRMED (speed: costs the window) — a ref-name FROZEN passes every --dry-run, then every job fails
jobs/common.sh check_inputs accepts any FROZEN that `rev-parse "$FROZEN^{commit}"` resolves (a branch name
passes); run.py `run` passes CODE_COMMIT=$FROZEN to `record.py window`, which requires `[0-9a-f]{7,40}`.
Repro: `record.py window D r1 lane/memfn-s2c` -> "record: REFUSED: ... a commit is a hex object name", rc 2,
while `git rev-parse lane/memfn-s2c^{commit}` resolves. So every timing job's run fails at its first step
("record.py window rc 2"), after the queue's dry runs were all green. Fix: check_inputs requires FROZEN to be
the hex sha `rev-parse` returns (or exports the resolved sha as CODE_COMMIT); window.env.example says "full sha".

### FIX-4 CONFIRMED (maintenance) — S2934 (l3) reaches the CONTROL's gate only; sabotage.sh's control evidence is overwritten
sabotage.sh l3 plants the shared WRAP_FIND text, so the planted ctl (built from the copy's link.py) refuses
first: observed `GATE MISS ctl len 65536 subject 0 SENTINEL ... timed 0, planted 1`, "== s2 GATE FAILED: 1 arms,
3 pools, 336 subjects" and run.py exits before any LAUNCH executable is gated. The row's own text ("even the
miss-only find_byte arms miss") is never exercised: a drv/run.py bug that skipped the timed check on the launch
gates only would leave S2934 DETECTED ([MECH-REACH] shape). Fix: plant in the arms' TUs only (e.g. key the plant
on a -D only link_job passes, or build ctl from the unplanted text) and widen `want` to name a kit arm.
Also: `dry control est` writes `$SCR/control.out` and `rm -rf $SCR/run.control` after `dry control J2`, so the
control's J2 dry-run output and RUNDIR (manifest, cell_text) are destroyed; only its rc survives. Use
`control.est` names.

### FIX-5 CONFIRMED (design/doc, latent) — vcls's "lowering shapes" are not gcc's lowering
vcls.py `shape()`: "case" requires `a ^ b == 0x20 and chr(b).isalpha()`; "range" is documented "(two compares)".
gcc 15.2 -O2 -march=x86-64 -mtune=generic (the declared target): `x>=48 && x<=57` -> `subl $48; cmpb $9`
(ONE compare); `x==64 || x==96` ({@,`}, non-alpha, one bit apart) -> `andl $-33; cmpb $64`, identical to the case
pair, yet vcls calls it "pair"; only a pair differing in more than one bit is two compares. Today's verdict holds
(c2 = case 156, pair 79, range 53, other 4: the instance's shape `case` is the majority, and the true one-compare
share is at least 209/292), so EMIT-3's ruling is not undone. But the gate in link.py `shape_tag` would REFUSE a
future census where `range` outnumbers `case` (same lowering) and tag `lower-bound` where neither alone is a
majority (case 120, range 100, pair 72), both wrongly. Fix: classify by lowering (one ALU op + one compare: any
single-bit pair or an inner range; two compares: other pairs), and correct the vcls.py/CLAUDE.md text.

### FIX-6 SUSPECTED (size: abs_ns_e6 only) — the ROUND's call loop is unchecked; ACC is printed and never read
drv.c `run_n` times `n` calls of `a->time`; its ACC (Σ counts) is printed as field 7 of each `pt` line, and
run.py reads only field 6 (`int(p[5])`). A plant that shortens run_n's loop (or its pool, `p->np`) is caught by
nothing; because ctl uses the same drv.c, ratio values survive it and abs_ns_e6 does not, unless the plant is
kind-specific. Would confirm: plant `k < n / 2` in run_n under `a->kind == K_CMP`, run J4 dry + one round: green.
Cheap close: drv `round` checks ACC against Σ planted counts over the n calls (gen.c already returns them).

### FIX-7 CONFIRMED (speed: the window's order) — the placement screen is no job; nothing holds J1 on its verdict
span_cards.md:1660 (S2d row): "FIRST STEP: the placement screen, run quiet at the window's start before J1 ...
over the half gate -> HELD, no J1", and "the manifests the timing jobs verify and the screen reads". The
committed jobs (slot/jobs/: 480 prep, 481-486, 489) have no screen job; 481-kit-s2d-J1's `--ready` is
`ready_after` (prep green only), so J1 starts the moment prep is green and the screen, needing prep's J2
manifest, can only run by hand in a gap the queue does not leave (HOLD exists in window.env but no text says
to use it so). Same row still says "J3-J5 chained `after`" beside §3.3's END-chaining (stale wording, doc).
Fix: a screen job between prep and J1 (rc 3 -> J1..J5 answer 77 through ready_after), or §9/§3.3 text naming the
HOLD procedure; drop "chained `after`".

### FIX-8 CONFIRMED (maintenance/design: red at the set's commit) — SLOT-17's resolved gate breaks check C's cards equality
est.py write_draft rewrites each ver-3 card's `gate_e6` from `-` to the policy value (est.py:310-314, per
SLOT-17's ruling "the producer publishes the resolved value"); finder_check.py:488-490 (check C) requires every
committed set's `cards` section to EQUAL its card table's rows of that ver. Repro: synthetic finalized run
(est._synth + the window facts + cell_text.tsv per job), `est.write_draft` -> 38 rows, outcome FULL; its cards
section vs kit-grid.tsv's ver-3 rows: not equal (`30000` vs `-`). So zen4-grid3, committed under
memfn/data/sets as drafted, turns `make test-memfn-finder` red. The fix added a reader-visible write without
tracing the existing reader of the same column ((b)). Fix: check C resolves `-` through policy.tsv for the
comparison (and policy.tsv's header lists that second reader), or the ruling is restated; decide before S2e/S2f.

## PROBED-AND-HELD

- S2933 (G4 FOLD): fx built from the export; `finder_check.py` (check B/C) green, 1,064 checks, 0 failed. Planted
  S2933's SAB_BEFORE/AFTER into a copy of formhash.c (linked ahead of libpcrec.a, traced copy for fxt): rc 1,
  exactly 2 failures "mf_form_hash(settest|rc-words) ... is not the fold of its 3 instances' site texts". Red
  planted, green correct. (Note: the per-instance `foldedit != FORM` checks stay green under that plant; only the
  fold-equality check catches it, so it is the load-bearing one.)
- walk/libc/pair hashes unmoved by the fold (bc7b2e02f06fe955, d7672e87c1dd6d97 as r9 recorded).
- est.py selftest on the export: 6 cases, 0 wrong (complete FULL; never-ran leftover, missing cell, other run id,
  wrong base, id/column disagreement all refused). r9 G3's original repro (identical records, a leftover
  cells.J3.tsv of a never-ran job) now REFUSES the input instead of flipping FULL/REFUSED. Held.
- S2934 (l3) and S2936 (g3), run by `slot/sabotage.sh SCR l3 g3` from the export (2 slot dry runs: control J2 +
  l3 J2; 14:5x, outside 19-01): control J2 dry green, control est self-test green; l3 DETECTED (rc 1, ctl
  SENTINEL miss, "336 subjects, 336 timed calls, 336 misses"); g3 DETECTED (self-test WRONG on the leftover
  case). Red planted, green correct (reach caveat: FIX-4).
- S2935 (g2) without a dry run: `link.render` on the export with S2935's Arm -> "KEY-ARM MISMATCH
  kit.find_byte.libc: the key names ('libc', None), the Arm walk None". Held for form/cls (dims: FIX-2).
- Per FIX-NOW id, by reading the subject (plus the runs above):
  G1 drv gate runs `_time` and `_gate` per subject + sentinel (find, cmp); null `_gate` IS `_time` (count E);
  population line asserted; every launch + ctl gated; manifest (run id, plan, fx, libpcrec, ctl, placement,
  cell_text, L1-L7) verified first by `run` and `screen`; fx cached by inputs' sha; ctl refuses moved inputs.
  HELD (population assert shares plan.build() with link: a missing twin/base is caught only downstream by est's
  need(), which it is). G2 HELD (form/cls). G3 HELD for jobs/plan/floor/run id; FIX-1 for cards/policy.
  G4 FOLD HELD (S2933). G5 HELD (deps from cell_text.tsv; box/isa/libc/gcc from the record; no draft on
  REFUSED). G6 HELD (window facts every job + finalize; CAUSE table first-match; `cancelled` covered; boxqueue's
  --ready 77 ends as outcome=cancelled, scripts/boxqueue:749/448, so J9 and J3 never wait on it). G7 HELD (cards
  + policy one home; null base bytes from facts; CAND_STRIDE/POOL_BYTES `#error` without plan's -D; doubled
  gate) — but see FIX-8. G8 HELD (unknown landing refuses; git rc checked). W1 HELD (scripts committed, stale-copy
  cmp, expect lines) — FIX-3, FIX-7. W2 HELD (ready = ENDED; prep non-green -> 77; J2p 77 on J1 failed/cancelled;
  J3 after J2 and J2p). W3 HELD (Waiter accumulates wait time only). CONTRACT-1/3/4 HELD (§3.4¶1, ¶2a, ¶14a,
  §3.5¶8a, §2.1 `partial`, table row 1; est enforces rules key, L=7, E>0, u>0, W>0). EMIT-3 HELD (c2 instance
  `{X,x}` = case = majority 156/292; link refuses a non-majority instance) — FIX-5 on the classifier. EMIT-4 HELD
  (guard `arm == &runcmp_arm`; settest stated a leaf). CHECKS-3/4/6 HELD (named deps resolve, count EXACT 17;
  `renamed > 0` per instance; edit + foldedit per instance, 10 instances). SLOT-9 HELD (vcls.out stamps sweep
  sha + commit; frozen plan pins vcls.out's sha).
- (c) harness fidelity, one cell per job by reading: the timer's entry (`a->time` in run_n) is the gate's
  (`a->time` in pool_make) over the same seeded pool (gen_subject idx 0..np-1, sentinel never timed); the cell's
  key is the tab.c name of the Arm whose (form, cls) the key named; its dep is the fold in cell_text.tsv from
  the fx that rendered it, pinned by the manifest; the verdict reads the finalized record (FIX-1 excepted).
  Plants: halve the timed loop -> DETECTED (S2934); swap one arm's key -> refused (S2935; dims: FIX-2); two
  identical records with different leftover cells -> refused input (est self-test, S2936).
- Not a finding: `expect groups=N` and the `GROUP done` lines both come from plan.groups(job) and print only on
  rc 0, so the population check is rc 0 restated (a control sharing its source; harmless).

Counts: 1 export build; finder_check 2 runs (1,064 / 1,062+2 red); est self-test 1 run (6 cases); sabotage.sh
1 run (2 rows + 2 controls, 2 slot dry runs); 6 python repros (key dims x3, equal-record x2 trees, draft cards);
1 gcc lowering probe (4 functions); boxqueue/record readiness traced by reading.

## Verdict

**Ready with listed fixes** for the S2d window. Before the window: FIX-1 (est refuses unless the frozen plan's
inputs, cards and policy, match; small), FIX-3 (FROZEN must be the hex sha; one line), FIX-7 (put the screen in
the queue or state the HOLD step). Before the set's commit (S2e/S2f): FIX-8. Next touch or PLAN: FIX-2, FIX-4,
FIX-5, FIX-6. Every r9 FIX-NOW id is closed as ruled, apart from the residues these findings name.
