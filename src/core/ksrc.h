/* src/core/ksrc.h — [KNOW-SRC] the knowledge-source module's kind-independent
 * PARTS: the name rule and its classification, the stop-order resolver,
 * fill-only precedence, and the digest builder (docs/design/measure_sets.md
 * rev 3 §9.2, plan row [KNOW-SRC]).
 *
 * A KIND is one body of named, versioned knowledge a compile or a harness
 * loads (the analysis object, `lib` references; measurement sets, picks and
 * evaluator parameters when their steps land). Each kind is ONE ROW, a
 * `KsKind`, defined in its own TU (`src/parse/ks_analysis.c`,
 * `src/parse/ks_lib.c`); the table assembling the rows is
 * `src/core/ksrc_kinds.c`, at the library tier. Every way two kinds differ
 * is a COLUMN of that row, so the parts below hold one loop each and the
 * differences are listed rather than copied (§9.5).
 *
 * DEPENDENCY RULE (§9.2, sabotage S989): `ksrc.c` and this header include
 * libc, POSIX `<dirent.h>`/`<sys/stat.h>` and this header ONLY — never
 * `core/internal.h`, which pulls in `Arena`, `StrBuf`, `Ctx` and the whole
 * compiler. They allocate through a caller's `KsAlloc` and report through a
 * fixed `KsErr`, so a tool that links the parts (`pcrec-measure`, §7.1)
 * links nothing else of `src/`.
 *
 * WHAT IS NOT HERE YET, by step (§9.7): the section-TSV reader (part 1)
 * lands with its first reader, the `measures` kind (M0). The embed
 * generator (part 4) is `scripts/ksgen.c` (K2), which links these parts. The
 * views (part 6) are here since K3: `pcrec_ks_view_write` dispatches a view
 * NAME to the row's writer columns, and `pcrec_ks_derived_section` is the
 * loader's refusal of a derived view fed back as an input (§9.6). A column
 * joins `KsKind` in the step that first reads it. */
#ifndef PCREC_KSRC_H
#define PCREC_KSRC_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* An allocator the caller supplies; memory comes back zeroed and is never
 * freed by the parts (an arena's lifetime is the caller's). */
typedef struct {
    void *(*alloc)(void *ctx, size_t n);
    void  *ctx;
} KsAlloc;

/* A refusal's text, the size of `pcrec_error.msg` so a caller copies it
 * across with "%s" and truncation happens at the same byte. */
typedef struct {
    char msg[256];
} KsErr;

/* A writer the caller supplies (a view's destination): `write` appends `n`
 * bytes and returns 0, or nonzero on failure. The parts never see the
 * caller's buffer type. */
typedef struct {
    int  (*write)(void *ctx, const char *p, size_t n);
    void  *ctx;
} KsOut;

/* ---- the row's column vocabularies (§9.5) ---------------------------- */

/* A STOP: where a resolution looks, in this order. Index space: 0 is the
 * row's OWN stop (`KS_AT_S1`, the compiling file, or `KS_AT_SRCDIR`, the
 * naming file's directory — no kind has both), 1..ndirs the `-I` directories
 * in order, ndirs + 1 the kind's built-in store. An absent stop is skipped,
 * never renumbered, so "the stop after s" is always s + 1. */
typedef enum { KS_AT_SRCDIR, KS_AT_S1, KS_AT_DIRS, KS_AT_STORE } KsAt;
#define KS_STOP_BIT(at) (1u << (at))

/* How a request's spelling is classified (§3.2): a NAME only, a NAME else a
 * FILE (a non-name is a file path, with no probe), or a FILE only. */
typedef enum {
    KS_CLS_NAME_ONLY, KS_CLS_NAME_ELSE_FILE, KS_CLS_FILE_ONLY
} KsClassify;
/* What a request is, once classified; KS_REQ_BAD refuses it. A `lib "x"`
 * reference is a KS_REQ_PATH by its syntax, never classified. */
typedef enum { KS_REQ_BAD, KS_REQ_NAME, KS_REQ_FILE, KS_REQ_PATH } KsReq;

/* An `-I` file that holds no item of the requested name, or several. */
typedef enum { KS_S2_FALLTHROUGH_NOTE, KS_S2_REFUSE } KsS2;

/* How an `-I` (or source-directory) entry is matched [r2 M6]: EXACT is an
 * equality test over the directory's entries, so a case-insensitive
 * filesystem cannot answer `log` with `Log.rxt`; PROBE_EXISTS is a stat of
 * the joined path (`lib`'s shipped probe, kept for zero movers: F12). */
typedef enum { KS_ENTRY_EXACT, KS_ENTRY_PROBE_EXISTS } KsEntry;

