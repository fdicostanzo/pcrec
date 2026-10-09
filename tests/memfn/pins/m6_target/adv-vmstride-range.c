/* M6 frozen target adv-vmstride-range: the VM cursor rung's strided span loop for witness `(?:[a-z][0-9])+@`, --engine=vm (byte) (pcrec 00b1f3da build/pcrec, -p rx -o rx.c). */
/* hooks: more `rx_span_cursor + 2 <= subject_length`, step `rx_span_cursor += 2`, members `(unsigned)(subject[rx_span_cursor + i] - <lo>) <= <hi - lo>u` (opaque, range class tests), no counter */
/* indent 8 spaces; below: generic row, SKIP / ADVANCE strided (MF_SITE_ABI 8), W = 2 with range members, byte for byte. */
        while ((rx_span_cursor + 2 <= subject_length) && ((unsigned)(subject[rx_span_cursor + 0] - 97) <= 25u) && ((unsigned)(subject[rx_span_cursor + 1] - 48) <= 9u)) {
            rx_span_cursor += 2;
        }
/* pcrec today: the body above, byte for byte: it was cut from that artifact (vm_stride_loop), so the kit's render must equal pcrec's pre-migration text. */
