# l3chk report

STATE: done (local verification green; cloud run dispatched, not awaited)

## Summary
Cloud run 44855950624 shard 13 (DD12a(i)) failed on `(?<=a)(b)\1x` and `(?i)(?<=ab)(b)\1x`: byte states a required run (the byte-only byte-rate tie-break, D123-4, src/findings/default.rxt:42-46), UTF-8 states none. Per R-1 (route 1, "declare it") the DD12a(i) coherence checker is generalized to a run stated on ONE encoding only, the two patterns are listed in the K50 exception list, and route 2 is filed as a plan row. No src/ edit. Premise test: the section reproduced red locally on this worktree build before the edit (3 FAIL lines, as in l3r65tri_report.md).

## Checker change
tests/codegen/run_encoding_checks.sh, the DD12a(i) python (search `[l3chk]`):
- A run stated on one side only: the run-less side's required presence bytes must be covered by the run-bearing side's presence gates plus the bytes its rx_reqrun scans (`have <= want and want - have <= got`); otherwise the pair is reported incoherent. The run-bearing side's own presence gates are then not counted as "pre-check scans" against its REQ_BYTE (`gate_ok`).
- REQ_WHY: (run side "emitted", other side "none") is accepted when exactly one side states a run (the run is that side's pre-check; the per-side stamp-vs-pre-check check still holds each side to its own stamp). Side-agnostic: no pattern allowlist.
- A counter `RUN_ONE_SIDED` is printed.
Earlier re-aims of this same script (git log --since=14.days): 65cbc4c97 (l3tri, 2026-11-20: K < 0 entry move as encoding-owned region, presence order) and c29d6b716 (l3r65, 2026-11-20: witnesses re-aimed for the pick rule). Both read a run stated on both sides; this change is the one-sided form.
Incoherent-case proof: a scratch shim (not committed) rewrote the UTF-8 REQ_RUN stamp of `(?<=a)(b)\1x` from "none" to "6162@1" while the code stays run-free; the checker FAILED (rc=1): "encoding-keyed selection incoherent with its stamp: ... utf8 REQ_BYTE "120" is not REQ_RUN "6162@1"'s member; REQ_HANDOFF byte "-1" vs utf8 "none" ..." (scratch/l3chk/enc_bad.log; the "population collapsed" FAIL beside it is the ENC_MAX_BLOCKS=1 speed-up).
Local result: `bash tests/codegen/run_encoding_checks.sh` rc=0, DD12a(i) PASS (249 strict pairs, 6 undeclared-form rows matched exactly); `make test-cpset-structure` rc=0 (59 checks passed, 0 failed).

## K50 rows
tests/codegen/manifests/k50_gate_refinement.txt: two `#UNDECLARED` rows with the reason (byte-rate prior byte-only, D123-4; stamped selection, not a hot-path conditional; neither side slower than BASE). The script's reached-case list for the undeclared class gained `(?i)(?<=ab)(b)\1x` (the other pattern was already a hardcoded witness).

## Plan row
[L3-BOUNDED-RUN-REFINE] (child of [REQ-LOOKAROUND]) in docs/dev/plan.md: route 2, trigger "L2's design or a measured loss from a bounded run that hands off nothing". `make -s test-plan-lint` passes.

## Validation dispatched
Cloud run: `scripts/cloudrun --owner main --kind test --ref <tip> --name l3chk-test` (see the tip and ref in the reply to main). Not awaited. Local box use ended 23:50 with nice make -j4, failing sections only.

## STATE AT HANDOFF
- Branch lane/l3chk (from lane/l3enc e9be43e92): WIP commit 05ea100ea plus a follow-up fixing the undeclared reached-case list, plus this report.
- Last R-n applied: R-1.
OWED: none (the cloud verdict, shard 13 and the full test, goes to main).
- Scratch: /var/tmp/pcrec-pcrec/scratch/l3chk/ (enc*.log, cpset.log, shim.sh).
