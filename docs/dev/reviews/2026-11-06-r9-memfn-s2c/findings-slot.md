# findings — slot — memfn-s2c
## Findings

Subject 8983c4026 (review tree worktrees/crit-memfn-s2c), slot = docs/design/memfn/span_cards/slot. Probes under
$R/slot (synthetic cells generator $R/slot/tools/gen_cells.py; synthetic, not measurements). All six dry runs
(J1, J2, J2p, J3, J4, J5) run once each, sequentially, run id s2c-dry, rc 0.

### SLOT-1 CONFIRMED (answer, for the set) — the slot's verdict does not read the run record: EQUAL records, DIFFERENT verdicts
`est.py compute` derives "which jobs ran" from the presence of `cells.J*.tsv` files in RUNDIR (est.py:89 `ran =
{x["group"].split(".")[0] for x in cells}`) and the plan and floor from a LIVE `plan.build()` (est.py:82, reading
census0.out, vcls.out, enter/fixtures.tsv from SLOT_TREE at est time). It never reads the record's `jobs`, `plan`
or `floor` sections (read_record keeps only `run` and `jobs`, and `jobs` is unused). The cells carry no run id.
Repro 1 (stale cells): rundir with synthetic cells for every job, `record.py j1`, `record.py finalize` with STATES
J3=wait-timeout (others green) -> two copies eqA/eqB, byte-identical run_record.tsv (sha 5504e43a5b67b8c7, `J3
never-ran wait-timeout`); eqB lacks cells.J3.tsv. `est.py rows eqA` -> `OUTCOME FULL exit 0` (J3's rows priced
from cells the record says never ran); `est.py rows eqB` -> `REFUSED floor:hit.libc (never-ran:J3); floor:hit.walk`.
A leftover cells.J3.tsv from an earlier attempt in the same RUNDIR (run.py writes cells only on success and never
deletes) is exactly this. Repro 2 (live plan): record eqC finalized with the tree's plan (lists the 2 w3 keys
and clause `verify.rc-words.w3`, sha 83b0bd1e981f5146), w3 rows made `null`: `est.py rows` from the tree ->
`REFUSED floor:verify.rc-words.w3 (text)`; the same est.py from a slot copy whose vcls.out lacks w3 -> `FULL`;
record unchanged. Expected (§3.5, Goal 3): the verdict reads the set + the record and nothing else; the record's
`jobs` is "the one input taken as given", cross-checked against the cells. S2e's recompute would refuse case 1
(its never-ran/no-cell cross-check), so the WRONG verdict is the slot's own (the one S2d reports and drafts by).
Fix: est.py reads plan/floor/jobs from the record (finalize before est), refuses a cells file of a never-ran job
and a ran job missing a planned cell; put the run id on every cells file (a header line) and check it.
Effort small. Blast: the window's outcome and draft.

### SLOT-2 CONFIRMED (answer) — `run.py run` times whatever executables are in RUNDIR; the run id it is given is only logged
run.py:90-114: `run(job, rundir, run_id)` uses run_id only in the transcript's `start` line (:96); it times
`RUNDIR/<job>/L<l>/<job>.L<l>` as found, with no check that they were linked under this run id, by this dry run, or
that the dry run completed (link_job refuses mid-way leave launches 1..k-1 of the refused draw on disk; an earlier
`s2c-dry` dry run in the same RUNDIR leaves s2c-dry placements). Only ctl's sha is checked (:29-35). §3.2
READY-8: "the window's own --dry-run (run at its enqueue, with its s2d- id) re-links and re-asserts every launch
under the real id" — nothing ties the timed executables to that re-link. Also the answer gate runs on launch 1
only (run.py:54), not on the six other executables timed. Fix: dry writes a manifest (run id, sha-256 of every
launch executable, placement.tsv sha) and run refuses on mismatch; gate every launch. Effort small.

