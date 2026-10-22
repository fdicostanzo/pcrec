/* §3: the needed shape, satisfaction, pcrec_subst_bind's codes and writes. */
#include "t.h"

int main(void)
{
    rx_subst_binding b;
    int bad, rc;
    rx_subst_run runs[8];

    /* §3¶2 the NEEDED shape: named rows first, then numbered, first-reference order, once each */
    const struct rx_subst_info *S = &sall_subst_info;   /* $n$2$0${n}$1$n${m}$0$2 */
    CHECK("shape.nneeds", S->nneeds == 5, "nneeds %d (want n,m,2,0,1)", S->nneeds);
    if (S->nneeds == 5) {
        CHECK("shape.order", S->needs[0].name && !strcmp(S->needs[0].name, "n") && S->needs[1].name
              && !strcmp(S->needs[1].name, "m") && !S->needs[2].name && S->needs[2].number == 2
              && S->needs[3].number == 0 && S->needs[4].number == 1, "order wrong");
    }
    int okf = 1;
    for (int i = 0; i < S->nneeds; i++) {
        if (S->needs[i].slot != -1 || S->needs[i].ref) okf = 0;
        if (S->needs[i].name && S->needs[i].number != -1) okf = 0;
    }
    CHECK("shape.fields", okf, "slot/ref/number not as §3¶2");
    CHECK("shape.nruns", S->nruns == 2, "nruns %d", S->nruns);
    CHECK("shape.maxnum", S->maxnum == 2, "maxnum %d", S->maxnum);
    CHECK("shape.nvrefs0", S->nvrefs == 0 && S->vrefs == NULL, "nvrefs %d vrefs %p", S->nvrefs, (void *)S->vrefs);
    CHECK("shape.name", !strcmp(S->name, "sall"), "name %s", S->name);
    CHECK("shape.abi", S->abi == PCREC_RX_ABI_H, "abi %u", S->abi);
    CHECK("shape.text", S->template_len == strlen("$n$2$0${n}$1$n${m}$0$2")
          && !memcmp(S->template_text, "$n$2$0${n}$1$n${m}$0$2", S->template_len), "template_text");
    CHECK("shape.unset.empty", S->unset == PCREC_SUBST_UNSET_EMPTY, "unset %d", S->unset);
    CHECK("shape.unset.error", se1_subst_info.unset == PCREC_SUBST_UNSET_ERROR, "unset %d", se1_subst_info.unset);
    CHECK("shape.render", S->render == sall_render, "render pointer");
    CHECK("shape.nul.len", snul_subst_info.template_len == 6 && !memcmp(snul_subst_info.template_text, "a\0$1\0b", 6),
          "template with NULs: len %zu", snul_subst_info.template_len);
    CHECK("shape.vrefs", sv_subst_info.nvrefs == 2 && !strcmp(sv_subst_info.vrefs[0], "v")
          && !strcmp(sv_subst_info.vrefs[1], "w"), "vrefs: nvrefs %d", sv_subst_info.nvrefs);
    CHECK("shape.nonum", snone_subst_info.nneeds == 0 && snone_subst_info.maxnum == 0 && snone_subst_info.nruns == 0,
          "literal template: nneeds %d", snone_subst_info.nneeds);
    CHECK("shape.macros", SALL_NREFS == 2 && SALL_NSEGS == 1 && SALL_MAXNUM == 2 && SNONE_NREFS == 1
          && SNONE_MAXNUM == 0 && SV_NREFS == 1, "header constants (§1¶1)");
    CHECK("shape.s0", s0_subst_info.nneeds == 1 && s0_subst_info.needs[0].number == 0 && s0_subst_info.maxnum == 0,
          "$0 template: nneeds %d", s0_subst_info.nneeds);

    /* §3¶5 success */
    bad = 99;
    rc = pcrec_subst_bind(&b, &rn_info, &snm_subst_info, runs, SNM_NREFS, NULL, 0, &bad);
    CHECK("bind.ok", rc == 0 && bad == -1 && b.tag == PCREC_SUBST_BOUND, "rc %d bad %d tag %x", rc, bad, b.tag);
    CHECK("bind.runs", runs[0].count == 1 && runs[1].count == 1, "runs %d/%d", runs[0].count, runs[1].count);
    /* exact nruns, zero nseg with NULL seg_user (nsegs 0) */
    rc = pcrec_subst_bind(&b, &ra_info, &s1_subst_info, runs, 0, NULL, 0, &bad);
    CHECK("bind.nruns0.nonamed", rc == 0, "a numbered-only template needs no runs: rc %d", rc);
    rc = pcrec_subst_bind(&b, &ra_info, &s1_subst_info, NULL, 0, NULL, 0, &bad);
    CHECK("bind.runsNULL.nonamed", rc == 0, "runs NULL, nruns 0: rc %d", rc);

    /* MISMATCH: nruns too small */
    bad = 99;
    rc = pcrec_subst_bind(&b, &rn_info, &snm_subst_info, runs, 1, NULL, 0, &bad);
    CHECK("bind.nruns.small", rc == PCREC_SUBST_MISMATCH && bad == -1 && b.tag != PCREC_SUBST_BOUND,
          "rc %d bad %d", rc, bad);
    /* MISMATCH: forged abi on either record */
    struct rx_subst_info sx = snm_subst_info; sx.abi = PCREC_RX_ABI_H + 1;
    rc = pcrec_subst_bind(&b, &rn_info, &sx, runs, 8, NULL, 0, &bad);
    CHECK("bind.subabi", rc == PCREC_SUBST_MISMATCH && bad == -1, "rc %d bad %d", rc, bad);
    sx.abi = PCREC_RX_ABI_H - 1;
    rc = pcrec_subst_bind(&b, &rn_info, &sx, runs, 8, NULL, 0, &bad);
    CHECK("bind.subabi.old", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    struct rx_info rxx = rn_info; rxx.abi = 0;
    rc = pcrec_subst_bind(&b, &rxx, &snm_subst_info, runs, 8, NULL, 0, &bad);
    CHECK("bind.rxabi", rc == PCREC_SUBST_MISMATCH && bad == -1, "rc %d", rc);
    /* MISMATCH: an rx with no slot */
    rxx = ra_info; rxx.ncaps = 0;
    rc = pcrec_subst_bind(&b, &rxx, &s0_subst_info, runs, 8, NULL, 0, &bad);
    CHECK("bind.ncaps0", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    rxx.ncaps = -5;
    rc = pcrec_subst_bind(&b, &rxx, &s0_subst_info, runs, 8, NULL, 0, &bad);
    CHECK("bind.ncapsneg", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    /* MISMATCH: nseg < nsegs (forged nsegs; core forms have none) */
    sx = s1_subst_info; sx.nsegs = 2;
    void *segs[2] = { 0, 0 };
    rc = pcrec_subst_bind(&b, &ra_info, &sx, runs, 8, NULL, 0, &bad);
    CHECK("bind.nseg0", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    rc = pcrec_subst_bind(&b, &ra_info, &sx, runs, 8, segs, 1, &bad);
    CHECK("bind.nseg1", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    rc = pcrec_subst_bind(&b, &ra_info, &sx, runs, 8, segs, 2, &bad);
    CHECK("bind.nseg2", rc == 0, "rc %d", rc);
    /* a seg_user passed where none is needed is accepted */
    rc = pcrec_subst_bind(&b, &ra_info, &s1_subst_info, runs, 8, segs, 2, &bad);
    CHECK("bind.nseg.extra", rc == 0, "rc %d", rc);

    /* MISSING_REF and the index (§3¶5): sn = $3${zz}$1 -> needs [zz, 3, 1] */
    bad = 99;
    rc = pcrec_subst_bind(&b, &ra_info, &sn_subst_info, runs, 8, NULL, 0, &bad);
    CHECK("bind.missing.name", rc == PCREC_SUBST_MISSING_REF && bad == 0 && b.tag != PCREC_SUBST_BOUND,
          "rc %d bad %d", rc, bad);
    rc = pcrec_subst_bind(&b, &rz_info, &sn_subst_info, runs, 8, NULL, 0, &bad);   /* has zz, 1 group */
    CHECK("bind.missing.num", rc == PCREC_SUBST_MISSING_REF && bad == 1, "rc %d bad %d", rc, bad);
    /* a refusal after a success: the tag must not stay BOUND */
    rc = pcrec_subst_bind(&b, &ra_info, &s1_subst_info, runs, 8, NULL, 0, &bad);
    rc = pcrec_subst_bind(&b, &rb_info, &sn_subst_info, runs, 8, NULL, 0, &bad);
    CHECK("bind.refuse.after.ok", rc == PCREC_SUBST_MISSING_REF && b.tag != PCREC_SUBST_BOUND, "tag %x", b.tag);
    rc = pcrec_subst_bind(&b, &ra_info, &s1_subst_info, runs, 8, NULL, 0, &bad);
    sx = s1_subst_info; sx.abi = 1;
    rc = pcrec_subst_bind(&b, &ra_info, &sx, runs, 8, NULL, 0, &bad);
    CHECK("bind.mismatch.after.ok", rc == PCREC_SUBST_MISMATCH && b.tag != PCREC_SUBST_BOUND, "tag %x", b.tag);
    size_t L, K;
    rc = glue(&b, "aab", 3, SIZE_MAX, 64, NULL, &L, &K);
    CHECK("glue.after.refused.bind", rc == PCREC_SUBST_MISMATCH && L == 0 && K == 0, "rc %d", rc);

    /* --no-captures: the group exists in the text but has no slot (§3¶3: k < ncaps) */
    rc = pcrec_subst_bind(&b, &rnc_info, &s1_subst_info, runs, 8, NULL, 0, &bad);
    CHECK("bind.nocaps.num", rc == PCREC_SUBST_MISSING_REF && bad == 0, "rc %d bad %d", rc, bad);
    rc = pcrec_subst_bind(&b, &rnc_info, &s0_subst_info, runs, 8, NULL, 0, &bad);
    CHECK("bind.nocaps.zero", rc == 0, "rc %d", rc);
    /* a forged named row with slot >= ncaps or -1 */
    rx_group_entry ge[1] = { { "n", 1, 5, NULL } };
    rxx = rn_info; rxx.groups = ge; rxx.nnames = 1; rxx.nentries = 1;
    rc = pcrec_subst_bind(&b, &rxx, &sdn_subst_info, runs, 8, NULL, 0, &bad);
    CHECK("bind.slot.past", rc == PCREC_SUBST_MISSING_REF && bad == 0, "rc %d bad %d", rc, bad);
    ge[0].slot = -1;
    rc = pcrec_subst_bind(&b, &rxx, &sdn_subst_info, runs, 8, NULL, 0, &bad);
    CHECK("bind.slot.neg", rc == PCREC_SUBST_MISSING_REF && bad == 0, "rc %d bad %d", rc, bad);
    /* a numbered row k <= ngroups but k >= ncaps */
    rxx = ra_info; rxx.ncaps = 2;   /* ngroups 2 */
    rc = pcrec_subst_bind(&b, &rxx, &se1_subst_info, runs, 8, NULL, 0, &bad);
    CHECK("bind.k.ge.ncaps", rc == PCREC_SUBST_MISSING_REF && bad == 1, "rc %d bad %d", rc, bad);
    rxx = ra_info; rxx.ngroups = 1;  /* ncaps 3 */
    rc = pcrec_subst_bind(&b, &rxx, &se1_subst_info, runs, 8, NULL, 0, &bad);
    CHECK("bind.k.gt.ngroups", rc == PCREC_SUBST_MISSING_REF && bad == 1, "rc %d bad %d", rc, bad);

    /* duplicate names: the run */
    rc = pcrec_subst_bind(&b, &rd_info, &sdn_subst_info, runs, 8, NULL, 0, &bad);
    CHECK("bind.dup.run", rc == 0 && runs[0].count == 2, "rc %d count %d", rc, runs[0].count);
    char out[64];
    rc = glue(&b, "ab", 2, SIZE_MAX, 64, out, &L, &K);
    CHECK("glue.dup.render", rc == 0 && !strcmp(out, "<a><b>") && K == 2, "rc %d out %s", rc, out);

    /* a binding reused: rebind the same object to a different rx (§3¶5 keeps pointers to both records) */
    rc = pcrec_subst_bind(&b, &ra_info, &s2_subst_info, runs, 8, NULL, 0, &bad);
    rc |= glue(&b, "xay", 3, SIZE_MAX, 64, out, &L, &K);
    CHECK("rebind.a", rc == 0 && !strcmp(out, "x<a>y"), "rc %d out %s", rc, out);
    rc = pcrec_subst_bind(&b, &rb_info, &s2_subst_info, runs, 8, NULL, 0, &bad);
    rc |= glue(&b, "axyb", 4, SIZE_MAX, 64, out, &L, &K);
    CHECK("rebind.b", rc == 0 && !strcmp(out, "a<xy>b"), "rc %d out %s", rc, out);
    /* two bindings of one subst to two rx, used interleaved */
    rx_subst_binding b1, b2; rx_subst_run r1[2], r2[2];
    pcrec_subst_bind(&b1, &ra_info, &s1_subst_info, r1, 2, NULL, 0, &bad);
    pcrec_subst_bind(&b2, &rb_info, &s1_subst_info, r2, 2, NULL, 0, &bad);
    rc = glue(&b1, "xyab", 4, SIZE_MAX, 64, out, &L, &K);
    CHECK("two.bindings.1", rc == 0 && !strcmp(out, "xy[a]"), "out %s", out);
    rc = glue(&b2, "xyab", 4, SIZE_MAX, 64, out, &L, &K);
    CHECK("two.bindings.2", rc == 0 && !strcmp(out, "[x]ab"), "out %s", out);

    /* a zeroed / garbage binding */
    rx_subst_binding z; memset(&z, 0, sizeof z);
    L = K = 5;
    unsigned char o1[8]; rx_iter it = RX_ITER_INIT((const unsigned char *)"a", 1);
    rc = pcrec_subst(&z, &it, SIZE_MAX, o1, 8, &L, &K);
    CHECK("glue.zeroed.binding", rc == PCREC_SUBST_MISMATCH && L == 0 && K == 0, "rc %d L %zu K %zu", rc, L, K);
    /* a bound binding whose rx record is later seen with another abi (dlopen case, §1¶4) */
    rxx = ra_info;
    rc = pcrec_subst_bind(&b, &rxx, &s1_subst_info, runs, 8, NULL, 0, &bad);
    rxx.abi = 1;
    it = RX_ITER_INIT((const unsigned char *)"a", 1);
    rc = pcrec_subst(&b, &it, SIZE_MAX, o1, 8, &L, &K);
    CHECK("glue.rx.abi.changed", rc == PCREC_SUBST_MISMATCH && L == 0 && K == 0, "rc %d", rc);
    sx = s1_subst_info;
    rc = pcrec_subst_bind(&b, &ra_info, &sx, runs, 8, NULL, 0, &bad);
    sx.abi = 1;
    it = RX_ITER_INIT((const unsigned char *)"a", 1);
    rc = pcrec_subst(&b, &it, SIZE_MAX, o1, 8, &L, &K);
    CHECK("glue.sub.abi.changed", rc == PCREC_SUBST_MISMATCH && L == 0 && K == 0, "rc %d", rc);
    /* rx without next_n */
    rxx = ra_info; rxx.next = 0; rxx.next_n = 0;
    rc = pcrec_subst_bind(&b, &rxx, &s1_subst_info, runs, 8, NULL, 0, &bad);
    it = RX_ITER_INIT((const unsigned char *)"a", 1);
    L = K = 5;
    int rc2 = pcrec_subst(&b, &it, SIZE_MAX, o1, 8, &L, &K);
    CHECK("glue.no.next_n", rc2 < 0 && rc2 != -1 && L == 0 && K == 0,
          "bind rc %d (the contract does not name next_n NULL at bind), glue rc %d", rc, rc2);
    DONE();
}
