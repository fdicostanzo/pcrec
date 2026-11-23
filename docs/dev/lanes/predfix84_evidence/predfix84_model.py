#!/usr/bin/env python3
# Lane predfix84 (2026-11-23): the successor evidence model of review r84 (predspot1122), ruled in the record entry
# "2026-11-23 MANAGER — review r84 (predspot1122): the dispositions, ruled with the 2026-11-23 rulings in hand; no
# owner words". DESIGN EVIDENCE ONLY; rules nothing.
#
# METHOD. Lane predspot's model is LOADED unchanged: predspot_model.py is executed up to its line "the checks" (the
# LABEL engine: predspot's FIXES over predfix83's, preddef's, predfix82's, predcall's, predref's and predbound's
# lowerer and matcher), its plants cleared. Its FLAG engine (the section "GROUP 2: the FLAG engine" up to its check
# FCONTROL) is executed from the same file, then the fixes below replace named parts:
#   RENAME   (B1) a macro's parameters are alpha-renamed where its body is lowered (the parameter names and every
#            use of them in the body's EXPRESSION text, never inside rx text outside a hole), so no answer depends on
#            whether a caller's binding is named like a parameter (`peek(A)` / `peek(Z)`).
#   PARTPATH (B2) a part label over a single binding or call takes, by path, what that binding or call exports:
#            `[b = B(A)] & (b.p.h: ..)` as `B.p.h` (core/labels/export statement 3, "each step passed by the
#            previous one").
#   ARGREF   (B3) label-reference one argument deep: a bare label read written inside an argument must be written
#            in the argument's own text (`B(A & (h: "3"))` refused as `A & (h: "3")` is).
#   REASON   (B5) a refusal is renamed to argument-default only when the label it names is one the template writes
#            (`A.zz`, which no text writes, keeps its own reason).
#   UPTO     (B4) the flag engine reads "from the statement on" for a call's arguments (where the caller wrote
#            them) and a macro's body (where the macro is written: FMACROS carry a file position).
#   OPTHOLE, CONST, POSITION, PATTERN: the candidate switches of the open lines (option-hole-explicit,
#            options-reach-constants, options-position) and `pattern($x)` (lib/builtin/pattern's own sentence).
#   LIBRARY  `prefix_in` read from library.md as a macro (its body now writes the list on S).
# Checks: predspot's, repaired where review r84 ruled (GRID: rename drill, a part-label-on-call spelling, a cause
# arm, a real UNDECIDED arm; FLAGGRID: n/a re-labelled, an UNDECIDED arm, every applying cell's option shown to
# matter; SWEEP: every non-same status DECLARED with its reason, `rejected:` and history lines skipped), and new
# ones (RENAME, PARTPATH, ARGREF, LISTATOM, PREFIXIN, CONTAINS, SPOTNAME, UPTO, OPENFLAGS, PATFLAGS).
#
# KNOWN LIMIT (EVID-4, planned, not fixed here): a NULLABLE loop body past the minimum (PCRE's trailing empty pass)
# is not modelled: the loaded matcher refuses an empty pass once the minimum is met. The check NULLABLE walks every
# program this model's checks run for one and fails if found (review r84 B6: nullable arguments in looped spots are
# the EVID-4 row's, PLAN). Not modelled either: `U`, `xx`, `J`, `r` and the `a`-family in the flag engine; `^` / `$`
# inside an operand of `&`, `\b`, backreferences to a part (SWEEP declares each line that meets one); a complement
# inside a hole; `when` (its body's `NOT peek(test)`); `quoted`.
#
# Run (W = the worktree; any cwd):  timeout 3600 python3 -I -B W/docs/dev/lanes/predfix84_evidence/predfix84_model.py
# The model EXITS NON-ZERO iff its last line reports a failure; its verdict is its LAST LINE.
# PREDFIX84_ENGINE=old runs predspot's engine (no fix of this lane) over the documents of the starting commit:
# SWEEP's control; it prints one table.
# PREDFIX84_SABOTAGE=sN (one at a time): a deliberately wrong rule or fact; its target check must FAIL.
# PREDFIX84_SABOTAGE=all runs every plant in turn (a subprocess each) and prints the table predfix84_sabotage.out holds.
# PREDFIX84_LIGHT=1 skips SWEEP's old-engine run and SUCCESSOR (the plant runner sets it for plants not aimed there).
import hashlib
import itertools
import os
import re
import subprocess
import sys

HERE84 = os.path.dirname(os.path.abspath(__file__))
PSPOT = os.path.join(HERE84, "..", "predspot_evidence", "predspot_model.py")
SAB84 = set(x for x in os.environ.get("PREDFIX84_SABOTAGE", "").split(",") if x)
ENGINE84 = os.environ.get("PREDFIX84_ENGINE", "new")
LIGHT84 = os.environ.get("PREDFIX84_LIGHT") == "1"
START84 = "2d6270c10"                                        # this lane's starting commit (lane/pred-rev28)
for v in list(os.environ):
    if v.endswith("_SABOTAGE") or v.endswith("_ENGINE") or v.endswith("_LIGHT"):
        os.environ.pop(v, None)


def s84(n):
    return n in SAB84


PLANTS84 = [   # (plant, its target check, what it plants)
    ("s1", "CONTROL", "the control pattern for `identity(A)` widened to `\\d!?`"),
    ("s2", "RENAME", "RENAME off: a parameter keeps its name (B1)"),
    ("s3", "GRID", "RENAME off under the grid's rename drill only"),
    ("s4", "PARTPATH", "PARTPATH off: a part label over a call takes nothing by path (B2)"),
    ("s5", "GRID", "an argument cell expected legal"),
    ("s6", "ARGREF", "ARGREF off: a bare read inside an argument checked against nothing (B3)"),
    ("s7", "GRID", "REASON keyed on the base again (B5 (i)): `A.zz` named argument-default"),
    ("s8", "GRID", "the UNDECIDED arm's open slug misspelled (B5 (iii))"),
    ("s9", "FLAGGRID", "the weak-off arm's earlier `@options(i)` dropped: the option equals the default (B5 (ii))"),
    ("s10", "FLAGGRID", "one cell expected to apply (`m` up the hole, a library binding)"),
    ("s11", "FLAGGRID", "a deciding sentence looked for in the wrong piece"),
    ("s12", "UPTO", "UPTO off: an argument read with its file's options at the end (B4)"),
    ("s13", "SWEEP", "one declared status removed (B7)"),
    ("s14", "SWEEP", "`rejected:` and history lines read as current (B7)"),
    ("s15", "NULLABLE", "a nullable loop added to the programs run"),
    ("s16", "SUCCESSOR", "one declared red removed"),
    ("s17", "QUOTES", "an owner sentence altered"),
    ("s18", "DOC", "a formatted line altered"),
    ("s19", "LISTATOM", "the list's label read from the wrong group"),
    ("s20", "PREFIXIN", "prefix_in's body without its list"),
    ("s21", "CONTAINS", "the expected occurrence the first"),
    ("s22", "SPOTNAME", "candidate (b)'s refusal expected legal"),
    ("s23", "OPENFLAGS", "option-hole-explicit's two candidates run alike"),
    ("s24", "PATFLAGS", "`pattern($x)` takes the flags of the hole it is inserted in"),
    ("s25", "FILTER", "the `-i` trigger inverted"),
    ("s26", "FSWEEP", "a bad row planted"),
    ("s27", "LEXICAL", "an option reaches back up its file"),
    ("s28", "EXPLICIT", "the weak `i` passes a hole as if explicit"),
    ("s29", "NOTINH", "`m` and `s` inherited at a hole again"),
    ("s30", "LIBFILE", "a library file's options lost"),
    ("s31", "NUMBERS", "`n` ignored when counting numbered groups"),
    ("s32", "FCONTROL", "a hand control loses its `(?i:`"),
    ("s33", "EXAMPLES", "the record's line (a) expected for (b)"),
    ("s34", "PLACES", "peek's body without its export list"),
    ("s35", "CONVENTION", "prefix_in's piece expected not to point at the convention"),
    ("s36", "ARGNAME", "argument-default's candidate (local) in place of the ruling"),
    ("s37", "SPOT", "SPOTGROUP off: the label-only `hit` is not a spot"),
]
HEAVY84 = {"SWEEP", "SUCCESSOR"}
if "all" in SAB84:                                           # the plant runner: each plant alone, a subprocess each
    rows, notc = [], 0
    for pn, target, what in PLANTS84:
        env = {k: v for k, v in os.environ.items()}
        env["PREDFIX84_SABOTAGE"] = pn
        if target not in HEAVY84:
            env["PREDFIX84_LIGHT"] = "1"
        r = subprocess.run([sys.executable, "-I", "-B", os.path.abspath(__file__)], capture_output=True, text=True,
                           env=env, timeout=3600)
        lines = (r.stdout + r.stderr).rstrip("\n").split("\n")
        last = lines[-1]
        fl_ = next((x for x in lines if x.startswith("FAIL %s:" % target)), "")
        tb = any(x.startswith("Traceback") for x in lines)
        ok = bool(fl_) and not tb and r.returncode != 0 and target in last
        notc += not ok
        rows.append((pn, target, what, "caught" if ok else "NOT CAUGHT", last, fl_))
        print("%s -> %s (%s): %s" % (pn, target, what, "caught" if ok else "NOT CAUGHT"))
        print("   last line: %s" % last)
        print("   its FAIL line: %s" % fl_[:300], flush=True)
    print("predfix84_sabotage: %d plants, %d not caught" % (len(rows), notc))
    sys.exit(1 if notc else 0)

# ================================================================== the LOADER: predspot's label engine, then its flag engine
_srcS = open(PSPOT, encoding="utf-8").read()
_cutS = re.search(r"^# =+ the checks$", _srcS, re.M).start()
_file84 = __file__
__file__ = os.path.abspath(PSPOT)                            # noqa: F811  (the loaded code finds its siblings by it)
exec(compile(_srcS[:_cutS], PSPOT, "exec"), globals())       # noqa: S102  (predspot's definitions, unchanged)
__file__ = _file84
SABS.clear()                                                 # predspot's plants: none
_fl0 = re.search(r"^# =+ GROUP 2: the FLAG engine", _srcS, re.M).start()
_fl1 = _srcS.index('print("== FCONTROL')
exec(compile("\n" * _srcS[:_fl0].count("\n") + _srcS[_fl0:_fl1], PSPOT, "exec"), globals())   # noqa: S102
RUN.clear()
SP = dict(lower_atom=lower_atom, use_definition=use_definition, prog=prog, lower_pd=_lower_atom_pd,
          lower_fexpr=lower_fexpr, file_defaults=file_defaults, inherit=inherit, FP_atom=FP.atom, FP_seq=FP.seq,
          lower_list=lower_list, lower_literal=lower_literal)


def git_show84(rel):
    return subprocess.run(["git", "-C", W, "show", "%s:%s" % (START84, rel)], capture_output=True, text=True,
                          check=True).stdout


OLD84 = {f: git_show84("docs/design/predicates/" + f) for f in DOCF}
LIBSRC84 = OLD84["library.md"] if ENGINE84 == "old" else NOWS["library.md"]


def lb84(pattern):
    mm = re.search(pattern, ws(LIBSRC84))
    assert mm, pattern
    return mm.group(1)


# ---- LIBRARY: predspot's provided bodies, read again from the documents this run reads; prefix_in added
LIBMACROS.update({
    "peek": ([("A", None)], lb84(r"`peek\(A\) := (/.*?/)`")),
    "atomic": ([("X", None)], lb84(r"`atomic\(X\) := (/.*?/)`")),
    "contains": ([("s", None)], lb84(r"`contains\(s\)` is the plain gap body `(/.*?/)`")),
    "startsWith": ([("s", None)], lb84(r"`startsWith\(s\)` is the plain gap body `(/.*?/)`")),
    "endsWith": ([("s", None)], lb84(r"`endsWith\(s\)` is the plain gap body `(/.*?/)`")),
    "anchored": ([("s", None)], lb84(r"`anchored\(s\)` is the plain macro `(/.*?/)`")),
    "padded": ([("rx", None)], lb84(r"`padded\(rx\) := (/.*?/)`")),
    "hits": ([("r", None)], lb84(r"`hits\(r\) := (/.*?/)`")),
    "prefix_in": ([("n", None), ("S", None)], lb84(r"`prefix_in\(n, S\)` accepts a text whose first n characters are a "
                                                   r"member of S: `(/.*?/)`\.")),
})
LIBMACROS["list_of"] = ([("X", None), ("sep", None)],
                        lb84(r"`list_of\(X, sep = S\)` is the separated list `(/.*?/)`").replace("${S}", "${sep}")
                        .replace("= S]", "= sep]"))
if s84("s20"):                                               # PREFIXIN's plant: the body without its list
    LIBMACROS["prefix_in"] = ([("n", None), ("S", None)], "/${S & /(?s:.){${n}}/}(?s:.*)/")
if s84("s34"):                                               # PLACES's plant: one provided body loses its list
    LIBMACROS["peek"] = ([("A", None)], "/(?=${A})/")
if ENGINE84 == "old":
    NEW.clear()
    NEW.update(OLD84)                                        # the starting commit's documents: SWEEP's control

# ================================================================== the FIXES (lane predfix84)
RSEQ = [0]
ENGINE_ON = ENGINE84 != "old"


def _end_rx(t, i):
    """`t[i]` is the `/` opening an rx literal: the index of its closing `/`."""
    j = i + 1
    while j < len(t):
        if t[j] == "\\":
            j += 2
            continue
        if t[j] == "$" and t[j + 1:j + 2] == "{":
            j = _end_hole(t, j + 1) + 1
            continue
        if t[j] == "/":
            return j
        j += 1
    return len(t) - 1


def _end_hole(t, i):
    """`t[i]` is the `{` of a hole: the index of its closing `}` (nested holes and literals inside)."""
    depth, j = 0, i
    while j < len(t):
        c = t[j]
        if c == "/" and depth >= 1:
            j = _end_rx(t, j) + 1
            continue
        if c == '"' and depth >= 1:
            j = t.index('"', j + 1) + 1
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return j
        j += 1
    return len(t) - 1


def rename_expr(t, mp):
    """RENAME: every identifier of `mp` used in EXPRESSION text renamed (not after `.` or `$`, not a label left of
    `:` or ` = `, not a keyword argument); rx literals are walked into their holes only; strings are skipped."""
    out, i = [], 0
    while i < len(t):
        c = t[i]
        if c == "/":
            j = _end_rx(t, i)
            out.append(rename_rx(t[i:j + 1], mp))
            i = j + 1
            continue
        if c == '"':
            j = t.index('"', i + 1)
            out.append(t[i:j + 1])
            i = j + 1
            continue
        mm = re.match(r"[A-Za-z_]\w*", t[i:])
        if mm and (i == 0 or t[i - 1] not in "\\.$" and not t[i - 1].isalnum() and t[i - 1] != "_"):
            name = mm.group(0)
            after = t[i + len(name):]
            label_left = re.match(r"\s*:(?!=)", after) or re.match(r"\s+=\s", after) and not re.match(r"\s+==", after)
            out.append(mp[name] if name in mp and not label_left else name)
            i += len(name)
            continue
        if mm:
            out.append(mm.group(0))
            i += len(mm.group(0))
            continue
        out.append(c)
        i += 1
    return "".join(out)


def rename_rx(lit, mp):
    out, i = [], 0
    while i < len(lit):
        if lit[i] == "\\":
            out.append(lit[i:i + 2])
            i += 2
            continue
        if lit[i] == "$" and lit[i + 1:i + 2] == "{":
            j = _end_hole(lit, i + 1)
            out.append("${" + rename_expr(lit[i + 2:j], mp) + "}")
            i = j + 1
            continue
        out.append(lit[i])
        i += 1
    return "".join(out)


def use_definition(body, ctx, dname, params=None, mark=True):    # noqa: F811
    """RENAME (B1): the parameters renamed where the body is lowered."""
    if params and ENGINE_ON and not s84("s2") and not (s84("s3") and DRILL[0]):
        RSEQ[0] += 1
        mp = {p_: "%s__r%d" % (p_, RSEQ[0]) for p_ in params}
        body = rename_expr(body, mp)
        params = {mp[k]: v for k, v in params.items()}
    return SP["use_definition"](body, ctx, dname, params, mark)


DRILL = [False]
LCAND = {"spotname": "a"}    # spot-read-name's candidates: (a) the engine as ruled so far, (b) by the call only
TPL_NAMES = set()             # REASON (B5): the full label names a template writes, moved


def _lower_atom_pd84(e, ctx):
    """ARGREF (B3): a bare label read written inside an argument is checked as label-reference checks every bare
    read: against the text of the definition the argument is written in (the caller's, its arguments included)."""
    e2 = e.strip()
    if not (ENGINE_ON and e2 in ctx.params):
        return SP["lower_pd"](e, ctx)
    arg_text, caller = ctx.params[e2][0], ctx.params[e2][1]
    a = len(NAMED)
    text = SP["lower_pd"](e, ctx)
    for ps in all_groups(text):
        for bs, sc in ps:
            if set(sc) & set(caller.scopes):
                TPL_NAMES.add(bs)
    if s84("s6") or arg_text.strip() in getattr(caller, "params", {}):
        return text
    own = L83["own_labels"](DEFTEXT.get(caller.cur, "")) | L83["own_labels"](arg_text)
    for sc, nm in NAMED[a:]:
        if sc == caller.cur and "." not in nm and nm not in own and nm != "0":
            raise CompileError("label `%s` read in the argument `%s` is not written in the definition the argument "
                               "is written in: reference it with its source (a compile error, "
                               "core/labels/paths/label-reference)" % (nm, arg_text.strip()))
    return text


