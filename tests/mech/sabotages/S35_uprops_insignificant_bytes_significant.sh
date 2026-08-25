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
# [MECH-REACH, 2026-08-25] THIS ROW DECLARES ITS WITNESS'S REACH.
# THE WITNESS IS A BODY WITH AN INSIGNIFICANT BYTE IN IT. `\p{ A}` is
# a ONE-significant-character name on the clean tree (the space is skipped)
# and therefore gets the one-letter-code sentence; with the skip deleted it
# is a TWO-character name and takes the generic path. A body with no space,
# tab, hyphen or underscore in it cannot see this edit at all.
SAB_REACH='"$PCREC" --features none -p rx -o "$REACH_TMP/o0.c" -- "\\p{ A}"'
SAB_REACH_EXPECT="\\p{...}: not a one-letter Unicode property code pcrec recognises — requires module 'unicode-props' (pattern offset 6)"
SAB_COUNT=1
SAB_BEFORE="        if (c == ' ' || c == '\\t' || c == '-' || c == '_')
            continue;   /* insignificant — measured exhaustively for
                           \\p{L}-vs-variants; does not enter the count */"
SAB_AFTER=""
