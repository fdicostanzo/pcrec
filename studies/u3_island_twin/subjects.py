#!/usr/bin/env python3
"""subjects.py -- the subject sets.

  correctness: ~6,000 short subjects (well-formed text over a pool that
    straddles every set edge the patterns use, plus the ILL-FORMED matrix:
    truncated 2/3/4-byte, overlong, surrogate, > U+10FFFF, stray continuation,
    0xFF, and a lead followed by too many continuations), each searched from
    every character boundary (short subjects) or a sample of them.
  bench regimes (design UD-7 b-island): ascii prose, latin1-heavy prose, cjk,
    mixed -- ~1 MiB each, deterministic (seeded), built without any corpus
    that is not in this repository.

Everything is deterministic (random.Random(seed)).
"""
import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# code points that straddle the edges of every set the cases use
EDGE = [0x41, 0x5A, 0x61, 0x78, 0x58, 0x7A, 0x30, 0x39, 0x5F, 0x20, 0x2E, 0x2D,
        0x7F, 0x80, 0xAA, 0xB5, 0xBF, 0xC0, 0xD7, 0xD8, 0xE9, 0xF7, 0xFF, 0x100, 0x101,
        0x24F, 0x250, 0x2FF, 0x300, 0x36F, 0x370, 0x3A9, 0x3FF, 0x400, 0x44F, 0x4FF, 0x500, 0x52F,
        0x530, 0x660, 0x669, 0x66A, 0x9E6, 0x1FFF, 0x2000, 0x2001, 0x203F, 0x3042, 0x3001,
        0x4E00, 0x5B57, 0x9FFF, 0xA000, 0xD7FF, 0xE000, 0xFF10, 0xFF21, 0xFFFD, 0xFFFE, 0xFFFF,
        0x10000, 0x10400, 0x1D7CE, 0x1F600, 0x20000, 0xE0100, 0xE01EF, 0x10FFFF]

BAD = [b"\x80", b"\xbf", b"\x80\x80", b"\xc0\x80", b"\xc1\xbf", b"\xc2", b"\xc3", b"\xdf",
       b"\xe0\x80\x80", b"\xe0\x9f\xbf", b"\xe2", b"\xe2\x80", b"\xed\xa0\x80", b"\xed\xbf\xbf",
       b"\xef\xbf", b"\xf0\x80\x80\x80", b"\xf0\x9f\x98", b"\xf4\x90\x80\x80", b"\xf5\x80\x80\x80",
       b"\xf8\x88\x80\x80\x80", b"\xff", b"\xfe", b"\xc2\x80\x80", b"\xe2\x82\xac\x80", b"\xe2\x82\xac\xac",
       # overlong forms of ASCII word / 'x' characters, and lead + too many continuations
       b"\xc1\xa1", b"\xc1\xb8", b"\xc0\xaf", b"\xe0\x81\xa1", b"\xc3\x80\x80", b"\xc4\x80\x80", b"\xe1\x80\x80\x80"]


def enc(cp):
    return chr(cp).encode("utf-8", "surrogatepass") if not (0xD800 <= cp <= 0xDFFF) else b""


def correctness(seed=20260930, n=6000):
    r = random.Random(seed)
    subs = [b"", b"x", b"\xc4\x80x", b"a\xc4\x80xb", b"\xe2\x80\x80x", b"\xe2\x80\x81x"]
    for _ in range(n):
        L = r.choice([1, 2, 3, 4, 5, 6, 8, 10, 14])
        parts = []
        for _ in range(L):
            u = r.random()
            if u < 0.10:
                parts.append(r.choice(BAD))
            elif u < 0.60:
                parts.append(enc(r.choice(EDGE)))
            elif u < 0.80:
                parts.append(bytes([r.choice(b"abxyz XYZ019_.-")]))
            else:
                parts.append(enc(r.choice([0x100 + r.randrange(0x1F00), 0xC0 + r.randrange(0x40),
                                           0x370 + r.randrange(0x200), 0x4E00 + r.randrange(0x5200)])))
        subs.append(b"".join(parts))
    # every ill-formed token alone and between x / word characters
    for b in BAD:
        for pre in (b"", b"x", "ā".encode(), "āx".encode(), b"ab"):
            for post in (b"", b"x", "ā".encode(), b"cd", "Ȃ".encode()):
                subs.append(pre + b + post)
    return subs


def boundaries(s):
    return [p for p in range(len(s) + 1) if p == len(s) or p == 0 or (s[p] & 0xC0) != 0x80]


def cases(subs, seed=7):
    r = random.Random(seed)
    out = []
    for i, s in enumerate(subs):
        bs = boundaries(s)
        if len(s) <= 12:
            fr = bs
        else:
            fr = sorted(set([0, len(s)] + r.sample(bs, min(4, len(bs)))))
        for f in fr:
            out.append((i, f))
    return out


def write_correctness():
    os.makedirs(OUT, exist_ok=True)
    subs = correctness()
    with open(os.path.join(OUT, "subjects.bin"), "wb") as f:
        f.write(struct.pack("<I", len(subs)))
        for s in subs:
            f.write(struct.pack("<I", len(s)) + s)
    cs = cases(subs)
    with open(os.path.join(OUT, "cases.tsv"), "w") as f:
        for i, fr in cs:
            f.write("%d\t%d\n" % (i, fr))
    return subs, cs


