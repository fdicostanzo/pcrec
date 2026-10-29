#!/usr/bin/env python3
"""rwsurvey runner: feed a pattern population through build/probe/pcrec_probe.

  run_survey.py corpus OUT     pcrec's own tests/**/*.rxt `pattern` rows
  run_survey.py bench  OUT     pcrec-bench bench/*/patterns/*.rx  (READ-ONLY)
  run_survey.py list FILE OUT  one pattern per line (escaped as .rxt subject escapes)

Each compile appends a '@@ SRC' marker and the probe's own dump to OUT.
One pcrec_probe process per pattern, sequential. Heavy by the BOILERPLATE
sweep cap: launch it through scripts/boxlock run.
"""
import os, re, subprocess, sys, glob

W = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROBE = os.environ.get("PROBE_BIN", os.path.join(W, "build/probe/pcrec_probe"))
CLI = os.path.join(W, "build/pcrec")
BENCH = "/home/pcrec/projects/pcrec-bench/bench"


def unesc(s):
    out = bytearray()
    i = 0
    b = s.encode("utf-8", "surrogateescape")
    while i < len(b):
        c = b[i]
        if c == 0x5C and i + 1 < len(b):
            n = b[i + 1]
            if n == ord("n"): out.append(10); i += 2; continue
            if n == ord("t"): out.append(9); i += 2; continue
            if n == ord("r"): out.append(13); i += 2; continue
            if n == ord("\\"): out.append(0x5C); i += 2; continue
            if n == ord("x") and i + 3 < len(b) + 0:
                try:
                    out.append(int(b[i + 2:i + 4], 16)); i += 4; continue
                except ValueError:
                    pass
        out.append(c); i += 1
    return bytes(out)


def corpus_rows():
    files = sorted(glob.glob(os.path.join(W, "tests/**/*.rxt"), recursive=True))
    for f in files:
        try:
            txt = subprocess.run([CLI, "--list-source", f], capture_output=True, timeout=60).stdout
        except Exception:
            continue
        head = {}
        for ln in txt.decode("utf-8", "surrogateescape").split("\n"):
            if ln.startswith("#section"):
                break
            if not ln or ln.startswith("#"):
                continue
            c = ln.split("\t")
            if len(c) < 5:
                continue
            kind = c[0]
            if kind in ("features", "encoding", "flags", "engine"):
                head[kind] = c[3]
            elif kind in ("pattern", "pattern-esc"):
                opt = {
                    "flags": c[5] or head.get("flags", ""),
                    "features": c[6] or head.get("features", ""),
                    "encoding": c[8] or head.get("encoding", ""),
                    "engine": c[9] if len(c) > 9 and c[9] else head.get("engine", ""),
                }
                yield ("corpus", os.path.relpath(f, W) + ":" + c[1], unesc(c[4]), opt)


def bench_rows():
    for d in sorted(glob.glob(BENCH + "/*/patterns")):
        s = os.path.basename(os.path.dirname(d))
        for f in sorted(glob.glob(d + "/*.rx")):
            b = open(f, "rb").read()
            yield ("bench:" + s, os.path.basename(f), b, {"encoding": "utf8" if s == "utf8" else "", "features": "all"})


def run(rows, out, stamp=False):
    env = dict(os.environ)
    env["PROBE_OUT"] = out
    n = bad = 0
    for src, name, pat, opt in rows:
        if b"\x00" in pat:
            continue
        cmd = [CLI if stamp else PROBE, "-p", "rx", "-o", "-", "--features", "all"]
        if opt.get("encoding") == "utf8":
            cmd += ["-e", "utf8"]
        if "i" in opt.get("flags", "").split() or opt.get("flags", "") == "i":
            cmd += ["-i"]
        if opt.get("engine") in ("vm", "dfa"):
            cmd += ["--engine=" + opt["engine"]]
        cmd += ["--pattern", pat]
        if stamp:
            try:
                r = subprocess.run(cmd, env=env, capture_output=True, timeout=120)
                m = re.search(rb'#define RX_DFA_SCAN_EDGE "([^"]*)"', r.stdout)
                with open(out, "ab") as f:
                    f.write(("%s\t%s\t%d\t%s\n" % (src, name, r.returncode, m.group(1).decode() if m else "-")).encode())
            except subprocess.TimeoutExpired:
                pass
            n += 1
            continue
        with open(out, "ab") as f:
            f.write(("@@\tSRC\t%s\t%s\tfeat=%s enc=%s flags=%s eng=%s\n" % (
                src, name, "all", opt.get("encoding", ""), opt.get("flags", ""), opt.get("engine", ""))).encode())
        try:
            r = subprocess.run(cmd, env=env, capture_output=True, timeout=120)
            rc = r.returncode
        except subprocess.TimeoutExpired:
            rc = 124
        n += 1
        if rc != 0:
            bad += 1
        with open(out, "ab") as f:
            f.write(("@@\tRC\t%d\n" % rc).encode())
    print("compiled %d patterns, %d nonzero rc" % (n, bad))


def list_rows(path):
    for i, ln in enumerate(open(path, "rb").read().split(b"\n")):
        if ln:
            yield ("list", str(i), unesc(ln.decode("utf-8", "surrogateescape")), {})


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "corpus":
        run(corpus_rows(), sys.argv[2])
    elif mode == "bench":
        run(bench_rows(), sys.argv[2])
    elif mode == "stamp-corpus":
        run(corpus_rows(), sys.argv[2], True)
    elif mode == "stamp-bench":
        run(bench_rows(), sys.argv[2], True)
    elif mode == "list":
        run(list_rows(sys.argv[2]), sys.argv[3])
