#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
static int unesc(const char*s, unsigned char*o){int n=0;while(*s){if(s[0]=='\\'&&s[1]=='x'){unsigned v;sscanf(s+2,"%2x",&v);o[n++]=v;s+=4;}else o[n++]=*s++;}return n;}
/* pr4 PATTERN SUBJ START : PCRE2_UTF only (checking ON): rc, and for UTF errors pcre2_get_startchar */
int main(int argc,char**argv){
  int err; PCRE2_SIZE eo;
  pcre2_code*re=pcre2_compile((PCRE2_SPTR)argv[1],PCRE2_ZERO_TERMINATED,PCRE2_UTF,&err,&eo,NULL);
  if(!re){printf("compile err\n");return 1;}
  pcre2_match_data*md=pcre2_match_data_create_from_pattern(re,NULL);
  unsigned char s[256]; int n=unesc(argv[2],s); size_t st=strtoul(argv[3],0,10);
  int rc=pcre2_match(re,s,n,st,0,md,NULL);
  if(rc>=0){PCRE2_SIZE*o=pcre2_get_ovector_pointer(md);printf("[%s] \"%s\"@%zu: match (%zu,%zu)\n",argv[1],argv[2],st,o[0],o[1]);}
  else {unsigned char b[120]; pcre2_get_error_message(rc,b,sizeof b);
    printf("[%s] \"%s\"@%zu: rc=%d (%s) startchar=%zu\n",argv[1],argv[2],st,rc,b,(size_t)pcre2_get_startchar(md));}
  return 0;}
