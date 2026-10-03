# c3build: `[OPT-LITSCAN]` S4 commit C3 — the caseless necessary run (lane report)

Lane `c3build` (opus), 2026-10-03. Branch `lane/c3build` from `lane/r1land`
(`d832fc2a`), with main's docs-only r2 design revision merged in first
(`a1abeb81`, one union conflict in the lanes index). **NOT merged.** Built per
`docs/design/litscan_s4.md` §2.3 as revised by r1 and r2, against both rounds
of `docs/dev/reviews/2026-10-03-r1-litscan-s4-c3.md`.

## Summary (resume from here)

| item | value |
|---|---|
| abi | **58 -> 59** (`PCREC_ARTIFACT_ABI`, `ABI_EXPECT`, `match_api.md` §2 guard quote + §6 log, recursion-identity (B) FILEPIN `cc342ddc`) |
| deny bit | **44**, `-fno-req-run-fold` (`PCREC_NO_REQ_RUN_FOLD`), fact-level, masked out of `rx_info.flags` |
| tuning section | **§2.39** (new); §2.27-§2.30, §2.38, §4, §5.4 amended |
| limits.def | `PCREC_MIN_REQ_RUN_BITS` 16 (`bits`, a new unit token), `PCREC_MAX_REQ_RUN_POS_SET` 2; `PCREC_MAX_REQ_RUN_EMIT`'s unit `bytes` -> `positions`; manifest 70 -> 72 |
| sabotage | **S446-S456** — the design's provisional S445-S455, renumbered +1 in order because S445 is C1's (r1land). All 11 validated by plant (table below) |
| `--list-axes` | 115 -> **119 rows / 41 axes** (`run-overlap` +2 rows `words`/`bytes`; new axis `req-run-fold` +2); `registry.md` re-derived |
| registry axis-coverage pin | 177 -> **183** (measured: two new triples, 3 PASS lines each) |

**What it is.** A necessary-run position may be a byte or a two-member cube
`(T, K)` (a caseless letter, `[jk]`, an alternation's one-bit hull). Runs are
ranked by information (`Σ popcount(K)`), floored at 16 bits; an alternation's
common head/tail are the cube hull (`K' = Ka & Kb & ~(Ta ^ Tb)`); the walk's
one position constructor refuses a non-canonical pair as an internal error.
The PICK primitive takes cube candidates (NONE still `rightmost`, inside it);
the window lists members into one MASS call. `req_byte` is the run's scan
member only where it is exact. The pin is the maximal EXACT stretch
(`RunPin.at/len/idx`, rendered `o` or `o:at+len`). The run pre-check compares a
masked run through the run compare's new `words`/`bytes` rows and scans a pair
position as two leapfrogged `memchr` streams, every search inside the block's
guarded loop, dispatched FIRST; K65's `done[]` marks exact positions only;
`req_admit` is NONE only for no byte AND no run. The emitted block is the
design's §2.3.4 block verbatim (`(?i)select` emits it character for character
modulo constants; see `tuning.md` §2.39).

## Validation

**Mac, all on this branch's tip unless stated; logs in the session scratchpad
`worktrees/c3build-scratch/` and, for the archived ones, in
`docs/dev/optloop/s4/`.**

- `make` + `make strict` (gcc-16): green (`strict: whole tree compiles clean
  with -Werror -Wshadow`).
- **Mover manifest** (`docs/dev/optloop/s4/c3_movers.py`, log
  `c3_movers.log`): corpus via `--list-source` x {auto, vm}, bench x {auto,
  vm} x {caps, nocaps}; byte for byte after the abi digit. **PASS: 0
  off-diagonal, deny arm identical on all 7,802 compiled artifact-configs.**
  Auto movers: corpus 30 (15 A1 + 15 C), bench 11 (8 A1 + 3 C) = **41, the
  census's 41 exactly**, class for class. vm and the nocaps configs move the
  same patterns. Sub-populations vs §2.3.7:
  - pins: of the 10 previously pinned movers, 9 keep a pin at the SAME offset
    (now the exact stretch: `a[bc]de` 2:2+2, `(?i)x/1234` 1:1+5, `frank|fred`
    0:0+2, `/abcd[xy]/user` 6:6+2, the emoji/CJK utf8 ones 0:0+3) and 1 loses
    it (`slack`, `offset-set`, which does not read it) — **as predicted**;
  - `RX_DFA_PREFILTER` selections moved: **0** — as predicted;
  - **G1 verdicts `dominated` -> `emitted`: 7, not the predicted 1** — see
    finding 1.
