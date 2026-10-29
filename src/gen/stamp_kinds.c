/* [COMPOUND] THE STAMP CATALOGUE (docs/design/compound.md §A.7; the value
 * table is docs/spec/match_api.md §6.3's "On a compound").
 *
 * Every stamp the emitters write through the stamp primitives
 * (`pcrec_sb_stampf` and its siblings, src/core/sb.c), classified by WHAT IT
 * IS A FACT ABOUT, which decides its value on a compound:
 *
 *   PATTERN  true of the pattern and the caller contract, whichever machine
 *            runs: the compound writes P's own value (the plain compile's,
 *            which the shell IS). Also the facts about the emitted TEXT as a
 *            whole (`MEMFN_LIBC`, `SIMD_GUARDED_BYTES`), which the shell
 *            measures over the assembled artifact, parts included.
 *   UNION    a list of what the TEXT holds, written by each part's own
 *            emission (`MEMFN_FORMS`, the kit forms): the sorted, distinct
 *            union of the parts' values, `"none"` when every part's is.
 *   MACHINE  one machine's route or strategy: on a compound the controller
 *            is no such machine, so the stamp takes a DEFINED compound value
 *            -- `"compound"` for a string, -1 for a count -- and each part
 *            keeps its own value under its part prefix (`<PREFIX>__F_...`).
 *            No reader infers a fact from a stamp's absence.
 *
 * A row is matched by its NAME, or by a name FAMILY's prefix (`VAR_`, the
 * VM's slot legend) where the emitter computes the name. A stamp this table
 * does not classify is an INTERNAL ERROR on a compound's shell (the filter
 * below), so a new stamp cannot ship on a compound unclassified.
 *
 * `COMPOUND` itself is pattern-level: the shell writes the row's name. */
#include "core/internal.h"

#include <string.h>

typedef enum { SK_PATTERN, SK_PARTS_UNION, SK_MACHINE_STR, SK_MACHINE_NUM } StampKind;

typedef struct {
    const char *name;     /* the stamp's name after `<PREFIX>_` */
    bool family;          /* `name` is a prefix (the emitter computes the rest) */
    StampKind kind;
    /* true: written as a stamp but internal to the artifact, not the
     * caller contract (match_api.md §6.3.1¶10), so a code segment block
     * `#undef`s it (`pcrec_stamp_is_contract`); false on every other row */
    bool internal;
} StampRow;

