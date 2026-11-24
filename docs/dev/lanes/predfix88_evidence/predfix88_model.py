#!/usr/bin/env python3
# Lane predfix88 (2026-11-23): the successor evidence model for review r88 of the fold predfold1123b. DESIGN
# EVIDENCE ONLY; rules nothing. It succeeds docs/dev/lanes/predfold1123b_evidence/predfold1123b_model.py.
#
# METHOD. predfold1123b's model is LOADED unchanged: it is executed up to its line "the checks" (it loads predfix86's
# and, through it, the older engines). Then the R88 extensions act, each switched by X8[0] (on for the documents now;
# off for the starting commit's documents under predfold1123b's engine: SWEEP's control):
#   NESTED    (B8) a program whose own macro passes a PATTERN parameter on to another macro is refused LOUDLY as "not
#             modelled" (the loaded engine lost every label there, silently).
#   EXPRARG   (B8) a read through a binding written inside an EXPRESSION argument (`B(A SEQ /x/) & (A.h: ..)`) is
#             refused as "not modelled" (the loaded engine refused it on the reversed argument-default ground).
#   SAMELIST  (B8) a caller's same-name list `[(=) = A]` / `[(=h) = A]` takes A's label as its own (the loaded
#             engine renamed the list's name and refused it).
#   SPOTON    (A10, the manager's reading) a label is ON the spot it is written directly around: a body's
#             `[p = rx SEQ /x/]` makes no label on the argument's spot (condition 4 no longer refuses it).
#   MSGS      (B8) refusals that named the wrong mechanism are re-worded: the caller's own label then `A.h`
#             (condition 4), a call's name with nothing exported.
# Every regex the model matches with is built mechanically from the program text; the array-count lowering
# (ARRAYCOUNT) is built from the repeat head's text in library.md and run through libpcre2 (ctypes, the installed
# library, never read: D181).
#
# Run (W = the worktree; any cwd):  timeout 1800 python3 -I -B W/docs/dev/lanes/predfix88_evidence/predfix88_model.py
# Its verdict is its LAST LINE, `predfix88_model: N checks, F failed`; it EXITS NON-ZERO iff that line reports one.
# PREDFIX88_SABOTAGE=pN: one deliberately wrong rule, fact or document text; its target check must FAIL.
# PREDFIX88_SABOTAGE=all: every plant in turn (a subprocess each, a per-unit timeout naming the plant).
# PREDFIX88_LIGHT=1 skips SUCCESSOR. `--succ MODEL PIN` (internal): one earlier model run with library.md served
# from PIN (SUCCESSOR's runner; nested model runs inside it are routed the same way, each to its own pin).
import builtins
import ctypes
import hashlib
import io
import os
import re
import subprocess
import sys
import time

HERE8 = os.path.dirname(os.path.abspath(__file__))
LANES8 = os.path.normpath(os.path.join(HERE8, ".."))
W8 = os.path.normpath(os.path.join(HERE8, "..", "..", "..", ".."))
LIB8 = os.path.join(W8, "docs", "design", "predicates", "library.md")
UNIT_TIMEOUT8 = 120                                           # seconds per plant or per re-run model (B9)

# Each earlier in-force model and the commit its library is served from (B1): the commit that committed its .out,
# the library its own load-time readers were written against (its lane's start commit fails at load for predbound:
# the report). PINNED by hash, never a branch name.
PINS8 = {
    "predfold1123b": "d82b1ad36", "predfix86": "3d38aa9f8", "predfold1123": "69cb9a344", "predfix84": "97549667e",
    "predspot": "e451772d4", "predfix83": "595ff0d6b", "preddef": "ed37dc43a", "predfix82": "b5ed9b10d",
    "predcall": "6f1fe4e84", "predref": "9518f758e", "predbound": "1c52080a4", "predfix77": "1c768eb40",
    "predarr": "5133528c6", "predscope": "6d2dd2a0e",
}
LIGHTENV8 = {"predfold1123b": "PREDFOLD1123B_LIGHT", "predfix86": "PREDFIX86_LIGHT", "predfold1123": "PREDFOLD_LIGHT",
             "predfix84": "PREDFIX84_LIGHT", "predspot": "PREDSPOT_LIGHT"}


def _git8(rel, rev):
    return subprocess.run(["git", "-C", W8, "show", "%s:%s" % (rev, rel)], capture_output=True, text=True,
                          check=True).stdout


# ================================================================== SUCCESSOR's runner (a mode of its own)
if len(sys.argv) == 4 and sys.argv[1] == "--succ":
    import runpy
    mpath, pin = os.path.abspath(sys.argv[2]), sys.argv[3]
    libtxt = _git8("docs/design/predicates/library.md", pin)
    _open0 = builtins.open

    def _op(p, *a, **k):
        if isinstance(p, (str, os.PathLike)) and os.path.abspath(os.fsdecode(p)) == LIB8 and \
                "w" not in (a[0] if a else k.get("mode", "r")):
            return io.StringIO(libtxt)
        return _open0(p, *a, **k)
    builtins.open = _op
    io.open = _op
    _run0, _popen0 = subprocess.run, subprocess.Popen

    def _route(cmd):
        """A nested run of an earlier model is routed through this runner with ITS OWN pin."""
        if isinstance(cmd, (list, tuple)):
            for i_, a_ in enumerate(cmd):
                mm_ = re.search(r"(\w+)_model\.py$", str(a_))
                if mm_ and mm_.group(1) in PINS8:
                    return [sys.executable, "-I", "-B", os.path.abspath(__file__), "--succ",
                            os.path.abspath(str(a_)), PINS8[mm_.group(1)]] + list(cmd[i_ + 1:])
        return cmd

    subprocess.run = lambda cmd, *a, **k: _run0(_route(cmd), *a, **k)

    class _P(_popen0):
        def __init__(self, cmd, *a, **k):
            super().__init__(_route(cmd), *a, **k)
    subprocess.Popen = _P
    sys.argv = [mpath]
    runpy.run_path(mpath, run_name="__main__")
    sys.exit(0)

SAB8 = set(x for x in os.environ.get("PREDFIX88_SABOTAGE", "").split(",") if x)
LIGHT8 = os.environ.get("PREDFIX88_LIGHT") == "1"
START8 = "b63928b48"                                          # this lane's starting commit (lane/predfix88), PINNED


def s8(n):
    return n in SAB8


PLANTS8 = [   # (plant, its target check, what it plants: each changes the ENGINE, the evidence or a document read)
    ("p1", "CONTROL", "the control's python `re` for `repeat(D, 3, _)` written `(?:\\d){3}`"),
    ("p2", "CALLFORMS", "a positional entry after a named one accepted"),
    ("p3", "CALLFORMS", "a default naming a LATER parameter accepted, bound to that parameter's value"),
    ("p4", "CALLFORMS", "call-forms line 3 in core.md altered (\"never a later one\" dropped)"),
    ("p5", "ARRAYCOUNT", "a default naming an earlier parameter read as its TEXT (a second mention of the array)"),
    ("p6", "REPEAT", "`_` taken as \"use the default\" (call-forms line 4 undone)"),
    ("p7", "UNSPEC", "`_` for a count's lower bound read as 1, not 0"),
    ("p8", "UNSPEC", "the overlay sentence in core.md made the rule (\"It is not that the rule gives none\" dropped)"),
    ("p9", "COUNT", "libpcre2 run on `a{0,}` where the record's run reads `a{,}`"),
    ("p10", "SHORTHAND", "condition 4 off: the shorthand also through a spot the body labels"),
    ("p11", "SHORTHAND", "the shorthand label exported (A5's reading undone: `pub.A.h` legal through the sugar)"),
    ("p12", "SHORTHAND", "condition 1 off: a binding used twice in the caller's text takes the shorthand"),
    ("p13", "NOLABEL", "`_:` on a spot written out as the blank mark `[_ = v]` again (reading (a))"),
    ("p14", "NOLABEL", "label-omitted's rule sentence in core.md reversed to the blank mark"),
    ("p15", "STACK", "stacked labels read in nesting order: the outer one passes only what the inner one exports"),
    ("p16", "STACK", "a blank `_` in a stack closes the whole spot (the other label dropped with it)"),
    ("p17", "STACKCHAIN", "two public stacked labels chain (`n.m.d` legal, candidate (b) taken)"),
    ("p18", "SPOTON", "a label over a wider spot counted as on the argument's spot (A10's reading undone)"),
    ("p19", "OWNERBODY", "the owner's two-label body: `_:` written out as the blank mark (his body refused)"),
    ("p20", "LIBLINES", "padded_to's zeros `0*` read as `0?` (library.md's body altered as read)"),
    ("p21", "TABLE", "the ownership table's header: `used alone` and `labelled` swapped in core.md as read"),
    ("p22", "TABLE", "the table's column sentence: the alone and labelled bodies swapped in core.md as read"),
    ("p23", "TABLE", "a sixth row added to the table in core.md as read"),
    ("p24", "TABLE", "one cell of the table changed to the opposite legality in core.md as read"),
    ("p25", "NESTED", "the loud refusal off: a body passing its pattern parameter on runs silently"),
    ("p26", "SAMELIST", "the same-name list's fix off (the loaded engine's rename)"),
    ("p27", "CAPNAME", "`_` into a capturing group's whole-name hole written `(?:...)`"),
    ("p28", "EXPAND", "argument-default's written-out form read as `B([_ = A])` (core.md altered as read)"),
    ("p29", "READINGS", "a reading's run moved: the shorthand set on EVERY spot of a body using the argument alone and "
                        "labelled"),
    ("p30", "SWEEP", "one printed answer of the documents moved under an unchanged key (the same-key arm)"),
    ("p31", "SWEEP", "predfix84's stale `rx.repeat(rx.digit, 3)` declaration restored and a wrong line printed"),
    ("p32", "NULLABLE", "one program with a nullable loop run (`rx.repeat(/a?/)`)"),
    ("p33", "SUCCESSOR", "one declared red's text altered"),
    ("p34", "SUCCESSOR", "a load-time traceback declared superseded"),
    ("p35", "QUOTES", "core/labels/rule's line 5 altered in the base piece only (its details copies kept)"),
    ("p36", "DOC", "a formatted line altered"),
    ("p37", "DOC", "a line looked for under another piece's tag"),
    ("p38", "NAMEGRID", "one decided cell's expected verdict flipped"),
    ("p39", "NAMEGRID", "an undecided cell's open slug (both-uses) dropped from the documents (core.md altered as read)"),
]
HEAVY8 = {"SUCCESSOR"}
STRICT8 = re.compile(r"^predfix88_model: (\d+) checks, (\d+) failed(?: \(([^)]*)\))?$")
if "all" in SAB8:                                            # the plant runner: each plant alone, a subprocess each
    rows, notc = [], 0
    for pn, target, what in PLANTS8:
        env = {k: v for k, v in os.environ.items()}
        env["PREDFIX88_SABOTAGE"] = pn
        if target not in HEAVY8:
            env["PREDFIX88_LIGHT"] = "1"
        t0 = time.time()
        try:
            r = subprocess.run([sys.executable, "-I", "-B", os.path.abspath(__file__)], capture_output=True,
                               text=True, env=env, timeout=UNIT_TIMEOUT8 * (8 if target in HEAVY8 else 1))
            out_, rc_ = r.stdout + r.stderr, r.returncode
        except subprocess.TimeoutExpired:
            out_, rc_ = "TIMEOUT: plant %s did not finish in its unit time" % pn, None
        lines = out_.rstrip("\n").split("\n")
        last = lines[-1]
        mm = STRICT8.match(last)
        fl_ = next((x for x in lines if x.startswith("FAIL %s:" % target)), "")
        tb = any(x.startswith("Traceback") or re.search(r"\bCRASH [A-Z]\w*(Error|Exception)\b", x) for x in lines)
        ok = bool(fl_) and not tb and rc_ not in (0, None) and bool(mm) and target in (mm.group(3) or "").split(", ")
        notc += not ok
        rows.append((pn, target, what, ok))
        print("%s -> %s (%s): %s (%.0f s)" % (pn, target, what, "caught" if ok else "NOT CAUGHT", time.time() - t0))
        print("   last line: %s" % last)
        print("   its FAIL line: %s" % fl_[:300], flush=True)
    print("predfix88_sabotage: %d plants, %d not caught%s" % (
        len(rows), notc, " (each plant turned its target check FAIL, no traceback, no engine crash)" if not notc
        else ""))
    sys.exit(1 if notc else 0)


