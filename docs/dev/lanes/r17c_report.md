# r17c — R17-b's review fixes, the size-ladder kit rung, U1 (lane report)

Branch `lane/r17c`, cut from `lane/r17b` @ 174f3e320. Every change is inside
R17-b's abi-77 event: no abi bump, and `MF_SITE_ABI` stays 12. The brief and
its dispositions are in `docs/dev/reviews/2026-10-12-r1-memfn-r17b.md`, read
on the memfn-r17 branch. Validation was LIGHT only, and the verdicts are in
§6.

**Headline.** All ten r17c rows of the review are done, and so is the size
rung that main ruled. A new size-cap ladder rung, `drop-kit-bytes`, denies
every kit row whose registry entry declares it byte-adding. The deny set
comes from a new `size` column in `options.def`, and pcrec holds no row
names. The rung's own deny is `-fno-kit-size-drop` (bit 55), and
`--size-cap=refuse` denies it too. Its witness `(?:[a-z][0-9]){1,12520}`
behaves as follows:
- before R17-b it compiled, at 998,805 bytes;
- under R17-b with the rung denied it is refused, at 1,001,024 bytes;
- under R17-b with the rung it compiles again, at 998,811 bytes.

U1, the artifact-level cover check, is a new section of `test-memfn-setfind`.
It covers 476 movers, all equal to the deny arm's table over 256 bytes.
Sabotage rows S867-S870 are all DETECTED solo.

## 1. Disposition table

