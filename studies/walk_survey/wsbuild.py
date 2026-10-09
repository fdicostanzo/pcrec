#!/usr/bin/env python3
"""walk_survey: build ONE instrumented artifact + its phase map.

    wsbuild.py PCREC OUTDIR [pcrec args...]      (args end with --pattern P)

Writes OUTDIR/{rx.c,rx.h,bin,map,sites.tsv}. Exit 3 if pcrec refuses the
pattern (its stderr's first line is printed), 4 if gcc fails.

THE PHASE MAP. Every call site the linked binary makes to a load hook
(__asan_load*_noabort) or an interposed scanner (memchr, memrchr, memcmp,
memmem) is found by objdump; its return address is the key wsdrv.c looks up.
addr2line -i on (return address - 1) names the emitted source line and the
inline chain of emitted functions around it; classify() maps that to a phase
from the EMITTED TEXT ALONE (identifiers the emitter writes: rx_forward_*,
rx_reverse_*, rx_anchored_*, rx_can_begin_match, the VM's rx_L labels and
rx_match_anchored, the search wrapper's pre-checks). sites.tsv lists every
site with its phase and the line, so the classification is auditable; a site
no rule claims is phase `unk` and wsdrv reports any load through it.
"""
import os, re, subprocess, sys

PHASES = ["pre", "skip", "fwd", "rev", "anc", "vm", "endw", "misc", "up", "unk"]
HOOK = re.compile(r"call\s+[0-9a-f]+\s+<(__asan_load(?:1|2|4|8|16|N)_noabort|memchr|memrchr|memcmp|memmem)>")
# every other call out of an emitted function: mapped too, so a load inside a
# non-inlined helper (-O0) is attributed through ITS caller (phase `up`)
CALL = re.compile(r"call\s+[0-9a-f]+\s+<(rx_[A-Za-z0-9_.]+)>")
HERE = os.path.dirname(os.path.abspath(__file__))
CFLAGS = ["-O0", "-g", "-fno-pie", "-fsanitize=kernel-address",
          "--param", "asan-instrumentation-with-call-threshold=0",
          "--param", "asan-stack=0", "--param", "asan-globals=0",
          "-fno-builtin-memchr", "-fno-builtin-memrchr", "-fno-builtin-memcmp",
          "-fno-builtin-memmem", "-w"]


def classify(chain, text, callee):
    """chain: emitted function names, innermost first; text: the line.
    First rule that fires wins; the order is the precedence."""
    fns = " ".join(chain)
    t = text
    inner = chain[0] if chain else ""
    # utf8 boundary bookkeeping (K50 startpos guard, next_pos, valid_upto,
    # back_step, a hand-off moved to a character boundary)
    if re.search(r"rx_valid_upto|rx_next_pos|rx_back_step|rx_utf", fns) or \
       "PCREC_ERR_STARTPOS" in t or re.search(r"& 0xC0u?\) [!=]= 0x80", t):
        return "misc"
    # the VM: its labels, span cursors, class atoms/bitmaps, backref compare
    if "_match_anchored" in fns or re.search(r"\brx_L\d|rx_span_cursor|rx_class_(bitmap|atom)|ref\[i\]|rx_vm_", t):
        return "vm"
    if "anchored_" in t:
        return "anc"
    if "reverse" in t or "rewind" in t or "_reverse" in inner:
        return "rev"
    # candidate skipping ahead of a machine: start-byte tables, memchr in
    # the forward search, the offset-skip helper
    if re.search(r"can_begin|start_bytes|start_set|first_byte|ofsskip", t) or "ofsskip" in fns:
        return "skip"
    if callee in ("memchr", "memrchr", "memmem") and "scan_position" in t:
        return "skip"
    if "reqrun" in fns or "req_" in inner or "reqbyte" in fns or "reqrun" in t:
        return "pre"
    if "end_window" in t or "_END_WINDOW" in t or "window" in inner:
        return "endw"
    if re.search(r"forward|scan_position|rx_targets|seed_state|goto \*", t):
        return "fwd"
    if callee in ("memchr", "memrchr", "memmem", "memcmp") and ("_search" in inner or "search_run" in inner):
        return "pre"
    return "unk"