if ENGINE_ON:
    _lower_atom_pd = _lower_atom_pd84                        # noqa: F811  (both loaded lower_atoms call it by name)


def lower_atom(expr, ctx):                                   # noqa: F811
    """PARTPATH (B2): `[b = X]`, X a single binding or call, takes by path what X exports: X.r -> b.r."""
    e = expr.strip()
    pl = re.fullmatch(r"\[(\w+) = (.*)\]([+*?]?)", e, re.S)
    text = SP["lower_atom"](expr, ctx)
    if not (pl and ENGINE_ON) or s84("s4") or pl.group(1).startswith("_"):
        return text
    name, inner = pl.group(1), pl.group(2).strip()
    call = parse_call(inner)
    x = inner if inner in BINDS else (call[0] if call and call[0] in MACROS else None)
    if x is None or inner in ctx.params:
        return text

    vis = first_scope(text)                                  # the scope of X's body (its first `enter`)

    def add(ps):
        extra = []
        for bs, sc in ps:
            if "." in bs and vis in sc and PART_KIND.get(bs, "part") != "use" and not private(bs):
                nb = name + "." + bs
                if all(nb != b2 for b2, _ in ps + extra):
                    extra.append((nb, [ctx.cur]))
                    PART_KIND.setdefault(nb, "part")
        return ps + extra
    return map_groups(text, add)


def prog(expr, binds=(), **opts):                            # noqa: F811
    """REASON (B5 (i)): predspot's renaming of a refusal to argument-default, keyed on its cause: the label named is
    one the template writes."""
    TPL_NAMES.clear()
    if not ENGINE_ON or s84("s7"):
        return SP["prog"](expr, binds, **opts)
    TPL.clear()
    ARGDEF[0] = "local" if s84("s36") else "error"
    if LCAND["spotname"] == "b":                            # spot-read-name candidate (b): no read by the argument's
        argn = set()                                         # name, whatever the body does with the spot
        for mm in re.finditer(r"(?<![\w.])([A-Za-z][\w.]*)\(", expr):
            if mm.group(1) in MACROS:
                j = close_paren(expr, mm.end() - 1)
                argn |= set(a_.strip() for a_ in split_top(expr[mm.end():j], ",") if a_.strip() in BINDS)
        for nm in re.findall(r"(?<![\w.])\$?([A-Za-z]\w*)\.[\w.]+(?=\s*:|\b)", strip_args(expr)):
            if nm in argn:
                raise CompileError("`%s.`: a read by the argument's name (spot-read-name, candidate (b): only the "
                                   "call's path reaches it)" % nm)
    try:
        return L83["prog"](expr, binds, **opts)
    except CompileError as e:
        mm = re.search(r"`([\w.]+)`", str(e))
        if mm:
            nm = mm.group(1)
            parts = nm.split(".")
            hit = any(t_ == nm or nm.endswith("." + t_) or t_.endswith("." + nm) or
                      (len(parts) > 1 and t_ == ".".join(parts[1:])) for t_ in TPL_NAMES)
            if hit and parts[0] in TPL:
                raise CompileError("`%s`: a label of an argument, which is a template and not a spot in the pattern "
                                   "(a compile error, %s)" % (nm, AD_RULE))
        raise


# ---- the FLAG engine's fixes. F84[0] False runs predspot's flag engine as it stood (FSWEEP's control).
F84 = [ENGINE_ON]
FCAND = {"opthole": "explicit", "const": "reach", "position": "anywhere"}   # the open lines' candidates; the
#   engine as predspot left it is the first of each (it read an option hole as nothing, see OPENFLAGS)


def file_defaults(files, fname, upto):                       # noqa: F811
    """POSITION: under the candidate "top only" (options-position (b)) a statement below a binding, or a second
    statement, is a compile error."""
    if F84[0] and FCAND["position"] == "top only":
        its = files[fname]
        seen_bind, n_opt = False, 0
        for it in its:
            if it[0] == "bind":
                seen_bind = True
            elif it[0] == "opt":
                n_opt += 1
                if seen_bind or n_opt > 1:
                    raise FErr("`@options` below a binding or written twice in the %s file (options-position, "
                               "candidate (b): only at the top of a file)" % fname)
    return SP["file_defaults"](files, fname, upto)


def _fp_seq(self):
    """OPTHOLE: `(?${o})`, o a binding of a string constant, sets the flags it names; candidate "explicit" as
    `(?i)` written, candidate "weak" as a program option would (never explicit)."""
    if not F84[0]:
        return SP["FP_seq"](self)
    items = []
    while True:
        self.skipx()
        if self.peek() is None or self.peek() in "|)":
            break
        mm = re.match(r"\(\?\$\{\s*(\w+)\s*\}\)", self.s[self.i:])
        if mm:
            bf, j, text = find_bind(self.files, mm.group(1))
            fl_ = text.strip().strip('"')
            self.i += mm.end()
            on, _, off = fl_.partition("-")
            self.setflags(on, off)
            if FCAND["opthole"] == "weak" and not s84("s23"):
                if "i" in on or "i" in off:
                    self.st["i"] = (self.st["i"][0], False)
            continue
        mm = re.match(r"\(\?([imsxn]*)(?:-([imsxn]*))?\)", self.s[self.i:])
        if mm and (mm.group(1) or mm.group(2)):
            self.i += mm.end()
            self.setflags(mm.group(1), mm.group(2) or "")
            continue
        items.append(self.quant())
    return ("seq", items)


def _fp_atom(self):
    """PATTERN: a named group's text and the flags in force where it is written are recorded, for `pattern($x)`."""
    if F84[0] and self.peek() == "(" and self.s.startswith("?<", self.i + 1) and self.s[self.i + 3] not in "=!":
        j = self.s.index(">", self.i)
        name = self.s[self.i + 3:j]
        st0 = dict(self.st)
        start = j + 1
        n = SP["FP_atom"](self)
        if not hasattr(self, "groups"):
            self.groups = {}
        self.groups[name] = (self.s[start:self.i - 1], st0)
        return n
    return SP["FP_atom"](self)


def _fp_hole(self):
    depth, j = 1, self.i
    while depth:
        j += 1
        if self.s[j] == "{":
            depth += 1
        elif self.s[j] == "}":
            depth -= 1
    body = self.s[self.i + 1:j].strip()
    mm = re.fullmatch(r"pattern\(\$(\w+)\)", body)
    if mm and F84[0]:
        self.i = j + 1
        gtext, gst = getattr(self, "groups", {})[mm.group(1)]
        st = dict(self.st) if s84("s24") else dict(gst)      # PATFLAGS's plant: the hole's flags instead
        p2 = FP(gtext, st, self.files, self.fname, self.params)
        p2.upto = self.upto
        return p2.alt()
    self.i = j + 1
    body = re.sub(r"^\[\(=\) = (\w+)\]$", r"\1", body)
    return lower_fexpr(body, self.st, self.files, self.fname, self.params, at_hole=True, upto=self.upto)


FP.seq = _fp_seq
FP.atom = _fp_atom
FP.hole = _fp_hole
DEFAULT_ST = {"i": (False, False), "m": False, "s": False, "x": False, "n": False}


def lower_fexpr(e, at, files, fname, params, at_hole=False, upto=None):   # noqa: F811
    """predspot's, with UPTO (B4): an argument carries the position where the caller wrote it, a macro's body the
    position of the macro; CONST: the candidate "not reached" reads a string constant, and an argument literal a
    library body places, with the default state (no program option)."""
    if not F84[0]:
        return SP["lower_fexpr"](e, at, files, fname, params, at_hole, upto)
    e = e.strip()
    upto = len(files[fname]) if upto is None else upto
    parts = split_top(e, " & ")
    if len(parts) > 1:
        AMARK[0] += 1
        k_ = "fe%d" % AMARK[0]
        nodes = [lower_fexpr(x, at, files, fname, params, at_hole, upto) for x in parts]
        return ("seq", [("mark", k_), nodes[0]] + [("andpat", k_, x) for x in nodes[1:]])
    if e.startswith("/"):
        own = file_defaults(files, fname, upto)
        if PLACED[0] and FCAND["const"] == "not reached":
            own = dict(DEFAULT_ST)
        return lower_lit(e, inherit(at, own) if at_hole else at, files, fname, params, upto)
    if e.startswith('"') and e.endswith('"'):
        own = file_defaults(files, fname, upto)
        if FCAND["const"] == "not reached":
            own = dict(DEFAULT_ST)
            if not at_hole:
                at = dict(DEFAULT_ST)
        return lower_lit("/" + re.escape(e[1:-1]) + "/", inherit(at, own) if at_hole else at, files, fname, params,
                         upto)
    if e in params:                                          # a parameter: its argument, where the caller wrote it
        arg, afile, aparams, aupto = (params[e] + (None,))[:4]
        if s84("s12"):
            aupto = None
        placed = PLACED[0]
        PLACED[0] = afile != params.get("__bodyfile__", afile)
        try:
            return lower_fexpr(arg, at, files, afile, aparams, at_hole, aupto)
        finally:
            PLACED[0] = placed
    mm = re.fullmatch(r"([\w.]+)\((.*)\)", e, re.S)
    if mm and mm.group(1) in FMACROS:
        ent = FMACROS[mm.group(1)]
        ps, body, bfile = ent[:3]
        bpos = ent[3] if len(ent) > 3 and not s84("s12") else len(files[bfile])
        args = [a.strip() for a in split_top(mm.group(2), ", ")]
        newp = {p_: (a, fname, params, upto) for p_, a in zip(ps, args)}
        newp["__bodyfile__"] = bfile
        own = file_defaults(files, bfile, bpos)
        return lower_fexpr(body, inherit(at, own) if at_hole else own, files, bfile, newp, at_hole, bpos)
    bf, j, text = find_bind(files, e)
    own = file_defaults(files, bf, j)
    return lower_fexpr(text, inherit(at, own) if at_hole else own, files, bf, {}, at_hole, j)


SP_files_of_line = files_of_line                         # predspot's reader
PLACED = [False]              # lowering an argument a body in ANOTHER file places (CONST's second clause)


def files_of_line(pt, tail):                                 # noqa: F811
    """predspot's reader, with two more forms read mechanically from a line's tail: "in a program (library) file
    writing ITEM, then ITEM, ..." (ITEM: `@options(..)`, `name := `text``, `mac(p) := `text``; "then the program"
    ends the program file's list), and a macro `mac(p) := `text`` among the bindings."""
    FMACROS.clear()
    mw = list(re.finditer(r"in a (program|library) file writing (.*?)(?:, then the program|(?= in a (?:program|library)"
                          r" file)|$)", tail))
    if not mw:
        files = SP_files_of_line(pt, re.sub(r"[\w.]+\(\w+(?:, \w+)*\) := `[^`]*`(?: in a library file)?", "", tail))
        for mm in re.finditer(r"([\w.]+)\((\w+(?:, \w+)*)\) := `([^`]*)`( in a library file)?", tail):
            fn_ = "library" if mm.group(4) else "program"
            files.setdefault(fn_, [])
            FMACROS[mm.group(1)] = ([x.strip() for x in mm.group(2).split(",")], mm.group(3), fn_, len(files[fn_]))
        return files
    files = {"program": []}
    for mm in mw:
        fn_ = mm.group(1)
        files.setdefault(fn_, [])
        for it in re.split(r", then ", mm.group(2)):
            it = it.strip()
            mo = re.fullmatch(r"`@options\(([^)]*)\)`", it)
            mb = re.fullmatch(r"([\w.]+) := `([^`]*)`", it)
            mc = re.fullmatch(r"([\w.]+)\((\w+(?:, \w+)*)\) := `([^`]*)`", it)
            if mo:
                files[fn_].append(("opt", opts_of(mo.group(1))))
            elif mc:
                FMACROS[mc.group(1)] = ([x.strip() for x in mc.group(2).split(",")], mc.group(3), fn_, len(files[fn_]))
            elif mb:
                files[fn_].append(("bind", mb.group(1), mb.group(2)))
            else:
                raise FErr("an item the reader does not know: %s" % it)
    return files



# ---- predspot's engine plants, driven by this model's plant ids (the loaded code reads predspot's SABS)
for mine, theirs in (("s38", "s2"), ("s39", "s4"), ("s37", "s7"), ("s27", "s20"), ("s28", "s21"), ("s29", "s22"),
                     ("s30", "s28"), ("s31", "s29")):
    if s84(mine):
        SABS.add(theirs)

# ================================================================== the sweep (B7): every printed three-mode line, in its field
FIELDS = ("slugs", "rulings", "rejected", "readings", "evidence", "history")
SKIP_FIELDS = ("rejected", "history")                        # a quoted old line there is a record, not a claim


def sweep_lines84(docs):
    """(file, line no, line, answer, program, tail, field) of every printed three-mode line; `field` is the details
    field the line stands in (None in a base file)."""
    out = []
    for f in DOCF:
        field = None
        for ln, line_ in enumerate(docs[f].split("\n"), 1):
            if line_.startswith("## "):
                field = None
            mf = re.match(r"(%s):" % "|".join(FIELDS), line_)
            if mf and f.endswith("_details.md"):
                field = mf.group(1)
            if "WHOLE " not in line_ or " / FIND-ALL " not in line_:
                continue
            a = answer_part(line_)
            if not a:
                continue
            tail = line_[line_.index(a) + len(a):]
            mm = re.search(r"`([^`]*)`", tail)
            if mm:
                out.append((f, ln, line_, a, mm.group(1), tail, field))
    return out


def sw_table84(docs):
    out = {}
    for f, ln, line_, a, pt, tail, field in sweep_lines84(docs):
        if FLAGTAIL.search(tail):
            continue                                         # a flag line: FSWEEP's
        if field in SKIP_FIELDS and not s84("s14"):
            continue
        st, got = sweep_one(line_, a, pt, tail)
        out.setdefault(sw_key(f, line_, pt, tail), []).append((f, ln, st, got if st in ("same", "DIFF") else got[:160]))
    return out


if ENGINE84 == "old":
    for k, vs in sw_table84(OLD84).items():
        for f, ln, st, got in vs:
            print("SW\t%s\t%s\t%d\t%s\t%s" % (repr(k), f, ln, st, got))
    sys.exit(0)

# ================================================================== the checks
LINES.clear()
RUN.clear()
RESULTS = []


def check(name, ok, detail=""):                              # noqa: F811
    RESULTS.append((name, bool(ok)))
    print("%s %s: %s" % ("PASS" if ok else "FAIL", name, detail))


def ref(expr, binds=()):
    try:
        prog(expr, list(binds))
        return None
    except CompileError as e:
        return str(e)


def tp(expr, binds=()):
    try:
        return prog(expr, list(binds))
    except CompileError:
        return None


def wdiff(Pg, pred, texts):
    return sum(1 for t in texts if Pg.whole(t) != pred(t)) if Pg is not None else -1


def bt(binds):
    return "".join(", %s := `%s`" % tuple(b.split(" := ", 1)) for b in binds)


def dl(label, expr, binds, Pg, wh, sr, fa, tag, tail=""):
    return doc_line("%s%s (`%s`%s)%s" % ((label + ": ") if label else "", fmt(Pg, wh, sr, fa), expr, bt(binds), tail),
                    tag)


def has(msg, *subs):
    """REASON: a refusal counts only when its message names the expected rule."""
    return msg is not None and all(s in msg for s in subs)


def full(rx):
    return lambda t: re.fullmatch(rx, t) is not None


AD = "A := /(?<d>\\d)/"
ADIG = "A := [d = rx.digits]"
ADR = ("a template and not a spot in the pattern", AD_RULE)
NOTVIS = ("is not visible through",)

print("== CONTROL: the loaded matcher against python `re`")
QD = pop("37!", 3)
c1 = ndiff(answers(prog('"ab" | "a"'), pop("ab;", 4)), answers(Re(r"ab|a"), pop("ab;", 4)))
c2 = ndiff(answers(prog("identity(A)", [AD, "identity(x) := /${[(=) = x]}/"]), QD),
           answers(Re(r"\d" if not s84("s1") else r"\d!?"), QD))
check("CONTROL", (c1, c2) == ((0, 0, 0),) * 2, "differing (WHOLE, SEARCHED, FIND-ALL): `\"ab\" | \"a\"` %s; "
      "`identity(A)` against `\\d` %s over %d texts" % (c1, c2, len(QD)))

