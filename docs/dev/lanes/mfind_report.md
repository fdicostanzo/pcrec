# Lane mfind: the kit's inline one-member finder

Lane mfind, branch `lane/memfn-mfind`, cut from the kit branch `lane/memfn-k1108` at 9798d196e.
Build go from Frank on 2026-11-14 ("Agree with plan. Proceed"). Report written 2026-11-14 23:40.

## Summary

- **What was built.** A SEARCH piece for one exact byte, whose STREAM is MASK ("continue through the current block
  mask", D190). It has three forms:
  - `fn-mfind`: the SIMD-off layer, exact SWAR on an `unsigned long long`;
  - `mfind-w16`: SSE2, levels.def LV_X86_W16;
  - `mfind-w32`: AVX2, LV_X86_W32, with rung `mfind-w16`.
- **Where it lives.** It sits at the offset-skip FUNC site, as a BODY row and two PREFIX rows of `fn_rows[]`
  (memfn/src/ofsskip.c). The renderer is in memfn/src/vrun.c.
- **UNPICKED.** Only the test-only kit lever `mfind` reaches it: `mf_lever(art, "mfind")`, and pcrec's own probe
  `--harness=mfind`. There is no public flag, no deny and no pick. No selection table chooses it, and no emitted byte
  moves on any default arm. There is no abi event.
- **Its card is in this change.** It adds four form-hash entries (mfind-swar, mfind-w16, mfind-w32, fn-memchr) and
  two kit-grid@6 cards (find_byte, find_hit), all visibly UNMEASURED. The timing plan is prepared, not queued, under
  `$PCREC_TMPDIR/scratch/memfn/mfind/jobs/`.
- **Checks run here, all green:**
  - `make strict`, test-memfn-arch, test-memfn-targets, test-memfn-finder (18,102 checks), test-memfn-rows and
    test-memfn-arms;
  - the G2 one-member family, quick tier: 7 builds × 13.17M answer checks each, with 10 plants each in its declared
    class;
  - the G2 part selector's self-test.
- **Heavy gate: queued, not yet run.** It is in the box queue, final key `kit-mfind-gate` (jobs 620-628). The
  evening hold keeps it from starting before 01:00.
- **One correction to the premise.** Pair's machinery is NOT an inline word loop. memfn/docs/ideas.md calls it one,
  but fn-pair is two `memchr` streams (`arm_fixtures --site-text pair`). So the reuse is:
  - the offset-skip FUNC seam;
  - vrun's level table, its intrinsic spellings and its block shape;
  - the D155 helper/selector ladder.

  No pair code is reused, and no parallel mechanism was needed (Design).

## Design

**Where the form lives, and what it reuses.** The site is fn-memchr's: an offset-skip FUNC whose scanned position
is one byte `a` at offset `k`. Its check is that function's own VERIFY CHAIN, every term except the scanned one, so
the answer contract is fn-memchr's unchanged: the leftmost candidate `>= pos` whose terms all hold, else `n`. The
form is three rows in the existing first-match table:

- **BODY row** `{ FN_BODY, mfind_holds, mfind_body, &fn_mfind_ct, NULL, FF_MFIND }`. It sits ahead of fn-memchr.
  `mfind_holds` is `memchr_holds && (levers & KIT_LEVER_MFIND)`, so without the lever the walk reaches fn-memchr
  exactly as before.
- **PREFIX rows** `mfind-w32` and `mfind-w16` are mf_formdecl rows after vrun's, with the same helper names
  (`<fn>__w32`/`<fn>__w16`), the same selector (D155) and the same fall-through (`<fn>__w32` → `<fn>__w16` →
  `<fn>__body`).

New pieces are confined to the following:

- `FF_MFIND` and a `levers` word in `fn_in`;
- `KIT_LEVER_MFIND` in compose.c's `kit_levers[]`;
- two thin exports from ofsskip.c, so that vrun.c can write the verify chain and the fall-through call:
  `ofs_verify_chain` and `ofs_fn_fall`;
- one renderer `mfind_text` over a level table `mfind_lv` (swar / w16 / w32).

The w16/w32 text uses vrun's own `ops_of` spellings. Pair's machinery was the brief's candidate. It is two memchr
streams, so it has no word loop to reduce to one member. Its one-member degenerate case is fn-memchr itself. The
seam and vrun carry one member without a parallel mechanism, so the stop-and-report clause did not fire.

**The SWAR exact mask.** Let `t = w ^ (0x0101..01 * a)`. Then
`m = ~(((t & 0x7f..7f) + 0x7f..7f) | t) & 0x80..80` sets bit 7 of byte j exactly when `t`'s byte j is 0:

- `(t_j & 0x7f) + 0x7f <= 0xfe`, so no carry crosses a byte.
- Its bit 7 is set exactly when the low seven bits of `t_j` are not all zero, and OR-ing in `t_j` adds bit 7 itself.

Every set bit is therefore a real hit. The classic `(t - 0x01..) & ~t & 0x80..` is exact only at its lowest set bit:
its borrow invents a lane for a 0x01 byte above a 0x00 byte. That is fine for a one-shot find but wrong for a MASK
stream, which hands every set lane to the check. Plant S3154 swaps it in, and the G2 family goes LOUD.

The word is one 8-byte `memcpy` load, put into little-endian lane order by
`if (__BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__) w = __builtin_bswap64(w);`. That is an ordinary `if` on a
compiler-predefined constant, folded away, never an `#if` (no CPU fact; D155). gcc 15.2 -O2 did not fold a
byte-by-byte assembly into one load: measured, it emitted eight `movzbl`. The memcpy form is one
`xor (%rdi,%rcx,1)` per word. The lane shift is 3 (a lane's mask bit is its byte's bit 7) and the count is
`__builtin_ctzll`.

**The w16/w32 forms.** Each block is broadcast(a) once, then per block one unaligned load, one compare-equal and
one movemask, giving `m` as an `unsigned` with one bit per lane (lane shift 0, `__builtin_ctz`). The ISA comes from
the host's bracket ops at the level (the art's target, U2). The kit text has no `#include` and no CPU `#if`. The G2
family checks both structurally on every rendered file.

