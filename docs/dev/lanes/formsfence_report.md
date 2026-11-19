# formsfence report

## Summary
The G7 lever fence went red in the cloud because r36 G10's span-head parse rows in tests/cli/run_cli_tests.sh named `--harness=span-head=`. The rows now live in tests/compound/, which the fence already allowlists. The fence allowlist is unchanged.

## Fix
- The rows moved verbatim (refused `-0`, `+8`, `' 8'`, `4096`, empty, `8x`; accepted `08`, `4095`; same option-text check, same harness binary) into tests/compound/run_shell_checks.sh as section (4). They were removed from tests/cli/run_cli_tests.sh, which keeps a one-line pointer that does not name the spelling.
- Sabotage S3286: SAB_SUITES changed from cli to compound, and its description was reworded so it does not carry the fence's spelling. SAB_FILE and the edit are unchanged. The shard table row needs no change.
- tests/compound/CLAUDE.md updated.

## Validation
- tests/compound/run_lever_fence.sh: PASS (3 checks, 4 controls).
- make test-compound: PASS. run_shell_checks.sh reports 15 checks, 0 failed (the 8 new rows included).
- make test-cli: rc 0, cases failed 0.
- S3286: `compound:1fail DETECTED`, at committed HEAD 704a8b8aa. (The first matrix run, at the pre-commit HEAD, was killed with safekill and its /tmp scratch removed.)
- m6read_check_sab_anchors.py: all anchors resolve. make strict: clean.

## STATE AT HANDOFF
Branch lane/memfn-forms, tip see git log. OWED: none
