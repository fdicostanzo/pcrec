import os, subprocess
T='/var/tmp/pcrec-pcrec/scratch/trailgen'; W='/home/pcrec/projects/pcrec/worktrees/trailgen'
d=T+'/sab'; os.makedirs(d+'/s',exist_ok=True)
def build(dd):
    os.makedirs(dd,exist_ok=True)
    return subprocess.run(['gcc','-O2','-std=gnu11','-I'+W+'/lib','-I'+dd,'-DHDR="rx.h"','-DPFX_search=rx_search','-DPFX_search_in=rx_search_in','-DPFX_NCAPS=RX_NCAPS','-DPFX_RESUME_FRAME_SIZE=RX_RESUME_FRAME_SIZE','-DPFX_TRAIL_FRAME_SIZE=RX_TRAIL_FRAME_SIZE','-DPFX_buffers=rx_buffers','-o',dd+'/cdrv','/var/tmp/pcrec-pcrec/scratch/vmbc/cdrv.c',dd+'/rx.c'],capture_output=True,text=True)
subprocess.run([W+'/build/pcrec','-p','rx','--features','all','--engine=vm','--pattern','a|(b)c','-o',d+'/s/rx.c'],check=True)
build(d+'/s')
for tag,env in (('U',{}),('sab',{'TG_SAB_ENTRY':'1'})):
    os.makedirs(d+'/'+tag,exist_ok=True)
    e=dict(os.environ); e.update(env)
    r=subprocess.run(['python3','-I',T+'/vmopt_tg.py','-m','BCdU',d+'/s/rx.c',d+'/'+tag+'/rx.c'],capture_output=True,text=True,env=e); print(tag, r.stderr.strip()[-90:])
    open(d+'/'+tag+'/rx.h','w').write(open(d+'/s/rx.h').read()); build(d+'/'+tag)
open(d+'/sub','w').write('bxa')
for tag in ('s','U','sab'):
    print(tag, subprocess.run([d+'/'+tag+'/cdrv',d+'/sub'],capture_output=True,text=True).stdout.strip())
