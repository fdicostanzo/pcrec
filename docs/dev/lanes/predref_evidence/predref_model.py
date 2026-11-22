#!/usr/bin/env python3
# Lane predref (2026-11-22): the evidence for (A) sweeping every printed program of the predicate documents under
# the owner's label-reference ruling ("required"), (B) the flat-read statements rewritten, (C) helper-captures
# folded (a provided body's groups are labels only, the label-only group `(?<:x>...)` under construction), and
# the manager's readings (a)..(f) of the lane brief. DESIGN EVIDENCE ONLY; rules nothing.
#
# METHOD. Lane predbound's lowerer and label matcher are LOADED unchanged: predbound_model.py is executed up to its
# line "the checks" (its definitions only; its own checks never run; PREDBOUND_SABOTAGE is cleared so none of its
# plants fires). That model already refuses a bare label not written in the referencing definition (its R-3
# source_check) and gives a used binding its prefix (binding-prefix). EXTENSIONS of this lane, after the load:
#   LABEL-ONLY  `(?<:x>...)` in rx text sets the label x exactly as `(?<x>...)` does, and is no capture.
#   CLASSES     `[\s\S]` (in `hits`'s body) is any character.
#   MACROS      `atomic` and `hits` are read from library.md's bodies as they stand.
#   TUPLES      a joint entry against a tuple comparison, `((p, q): >= (a, b))`, is the dictionary order on numerals.
#   SCAN        a TEXTUAL label-reference checker over every backtick program span of the three base files: per
#               definition (the program, or a binding's body), the labels it WRITES (a group in one of its literals,
#               a part label `[x = ..]`) and the names it USES; a bare name read left of `:`, in a joint entry or by
#               `$` must be written there; a path `x.y` must start at a written label or a used name.
# The OLD printed lines are read from the lane's starting commit 915b47e64 by `git show`, never typed by hand.
# Every three-mode line formatted for the documents must occur VERBATIM in them (DOC).
#
# Run (W = the worktree; any cwd):  timeout 300 python3 -I -B W/docs/dev/lanes/predref_evidence/predref_model.py
# PREDREF_SABOTAGE=sN (one at a time): a deliberately wrong rule or fact; its target check must FAIL.
#   s1  a planted printed program reading a borrowed label bare (in memory)                   -> SCAN
#   s2  the textual checker counts a used binding's labels as written                         -> SCAN
#   s3  the matcher tries alternatives last first                                             -> CONTROL
#   s4  a label-only group counted a capture                                                  -> LABELONLY
#   s5  the label-reference requirement off in the model (the old bare spelling accepted)     -> RESPELL
#   s6  `hits`'s atomic group dropped (the hit list re-entered)                               -> HITS
#   s7  a tuple comparison read component by component (each >=), not in dictionary order    -> RESPELL
#   s8  a quoted owner sentence altered (in memory)                                           -> QUOTES
#   s9  the parked label-only piece read back as still parked (in memory)                     -> MARKS
#   s10 one formatted line's subject altered before the document lookup                       -> DOC
import os
import re
import subprocess
import sys

HERE0 = os.path.dirname(os.path.abspath(__file__))
PB = os.path.join(HERE0, "..", "predbound_evidence", "predbound_model.py")
SABR = set(x for x in os.environ.get("PREDREF_SABOTAGE", "").split(",") if x)
os.environ.pop("PREDBOUND_SABOTAGE", None)


def sabr(n):
    return n in SABR


_src = open(PB, encoding="utf-8").read()
_cut = _src.index("# ================================================================== the checks")
exec(compile(_src[:_cut], PB, "exec"), globals())         # noqa: S102  (predbound's definitions, unchanged)

RESULTS = []


def check(name, ok, detail=""):                              # noqa: F811
    RESULTS.append((name, bool(ok)))
    print("%s %s: %s" % ("PASS" if ok else "FAIL", name, detail))


START2 = "915b47e64"                                         # this lane's starting commit (lane/pred-rev28)


def git_show2(rel):
    return subprocess.run(["git", "-C", W, "show", "%s:%s" % (START2, rel)], capture_output=True, text=True,
                          check=True).stdout


