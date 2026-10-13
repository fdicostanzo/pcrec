# restri — TRIAGE of test-resource red at e842fe537 (lane report)

Lane restri (sonnet), 2026-10-13, `lane/restri` from main `e842fe537`. Tests only; no `src/`.

## 1. What failed
`make test` log (`worktrees/.mgr/mt111b/test.log`): `test-resource` 41 passed, 1 failed. The one FAIL:

    'a{5,25000}' -fno-scan-edge -fno-start-pinned rescued at 762911 bytes, pinned 762884

([K59-PREMUL] drop-ladder rescue byte pin in `tests/resource/run_resource_tests.sh`.) The mechwit
[PF-DROP] witnesses and the K7 identity section passed.

## 2. Cause: stale byte pin, moved by B4's stamp (not the fit rung, not mechwit)
Built main `be9b255e5` (pre-B4) and the current tree, same flags and `-o` basename, and diffed the
artifacts: 762884 -> 762911 (+27). The ONLY differences are the two abi digits (76 -> 77, same width) and
one inserted line `#define RX_COMPOUND "none"` (+27). This is the usual per-abi stamp re-pin; B4 repinned
the other readers but missed this one (it is a size pin, not an abi reader).

## 3. Class and fix
Stale pin, re-pinned with the diff evidence in the pin's history comment (762884 -> 762911). Not a B4
regression, not flaky (deterministic byte count). Mechwit's witnesses are untouched, so the S421/S422/S423
mech rows are unaffected (no witness changed; only a size constant in a non-mech check).

## 4. Validation
`bash tests/resource/run_resource_tests.sh` alone: see result line appended below.
Result: 42 passed, 0 failed, 0 inconclusive, rc=0 (single section, run directly).