/* How a directory and an entry are joined into the path a resolution
 * reports: SLASH always inserts one '/' (the analysis row's shipped
 * `DIR/<name>.rxt`, so `-I d/` reports `d//x.rxt`); CLEAN inserts one only
 * when the directory is non-empty and does not end in '/' (`lib`'s shipped
 * `join_path`). A divergence kept as a column for zero movers, beside F12. */
typedef enum { KS_JOIN_SLASH, KS_JOIN_CLEAN } KsJoin;

typedef enum { KS_VIEW_CANONICAL, KS_VIEW_SHIPPED } KsView;
typedef enum { KS_R4_REQUIRED, KS_R4_EXEMPT } KsR4;
typedef enum { KS_LIST_NONE, KS_LIST_CLI, KS_LIST_HARNESS } KsListSurface;

/* One digest ROLE [r2 M5]: FNV-1a-64 over `domain` (LITERAL bytes, explicit
 * length because the shipped tags hash their NUL — §9.2 part 5), then the
 * sub-key's bytes and a NUL when `subkey` is KS_SUB_QUERY, then the kind's
 * own fold over the document. */
typedef enum { KS_SUB_NONE, KS_SUB_QUERY } KsSub;
typedef struct {
    const unsigned char *domain;
    size_t               domain_len;
    KsSub                subkey;
    uint64_t (*fold)(uint64_t h, const void *doc, const char *subkey_val);
} KsDigest;
/* A domain spelled once: the literal's bytes INCLUDING its terminator. */
#define KS_DOMAIN(lit) (const unsigned char *)(lit), sizeof (lit)

/* What a kind's file probe found in one candidate file. */
typedef enum {
    KS_FILE_FOUND,   /* it defines the requested item; `*doc` is the kind's */
    KS_FILE_OTHER,   /* it defines no item of that name (zero or one other) */
    KS_FILE_MULTI,   /* it defines `*nitems` > 1 items */
    KS_FILE_ERROR    /* it could not be read; `err` filled */
} KsFile;

/* One knowledge KIND: a row of the closed kinds table. */
typedef struct KsKind {
    const char   *kind;          /* "analysis", "lib" */
    const char   *suffix;        /* the entry a NAME request looks for */
    unsigned      stops;         /* KS_STOP_BIT(KsAt) set */
    KsClassify    flag_classify; /* the CLI flag's operand */
    KsClassify    list_classify; /* `--list-<kind> X`'s operand */
    bool          revs;          /* NAME@REV accepted (no kind yet) */
    KsS2          s2_mismatch;
    KsS2          s2_multi;
    KsEntry       entry_match;
    KsJoin        join;
    KsView        bare_view;
    KsR4          r4;
    KsListSurface list_surface;
    const char   *cli_flag, *cfg_line, *list_flag;  /* NULL: none */
    /* The words the shared refusals and notes say: "analysis", "analyses",
     * "bundle". */
    const char   *noun, *nouns, *item_noun;
    const KsDigest *item;        /* the loadable item's identity, or NULL */
    const KsDigest *stamp;       /* what a compile consumed, or NULL */
    /* Reads `path` and reports whether it defines item `name`. NULL for a
     * resolve-only kind (`lib`), whose stop answers by existence alone. On
     * KS_FILE_FOUND `*doc` is the kind's parse, owned by the caller; on
     * every other answer the probe has released it. */
    KsFile (*probe)(const char *path, const char *name, void **doc,
                    size_t *nitems, KsErr *err);
    /* §9.6's two views of ONE loaded item (`doc` is the kind's own item
     * handle, not the probe's parse): the CANONICAL view, which IS a
     * loadable input of the kind, and the DECODED view, the loaded document
     * field by field (a derived view, never an input). NULL: the kind has
     * no such view. 0, or -1 with `err` filled. */
    int  (*write_canonical)(const KsOut *o, const void *doc, KsErr *err);
    int  (*write_decoded)(const KsOut *o, const void *doc, KsErr *err);
    /* The section names of the kind's DERIVED views (§9.5's last row),
     * NULL-terminated: a file carrying `#section <one of them>` is a listing
     * fed back, and the loader refuses it naming the section. NULL: none. */
    const char *const *derived_sections;
} KsKind;

/* ---- part 2: the resolver -------------------------------------------- */

/* One resolution: the kind, the stops' inputs, and the caller's hooks for
 * the two stops that are the CALLER's data (the compiling file and the
 * store). `has` answers "does stop `at` define `name`" for KS_AT_S1 and
 * KS_AT_STORE; the caller builds its own result from the hit. `note`, when
 * non-NULL, receives the fall-through note's text (no prefix, no newline);
 * NULL suppresses notes. */
