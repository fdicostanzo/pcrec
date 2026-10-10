"""tests/spec_history/specdoc.py -- reads the numbering of a numbered spec doc.

A numbered spec document (docs/spec/CLAUDE.md, "Numbering") carries

  * section headings that start with their number (`## 3. T`, `### 3.1 T`),
    each preceded by a line `<a id="s3-1"></a>`;
  * paragraph labels `[3.1¶4]` at the start of every paragraph, list item and
    block quote (an `<a id="s3-1-p4"></a>` just before the label), numbered
    within the innermost section; `0` is the preamble above the first section;
  * a code block or table belongs to the paragraph it follows.

`parse(lines)` returns the document's structure; the checks in spec_cites.py
read it. The paragraph rule below is the one scripts a numbering pass and a
reviewer apply by eye: change it and the whole document's labels move.
Python 3 standard library only.
"""
import re

# a number: dotted components, each optionally lettered (an inserted section
# is 3.2a; its subsections 3.2a.1)
NUM = r"\d+[a-z]?(?:\.\d+[a-z]?)*"
PARA = r"\d+[a-z]?"
HEAD = re.compile(r"^(#{1,6})\s+(" + NUM + r")\.?\s+(.*?)\s*$")
ANCH_LINE = re.compile(r'^<a id="([^"]+)"></a>\s*$')
LABEL = re.compile(r'^(?P<lead>(?:[-*]|\d+[.)])\s+|>\s+)?<a id="(?P<aid>[^"]+)"></a>'
                   r"\[(?P<sec>" + NUM + r")¶(?P<k>" + PARA + r")\](?: |$)")
ITEM = re.compile(r"^([-*]|\d+[.)])\s")


TOC_BEGIN = "<!-- spec-toc:begin -->"
TOC_END = "<!-- spec-toc:end -->"


def anchor_of(num):
    return "s" + num.replace(".", "-")


def para_anchor_of(num, k):
    return "%s-p%s" % (anchor_of(num), k)


class Doc:
    """headings: [(lineno, level, number, title, prev_line_text)]
    units: [(lineno, section, label_match_or_None, first_line)]
    labels: {(section, k)} ; sections: {number}"""

    def __init__(self):
        self.headings = []
        self.units = []
        self.labels = set()
        self.sections = {"0"}


def parse(lines):
    d = Doc()
    sec = "0"
    fence = False
    after_fence = False
    prev_blank = True
    in_toc = False
    for i, l in enumerate(lines):
        n = i + 1
        if l.strip() == TOC_BEGIN:
            in_toc = True
            continue
        if l.strip() == TOC_END:
            in_toc = False
            prev_blank = False
            continue
        if in_toc:
            continue        # the generated contents list is not paragraphs
        if fence:
            if l.lstrip().startswith("```"):
                fence = False
                after_fence = True
            continue
        if not l.strip():
            prev_blank = True
            continue
        if ANCH_LINE.match(l):
            continue
        m = HEAD.match(l)
        if m and len(m.group(1)) >= 2:
            sec = m.group(2)
            d.sections.add(sec)
            d.headings.append((n, len(m.group(1)), sec, m.group(3),
                               lines[i - 1] if i else ""))
            after_fence = False
            prev_blank = False
            continue
        if l.startswith("#") and re.match(r"#{1,6}\s", l):
            prev_blank = False       # the title, or an unnumbered heading
            continue
        if l.startswith("```"):
            fence = True
            continue
        if l.startswith("---") and not l.strip("-"):
            prev_blank = False
            continue
        if l.startswith("<!--") or l.startswith("|"):
            prev_blank = False
            continue
        start = False
        if prev_blank and not l.startswith(" "):
            start = True
        elif ITEM.match(l):
            start = True
        if after_fence and l[0].islower():
            start = False
        after_fence = False
        prev_blank = False
        if start:
            lm = LABEL.match(l)
            d.units.append((n, sec, lm, l))
            if lm:
                d.labels.add((lm.group("sec"), lm.group("k")))
    return d