OLD2 = {f: git_show2("docs/design/predicates/" + f) for f in ("core.md", "library.md", "parked.md")}
NEW = {f: read(os.path.join(PRED, f)) for f in ("core.md", "library.md", "parked.md", "core_details.md",
                                                 "library_details.md", "parked_details.md")}

# ================================================================== EXTENSIONS (lane predref)
_lower_literal0 = lower_literal


def lower_literal(rx, ctx):                                  # noqa: F811
    """LABEL-ONLY: `(?<:x>...)` sets the label x as `(?<x>...)` does; it is no capture."""
    only = re.findall(r"\(\?<:(\w+)>", rx)
    n = len(CAPTURES)
    out = _lower_literal0(re.sub(r"\(\?<:(\w+)>", r"(?<\1>", rx), ctx)
    if not sabr("s4"):
        CAPTURES[n:] = [c for c in CAPTURES[n:] if c[1] not in only]
    return out


_p_class0 = p_class


def p_class(p):                                              # noqa: F811
    if p.s.startswith("\\s\\S]", p.i):
        p.i += 5
        return ("cls", ANY)
    return _p_class0(p)


HITS_BODY = lib_body(r"`hits\(r\) := (/.*?/)`")
ATOMIC_BODY = lib_body(r"`atomic\(X\) := (/.*?/)`")
_base_binds1 = base_binds


def base_binds():                                            # noqa: F811
    _base_binds1()
    body = HITS_BODY.replace("(?>", "(?:") if sabr("s6") else HITS_BODY
    MACROS["hits"] = [([("r", None)], body)]
    MACROS["atomic"] = [([("X", None)], ATOMIC_BODY)]


ANYTHING = lib_body(r"`anything` is `(.*?)`")
_parse_value2 = parse_value


def parse_value(v, ctx):                                     # noqa: F811
    if v.strip() == "anything":                              # lib/sets/anything, its body read from library.md
        return ("rx", p_alt(Src(ANYTHING)))
    return _parse_value2(v, ctx)


TUPLE = re.compile(r"\(\(([\w., ]+)\): (>=|<=|>|<) \(([\d, ]+)\)\)")
_lower_cond2 = lower_cond


def lower_cond(text, ctx, zero_key=None):                    # noqa: F811
    mm = TUPLE.fullmatch(text.strip())
    if mm:
        names = [x.strip() for x in mm.group(1).split(",")]
        for nm in names:
            NAMED.append((ctx.cur, nm))
        keys = ["%s@%s" % (nm, ctx.cur) for nm in names]
        return node_ref(("tcmp", keys, mm.group(2), [int(x) for x in mm.group(3).split(",")]))
    return _lower_cond2(text, ctx, zero_key)


_m2 = m


def m(node, s, pos, st, k):                                  # noqa: F811
    t = node[0]
    if t == "alt" and sabr("s3"):
        st2 = reset(st, node[2])
        for a in node[1][::-1]:
            r = m(a, s, pos, st2, k)
            if r is not None:
                return r
        return None
    if t == "tcmp":
        vs = [st.lab.get(x) for x in node[1]]
        if any(v is None or not CANON.fullmatch(v) for v in vs):
            return None
        a, b = tuple(int(v) for v in vs), tuple(node[3])
        if sabr("s7"):
            ok = all(CMP[node[2]](x, y) for x, y in zip(a, b))
        else:
            ok = CMP[node[2]](a, b)
        return k(pos, st) if ok else None
    return _m2(node, s, pos, st, k)


_source_check0 = source_check


def source_check(scope, start, text):                        # noqa: F811
    if sabr("s5"):
        return
    return _source_check0(scope, start, text)


def whole_state(Pg, t):
    r = Pg.at(t, 0, need_end=len(t))
    return r[2] if r else None


ANNOT = re.compile(r" \((?:[a-z_.]+ = `[^`]*`(?:, )?|[a-z_.]+ unset(?:, )?)+\)| \(hits \[[^\]]*\][^)]*\)")


def strip_annot(a):
    return ANNOT.sub("", a)


