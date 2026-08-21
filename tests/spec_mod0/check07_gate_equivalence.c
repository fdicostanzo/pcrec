/* check07_gate_equivalence.c — INVARIANT 7: gate equivalence, with a real
 * population. (And invariant 9's population machinery; see check09.)
 *
 * THE PROMISE. "Disabled-feature verdicts equal enabled-feature verdicts,
 * varied over the WHOLE enabled set (all on / all off / one inverted), with a
 * per-name compared-pair count and a ratcheting floor printed on the PASS
 * line — an empty population is indistinguishable from a pass otherwise, and
 * at landing the population IS empty until the first module flips. Membership
 * ('whose validity PCRE2 decides') is computed by asking libpcre2, never
 * hand-listed."
 *
 * THE CLAIM. Whether pcrec has a feature switched on must not change what it
 * says about a pattern's VALIDITY. A disabled feature changes what pcrec can
 * COMPILE — that is the point of a gate — but not what it considers real: a
 * construct pcrec refuses because the module is off must still be refused as
 * "requires module 'X'", never as "that is not valid syntax". Otherwise the
 * gate is not a gate, it is a second, quieter grammar.
 *
 * MEMBERSHIP IS MEASURED, NOT LISTED. "Whose validity PCRE2 decides" is a
 * question about PCRE2, so it is put to PCRE2: a row is a member iff libpcre2
 * ACCEPTS the row's `syntax` probe as a pattern. A hand-maintained list of
 * member rows would be a transcription of somebody's belief about which
 * constructs are real, and it would agree with that belief forever. The count
 * is printed every run, so a row leaving the set is visible.
 *
 * ARMED SURFACE (measured 2026-08-11). `pcrec --features LIST [...]` exists:
 * LIST is comma-separated module names from --list-syntax's module column,
 * or 'all'/'none' (default none), and refuses an unknown name BY NAME, exit
 * 1. Detected live by grepping `--help` for "--features" — never assumed.
 *
 * A COMPARED PAIR, defined and defended BEFORE the first run of this armed
 * version (a correction below records where the first draft of this
 * definition was wrong). The naive definition — "any row, under any
 * configuration where the module's state differs from 'all on'" — would
 * inflate the count with TRIVIALLY-equal comparisons: today every module is
 * unimplemented, so a module-gated row is refused as "requires module 'X'"
 * under EVERY configuration, whether that module is on or off. Counting those
 * as "compared" would claim a comparison was meaningful when the two sides
 * could not have differed no matter what pcrec does — the exact inflation the
 * brief warns against. So a pair counts ONLY when it was CAPABLE of
 * disagreeing: a row R, owned by module M (R's `module` column == M), that
 * libpcre2 accepts (R is a member) AND that pcrec ACCEPTS under 'all on'.
 * Only an accepted-under-all-on row demonstrates the module is doing
 * anything; disabling a module that was never going to let the row through
 * either way tests nothing. Each eligible row contributes 2 pairs (all-off
 * vs all-on, and inverted-M vs all-on) to `pairs[M]`.
 *
 * CORRECTION (made before landing, not after — this is the version that
 * shipped). The first idea was to count every (module-owned row) x (differing
 * config) as a pair regardless of accept/refuse, on the theory that "the gate
 * COULD in principle be wired differently". Measuring against the real binary
 * showed that gives ~1700 nonzero "compared pairs" TODAY, while every one of
 * them is refused identically in all three configurations — a pass that would
 * read as "gate equivalence holds over 1700 pairs" when not one row has ever
 * been let through a gate. That is precisely the vacuous-pass shape C4/F4
 * named. The accepted-under-all-on gate above is what makes the count track
 * whether anything is actually switchable, not merely nameable.
 *
 * WHAT IS ASSERTED, over the WHOLE registry, regardless of eligibility: for
 * each module name M, and each of the two non-baseline configurations (all
 * off, inverted-M = every module but M), every registry row's syntax probe is
 * compiled with pcrec and its VERDICT CLASS (accepted / refused-as-
 * unimplemented — stderr contains "requires module '" — / refused-as-invalid
 * — any other refusal) is compared against the same row compiled under 'all
 * on'. ANY class mismatch is a FAILURE naming the row, its module (or "none"
 * for base/rejected rows), and both configurations — this check is NOT
 * restricted to eligible rows; a cross-module leak on a row owned by a
 * DIFFERENT module, or a rejected/base row flipping classes, is exactly the
 * kind of bug the invariant exists to catch, and is checked even though it
 * will never count toward `gate.compared_pairs`.
 *
 * WHY A SEPARATE INSTRUMENT-LIVENESS CHECK, GIVEN THE COMPARISON ABOVE. The
 * verdict-CLASS comparison above is BLIND to whether --features is wired to
 * anything at all while no module is implemented: a --features flag that was
 * silently a no-op would pass the class comparison exactly as well as a
 * correctly-wired one, because every row is refused-as-unimplemented in every
 * configuration either way — a control sharing its source with the thing it
 * controls (see tests/spec_mod0's own method note and the project's recorded
 * check-design lesson: a check that never observed the flag doing anything
 * cannot tell a live flag from a dead one). So before the sweep, this check
 * proves the flag reaches the parser, live, two ways using --probe-ask's
 * `answered_at` field (the channel check06 already established as the
 * cursor's own voice, reused here for the gate's): (a) an unknown module name
 * is refused BY NAME; (b) enabling module M's own construct reaches
 * `answered_at=result` (module M's doorway now proceeds past the point of
 * asking "is this real"), while an UNRELATED module's construct, probed under
 * the same `--features M`, still stops at `answered_at=verdict` — proving
 * enabling M does not also enable something else. Both are measured against
 * rows FOUND from the registry (names[0], names[1] and their first matching
 * rows), never hand-listed.
 *
 * WHAT IS ASSERTED, TODAY, TO REMAIN AWAITING RATHER THAN PASS. With the
 * instrument proven live and the sweep run in full, `gate.compared_pairs` is
 * still 0: `gate.baseline_accepted_rows` is 1 (only the base row `(?:...)`,
 * which is owned by no module) and `gate.eligible_rows` is 0. A check that
 * cannot yet disagree — because nothing is comparable — must not report a
 * pass (C4/F4). So this check exits AWAITING-POPULATION (distinct from the
 * old AWAITING-SURFACE: the surface exists and the comparison runs; what is
 * missing is a module for it to have an opinion about) until the first module
 * lands and gate.compared_pairs's floor is raised above 0 in floors.txt.
 *
 * CORRECTED 2026-08-12 — THE DAY THE POPULATION ARRIVED (module `classes`,
 * MOD-0.3c; 12 eligible rows, 24 pairs). The paragraph above is now history,
 * and so is the strict class-EQUALITY the sweep originally asserted: on its
 * first live population it reported 24 "disagreements" that were all the
 * gate DOING ITS JOB (accepted under all-on, refused-as-unimplemented with
 * the module off) — the CLAIM paragraph had said "a disabled feature changes
 * what pcrec can COMPILE — that is the point of a gate" all along, and the
 * equality form was only the exercisable subset while nothing could flip.
 * The sweep now applies the TRANSITION RULE (transition_ok below): a
 * disabled-module row that was accepted at baseline MUST flip to
 * refused-as-unimplemented NAMING ITS OWN MODULE — still-accepted is a DEAD
 * GATE (the direction equality was structurally blind to, sabotage-verified:
 * an ext_gate that never demotes fails 24 clauses by name), refused-as-
 * invalid is the second-quieter-grammar defect, someone else's name is a
 * misattribution; every other row keeps the equality requirement, so
 * cross-module leaks still fail. `gate.eligible_rows` (12) and
 * `gate.baseline_accepted_rows` (13) are floored; `gate.compared_pairs`
 * stays floor-0 DELIBERATELY — check09's per-name-nonzero assertion arms on
 * that floor and would demand all 17 modules toggle while only one has a
 * producer; the pair count is transitively ratcheted meanwhile by the
 * eligible_rows floor through the pairs==eligible*2 self-consistency
 * assertion. Raising it is MOD-0.8-close work (or the second module's).
 *
 * SPEC-M AMENDMENT (2026-08-21, docs/dev/plan.md [SPEC-M]). `(?m)` measurably
 * needs TWO modules ('modifiers' for its GROUP SYNTAX, 'assertions' for its
 * MULTILINE EFFECT), which this file's original model — one construct, one
 * owning module — did not anticipate and, correctly, flagged as a disagreement
 * once module `assertions` landed ([M6.2] wave C, 2026-08-19). See
 * `is_m_cross_module_row`'s own comment, right above `member_ok[]` below, for
 * the fact, the evidence, the exact scope, and the expiry condition.
 *
 * SABOTAGE (verified — see the final report for exact commands and output).
 * (1) Oracle half: drop the membership test and take all 100 rows as members
 *     — the printed membership count jumps, failing the pinned floor's
 *     sibling assertion below.
 * (2) A lying pcrec stand-in that reports refused-as-INVALID (no "requires
 *     module" text) for one specific row only under its 'inverted-M'
 *     configuration, matching the real binary everywhere else — this check
 *     FAILS, naming that row, its module, and the two configurations that
 *     disagreed.
 * (3) A stand-in whose --help does not mention --features — this check
 *     reports AWAITING-SURFACE (the old path, still live as a fallback),
 *     never a pass.
 * (4) A stand-in whose --features silently does nothing (always behaves as
 *     'all') — the instrument-liveness check (b) above catches this: the
 *     "other module still stops at verdict" assertion fails, because a no-op
 *     flag would answer 'result' unconditionally. THIS is the sabotage the
 *     class-comparison sweep alone cannot see, which is why (b) exists.
 * (5) The real build/pcrec — instrument validated live, 1700 verdict-class
 *     checks run, 0 disagreements, 0 eligible pairs (honestly), reported as
 *     AWAITING-POPULATION.
 *
 * Build: TMPDIR=/var/tmp gcc -I tests/fuzz -I tests/spec_mod0 \
 *          -o /var/tmp/check07 check07_gate_equivalence.c -ldl
 * Run:   check07 floors.txt registry.tsv [pcrec-path]
 */
