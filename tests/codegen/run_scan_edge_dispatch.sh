#!/usr/bin/env bash
# tests/codegen/run_scan_edge_dispatch.sh — [OPT-EDGE] STEP 1: the scan edge
# costs the loop's GENERIC PATH nothing, held to the object code.
#
# STATUS: DRAFT, written 2026-09-03 by lane edge1 under the bench's box hold,
# AND IT IS RED ON TWO OF ITS FOUR WITNESSES BY CONSTRUCTION — the measurement
# cannot reach them, and it says INCONCLUSIVE and FAILS rather than passing.
# It has been run against single artifacts only. It has NOT been run inside
# `make test`, it is NOT wired into tests/codegen/run_codegen_tests.sh, it has
# no make target, and it carries NO sabotage row yet. §6 lists what is owed,
# and item 1 is the measurement's own gap. Do not wire it in as it stands.
#
# =========================================================================
# WHAT IS BEING DEFENDED
# =========================================================================
# [OPT-5] emitted every scan edge as its own `if (state == HEAD && more &&
# class_test)` block ON THE SCAN LOOP'S GENERIC PATH. A machine with N edges
# therefore paid N compares PER BYTE whether or not any edge could fire, and
# the bench sized that at x1.089 on iso-ts (8 edges in `rx_search`) against a
# `-fno-scan-edge` arm.
#
# [OPT-EDGE] STEP 1 folds the edge test into the ONE state test the loop
# already had. The claim this file defends is not "the emitter writes the new
# shape" — that is a text fact any grep can see and any rewrite can break
# without breaking the property. It is:
#
#     THE SCAN LOOP'S GENERIC PATH IS NO LONGER, IN INSTRUCTIONS, THAN THE
#     SAME PATTERN'S LOOP WITH THE WHOLE TRANSFORM DENIED.
#
# =========================================================================
# THE CONTROL DOES NOT SHARE A SOURCE WITH WHAT IT CONTROLS
# =========================================================================
# docs/dev/learnings.md §3, memory `pcrec-check-design-lessons`. The reference
# arm is the SAME pattern compiled `-fno-scan-edge`, and that is a real
# control rather than a second reading of the subject: the denial is at the
# PASS (`src/opt/scanedge.c` returns before it annotates anything), so the
# reference machine has no heads, no renumbering, no `is_stop` accessor and no
# edge path — it is the pre-[OPT-5] loop. A sabotage that puts the per-edge
# compares back on the generic path moves the SUBJECT arm and leaves the
# REFERENCE arm untouched, so this check goes red. A sabotage that damages
# both arms equally is not expressible here, because the reference arm
# contains none of the mechanism.
#
# =========================================================================
# THE MEASURABLE IS A CYCLE LENGTH, NOT A TEXT PATTERN
# =========================================================================
# Three earlier checks in this tree were PRESENCE-BY-TEXT detectors and all
# three went vacuous when the text moved for an unrelated reason ([CC-DIFF]
# STEP 1's report §5 lists them). So this file reads OBJECT CODE:
#
#   1. `objdump -dr` the compiled artifact and take `rx_search`.
#   2. Find the instruction that loads `<prefix>_forward_byte_class` — the
#      byte-class table, which every DFA scan of either engine emits
#      unconditionally and which no fold or axis removes (the same
#      discriminator `run_dfa_uniform_fold.sh` uses, and for the same reason:
#      a check that selected its subject by reading a macro would be reading
#      the thing it is checking). The table is a FUNCTION-LOCAL static, so its
#      relocation names a SECTION (`.rodata+0xb1c`) and not the table; `nm`
#      supplies the symbol's own address and the two are matched through the
#      `R_X86_64_PC32` addend of -4. That resolution is the one fragile step
#      in this file and §6 says so.
#   3. Build the function's control-flow graph and take the SHORTEST CYCLE
#      through that instruction. The shortest way round the scan loop is by
#      construction the path that takes no edge, no prefilter and no skip:
#      the GENERIC PATH. Its length in instructions is the number.
#
# The cycle is found by breadth-first search over the CFG, so it does not
# assume the loop body is laid out contiguously — which it is not: gcc splits
# the [OPT-EDGE] loop's cold edge path out of line and the hot blocks end up
# at higher addresses than the branch that reaches them.
#
# =========================================================================
# THE VACUITY GUARD
# =========================================================================
# [MECH-REACH]'s lesson — a witness that stopped reaching its site. Every
# witness below must actually CARRY at least two forward scan edges, and this
# file FAILS LOUDLY if one does not, rather than passing on an artifact where
# the mechanism is absent. The edge count is read from the emitted C's own
# `[OPT-5] SCAN EDGE` markers; if that marker is ever renamed this check goes
# red rather than vacuous, which is the direction it must fail in.

