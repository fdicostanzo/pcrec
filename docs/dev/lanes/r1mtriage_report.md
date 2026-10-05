# r1mtriage: triage of round 1's red mech battery (2026-10-05)

Lane `r1mtriage` (opus). Branch `lane/r1mtriage`, cut from main a4c752a2.
The input was the D144 [OPTLOOP] round-1 batch gate's full mech run on Linux
at the pinned commit c4c70f2c. Its log was `scratch_lx/lx1005/mech.log`
(copied, read-only), and its trailer read:

    == mech run COMPLETE: 408 rows (unexpected: 7, undetected: 14, unreached: 5, anomalies: 3, oracle-skipped: 0) at c4c70f2c… ==

The per-row `reach.log`/`build.log` paths it cites were gone, because the
scratch root had already been removed. Every row was therefore re-derived
from scratch builds at three trees:

- 9f13b8d6, main just before round 1 landed;
- c4c70f2c, the gated tree;
- current main / this branch.

**No real compiler regression was found.** Every unexpected row and every
anomaly is check-side: a stale witness, a stale anchor, bit-rotted sabotage
text, a check that was vacuous on ELF, or a mis-scored earlier triage.
Most of them were already stale before round 1 (see "Pre-existing" below).

## Per-class counts (the 29 flagged rows; S220 is counted in both the unexpected and the undetected column, as the driver counts it)

| class | rows | count |
|---|---|---|
| A stale [MECH-REACH] witness (the probe greps text a later change moved; the plant still reaches its site) | S268, S278, S280, S305 | 4 |
| B stale anchor, already superseded on main (the plant site was dead at c4c70f2c; k82fix re-anchored it 2026-10-04) | S294 | 1 |
| C check defect: the detector was vacuous on Linux | S297 | 1 |
| D mis-scored earlier triage: the expectation was flipped on a clean-tree red; a real witness has now been added | S220 | 1 |
| E sabotage AFTER text bit-rotted (BUILD-FAILED anomaly) | S168, S185, S222 | 3 |
| F pre-existing and expected: declared by the row's own `SAB_EXPECT`, not part of the red | UNDETECTED: S150 S151 S152 S153 S160 S178 S219 S284 S287 S-U6 S-U9 (11); UNREACHED: S121 (1) | 12 |

The arithmetic checks out:

- 7 unexpected = A(4) + B + C + D.
- 14 undetected = F's 11 + S220 + S294 + S297.
- 5 unreached = A(4) + S121.
- 3 anomalies = E.

## Row by row

The "solo re-run" column gives the driver's own row line. Each run was
`bash tests/mech/run_sabotage_matrix.sh <id>` against a committed HEAD. On
Linux it ran in a standalone clone, `scratch_lx/r1mtriage_wt`, never in the
main clone. Every run listed below ended `unexpected: 0, anomalies: 0`.

