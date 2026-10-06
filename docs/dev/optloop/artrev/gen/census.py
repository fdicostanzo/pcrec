#!/usr/bin/env python3
"""[ARTREV] S5 generalizer census: how many artifacts carry each pilot lead's shape.

COMPILE-SIDE ONLY (K35: an uncounted population is not a finding). No subject is
matched and no clock is read. Every classifier reads what pcrec itself emits
(`--emit-facts`: the facts record + the decision stamps; `-o -`: the artifact),
plus, for two leads, a second compile of a VARIANT pattern (I6: the hand-
possessified spelling; I11: the START-SET stage-3 compiler) whose emitted text
says whether the shipped emitter already reaches the lead's shape.

Populations (the revend census's rule, docs/dev/optloop/revend/census.py):
  bench   every pcrec-bench bench/<set>/patterns/*.rx (READ-ONLY), compiled as the
          bench's pcrec-auto testee does: --features all, -e utf8 on set `utf8`.
  corpus  every `pattern`/`pattern-esc` block of every tests/**/*.rxt
          (pcrec --list-source), with the block's own encoding and `i` flag,
          --features all; DEDUPLICATED on (pattern bytes, encoding, icase).

Classifiers (one per idea of generalize.md; each has a positive and a negative
control, run by --selftest, whose transcript is committed as selftest.txt):

  K1  I1  inner rare anchor: DFA engine, unanchored scan, and the byte-rate
          prior's rarest necessary byte r is NOT in the start set and is at
          least F x rarer than what the scan keys on today (the run's memchr
          byte, else the start set's summed mass). F = 1, 2, 8 reported;
          2 is the headline (UNMEASURED DEFAULT, D149).
  K2  I2  run-member pick: req_run shipped (len >= 2); sub-count where the
          shipped `log` or `weblog` analysis moves RX_REQ_BYTE.
  K3  I3  start marker instead of the reverse pass: RX_DFA_START reverse-pass
          and the req run starts every match (facts `req_run_maxoff` 0; the
          stamp's `@N` is the scan member's index, NOT the offset) -- a NECESSARY condition
          only (the run must also not recur inside a match; not decided here).
  K4  I4  handoff re-skip: RX_REQ_HANDOFF names a position and the artifact
          calls `<p>_ofsskip` (the state-0 skip re-run at the handoff).
  K5  I5  VM attempt opens on a context test: VM route with no prefilter and the
          attempt's first label reads subject[scan_position-1].
  K6  I6  possessify arms the shipped pass declines: a greedy single-atom
          quantifier (m >= 1) followed by `\\b` with atom in \\w or in \\W
          (arm B), or followed by a backreference whose group is closed,
          non-nullable and first-set-disjoint from the atom (arm R). VM route.
          Validated by compiling the possessified spelling: frames drop?
  K7  I7  trailed slot writes: VM, RX_SET in the matcher; split by FRAMELESS.
  K8  I8  frameless entry shapes already shipped ([CC-DIFF]): context count.
  K9  I9  bitmap class tests in the VM matcher (`_class_bitmapN[` reads).
  K10 I10 run counters in memory: framed VM matcher (RX_VM_FRAMELESS 0).
  K11 I11 seeded start component: the forward machine is SEEDED (a leading
          context assertion) on an unanchored scan; sub-count whose stage-3
          compile (lane/ssbuild3 tip) takes a first-* prefilter row.
  K12 I12 per-alternative streams: the pattern opens (after zero-width items)
          on an alternation of >= 2 pure literals sharing no necessary byte, and
          the sum over alternatives of each one's rarest byte mass is below half
          the start set's mass.
  K13 I13 mid-run multi-state stay set: in the forward premultiplied machine,
          a 1-LOCAL stay set (see stay_sets) of >= 2 non-accepting states, not
          containing state 0, with <= 32 exit bytes (UNMEASURED DEFAULT). The
          set containing state 0 is K11's start-component analogue.
  K14 I14 hybrid VM verification: RX_VM_PREFILTER hybrid, by LANG and NCAPS.
  K15 I15 lazy quantifier with resume frames on the VM route.

    PCREC=build/pcrec SS3=build-artrev/ss3src/build/pcrec \\
    BENCH=/path/pcrec-bench CORPUS=/path/worktree OUT=dir \\
    python3 census.py [--selftest] [--limit N] [--workers N]
"""
import argparse, collections, concurrent.futures as cf, glob, gzip, hashlib
import json, os, re, subprocess, sys

E = os.environ
PCREC = E.get("PCREC", "build/pcrec")
SS3 = E.get("SS3", "")
BENCH = E.get("BENCH", "/Users/fdicostanzo/pcrec-bench")
CORPUS = E.get("CORPUS", ".")
OUT = E.get("OUT", "build-artrev/gencensus")
NICE = ["nice", "-n", "10"]
TMO = 120

W = set(range(48, 58)) | set(range(65, 91)) | set(range(97, 123)) | {95}


def prior():
    p = {}
    for ln in open(os.path.join(CORPUS, "tests/findings/default_ppm.tsv")):
        f = ln.split()
        if len(f) == 2 and f[0].isdigit():
            p[int(f[0])] = int(f[1])
    return p