static const StampRow stamp_rows[] = {
    /* the shared prologue (src/gen/emit_dfa.c `pcrec_emit_prologue`) */
    { "ALTCLS_MERGES",      false, SK_PATTERN, false },      /* P's tree rewrite */
    { "ALTCLS_FACTORED",    false, SK_PATTERN, false },
    { "STARTPOS_GUARD",     false, SK_PATTERN, false },      /* the caller contract */
    { "UTF_CHECK",          false, SK_PATTERN, false },
    { "ITER_RETRY",         false, SK_PATTERN, false },      /* the shell's own iterator */
    { "END_WINDOW",         false, SK_MACHINE_STR, false },  /* the search entry's clamp */
    { "REQ_BYTE",           false, SK_PATTERN, false },      /* the analysis: a pattern fact */
    { "REQ_RUN",            false, SK_PATTERN, false },
    { "REQ_WHY",            false, SK_MACHINE_STR, false },  /* whether an entry acted on it */
    { "REQ_HANDOFF",        false, SK_MACHINE_STR, false },
    { "VM_START_SCAN",      false, SK_MACHINE_STR, false },
    { "TUNE",               false, SK_PATTERN, false },
    { "PART_LAYOUT",        false, SK_PATTERN, false },      /* the caller's controls, */
    { "PART_LAYOUT_WHY",    false, SK_PATTERN, false },      /* over the whole artifact */
    { "COMPOUND",           false, SK_PATTERN, false },
    { "NCAPS",              false, SK_PATTERN, false },
    { "NVARS",              false, SK_PATTERN, false },
    { "VAR_",               true,  SK_PATTERN, false },
    { "CALLOUTS",           false, SK_PATTERN, false },      /* [INLINE-C] 1b the sites */
    { "CALLOUT_BINDINGS",   false, SK_PATTERN, false },      /* and the symbols they need */
    { "CODE_LANGS",         false, SK_PATTERN, false },      /* [INLINE-C] stage 2 code's languages */
    { "RESUME_FRAMES",      false, SK_PATTERN, false },      /* the buffer surface: */
    { "TRAIL_FRAMES",       false, SK_PATTERN, false },      /* the caller contract */
    { "RESUME_FRAME_SIZE",  false, SK_PATTERN, false },
    { "TRAIL_FRAME_SIZE",   false, SK_PATTERN, false },
    { "BUFFER_ALIGN",       false, SK_PATTERN, false },
    /* the engine stamps */
    { "ENGINE",             false, SK_PATTERN, false },      /* "can a call give up" */
    { "ENGINE_SEL",         false, SK_PATTERN, false },
    /* written by hand, never filtered (the VM's reason line); the row
     * classifies it as a contract stamp for the segment block */
    { "ENGINE_WHY",         false, SK_PATTERN, false },
    { "MAX_EMIT_BYTES",     false, SK_PATTERN, false },      /* the limit built under */
    { "MAX_EMIT_CODE_BYTES", false, SK_PATTERN, false },
    { "STEP_BUDGET",        false, SK_PATTERN, false },      /* per call: the contract */
    { "WORK_BUDGET",        false, SK_PATTERN, false },
    { "FINDINGS",           false, SK_PATTERN, false },
    { "MEASURES",           false, SK_PATTERN, false },      /* over P and the parts (match_api §6.3.10¶13) */
    /* the DFA scan family (`pcrec_emit_dfa_scan_stamps`, `emit_dfa_stamps`) */
    { "DFA_SCAN",           false, SK_MACHINE_STR, false },
    { "DFA_PREFILTER",      false, SK_MACHINE_STR, false },
    /* written by hand, never filtered (a streamed value, emit_dfa.c); the
     * row classifies it as a contract stamp for the segment block */
    { "DFA_PREFILTER_OFFSETS", false, SK_MACHINE_STR, false },
    { "DFA_TABLE",          false, SK_MACHINE_STR, false },
    { "DFA_UNIFORM_FOLDS",  false, SK_MACHINE_NUM, false },
    { "DFA_SCAN_EDGE",      false, SK_MACHINE_STR, false },
    { "DFA_START",          false, SK_MACHINE_STR, false },
    { "DFA_MATCH",          false, SK_MACHINE_STR, false },
    /* the kit's every-artifact stamps (src/gen/memfn_stamps.c) */
    { "RUN_WORDS",          false, SK_MACHINE_NUM, false },
    { "MEMFN_FORMS",        false, SK_PARTS_UNION, false },  /* the forms the parts emit */
    { "MEMFN_LIBC",         false, SK_PATTERN, false },      /* the assembled text's calls */
    { "SIMD_GUARDED_BYTES", false, SK_PATTERN, false },      /* the assembled text's bytes */
    /* the VM's stamp block (src/gen/emit_vm.c): a compound's parts are DFA
     * parts in this build, so its shell writes none of these; they are
     * classified so a VM shell (B6) is a value decision, not a crash. */
    { "VM_PREFILTER",       false, SK_MACHINE_STR, false },
    { "VM_PREFILTER_WHY",   false, SK_MACHINE_STR, false },
    { "VM_PREFILTER_LANG",  false, SK_MACHINE_STR, false },
    { "VM_PREFILTER_LANG_WHY", false, SK_MACHINE_STR, false },
    { "VM_START",           false, SK_MACHINE_STR, false },
    { "VM_RESEED",          false, SK_MACHINE_STR, false },
    { "VM_RUNGS",           false, SK_MACHINE_NUM, false },
    { "VM_STRATS",          false, SK_MACHINE_NUM, false },
    { "VM_PRUNES",          false, SK_MACHINE_NUM, false },
    { "VM_PRUNE_CEILING",   false, SK_MACHINE_STR, false },
    { "VM_ENTRY_SHAPE",     false, SK_MACHINE_STR, false },
    { "VM_FRAMELESS",       false, SK_MACHINE_NUM, false },
    { "VM_LIT_RUNS",        false, SK_MACHINE_NUM, false },
    { "VM_POSS_ARMS",       false, SK_MACHINE_NUM, false },
    { "VM_ALT_ISLANDS",     false, SK_MACHINE_NUM, false },
    { "VM_CLS_ATOMS",       false, SK_MACHINE_NUM, false },
    { "VM_CLS_FOLDS",       false, SK_MACHINE_NUM, false },
    { "VM_CLS_KIT",         false, SK_MACHINE_STR, false },
    { "VM_CALL_LINKED",     false, SK_MACHINE_NUM, false },
    { "VM_CALL_SPLICED",    false, SK_MACHINE_NUM, false },
    { "VM_ROOT_MINW",       false, SK_MACHINE_NUM, false },
    { "VM_PROGRAM_BYTES",   false, SK_MACHINE_NUM, false },
    { "UNROLL_K",           false, SK_MACHINE_NUM, false },
    { "UNROLL_K_WHY",       false, SK_MACHINE_STR, false },
    { "NSLOTS",             false, SK_MACHINE_NUM, true },
    { "FAST_FRAMES",        false, SK_MACHINE_NUM, false },
    { "FAST_TRAIL",         false, SK_MACHINE_NUM, false },
    { "CALL_TOP_NONE",      false, SK_MACHINE_NUM, true },
    { "TRACE",              false, SK_PATTERN, true },   /* a build option */
    { "R_",                 true,  SK_PATTERN, true },   /* the give-up codes */
};

