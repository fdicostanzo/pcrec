/* R4h frozen target adv-vmspan-it: witness `(a)[a-z]{2,9}x`, --engine=vm (pcrec 9bf09133 build/pcrec, -o rx.c). */
/* hooks: more `rx_span_cursor + 1 <= lim_`, peek `subject[rx_span_cursor + 0]`, step `rx_span_cursor += 1`, member `(unsigned)(subject[rx_span_cursor + 0] - 97) <= 25u` (opaque). */
/* count `it_ (caller's, start 0, span_hi 9)`, cursor `rx_span_cursor`, indent 8 spaces; below: generic row, ADVANCE, byte for byte. */
        while ((rx_span_cursor + 1 <= lim_) && it_ < 9ULL && ((unsigned)(subject[rx_span_cursor + 0] - 97) <= 25u)) {
            rx_span_cursor += 1;
            it_++;
        }
/* pcrec today:
        while (rx_span_cursor + 1 <= lim_ && it_ < 9UL && ((unsigned)(subject[rx_span_cursor + 0] - 97) <= 25u)) { rx_span_cursor += 1; it_++; }
*/
