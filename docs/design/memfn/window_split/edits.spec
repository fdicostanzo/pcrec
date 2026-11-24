# window_split.md rev 2 §5: every edit the unit makes beyond the cut, read by assemble.py.
# First the renames (R6: code tokens only, comments and strings untouched), then FROM/TO
# blocks (R7: each FROM exactly once in its file, after the renames). A block's header line
# names its file and the design item it carries. Nothing here changes a statement's effect or
# order: an accessor holds the moved lines (A2, A3, A5's walks), a one-line read (A1/O3, A4,
# A5's columns, the ren pieces), or a check's return propagation (A5, O1).

# ---- H3 (U2): the set family's names (kit_pos.c, kit.h)
rename in_set kit_pos_in in family
rename count kit_pos_count in family
rename shape kit_pos_shape in family
rename two kit_pos_two in family
rename full kit_pos_full in family

@@ kit_pos.c  H3: the family loses `static` (kit.h names), kit_pos_first born
<<<
static int kit_pos_in(const uint8_t s[32], unsigned b) { return s[b >> 3] >> (b & 7) & 1; }

static unsigned kit_pos_count(const uint8_t s[32])
===
int kit_pos_in(const uint8_t s[32], unsigned b) { return s[b >> 3] >> (b & 7) & 1; }

unsigned kit_pos_count(const uint8_t s[32])
>>>
@@ kit_pos.c  H3
<<<
static int kit_pos_shape(const uint8_t s[32], int *a, int *b)
===
int kit_pos_shape(const uint8_t s[32], int *a, int *b)
>>>
@@ kit_pos.c  H3
<<<
static void kit_pos_two(const uint8_t s[32], int m[2])
===
void kit_pos_two(const uint8_t s[32], int m[2])
>>>
@@ kit_pos.c  H3: kit_pos_first, the one "first member" spelling (U2b's sites)
<<<
static int kit_pos_full(const uint8_t s[32])
{
    for (unsigned i = 0; i < 32; i++) if (s[i] != 0xFF) return 0;
    return 1;
}
===
int kit_pos_full(const uint8_t s[32])
{
    for (unsigned i = 0; i < 32; i++) if (s[i] != 0xFF) return 0;
    return 1;
}

/* The least member of the position, or -1 for the empty one (kit.h). */
int kit_pos_first(const uint8_t s[32])
{
    for (unsigned b = 0; b < 256; b++)
        if (kit_pos_in(s, b)) return (int)b;
    return -1;
}
>>>
@@ kit.h  H3: the set family's new kit.h names, beside its head kit_pos_class_of
<<<
kit_pos_class kit_pos_class_of(const uint8_t set[32]);
int kit_pos_spelled(const uint8_t set[32]);
===
kit_pos_class kit_pos_class_of(const uint8_t set[32]);
int kit_pos_spelled(const uint8_t set[32]);
/* THE SET FAMILY (kit_pos.c; ARV-5, H3): a position's membership, member
 * count, least member (-1: empty), shape (1: one member *a; 2: a two-member
 * cube *a < *b; 0: neither), two members ascending, and fullness. Kit-wide
 * by H3 whatever its callers today (window_split.md §10's exception). */
#define kit_pos_in    MF_NS(kit_pos_in)
#define kit_pos_count MF_NS(kit_pos_count)
#define kit_pos_first MF_NS(kit_pos_first)
#define kit_pos_shape MF_NS(kit_pos_shape)
#define kit_pos_two   MF_NS(kit_pos_two)
#define kit_pos_full  MF_NS(kit_pos_full)
int kit_pos_in(const uint8_t s[32], unsigned b);
unsigned kit_pos_count(const uint8_t s[32]);
int kit_pos_first(const uint8_t s[32]);
int kit_pos_shape(const uint8_t s[32], int *a, int *b);
void kit_pos_two(const uint8_t s[32], int m[2]);
int kit_pos_full(const uint8_t s[32]);
>>>

# ---- H2/O3 (U3): the TIE table's searchers; kit_tie_member_key to its one caller
@@ kit_pick.c  O3: kit_tie_takes static (its one caller is kit_pick_takes); the two predicates
<<<
int kit_tie_takes(int r, int32_t c, int32_t b)
{
    wf_tie_to to = wf_ties[r].to;
    return to == TIE_HIGHER ? c > b : to == TIE_LOWER || to == TIE_LEFTMOST ? c < b : 0;
}
===
static int kit_tie_takes(int r, int32_t c, int32_t b)
{
    wf_tie_to to = wf_ties[r].to;
    return to == TIE_HIGHER ? c > b : to == TIE_LOWER || to == TIE_LEFTMOST ? c < b : 0;
}

/* 1 iff row `r` breaks its tie by an EXCHANGE sort (C-model's verify-NO
 * order), 1 iff it RE-SEEDS on an equal margin (MARGIN): the two TIE reads
 * that are no pick (kit.h). */
int kit_tie_exchanges(int r) { return wf_ties[r].to == TIE_EXCHANGE; }
int kit_tie_reseeds(int r)   { return wf_ties[r].to == TIE_RESEED; }
>>>
@@ kit.h  O3: the predicates replace kit_tie_takes and the "NOT through it" exception
<<<
 * T_PRES_MEMBER's: kit_tie_member_key (member order above the byte). Every
 * pick asks it through kit_pick_takes below. NOT through it: window.c reads
 * `wf_ties[T_CMODEL/T_MARGIN].to` directly (an exchange sort and a
 * rejection, not a pick); P2 and P4 compare with no TIE row. */
enum { T_MASS_STRETCH, T_MASS_SET, T_MODEL, T_CMODEL, T_MARGIN, T_WINDOW, T_PRES_MEMBER,
       T_RUN_LEFT, T_N };
#define kit_tie_takes      MF_NS(kit_tie_takes)
#define kit_tie_member_key MF_NS(kit_tie_member_key)
int kit_tie_takes(int r, int32_t c, int32_t b);
int32_t kit_tie_member_key(unsigned member_order, int byte);
===
 * T_PRES_MEMBER's (presence.c's member key: member order above the byte).
 * Every pick asks it through kit_pick_takes below; the two reads that are no
 * pick (C-model's exchange sort, MARGIN's rejection) through the two
 * predicates (kit_pick.c, O3); P2 and P4 compare with no TIE row. */
