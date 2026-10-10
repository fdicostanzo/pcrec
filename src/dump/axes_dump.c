/* src/dump/axes_dump.c — [CHK-2] PIECE 1: `pcrec --list-axes`, the
 * optimization-axis registry's FOURTH TSV surface (docs/spec/registry.md).
 *
 * WHAT THIS PROVES AND WHAT IT DOES NOT (docs/dev/plan.md [CHK-2]'s own
 * boundary, restated at the one place a reader will actually see it): this
 * dump shares its source with the emitter — it reads the SAME candidate-list
 * arrays `src/gen/emit_dfa.c`'s selection walks read (`dfa_select`'s lists;
 * the one start table `cand_rows[]` for every start axis since [START-TABLE]
 * C6, `emit_cand_axis`), via the accessors declared in internal.h, and
 * hand-states the rest from
 * `lib/pcrec.h`'s own enum symbols. It proves what the compiler THINKS its options are. It is
 * NOT independent evidence that a stamp or a flag actually behaves as
 * described — the checks that read an EMITTED ARTIFACT (tests/codegen/
 * run_dfa_stamps.sh, the tuning.md differentials) are the independent side of
 * that claim, and `tests/registry/`'s axis registry check (below) is the
 * independent side of THIS dump specifically: it reads this TSV against
 * docs/spec/tuning.md and cli/main.c, two sources this file never opens.
 *
 * TWO KINDS OF ROW, named in the `kind` column:
 *
 *   "list"      — a real preference-list-of-candidate-objects exists in
 *                  emit_dfa.c (axes A-E: table, prefilter, view, seed,
 *                  accept). Candidate NAME and DENY BIT come from the SAME
 *                  `DfaCand`-headed array the emitter selects from
 *                  (src/gen/emit_dfa.c's [CHK-2] accessor block) — a
 *                  candidate added there appears here with no edit to this
 *                  file. The one-line APPLIES summary is hand-authored
 *                  prose (this file's own AXIS_DESC table), matching
 *                  docs/design/emitter_form.md §3's own "applies when"
 *                  column, because evaluating the real predicate needs a
 *                  live pattern this context-free command does not have; an
 *                  unmatched (newly-added) candidate still gets a row, with
 *                  an honest placeholder description rather than being
 *                  silently dropped.
 *   "both"      — axis F, the scan direction: not a candidate list at all
 *                  (emitter_form.md §3's own words) — both objects are
 *                  ALWAYS emitted, once each, per machine.
 *                  The fallback axes are `list` since [DEC-FALLBACK] B7:
 *                  `engine-route`, `size-term` and `prefilter-lang` project
 *                  the fallback tables' `axlist` cells, and `fallback` and
 *                  `prefilter-admit` list T1 and T2 whole, one row each
 *                  (`emit_fb_axis`, `emit_fb_table_axis`).
 *   "predicate" — the VM/engine-selection axes (`docs/spec/
 *                  tuning.md` §2.1-2.9, its coarse §2.11 engine axis) have
 *                  no candidate-list-as-data anywhere in the tree yet
 *                  (`[ENG-FORM]` relayered emit_dfa.c only — src/gen/
 *                  CLAUDE.md's own "SCOPE: emit_dfa.c first" note). Most are
 *                  the two-candidate shape a deny bit implies (the
 *                  mechanism, and the denied fallback); a stamp whose real
 *                  value set is wider than "selected"/"denied" — because the
 *                  artifact reports WHY a selection declined, or composes a
 *                  fact from more than one machine, not because the
 *                  emitter chose among named candidates — gets ONE ROW PER
 *                  VALUE instead (`engine-route` was the first instance;
 *                  `size-term`, below, and `table`'s two composite rows,
 *                  [REG-SV], are two more). A row with no deny/force macro
 *                  and no cli_flag is not reachable by any flag on its own —
 *                  it is what the artifact reports having landed on, and its
 *                  `applies` text says the condition in place of a lever.
 *                  Names and applies text are hand-stated from
 *                  `lib/pcrec.h`'s own enum symbols (never a hand-typed bit
 *                  NUMBER, so a bit's numeric position can move with no edit
 *                  here) and docs/spec/tuning.md §2's own prose, which is
 *                  exactly the "do NOT restructure the VM emitter to
 *                  manufacture lists; state the source" allowance the plan
 *                  row gives this piece. A predicate-kind row may also
 *                  attach to a `list`-kind axis (`table`'s `"none"`/
 *                  `"mixed"` rows, order 3/4): those two values are
 *                  ARTIFACT-LEVEL compositions of the forward and reverse
 *                  machine's own per-machine choice (`RX_DFA_TABLE`,
 *                  `dfa_table_name()`, src/gen/emit_dfa.c) and are never
 *                  candidates the per-machine list itself could select on
 *                  its own — see `emit_table_composite_rows` below, and
 *                  `docs/spec/registry.md` §6 for why mixing kinds within
 *                  one axis is the honest shape rather than a fifth kind.
 *
 * Wire format: docs/spec/table_contract.md (TSV, `#` comments, last `#`
 * line before data is the header, columns append-only). */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/internal.h"
#include "pcrec.h"
/* The kit's one public header, by its path from here: pcrec's sources reach
 * pcrec-memory-functions through this file and nothing else (memfn/CLAUDE.md),
 * and a relative spelling needs no -I that every from-source reference build
 * would then have to carry. */
#include "../../memfn/include/memfn.h"
/* [MEMFN] M1b the in-emitter deny map's reverse, for the run-overlap rows. */
#include "gen/memfn_sites.h"

/* ---- hand-authored one-line descriptions for the "list"/"both" rows ---- */

typedef struct {
    const char *axis;
    const char *candidate;
    const char *applies;
} AxisDesc;

/* docs/design/emitter_form.md §3's own "applies when" column, transcribed by
 * a human at review time — see this file's header for why it cannot be
 * derived. Order here does not need to match the emitter's preference
 * order; the dump orders by the LIVE array, this table is looked up by
 * (axis, candidate) name. */
static const AxisDesc AXIS_DESC[] = {
    { "table", "premultiplied", "this machine's states*classes <= 65535 and no emitted seed cell is negative" },
    { "table", "indexed", "always (fallback)" },

    { "view", "end+eol", "both a \\z view and a $/\\Z view exist on this machine" },
    { "view", "end", "a \\z view exists and no $/\\Z view does" },
    { "view", "eol", "a $/\\Z view exists and no \\z view does" },
    { "view", "none", "always (fallback) — no position view at all" },

    { "seed", "seeded", "mechanism 4: the start state depends on a context byte (\\b, (?m)^, ...)" },
    { "seed", "constant", "always (fallback)" },

    { "accept", "by-class", "some state's accept depends on the next byte (\\b/(?m)$'s class axis)" },
    { "accept", "scalar-viewed", "a position view exists (D11: recorded AFTER the view selector, never before)" },
    { "accept", "scalar-plain", "always (fallback) — recorded at the top of the loop" },

    { "direction", "forward", "always — finds where a match ENDS" },
    { "direction", "reverse", "always — finds where that match BEGINS" },
    { "direction", "anchored", "always on a DFA artifact that selects the unwrapped match-here form ([ENG-ABS]) — finds where the match beginning at ctx->pos ends" },

    { "scan-edge", "scan-edge", "per STATE: src/opt/scanedge.c found a maximal run of states differing only in how many bytes of ONE class have been counted, rooted here, and DELETED the run's interior from the table -- so this state's edge is mandatory, not an accelerator ([OPT-5])" },
    { "scan-edge", "table-walk", "always (fallback) -- this state counts nothing, or the axis is denied and the pass left every state where it was" },

    { "scan-body", "range", "the class-form table (src/gen/clskit.c ROWS, site scan) answers byte-range: the edge's class is ONE interval, tested inline against immediates (the same spelling a VM class read uses), no memory touched but the subject ([OPT-5]; D139)" },
    { "scan-body", "fold", "size-leaning --tune positions only (-2/-1): the class-form table answers byte-fold, an ASCII case pair {X, x}, tested inline as (byte | 0x20) == x; at the default positions the scan edge's pair keeps its table until D138 Q1's measurement rules the default fold for both sites; -fno-cls-fold denies it ([CLS-TREE] S2 review fixes, D139)" },
    { "scan-body", "kit", "size-leaning --tune positions only (-2/-1): the class-form table answers byte-kit, i.e. the class's kit matcher written at the edge's two test sites is smaller than its 256-byte table, tested by a static inline kit matcher <prefix>_<machine>_scankit<N>; -fno-cls-kit denies it ([CLS-TREE] S2, D131 item 5, D139 item 1)" },
    { "scan-body", "bitmap", "always (fallback) -- the class-form table answers byte-table and the table selection (TAB_ROWS, site scan) picks the scan-table row: one 256-byte membership table per edge. The load is VALUE-addressed, not result-addressed, so the cursor is still the only loop-carried register. A per-ISA SIMD run-extension form would be a form of the edge's LOOP ([OPT-SIMD]; ISA-neutral by ruling, scalar forms always the fallback)" },

};
#define N_AXIS_DESC (sizeof AXIS_DESC / sizeof AXIS_DESC[0])

