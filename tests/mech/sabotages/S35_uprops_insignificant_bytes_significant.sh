# S35 — the insignificant-byte skip (space, tab, hyphen, underscore) is
# dropped, so every byte in a `{...}` body enters the significant-character
# count and the accumulated name. Measured against libpcre2 10.46
# (tests/probes/probe_uprops.c): `\p{ L }`, `\p{L-e-t-t-e-r}` and similar
# variants all normalise to the SAME property as `\p{L}`/`\p{Letter}` — this
# sabotage is the exact truncation/over-counting hazard the plan's own
# "the buffer is not fixed" warning names: a name with insignificant
# padding now consumes budget it should not, and the accumulated name no
# longer matches what libpcre2 actually reads.
SAB_ID="S35-uprops-insignificant-bytes-significant"
SAB_FILE="src/parse/mod_uprops.c"
SAB_SUITES="reject"
SAB_DESC="pcrec_modport_uprops: space/tab/hyphen/underscore stop being skipped in the body scan"
SAB_DOC_FIGURE="measured at MOD-0.6 phase 2 landing: \\p{L} and \\p{ L } (a space-padded body, both currently GENERIC/known-name) diverge in accumulated name length; the streaming/padding boundary pins move"
SAB_COUNT=1
SAB_BEFORE="        if (c == ' ' || c == '\\t' || c == '-' || c == '_')
            continue;   /* insignificant — measured exhaustively for
                           \\p{L}-vs-variants; does not enter the count */"
SAB_AFTER=""
