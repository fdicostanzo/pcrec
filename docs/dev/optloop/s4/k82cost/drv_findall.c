/* k82cost: find-all timing driver for the T3 handoff twins (litscan_k82b.md
 * §5.2). Calls rx_search from 0, then from each match end (end+1 on an empty
 * match), over the whole subject; calibrates to >= 50 ms per timed loop and
 * prints the median ns/B of 5 loops plus the match count. Mac, directional. */
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <time.h>
int rx_search(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec*1e9+t.tv_nsec;}
static long findall(const unsigned char *s, size_t n){ long m=0; size_t p=0; ptrdiff_t c[1][2];
    while (p <= n && rx_search(s, n, p, c) == 1) { m++; p = (size_t)c[0][1] > p || c[0][1] > c[0][0] ? (size_t)c[0][1] + (c[0][1]==c[0][0]) : p + 1; }
    return m; }
static int cmp(const void*a,const void*b){double x=*(double*)a,y=*(double*)b;return x<y?-1:x>y;}
int main(int argc,char**argv){ FILE*f=fopen(argv[1],"rb"); fseek(f,0,2); size_t n=ftell(f); rewind(f);
    unsigned char*s=malloc(n+1); if(fread(s,1,n,f)!=n) return 2; fclose(f);
    long m=findall(s,n); int reps=1; for(;;){double t0=now(); for(int i=0;i<reps;i++) findall(s,n); if(now()-t0>5e7) break; reps*=2;}
    double v[5]; for(int k=0;k<5;k++){double t0=now(); for(int i=0;i<reps;i++) findall(s,n); v[k]=(now()-t0)/reps/n;}
    qsort(v,5,sizeof v[0],cmp); printf("matches=%ld median=%.4f ns/B\n", m, v[2]); return 0; }