/* Looks up the authored `applies` description for (axis, candidate) in
 * AXIS_DESC, or a placeholder pointing at the emitter's own `applies` function
 * when nobody has authored one yet. */
static const char *desc_of(const char *axis, const char *cand)
{
    for (size_t i = 0; i < N_AXIS_DESC; i++)
        if (!strcmp(AXIS_DESC[i].axis, axis) && !strcmp(AXIS_DESC[i].candidate, cand))
            return AXIS_DESC[i].applies;
    return "(no description authored for this candidate yet — read its "
           "`applies` function in src/gen/emit_dfa.c)";
}

/* Per-axis scalar stamp macro, where one exists — axes C-E's own
 * candidate objects have no `#define` of their own (view/seed/accept/
 * direction are emitter-internal decisions with no observable trace in the
 * artifact). Where a stamp exists, D82's own rule ("the chosen object's name
 * IS the stamp value") makes `stamp_value` exactly the candidate's own name
 * — never re-derived. The start axes (`prefilter`, `search-start`) are not
 * here: their rows carry their own stamp (`emit_cand_axis`), and so since
 * [OPT-REVEND] L0 does axis G (`match`, `RX_DFA_MATCH`): the FINISH rows. */
static const char *stamp_macro_of(const char *axis)
{
    if (!strcmp(axis, "table")) return "RX_DFA_TABLE";
    /* [OPT-5] The stamp belongs to the BODY axis, whose candidate names ARE
     * its values. The REGION axis (`scan-edge`) has no value stamp of its
     * own: what an artifact reports is which body its edges took, and
     * "table-walk everywhere" is that stamp's `"none"`. */
    if (!strcmp(axis, "scan-body")) return "RX_DFA_SCAN_EDGE";
    return "";
}

/* [OPT-K] AXIS B'S GAP IS NOW PARTLY CLOSED, and the shape of what remains is
 * worth stating rather than leaving as a shorter comment. `emitter_form.md`
 * §3 recorded that the DFA scan's prefilter axis had NO deny flag at all —
 * `PCREC_NO_PREFILTER` gates only the VM hybrid's `fit.prefilter`, never
 * `emit_unanchored`'s own start-state filter — and named [CHK-2]'s registry
 * check as where the gap belonged. `-fno-offset-skip` denies the TWO
 * offset-set candidates, so those two rows now carry a CLI spelling; the four
 * offset-0 forms (`memchr`, `byte-class`, their `-bounded` twins) still have
 * none, and that is the residue of the same finding rather than an omission
 * here. Denying them would mean choosing what a denied build emits instead,
 * which is a caller-observable change no row has asked for.
 *
 * [REVW.4] wave 4 (D111): the (axis, candidate) -> flag LADDER this comment
 * used to sit above is GONE. A candidate's CLI spelling is now derived from
 * its own deny BIT through `src/core/axes.def`, so the two facts cannot
 * disagree — and the paragraph above is still exactly true, because a
 * candidate with no deny bit derives no flag. */

/* ---- THE AXIS TABLE's two lookups (src/core/axes.def, D111) ------------
 *
 * `PcrecAxisCand.deny` comes straight off the live `DfaCand.deny` field the
 * EMITTER itself consults, and `emit_predicate_axes` below passes the
 * `lib/pcrec.h` macro directly; both are VALUES. These two functions are the
 * only place a value becomes TEXT, and both read the one table — so a bit,
 * its printed symbol name and its CLI spelling are one row and cannot drift.
 * An unrecognised nonzero value prints as a bare hex number rather than
 * silently vanishing or crashing (the merge-safety property [CHK-2]'s brief
 * asks for): a bit that has no row is visible in the dump as a number. */

/* The `#define` name (deny or force macro) whose value equals `v`, iterated
 * off core/axes.def -- the same table axis_cli_flag reads, so a bit's macro
 * name and its CLI spelling cannot drift. NULL for a bit with no row. */
static const char *axis_macro_name(uint64_t v)
{
    if (!v) return NULL;
#define PCREC_AXIS(dm, df, fm, ff, defst)                 \
    if ((dm) && (uint64_t)(dm) == v) return #dm;          \
    if ((fm) && (uint64_t)(fm) == v) return #fm;
#include "core/axes.def"
    return NULL;
}

/* The CLI spelling a row reports, rendered from the bits it carries: the
 * deny flag, the force flag, or `"deny / force"` for the two axes that are a
 * pair. A row with no bits reports nothing from here — its `cli_flag`, if it
 * has one at all, is a VALUE parameter (`--engine=`) the caller states.
 *
 * [OPT-LITSCAN] S1: a candidate removed by EITHER of two deny bits (the
 * run-pinned prefilter rows) reports both flags `|`-joined, lowest bit first
 * — docs/spec/registry.md's one convention for a multi-bit deny cell. */
static void axis_cli_flag(uint64_t deny, uint64_t force, char *buf, size_t cap)
{
    char d[96] = "";
    const char *f = NULL;
    size_t n = 0;
    buf[0] = 0;
    for (unsigned b = 0; b < 64; b++) {
        const uint64_t bit = (uint64_t)1 << b;
        const char *one = NULL;
        if (!(deny & bit)) continue;
#define PCREC_AXIS(dm, df, fm, ff, defst)                        \
        if ((dm) && (uint64_t)(dm) == bit) one = df;
#include "core/axes.def"
        if (one && n < sizeof d)
            n += (size_t)snprintf(d + n, sizeof d - n, "%s%s", n ? "|" : "", one);
    }
#define PCREC_AXIS(dm, df, fm, ff, defst)                        \
    if ((fm) && (uint64_t)(fm) == force) f = ff;
#include "core/axes.def"
    if (d[0] && f) snprintf(buf, cap, "%s / %s", d, f);
    else if (d[0]) snprintf(buf, cap, "%s", d);
    else if (f) snprintf(buf, cap, "%s", f);
}

/* The bit INDEX of the single set bit in `flag` (0 for flag<=1). */
static unsigned bit_of(uint64_t flag)
{
    unsigned b = 0;
    while (flag > 1u) { flag >>= 1; b++; }
    return b;
}

/* Renders a deny/force value's macro-name column (axis_macro_name, or a bare
 * hex number when no row claims the bit -- a merge-safety fallback) and its
 * bit-index column (bit_of) into `macro`/`bit`, one entry per set bit,
 * `|`-joined lowest first when a candidate carries more than one
 * ([OPT-LITSCAN] S1's two-bit deny; axis_cli_flag's convention). */
static void deny_cols(uint64_t v, char *macro, size_t macrocap, char *bit, size_t bitcap)
{
    size_t m = 0, k = 0;
    macro[0] = 0; bit[0] = 0;
    for (unsigned b = 0; b < 64; b++) {
        const uint64_t one = (uint64_t)1 << b;
        if (!(v & one)) continue;
        const char *n = axis_macro_name(one);
        if (m < macrocap) {
            if (n) m += (size_t)snprintf(macro + m, macrocap - m, "%s%s", m ? "|" : "", n);
            else   m += (size_t)snprintf(macro + m, macrocap - m, "%s0x%llx", m ? "|" : "",
                                         (unsigned long long)one);   /* a bit with no row */
        }
        if (k < bitcap)
            k += (size_t)snprintf(bit + k, bitcap - k, "%s%u", k ? "|" : "", bit_of(one));
    }
}

/* ---- one TSV row -------------------------------------------------------- */

/* ONE ROW, through the text layer's `pcrec_sb_row` (src/core/sb.c): twelve cells a
 * reader can count against this dump's header, each escaped so a control byte
 * in an `applies` sentence cannot split the record. `order` is the only cell
 * that is not already text; `char[16]` holds every `int` and is not the
 * `PCREC_MAX_EMIT_NAME_LEN` class of buffer (no prefix reaches it). */
static void axis_row(StrBuf *sb, const char *axis, int order,
                     const char *candidate, const char *kind,
                     const char *stamp_macro, const char *stamp_value,
                     const char *deny_macro, const char *deny_bit,
                     const char *force_macro, const char *force_bit,
                     const char *cli_flag, const char *applies)
{
    char ord[16];
    snprintf(ord, sizeof ord, "%d", order);
    const char *cells[] = { axis, ord, candidate, kind,
                            stamp_macro, stamp_value, deny_macro, deny_bit,
                            force_macro, force_bit, cli_flag, applies };
    pcrec_sb_row(sb, cells, sizeof cells / sizeof *cells);
}

/* ---- "list"/"both" axes: walked off the LIVE candidate arrays ---------- */

/* Emits one TSV row per candidate of a LIST-kind axis, walked off the live
 * candidate array `get` fills (up to 16): renders the deny/CLI-flag columns
 * from each candidate's own `.deny` bit, the stamp value (this candidate's
 * name, when the axis has a stamp macro) and the authored `applies` text
 * (desc_of). */
