# Lane slotx: the slot harness's target region, find_hit's reject dimension, ver-6 planning

Lane slotx, 2026-11-14 (opus), branch lane/memfn-slotx, cut from lane/memfn-mfind @ 1840f4e81. Frank's GO of
2026-11-15 ("agree with kit options") covered pieces 1, 3 and 4. Only harness and measurement scripts changed:
no byte pcrec or the kit emits moved (identity job 643, below). Nothing was timed.

## Summary

- **Piece 1, the per-arm target region.** A slot TU whose instance's kit target opens a region is now compiled
  inside that region, the same way pcrec places one: header lines first at file scope, then the region around the
  TU's functions. The w32 arm therefore compiles under x86-64-v3, and the swar, w16, memchr and every ver-3 arm keep
  their bytes and keys (77 base-plan TUs byte-identical, scratch tools/tucmp.py). The target is part of the arm's
  record (cell_text.tsv `target`, `target_isa`) and of its check: an ISA check refuses an object that uses a
  feature outside floor + target, or that uses none of what its target adds.
- **Piece 3, reject rate in find_hit.** A find site's run is now two bytes, `xy`: x is scanned and y is the check
  at offset 1. The new `reject` dimension sets the share of hits whose check byte fails: 0, 100, and 50 at gaps 4,
  32 and 256. The generator writes exactly floor(E*R/100) failing hits. The gate counts the realized rejections
  from the subject's bytes, and run.py refuses any count other than the key's.
- **Piece 4, ver-6 planning.** plan.py now plans ver 6 alongside 3 and 4:
  - `card_of` resolves a key to its card by form, because find_byte and find_hit have cards at both ver 3 and 6.
  - Job JMB covers find_byte@6 and job JMH the find_hit@6 sweep over GAPS6 x reject.
  - The UNMEASURED classes (mfind-w64, gap 1) stay listed in `UNPLANNED6` and are never scheduled or priced.
  - record.py has a `mfcard` window, the job set J2 J2p JMB JMH.
  - est.py prices only the rows of the window's own jobs and splits the draft by ver. `draft_split` holds each
    set's rows to that set's own cards.
- **Piece 2 (mfind-w64) stays OWED**, along with both IPv4 one-axis comparisons; the slot harness cannot express
  them yet (see Timing jobs).
- **Gate:** queued as 640-649, final key kit-slotx-gate, not before 2026-11-15T01:05. It is OWED.

## Harness pieces

Files, all under docs/design/memfn/span_cards/slot/ unless named:

