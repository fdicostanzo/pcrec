#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stddef.h>
/* usage: p2 PATTERN FLAGS(u=utf,i=caseless,x=..) subj... */
int main(int argc,char**argv){
  uint32_t opt=0; for(char*f=argv[2];*f;f++){ if(*f=='u')opt|=PCRE2_UTF; if(*f=='i')opt|=PCRE2_CASELESS; if(*f=='s')opt|=PCRE2_DOTALL; if(*f=='m')opt|=PCRE2_MULTILINE;}
  int en; PCRE2_SIZE eo;
  pcre2_code*re=pcre2_compile((PCRE2_SPTR)argv[1],PCRE2_ZERO_TERMINATED,opt,&en,&eo,NULL);
  if(!re){printf("compile error %d at %zu\n",en,eo);return 1;}
  uint32_t nc; pcre2_pattern_info(re,PCRE2_INFO_CAPTURECOUNT,&nc);
  pcre2_match_data*md=pcre2_match_data_create_from_pattern(re,NULL);
  for(int i=3;i<argc;i++){
    int rc=pcre2_match(re,(PCRE2_SPTR)argv[i],strlen(argv[i]),0,0,md,NULL);
    printf("%s => rc=%d",argv[i],rc>0?1:rc);
    if(rc>0){PCRE2_SIZE*ov=pcre2_get_ovector_pointer(md);
      for(uint32_t g=0;g<=nc;g++) printf(" %u:%td,%td",g,ov[2*g]==PCRE2_UNSET?(ptrdiff_t)-1:(ptrdiff_t)ov[2*g],ov[2*g+1]==PCRE2_UNSET?(ptrdiff_t)-1:(ptrdiff_t)ov[2*g+1]);}
    printf("\n");
  }
  return 0;
}