static void emit_dfa_list_axis(StrBuf *sb, const char *axis, const char *kind,
                               size_t (*get)(PcrecAxisCand *, size_t))
{
    PcrecAxisCand cands[16] = { { 0 } };
    size_t n = get(cands, 16);
    for (size_t i = 0; i < n; i++) {
        char deny_macro[64], deny_bit[8], flag[96];
        const char *stamp_macro = stamp_macro_of(axis);
        deny_cols(cands[i].deny, deny_macro, sizeof deny_macro, deny_bit, sizeof deny_bit);
        axis_cli_flag(cands[i].deny, 0, flag, sizeof flag);
        const char *stamp_value = stamp_macro[0] ? cands[i].name : "";
        axis_row(sb, axis, (int)(i + 1), cands[i].name, kind,
                 stamp_macro, stamp_value,
                 deny_macro, deny_bit, "", "",
                 flag,
                 desc_of(axis, cands[i].name));
    }
}

/* ---- the start axes: projected off the one start table ------------------
 *
 * [START-TABLE] C6. Every start axis (`prefilter`, `search-start`,
 * `req-admit`, `req-use`, `hyb-reseed`, `vm-anchor-bound`, `end-window`) is
 * the rows of `cand_rows[]` (src/gen/emit_dfa.c) listed under it, walked
 * live off `pcrec_cand_list_row`: name, order, deny bits, stamp macro and
 * value, and the `applies` text, which sits beside its row in that table
 * rather than in a hand table here (start_table.md §2.4 D-3: the hand table
 * had drifted from the row it described). This surface therefore cannot
 * state a row the emitter's walk does not have. Every start axis is a `list`
 * axis since C7: its rows ARE a candidate list, the table the walk reads
 * (C6 printed `predicate` for the five that had been hand-stated before
 * their tables existed, to keep the listing byte-identical through the
 * fold). */
static void emit_cand_axis(StrBuf *sb, const char *axis)
{
    PcrecCandListRow r;
    for (int i = 0; pcrec_cand_list_row(axis, i, &r); i++) {
        char deny_macro[64], deny_bit[8], flag[96];
        deny_cols(r.deny, deny_macro, sizeof deny_macro, deny_bit, sizeof deny_bit);
        axis_cli_flag(r.deny, 0, flag, sizeof flag);
        /* A row with no desc prints `desc_of`'s placeholder, which the axis
         * registry check reads as an unauthored candidate, never an empty
         * cell nothing reads. */
        axis_row(sb, axis, r.order, r.name, "list", r.stamp, r.value,
                 deny_macro, deny_bit, "", "", flag,
                 r.desc ? r.desc : desc_of(axis, r.name));
    }
}

/* [REG-SV] `table`'s TWO COMPOSITE ROWS. `RX_DFA_TABLE`'s real value set is
 * FOUR strings (`docs/spec/match_api.md` §6.3, the 2026-08-26 THIRD-machine
 * paragraph), not the two `pcrec_dfa_axis_table_cands()` reports above:
 * `dfa_table_name()` (src/gen/emit_dfa.c) answers `"none"` when the artifact
 * has no scan to have a table at all (a proven-empty engine, or ENG_ATTEMPT's
 * label-indexed dispatch, which has no transition table of this shape),
 * `"mixed"` when the forward and reverse (and, since [ENG-ABS], the anchored)
 * machines took DIFFERENT per-machine representations, and only otherwise
 * the shared representation name — which is exactly `emit_dfa_list_axis`'s
 * own two candidates above. `"none"`/`"mixed"` are therefore never a
 * candidate the per-machine `table` axis could select on its own (this
 * file's own header comment states the boundary); they are hand-stated
 * outcome rows, order continuing from the list rows above, the same
 * shape a `kind=predicate` row already has elsewhere in this dump. No
 * deny/force/cli lever exists for either — nothing asks specifically for
 * "no table" or "a mismatched pair" — so `applies` states the condition
 * in prose, as the size-term outcome rows do. */
static void emit_table_composite_rows(StrBuf *sb)
{
    axis_row(sb, "table", 3, "none", "predicate",
             "RX_DFA_TABLE", "none", "", "", "", "", "",
             "the artifact has no DFA scan-table at all: a proven-empty engine (dfa_engine_is_empty), or the ENG_ATTEMPT label-dispatch engine, which is asked first (src/gen/CLAUDE.md's [DD-13c] #5)");
    axis_row(sb, "table", 4, "mixed", "predicate",
             "RX_DFA_TABLE", "mixed", "", "", "", "", "",
             "the artifact's own machines took DIFFERENT per-machine table representations (dfa_table_name(): forward vs. reverse, and since [ENG-ABS] the anchored machine, disagree) — a per-artifact composition, never a single machine's own selection");
}

/* [OPT-5] `scan-body`'s TWO COMPOSITE ROWS, and they exist for `table`'s
 * reason exactly. `RX_DFA_SCAN_EDGE`'s real value set is SIX strings
 * (docs/spec/match_api.md §6.3) and `pcrec_dfa_axis_scanbody_cands()` reports
 * the FOUR run tests an edge can take — the class-form table's byte rows at
 * the scan site ([CLS-TREE] S2, D139 item 2). `dfa_scan_edge_name()`
 * (src/gen/emit_dfa.c) answers `"none"` when the REGION axis chose
 * `table-walk` at every state — no edge, so no body to name — and `"mixed"`
 * when the artifact's edges did not all take the same body. Neither is
 * something the per-edge list could ever select on its own.
 *
 * NEITHER CARRIES THE DENY LEVER, and that is not an oversight: the flag
 * belongs to the axis that decides whether an edge EXISTS (`scan-edge`,
 * where it is reported on that axis's own first candidate), not to the axis
 * that decides what an edge's loop looks like. `"none"` IS what a denied
 * build stamps, which the prose below says rather than the column. */
static void emit_scan_composite_rows(StrBuf *sb)
{
    axis_row(sb, "scan-body", 5, "none", "predicate",
             "RX_DFA_SCAN_EDGE", "none", "", "", "", "", "",
             "the artifact carries no scan edge, so there is no body to name: no machine has a collapsible counted run, or the engine is ENG_ATTEMPT (label dispatch, no table walk to shorten) or provably empty -- and it is also what every artifact stamps under -fno-scan-edge, which denies the scan-edge axis above rather than this one");
    axis_row(sb, "scan-body", 6, "mixed", "predicate",
             "RX_DFA_SCAN_EDGE", "mixed", "", "", "", "", "",
             "the artifact's own edges took DIFFERENT bodies (dfa_scan_edge_name(): one machine's edge tests a contiguous range, another's reads a membership table, calls a kit matcher or compares a fold pair) -- a per-artifact composition, never a single edge's own selection");
}

/* ---- "predicate" axes: no candidate-list-as-data yet -------------------
 *
 * Sourced from lib/pcrec.h's own enum symbols (the `V()` macro below
 * stringifies the identifier it is handed, so the printed macro name and
 * the value used to compute the bit number cannot drift apart — a rename
 * in lib/pcrec.h breaks this file at compile time rather than silently
 * printing a stale name) and from docs/spec/tuning.md §2's own prose for
 * the candidate names and one-line descriptions. */
typedef struct {
    const char *axis;
    const char *candidate;
    const char *stamp_macro;
    const char *stamp_value;   /* "" when the stamp is a count/bitmask,
                                 * never a single value this candidate owns */
    uint64_t    deny_val;   const char *deny_macro;
    uint64_t    force_val;  const char *force_macro;
    const char *cli_flag;
    const char *applies;
} PredAxis;

/* [REVW.4] wave 4 (D111): a row states its deny/force BITS and nothing else.
 * The symbol NAMES, the bit NUMBERS and the CLI SPELLING are all derived from
 * `src/core/axes.def` — fifteen hand-typed `cli_flag` strings and seventeen
 * hand-typed macro names used to live at these call sites, and an axis whose
 * spelling changed had to be edited in both this file and `cli/main.c` with a
 * pair of awk scrapers standing over them to notice when it was not.
 *
 * `cli_flag_lit` is for a row whose lever is NOT a flags bit at all — the
 * `engine` axis's `--engine=vm`/`--engine=dfa`, a VALUE parameter and
 * do-or-die. A row never has both: if it carries bits, the spelling is
 * derived, and passing a literal too would be a second spelling of one
 * fact. */
static void emit_kind_row(StrBuf *sb, const PredAxis *p, const char *kind, int order,
                          const char *candidate, const char *stamp_value,
                          uint64_t deny_val, uint64_t force_val,
                          const char *cli_flag_lit, const char *applies)
{
    char db[8] = "", fb[8] = "", flag[96];
    if (deny_val) snprintf(db, sizeof db, "%u", bit_of(deny_val));
    if (force_val) snprintf(fb, sizeof fb, "%u", bit_of(force_val));
    axis_cli_flag(deny_val, force_val, flag, sizeof flag);
    axis_row(sb, p->axis, order, candidate, kind,
             p->stamp_macro, stamp_value,
             deny_val ? axis_macro_name(deny_val) : "", db,
             force_val ? axis_macro_name(force_val) : "", fb,
             (deny_val || force_val) ? flag : cli_flag_lit, applies);
}

