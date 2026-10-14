/* grid1: the subject loader shared by gdrv.c (timed) and gchk.c (checker,
 * counters). A subject argument is one of
 *   a regular file        one buffer (slot25c drv.c's case);
 *   a directory           every regular file in it, in name order (alphasort):
 *                         the STREAMED subject, one buffer per file;
 *   a file named *.list   a manifest: one path per line (relative paths are
 *                         taken from the manifest's own directory), blank
 *                         lines and lines starting with '#' ignored.
 * Every buffer gets its own posix_memalign(64) block and starts OFF bytes
 * past it (env GRID_OFF, default 0), so the subject's start alignment is
 * controlled (slot25c's malloc gave 16-aligned heap or page+16 mmap). The
 * block holds exactly OFF + n bytes (+1 so n = 0 is an allocation), so a read
 * past s + n leaves the allocation under ASan. */
#ifndef GRID_GLOAD_H
#define GRID_GLOAD_H
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

struct gbuf { unsigned char *p; size_t n; void *blk; };
static struct gbuf *gbufs;
static size_t gnbuf, gcap;

static size_t goff(void)
{
    const char *e = getenv("GRID_OFF");
    return e && *e ? strtoul(e, 0, 10) : 0;
}

static void gadd(const char *path, size_t off)
{
    FILE *f = fopen(path, "rb");
    if (!f) { fprintf(stderr, "grid: cannot open %s\n", path); exit(2); }
    fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
    void *blk = NULL;
    if (posix_memalign(&blk, 64, off + (size_t)n + 1)) exit(3);
    unsigned char *p = (unsigned char *)blk + off;
    if (fread(p, 1, (size_t)n, f) != (size_t)n) { fprintf(stderr, "grid: short read %s\n", path); exit(2); }
    fclose(f);
    if (gnbuf == gcap) { gcap = gcap ? 2 * gcap : 16; gbufs = realloc(gbufs, gcap * sizeof *gbufs); if (!gbufs) exit(3); }
    gbufs[gnbuf].p = p; gbufs[gnbuf].n = (size_t)n; gbufs[gnbuf].blk = blk; gnbuf++;
}

static int gregular(const struct dirent *d) { return d->d_name[0] != '.'; }

static void gload(const char *arg, size_t off)
{
    struct stat st;
    if (stat(arg, &st)) { fprintf(stderr, "grid: no subject %s\n", arg); exit(2); }
    char path[4096];
    if (S_ISDIR(st.st_mode)) {
        struct dirent **ents;
        int k = scandir(arg, &ents, gregular, alphasort);
        if (k < 0) exit(2);
        for (int i = 0; i < k; i++) {
            if (snprintf(path, sizeof path, "%s/%s", arg, ents[i]->d_name) >= (int)sizeof path) exit(2);
            struct stat es;
            if (!stat(path, &es) && S_ISREG(es.st_mode)) gadd(path, off);
            free(ents[i]);
        }
        free(ents);
    } else if (strlen(arg) > 5 && !strcmp(arg + strlen(arg) - 5, ".list")) {
        FILE *m = fopen(arg, "r");
        if (!m) exit(2);
        char dir[4096], line[4096];
        if (snprintf(dir, sizeof dir, "%s", arg) >= (int)sizeof dir) exit(2);
        char *sl = strrchr(dir, '/');
        if (sl) *sl = 0; else strcpy(dir, ".");
        while (fgets(line, sizeof line, m)) {
            line[strcspn(line, "\r\n")] = 0;
            if (!line[0] || line[0] == '#') continue;
            if (line[0] == '/') gadd(line, off);
            else { if (snprintf(path, sizeof path, "%s/%s", dir, line) >= (int)sizeof path) exit(2); gadd(path, off); }
        }
        fclose(m);
    } else gadd(arg, off);
    if (!gnbuf) { fprintf(stderr, "grid: subject %s holds no buffer\n", arg); exit(2); }
}

/* the answer fold over buffers: one buffer gives drv.c's own (matches, hash) */
#define GRID_FOLD(H, h) ((H) = (H) * 1099511628211ul + (h))
#endif
