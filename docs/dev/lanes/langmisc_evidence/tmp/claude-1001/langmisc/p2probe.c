/* libpcre2 oracle: p2probe OPTS PATHEX [startpos:SUBJHEX ...]
   OPTS letters: u=UTF i=CASELESS p=UCP m=MULTILINE s=DOTALL x=EXTENDED n=NO_AUTO_CAPTURE U=UNGREEDY J=DUPNAMES I=MATCH_INVALID_UTF(match) */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned char *unhex(const char *h, size_t *n){size_t l=strlen(h)/2;unsigned char*b=malloc(l+1);for(size_t i=0;i<l;i++){unsigned v;sscanf(h+2*i,"%2x",&v);b[i]=v;}b[l]=0;*n=l;return b;}
int main(int argc,char**argv){
  uint32_t o=0; const char*f=argv[1];
  if(strchr(f,'u'))o|=PCRE2_UTF|PCRE2_MATCH_INVALID_UTF; if(strchr(f,'i'))o|=PCRE2_CASELESS; if(strchr(f,'p'))o|=PCRE2_UCP;
  if(strchr(f,'m'))o|=PCRE2_MULTILINE; if(strchr(f,'s'))o|=PCRE2_DOTALL; if(strchr(f,'x'))o|=PCRE2_EXTENDED;
  if(strchr(f,'U'))o|=PCRE2_UNGREEDY; if(strchr(f,'J'))o|=PCRE2_DUPNAMES;
  size_t pl; unsigned char*p=unhex(argv[2],&pl); int en; PCRE2_SIZE eo;
  pcre2_code*re=pcre2_compile(p,pl,o,&en,&eo,NULL);
  if(!re){PCRE2_UCHAR m[256];pcre2_get_error_message(en,m,256);printf("ERR %d %zu %s\n",en,(size_t)eo,m);return 0;}
  uint32_t cc; pcre2_pattern_info(re,PCRE2_INFO_CAPTURECOUNT,&cc); printf("OK %u\n",cc);
  pcre2_match_data*md=pcre2_match_data_create_from_pattern(re,NULL);
  for(int a=3;a<argc;a++){char*c=strchr(argv[a],':');size_t sp=strtoul(argv[a],0,10);size_t sl;unsigned char*s=unhex(c+1,&sl);
    int rc=pcre2_match(re,s,sl,sp,0,md,NULL);
    if(rc==PCRE2_ERROR_NOMATCH){printf("N\n");continue;}
    if(rc<0){printf("E %d\n",rc);continue;}
    PCRE2_SIZE*ov=pcre2_get_ovector_pointer(md);printf("M");
    for(uint32_t g=0;g<=cc;g++){ if((int)g<rc && ov[2*g]!=PCRE2_UNSET) printf(" %zu %zu",(size_t)ov[2*g],(size_t)ov[2*g+1]); else printf(" -1 -1");}
    printf("\n");}
  return 0;}
