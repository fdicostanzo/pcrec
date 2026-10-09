#!/usr/bin/env python3
"""walk_survey: the CORPUS population -- every distinct pattern block of every
shipped .rxt (pcrec --list-source, the block's own encoding and `i` flag, as
docs/dev/optloop/revend/census.py), with subjects:

  short   the block's own inline m/n case subjects (search; match on m)
  large   synthesized from a 16 KiB deterministic prose FILLER and the
          block's longest m subject M (or n subject N):
            fm = FILLER + M   a match near the END (search, findall)
            mf = M + FILLER   a match at the START (search, findall, match)
            fn = FILLER + N   (or FILLER alone)   (search, findall)

    pop_corpus.py PCREC REPO SUBJDIR > work/pop_corpus.tsv
"""
import hashlib, os, random, subprocess, sys

PCREC, REPO, SUBJ = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3])
os.makedirs(SUBJ, exist_ok=True)


def dec_field(b):
    out = bytearray(); i = 0
    while i < len(b):
        c = b[i]
        if c == 0x5c and i + 1 < len(b):
            n = b[i + 1]
            m = {0x5c: 0x5c, 0x74: 9, 0x6e: 10, 0x72: 13}
            if n in m: out.append(m[n]); i += 2; continue
            if n == 0x78 and i + 3 < len(b):
                try: out.append(int(b[i + 2:i + 4], 16)); i += 4; continue
                except ValueError: pass
        out.append(c); i += 1
    return bytes(out)


def dec_subject(b):
    """the .rxt quoted subject: "..." with \\" \\\\ \\n \\t \\r \\f \\v \\xHH"""
    if len(b) < 2 or b[:1] != b'"' or b[-1:] != b'"':
        return None
    b = b[1:-1]; out = bytearray(); i = 0
    m = {0x22: 0x22, 0x5c: 0x5c, 0x6e: 10, 0x74: 9, 0x72: 13, 0x66: 12, 0x76: 11}
    while i < len(b):
        c = b[i]
        if c == 0x5c and i + 1 < len(b):
            n = b[i + 1]
            if n in m: out.append(m[n]); i += 2; continue
            if n == 0x78 and i + 3 < len(b):
                try: out.append(int(b[i + 2:i + 4], 16)); i += 4; continue
                except ValueError: pass
        out.append(c); i += 1
    return bytes(out)


def filler():
    rnd = random.Random(0x5eed)
    words = ("the of and to in is was for on that with as by at from his her it "
             "an were are which this be or has had not but what all when there "
             "can more if no out so said who about time year people way day man "
             "thing woman life child world school state family student group "
             "country problem hand part place case week company system program "
             "question work government number night point home water room mother "
             "area money story fact month lot right study book eye job word "
             "business issue side kind head house service friend father power hour "
             "game line end member law car city community name president team").split()
    out = bytearray(); col = 0
    while len(out) < 16384:
        w = rnd.choice(words)
        r = rnd.random()
        if r < 0.03: w = str(rnd.randrange(1, 100000))
        elif r < 0.08: w = w.capitalize()
        out += w.encode(); col += len(w)
        r = rnd.random()
        if col > 68: out += b".\n" if r < 0.5 else b"\n"; col = 0
        elif r < 0.06: out += b", "; col += 2
        else: out += b" "; col += 1
    return bytes(out[:16384])


FILL = filler()


def put(b):
    h = hashlib.sha1(b).hexdigest()[:20]
    p = os.path.join(SUBJ, h)
    if not os.path.exists(p):
        open(p, "wb").write(b)
    return p


blocks = {}
files = []
for root, _d, fs in os.walk(os.path.join(REPO, "tests")):
    files += [os.path.join(root, f) for f in fs if f.endswith(".rxt")]
for f in sorted(files):
    r = subprocess.run([PCREC, "--list-source", f], capture_output=True, timeout=120)
    if r.returncode != 0:
        continue
    rel = os.path.relpath(f, REPO)
    sect = None; pats = {}
    for ln in r.stdout.split(b"\n"):
        if ln.startswith(b"#section"):
            sect = ln.split()[1].decode(); continue
        if not ln or ln.startswith(b"#"):
            continue
        fl = ln.split(b"\t")
        if sect is None:
            if len(fl) >= 9 and fl[0] in (b"pattern", b"pattern-esc"):
                pat = dec_field(fl[4])
                if pat and b"\x00" not in pat:
                    pats[fl[1].decode()] = (pat, "i" in fl[5].decode(),
                                            "utf8" if fl[8] == b"utf8" else "byte")
        elif sect == "cases" and len(fl) >= 8 and fl[1].decode() in pats and fl[6] == b"inline":
            s = dec_subject(fl[7])
            if s is None or fl[5] not in (b"0", b""):
                continue
            kind = fl[3].decode()
            if kind not in ("m", "n", "ms", "ns", "mc"):
                continue
            pat, ic, enc = pats[fl[1].decode()]
            key = (enc, ic, pat)
            g = blocks.setdefault(key, dict(id="%s:%s" % (rel, fl[1].decode()), m=[], n=[]))
            g["m" if kind.startswith("m") else "n"].append(s)
    for bl, (pat, ic, enc) in pats.items():
        blocks.setdefault((enc, ic, pat), dict(id="%s:%s" % (rel, bl), m=[], n=[]))

print("pid\tset\tenc\ticase\tpattern_hex\tregime\tsubjects")
for (enc, ic, pat), g in blocks.items():
    ms = sorted(set(g["m"]), key=len); ns = sorted(set(g["n"]), key=len)
    short_all = [put(s) for s in ms + ns][:24]
    M = ms[-1] if ms else b""; N = ns[-1] if ns else b""
    fm, mf, fn = put(FILL + M), put(M + FILL), put(FILL + N)
    st = g["id"].split("/")[1] if "/" in g["id"] else "?"
    row = lambda reg, subs: print("%s\t%s\t%s\t%d\t%s\t%s\t%s" % (g["id"], st, enc, ic, pat.hex(), reg, ",".join(subs)))
    if short_all:
        row("search", short_all)
    row("search", [fm, mf, fn])
    row("findall", [fm, mf, fn])
    row("match", ([put(s) for s in ms][:12]) + [mf])