PRIOR = None


def dec_field(b):
    """pcrec_sb_field's escape vocabulary, inverted (src/core/sb.c)."""
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


def bench_pop():
    rows = []
    for p in sorted(glob.glob(os.path.join(BENCH, "bench", "*", "patterns", "*.rx"))):
        sb = p.split(os.sep)[-3]
        b = open(p, "rb").read().rstrip(b"\n")
        if b and b"\x00" not in b:
            rows.append(dict(pop="bench", id="%s/%s" % (sb, os.path.basename(p)[:-3]),
                             enc="utf8" if sb == "utf8" else "byte", icase=False, pat=b))
    return rows


def corpus_pop():
    rows, seen = [], set()
    files = []
    for root, _d, fs in os.walk(os.path.join(CORPUS, "tests")):
        files += [os.path.join(root, f) for f in fs if f.endswith(".rxt")]
    for f in sorted(files):
        r = subprocess.run([PCREC, "--list-source", f], capture_output=True, timeout=TMO)
        if r.returncode != 0:
            continue
        rel = os.path.relpath(f, CORPUS)
        for ln in r.stdout.split(b"\n"):
            if ln.startswith(b"#section"):
                break
            if not ln or ln.startswith(b"#"):
                continue
            fl = ln.split(b"\t")
            if len(fl) < 9 or fl[0] not in (b"pattern", b"pattern-esc"):
                continue
            pat = dec_field(fl[4])
            if not pat or b"\x00" in pat:
                continue
            enc = "utf8" if fl[8].decode() == "utf8" else "byte"
            icase = "i" in fl[5].decode()
            key = (pat, enc, icase)
            if key in seen:
                continue
            seen.add(key)
            rows.append(dict(pop="corpus", id="%s:%s" % (rel, fl[1].decode()),
                             enc=enc, icase=icase, pat=pat))
    return rows


def opts(r, extra=()):
    o = ["--features", "all"]
    if r["icase"]: o.append("-i")
    if r["enc"] == "utf8": o += ["-e", "utf8"]
    return o + list(extra)


def run(cmd):
    try:
        p = subprocess.run(NICE + cmd, capture_output=True, timeout=TMO)
    except subprocess.TimeoutExpired:
        return None, "timeout"
    if p.returncode != 0:
        return None, p.stderr.decode("utf8", "replace").split("\n")[0][:100]
    return p.stdout.decode("latin-1"), None


def compile_c(r, pat=None, binary=None, extra=()):
    return run([binary or PCREC, "-p", "rx"] + opts(r, extra) + ["-o", "-", "--pattern", pat or r["pat"]])


def facts(r):
    out, err = run([PCREC, "--emit-facts=" + r["enc"]] + opts(r) + ["--pattern", r["pat"]])
    if out is None:
        return None, err
    f, d, sect = {}, {}, None
    for ln in out.split("\n"):
        if ln.startswith("#section"):
            sect = ln.split()[1]; continue
        if ln.startswith("#") or not ln:
            continue
        x = ln.split("\t")
        if sect == "facts" and len(x) >= 7:
            f[x[1]] = x[6]
        elif sect == "decisions" and len(x) >= 3:
            d[x[1].replace("RX_", "")] = x[2].strip('"')
    return (f, d), None


# ---- emitted-text readers -------------------------------------------------

def bitset(v):
    """start_set's `count:hex` -> set of bytes; None for nullable/absent."""
    if not v or ":" not in v:
        return None
    hx = v.split(":", 1)[1]
    if len(hx) != 64:
        return None
    bs = bytes.fromhex(hx)
    return {b for b in range(256) if (bs[b >> 3] >> (b & 7)) & 1}


def intlist(v):
    try:
        return [int(x) for x in v.split(",") if x != ""]
    except ValueError:
        return []


def vm_matcher(c):
    m = re.search(r"ptrdiff_t rx_match_anchored\(.*?\n#undef RX_TRAIL", c, re.S)
    return m.group(0) if m else ""


def first_label_reads_prev(body):
    m = re.search(r"\nrx_L0:[^\n]*\n(.*?)\nrx_L\d+:", body, re.S)
    return bool(m and re.search(r"scan_position ?- ?1\]", m.group(1)))


def arr(c, name):
    m = re.search(r"%s\[(\d+)\] = \{(.*?)\};" % re.escape(name), c, re.S)
    if not m:
        return None
    return [int(x) for x in re.findall(r"\d+", m.group(2))]


