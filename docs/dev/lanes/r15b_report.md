# r15b — [MEMFN] R-15 BUILD: the row `precheck_assign_byte` (the kept one-byte landmark)

**Lane `r15b`, 2026-10-11, opus.** Branch `lane/r15b`, cut from
`lane/memfn-r15` = main `f18935d4`. Charter: `memfn/docs/requests.md` R-15.
Design: `docs/dev/lanes/r15scope_report.md` (followed; deviations in §8).
Sabotage ids S800-S804. Every run was pinned to `taskset -c 12-15` at `-j4`.
The box's load1 was 1.05 at the start (no wait was needed).

## 0. Answers first (resume from here)

1. **The row is built**, as a THIRD row of precheck.c's one renderer. Its
   name is `precheck_assign_byte` and its form id is `precheck`. It sits in
   compose.c's `arms[]` directly after `precheck_assign`, so it is above
   `generic`.
   - **Predicate:** `handoff == ASSIGN && precheck_parts(...) &&
     byte_landmark(s)`, where `byte_landmark` holds iff `ret_pred` is 0 and
     part 0 is ONE REQUIRED byte in a REQUIRED predicate. `precheck_parts`
     is the old `precheck_applies` without its last line, now shared by all
     three rows.
   - **Text (`landmark`)**: one `memchr` behind the empty test, inside a
     statement expression, then pcrec's `on_miss` when the result is `n`:
     ```c
     <decl><result> = ({ const void *<prefix>_mf<h>_q = <n> > <lo> ? memchr(<s> + <lo>, <b>, <n> - <lo>) : NULL; <prefix>_mf<h>_q ? (size_t)((const unsigned char *)<prefix>_mf<h>_q - (const unsigned char *)<s>) : <n>; });
     if (<result> >= <n>) <on_miss>
     ```
     The statement expression lets a site's second use, rlhbuild's
     re-entry, sit in the same function without declaring anything twice.
   - **Contract:** `precheck_assign_byte_ct`. It declares the same `uses` and
     `serves` as `precheck_assign` (MISS_N, floor 0, on_miss JUMP|BRACED,
     IDENT s/n/lo). The predicate holds what a class cannot say: one member,
     offset 0, REQUIRED, `ret_pred` 0.
2. **This is the kit's first SCALAR deny, `--memfn=no-precheck-assign-byte`.**
   - The `options.def` row is `MF_OPT_DENY`, `MF_B_ANY`, `MF_L_SCALAR`.
   - The `arm` struct gains `opt`. It is NULL on every transcribed row and
     on `generic`.
   - `arm_table` gains its `opt` accessor (`arm_opt`). `walk_row` already
     read it.
   - Denied, `generic` renders the site.
3. **Main is byte-identical (ZERO movers), §2.**
   - The method was emit_sweep against a base build of `f18935d4`, over a
     1-in-8 sample of the corpus (567 patterns) plus 6 witnesses.
   - Four arms were run: SIMD-off, `-fmemfn-simd`, the deny, and the deny
     with `-fmemfn-simd`. All four showed 0 artifact movers on every stream.
   - The only mover was the `--list-axes` dump, by exactly the new row.
4. **The row serves rlhbuild's site, §3.** I merged this branch into
   `lane/rlhbuild` in a scratch worktree (now removed).
   - ipv6, ipv4 and dotted4 render `memchr` ASSIGN at BOTH the entry and the
     re-entry.
   - `--memfn=no-precheck-assign-byte` reproduces rlhbuild's generic text
     byte for byte (`rx.c` and `rx.h`, all three cells).
   - The answers are equal: 0 differing lines against rlhbuild as built,
     against main and against libpcre2 10.46, on rlhbuild's own subjects.
     `tests/litscan/handoff.rxt` passes 4908/0 with the row and 4908/0
     under the deny; 11 of its 40 distinct patterns render the row.
5. **G2 was extended (not blinded) and a standalone runner added, §4.**
   - The gate family gains R-15's landmark sites: 256 hard sites (every
     member byte) plus 15 near-miss kinds, on their own RNG stream.
   - `g2_gen --gate-only 1` generates that family alone.
   - The runner is `memfn/tests/run_g2_gate.sh`, with a W2 control.
   - Result: 806 gate sites, 0 failed, both plain and ASan+UBSan. The row
     was chosen 802 times; the control killed 345 of 388 mutants.
   - **Mech arm `g2gate`** registers that runner.
