# m1bfix: M1b's G2 fault, lane report

**Owed runs DONE (2026-10-07 09:16, Mac, under the lock):** G2 `--quick`
checks failed 0 (rc 0; W1 controls fire); test-memfn-arms, -forms and
-manifest rc 0. Merged into lane/memfn-m1b.

Lane `lane/m1bfix`, cut from the kit branch `lane/memfn-m1b` at 6467f6a2.
Mac (gcc-16, clang for the ASan leg). Brief: reproduce G2's red after M1b,
classify it, fix it without moving a pcrec byte, pin it, validate.

## 1. Root cause

**ORIGIN (kit manager, 2026-10-07): an UNSTATED PRECONDITION, latent on
main since R4c (81bc13de).** R4c's offset-skip arm was correct only under a
guarantee pcrec's facts always give at OFS/PRE: `miss` is `n` and no
`floor` is stated. The kit contract (§14.7, §15) does not require that, so
G2 legally built sites pcrec never would. Before M1b those sites were
unreachable, because their RUN term needed the run_cmp hook G2 leaves NULL.
This is not an M1b translation slip, and pcrec's pre-M1b runcmp.c is not at
fault: both failing sites used the memcmp row correctly. No pcrec artifact
was ever affected. The fix closes the contract edge: decline to the generic
row, and refuse loudly at use. Main files it as K96.

**A kit defect in the offset-skip ARM's applicability (`memfn/src/ofsskip.c`
`ofsskip_applies` / `ofs_fn_applies`), not in the run compare.** The arm
writes a function that returns its own `n` parameter on a miss and bounds
its reads by `pos` and `n` only. It accepted any FIND/FUNC/RETURN site,
whatever the site's `miss` value and whether it stated a `floor`. pcrec's OFS
site has `miss` = `n` and no floor (integration.md §15's table: "`s`, `n`,
`lo`, `miss` | `subject`, `n`, `pos`, `n`"), so pcrec never saw it. The
contract makes the miss a value the site owns ("In EXPR and FUNC forms the
miss is a VALUE (`miss`)", §14.1). It also says the kit bounds every TERM
read by `floor` (§14.7, memfn.h `floor`).

Why M1b exposed it: before M1b, a RUN term needed the `run_cmp` hook, which
G2 leaves NULL, so `ofs_fn_applies` declined. With the run compare in the kit,
a G2 RUN predicate that meets the arm's shape (fn_ref set, the scanned
position exact, a table name for each multi-byte set) now selects the arm.
In G2's seed 20261005 population exactly **two** sites do. They are the only
two sites in the whole run that render through ofsskip.

| site | batch | shape | `miss` | floor | what failed |
|---|---|---|---|---|---|
| 1682 | 014 | SET@2 (table) + RUN@7 len 25 exact, scanned at 29 (byte 129), `memcmp` row; hook style 1 (`G2_EV`), via 1 | `n + 5` | `fl` (stated) | every miss answered `n`, not `n + 5` (gcc leg only: batch 14 is outside the ASan sample) |
| 2587 | 021 | SET@1 (table) + RUN@4 len 2 exact `{51,3}`, scanned at 4, `memcmp` row; style 0, via 0, DISCARD | `((size_t)-1)` | `fl` (stated) | every miss answered `n`; **all 11 faults**: layout L with `fl = lo + 2`, the table probe `subject[cand + 1]` at `cand = lo` reads below the floor (SIGBUS) |

The cells: both are **VERIFY terms inside an OFS FUNC** (not STMT, not
VMRUN); the run compare's own rows were correct (`memcmp`, words never
reached); `guard_by_caller` 0; `empty` MISS. The empty-range lines in
`run-*.err` (`n=0 ... res 0`) are the first, not the only, symptom of the
wrong miss. The 2292 ASan-leg failures are site 2587's (batch 21 is in the
QUICK_STRIDE sample). ASan reported no over-read: the faults are under-reads
below a floor that is mapped memory to ASan, caught only by G2's guard page.

**`coverage-missing 1`** is `G2 coverage MISSING: subject axes`. The quick
tier runs alignments 4/16 by design, and run_g2.sh line 341 accounts for it
(`sa`). It is not a failure and not M1b's. It was the same before M1b.

### The floor half and the contract

