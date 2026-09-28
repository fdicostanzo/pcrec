/* main.c -- pcrec-analyze CLI (design.md §10.2's four command forms).
 * Ported 1:1 from scripts/pcrec_analyze.py's argparse wiring + main();
 * see analyze.h's header comment and docs/dev/lanes/findb6_report.md.
 */
#include "analyze.h"
#include "sha256.h"

#include <errno.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    const char *name, *retrieved, *scan, *source, *url, *ref, *license;
    const char *fidelity, *adaptation, *shard, *file;
} ScanArgs;

/* ---------------------------------------------------------------------
 * Command: scan (the default form)
 * --------------------------------------------------------------------- */

static int cmd_scan(const ScanArgs *a)
{
    const char *scan_arg = a->scan ? a->scan : "freq,bigram";
    int req_freq = 0, req_cpfreq = 0, req_bigram = 0;

    {
        char buf[512];
        strncpy(buf, scan_arg, sizeof(buf) - 1);
        buf[sizeof(buf) - 1] = '\0';
        char *p = buf;
        while (*p) {
            while (*p == ',') p++;
            if (!*p) break;
            char *s = p;
            while (*p && *p != ',') p++;
            char save = *p;
            *p = '\0';
            char *tok = s;
            while (*tok == ' ') tok++;
            char *end = tok + strlen(tok);
            while (end > tok && end[-1] == ' ') *--end = '\0';
            if (*tok) {
                Kind k;
                if (pcrec_analyze_kind_from_name(tok, &k) != 0) {
                    fprintf(stderr, "pcrec-analyze: unknown --scan kind '%s'\n", tok);
                    return 2;
                }
                if (k == KIND_FREQ) req_freq = 1;
                else if (k == KIND_CPFREQ) req_cpfreq = 1;
                else req_bigram = 1;
            }
            *p = save;
        }
    }

    long shard_k = 0, shard_n = 0;
    int has_shard = 0;
    if (a->shard) {
        if (sscanf(a->shard, "%ld/%ld", &shard_k, &shard_n) != 2 || shard_n < 1 ||
            shard_k < 1 || shard_k > shard_n) {
            fprintf(stderr, "pcrec-analyze: shard %s out of range\n", a->shard);
            return 2;
        }
        has_shard = 1;
    }

    int is_stdin = (a->file == NULL || !strcmp(a->file, "-"));
    if (has_shard && is_stdin) {
        fprintf(stderr, "pcrec-analyze: --shard cannot be used with stdin (design.md §10.4)\n");
        return 2;
    }

    unsigned char *data;
    size_t data_len;
    if (read_whole_file(a->file, &data, &data_len) != 0) {
        fprintf(stderr, "pcrec-analyze: %s\n", strerror(errno));
        return 2;
    }

    size_t fs, fe, bs, be, cs, ce;
    long long provenance_bytes;
    int have_sha = 0;
    char sha_hex[65];
    if (has_shard) {
        freq_shard_range(data_len, shard_k, shard_n, &fs, &fe);
        bigram_shard_range(data_len, shard_k, shard_n, &bs, &be);
        cpfreq_shard_range(data, data_len, shard_k, shard_n, &cs, &ce);
        provenance_bytes = (long long)(fe - fs); /* the nominal shard size */
    } else {
        fs = bs = cs = 0;
        fe = be = ce = data_len;
        provenance_bytes = (long long)data_len;
        pcrec_analyze_sha256_hex(data, data_len, sha_hex);
        have_sha = 1;
    }

    /* design.md §10.2: classification always reads the code-point-aligned
     * window, so a sharded cut that splits a UTF-8 sequence never reads
     * "bytes" for what is really the middle of valid UTF-8. */
    const char *encoding = classify_encoding(data + cs, ce - cs);

    CpTable cp_scanned;
    cp_table_init(&cp_scanned);
    if (req_cpfreq) {
        size_t bad_pos = 0;
        if (!utf8_decode_strict(data + cs, ce - cs, &cp_scanned, &bad_pos)) {
            fprintf(stderr,
                    "pcrec-analyze: --scan cpfreq requires valid UTF-8 input (R26); "
                    "decode failed at byte offset %zu\n",
                    cs + bad_pos);
            return 2;
        }
    }

    Bundle bd;
    bundle_init(&bd);

    if (req_freq) {
        KindBlock *b = &bd.blocks[KIND_FREQ];
        b->present = 1;
        for (size_t i = fs; i < fe; i++) kind_block_add_freq(b, data[i], 1);
        strncpy(b->encoding, encoding, sizeof(b->encoding) - 1);
    }
    if (req_cpfreq) {
        KindBlock *b = &bd.blocks[KIND_CPFREQ];
        b->present = 1;
        b->cp = cp_scanned; /* ownership transfer */
        strncpy(b->encoding, encoding, sizeof(b->encoding) - 1);
    } else {
        cp_table_free(&cp_scanned);
    }
    if (req_bigram) {
        KindBlock *b = &bd.blocks[KIND_BIGRAM];
        b->present = 1;
        for (size_t i = bs; i + 1 < be; i++) kind_block_add_bigram(b, data[i], data[i + 1], 1);
        strncpy(b->encoding, encoding, sizeof(b->encoding) - 1);
    }

    for (int i = 0; i < KIND__COUNT; i++) {
        KindBlock *b = &bd.blocks[i];
        if (!b->present) continue;
        b->source = strdup(a->source ? a->source : "exemplar");
        if (a->retrieved) b->retrieved = strdup(a->retrieved);
        if (a->url) b->url = strdup(a->url);
        if (a->ref) b->ref = strdup(a->ref);
        if (a->license) b->license = strdup(a->license);
        if (a->fidelity) b->fidelity = strdup(a->fidelity);
        if (a->adaptation) b->adaptation = strdup(a->adaptation);
        b->have_bytes = 1;
        b->bytes_val = provenance_bytes;
        if (have_sha) {
            b->have_sha256 = 1;
            memcpy(b->sha256_val, sha_hex, sizeof(sha_hex));
        }
    }

    render_bundle(stdout, a->name, &bd);
    return 0;
}

