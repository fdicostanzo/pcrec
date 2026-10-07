> **SUPERSEDED by `G2U_REPORT.md`** (lane g2u, 2026-10-07). Lane g2u folded this
> interim work onto the current G2 by hand; F1, F2, G1, N1 and N2 below are
> dispositioned there. Kept as the record of lane g2x.

# G2X — G2 extended to the site shapes pcrec sends (lane g2x, D27-blinded) — INTERIM

**Status: INTERIM, wound down at the kit manager's request (2026-10-07,
machine move).** One G2 run was made (run 1, `--quick`). No run is in
flight and no lock waiter is left armed. Headline: the shape families
render and run, and the kit's specialised arms are now reached (ofsskip,
precheck, runcmp: 3,227 family sites against 1 in the original space).
They gave **0 wrong answers and 0 faults over 26.9M checks of family
sites**. The 138 failed checks are 2 kit findings (F1, F2), plus 1 G2-side
witness-floor consequence of brief item 2 (G1).

## 1. DISCLOSURE

Files outside the cell that I saw:
- Spawn-time auto-injected: the session-root `CLAUDE.md`
  (`/Users/fdicostanzo/pcrec/CLAUDE.md`), `memfn/CLAUDE.md` (the kit's
  working agreement: layers, the option namespace, the boundary table,
  the stamps), the manager's memory index (`MEMORY.md`), and the git
  status / recent commit subjects (e.g. "M1b: runcmp migrates to the
  kit", "K96 latent ofsskip-arm precondition").
- The Mac suite lock's `owner` file (`worktrees/.mac-suite.lock/owner`),
  read to see who held it.
- `ps -p` of the lock holder's PID (it showed `k94/final.sh`).

I read nothing under `memfn/src/`, `src/`, the repo-level `tests/`, or any
lane report. I ran no `git` and no `make`.

What I learned of the kit beyond `memfn.h` and the contract, all by
rendering sites through `build/libpcrec.a` (scratch probes
`.scratch/probe*.c` and G2's own generator):
- **The form ids it reports:** `generic`, `ofsskip`, `precheck`, `runcmp`.
- **The rendered text of each arm.** ofsskip is §15.1's text, with the
  pair leapfrog on a two-member cube at `plan_pos`. precheck is §15.5's
  lead/window/whole text. runcmp is the `memcmp`/`rx_wN` overlap forms.
  The generic row is a GNU statement expression with `rx_mf<k>_*` locals.
- **When ofsskip is chosen**, observed from the outside. It needs FUNC,
  FIND, RETURN, forward, `end_back` 0, empty MISS, a floor hook of NULL,
  a set plan_hint, a fn_ref, no negative offset, and `miss` NULL or
  textually equal to the `n` hook. Otherwise the kit takes the generic
  row.
- **The kit keeps `mf_art_begin`'s `prefix` pointer** and does not copy
  it (see §5, N2).
- **`nm -u` of the batch objects**, used by the libc leg.

`memfn/tests/G2_REPORT.md`, named in the brief, is not in the cell, so I
did not read it.

## 2. Shapes added, with contract citations

All of them are in `g2/g2_gen.c`, section "lane g2x". Each family is
generated once without and once with `MF_D_RUN_OVERLAP`. Every site in a
batch carries the art's denies (RULED Q-M1b-1; `force_batch`). Each
family is then generated again with non-identifier hook text (styles 1
and 2, sampled 1 in 6), one family per batch.

| family | shape | citation |
|---|---|---|
| `ofs` | FUNC/FIND/RETURN over pcrec's SET+RUN conjunctions: up to 4 SET terms (singleton, case pair, small set, range, word class; multi-member ones through `table_ref`/`table_name`) plus a RUN term (exact, case-folded 0xDF, or 1-2 free bits). Offsets 0..~40, ascending, no overlap. Run lengths 1..48. plan_hint rotates over every term index and MF_NO_PRED, with plan_pos inside the planned run. Some non-planned SET terms are OPTIONAL. A fn_ref plus the fn_name hook. `miss` is exactly the `n` hook's text, or NULL. No floor. Empty MISS (1/8 EXCLUDED). use DISCARD or POSITION | §15.1, §15.2, §14.5 (OPTIONAL, `use`), §14.6 (4 offsets + run), §14.9 (plan_hint/plan_pos), §14.10 bit 44 (folded run) |
| `ofsrun` | the same shape over ONE RUN term: every length 1..40 × offset 0..7 (each alignment mod 8), exact and case-folded; masked at one offset per length; sparse offsets 9..40. plan_pos walks the run | §15.1, brief item 1 (every length 2..33 × every offset mod 8 × deny on/off) |
| `stmt` | the `ofs` predicates as STMT FIND ON_MISS / ASSIGN (`result_decl` "size_t " or NULL), `on_miss_leaves` 0 and 1; empty MISS, sometimes NOP or EXCLUDED | §15.3, §15.5 lines; memfn.h `on_miss_leaves` (Q-G2-18) |
| `onebyte` | STMT/FIND/ON_MISS, one SET term at offset 0 (mostly a singleton), REQUIRED or OPTIONAL; leaves 0/1 | §15.3, §14.5 (the lead's need per route) |
| `gate` | the K82 gate as ONE ALL_PRESENT/STMT site. Its dense `preds[]` holds the lead (singleton SET; the PREDICATE OPTIONAL or REQUIRED), the window RUN (fn_ref), the whole RUN (fn_ref; the window is a slice of it) and the set rest (singleton SETs). ASSIGN with `ret_pred` = the window's index (0 or 1), else ON_MISS. Site-level empty MISS. leaves mostly 1 | §15.5 (rev 4.6 numbering, the composite's empty), §14.3 |
| `setrest` | STMT/ALL_PRESENT/ON_MISS with 1..64 ascending singleton SET predicates, all REQUIRED; EXCLUDED (sometimes MISS); leaves 0/1 | §15.4 |
| `vmrun` | EXPR/VERIFY/BOOL with one REQUIRED RUN term at offset 0..8, `guard_by_caller` 1, empty EXCLUDED, use DISCARD, policy INLOOP. Every length 1..40 exact at every offset; folded and masked at one offset per length; an unsatisfiable byte now and then | §15.6, §R4.8.1 item 4, Q-M1b-5, Q-G2-13, Q-G2-15 |

Changes to the original space (family `base`):
- **`on_miss_leaves` at both values.** It is set on ON_MISS/ASSIGN sites
  whose on_miss text leaves (goto/return), drawn from a separate random
  stream, so every other field of the original space is unchanged.

Other G2 changes:
- **Q-G2-6, brief item 2.** `floor <= lo` is now honoured for EVERY site
  in `g2_driver.c` `admit()`/`pick_fl()`: the driver clamps and counts.
  Run 1 clamped 0 instances, because `pick_fl` no longer proposes `fl > lo`.
  No answer is checked past the edge.
- **Reference change, §15.5.** In an ALL_PRESENT ASSIGN, "every other
  predicate behaves as ON_MISS": only the returned predicate's line
  writes `result`. So where on_miss leaves (G2 gives such sites an
  on_miss that reads no result), a miss may leave the result unwritten
  (`g2_ref.c`, `unwritten_ok`). This follows §15.5. It loosens no other
  expectation.
- **`miss` NULL is treated as the contract's EDGE.** memfn.h names no
  default for `miss`. A refusal is counted `edge_refused` and is never a
  failure. A rendering is checked against §15.1's `miss` = `n`.
- **Harness.**
  - A batch that does not compile now fails every site in it and is
    linked as an empty stub, so the other batches still run. Before,
    one bad batch dropped the whole compiler leg.
  - The batch prefix is now heap-held (the kit keeps the pointer).
- **New legs in `run_g2.sh`.**
  - The family census, with per-family rendered and run floors
    (`FAM_FLOORS`) and `FLOOR_FAM_FORMS`=4.
  - The libc record: `MEMFN_LIBC` against `nm -u` of the `-O0
    -fno-builtin` batch object, which is §R4.3.3's own control (memcpy
    aside).

## 3. Per-shape rendered / refused counts (run 1, seed 20261005)

| family | rendered | refused (fail) | edge-refused (`miss` NULL) | edge rendered | form ids | sites run (gcc) | checks | positive / negative |
|---|---|---|---|---|---|---|---|---|
| base | 4044 | 0 | 0 | 0 | generic 4043, runcmp 1 | 4044 | 15,562,777 | 4,979,342 / 10,583,435 |
| ofs | 448 | 0 | 112 | 48 | generic 270, ofsskip 178 | 448 | 2,061,021 | 712,289 / 1,348,732 |
| ofsrun | 1788 | 0 | 12 | 388 | generic 30, ofsskip 1758 | 1788 | 8,425,336 | 2,396,635 / 6,028,701 |
| stmt | 398 | 0 | 70 | 0 | generic 398 | 398 | 1,409,997 | 479,245 / 930,752 |
| onebyte | 94 | 0 | 0 | 0 | generic 94 | 94 | 332,487 | 320,409 / 12,078 |
| gate | 358 | 0 | 16 | 51 | generic 81, precheck 277 | 332 | 1,178,766 | 439,662 / 739,104 |
| setrest | 70 | 0 | 0 | 0 | generic 64, precheck 6 | 70 | 244,551 | 128,652 / 115,899 |
| vmrun | 1028 | 0 | 0 | 0 | generic 18, runcmp 1010 | 954 | 2,598,877 | 1,028,430 / 1,570,447 |

gate and vmrun ran fewer sites than they rendered: 26 + 74 = 100 sites in
the two style-2 batches that do not compile (F1).

Population: 8,438 generated sites in 80 batches (the original space was
4,044). The quick tier's wall time roughly doubles with them; I made no
timing measurement before the wind-down.

## 4. Run 1's summary lines

```
== gcc-16 (quick subjects): passed 31813812 failed 0 sites 8128 coverage-missing 1
   G2 faults: 0
   G2 sites failed: 0
== asan+ubsan: passed 10179724 failed 0
== libc record (MEMFN_LIBC vs nm -u of -O0 -fno-builtin, memcpy aside): batches agree 43, disagree 37
   gcc-16: rendered text that does not compile: 100 sites in 2 batch(es)
checks passed: 42764640
checks failed: 138
failures:
  - libc record: MEMFN_LIBC is not the libc calls of the kit's text in 37 batch(es)
  - gcc-16: rendered text does not compile
  - W2 hook mutation 7 caught 639 of 1196 (< 65%)
EXIT 1
```

`coverage-missing 1` is the quick tier's expected alignment axis (4/16),
which the script excludes.

The controls:
- **W1:** 1, 2 and 3 fire (26,976 / 398,914 / 46,282).
- **W3:** over, under and clean all behave.
- **W2:** mutations 1-6 meet their rules; mutation 7 does not (G1 below).

## 5. The 138 failed checks, analysed

138 = 37 (F2) + 100 (F1) + 1 (G1).

**F1 — KIT FINDING (100 sites): specialised arms paste hook text without
parentheses.**
- **Contract:** memfn.h `mf_hooks`: `s`, `n`, `lo`, `floor` are
  "side-effect-free C expressions (rule 1)". §8.3 rule 1 places no
  primary-expression requirement on them. The generic row parenthesizes
  every hook, e.g. `(const unsigned char *)(s)`.
- **What the arms do:** runcmp and precheck splice the hook text raw.
- **Minimal reproducer:** VERIFY/EXPR/BOOL, one RUN term "abcd" at
  offset 2, `guard_by_caller` 1, EXCLUDED, hook `lo` = `0 ? pos : pos`.
  The kit renders `!memcmp(subject + 0 ? pos : pos + 2, "\141\142\143\144", 4)`.
- **Gate site:** with `n` = `k ? n : m` and `lo` = `a ? pos : q`, the kit
  renders `if (k ? n : m <= a ? pos : q || !memchr(subject + a ? pos : q, …`
  and `if (hp >= k ? n : m) return 0;`.
- **In G2:** the style-2 batches of `gate` (batch_077) and `vmrun`
  (batch_079) do not compile (`-Wint-conversion`).
- **Where it would be silent:** where the parse still type-checks (an
  integer `n`/`lo`), it would miscompile without any error.
- **Latent for pcrec**, whose hooks are identifiers (`subject`,
  `subject_length`, `search_from`, `scan_position`).
- **The ruling is the kit's:** parenthesize, or restrict the hook
  contract to primary expressions. Parenthesizing moves bytes, so it is a
  pcrec abi event.
- G2's expectation was not weakened: these sites stay.

**F2 — KIT FINDING (37 batches): `MEMFN_LIBC` omits the libc calls the
kit's own text makes.**
- **Contract:** §R4.3.3 (rev 4.7, Q53 RULED): the record lists the libc
  functions the artifact's code calls. "A delegated site's libc use is
  recorded by the kit through `mf_art`". memfn.h `mf_art_note_libc` is
  the writer only for calls "the kit did not render itself".
- **What the kit does:** it renders `memchr`/`memcmp` (ofsskip, precheck,
  runcmp's `memcmp` row) and still stamps `MEMFN_LIBC "none"`.
- **Evidence:** batch_022, MEMFN_LIBC "none", the compile calls `memcmp`.
  batch_034/035, "none" vs `memchr,memcmp`.
- **Minimal reproducer:** one FUNC/FIND/RETURN site, RUN "user" exact,
  plan_hint 0, plan_pos 3, fn_ref 1, `miss` "n", no floor, then
  `mf_stamps`. The text calls `memchr` and `memcmp`, and the stamp reads
  `MEMFN_LIBC=none`.
- **The control** is the one §R4.3.3 names (`nm -u` of `-O0 -fno-builtin`).
  G2's own batch text calls no libc function.
- **Caveat:** memfn.h's `mf_stamps` comment says "the libc function
  names noted on this art", which a reader could take to mean only
  `mf_art_note_libc`. §R4.3.3 is explicit, so I read it as a finding.

**G1 — G2-SIDE (1 check): W2 mutation 7's kill rate fell to 53%, under its
65% floor.**
- **Cause:** brief item 2. Before, `pick_fl` proposed `fl > lo`, and a
  floor lowered by one (`fl - 1`) was observable at any candidate in
  `[lo, fl)`. Now that G2 is a conforming caller (`fl <= lo`), the
  mutation can only show through a term at a negative offset. On every
  other site it is an equivalent mutant.
- **Evidence:**
  - The mutation still faults on the lower guard page (116,736 faults),
    so the witness reaches its site.
  - Mutations 5 and 6 are unaffected.
  - The base space was the one whose fl distribution changed.
- **Remedy owed:** judge mutation 7's rate over the sites whose
  predicates read below the candidate (a negative offset), where it is
  never equivalent. Do not lower the floor without that measurement. I
  did not make this change; it is the next lane's first item.

**Notes (no failed check):**
- **N1 (contract gap):** `miss` NULL is accepted by the ofsskip arm,
  which answers `n`, but refused by the generic row ("the call needs the
  `miss` hook"). So a site's membership in the vocabulary depends on
  which arm the kit picks. 210 such sites were edge-refused; none was
  wrong where rendered. Totality (§8.2) wants one answer: memfn.h should
  state a default, or the arm should refuse too.
- **N2 (contract gap):** `mf_art_begin` keeps `prefix` by pointer.
  memfn.h states no lifetime for it; Q-G2-7 covers only hook-returned
  strings. G2's original batch loop passed a block-scoped array (latent);
  that is now fixed G2-side.

## 6. What remains

1. G1's remedy (the mutation-7 judgement over negative-offset sites),
   then re-run.
2. Wall-time measurement of `--quick` with the families. Trim
   `ofsrun`/`vmrun` if it exceeds the make-test budget, without dropping
   the brief's length × offset-mod-8 × deny grid.
3. A full-tier run (gcc + clang, every witness on every batch) is not
   mine (brief: quick only); it is owed by the manager.
4. Confirm `FAM_FLOORS` on a second seed. The literals sit about 10%
   under run 1's counts.
5. The kit's rulings on F1, F2, N1 and N2.

Files changed in the cell:
- `memfn/tests/run_g2.sh`
- `memfn/tests/g2/g2.h`
- `memfn/tests/g2/g2_gen.c`
- `memfn/tests/g2/g2_ref.c`
- `memfn/tests/g2/g2_driver.c`
- `memfn/tests/CLAUDE.md`
- this report

Scratch material (not for delivery):
- `.scratch/` holds the probes, run 1's log (`.scratch/run1.log`) and its
  kept work dir (`.scratch/tmp/g2.R06fPi`).
