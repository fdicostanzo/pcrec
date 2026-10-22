/* §3¶4, §3¶7: rx_group_run and rx_shape_match directly. */
#include "t.h"

int main(void)
{
    int first = -7, n;
    n = rx_group_run(&rd_info, "n", NULL, &first);
    CHECK("run.dup", n == 2 && first == 0, "n %d first %d", n, first);
    n = rx_group_run(&rd_info, "m", NULL, &first);
    CHECK("run.absent", n == 0, "n %d", n);
    n = rx_group_run(&ra_info, "n", NULL, &first);
    CHECK("run.nogroups", n == 0, "n %d", n);
    n = rx_group_run(&rn_info, "m", NULL, &first);
    CHECK("run.m", n == 1 && rn_info.groups[first].name && !strcmp(rn_info.groups[first].name, "m"), "n %d", n);
    n = rx_group_run(&rn_info, "", NULL, &first);
    CHECK("run.empty.name", n == 0, "n %d", n);
    n = rx_group_run(&rn_info, "n", "nosuchscope", &first);
    CHECK("run.scope.absent", n == 0, "n %d", n);
    /* a synthetic sorted index with a run in the middle and at the ends */
    rx_group_entry g[] = { { "a", 1, 1, NULL }, { "b", 2, 2, NULL }, { "b", 3, 3, NULL }, { "b", 4, 4, NULL },
                           { "c", 5, 5, NULL }, { "s.b", 6, 6, "s" }, { "s.b", 7, 7, "s" }, { "t.b", 8, 8, "t" } };
    struct rx_info r = ra_info;
    r.groups = g; r.nnames = 5; r.nentries = 8; r.ncaps = 9; r.ngroups = 8;
    n = rx_group_run(&r, "b", NULL, &first);
    CHECK("run.mid", n == 3 && first == 1, "n %d first %d", n, first);
    n = rx_group_run(&r, "a", NULL, &first);
    CHECK("run.head", n == 1 && first == 0, "n %d first %d", n, first);
    n = rx_group_run(&r, "c", NULL, &first);
    CHECK("run.tail", n == 1 && first == 4, "n %d first %d", n, first);
    n = rx_group_run(&r, "s.b", NULL, &first);
    CHECK("run.site.not.caller", n == 0, "n %d: the caller scope is [0,nnames)", n);
    n = rx_group_run(&r, "b", "s", &first);
    CHECK("run.site", n == 2 && first == 5, "n %d first %d", n, first);
    n = rx_group_run(&r, "b", "t", &first);
    CHECK("run.site.t", n == 1 && first == 7, "n %d first %d", n, first);
    n = rx_group_run(&r, "b", "", &first);
    CHECK("run.site.emptyref", n == 0, "n %d first %d (ref \"\" )", n, first);
    for (int k = 1; k <= 7; k++) {   /* every run length, bsearch landing anywhere in it */
        rx_group_entry gg[16]; int m = 0;
        gg[m++] = (rx_group_entry){ "a", 1, 1, NULL };
        for (int i = 0; i < k; i++) gg[m++] = (rx_group_entry){ "m", 2 + i, 2 + i, NULL };
        gg[m++] = (rx_group_entry){ "z", 9, 9, NULL };
        struct rx_info rr = r; rr.groups = gg; rr.nnames = m; rr.nentries = m; rr.ncaps = 12;
        n = rx_group_run(&rr, "m", NULL, &first);
        char id[32]; snprintf(id, sizeof id, "run.len%d", k);
        CHECK(id, n == k && first == 1, "n %d first %d", n, first);
    }

    /* rx_shape_match: index of the first unsatisfied row, -1 otherwise, runs filled */
    rx_subst_run runs[4];
    rx_group_entry need[] = { { "b", -1, -1, NULL }, { "c", -1, -1, NULL }, { NULL, 0, -1, NULL }, { NULL, 8, -1, NULL } };
    int i = rx_shape_match(need, 4, &r, runs);
    CHECK("shape.ok", i == -1 && runs[0].first == 1 && runs[0].count == 3 && runs[1].first == 4, "i %d", i);
    need[3].number = 9;
    i = rx_shape_match(need, 4, &r, runs);
    CHECK("shape.num.past", i == 3, "i %d", i);
    need[3].number = 8;
    g[2].slot = 9;   /* one member of the run without a slot */
    i = rx_shape_match(need, 4, &r, runs);
    CHECK("shape.run.member.noslot", i == 0, "i %d", i);
    g[2].slot = 3;
    i = rx_shape_match(need, 0, &r, runs);
    CHECK("shape.empty", i == -1, "i %d", i);
    rx_group_entry negnum[] = { { NULL, -3, -1, NULL } };
    i = rx_shape_match(negnum, 1, &r, runs);
    printf("INFO shape.negative.number i=%d (a forged numbered row -3 is %s)\n", i, i < 0 ? "SATISFIED" : "refused");
    rx_group_entry scoped[] = { { "b", -1, -1, "s" } };
    i = rx_shape_match(scoped, 1, &r, runs);
    CHECK("shape.scoped", i == -1 && runs[0].first == 5 && runs[0].count == 2, "i %d", i);
    DONE();
}
