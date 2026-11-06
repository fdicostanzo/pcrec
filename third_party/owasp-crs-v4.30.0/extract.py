#!/usr/bin/env python3
"""Extract every regex from the OWASP CRS rule files into patterns.tsv.

usage: python3 -I extract.py CRS_DIR [--out DIR] [--bench-dir DIR]

CRS_DIR is a checkout of coreruleset/coreruleset at the pinned tag (see
PROVENANCE.md).  It is read as TEXT ONLY: nothing in it is executed.

NOT a gen-tables generator, on purpose: the Makefile's `gen-tables` runs every
third_party/*/generate.py, and this script needs the downloaded source, which
is not in the tree.  It is named extract.py so gen-tables never picks it up;
patterns.tsv is the committed data, this script is its recipe.

Output (deterministic, rule files in sorted order):
  patterns.tsv   one row per regex (see COLUMNS)
  summary.txt    counts (operators, data files, .ra files, validation)
With --bench-dir (a pcrec-bench bench/capability/patterns dir, read-only) the
overlap with the bench's wild patterns is printed to stdout.
"""
import ctypes
import os
import re
import sys

COLUMNS = ["id", "file", "line", "rule_id", "chain_pos", "operator", "negated",
           "phase", "paranoia", "transforms", "flags", "pattern",
           "libpcre2_ok", "dup_of"]


def logical_lines(path):
    """Apache-style lines: a trailing backslash joins the next physical line
    (backslash and newline dropped, the next line's leading blanks dropped).
    Yields (first physical line number, text)."""
    with open(path, "rb") as f:
        phys = f.read().decode("utf-8", "surrogateescape").split("\n")
    i = 0
    while i < len(phys):
        start = i + 1
        text = phys[i].rstrip("\r")
        while text.endswith("\\") and i + 1 < len(phys):
            i += 1
            text = text[:-1] + phys[i].rstrip("\r").lstrip(" \t")
        i += 1
        yield start, text


def word(s, pos):
    """Read one config word from s at pos.  Quoted words end at an unescaped
    double quote; a backslash-quote yields a quote, every other backslash pair
    is kept verbatim.  Returns (word, newpos) or (None, pos)."""
    n = len(s)
    while pos < n and s[pos] in " \t":
        pos += 1
    if pos >= n:
        return None, pos
    if s[pos] != '"':
        e = pos
        while e < n and s[e] not in " \t":
            e += 1
        return s[pos:e], e
    out = []
    pos += 1
    while pos < n:
        c = s[pos]
        if c == "\\" and pos + 1 < n:
            if s[pos + 1] == '"':
                out.append('"')
            else:
                out.append(s[pos:pos + 2])
            pos += 2
        elif c == '"':
            return "".join(out), pos + 1
        else:
            out.append(c)
            pos += 1
    return "".join(out), pos  # unterminated: keep what there is


def split_actions(a):
    parts, cur, q = [], [], False
    for c in a:
        if c == "'":
            q = not q
        if c == "," and not q:
            parts.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
    parts.append("".join(cur).strip())
    return [p for p in parts if p]


SEL = re.compile(r"([A-Za-z_]+):/")


def selectors(varfield):
    """Regex selectors in a variable list, e.g. TX:/^foo_/ (XML: is XPath)."""
    out = []
    for m in SEL.finditer(varfield):
        if m.group(1) == "XML":
            continue
        rest = varfield[m.end():]
        e = re.search(r"/(?=\||$)", rest)
        if e:
            out.append((m.group(1), rest[:e.start()]))
    return out


class Pcre2:
    def __init__(self):
        self.lib = ctypes.CDLL("libpcre2-8.so.0")
        self.lib.pcre2_compile_8.restype = ctypes.c_void_p
        self.lib.pcre2_compile_8.argtypes = [
            ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_void_p]
        self.lib.pcre2_code_free_8.argtypes = [ctypes.c_void_p]
        buf = ctypes.create_string_buffer(64)
        self.lib.pcre2_config_8(11, buf)  # PCRE2_CONFIG_VERSION
        self.version = buf.value.decode()

    def ok(self, pat):
        err = ctypes.c_int()
        off = ctypes.c_size_t()
        code = self.lib.pcre2_compile_8(pat, len(pat), 0, ctypes.byref(err),
                                        ctypes.byref(off), None)
        if code:
            self.lib.pcre2_code_free_8(code)
            return True
        return False