6. **Sabotage: S800-S804 are each DETECTED solo, §5.** `memfnarms` detects
   all five. S802 and S804 are also detected by `g2gate`.
7. **Only light validation was run; the OWED heavy list is §6.** One
   deviation: an emit_sweep that I meant as a sample ran the full argv
   corpus for one arm (89 s, pinned to 4 cores) before I stopped the chain.
   Details are in §2.
8. **L1's merge has three things on it that this branch makes red or stale
   ON PURPOSE** (§7):
   - the cli case "deny moves nothing on dotted4";
   - the spec sentences "today the deny moves no artifact";
   - rows.tsv's `pending-site` reach.

## 1. What changed (files)

**Kit**
- `memfn/src/precheck.c`:
  - `precheck_parts`, split out of `precheck_applies`;
  - `byte_landmark`, `precheck_assign_byte_applies`;
  - `landmark` (the text), with the ret_pred branch in `precheck_use`;
  - `precheck_assign_byte_ct`, `precheck_assign_byte_arm`;
  - the header's form list, the split comment, and the contracts' `:line`
    cites re-aligned (each was checked against its line);
  - the provenance header: `landmark` is original kit text, also noted in
    `memfn/PROVENANCE.md`.
- `memfn/src/kit.h`:
  - `arm.opt`;
  - the new arm's extern;
  - the precheck comment: three rows.
- `memfn/src/compose.c`:
  - the row in `arms[]`;
  - `arm_opt`, and `arm_table`'s accessor;
  - the selection-table and `select_arm` comments.
- `NULL` opt on every existing arm: `generic.c`, `ofsskip.c`, `runcmp.c`,
  `mismatch.c` and `pffind.c` (5 rows). Positional initializers, so
  `-Wextra` stays quiet.
- `memfn/src/options.def`: the row, and its header sentence.

**Spec (D80)**
- `docs/spec/registry.md`:
  - §6¶7: a `scalar` row is live at both settings;
  - §6¶8a: the row, and the layer/budget sentence;
  - §6¶8b: `memfn` section floor 5 -> **6**.
- `docs/spec/tuning.md`: **§2.43¶3c** (new), the scalar rows' switches.
  This is the section the SIMD-only ¶3b could not hold.

**Tests**
- `tests/memfn/arm_fixtures.c`, five fixtures:
  - `pre-landmark-byte`;
  - `-byte-deny`, the deny in `opts`;
  - `-two-members`, `-optional`, `-later`.
- `arm_fixtures.c` also gains five gate cases: `pre-landmark-miss-token`,
  `-miss-unstated`, `-miss-other`, `-define-floor`, `-define-nonident`.
- `tests/memfn/pins/arms.tsv`: 10 pin rows. No row was re-pinned.
- `tests/memfn/run_arm_pins.sh`:
  - `ARMS_ROW_FLOOR` 102 -> 112, `GATE_CASE_FLOOR` 74 -> 79;
  - **check 14**: the kept landmark run on 770 subjects (every subject
    over { '.', 'a' } up to length 6, from every lo, plus a NULL subject at
    n = 0). It is built with `-fsanitize=undefined`. The reference loop is
    written from memfn.h. It runs the generic deny text too.
- `tests/memfn/rows.tsv`: the row line.
  - reach: `pending-site:REQ-HANDOFF-L1`;
  - witness: fixture `pre-landmark-byte`;
  - signature: `_q = subject_length > search_from ? memchr(`;
  - control: `pre-landmark-byte-deny`.
- `tests/memfn/row_floors.tsv`: pcrec_floor `-`; g2_floor **721**, which is
  floor(0.9 x 802), and the header names the run.
- `tests/memfn/run_rows.sh`: `ROWS_FLOOR` 19 -> 20, `FIXTURE_FLOOR` 29 -> 34.
- `tests/cli/run_cli_tests.sh`: 5 cases.
  - On main, the deny moves nothing at `-fno-memfn-simd` and at
    `-fmemfn-simd`, on dotted4 and on `(ab)c?userpass`.
  - The force spelling is refused, with the kit's own text.
