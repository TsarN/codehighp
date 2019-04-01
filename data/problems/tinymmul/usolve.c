#include <stdint.h>
#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>

void solve()
{
    unsigned int n;
    fread(&n, sizeof(n), 1, stdin);
    unsigned int *a = malloc(3 * n * n * sizeof(unsigned int));
    unsigned int *b = a + n * n;
    unsigned int *c = b + n * n;
    fread(a, 2 * n * sizeof(unsigned int), 1, stdin);
    for (unsigned int i = 0; i < n; ++i) {
        for (unsigned int j = 0; j < n; ++j) {
            for (unsigned int k = 0; k < n; ++k) {
                c[n * i + k] += a[n * i + j] * b[n * j + k];
            }
        }
    }
    fwrite(c, n * n * sizeof(unsigned int), 1, stdout);
}
