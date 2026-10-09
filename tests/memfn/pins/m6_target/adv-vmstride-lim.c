/* M6 frozen target adv-vmstride-lim: the VM cursor rung's strided span loop for witness `x(?:ab)*abc`, --engine=vm (byte) (pcrec 00b1f3da build/pcrec, -p rx -o rx.c). */
/* hooks: more `rx_span_cursor + 2 <= lim_` (the MRL-folded bound), step `rx_span_cursor += 2`, members `subject[rx_span_cursor + i] == <byte>` (opaque), no counter */
/* indent 8 spaces; below: generic row, SKIP / ADVANCE strided (MF_SITE_ABI 8), the greedy arm, W = 2, MRL-folded, byte for byte. */
        while ((rx_span_cursor + 2 <= lim_) && (subject[rx_span_cursor + 0] == 97) && (subject[rx_span_cursor + 1] == 98)) {
            rx_span_cursor += 2;
        }
/* pcrec today: the body above, byte for byte: it was cut from that artifact (vm_stride_loop), so the kit's render must equal pcrec's pre-migration text. */
