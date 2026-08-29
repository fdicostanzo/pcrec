/* src/parse/axes_dump.c — [CHK-2] PIECE 1: `pcrec --list-axes`, the
 * optimization-axis registry's FOURTH TSV surface (docs/spec/registry.md).
 *
 * WHAT THIS PROVES AND WHAT IT DOES NOT (docs/dev/plan.md [CHK-2]'s own
 * boundary, restated at the one place a reader will actually see it): this
 * dump shares its source with the emitter — it reads the SAME candidate-list
 * arrays `src/gen/emit_dfa.c`'s `dfa_select` walks (via the accessors
 * declared in internal.h), and hand-states the rest from `lib/pcrec.h`'s own
 * enum symbols. It proves what the compiler THINKS its options are. It is
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
 *   "predicate" — the eleven VM/engine-selection axes (`docs/spec/
 *                  tuning.md` §2.1-2.9, its coarse §2.11 engine axis) have
 *                  no candidate-list-as-data anywhere in the tree yet
 *                  (`[ENG-FORM]` relayered emit_dfa.c only — src/gen/
 *                  CLAUDE.md's own "SCOPE: emit_dfa.c first" note). Each is
 *                  represented here as the two-candidate shape the deny bit
 *                  already implies (the mechanism, and the denied
 *                  fallback), sourced from `lib/pcrec.h`'s own enum symbols
 *                  (never a hand-typed bit NUMBER) so a bit's numeric
 *                  position can move with no edit here; the CANDIDATE NAMES
 *                  and the one-line APPLIES text are hand-authored from
 *                  docs/spec/tuning.md §2's own prose, which is exactly the
 *                  "do NOT restructure the VM emitter to manufacture lists;
 *                  state the source" allowance the plan row gives this
 *                  piece.
 *
 * Wire format: docs/spec/table_contract.md (TSV, `#` comments, last `#`
 * line before data is the header, columns append-only). */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "pcrec.h"

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

    { "prefilter", "offset-set-bounded", "forward scan, an offset-k candidate SET was selected, under a $/\\Z/\\z view or a word-context accept ([OPT-K])" },
    { "prefilter", "offset-set", "forward scan, an offset-k candidate SET was selected: one memchr at the chosen offset k*, the other offsets verified per candidate ([OPT-K])" },
    { "prefilter", "memchr-bounded", "forward scan, one candidate byte, under a $/\\Z/\\z view or a word-context accept" },
    { "prefilter", "memchr", "forward scan, one candidate byte" },
    { "prefilter", "byte-class-bounded", "forward scan, several candidate bytes, under a $/\\Z/\\z view or a word-context accept" },
    { "prefilter", "byte-class", "forward scan, several candidate bytes" },
    { "prefilter", "none", "always (fallback) — also the reverse machine, and every case where the start state itself accepts (no skip is sound there)" },

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

    { "match", "unwrapped", "the artifact's own ENG_UNANCH _match, and its anchored machine built inside the DFA caps ([ENG-ABS])" },
    { "match", "search-filter", "always (fallback) — ENG_ATTEMPT, the empty engine, an anchored machine over a cap, or the deny flag" },
};
#define N_AXIS_DESC (sizeof AXIS_DESC / sizeof AXIS_DESC[0])

static const char *desc_of(const char *axis, const char *cand)
{
    for (size_t i = 0; i < N_AXIS_DESC; i++)
        if (!strcmp(AXIS_DESC[i].axis, axis) && !strcmp(AXIS_DESC[i].candidate, cand))
            return AXIS_DESC[i].applies;
    return "(no description authored for this candidate yet — read its "
           "`applies` function in src/gen/emit_dfa.c)";
}

/* Per-axis scalar stamp macro, where one exists — axes B and C-E's own
 * candidate objects have no `#define` of their own (docs/spec/tuning.md's
 * per-artifact stamp table only names RX_DFA_TABLE and RX_DFA_PREFILTER;
 * view/seed/accept/direction are emitter-internal decisions with no
 * observable trace in the artifact). Where a stamp exists, D82's own rule
 * ("the chosen object's name IS the stamp value") makes `stamp_value`
 * exactly the candidate's own name — never re-derived. */