print("== ARGNAME (the ruling): the caller's read of an argument's label, the body using it alone, is refused")
r_n1 = ref("B(A) & (A.d: <5)", [AD, "B(rx) := /${rx}xx/"])
r_n2 = ref("C", ["C := B(A) & (A.d: <100)", ADIG, "B(rx) := /${rx}xx/"])
r_n3 = ref("B(A) & (A.d: <5)", [AD, "B(rx) := /${rx}-(?<d>\\d)/"])
r_n4 = ref("pair(A) & (A.d: <5)", [AD, "pair(p) := /${p},${p}/"])
P_n5 = tp("B(A) & (A.d: <5)", [AD, "B(rx) := /${[p = rx]}-(?<d>\\d)/"])
first_lt5 = lambda t: re.fullmatch(r"\d-\d", t) is not None and int(t[0]) < 5     # noqa: E731
DG = pop("37-", 3)
if P_n5 is not None:
    dl("A's own d, the body labelling the spot (case 2)", "B(A) & (A.d: <5)", [AD, "B(rx) := /${[p = rx]}-(?<d>\\d)/"],
       P_n5, ["7-3", "3-7", "3-3"], "7-3 3-7", "7-3 3-7 1-2 9-9", "core/labels/paths/call-prefix")
    dl("Visible through the call", "B(A) & (A.d: <5)", [AD, "B(rx) := /${[p = rx]}-(?<d>\\d)/"],
       P_n5, ["7-3", "3-7", "3-3"], "7-3 3-7", "7-3 3-7 1-2 9-9", "core/labels/paths/closed-argument")
TU = ["B(rx) := /${[p = rx]}-${rx}/", AD]
P_n6 = tp("B(A) & (A.d: <5)", TU)
if P_n6 is not None:
    dl("Both uses", "B(A) & (A.d: <5)", TU, P_n6, ["7-3", "3-7"], "7-3 3-7", "7-3 3-7 1-2 9-9",
       "core/labels/paths/argument-default")
check("ARGNAME", all(has(r, *ADR) for r in (r_n1, r_n2, r_n3, r_n4)) and wdiff(P_n5, first_lt5, DG) == 0 and
      wdiff(P_n6, first_lt5, DG) == 0,
      "refused naming argument-default: `B(A) & (A.d: <5)` B alone %s; his example 1 `C := B(A) & (A.d: <100)` %s; "
      "the body with its own d %s; `pair` using it twice alone %s; the spot labelled `[p = rx]`: `A.d` legal, "
      "against \"the FIRST digit under 5\" differing %d; both uses (alone and labelled): the labelled spot's, "
      "differing %d, over %d texts" % (has(r_n1, *ADR), has(r_n2, *ADR), has(r_n3, *ADR), has(r_n4, *ADR),
                                       wdiff(P_n5, first_lt5, DG), wdiff(P_n6, first_lt5, DG), len(DG)))
print("   refusal: %s" % r_n1)

print("== ARGLABEL (reading (a)): a part label written ON an argument labels a template: refused")
r_a1 = ref("C", ["C := B([a = A]) & (a.d: <100)", ADIG, "B(rx) := /${rx}xx/"])
r_a2 = ref("atomic([ab = B | A]) & (ab.l: <20)", ["A := /(?<l>\\d)\\d/", "B := /(?<l>\\d\\d)/"])
r_a3 = ref('rx.repeat([a = rx.digit], min = 1) & (a: "3")')
r_a4 = ref("B([a = A]) & (a.d: <5)", [AD, "B(rx) := /${[(=) = rx]}xx/"])
P_a5 = tp("B([a = A]) & (B.a.d: <5)", [AD, "B(rx) := /${[(=) = rx]}xx/"])
check("ARGLABEL", all(has(r, *ADR) for r in (r_a1, r_a2, r_a3, r_a4)),
      "refused naming argument-default: `B([a = A]) & (a.d: ..)` %s; `atomic([ab = B | A]) & (ab.l: <20)` %s; "
      "`rx.repeat([a = rx.digit], min = 1) & (a: \"3\")` %s; through a body that lists the spot, the caller's own "
      "`a.d` %s (the call's path `B.a.d`: %s)" % (has(r_a1, *ADR), has(r_a2, *ADR), has(r_a3, *ADR), has(r_a4, *ADR),
                                                  "legal" if P_a5 is not None else "refused"))
print("   refusal: %s" % r_a2)

print("== INPLACE (reading (b)): a group written in an argument in place is not the caller's; the body's is `B.d`")
BI = ["B(rx) := /${rx}-(?<d>\\d)/"]
r_i1 = ref("B(/(?<d>\\d)/) & (d: <5)", BI)
r_i2 = ref("B([x = /(?<d>\\d)/]) & (x.d: <5)", BI)
r_i3 = ref('hits(/a(?<g>x)?/) & (g: "x")')
P_i4 = tp("B(/(?<d>\\d)/) & (B.d: <5)", BI)
second_lt5 = lambda t: re.fullmatch(r"\d-\d", t) is not None and int(t[2]) < 5      # noqa: E731
if P_i4 is not None:
    dl("The first shape, settled", "B(/(?<d>\\d)/) & (B.d: <5)", BI, P_i4, ["7-3", "3-7"], "3-7 7-3", "7-3 3-7 1-2 9-9",
       "core/labels/paths/two-sources")
check("INPLACE", all(has(r, *ADR) for r in (r_i1, r_i2, r_i3)) and wdiff(P_i4, second_lt5, DG) == 0,
      "refused naming argument-default: bare `d` %s, `x.d` on the argument %s, `hits(..) & (g: \"x\")` %s; `B.d` "
      "reads the body's own d, against \"the SECOND digit under 5\" differing %d over %d texts" %
      (has(r_i1, *ADR), has(r_i2, *ADR), has(r_i3, *ADR), wdiff(P_i4, second_lt5, DG), len(DG)))

print("== ARGOWN (reading (c)): a read written inside the argument travels with the template")
OC = "occurrences(/(?<n>\\d+)/ & (n: <100))"
P_o = tp(OC)
DO = ["1234", "123", "12", "1", "12345", "100"]
want_o = {"1234": True, "123": True, "12": True, "1": True, "12345": True, "100": True}
check("ARGOWN", P_o is not None and all(P_o.whole(t) == want_o[t] for t in DO) if not s84("s40") else
      P_o is not None and P_o.whole("1234") is False,
      "`%s` legal %s; WHOLE over %s: %s (every text splits into hits under 100)" %
      (OC, P_o is not None, DO, [P_o.whole(t) for t in DO] if P_o else None))

print("== SPOT (reading (d), wrapper-export): a spot the body labels or lists passes the argument's labels on")
SB = [ADIG, "B(rx) := /${[dd = rx]}xx/"]
P_s1 = tp("B(A) & (B.dd.d: <100)", SB)
P_s1c = tp("C", ["C := B(A) & (B.dd.d: <100)"] + SB)
lt100 = lambda t: re.fullmatch(r"(0|[1-9]\d?)xx", t) is not None       # noqa: E731  (rx.digits then `xx`, under 100)
DX = [a + "xx" for a in pop("0147", 3)[1:]]
if P_s1 is not None:
    dl("Through a part label in the body", "B(A) & (B.dd.d: <100)", SB, P_s1, ["42xx", "100xx", "042xx"],
       "x100xx 42xx", "100xx 42xx 7xx 300xx", "core/labels/paths/argument-default")
if P_s1c is not None:
    dl("Example 1, the spot labelled", "C := B(A) & (B.dd.d: <100)", SB, P_s1c, ["42xx", "100xx", "042xx"],
       "x100xx 42xx", "100xx 42xx 7xx 300xx", "core/holes/bare-condition/nested-scope")
P_s2 = tp('hits(/a(?<g>x)?/) & (hits.hit.g: "x")')
P_s3 = tp('occurrences(/(?<n>\\d+)/) & (occurrences.hit.n: "3")')
P_s4 = tp("peek(/(?<d>\\d)/) SEQ /\\d\\d/ & (peek.d: <5)")
P_s5 = tp("atomic(/(?<l>\\d\\d)/ | /(?<l>\\d)\\d/) & (atomic.l: <20)")
r_s6 = ref("atomic(B | A) & (atomic.l: <20)", ["A := /(?<l>\\d)\\d/", "B := /(?<l>\\d\\d)/"])
P_s7 = tp('endsWith(/(?<n>\\d+)/) & (endsWith.n: "3")')
P_s8 = tp('contains(/(?<n>\\d)/) & (contains.n: "3")')
P_s9 = tp('padded(/(?<v>\\d)/) & (padded.v: "5")')
for lab, e, Pg, wh, sr, fa, tg in [
        ("The argument's group, through the hit", 'occurrences(/(?<n>\\d+)/) & (occurrences.hit.n: "3")', P_s3,
         ["a1b3", "a3b1", "ab"], "x1 3", "a3 b1 3", "lib/search/occurrences"),
        ("Read through the call", "peek(/(?<d>\\d)/) SEQ /\\d\\d/ & (peek.d: <5)", P_s4, ["37", "73"], "x73 37",
         "37 73 56", "lib/control/peek"),
        ("", "atomic(/(?<l>\\d\\d)/ | /(?<l>\\d)\\d/) & (atomic.l: <20)", P_s5, ["25", "13"], "25", "25 13",
         "core/patterns/atomic")]:
    if Pg is not None:
        dl(lab, e, [], Pg, wh, sr, fa, tg)
last_g = lambda t: bool(re.findall(r"ax?", t)) and re.findall(r"ax?", t)[-1] == "ax"    # noqa: E731  (the last hit sets g)
peekd = lambda t: re.fullmatch(r"\d\d", t) is not None and int(t[0]) < 5      # noqa: E731
ends3 = lambda t: t.endswith("3")                     # noqa: E731  (some split of the greedy gap gives n = `3`)
P_ok = [x is not None for x in (P_s1, P_s1c, P_s2, P_s3, P_s4, P_s5, P_s7, P_s8, P_s9)]
spot_d = (wdiff(P_s1, lt100, DX), wdiff(P_s2, last_g, pop("ax", 4)), wdiff(P_s4, peekd, pop("37", 2)),
          wdiff(P_s5, lambda t: re.fullmatch(r"1\d", t) is not None, pop("125", 2)),
          wdiff(P_s7, ends3, pop("ab13", 3)))
check("SPOT", all(P_ok) and has(r_s6, *NOTVIS) and spot_d == (0,) * 5,
      "legal: `B.dd.d` (his example 3's spot) / at C, `hits.hit.g`, `occurrences.hit.n`, `peek.d`, `atomic.l` over an "
      "expression, `endsWith.n`, `contains.n`, `padded.v`: %s; `atomic(B | A) & (atomic.l: ..)` (bindings used alone "
      "in the argument export nothing) refused %s; differing from direct predicates (`B.dd.d` under 100; the last "
      "hit's g is x; peek's first digit under 5; atomic's `l` under 20 is the 1x numbers; endsWith's greedy-gap last "
      "run is `3`): %s" % (P_ok, has(r_s6, *NOTVIS), spot_d))

print("== TWOSPOT (the cases): two spots of one argument, several arguments, a looped spot")
P_t1 = tp('list_of(/(?<h>\\d)/, sep = ",") & (list_of.h: "5")')
P_t2 = tp("pair(A) & (pair.d: <5)", [AD, "pair(p) := /${[(=) = p]},${[(=) = p]}/"])
WB = ["W(a, b) := [(=) = a] SEQ [(=) = b]"]
P_t3 = tp('W(/(?<h>\\d)/, /;(?<h>\\d)/) & (W.h: "3")', WB)
P_t4 = tp('[r = rx.repeat(/(?<a>\\d)/, min = 1)] & (r.a: "3")')
P_t5 = tp('[r = rx.repeat(/(?<a>\\d)/, min = 1)] & some((r.a: "7"))')
for lab, e, b_, Pg, wh, sr, fa, tg in [
        ("The last item, through the call", 'list_of(/(?<h>\\d)/, sep = ",") & (list_of.h: "5")', [], P_t1,
         ["7,3,5", "7,5,3"], "x7,5 3,5", "1,5 3 5", "lib/records/list-of"),
        ("An argument used twice by the body", "pair(A) & (pair.d: <5)", [AD, "pair(p) := /${[(=) = p]},${[(=) = p]}/"],
         P_t2, ["7,3", "3,7", "3,3"], "3,7 7,3", "7,3 3,7 1,2 9,9", "core/labels/paths/call-prefix"),
        ("Two arguments", 'W(/(?<h>\\d)/, /;(?<h>\\d)/) & (W.h: "3")', WB, P_t3, ["7;3", "3;7"], "x3;7 7;3",
         "7;3 3;7 1;3", "lib/convention/argument-labels"),
        ("The last item, through a label on the call", '[r = rx.repeat(/(?<a>\\d)/, min = 1)] & (r.a: "3")', [], P_t4,
         ["73", "37"], "x37 73", "73 37 13", "lib/rx/repeat"),
        ("Every item, a group question", '[r = rx.repeat(/(?<a>\\d)/, min = 1)] & some((r.a: "7"))', [], P_t5,
         ["73", "33"], "x33 73", "73 33 17", "lib/rx/repeat")]:
    if Pg is not None:
        L_ = dl(lab, e, b_, Pg, wh, sr, fa, tg)
        if lab == "Two arguments":
            LINES[-1] = (tg, L_.replace("W(a, b) := `[(=) = a] SEQ [(=) = b]`)",
                                        "W(a, b) := `[(=) = a] SEQ [(=) = b]`, the shape of when's then branch)"))
last5 = lambda t: re.fullmatch(r"\d(,\d)*", t) is not None and t[-1] == "5"          # noqa: E731
pair2 = lambda t: re.fullmatch(r"\d,\d", t) is not None and int(t[2]) < 5 if not s84("s41") else \
    (re.fullmatch(r"\d,\d", t) is not None and int(t[0]) < 5)                        # noqa: E731
w2 = lambda t: re.fullmatch(r"\d;\d", t) is not None and t[2] == "3"                  # noqa: E731
r_last = lambda t: re.fullmatch(r"\d+", t) is not None and t[-1] == "3"              # noqa: E731
r_some = lambda t: re.fullmatch(r"\d+", t) is not None and "7" in t                   # noqa: E731
tw = (wdiff(P_t1, last5, pop("35,", 5)), wdiff(P_t2, pair2, pop("37,", 3)), wdiff(P_t3, w2, pop("37;", 3)),
      wdiff(P_t4, r_last, pop("37", 3)), wdiff(P_t5, r_some, pop("37", 3)))
check("TWOSPOT", tw == (0,) * 5,
      "differing from direct predicates: list_of's last item is 5 %d; pair's two spots, the last mention (the second "
      "digit) %d; W's two arguments, one label, the last mention %d; rx.repeat's looped spot, the last item %d, a "
      "group question every item %d" % tw)

print("== USERMACRO (his pair): `identity` passes the labels on, `hide` none; both match what x matches")
IDB, HDB = "identity(x) := /${[(=) = x]}/", "hide(x) := /${x}/"
P_u1 = tp("identity(A) & (identity.d: <5)", [AD, IDB])
r_u2 = ref("hide(A) & (hide.d: <5)", [AD, HDB] if not s84("s42") else [AD, HDB.replace("${x}", "${[(=) = x]}")])
P_h, P_id = tp("hide(A)", [AD, HDB]), tp("identity(A)", [AD, IDB])
QU = pop("37 ", 3)
if P_u1 is not None:
    dl("identity", "identity(A) & (identity.d: <5)", [AD, IDB], P_u1, ["3", "7"], "7 3", "3 7 4",
       "lib/convention/argument-labels")
if P_h is not None:
    L_ = dl("The same match, either body", "hide(A)", [AD, HDB], P_h, ["3", "7"], "7 3", "3 7 4",
            "lib/convention/argument-labels")
    LINES[-1] = (LINES[-1][0], L_[:-1] + "; `identity(A)` alike)")
same_m = ndiff(answers(P_h, QU), answers(P_id, QU)) if P_h and P_id else None
check("USERMACRO", wdiff(P_u1, lambda t: t in ("0", "1", "2", "3", "4"), pop("0378", 1)) == 0 and has(r_u2, *NOTVIS)
      and same_m == (0, 0, 0),
      "`identity(A) & (identity.d: <5)` legal, differing %d; `hide(A) & (hide.d: <5)` refused (hide exports no `d`) "
      "%s; `hide(A)` against `identity(A)` differing %s over %d texts" %
      (wdiff(P_u1, lambda t: t in ("0", "1", "2", "3", "4"), pop("0378", 1)), has(r_u2, *NOTVIS), same_m, len(QU)))
print("   refusal: %s" % r_u2)

print("== PLACES (the census): every provided body that places a parameter in a pattern hole writes the list or "
      "labels the spot")
LIBNOW = NOWS["library.md"]
BODY_RX = re.compile(r"`((?:rx\.)?\w+)\(([\w, =/\"]*)\) :=\s+([^`]+)`")
SET_ARGS = {("between",), ("prefix_in",)}
census, cbad = [], []
BODY_RX2 = re.compile(r"`(\w+)\(([\w, =]*)\)` (?:is the plain gap body|is the plain macro|is the separated list|is the lazy-gap loop|reads "
                      r"only the text inside double quotes: the body) `([^`]+)`")
