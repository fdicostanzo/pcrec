/* [START-SET] Mac SCRATCH find-all timing (D144 addendum 1: directional only,
 * never a verdict): base vs twin on one subject file, interleaved, best of R. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <time.h>
#include "rx.h"
#include "tw.h"
static double now(void){ struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec+t.tv_nsec*1e-9; }
typedef int (*fn)(const unsigned char*,size_t,size_t,ptrdiff_t(*)[2]);
static long findall(fn f, const unsigned char*s, size_t n, long *sum){ ptrdiff_t c[16][2]; size_t p=0; long k=0;
  for(;;){ int r=f(s,n,p,c); if(r!=1) { if(r<0) return -1000+r; break; } k++; *sum+=c[0][0]; p = (size_t)c[0][1] > p ? (size_t)c[0][1] : p+1; if(p>n) break; } return k; }
int main(int argc,char**argv){ FILE*fp=fopen(argv[1],"rb"); fseek(fp,0,SEEK_END); long n=ftell(fp); rewind(fp);
  unsigned char*s=malloc(n); fread(s,1,n,fp); fclose(fp); int R=argc>2?atoi(argv[2]):5;
  double bb=1e9,bt=1e9; long kb=0,kt=0,sb=0,st=0;
  for(int i=0;i<R;i++){ double t0=now(); kb=findall(rx_search,s,n,&sb); double t1=now(); kt=findall(tw_search,s,n,&st); double t2=now();
    if(t1-t0<bb) bb=t1-t0; if(t2-t1<bt) bt=t2-t1; }
  printf("matches base=%ld twin=%ld  base %.3f ns/B  twin %.3f ns/B  ratio x%.1f%s\n",kb,kt,bb*1e9/n,bt*1e9/n,bb/bt,(kb==kt&&sb==st)?"":"  ANSWER MISMATCH");
  return 0; }