# ================================================================== the LOADER: predfold1123b's engines, unchanged
for v in list(os.environ):
    if v.startswith("PREDFOLD1123B_"):
        os.environ.pop(v, None)
P1123B = os.path.join(LANES8, "predfold1123b_evidence", "predfold1123b_model.py")
_srcB = builtins.open(P1123B, encoding="utf-8").read()
_cutB = re.search(r"^# =+ the checks$", _srcB, re.M).start()
_file8 = __file__
__file__ = P1123B                                            # noqa: F811  (the loaded code finds its siblings by it)
exec(compile(_srcB[:_cutB], P1123B, "exec"), globals())      # noqa: S102  (predfold1123b's definitions, unchanged)
__file__ = _file8
LINES.clear()
RUN.clear()
P88F = dict(prog=prog, two_sources=two_sources, placements=placements, shorthand=shorthand, unspec_body=unspec_body)
X8 = [True]


def x8():
    return X8[0]


# ================================================================== the R88 extensions (lane predfix88)
NOTMOD8 = "not modelled (predfix88's known limits): "


def _plain_heads(binds):
    out = {}
    for b in binds:
        h = head_of(b)
        if h and not any(k == "label" for _, _, k in h[1]):
            out[h[0]] = (h[1], h[2])
    return out


def _arg_val(a):
    a = a.strip()
    return a.split(" = ", 1)[1].strip() if re.fullmatch(r"\w+ = .*", a, re.S) else a


def nested_check(binds):
    """NESTED (B8): a user macro whose body passes one of its PATTERN parameters on to another macro call."""
    if s8("p25"):
        return
    heads = set(_plain_heads(binds)) | set(PROV) | set(MACROS) | set(h[0] for h in map(head_of, binds) if h)
    for b in binds:
        h = head_of(b)
        if not h:
            continue
        params = [p for p, _, k in h[1] if k == "plain"]
        body = h[2]
        for mm in re.finditer(r"(?<![\w.$])([A-Za-z_][\w.]*)\(", body):
            if mm.group(1) not in heads or mm.group(1) == h[0]:
                continue
            j = close_paren(body, mm.end() - 1)
            for a in split_top(body[mm.end():j], ","):
                if _arg_val(a) in params:
                    raise CompileError(NOTMOD8 + "the body of %s passes its pattern parameter `%s` on to %s (a nested "
                                       "body)" % (h[0], _arg_val(a), mm.group(1)))


def exprarg_check(expr, binds):
    """EXPRARG (B8) and MSGS: a read `N.` of a binding N the caller passes inside an EXPRESSION argument is not
    modelled; one the caller passes under its own label is refused by condition 4, so named; a read through the
    name of a macro whose only call the caller labels is refused by condition 4, so named. Returns the expression."""
    bnames = set(b.partition(" := ")[0].strip() for b in binds if not head_of(b))
    heads = set(_plain_heads(binds)) | set(PROV) | set(MACROS)
    sl = strip_lits(expr)
    for M_ in sorted(set(re.findall(r"(?<![\w.$])\$?([A-Za-z_]\w*)\.[A-Za-z_]", sl)) & (heads - bnames)):
        calls = [m_ for m_ in re.finditer(r"(?<![\w.])%s\(" % re.escape(M_), sl)]
        if calls and all(re.search(r"\[\w+ = $", sl[:m_.start()]) for m_ in calls):
            raise CompileError("`%s.`: the caller labels the call of %s, a label made on that use (a compile error, "
                               "binding-as-label condition 4, the manager's reading); the read is through the "
                               "caller's label" % (M_, M_))
    for N in sorted(set(re.findall(r"(?<![\w.$])\$?([A-Za-z_]\w*)\.[A-Za-z_]", sl)) & bnames):
        for mm in re.finditer(r"(?<![\w.])([A-Za-z_][\w.]*)\(", expr):
            if mm.group(1) not in heads:
                continue
            j = close_paren(expr, mm.end() - 1)
            if not re.search(r"(?<![\w.$])\$?%s\.[A-Za-z_]" % re.escape(N), sl[:mm.end()] + " " * (j - mm.end()) +
                             sl[j:]):
                continue                                     # every read of N is inside this call: it travels with it
            for a in split_top(expr[mm.end():j], ","):
                av = _arg_val(a)
                avp = re.sub(r"(?<![\w.$])\$?%s\.[\w.]+" % re.escape(N), "", strip_lits(av))   # its reads are no use
                if av == N or not re.search(r"(?<![\w.$])%s(?![\w])" % re.escape(N), avp):
                    continue
                lab = re.fullmatch(r"\[(\w+) = %s\]" % re.escape(N), av)
                if lab and lab.group(1) == N:
                    continue                                 # the written-out shorthand: the caller's label N
                if lab:
                    if s8("p11"):                            # the plant: the read routed to the caller's label
                        return re.sub(r"(?<![\w.$])%s\." % re.escape(N), lab.group(1) + ".", expr)
                    raise CompileError("`%s.`: the caller's own label `%s` is made on the spot where %s places `%s` "
                                       "(a compile error, binding-as-label condition 4); the read is `%s.`"
                                       % (N, lab.group(1), mm.group(1), N, lab.group(1)))
                raise CompileError(NOTMOD8 + "`%s.` reads a binding passed inside an expression argument (`%s` to "
                                   "%s)" % (N, av, mm.group(1)))
    return expr


def placements(body, p, lmap):                               # noqa: F811
    """SPOTON (A10, the manager's reading): a label is ON the spot only when written directly around the
    parameter, `[l = p]`, nothing between; `[l = p SEQ /x/]` labels a wider spot."""
    if not x8() or s8("p18"):
        return P88F["placements"](body, p, lmap)
    out = []
    for mm in re.finditer(r"(?<![\w.$])%s(?![\w])" % re.escape(p), body):
        left, right = body[:mm.start()], body[mm.end():]
        lb = re.search(r"\[(\w+|\([^()]*\)) = $", left) if right.startswith("]") else None
        lb = lb or (re.search(r"\(\?<:?(\w+)>\$\{$", left) if right.startswith("}") else None)
        out.append((None if lmap.get(lb.group(1)) == "_" else lb.group(1)) if lb else None)
    return out


def two_sources(expr, binds):                                # noqa: F811
    """SAMELIST (B8): predfold1123's, with a name the caller LISTS (`[(=h) = A]`) left as written: the list makes
    it the caller's own label, so it is not renamed."""
    if not x8() or s8("p26"):
        return P88F["two_sources"](expr, binds)
    listed = set(x.strip().split("=")[-1].strip() for g in re.findall(r"\[\(=([^()]*)\) = ", expr)
                 for x in g.split(",") if x.strip())
    keep = {}
    for i, n in enumerate(sorted(listed)):
        keep[n] = "zzlist%dzz" % i
        expr = re.sub(r"(?<![\w.$])%s(?![\w])" % re.escape(n), keep[n], expr)
    expr = P88F["two_sources"](expr, binds)
    for n, t_ in keep.items():
        expr = expr.replace(t_, n)
    return expr


def samelist_inline(expr, binds):
    """SAMELIST (B8): `[(=..) = N]` over a binding N whose text is one rx literal: N's text in place (the list
    takes N's exported labels as the caller's own; the same answers by construction: the model's limit)."""
    if s8("p26"):
        return expr
    bd = dict((b.partition(" := ")[0].strip(), b.partition(" := ")[2].strip()) for b in binds if not head_of(b))

    def sub(mm):
        n = mm.group(2)
        if n in bd and re.fullmatch(r"/[^/]*/", bd[n]):
            return "[(=%s) = %s]" % (mm.group(1), bd[n])
        return mm.group(0)
    return re.sub(r"\[\(=([^()]*)\) = (\w+)\]", sub, expr)


def unspec_body(name, p, body):                              # noqa: F811
    """p7's site: `_` for a count's lower bound (the plant reads it 1)."""
    if x8() and s8("p7"):
        body = body.replace("{${%s}," % p, "{1,")
    return P88F["unspec_body"](name, p, body)


def prog(expr, binds=(), **opts):                            # noqa: F811
    if not x8():
        return P88F["prog"](expr, binds, **opts)
    binds = list(binds)
    nested_check(binds)
    if s8("p3"):                                             # the plant: a later default bound to that one's value
        b2 = []
        for b in binds:
            h = head_of(b)
            if h:
                names = [q for q, _, _ in h[1]]
                dd = dict((q, d) for q, d, _ in h[1])
                for i, (q, d, k) in enumerate(h[1]):
                    if d in names and names.index(d) > i:
                        b = re.sub(r"\b%s = %s\b" % (q, d), "%s = %s" % (q, dd[d]), b, count=1)
            b2.append(b)
        binds = b2
    if s8("p17"):                                            # the plant: two public stacked labels chain
        expr = re.sub(r"\[(\w+) = \[(\w+) = (\w+)\]\]", lambda m_: "[%s = ([%s = %s])]" % m_.groups()
                      if not m_.group(1).startswith("_") and not m_.group(2).startswith("_") else m_.group(0), expr)
    expr = exprarg_check(expr, binds)
    return P88F["prog"](samelist_inline(expr, binds), binds, **opts)


# ---- the libpcre2 three-mode matcher (ctypes, the installed library; never read: D181)
_PCA, _PCE, _PCN = 0x80000000, 0x20000000, 0x00000008       # ANCHORED, ENDANCHORED, NOTEMPTY_ATSTART
PC2.pcre2_compile_8.restype = ctypes.c_void_p
PC2.pcre2_match_data_create_from_pattern_8.restype = ctypes.c_void_p
PC2.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
PC2.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_uint32,
                              ctypes.c_void_p, ctypes.c_void_p]
PC2.pcre2_match_data_create_from_pattern_8.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
PC2.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]


class PC8:
    """A regex text through libpcre2, the three modes (FIND-ALL as the engine's own)."""

    def __init__(self, rx):
        self.rx = rx
        b = rx.encode()
        e, o = ctypes.c_int(), ctypes.c_size_t()
        self.code = PC2.pcre2_compile_8(b, len(b), 0, ctypes.byref(e), ctypes.byref(o), None)
        if not self.code:
            raise CompileError("libpcre2 refuses `%s` (error %d at %d)" % (rx, e.value, o.value))
        self.md = PC2.pcre2_match_data_create_from_pattern_8(self.code, None)

    def _m(self, s, i, fl):
        sb_ = s.encode()
        r = PC2.pcre2_match_8(self.code, sb_, len(sb_), i, fl, self.md, None)
        if r < 0:
            return None
        ov = PC2.pcre2_get_ovector_pointer_8(self.md)
        return (ov[0], ov[1], None)

    def whole(self, s):
        return self._m(s, 0, _PCA | _PCE) is not None

    def search(self, s, frm=0):
        return self._m(s, frm, 0)

    def at(self, s, i, nonempty=False):
        return self._m(s, i, _PCA | (_PCN if nonempty else 0))

    def findall(self, s):
        return Prog.findall(self, s)

    def captures(self):
        n = ctypes.c_uint32()
        PC2.pcre2_pattern_info_8(ctypes.c_void_p(self.code), 4, ctypes.byref(n))
        return n.value


# ---- the unit timeout (B9): every check is a unit; a hung unit is named on the last line
import signal  # noqa: E402

UNIT8 = ["(load)"]


def _alarm(sig, frm):
    print("TIMEOUT: unit %s ran over %d s" % (UNIT8[0], UNIT_TIMEOUT8), flush=True)
    print("predfix88_model: unit %s timed out" % UNIT8[0], flush=True)
    os._exit(3)


signal.signal(signal.SIGALRM, _alarm)


def unit(name, what, secs=UNIT_TIMEOUT8):
    UNIT8[0] = name
    signal.alarm(secs)
    print("== %s: %s" % (name, what))


# ================================================================== the checks
LINES.clear()
RUN.clear()
RESULTS = []
D8 = dict(NOWS)                                              # the documents as READ by the checks (plants alter it)


def check(name, ok, detail=""):                              # noqa: F811
    signal.alarm(0)
    RESULTS.append((name, bool(ok)))
    print("%s %s: %s" % ("PASS" if ok else "FAIL", name, detail), flush=True)