#include "spec_common.h"
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

/* module names, as they appear in the registry's `module` column */
static char names[64][64];
static long pairs[64];
static int nnames;

static int name_index(const char *m)
{
    for (int i = 0; i < nnames; i++)
        if (!strcmp(names[i], m)) return i;
    if (nnames >= 64) return -1;
    snprintf(names[nnames], 64, "%s", m);
    pairs[nnames] = 0;
    return nnames++;
}

/* Lookup only — never inserts. Used once module collection is complete, so a
 * module value that somehow was not seen during collection is a bug to
 * surface (-1), not a name to silently add. */
static int name_lookup(const char *m)
{
    if (!m || !*m) return -1;
    for (int i = 0; i < nnames; i++)
        if (!strcmp(names[i], m)) return i;
    return -1;
}

/* ------------------------------------------------------------------------
 * Running pcrec as a black box, no shell involved anywhere: every syntax
 * probe reaches pcrec as one argv element via execv(), so a construct's
 * quotes/backslashes/parens reach it exactly as the registry spelled them.
 * Modelled on check02's run_pcrec_count, generalised to a caller-supplied
 * argv and an optional stdout capture (compiles redirect stdout to
 * /dev/null in the child instead of piping it — nothing here reads generated
 * C, and piping-then-not-draining a large "-o -" dump risks the child
 * blocking on a full pipe while this check has stopped reading it).
 * ---------------------------------------------------------------------- */