/* ---------------------------------------------------------------------
 * Command: --digest-only
 * --------------------------------------------------------------------- */

static int cmd_digest_only(const char *file)
{
    unsigned char *data;
    size_t len;
    if (read_whole_file(file, &data, &len) != 0) {
        fprintf(stderr, "pcrec-analyze: %s\n", strerror(errno));
        return 2;
    }
    char hex[65];
    pcrec_analyze_sha256_hex(data, len, hex);
    printf("bytes %zu\n", len);
    printf("sha256 %s\n", hex);
    return 0;
}

/* ---------------------------------------------------------------------
 * Command: --merge
 * --------------------------------------------------------------------- */

#define MERGE_NFIELDS 7
static const char *MERGE_FIELD_NAMES[MERGE_NFIELDS] = {
    "source", "retrieved", "url", "ref", "license", "fidelity", "adaptation",
};

typedef struct {
    int have;
    const char *encoding_acc;
    char *field[MERGE_NFIELDS];
    int field_conflict[MERGE_NFIELDS];
    long long bytes_sum;
    int any_bytes;
} MergeAcc;

static int cmd_merge(const char *name, char **parts, int nparts, int has_bytes,
                      long long bytes_opt, const char *sha256_opt)
{
    if (nparts == 0) {
        fprintf(stderr, "pcrec-analyze: --merge needs at least one PART.rxt\n");
        return 2;
    }

    Bundle merged;
    bundle_init(&merged);
    MergeAcc acc[KIND__COUNT];
    memset(acc, 0, sizeof(acc));

    for (int pi = 0; pi < nparts; pi++) {
        unsigned char *text;
        size_t tlen;
        if (read_whole_file(parts[pi], &text, &tlen) != 0) {
            fprintf(stderr, "pcrec-analyze: %s: %s\n", parts[pi], strerror(errno));
            return 2;
        }
        Bundle part;
        char *err = NULL;
        if (parse_bundle((const char *)text, tlen, &part, &err) != 0) {
            fprintf(stderr, "pcrec-analyze: %s: %s\n", parts[pi], err ? err : "parse error");
            return 2;
        }
        for (int k = 0; k < KIND__COUNT; k++) {
            KindBlock *pk = &part.blocks[k];
            if (!pk->present) continue;
            acc[k].have = 1;
            kind_block_merge_from(&merged.blocks[k], pk);

            const char *encv = (pk->encoding[0]) ? pk->encoding : NULL;
            acc[k].encoding_acc = combine_encoding(acc[k].encoding_acc, encv);

            char *vals[MERGE_NFIELDS] = { pk->source, pk->retrieved, pk->url, pk->ref,
                                           pk->license, pk->fidelity, pk->adaptation };
            for (int f = 0; f < MERGE_NFIELDS; f++) {
                if (!vals[f]) continue;
                if (!acc[k].field[f]) acc[k].field[f] = strdup(vals[f]);
                else if (strcmp(acc[k].field[f], vals[f]) != 0) acc[k].field_conflict[f] = 1;
            }
            if (pk->have_bytes) { acc[k].bytes_sum += pk->bytes_val; acc[k].any_bytes = 1; }
        }
    }

    long long nominal_bytes_total = 0;
    for (int k = 0; k < KIND__COUNT; k++) {
        if (!acc[k].have) continue;
        for (int f = 0; f < MERGE_NFIELDS; f++) {
            if (acc[k].field_conflict[f]) {
                fprintf(stderr,
                        "pcrec-analyze: --merge: parts disagree on provenance '%s' for kind '%s'\n",
                        MERGE_FIELD_NAMES[f], pcrec_analyze_kind_name((Kind)k));
                return 2;
            }
        }
        KindBlock *b = &merged.blocks[k];
        b->source = acc[k].field[0];
        b->retrieved = acc[k].field[1];
        b->url = acc[k].field[2];
        b->ref = acc[k].field[3];
        b->license = acc[k].field[4];
        b->fidelity = acc[k].field[5];
        b->adaptation = acc[k].field[6];
        strncpy(b->encoding, acc[k].encoding_acc ? acc[k].encoding_acc : "", sizeof(b->encoding) - 1);

        long long kind_bytes = acc[k].any_bytes ? acc[k].bytes_sum : 0;
        if (kind_bytes) { b->have_bytes = 1; b->bytes_val = kind_bytes; }
        if (kind_bytes > nominal_bytes_total) nominal_bytes_total = kind_bytes;
    }

    if (has_bytes) {
        if (nominal_bytes_total != 0 && nominal_bytes_total != bytes_opt) {
            fprintf(stderr,
                    "pcrec-analyze: --merge: shard byte total %lld != --bytes %lld "
                    "(a shard boundary or overlap is wrong)\n",
                    nominal_bytes_total, bytes_opt);
            return 2;
        }
        for (int k = 0; k < KIND__COUNT; k++) {
            if (!merged.blocks[k].present) continue;
            merged.blocks[k].have_bytes = 1;
            merged.blocks[k].bytes_val = bytes_opt;
        }
    }
    if (sha256_opt) {
        for (int k = 0; k < KIND__COUNT; k++) {
            if (!merged.blocks[k].present) continue;
            merged.blocks[k].have_sha256 = 1;
            strncpy(merged.blocks[k].sha256_val, sha256_opt, 64);
            merged.blocks[k].sha256_val[64] = '\0';
        }
    }

    render_bundle(stdout, name, &merged);
    return 0;
}

