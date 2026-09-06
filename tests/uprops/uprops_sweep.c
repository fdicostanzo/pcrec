/* uprops_sweep.c — THE PCREC SIDE of the `\p{...}` membership differential
 * ([M5.0] stage 3).
 *
 * Compiled ONCE PER PROPERTY, against that property's own emitted artifact
 * (`#include`d as `UPROPS_ARTIFACT`), and it prints the property's MEMBER SET
 * as a code-point interval list on stdout — the same shape and the same
 * ordering `uprops_oracle.c` prints for libpcre2, so the comparator is a
 * line-by-line set comparison and neither side has to know how the other
 * decided.
 *
 * IT SWEEPS BY FIND-ALL OVER ONE SUBJECT THAT IS EVERY CODE POINT IN ORDER,
 * not by one call per code point, and that is what makes a whole-space
 * differential affordable rather than a sample: 1,112,064 code points cost one
 * pass, so there is no sampling rule for a bug to hide behind. The subject is
 * built here rather than read from a file so that the two sides cannot be
 * handed different bytes.
 *
 * THE SURROGATES ARE ABSENT FROM THE SUBJECT, on both sides, and that is a
 * fact about the ENCODING rather than a convenience: U+D800..U+DFFF have no
 * UTF-8 encoding at all (src/opt/lower_enc.c's own surrogate gap), so no
 * subject can contain one and no sweep can ask about one. `\p{Cs}` is
 * therefore measured EMPTY by both sides, which is the honest answer and not
 * a hole in the check.
 *
 * UNDER `--encoding=byte` the sweep is the 256 single BYTES instead, which is
 * the same statement one universe down: that encoding's code points ARE its
 * bytes (D58), so the interval list it prints is directly comparable with the
 * oracle's own 8-bit non-UTF sweep. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include UPROPS_ARTIFACT

#ifndef UPROPS_MAXCP
#define UPROPS_MAXCP 0x10FFFFu
#endif

static unsigned char *subj;
static size_t subjlen;
static unsigned *cp_at;

static int u8enc(unsigned c, unsigned char *o)
{
    if (c < 0x80)    { o[0] = (unsigned char)c; return 1; }
    if (c < 0x800)   { o[0] = (unsigned char)(0xC0 | (c >> 6));
                       o[1] = (unsigned char)(0x80 | (c & 0x3F)); return 2; }
    if (c < 0x10000) { o[0] = (unsigned char)(0xE0 | (c >> 12));
                       o[1] = (unsigned char)(0x80 | ((c >> 6) & 0x3F));
                       o[2] = (unsigned char)(0x80 | (c & 0x3F)); return 3; }
    o[0] = (unsigned char)(0xF0 | (c >> 18));
    o[1] = (unsigned char)(0x80 | ((c >> 12) & 0x3F));
    o[2] = (unsigned char)(0x80 | ((c >> 6) & 0x3F));
    o[3] = (unsigned char)(0x80 | (c & 0x3F));
    return 4;
}

int main(void)
{
    size_t cap = (size_t)UPROPS_MAXCP * 4u + 8u;
    subj  = malloc(cap);
    cp_at = malloc(cap * sizeof *cp_at);
    if (!subj || !cp_at) { fprintf(stderr, "oom\n"); return 2; }

    subjlen = 0;
    for (unsigned c = 0; c <= (unsigned)UPROPS_MAXCP; c++) {
        if (c >= 0xD800u && c <= 0xDFFFu) continue;
        cp_at[subjlen] = c;
        subjlen += (UPROPS_MAXCP > 0xFFu) ? (size_t)u8enc(c, subj + subjlen)
                                          : (subj[subjlen] = (unsigned char)c, 1u);
    }

    /* THE ARTIFACT IS ASKED FOR EVERY MATCH, LEFT TO RIGHT. `\p{X}` is a
     * single character, so a match at offset `o` means "the code point stored
     * at `o` is a member" and nothing else — the ovector's own end tells us
     * where to resume, so a multi-byte member advances by its own width with
     * no decode here. */
    ptrdiff_t caps[1][2];
    size_t pos = 0;
    unsigned lo = 0, hi = 0;
    int have = 0;
    unsigned long nint = 0, nmemb = 0;

    while (pos < subjlen) {
        int rc = rx_search(subj, subjlen, pos, caps);
        if (rc <= 0) break;
        size_t s = (size_t)caps[0][0], e = (size_t)caps[0][1];
        unsigned cp = cp_at[s];
        nmemb++;
        if (have && cp == hi + 1) hi = cp;
        else { if (have) { printf(" %X-%X", lo, hi); nint++; } lo = hi = cp; have = 1; }
        pos = (e > s) ? e : s + 1;
    }
    if (have) { printf(" %X-%X", lo, hi); nint++; }
    printf("\n");
    fprintf(stderr, "pcrec intervals=%lu members=%lu\n", nint, nmemb);
    return 0;
}