static void emit_pred_row(StrBuf *sb, const PredAxis *p, int order,
                          const char *candidate, const char *stamp_value,
                          uint64_t deny_val, uint64_t force_val,
                          const char *cli_flag_lit, const char *applies)
{
    emit_kind_row(sb, p, "predicate", order, candidate, stamp_value,
                  deny_val, force_val, cli_flag_lit, applies);
}

/* [DEC-FALLBACK] B6/B7: the three fallback axes (`engine-route`, `size-term`,
 * `prefilter-lang`) are projected off the tables' `axlist` columns
 * (`pcrec_fb_list_row`, src/core/compile.c) rather than stated here: name,
 * order, deny/force bits, lever spelling and `desc` sit beside their rows, so
 * this surface cannot list a candidate the walk does not have. They are
 * `kind=list` (B7): a candidate list of rows, in the order the tables walk
 * them. `stamp` is the axis's stamp macro, which names the artifact's side of
 * the listing and is not a table fact. */
static void emit_fb_axis(StrBuf *sb, const char *axis, const char *stamp)
{
    PredAxis p = { axis, NULL, stamp, "", 0, NULL, 0, NULL, NULL, NULL };
    const FbList *l;
    for (int i = 0; (l = pcrec_fb_list_row(axis, i)); i++)
        emit_kind_row(sb, &p, "list", l->order, l->name, l->name, l->deny, l->force, l->cli, l->desc);
}

/* [DEC-FALLBACK] B7 (Q4(b)): T1 and T2 listed WHOLE, one `list` candidate per
 * table row in walk order, as the `fallback` and `prefilter-admit` axes. A
 * row's name and caller deny bit are its cells and its `applies` text is
 * generated from the rest (`pcrec_fit_table_row`, `pcrec_pf_admit_table_row`).
 * They have no stamp macro: the tokens they feed are listed by the three
 * axes above, which hold the per-VALUE view of the same tables. */
static void emit_fb_table_axis(StrBuf *sb, const char *axis,
                               bool (*row)(int, FbTabRow *))
{
    PredAxis p = { axis, NULL, "", "", 0, NULL, 0, NULL, NULL, NULL };
    FbTabRow r;
    for (int i = 0; row(i, &r); i++)
        emit_kind_row(sb, &p, "list", i + 1, r.name, "", r.deny, 0, "", r.desc);
}

/* `--list-axes`' eleven hand-stated VM/engine-selection axis rows — the
 * ones with no candidate-list-as-data anywhere in the tree yet, unlike the
 * six DFA layer-1 axes above this function, which are walked live off
 * `emit_dfa.c`'s own candidate arrays. Each block is one axis: its rungs
 * in preference order, the deny flag and stamp bit that address it, and a
 * one-line description transcribed from `docs/spec/tuning.md`. No `if`, no
 * loop — a straight-line list of `emit_pred_row` calls, one axis-table
 * centralization away from its own remedy (not built here; see the file's
 * own header for what the dump proves and does not). */
