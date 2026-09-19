"""[REVW.4] item 3 acceptance proof: every 1-, 2- and 3-subset of the CLI's
14 MODE flags, in three operand shapes, run against the branch-point binary
and the working binary, compared on (returncode, stdout, stderr)."""
import itertools, subprocess, sys, os, hashlib, tempfile

REF, NEW = sys.argv[1], sys.argv[2]
RXT = sys.argv[3]
MODES = [
    ["--list-syntax"], ["--list-definitions"], ["--list-verbs"],
    ["--list-families"], ["--list-axes"], ["--list-limits"],
    ["--list-schema"], ["--explain", "\\d"], ["--count-groups"],
    ["--emit-ir"], ["--probe-ask", "claim"], ["--list-source", RXT],
    ["--source", RXT], ["--flavour", "pcre2"],
]
tmp = tempfile.mkdtemp()
OPERANDS = [
    ("bare", []),
    ("pattern", ["--", "a(b|c)"]),
    ("pattern+o", ["-o", os.path.join(tmp, "out.c"), "--", "a(b|c)"]),
]

def run(binp, args):
    try:
        r = subprocess.run([binp] + args, capture_output=True, timeout=30)
        return (r.returncode,
                hashlib.sha256(r.stdout).hexdigest()[:16],
                r.stderr.decode("utf-8", "replace").strip())
    except subprocess.TimeoutExpired:
        return ("TIMEOUT", "", "")

subsets = []
for k in (1, 2, 3):
    subsets += list(itertools.combinations(range(len(MODES)), k))

n = same = diff = 0
acc_ref = acc_new = 0
diffs = []
for combo in subsets:
    flags = [t for i in combo for t in MODES[i]]
    for oname, ops in OPERANDS:
        args = flags + ops
        a = run(REF, args); b = run(NEW, args)
        n += 1
        if a[0] == 0: acc_ref += 1
        if b[0] == 0: acc_new += 1
        if a == b: same += 1
        else:
            diff += 1
            if len(diffs) < 20: diffs.append((args, a, b))

print(f"invocations: {n}  identical(rc+stdout+stderr): {same}  DIFFERING: {diff}")
print(f"accepted (rc=0) ref: {acc_ref}   new: {acc_new}")
print(f"refused  (rc!=0) ref: {n-acc_ref}   new: {n-acc_new}")
for d in diffs:
    print("DIFF", d)
sys.exit(1 if diff else 0)