| row | class | cause | fix commit | solo re-run |
|---|---|---|---|---|
| S268 | A | The probe's no-common-affix half `(?:xabcy\|zabcw)q` now gets a MASKED run `(x\|z)abc@0`: S4 C3's cube hull, since x/z differ in one bit. run_prechecks §4.7 had already moved to `(?:xabcy\|wabcv)q`; the probe had not. Went stale at round 1 (c3build, abi 59). | 4688b81f | Linux @4688b81f: DETECTED — reach ok, corpus 1025fail/37723pass, prechecks 19fail/326pass, altdiff 0/41 |
| S278 | A | The probe pinned `RX_REQ_RUN "…@0"`. The scan member moved to `@6` at [FIND-TIE] 72e3ae41 (2026-09-28, bisected), so this was stale BEFORE round 1. The window, the whole-run block and its call are unchanged. Re-pinned `@6`. | 4688b81f | Linux: DETECTED — reach ok, prechecks 4fail/341pass, corpus 8fail/8pass |
| S280 | A | C3 folds `[xy]` into the run, so `/abcd[xy]/user`'s run is now the hull `2f61626364782f75@6/fffffffffffeffff`, not `/user@0`. The plant STILL REACHES the pin. With the plant applied on a4c752a2: memchr → run-pinned `0*,1`, and both run_pinned.rxt m cells answer nomatch (clean: 0 11 / 1 12). Re-pinned the stamp. The header names `/abcd[xq]/user` as the C3-proof spelling of the original mechanism. | 4688b81f | Linux: DETECTED — reach ok, corpus 2fail/53pass, prechecks 1fail/344pass |
| S305 | A | The probe grepped `!memcmp(subject + scan_position, "xyz", 3)`. rsform A1 (abi 56) respells the run compare as overlapping `rx_w2` words. The probe now greps the run arm's ADVANCE, `{ scan_position += 3; goto rx_L`, which no compare respelling moves and the per-byte arm never emits. | 4688b81f | Linux: DETECTED — reach ok, irlist 2fail/153pass |
| S294 | B | At c4c70f2c the anchor `if (!rate) return rightmost;` was DEAD. With the plant on c4c70f2c and on 9f13b8d6, `é@`/`Москва` under utf8 stamp identically to clean. Bisected: the plant went dead at [FIND-TIE] 72e3ae41. k82fix re-anchored the row on main to PICK's tie (2026-10-04, after the pin), so main needed no edit. | none (main already fixed) | Linux @4688b81f: DETECTED — reach ok, prechecks 29fail/316pass, corpus 0/38748 (structural row, as designed) |
| S297 | C | `[facts-link]` joined `nm -u` WHOLE LINES. GNU nm prints `                 U name`, and Mach-O prints a bare `_name`. On ELF the join was always empty, so the assertion passed vacuously on Linux; it was only ever measured on darwin. At c4c70f2c on the Mac the same plant IS detected (1fail/7pass). Fix in `tests/codegen/run_facts_checks.sh`: read the last field, plus a new control (see below). | 4688b81f, 71bb1f4a (figure) | Linux @4688b81f: DETECTED — facts 1fail/7pass. Mac @a4c752a2 (fixed script): DETECTED 1fail/7pass. Clean tree: 8pass/0fail, "27 accessor reference(s) joined" |
| S220 | D | UNDETECTED on Linux at c4c70f2c and 4688b81f (searchpinned 0fail/17pass, corpus 0/38748). The 2026-09-29 tri220 flip to DETECTED was a CLEAN-TREE RED. Rebuilt 61cbc894 WITHOUT the plant: run_search_pinned.sh is 1fail/15pass, the same §9 "-fprefilter force axis pinned population 14 < 20 floor" failure that was scored as detection. tri220's reasoned mechanism is nonetheless real, and is now MEASURED: a one-character lookahead never needs seeding, so P3 never runs and P2 is the only guard. Under the plant, `(?!a)` and `x*(?!a)` stamp pinned and answer "a" as `0 1`; python re and the clean tree give `1 1`. No .rxt cell has that shape. Fix: both patterns are added as run_search_pinned.sh §1 named witnesses (stamp + mechanism), and the reach probe also requires `(?!a)` declined. SAB_EXPECT stays DETECTED, now on a witness. | 85b9108e | Mac @85b9108e: run_search_pinned.sh clean 17pass/0fail, plant 15pass/6fail (both witnesses). Linux solo @85b9108e: DETECTED, searchpinned 6fail/15pass |
| S168 | E | AFTER2 used `v.`. The site moved into `vm_emit_search_body`, where `v` is a pointer: lane/tour1 672b4cdd, 2026-09-20 (bisected). Fixed to `v->`. | 46391ae1 | Mac @46391ae1: DETECTED — codegen 10fail/320pass, recdiff 0/10. Linux @71bb1f4a: DETECTED, same figures |
| S185 | E | AFTER called `ofsk_scan(f)->k`. [OPT-LITSCAN] S1 0bb87eda (2026-09-26) moved the resume line into the OfsTest emitter, where the offset is `t->scan_k`. Fixed. | 46391ae1 | Mac @71bb1f4a: DETECTED — corpus 1fail/97pass, offsetskip 7fail/23pass. Linux @71bb1f4a: DETECTED, same figures |
| S222 | E | AFTER used `state_acc_any(st)`, `UPC_N` and `upc_emit_live`. [UCP] U2 601f2e5e (2026-09-29) moved to per-machine `natoms` and a 2-argument `state_acc_any`. The fork now walks `u < fd->natoms`, like P3's own loop. Intent unchanged. | 46391ae1 | Mac @71bb1f4a: DETECTED — pop 16 (want ≥ 12), reach ok, searchpinned 5fail/10pass. Linux @71bb1f4a: DETECTED, same figures |
| S150 S151 S152 S153 S160 S178 S219 S284 S287 S-U6 S-U9 | F | Each row's own `SAB_EXPECT=UNDETECTED` with a SAB_DOC_FIGURE naming what would close it. The 08-30 battery's 10 standing rows are the subset S150-S153, S160, S178, …; the rest were declared at their own landings. | — | not re-run (expected) |
| S121 | F | Declared UNREACHED (EXPECTED): the hazard is structurally unreachable (M5.0 stage 3 re-measure). | — | not re-run (expected) |

