# s1build — [OPT-LITSCAN] S1 steps 1-5 (lane s1build, opus, 2026-09-25)

Branch `lane/s1build` from main `27a63314` (abi 35: K64 fix A, K65, K66,
GIVEUP1 merged). Governing spec: `docs/design/litscan_s1.md` revision 3
(§R3 and the r3 panel binding; D122 addenda 2 and 4). Steps 1-5 of §7.2
built in order; **step 6 (the Q1 floating-run conversion) NOT built** (brief),
§6 below says what it must re-derive.

## FINDINGS FIRST

1. **The mechanism landed as designed, and its movers equal the census BY
   ID.** `s1_movers.py` emits every artifact of `census_b.py`'s own
   populations from the base and from each step's build and joins the
   verdict to the census class (`docs/dev/optloop/s1/s1build_movers.txt`):
   - steps 1-4: **zero** artifacts move (bench 249 identical / 7 refused,
     corpus 5,673 / 715, auto + `--engine=vm`);
   - 5a (G1 widened): exactly classes **A + E** move — corpus 74 + 253,
     bench 6 + 10 (both auto configs);
   - 5b (the rows): exactly **A + E + rowb** — **corpus 505** (74 A, 253 E,
     58 B, 5 B-bounded, 115 C1), **bench 110 artifact-configs**, 0
     unpredicted, 0 predicted-not-moved;
   - `-fno-run-prefilter` on the new build: exactly A + E move (the run
     rows are gone; the admission elisions have no axis);
   - `-fno-offset-skip` on both sides: **zero** move (the pre-`[OPT-K]`
     artifact, as `lib/pcrec.h` promises).
2. **The design's corpus count 513 was 8 too high, and the cause is an
   instrument defect, now fixed.** `census.py`'s `probe()` passed the pattern
   as `pat.decode("latin-1")`, a `str` that `subprocess` re-encodes UTF-8
   into argv — so every non-ASCII pattern was probed as mojibake (`é+` became
   `Ã©+`, whose run `c3 83 c2` pins). The 8 corpus class-B rows (all
   `tests/utf8/`) and 3 bench ones were artefacts. The census now passes the
   bytes; corrected census committed as `census_b_27a63314.tsv`. The same
   defect sat under revisions 1-3's 513 (b5c1423b/4976f385 censuses).
