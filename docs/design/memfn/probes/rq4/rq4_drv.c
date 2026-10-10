/* memfn RQ-4 (lane rq4h): the tier-U timing driver for the vrun KB question.
 *
 * Question (docs/dev/lanes/rankuse_report.md §6; integration.md §R4.9.5):
 * at each cell, does DEFAULT (-fmemfn-simd: KA AND KB) differ from KB-DENY
 * (--memfn=no-vrun-kb: KA alone) past the null band, and does SIMD-on differ
 * from OFF (-fno-memfn-simd, glibc memchr inside), in which regime?
 *
 * This file is ONE side of a binary: it is linked against ONE artifact
 * pcrec emitted (`-p rx`), compiled at the same -O2 -march as the artifact,
 * and it times that artifact's PUBLIC entry `rx_search` (match_api.md §3.1)
 * and the §3.1.3 find-all loop over it. No FUNC is copied: every arm is its
 * own binary (§R4.9.5 item 3). rq4.py builds the binaries, interleaves the
 * arms per launch and writes raw.tsv; rq4_table.py reads it.
 *
 *   rq4_drv --witness=W --subject=SPEC --regime=R [--inject=V,M,DEN]
 *           [--min-ms=50] [--seed=N]
 *
 * SUBJECTS (every byte a function of SPEC, the witness and the seed, so the
 * three arms of a cell time the same bytes; each row prints the subject's
 * FNV-1a hash and the find-all answer, which rq4_table.py compares across
 * arms):
 *   tail:N        N bytes of filler, the witness once, at its END (the scan
 *                 crosses the whole subject: the hit-sparse extreme)
 *   rand:N:MEAN   filler, the witness planted at gaps drawn from
 *                 [MEAN/2, 3*MEAN/2) (hit-sparse MEAN 16384, hit-dense 256)
 *   space:N:S     filler, the witness planted every S bytes from 0 (the
 *                 hit-spacing ladder; S < witness length + 1 is refused)
 *   file:PATH     a bench subject, read as is (R-1's cap/syn t-64k/t-1m)
 *   short:PATH    a list of subjects, <u32 little-endian len><bytes>... (the
 *                 capability set's 75 short subjects, subjects_r4b.py)
 * The filler is English-like words (the list below), with every byte the
 * pattern would match killed first: each match's last byte becomes '#'
 * until rx_search finds none (at most 64 passes, else exit 3). --inject
 * then sets a 1/DEN share of filler bytes to V | (~M & random): KA's
 * scanned byte (V under mask M, read from the artifact by rq4.py), so KA
 * is COMMON and the run stays rare (the KB cell), sanitized again after.
 *
 * REGIMES (ns; min of REPEATS loops >= min-ms each, spread = max/min - 1):
 *   gate    one rx_search from 0 on each subject in the set (ns per call)
 *   sweep   the §3.1.3 find-all loop over the subject (ns per find-all)
 *   pcL     one rx_search from 0 on each of up to 256 consecutive L-byte
 *           chunks of the subject (the per-call span ladder; ns per call)
 *   check   no timing: prints the answer row only (rq4.py's check stage)
 *
 * Output: one machine-read line,
 *   R <regime> <subject> <ns> <spread%> <hits> <fnv> <possum> <calls>
 * hits/possum are the find-all answer over the WHOLE subject set (count of
 * matches, sum of start*31+end), the same for every regime of a subject.
 */
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/* the artifact's public entries (match_api.md §3.1, §3.1.1), prefix rx */
int rx_search(const unsigned char *subject, size_t subject_length, size_t search_from,
              ptrdiff_t (*capture_spans)[2]);
size_t rx_next_pos(const unsigned char *s, size_t n, size_t pos);

#define REPEATS 3      /* UNMEASURED DEFAULT: R-1's 3 loops per launch (§R4.9.5 item 8) */
#define MAX_SUBJ 256   /* the pc ladder's chunk cap, and the short list's (tb_r4b.c's) */

static uint64_t g_rng;
static uint64_t rng(void) /* splitmix64 */
{
    uint64_t z = (g_rng += 0x9E3779B97F4A7C15ull);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
    return z ^ (z >> 31);
}
static uint64_t fnv(const uint8_t *s, size_t n, uint64_t h)
{
    for (size_t i = 0; i < n; i++) h = (h ^ s[i]) * 0x100000001B3ull;
    return h;
}

/* ---- filler ---------------------------------------------------------------- */