**The over-read argument.** The function reads only `[pos, n)`:

- Let `D = maxk - k >= 0` and `e = n - D`. A candidate `c` is valid iff `pos <= c` and `c + maxk < n`, so its
  scanned byte lies in `[pos + k, e)`.
- **Entry.** At `pos + maxk >= n` the body returns `n` and a helper falls through. A helper also falls through when
  `e - (pos + k) < VW`, and for that short span the body runs a byte loop.
- **Whole blocks.** A block at `i` is taken while `e - i >= VW` and reads `[i, i + VW)`.
- **Final block.** The loop leaves with `0 <= e - i < VW`. If anything is left, the final block reads `[f, e)` with
  `f = e - VW >= pos + k`, and masks off its lanes below `i` with `m &= ONES << ((i - f) << shift)`. The shift is
  1..VW-1, so there is no UB.

  Unlike vany's final block, those lower lanes were candidates the check may already have rejected, so they must
  not be handed over twice. Re-handing them is still answer-identical, because the check is deterministic. Plant
  S3153 confirms this is SAME, as predicted.
- **The check** reads `[c, c + maxk]`, inside the subject.

G2's guard pages sit at `s + n` and below `s + pos`. Each plant that moves a bound by one byte FAULTs: S3150, S3151,
S3152, S3157.

**How the stream hands candidates to the check.** Per block:

```
while (m) { size_t cand = i + (ctz(m) >> SHIFT) - K; if (VERIFY(cand)) return cand; m &= m - 1; }
```

`VERIFY` is `ofs_verify_chain`'s text, the same chain fn-memchr writes. A rejected candidate continues to the next
set lane of the same mask. There is no call per hit and no re-scan, and no byte is compared twice by the search.

