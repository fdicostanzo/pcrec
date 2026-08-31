/* pcrec command-line interface.
 *
 *   pcrec [-p PREFIX] [-e byte|utf8] [-i] [--emit-main] -o OUT.c 'PATTERN'
 *   pcrec -o - 'PATTERN'      self-contained C on stdout (no header file)
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "pcrec.h"
/* The syntax-query modes read the construct registry, which is internal: the
 * CLI and the test suite are its only consumers, so it is not part of the
 * public surface (see src/parse/syntax_dump.c). main.c touches no registry
 * type — it calls two functions that hand back finished text. */
#include "core/internal.h"
/* [M5-SEAM] the ENCODING REGISTRY: the one table the `byte`/`utf8` names are
 * defined by, so this file maps no encoding name of its own (see D58/SR-10). */
#include "gen/enc/enc.h"

/* [ART-SIZE] Parse a RAISE-ONLY size override. Shared by both caps so the
 * two cannot drift in what they accept, and so the "below the default is a
 * malformed option" rule has exactly one implementation. */
static int parse_raise_only(const char *arg, const char *flag,
                            unsigned long long floor, uint64_t *slot)
{
    char *end = NULL;
    unsigned long long v = strtoull(arg, &end, 10);
    if (!end || *end || arg[0] == '-' || v == 0) {
        fprintf(stderr, "pcrec: %s wants a positive integer (got '%s')\n",
                flag, arg);
        return 1;
    }
    if (v < floor) {
        fprintf(stderr, "pcrec: %s is RAISE-ONLY: %llu is below the built-in "
                        "limit of %llu. These overrides exist to let a caller "
                        "accept a larger artifact, never to make a build "
                        "refuse one it would have accepted\n",
                flag, v, floor);
        return 1;
    }
    *slot = (uint64_t)v;
    return 0;
}

static void usage(FILE *f)
{
    fputs("usage: pcrec [options] -o OUT.c [--] 'PATTERN'\n"
          "  -o FILE        output C file; a matching header FILE with .h is\n"
          "                 also written. '-o -' prints self-contained C to\n"
          "                 stdout with no header file\n"
          "  -p PREFIX      symbol prefix for generated identifiers (default rx)\n"
          "  -e ENCODING, --encoding=ENCODING\n"
          "                 subject encoding for THIS pattern: byte (default)\n"
          "                 or utf8. Per-compile, never global: two patterns\n"
          "                 in one binary may use different encodings. utf8\n"
          "                 is refused until milestone M5\n"
          "  -i             match case-insensitively (ASCII letters); folded\n"
          "                 into the automaton, no run-time cost\n"
          "  --emit-main    append a standalone main() (subject from argv[1])\n"
          "  --no-captures  emit a matcher with no capture output (RX_NCAPS 1,\n"
          "                 DFA engine). Captures are ON by default; this is\n"
          "                 the generation axis that recovers the pre-M4.5\n"
          "                 pure-DFA artifact for a group-bearing pattern\n"
          "  --emit-ir      print the VM PROGRAM LISTING for the pattern and exit:\n"
          "                 labels, choice points with their preference order,\n"
          "                 capture slot assignments, island boundaries and\n"
          "                 callout sites. A query -- takes no -o, emits no C.\n"
          "                 Produced by the emitter's own walk, so it cannot\n"
          "                 drift from the code it describes\n"
          "  --trace        emit an INSTRUMENTED matcher that prints every\n"
          "                 resume-frame push/pop and capture write to stderr\n"
          "                 as it runs. A generation axis: never the default,\n"
          "                 and the artifact says so\n"
          "  --engine=E     dfa | vm | auto (default auto). Diagnostic: a\n"
          "                 request the pattern cannot honour is REFUSED, never\n"
          "                 silently downgraded. --engine=vm also disables the\n"
          "                 DFA prefilter, so the VM derives the whole span\n"
          "                 independently -- which is what makes it usable as a\n"
          "                 cross-check against the DFA rather than an echo of it\n"
          "  --step-budget=N  backtrack resumptions the emitted VM may spend\n"
          "                 before returning PCREC_ERR_STEPS (default:\n"
          "                 500,000,000, D51; docs/spec/limits.md)\n"
          "  --work-budget=N  work units the emitted VM may spend on forward\n"
          "                 work the fail label does not see (frames discarded\n"
          "                 at a cut, frameless scan iterations) before\n"
          "                 returning PCREC_ERR_WORK. A SEPARATE counter\n"
          "                 from the step budget (default: 1,000,000,000, D49;\n"
          "                 docs/spec/limits.md)\n"
          "  --fno-step-budget  emit no step counter at all -- and no work\n"
          "                 counter either, one gate for both. Zero cost, and\n"
          "                 honest because the artifact says so\n"
          "  --warn-emit-bytes=N   warn (never refuse) when an accepted\n"
          "                        artifact exceeds N total bytes; 0 disables\n"
          "  --max-emit-code-bytes=N, --max-emit-bytes=N\n"
          "                 RAISE the two emitted-size limits (bytes of\n"
          "                 emitted C source, comments excluded; the .o is\n"
          "                 ~17% of that). Raise-only: a value below the\n"
          "                 built-in limit is refused. Defaults 500,000 code\n"
          "                 / 1,000,000 total. For a real build put these in\n"
          "                 the pattern source's config block instead\n"
          "  --backtrack-frames=N  the resume-stack capacity. Default: sized\n"
          "                 exactly where the pattern's depth is statically\n"
          "                 bounded, a stamped default otherwise\n"
          "  -h, --help     this help\n"
          "\n"
          "syntax queries (no pattern, no -o):\n"
          "  --list-syntax     TSV of every non-base construct pcrec knows\n"
          "  --list-definitions  TSV of the replacement/definition table\n"
          "                    (D85): one line per (row, definition), the\n"
          "                    core-syntax substitution and the option-scope\n"
          "                    tag it fires under. Joins --list-syntax on\n"
          "                    kind/selector/syntax\n"
          "  --list-verbs      TSV of the (*VERB) names pcrec recognises\n"
          "  --list-families   TSV of the construct FAMILIES (D71): one line\n"
          "                    per family, `built` ANDed over its spellings\n"
          "  --list-axes       TSV of the optimization-axis registry ([CHK-2]):\n"
          "                    one line per (axis, candidate), preference order,\n"
          "                    with its stamp, deny/force flag and one-line\n"
          "                    description. No --flavour axis\n"
          "  --list-limits     TSV of every numeric limit (D90/[LIM-1]): one\n"
          "                    line per limit, its value, unit, kind, whether\n"
          "                    a flag/-D/nothing overrides it, and a one-line\n"
          "                    description. No --flavour axis\n"
          "  --explain SYNTAX  what pcrec knows about one construct, e.g. '\\\\v'\n"
          "  --flavour NAME    restrict either query to a flavour (only 'pcre2'\n"
          "                    exists today; a second one arrives with SR-7)\n"
          "  --count-groups [--] PATTERN\n"
          "                    parse only; print the number of capturing\n"
          "                    groups. A pattern pcrec refuses is refused\n"
          "                    here too, with the same diagnostic\n"
          "  --features LIST   enable feature modules for this invocation:\n"
          "                    comma-separated names from --list-syntax's\n"
          "                    module column, a frozen named set ('std1'),\n"
          "                    'all', or 'none' (default: std1 — an explicit\n"
          "                    --features always wins over the default; see\n"
          "                    docs/dev/decisions.md D37). Composes with\n"
          "                    every mode. Most modules have no producer\n"
          "                    yet, so enabling one changes no verdict —\n"
          "                    the gate's state is visible via --probe-ask's\n"
          "                    answered_at either way\n"
          "  --list-source FILE\n"
          "                    TSV of a `.rxt` SOURCE file AS WRITTEN (DD-13b\n"
          "                    W1): one row per head declaration and per\n"
          "                    pattern block, in FILE ORDER. The head ends at\n"
          "                    the first `pattern` row, so a head row is\n"
          "                    exactly one preceding it. Never resolved --\n"
          "                    `config` composition is validated, not applied\n"
          "  --probe-ask WANT [--] CONSTRUCT\n"
          "                    drive the construct's doorway ONCE at ask\n"
          "                    level WANT (claim|verdict|result) and report\n"
          "                    the parser cursor. TSV: doorway, want,\n"
          "                    answered_at, pos_before, pos_after, outcome,\n"
          "                    at, ep_set_certain, end, msg. The cursor rule\n"
          "                    (pos moves only under result) is what\n"
          "                    tests/spec_mod0's check06 compares here\n", f);
}

