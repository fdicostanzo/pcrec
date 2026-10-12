#!/usr/bin/env python3
"""[COMPOUND] design lane mscomp2: the generators revision 1's sizes.tsv and
one_tu_probe.txt never had (chk S11), re-done with revision 2's parts
(derived Q, F = P under the bound, the ctrl2.c.in controller).

  probes2.py PCREC OUTDIR sizes      -> results/sizes2.tsv
  probes2.py PCREC OUTDIR one-tu     -> results/one_tu_probe2.txt

sizes: linked .text+.rodata+.data.rel.ro of a binary whose main calls only
rx_search (gcc -O2, -ffunction-sections -fdata-sections, -Wl,--gc-sections:
the omission [EMIT-ENTRIES] would do), today vs compound.
one-tu: F + Q + the controller in ONE translation unit, gcc -O1 -std=gnu11
-Wall -Wextra -Werror; first with every part entry exported, then with every
part entry and rx_info made static and nothing omitted (counted diagnostics)."""
import collections, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import twin2                                   # noqa: E402

GT = "/usr/bin/gnutimeout"
CASES = os.path.join(HERE, "results", "cases2.tsv")
MAIN = ('#include <stddef.h>\nint rx_search(const unsigned char*, size_t, size_t, ptrdiff_t (*)[2]);\n'
        'int main(int c, char **v) { (void)v; return rx_search((const unsigned char *)"x", 1, (size_t)c, 0); }\n')


def run(cmd, **kw):
    return subprocess.run([GT, "300"] + cmd, capture_output=True, **kw)


def sqli():
    for ln in open(CASES):
        if "concat-sqli" in ln:
            return bytes.fromhex(ln.split("\t")[2])


def parts(pcrec, p, wd, prefix_today="rx"):
    os.makedirs(wd, exist_ok=True)
    q, has_g, why = twin2.derive(p, "byte")
    assert why.startswith("ok"), why
    r = run([pcrec, "--features", "all", "-p", prefix_today, "-o", f"{wd}/today.c", "--pattern", p])
    assert r.returncode == 0, r.stderr
    for pre, name, text in (("rxf", "floor", p),) + ((("rxq", "q", q),) if q is not None else ()):
        r = run([pcrec, "--features", "all", "-p", pre, "-o", f"{wd}/{name}.c", "--pattern", text])
        assert r.returncode == 0, r.stderr
    fmode = twin2.bound_floor(f"{wd}/floor.c")
    open(f"{wd}/plain.h", "w").write("#define RXP_NCAPS RXF_NCAPS\n")
    inc = '#include "floor.c"\n' + ('#include "q.c"\n' if q is not None else "")
    open(f"{wd}/comp.c", "w").write(inc + open(f"{HERE}/ctrl2.c.in").read())
    defs = ["-DUTF=0", "-DGUARD=0", "-DUCHECK=0", f"-DHAS_G={1 if has_g else 0}",
            f"-DQNEVER={1 if q is None else 0}", f"-DFMODE={fmode}"]
    return defs, q


def linked(wd, src, defs):
    open(f"{wd}/main.c", "w").write(MAIN)
    flags = ["-O2", "-w", "-ffunction-sections", "-fdata-sections", "-Wl,--gc-sections", "-I", wd]
    r = run(["gcc"] + flags + defs + ["-x", "c", "-o", f"{wd}/bin", src, f"{wd}/main.c"])
    assert r.returncode == 0, r.stderr.decode()[:500]
    out = run(["size", "-A", f"{wd}/bin"]).stdout.decode()
    return sum(int(m.group(2)) for m in re.finditer(r"^(\.text|\.rodata|\.data\.rel\.ro)\s+(\d+)", out, re.M))


def sizes(pcrec, out):
    print("# compound vs today, linked .text+.rodata+.data.rel.ro of a binary whose main calls only rx_search")
    print("# (gcc -O2 -ffunction-sections -fdata-sections -Wl,--gc-sections); Q derived, F = P under the bound")
    print("cell\tQ\tlinked_today\tlinked_compound\tratio")
    for name, p in (("trim", rb"^\s+|\s+$"), ("wrapper", rb"^\s*\{|\}\s*$"), ("floor-only", rb"a{0,4}\A"),
                    ("sqli", sqli())):
        wd = f"{out}/sizes/{name}"
        defs, q = parts(pcrec, p, wd)
        t = linked(wd, f"{wd}/today.c", [])
        c = linked(wd, f"{wd}/comp.c", defs)
        qs = "never" if q is None else ("(derived)" if len(q) > 40 else q.decode())
        print(f"{name}\t{qs}\t{t}\t{c}\t{c / t:.2f}", flush=True)


def one_tu(pcrec, out):
    wd = f"{out}/onetu"
    defs, q = parts(pcrec, rb"^\s+|\s+$", wd)
    cc = ["gcc", "-O1", "-std=gnu11", "-Wall", "-Wextra", "-Werror", "-I", wd] + defs + ["-x", "c", "-c", "-o", f"{wd}/c.o"]
    print("# one-TU probe: F (P = ^\\s+|\\s+$ under the bound) + Q (derived: \\s+$) + ctrl2.c.in,")
    print("# gcc -O1 -std=gnu11 -Wall -Wextra -Werror")
    r = run(cc + [f"{wd}/comp.c"])
    print(f"## parts exported: rc={r.returncode}{', no diagnostic' if not r.stderr else ''}")
    for nm in ("floor", "q"):
        s = open(f"{wd}/{nm}.c").read()
        s = re.sub(r"^(int|size_t|ptrdiff_t|const struct rx_info) (rx[fq]_)", r"static \1 \2", s, flags=re.M)
        open(f"{wd}/{nm}_static.c", "w").write(s)
    open(f"{wd}/comp_static.c", "w").write(open(f"{wd}/comp.c").read()
                                           .replace('"floor.c"', '"floor_static.c"').replace('"q.c"', '"q_static.c"'))
    r = run(cc + [f"{wd}/comp_static.c"])
    errs = collections.Counter(re.sub(r"^.*?(error: |cc1: )", r"\1", ln) for ln in r.stderr.decode().splitlines()
                               if "error:" in ln or ln.startswith("cc1:"))
    print(f"## parts' entries and rx_info made static (no omission): rc={r.returncode}, {sum(errs.values())} diagnostics")
    for e, k in sorted(errs.items()):
        print(f"{k:7d} {e}")


def main():
    pcrec, out, what = sys.argv[1:4]
    {"sizes": sizes, "one-tu": one_tu}[what](pcrec, out)


if __name__ == "__main__":
    main()