static const char *const words[] = {
    "the", "of", "and", "to", "in", "is", "that", "it", "was", "for", "on", "are",
    "with", "as", "his", "they", "be", "at", "one", "have", "this", "from", "or",
    "had", "by", "word", "but", "what", "some", "we", "can", "out", "other", "were",
    "all", "there", "when", "up", "use", "your", "how", "said", "an", "each",
    "which", "she", "do", "their", "time", "if", "will", "way", "about", "many",
    "then", "them", "write", "would", "like", "so", "these", "her", "long", "make",
    "thing", "see", "him", "two", "has", "look", "more", "day", "could", "go",
    "come", "did", "number", "sound", "no", "most", "people", "my", "over", "know",
    "water", "than", "call", "first", "who", "may", "down", "side", "been", "now",
    "find", "head", "stand", "own", "page", "should", "country", "found", "answer",
    "school", "grow", "study", "still", "learn", "plant", "cover", "food", "sun",
    "four", "between", "state", "keep", "eye", "never", "last", "let", "thought",
    "city", "tree", "cross", "farm", "hard", "start", "might", "story", "saw",
    "far", "sea", "draw", "left", "late", "run", "while", "press", "close", "night",
    "real", "life", "few", "north", "open", "seem", "together", "next", "white",
    "children", "begin", "got", "walk", "example", "ease", "paper", "group",
    "always", "music", "those", "both", "mark", "often", "letter", "until", "mile",
    "river", "car", "feet", "care", "second", "book", "carry", "took", "science",
    "eat", "room", "friend", "began", "idea", "fish", "mountain", "stop", "once",
    "base", "hear", "horse", "cut", "sure", "watch", "color", "face", "wood",
    "main", "enough", "plain", "girl", "usual", "young", "ready", "above", "ever",
    "red", "list", "though", "feel", "talk", "bird", "soon", "body", "dog", "family",
    "direct", "pose", "leave", "song", "measure", "door", "product", "black",
    "short", "numeral", "class", "wind", "question", "happen", "complete", "ship",
    "area", "half", "rock", "order", "fire", "south", "problem", "piece", "told",
    "knew", "pass", "since", "top", "whole", "king", "space", "heard", "best",
    "hour", "better", "true", "during", "hundred", "five", "remember", "step",
    "early", "hold", "west", "ground", "interest", "reach", "fast", "verb", "sing",
    "listen", "six", "table", "travel", "less", "morning", "ten", "simple",
    "several", "vowel", "toward", "war", "lay", "against", "pattern", "slow",
    "center", "love", "person", "money", "serve", "appear", "road", "map", "rain",
    "rule", "govern", "pull", "cold", "notice", "voice", "unit", "power", "town",
    "fine", "certain", "fly", "fall", "lead", "cry", "dark", "machine", "note",
    "wait", "plan", "figure", "star", "box", "noun", "field", "rest", "correct",
    "able", "pound", "done", "beauty", "drive", "stood", "contain", "front",
    "teach", "week", "final", "gave", "green", "oh", "quick", "develop", "ocean",
    "warm", "free", "minute", "strong", "special", "mind", "behind", "clear",
    "tail", "produce", "fact", "street", "inch", "multiply", "nothing", "course",
    "stay", "wheel", "full", "force", "blue", "object", "decide", "surface",
    "deep", "moon", "island", "foot", "system", "busy", "test", "record", "boat",
    "common", "gold", "possible", "plane", "stead", "dry", "wonder", "laugh",
    "thousand", "ago", "ran", "check", "game", "shape", "equate", "hot", "miss",
    "brought", "heat", "snow", "tire", "bring", "yes", "distant", "fill", "east",
    "paint", "language", "among", "zone", "quiet", "size", "jazz", "quote",
};
#define NWORDS (sizeof words / sizeof words[0])

static void filler(uint8_t *s, size_t n)
{
    size_t i = 0, col = 0;
    while (i < n) {
        const char *w = words[rng() % NWORDS];
        uint64_t r = rng();
        for (const char *c = w; *c && i < n; c++, col++)
            s[i++] = (uint8_t)((r & 15) == 0 && c == w ? *c - 32 : *c); /* 1/16 capitalized */
        if (i >= n) break;
        if (col > 70) s[i++] = '\n', col = 0;
        else if ((r >> 8) % 12 == 0) { s[i++] = (r >> 12) & 1 ? ',' : '.'; col++; }
        else s[i++] = ' ', col++;
    }
}

