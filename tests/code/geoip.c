/* tests/code/geoip.c — UC-3's user source, a stub: an address is private
 * when it starts with `10.` or `192.168.`. Linked into every driver of this
 * section by harness.manifest; the artifact reaches it through geoip.h. */
#include <string.h>
#include "geoip.h"

int geo_is_private(const unsigned char *s, size_t n)
{
    return (n >= 3 && !memcmp(s, "10.", 3)) ||
           (n >= 8 && !memcmp(s, "192.168.", 8));
}
