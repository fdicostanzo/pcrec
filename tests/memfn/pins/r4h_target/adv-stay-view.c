/* R4h frozen target adv-stay-view: witness `a[^x]*x$`, default flags (pcrec 9bf09133 build/pcrec, -o rx.c). */
/* hooks: more `scan_position + 1 < subject_length`, peek `subject[scan_position]`, step `scan_position++`, member `rx_forward_stay1[subject[scan_position]]` (opaque). */
/* count `none (unbounded)`, cursor `scan_position`, indent 12 spaces; below: generic row, ADVANCE, byte for byte. */
            while ((scan_position + 1 < subject_length) && (rx_forward_stay1[subject[scan_position]])) {
                scan_position++;
            }
/* pcrec today:
            while (scan_position + 1 < subject_length && rx_forward_stay1[subject[scan_position]]) scan_position++;
*/
