#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int unhex(const char *h, unsigned char *o){int n=0;while(h[0]&&h[1]){unsigned v;sscanf(h,"%2x",&v);o[n++]=v;h+=2;}return n;}
/* pr PATTERN HEX... : every (subject, startoffset) x {U,I,UA,IA} */
int main(int argc,char**argv){
  int err; PCRE2_SIZE eo; pcre2_code *re[2];
  re[0]=pcre2_compile((PCRE2_SPTR)argv[1],PCRE2_ZERO_TERMINATED,PCRE2_UTF,&err,&eo,NULL);
  re[1]=pcre2_compile((PCRE2_SPTR)argv[1],PCRE2_ZERO_TERMINATED,PCRE2_UTF|PCRE2_MATCH_INVALID_UTF,&err,&eo,NULL);
  if(!re[0]||!re[1]){printf("COMPILE-FAIL\n");return 1;}
  pcre2_match_data*md=pcre2_match_data_create(8,NULL);
  const char*arm[4]={"U","I","UA","IA"};
  for(int a=2;a<argc;a++){unsigned char s[256];int n=unhex(argv[a],s);
    for(int f=0;f<=n;f++)for(int k=0;k<4;k++){
      int rc=pcre2_match(re[k&1],s,n,f,(k>>1)?PCRE2_ANCHORED:0,md,NULL);
      if(rc>=0){PCRE2_SIZE*o=pcre2_get_ovector_pointer(md);printf("%d\t%d\t%s\t%zu,%zu\n",a-2,f,arm[k],o[0],o[1]);}
      else if(rc==PCRE2_ERROR_NOMATCH)printf("%d\t%d\t%s\tnomatch\n",a-2,f,arm[k]);
      else printf("%d\t%d\t%s\terr%d\n",a-2,f,arm[k],rc);}}
  return 0;}