enum { T_MASS_STRETCH, T_MASS_SET, T_MODEL, T_CMODEL, T_MARGIN, T_WINDOW, T_PRES_MEMBER,
       T_RUN_LEFT, T_N };
#define kit_tie_exchanges MF_NS(kit_tie_exchanges)
#define kit_tie_reseeds   MF_NS(kit_tie_reseeds)
int kit_tie_exchanges(int r);
int kit_tie_reseeds(int r);
>>>
@@ window_stop.c  O3 (A1): C-model's exchange sort asks the predicate
<<<
        if (wf_ties[T_CMODEL].to == TIE_EXCHANGE)
===
        if (kit_tie_exchanges(T_CMODEL))
>>>
@@ window_margin.c  O3 (A1) and A2: MARGIN's reads
<<<
    if (!d->a[pk].priced || !d->a[rs].priced || wf_arows[d->a[rs].arow].ct != &ct_a_model)
        return 0;
    unsigned long long l = d->a[rs].cost * COST(MATERIAL_NUM);
    unsigned long long r = d->a[pk].cost * COST(MATERIAL_DEN);
    return l < r || (l == r && wf_ties[T_MARGIN].to == TIE_RESEED);
===
    if (!d->a[pk].priced || !d->a[rs].priced || !wf_a_is_model(d->a[rs].arow))
        return 0;
    unsigned long long l = d->a[rs].cost * COST(MATERIAL_NUM);
    unsigned long long r = d->a[pk].cost * COST(MATERIAL_DEN);
    return l < r || (l == r && kit_tie_reseeds(T_MARGIN));
