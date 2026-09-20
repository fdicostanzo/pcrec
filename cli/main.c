/* pcrec command-line interface.
 *
 *   pcrec [-p PREFIX] [-e byte|utf8] [-i] [--emit-main] -o OUT.c 'PATTERN'
 *   pcrec -o - 'PATTERN'      self-contained C on stdout (no header file)
 */

#include <limits.h>
#include <stdarg.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#include "pcrec.h"
/* The syntax-query modes read the construct registry, which is internal: the
 * CLI and the test suite are its only consumers, so it is not part of the
 * public surface (see src/dump/syntax_dump.c). main.c touches no registry
 * type — it calls two functions that hand back finished text. */
#include "core/internal.h"
/* [M5-SEAM] the ENCODING REGISTRY: the one table the `byte`/`utf8` names are
 * defined by, so this file maps no encoding name of its own (see D58/SR-10). */
#include "enc/enc.h"

/* ---- THE CLI DIAGNOSTIC CHANNEL ([REVW.1] wave 1) -----------------------
 *
 * ONE diagnostic: `"pcrec: "`, the message, a newline, on stderr. Returns 1,
 * so a call site that refuses stays `return cli_err(...)`; a site that only
 * WARNS ignores it.
 *
 * IT IS CLI-LOCAL AND STAYS THAT WAY. The library does not print — every
 * refusal below `lib/pcrec.h` travels as a `pcrec_error`, and `src/`'s only
 * stdio is the four dump surfaces handing back finished text. That separation
 * is already right and this channel must not become the crack in it.
 *
 * D26: THE WORDING DOES NOT MOVE. This function owns the PREFIX and the
 * NEWLINE — the two things 73 call sites were each spelling by hand — and
 * nothing else. Every word of every message is the word it was.
 *
 * NO `where` PARAMETER. Lens 2's sketch and the wave-1 charter both give this
 * a leading `const char *where` rendered as `" (<where>)"`; MEASURED on this
 * tree, not one of the 79 stderr sites has that shape — the parentheticals in
 * these messages are prose inside the sentence, at a dozen different
 * positions, and none of them is a location this channel could compose. A
 * parameter with no caller is machinery ahead of a measured need (D77), so it
 * is not built; the day a site wants one, it is a two-line change here. */
static int cli_err(const char *fmt, ...) __attribute__((format(printf, 1, 2)));
static int cli_err(const char *fmt, ...)
{
    va_list ap;
    fputs("pcrec: ", stderr);
    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    va_end(ap);
    fputc('\n', stderr);
    return 1;
}

/* [ART-SIZE] Parse a RAISE-ONLY size override. Shared by both caps so the
 * two cannot drift in what they accept, and so the "below the default is a
 * malformed option" rule has exactly one implementation. */
static int parse_raise_only(const char *arg, const char *flag,
                            unsigned long long floor, uint64_t *slot)
{
    char *end = NULL;
    unsigned long long v = strtoull(arg, &end, 10);
    if (!end || *end || arg[0] == '-' || v == 0) {
        cli_err("%s wants a positive integer (got '%s')",
                flag, arg);
        return 1;
    }
    if (v < floor) {
        cli_err("%s is RAISE-ONLY: %llu is below the built-in "
                        "limit of %llu. These overrides exist to let a caller "
                        "accept a larger artifact, never to make a build "
                        "refuse one it would have accepted",
                flag, v, floor);
        return 1;
    }
    *slot = (uint64_t)v;
    return 0;
}

/* [LIM-2] N1 THE GENERAL RAISE-ONLY SURFACE (D84 ruling 1, generalized here
 * rather than hand-copied four more times). `parse_raise_only` above still
 * owns the ONE "below the built-in default is a malformed option" rule and
 * its ONE error message; this table is what DISPATCHES an argv token to it —
 * a flag's argv spelling, the built-in floor it may only rise above, and the
 * `pcrec_options` field it writes, addressed by `offsetof` rather than a
 * hand-written setter. A seventh raise-only cap costs one row here, not one
 * more `else if` block in `cli_parse`'s chain below.
 *
 * `PCREC_MAX_DFA_STATES_TABLE` carries NO row: its consumer is the
 * table-engine's EMITTED cell type (a C `short`/`unsigned short`,
 * src/gen/emit_dfa.c), so raising the CHECK here past what that format can
 * represent would be a lever whose number the artifact cannot honour — see
 * limits.def's own comment on that row and docs/spec/limits.md §3.6. */
typedef struct {
    const char *flag;   /* argv spelling, no trailing '=' */
    unsigned long long floor;
    size_t offset;      /* offsetof(pcrec_options, <field>) */
} RaiseOnlyLimit;

static const RaiseOnlyLimit raise_only_limits[] = {
    { "--max-emit-code-bytes", PCREC_MAX_VM_EMIT_CODE_BYTES,
      offsetof(pcrec_options, max_emit_code_bytes) },
    { "--max-emit-bytes",      PCREC_MAX_EMIT_BYTES,
      offsetof(pcrec_options, max_emit_bytes) },
    { "--max-nfa-states",      PCREC_MAX_NFA_STATES,
      offsetof(pcrec_options, max_nfa_states) },
    { "--max-dfa-states-goto", PCREC_MAX_DFA_STATES_GOTO,
      offsetof(pcrec_options, max_dfa_states_goto) },
    { "--max-subset-elems",    PCREC_MAX_SUBSET_ELEMS,
      offsetof(pcrec_options, max_subset_elems) },
    { "--max-auto-dfa-elems",  PCREC_MAX_AUTO_DFA_ELEMS,
      offsetof(pcrec_options, max_auto_dfa_elems) },
};
#define N_RAISE_ONLY_LIMITS \
    ((int)(sizeof raise_only_limits / sizeof raise_only_limits[0]))

/* Is argv token `a` spelled "<flag>=<value>" for one of the rows above?
 * Returns the row index, or -1. Called once per argv token regardless of
 * match — the same shape every other flag in this file's `else if` chain
 * already costs on a non-matching token. */
static int raise_only_match(const char *a)
{
    for (int i = 0; i < N_RAISE_ONLY_LIMITS; i++) {
        size_t n = strlen(raise_only_limits[i].flag);
        if (!strncmp(a, raise_only_limits[i].flag, n) && a[n] == '=')
            return i;
    }
    return -1;
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
          "  --pattern-esc  the PATTERN operand is the .rxt format's quoted-\n"
          "                 escape form (\\\" \\\\ \\n \\t \\r \\f \\v \\xHH), decoded by\n"
          "                 pcrec's own decoder. Lets a multi-line or high-byte\n"
          "                 pattern be written on one line; \\x00 is refused (K9)\n"
          "  --no-captures  emit a matcher with no capture output (RX_NCAPS 1,\n"
          "                 DFA engine). Captures are ON by default; this is\n"
          "                 the generation axis that recovers the pre-M4.5\n"
          "                 pure-DFA artifact for a group-bearing pattern\n"
          "  --emit-ir      print the VM PROGRAM LISTING for the pattern and exit:\n"
          "                 labels, choice points with their preference order,\n"
          "                 capture slot assignments, island boundaries and\n"
          "                 callout sites. A query -- takes no -o, emits no C.\n"
          "                 Produced by the emitter's own walk, so it cannot\n"
          "                 drift from the code it describes. TAB-separated,\n"
          "                 one #section per table with its own column header\n"
          "                 (docs/spec/ir_listing.md); a DEBUG listing, VM-only\n"
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
          "  --tune=N       the SPEED-VS-SIZE DIAL: -2 | -1 | 0 | 1 | 2, or\n"
          "                 equivalently min-size | size | balanced | speed |\n"
          "                 max-speed (default 0/balanced, today's defaults\n"
          "                 byte for byte). A NEGATIVE value needs the = form\n"
          "                 (--tune=-2); the aliases have no leading dash and\n"
          "                 are the preferred spelling. Out of range is an\n"
          "                 error, never a clamp. Every position answers\n"
          "                 identically; the artifact stamps <PREFIX>_TUNE.\n"
          "                 The per-position switch table is docs/spec/\n"
          "                 tuning.md section 5\n"
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
          "  --max-nfa-states=N, --max-dfa-states-goto=N, --max-subset-elems=N\n"
          "                 [LIM-2] RAISE three compile-time construction\n"
          "                 budgets (NFA states, the computed-goto attempt\n"
          "                 engine's DFA state ceiling, and K7's subset-\n"
          "                 construction element total). Same raise-only\n"
          "                 rule as above. Defaults 131,072 / 10,000 /\n"
          "                 48,000,000. --engine=dfa pays whichever of\n"
          "                 these applies in full; see docs/spec/limits.md\n"
          "  --max-auto-dfa-elems=N\n"
          "                 [LIM-2] RAISE the AUTO route's own DFA-attempt\n"
          "                 work budget (K7 elements; default 30,000,000,\n"
          "                 below --max-subset-elems by design). Only\n"
          "                 applies under --engine=auto: over budget there,\n"
          "                 the DFA attempt is abandoned and the compile\n"
          "                 falls back to the VM. --engine=dfa is unaffected\n"
          "                 and pays --max-subset-elems' own cap instead\n"
          "  --backtrack-frames=N  the resume-stack capacity. Default: sized\n"
          "                 exactly where the pattern's depth is statically\n"
          "                 bounded, a stamped default otherwise\n"
          "  -h, --help     this help\n"
          "\n"
          "compiling from a .rxt SOURCE file (docs/spec/rxt_format.md):\n"
          "  --source FILE  compile the `target` lines of a .rxt source. Each\n"
          "                 target is its own artifact under its own prefix,\n"
          "                 built from the pattern block its definition names,\n"
          "                 under the configs its `with` list composes. Takes\n"
          "                 no pattern argument: the file holds the patterns.\n"
          "                 -o names a FILE for one target, an existing\n"
          "                 DIRECTORY for several (<dir>/<prefix>.c and .h per\n"
          "                 target), or '-' for one target on stdout. A file\n"
          "                 that declares no target is a library and builds\n"
          "                 nothing, at exit 0\n"
          "  --target NAME  build only the target with this prefix\n"
          "  --lib-path DIR  a directory to resolve `lib \"path\"` references\n"
          "                 against. Repeatable; order is the search order,\n"
          "                 after the source file's own directory\n"
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
          "  --list-schema     TSV of the .rxt FORMAT's own schema\n"
          "                    ([DD-13b.W23.1]): one line per (scope, line\n"
          "                    kind), with its value shape, what may be\n"
          "                    indented under it, cardinality, constraints and\n"
          "                    which readers validate it, plus a `surface`\n"
          "                    section naming what it does NOT validate and\n"
          "                    why. No --flavour axis\n"
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
 * The name is looked up in the ENCODING REGISTRY (src/enc/) rather than
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
        cli_err("unknown encoding '%s' (want %s)", v, names);
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
    if (ferror(f)) { fclose(f); fprintf(stderr, "%s: write error\n", path); return -1; }
    if (fclose(f) != 0) { perror(path); return -1; }
    return 0;
}

