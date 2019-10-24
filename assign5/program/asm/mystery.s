	.globl	_mystery
_mystery:
  movl $0, -4(%rsp)
WHILE:
  addl $1, -4(%rsp)
	cmpl	$1, %edi
	je	ENDWHILE
IF:
	movl	%edi, %eax
  cltd
	movl	$2, %ecx
	idivl	%ecx
	cmpl	$0, %edx
	jne	ELSE
THEN:
	movl	%edi, %eax
  cltd
	movl	$2, %ecx
	idivl	%ecx
	movl	%eax, %edi
	jmp	ENDIF
ELSE:
	imull	$3, %edi, %edi
	addl	$1, %edi
ENDIF:
	jmp	WHILE
ENDWHILE:
  movl -4(%rsp), %eax
	retq
