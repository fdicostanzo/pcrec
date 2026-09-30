#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <string.h>
/* lb PATTERN...: per pattern, PCRE2_INFO_MAXLOOKBEHIND and the measured
   step-back: subject "\xff" + 10 x 'z', PCRE2_UTF (checking ON); the largest
   startoffset that still returns a UTF error is the step-back in chars. */
int main(int argc,char**argv){
  unsigned char s[16]; s[0]=0xff; memset(s+1,'z',10); size_t n=11;
  for(int i=1;i<argc;i++){
    int err; PCRE2_SIZE eo;
    pcre2_code*re=pcre2_compile((PCRE2_SPTR)argv[i],PCRE2_ZERO_TERMINATED,PCRE2_UTF,&err,&eo,NULL);
    if(!re){unsigned char b[120];pcre2_get_error_message(err,b,sizeof b);printf("%-40s compile error: %s\n",argv[i],b);continue;}
    uint32_t mlb=0; pcre2_pattern_info(re,PCRE2_INFO_MAXLOOKBEHIND,&mlb);
    pcre2_match_data*md=pcre2_match_data_create_from_pattern(re,NULL);
    int smax=-1;
    for(size_t st=0;st<=n;st++){int rc=pcre2_match(re,s,n,st,0,md,NULL); if(rc<=PCRE2_ERROR_UTF8_ERR1&&rc>=PCRE2_ERROR_UTF8_ERR21) smax=(int)st;}
    printf("%-40s INFO_MAXLOOKBEHIND=%u measured_stepback=%d\n",argv[i],mlb,smax);
    pcre2_match_data_free(md); pcre2_code_free(re);}
  return 0;}