#define PCREC_TIMEOUT_MS 3000

typedef struct {
    int ran;
    int timed_out;
    int exit_code;
    char out[4096];
    char err[512];
} PcrecRun;

static PcrecRun run_pcrec(const char *path, char *const argv[], int capture_stdout)
{
    PcrecRun r; memset(&r, 0, sizeof r);
    int opfd[2] = {-1, -1}, epfd[2];
    if (capture_stdout && pipe(opfd) != 0) return r;
    if (pipe(epfd) != 0) {
        if (capture_stdout) { close(opfd[0]); close(opfd[1]); }
        return r;
    }
    pid_t pid = fork();
    if (pid < 0) {
        if (capture_stdout) { close(opfd[0]); close(opfd[1]); }
        close(epfd[0]); close(epfd[1]);
        return r;
    }
    if (pid == 0) {
        if (capture_stdout) {
            close(opfd[0]);
            dup2(opfd[1], STDOUT_FILENO);
            close(opfd[1]);
        } else {
            int devnull = open("/dev/null", O_WRONLY);
            if (devnull >= 0) { dup2(devnull, STDOUT_FILENO); close(devnull); }
        }
        close(epfd[0]);
        dup2(epfd[1], STDERR_FILENO);
        close(epfd[1]);
        execv(path, argv);
        _exit(127);   /* exec failed: no such binary, or not executable */
    }
    if (capture_stdout) close(opfd[1]);
    close(epfd[1]);
    if (capture_stdout) {
        int fo = fcntl(opfd[0], F_GETFL, 0);
        fcntl(opfd[0], F_SETFL, fo | O_NONBLOCK);
    }
    int fe = fcntl(epfd[0], F_GETFL, 0);
    fcntl(epfd[0], F_SETFL, fe | O_NONBLOCK);

    struct timespec deadline;
    clock_gettime(CLOCK_MONOTONIC, &deadline);
    deadline.tv_sec += PCREC_TIMEOUT_MS / 1000;

    size_t to = 0, te = 0;
    int status = 0, exited = 0;
    for (;;) {
        pid_t w = waitpid(pid, &status, WNOHANG);
        if (w == pid) exited = 1;

        ssize_t n;
        if (capture_stdout)
            while (to < sizeof r.out - 1 &&
                   (n = read(opfd[0], r.out + to, sizeof r.out - 1 - to)) > 0)
                to += (size_t)n;
        while (te < sizeof r.err - 1 &&
               (n = read(epfd[0], r.err + te, sizeof r.err - 1 - te)) > 0)
            te += (size_t)n;

        if (exited) break;

        struct timespec now;
        clock_gettime(CLOCK_MONOTONIC, &now);
        if (now.tv_sec > deadline.tv_sec ||
            (now.tv_sec == deadline.tv_sec && now.tv_nsec >= deadline.tv_nsec)) {
            kill(pid, SIGKILL);
            waitpid(pid, &status, 0);
            r.timed_out = 1;
            break;
        }
        struct timespec nap = {0, 2 * 1000 * 1000};
        nanosleep(&nap, NULL);
    }
    if (capture_stdout) close(opfd[0]);
    close(epfd[0]);
    r.out[to] = 0;
    r.err[te] = 0;
    r.ran = 1;
    if (!r.timed_out) r.exit_code = WIFEXITED(status) ? WEXITSTATUS(status) : -1;
    return r;
}

/* -------------------------------------------------------- verdict class */

/* [M6.3] VC_SCOPE joins the three-way model: a refusal saying the
 * construct is out of pcrec's scope FOREVER (K14's ROADMAP_NEVER shape;
 * spec_pcrec.h's shared SPEC_VC_SCOPE names the identical category for
 * every other spec_mod0 check). Kept as READY INFRASTRUCTURE — mirroring
 * the registry's own "no RS_MODULE ROADMAP_NEVER rows today; the check
 * stays column-derived and re-arms the day one exists" posture
 * (registry_check.c) — even though no row this sweep can reach uses it
 * today: `(?J)` was briefly the first (a same-day intermediate wording
 * used K14's shape), but the manager's RULING (citing the ratified D38
 * PCRE2_DUPNAMES row — a PLANNED-LATER disposition, not NEVER — and
 * docs/pcre2_compliance.md's own REJECTED/planned status) replaced it
 * with a truthful-but-not-"requires" phrasing that this file's VC_UNIMPL
 * detection now recognises directly (see compile_verdict below) rather
 * than needing this fourth state. Left in place because the CATEGORY —
 * a real, permanently-excluded construct — is still a real shape D26
 * distinguishes from VC_INVALID's "not valid PCRE2 at all", and the next
 * row that genuinely needs it should not have to reinvent the plumbing. */