/* [M5-SEAM] (D58) The encoding is a PER-COMPILE scalar, so this sets a field
 * of THIS invocation's options and nothing else — there is no global to set.
 * The name is looked up in the ENCODING REGISTRY (src/gen/enc/) rather than
 * mapped by hand here: [SR-10]'s motivating instance was precisely this site
 * hand-mapping "utf8" while src/core/compile.c separately hand-wrote the
 * diagnostic for it. Whether the named encoding is IMPLEMENTED is not asked
 * here — pcrec_compile() owns that refusal, so the CLI and a library caller
 * get the same answer for the same request. */
static int set_encoding(pcrec_options *opt, const char *v)
{
    const PcrecEnc *e = pcrec_enc_by_name(v);
    if (!e) {
        char names[128];
        pcrec_enc_names(names, sizeof names);
        fprintf(stderr, "pcrec: unknown encoding '%s' (want %s)\n", v, names);
        return -1;
    }
    opt->encoding = e->id;
    return 0;
}

static const char *base_name(const char *path)
{
    const char *s = strrchr(path, '/');
    return s ? s + 1 : path;
}

static int write_file(const char *path, const char *text)
{
    FILE *f = fopen(path, "w");
    if (!f) { perror(path); return -1; }
    fputs(text, f);
    if (fclose(f) != 0) { perror(path); return -1; }
    return 0;
}

