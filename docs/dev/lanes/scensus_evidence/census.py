#!/usr/bin/env python3
"""scensus: compile-only censuses M0-M6 for the "one instruction stream" design.

Plan: scratch/stream/synth/approach.md section 7 (M0-M6).  READ-ONLY on the
tree: it runs build/pcrec (--emit-ir, --emit-facts, --list-source), greps
src/, and writes only under --out.  No timing, no emitted C.

Per pattern it reads ONLY fields pcrec already prints:
  --emit-ir  #section summary: engine (+ "forced by:" note), prefilter,
             rungs, resume-points, prune-ceiling, subject-ceiling.
             A DFA-routed pattern makes --emit-ir refuse ("compiles to the
             DFA engine"): that refusal is the DFA verdict.
  --no-captures --emit-facts (M1 proxy only): req_byte / req_run /
             req_landmark_maxoff of the capture-erased compile.
Pattern STRUCTURE (M3-M6) is not printed by pcrec as a tree: the small
conservative scanner below (Scanner) builds one from the pattern text.  Every
structural count is therefore "what the pattern text admits", with the
approximations named in the report.  A pattern the scanner cannot follow is
counted `unparsed`, never guessed.

Usage:  census.py [--root DIR] [--out DIR] [--smoke] [--limit N] [--jobs N]
Exit 0 and a final `scensus: COMPLETE ...` line only if every plant passed.
"""
import argparse, collections, concurrent.futures as cf, os, re, subprocess, sys

# ---------------------------------------------------------------- scanner --
IRREG = ("backref", "callout", "look", "atomic", "recurse", "cond", "verb", "keep")
ALPHA = {"pla": "look", "plb": "look", "nla": "look", "nlb": "look",
         "positive_lookahead": "look", "positive_lookbehind": "look",
         "negative_lookahead": "look", "negative_lookbehind": "look", "atomic": "atomic"}
VERBS = {"ACCEPT", "FAIL", "F", "COMMIT", "PRUNE", "SKIP", "THEN", "MARK"}


class N:
    """pattern node.  kind: lit cls any anchor cap grp alt seq rep + IRREG"""
    __slots__ = ("kind", "kids", "lo", "hi")

    def __init__(self, kind, kids=(), lo=1, hi=1):
        self.kind, self.kids, self.lo, self.hi = kind, list(kids), lo, hi


class Bad(Exception):
    pass