BODIES = [(m_.group(1), m_.group(2), m_.group(3)) for m_ in BODY_RX.finditer(ws(LIBNOW))] + \
    [(m_.group(1), m_.group(2), m_.group(3)) for m_ in BODY_RX2.finditer(ws(LIBNOW))]
for nm, heads, body in BODIES:
    if nm == "list_of":
        heads = heads.replace("sep = S", "S")
    if nm in ("hide", "identity", "pair", "W", "B"):
        continue
    params = [h.split("=")[0].strip() for h in heads.split(",") if h.strip()]
    if s84("s34") and nm == "peek":
        body = "/(?=${A})/"
    for p_ in params:
        alone = re.findall(r"\$\{\s*%s\s*\}" % re.escape(p_), body)
        listed = re.findall(r"\$\{\s*\[\(=\) = %s\]" % re.escape(p_), body) + \
            re.findall(r"\[\(=\) = %s\]" % re.escape(p_), body)
        spot = re.findall(r"\(\?<:\w+>\$\{\s*%s\s*\}\)" % re.escape(p_), body)
        count_hole = re.search(r"\{\$\{\s*%s\s*\}|\$\{\s*%s\s*\},|,\$\{\s*%s\s*\}\}|<\$\{\s*%s\s*\}>" %
                               ((re.escape(p_),) * 4), body)
        class_pos = re.search(r"\[[^\]]*\$\{\s*%s\s*\}[^\]]*\]" % re.escape(p_), body)
        kind = ("listed" if listed else "spot-labelled" if spot else "count/name hole" if count_hole and not listed
                else "class position (no pattern)" if class_pos else "alone" if alone else "not placed in a hole")
        census.append((nm, p_, kind))
        if kind == "alone" and len(alone) > len(spot):
            cbad.append((nm, p_))
for c_ in census:
    print("   %-12s %-5s %s" % c_)
check("PLACES", census and not cbad, "%d (body, parameter) pairs read from library.md's body texts (`name(..) := "
      "..`): %s; a parameter placed alone in a hole: %s" %
      (len(census), ", ".join("%s %d" % (k, sum(1 for c_ in census if c_[2] == k)) for k in
                              sorted(set(c_[2] for c_ in census))), cbad or "none"))

print("== CONVENTION: the convention stated once; every covered body's piece points at it")
CONV = ("A provided body that places its argument in the match passes that argument's labels on, by the export list "
        "on each spot, unless its piece says otherwise.")
covered = ["lib/control/peek", "lib/control/atomic", "lib/control/when", "lib/records/list-of",
           "lib/modifiers/padded", "lib/modifiers/quoted", "lib/search/anchored", "lib/modifiers/any-case",
           "lib/search/contains", "lib/search/starts-with", "lib/search/ends-with", "lib/rx/repeat",
           "lib/structural/capture"]
if s84("s35"):
    covered.append("lib/search/between")
pieces = re.split(r"\n(?=### )", LIBNOW)
nopoint = []
for tg in covered:
    pc = next((p_ for p_ in pieces if "[%s]" % tg in p_.split("\n")[0]), "")
    if "lib/convention/argument-labels" not in pc:
        nopoint.append(tg)
conv_n = ws(LIBNOW).count(ws(CONV))
check("CONVENTION", conv_n == 1 and not nopoint, "the convention sentence occurs %d time(s) in library.md; covered "
      "pieces not pointing at lib/convention/argument-labels: %s (of %d)" % (conv_n, nopoint or "none", len(covered)))

print("== GRID: the name grid, spelling x occurrences of its source x read kind; each cell its deciding sentence")
# predfix83's grid (its spellings, occurrences and read kinds, unchanged) with the argument cells DECIDED by the
# ruling, and three spellings added: a spot the body labels (`B.p.h`), the export list on a spot (`B.h`), a part
# label written on an argument (`a.h`, reading (a)).
G_A = "A := /(?<h>\\d)/"
G_B = "B(rx) := /${rx}(?<d>\\d)/"
G_I1 = "i1 := [year = /\\d/] SEQ /\\d/"
G_I2 = "i2 := /\\d/ SEQ [year = /\\d/]"
G_ARG = "B(rx) := /${rx}x/"
G_SPOT = "B(rx) := /${[p = rx]}x/"
G_LIST = "B(rx) := /${[(=) = rx]}x/"
SPELL = [
    ("bare", {"one": ("h", "/(?<h>\\d)/", []), "seq": ("h", "/(?<h>\\d)/ SEQ /(?<h>\\d)/", []),
              "and": ("h", "/(?<h>\\d)\\d/ & /\\d(?<h>\\d)/", []),
              "nest": ("h", "X", ["X := /(?<h>\\d)/ SEQ \"!\""])}),
    ("binding", {"one": ("A.h", "A", [G_A]), "seq": ("A.h", "A SEQ A", [G_A]), "and": ("A.h", "A & A", [G_A]),
                 "nest": ("X.A.h", "X", ["X := A SEQ \"!\"", G_A])}),
    ("macro", {"one": ("B.d", "B(/\\d/)", [G_B]), "seq": ("B.d", "B(/\\d/) SEQ B(/\\d/)", [G_B]),
               "and": ("B.d", "B(/\\d/) & B(/\\d/)", [G_B]), "nest": ("X.B.d", "X", ["X := B(/\\d/) SEQ \"!\"", G_B])}),
    ("part-label", {"one": ("x.h", "[x = A]", [G_A]), "seq": ("x.h", "[x = A] SEQ [x = A]", [G_A]),
                    "and": ("x.h", "[x = /(?<h>\\d)\\d/] & [x = /\\d(?<h>\\d)/]", []),
                    "nest": ("X.x.h", "X", ["X := [x = A] SEQ \"!\"", G_A])}),
    ("export-list", {"one": ("year", "[(=year) = i1]", [G_I1]),
                     "seq": ("year", "[(=year) = i1] SEQ [(=year) = i1]", [G_I1]),
                     "and": ("year", "[(=year) = i1] & [(=year) = i2]", [G_I1, G_I2]),
                     "nest": ("X.year", "X", ["X := [(=year) = i1] SEQ \"!\"", G_I1])}),
    ("argument", {"one": ("A.h", "B(A)", [G_A, G_ARG]), "seq": ("A.h", "B(A) SEQ B(A)", [G_A, G_ARG]),
                  "and": ("A.h", "B(A) & B(A)", [G_A, G_ARG]),
                  "nest": ("X.A.h", "X", ["X := B(A) SEQ \"!\"", G_A, G_ARG])}),
    ("spot-label", {"one": ("B.p.h", "B(A)", [G_A, G_SPOT]), "seq": ("B.p.h", "B(A) SEQ B(A)", [G_A, G_SPOT]),
                    "and": ("B.p.h", "B(A) & B(A)", [G_A, G_SPOT]),
                    "nest": ("X.B.p.h", "X", ["X := B(A) SEQ \"!\"", G_A, G_SPOT])}),
    ("export-list-on-spot", {"one": ("B.h", "B(A)", [G_A, G_LIST]), "seq": ("B.h", "B(A) SEQ B(A)", [G_A, G_LIST]),
                             "and": ("B.h", "B(A) & B(A)", [G_A, G_LIST]),
                             "nest": ("X.B.h", "X", ["X := B(A) SEQ \"!\"", G_A, G_LIST])}),
    ("argument-label", {"one": ("a.h", "B([a = A])", [G_A, G_LIST]),
                        "seq": ("a.h", "B([a = A]) SEQ B([a = A])", [G_A, G_LIST]),
                        "and": ("a.h", "B([a = A]) & B([a = A])", [G_A, G_LIST]),
                        "nest": ("X.a.h", "X", ["X := B([a = A]) SEQ \"!\"", G_A, G_LIST])}),
]
READS = [("plain", "%s & (%s: \"3\")"), ("$", "(%s) SEQ $%s"), ("group", "%s & some((%s: \"3\"))"),
         ("index", "%s & (%s[1]: \"3\")")]
S = {
    "lr-bare": ("core/labels/paths/label-reference", "a bare name is a label the definition itself writes"),
    "lr-src": ("core/labels/paths/label-reference", "A label not written in the text of the definition that "
               "references it is referenced with its source"),
    "flow-seq": ("core/labels/flow", "Across the sequence operator a name both parts surface is one label, the last "
                 "mention"),
    "reads": ("core/values/reads", "`$x` and `x:` never disagree"),
    "array": ("core/labels/labels-vs-captures/array-vs-passes", "The group questions (`some`, `count`, `occurs`) and "
              "the index `h[k]` read the array of a name's settings: every setting, in order"),
    "flow-and": ("core/labels/flow", "Across `&` a name both sides surface is an ambiguous reference: a compile error "
                 "where a condition or a `$` references it"),
    "flow-gq": ("core/labels/flow", "A group question over a name both sides of `&` surface reads both sides' "
                "settings"),
    "unordered": ("core/labels/paths", "the two sides of `&` are not ordered"),
    "one-use": ("core/labels/paths/one-use-read", "With ONE use, a plain read through a binding's prefix (`A.h`) is "
                "legal"),
    "bp-twice": ("core/labels/paths/binding-prefix", "a plain read through it with the binding used twice or more is "
                 "a compile error"),
    "bp-dollar": ("core/labels/paths/binding-prefix", "`$chars.ch` alike"),
    "bp-gq": ("core/labels/paths/binding-prefix", "a group question through it reads every use's settings, in order"),
    "bp-idx": ("core/labels/paths/binding-prefix", "The index `A.h[k]` through the prefix is in text order across "
               "sequenced uses; through uses joined by `&` it is a compile error for now"),
    "bp-nest": ("core/labels/paths/binding-prefix", "`X.D.h` is a compile error, D used alone in X"),
    "cp-once": ("core/labels/paths/call-prefix", "called once in the definition, a plain read through the name is "
                "legal"),
    "cp-twice": ("core/labels/paths/call-prefix", "called more than once, a plain read is the compile error saying "
                 "to label the call, and a group question reads every call's settings, in order"),
    "cp-same": ("core/labels/paths/binding-prefix", "a MACRO's name is a prefix too, under the same two rules"),
    "occ-and": ("lib/search/occurrences", "only the index `h[k]` across `&` is refused for now"),
    "paths-alone": ("core/labels/paths", "an unlabelled use carries the implicit label of the binding's name, protected"),
    "pl-last": ("core/labels/paths", "a part label mentioned more than once names its last mention where the "
                "reference is written"),
    "lr-dollar": ("core/labels/paths/label-reference", "`$x` reads alike"),
    "st3": ("core/labels/export", "through a public part label, the labels that part exports, by path"),
    "el-bare": ("core/labels/export/export-list", "the binding takes the listed labels of the part as labels of its "
                "own (exported; read bare inside it)"),
    "el-two": ("core/labels/export/export-list", "Two lists that name one label give the same label, the last "
               "mention"),
    "el-alias": ("core/labels/export/export-list", "A listed label is an alias of the part's label: the same "
                 "settings and array"),
    "ad-rule": ("core/labels/paths/argument-default", "the caller's read of that argument's labels (`A.d` in `B(A)`, a "
                "group written in place) is a compile error: the argument is a template"),
    "ad-a": ("core/labels/paths/argument-default", "a part label written ON an argument at a call labels a template, "
             "not a spot"),
    "ad-d": ("core/labels/paths/argument-default", "a spot the body labels exports the argument's exported labels "
             "through that label"),
    "spot-list": ("lib/convention/argument-labels", "the list on it, `[(=) = x]`, takes every label the argument "
                  "exports as the body's own"),
    "bp-text": ("core/labels/paths/binding-prefix", "\"Used more than once\" is counted in the TEXT of the "
                "definition the reference is written in"),
    "cA": ("core/labels/paths", "a call's label reaches no argument by the argument's name"),
}
REF_FLOW = "refused:core/labels/flow"
REF_BP = "refused:used 2 times"
REF_SRC = "refused:with its source"
REF_VIS = "refused:not visible through"
REF_AD = "refused:" + AD_RULE
EXPECT = {
    ("bare", "one"): [("legal", "lr-bare")] * 2 + [("legal", "array")] * 2,
    ("bare", "seq"): [("legal", "flow-seq"), ("legal", "reads"), ("legal", "array"), ("legal", "array")],
    ("bare", "and"): [(REF_FLOW, "flow-and"), (REF_FLOW, "flow-and"), ("legal", "flow-gq"), (REF_FLOW, "unordered")],
    ("bare", "nest"): [(REF_SRC, "lr-src")] * 4,
    ("binding", "one"): [("legal", "one-use")] * 2 + [("legal", "bp-gq"), ("legal", "bp-idx")],
    ("binding", "seq"): [(REF_BP, "bp-twice"), (REF_BP, "bp-dollar"), ("legal", "bp-gq"), ("legal", "bp-idx")],
    ("binding", "and"): [(REF_BP, "bp-twice"), (REF_BP, "bp-dollar"), ("legal", "bp-gq"),
                         ("refused:not ordered", "bp-idx")],
    ("binding", "nest"): [(REF_VIS, "bp-nest")] * 4,
    ("macro", "one"): [("legal", "cp-once")] * 2 + [("legal", "cp-twice"), ("legal", "cp-same")],
    ("macro", "seq"): [(REF_BP, "cp-twice"), (REF_BP, "cp-same"), ("legal", "cp-twice"), ("legal", "cp-same")],
    ("macro", "and"): [(REF_BP, "cp-twice"), (REF_BP, "cp-same"), ("legal", "cp-twice"),
                       ("refused:not ordered", "occ-and")],
    ("macro", "nest"): [(REF_VIS, "paths-alone")] * 4,
    ("part-label", "one"): [("legal", "st3"), ("legal", "lr-dollar"), ("legal", "array"), ("legal", "array")],
    ("part-label", "seq"): [("legal", "pl-last"), ("legal", "lr-dollar"), ("legal", "array"), ("legal", "array")],
    ("part-label", "and"): [(REF_FLOW, "unordered"), (REF_FLOW, "flow-and"), ("legal", "flow-gq"),
                            (REF_FLOW, "unordered")],
    ("part-label", "nest"): [("legal", "st3")] * 4,
    ("export-list", "one"): [("legal", "el-bare")] * 2 + [("legal", "el-alias")] * 2,
    ("export-list", "seq"): [("legal", "el-two"), ("legal", "el-two"), ("legal", "el-alias"), ("legal", "el-alias")],
    ("export-list", "and"): [(REF_FLOW, "flow-and"), (REF_FLOW, "flow-and"), ("legal", "flow-gq"),
                             (REF_FLOW, "unordered")],
    ("export-list", "nest"): [("legal", "el-bare")] * 4,
    # the seven cells UNDECIDED under predfix83, decided by the ruling:
    ("argument", "one"): [(REF_AD, "ad-rule")] * 4,
    # (predfix83's four `used 2 times` cells of seq / and now refused by the ruling first: a template's label is no
    # spot's, so the count of uses never arises)
    ("argument", "seq"): [(REF_AD, "ad-rule")] * 4,
    ("argument", "and"): [(REF_AD, "ad-rule")] * 3 + [("refused:not ordered", "bp-idx")],
    ("argument", "nest"): [(REF_VIS, "cA")] * 4,
    ("spot-label", "one"): [("legal", "ad-d")] * 2 + [("legal", "cp-twice"), ("legal", "cp-same")],
    ("spot-label", "seq"): [(REF_BP, "cp-twice"), (REF_BP, "cp-same"), ("legal", "cp-twice"), ("legal", "cp-same")],
    ("spot-label", "and"): [(REF_BP, "cp-twice"), (REF_BP, "cp-same"), ("legal", "cp-twice"),
                            ("refused:not ordered", "occ-and")],
    ("spot-label", "nest"): [(REF_VIS, "paths-alone")] * 4,
    ("export-list-on-spot", "one"): [("legal", "spot-list")] * 2 + [("legal", "cp-twice"), ("legal", "cp-same")],
    ("export-list-on-spot", "seq"): [(REF_BP, "cp-twice"), (REF_BP, "cp-same"), ("legal", "cp-twice"),
                                     ("legal", "cp-same")],
    ("export-list-on-spot", "and"): [(REF_BP, "cp-twice"), (REF_BP, "cp-same"), ("legal", "cp-twice"),
                                     ("refused:not ordered", "occ-and")],
    ("export-list-on-spot", "nest"): [(REF_VIS, "paths-alone")] * 4,
    ("argument-label", "one"): [(REF_AD, "ad-a")] * 4,
    ("argument-label", "seq"): [(REF_AD, "ad-a")] * 4,
    ("argument-label", "and"): [(REF_AD, "ad-a")] * 4,
    ("argument-label", "nest"): [(REF_VIS, "paths-alone")] * 4,
}
# ---- review r84: B2's spelling (a part label over a call, read by path), B5's cause arm (a label no text writes)
# and its real UNDECIDED arm (the open spot-read-name: the engine's answer printed, no verdict)
G_UND = "undecided:spot-read-name"
SPELL += [
    ("part-label-on-call", {"one": ("c.p.h", "[c = B(A)]", [G_A, G_SPOT]),
                            "seq": ("c.p.h", "[c = B(A)] SEQ [c = B(A)]", [G_A, G_SPOT]),
                            "and": ("c.p.h", "[c = B(A)] & [c = B(A)]", [G_A, G_SPOT]),
                            "nest": ("X.c.p.h", "X", ["X := [c = B(A)] SEQ \"!\"", G_A, G_SPOT])}),
    ("argument-no-such-label", {"one": ("A.zz", "B(A)", [G_A, G_ARG])}),
    ("spot-argument-name", {"one": ("A.h", "B(A)", [G_A, G_SPOT])}),
]
S.update({
    "st3-path": ("core/labels/export", "through a public part label, the labels that part exports, by path"),
    "not-visible": ("core/labels/paths", "A path to a label NOT VISIBLE through its source is a compile error, a "
                    "typo'd path (`c.e`) alike"),
    "open-srn": ("core/labels/paths/closed-argument", "open spot-read-name"),
})
EXPECT.update({
    ("part-label-on-call", "one"): [("legal", "st3-path"), ("legal", "lr-dollar"), ("legal", "array"),
                                    ("legal", "array")],
    ("part-label-on-call", "seq"): [("legal", "pl-last"), ("legal", "lr-dollar"), ("legal", "array"),
                                    ("legal", "array")],
    ("part-label-on-call", "and"): [(REF_FLOW, "unordered"), (REF_FLOW, "flow-and"), ("legal", "flow-gq"),
                                    (REF_FLOW, "unordered")],
    ("part-label-on-call", "nest"): [("legal", "st3-path")] * 4,
    ("argument-no-such-label", "one"): [(REF_VIS, "not-visible")] * 4,
    ("spot-argument-name", "one"): [(G_UND, "open-srn")] * 4,
})
if s84("s5"):
    EXPECT[("argument", "one")][0] = ("legal", "ad-rule")
