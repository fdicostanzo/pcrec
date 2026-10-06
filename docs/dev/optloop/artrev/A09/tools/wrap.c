#define rx_search        ARM(rx_search)
#define rx_search_in     ARM(rx_search_in)
#define rx_match         ARM(rx_match)
#define rx_match_in      ARM(rx_match_in)
#define rx_match_caps    ARM(rx_match_caps)
#define rx_match_caps_in ARM(rx_match_caps_in)
#define rx_next_pos      ARM(rx_next_pos)
#define rx_valid_upto    ARM(rx_valid_upto)
#define rx_info          ARM(rx_info)
#define CAT2(a,b) a##_##b
#define CAT(a,b) CAT2(a,b)
#define ARM(x) CAT(x, ARMNAME)
#include "artifact.c"
int CAT(pf, ARMNAME)(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*w)[2]) { return rx_prefilter(s, n, from, w); }