int main(int argc, char **argv)
{
    pcrec_options opt;
    pcrec_default_options(&opt);
    const char *outpath = NULL;
    const char *pattern = NULL;
    int list_syntax = 0;
    int list_definitions = 0;
    const char *explain = NULL, *flavour = NULL;
    int list_verbs = 0;
    int list_families = 0;
    int list_axes = 0;
    int list_limits = 0;
    int count_groups = 0;
    int emit_ir = 0;
    const char *probe_want = NULL;
    const char *features = NULL;
    const char *list_source = NULL;

    int no_more_opts = 0;
    for (int i = 1; i < argc; i++) {
        const char *a = argv[i];
        if (!no_more_opts && !strcmp(a, "--")) no_more_opts = 1;
        else if (!no_more_opts && (!strcmp(a, "-h") || !strcmp(a, "--help"))) {
            usage(stdout);
            return 0;
        }
        else if (!no_more_opts && !strcmp(a, "--emit-main")) opt.flags |= PCREC_EMIT_MAIN;
        else if (!no_more_opts && !strcmp(a, "-i")) opt.flags |= PCREC_CASELESS;
        /* [M4.5b] the generation axes engine_m4.md §4.6/§5.3/§5.6 name.
         * `--engine=` takes its value with `=` rather than as a separate
         * argument because it is a MODE, not a file or a name — and the
         * separate-argument forms above (-o/-p/-e) all take one. */
        else if (!no_more_opts && !strcmp(a, "--no-captures"))
            opt.flags |= PCREC_NO_CAPTURES;
        else if (!no_more_opts && !strcmp(a, "--trace"))
            opt.flags |= PCREC_TRACE;
        else if (!no_more_opts && !strcmp(a, "--emit-ir")) emit_ir = 1;
        else if (!no_more_opts && !strcmp(a, "--fno-step-budget"))
            opt.step_budget = PCREC_STEP_BUDGET_NONE;
        /* [ENG-BREP] the first of D47.3's DENY family. Spelled `-fno-` in the
         * gcc style the ruling names, and as a bare flag rather than an
         * `=value` mode because a denial has no value to carry. It denies a
         * STRATEGY, never an answer: the artifact matches identically either
         * way, which is exactly what the differential it exists for checks. */
        else if (!no_more_opts && !strcmp(a, "-fno-possessify"))
            opt.flags |= PCREC_NO_POSSESSIFY;
        /* [ENG-BREP] the family's second member. Denying it drops a qualifying
         * quantifier one rung, to frames — which for a bounded repeat is
         * literal replication and therefore the semantic ground truth the
         * differential compares against. */
        else if (!no_more_opts && !strcmp(a, "-fno-revdet"))
            opt.flags |= PCREC_NO_REVDET;
        /* [ENG-BREP] the family's THIRD member, and the one whose denial is
         * load-bearing beyond testing: dropping the counter rung leaves a
         * bounded repeat on frames, i.e. literal replication, i.e. what ships
         * today — the ground truth §8.1's differential compares against. */
        else if (!no_more_opts && !strcmp(a, "-fno-counter"))
            opt.flags |= PCREC_NO_COUNTER;
        /* [M6.4.2] the family's newest member, and the only one that denies an
         * ENGINE rather than a strategy: leaving the proved-dead `A_ATOMIC` in
         * the tree makes SR-8's consultation see a DFA-excluding node. It
         * exists so the free discharge's "changes no answer" claim has a
         * differential; see lib/pcrec.h. */
        else if (!no_more_opts && !strcmp(a, "-fno-atomic-discharge"))
            opt.flags |= PCREC_NO_ATOMIC_DISCHARGE;
        /* [DD-14 wave G] the SPLICE-vs-LINKAGE axis (design §6.3, §9.2).
         * `-fno-atomic-discharge`'s shape, not `-fno-possessify`'s: denying
         * the splice leaves a LINKED call, which is structurally VM-only, so
         * this denial can change which ENGINE a pattern gets and
         * `--engine=dfa -fno-splice-calls` on a spliceable pattern REFUSES.
         * See lib/pcrec.h's PCREC_NO_SPLICE_CALLS comment. */
        else if (!no_more_opts && !strcmp(a, "-fno-splice-calls"))
            opt.flags |= PCREC_NO_SPLICE_CALLS;
        /* [OPT-1] the TWO-TIER ENTRY axis (docs/design/two_tier_entry.md,
         * docs/spec/tuning.md §2.12). Back to `-fno-possessify`'s shape: it
         * changes no answer and is masked out of `rx_info.flags`. Denying it
         * emits the un-suffixed entries as they shipped before [OPT-1], which
         * is the bisect lever for the optimization and the build an identity
         * gate compares the old entry against. See lib/pcrec.h. */
        else if (!no_more_opts && !strcmp(a, "-fno-tiered-entry"))
            opt.flags |= PCREC_NO_TIERED_ENTRY;
        /* [OPT-3] the DFA TABLE-FORM axis (docs/design/premultiplied_dfa_table.md,
         * docs/spec/tuning.md §2.13). `-fno-tiered-entry`'s shape again: it
         * changes no answer and is masked out of `rx_info.flags`. Denying it
         * emits the DFA scan's tables and loop as they shipped before [OPT-3],
         * which is the bisect lever for the optimization and the build the
         * identity comparison uses as its control. See lib/pcrec.h. */
        else if (!no_more_opts && !strcmp(a, "-fno-premul-table"))
            opt.flags |= PCREC_NO_PREMUL_TABLE;
        else if (!no_more_opts && !strcmp(a, "-fno-offset-skip"))
            opt.flags |= PCREC_NO_OFFSET_SKIP;
        else if (!no_more_opts && !strcmp(a, "-fno-anchored-dfa"))
            opt.flags |= PCREC_NO_ANCHORED_DFA;
        /* [OPT-5] Denies the SCAN EDGE, which is the one DFA axis whose
         * denial changes the MACHINE and not only the emitted loop: the run's
         * interior states come back and the table walk with them. That is
         * what makes the denied build the answer-identity sweep's reference
         * rather than merely a slower variant. See lib/pcrec.h. */
        else if (!no_more_opts && !strcmp(a, "-fno-scan-edge"))
            opt.flags |= PCREC_NO_SCAN_EDGE;
        /* [ART-SIZE] Denies the K SELECTION only. It does NOT reach either
         * emitted-size cap — those are raise-only via --max-emit-*-bytes
         * (D84 ruling 1): a safety refusal a flag turns off is not one. */
        else if (!no_more_opts && !strcmp(a, "-fno-size-term"))
            opt.flags |= PCREC_NO_SIZE_TERM;
        /* [M4.6d] the family's FOURTH member: MINIMUM-REMAINING-LENGTH pruning
         * (D51 ruling 1), D46's controllability half for it. Denying it is
         * BYTE-IDENTITY-safe by construction — MRL emits a bound on whichever
         * rung a quantifier already took and changes no rung, slot or capacity
         * — which is what makes the denied build the differential's ground
         * truth rather than merely a slower arm. */
        else if (!no_more_opts && !strcmp(a, "-fno-length-prune"))
            opt.flags |= PCREC_NO_LENGTH_PRUNE;
        /* [M4.6f] the D46 close-out for the PREFILTER axis: a FORCE PAIR,
         * not a deny-only flag, because fit.prefilter is one verdict for
         * the whole artifact rather than a per-quantifier ladder step (see
         * lib/pcrec.h's PCREC_NO_PREFILTER/PCREC_FORCE_PREFILTER comment).
         * Do-or-die on the FORCE-ON direction is asserted in
         * src/opt/select_engine.c, not here — same posture as --engine. */
        else if (!no_more_opts && !strcmp(a, "-fno-prefilter"))
            opt.flags |= PCREC_NO_PREFILTER;
        else if (!no_more_opts && !strcmp(a, "-fprefilter"))
            opt.flags |= PCREC_FORCE_PREFILTER;
        /* [OPT-4] THE PREFILTER'S LANGUAGE (K39), a SECOND force pair on the
         * same axis's neighbourhood and for a different reason from the one
         * above. `-fprefilter` decides WHETHER the hybrid runs; these decide
         * what language its DFA recognises when it does.
         *
         * A PAIR RATHER THAN DENY-ONLY, and the two halves are not mirror
         * images: `-fno-prefilter-collapse` restores the exact machine (the
         * sharper start and the `prefilter-window` ceiling, at a size that
         * scales with the count), while `-fprefilter-collapse` drops only the
         * STATE-BUDGET conjunct — so every counted repeat collapses and the
         * emitted size becomes count-INDEPENDENT rather than count-bounded.
         * Neither reaches the two correctness conjuncts (the DFA is the
         * engine; there is nothing to collapse), which is why neither can
         * change an answer and why the pair is a `make test-axes` sweep
         * subject rather than a semantic switch.
         *
         * NOT DO-OR-DIE, unlike `-fprefilter` above. Forcing the collapse on a
         * pattern with no counted repeat is a request the compiler HONOURS —
         * the collapsed language of such a pattern IS its exact language — so
         * there is nothing to refuse; the artifact stamps `"exact"` because
         * that is what was built. The conflict pair IS refused, in
         * src/opt/select_engine.c beside the existing one. */
        else if (!no_more_opts && !strcmp(a, "-fno-prefilter-collapse"))
            opt.flags |= PCREC_NO_PREFILTER_COLLAPSE;
        else if (!no_more_opts && !strcmp(a, "-fprefilter-collapse"))
            opt.flags |= PCREC_FORCE_PREFILTER_COLLAPSE;
        /* [OPT-ALTCLS] D46's controllability half for src/opt/altcls.c.
         * BACK to the DENY-only family's shape (unlike the FORCE pair just
         * above): each mergeable/factorable alternation run is its own
         * selection point, addressed independently, the same reason
         * -fno-possessify/-fno-revdet/-fno-counter/-fno-length-prune are
         * deny-only — see lib/pcrec.h's PCREC_NO_ALTCLS_MERGE/
         * PCREC_NO_ALTCLS_FACTOR comment. Two separate flags because the
         * stages are separately useful to pin: stage 2 runs on stage 1's
         * output, so denying stage 1 alone still lets stage 2 factor an
         * unmerged run's literal spelling. */
        else if (!no_more_opts && !strcmp(a, "-fno-altcls-merge"))
            opt.flags |= PCREC_NO_ALTCLS_MERGE;
        else if (!no_more_opts && !strcmp(a, "-fno-altcls-factor"))
            opt.flags |= PCREC_NO_ALTCLS_FACTOR;
        /* [ENG-BREP] K, the counter rung's value parameter. One per artifact,
         * never per quantifier (D47 ADDENDUM). */
        else if (!no_more_opts && !strncmp(a, "--unroll=", 9)) {
            char *end = NULL;
            long v = strtol(a + 9, &end, 10);
            if (!end || *end || v < 1 || v > 4096) {
                fprintf(stderr, "pcrec: --unroll wants an integer in 1..4096 "
                                "(got '%s')\n", a + 9);
                return 1;
            }
            opt.unroll_k = (int)v;
        }
        /* [M5-SEAM] (D58) `--encoding=` is the long spelling of `-e`, in the
         * `=value` MODE form `--engine=` already uses (the separate-argument
         * forms are for files and names). Both spellings reach the same
         * lookup, so they cannot drift. */
        else if (!no_more_opts && !strncmp(a, "--encoding=", 11)) {
            if (set_encoding(&opt, a + 11) != 0) return 1;
        }
        else if (!no_more_opts && !strncmp(a, "--engine=", 9)) {
            const char *v = a + 9;
            if (!strcmp(v, "auto"))      opt.engine = PCREC_ENGINE_AUTO;
            else if (!strcmp(v, "dfa"))  opt.engine = PCREC_ENGINE_DFA;
            else if (!strcmp(v, "vm"))   opt.engine = PCREC_ENGINE_VM;
            else {
                fprintf(stderr, "pcrec: --engine must be auto, dfa or vm "
                                "(got '%s')\n", v);
                return 1;
            }
        }
        else if (!no_more_opts && !strncmp(a, "--step-budget=", 14)) {
            char *end = NULL;
            long long v = strtoll(a + 14, &end, 10);
            if (!end || *end || v < 1) {
                fprintf(stderr, "pcrec: --step-budget wants a positive integer "
                                "(use --fno-step-budget for no counter)\n");
                return 1;
            }
            opt.step_budget = v;
        }
        /* [ENG-BREP counter-K] The value knob for the THIRD bound. There is
         * deliberately no `--fno-work-budget`: v1 rides ONE existence gate, so
         * `--fno-step-budget` above suppresses both counters (D49). */
        else if (!no_more_opts && !strncmp(a, "--work-budget=", 14)) {
            char *end = NULL;
            long long v = strtoll(a + 14, &end, 10);
            if (!end || *end || v < 1) {
                fprintf(stderr, "pcrec: --work-budget wants a positive integer "
                                "(use --fno-step-budget for no counters)\n");
                return 1;
            }
            opt.work_budget = v;
        }
        /* [ART-SIZE] The two emitted-size caps' RAISE-ONLY overrides (D84
         * ruling 1). Rejecting a value BELOW the built-in default is the
         * point, not a convenience: raise-only means these can never be used
         * to MANUFACTURE a refusal on someone else's build. For a real build
         * the override belongs in the pattern-source file's `config` block
         * (D84 addendum 3); this flag is for one-off compiles and the
         * harness. */
        else if (!no_more_opts && !strncmp(a, "--max-emit-code-bytes=", 22)) {
            if (parse_raise_only(a + 22, "--max-emit-code-bytes",
                                 PCREC_MAX_VM_EMIT_CODE_BYTES,
                                 &opt.max_emit_code_bytes) != 0) return 1;
        }
        else if (!no_more_opts && !strncmp(a, "--max-emit-bytes=", 17)) {
            if (parse_raise_only(a + 17, "--max-emit-bytes",
                                 PCREC_MAX_EMIT_BYTES,
                                 &opt.max_emit_bytes) != 0) return 1;
        }
        /* [OPT-4] THE ADVISORY WARNING, and it is deliberately NOT
         * `parse_raise_only`. The two caps above are raise-only so no caller
         * can manufacture someone else's refusal; a warning has no such
         * authority — the build succeeds either way — so LOWERING it is the
         * whole point for a project that wants earlier notice, and 0 turns it
         * off. Accepting any value is the correct policy here precisely
         * because this option cannot fail a build. */
        else if (!no_more_opts && !strncmp(a, "--warn-emit-bytes=", 18)) {
            char *end = NULL;
            unsigned long long v = strtoull(a + 18, &end, 10);
            if (!end || *end || a[18] == '\0') {
                fprintf(stderr, "pcrec: --warn-emit-bytes wants a "
                                "non-negative integer (0 disables the "
                                "warning)\n");
                return 1;
            }
            opt.warn_emit_bytes = (uint64_t)v;
        }
        else if (!no_more_opts && !strncmp(a, "--backtrack-frames=", 19)) {
            char *end = NULL;
            long v = strtol(a + 19, &end, 10);
            if (!end || *end || v < 1 || v > 1000000) {
                fprintf(stderr, "pcrec: --backtrack-frames wants a positive "
                                "integer (the array is a LOCAL of the search "
                                "entry, so this is stack)\n");
                return 1;
            }
            opt.frame_capacity = (int)v;
        }
        else if (!no_more_opts && !strcmp(a, "--list-syntax")) list_syntax = 1;
        else if (!no_more_opts && !strcmp(a, "--list-definitions")) list_definitions = 1;
        else if (!no_more_opts && !strcmp(a, "--list-verbs"))  list_verbs = 1;
        else if (!no_more_opts && !strcmp(a, "--list-families")) list_families = 1;
        else if (!no_more_opts && !strcmp(a, "--list-axes"))   list_axes = 1;
        else if (!no_more_opts && !strcmp(a, "--list-limits")) list_limits = 1;
        else if (!no_more_opts && !strcmp(a, "--count-groups")) count_groups = 1;
        /* [DD-13b.W1.1] `--list-source FILE` — the `.rxt` SOURCE dump.
         * Takes its file as the option's VALUE, like --explain and
         * --probe-ask take theirs, rather than as the bare positional
         * argument: that slot is the PATTERN's, and a query that quietly
         * reinterpreted it would make `pcrec --list-source 'a(b|c)'` read
         * a file named after a regex. */
        else if (!no_more_opts && !strcmp(a, "--list-source")) {
            if (i + 1 >= argc) {
                fprintf(stderr, "pcrec: missing value for %s\n", a);
                return 1;
            }
            list_source = argv[++i];
        }
        else if (!no_more_opts && !strcmp(a, "--probe-ask")) {
            if (i + 1 >= argc) {
                fprintf(stderr, "pcrec: missing value for %s\n", a);
                return 1;
            }
            probe_want = argv[++i];
        }
        else if (!no_more_opts && !strcmp(a, "--features")) {
            if (i + 1 >= argc) {
                fprintf(stderr, "pcrec: missing value for %s\n", a);
                return 1;
            }
            features = argv[++i];
        }
        else if (!no_more_opts &&
                 (!strcmp(a, "--explain") || !strcmp(a, "--flavour"))) {
            if (i + 1 >= argc) {
                fprintf(stderr, "pcrec: missing value for %s\n", a);
                return 1;
            }
            const char *v = argv[++i];
            if (a[2] == 'e') explain = v; else flavour = v;
        }
        else if (!no_more_opts &&
                 (!strcmp(a, "-o") || !strcmp(a, "-p") || !strcmp(a, "-e"))) {
            if (i + 1 >= argc) {
                fprintf(stderr, "pcrec: missing value for %s\n", a);
                return 1;
            }
            const char *v = argv[++i];
            if (a[1] == 'o') outpath = v;
            else if (a[1] == 'p') opt.prefix = v;
            else if (set_encoding(&opt, v) != 0) return 1;
        }
        else if (!no_more_opts && a[0] == '-' && a[1]) {
            fprintf(stderr, "pcrec: unknown option '%s' (use -- before a "
                            "pattern that starts with '-')\n", a);
            usage(stderr);
            return 1;
        }
        else if (!pattern) pattern = a;
        else { fprintf(stderr, "pcrec: exactly one pattern expected\n"); return 1; }
    }

    /* --count-groups is the one query that TAKES a pattern — it runs the real
     * parser (parse only, nothing emitted) and prints the running capture
     * count's end-of-parse value (§18.1; the channel tests/spec_mod0/check02
     * compares against libpcre2). A pattern pcrec refuses is refused here
     * with pcrec_compile's exact diagnostic — leftmost refusal, so a count is
     * never reported for a pattern whose constructs pcrec does not know. */
    /* --features installs the enabled set BEFORE anything consults the gate
     * (slice 9). It composes with every mode — a compile, --probe-ask,
     * --count-groups — because it is configuration, not a query; an unknown
     * module name is refused BY NAME rather than silently enabling nothing
     * (the --flavour rule). Modules with a producer (classes, modifiers)
     * change VERDICTS by design — that is the point of a gate; modules
     * without one still change only the probe channel's answered_at
     * (check07 holds that verdict-equivalence half for the rest).
     *
     * D37 (docs/dev/decisions.md): an explicit --features ALWAYS wins; a
     * bare invocation resolves through PCREC_DEFAULT_FEATURES instead of
     * skipping this call — that constant is the one bare-default mapping
     * point — "std1" since [STD1b], advancing only at announced version
     * boundaries (--features none is the verbatim old bare behaviour;
     * --features stdN pins a set forever). Either way the set gets
     * INSTALLED (never left at whatever a previous call left it), which is
     * also what gives the artifact stamp (src/gen) something honest to
     * report for a bare invocation. */
    {
        char ferr[256];
        const char *fspec = features ? features : PCREC_DEFAULT_FEATURES;
        if (pcrec_enabled_set_spec(fspec, ferr, sizeof ferr) != 0) {
            fprintf(stderr, "pcrec: --features: %s\n", ferr);
            return 1;
        }
    }

    /* [DD-13b.W1.1] `--list-source` — the `.rxt` SOURCE dump (w1_impl
     * §1.8, docs/spec/rxt_format.md). A QUERY in --list-syntax's shape:
     * it reads a file, takes no pattern and no -o, and writes a TSV under
     * docs/spec/table_contract.md.
     *
     * IT IS THE SEAM. tests/harness/run.sh calls this once for a
     * head-bearing file and starts its own per-line loop at the `line`
     * column of the first `pattern` row, so the head is a byte range the
     * harness never parses and the head grammar has exactly ONE
     * implementation. That makes the `line` column load-bearing, which is
     * why it has a sabotage row of its own.
     *
     * A file with a head and NO pattern blocks is LEGAL and prints its
     * head rows with no `pattern` row among them — distinct, in exit
     * status and in stderr, from a call that FAILED. run.sh depends on
     * being able to tell those two apart. */
    if (list_source) {
        if (list_syntax || list_definitions || list_verbs || list_families ||
            list_axes || list_limits || explain || count_groups || emit_ir || probe_want) {
            fprintf(stderr, "pcrec: --list-source is a separate query; use one\n");
            return 1;
        }
        if (pattern || outpath) {
            fprintf(stderr, "pcrec: --list-source takes no pattern and no -o "
                            "(it reads the file named by its own value)\n");
            return 1;
        }
        if (flavour) {
            fprintf(stderr, "pcrec: --flavour applies to --list-syntax, "
                            "--list-definitions and --explain only\n");
            return 1;
        }
        /* [DD-13b.W1.1 r46sem finding 24, FIXED] initialized at the call
         * site rather than left to `pcrec_rxt_source_parse`'s own
         * zeroing, which runs BEFORE the `calloc` that can fail — a
         * `calloc` failure returns NULL with `err->msg` already zeroed to
         * "" by that point, so this line prints a bare "pcrec: " with no
         * diagnostic text on out-of-memory. Zeroing here too costs
         * nothing and keeps this call site correct independent of
         * whichever side of its own `calloc` check the callee's own
         * zeroing sits on. */
        pcrec_error serr = { 0 };
        RxtSource *src = pcrec_rxt_source_parse(list_source, &serr);
        if (!src) {
            fprintf(stderr, "pcrec: %s\n", serr.msg);
            return 1;
        }
        char *text = pcrec_rxt_source_tsv(src);
        fputs(text, stdout);
        free(text);
        pcrec_rxt_source_free(src);
        return 0;
    }

    /* --probe-ask drives ONE doorway call and reports the cursor — the
     * check06 channel (§18.2's cursor rule). The doorway REFUSING the
     * construct is a normal, reportable outcome here (exit 0, outcome
     * column says so): probing is not compiling. Only a channel that could
     * not run at all exits nonzero, so the check can tell "measured a
     * refusal" from "measured nothing". */
    if (probe_want) {
        if (list_syntax || list_definitions || list_verbs || list_families || list_axes || list_limits || explain || count_groups) {
            fprintf(stderr, "pcrec: --probe-ask is a separate query; use one\n");
            return 1;
        }
        if (outpath) {
            fprintf(stderr, "pcrec: --probe-ask takes no -o\n");
            return 1;
        }
        if (flavour) {
            fprintf(stderr, "pcrec: --flavour applies to --list-syntax and "
                            "--explain only\n");
            return 1;
        }
        if (!pattern) {
            fprintf(stderr, "pcrec: --probe-ask needs a construct\n");
            return 1;
        }
        /* Two NULLs with different causes (R20/MOD07-1): a port that RAISED
         * fills perr, and gets the compile path's own error shape rather
         * than the usage sentence below — the operator's command line is
         * fine, their pattern is not. */
        pcrec_error perr;
        char *line = pcrec_probe_ask(probe_want, pattern, &perr);
        if (!line && perr.msg[0]) {
            fprintf(stderr, "pcrec: --probe-ask: %s (pattern offset %zu)\n",
                    perr.msg, perr.pos);
            return 1;
        }
        if (!line) {
            fprintf(stderr, "pcrec: --probe-ask: WANT must be claim, verdict "
                            "or result, and the construct must reach a "
                            "doorway (start with '\\', '(?', '(*' or '[' — "
                            "except '(?:', which the base grammar answers "
                            "before any doorway is consulted)\n");
            return 1;
        }
        fputs(line, stdout);
        free(line);
        return 0;
    }

    /* [M4.5c] DD-8's listing. Shaped like --count-groups: it runs the REAL
     * pipeline (nothing less could honestly describe the emitted program) and
     * prints, taking no -o and writing no C. A pattern pcrec refuses is
     * refused here with pcrec_compile's exact diagnostic. */
    if (emit_ir) {
        if (list_syntax || list_definitions || list_verbs || list_families || list_axes || list_limits || explain || count_groups) {
            fprintf(stderr, "pcrec: --emit-ir is a separate query; use one\n");
            return 1;
        }
        if (outpath) {
            fprintf(stderr, "pcrec: --emit-ir takes no -o (it prints the "
                            "listing, not C)\n");
            return 1;
        }
        if (!pattern) {
            fprintf(stderr, "pcrec: --emit-ir needs a pattern\n");
            return 1;
        }
        {
            pcrec_error err;
            char *text = pcrec_emit_ir(pattern, &opt, &err);
            if (!text) {
                fprintf(stderr, "pcrec: %s (pattern offset %zu)\n",
                        err.msg, err.pos);
                return 1;
            }
            fputs(text, stdout);
            free(text);
            return 0;
        }
    }

    if (count_groups) {
        if (list_syntax || list_definitions || list_verbs || list_families || list_axes || list_limits || explain) {
            fprintf(stderr, "pcrec: --count-groups is a separate query; use one\n");
            return 1;
        }
        if (outpath) {
            fprintf(stderr, "pcrec: --count-groups takes no -o\n");
            return 1;
        }
        if (flavour) {
            fprintf(stderr, "pcrec: --flavour applies to --list-syntax and "
                            "--explain only\n");
            return 1;
        }
        if (!pattern) {
            fprintf(stderr, "pcrec: --count-groups needs a pattern\n");
            return 1;
        }
        pcrec_error err;
        int n = pcrec_count_groups(pattern, &err);
        if (n < 0) {
            fprintf(stderr, "pcrec: %s (pattern offset %zu)\n", err.msg, err.pos);
            return 1;
        }
        printf("%d\n", n);
        return 0;
    }

    /* Syntax queries answer from the registry and compile nothing, so they take
     * neither a pattern nor -o. They are checked before the pattern/-o
     * requirement and reject a mixed invocation rather than silently ignoring
     * half of it. */
    if (list_syntax || list_definitions || explain || list_verbs || list_families || list_axes || list_limits) {
        if (list_syntax + list_definitions + list_verbs + list_families + list_axes + list_limits + (explain != NULL) > 1) {
            fprintf(stderr, "pcrec: --list-syntax, --list-definitions, --list-verbs, "
                            "--list-families, --list-axes, --list-limits and --explain "
                            "are separate queries; use one\n");
            return 1;
        }
        if (pattern || outpath) {
            fprintf(stderr, "pcrec: %s takes no pattern and no -o\n",
                    list_syntax      ? "--list-syntax" :
                    list_definitions ? "--list-definitions" :
                    list_verbs       ? "--list-verbs"  :
                    list_families    ? "--list-families" :
                    list_axes        ? "--list-axes" :
                    list_limits      ? "--list-limits" : "--explain");
            return 1;
        }
        /* --list-verbs has no flavour axis: the verb tables record what libpcre2
         * accepts, and there is exactly one PCRE2. When SR-7 adds a flavour that
         * genuinely differs here, this is where it grows one.
         *
         * [M6.6.2 wave F] --list-families has none EITHER, and for a reason of
         * its own rather than by inheritance: a family is a grouping OF rows,
         * so filtering its members by flavour would print families whose
         * membership silently depends on the filter -- and `built`, which this
         * view ANDs over the members, would then mean something different per
         * invocation. When SR-7 lands, the honest shape is a flavour filter
         * applied to the members with the family line stating it.
         *
         * [CHK-2] --list-axes has none either, and for --list-verbs'/
         * --list-families' reason rather than a new one: it reports what THIS
         * BUILD of pcrec (one flavour's worth of machinery, always) thinks its
         * own axes are, never a claim about a flavour's syntax.
         *
         * [DD-11.2] --list-definitions DOES take --flavour, and joins
         * --list-syntax/--explain below rather than this exclusion list —
         * r43 K6's ruling, reversing the first design pass's "no": it walks
         * the SAME RegRows --list-syntax does, and an unfiltered dump would
         * print a definition for a construct --list-syntax --flavour=X says
         * does not exist under that flavour.
         *
         * [LIM-1] --list-limits joins --list-axes' reason exactly: it
         * reports what THIS BUILD's own limits.def says, never a claim
         * about a flavour's syntax — a numeric limit has no flavour axis
         * at all. */
        if ((list_verbs || list_families || list_axes || list_limits) && flavour) {
            fprintf(stderr, "pcrec: --flavour applies to --list-syntax, "
                            "--list-definitions and --explain only\n");
            return 1;
        }
        if (list_verbs) {
            char *v = pcrec_syntax_verbs();
            fputs(v, stdout);
            free(v);
            return 0;
        }
        if (list_families) {
            char *v = pcrec_syntax_families();
            fputs(v, stdout);
            free(v);
            return 0;
        }
        if (list_axes) {
            char *v = pcrec_axes_tsv();
            fputs(v, stdout);
            free(v);
            return 0;
        }
        if (list_limits) {
            char *v = pcrec_limits_tsv();
            fputs(v, stdout);
            free(v);
            return 0;
        }
        unsigned fl = 0;
        if (flavour && !(fl = pcrec_flavour_by_name(flavour))) {
            fprintf(stderr, "pcrec: unknown flavour '%s' (only 'pcre2' exists; "
                            "more arrive with SR-7)\n", flavour);
            return 1;
        }
        if (list_definitions) {
            char *v = pcrec_definitions_tsv(fl);
            fputs(v, stdout);
            free(v);
            return 0;
        }
        int ndissent = 0;
        pcrec_error eerr = { .msg = { 0 }, .pos = 0 };
        char *text = list_syntax ? pcrec_syntax_tsv(fl)
                                 : pcrec_syntax_explain(explain, fl, &ndissent,
                                                        &eerr);
        /* A DOORWAY THAT RAISED (R20/MOD07-1), not a query nothing matches:
         * an enabled module port parsed the query text for real and that
         * parse failed. Same shape a compile error gets, so an operator who
         * has seen one recognises the other. */
        if (!text && eerr.msg[0]) {
            fprintf(stderr, "pcrec: --explain: %s (pattern offset %zu)\n",
                    eerr.msg, eerr.pos);
            return 1;
        }
        if (!text) {
            /* --explain only; the TSV always has rows */
            fprintf(stderr, "pcrec: no construct matches '%s' — it is either "
                            "base syntax or not a construct pcrec knows\n",
                    explain);
            return 1;
        }
        fputs(text, stdout);
        free(text);
        /* EXIT 3 IS A DISSENT (MOD-0.7): --explain prints the registry's
         * declared attribution beside the live doorway's answer and compares
         * them per row. A disagreement is a DEFECT SURFACED, not a bad
         * question, and a script must be able to tell the two apart — exit 1
         * already means "your query could not be answered", and every other
         * misuse of this CLI is exit 1 too. The full answer still goes to
         * stdout; the failing rows carry `agree  DISSENT: <clause>: …`. */
        if (ndissent > 0) {
            /* the VERB agrees too (R20/MOD07-9): "1 row DISAGREES", "2 rows
             * DISAGREE". The old form pluralized only the noun. */
            fprintf(stderr, "pcrec: --explain: %d row%s DISAGREE%s with the live "
                            "doorway (see the 'agree' lines) — this is a pcrec "
                            "defect, not a bad query\n",
                    ndissent, ndissent == 1 ? "" : "s",
                    ndissent == 1 ? "S" : "");
            return 3;
        }
        return 0;
    }
    if (flavour) {
        fprintf(stderr, "pcrec: --flavour applies to --list-syntax and "
                        "--explain only\n");
        return 1;
    }

    if (!pattern || !outpath) {
        fprintf(stderr, "pcrec: pattern and -o are required\n");
        usage(stderr);
        return 1;
    }

    int to_stdout = !strcmp(outpath, "-");
    char *hpath = NULL;
    if (!to_stdout) {
        size_t len = strlen(outpath);
        hpath = malloc(len + 3);
        if (!hpath) { perror("malloc"); return 1; }
        strcpy(hpath, outpath);
        if (len > 2 && !strcmp(hpath + len - 2, ".c")) strcpy(hpath + len - 2, ".h");
        else strcat(hpath, ".h");
        opt.header_name = base_name(hpath);
    }

    pcrec_output out;
    pcrec_error err;
    if (pcrec_compile(pattern, &opt, &out, &err) != 0) {
        fprintf(stderr, "pcrec: %s (pattern offset %zu)\n", err.msg, err.pos);
        free(hpath);
        return 1;
    }

    int rc = 0;
    if (to_stdout) {
        fputs(out.c_src, stdout);
    } else {
        if (write_file(outpath, out.c_src) != 0 ||
            write_file(hpath, out.h_src) != 0)
            rc = 1;
    }
    pcrec_output_free(&out);
    free(hpath);
    return rc;
}
