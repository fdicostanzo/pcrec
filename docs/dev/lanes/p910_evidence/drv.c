/* p910 driver: the bench's find-all (timed.c: rx_search from pos, advance
 * off the match's reported start/end) over each subject file, with
 * user-space instructions/cycles read around the find-all only.
 * Build: gcc -O2 -DART=<dir> drv.c   (includes <dir>/rx.c)
 * Run:   drv REPS FILE...    prints: file count hash instr cycles
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

#define STR2(x) #x
#define STR(x) STR2(x)
#include STR(ART/rx.c)

static int pfd(uint64_t cfg) {
    struct perf_event_attr a; memset(&a, 0, sizeof a);
    a.type = PERF_TYPE_HARDWARE; a.size = sizeof a; a.config = cfg;
    a.disabled = 1; a.exclude_kernel = 1; a.exclude_hv = 1;
    return (int)syscall(SYS_perf_event_open, &a, 0, -1, -1, 0);
}

static unsigned long long hash;
static long find_all(const unsigned char *s, size_t n) {
    ptrdiff_t caps[RX_NCAPS][2];
    size_t pos = 0; long count = 0;
    for (;;) {
        int r = rx_search(s, n, pos, caps);
        if (r == 0) break;
        if (r < 0) return r;
        count++;
        hash = hash * 1000003ULL + (unsigned long long)caps[0][0] * 31ULL + (unsigned long long)caps[0][1];
        size_t st = (size_t)caps[0][0], en = (size_t)caps[0][1];
        pos = en > st ? en : st + 1;
        if (pos > n) break;
    }
    return count;
}

int main(int argc, char **argv) {
    int reps = atoi(argv[1]);
    int fi = pfd(PERF_COUNT_HW_INSTRUCTIONS), fc = pfd(PERF_COUNT_HW_CPU_CYCLES);
    unsigned long long ti = 0;
    for (int a = 2; a < argc; a++) {
        FILE *f = fopen(argv[a], "rb"); if (!f) { perror(argv[a]); return 2; }
        fseek(f, 0, SEEK_END); size_t n = (size_t)ftell(f); fseek(f, 0, SEEK_SET);
        unsigned char *s = malloc(n + 1);
        if (fread(s, 1, n, f) != n) return 2;
        fclose(f);
        uint64_t best_i = ~0ULL, best_c = ~0ULL; long cnt = 0;
        for (int r = 0; r < reps; r++) {
            uint64_t vi = 0, vc = 0;
            hash = 0;
            ioctl(fi, PERF_EVENT_IOC_RESET, 0); ioctl(fc, PERF_EVENT_IOC_RESET, 0);
            ioctl(fi, PERF_EVENT_IOC_ENABLE, 0); ioctl(fc, PERF_EVENT_IOC_ENABLE, 0);
            cnt = find_all(s, n);
            ioctl(fi, PERF_EVENT_IOC_DISABLE, 0); ioctl(fc, PERF_EVENT_IOC_DISABLE, 0);
            if (read(fi, &vi, 8) != 8 || read(fc, &vc, 8) != 8) vi = vc = 0;
            if (vi < best_i) best_i = vi;
            if (vc < best_c) best_c = vc;
        }
        const char *b = strrchr(argv[a], '/');
        printf("%s\t%zu\t%ld\t%016llx\t%llu\t%llu\n", b ? b + 1 : argv[a], n, cnt, hash,
               (unsigned long long)best_i, (unsigned long long)best_c);
        ti += best_i;
        free(s);
    }
    printf("TOTAL\t-\t-\t-\t%llu\t-\n", ti);
    return 0;
}
