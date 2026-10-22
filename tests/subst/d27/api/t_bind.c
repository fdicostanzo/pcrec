/* §3: the record's shape, the check (pcrec_subst_check, rx_subst_ctx_init) and
 * the by-name helper (pcrec_subst_map_names).  substb2: was the R3 bind. */
#include "t.h"

static int ctx_chk(const struct rx_info *rx, const struct rx_subst_info *t, const rx_subst_map *map,
                   unsigned flags, int *bad)
{
    rx_iter it = RX_ITER_INIT((const unsigned char *)"a", 1);
    rx_var vres[4];
    rx_ctx ctx;
    return rx_subst_ctx_init(&ctx, &it, rx, t, map, vres, flags, bad);
}

int main(void)
{
    int bad, rc;
    rx_subst_map m;
    size_t na;

    /* §3¶2 the REFERENCE LIST: every group but 0, once, first-appearance order */
    const struct rx_subst_info *S = &sall_subst_info;   /* $n$2$0${n}$1$n${m}$0$2 */
    CHECK("shape.nrefs", S->nrefs == 4, "nrefs %d (want n,2,1,m)", S->nrefs);
    if (S->nrefs == 4) {
        CHECK("shape.order", S->refs[0].name && !strcmp(S->refs[0].name, "n") && !S->refs[1].name
              && S->refs[1].number == 2 && !S->refs[2].name && S->refs[2].number == 1
              && S->refs[3].name && !strcmp(S->refs[3].name, "m"), "order wrong");
    }
    int okf = 1;
    for (int i = 0; i < S->nrefs; i++) {
        if (S->refs[i].slot != -1 || S->refs[i].ref) okf = 0;
        if (S->refs[i].name && S->refs[i].number != -1) okf = 0;
    }
    CHECK("shape.fields", okf, "slot/ref/number not as §3¶2");
    CHECK("shape.maxnum", S->maxnum == 2, "maxnum %d", S->maxnum);
    CHECK("shape.npieces", S->npieces == 10 && SALL_PIECES == 10, "npieces %d (gap + 9 forms, §4¶5)", S->npieces);
    CHECK("shape.nvrefs0", S->nvrefs == 0 && S->vrefs == NULL, "nvrefs %d vrefs %p", S->nvrefs, (void *)S->vrefs);
    CHECK("shape.name", !strcmp(S->name, "sall"), "name %s", S->name);
    CHECK("shape.abi", S->abi == PCREC_RX_ABI_H, "abi %u", S->abi);
    CHECK("shape.text", S->template_len == strlen("$n$2$0${n}$1$n${m}$0$2")
          && !memcmp(S->template_text, "$n$2$0${n}$1$n${m}$0$2", S->template_len), "template_text");
    CHECK("shape.encoding.any", S->encoding == -1, "an all-ASCII template reads the same everywhere: %d (§2¶5)", S->encoding);
    CHECK("shape.nouse", S->uses == 0 && S->support == NULL && S->support_id == 0,
          "uses %u support %p id %llu (§2¶7: no scratch, no support)", S->uses, (const void *)S->support, S->support_id);
    CHECK("shape.render", S->render == sall_render, "render pointer");
    CHECK("shape.nul.len", snul_subst_info.template_len == 6 && !memcmp(snul_subst_info.template_text, "a\0$1\0b", 6),
          "template with NULs: len %zu", snul_subst_info.template_len);
    CHECK("shape.vrefs", sv_subst_info.nvrefs == 2 && !strcmp(sv_subst_info.vrefs[0], "v")
          && !strcmp(sv_subst_info.vrefs[1], "w"), "vrefs: nvrefs %d", sv_subst_info.nvrefs);
    CHECK("shape.nonum", snone_subst_info.nrefs == 0 && snone_subst_info.maxnum == 0 && snone_subst_info.npieces == 2,
          "literal template: nrefs %d npieces %d", snone_subst_info.nrefs, snone_subst_info.npieces);
    CHECK("shape.macros", SALL_NREFS == 4 && SALL_MAXNUM == 2 && SNONE_NREFS == 1
          && SNONE_MAXNUM == 0 && SV_NREFS == 1 && SV_NVREFS == 2 && SNONE_PIECES == 2, "header constants (§1¶1)");
    CHECK("shape.s0", s0_subst_info.nrefs == 0 && s0_subst_info.maxnum == 0, "$0 template: nrefs %d", s0_subst_info.nrefs);
    CHECK("shape.dup.once", sdn_subst_info.nrefs == 1 && sdn_subst_info.refs[0].name, "<$n>: nrefs %d", sdn_subst_info.nrefs);

    /* §3¶8 the check: success, and no map: the numbers are the slots */
    bad = 99;
    rc = pcrec_subst_check(&s1_subst_info, NULL, &ra_info, 0, &bad);
    CHECK("check.nomap.ok", rc == 0 && bad == -1, "rc %d bad %d", rc, bad);
    rc = pcrec_subst_check(&s1_subst_info, NULL, &ra_info, RX_SUBST_GAPS | RX_SUBST_STRICT, &bad);
    CHECK("check.flags.ok", rc == 0, "rc %d", rc);
    rc = pcrec_subst_check(&s1_subst_info, NULL, &ra_info, 0x4, &bad);
    CHECK("check.flag.unknown", rc == PCREC_SUBST_MISMATCH && bad == -1, "rc %d bad %d", rc, bad);
    rc = pcrec_subst_check(&s0_subst_info, NULL, &ra_info, 0, &bad);
    CHECK("check.nomap.noreferences", rc == 0, "rc %d", rc);
    /* §3¶3: a named reference with no map is MISSING_REF at its index */
    rc = pcrec_subst_check(&snm_subst_info, NULL, &rn_info, 0, &bad);
    CHECK("check.nomap.named", rc == PCREC_SUBST_MISSING_REF && bad == 0, "rc %d bad %d", rc, bad);
    rc = pcrec_subst_check(&sn_subst_info, NULL, &ra_info, 0, &bad);   /* $3${zz}$1 on 2 groups: refs 3, zz, 1 */
    CHECK("check.nomap.k.ge.ncaps", rc == PCREC_SUBST_MISSING_REF && bad == 0, "rc %d bad %d", rc, bad);
    struct rx_info rxx = ra_info; rxx.ncaps = 2;   /* ngroups 2 */
    rc = pcrec_subst_check(&se1_subst_info, NULL, &rxx, 0, &bad);   /* [$1|$2] */
    CHECK("check.nomap.k.past", rc == PCREC_SUBST_MISSING_REF && bad == 1, "rc %d bad %d", rc, bad);
    /* --no-captures: the group exists in the text but has no slot (k >= ncaps) */
    rc = pcrec_subst_check(&s1_subst_info, NULL, &rnc_info, 0, &bad);
    CHECK("check.nocaps.num", rc == PCREC_SUBST_MISSING_REF && bad == 0, "rc %d bad %d", rc, bad);
    rc = pcrec_subst_check(&s0_subst_info, NULL, &rnc_info, 0, &bad);
    CHECK("check.nocaps.zero", rc == 0, "rc %d", rc);
    /* MISMATCH: records and rx fields that do not belong (§3¶10) */
    struct rx_subst_info sx = s1_subst_info; sx.abi = PCREC_RX_ABI_H + 1;
    rc = pcrec_subst_check(&sx, NULL, &ra_info, 0, &bad);
    CHECK("check.subabi", rc == PCREC_SUBST_MISMATCH && bad == -1, "rc %d bad %d", rc, bad);
    sx.abi = PCREC_RX_ABI_H - 1;
    rc = pcrec_subst_check(&sx, NULL, &ra_info, 0, &bad);
    CHECK("check.subabi.old", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    rxx = ra_info; rxx.ncaps = 0;
    rc = pcrec_subst_check(&s0_subst_info, NULL, &rxx, 0, &bad);
    CHECK("check.ncaps0", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    rxx.ncaps = -5;
    rc = pcrec_subst_check(&s0_subst_info, NULL, &rxx, 0, &bad);
    CHECK("check.ncapsneg", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    sx = s1_subst_info; sx.encoding = PCREC_ENC_UTF8_;   /* a utf8 record over a byte rx (§2¶5) */
    rc = pcrec_subst_check(&sx, NULL, &ra_info, 0, &bad);
    CHECK("check.encoding.mismatch", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    sx.encoding = PCREC_ENC_BYTE_;
    rc = pcrec_subst_check(&sx, NULL, &ru_info, 0, &bad);   /* a byte record over a utf8 rx */
    CHECK("check.encoding.mismatch.byte", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    CHECK("check.encoding.record.any", s0_subst_info.encoding == -1, "encoding %d", s0_subst_info.encoding);
    rc = pcrec_subst_check(&s0_subst_info, NULL, &ru_info, 0, &bad);   /* encoding -1 */
    CHECK("check.encoding.any", rc == 0, "encoding -1 reads the same in every encoding: rc %d", rc);
    unsigned long long fake_id = 1;
    sx = s1_subst_info; sx.support = &fake_id; sx.support_id = 2;   /* §10¶3: a support unit of other text */
    rc = pcrec_subst_check(&sx, NULL, &ra_info, 0, &bad);
    CHECK("check.support.id", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    sx.support_id = 1;
    rc = pcrec_subst_check(&sx, NULL, &ra_info, 0, &bad);
    CHECK("check.support.id.same", rc == 0, "rc %d", rc);
    /* §3¶3: a composed rx (ncaps > ngroups + 1) takes no no-map form */
    rxx = ra_info; rxx.ncaps = rxx.ngroups + 2;
    rc = pcrec_subst_check(&s0_subst_info, NULL, &rxx, 0, &bad);
    CHECK("check.composed.nomap", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);

    /* §3¶13 the by-name helper: success and the runs */
    bad = 99; na = 99;
    rc = pcrec_subst_map_names(&snm_subst_info, &rn_info, 0, SLOTS, SNM_NREFS + rn_info.ncaps, RUNS, SNM_NREFS, &m, &bad, &na);
    CHECK("names.ok", rc == 0 && bad == -1 && na == 0, "rc %d bad %d na %zu", rc, bad, na);   /* $n $m $1 */
    CHECK("names.runs", RUNS[0].count == 1 && RUNS[1].count == 1 && RUNS[2].count == 1 && m.nrun == (size_t)SNM_NREFS
          && m.slot[RUNS[0].first] == 1 && m.slot[RUNS[1].first] == 2 && m.slot[RUNS[2].first] == 1,
          "runs %d/%d/%d slots", RUNS[0].count, RUNS[1].count, RUNS[2].count);
    /* a template of numbers only is mapped too (§3¶14: number k reads slot k) */
    rc = pcrec_subst_map_names(&s1_subst_info, &ra_info, 0, SLOTS, 8, RUNS, 1, &m, &bad, &na);
    CHECK("names.numbers", rc == 0 && m.slot[RUNS[0].first] == 1, "rc %d", rc);
    /* MISMATCH: run or slot storage too small, an unknown option, a forged abi */
    bad = 99;
    rc = pcrec_subst_map_names(&snm_subst_info, &rn_info, 0, SLOTS, 64, RUNS, 1, &m, &bad, &na);
    CHECK("names.nrun.small", rc == PCREC_SUBST_MISMATCH && bad == -1, "rc %d bad %d", rc, bad);
    rc = pcrec_subst_map_names(&snm_subst_info, &rn_info, 0, SLOTS, 2, RUNS, 8, &m, &bad, &na);
    CHECK("names.nslot.small", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    rc = pcrec_subst_map_names(&snm_subst_info, &rn_info, 0x2, SLOTS, 64, RUNS, 8, &m, &bad, &na);
    CHECK("names.opt.unknown", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    sx = snm_subst_info; sx.abi = PCREC_RX_ABI_H + 1;
    rc = pcrec_subst_map_names(&sx, &rn_info, 0, SLOTS, 64, RUNS, 8, &m, &bad, &na);
    CHECK("names.subabi", rc == PCREC_SUBST_MISMATCH && bad == -1, "rc %d bad %d", rc, bad);
    sx = snm_subst_info; sx.encoding = PCREC_ENC_UTF8_;
    rc = pcrec_subst_map_names(&sx, &rn_info, 0, SLOTS, 64, RUNS, 8, &m, &bad, &na);
    CHECK("names.encoding", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    rxx = ra_info; rxx.ncaps = 0;
    rc = pcrec_subst_map_names(&s0_subst_info, &rxx, 0, SLOTS, 8, RUNS, 1, &m, &bad, &na);
    CHECK("names.ncaps0", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);

    /* MISSING_REF and the reference index: sn = $3${zz}$1 -> refs [3, zz, 1] */
    bad = 99;
    rc = pcrec_subst_map_names(&sn_subst_info, &ra_info, 0, SLOTS, 64, RUNS, 8, &m, &bad, &na);
    CHECK("names.missing.num", rc == PCREC_SUBST_MISSING_REF && bad == 0, "rc %d bad %d", rc, bad);
    rc = pcrec_subst_map_names(&sn_subst_info, &rz_info, 0, SLOTS, 64, RUNS, 8, &m, &bad, &na);   /* has zz, 1 group */
    CHECK("names.missing.num.rz", rc == PCREC_SUBST_MISSING_REF && bad == 0, "rc %d bad %d", rc, bad);
    rc = pcrec_subst_map_names(&snm_subst_info, &ra_info, 0, SLOTS, 64, RUNS, 8, &m, &bad, &na);   /* no names */
    CHECK("names.missing.name", rc == PCREC_SUBST_MISSING_REF && bad == 0, "rc %d bad %d", rc, bad);
    rx_group_entry ge[1] = { { "n", 1, 1, NULL } };   /* only n: m is the second reference */
    rxx = rn_info; rxx.groups = ge; rxx.nnames = 1; rxx.nentries = 1;
    rc = pcrec_subst_map_names(&snm_subst_info, &rxx, 0, SLOTS, 64, RUNS, 8, &m, &bad, &na);
    CHECK("names.missing.second", rc == PCREC_SUBST_MISSING_REF && bad == 1, "rc %d bad %d", rc, bad);
    /* RX_SUBST_MAP_ABSENT: the absent reference becomes NOGROUP, counted, the first one named */
    rc = pcrec_subst_map_names(&snm_subst_info, &rxx, RX_SUBST_MAP_ABSENT, SLOTS, 64, RUNS, 8, &m, &bad, &na);
    CHECK("names.absent", rc == 0 && na == 1 && bad == 1 && m.slot[RUNS[1].first] == RX_SUBST_NOGROUP,
          "rc %d na %zu bad %d", rc, na, bad);
    /* a forged named row with slot >= ncaps or -1 */
    ge[0] = (rx_group_entry){ "n", 1, 5, NULL };
    rxx = rn_info; rxx.groups = ge; rxx.nnames = 1; rxx.nentries = 1;
    rc = pcrec_subst_map_names(&sdn_subst_info, &rxx, 0, SLOTS, 64, RUNS, 8, &m, &bad, &na);
    CHECK("names.slot.past", rc == PCREC_SUBST_MISSING_REF && bad == 0, "rc %d bad %d", rc, bad);
    ge[0].slot = -1;
    rc = pcrec_subst_map_names(&sdn_subst_info, &rxx, 0, SLOTS, 64, RUNS, 8, &m, &bad, &na);
    CHECK("names.slot.neg", rc == PCREC_SUBST_MISSING_REF && bad == 0, "rc %d bad %d", rc, bad);
    /* a numbered row k <= ngroups but k >= ncaps, and k > ngroups with room in ncaps (§3¶14's two tests) */
    rxx = ra_info; rxx.ncaps = 2;   /* ngroups 2 */
    rc = pcrec_subst_map_names(&se1_subst_info, &rxx, 0, SLOTS, 64, RUNS, 8, &m, &bad, &na);
    CHECK("names.k.ge.ncaps", rc == PCREC_SUBST_MISSING_REF && bad == 1, "rc %d bad %d", rc, bad);
    rxx = ra_info; rxx.ngroups = 1;  /* ncaps 3 */
    rc = pcrec_subst_map_names(&se1_subst_info, &rxx, 0, SLOTS, 64, RUNS, 8, &m, &bad, &na);
    CHECK("names.k.gt.ngroups", rc == PCREC_SUBST_MISSING_REF && bad == 1, "rc %d bad %d", rc, bad);

    /* duplicate names: the run, and the element's first-that-participated walk */
    rc = pcrec_subst_map_names(&sdn_subst_info, &rd_info, 0, SLOTS, 64, RUNS, 8, &m, &bad, &na);
    CHECK("names.dup.run", rc == 0 && RUNS[0].count == 2, "rc %d count %d", rc, RUNS[0].count);
    char out[64];
    size_t L;
    rc = rall(&rd_info, &sdn_subst_info, &m, 0, "ab", 2, 64, out, &L);
    CHECK("names.dup.render", rc == 2 && !strcmp(out, "<a><b>"), "rc %d out %s", rc, out);

    /* a map by hand (§3¶7), and the check on its shapes (§3¶10, §3¶11) */
    static const int hs[] = { 2, 1 };               /* snm refs: n, m, 1: three of them */
    rx_subst_map hm = { hs, 2, NULL, 0 };
    rc = pcrec_subst_check(&snm_subst_info, &hm, &rn_info, 0, &bad);
    CHECK("map.nslot.short", rc == PCREC_SUBST_MISMATCH && bad == -1, "rc %d bad %d", rc, bad);
    static const int hs3[] = { 2, RX_SUBST_NOGROUP, 1 };
    hm = (rx_subst_map){ hs3, 3, NULL, 0 };
    rc = pcrec_subst_check(&snm_subst_info, &hm, &rn_info, 0, &bad);
    CHECK("map.nogroup.ok", rc == 0, "rc %d", rc);
    static const int hbad[] = { 2, 4, 1 };          /* slot 4 >= ncaps 4: MISSING_REF at reference 1 */
    hm = (rx_subst_map){ hbad, 3, NULL, 0 };
    rc = pcrec_subst_check(&snm_subst_info, &hm, &rn_info, 0, &bad);
    CHECK("map.slot.past", rc == PCREC_SUBST_MISSING_REF && bad == 1, "rc %d bad %d", rc, bad);
    static const int hneg[] = { 2, -2, 1 };
    hm = (rx_subst_map){ hneg, 3, NULL, 0 };
    rc = pcrec_subst_check(&snm_subst_info, &hm, &rn_info, 0, &bad);
    CHECK("map.slot.neg", rc == PCREC_SUBST_MISSING_REF && bad == 1, "rc %d bad %d", rc, bad);
    static const int hz[] = { 0, 0, 0 };            /* slot 0 and one slot under three references are allowed (§3¶5) */
    hm = (rx_subst_map){ hz, 3, NULL, 0 };
    rc = pcrec_subst_check(&snm_subst_info, &hm, &rn_info, 0, &bad);
    CHECK("map.slot0.shared", rc == 0, "rc %d", rc);
    static const rx_subst_run hr[] = { { 0, 1 }, { 1, 2 }, { 0, 0 } };
    hm = (rx_subst_map){ hs3, 3, hr, 3 };
    rc = pcrec_subst_check(&snm_subst_info, &hm, &rn_info, 0, &bad);
    CHECK("map.run.count0", rc == PCREC_SUBST_MISSING_REF && bad == 2, "rc %d bad %d", rc, bad);
    static const rx_subst_run hr2[] = { { 0, 1 }, { 2, 2 }, { 0, 1 } };
    hm = (rx_subst_map){ hs3, 3, hr2, 3 };
    rc = pcrec_subst_check(&snm_subst_info, &hm, &rn_info, 0, &bad);
    CHECK("map.run.past", rc == PCREC_SUBST_MISSING_REF && bad == 1, "rc %d bad %d", rc, bad);
    hm = (rx_subst_map){ hs3, 3, hr2, 2 };
    rc = pcrec_subst_check(&snm_subst_info, &hm, &rn_info, 0, &bad);
    CHECK("map.nrun.short", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    /* a composed rx takes a map (§3¶3) */
    rxx = rn_info; rxx.ncaps = rxx.ngroups + 2;
    hm = (rx_subst_map){ hs3, 3, NULL, 0 };
    rc = pcrec_subst_check(&snm_subst_info, &hm, &rxx, 0, &bad);
    CHECK("map.composed.ok", rc == 0, "rc %d", rc);

    /* the context setup runs the check first and refuses before any match (§7¶4) */
    rx_ctx ctx;
    memset(&ctx, 0x77, sizeof ctx);
    rx_var vres[4];
    rx_iter it = RX_ITER_INIT((const unsigned char *)"zzz", 3);
    bad = 99;
    rc = rx_subst_ctx_init(&ctx, &it, &ra_info, &sn_subst_info, NULL, vres, 0, &bad);
    CHECK("ctxinit.refuses", rc == PCREC_SUBST_MISSING_REF && bad == 0 && ctx.len == 0x7777777777777777ULL,
          "rc %d bad %d: MISSING_REF on a subject with no match, ctx untouched", rc, bad);
    rc = ctx_chk(&ra_info, &s1_subst_info, NULL, 0, &bad);
    CHECK("ctxinit.ok", rc == 0 && bad == -1, "rc %d bad %d", rc, bad);
    rc = ctx_chk(&ra_info, &s1_subst_info, NULL, 0x8, &bad);
    CHECK("ctxinit.flag", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    /* no replace-all call when the setup refused: the by-name form on a rx that lacks the name never reaches it */
    rc = rall(&ra_info, &sn_subst_info, NULL, 0, "aab", 3, 64, out, &L);
    CHECK("setup.refused.no.output", rc == PCREC_SUBST_MISSING_REF && L == 0, "rc %d L %zu", rc, L);

    /* an rx map used for two rx, one subst, interleaved: the record and the map are const (§7¶5) */
    char o1[64], o2[64];
    rx_subst_map ma, mb;
    int sl1[4], sl2[4]; rx_subst_run ru1[1], ru2[1];
    rc = pcrec_subst_map_names(&s1_subst_info, &ra_info, 0, sl1, 4, ru1, 1, &ma, &bad, &na);
    rc |= pcrec_subst_map_names(&s1_subst_info, &rb_info, 0, sl2, 4, ru2, 1, &mb, &bad, &na);
    int r1 = rall(&ra_info, &s1_subst_info, &ma, 0, "xyab", 4, 64, o1, &L);
    int r2 = rall(&rb_info, &s1_subst_info, &mb, 0, "xyab", 4, 64, o2, &L);
    CHECK("two.maps", rc == 0 && r1 == 1 && r2 == 1 && !strcmp(o1, "xy[a]") && !strcmp(o2, "[x]ab"), "%s | %s", o1, o2);
    /* one template over two rx with the no-map form */
    r1 = rall(&ra_info, &s2_subst_info, NULL, 0, "xay", 3, 64, o1, &L);
    r2 = rall(&rb_info, &s2_subst_info, NULL, 0, "axyb", 4, 64, o2, &L);
    CHECK("two.rx", r1 == 1 && r2 == 1 && !strcmp(o1, "x<a>y") && !strcmp(o2, "a<xy>b"), "%s | %s", o1, o2);
    DONE();
}
