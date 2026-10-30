/* perf driver: drv SUBJECT-FILE REPS MODE(0=search_in big,1=default search) ; find-all, prints count+checksum */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "gen.h"
static unsigned long esc; void rx_tier_escalated(void){esc++;}
static unsigned char *slurp(const char *p, size_t *n){FILE*f=fopen(p,"rb");if(!f)exit(2);fseek(f,0,SEEK_END);long l=ftell(f);rewind(f);unsigned char*b=malloc(l+1);if(fread(b,1,l,f)!=(size_t)l)exit(2);fclose(f);*n=l;return b;}
int main(int argc,char**argv){
  size_t n; unsigned char*s=slurp(argv[1],&n); long reps=atol(argv[2]); int mode=argc>3?atoi(argv[3]):0;
  size_t nf=(size_t)1<<20, nt=(size_t)1<<22; if(mode==2){nt=(size_t)atol(argv[4]); if(argc>5) nf=(size_t)atol(argv[5]); mode=0;}
  rx_buffers b={malloc(nf*RX_RESUME_FRAME_SIZE),nf,malloc(nt*RX_TRAIL_FRAME_SIZE),nt};
  ptrdiff_t caps[RX_NCAPS][2]; unsigned long cnt=0, sum=0; int lastrc=0;
  for(long r=0;r<reps;r++){ size_t pos=0;
    while(pos<=n){ int rc= mode? rx_search(s,n,pos,caps) : rx_search_in(s,n,pos,caps,&b); lastrc=rc;
      if(rc!=1)break; cnt++; for(int i=0;i<RX_NCAPS;i++) sum=sum*31+(unsigned long)(caps[i][0]+3*caps[i][1]);
      pos = caps[0][1]>caps[0][0]? (size_t)caps[0][1] : (size_t)caps[0][0]+1; }
  }
  printf("cnt %lu sum %lu lastrc %d esc %lu\n",cnt,sum,lastrc,esc); return 0;}