def run(expr, binds=()):                                     # noqa: F811
    """(the program, None) or (None, the refusal); a crash is a refusal marked CRASH, which no check accepts."""
    try:
        return prog(expr, list(binds)), None
    except CompileError as e:
        return None, str(e)
    except Exception as e:                                   # noqa: BLE001
        return None, "CRASH %s: %s" % (type(e).__name__, e)


def bt(binds):                                               # noqa: F811
    return "".join(", %s := `%s`" % tuple(b.split(" := ", 1)) for b in binds)


def pl(label, expr, binds, wh, sr, fa, tag, tail="", P=None, shown=None, bdesc=None, ann=None):   # noqa: F811
    Pg, err = (P, None) if P is not None else run(expr, binds)
    if Pg is None:
        print("   REFUSED [%s] %s: %s" % (tag, label, err))
        return None
    w = fmt(Pg, wh, sr, fa)
    for t in (ann and wh or []):
        if Pg.whole(t):
            st = whole_state(Pg, t)
            vs = ", ".join(("%s = `%s`" % (n, label_of(st, n))) if label_of(st, n) is not None else "%s unset" % n
                           for n in ann)
            w = w.replace("`%s` HOLDS" % t, "`%s` HOLDS (%s)" % (t, vs), 1)
    L_ = "%s%s (`%s`%s)%s" % ((label + ": ") if label else "", w, shown or expr, bt(binds) if bdesc is None else bdesc,
                              tail)
    doc_line(L_, tag)
    print("   LINE [%s] %s" % (tag, L_))
    return Pg


def rl(label, expr, binds, key, reason, tag, shown=None):    # noqa: F811
    """A printed refusal line; the refusal must name `key` (never empty) and be no crash."""
    assert key, "a refusal line needs a key (B7)"
    Pg, err = run(expr, binds)
    L_ = "%s: modes: a compile error (`%s`%s: %s)." % (label, shown or expr, bt(binds), reason)
    doc_line(L_, tag)
    print("   LINE [%s] %s\n      (refusal: %s)" % (tag, L_, err))
    return err is not None and key in err and not err.startswith("CRASH"), err


def refused(expr, binds, key):                               # noqa: F811
    assert key
    Pg, err = run(expr, binds)
    print("   RUN `%s`%s: %s" % (expr, bt(binds), ("refused: " + err) if err else "legal"))
    return err is not None and key in err and not err.startswith("CRASH")


def wh_(Pg, texts):
    return [Pg.whole(t) for t in texts] if Pg is not None else None


def piece8(tag):
    """The base piece of `tag` in the documents as read."""
    for f_, txt in D8.items():
        if f_.endswith("_details.md"):
            continue
        mm = re.search(r"^### .*\[%s\].*$" % re.escape(tag), txt, re.M)
        if mm:
            nx = re.search(r"^### ", txt[mm.end():], re.M)
            return txt[mm.start():mm.end() + (nx.start() if nx else len(txt) - mm.end())]
    return ""


def entry8(tag):
    """The details entry of `tag` in the documents as read."""
    for f_, txt in D8.items():
        if not f_.endswith("_details.md"):
            continue
        mm = re.search(r"^## %s — .*$" % re.escape(tag), txt, re.M)
        if mm:
            nx = re.search(r"^## ", txt[mm.end():], re.M)
            return txt[mm.start():mm.end() + (nx.start() if nx else len(txt) - mm.end())]
    return ""


def pinned(check_name, pins):
    """B4: each (tag, sentence) a check rests on, read from that piece of the documents; the missing ones."""
    miss = [(t_, s_) for t_, s_ in pins if ws(s_) not in ws(piece8(t_))]
    for t_, s_ in miss:
        print("   RULE SENTENCE MISSING [%s] %s" % (t_, s_))
    print("   %d rule sentences pinned for %s, %d missing" % (len(pins), check_name, len(miss)))
    return not miss


A_D = "A := /(?<d>\\d)/"
A_H = "A := /(?<h>\\d)/"
ADIG = "A := [d = rx.digits]"
B_XX = "B(rx) := /${rx}xx/"
B_AL = "B(rx) := /${rx}-(?<d>\\d)/"
B_P = "B(rx) := /${[p = rx]}-(?<d>\\d)/"
B_LS = "B(rx) := /${[(=) = rx]}xx/"
B_CL = "B(rx) := /${[_ = rx]}xx/"
B_CP = "B(rx) := /${[_p = rx]}xx/"
B_PH = "B(rx) := /${[p = rx]}xx/"
B_ST = "B(rx) := /${[n = [_x = rx]]}xx/"
B_BOTH = "B(rx) := /${[p = rx]}-${rx}/"
B_AF = "B(rx) := /${rx}-${[p = rx]}/"
B_WD = "B(rx) := [p = rx SEQ /x/] SEQ /x/"
B_NS = "B(rx) := /${C(rx)}xx/"
C_PH = "C(rx) := /${[p = rx]}/"
PAIR = "pair(p) := /${p},${p}/"
W_ = "W(l:, v) := /<${[l = v]}>/"
P_ = "P := /(?<d>\\d)\\d/"
P_XX = "P := /(?<d>\\d)xx/"
OWNB = "A(l:, P) := [l = [_x = P]] & (_x: 5)"
W_AB = "W(a, b) := [(=) = a] SEQ [(=) = b]"
REP_T = "lib/rx/repeat"
CF_T = "core/operators/bindings/call-forms"
UN_T = "core/operators/bindings/unspecified"
CNT_T = "core/holes/count"
RULE_T = "core/labels/rule"
SC_T = "core/labels/rule/stacked-chain"
OWN_T = "core/labels/ownership"
AD_T = "core/labels/paths/argument-default"
CA_T = "core/labels/paths/closed-argument"
CP_T = "core/labels/paths/call-prefix"
ARGT = "core/labels/export/arguments"
LO_T = "core/operators/bindings/label-omitted"
NS_T = "core/holes/bare-condition/nested-scope"
NAME_T = "core/holes/name"
QR = ["", "12", "123", "123456"]
Q3 = (["3xx", "7xx"], "7xx 3xx", "3xx 7xx 4xx")
REC8 = _git8("docs/design/plan_row_bodies/COND-FAMILY.md", START8)
if s8("p4"):
    D8["core.md"] = D8["core.md"].replace("parameter, never a later one.\"", "parameter.\"", 1)
if s8("p8"):
    D8["core.md"] = D8["core.md"].replace("It is not that the rule gives none", "The rule gives none", 1)
if s8("p14"):
    D8["core.md"] = D8["core.md"].replace("In the body an unspecified label is the part with NO label",
                                          "In the body an unspecified label is the blank mark", 1)

unit("CONTROL", "the extended matcher against python `re` and libpcre2")
QC = pop("12x", 6)
ctl = []
for e, rx in (("rx.repeat(rx.digit)", r"(?:\d){0,}"), ("rx.repeat(rx.digit, 3)", r"(?:\d){3,3}"),
              ("rx.repeat(rx.digit, 3, _)", r"(?:\d){3}" if s8("p1") else r"(?:\d){3,}"),
              ("rx.repeat(rx.digit, _, 5)", r"(?:\d){0,5}"), ("rx.repeat(rx.digit, 2, 5)", r"(?:\d){2,5}"),
              ("rx.repeat(rx.digit, 0)", r"(?:\d){0,0}"), ("rx.digits", r"\d+")):
    Pg, err = run(e)
    ctl.append((e, ndiff(answers(Pg, QC), answers(Re(rx), QC)) if Pg is not None else err,
                ndiff(answers(PC8(rx), QC), answers(Re(rx), QC))))
P_stc = run("[n = [_x = P]] & (n.d: <5)", [P_])[0]
QS = pop("37", 3)
ctl.append(("stacked", ndiff(answers(P_stc, QS), answers(Re(r"[0-4]\d"), QS)) if P_stc is not None else "refused",
            (0, 0, 0)))
check("CONTROL", all(v == (0, 0, 0) and w == (0, 0, 0) for _, v, w in ctl),
      "differing (WHOLE, SEARCHED, FIND-ALL) against python `re` over %d texts, and libpcre2 against python `re` "
      "(the control's own control): %s" % (len(QC), [(e, v, w) for e, v, w in ctl]))

unit("CALLFORMS", "call-forms (ruled): one head per name; positional first, then named; defaults")
cf_pins = [(CF_T, "1. One head per name. There is no overloading; a call is never matched against several bodies."),
           (CF_T, "A positional entry after a named one is a compile error for now."),
           (CF_T, "it may name an earlier parameter, never a later one."),
           (CF_T, "The underscore does not take the default"),
           (CF_T, "A default naming an earlier parameter names that parameter's VALUE in the copy being made")]
cf_pin = pinned("CALLFORMS", cf_pins)
if s8("p2"):
    SABB.add("s2")
P_cf1 = pl("Named after positional", "rx.repeat(rx.digit, max = 5, min = 2)", [], ["1", "12", "123456"], "x1234567",
           "1234567 1 12", CF_T)
ok_cf2, r_cf2 = rl("A positional entry after a named one", "rx.repeat(rx.digit, max = 5, 2)", [], "positional entry after",
                   "a compile error for now", CF_T)
SABB.discard("s2")
ok_cf3, r_cf3 = rl("A parameter filled twice", "rx.repeat(rx.digit, 3, min = 2)", [], "twice",
                   "`min` by position and by name", CF_T)
ok_cf4 = refused("rx.repeat(rx.digit, low = 2)", [], "does not have")
ok_cf5, r_cf5 = rl("A default naming a later parameter", "R(rx.digit)",
                   ["R(x, min = max, max = _) := /(?:${x}){${min},${max}}/"], "not an earlier parameter",
                   "a default may name an earlier parameter only", CF_T)
ok_cf6, r_cf6 = rl("Two heads for one name", "R(rx.digit)", ["R(x) := /${x}/", "R(x, y) := /${x}${y}/"],
                   "one head per name", "one head per name, no overloading", CF_T)
ok_cf7 = refused("rx.repeat()", [], "binds no `x`")
cf_arms = {"pins": cf_pin, "named after positional": P_cf1 is not None and wh_(P_cf1, ["1", "12", "123456"]) ==
           [False, True, False], "positional after named": ok_cf2, "filled twice": ok_cf3, "unknown name": ok_cf4,
           "later default": ok_cf5, "two heads": ok_cf6, "required unset": ok_cf7}
check("CALLFORMS", all(cf_arms.values()), "arms failing: %s (refusals: %s; %s)" %
      ([k for k, v in cf_arms.items() if not v] or "none", r_cf2, r_cf5))

unit("ARRAYCOUNT", "A3 (the manager's reading): a default naming an earlier parameter names its VALUE per copy; "
     "the copies built from the repeat head in library.md, run through libpcre2")
_rh = head_of(REPEAT_LINE)
_rx_digit = re.search(r"`rx\.digit := /([^/`]*)/`", D8["library.md"]).group(1)
_arr = re.search(r"n := \[(\d+), (\d+)\]", piece8(CF_T) + piece8(REP_T))
NARR = [int(_arr.group(1)), int(_arr.group(2))] if _arr else []


def copies(written, per_value):
    """The count copies of `rx.repeat(x, <written>)`, n an array: `written` maps a parameter to its argument text
    ("n" for the array; unset parameters take their head default). per_value: a default naming an earlier
    parameter takes that parameter's value in the copy (A3); else the default's text is one more mention."""
    ps = _rh[1]
    vals = {}
    for p, d, _ in ps[1:]:
        vals[p] = written.get(p, d)
    mentions = [p for p in vals if vals[p] == "n"]
    for p in vals:                                           # a default naming an earlier parameter
        if p not in written and vals[p] in vals and vals[p] != p:
            if per_value and not s8("p5"):
                continue
            mentions.append(p)
    out = []
    for combo in itertools.product(NARR, repeat=len(mentions)):
        cv = dict(vals)
        for p, v in zip(mentions, combo):
            cv[p] = str(v)
        for p in cv:
            if cv[p] in cv and p not in written:
                cv[p] = cv[cv[p]]
        lo, hi = cv["min"], cv["max"]
        if lo != "_" and hi != "_" and int(lo) > int(hi):
            continue                                         # an illegal copy (min above max) removed
        body = _rh[2].strip("/").replace("(?:${[(=) = x]})", _rx_digit if len(_rx_digit) == 2 else "(?:%s)" %
                                         _rx_digit)
        out.append(body.replace("${min}", lo).replace("${max}", hi))
    return "(?|%s)" % "|".join(dict.fromkeys(out))


