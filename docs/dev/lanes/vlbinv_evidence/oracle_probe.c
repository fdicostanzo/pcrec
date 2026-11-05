/* lane vlbinv scratch oracle: libpcre2-8 10.46 as a LIBRARY.
   stdin lines: PATTERN            (compile mode, argv[1]=c)
                PATTERN<TAB>SUBJ   (match mode, argv[1]=m; subject \xHH-free, literal)
   argv[2]=u for UTF. Output: accept/reject + maxlookbehind; or every match (global) with all groups. */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <string.h>
int main(int argc,char**argv){char line[8192];int m=argc>1&&argv[1][0]=='m';uint32_t opt=(argc>2&&argv[2][0]=='u')?PCRE2_UTF:0;
while(fgets(line,sizeof line,stdin)){size_t n=strlen(line);if(n&&line[n-1]=='\n')line[--n]=0;
 char*subj=NULL; if(m){char*t=strchr(line,'\t'); if(!t)continue; *t=0; subj=t+1; n=strlen(line);}
 int e;PCRE2_SIZE eo;pcre2_code*c=pcre2_compile((PCRE2_SPTR)line,n,opt,&e,&eo,NULL);
 if(!c){PCRE2_UCHAR b[256];pcre2_get_error_message(e,b,256);printf("%s\tREJECT\t%d at %zu: %s\n",line,e,(size_t)eo,b);continue;}
 if(!m){uint32_t mlb=0,cap=0;pcre2_pattern_info(c,PCRE2_INFO_MAXLOOKBEHIND,&mlb);pcre2_pattern_info(c,PCRE2_INFO_CAPTURECOUNT,&cap);
   printf("%s\tACCEPT\tmaxlookbehind=%u caps=%u\n",line,mlb,cap);}
 else { size_t sl=strlen(subj); pcre2_match_data*md=pcre2_match_data_create_from_pattern(c,NULL);
   printf("%s\t%s\t",line,subj); size_t start=0; int any=0;
   while(start<=sl){int rc=pcre2_match(c,(PCRE2_SPTR)subj,sl,start,0,md,NULL);
     if(rc<0){ if(rc!=PCRE2_ERROR_NOMATCH) printf("ERR%d",rc); break;}
     PCRE2_SIZE*ov=pcre2_get_ovector_pointer(md); any=1; printf("[");
     for(int i=0;i<rc;i++){ if(ov[2*i]==PCRE2_UNSET)printf("%s-",i?",":""); else printf("%s%zu-%zu",i?",":"",(size_t)ov[2*i],(size_t)ov[2*i+1]);}
     printf("]"); size_t ns = ov[1]>ov[0]?ov[1]:ov[1]+1; if(ov[1]<ov[0]) ns=start+1; start=ns; }
   if(!any)printf("nomatch"); printf("\n"); pcre2_match_data_free(md);}
 pcre2_code_free(c);}return 0;}