>>>
@@ presence.c  H2: kit_tie_member_key moves to its one caller, static (window.c :132-139 verbatim)
<<<
/* A member span's key under the TIE table's presence-member row. */
===
/* The presence-member row's key of a one-byte member span: its pattern order
 * above its byte, an UNKNOWN order as 0, below every known one (a stated
 * order is 1..256, kit_presence_check). */
static int32_t kit_tie_member_key(unsigned member_order, int byte)
{
    unsigned o = member_order == MF_ORDER_UNKNOWN ? 0 : member_order;
    return (int32_t)(o << 8 | (unsigned)byte);
}

/* A member span's key under the TIE table's presence-member row. */
>>>

# ---- A2 (U5): Table A's searchers, window_stop.c
@@ window_stop.c  A2
<<<
static const kit_table wf_atable = { "wfA", WF_NAROWS, a_ct, NULL, NULL, a_holds, NULL };
===
static const kit_table wf_atable = { "wfA", WF_NAROWS, a_ct, NULL, NULL, a_holds, NULL };

/* Table A's walk for alternative `ai` of `d` (decide's per-alternative step,
 * traced unless `quiet`): the row taken, then its choose. */
void wf_a_choose(const mf_art *art, const mf_site *s, int quiet, wf_dec *d, unsigned ai)
{
    wf_facts f = { s, &s->alts[ai] };
    gate_in in = { .s = s, .wf = &f };
    gate_tctx tc = { art, "wfA", art->nsites + 1, MF_PH_DEFINE, &in, 0, quiet, 0, NULL };
    gate_verdict why = { 0, 0 };
    wf_x x = { d, ai };
    size_t r = kit_walk(&wf_atable, 0, &in, MF_PH_DEFINE, 0, &x, &tc, &why);
    /* the floor row serves every class: the walk always chooses */
    d->a[ai].arow = r < WF_NAROWS ? r : WF_NAROWS - 1;
    wf_arows[d->a[ai].arow].choose(&x);
}

/* Table A row `arow`'s path id (the reply's `path`). */
const char *wf_a_path(size_t arow) { return wf_arows[arow].path; }

/* 1 iff Table A row `arow` is A-model (C-model's and MARGIN's reading). */
int wf_a_is_model(size_t arow) { return wf_arows[arow].ct == &ct_a_model; }
>>>
@@ window_verify.c  A2
<<<
    return chosen(d)->has_stop && wf_arows[chosen(d)->arow].ct == &ct_a_model;
===
    return chosen(d)->has_stop && wf_a_is_model(chosen(d)->arow);
>>>

# ---- A3 (U5): Table M's searcher, window_margin.c (decide keeps f, in, tc: trace_cands reads tc)
@@ window_margin.c  A3
<<<
static const kit_table wf_mtable = { "wfM", WF_NMROWS, m_ct, NULL, NULL, m_holds, NULL };
===
static const kit_table wf_mtable = { "wfM", WF_NMROWS, m_ct, NULL, NULL, m_holds, NULL };

/* Table M's walk over decision `d` under decide's `in` and `tc`: the
 * chosen alternative `d->ch` (MARGIN: the re-seeding one; M-parked: the
 * parked one; else 0). */