/* [DD-13b.W1.2] EVERY OPTION THIS CLI UNDERSTANDS, IN ONE PLACE.
 *
 * These were locals of `main` until a `.rxt` source's `config` block gained
 * a `pcrec <raw>` line, which has to mean the SAME thing the command line
 * means — a flag that reads one way on the command line and another in a
 * config block is exactly the two-homes drift D24 exists to prevent, one
 * surface over. So the argument loop became `cli_parse` over this struct
 * and the config block is a second CALLER of it, never a second parser.
 *
 * THE LAYOUT IS LOAD-BEARING: `opt` is FIRST and everything else follows,
 * because a config block may set the compile options and nothing else, and
 * `cli_extras_clean` checks that by testing the bytes PAST `opt` against
 * zero. Written as a field list it would be a list to keep in step with
 * this struct; written as one span it covers a field added tomorrow by an
 * author who never reads this comment. `saw_prefix` is in the tail rather
 * than being inferred from `opt.prefix` for exactly that reason — `-p` sets
 * a field inside `opt`, so the span cannot see it, and this is how it is
 * brought back under the same guard. */
typedef struct {
    pcrec_options opt;

    const char *outpath;
    const char *pattern;
    int         list_syntax;
    int         list_definitions;
    int         list_verbs;
    int         list_families;
    int         list_axes;
    int         list_limits;
    int         list_schema;
    int         count_groups;
    int         emit_ir;
    /* [DD-13b.W23.3] the pattern OPERAND is the `.rxt` format's
     * quoted-escape form, decoded by pcrec's one decoder (§2.19). */
    int         pattern_esc;
    int         saw_prefix;
    int         want_help;
    const char *explain;
    const char *flavour;
    const char *probe_want;
    const char *features;
    const char *list_source;
    /* [DD-13b.W1.2] the `.rxt` SOURCE surface */
    const char *source;
    const char *target;
    const char **libdirs;
    size_t      nlibdirs, libcap;
} CliState;

/* [REVW.4] wave 4 (L11-F4) — THE MODE RELATION, WRITTEN ONCE.
 *
 * `main` dispatches on MODES: the seven registry queries, `--explain`,
 * `--count-groups`, `--emit-ir`, `--probe-ask`, `--list-source`, `--source`
 * and `--flavour`. Each mode that RETURNS from `main` on its own first
 * refuses the other modes it does not compose with — and until this wave
 * that refusal was spelled out SIX TIMES as an `||` chain, with FOUR
 * DIFFERENT memberships (13 / 12 / 9 / 8 flags), no two of which a reader
 * could compare without counting. Adding a mode meant remembering six
 * chains and knowing which of the four each one belongs to; the review's
 * finding is that the arrangement is correct today only because of BLOCK
 * ORDER.
 *
 * ONE TABLE of modes, ONE activity test, and a NAMED MASK per site. The
 * memberships below are the NARROWEST-PER-SITE, i.e. exactly what each site
 * accepts and refuses today (Frank's ruling for this item): this is an
 * extraction, not a contract change, and `docs/spec/cli.md` is unchanged by
 * it. Widening every site to the union would be a real behaviour change —
 * `--probe-ask --flavour=pcre2` is accepted today and the union would refuse
 * it — and it is PROPOSED in docs/dev/lanes/w4_report.md rather than built.
 *
 * THE SUMMED-COUNT RELATION AT THE SEVEN-QUERY SITE IS NOT FOLDED IN, and
 * that is also ruled. "Is some OTHER mode active" and "is at most one of
 * these co-equal flags set" are two different relations over one set; one
 * mechanism per relation kind, so the count relation gets
 * `cli_modes_count` and keeps its own shape. */
#define CLI_MODE_TABLE(X)                                                \
    X(LIST_SYNTAX,      list_syntax,      INT, "--list-syntax")          \
    X(LIST_DEFINITIONS, list_definitions, INT, "--list-definitions")     \
    X(LIST_VERBS,       list_verbs,       INT, "--list-verbs")           \
    X(LIST_FAMILIES,    list_families,    INT, "--list-families")        \
    X(LIST_AXES,        list_axes,        INT, "--list-axes")            \
    X(LIST_LIMITS,      list_limits,      INT, "--list-limits")          \
    X(LIST_SCHEMA,      list_schema,      INT, "--list-schema")          \
    X(EXPLAIN,          explain,          PTR, "--explain")              \
    X(COUNT_GROUPS,     count_groups,     INT, "--count-groups")         \
    X(EMIT_IR,          emit_ir,          INT, "--emit-ir")              \
    X(PROBE_ASK,        probe_want,       PTR, "--probe-ask")            \
    X(LIST_SOURCE,      list_source,      PTR, "--list-source")          \
    X(SOURCE,           source,           PTR, "--source")               \
    X(FLAVOUR,          flavour,          PTR, "--flavour")

typedef enum {
#define CLI_MODE_ENUM_ROW(id, field, kind, spelling) CM_##id,
    CLI_MODE_TABLE(CLI_MODE_ENUM_ROW)
#undef CLI_MODE_ENUM_ROW
    CM_N
} CliModeId;

#define CMB(id) (1u << CM_##id)

/* The two field SHAPES a mode is stored in: a flag, and a value-bearing
 * option whose presence IS the mode. The table's `kind` column dispatches
 * here, so `cli_modes_active` has no per-mode line of its own. */
#define CLI_MODE_LIVE_INT(v) ((v) != 0)
#define CLI_MODE_LIVE_PTR(v) ((v) != NULL)

