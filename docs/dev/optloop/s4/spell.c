#include <stdint.h>
#include <string.h>
#include <stddef.h>
/* candidate emitted helpers: endian-neutral loads, constants loaded the same way */
static inline uint16_t rx_ld2(const unsigned char *p){uint16_t w; memcpy(&w,p,2); return w;}
static inline uint32_t rx_ld4(const unsigned char *p){uint32_t w; memcpy(&w,p,4); return w;}
static inline uint64_t rx_ld8(const unsigned char *p){uint64_t w; memcpy(&w,p,8); return w;}
#define C2(s) rx_ld2((const unsigned char *)(s))
#define C4(s) rx_ld4((const unsigned char *)(s))
#define C8(s) rx_ld8((const unsigned char *)(s))

/* L=6 caseless "select": two 4-byte windows at 0 and 2 */
int and6(const unsigned char *s, size_t p, size_t n){
  return p + 6 <= n
    && (rx_ld4(s+p) & C4("\337\337\337\337")) == C4("SELE")
    && (rx_ld4(s+p+2) & C4("\337\337\337\337")) == C4("LECT");
}
int or6(const unsigned char *s, size_t p, size_t n){
  return p + 6 <= n
    && !(((rx_ld4(s+p) & C4("\337\337\337\337")) ^ C4("SELE"))
       | ((rx_ld4(s+p+2) & C4("\337\337\337\337")) ^ C4("LECT")));
}
/* L=3 caseless "ion" */
int and3(const unsigned char *s, size_t p, size_t n){
  return p + 3 <= n
    && (rx_ld2(s+p) & C2("\337\337")) == C2("IO")
    && (rx_ld2(s+p+1) & C2("\337\337")) == C2("ON");
}
int or3(const unsigned char *s, size_t p, size_t n){
  return p + 3 <= n
    && !(((rx_ld2(s+p) & C2("\337\337")) ^ C2("IO"))
       | ((rx_ld2(s+p+1) & C2("\337\337")) ^ C2("ON")));
}
/* L=12 mixed: "group_concat" caseless letters, '_' exact (K=0xff) */
int and12(const unsigned char *s, size_t p, size_t n){
  return p + 12 <= n
    && (rx_ld8(s+p) & C8("\337\337\337\337\337\377\337\337")) == C8("GROUP_CO")
    && (rx_ld8(s+p+4) & C8("\337\377\337\337\337\337\337\337")) == C8("P_CONCAT");
}
int or12(const unsigned char *s, size_t p, size_t n){
  return p + 12 <= n
    && !(((rx_ld8(s+p) & C8("\337\337\337\337\337\377\337\337")) ^ C8("GROUP_CO"))
       | ((rx_ld8(s+p+4) & C8("\337\377\337\337\337\337\337\337")) ^ C8("P_CONCAT")));
}
/* L=20 masked multi-word: 3 words at 0, 8, 12 */
int and20(const unsigned char *s, size_t p, size_t n){
  return p + 20 <= n
    && (rx_ld8(s+p) & C8("\337\337\337\337\337\337\337\337")) == C8("INFORMAT")
    && (rx_ld8(s+p+8) & C8("\337\337\337\337\377\337\337\337")) == C8("ION_SCHE")
    && (rx_ld8(s+p+12) & C8("\377\337\337\337\337\337\337\337")) == C8("_SCHEMAX");
}
/* exact L=5 "/user": memcmp vs overlap */
int mc5(const unsigned char *s, size_t p, size_t n){ return p + 5 <= n && !memcmp(s+p, "/user", 5); }
int ov5(const unsigned char *s, size_t p, size_t n){
  return p + 5 <= n && rx_ld4(s+p) == C4("/use") && rx_ld4(s+p+1) == C4("user");
}
int mc3(const unsigned char *s, size_t p, size_t n){ return p + 3 <= n && !memcmp(s+p, "://", 3); }
int ov3(const unsigned char *s, size_t p, size_t n){
  return p + 3 <= n && rx_ld2(s+p) == C2(":/") && rx_ld2(s+p+1) == C2("//");
}
