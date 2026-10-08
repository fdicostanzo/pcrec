# b1tri report (triage of decfbB1's test-registry red)

Failed: axes_registry_check.sh "RX_UNROLL_K_WHY (compile.c cx.size_term_why
derivation)" -- 3 FAILs, values '-', 'st-why', 'stwhy' "documented ... that
--list-axes names on no row". Class (a)/(b): B1's `PCREC_CAND_TRACE_REC("stwhy",
"-", cx.size_term_why, "st-why")` sat on the line right after the ternary
chain; the check's extract_prose_values runs from the anchor to the next BLANK
line, so it scraped the trace record's literals. Not load/env.

Fix: one blank line between chain and trace record (replacing one line of the
two-line comment, so no later compile.c line number moves; call_graph /
dec_fallback.md anchors stay valid). Comment-only, no abi.
Solo: make test-registry rc=0; make strict rc=0.
