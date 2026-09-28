# land85 — TRIAGE + re-pin, main c90e4481 (2026-09-28, lane land85, sonnet)

Chartered to triage land84's two `make test` reds (test-registry,
test-codegen) against main d604bee9 + findtie/optc2/findb6/ucpthink, and to
close the [FIND-TIE] lane's four OWED items (findtie_report.md §7).

## 1. Triage of land84's two reds

The brief's EXPECTED table was **half right**: test-codegen was NOT only the
standing darwin nm probe — there was a real third FAIL between it and the
limits one. Full grep of `/private/tmp/claude-501/-Users-fdicostanzo-pcrec/
land84/make_test.log` for `^FAIL:` finds exactly three lines, at 2139, 2433,
2570:

1. **`[count] --list-limits reports 67 row(s); manifest mismatch`**
   (test-registry, line 2139) — EXACTLY as predicted: `limits_check.sh`'s
   66-name manifest was missing `PCREC_MAX_FIND_CPFREQ_ROWS`
   (`src/core/limits.def:178`, [FINDINGS] B5, landed at d604bee9). Fixed at
   **both readers** (the manifest itself, 66->67 names, AND
   `run_registry_tests.sh`'s own SECOND reader of the row count — it counts
   `limits_check.sh`'s PASS lines rather than citing the manifest number, so
   a grep for "66"/"67" cannot find it; this is the SIXTH time this file's
   own documented class has bitten a landing, per its own comment history).
   `PCREC=build/pcrec bash tests/registry/limits_check.sh` now reads 34/0
   (was 33/1).

2. **`[SABANCHOR] ... a stale or unreadable anchor`** (test-codegen, line
   2433) — **NOT in the brief's EXPECTED list; found by grepping the log
   rather than assuming.** S311's anchor
   (`tests/mech/sabotages/S311_findings_answer_from_other_block.sh`,
   `src/core/findings.c`) quoted `nr = pcrec_find_normalize(fb->counts,
   fr->byte_rate);`, a line findb1's own relocation deleted — the current
   call site is `nr = pcrec_find_block_byte_rate(fb, sv->via, fr->byte_rate,
   NULL);`. Re-derived (not copied): the sabotage's intent is unchanged
   (answer from the chain terminal's block instead of the selection rule's
   block), re-anchored on the new call, and the `fb`/`chain->links[chain->n
   - 1].blocks[0]` substitution adjusted for the new signature.
   `scripts/m6read_check_sab_anchors.py` now resolves all 332 rows (348
   anchor sites); S311 solo-run reads DETECTED (`reach:ok(1/1),
   findings:24fail/63pass`).

3. **`FAIL: nm could not read arm_a.o`** (test-codegen, line 2570) — the
   standing darwin-accepted probe, unrelated to anything in this delivery.
   No action.

No other `^FAIL:` lines exist anywhere in land84's 5,223-line log.

## 2. findtie's four OWED items (findtie_report.md §7)

**(a) §8 witness re-pin + investigation.**
- `w-c2a` (`REQ_RUN`, `github_pat_[0-9]+`): the DEFAULT axis reads real data
  under `-e byte` (`default.rxt` serves `byte-rate` unconditionally there),
  and the two tied `_` occurrences now resolve rightmost (idx 3 -> 7),
  matching findtie's own §5 finding exactly. Re-pinned.
