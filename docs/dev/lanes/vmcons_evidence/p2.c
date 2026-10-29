#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <string.h>
int main(int argc,char**argv){int e;PCRE2_SIZE eo;pcre2_code*re=pcre2_compile((PCRE2_SPTR)argv[1],PCRE2_ZERO_TERMINATED,0,&e,&eo,0);
if(!re){printf("compile error %d\n",e);return 2;}pcre2_match_data*md=pcre2_match_data_create_from_pattern(re,0);
for(int i=2;i<argc;i++){int rc=pcre2_match(re,(PCRE2_SPTR)argv[i],strlen(argv[i]),0,0,md,0);printf("%s: ",argv[i]);
if(rc<0){printf("rc %d\n",rc);continue;}PCRE2_SIZE*ov=pcre2_get_ovector_pointer(md);uint32_t n=pcre2_get_ovector_count(md);
for(uint32_t g=0;g<n;g++){if(ov[2*g]==PCRE2_UNSET)printf("%u:-1,-1 ",g);else printf("%u:%zu,%zu ",g,ov[2*g],ov[2*g+1]);}printf("\n");}return 0;}