static void emit_predicate_axes(StrBuf *sb)
{
    /* possessify — tuning.md §2.1, RX_VM_STRATS's own named pair */
    {
        PredAxis p = { "possessify", NULL, "RX_VM_STRATS", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "possessive", "PCREC_VM_STRAT_POSSESSIVE",
                     PCREC_NO_POSSESSIFY, 0, "",
                     "per A_REP: possessify.c proves the loop's body can never profitably re-enter");
        emit_pred_row(sb, &p, 2, "backtracking", "PCREC_VM_STRAT_BACKTRACKING",
                     0, 0, "", "always (fallback)");
    }
    /* [ART-POSS-ARMS] the two possessify ARMS — tuning.md §2.44/§2.45. The
     * stamp is RX_VM_POSS_ARMS; a row's stamp value is the bit it sets (the
     * bits are match_api.md §6.3's, not named constants). poss-ctx-follow is
     * ENGINE-SELECTING (the free discharge asks the same verdict). */
    {
        PredAxis p = { "poss-ctx-follow", NULL, "RX_VM_POSS_ARMS", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "a0", "0x1",
                     PCREC_NO_POSS_CTX_FOLLOW, 0, "",
                     "per A_REP: a lookahead-born context gate in the follow narrows to the characters it admits with nothing known on its left (S(P) at P = {0,1})");
        emit_pred_row(sb, &p, 2, "a1", "0x2",
                     PCREC_NO_POSS_CTX_FOLLOW, 0, "",
                     "per greedy A_REP with m >= 1: row 3 re-asked over the loop's continuation, each gate valued by the polarities of the body's LAST classes");
        emit_pred_row(sb, &p, 3, "widen", "",
                     0, 0, "", "always (fallback) — a gate widens the follow to every byte; ENGINE-SELECTING: a possessive suffix the arm would discharge stays, so RX_ENGINE can move to \"vm\"");
    }
    {
        PredAxis p = { "poss-bref-first", NULL, "RX_VM_POSS_ARMS", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "group-text", "0x4",
                     PCREC_NO_POSS_BREF_FIRST, 0, "",
                     "per A_BREF: FIRST is the union of every referenced group's captured-TEXT first characters, folded when the reference is caseless (in progress or past PCREC_MAX_POSS_REF_DEPTH: widen)");
        emit_pred_row(sb, &p, 2, "widen", "",
                     0, 0, "", "always (fallback) — every byte, nullable");
    }
    /* revdet — §2.2, RX_VM_RUNGS bit PCREC_VM_RUNG_REVDET */
    {
        PredAxis p = { "revdet", NULL, "RX_VM_RUNGS", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "revdet", "PCREC_VM_RUNG_REVDET",
                     PCREC_NO_REVDET, 0, "",
                     "per A_REP: forward unique-iteration lets the body run backward with no choice points");
        emit_pred_row(sb, &p, 2, "denied", "",
                     0, 0, "", "always (fallback) — the ladder's next rung (counter, or literal frames)");
    }
    /* counter — §2.3, RX_VM_RUNGS bit PCREC_VM_RUNG_COUNTER */
    {
        PredAxis p = { "counter", NULL, "RX_VM_RUNGS", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "counter", "PCREC_VM_RUNG_COUNTER",
                     PCREC_NO_COUNTER, 0, "",
                     "per A_REP: a bounded repeat, unrolled by --unroll=K (default PCREC_DEFAULT_UNROLL_K), below the replication cap");
        emit_pred_row(sb, &p, 2, "denied", "",
                     0, 0, "", "always (fallback) — literal replication (frames)");
    }
    /* [ART-SIZE]/[REG-SV] size-term — the UNROLL LADDER's selection, D84.
     * `<PREFIX>_UNROLL_K_WHY` is the stamp, and it carries SEVEN values
     * (docs/spec/match_api.md §6.3, docs/spec/tuning.md §2.16) — one row per
     * value here, `engine-route`'s own shape, because five of the seven are
     * OUTCOMES the artifact reports (why the ladder ran and what it landed
     * on) rather than candidates this registry's usual deny-bit mechanism
     * denies one at a time. The seven rows are written in the SAME priority
     * order `src/core/compile.c`'s own derivation tests them in (T4,
     * `st_whys[]`, walked right before `pcrec_emit_vm`/`pcrec_emit_dfa`;
     * [DEC-FALLBACK] B5 replaced the ternary chain that held this order) — one
     * derivation, two readers, never re-decided here — so row 7 is T4's own
     * unconditional last row
     * and the axis's own "last entry always applies" rule holds for this
     * predicate axis too, not only for the `list`-kind ones.
     *
     * ONLY ROW 2 ("denied") CARRIES A LEVER: `PCREC_NO_SIZE_TERM`/
     * `-fno-size-term` stops the ladder from running at all. That bit used
     * to sit on the row named "size-model" (order 1 before this pass) —
     * WRONG: denying the axis makes the artifact stamp `"denied"`, never
     * `"size-model"`, which is the very drift [REG-SV] was opened to find
     * (a hand-typed row whose stamp_value the emitter can never actually
     * produce is worse than an empty one, because it reads as covered).
     * Row 1 ("option") has a real lever too (`--unroll=K` on the command
     * line) but it is a VALUE parameter rather than a `pcrec_options.flags`
     * bit, so it has no `deny_macro`/`cli_flag` to report here — the same
     * shape `engine`'s `--engine=` rows would be in if they had no coarse
     * do-or-die special case; `applies` states the lever in prose instead,
     * matching `deny_bit`/`force_bit`'s own empty-string convention for a
     * fact this table's columns cannot carry. Rows 3-7 have no lever at
     * all: nothing denies "the ladder chose K by argmin" specifically. */
    /* [DEC-FALLBACK] B6: the seven rows above are T4's (`st_whys[]`, src/core/compile.c) `axlist` cells. */
    emit_fb_axis(sb, "size-term", "RX_UNROLL_K_WHY");
    /* length-prune — §2.4, RX_VM_PRUNES's own named pair */
    {
        PredAxis p = { "length-prune", NULL, "RX_VM_PRUNES", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "clamped", "PCREC_VM_PRUNE_CLAMPED",
                     PCREC_NO_LENGTH_PRUNE, 0, "",
                     "per A_REP: a minimum-remaining-length bound is derivable for this quantifier's rung");
        emit_pred_row(sb, &p, 2, "unclamped", "PCREC_VM_PRUNE_UNCLAMPED",
                     0, 0, "", "always (fallback) — no bound derivable, or the axis denied");
    }
    /* vm-prefilter — §2.5, the ONE force pair; RX_VM_PREFILTER's own values.
     * NOT the same axis as "prefilter" above (docs/spec/tuning.md §3.1: "the
     * two prefilter macros are two different selections") — this one is
     * whether the VM runs a capture-erased DFA ahead of its program at all. */
    {
        PredAxis p = { "vm-prefilter", NULL, "RX_VM_PREFILTER", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "hybrid", "hybrid",
                     PCREC_NO_PREFILTER, PCREC_FORCE_PREFILTER, "",
                     "auto+captures selects it jointly with the engine (select_engine.c); -fprefilter REFUSES on a pure-DFA-selected pattern (do-or-die)");
        emit_pred_row(sb, &p, 2, "none", "none",
                     0, 0, "", "always (fallback) — also the --engine=vm side effect (R21 E-6)");
    }
    /* [OPT-4] prefilter-lang — §2.15, K39. A THIRD axis in the prefilter
     * neighbourhood and a third question: "prefilter" is the DFA scan's own
     * candidate-start filter, "vm-prefilter" is whether the VM runs a DFA
     * ahead of its program at all, and this is WHICH LANGUAGE that DFA
     * recognises. All three can be answered independently by one artifact.
     * `RX_VM_PREFILTER_LANG` is emitted only where `RX_VM_PREFILTER` reads
     * "hybrid", for the reason the `RX_DFA_*` pair is (there is no language to
     * name where there is no machine).
     *
     * THE AXIS'S STAMP IS THE LANG MACRO, NOT ITS `_WHY` COMPANION, and the
     * distinction is this table's own: a row names the macro whose VALUE
     * SELECTS the candidate. `RX_VM_PREFILTER_LANG_WHY` says which conjunct
     * decided, which is a different question and one with six answers
     * against this axis's two, so it would not fit a candidate column. It is
     * specified in docs/spec/tuning.md §2.17 beside the values below.
     * (`size-term` above is the other shape — there the `_WHY` macro IS the
     * selector, because that axis has no separate value stamp.) */
    /* [DEC-FALLBACK] B6: the two rows above are T3's (`pflw_rows[]`, src/core/compile.c) `axlist` cells. */
    emit_fb_axis(sb, "prefilter-lang", "RX_VM_PREFILTER_LANG");
    /* altcls-merge — §2.6, RX_ALTCLS_MERGES is an ACTIVITY COUNT, not a
     * named value — stamp_value left empty on both rows for that reason. */
    {
        PredAxis p = { "altcls-merge", NULL, "RX_ALTCLS_MERGES", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "merged", "",
                     PCREC_NO_ALTCLS_MERGE, 0, "",
                     "a maximal run of single-character alternation branches qualifies (runs before either engine is built)");
        emit_pred_row(sb, &p, 2, "denied", "",
                     0, 0, "", "always (fallback)");
    }
    /* altcls-factor — §2.7 */
    {
        PredAxis p = { "altcls-factor", NULL, "RX_ALTCLS_FACTORED", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "factored", "",
                     PCREC_NO_ALTCLS_FACTOR, 0, "",
                     "a maximal run sharing a literal first byte qualifies, on stage 1's own output");
        emit_pred_row(sb, &p, 2, "denied", "",
                     0, 0, "", "always (fallback)");
    }
    /* [ENG-ISL] alt-island — §2.20. RX_VM_ALT_ISLANDS is an ACTIVITY COUNT,
     * not a named value — stamp_value left empty on both rows for the reason
     * altcls-merge's own comment gives one axis up. */
    {
        PredAxis p = { "alt-island", NULL, "RX_VM_ALT_ISLANDS", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "island", "",
                     PCREC_NO_ALT_ISLAND, 0, "",
                     "per flat alternation on the VM route: the whole subtree's language is a finite set of literal byte strings within the emitter's enumeration budget (a caseless alternation is class-leading by D23 and declines)");
        emit_pred_row(sb, &p, 2, "denied", "",
                     0, 0, "", "always (fallback) — vm_alt's serial resume chain, one frame per untried branch");
    }
    /* [FORM-CHAR] cls-fold — §2.22. RX_VM_CLS_FOLDS is an ACTIVITY COUNT,
     * stamp_value left empty on both rows for alt-island's reason above. */
    {
        PredAxis p = { "cls-fold", NULL, "RX_VM_CLS_FOLDS", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "fold", "",
                     PCREC_NO_CLS_FOLD, 0, "",
                     "per VM pool class: the set is exactly an ASCII fold pair (two members differing only in bit 0x20, both letters — what D23's parse-time caseless folding produces), so the test is one or-mask-and-compare and the 32-byte bitmap is not emitted");
        emit_pred_row(sb, &p, 2, "denied", "",
                     0, 0, "", "always (fallback) — the class keeps its singleton/range/bitmap shape");
    }
    /* [CLS-TREE] S4 cls-kit — §2.33. RX_VM_CLS_KIT is an ACTIVITY COUNT
     * (distinct kit matchers), stamp_value empty for alt-island's reason. */
    {
        PredAxis p = { "cls-kit", NULL, "RX_VM_CLS_KIT", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "kit", "",
                     PCREC_NO_CLS_KIT, 0, "",
                     "per wide class on the VM route (members encode deeper than one code unit, more than one member) where the encoding has a one-character decode entry: decode one character and test it with the class-matcher kit's function, its form chosen by the --tune class table (src/gen/clskit.c)");
        emit_pred_row(sb, &p, 2, "denied", "",
                     0, 0, "", "always (fallback) — the class's byte alternation, and every one-member class (a literal) keeps its bytes");
    }
    /* [OPT-CLSPACK] cls-pack — §2.34. RX_VM_CLS_ATOMS is an ACTIVITY COUNT
     * (the shared table's atoms), stamp_value empty for alt-island's reason.
     * The one artifact-level row of src/gen/clskit.c's TAB_ROWS. */
    {
        PredAxis p = { "cls-pack", NULL, "RX_VM_CLS_ATOMS", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "atom", "",
                     PCREC_NO_CLS_PACK, 0, "",
                     "per VM artifact: at least 11 of its byte classes read a table (no singleton/range/fold compare covers them) and their byte partition has at most 64 atoms, so they share ONE 256-byte byte->atom table with a 64-bit mask per class instead of a 32-byte bitmap each (src/gen/clskit.c TAB_ROWS); -fno-cls-kit denies this row too");
        emit_pred_row(sb, &p, 2, "denied", "",
                     0, 0, "", "always (fallback) — a 32-byte bitmap per table-read class");
    }
    /* [OPT-LITSCAN] S2a lit-run — §2.31. RX_VM_LIT_RUNS is an ACTIVITY
     * COUNT, stamp_value left empty on both rows for alt-island's reason.
     * F5 (D127, abi 43) narrowed the floor from two to three: it lives in
     * pcrec_lit_run itself, so this row's prose narrows with it. */
    {
        PredAxis p = { "lit-run", NULL, "RX_VM_LIT_RUNS", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "run", "",
                     PCREC_NO_LIT_RUN, 0, "",
                     "per VM literal run: three or more consecutive one-byte literals on one concatenation (pcrec_lit_run; a two-byte pair keeps its own byte chain), or an island's single-child trie chain, compared as one bounds check and one run compare (run-overlap's rows)");
        emit_pred_row(sb, &p, 2, "denied", "",
                     0, 0, "", "always (fallback) — one per-byte compare per literal");
    }
    /* [OPT-LITSCAN] S4 run-overlap — §2.38, the run compare's rows WALKED
     * LIVE off the kit's own table (`mf_run_rows`, memfn/src/runcmp.c,
     * [MEMFN] M1b), so this surface cannot state a predicate the renderer
     * does not ask. Each row's MF_D_* deny is shown as pcrec's flag through
     * the one deny map (`pcrec_memfn_deny_flags`). RX_RUN_WORDS is an
     * ACTIVITY COUNT, stamp_value empty for alt-island's reason. */
    {
        PredAxis p = { "run-overlap", NULL, "RX_RUN_WORDS", "", 0, NULL, 0, NULL, NULL, NULL };
        const mf_run_row *r;
        for (size_t i = 0; (r = mf_run_rows(i)) != NULL; i++)
            emit_pred_row(sb, &p, (int)i + 1, r->name, "",
                         pcrec_memfn_deny_flags(r->deny), 0, "", r->doc);
    }
    /* [OPT-ANCHOR-VM] vm-anchor-bound — §2.25. The VM's attempt-loop start
     * bound: the BOUND rows of `cand_rows[]` listed on the VM route since
     * [START-TABLE] C6 (C5 made `<PREFIX>_VM_START` read the same rows, so the
     * listing and the stamp name one set). Its stamp is a closed TOKEN, so
     * `stamp_value` is spelled on every row; the two anchored rows show
     * `-fno-vm-anchor-bound`, the `start_anchor` FACT's deny, as a projection
     * (start_table.md §3.7): the bit empties the landmark, not the row.
     *
     * THE AXIS IS THE VM's AND THE FACT IS NOT. The same three values
     * describe the DFA's `start_max`, which this dump reports nowhere because
     * that emitter derives it from its own machine; the `search-start` axis
     * above is a different question (where the MATCH begins once one is
     * found), not this one (where an ATTEMPT may begin at all). */
    emit_cand_axis(sb, "vm-anchor-bound");
    /* [OPT-ENDWIN] end-window — §2.26. The END-ANCHOR START WINDOW: the
     * WINDOW rows of `cand_rows[]` since [START-TABLE] C6, on BOTH engines.
     *
     * `stamp_value` IS SPELLED ON THE FALLBACK ROW AND EMPTY ON THE OTHER,
     * which no other axis in this dump does, and the asymmetry is the stamp's
     * own shape rather than an omission: `<PREFIX>_END_WINDOW` carries a
     * NUMBER when the analysis proved a bound (there is no named value to
     * put here, `alt-island`'s reason) and the literal token `"none"` when it
     * declined (which IS a named value, and a consumer buckets on it). The
     * `window` row shows `-fno-end-window`, the `end_window` FACT's deny, as
     * a projection (§3.7). */
    emit_cand_axis(sb, "end-window");
    /* [OPT-REQBYTE] req-byte — §2.27. The NECESSARY-BYTE whole-window
     * pre-check, from the `req_byte` fact's one AST-level derivation, on BOTH
     * engines' search entries. `stamp_value` is spelled on the fallback row
     * and empty on the other, `end-window`'s asymmetry one axis up and for
     * its reason: the stamp carries a NUMBER where the analysis found a byte
     * and the token `"none"` where it did not. */
    {
        PredAxis p = { "req-byte", NULL, "RX_REQ_BYTE", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "byte", "",
                     PCREC_NO_REQ_BYTE, 0, "",
                     "per artifact, both engines: every match of the pattern must contain some literal byte (a bottom-up AST walk — concatenation unions, alternation intersects, a min-0 quantifier contributes nothing, a one-byte class is a singleton, a backreference/call/assertion is empty), so ONE memchr over [search_from, subject_length) answers NOMATCH for the whole call; the stamp carries the byte, the RIGHTMOST member like PCRE2's own LASTCODEUNIT");
        emit_pred_row(sb, &p, 2, "none", "none",
                     0, 0, "",
                     "always (fallback) — no byte is necessary on every path (an alternation with no common literal, a caselessly folded literal, a nullable quantifier), or the deny flag");
    }
    /* [OPT-REQPOS] tier 2b req-run — §2.28. The NECESSARY literal RUN, the
     * same fact at word grain, from the `req_run` fact's second accumulator on the
     * same walk. `req-byte` above is its `L = 1` case, which is why the two
     * rows read as one mechanism at two grains and why the run's own stamp
     * carries the scan member's INDEX as well as the bytes. */
    {
        PredAxis p = { "req-run", NULL, "RX_REQ_RUN", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "run", "",
                     PCREC_NO_REQ_RUN, 0, "",
                     "per artifact, both engines: every match of the pattern must contain a RUN of contiguous positions carrying at least 16 bits of information, each position a literal byte or (req-run-fold) a two-member cube such as a caseless letter (the same bottom-up walk as req-byte with a second accumulator — a concatenation joins the left factor's guaranteed suffix to the right factor's guaranteed prefix, an alternation keeps only its branches' common prefix and suffix, nothing is joined across a repeat's iterations), so one memchr for the run's rarest member plus one run compare per hit answers NOMATCH for the whole call where the byte alone could not; the stamp carries the run's bytes in lowercase hex and the scanned member's index");
        emit_pred_row(sb, &p, 2, "none", "none",
                     0, 0, "",
                     "always (fallback) — no run of two or more bytes is necessary (a single literal between non-literals, a caselessly folded literal, an alternation with no common affix), or either this axis's deny flag or -fno-req-byte's");
    }
    /* [OPT-LITSCAN] S4 C3 req-run-fold — §2.39. The necessary run's CUBE
     * positions (src/facts/req.c): a FACT-LEVEL deny, so its activity record
     * is `RX_REQ_RUN`'s `/mask` suffix, which only a masked run carries;
     * stamp_value empty for that reason (the stamp holds the run, not a
     * token). */
    {
        PredAxis p = { "req-run-fold", NULL, "RX_REQ_RUN", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "cube", "",
                     PCREC_NO_REQ_RUN_FOLD, 0, "",
                     "per necessary-run position, both engines: a class that is one two-member cube (a caseless letter [Ss], [jk], an alternation's one-bit hull fr[ae]) joins the run as a masked position; runs are ranked by information (popcount of each position's mask, 8 per byte, 7 per pair), an alternation's common head and tail are the cube hull of its branches, and the pre-check compares a masked run masked and scans a two-member position as two memchr streams; the stamp's run carries a /mask suffix");
        emit_pred_row(sb, &p, 2, "exact", "",
                     0, 0, "",
                     "always (fallback) — single bytes only, the pre-row walk, ranked by length; the deny flag");
    }
    /* [OPT-PRECHECK-ADMIT] [K82] req-admit — §2.29/§2.40. The whole-window
     * pre-check's admission rows: the PRESENCE rows of `cand_rows[]`
     * (src/gen/emit_dfa.c, since [START-TABLE] C4), projected since C6 with
     * the `desc` beside each row, so this surface cannot state a predicate
     * the emitter does not ask. Its stamp is `RX_REQ_WHY`; `set-leads` is a
     * SHAPE of an emitted pre-check, so it stamps `emitted` too. */
    emit_cand_axis(sb, "req-admit");
    /* [K82] (B) req-use — §2.41. What the body does with an emitted run
     * pre-check's answer: the FIRST rows of `cand_rows[]`, as req-admit's
     * are PRESENCE's. Its stamp is `RX_REQ_HANDOFF`, whose value on the
     * `handoff` row is the artifact's own K, so no row names a fixed value. */
    emit_cand_axis(sb, "req-use");
    /* [K50] startpos-guard — §2.23. A CONTRACT AXIS, NOT ANSWER-IDENTICAL:
     * each row describes a real semantics for a mid-character caller
     * startpos, and which one an artifact carries is a contract fact rather
     * than a shape choice. Its stamp is a closed TOKEN, so `stamp_value` is
     * spelled on every row — unlike the two activity counts above, where
     * there is no per-row value to name. [UTF-VALID] (D133) added the third
     * value, `align`, as the axis's FORCE column: it is first because a
     * caller who asked for it gets it wherever the encoding restricts a
     * position at all. */
    {
        PredAxis p = { "startpos-guard", NULL, "RX_STARTPOS_GUARD", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "align", "align",
                     0, PCREC_FORCE_STARTPOS_ALIGN, "",
                     "per artifact, -fstartpos-guard=align: this encoding has positions that are not character boundaries, so a mid-character caller startpos other than 0 is advanced to the next character start ONCE, at entry (a search runs from there; an anchored match-here entry answers -1). For a misaligned pointer into valid text (D133); -futf-check then validates from the aligned position");
        emit_pred_row(sb, &p, 2, "guarded", "guarded",
                     PCREC_NO_STARTPOS_GUARD, 0, "",
                     "per artifact: this encoding has positions that are not character boundaries (PcrecEnc.start_cls), so the entries refuse a mid-character caller startpos with PCREC_ERR_STARTPOS — libpcre2's own PCRE2_UTF behaviour (BADUTFOFFSET)");
        emit_pred_row(sb, &p, 3, "permissive", "permissive",
                     0, 0, "", "always (fallback) — the artifact answers at whatever position the caller named (utf8_design.md §2.6.1.1's ruled semantics), and on a byte artifact this row is the ONLY one reachable: every position is a boundary there and no setting emits a guard");
    }
    /* [UTF-VALID] utf-check — §2.36. The SECOND CONTRACT AXIS, OFF by
     * default: the rows read `comments`' direction, the force flag reaching
     * the non-default row. `inert` is first because it answers for the
     * ENCODING before the flag is asked: a backend under which every byte
     * string is valid has nothing to check (its table carries no
     * value-validity row, src/enc/enc.h), whatever the caller passed. */
    {
        PredAxis p = { "utf-check", NULL, "RX_UTF_CHECK", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "inert", "inert",
                     0, 0, "",
                     "per artifact: this encoding has no ill-formed byte strings (byte), so no check is emitted and the flag, if passed, is masked out of rx_info.flags");
        emit_pred_row(sb, &p, 2, "whole", "whole",
                     0, PCREC_FORCE_UTF_CHECK, "",
                     "per artifact, -futf-check: every entry that takes a subject refuses the call with PCREC_ERR_UTF when an ill-formed sequence begins in [startpos - LB, n) — PCRE2_UTF's own contract, checked after the K50 guard and before any attempt; <prefix>_valid_upto(s, n, startpos) gives the offset");
        emit_pred_row(sb, &p, 3, "off", "off",
                     0, 0, "",
                     "always (fallback, THE DEFAULT) — the artifact is invalid-tolerant: an ill-formed sequence matches nothing and is not reported (PCRE2_MATCH_INVALID_UTF's semantics); <prefix>_valid_upto is still emitted, the find-all escape (match_api.md §3.1.2)");
    }
    /* [EMIT-VERB] comments — §2.24, D112. THE ONE AXIS IN THIS DUMP THAT IS
     * OFF BY DEFAULT, so its ROWS READ IN THE OTHER DIRECTION: order 1 is
     * what a build gets by default (comment-free) and the FORCE flag is what
     * reaches order 2, where every other force pair here forces the rung the
     * compiler would otherwise choose. It has NO STAMP — the prose's presence
     * is its own record, and a `<PREFIX>_COMMENTS` macro would be a second
     * fact about the first, readable off a file some other tool had stripped.
     * That is why `stamp_macro` is empty rather than pointing somewhere. */
    {
        /* WHICH ROW IS THE DEFAULT IS DERIVED, not typed. `axes.def`'s
         * `default_state` column is the one home of that fact (D111), so the
         * dump asks it rather than carrying a sentence that would have to be
         * re-pinned the day the column flips — which is exactly what
         * [EMIT-VERB] does to this row between its two events. */
        const bool full_by_default =
            pcrec_axis_on(0, PCREC_NO_COMMENTS, PCREC_FORCE_COMMENTS);
        PredAxis p = { "comments", NULL, "", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "essential-only", "",
                     PCREC_NO_COMMENTS, 0, "",
                     full_by_default
                       ? "-fno-comments: the artifact keeps only its ESSENTIAL comments — the generated-by/pattern-echo provenance line and the emitted rx_ctx/rx_matchfn/rx_info ABI block docs/spec/match_api.md names as the embedder's contract — and drops the rest"
                       : "THE DEFAULT (D112): the artifact keeps only its ESSENTIAL comments — the generated-by/pattern-echo provenance line and the emitted rx_ctx/rx_matchfn/rx_info ABI block docs/spec/match_api.md names as the embedder's contract — and drops the rest; -fno-comments states it explicitly and overrides a config/target row that asked for the full set");
        emit_pred_row(sb, &p, 2, "full", "",
                     0, PCREC_FORCE_COMMENTS, "",
                     full_by_default
                       ? "THE DEFAULT: every comment the emitter has to offer (the orientation block, the table legends, the per-label role text); -fcomments states it explicitly. Changes no answer and no object byte — the C compiler discards comments — so it is a SOURCE-readability axis and never a performance one ([ART-SIZE]: comments vs .o size r=0.43)"
                       : "-fcomments: every comment the emitter has to offer (the orientation block, the table legends, the per-label role text). Changes no answer and no object byte — the C compiler discards comments — so it is a SOURCE-readability axis and never a performance one ([ART-SIZE]: comments vs .o size r=0.43)");
    }
    /* memfn-simd — the memory-function kit's ONE switch (D147 addenda 6-7).
     * OFF by default and INERT until R4e': no SIMD form exists, so both rows
     * render the same artifact. The stamp is the kit's own record of what it
     * rendered; `none` is its value for an artifact identical to the
     * portable one. */
    {
        PredAxis p = { "memfn-simd", NULL, "RX_MEMFN_FORMS", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "portable", "none",
                     PCREC_NO_MEMFN_SIMD, 0, "",
                     "THE DEFAULT: the kit renders portable C only (plain C, SWAR, libc calls, loop-free forms); runs on any target. -fno-memfn-simd states it explicitly and overrides a config/target row that asked for the SIMD forms");
        emit_pred_row(sb, &p, 2, "simd", "",
                     0, PCREC_FORCE_MEMFN_SIMD, "",
                     "-fmemfn-simd: the kit may render hardware-optimized forms that MAY NOT EXECUTE ON ANOTHER CPU. Inert until a SIMD form exists (R4e'): today both settings render the same artifact");
    }
    /* atomic-discharge — §2.8, ENGINE-SELECTING; no dedicated stamp of its
     * own (its activity is folded into RX_VM_STRATS via vm_cuts(); RX_ENGINE
     * is the observable consequence when it changes which engine a pattern
     * gets). */
    {
        PredAxis p = { "atomic-discharge", NULL, "", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "discharged", "",
                     PCREC_NO_ATOMIC_DISCHARGE, 0, "",
                     "possessify's own verdict proves the A_ATOMIC node's cut is a no-op (docs/design/atomic_groups_design.md §5.3)");
        emit_pred_row(sb, &p, 2, "denied", "",
                     0, 0, "", "always (fallback) — ENGINE-SELECTING: the A_ATOMIC node stays, which is DFA-excluding, so RX_ENGINE can move to \"vm\"");
    }
    /* [UCP] U2 ctx-node — §2.32, ENGINE-SELECTING; T3's rows WALKED LIVE off
     * `pcrec_look_rows` (src/parse/ctxnode.c), so this surface cannot state
     * a predicate the recognizer does not ask. No stamp: RX_ENGINE is the
     * observable consequence when it moves a pattern VM -> DFA. */
    {
        PredAxis p = { "ctx-node", NULL, "", "", 0, NULL, 0, NULL, NULL, NULL };
        for (int i = 0; i < pcrec_look_nrows; i++)
            emit_pred_row(sb, &p, i + 1, pcrec_look_rows[i].name, "",
                         pcrec_look_rows[i].deny, 0, "",
                         pcrec_look_rows[i].applies_desc);
    }
    /* [OPT-HYB-RESEED] hyb-reseed — §2.35, the VM hybrid's retry re-seed:
     * the RETRY rows of `cand_rows[]` (since [START-TABLE] C5; was
     * `pcrec_reseed_rows[]`), projected since C6 with the `desc` beside each
     * row, so this surface cannot state a predicate the emitter does not
     * ask. The row's listed name is the RX_VM_RESEED value it stamps. */
    emit_cand_axis(sb, "hyb-reseed");
    /* splice-calls — §2.9, ENGINE-SELECTING; RX_VM_CALL_SPLICED/_LINKED are
     * two separate counts, one per candidate. */
    {
        PredAxis p1 = { "splice-calls", NULL, "RX_VM_CALL_SPLICED", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p1, 1, "spliced", "",
                     PCREC_NO_SPLICE_CALLS, 0, "",
                     "the callee is not in a call-graph cycle and its expansion fits the splice size budget (PCREC_MAX_SPLICE_NODES/_TOTAL)");
        PredAxis p2 = { "splice-calls", NULL, "RX_VM_CALL_LINKED", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p2, 2, "linked", "",
                     0, 0, "", "always (fallback) — ENGINE-SELECTING: a linked call is structurally VM-only");
    }
    /* tiered-entry — §2.12, RX_FAST_FRAMES/_TRAIL (numeric; FAST==RESUME/
     * TRAIL is how a denied artifact is told apart). */
    {
        PredAxis p = { "tiered-entry", NULL, "RX_FAST_FRAMES", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "tiered", "",
                     PCREC_NO_TIERED_ENTRY, 0, "",
                     "the stamped default resume/trail storage does not fit one 4KB page (docs/spec/match_api.md §10.9)");
        emit_pred_row(sb, &p, 2, "single-tier", "",
                     0, 0, "", "always (fallback) — FAST_FRAMES==RESUME_FRAMES, FAST_TRAIL==TRAIL_FRAMES");
    }
    /* [OPT-VEDGE] view-edge — §2.37, the view-tolerant half of the scan
     * edge (src/opt/scanedge.c). It widens which chains `scan-edge` row 1
     * takes and adds no stamp value: RX_DFA_SCAN_EDGE leaving "none" on a
     * `(?:[a-z]{0,n})\z`-shaped artifact is its observable consequence. */
    {
        PredAxis p = { "view-edge", NULL, "RX_DFA_SCAN_EDGE", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "view-tolerant", "",
                     PCREC_NO_VIEW_EDGE, 0, "",
                     "per CHAIN: on a machine whose walk ends at the subject's end, a member may carry an END (\\z) view the scan's pos == n exit evaluates; and on any machine a chain whose head is another state's view target starts one link later instead of being refused");
        emit_pred_row(sb, &p, 2, "view-free", "",
                     0, 0, "", "always (fallback) -- a chain touching a position view is refused, as before [OPT-VEDGE]; changes no answer");
    }
    /* engine — §2.11, the coarsest-grained member; RX_ENGINE's own values.
     * `--engine=` is DO-OR-DIE (never a bit in pcrec_options.flags), so
     * deny/force columns are empty and the CLI spellings carry the axis. */
    {
        PredAxis p = { "engine", NULL, "RX_ENGINE", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "vm", "vm",
                     0, 0, "--engine=vm",
                     "auto: any construct select_engine.c decides is VM-only (captures, possessive quantifiers, \\K, backreferences, calls, ...); forced by --engine=vm (also disables the DFA hybrid prefilter, R21 E-6)");
        emit_pred_row(sb, &p, 2, "dfa", "dfa",
                     0, 0, "--engine=dfa",
                     "auto: always, when no construct forces the VM; --engine=dfa REFUSES a pattern needing VM-only machinery (do-or-die)");
    }
    /* [OPT-4] engine-route — §2.11's ROUTE, not its outcome, and a SEPARATE
     * axis from `engine` above for the reason `prefilter-lang` is separate
     * from `vm-prefilter`: it answers a different question about the same
     * neighbourhood. `engine` says WHICH engine this artifact got;
     * `RX_ENGINE_SEL` says HOW it got there, and the two are independent —
     * `RX_ENGINE "vm"` is reached by EVERY one of the eight routes below.
     *
     * THE VALUE SET IS CLOSED AND THE STAMP IS UNCONDITIONAL (D81), which is
     * the whole point of it: `RX_ENGINE_WHY` already carries the reason as
     * PROSE and a consumer cannot BUCKET on prose — telling "auto picked the
     * VM" from "auto FELL BACK to the VM" meant substring-matching English,
     * which is what the comparative bench was reduced to (its O-8). No flags:
     * the route is an OUTCOME of `--engine=` and of build results, never a
     * thing a bit requests, so the deny/force columns are empty exactly as
     * `engine`'s are. */
    /* [DEC-FALLBACK] B6: the eight routes above are T1's and T2's `axlist` cells (`fit_rungs[]`, src/core/compile.c;
     * `pf_admits[]`, src/opt/select_engine.c) and the attribution walk's two ends (`esel_ends[]`). */
    emit_fb_axis(sb, "engine-route", "RX_ENGINE_SEL");
    emit_fb_table_axis(sb, "fallback", pcrec_fit_table_row);
    emit_fb_table_axis(sb, "prefilter-admit", pcrec_pf_admit_table_row);
}