| id | disposition | status |
|---|---|---|
| A-S1 | `mf_use` refuses a use whose `s`/`n` text differs from the binding | **DONE.** `memfn/src/compose.c` `mf_use` makes the `same_text` comparison against `def_s`/`def_n` on a `decl_point` site. C5 gate cases `use-n-differs`/`use-s-differs` are in `tests/memfn/arm_fixtures.c` and `run_arm_pins.sh`. G2's binding fixture is `check_binding` in `memfn/tests/g2/g2_setfind_gen.c`, surfaced as `[binding]` in `run_g2_setfind.py`. Sabotage S867. Hunks in memfn.h and setfind.md §7.4 |
| A-N1 | pffind.c floor comment | **DONE.** `pf_terms_mask_ct` states its own `pred`/`floor` cells: "the overlapped tail word reads below lo, down to 0: a stated floor declines" |
| A-N2 | trace re-probe shares a source | **DONE via U1**, the disposition's fold: U1's oracle is the deny arm's table, not the cover. The trace-side extensions (re-probe every return; a bitmap `__first`) are **NOT done** and stay unlocks |
| A-N3 | W8 block names `size_t` while called header-free | **DONE.** `pcrec_mfk_w8_first_lane` returns `unsigned` (a lane index below 8), so the block really is header-free (mfk.c's header says so) |
| B-S1 | compile time 3-7x | r17b2's row. U2 (memoize) was not needed by this lane and was **not built** |
| B-S2 | slot25 lacks test-axes and the recursion-identity gate | **DONE** in `docs/dev/optloop/slot25_run.sh` (§5): `make test-axes` (`AXES_FULL=1 HARNESS_BATCH=64`) and `make test-recursion-identity`, printed OWED-AT-MERGE because FILEPIN is unmoved (B-N8) |
| B-S3 | toothless census, alpha and trace judges | **DONE** (§5). Census floors and caps per arm (U5); `alpha_r17b.sh check` returns rc 1 on DENY!=BASE and on NEW==BASE; the c-stream judge reads the census's mover list (`r17b_movers.py --list-movers`, opt-in, default output byte-identical) |
| B-S4 | registry.md row outside its table | **DONE**: the blank line removed |
| B-S5 | tuning §2.43¶3c "the one today" | **DONE**: "There are two today", with `pf-terms-mask` described method-blind |
| B-S6 | `--list-axes` "256-entry" text | **DONE**: `first-class-bounded` and `first-class` descs say "the search kit's find of the next member" / "(the search kit's set find)" (src/gen/emit_dfa.c). A listing mover, declared in §5.2 |
| B-S7 | no pcrec-side mutation test, no artifact-level cover check | **U1 DONE** (§3) plus sabotage S870, S841's shape. **The owed S820-S843 rows stay OWED** to the later lane, as the brief excludes them |
| B-S8 | MF_SET_BUDGET | r17b2's row |
| B-S9 | +2.2 KB per site; the refusal set moves | **DONE** (§2): the rung, its witness, the near-cap census (§4) and the U4 manifest generator plus the variants judge (§5) |
| B-N1 | codegen/assertions CLAUDE.md abi ledgers | **DONE**: `tests/codegen/CLAUDE.md` gains the abi 76 -> 77 entry (R17-b plus r17c); `tests/assertions/CLAUDE.md`'s run_mline_diff entry names the kit form |
| B-N2 | `_Static_assert` under `-std=gnu99 -pedantic-errors` | **DONE**: `__extension__ _Static_assert(...)`. Checked under `gcc -std=gnu99 -Wall -Wextra -pedantic-errors -c`: the default DFA artifact `[0-9]+abc` and the mover `[a-z]+@[a-z]+` compile clean. **Finding:** a VM artifact (`(\w+)@\1 --engine=vm`) fails that build already, on pcrec's OWN pre-existing `_Static_assert(sizeof(rx_frame) ...)`/`_Alignof` lines (DD-14.FB). That is not R17-b's and not fixed here; it is a separate row if the property is wanted |
| B-N3 | match_api §6.3.10¶3 | **DONE**: "which hardware-specific (SIMD) forms the kit rendered, if any (a scalar form never appears here...)" |
| B-N4 | `keeps_storage` names the kit's method | **DONE**: renamed `mf_result.needs_const_subject`: "1 iff the chosen form requires the subject inputs (`s`, `n`) of the body holding its uses to be const there". pcrec's `MemfnFind.needs_const_subject` and the comments at emit_dfa.c/emit_vm.c/internal.h say what pcrec acts on. MF_SITE_ABI stays 12 |
| B-N5 | registry row describes the method | **DONE**: the registry.md row and the options.def doc are method-blind |
| B-N6 | test-spec-history red | not this lane's. Still red at this tip, on the same pre-existing line citations (slot24_triage.md, responses.md:2303, plus `2026-10-12-r1-match-split-pinonly.md:78`), which clear at the merge of main. The `limits` numbering red was mine (¶2b placed before ¶2a) and is fixed |
| B-N7 | `tolower` locale-dependent | **DONE**: `valid_prefix` folds through `pcrec_ascii_fold` (the locale-free partner table) |
| B-N8 | FILEPIN | at the kit-branch merge (named OWED in slot25_run.sh) |

## 2. The size-ladder kit rung (B-S9, ruled by main 2026-10-12)

**The kit's declaration.** `MF_OPT` gains a column `size` (`MF_SZ_ADDS` |
`MF_SZ_NEUTRAL`) before `doc`. ADDS means the row's form can emit more of the
bytes the caps count than its deny renders. Only `pf-terms-mask` declares
ADDS. The SIMD rows are NEUTRAL because their bytes are all guarded
(limits.md §8.3). `precheck-assign-byte` is NEUTRAL by its form and labelled
UNMEASURED, because no main site states its shape. Two new accessors:
- `mf_opts_size_relief(buf, n)` writes the `--memfn=` deny set, `no-NAME`
  comma-joined, and returns its length snprintf-style;
- `mf_art_sized(art)` is 1 iff some site of the art chose an ADDS row.

`--list-axes`' memfn section prints the column (`adds`/`neutral`), and
registry.md §6¶6 documents it.

