/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2's find-any family,
 *   lane simdset).
 *
 * memfn/tests/g2/g2_any_driver.c — the DRIVER of G2's find-any family
 * (run_g2_any.py). Compiled with `-include g2a_kernels.c`'s path as
 * G2A_KERNELS, at each build's flags. Every kernel of the table is called
 * over a generated subject space and each answer is held to THIS FILE'S
 * scalar byte loop (`ref_find`, over the table's bytes as given, duplicates
 * kept), never to another kit output:
 *   - lengths n 0..G2A_MAXN (2 x 32 + 9), start positions pos from a fixed
 *     list (block edges at 16 and 32) plus n - 1 and n;
 *   - a member planted at EVERY position p in [pos, n), each member in
 *     turn, and the no-hit subject; members planted before pos (layout U and
 *     A) and after p (a later hit never wins); the filler is non-members,
 *     half of them one bit away from a member;
 *   - layout U: subject + n is the first byte of a PROT_NONE page;
 *     layout L: subject + pos is the first byte after a PROT_NONE page (a
 *     read below pos faults); layout A: every alignment 0..31 of subject
 *     from a 64-byte-aligned base, for the hit at pos, at n - 1, at a
 *     random p and none.
 * A fault ends the process by its signal (the runner reads it); a kernel
 * that does not return is stopped by a 10 s alarm. Prints `checks N` and
 * `failures N`, the first 20 failures as FAIL lines; exit 1 on a failure.
 *
 *   g2a_driver [STRIDE [stop]]
 * STRIDE (default 1) runs the kernels whose id is a multiple of it (the
 * runner's plant runs that must stay green); `stop` exits 1 at the first
 * failure (a plant that must go red).
 */
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

struct g2a_kernel {
    size_t (*f)(const unsigned char *subject, size_t n, size_t pos);
    unsigned k;
    unsigned char b[3];
    unsigned levels;
};

#include G2A_KERNELS

#define G2A_MAXN 73

static unsigned long long rng = 20261029;
static unsigned rnd(unsigned n)
{
    rng = rng * 6364136223846793005ULL + 1442695040888963407ULL;
    return (unsigned)(rng >> 33) % n;
}

/* The reference: the first i in [pos, n) whose byte is one of b[0..k). */
static size_t ref_find(const unsigned char *s, size_t n, size_t pos, const unsigned char *b,
                       unsigned k)
{
    for (size_t i = pos; i < n; i++)
        for (unsigned j = 0; j < k; j++)
            if (s[i] == b[j]) return i;
    return n;
}

static unsigned long long checks, failures;
static int stop_first;

static void check(const struct g2a_kernel *kn, unsigned id, const char *lay,
                  const unsigned char *s, size_t n, size_t pos, unsigned align)
{
    size_t want = ref_find(s, n, pos, kn->b, kn->k);
    size_t got = kn->f(s, n, pos);
    checks++;
    if (got != want && ++failures <= 20)
        printf("FAIL kernel %u (levels %u, bytes %u,%u,%u k %u) layout %s align %u n %zu pos %zu: "
               "got %zu want %zu\n", id, kn->levels, kn->b[0], kn->b[1], kn->b[2], kn->k, lay,
               align, n, pos, got, want);
    if (failures && stop_first) {
        printf("checks %llu\nfailures %llu\n", checks, failures);
        exit(1);
    }
}

static int member(const struct g2a_kernel *kn, unsigned char c)
{
    for (unsigned j = 0; j < kn->k; j++)
        if (kn->b[j] == c) return 1;
    return 0;
}

/* A non-member: half the time one bit away from a member. */
static unsigned char filler(const struct g2a_kernel *kn)
{
    for (;;) {
        unsigned char c = rnd(2) ? (unsigned char)(kn->b[rnd(kn->k)] ^ (1u << rnd(8)))
                                 : (unsigned char)rnd(256);
        if (!member(kn, c)) return c;
    }
}

/* Writes into s[0..n) the subject: filler, a member at p (p == n: none),
 * a member at a random later position, and members before pos where
 * `below` (s[0..pos) is then readable). */
static void subject(const struct g2a_kernel *kn, unsigned char *s, size_t n, size_t pos,
                    size_t p, int below)
{
    for (size_t i = below ? 0 : pos; i < n; i++) s[i] = filler(kn);
    if (p < n) {
        s[p] = kn->b[(p + n) % kn->k];
        if (p + 1 < n && rnd(2)) s[p + 1 + rnd((unsigned)(n - p - 1))] = kn->b[rnd(kn->k)];
    }
    if (below && pos) {
        s[pos - 1] = kn->b[rnd(kn->k)];
        s[rnd((unsigned)pos)] = kn->b[rnd(kn->k)];
    }
}

static const size_t pos_list[] = {0, 1, 2, 3, 15, 16, 17, 31, 32, 33};

int main(int argc, char **argv)
{
    unsigned stride = argc > 1 ? (unsigned)atoi(argv[1]) : 1;
    stop_first = argc > 2 && !strcmp(argv[2], "stop");
    if (!stride) stride = 1;
    long pg = sysconf(_SC_PAGESIZE);
    /* U: [data page][guard]; L: [guard][data page] */
    unsigned char *u = mmap(NULL, 2 * (size_t)pg, PROT_READ | PROT_WRITE,
                            MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    unsigned char *l = mmap(NULL, 2 * (size_t)pg, PROT_READ | PROT_WRITE,
                            MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (u == MAP_FAILED || l == MAP_FAILED || mprotect(u + pg, (size_t)pg, PROT_NONE) ||
        mprotect(l, (size_t)pg, PROT_NONE)) {
        perror("g2_any_driver: guard pages");
        return 2;
    }
    static unsigned char abuf[64 + 32 + G2A_MAXN] __attribute__((aligned(64)));
    alarm(10);
    for (unsigned id = 0; id < G2A_NKERNEL; id += stride) {
        const struct g2a_kernel *kn = &g2a_table[id];
        alarm(10);
        for (size_t n = 0; n <= G2A_MAXN; n++) {
            size_t plist[sizeof pos_list / sizeof pos_list[0] + 2];
            size_t np = 0;
            for (size_t j = 0; j < sizeof pos_list / sizeof pos_list[0]; j++)
                if (pos_list[j] <= n) plist[np++] = pos_list[j];
            for (size_t e = n ? n - 1 : 0; e <= n; e++) {
                size_t j = 0;
                while (j < np && plist[j] != e) j++;
                if (j == np) plist[np++] = e;
            }
            for (size_t q = 0; q < np; q++) {
                size_t pos = plist[q];
                for (size_t p = pos; p <= n; p++) {
                    unsigned char *s = u + pg - n;          /* U */
                    subject(kn, s, n, pos, p, 1);
                    check(kn, id, "U", s, n, pos, 0);
                    s = l + pg - pos;                        /* L */
                    subject(kn, s, n, pos, p, 0);
                    check(kn, id, "L", s, n, pos, 0);
                }
                size_t pa[4] = {pos, n ? n - 1 : 0, pos + (n > pos ? rnd((unsigned)(n - pos)) : 0), n};
                for (unsigned h = 0; h < 4; h++) {
                    if (pa[h] < pos) continue;
                    for (unsigned a = 0; a < 32; a++) {      /* A */
                        unsigned char *s = abuf + a;
                        subject(kn, s, n, pos, pa[h], 1);
                        check(kn, id, "A", s, n, pos, a);
                    }
                }
            }
        }
    }
    printf("checks %llu\nfailures %llu\n", checks, failures);
    return failures ? 1 : 0;
}
