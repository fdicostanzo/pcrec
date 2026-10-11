/* lossreview/misc: ANSWER-IDENTITY driver for hand twins.
 *
 *   gcc -O1 -I DIRA -I DIRB -DAP=ra -DBP=rb ident.c A.c B.c -o ident
 *   ./ident SUBJECT_FILE...
 *
 * A and B are two artifacts of the same pattern compiled with different -p
 * prefixes (AP / BP; the generated headers ra.h / rb.h are -include'd by the
 * Makefile-free build line in the lane notes).  For every subject, and for the
 * subject with each EDIT applied (append \n, append \n\n, drop the last byte,
 * prepend a byte, empty), every start position (capped at MAXPOS evenly spread
 * positions on large subjects, always including 0, n-2..n) calls A_search and
 * B_search; any difference in return value or in the match span is printed and
 * counted.  Exit status = 1 if any difference.  Nothing is timed. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#define CAT2(a, b) a##b
#define CAT(a, b) CAT2(a, b)
#define SA CAT(AP, _search)
#define SB CAT(BP, _search)
int SA(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
int SB(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
#define MAXPOS 400
static long ncell, ndiff, nmatch;
static void cmp(const unsigned char *s, size_t n, const char *name, int edit)
{
    size_t step = n / MAXPOS + 1;
    for (size_t p = 0; p <= n; p += (p + 3 >= n ? 1 : step)) {
        ptrdiff_t ca[64][2], cb[64][2];
        memset(ca, 0xAA, sizeof ca); memset(cb, 0xAA, sizeof cb);
        int ra = SA(s, n, p, ca), rb = SB(s, n, p, cb);
        ncell++; nmatch += ra == 1;
        if (ra != rb || (ra == 1 && (ca[0][0] != cb[0][0] || ca[0][1] != cb[0][1]))) {
            if (ndiff++ < 20) printf("DIFF %s edit=%d n=%zu start=%zu A=%d[%td,%td] B=%d[%td,%td]\n", name, edit, n, p, ra, ca[0][0], ca[0][1], rb, cb[0][0], cb[0][1]);
        }
    }
}
int main(int argc, char **argv)
{
    for (int i = 1; i < argc; i++) {
        FILE *f = fopen(argv[i], "rb"); if (!f) { perror(argv[i]); return 2; }
        fseek(f, 0, SEEK_END); size_t n = (size_t)ftell(f); fseek(f, 0, SEEK_SET);
        unsigned char *b = malloc(n + 4); if (fread(b, 1, n, f) != n) return 2; fclose(f);
        unsigned char *e = malloc(n + 4);
        cmp(b, n, argv[i], 0);
        memcpy(e, b, n); e[n] = '\n'; cmp(e, n + 1, argv[i], 1);
        memcpy(e, b, n); e[n] = '\n'; e[n + 1] = '\n'; cmp(e, n + 2, argv[i], 2);
        if (n) { cmp(b, n - 1, argv[i], 3); }
        e[0] = 'x'; memcpy(e + 1, b, n); cmp(e, n + 1, argv[i], 4);
        cmp(b, 0, argv[i], 5);
        free(b); free(e);
    }
    printf("cells %ld matches %ld differences %ld\n", ncell, nmatch, ndiff);
    return ndiff != 0;
}
