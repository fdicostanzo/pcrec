static inline uint32_t rx_w4(const void *p) { uint32_t w; memcpy(&w, p, 4); return w; }

static inline size_t rx_reqrun(const unsigned char *subject, size_t n, size_t pos)
{
    size_t ha = 0, hb = 0;
    int fresh = 1;
    while (pos + 5 < n) {
        size_t cand;
        if (fresh || ha < pos + 4) {
            const void *q = memchr(subject + pos + 4, 67, n - pos - 4);
            ha = q ? (size_t)((const unsigned char *)q - subject) : n;
        }
        if (fresh || hb < pos + 4) {
            const void *q = memchr(subject + pos + 4, 99, n - pos - 4);
            hb = q ? (size_t)((const unsigned char *)q - subject) : n;
        }
        fresh = 0;
        cand = ha < hb ? ha : hb;
        if (cand >= n) return n;
        cand -= 4;
        if (cand + 5 >= n) return n;
        if ((rx_w4(subject + cand) & rx_w4("\337\337\337\337")) == rx_w4("SELE") && (rx_w4(subject + cand + 2) & rx_w4("\337\337\337\337")) == rx_w4("LECT")) return cand;
        pos = cand + 1;
    }
    return n;
}