3. **Row (j) was built, run and logged: UNDETECTED (EXPECTED), with a
   measured derivation** (R3-11). A real build with `reseeds = false` on the
   run rows moves **0** artifacts over 151 corpus + 94 bench run-row
   artifact-configs and 21 constructed seeded witnesses; only 2 run-row
   artifacts have a forward seed table (bench `wild-secrets-github-pat`, 0
   edges either way). Derivation (in S284's header): a seed target is a
   start-state variant, a chain head is inside a counted run, and a run row
   needs every byte to the run at a fixed offset, so no run-row machine can
   make a start variant a head. Shipped on S219's precedent.
4. **Sabotage: 6 ids for 11 rows.** S279 (a), S280 (g), S281 (h), S282 (i),
   S283 (k) all **DETECTED** in single-row mech; S284 (j) UNDETECTED
   (EXPECTED). Rows (b), (c), (d), (e), (f) need ids (asked of the manager);
   the structural witnesses for (c), (e), (f) are already `run_prechecks.sh`
   §5.10 rows, so each needs only its plant file. S267 re-anchored onto P4
   (COUNT 2 -> 1) and S270 onto the widened G1, both re-validated by hand
   (plant, build, prechecks): S267 18 fail, S270 8 fail.
5. **R3-1's K65-witness check holds**: `(x?)([a-z]+)+Z.@\1` reads
   `RX_REQ_WHY "emitted"` under both encodings (§5.10). `dfa_cand_scan`'s
   first two lines are the `pcrec_artifact_has_dfa_scan` guard and the
   ENG_ATTEMPT/`attempt_cand` arm, verbatim.
6. **Row (k)**: router under `-fno-offset-skip` stamps `"memchr"` / REQ_WHY
   `"emitted"` (§5.10), and S283 (the bit dropped) turns it red.
7. **A VM hybrid consumes the row with no clause of its own**: `a\K/user`
   is `RX_ENGINE "vm"` with `RX_DFA_PREFILTER "run-pinned"` (§3.2's claim,
   now a corpus cell in `run_pinned.rxt`).

## The commits (one per §7.2 step, then checks/spec/docs)

| commit | step |
|---|---|
| `73cc9fb4` | 1: uint64 deny plumbing (grep recipe + the typed sites; compile.c `pfc_flags`); `--list-axes` byte-identical |
| `d688dae6` | 2: P4 `emit_exact_compare`; REQ_RUN through it; S267 re-anchored |
| `3700f290` | 3: `OfsTest` (`ofs_test_of`, `ofs_test_at`); every offset-skip reader routed |
| `7614aac1` | 4: `PrefixKSets.run_pinned`/`run_o` in prefix_k.c |
| `6be904f7` | 5a: G1 reads the selected row's test (`dfa_cand_scan`, `CandScan`); abi 35 -> 36; S270 re-anchored |
| `6d92764d` | 5b: bit 32 `PCREC_NO_RUN_PREFILTER`, axes.def row, the run-pinned pair, run term, `--list-axes` multi-bit deny, AXIS_DESC, strategy_denials — **the last `src/` commit** |
| later | readers, spec, census fix, witness corpus, sabotage, docs |

## Validation (this lane, darwin)

- `make strict`: clean on step 1 and on the tip.
- `make test-codegen`: **10/11 scripts pass**; the one red,
  `run_inline_capability.sh` ("nm could not read arm_a.o"), is
  pre-existing — identical on a scratch build of the base `27a63314`.
- `run_prechecks.sh` (test-prechecks): **289/0** (§5.10 new: 13 rows).
- `run_dfa_stamps.sh` 33/0; `run_offset_skip.sh` 25/0; `run_form_census.sh`
  1/0 (floors: run-pinned 150, run-pinned-bounded 14 measured);
  `run_scan_edge_census.sh` 14/0 (P1 520 / P2 26 / P3 0);
  `run_cpset_structure.sh` 28/0 after a deliberate 3-row manifest re-record;
  `axes_registry_check.sh` 135/0.
- `tests/offsetskip/run_pinned.rxt`: harness 55/0; python3 `re` 48 PASS /
  7 SKIP / 0 FAIL; 51/51 on the base compiler (the pre-C0-block version).
- `run_recursion_identity.sh` (test-recursion-identity): **16/0** with (B)
  re-pinned to `6d92764d`.
- `make test-rxtsource`: **214/0** after re-pinning the census
  (+1 file / +10 blocks / +55 lines for `run_pinned.rxt`: 220/4016/29224).
- Sabotage, single-row mech: S279-S283 DETECTED, S284 UNDETECTED
  (EXPECTED); S267/S270 re-anchors validated by hand (see findings).
- **OWED**: the full `make test`. It could not start inside the lane: the
  manager's `make test-axes` held the heavy slot (no `EXIT=` line in
  `/tmp/pcrec_axes/axes.log` at the lane's end). The lane armed a DETACHED
  waiter, `/tmp/s1build_scratch/scripts/maketest_after_axes.sh`, which polls
  for that `EXIT=` line and then runs `make test CC=gcc-16` in this worktree;
  log `/tmp/s1build_scratch/maketest.log`, completion line
  `MAKETEST-EXIT=<rc>` at its end (verdict = make's `*** [test-X] Error`
  lines). Known pre-existing darwin red: `run_inline_capability.sh`.
  Also owed: the post-S1 `make test-axes` (the manager's), which now
  includes `-fno-run-prefilter` (bit 32, derived from the header).

## abi 35 -> 36 (D76/D94)

Readers found by grep of `35`: `PCREC_ARTIFACT_ABI`, `run_codegen_tests.sh`
`ABI_EXPECT`, `match_api.md` §6 (new top entry, "gap-free 2 to 36"),
`run_recursion_identity.sh` (B) FILEPIN -> the last `src/` commit
`6d92764d`. Byte-count classes the grep misses: the cpset-structure
manifest's `EMITTED_BYTES` rows (3 re-recorded, all census movers:
`abc`, `(a)(b)(c)`, `(?<=foo)bar`, -543/-543/-188), and
`run_form_census.sh`'s floors. Spec hunks: `match_api.md` §6.3 (9
prefilter values; OFFSETS domain incl. `0*`), `tuning.md` §2.14, §2.29 G1,
new §2.30 (bit 32), `registry.md` (the `|`-joined deny cell).

## Deviations from the design, stated

- `pf_block_ofs` keeps its `DfaForm` parameter; it reads only `f->p`,
  `f->cx`, `f->ofs`. §1.3's narrowing to `(cx, p, const OfsTest *)` is not
  done (no second caller yet — step 6 or VMSEED will need it).
- The run pin is computed on every walk, before the `k0` return, as §1.1
  says; `ofs_test_of`'s two read-back checks are `pcrec_ctx_fail`s.