- **Answer differential** (`c3_answers.py`, the design's classification
  table, every startpos, PREFIXES=1 + subjects of length 0..7): **104/104
  movers identical, 125,328 cells, 0 allowed, 0 DEFECT** (`c3_answers.log`).
- **ASan + UBSan sweep** (`-fsanitize=address,undefined
  -fno-sanitize-recover=all -fno-builtin-memcmp -DDIFF_EXACT_SUBJECT`):
  **104/104 identical, 125,328 cells, no report** (`c3_answers_san.log`). Its
  CONTROL reads red: on S455's plant (searches hoisted above the guard) 6 of 8
  caseless movers abort with an AddressSanitizer SEGV
  (`c3_answers_san_control_S455.log`).
- **`tests/litscan/reqcube.rxt`** (python3 `re`-generated, 275 cells, both
  routes per block): 275/0 on this tree AND 263/0 (its pre-min0 version) on
  r1land's compiler — the answers are unchanged, which is the point.
  `verify_rxt.py`: ALL CHECKS PASSED (1 pcre2-only, 4 giveup skips).
- **`tests/codegen/reqcube_check.py`** (wired into `run_codegen_tests.sh` as
  `[OPT-LITSCAN S4 C3]`): 86/0 standalone; canonical form over 3,661 corpus
  patterns: **92 masked rows, all `T & ~K == 0`, popcount 7/8** (floor 46).
  `[K27 pair arm]` NULL driver: both witnesses answer 0 under ASan+UBSan.
- **`run_prechecks.sh`** (re-pinned, see below): **304/0**.
- **`run_cpset_structure.sh`** (one manifest row re-recorded): **28/0**.
- **bit-44 axis over the 17 mover-bearing files** (`SKIP_ORACLE=1
  AXES=-fno-req-run-fold`): **2434/2434 agree, giveup1 0** (`c3_axes_subset.log`)
  — GROUP F2 in `run_axes.sh` is stated empty with these numbers.
- **Linux alpha script** (`alpha_c3.sh`): `build` + `check` smoke-tested on
  the Mac with BASE = `d832fc2a` and this branch: 19/19 cells DENY == BASE
  modulo the abi digit, witnesses moved with a masked REQ_RUN, controls
  unmoved, answers identical on every throughput subject and the 75
  union-select short subjects (all bench subjects sha256-matched the committed
  manifests). `time` is Linux-only.
- **Suites under the Mac lock** (gcc-16, final tip), verdict = make's `*** [`
  lines: `test-rxtsource` green (271 passed / 0 failed, plus the standing
  python-3.9 RECORD); `test-registry` green (all five sub-suites 0 failed);
  `test-codegen` red ONLY on the standing darwin `nm arm_a.o` probe (accepted);
  `test-prechecks`, `test-cpset-structure`, `test-encoding-checks` (slice 250)
  and `test-recursion-identity` (FILEPIN `cc342ddc`) green. Each red met on the
  way and its fix is under "Readers re-pinned". Logs in `c3build-scratch/`.

### Sabotage validation (by plant, scratch tree per row, this tip)

Detector numbers are the reqcube harness's failed cells and reqcube_check's
failed checks on the planted build (clean: 0 and 0).

| row | plant | harness reqcube | reqcube_check |
|---|---|---|---|
| S446 req-cube-crosses-repeat | min-0 repeat joins its body | **16** | 1 |
| S447 pair-scan-one-stream | B = A | **78** | **7** |
| S448 req-pin-takes-masked | run row's term = whole window, exact | **4** | **3** |
| S449 whole-run-unmasked | t[1] loses its mask | **14** | **2** |
| S450 pair-research-behind | re-search bound `pos` | **10** (hang, per-case timeout) | **7** |
| S451 req-hull-keeps-left | round 0's head rule | **8** | 0 (not its arm) |
| S452 set-rest-marks-masked | `done[]` at pair T | **7** (n -> gu) | 1 |
| S453 req-pick-takes-pair | REQ_BYTE = T | 0 (answer-preserving) | **10** |
| S454 pair-dispatch-memchr-first | pair arm unreachable | **78** | **7** |
| S455 pair-search-above-guard | searches hoisted | 8 | **14** (+ ASan red) |
| S456 cube-stores-upper | hull stores the upper member | **60** (internal error refuses `frank|fred`) | 1 |

Re-aimed (anchors moved by this change, intent unchanged): S185 (the pair
arm's tail is now spelled as one `puts`, so S185's anchor is unique again),
S266, S268, S277, S280, S285, S289, S316, S329. `scripts/m6read_check_sab_anchors.py`:
408 rows, all anchors resolve.

## Readers re-pinned (found by grep, D94)