/* The catalogue row for stamp `name`, or NULL. An exact name wins over a
 * family prefix. */
static const StampRow *stamp_row(const char *name)
{
    const StampRow *fam = NULL;
    for (size_t i = 0; i < sizeof stamp_rows / sizeof stamp_rows[0]; i++) {
        const StampRow *r = &stamp_rows[i];
        if (!r->family && !strcmp(r->name, name)) return r;
        if (r->family && !strncmp(r->name, name, strlen(r->name))) fam = r;
    }
    return fam;
}

/* Is `<PREFIX>_<name>` (the name after the prefix, len bytes) a stamp of
 * the caller contract: a catalogue row (exact, or a family's prefix) not
 * marked internal? The segment block's keep rule (emit_code.c; review
 * 2026-10-27-r1-ic2 F3): a name nobody catalogued is not kept. */
bool pcrec_stamp_is_contract(Ctx *cx, const char *name, size_t len)
{
    const StampRow *r = stamp_row(pcrec_sb_fragf(&cx->arena, "%.*s", (int)len, name));
    return r && !r->internal;
}

/* The sorted, distinct union of the comma lists in the shell's parts'
 * `MEMFN_FORMS`, quoted; `"none"` when no part names a form. */
static const char *parts_forms_union(Ctx *cx)
{
    const PcrecCompShell *sh = cx->job->comp_shell;
    size_t cap = 0, n = 0;
    for (int i = 0; i < PCREC_COMP_MAXPARTS; i++)
        for (const char *v = sh->text[i] ? sh->facts[i].memfn_forms : NULL; v && *v; v++)
            cap += *v == ',' || v == sh->facts[i].memfn_forms;
    const char **names = pcrec_arena_alloc(&cx->arena, (cap ? cap : 1) * sizeof *names);
    for (int i = 0; i < PCREC_COMP_MAXPARTS; i++) {
        if (!sh->text[i]) continue;
        const char *v = sh->facts[i].memfn_forms;
        while (v && *v) {
            size_t len = strcspn(v, ",");
            const char *w = pcrec_sb_fragf(&cx->arena, "%.*s", (int)len, v);
            v += len + (v[len] == ',');
            if (!strcmp(w, "none")) continue;
            size_t k = 0;
            while (k < n && strcmp(names[k], w) < 0) k++;
            if (k < n && !strcmp(names[k], w)) continue;
            memmove(&names[k + 1], &names[k], (n - k) * sizeof names[0]);
            names[k] = w;
            n++;
        }
    }
    const char *u = n ? names[0] : "none";
    for (size_t k = 1; k < n; k++) u = pcrec_sb_fragf(&cx->arena, "%s,%s", u, names[k]);
    return pcrec_sb_fragf(&cx->arena, "\"%s\"", u);
}

/* The filter a compound shell sets (`Ctx.stamp_filter`): P's value for a
 * pattern-level stamp, the declared compound value for a machine-level
 * one, and an internal error for a stamp nobody classified. The VM slot
 * legend's names are computed per program and are VM-only, so they never
 * reach a DFA shell; they are not listed. */
const char *pcrec_stamp_compound_filter(Ctx *cx, const char *name, const char *value)
{
    (void)value;
    const StampRow *r = stamp_row(name);
    if (!r)
        pcrec_ctx_fail(cx, 0, "internal error: the stamp `%s` has no row in the "
                       "stamp catalogue (src/gen/stamp_kinds.c), so its value on a "
                       "compound is undefined", name);
    switch (r->kind) {
    case SK_PATTERN:     return NULL;
    case SK_PARTS_UNION: return parts_forms_union(cx);
    case SK_MACHINE_STR: return "\"compound\"";
    case SK_MACHINE_NUM: return "-1";
    }
    return NULL;
}
