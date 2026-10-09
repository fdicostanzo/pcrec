/* M7 frozen target mm-exact: rx_span_match's compare loop for witness `(a+)\1`, `--features all` (byte) (pcrec 1adead14 build/pcrec, -p rx -o rx.c). */
/* hooks: s `s`, n `n`, lo `at`, ref `ref`, reflen `reflen`, result `i` (decl `size_t `), on_miss `return -(ptrdiff_t)i - 1;`, fold_kind NONE, no fold. */
/* indent 4 spaces; below: generic row, MISMATCH / ON_DIFF, the exact shape, byte for byte. */
    size_t i;
    for (i = 0; i < reflen; i++) {
        if (at + i >= n || s[at + i] != ref[i])
            return -(ptrdiff_t)i - 1;
    }
/* pcrec today: the body above, byte for byte: it was cut from that artifact, so the kit's render must equal pcrec's pre-migration text. */