/* ---- the kit's section ---------------------------------------------------- */

/* The kit enum spellings the `memfn` section prints. Exhaustive switches,
 * no default (coding_guide.md §1.3): a kit enum that grows a value breaks
 * this build rather than printing a stale word. */
static const char *mf_kind_word(mf_opt_kind k)
{
    switch (k) {
    case MF_OPT_DENY: return "deny";
    case MF_OPT_PAIR: return "pair";
    }
    return "?";
}

static const char *mf_budget_word(mf_budget b)
{
    switch (b) {
    case MF_B_SCAN: return "scan";
    case MF_B_LOOP: return "loop";
    case MF_B_ANY:  return "any";
    }
    return "?";
}

static const char *mf_layer_word(mf_layer l)
{
    switch (l) {
    case MF_L_SCALAR: return "scalar";
    case MF_L_SIMD:   return "simd";
    }
    return "?";
}

/* [MEMFN] R4a: the kit's option registry as the `memfn` section
 * (docs/design/memfn/integration.md §R4.4.1; table_contract.md §Sections),
 * one row per mf_options() entry, after the anonymous main table. pcrec
 * names no row: the rows are whatever the kit's options.def holds (none at
 * R4a). Nothing follows the section's header line, so an empty registry is
 * an empty section, never a comment read as its header (table_contract.md
 * rule 3; the --emit-ir precedent). */
