/* d27 driver: two code artifacts (prefixes pa, pb) in one translation unit
 * (match_api.md §1¶5-¶6b: the shared and callout families are guarded so two
 * artifacts compose; §11.9¶4: each one's macro set is #undef'ed after its
 * segments, so the second can define it again). */
#include <stdio.h>
#include GEN_A
#include GEN_B

int main(void)
{
    int a = pa_search((const unsigned char *)"xa", 2, 0, NULL);
    int b = pb_search((const unsigned char *)"xb", 2, 0, NULL);
    printf("%s two.pa_search\n", a == 1 ? "PASS" : "FAIL");
    printf("%s two.pb_search\n", b == 1 ? "PASS" : "FAIL");
    return 0;
}
