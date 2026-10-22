/* pcrec driver: links with a generated rx.c; args startpos:SUBJHEX ... */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include RXH
static unsigned char *unhex(const char *h, size_t *n){size_t l=strlen(h)/2;unsigned char*b=malloc(l+1);for(size_t i=0;i<l;i++){unsigned v;sscanf(h+2*i,"%2x",&v);b[i]=v;}b[l]=0;*n=l;return b;}
int main(int argc,char**argv){
  printf("OK %d\n",RX_NCAPS-1);
  for(int a=1;a<argc;a++){char*c=strchr(argv[a],':');size_t sp=strtoul(argv[a],0,10);size_t sl;unsigned char*s=unhex(c+1,&sl);
    ptrdiff_t caps[RX_NCAPS][2]; for(int g=0;g<RX_NCAPS;g++)caps[g][0]=caps[g][1]=-7;
    int rc=rx_search(s,sl,sp,caps);
    if(rc==0){printf("N\n");continue;}
    if(rc!=1){printf("E %d\n",rc);continue;}
    printf("M");for(int g=0;g<RX_NCAPS;g++)printf(" %td %td",caps[g][0],caps[g][1]);printf("\n");}
  return 0;}
