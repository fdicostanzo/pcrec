/* [START-SET] two-artifact differential: every subject line, every startpos,
 * the full capture vector compared.  ANSWERS ONLY. */
#include <stdio.h>
#include <string.h>
#include <stddef.h>
#include "rx.h"
#include "tw.h"
int main(void){ char line[256]; long cases=0, diffs=0, matches=0;
  while(fgets(line,sizeof line,stdin)){ size_t n=strlen(line); if(n&&line[n-1]=='\n') line[--n]=0;
    const unsigned char*s=(const unsigned char*)line;
    for(size_t f=0; f<=n; f++){ ptrdiff_t a[RX_NCAPS][2], b[TW_NCAPS][2];
      memset(a,0xff,sizeof a); memset(b,0xff,sizeof b);
      int r0=rx_search(s,n,f,a), r1=tw_search(s,n,f,b); cases++; if(r0==1) matches++;
      int bad = r0!=r1 || (r0==1 && memcmp(a,b,sizeof a)!=0);
      if(bad){ if(diffs<5) printf("DIFF [%s]@%zu base=%d(%td,%td) twin=%d(%td,%td)\n",line,f,r0,a[0][0],a[0][1],r1,b[0][0],b[0][1]); diffs++; }
    }}
  printf("cases=%ld matches=%ld diffs=%ld\n",cases,matches,diffs); return diffs!=0; }