def stay_sets(c):
    """K13/K11: 1-LOCAL STAY SETS of the FORWARD premultiplied machine (A09's
    dfa_dump.py table reading, generalized). A stay set C is grown from a seed
    state along every transition on a WIDE class (>= 4 bytes) to a live
    non-accepting state, then VALIDATED: for every byte class, the states of C
    that stay inside C all go to ONE state (so the state after a run inside C
    is determined by the last byte -- 'the predecessor decides', rvA09 L3).
    Exits = the bytes of every class on which ANY state of C leaves C (A09's
    406 leaves on d/r/t/u where 435 stays: still an exit byte for the skip). Narrow-class transitions
    (a keyword's first letter, a newline) are exits even when the target later
    returns -- a stay set is not an SCC, which is why the first version of this
    reader (Tarjan SCCs) read A09's keyword-prefix states into one 44-state
    component and found nothing. Every member must itself SELF-LOOP on a wide
    class (a run state, as OPT-3's stay loop needs); without that rule each
    keyword-prefix state formed its own {prefix, 406, 435} set (24 on A09). Returns dict(start=..., mid=[...]) or None."""
    bc = arr(c, "rx_forward_byte_class")
    ns = arr(c, "rx_forward_next_state")
    acc = arr(c, "rx_forward_is_accepting")
    if not bc or not ns or not acc or len(bc) != 256:
        return None
    nc = max(bc) + 1
    if len(ns) % nc:
        return None
    abc = arr(c, "rx_forward_is_accepting_by_class") or [0] * len(ns)
    width = collections.Counter(bc)
    live = lambda t: t != 65535 and t < len(ns)
    accepting = lambda s: acc[s] or any(abc[s + j] for j in range(nc))

    def loops(t):
        return any(ns[t + j] == t and width[j] >= 4 for j in range(nc))

    def grow(seed):
        if not loops(seed):
            return None
        C, todo = {seed}, [seed]
        while todo:
            s = todo.pop()
            for j in range(nc):
                t = ns[s + j]
                if width[j] >= 4 and live(t) and t not in C and not accepting(t) and loops(t):
                    C.add(t); todo.append(t)
            if len(C) > 16:
                return None
        exits = 0
        for j in range(nc):
            tg = {ns[s + j] for s in C}
            inside = {t for t in tg if t in C}
            if len(inside) > 1:
                return None
            if tg - C:
                exits += width[j]
        return dict(states=frozenset(C), size=len(C), exits=exits)

    seen, mid, start = set(), [], None
    for s in range(0, len(ns), nc):
        if accepting(s):
            continue
        g = grow(s)
        if not g or g["size"] < 2 or g["states"] in seen:
            continue
        seen.add(g["states"])
        if 0 in g["states"]:
            start = g
        else:
            mid.append(g)
    return dict(start=start, mid=mid)


# ---- a minimal pattern reader for K6 / K12 / K15 --------------------------

class Unparsed(Exception):
    pass


def esc_set(ch):
    D = set(range(48, 58)); S = {9, 10, 11, 12, 13, 32}
    return {"w": W, "d": D, "s": S, "W": set(range(256)) - W,
            "D": set(range(256)) - D, "S": set(range(256)) - S}.get(ch)


