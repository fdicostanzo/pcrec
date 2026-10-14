/* r17b2 scratch harness: the new mf_set_terms vs the OLD search (174f3e320)
 * with the budget lifted to CAP, over sets read as 64 hex digits per line
 * (set[0] first). Prints one line per set. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "kit.h"
extern unsigned old_budget;
int old_set_terms(const uint8_t set[32], unsigned K, mf_cover *out);
static double now(void){ struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec+t.tv_nsec*1e-9; }
static void pc(const mf_cover *c, int ok, char *o){
    if(!ok){ strcpy(o,"-"); return; }
    o += sprintf(o, "%c", c->complement?'C':'D');
    for(unsigned i=0;i<c->n;i++) o += sprintf(o, ",%c%02x.%02x", c->t[i].kind?'A':'Q', c->t[i].a, c->t[i].b);
}
int main(int argc, char **argv){
    unsigned cap = argc > 1 ? (unsigned)strtoul(argv[1],0,10) : 0;  /* 0: no old run */
    static char line[1 << 20];
    while (fgets(line, sizeof line, stdin)) {
        uint8_t s[32];
        if (strlen(line) < 64) continue;
        for (int i=0;i<32;i++){ unsigned v; sscanf(line+2*i, "%2x", &v); s[i]=(uint8_t)v; }
        mf_cover a, b; char ca[128], cb[128];
        double t0=now(); int oka = pcrec_mf_set_terms(s, 4, &a); double t1=now();
        pc(&a, oka, ca);
        char tag[128] = "-"; if (strlen(line) > 65) { sscanf(line + 65, "%127s", tag); }
        line[64]=0;
        if (!cap) { printf("%s new %d %u %.3f %s %s\n", line, oka, a.nodes, (t1-t0)*1e3, ca, tag); continue; }
        old_budget = cap;
        double t2=now(); int okb = old_set_terms(s, 4, &b); double t3=now();
        int ab = !okb && b.nodes > cap;
        pc(&b, okb, cb);
        const char *v = ab ? "REF-INCOMPLETE" : (oka==okb && (!oka || !strcmp(ca,cb))) ? "SAME"
                      : (a.nodes > MF_SET_BUDGET) ? "NEW-BUDGET-DECLINE" : "DIFF";
        printf("%s %s new %d %u %.3f %s old %d %u %.3f %s %s\n", line, v, oka, a.nodes, (t1-t0)*1e3, ca, okb, b.nodes, (t3-t2)*1e3, cb, tag); fflush(stdout);
    }
    return 0;
}