**Interaction with pcrec.** pcrec's probe `--harness=mfind` (src/core/internal.h `harness.mfind`, cli/main.c,
src/gen/memfn_sites.c) sets the kit lever on each art. It is listed among test-axes' INTERNAL_ARMS, and the cloud
axes shard table was regenerated (cloud_axes_check.sh PASS, 117 jobs). Spot checks under the lever:

| Pattern | Without the lever | Under the lever |
|---|---|---|
| IPv4 pattern | 2 `memchr` calls | 0 `memchr`, SWAR text present |
| `foo[0-9]bar` | (as default) | moves to SWAR |
| `x.{3}y` | (as default) | identical except the output filename (its site is not fn-memchr's) |

## Forms and levels

| form id (formhash) | kit row | layer | level / target | lanes per block | count | reached by |
|---|---|---|---|---|---|---|
| mfind-swar | BODY `fn-mfind` | SIMD-off | portable (every target) | 8 bytes of a `unsigned long long` | `__builtin_ctzll`, shift 3 | lever `mfind` |
| mfind-w16 | PREFIX `mfind-w16` | SIMD-on | LV_X86_W16 (x86-64 and up) | 16 | `__builtin_ctz`, shift 0 | lever `mfind` + a target admitting w16 |
| mfind-w32 | PREFIX `mfind-w32`, rung `mfind-w16` | SIMD-on | LV_X86_W32 (x86-64-v3) | 32 | `__builtin_ctz`, shift 0 | lever + a target admitting w32 |
| fn-memchr | BODY `fn-memchr` (existing) | libc | every | n/a | n/a | the default (the control) |

**Gate contracts.**

- The mfind contracts' table_ref is `CM(NONE)|CM(REF)`, because the verify chain may reference a set's table.
- vrun's VRUN_SERVES no longer carries a table_ref cell. Both vrun contracts now state `[FLD_table_ref] = CM(NONE)`
  explicitly, which is the same value as before.

**guarded_max, measured by G2 (`G2M guarded`):**

- The alone maxima were w16 1,291 and w32 1,311 at the default seed. Over 44 generator seeds at 160 sites they were
  1,299 and 1,385.
- The bounds are 1,400 (w16) and 1,500 (w32): rounded up to the next 100, plus 100 of headroom.
- They are pinned both in memfn/src/vrun.c and in tests/memfn/simd_bounds.tsv.
- run_g2_mfind.py now holds the measured maxima to the simd_bounds rows. A hand plant tightening w32 to 1,300 went
  red: "alone maximum 1311 over the declared 1300".

**Row manifests.** rows.tsv has `fn-mfind`, `mfind-w16` and `mfind-w32` as reach `pending-site:span_pick-row-1`.
Their witnesses are four new arm_fixtures fixtures rendered under the lever (`ofs-mfind-off`, `ofs-mfind`,
`ofs-mfind-w16`, `ofs-mfind-w32`), each against the next narrower one. The other manifests were updated to match:

- row_floors.tsv: PLACEHOLDER;
- FIXTURE_FLOOR: 40;
- pins/arms.tsv: the four fixtures' digests;
- g2_units.tsv: unit `mfind`, 73 s.

simd_accept.tsv gets no lines: its check F lists only `--list-axes` simd deny rows, and the form has no deny. A
picking unit adds the deny and the CANDIDATE lines.

**The pick was not done, by design.** span_pick row 1 (D190 Q6) waits for this form and its measured card. The unit
that picks it is the abi event. It owns the pick table row, a public deny flag (memory
pcrec-flag-follows-caller-effect: only if it can be slower), the accept lines and the re-pins.

## Card

**Form-hash entries** (memfn/src/formhash.c), all on a new sixth site shape `MF_FH_OFS`:

- the shape is "find-fn": an offset-skip FUNC/FIND/RETURN with one RUN term, the call assigned to `pos`;
- the entry table gained a `lever` column, NULL on every older entry;
- the four entries:

| id | row | target | lever |
|---|---|---|---|
| mfind-swar | fn-mfind | generic | mfind |
| mfind-w16 | mfind@w16 | x86-64 | mfind |
| mfind-w32 | mfind@w32+w16 | x86-64-v3 | mfind |
| fn-memchr | fn-memchr | generic | none |

finder_check.py registers them: FORM_IDS, CARD_FORMDEP_COUNT 20, FORM_INSTANCE_FLOOR 14. arm_fixtures carries the
four hash ids and their rename/edit fixtures.

**Cards** (memfn/data/cards/kit-grid.tsv, ver 6, append-only), both UNMEASURED:

- `find_byte@6`: form ratio, streamed-fresh, pool16Mi, miss-only, slope over 65536 / 262144 / 1048576, 7×7,
  twin-per-arm, bimodal-test.
- `find_hit@6`: form / landing / split / gap, walkbytes, delta at 1048576, 7×7, twin-per-arm.

Both depend on `kit:form.mfind-swar`, `kit:form.mfind-w16`, `kit:form.mfind-w32` and `kit:form.fn-memchr`.
cards/CLAUDE.md carries the @6 line and the pin text "20 (kit-grid 15, kit-kernels 5)".

**Can the slot harness time it? Not yet.** Exactly what is missing (none of it was built, per the brief):

1. **No per-arm target region and no level include in a cell.** link.py's `WRAP_FIND` writes neither, and CC is
   fixed at `-march=x86-64`. The w16/w32 instances therefore cannot compile inside a cell. mfind-swar and fn-memchr
   can.
2. **No measurement-only w64 arm.** An AVX-512BW form would need text that is not from the entry table, and
   link.py's KEY-ARM check refuses that. w64 is OWED: listed, not built.
3. **No reject-rate dimension in find_hit.** gen.c makes every planted hit an answer, so the instance's verify always
   passes. The MASK stream's distinguishing behaviour, continuing through the mask after a REJECTED candidate, is
   therefore not timed. That needs a "decoy" landing (hits that fail the check) in gen.c and in the card's dims.
4. **The libc arm's ifunc is per process.** `GLIBC_TUNABLES=glibc.cpu.hwcaps=-AVX512F` must go in its own job,
   writing its own run dir. This needs no harness change; the plan does it in job 603.
5. **plan.py plans no ver-6 card.** Jobs J6B and J6H do not exist in it yet, so the prepared jobs' dry runs refuse
   (by design) until 1-3 land.

**The timing plan.** It is PREPARED, NOT QUEUED, in `$PCREC_TMPDIR/scratch/memfn/mfind/jobs/`: `common.sh`,
`window.vars.example`, and jobs 600-603. Each job declares `boxqueue: not-before PLACEHOLDER`.

| job | what | est |
|---|---|---|
| 600-kit-mfind-prep | `run.py dry` for J6B and J6H: frozen plan, links, placement, answer gate; no clock | 600 s |
| 601-kit-mfind-byte | find_byte@6: the miss-only per-byte slope at 64 KiB / 256 KiB / 1 MiB. Arms mfind-swar, mfind-w16, mfind-w32, fn-memchr, plus the ver-3 walk/libc/pair instances as anchors | 300 s |
| 602-kit-mfind-hit | find_hit@6, THE HIT-GAP SWEEP: landing periodic, split one, gap ∈ {1, 2, 4, 8, 16, 32, 64, 128, 256, 1024, 4096, 65536}, delta at 1 MiB against the miss-only arm. Arms mfind-swar, mfind-w16, mfind-w32, fn-memchr (glibc default, evex on Zen 4) and pair. The slope over 1/gap is the per-hit cost | 900 s |
| 603-kit-mfind-hit-avx2libc | J6H again under `GLIBC_TUNABLES=glibc.cpu.hwcaps=-AVX512F` (libc memchr at AVX2, width-matched to w32), in its own run dir | 900 s |
| (owed) w64 | an AVX-512BW measurement-only arm, after harness piece 2 | n/a |

Both layers are covered:

- SIMD-off: the mfind-swar arm, which is also each helper's short-span fall-through;
- SIMD-on: the mfind-w16 and mfind-w32 arms.

**Estimated wall: about 2,700 s (45 min) of runs, plus the quiet-gate waits; plan on about 1 hour.** It must run in
a night window Frank clears, never 20:00-01:00. The official SIMD verdict is that run on the targeted hardware
(D144 addendum 4).

## Checks and plants

Checks run here (light), all green:

- `make strict`, test-memfn-arch, test-memfn-targets;
- test-memfn-finder: 18,102 checks;
- test-memfn-rows, test-memfn-arms;
- `g2_parts_selftest.sh`;
- `run_g2_mfind.py --quick`: 168 checks;
- the `--harness=mfind` spot checks (Design).

**G2's one-member family** (memfn/tests/run_g2_mfind.py with g2/g2_mfind_gen.c and g2/g2_mfind_driver.c; run_g2.sh
section 4z, unit `mfind`). It is written by the form's author, not D27-blinded. Its controls are its own:

- G2's scalar byte loop over the predicate as drawn;
- guard pages;
- the generated space;
- per-plant classes.

**The space:** 480 sites per tier.

- The scanned byte includes 0x00, 0x01, 0x7f, 0x80, 0xfe, 0xff, 'a', 'x', 0x20 and 0xdf.
- k runs 0..12, with 0..3 other terms: singleton or multi-member SETs through a table, RUNs of 2..12 bytes, some
  caseless.
- Each site is rendered per target (x86-64-v3, x86-64, generic) with the lever on and off.

**The answers:** every n 0..73, which is 0 to more than 2 blocks at w32 and many SWAR words. They include:

- a passing candidate at every position;
- the MASK stream: failing hits before and just below the passing one, in one block;
- the SWAR exactness trap;
- every alignment, and guard pages at both ends.

**The builds:**

- the x86-64-v3 file at `-march=x86-64` (the region supplies the ISA) and at `-march=x86-64-v3`;
- the x86-64 file;
- the generic file at `-mgeneral-regs-only`;
- the v3 file under ASan+UBSan;
- two lever-0 control builds.

Every build ran 13,172,320 checks with rc 0. The stream and trap populations had floors (K35) and were met:
hits 6.07M, stream1 1.90M, stream2 0.56M, trap 2.24M, late 1.69M.