def parse(p, icase):
    """Pattern bytes -> nested list of items. Item kinds: ('set', bytes),
    ('zw', name), ('bref', n), ('grp', capidx|None, [alts]), ('rep', item, m, M,
    mode). Raises Unparsed on anything outside the small grammar (counted)."""
    s = p.decode("latin-1")
    if "(?x" in s or "(*" in s or "\\Q" in s or "(?#" in s:
        raise Unparsed()
    pos = [0]; ncap = [0]

    def fold(st):
        if not icase:
            return st
        return st | {b ^ 32 for b in st if 65 <= (b | 32) - 32 <= 90 or 97 <= b <= 122}

    def cls():
        i = pos[0] + 1; neg = False; out = set()
        if i < len(s) and s[i] == "^":
            neg = True; i += 1
        first = True
        while i < len(s) and (s[i] != "]" or first):
            first = False
            c = s[i]
            if c == "[":
                raise Unparsed()
            if c == "\\":
                i += 1
                if i >= len(s): raise Unparsed()
                e = esc_set(s[i])
                if e is not None:
                    out |= e; i += 1; continue
                lo = {"n": 10, "t": 9, "r": 13, "f": 12, "v": 11}.get(s[i])
                if lo is None:
                    if s[i] == "x" and i + 2 < len(s) and re.match(r"[0-9a-fA-F]{2}", s[i+1:i+3]):
                        lo = int(s[i+1:i+3], 16); i += 2
                    elif s[i].isalnum():
                        raise Unparsed()
                    else:
                        lo = ord(s[i])
                i += 1
            else:
                lo = ord(c); i += 1
            if i + 1 < len(s) and s[i] == "-" and s[i + 1] != "]":
                hi = s[i + 1]
                if hi == "\\":
                    raise Unparsed()
                out |= set(range(lo, ord(hi) + 1)); i += 2
            else:
                out.add(lo)
        if i >= len(s):
            raise Unparsed()
        pos[0] = i + 1
        out = fold(out)
        return set(range(256)) - out if neg else out

    def atom():
        c = s[pos[0]]
        if c == "(":
            if s.startswith("(?:", pos[0]):
                pos[0] += 3; cap = None
            elif s.startswith("(?<", pos[0]) and not s.startswith("(?<=", pos[0]) and not s.startswith("(?<!", pos[0]):
                j = s.index(">", pos[0]); pos[0] = j + 1; ncap[0] += 1; cap = ncap[0]
            elif s.startswith("(?", pos[0]):
                raise Unparsed()
            else:
                pos[0] += 1; ncap[0] += 1; cap = ncap[0]
            alts = alternation()
            if pos[0] >= len(s) or s[pos[0]] != ")":
                raise Unparsed()
            pos[0] += 1
            return ("grp", cap, alts)
        if c == "[":
            return ("set", cls())
        if c == ".":
            pos[0] += 1; return ("set", set(range(256)) - {10})
        if c in "^$":
            pos[0] += 1; return ("zw", c)
        if c == "\\":
            n = s[pos[0] + 1] if pos[0] + 1 < len(s) else ""
            pos[0] += 2
            e = esc_set(n)
            if e is not None:
                return ("set", e)
            if n in "bBAzZG":
                return ("zw", n)
            if n.isdigit() and n != "0":
                return ("bref", int(n))
            m = {"n": 10, "t": 9, "r": 13, "f": 12, "v": 11}.get(n)
            if m is not None:
                return ("set", {m})
            if n == "x" and re.match(r"[0-9a-fA-F]{2}", s[pos[0]:pos[0]+2]):
                v = int(s[pos[0]:pos[0]+2], 16); pos[0] += 2; return ("set", fold({v}))
            if n.isalnum() or n == "":
                raise Unparsed()
            return ("set", {ord(n)})
        if c in "*+?{)|":
            raise Unparsed()
        pos[0] += 1
        return ("set", fold({ord(c)}))

    def quant(it):
        if pos[0] >= len(s):
            return it
        c = s[pos[0]]
        if c in "*+?":
            m, M = {"*": (0, None), "+": (1, None), "?": (0, 1)}[c]; pos[0] += 1
        elif c == "{":
            mm = re.match(r"\{(\d+)(,(\d*))?\}", s[pos[0]:])
            if not mm:
                return it
            m = int(mm.group(1)); M = m if mm.group(2) is None else (int(mm.group(3)) if mm.group(3) else None)
            pos[0] += len(mm.group(0))
        else:
            return it
        mode = "greedy"
        if pos[0] < len(s) and s[pos[0]] in "?+":
            mode = "lazy" if s[pos[0]] == "?" else "poss"; pos[0] += 1
        return ("rep", it, m, M, mode, pos[0] - (0 if mode == "greedy" else 1))

    def seq():
        items = []
        while pos[0] < len(s) and s[pos[0]] not in "|)":
            items.append(quant(atom()))
        return items

    def alternation():
        alts = [seq()]
        while pos[0] < len(s) and s[pos[0]] == "|":
            pos[0] += 1; alts.append(seq())
        return alts

    tree = alternation()
    if pos[0] != len(s):
        raise Unparsed()
    return tree


def first_info(item, groups):
    """(first byte set, nullable) of an item; None set = unknown (all)."""
    k = item[0]
    if k == "set":
        return item[1], False
    if k == "zw":
        return set(), True
    if k == "bref":
        return None, True
    if k == "rep":
        f, n = first_info(item[1], groups)
        return f, n or item[2] == 0
    if k == "grp":
        fs, nul = set(), False
        for a in item[2]:
            f, n = seq_first(a, groups)
            if f is None:
                return None, True
            fs |= f; nul = nul or n
        return fs, nul
    return None, True


def seq_first(items, groups):
    fs = set()
    for it in items:
        f, n = first_info(it, groups)
        if f is None:
            return None, True
        fs |= f
        if not n:
            return fs, False
    return fs, True


def walk_k6(tree):
    """K6: candidate (arm, rep-node) pairs. Follow = the next item at the same
    level, climbing out of UNQUANTIFIED groups when the rep is last."""
    groups, closed = {}, set()
    out = []

    def index_groups(alts):
        for a in alts:
            for it in a:
                n = it[1] if it[0] == "rep" else it
                if n[0] == "grp":
                    if n[1]:
                        groups[n[1]] = n
                    index_groups(n[2])
    index_groups(tree)

    def visit(alts, follow_stack, closed_before):
        for a in alts:
            for i, it in enumerate(a):
                nxt = a[i + 1] if i + 1 < len(a) else None
                if it[0] == "grp":
                    visit(it[2], [nxt] + follow_stack if nxt is not None else follow_stack, closed_before)
                    if it[1]:
                        closed_before.add(it[1])
                    continue
                if it[0] != "rep":
                    continue
                body = it[1]
                if body[0] == "grp":
                    visit(body[2], [], closed_before)  # quantified group: no climb
                    if body[1]:
                        closed_before.add(body[1])
                    continue
                if body[0] != "set" or it[4] != "greedy" or it[2] < 1 or it[3] == it[2]:
                    continue
                fol = nxt
                if fol is None:
                    fol = follow_stack[0] if follow_stack else None
                if fol is None:
                    continue
                X = body[1]
                if fol[0] == "zw" and fol[1] == "b" and (X <= W or not (X & W)):
                    out.append(("B", it))
                elif fol[0] == "bref" and fol[1] in closed_before and fol[1] in groups:
                    f, n = seq_first(groups[fol[1]][2][0], groups) if len(groups[fol[1]][2]) == 1 else first_info(groups[fol[1]], groups)
                    if f is not None and not n and not (f & X):
                        out.append(("R", it))
    visit(tree, [], closed)
    return out


