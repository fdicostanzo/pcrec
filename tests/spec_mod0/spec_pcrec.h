/* spec_pcrec.h — running the pcrec BINARY as a black box, and classifying
 * what it says. Shared by the checks that compare pcrec's verdict against
 * libpcre2's, rather than comparing two libpcre2 answers to each other.
 *
 * WHY IT EXISTS. check02, check07 and check11 each carry their own private
 * copy of a fork/exec-with-timeout helper, trimmed to what that check needed.
 * A fourth and fifth copy would be the shape this repo keeps paying for, so
 * the two checks added in the 2026-08-12 MOD-0.8b pass share this one. The
 * three older copies are deliberately NOT touched here: they are passing
 * checks owned by other work, and rewriting them to route through a new
 * header is a change to what they test, not a cleanup. (Noted in the pass's
 * report as a consolidation the main session may want.)
 *
 * WHAT IS DIFFERENT FROM THE OLDER COPIES: stdout is COUNTED, not discarded.
 * "never miscompile" is a claim about the C that comes out, and a refusal
 * that still emitted a partial translation unit would satisfy an exit-code
 * assertion while breaking the promise. The byte count is the cheapest
 * observation that distinguishes them.
 *
 * NO SHELL is involved anywhere: one argv element per pattern, so a pattern
 * containing quotes, backslashes, newlines or `$(` is passed through byte for
 * byte. (Every byte except NUL is reachable this way; NUL is not, and the
 * checks that sweep a byte space say so.)
 */

#ifndef PCREC_SPEC_MOD0_PCREC_H
#define PCREC_SPEC_MOD0_PCREC_H

#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#define SPEC_PCREC_TIMEOUT_MS 5000

typedef struct {
    int    ran;          /* fork+exec succeeded */
    int    timed_out;
    int    exit_code;
    long   out_bytes;    /* bytes pcrec wrote to STDOUT (generated C) */
    char   err[1024];    /* first 1023 bytes of stderr, NUL-terminated */
} SpecPcrecRun;

static inline SpecPcrecRun spec_pcrec_run(const char *path, char *const argv[])
{
    SpecPcrecRun r; memset(&r, 0, sizeof r);
    int op[2], ep[2];
    if (pipe(op) != 0) return r;
    if (pipe(ep) != 0) { close(op[0]); close(op[1]); return r; }
    pid_t pid = fork();
    if (pid < 0) { close(op[0]); close(op[1]); close(ep[0]); close(ep[1]); return r; }
    if (pid == 0) {
        close(op[0]); close(ep[0]);
        dup2(op[1], STDOUT_FILENO); close(op[1]);
        dup2(ep[1], STDERR_FILENO); close(ep[1]);
        execv(path, argv);
        _exit(127);
    }
    close(op[1]); close(ep[1]);
    for (int i = 0; i < 2; i++) {
        int fd = i ? ep[0] : op[0];
        int fl = fcntl(fd, F_GETFL, 0);
        fcntl(fd, F_SETFL, fl | O_NONBLOCK);
    }

    struct timespec deadline;
    clock_gettime(CLOCK_MONOTONIC, &deadline);
    deadline.tv_sec += SPEC_PCREC_TIMEOUT_MS / 1000;

    size_t te = 0;
    int status = 0, exited = 0;
    char sink[4096];
    for (;;) {
        if (waitpid(pid, &status, WNOHANG) == pid) exited = 1;
        ssize_t n;
        while ((n = read(op[0], sink, sizeof sink)) > 0) r.out_bytes += (long)n;
        while (te < sizeof r.err - 1 &&
               (n = read(ep[0], r.err + te, sizeof r.err - 1 - te)) > 0)
            te += (size_t)n;
        /* stderr past the buffer is drained so pcrec can never block on a
         * full pipe while this loop waits for it to exit. */
        if (te >= sizeof r.err - 1)
            while ((n = read(ep[0], sink, sizeof sink)) > 0) { }
        if (exited) break;
        struct timespec now;
        clock_gettime(CLOCK_MONOTONIC, &now);
        if (now.tv_sec > deadline.tv_sec ||
            (now.tv_sec == deadline.tv_sec && now.tv_nsec >= deadline.tv_nsec)) {
            kill(pid, SIGKILL); waitpid(pid, &status, 0); r.timed_out = 1; break;
        }
        struct timespec nap = {0, 1000 * 1000};
        nanosleep(&nap, NULL);
    }
    close(op[0]); close(ep[0]);
    r.err[te] = 0;
    r.ran = 1;
    if (!r.timed_out) r.exit_code = WIFEXITED(status) ? WEXITSTATUS(status) : -1;
    return r;
}

