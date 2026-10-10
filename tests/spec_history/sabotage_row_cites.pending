#!/usr/bin/env bash
# PENDING SABOTAGE ROW -- the id is the manager's to allocate (lane specnum,
# 2026-10-09; the lane was told not to take one). To land it: pick a free
# S-id (BOILERPLATE: not inside a range memfn/docs/requests.md reserves),
# replace every `SXXX` below, and move this file to
# tests/mech/sabotages/S<id>_spec_cite_dangling.sh. The suite word
# `spechistory` is already registered in tests/mech/run_sabotage_matrix.sh.
#
# SXXX ([SPEC-CLEAN] / spec numbering) -- a citation of a paragraph that does
# not exist, planted into another spec doc: `match_api.md §9.9`. The numbering
# rule's promise is that a citation which was true stays resolvable (a removal
# leaves a `— retired` stub), and the check that holds it is the citation scan
# in tests/spec_history/spec_cites.py: every `<doc>.md §N` in the tree must
# name a heading or a paragraph label that exists. Detector: the spechistory
# arm. Expected: one FAIL, the `[cites] match_api: dangling citation(s)` line
# naming docs/spec/vars.md; hand-verified at the lane against a scratch copy of
# the tree. The plant adds no history marker and no unnumbered paragraph, so
# the cites check is the ONLY thing that reddens (the other 63 stay green).
SAB_ID='SXXX-spec-cite-dangling'
SAB_FILE='docs/spec/vars.md'
SAB_SUITES='spechistory'
SAB_DESC='vars.md gains a one-line citation of match_api.md section 9.9, which does not exist, so the spec-citation scan finds a dangling number'
SAB_DOC_FIGURE='Hand-verified at landing (docs/dev/lanes/specnum_report.md): exactly one FAIL (the dangling-citation line), 63 pass. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh SXXX.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='# `vars` — caller variables in a pattern'
SAB_AFTER='# `vars` — caller variables in a pattern
<!-- planted: see match_api.md §9.9 -->'
