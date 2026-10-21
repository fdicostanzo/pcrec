/* tests/memfn/proof_meta.h — [MEMFN] R-26 (lane r26z1): the site descriptions
 * the proof family's generator (proof_check.c) writes and its oracle driver
 * (proof_run.c) reads. DATA ONLY: the terms each site was GENERATED with, and
 * the class the kit returned for it (the claim under test). It includes no
 * kit header, so the driver's oracle reads G2's own facts, never the kit's
 * text (memfn/CLAUDE.md, "Independent control").
 */
#ifndef PROOF_META_H
#define PROOF_META_H

#define PM_MAXT  6      /* terms per predicate in the generated space          */
#define PM_MAXP  3      /* span 0 (or a context stop) and up to two ctx items  */
#define PM_NPROOF 41    /* MF_MAX_FWD - MF_PROOF_LO, checked by the generator  */
#define PM_PROOF_LO (-8)

enum { PM_SET = 0, PM_RUN = 1 };
enum { PM_REQ = 1, PM_OPT = 2 };
enum { PM_SAT = 1, PM_FAILS = 2 };

typedef struct {
    int kind;                   /* PM_SET / PM_RUN                           */
    int off;                    /* from the candidate                        */
    int len;                    /* 1 for a SET term                          */
    unsigned char set[32];      /* PM_SET                                    */
    unsigned char run[8];       /* PM_RUN, exact                             */
    int need;
} pm_term;

typedef struct {
    int nterm;
    pm_term t[PM_MAXT];
    int need;
    int context;                /* 1: a CONTEXT predicate (absent read)       */
    int absent;                 /* PM_SAT / PM_FAILS where context           */
} pm_pred;

typedef struct {
    const char *name;
    int stop;                   /* a context stop: range [lo, n]             */
    int npred;                  /* p[0] the site's pred, p[1..] its ctx      */
    pm_pred p[PM_MAXP];
    unsigned char proven[PM_NPROOF][32];   /* the kit's class (the claim)    */
    unsigned char alpha[8];     /* the subject alphabet                      */
    int nalpha;
} pm_site;

typedef unsigned long (*pm_fn)(const unsigned char *subject, unsigned long n,
                               unsigned long pos);

#endif /* PROOF_META_H */