- G2: `memfn/tests/g2/g2_gen.c` (`landmark_one`, `gen_fam_landmark`,
  `--gate-only`, `LMSITES`), `memfn/tests/run_g2.sh` (`FLOOR_ROWS` 19 -> 20)
  and the new file `memfn/tests/run_g2_gate.sh`.
- Mech: the arm `g2gate` in `tests/mech/run_sabotage_matrix.sh`, and the
  rows `tests/mech/sabotages/S800`-`S804`.

**Docs:** `memfn/CLAUDE.md`, `memfn/src/CLAUDE.md`, `memfn/tests/CLAUDE.md`,
`tests/memfn/CLAUDE.md`, `tests/mech/CLAUDE.md`, this report, and its
`docs/dev/lanes/CLAUDE.md` line.

**Not touched**
- `tests/memfn/site_manifest.tsv` is MAIN's file and was not edited. No
  change is needed for this branch: the PRE site's entry is unchanged and
  the row adds no site.
- Request for main: at L1's merge, decide whether the re-entry (the PRE
  site's SECOND use point, `emit_req_reentry_use`) needs a manifest line or
  is covered by the PRE site's existing row. That is main's call, from
  C17's rules.

## 2. Identity on main (ZERO movers)

The base was `build/pcrec` of this worktree at `f18935d4`, built before any
edit and copied to scratch. The population was `--no-corpus
--patterns-file`: every 8th distinct corpus pattern, by emit_sweep's own
`distinct_patterns` rule (4531 distinct, 567 kept, r14b's population). Six
witnesses were added: dotted4, ipv4, ipv6, `(ab)c?userpass`,
`abc[0-9]+xyz` and `(?i)cat`, for 573 in all.

Every arm ran from 08:20:01 to 08:20:47. Each arm's self-check passed
(all-identical, no asymmetry).

| arm | c-default | c-vm | emit-ir-vm | facts | emit-ir-auto (x4) | stderr | dumps |
|---|---|---|---|---|---|---|---|
| SIMD-off | 0 movers (535 reached) | 0 | 0 | 0 | 0 | 0 | 1: `--list-axes`, `+precheck-assign-byte` only |
| `--extra=-fmemfn-simd` | 0 | 0 | 0 | 0 | 0 | 0 | same |
| tree + `--memfn=no-precheck-assign-byte` vs base | 0 | 0 | 0 | 0 | 0 | 0 | same |
| same, plus `-fmemfn-simd` | 0 | 0 | 0 | 0 | 0 | 0 | same |

`make test-memfn-stamps` (SIMD-on FORMS movers: exactly the 3 vrun movers)
and `make test-memfn-simdfloor` (44 movers) are both green.

**Deviation, stated plainly.** My first sweep chain passed `--every 8`.
- In emit_sweep, `--every` samples only the arms and the trace, not the
  argv streams, so the SIMD-off arm ran the FULL argv corpus: 5621
  patterns, plus 384 composition files. It took 89 s (08:17:23-08:18:53),
  pinned to 4 cores.
- Its result is 0 movers on every artifact stream, composition included
  (37 producing files, 106 artifacts). The dumps show 1 mover, the same
  row.
- I stopped the chain with `scripts/safekill` during its second arm and
  reran the sample above. The brief forbade a full-corpus sweep, and this
  was one.

## 3. The row serves rlhbuild's site (scratch, removed)

**The scratch tree**
- `git worktree add --detach <scratch>/rlh lane/rlhbuild` (`39684936`), then
  `git merge lane/r15b`. The only conflicts were docs: lanes/CLAUDE.md and
  then mech/CLAUDE.md, taken as this branch's in scratch.
- The merge was first at `3a16c940`, then re-merged at the tip `d641b3f8`.
  The numbers below are from the tip.
- `lane/rlhbuild` was never written. The worktree was removed with
  `git worktree remove --force` and pruned.

**The three builds compared**
- `gen` is rlhbuild as built: its tip binary, abi 75.
- `new` is rlhbuild + r15b.
- `deny` is `new` with `--memfn=no-precheck-assign-byte`.
- All use `--features all`, with the bench's own pattern files (the `pat`
  files in rlhbuild's cells, read only).

### 3.1 Before/after text

These lines are the same on all three cells. Only the byte differs: `:` (58)
on ipv6, `.` (46) on ipv4 and dotted4.

**Main today (abi 74): the ON_MISS gate through `precheck`.**
```c
    if (subject_length <= search_from ||
        !memchr(subject + search_from, 46, subject_length - search_from))
        return 0;
```
The stamps are `RX_REQ_HANDOFF "none"` and `RX_MEMFN_LIBC "memchr"`.

**Under rlhbuild without R-15 (`gen`): the generic row, at the entry and at
the re-entry.**
```c
    size_t handoff_position = ({ const unsigned char *rx_mf1_s = (const unsigned char *)(subject); size_t rx_mf1_n = subject_length; size_t rx_mf1_lo = search_from; int rx_mf1_a = 1; size_t rx_mf1_r = 0; if (rx_mf1_a) { size_t rx_mf1_c0 = rx_mf1_lo; int rx_mf1_f0 = 0; for (; rx_mf1_c0 < rx_mf1_n; rx_mf1_c0++) if ((rx_mf1_c0 + 1 <= rx_mf1_n && (rx_mf1_s[rx_mf1_c0] == 46))) { rx_mf1_f0 = 1; break; } if (!rx_mf1_f0) rx_mf1_a = 0; rx_mf1_r = rx_mf1_c0; } rx_mf1_a ? rx_mf1_r : (subject_length); });
    if (handoff_position == (subject_length)) {
        return 0;
    }
...
                landmark_position = ({ ...the same loop from scan_position... });
                if (landmark_position == (subject_length)) {
                    return 0;
                }
```
The stamp is `RX_MEMFN_LIBC "none"`.

**rlhbuild + R-15 (`new`): `precheck_assign_byte` at both points.**
```c
    size_t handoff_position = ({ const void *rx_mf1_q = subject_length > search_from ? memchr(subject + search_from, 46, subject_length - search_from) : NULL; rx_mf1_q ? (size_t)((const unsigned char *)rx_mf1_q - (const unsigned char *)subject) : subject_length; });
    if (handoff_position >= subject_length) return 0;
...
                landmark_position = ({ const void *rx_mf1_q = subject_length > scan_position ? memchr(subject + scan_position, 46, subject_length - scan_position) : NULL; rx_mf1_q ? (size_t)((const unsigned char *)rx_mf1_q - (const unsigned char *)subject) : subject_length; });
                if (landmark_position >= subject_length) return 0;
```
- The stamps are `RX_MEMFN_LIBC "memchr"` and `RX_REQ_HANDOFF "4"` (ipv6)
  or `"3"` (ipv4, dotted4).
- The diff `gen` -> `new` is exactly these two statements plus the LIBC
  stamp, on all three cells.
- The `gen` -> `new` diff is also rlhbuild §5.1 item 2's fix. It restores
  the one-`memchr` rejection on landmark-absent subjects (dotted4 x46,
  hcolon x35-53 through the generic loop). I ran no timing here (forbidden);
  the twin is rlhbuild's `newm`.

### 3.2 The deny is rlhbuild's text

`deny` == `gen` byte for byte, `rx.c` and `rx.h`, on ipv6, ipv4 and
dotted4.

rlhbuild's committed `build/rlh/cells/*/src_new` differs from `gen` only in
the abi line: it was emitted before rlhbuild's 74 -> 75 bump. So the
comparison is against the branch tip's binary.

### 3.3 Answers

- The ident runs used et1twin's `etdrv ident`: a find-all pass plus a
  single search from every startpos, on each subject.
- The subjects were rlhbuild's own, read only: the bench copy's `subjects`
  and `throughput` sets, plus 400 adversarial ones per cell. That gives 524
  subjects for ipv6 and ipv4, and 454 for dotted4.

| cell | diff(new, gen) | diff(new, deny) | diff(new, main: rlhbuild's ident.base) | diff(new, libpcre2: rlhbuild's ident.p2) |
|---|---|---|---|---|
| ipv6 | 0 | 0 | 0 | 0 |
| ipv4 | 0 | 0 | 0 | 0 |
| dotted4 | 0 | 0 | 0 | 0 |

- **The corpus subset:** rlhbuild's `tests/litscan/handoff.rxt` holds the
  landmark and re-entry blocks, oracled by libpcre2 and python.
  `tests/harness/run.sh` on it passes 4908/0, and 4908/0 with
  `RXTFLAGS=--memfn=no-precheck-assign-byte`. 11 of its 40 distinct
  patterns render the row.
- In the merged tree, `make test-memfn-rows` (157/0) and
  `make test-memfn-arms` (364/0) are green.

## 4. G2: the landmark site space (written, not blinded)

**Judgement.** I wrote it myself rather than leave it OWED to a blinded
author.
- G2's answers come from `g2_ref.c`, the contract's loop, never from the
  kit. The sites follow memfn.h and r15scope §3.2/§5.2's field list (written
  before this code).