static void emit_memfn_section(StrBuf *sb)
{
    size_t n;
    const mf_option *o = mf_options(&n);

    pcrec_sb_puts(sb,
        "#section memfn\n"
        "# pcrec-memory-functions' own option registry (memfn/src/options.def;\n"
        "# docs/spec/registry.md §6). NOT pcrec axes: each row is reached as\n"
        "# --memfn=no-NAME (a `pair` row also as --memfn=NAME), a string pcrec\n"
        "# passes to the kit uninterpreted. budget: D91's scan/loop/any; layer:\n"
        "# the acceptance reading that owns the row (a simd row is inert at\n"
        "# -fno-memfn-simd).\n"
        "#name\tkind\tbudget\tlayer\tspelling\tdoc\n");
    for (size_t i = 0; i < n; i++) {
        StrBuf sp = {0};
        pcrec_sb_printf(&sp, "--memfn=no-%s", o[i].name);
        if (o[i].kind == MF_OPT_PAIR) pcrec_sb_printf(&sp, "|--memfn=%s", o[i].name);
        char *spell = pcrec_sb_take(&sp);
        const char *cells[] = { o[i].name, mf_kind_word(o[i].kind),
                                mf_budget_word(o[i].budget),
                                mf_layer_word(o[i].layer), spell, o[i].doc };
        pcrec_sb_row(sb, cells, sizeof cells / sizeof cells[0]);
        free(spell);
    }
}

