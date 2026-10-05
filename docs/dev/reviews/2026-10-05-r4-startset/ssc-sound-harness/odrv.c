/* differential: pcrec artifact (rx) vs local libpcre2 (10.48, NOT the reference), every startpos */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stddef.h>
#include "rx.h"
static size_t unesc(const char*in, unsigned char*out){size_t n=0;for(const char*p=in;*p;){if(p[0]=='\\'&&p[1]=='x'){unsigned v;sscanf(p+2,"%2x",&v);out[n++]=v;p+=4;}else out[n++]=(unsigned char)*p++;}return n;}
int main(int argc,char**argv){ const char*pat=argv[1]; int utf=argc>2&&!strncmp(argv[2],"utf8",4); int ucp=argc>2&&strstr(argv[2],"ucp")!=NULL;
  uint32_t opt=(utf?(PCRE2_UTF|PCRE2_MATCH_INVALID_UTF):0)|(ucp?PCRE2_UCP:0); int en; PCRE2_SIZE eo;
  pcre2_code*re=pcre2_compile((PCRE2_SPTR)pat,PCRE2_ZERO_TERMINATED,opt,&en,&eo,NULL);
  if(!re){printf("pcre2 compile fail %d\n",en);return 2;}
  pcre2_match_data*md=pcre2_match_data_create_from_pattern(re,NULL);
  char line[4096]; unsigned char s[4096]; long cases=0,diffs=0,m=0;
  while(fgets(line,sizeof line,stdin)){ size_t L=strlen(line); if(L&&line[L-1]=='\n') line[--L]=0; size_t n=unesc(line,s);
    for(size_t f=0;f<=n;f++){ ptrdiff_t c[RX_NCAPS][2]; memset(c,0xff,sizeof c);
      int r=rx_search(s,n,f,c); int pr=pcre2_match(re,s,n,f,0,md,NULL); PCRE2_SIZE*ov=pcre2_get_ovector_pointer(md);
      int pm = pr>0; cases++; if(pm) m++;
      if((pr<0 && pr!=PCRE2_ERROR_NOMATCH) || r==-7){ continue; } /* e.g. bad offset in utf */
      int bad = (r==1)!=pm || (pm && (c[0][0]!=(ptrdiff_t)ov[0]||c[0][1]!=(ptrdiff_t)ov[1]));
      if(bad){ if(diffs<6) printf("DIFF [%s]@%zu pcrec=%d(%td,%td) pcre2=%d(%zd,%zd)\n",line,f,r,c[0][0],c[0][1],pr,pm?(ssize_t)ov[0]:-1,pm?(ssize_t)ov[1]:-1); diffs++; } }}
  printf("cases=%ld pcre2matches=%ld diffs=%ld\n",cases,m,diffs); return 0; }