def possessify_text(p, cands):
    s = p.decode("latin-1")
    for _arm, it in sorted(cands, key=lambda c: -c[1][5]):
        s = s[:it[5]] + "+" + s[it[5]:]
    return s.encode("latin-1")


def has_lazy_rep(tree):
    def v(alts):
        for a in alts:
            for it in a:
                if it[0] == "rep":
                    if it[4] == "lazy" and it[3] != it[2]:
                        return True
                    if it[1][0] == "grp" and v(it[1][2]):
                        return True
                elif it[0] == "grp" and v(it[2]):
                    return True
        return False
    return v(tree)


def lead_alternation(tree):
    """K12: the first non-zero-width item, if it is a group of >= 2 pure
    literal alternatives (each >= 2 bytes): their byte lists, else None."""
    if len(tree) != 1:
        return None
    for it in tree[0]:
        if it[0] == "zw":
            continue
        if it[0] != "grp" or len(it[2]) < 2:
            return None
        lits = []
        for a in it[2]:
            if len(a) < 2 or any(x[0] != "set" or len(x[1]) > 2 for x in a):
                return None
            lits.append([min(x[1]) for x in a])
        return lits
    return None


# ---- per-row census -------------------------------------------------------

def census_row(r):
    o = dict(pop=r["pop"], id=r["id"], enc=r["enc"], icase=int(r["icase"]),
             pat_sha=hashlib.sha1(r["pat"]).hexdigest()[:12])
    fd, err = facts(r)
    if fd is None:
        o["refused"] = err; return o
    f, d = fd
    c, err = compile_c(r)
    if c is None:
        o["refused"] = err; return o
    eng = d.get("ENGINE", ""); vpf = d.get("VM_PREFILTER", "")
    o.update(engine=eng, vm_prefilter=vpf, lang=d.get("VM_PREFILTER_LANG", ""),
             ncaps=d.get("NCAPS", ""), dfa_scan=d.get("DFA_SCAN", ""),
             dfa_pf=d.get("DFA_PREFILTER", ""), dfa_start=d.get("DFA_START", ""),
             req_byte=d.get("REQ_BYTE", ""), req_run=d.get("REQ_RUN", ""),
             handoff=d.get("REQ_HANDOFF", ""), vm_start=d.get("VM_START_SCAN", ""),
             frameless=d.get("VM_FRAMELESS", ""), shape=d.get("VM_ENTRY_SHAPE", ""))
    S = bitset(f.get("start_set", ""))
    req = intlist(f.get("req_set", "")) if f.get("req_set", "none") != "none" else []
    # K1
    k1 = 0
    if eng == "dfa" and o["dfa_scan"] == "unanchored" and req and S is not None:
        r_ = min(req, key=lambda b: (PRIOR.get(b, 2), -b))
        try:
            key = PRIOR.get(int(o["req_byte"]), 2) if o["req_run"] not in ("", "none") else sum(PRIOR.get(b, 2) for b in S)
        except ValueError:
            key = sum(PRIOR.get(b, 2) for b in S)
        if r_ not in S:
            ratio = key / max(1, PRIOR.get(r_, 2))
            k1 = 8 if ratio >= 8 else 2 if ratio >= 2 else 1 if ratio > 1 else 0
            o["k1_byte"] = r_
            o["k1_presence"] = int(bool(re.search(r"memchr\(subject \+ search_from, %d," % r_, c)))
    o["k1"] = k1
    # K2
    o["k2"] = int(o["req_run"] not in ("", "none"))
    if o["k2"]:
        mv = []
        for a in ("log", "weblog"):
            out, _e = run([PCREC, "-p", "rx"] + opts(r, ["--analysis", a]) + ["-o", "-", "--pattern", r["pat"]])
            m = re.search(r'#define RX_REQ_BYTE "([^"]*)"', out or "")
            if m and m.group(1) != o["req_byte"]:
                mv.append(a)
        o["k2_moves"] = ",".join(mv)
    # K3
    o["k3"] = int(o["dfa_start"] == "reverse-pass" and o["req_run"] not in ("", "none")
                  and f.get("req_run_maxoff") == "0")
    # K4
    o["k4"] = int(o["handoff"] not in ("", "none") and "_ofsskip(" in c)
    body = vm_matcher(c) if eng == "vm" else ""
    # K5
    o["k5"] = int(eng == "vm" and vpf == "none" and first_label_reads_prev(body))
    # K6
    o["k6"] = ""
    try:
        tree = parse(r["pat"], r["icase"])
        o["parsed"] = 1
    except (Unparsed, ValueError, IndexError):
        tree = None; o["parsed"] = 0
    if tree is not None and r["enc"] == "byte":
        cands = walk_k6(tree)
        if cands:
            o["k6"] = "".join(sorted({a for a, _ in cands}))
            if eng == "vm":
                pc, _e = compile_c(r, possessify_text(r["pat"], cands))
                o["k6_push_before"] = body.count("RX_PUSH(&&")
                if pc:
                    pb = vm_matcher(pc)
                    o["k6_push_after"] = pb.count("RX_PUSH(&&")
                    m = re.search(r"#define RX_VM_FRAMELESS (\d)", pc)
                    o["k6_frameless_after"] = m.group(1) if m else ""
    # K7-K10
    o["n_set"] = body.count("RX_SET(")
    o["n_push"] = body.count("RX_PUSH(&&")
    o["n_bitmap"] = len(re.findall(r"_class_bitmap\d+\[", body))
    # K11 / K13
    o["seeded"] = int("_forward_seed_state[" in c and o["dfa_scan"] == "unanchored")
    if o["seeded"] and SS3:
        sc, _e = compile_c(r, binary=SS3)
        m = re.search(r'#define RX_DFA_PREFILTER "([^"]*)"', sc or "")
        o["ss3_pf"] = m.group(1) if m else ""
    if d.get("DFA_TABLE") == "premultiplied":
        g = stay_sets(c)
        if g:
            st = g["start"]
            o["start_stay"] = "%d/%d" % (st["size"], st["exits"]) if st else ""
            o["k13"] = len([m for m in g["mid"] if m["exits"] <= 32])
            o["k13_any"] = len(g["mid"])
    # K12
    o["k12"] = 0
    if tree is not None and S is not None:
        lits = lead_alternation(tree)
        if lits and not (set(req) & set(b for l in lits for b in l)):
            streams = sum(min(PRIOR.get(b, 2) for b in l) for l in lits)
            o["k12"] = 2 if streams * 2 <= sum(PRIOR.get(b, 2) for b in S) else 1
    # K15
    o["k15"] = int(eng == "vm" and tree is not None and has_lazy_rep(tree) and o["n_push"] > 0)
    return o