/* ---- the whole dump ------------------------------------------------------ */

/* The `--list-axes` TSV, the fourth registry surface (docs/spec/registry.md,
 * [CHK-2] piece 1): the fixed 12-column header, then one row per (axis,
 * candidate) in preference order -- LIST-kind axes walked live off their
 * candidate arrays (emit_dfa_list_axis), axis F's both-kind direction
 * candidates, the table/scan-edge composite rows, and the hand-stated
 * predicate axes (emit_predicate_axes) for which no candidate-list-as-data
 * exists yet. */
char *pcrec_axes_tsv(void)
{
    StrBuf sb = {0};

    pcrec_sb_puts(&sb,
        "# pcrec optimization-axis registry (docs/spec/registry.md, the FOURTH\n"
        "# TSV surface; [CHK-2] piece 1). One row per (axis, candidate), in\n"
        "# PREFERENCE order within the axis (order 1 is tried first).\n"
        "#\n"
        "# kind: \"list\" — a real candidate-list-of-objects exists in\n"
        "#   src/gen/emit_dfa.c and this row's name/deny came straight off it.\n"
        "#   \"both\" — axis F (scan direction): not a preference list, both\n"
        "#   candidates are ALWAYS emitted, once each, per machine.\n"
        "#   \"predicate\" — no candidate-list-as-data exists yet for this axis\n"
        "#   ([ENG-FORM] relayered emit_dfa.c only); name/deny are hand-stated\n"
        "#   from lib/pcrec.h's own enum symbols and docs/spec/tuning.md's\n"
        "#   prose. See this file's (src/dump/axes_dump.c) own header comment\n"
        "#   for the full boundary this dump does and does not prove.\n"
        "#\n"
        "# stamp_macro/stamp_value: the emitted #define this candidate is\n"
        "# reported through and the value it takes when chosen — empty when no\n"
        "# such macro exists (axes C/D/E/F; the activity-count axes, whose\n"
        "# stamp is a NUMBER rather than a named value).\n"
        "# deny_macro/deny_bit, force_macro/force_bit: the PCREC_NO_*/\n"
        "# PCREC_FORCE_* bit (lib/pcrec.h) that removes/forces this candidate,\n"
        "# empty when none exists — axis B's own missing deny flag is a named\n"
        "# finding (docs/design/emitter_form.md §3), not an omission here.\n"
        "# cli_flag: the -f/-fno-/--engine= spelling, empty for a candidate\n"
        "# reached only as a fallback.\n"
        "#axis\torder\tcandidate\tkind\tstamp_macro\tstamp_value\tdeny_macro\t"
        "deny_bit\tforce_macro\tforce_bit\tcli_flag\tapplies\n");

    emit_dfa_list_axis(&sb, "table", "list", pcrec_dfa_axis_table_cands);
    emit_table_composite_rows(&sb);
    emit_cand_axis(&sb, "prefilter");
    emit_dfa_list_axis(&sb, "view", "list", pcrec_dfa_axis_view_cands);
    emit_dfa_list_axis(&sb, "seed", "list", pcrec_dfa_axis_seed_cands);
    emit_dfa_list_axis(&sb, "accept", "list", pcrec_dfa_axis_accept_cands);
    emit_dfa_list_axis(&sb, "direction", "both", pcrec_dfa_axis_direction_cands);
    emit_cand_axis(&sb, "match");     /* [OPT-REVEND] L0: the FINISH rows */
    /* [OPT-5] axes H and I. Both are LIST axes off live candidate arrays,
     * not hand-stated predicate rows: manager ruling R1 makes the region
     * decision a D82 selection and the edge's run-extension body its own
     * representation axis, so both have a real array for this walk to read
     * and a SIMD body added later appears here with no edit. */
    emit_dfa_list_axis(&sb, "scan-edge", "list", pcrec_dfa_axis_edge_cands);
    emit_dfa_list_axis(&sb, "scan-body", "list", pcrec_dfa_axis_scanbody_cands);
    emit_scan_composite_rows(&sb);
    /* [OPT-5 STEP 2] axis J. A LIST axis off the live candidate array, axis
     * G's shape: the two forms of <prefix>_search's post-loop block. It has
     * NO composite rows -- unlike `table` and `scan-body`, whose stamps
     * compose a fact across machines, RX_DFA_START names one artifact-level
     * selection and its value set is exactly these two candidates. */
    emit_cand_axis(&sb, "search-start");

    emit_predicate_axes(&sb);
    emit_memfn_section(&sb);

    return pcrec_sb_take(&sb);
}
