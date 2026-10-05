static inline size_t rx_reqrun(const unsigned char *subject, size_t n, size_t pos)
{
    while (pos + 1 < n) {
        size_t cand;
        const void *q = memchr(subject + pos, 105, n - pos);
        if (!q) return n;
        cand = (size_t)((const unsigned char *)q - subject);
        if (cand + 1 >= n) return n;
        if (!memcmp(subject + cand, "it", 2)) return cand;
        pos = cand + 1;
    }
    return n;
}
