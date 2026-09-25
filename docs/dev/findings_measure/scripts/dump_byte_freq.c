/* Dumps the shipped static byte-frequency prior (src/opt/prefix_k.c's
 * pcrec_byte_freq_ppm) to stdout as `byte\tppm` rows, 0..255, with the
 * table's total on stderr (must be 1000000, see prefix_k.c's own check).
 * This is candidate estimator (0)'s whole table -- reproduced here rather
 * than hand-transcribed so it can never drift from the real one.
 *
 * Build: gcc -O2 -Ilib -Isrc -o dump_byte_freq dump_byte_freq.c ../../../build/libpcrec.a
 * (path is relative to this file inside the worktree that built libpcrec.a)
 */
#include <stdio.h>
unsigned pcrec_byte_freq_ppm(int b);
unsigned pcrec_byte_freq_total_ppm(void);
int main(void) {
    for (int b = 0; b < 256; b++)
        printf("%d\t%u\n", b, pcrec_byte_freq_ppm(b));
    fprintf(stderr, "total=%u\n", pcrec_byte_freq_total_ppm());
    return 0;
}