/* kill every match in s[0..n): the last byte of each becomes '#', until
 * rx_search finds none; the witnesses are planted after, never killed */
static void sanitize(uint8_t *s, size_t n)
{
    ptrdiff_t caps[64][2];
    for (int pass = 0; pass < 64; pass++) {
        int found = 0;
        size_t p = 0;
        while (p <= n && rx_search(s, n, p, caps) == 1) {
            size_t a = (size_t)caps[0][0], e = (size_t)caps[0][1];
            size_t k = e > a ? e - 1 : a;
            if (k >= n) break;
            s[k] = s[k] == '#' ? '~' : '#';
            found = 1;
            p = a + 1;
        }
        if (!found) return;
    }
    fprintf(stderr, "rq4_drv: SANITIZE-FAIL: matches remain after 64 passes\n");
    exit(3);
}

/* ---- subjects ---------------------------------------------------------------- */

static const uint8_t *g_s[MAX_SUBJ];
static size_t g_n[MAX_SUBJ];
static int g_ns;

static uint8_t *slurp(const char *path, size_t *n)
{
    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); exit(2); }
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    uint8_t *b = malloc((size_t)len + 1);
    if (!b || fread(b, 1, (size_t)len, f) != (size_t)len) { perror(path); exit(2); }
    fclose(f);
    *n = (size_t)len;
    return b;
}

static void build_subject(const char *spec, const char *w, int inj_v, int inj_m, unsigned inj_den)
{
    size_t wl = strlen(w), n = 0, a = 0;
    char kind[16] = "";
    sscanf(spec, "%15[a-z]:", kind);
    const char *arg = strchr(spec, ':') ? strchr(spec, ':') + 1 : "";
    if (!strcmp(kind, "file")) {
        g_s[0] = slurp(arg, &g_n[0]);
        g_ns = 1;
        return;
    }
    if (!strcmp(kind, "short")) {
        size_t sl;
        uint8_t *sb = slurp(arg, &sl);
        for (size_t o = 0; o + 4 <= sl && g_ns < MAX_SUBJ;) {
            uint32_t len;
            memcpy(&len, sb + o, 4);
            uint8_t *cp = malloc(len + 1u); /* each in its own allocation, exact */
            memcpy(cp, sb + o + 4, len);
            g_s[g_ns] = cp, g_n[g_ns++] = len;
            o += 4 + (size_t)len;
        }
        free(sb);
        return;
    }
    if (sscanf(arg, "%zu:%zu", &n, &a) < 1 || n < wl) {
        fprintf(stderr, "rq4_drv: bad subject %s\n", spec);
        exit(2);
    }
    g_rng = fnv((const uint8_t *)spec, strlen(spec), fnv((const uint8_t *)w, wl, 0xCBF29CE484222325ull));
    uint8_t *s = malloc(n + 1);
    filler(s, n);
    sanitize(s, n);
    if (inj_den) {
        for (size_t i = 0; i < n; i++)
            if (rng() % inj_den == 0) s[i] = (uint8_t)(inj_v | (~inj_m & (int)(rng() & 0xFF)));
        sanitize(s, n);
    }
    if (!strcmp(kind, "tail"))
        memcpy(s + n - wl, w, wl);
    else if (!strcmp(kind, "rand") && a >= 2) {
        for (size_t p = a / 2 + rng() % a; p + wl <= n; p += wl + a / 2 + rng() % a)
            memcpy(s + p, w, wl);
    } else if (!strcmp(kind, "space") && a > wl) {
        for (size_t p = 0; p + wl <= n; p += a) memcpy(s + p, w, wl);
    } else {
        fprintf(stderr, "rq4_drv: bad subject %s (witness %zu B)\n", spec, wl);
        exit(2);
    }
    g_s[0] = s, g_n[0] = n, g_ns = 1;
}

/* ---- the two loops ------------------------------------------------------------ */

static long g_hits;
static double g_possum;

static size_t sweep1(const uint8_t *s, size_t n, int count)
{
    ptrdiff_t caps[64][2];
    size_t p = 0, k = 0;
    while (p <= n) {
        if (rx_search(s, n, p, caps) != 1) break;
        k++;
        if (count) g_possum += (double)caps[0][0] * 31 + (double)caps[0][1];
        p = caps[0][1] > caps[0][0] ? rx_next_pos(s, n, (size_t)caps[0][1] - 1)
                                    : rx_next_pos(s, n, (size_t)caps[0][0]);
    }
    return k;
}

static volatile size_t g_sink;
static const uint8_t *const *g_ts;
static const size_t *g_tn;
static int g_tm;

