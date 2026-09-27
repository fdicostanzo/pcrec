#!/usr/bin/env python3
"""gen_corpus.py -- the SYNTHETIC CORPUS GENERATOR for `[FINDINGS]`'s `log`
bundle sourcing half (docs/design/findings/design.md finding 9, D123
addendum 6 (Q9), D123-8 item 6, [r2 A-4]).

WHY THIS EXISTS: the design's own finding 9 measured that the obvious real
source for a "log_lines" class -- loghub's HDFS_2k.log
(https://github.com/logpai/loghub) -- carries a licence that is "freely
available for research or academic work" and NOT a clearly permissive
REDISTRIBUTION licence (R29). Frank's ruling (D123-8 item 6) is: one
sourcing-lane attempt for a permissively licensed, stably retrievable real
log corpus; failing that, a `fidelity synthesized` corpus, labelled as such,
with its generator and seed committed.

THE SOURCING ATTEMPT (lane `findb5src`, 2026-09-27, ~30 minutes): beyond the
design's own already-recorded loghub finding, this lane separately checked
(a) loghub's own LICENSE file directly (same "research or academic work"
text, SPDX `NOASSERTION`/`other`, confirmed via the GitHub API rather than
trusted from memory), (b) whether elastic/examples (the `weblog` source)
ships a second, non-web-request log sample under the same Apache-2.0 grant
-- it has `cef`/`nginx_logs`/`nginx_json_logs`/`twitter`, all still
web/HTTP-adjacent rather than an application/system log's character, and
reusing the same repository as both `log` and `weblog` sources would also
weaken the two classes' independence (RUNEST's whole point is to test the
model against ends of the character SPECTRUM, not one source twice) --
declined without vendoring, (c) Apache Hadoop's own test-resource tree
(`hadoop-hdfs-project/.../src/test/resources`, Apache-2.0), which held no
committed sample log dump (config files and scripts only, checked directly
via the GitHub API), and (d) a Zenodo search for an independently
CC-licensed mirror of loghub's data, which returned nothing usable within
this lane's time box. No permissively licensed, stably retrievable real
`log_lines`-class corpus was found. Per the ruling, this generator
substitutes.

WHAT IT GENERATES: lines matching the STRUCTURAL SHAPE of a
Hadoop/HDFS-DataNode-style distributed-system log -- `DATE TIME PID LEVEL
component.path: message` -- with invented (not copied) component names,
message templates and a level mix (INFO/WARN/ERROR ratio) chosen to be
plausible for this log family. NO TEXT IS COPIED from any real log corpus.
This lane separately inspected a transient, NEVER-COMMITTED copy of
loghub's HDFS_2k.log (fetched to /tmp, deleted before this lane's first
commit) ONLY to calibrate structural ratios that matter for STATISTICAL
fidelity -- the INFO:WARN:ERROR level mix, the rough share of lines that
carry an IPv4:port pair, a block-identifier-shaped token, or a file path --
never to copy field values, message text or component names. The synthetic
component names, message templates, hostnames and identifiers below are
this generator's own invention.

DETERMINISM (R27c's own discipline, applied here too): one integer SEED,
below, feeds `random.Random(SEED)` exclusively -- no wall clock, no
`os.urandom`. Re-running this script reproduces the committed
`synthetic_log_lines.txt` byte for byte. A seed or template change is a
version bump (`third_party/README.md`'s "one directory per source, version
in the name" rule, applied to a generated source exactly as to a fetched
one) -- bump the directory to `synth-log-lines-v2` rather than editing this
one in place.

    python3 third_party/synth-log-lines-v1/gen_corpus.py            # writes
    python3 third_party/synth-log-lines-v1/gen_corpus.py --check    # verifies

Output: `synthetic_log_lines.txt`, beside this file, committed.
"""
from __future__ import annotations

import argparse
import hashlib
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "synthetic_log_lines.txt"

SEED = 20260927  # the date this lane ran; a fixed, arbitrary, documented pin
TARGET_BYTES = 1_000_000  # matches `weblog`'s committed sample size (design.md
                           # §8.3 states bundle byte estimates against this
                           # order of magnitude; consistency lets the two
                           # first-shipped bundles' freq/cpfreq/bigram numbers
                           # sit at a comparable statistical weight)

# ---------------------------------------------------------------------------
# Invented vocabulary. None of these strings appear in loghub's HDFS_2k.log
# (or in any other real corpus this generator was informed by) -- they are
# built to be STRUCTURALLY the same shape (dotted Java-style package path,
# optional `$InnerClass`) without being the same names.
# ---------------------------------------------------------------------------

COMPONENTS = [
    "svc.BlockKeeper",
    "svc.BlockKeeper$AckHandler",
    "svc.ChunkStore",
    "svc.ChunkStore$Receiver",
    "svc.NodeRegistry",
    "svc.ReplicaScanner",
    "svc.LeaseMonitor",
]

# Weighted so the busiest two components dominate, as in a real DataNode log
# (PacketResponder + FSNamesystem together carry most lines).
COMPONENT_WEIGHTS = [3, 30, 4, 28, 18, 2, 1]

WORDS_FRAGMENT = [
    "temp", "stage", "part", "job", "task", "attempt", "batch", "shard",
]

HOSTS_OCTET_LOW, HOSTS_OCTET_HIGH = 10, 10  # keep the private 10.x.x.x shape


