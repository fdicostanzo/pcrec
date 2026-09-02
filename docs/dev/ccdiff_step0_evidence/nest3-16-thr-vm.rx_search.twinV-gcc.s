0000000000002ea0 <rx_search>:
    2ea0:	endbr64
    2ea4:	push   %r15
    2ea6:	push   %r14
    2ea8:	push   %r13
    2eaa:	push   %r12
    2eac:	push   %rbp
    2ead:	push   %rbx
    2eae:	sub    $0xc98,%rsp
    2eb5:	mov    %rcx,0x8(%rsp)
    2eba:	lea    0x790(%rsp),%rax
    2ec2:	mov    %fs:0x28,%r13
    2ecb:	mov    %r13,0xc88(%rsp)
    2ed3:	lea    0xd0(%rsp),%r13
    2edb:	mov    %rax,0x98(%rsp)
    2ee3:	movq   $0x48,0x90(%rsp)
    2eef:	movq   $0x4f,0xa0(%rsp)
    2efb:	mov    %r13,0x88(%rsp)
    2f03:	cmp    %rdx,%rsi
    2f06:	jb     3000 <rx_search+0x160>
    2f0c:	pcmpeqd %xmm0,%xmm0
    2f10:	mov    %rdi,0x10(%rsp)
    2f15:	mov    %rsi,%r14
    2f18:	mov    %rdi,%r12
    2f1b:	movdqa 0x118d(%rip),%xmm1        # 40b0 <_fini+0x520>
    2f23:	movaps %xmm0,0x40(%rsp)
    2f28:	mov    %rdx,%rbp
    2f2b:	mov    %rdx,%r15
    2f2e:	movq   $0xffffffffffffffff,0x80(%rsp)
    2f3a:	movq   $0x0,0x28(%rsp)
    2f43:	movaps %xmm0,0x50(%rsp)
    2f48:	movaps %xmm0,0x60(%rsp)
    2f4d:	movaps %xmm0,0x70(%rsp)
    2f52:	pxor   %xmm0,%xmm0
    2f56:	mov    %rsi,0x18(%rsp)
    2f5b:	lea    0x40(%rsp),%rsi
    2f60:	movups %xmm0,0xa8(%rsp)
    2f68:	movups %xmm1,0xb8(%rsp)
    2f70:	movaps %xmm0,0x30(%rsp)
    2f75:	data16 cs nopw 0x0(%rax,%rax,1)
    2f80:	mov    %r14,%rdx
    2f83:	lea    0x10(%rsp),%rdi
    2f88:	mov    %r15,0x20(%rsp)
    2f8d:	call   21c0 <rx_match_anchored>
    2f92:	lea    0x6(%rax),%rdx
    2f96:	cmp    $0x4,%rdx
    2f9a:	jbe    3027 <rx_search+0x187>
    2fa0:	test   %rax,%rax
    2fa3:	jns    3042 <rx_search+0x1a2>
    2fa9:	mov    0xb0(%rsp),%rax
    2fb1:	test   %rax,%rax
    2fb4:	je     2fe7 <rx_search+0x147>
    2fb6:	shl    $0x4,%rax
    2fba:	add    %r13,%rax
    2fbd:	nopl   (%rax)
    2fc0:	mov    0x6b0(%rax),%edx
    2fc6:	mov    0x6b8(%rax),%rcx
    2fcd:	sub    $0x10,%rax
    2fd1:	mov    %rcx,0x40(%rsp,%rdx,8)
    2fd6:	cmp    %rax,%r13
    2fd9:	jne    2fc0 <rx_search+0x120>
    2fdb:	movq   $0x0,0xb0(%rsp)
    2fe7:	movq   $0x0,0xa8(%rsp)
    2ff3:	cmp    %r15,%r14
    2ff6:	je     3000 <rx_search+0x160>
    2ff8:	add    $0x1,%r15
    2ffc:	jmp    2f80 <rx_search+0xe0>
    2ffe:	xchg   %ax,%ax
    3000:	xor    %eax,%eax
    3002:	mov    0xc88(%rsp),%rdx
    300a:	sub    %fs:0x28,%rdx
    3013:	jne    305d <rx_search+0x1bd>
    3015:	add    $0xc98,%rsp
    301c:	pop    %rbx
    301d:	pop    %rbp
    301e:	pop    %r12
    3020:	pop    %r13
    3022:	pop    %r14
    3024:	pop    %r15
    3026:	ret
    3027:	cmp    $0xfffffffffffffffd,%rax
    302b:	jne    3002 <rx_search+0x162>
    302d:	mov    0x8(%rsp),%rcx
    3032:	mov    %rbp,%rdx
    3035:	mov    %r14,%rsi
    3038:	mov    %r12,%rdi
    303b:	call   2b20 <rx_search_deep>
    3040:	jmp    3002 <rx_search+0x162>
    3042:	mov    0x8(%rsp),%rbx
    3047:	test   %rbx,%rbx
    304a:	je     3056 <rx_search+0x1b6>
    304c:	add    %r15,%rax
    304f:	mov    %r15,(%rbx)
    3052:	mov    %rax,0x8(%rbx)
    3056:	mov    $0x1,%eax
    305b:	jmp    3002 <rx_search+0x162>
    305d:	call   20b0 <__stack_chk_fail@plt>
    3062:	nopl   (%rax)
    3065:	data16 cs nopw 0x0(%rax,%rax,1)

