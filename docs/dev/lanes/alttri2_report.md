# alttri2 — triage of the 210 altcatch-test red (2026-11-07, lane alttri2, sonnet)

Run: `.boxqueue/failed/20261107T104557.584450434-210-altcatch-test/` (make test at lane/altbuild f15a5d4e6,
rc=2). Verdict lines: three sections, `test-memfn-arch`, `test-encoding-checks`, `test-startset`.
All three have ONE cause: the merged-in `tests/altcls/altnf_lookbehind.rxt` (+ `.gen.py`, main's
variable-lookbehind stage 1 meeting the alternation branch's corpus) is a new file that three
instruments had never seen. No answer regression; no engine change.

## Failures

1. **test-memfn-arch** (C4, `run_arch_blind.sh`). Class: stale allowlist (the same shape as the
   `lookbehind_group_alt` rows). Evidence: `NEW architecture vocabulary: tests/altcls/altnf_lookbehind.{gen.py,rxt}
   class 1 (isa-name)`, 2 hits each: the SUBJECT string "adx" (a, d, x), not the ADX extension. Fix 403aa54c8:
   two allowlist rows (count 2 each). Section script re-run: 17 passed, 0 failed.
2. **test-encoding-checks** (DD12a(i) [K50]). Class: stale manifest. Evidence: `1 pair(s) entered the
   gate-refinement class WITHOUT a manifest row. First: (?:cat|bat)(?<=[cb]at|a{1,3}t)s`, the block at
   altnf_lookbehind.rxt:173. The check's own classifier found the byte/utf8 difference data-only (the K50 +1
   alphabet class), so it is the existing class, not a new axis. Fix def03a8cf: one row appended to
   `tests/codegen/manifests/k50_gate_refinement.txt` with a dated comment. `run_encoding_checks.sh` re-run: 14
   passed, 0 failed.
3. **test-startset** (`[vm-movers]`, vmhat_checks.py). Class: unpinned mover manifests (altcatch's open item
   (1)). Evidence: auto 1 and forced 18 `MOVER-NOT-IN-MANIFEST`, every one a block of altnf_lookbehind.rxt, 0
   manifest rows not movers (nothing moved or vanished). Fix def03a8cf: +1 row `manifest_s2_vm_auto.tsv`, +18 rows
   `manifest_s2_vm_forced.tsv` (id, options, pattern hex taken from the check's own population, the mttri
   precedent; dated comment lines). `vmhat_checks.py` re-run: 20 passed, 0 failed. The dfa half and `s3_dfa`
   were already green.

Not touched: `tests/axes/start_landing_movers.tsv` is read only by `make test-axes` (run_axes.sh), not by
`make test`; this triage did not run it, so whether the new file moves it is unknown (altcatch-axes is the
queued run that will say).

## STATE AT HANDOFF

- Branch lane/altbuild, fixes at 403aa54c8 and def03a8cf; this report on top (docs only).
- Rulings file last entry applied: R7.
- OWED: confirming make test queued as `210-alttri2-test` (KEY `alttri2-test`), snapshot of def03a8cf (the
  tests-only fixes; the report commit is docs). Green = no `*** [...test-X] Error` line.
- Scratch: /var/tmp/pcrec-pcrec/scratch/alttri2/ (check logs, the extracted mover rows).