- The risk a blinded author removes is an alphabet inherited from the
  implementation (D27). It is reduced, not removed: the near-miss list is
  r15scope's, not mine.
- **A D27-blinded pass over the same space is still recommended**, at
  main's discretion. It is cheap: the family runs standalone in about 30 s.

**The sites**
- `landmark_one`, part of family `gate`, in section (5)'s two batches.
- It draws from its own RNG stream and id range (2000000), so no older
  site moved.
- 256 sites per call:
  - **hard**: the shape, followed now and then by a run with a fn_ref or a
    set rest. The member steps through all 256 bytes, the miss is stated as
    `n` three ways, and on_miss_leaves is mostly 1.
  - **near-misses**, 15 kinds: 2/3/255/256 members, offset 1 and -1, an
    OPTIONAL term or predicate, ret_pred a later byte, end_back 1, empty
    NOP/EXCLUDED/AT_N, a stated floor, and a miss other than n.

**The standalone run: `memfn/tests/run_g2_gate.sh`**, at the tip,
08:15:52-08:16:21 (29 s).

| check | result |
|---|---|
| generator | 832 sites (320 gate_one + 512 landmark), 806 rendered; the 26 others are gate_one's own `miss-unstated` class, refused naming `miss` as expected; 0 render/refusal/vocab/api/poison/strict failures |
| plain gcc run | 806 gate sites, 11,475,858 checks, 0 failed, 0 faults |
| ASan+UBSan (gcc) | 806 sites, 0 failed, 0 faults |
| LMSITES | hard 256, every member 0..255 covered, near-miss kinds 18/18/18/18/18/18/18/18/16 x7 |
| reach (trace) | `precheck_assign_byte` chosen 802 times |
| CONTROL (W2 mutation 2, the first ` >= ` made ` > `) | 345 of 388 mutated sites killed (88%; floor 80%) |