AC_WH, AC_SR, AC_FA = ["12", "123", "1234"], "x123", "123 1234 12345"
rx_v = copies({"min": "n"}, True)
rx_i = copies({"min": "n"}, False)
rx_lib = copies({"min": "n", "max": "n"}, True)
P_av, P_ai, P_al = PC8(rx_v), PC8(rx_i), PC8(rx_lib)
pl("An array count, the value per copy", "", [], AC_WH, AC_SR, AC_FA, CF_T, P=P_av,
   shown="rx.repeat(rx.digit, n)", bdesc=", n := [2, 4], is `%s` (the reading)" % rx_v)
pl("An array count, a second mention (not taken)", "", [], AC_WH, AC_SR, AC_FA, CF_T, P=P_ai,
   shown="rx.repeat(rx.digit, n)", bdesc=", n := [2, 4], read as `%s`" % rx_i)
pl("", "", [], ["123", "1"], "12345", "12345 6", REP_T, P=P_al, shown="rx.repeat(rx.digit, min = n, max = n)",
   bdesc=", n := [2, 4], is `%s`: the copy (4,2) removed" % rx_lib)
ac_arms = {"array read from the documents": NARR == [2, 4],
           "per value: 123 FAILS": wh_(P_av, AC_WH) == [True, False, True],
           "second mention: 123 HOLDS": wh_(P_ai, AC_WH) == [True, True, True],
           "the ruled quote": ws("an exact count of n is `\\d{2}|\\d{4}`") in ws(piece8(CF_T))
           and ws("an exact count of n is `\\d{2}|\\d{4}`") in ws(REC8)}
check("ARRAYCOUNT", all(ac_arms.values()), "the copies per value `%s`, per mention `%s`; arms failing: %s"
      % (rx_v, rx_i, [k for k, v in ac_arms.items() if not v] or "none"))

unit("REPEAT", "repeat-head (ruled: head (i)): one count exact, 0 included; `_` leaves a bound out")
if s8("p6"):
    SABB.add("s7")
RP = [("No count", "rx.repeat(rx.digit)", [True, True, True, True]),
      ("One count, exact", "rx.repeat(rx.digit, 3)", [False, False, True, False]),
      ("No maximum", "rx.repeat(rx.digit, 3, _)", [False, False, True, True]),
      ("No minimum", "rx.repeat(rx.digit, _, 5)", [True, True, True, False]),
      ("A range", "rx.repeat(rx.digit, 2, 5)", [False, True, True, False]),
      ("A written 0, exact", "rx.repeat(rx.digit, 0)", [True, False, False, False])]
rp_got = []
for lab, e, want in RP:
    Pg = pl(lab, e, [], QR, "x1234567", "1234567 12", REP_T)
    rp_got.append((e, wh_(Pg, QR) == want))
P_rp1 = run("rx.repeat(rx.digit, min = 3)")[0]
P_rp2 = run("rx.repeat(rx.digit, min = 3, max = _)")[0]
SABB.discard("s7")
unset_vs_ = P_rp1 is not None and P_rp2 is not None and P_rp1.whole("123") and not P_rp1.whole("1234") and \
    P_rp2.whole("1234")
check("REPEAT", all(ok for _, ok in rp_got) and unset_vs_, "WHOLE over %s against the ruled table: %s; unset `max` "
      "(the default `min`, exact) and `max = _` (no maximum) differ %s" % (QR, rp_got, unset_vs_))
for lab, e, _ in RP[:4]:
    pl(lab, e, [], QR, "x1234567", "1234567 12", CF_T)

unit("UNSPEC", "unspecified-rule (ruled) with the conservative overlay (the manager's reading)")
un_pin = pinned("UNSPEC", [(UN_T, "An argument given as the underscore says: this part is not written."),
                           (UN_T, "a conservative overlay (the manager's reading"),
                           (UN_T, "It is not that the rule gives none"),
                           (UN_T, "open exact-count-unspecified")])
P_u1 = pl("A label", 'A(_:) SEQ "!"', ["A(l:) := /(?<:${l}>\\d)/"], ["3!", "7!"], "x3!", "3! 7!", UN_T)
P_u2 = pl("An option", "opt(_)", ["opt(o) := /(?${o})ab/"], ["ab", "AB"], "x AB ab", "ab AB Ab", UN_T)
P_u2w = run("/ab/")[0]
P_u3 = pl("A count bound", "rx.repeat(rx.digit, 3, _)", [], QR, "x1234567", "1234567 12", UN_T)
P_u3b = run("rx.repeat(rx.digit, _, 5)")[0]
ok_u4, r_u4 = rl("A pattern", "P2(_, /b/)", ["P2(a, b) := /${a}${b}/"], "no form without the part",
                 "a compile error for now, the overlay", UN_T)
ok_u5, r_u5 = rl("An exact count", "E(rx.digit, _)", ["E(x, n) := /(?:${x}){${n}}/"], "no form without the part",
                 "a compile error for now, the overlay; candidate (b) of exact-count-unspecified", UN_T)
P_u9 = pl("Candidate (a)", "EB(rx.digit, _)", ["EB(x, n) := /(?:${x}){${n},${n}}/"], QR, "x1234567", "1234567 12",
          UN_T, tail=": exact-count-unspecified's (a), `{${n}}` written as both bounds, each unspecified")
P_u8 = pl("Laid into two positions", "T(rx.digit, _)", ["T(x, n) := /(?:${x}){${n},}b{0,${n}}/"],
          ["1b", "bbbb", "1"], "x1bb", "1bb 2 b", UN_T)
ok_u6 = refused("G(_)", ["G(n) := /\\d/ & (0: >= ${n})"], "no form without the part")
ok_u7 = refused("Q(_)", ["Q(s) := /x/ & (0: s)"], "no form without the part")
un_arms = {"pins": un_pin, "label": P_u1 is not None,
           "option = `/ab/`": P_u2 is not None and answers(P_u2, pop("abAB", 2)) == answers(P_u2w, pop("abAB", 2)),
           "upper bound `_`": P_u3 is not None and wh_(P_u3, QR) == [False, False, True, True],
           "lower bound `_` is 0": P_u3b is not None and P_u3b.whole(""),
           "pattern (overlay)": ok_u4, "exact count (overlay)": ok_u5,
           "candidate (a) `{0,}`": wh_(P_u9, QR) == [True] * 4,
           "two positions": wh_(P_u8, ["1b", "bbbb", "1"]) == [True, True, True],
           "comparison bound (overlay)": ok_u6, "set (overlay)": ok_u7}
check("UNSPEC", all(un_arms.values()), "arms failing: %s" % ([k for k, v in un_arms.items() if not v] or "none"))

unit("COUNT", "count-unspecified (ruled): by meaning, never the empty text; libpcre2 reads `{,}` as text")
P_c0 = pl("Both bounds unspecified", "rx.repeat(rx.digit, _, _)", [], QR, "x1234567", "1234567 12", CNT_T)
pc_src = "a{0,}" if s8("p9") else "a{,}"
pcw = [(s, PC8(pc_src).whole(s)) for s in ("", "aaa", "a{,}")]
print("   libpcre2 (ctypes, the installed library) WHOLE on `%s`: %s" % (pc_src, pcw))
check("COUNT", P_c0 is not None and wh_(P_c0, QR) == [True] * 4 and pcw == [("", False), ("aaa", False), ("a{,}", True)],
      "`rx.repeat(rx.digit, _, _)` is `{0,}` %s; libpcre2 `a{,}` WHOLE ``, `aaa`, `a{,}`: %s" % (wh_(P_c0, QR), pcw))

unit("SHORTHAND", "binding-as-label (ruled): the four conditions; the shorthand protected (A5, the manager's reading)")
sh_pin = pinned("SHORTHAND", [(RULE_T, "4. no label has already been made on it"),
                              (RULE_T, "A label made there is made by anyone on that use, the body included"),
                              (AD_T, "The shorthand label is protected, as statement 2's implicit label is")])
if s8("p10"):
    SABB.add("s10")
if s8("p12"):
    SABB.add("s11")
P_s1 = pl("The body using the argument alone", "B(A) & (A.d: <5)", [A_D, B_AL], ["7-3", "3-7", "3-3"], "7-3 3-7",
          "7-3 3-7 1-2 9-9", CA_T)
pl("A's own d, the body using the argument alone (case 2)", "B(A) & (A.d: <5)", [A_D, B_AL], ["7-3", "3-7", "3-3"],
   "7-3 3-7", "7-3 3-7 1-2 9-9", CP_T)
ok_s2, r_s2 = rl("The body labelling the spot", "B(A) & (A.d: <5)", [A_D, B_P], "condition 4",
                 "a label is made on the spot; the read is `B.p.d`, the line \"Through the body's path\"", CA_T)
rl("A's own d, the body labelling the spot (case 2)", "B(A) & (A.d: <5)", [A_D, B_P], "condition 4",
   "a label is made on the spot; the read is `B.p.d` (core/labels/paths/closed-argument)", CP_T)
P_s3 = pl("Through the body's path", "B(A) & (B.p.d: <5)", [A_D, B_P], ["7-3", "3-7", "3-3"], "7-3 3-7",
          "7-3 3-7 1-2 9-9", CA_T)
ok_s4, r_s4 = rl("The body listing the spot", "B(A) & (A.d: <5)", [A_D, B_LS], "condition 4",
                 "the list is a label made on the spot (the manager's reading (b)); the read is `B.d`", CA_T)
P_s5 = pl("Through the call, the list", "B(A) & (B.d: <5)", [A_D, B_LS], *Q3, tag=CA_T)
ok_s6, r_s6 = rl("Closed by the macro", "B(A) & (A.d: <5)", [A_D, B_CL], "closes the spot",
                 "the blank mark is a label made on the spot; `[c = B(A)] & (c.d: <5)` alike", CA_T)
ok_s6b = refused("[c = B(A)] & (c.d: <5)", [A_D, B_CL], "not visible")
ok_s7, r_s7 = rl("Closed by a `_` part label", "B(A) & (A.d: <5)", [A_D, B_CP], "condition 4",
                 "`c.d` and `B.d` alike; inside its binding a `_` part label is an ordinary one", CA_T)
P_s8 = pl("The caller's own label, under a closing body", "B([a = A]) & (a.h: <5)", [A_H, B_CL], *Q3, tag=CA_T)
ok_s9, r_s9 = rl("The caller's label, then the binding's name", "B([a = A]) & (A.h: <5)", [A_H, B_XX], "condition 4",
                 "the caller's label `a` is made on the spot (condition 4); the read is `a.h`", OWN_T)
ok_s10, r_s10 = rl("Used twice in the caller's text", "B(A) SEQ A & (A.d: <5)", [A_D, B_XX], "condition 1",
                   "the binding is not referenced unambiguously (condition 1); label the uses", AD_T)
P_s11 = pl("The caller's read through the shorthand", "B(A) & (A.d: <5)", [A_D, B_XX], *Q3, tag=AD_T)
P_s11w = pl("Written out", "B([A = A]) & (A.d: <5)", [A_D, B_XX], *Q3, tag=AD_T)
pl("The body using its argument alone", "B(A) & (A.d: <5)", [A_D, B_XX], *Q3, tag=ARGT)
P_s12 = pl("Both uses", "B(A) & (A.d: <5)", [B_BOTH, A_D], ["7-3", "3-7"], "7-3 3-7", "7-3 3-7 1-2 9-9", AD_T)
P_s16 = pl("Alone first", "B(A) & (A.d: <5)", [B_AF, A_D], ["3-7", "7-3"], "7-3 3-7", "7-3 3-7 1-2 9-9", AD_T)
P_s16w = pl("Alone first, the caller's label written (not its expansion)", "B([A = A]) & (A.d: <5)", [B_AF, A_D],
            ["3-7", "7-3"], "7-3 3-7", "7-3 3-7 1-2 9-9", AD_T, tail=": the last mention, the labelled spot")
ok_s17, r_s17 = rl("From outside", '[pub = B(A)] & (pub.A.h: <5)', [A_H, B_XX], "not visible",
                   "the shorthand label is protected: it adds no export (the manager's reading)", AD_T)