**Structural checks:**

- Helpers exactly per target: v3 has w16 + w32, x86-64 has w16, generic has none.
- `memcpy(&w` is present and `memchr(` absent under the lever; the reverse without it.
- There is no CPU `#if` and no `#include`.
- There is no PDEP/PEXT and no gather in the v3 driver.

**Plants** (in-runner, applied to the rendered lever-1 text per helper, each edit counted). They run on every G2
run, so they cannot silently stop reaching their site. Every class below is as measured, and every one is the class
predicted:

| id | name | what it does | measured | brief's class |
|---|---|---|---|---|
| S3150 | final-late | the final block starts one byte late (reads past e) | FAULT | LOUD |
| S3151 | loop-past | whole blocks taken while `e - i > VW - 1` +1 | FAULT | LOUD |
| S3152 | entry-short | the helper's entry test admits a span one byte short of a block | FAULT | LOUD |
| S3153 | no-final-mask | the final block's below-i lane mask dropped | SAME (expected; the check is deterministic) | SAME |
| S3154 | swar-classic | the classic `(t-0x01..)&~t&0x80..` zero-byte test | LOUD | LOUD |
| S3155 | high-lane | the final mask keeps the wrong side | LOUD | LOUD |
| S3156 | stream-drop | a rejected candidate ends the block instead of the next lane | LOUD | LOUD |
| S3157 | body-short | the body's short-span byte loop runs one byte past e | FAULT | LOUD |
| S3158 | lane-shift | the lane shift is off by one | LOUD | LOUD |
| S3159 | endian | the byte swap is inverted | LOUD | LOUD |

FAULT and LOUD both fail the run, so both map to the brief's LOUD. No plant is SILENT-MOVE.

**Other new checks, each with one plant:**

- **The guarded-bytes bound check:** plant w32 → 1,300, measured RED.
- **The form-hash rename/edit fixtures for the four ids:** each fixture is itself an edit that must move the hash.
  They were green after their entries were added; red before, when the run printed "renamed nothing" and "edit left
  its hash".
