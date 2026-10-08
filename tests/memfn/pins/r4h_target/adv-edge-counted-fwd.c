/* R4h frozen target adv-edge-counted-fwd: witness `a[0-9]{3,20}x`, default flags (pcrec 9bf09133 build/pcrec, -o rx.c). */
/* hooks: more `scan_position < subject_length`, peek `subject[scan_position]`, step `scan_position++`, member `(unsigned)(subject[scan_position] - 48) <= 9u` (opaque). */
/* count `scan_run_length (caller's, start 1, span_hi 3)`, cursor `scan_position`, indent 12 spaces; below: generic row, ADVANCE, byte for byte. */
            while ((scan_position < subject_length) && scan_run_length < 3ULL && ((unsigned)(subject[scan_position] - 48) <= 9u)) {
                scan_position++;
                scan_run_length++;
            }
/* pcrec today:
            while (scan_position < subject_length && scan_run_length < 3UL
                   && (unsigned)(subject[scan_position] - 48) <= 9u) { scan_position++; scan_run_length++; }
*/
