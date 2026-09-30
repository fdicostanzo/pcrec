#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <string.h>
#include "enum.h"
int main(int argc,char**argv){int err;PCRE2_SIZE eo;
  pcre2_code*re=pcre2_compile((PCRE2_SPTR)argv[1],PCRE2_ZERO_TERMINATED,PCRE2_UTF|PCRE2_MATCH_INVALID_UTF,&err,&eo,NULL);
  pcre2_match_data*md=pcre2_match_data_create(8,NULL);
  FOREACH_SUBJ(
    char out[512],*o=out;*o=0;size_t p=0;
    while(p<=(size_t)n){int rc=pcre2_match(re,s,n,p,0,md,NULL);if(rc<0)break;PCRE2_SIZE*v=pcre2_get_ovector_pointer(md);
      o+=sprintf(o,"(%zu,%zu)",v[0],v[1]);
      if(v[1]>v[0])p=v[1];else{p=v[0]+1;while(p<(size_t)n&&(s[p]&0xC0)==0x80)p++;}}
    for(int i=0;i<n;i++)printf("%02x",s[i]);printf("\t%s\n",out);)
  return 0;}