CONTROLS = [
    # (classifier, expected, pattern, note)
    ("k1", "pos", rb"\bat (?:[A-Za-z_$][A-Za-z0-9_$]*\.){2,}[A-Za-z_$][A-Za-z0-9_$]*\((?:[A-Za-z0-9_$]+\.java:[0-9]+|Native Method|Unknown Source)\)", "A01"),
    ("k1", "neg", rb"\bat [a-z]+", "rarest necessary byte is in the run/start"),
    ("k2", "pos", rb"\bat (?:[A-Za-z_$][A-Za-z0-9_$]*\.){2,}[A-Za-z_$][A-Za-z0-9_$]*\((?:[A-Za-z0-9_$]+\.java:[0-9]+|Native Method|Unknown Source)\)", "A01 (run 'at ')"),
    ("k2", "neg", rb"[a-z]+@[0-9]", "one-byte requirement, no run"),
    ("k3", "pos", rb"\bat (?:[A-Za-z_$][A-Za-z0-9_$]*\.){2,}[A-Za-z_$][A-Za-z0-9_$]*\((?:[A-Za-z0-9_$]+\.java:[0-9]+|Native Method|Unknown Source)\)", "A01"),
    ("k3", "neg", rb"[a-z]+@example", "run not at offset 0"),
    ("k4", "pos", rb"\bat (?:[A-Za-z_$][A-Za-z0-9_$]*\.){2,}[A-Za-z_$][A-Za-z0-9_$]*\((?:[A-Za-z0-9_$]+\.java:[0-9]+|Native Method|Unknown Source)\)", "A01"),
    ("k4", "neg", rb"\b(?:ERROR|FATAL|CRIT)\b.{0,200}?\b(?:timeout|timed out|refused|denied|unreachable)\b", "A09 (no handoff)"),
    ("k5", "pos", rb"\b(\w+)\b\s+\1\b", "A07"),
    ("k5", "neg", rb"(\w+)\s+\1\b", "no leading context test"),
    ("k6", "pos", rb"\b(\w+)\b\s+\1\b", "A07 (arms B and R)"),
    ("k6", "neg", rb"([a-z]+)\B[a-z]", "\\B follow: give-back can pass"),
    ("k6", "neg", rb"\b(\w*)\b\s+\1", "m = 0: the zero-iteration retreat can pass \\b"),
    ("k7", "pos", rb"(abc)(def)", "frameless with slot writes"),
    ("k7", "neg", rb"abc", "no captures"),
    ("k8", "pos", rb"(abc)(def)", "frameless"),
    ("k8", "neg", rb"\b(\w+)\b\s+\1\b", "framed"),
    ("k9", "pos", rb"\b(\w+)\b\s+\1\b", "A07"),
    ("k9", "neg", rb"(abc)\1", "no class test"),
    ("k10", "pos", rb"\b(\w+)\b\s+\1\b", "framed"),
    ("k10", "neg", rb"(abc)(def)", "frameless"),
    ("k11", "pos", rb"\b(?:ERROR|FATAL|CRIT)\b.{0,200}?\b(?:timeout|timed out|refused|denied|unreachable)\b", "A09 (seeded; stage 3 moves it)"),
    ("k11", "neg", rb"abc[0-9]+", "no leading context"),
    ("k12", "pos", rb"\b(?:ERROR|FATAL|CRIT)\b.{0,200}?\b(?:timeout|timed out|refused|denied|unreachable)\b", "A09"),
    ("k12", "neg", rb"\b(?:foo|bar)baz", "a common necessary run"),
    ("k13", "pos", rb"\b(?:ERROR|FATAL|CRIT)\b[^\n]*\b(?:timeout|refused)\b", "A09's after-level shape, DFA engine"),
    ("k13", "neg", rb"abc[0-9]+def", "no multi-state component"),
    ("k14", "pos", rb"\b(?:ERROR|FATAL|CRIT)\b.{0,200}?\b(?:timeout|timed out|refused|denied|unreachable)\b", "A09"),
    ("k14", "neg", rb"\b(\w+)\b\s+\1\b", "plain VM"),
    ("k15", "pos", rb"\b(?:ERROR|FATAL|CRIT)\b.{0,200}?\b(?:timeout|timed out|refused|denied|unreachable)\b", "A09"),
    ("k15", "neg", rb"a.*b(c)", "greedy only"),
]


