/* M7 frozen target mm-ucp-expr: rx_span_match_caseless's compare loop for witness `(?i)(ab)\1`, `--features all --ucp` (byte) (pcrec 1adead14 build/pcrec, -p rx -o rx.c). */
/* hooks: s `s`, n `n`, lo `at`, ref `ref`, reflen `reflen`, result `i` (decl `size_t `), on_miss `return -(ptrdiff_t)i - 1;`, fold_kind UCP, fold `rx_span_ci_fold(@)` (FOLD_EXPR). */
/* indent 4 spaces; below: generic row, MISMATCH / ON_DIFF, the expression-fold shape, byte for byte. */
    size_t i;
    for (i = 0; i < reflen; i++) {
        if (at + i >= n || rx_span_ci_fold(s[at + i]) != rx_span_ci_fold(ref[i]))
            return -(ptrdiff_t)i - 1;
    }
/* pcrec today: the body above, byte for byte: it was cut from that artifact, so the kit's render must equal pcrec's pre-migration text. */
