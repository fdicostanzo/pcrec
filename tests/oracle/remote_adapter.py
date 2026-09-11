r"""tests/oracle/remote_adapter.py — the REMOTE REFERENCE adapter
(`docs/design/oracle_interface.md` §6, "Remote reference adapter"): wraps
the ssh-stdin-payload mechanism `docs/design/utf8_measurements/probes/
bundle.py` already uses for the 10.46 reference box, GENERALIZED from one
probe script to one `Question`-batch payload -- exactly the design's own
words for this adapter. Answers over the tailnet-only reference box
(`docs/dev/lanes/BOILERPLATE.md`'s travel-month topology:
`duxevents@100.69.121.107`), LIGHT PROBES ONLY, never a suite run.

WHAT IS BORROWED, AND WHAT IS GENERALIZED, stated separately because the
design's own §6 text uses both words for a reason: the BINDING CHAIN
(`pcre2_ctypes.py`) is borrowed verbatim, embedded by the identical
mechanism `bundle.py` uses (source-as-`repr()`, an `importlib` shim
resolving a borrowed basename out of a dict instead of the filesystem) --
never re-implemented, on `br_oracle.py`'s own rule that a lane which
re-implements the binding it is checking cannot detect that the original
moved. The TRANSPORT SHIM ITSELF (the PREAMBLE below) is a GENERALIZATION
of `bundle.py`'s: that file's borrowed-file list is hardcoded to ONE
specific three-file chain at paths relative to its own directory, because
it exists to run exactly one lane's probes; this module needs a different,
smaller borrowed set (`pcre2_ctypes.py` alone -- the six kinds this lane's
LocalAdapter answers via ctypes never call `br_oracle.py`'s two added
helpers `compile_err`/`nametable` over ssh, because the remote adapter
answers `membership` questions only, the one kind whose reference-vs-local
answer can actually differ for the store's own first customer), so the
embedding shim is written here as a small reusable function parameterized
on the borrowed-file list, rather than importing `bundle.py` and fighting
its fixed list. Nothing is copied from `pcre2_ctypes.py` itself.

**SCOPE, matching LocalAdapter's own stated limitation**: this adapter
answers `membership` ONLY. The design's migration ladder (§9 Step 1) needs
exactly that kind from the remote reference; a general six-kind remote
adapter is a straightforward extension of the same shim (embed
`br_oracle.py` too) but is not built here — D77 (build under measurement),
since nothing in this lane's scope asks the reference box a `compile-accept`
or `match-at` question."""
import hashlib
import json
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
_PCRE2_CTYPES = os.path.join(
    _ROOT, "docs", "design", "eng_brep_measurements", "probes",
    "pcre2_ctypes.py")

sys.path.insert(0, _HERE)
import oracle_store as _os_  # noqa: E402

# `BatchMode=yes`/`ConnectTimeout=10` -- `archive.sh`'s own discipline,
# inherited unchanged (§6).
_SSH_OPTS = ["-o", "ConnectTimeout=10", "-o", "BatchMode=yes"]