def fires(k, o):
    if k == "k1": return o.get("k1", 0) >= 2
    if k == "k2": return o.get("k2", 0) == 1
    if k in ("k3", "k4", "k5", "k15"): return o.get(k, 0) == 1
    if k == "k6": return o.get("k6", "") != "" and o.get("engine") == "vm"
    if k == "k7": return o.get("engine") == "vm" and o.get("n_set", 0) > 0
    if k == "k8": return o.get("engine") == "vm" and o.get("frameless") == "1"
    if k == "k9": return o.get("engine") == "vm" and o.get("n_bitmap", 0) > 0
    if k == "k10": return o.get("engine") == "vm" and o.get("frameless") == "0"
    if k == "k11": return o.get("seeded", 0) == 1
    if k == "k12": return o.get("k12", 0) >= 1
    if k == "k13": return o.get("k13", 0) > 0
    if k == "k14": return o.get("vm_prefilter") == "hybrid"
    raise KeyError(k)


def selftest():
    bad = 0
    for k, exp, pat, note in CONTROLS:
        o = census_row(dict(pop="control", id=k, enc="byte", icase=False, pat=pat))
        got = fires(k, o)
        ok = got == (exp == "pos")
        bad += not ok
        extra = {x: o.get(x) for x in ("engine", "k1", "k1_byte", "k6", "k6_push_before", "k6_push_after",
                                         "k6_frameless_after", "ss3_pf", "start_stay", "k13", "k12", "frameless",
                                         "n_set", "n_bitmap", "lang", "ncaps") if o.get(x) not in (None, "")}
        print("%-4s %-3s %-4s %s  [%s]  %s" % (k, exp, "OK" if ok else "FAIL", pat.decode("latin-1")[:60], note,
                                                 json.dumps(extra, sort_keys=True)))
    print("selftest: %d controls, %d failed" % (len(CONTROLS), bad))
    return bad