/* ---------------------------------------------------------------------
 * Command: --check
 * --------------------------------------------------------------------- */

static int cmd_check(const char *bundle_path, const char *file)
{
    FILE *probe = fopen(bundle_path, "rb");
    if (!probe) {
        fprintf(stderr, "pcrec-analyze: --check: %s not found\n", bundle_path);
        return 2;
    }
    fclose(probe);

    unsigned char *btext;
    size_t blen;
    if (read_whole_file(bundle_path, &btext, &blen) != 0) {
        fprintf(stderr, "pcrec-analyze: --check: cannot read %s\n", bundle_path);
        return 2;
    }
    Bundle bd;
    char *err = NULL;
    if (parse_bundle((const char *)btext, blen, &bd, &err) != 0) {
        fprintf(stderr, "pcrec-analyze: --check: %s\n", err ? err : "parse error");
        return 2;
    }

    /* [r2 A-5]'s analyzer-level analogue: a NAMED, missing FILE fails
     * CLOSED, loudly. Stdin ("-"/omitted) is always available. */
    if (file != NULL && strcmp(file, "-") != 0) {
        FILE *sf = fopen(file, "rb");
        if (!sf) {
            fprintf(stderr,
                    "pcrec-analyze: --check: source '%s' not found -- cannot recount "
                    "(manifest-only sources fail CLOSED, never skip)\n",
                    file);
            return 2;
        }
        fclose(sf);
    }

    unsigned char *data;
    size_t data_len;
    if (read_whole_file(file, &data, &data_len) != 0) {
        fprintf(stderr, "pcrec-analyze: --check: %s\n", strerror(errno));
        return 2;
    }

    int nmismatch = 0;
    for (int i = 0; i < KIND__COUNT; i++) {
        KindBlock *pk = &bd.blocks[i];
        if (!pk->present) continue;
        KindBlock recount;
        kind_block_init(&recount, (Kind)i);
        int rows_ok;

        if (i == KIND_FREQ) {
            for (size_t j = 0; j < data_len; j++) kind_block_add_freq(&recount, data[j], 1);
            rows_ok = kind_block_rows_equal(&recount, pk);
        } else if (i == KIND_BIGRAM) {
            for (size_t j = 0; j + 1 < data_len; j++) kind_block_add_bigram(&recount, data[j], data[j + 1], 1);
            rows_ok = kind_block_rows_equal(&recount, pk);
        } else {
            if (!utf8_decode_strict(data, data_len, &recount.cp, NULL)) {
                fprintf(stderr, "pcrec-analyze: --check FAILED: cpfreq: source no longer decodes as UTF-8\n");
                nmismatch++;
                rows_ok = 1; /* already reported; do not double-report the rows-mismatch */
            } else {
                rows_ok = kind_block_rows_equal(&recount, pk);
            }
        }
        if (!rows_ok) {
            fprintf(stderr, "pcrec-analyze: --check FAILED: %s: recount does not match the bundle's rows\n",
                    pcrec_analyze_kind_name((Kind)i));
            nmismatch++;
        }
        if (pk->have_bytes && pk->bytes_val != (long long)data_len) {
            fprintf(stderr, "pcrec-analyze: --check FAILED: %s: provenance bytes %lld != source length %zu (drift)\n",
                    pcrec_analyze_kind_name((Kind)i), pk->bytes_val, data_len);
            nmismatch++;
        }
        if (pk->have_sha256) {
            char hex[65];
            pcrec_analyze_sha256_hex(data, data_len, hex);
            if (strcmp(hex, pk->sha256_val) != 0) {
                fprintf(stderr, "pcrec-analyze: --check FAILED: %s: provenance sha256 %s != recomputed %s (drift)\n",
                        pcrec_analyze_kind_name((Kind)i), pk->sha256_val, hex);
                nmismatch++;
            }
        }
    }

    if (nmismatch > 0) return 1;
    printf("pcrec-analyze: --check OK: '%s' reproduces its rows from %s\n", bd.name, file ? file : "-");
    return 0;
}