P_s13 = pl("Used twice alone, the last mention", "pair(A) & (A.d: <5)", [A_D, PAIR], ["7,3", "3,7"], "3,7 7,3",
           "7,3 3,7 1,2", CP_T)
P_s14c = run("C", ["C := B(A) & (A.d: <100)", ADIG, B_XX])[0]
P_s14 = pl("Example 1", "C := B(A) & (A.d: <100)", [ADIG, B_XX], ["42xx", "100xx", "042xx"], "x100xx 42xx",
           "100xx 42xx 7xx 300xx", NS_T, P=P_s14c)
P_s15 = pl("The unspecified label on a spot", "W(_:, A) & (A.h: <5)", [W_, A_H], ["<3>", "<7>"], "<7> <3>",
           "<3> <7> <4>", LO_T)
SABB.discard("s10")
SABB.discard("s11")
sh_arms = {"pins": sh_pin, "alone": wh_(P_s1, ["7-3", "3-7", "3-3"]) == [False, True, True],
           "labelled refused": ok_s2, "`B.p.d`": wh_(P_s3, ["7-3", "3-7", "3-3"]) == [False, True, True],
           "listed refused": ok_s4, "`B.d` listed": wh_(P_s5, Q3[0]) == [True, False], "closed refused": ok_s6,
           "`c.d` closed": ok_s6b, "`_p` refused": ok_s7, "caller's label under a closing body":
           wh_(P_s8, Q3[0]) == [True, False], "caller's label then `A.h` refused": ok_s9, "used twice refused": ok_s10,
           "shorthand": wh_(P_s11, Q3[0]) == [True, False], "written out alike":
           P_s11w is not None and answers(P_s11w, pop("37x", 3)) == answers(P_s11, pop("37x", 3)),
           "both uses (the alone spot)": wh_(P_s12, ["7-3", "3-7"]) == [True, False],
           "alone first (the alone spot)": wh_(P_s16, ["3-7", "7-3"]) == [True, False],
           "alone first written: another read": wh_(P_s16w, ["3-7", "7-3"]) == [False, True],
           "from outside refused": ok_s17, "pair alone twice": wh_(P_s13, ["7,3", "3,7"]) == [True, False],
           "example 1": wh_(P_s14, ["42xx", "100xx"]) == [True, False], "`W(_:, A)`": wh_(P_s15, ["<3>", "<7>"]) ==
           [True, False]}
check("SHORTHAND", all(sh_arms.values()), "arms failing: %s (labelled: %s; caller's label: %s)"
      % ([k for k, v in sh_arms.items() if not v] or "none", r_s2, r_s9))

unit("NOLABEL", "`_:` is the part with no label, not `[_ = v]` (label-omitted's rule sentence, pinned)")
nl_pin = pinned("NOLABEL", [(LO_T, "In the body an unspecified label is the part with NO label")])
if s8("p13"):
    SABB.add("s12")
P_nl1 = run("W(_:, A) & (A.h: <5)", [W_, A_H])[0]
ok_nl2 = refused("W4(A) & (A.h: <5)", ["W4(v) := /<${[_ = v]}>/", A_H], "closes")
P_nl3 = run("W3(A) & (A.h: <5)", ["W3(v) := /<${v}>/", A_H])[0]
nl_low = _sub_labels("[l = v]", {"l": "_"}, {})
SABB.discard("s12")
print("   `[l = v]` with l passed `_` lowers to: %s" % nl_low)
nl_arms = {"pins": nl_pin, "`W(_:, A)` legal": P_nl1 is not None,
           "as no label": P_nl1 is not None and P_nl3 is not None and
           answers(P_nl1, pop("<37>", 3)) == answers(P_nl3, pop("<37>", 3)),
           "blank mark refused": ok_nl2, "lowered with no label": "_ =" not in nl_low}
check("NOLABEL", all(nl_arms.values()), "arms failing: %s" % ([k for k, v in nl_arms.items() if not v] or "none"))

unit("STACK", "label-doors line 5: labels stacked on one spot are equal names; the order does not matter")
st_pin = pinned("STACK", [(RULE_T, "5. Labels stacked on one spot are equal names of it; their order does not matter.")])
if s8("p15"):
    SABB.add("s13")
if s8("p16"):
    SABB.add("s14")
P_k1 = pl("Outer the caller's, inner private", "[n = [_x = P]] & (n.d: <5)", [P_], ["37", "73", "3"], "73 37",
          "37 73 14", RULE_T)
P_k2 = pl("Outer private, inner the caller's", "[_x = [n = P]] & (n.d: <5)", [P_], ["37", "73", "3"], "73 37",
          "37 73 14", RULE_T)
P_k3 = pl("A blank label in the stack", "[l = [_ = P]] & (l.d: <5)", [P_], ["37", "73"], "73 37", "37 73 14", OWN_T)
P_k3b = run("[_ = [l = P]] & (l.d: <5)", [P_])[0]
P_k4 = run("[n = [_x = P]] & (_x.d: <5)", [P_])[0]
ok_k5, r_k5 = rl("Something between the two labels", "[n = [_x = P] SEQ \"!\"] & (n.d: <5)", [P_], "not visible",
                 "two spots: `_x`'s door is shut to `n` (the manager's reading (a))", RULE_T)
SABB.difference_update(("s13", "s14"))
QK = pop("37", 3)
st_arms = {"pins": st_pin, "either order": P_k1 is not None and P_k2 is not None and answers(P_k1, QK) ==
           answers(P_k2, QK), "`n.d`": wh_(P_k1, ["37", "73", "3"]) == [True, False, False],
           "blank inner opens through `l`": wh_(P_k3, ["37", "73"]) == [True, False],
           "blank outer opens through `l`": wh_(P_k3b, ["37", "73"]) == [True, False],
           "`_x.d` alike": P_k4 is not None and P_k1 is not None and answers(P_k4, QK) == answers(P_k1, QK),
           "something between": ok_k5}
check("STACK", all(st_arms.values()), "arms failing: %s" % ([k for k, v in st_arms.items() if not v] or "none"))

unit("STACKCHAIN", "open stacked-chain: two public stacked labels; the reading meanwhile (a), candidate (b) run nested")
P_sc1 = pl("Candidate (a), the first name", "[n = [m = P]] & (n.d: <5)", [P_XX], *Q3, tag=SC_T)
P_sc2 = pl("Candidate (a), the second name", "[n = [m = P]] & (m.d: <5)", [P_XX], *Q3, tag=SC_T)
ok_sc3, r_sc3 = rl("Candidate (a), a chain", "[n = [m = P]] & (n.m.d: <5)", [P_XX], "not visible",
                   "equal names do not chain (the reading meanwhile)", SC_T)
P_sc4 = pl("Candidate (b), run as the nested form", "[n = ([m = P])] & (n.m.d: <5)", [P_XX], *Q3, tag=SC_T)
check("STACKCHAIN", wh_(P_sc1, Q3[0]) == [True, False] and wh_(P_sc2, Q3[0]) == [True, False] and ok_sc3 and
      wh_(P_sc4, Q3[0]) == [True, False] and ws("open stacked-chain") in ws(piece8(SC_T)),
      "`n.d` %s, `m.d` %s, `n.m.d` refused %s (%s), the nested form %s" %
      (wh_(P_sc1, Q3[0]), wh_(P_sc2, Q3[0]), ok_sc3, r_sc3, wh_(P_sc4, Q3[0])))

unit("SPOTON", "A10 (the manager's reading): a label is on the spot only when written directly around it")
sp_pin = pinned("SPOTON", [(RULE_T, "the label written directly around the part, nothing between")])
P_sp1 = pl("A label over a wider spot", "B(A) & (A.h: <5)", [A_H, B_WD], *Q3, tag=CA_T,
           tail=": the body's label is not on the argument's spot")
ok_sp2 = refused("B(A) & (A.h: <5)", [A_H, "B(rx) := [p = rx] SEQ /xx/"], "condition 4")
check("SPOTON", sp_pin and wh_(P_sp1, Q3[0]) == [True, False] and ok_sp2,
      "`[p = rx SEQ /x/]`: `A.h` %s; `[p = rx]` directly: refused %s" % (wh_(P_sp1, Q3[0]), ok_sp2))

unit("NESTED", "B8: a body passing its pattern parameter on is refused LOUDLY as not modelled (the loaded engine "
     "lost every label there, silently); no document line rests on it (rulings R-1: shorthand-is-callers dissolves it)")
ok_n1 = refused("B(A) & (A.h: <5)", [A_H, B_NS, C_PH], "not modelled")
ok_n2 = refused("B(S(x:)) & (x: <5)", ["S(l:) := /(?<:${l}>\\d)/", B_NS, C_PH], "not modelled")
ok_n3 = refused("B(A) & (B.h: <5)", [A_H, B_NS, C_PH], "not modelled")
check("NESTED", ok_n1 and ok_n2 and ok_n3, "refused as not modelled: the binding's name %s, a sent label %s, the "
      "call's name %s" % (ok_n1, ok_n2, ok_n3))

unit("SAMELIST", "B8: the caller's same-name list over a binding takes its labels as the caller's own")
P_l_1 = pl("The caller's list", "[(=) = A] SEQ /xx/ & (h: <5)", [A_H], *Q3, tag=OWN_T)
P_l_2 = run("[(=h) = A] SEQ /xx/ & (h: <5)", [A_H])[0]
P_l_3 = run("[(=) = /(?<h>\\d)/] SEQ /xx/ & (h: <5)")[0]
check("SAMELIST", P_l_1 is not None and P_l_2 is not None and P_l_3 is not None and
      answers(P_l_1, pop("37x", 3)) == answers(P_l_3, pop("37x", 3)) == answers(P_l_2, pop("37x", 3)),
      "`[(=) = A]` %s, `[(=h) = A]` %s, alike the literal written in place" %
      (wh_(P_l_1, Q3[0]), wh_(P_l_2, Q3[0])))

unit("CAPNAME", "A11 (the manager's reading): `_` into a capturing group's whole-name hole is `(...)`; the lowered "
     "text built from the body, run through libpcre2")
cn_body = "/(?<${n}>\\d)x/"
cn_rx = cn_body.strip("/").replace("(?<${n}>", "(?:" if s8("p27") else "(")
P_cn = PC8(cn_rx)
pl("A capturing group, the unspecified label", "", [], ["7x", "x"], "a7x", "7x 8x", NAME_T, P=P_cn,
   shown="C(_)", bdesc=", C(n) := `%s`, is `%s`" % (cn_body, cn_rx))
check("CAPNAME", P_cn.captures() == 1 and wh_(P_cn, ["7x", "x"]) == [True, False] and
      ws("is `(...)`, regex's") in ws(piece8(NAME_T)), "`%s`: %d capture(s), WHOLE %s" %
      (cn_rx, P_cn.captures(), wh_(P_cn, ["7x", "x"])))

unit("OWNERBODY", "his two-label body, `A(l:, P) := [l = [_x = P]] & (_x: 5)`, with a name and with `_`")
P_o1 = pl("His body, a name", "A(n:, /\\d/)", [OWNB], ["5", "7", "55"], "7 5", "5 7 5 3", LO_T)
P_o2 = pl("His body, the unspecified label", "A(_:, /\\d/)", [OWNB], ["5", "7", "55"], "7 5", "5 7 5 3", LO_T)
if s8("p19"):
    SABB.update(("s12", "s14"))
    P_o2 = run("A(_:, /\\d/)", [OWNB])[0]
    SABB.difference_update(("s12", "s14"))
P_o3 = run("A(n:, /\\d/) & (n: 5)", [OWNB])[0]
check("OWNERBODY", P_o1 is not None and P_o2 is not None and answers(P_o1, pop("57", 2)) == answers(P_o2, pop("57", 2))
      and wh_(P_o1, ["5", "7", "55"]) == [True, False, False] and P_o3 is not None,
      "with `n:` %s, with `_:` %s; the caller's `n` read %s" % (wh_(P_o1, ["5", "7", "55"]), wh_(P_o2, ["5", "7", "55"]),
                                                              P_o3 is not None))

unit("LIBLINES", "the library's lines under the one head (rx.repeat; padded_to with the `005` witness; when; peek; ...)")
if s8("p20"):
    PROV["padded_to"] = (PROV["padded_to"][0], PROV["padded_to"][1].replace("0*", "0?"))
    MACROS["padded_to"] = [([(p, None) for p, _, _ in PROV["padded_to"][0]], PROV["padded_to"][1])]