def modes_of(line):
    """The texts of a printed line: WHOLE texts, the SEARCHED text, the FIND-ALL text."""
    a = answer_part(line)
    wseg = a.split(" / SEARCHED ")[0]
    wh = re.findall(r"`([^`]*)` (?:HOLDS|FAILS)", wseg)
    sr = re.search(r" / SEARCHED `([^`]*)`", a).group(1)
    fa = re.search(r" / FIND-ALL `([^`]*)` \[", a).group(1)
    return wh, sr, fa


def label_of(st, name):
    vals = set(v for kk, v in st.lab.items() if kk.endswith("@top") and kk.split("@")[0].split(".")[-1] == name)
    return vals.pop() if len(vals) == 1 else None


def annot_ok(Pg, line):
    """Each WHOLE `t` HOLDS (l = `v`) annotation: the label's value on t's whole path."""
    bad = 0
    for t, ann in re.findall(r"`([^`]*)` HOLDS \(((?:[a-z_.]+ = `[^`]*`(?:, )?)+)\)", answer_part(line).split(" / SEARCHED ")[0]):
        st = whole_state(Pg, t)
        for nm, v in re.findall(r"([a-z_.]+) = `([^`]*)`", ann):
            if st is None or label_of(st, nm) != v:
                bad += 1
    return bad


def old_line(fname, prog_text):
    ls = [x for x in OLD2[fname].split("\n") if ("(`%s`" % prog_text) in x and "WHOLE " in x]
    assert len(ls) == 1, (prog_text, ls)
    return ls[0]


def binds_of(line, prog_text):
    tail = line.split("(`%s`" % prog_text, 1)[1]
    return ["%s := %s" % (h, b) for h, b in re.findall(r"([\w.]+(?:\([\w, ]*\))?) := `([^`]*)`", tail)]


def body_of(prog_text):
    return prog_text.split(":=", 1)[1].strip() if ":=" in prog_text and not prog_text.startswith("[") else prog_text


# ================================================================== the textual checker (SCAN)
NAME = r"[A-Za-z_]\w*"


def split_rx(t):
    """(the expression text with literals and strings blanked, the literals' texts, the holes' texts)."""
    out, rxs, holes = [], [], []
    i, n = 0, len(t)
    while i < n:
        c = t[i]
        if c == '"':
            j = i + 1
            while j < n and t[j] != '"':
                j += 2 if t[j] == "\\" else 1
            out.append('""')
            i = j + 1
            continue
        if c == "/":
            j, buf = i + 1, []
            while j < n and t[j] != "/":
                if t[j] == "\\":
                    buf.append(t[j:j + 2])
                    j += 2
                    continue
                if t.startswith("${", j):
                    d, kk = 1, j + 2
                    while kk < n and d:
                        d += {"{": 1, "}": -1}.get(t[kk], 0)
                        kk += 1
                    holes.append(t[j + 2:kk - 1])
                    buf.append("${}")
                    j = kk
                    continue
                buf.append(t[j])
                j += 1
            rxs.append("".join(buf))
            out.append(" RX ")
            i = j + 1
            continue
        out.append(c)
        i += 1
    return "".join(out), rxs, holes


def analyse(t):
    """(labels written, names used, labels read) of one definition's text, its holes included."""
    e, rxs, holes = split_rx(t)
    own = set()
    for r in rxs:
        own |= set(x.lstrip(":") for x in re.findall(r"\(\?<(?![=!])(:?" + NAME + r")>", r))
    own |= set(re.findall(r"\[(" + NAME + r") = ", e))
    e2 = re.sub(r"(?<![\w.$@])" + NAME + r"(?:\.@?\w+)+", " ", re.sub(r"\$" + NAME + r"(?:\.@?\w+)*", " ", e))
    used = set(re.findall(r"(?<![\w.$])(" + NAME + r")", e2))   # a path's own head is not a use
    refs = [mm.group(1) for mm in re.finditer(r"(?<![\w.$@])(" + NAME + r"(?:\.@?\w+)*)(?:\[\d+\])?\s*:(?!=)", e)]
    for mm in re.finditer(r"\((" + NAME + r"(?:\.\w+)*(?:\s*,\s*" + NAME + r"(?:\.\w+)*)+)\)\s*:(?!=)", e):
        refs += [x.strip() for x in mm.group(1).split(",")]
    refs += [mm.group(1) for mm in re.finditer(r"\$(" + NAME + r"(?:\.@?\w+)*)", e)]
    for h in holes:
        o2, u2, r2 = analyse(h)
        own |= o2
        used |= u2
        refs += r2
    return own, used, refs


