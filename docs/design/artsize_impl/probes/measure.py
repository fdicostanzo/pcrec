#!/usr/bin/env python3
"""[ART-SIZE] STEP 2 lane artsize3 — corpus measurement for the size model.

For every distinct corpus pattern: emit the self-contained artifact once and
record (comment-excluded bytes, node-label count, table bytes, stamps).

Comment-excluded bytes uses tests/lib/size_count.sh's definition VERBATIM
(a flat three-state comment tracker; a line that OPENS a block comment or is
a `//` line is prose in full, including its newline).
"""
import argparse, glob, os, re, subprocess, sys, random, time

ROOT = "/home/duxevents/pcrec/worktrees/artsize3"
PCREC = ROOT + "/build/pcrec"

# [r40 F1] EVERY label form and EVERY table form. The first cut of this file
# matched only `rx_L<N>:` and only `static const <word-type>` arrays, which
# made the VM HYBRID PREFILTER'S COMPUTED-GOTO MACHINERY INVISIBLE: its
# `static const void *const rx_targets_N[11]` jump tables cannot be crossed by
# a `\w`-only type pattern, and its `rx_s<N>:` state labels are not `rx_L`.
# On K41's second witness that hid 3,108 tables and 3,108 labels and made the
# model read 118,240 B for a 1,214,333 B artifact. The classifier's own
# regexes were the population nobody counted.
#
# Anchored on the RIGHT-HAND side (`= {`) and on the emitter's own `rx_`
# prefix rather than on a type spelling, so a new table element type cannot
# silently drop out of the count again.
LABEL_RE = re.compile(r'^(rx_[A-Za-z]+)(\d*): ')
STAMP_RE = re.compile(r'^#define (RX_[A-Z0-9_]+) (.*)$')
TABLE_DECL_RE = re.compile(
    r'static const\s+.*?\b(rx_\w+)\s*((?:\[\d+\])+)\s*=\s*\{')
TABLE_OPEN_RE = TABLE_DECL_RE


def scan(text):
    """Return dict of measured quantities. One pass, size_count.sh's comment rule."""
    total = 0
    prose = 0
    tables = 0
    table_entries = 0      # entries in DATA tables (unsigned char/short/...)
    jump_entries = 0       # entries in POINTER tables (computed-goto targets)
    table_arrays = 0
    jump_arrays = 0
    labels = 0          # rx_L<N>: -- VM nodes
    slabels = 0         # rx_s<N>: -- hybrid-prefilter computed-goto states
    olabels = 0         # every other rx_*: label (rx_fail, rx_done, ...)
    gotos = 0
    addr_taken = set()
    stamps = {}
    in_comment = False
    in_table = 0          # brace depth inside a table literal, 0 = not in one
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()   # awk emits no final empty record for a trailing newline
    for line in lines:
        lb = len(line) + 1
        total += lb
        s = line.lstrip(" \t")
        if in_comment:
            prose += lb
            if "*/" in line:
                in_comment = False
            continue
        if s.startswith("/*"):
            prose += lb
            rest = line[line.index("/*") + 2:]
            if "*/" not in rest:
                in_comment = True
            continue
        if s.startswith("//"):
            prose += lb
            continue
        # non-prose line
        if in_table:
            tables += lb
            in_table += line.count("{") - line.count("}")
            if in_table <= 0:
                in_table = 0
            continue
        md = TABLE_DECL_RE.search(line)
        if md:
            tables += lb
            n = 1
            for dim in re.findall(r'\[(\d+)\]', md.group(2)):
                n *= int(dim)
            # A POINTER table (`static const void *const rx_targets_7[11]`) is
            # the hybrid prefilter's computed-goto jump table; a DATA table is
            # a transition/accept/class array. Different gcc cost per entry
            # (measured, note §2.6), so they are counted apart.
            if '*' in line[:line.index(md.group(1))]:
                jump_entries += n
                jump_arrays += 1
            else:
                table_entries += n
                table_arrays += 1
            d = line.count("{") - line.count("}")
            in_table = d if d > 0 else 0
            continue
        m = LABEL_RE.match(s)
        if m:
            fam = m.group(1)
            if fam == "rx_L":
                labels += 1
            elif fam == "rx_s":
                slabels += 1
            else:
                olabels += 1
        gotos += line.count("goto rx_L")
        for a in re.findall(r'&&rx_L(\d+)', line):
            addr_taken.add(a)
        m = STAMP_RE.match(line)
        if m:
            stamps[m.group(1)] = m.group(2).strip().strip('"')
    return dict(total=total, prose=prose, bytes=total - prose, tables=tables,
                table_entries=table_entries, table_arrays=table_arrays,
                jump_entries=jump_entries, jump_arrays=jump_arrays,
                labels=labels, slabels=slabels, olabels=olabels,
                gotos=gotos, addr_taken=len(addr_taken), stamps=stamps)