Floors are literals in the script, measured less ~10%.
- **The row's g2 floor:** `row_floors.tsv` gets 721 = floor(0.9 x 802).
  The quick tier's generator renders the same landmark sites (same stream),
  so its count is at least 802. A quick-tier reading is OWED (§6).
- **`make test-memfn-g2` was not run** (forbidden). Its `FLOOR_ROWS` moved
  19 -> 20, and the landmark sites now sit inside its gate family.

## 5. Sabotage S800-S804 (each solo, each DETECTED)

- Command: `KEEP=1 PROCS=1 JOBS=4 taskset -c 12-15 bash
  tests/mech/run_sabotage_matrix.sh SNNN`.
- Run on the tip `d641b3f8` (08:23:02-08:24:48). The same verdicts also
  came at `a8c77784` (08:21:03-08:22:50).
- Each row's reach is a fixture compile whose `.use` must contain the row's
  line, and each reached (`reach:ok(1/1)`).

| id | plant (memfn/src/precheck.c) | arms | verdict, and what fired |
|---|---|---|---|
| S800 | the landmark searched from `lo + 1` (a later occurrence kept) | memfnarms | DETECTED, 2 fail / 362 pass: the `pre-landmark-byte` pin moved, and check 14 had 321 of 770 cases wrong (every '.' at lo) |
| S801 | the empty test made always true (`(n > lo \|\| 1)`) | memfnarms | DETECTED, 2 / 362: the pin, and check 14's NULL subject hit UBSan: "null pointer passed as argument 1, which is declared to never be null" |
| S802 | a miss stores `lo`, not `n`, and falls through | memfnarms g2gate | DETECTED: memfnarms 2 / 362 (pin; check 14, 120 cases take the hit path on a no-'.' window), g2gate 2 / 7 (176 gate sites failed, plain and ASan) |
| S803 | the row's `opt` NULL (the deny unwired) | memfnarms | DETECTED, 3 / 361: `pre-landmark-byte-deny` renders through `precheck`, not `generic` (check 1, both counts), and its pin moved |
| S804 | `single_byte` widened to any non-empty set | memfnarms g2gate | DETECTED: memfnarms 3 / 361 (`pre-landmark-two-members` renders through `precheck`), g2gate 2 / 7 (53 sites failed; the row was chosen 1042 times, up from 802) |