void wf_m_choose(wf_dec *d, const gate_in *in, const gate_tctx *tc)
{
    gate_verdict why = { 0, 0 };
    wf_x x = { d, 0 };
    size_t mr = kit_walk(&wf_mtable, 0, in, MF_PH_DEFINE, 0, &x, tc, &why);
    if (mr == M_MARGIN) {
        unsigned pk, rs;
        m_pair(d, &pk, &rs);
        d->ch = (int)rs;
    } else if (mr == M_PARKED) {
        unsigned pk, rs;
        m_pair(d, &pk, &rs);
        d->ch = (int)pk;
    } else {
        d->ch = 0;
    }
}
>>>
@@ window_decide.c  A2, A3: decide walks A, M and C through their searchers
<<<
        cands(&s->alts[ai], d->rate, &d->a[ai], pos[ai]);
        wf_facts f = { s, &s->alts[ai] };
        gate_in in = { .s = s, .wf = &f };
        gate_tctx tc = { art, "wfA", art->nsites + 1, MF_PH_DEFINE, &in, 0, quiet, 0, NULL };
        gate_verdict why = { 0, 0 };
        wf_x x = { d, ai };
        size_t r = kit_walk(&wf_atable, 0, &in, MF_PH_DEFINE, 0, &x, &tc, &why);
        /* the floor row serves every class: the walk always chooses */
        d->a[ai].arow = r < WF_NAROWS ? r : WF_NAROWS - 1;
        wf_arows[d->a[ai].arow].choose(&x);
    }
    wf_facts f = { s, NULL };
    gate_in in = { .s = s, .wf = &f };
    gate_tctx tc = { art, "wfM", art->nsites + 1, MF_PH_DEFINE, &in, 0, quiet, 0, NULL };
    gate_verdict why = { 0, 0 };
    wf_x x = { d, 0 };
    size_t mr = kit_walk(&wf_mtable, 0, &in, MF_PH_DEFINE, 0, &x, &tc, &why);
    if (mr == M_MARGIN) {
        unsigned pk, rs;
        m_pair(d, &pk, &rs);
        d->ch = (int)rs;
    } else if (mr == M_PARKED) {
        unsigned pk, rs;
        m_pair(d, &pk, &rs);
        d->ch = (int)pk;
    } else {
        d->ch = 0;
    }
    c_plan(d);
    snprintf(d->path, sizeof d->path, "%s%s", wf_arows[d->a[d->ch].arow].path,
             d->pinned ? "+pin" : "");
===
        cands(&s->alts[ai], d->rate, &d->a[ai], pos[ai]);
        wf_a_choose(art, s, quiet, d, ai);
    }
    wf_facts f = { s, NULL };
    gate_in in = { .s = s, .wf = &f };
    gate_tctx tc = { art, "wfM", art->nsites + 1, MF_PH_DEFINE, &in, 0, quiet, 0, NULL };
    wf_m_choose(d, &in, &tc);
    c_plan(d);
    snprintf(d->path, sizeof d->path, "%s%s", wf_a_path(d->a[d->ch].arow),
             d->pinned ? "+pin" : "");
>>>

# ---- A4 (U5): the legacy frames' declared stream, window_ren.c
@@ window_ren.c  A4 (beside ren_find: a noted deviation, W11)
<<<
fd_form wf_arm_pick(const arm *a)
{
    for (size_t i = 0; i < RB_N; i++)
        if (ren_search[i].k.frame == E_STMT && ren_search[i].arm == a)
            return (fd_form)__builtin_ctz(ren_search[i].k.keys);
    return FF_UNSTATED;
}
===
fd_form wf_arm_pick(const arm *a)
{
    for (size_t i = 0; i < RB_N; i++)
        if (ren_search[i].k.frame == E_STMT && ren_search[i].arm == a)
            return (fd_form)__builtin_ctz(ren_search[i].k.keys);
    return FF_UNSTATED;
}

/* The declared stream of a legacy frame's renderer, by index (NOT through
 * ren_find: the framed ask reads one named row per frame, W11): E-func's
 * offset-skip function is B-fn's fused row, E-stmt's PF arm the caller's
 * stream row. */
unsigned wf_legacy_stream(wf_frame_row f)
{
    return f == E_FUNC ? ren_fused[RF_FN].stream : ren_stream[RS_CALLER].k.keys;
}
>>>
@@ window_ask.c  A4 (wf_frame_of)
<<<
        fp->stream = wstream_of(ren_fused[RF_FN].stream);
===
        fp->stream = wstream_of(wf_legacy_stream(E_FUNC));
>>>
@@ window_ask.c  A4 (wf_frame_of)
<<<
        fp->stream = wstream_of(ren_stream[RS_CALLER].k.keys);
===
        fp->stream = wstream_of(wf_legacy_stream(E_STMT));
>>>
@@ window_ask.c  A4 (wf_agree, MF_TRACE)
<<<
        held.stream = wstream_of(ren_fused[RF_FN].stream);
===
        held.stream = wstream_of(wf_legacy_stream(E_FUNC));
