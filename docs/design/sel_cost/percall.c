#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>
#include <time.h>
extern int rx_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2]);
static uint64_t now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return (uint64_t)t.tv_sec*1000000000ull+t.tv_nsec;}
static int cmp(const void*a,const void*b){double x=*(double*)a,y=*(double*)b;return x<y?-1:x>y;}
int main(int c,char**v){FILE*f=fopen(v[1],"rb");fseek(f,0,2);long n=ftell(f);fseek(f,0,0);unsigned char*b=malloc(n+1);fread(b,1,n,f);
 ptrdiff_t cp[1][2]; int r=rx_search(b,n,0,cp); long it=1; uint64_t t0;
 do{it*=2;t0=now();for(long i=0;i<it;i++)rx_search(b,n,0,cp);}while(now()-t0<20000000);
 double t[7];for(int k=0;k<7;k++){t0=now();for(long i=0;i<it;i++)rx_search(b,n,0,cp);t[k]=(double)(now()-t0)/it;}
 qsort(t,7,sizeof t[0],cmp);printf("r=%d span=%td,%td ns/call=%.1f\n",r,r==1?cp[0][0]:-1,r==1?cp[0][1]:-1,t[3]);return 0;}
