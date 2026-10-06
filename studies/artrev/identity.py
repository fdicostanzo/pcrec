"""identity.py -- [ARTREV] answer identity of a twin against the pinned original.

Every exported call shape (search, search_in, match, match_in, match_caps,
match_caps_in, next_pos, valid_upto) is run on three populations -- supplied
subject files, the corpus .rxt cases for the pattern, a generated battery --
and the two arms' TRANSCRIPTS must be byte-identical (matches, spans and every
capture slot, error codes included).  A libpcre2 sample check and an optional
ASan+UBSan build ride along.  Zero differences = pass.

Three further phases are part of identity by default (charter S1-S3 / S4):
  shrunken resources  every `_in` shape is driven with {0,1} frames x {0,1} trail
                      and the step/work budgets shrunk (compile time), and the
                      two transcripts are compared under THE GIVE-UP RULE:
                      original gives up + twin answers -> the twin's answer must
                      equal libpcre2's (the repair direction), original answers +
                      twin gives up or differs -> FAIL;
  window start        for an artifact with an internal `<p>_prefilter` (the
                      hybrids), the window the prefilter proposes at every
                      search_from must be IDENTICAL, orig vs twin;
  livelock bound      the twin's driver run gets a wall budget of a multiple of
                      the original's, so a twin whose start moves early fails in
                      seconds instead of by the 900 s timeout.
--strict-giveup turns the permitted repair direction into a FAIL too (a twin must reproduce the
original's give-ups exactly): the rule's complement, for asking "does this twin change the limits
behaviour AT ALL" -- a repair is legal under the default rule, never silent under this flag.
--skip-shrunk / --skip-window exist for iteration speed; a run that skips either
logs status PASS-PARTIAL, which `time` refuses (it wants PASS).
"""
import glob
import os
import random
import re
import struct
import subprocess
import sys
import time

import common as C

HERE = C.HERE
SHAPE_FROM_CASES = (0,)


# --------------------------------------------------------------- the pattern's alphabet
def alphabet(pat, utf8):
    text = pat.decode("latin-1")
    lit, cls = set(), set()
    if r"\d" in text:
        cls |= set("0123456789")
    if r"\w" in text:
        cls |= set("abcxyzABCXYZ0189_")
    if r"\s" in text:
        cls |= set(" \t\n")
    for m in re.finditer(r"\[\^?((?:\\.|[^\]\\])+)\]", text):
        body = m.group(1)
        i = 0
        while i < len(body):
            if body[i] == "\\" and i + 1 < len(body):
                e = body[i + 1]
                cls |= set({"d": "019", "w": "aZ09_", "s": " \t", "n": "\n", "t": "\t"}.get(e, e))
                i += 2
            elif i + 2 < len(body) and body[i + 1] == "-":
                lo, hi = ord(body[i]), ord(body[i + 2])
                if hi - lo < 64:
                    cls |= set(chr(c) for c in range(lo, hi + 1))
                else:
                    cls |= set(chr(c) for c in random.Random(lo).sample(range(lo, hi + 1), 12))
                i += 3
            else:
                cls.add(body[i])
                i += 1
    for ch in text:
        if (ch.isalnum() or ch in " -_@/:,;'\"<>=#%&!~") and ord(ch) < 128:
            lit.add(ch)
    return "".join(sorted(lit)), "".join(sorted(c for c in cls if ord(c) < 128))


NEUTRAL = "xyzXYZ019 .,-_@/:\n\t"
UTF8_EXOTIC = ["\u00e9", "\u20ac", "\U0001f600", "\u65e5", "\u00df", "\u0394"]


def rnd_text(rng, lit, cls, n, utf8, byte_exotic=True):
    out = []
    pool_lit = lit or NEUTRAL
    pool_cls = cls or pool_lit
    while len(out) < n:
        r = rng.random()
        if r < 0.45:
            out.append(rng.choice(pool_lit).encode("latin-1"))
        elif r < 0.75:
            out.append(rng.choice(pool_cls).encode("latin-1"))
        elif r < 0.93:
            out.append(rng.choice(NEUTRAL).encode("latin-1"))
        elif utf8:
            out.append(rng.choice(UTF8_EXOTIC).encode("utf-8"))
        elif byte_exotic:
            out.append(bytes([rng.choice([0, 0x7f, 0x80, 0xa0, 0xc3, 0xe9, 0xff])]))
    b = b"".join(out)
    if not utf8:
        return b[:n]
    # keep valid UTF-8: truncate at a char boundary
    b = b[:n + 4]
    while b:
        try:
            b.decode("utf-8")
            break
        except UnicodeDecodeError:
            b = b[:-1]
    return b



# ------------------------------------------------- a sampler of strings the pattern matches
def _pcre_to_py(text):
    """Best-effort PCRE -> Python-re spelling, enough for sre_parse to read the shape.
    Returns None if the pattern uses something this sampler does not model."""
    t = text
    if "\\Q" in t or "(?*" in t or "(*" in t or "(?R" in t or "(?&" in t or "(?(" in t or "(?+" in t or "(?-" in t:
        return None
    t = re.sub(r"\(?<([A-Za-z_]\w*)>", r"(?P<\1>", t)
    t = re.sub(r"\(\?'([A-Za-z_]\w*)'", r"(?P<\1>", t)
    t = re.sub(r"\\k<([A-Za-z_]\w*)>", r"(?P=\1)", t)
    t = re.sub(r"\\g\{?-?\d+\}?", "", t)
    t = t.replace("(?>", "(?:").replace("\\h", "[ \\t]").replace("\\z", "\\Z")
    t = re.sub(r"\\[pP]\{\^?[A-Za-z_]+\}", "[A-Za-z]", t)
    t = re.sub(r"(?<!\\)([*+?}])\+", r"\1", t)             # possessive -> greedy
    return t


