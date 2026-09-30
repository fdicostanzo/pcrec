static const unsigned char ALPHA[7]={0x61,0x62,0x80,0xc3,0xa9,0xe3,0xff};
#define MAXLEN 5
/* iterate all strings over ALPHA of length 0..MAXLEN */
#define FOREACH_SUBJ(...) for(int L=0;L<=MAXLEN;L++){long tot=1;for(int i=0;i<L;i++)tot*=7;for(long c=0;c<tot;c++){unsigned char s[16];long x=c;for(int i=0;i<L;i++){s[i]=ALPHA[x%7];x/=7;}int n=L;s[n]=0x80;__VA_ARGS__}}
