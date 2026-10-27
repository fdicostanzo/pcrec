/* subtri driver: substitution vs plain find-all over one subject, with
 * user-space instruction/cycle counts read around the region only.
 * Build: gcc -O2 -DART=<dir> drv.c  (includes support.c, rx.c, sub.c)
 * Run:   drv MODE FILE REPS    MODE = subst | find | none
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/perf_event.h>
#include <sys/ioctl.h>
#include <time.h>

#define STR2(x) #x
#define STR(x) STR2(x)
#define PCREC_SUPPORT_STATIC
#include STR(ART/../support.c)
#include STR(ART/rx.c)
#include STR(ART/sub.c)
#include "attr_print.h"

static int pfd(uint64_t cfg) {
    struct perf_event_attr a; memset(&a, 0, sizeof a);
    a.type = PERF_TYPE_HARDWARE; a.size = sizeof a; a.config = cfg;
    a.disabled = 1; a.exclude_kernel = 1; a.exclude_hv = 1;
    return (int)syscall(SYS_perf_event_open, &a, 0, -1, -1, 0);
}

static unsigned char scratch[65536];

static int sub_all(const unsigned char *s, size_t n, unsigned char *out, size_t cap, size_t *len) {
    const struct pcrec_subst_info *t = &sub_subst_info;
    rx_iter it = RX_ITER_INIT(s, n);
    rx_var vres[SUB_NVREFS];
    pcrec_subst_piece pc[64 * SUB_PIECES];
    pcrec_subst_out o = { .pc = pc, .cap = 64 * SUB_PIECES, .scratch = scratch, .scap = sizeof scratch };
    rx_ctx ctx;
    int bad, rc = pcrec_subst_ctx_init(&ctx, &it, &rx_info, t, NULL, vres, 0, &bad);
    if (rc < 0) return rc;
    return pcrec_subst_replace_all(rx_info.next_n, &it, t, &ctx, NULL, 0, &o, out, cap, len);
}

static long find_all(const unsigned char *s, size_t n) {
    rx_iter it = RX_ITER_INIT(s, n);
    static ptrdiff_t caps[64 * RX_NCAPS][2];
    long tot = 0; size_t got;
    do { got = rx_next_n(&it, caps, 64); tot += (long)got; } while (got == 64);
    if (it.rc < 0) return it.rc;
    return tot;
}

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: drv MODE FILE REPS\n"); return 2; }
    FILE *f = fopen(argv[2], "rb"); if (!f) { perror("open"); return 2; }
    fseek(f, 0, SEEK_END); size_t n = (size_t)ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *s = malloc(n + 1);
    if (fread(s, 1, n, f) != n) return 2;
    fclose(f);
    size_t cap = n * 2 + 4096;
    unsigned char *out = malloc(cap); memset(out, 0, cap);
    int reps = atoi(argv[3]);
    if (pmc_init() <= 0) { fprintf(stderr, "no rdpmc\n"); return 3; }
    int fi = pfd(PERF_COUNT_HW_INSTRUCTIONS), fc = pfd(PERF_COUNT_HW_CPU_CYCLES);
    for (int r = 0; r < reps; r++) {
        long res = 0; size_t len = 0;
        uint64_t vi = 0, vc = 0;
        struct timespec t0, t1;
        ioctl(fi, PERF_EVENT_IOC_RESET, 0); ioctl(fc, PERF_EVENT_IOC_RESET, 0);
        clock_gettime(CLOCK_MONOTONIC, &t0);
        ioctl(fi, PERF_EVENT_IOC_ENABLE, 0); ioctl(fc, PERF_EVENT_IOC_ENABLE, 0);
        if (!strcmp(argv[1], "subst")) res = sub_all(s, n, out, cap, &len);
        else if (!strcmp(argv[1], "find")) res = find_all(s, n);
        ioctl(fi, PERF_EVENT_IOC_DISABLE, 0); ioctl(fc, PERF_EVENT_IOC_DISABLE, 0);
        clock_gettime(CLOCK_MONOTONIC, &t1);
        if (read(fi, &vi, 8) != 8 || read(fc, &vc, 8) != 8) { vi = vc = 0; }
        double ms = (t1.tv_sec - t0.tv_sec) * 1e3 + (t1.tv_nsec - t0.tv_nsec) / 1e6;
        printf("%s res=%ld len=%zu instr=%llu cycles=%llu ipc=%.2f ms=%.1f(not-evidence)\n",
               argv[1], res, len, (unsigned long long)vi, (unsigned long long)vc,
               vc ? (double)vi / vc : 0, ms);
#ifdef INSTR_PRINT
        INSTR_PRINT
#endif
    }
    return 0;
}