def sample_matches(pat, rng, k, utf8, caseless):
    try:
        import sre_parse
        tree = sre_parse.parse(_pcre_to_py(pat.decode("latin-1" if not utf8 else "utf-8", "replace")) or "(")
    except Exception:
        return []
    import sre_constants as sc
    out = []

    def pick_in(items):
        pool = []
        neg = False
        for op, arg in items:
            if op == sc.NEGATE:
                neg = True
            elif op == sc.LITERAL:
                pool.append(chr(arg))
            elif op == sc.RANGE:
                lo, hi = arg
                pool.extend(chr(rng.randint(lo, min(hi, lo + 5000))) for _ in range(3))
                pool.append(chr(lo))
                pool.append(chr(min(hi, 0x10ffff)))
            elif op == sc.CATEGORY:
                pool.extend({sc.CATEGORY_DIGIT: "019", sc.CATEGORY_WORD: "aZ_9", sc.CATEGORY_SPACE: " \t",
                             sc.CATEGORY_NOT_DIGIT: "x.", sc.CATEGORY_NOT_WORD: " .-", sc.CATEGORY_NOT_SPACE: "xy9"}.get(arg, "x"))
        if neg:
            cand = [c for c in "xyzXYZ019 .,-_@/:" if c not in pool] or ["\x01"]
            return rng.choice(cand)
        return rng.choice(pool) if pool else "x"

    def gen(seq, groups, buf):
        for op, arg in seq:
            if op == sc.LITERAL:
                buf.append(chr(arg))
            elif op == sc.NOT_LITERAL:
                buf.append(rng.choice([c for c in "xyz019 " if ord(c) != arg]))
            elif op == sc.ANY:
                buf.append(rng.choice("xyzXYZ019 .,-_@/:"))
            elif op == sc.IN:
                buf.append(pick_in(arg))
            elif op == sc.BRANCH:
                gen(rng.choice(arg[1]), groups, buf)
            elif op == sc.SUBPATTERN:
                gid, _a, _b, sub = arg
                start = len(buf)
                gen(sub, groups, buf)
                if gid is not None:
                    groups[gid] = "".join(buf[start:])
            elif op in (sc.MAX_REPEAT, sc.MIN_REPEAT, getattr(sc, "POSSESSIVE_REPEAT", -1)):
                lo, hi, sub = arg
                hi = min(hi if hi != sc.MAXREPEAT else lo + 4, lo + 4)
                n = rng.randint(lo, max(lo, hi)) if rng.random() < 0.7 else lo
                for _ in range(min(n, 2000)):
                    gen(sub, groups, buf)
            elif op == sc.GROUPREF:
                buf.append(groups.get(arg, ""))
            elif op == sc.CATEGORY:
                buf.append(pick_in([(sc.CATEGORY, arg)]))
            elif op == sc.AT and arg in (sc.AT_BOUNDARY, sc.AT_NON_BOUNDARY):
                last = "".join(buf[-1:])
                if arg == sc.AT_BOUNDARY and last and (last.isalnum() or last == "_"):
                    buf.append(" ")        # \b after a word char: step off it (the next piece may be a word char too)
            # other AT / ASSERT / ASSERT_NOT: no text
    for _ in range(k * 3):
        try:
            buf = []
            gen(tree, {}, buf)
            sm = "".join(buf)
            if caseless:
                sm = "".join(c.swapcase() if rng.random() < 0.3 else c for c in sm)
            b = sm.encode("utf-8") if utf8 else sm.encode("latin-1", "replace")
            if len(b) <= 600:
                out.append(b)
        except Exception:
            return out
        if len(out) >= k:
            break
    return out


# ------------------------------------------------------------------ the corpus reader
_ESC = {"n": 10, "t": 9, "r": 13, "f": 12, "v": 11, "\\": 92, '"': 34}


def unquote(s):
    """Decode one leading double-quoted .rxt subject string; None if not of that shape."""
    if not s.startswith('"'):
        return None
    out = bytearray()
    i = 1
    while i < len(s):
        c = s[i]
        if c == '"':
            rest = s[i + 1:]
            return bytes(out) if (rest == "" or rest[0] in " \t") else None
        if c == "\\" and i + 1 < len(s):
            e = s[i + 1]
            if e == "x" and i + 3 < len(s) + 1 and re.match(r"[0-9a-fA-F]{2}", s[i + 2:i + 4]):
                out.append(int(s[i + 2:i + 4], 16))
                i += 4
                continue
            if e in _ESC:
                out.append(_ESC[e])
                i += 2
                continue
            return None
        out += c.encode("utf-8")
        i += 1
    return None


def art_signature(meta):
    fl = meta["pcrec_flags"]
    letters = set("i") if "-i" in fl else set()
    enc = "byte"
    for k, f in enumerate(fl):
        if f in ("-e", "--encoding") and k + 1 < len(fl):
            enc = fl[k + 1]
        if f.startswith("--encoding="):
            enc = f.split("=", 1)[1]
    return letters, enc