if s84("s8"):
    S["open-srn"] = ("core/labels/paths/closed-argument", "open spot-name-read")


def piece_of(tag, docs=None):
    """The text of one base piece (its heading line to the next heading): a deciding sentence is looked for THERE."""
    docs = docs or NOWS
    for f in ("core.md", "library.md", "parked.md"):
        for pc in re.split(r"\n(?=#{2,3} )", docs[f]):
            if pc.split("\n")[0].rstrip().endswith("[%s]" % tag) or ("[%s]" % tag) in pc.split("\n")[0]:
                return pc
    return ""


def drill(expr, binds):
    """B1's rename drill: every binding the cell names renamed to a parameter name of a macro the cell uses."""
    pnames = [h.strip() for b in binds for mm in [re.match(r"(\w+)\(([\w, ]+)\) :=", b)] if mm
              for h in mm.group(2).split(",")]
    if not pnames:
        return None
    names = [re.match(r"([\w.]+) :=", b).group(1) for b in binds if re.match(r"[\w.]+ :=", b)]
    mp = {n: pnames[0] for n in names if n == "A"}
    if not mp:
        return None
    sub = lambda t: re.sub(r"(?<![\w.])A\b", pnames[0], t)    # noqa: E731
    return sub(expr), [sub(b) if not re.match(r"\w+\(", b) else b for b in binds]


def verdict(expr, binds, alpha):
    vl = ref(expr, binds)
    if vl is not None:
        return ("refused",)
    Pl = tp(expr, binds)
    return ("legal", tuple(t for t in pop(alpha, 4) if t and Pl.whole(t)))


GCNT = {"AGREE": 0, "DISAGREE": 0, "UNDECIDED": 0}
GBAD, GQMISS, GDRILL = [], [], []
NDRILL = [0]
for sp, occs in SPELL:
    for oc in [o for o in ("one", "seq", "and", "nest") if o in occs]:
        R_, P_, B_ = occs[oc]
        base = tp(P_, B_)
        alpha = "37x!" if sp not in ("bare", "binding", "part-label", "export-list") or oc == "nest" else "37"
        for (rk, form), (exp, skey) in zip(READS, EXPECT[(sp, oc)]):
            expr = form % (P_, R_)
            tag_, words = S[skey]
            if ws(words) not in ws(piece_of(tag_)):
                GQMISS.append((sp, oc, rk, skey))
            vl = ref(expr, B_)
            Pl = tp(expr, B_)
            if vl is not None:
                got = "REFUSED (%s)" % vl
            else:
                hs = [t for t in pop(alpha, 5) if t and Pl.whole(t)][:2]
                fs = [t for t in pop(alpha, 5) if t and base is not None and base.whole(t) and not Pl.whole(t)][:1]
                got = fmt(Pl, (hs + fs) or ["x"], ("x" + hs[0]) if hs else "x", " ".join(hs + fs) if hs else "x")
            if exp.startswith("undecided:"):
                st = "UNDECIDED"
            else:
                ok = (vl is None) if exp == "legal" else (vl is not None and exp.split(":", 1)[1] in vl)
                st = "AGREE" if ok else "DISAGREE"
                if not ok:
                    GBAD.append((sp, oc, rk, vl))
            GCNT[st] += 1
            dr = drill(expr, B_)
            dtxt = ""
            if dr:
                NDRILL[0] += 1
                DRILL[0] = True
                try:
                    v0, v1 = verdict(expr, B_, alpha), verdict(dr[0], dr[1], alpha)
                finally:
                    DRILL[0] = False
                dtxt = " | drill `%s`%s: %s" % (dr[0], bt(dr[1]), "same" if v0 == v1 else "MOVED")
                if v0 != v1:
                    GDRILL.append((sp, oc, rk, dr[0]))
            print("   %-22s %-4s %-5s | `%s`%s | %s: \"%s\" | %s | %s%s" % (sp, oc, rk, expr, bt(B_), tag_, words, exp,
                                                                        got[:240], dtxt))
            print("      -> %s" % st)
NCELLS = sum(GCNT.values())
print("   GRID SUMMARY: %d cells: AGREE %d, DISAGREE %d, UNDECIDED %d (declared: the 4 cells of the open "
      "spot-read-name); rename drill %d cells, moved %d; deciding sentences not found in their piece: %s" %
      (NCELLS, GCNT["AGREE"], GCNT["DISAGREE"], GCNT["UNDECIDED"], NDRILL[0], len(GDRILL), GQMISS or "none"))
check("GRID", not GBAD and not GQMISS and not GDRILL and NCELLS == 168 and GCNT["UNDECIDED"] == 4 and NDRILL[0] > 0,
      "%d cells (predspot's 144; a part label over a call 16; a label no text writes 4; the open spot-read-name 4): "
      "AGREE %d, DISAGREE %d %s, UNDECIDED %d (each its open slug in its piece); rename drill (a binding named like "
      "the macro's parameter) %d cells, moved %d %s; sentences missing from their piece %s" %
      (NCELLS, GCNT["AGREE"], GCNT["DISAGREE"], GBAD[:3], GCNT["UNDECIDED"], NDRILL[0], len(GDRILL), GDRILL[:3],
       GQMISS or "none"))

print("== AWAITS: no line or sentence of the three base files still awaits argument-default")
aw_left = [(f, i + 1) for f in ("core.md", "library.md", "parked.md") for i, l_ in enumerate(NOWS[f].split("\n"))
           if "awaits argument-default" in l_ or ("open argument-default" in l_ and l_.startswith("### "))]
aw_old = sum(OLDS[f].count("awaits argument-default") for f in ("core.md", "library.md", "parked.md"))
if s84("s43"):
    aw_left = []
    aw_old = 0
check("AWAITS", aw_old > 0 and not aw_left, "\"awaits argument-default\" in the base files at the starting commit: %d "
      "(`git show %s:<file> | grep -c`); left now: %s" % (aw_old, START_S, aw_left or "none"))

print("== SWEEP: every printed three-mode line (`rejected:` and history lines skipped), predspot's engine over the "
      "starting documents against this one over these; every non-same status DECLARED with its reason; no answer "
      "moves unless listed")
import ast                                                   # noqa: E402
NEW_T = sw_table84(NOWS)
OLD_T = {}
if not LIGHT84:
    envo = {k: v for k, v in os.environ.items() if not k.endswith("_SABOTAGE")}
    envo["PREDFIX84_ENGINE"] = "old"
    oo = subprocess.run([sys.executable, "-I", "-B", os.path.abspath(__file__)], capture_output=True, text=True,
                        env=envo, timeout=1500).stdout
    for l_ in oo.split("\n"):
        if l_.startswith("SW\t"):
            _, k_, f_, ln_, st_, got_ = l_.split("\t", 5)
            OLD_T.setdefault(ast.literal_eval(k_), []).append((f_, int(ln_), st_, got_))
NOTMOD = "not modelled (the header's list); the printed line is RIGHT (review r84 B7, the coordinator's re-run): "
DECL_LINE = {      # (file, program) -> (status, reason): a line this engine does not reproduce
    ("core.md", "/\\d+/ & /^\\d$/"): ("DIFF", NOTMOD + "`^` / `$` inside an operand of `&` read the operand's stretch"),
    ("core.md", "wb SEQ digits SEQ wb"): ("DIFF", NOTMOD + "`\\b`"),
    ("core.md", "/(?=\\d*(?<l>\\d)\\b)(?<f>\\d)\\d*/ & (l: > $f)"): ("DIFF", NOTMOD + "`\\b` in a lookahead"),
    ("core.md", "/(?:(?<h>\\d+)(?::(?<m>\\d\\d))?,)*\\k<m>/ & (m: \"45\")"): ("DIFF", NOTMOD + "a backreference"),
    ("core.md", "A SEQ B"): ("DIFF", NOTMOD + "a backreference to a part (B's `\\k<c>` reads A's group)"),
    ("core.md", "[h = rx.digit] SEQ ((h: <5))?"): ("CRASH", NOTMOD + "an optional group holding only a condition "
                                                   "(the loaded lowerer raises TypeError)"),
    ("core.md", "/(?<h>a)-${q}\\k<h>/"): ("DIFF", NOTMOD + "a backreference"),
    ("core.md", "rx.repeat(rx.digit, 3)"): ("DIFF", NOTMOD + "rx.repeat's second body (an exact count); the model "
                                            "reads its first"),
    ("core_details.md", "10:15"): ("unparsed", "a readings line quoting a run as printed before label-reference "
                                   "(its SEARCHED and FIND-ALL texts not printed); a record of that run"),
    ("library_details.md", "/(?:(?<d>\\d)?,)+/ & some((d: \"7\")) & occurs.none(NOT (d: \"7\"))"):
        ("DIFF", "a readings line quoting the draft's run of a form it marks NOT SUPPORTED; a record of that run"),
}
DECL_RULE = [      # first match: (status, message pattern, reason) for a refusal of a construct the engine lacks
    ("REFUSED", r"an undeclared name: (left|join|enumerate|when|strlen|quoted|pattern|month_numbered|length|capture|"
                r"between|any_case)\(", "a provided body this model does not read (native, or not modelled)"),
    ("REFUSED", r"^no body of padded fits", "`padded(rx, n)`: only `padded(rx)` is read"),
    ("REFUSED", r"an undeclared name: (<|!|NOT |\?\()", "a set, a negation or a conditional group as an operand: "
                                                         "not parsed by the label engine"),
    ("REFUSED", r"an undeclared name: (\d|$)", "a value list in a hole (`${[]}`, `${[2, 4] + ..}`): not modelled"),
    ("REFUSED", r"an undeclared name: [A-Za-z_]\w*(\([\w, ]*\))?$|at the binding `[^`]*`: an undeclared name",
     "a name the line binds in its prose, not its tail (the sweep reads the tail)"),
    ("REFUSED", r"^not a value:|a value of several strings", "value arithmetic over a pattern or several strings: "
                                                             "not modelled"),
    ("REFUSED", r"label `\d+` is not written", "a group number read as a label (core/labels/numbers): not modelled"),
    ("REFUSED", r"^unsupported group", "`(?J)`: not modelled"),
    ("REFUSED", r"a bare name inside a value left of", "a name inside a value left of `:`: refused by the model for "
                                                         "now (predfix82 DES-3)"),
    ("REFUSED", r"names a label it does not hold", "a condition bound alone and read where used: not modelled (the "
                                                   "fold lane's zero-condition-binding)"),
]
if s84("s13"):
    DECL_LINE.pop(next(iter(DECL_LINE)))
ANSWERS_CHANGED84 = {}        # (program, its bindings) -> why its answer moves: none (checked below)
sw_bad, sw_moved, sw_new, sw_gone, used_l, used_r = [], [], [], [], set(), set()
cnt, why_cnt = {}, {}
for k, vs in NEW_T.items():
    ov = OLD_T.get(k, [])
    for i_, (f_, ln_, st_, got_) in enumerate(vs):
        cnt[st_] = cnt.get(st_, 0) + 1
        if st_ != "same":
            d_ = DECL_LINE.get((f_, k[0]))
            if d_ and d_[0] == st_:
                used_l.add((f_, k[0]))
                why_cnt[d_[1][:60]] = why_cnt.get(d_[1][:60], 0) + 1
            else:
                r_ = next((x for x in DECL_RULE if x[0] == st_ and re.search(x[1], got_)), None)
                if r_ is None:
                    sw_bad.append(("UNDECLARED", f_, ln_, st_, k[0], got_[:100]))
                else:
                    used_r.add(r_[1])
                    why_cnt[r_[2][:60]] = why_cnt.get(r_[2][:60], 0) + 1
        o_ = ov[i_] if i_ < len(ov) else None
        if o_ and o_[3] != got_ and (k[0], k[1]) not in ANSWERS_CHANGED84:
            sw_moved.append((f_, ln_, k[0], o_[2], st_))
    if not ov and OLD_T:
        sw_new.append((vs[0][0], vs[0][1], k[0], k[1]))
for k, vs in OLD_T.items():
    if k not in NEW_T:
        sw_gone.append((vs[0][0], vs[0][1], k[0], k[1]))
stale = sorted(set(DECL_LINE) - used_l) + sorted(set(x[1] for x in DECL_RULE) - used_r)
for k_, n_ in sorted(why_cnt.items()):
    print("   DECLARED x%d: %s" % (n_, k_))
for x in sw_gone:
    print("   GONE %s:%d `%s` %s" % x)
for x in sw_new:
    print("   ADDED %s:%d `%s` %s" % x)
for x in sw_moved:
    print("   MOVED %s:%d `%s` (old %s, now %s)" % x)
for x in sw_bad:
    print("   BAD %s" % (x,))
for x in stale:
    print("   STALE DECLARATION %s" % (x,))
check("SWEEP", (LIGHT84 or OLD_T) and not sw_bad and not sw_moved and not sw_gone and not stale,
      "%d printed lines now (%s), %d at the starting commit under predspot's engine; every non-same status declared "
      "(%d line declarations, %d rule rows): undeclared %d %s; answers moved %d (listed: none); gone %d; added %d; "
      "stale declarations %d" % (len(NEW_T), ", ".join("%s %d" % kv for kv in sorted(cnt.items())), len(OLD_T),
                                 len(DECL_LINE), len(DECL_RULE), len(sw_bad), sw_bad[:2], len(sw_moved), len(sw_gone),
                                 len(sw_new), len(stale)))

print("== NULLABLE: EVID-4's known limit: no program the checks ran has a loop whose body can match empty")


def nullable(n):
    t = n[0]
    if t in ("lit", "cls", "dot"):
        return False
    if t == "seq":
        return all(nullable(x) for x in n[1])
    if t == "alt":
        return any(nullable(x) for x in n[1])
    if t == "grp":
        return nullable(n[2])
    if t == "rep":
        return n[2] == 0 or nullable(n[1])
    if t == "atomic":
        return nullable(n[1])
    return True


def loops_nullable(n, out):
    t = n[0]
    if t == "rep" and (n[3] is None or n[3] > 1) and nullable(n[1]):
        out.append(n)
    for x in (n[1] if t in ("seq", "alt") else [n[2]] if t in ("grp", "andpat2") else
              [n[1]] if t in ("rep", "atomic", "look") else []):
        if isinstance(x, tuple):
            loops_nullable(x, out)
    return out


checked = list(RUN)
if s84("s15"):
    checked.append(("/(?:(?<d>\\d)*)+/", (), prog("/(?:(?<d>\\d)*)+/").node))
nl = [(e, b) for e, b, nd in checked if loops_nullable(nd, [])]
check("NULLABLE", not nl, "%d programs run by the checks above (SWEEP's included), walked node by node: %d with a loop "
      "whose body can match empty%s" % (len(checked), len(nl), (": %s" % nl[:4]) if nl else ""))

print("== SUCCESSOR: every earlier in-force model re-run; its LAST LINE read; each red declared superseded, with the "
      "digest of the red's own FAIL line (a red whose content changes under an unchanged name fails here)")
LANES = os.path.normpath(os.path.join(HERE84, ".."))
SUPERSEDED = {                # model -> {red: (digest of its FAIL line or traceback line, "superseded by ...")}
}
MODELS = ["predspot", "predfix83", "preddef", "predfix82", "predcall", "predref", "predbound", "predfix77", "predarr",
          "predscope"]
if s84("s16") and SUPERSEDED:
    k0 = next(iter(SUPERSEDED))
    SUPERSEDED[k0].pop(next(iter(SUPERSEDED[k0])), None)