P_l1 = pl("The last item, through a label on the call", '[r = rx.repeat(/(?<a>\\d)/, min = 1, max = _)] & (r.a: "3")',
          [], ["73", "37"], "x37 73", "73 37 13", REP_T)
P_l2 = pl("A label written on the argument", "rx.repeat([a = rx.digit], min = 1, max = _) & (a: <5)", [],
          ["3", "73", "37"], "7 3", "37 73 4", REP_T, ann=["a"])
P_l3 = pl("Every item, a group question", '[r = rx.repeat(/(?<a>\\d)/, min = 1, max = _)] & some((r.a: "7"))', [],
          ["73", "33"], "x33 73", "73 33 17", REP_T)
P_l4 = pl("", "/${padded_to(/(?:\\d\\d)+?/, 3)}/", [], ["0129"], "x0129", "0129 0000 12", "lib/modifiers/padded-to")
P_l5 = pl("Two digits at least", "padded_to(rx.digit, 2)", [], ["5", "05", "005", "55"], "x5 07", "5 07 123",
          "lib/modifiers/padded-to")
P_l5b = pl("Three digits at least, two zeros", "padded_to(rx.digit, 3)", [], ["005", "05", "0005"], "x005", "5 005 0005",
           "lib/modifiers/padded-to")
ok_l6, r_l6 = rl("Through the argument's name", "W(A, (A.h: <5))", [W_AB, A_H], "condition 4",
                 "the spot is listed, a label made (binding-as-label, the manager's reading (b)); "
                 "`W([a = A], (a.h: <5))` reads it", "lib/control/when")
P_l7 = pl("The caller's own label", "W([a = A], (a.h: <5))", [W_AB, A_H], ["3", "7"], "7 3", "3 7 4", "lib/control/when")
ok_l8, r_l8 = rl("Through the argument's name", "peek(A) SEQ /\\d/ & (A.d: <5)", [A_D], "condition 4",
                 "the body lists the spot, a label made (binding-as-label); the read is `peek.d`", "lib/control/peek")
ok_l9, r_l9 = rl("Through the argument's name", "atomic(A) & (A.d: <5)", [A_D], "condition 4",
                 "the body lists the spot; the read is `atomic.d`", "lib/control/atomic")
ok_l10, r_l10 = rl("Through the argument's name", "hits(A) & (A.d: <5)", [A_D], "condition 4",
                   "the body labels the spot `hit`; the read is `hits.hit.d`", "lib/search/hits")
ok_l14, r_l14 = rl("A labelled call, through the macro's name", "[h = hits(/\\d+/)] & (hits.hit: 3)", [],
                   "condition 4", "a label is made on that use (condition 4, a reading); the read is `h.hit`", CP_T)
ok_l11 = refused("occurrences(A) & (A.d: <5)", [A_D], "condition 4")
P_l12 = pl("A binding used alone in a call, through its name", "identity(A) & (identity.d: <5)",
           [A_D, "identity(x) := /${[(=) = x]}/"], ["3", "7"], "7 3", "3 7 4", "lib/convention/argument-labels")
ok_l13, r_l13 = rl("The same read through the argument's name", "identity(A) & (A.d: <5)",
                   [A_D, "identity(x) := /${[(=) = x]}/"], "condition 4",
                   "the list on the spot is a label made (binding-as-label, the manager's reading (b))",
                   "lib/convention/argument-labels")
QD5 = pop("1x", 5)
dg = ndiff(answers(run("rx.digits")[0], QD5), answers(Re(r"\d+"), QD5))
li_arms = {"repeat lines": all(x is not None for x in (P_l1, P_l2, P_l3)), "padded_to lines": all(
           x is not None for x in (P_l4, P_l5)), "padded_to two zeros (`005`)": wh_(P_l5b, ["005", "05", "0005"]) ==
           [True, False, False], "`W(A, ..)` refused": ok_l6, "`W([a = A], ..)`": P_l7 is not None,
           "peek": ok_l8, "atomic": ok_l9, "hits": ok_l10, "a labelled call's name": ok_l14, "occurrences": ok_l11,
           "identity": ok_l13 and P_l12 is not None, "rx.digits = `\\d+`": dg == (0, 0, 0) and len(QD5) == 63}
check("LIBLINES", all(li_arms.values()), "arms failing: %s" % ([k for k, v in li_arms.items() if not v] or "none"))

unit("TABLE", "B3: the ownership table READ from core.md (header, column sentence, rows, cells), every read run")
_own = piece8(OWN_T)
if s8("p21"):
    _own = _own.replace("| used alone | labelled |", "| labelled | used alone |", 1)
if s8("p22"):
    _own = _own.replace("alone `/${rx}xx/`; labelled `/${[p = rx]}xx/`", "alone `/${[p = rx]}xx/`; labelled `/${rx}xx/`", 1)
if s8("p23"):
    _own = _own.replace("\n- A body that passes its PATTERN", "\n| a sixth writer | `h` | `h` | `h` | `h` | `h` |\n- A body "
                        "that passes its PATTERN", 1)
if s8("p24"):
    _own = _own.replace("| `h` bare (line 1) |", "| `h` a compile error (line 1) |", 1)
_ow = ws(_own)
COLB = dict(re.findall(r"(alone|labelled|listed|closed|stacked) `(/[^`]*/)`", _ow.split("the column says:", 1)[1]
                       .split("The first row", 1)[0])) if "the column says:" in _ow else {}
_mm = re.search(r"the three modes: (WHOLE .*?\])\.", _ow)
T_EXP = _mm.group(1) if _mm else ""
T_WH, T_SR, T_FA = modes_of(T_EXP) if T_EXP else ([], "", "")
_rows = [l_ for l_ in _own.split("\n") if l_.startswith("|")]
_hdr = [c.strip() for c in _rows[0].strip("|").split("|")] if _rows else []
_cols = []
for h_ in _hdr[1:]:
    k_ = [k for k in ("alone", "labelled", "listed", "closed", "stacked") if k in h_]
    _cols.append(k_[0] if len(k_) == 1 else None)
WRITERS = [("own text", "R1"), ("argument's binding", "R2"), ("the body", "R3"), ("the caller", "R4"),
           ("a sent label", "R5")]
SXL = "S(l:) := /(?<:${l}>\\d)/"


def cell_prog(row, body, read):
    if row == "R1":
        inner = re.fullmatch(r"/\$\{(.*)\}xx/", body).group(1).replace("rx", "/(?<h>\\d)/")
        return "%s SEQ /xx/ & (%s: <5)" % (inner, read), []
    if row in ("R2", "R3"):
        return "B(A) & (%s: <5)" % read, [A_H, "B(rx) := " + body]
    if row == "R4":
        return "B([a = A]) & (%s: <5)" % read, [A_H, "B(rx) := " + body]
    return "B(S(x:)) & (%s: <5)" % read, [SXL, "B(rx) := " + body]


def cell_reads(text, header=False):
    """(read, legal?) of every backticked read in a cell; refused iff "compile error" follows before the next read."""
    out = []
    if not header:                                           # a parenthesis is a ground, not a read
        while re.search(r"\([^()]*\)", text):
            text = re.sub(r"\([^()]*\)", "", text)
    parts = re.split(r"`([A-Za-z_][\w.]*)`", text)
    for i in range(1, len(parts), 2):
        bad = "compile error" in parts[i + 1].split("`")[0]
        if header and not bad:
            continue
        out.append((parts[i], not bad))
    return out


tb_bad, tb_n, tb_rows = [], 0, 0
if len(_cols) != 5 or None in _cols or sorted(_cols) != sorted(COLB) or not T_EXP:
    tb_bad.append(("the header or the column sentence unread", _hdr, sorted(COLB), T_EXP))
for l_ in _rows[2:]:
    cs = [c.strip() for c in l_.strip("|").split("|")]
    row = next((r_ for k_, r_ in WRITERS if k_ in cs[0]), None)
    if row is None:
        tb_bad.append(("a row of an unknown writer", cs[0]))
        continue
    tb_rows += 1
    for col, cell in zip(_cols, cs[1:]):
        if col not in COLB:
            continue
        for rd, legal in cell_reads(cell) + cell_reads(cs[0], header=True):
            e, b = cell_prog(row, COLB[col], rd)
            Pg, err = run(e, b)
            tb_n += 1
            got = fmt(Pg, T_WH, T_SR, T_FA) if Pg is not None else None
            ok = (got == T_EXP) if legal else (Pg is None and not err.startswith("CRASH"))
            print("   %s %-8s `%s`: %s%s" % (row, col, rd, ("legal" if Pg else "refused: " + err[:90]),
                                             "" if ok else "   <-- DISAGREES (the cell says %s)" %
                                             ("legal" if legal else "a compile error")))
            if not ok:
                tb_bad.append((row, col, rd, e, "legal" if Pg else err[:120]))
check("TABLE", not tb_bad and tb_rows == 5, "%d rows read (5 writers), %d columns from the header and the column "
      "sentence, %d reads run against the cells' legality and the piece's three-mode answer; disagreeing: %s"
      % (tb_rows, len(_cols), tb_n, tb_bad or "none"))

unit("NAMEGRID", "the name grid: every cell decided by a sentence and run, or UNDECIDED with its open slug, or not "
     "modelled (refused loudly)")
G_ = [   # (writer, case, program, binds, expected: legal | refused | notmod, the open slug or None, where it lives)
    ("A.h", "alone", "B(A) & (A.h: <5)", [A_H, B_XX], "legal", None, None),
    ("A.h", "labelled", "B(A) & (A.h: <5)", [A_H, B_PH], "refused", None, None),
    ("A.h", "listed", "B(A) & (A.h: <5)", [A_H, B_LS], "refused", "list-is-label", "record"),
    ("A.h", "closed", "B(A) & (A.h: <5)", [A_H, B_CL], "refused", None, None),
    ("A.h", "`_p`", "B(A) & (A.h: <5)", [A_H, B_CP], "refused", None, None),
    ("A.h", "stacked", "B(A) & (A.h: <5)", [A_H, B_ST], "refused", None, None),
    ("A.h", "two public stacked", "B(A) & (A.h: <5)", [A_H, "B(rx) := /${[n = [m = rx]]}xx/"], "refused", None, None),
    ("A.h", "a wider spot", "B(A) & (A.h: <5)", [A_H, B_WD], "legal", None, None),
    ("A.h", "nested body", "B(A) & (A.h: <5)", [A_H, B_NS, C_PH], "notmod", None, None),
    ("A.h", "an expression argument", "B(A SEQ /x/) & (A.h: <5)", [A_H, "B(rx) := /${rx}x/"], "notmod", None, None),
    ("A.h", "both uses", "B(A) & (A.h: <5)", [A_H, "B(rx) := /${[p = rx]}${rx}xx/"], "legal", "both-uses", AD_T),
    ("A.h", "placed twice alone", "pair(A) & (A.h: <5)", [A_H, PAIR], "legal", "pair-twice-alone", "record"),
    ("A.h", "the caller's label", "B([a = A]) & (A.h: <5)", [A_H, B_XX], "refused", None, None),
    ("B.h", "alone", "B(A) & (B.h: <5)", [A_H, B_XX], "refused", None, None),
    ("B.p.h", "labelled", "B(A) & (B.p.h: <5)", [A_H, B_PH], "legal", None, None),
    ("B.h", "listed", "B(A) & (B.h: <5)", [A_H, B_LS], "legal", None, None),
    ("B.h", "closed", "B(A) & (B.h: <5)", [A_H, B_CL], "refused", None, None),
    ("B.n.h", "stacked", "B(A) & (B.n.h: <5)", [A_H, B_ST], "legal", None, None),
    ("B._x.h", "stacked", "B(A) & (B._x.h: <5)", [A_H, B_ST], "refused", None, None),
    ("B.n.h", "two public stacked", "B(A) & (B.n.h: <5)", [A_H, "B(rx) := /${[n = [m = rx]]}xx/"], "legal", None, None),
    ("B.n.m.h", "two public stacked", "B(A) & (B.n.m.h: <5)", [A_H, "B(rx) := /${[n = [m = rx]]}xx/"], "refused",
     "stacked-chain", SC_T),
    ("a.h", "the caller's label, closed", "B([a = A]) & (a.h: <5)", [A_H, B_CL], "legal", None, None),
    ("x", "a sent label, labelled", "B(S(x:)) & (x: <5)", [SXL, B_PH], "legal", None, None),
    ("x", "a sent label, nested body", "B(S(x:)) & (x: <5)", [SXL, B_NS, C_PH], "notmod", None, None),
]
if s8("p38"):
    G_[0] = G_[0][:4] + ("refused",) + G_[0][5:]