static unsigned cli_modes_active(const CliState *st)
{
    unsigned m = 0u;
#define CLI_MODE_TEST_ROW(id, field, kind, spelling) \
    if (CLI_MODE_LIVE_##kind(st->field)) m |= CMB(id);
    CLI_MODE_TABLE(CLI_MODE_TEST_ROW)
#undef CLI_MODE_TEST_ROW
    return m;
}

/* The FIRST active mode's own spelling, in table order — which is the order
 * the hand-written conditional ladder it replaces used. */
static const char *cli_mode_name(unsigned modes)
{
#define CLI_MODE_NAME_ROW(id, field, kind, spelling) \
    if (modes & CMB(id)) return spelling;
    CLI_MODE_TABLE(CLI_MODE_NAME_ROW)
#undef CLI_MODE_NAME_ROW
    return "";
}

static int cli_modes_count(unsigned modes)
{
    int n = 0;
    for (; modes; modes >>= 1) n += (int)(modes & 1u);
    return n;
}

/* THE FOUR MEMBERSHIPS, each named for the site that owns it. Every one is
 * built from the one below it, so the nesting a reader had to infer by
 * comparing six `||` chains is now the definition itself. */

/* The seven registry queries plus `--explain`: they answer from the registry
 * and compile nothing, so they take no pattern and no -o. */
#define CLI_MODES_REGISTRY_QUERY                                          \
    (CMB(LIST_SYNTAX) | CMB(LIST_DEFINITIONS) | CMB(LIST_VERBS) |         \
     CMB(LIST_FAMILIES) | CMB(LIST_AXES) | CMB(LIST_LIMITS) |             \
     CMB(LIST_SCHEMA) | CMB(EXPLAIN))

/* `--count-groups` refuses the registry queries and nothing else: it TAKES
 * a pattern, so it composes with the pattern-bearing modes below it. */
#define CLI_MODES_VS_COUNT_GROUPS CLI_MODES_REGISTRY_QUERY

/* `--probe-ask` and `--emit-ir` additionally refuse `--count-groups` — the
 * other pattern-bearing query — but not each other, which is block order
 * doing the work and is preserved exactly as it stands. */
#define CLI_MODES_VS_PATTERN_QUERY (CLI_MODES_REGISTRY_QUERY | CMB(COUNT_GROUPS))

/* `--list-source` READS a `.rxt` file: it refuses every query above plus the
 * other two pattern-bearing ones and `--source`, which COMPILES one.
 * `--flavour` is deliberately absent — that site refuses it separately, with
 * its own applies-to diagnostic, which is a different rule. */
#define CLI_MODES_VS_LIST_SOURCE                                          \
    (CLI_MODES_VS_PATTERN_QUERY | CMB(EMIT_IR) | CMB(PROBE_ASK) | CMB(SOURCE))

/* `--source` COMPILES a `.rxt` file and refuses every query surface there
 * is, `--flavour` among them — the one membership that includes it. */
#define CLI_MODES_VS_SOURCE                                               \
    (CLI_MODES_VS_PATTERN_QUERY | CMB(EMIT_IR) | CMB(PROBE_ASK) |         \
     CMB(LIST_SOURCE) | CMB(FLAVOUR))

/* Everything past `opt` is zero — i.e. this invocation asked for compile
 * options and nothing else. The comparison is over the raw bytes of the
 * tail, which is well defined here because every `CliState` in this file is
 * `memset` to zero before a field is assigned, so padding is zero too. */
static int cli_extras_clean(const CliState *st)
{
    const unsigned char *p = (const unsigned char *)st + sizeof st->opt;
    size_t n = sizeof *st - sizeof st->opt;
    for (size_t i = 0; i < n; i++) if (p[i]) return 0;
    return 1;
}

static int libdir_push(CliState *st, const char *dir)
{
    if (st->nlibdirs == st->libcap) {
        size_t cap = st->libcap ? st->libcap * 2 : 4;
        const char **v = realloc(st->libdirs, cap * sizeof *v);
        if (!v) { perror("realloc"); return 1; }
        st->libdirs = v;
        st->libcap = cap;
    }
    st->libdirs[st->nlibdirs++] = dir;
    return 0;
}

/* [REVW.4] wave 4 (L2-L2-7, M3) — THE ENGINE VOCABULARY, in one place.
 * `--engine=`'s three-arm `strcmp` ladder, `engine_name`'s three-arm reverse
 * ladder and the `.rxt` `engine` row's own one-value test were three
 * independent spellings of one three-value set. They are one table; the
 * format's VM-ONLY restriction is now stated AS a restriction, applied after
 * the shared parse, rather than implemented as a second, narrower parser. */
static const struct { const char *name; int value; } ENGINE_NAMES[] = {
    { "auto", PCREC_ENGINE_AUTO },
    { "dfa",  PCREC_ENGINE_DFA  },
    { "vm",   PCREC_ENGINE_VM   },
};
#define N_ENGINE_NAMES (sizeof ENGINE_NAMES / sizeof ENGINE_NAMES[0])

static int engine_by_name(const char *v, int *out)
{
    for (size_t i = 0; i < N_ENGINE_NAMES; i++)
        if (!strcmp(v, ENGINE_NAMES[i].name)) { *out = ENGINE_NAMES[i].value; return 0; }
    return 1;
}

static const char *engine_name(int e)
{
    for (size_t i = 0; i < N_ENGINE_NAMES; i++)
        if (ENGINE_NAMES[i].value == e) return ENGINE_NAMES[i].name;
    return "auto";
}

/* [REVW.4] wave 4 (L2-L2-7) — ONE JOIN POLICY for every valid-value MENU a
 * diagnostic in this file prints. `pcrec_enc_names` (src/enc/enc.c) and
 * `pcrec_tune_names` (src/core/tune.c) each render their own registry's menu
 * because the registry is theirs; this is for the menus whose vocabulary is
 * the CLI's own. Its bounded-join policy is those two functions' exactly —
 * an ordered PREFIX rather than a gap, and the separator written under the
 * SAME bound as the name it follows, so a tight cap can never emit a
 * dangling ", " ([REVW.1] wave 1's L10-2).
 *
 * `last` is the connective before the final name (" or " today), because the
 * sentences these menus sit in read "must be auto, dfa or vm" and D26 forbids
 * re-wording a shipped diagnostic to suit a helper. */
static void cli_menu(const char *const *names, size_t n, const char *last,
                     char *buf, size_t cap)
{
    size_t k = 0;
    if (!cap) return;
    buf[0] = 0;
    for (size_t i = 0; i < n; i++) {
        const char *sep = (i == 0) ? "" : (i + 1 == n ? last : ", ");
        size_t ls = strlen(sep), ln = strlen(names[i]);
        if (k + ls + ln + 1 > cap) break;     /* an ordered PREFIX, never a gap */
        memcpy(buf + k, sep, ls); k += ls;
        memcpy(buf + k, names[i], ln); k += ln;
    }
    buf[k] = 0;
}

/* [REVW.4] wave 4 (L1-X10) — ONE bounded-integer VALUE parser for the five
 * `--flag=N` arms that each spelled `strtol`/`strtoll` plus the same
 * no-junk-and-in-range test for themselves.
 *
 * IT DELIBERATELY DOES NOT REJECT AN EMPTY VALUE OF ITS OWN ACCORD, and that
 * is measured rather than assumed: `strtol("")` returns 0 leaving `*end` at
 * the terminator, so today `--unroll=`, `--step-budget=` and
 * `--backtrack-frames=` are refused by their RANGE (0 is below every one of
 * their floors) while `--vm-entry-shape=` is ACCEPTED as rung 0, auto. An
 * emptiness test here would be a fourth behaviour change nobody asked for.
 *
 * The DIAGNOSTIC stays at each call site: every one of the five names its own
 * range and its own advice, and D26 forbids folding five shipped sentences
 * into one. What is shared is the RULE, which is what was repeated. */
static int cli_int_value(const char *s, long long lo, long long hi, long long *out)
{
    char *end = NULL;
    long long v = strtoll(s, &end, 10);
    if (!end || *end || v < lo || v > hi) return 1;
    *out = v;
    return 0;
}

/* [REVW.4] wave 4 (D111, L1-X9) — THE OPTIMIZATION-AXIS GRAMMAR, in one
 * loop over `src/core/axes.def`.
 *
 * Twenty-two `else if (!no_more_opts && !strcmp(a, "-fno-X")) opt.flags |=
 * PCREC_NO_X;` arms stood here, each one line of grammar under a paragraph of
 * prose, and their flag-text-to-bit pairing was one of the THREE hand-
 * maintained spellings of the axis table that two `awk` scrapers existed to
 * reconcile. The prose did not move far: every one of those paragraphs said
 * "this axis is deny-only / a force pair, and here is why — see
 * lib/pcrec.h", which is a fact about the AXIS and now lives on its row.
 *
 * Returns 1 when `a` was an axis spelling and the bit was set, 0 otherwise —
 * so the caller's chain reads as one arm and an unknown `-f...` still falls
 * through to the unknown-option diagnostic, unchanged. Order within the
 * chain is immaterial: every spelling here is an exact `strcmp` against a
 * distinct literal. */
static int cli_axis_apply(const char *a, uint64_t *flags)
{
#define PCREC_AXIS(dm, df, fm, ff, defst)                                 \
    if ((dm) && (df)[0] && !strcmp(a, (df))) { *flags |= (dm); return 1; } \
    if ((fm) && (ff)[0] && !strcmp(a, (ff))) { *flags |= (fm); return 1; }
#include "core/axes.def"
    return 0;
}

/* The pattern OPERAND: exactly one, anywhere in the argv. Its own function
 * because `cli_parse` reaches it from TWO places — after `--`, and as the
 * option chain's own fall-through — and duplicating four lines to save a
 * helper is how a rule ends up with two spellings. */
static int cli_operand(CliState *st, const char *a, const char *where)
{
    if (!st->pattern) { st->pattern = a; return 0; }
    cli_err("exactly one pattern expected (%s)", where);
    return 1;
}

/* THE ONE OPTION PARSER (w1_impl §1.5). `argv`/`argc` exclude argv[0].
 * `where` names the surface for diagnostics — "command line", or a config
 * block — and changes nothing else: both callers get the same grammar, the
 * same values and the same refusals. */
static int cli_parse(int argc, char **argv, CliState *st, const char *where)
{
    pcrec_options opt = st->opt;
    int no_more_opts = 0;
    for (int i = 0; i < argc; i++) {
        const char *a = argv[i];
        /* [LIM-2] N1: computed once per token so the dispatch below and its
         * body read the SAME match rather than re-scanning the table. */
        const int rom_idx = raise_only_match(a);
        /* [REVW.4] wave 4 (L11-F3) — THE `--` GUARD, WRITTEN ONCE.
         *
         * Every arm of the chain below used to re-type the same conjunct for
         * itself: 59 times before this wave, 37 after item 4 retired the axis
         * arms. The repetition was a named CORRECTNESS HAZARD, not a tidiness
         * one — a new arm written without the conjunct silently breaks `--`
         * for that one flag, and nothing structural reminded an author to add
         * it. Handling the after-`--` case HERE, once, with a `continue`,
         * makes the reminder structural instead: reaching the chain at all now
         * MEANS options are still live, so an arm cannot forget a guard it
         * does not have.
         *
         * The chain's own fall-through still reaches the operand, for an
         * argument that is neither an option nor after `--`. */
        if (no_more_opts) {
            if (cli_operand(st, a, where) != 0) return 1;
            continue;
        }
        if (!strcmp(a, "--")) no_more_opts = 1;
        /* `-h` sets a FLAG rather than printing and exiting, because this
         * function has a second caller: a `config` block's `pcrec -h` must
         * not print usage and exit 0 in the middle of a compile. The flag
         * lives in the tail of `CliState`, so `cli_extras_clean` refuses it
         * there with no clause of its own. */
        else if ((!strcmp(a, "-h") || !strcmp(a, "--help")))
            st->want_help = 1;
        else if (!strcmp(a, "--emit-main")) opt.flags |= PCREC_EMIT_MAIN;
        else if (!strcmp(a, "-i")) opt.flags |= PCREC_CASELESS;
        /* [M4.5b] the generation axes engine_m4.md §4.6/§5.3/§5.6 name.
         * `--engine=` takes its value with `=` rather than as a separate
         * argument because it is a MODE, not a file or a name — and the
         * separate-argument forms above (-o/-p/-e) all take one. */
        else if (!strcmp(a, "--no-captures"))
            opt.flags |= PCREC_NO_CAPTURES;
        else if (!strcmp(a, "--trace"))
            opt.flags |= PCREC_TRACE;
        else if (!strcmp(a, "--emit-ir")) st->emit_ir = 1;
        else if (!strcmp(a, "--pattern-esc"))
            st->pattern_esc = 1;
        else if (!strcmp(a, "--fno-step-budget"))
            opt.step_budget = PCREC_STEP_BUDGET_NONE;
        /* [REVW.4] wave 4 (D111): THE TWENTY-TWO AXIS SPELLINGS, one arm.
         * `cli_axis_apply` walks `src/core/axes.def`, the one home of each
         * axis's bit, its `-fno-X` / `-fX` spellings and its default
         * polarity. An unknown `-f...` returns 0 here and falls through to
         * the unknown-option diagnostic below exactly as it always did. */
        else if (cli_axis_apply(a, &opt.flags)) { }
        /* [ENG-BREP] K, the counter rung's value parameter. One per artifact,
         * never per quantifier (D47 ADDENDUM). */
        else if (!strncmp(a, "--unroll=", 9)) {
            long long v;
            if (cli_int_value(a + 9, 1, 4096, &v) != 0) {
                cli_err("--unroll wants an integer in %d..%d "
                                "(got '%s')", 1, 4096, a + 9);
                return 1;
            }
            opt.unroll_k = (int)v;
        }
        /* [CC-DIFF] STEP 2 `--vm-entry-shape=N` — the VM entry chain's rung,
         * an ORDINAL in the dial's own direction (1 min size .. 4 max speed),
         * `--unroll=`'s value-parameter shape rather than a `-f` bit. 0 is
         * AUTO, the default, where the size term decides; naming it
         * explicitly is legal and means the same thing. A rung this artifact
         * cannot legally take is a SELECTION OUTCOME, not a refusal — see
         * lib/pcrec.h's `vm_entry_shape` and docs/spec/tuning.md §2.21. */
        else if (!strncmp(a, "--vm-entry-shape=", 17)) {
            long long v;
            if (cli_int_value(a + 17, 0, PCREC_VM_ENTRY_INLINE, &v) != 0) {
                /* [REVW.4] wave 4: the RUNG MENU is rendered from
                 * `src/core/tune.c`'s own name table, which `src/gen/
                 * emit_vm.c`'s `<PREFIX>_VM_ENTRY_SHAPE` stamp also reads —
                 * it was hand-typed here, a THIRD spelling of five words. */
                char rungs[128];
                pcrec_vm_entry_shape_names(rungs, sizeof rungs);
                cli_err("--vm-entry-shape wants an integer in "
                                "0..%d (%s; got '%s')",
                        PCREC_VM_ENTRY_INLINE, rungs, a + 17);
                return 1;
            }
            opt.vm_entry_shape = (int)v;
        }
        /* [OPT-DIAL] `--tune=N` — the speed-vs-size dial, an ORDINAL in
         * -2..+2 with five mnemonic aliases accepted on equal terms
         * (`src/core/tune.c` owns both spellings, so the CLI cannot drift
         * from the stamp). `--vm-entry-shape=`'s value-parameter shape.
         *
         * THE `=` FORM IS REQUIRED FOR A NEGATIVE VALUE, and the separated
         * form is REFUSED BY NAME rather than accepted by look-ahead:
         * `--tune -2` is two tokens whose second begins with `-`, which
         * every argv parser in this CLI would have to special-case, and a
         * look-ahead that guessed would make `--tune -o out.c` mean
         * something nobody typed. The diagnostic names the `=` spelling.
         *
         * OUT OF RANGE IS AN ERROR, NEVER A CLAMP. A clamp would let a
         * caller believe they had asked for something the artifact does not
         * have, and `<PREFIX>_TUNE` exists precisely so an artifact says how
         * it was built. */
        else if (!strncmp(a, "--tune=", 7)) {
            int v = 0;
            if (pcrec_tune_parse(a + 7, &v) != 0) {
                /* [REVW.4] wave 4 (L2-L2-7): the menu is RENDERED from
                 * `src/core/tune.c`'s own alias table, which D103 makes the
                 * dial's one home — it was hand-typed here, a second
                 * spelling that a sixth position would have left stale. */
                char menu[128];
                pcrec_tune_names(menu, sizeof menu);
                cli_err("--tune wants -2..2 or one of %s (got '%s')",
                        menu, a + 7);
                return 1;
            }
            opt.tune = v;
        }
        else if (!strcmp(a, "--tune")) {
            cli_err("--tune takes its value with '=' "
                    "(--tune=-2, --tune=min-size)");
            return 1;
        }
        /* [M5-SEAM] (D58) `--encoding=` is the long spelling of `-e`, in the
         * `=value` MODE form `--engine=` already uses (the separate-argument
         * forms are for files and names). Both spellings reach the same
         * lookup, so they cannot drift. */
        else if (!strncmp(a, "--encoding=", 11)) {
            if (set_encoding(&opt, a + 11) != 0) return 1;
        }
        else if (!strncmp(a, "--engine=", 9)) {
            const char *v = a + 9;
            int want;
            if (engine_by_name(v, &want) != 0) {
                /* [REVW.4] wave 4: the menu is the TABLE's, rendered with
                 * this file's one join policy, so a fourth engine name would
                 * appear here without an edit. */
                const char *names[N_ENGINE_NAMES];
                char menu[64];
                for (size_t k = 0; k < N_ENGINE_NAMES; k++) names[k] = ENGINE_NAMES[k].name;
                cli_menu(names, N_ENGINE_NAMES, " or ", menu, sizeof menu);
                cli_err("--engine must be %s (got '%s')", menu, v);
                return 1;
            }
            opt.engine = want;
        }
        else if (!strncmp(a, "--step-budget=", 14)) {
            long long v;
            if (cli_int_value(a + 14, 1, LLONG_MAX, &v) != 0) {
                cli_err("--step-budget wants a positive integer "
                                "(use --fno-step-budget for no counter)");
                return 1;
            }
            opt.step_budget = v;
        }
        /* [ENG-BREP counter-K] The value knob for the THIRD bound. There is
         * deliberately no `--fno-work-budget`: v1 rides ONE existence gate, so
         * `--fno-step-budget` above suppresses both counters (D49). */
        else if (!strncmp(a, "--work-budget=", 14)) {
            long long v;
            if (cli_int_value(a + 14, 1, LLONG_MAX, &v) != 0) {
                cli_err("--work-budget wants a positive integer "
                                "(use --fno-step-budget for no counters)");
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
        else if (rom_idx >= 0) {
            const RaiseOnlyLimit *r = &raise_only_limits[rom_idx];
            uint64_t *slot = (uint64_t *)((char *)&opt + r->offset);
            if (parse_raise_only(a + strlen(r->flag) + 1, r->flag, r->floor,
                                 slot) != 0) return 1;
        }
        /* [OPT-4] THE ADVISORY WARNING, and it is deliberately NOT
         * `parse_raise_only`. The two caps above are raise-only so no caller
         * can manufacture someone else's refusal; a warning has no such
         * authority — the build succeeds either way — so LOWERING it is the
         * whole point for a project that wants earlier notice, and 0 turns it
         * off. Accepting any value is the correct policy here precisely
         * because this option cannot fail a build. */
        else if (!strncmp(a, "--warn-emit-bytes=", 18)) {
            char *end = NULL;
            unsigned long long v = strtoull(a + 18, &end, 10);
            if (!end || *end || a[18] == '\0') {
                cli_err("--warn-emit-bytes wants a "
                                "non-negative integer (0 disables the "
                                "warning)");
                return 1;
            }
            opt.warn_emit_bytes = (uint64_t)v;
        }
        else if (!strncmp(a, "--backtrack-frames=", 19)) {
            long long v;
            if (cli_int_value(a + 19, 1, 1000000, &v) != 0) {
                cli_err("--backtrack-frames wants a positive "
                                "integer (the array is a LOCAL of the search "
                                "entry, so this is stack)");
                return 1;
            }
            opt.frame_capacity = (int)v;
        }
        else if (!strcmp(a, "--list-syntax")) st->list_syntax = 1;
        else if (!strcmp(a, "--list-definitions")) st->list_definitions = 1;
        else if (!strcmp(a, "--list-verbs"))  st->list_verbs = 1;
        else if (!strcmp(a, "--list-families")) st->list_families = 1;
        else if (!strcmp(a, "--list-axes"))   st->list_axes = 1;
        else if (!strcmp(a, "--list-limits")) st->list_limits = 1;
        else if (!strcmp(a, "--list-schema")) st->list_schema = 1;
        else if (!strcmp(a, "--count-groups")) st->count_groups = 1;
        /* [DD-13b.W1.1] `--list-source FILE` — the `.rxt` SOURCE dump.
         * Takes its file as the option's VALUE, like --explain and
         * --probe-ask take theirs, rather than as the bare positional
         * argument: that slot is the PATTERN's, and a query that quietly
         * reinterpreted it would make `pcrec --list-source 'a(b|c)'` read
         * a file named after a regex. */
        else if (!strcmp(a, "--list-source")) {
            if (i + 1 >= argc) {
                cli_err("missing value for %s", a);
                return 1;
            }
            st->list_source = argv[++i];
        }
        else if (!strcmp(a, "--probe-ask")) {
            if (i + 1 >= argc) {
                cli_err("missing value for %s", a);
                return 1;
            }
            st->probe_want = argv[++i];
        }
        else if (!strcmp(a, "--features")) {
            if (i + 1 >= argc) {
                cli_err("missing value for %s", a);
                return 1;
            }
            st->features = argv[++i];
        }
        else if (!strcmp(a, "--explain") || !strcmp(a, "--flavour")) {
            if (i + 1 >= argc) {
                cli_err("missing value for %s", a);
                return 1;
            }
            const char *v = argv[++i];
            if (a[2] == 'e') st->explain = v; else st->flavour = v;
        }
        else if (!strcmp(a, "-o") || !strcmp(a, "-p") || !strcmp(a, "-e")) {
            if (i + 1 >= argc) {
                cli_err("missing value for %s", a);
                return 1;
            }
            const char *v = argv[++i];
            if (a[1] == 'o') st->outpath = v;
            else if (a[1] == 'p') { opt.prefix = v; st->saw_prefix = 1; }
            else if (set_encoding(&opt, v) != 0) return 1;
        }
        /* [DD-13b.W1.2] THE `.rxt` SOURCE SURFACE (S11). All three take
         * their value as a separate argument, like -o/-p/-e and unlike the
         * `=value` MODE flags: a file, a name and a directory are exactly
         * the three things that spelling is for. */
        else if (!strcmp(a, "--source")) {
            if (i + 1 >= argc) {
                cli_err("missing value for %s", a);
                return 1;
            }
            st->source = argv[++i];
        }
        else if (!strcmp(a, "--target")) {
            if (i + 1 >= argc) {
                cli_err("missing value for %s", a);
                return 1;
            }
            st->target = argv[++i];
        }
        /* REPEATABLE, and order is the search order — the one flag in this
         * CLI that accumulates rather than replacing. A single-valued
         * --lib-path would make two libraries an either/or. */
        else if (!strcmp(a, "--lib-path")) {
            if (i + 1 >= argc) {
                cli_err("missing value for %s", a);
                return 1;
            }
            if (libdir_push(st, argv[++i]) != 0) return 1;
        }
        else if (a[0] == '-' && a[1]) {
            cli_err("unknown option '%s' in the %s (use -- "
                            "before a pattern that starts with '-')",
                    a, where);
            if (!strcmp(where, "command line")) usage(stderr);
            return 1;
        }
        else if (cli_operand(st, a, where) != 0) return 1;
    }
    st->opt = opt;
    return 0;
}

/* ------------- [DD-13b.W1.2] compiling from a `.rxt` SOURCE ------------- */

/* Splits a `config` block's `pcrec <raw>` text into an argv on whitespace.
 * DELIBERATELY NOT A SHELL: there is no quoting, no escaping and no
 * variable expansion, because no flag in this CLI's surface takes a value
 * containing a space and inventing a quoting language for a case that does
 * not exist is a grammar somebody would then have to keep. The returned
 * vector and its one backing buffer are freed together by the caller. */
static int raw_split(const char *raw, char ***vout, int *nout, char **bufout)
{
    size_t len = strlen(raw);
    char *buf = malloc(len + 1);
    if (!buf) { perror("malloc"); return 1; }
    memcpy(buf, raw, len + 1);

    int cap = 8, n = 0;
    char **v = malloc((size_t)cap * sizeof *v);
    if (!v) { perror("malloc"); free(buf); return 1; }

    char *p = buf;
    while (*p) {
        while (*p == ' ' || *p == '\t') p++;
        if (!*p) break;
        if (n == cap) {
            cap *= 2;
            char **nv = realloc(v, (size_t)cap * sizeof *nv);
            if (!nv) { perror("realloc"); free(v); free(buf); return 1; }
            v = nv;
        }
        v[n++] = p;
        while (*p && *p != ' ' && *p != '\t') p++;
        if (*p) *p++ = '\0';
    }
    *vout = v; *nout = n; *bufout = buf;
    return 0;
}

/* [M4.5b] `pcrec_options.engine`'s three values, for a diagnostic only —
 * `PCREC_ENGINE_AUTO` is the only `enum` member (`lib/pcrec.h`'s [ABI-NS]
 * comment explains why DFA/VM are `#define`s instead), so this is the one
 * place that needs all three spellings back as text. */


/* The target's composed settings, ON TOP OF the command line's options.
 *
 * THE FILE WINS, and the precedent is in the tree rather than invented
 * here: `tests/harness/run.sh` appends `RXTFLAGS` LAST to its flag array
 * "so a directive on the same axis wins". A `.rxt` source states the build
 * its patterns are meant to have, and that build should not change with the
 * invocation that happened to trigger it; a command-line flag is the BASE a
 * file has not spoken about.
 *
 * WITHIN a target, `pcrec <raw>` is applied FIRST and the typed directives
 * on top. The typed spellings are the format's own named axes and are the
 * only ones a pattern BLOCK can write, so they are the more specific of the
 * two; `pcrec` is the general escape hatch, which is what makes it the
 * base rather than the override.
 *
 * **`engine` IS THE ONE NAMED EXCEPTION** (Frank's ruling, w235 finding 2,
 * 2026-09-15): an EXPLICIT `--engine=` on the actual command line wins over
 * a target's `engine vm` row rather than being silently discarded by it, and
 * a conflict is reported (stderr, non-fatal) naming both sources and both
 * values. "Explicit" is exactly `ts.opt.engine != PCREC_ENGINE_AUTO` at the
 * point this function reaches the `engine` row: the only two writers of that
 * field are this exact `--engine=` flag (parsed identically whether it came
 * from the real argv or from a `config` block's own `pcrec <raw>` line,
 * reparsed above through the SAME `cli_parse`) and the `engine` row below —
 * so a non-AUTO value here can only mean an explicit flag was typed, never
 * an inferred default. `--engine=auto` typed explicitly is INDISTINGUISHABLE
 * from no flag at all (both leave the field at its zero default) and this
 * function does not try to tell them apart — AUTO is what "the CLI is
 * silent" already means, so the two cases want the identical outcome
 * (the file's `engine` row applies) regardless of which one actually
 * happened. */
static int apply_target(const CliState *cli, const RxtTarget *t,
                        pcrec_options *out)
{
    CliState ts;
    memset(&ts, 0, sizeof ts);
    ts.opt = cli->opt;
    ts.opt.prefix = t->prefix;
    ts.opt.name = t->name;

    if (t->pcrec_raw) {
        char **v = NULL, *buf = NULL;
        int n = 0;
        if (raw_split(t->pcrec_raw, &v, &n, &buf) != 0) return 1;
        /* 24 literal bytes + a prefix capped by the RXT_TARGET_PREFIX_MAX
         * row (docs/spec/limits.md §3.5) + a quote + NUL = 153 worst case,
         * so this cannot truncate — stated because `-Wformat-truncation`
         * has bitten this tree once (src/parse/rxt_source.c's rxt_fail).
         * The row's name is kept on ONE line: the [LIM-1] bare-numeric
         * guard reads tokens, and a wrapped name reads as a bare limit. */
        char where[160];
        snprintf(where, sizeof where, "`pcrec` line of target '%s'", t->prefix);
        int rc = cli_parse(n, v, &ts, where);
        free(v); free(buf);
        if (rc != 0) { free(ts.libdirs); return 1; }
        /* THE CONTAINMENT, and it is one test rather than a list. A config
         * block sets COMPILE OPTIONS; anything else it could have set — an
         * output path, a pattern, a query mode, another source file, `-h`,
         * or `-p`, which would silently overrule the target's own prefix —
         * is refused here, and a flag added to this CLI tomorrow is covered
         * without an edit because the check is over the whole tail of the
         * struct rather than over a list of names.
         *
         * SHORTENED (msgtrim, 2026-09-10): this refusal joins `.rxt` source
         * resolution's 256-byte-buffer messages on `tests/rxtsource/
         * run_rxtsource_tests.sh`'s truncation CLASS check even though it
         * has no fixed-size buffer of its own — `cli->source` grows with
         * `TMPDIR` exactly as `rxt_fail`'s path prefix does, so the same
         * "shorten the prose, keep the path and the raw line" rule applies. */
        if (!cli_extras_clean(&ts)) {
            free(ts.libdirs);   /* a config that reached for --lib-path */
            cli_err("%s:%zu: `pcrec` line: compile options only, "
                    "not output/pattern/prefix/query/source: '%s'",
                    cli->source, t->line, t->pcrec_raw);
            return 1;
        }
    }

    /* [DD-13b.W1.3] ONE HOME for the letter -> bit mapping
     * (`src/parse/rxt_source.c`), because a DEFINITION's own `flags` are
     * read there too and a letter added to one loop and not the other would
     * make a library mean one thing built as a target and another bound into
     * a caller. */
    {
        unsigned long long f = 0;
        char bad = 0;
        if (pcrec_rxt_flags_from_letters(t->flags, &f, &bad) != 0) {
            cli_err("%s:%zu: unknown flag letter '%c' in "
                    "`flags %s`", cli->source, t->block_line, bad,
                    t->flags);
            return 1;
        }
        ts.opt.flags |= f;
    }
    if (t->encoding && set_encoding(&ts.opt, t->encoding) != 0) {
        cli_err("%s:%zu: in `encoding %s`",
                cli->source, t->block_line, t->encoding);
        return 1;
    }
    if (t->engine) {
        /* [REVW.4] wave 4 (L2-L2-7): parsed through the ONE engine
         * vocabulary, then narrowed by the FORMAT's own restriction. It used
         * to be a second, separately-worded engine menu that happened to
         * know one word; stating the restriction as a restriction is what
         * keeps `dfa` spelled once in this file. `dfa` and a typo are
         * refused with the same sentence here, exactly as before. */
        int want;
        if (engine_by_name(t->engine, &want) != 0 || want != PCREC_ENGINE_VM) {
            cli_err("%s:%zu: `engine %s` is not a value this format "
                    "accepts (only `vm`)",
                    cli->source, t->block_line, t->engine);
            return 1;
        }
        /* An explicit CLI `--engine=` (this invocation's own argv, or a
         * `config` block's `pcrec <raw>` line reparsed above) WINS over this
         * row rather than being silently overridden by it — see this
         * function's own header comment for why `!= PCREC_ENGINE_AUTO` here
         * is exactly "a flag was typed". */
        if (ts.opt.engine != PCREC_ENGINE_AUTO && ts.opt.engine != want) {
            cli_err("%s:%zu: target '%s': CLI --engine=%s and this "
                    "file's `engine %s` disagree; using the CLI's explicit "
                    "choice",
                    cli->source, t->block_line, t->prefix,
                    engine_name(ts.opt.engine), t->engine);
        } else {
            ts.opt.engine = want;
        }
    }
    /* [OPT-DIAL] `tune` IS NOT A SECOND `--engine` EXCEPTION: THE FILE WINS
     * (Frank's ruling 2026-09-16, decisions.md D93's addendum), which is the
     * GENERAL D93 rule unchanged, plus a loud non-fatal conflict diagnostic.
     *
     * The shape below is `--engine`'s own, with the OPPOSITE winner, and the
     * asymmetry is ruled rather than accidental. D93 rests on two supports:
     * a target is the artifact's DEFINITION, and letting an ambient flag
     * reshape a target breaks H11's free identity control. The second is
     * VACUOUS for `tune`, which is answer-preserving by its own acceptance
     * criterion — so H11's control survives either precedence and only the
     * definition argument is left standing, and that one says the file wins.
     * `--engine`'s exception had a forcing reason `tune` lacks: it is a
     * comparability facility (a caller types `--engine=vm` precisely to
     * compare two builds of one pattern) and it can make a pattern REFUSE.
     * `tune` can do neither.
     *
     * "AN EXPLICIT CLI --tune" IS `ts.opt.tune != PCREC_TUNE_BALANCED`, and
     * that carries the same accepted residual `--engine`'s does: a caller
     * who types `--tune=balanced` is indistinguishable from one who typed
     * nothing, because both leave the field at its zero default. Here that
     * costs nothing at all — under file-wins the two want the identical
     * outcome (the file's row applies), so there is no case to tell apart.
     * The general fix is explicit-set PROVENANCE for every D93-composed
     * axis, and it is DEFERRED to its own trigger (D77): the THIRD axis that
     * needs the distinction. `--engine` is the first and shipped without it;
     * this is the second and does not need it.
     *
     * THERE IS NO `--force-tune`. If an override is ever wanted, D93's own
     * revisit-when already names its shape — an explicit loud override flag,
     * never a silent precedence flip — and this diagnostic deliberately does
     * not advertise a flag no section of the spec defines. */
    if (t->tune) {
        int want = 0;
        if (pcrec_tune_parse(t->tune, &want) != 0) {
            /* Unreachable through `--source`: the parser validated this row
             * with this same function. It is a diagnosed internal error
             * rather than an assert because a library caller can build an
             * RxtTarget of its own. */
            cli_err("%s:%zu: internal error: `tune %s` reached the "
                    "CLI unvalidated",
                    cli->source, t->block_line, t->tune);
            return 1;
        }
        if (ts.opt.tune != PCREC_TUNE_BALANCED && ts.opt.tune != want)
            cli_err("%s:%zu: target '%s': CLI --tune=%s and this "
                    "file's `tune %s` disagree; using the file's value "
                    "(--tune is not the --engine exception)",
                    cli->source, t->block_line, t->prefix,
                    pcrec_tune_token(ts.opt.tune), t->tune);
        ts.opt.tune = want;
    }
    /* `budget frames=` sizes the ARTIFACT's resume stack, which is
     * `--backtrack-frames`, not the caller-supplied buffer of §10 —
     * tests/harness/run.sh maps the same directive the same way. */
    if (t->budget_steps  >= 0) ts.opt.step_budget = t->budget_steps;
    if (t->budget_frames >= 0) ts.opt.frame_capacity = (int)t->budget_frames;

    /* The enabled set is PROCESS-WIDE (src/parse/enabled.c), so it is
     * installed per target, immediately before that target's compile. */
    {
        char ferr[256];
        const char *fspec = t->features ? t->features
                          : (cli->features ? cli->features
                                           : pcrec_default_features);
        if (pcrec_enabled_set_spec(fspec, ferr, sizeof ferr) != 0) {
            cli_err("%s:%zu: features: %s%s",
                    cli->source, t->block_line, ferr,
                    (t->features && !t->features_only)
                        ? ".\n       This list is the UNION of the target's "
                          "configs and the block's own `features` line. "
                          "`features only <list>` on the block makes the "
                          "block's list stand alone."
                        : "");
            return 1;
        }
    }

    *out = ts.opt;
    return 0;
}

static int path_is_dir(const char *p)
{
    struct stat sb;
    return stat(p, &sb) == 0 && S_ISDIR(sb.st_mode);
}

/* `--source FILE`: parse the head, resolve the targets, compile each one.
 *
 * D88 HOLDS BY CONSTRUCTION HERE and is worth naming at the site: each
 * target is a SEPARATE `pcrec_compile()` call writing its own translation
 * unit, so there is no code path that could produce a multi-artifact TU
 * even if someone wanted one. */
static int compile_source(const CliState *cli)
{
    pcrec_error err = { 0 };
    RxtSource *src = pcrec_rxt_source_parse(cli->source, &err);
    if (!src) { cli_err("%s", err.msg); return 1; }

    RxtTarget *ts = NULL;
    size_t nt = 0;
    if (pcrec_rxt_source_resolve(src, cli->libdirs, cli->nlibdirs,
                                 &ts, &nt, &err) != 0) {
        cli_err("%s", err.msg);
        pcrec_rxt_source_free(src);
        return 1;
    }

    /* `--target NAME` selects by PREFIX, which is the name a `target` line
     * declares and the name the artifact's symbols carry. */
    if (cli->target) {
        size_t k = nt;
        for (size_t i = 0; i < nt; i++)
            if (!strcmp(ts[i].prefix, cli->target)) { k = i; break; }
        if (k == nt) {
            fprintf(stderr, "pcrec: %s: no target named '%s'", cli->source,
                    cli->target);
            if (!nt) fprintf(stderr, " (this file declares no target at all)");
            else {
                fprintf(stderr, " (it declares: ");
                for (size_t i = 0; i < nt; i++)
                    fprintf(stderr, "%s%s", i ? ", " : "", ts[i].prefix);
                fputc(')', stderr);
            }
            fputc('\n', stderr);
            pcrec_rxt_source_free(src);
            return 1;
        }
        ts = &ts[k];
        nt = 1;
    }

    /* A LIBRARY SHIPS NOTHING BY ITSELF (format_design §6.1). Zero targets
     * is not an error — it is what a file of definitions means — but it is
     * surprising enough at a build step that it says so, on stderr, at exit
     * 0, where a script that meant it is unaffected. */
    if (nt == 0) {
        cli_err("%s declares no target and is not a single unnamed "
                "pattern block, so it builds nothing (it is a library of "
                "definitions). Add a `target <prefix> = <definition>` line "
                "to build from it", cli->source);
        pcrec_rxt_source_free(src);
        return 0;
    }

    /* THE OUTPUT NAMING RULE (w1_impl §1.5). Three forms, and which one
     * applies is decided by the SHAPE of `-o`'s value, not by a flag:
     *   `-o -`          self-contained C on stdout; exactly one target
     *   `-o <dir>`      <dir>/<prefix>.c + .h, one pair per target
     *   `-o out.c`      one pair; exactly one target
     * A directory is an existing directory. Anything else is a file name,
     * which is what makes `-o out.c` on a fresh checkout behave the same
     * whether or not `out.c` exists yet. */
    int to_stdout = !strcmp(cli->outpath, "-");
    int to_dir = !to_stdout && path_is_dir(cli->outpath);

    if (nt > 1 && !to_dir) {
        fprintf(stderr,
                "pcrec: %s has %zu targets (", cli->source, nt);
        for (size_t i = 0; i < nt; i++)
            fprintf(stderr, "%s%s", i ? ", " : "", ts[i].prefix);
        fprintf(stderr,
                ") and `-o %s` names %s. Either build one target "
                "(`--target <prefix>`) or name an existing DIRECTORY with "
                "`-o`, which writes <dir>/<prefix>.c and .h per target\n",
                cli->outpath, to_stdout ? "stdout" : "a single file");
        pcrec_rxt_source_free(src);
        return 1;
    }

    int rc = 0;
    for (size_t i = 0; i < nt && rc == 0; i++) {
        const RxtTarget *t = &ts[i];
        pcrec_options topt;
        if (apply_target(cli, t, &topt) != 0) { rc = 1; break; }

        char *cpath = NULL, *hpath = NULL;
        if (!to_stdout) {
            size_t n;
            if (to_dir) {
                n = strlen(cli->outpath) + 1 + strlen(t->prefix) + 3;
                cpath = malloc(n);
                hpath = malloc(n);
                if (!cpath || !hpath) { perror("malloc"); free(cpath); free(hpath); rc = 1; break; }
                snprintf(cpath, n, "%s/%s.c", cli->outpath, t->prefix);
                snprintf(hpath, n, "%s/%s.h", cli->outpath, t->prefix);
            } else {
                size_t len = strlen(cli->outpath);
                cpath = malloc(len + 1);
                hpath = malloc(len + 3);
                if (!cpath || !hpath) { perror("malloc"); free(cpath); free(hpath); rc = 1; break; }
                memcpy(cpath, cli->outpath, len + 1);
                memcpy(hpath, cli->outpath, len + 1);
                if (len > 2 && !strcmp(hpath + len - 2, ".c"))
                    strcpy(hpath + len - 2, ".h");
                else strcat(hpath, ".h");
            }
            topt.header_name = base_name(hpath);
        }

        pcrec_output out;
        pcrec_error cerr;
        /* [DD-13b.W1.3] the COMPOSING entry: same pipeline, plus the
         * file's definition closure. `t->defs` is never NULL (an empty set
         * for a file with no named block), so there is one call here and no
         * branch on whether this source composes. */
        if (pcrec_compile_defs(t->pattern, &topt, t->defs, &out, &cerr) != 0) {
            /* THE FILE AND THE LINE COME FIRST, THEN pcrec's OWN OFFSET.
             * A `.rxt` author's coordinates are file:line; the pattern
             * offset is still printed, because it is the only thing that
             * locates a failure INSIDE a pattern. */
            cli_err("%s:%zu: target '%s': %s (pattern offset "
                            "%zu)",
                    cli->source, t->block_line, t->prefix, cerr.msg, cerr.pos);
            free(cpath); free(hpath);
            rc = 1;
            break;
        }
        if (to_stdout) {
            fputs(out.c_src, stdout);
            if (fflush(stdout) != 0 || ferror(stdout)) {
                cli_err("write error on stdout");
                rc = 1;
            }
        } else if (write_file(cpath, out.c_src) != 0 ||
                   write_file(hpath, out.h_src) != 0) {
            rc = 1;
        }
        pcrec_output_free(&out);
        free(cpath);
        free(hpath);
    }

    pcrec_rxt_source_free(src);
    return rc;
}

/* Parses the command line via `cli_parse`, then dispatches: a syntax/
 * registry query (`--list-*`, `--explain`, `--probe-ask`, `--count-groups`
 * — no pattern, no `-o`, each returning before anything else runs), a
 * `.rxt` `--source` compile (`compile_source`, one or more targets), or an
 * ordinary single-pattern compile to `-o`. `--target`/`--lib-path` are
 * refused above every query since they apply to `--source` alone (the one
 * refusal that also has to free `st.libdirs`, this CLI's only allocation
 * outside that path). Returns 0 on success, 1 on any refusal or compile
 * failure. */
int main(int argc, char **argv)
{
    CliState st;
    memset(&st, 0, sizeof st);
    pcrec_default_options(&st.opt);
    if (cli_parse(argc - 1, argv + 1, &st, "command line") != 0) {
        free(st.libdirs);
        return 1;
    }
    if (st.want_help) { usage(stdout); return 0; }

    /* [DD-13b.W1.2] `--target`/`--lib-path` APPLY TO `--source` ALONE, and
     * this is refused HERE — above every query — for two reasons that
     * happen to coincide. A query returns from `main` on its own, so a
     * conflict tested lower down is one the query already won silently;
     * and `--lib-path` is the only option in this CLI that ALLOCATES, so
     * refusing it here is what makes "st.libdirs is non-NULL" true on
     * exactly two paths — this one and the `--source` compile — both of
     * which free it. Every other exit from `main` provably has nothing to
     * free, which is why none of them carries a `free` that a reader would
     * have to keep in step. */
    if (!st.source && (st.target || st.libdirs)) {
        cli_err("%s applies to --source only",
                st.target ? "--target" : "--lib-path");
        free(st.libdirs);
        return 1;
    }

    /* Read-only aliases for the modes below, so the query dispatch reads
     * exactly as it did before the parser was factored out. `opt` is a COPY
     * the compile path may still adjust (`header_name`). */
    pcrec_options opt        = st.opt;
    const char *outpath      = st.outpath;
    const char *pattern      = st.pattern;
    const int list_syntax    = st.list_syntax;
    const int list_definitions = st.list_definitions;
    const int list_verbs     = st.list_verbs;
    const int list_families  = st.list_families;
    const int list_axes      = st.list_axes;
    const int list_limits    = st.list_limits;
    const int list_schema    = st.list_schema;
    const int count_groups   = st.count_groups;
    const int emit_ir        = st.emit_ir;
    const char *explain      = st.explain;
    const char *flavour      = st.flavour;
    const char *probe_want   = st.probe_want;
    const char *features     = st.features;
    const char *list_source  = st.list_source;
    /* [REVW.4] wave 4: every mutual-exclusion test below reads THIS, against
     * a named membership from the table beside `CliState`. Nothing between
     * `cli_parse` and here writes a mode field, so one computation serves
     * all six sites. */
    const unsigned modes     = cli_modes_active(&st);

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
     * bare invocation resolves through pcrec_default_features instead of
     * skipping this call — that constant is the one bare-default mapping
     * point — "std1" since [STD1b], advancing only at announced version
     * boundaries (--features none is the verbatim old bare behaviour;
     * --features stdN pins a set forever). Either way the set gets
     * INSTALLED (never left at whatever a previous call left it), which is
     * also what gives the artifact stamp (src/gen) something honest to
     * report for a bare invocation. */
    {
        char ferr[256];
        const char *fspec = features ? features : pcrec_default_features;
        if (pcrec_enabled_set_spec(fspec, ferr, sizeof ferr) != 0) {
            cli_err("--features: %s", ferr);
            return 1;
        }
    }

    /* [DD-13b.W1.2] `--source` VERSUS EVERY QUERY, CHECKED HERE AND NOT AT
     * THE COMPILE PATH. Each query mode below returns from `main` on its
     * own, so a conflict tested down beside the compile is a conflict the
     * query already won SILENTLY — `--source f.rxt --count-groups -- a`
     * would have counted the pattern's groups and ignored the file. The
     * test is one place, above all of them, and it names both surfaces. */
    if (st.source && (modes & CLI_MODES_VS_SOURCE)) {
        cli_err("--source COMPILES a .rxt file; it does not "
                        "compose with a query surface (--list-source READS "
                        "one)");
        free(st.libdirs);
        return 1;
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
        if (modes & CLI_MODES_VS_LIST_SOURCE) {
            cli_err("--list-source is a separate query; use one "
                            "(--list-source READS a .rxt file, --source "
                            "COMPILES one)");
            return 1;
        }
        if (pattern || outpath) {
            cli_err("--list-source takes no pattern and no -o "
                            "(it reads the file named by its own value)");
            return 1;
        }
        if (flavour) {
            cli_err("--flavour applies to --list-syntax, "
                            "--list-definitions and --explain only");
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
            cli_err("%s", serr.msg);
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
        if (modes & CLI_MODES_VS_PATTERN_QUERY) {
            cli_err("--probe-ask is a separate query; use one");
            return 1;
        }
        if (outpath) {
            cli_err("--probe-ask takes no -o");
            return 1;
        }
        if (flavour) {
            cli_err("--flavour applies to --list-syntax and "
                            "--explain only");
            return 1;
        }
        if (!pattern) {
            cli_err("--probe-ask needs a construct");
            return 1;
        }
        /* Two NULLs with different causes (R20/MOD07-1): a port that RAISED
         * fills perr, and gets the compile path's own error shape rather
         * than the usage sentence below — the operator's command line is
         * fine, their pattern is not. */
        pcrec_error perr;
        char *line = pcrec_probe_ask(probe_want, pattern, &perr);
        if (!line && perr.msg[0]) {
            cli_err("--probe-ask: %s (pattern offset %zu)",
                    perr.msg, perr.pos);
            return 1;
        }
        if (!line) {
            /* [REVW.4] wave 4: the WANT vocabulary is `src/dump/
             * syntax_dump.c`'s own table — the same one `pcrec_probe_ask`
             * parses against — rendered with its last comma replaced by
             * "or" so the sentence reads as it always has. */
            char wants[128];
            pcrec_probe_want_names(wants, sizeof wants);
            char *lastc = strrchr(wants, ',');
            cli_err("--probe-ask: WANT must be %.*s%s%s, and the construct "
                            "must reach a doorway (start with '\\', '(?', "
                            "'(*' or '[' — except '(?:', which the base "
                            "grammar answers before any doorway is "
                            "consulted)",
                    lastc ? (int)(lastc - wants) : (int)strlen(wants), wants,
                    lastc ? " or" : "", lastc ? lastc + 1 : "");
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
        if (modes & CLI_MODES_VS_PATTERN_QUERY) {
            cli_err("--emit-ir is a separate query; use one");
            return 1;
        }
        if (outpath) {
            cli_err("--emit-ir takes no -o (it prints the "
                            "listing, not C)");
            return 1;
        }
        if (!pattern) {
            cli_err("--emit-ir needs a pattern");
            return 1;
        }
        {
            pcrec_error err;
            char *text = pcrec_emit_ir(pattern, &opt, &err);
            if (!text) {
                cli_err("%s (pattern offset %zu)",
                        err.msg, err.pos);
                return 1;
            }
            fputs(text, stdout);
            free(text);
            return 0;
        }
    }

    if (count_groups) {
        if (modes & CLI_MODES_VS_COUNT_GROUPS) {
            cli_err("--count-groups is a separate query; use one");
            return 1;
        }
        if (outpath) {
            cli_err("--count-groups takes no -o");
            return 1;
        }
        if (flavour) {
            cli_err("--flavour applies to --list-syntax and "
                            "--explain only");
            return 1;
        }
        if (!pattern) {
            cli_err("--count-groups needs a pattern");
            return 1;
        }
        pcrec_error err;
        int n = pcrec_count_groups(pattern, &err);
        if (n < 0) {
            cli_err("%s (pattern offset %zu)", err.msg, err.pos);
            return 1;
        }
        printf("%d\n", n);
        return 0;
    }

    /* Syntax queries answer from the registry and compile nothing, so they take
     * neither a pattern nor -o. They are checked before the pattern/-o
     * requirement and reject a mixed invocation rather than silently ignoring
     * half of it. */
    if (modes & CLI_MODES_REGISTRY_QUERY) {
        /* THE SECOND RELATION (see the mode table): at most one of these
         * eight co-equal flags, which is a different question from "is some
         * OTHER mode active" and keeps its own shape by ruling. */
        if (cli_modes_count(modes & CLI_MODES_REGISTRY_QUERY) > 1) {
            cli_err("--list-syntax, --list-definitions, --list-verbs, "
                            "--list-families, --list-axes, --list-limits, --list-schema "
                            "and --explain are separate queries; use one");
            return 1;
        }
        if (pattern || outpath) {
            /* Exactly one is set here — the count relation above returned
             * otherwise — so the FIRST active mode in table order IS it, and
             * the table's order is the hand ladder's order. */
            cli_err("%s takes no pattern and no -o",
                    cli_mode_name(modes & CLI_MODES_REGISTRY_QUERY));
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
        if ((list_verbs || list_families || list_axes || list_limits ||
             list_schema) && flavour) {
            cli_err("--flavour applies to --list-syntax, "
                            "--list-definitions and --explain only");
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
        /* [DD-13b.W23.1] --list-schema joins --list-axes'/--list-limits'
         * no-flavour reason rather than a new one: it reports what THIS
         * BUILD's own `rxt_schema.def` says about the `.rxt` FORMAT, which
         * has no flavour axis at all — a flavour is a PATTERN-syntax
         * dialect (SR-7), and the file format that carries a pattern is
         * the same file format whichever dialect the pattern is in. */
        if (list_schema) {
            char *v = pcrec_rxt_schema_tsv();
            fputs(v, stdout);
            free(v);
            return 0;
        }
        unsigned fl = 0;
        if (flavour && !(fl = pcrec_flavour_by_name(flavour))) {
            /* [REVW.4] wave 4: the name comes from the same table
             * `pcrec_flavour_by_name` just failed against, so the refusal
             * cannot name a vocabulary the lookup does not have. The
             * SENTENCE still says "only", because there is still exactly
             * one row; SR-7's second flavour is the D80 event that rewords
             * it, and it will be unable to land without noticing. */
            char flavs[128];
            pcrec_flavour_names(flavs, sizeof flavs);
            cli_err("unknown flavour '%s' (only '%s' exists; "
                            "more arrive with SR-7)", flavour, flavs);
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
            cli_err("--explain: %s (pattern offset %zu)",
                    eerr.msg, eerr.pos);
            return 1;
        }
        if (!text) {
            /* --explain only; the TSV always has rows */
            cli_err("no construct matches '%s' — it is either "
                            "base syntax or not a construct pcrec knows",
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
            cli_err("--explain: %d row%s DISAGREE%s with the live "
                            "doorway (see the 'agree' lines) — this is a pcrec "
                            "defect, not a bad query",
                    ndissent, ndissent == 1 ? "" : "s",
                    ndissent == 1 ? "S" : "");
            return 3;
        }
        return 0;
    }
    if (flavour) {
        cli_err("--flavour applies to --list-syntax and "
                        "--explain only");
        return 1;
    }

    /* [DD-13b.W1.2] `--source FILE` — COMPILE FROM A `.rxt` SOURCE.
     *
     * It is a COMPILE MODE, not a query: it takes `-o` and honours every
     * compile flag, and the one thing it refuses beside a query is a
     * positional PATTERN, because a source file IS the pattern (or several)
     * and accepting both would leave "which one did I build" answerable two
     * ways. `--target` and `--lib-path` are meaningful only with it. */
    if (st.source) {
        /* the query conflict was refused above, before any query could
         * return; what is left is this mode's own two requirements. */
        if (pattern) {
            cli_err("--source takes no pattern argument — the "
                            "file's `pattern` blocks are the patterns (got "
                            "'%s')", pattern);
            free(st.libdirs);
            return 1;
        }
        if (!outpath) {
            cli_err("--source needs -o: a FILE for one target, "
                            "an existing DIRECTORY for several (which writes "
                            "<dir>/<prefix>.c and .h per target), or '-' for "
                            "one target on stdout");
            free(st.libdirs);
            return 1;
        }
        {
            int rc = compile_source(&st);
            free(st.libdirs);
            return rc;
        }
    }
    if (!pattern || !outpath) {
        cli_err("pattern and -o are required");
        usage(stderr);
        return 1;
    }

    /* [DD-13b.W23.3] `--pattern-esc`: THE OPERAND IS THE `.rxt` FORMAT'S
     * QUOTED-ESCAPE FORM, decoded by the format's OWN decoder.
     *
     * WHO DECODES: PCREC, ONCE (format_design §2.19). A `pattern-esc` block
     * exists so a multi-line or high-byte pattern is expressible without
     * multi-line SYNTAX, which keeps every reader's line-oriented loop
     * intact — and that only pays if the DECODING has one home. `run.sh`
     * passes the still-encoded text through with this flag rather than
     * approximating it with `printf %b`, which would be a SECOND escape
     * vocabulary drifting from this one by construction;
     * `verify_rxt.py` decodes with the table it already has for subjects,
     * which is the same table.
     *
     * The arena is local and freed on every path out, so the decoded bytes
     * outlive `pcrec_compile` (which copies what it needs into its own
     * arena) and nothing outlives this function. */
    Arena esc = { 0 };
    if (st.pattern_esc) {
        char emsg[192];
        const char *dec = NULL;
        if (pcrec_rxt_decode_escaped(pattern, &esc, &dec, emsg,
                                     sizeof emsg) != 0) {
            cli_err("--pattern-esc: %s", emsg);
            pcrec_arena_free(&esc);
            return 1;
        }
        pattern = dec;
    }

    int to_stdout = !strcmp(outpath, "-");
    char *hpath = NULL;
    if (!to_stdout) {
        size_t len = strlen(outpath);
        hpath = malloc(len + 3);
        if (!hpath) { perror("malloc"); pcrec_arena_free(&esc); return 1; }
        strcpy(hpath, outpath);
        if (len > 2 && !strcmp(hpath + len - 2, ".c")) strcpy(hpath + len - 2, ".h");
        else strcat(hpath, ".h");
        opt.header_name = base_name(hpath);
    }

    pcrec_output out;
    pcrec_error err;
    if (pcrec_compile(pattern, &opt, &out, &err) != 0) {
        cli_err("%s (pattern offset %zu)", err.msg, err.pos);
        free(hpath);
        pcrec_arena_free(&esc);
        return 1;
    }

    int rc = 0;
    if (to_stdout) {
        fputs(out.c_src, stdout);
        if (fflush(stdout) != 0 || ferror(stdout)) {
            cli_err("write error on stdout");
            rc = 1;
        }
    } else {
        if (write_file(outpath, out.c_src) != 0 ||
            write_file(hpath, out.h_src) != 0)
            rc = 1;
    }
    pcrec_output_free(&out);
    free(hpath);
    pcrec_arena_free(&esc);
    return rc;
}
