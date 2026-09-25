#!/usr/bin/env python3
"""[WORD-FOLD] engine-route stamps for the QUALIFYING population only
(best_len >= 4) — compiling all ~4,000 corpus patterns for a stamp read is
unnecessary; the D77 question is about the population that carries a run,
which is what wf_census.json already narrowed to. Compiles each qualifying
pattern at the shipped default (`--features all -p rx`) and reads
`RX_ENGINE`, `RX_ENGINE_WHY`, `RX_VM_FRAMELESS`, `RX_VM_PREFILTER` off the
emitted artifact.

Env: PCREC, IN (wf_census.json), OUT.
"""
import os, sys, json, subprocess, tempfile

E = os.environ
PCREC = E["PCREC"]


def stamps_for(pat: bytes):
    with tempfile.NamedTemporaryFile(suffix=".c", delete=False) as tf:
        path = tf.name
    try:
        r = subprocess.run([PCREC.encode(), b"--features", b"all", b"-p", b"rx",
                            b"-o", path.encode(), b"--pattern", pat],
                           capture_output=True, timeout=60)
        if r.returncode != 0:
            return {"compile": "refused"}
        text = open(path, encoding="latin-1", errors="replace").read()
        out = {"compile": "ok"}
        for name in ("RX_ENGINE", "RX_ENGINE_WHY", "RX_VM_FRAMELESS",
                     "RX_VM_PREFILTER", "RX_DFA_SCAN", "RX_DFA_PREFILTER"):
            for ln in text.split("\n"):
                if ln.startswith("#define %s " % name):
                    v = ln.split(None, 2)[2].strip()
                    out[name] = v.strip('"')
                    break
        return out
    finally:
        try: os.unlink(path)
        except OSError: pass


def main():
    d = json.load(open(E["IN"]))
    result = {}
    for pop in ("bench", "corpus"):
        rows = [r for r in d[pop] if int(r["best_len"]) >= 4]
        out = []
        for r in rows:
            pat = bytes.fromhex(r["pattern_hex"])
            st = stamps_for(pat)
            out.append({"id": r["id"], "best_len": r["best_len"],
                       "n_cube_ns": r["n_cube_ns"], "is_caseless": r.get("is_caseless"),
                       **st})
        result[pop] = out
        print("%s: %d qualifying, stamped" % (pop, len(out)), file=sys.stderr)
    os.makedirs(E.get("OUT", "."), exist_ok=True)
    with open(os.path.join(E.get("OUT", "."), "wf_stamps.json"), "w") as f:
        json.dump(result, f, indent=1)


if __name__ == "__main__":
    main()
