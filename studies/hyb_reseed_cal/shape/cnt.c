#include <stdio.h>
#include <stddef.h>
#include <string.h>
#include <stdlib.h>
extern unsigned long n_att, n_seed, n_fail;
extern int rx_search(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
int main(int argc, char **argv) {
  int fa = argv[1][0]=='f'; unsigned long calls=0, reach=0, bytes=0;
  for (int i = 2; i < argc; i++) {
    FILE *f = fopen(argv[i], "rb"); static unsigned char b[1<<21]; size_t n = fread(b,1,sizeof b,f); fclose(f); bytes+=n;
    size_t pos = 0; ptrdiff_t c[1][2];
    for (;;) { unsigned long a0=n_att; calls++; int k = rx_search(b, n, pos, c); if (n_att>a0) reach++;
      if (k != 1 || !fa) break; pos = c[0][1] > c[0][0] ? (size_t)c[0][1] : (size_t)c[0][0]+1; if (pos>n) break; }
  }
  printf("calls=%lu reach_vm=%lu attempts=%lu failed=%lu reseeds=%lu bytes=%lu\n", calls, reach, n_att, n_fail, n_seed, bytes);
}
