/* k82cost: the calibration probe the cost model's machine terms come from
 * (litscan_k82b.md §1.3). Measures, on THIS box and libc:
 *   f    ns per memchr CALL that finds its byte at distance 0 (the entry term)
 *   beta ns per BYTE memchr reads (slope over distances 64..65536)
 *   s    ns per STOP of the run block's memchr arm: re-search + 3-byte masked
 *        compare that fails, on a buffer where the scan byte recurs every D
 * Directional only (no taskset, M1); a build-time calibration would emit the
 * same three numbers as a table row. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec*1e9+t.tv_nsec;}
static volatile size_t sink;
static double time_dist(unsigned char *b, size_t d, long reps){
    b[d]='Z'; double t0=now(); size_t acc=0;
    for(long i=0;i<reps;i++){ const unsigned char *p=memchr(b,(int)("Z"[0]),d+1); acc+=(size_t)(p-b); __asm__ volatile(""::"r"(acc):"memory"); }
    double t=(now()-t0)/reps; b[d]='.'; sink=acc; return t;
}
static double time_stops(unsigned char *b, size_t n, size_t D){
    for(size_t i=0;i<n;i++) b[i]='.';
    for(size_t i=D;i+3<n;i+=D){ b[i]='c'; b[i+1]='x'; b[i+2]='x'; }
    long stops=0; double t0=now(); int rep;
    for(rep=0;rep<50;rep++){ size_t pos=0;
        while(pos<n){ const unsigned char *q=memchr(b+pos,'c',n-pos); if(!q) break;
            size_t c=(size_t)(q-b); stops++;
            if(c+3<=n && ((b[c]|0x20)=='c') && ((b[c+1]|0x20)=='a') && ((b[c+2]|0x20)=='t')) {sink=c;break;}
            pos=c+1; } }
    return (now()-t0)/stops;
}
int main(void){
    size_t n=1<<20; unsigned char *b=malloc(n+64); memset(b,'.',n+64);
    size_t ds[]={0,16,64,256,1024,4096,16384,65536}; double t[8];
    for(int i=0;i<8;i++){ long reps= ds[i]<1024? 20000000 : (long)(2e9/ (ds[i]+64)); t[i]=time_dist(b,ds[i],reps); printf("memchr d=%6zu  %8.2f ns/call\n",ds[i],t[i]); }
    /* least squares over d>=64 */
    double sx=0,sy=0,sxx=0,sxy=0; int k=0; for(int i=2;i<8;i++){sx+=ds[i];sy+=t[i];sxx+=(double)ds[i]*ds[i];sxy+=ds[i]*t[i];k++;}
    double beta=(k*sxy-sx*sy)/(k*sxx-sx*sx), a=(sy-beta*sx)/k;
    printf("CAL f=%.2f ns/call  beta=%.4f ns/B (fit intercept %.2f)\n", t[0], beta, a);
    size_t Ds[]={8,32,128,512}; for(int i=0;i<4;i++){ double s=time_stops(b,n,Ds[i]); printf("stop D=%4zu  %6.2f ns/stop (incl. %zu B memchr) -> s=%.2f\n",Ds[i],s,Ds[i], s-beta*Ds[i]); }
    return 0;
}