SETWORDS = {"anything", "S"}                                 # set names a rule sentence uses left of nothing


def bad_refs(text):
    own, used, refs = analyse(text)
    if sabr("s2"):
        own |= used
    bad = []
    for r in refs:
        if r in SETWORDS:
            continue
        head = r.split(".")[0]
        if "." not in r:
            if r not in own:
                bad.append(r)
        elif head not in own and head not in used:
            bad.append(r)
    return bad


def program_spans(text):
    """(line number, span) of every backtick span that is a definition body or a program with a condition."""
    out = []
    for ln, line in enumerate(text.split("\n"), 1):
        sp = re.findall(r"`([^`]*)`", line)
        defs = [s for s in sp if re.match(r"\s*" + NAME + r"(?:\.\w+)*(\([^)]*\))?\s*:=", s)]
        progs = [s for s in sp if s not in defs and re.search(r"[\w\])]\s*:\s", s)
                 and re.search(r"&|SEQ|\$\{|\||some\(|count\(|occurs", s)]
        for s in progs + [d.split(":=", 1)[1].strip() for d in defs]:
            out.append((ln, s))
    return out


# What is LEFT bare, each with its reason. F = a fragment in a rule sentence (a condition or a group question shown
# alone or over a placeholder `P`, `S`: no definition to borrow from); Q = the owner's words or his spelling,
# quoted; R = printed as a compile error, still one; W = the worked examples' uses quoted as found (computed values
# bound alone: a compile error by bound-condition since predbound; the names are planned, undefined).
LEFT = {
    ('core.md', 'some((h: "5", m: "3"))'): "F", ('core.md', 'some(((h, m): ("5", "3")))'): "F",
    ('core.md', 'chars & (count((ch: /(?s:.)/)): ==3)'): "R",
    ('core.md', 'count((chars.ch: anything))'): "F", ('core.md', '(count((chars.ch: /(?s:.)/)): S)'): "F",
    ('core.md', 'P & x: S'): "F", ('core.md', 'P & (count((d: "7")): ==2)'): "F",
    ('core.md', 'P & !(P & (h: <5))'): "F", ('core.md', '((h: <5) SEQ (h: <5))*'): "F",
    ('core.md', '(a: "1") & P'): "F", ('core.md', 'P & (a: "1")'): "F", ('core.md', '$a + $b'): "R",
    ('core.md', 'B(A) & (d: <100)'): "Q", ('core.md', '/x${(h: <5)}/'): "R", ('core.md', '/${rx}xx/ & (d: <100)'): "R",
    ('core.md', 'count((d: "7"))'): "R", ('core.md', '(h: S)'): "R", ('core.md', '(count((d: "7")): ==2)'): "F",
    ('core.md', '(x: < 2100)'): "Q",
    ('core.md', '(year: < 2100)'): "Q", ('core.md', '(x: <200 | >900)'): "F",
    ('core.md', '(h: >5) | (h: 5, m: >=3)'): "F",
    ('library.md', 'some((ok: anything))'): "F", ('library.md', '(count((d: "7")): ==2)'): "F",
    ('library.md', 'count((d: "7"))'): "R", ('library.md', 'occurs.exactly(1, (name: set))'): "F",
    ('library.md', 'days($b) - days($a)'): "W", ('library.md', 'weekday_of($rest.year, $rest.month, $rest.day)'): "W",
    ('library.md', 'days_in($year, $month)'): "W",
}


def scan(docs):
    flagged, total = {}, 0
    for f in ("core.md", "library.md", "parked.md"):
        for ln, s in program_spans(docs[f]):
            total += 1
            b = bad_refs(s)
            if b:
                flagged.setdefault((f, s), []).append((ln, b))
    return total, flagged