memfn.h `floor` says "floor <= lo is the CALLER's precondition (RULED
Q-G2-6): the kit bounds term reads by floor, never a candidate or on_cand's
reads". G2's `admit()` clamps `fl` to `lo` only for SKIP and ON_CAND. It
deliberately runs FIND with `fl > lo`, and the generic row honours that
(`c + k >= fl` on every term). Read narrowly, as G2 reads it, Q-G2-6 is about
candidates and on_cand. Read broadly, G2's `fl = lo + 2` instances are outside
the precondition, and the fault is G2's. I did NOT change G2: the brief's
default is a kit defect, and "the kit bounds term reads by floor" is
explicit. Instead the arm declines where it cannot honour a stated floor,
exactly as the generic row would. **For the manager / kit session:** whether
Q-G2-6's precondition is general (memfn.h's wording) or SKIP/ON_CAND-only
(G2's `admit()`) is worth one ruling line. The fix below is right under
either reading.

## 2. The fix (memfn/src/ofsskip.c)

- `ofs_fn_applies`: declines when the definition hooks state a `floor`.
  This is shared with precheck's FUNC parts. pcrec states no floor at OFS or
  PRE.
- `ofsskip_applies`: also needs `miss_is_n(def)`, true when `miss` is unstated
  (pcrec's define hooks) or is the `n` hook's own text.
- The use side refuses loudly rather than mis-rendering: `ofsskip_use`
  refuses a call whose `miss` is not its `n`. `ofs_fn_call` refuses a call
  that states a floor. pcrec's use hooks state neither.
- The header comment states the arm's edge.

A declined site falls to the generic row, which already renders both cells
correctly. G2 has always checked that row.

## 3. The pin (tests/memfn/arm_fixtures.c, pins/arms.tsv, run_arm_pins.sh)

`runcmp_check.py` drives the pcrec CLI and cannot state a site's `miss` or
`floor`. The cell lives in the kit API, so the pin is C5's per-arm fixtures
(the house's arm-pin pattern). A new `render_h` passes `n`/`miss`/`floor`
hooks. There are three fixtures on `ofs-run-pinned`'s predicate:

- `ofs-miss-n`: `miss` stated as the `n` hook's text, so it stays `ofsskip`
  (its def/use bytes equal `ofs-run-pinned`'s);
- `ofs-decline-miss`: `miss` `((size_t)-1)`, so it is pinned to `generic`;
- `ofs-decline-floor`: floor `search_floor`, so it is pinned to `generic`.

Six rows were added (no existing row moved) and `ARMS_ROW_FLOOR` went from 28
to 34. **Sabotage-validated:** with the three conditions reverted in
ofsskip.c and libpcrec rebuilt, `run_arm_pins.sh` gave `checks failed: 8`
("ofs-decline-miss renders through 'ofsskip', its pin says 'generic'", and
the floor fixture's digests moved). Restored, it gave 73 passed / 0 failed.
No S-id was used. S574-S579 remain free.

## 4. Zero-mover proof

I compiled 50 run-bearing corpus patterns with base 6467f6a2 (a `git archive`
build in the scratchpad) and with this tip. They were harvested from
`tests/*/*.rxt`, keeping those whose artifact carries ofsskip, `reqrun`,
`memcmp` or a word compare. Each was compiled at `--engine=dfa` and `vm`,
with and without `-fno-run-overlap`: 200 compiles in all, every `.c`/`.h`
pair compared with `cmp` under identical output names.

**156 identical, 0 differ, 44 refused identically by both** (DFA-ineligible
patterns, same rc and stderr). Of the identical artifacts, 40 carry the
offset-skip function, 94 the pre-check, and 101 a run compare. No pcrec
artifact byte can move: pcrec's OFS/PRE define hooks state neither `miss` nor
`floor` (emit_dfa.c `ofs_site_define`, `req_site` define), and its use hooks
state neither (`pf_emit_ofs`'s call, the pre-check's use).

## 5. Validation (Mac)

| check | result |
|---|---|
| G2 `run_g2.sh --quick` | OWED, §5.1 |
| `tests/memfn/run_arm_pins.sh` (CC=gcc-16) | 73 passed, 0 failed (34 rows, 17 fixtures) |
| `make strict` | clean |
| `make test-memfn-arms` / `-forms` / `-manifest` | OWED, §5.1 |
| zero-mover cmp | 156/156 identical (§4) |

### 5.1 Runs taken under the suite lock

**OWED.** The suite lock was held by lane possarms2 (census+sweeps) from
08:51 through this lane's end. A detached chain (`nohup caffeinate -s
owed.sh`) waits for the lock, takes it (an `owner` file naming m1bfix),
runs `run_g2.sh --quick --keep`, then `make test-memfn-arms`,
`test-memfn-forms` and `test-memfn-manifest` solo, and releases the lock.
Log: `/var/folders/sj/jbcblbpx13n6342cgcfhgbxr0000gn/T//m1bfix/owed.log`. Completion line: `OWED CHAIN COMPLETE`. Per-step lines:
`G2 rc=`, `test-memfn-<x> rc=`. The verdict is `checks failed: 0` in the G2
block and rc=0 on each make step.

The fix's G2 effect is predictable from §1: both failing sites now decline
to the generic row, which G2 already passes on every other site.


## 6. Findings for the kit session (not fixed here)

1. **G2 barely reaches the kit's run compare.** After the fix, no G2 site
   renders through ofsskip. Before the fix, two did, both wrong. The runcmp
   arm (EXPR VERIFY, guard_by_caller) is reached by one site (batch 22,
   `memcmp`). The precheck arm is never reached, because G2 never sets
   `on_miss_leaves`. So "the first time G2 exercises the kit's run compare"
   is three sites, and none of them reaches the `words` row. That is a
   population nobody counts (K35). A G2 floor on per-arm reach, or
   generator bias toward the arms' shapes (fn_ref + table names + no floor
   + miss `n`; `on_miss_leaves`), is the kit session's call.
2. Q-G2-6's scope (§1, the floor half): one ruling line.