set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PCREC="${PCREC:-$ROOT/build/pcrec}"
CC="${CC:-gcc}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

fails=0
ok()  { printf '  ok   %s\n' "$*"; }
bad() { printf '  FAIL %s\n' "$*"; fails=$((fails + 1)); }

# ---- the witnesses -------------------------------------------------------
# Each must carry >= 2 scan edges in its FORWARD machine. They are the bench's
# own loglines patterns plus one synthetic two-chain shape, so the population
# this check speaks for is the population [OPT-EDGE] was chartered against.
witness_names=(iso-ts http-5xx two-chain digits-then-letters)
witness_pats=(
  '\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d{1,6})?(?:Z|[+-]\d{2}:?\d{2})?'
  '(?:GET|POST|PUT|PATCH|DELETE|HEAD) [^ "]+ HTTP/1\.[01]" 5[0-9]{2}\b'
  '[a-z]{2}[0-9]{2}'
  '\d{2}[.]\d{2}'
)

# ---- the cycle measurement ----------------------------------------------
# The measurement is a python program rather than awk because it is a
# graph search; it is written out once at startup so that objdump's output
# can be PIPED into it (a heredoc on the same command would take stdin).
CYCLE_PY="$WORK/cycle.py"
cat > "$CYCLE_PY" <<'PY'
import re, sys, collections, subprocess
anchor, obj = sys.argv[1], sys.argv[2]

# The table is a function-local static: `nm` spells it `<name>.<n>` and the
# relocation names its SECTION plus an offset. Resolve by address.
sym_addrs = []
for line in subprocess.run(['nm', obj], capture_output=True, text=True).stdout.splitlines():
    f = line.split()
    if len(f) == 3 and (f[2] == anchor or f[2].startswith(anchor + '.')):
        sym_addrs.append(int(f[0], 16))
if not sym_addrs:
    print('ERR symbol %s not in %s' % (anchor, obj)); sys.exit(2)

fn, insns, relocs = None, [], {}
line_re = re.compile(r'^\s+([0-9a-f]+):\t(.*)$')
for raw in sys.stdin:
    m = re.match(r'^[0-9a-f]+ <([^>]+)>:', raw)
    if m:
        fn = m.group(1)
        continue
    if fn != 'rx_search':
        continue
    m = line_re.match(raw.rstrip('\n'))
    if not m:
        # a relocation line belongs to the instruction just emitted
        if 'R_X86_64' in raw and insns:
            relocs.setdefault(insns[-1][0], []).append(raw.split()[-1])
        continue
    addr = int(m.group(1), 16)
    body = m.group(2).strip()
    parts = body.split(None, 1)
    mn = parts[0]
    ops = parts[1] if len(parts) > 1 else ''
    ops = ops.split('#', 1)[0].rstrip()   # drop objdump's target annotation
    tgt = None
    if mn[0] == 'j' or mn.startswith('loop'):
        t = re.match(r'^([0-9a-f]+)\b', ops)
        if t:
            tgt = int(t.group(1), 16)
    uncond = (mn == 'jmp' or mn == 'jmpq')
    term = mn in ('ret', 'retq', 'hlt', 'ud2')
    insns.append((addr, mn, tgt, uncond, term, ops))

