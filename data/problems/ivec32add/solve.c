#include <stdint.h>
#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

unsigned int main()
{
    unsigned int n;
    fread(&n, sizeof(n), 1, stdin);
    unsigned int *a = malloc(3 * n * sizeof(unsigned int));
    unsigned int *b = a + n;
    unsigned int *c = b + n;
    memset(c, 0, n);
    fread(a, 2 * n * sizeof(unsigned int), 1, stdin);
    for (unsigned int i = 0; i < n; ++i) {
        c[i] = a[i] + b[i];
    }
    fwrite(c, n * sizeof(unsigned int), 1, stdout);
    return 0;
}
