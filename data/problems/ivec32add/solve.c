#include <stdint.h>
#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>

int main()
{
    unsigned int n;
    fread(&n, sizeof(n), 1, stdin);
    int *a = malloc(3 * n * sizeof(int));
    int *b = a + n;
    int *c = b + n;
    fread(a, 2 * n * sizeof(int), 1, stdin);
    for (unsigned int i = 0; i < n; ++i) {
        c[i] = a[i] + b[i];
    }
    fwrite(c, n * sizeof(int), 1, stdout);
    return 0;
}