- `w-c4` (`DFA_PREFILTER_OFFSETS`, `(a)\Q(b)\E(c)`, literal "a(b)c"):
  **investigated, not just copied.** The shipped default table ties `(`
  and `)` at ppm=1661 — the run's two rarest bytes. Before the fix,
  `req_run`'s tie-break (leftmost) picked `(` at index 1, which happened to
  agree with the k-set walk's OWN, unrelated, already-rightmost-tied scan
  pick at offset 1 (`src/gen/emit_dfa.c`'s `ofs_test_model`/`us->ofsk`) —
  so `pf_run_applies_common`'s identity clause held, the run-pinned row
  applied, and the offsets stamp tested the whole 5-byte run
  (`0,1*,2,3,4`). After the fix, `req_run` picks `)` at index 3 instead,
  which the k-set walk's own offset-1 pick no longer agrees with — the
  identity clause now DECLINES the run-pinned row for this witness's
  default axis, and the stamp falls back to the un-pinned model's smaller
  set (`0,1*`, 2 offsets). This is a real, mechanically-explained
  consequence of generalizing the tie rule (two independently tie-broken
  PICK readers can legitimately disagree under a genuine data tie), not a
  bug — the witness's own MOVED value (under the `w-c4` bundle) is
  unaffected and was already green. Re-pinned. `PCREC=build/pcrec python3
  tests/findings/gen_adversarial.py witness` now reads 5/5 PASS.

**(b) The explicit guard.** `pcrec_find_run_scan_index` trusted its one
caller's own bound on `n` with no guard of its own — a caller violating it
would silently overrun the fixed `cand[PCREC_MAX_REQ_RUN_SCAN]` buffer.
Added `if (n > PCREC_MAX_REQ_RUN_SCAN) abort();` (this primitive has no
`Ctx` to route an internal-error diagnostic through, so it fails the way
`sb.c`'s own no-error-channel sites do — coding_guide.md's fail-loudly
rule). `make strict CC=gcc-16` clean.

**(c) The corpus-wide mover census**, base main `d604bee9`
(`/private/tmp/claude-501/-Users-fdicostanzo-pcrec/land85/base_d604bee9`,
built via `git archive`) vs this lane's tip
(`docs/dev/lanes/findb5_evidence/ship_census.py`, `POPS=corpus`):

**DEFAULT-PATH (no analysis named), the number this brief asked to be
prominent — corpus, 6,466 artifact-configs (auto+vm x 3,233 distinct
patterns) per encoding, findtie's own [ART-SIZE]-family abi digit
(43->44) stripped from both the generated-by comment and the `.abi = N,`
rx_info initializer before comparing (else literally 100% of artifacts
read "changed" for a reason unrelated to any mechanism — caught live: the
first uncorrected run read `changed: 5751` under `-e byte`, all polluted;
see `/private/tmp/claude-501/-Users-fdicostanzo-pcrec/land85/
default_movers.py`):**

  - **`-e byte`: 134 of 5,751 non-refused artifact-configs move**
    (`{'RX_REQ_RUN,program': 29, 'RX_DFA_PREFILTER,RX_DFA_PREFILTER_OFFSETS,
    RX_REQ_BYTE,RX_REQ_RUN,RX_REQ_WHY,program': 42, 'RX_REQ_BYTE,RX_REQ_RUN,
    program': 44, 'RX_REQ_RUN': 12, 'RX_DFA_PREFILTER,
    RX_DFA_PREFILTER_OFFSETS,RX_REQ_RUN,RX_REQ_WHY,program': 7}`).
  - **`-e utf8`: 0 of 5,796 move** — the default bundle serves `byte-rate`
    under `byte` only, so the utf8 axis is the untouched NONE case, exactly
    as findtie's §2/§8 predicted.

  ship_weblog/ship_log DELTA against findb5's own corpus-only figures
  (153/781 weblog byte/utf8, 315/971 log byte/utf8):
  - `ship_weblog`: byte 153 -> **150** (-3), utf8 781 -> **636** (-145)
  - `ship_log`: byte 315 -> **315** (unchanged), utf8 971 -> **833** (-138)

  `tests/findings/manifests/ship_weblog_movers.txt` / `ship_log_movers.txt`
  re-pinned: the corpus rows regenerated from this lane's own
  `ship_census.json` (POPS=corpus only), COMBINED with findb5's own
  unmoved `bench_ship_census.json` (still on its scratchpad) through
  `make_manifests.py` unmodified — so the shipped manifest keeps its
  established combined bench+corpus shape and only the corpus component
  moved. Combined header MOVERS: weblog byte 203->200, utf8 949->804; log
  byte 409->409 (unchanged), utf8 1139->1001.

**(d) `run_recursion_identity.sh`'s (B) FILEPIN**, re-pinned `51e10961`
([OPT-LITSCAN] F5, abi 42->43) -> **`ed51481b`** (findtie's own, and only,
src commit, abi 43->44; confirmed reachable from main via
`git merge-base --is-ancestor`) — the k64fix/k66fix self-pin convention for
a lane whose own change needs to be its own comparison-(B) baseline. Gate
launched as the chain's own act (§4); see completion line there.

## 3. Validation

Light, run live on this box:
- `make -j4 CC=gcc-16` / `make strict CC=gcc-16` — clean.
- `scripts/m6read_check_sab_anchors.py` — 332 sabotages / 348 anchor sites,
  all resolve.
- `PCREC=build/pcrec bash tests/registry/limits_check.sh` — 34/0 (was
  33/1).
- `PCREC=build/pcrec python3 tests/findings/gen_adversarial.py witness` —
  5/5 PASS (was 3/5).
- `S311` solo mech row: DETECTED (`reach:ok(1/1),
  findings:24fail/63pass`).
- `zzz` manual spot-check (an independent third witness beside the two
  §2(a) hand-derivations): base stamps `RX_REQ_RUN "7a7a7a@0"`/
  `RX_DFA_PREFILTER "run-pinned"` (leftmost of the 3-way 'z' tie), this
  lane's tip stamps `RX_REQ_RUN "7a7a7a@2"`/`RX_DFA_PREFILTER "memchr"`
  (rightmost) — the run-pinned form declines once the scan moves off the
  position the k-set walk independently selected, same mechanism as
  §2(a)'s `w-c4` finding.

**OWED at hand-off — both launched detached (`nohup ... & disown`), not
blocking this report:**
- `S329` solo mech row (pre-report-commit tree `7409ee63`): log
  `/private/tmp/claude-501/-Users-fdicostanzo-pcrec/land85/s329_solo.log`,
  completion line `== mech run COMPLETE`.
- `test-recursion-identity` gate, item (d)'s own validation (relaunched
  with a generous 3600s budget after a first attempt's 900s `timeout`
  self-inflicted-killed it, `docs/dev/learnings.md`-class mistake this
  report records rather than hides): log
  `/private/tmp/claude-501/-Users-fdicostanzo-pcrec/land85/
  recursion_identity.log`, completion line `checks passed:`/
  `checks failed:`.

