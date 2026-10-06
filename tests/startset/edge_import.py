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

    edge_import.py DRAFT[,DRAFT...] HOME STAGE     (e.g. .../edge/vmhat.rxt vmhat.rxt 2)

Several comma-separated drafts are concatenated into one home, in the order
given (stage 3's `dfahat.rxt` gathers six, startset.md §6.4.4). Re-run after
`gen_rxt.py write` regenerates a draft.
"""
import os, sys

srcs, dst, stage = sys.argv[1].split(","), sys.argv[2], sys.argv[3]
body = []
for src in srcs:
    if len(srcs) > 1:
        body += ["", "# ---- from the draft %s ----" % os.path.basename(src), ""]
    seen_body = False
    in_config = False
    for ln in open(src, encoding="utf-8").read().split("\n"):
        if in_config and ln.startswith((" ", "\t")):
            continue          # the dropped config's indented body
        in_config = False
        if ln.startswith("config ") or ln.startswith("target "):
            # HEAD declarations again (hybrid.rxt's `-fprefilter-collapse`
            # targets): a head makes the file unreadable to verify_rxt.py and
            # the harness builds no target, so they are dropped; the compiled
            # collapse is tests/startset/vmhat_diff.py's `collapse` config
            in_config = ln.startswith("config ")
            continue
        if not seen_body:
            if ln.startswith("#") or not ln.strip():
                continue          # the draft's own header, replaced below
            seen_body = True
        if ln.startswith("oracle "):
            # a HEAD declaration: verify_rxt.py (the C3 python tier) cannot read
            # a head-bearing file, and every block the oracle line covered
            # already carries `# pcre2-only` where python cannot answer it
            continue
        if ln.startswith("name "):
            # a dropped target's definition name (hybrid.rxt's); a `name` line
            # with no target to build is a W1 keyword collision (rxtsource's
            # keyword census), kept as a comment so line numbers hold
            ln = "# " + ln
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
    "# docs/design/startset/edge/%s -> tests/startset/edge_import.py (adds" % ",".join(os.path.basename(x) for x in srcs),
    "# `features all` to each block, drops the head `oracle` line). Each block carries `# tag edge=<key>`; the",
    "# key's meaning is startset.md §6.4.1's table.",
    "",
]
open(dst, "w", encoding="utf-8").write("\n".join(head + body).rstrip("\n") + "\n")
print("wrote %s (%d lines)" % (dst, len(head) + len(body)))