# ================================================================== the checks
print("== CONTROL: the loaded matcher, programs without conditions, against python `re`")
POPA = pop("ab;7", 4)
c1 = ndiff(answers(prog('"ab" | "a"'), POPA), answers(Re(r"ab|a"), POPA))
c2 = ndiff(answers(prog("/(?:a|ab)??;/"), POPA), answers(Re(r"(?:a|ab)??;"), POPA))
c3 = ndiff(answers(prog("atomic(/a|ab/) SEQ \"c\""), pop("abc", 4)), answers(Re(r"(?>(?:a|ab))c"), pop("abc", 4)))
c4 = ndiff(answers(prog("hits(/\\d+/)"), pop("1a ", 4)), answers(Re(r"\A(?>(?:(?s:.*?)(?:\d+))*[\s\S]*)\Z"), pop("1a ", 4)))
check("CONTROL", (c1, c2, c3, c4) == ((0, 0, 0),) * 4,
      "differing (WHOLE, SEARCHED, FIND-ALL): `\"ab\" | \"a\"` %s, `(?:a|ab)??;` %s over %d texts; `atomic` %s, "
      "`hits` (its body as python `re`, `\\Z` for `\\z`: no newline in the texts) %s" % (c1, c2, len(POPA), c3, c4))

print("== SCAN: every printed program span of the three base files against label-reference (textual checker)")
docs = dict(NEW)
if sabr("s1"):
    docs["core.md"] = docs["core.md"] + "\nPlant: WHOLE `3!` HOLDS / SEARCHED `3!` `3!`@0 / FIND-ALL `3!` [`3!`@0] (`pub & (h: <5)`, pub := `[a = A] SEQ \"!\"`)\n"
total, flagged = scan(docs)
extra = sorted(k for k in flagged if k not in LEFT)
gone = sorted(k for k in LEFT if k not in flagged)
by = {}
for k in flagged:
    by[LEFT.get(k, "?")] = by.get(LEFT.get(k, "?"), 0) + 1
check("SCAN", not extra and not gone,
      "%d program spans checked; %d distinct spans still read a label bare, all on LEFT (%s); not on LEFT: %s; "
      "on LEFT but no longer flagged: %s" % (total, len(flagged), ", ".join("%s %d" % kv for kv in sorted(by.items())),
                                             extra or "none", gone or "none"))
ototal, oflagged = scan(OLD2)
print("   at %s: %d spans checked, %d distinct spans flagged; re-spelled since: %d" %
      (START2, ototal, len(oflagged), len([k for k in oflagged if k not in flagged])))
for k in sorted(oflagged):
    if k not in flagged:
        print("   re-spelled: %s `%s`" % k)

print("== RESPELL: each re-spelled printed line, the old program (read bare, as before) against the new")
RESPELL = [  # (file, tag, old program, new program)
    ("core.md", "core/patterns/alternation", "(B | A) & (l: <20)", "[ab = B | A] & (ab.l: <20)"),
    ("core.md", "core/patterns/atomic", "atomic(B | A) & (l: <20)", "[ab = atomic(B | A)] & (ab.l: <20)"),
    ("core.md", "core/labels/labels-vs-captures/array-vs-passes",
     '([ok = item & ((h, m): ("5", "3"))] | item)+ & some((ok: anything))',
     '([ok = [it = item] & ((it.h, it.m): ("5", "3"))] | item)+ & some((ok: anything))'),
    ("core.md", "core/labels/export", "pub & (h: <5)", "pub & (pub.h: <5)"),
    ("core.md", "core/labels/export/flat-read-outside", "pair & (x: <5)", "pair & (pair.x: <5)"),
    ("core.md", "core/labels/export/flat-read-outside", "date & (v: <5)", "date & (date.v: <5)"),
    ("core.md", "core/values/tuples", "time & ((h, m): >= (9, 30))", "time & ((time.h, time.m): >= (9, 30))"),
    ("core.md", "core/values/metadata", "/${days}/ & (w.index: >= 2)", "/${days}/ & (days.w.index: >= 2)"),
    ("core.md", "core/holes/labels", "/${year}-x/ & (v: >= 2000)", "/${year}-x/ & (year.v: >= 2000)"),
    ("core.md", "core/holes/bare-condition/nested-scope", "C := B(A) & (d: <100)", "C := B(A) & (A.d: <100)"),
]
rs_bad = []
for f, tag, old, new in RESPELL:
    L0 = old_line(f, old)
    binds = binds_of(L0, old)
    wh, sr, fa = modes_of(L0)
    printed_old = strip_annot(answer_part(L0))
    Po = prog(body_of(old), binds, bare=True)
    ro = refused(body_of(old), binds)
    try:
        Pn = prog(body_of(new), binds)
        got = fmt(Pn, wh, sr, fa)
        an = annot_ok(Pn, L0)
    except CompileError as e:
        got, an = "REFUSED (%s)" % e, -1
    got_old = fmt(Po, wh, sr, fa)
    L1 = L0.replace("(`%s`" % old, "(`%s`" % new)
    doc_line(L1, tag)
    ok = got == printed_old and got_old == printed_old and ro is not None and an == 0
    if not ok:
        rs_bad.append(tag)
    print("   %s: `%s` -> `%s`: new %s the printed answers%s; old read bare %s; old under the rule %s" %
          (tag, old, new, "GIVES" if got == printed_old else "DIFFERS FROM", "" if an <= 0 else " (annotations %d bad)" % an,
           "gives them" if got_old == printed_old else "DIFFERS", "refused" if ro else "ACCEPTED"))