if not insns:
    print('ERR no rx_search'); sys.exit(2)

idx = {a: i for i, (a, *_ ) in enumerate(insns)}
def hits(target):
    m = re.match(r'^\.[A-Za-z0-9_.]+\+0x([0-9a-f]+)$', target)
    if not m:
        return target == anchor or target.startswith(anchor + '.')
    v = int(m.group(1), 16)
    # R_X86_64_PC32 on a rip-relative lea carries an addend of -4.
    return any(v == a or v + 4 == a for a in sym_addrs)

anchors = [a for a, names in relocs.items() if any(hits(n) for n in names)]
if not anchors:
    print('ERR anchor %s not reached from rx_search' % anchor); sys.exit(2)

succ = collections.defaultdict(list)
for i, (a, mn, tgt, uncond, term, ops) in enumerate(insns):
    if term:
        continue
    if tgt is not None and tgt in idx:
        succ[i].append(idx[tgt])
    if not uncond and i + 1 < len(insns):
        succ[i].append(i + 1)

best = None
for a in anchors:
    s = idx[a]
    dist = {}
    q = collections.deque()
    for n in succ[s]:
        if n not in dist:
            dist[n] = 1
            q.append(n)
    while q:
        u = q.popleft()
        if u == s:
            break
        for n in succ[u]:
            if n not in dist:
                dist[n] = dist[u] + 1
                q.append(n)
    if s in dist and (best is None or dist[s] < best):
        best = dist[s]
if best is None:
    print('INCONCLUSIVE the table load is not on a cycle (gcc hoisted it)'); sys.exit(3)
print(best)
PY

cycle_len() {   # $1 = .o file, $2 = symbol to anchor on
    "${OBJDUMP:-objdump}" -dr --no-show-raw-insn "$1" | python3 "$CYCLE_PY" "$2" "$1"
}

echo "[OPT-EDGE] scan-edge dispatch: the generic path against the denied arm"
echo

for i in "${!witness_names[@]}"; do
    name="${witness_names[$i]}"; pat="${witness_pats[$i]}"
    d="$WORK/$name"; mkdir -p "$d/on" "$d/off"

    "$PCREC" --features all -p rx -o "$d/on/a.c"  "$pat" >/dev/null 2>&1 || {
        bad "$name: pcrec refused the pattern"; continue; }
    "$PCREC" --features all -p rx -o "$d/off/a.c" -fno-scan-edge "$pat" >/dev/null 2>&1 || {
        bad "$name: pcrec refused the pattern under -fno-scan-edge"; continue; }

    # THE VACUITY GUARD. The witness must reach the mechanism.
    nedge=$(grep -c '\[OPT-5\] SCAN EDGE' "$d/on/a.c" || true)
    if [ "$nedge" -lt 2 ]; then
        bad "$name: carries $nedge scan edges, needs >= 2 — this witness no longer reaches the mechanism (replace it, do not lower the bar)"
        continue
    fi
    noff=$(grep -c '\[OPT-5\] SCAN EDGE' "$d/off/a.c" || true)
    if [ "$noff" -ne 0 ]; then
        bad "$name: the -fno-scan-edge arm carries $noff scan edges — the reference arm is not a reference"
        continue
    fi

    for arm in on off; do
        ( cd "$d/$arm" && "$CC" -O2 -std=gnu11 -w -c -o a.o a.c ) || {
            bad "$name/$arm: the artifact did not compile"; continue 2; }
    done

    con=$(cycle_len "$d/on/a.o"  rx_forward_byte_class)
    coff=$(cycle_len "$d/off/a.o" rx_forward_byte_class)
    case "$con$coff" in *ERR*|*INCONCLUSIVE*) bad "$name: $con / $coff"; continue;; esac

    if [ "$con" -le "$coff" ]; then
        ok "$name: generic path $con insns with $nedge edges, $coff denied — the edges cost the hot loop nothing"
    else
        bad "$name: generic path $con insns with $nedge edges against $coff denied — the edges are back on the hot path"
    fi
