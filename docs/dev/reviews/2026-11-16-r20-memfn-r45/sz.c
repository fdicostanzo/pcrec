#include "/home/pcrec/projects/pcrec/worktrees/crit-memfn-r45/memfn/src/window.c"
#include <stdio.h>
#include <stddef.h>
#define P(x) printf("%-22s %zu\n", #x, sizeof(x))
int main(void){
 P(mf_class); printf("proven %zu\n", sizeof(((mf_class*)0)->proven));
 P(mf_result); P(mf_wspan); P(mf_walt); P(mf_wreply); P(mf_site); P(mf_pred); P(mf_term); P(mf_run_reply);
 P(wf_pos); P(wf_alt); P(wf_dec); P(struct wf_plan); P(wf_legacy);
 printf("MF_PROOF_LO %d MF_MAX_FWD %d WREACH %d WSPAN_POS %d WPLAN_MAX %d\n", MF_PROOF_LO, MF_MAX_FWD, MF_WREACH, MF_WSPAN_POS, (int)MF_WPLAN_MAX);
 printf("offsetof proven %zu run %zu\n", offsetof(mf_class, proven), offsetof(mf_class, run));
 return 0;}
