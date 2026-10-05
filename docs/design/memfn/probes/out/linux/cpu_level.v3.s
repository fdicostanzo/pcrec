# ARCHIVED 2026-10-05 by lane lxread from duxevents@ubuntubudu:/home/duxevents/pcrec/scratch_lx/wt_main/build/memfn_linux/20261005T130303Z/cpu_level.v3.s
# run: lane lxrun serial driver scratch_lx/run_lx1005.sh (quiet box; main clone c4c70f2c, probe tree wt_main = eb6fe6139);
# read in docs/design/memfn/linux_results.md. Content below is verbatim.
0000000000003380 <cpu_level>:
    3380:	push   %rbx
    3381:	xor    %eax,%eax
    3383:	xor    %ecx,%ecx
    3385:	cpuid
    3387:	xor    %ecx,%ecx
    3389:	mov    %eax,%r9d
    338c:	mov    $0x1,%eax
    3391:	cpuid
    3393:	mov    $0x80000001,%eax
    3398:	mov    %ecx,%r8d
    339b:	xor    %ecx,%ecx
    339d:	cpuid
    339f:	xor    %edi,%edi
    33a1:	mov    %ecx,%esi
    33a3:	cmp    $0x6,%r9d
    33a7:	jbe    33b4 <cpu_level+0x34>
    33a9:	mov    $0x7,%eax
    33ae:	mov    %edi,%ecx
    33b0:	cpuid
    33b2:	mov    %ebx,%edi
    33b4:	mov    %r8d,%eax
    33b7:	mov    $0x1,%r9d
    33bd:	not    %eax
    33bf:	test   $0x982201,%eax
    33c4:	je     33d0 <cpu_level+0x50>
    33c6:	mov    %r9d,%eax
    33c9:	pop    %rbx
    33ca:	ret
    33cb:	nopl   0x0(%rax,%rax,1)
    33d0:	test   $0x1,%sil
    33d4:	je     33c6 <cpu_level+0x46>
    33d6:	mov    $0x2,%r9d
    33dc:	test   $0x8000000,%r8d
    33e3:	je     33c6 <cpu_level+0x46>
    33e5:	xor    %ecx,%ecx
    33e7:	xgetbv
    33ea:	mov    %eax,%eax
    33ec:	shl    $0x20,%rdx
    33f0:	or     %rax,%rdx
    33f3:	not    %rax
    33f6:	test   $0x6,%al
    33f8:	jne    33c6 <cpu_level+0x46>
    33fa:	not    %r8d
    33fd:	and    $0x30401000,%r8d
    3404:	jne    33c6 <cpu_level+0x46>
    3406:	mov    %edi,%eax
    3408:	not    %eax
    340a:	test   $0x128,%eax
    340f:	jne    33c6 <cpu_level+0x46>
    3411:	and    $0x20,%esi
    3414:	je     33c6 <cpu_level+0x46>
    3416:	not    %rdx
    3419:	mov    $0x3,%r9d
    341f:	and    $0xe6,%edx
    3425:	jne    33c6 <cpu_level+0x46>
    3427:	xor    %r9d,%r9d
    342a:	test   $0xd0030000,%eax
    342f:	sete   %r9b
    3433:	add    $0x3,%r9d
    3437:	jmp    33c6 <cpu_level+0x46>
    3439:	nopl   0x0(%rax)