static double now_ns(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}
static double t_gate(long reps)
{
    size_t acc = 0;
    double t0 = now_ns();
    for (long r = 0; r < reps; r++)
        for (int i = 0; i < g_tm; i++) acc += (size_t)rx_search(g_ts[i], g_tn[i], 0, NULL);
    double t = now_ns() - t0;
    g_sink += acc;
    return t;
}
static double t_sweep(long reps)
{
    size_t acc = 0;
    double t0 = now_ns();
    for (long r = 0; r < reps; r++)
        for (int i = 0; i < g_tm; i++) acc += sweep1(g_ts[i], g_tn[i], 0);
    double t = now_ns() - t0;
    g_sink += acc;
    return t;
}

/* calibrate to >= min loop, then REPEATS timed runs: min/max ns per rep
 * (vec.h's tmeasure, D144 addendum 1) */
static void tmeasure(double (*f)(long), double min_ns, double *lo, double *hi)
{
    long reps = 1;
    double t;
    while ((t = f(reps)) < min_ns)
        reps = (long)(reps * (t > 1e5 ? 1.2 * min_ns / t : 16.0)) + 1;
    *lo = 1e300, *hi = 0;
    for (int k = 0; k < REPEATS; k++) {
        double x = f(reps) / reps;
        if (x < *lo) *lo = x;
        if (x > *hi) *hi = x;
    }
}

int main(int argc, char **argv)
{
    const char *w = NULL, *spec = NULL, *regime = NULL;
    double min_ms = 50;
    int inj_v = 0, inj_m = 0xFF;
    unsigned inj_den = 0;
    for (int i = 1; i < argc; i++) {
        if (!strncmp(argv[i], "--witness=", 10)) w = argv[i] + 10;
        else if (!strncmp(argv[i], "--subject=", 10)) spec = argv[i] + 10;
        else if (!strncmp(argv[i], "--regime=", 9)) regime = argv[i] + 9;
        else if (!strncmp(argv[i], "--min-ms=", 9)) min_ms = atof(argv[i] + 9);
        else if (!strncmp(argv[i], "--inject=", 9)) {
            if (sscanf(argv[i] + 9, "%i,%i,%u", &inj_v, &inj_m, &inj_den) != 3) {
                fprintf(stderr, "rq4_drv: bad %s\n", argv[i]);
                return 2;
            }
        } else {
            fprintf(stderr, "rq4_drv: unknown argument %s\n", argv[i]);
            return 2;
        }
    }
    if (!w || !spec || !regime) {
        fprintf(stderr, "usage: rq4_drv --witness=W --subject=SPEC --regime=gate|sweep|pcL|check "
                        "[--inject=V,M,DEN] [--min-ms=MS]\n");
        return 2;
    }
    build_subject(spec, w, inj_v, inj_m, inj_den);
    uint64_t h = 0xCBF29CE484222325ull;
    for (int i = 0; i < g_ns; i++) {
        h = fnv(g_s[i], g_n[i], h);
        g_hits += (long)sweep1(g_s[i], g_n[i], 1);
    }

    static const uint8_t *cs[MAX_SUBJ];
    static size_t cn[MAX_SUBJ];
    double (*f)(long) = t_gate;
    size_t chunk = 0;
    g_ts = g_s, g_tn = g_n, g_tm = g_ns;
    if (!strcmp(regime, "sweep")) f = t_sweep;
    else if (sscanf(regime, "pc%zu", &chunk) == 1 && chunk) {
        int m = 0;
        for (size_t o = 0; o + chunk <= g_n[0] && m < MAX_SUBJ; o += chunk)
            cs[m] = g_s[0] + o, cn[m++] = chunk;
        g_ts = cs, g_tn = cn, g_tm = m;
    } else if (strcmp(regime, "gate") && strcmp(regime, "check")) {
        fprintf(stderr, "rq4_drv: unknown regime %s\n", regime);
        return 2;
    }
    double lo = 0, hi = 0;
    if (strcmp(regime, "check")) tmeasure(f, min_ms * 1e6, &lo, &hi);
    int per = f == t_sweep ? 1 : g_tm;
    printf("R\t%s\t%s\t%.3f\t%.1f\t%ld\t%016llx\t%.0f\t%d\n", regime, spec, lo / per,
           lo > 0 ? 100 * (hi / lo - 1) : 0.0, g_hits, (unsigned long long)h, g_possum, per);
    return 0;
}
