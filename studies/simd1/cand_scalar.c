#include <stddef.h>
#include <string.h>

/* Naive scalar control: for each candidate start, check 'h' then full memcmp.
 * i + 5 <= n keeps every read inside [hay, hay+n); n < 5 never enters the loop. */
const char *find_hello_scalar(const char *hay, size_t n)
{
    for (size_t i = 0; i + 5 <= n; i++) {
        if (hay[i] == 'h' && memcmp(hay + i, "hello", 5) == 0) {
            return hay + i;
        }
    }
    return NULL;
}