def corpus_subjects(meta, tests_dir):
    pat = bytes.fromhex(meta["pattern_hex"])
    want_flags, want_enc = art_signature(meta)
    subs = []
    nfiles = 0
    for path in sorted(glob.glob(os.path.join(tests_dir, "**", "*.rxt"), recursive=True)):
        head_flags, head_enc = set(), "byte"
        cur = None
        in_block = False
        try:
            lines = open(path, "rb").read().decode("utf-8", "surrogateescape").split("\n")
        except OSError:
            continue

        def flush(cur):
            if cur and cur["pat"] == pat and cur["flags"] == want_flags and cur["enc"] == want_enc:
                subs.extend(cur["subs"])
                return 1
            return 0
        for ln in lines:
            if ln.startswith("pattern ") or ln.startswith("pattern-esc "):
                nfiles += 0
                flush(cur)
                rest = ln.split(" ", 1)[1]
                if ln.startswith("pattern-esc "):
                    p = unquote('"' + rest.strip().strip('"') + '"')
                    p = p if p is not None else b"\0invalid"
                else:
                    p = rest.encode("utf-8", "surrogateescape")
                cur = {"pat": p, "flags": set(head_flags), "enc": head_enc, "subs": []}
                in_block = True
            elif not in_block:
                if ln.startswith("flags "):
                    head_flags = set(ln.split()[1])
                elif ln.startswith("encoding "):
                    head_enc = ln.split()[1]
            elif cur is not None:
                if ln.startswith("flags "):
                    cur["flags"] = set(ln.split()[1])
                elif ln.startswith("encoding "):
                    cur["enc"] = ln.split()[1]
                elif ln.startswith("m ") or ln.startswith("n "):
                    sj = unquote(ln.split(" ", 1)[1])
                    if sj is not None:
                        cur["subs"].append(sj)
        flush(cur)
    return subs


# --------------------------------------------------------------------------- files
def write_subjects(path, subs):
    with open(path, "wb") as f:
        f.write(struct.pack("<I", len(subs)))
        for s in subs:
            f.write(struct.pack("<I", len(s)))
            f.write(s)


def write_cases(path, cases):
    with open(path, "w") as f:
        for idx, frm, mode in cases:
            f.write("%d\t%d\t%s\n" % (idx, frm, mode))