typedef enum { VC_ACCEPTED, VC_UNIMPL, VC_SCOPE, VC_INVALID, VC_ERROR } VClass;

static const char *vclass_name(VClass c)
{
    switch (c) {
    case VC_ACCEPTED: return "accepted";
    case VC_UNIMPL:   return "refused-as-unimplemented";
    case VC_SCOPE:    return "refused-as-out-of-scope";
    case VC_INVALID:  return "refused-as-invalid";
    default:          return "ERROR";
    }
}

/* Compile SYNTAX as a whole pattern under a chosen --features LIST, via
 * `-o -` (self-contained C to stdout, discarded — only the exit code and
 * stderr diagnostic classify the verdict). exit 0 = accepted; exit 1 with
 * "requires module '" in stderr = refused-as-unimplemented; exit 1
 * otherwise = refused-as-invalid; anything else is a harness-level failure,
 * reported once here rather than silently miscounted downstream. */
static VClass compile_verdict(const char *pcrec_path, const char *features,
                               const char *syntax, char *named_module,
                               size_t named_sz)
{
    char *argv[] = {
        (char *)pcrec_path, (char *)"--features", (char *)features,
        (char *)"-o", (char *)"-", (char *)"--", (char *)syntax, NULL
    };
    if (named_module && named_sz) named_module[0] = '\0';
    PcrecRun r = run_pcrec(pcrec_path, argv, 0);
    if (!r.ran) {
        spec_fail("compile_verdict: fork/exec failed for '%s' under "
                  "--features %s", syntax, features);
        return VC_ERROR;
    }
    if (r.timed_out) {
        spec_fail("compile_verdict: pcrec did not return within %dms for "
                  "'%s' under --features %s", PCREC_TIMEOUT_MS, syntax, features);
        return VC_ERROR;
    }
    if (r.exit_code == 0) return VC_ACCEPTED;
    if (r.exit_code == 1) {
        /* [M6.3] THIRD PASS: the module-naming phrase is no longer always
         * "requires module 'X'" — the manager's ruling on (?J) (citing
         * the ratified D38 PCRE2_DUPNAMES row) replaced that framing with
         * "module 'X' does not implement ..." specifically to avoid the
         * false "enabling X fixes this" implication, since named-groups
         * IS enabled when this refusal fires. Both shapes are the SAME
         * verdict class — a REAL construct pcrec knows about and has not
         * (yet, or ever, for DUPNAMES specifically) built — so the
         * extraction now matches the bare `module '` marker rather than
         * requiring the "requires " prefix; the two known phrasings both
         * contain it and nothing else in this doorway's vocabulary does.
         * "outside pcrec's scope" (K14's ROADMAP_NEVER shape) is checked
         * first anyway, unreachable today (no RS_MODULE row uses it) but
         * kept as ready infrastructure — see VC_SCOPE's own comment. */
        if (strstr(r.err, "outside pcrec's scope")) return VC_SCOPE;
        const char *p = strstr(r.err, "module '");
        if (!p) return VC_INVALID;
        /* which module the refusal NAMES — the 2026-08-12 transition rule
         * (below) requires a gate-flip to name the row's OWN module, so a
         * misattributed refusal cannot pass as a healthy toggle */
        if (named_module && named_sz) {
            p += strlen("module '");
            size_t i = 0;
            while (p[i] && p[i] != '\'' && i + 1 < named_sz) {
                named_module[i] = p[i];
                i++;
            }
            named_module[i] = '\0';
        }
        return VC_UNIMPL;
    }
    spec_fail("compile_verdict: pcrec exited %d (expected 0 or 1) for '%s' "
              "under --features %s (stderr: %s)", r.exit_code, syntax,
              features, r.err);
    return VC_ERROR;
}

/* THE TRANSITION RULE (2026-08-12, the day the first module landed — a
 * dated correction per this suite's own convention, recorded rather than
 * edited away; the original strict-equality comparison below it was the
 * exercisable subset while the population was zero and became WRONG the
 * moment it wasn't — its own CLAIM paragraph said so all along: "a disabled
 * feature changes what pcrec can COMPILE — that is the point of a gate").
 *
 * For a row R under configuration C compared against 'all on':
 *   - R's module DISABLED in C, baseline accepted:  R must flip to
 *     refused-as-unimplemented AND the refusal must name R's OWN module.
 *     Staying accepted is a DEAD GATE (the direction strict equality was
 *     blind to); flipping to invalid is the second-quieter-grammar defect;
 *     naming someone else's module is a misattribution.
 *   - [M6.3] R's module DISABLED in C, baseline OUT-OF-SCOPE: the SAME
 *     rule, one terminal state over, kept as READY INFRASTRUCTURE
 *     alongside VC_SCOPE itself (see that enum's own comment) — NOT
 *     exercised by any row today. Were a row's construct REAL but
 *     PERMANENTLY excluded (K14's ROADMAP_NEVER shape) and its owning
 *     module's gate actually flippable, its refusal's SHAPE would depend
 *     on that gate exactly the way an accepted row's does: gate OPEN, the
 *     construct-specific producer answers the PERMANENT scope exclusion
 *     (never a module name — that is what makes it permanent); gate
 *     CLOSED, the producer never runs and the generic ROW-level catch-all
 *     answers instead, which DOES name the row's own module. So the
 *     required flip under a disabled-module config would be OUT-OF-SCOPE
 *     -> refused-as-unimplemented, naming the row's own module —
 *     structurally identical to the accepted case, and checked by the
 *     same two clauses below with `dead_state` standing in for "still
 *     ACCEPTED"/"still OUT-OF-SCOPE".
 *   - R's module DISABLED in C, baseline not accepted and not
 *     out-of-scope: class equality (a port-less row refuses identically
 *     either way).
 *   - R's module NOT disabled in C (including no-module rows): class
 *     equality — any change is a cross-module leak.
 * Returns 1 if ok, else 0 after reporting. */
