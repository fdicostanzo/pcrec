# s2cfix2 report: review r9's fix check, FIX-1 to FIX-8 (span_pick S2c, lane/memfn-s2c)

Lane s2cfix2 (opus), worktree `worktrees/s2c`, branch `lane/memfn-s2c`. Subject: the eight leftovers in the
"Fix check" section of `docs/dev/reviews/2026-11-06-r9-memfn-s2c.md` (critic text and repros:
`docs/dev/reviews/2026-11-06-r9-memfn-s2c/fixcheck.md`), all RULED FIX-NOW. Scratch:
`/var/tmp/pcrec-pcrec/scratch/memfn/s2cfix2/`. Nothing queued, no timing run, no `make test`, no mech.

## Summary

- All eight fixes are in. Each critic repro was re-run against the fix and its result is quoted below.
- **FIX-1.** The frozen plan pins the ver-3 card rows and the policy rows verbatim. `record.py finalize` copies
  them into the run record (sections `cards` and `policy`) with the two tables' sha-256 (`cards_sha256`,
  `policy_sha256`). `est.py` builds its cards, lengths, launches, rounds, units and gates from those rows
  only. The critic's repro now gives `('FULL', 0)` under the live gate 30000 AND under a live gate 300, over
  the same record and cells (sha `f9187b76…`).
- **FIX-2.** `plan.DIM_FIELD` is the one table from each card dim to its Arm field. `link.render` parses every
  key token by the card's `dims` and refuses on any mismatch. Both of the critic's repros now refuse.
- **FIX-3.** `jobs/common.sh` resolves FROZEN to its full sha (`CODE_COMMIT`). A non-hex FROZEN refuses at
  `--dry-run`.
- **FIX-4.** S2934 plants the arms' TUs only. `ctl` gates green, then the J2 LAUNCH gate refuses. The
  control's est output is now `control.est.out`.
- **FIX-5.** `vcls.py` classifies by gcc's lowering: `alu1` is one ALU op plus one compare (a single-bit pair
  or an inner range), and `cmp2` is everything else. The new c2 counts are **alu1 217, cmp2 75 of 292**. The
  `{X,x}` instance is `alu1`, so the instance shape is still the majority.
- **FIX-6.** The driver's round checks ACC against the planted counts on every point (`ROUND MISS`, exit 3).
  The dry run also runs `drv check` (the round's code, each subject once, population asserted) on `ctl` and
  every launch.
- **FIX-7.** The placement screen is now the queue job `480-kit-s2d-screen`: after the prep, and quiet-gated.
  Every timing job's `--ready` waits for its verdict, and a non-green screen makes them answer 77.
- **FIX-8.** The draft writes the cards as the record pins them, with the declared `-`. Check C's cards
  equality holds on a synthetic FULL draft; the pre-fix code fails it. The value a `-` took lives in the
  record's `policy` section. `measures.md` §3.5¶2 says so.
- Sabotage: three new slot-local rows, (f1) S2937, (f2) S2938 and (f6) S2939. All 11 slot rows are DETECTED,
  and each new row is green when reverted. No emitted pcrec byte moves (emit_sweep spot: 0 movers).

## Fixes by finding id

**FIX-1** (`est.py`, `plan.py`, `record.py`; span_cards §2.4, §3.5 "The run record" `[rev1.3 r9fc-FIX-1]`)

What changed:

- `plan.py` has one card parser over field rows (`parse_cards`, `parse_policy`, `card_facts`). It serves the
  live tables at the dry run and the record's pinned copies.
- `frozen_text` adds the sections `cards` (the ver-3 rows) and `policy` (verbatim).
- `record.pin` (called by finalize and by est's `_synth`) writes `plan`, `floor`, `cards`, `policy`,
  `cards_sha256` and `policy_sha256`. It refuses a frozen plan with no pins.
- `est.read_record` refuses a record without the pinned values or their shas. `compute` and `write_draft`
  read `rec["card"]` and `rec["facts"]` and never `plan.CARD`, `plan.LENGTHS` or `plan.L_LAUNCHES`.
- Two new self-test cases: "a record pinning no policy values" (refused), and "live card/policy edit after
  the run" (the outcome must equal the previous case's over byte-equal inputs while `plan.CARD`'s gates are
  300).

Repro re-run (`scratch/s2cfix2/fix1.py`: `est._synth`, then 4 of 7 unit-twin launches x1.004 in `cells.J2.tsv`,
`compute` under two `SLOT_TREE`s):

```
live policy gate_default_e6 30000; outcome ('FULL', 0); unit noise 4000; record+cells sha f9187b76dda734b9
live policy gate_default_e6 300; outcome ('FULL', 0); unit noise 4000; record+cells sha f9187b76dda734b9
```

Before the fix the second line was `('REFUSED', 3)`. The finalize witness on the dry-run window pins
`cards_sha256 5bd523c0…` and `policy_sha256 08a81e4b…`, which are the files' sha-256.

**FIX-2** (`plan.py` `DIM_FIELD`, `key_dims`, `key_arm_mismatch`, `key_form`; `link.render`; span_cards §3.2
`[rev1.3 r9fc-FIX-2]`)

What changed:

- `key_dims` reads a row key through its card's `dims`. A wrong token count, or a quantity with no card,
  refuses.
- `key_arm_mismatch` compares each dim's token with the Arm field `DIM_FIELD` maps it to (form, landing,
  split, gap, cls, pass, kind, entry). A dim with no line refuses.