def main():
    pcrec, out = sys.argv[1], sys.argv[2]
    args = sys.argv[3:]
    os.makedirs(out, exist_ok=True)
    c = os.path.join(out, "rx.c")
    r = subprocess.run([pcrec, "-p", "rx", "-o", c] + args, capture_output=True, timeout=300)
    if r.returncode != 0:
        print("REFUSED\t" + r.stderr.decode("utf8", "replace").split("\n")[0][:200])
        sys.exit(3)
    b = os.path.join(out, "bin")
    r = subprocess.run(["gcc"] + CFLAGS + ["-c", c, "-o", os.path.join(out, "rx.o")],
                       capture_output=True, timeout=600)
    if r.returncode != 0:
        print("GCC\t" + r.stderr.decode("utf8", "replace")[:300]); sys.exit(4)
    r = subprocess.run(["gcc", "-O1", "-g", "-no-pie", "-fno-pie", "-I", out,
                        os.path.join(HERE, "wsdrv.c"), os.path.join(out, "rx.o"), "-o", b],
                       capture_output=True, timeout=300)
    if r.returncode != 0:
        print("LINK\t" + r.stderr.decode("utf8", "replace")[:300]); sys.exit(4)
    dis = subprocess.run(["objdump", "-d", "--no-show-raw-insn", b], capture_output=True,
                         timeout=300).stdout.decode("utf8", "replace").split("\n")
    sites = []   # (return address, callee)
    infn = None
    for i, ln in enumerate(dis):
        m = re.match(r"^[0-9a-f]+ <(.*)>:", ln)
        if m:
            infn = m.group(1); continue
        if infn and (infn.startswith("rx_") or infn.startswith("rx.")) or (infn and ".part" in infn):
            pass
        m = HOOK.search(ln) or CALL.search(ln)
        if not m or infn is None:
            continue
        if not (infn.startswith("rx_") or ".rx_" in infn):
            continue
        # return address = next instruction's address
        for j in range(i + 1, min(i + 4, len(dis))):
            mm = re.match(r"^\s*([0-9a-f]+):", dis[j])
            if mm:
                sites.append((int(mm.group(1), 16), m.group(1).replace("_noabort", "")))
                break
    srcs = {}

    def src_line(loc):
        m = re.match(r"(.*):(\d+)", loc)
        if not m:
            return 0, ""
        f, ln = m.group(1), int(m.group(2))
        if f not in srcs:
            try:
                srcs[f] = open(f, encoding="utf8", errors="replace").read().split("\n")
            except OSError:
                srcs[f] = []
        L = srcs[f]
        return ln, (L[ln - 1].strip() if 0 < ln <= len(L) else "")
    a2l = subprocess.run(["addr2line", "-f", "-i", "-a", "-e", b] +
                         ["%x" % (a - 1) for a, _ in sites], capture_output=True,
                         timeout=300).stdout.decode("utf8", "replace").split("\n")
    # parse: 0xADDR, then pairs (fn, file:line) until the next 0x
    recs, cur = [], None
    k = 0
    while k < len(a2l):
        l = a2l[k]
        if l.startswith("0x"):
            cur = []; recs.append(cur); k += 1; continue
        if not l:
            k += 1; continue
        fn = l; loc = a2l[k + 1] if k + 1 < len(a2l) else "?:0"
        cur.append((fn, loc)); k += 2
    with open(os.path.join(out, "map"), "w") as fm, open(os.path.join(out, "sites.tsv"), "w") as fs:
        fm.write("#phases " + " ".join(PHASES) + "\n")
        for (a, callee), rec in sorted(zip(sites, recs)):
            chain = [fn for fn, _ in rec]
            texts = []
            for _fn, loc in rec:
                texts.append(src_line(loc.split(" (discriminator")[0]))
            d = 0
            if callee.startswith("rx_"):
                # a CALL SITE of a non-inlined emitted helper: classified by
                # what the caller's line is doing; used only for loads the
                # helper itself makes (its own sites map to `up`)
                ph = classify(chain, texts[0][1] if texts else "", "call")
            else:
                ph = "unk"
                for d in range(len(rec)):
                    ph = classify(chain[d:], texts[d][1], callee.replace("__asan_", ""))
                    if ph != "unk":
                        break
                # a load inside a small non-inlined helper (-O0: rx_w2,
                # rx_ofsskip, ...) that no rule claims: its caller decides
                if ph == "unk" and len(chain) == 1 and chain[0].startswith("rx_") and \
                        not re.match(r"rx_(search|match|prefilter)", chain[0]):
                    ph = "up"
            ln, text = texts[min(d, len(texts) - 1)] if texts else (0, "")
            fm.write("%x %d\n" % (a, PHASES.index(ph)))
            fs.write("%x\t%s\t%s\t%d\t%s\t%s\n" % (a, ph, callee, ln, ">".join(chain), text[:160]))
    print("OK\t%d" % len(sites))


if __name__ == "__main__":
    main()