static const char *stamp_macro_of(const char *axis)
{
    if (!strcmp(axis, "table")) return "RX_DFA_TABLE";
    if (!strcmp(axis, "prefilter")) return "RX_DFA_PREFILTER";
    /* [ENG-ABS] axis G HAS a per-artifact stamp, unlike view/seed/accept/
     * direction — its value is a caller-visible cost property of
     * `<prefix>_match` (spec §3.2), not an emitter-internal decision. */
    if (!strcmp(axis, "match")) return "RX_DFA_MATCH";
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
 * which is a caller-observable change no row has asked for. */
static const char *cli_flag_of(const char *axis, const char *cand)
{
    if (!strcmp(axis, "table") && !strcmp(cand, "premultiplied"))
        return "-fno-premul-table";
    if (!strcmp(axis, "match") && !strcmp(cand, "unwrapped"))
        return "-fno-anchored-dfa";
    if (!strcmp(axis, "prefilter") &&
        (!strcmp(cand, "offset-set") || !strcmp(cand, "offset-set-bounded")))
        return "-fno-offset-skip";
    return "";
}

/* ---- deny-bit VALUE -> MACRO NAME, for the "list" axes' own deny field --
 *
 * The `PcrecAxisCand.deny` value comes straight off the live `DfaCand.deny`
 * field the emitter itself consults (never hand-typed), so this table only
 * has to translate a KNOWN value into its symbol's name for display —
 * an unrecognised nonzero value (a bit this table has not caught up with
 * yet, e.g. a newly landed axis) prints as a bare hex number rather than
 * silently vanishing or crashing, which is the merge-safety property the
 * brief asks for. */
static const struct { unsigned v; const char *n; } DENY_NAMES[] = {
    { PCREC_NO_POSSESSIFY, "PCREC_NO_POSSESSIFY" },
    { PCREC_NO_REVDET, "PCREC_NO_REVDET" },
    { PCREC_NO_COUNTER, "PCREC_NO_COUNTER" },
    { PCREC_NO_LENGTH_PRUNE, "PCREC_NO_LENGTH_PRUNE" },
    { PCREC_NO_PREFILTER, "PCREC_NO_PREFILTER" },
    { PCREC_FORCE_PREFILTER, "PCREC_FORCE_PREFILTER" },
    { PCREC_NO_ALTCLS_MERGE, "PCREC_NO_ALTCLS_MERGE" },
    { PCREC_NO_ALTCLS_FACTOR, "PCREC_NO_ALTCLS_FACTOR" },
    { PCREC_NO_ATOMIC_DISCHARGE, "PCREC_NO_ATOMIC_DISCHARGE" },
    { PCREC_NO_SPLICE_CALLS, "PCREC_NO_SPLICE_CALLS" },
    { PCREC_NO_TIERED_ENTRY, "PCREC_NO_TIERED_ENTRY" },
    { PCREC_NO_PREMUL_TABLE, "PCREC_NO_PREMUL_TABLE" },
    { PCREC_NO_OFFSET_SKIP, "PCREC_NO_OFFSET_SKIP" },
    { PCREC_NO_ANCHORED_DFA, "PCREC_NO_ANCHORED_DFA" },
};
#define N_DENY_NAMES (sizeof DENY_NAMES / sizeof DENY_NAMES[0])

static unsigned bit_of(unsigned flag)
{
    unsigned b = 0;
    while (flag > 1u) { flag >>= 1; b++; }
    return b;
}

static void deny_cols(unsigned v, char *macro, size_t macrocap, char *bit, size_t bitcap)
{
    macro[0] = 0; bit[0] = 0;
    if (!v) return;
    for (size_t i = 0; i < N_DENY_NAMES; i++) {
        if (DENY_NAMES[i].v == v) {
            snprintf(macro, macrocap, "%s", DENY_NAMES[i].n);
            snprintf(bit, bitcap, "%u", bit_of(v));
            return;
        }
    }
    /* unrecognised bit — report the hex value rather than dropping the row */
    snprintf(macro, macrocap, "0x%x", v);
    snprintf(bit, bitcap, "%u", bit_of(v));
}

/* ---- one TSV row -------------------------------------------------------- */

static void axis_row(StrBuf *sb, const char *axis, int order,
                     const char *candidate, const char *kind,
                     const char *stamp_macro, const char *stamp_value,
                     const char *deny_macro, const char *deny_bit,
                     const char *force_macro, const char *force_bit,
                     const char *cli_flag, const char *applies)
{
    sb_printf(sb, "%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n",
              axis, order, candidate, kind,
              stamp_macro, stamp_value, deny_macro, deny_bit,
              force_macro, force_bit, cli_flag, applies);
}

/* ---- "list"/"both" axes: walked off the LIVE candidate arrays ---------- */

static void emit_dfa_list_axis(StrBuf *sb, const char *axis, const char *kind,
                               size_t (*get)(PcrecAxisCand *, size_t))
{
    PcrecAxisCand cands[16];
    size_t n = get(cands, 16);
    const char *stamp_macro = stamp_macro_of(axis);
    for (size_t i = 0; i < n; i++) {
        char deny_macro[64], deny_bit[8];
        deny_cols(cands[i].deny, deny_macro, sizeof deny_macro, deny_bit, sizeof deny_bit);
        const char *stamp_value = stamp_macro[0] ? cands[i].name : "";
        axis_row(sb, axis, (int)(i + 1), cands[i].name, kind,
                 stamp_macro, stamp_value,
                 deny_macro, deny_bit, "", "",
                 cli_flag_of(axis, cands[i].name),
                 desc_of(axis, cands[i].name));
    }
}

/* ---- "predicate" axes: no candidate-list-as-data yet -------------------
 *
 * Sourced from lib/pcrec.h's own enum symbols (the `V()` macro below
 * stringifies the identifier it is handed, so the printed macro name and
 * the value used to compute the bit number cannot drift apart — a rename
 * in lib/pcrec.h breaks this file at compile time rather than silently
 * printing a stale name) and from docs/spec/tuning.md §2's own prose for
 * the candidate names and one-line descriptions. */
#define V(x) (x), #x

typedef struct {
    const char *axis;
    const char *candidate;
    const char *stamp_macro;
    const char *stamp_value;   /* "" when the stamp is a count/bitmask,
                                 * never a single value this candidate owns */
    unsigned    deny_val;   const char *deny_macro;
    unsigned    force_val;  const char *force_macro;
    const char *cli_flag;
    const char *applies;
} PredAxis;

static void emit_pred_row(StrBuf *sb, const PredAxis *p, int order,
                          const char *candidate, const char *stamp_value,
                          unsigned deny_val, const char *deny_macro,
                          unsigned force_val, const char *force_macro,
                          const char *cli_flag, const char *applies)
{
    char db[8] = "", fb[8] = "";
    if (deny_val) snprintf(db, sizeof db, "%u", bit_of(deny_val));
    if (force_val) snprintf(fb, sizeof fb, "%u", bit_of(force_val));
    axis_row(sb, p->axis, order, candidate, "predicate",
             p->stamp_macro, stamp_value,
             deny_val ? deny_macro : "", db,
             force_val ? force_macro : "", fb,
             cli_flag, applies);
}

static void emit_predicate_axes(StrBuf *sb)
{
    /* possessify — tuning.md §2.1, RX_VM_STRATS's own named pair */
    {
        PredAxis p = { "possessify", NULL, "RX_VM_STRATS", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "possessive", "PCREC_VM_STRAT_POSSESSIVE",
                     V(PCREC_NO_POSSESSIFY), 0, "", "-fno-possessify",
                     "per A_REP: possessify.c proves the loop's body can never profitably re-enter");
        emit_pred_row(sb, &p, 2, "backtracking", "PCREC_VM_STRAT_BACKTRACKING",
                     0, "", 0, "", "", "always (fallback)");
    }
    /* revdet — §2.2, RX_VM_RUNGS bit PCREC_VM_RUNG_REVDET */
    {
        PredAxis p = { "revdet", NULL, "RX_VM_RUNGS", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "revdet", "PCREC_VM_RUNG_REVDET",
                     V(PCREC_NO_REVDET), 0, "", "-fno-revdet",
                     "per A_REP: forward unique-iteration lets the body run backward with no choice points");
        emit_pred_row(sb, &p, 2, "denied", "",
                     0, "", 0, "", "", "always (fallback) — the ladder's next rung (counter, or literal frames)");
    }
    /* counter — §2.3, RX_VM_RUNGS bit PCREC_VM_RUNG_COUNTER */
    {
        PredAxis p = { "counter", NULL, "RX_VM_RUNGS", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "counter", "PCREC_VM_RUNG_COUNTER",
                     V(PCREC_NO_COUNTER), 0, "", "-fno-counter",
                     "per A_REP: a bounded repeat, unrolled by --unroll=K (default PCREC_DEFAULT_UNROLL_K), below the replication cap");
        emit_pred_row(sb, &p, 2, "denied", "",
                     0, "", 0, "", "", "always (fallback) — literal replication (frames)");
    }
    /* length-prune — §2.4, RX_VM_PRUNES's own named pair */
    {
        PredAxis p = { "length-prune", NULL, "RX_VM_PRUNES", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "clamped", "PCREC_VM_PRUNE_CLAMPED",
                     V(PCREC_NO_LENGTH_PRUNE), 0, "", "-fno-length-prune",
                     "per A_REP: a minimum-remaining-length bound is derivable for this quantifier's rung");
        emit_pred_row(sb, &p, 2, "unclamped", "PCREC_VM_PRUNE_UNCLAMPED",
                     0, "", 0, "", "", "always (fallback) — no bound derivable, or the axis denied");
    }
    /* vm-prefilter — §2.5, the ONE force pair; RX_VM_PREFILTER's own values.
     * NOT the same axis as "prefilter" above (docs/spec/tuning.md §3.1: "the
     * two prefilter macros are two different selections") — this one is
     * whether the VM runs a capture-erased DFA ahead of its program at all. */
    {
        PredAxis p = { "vm-prefilter", NULL, "RX_VM_PREFILTER", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "hybrid", "hybrid",
                     V(PCREC_NO_PREFILTER), V(PCREC_FORCE_PREFILTER), "-fno-prefilter / -fprefilter",
                     "auto+captures selects it jointly with the engine (select_engine.c); -fprefilter REFUSES on a pure-DFA-selected pattern (do-or-die)");
        emit_pred_row(sb, &p, 2, "none", "none",
                     0, "", 0, "", "", "always (fallback) — also the --engine=vm side effect (R21 E-6)");
    }
    /* altcls-merge — §2.6, RX_ALTCLS_MERGES is an ACTIVITY COUNT, not a
     * named value — stamp_value left empty on both rows for that reason. */
    {
        PredAxis p = { "altcls-merge", NULL, "RX_ALTCLS_MERGES", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "merged", "",
                     V(PCREC_NO_ALTCLS_MERGE), 0, "", "-fno-altcls-merge",
                     "a maximal run of single-character alternation branches qualifies (runs before either engine is built)");
        emit_pred_row(sb, &p, 2, "denied", "",
                     0, "", 0, "", "", "always (fallback)");
    }
    /* altcls-factor — §2.7 */
    {
        PredAxis p = { "altcls-factor", NULL, "RX_ALTCLS_FACTORED", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "factored", "",
                     V(PCREC_NO_ALTCLS_FACTOR), 0, "", "-fno-altcls-factor",
                     "a maximal run sharing a literal first byte qualifies, on stage 1's own output");
        emit_pred_row(sb, &p, 2, "denied", "",
                     0, "", 0, "", "", "always (fallback)");
    }
    /* atomic-discharge — §2.8, ENGINE-SELECTING; no dedicated stamp of its
     * own (its activity is folded into RX_VM_STRATS via vm_cuts(); RX_ENGINE
     * is the observable consequence when it changes which engine a pattern
     * gets). */
    {
        PredAxis p = { "atomic-discharge", NULL, "", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "discharged", "",
                     V(PCREC_NO_ATOMIC_DISCHARGE), 0, "", "-fno-atomic-discharge",
                     "possessify's own verdict proves the A_ATOMIC node's cut is a no-op (docs/design/atomic_groups_design.md §5.3)");
        emit_pred_row(sb, &p, 2, "denied", "",
                     0, "", 0, "", "", "always (fallback) — ENGINE-SELECTING: the A_ATOMIC node stays, which is DFA-excluding, so RX_ENGINE can move to \"vm\"");
    }
    /* splice-calls — §2.9, ENGINE-SELECTING; RX_VM_CALL_SPLICED/_LINKED are
     * two separate counts, one per candidate. */
    {
        PredAxis p1 = { "splice-calls", NULL, "RX_VM_CALL_SPLICED", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p1, 1, "spliced", "",
                     V(PCREC_NO_SPLICE_CALLS), 0, "", "-fno-splice-calls",
                     "the callee is not in a call-graph cycle and its expansion fits the splice size budget (PCREC_MAX_SPLICE_NODES/_TOTAL)");
        PredAxis p2 = { "splice-calls", NULL, "RX_VM_CALL_LINKED", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p2, 2, "linked", "",
                     0, "", 0, "", "", "always (fallback) — ENGINE-SELECTING: a linked call is structurally VM-only");
    }
    /* tiered-entry — §2.12, RX_FAST_FRAMES/_TRAIL (numeric; FAST==RESUME/
     * TRAIL is how a denied artifact is told apart). */
    {
        PredAxis p = { "tiered-entry", NULL, "RX_FAST_FRAMES", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "tiered", "",
                     V(PCREC_NO_TIERED_ENTRY), 0, "", "-fno-tiered-entry",
                     "the stamped default resume/trail storage does not fit one 4KB page (docs/spec/match_api.md §10.9)");
        emit_pred_row(sb, &p, 2, "single-tier", "",
                     0, "", 0, "", "", "always (fallback) — FAST_FRAMES==RESUME_FRAMES, FAST_TRAIL==TRAIL_FRAMES");
    }
    /* engine — §2.11, the coarsest-grained member; RX_ENGINE's own values.
     * `--engine=` is DO-OR-DIE (never a bit in pcrec_options.flags), so
     * deny/force columns are empty and the CLI spellings carry the axis. */
    {
        PredAxis p = { "engine", NULL, "RX_ENGINE", "", 0, NULL, 0, NULL, NULL, NULL };
        emit_pred_row(sb, &p, 1, "vm", "vm",
                     0, "", 0, "", "--engine=vm",
                     "auto: any construct select_engine.c decides is VM-only (captures, possessive quantifiers, \\K, backreferences, calls, ...); forced by --engine=vm (also disables the DFA hybrid prefilter, R21 E-6)");
        emit_pred_row(sb, &p, 2, "dfa", "dfa",
                     0, "", 0, "", "--engine=dfa",
                     "auto: always, when no construct forces the VM; --engine=dfa REFUSES a pattern needing VM-only machinery (do-or-die)");
    }
}
#undef V

/* ---- the whole dump ------------------------------------------------------ */

char *pcrec_axes_tsv(void)
{
    StrBuf sb = {0};

    sb_puts(&sb,
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
        "#   prose. See this file's (src/parse/axes_dump.c) own header comment\n"
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
    emit_dfa_list_axis(&sb, "prefilter", "list", pcrec_dfa_axis_prefilter_cands);
    emit_dfa_list_axis(&sb, "view", "list", pcrec_dfa_axis_view_cands);
    emit_dfa_list_axis(&sb, "seed", "list", pcrec_dfa_axis_seed_cands);
    emit_dfa_list_axis(&sb, "accept", "list", pcrec_dfa_axis_accept_cands);
    emit_dfa_list_axis(&sb, "direction", "both", pcrec_dfa_axis_direction_cands);
    emit_dfa_list_axis(&sb, "match", "list", pcrec_dfa_axis_match_cands);

    emit_predicate_axes(&sb);

    return sb_take(&sb);
}
