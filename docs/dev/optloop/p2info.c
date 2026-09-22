#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc,char**argv){
  (void)argc;
  FILE*f=fopen(argv[1],"rb"); if(!f)return 2;
  static unsigned char buf[1<<20];
  size_t n=fread(buf,1,sizeof buf,f); fclose(f);
  int e; PCRE2_SIZE eo;
  pcre2_code*c=pcre2_compile(buf,n,0,&e,&eo,NULL);
  if(!c){ PCRE2_UCHAR m[256]; pcre2_get_error_message(e,m,sizeof m);
          printf("ERR\t%s\n",(char*)m); return 0; }
  uint32_t fct=0,fcu=0,lct=0,lcu=0,anch=0; PCRE2_SIZE ml=0;
  unsigned char*bm=NULL;
  pcre2_pattern_info(c,PCRE2_INFO_FIRSTCODETYPE,&fct);
  pcre2_pattern_info(c,PCRE2_INFO_FIRSTCODEUNIT,&fcu);
  pcre2_pattern_info(c,PCRE2_INFO_LASTCODETYPE,&lct);
  pcre2_pattern_info(c,PCRE2_INFO_LASTCODEUNIT,&lcu);
  pcre2_pattern_info(c,PCRE2_INFO_MINLENGTH,&ml);
  pcre2_pattern_info(c,PCRE2_INFO_FIRSTBITMAP,&bm);
  int bits=0; if(bm) for(int i=0;i<256;i++) if(bm[i>>3]&(1u<<(i&7))) bits++;
  printf("OK\tfirstcodetype=%u\tfirstcodeunit=%u\tlastcodetype=%u\tlastcodeunit=%u\tminlength=%lu\tbitmapbits=%d\n",
         fct,fcu,lct,lcu,(unsigned long)ml,bm?bits:-1);
  return 0;
}