### SLOT-3 CONFIRMED (answer/design) — the run id, set and code_commit are written ONLY on J1's success path
record.py:52-63 writes `run_id`, `set`, `code_commit` in `j1`; `finalize` (:73-92) writes only
`transcript_sha256`. Repro: empty rundir, STATES `J1 failed, J2 green`, `record.py finalize` -> the record's `run`
section holds only `transcript_sha256 -`: no run id, no set, no code_commit, while `jobs` says J2 ran. The
three-copy compare (§3.5 READY-5 (b)) then has no record run id; est.py's draft header becomes `run	 record:<sha>`
(empty id). Also `J2p never-ran declined-j1b` is written although no (b) verdict exists (record.py:81 maps any
non-green J2p to declined-j1b). Fix: the run id/set/code_commit are WINDOW facts: write them at finalize (or at the
first job), and derive J2p's cause from the record's j1_verdict (b -> declined-j1b, else failed/upstream-failed).

### SLOT-4 CONFIRMED by boxqueue's contract (design; window wedges) — a failed J1 leaves J2p, the `after` chain and J9 pending forever
boxqueue `after KEY` answers 75 while KEY is pending/running/FAILED (scripts/boxqueue:21, :1110-1111);
`record.py ready-j2p` answers 75 while no `j1_verdict` line exists (verified: rc 75 on an absent verdict and on
the J1-failed record above). §3.3 says `patience none`. So one failed J1 (or any failed link of "J3-J5 chained
`after`") leaves its dependents pending at 75 indefinitely, and J9's `--ready` ("0 once none is pending or
running", §3.5) never answers 0: the record is never finalized, contradicting §3.5's "a failed or declined job
still gets its `jobs` row". The job scripts that would resolve it do not exist (SLOT-5). Fix (design): J2p's
--ready answers 77 when J1 ended non-green (read `boxqueue state J1`), the chain uses a "J<prev> ended" readiness
rather than `after`, or J9 treats pending-on-a-failed-upstream as ended.

### SLOT-5 CONFIRMED (charter MISSING) — no job scripts: §3.3's job shape is not implemented
§3.1's table puts "the job scripts" in THIS RUN's harness (S2c); §3.3: each job's `--dry-run` prints `boxqueue:
cap`, `patience none`, `idle-ok`, `est`, `expect groups=N lines=^== s2 GROUP done`, `--ready` is 650's quiet gate,
J9 finalize's `--ready` reads `scripts/boxqueue state`. `grep -rn "expect groups\|patience\|idle-ok\|boxqueue: cap"
slot/` -> nothing; no J1..J5/J2p/J9 job file exists in slot/; nothing produces record.py finalize's STATES file
from the queue's records (finalize reads a hand-made file). `run.py dry` prints "would run ... groups N" only.
Population note: run.py prints `== s2 GROUP done` for every group INCLUDING `J<j>.ctl` and `J<j>.base`, so the
expect N must count those (J2: 3, J2p: 7, J3: 6, J4: 5, J5: 3, J1: 9 by the dry runs). If deferred to S2d, §9
should say so; today S2c's witness "every job's --dry-run green" is met only by `run.py dry`, not by a queue job.

### SLOT-6 CONFIRMED (answer, staleness) — a non-canonical verify class records the CANONICAL instance's hash as its dep
est.py:178-185/219-222: deps = `kit:form.<q[2]>=<FORM hash>` from `build/arm_fixtures --hash`'s `FORM` line, i.e.
the canonical instance (settest c2, rc-words w2). The cells of `verify_cmp.settest.c1.*`, `.cn.*`, `rc-words.w1.*`,
`.w3.*` time the NON-canonical instances, whose hashes differ (`fx --hash`: settest c1 b2abe5278b2f6fa0, c2
206d9992b608b279, cn 189186e257d7fbcb; rc-words w1 0538945cb4a8d9d8, w2 8957c3f88142ab53, w3 19e26b4da50a49ec), and
link.py's cell-text check compares those cells against the FORMCLS hash. So §2.4 READY-8's "the hash the cell-text
check already computes for the row's cells" is false for 4 of 7 verify pairs (8 of 14 verify rows): a kit change
that moves only the c1 or w3 text leaves those rows' recorded dep equal to today's `mf_form_hash(settest)` and they
never read STALE. Design + code both: the dep grammar `kit:form.<id>` has no class. Fix: record the instance
(`kit:form.settest.c1=<hash>` or a `cls` field) and have S2e's pass compare against mf_form_hash_cls; or state the
gap with its trigger. Effort small-medium (grammar touch, S2e pass).

### SLOT-7 CONFIRMED (answer, the window's last step fails) — est.py's draft reads a binary nothing builds, and header keys nothing writes
est.py:179 `fx = TREE/build/arm_fixtures`: `ls $T/build/arm_fixtures` -> No such file (make builds it nowhere:
tests/memfn/run_finder.sh etc. build their own copies in scratch). `est.py draft` therefore dies with "no form
hash" at S2d's end, or someone builds it ad hoc from an unrecorded libpcrec (an implicit input: the dep hash is
then not the hash link.py's cell-text check computed on the timed text, which is printed and never persisted).
est.py:230-234 read `isa`, `box`, `libc` from the record's `run` section; record.py never writes them -> empty
header values in the draft. Fix: link.py persists its per-cell (form, cls, hash) to RUNDIR; est.py reads it; the
record (or finalize) carries box/isa/libc. Effort small.

### SLOT-8 CONFIRMED (design: "one table per slot") — the cards' facts have a second home in plan.py
plan.py:23-29 hard-codes LENGTHS (65536,262144,1048576), LEN, L_LAUNCHES=7, R_ROUNDS=7, GATE_E6=30000, and est.py uses
them for every gate, n, slope and delta (est.py:85,94,103-105,129,139,147,224); kit-grid.tsv's ver-3 rows hold the
same facts and are what the draft publishes (est.py:209-210) and what S2e's recompute reads. A card edit (e.g. a
gate) changes the published card and the recompute but not the slot's own gating: the slot and the recompute
disagree and the slot's verdict was computed under a card it does not publish. The card's `lengths` (the
ESTIMATOR, §2.4 "a card says how its rows are computed") is never parsed by the producer: est.py picks slope/delta
from plan.py's own `est` strings. Same pattern: CAND_STRIDE has three homes (plan.py:30, slot.h:49, link.py:217
literal `plan.LEN // 64`), and the null verify base's run lengths are a hand dict `{"w1": 4, "w2": 3, "w3": 18,
"l1": 4}` (link.py:209) duplicating formhash.c's entry bytes ("USER", "ABC", 18 bytes, "/use"). Fix: plan.py reads
the ver-3 cards (lengths, launches, rounds, gate_e6) and the null base reads L from `--facts`.

### SLOT-9 CONFIRMED (design: second home, and an unreproducible input) — vcls.out is a second census with its own class vocabulary
plan.py:9,40-46 takes the verify (form, cls) population from vcls.out, not census0.out. census0.out's "(2) the
card population" lines carry another class vocabulary for the same sites (`settest cls=set1/set2/setN`,
`rc-words cls=short/long`, `rc-memcmp cls=short`) and other counts (census0 RTE settest 60+395+11 units; vcls
48+290+7 sites), so the tree now has two published classifications of one population, one of which (census0's
`cls`) no reader reads. vcls.py re-derives the kit's text boundaries in python (`words()` mirrors rc_width,
`settest_cls` mirrors kit_set_test's compare count, vcls.py:32-55) — a third home beside runcmp.c/generic.c and
formhash.c's entry rows; no check ties them (a change to rc_width moves the instances' text, not vcls's
classes). vcls.out cites only "sweep.jsonl" (no path, commit or digest of the J0 sweep it read; census0.out's
header names the s2b base 71cad723e), and the sweep lives in a lane scratch dir (art.py:19 names
/var/tmp/.../s2b/j0/sweep.jsonl), so the plan's verify keys are not reproducible from the tree. §7 (rev1 COST-2):
"census0.out ... read by S2c's slot harness when it lists the cells; there is no separate cell manifest". Fix:
fold the text-boundary classes into census0 (one pricer/classifier, §7 FAM-D says census0 is THE tool) or make
census0.out's `cls` column vcls's, and stamp vcls.out with the sweep's sha.

### SLOT-10 CONFIRMED (doc/narrowing) — the walk's `alt` hit rows: §2.5 says they are walk's, the plan drops them
§2.5: "`[rev1.3 S2c-2]` the `walk-set` `alt` rows are `walk`'s"; plan.py:105-112 plans walk `one` only (8 J3
rows: libc one, walk one); `plan.py report` lists no `find_hit.walk.*.alt.*`. §3.7's J3 still counts "walk-set alt"
and defers to "S2c's plan is the record". Defensible on the text (the table walk's control flow never sees which
member hit, so alt = one for the walk), but the design says the opposite of the plan; one must move. Doc.

### SLOT-11 CONFIRMED (design) — two of five `enter` rows do not measure the card's declared regime `die1`
kit-grid.tsv `enter` card subject `artifact die1 g256`; enter/fixtures.tsv: kind 6 (REPORT) has die `-` ("a pass
candidate IS a match"), kind 5's fixture is "NOT row-1-class" ((?m)^\bfoo\b$, chosen because census0's one kind-5
unit ends at its window, no die1). So `enter.6.NONE` times match-report-and-restart cost and `enter.5.NONE` a
non-census pattern, both under a card that says die1. The rows' `source` will say `slot J5`. Fix: state the
regime per row (a card note or a `tags` value) or exclude kind 5/6 until a fixture meets the card.

### SLOT-12 CONFIRMED (answer, box time) — the per-job quiet wait is bounded from the JOB's start, not per wait
run.py:71-88 `wait_quiet(t0, log)` with t0 = the job's start (:98): once a job has run WAIT_BOUND (300 s) of timing,
the first non-quiet per-launch sample fails the job at once (the while loop never executes; logs `wait-timeout`),
discarding all launches. §3.3: "bounded at 5 minutes per job" for the WAIT; "a wait extends its job within the
job's cap". J1 is 5.7 timed minutes by §3.7, so its launch 7 (and J4's at 4.1 min plus calibration) can fail on a
single loaded sample with zero waiting. Also the job's own pinned process holds load1 near 1.0 during its
launches, so the `load1 < 2.0` single sample has half its margin used by the job itself (SUSPECTED effect; 650's
gate shape). Fix: track the accumulated wait, not wall time since start.

### SLOT-13 CONFIRMED (doc vs code) — the re-draw bound is per (launch, arm), and the D149 trigger already fired
§3.2 READY-5: "at most 64 draws per launch executable ... trigger: a dry run that needs more than 8 draws for any
launch". link.py:361-365 bounds each (launch, arm) at 64, so one launch executable may take up to 64 x arms
draws. The dry runs here: J3 launch draws 8,17,14,6,7,8,8; J4 12,11,12,8,15,9,14 (sums per launch, per-arm max 5):
the stated trigger (more than 8 for a launch) is met in S2c's own dry runs and nothing flags it. Either the
trigger means per arm (say so) or it fired (rule it).

### SLOT-14 CONFIRMED (doc) — gen.c's "twins and bases draw the same subjects as their arm" is false for verify bases
gen.c:61-62. The verify subject seed includes `pass` (gen.c:140) and the null base has pass 0, so a p50 arm and
its `base.null.<cls>` draw different subjects; for p0 the rejection sampling over different run/mask bytes moves
the stream after the first candidate, so the candidate offsets differ too. Cost-neutral for the stride loop
(candidates never cross a line), so the delta stays sound; the comment is wrong.

### SLOT-15 CONFIRMED (answer) — the cell-text check compares against the ARM's fields, not the KEY: a key timed with another form's text passes
link.py:286-296: the expected hash is `form_hash(fx, a.form, a.cls)` and the rendered text is `parts(fx, a.form,
a.cls)` — both from the same Arm fields; the key string (`kit.find_byte.libc`) is never parsed. §3.2 says the
check is "mf_form_hash(<the key's form token>)" and guards the KEY-to-ROW mapping. Plant (scratch copy
$R/slot/plantK, plan.py J2: `Arm("kit.find_byte.libc", "J2.byte", "find", "walk", ...)`), `run.py dry J2` -> rc 0,
"cell-text: 4 cell TUs, every site-text hash equals its key's form hash", gate ok (hits come from the same facts):
SILENT. The row `find_byte.libc` would be the walk's cost, and est.py's draft would record `deps
kit:form.libc=d7672e87c1dd6d97` (from the KEY, est.py:221) for walk-timed cells. Sabotage (k) plants in link.py's
`parts()` call, so it cannot see this class. Same for verify cls (key `.c1`, Arm cls `c2`). Fix: derive (form,
cls) from the key's tokens (`kit.<q>.<form>[.<cls>]`) in link.py and compare both the render and the hash
against them; add a plant in plan.py to sabotage.sh. Effort small.

### SLOT-16 CONFIRMED (design, seam round trip) — the run record and the cells files are not self-contained
Principle 9 (written as text, read back by another process with nothing else). Implicit inputs found:
- cells.J*.tsv: no run id, no executable/placement identity, no ctl sha, no N per point (N lives in
  RUNDIR/<job>/L<l>/N.*), `events` taken from plan.py's Arm (run.py:125), never from the answer gate's count.
- run_record.tsv: `plan`/`floor` are plan.build() AT FINALIZE (live census0.out, vcls.out, enter/fixtures.tsv via
  SLOT_TREE or the slot's own path), not the plan the links used; `code_commit` = env CODE_COMMIT else `git -C TREE
  rev-parse HEAD` at J1's end (run.py:150); `jobs` from a hand STATES file (record.py:74), no producer; no ctl
  sha, no gcc version (the set header's `gcc 15.2.0 -O2 ...` is a literal, est.py:233, never read from `gcc
  --version`; it is 15.2.0 on this box today), no box/isa/libc (SLOT-7), no sha of census0.out/vcls.out/fixtures.
- run.py: MAIN hard-coded `/home/pcrec/projects/pcrec` (boxqueue running dir, scripts/boxlock), /proc/loadavg,
  BQ_JOB, CPU 7 (sibling 15 named, never checked: `SIB` unused, run.py:22).
- link.py/art.py: TREE/build/libpcrec.a and TREE/build/pcrec at dry time (unrecorded), artifacts and `.exp`
  expectations CACHED in RUNDIR/art by pattern sha / existence (art.py:205-210, :306-318): a rebuilt pcrec or an
  edited fixture in a reused RUNDIR keeps stale text and stale expectations; the bench checkout (sha-pinned: good).
- est.py: TREE/build/arm_fixtures (absent), TREE/memfn/data/cards/kit-grid.tsv, TREE/tests/knowledge/ks_ref.py.
Equal records, different verdicts: SLOT-1 (two constructions, byte-identical records). Fix shape: the record's
`run` section carries every window fact (run id, code commit, ctl sha, executable manifest sha, gcc version,
box/isa/libc, input shas), finalize writes plan/floor from the dry run's frozen plan file, every cells file
starts with the run id, and est.py reads only RUNDIR.

### SLOT-17 SUSPECTED (ruling: R-35 (e)) — the gate default has two homes, neither the kit policy table
R-35 (e): "z, the gate default and MATERIAL are POLICY ... they live in one kit policy table outside the sets".
gate_e6 30000 sits on every kit-grid@3 card (published in the set's `cards`) and again in plan.py GATE_E6 (the
value the slot actually gates by, SLOT-8). If (e)'s "gate default" is this gate (design §2.4 calls it "grid1's
UNMEASURED DEFAULT (D149) carried"), the cards should name it from the policy table, or the design should state
why a card column is not "the gate default" (§0 row 5 discusses only z). Confirm by main's reading of (e).

### SLOT-18 CONFIRMED (maintenance, D149) — estimator primitives copied inside the slot; pad range unlabelled where it lives
j1_rule.py:11-29 re-implements rhafz/isqrt_rn/med/sp2 with K_TRIM as a bare literal `1723000` (est.py:16 names
it); est.py states its arithmetic "is drill.py's (the same text implemented literally)" — a third copy beside
drill.py/j1_drill.py. The slot is one producer; its own two copies can drift apart silently (only the S2e
recompute would notice, after the window). link.py:13-14,229 the pad range P = 16 x (1 + draw mod 255) is
labelled UNMEASURED in the design (§3.2) but not at the code site (D149: "a comment where it lives").

## Charter check (§9 S2c), each item PRESENT / MISSING / UNEXERCISED
Content:
- formhash entry table + renderer entry (mf_form_site_text/split, mf_form_hash_cls): PRESENT, exercised (6 dry
  runs: 1+4+19+18+28 cell TUs; walk/libc hashes unmoved vs base: bc7b2e02f06fe955 / d7672e87c1dd6d97 both).
- kit-grid@3 cards (4 rows): PRESENT; read by the slot only to COPY into the draft (SLOT-8), never parsed.
- check C's deps guard on card rows, floor 17: PRESENT (finder_check.py CARD_FORMDEP_FLOOR = 17); not run here
  (make-only).
- measures.md §3.4-§3.5 + §2.2¶5, measure_sets lines: PRESENT (diff); not this lens.
- arm_fixtures ids[] / check_hash resolve list with every new id: PRESENT (`fx --hash`: pair, settest, rc-words,
  rc-memcmp resolve; 10 FORMCLS instances).
- slot: driver, generator, per-launch link + placement (run id in the seed: seed_pad hashes run_id), bounded
  re-draw, ctl, estimator, j1_rule.py, record writer, sabotage.sh, movers.py: PRESENT. The estimator and record
  have no committed exercise (I drove them on synthetic cells); movers.py UNEXERCISED by charter (S2e runs it).
- the job scripts (§3.1 "the job scripts", §3.3's job shape, J9's finalize readiness): MISSING (SLOT-5).
- dry runs of every job: PRESENT, exercised (J1, J2, J2p, J3, J4, J5: rc 0); answer gate on launch 1 only.
- the placement screen: PRESENT (run.py screen); its witness "unit noise under the half gate" is UNMET at S2c
  (8.56 % on a loaded box, ruled NO READING and moved to S2d's first step, rev1.3 S2c-3); not run here (forbidden).
Witness:
- every --dry-run green incl. placement constraints, ctl sha, gate on counts AND positions: PRESENT, exercised.
  Placement constraints are VACUOUS for J2p (all objects 64-aligned, need 1: draws 0 in every launch) per the
  S2c-1 ruling.
- check C's guard over every card table, 17: PRESENT (not run: make).
- sabotage.sh every slot-local row DETECTED: exercised here, 5/5 DETECTED + control green (34.9 s). (k) fires
  first on the CTL build's walk TU, not on J2's arm; SLOT-15 is the class it cannot see.
- R-MS3's two fixtures per new id: PRESENT for the CANONICAL instances only (TEXT pair/settest/rc-words/rc-memcmp
  rename = FORM hash, edit moves); the non-canonical instances the cells time (settest c1/cn, rc-words w1/w3)
  have none: UNEXERCISED (and their hash is not recorded, SLOT-6).
- ids pairwise distinct: PRESENT (check_hash over FORMCLS instances; 10 distinct hashes in `fx --hash`).
- every cell's site-text hash = its key's form hash: PRESENT but compares the ARM, not the key (SLOT-15).
- run record's two writes dry-run (J1's, J2p --ready on absent/a/b/c, finalize): no committed exercise in the
  tree (UNEXERCISED in-tree); exercised here: absent 75, a 0, b 77 (`j1_verdict b widths 64`), c 0; finalize
  works on a hand STATES file and exposes SLOT-3.
- all under run id s2c-dry: PRESENT (sabotage.sh and the dry runs).
Sabotage (j)..(o): (j),(j2),(k),(l1),(l2) DETECTED here; (m),(n),(o) are S2930-S2932 (not run: mech).

## Ruling check
- D77 (no card without a reader; build under measurement): cards and keys are census-scoped (census0 + vcls) and
  every key has row 1 as reader. Two departures: `enter.5.NONE`'s fixture is not row-1-class (SLOT-11), and the
  verify classes are scoped by vcls.out, a second census (SLOT-9). movers.py is built ahead of its S2e use but is
  in S2c's charter.
- D149: labelled: MAXDRAW 64, WAIT_BOUND 300, CAND_STRIDE, GATE_E6. Unlabelled at the code site: the pad range
  (SLOT-18). The MAXDRAW trigger ("more than 8 draws for any launch") is met by S2c's own dry runs (SLOT-13).
- D157 (facts, not methods): holds for the slot; the entry table's `row` column (the kit row the facts must
  reach) is kit-internal, never on a pcrec seam.
- D174: no caller-facing name added by the slot; the spec hunk's examples use key spellings (data), not mechanism
  names. Holds.
- D186: J1's (b) needs "beats on >= 5 of 8 and loses on none" = a unit change with no losing regime; agrees.
  add. 2: the set takes the fresh id zen4-grid3 (record `set zen4-grid3@1`): agrees. add. 2 C9 ("SIMD-form cards
  join stage 2") is narrowed by D188 add. 1's hold (J6, S2g): the code times no SIMD form, agrees with the design.
- D188 (+ add. 1): no SIMD level is timed (-march=x86-64, scalar), so (c) never arises; facts (a)/(b) are not
  recorded by the slot (deferred to PROVENANCE at S2e, §2.7). The J1/enter artifacts' MEMFN_FORMS stamp is never
  read, so (b) for the timed artifacts is asserted by construction, not observed. Agrees, thinly.
- R-35: (b) timing in a cleared window — run.py has no time-of-day guard (window scheduling lives in the missing
  job scripts, SLOT-5); (c) DEFAULTS at S2e, (d) cell-less embed: S2e's, not S2c's; (e) see SLOT-17. Item 1's
  "each form ... scalar and SIMD", memchr-back, derived noise by quadrature: narrowed by the design (§10 items
  8-10), and the code follows the narrowed design.

## Standing questions
SIBLING OF A FAMILY. This is at least the fifth hand-built slot harness: kit_proof/measure/650-covertime-slot
(cdrv.c, gen_subjects.py, measure.sh, read.py: the job-shape template), r17b_prime/{b3a,b3b,b4p,fdb1,fdb2,
grid2read}, studies/simd1 (harness.c, findall.c), probes/rq4. Each re-writes a driver, a seeded generator, a
median-of-rounds reader and a verdict; inside span_cards the estimator now exists as drill.py, j1_drill.py,
est.py and j1_rule.py (SLOT-18) and will exist again as S2e's recompute (by design, independent). movers.py is
an acknowledged copy of m0build's census with a ruled replacement (`emit_sweep.py --data measures`, §10 item 12).
GENERAL FORM + UNLOCKS. The general form is measure_sets §7.1's own: an owner supplies (cards, probes) and ONE
driver runs plan -> link/place -> gate -> time -> cells -> record -> verdict. Concretely, the slot's
plan.py + link.py + drv.c are already that driver with the cards and probes hard-wired; reading the ver-3 cards
(SLOT-8) and the key tokens (SLOT-15), and making the record the plan's frozen copy (SLOT-1/16), would make it a
card interpreter. Unlocks, each with its trigger: (1) S2g/J6 (SIMD) reuses the same driver with a per-variant
target column — trigger: [XARCH-DEV]'s go; (2) a second box's set (Mac / Zen 1) is the same run with another
`class` — trigger: the first priced row needing a non-zen4 target; (3) M3's pcrec-measure starts from this driver
ported to C rather than from scratch — trigger: the second window that would reuse est.py (a REFUSED zen4-grid3
re-run counts), at which point the copies become a cost; (4) the record-as-frozen-plan makes the recompute and the
slot read ONE plan, closing SLOT-1 by construction.

## PROBED-AND-HELD
- Six dry runs (J1 16.3 s, J2 2.3 s, J2p, J3, J4, J5), run id s2c-dry, sequential, rc 0: cell-text 70 TUs
  equal their (form, cls) hashes; answer gates 0 misses on 1+4+19+18+35+15+48 arms (launch 1); ctl sha
  c17c56ed... identical across the six jobs; per-arm draws max 5 (bound 64).
- sabotage.sh: control green, (j) (j2) (k) (l1) (l2) DETECTED, 5/5, via their stated detectors.
- plan.py vs §2.5/§1 Goal 2: 38 rows, 30 floor lines over 18 clauses; the unit group holds walk + twin only;
  every find form has a random hit clause; pair clauses `unless-j1-b`; enter NONE per census kind (1,3,4,5,6);
  verify clauses per vcls pair (7); the walk-set fold has no key (S2c-2). Bases on the job's base group.
- Form hashes: walk/libc unmoved base vs subject; 10 instances pairwise distinct; canonical instance = FORM line.
- record.py: J2p --ready absent 75 / a 0 / b 77 / c 0; j1_rule (b) on a constructed width-64 win (8 of 8),
  (c) on 7 of 8.
- est.py on synthetic cells: FULL with 5 drifts kept; one w3 clause null -> REFUSED floor:verify.rc-words.w3 (text).
- §3.4 arithmetic in est.py (rhafz, isqrt_rn, lower median, trim ties later, sp2 K_TRIM, slope, delta per E,
  ctl normalization, anchor W, aa, NULL rule over the trimmed six, drift with K_MED): read against §3.4/§3.5,
  agrees.
- gen.c: E = len/gap exactly; periodic at k*g + g-1; random distinct positions; miss bytes exclude every find
  form's members; the enter/J1 expectations are python re's, independent of the artifact.
- Budget: ~0 pattern compiles of my own (the dry runs' artifacts only); 7 dry runs + 6 inside sabotage.sh.
