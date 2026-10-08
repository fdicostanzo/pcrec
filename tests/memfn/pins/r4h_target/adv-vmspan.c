/* R4h frozen target adv-vmspan: witness `a[a-z]*x`, --engine=vm (pcrec 9bf09133 build/pcrec, -o rx.c). */
/* hooks: more `rx_span_cursor + 1 <= lim_`, peek `subject[rx_span_cursor + 0]`, step `rx_span_cursor += 1`, member `(unsigned)(subject[rx_span_cursor + 0] - 97) <= 25u` (opaque). */
/* count `none (unbounded)`, cursor `rx_span_cursor`, indent 8 spaces; below: generic row, ADVANCE, byte for byte. */
        while ((rx_span_cursor + 1 <= lim_) && ((unsigned)(subject[rx_span_cursor + 0] - 97) <= 25u)) {
            rx_span_cursor += 1;
        }
/* pcrec today:
        while (rx_span_cursor + 1 <= lim_ && ((unsigned)(subject[rx_span_cursor + 0] - 97) <= 25u)) { rx_span_cursor += 1; }
*/
