"""tests/oracle/local_adapter.py — the LOCAL DIRECT-LINK adapter
(`docs/design/oracle_interface.md` §6, "Local direct-link adapter"): wraps
libpcre2 in-process and answers whichever local library this box resolves
(Homebrew 10.48 on the Mac dev box; whatever the CI/dev box has) — never the
pinned 10.46 reference unless it happens to be the one resolved.

**IMPLEMENTATION CHOICE, recorded per the brief (the design leaves this
open):** the design's own text says the local adapter "wraps §1.2/§1.3's
existing `pcre2_abi.h` binding" -- the C direct-link header PC-3/PC-4/
uprops_oracle.c use. This module instead:

  - answers `membership` by BUILDING AND SHELLING OUT TO the existing,
    already-tested `tests/uprops/uprops_oracle.c` binary (which already
    uses `pcre2_abi.h`, and whose own stdout format IS §5.5's wire format
    verbatim -- no translation layer needed), rather than re-deriving the
    whole-code-point-space sweep in Python. A find-all sweep over 1.1M code
    points is exactly the workload `uprops_oracle.c`'s own header says a
    per-call binding would be too slow for ("still unfinished after ten
    minutes on ONE property" without `PCRE2_NO_UTF_CHECK`); reusing the
    proven C sweep is the simplest conforming choice, not a new mechanism.
  - answers the other five kinds via CTYPES, BORROWING (not copying)
    `docs/design/backrefs_measurements/probes/br_oracle.py` (which in turn
    borrows `pcre2_ctypes.py`) -- the same two-level borrowing chain
    `u8_oracle.py`/`la_oracle.py` already use, on `br_oracle.py`'s own rule
    ("a lane that re-implements the binding it is checking cannot detect
    that the original moved").

Net effect: one adapter, two transports underneath it, both already-proven
mechanisms in this tree -- nothing new was invented to reach libpcre2.

**SCOPE LIMITATION, recorded rather than silently narrowed**: only the
DEFAULT `OracleId.config` (utf=False, caseless=False, the default limit
triple) is implemented. A non-default `utf`/`caseless`/limit config would
need `pcre2_compile_8`'s options word and a `pcre2_match_context` built with
`pcre2_set_match_limit`/`_depth_limit`/`_heap_limit` -- neither
`pcre2_ctypes.py` nor `br_oracle.py` expose that today, and the uprops
customer (this lane's own scope) never asks for one. `answer()` raises
NotImplementedError on a non-default `oracle_id` rather than silently
answering the wrong config.
"""
import ctypes
import importlib.util
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
_BR_ORACLE = os.path.join(
    _ROOT, "docs", "design", "backrefs_measurements", "probes",
    "br_oracle.py")
_UPROPS_ORACLE_C = os.path.join(_ROOT, "tests", "uprops", "uprops_oracle.c")

sys.path.insert(0, os.path.join(_ROOT, "tests", "oracle"))
import oracle_store as _os_  # noqa: E402