- `run_prechecks.sh` §3.4b/§4.1/§4.3/§4.4/§4.5 now read the run check under
  `-fno-offset-skip` (S1 elides it on those witnesses by design); §5.5's
  "still emit" floor re-derived 4 -> 1 (literal runs now dominated).
- `probe_b_patch.py`'s vestigial `implies` variable (R3-9) was NOT deleted
  (the probe is a scratch-only instrument; untouched).
- The prose `SAB_DOC_FIGURE` counts of S269/S270/S277/S278 ("278 passed")
  are stale by the new §5.10 rows; not re-measured.

## Step 6 — what it must re-derive on K66's loop (not built)

Q1's conversion turns the floating-run pre-check into a call of the one
search block. After K66 that pre-check is **two callers of one loop text**,
`emit_run_scan_loop`: the window compare (`Job.req_run.bytes/len/idx`) on
every route, and `emit_req_run_rest`'s WHOLE-run compare
(`whole/whole_len`, scanned at `at + idx`) on no-DFA-front VM routes. Step
6 must convert BOTH or neither — K66's "the two cannot compare a run in two
shapes" invariant is exactly what one shared loop bought.

1. **The shape maps exactly.** A presence test over `[pos, n)` for run `R`
   scanned at `i` IS an `OfsTest` with `scan_k = i`, `scan_byte = R[i]`, one
   run term at offset 0 of length L, `maxk = L - 1`: the run is present iff
   the block returns `< n`. The loop's guard pair (`rp_c - pos >= i`,
   `rp_c - i + L <= n`) is the block's `memchr(s+pos+i)` start plus
   `cand + maxk >= n`; its resume (`rp_c + 1`) equals the block's
   `cand + 1` (next memchr from `cand + 1 + i`). The empty-window arm
   (`n <= pos`, K27's `memchr(NULL,..,0)`) is the block's loop guard.
2. **The block emitter must lose its `DfaForm`.** The pre-check is emitted
   in DFA, hybrid AND no-DFA VM search entries; a VM-only artifact has no
   `DfaForm`. Narrow `pf_block_ofs`/`ofsk_emit_verify` to
   `(cx, name, const OfsTest *)` (§1.3's unfinished narrowing) and give
   each block its own name — an artifact can carry the `<p>_ofsskip`
   prefilter AND a pre-check block, and on the K66 route two pre-check
   blocks (window and whole).
3. **Every reader of the loop's TEXT moves**: `run_prechecks.sh` §4.1/4.1b/
   4.1c/4.3 (`!memcmp(subject + rp_c`, `memchr(subject + rp_pos`), §5.9's
   `wholerun()` sed, S267's REACH string and S278's REACH string, and the
   §5.1b/§5.10b `rp_pos` counts. `emit_exact_compare` (P4) is already the
   one compare both would call, so S267's plant site does not move.
4. **The block's comment names `-fno-offset-skip`**; a pre-check block must
   name `-fno-req-run`/`-fno-req-byte` instead — parameterize, and keep
   `emit_comment_safe_byte` for the run bytes (the `*/x` member).
5. **The whole-run term can exceed 8 bytes** (up to
   `PCREC_MAX_REQ_RUN_SCAN` = 32): `OfsTest.run_bytes/run_len` then point
   at `ReqRun.whole` — still the ONE `Job.req_run` field (R3-2); no copy.
6. **K65's `rq_set[]` half follows the converted block unchanged**, and the
   converted block must `return 0` from the search entry on absence (a
   block returning `n` plus one test at the call site), preserving that the
   no-DFA-front route keeps a linear NO-MATCH proof.
7. **Give-up transitions (GIVEUP1's vocabulary, now merged)**: the bar is
   zero unintended transitions with K64/K65/K66's `.rxt` cells as the named
   give-up population — the conversion must keep every NOMATCH they answer.
8. **abi**: §7.2 has step 6 ride S1's abi event. If S1 merges alone at 36,
   step 6 is its own event (37) unless the manager holds S1 for it.

## Files

- `src/`: `core/compile.c`, `core/internal.h`, `core/axes.def`,
  `gen/emit_dfa.c`, `opt/prefix_k.c`, `dump/axes_dump.c`; `lib/pcrec.h`.
- checks: `tests/codegen/run_prechecks.sh`, `run_dfa_stamps.sh`,
  `run_offset_skip.sh`, `run_form_census.sh`, `run_scan_edge_census.sh`,
  `run_cpset_structure.sh` + `manifests/m5_stage1_stamps.tsv`,
  `run_codegen_tests.sh`, `run_recursion_identity.sh`;
  `tests/registry/axes_registry_check.sh`; `tests/axes/run_axes.sh`;
  `tests/offsetskip/run_pinned.rxt`; `tests/mech/sabotages/S279-S284`,
  S267/S270 re-anchored.
- instruments: `docs/dev/optloop/s1/` (`s1_identity.py`, `s1_movers.py`,
  `rowj_reach.py` + outputs, `census.py` fix, `census_b_27a63314.*`).
- spec/docs: `docs/spec/match_api.md`, `tuning.md`, `registry.md`;
  `docs/design/compare_stack.md`; CLAUDE.md files (src/gen, src/opt,
  tests, tests/offsetskip, tests/mech, docs/dev/optloop/s1); plan row.

## Finish — triage S1 reds + sabotage rows (b)-(f) (2026-09-25)

**PART 1, the three S1-battery reds — all diagnosed, none are S1 bugs.**

- **test-codegen**: `run_group: 10/11 scripts passed`, the ONE failure is
  `run_inline_capability.sh`'s standing `FAIL: nm could not read arm_a.o`
  probe. Confirmed pre-existing at the branch point: `bash tests/codegen/
  run_inline_capability.sh` against a scratch build of main `27a63314`
  fails identically. Not S1's; not fixed (nothing to fix).
- **test-registry**: `axes_registry_check` COVERAGE CHANGED, 123 -> 135 —
  a real, legitimate move. The two run-pinned candidates
  (`run-pinned-bounded`, `run-pinned`) each carry a `|`-joined TWO-BIT deny
  cell, and the script's own S1-added multi-bit-deny arm checks EACH half
  as its own (macro, bit, flag) triple: 2 candidates x 2 bits x 3 checks =
  12 new PASS lines (verified against the script's live output — 6 lines
  per candidate, `bit 16`/`bit 32` interleaved — not guessed from the new
  axis count alone, which would predict 6 not 12). Re-pinned to 135 with
  the derivation in the comment. **`bash tests/registry/run_registry_tests.sh`:
  green** (registry_check 226/0, PC-3 210/0, limits_check 29/0 all already
  matched their pins — only the axes arm's own pin was stale).
- **test-resource**: `'a{5,25000}' -fno-scan-edge -fno-start-pinned`
  rescued at 762270 bytes, pinned 762401 — S1's own G1 mechanism now elides
  this witness's require-byte pre-check (the DFA candidate scan for
  `a{5,25000}` already implies byte 'a', so `RX_REQ_WHY` flips "emitted" ->
  "dominated" and the 133-byte memchr-guarded block is dropped; +2 bytes
  from the longer REQ_WHY string nets -131). Confirmed by diffing the exact
  artifact at the branch point (abi 35) against this tip (abi 36) at the
  same `-o` basename: only the abi digit, the REQ_WHY value and the three
  deleted lines move. Re-pinned to 762270 with the byte accounting in the
  comment. **`bash tests/resource/run_resource_tests.sh`: 27/0/0** (was
  26/1).

**PART 2, sabotage rows (b)-(f) — S285-S289, none folded into an existing
row.** All five are genuinely distinct sites from (a)/(g)/(h)/(i)/(j)/(k):
(c)/(e)/(f) needed only a plant file since their structural witnesses
already exist as `run_prechecks.sh` §5.10 rows (the build lane's own
witness table already carries the "(sabotage row c/e/f: ...)" parentheticals
that name them). S285 (b) and S287 (d) needed new witnesses too. All five
validated SOLO via `bash tests/mech/run_sabotage_matrix.sh S28<N>`:
S285/S286/S288/S289 DETECTED; S287 UNDETECTED (EXPECTED) — the defect is
real (confirmed by a hand ASan reproduction, see the row's own header) but
no suite arm in this matrix links generated code against a sanitizer
runtime, and exporting `GENCFLAGS` with `-fsanitize=` into the matrix's own
environment does not thread through to `harness`'s per-case gcc invocation
(measured). `tests/mech/CLAUDE.md`'s S1 table extended to the full eleven
rows.

**Validation run in this finish**: `make strict CC=gcc-16` clean;
`bash tests/registry/run_registry_tests.sh` green; `bash tests/resource/
run_resource_tests.sh` 27/0/0; `bash tests/codegen/run_inline_capability.sh`
confirmed pre-existing at branch point; `bash tests/codegen/run_prechecks.sh`
289/0 (was 289/0 — unchanged by this finish, S285-S289 are new sabotage
DEFINITIONS, not new prechecks assertions); `bash tests/rxtsource/
run_rxtsource_tests.sh` 214/0 (1 recorded, the pre-existing darwin
python-version note); each of S285-S289 solo. Full `make test` NOT re-run
(the manager schedules the next heavy run, per this lane's own boilerplate).
Not merged.