typedef struct {
    const KsKind       *kind;
    const char *const  *dirs;       /* the `-I` list, `ndirs` long */
    size_t              ndirs;
    bool                s1;         /* KS_AT_S1 is present this time */
    const char         *srcdir;     /* KS_AT_SRCDIR's directory ("" = none) */
    const KsAlloc      *alloc;
    void               *ctx;
    bool (*has)(void *ctx, KsAt at, const char *name);
    void (*note)(void *ctx, const char *text);
    KsErr              *err;
} KsWalk;

/* Where a resolution landed: the stop index (see KsAt), what kind of stop,
 * the file's path (a directory or source-directory stop; else NULL), and the
 * kind's probe result (else NULL). */
typedef struct {
    size_t      stop;
    KsAt        at;
    const char *path;
    void       *doc;
} KsHit;

typedef enum { KS_RES_FOUND, KS_RES_ABSENT, KS_RES_ERROR } KsRes;

/* Resolves `ref` (a NAME, or for a resolve-only kind a PATH) from stop
 * `from` onward, into `*hit`. ABSENT fills nothing: the caller words its
 * own unknown-name refusal (`pcrec_ks_refuse_unknown` for a NAME kind). ERROR has
 * filled `w->err`. */
KsRes pcrec_ks_resolve(const KsWalk *w, KsReq req, const char *ref, size_t from,
                 KsHit *hit);

/* The stops a NAME resolution searched, as its refusal lists them: "the
 * compiling file, -I d1, -I d2, the built-in store". */
const char *pcrec_ks_stops_text(const KsWalk *w);

/* Fills `w->err` with the unknown-name refusal naming every stop searched. */
void pcrec_ks_refuse_unknown(const KsWalk *w, const char *name);

/* Does `dir` hold an entry named exactly `fname`? */
bool pcrec_ks_dir_has_exact(const char *dir, const char *fname);

/* ---- the name rule and classification -------------------------------- */

/* Is `s[0..n)` a legal knowledge name: a lowercase letter, then lowercase
 * letters, digits, `_` or `-` (findings design §3.1 [r2 M-S6])? */
bool pcrec_ks_name_ok(const char *s, size_t n);

/* What spelling `s` is under classification `c`. */
KsReq pcrec_ks_classify(KsClassify c, const char *s);

/* ---- part 3: fill-only precedence (D93) ------------------------------ */

typedef enum { KS_SRC_NONE, KS_SRC_FLAG, KS_SRC_FILE } KsSource;
/* The decision and its disagreement, as data: the file's value wins for a
 * target that names one, the flag fills a target that names none.
 * `disagree` is true when both are set and differ — the caller prints its
 * own note naming its own flag and line (the library has no stderr). */
typedef struct {
    const char *chosen;
    KsSource    source;
    const char *flag_value, *file_value;
    bool        disagree;
} KsPick;
KsPick pcrec_ks_pick(const char *flag_value, const char *file_value);

/* ---- part 6: the views (§9.2 part 6, §9.6) ---------------------------- */

/* Writes `s` (NUL-terminated) to `o`; 0, or nonzero when the writer fails. */
int pcrec_ks_out(const KsOut *o, const char *s);

/* Writes view `view` ("canonical" or "decoded") of item `doc` through the
 * row's writer column. -1 with `err` filled on an unknown view, a view the
 * kind has no writer for, or the writer's own refusal. */
int pcrec_ks_view_write(const KsKind *k, const char *view, const KsOut *o,
                        const void *doc, KsErr *err);

/* The first `#section NAME` line (at column 1) of the file at `path` whose
 * NAME is one of `k->derived_sections`, or NULL (none, an unreadable file,
 * or a kind with no derived sections). The returned name is the row's own
 * string. */
const char *pcrec_ks_derived_section(const KsKind *k, const char *path);

/* ---- part 5: the digests --------------------------------------------- */

/* One FNV-1a-64 step over `n` bytes; `KS_FNV_BASIS` starts a hash. FNV and
 * not SHA-256: identity against accidental change, not an adversarial
 * setting, and it keeps libpcrec dependency-free (findings design §7). */
uint64_t pcrec_ks_fnv1a(uint64_t h, const void *p, size_t n);
extern const uint64_t pcrec_ks_fnv_basis;

/* `role`'s digest of `doc`: the domain bytes, the sub-key (`subkey_val` and
 * a NUL) where the role takes one, then the role's fold. */
uint64_t pcrec_ks_digest(const KsDigest *role, const void *doc,
                   const char *subkey_val);

#endif
