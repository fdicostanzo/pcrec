/* [START-SET] three-artifact differential (base / narrowed / narrowed+reseed),
 * every subject line, every startpos, full capture vector.  ANSWERS ONLY. */
#include <stdio.h>
#include <string.h>
#include <stddef.h>
#include "rx.h"
#include "tw.h"
#include "rs.h"
int main(void){ char line[256]; long cases=0, dtw=0, drs=0, m=0;
  while(fgets(line,sizeof line,stdin)){ size_t n=strlen(line); if(n&&line[n-1]=='\n') line[--n]=0;
    const unsigned char*s=(const unsigned char*)line;
    for(size_t f=0; f<=n; f++){ ptrdiff_t a[RX_NCAPS][2], b[RX_NCAPS][2], c[RX_NCAPS][2];
      memset(a,0xff,sizeof a); memset(b,0xff,sizeof b); memset(c,0xff,sizeof c);
      int r0=rx_search(s,n,f,a), r1=tw_search(s,n,f,b), r2=rs_search(s,n,f,c); cases++; if(r0==1) m++;
      if(r0!=r1 || (r0==1&&memcmp(a,b,sizeof a))) { if(dtw<3) printf("  TW [%s]@%zu base=%d(%td,%td) tw=%d\n",line,f,r0,a[0][0],a[0][1],r1); dtw++; }
      if(r0!=r2 || (r0==1&&memcmp(a,c,sizeof a))) { if(drs<3) printf("  RS [%s]@%zu base=%d(%td,%td) rs=%d\n",line,f,r0,a[0][0],a[0][1],r2); drs++; }
    }}
  printf("cases=%ld matches=%ld narrowed_no_reseed_diffs=%ld narrowed_reseed_diffs=%ld\n",cases,m,dtw,drs); return drs!=0; }