static int transition_ok(const char *syntax, const char *rowmod,
                         int mod_disabled_in_cfg, const char *cfgname,
                         VClass base, VClass vc, const char *named)
{
    if (mod_disabled_in_cfg && (base == VC_ACCEPTED || base == VC_SCOPE)) {
        const char *dead_state = base == VC_ACCEPTED ? "ACCEPTED" : "OUT-OF-SCOPE";
        if (vc != VC_UNIMPL) {
            spec_fail("row '%s' (module '%s'): still %s under %s (got %s) — "
                      "a row whose baseline is %s and whose OWN module is "
                      "OFF must refuse as unimplemented (staying %s or an "
                      "unrelated flip to invalid are both dead-gate shapes)",
                      syntax, rowmod, dead_state, cfgname, vclass_name(vc),
                      dead_state, dead_state);
            return 0;
        }
        if (strcmp(named, rowmod) != 0) {
            spec_fail("row '%s' (module '%s'): gate-flip under %s names module "
                      "'%s' — a flip must name the row's own module",
                      syntax, rowmod, cfgname, named);
            return 0;
        }
        return 1;
    }
    if (vc != base) {
        spec_fail("row '%s' (module '%s'): verdict class differs — all-on=%s, "
                  "%s=%s%s", syntax, (rowmod && *rowmod) ? rowmod : "(none)",
                  vclass_name(base), cfgname, vclass_name(vc),
                  mod_disabled_in_cfg ? "" :
                  " — the varied module does not own this row: a cross-module leak");
        return 0;
    }
    return 1;
}

/* answered_at (TSV field 3) from `--probe-ask result -- SYNTAX` under a
 * chosen --features LIST. NULL on any run failure. Used only by the
 * instrument-liveness sanity below, never by the verdict-class sweep. */
static const char *probe_answered_at(const char *pcrec_path, const char *features,
                                      const char *syntax, char *buf, size_t bufsz)
{
    char *argv[] = {
        (char *)pcrec_path, (char *)"--features", (char *)features,
        (char *)"--probe-ask", (char *)"result", (char *)"--",
        (char *)syntax, NULL
    };
    PcrecRun r = run_pcrec(pcrec_path, argv, 1);
    if (!r.ran || r.timed_out || r.exit_code != 0) return NULL;
    char f0[128];
    if (sscanf(r.out, "%127[^\t]\t%*[^\t]\t%127[^\t\n]", f0, buf) != 2) {
        (void)bufsz;
        return NULL;
    }
    return buf;
}

/* Every module name except `skip`, comma-joined — 'none' if that empties the
 * list (only possible when the registry declares a single module name). */
static void build_inverted_list(char *buf, size_t bufsz, int skip)
{
    buf[0] = 0;
    int first = 1;
    for (int i = 0; i < nnames; i++) {
        if (i == skip) continue;
        if (!first) strncat(buf, ",", bufsz - strlen(buf) - 1);
        strncat(buf, names[i], bufsz - strlen(buf) - 1);
        first = 0;
    }
    if (buf[0] == 0) snprintf(buf, bufsz, "none");
}

