/* studies/linktest_probe/p2_header_vs_runtime.c — P2's own witness: proves
 * the header's PCRE2_MAJOR/PCRE2_MINOR (compile-time, from whatever pcre2.h
 * the -I flag pointed at) and pcre2_config(PCRE2_CONFIG_VERSION) (run-time,
 * from whatever libpcre2 the linker/loader actually bound) are the SAME
 * library under direct linking — the property that is structurally
 * impossible to violate once there is only one libpcre2 in the picture,
 * unlike the dlopen shim's candidate list resolving a library the header
 * never described (U13/U15b). */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <string.h>

int main(void)
{
    char buf[64] = {0};
    pcre2_config(PCRE2_CONFIG_VERSION, buf);
    printf("header PCRE2_MAJOR.PCRE2_MINOR: %d.%d\n", PCRE2_MAJOR, PCRE2_MINOR);
    printf("runtime pcre2_config(VERSION):  %s\n", buf);

    char want[16];
    snprintf(want, sizeof want, "%d.%d", PCRE2_MAJOR, PCRE2_MINOR);
    int match = strncmp(buf, want, strlen(want)) == 0;
    printf("MATCH: %s\n", match ? "yes" : "NO");
    return match ? 0 : 1;
}
