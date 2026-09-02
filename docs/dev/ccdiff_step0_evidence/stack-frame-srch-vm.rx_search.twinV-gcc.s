0000000000003020 <rx_search>:
    3020:	endbr64
    3024:	push   %r15
    3026:	push   %r14
    3028:	push   %r13
    302a:	push   %r12
    302c:	push   %rbp
    302d:	push   %rbx
    302e:	sub    $0xc88,%rsp
    3035:	mov    %rcx,0x8(%rsp)
    303a:	lea    0x698(%rsp),%rax
    3042:	mov    %fs:0x28,%r13
    304b:	mov    %r13,0xc78(%rsp)
    3053:	lea    0xb0(%rsp),%r13
    305b:	mov    %rax,0x78(%rsp)
    3060:	movq   $0x3f,0x70(%rsp)
    3069:	movq   $0x5e,0x80(%rsp)
    3075:	mov    %r13,0x68(%rsp)
    307a:	cmp    %rdx,%rsi
    307d:	jb     3160 <rx_search+0x140>
    3083:	pcmpeqd %xmm0,%xmm0
    3087:	mov    %rdi,0x10(%rsp)
    308c:	mov    %rsi,%r14
    308f:	mov    %rdi,%r12
    3092:	movdqa 0x10e6(%rip),%xmm1        # 4180 <rx_class_bitmap0+0xa0>
    309a:	movaps %xmm0,0x40(%rsp)
    309f:	mov    %rdx,%rbp
    30a2:	mov    %rdx,%r15
    30a5:	movq   $0xffffffffffffffff,0x60(%rsp)
    30ae:	movq   $0x0,0x28(%rsp)
    30b7:	movaps %xmm0,0x50(%rsp)
    30bc:	pxor   %xmm0,%xmm0
    30c0:	mov    %rsi,0x18(%rsp)
    30c5:	lea    0x40(%rsp),%rsi
    30ca:	movups %xmm0,0x88(%rsp)
    30d2:	movups %xmm1,0x98(%rsp)
    30da:	movaps %xmm0,0x30(%rsp)
    30df:	nop
    30e0:	mov    %r14,%rdx
    30e3:	lea    0x10(%rsp),%rdi
    30e8:	mov    %r15,0x20(%rsp)
    30ed:	call   21c0 <rx_match_anchored>
    30f2:	lea    0x6(%rax),%rdx
    30f6:	cmp    $0x4,%rdx
    30fa:	jbe    3187 <rx_search+0x167>
    3100:	test   %rax,%rax
    3103:	jns    31a2 <rx_search+0x182>
    3109:	mov    0x90(%rsp),%rax
    3111:	test   %rax,%rax
    3114:	je     3147 <rx_search+0x127>
    3116:	shl    $0x4,%rax
    311a:	add    %r13,%rax
    311d:	nopl   (%rax)
    3120:	mov    0x5d8(%rax),%edx
    3126:	mov    0x5e0(%rax),%rcx
    312d:	sub    $0x10,%rax
    3131:	mov    %rcx,0x40(%rsp,%rdx,8)
    3136:	cmp    %rax,%r13
    3139:	jne    3120 <rx_search+0x100>
    313b:	movq   $0x0,0x90(%rsp)
    3147:	movq   $0x0,0x88(%rsp)
    3153:	cmp    %r15,%r14
    3156:	je     3160 <rx_search+0x140>
    3158:	add    $0x1,%r15
    315c:	jmp    30e0 <rx_search+0xc0>
    315e:	xchg   %ax,%ax
    3160:	xor    %eax,%eax
    3162:	mov    0xc78(%rsp),%rdx
    316a:	sub    %fs:0x28,%rdx
    3173:	jne    31bd <rx_search+0x19d>
    3175:	add    $0xc88,%rsp
    317c:	pop    %rbx
    317d:	pop    %rbp
    317e:	pop    %r12
    3180:	pop    %r13
    3182:	pop    %r14
    3184:	pop    %r15
    3186:	ret
    3187:	cmp    $0xfffffffffffffffd,%rax
    318b:	jne    3162 <rx_search+0x142>
    318d:	mov    0x8(%rsp),%rcx
    3192:	mov    %rbp,%rdx
    3195:	mov    %r14,%rsi
    3198:	mov    %r12,%rdi
    319b:	call   2cd0 <rx_search_deep>
    31a0:	jmp    3162 <rx_search+0x142>
    31a2:	mov    0x8(%rsp),%rbx
    31a7:	test   %rbx,%rbx
    31aa:	je     31b6 <rx_search+0x196>
    31ac:	add    %r15,%rax
    31af:	mov    %r15,(%rbx)
    31b2:	mov    %rax,0x8(%rbx)
    31b6:	mov    $0x1,%eax
    31bb:	jmp    3162 <rx_search+0x142>
    31bd:	call   20b0 <__stack_chk_fail@plt>
    31c2:	nopl   (%rax)
    31c5:	data16 cs nopw 0x0(%rax,%rax,1)

