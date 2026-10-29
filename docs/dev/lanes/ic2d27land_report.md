# ic2d27land report

STATE: delivered (validation owed: ic2d27-test, ic2d27-mech)

## Summary

The D27 spec-first embedded-C suite (author's record: tests/code/d27/REPORT.md) is in the tree and runs under `make test-code` as arm 12, with a self-checked control. Both diagnostic bugs it found are fixed (no artifact bytes move, abi stays 90), the spec gaps are closed with letter-suffixed paragraphs, and the three masked rows are annotated. Premise reproduced first: 542 passed, 0 failed on the cell layout, and the old main-tree binary shows raw E2 80 AE on stderr.

## Tests landed

- `tests/code/d27/` (run.sh, driver_*.c, cli_cases.tsv 108 rows, match_cases.tsv 71 rows, hdr/, rxt/, REPORT.md, CLAUDE.md). Author expectations unchanged except the ones named under Bug fixes.
- Plumbing only: run.sh builds a scratch cell under `$D27_OUT` (default `$TMPDIR/d27run`) whose `d27/rxt/` holds the fixtures renamed `.rxtin` -> `.rxt`; stored as `.rxt` they were picked up by the harness walk of `tests/code/` (arm 1 went red with 20 HARNESS FAILUREs). The cases still name `d27/rxt/NAME.rxt`, so the `#line` expectations are untouched. The compiler variable is `$RXC` and the bound is `$TIMEOUT_BIN 30`, which the K37 guard in test-codegen requires.
- Wiring: arm 12 of `tests/code/run_code_tests.sh` (no new make section, so no Makefile/shards pin moves). It asserts `0 failed` and floor 545 passes, then runs the same suite with `PCREC=/bin/true` and requires at least 100 failures (measured 219; control goes red, learnings §3).
- Added rows (manager ruling, Bug A/B): `cli.hdr_bidi_refused_no_raw_bytes`, `cli.hdr_nonascii_refused_no_raw_bytes`, `file.hdr_nonascii_refused_no_raw_bytes`, plus stderr regexes on `hdr_control_refused`, `hdr_nonascii_refused`, `hdr_bidi_refused` (escaped `\xNN`) and `ref_cr_lone` (the sentence's last words and offset). Suite is now 545. These six go red on the pre-fix binary (checked).
- Citations: the author's compact two-doc cite form chained match_api numbers onto cli.md and failed test-spec-history; re-spelled with `match_api` inserted (cli_cases.tsv, run.sh, REPORT.md).
- Sabotage S1740 (the `--code-header` echo back to the frame-only escape) and S1741 (the long refusal tail back) in `tests/mech/sabotages/`, suite `code`; field validation: 2 definitions valid. Measuring them is owed (below); a foreground run waited on the box lock behind a queue job and was killed by PID.

## Bug fixes

- Bug A (F1): the `--code-header` shape refusal (`cli/main.c`) and the `.rxt` `code-header` refusal (`src/parse/rxt_source.c`) echoed the value through `pcrec_sb_text`, which numbers control bytes only. Both now use `pcrec_sb_ctext(..., PCREC_CTEXT_COMMENT)`, the existing escaper that numbers every non-printable-ASCII byte (no second escaper; contract note added at its declaration in `src/core/internal.h`). The two `callout` shape echoes (CLI and `.rxt`) had the same hole and take the same call. Observed: `got 'c:"a\xe2\x80\xaeb.h"'`. Side effect: a literal `*/` or `/*` in a refused value is split by that frame (diagnostic only).
- Bug B (F2): not a buffer in the CLI: `pcrec_ext_msgf` cuts a refusal at `pcrec_error.msg`'s 256 bytes (public struct, so the cap stays). The refusal sentence plus the lone-CR `what` ran to 268 bytes. The tail is now "the code a reviewer reads would differ from what gcc compiles" (246 bytes with six-digit offsets), with a comment at the site. The full sentence now ends "... (pattern offset 1)" and `ref_cr_lone` checks that.

## Spec gaps

All edits are letter-suffixed paragraphs; no number moved (`make test-spec-history` green).

1. Code needs the grant, not module `callouts` (design inline_c.md section 2.2 "[r1 D7]": code owns its own rows): match_api §11.9¶1a, pattern_language §7.12¶2a; `PCREC_FEATURE_MODULES` never lists `code-c`, `_CODE_LANGS` discloses it. Not a code change.
2. DEFINE: match_api §11.1¶1a (an uncalled DEFINE group's site is admitted and counted; a reached one is refused). Verified: uncalled builds, called refused.
3. LOCAL rule: match_api §11.9¶8a says why it is unobservable today (§11.1¶1 refuses first; an included fragment's block is no nameable definition). Rule kept.
4. Offset: §11.9¶3a (0-based, decoded text after the tag's `:`).
5. Describe modes: §11.9¶8a (they apply the refusals and the unknown-language refusal; verified for U+202E and `py`).
6. `rx_u8next`: §11.10¶2 (0 return changes nothing, a negative `*i` reads as the end; verified, the loop idiom holds). Not wrong, nothing to stop for.
7. `z == NULL`: §11.10¶2 (outside the contract; verified all of `rx_eq`, `rx_eqi`, `rx_find` dereference it and crash, set or unset span).
Extras the author listed (8-12): 8 repeated/cased language (§11.9¶8a, verified `c,c` ok, `C` unknown); 9 closing-delimiter refusal and the escaped echo (cli §1.22¶2, rxt_format §1.1); 10 header with no segment (§11.9¶8a, verified); 11 column when unpadded (§11.9¶4a, verified columns 9/10 from the code's first byte); 12 `_CODE_LANGS` absent without a segment: not changed; the stamp table row already says "code-bearing", left as is.

Masked rows (F3), kept, each commented: `cond_condition_refused` (conditionals not implemented), `file.include_code_refused` ("no definition" refusal), `file.local_def_delivering_refused` (§11.1¶1 first).

## Validation

At commit 85d99c09d plus the K37 fix (the final commit): 
- d27 suite: 545 passed, 0 failed; control `/bin/true`: 219 failed.
- `make test-code`: 91 checks, 0 failed (arm 12 both PASS lines). test-registry, test-spec-history: green (`make test-code test-registry test-spec-history`, no `*** [test-` line). `make strict`, `make test-claudemd-size`: green.
- `make test-codegen`: first run red on the K37 guard (18 unbounded `$PCREC` sites in d27/run.sh), fixed as above; fixed (`$RXC`, `${PCREC}` spellings), re-run with `make test-codegen test-code`: 19/19 scripts passed, K37 PASS (1470 sites), test-code 0 failed, no `*** [test-` line.
- Not run: `make test` (owed), mech rows (owed).

## STATE AT HANDOFF

- Rulings file: `docs/dev/lanes/ic2d27land_rulings.md` did not exist at any point; no ruling applied beyond the brief.
- Owed: `docs/dev/lanes/ic2d27_job` (make test of this tree, dry-run ok: 81 sections) queued as `655-ic2d27-test`; `docs/dev/lanes/ic2d27_mech_job` (S1740, S1741; dry-run ok) queued as `656-ic2d27-mech`.
- Scratch: `$PCREC_TMPDIR/scratch/ic2d27land/` (logs val1-val3).
