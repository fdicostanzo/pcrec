/* harness.c -- [ENG-ISL.S0] driver: for every (pattern, subject) pair, run
 * all five dispatch algorithms over every subject position, check (b)/(c)/
 * (d)/(e) against (a)'s answer (the oracle), and emit TSVs under results/.
 * (e), the VM-native trie walk, is ruling R1 (Frank, 2026-09-03) -- the
 * PRIMARY candidate, added mid-study; it shares (c)'s trie (no separate
 * construction line in construction.tsv) and additionally reports frames
 * pushed and the deferred-list ("mask width") it needed, both 0 for every
 * other algorithm.
 *
 * Usage:
 *   altdispatch --patterns DIR --subjects DIR --out DIR [--rounds N]
 *               [--pattern-list a,b,c] [--subject-list x,y,z]
 */
#include "common.h"
#include "algo_serial.h"
#include "algo_firstbyte.h"
#include "algo_trie.h"
#include "algo_hash.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <math.h>

#define ROUNDS_DEFAULT 11

static double loadavg1(void)
{
    FILE *f = fopen("/proc/loadavg", "r");
    if (!f) return -1.0;
    double l1 = -1.0;
    if (fscanf(f, "%lf", &l1) != 1) l1 = -1.0;
    fclose(f);
    return l1;
}

