/* flat/stretch.c -- count-only inputs for an adaptive per-stretch probe (lane flat; no clock).
 *   stretch MEMBERS_HEX SUBJECT  ->  bytes stretches members e8 e64 trans64 trans64_ne
 * Over the subject's whole 64-byte stretches (the tail ignored) with m = the stretch's member bit mask (bit k = byte
 * k is a member, the walk's skip-table set): e8 = share of 8-byte blocks with no member, e64 = share of stretches
 * with no member, trans64 = mean popcount(m ^ (m >> 1)) over all stretches (member/non-member boundaries inside the
 * stretch, the top bit's boundary with the next stretch not counted), trans64_ne = the same mean over non-empty
 * stretches only. A directory subject is every b* file in it. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
static unsigned char mem[256];
static unsigned long long nst, nempty, nb8, nempty8, tr, trne, nmem, nbytes;
static void scan(const char *path)
{
    FILE *f = fopen(path, "rb"); if (!f) { perror(path); exit(2); }
    static unsigned char b[64];
    while (fread(b, 1, 64, f) == 64) {
        unsigned long long m = 0;
        for (int k = 0; k < 64; k++) m |= (unsigned long long)mem[b[k]] << k;
        for (int j = 0; j < 8; j++) { nb8++; nempty8 += !((m >> (8 * j)) & 0xff); }
        unsigned t = (unsigned)__builtin_popcountll((m ^ (m >> 1)) & 0x7fffffffffffffffULL);
        nst++; nempty += !m; tr += t; if (m) trne += t;
        nmem += (unsigned)__builtin_popcountll(m); nbytes += 64;
    }
    fclose(f);
}
int main(int c, char **v)
{
    if (c != 3) return 2;
    for (int i = 0; i < 64; i++) { unsigned d; sscanf(v[1] + i, "%1x", &d); for (int k = 0; k < 4; k++) mem[i * 4 + k] = d >> k & 1; }
    DIR *d = opendir(v[2]);
    if (d) { struct dirent *e; char p[4096];
        while ((e = readdir(d))) if (e->d_name[0] == 'b') { snprintf(p, sizeof p, "%s/%s", v[2], e->d_name); scan(p); }
        closedir(d);
    } else scan(v[2]);
    printf("%llu %llu %llu %.4f %.4f %.3f %.3f\n", nbytes, nst, nmem, nempty8 / (double)nb8, nempty / (double)nst,
           tr / (double)nst, nempty < nst ? trne / (double)(nst - nempty) : 0.0);
    return 0;
}
