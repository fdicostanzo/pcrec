#!/usr/bin/env python3
"""clsmask_candidates: the PER-SITE CLASS-TEST instrument (source rewrite).

    instrument.py IN.c OUTDIR

Reads one pcrec-emitted artifact and writes, in OUTDIR:
  inst.c    the artifact with every VM BYTE TEST wrapped so that each
            evaluation calls rxcs_hit(site, position) (cs_drv.c defines it),
            plus an attempt counter at rx_match_anchored's entry and a
            backtrack counter at its rx_fail label;
  ev.c      the UNMODIFIED artifact plus an evaluator main() that prints,
            for every byte-domain site, the 256-bit set of bytes its own
            predicate accepts (the predicate's emitted text with the subject
            read replaced by the byte -- the compiler's own tables and
            helpers decide membership, nothing is re-derived from the
            pattern), and for every utf8 code-point class site its size
            over U+0000..U+10FFFF and its ASCII bitmap;
  sites.tsv one row per site: site kind form label line_text.

WHAT IS A SITE: one occurrence, inside rx_match_anchored (the VM program)
or rx_search_run (the attempt loop), of one of these emitted predicate forms
over a single subject byte (the forms were enumerated from every VM
artifact of the population, see the memo §2):
  bitmap  ((rx_class_bitmapK[(subject[E]) >> 3] >> ((subject[E]) & 7)) & 1)
  fold    ((subject[E] | 0xNN) == V)
  range   ((unsigned)(subject[E] - L) <= Wu)
  atom    rx_class_atomK(subject[E])
  start   rx_start_set[subject[E]]          (the attempt loop's start skip)
  le      subject[E] <= V
  eq      subject[E] == V                    (a literal byte)
  switch  switch (subject[E]) { case ... }   (byte dispatch; set = its cases)
  ucls    rx_wclsK(cp_) after rx_decode       (a utf8 code-point class)
Literal-run word compares (rx_wN / memcmp) and backreference compares
(rx_span_match*) are NOT sites; they are counted statically (`litrun`,
`bref`). Any `subject[` left unwrapped inside the two functions is reported
as `unwrapped` (the audit; the memo states the count).

SITE KIND (the context, from the emitted line):
  run_c   a counted/bounded span-loop `while` (`it_ <` bound)
  run_u   an unbounded span-loop `while`
  start   the attempt loop's start-set skip
  behind  a read left of the position (E ends in `- N` / `-N`, rv cursors)
  step    a consuming single test (`{ scan_position++` / `+= len_`)
  cstep   a cursor-rung iteration test (`if (!(rx_span_cursor ...)) goto rx_fail`)
  peek    any other test (lookahead, guards, \\b's right half, dispatch)
`label` is the nearest preceding rx_LN label: the IR listing's rungs/
strategies rows are keyed on it (the possessify join).
"""
import os, re, sys

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
text = open(src, errors="replace").read()
lines = text.split("\n")

E = r"([^\]\[]+)"
ATOM = re.compile(
    r"(?P<bitmap>\(\(rx_class_bitmap(?P<bk>\d+)\[\(subject\[" + E + r"\]\) >> 3\] >> \(\(subject\[[^\]\[]+\]\) & 7\)\) & 1\))"
    r"|(?P<fold>\(subject\[" + E + r"\] \| 0x[0-9a-fA-F]+\) == \d+)"
    r"|(?P<range>\(unsigned\)\(subject\[" + E + r"\] - \d+\) <= \d+u)"
    r"|(?P<atom>rx_class_atom\d+\(subject\[" + E + r"\]\))"
    r"|(?P<start>rx_start_set\[subject\[" + E + r"\]\])"
    r"|(?P<le>subject\[" + E + r"\] <= \d+)"
    r"|(?P<eq>subject\[" + E + r"\] == (?:\d+|'(?:\\.|[^'])'))"
    r"|(?P<switch>switch \(subject\[" + E + r"\]\))")
SUBJ = re.compile(r"subject\[([^\]\[]+)\]")
# FAILING-DIRECTION CONTROL (validate.py): CS_SABOTAGE=drop-range stops the
# instrument from recognising the `range` form, so those reads go uncounted;
# the independent cross-check must then go red.
if os.environ.get("CS_SABOTAGE") == "drop-range":
    ATOM = re.compile(ATOM.pattern.replace(r"(?P<range>\(unsigned\)", r"(?P<range>\(NEVER\)"))


def fn_ranges():
    rs = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if re.match(r"^static .*\b(rx_match_anchored|rx_search_run)\(", ln) and not ln.rstrip().endswith(";"):
            j = i
            while j < len(lines) and lines[j] != "}":
                j += 1
            rs.append((i, j, re.search(r"(rx_match_anchored|rx_search_run)", ln).group(1)))
            i = j
        i += 1
    return rs


def kind_of(ln, form, expr):
    s = ln.strip()
    if form == "start":
        return "start"
    if re.search(r"(-\s*\d+\s*$)|rx_rv\d+_cursor", expr):
        return "behind"
    if s.startswith("while (") and "rx_span_cursor" in s:
        return "run_c" if "it_ <" in s else "run_u"
    if "scan_position++" in s or "+= len_" in s:
        return "step"
    if s.startswith("if (!(rx_span_cursor"):
        return "cstep"
    return "peek"


