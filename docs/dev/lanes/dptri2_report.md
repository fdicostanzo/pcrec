# dptri2 report

## Summary
The RED job 200-dptri-mech was 13 of 14 rows DETECTED/clean; one row, S3589, was an ANOMALY (BUILD-FAILED). Trailer: `== mech run COMPLETE: 14 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 1 ...)`. It did not die early (258 s is a full 14-row run). Fixed in commit "dptri2: S3589 plant compiles"; no src or emitted-byte change.

## Diagnosis
S3589's SAB_AFTER used `#include S3589_HDR` with `#define S3589_HDR "ucd_" "tables" ".inc"`. A macro-expanded `#include` must expand to a single string-literal token; adjacent literals are not concatenated there (gcc: "extra tokens", "fatal error: ucd_"). So the plant never compiled and the row measured nothing. Not a detection gap, not anchor drift (anchor check: all 1415 resolve), not a box effect.

## Class
A plant that is not valid C in its own context (the row certifies nothing, learnings §3 "witnesses that stopped reaching their site", here never reached). House rule: a plant must build, so its verdict is the detector's. Sibling count: 8 other wall rows (S3575-S3579, S3587, S3588, S3590-S3592) all DETECTED in the same run, so they build; grep for `#include <MACRO>` in plants of S3575-S3592: 1 (this row).
Class-level fix: the harness already reports BUILD-FAILED as an ANOMALY with a zero ceiling, which is what caught it; nothing further needed.

## Fix
S3589 plant is now `static const char s3589_name[] __attribute__((unused)) = S3589_HDR;` (valid C; the wall joins adjacent literals in text, which is the structural rule the row proves). VALIDATE_ONLY S3589 valid; `scripts/m6read_check_sab_anchors.py`: all anchors resolve. The real run could not start by 19:40: the box is held by queue job 200-dptri-sweep (started 19:10, already running, so it could not be cancelled; it tests this tree, and my change touches only a mech row file).

## STATE AT HANDOFF
OWED, queued with not-before 2026-11-25T01:00: `200-dptri2-mech` (S3589 only; expect `== mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0 ...anomalies: 0`) and `202-dptri2-sweep` (emit_sweep vs 2fdbcad38, out build/dptri2_sweep). No rulings file entries (dptri2_rulings.md empty).
