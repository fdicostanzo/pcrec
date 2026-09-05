"""bundle.py — make one self-contained python program out of a probe plus the
files it BORROWS, so the probe can run on a machine that has no copy of this
repository.

WHY THIS EXISTS, and it is a fact about this lane rather than a preference.
The project's reference libpcre2 is **10.46, and it is on the old box**
(`duxevents@192.168.1.100`). This Mac's Homebrew libpcre2 is 10.48, and the
two DIVERGE (the option-run acceptance drift PC-3 found on 2026-09-04). So
every MEASURED-against-libpcre2 claim in `../utf8_design.md` has to execute
where 10.46 is, and the only sanctioned channel there is a light ssh probe
(the [M5.0] brief: "ssh one-liner probes to the old box (light, seconds)").

THE CONSTRAINT THAT SHAPES THE MECHANISM: **nothing is written on the old
box.** Not a temp file, not a checkout. The whole program therefore has to
arrive on stdin, which is why it must be ONE file — and the house oracle is
three files deep (`u8_oracle.py` loads `br_oracle.py` loads
`pcre2_ctypes.py`, each by relative path through `importlib`).

WHAT THIS DOES NOT DO: re-implement the binding. `br_oracle.py`'s own header
states the rule — *"a lane that re-implements the binding it is checking
cannot detect that the original moved"* — and copying the three files into a
fourth would break it exactly as a rewrite would. Instead the borrowed files
are embedded VERBATIM (as `repr()` of their bytes, so no quoting can corrupt
them) and `importlib.util.spec_from_file_location` is shimmed to resolve a
borrowed BASENAME out of that dict instead of off a filesystem. The import
chain that runs on the far end is the same chain, executing the same bytes;
only where the bytes came from changed. If someone edits `pcre2_ctypes.py`
tomorrow, the next bundle carries the edit, which is the whole property
borrowing was for.

The embedded texts are also HASHED into the header the payload prints, so an
archived transcript names the exact bytes of every borrowed file that
produced it — a bundle is not reconstructible from the transcript otherwise.

Usage:
    python3 bundle.py PROBE.py [args...]      # writes the payload to stdout

and `archive.sh` is what pipes it into ssh. Run it against `python3 -` locally
and you get the same measurement against the LOCAL libpcre2, which is how the
10.46-vs-10.48 comparison rows are produced.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# The borrowed chain, deepest first. Basenames, because the shim resolves on
# basename — which is exactly what the borrowers write in their own relative
# paths.
BORROWED = [
    os.path.normpath(os.path.join(
        HERE, "..", "..", "eng_brep_measurements", "probes", "pcre2_ctypes.py")),
    os.path.normpath(os.path.join(
        HERE, "..", "..", "backrefs_measurements", "probes", "br_oracle.py")),
    os.path.join(HERE, "u8_oracle.py"),
]

PREAMBLE = r'''
# ==== bundle.py preamble — the borrowed files, verbatim, and the import shim.
import importlib.machinery as _im
import importlib.util as _iu
import os as _os
import sys as _sys

_BUNDLED_SRC = %(files)r
_BUNDLED_SHA = %(shas)r


class _MemLoader:
    """Executes an embedded file's bytes as a module. Deliberately minimal:
    the borrowed sources import only stdlib and each other."""

    def __init__(self, base):
        self.base = base

    def create_module(self, spec):
        return None

    def exec_module(self, mod):
        mod.__file__ = "<bundled:%%s>" %% self.base
        exec(compile(_BUNDLED_SRC[self.base], mod.__file__, "exec"),
             mod.__dict__)


_real_spec_from_file = _iu.spec_from_file_location


def _spec_from_file(name, location=None, **kw):
    base = _os.path.basename(location or "")
    if base in _BUNDLED_SRC:
        return _iu.spec_from_loader(name, _MemLoader(base))
    return _real_spec_from_file(name, location, **kw)


_iu.spec_from_file_location = _spec_from_file


class _MemFinder:
    """The other half. The shim above covers the BORROWED files, which load
    each other by relative PATH; a probe reaches its oracle by ordinary
    `import u8_oracle`, which never goes near spec_from_file_location. This
    finder answers that import from the same embedded dict, so a probe body
    needs no bundle-awareness -- it is the identical source whether it runs
    here or from the probes directory."""

    @staticmethod
    def find_spec(name, path=None, target=None):
        base = name + ".py"
        if base in _BUNDLED_SRC:
            return _iu.spec_from_loader(name, _MemLoader(base))
        return None


_sys.meta_path.insert(0, _MemFinder)
# ==== end preamble
'''


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: bundle.py PROBE.py [args...]\n")
        return 2
    probe = sys.argv[1]
    if not os.path.isabs(probe):
        probe = os.path.join(HERE, probe)

    files, shas = {}, {}
    for path in BORROWED:
        with open(path, "r") as fh:
            src = fh.read()
        base = os.path.basename(path)
        files[base] = src
        shas[base] = hashlib.sha256(src.encode()).hexdigest()[:16]

    with open(probe, "r") as fh:
        probe_src = fh.read()
    shas[os.path.basename(probe)] = hashlib.sha256(
        probe_src.encode()).hexdigest()[:16]

    out = sys.stdout
    out.write(PREAMBLE % {"files": files, "shas": shas})
    # The probe runs as __main__, which is what it already is when run
    # directly — so a probe body needs no bundle-awareness at all.
    out.write("\n_sys.argv = %r\n" % ([os.path.basename(probe)]
                                      + sys.argv[2:]))
    out.write(probe_src)
    return 0


if __name__ == "__main__":
    sys.exit(main())