# The remote-side python program that answers ONE `membership` batch,
# printed as the tail of the bundled payload (after the borrowed-file
# preamble below splices `pcre2_ctypes` into `sys.modules`-reachable
# form). Deliberately minimal: it imports the bundled `pcre2_ctypes`,
# builds the whole-code-point subject exactly as `uprops_oracle.c` does
# (one find-all pass, `PCRE2_NO_UTF_CHECK` set -- inert on a well-formed
# subject, which this construction always is, and excluded from
# `OracleId.config` for exactly that reason, §3), and prints one JSON
# object per question, one per line, so a truncated remote run is visible
# line by line rather than as one big parse failure.
_REMOTE_MAIN = r'''
import ctypes, json, sys

PCRE2_ZERO_TERMINATED = ctypes.c_size_t(-1).value
PCRE2_UTF_OPT = 0x00080000
PCRE2_NO_UTF_CHECK_OPT = 0x40000000

_lib = pcre2_ctypes._lib


def _u8enc(c):
    if c < 0x80:
        return bytes([c])
    if c < 0x800:
        return bytes([0xC0 | (c >> 6), 0x80 | (c & 0x3F)])
    if c < 0x10000:
        return bytes([0xE0 | (c >> 12), 0x80 | ((c >> 6) & 0x3F),
                       0x80 | (c & 0x3F)])
    return bytes([0xF0 | (c >> 18), 0x80 | ((c >> 12) & 0x3F),
                   0x80 | ((c >> 6) & 0x3F), 0x80 | (c & 0x3F)])


def _build_subject(utf):
    # `cp_at` is indexed by BYTE OFFSET (matching uprops_oracle.c's own
    # `cp_at[subjlen] = c` before `subjlen` advances by the encoded width),
    # NOT by codepoint ORDER -- `pcre2_match`'s ovector reports a byte
    # offset, and a list built by codepoint order silently indexes the
    # wrong entries the moment a codepoint is not 1 byte wide (an
    # IndexError the first time a UTF-8 offset exceeds the codepoint
    # count, caught by this lane's own validation run rather than shipped
    # silently wrong).
    maxcp = 0x10FFFF if utf else 0xFF
    subj = bytearray()
    cp_at = {}
    for c in range(0, maxcp + 1):
        if utf and 0xD800 <= c <= 0xDFFF:
            continue
        cp_at[len(subj)] = c
        if utf:
            subj += _u8enc(c)
        else:
            subj.append(c)
    return bytes(subj), cp_at


_subjects = {}


def sweep(prop, encoding):
    utf = encoding == "utf8"
    if encoding not in _subjects:
        _subjects[encoding] = _build_subject(utf)
    subj, cp_at = _subjects[encoding]
    pat = ("\\p{%s}" % prop).encode("latin-1")
    errcode = ctypes.c_int(0)
    erroff = ctypes.c_size_t(0)
    copts = PCRE2_UTF_OPT if utf else 0
    code = _lib.pcre2_compile_8(pat, len(pat), copts,
                                 ctypes.byref(errcode), ctypes.byref(erroff),
                                 None)
    if not code:
        return None
    md = _lib.pcre2_match_data_create_8(4, None)
    mopts = PCRE2_NO_UTF_CHECK_OPT if utf else 0
    pos = 0
    lo = hi = have = 0
    ivs = []
    while pos < len(subj):
        rc = _lib.pcre2_match_8(code, subj, len(subj), pos, mopts, md, None)
        if rc < 0:
            break
        ov = _lib.pcre2_get_ovector_pointer_8(md)
        cp = cp_at[ov[0]]
        if have and cp == hi + 1:
            hi = cp
        else:
            if have:
                ivs.append((lo, hi))
            lo = hi = cp
        have = 1
        pos = ov[1] if ov[1] > ov[0] else ov[0] + 1
    if have:
        ivs.append((lo, hi))
    _lib.pcre2_match_data_free_8(md)
    _lib.pcre2_code_free_8(code)
    return " ".join("%X-%X" % (l, h) for l, h in ivs)


_lib.pcre2_match_data_create_8.restype = ctypes.c_void_p
_lib.pcre2_match_data_create_8.argtypes = [ctypes.c_uint32, ctypes.c_void_p]

batch = json.loads(_BATCH_JSON)
out = []
for q in batch:
    ivs = sweep(q["property"], q["encoding"])
    out.append({"property": q["property"], "encoding": q["encoding"],
                "intervals": ivs})
sys.stdout.write("__ORACLE_STORE_RESULT__ " + json.dumps(out) + "\n")
sys.stdout.write("__ORACLE_STORE_LIBVERSION__ " + pcre2_ctypes.version()
                  + "\n")
'''

# The embedding shim, generalized from `bundle.py`'s own preamble (see this
# module's header). Structurally identical: borrowed source as `repr()`,
# an `importlib.util.spec_from_file_location` shim resolving a borrowed
# BASENAME out of an in-memory dict instead of a real file, so the whole
# program travels on stdin and nothing is written on the far end.
_PREAMBLE = r'''
# ==== remote_adapter.py preamble -- generalized from bundle.py's own shim.
import importlib.machinery as _im
import importlib.util as _iu

_BUNDLED_SRC = %(files)r


class _MemLoader:
    def __init__(self, base):
        self.base = base

    def create_module(self, spec):
        return None

    def exec_module(self, mod):
        mod.__file__ = "<bundled:%%s>" %% self.base
        exec(compile(_BUNDLED_SRC[self.base], mod.__file__, "exec"),
             mod.__dict__)


class _MemFinder:
    @staticmethod
    def find_spec(name, path=None, target=None):
        base = name + ".py"
        if base in _BUNDLED_SRC:
            return _iu.spec_from_loader(name, _MemLoader(base))
        return None


import sys as _sys
_sys.meta_path.insert(0, _MemFinder)
import pcre2_ctypes
# ==== end preamble
'''


