/* R4h frozen target adv-edge-unbounded: witness `[a-z]*`, default flags (pcrec 9bf09133 build/pcrec, -o rx.c). */
/* hooks: more `scan_position < subject_length`, peek `subject[scan_position]`, step `scan_position++`, member `(unsigned)(subject[scan_position] - 97) <= 25u` (opaque). */
/* count `none (unbounded)`, cursor `scan_position`, indent 12 spaces; below: generic row, ADVANCE, byte for byte. */
            while ((scan_position < subject_length) && ((unsigned)(subject[scan_position] - 97) <= 25u)) {
                scan_position++;
            }
/* pcrec today:
            while (scan_position < subject_length && (unsigned)(subject[scan_position] - 97) <= 25u) scan_position++;
*/
