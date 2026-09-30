/* [FORM-CHAR2] timing driver: ONE binary per (witness, arm), linked against a
 * generated artifact WITHOUT --emit-main (prefix rx, header via -DHDR).
 *   usage: drv MODE SUBJECTFILE [MIN_SECONDS]
 *   MODE = search   one rx_search(s,n,0) per call (a no-match subject scans it all)
 *          findall  spec find-all loop over the whole subject (bench "thr")
 *          match    rx_match at pos 0 on a short subject (bench "match")
 * prints: ns_per_char  answer_checksum  work_chars   (one line)
 * ns/char = ns per call / chars examined (search: match end if hit else n). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <time.h>
#include HDR
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+1e-9*t.tv_nsec;}
static volatile unsigned long long sink;
int main(int argc,char**argv){
  if(argc<3){fprintf(stderr,"usage: drv MODE FILE [SEC]\n");return 2;}
  const char*mode=argv[1]; double minsec=argc>3?atof(argv[3]):0.15;
  FILE*f=fopen(argv[2],"rb"); if(!f){perror("open");return 2;}
  fseek(f,0,SEEK_END); long nl=ftell(f); fseek(f,0,SEEK_SET);
  unsigned char*s=malloc(nl+1); if(fread(s,1,nl,f)!=(size_t)nl)return 2; fclose(f);
  size_t n=(size_t)nl; ptrdiff_t caps[64][2]; unsigned long long ck=0; double work=0;
  long reps=1; double el=0;
  for(;;){
    ck=0; work=0; double t0=now();
    for(long r=0;r<reps;r++){
      ck=0;
      if(!strcmp(mode,"search")){
        int rc=rx_search(s,n,0,caps);
        ck=ck*1000003ULL+(unsigned long long)(rc+3)+(rc>0?(unsigned long long)(caps[0][0]+1)*7919ULL+(unsigned long long)(caps[0][1]+1):0);
        work+=(rc>0?(double)caps[0][1]:(double)n);
      } else if(!strcmp(mode,"findall")){
        for(size_t from=0;from<=n;){
          int rc=rx_search(s,n,from,caps); if(rc<=0)break;
          ck=ck*1000003ULL+(unsigned long long)(caps[0][0]+1)+(unsigned long long)(caps[0][1]+1)*7919ULL;
          from=(size_t)caps[0][1]>from?(size_t)caps[0][1]:from+1;
        }
        work+=(double)n;
      } else { /* match */
        rx_ctx c; memset(&c,0,sizeof c); c.subject=s; c.len=n; c.pos=0;
        ptrdiff_t m=rx_match(&c); ck=ck*1000003ULL+(unsigned long long)(m+9); work+=(double)n;
      }
    }
    el=now()-t0; sink=ck;
    if(el>=minsec)break;
    reps*= (el<minsec/20)?16:2;
  }
  printf("%.6f %llu %.0f\n", el*1e9/work, ck, work/reps);
  return 0;
}
