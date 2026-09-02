/* ccdiff micro-driver: the bench's driver.c regime loops, one .so, one subject. */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <dlfcn.h>
#include <time.h>
static int (*pb_search)(const unsigned char*, size_t, size_t, ptrdiff_t(*)[2]);
static long long (*pb_match_caps)(const void*, ptrdiff_t(*)[2]);
struct rx_ctx_min { const unsigned char *subject; size_t len; size_t pos; size_t ncap; const ptrdiff_t (*caps)[2]; void *user; };
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+1e-9*t.tv_nsec;}
int main(int argc,char**argv){
  /* argv: so subjectfile regime iters   regime = findall|match|search */
  void*h=dlopen(argv[1],RTLD_NOW); if(!h){fprintf(stderr,"%s\n",dlerror());return 2;}
  const char*regime=argv[3]; long iters=atol(argv[4]);
  FILE*f=fopen(argv[2],"rb"); fseek(f,0,SEEK_END); long n=ftell(f); fseek(f,0,SEEK_SET);
  unsigned char*buf=malloc(n+1); if(fread(buf,1,n,f)!=(size_t)n)return 3; fclose(f);
  int ncaps=1; int*pn=(int*)dlsym(h,"rx_ncaps_v"); (void)pn;
  ptrdiff_t (*caps)[2]=calloc(64,sizeof *caps);
  volatile long sink=0; double t0,t1;
  if(!strcmp(regime,"match")){
    pb_match_caps=(long long(*)(const void*,ptrdiff_t(*)[2]))dlsym(h,"rx_match_caps");
    struct rx_ctx_min ctx={buf,(size_t)n,0,0,NULL,NULL};
    t0=now();
    for(long it=0;it<iters;it++){ long long r=pb_match_caps(&ctx,caps); sink+=(long)r; }
    t1=now();
  } else {
    pb_search=(int(*)(const unsigned char*,size_t,size_t,ptrdiff_t(*)[2]))dlsym(h,"rx_search");
    if(!pb_search){fprintf(stderr,"no rx_search\n");return 4;}
    if(!strcmp(regime,"findall")){
      t0=now();
      for(long it=0;it<iters;it++){
        size_t pos=0; long count=0;
        for(;;){ int r=pb_search(buf,(size_t)n,pos,caps); if(r==0)break; if(r<0){break;}
          count++; size_t end=(size_t)caps[0][1]; pos=(end>pos)?end:pos+1; if(pos>(size_t)n)break; }
        sink+=count;
      }
      t1=now();
    } else {
      t0=now();
      for(long it=0;it<iters;it++){ int r=pb_search(buf,(size_t)n,0,caps); sink+=r; }
      t1=now();
    }
  }
  (void)ncaps;
  printf("%.1f\t%ld\n",(t1-t0)/iters*1e9,(long)sink);
  return 0;
}