if s8("p39"):
    D8["core.md"] = D8["core.md"].replace("open both-uses", "both-uses", 1)
g_bad, g_und = [], []
for wr, case, e, b, want, slug, where in G_:
    Pg, err = run(e, b)
    got = "legal" if Pg is not None else ("notmod" if NOTMOD8 in err else "CRASH" if err.startswith("CRASH") else
                                          "refused")
    gt = {"both uses": ["73xx", "37xx"], "placed twice alone": ["7,3", "3,7"]}.get(case, Q3[0])
    ok = got == want and (got != "legal" or wh_(Pg, gt) == [True, False])
    if slug:
        home = ws(REC8) if where == "record" else ws(piece8(where))
        has = ("open " + slug) in home if where != "record" else slug in home
        g_und.append((wr, case, slug, has))
        ok = ok and has
        print("   UNDECIDED `%s` %s: open %s (%s); the reading meanwhile runs %s" % (wr, case, slug, where, got))
    else:
        print("   %s `%s` %s: %s" % ("DECIDED" if want != "notmod" else "NOT MODELLED", wr, case, got))
    if not ok:
        g_bad.append((wr, case, want, got, slug))
check("NAMEGRID", not g_bad, "%d cells: decided %d, UNDECIDED %d (%s), not modelled %d; disagreeing: %s" % (
      len(G_), sum(1 for x in G_ if not x[5] and x[4] != "notmod"), len(g_und),
      ", ".join(sorted(set(s for _, _, s, _ in g_und))), sum(1 for x in G_ if x[4] == "notmod" and not x[5]),
      g_bad or "none"))

unit("EXPAND", "the expansion drill: each sugar form against its written-out form READ from the documents")
_ad = ws(piece8(AD_T))
_wo = re.search(r"Written out, `(\w+)\((\w+)\)` is `([^`]*)`", _ad)
if s8("p28") and _wo:
    _ad = _ad.replace(_wo.group(0), "Written out, `B(A)` is `B([_ = A])`")
    _wo = re.search(r"Written out, `(\w+)\((\w+)\)` is `([^`]*)`", _ad)
_dg8 = re.search(r"`rx\.digits := (rx\.repeat\([^`]*\))`", ws(D8["library.md"]))
_ro = re.search(r"`(\[l = B\])` is `(B)` on that spot", ws(piece8(LO_T)))
QX = ['3xx', '7xx', '7-3', '3-7', '<3>', '<7>', '5', '55', '7', '12', '123', '1234', '123456', '37', '73', 'ab', 'AB',
      'x', '3x', '7x', '']
DRILL = [   # (sugar, its binds, the written-out form, its binds, where the written-out form is read)
    ("B(A) & (A.d: <5)", [A_D, B_XX], (_wo.group(3) if _wo else "?") + " & (A.d: <5)", [A_D, B_XX], AD_T),
    ("W(_:, A) & (A.h: <5)", [W_, A_H], ("W3(A) & (A.h: <5)" if _ro else "?"), ["W3(v) := /<${v}>/", A_H], LO_T),
    ("rx.digits", [], _dg8.group(1) if _dg8 else "?", [], "library.md"),
    ("A(_:, /\\d/)", [OWNB], "[_x = /\\d/] & (_x: 5)", [], "the rule: `_:` is no label"),
    ("rx.repeat(rx.digit, 3)", [], "rx.repeat(rx.digit, 3, 3)", [], "an unset parameter takes its default"),
    ("rx.repeat(rx.digit, 3, _)", [], "/(?:\\d){3,}/", [], "`_` for the upper bound"),
    ("rx.repeat(rx.digit)", [], "/(?:\\d){0,}/", [], "`_` for both bounds"),
    ("rx.repeat(rx.digit, max = 5, min = 2)", [], "rx.repeat(rx.digit, 2, 5)", [], "named entries"),
    ("opt(_)", ["opt(o) := /(?${o})ab/"], "/ab/", [], "`_` for an option: no letters"),
    ("[n = [_x = P]] & (n.d: <5)", [P_], "[_x = [n = P]] & (n.d: <5)", [P_], "stacked labels, either order"),
]
xd_bad = []
for a_, ab, b_, bb, where in DRILL:
    Pa, ea = run(a_, ab)
    Pb, eb = run(b_, bb)
    same = Pa is not None and Pb is not None and answers(Pa, QX) == answers(Pb, QX)
    print("   %s `%s` / `%s` (%s)" % ("AGREE" if same else "DIFFER", a_, b_, where))
    if not same:
        xd_bad.append((a_, b_, ea, eb))
check("EXPAND", not xd_bad and _wo is not None and _ro is not None and _dg8 is not None,
      "%d sugar forms against their written-out forms, every mode over %d texts; differing or refused: %s" %
      (len(DRILL), len(QX), xd_bad or "none"))

unit("READINGS", "the manager's readings a run can decide")
if s8("p29"):
    SABB.add("s17")
P_r2 = run("T(rx.digit, _)", ["T(x, n) := /(?:${x}){${n},}b{0,${n}}/"])[0]
P_r3 = run("[n = [_x = P] SEQ \"!\"] & (n.d: <5)", [P_])[0]
P_r5 = run("B(A) & (A.d: <5)", [A_D, B_BOTH])[0]
P_r6 = run("B(A) & (A.d: <5)", [A_D, B_AF])[0]
P_r7 = run("[pub = B(A)] & (pub.A.d: <5)", [A_D, B_XX])[0]
SABB.discard("s17")
RD = [
    ("unspecified-rule (b): `_` may be passed to any parameter, judged at each position it is laid into",
     P_r2 is not None and P_r2.whole("1b") and P_r2.whole("bbbb")),
    ("label-doors (a): anything between two labels makes two spots", P_r3 is None),
    ("binding-as-label, both uses: the shorthand on the alone spot, labelled second",
     P_r5 is not None and P_r5.whole("7-3") and not P_r5.whole("3-7")),
    ("binding-as-label, both uses: the shorthand on the alone spot, alone first",
     P_r6 is not None and P_r6.whole("3-7") and not P_r6.whole("7-3")),
    ("A5: the shorthand label is protected (no export through the caller's label)", P_r7 is None),
]
for a, v in RD:
    print("   %s: %s" % ("SUPPORTED" if v else "NOT SUPPORTED", a))
print("   UNTESTABLE: the written-out form's export (`[pub = B([A = A])] & (pub.A.h: ..)`): the model passes no caller "
      "label through a call at all, so the difference A5 names is not run")
check("READINGS", all(v for _, v in RD), "%d readings run: %s" % (len(RD), [a for a, v in RD if not v] or "all SUPPORTED"))

unit("SWEEP", "every printed three-mode line (`rejected:` and history skipped): predfold1123b's engine (the R88 "
     "extensions off) over the starting commit's documents against this one over these; every non-same status and "
     "every moved or gone answer DECLARED", 900)
_d0 = _src84.index("NOTMOD = ")
_d1 = _src84.index('if s84("s13"):')
exec(compile(_src84[_d0:_d1], P84, "exec"), globals())      # noqa: S102  predfix84's DECL_LINE / DECL_RULE, verbatim
STALE84 = [("core.md", "rx.repeat(rx.digit, 3)"),          # B2: stale since the one repeat head (predfold1123b)
           ("core.md", "[h = rx.digit] SEQ ((h: <5))?")]   # B2: no longer a crash (found by the inherited stale test)
for k_ in STALE84[1:] if s8("p31") else STALE84:
    DECL_LINE.pop(k_, None)
OLD8 = {f: _git8("docs/design/predicates/" + f, START8) for f in DOCF}
J_ = "a JSON sketch line: its bodies (`row`, `value`, `string`, ...) are in the line's prose, not its tail (predfix86)"
DECL8 = {                     # (file, program) -> (status, reason)
    ("library.md", 'row(v:, "v") & (v: "ok" | <5)'): ("REFUSED", J_),
    ("library.md", 'row(lo:, "lo") & row(hi:, "hi") & (lo: <$hi)'): ("REFUSED", J_),
    ("library.md", 'row(x:, "a" | "b") & (x: <5)'): ("REFUSED", J_),
    ("library.md", 'row(m:, "msg", contains("timeout"))'): ("REFUSED", J_),
}
DECL8[("core.md", "C(_)")] = ("REFUSED", "the lowered `(\\d)x` holds an unnamed group, which the label engine does "
                                          "not run; CAPNAME runs it through libpcre2 (the line is CAPNAME's)")
DECL_RULE8 = []
MOVED8 = {}                   # program -> why its printed answer or legality moved, or why the line is gone
NOWS8 = dict(NOWS)
if s8("p30"):                                                # the plant: one printed answer moved, its key unchanged
    NOWS8["core.md"] = NOWS8["core.md"].replace("WHOLE `37` HOLDS, `73` FAILS, `3` FAILS / SEARCHED `73 37`",
                                                "WHOLE `37` FAILS, `73` FAILS, `3` FAILS / SEARCHED `73 37`", 1)
X8[0] = False
OLD_T8 = sw_table84(OLD8)
X8[0] = True
NEW_T8 = sw_table84(NOWS8)
sw_bad, sw_moved, sw_new, sw_gone, used8 = [], [], [], [], set()
cnt8, why8 = {}, {}
for k, vs in NEW_T8.items():
    ov = OLD_T8.get(k, [])
    for i_, (f_, ln_, st_, got_) in enumerate(vs):
        cnt8[st_] = cnt8.get(st_, 0) + 1
        if st_ != "same":
            d_ = DECL8.get((f_, k[0])) or DECL_LINE.get((f_, k[0]))
            if d_ and d_[0] == st_:
                used8.add((f_, k[0]))
                why8[d_[1][:70]] = why8.get(d_[1][:70], 0) + 1
            else:
                r_ = next((x for x in DECL_RULE8 + DECL_RULE if x[0] == st_ and re.search(x[1], got_)), None)
                if r_ is None:
                    sw_bad.append(("UNDECLARED", f_, ln_, st_, k[0], got_[:160]))
                else:
                    used8.add(r_[1])
                    why8[r_[2][:70]] = why8.get(r_[2][:70], 0) + 1
        o_ = ov[i_] if i_ < len(ov) else None
        if o_ and (o_[3] != got_ or o_[2] != st_):
            if k[0] in MOVED8:
                used8.add(("moved", k[0]))
            else:
                sw_moved.append((f_, ln_, k[0], o_[2], st_, o_[3][:160], got_[:160]))
    if not ov:
        sw_new.append((vs[0][0], vs[0][1], k[0]))
for k, vs in OLD_T8.items():
    if k not in NEW_T8:
        if k[0] in MOVED8:
            used8.add(("moved", k[0]))
        else:
            sw_gone.append((vs[0][0], vs[0][1], k[0], vs[0][2]))
stale8 = sorted(k for k in list(DECL8) + list(DECL_LINE) if k not in used8) + \
    sorted(k for k in MOVED8 if ("moved", k) not in used8)
for k_, n_ in sorted(why8.items()):
    print("   DECLARED x%d: %s" % (n_, k_))
for x in sw_gone:
    print("   GONE %s:%d `%s` (was %s)" % x)
for x in sw_new:
    print("   ADDED %s:%d `%s`" % x)
for x in sw_moved:
    print("   MOVED %s:%d `%s` (old %s, now %s)\n      old: %s\n      now: %s" % x)
for x in sw_bad:
    print("   BAD %s" % (x,))
for x in stale8:
    print("   STALE DECLARATION %s" % (x,))
for k_, why in sorted(MOVED8.items()):
    print("   ANSWER MOVED (declared): `%s`: %s" % (k_, why))
check("SWEEP", OLD_T8 and not sw_bad and not sw_moved and not sw_gone and not stale8,
      "%d printed lines now (%s), %d at the starting commit under predfold1123b's engine; undeclared %d; moved or "
      "gone and not declared %d; declared moves %d; added %d; stale declarations %d (predfix84's inherited ones "
      "included)" % (len(NEW_T8), ", ".join("%s %d" % kv for kv in sorted(cnt8.items())), len(OLD_T8), len(sw_bad),
                     len(sw_moved) + len(sw_gone), len(MOVED8), len(sw_new), len(stale8)))