def _build_payload(batch):
    with open(_PCRE2_CTYPES, "r") as f:
        src = f.read()
    files = {"pcre2_ctypes.py": src}
    payload = _PREAMBLE % {"files": files}
    payload += "\n_BATCH_JSON = %r\n" % json.dumps(batch)
    payload += _REMOTE_MAIN
    return payload


class RemoteAdapter(object):
    """`capabilities()` + `answer(batch)` (§6), `membership` kind only
    (this module's own header explains why). `max_batch` is a REAL knob
    here (§6): this implementation sends the WHOLE batch in one ssh round
    trip and leaves splitting a batch too large for one light probe to the
    CALLER, per `capabilities().max_batch` -- deliberately returned as a
    conservative number rather than `None`, so a caller does not have to
    discover the light-probe ceiling by timing out on the reference box."""

    NAME = "libpcre2"
    MAX_BATCH = 8  # conservative: one whole-code-point-space utf8 sweep per
    # property is itself the expensive unit (uprops_oracle.c's own header:
    # "still unfinished after ten minutes" without PCRE2_NO_UTF_CHECK, which
    # this module sets); 8 properties/round trip keeps one call inside the
    # BOILERPLATE.md "seconds" light-probe budget on the properties this
    # lane's own validation used (measured below), not derived from a
    # timing sweep across the whole property table -- OWED, named in the
    # lane report, not silently assumed safe at any N.

    def __init__(self, host):
        self.host = host
        self._version = None  # discovered on first successful call

    def capabilities(self):
        return {
            "oracle_id": None if self._version is None
            else self.oracle_id(),
            "kinds": ["membership"],
            "transport": "ssh-stdin-payload",
            "max_batch": self.MAX_BATCH,
        }

    def oracle_id(self):
        if self._version is None:
            raise RuntimeError(
                "RemoteAdapter.oracle_id() called before any answer() -- "
                "the version is read off the remote run, never hand-typed")
        return _os_.OracleId(self.NAME, self._version)

    def answer(self, batch):
        """`batch`: list of (kind, question_fields_dict), every kind must
        be `membership`. Splits into `<= MAX_BATCH`-sized chunks, one ssh
        call per chunk, positional correspondence preserved."""
        for kind, _ in batch:
            if kind != "membership":
                raise ValueError(
                    "RemoteAdapter answers `membership` only, got %r -- "
                    "see this module's own header for why" % (kind,))
        out = [None] * len(batch)
        for start in range(0, len(batch), self.MAX_BATCH):
            chunk_idx = list(range(start, min(start + self.MAX_BATCH,
                                               len(batch))))
            chunk = [batch[i][1] for i in chunk_idx]
            results, version = self._one_round_trip(chunk)
            self._version = version
            by_key = {(r["property"], r["encoding"]): r for r in results}
            for i in chunk_idx:
                q = batch[i][1]
                r = by_key.get((q["property"], q["encoding"]))
                if r is None:
                    raise RuntimeError(
                        "remote run printed no result for %r -- the run "
                        "is short" % (q,))
                out[i] = (r["intervals"] or "",)
        return out

    def _one_round_trip(self, chunk):
        payload = _build_payload(chunk)
        cmd = ["ssh"] + _SSH_OPTS + [self.host, "python3 -"]
        r = subprocess.run(cmd, input=payload, capture_output=True,
                            text=True, timeout=120)
        if r.returncode != 0:
            raise RuntimeError(
                "RemoteAdapter: ssh %s failed (rc=%d): %s"
                % (self.host, r.returncode, r.stderr[-2000:]))
        results = None
        version = None
        for line in r.stdout.splitlines():
            if line.startswith("__ORACLE_STORE_RESULT__ "):
                results = json.loads(line[len("__ORACLE_STORE_RESULT__ "):])
            elif line.startswith("__ORACLE_STORE_LIBVERSION__ "):
                version = line[len("__ORACLE_STORE_LIBVERSION__ "):].strip()
        if results is None or version is None:
            raise RuntimeError(
                "RemoteAdapter: could not find the result/version markers "
                "in remote stdout -- got: %r" % (r.stdout[-2000:],))
        return results, version.split()[0]


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "duxevents@100.69.121.107"
    a = RemoteAdapter(host)
    batch = [
        ("membership", {"property": "Greek", "encoding": "byte"}),
        ("membership", {"property": "Unknown", "encoding": "byte"}),
    ]
    ans = a.answer(batch)
    print("oracle_id:", a.oracle_id())
    for (kind, q), r in zip(batch, ans):
        print(kind, q, "->", r)
