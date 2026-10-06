# enctri report: Linux `test-encoding-checks` red on R4a' (lane/memfn-r4a2 @ eef95511)

## Verdict
R4a' owns the red; stage 2 (main 57db5152) is clean. ONE real item, check-side only,
not an emitter break. All seven FINDING pairs and the K50 list mismatch are one cause.

## What DD12a(i) compares
`tests/codegen/run_encoding_checks.sh`: re-emits each ASCII block byte vs utf8 (same
prefix/basename), excises named encoding-owned regions from the TEXT (counted), and demands the
rest be identical (STRICT bucket). K50 manifest: `tests/codegen/manifests/k50_gate_refinement.txt`
(`#UNDECLARED` rows = the 11 exact-match axis-E patterns). It does NOT skip on darwin (source-text
based); the Mac run executes and is green.

## Three-tree results (Linux, `make test-encoding-checks`, ENC_MAX_BLOCKS=250 default)
| tree | result |
|---|---|
| main 57db5152 (stage 2) | 11 passed, 0 failed |
| 28284364 (first parent, pre stage 2) | 11 passed, 0 failed |
| r4a2 kit tip eef95511 | 10 passed, 2 failed (reproduced) |
| Mac main 2b51e6eb | 11 passed, 0 failed (runs, not skipped) |
| eef95511 + this fix | 11 passed, 0 failed |

## Per-pair attribution
| item | owner | class |
|---|---|---|
| `fra(n\|m)k\|frost` (first diff `#define RX_MEMFN_LIBC`) | R4a' | new stamp: byte "memchr,memcmp" vs utf8 "memchr". Byte emits `rx_reqrun` (memchr 'f' + memcmp "fr"); utf8 REQ_WHY "dominated" declines it. The check already excises that block on both sides (`req_run_asym`); the new stamp, an inventory of the artifact's libc calls, follows the block and the check did not know. Not a real encoding break (the byte/utf8 asymmetry is the pre-existing, stamp-declared REQ_WHY one). |
| K50 undeclared-form list mismatch ("reached 4, diverged on 5", first diff `fra(n\|m)k\|frost`) | R4a' | derived from the row above: the sixth strict-diverger is that pattern. |
| `[\Z]` x2, `[$]`, `[\b]` x2, `[\B]` (diff at `rx_forward_accepts_class` / `rx_forward_row`) | pre-existing, expected | these are the 4 manifested axis-E patterns (`\Z`,`$`,`\b`,`\B`), reached identically on all trees; they appear in the FINDING list only because the mismatch left DIVERGE_STRICT unzeroed. Green on main and pre-stage-2. |

## Fix (check-side, uncontroversial)
In the `drop_run` branch of the extractor, `#define RX_MEMFN_LIBC "..."` is normalized to `"N"`
(counted into `req_run_asym`; `MEMFN_LIBC_RE`). Applies only when REQ_WHY differs (the same
condition that excises the block); where stamps agree the line is still compared token for token.
Caveat: on asymmetric pairs the LIBC stamp is no longer compared across encodings (C11 still
holds each artifact's stamp to its own text). `req_run_asym` EXCISED count 20 -> 56 on r4a2.
No `src/` change. Note `drop_run` also fires when the two sides' pick FORMS differ (not only REQ_WHY).

## Sabotage control (failing direction)
On a scratch Linux copy of eef95511 + fix (planted line not committed): for every pair with
`drop_run` False, the utf8 text gets `RX_MEMFN_LIBC "zz,..."`. Result: section FAILS, 10 passed /
4 failed, `218 of 245 strict-identity pairs differ OUTSIDE the named regions`, first FINDING's
first diff `#define RX_MEMFN_LIBC "memchr"`. 218 = the 219 of an earlier (unfixed) sabotage run
minus the one pair (`fra(n|m)k|frost`) the normalization legitimately covers, so the
normalization masks only the drop_run pair. Same tree restored without the plant: 11 passed,
0 failed. (A first sabotage attempt ran without the fix applied because of a bad patch; discarded.)

## Housekeeping
Linux worktrees enctri_s2, enctri_pre, enctri_fix and helper files removed from the box.
