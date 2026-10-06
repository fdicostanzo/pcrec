#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
int pf_orig(const unsigned char*,size_t,size_t,ptrdiff_t(*)[2]);
int pf_twin(const unsigned char*,size_t,size_t,ptrdiff_t(*)[2]);
int main(int argc,char**argv){
 long bad=0,tot=0,hits=0;
 for(int i=1;i<argc;i++){
  FILE*f=fopen(argv[i],"rb");fseek(f,0,2);long n=ftell(f);rewind(f);unsigned char*s=malloc(n?n:1);fread(s,1,n,f);fclose(f);
  long step = n > 20000 ? 7 : 1;
  for(long from=0; from<=n; from+=step){
    ptrdiff_t a[1][2]={{-9,-9}},b[1][2]={{-9,-9}};
    int ra=pf_orig(s,n,from,a), rb=pf_twin(s,n,from,b); tot++; if(ra==1)hits++;
    if(ra!=rb || (ra==1 && a[0][0]!=b[0][0])){ if(bad<5) printf("DIFF %s from=%ld orig=%d[%td,%td] twin=%d[%td,%td]\n",argv[i],from,ra,a[0][0],a[0][1],rb,b[0][0],b[0][1]); bad++; }
  }
  free(s);
 }
 printf("prefilter windows compared=%ld (orig hits %ld) start-differences=%ld\n",tot,hits,bad); return bad!=0;
}
