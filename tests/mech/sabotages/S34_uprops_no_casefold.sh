# S34 — the significant-character accumulator stops case-folding: a
# lowercase name byte is stored as-is instead of uppercased. Measured
# against libpcre2 10.46 (tests/probes/probe_uprops.c): ASCII case is
# insignificant in a \p{...} body (\p{l} means the same as \p{L}).
#
# HISTORY (design note §8): this sabotage's first landing was UNDETECTED
# (0/465) because the buffer's only reader — the short-name lookup — folded
# AGAIN on the way in, silently repairing the broken accumulator (the
# control sharing a source with what it controls, one more time). The fix
# made the brace path's lookup FOLD-FREE (uprops_short_lookup expects an
# already-folded byte; only the bare-letter path folds at the call), so the
# accumulator's fold is now load-bearing and `\p{c}` is its pin: sabotaged,
# 'c' is stored raw, misses the UPPERCASE-only table, and flips from the
# GENERIC message to the not-recognised one.
SAB_ID="S34-uprops-no-casefold"
SAB_FILE="src/parse/mod_uprops.c"
SAB_SUITES="reject"
SAB_DESC="pcrec_modport_uprops: the name accumulator stops folding ASCII case"
SAB_DOC_FIGURE="measured at MOD-0.6 phase 2 landing (post-§8 fix): \\p{c} flips from the GENERIC message (offset 5) to the NOT-RECOGNISED message — the fold-free brace-path lookup is what makes the accumulator's fold observable"
SAB_COUNT=1
SAB_BEFORE="        name[sig_count++] = (char)((c >= 'a' && c <= 'z') ? c - 'a' + 'A' : c);"
SAB_AFTER="        name[sig_count++] = (char)c;"
