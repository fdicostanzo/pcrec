/* dec.c: decode cost of the delta-varint pool vs zlib inflate (scratch measurement) */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <zlib.h>
static unsigned char *slurp(const char *p, size_t *n) {
    FILE *f = fopen(p, "rb"); fseek(f, 0, SEEK_END); *n = ftell(f); rewind(f);
    unsigned char *b = malloc(*n); if (fread(b, 1, *n, f) != *n) exit(1); fclose(f); return b; }
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + t.tv_nsec * 1e-9; }
static size_t decode(const unsigned char *s, size_t n, unsigned *out) {
    size_t i = 0, k = 0; unsigned prev = 0;
    while (i < n) {
        unsigned v[2];
        for (int j = 0; j < 2; j++) { unsigned x = 0, sh = 0; unsigned char c;
            do { c = s[i++]; x |= (unsigned)(c & 127) << sh; sh += 7; } while (c & 128); v[j] = x; }
        unsigned lo = prev + v[0], hi = lo + v[1];   /* list boundaries ignored: cost only */
        out[k++] = lo; out[k++] = hi; prev = hi; }
    return k / 2; }
int main(int argc, char **argv) {
    size_t vn, zn; unsigned char *v = slurp(argv[1], &vn), *z = slurp(argv[2], &zn);
    unsigned *out = malloc(vn * 2 * sizeof *out); unsigned char *inf = malloc(vn + 64);
    int R = 2000; double t0 = now(); size_t k = 0;
    for (int r = 0; r < R; r++) k += decode(v, vn, out);
    double t1 = now();
    for (int r = 0; r < R; r++) { uLongf dl = vn + 64; if (uncompress(inf, &dl, z, zn) != Z_OK) return 2; }
    double t2 = now();
    printf("varint bytes %zu intervals/pass %zu  decode whole pool: %.1f us/pass\n", vn, k / R, (t1 - t0) / R * 1e6);
    printf("zlib bytes %zu  inflate whole pool: %.1f us/pass (then the varint decode on top)\n", zn, (t2 - t1) / R * 1e6);
    return out[0] == 12345; }
