/* entry_shape_driver.c -- [CC-DIFF] STEP 2 (2026-09-04, lane ccd2).
 *
 * The find-all driver `run_entry_shape_identity.sh` compiles once per
 * (witness, rung). It prints EVERY span and EVERY capture group of EVERY
 * match, so the gate's comparison is over the ANSWERS and not over a hit
 * count: a rung that finds the same NUMBER of matches in different places, or
 * the same spans with different group boundaries, must part.
 *
 * It also prints the two stamps the rung ladder introduced. That is what makes
 * the gate's non-vacuity arm POSITIVE rather than assumed: the script asserts
 * that the artifact it just timed really was emitted at the rung it asked for,
 * instead of trusting that `--vm-entry-shape=N` reached the emitter. A flag
 * that silently stopped being parsed would otherwise turn the whole sweep
 * green -- five identical builds agree with each other perfectly.
 *
 * The find-all loop is docs/spec/match_api.md S3.1's, `rx_next_pos` and all:
 * a zero-length match advances by one CHARACTER, not one byte, so the driver
 * is correct under a non-byte encoding without a second spelling.
 *
 * Subjects arrive on argv, and TWO tokens stand for bytes the caller's
 * space-separated subject list cannot carry. `@EMPTY` is the whole empty
 * string -- a real population member, since `[a-z]{0,8}` matches it. `@SP`
 * anywhere inside a subject becomes one space, which is what lets a
 * whitespace-bearing witness exist at all: `(\w+)\s+\1` needs a subject with
 * a space in it, and the gate's own first run reported that witness VACUOUS
 * because every "subject" in its list was a single word.
 */
#include <stdio.h>
#include <string.h>
#include <stddef.h>
#include "art.h"

int main(int argc, char **argv)
{
    /* THE STAMPS ARE NOT IN THE HEADER. The emitter writes
     * `<PREFIX>_VM_ENTRY_SHAPE` and `<PREFIX>_VM_PROGRAM_BYTES` into the
     * generated .c (src/gen/emit_vm.c), not the paired .h, so a driver that
     * `#include`s only "art.h" cannot see them and an `#ifdef` on them here
     * would silently take its else-branch forever. The SCRIPT greps the .c
     * instead, which is why this file prints no stamp line: a check must not
     * read a fact from a place that can quietly stop carrying it.
     * (docs/dev/learnings.md S3.) */
    printf("ngroups\t%d\n", rx_info.ngroups);

    for (int a = 1; a < argc; a++) {
        const char *raw = argv[a];
        const unsigned char *s;
        size_t n;
        char sbuf[1024];
        if (strcmp(raw, "@EMPTY") == 0) { s = (const unsigned char *)""; n = 0; }
        else {
            /* expand @SP -> ' ' */
            size_t o = 0;
            for (const char *p = raw; *p && o + 1 < sizeof sbuf; ) {
                if (p[0] == '@' && p[1] == 'S' && p[2] == 'P') { sbuf[o++] = ' '; p += 3; }
                else sbuf[o++] = *p++;
            }
            sbuf[o] = '\0';
            s = (const unsigned char *)sbuf; n = o;
        }

        ptrdiff_t caps[64][2];
        size_t pos = 0;
        long m = 0;
        for (;;) {
            for (int g = 0; g <= rx_info.ngroups && g < 64; g++) {
                caps[g][0] = -1; caps[g][1] = -1;
            }
            if (!rx_search(s, n, pos, caps)) break;
            printf("s%d\tm%ld", a, m);
            for (int g = 0; g <= rx_info.ngroups && g < 64; g++)
                printf("\t%ld,%ld", (long)caps[g][0], (long)caps[g][1]);
            printf("\n");
            m++;
            pos = (caps[0][1] > caps[0][0])
                ? (size_t)caps[0][1]
                : rx_next_pos(s, n, (size_t)caps[0][0]);
            if (pos > n) break;
            if (m > 4096) { printf("s%d\tRUNAWAY\n", a); break; }
        }
        printf("s%d\ttotal\t%ld\n", a, m);
    }
    return 0;
}