- abi: `src/gen/emit_dfa.c`, `run_codegen_tests.sh` (`ABI_EXPECT` + the
  narrative message's 58->59 clause), `match_api.md` §2's guard quote and §6
  (new "is 59" entry; s4build's became "was 58"), `run_recursion_identity.sh`
  (B) FILEPIN -> `cc342ddc` (the lane's last `src/` commit; (A) is untouched:
  the pre-check sits outside the program region), CHANGELOG.
- limits: `limits_check.sh` manifest (70 -> 72 names + count).
- registry: `registry.md` §6 row/axis count and axis list; `cli.md` §2's flag
  list. The axis-coverage pin in `run_registry_tests.sh` 177 -> 183 with the two
  new triples (`req-run-fold`'s bit 44, `words`'s bit 43) — measured by the
  suite.
- rxtsource: census 261/4395/36325 -> 262/4442/36600 (and RUNSH_* the same
  delta) for `tests/litscan/reqcube.rxt`; C3 PASS +270 (3.14 number inferred),
  SKIP +5 (pcre2-only +1, give-up +4), VERIFIABLE 17056 -> 17326, measured on
  python 3.9 by `verify_rxt.py tests/litscan/reqcube.rxt`.
- Three run-spelling readers `make test-codegen`/`test-encoding-checks` found:
  `runcmp_check.py`'s RX_RUN_WORDS count (now reads the masked spelling too),
  `run_facts_checks.sh` [facts-e3]'s `/abcd[xy]/user` pin (`6` -> `6:6+2`; a
  test-script-only witness outside the census's populations, so a mover the
  manifest could not list; legitimately: the {x,y} cube joins its run window),
  and `run_encoding_checks.sh` DD12a(i)'s REQ_RUN parse (`hex@k/mask`; a pair
  arm's scanned bytes are its cube's members). And one stale since C1:
  `run_wclass_census.sh` [W1] grepped for the five-byte `memcmp` that C1's
  overlap row replaced (red on r1land `d832fc2a`'s own binary too).
- `run_recursion_identity.sh` (A): reqcube.rxt's caseless patterns are the
  gate's first whose `-fno-cls-fold` excuse build crosses CLSPACK's
  11-table-read atom row (`(?i)information_schema`, fold 12 / atoms 0; the
  deny build reads `rx_class_atomN`, the pin has bitmaps), so 1/3/1
  REGION DIFFERS on default/vm/noprefilter. The deny builds are
  region-identical on r1land's binary: a gate gap, not a C3 region move.
  `-fno-cls-pack` now joins a fold excuse build (the `-fno-lit-run` argument).
- `run_encoding_checks.sh` DD12a(i), three more after the parse fix (r1land's
  own tree and binary read 0 failed on the same slice, so all are C3's): the
  pair arm's re-search guards and back-off carry the pick offset K
  (normalized, like the memchr lines); byte and utf8 may take DIFFERENT scan
  forms (utf8's NONE picks the rightmost position, which can be a cube where
  byte's argmin is an exact byte) — excised like a REQ_WHY split, each side
  held to its stamp (a cube scan position must carry the pair arm, and scan
  only its two members); and the prior-keyed prefilter-form bucket admits
  C3's reverse orientation (byte `offset-set`, utf8 `run-pinned`:
  `(frank)|fred`'s run became `fr[ae]`, the model's offsets stopped testing
  the whole run, and the run rows' identity clause holds only under utf8's
  rightmost pick), checked before the data-only K50 bar. 11 -> 13 pairs.
- `run_prechecks.sh`: `[3.1w]` now asserts `REQ_WHY "none"` iff REQ_BYTE AND
  REQ_RUN are "none"; `[3.1b]`/`[3.6b]` check a pair scan position on both
  members (`run_scan_members`); literals moved: `(?i)abc` REQ_RUN
  `414243@1/dfdfdf`; `x(é|è)y` under utf8 REQ_BYTE 121, REQ_RUN
  `78c3a879@3/fffffeff` (the hull joins é/è); `[4.7]`'s alternation decline
  witness `(?:xabcy|zabcw)q` -> `(?:xabcy|wabcv)q` (x/z differ in one bit, so
  the hull now — soundly — claims `[xz]abc`; the decline's intent needs
  branches whose heads differ in more than one bit), and `a(?i)bc`'s reason
  reworded.
- `run_cpset_structure.sh` manifest: `(?i)HeLLo` EMITTED_BYTES 30105 ->
  31220 (+1115, a class-A1 mover), diff-verified; the other 11 unmoved.
- `run_axes.sh`: GROUP F2.
- Spec (D80): `tuning.md` §2.27-§2.30, §2.38 (rows table + example), §2.39,
  §4, §5.4; `match_api.md` §6 + §6.3 (REQ_BYTE, REQ_RUN suffix grammar and
  example, REQ_WHY iff, RUN_WORDS); `findings.md` §4; `facts_listing.md`'s
  value column (mask suffix, `o:at+len`); `limits.md` §3.4a (the `bits` unit;
  the knees carry no anchor, §8b's rule); `findings/design.md` §6.1/§6.2
  (PICK's cube candidates, C2a's candidates); `compare_stack.md` §2's P4 row
  and §5 (keep-it-true); `table_contract.md`: no hunk (the mask rides in the
  `value` cell, per the design).
- NOT regenerated: `tests/findings/manifests/ship_log_movers.txt` /
  `ship_weblog_movers.txt` (design §4 R2-C6). No check reads them (grep:
  only `tests/findings/CLAUDE.md`); regenerating is `findb5_evidence`'s
  four-compiler census over ~14k artifact-configs. **OWED** (finding 6).

## Findings

1. **G1 moves 7 verdicts, not the census's 1.** The census predicted G1 only
   for class C (from BASE's `RX_DFA_PREFILTER_OFFSETS`). Six class-A1
   corpus artifacts whose one-byte pre-check was G1-`dominated` by their
   prefilter's own scan byte now carry a masked run their prefilter does not
   verify (no pin covers the cube position), so G1's first conjunct keeps a
   run pre-check: `c[aA]t`, `c[ac]t`, `([Aa])([ac])d`, `(a(b|c)(d|e))`,
   `(a[bc]d)`, `a-z` (`-i -e utf8`). That is the design's rule applied
   (§2.3.5: elide a run pre-check only behind a scan that verifies the run),
   not a deviation — but it is an extra pass the census did not price. All
   six are corpus witnesses, none a bench cell; bit 44 is the interim kill
   switch if an alpha cell shows it.
2. **§5.4's "(?i)select carries memchr 84 and 116 (T, t)" contradicts the
   design's own stamp** `53454c454354@4/...`: idx 4 is `C`, so the streams
   are 67/99. The check derives the pair from the stamp, never a literal.
3. **§5.4's "`[0-7]ab` takes `words` with one masked byte" is C2's case** (the
   VM run's any-cube domain); C3's position domain is two members, so `[0-7]`
   is not a necessary-run position. The all-`0xFF`-word direction is checked
   on `[0-9]+(?i:a)bcdefg` instead.
4. **The S2b L = 30 witness: libpcre2 10.46 answers MATCHLIMIT (-47), not
   NOMATCH** (its required unit is the caseless `t`, present). Probed once
   over the tailnet; recorded in `reqcube.rxt`'s header. pcrec answers
   NOMATCH (K65's `memchr('S')`). The block is `# pcre2-only` as a python
   TIME exclusion; it has no upstream_issues entry because it is not a
   semantic divergence — flagged in case the manager wants one anyway.
5. **An inline option `(?i)` mid-pattern breaks run contiguity** (its node
   is `rr_none`), so `a(?i)bc` has no run (14 bits after the break). Pre-
   existing property; noted because it shrinks the caseless population for
   patterns written `x(?i)word`.
6. **Owed:** the two `ship_*_movers.txt` manifests; the full-corpus
   `make test-axes AXES=-fno-req-run-fold` (the landing run); the Linux
   alpha (`alpha_c3.sh build check time`, BASE_REV = r1land's tip,
   NEW_REV = this branch); the full `make test` (Linux, the manager's);
   `make mech` rows S446-S456 (validated here by plant, not through the
   matrix driver). `[FINDINGS.B4]`'s data half is the next commit (Q7).

## Files

New: `tests/litscan/reqcube.rxt`, `tests/litscan/gen_reqcube.py`,
`tests/codegen/reqcube_check.py`, `tests/mech/sabotages/S446..S456_*.sh`,
`docs/dev/optloop/s4/c3_movers.py`, `c3_answers.py`, `alpha_c3.sh`,
`c3_movers.log`, `c3_answers.log`, `c3_answers_san.log`,
`c3_answers_san_control_S455.log`, `c3_axes_subset.log`, this report.
Changed under `src/`/`lib/`: `lib/pcrec.h`, `src/core/{axes.def,limits.def,
internal.h,findings.c,findings.h}`, `src/facts/{req.c,facts.c,facts.h,
facts_derive.h,kset.c}`, `src/gen/{runcmp.c,emit_dfa.c,emit_vm.c}`,
`src/dump/axes_dump.c`.
