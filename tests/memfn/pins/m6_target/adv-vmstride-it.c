/* M6 frozen target adv-vmstride-it: the VM cursor rung's strided span loop for witness `(?:ab){2,5}c`, --engine=vm (byte) (pcrec 00b1f3da build/pcrec, -p rx -o rx.c). */
/* hooks: more `rx_span_cursor + 2 <= subject_length`, step `rx_span_cursor += 2`, members `subject[rx_span_cursor + i] == <byte>` (opaque, one per term), count `it_` (caller's, start 0, span_hi 5 iterations) */
/* indent 8 spaces; below: generic row, SKIP / ADVANCE strided (MF_SITE_ABI 8), the possessive arm, W = 2, the caller's cap, byte for byte. */
        while ((rx_span_cursor + 2 <= subject_length) && it_ < 5ULL && (subject[rx_span_cursor + 0] == 97) && (subject[rx_span_cursor + 1] == 98)) {
            rx_span_cursor += 2;
            it_++;
        }
/* pcrec today: the body above, byte for byte: it was cut from that artifact (vm_stride_loop), so the kit's render must equal pcrec's pre-migration text. */
