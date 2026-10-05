#include <stdio.h>
#include <string.h>
#include <stddef.h>
#include "rx.h"
#include "tw.h"
#include "rs.h"
/* find-all, every startpos: compare the three artifacts' answers */
static int one(int (*f)(const unsigned char*,size_t,size_t,ptrdiff_t(*)[2]), const unsigned char*s,size_t n,size_t from, ptrdiff_t *a,ptrdiff_t *b){
  ptrdiff_t sp[8][2]; memset(sp,0,sizeof sp); int r=f(s,n,from,sp); *a=sp[0][0]; *b=sp[0][1]; return r; }
int main(void){ char line[256]; long cases=0, dtw=0, drs=0;
  while(fgets(line,sizeof line,stdin)){ size_t n=strlen(line); if(n&&line[n-1]=='\n') line[--n]=0;
    const unsigned char*s=(const unsigned char*)line;
    for(size_t f=0; f<=n; f++){ ptrdiff_t a0,b0,a1,b1,a2,b2;
      int r0=one(rx_search,s,n,f,&a0,&b0), r1=one(tw_search,s,n,f,&a1,&b1), r2=one(rs_search,s,n,f,&a2,&b2);
      cases++;
      if(r0!=r1 || (r0==1&&(a0!=a1||b0!=b1))) { if(dtw<5) printf("TW [%s]@%zu base=%d(%td,%td) tw=%d(%td,%td)\n",line,f,r0,a0,b0,r1,a1,b1); dtw++; }
      if(r0!=r2 || (r0==1&&(a0!=a2||b0!=b2))) { if(drs<5) printf("RS [%s]@%zu base=%d(%td,%td) rs=%d(%td,%td)\n",line,f,r0,a0,b0,r2,a2,b2); drs++; }
    }}
  printf("cases=%ld twin_diffs=%ld reseed_diffs=%ld\n",cases,dtw,drs); return 0; }
