/* memfnsurvey: what PCRE2-JIT's own search costs per call and per byte on a
 * MISS (the needle absent, whole subject scanned). Same calibration as tim.c.
 * Mac + Homebrew libpcre2 10.48 (NOT the 10.46 reference): directional. */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
static double now_ns(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec * 1e9 + t.tv_nsec; }
int main(void) {
    static const char *pats[] = {"Z", "(?i)z", "Zq", "Z...q", "[Zz]", "[XYZ]", "[0-9]", "Zqx", "(?i)zqx", "[a-z]*Z"};
    static const size_t ns[] = {1, 8, 16, 64, 256, 1024, 4096, 65536};
    uint8_t *buf = malloc(65536);
    for (int i = 0; i < 65536; i++) buf[i] = (uint8_t)('a' + i % 20);
    char ver[64]; pcre2_config(PCRE2_CONFIG_VERSION, ver); printf("# pcre2-jit %s (system lib, x86-64), ns/call min..max of 3 loops >= 50 ms, case=miss\n%-10s", ver, "pattern");
    for (size_t j = 0; j < sizeof ns / sizeof ns[0]; j++) printf(" %13zu", ns[j]);
    printf("\n");
    for (size_t p = 0; p < sizeof pats / sizeof pats[0]; p++) {
        int ec; PCRE2_SIZE eo;
        pcre2_code *re = pcre2_compile((PCRE2_SPTR)pats[p], PCRE2_ZERO_TERMINATED, 0, &ec, &eo, 0);
        if (!re || pcre2_jit_compile(re, PCRE2_JIT_COMPLETE)) { printf("%s: compile fail\n", pats[p]); continue; }
        pcre2_match_data *md = pcre2_match_data_create_from_pattern(re, 0);
        pcre2_match_context *mc = pcre2_match_context_create(0);
        pcre2_jit_stack *js = pcre2_jit_stack_create(32 * 1024, 512 * 1024, 0);
        pcre2_jit_stack_assign(mc, 0, js);
        printf("%-10s", pats[p]);
        for (size_t j = 0; j < sizeof ns / sizeof ns[0]; j++) {
            long reps = 64; double t;
            for (;;) {
                double t0 = now_ns();
                for (long r = 0; r < reps; r++)
                    if (pcre2_jit_match(re, buf, ns[j], 0, 0, md, mc) != PCRE2_ERROR_NOMATCH) { printf("unexpected\n"); return 1; }
                t = now_ns() - t0;
                if (t >= 50e6) break;
                reps = (long)(reps * (t > 1e5 ? 1.2 * 50e6 / t : 16.0));
            }
            double lo = 1e300, hi = 0;
            for (int k = 0; k < 3; k++) {
                double t0 = now_ns();
                for (long r = 0; r < reps; r++) pcre2_jit_match(re, buf, ns[j], 0, 0, md, mc);
                double x = (now_ns() - t0) / reps; if (x < lo) lo = x; if (x > hi) hi = x;
            }
            printf(" %6.1f..%-6.1f", lo, hi);
            fflush(stdout);
        }
        printf("\n");
    }
    return 0;
}
