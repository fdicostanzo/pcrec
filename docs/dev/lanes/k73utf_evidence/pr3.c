#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <string.h>
static int unesc(const char*s, unsigned char*o){int n=0;while(*s){if(s[0]=='\\'&&s[1]=='x'){unsigned v;sscanf(s+2,"%2x",&v);o[n++]=v;s+=4;}else o[n++]=*s++;}return n;}
/* pr3 PATTERN SUBJ : pcrec's find-all protocol (match_api 3.1) driven through libpcre2
   PCRE2_UTF|PCRE2_MATCH_INVALID_UTF: search from p; empty match -> p = start+1 then skip 0x80-0xBF */
int main(int argc,char**argv){
  int err; PCRE2_SIZE eo;
  pcre2_code*re=pcre2_compile((PCRE2_SPTR)argv[1],PCRE2_ZERO_TERMINATED,PCRE2_UTF|PCRE2_MATCH_INVALID_UTF,&err,&eo,NULL);
  pcre2_match_data*md=pcre2_match_data_create_from_pattern(re,NULL);
  unsigned char s[256]; int n=unesc(argv[2],s); size_t p=0; int count=0;
  while(p<=(size_t)n){int rc=pcre2_match(re,s,n,p,0,md,NULL); if(rc<0) break; PCRE2_SIZE*o=pcre2_get_ovector_pointer(md);
    printf("(%zu,%zu) ",o[0],o[1]); count++;
    if(o[1]>o[0]) p=o[1]; else {p=o[0]+1; while(p<(size_t)n&&(s[p]&0xC0)==0x80)p++;}}
  printf("count=%d\n",count); return 0;}