def summarize(rows):
    L = []
    for pop in ("corpus", "bench"):
        R = [o for o in rows if o["pop"] == pop]
        ok = [o for o in R if "refused" not in o]
        vm = [o for o in ok if o.get("engine") == "vm"]
        dfa = [o for o in ok if o.get("engine") == "dfa"]
        L.append("## %s: %d patterns, %d compiled (%d refused/timeout), dfa %d, vm %d (hybrid %d); "
                 "pattern-reader parsed %d" % (pop, len(R), len(ok), len(R) - len(ok), len(dfa), len(vm),
                                               len([o for o in vm if o.get('vm_prefilter') == 'hybrid']),
                                               len([o for o in ok if o.get('parsed')])))
        c = lambda pred: len([o for o in ok if pred(o)])
        L.append("K1  I1 inner rare anchor (dfa unanch): >=1x %d, >=2x %d, >=8x %d; of >=2x, already presence-checked %d"
                 % (c(lambda o: o.get("k1", 0) >= 1), c(lambda o: o.get("k1", 0) >= 2), c(lambda o: o.get("k1", 0) >= 8),
                    c(lambda o: o.get("k1", 0) >= 2 and o.get("k1_presence"))))
        L.append("K2  I2 run-bearing %d; pick moved by log %d, by weblog %d, by either %d"
                 % (c(lambda o: o.get("k2")), c(lambda o: "log" in o.get("k2_moves", "").split(",")),
                    c(lambda o: "weblog" in o.get("k2_moves", "").split(",")), c(lambda o: o.get("k2_moves"))))
        L.append("K3  I3 reverse-pass + run@0 (necessary cond.) %d (dfa %d, hybrid %d); all reverse-pass %d"
                 % (c(lambda o: o.get("k3")), c(lambda o: o.get("k3") and o.get("engine") == "dfa"),
                    c(lambda o: o.get("k3") and o.get("engine") == "vm"), c(lambda o: o.get("dfa_start") == "reverse-pass")))
        L.append("K4  I4 handoff + ofsskip %d (handoff any %d)" % (c(lambda o: o.get("k4")),
                 c(lambda o: o.get("handoff") not in ("", "none", None))))
        L.append("K5  I5 VM no-prefilter attempt opens on a context test %d (of VM no-prefilter %d); by VM_START_SCAN: %s"
                 % (c(lambda o: o.get("k5")), c(lambda o: o.get("engine") == "vm" and o.get("vm_prefilter") == "none"),
                    dict(collections.Counter(o.get("vm_start") for o in ok if o.get("k5")))))
        k6 = [o for o in vm if o.get("k6")]
        L.append("K6  I6 possessify arms (VM): %d (arm B only %d, R only %d, both %d); frames drop on the possessified "
                 "spelling %d; becomes frameless %d; dfa-route rows with a candidate %d (frames moot)"
                 % (len(k6), len([o for o in k6 if o["k6"] == "B"]), len([o for o in k6 if o["k6"] == "R"]),
                    len([o for o in k6 if o["k6"] == "BR"]),
                    len([o for o in k6 if o.get("k6_push_after", 10**9) < o.get("k6_push_before", 0)]),
                    len([o for o in k6 if o.get("k6_frameless_after") == "1"]),
                    c(lambda o: o.get("k6") and o.get("engine") == "dfa")))
        L.append("K7  I7 VM matcher with RX_SET %d (frameless %d, framed %d)"
                 % (len([o for o in vm if o.get("n_set", 0) > 0]),
                    len([o for o in vm if o.get("n_set", 0) > 0 and o.get("frameless") == "1"]),
                    len([o for o in vm if o.get("n_set", 0) > 0 and o.get("frameless") == "0"])))
        L.append("K8  I8 frameless VM %d; entry shapes %s" % (len([o for o in vm if o.get("frameless") == "1"]),
                 dict(collections.Counter(o.get("shape") for o in vm))))
        L.append("K9  I9 VM matcher with bitmap class tests %d (tests total %d)"
                 % (len([o for o in vm if o.get("n_bitmap", 0) > 0]), sum(o.get("n_bitmap", 0) for o in vm)))
        L.append("K10 I10 framed VM (counters in run->) %d" % len([o for o in vm if o.get("frameless") == "0"]))
        sd = [o for o in ok if o.get("seeded")]
        L.append("K11 I11 seeded unanchored forward machine %d (dfa %d, hybrid %d); stage-3 takes first-*: %d; "
                 "start state in a >=2-state 1-local stay set: %d"
                 % (len(sd), len([o for o in sd if o.get("engine") == "dfa"]), len([o for o in sd if o.get("engine") == "vm"]),
                    len([o for o in sd if o.get("ss3_pf", "").startswith("first-")]),
                    len([o for o in sd if o.get("start_stay")])))
        L.append("K12 I12 leading literal alternation, no shared necessary byte: %d; streams < half the start-set mass %d"
                 % (c(lambda o: o.get("k12", 0) >= 1), c(lambda o: o.get("k12", 0) == 2)))
        L.append("K13 I13 mid-run 1-local stay set (>=2 states, <=32 exit bytes): %d artifacts (%d sets); any "
                 "exit width: %d" % (c(lambda o: o.get("k13", 0) > 0), sum(o.get("k13", 0) for o in ok),
                                                     c(lambda o: o.get("k13_any", 0) > 0)))
        hy = [o for o in vm if o.get("vm_prefilter") == "hybrid"]
        L.append("K14 I14 hybrids %d; by lang %s; ncaps==1 %d (count-collapsed and ncaps==1 %d)"
                 % (len(hy), dict(collections.Counter(o.get("lang") for o in hy)),
                    len([o for o in hy if o.get("ncaps") == "1"]),
                    len([o for o in hy if o.get("ncaps") == "1" and o.get("lang") == "count-collapsed"])))
        L.append("K15 I15 VM lazy quantifier with frames %d" % c(lambda o: o.get("k15")))
        L.append("")
    return "\n".join(L)


def main():
    global PRIOR
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    PRIOR = prior()
    if a.selftest:
        sys.exit(1 if selftest() else 0)
    os.makedirs(OUT, exist_ok=True)
    pop = bench_pop() + corpus_pop()
    if a.limit:
        pop = pop[:a.limit]
    rows = []
    with cf.ThreadPoolExecutor(a.workers) as ex, open(os.path.join(OUT, "progress.log"), "w") as pl:
        for i, o in enumerate(ex.map(census_row, pop)):
            rows.append(o)
            if i % 100 == 0:
                pl.write("%d/%d\n" % (i, len(pop))); pl.flush()
    keys = sorted({k for o in rows for k in o})
    with gzip.open(os.path.join(OUT, "rows.tsv.gz"), "wt") as fh:
        fh.write("\t".join(keys) + "\n")
        for o in rows:
            fh.write("\t".join(str(o.get(k, "")) for k in keys) + "\n")
    s = summarize(rows)
    open(os.path.join(OUT, "summary.txt"), "w").write(s + "\n")
    print(s)


if __name__ == "__main__":
    main()
