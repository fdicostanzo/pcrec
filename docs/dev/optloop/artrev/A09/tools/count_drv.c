#include <stdio.h>
#include <stdlib.h>
#include "artifact.c"
int main(int argc,char**argv){
 for(int i=1;i<argc;i++){
  FILE*f=fopen(argv[i],"rb");fseek(f,0,2);long n=ftell(f);rewind(f);unsigned char*s=malloc(n+1);fread(s,1,n,f);fclose(f);
  C_calls=C_skip0=C_skip406=C_fstep=C_rskip=C_rstep=C_pf=C_vm=C_vmfail=C_vmpos=C_memchr=C_cand=0;
  size_t pos=0; ptrdiff_t caps[1][2]; long m=0;
  for(;;){int rc=rx_search(s,n,pos,caps); if(rc!=1)break; m++; pos=caps[0][1]; if(caps[0][1]==caps[0][0])pos++; if(pos>(size_t)n)break;}
  double k=1048576.0/n;
  printf("%-20s m=%4ld memchr=%.0f cand=%.0f skip406=%.0f fstep=%.0f rskip=%.0f rstep=%.0f vm=%.0f vmpos=%.0f /MiB\n",strrchr(argv[i],'/')+1,m,C_memchr*k,C_cand*k,C_skip406*k,C_fstep*k,C_rskip*k,C_rstep*k,C_vm*k,C_vmpos*k);
 }}
