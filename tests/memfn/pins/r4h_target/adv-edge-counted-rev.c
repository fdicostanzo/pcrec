/* R4h frozen target adv-edge-counted-rev: witness `a[0-9]{3,20}x`, default flags (pcrec 9bf09133 build/pcrec, -o rx.c). */
/* hooks: more `rewind_position > search_from`, peek `subject[rewind_position - 1]`, step `rewind_position--`, member `(unsigned)(subject[rewind_position - 1] - 48) <= 9u` (opaque). */
/* count `scan_run_length (caller's, start 1, span_hi 3)`, cursor `rewind_position`, indent 16 spaces; below: generic row, ADVANCE, byte for byte. */
                while ((rewind_position > search_from) && scan_run_length < 3ULL && ((unsigned)(subject[rewind_position - 1] - 48) <= 9u)) {
                    rewind_position--;
                    scan_run_length++;
                }
/* pcrec today:
                while (rewind_position > search_from && scan_run_length < 3UL
                       && (unsigned)(subject[rewind_position - 1] - 48) <= 9u) { rewind_position--; scan_run_length++; }
*/