def emit(pattern, extra=(), timeout=120):
    cmd = [PCREC, "-p", "rx", "--features", "all"] + list(extra) + ["-o", "-", "--", pattern]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT", time.time() - t0
    if p.returncode != 0:
        err = p.stderr.decode("utf-8", "replace").strip().split("\n")
        return None, (err[0][:120] if err else "rc=%d" % p.returncode), time.time() - t0
    return p.stdout.decode("utf-8", "replace"), None, time.time() - t0


def corpus_patterns():
    pats = set()
    for f in glob.glob(ROOT + "/tests/**/*.rxt", recursive=True):
        with open(f, "rb") as fh:
            for raw in fh.read().split(b"\n"):
                if raw.startswith(b"pattern "):
                    pats.add(raw[8:].decode("utf-8", "surrogateescape"))
    return sorted(pats)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--sample", type=int, default=0)
    ap.add_argument("--seed", type=int, default=20260828)
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()

    pats = corpus_patterns()
    if args.sample:
        random.Random(args.seed).shuffle(pats)
        pats = pats[:args.sample]
    if args.limit:
        pats = pats[:args.limit]

    from concurrent.futures import ThreadPoolExecutor
    cols = ["idx", "bytes", "total", "prose", "tables", "table_entries",
            "table_arrays", "jump_entries", "jump_arrays",
            "labels", "slabels", "olabels", "gotos",
            "addr_taken", "engine", "rungs", "prefilter", "dfa_table",
            "ncaps", "emit_s", "err", "pattern"]
    out = open(args.out, "w")
    out.write("\t".join(cols) + "\n")
    log = open(args.out + ".log", "w")
    done = [0]

    def work(item):
        i, pat = item
        text, err, secs = emit(pat)
        if err is not None:
            return dict(idx=i, err=err, emit_s="%.3f" % secs, pattern=pat)
        r = scan(text)
        st = r["stamps"]
        return dict(idx=i, bytes=r["bytes"], total=r["total"], prose=r["prose"],
                    tables=r["tables"], table_entries=r["table_entries"],
                    table_arrays=r["table_arrays"],
                    jump_entries=r["jump_entries"], jump_arrays=r["jump_arrays"],
                    labels=r["labels"], slabels=r["slabels"],
                    olabels=r["olabels"], gotos=r["gotos"],
                    addr_taken=r["addr_taken"],
                    engine=st.get("RX_ENGINE", ""), rungs=st.get("RX_VM_RUNGS", ""),
                    prefilter=st.get("RX_VM_PREFILTER", ""),
                    dfa_table=st.get("RX_DFA_TABLE", ""), ncaps=st.get("RX_NCAPS", ""),
                    emit_s="%.3f" % secs, err="", pattern=pat)

    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        for row in ex.map(work, list(enumerate(pats))):
            out.write("\t".join(str(row.get(c, "")).replace("\t", "\\t").replace("\n", "\\n")
                                for c in cols) + "\n")
            done[0] += 1
            if done[0] % 50 == 0:
                out.flush()
                log.write("%d/%d\n" % (done[0], len(pats)))
                log.flush()
    out.close()
    log.write("DONE %d\n" % done[0])
    log.close()


if __name__ == "__main__":
    main()