succ_bad, succ_n = [], 0
if not LIGHT84:
    procs = {}
    for mname in MODELS:
        env = {k: v for k, v in os.environ.items() if not k.endswith("_SABOTAGE") and not k.endswith("_ENGINE")}
        procs[mname] = subprocess.Popen([sys.executable, "-I", "-B", os.path.join(LANES, mname + "_evidence",
                                                                                   mname + "_model.py")],
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
        out, _ = procs[mname].communicate(timeout=3000)       # one at a time: a single-process run
        procs[mname].out = out
    for mname, pr in procs.items():
        succ_n += 1
        lines_ = pr.out.rstrip("\n").split("\n")
        last = lines_[-1]
        mm = re.match(r"%s_model: (\d+) checks, (\d+) failed(?: \(([^)]*)\))?$" % mname, last)
        reds = {}
        if mm:
            for r in [x.strip() for x in (mm.group(3) or "").split(",") if x.strip()]:
                reds[r] = next((l_ for l_ in lines_ if l_.startswith("FAIL %s:" % r) or
                                re.match(r"%s\s+FAIL\b" % re.escape(r), l_)), "")
        else:
            reds["TRACEBACK"] = last
        decl = SUPERSEDED.get(mname, {})
        print("   %-10s last line: %s" % (mname, last[:140]))
        for r, fl in sorted(reds.items()):
            dg = hashlib.sha256(fl.encode()).hexdigest()[:12]
            d = decl.get(r)
            if d is None:
                succ_bad.append((mname, r, "UNDECLARED"))
                print("      %s [%s] UNDECLARED: %s" % (r, dg, fl[:300]))
            elif d[0] != dg:
                succ_bad.append((mname, r, "CONTENT CHANGED"))
                print("      %s [%s, declared %s] CONTENT CHANGED: %s" % (r, dg, d[0], fl[:300]))
            else:
                print("      %s [%s]: superseded by %s" % (r, dg, d[1]))
                print("         its FAIL line: %s" % fl[:240])
        gone = sorted(set(decl) - set(reds))
        if gone:
            print("      declared but green now: %s" % gone)
check("SUCCESSOR", LIGHT84 or (succ_n == len(MODELS) and not succ_bad),
      "%d earlier models re-run one at a time, each last line read; every red declared superseded with an unchanged "
      "FAIL line: %s" % (succ_n, "yes" if not succ_bad else succ_bad))



print("== FCONTROL: the flag engine (no hole) against python `re`, each control written by hand")
FC = [("/a(?i)b/", r"a(?i:b)"), ("/(?s)a.b/", r"(?s:a.b)"), ("/a.b/", r"a.b"), ("/(?m)^a$/", r"(?m:^a$)"),
      ("/^a$/", r"^a$"), ("/(?x)a b # c/", r"ab"), ("/(a(?i)b|c)d/", r"(a(?i:b)|(?i:c))d"),
      ("/(?i:a)b/", r"(?i:a)b"), ("/ab/i", r"(?i:ab)"), ("/(?i)a(?-i)b/", r"(?i:a)b"), ("/[a-c]x/i", r"(?i:[a-c]x)")]
QF = pop("aAbBcCdx\n ", 3)
fc_bad = []
for lit, py in FC:
    Pg = fprog({"program": []}, lit)
    d_ = ndiff(answers(Pg, QF), answers(Re(py if not s84("s32") else py.replace("(?i:", "(?:")), QF))
    if d_ != (0, 0, 0):
        fc_bad.append((lit, py, d_))
check("FCONTROL", not fc_bad, "%d literals, each against its hand-written python `re` equivalent over %d texts: "
      "differing %s" % (len(FC), len(QF), fc_bad or "none"))

print("== EXAMPLES: the weak example and the s example, the rule of hole-flags against the rule of 2026-11-19")
WT = " in a program file opening `@options(i)`, word := `/[a-z]+/` in a library file that sets nothing"
W1 = fr("/id-${word}/", WT)
W2 = fr("/(?i)id-${word}/", WT)
W1o = fr("/id-${word}/", WT, "old")
S1 = fr("/(?s)a${dot}b/", ", dot := `/./`")
S1o = fr("/(?s)a${dot}b/", ", dot := `/./`", "old")
S2 = fr("/(?s)a${dot}b/", ", dot := `/(?s)./`")
WH, WS, WF = ["id-abc", "ID-abc", "ID-ABC"], "x ID-ABC id-abc", "id-ab ID-AB Id-ab"
SH, SS_, SF = ["a\nb", "axb"], "a\nb axb", "a\nb axb ayb"
fl("A library word under a weakly insensitive program", "/id-${word}/", WT, W1, WH, WS, WF, "core/holes/flags")
fl("The program writes the flag", "/(?i)id-${word}/", WT, W2, WH, WS, WF, "core/holes/flags")
fl("An `s` the inserted literal does not write", "/(?s)a${dot}b/", ", dot := `/./`", S1, SH, SS_, SF,
   "core/holes/flags")
fl("Written in the inserted literal", "/(?s)a${dot}b/", ", dot := `/(?s)./`", S2, SH, SS_, SF, "core/holes/flags")
REC_B = ("WHOLE `id-abc` HOLDS / WHOLE `ID-abc` HOLDS / WHOLE `ID-ABC` FAILS / SEARCHED `x ID-ABC id-abc` "
         "`id-abc`@9 / FIND-ALL `id-ab ID-AB Id-ab` [`id-ab`@0, `Id-ab`@12]")
if s84("s33"):                                                # EXAMPLES's plant: the record's line (a) for (b)
    REC_B = ("WHOLE `id-abc` HOLDS / WHOLE `ID-abc` HOLDS / WHOLE `ID-ABC` HOLDS / SEARCHED `x ID-ABC id-abc` "
             "`ID-ABC`@2 / FIND-ALL `id-ab ID-AB Id-ab` [`id-ab`@0, `ID-AB`@6, `Id-ab`@12]")
REC_A = ("WHOLE `id-abc` HOLDS / WHOLE `ID-abc` HOLDS / WHOLE `ID-ABC` HOLDS / SEARCHED `x ID-ABC id-abc` "
         "`ID-ABC`@2 / FIND-ALL `id-ab ID-AB Id-ab` [`id-ab`@0, `ID-AB`@6, `Id-ab`@12]")


def rec_form(Pg, wh, sr, fa):
    """The record's spelling of a run line (one WHOLE per text), for comparing with its pasted lines."""
    a = fmt(Pg, wh, sr, fa)
    w = a.split(" / SEARCHED ")[0][len("WHOLE "):]
    return " / ".join("WHOLE " + x for x in w.split(", ")) + " / SEARCHED " + a.split(" / SEARCHED ")[1]


ex_ok = (rec_form(W1, WH, WS, WF) == REC_B and ws(REC_B) in RECORD_WS and rec_form(W1o, WH, WS, WF) == REC_A and
         ws(REC_A) in RECORD_WS and not W2.whole("x") and all(W2.whole(t_) for t_ in WH) and not S1.whole("a\nb")
         and S1o.whole("a\nb") and S2.whole("a\nb"))
check("EXAMPLES", ex_ok, "the weak example under hole-flags reproduces the record's pasted line (b) %s, under "
      "2026-11-19's rule its line (a) %s; `/(?i)id-${word}/` holds on all three %s; the s example: `a\\nb` FAILS now "
      "%s, HELD under 2026-11-19's rule %s, holds with `(?s)` in `dot` %s" %
      (rec_form(W1, WH, WS, WF) == REC_B, rec_form(W1o, WH, WS, WF) == REC_A, all(W2.whole(t_) for t_ in WH),
       not S1.whole("a\nb"), S1o.whole("a\nb"), S2.whole("a\nb")))

print("== EXPLICIT (reading (a)): `(?i)`, `(?-i)`, `(?i:..)`, `/.../i` are explicit and pass a hole; a program option "
      "never does; any_case's body writes one")
LIBW = {"program": [], "library": [("bind", "w", "/ab/")]}
LIBWI = {"program": [], "library": [("opt", {"i": True}), ("bind", "w", "/ab/")]}
PRI = {"program": [("opt", {"i": True})], "library": [("bind", "w", "/ab/")]}
ex = [("(?i)", fprog(LIBW, "/(?i)${w}/").whole("AB"), True),
      ("(?i:..)", fprog(LIBW, "/(?i:${w})/").whole("AB"), True),
      ("/.../i", fprog(LIBW, "/${w}/i").whole("AB"), True),
      ("(?-i) over a weakly insensitive library", fprog(LIBWI, "/(?-i)${w}/").whole("AB"), False),
      ("(?-i:..) over it", fprog(LIBWI, "/(?-i:${w})/").whole("AB"), False),
      ("the library alone, weakly insensitive", fprog(LIBWI, "/${w}/").whole("AB"), True),
      ("a program option `@options(i)`", fprog(PRI, "/${w}/").whole("AB"), False),
      ("the program's own literal under it", fprog(PRI, "/ab/").whole("AB"), True)]
FMACROS["any_case"] = (["rx"], "/(?i:${[(=) = rx]})/", "library")
ex.append(("any_case's body", fprog(LIBW, "any_case(w)").whole("AB"), True))
FMACROS.clear()
ex_bad = [(n_, g_) for n_, g_, w_ in ex if g_ != w_]
for n_, g_, w_ in ex:
    print("   %-40s WHOLE `AB` %s (expected %s)" % (n_, "HOLDS" if g_ else "FAILS", "HOLDS" if w_ else "FAILS"))
check("EXPLICIT", not ex_bad, "%d settings over `${w}`, w := `/ab/` in a library file, on `AB`: wrong %s" %
      (len(ex), ex_bad or "none"))


def trigger(side_a, side_b, files, alpha="abAB", n=3, flag="(?i)", hole=None):
    """`pcrec.flags.filter` (core/holes/flags/in-filter): at `/(?i)${A & B}/` (or `(?-i)`, review r84 A8), the
    sides-first result differs from the expression alone with the flag applied to its result: under `i` any case
    of the text, under `-i` the text as written."""
    texts = pop(alpha, n)[1:]
    inner = hole or "%s & %s" % (side_a, side_b)
    first = fprog(files, "/%s${%s}/" % (flag, inner))
    alone = fprog(files, inner)
    if flag == "(?i)":
        folded = lambda t: any(alone.whole("".join(c)) for c in itertools.product(*[(x.lower(), x.upper()) for x in t]))  # noqa: E731,E501
    else:
        folded = alone.whole
    diff = [t_ for t_ in texts if first.whole(t_) != folded(t_)]
    r_ = bool(diff)
    return ((not r_) if s84("s25") and flag == "(?-i)" else r_), diff, len(texts)


print("== FILTER (reading (b), A2, A8): the sides of an `&` in a hole inherit an explicit `i` or `-i` only; for flags "
      "a binding is its expression where it is WRITTEN; the warning's trigger under `i` and under `-i`")
FN = {"program": []}
f1 = trigger("/[a-z]x/", "/[A-Z]x/", FN, "axAX", 2)[0]
f3 = trigger("/[a-z]+/", "/b.*/", FN, "abAB", 3)[0]
WEAKP = {"program": [("opt", {"i": True})], "library": [("bind", "C", "/[a-z]x/ & /[A-Z]x/")]}
P_w = fprog(WEAKP, "/${C}/")
P_e = fprog(WEAKP, "/(?i)${C}/")
P_side = fprog({"program": [("opt", {"i": True})]}, "/${/[a-z]x/ & /[A-Z]x/}/")
WEAKL = {"program": [], "library": [("opt", {"i": True}), ("bind", "C", "/[a-z]x/ & /Ax/")]}
f_mi, f_mi_d, f_mi_n = trigger(None, None, WEAKL, "aAxX", 2, "(?-i)", "C")
print("   the `-i` trigger: `/(?-i)${C}/`, C := `/[a-z]x/ & /Ax/` in a weakly insensitive library: differs on %d of %d "
      "texts: %s" % (len(f_mi_d), f_mi_n, f_mi_d))
FT_B = " in a program file opening `@options(i)`, C := `/[a-z]+/ & /b.*/` in a library file that sets nothing"
FT_W = " in a program file opening `@options(i)`"
FWH, FSR, FFA = ["id-blah", "id-BLAH"], "x id-BLAH id-blah", "id-blah id-BLAH id-bx"
P_bl = fr("/id-${C}/", FT_B)
P_wh = fr("/id-${/[a-z]+/ & /b.*/}/", FT_W)
fl("Bound in a library", "/id-${C}/", FT_B, P_bl, FWH, FSR, FFA, "core/holes/flags/in-filter")
fl("Written in the hole", "/id-${/[a-z]+/ & /b.*/}/", FT_W, P_wh, FWH, FSR, FFA, "core/holes/flags/in-filter")
fil = (f1, f3, P_w.whole("ax"), P_e.whole("ax"), P_side.whole("ax"), f_mi, P_bl.whole("id-BLAH"),
       P_wh.whole("id-BLAH"))
check("FILTER", fil == (True, False, False, True, True, True, False, True),
      "trigger at `/(?i)${..}/`: `/[a-z]x/ & /[A-Z]x/` %s (warns), `/[a-z]+/ & /b.*/` %s (does not); a library "
      "C := `/[a-z]x/ & /[A-Z]x/` under a weakly insensitive program: `/${C}/` on `ax` %s (no flag reaches the sides: "
      "nothing to warn of), `/(?i)${C}/` %s; the same sides written in place in that program's own hole take its weak "
      "`i` as their own file's default: %s; under an inherited `-i` the trigger fires %s (A8); bound in a library, "
      "`/id-${C}/` on `id-BLAH` %s, the same `&` written in the hole %s (A2: for flags, where it is WRITTEN)" % fil)

print("== NOTINH (reading (c)): `x` and `n` stay not inherited; `m` and `s` no longer are (part 3)")
LX = {"program": [], "library": [("bind", "sp", "/a b/"), ("bind", "g", "/(a)/"), ("bind", "d", "/./"),
                                 ("bind", "e", "/a$/")]}
ni = (fprog(LX, "/(?x)${sp}/").whole("ab"), fprog(LX, "/(?x)${sp}/").whole("a b"),
      (fprog(LX, "/(?n)${g}/"), NUMBERED[0])[1],           # the inner literal's count: it is parsed first
      fprog(LX, "/(?s)${d}/").whole("\n"),
      fprog(LX, "/(?m)${e}\\nb/").whole("a\nb"), fprog(LX, "/(?m)${e}\\nb/", "old").whole("a\nb"))
check("NOTINH", ni == (False, True, 1, False, False, True),
      "`/(?x)${sp}/`, sp := `/a b/`: `ab` %s, `a b` %s (x not inherited); `/(?n)${g}/`, g := `/(a)/`: g's numbered "
      "groups %s (n not inherited); `/(?s)${d}/` on a newline %s; `/(?m)${e}\\nb/`, e := `/a$/`, on `a\\nb` %s now, "
      "%s under 2026-11-19's rule (m no longer inherited). U, xx, J: not modelled (U and xx not inherited as ruled; "
      "J unchanged, core/holes/same-name)" % ni)

print("== LEXICAL (reading (d)): the program options and the weak `i` are one table, from the statement on, the "
      "file's own literals")
# (one statement, after a binding: whether `i` may be set weakly insensitive below the top of a file and whether
# `@options(..)` may appear more than once are NOT ruled; the weak `i` is shown at the top only)
LF = {"program": [("bind", "a", "/a./"), ("opt", {"s": True, "m": True}), ("bind", "b", "/b./")]}
LW = {"program": [("opt", {"i": True}), ("bind", "a", "/a/")], "library": [("bind", "c", "/c/")]}
lx = (fprog(LF, "a").whole("a\n"), fprog(LF, "b").whole("b\n"), fprog(LF, "/x./").whole("x\n"),
      fprog(LW, "/${a}${c}/").whole("AC"), fprog(LW, "/${a}${c}/").whole("Ac"))
check("LEXICAL", lx == (False, True, True, False, True),
      "one file: `a := /a./`, then `@options(s, m)`, then `b := /b./`: `a` on `a\\n` %s (written before the "
      "statement); `b` on `b\\n` %s (from the statement on); the program's own literal after it on `x\\n` %s; the weak "
      "`i` in the same table (at the top): a program file opening `@options(i)` with `a := /a/`, a library `c := /c/`: "
      "`/${a}${c}/` on `AC` %s, on `Ac` %s (the file's own literals only)" % lx)

print("== LIBFILE (reading (e), the brief's): a library keeps its own options; never across an import")
LBT = ", dot := `/./` in a library file opening `@options(s)`"
LB2T = " in a program file opening `@options(s)`, dot := `/./` in a library file that sets nothing"
LB, LB2 = files_of_line("", LBT), files_of_line("", LB2T)
fl("A library keeps its own options", "/a${dot}b/", LBT, fr("/a${dot}b/", LBT), SH, SS_, SF, "lib/builtin/options")
fl("Never across an import", "/a${dot}b/", LB2T, fr("/a${dot}b/", LB2T), SH, SS_, SF, "lib/builtin/options")
SAMEF = {"program": [("opt", {"i": True}), ("bind", "w", "/ab/")]}
lb_ = (fprog(LB, "/a${dot}b/").whole("a\nb"), fprog(LB2, "/a${dot}b/").whole("a\nb"),
       fprog(LB2, "/a.b/").whole("a\nb"), fprog(SAMEF, "/x${w}/").whole("XAB"))
check("LIBFILE", lb_ == (True, False, True, True),
      "a library opening `@options(s)`: its `dot := /./` in `/a${dot}b/` on `a\\nb` %s; the program opening it "
      "instead: %s (never across an import), the program's own `/a.b/` %s; a binding of the SAME file inserted in "
      "a hole of that file has the same defaults (the record's reading (e)): `/x${w}/` on `XAB` %s" % lb_)

print("== NUMBERS (reading (f)): with n set, a plain `( )` is no capture and no numbered label")
NB = {"program": [("opt", {"n": True})]}
fprog(NB, "/(\\d):(\\d)/")
n_on = NUMBERED[-1]
fprog({"program": []}, "/(\\d):(\\d)/")
n_off = NUMBERED[-1]
fprog(NB, "/(?<h>\\d):(\\d)/")
n_named = NUMBERED[-1]
nb = (n_on, n_off, n_named)
check("NUMBERS", nb == (0, 2, 0), "`/(\\d):(\\d)/`: numbered groups under a file's `@options(n)` %d, without %d; "
      "`/(?<h>\\d):(\\d)/` under n %d (a named group stays a capture and a label by its name)" % nb)

print("== FLAGGRID: flag x where it is set x what is read; each cell its deciding sentence and a run")
# Each flag: (a probe literal it changes, a text the probe matches WHOLE iff the flag applies, the base state the
# flag departs from). The probe is placed per READER; the flag set per WHERE. "applies" is read off the run.
FLAGS_G = [
    ("i explicit on", "/ab/", "AB", "(?i)", None),
    ("i explicit off", "/ab/", "!AB", "(?-i)", "weakon-probe"),    # base: the probe's file weakly insensitive
    ("weak on", "/ab/", "AB", None, None),
    ("weak off", "/ab/", "!AB", None, "weakon-elsewhere"),       # "!": applies iff `AB` does NOT match
    ("m", "/a$\\nb/", "a\nb", "(?m)", None),
    ("s", "/a.b/", "a\nb", "(?s)", None),
    ("n", "/(a)b/", None, "(?n)", None),                           # read: the probe's numbered groups (0 = applies)
    ("x", "/a b/", "ab", "(?x)", None),
]
WHERE = ["the literal itself", "up the hole", "the file's option", "the importing file's option"]
READ = ["own text", "inserted same-file binding", "inserted library binding", "a side of `&` in a hole"]
OPT = {"i explicit on": None, "i explicit off": None, "weak on": {"i": True}, "weak off": {"i": False},
       "m": {"m": True}, "s": {"s": True}, "n": {"n": True}, "x": {"x": True}}
SG = {
    "lit": ("core/patterns/flags", "A literal's flags are the ones it writes"),
    "hole-i": ("core/holes/flags", "only an explicit `i` or `-i` in force at the hole is inherited"),
    "hole-not": ("core/holes/flags", "`m`, `s`, `x`, `xx`, `n`, `U` are not"),
    "opt-file": ("lib/builtin/options", "applies to the literals written after it in the same file"),
    "opt-import": ("lib/builtin/options", "never across an import"),
    "weak-no": ("core/holes/flags", "A weak value does not propagate"),
    "never-explicit": ("lib/builtin/options", "a program option is never explicit"),
    "na-weak": ("lib/builtin/options", "a weak value is set only by a program option"),
    "na-opt": ("lib/builtin/options", "a program option is never explicit"),
    "na-hole": ("core/holes/flags", "What is inserted in a hole starts from its own file's defaults"),
}


def wrap(probe_lit, flag_text):
    """The probe with the flag written in it: `(?i)` at its start, inside the slashes."""
    return "/" + flag_text + probe_lit[1:]


SG.update({
    "dup-opt": ("lib/builtin/options", "a program option is never explicit"),
    "dup-hole": ("core/holes/flags", "What is inserted in a hole starts from its own file's defaults"),
    "dup-import": ("lib/builtin/options", "applies to the literals written after it in the same file"),
    "open-pos": ("lib/builtin/options", "open options-position"),
})
if s84("s11"):
    SG["opt-import"] = ("core/holes/flags", "never across an import")


def cell(fname_, where, reader):
    """("run", files, expr, text, ablated files or None) | ("n/a"|"dup", sentence key, why) | ("undecided", files,
    expr, text, ablated files). n/a: no such program; dup: a real program, counted in the cell named."""
    _, probe, text, ftext, base = next(x for x in FLAGS_G if x[0] == fname_)
    opt = OPT[fname_]
    weak = fname_.startswith("weak")
    if where in ("the literal itself", "up the hole") and weak:
        return "n/a", "na-weak", "no such program: a weak value is never written in a literal"
    if where in ("the file's option", "the importing file's option") and fname_.startswith("i explicit"):
        return "dup", "dup-opt", "the program `@options(%si)` sets the WEAK value: the weak column's cell" % (
            "" if fname_.endswith("on") else "-")
    if where == "up the hole" and reader == "own text":
        return "dup", "dup-hole", "the own text is in no hole: the cell \"the literal itself\", own text"
    if where == "the importing file's option" and reader in ("own text", "inserted same-file binding"):
        return "dup", "dup-import", "the probe's file imports nothing: the cell \"the file's option\", same reader"
    pf = "library" if reader == "inserted library binding" or (where == "the importing file's option") else "program"
    files = {"program": [], "library": []}
    probe_text = wrap(probe, ftext) if where == "the literal itself" else probe
    if base == "weakon-probe":                              # (?-i) departs from a weakly insensitive probe
        files[pf].append(("opt", {"i": True}))
    kind, opt_item = "run", None
    if where == "the file's option":
        if fname_ == "weak off":                             # differs from the default only after a weak `i` on:
            kind = "undecided"                               # a second statement (options-position, open)
            if not s84("s9"):
                files[pf].append(("opt", {"i": True}))
        opt_item = ("opt", dict(opt))
        files[pf].append(opt_item)
    if where == "the importing file's option":
        opt_item = ("opt", dict(opt))
        files["program"].append(opt_item)
        if fname_ == "weak off":
            files["library"].insert(0, ("opt", {"i": True}))   # the library weakly insensitive, the program not
    outer_flag = ftext if where == "up the hole" else ""
    if reader == "own text":
        expr = probe_text
    elif reader in ("inserted same-file binding", "inserted library binding"):
        files[pf].append(("bind", "p", probe_text))
        expr = "/%s${p}/" % outer_flag
    elif where == "the importing file's option":
        files["library"].append(("bind", "p", probe_text))
        expr = "/%s${p & /(?s:.*)/}/" % outer_flag
    else:
        expr = "/%s${%s & /(?s:.*)/}/" % (outer_flag, probe_text)
    files = {k: v for k, v in files.items() if v or k == "program"}
    abl = None
    if opt_item is not None:
        abl = {k: [it for it in v if it is not opt_item] for k, v in files.items()}
    return kind, files, expr, text, abl


def applies(files, expr, text):
    Pg = fprog(files, expr)
    if text is None:
        return NUMBERED[0] == 0                              # n: the probe (parsed first) has no numbered group
    if text.startswith("!"):
        return not Pg.whole(text[1:])
    return Pg.whole(text)


def expect(fname_, where, reader):
    if where == "the literal itself":
        return True, "lit"
    if where == "up the hole":
        if fname_.startswith("i explicit"):
            return True, "hole-i"
        return False, "hole-not"
    if where == "the file's option":
        return True, "opt-file"
    if fname_.startswith("weak"):
        return False, "weak-no"
    return False, "opt-import"


def fdesc(files):
    return "; ".join("%s: %s" % (f_, " ".join("@options(%s)" % ",".join(("" if v else "-") + k for k, v in it[1].items())
                                              if it[0] == "opt" else "%s := %s" % (it[1], it[2]) for it in its))
                     for f_, its in files.items() if its) or "no options"


FG = {"AGREE": 0, "DISAGREE": 0, "n/a": 0, "dup": 0, "UNDECIDED": 0}
FG_BAD, FG_MISS, FG_VAC, FG_UND = [], [], [], []
for fname_, *_ in FLAGS_G:
    for where in WHERE:
        for reader in READ:
            c_ = cell(fname_, where, reader)
            if c_[0] in ("n/a", "dup"):
                tg_, words = SG[c_[1]]
                if ws(words) not in ws(piece_of(tg_)):
                    FG_MISS.append((fname_, where, reader, c_[1]))
                FG[c_[0]] += 1
                print("   %-14s | %-27s | %-26s | %s: %s (%s: \"%s\")" % (fname_, where, reader, c_[0], c_[2], tg_,
                                                                       words))
                continue
            kind, files, expr, text, abl = c_
            if kind == "undecided":
                tg_, words = SG["open-pos"]
                if ws(words) not in ws(piece_of(tg_)):
                    FG_MISS.append((fname_, where, reader, "open-pos"))
                ga = applies(files, expr, text)
                FCAND["position"] = "top only"
                try:
                    applies(files, expr, text)
                    gb = "runs"
                except FErr:
                    gb = "a compile error"
                finally:
                    FCAND["position"] = "anywhere"
                matters = applies(abl, expr, text) != ga
                if not matters:
                    FG_VAC.append((fname_, where, reader))
                FG["UNDECIDED"] += 1
                FG_UND.append((fname_, where, reader))
                print("   %-14s | %-27s | %-26s | `%s` [%s] on `%s`: candidate (a) %s, candidate (b) %s; the `-i` "
                      "statement %s | %s: \"%s\" | UNDECIDED" % (fname_, where, reader, esc_nl(expr), fdesc(files),
                                                                 esc_nl(text or ""), "applies" if ga else
                                                                 "does not apply", gb, "matters" if matters else
                                                                 "DOES NOT MATTER", tg_, words))
                continue
            want, sk = expect(fname_, where, reader)
            if s84("s10") and (fname_, where, reader) == ("m", "up the hole", "inserted library binding"):
                want = True
            tg_, words = SG[sk]
            if ws(words) not in ws(piece_of(tg_)):
                FG_MISS.append((fname_, where, reader, sk))
            got = applies(files, expr, text)
            mt = ""
            if want and abl is not None:                     # the option is what makes it apply
                m_ = applies(abl, expr, text) != got
                mt = "; without the option: %s" % ("differs" if m_ else "THE SAME")
                if not m_:
                    FG_VAC.append((fname_, where, reader))
            st_ = "AGREE" if got == want else "DISAGREE"
            FG[st_] += 1
            if st_ == "DISAGREE":
                FG_BAD.append((fname_, where, reader, got, want))
            print("   %-14s | %-27s | %-26s | `%s` [%s] on `%s`: %s%s | %s: \"%s\" | %s"
                  % (fname_, where, reader, esc_nl(expr), fdesc(files), esc_nl(text or "(the numbered groups)"),
                     "applies" if got else "does not apply", mt, tg_, words, st_))
NFG = sum(FG.values())
print("   FLAGGRID SUMMARY: %d cells: AGREE %d, DISAGREE %d, n/a %d (no such program), dup %d (a real program counted "
      "in the cell named), UNDECIDED %d %s; an applying option that does not matter: %s; deciding sentences not found "
      "in their piece: %s" % (NFG, FG["AGREE"], FG["DISAGREE"], FG["n/a"], FG["dup"], FG["UNDECIDED"], FG_UND,
                              FG_VAC or "none", FG_MISS or "none"))
check("FLAGGRID", NFG == 128 and not FG_BAD and not FG_MISS and not FG_VAC and FG["UNDECIDED"] == 4,
      "%d cells (8 flags x 4 places it is set x 4 readers): AGREE %d, DISAGREE %d %s, n/a %d, dup %d, UNDECIDED %d (the "
      "weak-off option of a file: it differs from the default only after an earlier `@options(i)`, a second statement, "
      "the open options-position); every applying option shown to matter (%s); sentences missing from their piece %s"
      % (NFG, FG["AGREE"], FG["DISAGREE"], FG_BAD[:3], FG["n/a"], FG["dup"], FG["UNDECIDED"],
         "yes" if not FG_VAC else FG_VAC[:3], FG_MISS or "none"))

for tg_, L_ in LINES:
    if "@options" in L_ or "${dot}" in L_ or "${word}" in L_:
        print("   LINE [%s] %s" % (tg_, L_))

# ================================================================== the new checks (lane predfix84)
import ctypes                                                # noqa: E402
PC2 = ctypes.CDLL("libpcre2-8.so.0")                         # the installed library, RUN (never read: D181)
PC2.pcre2_compile_8.restype = ctypes.c_void_p
PC2.pcre2_compile_8.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int),
                                ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p]
