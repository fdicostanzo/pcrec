/* cdrv SUBJFILE [NF NT] : print rc and every capture span; NF/NT given = _in arm with those caps, else default arm */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include HDR
int main(int argc,char**argv){
  FILE*f=fopen(argv[1],"rb"); if(!f) return 2; fseek(f,0,SEEK_END); size_t n=ftell(f); fseek(f,0,SEEK_SET);
  unsigned char*s=malloc(n+1); if(fread(s,1,n,f)!=n) return 2; fclose(f);
  ptrdiff_t caps[PFX_NCAPS][2]; int rc;
  if(argc>3){ size_t nf=strtoul(argv[2],0,10), nt=strtoul(argv[3],0,10);
    void*F=malloc(nf*PFX_RESUME_FRAME_SIZE+1),*T=malloc(nt*PFX_TRAIL_FRAME_SIZE+1); PFX_buffers bu={F,nf,T,nt};
    rc=PFX_search_in(s,n,0,caps,&bu);
  } else rc=PFX_search(s,n,0,caps);
  printf("rc=%d",rc); if(rc>0) for(int g=0;g<PFX_NCAPS;g++) printf(" %td,%td",caps[g][0],caps[g][1]); printf("\n"); return 0;}
