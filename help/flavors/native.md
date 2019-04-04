# Native flavor

Solutions for problems with `native` flavor
are written in ordinary programming languages
(currently C and C++) and ran on ordinary
x86_64 computers under Linux. They are similar
to traditional problems seen in many other online 
judges, but with a few differences.

First of all, most native problems use binary
input/output instead of text. This helps eliminate
the bottleneck of converting string representations
of ints/floats/etc into native data types.
We're not here to compete who can divide by 10 
repeatedly faster than anybody else after all.

Secondly, native problems are not compiled by
themselves, but are linked to a special wrapper.
It allows greater security than other sandboxing
solutions with much less performance hit.
For this reason, entry point of your solution
is the `solve` function.

## What can I do

You can read from `stdin` and write to `stdout`.
You can also allocate memory, but your entire program
(code + libraries + data) cannot use more memory
than specified in problem statement (per test).

## Example solution for A+B

<pre>
#include &lt;stdio.h&gt;

void solve()
{
    int a, b;
    fread(&a, sizeof(a), 1, stdin);
    fread(&b, sizeof(b), 1, stdin);
    int c = a + b;
    fwrite(&c, sizeof(c), 1, stdout);
}
</pre>

## nostdlib mode

If you want, you can ditch the standard C library.
The only function that will be available is the
`syscall` function. To do this, choose a `nostdlib`
compiler when submitting your solution.
