#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <string.h>
static int unesc(const char*s, unsigned char*o){int n=0;while(*s){if(s[0]=='\\'&&s[1]=='x'){unsigned v;sscanf(s+2,"%2x",&v);o[n++]=v;s+=4;}else o[n++]=*s++;}return n;}
/* usage: pr1 PATTERN SUBJ... ; prints rxt m/n lines */
int main(int argc,char**argv){
  int err; PCRE2_SIZE eo;
  pcre2_code*re=pcre2_compile((PCRE2_SPTR)argv[1],PCRE2_ZERO_TERMINATED,PCRE2_UTF|PCRE2_MATCH_INVALID_UTF,&err,&eo,NULL);
  if(!re){printf("compile err %d\n",err);return 1;}
  pcre2_match_data*md=pcre2_match_data_create_from_pattern(re,NULL);
  for(int i=2;i<argc;i++){
    unsigned char subj[256]; int n=unesc(argv[i],subj);
    int rc=pcre2_match(re,subj,n,0,0,md,NULL);
    if(rc<0) printf("n \"%s\"\n",argv[i]);
    else {PCRE2_SIZE*o=pcre2_get_ovector_pointer(md); printf("m \"%s\" %zu %zu\n",argv[i],o[0],o[1]);}
  }
  return 0;}
