# prunechk.py IN OUT : greedily drop each whole-line RX_TRAIL_CHECK(); whose removal keeps
# trail_checkpoints.py clean (no trail-writing cycle without a checkpoint) -- what D183's
# placement rule gives once it counts only SURVIVING writes
import sys, importlib.util
spec = importlib.util.spec_from_file_location('tc', '/home/pcrec/projects/pcrec/worktrees/trailgc/tests/vm/trail_checkpoints.py')
tc = importlib.util.module_from_spec(spec); spec.loader.exec_module(tc)
lines = open(sys.argv[1], encoding='latin-1').read().split('\n')
idx = [i for i, l in enumerate(lines) if l.strip() == 'RX_TRAIL_CHECK();']
dropped = 0
for i in idx:
    save = lines[i]; lines[i] = '    ;'
    errs, worst, margin, n = tc.check_text('\n'.join(lines), 'x')
    if any('cycle' in e for e in errs): lines[i] = save
    else: dropped += 1
open(sys.argv[2], 'w', encoding='latin-1').write('\n'.join(lines))
print('checkpoints %d, droppable %d' % (len(idx), dropped))
