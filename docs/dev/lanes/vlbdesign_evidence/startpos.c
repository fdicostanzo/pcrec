/* lane vlbdesign scratch: one match at a start offset. argv: pattern subject offset */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
int main(int c,char**v){int e;PCRE2_SIZE eo;pcre2_code*re=pcre2_compile((PCRE2_SPTR)v[1],PCRE2_ZERO_TERMINATED,0,&e,&eo,NULL);
if(!re){printf("REJECT %d\n",e);return 0;}pcre2_match_data*md=pcre2_match_data_create_from_pattern(re,NULL);
int rc=pcre2_match(re,(PCRE2_SPTR)v[2],strlen(v[2]),atoi(v[3]),0,md,NULL);
if(rc<0){printf("%s\t%s\tstart=%s\tnomatch\n",v[1],v[2],v[3]);return 0;}PCRE2_SIZE*o=pcre2_get_ovector_pointer(md);
printf("%s\t%s\tstart=%s\t[%zu-%zu]\n",v[1],v[2],v[3],(size_t)o[0],(size_t)o[1]);return 0;}