class Scanner:
    def __init__(self, s):
        self.s, self.i, self.n = s, 0, len(s)

    def peek(self, k=0):
        return self.s[self.i + k] if self.i + k < self.n else ""

    def parse(self):
        # leading (*OPTION) verbs are settings, not backtracking verbs
        while True:
            m = re.match(r"\(\*[A-Z_0-9=]+\)", self.s[self.i:])
            if not m or m.group(0)[2:-1].split("=")[0] in VERBS:
                break
            self.i += m.end()
        node = self.alt()
        if self.i != self.n:
            raise Bad("unbalanced )")
        return node

    def alt(self):
        branches = [self.seq()]
        while self.peek() == "|":
            self.i += 1
            branches.append(self.seq())
        return branches[0] if len(branches) == 1 else N("alt", branches)

    def seq(self):
        items = []
        while self.i < self.n and self.peek() not in "|)":
            a = self.atom()
            if a is not None:
                items.append(self.quant(a))
        return N("seq", items)

    def quant(self, a):
        while True:
            c = self.peek()
            if c in ("*", "+", "?"):
                lo, hi = {"*": (0, None), "+": (1, None), "?": (0, 1)}[c]
                self.i += 1
            elif c == "{":
                m = re.match(r"\{(\d*)(?:,(\d*))?\}", self.s[self.i:])
                if not m or (m.group(1) == "" and not m.group(2)):
                    return a                      # literal brace
                lo = int(m.group(1) or 0)
                hi = (int(m.group(2)) if m.group(2) else None) if "," in m.group(0) else lo
                self.i += m.end()
            else:
                return a
            if self.peek() in ("?", "+"):         # lazy / possessive: same shape
                self.i += 1
            a = N("rep", [a], lo, hi)

    def group_end(self):
        if self.peek() != ")":
            raise Bad("missing )")
        self.i += 1

    def atom(self):
        c = self.s[self.i]
        self.i += 1
        if c == "\\":
            return self.escape()
        if c == "[":
            self.bracket()
            return N("cls")
        if c == ".":
            return N("any")
        if c in "^$":
            return N("anchor")
        if c == "(":
            return self.group()
        return N("lit")

    def escape(self):
        c = self.peek()
        if c == "":
            raise Bad("trailing backslash")
        self.i += 1
        if c == "Q":                              # \Q...\E literal run
            e = self.s.find("\\E", self.i)
            lit = self.s[self.i:] if e < 0 else self.s[self.i:e]
            self.i = self.n if e < 0 else e + 2
            return N("seq", [N("lit") for _ in lit])
        if c == "E":
            return None
        if c in "123456789":
            while self.peek().isdigit():
                self.i += 1
            return N("backref")
        if c in "gk":
            m = re.match(r"(\{[^}]*\}|<[^>]*>|'[^']*'|-?\d+)", self.s[self.i:])
            if not m:
                raise Bad("bad \\g/\\k")
            body = m.group(1)
            self.i += m.end()
            if c == "g" and re.match(r"[<'].*", body):
                return N("recurse")               # \g<n> is a subroutine call
            return N("backref")
        if c == "K":
            return N("keep")
        if c in "bBAzZG":
            return N("anchor")
        if c in "pP":
            m = re.match(r"(\{[^}]*\}|.)", self.s[self.i:])
            self.i += m.end() if m else 0
            return N("cls")
        if c in "xo":
            m = re.match(r"(\{[^}]*\}|[0-9A-Fa-f]{0,2})", self.s[self.i:])
            self.i += m.end() if m else 0
            return N("lit")
        if c == "c":
            self.i += 1
            return N("lit")
        if c == "0":
            while self.peek() in list("01234567") and self.peek():
                self.i += 1
            return N("lit")
        if c in "dDwWsShHvVRNX":
            return N("cls")
        return N("lit")

    def bracket(self):
        if self.peek() == "^":
            self.i += 1
        if self.peek() == "]":
            self.i += 1
        while self.i < self.n and self.s[self.i] != "]":
            if self.s[self.i] == "\\":
                self.i += 2
            elif self.s.startswith("[:", self.i):
                e = self.s.find(":]", self.i + 2)
                self.i = self.i + 2 if e < 0 else e + 2
            else:
                self.i += 1
        if self.i >= self.n:
            raise Bad("unterminated class")
        self.i += 1

    def group(self):
        s = self.s
        if self.peek() == "*":                    # (*VERB) / (*pla:...) alpha forms
            m = re.match(r"\*([A-Za-z_]+)(?::[^)]*)?\)", s[self.i:])
            if m and m.group(1) in VERBS:
                self.i += m.end()
                return N("verb")
            m = re.match(r"\*([A-Za-z_]+):", s[self.i:])
            nm = m.group(1) if m else ""
            if m and (nm in ALPHA or nm.startswith(("na", "non_atomic"))):
                self.i += m.end()
                body = self.alt()
                self.group_end()
                return N(ALPHA.get(nm, "look"), [body])
            m = re.match(r"\*[A-Z_0-9=]+\)", s[self.i:])
            if m:                                 # mid-pattern (*UCP)-style option
                self.i += m.end()
                return None
            raise Bad("unmodelled (* group")
        if self.peek() != "?":
            body = self.alt()
            self.group_end()
            return N("cap", [body])
        self.i += 1
        c = self.peek()
        if c == "#":
            e = s.find(")", self.i)
            if e < 0:
                raise Bad("unterminated comment")
            self.i = e + 1
            return None
        if c == ":" or c == "|":
            self.i += 1
            body = self.alt()
            self.group_end()
            return N("grp", [body])
        if c == "*" or (c == "<" and self.peek(1) == "*"):      # non-atomic lookaround
            self.i += 1 if c == "*" else 2
            body = self.alt()
            self.group_end()
            return N("look", [body])
        if c in "=!":
            self.i += 1
            body = self.alt()
            self.group_end()
            return N("look", [body])
        if c == "<" and self.peek(1) in "=!":
            self.i += 2
            body = self.alt()
            self.group_end()
            return N("look", [body])
        if c == ">":
            self.i += 1
            body = self.alt()
            self.group_end()
            return N("atomic", [body])
        if c in "<'" or (c == "P" and self.peek(1) == "<"):
            if c == "P":
                self.i += 1
            close = ">" if self.s[self.i] == "<" else "'"
            e = s.find(close, self.i + 1)
            if e < 0:
                raise Bad("bad group name")
            self.i = e + 1
            body = self.alt()
            self.group_end()
            return N("cap", [body])
        if c == "P" and self.peek(1) in ">=":
            kind = "recurse" if self.peek(1) == ">" else "backref"
            e = s.find(")", self.i)
            self.i = e + 1
            return N(kind)
        if c == "&" or c == "R" or c.isdigit() or (c in "+-" and self.peek(1).isdigit()):
            e = s.find(")", self.i)
            if e < 0:
                raise Bad("bad recursion")
            self.i = e + 1
            return N("recurse")
        if c == "(":                              # conditional
            e = s.find(")", self.i)
            if e < 0:
                raise Bad("bad condition")
            self.i = e + 1
            body = self.alt()
            self.group_end()
            return N("cond", [body])
        if c == "C":
            if self.peek(1) == "`":              # inline-C callout: (?C`code`)
                e = s.find("`", self.i + 2)
                e = s.find(")", e) if e >= 0 else -1
            else:
                e = s.find(")", self.i)
            if e < 0:
                raise Bad("bad callout")
            self.i = e + 1
            return N("callout")
        m = re.match(r"([A-Za-z\-^]*)(\)|:)", s[self.i:])   # (?i) / (?i:...)
        if m:
            self.i += m.end()
            if m.group(2) == ")":
                return None
            body = self.alt()
            self.group_end()
            return N("grp", [body])
        raise Bad("unmodelled (? group")


