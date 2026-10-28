/* tests/code/geoip.h — UC-3's user header: a function DEFINED in the user's
 * own source (geoip.c, linked through harness.manifest), declared here. */
#ifndef TESTS_CODE_GEOIP_H
#define TESTS_CODE_GEOIP_H
#include <stddef.h>
int geo_is_private(const unsigned char *s, size_t n);
#endif