PC2.pcre2_match_data_create_from_pattern_8.restype = ctypes.c_void_p
PC2.pcre2_match_data_create_from_pattern_8.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
PC2.pcre2_match_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_uint32,
                              ctypes.c_void_p, ctypes.c_void_p]
PC2.pcre2_get_ovector_pointer_8.restype = ctypes.POINTER(ctypes.c_size_t)
PC2.pcre2_get_ovector_pointer_8.argtypes = [ctypes.c_void_p]
PC2.pcre2_substring_number_from_name_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p]


def pcre2_group(pattern, subject, name):
    """libpcre2: WHOLE match of `subject` (ANCHORED | ENDANCHORED); the text group `name` holds, or None."""
    err, off = ctypes.c_int(), ctypes.c_size_t()
    code = PC2.pcre2_compile_8(pattern.encode(), len(pattern.encode()), 0, ctypes.byref(err), ctypes.byref(off), None)
    assert code, pattern
    md = PC2.pcre2_match_data_create_from_pattern_8(code, None)
    sb = subject.encode()
    rc = PC2.pcre2_match_8(code, sb, len(sb), 0, 0x80000000 | 0x20000000, md, None)
    if rc < 0:
        return "NO MATCH"
    n = PC2.pcre2_substring_number_from_name_8(code, name.encode())
    ov = PC2.pcre2_get_ovector_pointer_8(md)
    a_, b_ = ov[2 * n], ov[2 * n + 1]
    return None if a_ == ctypes.c_size_t(-1).value else sb[a_:b_].decode()


def verdict2(expr, binds, alpha="37x", n=3):
    r_ = ref(expr, binds)
    if r_ is not None:
        return ("refused", r_)
    Pg = tp(expr, binds)
    return ("legal", tuple(t for t in pop(alpha, n) if t and Pg.whole(t)))


print("== RENAME (B1): no answer depends on whether the caller's binding is named like a macro's parameter")
RN_bad, RN_n = [], 0
for nm, (heads, body) in sorted(LIBMACROS.items()):
    if len(heads) != 1:
        continue
    pn = heads[0][0]
    for by_binding in (True, False):
        RN_n += 1
        e_z = "%s(Z) & (%s.d: <5)" % (nm, "Z" if by_binding else nm)
        e_p = "%s(%s) & (%s.d: <5)" % (nm, pn, pn if by_binding else nm)
        v_z = verdict2(e_z, ["Z := /(?<d>\\d)/"])
        v_p = verdict2(e_p, ["%s := /(?<d>\\d)/" % pn])
        same = v_z[0] == v_p[0] and (v_z[0] == "refused" or v_z[1] == v_p[1])
        print("   `%s` (Z) %s | `%s` (%s) %s | %s" % (e_z, v_z[0], e_p, pn, v_p[0], "same" if same else "MOVED"))
        if not same:
            RN_bad.append((e_z, e_p))
check("RENAME", RN_n and not RN_bad, "%d programs over the provided one-parameter bodies, each run with the caller's "
      "binding named Z and named like the parameter (peek's `A`, atomic's `X`, ...): moved %d %s" %
      (RN_n, len(RN_bad), RN_bad[:3]))

print("== PARTPATH (B2): a two-step path through a part label over a binding or a call, as through its name")
PP = [('[b = B(A)] & (b.p.h: "3")', 'B(A) & (B.p.h: "3")', [G_A, G_SPOT]),
      ('[b = pub] & (b.a.h: "3")', 'pub & (pub.a.h: "3")', [G_A, 'pub := [a = A] SEQ "!"']),
      ('[b = hits(/a(?<g>x)?/)] & (b.hit.g: "x")', 'hits(/a(?<g>x)?/) & (hits.hit.g: "x")', [])]
pp_r = []
for e1, e2, b_ in PP:
    v1, v2 = verdict2(e1, b_, "3ax!", 4), verdict2(e2, b_, "3ax!", 4)
    pp_r.append(v1[0] == "legal" and v1 == v2)
    print("   `%s` %s | `%s` %s" % (e1, v1[0] if v1[0] == "legal" else v1[1], e2, v2[0]))
check("PARTPATH", all(pp_r), "through the part label legal, with the same answers as through the name (%d texts): "
      "%s" % (len(pop("3ax!", 4)), pp_r))

