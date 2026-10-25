/* §3¶17, §3¶14: pcrec_subst_group_run directly, and the run/slot layout pcrec_subst_map_names
 * builds over a synthetic group index (was rx_shape_match, R3).  substb2. */
#include "t.h"

int main(void)
{
    int first = -7, n;
    n = pcrec_subst_group_run(&rd_info, "n", NULL, &first);
    CHECK("run.dup", n == 2 && first == 0, "n %d first %d", n, first);
    n = pcrec_subst_group_run(&rd_info, "m", NULL, &first);
    CHECK("run.absent", n == 0, "n %d", n);
    n = pcrec_subst_group_run(&ra_info, "n", NULL, &first);
    CHECK("run.nogroups", n == 0, "n %d", n);
    n = pcrec_subst_group_run(&rn_info, "m", NULL, &first);
    CHECK("run.m", n == 1 && rn_info.groups[first].name && !strcmp(rn_info.groups[first].name, "m"), "n %d", n);
    n = pcrec_subst_group_run(&rn_info, "", NULL, &first);
    CHECK("run.empty.name", n == 0, "n %d", n);
    n = pcrec_subst_group_run(&rn_info, "n", "nosuchscope", &first);
    CHECK("run.scope.absent", n == 0, "n %d", n);
    /* a synthetic sorted index with a run in the middle and at the ends */
    rx_group_entry g[] = { { "a", 1, 1, NULL }, { "b", 2, 2, NULL }, { "b", 3, 3, NULL }, { "b", 4, 4, NULL },
                           { "c", 5, 5, NULL }, { "s.b", 6, 6, "s" }, { "s.b", 7, 7, "s" }, { "t.b", 8, 8, "t" } };
    struct rx_info r = ra_info;
    r.groups = g; r.nnames = 5; r.nentries = 8; r.ncaps = 9; r.ngroups = 8;
    n = pcrec_subst_group_run(&r, "b", NULL, &first);
    CHECK("run.mid", n == 3 && first == 1, "n %d first %d", n, first);
    n = pcrec_subst_group_run(&r, "a", NULL, &first);
    CHECK("run.head", n == 1 && first == 0, "n %d first %d", n, first);
    n = pcrec_subst_group_run(&r, "c", NULL, &first);
    CHECK("run.tail", n == 1 && first == 4, "n %d first %d", n, first);
    n = pcrec_subst_group_run(&r, "s.b", NULL, &first);
    CHECK("run.site.not.caller", n == 0, "n %d: the caller scope is [0,nnames)", n);
    n = pcrec_subst_group_run(&r, "b", "s", &first);
    CHECK("run.site", n == 2 && first == 5, "n %d first %d", n, first);
    n = pcrec_subst_group_run(&r, "b", "t", &first);
    CHECK("run.site.t", n == 1 && first == 7, "n %d first %d", n, first);
    n = pcrec_subst_group_run(&r, "b", "", &first);
    CHECK("run.site.emptyref", n == 0, "n %d first %d (ref \"\" )", n, first);
    for (int k = 1; k <= 7; k++) {   /* every run length, bsearch landing anywhere in it */
        rx_group_entry gg[16]; int m = 0;
        gg[m++] = (rx_group_entry){ "a", 1, 1, NULL };
        for (int i = 0; i < k; i++) gg[m++] = (rx_group_entry){ "m", 2 + i, 2 + i, NULL };
        gg[m++] = (rx_group_entry){ "z", 9, 9, NULL };
        struct rx_info rr = r; rr.groups = gg; rr.nnames = m; rr.nentries = m; rr.ncaps = 12;
        n = pcrec_subst_group_run(&rr, "m", NULL, &first);
        char id[32]; snprintf(id, sizeof id, "run.len%d", k);
        CHECK(id, n == k && first == 1, "n %d first %d", n, first);
    }

    /* pcrec_subst_map_names over the synthetic index: the runs and slots it lays out (§3¶14) */
    rx_group_entry need[] = { { "b", -1, -1, NULL }, { "c", -1, -1, NULL }, { NULL, 8, -1, NULL }, { NULL, 1, -1, NULL } };
    struct pcrec_subst_info tt = sall_subst_info;
    tt.refs = need; tt.nrefs = 4;
    pcrec_subst_run runs[4];
    int slots[32], bad = 99;
    size_t na;
    pcrec_subst_map m;
    int rc = pcrec_subst_map_names(&tt, &r, 0, slots, 32, runs, 4, &m, &bad, &na);
    CHECK("map.ok", rc == 0 && runs[0].count == 3 && runs[1].count == 1 && runs[2].count == 1 && runs[3].count == 1
          && slots[runs[0].first] == 2 && slots[runs[0].first + 1] == 3 && slots[runs[0].first + 2] == 4
          && slots[runs[1].first] == 5 && slots[runs[2].first] == 8 && slots[runs[3].first] == 1,
          "rc %d counts %d %d %d %d", rc, runs[0].count, runs[1].count, runs[2].count, runs[3].count);
    CHECK("map.shape", m.run == runs && m.nrun == 4 && m.slot == slots, "map fields");
    need[2].number = 9;   /* past ngroups 8 */
    rc = pcrec_subst_map_names(&tt, &r, 0, slots, 32, runs, 4, &m, &bad, &na);
    CHECK("map.num.past", rc == PCREC_SUBST_MISSING_REF && bad == 2, "rc %d bad %d", rc, bad);
    need[2].number = 8;
    g[2].slot = 9;   /* one member of the run outside ncaps 9: the whole name lacks */
    rc = pcrec_subst_map_names(&tt, &r, 0, slots, 32, runs, 4, &m, &bad, &na);
    CHECK("map.run.member.noslot", rc == PCREC_SUBST_MISSING_REF && bad == 0, "rc %d bad %d", rc, bad);
    g[2].slot = 3;
    tt.nrefs = 0;
    rc = pcrec_subst_map_names(&tt, &r, 0, slots, 32, runs, 0, &m, &bad, &na);
    CHECK("map.empty", rc == 0, "rc %d", rc);
    tt.nrefs = 4;
    need[2].number = -3;   /* a forged numbered row: the contract is silent (§3¶14 says number k >= 1) */
    rc = pcrec_subst_map_names(&tt, &r, 0, slots, 32, runs, 4, &m, &bad, &na);
    printf("INFO map.negative.number rc=%d (a forged numbered row -3 is %s)\n", rc, rc == 0 ? "SATISFIED" : "refused");
    DONE();
}