sites = []        # (site, kind, form, label, fn, pred_text, line)
counts = dict(litrun=0, bref=0, unwrapped=0)
new = list(lines)
for a, b, fn in fn_ranges():
    label = ""
    for i in range(a, b + 1):
        ln = lines[i]
        m = re.match(r"^(rx_L\d+):", ln)
        if m:
            label = m.group(1)
        if fn == "rx_match_anchored":
            counts["litrun"] += len(re.findall(r"rx_w\d\(subject|memcmp\(subject", ln))
            counts["bref"] += len(re.findall(r"rx_span_match(?:_caseless)?\(subject", ln))

        def rep(m):
            form = m.lastgroup if m.lastgroup != "bk" else "bitmap"
            for g in ("bitmap", "fold", "range", "atom", "start", "le", "eq", "switch"):
                if m.group(g):
                    form = g
                    break
            whole = m.group(form)
            sm = SUBJ.search(whole)
            expr = sm.group(1)
            k = len(sites)
            kind = kind_of(ln, form, expr)
            pred = whole
            if form == "switch":
                cases = []
                for j in range(i + 1, min(b, i + 400)):
                    cm = re.match(r"^\s*case (\d+):", lines[j])
                    if cm:
                        cases.append(int(cm.group(1)))
                    elif lines[j].strip() == "}":
                        break
                pred = "(" + " || ".join("subject[%s] == %d" % (expr, c) for c in cases) + ")" if cases else "0"
            sites.append((k, kind, form, label, fn, pred, ln.strip()))
            return whole[:sm.start()] + "RXCS(%d, %s)" % (k, expr) + whole[sm.end():]

        nl = ATOM.sub(rep, ln) if fn == "rx_match_anchored" else re.sub(
            r"rx_start_set\[subject\[([^\]\[]+)\]\]", lambda m: rep(ATOM.search(m.group(0))), ln)
        # utf8 code-point class: rx_wclsK(cp_) after an rx_decode at scan_position
        if fn == "rx_match_anchored":
            def urep(m):
                k = len(sites)
                sites.append((k, kind_of(ln, "ucls", "scan_position"), "ucls", label, fn, m.group(0), ln.strip()))
                return "(rxcs_hit(%d, (size_t)scan_position), %s)" % (k, m.group(0))
            nl = re.sub(r"rx_wcls\d+\(cp_\)", urep, nl)
            # the bitmap form's second read and switch-less reads are accounted
            counts["unwrapped"] += len(SUBJ.findall(nl)) - len(re.findall(r"rx_class_bitmap\d+\[\(RXCS", nl))
            m2 = re.match(r"^(rx_fail): __attribute__\(\(unused\)\);$", ln)
            if m2:
                nl = ln + " rxcs_fails++;"
        new[i] = nl
    # the attempt counter: first statement of rx_match_anchored's body
    if fn == "rx_match_anchored":
        k = a
        while not lines[k].rstrip().endswith("{"):
            k += 1
        new[k] = new[k] + " rxcs_attempts++;"

pre = ("#include <stddef.h>\nextern void rxcs_hit(int site, size_t pos);\n"
       "extern unsigned long long rxcs_attempts, rxcs_fails;\n"
       "#define RXCS(k, e) (rxcs_hit((k), (size_t)(e)), subject[e])\n")
open(os.path.join(out, "inst.c"), "w").write(pre + "\n".join(new))

ev = [text, "\n#include <stdio.h>\n#include <stdint.h>"]
# the attempt loop's start table is function-local: lift the emitted text
sm = re.search(r"static const unsigned char rx_start_set\[256\] = \{[^}]*\};", text)
if sm:
    ev.append(sm.group(0).replace("rx_start_set", "rxcs_start_set"))
for k, kind, form, label, fn, pred, ln in sites:
    if form == "ucls":
        ev.append("static int rxcs_ev_%d(unsigned cp_) { return %s; }" % (k, pred))
    else:
        p = SUBJ.sub("rxcs_c", pred).replace("rx_start_set", "rxcs_start_set")
        ev.append("static int rxcs_ev_%d(unsigned char rxcs_c) { return (%s) != 0; }" % (k, p))
ev.append("int main(void) {")
for k, kind, form, label, fn, pred, ln in sites:
    if form == "ucls":
        ev.append('  { unsigned long n = 0; unsigned char bm[32] = {0}; for (unsigned cp = 0; cp < 0x110000u; cp++) '
                  'if (rxcs_ev_%d(cp)) { n++; if (cp < 256) bm[cp >> 3] |= (unsigned char)(1u << (cp & 7)); } '
                  'printf("%d\\t%%lu\\t", n); for (int i = 0; i < 32; i++) printf("%%02x", bm[i]); printf("\\n"); }' % (k, k))
    else:
        ev.append('  { unsigned n = 0; unsigned char bm[32] = {0}; for (unsigned c = 0; c < 256; c++) '
                  'if (rxcs_ev_%d((unsigned char)c)) { n++; bm[c >> 3] |= (unsigned char)(1u << (c & 7)); } '
                  'printf("%d\\t%%u\\t", n); for (int i = 0; i < 32; i++) printf("%%02x", bm[i]); printf("\\n"); }' % (k, k))
ev.append("  return 0; }")
open(os.path.join(out, "ev.c"), "w").write("\n".join(ev) + "\n")

with open(os.path.join(out, "sites.tsv"), "w") as f:
    f.write("#litrun=%d bref=%d unwrapped=%d\n" % (counts["litrun"], counts["bref"], counts["unwrapped"]))
    f.write("site\tkind\tform\tlabel\tfn\tline\n")
    for k, kind, form, label, fn, pred, ln in sites:
        f.write("%d\t%s\t%s\t%s\t%s\t%s\n" % (k, kind, form, label, fn, ln.replace("\t", " ")[:300]))
