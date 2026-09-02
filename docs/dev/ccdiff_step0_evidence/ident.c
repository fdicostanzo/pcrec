/* ccdiff answer-identity dump: every span the artifact reports, all regimes. */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <dlfcn.h>
struct rx_ctx_min { const unsigned char *s; size_t len; size_t pos; size_t ncap; const ptrdiff_t (*caps)[2]; void *user; };
int main(int argc,char**argv){
  void*h=dlopen(argv[1],RTLD_NOW); if(!h){fprintf(stderr,"%s\n",dlerror());return 2;}
  int(*sea)(const unsigned char*,size_t,size_t,ptrdiff_t(*)[2])=dlsym(h,"rx_search");
  long long(*mca)(const void*,ptrdiff_t(*)[2])=dlsym(h,"rx_match_caps");
  const struct{int n;}*ncp=dlsym(h,"rx_info"); (void)ncp;
  FILE*f=fopen(argv[2],"rb"); fseek(f,0,SEEK_END); long n=ftell(f); rewind(f);
  unsigned char*b=malloc(n+1); if(fread(b,1,n,f)!=(size_t)n)return 3; fclose(f);
  ptrdiff_t(*caps)[2]=calloc(256,sizeof *caps);
  const char*R=argv[3];
  if(!strcmp(R,"match")){ struct rx_ctx_min c={b,(size_t)n,0,0,NULL,NULL};
    long long r=mca(&c,caps); printf("m %lld",r);
    if(r>=0) for(int g=0;g<8;g++) printf(" %td:%td",caps[g][0],caps[g][1]);
    printf("\n"); }
  else if(!strcmp(R,"findall")){ size_t pos=0; long cnt=0;
    for(;;){ int r=sea(b,(size_t)n,pos,caps); if(r==0)break; if(r<0){printf("E %d\n",r);break;}
      printf("s %td %td\n",caps[0][0],caps[0][1]); cnt++;
      size_t e=(size_t)caps[0][1]; pos=(e>pos)?e:pos+1; if(pos>(size_t)n)break; }
    printf("n %ld\n",cnt); }
  else { int r=sea(b,(size_t)n,0,caps); printf("r %d",r);
    if(r==1) for(int g=0;g<8;g++) printf(" %td:%td",caps[g][0],caps[g][1]);
    printf("\n"); }
  return 0; }