**pcrec's rung.** `fit_rungs[]` gains the row `drop-kit-bytes`, right after
`unroll-rescue`: limits.md §8.4 row 2, both engines. Its cells:
- `degrading`, `fof` IN: `--size-cap=refuse` denies it;
- its own deny `PCREC_NO_KIT_SIZE_DROP`;
- `restart` true: the VM size term restarts;
- cells `ESEL_SIZE_CAP_RETRY`;
- an stderr note: "dropped the search kit's byte-adding search forms --
  each such search site takes its smaller form...".

It applies where the refused attempt's art chose an ADDS row
(`pcrec_memfn_art_sized`) and the rung has not fired yet. It reads its state
from the fired record (`fit_kit_dropped`), the shape `anchored_dropped`
already uses, so FitSets and the anchored sabotage lines did not move.

Once the rung has fired, every later attempt sets `defo.memfn` to the
caller's string plus the deny set. `pcrec_memfn_relief_opts` builds it after
the setjmp, in the attempt's arena, so an allocation failure routes through
`pcrec_ctx_nomem`. Every other attempt reads the caller's own string
(`user_memfn`).

Two more consequences of the new row:
- `COMPILE_MAX_ATTEMPTS` gains one retry and one ladder run, and the trace
  build's `fit_attempt_bound` equality holds it;
- `fit_seq_legal` gains the rung's ten transitions.

The flag:
- it is in `axes.def` and `lib/pcrec.h`, and masked from `rx_info.flags`;
- it has R17-b's tuning.md `drop-kit-bytes` section (lane/memfn-r17 only) plus its index, table and mirror rows;
- registry coverage goes 229 -> 232;
- **bits: 56 used, 8 free**, above the <=4 IFACE trigger.

Ordering is not tuned. R17-b's limits.md rung-2 paragraph (lane/memfn-r17 only) says: "Rung 2 is the first retry
because it costs only search speed... The rung's position follows from that
cost, not from a measurement of how often it rescues a pattern."

Spec readers, found by grep:
- limits.md §8.4: the table, ¶2, the new ¶2b, ¶2a and ¶3 renumbered;
- limits.md §8.5: ¶1a new, ¶2-¶6 renumbered;
- R17-b's tuning.md `drop-kit-bytes` section (lane/memfn-r17 only) and §2.43¶3c;
- registry.md §6¶6/¶8a.

cli.md §1.15¶5 does not enumerate rungs, so it is unchanged.
**`ir_listing.md` has no rung table** (grep finds no ladder row there), so it
is unchanged.

**The witness, and the brief's pin.** The brief's
`(?:[a-z][0-9]){1,13000}` **refused before R17-b too**, at 1,037,212 bytes
at 010b612c9, so it cannot "compile again". Its pin in
`tests/resource/run_resource_tests.sh` (1,034,779) was stale. It now reads
1,037,211 with the three measured figures in a comment; the field is printed,
never compared.

The real witness, found by bisecting N against the ref build, is
`(?:[a-z][0-9]){1,12520}`, measured at each stage:

| compiler | outcome | bytes |
|---|---|---|
| 010b612c9 (before R17-b) | compiles | 998,805 |
| this tip with `-fno-kit-size-drop` | refused | 1,001,024 |
| this tip (the rung) | compiles | 998,811 |

The tip's 6 extra bytes are `ENGINE_SEL "size-cap-retry"` in place of
`"selected"`. These are new cells in run_resource_tests.sh:
- the default rescues it: the note, no `__next_candidate(&`,
  `RX_ENGINE_SEL "size-cap-retry"`;
- `-fno-kit-size-drop` and `--size-cap=refuse` both refuse it;
- the control `--memfn=no-pf-terms-mask` fits with no rung.

All PASS in `test-resource`.

## 3. U1, the artifact-level cover check (B-S7)

`tests/memfn/setfind_cover.py`, run as `run_setfind.sh` section 5
(`test-memfn-setfind`, mech arm `setfind`). It takes every 10th distinct
corpus pattern, at byte, `--engine=vm` and `-e utf8`. For each mover:
- its deny artifact is compiled at the same prefix;
- the sites are paired in text order, each walk's table being the last
  declaration of its name above it;