**OWED — the detached chain (§4), launched as this lane's last act per
BOILERPLATE's DO-THEN-FINISH; re-validates S329/S311 at the FINAL
committed tip (this report's own commit), so the two items above are
corroborating pre-checks, not a substitute.**

## 4. The detached chain

Launched in this worktree (main + this lane's fixes) via
`nohup caffeinate -s bash chain.sh > chain.log 2>&1 & disown`, sequentially:

  (i) `timeout 9000 make test CC=gcc-16`
  (ii) `make test-findings` (rides inside `make test`'s `TEST_SECTIONS`,
       already covers findb6's owed run per the brief)
  (iii) mech rows S329 (this lane's re-derivation) + S311 (this lane's
        re-anchor)

Log: `/Users/fdicostanzo/pcrec/worktrees/land85/chain.log`. Completion
line: `LAND85 CHAIN DONE <rcs>`.

## Files touched

- `tests/mech/sabotages/S311_findings_answer_from_other_block.sh` —
  re-anchored to the current call site.
- `tests/findings/witness/witness.tsv` — `w-c2a`/`w-c4` DEFAULT values
  re-pinned.
- `src/core/findings.c` — `pcrec_find_run_scan_index`'s explicit bound
  guard; `#include <stdlib.h>`.
- `tests/codegen/run_recursion_identity.sh` — (B) FILEPIN re-pinned to
  `ed51481b`.
- `tests/registry/limits_check.sh` — `PCREC_MAX_FIND_CPFREQ_ROWS` added to
  the manifest, 66 -> 67.
- `tests/registry/run_registry_tests.sh` — the second (PASS-count) reader
  of the same manifest, 33 -> 34.
- `tests/findings/manifests/ship_weblog_movers.txt` /
  `ship_log_movers.txt` — corpus rows re-derived for `[FIND-TIE]`.
- `docs/dev/lanes/land85_report.md` — this report.
