static inline uint16_t rx_w2(const void *p) { uint16_t w; memcpy(&w, p, 2); return w; }

static inline size_t rx_reqrun(const unsigned char *subject, size_t n, size_t pos)
{
    size_t ha = 0, hb = 0;
    int fresh = 1;
    while (pos + 2 < n) {
        size_t cand;
        if (fresh || ha < pos) {
            const void *q = memchr(subject + pos, 67, n - pos);
            ha = q ? (size_t)((const unsigned char *)q - subject) : n;
        }
        if (fresh || hb < pos) {
            const void *q = memchr(subject + pos, 99, n - pos);
            hb = q ? (size_t)((const unsigned char *)q - subject) : n;
        }
        fresh = 0;
        cand = ha < hb ? ha : hb;
        if (cand >= n) return n;
        if (cand + 2 >= n) return n;
        if ((rx_w2(subject + cand) & rx_w2("\337\337")) == rx_w2("CA") && (rx_w2(subject + cand + 1) & rx_w2("\337\337")) == rx_w2("AT")) return cand;
        pos = cand + 1;
    }
    return n;
}
