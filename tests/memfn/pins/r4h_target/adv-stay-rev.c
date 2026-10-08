/* R4h frozen target adv-stay-rev: witness `a[^x]*`, default flags (pcrec 9bf09133 build/pcrec, -o rx.c). */
/* hooks: more `rewind_position > search_from`, peek `subject[rewind_position - 1]`, step `rewind_position--`, member `rx_reverse_stay0[subject[rewind_position - 1]]` (opaque). */
/* count `none (unbounded)`, cursor `rewind_position`, indent 16 spaces; below: generic row, ADVANCE, byte for byte. */
                while ((rewind_position > search_from) && (rx_reverse_stay0[subject[rewind_position - 1]])) {
                    rewind_position--;
                }
/* pcrec today:
                while (rewind_position > search_from && rx_reverse_stay0[subject[rewind_position - 1]]) rewind_position--;
*/