- `render` refuses KEY-ARM MISMATCH and names every disagreeing dim. `key_form` now reads (form, cls) through
  `key_dims`.
- All 145 planned arms agree.

Repro re-run:

```
link: KEY-ARM MISMATCH kit.find_hit.libc.periodic.one.256: dim landing: the key names periodic, the Arm random; dim split: the key names one, the Arm alt; dim gap: the key names 256, the Arm 1024
link: KEY-ARM MISMATCH kit.verify_cmp.settest.c2.p0: dim pass: the key names p0, the Arm p50
```

**FIX-3** (`jobs/common.sh`, `489-kit-s2d-J9`, `window.env.example`)

What changed:

- `common.sh` sets `CODE_COMMIT` to `rev-parse --verify "$FROZEN^{commit}"` when FROZEN is hex.
- `check_inputs` refuses a non-hex FROZEN or one that resolves to no commit, and compares HEAD with the full
  sha.
- J9 passes `$CODE_COMMIT` to finalize.

Repro re-run (a scratch copy of the jobs with its own `window.env`):

```
FROZEN=lane/memfn-s2c  -> FROZEN (lane/memfn-s2c) is not a hex object name (a commit sha, never a ref name)   rc=1
FROZEN=<short sha>     -> J2 --dry-run rc=0; J9 --dry-run: would run ... record.py finalize ... s2c-dry 64695edeb3db804b9b28aec0b348fefe6fe656e4 ...
```

**FIX-4** (`sabotage.sh`)

What changed:

- (l3) now patches `build_objs` in the copy's `link.py`. A job other than `ctl` compiles the halved `_time`
  loop, and `ctl` compiles the unplanted text.
- `want` names the kit arm: `GATE MISS kit\.find_byte\.walk ... SENTINEL ... timed 0, planted 1`.
- `dry` takes an output name. The control's est self-test writes `control.est.out` and `run.control.est`.