check("RESPELL", not rs_bad, "%d lines re-spelled, every answer unchanged in every mode (annotated labels too); the "
      "old spelling refused under the rule; failing: %s" % (len(RESPELL), rs_bad or "none"))

print("== HITS: his example and the atomic hit list; the record's four pasted lines, from the program text")
rec_lines = [x for x in RECORD.split("\n") if x.startswith("plain (hits.hit: <5), the last hit: ")
             or x.startswith("occurs.none((hits.hit: >= 5)), every hit: ")]
assert len(rec_lines) == 4, rec_lines
HW, HS, HF = ["a1b3", "a9b3", "a3b9", "a1b22", "ab"], "x9 3", "a9b3 c7"


def hitlist(lab, call, t):
    st = whole_state(prog("[%s = %s]" % (lab, call)), t)
    return settings(st.log, "%s.hit@top" % lab, "top") if st else None


def fmt_rec(Pg, lab=None, call=None):
    parts = []
    for t in HW:
        x = "WHOLE `%s` %s" % (t, "HOLDS" if Pg.whole(t) else "FAILS")
        if lab:
            x += " (hits %r)" % (hitlist(lab, call, t),)
        parts.append(x)
    r = Pg.search(HS)
    parts.append("SEARCHED `%s` %s" % (HS, "`%s`@%d" % (HS[r[0]:r[1]], r[0]) if r else "FAILS"))
    parts.append("FIND-ALL `%s` [%s]" % (HF, ", ".join("`%s`@%d" % x for x in Pg.findall(HF))))
    return " / ".join(parts)


def fmt_doc(Pg, lab=None, call=None):
    w = []
    for t in HW:
        x = "`%s` %s" % (t, "HOLDS" if Pg.whole(t) else "FAILS")
        if lab:
            x += " (hits [%s])" % ", ".join("`%s`" % v for v in hitlist(lab, call, t))
        w.append(x)
    r = Pg.search(HS)
    return "WHOLE %s / SEARCHED `%s` %s / FIND-ALL `%s` [%s]" % (
        ", ".join(w), HS, "`%s`@%d" % (HS[r[0]:r[1]], r[0]) if r else "FAILS", HF,
        ", ".join("`%s`@%d" % x for x in Pg.findall(HF)))


HPROG = [  # (record line, doc piece, doc label, program, hit-list label and call or None)
    (0, "lib/search/occurrences", "Plain read, the last hit", "[hits = occurrences(/\\d+/)] & (hits.hit: <5)", None),
    (1, "lib/search/occurrences", "Every hit, a group question", "[hits = occurrences(/\\d+/)] & occurs.none((hits.hit: >= 5))", None),
    (2, "lib/search/hits", "Plain read, the last hit", "[h = hits(/\\d+/)] & (h.hit: <5)", ("h", "hits(/\\d+/)")),
    (3, "lib/search/hits", "Every hit, a group question", "[h = hits(/\\d+/)] & occurs.none((h.hit: >= 5))", ("h", "hits(/\\d+/)")),
]
h_bad = []
for i, tag, label, expr, hl in HPROG:
    Pg = prog(expr)
    got = fmt_rec(Pg, *(hl or (None, None)))
    want = rec_lines[i].split(": ", 1)[1].split(" ", 0)[0]
    want = rec_lines[i][len(rec_lines[i].split("WHOLE", 1)[0]):]
    same = got == want
    if not same:
        h_bad.append(i)
    print("   record line %d %s: `%s`" % (i + 1, "REPRODUCED" if same else "DIFFERS (%s)" % got, expr))
    print("   " + doc_line("%s: %s (`%s`)" % (label, fmt_doc(Pg, *(hl or (None, None))), expr), tag))
