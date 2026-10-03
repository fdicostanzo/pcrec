#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
static inline uint16_t rx_ld2(const unsigned char *p){uint16_t w; memcpy(&w,p,2); return w;}
static inline uint32_t rx_ld4(const unsigned char *p){uint32_t w; memcpy(&w,p,4); return w;}
static inline uint64_t rx_ld8(const unsigned char *p){uint64_t w; memcpy(&w,p,8); return w;}
#define C2(s) rx_ld2((const unsigned char *)(s))
#define C4(s) rx_ld4((const unsigned char *)(s))
#define C8(s) rx_ld8((const unsigned char *)(s))
#define K4 C4("\337\337\337\337")
#define K8 C8("\337\337\337\337\337\337\337\337")
__attribute__((noinline)) static size_t and6(const unsigned char *s,size_t n){size_t c=0;
 for(size_t p=0;p<n;p++) c+= p+6<=n && (rx_ld4(s+p)&K4)==C4("SELE") && (rx_ld4(s+p+2)&K4)==C4("LECT"); return c;}
__attribute__((noinline)) static size_t or6(const unsigned char *s,size_t n){size_t c=0;
 for(size_t p=0;p<n;p++) c+= p+6<=n && !(((rx_ld4(s+p)&K4)^C4("SELE"))|((rx_ld4(s+p+2)&K4)^C4("LECT"))); return c;}
__attribute__((noinline)) static size_t byt6(const unsigned char *s,size_t n){size_t c=0; /* today's VM-ish byte chain */
 for(size_t p=0;p<n;p++) c+= p+6<=n && (s[p]|32)=='s'&&(s[p+1]|32)=='e'&&(s[p+2]|32)=='l'&&(s[p+3]|32)=='e'&&(s[p+4]|32)=='c'&&(s[p+5]|32)=='t'; return c;}
__attribute__((noinline)) static size_t and12(const unsigned char *s,size_t n){size_t c=0;
 for(size_t p=0;p<n;p++) c+= p+12<=n && (rx_ld8(s+p)&K8)==C8("INFORMAT") && (rx_ld8(s+p+4)&K8)==C8("RMATIONS"); return c;}
__attribute__((noinline)) static size_t or12(const unsigned char *s,size_t n){size_t c=0;
 for(size_t p=0;p<n;p++) c+= p+12<=n && !(((rx_ld8(s+p)&K8)^C8("INFORMAT"))|((rx_ld8(s+p+4)&K8)^C8("RMATIONS"))); return c;}
__attribute__((noinline)) static size_t mc7(const unsigned char *s,size_t n){size_t c=0;
 for(size_t p=0;p<n;p++) c+= p+7<=n && !memcmp(s+p,"selects",7); return c;}
__attribute__((noinline)) static size_t ov7(const unsigned char *s,size_t n){size_t c=0;
 for(size_t p=0;p<n;p++) c+= p+7<=n && rx_ld4(s+p)==C4("sele") && rx_ld4(s+p+3)==C4("ects"); return c;}
__attribute__((noinline)) static size_t ovor7(const unsigned char *s,size_t n){size_t c=0;
 for(size_t p=0;p<n;p++) c+= p+7<=n && !((rx_ld4(s+p)^C4("sele"))|(rx_ld4(s+p+3)^C4("ects"))); return c;}
typedef size_t (*fn)(const unsigned char*,size_t);
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec*1e9+t.tv_nsec;}
int main(int argc,char**argv){ int regime=atoi(argv[1]); size_t n=1<<20; unsigned char*s=malloc(n+16);
 srand(7); for(size_t i=0;i<n;i++) s[i]="abcdefghijklmnopqrstuvwxyz      .,"[rand()%34];
 if(regime==1) for(size_t i=0;i+16<n;i+=29){ const char*w=(rand()&1)?"SeLeCx informatioX selectz":"selectx INFORMATIONs selecTs"; memcpy(s+i,w,12);} /* near misses */
 struct {const char*nm;fn f;} A[]={{"byte6",byt6},{"and6",and6},{"or6",or6},{"and12",and12},{"or12",or12},{"mc7",mc7},{"ov7",ov7},{"ovor7",ovor7}};
 for(int a=0;a<8;a++){ double best=1e30; size_t r=0; for(int k=0;k<9;k++){double t0=now(); for(int q=0;q<20;q++) r+=A[a].f(s,n); double t=(now()-t0)/20/n; if(t<best)best=t;}
   printf("regime%d %-6s %.3f ns/pos (chk %zu)\n",regime,A[a].nm,best,r); }
 return 0;}