def main(argv):
    args = argv[1:]
    out = os.path.dirname(os.path.abspath(__file__))
    bench = None
    crs = None
    while args:
        a = args.pop(0)
        if a == "--out":
            out = args.pop(0)
        elif a == "--bench-dir":
            bench = args.pop(0)
        else:
            crs = a
    if not crs:
        sys.exit(__doc__)
    rules = os.path.join(crs, "rules")
    pc = Pcre2()
    rows = []
    opcount = {}
    skipped_update = 0
    for fn in sorted(os.listdir(rules)):
        if not fn.endswith(".conf"):
            continue
        head = {"id": "", "para": "", "phase": "", "pos": 0}
        chain_pending = False
        for ln, text in logical_lines(os.path.join(rules, fn)):
            t = text.strip()
            if t.startswith("SecRuleUpdate") or t.startswith("SecRuleRemove"):
                skipped_update += 1
                continue
            if not re.match(r"SecRule\s", t):
                continue
            pos = len("SecRule")
            var, pos = word(t, pos)
            opw, pos = word(t, pos)
            act, pos = word(t, pos)
            if var is None or opw is None:
                continue
            acts = split_actions(act or "")
            kv = {}
            trans = []
            para = ""
            chain = False
            for a in acts:
                if a == "chain":
                    chain = True
                k, _, v = a.partition(":")
                if k == "id":
                    kv["id"] = v
                elif k == "phase":
                    kv["phase"] = v
                elif k == "t":
                    trans.append(v)
                elif k == "tag" and v.strip("'").startswith("paranoia-level/"):
                    para = v.strip("'").split("/")[1]
            if "id" in kv:
                head = {"id": kv["id"], "para": para,
                        "phase": kv.get("phase", ""), "pos": 0}
            elif chain_pending:
                head["pos"] += 1
            else:
                head = {"id": "", "para": "", "phase": "", "pos": 0}
            chain_pending = chain
            neg = opw.startswith("!")
            body = opw[1:] if neg else opw
            if body.startswith("@"):
                m = re.match(r"(@\w+)\s*", body)
                opname, arg = m.group(1), body[m.end():]
            else:
                opname, arg = "@rx(implicit)", body
            opcount[opname] = opcount.get(opname, 0) + 1
            common = (fn, str(ln), head["id"], str(head["pos"]))
            tail = (head["phase"], head["para"], "+".join(trans))
            if opname.startswith("@rx"):
                rows.append((common, opname, neg, tail, arg))
            for name, sel in selectors(var):
                rows.append((common, "var-selector:" + name, False, tail, sel))

    seen = {}
    lines = []
    nbad = 0
    for i, (common, opname, neg, tail, pat) in enumerate(rows, 1):
        rid = "crs%04d" % i
        if any(c in pat for c in "\t\n\r"):
            sys.exit("pattern with tab/newline at %s:%s" % common[:2])
        pb = pat.encode("utf-8", "surrogateescape")
        ok = pc.ok(pb)
        nbad += (not ok)
        dup = seen.setdefault(pat, rid)
        lines.append("\t".join((rid,) + common + (opname, "1" if neg else "0")
                               + tail + ("s", pat, "1" if ok else "0",
                                         "" if dup == rid else dup)))
    with open(os.path.join(out, "patterns.tsv"), "w", encoding="utf-8",
              errors="surrogateescape", newline="\n") as f:
        f.write("\t".join(COLUMNS) + "\n")
        f.write("\n".join(lines) + "\n")

    ndata = sum(1 for x in os.listdir(rules) if x.endswith(".data"))
    datalines = 0
    for x in sorted(os.listdir(rules)):
        if x.endswith(".data"):
            with open(os.path.join(rules, x), "rb") as f:
                datalines += sum(1 for l in f if l.strip() and not l.startswith(b"#"))
    ra = os.path.join(crs, "regex-assembly")
    nra = sum(1 for x in os.listdir(ra) if x.endswith(".ra")) if os.path.isdir(ra) else 0
    uniq = len(seen)
    summ = ["libpcre2 %s" % pc.version,
            "rows %d  unique-pattern-text %d  libpcre2-rejected %d" % (len(rows), uniq, nbad),
            "operators (every SecRule): " + ", ".join(
                "%s=%d" % kv for kv in sorted(opcount.items())),
            "var-selector rows %d" % sum(1 for r in rows if r[1].startswith("var-selector")),
            "skipped SecRuleUpdate*/Remove* lines %d" % skipped_update,
            "data files %d (non-comment lines %d); regex-assembly .ra files %d"
            % (ndata, datalines, nra)]
    with open(os.path.join(out, "summary.txt"), "w") as f:
        f.write("\n".join(summ) + "\n")
    print("\n".join(summ))

    if bench:
        bset = {}
        for x in sorted(os.listdir(bench)):
            if x.endswith(".rx"):
                with open(os.path.join(bench, x), "rb") as f:
                    bset[x] = f.read().decode("utf-8", "surrogateescape").rstrip("\n")
        by = {}
        for (common, opname, neg, tail, pat) in rows:
            by.setdefault(pat, []).append(common[2] or common[0])
        for x, p in bset.items():
            if x.startswith("wild-") and p in by:
                print("bench overlap: %s == CRS %s" % (x, ",".join(by[p])))


if __name__ == "__main__":
    main(sys.argv)
