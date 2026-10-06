#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include "artifact.h"
#define DECL(a) int rx_search_##a(const unsigned char*,size_t,size_t,ptrdiff_t(*)[2]); \
 int rx_search_in_##a(const unsigned char*,size_t,size_t,ptrdiff_t(*)[2],const rx_buffers*); \
 ptrdiff_t rx_match_in_##a(const rx_ctx*,const rx_buffers*);
DECL(orig) DECL(twin)
int main(int argc,char**argv){
 long bad=0,tot=0,give=0; static char fr[4096] __attribute__((aligned(64))), tr[4096] __attribute__((aligned(64)));
 for(int i=1;i<argc;i++){
  FILE*f=fopen(argv[i],"rb");fseek(f,0,2);long n=ftell(f);rewind(f);unsigned char*s=malloc(n?n:1);fread(s,1,n,f);fclose(f);
  long step = n > 20000 ? 13 : 1;
  for(long from=0; from<=n; from+=step){
   for(int k=0;k<4;k++){
    rx_buffers b; b.frames=fr; b.trail=tr; b.nframes = (k&1)?1:0; b.ntrail=(k&2)?1:0;
    ptrdiff_t a[1][2]={{-9,-9}},c[1][2]={{-9,-9}};
    int ra = k==3 ? rx_search_orig(s,n,from,a) : rx_search_in_orig(s,n,from,a,&b);
    int rb = k==3 ? rx_search_twin(s,n,from,c) : rx_search_in_twin(s,n,from,c,&b);
    rx_ctx x; memset(&x,0,sizeof x); x.subject=s; x.len=n; x.pos=from;
    ptrdiff_t ma=rx_match_in_orig(&x,&b), mb=rx_match_in_twin(&x,&b);
    tot++; if(ra<0)give++;
    if(ra!=rb || (ra==1&&(a[0][0]!=c[0][0]||a[0][1]!=c[0][1])) || ma!=mb){ if(bad<5)printf("DIFF %s from=%ld k=%d s:%d/%d m:%td/%td\n",argv[i],from,k,ra,rb,ma,mb); bad++; }
   }
  }
  free(s);
 }
 printf("budget-shrunk calls=%ld give-ups(orig)=%ld differences=%ld\n",tot,give,bad); return bad!=0;
}
