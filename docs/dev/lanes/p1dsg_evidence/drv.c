/* p1dsg find-all driver (after subtri's drv.c): instructions:u / cycles:u around
 * a plain rx_next_n find-all; HASH=1 hashes every capture span.
 * Build: gcc -O2 -DART=\"dir/rx.c\" -I dir drv.c   Run: drv FILE REPS */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/perf_event.h>
#include <sys/ioctl.h>
#include ART
static int pfd(uint64_t cfg) {
    struct perf_event_attr a; memset(&a, 0, sizeof a);
    a.type = PERF_TYPE_HARDWARE; a.size = sizeof a; a.config = cfg;
    a.disabled = 1; a.exclude_kernel = 1; a.exclude_hv = 1;
    return (int)syscall(SYS_perf_event_open, &a, 0, -1, -1, 0);
}
static unsigned long long span_hash;
static long find_all(const unsigned char *s, size_t n) {
    rx_iter it = RX_ITER_INIT(s, n);
    static ptrdiff_t caps[64 * RX_NCAPS][2];
    long tot = 0; size_t got;
    do { got = rx_next_n(&it, caps, 64); tot += (long)got;
         for (size_t i = 0; i < got; i++) for (int g = 0; g < RX_NCAPS; g++) span_hash = span_hash * 1000003ULL + (unsigned long long)caps[i * RX_NCAPS + g][0] * 31ULL + (unsigned long long)caps[i * RX_NCAPS + g][1];
    } while (got == 64);
    if (it.rc < 0) return it.rc;
    return tot;
}
int main(int argc, char **argv) {
    if (argc < 3) return 2;
    FILE *f = fopen(argv[1], "rb"); if (!f) { perror("open"); return 2; }
    fseek(f, 0, SEEK_END); size_t n = (size_t)ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *s = malloc(n + 1);
    if (fread(s, 1, n, f) != n) return 2;
    fclose(f);
    int reps = atoi(argv[2]);
    int fi = pfd(PERF_COUNT_HW_INSTRUCTIONS), fc = pfd(PERF_COUNT_HW_CPU_CYCLES);
    for (int r = 0; r < reps; r++) {
        uint64_t vi = 0, vc = 0; span_hash = 0;
        ioctl(fi, PERF_EVENT_IOC_RESET, 0); ioctl(fc, PERF_EVENT_IOC_RESET, 0);
        ioctl(fi, PERF_EVENT_IOC_ENABLE, 0); ioctl(fc, PERF_EVENT_IOC_ENABLE, 0);
        long res = find_all(s, n);
        ioctl(fi, PERF_EVENT_IOC_DISABLE, 0); ioctl(fc, PERF_EVENT_IOC_DISABLE, 0);
        if (read(fi, &vi, 8) != 8 || read(fc, &vc, 8) != 8) { vi = vc = 0; }
        printf("res=%ld hash=%016llx instr=%llu cycles=%llu\n", res, span_hash,
               (unsigned long long)vi, (unsigned long long)vc);
    }
    return 0;
}
