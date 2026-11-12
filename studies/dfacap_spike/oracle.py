"""oracle.py -- the two witnesses the spike is differenced against.

PCRE2: the repo's own ctypes binding (docs/design/eng_brep_measurements/
probes/pcre2_ctypes.py, borrowed, not copied -- the same chain
tests/oracle/local_adapter.py uses), against this box's libpcre2-8 (10.46).

pcrec VM: `build/pcrec --engine=vm` artifacts of THIS worktree, linked into a
tiny batch driver (vmdriver.c) that reads hex subjects on stdin and prints
every group's offsets -- one compile per pattern, not one process per subject.
"""
import importlib.util
import os
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
_B = os.path.join(ROOT, "docs", "design", "eng_brep_measurements", "probes", "pcre2_ctypes.py")
_spec = importlib.util.spec_from_file_location("pcre2_ctypes", _B)
p2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(p2)

PCRE2_CASELESS = 0x00000008
PCRE2_DOTALL = 0x00000020
PCRE2_EXTENDED = 0x00000080

SCRATCH = os.environ.get("CAPSPIKE_SCRATCH",
                         os.path.join(os.environ.get("PCREC_TMPDIR", "/var/tmp/pcrec-" + os.environ.get("USER", "pcrec")),
                                      "scratch", "capspike"))
PCREC = os.environ.get("PCREC", os.path.join(ROOT, "build", "pcrec"))


def pcre2_version():
    return p2.version()


class Pcre2:
    def __init__(self, pat, flags, utf8, ncap):
        opts = 0
        if "i" in flags:
            opts |= PCRE2_CASELESS
        if "s" in flags:
            opts |= PCRE2_DOTALL
        if "x" in flags:
            opts |= PCRE2_EXTENDED
        if utf8:
            opts |= p2.PCRE2_UTF
        self.ncap = ncap
        self.rx = p2.Compiled(pat, opts)

    def search(self, subj):
        try:
            m = self.rx.search(subj)
        except p2.Pcre2Error as e:
            return ("ERR", str(e))
        if m is None:
            return None
        span, groups = m
        g = [span] + list(groups)
        g += [None] * (self.ncap + 1 - len(g))
        return g


VMDRIVER = r'''
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "m.c"
static int hx(int c){ return c<='9'?c-'0':(c|32)-'a'+10; }
int main(void){
    static char line[1<<16]; static unsigned char s[1<<15];
    ptrdiff_t caps[RX_NCAPS][2];
    while (fgets(line, sizeof line, stdin)) {
        size_t n = 0, L = strcspn(line, "\n");
        for (size_t i = 0; i + 1 < L; i += 2) s[n++] = (unsigned char)(hx(line[i])*16 + hx(line[i+1]));
        for (int g = 0; g < RX_NCAPS; g++) caps[g][0] = caps[g][1] = -1;
        int r = rx_search(s, n, 0, caps);
        if (r <= 0) { printf("%s %d\n", r == 0 ? "N" : "E", r); continue; }
        printf("M");
        for (int g = 0; g < RX_NCAPS; g++) printf(" %td,%td", caps[g][0], caps[g][1]);
        printf("\n");
    }
    return 0;
}
'''


def pcrec_vm(pat, flags, utf8, subjects, tag="p"):
    """Returns (list of results aligned to subjects, None) or (None, reason)."""
    d = tempfile.mkdtemp(prefix=tag + "_", dir=SCRATCH)
    try:
        a = [PCREC, "--features", "all", "--engine=vm", "-p", "rx", "-o", os.path.join(d, "m.c")]
        if "i" in flags:
            a.append("-i")
        if utf8:
            a += ["-e", "utf8"]
        a += ["--pattern", pat]
        r = subprocess.run(a, capture_output=True, timeout=120)
        if r.returncode != 0:
            return None, "pcrec refused: " + r.stderr.decode("utf8", "replace").strip().split("\n")[0]
        with open(os.path.join(d, "drv.c"), "w") as fh:
            fh.write(VMDRIVER)
        r = subprocess.run(["gcc", "-O0", "-w", "-o", os.path.join(d, "drv"), os.path.join(d, "drv.c")],
                           capture_output=True, timeout=300, cwd=d)
        if r.returncode != 0:
            return None, "gcc failed: " + r.stderr.decode("utf8", "replace")[:200]
        inp = "".join(s.hex() + "\n" for s in subjects)
        r = subprocess.run([os.path.join(d, "drv")], input=inp.encode(), capture_output=True, timeout=600)
        res = []
        for l in r.stdout.decode().split("\n")[:len(subjects)]:
            f = l.split()
            if not f or f[0] == "N":
                res.append(None)
            elif f[0] == "E":
                res.append(("ERR", f[1]))
            else:
                g = []
                for x in f[1:]:
                    s, e = map(int, x.split(","))
                    g.append(None if s < 0 or e < 0 else (s, e))
                res.append(g)
        if len(res) != len(subjects):
            return None, "driver output short (%d of %d)" % (len(res), len(subjects))
        return res, None
    finally:
        subprocess.run(["rm", "-rf", "--", d])
