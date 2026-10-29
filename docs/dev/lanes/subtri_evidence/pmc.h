#ifndef PMC_H
#define PMC_H
/* user-space instruction counter via perf mmap + rdpmc (subtri scratch) */
#include <linux/perf_event.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>
static struct perf_event_mmap_page *pmc_pg;
static int pmc_init(void) {
    struct perf_event_attr a; memset(&a, 0, sizeof a);
    a.type = PERF_TYPE_HARDWARE; a.size = sizeof a; a.config = getenv("PMC_CYCLES") ? PERF_COUNT_HW_CPU_CYCLES : PERF_COUNT_HW_INSTRUCTIONS;
    a.exclude_kernel = 1; a.exclude_hv = 1;
    int fd = (int)syscall(SYS_perf_event_open, &a, 0, -1, -1, 0);
    if (fd < 0) return -1;
    pmc_pg = mmap(0, sysconf(_SC_PAGESIZE), PROT_READ, MAP_SHARED, fd, 0);
    if (pmc_pg == MAP_FAILED) return -2;
    return pmc_pg->cap_user_rdpmc ? (int)pmc_pg->index : -3;
}
static inline uint64_t pmc_now(void) {
    uint32_t seq; uint64_t v;
    do {
        seq = pmc_pg->lock; __asm__ volatile("" ::: "memory");
        int64_t pmc = (int64_t)__builtin_ia32_rdpmc((int)pmc_pg->index - 1);
        pmc <<= 64 - pmc_pg->pmc_width; pmc >>= 64 - pmc_pg->pmc_width;
        v = (uint64_t)(pmc_pg->offset + pmc);
        __asm__ volatile("" ::: "memory");
    } while (pmc_pg->lock != seq);
    return v;
}
#endif
