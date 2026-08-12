# S34 — the significant-character accumulator stops case-folding: a
# lowercase name byte is stored as-is instead of uppercased. Measured
# against libpcre2 10.46 (tests/probes/probe_uprops.c): ASCII case is
# insignificant in a \p{...} body (\p{l} means the same as \p{L}) and the
# bare-letter short-name table is case-insensitive (\pc compiles same as
# \pC) — this sabotage makes the table lookup (case-sensitive against an
# UPPERCASE-only table) miss every lowercase short name, so `\pc`/`\p{l}`
# move from the GENERIC "requires module" message to the "not recognised"
# one, a tier-1-shaped divergence at the recognition boundary.
SAB_ID="S34-uprops-no-casefold"
SAB_FILE="src/parse/mod_uprops.c"
SAB_SUITES="reject"
SAB_DESC="pcrec_modport_uprops: the name accumulator stops folding ASCII case"
SAB_DOC_FIGURE="measured at MOD-0.6 phase 2 landing: \\pc flips from the GENERIC message (offset 3) to the NOT-RECOGNISED message"
SAB_COUNT=1
SAB_BEFORE="        name[sig_count++] = (char)((c >= 'a' && c <= 'z') ? c - 'a' + 'A' : c);"
SAB_AFTER="        name[sig_count++] = (char)c;"
