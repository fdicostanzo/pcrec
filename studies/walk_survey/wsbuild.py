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

PHASES = ["pre", "skip", "fwd", "rev", "anc", "vm", "endw", "misc", "unk"]
HOOK = re.compile(r"call\s+[0-9a-f]+\s+<(__asan_load(?:1|2|4|8|16|N)_noabort|memchr|memrchr|memcmp|memmem)>")
HERE = os.path.dirname(os.path.abspath(__file__))
CFLAGS = ["-O2", "-g", "-fno-pie", "-fsanitize=kernel-address",
          "--param", "asan-instrumentation-with-call-threshold=0",
          "--param", "asan-stack=0", "--param", "asan-globals=0",
          "-fno-builtin-memchr", "-fno-builtin-memrchr", "-fno-builtin-memcmp",
          "-fno-builtin-memmem", "-w"]


def classify(chain, text, callee):
    """chain: emitted function names, innermost first; text: the line."""
    fns = " ".join(chain)
    t = text
    inner = chain[0] if chain else ""
    # the anchored match-here machine (the `match` entry and a hybrid's
    # anchored DFA), before the generic forward/reverse words
    if "anchored_" in t or inner.endswith("_match") or "_match_dfa" in inner:
        return "anc"
    if re.search(r"\brx_L\w+|_match_anchored|_vm_", fns) or re.search(r"\brx_L\d", t):
        return "vm"
    if "reverse" in t or "rewind" in t or "_reverse" in inner:
        return "rev"
    if "can_begin" in t or "start_byte" in t or "first_byte" in t:
        return "skip"
    if "reqrun" in fns or "req_" in inner or "reqbyte" in fns:
        return "pre"
    if "end_window" in t or "_END_WINDOW" in t or "window" in inner:
        return "endw"
    if "forward" in t or "scan_position" in t:
        return "skip" if callee in ("memchr", "memrchr", "memmem") else "fwd"
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
        m = HOOK.search(ln)
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
    lines = open(c, encoding="utf8", errors="replace").read().split("\n")
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
                m = re.search(r":(\d+)", loc)
                ln = int(m.group(1)) if m else 0
                texts.append((ln, lines[ln - 1].strip() if 0 < ln <= len(lines) else ""))
            ph = "unk"
            for d in range(len(rec)):
                ph = classify(chain[d:], texts[d][1], callee.replace("__asan_", ""))
                if ph != "unk":
                    break
            ln, text = texts[min(d, len(texts) - 1)] if texts else (0, "")
            fm.write("%x %d\n" % (a, PHASES.index(ph)))
            fs.write("%x\t%s\t%s\t%d\t%s\t%s\n" % (a, ph, callee, ln, ">".join(chain), text[:160]))
    print("OK\t%d" % len(sites))


if __name__ == "__main__":
    main()