- **rows.tsv's witnesses for the three rows:** green. Run before their lines existed, the check printed "the kit has
  row fn/fn-mfind and rows.tsv does not", a measured red.

**Mech rows re-aimed.** My edits moved the anchors of four existing rows. A scan of all 1,353 mech anchors against
the tree found them:

- **S2930:** the formhash entry gained the lever column.
- **S686:** fn-mfind's row now sits between pair and memchr. The row now writes memchr's row ahead of pair's.
- **S722 and S2999:** mfind's own contract comments duplicated their anchor text. Those comments are now "admits
  wNN".

The gate's job 626 runs these four rows. All other anchors match.

## Identity

The form is unpicked, so the claim is **0 emitted-byte movers on every default arm, and no abi event**. The witness
is box-queue jobs 622-624 (kit-mfind-ident1..3):

- scripts/emit_sweep.py runs the record-first identity gate's declared arms, `--list-ident-arms 9798d196e`: 68 arms.
- It adds one arm per kit CPU target, `-fmemfn-simd=generic|x86-64|x86-64-v3|armv8-a` over c-default and c-vm.
  tgt-generic is the direct generic == plain check. That makes 72 arms.
- It compares the frozen BASE binary (git archive 9798d196e, built by job 620) against HEAD, over the corpus, with
  no declared movers.

No arm names `--harness=mfind`. The lever's own behaviour is the test-axes INTERNAL_ARMS entry, which is
answer-identical by construction of that sweep (Owed runs).

Local evidence already in hand:

- pins/arms.tsv shows no pre-existing fixture digest moved. The four new fixtures were ADDED, and test-memfn-arms is
  green.
- The form-hash table adds entries only.
- Without the lever, `mfind_holds` is false, so the walk is unchanged.

## Owed runs

1. **The validation gate, QUEUED** in the box queue, owner kit. It cannot start before 01:00 (the evening hold); the
   lane does not poll it.

   | job | what | depends on |
   |---|---|---|
   | 620 kit-mfind-strict | `make strict` + the BASE build | none |
   | 621 kit-mfind-g2 | `make test-memfn-g2`; expects the 10 PLANT lines | 620 |
   | 622-624 kit-mfind-ident1..3 | the 72-arm identity sweep | chained after 620 |
   | 625 kit-mfind-test | `make test` via perfrun | 624 |
   | 626 kit-mfind-mech | mech rows S2930, S686, S722, S2999 | 621 |
   | 628 **kit-mfind-gate** | green iff all seven stages ended green | all seven |

   Job files: `$PCREC_TMPDIR/scratch/memfn/mfind/gate/`. Estimated wall about 2.6 h of box time.
2. **Cloud, for the kit manager to dispatch** (not dispatched by this lane):
   - the test kind on this branch, then
   - the AXES kind, because the change touches memfn emit and the harness arms: test-axes' new `--harness=mfind`
     INTERNAL arm must be answer-identical over the corpus;
   - the full mech run, once, on the final commit.
3. **The timing plan, PREPARED, NOT QUEUED:** jobs 600-603 in `scratch/memfn/mfind/jobs/`, about 45 min of runs
   (plan about 1 h), in a night window Frank clears. It is blocked on harness pieces 1, 2 (for w64), 3 and 5
   (Card). Until those land, its dry runs refuse. The w64 (AVX-512BW) arm is owed after piece 2.
4. **Placeholders to measure:**
   - row_floors.tsv g2_floor for the three rows: read from a G2 `--rows` REACH run;
   - the D149 "UNMEASURED DEFAULT" on the entry cut-over (vrun.c's design comment), which only the timing plan
     answers.
5. **The pick** (span_pick row 1): a separate unit after a measured card. That unit is the abi event and needs the
   public deny decision, the simd_accept lines and the re-pins.
6. **Correct memfn/docs/ideas.md.** Its note calling pair "an inline word-at-a-time loop" is wrong (Summary). That
   file is a kit-manager-owned log, so the correction is owed there.
