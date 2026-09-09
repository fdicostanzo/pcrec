/* studies/linktest_probe/microbench_linked.c — P5's minimal exec-and-resolve
 * microbench, LINKED shape: bind, query version, exit. */
#include "pcre2_abi_linked.h"

int main(void)
{
    Pcre2Abi abi;
    char why[256], ver[64];
    if (pcre2_abi_load(&abi, why, sizeof why) != PCRE2_ABI_OK) return 1;
    pcre2_abi_version(&abi, ver, sizeof ver);
    return ver[0] ? 0 : 1;
}