S185's Mac run measured 71bb1f4a rather than 46391ae1. I committed
doc-field-only edits to OTHER rows while it was running, and the runner
archives HEAD per row. S185's definition and the compiler are identical
across those two commits.

## The new check control (S297's fix)

The same `nm -u` read that would find a leak must also find the consumers'
LEGITIMATE calls to `facts.h` accessors. The new control does this: it
intersects the owners' defined symbols with `facts.h`'s declared names, and
requires the count of non-owner references to them to be > 0. If the count
is 0, the result is reported as `the nm -u parse joins nothing, so the link
assertion is vacuous` rather than as a PASS.

- Darwin, clean tree: 27 accessor references joined.
- Linux proof that the control fires on the old parse: queued (below).

## Pre-existing, not round 1's doing

Only S268, S280 and S305 went stale at round 1, and all three are reach-probe
text: C3 hull folding, and the rsform respelling. Everything else was already
red before round 1 landed. No full mech run had completed since the
2026-08-30 battery (269 rows, unexpected 0).

| commit | what it broke |
|---|---|
| tour1 672b4cdd (09-20) | S168 |
| S1 0bb87eda (09-26) | S185 |
| [FIND-TIE] 72e3ae41 (09-28) | S278 and S294 |
| U2 601f2e5e (09-29) | S222 |
| tri220 (09-29) | S220 (the false flip) |

The lesson matches learnings §3: rows re-aimed or flipped by solo runs inside
other lanes were never re-checked by a full run for five weeks, and one
"detection" was never A/B'd against its own clean tree.

## Linux validation (COMPLETE, 2026-10-05 20:23Z)

All runs used the standalone clone `scratch_lx/r1mtriage_wt`. The logs are
in `scratch_lx/r1mtriage/`: `chain.log`, `chain2.log`, `chain3.log`,
`mech_<ID>.log` and `facts_control.log`. Every run below completed with
`unexpected: 0, anomalies: 0`.

| row | commit | result |
|---|---|---|
| S168 | 71bb1f4a | DETECTED (codegen 10fail/320pass) |
| S185 | 71bb1f4a | DETECTED (corpus 1fail/97pass, offsetskip 7fail/23pass) |
| S222 | 71bb1f4a | DETECTED (pop 16 ≥ 12, reach ok, searchpinned 5fail/10pass) |
| S220 | 85b9108e | DETECTED (pop 3 ≥ 3, reach ok, searchpinned 6fail/15pass, corpus 0/38748) |
| S297 | 85b9108e | DETECTED (facts 1fail/7pass) |

The `[facts-link]` control was checked on Linux against the clone's own
build at 85b9108e, in both directions:

- **Fixed script:** PASS, "27 accessor reference(s) joined", 8 checks
  passed, 0 failed.
- **Old whole-line parse** (one `sed` removing the `awk '{ print $NF }'`
  stage): FAIL "the nm -u parse joins nothing, so the link assertion is
  vacuous", 7 passed, 1 failed. The control fires on exactly the defect it
  guards.

## Needs a ruling / follow-ups

1. **S220's corpus gap.** No `.rxt` cell distinguishes a bare nullable
   negative lookahead at subject "a" (`(?!a)` → `1 1`). §1 now detects the
   plant structurally. An answer cell in `tests/lookaround/lookahead.rxt`
   (generated by `gen_corpus.py`) would add an answer-level detector, but it
   moves corpus counts. That is left to a ruling rather than done here.
2. **`tests/codegen/manifests/s220_view_decliners.txt`** still states the
   2026-09-02 corpus sweep's "exactly three". That is still true of the
   corpus, since the new witnesses are §1 literals, not corpus patterns. A
   re-sweep under U2's context atoms was never done.
3. The tri220 report (docs/dev/lanes/tri220_report.md) is superseded on its
   verdict and left unedited, as a historical lane record.
