#!/usr/bin/env python3
"""lens10kit A3 -- the sabotage-anchor census, by ANCHOR not by row.

A row may carry TWO anchors (SAB_FILE/SAB_BEFORE and SAB_FILE2/SAB_BEFORE2;
16 rows do).  Each anchor is a verbatim source-text block that must match its
file byte for byte, so each is independently re-aim-able and must be counted
independently.

For each anchor targeting a wave-1 file, classify what it quotes:
  TEXTCALL  - the block contains an sb_puts/sb_printf/sb_putc call
  SNPRINTF  - the block contains an snprintf call
  BUFDECL   - the block declares a `char NAME[...]` scratch buffer
  OTHER     - quotes non-text code (survives a text-only migration, but must
              be RE-VERIFIED if a changed line abuts it)
"""
import re, sys, glob, collections, os

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
TARGETS = {"src/gen/emit_vm.c", "src/gen/emit_dfa.c", "src/parse/syntax_dump.c",
           "src/parse/rxt_source.c", "src/parse/axes_dump.c",
           "src/parse/limits_dump.c", "src/parse/schema_dump.c",
           "cli/main.c", "src/gen/enc/enc.c", "src/core/sb.c",
           "src/parse/enabled.c"}

VAR = re.compile(r"^(SAB_[A-Z_0-9]+)=", re.M)


def fields(text):
    """Split a sabotage file into SAB_* assignments (value = text up to the
    next top-level SAB_ assignment)."""
    marks = [(m.group(1), m.start(), m.end()) for m in VAR.finditer(text)]
    out = {}
    for i, (name, s, e) in enumerate(marks):
        end = marks[i + 1][1] if i + 1 < len(marks) else len(text)
        out[name] = text[e:end]
    return out


def classify(block):
    tags = []
    if re.search(r"\bsb_(printf|puts|putc)\s*\(", block):
        tags.append("TEXTCALL")
    if re.search(r"\bsnprintf\s*\(", block):
        tags.append("SNPRINTF")
    if re.search(r"\bchar\s+\w+\s*\[", block):
        tags.append("BUFDECL")
    return tags or ["OTHER"]


def main():
    per_file = collections.Counter()
    per_file_tag = collections.defaultdict(collections.Counter)
    rows = 0
    anchors = 0
    detail = collections.defaultdict(list)
    for path in sorted(glob.glob(os.path.join(ROOT, "tests/mech/sabotages/*.sh"))):
        t = open(path, encoding="utf-8", errors="replace").read()
        f = fields(t)
        rows += 1
        for fk, bk in (("SAB_FILE", "SAB_BEFORE"), ("SAB_FILE2", "SAB_BEFORE2")):
            if fk not in f or bk not in f:
                continue
            fname = f[fk].strip().strip("'\"")
            block = f[bk]
            anchors += 1
            per_file[fname] += 1
            for tag in classify(block):
                per_file_tag[fname][tag] += 1
                if fname in TARGETS and tag != "OTHER":
                    detail[(fname, tag)].append(os.path.basename(path))
    print("sabotage ROWS: %d    ANCHORS (incl. SAB_*2): %d\n" % (rows, anchors))
    print("%-28s %7s  %s" % ("SAB_FILE", "anchors", "tags"))
    for fname, n in per_file.most_common():
        if fname not in TARGETS and n < 3:
            continue
        tags = ", ".join("%s=%d" % kv for kv in
                         sorted(per_file_tag[fname].items()))
        star = " *" if fname in TARGETS else "  "
        print("%-28s %7d%s %s" % (fname, n, star, tags))
    print("\n(* = a file a kit migration would touch)")
    print("\n--- anchors quoting TEXT-PRODUCING code in wave-1 files ---")
    for (fname, tag), lst in sorted(detail.items()):
        print("%-24s %-9s %d:" % (fname, tag, len(lst)))
        for b in sorted(lst):
            print("        %s" % b)


if __name__ == "__main__":
    main()
