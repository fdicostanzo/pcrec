/* M6 frozen target adv-vmstride-u8w3: the VM cursor rung's strided span loop for witness `(?:aé)+x`, -e utf8 --engine=vm (pcrec 00b1f3da build/pcrec, -p rx -o rx.c). */
/* hooks: more `rx_span_cursor + 3 <= subject_length`, step `rx_span_cursor += 3`, members `subject[rx_span_cursor + i] == <byte>` (opaque), no counter */
/* indent 8 spaces; below: generic row, SKIP / ADVANCE strided (MF_SITE_ABI 8), W = 3 (utf8), byte for byte. */
        while ((rx_span_cursor + 3 <= subject_length) && (subject[rx_span_cursor + 0] == 97) && (subject[rx_span_cursor + 1] == 195) && (subject[rx_span_cursor + 2] == 169)) {
            rx_span_cursor += 3;
        }
/* pcrec today: the body above, byte for byte: it was cut from that artifact (vm_stride_loop), so the kit's render must equal pcrec's pre-migration text. */