bare_hit = refused("hits(/\\d+/) & (hit: <5)")
U100 = {"1234": False, "12 34": True, "12 345": False, "x300 12": False}
P100 = prog("[h = hits(/\\d+/)] & occurs.none((h.hit: >= 100))")
u100 = all(P100.whole(t) == v for t, v in U100.items())
u100l = hitlist("h", "hits(/\\d+/)", "1234") == ["1234"]
check("HITS", not h_bad and bare_hit is not None and u100 and u100l,
      "the record's four pasted lines reproduced: %s; the bare `hits(/\\d+/) & (hit: <5)` %s; \"Every hit under 100\" "
      "re-spelled `[h = hits(/\\d+/)] & occurs.none((h.hit: >= 100))`: its four prose answers %s, `1234`'s hit list %s"
      % ("all 4" if not h_bad else "NOT %s" % h_bad, "refused" if bare_hit else "ACCEPTED", "agree" if u100 else "DIFFER",
         "[`1234`]" if u100l else "differs"))

print("== LABELONLY: the label-only group in the provided bodies; the census of provided bodies writing a group")
CENSUS = {}
for s in re.findall(r"`([^`]*)`", ws(NEW["library.md"])):
    mm = re.match(r"([\w.]+)\([^)]*\)(?: := | is the lazy-gap loop )?", s)
    if not mm or ":=" not in s or "(?<" not in s:
        continue
    body = s.split(":=", 1)[1]
    kind = ("label-only" if re.search(r"\(\?<:\w+>", body) else
            "hole-named" if "(?<${" in body else "capture" if re.search(r"\(\?<\w+>", body) else None)
    if kind:
        CENSUS[mm.group(1)] = kind
occ_stmt = re.search(r"`occurrences\(x, min = 0\)` is the lazy-gap loop `(/.*?/)`", NEW["library.md"]).group(1)
CENSUS["occurrences"] = "label-only" if "(?<:hit>" in occ_stmt else "capture"
census_ok = CENSUS == {"occurrences": "label-only", "hits": "label-only", "capture": "hole-named"}
print("   provided bodies writing a group in rx text (library.md): %s" % CENSUS)
OLDOCC = re.search(r"`occurrences\(x, min = \d+\)` is the lazy-gap loop `(/.*?/)`", OLD2["library.md"]).group(1)
OLDHITS = re.search(r"`hits\(r\) := (/.*?/)`", OLD2["library.md"]).group(1)
lo_rows = []
for expr, tx in [("[hits = occurrences(/\\d+/)] & (hits.hit: <5)", HW + [HS, HF]),
                 ("[h = hits(/\\d+/)] & occurs.none((h.hit: >= 5))", HW + [HS, HF]),
                 ('hits(/a(?<g>x)?/) & (g: "x")', ["aax", "axa", "aax axa"]),
                 ("occurrences(/(?<n>\\d+)/ & (n: <100))", ["1234", "12345", "1 2"])]:
    Pn = prog(expr)
    capn = sorted(set(c[1] for c in CAPTURES))
    MACROS_SAVE = (OCC_BODY, HITS_BODY)
    globals()["OCC_BODY"], globals()["HITS_BODY"] = OLDOCC, OLDHITS
    Po = prog(expr)
    capo = sorted(set(c[1] for c in CAPTURES))
    globals()["OCC_BODY"], globals()["HITS_BODY"] = MACROS_SAVE
    d = ndiff(answers(Pn, tx), answers(Po, tx))
    lo_rows.append((expr, d, capn, capo))
    print("   `%s`: label-only body against the old `(?<hit>...)` body %s differing; captures now %s, before %s"
          % (expr, d, capn, capo))