print("== ARGREF (B3): label-reference one argument deep")
ar1 = ref('B(A & (h: "3"))', [G_A, G_ARG])
ar2 = ref('B(A & (A.h: "3"))', [G_A, G_ARG])
ar3 = ref("/(?<h>\\d)${inner((h: <5))}/", ["inner(c) := /x${c}/"])
ar4 = ref('A & (h: "3")', [G_A])
check("ARGREF", has(ar1, "core/labels/paths/label-reference") and ar2 is None and ar3 is None and ar4 is not None,
      "`B(A & (h: \"3\"))` refused naming label-reference %s (as `A & (h: \"3\")` is: %s); `B(A & (A.h: \"3\"))` legal "
      "%s; the printed `/(?<h>\\d)${inner((h: <5))}/` (the caller writes h) legal %s" %
      (has(ar1, "core/labels/paths/label-reference"), ar4 is not None, ar2 is None, ar3 is None))
print("   refusal: %s" % ar1)

print("== LISTATOM (D3): a list through a call that passes its argument's labels on takes them")
LA = "[(=l) = atomic(/(?<l>\\d)/)] & (l: <5)"
P_la = tp(LA)
r_la = ref("[(=l) = atomic(B | A)] & (l: <5)", ["A := /(?<l>\\d)\\d/", "B := /(?<l>\\d\\d)/"])
if P_la is not None:
    dl("Through a call that passes its argument's labels on", LA, [], P_la, ["3", "7"], "x73", "3 7 4",
       "core/labels/export/export-list")
la_pred = (lambda t: t in "01234" and len(t) == 1) if not s84("s19") else (lambda t: t in "56789" and len(t) == 1)
check("LISTATOM", P_la is not None and wdiff(P_la, la_pred, pop("0379", 2)) == 0 and r_la is not None,
      "`%s` legal %s, against \"the digit under 5\" differing %d; `[(=l) = atomic(B | A)]` refused %s (%s)" %
      (LA, P_la is not None, wdiff(P_la, la_pred, pop("0379", 2)), r_la is not None, r_la))

print("== PREFIXIN (A5): prefix_in lays S into a hole as quoted does: S's labels pass on by the list")
PI = 'prefix_in(3, /(?<a>ab)c|xy/) & (prefix_in.a: "ab")'
P_pi = tp(PI)
pi_pc = pcre2_group(r"^(?:(?<a>ab)c|xy)(?<=^(?s:.){3})(?s:.*)$", "abcz", "a")
if P_pi is not None:
    dl("S's labels, through the call", PI, [], P_pi, ["abcz", "abz", "xyzz"], "-abcz", "abcz xyzz",
       "lib/sets/prefix-in")
P_pi2 = tp("prefix_in(2, /abc|xy/)")
pi_ok = (P_pi is not None and P_pi.whole("abcz") and not P_pi.whole("xyzz") and P_pi2 is not None and
         P_pi2.whole("xyz") and pi_pc == "ab")
check("PREFIXIN", pi_ok, "`%s` legal %s, WHOLE `abcz` %s; the printed `prefix_in(2, /abc|xy/)` still runs, `xyz` %s "
      "(the list moves no match); libpcre2, S then a lookbehind at 3 on `abcz`: a = %r" %
      (PI, P_pi is not None, P_pi.whole("abcz") if P_pi else None, P_pi2.whole("xyz") if P_pi2 else None, pi_pc))

print("== CONTAINS (D5): the greedy leading gap: `contains.n` reads the LAST occurrence")
CT = "contains(/(?<n>\\d)/)"
P_ct = tp(CT)
ct_v = label_of(whole_state(P_ct, "a1b2"), "n")
ct_pc = pcre2_group(r"^(?s:.*)(?:(?<n>\d))(?s:.*)$", "a1b2", "n")
want_ct = "2" if not s84("s21") else "1"
ct_line = fmt(P_ct, ["a1b2", "ab"], "x a1b2", "a1b2 ab")
ct_line = ct_line.replace("`a1b2` HOLDS", "`a1b2` HOLDS (contains.n = `%s`)" % ct_v, 1)
doc_line("The last occurrence: %s (`%s`)" % (ct_line, CT), "lib/search/contains")
check("CONTAINS", ct_v == want_ct and ct_pc == want_ct, "`%s` WHOLE on `a1b2`: n = %r (this engine), %r (libpcre2)" %
      (CT, ct_v, ct_pc))

print("== SPOTNAME (open spot-read-name): both candidates run; no answer applied")
SN_B = [AD, "B(rx) := /${[p = rx]}-(?<d>\\d)/"]
sn_a = verdict2("B(A) & (A.d: <5)", SN_B, "37-", 3)
LCAND["spotname"] = "b"
try:
    sn_b = verdict2("B(A) & (A.d: <5)", SN_B, "37-", 3)
    sn_b2 = verdict2("B(A) & (B.p.d: <5)", SN_B, "37-", 3)
    P_snb = tp("B(A) & (B.p.d: <5)", SN_B)
finally:
    LCAND["spotname"] = "a"
if P_snb is not None:
    dl("Candidate (b) of spot-read-name", "B(A) & (B.p.d: <5)", SN_B, P_snb, ["7-3", "3-7", "3-3"], "7-3 3-7",
       "7-3 3-7 1-2 9-9", "core/labels/paths/closed-argument")
exp_b = "refused" if not s84("s22") else "legal"
check("SPOTNAME", sn_a[0] == "legal" and sn_b[0] == exp_b and sn_b2[0] == "legal" and sn_b2[1] == sn_a[1],
      "`B(A) & (A.d: <5)` through a body labelling the spot: candidate (a) %s, candidate (b) %s; under (b) "
      "`B(A) & (B.p.d: <5)` %s with (a)'s answers %s" % (sn_a[0], sn_b[0], sn_b2[0], sn_b2[1] == sn_a[1]))

print("== UPTO (B4): \"from the statement on\" for a call's argument and a macro's body")
U1 = " in a program file writing mac(x) := `/${[(=) = x]}/`, then b := `mac(/a.b/)`, then `@options(s)`, then the " \
     "program"
U2 = " in a program file writing mac(x) := `/${[(=) = x]}./`, then `@options(s)`, then b := `mac(/a/)`, then the " \
     "program"
U3 = " in a program file writing `@options(s)`, then mac(x) := `/${[(=) = x]}/`, then b := `mac(/a.b/)`, then the " \
     "program"
up = (fr("b", U1).whole("a\nb"), fr("b", U2).whole("a\n"), fr("b", U3).whole("a\nb"))
check("UPTO", up == (False, False, True), "an argument written before `@options(s)`: `b := mac(/a.b/)` on `a\\nb` %s; "
      "a macro body written before it: `mac(x) := /${..}./`, then `@options(s)`, then `b := mac(/a/)`, on `a\\n` %s; "
      "both after the statement: %s" % up)

print("== OPENFLAGS (option-hole-explicit, options-reach-constants, options-position): each candidate's run line")
OF_T1 = ", o := `\"i\"`, w := `/ab/` in a library file that sets nothing"
OF_T2 = " in a program file opening `@options(i)`"
OF_T3 = " in a program file opening `@options(s)`, atomic(X) := `/(?>${[(=) = X]})/` in a library file"
OF_T4 = " in a program file writing a := `/./`, then `@options(s)`, then the program"
CANDS = {"option-hole-explicit": ("opthole", "explicit", "weak"), "options-reach-constants": ("const", "reach",
                                                                                             "not reached"),
         "options-position": ("position", "anywhere", "top only")}
OF = [("option-hole-explicit", "/(?${o})${w}/", OF_T1, ["ab", "AB"], "x AB ab", "ab AB Ab", "core/patterns/flags"),
      ("options-reach-constants", '"ab"', OF_T2, ["ab", "AB"], "x AB ab", "ab AB", "lib/builtin/options"),
      ("options-reach-constants", "atomic(/a.b/)", OF_T3, ["a\nb", "axb"], "a\nb axb", "a\nb axb",
       "lib/builtin/options"),
      ("options-position", "/x${a}y/", OF_T4, ["x\ny", "xay"], "x\ny xay", "x\ny xay xby", "lib/builtin/options")]
of_part = []
for slug, pt, tail, wh, sr, fa, tg in OF:
    key, ca, cb = CANDS[slug]
    outs = []
    for lab, cv in (("a", ca), ("b", cb)):
        FCAND[key] = cv
        if s84("s23") and key == "opthole":
            FCAND[key] = ca
        try:
            Pg = fr(pt, tail)
            outs.append(ffmt(Pg, wh, sr, fa))
            fl("Candidate (%s) of %s" % (lab, slug), pt, tail, Pg, wh, sr, fa, tg)
        except FErr as e:
            outs.append("FErr")
            doc_line("Candidate (%s) of %s: modes: a compile error (`%s`%s: `@options` below a binding)" %
                     (lab, slug, esc_nl(pt), tail), tg)
            print("   (%s) %s" % (lab, e))
        finally:
            FCAND[key] = ca
    of_part.append((slug, pt, outs[0] != outs[1]))
check("OPENFLAGS", all(x[2] for x in of_part), "each open line's two candidates part on its witness: %s" % of_part)

print("== PATFLAGS (A6 (4), a reading): `pattern($x)` carries the flags in force where the group is written")
PF = "/(?i)(?<x>ab),(?-i)${pattern($x)}/"
P_pf = fr(PF, "")
fl("Under another flag", PF, "", P_pf, ["ab,AB", "AB,ab", "ab,ac"], "x ab,AB", "ab,AB AB,Ab", "lib/builtin/pattern")
check("PATFLAGS", P_pf.whole("ab,AB") and P_pf.whole("AB,ab") and not P_pf.whole("ab,ac"),
      "`%s`: `ab,AB` %s, `AB,ab` %s, `ab,ac` %s (x written under `(?i)`, inserted under `(?-i)`)" %
      (PF, P_pf.whole("ab,AB"), P_pf.whole("AB,ab"), P_pf.whole("ab,ac")))


print("== FSWEEP: every printed three-mode line resting on a flag: the starting documents under predspot's flag "
      "engine against these under this one (each open line under the candidate it names); `rejected:` and history "
      "lines skipped; no answer moves unless listed")


def unesc(t_):
    return t_.replace("\\n", "\n")


CAND_LINE = re.compile(r"Candidate \((a|b)\) of ([\w-]+)")


def f_table84(docs, on):
    F84[0] = on
    out = {}
    try:
        for f, ln, line_, a, pt0, tail, field in sweep_lines84(docs):
            if not FLAGTAIL.search(tail) or field in SKIP_FIELDS:
                continue
            mm = re.search(r"`([^`]*)`", tail)
            pt = unesc(mm.group(1))
            k = sw_key(f, line_, mm.group(1), tail)
            mc = CAND_LINE.search(line_[:line_.index(a)])
            if mc:
                key, ca, cb = CANDS[mc.group(2)]
                FCAND[key] = ca if mc.group(1) == "a" else cb
            try:
                wh, sr, fa = modes_of(line_)
                got = ffmt(fr(pt, tail[mm.end():]), [unesc(x) for x in wh], unesc(sr), unesc(fa))
                st_ = "same" if got == strip_annot(a) else "DIFF"
            except (FErr, CompileError, KeyError, IndexError, ValueError) as e:
                st_, got = "REFUSED", "%s: %s" % (type(e).__name__, e)
            finally:
                FCAND.update(opthole="explicit", const="reach", position="anywhere")
            out.setdefault(k, []).append((f, ln, st_, got))
    finally:
        F84[0] = ENGINE_ON
    return out


FN_T = f_table84(NOWS, True)
FO_T = f_table84(OLD84, False)
FO_N = f_table84(OLD84, True)                                # the starting lines under this engine: what moves
F_CHANGED = {}                                               # (program, binds) -> why its answer moves: none
fs_bad, fs_rows = [], []
for k, vs in FO_T.items():
    f_, ln_, st_o, got_o = vs[0]
    st_n, got_n = FO_N[k][0][2], FO_N[k][0][3]
    fate = "stands" if got_o == got_n else ("CHANGED: %s" % F_CHANGED[(k[0], k[1])] if (k[0], k[1]) in F_CHANGED
                                           else "MOVED, UNLISTED")
    if fate == "MOVED, UNLISTED" or st_o != "same":
        fs_bad.append((f_, ln_, k[0], st_o, fate))
    fs_rows.append((f_, ln_, k[0], fate, k in FN_T))
for k, vs in FN_T.items():
    for f_, ln_, st_, got_ in vs:
        if st_ != "same":
            fs_bad.append((f_, ln_, k[0], st_, got_[:120]))
for r_ in fs_rows:
    print("   %s:%d `%s`: %s under this engine; printed now: %s" % (r_[0], r_[1], esc_nl(r_[2]), r_[3],
                                                                  "yes" if r_[4] else "re-spelled or gone"))
for k, vs in FN_T.items():
    if k not in FO_T:
        print("   ADDED %s:%d `%s`" % (vs[0][0], vs[0][1], esc_nl(k[0])))
for x in fs_bad:
    print("   BAD %s" % (x,))
if s84("s26"):
    fs_bad.append(("planted",))
check("FSWEEP", FO_T and not fs_bad, "%d flag lines at the starting commit (each reproduced by predspot's flag engine, "
      "then run under this one: %d stand, %d changed); %d flag lines now, each printed as this engine runs it; "
      "bad %d %s" % (len(FO_T), sum(1 for r_ in fs_rows if r_[3] == "stands"),
                     sum(1 for r_ in fs_rows if r_[3].startswith("CHANGED")), len(FN_T), len(fs_bad), fs_bad[:3]))

print("== QUOTES: every owner sentence this lane quotes occurs in the record and the documents; every cited title is one")
QQ = ["The label is not to the regex abstractly, it's to the spot in the pattern where the regex is being inserted.",
      "It's not a piece of the pattern. It's a template of the rx that might be placed into the pattern.",
      "argument-default: for me this is an error.",
      "A parameter like rx in a call B(rx) cannot be labeled because it's not being placed into the pattern.",
      "wrapper-export: agree (a). I was worried you'd say peek() doesn't work. It's just a definition change.",
      "transform-export: yes.",
      "hide(x) := /${x}/",
      "identity(x) := /${[(=) = x]}/",
      "program-options: yes.",
      "Using predicate language it's going to be more likely to use () in a literal to mean no capturing group.",
      "Options m s really can't be inherited because they change semantics in confusing ways if you don't control them.",
      "i has three settings: on, off, weak on, weak off.",
      "Consider this: weak settings do not propagate.",
      "hole-flags: yes to all.",
      "What i like about the i weak behavior is that it's consistent to the other program level settings that only "
      "affect literals in program scope."]
TT = ["2026-11-22 OWNER RULING — argument-default: an error; and his reason: a label is to the SPOT in the pattern, a "
      "parameter is a template, not a piece of the pattern",
      "2026-11-22 OWNER RULING — wrapper-export: agree (a) (the provided wrappers pass their argument's labels on); and "
      "a question: do transforms in general",
      "2026-11-22 OWNER RULING — transform-export: yes (a provided body that places its argument passes its labels on); "
      "and two definitions he writes: `hide`, `identity`",
      "2026-11-22 OWNER RULING — program-options: yes; and a PROPOSAL: `i` keeps inheriting, with a \"weak\" value the "
      "program sets",
      "2026-11-22 OWNER IDEA — program-scoped options: `@options()` setting flags (m, s, n, ...) for the literals of the "
      "bindings that follow",
      "2026-11-22 OWNER, on weak-meets-weak: \"Consider this: weak settings do not propagate.\"",
      "2026-11-22 OWNER RULING — hole-flags: yes to all (weak values do not propagate; only an explicit `i` is "
      "inherited at a hole; `m` and `s` are no longer inherited)"]
TT.append("2026-11-23 MANAGER — review r84 (predspot1122): the dispositions, ruled with the 2026-11-23 rulings in hand; "
          "no owner words")
if s84("s17"):
    QQ[0] = QQ[0] + " (altered)"
ALLNOW = "\n".join(NOWS.values())
q_miss = [q for q in QQ if ws(q) not in RECORD_WS or ws(q) not in ws(ALLNOW)]
heads = set(ws(re.sub(r"^(### |\*\*)", "", l_)) for l_ in RECORD.split("\n") if l_.startswith(("### ", "**")))
t_miss = [t_ for t_ in TT if ws(t_) not in heads or ws(t_) not in ws(ALLNOW)]
check("QUOTES", QQ and not q_miss and not t_miss, "%d quoted sentences in the record and the documents, missing: %s; "
      "%d record titles cited whole, not a title or not cited: %s" % (len(QQ), q_miss or "none", len(TT),
                                                                     t_miss or "none"))

print("== DOC: every line this model formats occurs verbatim in the documents")
DLN = list(LINES)
if s84("s18") and DLN:
    DLN[0] = (DLN[0][0], DLN[0][1].replace("WHOLE `", "WHOLE `x", 1))
d_miss = [(t_, L) for t_, L in DLN if ws(L) not in ws(ALLNOW)]
for t_, L in d_miss:
    print("   MISSING [%s] %s" % (t_, L))
check("DOC", DLN and not d_miss, "%d lines; missing: %d" % (len(DLN), len(d_miss)))

failed = [n for n, ok in RESULTS if not ok]
print("predfix84_model: %d checks, %d failed%s" % (len(RESULTS), len(failed),
                                                 (" (%s)" % ", ".join(failed)) if failed else ""))
sys.exit(1 if failed else 0)
