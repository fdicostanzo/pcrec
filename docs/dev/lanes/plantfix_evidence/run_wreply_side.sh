S=/var/tmp/pcrec-claude/scratch/plantfix; T=$1; TAG=$2
export TMPDIR=$S/tmp CC=gcc-16 PATH=$S/shim:$PATH
s0=$(date +%s); timeout 3600 bash $T/tests/memfn/run_wreply.sh --plants > $S/out_$TAG/run_wreply.shim.out 2> $S/out_$TAG/run_wreply.shim.err; echo "rc=$? $(( $(date +%s) - s0 ))s" > $S/out_$TAG/run_wreply.shim.rc