/* The four things pcrec can say about a pattern, as an outside caller can
 * tell them apart. The three refusal classes are NOT interchangeable:
 *
 *   SPEC_VC_ACCEPTED  exit 0 — pcrec translated the pattern.
 *   SPEC_VC_MODULE    a refusal naming a module owner ("requires module
 *                     'X'", or — [M6.3], `(?J)`'s ruled wording — "module
 *                     'X' does not implement ..." for a construct that IS
 *                     enabled but whose owning module still does not cover
 *                     it, which reads as a false "enabling X fixes this"
 *                     if forced into the "requires" phrasing). Either way
 *                     pcrec is saying the construct is REAL and unimplemented.
 *   SPEC_VC_SCOPE     a refusal saying the construct is out of pcrec's scope
 *                     forever. Also an assertion that the construct is REAL.
 *   SPEC_VC_INVALID   any other refusal. pcrec is saying the pattern is not
 *                     valid PCRE2 — an opinion libpcre2 can contradict.
 *
 * The MODULE/SCOPE vs INVALID split is the whole of D26's "whether a
 * construct is REAL is exact": refusing a real construct as INVALID is a
 * defect even though both are refusals and neither miscompiles. */
typedef enum {
    SPEC_VC_ACCEPTED, SPEC_VC_MODULE, SPEC_VC_SCOPE, SPEC_VC_INVALID, SPEC_VC_ERROR
} SpecVClass;

static inline SpecVClass spec_pcrec_classify(const SpecPcrecRun *r)
{
    if (!r->ran || r->timed_out) return SPEC_VC_ERROR;
    if (r->exit_code == 0) return SPEC_VC_ACCEPTED;
    if (r->exit_code != 1) return SPEC_VC_ERROR;
    /* [M6.3]: "module '" (no longer requiring the "requires " prefix)
     * catches both known module-naming shapes — see the enum's own
     * comment above. */
    if (strstr(r->err, "module '")) return SPEC_VC_MODULE;
    if (strstr(r->err, "outside pcrec's scope")) return SPEC_VC_SCOPE;
    return SPEC_VC_INVALID;
}

static inline const char *spec_vclass_name(SpecVClass c)
{
    switch (c) {
        case SPEC_VC_ACCEPTED: return "ACCEPTED";
        case SPEC_VC_MODULE:   return "REFUSED-AS-UNIMPLEMENTED";
        case SPEC_VC_SCOPE:    return "REFUSED-AS-OUT-OF-SCOPE";
        case SPEC_VC_INVALID:  return "REFUSED-AS-INVALID";
        default:               return "ERROR";
    }
}

/* The module name out of either module-naming shape (see SpecVClass's own
 * comment: "requires module 'X'" or [M6.3]'s "module 'X' does not
 * implement ..."), or "" if there is none. */
static inline const char *spec_pcrec_module(const SpecPcrecRun *r)
{
    static char buf[64];
    buf[0] = 0;
    const char *p = strstr(r->err, "module '");
    if (!p) return buf;
    p += strlen("module '");
    size_t n = 0;
    while (p[n] && p[n] != '\'' && n < sizeof buf - 1) { buf[n] = p[n]; n++; }
    buf[n] = 0;
    return buf;
}

/* The N out of "(pattern offset N)", or -1 if the diagnostic has none. */
static inline long spec_pcrec_offset(const SpecPcrecRun *r)
{
    const char *p = strstr(r->err, "(pattern offset ");
    if (!p) return -1;
    return strtol(p + strlen("(pattern offset "), NULL, 10);
}

/* Compile PAT under a given --features setting. Everything the callers need
 * is in the returned struct; classification is theirs to do. */
static inline SpecPcrecRun spec_pcrec_compile(const char *path, const char *features,
                                       const char *pat, const char *extra_flag)
{
    char *argv[10]; int k = 0;
    argv[k++] = (char *)path;
    argv[k++] = (char *)"--features"; argv[k++] = (char *)features;
    if (extra_flag && *extra_flag) argv[k++] = (char *)extra_flag;
    argv[k++] = (char *)"-o"; argv[k++] = (char *)"-";
    argv[k++] = (char *)"--"; argv[k++] = (char *)pat;
    argv[k] = NULL;
    return spec_pcrec_run(path, argv);
}

#endif /* PCREC_SPEC_MOD0_PCREC_H */
