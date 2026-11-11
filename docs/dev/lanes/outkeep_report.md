# outkeep — [CLI-OUTKEEP] `-o` writes only when the bytes change

## STATE AT HANDOFF

Built on lane/outkeep (commit 656690044). Owner build GO: Frank 2026-11-10.

What changed
- `cli/main.c`: `write_file` is the ONE writer behind every `-o` output (matcher `.c`/`.h`, directory `-o`, `--emit-support`, subst), so the rule lands once. Identical existing regular file: untouched (bytes and mtime). Otherwise temp `FILE.pcrec-tmp.PID` (O_EXCL, same directory) then `rename`. Helpers `file_equals`, `write_in_place`.
- Mode choice: a replaced file keeps the old permission bits (fchmod); owner/group are not preserved; a new file gets the umask default (temp opened 0666). Why: build trees expect a 0640/0644 file to stay what it was; preserving ownership would need privilege.
- Non-regular targets (symlink, device, FIFO) are written in place, since a rename would replace the thing named; a symlink to a file keeps its link.
- Errors, each a diagnostic naming the file, exit 1, old file intact: temp creation failure (unwritable directory, even when the old file is writable: a behaviour change from in-place writing), comparison read failure, write error, rename failure (temp unlinked).
- Spec: `docs/spec/cli.md` §1.2¶3-4 (new); `docs/spec/subst_api.md` §10¶2 no longer says the cure is future work.
- Tests: `tests/cli/run_cli_tests.sh` 10 "outkeep:" cases (identical rerun keeps mtime for .c and .h; changed output replaces, no temp left, mode kept; failed compile keeps old file; missing dir; unwritable dir (skipped as root); read-only file replaced; `--emit-support` rerun; symlink). `tests/examples/run_examples_tests.sh` check (5): a second `pcrec -o gen/` over unchanged sources rewrites no file. Mech row S3020 (`tests/mech/sabotages/S3020_cli_outkeep_compare_dropped.sh`, id taken above the highest on main and worktrees, no kit range there).
- Plan row [CLI-OUTKEEP] left STATE:not-started (PL13 refuses started outside Active); status line updated. Manager moves it on merge.

Validated (this lane, light only)
- `nice make -j2`: builds. CLI test script alone: 287 passed, 0 failed. `tests/examples/run_examples_tests.sh` alone: 5 passed, 0 failed.
- `make strict` NOT run (it is a full-tree compile; queued behind the suite is the manager's call): OWED.
- New lines in the test scripts use braced variables (K37); `make test-codegen` (K37/TT-9) is inside the queued make test.

OWED (queued, box busy until ~08:00 Wed)
- `4xx-main-outkeep-maketest` (make test via perfrun; log /var/tmp/pcrec-pcrec/scratch/outkeep/maketest.log, verdict = `scripts/verdict` on it).
- `401-main-outkeep-mech` (S3020 must read DETECTED; log under the queue run dir).
- Not done: a real second-`make` recompiles-nothing test: examples/makefile's rule touches `gen/.stamp`, so its own `make` recompiles by design; the test checks the pcrec rerun instead. Changing that Makefile to drop the stamp is the follow-up if wanted.