- the default artifacts are compiled in batches of 40, one prefix each, one
  translation unit.

Then `__member(x)` is checked for every x, and `__mask` for every byte at
every lane under four fills plus 4,096 random words, against the deny table.
It never calls the kit. It took 7.7 s.

First run: 455 patterns, **476 movers / 476 stems, 0 mismatches** (byte 95,
byte-vm 282, utf8 99). The floors floor(0.9 x) are 428/428/85/253/89.
Sabotage S870 is S841's shape: pcrec hands the kit the set with byte 0x00
flipped. It is DETECTED at `setfind:435fail/31pass`, the U1 mismatches.

## 4. The near-cap census (B-S9)

`docs/dev/lanes/r17c_nearcap.py --nearcap` was written by a sonnet helper
under this lane. It generates set-site shapes, bisects N on the BASE compiler
until each lands within 8% below or above a cap, and judges compiles-both /
refuses-both / BAD-refusal-moved on byte, byte-vm and utf8, with a floor of
40 per arm. The caps covered are max_emit_bytes, max_emit_code_bytes and the
DFA goto state cap.

**RESULT, at 2fdc4215b vs 010b612c9 (all three arms plus byte-dfa,
`build/r17c-scratch/light3/nearcap.log`, committed as
`docs/dev/lanes/r17c_nearcap.out`):**
- **BAD 0** over 88 candidates.
- Within 10% of a cap: byte 25, byte-vm 20, utf8 25; plus 6 state-cap
  candidates per arm, and 6 on byte-dfa.
- The set-site shapes cross the cap exactly where the rung must act, at the
  x1.000 rows:
  - `rep_cd` N=7484: base ok 999,865, tip ok 999,871;
  - `rep_w` N=7494: base ok 999,917, tip ok 999,923;
  - `cat_cls` code N=1373: base ok 501,124 / 499,656, tip the same bytes.

  Each compiles on both sides. The tip's +6 is `ENGINE_SEL
  "size-cap-retry"`, and the x0.94/x0.96 rows show the kit's +2.2 KB that
  would have refused them without the rung.
- The helper's suggested floor of 40 per arm is NOT met: the shape families
  reach no more (NOGROW/UNREACHED notes in the log), so rc 1 came from the
  floor. The floors are now pinned per arm at floor(0.9 x measured): byte
  22, byte-vm 18, utf8 22.

`--u4 OUT` writes the lowered-cap predicted-mover manifest that slot25's
variants judge reads. It was NOT run at this tip; the slot runs it.

## 5. slot25 and the alpha

### 5.1 The script changes

- **`docs/dev/optloop/slot25_run.sh`** is a COPY of
  worktrees/memfn-slot/slot25/run.sh. That directory is outside this
  worktree, and main was told the copy lives here. Every addition is a
  `# ---- r17c: ... ----` block, and every block prints a `*_JUDGE` line.
  The additions:
  - U5 pins: `CPIN_MOVER_FLOOR` is the .out's movers less 2%, and
    `CPIN_DECL_CAP` is byte=39 byte-vm=44, with no slack. Re-pin both after
    r17b2.
  - the near-cap census and the U4 manifest;
  - the variants judge against the manifest;
  - the c-stream judge against the census mover list;
  - test-axes;
  - recursion-identity, printed OWED-AT-MERGE.
- **`alpha_r17b.sh`**: `check` now returns rc 1 on DENY!=BASE and on
  NEW==BASE, as its header documents.
- **`r17b_movers.py`**: an opt-in `--list-movers FILE` in a delimited block.
  Without the flag its output is unchanged.

### 5.2 The dumps-stream movers to expect against KREF

These are the `sw listing` dumps. The diff of `--list-axes`, 010b612c9 vs
this tip:
- `prefilter` rows 7-8 (the two descs);
- `fallback`: row 7 `drop-kit-bytes` inserted, and the old rows 7-11
  renumbered 8-12;
