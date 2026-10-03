#include <stdint.h>
#include <string.h>
#include <stddef.h>
static inline uint32_t rx_ld4(const unsigned char *p){uint32_t w; memcpy(&w,p,4); return w;}
#define C4(s) rx_ld4((const unsigned char *)(s))
int ov5(const unsigned char *s, size_t p, size_t n){
  return p + 5 <= n && rx_ld4(s+p) == C4("/use") && rx_ld4(s+p+1) == C4("user");
}