Re-run: l3's output shows `ctl gate: == s2 GATE ok`, `ctl round check: ... ok`, then `run: THE ANSWER GATE refused
.../run.l3/J2/L1/J2.L1` with `GATE MISS kit.find_byte.walk len 65536 subject 0 SENTINEL: found 1 ... timed 0,
planted 1`. `control.out` (the J2 dry run, ending `would run ... groups 3`), `control.est.out` (`== est SELFTEST
ok`), `run.control/` and `run.control.est/` all survive.

**FIX-5** (`vcls.py`, `vcls.out`, slot `CLAUDE.md`; span_cards §3.2 `[rev1.3 r9fc-FIX-5]`)

What changed:

- `shape()` now returns `alu1` (two singletons one bit apart, or one inner range) or `cmp2` (anything else).
- The pre-change script reproduced the committed `vcls.out` byte for byte before the edit (the control).

The re-run over the same sweep (sha `b88599f6…`, commit `71cad723e`) gives:

```
DEF  shape settest c2.alu1 1      DEF  shape settest c2.cmp2 1
RTE  shape settest c2.alu1 216    RTE  shape settest c2.cmp2 74
```

c2 is alu1 217 and cmp2 75 of 292. By spelling it was case 156, pair 79, range 53, other 4: 8 pairs were single-bit
non-case. `plan.shape_majority('settest','c2')` = `alu1`, and J4's dry run is green, so the `{X,x}` instance is
the majority's.

gcc 15.2 probe, `-O2 -march=x86-64 -mtune=generic` (`scratch/s2cfix2/low.c`):

- `[0-9]` is `subl $48; cmpb $9`.
- `{@,`}` is `andl $-33; cmpb $64`.
- `{A,b}` is two `cmpb`.

One residual against the ruling's wording. The four `cmp2` sites that are not pairs are `[^\n]` (2) and
`[^a]` (2), each an edge range plus an edge range. Their complement is one byte, and gcc lowers them to ONE
`cmpb $10; setne`, with no ALU op. Following the ruling's enumeration they are classed `cmp2`. They do not move
the majority either way (217 or 221 of 292). This is noted for the ruling; the instance is unchanged.

**FIX-6** (`drv.c`, `run.py`; span_cards §3.2 "The answer gate" `[rev1.3 r9fc-FIX-6]`)

What changed:

- `pool` keeps each subject's planted count (`ec`).
- `timed()` wraps `run_n`. It computes the planted sum from the pool (call k reads subject k mod np) and
  prints `ROUND MISS` on a mismatch.
- `round` exits 3 on any miss. Field 7 is now the point's own ACC.
- `drv check` runs the round's code with N = the pool size per point and prints
  `== s2 ROUND CHECK ok: P points, C calls, 0 misses`. `run.py dry` asserts that line on `ctl` and every
  launch, and `run`/`screen` print the round's stdout on failure.

Repro re-run (the critic's "plant `k < n / 2` under K_CMP, J4 dry"; before the fix it was green):

```
f6  DETECTED (J4 dry run rc 1: ROUND MISS kit.verify_cmp.rc-memcmp.l1.p50 len 1048576: 16 calls, ACC 65814, planted 131232)
```

Limit (stated in §3.2): ACC is a sum of counts, so it sees skipped calls only where the subjects' planted counts
differ, as in p50 verify and landed find. A p0 or miss-only pool plants 0 everywhere and cannot show the miss.
The answer gate's sentinel already covers a short `_time` loop there.

**FIX-7** (`jobs/480-kit-s2d-screen` new; `jobs/common.sh` `ready_prep`/`ready_after`; `481`, `489`; `run.py
screen`; span_cards §3.2, §3.3, §9 S2d `[rev1.3 r9fc-FIX-7]`)

What changed:

- `run.py screen` takes the quiet gate (one `Waiter`, transcript lines `screen\tquiet...`, exit 5 on
  wait-timeout).
- The screen job is ready on prep green (77 on a non-green prep). Its `--dry-run` declares `idle-ok`,
  `est 120` and `expect screens=1 lines=^== s2 SCREEN unit noise_e6 `.
- `ready_after` (every timing job) waits for the screen. On green it continues, on failed or cancelled it
  answers 77 (HELD), otherwise 75.
- J9 waits for the screen to end.
- §9 S2d's stale "J3-J5 chained `after`" now reads "chained by END (§3.3)".

Re-run with the queue stubbed in `common.sh`:

```
screen=green -> J1 --ready rc=0
screen=failed -> J1 --ready rc=77   (kit-s2d-screen ended non-green: ... HELD, never)
screen=running -> J1 --ready rc=75
prep pending -> screen --ready rc=75
```

**FIX-8** (`est.write_draft`; `kit-grid.tsv`, `policy.tsv` header text; span_cards §2.4; `measures.md` §3.5¶2)

What changed:

- The draft's `cards` section is the record's pinned rows, verbatim, so it keeps the declared `-`.
- The `policy.tsv` header now names both readers (the slot's dry run and record, and check C's equality).
- `measures.md` §3.5¶2 now states that a card stating `-` takes the value the run record pins.

Repro re-run (`scratch/s2cfix2/draftc.py`: `est._synth`, window facts, a `cell_text.tsv` per ran job,
`est.write_draft`, then check C's own comparison from `finder_check.py` `read_sections`/`read_cards`):

```
fix:      draft ... 38 rows, 826 cells, outcome FULL; check C cards: EQUAL (4 rows vs 4)
pre-fix:  (88a47cff8's slot, same script)              check C cards: NOT EQUAL (4 rows vs 4)
```

## Sabotage

Slot-local rows in `docs/design/memfn/span_cards/slot/sabotage.sh`. These are not mech rows: no make suite runs
their detectors. Their ids are the kit's (§R1.3 r9fc).

| row | id | plant | detector | planted | reverted |
|---|---|---|---|---|---|
| (f1) | S2937 | `est.py`: a cost row's `G` from `plan.CARD` (live) instead of the pinned `card` | est self-test "live card/policy edit after the run": `WRONG moved (REFUSED exit 3 (the previous case's: FULL exit 0))` | DETECTED | green: the control's self-test, `9 cases, 0 wrong` |
| (f2) | S2938 | `plan.py`: J3's find_hit Arms built with `landing="random"` (form and class kept) | J3 dry run: `link: KEY-ARM MISMATCH kit.find_hit.libc.periodic.one.256: dim landing: the key names periodic, the Arm random` | DETECTED | green: J3 dry run rc 0 (`dryall/J3.log`) |
| (f6) | S2939 | `drv.c`: `run_n` loops `n / 2` for K_CMP arms | J4 dry run: `ROUND MISS kit.verify_cmp.rc-memcmp.l1.p50 ...` | DETECTED | green: J4 dry run rc 0, `ROUND CHECK ok: 35 points, 560 calls` |
| (l3) | S2934 | re-aimed (FIX-4): arms' TUs only | J2 LAUNCH gate, `ctl` green first | DETECTED | green: control J2 |

The full run is `sabotage.sh scratch/s2cfix2/saball`, all 11 rows (log `scratch/s2cfix2/saball.log`):

```
control   J2 dry run green
control   est.py self-test green
j   DETECTED (J2: link: REFUSED: J2 launch 7 arm kit.find_byte.walk: 64 draws, the cross-launch constraint ...)
j2  DETECTED (J2: link: REFUSED: J2 launch 1 arm kit.find_byte.walk#b: 64 draws, the per-launch constraint ...)
k   DETECTED (J2: CELL-TEXT MISMATCH ctl: site text d7672e87c1dd6d97, ... (walk -) bc7b2e02f06fe955)
l1  DETECTED (J3: GATE MISS base.libc len 1048576 subject 0 SENTINEL: found 0 ... timed 0, planted 1 ...)
l2  DETECTED (J3: GATE MISS ctl len 65536 subject 0 SENTINEL: found 1 sum 65536 ... timed 1, planted 1 sum 65535 ...)
l3  DETECTED (J2: GATE MISS kit.find_byte.walk len 65536 subject 0 SENTINEL: found 1 ... timed 0, planted 1 ...)
g2  DETECTED (J2: link: KEY-ARM MISMATCH kit.find_byte.libc: dim form: the key names libc, the Arm walk)
g3  DETECTED (est: selftest leftover cells of a never-ran job WRONG ok (REFUSED exit 3))
f1  DETECTED (est: selftest live card/policy edit after the run WRONG moved (REFUSED exit 3 (the previous case's: FULL exit 0)))
f2  DETECTED (J3: link: KEY-ARM MISMATCH kit.find_hit.libc.periodic.one.256: dim landing: ...)
f6  DETECTED (J4: ROUND MISS kit.verify_cmp.rc-memcmp.l1.p50 len 1048576: 16 calls, ACC 65814, planted 131232)
== slot sabotage: 11 DETECTED, 0 MISSED of 11 rows
```

(g2) S2935 is now refused by FIX-2's per-dim message, and its `want` still matches. The unplanted control's J2
dry run and est self-test are green, so every row is green when reverted.

## Validation

All runs were light and done before 19:00. No timing run, no `make test`, no mech, nothing queued.

- `make -j16`: nothing to rebuild (no C under `src/` changed).
- `make strict`: `whole tree compiles clean with -Werror -Wshadow`, rc 0.
- `make test-memfn-finder`: rc 0, `checks passed: 3272, checks failed: 0`, `check C: 17 cards with a kit:form.
  dep` (log `scratch/s2cfix2/finder.log`; no `*** [test-` line).
- `bash tests/registry/limits_check.sh`: `checks passed: 39, checks failed: 0`.
- `est.py selftest`: `== est SELFTEST ok: 9 cases, 0 wrong`.
- Slot dry runs of every job, `run.py dry J RUNDIR s2c-dry` (`scratch/s2cfix2/dryall/`): J1 J2 J2p J3 J4 J5 all
  rc 0. Each has a gate line and a round-check line on all seven launches:
  - J1: 48 arms and points, 48 calls.
  - J2: 12 points, 1344 calls.
  - J2p: 23 points, 944 calls.
  - J3: 18 points, 288 calls.
  - J4: 35 points, 560 calls; settest c2 tagged `-`, the instance is the majority shape.
  - J5: 15 points, 15 calls.
- Finalize witness on that dry-run window (states green/green/cancelled/failed/none/wait-timeout):
  `== s2 FINALIZE ...: 6 jobs (2 ran), 38 plan keys, 30 floor lines, 4 cards, 1 policy rows`.
- Job-script `--dry-run`s under run id `s2c-dry`, FROZEN = the lane's HEAD, from a scratch copy of `jobs/`:

JOBDRY_RESULT

- Synthetic FULL draft through check C: EQUAL (FIX-8 above).
- emit_sweep spot, `--ref 88a47cff8 --bin build/pcrec --no-corpus --patterns-file` (s2c's 159 patterns), streams
  c-default, c-vm, emit-ir, facts: self-check passed. Real run **movers=0, asymmetric=0** on every stream,
  `emit_sweep: DONE rc=0` (`scratch/s2cfix2/emit/sweep.log`).

## Gate jobs

These are in scratch `/var/tmp/pcrec-pcrec/scratch/memfn/s2c/jobs/`. Nothing was queued.

- `474-kit-s2c-slotsab`: rows j j2 k l1 l2 l3 g2 g3 **f1 f2 f6**, `expect rows=11
  lines=^(j|j2|k|l1|l2|l3|g2|g3|f1|f2|f6)  DETECTED ` (was 8).
- `473-kit-s2c-mech`: ids unchanged (14). The header names S2937-S2939 as slot-local. `rows_for.sh` over this
  lane's data and spec edits (`kit-grid.tsv`, `policy.tsv`, `measures.md`) selects only S2931, which is
  already there, and its anchor row is untouched.
- 470, 471 and 472 are unchanged. 471's `test-memfn-finder` pin ("count EXACT 17") still holds.
- S2d job dir `.../s2c/jobs/s2d/`: every job script and `common.sh` is re-copied from the tree, and the new
  `480-kit-s2d-screen` is added. `window.env` was left untouched; my session could not read it (permission
  denied).

## Charter-vs-committed checklist

- [x] FIX-1 (answer): the record pins the card and policy rows with their sha-256; est reads only them; self-test case; S2937
- [x] FIX-2 (answer): one `DIM_FIELD` table; render parses every key token and refuses a mismatch; S2938
- [x] FIX-3: FROZEN resolved to its full sha; non-hex refuses at dry run; J9 passes the full sha
- [x] FIX-4: S2934 plants the arms' TUs only (a LAUNCH gate refuses); the control's est evidence keeps its own names
- [x] FIX-5: vcls by lowering (alu1 / cmp2); text corrected (vcls.py, slot CLAUDE.md, span_cards §3.2); re-run: c2 alu1 217, cmp2 75 of 292, the instance shape is the majority (residual: 4 one-byte complements, noted, not reclassed)
- [x] FIX-6: drv's round checks ACC against the planted counts; `drv check` in the dry run; S2939
- [x] FIX-7: the placement screen is job `480-kit-s2d-screen` (S2d's first after prep); J1-J5 readiness waits on its verdict
- [x] FIX-8: the draft writes the cards' declared gate (`-`); check C's equality holds on a synthetic FULL draft
- [x] Sabotage S2937-S2939: red when planted, green when reverted
- [x] Design text marked `[rev1.3 r9fc-<id>]` with §R1.3 rows; spec hunk `measures.md` §3.5¶2 (cited by section)
- [x] Gate jobs 470-474 and the S2d job dir updated; nothing queued
- [x] `s2cfix_deliver.txt` committed unchanged
