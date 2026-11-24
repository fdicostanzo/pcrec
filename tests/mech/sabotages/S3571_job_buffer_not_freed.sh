# S3571 -- [K155] (lane k155fix, 2026-11-24): a Job-owned builder is no longer
# freed by job_cleanup.
#
# `src/core/compile.c`'s job_cleanup frees every StrBuf field of the Job (the
# half of the builder rule a Job-owned buffer rests on); the plant drops the
# `irsb` free. A leak on every --emit-ir compile, refused or not, that no
# answer or artifact byte shows. The net is the Job-field half of
# `tests/core/scratch_builder_check.py` (the core arm).
SAB_ID="S3571-job-buffer-not-freed"
SAB_FILE="src/core/compile.c"
SAB_SUITES="core"
SAB_DESC="job_cleanup no longer frees the Job's irsb: no answer or byte moves, so only the K155 builder census's Job-field check (tests/core/scratch_builder_check.py, run by the core arm) can see it"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3571."
SAB_REACH_POP="src/core/compile.c|^        pcrec_sb_free\\(&cx->job->irsb\\);|1"
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_free(&cx->job->irsb);'
SAB_AFTER='        /* SABOTAGE S3571: irsb not freed */'