def parse_pattern(p):
    """tree or None (unparsed)"""
    try:
        return Scanner(p).parse()
    except (Bad, IndexError, ValueError, RecursionError):
        return None


def flatten(root):
    toks = []                                     # (node, depth, rep_anc, irreg_anc)

    def go(n, depth, rep, irr):
        toks.append((n, depth, rep, irr))
        k = n.kind
        for c in n.kids:
            d = depth
            if k in ("cap", "grp", "atomic", "look", "cond", "rep", "alt"):
                d += 1
            go(c, d, rep or (k == "rep" and (n.hi is None or n.hi > 1)),
               irr or k in IRREG)
    go(root, 0, False, False)
    return toks


def structure(p):
    try:
        return _structure(p)
    except RecursionError:
        return None


def _structure(p):
    """structural flags for pattern text p, or None if unparsed"""
    t = parse_pattern(p)
    if t is None:
        return None
    toks = flatten(t)
    kinds = collections.Counter(n.kind for n, *_ in toks)
    irr = [(i, n, d) for i, (n, d, r, a) in enumerate(toks) if n.kind in IRREG]
    caps = kinds["cap"]
    cap_in_rep = any(n.kind == "cap" and r for n, d, r, a in toks)
    # M5a: first irregular node at depth>=1, then a regular consuming leaf
    # after its subtree, outside any irregular ancestor.
    reg_after = False
    nested = [(i, n, d) for i, n, d in irr if d >= 1]
    if nested:
        i, x, _ = nested[0]
        end = i + 1 + sum(1 for _ in subtree(x)) - 1       # skip x's own subtree
        for n, d, r, a in toks[end:]:
            if n.kind in ("lit", "cls", "any") and not a:
                reg_after = True
                break
    return {"caps": caps, "irreg": sorted(set(n.kind for _, n, _ in irr)),
            "n_irreg": len(irr), "top_irreg": sum(1 for _, _, d in irr if d == 0),
            "nested_irreg": len(nested), "cap_in_rep": cap_in_rep,
            "reg_after_nested": reg_after}


def subtree(n):
    yield n
    for c in n.kids:
        yield from subtree(c)


# ------------------------------------------------------------ pcrec runner --
def esc_arg(p):
    """pattern text -> --pattern-esc value (the .rxt quoted-escape form)"""
    out = []
    for ch in p:
        o = ord(ch)
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif 32 <= o < 127:
            out.append(ch)
        else:
            for b in ch.encode("utf-8", "surrogateescape"):
                out.append("\\x%02x" % b)
    return "\"" + "".join(out) + "\""


