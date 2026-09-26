# s1step6 — [OPT-LITSCAN] S1 step 6, the Q1 conversion (lane s1step6, opus, 2026-09-26)

Branch `lane/s1step6` from main `54bb1159` (abi 36). Governing spec:
`docs/design/litscan_s1.md` rev 3 §7.2 step 6, §9 item 1, §10, and
`s1build_report.md`'s "Step 6 — what it must re-derive". abi 36 -> 37 as
its own event (S1 merged alone at 36).

## FINDINGS FIRST

1. **Both callers of K66's loop converted together, through the ONE block
   emitter.** The run pre-check's window search and, on the no-DFA-front
   route with a run longer than its window, K66's whole-run search are each
   an `OfsTest` (`ofs_test_run`: the run as one term at offset 0, scanned on
   its member at that member's offset, `maxk = L-1`), derived ONCE by
   `req_run_tests` and read by both `pcrec_emit_req_run_blocks` (file-scope
   `static inline size_t <p>_reqrun` / `<p>_reqrun_whole(subject, n, pos)`)
   and `emit_req_run_check` (one call line each:
   `if (<p>_reqrun(subject, subject_length, search_from) >= subject_length) return 0;`).
   A block cannot be written without its call. `emit_run_scan_loop` and
   `emit_req_run_rest` are gone.
2. **`pf_block_ofs` lost its `DfaForm`** (§1.3's narrowing, s1build's stated
   deviation): `ofs_test_emit_fn(cx, c, p, name, const OfsTest *)` is the
   block; `ofsk_emit_verify`/`ofsk_emit_params`/`ofsk_tbl_name` take
   `(cx, p, t)`. `pf_block_ofs` is its offset-skip comment plus a call. The
   VM `_run` emitter and both DFA entries (`emit_unanchored`, `emit_attempt`,
   under the same `fit.chosen == ENGM_DFA` condition as their call) emit the
   blocks at file scope above the entry.
3. **`Job.req_run` is not forked.** `OfsTest.run_bytes` points into
   `ReqRun.bytes` (window) or `ReqRun.whole` (whole run, scanned at
   `at + idx`); no copy, no new field.
4. **Movers = exactly the prediction, and nothing but the pre-check moved.**
   `docs/dev/optloop/s1/s1step6_movers.py` (base `54bb1159` vs this tip,
   abi-digit normalized): predicted = base stamps `REQ_WHY "emitted"` with a
   `REQ_RUN`. Every artifact: changed iff predicted, every `#define` stamp
   identical, and after removing base's `rp_pos` loop(s) + empty-window line
   and new's block(s) + call(s) the two texts are BYTE-IDENTICAL, with one
   block per old loop carrying the same run and scan byte. **0 bad of 13,348
   artifact-configs**: bench 236 changed / 931 identical / 133 refused
   (caps, nocaps, each also `--engine=vm`), corpus 763 / 10,055 / 1,230
   (auto, `--engine=vm`, `-e utf8`). Transcript `s1step6_movers.txt`, ids
   `s1step6_movers_list.tsv`.
5. **The empty-window `return 0` is gone, by design**: the block's loop
   guard `pos + L-1 < n` is false on an empty window, so `memchr` is never
   reached with a NULL subject (K27) and the block returns `n`. K65's
   `rq_set[]` half still runs only after a block returned `< n`, i.e. on a
   non-empty window.
6. **Two readers the report's own list did not name, found by running
   suites**: `tests/codegen/run_encoding_checks.sh`'s DD12a(i) FREQPICK
   normalizer (it rewrote the loop's `rp_c` guard lines per encoding) and
   `tests/codegen/run_dfa_stamps.sh`'s run-pinned marker
   (`!memcmp(subject + cand` unscoped, which read 63 offset-set artifacts
   with a run pre-check as `run-pinned`; now scoped to the `rx_ofsskip`
   body). Plus `run_prechecks.sh` §4.5b's `"hub_pat_", 8)) break;` needle,
   which contains no `rp_` and so escaped the grep.
7. **S267's REACH had been dead since S1 step 5** (not this lane's
   regression, found here): it grepped default-flag `a=b`, whose pre-check
   G1 elides as `dominated` since S1. Re-aimed with `-fno-offset-skip` onto
   the block's compare and call.
8. **Pre-existing red, not this lane's**: `run_encoding_checks.sh` DD12a(i)
   fails 3 checks on this tip — and identically (same three FAIL lines, same
   11-pattern FINDING list) on a run of main `54bb1159`'s own script and
   build (`/tmp/s1step6/enc_base.log` vs `enc1.log`). Includes the
   byte-"dominated"/utf8-"emitted" run pairs (`ab\K`, `\Kab`), which the
   normalizer never excised for runs before or after this change.

## The commits

| commit | content |
|---|---|
| `dec4e46b` | the conversion (src), pre-abi |
| (next) | prechecks readers + the mover instrument |
| `c9dec3e4` | abi 36 -> 37 + ABI_EXPECT/message + match_api §6; encoding normalizer; S267/S278/S279 re-anchors; S293 — **the last `src/` commit, the (B) FILEPIN** |
| `ca6538af` | FILEPIN, cpset manifest row, dfa_stamps scoping, CLAUDE.md files |
| later | mover census at abi 37, design as-built note, this report |

## abi 36 -> 37 (D76/D94), readers by grep + by suite

`PCREC_ARTIFACT_ABI`; `run_codegen_tests.sh` `ABI_EXPECT` (+ the message's
missing 35->36 clause backfilled with 36->37); `match_api.md` §6 (new top
entry, "gap-free 2 to 37"); `run_recursion_identity.sh` (B) FILEPIN ->
`c9dec3e4`. Byte-count class the grep misses: cpset
`m5_stage1_stamps.tsv` — ONE row, `\bword\b` 27302 -> 27284 (-18),
attributed by a same-basename base/new diff (only the pre-check and the two
abi digits move; it is a predicted mover). `tests/resource`'s `a{5,25000}`
pin: unmoved (dominated, no pre-check). rxtsource census: no `.rxt` added.

## Sabotage

- **S293 (new)**: `ofs_test_run` records the scan member's offset as 0 — the
  arithmetic step 6 moved from the loop's compare (`rp_c - i`) into the
  candidate test (`cand = hit - scan_k`). Target
  `tests/base/k66_precheck_whole_run.rxt` + prechecks.
- **S267** REACH re-aimed (finding 7); plant unchanged.
- **S278** re-anchored onto `req_run_tests`'s whole-run guard (`return 1`).
- **S279** re-anchored (`f->cx` -> `cx`); its plant now also shifts every
  run pre-check's compare.
- S294 unused.

## Bench pin (P2) — mover list

The bench's P2 cells (§10 "On P2"): capability movers are
`file-ext-order`, `keyword-prefix-order`, `router-prefix-order`,
`wild-secrets-github-pat`, `wild-secrets-slack-webhook-url`,
`wild-semdiv-altorder-foo-foobar-rustregex`,
`wild-semdiv-dollar-trailing-newline-pcre2`, `winpath-near-miss` on
vm-caps/vm-nocaps only; `nested-comment-rec`, `tag-depth3-bound`,
`tag-pair-match`, `wild-waf-crs-942500-comment-obfuscation` on all four
configs. So router/keyword/github-pat/nested-comment-rec on forced VM are
§10's "changed program, predicted equal" controls. Full list (85 distinct
bench patterns, 236 configs): `docs/dev/optloop/s1/s1step6_movers_list.tsv`.