def froms_for(n):
    s = {0, n}
    if n >= 1:
        s |= {1, n - 1}
    if n >= 2:
        s.add(n // 2)
    return sorted(s)


def run_driver(exe, subj, cases, san=False, timeout=900, extra=()):
    env = dict(os.environ)
    if san:
        env["ASAN_OPTIONS"] = "detect_leaks=0:abort_on_error=0:allocator_may_return_null=1"
        env["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
    try:
        argv = [exe, subj] + ([cases] if cases else []) + list(extra)
        r = subprocess.run(argv, capture_output=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return None, b"", "TIMEOUT after %ds" % timeout
    return r.returncode, r.stdout, r.stderr.decode("utf-8", "replace")[-1500:]


# ----------------------------------------------------------------------- the battery
def build_battery(meta, orig_exe, wdir, a, extra_subs, rng):
    pat = bytes.fromhex(meta["pattern_hex"])
    _, enc = art_signature(meta)
    utf8 = enc.lower() in ("utf8", "utf-8")
    lit, cls = alphabet(pat, utf8)
    blocks = sorted(set(b for b in a.block if b > 0))
    lens = list(range(0, 65))
    for b in blocks:
        for k in (1, 2, 3, 4, 8):
            lens += [k * b - 1, k * b, k * b + 1]
    lens = sorted(set(x for x in lens if x >= 0))
    N = a.battery
    subs = []
    seen = set()

    def add(s):
        if s not in seen and len(subs) < N + len(extra_subs):
            seen.add(s)
            subs.append(s)

    for s in extra_subs:
        seen.add(s)
        subs.append(s)
    # phase 1: random over the alphabet, lengths 0-64 and around each block size
    n1 = max(N * 4 // 10, 1)
    guard = 0
    while len(subs) < len(extra_subs) + n1 and guard < n1 * 20:
        guard += 1
        L = rng.choice(lens) if rng.random() < 0.8 else rng.randint(0, 64)
        add(rnd_text(rng, lit, cls, L, utf8))
    # harvest matches from phase 1 + the extras with the ORIGINAL arm
    p1 = os.path.join(wdir, "p1.subj")
    write_subjects(p1, subs)
    cases = [(i, f, "p") for i, s in enumerate(subs) for f in froms_for(len(s))]
    write_cases(os.path.join(wdir, "p1.cases"), cases)
    rc, out, err = run_driver(orig_exe, p1, os.path.join(wdir, "p1.cases"))
    harvest = [m.encode("utf-8") if isinstance(m, str) else m for m in a.match_example]
    harvest += sample_matches(pat, rng, max(N // 6, 20), utf8, "-i" in meta["pcrec_flags"])
    if rc == 0:
        for ln in out.decode("latin-1").split("\n"):
            if ln.startswith("S\t"):
                t = ln.split("\t")
                if t[3] == "1":
                    i, s0, e0 = int(t[1]), int(t[4]), int(t[5])
                    if 0 <= s0 <= e0 <= len(subs[i]) and e0 - s0 <= 512:
                        harvest.append(subs[i][s0:e0])
    # corpus subjects are not matches by themselves, but their matched spans are
    harvest = list(dict.fromkeys(harvest))
    rng.shuffle(harvest)
    fillers = [0, 1, 2, 5] + [b - 1 for b in blocks if b > 1] + blocks + [b + 1 for b in blocks] + [63, 64]
    def filler(k):
        return rnd_text(rng, "", "", k, utf8, byte_exotic=False).replace(b"\0", b"x") if k else b""
    for h in harvest:
        if len(subs) >= N + len(extra_subs):
            break
        for k in rng.sample(fillers, min(3, len(fillers))):
            f = filler(k)
            add(h)                      # match is the whole subject (start AND end)
            add(f + h)                  # match at the END of the subject
            add(h + f)                  # match at the START
            add(f + h + filler(k))
        # near misses
        if len(h) >= 1:
            p = rng.randrange(len(h))
            add(h[:p] + h[p + 1:])                                           # delete a byte
            add(h[:p] + bytes([rng.choice(list((lit + cls + NEUTRAL).encode("latin-1") or b"x"))]) + h[p + 1:])
            add(h[:-1])
            add(h[1:])
            add(h + h[:1])
            add(h[:p] + h[p:p + 1] + h[p:])                                  # duplicate one
    # top up with random if harvest was thin
    guard = 0
    while len(subs) < N + len(extra_subs) and guard < N * 20:
        guard += 1
        add(rnd_text(rng, lit, cls, rng.choice(lens), utf8))
    return subs


# -------------------------------------------------------------------------- pcre2
def pcre2_ref_exe():
    exe = os.path.join(C.art_root(), "_pcre2_ref")
    src = os.path.join(HERE, "pcre2_ref.c")
    if os.path.exists(exe) and os.path.getmtime(exe) >= os.path.getmtime(src):
        return exe, C.run([exe]).stderr and None
    os.makedirs(C.art_root(), exist_ok=True)
    cands = []
    pk = C.run(["pkg-config", "--cflags", "--libs", "libpcre2-8"])
    if pk.returncode == 0:
        cands.append(pk.stdout.split())
    cands += [["-I/opt/homebrew/include", "-L/opt/homebrew/lib", "-lpcre2-8"], ["-lpcre2-8"]]
    for fl in cands:
        r = C.run(["cc", "-O1", "-w", src, "-o", exe] + fl)
        if r.returncode == 0:
            return exe, None
    return None, "cannot build pcre2_ref.c (libpcre2-8 not found)"


def pcre2_version():
    for inc in ("/opt/homebrew/include", "/usr/include", "/usr/local/include"):
        p = os.path.join(inc, "pcre2.h")
        if os.path.exists(p):
            t = open(p).read()
            mj = re.search(r"#define PCRE2_MAJOR\s+(\d+)", t)
            mn = re.search(r"#define PCRE2_MINOR\s+(\d+)", t)
            if mj and mn:
                return "%s.%s (%s)" % (mj.group(1), mn.group(1), inc)
    return "unknown"


def parse_S(out):
    d = {}
    for ln in out.decode("latin-1").split("\n"):
        if ln.startswith("S\t"):
            t = ln.split("\t")
            d[(int(t[1]), int(t[2]))] = (int(t[3]), tuple(int(x) for x in t[4:]))
    return d


def utf8_ok(s, frm):
    try:
        s.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return frm >= len(s) or (s[frm] & 0xC0) != 0x80


def pcre2_check(meta, subs, cases, wdir, orig_out, twin_out, nsample, rng):
    res = {"status": "SKIPPED", "checked": 0, "skipped": 0, "orig_disagree": 0, "twin_only": 0, "notes": []}
    if nsample <= 0:
        return res
    exe, err = pcre2_ref_exe()
    if not exe:
        res["notes"].append(err)
        return res
    _, enc = art_signature(meta)
    utf8 = enc.lower() in ("utf8", "utf-8")
    pool = [(i, f, m) for (i, f, m) in cases if m == "p" and (not utf8 or utf8_ok(subs[i], f))]
    rng.shuffle(pool)
    pool = pool[:nsample]
    sj, cs = os.path.join(wdir, "all.subj"), os.path.join(wdir, "pc2.cases")
    write_cases(cs, pool)
    flags = ("i" if "-i" in meta["pcrec_flags"] else "") + ("u" if utf8 else "") + \
            ("c" if utf8 or "--ucp" in meta["pcrec_flags"] else "")
    pf = os.path.join(wdir, "pattern.bin")
    open(pf, "wb").write(bytes.fromhex(meta["pattern_hex"]))
    r = subprocess.run([exe, sj, cs, str(meta["ncaps"]), pf, flags], capture_output=True, timeout=300)
    if r.returncode != 0:
        res["notes"].append("pcre2_ref rc=%d: %s" % (r.returncode, r.stderr.decode("utf-8", "replace")[:200]))
        return res
    ref, o, t = parse_S(r.stdout), parse_S(orig_out), parse_S(twin_out)
    res["status"] = "OK"
    for k, rv in ref.items():
        if k not in o or k not in t:
            continue
        def norm(x):
            return (x[0], x[1][:2 * meta["ncaps"]]) if x[0] == 1 else (x[0], ())
        if rv[0] < 0 or o[k][0] < 0 or t[k][0] < 0:
            res["skipped"] += 1
            continue
        res["checked"] += 1
        od, td = norm(o[k]) != norm(rv), norm(t[k]) != norm(rv)
        if od:
            res["orig_disagree"] += 1
            if len(res["notes"]) < 3:
                res["notes"].append("orig vs libpcre2 at %s: pcrec %s  pcre2 %s" % (k, norm(o[k]), norm(rv)))
        if td and not od:
            res["twin_only"] += 1
            if len(res["notes"]) < 6:
                res["notes"].append("TWIN-ONLY disagreement with libpcre2 at %s: twin %s  pcre2 %s" % (k, norm(t[k]), norm(rv)))
    return res



# ------------------------------------------------------------ the give-up rule
LIVELOCK_FLOOR = float(os.environ.get("ARTREV_LIVELOCK_FLOOR", "30"))   # s; the twin's wall bound = max(this, 25 x the original's)
GIVEUP = (-5, -4, -3, -2)           # PCREC_ERR_FLOOR .. PCREC_ERR_STEPS (artifact.h)
S_SHAPES = ("S", "SI", "F", "FSI")   # rc 1 / 0 are answers
M_SHAPES = ("M", "MI", "C", "CI", "FC")   # rc >= 0 (matched length) / -1 are answers
DEFAULT_BUDGETS = "8:64,64:1024,2000:40000"


def _family(shape):
    return shape.split(".")[0]


def _rc(t):
    try:
        return int(t[3])
    except (IndexError, ValueError):
        return None


def _is_answer(fam, rc):
    if rc is None:
        return False
    if fam in S_SHAPES:
        return rc in (0, 1)
    if fam in M_SHAPES:
        return rc >= -1
    return False


def giveup_compare(otext, ttext):
    """Compare two transcripts under THE GIVE-UP RULE.  Lines are keyed (shape, idx, from) --
    a twin that answers where the original gave up may walk a find-all further, so line
    positions are not stable.  Returns a dict: fails [(why, orig_line, twin_line)],
    repairs [(shape, idx, from, twin_line)] (the oracle checks these), counters."""
    def index(text):
        d, order = {}, []
        for ln in text.split(b"\n"):
            if not ln:
                continue
            t = ln.split(b"\t")
            k = (t[0].decode("latin-1"), t[1], t[2])
            if k not in d:
                order.append(k)
            d.setdefault(k, []).append(ln)
        return d, order
    od, oord = index(otext)
    td, tord = index(ttext)
    res = {"fails": [], "repairs": [], "twin_only": [], "n_orig_giveup": 0, "n_both_giveup": 0,
           "n_lines": sum(len(v) for v in od.values())}
    repaired_walks = set()
    for k in oord:
        ov = od[k]
        tv = td.get(k)
        if tv is None:
            res["fails"].append(("line missing from the twin transcript", ov[0], b"<missing>"))
            continue
        if len(ov) != len(tv):
            res["fails"].append(("line count differs for one call", ov[0], tv[0]))
            continue
        for x, y in zip(ov, tv):
            if x == y:
                if _rc(x.split(b"\t")) in GIVEUP:
                    res["n_orig_giveup"] += 1
                    res["n_both_giveup"] += 1
                continue
            xt, yt = x.split(b"\t"), y.split(b"\t")
            fam = _family(k[0])
            ro, rt = _rc(xt), _rc(yt)
            if fam not in S_SHAPES and fam not in M_SHAPES:
                res["fails"].append(("N/V line differs", x, y))
            elif ro in GIVEUP:
                res["n_orig_giveup"] += 1
                if rt in GIVEUP:
                    res["n_both_giveup"] += 1          # a different give-up code: still a give-up
                elif _is_answer(fam, rt):
                    res["repairs"].append((k[0], int(k[1]), int(k[2]), y))
                    if fam in ("F", "FSI", "FC"):
                        repaired_walks.add(int(k[1]))
                else:
                    res["fails"].append(("twin returned a non-answer, non-give-up code where the original gave up", x, y))
            elif rt in GIVEUP:
                res["fails"].append(("twin GIVES UP where the original answers", x, y))
            else:
                res["fails"].append(("answers differ", x, y))
    for k in tord:
        if k in od:
            continue
        fam = _family(k[0])
        if fam in ("F", "FSI", "FC") and int(k[1]) in repaired_walks:
            for y in td[k]:
                res["twin_only"].append((k[0], int(k[1]), int(k[2]), y))
        else:
            res["fails"].append(("line only in the twin transcript", b"<missing>", td[k][0]))
    return res


def oracle_check_repairs(meta, subs, repairs, wdir, rng_unused=None):
    """Every (repair | twin-only line) must equal libpcre2's answer.  Returns
    (checked, skipped, bad[list of messages], note|None)."""
    if not repairs:
        return 0, 0, [], None
    exe, err = pcre2_ref_exe()
    if not exe:
        return 0, 0, ["no libpcre2 oracle available (%s) -- cannot verify %d give-up repair(s)" % (err, len(repairs))], None
    _, enc = art_signature(meta)
    utf8 = enc.lower() in ("utf8", "utf-8")
    want = []
    skipped = 0
    for shape, idx, frm, line in repairs:
        fam = _family(shape)
        if utf8 and not utf8_ok(subs[idx], frm if fam in S_SHAPES + M_SHAPES else 0):
            skipped += 1
            continue
        if frm > len(subs[idx]):
            skipped += 1
            continue
        want.append((shape, idx, frm, line, "p" if fam in S_SHAPES else "a"))
    sj, cs = os.path.join(wdir, "all.subj"), os.path.join(wdir, "rep.cases")
    with open(cs, "w") as f:
        for _, idx, frm, _, mode in want:
            f.write("%d\t%d\t%s\n" % (idx, frm, mode))
    flags = ("i" if "-i" in meta["pcrec_flags"] else "") + ("u" if utf8 else "") + \
            ("c" if utf8 or "--ucp" in meta["pcrec_flags"] else "")
    pf = os.path.join(wdir, "pattern.bin")
    open(pf, "wb").write(bytes.fromhex(meta["pattern_hex"]))
    r = subprocess.run([exe, sj, cs, str(meta["ncaps"]), pf, flags], capture_output=True, timeout=300)
    if r.returncode != 0:
        return 0, 0, ["pcre2_ref rc=%d: %s" % (r.returncode, r.stderr.decode("utf-8", "replace")[:200])], None
    ref = {}
    for ln in r.stdout.decode("latin-1").split("\n"):
        t = ln.split("\t")
        if len(t) >= 4 and t[0] in ("S", "A"):
            ref[(t[0], int(t[1]), int(t[2]))] = (int(t[3]), tuple(int(x) for x in t[4:]))
    nc = meta["ncaps"]
    bad, checked = [], 0
    for shape, idx, frm, line, mode in want:
        rv = ref.get(("S" if mode == "p" else "A", idx, frm))
        if rv is None or rv[0] < 0:
            skipped += 1
            continue
        t = line.split(b"\t")
        rc = int(t[3])
        caps = tuple(int(x) for x in t[4:4 + 2 * nc]) if len(t) > 4 else ()
        fam = _family(shape)
        checked += 1
        if fam in S_SHAPES:
            ok = (rc == rv[0]) and (rv[0] == 0 or caps == rv[1][:2 * nc] or len(caps) == 0)
        else:
            if rv[0] == 0:
                ok = rc == -1
            else:
                ok = rc == rv[1][1] - frm and (len(caps) == 0 or caps == rv[1][:2 * nc])
        if not ok and len(bad) < 5:
            bad.append("REPAIR DISAGREES with libpcre2 at %s idx %d from %d: twin %s  libpcre2 rc=%d %s" % (
                shape, idx, frm, line.decode("latin-1").replace("\t", " "), rv[0], rv[1][:2 * nc]))
        elif not ok:
            bad.append("(more)")
    return checked, skipped, [b for b in bad if b != "(more)"] + (["..."] if "(more)" in bad else []), None


def shrunk_phase(a, meta, base, ad, od, sj, cs, subs, wdir):
    """Returns (status, text).  status in PASS/FAIL/NA."""
    budgets = []
    for p in a.shrunk_budgets.split(","):
        st, wk = p.split(":")
        budgets.append((int(st), int(wk)))
    has_b = C.has_budgets(od) and C.has_budgets(ad)
    if not meta.get("have_in") and not has_b:
        return "NA", "shrunken resources: n/a (no `_in` entries and no step/work budget stamps in this artifact)"
    runs = budgets if has_b else [None]
    lines, fails, tot_rep, tot_chk, tot_skip, tot_giveup, tot_lines = [], [], 0, 0, 0, 0, 0
    for bud in runs:
        if bud:
            ex_o, ex_t = C.compile_shrunk(meta, od, bud[0], bud[1], a.san), C.compile_shrunk(meta, ad, bud[0], bud[1], a.san)
            lab = "steps=%d work=%d" % bud
        else:
            ex_o, ex_t = C.compile_arm(meta, od, "id", a.san), C.compile_arm(meta, ad, "id", a.san)
            lab = "default budgets"
        t0 = time.monotonic()
        rco, oo, eo = run_driver(ex_o, sj, cs, san=a.san, extra=["shrunk"])
        el = time.monotonic() - t0
        if rco != 0:
            return "FAIL", "shrunken resources (%s): the ORIGINAL driver failed rc=%s: %s" % (lab, rco, eo)
        rct, ot, et = run_driver(ex_t, sj, cs, san=a.san, extra=["shrunk"], timeout=min(900, max(LIVELOCK_FLOOR, 25 * el)))
        if rct != 0:
            return "FAIL", "shrunken resources (%s): the TWIN driver FAILED rc=%s%s: %s" % (
                lab, rct, " (livelock bound: >25x the original's wall)" if rct is None else "", et)
        g = giveup_compare(oo, ot)
        if a.strict_giveup:
            for shape, idx, frm, y in g["repairs"][:3]:
                fails.append("[%s] --strict-giveup: twin answers where the original gave up: %s idx %d from %d" % (lab, shape, idx, frm))
            if g["repairs"]:
                fails.append("[%s] --strict-giveup: %d give-up repairs in all" % (lab, len(g["repairs"])))
        chk, skp, bad, _ = oracle_check_repairs(meta, subs, g["repairs"] + g["twin_only"], wdir)
        tot_rep += len(g["repairs"])
        tot_chk += chk
        tot_skip += skp
        tot_giveup += g["n_orig_giveup"]
        tot_lines += g["n_lines"]
        lines.append("  %-22s lines %d, original gives up on %d, repairs %d (+%d walk lines), oracle-checked %d" % (
            lab, g["n_lines"], g["n_orig_giveup"], len(g["repairs"]), len(g["twin_only"]), chk))
        for why, x, y in g["fails"][:3]:
            fails.append("[%s] %s:\n      orig: %s\n      twin: %s" % (lab, why, x.decode("latin-1").replace("\t", " "),
                                                                       y.decode("latin-1").replace("\t", " ")))
        if len(g["fails"]) > 3:
            fails.append("[%s] ... %d give-up-rule violations in all" % (lab, len(g["fails"])))
        for b in bad:
            fails.append("[%s] %s" % (lab, b))
    head = ("shrunken resources (0/1 frames x 0/1 trail%s): %d transcript lines, original gives up on %d, "
            "%d give-up repair(s) of which %d checked against libpcre2 (%d skipped)" % (
                ", budgets " + a.shrunk_budgets if has_b else "; no budget stamps, buffer axis only",
                tot_lines, tot_giveup, tot_rep, tot_chk, tot_skip))
    txt = head + "\n" + "\n".join(lines)
    if fails:
        return "FAIL", txt + "\nGIVE-UP RULE VIOLATED:\n  " + "\n  ".join(fails)
    return "PASS", txt


def window_phase(a, meta, base, ad, od, sj):
    """The window-start differential.  Returns (status, text)."""
    src = open(os.path.join(od, "artifact.c")).read()
    if not re.search(r"\nstatic int %s_prefilter\(" % re.escape(meta["prefix"]), src):
        return "NA", "window start: n/a (no internal %s_prefilter in this artifact)" % meta["prefix"]
    ex_o, ex_t = C.compile_arm(meta, od, "pf", a.san), C.compile_arm(meta, ad, "pf", a.san)
    t0 = time.monotonic()
    rco, oo, eo = run_driver(ex_o, sj, None, san=a.san)
    el = time.monotonic() - t0
    if rco != 0:
        return "FAIL", "window start: the ORIGINAL driver failed rc=%s: %s" % (rco, eo)
    rct, ot, et = run_driver(ex_t, sj, None, san=a.san, timeout=min(900, max(LIVELOCK_FLOOR, 25 * el)))
    if rct != 0:
        return "FAIL", "window start: the TWIN driver FAILED rc=%s%s: %s" % (
            rct, " (livelock bound: >25x the original's wall)" if rct is None else "", et)
    ol, tl = oo.split(b"\n"), ot.split(b"\n")
    nd, first = 0, None
    for k in range(max(len(ol), len(tl))):
        x = ol[k] if k < len(ol) else b"<missing>"
        y = tl[k] if k < len(tl) else b"<missing>"
        if x != y:
            nd += 1
            first = first or (x, y)
    hits = sum(1 for x in ol if x.split(b"\t")[3:4] == [b"1"])
    txt = "window start: %d prefilter windows compared (original proposes a window on %d), start differences %d" % (
        len(ol) - 1, hits, nd)
    if nd:
        return "FAIL", txt + "\n  FIRST: orig %s\n         twin %s" % (first[0].decode("latin-1").replace("\t", " "),
                                                                    first[1].decode("latin-1").replace("\t", " "))
    return "PASS", txt

# ----------------------------------------------------------------------------- main
def cmd_identity(a):
    meta = C.load_meta(a.name)
    base = C.art_dir(a.name)
    ad = os.path.join(base, "arms", a.arm)
    if not os.path.exists(os.path.join(ad, "artifact.c")):
        C.die("no arm %r under %s" % (a.arm, base))
    od = os.path.join(base, "arms", "orig")
    wdir = os.path.join(base, "identity", a.arm)
    os.makedirs(wdir, exist_ok=True)
    rng = random.Random(a.seed)
    orig_exe = C.compile_arm(meta, od, "id", san=a.san)
    twin_exe = C.compile_arm(meta, ad, "id", san=a.san)
    # ---- populations
    subs, cases, tags = [], [], []
    for path in a.subject:
        s = open(path, "rb").read()
        i = len(subs)
        subs.append(s)
        cases.append((i, 0, "f"))
        for f in (0, len(s)):
            cases.append((i, f, "p"))
        tags.append(("supplied", i, path))
    corp = corpus_subjects(meta, a.tests_dir or os.path.join(C.tree_root(), "tests")) if a.corpus else []
    n_corpus = len(corp)
    for s in corp:
        i = len(subs)
        subs.append(s)
        for f in froms_for(len(s)):
            cases.append((i, f, "p"))
        tags.append(("corpus", i, ""))
    n_before_batt = len(subs)
    if a.battery > 0:
        bs = build_battery(meta, orig_exe, wdir, a, [s for s in subs], rng)
        for s in bs[len(subs):]:
            i = len(subs)
            subs.append(s)
            for f in froms_for(len(s)):
                cases.append((i, f, "p"))
    n_batt = len(subs) - n_before_batt
    sj, cs = os.path.join(wdir, "all.subj"), os.path.join(wdir, "all.cases")
    write_subjects(sj, subs)
    write_cases(cs, cases)
    rcs = {}
    outs = {}
    tmo = 900
    for label, exe in (("orig", orig_exe), ("twin", twin_exe)):
        t0 = time.monotonic()
        rc, out, err = run_driver(exe, sj, cs, san=a.san, timeout=tmo)
        if label == "orig":
            tmo = min(900, max(LIVELOCK_FLOOR, 25 * (time.monotonic() - t0)))   # the livelock bound for the twin
        rcs[label], outs[label] = rc, out
        if rc != 0:
            msg = "%s arm driver FAILED (rc=%s)%s%s:\n%s" % (label, rc, " under ASan/UBSan" if a.san else "",
                                                          " -- LIVELOCK suspected (the twin ran >25x the original's wall)"
                                                          if rc is None and label == "twin" else "", err)
            return finish(a, meta, ad, "FAIL", msg)
    ol, tl = outs["orig"].split(b"\n"), outs["twin"].split(b"\n")
    ndiff = 0
    first = None
    for k in range(max(len(ol), len(tl))):
        x = ol[k] if k < len(ol) else b"<missing>"
        y = tl[k] if k < len(tl) else b"<missing>"
        if x != y:
            ndiff += 1
            if first is None:
                first = (k, x, y)
    repair_note = ""
    if ndiff:
        # a twin may ANSWER where the original gave up (THE GIVE-UP RULE); anything else stays a difference
        g0 = giveup_compare(outs["orig"], outs["twin"])
        if not g0["fails"]:
            chk0, skp0, bad0, _ = oracle_check_repairs(meta, subs, g0["repairs"] + g0["twin_only"], wdir)
            if not bad0:
                repair_note = "\ndefault-buffer give-up repairs: %d (+%d walk lines), %d checked against libpcre2, all equal" % (
                    len(g0["repairs"]), len(g0["twin_only"]), chk0)
                ndiff = 0
    nS = sum(1 for x in ol if x.startswith(b"S\t"))
    nSm = sum(1 for x in ol if x.startswith(b"S\t") and x.split(b"\t")[3] == b"1")
    p2 = pcre2_check(meta, subs, cases, wdir, outs["orig"], outs["twin"], a.pcre2_sample, rng)
    nSI = sum(1 for x in ol if x.startswith(b"SI\t"))
    summary = ("subjects: %d supplied, %d corpus, %d battery; %d cases, %d transcript lines compared "
               "(shapes: S M C%s N V + find-all F/FC%s; %d `_in` search lines driven); san=%s\n"
               "search cases that MATCH in the original: %d of %d%s\n"
               "libpcre2 %s: %s, checked %d, skipped %d, orig-vs-pcre2 disagreements %d, twin-only %d" % (
                   len(a.subject), n_corpus, n_batt, len(cases), len(ol), " SI MI CI" if meta["have_in"] else "",
                   " FSI" if meta["have_in"] else "", nSI, a.san, nSm, nS,
                   "   ** THIN: under 5% match -- pass --match-example STR (a string the pattern matches) or --subject **"
                   if nS and nSm * 20 < nS else "", pcre2_version(), p2["status"], p2["checked"], p2["skipped"],
                   p2["orig_disagree"], p2["twin_only"]))
    for n in p2["notes"]:
        summary += "\n  note: " + n
    summary += repair_note
    # ---- shrunken resources + window start (default parts of identity)
    extra_status = []
    if a.skip_shrunk:
        summary += "\nshrunken resources: SKIPPED (--skip-shrunk)"
        extra_status.append("PARTIAL")
    else:
        st, txt = shrunk_phase(a, meta, base, ad, od, sj, cs, subs, wdir)
        summary += "\n" + txt
        extra_status.append(st)
    if a.skip_window:
        summary += "\nwindow start: SKIPPED (--skip-window)"
        extra_status.append("PARTIAL")
    else:
        st, txt = window_phase(a, meta, base, ad, od, sj)
        summary += "\n" + txt
        extra_status.append(st)
    if ndiff:
        k, x, y = first
        cidx = int(x.split(b"\t")[1]) if b"\t" in x and x.split(b"\t")[1].isdigit() else None
        subj = subs[cidx] if cidx is not None and cidx < len(subs) else b""
        summary += ("\nFIRST DIFFERENCE (of %d differing lines) at transcript line %d:\n  orig: %s\n  twin: %s\n"
                    "  subject #%s (%d bytes): %r" % (ndiff, k, x.decode("latin-1"), y.decode("latin-1"), cidx,
                                                  len(subj), subj[:160]))
        return finish(a, meta, ad, "FAIL", summary)
    if p2["twin_only"] or "FAIL" in extra_status:
        return finish(a, meta, ad, "FAIL", summary)
    return finish(a, meta, ad, "PASS-PARTIAL" if "PARTIAL" in extra_status else "PASS", summary)


def finish(a, meta, ad, status, summary):
    revp = os.path.join(ad, "rev")
    rev = int(open(revp).read()) if os.path.exists(revp) else 0
    sha = C.sha256_file(os.path.join(ad, "artifact.c"))
    C.ledger_append(a.name, "identity", a.arm, rev, False, status, sha,
                    summary.split("\n")[0][:200] + (" [san]" if a.san else ""))
    print("IDENTITY %s  arm=%s rev=%d  %s\n%s" % (status, a.arm, rev, "(ASan+UBSan)" if a.san else "", summary))
    return 0 if status in ("PASS", "PASS-PARTIAL") else 1
