#include ART_H
#include <stdio.h>
#include "enum.h"
static void run(const unsigned char*s,int n,int m1,char*out){
  size_t p=0; char*o=out; *o=0;
  while(p<=(size_t)n){ptrdiff_t c[16][2];int r=rx_search(s,n,p,c);if(r!=1)break;
    o+=sprintf(o,"(%td,%td)",c[0][0],c[0][1]);
    if(c[0][1]>c[0][0]) p=m1?rx_next_pos(s,n,(size_t)c[0][1]-1):(size_t)c[0][1];
    else p=rx_next_pos(s,n,(size_t)c[0][0]);}
}
int main(void){FOREACH_SUBJ(
  char a[512],b[512];run(s,n,0,a);run(s,n,1,b);
  for(int i=0;i<n;i++)printf("%02x",s[i]);printf("\t%s\t%s\n",a,b);)
  return 0;}