static int cmp_double(const void *a, const void *b)
{
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

static double median(double *v, int n)
{
    qsort(v, (size_t)n, sizeof(double), cmp_double);
    return n % 2 ? v[n / 2] : (v[n / 2 - 1] + v[n / 2]) / 2.0;
}

typedef struct { char names[256][64]; int n; } NameList;

static void list_dir_branches(const char *dir, NameList *nl)
{
    DIR *d = opendir(dir);
    if (!d) { fprintf(stderr, "cannot open %s\n", dir); exit(1); }
    struct dirent *e;
    while ((e = readdir(d))) {
        size_t l = strlen(e->d_name);
        if (l > 9 && strcmp(e->d_name + l - 9, ".branches") == 0) {
            if (nl->n >= 256) { fprintf(stderr, "too many patterns\n"); exit(1); }
            size_t keep = l - 9;
            if (keep >= sizeof nl->names[0]) keep = sizeof nl->names[0] - 1;
            memcpy(nl->names[nl->n], e->d_name, keep);
            nl->names[nl->n][keep] = 0;
            nl->n++;
        }
    }
    closedir(d);
}

static void split_csv(const char *s, NameList *nl)
{
    nl->n = 0;
    const char *p = s;
    while (*p) {
        const char *comma = strchr(p, ',');
        size_t l = comma ? (size_t)(comma - p) : strlen(p);
        if (l >= sizeof nl->names[0]) l = sizeof nl->names[0] - 1;
        memcpy(nl->names[nl->n], p, l);
        nl->names[nl->n][l] = 0;
        nl->n++;
        p += l;
        if (comma) p++;
    }
}

/* ------------------------------------------------------------------ */

typedef struct {
    const char *label;
    Cost cost;
    long long mismatches;
    double construct_ns;
    size_t table_bytes;
} AlgoRun;

int main(int argc, char **argv)
{
    const char *patterns_dir = "patterns";
    const char *subjects_dir = "subjects";
    const char *out_dir = "results";
    int rounds = ROUNDS_DEFAULT;
    NameList pat_list = {.n = 0}, subj_list = {.n = 0};
    bool have_pat_list = false, have_subj_list = false;

    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--patterns") && i + 1 < argc) patterns_dir = argv[++i];
        else if (!strcmp(argv[i], "--subjects") && i + 1 < argc) subjects_dir = argv[++i];
        else if (!strcmp(argv[i], "--out") && i + 1 < argc) out_dir = argv[++i];
        else if (!strcmp(argv[i], "--rounds") && i + 1 < argc) rounds = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--pattern-list") && i + 1 < argc) { split_csv(argv[++i], &pat_list); have_pat_list = true; }
        else if (!strcmp(argv[i], "--subject-list") && i + 1 < argc) { split_csv(argv[++i], &subj_list); have_subj_list = true; }
        else { fprintf(stderr, "unknown arg %s\n", argv[i]); return 2; }
    }

    if (!have_pat_list) list_dir_branches(patterns_dir, &pat_list);
    if (!have_subj_list) {
        /* default: every .bin under subjects_dir */
        DIR *d = opendir(subjects_dir);
        if (!d) { fprintf(stderr, "cannot open %s\n", subjects_dir); return 1; }
        struct dirent *e;
        while ((e = readdir(d))) {
            size_t l = strlen(e->d_name);
            if (l > 4 && strcmp(e->d_name + l - 4, ".bin") == 0) {
                size_t keep = l - 4;
                if (keep >= sizeof subj_list.names[0]) keep = sizeof subj_list.names[0] - 1;
                memcpy(subj_list.names[subj_list.n], e->d_name, keep);
                subj_list.names[subj_list.n][keep] = 0;
                subj_list.n++;
            }
        }
        closedir(d);
    }

    char path[1024];
    snprintf(path, sizeof path, "%s/identity.tsv", out_dir);
    FILE *f_id = fopen(path, "w");
    snprintf(path, sizeof path, "%s/tries.tsv", out_dir);
    FILE *f_tries = fopen(path, "w");
    snprintf(path, sizeof path, "%s/timing.tsv", out_dir);
    FILE *f_time = fopen(path, "w");
    snprintf(path, sizeof path, "%s/construction.tsv", out_dir);
    FILE *f_cons = fopen(path, "w");
    if (!f_id || !f_tries || !f_time || !f_cons) { fprintf(stderr, "cannot open output files in %s\n", out_dir); return 1; }

    fprintf(f_id, "pattern\tsubject\talgo\tpositions\tmismatches\n");
    fprintf(f_tries, "pattern\tsubject\talgo\tpositions\ttotal_tries\ttries_per_byte\ttotal_verify_bytes\tverify_bytes_per_byte\ttotal_frames\tframes_per_byte\tmax_deferred\n");
    fprintf(f_time, "pattern\tsubject\talgo\trounds\tmedian_ns\tns_per_byte\tns_per_call\tload1\n");
    fprintf(f_cons, "pattern\talgo\tconstruct_ns\ttable_bytes\tdistinct_keys_or_fanout\n");

    for (int pi = 0; pi < pat_list.n; pi++) {
        snprintf(path, sizeof path, "%s/%s.branches", patterns_dir, pat_list.names[pi]);
        BranchSet *bs = bset_load(path);

        double t0, t1;
        t0 = now_ns();
        FirstByteIndex *fb = fb_build(bs);
        t1 = now_ns();
        double fb_cons_ns = t1 - t0;

        t0 = now_ns();
        Trie *tr = trie_build_from(bs);
        t1 = now_ns();
        double trie_cons_ns = t1 - t0;

        t0 = now_ns();
        HashIdx *h2 = hash_build(bs, 2);
        t1 = now_ns();
        double h2_cons_ns = t1 - t0;

        t0 = now_ns();
        HashIdx *h4 = hash_build(bs, 4);
        t1 = now_ns();
        double h4_cons_ns = t1 - t0;

        fprintf(f_cons, "%s\tfirstbyte\t%.1f\t%zu\t-\n", bs->name, fb_cons_ns, fb_bytes(fb));
        fprintf(f_cons, "%s\ttrie\t%.1f\t%zu\t%d\n", bs->name, trie_cons_ns, trie_bytes(tr), tr->max_fanout);
        fprintf(f_cons, "%s\thash2\t%.1f\t%zu\t%d\n", bs->name, h2_cons_ns, hash_bytes(h2), hash_distinct_keys(h2));
        fprintf(f_cons, "%s\thash4\t%.1f\t%zu\t%d\n", bs->name, h4_cons_ns, hash_bytes(h4), hash_distinct_keys(h4));
        fprintf(f_cons, "%s\tvm\t0.0\t0\tshares-trie-c\n", bs->name); /* (e) adds only the subtree_min pass, folded into trie_cons_ns above */
        fflush(f_cons);

        for (int si = 0; si < subj_list.n; si++) {
            snprintf(path, sizeof path, "%s/%s.bin", subjects_dir, subj_list.names[si]);
            Subject *subj = subject_load(path);

            /* ---- correctness sweep (single pass, all positions) ---- */
            long long mism_fb = 0, mism_trie = 0, mism_h2 = 0, mism_h4 = 0, mism_vm = 0;
            long long tries_a = 0, tries_b = 0, tries_c = 0, tries_d2 = 0, tries_d4 = 0, tries_e = 0;
            long long vb_a = 0, vb_b = 0, vb_c = 0, vb_d2 = 0, vb_d4 = 0, vb_e = 0;
            long long frames_e = 0;
            int max_deferred_e = 0;
            int cand[64];

            for (size_t pos = 0; pos < subj->len; pos++) {
                Cost ca = {0,0,0,0}, cb = {0,0,0,0}, cc = {0,0,0,0}, cd2 = {0,0,0,0}, cd4 = {0,0,0,0}, ce = {0,0,0,0};
                Answer aa = serial_try(bs, subj->data, subj->len, pos, &ca);
                Answer ab = fb_dispatch(fb, bs, subj->data, subj->len, pos, &cb);
                int ncand;
                Answer ac = trie_dispatch(tr, bs, subj->data, subj->len, pos, &cc, cand, 64, &ncand);
                Answer ad2 = hash_dispatch(h2, bs, subj->data, subj->len, pos, &cd2);
                Answer ad4 = hash_dispatch(h4, bs, subj->data, subj->len, pos, &cd4);
                Answer ae = trie_dispatch_vm(tr, bs, subj->data, subj->len, pos, &ce);

                bool ok_b = (ab.hit == aa.hit) && (!aa.hit || ab.index == aa.index);
                bool ok_c = (ac.hit == aa.hit) && (!aa.hit || ac.index == aa.index);
                bool ok_d2 = (ad2.hit == aa.hit) && (!aa.hit || ad2.index == aa.index);
                bool ok_d4 = (ad4.hit == aa.hit) && (!aa.hit || ad4.index == aa.index);
                bool ok_e = (ae.hit == aa.hit) && (!aa.hit || ae.index == aa.index);
                if (!ok_b) mism_fb++;
                if (!ok_c) mism_trie++;
                if (!ok_d2) mism_h2++;
                if (!ok_d4) mism_h4++;
                if (!ok_e) mism_vm++;

                tries_a += ca.tries; tries_b += cb.tries; tries_c += cc.tries;
                tries_d2 += cd2.tries; tries_d4 += cd4.tries; tries_e += ce.tries;
                vb_a += ca.verify_bytes; vb_b += cb.verify_bytes; vb_c += cc.verify_bytes;
                vb_d2 += cd2.verify_bytes; vb_d4 += cd4.verify_bytes; vb_e += ce.verify_bytes;
                frames_e += ce.frames;
                if (ce.deferred_seen > max_deferred_e) max_deferred_e = ce.deferred_seen;
            }

            long long npos = (long long)subj->len;
            fprintf(f_id, "%s\t%s\tfirstbyte\t%lld\t%lld\n", bs->name, subj->name, npos, mism_fb);
            fprintf(f_id, "%s\t%s\ttrie\t%lld\t%lld\n", bs->name, subj->name, npos, mism_trie);
            fprintf(f_id, "%s\t%s\thash2\t%lld\t%lld\n", bs->name, subj->name, npos, mism_h2);
            fprintf(f_id, "%s\t%s\thash4\t%lld\t%lld\n", bs->name, subj->name, npos, mism_h4);
            fprintf(f_id, "%s\t%s\tvm\t%lld\t%lld\n", bs->name, subj->name, npos, mism_vm);
            fflush(f_id);

            double npb = npos > 0 ? (double)npos : 1.0;
            fprintf(f_tries, "%s\t%s\tserial\t%lld\t%lld\t%.4f\t%lld\t%.4f\t0\t0.0000\t0\n", bs->name, subj->name, npos, tries_a, tries_a/npb, vb_a, vb_a/npb);
            fprintf(f_tries, "%s\t%s\tfirstbyte\t%lld\t%lld\t%.4f\t%lld\t%.4f\t0\t0.0000\t0\n", bs->name, subj->name, npos, tries_b, tries_b/npb, vb_b, vb_b/npb);
            fprintf(f_tries, "%s\t%s\ttrie\t%lld\t%lld\t%.4f\t%lld\t%.4f\t0\t0.0000\t0\n", bs->name, subj->name, npos, tries_c, tries_c/npb, vb_c, vb_c/npb);
            fprintf(f_tries, "%s\t%s\thash2\t%lld\t%lld\t%.4f\t%lld\t%.4f\t0\t0.0000\t0\n", bs->name, subj->name, npos, tries_d2, tries_d2/npb, vb_d2, vb_d2/npb);
            fprintf(f_tries, "%s\t%s\thash4\t%lld\t%lld\t%.4f\t%lld\t%.4f\t0\t0.0000\t0\n", bs->name, subj->name, npos, tries_d4, tries_d4/npb, vb_d4, vb_d4/npb);
            fprintf(f_tries, "%s\t%s\tvm\t%lld\t%lld\t%.4f\t%lld\t%.4f\t%lld\t%.4f\t%d\n", bs->name, subj->name, npos, tries_e, tries_e/npb, vb_e, vb_e/npb, frames_e, frames_e/npb, max_deferred_e);
            fflush(f_tries);

            /* ---- timing sweeps: `rounds` full passes per algorithm ---- */
            double *rt = malloc((size_t)rounds * sizeof(double));
            const char *algos[6] = {"serial", "firstbyte", "trie", "hash2", "hash4", "vm"};
            for (int alg = 0; alg < 6; alg++) {
                for (int r = 0; r < rounds; r++) {
                    Cost c = {0,0,0,0};
                    double s0 = now_ns();
                    volatile long long sink = 0;
                    for (size_t pos = 0; pos < subj->len; pos++) {
                        Answer a;
                        int ncand;
                        switch (alg) {
                        case 0: a = serial_try(bs, subj->data, subj->len, pos, &c); break;
                        case 1: a = fb_dispatch(fb, bs, subj->data, subj->len, pos, &c); break;
                        case 2: a = trie_dispatch(tr, bs, subj->data, subj->len, pos, &c, cand, 64, &ncand); break;
                        case 3: a = hash_dispatch(h2, bs, subj->data, subj->len, pos, &c); break;
                        case 4: a = hash_dispatch(h4, bs, subj->data, subj->len, pos, &c); break;
                        default: a = trie_dispatch_vm(tr, bs, subj->data, subj->len, pos, &c); break;
                        }
                        sink += a.hit ? a.index : 0;
                    }
                    double s1 = now_ns();
                    (void)sink;
                    rt[r] = s1 - s0;
                }
                double med = median(rt, rounds);
                double load = loadavg1();
                fprintf(f_time, "%s\t%s\t%s\t%d\t%.1f\t%.4f\t%.4f\t%.2f\n",
                        bs->name, subj->name, algos[alg], rounds, med,
                        med / npb, npos > 0 ? med / (double)npos : med, load);
                fflush(f_time);
            }
            free(rt);
            subject_free(subj);
        }

        fb_free(fb);
        trie_free(tr);
        hash_free(h2);
        hash_free(h4);
        bset_free(bs);
        fprintf(stderr, "[altdispatch] done: %s\n", pat_list.names[pi]);
    }

    fclose(f_id); fclose(f_tries); fclose(f_time); fclose(f_cons);
    /* Explicit completion trailer: a run's caller often redirects this
     * binary's stderr to a log and polls it rather than the process table
     * (docs/dev/learnings.md §6's "artifacts, never process greps"); a bare
     * `make run` (no `time` wrapper) leaves no other unambiguous end-of-run
     * marker in that log, which cost a false "is it still running?" check
     * during this study's own R1 re-run. */
    fprintf(stderr, "[altdispatch] ALL DONE: %d pattern(s) x %d subject(s), %d round(s) each\n",
            pat_list.n, subj_list.n, rounds);
    return 0;
}
