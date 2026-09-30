#include ART_H
#include <stdio.h>
#include <stdlib.h>
static int unhex(const char *h, unsigned char *o){int n=0;while(h[0]&&h[1]){unsigned v;sscanf(h,"%2x",&v);o[n++]=v;h+=2;}return n;}
int main(int argc,char**argv){
  for(int a=1;a<argc;a++){unsigned char s[256];int n=unhex(argv[a],s);s[n]=0x80;
    for(int f=0;f<=n;f++){
      ptrdiff_t c[16][2]={{-9,-9}};
      int r=rx_search(s,n,f,c);
      printf("%d\t%d\tpsearch\t",a-1,f);
      if(r==1)printf("%td,%td\n",c[0][0],c[0][1]);else if(r==0)printf("nomatch\n");else if(r==PCREC_ERR_STARTPOS)printf("REFUSED\n");else printf("err%d\n",r);
      rx_ctx x={0};x.subject=s;x.len=n;x.pos=f;
      ptrdiff_t m=rx_match(&x);
      printf("%d\t%d\tpmatch\t",a-1,f);
      if(m>=0)printf("%d,%td\n",f,m);else if(m==-1)printf("nomatch\n");else if(m==PCREC_ERR_STARTPOS)printf("REFUSED\n");else printf("err%td\n",m);}}
  return 0;}
