#!/usr/bin/env python3
"""
[REVW.1] wave 1 stage 0 -- the long-prefix full-corpus sweep.

WHY THIS EXISTS. lens10_emission_kit_charter.md S4.2 (F3b): the tree's only
long-prefix control (tests/cli/run_cli_tests.sh case3) compiles the pattern
`a` at a 60-byte prefix -- a trivial DFA artifact reaching essentially none
of emit_vm.c's 40+ literal-sized scratch buffers. Stage 3 (a future wave)
retires those buffers behind sb_fragf and claims byte-neutrality at the
60-byte prefix; that claim needs a control that actually REACHES the
buffers, which this sweep supplies as a committed baseline.

METHODOLOGY, dialtrain_byteid_evidence/byteid_sweep.py's own shape (K59RUNG-
BYTEID, 2026-09-17): enumerate every `pattern`/`pattern-esc` block across
tests/**/*.rxt via --list-source (avoids hand-parsing the .rxt escape
vocabulary), decode column 5's \\t \\n \\r \\\\ \\xNN escapes to raw bytes,
pass each pattern to pcrec via argv directly (never a shell string). Default
flags only (no --tune/--features/-i/--engine/--encoding): a module-gated
pattern both-refuses identically at both prefixes, which is not this
sweep's question.

PER PATTERN, two pcrec compiles:
  (1) -p rx            -- the corpus's own everyday prefix.
  (2) -p <60 x 'a'>     -- PCREC_MAX_PREFIX_LEN (limits.def:133), the legal
                           boundary case3 already exercises on ONE pattern.
And, only when (2) succeeds, a THIRD step: gcc-compile the emitted .c under
the harness's own GENCFLAGS (-O1 -std=gnu11 -Wall -Wextra -Werror,
tests/harness/run.sh:213) -- the actual K38 signal. A pcrec-level refusal at
60 bytes that did not occur at "rx" is recorded but is not itself evidence
of a miscompile (it can be an ordinary PCREC_MAX_EMIT_BYTES cap consequence
of longer identifiers); a gcc-level failure on code pcrec itself accepted
is the sharper anomaly and is called out by name in the driver's own
summary.

Usage: python3 longprefix_sweep.py <pcrec> <repo-root> <out-tsv> <cc> <gencflags...>
  gencflags is the REMAINDER of argv, split on spaces by the caller (a
  single environment-sourced string, same convention run_ir_listing.sh's
  GENCFLAGS uses).
"""
import subprocess
import sys
import os

PCREC = sys.argv[1]
REPO_ROOT = sys.argv[2]
OUT_TSV = sys.argv[3]
CC = sys.argv[4]
GENCFLAGS = sys.argv[5:]

P60 = "a" * 60  # PCREC_MAX_PREFIX_LEN = 60 (src/core/limits.def:133);
                # same shape as tests/cli/run_cli_tests.sh's case3 p60.

TIMEOUT_S = 30  # one pcrec compile or one gcc compile; D45's shape, this
                # sweep's own budget (not gen_timeout.sh's shared wrapper,
                # since this driver is python, not bash -- see the .sh
                # wrapper for the outer wall bound on the whole run).


def decode_escape(s: str) -> bytes:
    """Decode the .rxt subject-escape vocabulary: \\t \\n \\r \\\\ \\xNN.
    Verbatim copy of dialtrain_byteid_evidence/byteid_sweep.py's own
    decoder -- ONE implementation would live in tests/lib/ if a THIRD
    driver needs it; two independent copies is not yet the pattern
    memory pcrec-general-mechanisms-not-special-cases warns against."""
    out = bytearray()
    i = 0
    b = s.encode("utf-8", errors="surrogateescape")
    n = len(b)
    while i < n:
        c = b[i]
        if c == 0x5C and i + 1 < n:  # backslash
            nxt = b[i + 1]
            if nxt == ord('t'):
                out.append(0x09); i += 2; continue
            elif nxt == ord('n'):
                out.append(0x0A); i += 2; continue
            elif nxt == ord('r'):
                out.append(0x0D); i += 2; continue
            elif nxt == 0x5C:
                out.append(0x5C); i += 2; continue
            elif nxt == ord('x') and i + 3 < n:
                hx = bytes([b[i + 2], b[i + 3]])
                try:
                    val = int(hx, 16)
                    out.append(val)
                    i += 4
                    continue
                except ValueError:
                    pass
            out.append(c); i += 1; continue
        else:
            out.append(c); i += 1
    return bytes(out)


def find_rxt_files(root):
    files = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(root, "tests")):
        for fn in filenames:
            if fn.endswith(".rxt"):
                files.append(os.path.join(dirpath, fn))
    return sorted(files)