# ---------------------------------------------------------------- bench text
FR = "le la les un une des de du au aux et est sont dans pour avec sans sur sous entre chez très après avant déjà où être été à ça cœur élève forêt hôtel noël garçon façade théâtre café général problème système réponse première dernière même toujours jamais aujourd'hui demain hier maison femme homme enfant travail ville pays monde semaine année heure minute seconde grâce naïve œuvre français langue étudiant université bibliothèque".split()
DE = "der die das ein eine und ist sind nicht mit von zu für auf über unter zwischen nach vor schon noch immer wieder Größe Straße Mädchen Käse Bücher schön müde fröhlich Öl Übung Äpfel Mühle Fußball Grüße Geschäft Wörter Zeit Jahr Woche Stunde Haus Frau Mann Kind Arbeit Stadt Land Welt".split()
ES = "el la los las un una y es son en con sin por para sobre bajo entre desde hasta año niño señor mañana canción corazón más también él está aquí allí qué cómo cuándo dónde español pequeño montaña pingüino teléfono música día semana hora minuto trabajo ciudad país mundo casa mujer hombre".split()
PT = "o a os as um uma e é são em com sem por para sobre entre até não ação coração maçã pão irmão avó você também já está ele ela português tempo dia semana hora trabalho cidade país mundo casa mulher homem criança".split()
EN = "the of and to in is that for it as was with be by on not he this are or his from at which but have an had they you were their one all we can her has there been if more when will would who so no".split()
GR = "και το της των στο είναι για με ένα μια από που δεν να θα ως αλλά ή Ελλάδα ελληνικά γλώσσα κόσμος ζωή αγάπη ημέρα νύχτα".split()
CY = "и в не на я быть он с что а по это она этот к но они мы как из у который то за свой что ее так же от все Москва русский язык мир жизнь любовь день ночь".split()


def prose(r, words, n_bytes, sep=" ", end=". "):
    out = bytearray()
    while len(out) < n_bytes:
        k = r.randint(5, 16)
        sent = sep.join(r.choice(words) for _ in range(k))
        out += (sent[0].upper() + sent[1:] + end).encode()
    return bytes(out[:n_bytes]).decode("utf-8", "ignore").encode()


def ascii_prose(r, n):
    # real prose: this repository's own docs, ASCII only
    root = os.path.join(HERE, "..", "..")
    text = b""
    for rel in ("APPROACH.md", "README.md", "CONTRIBUTING.md", "docs/spec/match_api.md", "docs/design/ucp_design.md"):
        p = os.path.join(root, rel)
        if os.path.exists(p):
            text += bytes(c for c in open(p, "rb").read() if c < 0x80)
    if len(text) < 1000:
        return prose(r, EN, n)
    text = bytes(c for c in text if c in b"\n\t" or 32 <= c < 127)
    return (text * (n // len(text) + 1))[:n]


def cjk(r, n):
    out = bytearray()
    while len(out) < n:
        k = r.randint(4, 30)
        out += b"".join(enc(0x4E00 + r.randrange(0x51A6)) for _ in range(k))
        out += r.choice([enc(0x3002), enc(0x3001), enc(0xFF0C), b" ", b"\n", b"1", enc(0xFF11)])
    return bytes(out[:n]).decode("utf-8", "ignore").encode()


def latin1(r, n):
    out = bytearray()
    langs = [FR, DE, ES, PT]
    while len(out) < n:
        out += prose(r, r.choice(langs), 300)
        out += b" "
    return bytes(out[:n]).decode("utf-8", "ignore").encode()


def mixed(r, n):
    out = bytearray()
    gens = [lambda: prose(r, EN, r.randint(20, 300)), lambda: prose(r, FR, r.randint(20, 300)),
            lambda: prose(r, GR, r.randint(20, 300)), lambda: prose(r, CY, r.randint(20, 300)),
            lambda: cjk(r, r.randint(20, 300)), lambda: prose(r, DE, r.randint(20, 300)),
            lambda: b"".join(enc(0x0660 + r.randrange(10)) for _ in range(r.randint(1, 12))) + b" ",
            lambda: str(r.randrange(10 ** 8)).encode() + b" "]
    while len(out) < n:
        out += r.choice(gens)() + b" "
    return bytes(out[:n]).decode("utf-8", "ignore").encode()


REGIMES = {"ascii": ascii_prose, "latin1": latin1, "cjk": cjk, "mixed": mixed}


def write_bench(n=1 << 20):
    os.makedirs(OUT, exist_ok=True)
    info = {}
    for name, g in REGIMES.items():
        r = random.Random(hash(name) & 0xFFFF if False else sum(map(ord, name)) * 7919)
        s = g(r, n)
        s.decode("utf-8")   # well-formed by construction
        with open(os.path.join(OUT, "subj_%s.bin" % name), "wb") as f:
            f.write(s)
        info[name] = (len(s), len(s.decode()), sum(1 for c in s if c >= 0x80))
    return info


if __name__ == "__main__":
    subs, cs = write_correctness()
    print("correctness: %d subjects, %d cases" % (len(subs), len(cs)))
    for k, v in write_bench().items():
        print("bench %s: bytes=%d chars=%d nonascii_bytes=%d (%.1f%% of chars non-ASCII)" %
              ((k,) + v + (100.0 * (v[1] - (v[0] - v[2])) / v[1] if False else 0.0,)))