| piece | where | what |
|---|---|---|
| 1 | `link.py` `frame`/`framed`/`floor_features`/`isa_check`, `render`, `build_objs` | gets the frame from `arm_fixtures --frame ID CLS` (the kit's own include lines, region open, region close, target and features). `framed()` puts the header lines the prologue lacks first, then the region around the TU. `render` refuses a frame target other than the facts' target. Per object, `isa_check` reads `objdump -d` over `.text` against the ISA_NEEDS table and refuses either way: ISA MISMATCH. tzcnt is not in the table, because the floor's `rep bsf` decodes as tzcnt. cell_text.tsv gains `target` and `target_isa`, and link prints a `target:` line. |
| 1 | tests/memfn/arm_fixtures.c `--frame`, `--target-facts`; memfn/src/formhash.c `mf_form_includes` (kit.h) | the frame comes from the kit's own target table (targets.def, MF_NEEDS) and include facts, so the harness never spells a region. |
| 3 | memfn/src/formhash.c | the four mfind-site entries' run changes from `x` to `xy`, so the site's verify chain has a check that can fail. Not reached by any emitter: there is no caller of `mf_form_hash*` under src/, cli/ or lib/. |
| 3 | arm_fixtures.c `f_ofs_shape`, the facts | OFS instances: `members` is byte 0 only; L, run and mask describe the whole run. |
| 3 | `slot.h` (`reject`), `gen.c` | with L>1 each run occupies [p,p+L). Periodic hits sit at k*gap+gap-L, random hits do not overlap, and the sentinel sits at len-L. A seeded choice of exactly floor(E*R/100) hits gets a check byte that fails the mask and is no find member. The generator refuses a gap below L, a reject with L<2, and a check byte that is a member. Ver-3 subjects are byte-identical to the base generator's (scratch tools/gencmp.c). |
| 3 | `drv.c`, `run.py` `reject_check` | for each landed find arm, the gate prints `reject ARM CAND REJECTED`, counted from the bytes as candidates minus gate count. run.py requires rejected = pools x floor(E*R/100), E = LEN/gap and cand = pools x E; otherwise REJECT-RATE MISMATCH. |
| 3 | memfn/data/cards/kit-grid.tsv | find_hit@6's dims become `form;landing;split;gap;reject`, with subject `reject:percent`. I amended that row instead of adding a ver 7 because it has never been merged or timed, so nothing reads the old dims; the file's header note says so. |
| 4 | `plan.py` | `METHOD_VERS` gains 6. Cards are keyed `quantity@ver`. `card_of` returns the quantity's card whose deps name the key's form, or the one card naming no form, and refuses unless exactly one matches. Every row key is held to its card's dims at build time (`key_dims` in `row()`). New: JMB (9 arms), JMH (173 arms, groups `JMH.hit.rR.G`), GAPS6, REJECTS_ALL/SOME, `UNPLANNED6`, DIM_FIELD `reject`, and FLOOR rows `(quantity, ver, test, clause)` with find_hit@6's `hit6.<form>`. The plan report shows 151 rows. |
| 4 | `record.py` | `WINDOWS` (`s2d` and `mfcard`). finalize records the window whose job set equals the states. SETS gains ver 6, `zen4-grid6@1`. The `libc` fact names any GLIBC_TUNABLES. |
| 4 | `est.py` | `compute` keeps only the rows (and floor clauses) of the record's jobs. `card_of` supplies est and gate. `draft_split` raises DRAFT-VER MISMATCH. The draft's source field gains ` target T`. Self-test: 54 cases, 0 wrong (new: mf_priced, mf_split). |

## Fidelity

**One w32 cell end to end:** `kit.find_hit.mfind-w32.periodic.one.256.50`. Its arms are that key, its twin
`#b`, `base.mfind-w32` and a swar reject-100 arm. scratch tools/trace.py linked the four arms into one launch and
gated it (scratch/memfn/slotx/trace/).

1. **Key to card.** The key has five tokens after `kit.find_hit`. `card_of` finds find_hit@6, whose deps name
   `mfind-w32` and whose dims are `form;landing;split;gap;reject`. KEY-ARM agrees on every dim, `reject` 50
   included.
2. **Facts and frame.** Facts: target x86-64-v3, L 2, run `78 79` ("xy"), members byte 0. The frame holds
   string.h, emmintrin.h and immintrin.h, then `#pragma GCC push_options` / `target("avx2,...")`, and
   `pop_options` at the close.
3. **TU (arm4.c).** The header lines sit at file scope ahead of the region. The region encloses the CAT macros,
   the SITE FILE text, step, `_time` and `_gate`.
4. **Object.** It contains `vpcmpeqb ... %ymm`. `mf_fn__w32` is out of line (local symbol `t`). The ISA check
   reads avx,avx2,bmi,bmi2 within floor + x86-64-v3, and target features are present.
5. **Record.** cell_text.tsv: target `x86-64-v3`, target_isa `avx,avx2,bmi,bmi2`. Arm table entry: hit {120}
   ('x'), gap 256, L 2, run 78 79, reject 50.
6. **Subject and gate.** The gate line is `reject kit.find_hit.mfind-w32.periodic.one.256.50 65536 32768`:
   65536 candidates and 32768 rejected, which is exactly floor(E*50/100) per pool. Then `GATE ok: 6 arms, 8
   pools, 416 subjects` and `ROUND CHECK ok`. The x86-64-v3 TU sits in a binary whose driver (drv.c) and generator
   (gen.c) stay at the default target.

## Checks and plants

Checks run by the lane:

- `make strict` passes (rc 0: "whole tree compiles clean with -Werror -Wshadow; the kit's target table check
  passes").
- arm_fixtures.c, gen.c and drv.c compile with -Wall -Wextra -Werror.
- test-memfn-finder and test-memfn-arms passed after the formhash change (WIP 1).
- est.py self-test: 54/0.
- plan.py report: rc 0.
- The three mech rows whose SAB_FILE the lane changed (S2930, S2933, S520) have their anchors present, each once
  (scratch tools/anchors.py). The rows themselves run in gate job 644.
- 77 base-plan TUs are byte-identical, and so are the ver-3 subjects.

Plants use S3160-S3167 and are slot-local rows in sabotage.sh, because no make suite runs the slot dry run. A
plant is LOUD when a check refuses it, SILENT-MOVE when the timed number moves and nothing refuses, and SAME when
nothing observable changes.

| id | row | plant | measured | class |
|---|---|---|---|---|
| S3160 | t1 | (brief i) w32 compiled at the DEFAULT target while keyed v3: the region dropped, header lines kept | sabotage.sh: DETECTED, JMB dry: gcc `inlining failed ... target specific option mismatch` | LOUD |
| S3161 | t2 | (brief i, other half) the arm TUs compiled at -march=x86-64-v3 while the swar/w16 arms are keyed generic | sabotage.sh: DETECTED, `ISA MISMATCH ctl: keyed target generic, its code needs bmi2 (shrx ...)` | LOUD (without the ISA check: SILENT-MOVE, every generic arm timed at v3 code) |
| S3162 | r1 | (brief ii) gen.c writes no failing check (m = 0) while the key says 50/100 | trace subset: `REJECT-RATE MISMATCH ... 0 rejected; its key names reject 100%`. With the check off, the same binary's answer gate and round check stay GREEN (`reject ... 4194304 0`, `GATE ok`). | LOUD (without reject_check: SILENT-MOVE, the answer gate cannot see it) |
| S3163 | r2 | (brief ii) the arm table records reject 0 for every arm | trace subset: REJECT-RATE MISMATCH (gen reads the table's percent, the key names 100) | LOUD |
| S3167 | k1 | plan builds the reject-50 Arms with reject 0 (key still says 50) | trace subset: `KEY-ARM MISMATCH ... dim reject: the key names 50, the Arm 0` | LOUD |
| S3164 | v1 | (brief iii) draft_split moves the ver-6 rows into ver 4's set (priced from ver 4) | sabotage.sh: DETECTED (est self-test mf_split: DRAFT-VER MISMATCH) | LOUD |
| S3165 | v2 | (brief iii) `card_of` takes the quantity's FIRST card (`[:1]`), i.e. the ver-3 card prices a ver-6 key | sabotage.sh: DETECTED, `key kit.find_hit.mfind-swar.periodic.one.2.0 has 5 tokens, its card's dims [...] are 4`. The first try MISSED: the dims were first checked only at link, which the plan dry run never reaches. The fix holds every key to its card's dims at build time (`row()`). find_byte's two cards have equal dims, so for find_byte the draft split check is the second witness. | LOUD |
| S3166 | w1 | est's window filter removed (a mfcard record prices s2d rows it never ran) | sabotage.sh: DETECTED (est self-test mf_priced) | LOUD |

The ids S3168 and S3169 are unused. One more plant was considered: dropping the ISA check's "target features
must appear" clause. I predict it SAME for today's arms, because w32 does use avx2. It is listed, not planted. On
sabotage.sh, rows t1, t2, v1, v2 and w1 passed through sabotage.sh itself (the last run DETECTED v2 and t2 after
the fixes). Rows r1, r2 and k1 were measured on the 4-arm trace subset, because their JMH dry run takes about 8
minutes. The full sabotage.sh over every row (old and new) is gate job 642, OWED.

## Timing jobs

The jobs are PREPARED, NOT QUEUED, in /var/tmp/pcrec-pcrec/scratch/memfn/slotx/jobs/. They supersede mfind's
600-603, whose directory now has a SUPERSEDED.txt. Every job's `--dry-run` was checked rc 0 against a test
window.vars (RUN_ID mfcard-dryrun-check, FROZEN = the lane HEAD); that file was then removed.

- Every job prints `boxqueue: not-before PLACEHOLDER`. Main replaces it with the cleared window's start, and
  `boxqueue add` refuses a PLACEHOLDER by design.
- Main writes window.vars from window.vars.example.
- Every timing job runs `run.py run`: the prep's manifest, then 7 launches x 7 rounds, taskset to the plan's CPU,
  quiet-gated, idle-ok.

**(c) key kit-mfcard-time: the hit-gap sweep with reject rates.**

| job | what | est (s) | cap |
|---|---|---|---|
| 600-kit-mfcard-prep | dry runs of J2 J2p JMB JMH, in RUNDIR and in RUNDIR.avx2libc under GLIBC_TUNABLES=glibc.cpu.hwcaps=-AVX512F | 1500 | 5400 |
| 601 J2 | the unit (find_byte.walk) and libc's byte row, default memchr (evex) | 240 | 720 |
| 602 J2p | pair, the ver-3 anchor | 360 | 1080 |
| 603 JMB | find_byte@6: miss-only slope of mfind-swar, mfind-w16, mfind-w32 (in its region) and fn-memchr | 360 | 1080 |
| 604 JMH | find_hit@6: gaps 2..65536 x reject 0/100 (50 at 4, 32, 256), the same four forms, delta against base.FORM | 2400 | 7200 |
| 605-608 | J2, J2p, JMB, JMH again under the -AVX512F tunable in RUNDIR.avx2libc (glibc's ifunc is chosen per process, so one record per libc variant; record `libc` names the tunable) | 240/360/360/2400 | 3x est |
| 609-kit-mfcard-time | per rundir: record.py finalize (window mfcard), est.py rows, est.py draft (zen4-grid3 and zen4-grid6 `.v6`) | 120 | 900 |

**Estimated wall for the whole window: about 2 h 20 min.** That is 1500 + 2 x 3360 + 120 = 8340 s. The basis is
the measured dry-run gate and round cost (about 1 s per ~100 MiB generated; round 2 of the trace launch took
0.9 s) scaled by the plan's arms, groups and launches. The JMH figures are the least certain. Pair is part of
J2p. The two libc variants are memchr default (evex) and -AVX512F (the AVX2 variant, width-matched to w32).

**(d) key kit-ipv4-time: OWED.** The two one-axis comparisons cannot be expressed in the slot harness yet. Job
620-kit-ipv4-time exists so the key is visible, but its dry run REFUSES and names what is missing:

1. **One byte `.` vs the run `[0-9]\.[0-9]`, both through the kit's inline loop.** The slot's cells come from
   formhash's entry table, whose offset-skip site takes an exact run only. `[0-9]` is a set position, not a mask
   byte, and the kit has no fold-in-block check form. This needs a new entry shape and a new kit form, which is
   build work outside the three pieces.
2. **The kit loop vs libc memchr on TEXT.** Slot find subjects are synthetic, and the whole-artifact arm family
   takes neither pcrec's `--harness=mfind` lever nor an IPv4 text corpus. The finder-level half of this axis (kit
   loop vs memchr, same byte, declared gaps and reject rates) is covered by JMH (mfind-* vs fn-memchr).

## Owed runs

1. **kit-slotx-gate**, queued as 640-649, not before 2026-11-15T01:05 (the evening hold also holds every stage's
   readiness):

   | job | what | est (s) |
   |---|---|---|
   | 640 strict | make strict, plus the BASE build | 420 |
   | 641 memfn | test-memfn-finder, test-memfn-arms, test-memfn-targets | 600 |
   | 642 slot | est.py self-test, JMB and JMH dry runs, sabotage.sh over every row | 4200 (the sabotage time is UNMEASURED) |
   | 643 ident | the `base` identity arm plus three CPU-target arms, BASE vs HEAD, no movers | 600 |
   | 644 mech | S2930, S2933, S520 | 1200 |
   | 649 | the verdict | 5 |

   About 2 h in all. Watch it with `scripts/monread kit --wait`.
2. **The timing window kit-mfcard-time** (above): prepared, waiting for a Frank-cleared night window.
3. **Piece 2, the w64 arm (mfind-w64):** OWED. It is listed in `UNPLANNED6` and never scheduled or priced.
4. **kit-ipv4-time, both axes:** OWED, needing the pieces named in (d).

## STATE AT HANDOFF

- Branch lane/memfn-slotx in worktrees/slotx. Commits since the cut: WIP 4a694cd37 (kit side), dffc1eb65 (slot
  pieces), c230370d4 (plants, build-time key dims), dd5f84928 (CLAUDE.md), then this report.
- Gate 640-649 (final key kit-slotx-gate) is queued, owner kit, not before 2026-11-15T01:05; OWED. The timing jobs are prepared and not queued.
- Nothing is running from this lane.
