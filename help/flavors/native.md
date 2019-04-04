# Native flavor

Solutions for problems with `native` flavor
are written in ordinary programming languages
(currently C and C++) and ran on ordinary
x86_64 computers under Linux. They are similar
to traditional problems seen in many other online 
judges, but with a few differences.

Most native problems use binary
input/output instead of text. This helps eliminate
the bottleneck of converting string representations
of ints/floats/etc into native data types.
We're not here to compete who can divide by ten
repeatedly faster than anybody else after all.

## What can I do

You can read from `stdin` and write to `stdout`.
You can also allocate memory, but your entire program
(code + libraries + data) cannot use more memory
than specified in problem statement (per test).

## What should I know

Your solution's entry point is not named `main`.
For technical reasons it's actually `_SolutionMain`.
It's substituted using C preprocessor, so don't be
afraid if you see compilation error in `_SolutionMain`.

Following flags are used to compile C/C++ code:
`-g0 -O2 -static`.

Sometimes Memory Limit Exceeded is detected as
Runtime Error. It's because OS won't give your program
any more memory and it crashes when it tries to use
null pointer returned from `malloc()` for example.

## Example solution for A+B

<pre>
#include &lt;stdio.h&gt;

int main()
{
    int a, b;
    fread(&a, sizeof(a), 1, stdin);
    fread(&b, sizeof(b), 1, stdin);
    int c = a + b;
    fwrite(&c, sizeof(c), 1, stdout);
    return 0;
}
</pre>

## nostdlib mode

If you want, you can ditch the standard C/C++ library.
The only function that will be available is the
`syscall` function. To do this, choose a `nostdlib`
compiler when submitting your solution.
Following flags are used to compile C/C++ 
code in this mode:
`-g0 -O2 -nostdlib`.

Example solution for A+B:

<pre>
#define _GNU_SOURCE
#include &lt;unistd.h&gt;
#include &lt;sys/syscall.h&gt;

int main()
{
    int a, b;
    syscall(SYS_read, 0, &a, sizeof(a));
    syscall(SYS_read, 0, &b, sizeof(b));
    int c = a + b;
    syscall(SYS_write, 1, &c, sizeof(c));
    return 0;
}
</pre>