>>>
@@ window_ask.c  A4 (wf_agree, MF_TRACE)
<<<
        held.stream = wstream_of(ren_stream[RS_CALLER].k.keys);
===
        held.stream = wstream_of(wf_legacy_stream(E_STMT));
>>>

# ---- O1 (U5): frame / ren; the composing frame's pieces and the per-table checks
@@ window_ren.c  O1: the pieces wf_plan_site's piece selection read (moved lines)
<<<
/* E-FIND's SETUP: T-FIND (fd_find, the one walk, with the stop's facts and
===
/* THE COMPOSING FRAME's PIECES (§2.5.4) for frame `f` into `w`: its
 * skeleton row; where Table S answers ST-one for `search` (fused row `fu`
 * none), its stream and check rows. Table S's refusal text, or NULL. */
const char *wf_ren_pieces(struct wf_plan *w, wf_frame_row f, const ren_fused_row *fu,
                          fd_form search)
{
    uint8_t st;
    size_t sr = table_s(search, f, fu, &st);
    w->skel = ren_find(REN_ROWS(ren_skel), f, REN_FRAME, NULL);
    if (sr == ST_ONE && !fu) {
        w->strm = ren_find(REN_ROWS(ren_stream), f, st, NULL);
        w->chk = ren_find(REN_ROWS(ren_check), f, REN_FRAME, NULL);
    }
    return wf_srows[sr].why;
}

/* THE RENDERER TABLES' SELF-CHECK (wf_tables_check's part, items 2 and 3):
 * the first refusal, or NULL. */
const char *wf_ren_check(void)
{
    for (size_t i = 0; i < RB_N; i++) {
        const ren_search_row *r = &ren_search[i];
        if (r->k.frame != E_FIND) continue;
        if (r->k.holds) return "an E-find search renderer row takes a predicate";
        if (!r->head || !r->skip) return "an E-find search renderer row has no head or skip";
    }
    for (size_t i = 0; i < RF_N; i++)
        if (ren_fused[i].k.keys != REN_PICK(ren_fused[i].search))
            return "a fused row's key is not its declared search's pick";
    return NULL;
}

/* E-FIND's SETUP: T-FIND (fd_find, the one walk, with the stop's facts and
>>>
@@ window_frame.c  O1 + A5: the self-check asks each table's own check, in today's order
<<<
const char *wf_tables_check(void)
{
    for (size_t i = 0; i < WF_NEROWS; i++)
        if (!wf_erows[i].holds || !wf_erows[i].ct) return "a Table E row is a hole";
    for (size_t i = 0; i < WF_NSROWS; i++)
        if (!wf_spanrows[i].holds || !wf_spanrows[i].h || !wf_spanrows[i].render ||
            !wf_spanrows[i].ct)
            return "a span form row is a hole";
    for (size_t i = 0; i < WF_NSROWS; i++)
        if ((wf_spanrows[i].render == wf_span_v) != (wf_spanrows[i].define != NULL))
            return "a span form row's define and the V renderer do not pair";
    if (!wf_spanrows[WF_NSROWS - 1].holds(NULL))
        return "the last span form row does not hold always";
    for (size_t i = 0; i < RB_N; i++) {
        const ren_search_row *r = &ren_search[i];
        if (r->k.frame != E_FIND) continue;
        if (r->k.holds) return "an E-find search renderer row takes a predicate";
        if (!r->head || !r->skip) return "an E-find search renderer row has no head or skip";
    }
    for (size_t i = 0; i < RF_N; i++)
        if (ren_fused[i].k.keys != REN_PICK(ren_fused[i].search))
            return "a fused row's key is not its declared search's pick";
    return NULL;
}
===
const char *wf_tables_check(void)
{
    const char *e;
    for (size_t i = 0; i < WF_NEROWS; i++)
        if (!wf_erows[i].holds || !wf_erows[i].ct) return "a Table E row is a hole";
    if ((e = wf_span_check())) return e;
    return wf_ren_check();
}
>>>
@@ window_frame.c  O1: wf_plan_site asks the pieces (same order: Table S, skeleton, stream, check, refusal)
<<<
    uint8_t st;
    size_t sr = table_s(search, (wf_frame_row)r, fu, &st);
    const char *frame = wf_frame_name((wf_frame_row)r);
    w->skel = ren_find(REN_ROWS(ren_skel), (wf_frame_row)r, REN_FRAME, NULL);
    if (sr == ST_ONE && !fu) {
        w->strm = ren_find(REN_ROWS(ren_stream), (wf_frame_row)r, st, NULL);
        w->chk = ren_find(REN_ROWS(ren_check), (wf_frame_row)r, REN_FRAME, NULL);
    }
    if (wf_srows[sr].why) {
        char *buf = why_room(al, why);
        if (!buf) return -1;
        snprintf(buf, WF_WHY_MAX, "%s: %s", frame, wf_srows[sr].why);
        return -1;
    }
===
    const char *swhy = wf_ren_pieces(w, (wf_frame_row)r, fu, search);
    const char *frame = wf_frame_name((wf_frame_row)r);
    if (swhy) {
        char *buf = why_room(al, why);
        if (!buf) return -1;
        snprintf(buf, WF_WHY_MAX, "%s: %s", frame, swhy);
        return -1;
    }
>>>

# ---- A5 (U5): wfS's searchers, window_span.c
@@ window_span.c  A5
<<<
static const kit_table wf_spantable = {
===
/* wfS's columns for stretch `st` (its chosen row's): the use's text, and
 * the file-scope text where the row has a define (0 where none). */
