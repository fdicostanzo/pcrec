#!/usr/bin/env python3
"""tests/startset/edge_import.py -- writes a START-SET edge-cell HOME under
tests/startset/ from lane ssedge's DRAFT (docs/design/startset.md §6.4.4).

The cells' generator stays where ssedge put it: docs/design/startset/edge/
cells.py (the authored half: pattern, options, subjects, why) and gen_rxt.py
(every answer is libpcre2's, 10.48 and the 10.46 reference agreeing on every
cell). This script is the last link only: it copies a draft verbatim, block
for block, and adds the one line every block needs in the corpus and the
draft omits -- `features all`, which ssedge's mutation harness passed on the
command line -- after each `pattern` line, drops the file-level `oracle` head
line (verify_rxt.py reads no head), and replaces the draft's header.
No case line is touched, so an answer here is the draft's answer.

    edge_import.py DRAFT HOME STAGE     (e.g. .../edge/vmhat.rxt vmhat.rxt 2)

Re-run after `gen_rxt.py write` regenerates a draft.
"""
import os, sys

src, dst, stage = sys.argv[1], sys.argv[2], sys.argv[3]
lines = open(src, encoding="utf-8").read().split("\n")
body = []
seen_body = False
for ln in lines:
    if not seen_body:
        if ln.startswith("#") or not ln.strip():
            continue          # the draft's own header, replaced below
        seen_body = True
    if ln.startswith("oracle "):
        # a HEAD declaration: verify_rxt.py (the C3 python tier) cannot read
        # a head-bearing file, and every block the oracle line covered
        # already carries `# pcre2-only` where python cannot answer it
        continue
    if ln.startswith("tag "):
        # `tag` is a W1 candidate keyword the rxtsource keyword census
        # guards (a headless corpus line may not begin with it); kept as a
        # comment so the line numbers run_axes.sh's GROUP F5 keys name hold
        ln = "# " + ln
    body.append(ln)
    if ln.startswith("pattern ") or ln.startswith("pattern-esc "):
        body.append("features all")
name = os.path.basename(dst)
head = [
    "# tests/startset/%s -- [START-SET] edge cells for stage %s (D148 addendum 1;" % (name, stage),
    "# docs/design/startset.md §6.4, homes in §6.4.4). Every answer is libpcre2's",
    "# (local 10.48, agreeing with the 10.46 reference on every cell), at EVERY",
    "# startpos that is a character boundary of its subject.",
    "#",
    "# GENERATED, do not edit by hand: docs/design/startset/edge/cells.py (the",
    "# authored half) -> gen_rxt.py (the oracle's answers) -> the draft",
    "# docs/design/startset/edge/%s -> tests/startset/edge_import.py (adds" % os.path.basename(src),
    "# `features all` to each block, drops the head `oracle` line). Each block carries `# tag edge=<key>`; the",
    "# key's meaning is startset.md §6.4.1's table.",
    "",
]
open(dst, "w", encoding="utf-8").write("\n".join(head + body).rstrip("\n") + "\n")
print("wrote %s (%d lines)" % (dst, len(head) + len(body)))
