# mechtri2 report: triage of the red mech stage, full suite 20261110_7d74499bc

Matrix: 1225 rows, unexpected 4, anomalies 3, unreached 16 (all 16 carry EXPECTED reasons; not touched).
None of the reds is the K37 line or the axes stale pin (dc1988069): the causes are below.

## STATE AT HANDOFF

Branch lane/mechtri2 (commits after 7d74499bc). Rulings file: none. No memfn/ edits.

| row | class | cause (commit) | fix | proof |
|---|---|---|---|---|
| S1868 compile-check-dropped | CHECK GAP (redundant guard) | u3tgt 0dd11b280 added `pcrec_memfn_target_derive`, which re-resolves the same set per attempt and refuses it as an "internal error: the CPU target set was refused after option parse"; so with the early check in compile.c dropped, pcrec_compile still returned -1 with the kit's text appended, and every cli api cell (rc=-1, text contains the kit's) passed | tests/cli/run_cli_tests.sh: a cell requiring the refusal NOT to be the internal-error one (unknown token and list beside SIMD off) | before: row cli:0fail/287pass (matrix log + my solo run: all api cells PASS with the plant); after: OWED (queued) |
| S706, S708, S711 vmlazy reach rows | CHECK GAP (witness masked) | the whole-pattern required-run pre-check (sar1fix 001c0faf5 / req_whole_run, emitted `rx_reqrun` even under `engine vm`) demands the full `ababac` run, so a one-block subject never reaches the span scan; the reach test is redundant for every literal-block witness in tests/base/vm_lazy_rmin_prefix.rxt | the same rxt gets two class-block witnesses the run test cannot fold to a mask: `z[abc]{3,}?d?` (stride 1) and `(a)(?:a[bcd]){2,}?ae` (stride 2), each default and `engine vm`; expectations from python re | clean: harness on the file 162 pass / 0 fail (was 138). Plant by hand on the emitted C (reach line deleted): `zabd`, `zab`, `aabae`, `aabaex` answer match where clean/python say no match. Stride-1 plant `+2` for `+3` (S711's shape) likewise wrong on `zabd`. Matrix proof OWED |
| S268 req-run-alt-overclaim | STALE ANCHOR (plant no longer compiles) | `rn_better` grew a `w` parameter (sar1/sae walk rework): plant called `rn_better(l.head, r.head)` | plant now `rn_better(w, ...)` plus `(void)rn_common_head;` so the unused static stays warning-clean | scratch tree with the plant builds (rc=0). Matrix verdict OWED |
| S465 width-counts-characters | STALE ANCHOR | `rr_cat` grew `w` | plant now `rr_cat(w, rr_none(1), ...)` | scratch tree with the plant builds; handoff.rxt on that binary: 50 fail / 4858 pass (DETECTED). Matrix verdict OWED |
| S1896 include-not-held | HARNESS/classification | the row (re-aimed at c92313f76, never measured) leaves `<string.h>` inside a target region; the check's cell then fails to compile ("inlining failed in call to always_inline memcpy", gcc 15) besides the 4 red F1 checks; the matrix calls an undeclared compile failure ANOMALY | declared `SAB_EXPECT=COMPILE-CATCH` with the reason; the F1 checks still read 4fail/38pass | matrix verdict OWED (expect DETECTED-BUILD) |

Not touched: the 16 UNREACHED (EXPECTED) rows; S711's recidentity arm reads SKIPPED-no-git-history by design.

Also OWED (not run here): `make test` for the rxt additions (rxtsource census / corpus pins may count cases); the queue job below does only the seven rows.

Jobs: `200-mechtri2-mech` (rows S1868 S706 S708 S711 S1896 S268 S465 on this branch; expect 7 rows, unexpected 0).
Scratch stray: my first solo S1868 run (before TMPDIR was exported) wrote /tmp/pcrec-mech-sabotage.bnqVNR; it was removed.
