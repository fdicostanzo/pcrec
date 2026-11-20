/* dhremeas driver: ms per rx_search over a synthetic subject, one launch = one line.
   usage: driver KIND REPS   KIND: dense (" @x" x to 1 MB) | tail (" @x" then "ab " to 1 MB) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stddef.h>
int rx_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2]);
static double now_ms(void){ struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec*1e3+t.tv_nsec/1e6; }
int main(int argc, char **argv){
    if (argc < 3) return 2;
    size_t N = 1u<<20; unsigned char *s = malloc(N);
    int tail = !strcmp(argv[1], "tail"); int reps = atoi(argv[2]);
    const char *a = " @x", *b = "ab ";
    for (size_t i = 0; i < N; i++) s[i] = tail ? (i < 3 ? a[i] : b[(i-3)%3]) : a[i%3];
    ptrdiff_t caps[16][2]; int rc = 0;
    for (int i = 0; i < 20; i++) rc = rx_search(s, N, 0, caps);   /* warm */
    double t0 = now_ms();
    for (int i = 0; i < reps; i++) rc = rx_search(s, N, 0, caps);
    double t1 = now_ms();
    printf("%.5f rc=%d\n", (t1-t0)/reps, rc);
    return 0;
}