/* ---------------------------------------------------------------------
 * argv wiring
 * --------------------------------------------------------------------- */

int main(int argc, char **argv)
{
    int opt_merge = 0, opt_digest_only = 0;
    const char *opt_check = NULL;
    const char *opt_name = NULL, *opt_retrieved = NULL, *opt_scan = NULL;
    const char *opt_source = NULL, *opt_url = NULL, *opt_ref = NULL, *opt_license = NULL;
    const char *opt_fidelity = NULL, *opt_adaptation = NULL, *opt_shard = NULL;
    int has_bytes = 0;
    long long opt_bytes = 0;
    const char *opt_sha256 = NULL;

    char **pos = malloc(sizeof(char *) * (size_t)(argc + 1));
    int npos = 0;

    for (int i = 1; i < argc; i++) {
        const char *a = argv[i];
#define NEXTVAL() (i + 1 < argc ? argv[++i] : NULL)
        if (!strcmp(a, "--merge")) opt_merge = 1;
        else if (!strcmp(a, "--digest-only")) opt_digest_only = 1;
        else if (!strcmp(a, "--check")) {
            const char *v = NEXTVAL();
            if (!v) { fprintf(stderr, "pcrec-analyze: --check requires a value\n"); return 2; }
            opt_check = v;
        } else if (!strcmp(a, "--name")) opt_name = NEXTVAL();
        else if (!strcmp(a, "--retrieved")) opt_retrieved = NEXTVAL();
        else if (!strcmp(a, "--scan")) opt_scan = NEXTVAL();
        else if (!strcmp(a, "--source")) opt_source = NEXTVAL();
        else if (!strcmp(a, "--url")) opt_url = NEXTVAL();
        else if (!strcmp(a, "--ref")) opt_ref = NEXTVAL();
        else if (!strcmp(a, "--license")) opt_license = NEXTVAL();
        else if (!strcmp(a, "--fidelity")) {
            const char *v = NEXTVAL();
            if (v && strcmp(v, "verbatim") && strcmp(v, "adapted") && strcmp(v, "synthesized")) {
                fprintf(stderr,
                        "pcrec-analyze: --fidelity: invalid choice '%s' "
                        "(choose from verbatim, adapted, synthesized)\n", v);
                return 2;
            }
            opt_fidelity = v;
        } else if (!strcmp(a, "--adaptation")) opt_adaptation = NEXTVAL();
        else if (!strcmp(a, "--shard")) opt_shard = NEXTVAL();
        else if (!strcmp(a, "--bytes")) {
            const char *v = NEXTVAL();
            if (v) { has_bytes = 1; opt_bytes = strtoll(v, NULL, 10); }
        } else if (!strcmp(a, "--sha256")) opt_sha256 = NEXTVAL();
        else if (a[0] == '-' && a[1] == '-') {
            fprintf(stderr, "pcrec-analyze: unrecognized argument: %s\n", a);
            return 2;
        } else {
            pos[npos++] = (char *)a;
        }
#undef NEXTVAL
    }

    if (opt_merge) {
        if (!opt_name) { fprintf(stderr, "pcrec-analyze: --merge requires --name\n"); return 2; }
        return cmd_merge(opt_name, pos, npos, has_bytes, opt_bytes, opt_sha256);
    }

    if (npos > 1) {
        fprintf(stderr, "pcrec-analyze: unexpected extra arguments:");
        for (int i = 1; i < npos; i++) fprintf(stderr, " %s", pos[i]);
        fprintf(stderr, "\n");
        return 2;
    }
    const char *file = npos ? pos[0] : NULL;

    if (opt_digest_only) return cmd_digest_only(file);
    if (opt_check) return cmd_check(opt_check, file);

    if (!opt_name || !opt_retrieved) {
        fprintf(stderr, "pcrec-analyze: the scan form requires --name and --retrieved\n");
        return 2;
    }

    ScanArgs sa = {
        .name = opt_name, .retrieved = opt_retrieved, .scan = opt_scan,
        .source = opt_source, .url = opt_url, .ref = opt_ref, .license = opt_license,
        .fidelity = opt_fidelity, .adaptation = opt_adaptation, .shard = opt_shard,
        .file = file,
    };
    return cmd_scan(&sa);
}