def run(pcrec, args, timeout=40):
    try:
        r = subprocess.run([pcrec] + args, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")


def sections(text):
    cur, secs = None, {}
    for line in text.splitlines():
        if line.startswith("#section "):
            cur = line[9:].strip()
            secs[cur] = []
        elif cur is not None and line and not line.startswith("#"):
            secs[cur].append(line.split("\t"))
    return secs


def compile_one(pcrec, e):
    """-> record dict.  e: pattern, i, enc"""
    base = ["--features", "all"] + (["-i"] if e["i"] else []) + \
           (["-e", e["enc"]] if e["enc"] else []) + ["--pattern-esc", "--pattern", esc_arg(e["pat"])]
    rec = {"engine": "", "forced": "", "prefilter": "", "prune": "", "rungs": "",
           "resume": "", "subj_ceiling": "", "status": ""}
    rc, out, err = run(pcrec, base + ["--emit-ir"])
    if rc != 0:
        if "compiles to the DFA engine" in err:
            rec.update(engine="dfa", status="ok")
            m = re.search(r"because (.*?)(?: Pass| \(pattern)", err)
            rec["forced"] = ""
        else:
            rec.update(status="refused" if rc != 124 else "timeout",
                       forced=err.strip().splitlines()[0][:120] if err.strip() else "")
        return rec
    s = {r[0]: r for r in sections(out).get("summary", []) if len(r) >= 2}
    g = lambda k: s[k][1] if k in s else ""
    eng = s.get("engine", ["", "", ""])
    rec.update(status="ok", engine=eng[1], prefilter=g("prefilter"),
               prune=g("prune-ceiling"), rungs=g("rungs"), resume=g("resume-points"),
               subj_ceiling=g("subject-ceiling"))
    note = eng[2] if len(eng) > 2 else ""
    rec["forced"] = re.sub(r"^forced by:\s*", "", note)
    return rec


def landmark_proxy(pcrec, e):
    """M1 proxy: facts of the capture-erased compile.  NOT the D161 add. 17
    admission (not printed): only 'a necessary landmark exists'."""
    base = ["--features", "all", "--no-captures"] + (["-i"] if e["i"] else []) + \
           (["-e", e["enc"]] if e["enc"] else []) + ["--pattern-esc", "--pattern", esc_arg(e["pat"])]
    rc, out, err = run(pcrec, base + ["--emit-facts"])
    if rc != 0:
        return "err", ""
    f = {}
    for r in sections(out).get("facts", []):
        if len(r) >= 7:
            f[r[1]] = (r[4], r[6])
    have = [k for k in ("req_run", "req_byte") if k in f and f[k][0] == "derived"
            and f[k][1] not in ("none", "")]
    return ("landmark-exists" if have else "no-landmark"), \
        f.get("req_landmark_maxoff", ("", ""))[1]


# ---------------------------------------------------------------- corpora ---
def unesc(v):
    return re.sub(r"\\(x[0-9a-fA-F]{2}|.)", lambda m: {"t": "\t", "n": "\n", "r": "\r",
                  "\\": "\\"}.get(m.group(1)) if m.group(1)[0] != "x" and m.group(1) in "tnr\\"
                  else (chr(int(m.group(1)[1:], 16)) if m.group(1)[0] == "x" else m.group(0)), v)


def list_rxt(pcrec, path, pop):
    rc, out, err = run(pcrec, ["--list-source", path], timeout=60)
    if rc != 0:
        return []
    hdr, rows = None, []
    for line in out.splitlines():
        if line.startswith("#kind\t"):
            hdr = line[1:].split("\t")
        elif line.startswith("#section"):
            break
        elif hdr and line and not line.startswith("#"):
            f = line.split("\t")
            d = dict(zip(hdr, f + [""] * (len(hdr) - len(f))))
            if d["kind"] in ("pattern", "pattern-esc"):
                rows.append({"pat": unesc(d["pattern"]), "i": "i" in d.get("flags", ""),
                             "enc": d.get("encoding", "") if d.get("encoding", "") in ("byte", "utf8") else "",
                             "pop": pop, "src": "%s:%s" % (path, d["line"])})
    return rows


def load_corpora(root, bench, pcrec):
    ents = []
    for dp, dn, fn in os.walk(os.path.join(root, "tests")):
        for f in sorted(fn):
            if f.endswith(".rxt"):
                ents += list_rxt(pcrec, os.path.join(dp, f), "corpus")
    b = os.path.join(bench, "bench")
    if os.path.isdir(b):
        for sub in sorted(os.listdir(b)):
            for rel in ("patterns.rxt",):
                p = os.path.join(b, sub, rel)
                if os.path.isfile(p):
                    ents += list_rxt(pcrec, p, "bench")
            ex = os.path.join(b, sub, "export")
            if os.path.isdir(ex):
                for f in sorted(os.listdir(ex)):
                    if f.endswith(".rxt"):
                        ents += list_rxt(pcrec, os.path.join(ex, f), "bench")
        up = os.path.join(b, "unusual", "patterns")
        if os.path.isdir(up):
            for f in sorted(os.listdir(up)):
                if f.endswith(".rx"):
                    t = open(os.path.join(up, f), "rb").read().decode("utf-8", "replace").rstrip("\n")
                    ents.append({"pat": t, "i": False, "enc": "", "pop": "bench",
                                 "src": os.path.join(up, f)})
    seen, out = set(), []
    for e in ents:                                 # dedup within a population
        k = (e["pop"], e["pat"], e["i"], e["enc"])
        if k not in seen and "\x00" not in e["pat"]:
            seen.add(k)
            out.append(e)
    return out


# ------------------------------------------------------------------ plants --
# (pattern, {measurement: expected row}).  A plant is compiled by the same
# code as the corpus; any mismatch makes the whole run RED.  Rows are the
# classifier outputs below (cls_*).
PLANTS = [
    (r"(\w+)@(\w+)\.com", {"engine": "vm", "m1": "vm-resume0", "m2": "yes",
                           "m3": "captures-only", "m4": "no", "m5a": "no", "m5b": "no", "m6": "none"}),
    (r"(\w+)\s+\1", {"engine": "vm", "m2": "no-backreference", "m3": "mixed-or-other",
                     "m1": "vm-resume0"}),
    (r"x(?C1)y\d+", {"engine": "vm", "m2": "no-callout", "m3": "mixed-or-other"}),
    (r"(\w+\.)+com", {"engine": "vm", "m4": "yes", "m6": "resume>0 regular-apart-from-captures frames-unbounded"}),
    (r"(a+)+b", {"engine": "vm", "m4": "yes", "m6": "resume>0 regular-apart-from-captures frames-unbounded"}),
    (r"abc", {"engine": "dfa"}),
    (r"foo(?=bar)", {"engine": "vm", "m3": "zero-width-only"}),
    (r"(\w+)=([^;]*);(?:\1(?=x)|x)+", {"engine": "vm", "m5a": "yes", "m5b": "yes"}),
    (r"(?:a(\w)\1)cd", {"engine": "vm", "m5a": "yes", "m5b": "no"}),
    (r"(?:a(?=b))cd", {"engine": "dfa", "m5a": "yes", "m5b": "no"}),
    (r"(a)(?=a)b\1", {"engine": "vm", "m5a": "no", "m5b": "yes", "m3": "mixed-or-other"}),
]


def classify(rec, st):
    """measurement rows for one compiled pattern.  rec: compile record,
    st: structure() or None."""
    out = {"engine": rec["engine"] if rec["status"] == "ok" else rec["status"]}
    vm = rec["status"] == "ok" and rec["engine"] == "vm"
    if st is not None:
        out["m4"] = "yes" if st["cap_in_rep"] else "no"
        out["m5a"] = "yes" if st["reg_after_nested"] else "no"
        out["m5b"] = "yes" if st["n_irreg"] > 1 else "no"
    if not vm:
        return out
    res = int(rec["resume"] or 0)
    out["m1"] = "vm-resume0" if res == 0 else "vm-resume>0"
    pf = rec["prefilter"].split()[0] if rec["prefilter"] else "?"
    out["m2"] = pf
    out["m2_prune"] = rec["prune"]
    fb = rec["forced"]
    if st is None:
        out["m3"] = "unparsed"
    elif not st["irreg"] and st["caps"] and fb.startswith("capture group"):
        out["m3"] = "captures-only"
    elif st["irreg"] and set(st["irreg"]) <= {"look"}:
        out["m3"] = "zero-width-only"
    elif not st["irreg"]:
        out["m3"] = "no-irregular-node(forced-by-other)"
    else:
        out["m3"] = "mixed-or-other"
    reg = st is not None and not st["irreg"]
    fu = "frames-unbounded" in rec["rungs"].split(",")
    parts = []
    if res > 0 and reg:
        parts.append("resume>0 regular-apart-from-captures")
    if fu:
        parts.append("frames-unbounded")
    out["m6"] = " ".join(parts) if parts else "none"
    return out


def work(args):
    pcrec, e = args
    rec = compile_one(pcrec, e)
    st = structure(e["pat"])
    cl = classify(rec, st)
    prox, mo = "", ""
    if cl.get("m1") == "vm-resume0" and rec["forced"].startswith("capture group"):
        prox, mo = landmark_proxy(pcrec, e)
    return e, rec, st, cl, prox, mo


# --------------------------------------------------------------------- M0 ---
# (id, description, file, cited line range, regex that must occur in the range)
M0_SITES = [
    ("X1a", "hybrid prefilter pair emission", "src/gen/emit_vm.c", (13005, 13033), r"prefilter|prefn"),
    ("X1b", "H3 three-consumer window argument", "src/gen/emit_vm.c", (10366, 10441), r"prefilter|window|H1"),
    ("X2", "VM span-loop cursor rung vm_cursor_rep", "src/gen/emit_vm.c", (4890, 4890), r"vm_cursor_rep"),
    ("X3", "VM revdet vm_revdet_rep", "src/gen/emit_vm.c", (5705, 5705), r"vm_revdet_rep"),
    ("X4", "VM alternation island vm_isl_*", "src/gen/emit_vm.c", (4298, 4745), r"vm_isl_"),
    ("X5", "VM literal-run DELEG_VMRUN", "src/gen/emit_vm.c", None, r"DELEG_VMRUN"),
    ("X6", "VM backref compare DELEG_N7", "src/gen/emit_dfa.c", None, r"DELEG_N7"),
    ("X7", "DFA scan edges DELEG_EDGE", "src/gen/emit_dfa.c", None, r"DELEG_EDGE"),
    ("X7b", "scanedge.c analysis", "src/opt/scanedge.c", None, r"."),
    ("X8", "DFA stay/skip DELEG_STAY", "src/gen/emit_dfa.c", None, r"DELEG_STAY"),
    ("X9", "start search NEXT rows / VM start seek (DELEG_OFS, DELEG_MLINE)", "src/gen/emit_dfa.c", None, r"DELEG_OFS|DELEG_MLINE|DELEG_COVER"),
    ("X10", "PRESENCE / FIRST handoff (DELEG_PRE, DELEG_PF)", "src/gen/emit_dfa.c", None, r"DELEG_PRE|DELEG_PF"),
    ("X11", "LOCATE-RECOVER-FINISH (rev-end/reverse-pass/pinned/end-minus-width)", "src/gen/emit_dfa.c", None, r"reverse-pass|end-minus-width"),
    ("X12", "landmark walk emit_landmark_walk (p1build: NOT on main at this commit)", "src/gen/emit_dfa.c", None, r"emit_landmark_walk"),
    ("X13", "compound controller", "src/gen/emit_compound.c", None, r"."),
    ("X13b", "compound analysis", "src/core/compound.c", None, r"."),
    ("X14", "kit site kind keyed by engine (MF_SK_*)", "src/gen/memfn_sites.c", None, r"MF_SK_"),
]


def m0(root, out):
    rows = []
    for sid, desc, f, rng, rx in M0_SITES:
        path = os.path.join(root, f)
        try:
            lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
        except OSError:
            rows.append((sid, desc, f, rng and "%d-%d" % rng or "", "MISSING-FILE", ""))
            continue
        hits = [i + 1 for i, l in enumerate(lines) if re.search(rx, l)]
        if rng:
            ok = rng[1] <= len(lines) and any(rng[0] <= h <= rng[1] for h in hits)
            note = "cited %d-%d: %s" % (rng[0], rng[1], "CONFIRMED" if ok else "MOVED/GONE")
        else:
            ok = bool(hits)
            note = "no cited line; symbol %s" % ("present" if ok else "ABSENT")
        rows.append((sid, desc, f, "%d hits" % len(hits),
                     "ok" if ok else "FAIL", note + "; first at " + (str(hits[0]) if hits else "-")))
    with open(os.path.join(out, "m0_sites.tsv"), "w") as fh:
        fh.write("id\tdescription\tfile\thits\tverdict\tnote\n")
        for r in rows:
            fh.write("\t".join(map(str, r)) + "\n")
    # kind x host: DELEG_<site> occurrences by file; MF_SK_<kind> by file
    deleg = re.findall(r"DELEG_SITE\((\w+),", open(os.path.join(root, "src/gen/memfn_sites.def")).read())
    cells = collections.OrderedDict()
    srcs = []
    for dp, dn, fn in os.walk(os.path.join(root, "src")):
        for f in fn:
            if f.endswith((".c", ".h", ".def", ".inc")):
                srcs.append(os.path.join(dp, f))
    texts = {p: open(p, encoding="utf-8", errors="replace").read() for p in srcs}
    names = ["DELEG_" + d for d in deleg] + sorted({m for t in texts.values() for m in re.findall(r"\bMF_SK_[A-Z_]+", t)})
    for nme in names:
        for p, t in texts.items():
            c = len(re.findall(r"\b%s\b" % nme, t))
            if c:
                cells[(nme, os.path.relpath(p, root))] = c
    with open(os.path.join(out, "m0_kind_host.tsv"), "w") as fh:
        fh.write("kind_or_site\thost_file\tmentions\n")
        for (n_, h), c in cells.items():
            fh.write("%s\t%s\t%d\n" % (n_, h, c))
    hosts = collections.defaultdict(set)
    for (n_, h) in cells:
        hosts[n_].add(os.path.basename(h))
    return rows, deleg, hosts


# ------------------------------------------------------------------- main ---
def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--root", default=os.path.abspath(os.path.join(here, "..", "..", "..", "..")))
    ap.add_argument("--bench", default="/home/pcrec/projects/pcrec-bench")
    ap.add_argument("--out", required=True)
    ap.add_argument("--smoke", action="store_true", help="plants only (<=20 compiles)")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    pcrec = os.path.join(a.root, "build", "pcrec")
    if not os.access(pcrec, os.X_OK):
        print("scensus: RED no build/pcrec at", pcrec)
        return 2

    ents = [{"pat": p, "i": False, "enc": "", "pop": "plant", "src": "plant", "exp": ex}
            for p, ex in PLANTS]
    if not a.smoke:
        corp = load_corpora(a.root, a.bench, pcrec)
        if a.limit:
            corp = corp[:a.limit]
        ents += corp
    m0rows, deleg, hosts = m0(a.root, a.out)

    results = []
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for r in ex.map(work, [(pcrec, e) for e in ents]):
            results.append(r)

    red = []
    for sid, desc, f, hits, v, note in m0rows:
        if v != "ok" and sid != "X12":
            red.append("M0 %s %s" % (sid, note))
    # plants: same code path as the corpus
    for e, rec, st, cl, prox, mo in results:
        if e["pop"] != "plant":
            continue
        for k, want in e["exp"].items():
            if cl.get(k) != want:
                red.append("PLANT %r: %s want %r got %r (%s)" % (e["pat"], k, want, cl.get(k), rec["forced"]))
    pops = ("corpus", "bench")
    tally = {p: collections.Counter() for p in pops}
    unparsed = collections.Counter()
    okn = collections.Counter()
    total = collections.Counter()
    for e, rec, st, cl, prox, mo in results:
        if e["pop"] not in pops:
            continue
        total[e["pop"]] += 1
        if rec["status"] == "ok":
            okn[e["pop"]] += 1
        if st is None and rec["status"] == "ok":
            unparsed[e["pop"]] += 1
        if rec["status"] != "ok":
            tally[e["pop"]]["status:" + rec["status"]] += 1
            continue
        t = tally[e["pop"]]
        t["engine:" + rec["engine"]] += 1
        for k in ("m1", "m2", "m3", "m4", "m5a", "m5b", "m6"):
            if k in cl:
                t[k + ":" + cl[k]] += 1
        if cl.get("m2_prune"):
            t["m2prune:" + cl["m2_prune"]] += 1
        if prox:
            t["m1proxy:" + prox] += 1
        if st is not None and cl.get("engine") == "vm":
            t["m5a_vm:" + cl["m5a"]] += 1
            t["m5b_vm:" + cl["m5b"]] += 1
            t["m4_vm:" + cl["m4"]] += 1
    # parse-control: parser vs the compiler's own forced-by text
    ctl = collections.Counter()
    for e, rec, st, cl, prox, mo in results:
        if rec["status"] == "ok" and rec["engine"] == "vm" and st is not None:
            fb = rec["forced"]
            if fb.startswith("capture group"):
                ctl["forced-capture: tree has cap=%s" % (st["caps"] > 0)] += 1
            elif fb.startswith("(?C"):
                ctl["forced-callout: tree has callout=%s" % ("callout" in st["irreg"])] += 1
            elif "backreference" in fb:
                ctl["forced-backref: tree has backref=%s" % ("backref" in st["irreg"])] += 1
    for p in pops:
        n = total[p]
        if okn[p] and unparsed[p] * 20 > okn[p]:
            red.append("%s: %d of %d compiled patterns unparsed by the scanner (>5%%)" % (p, unparsed[p], okn[p]))
        if not a.smoke and not a.limit and n < 100:
            red.append("%s population only %d patterns" % (p, n))
    for k, v in ctl.items():
        if k.endswith("False"):
            red.append("parse-control %s: %d" % (k, v))

    # TSVs, one per measurement
    def tsv(name, cols, pick):
        with open(os.path.join(a.out, name), "w") as fh:
            fh.write("\t".join(cols) + "\n")
            for e, rec, st, cl, prox, mo in results:
                row = pick(e, rec, st, cl, prox, mo)
                if row:
                    fh.write("\t".join(str(x).replace("\t", " ").replace("\n", "\\n") for x in row) + "\n")
    pat = lambda e: e["pat"][:200]
    tsv("m1_resume0.tsv", ["pop", "pattern", "src", "forced_by", "landmark_proxy", "req_landmark_maxoff", "admission(D161a17)"],
        lambda e, r, s, c, p, m: (e["pop"], pat(e), e["src"], r["forced"], p, m, "NOT-MEASURABLE-TODAY") if c.get("m1") == "vm-resume0" else None)
    tsv("m2_prefilter.tsv", ["pop", "pattern", "src", "prefilter_reason", "prune_ceiling"],
        lambda e, r, s, c, p, m: (e["pop"], pat(e), e["src"], c["m2"], r["prune"]) if "m2" in c else None)
    tsv("m3_seam.tsv", ["pop", "pattern", "src", "class", "forced_by", "irregular_nodes"],
        lambda e, r, s, c, p, m: (e["pop"], pat(e), e["src"], c["m3"], r["forced"], ",".join(s["irreg"]) if s else "") if "m3" in c else None)
    tsv("m4_cap_in_repeat.tsv", ["pop", "pattern", "src", "engine", "cap_in_repeat"],
        lambda e, r, s, c, p, m: (e["pop"], pat(e), e["src"], c["engine"], c["m4"]) if "m4" in c else None)
    tsv("m5_regular_after_irregular.tsv", ["pop", "pattern", "src", "engine", "regular_after_nested_irregular", "multi_irregular", "irregular_kinds"],
        lambda e, r, s, c, p, m: (e["pop"], pat(e), e["src"], c["engine"], c["m5a"], c["m5b"], ",".join(s["irreg"])) if "m5a" in c else None)
    tsv("m6_resume_regular.tsv", ["pop", "pattern", "src", "resume_points", "rungs", "class"],
        lambda e, r, s, c, p, m: (e["pop"], pat(e), e["src"], r["resume"], r["rungs"], c["m6"]) if c.get("m6", "none") != "none" else None)

    def examples(pop, key, val, n=3):
        ex_ = [e["pat"][:70] for e, rec, st, cl, p, m in results
               if e["pop"] == pop and cl.get(key) == val]
        return "; ".join(ex_[:n])

    L = []
    L.append("scensus census: corpus %d patterns, bench %d patterns (deduplicated within population); plants %d"
             % (total["corpus"], total["bench"], len(PLANTS)))
    L.append("compiled ok: corpus %d, bench %d; of those unparsed by the structure scanner: corpus %d, bench %d (refused patterns are counted under engine/status)" % (okn["corpus"], okn["bench"], unparsed["corpus"], unparsed["bench"]))
    L.append("")
    L.append("M0 glue sites (src/ grep): %d rows, %s" % (len(m0rows),
             "all confirmed" if not [r for r in m0rows if r[4] != "ok"] else
             "NOT confirmed: " + ",".join(r[0] for r in m0rows if r[4] != "ok")))
    L.append("   DELEG sites %d; MF_SK kinds / DELEG sites by number of distinct host files: %s"
             % (len(deleg), ", ".join("%s=%d" % (k, len(v)) for k, v in sorted(hosts.items()))))
    for p in pops:
        L.append("")
        L.append("== population: %s (n=%d) ==" % (p, total[p]))
        t = tally[p]
        for pref, title in (("engine:", "engine"), ("status:", "not compiled"),
                            ("m1:", "M1 VM artifacts by resume-points"),
                            ("m1proxy:", "M1 capture-forced, resume-points 0: capture-erased landmark PROXY (admission split NOT MEASURABLE TODAY)"),
                            ("m2:", "M2 VM artifacts by prefilter reason"),
                            ("m2prune:", "M2 VM artifacts by prune-ceiling"),
                            ("m3:", "M3 VM artifacts by seam class"),
                            ("m4:", "M4 capture inside a repeat (all engines)"),
                            ("m4_vm:", "M4 capture inside a repeat (VM only)"),
                            ("m5a:", "M5a regular region after first nested irregular node (all)"),
                            ("m5a_vm:", "M5a (VM only)"),
                            ("m5b:", "M5b more than one VM-forcing construct (all)"),
                            ("m5b_vm:", "M5b (VM only)"),
                            ("m6:", "M6 VM artifacts: resume>0 regular apart from captures / frames-unbounded")):
            keys = sorted(k for k in t if k.startswith(pref))
            if not keys:
                continue
            L.append(title)
            for k in keys:
                key = k.split(":")[0]
                ex3 = examples(p, key, k.split(":", 1)[1]) if key in ("m1", "m2", "m3", "m4", "m5a", "m5b", "m6") else ""
                L.append("  %-60s %6d   e.g. %s" % (k.split(":", 1)[1], t[k], ex3))
    L.append("")
    L.append("parse-control (scanner tree vs the compiler's own `forced by` text): " +
             (", ".join("%s=%d" % kv for kv in sorted(ctl.items())) or "none"))
    L.append("")
    if red:
        L.append("scensus: RED")
        L += ["  " + r for r in red]
    else:
        L.append("scensus: COMPLETE plants=%d corpus=%d bench=%d vm_corpus=%d vm_bench=%d"
                 % (len(PLANTS), total["corpus"], total["bench"],
                    tally["corpus"]["engine:vm"], tally["bench"]["engine:vm"]))
    txt = "\n".join(L) + "\n"
    open(os.path.join(a.out, "summary.txt"), "w").write(txt)
    sys.stdout.write(txt)
    return 1 if red else 0


if __name__ == "__main__":
    sys.exit(main())