## Validation (darwin)

Complete (this lane, darwin, tip at report time):

- `make strict CC=gcc-16`: clean.
- `run_prechecks.sh` 289/0; `run_offset_skip.sh` 25/0; `run_dfa_stamps.sh`
  33/0 (after the marker scoping; 32/1 before); `run_cpset_structure.sh`
  28/0 (after the one-row re-record); `run_form_census.sh` 0 failed;
  `tests/resource/run_resource_tests.sh` 0 failed.
- `make test-codegen`: `run_group: 10/11 scripts passed`, the one red the
  standing darwin `run_inline_capability.sh` nm probe.
- `make test-rxtsource` 255/0; `make test-registry` EXIT 0;
  `make test-recursion-identity` 16/0 ((B) vs `c9dec3e4`: 2,575 identical,
  0 differing; (A) 0 differing). BSD awk prints a `towc` multibyte warning
  in that log on a non-ASCII pattern; the verdicts are unaffected.
- `run_encoding_checks.sh`: 10/3 — the SAME three DD12a(i) reds as main
  `54bb1159` (finding 8); non-vacuity arms (`req_run_offset0` 38,
  `req_pick` 423) hold.
- **K64/K65/K66 witnesses** (`tests/base/k6*_precheck*.rxt`, 49 cases) under
  default, `--engine=vm` and `-e utf8`: 49/0 on both base and tip, and the
  `RXTDUMP` per-case rows (route, trc, answer — give-ups included) are
  IDENTICAL base vs tip on all three flag sets: zero give-up transitions in
  the named population.
- Mover census: finding 4 (0 bad of 13,348).
- Sabotage, single-row mech: **S293 DETECTED** (reach ok, prechecks
  6fail/283pass, corpus 2fail/14pass); **S267 DETECTED** (reach ok, corpus
  752fail/28472pass, prechecks 18fail/271pass); **S278 DETECTED** (reach ok,
  prechecks 3fail/286pass, corpus 8fail/8pass); **S279 DETECTED** (reach
  ok, corpus 29fail/26pass, offsetskip 3fail/25pass); **S285 DETECTED**.

**OWED — the heavy battery, launched DETACHED as this lane's last act**
(`/tmp/s1step6/heavy.sh`, `nohup … & disown`), in sequence, one log each:
`make asan` -> `/tmp/s1step6/asan.log`, `make ubsan` ->
`/tmp/s1step6/ubsan.log`, `make test` -> `/tmp/s1step6/maketest.log`,
`AXES_FULL=1 HARNESS_BATCH=64 make test-axes` (4 h cap) ->
`/tmp/s1step6/axes.log`. Progress/verdict lines in `/tmp/s1step6/heavy.log`:
one `<stage> EXIT=<rc>` per stage and a final `HEAVY-DONE`. Read verdicts
from make's `*** [test-X] Error` lines; for axes also the `AXIS FAIL`
lines and any NEW give-up not in `GIVEUP1_ALLOWANCE` (a new one is a
failure). Known darwin red: the nm probe only.

## Residue (stated)

- On the K66 route the window block stays beside the whole-run block (one
  redundant pass on the 12 K66 movers); dropping it is a D77 question.
- The block scans from `pos + i` where the loop scanned from `pos`: the
  same candidate set, fewer discarded hits; no cost measurement on darwin
  (P2 is the bench's).
- `plan.md` row state not edited (manager's).