def list_source_patterns(pcrec_bin, rxt_file):
    """Run --list-source, return list of (kind, decoded_pattern_bytes)."""
    try:
        r = subprocess.run([pcrec_bin, "--list-source", rxt_file],
                            capture_output=True, timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return []
    out = r.stdout.decode("utf-8", errors="surrogateescape")
    rows = []
    for line in out.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        fields = line.split("\t")
        if len(fields) < 5:
            continue
        kind = fields[0]
        if kind not in ("pattern", "pattern-esc"):
            continue
        rows.append((kind, decode_escape(fields[4])))
    return rows


def tsv_escape(b: bytes) -> str:
    try:
        s = b.decode("utf-8", errors="backslashreplace")
    except Exception:
        s = repr(b)
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")


def stderr_tail(b: bytes, n=160) -> str:
    s = b.decode("utf-8", errors="replace").strip().replace("\n", " | ")
    return tsv_escape(s.encode("utf-8", "replace"))[:n]


def main():
    files = find_rxt_files(REPO_ROOT)
    print(f"# .rxt files found: {len(files)}", file=sys.stderr)

    all_patterns = []
    for f in files:
        for kind, pat in list_source_patterns(PCREC, f):
            all_patterns.append((f, kind, pat))
    print(f"# total pattern/pattern-esc lines: {len(all_patterns)}", file=sys.stderr)

    tmp_dir = os.path.join(os.path.dirname(os.path.abspath(OUT_TSV)) or ".", "_lp_tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    rows = []
    rx_ok_n = p60_ok_n = p60_gcc_ok_n = 0
    anomalies = []  # (idx, file, pattern) -- rx_ok and p60 pcrec-ok, but gcc failed

    for idx, (f, kind, pat) in enumerate(all_patterns):
        rx_c = os.path.join(tmp_dir, f"p{idx}_rx.c")
        p60_c = os.path.join(tmp_dir, f"p{idx}_60.c")
        p60_bin = os.path.join(tmp_dir, f"p{idx}_60.bin")

        rx_argv = [PCREC, "-p", "rx", "-o", rx_c, "--", pat]
        try:
            rr = subprocess.run(rx_argv, capture_output=True, timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            rr = None
        rx_ok = rr is not None and rr.returncode == 0 and os.path.exists(rx_c)
        rx_err = "" if rx_ok else stderr_tail(rr.stderr if rr else b"TIMEOUT")
        if os.path.exists(rx_c):
            os.remove(rx_c)

        p60_argv = [PCREC, "-p", P60, "-o", p60_c, "--", pat]
        try:
            rp = subprocess.run(p60_argv, capture_output=True, timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            rp = None
        p60_ok = rp is not None and rp.returncode == 0 and os.path.exists(p60_c)
        p60_err = "" if p60_ok else stderr_tail(rp.stderr if rp else b"TIMEOUT")

        p60_size = ""
        p60_gcc_ok = ""
        p60_gcc_err = ""
        if p60_ok:
            p60_size = str(os.path.getsize(p60_c))
            gcc_argv = [CC, *GENCFLAGS, "-I", REPO_ROOT + "/lib", "-c", "-o",
                        p60_bin + ".o", p60_c]
            try:
                rg = subprocess.run(gcc_argv, capture_output=True, timeout=TIMEOUT_S)
            except subprocess.TimeoutExpired:
                rg = None
            ok = rg is not None and rg.returncode == 0
            p60_gcc_ok = "1" if ok else "0"
            if not ok:
                p60_gcc_err = stderr_tail(rg.stderr if rg else b"TIMEOUT")
                anomalies.append((idx, f, pat, p60_gcc_err))
            if os.path.exists(p60_bin + ".o"):
                os.remove(p60_bin + ".o")
            os.remove(p60_c)

        if rx_ok:
            rx_ok_n += 1
        if p60_ok:
            p60_ok_n += 1
        if p60_gcc_ok == "1":
            p60_gcc_ok_n += 1

        rows.append((str(idx), f, kind, "1" if rx_ok else "0", rx_err,
                      "1" if p60_ok else "0", p60_err, p60_size, p60_gcc_ok,
                      p60_gcc_err, tsv_escape(pat)))

    try:
        os.rmdir(tmp_dir)
    except OSError:
        pass

    with open(OUT_TSV, "w") as fh:
        fh.write("idx\tfile\tkind\trx_ok\trx_err\tp60_ok\tp60_err\tp60_size\t"
                  "p60_gcc_ok\tp60_gcc_err\tpattern\n")
        for r in rows:
            fh.write("\t".join(r) + "\n")

    print("")
    print("=== RESULTS ===")
    print(f"total pattern lines:  {len(all_patterns)}")
    print(f"rx_ok:                {rx_ok_n}")
    print(f"p60_ok:               {p60_ok_n}")
    print(f"p60_gcc_ok:           {p60_gcc_ok_n}")
    print(f"pcrec-refused-at-60-only (rx_ok & !p60_ok): "
          f"{sum(1 for r in rows if r[3] == '1' and r[5] == '0')}")
    print(f"GCC ANOMALIES (pcrec accepted the 60-byte artifact, gcc did not): "
          f"{len(anomalies)}")
    for (idx, f, pat, err) in anomalies[:30]:
        pstr = pat.decode("utf-8", errors="backslashreplace")
        print(f"  idx={idx} file={f} pattern={pstr!r} gcc_err={err!r}")
    print("")
    print(f"rows written: {len(rows)} -> {OUT_TSV}")


if __name__ == "__main__":
    main()