def _borrow(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class LocalAdapter(object):
    """`capabilities()` + `answer(batch)` (§6). One instance per resolved
    library; `oracle_id` is discovered at construction (never hand-typed) by
    reading the version the borrowed binding actually loaded."""

    NAME = "libpcre2"

    def __init__(self):
        # [ORACLE-LINK]/D98's own lesson, applied to THIS binding too: a
        # ctypes CDLL load with no PCREC_PCRE2_PATH override resolves
        # whatever the OS's bare-SONAME search finds first, which on darwin
        # is the SYSTEM copy (10.42) via the dyld shared cache, not the
        # Homebrew one `tests/lib/resolve_pcre2.sh` resolves for every C
        # oracle in this tree (U13/U15b's own skew, one binding kind over).
        # `pcre2_ctypes.py`'s `_load()` already reads `PCREC_PCRE2_PATH` from
        # the environment FIRST when present (its own header, item 3) -- so
        # resolving it here, before `_borrow()` triggers that import, makes
        # this adapter see the SAME library every C oracle in this tree does,
        # rather than re-deriving a second candidate search.
        self._pcre2_env = self._resolve_pcre2_env()
        if self._pcre2_env.get("PCREC_PCRE2_PATH"):
            os.environ["PCREC_PCRE2_PATH"] = self._pcre2_env["PCREC_PCRE2_PATH"]
        self._br = _borrow(_BR_ORACLE, "br_oracle")
        # `pcre2_config(PCRE2_CONFIG_VERSION)` returns the FULL raw string
        # ("10.48 2024-06-06" -- release number and date together,
        # `pcre2_abi.h`'s own `pcre2_abi_version()` passes it through
        # unmodified). Every citation of a library version elsewhere in this
        # tree (`oracle_store/libpcre2-10.46/`, the design's own fixture
        # `libpcre2@10.46(...)`) is the bare release number -- so `OracleId`
        # takes the first whitespace-delimited token, a recorded
        # implementation choice (the design does not spell this split out).
        self._version = self._br.version().split()[0]
        self._uprops_bin = None  # built lazily, only if `membership` is asked

    @staticmethod
    def _resolve_pcre2_env():
        env_probe = subprocess.run(
            ["bash", "-c",
             ". tests/lib/resolve_pcre2.sh; "
             "printf 'PCRE2_AVAILABLE=%s\\nPCRE2_CFLAGS=%s\\n"
             "PCRE2_LIBS=%s\\nPCREC_PCRE2_PATH=%s\\n' "
             '"$PCRE2_AVAILABLE" "$PCRE2_CFLAGS" "$PCRE2_LIBS" '
             '"${PCREC_PCRE2_PATH:-}"'],
            cwd=_ROOT, capture_output=True, text=True, timeout=30)
        return dict(line.split("=", 1) for line in
                    env_probe.stdout.strip().splitlines() if "=" in line)

    # -- capabilities() ----------------------------------------------------

    def oracle_id(self, **config):
        if config:
            raise NotImplementedError(
                "LocalAdapter answers only the DEFAULT OracleId.config "
                "today (see this module's own header) -- got %r" % (config,))
        return _os_.OracleId(self.NAME, self._version)

    def capabilities(self):
        return {
            "oracle_id": self.oracle_id(),
            "kinds": list(_os_.KIND_QUESTION_FIELDS.keys()),
            "transport": "in-process",
            "max_batch": None,
        }

    # -- answer(batch) -------------------------------------------------

    def answer(self, batch):
        """`batch`: list of (kind, question_fields_dict). Returns a list of
        answer-field tuples, ordered per KIND_ANSWER_COLUMNS[kind],
        POSITIONALLY corresponding to `batch` (§6's contract) -- even though
        the membership kind is answered by one grouped subprocess call
        underneath, every question in `batch` gets its own answer slot back
        in its own input position."""
        out = [None] * len(batch)
        membership_idx = [i for i, (k, _) in enumerate(batch)
                           if k == "membership"]
        if membership_idx:
            self._answer_membership(batch, membership_idx, out)
        for i, (kind, q) in enumerate(batch):
            if kind == "membership":
                continue
            out[i] = self._answer_one(kind, q)
        return out

    def _answer_one(self, kind, q):
        if kind == "compile-accept":
            return self._compile_accept(q["pattern"])
        if kind == "match-at":
            return self._match_at(q["pattern"], q["subject"], q["startpos"])
        if kind == "captures":
            return self._captures(q["pattern"], q["subject"], q["startpos"],
                                   q["nslots"])
        if kind == "name-accept":
            return self._name_accept(q["namespace"], q["name"])
        if kind == "pattern-info":
            return self._pattern_info(q["pattern"])
        raise ValueError("LocalAdapter cannot answer kind %r here "
                          "(membership routes through _answer_membership)"
                          % (kind,))

    def _compile_accept(self, pattern):
        err = self._br.compile_err(pattern)
        if err is None:
            return ("accept", "", "")
        code, _offset, msg = err
        return ("reject", str(code), msg)

    def _match_at(self, pattern, subject, startpos):
        try:
            rx = self._br.pcre2.compile(pattern)
        except Exception as e:  # noqa: BLE001 -- a refused pattern has no match answer
            raise ValueError(
                "match-at question over a pattern libpcre2 refuses to "
                "compile: %r (%s) -- ask compile-accept first" % (pattern, e))
        r = rx.search(subject, startpos)
        if r is None:
            return ("nomatch", "", "", "")
        (s, e), _groups = r
        return ("match", str(s), str(e), "")

    def _captures(self, pattern, subject, startpos, nslots):
        rx = self._br.pcre2.compile(pattern)
        r = rx.search(subject, startpos)
        if r is None:
            # "Only meaningful attached to a match answer" (§5.3) -- a
            # captures question over a subject that turns out nomatch has
            # no answer to give; the adapter reports the unset pair for
            # every requested slot rather than raising, since the CALLER
            # asked for this exact (pattern, subject, startpos, nslots)
            # tuple and a batch answer must still be positional.
            pairs = [(-1, -1)] * nslots
        else:
            (s, e), groups = r
            pairs = [(s, e)] + [((-1, -1) if g is None else g)
                                 for g in groups]
            if len(pairs) < nslots:
                pairs += [(-1, -1)] * (nslots - len(pairs))
            else:
                pairs = pairs[:nslots]
        flat = []
        for s, e in pairs:
            flat.append(str(s)); flat.append(str(e))
        return (" ".join(flat),)

    # Namespace -> template synthesizing the probe pattern (§2 kind 4's own
    # argument for why name-accept is its own kind rather than a bare
    # compile-accept: the synthesis template is namespace-specific and
    # belongs in the adapter). Namespaces beyond `uprops-*` are named here
    # because PC-3 asks about `verb`/`posix-class` too (§1.2); wiring PC-3
    # itself through this adapter is a later migration-ladder step (§9
    # Step 3), not this lane's build, but the templates cost nothing to
    # state now and keep the namespace vocabulary in one place.
    _NAME_TEMPLATES = {
        "uprops-category": "\\p{%s}",
        "uprops-script-bare": "\\p{%s}",
        "uprops-script-sc": "\\p{sc=%s}",
        "uprops-script-scx": "\\p{scx=%s}",
        "verb": "(*%s)",
        "posix-class": "[[:%s:]]",
    }

    def _name_accept(self, namespace, name):
        tmpl = self._NAME_TEMPLATES.get(namespace)
        if tmpl is None:
            raise ValueError("unknown name-accept namespace %r (known: %r)"
                              % (namespace, sorted(self._NAME_TEMPLATES)))
        pat = (tmpl % name).encode("latin-1")
        err = self._br.compile_err(pat)
        if err is None:
            return ("accept", "")
        code, _offset, _msg = err
        return ("reject", str(code))

    def _pattern_info(self, pattern):
        code = self._br.Code(pattern)
        cc = ctypes.c_uint32(0)
        # PCRE2_INFO_CAPTURECOUNT = 4, MEASURED 2026-09-10 against this
        # binding's own resolved library (compiled "(a)(b)(c)", swept every
        # info code 0..19, code 4 is the only one returning 3) -- not read
        # from documentation, per this tree's standing rule that an
        # undocumented-here enum is measured before it is trusted.
        self._br._lib.pcre2_pattern_info_8(code._code, 4, ctypes.byref(cc))
        table = code.nametable()  # libpcre2's OWN order (§5.6: name-ascending)
        table.sort(key=lambda pair: pair[1])  # (name asc, byte-exact strcmp)
        nt = " ".join("%s:%d" % (name, num) for num, name in table)
        return (str(cc.value), str(len(table)), nt)

    # -- membership: grouped subprocess call to uprops_oracle -------------

    def _ensure_uprops_bin(self):
        if self._uprops_bin is not None:
            return self._uprops_bin
        env = self._pcre2_env
        if env.get("PCRE2_AVAILABLE") != "1":
            raise RuntimeError(
                "LocalAdapter: libpcre2 not resolvable (tests/lib/"
                "resolve_pcre2.sh) -- cannot answer `membership`")
        cc_probe = subprocess.run(
            ["bash", "-c", ". tests/lib/cc_resolve.sh; printf '%s' \"$CC\""],
            cwd=_ROOT, capture_output=True, text=True, timeout=30)
        workdir = os.path.join(_ROOT, "build", "oracle_cache", "_bin")
        os.makedirs(workdir, exist_ok=True)
        binpath = os.path.join(workdir, "uprops_oracle")
        cflags = env.get("PCRE2_CFLAGS", "").split()
        libs = env.get("PCRE2_LIBS", "").split()
        cc = cc_probe.stdout.strip() or "gcc"
        cmd = ([cc, "-O1", "-std=gnu11", "-I", os.path.join(_ROOT, "tests", "fuzz")]
               + cflags + ["-o", binpath, _UPROPS_ORACLE_C] + libs)
        r = subprocess.run(cmd, cwd=_ROOT, capture_output=True, text=True,
                            timeout=60)
        if r.returncode != 0:
            raise RuntimeError(
                "LocalAdapter: uprops_oracle.c failed to build: %s"
                % (r.stderr,))
        self._uprops_bin = binpath
        return binpath

    def _answer_membership(self, batch, idx, out):
        # uprops_oracle takes many NAMEs in one call per encoding, which is
        # exactly the batch-first shape (§6): one subprocess call per
        # encoding present in this batch, not one per question.
        by_enc = {}
        for i in idx:
            _, q = batch[i]
            by_enc.setdefault(q["encoding"], []).append(i)
        binpath = self._ensure_uprops_bin()
        for enc, indices in by_enc.items():
            if enc not in ("byte", "utf8"):
                raise ValueError("membership encoding must be 'byte' or "
                                  "'utf8', got %r" % (enc,))
            names = [batch[i][1]["property"] for i in indices]
            r = subprocess.run([binpath, enc] + names, cwd=_ROOT,
                                capture_output=True, text=True, timeout=600)
            if r.returncode != 0:
                raise RuntimeError("uprops_oracle %s failed: %s"
                                    % (enc, r.stderr))
            lines = {}
            for line in r.stdout.splitlines():
                parts = line.split(None, 1)
                if not parts:
                    continue
                lines[parts[0]] = parts[1] if len(parts) > 1 else ""
            for i in indices:
                name = batch[i][1]["property"]
                if name not in lines:
                    raise RuntimeError(
                        "uprops_oracle %s printed no line for %r "
                        "(the oracle run is short)" % (enc, name))
                body = lines[name]
                if body.startswith("ERR "):
                    # A name-accept-shaped refusal has no membership set;
                    # report the empty interval list, the honest "this
                    # oracle has no such property" answer for this kind.
                    out[i] = ("",)
                else:
                    out[i] = (_canon_intervals(body),)


def _canon_intervals(body):
    """`uprops_oracle.c`'s own printed format (`LO-HI LO-HI ...`, uppercase
    hex, ascending) IS §5.5's wire format already -- pass through
    unmodified rather than re-deriving it, per this module's own header."""
    return body.strip()


if __name__ == "__main__":
    a = LocalAdapter()
    print("oracle_id:", a.oracle_id())
    print("capabilities:", a.capabilities())
    batch = [
        ("compile-accept", {"pattern": b"a(b|c)+d"}),
        ("compile-accept", {"pattern": b"a("}),
        ("match-at", {"pattern": b"a(b|c)+d", "subject": b"xabcd", "startpos": 0}),
        ("captures", {"pattern": b"(a)(b)", "subject": b"ab", "startpos": 0, "nslots": 2}),
        ("name-accept", {"namespace": "uprops-category", "name": "L"}),
        ("name-accept", {"namespace": "uprops-category", "name": "NotAThing"}),
        ("pattern-info", {"pattern": b"(?<zeta>a)(?<alpha>b)(?<mu>c)"}),
        ("membership", {"property": "Greek", "encoding": "byte"}),
    ]
    for (kind, q), ans in zip(batch, a.answer(batch)):
        print(kind, q, "->", ans)
