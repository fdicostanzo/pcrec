#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "s.h"
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+t.tv_nsec*1e-9;}
int main(void){size_t n=64u<<20; unsigned char*s=malloc(n); const char*a="the quick brown fox jumps over the lazy dog 0123456789\n";size_t al=strlen(a),r=12345;
 for(size_t i=0;i<n;i++){r=r*1103515245+12345;s[i]=a[(r>>8)%al];}
 double best=1e9; for(int k=0;k<5;k++){ptrdiff_t c[RX_NCAPS][2];double t0=now();volatile int x=rx_search(s,n,0,c);(void)x;double t=(now()-t0)/n*1e9;if(t<best)best=t;}
 printf("%.4f ns/byte\n",best);return 0;}
