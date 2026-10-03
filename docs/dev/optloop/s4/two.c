#include <string.h>
#include <stddef.h>
int mc5(const unsigned char *s, size_t p, size_t n){ return p + 5 <= n && !memcmp(s+p, "/user", 5); }