int wf_span_render(wf_rc *rc, kb *t, const struct wf_stretch *st)
{
    return wf_spanrows[st->row].render(rc, t, st);
}

int wf_span_define(wf_rc *rc, const struct wf_stretch *st, mf_sink *out)
{
    return wf_spanrows[st->row].define && wf_spanrows[st->row].define(rc, st, out);
}

/* THE SPAN FORM TABLE's SELF-CHECK (wf_tables_check's part of item 1): the
 * first refusal, or NULL. */
const char *wf_span_check(void)
{
    for (size_t i = 0; i < WF_NSROWS; i++)
        if (!wf_spanrows[i].holds || !wf_spanrows[i].h || !wf_spanrows[i].render ||
            !wf_spanrows[i].ct)
            return "a span form row is a hole";
    for (size_t i = 0; i < WF_NSROWS; i++)
        if ((wf_spanrows[i].render == wf_span_v) != (wf_spanrows[i].define != NULL))
            return "a span form row's define and the V renderer do not pair";
    if (!wf_spanrows[WF_NSROWS - 1].holds(NULL))
        return "the last span form row does not hold always";
    return NULL;
}

static const kit_table wf_spantable = {
>>>
@@ window_test.c  A5
<<<
            if (wf_spanrows[st->row].render(rc, t, st)) return -1;
===
            if (wf_span_render(rc, t, st)) return -1;
>>>
@@ window_find.c  A5
<<<
        if (wf_spanrows[w->str[i].row].define &&
            wf_spanrows[w->str[i].row].define(&rc, &w->str[i], out))
            return -1;
===
        if (wf_span_define(&rc, &w->str[i], out))
            return -1;
>>>

# ---- W13: kit.h keeps only names an outside file calls (the H3 family excepted)
@@ kit.h  W13: the arms' declarations move to window.h
<<<
/* The floor row (Table E's E-generic; window_site.md §2 "floor: generic")
 * and E-find's row (D172 S3: the family's own find-then-verify text). */
extern const arm wf_floor_arm;
extern const arm wf_find_arm;
===
>>>
@@ kit.h  W13
<<<
#define wf_floor_arm    MF_NS(wf_floor_arm)
#define wf_find_arm     MF_NS(wf_find_arm)
===
>>>
@@ kit.h  W13: wf_part_site is parts' own (static)
<<<
#define wf_part_site     MF_NS(wf_part_site)
===
>>>
@@ kit.h  W13
<<<
/* Fills `*out` with FUNC part `i` of pre-check site `s` as the FIND site the
 * family decides: the offset-skip function's frame (FUNC/RETURN, miss `n`),
 * the part's predicate, and its window facts as the site's. */
void wf_part_site(const mf_site *s, unsigned i, mf_site *out);
===
>>>
@@ window_parts.c  W13: wf_part_site's comment takes kit.h's text; static
<<<
/* Part `i` of `s` as the FIND site the family decides (kit.h). */
void wf_part_site(const mf_site *s, unsigned i, mf_site *out)
===
/* Fills `*out` with FUNC part `i` of pre-check site `s` as the FIND site the
 * family decides: the offset-skip function's frame (FUNC/RETURN, miss `n`),
 * the part's predicate, and its window facts as the site's. */
static void wf_part_site(const mf_site *s, unsigned i, mf_site *out)
>>>

# ---- window.h: its head comment (W3) and include guard
@@ window.h  the family comment names the header
<<<
 * memfn/src/window.c — THE WINDOW FAMILY (D172;
===
 * memfn/src/window.h — THE WINDOW FAMILY's private header (window_split.md;
 * included by the window_*.c files only), and the family (D172;
>>>
@@ window.h  include guard after the family comment
<<<
 * (docs/dev/lanes/wsc1_report.md, finding F-1).
 */
===
 * (docs/dev/lanes/wsc1_report.md, finding F-1).
 */
#ifndef MF_WINDOW_H
#define MF_WINDOW_H

#include "kit.h"
>>>

# ---- U2b (O6 inside, widened per W12): the other kit files' private set spellings
# re-spell to the family. Kept byte for byte: S452's `if (m == 1)` (finder.c) and S804's
# `return n == 1;` (precheck.c), so neither mech row re-binds; no G2 plant quotes a line here.
# Excluded by R-1: formhash.c:493, k1_ref.c (main's ruling; not this unit).
rename popcount256 kit_pos_count in finder.c
rename set_count kit_pos_count in ofsskip.c
rename set_first kit_pos_first in ofsskip.c
rename set_first_member kit_pos_first in presence.c

@@ finder.c  U2b: popcount256 is kit_pos_count
<<<
static unsigned kit_pos_count(const uint8_t s[32])
{
    unsigned n = 0;
    for (unsigned i = 0; i < 32; i++) n += (unsigned)__builtin_popcount(s[i]);
    return n;
}

===
>>>
@@ finder.c  U2b (S452's line kept)
<<<
            unsigned m = 0;
            for (unsigned x = 0; x < 32; x++) m += (unsigned)__builtin_popcount(rs->set[j][x]);
            if (m == 1)
===
            unsigned m = kit_pos_count(rs->set[j]);
            if (m == 1)
>>>
@@ finder.c  U2b: the first member and an open read
<<<
        int b = -1;
        for (unsigned x = 0; x < 256 && b < 0; x++)
            if (s->pspans[i].term[0].set[x >> 3] >> (x & 7) & 1) b = (int)x;
        if (b >= 0 && (covered[b >> 3] >> (b & 7) & 1)) { k->verify = 0; continue; }
===
        int b = kit_pos_first(s->pspans[i].term[0].set);
        if (b >= 0 && kit_pos_in(covered, (unsigned)b)) { k->verify = 0; continue; }
>>>
@@ ofsskip.c  U2b: set_count and set_first are the family's
<<<
/* How many bytes the 256-bit set holds. */
static int kit_pos_count(const uint8_t set[32])
{
    int n = 0;
    for (int i = 0; i < 32; i++) n += __builtin_popcount(set[i]);
    return n;
}

/* The set's lowest byte (its only one, where it holds one). */
static int kit_pos_first(const uint8_t set[32])
{
    for (int b = 0; b < 256; b++)
        if ((set[b >> 3] >> (b & 7)) & 1) return b;
    return -1;
}

===
>>>
@@ precheck.c  U2b
<<<
    for (int b = 0; b < 256; b++)
        if ((p->term[0].set[b >> 3] >> (b & 7)) & 1) return b;
    return -1;
}
===
    return kit_pos_first(p->term[0].set);
}
>>>
@@ precheck.c  U2b (S804's line kept)
<<<
    int n = 0;
    for (int i = 0; i < 32; i++) n += __builtin_popcount(p->term[0].set[i]);
    return n == 1;
===
    int n = (int)kit_pos_count(p->term[0].set);
    return n == 1;
>>>
@@ presence.c  U2b: set_first_member is kit_pos_first
<<<
static int kit_pos_first(const uint8_t set[32])
{
    for (unsigned b = 0; b < 256; b++)
        if (set[b >> 3] >> (b & 7) & 1) return (int)b;
    return -1;
}

===
>>>
@@ presence.c  U2b: one_member is "only one", kit_pos_count(s) == 1 (W10's one spelling)
<<<
static int one_member(const uint8_t set[32])
{
    unsigned m = 0;
    for (unsigned i = 0; i < 32; i++) m += (unsigned)__builtin_popcount(set[i]);
    return m == 1;
}

===
>>>
@@ presence.c  U2b
<<<
    while (lo > 0 && one_member(at(src, lo - 1, buf))) lo--;
    while (hi < n && one_member(at(src, hi, buf))) hi++;
===
    while (lo > 0 && kit_pos_count(at(src, lo - 1, buf)) == 1) lo--;
    while (hi < n && kit_pos_count(at(src, hi, buf)) == 1) hi++;
>>>
@@ presence.c  U2b
<<<
rsc && one_member(rs->set[rr.scan]) ? kit_pos_first(rs->set[rr.scan]) : q;
===
rsc && kit_pos_count(rs->set[rr.scan]) == 1 ? kit_pos_first(rs->set[rr.scan]) : q;
>>>
@@ kit_pos.c  U2b: kit_mass's open read
<<<
            if (set[b >> 3] >> (b & 7) & 1) { k++; if (rate) m += rate[b]; }
===
            if (kit_pos_in(set, b)) { k++; if (rate) m += rate[b]; }
>>>
@@ compose.c  U2b
<<<
        unsigned m = 0;
        for (unsigned b = 0; b < 32; b++) m += (unsigned)__builtin_popcount(w->set[j][b]);
        if (!m)
===
        unsigned m = kit_pos_count(w->set[j]);
        if (!m)
>>>
@@ compose.c  U2b
<<<
        unsigned m = 0;
        for (unsigned b = 0; b < 32; b++) m += (unsigned)__builtin_popcount(t->set[b]);
        if (m != 1) return "a SET presence span is ONE member (PR-5: unpicked)";
===
        unsigned m = kit_pos_count(t->set);
        if (m != 1) return "a SET presence span is ONE member (PR-5: unpicked)";
>>>
@@ compose.c  U2b
<<<
        if ((p->term[0].set[x >> 3] >> (x & 7) & 1) != ((int)x == b)) return 0;
===
        if (kit_pos_in(p->term[0].set, x) != ((int)x == b)) return 0;
>>>
@@ compose.c  U2b
<<<
    for (unsigned x = 0; x < 256; x++)
        if (p->term[0].set[x >> 3] >> (x & 7) & 1) return (int)x;
    return -1;
}
===
    return kit_pos_first(p->term[0].set);
}
>>>
@@ pffind.c  U2b: set_size's count and least member (W12)
<<<
    int n = 0;
    *b = -1;
    for (int i = 0; i < 256; i++)
        if ((t->set[i >> 3] >> (i & 7)) & 1) {
            if (*b < 0) *b = i;
            n++;
        }
    return n;
===
    *b = kit_pos_first(t->set);
    return (int)kit_pos_count(t->set);
>>>
@@ generic.c  U2b: kit_set_test's range walk (W12)
<<<
        if (!((set[lo >> 3] >> (lo & 7)) & 1)) continue;
        int hi = lo;
        while (hi + 1 < 256 && ((set[(hi + 1) >> 3] >> ((hi + 1) & 7)) & 1)) hi++;
===
        if (!kit_pos_in(set, (unsigned)lo)) continue;
        int hi = lo;
        while (hi + 1 < 256 && kit_pos_in(set, (unsigned)hi + 1)) hi++;
>>>
