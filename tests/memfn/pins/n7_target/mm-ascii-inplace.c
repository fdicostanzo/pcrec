/* M7 frozen target mm-ascii-inplace: rx_span_match_caseless's compare loop for witness `(?i)(ab)\1`, `--features all` (byte) (pcrec 1adead14 build/pcrec, -p rx -o rx.c). */
/* hooks: s `s`, n `n`, lo `at`, ref `ref`, reflen `reflen`, result `i` (decl `size_t `), on_miss `return -(ptrdiff_t)i - 1;`, fold_kind ASCII, fold `if (@ >= 'A' && @ <= 'Z') @ = (unsigned char)(@ + 32);` (FOLD_STMT). */
/* indent 4 spaces; below: row mismatch_inplace, MISMATCH / ON_DIFF, the in-place shape, byte for byte. */
    size_t i;
    for (i = 0; i < reflen; i++) {
        unsigned char x, y;
        if (at + i >= n) return -(ptrdiff_t)i - 1;
        x = s[at + i];
        y = ref[i];
        if (x >= 'A' && x <= 'Z') x = (unsigned char)(x + 32);
        if (y >= 'A' && y <= 'Z') y = (unsigned char)(y + 32);
        if (x != y) return -(ptrdiff_t)i - 1;
    }
/* pcrec today: the body above, byte for byte: it was cut from that artifact, so the kit's render must equal pcrec's pre-migration text. */