/* SPEC-M NAMED EXCEPTION (2026-08-21, docs/dev/plan.md [SPEC-M], Frank's
 * ruling "agree but don't spend a lot of time as this is to be replaced").
 *
 * THE FACT. This suite's model (invariant 7 itself, and check01's isolation
 * invariant beside it) assumes a construct's behaviour depends only on its
 * OWN module's gate. `(?m)` measurably does not: its GROUP SYNTAX (the `(?`
 * doorway recognising the run, and the row itself) belongs to module
 * `modifiers`, but its MULTILINE MATCHING EFFECT is decided by module
 * `assertions` -- mod_modifiers.c's case 'm' calls
 * `pcrec_feature_enabled(FEAT_ASSERTIONS)`, not `FEAT_MODIFIERS`, before
 * setting the scoped multiline bit ([M6.2] wave C, src/parse/mod_modifiers.c
 * around line 314). That is correct pcrec design, not a cross-module leak:
 * the two modules own two different questions about the same eleven bytes.
 *
 * EVIDENCE (measured independently, twice, before this exception was
 * written). tests/assertions/d27/gating.rxt -- a D27-blinded corpus --
 * pins all FOUR gate combinations for `(?m)^a`: default (modifiers on,
 * assertions off under std1) refuses naming 'assertions'; --features none
 * refuses at the GROUP SYNTAX naming 'modifiers'; modifiers-only refuses
 * naming 'assertions' (same point as default); assertions-only refuses at
 * the GROUP SYNTAX naming 'modifiers' (the mirror case) -- and it only
 * compiles with BOTH enabled. docs/design/registry_built_status_memo.md
 * (D65, ratified) independently documents the identical fact from the
 * built-status side, and names this suite's own two red checks as the
 * pre-existing consequence.
 *
 * WHAT THIS DOES NOT DO. It does not weaken the invariant for any other
 * row, and it does not touch check01's discovery machinery or check07's
 * counting rule -- `(?m)` is selected by the row's own STRUCTURED fields
 * (kind/selector/module), never by matching "(?m)" as text, so a future row
 * that happens to share the syntax spelling would not silently inherit the
 * exception, and this row would stop matching (failing loud, per the
 * REQUIRED-below guard) if the registry ever renamed the selector or the
 * owning module.
 *
 * SCOPE, PRECISELY. The exception applies to exactly one comparison: the
 * INVERTED-ASSERTIONS configuration (module 'assertions' disabled, every
 * other module including the row's own 'modifiers' left enabled). Every
 * other configuration for this row -- all-off, inverted-modifiers, and
 * every other module's inverted sweep -- takes the ORDINARY transition
 * rule unchanged, because disabling 'modifiers' closes the GROUP SYNTAX
 * gate before mod_modifiers.c ever reaches the assertions check, and no
 * other module's state touches this row at all.
 *
 * EXPIRY. Resolved by [DD-11]'s flags-as-binding-mutators redesign, which
 * removes the cross-module read this exception exists to describe; this
 * fix is interim truth-restoration, not architecture (Frank's own framing
 * on the [SPEC-M] plan row). Delete this block and its call site the day
 * that lands, and the ordinary transition rule should just work. */
static int is_m_cross_module_row(const SpecRow *r)
{
    return !strcmp(spec_col(r, SPEC_COL_KIND), "group") &&
           !strcmp(spec_col(r, SPEC_COL_SELECTOR), "m") &&
           !strcmp(spec_col(r, SPEC_COL_MODULE), "modifiers");
}

static int member_ok[256];

