#include <stdio.h>
#include <string.h>
#include <stddef.h>
#include HDR
int main(int argc,char**argv){
  for(int i=1;i<argc;i++){
    ptrdiff_t caps[RX_NCAPS][2];
    for(int g=0;g<RX_NCAPS;g++)caps[g][0]=caps[g][1]=-9;
    int rc=rx_search((const unsigned char*)argv[i],strlen(argv[i]),0,caps);
    printf("%s => rc=%d",argv[i],rc);
    if(rc==1) for(int g=0;g<RX_NCAPS;g++) printf(" %d:%td,%td",g,caps[g][0],caps[g][1]);
    printf("\n");
  }
  return 0;
}
