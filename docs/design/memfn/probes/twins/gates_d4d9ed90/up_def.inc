static inline uint32_t rx_w4(const void *p) { uint32_t w; memcpy(&w, p, 4); return w; }

static inline size_t rx_reqrun(const unsigned char *subject, size_t n, size_t pos)
{
    size_t ha = 0, hb = 0;
    int fresh = 1;
    while (pos + 3 < n) {
        size_t cand;
        if (fresh || ha < pos) {
            const void *q = memchr(subject + pos, 85, n - pos);
            ha = q ? (size_t)((const unsigned char *)q - subject) : n;
        }
        if (fresh || hb < pos) {
            const void *q = memchr(subject + pos, 117, n - pos);
            hb = q ? (size_t)((const unsigned char *)q - subject) : n;
        }
        fresh = 0;
        cand = ha < hb ? ha : hb;
        if (cand >= n) return n;
        if (cand + 3 >= n) return n;
        if ((rx_w4(subject + cand) & rx_w4("\337\337\337\337")) == rx_w4("USER")) return cand;
        pos = cand + 1;
    }
    return n;
}