int main(int argc, char **argv)
{
    const char *rp = NULL;
    spec_start("check07_gate_equivalence", argc, argv, &rp);

    /* ---- membership: whose validity does PCRE2 decide? ------------------ */
    long members = 0, nonmembers = 0;
    for (int i = 0; i < spec_nrows; i++) {
        const SpecRow *r = &spec_rows[i];
        const char *S = spec_col(r, SPEC_COL_SYNTAX);
        member_ok[i] = spec_compile(S).ok;
        if (member_ok[i]) members++; else nonmembers++;
        const char *m = spec_col(r, SPEC_COL_MODULE);
        if (m && *m) name_index(m);
    }
    printf("  membership (libpcre2 accepts the row's syntax probe): %ld of "
           "%d rows; %ld rows it rejects\n", members, spec_nrows, nonmembers);
    printf("  module names in the registry: %d\n", nnames);
    spec_pop("gate.membership_rows", members);
    spec_pop("gate.module_names", nnames);

    /* Membership must not be everything or nothing: either would mean the
     * question was not actually asked. */
    if (members == 0 || members == spec_nrows)
        spec_fail("membership is %ld of %d — a set that is empty or universal "
                  "is not a measurement, it is a constant", members, spec_nrows);

    /* ---- surface detection: probe --help, never assume ------------------- */
    const char *pcrec_path = (argc >= 4 && argv[3][0]) ? argv[3] : getenv("PCREC");
    if (!pcrec_path || !*pcrec_path) pcrec_path = "build/pcrec";

    char *help_argv[] = { (char *)pcrec_path, (char *)"--help", NULL };
    PcrecRun help_r = run_pcrec(pcrec_path, help_argv, 1);
    int surface_present = help_r.ran && !help_r.timed_out &&
                           help_r.exit_code == 0 &&
                           strstr(help_r.out, "--features") != NULL;
    printf("  pcrec:  %s (--features %s)\n", pcrec_path,
           surface_present ? "present — comparing" : "not present — awaiting");

    long verdict_checks_total = 0, eligible_rows = 0, baseline_accepted_rows = 0;

    if (surface_present) {
        /* ---- instrument liveness: prove the flag reaches the gate -------
         * The class-comparison sweep below is BLIND to whether --features
         * does anything at all while no module is implemented (every row
         * refuses identically either way). These two live probes are the
         * only channel that can catch a no-op flag today. */

        /* (a) unknown module name refused BY NAME */
        {
            char *bad_argv[] = {
                (char *)pcrec_path, (char *)"--features",
                (char *)"__spec_mod0_unknown__", (char *)"-o", (char *)"-",
                (char *)"--", (char *)"a", NULL
            };
            PcrecRun r = run_pcrec(pcrec_path, bad_argv, 0);
            if (!r.ran || r.timed_out || r.exit_code != 1 ||
                !strstr(r.err, "unknown module") ||
                !strstr(r.err, "__spec_mod0_unknown__"))
                spec_fail("instrument: --features with an unknown module name "
                          "did not refuse BY NAME as documented (ran=%d exit=%d "
                          "stderr='%s')", r.ran, r.exit_code, r.err);
        }

        /* (b) per-module isolation via --probe-ask's answered_at, using
         * representative rows FOUND from the registry, never hand-listed */
        if (nnames >= 2) {
            const char *synA = NULL, *synB = NULL;
            for (int i = 0; i < spec_nrows && !(synA && synB); i++) {
                const char *m = spec_col(&spec_rows[i], SPEC_COL_MODULE);
                if (!m || !*m) continue;
                if (!synA && !strcmp(m, names[0]))
                    synA = spec_col(&spec_rows[i], SPEC_COL_SYNTAX);
                if (!synB && !strcmp(m, names[1]))
                    synB = spec_col(&spec_rows[i], SPEC_COL_SYNTAX);
            }
            if (synA && synB) {
                char bufA[128], bufB[128];
                const char *at_own = probe_answered_at(pcrec_path, names[0],
                                                        synA, bufA, sizeof bufA);
                const char *at_other = probe_answered_at(pcrec_path, names[1],
                                                          synA, bufB, sizeof bufB);
                if (!at_own || strcmp(at_own, "result") != 0)
                    spec_fail("instrument: --features %s --probe-ask result -- "
                              "'%s' answered at '%s', expected 'result' — the "
                              "module's own construct should reach the "
                              "furthest ask level when its module is enabled",
                              names[0], synA, at_own ? at_own : "(no answer)");
                if (!at_other || strcmp(at_other, "verdict") != 0)
                    spec_fail("instrument: --features %s --probe-ask result -- "
                              "'%s' (a construct of module '%s') answered at "
                              "'%s', expected 'verdict' — enabling module '%s' "
                              "must not also enable module '%s'",
                              names[1], synA, names[0],
                              at_other ? at_other : "(no answer)",
                              names[1], names[0]);
            } else {
                spec_fail("instrument: could not find registry rows owned by "
                          "'%s' and '%s' to test per-module isolation",
                          names[0], names[1]);
            }
        }

        /* ---- the armed comparison: all on (baseline) vs all off vs
         * inverted-M, over every row, for every module name ---------------- */
        VClass *vc_base = malloc((size_t)spec_nrows * sizeof *vc_base);
        if (!vc_base) { fprintf(stderr, "FAIL[%s]: out of memory\n", spec_check_name); exit(2); }

        for (int i = 0; i < spec_nrows; i++) {
            const char *S = spec_col(&spec_rows[i], SPEC_COL_SYNTAX);
            vc_base[i] = compile_verdict(pcrec_path, "all", S, NULL, 0);
            if (vc_base[i] == VC_ACCEPTED) baseline_accepted_rows++;
        }

        for (int i = 0; i < spec_nrows; i++) {
            const char *S = spec_col(&spec_rows[i], SPEC_COL_SYNTAX);
            const char *m = spec_col(&spec_rows[i], SPEC_COL_MODULE);
            char named[64];
            VClass vc = compile_verdict(pcrec_path, "none", S, named, sizeof named);
            verdict_checks_total++;
            if (vc_base[i] != VC_ERROR && vc != VC_ERROR) {
                /* all-off disables EVERY module, so any module-owned row is
                 * a disabled-module row here (the transition rule's first
                 * arm); no-module rows take the equality arm. */
                transition_ok(S, (m && *m) ? m : "", m && *m, "all-off",
                              vc_base[i], vc, named);
                int midx = name_lookup(m);
                if (midx >= 0 && member_ok[i] && vc_base[i] == VC_ACCEPTED) {
                    pairs[midx]++;
                    eligible_rows++;
                }
            }
        }

        int m_exception_fired = 0;
        for (int mi = 0; mi < nnames; mi++) {
            char inv[1024];
            build_inverted_list(inv, sizeof inv, mi);
            for (int i = 0; i < spec_nrows; i++) {
                const char *S = spec_col(&spec_rows[i], SPEC_COL_SYNTAX);
                const char *m = spec_col(&spec_rows[i], SPEC_COL_MODULE);
                char named[64];
                char cfg[96];
                VClass vc = compile_verdict(pcrec_path, inv, S, named, sizeof named);
                verdict_checks_total++;
                if (vc_base[i] == VC_ERROR || vc == VC_ERROR) continue;
                snprintf(cfg, sizeof cfg, "inverted(-%s)", names[mi]);
                int mod_disabled = m && *m && strcmp(m, names[mi]) == 0;

                /* SPEC-M NAMED EXCEPTION (see is_m_cross_module_row's own
                 * comment above): under inverted-assertions specifically,
                 * `(?m)`'s own module ('modifiers') stays enabled, so the
                 * ordinary rule would demand equality with baseline -- but
                 * the row's MULTILINE EFFECT genuinely depends on
                 * 'assertions' too, so a baseline-accepted row must flip to
                 * refused-as-unimplemented naming 'assertions', the SAME
                 * transition shape a disabled-own-module row takes, just
                 * naming a different module. */
                if (!mod_disabled && is_m_cross_module_row(&spec_rows[i]) &&
                    !strcmp(names[mi], "assertions")) {
                    m_exception_fired = 1;
                    if (vc_base[i] == VC_ACCEPTED) {
                        if (vc != VC_UNIMPL || strcmp(named, "assertions") != 0)
                            spec_fail("row '%s' (module '%s'): SPEC-M named "
                                      "exception -- disabling module "
                                      "'assertions' must flip (?m)'s "
                                      "MULTILINE EFFECT to "
                                      "refused-as-unimplemented naming "
                                      "'assertions' (got %s, named '%s')",
                                      S, m, vclass_name(vc), named);
                    } else if (vc != vc_base[i]) {
                        spec_fail("row '%s' (module '%s'): SPEC-M named "
                                  "exception -- baseline was not accepted "
                                  "(%s), yet disabling 'assertions' still "
                                  "changed the verdict to %s", S, m,
                                  vclass_name(vc_base[i]), vclass_name(vc));
                    }
                } else {
                    /* inverted-M disables ONLY M: rows of every other module
                     * take the equality arm, so a toggle that leaks across
                     * modules fails naming both sides. */
                    transition_ok(S, (m && *m) ? m : "", mod_disabled, cfg,
                                  vc_base[i], vc, named);
                }
                int midx = name_lookup(m);
                if (midx == mi && member_ok[i] && vc_base[i] == VC_ACCEPTED)
                    pairs[mi]++;
            }
        }
        /* Non-vacuity for the exception itself, the same discipline this
         * suite applies to every *.inc pin: an exception that stops
         * matching any row is stale and must fail loud, not quietly stop
         * asserting anything. */
        if (nnames >= 1 && !m_exception_fired) {
            int have_assertions = name_lookup("assertions") >= 0;
            if (have_assertions)
                spec_fail("SPEC-M named exception for row '(?m)' (kind=group, "
                          "selector=m, module=modifiers) matched zero rows "
                          "under inverted(-assertions) -- the exception is "
                          "stale (the row's selector/module moved, or the "
                          "registry dropped it) and needs re-verifying "
                          "before this file is trusted again");
        }
        free(vc_base);

        /* self-consistency: every eligible row contributes exactly 2 pairs
         * (all-off, inverted-own) — a design invariant of the counting rule
         * above, checked rather than merely asserted in a comment */
        {
            long expect = eligible_rows * 2, got = 0;
            for (int i = 0; i < nnames; i++) got += pairs[i];
            if (got != expect)
                spec_fail("internal: total pairs %ld != eligible_rows*2 (%ld) "
                          "— the counting rule and the sweep disagree", got, expect);
        }
    }

    /* ---- per-name compared pairs ---------------------------------------- */
    long total_pairs = 0;
    for (int i = 0; i < nnames; i++) {
        printf("  PERNAME %-18s pairs %ld\n", names[i], pairs[i]);
        total_pairs += pairs[i];
    }
    spec_pop("gate.compared_pairs", total_pairs);

    if (surface_present) {
        spec_pop("gate.baseline_accepted_rows", baseline_accepted_rows);
        spec_pop("gate.eligible_rows", eligible_rows);
        spec_pop("gate.verdict_checks_total", verdict_checks_total);
    }

    if (total_pairs == 0)
        printf("  POPULATION IS EMPTY: zero enabled/disabled pairs were "
               "compared. This is NOT a pass — no module can be toggled yet, "
               "so the equivalence claim is untested. Raise the "
               "gate.compared_pairs floor when the first module lands.\n");

    static const char *const owned[] = {
        "gate.membership_rows", "gate.module_names", "gate.compared_pairs"
    };
    spec_floors_require(owned, 3);
    if (surface_present) {
        static const char *const armed_owned[] = {
            "gate.baseline_accepted_rows", "gate.eligible_rows",
            "gate.verdict_checks_total"
        };
        spec_floors_require(armed_owned, 3);
    }
    if (spec_fails) return spec_finish();

    if (!surface_present)
        return spec_await(
            "a way to vary pcrec's enabled feature set",
            "this check needs to compile a pattern under a chosen enabled set — "
            "any stable channel (a `--features=a,b,c` flag, a `PCREC_FEATURES` "
            "environment variable, or a library entry point) that accepts the "
            "module names from `--list-syntax`'s module column. It then runs the "
            "three configurations the invariant names (all on / all off / every "
            "module but this one) over all registry rows, compares verdict "
            "CLASSES (accepted / refused-as-unimplemented / refused-as-invalid) "
            "against 'all on' for the membership set computed above, and prints "
            "the compared-pair count per module name");

    if (total_pairs == 0) {
        printf("\n  COMPARISON RAN: the surface exists, the instrument was "
               "validated LIVE (an unknown module name refused by name; "
               "enabling module '%s' alone reaches --probe-ask's furthest "
               "answer for its own construct but NOT for module '%s''s), and "
               "%ld verdict-class checks ran across %d module name(s) and %d "
               "row(s), 0 disagreements. Zero pairs were CAPABLE of "
               "disagreeing: only %ld row(s) are accepted under 'all on' "
               "(the base row, owned by no module) — no module has ever let "
               "a row through its gate, so the gate has never been exercised, "
               "only asked-about. This is NOT a pass — raise "
               "gate.compared_pairs's floor in floors.txt when the first "
               "module lands, and this check starts asserting something the "
               "invariant could actually fail.\n",
               nnames >= 2 ? names[0] : "?", nnames >= 2 ? names[1] : "?",
               verdict_checks_total, nnames, spec_nrows, baseline_accepted_rows);
        printf("AWAITING-POPULATION %s (surface present, comparison ran, "
               "instrument validated, 0 comparable pairs; oracle-side "
               "disagreements: %d)\n", spec_check_name, spec_fails);
        return 3;
    }

    return spec_finish();
}
