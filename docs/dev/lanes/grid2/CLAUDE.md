# docs/dev/lanes/grid2/ — the zen4-grid2 timing slot's scripts (lane grid2p, 2026-10-16; REV 3 by lane grid2r3)

The PREP lane's harness for r17b_prime.md §5.4 (D166, D167 option (B), one streamed
condition; lane grid2r3 brought it to rev 3's §5.4 — see `../grid2r3_report.md`): it extends `../grid1/` (reusing its driver, loader, checker, arm-table reader and
legs; grid1 stays runnable as it was — its only edits are two env-gated hooks, `EMIT_CELLS` in
`build.sh` and `ORACLE_CMD` in `check.sh`, both inert when unset). `README.md` is the run
contract (launch command, outputs, status lines, DRY); `../grid2p_report.md` is what was built,
the DRY run's verdict and the wall estimate; `../grid2r3_report.md` is the rev-2 -> rev-3 delta,
the compiler provenance and the re-run verdicts. Everything the slot produces lives in the slot
directory given to `slot.sh` (never committed).

- `README.md` — the run contract.
- `slot.sh` — the slot: build, check FIRST, the required phases, the optional passes; `slot.status` ends COMPLETE or FAILED.
- `build.sh`, `check.sh`, `time.sh`, `f2perf.sh` — the stages; `time.sh` is method `kit-grid@2` (three base copies, the rerun rule, the re-queue).
- `design2.py` — the design (items 1-4, 6-8 as tables), the subjects, the libpcre2 10.46 oracle (`tests/oracle/` local adapter), counts.
- `streamgen.py` — the streamed subject generator, importable by the kit's E4.
- `mkvar2.py` — the four variant generators: `disp` (dispatch twins), `scaf` (walk-in-helper scaffold), `ob` (one-byte arms and NONE), `vm` (the VM_ATTEMPT cell's walk/libc/v1 arms, rev 3).
- `ext_ob/build.sh`, `ext_trig/build.sh` — the ext sets' builders (copied into `<slot>/ext/<name>/` by `build.sh`).
- `provcheck.py` — [rev 3] the compiler's provenance record (commit, abi, sha256, staleness), the arm-signature gate (leg P: re-emission identity, V1/walk signatures, ROUTE stamps, cover shapes) and the manifest census (leg M); build.sh, check.sh (exit 4) and slot.sh call it.
- `paranoid.sh`, `paranoid_check.sh` — the counter-unavailable suggestion (D166 add. 1.1) and its check.
- `plants.sh` — the gate's failing direction for the new arms and (rev 3) for the provenance/census leg.
- `estimate.py` — the full-slot wall estimate from a dry run's measured per-launch costs.

Run with `python3 -I` / `bash`. Compile/check work pins to CPUs 12-15; timing only through `slot.sh` on a quiet box.
