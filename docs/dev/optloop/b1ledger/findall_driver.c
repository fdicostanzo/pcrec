#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "art.h"
int main(int argc,char**argv){
  FILE*f=fopen(argv[1],"rb"); if(!f)return 2;
  fseek(f,0,SEEK_END); long n=ftell(f); fseek(f,0,SEEK_SET);
  unsigned char*b=malloc(n); if(fread(b,1,n,f)!=(size_t)n)return 2; fclose(f);
  ptrdiff_t caps[RX_NCAPS][2];
  size_t pos=0; long cnt=0;
  for(;;){ int r=rx_search(b,(size_t)n,pos,caps); if(r!=1)break;
    size_t s=(size_t)caps[0][0],e=(size_t)caps[0][1];
    printf("%zu %zu\n",s,e); cnt++;
    pos=(e>s)?e:s+1; if(pos>(size_t)n)break; if(cnt>4000000)break; }
  fprintf(stderr,"matches=%ld\n",cnt); return 0;
}
