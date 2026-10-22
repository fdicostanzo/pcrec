r"""tests/oracle/build_casemap_store.py -- the CASE-MAP INSTANCE ([SUBST-CASE]):
populates the `case-map` kind with what libpcre2's own pcre2_substitute does
to every Unicode scalar value under `\U$0` and `\L$0` (PCRE2_SUBSTITUTE_EXTENDED,
UTF mode, pattern `(?s).`), one row per direction.

THE STORED ANSWERS COME FROM LIBPCRE2 AND NOTHING ELSE. This script reads no
UCD file and imports nothing from third_party/: the generator's case table
(src/core/case_tables.inc) is the thing under test, and a control that shared
its source would be one source wearing two hats (tests/oracle/case_map_check.py
is the comparison).

It binds libpcre2-8 directly through ctypes (the six existing kinds go through
the adapters; neither answers a substitute question) and REFUSES to write unless
the library it loaded is the 10.46 reference. Surrogates (U+D800-DFFF) are not
scalar values and are not swept. Each swept value must come back as exactly one
code point (the generator's table is one-to-one by construction; a 1:n answer
would be a finding, not a row).

Usage:
    python3 -I tests/oracle/build_casemap_store.py
"""
import ctypes
import datetime
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, _HERE)

import oracle_store as os_  # noqa: E402

PCRE2_UTF = 0x00080000
PCRE2_SUBSTITUTE_EXTENDED = 0x00000200
PCRE2_CONFIG_VERSION = 11
REFERENCE = "10.46"


def load():
    path = os.environ.get("PCREC_PCRE2_PATH") or "libpcre2-8.so.0"
    lib = ctypes.CDLL(path)
    buf = ctypes.create_string_buffer(64)
    lib.pcre2_config_8(PCRE2_CONFIG_VERSION, buf)
    version = buf.value.decode().split()[0]
    lib.pcre2_compile_8.restype = ctypes.c_void_p
    lib.pcre2_compile_8.argtypes = [
        ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_void_p]
    lib.pcre2_substitute_8.argtypes = [
        ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_size_t,
        ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p,
        ctypes.c_size_t, ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t)]
    return lib, version


def sweep(lib, templates):
    """{direction: {cp: to}} for every cp whose answer differs from itself."""
    err = ctypes.c_int()
    eo = ctypes.c_size_t()
    code = lib.pcre2_compile_8(b"(?s).", 5, PCRE2_UTF, ctypes.byref(err),
                               ctypes.byref(eo), None)
    if not code:
        raise SystemExit("pattern (?s). did not compile: %d" % err.value)
    out = {d: {} for d in templates}
    buf = ctypes.create_string_buffer(64)
    for cp in range(0x110000):
        if 0xD800 <= cp < 0xE000:
            continue
        subj = chr(cp).encode("utf-8")
        for d, tpl in templates.items():
            n = ctypes.c_size_t(64)
            rc = lib.pcre2_substitute_8(
                code, subj, len(subj), 0, PCRE2_SUBSTITUTE_EXTENDED, None,
                None, tpl, len(tpl), buf, ctypes.byref(n))
            if rc != 1:
                raise SystemExit("substitute U+%04X %s: rc=%d" % (cp, d, rc))
            res = buf.raw[:n.value].decode("utf-8")
            if len(res) != 1:
                raise SystemExit("U+%04X %s is not one-to-one: %r"
                                 % (cp, d, res))
            if ord(res) != cp:
                out[d][cp] = ord(res)
    return out


def main():
    lib, version = load()
    if version != REFERENCE:
        raise SystemExit("libpcre2 is %s, the reference is %s: not writing "
                         "the committed store" % (version, REFERENCE))
    swept = sweep(lib, {"upper": b"\\U$0", "lower": b"\\L$0"})
    oid = os_.OracleId("libpcre2", version, utf=True)
    rows = []
    for d in ("upper", "lower"):
        pairs = " ".join("%X>%X" % kv for kv in sorted(swept[d].items()))
        rows.append(({"direction": d, "encoding": "utf8"}, (pairs,)))
    path = os_.store_path(os.path.join(_ROOT, "oracle_store"), oid, "case-map")
    now = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    n = os_.write_store(
        path, oid, "case-map", rows, now, os.uname().nodename,
        "python3 -I tests/oracle/build_casemap_store.py "
        "(every scalar value U+0000-10FFFF minus surrogates)")
    print("wrote %s (%d rows: upper %d, lower %d changed code points)"
          % (path, n, len(swept["upper"]), len(swept["lower"])))


if __name__ == "__main__":
    main()
