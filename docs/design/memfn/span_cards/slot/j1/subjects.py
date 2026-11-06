# span_cards/slot/j1/subjects.py — J1's SUBJECTS (span_cards.md §3.6): pcrec-side, seeded generators of the
# SHAPES of the two bench capability subjects J1 sweeps over, never the bench's bytes (the bench's
# bench/capability/captext.py was READ for the shapes; nothing of its output is copied or read):
#   mixed  the throughput text's shape (`text()`: one line per entry, a log, HTTP, source or prose line,
#          LF-terminated, no `#`, no CR), the regime union-select's bench loss was measured on (t-1m)
#   qs     the URL query-string text's shape (`qs_text()`: `k=v&k=v...` per line, 2-10 params, one line in
#          300 a long one of 150-400, values numbers / hex / words / %-escapes / emails), where the pair's
#          look-ahead moved (t-qs-1m, O-117)
# Both plant a FEW real matches of each J1 pattern (one line in 1024 in a throughput subject, one record in 128
# in a short one), the same plant texts in both regimes, so the answer gate checks counts AND positions; the
# plant rate is far below anything that moves a 1 MiB find-all's time.
# Regimes: `throughput` = exactly LEN_TPUT bytes (the line grammar, the last line cut to fit); `short` = 1,024
# records (lines of at most 512 bytes, the bench's short_search_max_bytes), LF-joined and LF-padded to
# LEN_SHORT; a short call is the find-all over each record (a maximal LF-free run), positions absolute.
LEN_TPUT = 1048576
LEN_SHORT = 524288
NREC = 1024
MAXREC = 512

PLANTS = {
    "mixed": ['GET /search?q=1 UNION SELECT name FROM users HTTP/1.1 200 7ms',
              'cfg.load("db") username = "alice", password = "hunter22"'],
    "qs": ['q=1+union+select+id+from+t&page=2',
           "user='carol';pass='letmein99'&lang=en"],
}

M64 = (1 << 64) - 1

class Rng:
    """splitmix64, the subject generator's (gen.c's) own: stable across python versions."""
    def __init__(self, seed):
        self.x = seed & M64
    def next(self):
        self.x = (self.x + 0x9e3779b97f4a7c15) & M64
        z = self.x
        z = ((z ^ (z >> 30)) * 0xbf58476d1ce4e5b9) & M64
        z = ((z ^ (z >> 27)) * 0x94d049bb133111eb) & M64
        return z ^ (z >> 31)
    def below(self, n):
        return self.next() % n
    def pick(self, seq):
        return seq[self.below(len(seq))]

WORDS = ("data", "event", "user", "job", "item", "entry", "reply", "frame", "batch", "chunk", "lease", "route",
         "shard", "slot", "table", "agent", "probe", "timer", "trace", "result", "header", "target", "window")
HOSTS = ("app01", "db03", "lb02", "api-edge", "node-9", "store-4")
PROGS = ("sshd", "nginx", "cron", "postfix", "kernel")
LEVELS = ("INFO", "WARN", "ERROR", "DEBUG")

def _log(r):
    return "%s %s[%d]: %s %s %s" % (r.pick(HOSTS), r.pick(PROGS), 1000 + r.below(9000), r.pick(LEVELS),
                                    r.pick(WORDS), r.pick(WORDS))

def _http(r):
    return "%s /api/v2/%s/%d HTTP/1.1 %d %dms" % (r.pick(("GET", "POST", "PUT", "DELETE")), r.pick(WORDS),
                                                  r.below(9999), r.pick((200, 301, 400, 404, 500)), 1 + r.below(500))

def _source(r):
    if r.below(2):
        return 'log.debug("%s_%d")' % (r.pick(WORDS), r.below(1000))
    return "def %s_%d(v): return v * %d  # %s" % (r.pick(WORDS), r.below(99), r.below(1000), r.pick(WORDS))

def _prose(r):
    w = [r.pick(WORDS) for _ in range(6 + r.below(8))]
    return " ".join([w[0].capitalize()] + w[1:]) + "."

QS_STEMS = ("utm_source", "utm_medium", "utm_campaign", "id", "page", "q", "sort", "order", "lang", "ref", "sid",
            "session", "token", "filter", "cat", "tag", "limit", "offset", "ts", "v", "item", "lat", "lng", "sku")
QS_WORDS = ("spring", "promo", "mail", "digest", "cpc", "direct", "query", "start", "boots", "green", "gray",
            "tablet", "laptop", "en", "it", "es", "asc", "desc", "cost", "time", "title")
QS_PCT = ("%20", "%2F", "%3A", "%2C", "%40", "%C3%A9", "%2B", "%3F", "%23")
B36 = "0123456789abcdefghijklmnopqrstuvwxyz"
HEX = "0123456789abcdef"

def _qs_value(r):
    k = r.below(100)
    if k < 8:
        return ""
    if k < 38:
        return str(r.below(1000000))
    if k < 55:
        return "".join(r.pick(HEX) for _ in range(8 + r.below(25)))
    if k < 80:
        return r.pick(QS_WORDS)
    if k < 92:
        return r.pick(QS_WORDS) + r.pick(QS_PCT) + r.pick(QS_WORDS)
    return "%s%%40%s.com" % (r.pick(("ann", "ben", "cid", "dot")), r.pick(QS_WORDS))

def _qs(r):
    n = 150 + r.below(251) if r.below(300) == 0 else 2 + r.below(9)
    ks = []
    for _ in range(n):
        s = r.pick(QS_STEMS)
        ks.append(s if r.below(3) == 0 else "%s_%s" % (s, "".join(r.pick(B36) for _ in range(3))))
    return "&".join("%s=%s" % (k, _qs_value(r)) for k in ks)

KINDS = {"mixed": (_log, _http, _source, _prose), "qs": (_qs,)}
SEEDS = {("mixed", "throughput"): 0x51071A, ("mixed", "short"): 0x51071B,
         ("qs", "throughput"): 0x51071C, ("qs", "short"): 0x51071D}

def _line(r, shape):
    return r.pick(KINDS[shape])(r)

def generate(shape, regime):
    """the subject's bytes (exactly LEN_TPUT or LEN_SHORT)"""
    r = Rng(SEEDS[(shape, regime)])
    plants = PLANTS[shape]
    if regime == "throughput":
        out, total, i = [], 0, 0
        while total < LEN_TPUT:
            i += 1
            ln = plants[(i // 1024) % len(plants)] if i % 1024 == 0 else _line(r, shape)
            out.append(ln.encode())
            total += len(ln) + 1
        return (b"\n".join(out) + b"\n")[:LEN_TPUT]
    recs, i = [], 0
    while len(recs) < NREC:
        i += 1
        ln = plants[(i // 128) % len(plants)] if i % 128 == 0 else _line(r, shape)
        if 0 < len(ln) <= MAXREC:
            recs.append(ln.encode())
    b = b"\n".join(recs) + b"\n"
    assert len(b) <= LEN_SHORT, len(b)
    return b + b"\n" * (LEN_SHORT - len(b))

def records(buf):
    """(offset, bytes) per record: each maximal LF-free run, the order the artifact's short call takes them"""
    out, p = [], 0
    for part in buf.split(b"\n"):
        if part:
            out.append((p, part))
        p += len(part) + 1
    return out
