#!/usr/bin/env bash
# S748 ([SPEC-CLEAN], lane specclean 2026-10-09; landed with an id by lane
# specnum) -- a dated, row-tag-opened revision note planted into
# docs/spec/match_api.md (the shape the facts-only rewrite removed).
# Detector: the spechistory arm, tests/spec_history/run_spec_history.sh --
# match_api.md has no baseline row, so ANY unallowed marker there is red.
# Expected: the five marker classes red (date, addendum, walkback, narrative,
# tagopen), hand-verified at the lane against a scratch copy of the tree; the
# planted paragraph also carries no number, so the numbering check reddens
# with it (a sixth FAIL).
SAB_ID='S748-spec-history-marker'
SAB_FILE='docs/spec/match_api.md'
SAB_SUITES='spechistory'
SAB_DESC='a dated [TAG] ADDENDUM revision note with walkback and panel narrative is planted at the head of match_api.md section 4'
SAB_DOC_FIGURE='Hand-verified at landing (docs/dev/lanes/specclean_report.md, the check section): 5 history-marker FAIL lines; lane specnum adds the numbering FAIL for the unnumbered plant. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S748.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='## 4. Give-up and refusal codes'
SAB_AFTER='## 4. Give-up and refusal codes

**[XYZ-1], 2026-10-09 — ADDENDUM:** this section used to read otherwise; the R99 panel corrected it.'
