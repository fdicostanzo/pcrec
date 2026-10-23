 260:	endbr64
 264:	push   %r15
 266:	push   %r14
 268:	push   %r13
 26a:	push   %r12
 26c:	push   %rbp
 26d:	push   %rbx
 26e:	sub    $0x38,%rsp
 272:	mov    %rdx,0x8(%rsp)
 277:	mov    %fs:0x28,%rax
 280:	mov    %rax,0x28(%rsp)
 285:	xor    %eax,%eax
 287:	test   %rdx,%rdx
 28a:	je     348 <rx_next_n+0xe8>
 290:	mov    %rdi,%rbp
 293:	mov    %rsi,%r15
 296:	lea    0x10(%rsp),%r13
 29b:	xor    %r14d,%r14d
 29e:	mov    %r14,%rbx
 2a1:	shl    $0x4,%rbx
 2a5:	add    %r15,%rbx
 2a8:	test   %r15,%r15
 2ab:	cmove  %r13,%rbx
 2af:	cmpl   $0x49540302,0x0(%rbp)
 2b6:	jne    330 <rx_next_n+0xd0>
 2b8:	mov    0x20(%rbp),%r12
 2bc:	mov    0x18(%rbp),%rsi
 2c0:	mov    %rbx,%rcx
 2c3:	mov    0x10(%rbp),%rdi
 2c7:	mov    %r12,%rdx
 2ca:	call   80 <rx__find>
 2cf:	cmp    $0x1,%eax
 2d2:	je     308 <rx_next_n+0xa8>
 2d4:	mov    %r12,0x20(%rbp)
 2d8:	movq   $0x49540303,0x0(%rbp)
 2e0:	mov    0x28(%rsp),%rax
 2e5:	sub    %fs:0x28,%rax
 2ee:	jne    34d <rx_next_n+0xed>
 2f0:	add    $0x38,%rsp
 2f4:	mov    %r14,%rax
 2f7:	pop    %rbx
 2f8:	pop    %rbp
 2f9:	pop    %r12
 2fb:	pop    %r13
 2fd:	pop    %r14
 2ff:	pop    %r15
 301:	ret
 302:	nopw   0x0(%rax,%rax,1)
 308:	mov    0x8(%rbx),%rdx
 30c:	mov    (%rbx),%rcx
 30f:	cmp    %rcx,%rdx
 312:	lea    0x1(%rcx),%rax
 316:	cmovg  %rdx,%rax
 31a:	add    $0x1,%r14
 31e:	mov    %rax,0x20(%rbp)
 322:	cmp    %r14,0x8(%rsp)
 327:	jne    29e <rx_next_n+0x3e>
 32d:	jmp    2e0 <rx_next_n+0x80>
 32f:	nop
 330:	mov    %rbp,%rdi
 333:	call   0 <rx__enter>
 338:	test   %eax,%eax
 33a:	jne    2b8 <rx_next_n+0x58>
 340:	jmp    2e0 <rx_next_n+0x80>
 342:	nopw   0x0(%rax,%rax,1)
 348:	xor    %r14d,%r14d
 34b:	jmp    2e0 <rx_next_n+0x80>
 34d:	call   352 <rx_next_n+0xf2>
			34e: R_X86_64_PLT32	__stack_chk_fail-0x4
 352:	nopl   (%rax)
 355:	data16 cs nopw 0x0(%rax,%rax,1)

