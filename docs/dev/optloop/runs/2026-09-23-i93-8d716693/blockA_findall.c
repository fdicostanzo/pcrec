#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "art.h"
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);
  return t.tv_sec + 1e-9*t.tv_nsec;}
int main(int argc,char**argv){
  FILE*f=fopen(argv[1],"rb"); fseek(f,0,SEEK_END); long n=ftell(f); rewind(f);
  unsigned char*b=malloc(n); if(fread(b,1,n,f)!=(size_t)n) return 2; fclose(f);
  long iters = argc>2 ? atol(argv[2]) : 5;
  ptrdiff_t caps[RX_NCAPS][2];
  double best=1e30; long count=0;
  for(long it=0; it<iters; it++){
    double t0=now(); size_t pos=0; count=0;
    for(;;){ int r=rx_search(b,(size_t)n,pos,caps); if(r==0) break;
             if(r<0){ printf("giveup %d\n", r); break; }
             size_t s=(size_t)caps[0][0], e=(size_t)caps[0][1];
             count++; pos = (e>s)?e:s+1; if(pos>(size_t)n) break; }
    double dt=now()-t0; if(dt<best) best=dt; }
  printf("%-24s n=%ld matches=%ld best=%.9f s  %.4f ns/byte\n",
         argv[1], n, count, best, best*1e9/(double)n);
  return 0; }
