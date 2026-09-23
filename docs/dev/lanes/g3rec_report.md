# g3rec — reconcile O-48 against I-91/I-93 (2026-09-23, sonnet, docs-only)

Archived pcrec-bench's [B78]/O-48 answer to `cycle1_ledger_reading.md` §8's
I-91 block (text transcripts only — driver source, build scripts, raw
timing/census/disassembly output — at
`docs/dev/optloop/runs/2026-09-23-i93-8d716693/`, generated `.c`/`.h`/
binaries deliberately excluded per the optvmfl0/ccdiff_step0 precedent) and
appended §9 to `cycle1_ledger_reading.md` (§4.1/§6 untouched, one-line
pointers added at each).

**G3 (PLACEMENT) is REFUTED on x86_64** — no `.part.0` partial-inlining
split exists at either pin, on the box that measures the ledger's own
numbers; `nested-comment-rec`'s +18.8%-+25.0% regression is UNATTRIBUTED as
of now. §4.1's next-ranked hypothesis (2) is not confirmed by Block C's own
disassembly either (`rx_match_anchored` out-of-line at both pins, frame
flat 104 B both pins), so it survives only in a weakened form. Resolved the
`wild-secrets-github-pat` no-`rx_search_run`-symbol fact by compiling it
in this worktree: `RX_VM_ENTRY_SHAPE "inline"` + `RX_VM_FRAMELESS 1`, a
[CC-DIFF] STEP 1 always-inline rung, unrelated to batch 1 — corrects the
brief's own working guess (pinned-start/anchored; the artifact's own
`RX_VM_START` stamp reads `"unanchored"`). The 15-vs-16 program-identical
population gap traced to two different identity criteria (near-full
artifact-text diff vs. record stamp-equality) and the one differing
pattern named (`wild-waf-crs-942360-concat-sqli`). Null band confirmed
two-sided (−5.74%..+8.46%, median −0.08%) by an independent measurement.

**I-98 candidate block** drafted in §9(D): re-run the placement hand-twin
under the bench's own driver/store instead of the noisy `findall.c` one.

Updated `docs/dev/summaries/2026-09-23-optloop-cycle1-exec-summary.md`
(surprise D, the impact table's perturbation row, surprise A's two-sided
band, NEXT STEPS narrowed to `[OPT-PRECHECK-ADMIT]` G1+G2 only) and
`docs/dev/optloop/CLAUDE.md`. Nothing under `src/`/`cli`/`lib`/`tests`
touched beyond one `build/pcrec` compile used to read the emitted C for
the github-pat fact. No suite run — docs-only lane.

Head commit: `60b6c8f2`. Branch `lane/g3rec`, not merged.
