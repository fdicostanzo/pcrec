#!/usr/bin/env python3
"""artrev.py -- [ARTREV] harness CLI (docs/dev/optloop/artrev/charter.md 3.1, S0).

  gen      NAME --pcrec BIN (--pattern P | --pattern-file F) [--flags "..."] [--prefix rx]
  twin     NAME ARM (--patch FILE | --null | --new | --seal) [--control]
  identity NAME ARM [--subject FILE]... [--corpus] [--battery N] [--block B] [--san] ...
  time     NAME --arms A,B --subject LABEL=FILE ... [--rounds 11] [--remote ubuntubudu]
  ledger   NAME

Scratch lives under build-artrev/ (gitignored).  Python 3.9-clean.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

STANDARD_ARMS = ("orig", "orig2", "null")
ARM_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,31}$")


def arm_dir(name, arm):
    return os.path.join(C.art_dir(name), "arms", arm)


is_counted = C.is_counted_arm


def pat_argv(pat_bytes):
    """argv fragment passing the pattern bytes: plain --pattern when printable, else --pattern-esc."""
    plain = all(0x20 <= b <= 0x7e for b in pat_bytes)
    if plain:
        return ["--pattern", pat_bytes.decode("ascii")]
    out = []
    for b in pat_bytes:
        if b == 0x5c:
            out.append("\\\\")
        elif b == 0x22:
            out.append('\\"')
        elif 0x20 <= b <= 0x7e:
            out.append(chr(b))
        else:
            out.append("\\x%02x" % b)
    return ["--pattern-esc", "--pattern", "".join(out)]


def parse_stamps(ctext):
    st = {}
    for m in re.finditer(r'^#define (RX_[A-Z0-9_]+) ("[^"\n]*"|[0-9A-Fa-fx]+u?(?:ULL)?|\S+)\s*$', ctext, re.M):
        st[m.group(1)] = m.group(2).strip('"')
    return st


# --------------------------------------------------------------------- gen
def cmd_gen(a):
    d = C.art_dir(a.name)
    if os.path.exists(d):
        if not a.force:
            C.die("artifact %s already exists (%s); --force replaces it AND its ledger" % (a.name, d))
        shutil.rmtree(d)
    if a.pattern_file:
        pat = open(a.pattern_file, "rb").read().rstrip(b"\n") if a.strip_nl else open(a.pattern_file, "rb").read()
    else:
        pat = a.pattern.encode("utf-8", "surrogateescape")
    cc = a.cc or C.default_cc()
    ccv = C.check_cc_is_gcc(cc)
    os.makedirs(os.path.join(d, "arms", "orig"))
    flags = a.flags.split() if a.flags else []
    if "--features" not in flags:
        flags = ["--features", "all"] + flags       # the bench puts --features all on every config
    open(os.path.join(d, "pattern.bin"), "wb").write(pat)
    gen_cmd = [os.path.abspath(a.pcrec), "-p", a.prefix] + flags + ["-o", os.path.join(d, "artifact.c")] + pat_argv(pat)
    r = C.run(gen_cmd)
    if r.returncode != 0:
        shutil.rmtree(d)
        C.die("pcrec generation failed (rc %d): %s\n%s" % (r.returncode, " ".join(gen_cmd), r.stderr[-800:]))
    for f in ("artifact.c", "artifact.h"):
        if not os.path.exists(os.path.join(d, f)):
            C.die("pcrec did not write %s" % f)
    ctext = open(os.path.join(d, "artifact.c")).read()
    htext = open(os.path.join(d, "artifact.h")).read()
    m = re.search(r"#define PCREC_RX_ABI_H (\d+)", htext)
    P = a.prefix.upper()
    ncaps = re.search(r"#define %s_NCAPS (\d+)" % P, htext)
    fsz = re.search(r"#define %s_RESUME_FRAME_SIZE (\d+)" % P, htext)
    have_in = bool(re.search(r"#define %s_BUFFER_ALIGN\b" % P, htext))
    pin = a.pin
    if not pin:
        g = C.run(["git", "-C", os.path.dirname(os.path.abspath(a.pcrec)), "rev-parse", "HEAD"])
        pin = g.stdout.strip() if g.returncode == 0 else "unknown"
    stamps = parse_stamps(ctext)
    meta = {
        "name": a.name, "pattern_hex": pat.hex(), "pattern_text": pat.decode("utf-8", "replace"),
        "prefix": a.prefix, "pcrec_flags": flags, "pcrec_bin": os.path.abspath(a.pcrec),
        "pcrec_sha256": C.sha256_file(a.pcrec), "pin": pin, "abi": int(m.group(1)) if m else None,
        "ncaps": int(ncaps.group(1)) if ncaps else None, "have_in": have_in,
        "engine": stamps.get("RX_ENGINE"), "stamps": {k: v for k, v in stamps.items() if k.startswith("RX_") and len(v) < 80},
        "cc": cc, "cc_version": ccv, "base_flags": C.BASE_FLAGS, "gen_cmd": gen_cmd,
        "artifact_sha256": C.sha256_file(os.path.join(d, "artifact.c")),
        "generated": __import__("time").strftime("%Y-%m-%dT%H:%M:%S"),
    }
    for arm in ("orig", "orig2"):
        os.makedirs(arm_dir(a.name, arm), exist_ok=True)
        for f in ("artifact.c", "artifact.h"):
            shutil.copy(os.path.join(d, f), os.path.join(arm_dir(a.name, arm), f))
    # the asm the reviewer reads: the SAME TU, the SAME fixed flags, `-S`
    asm = os.path.join(d, "artifact.s")
    cmd = [cc] + C.BASE_FLAGS + ["-S", "-I" + arm_dir(a.name, "orig"), "-DARTREV_PFX=%s" % a.prefix,
                                   "-DARTREV_PFXU=%s" % P] + (["-DARTREV_HAVE_IN=1"] if have_in else []) + \
          [os.path.join(C.HERE, "shim.c"), "-o", asm]
    meta["asm_cmd"] = cmd
    r = C.run(cmd)
    if r.returncode != 0:
        C.die("asm compile failed: %s\n%s" % (" ".join(cmd), r.stderr[-1200:]))
    meta["compile_cmd_template"] = [cc] + C.BASE_FLAGS + ["-I<armdir>", "-DARTREV_PFX=%s" % a.prefix,
                                                           "-DARTREV_PFXU=%s" % P] + \
        (["-DARTREV_HAVE_IN=1"] if have_in else []) + ["shim.c", "<driver>.c", "-o", "<exe>"]
    C.save_meta(a.name, meta)
    # header comment of the fixed record, human-readable
    with open(os.path.join(d, "GENERATION.txt"), "w") as f:
        f.write("artifact   %s\npin        %s\nabi        %s\nengine     %s\ngcc        %s\n"
                "pcrec bin  %s (sha256 %s)\ngen line   %s\nasm line   %s\ncompile    %s\n" % (
                    a.name, pin, meta["abi"], meta["engine"], ccv, meta["pcrec_bin"], meta["pcrec_sha256"],
                    " ".join(gen_cmd), " ".join(cmd), " ".join(meta["compile_cmd_template"])))
    C.ledger_append(a.name, "gen", "-", 0, False, "OK", meta["artifact_sha256"],
                    "pin=%s abi=%s gcc=%s" % (pin, meta["abi"], ccv))
    print("generated %s: engine=%s abi=%s ncaps=%s have_in=%s  %s lines, %s asm lines" % (
        a.name, meta["engine"], meta["abi"], meta["ncaps"], have_in,
        ctext.count("\n"), sum(1 for _ in open(asm))))
    print("dir", d)


# -------------------------------------------------------------------- twin
NULL_TEXT = ("\n/* [ARTREV] null twin: a semantics-free textual change (an unused static) */\n"
             "static int artrev_null_unused(int x) { return x + 1; }\n")


def finish_arm(a, meta, arm, orig_text, rev, counted, how, patch_text=None):
    ad = arm_dir(a.name, arm)
    twin_text = open(os.path.join(ad, "artifact.c")).read()
    hdr_ok = open(os.path.join(ad, "artifact.h")).read() == open(os.path.join(C.art_dir(a.name), "artifact.h")).read()
    extras = sorted(set(os.listdir(ad)) - {"artifact.c", "artifact.h", "build", "rev"})
    bad = C.reject_check(orig_text, twin_text)
    status, detail = "APPLIED" if how != "seal" else "SEALED", ""
    if not hdr_ok:
        bad.append(("artifact.h changed (the public ABI must be preserved)", ""))
    if extras:
        bad.append(("stray files in the arm dir: %s" % ",".join(extras), ""))
    sha = C.sha256_file(os.path.join(ad, "artifact.c"))
    nchg = len(C.added_lines(orig_text, twin_text))
    if bad:
        status = "REJECTED"
        detail = "; ".join("%s: %s" % b for b in bad)[:300]
    C.ledger_append(a.name, "twin", arm, rev, counted, status, sha, "%s +%d lines %s" % (how, nchg, detail))
    if bad:
        shutil.rmtree(ad)
        sys.stderr.write("REJECTED twin %s rev %d of %s -- the charter forbids:\n" % (arm, rev, a.name))
        for why, t in bad:
            sys.stderr.write("  - %s  %s\n" % (why, t))
        sys.exit(4)
    pdir = os.path.join(C.art_dir(a.name), "twins")
    os.makedirs(pdir, exist_ok=True)
    patch_text = patch_text if patch_text is not None else make_patch(orig_text, twin_text)
    open(os.path.join(pdir, "%s.r%d.patch" % (arm, rev)), "w").write(patch_text)
    open(os.path.join(pdir, "%s.patch" % arm), "w").write(patch_text)
    open(os.path.join(ad, "rev"), "w").write(str(rev))
    print("%s twin %s rev %d of %s: %d added lines, sha %s%s" % (
        status, arm, rev, a.name, nchg, sha[:12], "" if counted else "  (uncounted: control/null)"))


def make_patch(orig_text, twin_text):
    import difflib
    return "".join(difflib.unified_diff(orig_text.splitlines(True), twin_text.splitlines(True),
                                        "a/artifact.c", "b/artifact.c"))


def cmd_twin(a):
    meta = C.load_meta(a.name)
    arm = a.arm
    if not ARM_RE.match(arm) or arm in ("orig", "orig2"):
        C.die("bad arm name %r (letters/digits/_, not orig/orig2)" % arm)
    if arm == "null":
        a.null = True
    counted = is_counted(arm) and not a.control
    base = C.art_dir(a.name)
    orig_text = open(os.path.join(base, "artifact.c")).read()
    if a.new:
        ad = arm_dir(a.name, arm)
        if os.path.exists(ad):
            C.die("arm dir %s exists" % ad)
        os.makedirs(ad)
        for f in ("artifact.c", "artifact.h"):
            shutil.copy(os.path.join(base, f), os.path.join(ad, f))
        print("arm dir ready for hand edits: %s/artifact.c  (then: twin %s %s --seal)" % (ad, a.name, arm))
        return
    rows = C.ledger_rows(a.name)
    rev = C.revs_of(rows, arm) + 1
    C.check_twin_bound(a.name, arm, counted)
    ad = arm_dir(a.name, arm)
    if a.seal:
        if not os.path.exists(os.path.join(ad, "artifact.c")):
            C.die("no arm dir for %s; run `twin %s %s --new` first" % (arm, a.name, arm))
        finish_arm(a, meta, arm, orig_text, rev, counted, "seal")
        return
    if os.path.exists(ad):
        shutil.rmtree(ad)
    os.makedirs(ad)
    for f in ("artifact.c", "artifact.h"):
        shutil.copy(os.path.join(base, f), os.path.join(ad, f))
    if a.null:
        with open(os.path.join(ad, "artifact.c"), "a") as f:
            f.write(NULL_TEXT)
        finish_arm(a, meta, arm, orig_text, rev, False, "null")
        return
    if not a.patch:
        C.die("one of --patch/--null/--new/--seal is required")
    ptxt = open(a.patch).read()
    r = C.run(["patch", "-s", "-p1", "-d", ad], input=ptxt)
    for junk in ("artifact.c.orig", "artifact.c.rej"):
        jp = os.path.join(ad, junk)
        if os.path.exists(jp):
            os.remove(jp)
    if r.returncode != 0:
        C.ledger_append(a.name, "twin", arm, rev, counted, "NOAPPLY", "", (r.stdout + r.stderr)[:200])
        shutil.rmtree(ad)
        C.die("patch does not apply to the pinned artifact: %s" % (r.stdout + r.stderr)[:400], 4)
    finish_arm(a, meta, arm, orig_text, rev, counted, "patch", patch_text=ptxt)


# ------------------------------------------------------------------ ledger
def cmd_ledger(a):
    rows = C.ledger_rows(a.name)
    leads = C.counted_leads(rows)
    print("artifact %s: %d/%d leads carried to a twin: %s" % (a.name, len(leads), C.MAX_LEADS, ",".join(leads) or "-"))
    for l in leads:
        rv = C.revs_of(rows, l)
        revs = sorted({int(r["rev"]) for r in rows if r["kind"] == "time" and r["arm"] == l} | {rv})
        print("  %-10s revisions %d/%d; timing runs per revision: %s" % (
            l, rv, C.MAX_REVS, ", ".join("r%d:%d/%d" % (x, C.timings_of(rows, l, x), C.MAX_TIMINGS) for x in revs if x)))
    print("ledger:", C.ledger_path(a.name), "(%d rows)" % len(rows))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    g = sp.add_parser("gen")
    g.add_argument("name")
    g.add_argument("--pcrec", required=True)
    g.add_argument("--pattern")
    g.add_argument("--pattern-file")
    g.add_argument("--strip-nl", action="store_true", help="strip ONE trailing newline of --pattern-file")
    g.add_argument("--flags", default="", help='pcrec flags, e.g. "--no-captures -i"; --features all is added unless given')
    g.add_argument("--prefix", default="rx")
    g.add_argument("--pin", help="the main sha the pcrec binary was built at (default: git rev-parse next to the binary)")
    g.add_argument("--cc")
    g.add_argument("--force", action="store_true")
    t = sp.add_parser("twin")
    t.add_argument("name")
    t.add_argument("arm")
    t.add_argument("--patch")
    t.add_argument("--null", action="store_true")
    t.add_argument("--new", action="store_true")
    t.add_argument("--seal", action="store_true")
    t.add_argument("--control", action="store_true", help="a self-test control: not counted toward the bounds")
    i = sp.add_parser("identity")
    i.add_argument("name")
    i.add_argument("arm")
    i.add_argument("--subject", action="append", default=[], help="a supplied subject file (find-all walk + point cases)")
    i.add_argument("--corpus", action="store_true", help="every tests/**/*.rxt case for the pattern")
    i.add_argument("--battery", type=int, default=3000, help="generated subjects (0 disables)")
    i.add_argument("--block", type=int, action="append", default=[], help="a block size the twin introduces (lengths around it)")
    i.add_argument("--seed", type=int, default=1)
    i.add_argument("--san", action="store_true", help="build both arms with -fsanitize=address,undefined")
    i.add_argument("--pcre2-sample", type=int, default=1500, help="cases checked against libpcre2 (0 disables)")
    i.add_argument("--match-example", action="append", default=[], help="a string known to match (planted in the battery)")
    i.add_argument("--tests-dir")
    i.add_argument("--shrunk-budgets", default="8:64,64:1024,2000:40000",
                   help="STEPS:WORK pairs the shrunken-resource phase compiles both arms with (identity.DEFAULT_BUDGETS)")
    i.add_argument("--strict-giveup", action="store_true",
                   help="shrunk phase: ALSO fail a twin that answers where the original gave up (default: allowed iff equal to libpcre2)")
    i.add_argument("--skip-shrunk", action="store_true", help="iteration speed only: logs PASS-PARTIAL, which `time` refuses")
    i.add_argument("--skip-window", action="store_true", help="iteration speed only: logs PASS-PARTIAL, which `time` refuses")
    tm = sp.add_parser("time")
    tm.add_argument("name")
    tm.add_argument("--arms", default="orig,orig2,null", help="comma list; orig is always included first")
    tm.add_argument("--subject", action="append", default=[], help="LABEL=FILE (cell subject, dense, sparse...)")
    tm.add_argument("--rounds", type=int, default=11)
    tm.add_argument("--wall", type=int, default=600, help="watchdog wall seconds (default 10 min)")
    tm.add_argument("--rss-kb", type=int, default=2000000)
    tm.add_argument("--load-max", type=float, default=None)
    tm.add_argument("--max-load-wait", type=int, default=300)
    tm.add_argument("--remote", help="ubuntubudu: ship the arms and time there (08:00-19:00 local only)")
    tm.add_argument("--dry-run", action="store_true", help="remote: print the commands and exit")
    tm.add_argument("--gate-override", action="store_true", help="SELFTEST ONLY (ARTREV_SELFTEST=1): skip the load gate")
    tm.add_argument("--hour-override", type=int, help="SELFTEST ONLY: pretend the local hour is H (remote window check)")
    tm.add_argument("--pads", default="", help="LAYOUT CONTROL: code-offset pads in bytes (>=4 multiples of 16, e.g. 16,32,48,64); "
                    "also times --pad-arms at each pad in the same interleaved rounds (timing.py docstring)")
    tm.add_argument("--pad-arms", default="", help="comma list of arms to pad (orig is always included); needs --pads")
    tm.add_argument("--tag", default="")
    raw = sp.add_parser("_rawtime")
    raw.add_argument("name")
    raw.add_argument("--arms", required=True)
    raw.add_argument("--subject", action="append", required=True)
    raw.add_argument("--rounds", type=int, default=11)
    raw.add_argument("--load-max", type=float, required=True)
    raw.add_argument("--max-load-wait", type=int, default=300)
    raw.add_argument("--gate-override", action="store_true")
    raw.add_argument("--out", required=True)
    raw.add_argument("--root")
    l = sp.add_parser("ledger")
    l.add_argument("name")
    a = ap.parse_args()
    if a.cmd == "gen":
        if bool(a.pattern) == bool(a.pattern_file):
            C.die("exactly one of --pattern / --pattern-file")
        cmd_gen(a)
    elif a.cmd == "twin":
        cmd_twin(a)
    elif a.cmd == "ledger":
        cmd_ledger(a)
    elif a.cmd == "identity":
        import identity
        sys.exit(identity.cmd_identity(a))
    elif a.cmd == "time":
        import timing
        sys.exit(timing.cmd_time(a))
    elif a.cmd == "_rawtime":
        import timing
        sys.exit(timing.cmd_rawtime(a))


if __name__ == "__main__":
    main()