hl = printed(NEW["library.md"], '(`hits(/a(?<g>x)?/) & (g: "x")`')
hl_got = fmt(prog('hits(/a(?<g>x)?/) & (g: "x")'), *modes_of(hl))
lo_ok = (census_ok and all(r[1] == (0, 0, 0) and "hit" not in r[2] and "hit" in r[3] for r in lo_rows)
         and "g" in lo_rows[2][2] and "n" in lo_rows[3][2] and hl_got == strip_annot(answer_part(hl)))
check("LABELONLY", lo_ok, "census %s; `(?<:hit>...)` answers as `(?<hit>...)` did on 4 programs and is no capture, "
      "the user's argument groups `g`, `n` stay captures; `hits(/a(?<g>x)?/) & (g: \"x\")`'s printed line %s"
      % ("as stated" if census_ok else "DIFFERS", "reproduced" if hl_got == strip_annot(answer_part(hl)) else "DIFFERS"))

print("== QUOTES: every owner sentence this lane prints, word for word in the record")
QUOTES = [
    "label-reference: required. we can relax it later as you say although i'm not inclined to.",
    "help-captures: 1. i propose the form (?<:x>...) for a label only group x. i've mentioned it before.",
    "occurences et al should only set labels not captures unless they are so declared.",
    "3. validate: you can label the results [ hits = occurences(...) ] & (hits.hit: <5)",
    "C can see d as a flat look into A",
    "for capture group regex: i proposed /(<:x>foo)/ would be regex for a labeled group that is not a",
    "oops. yes, i missed the ?. it should look like the top row",
]
if sabr("s8"):
    QUOTES[2] = QUOTES[2].replace("only set", "only ever set")
qbad = [q for q in QUOTES if ws(q) not in RECORD_WS]
qdoc = [q for q in QUOTES[:4] if ws(q) not in ws(NEW["core.md"] + NEW["library.md"] + NEW["core_details.md"]
                                                + NEW["library_details.md"])]
check("QUOTES", not qbad and not qdoc, "%d passages found in the record; missing: %s; the four of this day printed: %s"
      % (len(QUOTES) - len(qbad), qbad or "none", "all" if not qdoc else "NOT %s" % qdoc))

print("== MARKS: statuses, the move, the statements rewritten")
core, park = NEW["core.md"], NEW["parked.md"]
if sabr("s9"):
    park += "\n### The label-only group   [parked/ideas/label-only-group]   parked 2026-11-19\n"
marks = {
    "label-only group under construction": "[core/labels/label-only-group]   under-construction 2026-11-22" in core,
    "parked piece gone": "[parked/ideas/label-only-group]" not in park,
    "was: line on the new entry": "was: parked/ideas/label-only-group (2026-11-22" in NEW["core_details.md"],
    "call-prefix open": "[core/labels/paths/call-prefix]   open call-prefix 2026-11-22" in core,
    "no statement says read flat": not re.search(r"read flat|Read flat", core + NEW["library.md"]),
    "flat-read-outside statement": "is read through the binding's name (`pair.x`)" in core,
    "bodies label-only": "(?<:hit>${x})" in NEW["library.md"] and "(?<:hit>${r})" in NEW["library.md"],
    "no provided body called a capture": "so it is a capture" not in NEW["library.md"],
}
check("MARKS", all(marks.values()), "; ".join("%s %s" % (k, "yes" if v else "NO") for k, v in marks.items()))

print("== DOC: every formatted line verbatim in the documents")
ALLDOC = "\n".join(NEW.values())
missing = []
for i, (tag, L) in enumerate(LINES):
    if sabr("s10") and i == 0:
        L = L.replace("WHOLE `", "WHOLE `x", 1)
    if L not in ALLDOC:
        missing.append((tag, L[:90]))
check("DOC", not missing, "%d lines; missing: %s" % (len(LINES), missing or "none"))

nf = sum(1 for _, ok in RESULTS if not ok)
print("predref_model: %d checks, %d failed%s" % (len(RESULTS), nf,
                                                ("" if not nf else " (%s)" % ", ".join(n for n, ok in RESULTS if not ok))))
sys.exit(1 if nf else 0)