def rand_ip(rng: random.Random) -> str:
    return f"10.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"


def rand_chunk_id(rng: random.Random) -> str:
    # A large signed-looking integer token, the shape a hashed replica
    # identifier takes (sometimes negative, mirroring a 64-bit hash's sign
    # bit going either way -- structurally significant: it puts a literal
    # '-' inside an otherwise all-digit token, which matters for byte-level
    # fidelity).
    n = rng.randint(10**17, 10**19)
    if rng.random() < 0.5:
        n = -n
    return f"chk_{n}"

def rand_path(rng: random.Random) -> str:
    frag = rng.choice(WORDS_FRAGMENT)
    jobid = rng.randint(200000000000, 200999999999)
    part = rng.randint(0, 999)
    return f"/user/svc/{frag}/_tmp/_task_{jobid}_m_{part:06d}_0/part-{part:05d}"


def gen_line(rng: random.Random, date: str, t: int) -> str:
    hh, rem = divmod(t, 3600)
    mm, ss = divmod(rem, 60)
    time_s = f"{hh:02d}{mm:02d}{ss:02d}"
    pid = rng.randint(10, 9999)

    roll = rng.random()
    if roll < 0.955:
        level = "INFO"
    elif roll < 0.995:
        level = "WARN"
    else:
        level = "ERROR"

    comp = rng.choices(COMPONENTS, weights=COMPONENT_WEIGHTS, k=1)[0]
    chunk = rand_chunk_id(rng)
    ip = rand_ip(rng)
    size = rng.choice([67108864, rng.randint(1_000_000, 67_108_864)])

    if comp.endswith("AckHandler"):
        msg = f"AckHandler {rng.randint(0,2)} for chunk {chunk} terminating"
    elif comp == "svc.ChunkStore" and rng.random() < 0.5:
        msg = (f"REPL* Registry.addStoredChunk: chunkMap updated: "
               f"{ip}:50010 is added to {chunk} size {size}")
    elif comp == "svc.ChunkStore":
        if rng.random() < 0.5:
            msg = f"Registry.allocateChunk: {rand_path(rng)}. {chunk}"
        else:
            msg = f"REPL* Registry.delete: {chunk} is added to invalidSet of {ip}:50010"
    elif comp.endswith("Receiver"):
        if rng.random() < 0.5:
            msg = (f"Receiving chunk {chunk} src: /{ip}:{rng.randint(1024,65535)} "
                   f"dest: /{ip}:50010")
        else:
            msg = f"Received chunk {chunk} of size {size} from /{ip}"
    elif comp == "svc.NodeRegistry":
        msg = f"Deleting chunk {chunk} file /mnt/store/data/current/subdir{rng.randint(1,64)}/{chunk}"
    elif comp == "svc.LeaseMonitor":
        msg = f"Lease recovery triggered for {rand_path(rng)}"
    else:  # ReplicaScanner
        msg = f"Verification succeeded for {chunk}"

    if level == "WARN":
        msg = (f"{ip}:50010:Got exception while serving {chunk} "
               f"to /{rand_ip(rng)}:")
    elif level == "ERROR":
        msg = (f"{comp.split('$')[0]}: Failed to process {chunk}: "
               f"java.io.IOException: connection reset by peer")

    return f"{date} {time_s} {pid} {level} {comp}: {msg}"


def generate(seed: int, target_bytes: int) -> bytes:
    rng = random.Random(seed)
    dates = ["260924", "260925", "260926"]  # three synthetic dates, YYMMDD
    lines = []
    total = 0
    date_i = 0
    t = 0
    while total < target_bytes:
        date = dates[date_i % len(dates)]
        t += rng.randint(1, 45)
        if t >= 86400:
            t -= 86400
            date_i += 1
            date = dates[date_i % len(dates)]
        line = gen_line(rng, date, t)
        lines.append(line)
        total += len(line) + 1  # + newline
    text = "\n".join(lines) + "\n"
    # Trim to the exact target (deterministic: cuts at a line boundary at or
    # just past the target, then hard-trims and re-adds a final newline so
    # the byte count is exactly reproducible across re-runs).
    data = text.encode("ascii")
    if len(data) > target_bytes:
        data = data[:target_bytes]
        nl = data.rfind(b"\n")
        if nl > 0:
            data = data[: nl + 1]
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                     help="exit 1 if the committed output is stale")
    args = ap.parse_args()

    data = generate(SEED, TARGET_BYTES)

    if args.check:
        if not OUT.exists():
            print(f"MISSING: {OUT}", file=sys.stderr)
            return 1
        committed = OUT.read_bytes()
        if committed != data:
            print(f"STALE: {OUT} does not match a fresh run "
                  f"(seed={SEED}, target_bytes={TARGET_BYTES})", file=sys.stderr)
            print(f"  committed: {len(committed)} bytes, sha256="
                  f"{hashlib.sha256(committed).hexdigest()}", file=sys.stderr)
            print(f"  fresh:     {len(data)} bytes, sha256="
                  f"{hashlib.sha256(data).hexdigest()}", file=sys.stderr)
            return 1
        print(f"OK: {OUT} matches (seed={SEED}, {len(data)} bytes, "
              f"sha256={hashlib.sha256(data).hexdigest()})")
        return 0

    OUT.write_bytes(data)
    print(f"wrote {OUT} ({len(data)} bytes, "
          f"sha256={hashlib.sha256(data).hexdigest()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