- the memfn section: three comment lines, the header's `size` column, the
  `size` cell on every row, and the `pf-terms-mask` row (R17-b's).

Nothing else moves.

### 5.3 How far the scripts are validated

A sonnet helper of this lane wrote these files and never sent its report.
They are validated as follows:
- `bash -n` for both shell scripts and `py_compile` for both python
  scripts;
- `--nearcap` by the full run in §4;
- `--list-movers` read by eye: it is a delimited, opt-in block, and the
  default output is unchanged by construction.

Two parts were never exercised: slot25_run.sh's judges, which run only
inside the slot, and `--u4`. Treat both as first-run code at the slot.

## 6. Light validation (Linux dev box, `taskset -c 12-15`)

Logs: `build/r17c-scratch/light1/` (first pass, before the fixes below),
`light2/` (strict, registry, mech), `light3/` (re-runs and the near-cap
census).

| suite | verdict | log |
|---|---|---|
| `make -j4` | clean, no warnings | — |
| `make strict` | rc 0 | light2/strict.log |
| test-registry | rc 0 (light1 red only on the coverage pin 229 -> 232, re-pinned) | light2/test-registry.log |
| test-memfn-arms, -link, -rows, -stamps, -manifest, -forms, -deleg, -reach, -arch, -guarded, -simdfloor, -rank | all rc 0 | light1/ |
| test-memfn-setfind | rc 0, 38 checks incl. U1 | light1/, light3/ |
| test-memfn-g2 (quick) | rc 0, 52,987,688 checks, 0 failed; setfind family 22 checks incl. `[binding]` | light1/test-memfn-g2.log |
| test-startset | rc 0 | light1/ |
| test-cpset-structure | light1 red: the 4 manifest rows +32 (the W8 text), re-recorded; then 59 passed / 0 failed | light1/; re-run by hand |
| test-rxtsource | rc 0 | light1/ |
| test-resource | rc 0, incl. the 4 [KIT-SIZE-DROP] cells | light1/test-resource.log |
| test-spec-history | red on B-N6's pre-existing line citations only (slot24_triage.md:168/170/185, responses.md:2303, 2026-10-12-r1-match-split-pinonly.md:78), after this lane's ¶2b order fix | light3/, light4/ |
| test-codegen | light1 red on two causes, both fixed: (a) the residual scanner read `__extension__ _Static_assert` as an entry (8 FAILs); (b) S238's anchor matched the new row's cells line (3 vs 2). light3 found a third cause, an apostrophe in the awk comment of fix (a), also fixed. `run_codegen_tests.sh` standalone after the fixes: 330/1, the 1 being SABANCHOR (b), since fixed; `m6read_check_sab_anchors.py` reports all 713 resolving. **Final group re-run (light4): rc 0, 16/16 scripts passed** | light1/, light3/, light4/test-codegen.log |
| mech solo S867 | DETECTED (memfnarms 1 fail, setfind 2 fail) | light2/mech_S855.log |
| mech solo S868 | DETECTED (resource 1 fail) | light2/mech_S856.log |
| mech solo S869 | DETECTED (resource 1 fail) | light2/mech_S857.log |
| mech solo S870 | DETECTED (setfind 435 fail) | light2/mech_S858.log |

S-ids: the lane took S855-S858 provisionally, but main had allocated those to
endmark (D164). The kit manager renumbered the rows to MAIN'S allocation,
S867-S870, after delivery (files, ids and mentions; the solo logs keep their
old names). Field validation passes on the renamed rows; slot25's full mech re-measures them.

## 7. OWED

- The full `make test`, mech, sweeps and timing are the manager's or the
  slot's.
- S820-S843, T2/T4, Q8/Q10 and the disassembly check go to the later lane.
- FILEPIN at merge.
- Re-pin slot25_run.sh's `CPIN_*` after r17b2's census.
- The trace-side A-N2 extensions.
- A VM artifact's gnu99-pedantic build (pre-existing, §1 B-N2).
