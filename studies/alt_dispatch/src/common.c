#include "common.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <time.h>

double now_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e9 + (double)ts.tv_nsec;
}

static char *basename_noext(const char *path, char *out, size_t outsz)
{
    const char *slash = strrchr(path, '/');
    const char *base = slash ? slash + 1 : path;
    size_t n = strlen(base);
    const char *dot = strrchr(base, '.');
    size_t keep = dot ? (size_t)(dot - base) : n;
    if (keep >= outsz) keep = outsz - 1;
    memcpy(out, base, keep);
    out[keep] = 0;
    return out;
}

BranchSet *bset_load(const char *path)
{
    FILE *f = fopen(path, "r");
    if (!f) { fprintf(stderr, "bset_load: cannot open %s\n", path); exit(1); }

    char mode[16] = "literal";
    char line[4096];
    /* first pass: header + count words */
    long words_start = 0;
    int nwords = 0;
    while (fgets(line, sizeof line, f)) {
        if (line[0] == '#') {
            if (strncmp(line, "# MODE ", 7) == 0) {
                sscanf(line + 7, "%15s", mode);
            }
            words_start = ftell(f);
            continue;
        }
        size_t l = strlen(line);
        if (l == 0 || line[l - 1] != '\n') { /* last line w/o trailing NL */ }
        /* trim */
        while (l > 0 && (line[l-1] == '\n' || line[l-1] == '\r')) line[--l] = 0;
        if (l == 0) continue;
        nwords++;
    }

    BranchSet *bs = calloc(1, sizeof *bs);
    bs->br = calloc((size_t)nwords, sizeof(Branch));
    bs->n = nwords;
    basename_noext(path, bs->name, sizeof bs->name);
    snprintf(bs->mode, sizeof bs->mode, "%s", mode);
    bool ci = strcmp(mode, "ci") == 0;

    fseek(f, words_start, SEEK_SET);
    int idx = 0;
    while (fgets(line, sizeof line, f)) {
        if (line[0] == '#') continue;
        size_t l = strlen(line);
        while (l > 0 && (line[l-1] == '\n' || line[l-1] == '\r')) line[--l] = 0;
        if (l == 0) continue;
        Branch *b = &bs->br[idx];
        b->len = (int)l;
        b->index = idx;
        b->seq = calloc(l, sizeof(ByteSet));
        for (size_t k = 0; k < l; k++) {
            unsigned char c = (unsigned char)line[k];
            bs_clear(&b->seq[k]);
            bs_add(&b->seq[k], c);
            if (ci && isalpha(c)) bs_add(&b->seq[k], (unsigned char)(islower(c) ? toupper(c) : tolower(c)));
        }
        idx++;
    }
    fclose(f);
    return bs;
}

void bset_free(BranchSet *bs)
{
    if (!bs) return;
    for (int i = 0; i < bs->n; i++) free(bs->br[i].seq);
    free(bs->br);
    free(bs);
}

Subject *subject_load(const char *path)
{
    FILE *f = fopen(path, "rb");
    if (!f) { fprintf(stderr, "subject_load: cannot open %s\n", path); exit(1); }
    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    fseek(f, 0, SEEK_SET);
    Subject *s = calloc(1, sizeof *s);
    s->data = malloc((size_t)sz);
    s->len = (size_t)fread(s->data, 1, (size_t)sz, f);
    fclose(f);
    basename_noext(path, s->name, sizeof s->name);
    return s;
}

void subject_free(Subject *s)
{
    if (!s) return;
    free(s->data);
    free(s);
}