done

echo
if [ "$fails" -eq 0 ]; then echo "scan-edge dispatch: PASS"; else echo "scan-edge dispatch: $fails FAILED"; fi
exit $(( fails ? 1 : 0 ))

# =========================================================================
# §6 WHAT IS OWED BEFORE THIS IS A GATE (lane edge1, 2026-09-03)
# =========================================================================
# 1. **THE MEASUREMENT REACHES ONLY HALF ITS WITNESSES, AND THAT IS THE ITEM
#    TO FIX FIRST.** The anchor is the instruction that LOADS the byte-class
#    table's address, and gcc routinely HOISTS that load out of the loop — on
#    `http-5xx` and `[a-z]{2}[0-9]{2}` it parks the pointer in a callee-saved
#    register in the prologue, so the anchor is not on any cycle and this file
#    reports INCONCLUSIVE (and fails). Three repairs were tried and MEASURED,
#    and all three are recorded here so they are not re-tried blind:
#      (a) follow the anchor's REGISTER to any instruction mentioning it — the
#          register is scratch (%rcx on iso-ts) and the shortest cycle found is
#          the PREFILTER's inner loop, reading 11 where the truth is 15;
#      (b) the same, restricted to memory DEREFERENCES through that register —
#          same failure, same 11;
#      (c) compile the measurement object `-fno-move-loop-invariants` so the
#          load stays in the loop — it stays, and it also stops gcc rotating
#          the loop, so iso-ts reads 33 against the denied arm's 19. The flag
#          distorts exactly the thing being measured.
#    What is probably right is to identify the loop STRUCTURALLY (the cycle
#    containing the transition step AND the accept probe) rather than by a
#    single anchor instruction, or to measure the emitted C's own basic blocks
#    before gcc sees them. Neither was attempted tonight.
# 2. A SABOTAGE ROW: reverting `emit_scan_loop` to emit the edge chain on the
#    generic path. That is the change this file exists to catch, so it is the
#    right row — but it must be validated as a row (docs/dev/sabotage/), not
#    asserted here.
# 3. THE `<=` IS DELIBERATELY NOT `==`, and the reason is measured: on iso-ts
#    the subject arm is SHORTER than the reference (15 against 19), because
#    where `s0` is itself a scan head the candidate-start prefilter moves off
#    the generic path with the edges. An `==` would be red on the very
#    artifact the row was chartered for. Whether the check should also assert
#    an UPPER bound on how much shorter (so that a loop which lost something
#    it needed reads red) is an open question for the manager.
# 4. THE BFS MEASURES A SHORTEST CYCLE, which is the generic path only while
#    the generic path really is the cheapest way round. True of every shape
#    measured tonight and NOT proved. `call` is treated as a fall-through, so
#    a memchr prefilter's own body is not counted.
# 5. IT MEASURES THE FORWARD MACHINE ONLY. The reverse and anchored machines
#    carry edges too (iso-ts has 4 in each) and their loops are the same
#    emitter. Extending the anchor to `rx_reverse_byte_class` inside
#    `rx_search` and `rx_anchored_byte_class` inside `rx_match` is mechanical
#    and was left out to keep tonight's draft one claim wide.
# 6. RUNTIME. Four witnesses x two arms x (compile + objdump + nm) is about
#    eight pcrec runs and eight gcc runs; it belongs beside
#    run_dfa_uniform_fold.sh in `make test-codegen` rather than in the
#    per-pattern harness.
#
# MEASURED TONIGHT, for whoever picks this up (gcc 15.2.0, -O2, this box):
#
#   witness                 edges  generic path  denied arm
#   iso-ts                  12     15            19
#   digits-then-letters      6     15            19
#   http-5xx                 2     INCONCLUSIVE  INCONCLUSIVE
#   two-chain                4     INCONCLUSIVE  INCONCLUSIVE
#
# The two that measure agree with a hand count of the same disassembly, and
# iso-ts's 15 against the pre-[OPT-EDGE] compiler's 29 is the row's own number.