unit("NULLABLE", "EVID-4's known limit: no program the extended engine ran has a loop whose body can match empty")
exec(compile(_src84[_src84.index("def nullable(n):"):_src84.index("checked = list(RUN)")], P84, "exec"),
     globals())                                              # noqa: S102  predfix84's walker, verbatim
_nullable84 = nullable


def nullable(n):                                             # noqa: F811
    return False if n[0] == "ncls" else _nullable84(n)


if s8("p32"):
    run("rx.repeat(/a?/)")
checked8 = list(RUN)
nl8 = [(e, b) for e, b, nd in checked8 if loops_nullable(nd, [])]
check("NULLABLE", not nl8, "%d programs run by the checks above (SWEEP's included), walked node by node: %d with a "
      "loop whose body can match empty%s" % (len(checked8), len(nl8), (": %s" % nl8[:4]) if nl8 else ""))

unit("SUCCESSOR", "B1: every earlier in-force model re-run with library.md served from its PINNED delivery commit "
     "(nested model runs routed to their own pins); each red declared by its FAIL line VERBATIM with a reason; a "
     "traceback is never declared", 3600)
DECLF8 = os.path.join(HERE8, "predfix88_succ_decl.tsv")
SDECL8 = {}
for l_ in builtins.open(DECLF8, encoding="utf-8").read().split("\n"):
    if l_ and not l_.startswith("#"):
        m_, r_, why_, fl_ = l_.split("\t", 3)
        SDECL8.setdefault(m_, {})[r_] = (fl_, why_)
if s8("p33"):
    _k = sorted(SDECL8)[0]
    _r = sorted(SDECL8[_k])[0]
    SDECL8[_k][_r] = (SDECL8[_k][_r][0].replace("FAIL", "FAIL ", 1), SDECL8[_k][_r][1])
RUNPINS8 = dict(PINS8)
if s8("p34"):                                                # the plant: predbound at its lane's START commit, whose
    RUNPINS8 = {"predbound": "1e0384941"}                    # library its load-time reader asserts on: a traceback,
    SDECL8["predbound"] = {"TRACEBACK": ("x", "declared superseded")}   # here declared superseded
succ_bad, succ_n, succ_t = [], 0, {}
if not LIGHT8:
    for mname in sorted(RUNPINS8, key=lambda m_: list(PINS8).index(m_)):
        env = {k: v for k, v in os.environ.items() if not k.endswith(("_SABOTAGE", "_ENGINE", "_PROBE", "_LIGHT"))}
        for v_ in LIGHTENV8.values():
            env[v_] = "1"                                    # their own SUCCESSOR re-runs the same list: run once, here
        t0 = time.time()
        try:
            out = subprocess.run([sys.executable, "-I", "-B", os.path.abspath(__file__), "--succ",
                                  os.path.join(LANES8, mname + "_evidence", mname + "_model.py"), RUNPINS8[mname]],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env,
                                 timeout=600).stdout
        except subprocess.TimeoutExpired:
            out = "TIMEOUT: model %s did not finish in 600 s" % mname
        succ_t[mname] = time.time() - t0
        if os.environ.get("PREDFIX88_DUMPSUCC"):             # the declarations' source run (the lane's scratch)
            builtins.open(os.path.join(os.environ["PREDFIX88_DUMPSUCC"], mname + ".out"), "w").write(out)
        succ_n += 1
        lines_ = out.rstrip("\n").split("\n")
        last = lines_[-1]
        mm = re.match(r"%s_model: (\d+) checks, (\d+) failed(?: \(([^)]*)\))?$" % mname, last)
        reds = {}
        if mm and not any(x.startswith("Traceback") for x in lines_):
            for r in [x.strip() for x in (mm.group(3) or "").split(",") if x.strip()]:
                reds[r] = next((l_ for l_ in lines_ if l_.startswith("FAIL %s:" % r) or
                                re.match(r"%s\s+FAIL\b" % re.escape(r), l_)), "")
        else:
            reds["TRACEBACK"] = last
        decl = SDECL8.get(mname, {})
        print("   %-13s (library at %s, %.1f s) last line: %s" % (mname, RUNPINS8[mname], succ_t[mname], last[:150]))
        for r, fline in sorted(reds.items()):
            d = decl.get(r)
            if r == "TRACEBACK":
                succ_bad.append((mname, "TRACEBACK"))
                print("      TRACEBACK (never declarable): %s" % fline[:300])
            elif d is None:
                succ_bad.append((mname, r, "UNDECLARED"))
                print("      %s UNDECLARED: %s" % (r, fline[:400]))
            elif d[0] != fline:
                succ_bad.append((mname, r, "TEXT CHANGED"))
                print("      %s TEXT CHANGED:\n         declared: %s\n         now:      %s" % (r, d[0][:300], fline[:300]))
            else:
                print("      %s declared: %s\n         its FAIL line: %s" % (r, d[1], fline[:240]))
        gone = sorted(set(decl) - set(reds))
        if gone:
            succ_bad.append((mname, "GREEN NOW", gone))
            print("      declared but green now: %s" % gone)
check("SUCCESSOR", LIGHT8 or (succ_n == len(RUNPINS8) == len(PINS8) and not succ_bad),
      "%d earlier models re-run (%.0f s in all), each red against its declared FAIL line verbatim (%d declared): %s"
      % (succ_n, sum(succ_t.values()), sum(len(v) for v in SDECL8.values()), succ_bad or "every red declared, "
         "its text unchanged; no traceback"))

unit("QUOTES", "B5: the owner's sentences, each PINNED to the piece (or details entry) that quotes it, and in the "
     "record at the pinned start commit; the rulings' titles cited whole")
UNS, CFT, RHT = UN_T, CF_T, REP_T
QQ8 = [   # (his sentence, word for word; the piece that must hold it: a base tag, or "details:" + tag)
    ("unspecified-rule: yes and elegant", UNS),
    ("call-forms: yes.", CFT),
    ("repeat-head: agree with your lean", RHT),
    ("binding-as-label: yes", AD_T),
    ("label-doors: agree. Yes", RULE_T),
    ("I agree the count semantics should work that way", CNT_T),
    ("repeat(X, _, 5) is 0 up to 5", RHT),
    ("you can't go through A to get inside", RULE_T),
    ("It's closing that door but there may be other doors.", RULE_T),
    ("So I agree with your lean.", "details:core/labels/export"),
    ("Strictly that A doesn't make them visible through it.", RULE_T),
    ("the general canonical form is that all labels are chains of only labels", RULE_T),
    ("would the nesting order of the labels matter? By my reading no", RULE_T),
    ("Consider one additional rule based on your examples which is that a label on the binding has not already been "
     "made", "details:" + RULE_T),
    ("An argument given as the underscore says: this part is not written. The body then means what the construct at "
     "that position already means without that part. Where the construct has no form without the part, the call is a "
     "compile error.", UNS),
    ("1. One head per name. There is no overloading; a call is never matched against several bodies.", CFT),
    ("2. Positional entries first, then named ones. Positional entries fill the parameters in declared order, "
     "including those with defaults. Any parameter may be named. A positional entry after a named one is a compile "
     "error for now.", CFT),
    ("3. A default is the macro's own text. It is resolved in the macro's definition, and it may name an earlier "
     "parameter, never a later one.", CFT),
    ("4. Unset and the underscore are different. An argument left unset takes its default. The underscore does not "
     "take the default; it means \"not written\", by the rule you just ruled.", CFT),
    ("A binding's name may be used in a path as shorthand for a skipped label where: 1. the binding is referenced "
     "unambiguously; 2. a label could have been set on it there; 3. the reference reads as though through that label; "
     "4. no label has already been made on it there.", RULE_T),
    ("1. A label is owned by the text that writes its name; there it is read bare.", RULE_T),
    ("2. Any other label is read by a path, and a path is a chain of labels.", RULE_T),
    ("3. A binding's name may stand in a path for a skipped label, under your four conditions.", RULE_T),
    ("4. Each part decides the doors through itself, and closing one closes only that one.", RULE_T),
    ("5. Labels stacked on one spot are equal names of it; their order does not matter.", RULE_T),
    ("Labels stacked on one spot, with nothing between them, are equal names of that spot. Each is its own door to "
     "what the spot holds. One of them being private or blank closes only itself.", RULE_T),
    ("an exact count of n is `\\d{2}|\\d{4}`", CFT),
    ("label-hole-full: pure label must be whole the label is lost. Capture label can be partial but again, the label "
     "portion is lost.", NAME_T),
]
if s8("p35"):
    D8["core.md"] = D8["core.md"].replace("5. Labels stacked on one spot are equal names of it; their order does not "
                                          "matter.", "5. Labels stacked on one spot are equal names of it.", 1)
TT8 = [
    '2026-11-23 OWNER RULING — count-unspecified: "I agree the count semantics should work that way"; and the bigger question: do the argument rules force positions to be defined "meet me half way"',
    '2026-11-23 OWNER RULING — unspecified-rule: "yes and elegant" (the underscore as an argument: the part is not written)',
    "2026-11-23 OWNER RULING — call-forms: yes (one head per name; positional entries first, then named; a default is the macro's own text and may name an earlier parameter; unset takes the default, the underscore does not)",
    '2026-11-23 OWNER RULING — repeat-head: "agree with your lean" (head (i): `repeat(x, min = _, max = min)`)',
    '2026-11-23 OWNER RULING — closing-own-label: "I agree with your lean" (a caller\'s own label is not closed); the export statement closes ONE door: "there may be other doors"',
    "2026-11-23 OWNER RULING — binding-as-label: yes (a path is canonically a chain of labels; a binding's name is a shorthand for a skipped label, under four conditions)",
    '2026-11-23 OWNER RULING — label-doors: "agree. Yes" (the general rule of labels, five lines)',
    '2026-11-23 OWNER RULING — label-hole-full: a pure label\'s name hole must be whole; a capture\'s name may be partial, "but again, the label portion is lost"; and a sketch of the repeat head with a conditional default',
]
RW8 = ws(REC8)
q_miss = []
for q, where in QQ8:
    home = entry8(where[8:]) if where.startswith("details:") else piece8(where)
    if ws(q) not in RW8 or ws(q) not in ws(home):
        q_miss.append((q[:60], where, ws(q) in RW8))


def heads8(rec):
    return set(ws(re.sub(r"^(### |\*\*)", "", l_)) for l_ in rec.split("\n") if l_.startswith(("### ", "**")))


DET8 = D8["core_details.md"] + D8["library_details.md"] + D8["parked_details.md"]
t_miss = [t_ for t_ in TT8 if ws(t_) not in heads8(REC8) or ws('(record: "%s")' % t_) not in ws(DET8)]
check("QUOTES", not q_miss and not t_miss,
      "%d quoted sentences, each in the record at %s AND in its own piece, missing: %s; %d record titles cited whole "
      "as a `rulings:` item's record, not a title or not cited: %s" % (len(QQ8), START8, q_miss or "none", len(TT8),
                                                                   t_miss or "none"))

unit("DOC", "every line this model formats occurs verbatim in the piece its tag names")
DLN8 = list(LINES)
if s8("p36") and DLN8:
    DLN8[0] = (DLN8[0][0], DLN8[0][1].replace("WHOLE `", "WHOLE `x", 1))
if s8("p37") and DLN8:
    DLN8[0] = ("core/spellings/placeholders", DLN8[0][1])
D8DOC = dict(NOWS)
d_miss = []
for t_, L in DLN8:
    D8, _keep = D8DOC, D8
    if ws(L) not in ws(piece8(t_)):
        d_miss.append((t_, L))
    D8 = _keep
for t_, L in d_miss:
    print("   MISSING [%s] %s" % (t_, L))
check("DOC", DLN8 and not d_miss, "%d lines, each in its own piece; missing: %d" % (len(DLN8), len(d_miss)))

failed8 = [n for n, ok in RESULTS if not ok]
print("predfix88_model: %d checks, %d failed%s" % (len(RESULTS), len(failed8),
                                                  (" (%s)" % ", ".join(failed8)) if failed8 else ""))
sys.exit(1 if failed8 else 0)