**Arms.**
- No mech arm runs `test-memfn-rows` (r15scope's S803 concern). S803 needs
  no such arm: `memfnarms` sees it through the deny fixture.
- I added the arm r15scope proposed for G2, as `g2gate`: the gate family
  alone, ~30 s per row. S802 and S804 use it beside `memfnarms`.
- The proposed `memfnrows` arm stays unbuilt: no row here needs it.
- `VALIDATE_ONLY=1` passes all five definitions.

## 6. Validation run, and what is OWED

**Light chain at `fe0fdad9` (08:11:51-08:17:12)**, `make -j4 -Otarget`
pinned. Every row has rc 0 and 0 `*** [` lines.

| target | wall | result |
|---|---|---|
| all | 0 s | ok |
| strict | 10 s | ok |
| test-codegen | 198 s | 27/0 (last section) |
| test-registry | 51 s | green; axes coverage 226 unchanged |
| test-spec-history | 2 s | 145/0 |
| test-cli | 12 s | cases failed 0, the 5 new cases included |
| test-memfn-rows | 1 s | 157/0 |
| test-memfn-arms | 2 s | 364/0 |
| test-memfn-deleg | 0 s | 5/0 |
| test-memfn-stamps | 18 s | 25/0 |
| test-memfn-simdfloor | 26 s | 51/0 |

**Re-run at the tip `d641b3f8` (08:25:01-08:30:32): ALL GREEN.** The
changes after `fe0fdad9` are G2, docs, a comment and the mech rows. Every
target has rc 0 and 0 `*** [` lines:

| target | wall | result |
|---|---|---|
| all / strict | 0 s / 10 s | ok |
| test-codegen | 208 s | ok |
| test-registry | 49 s | ok |
| test-spec-history | 3 s | 145/0 |
| test-cli | 12 s | cases failed 0 |
| test-memfn-rows | 1 s | 157/0 |
| test-memfn-arms | 2 s | 364/0 |
| test-memfn-deleg | 0 s | 5/0 |
| test-memfn-stamps | 20 s | 25/0 |
| test-memfn-simdfloor | 26 s | 51/0 |

The log is `/home/pcrec/.claude/jobs/e99da2a5/tmp/r15b/light2.log`.

**OWED (heavy, the manager's slot)**
1. The FULL identity sweeps against a `f18935d4` base:
   - `scripts/emit_sweep.py --ref-bin <base>`, all streams, `--variant all`,
     `--arms start`;
   - the same with `--extra=-fmemfn-simd`;
   - the deny wrapper (`--bin` running `pcrec --memfn=no-precheck-assign-byte`),
     at both settings.
   - Expected for each: 0 artifact movers, dumps 1 (`--list-axes`).
2. `make test-memfn-g2-full`, and the quick tier `make test-memfn-g2`. The
   quick tier confirms check (e) with the 721 floor and `FLOOR_ROWS` 20, and
   gives the row's quick-tier count.
3. `scripts/perfrun --label r15b -- <log>` (`make test`).
4. The full N2 census: the row must be chosen 0 times on main
   (pending-site).
5. Mech S800-S804 in a batch with the slot's other rows. They were measured
   solo here.
6. `make test-axes`: the new deny is an axis now. On main it must be
   answer-identical and byte-identical.
7. Optional: a D27-blinded review pass over the landmark site space (§4).

## 7. For L1's merge (main): what this branch makes stale on purpose

When `[REQ-HANDOFF-L1]` lands with this row, the following move, IN THE L1
COMMIT, as its single abi event (r15scope §4).

**Red or stale on purpose**
- **The cli case goes red by design.**
  - `run_cli_tests.sh`: "--memfn=no-precheck-assign-byte ... moves nothing
    on (?:\d{1,3}\.){3}\d{1,3}" goes red at both settings.
  - Flip it to "the deny reproduces the generic text" (the `gen` text of
    §3.1), and keep the `(ab)c?userpass` cases (a run landmark: still
    `precheck_assign`).
- **The spec sentences:**
  - `registry.md` §6¶8a's "No pcrec site of this shape exists until
    [REQ-HANDOFF-L1] lands, so today the deny moves no artifact";
  - `tuning.md` §2.43¶3c's last sentence.
- **rows.tsv:** reach becomes `pcrec`.
  - witness `(?:\d{1,3}\.){3}\d{1,3}`;
  - cflags `--memfn=no-precheck-assign-byte`, control `=`;
  - signature `_q = subject_length > search_from ? memchr(` (it appears in
    exactly the row's renderings);
  - the pcrec_floor is the N2 census's.

**The mover proof, r15scope §4 (a)-(e).** It holds as built:
- the deny reproduces L1-alone byte for byte (§3.2);
- the movers are the PRE use lines plus `RX_MEMFN_LIBC`, and nothing else
  (§3.1's diff).

## 8. Charter checklist

| item | status |
|---|---|
| row `precheck_assign_byte`, (ALL_PRESENT, ASSIGN, SET), one byte term, position KEPT, memchr ASSIGN | DONE (§0.1) |
| third row of precheck.c's one renderer, in `arms[]` before generic | DONE |
| deny `--memfn=no-precheck-assign-byte`, the first scalar deny (MF_L_SCALAR), `arm.opt` + `arm_table` opt accessor | DONE |
| deny -> generic renders exactly as today | DONE (§3.2: byte-identical to rlhbuild's text) |
| registry.md §6¶8a row + §6¶8b floor 5 -> 6; the registry coverage pin | DONE. The coverage pin (226) did not move: a memfn row adds no axes_registry check, as with r14's two rows. test-registry green |
| tuning.md | DONE: new §2.43¶3c |
| cli cases | DONE (5) |
| rows.tsv / row_floors.tsv (pending-site, N2 `-`) | DONE. The g2 floor is 721, measured, not PLACEHOLDER (§4) |
| site manifest | not edited (main's file). No change is needed for this branch; L1's re-entry use point is a question for main (§1) |
| ZERO movers on main, light identity incl. -fmemfn-simd | DONE (§2). Deviation: one accidental full-argv arm (89 s), noted |
| the row SERVES the site under rlhbuild: ipv6/ipv4/dotted4 memchr ASSIGN at the re-entered site; the deny == rlhbuild generic byte for byte; answers equal | DONE (§3) |
| scratch worktree removed | DONE |
| G2 gate generator extended with the one-byte ASSIGN SET space, expectations from the contract, with a control | DONE, not blinded (§4; a blinded pass is recommended, not owed) |
| S800-S804 solo, each DETECTED; a missing arm is named and proposed | DONE: all DETECTED; arm `g2gate` added |
| light validation only, pinned, -j4, times recorded | DONE (§6), apart from the §2 deviation |
| report + lanes/CLAUDE.md line | DONE |

## 9. The three standing design questions

1. **Measurement regime: relevant, and not exercised.** No timing was run.
   rlhbuild §5.3 is the twin that justifies the row: the generic loop is
   x1.87 / x4.48 / x46 slower than a memchr ASSIGN on ipv6 / ipv4 / dotted4.
   The official verdict is the bench's (r15scope §5.3).
2. **Independent control: relevant.**
   - Main's identity is a byte diff against a base build, which shares no
     source with the row.
   - The rlhbuild deny equality is against rlhbuild's own binary.
   - The answers are checked against main's and libpcre2's ident outputs.
   - G2's answers are `g2_ref.c`'s; check 14's are a loop written from
     memfn.h.
   - The `g2gate` control is a W2 mutation.
3. **What moves when data is regenerated: relevant, narrowly.** The row
   reads no table, calibration or prior. The member is pcrec's `req_byte`.
