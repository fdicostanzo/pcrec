/* pdrv SUBJ : one _in call (NF/NT env), print rc and pushes per subject byte */
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include HDR
extern unsigned long long altd_npush;
int main(int argc,char**argv){ FILE*f=fopen(argv[1],"rb"); if(!f) return 2; fseek(f,0,SEEK_END); size_t n=ftell(f); fseek(f,0,SEEK_SET);
  unsigned char*s=malloc(n+1); if(fread(s,1,n,f)!=n) return 2; fclose(f);
  size_t nf=strtoul(getenv("NF"),0,10), nt=strtoul(getenv("NT"),0,10);
  void*F=malloc(nf*PFX_RESUME_FRAME_SIZE),*T=malloc(nt*PFX_TRAIL_FRAME_SIZE); PFX_buffers bu={F,nf,T,nt}; ptrdiff_t caps[PFX_NCAPS][2];
  int rc=PFX_search_in(s,n,0,caps,&bu); printf("rc=%d pushes/byte=%.3f\n",rc,(double)altd_npush/n); return 0;}
