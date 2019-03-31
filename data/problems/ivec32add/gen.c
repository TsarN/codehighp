#include <stdio.h>
#include <stdlib.h>

int main()
{
    freopen(NULL, "wb", stdout);
    unsigned int n = 1;
    fwrite(&n, sizeof(n), 1, stdout);
    for (unsigned int i = 0; i < 2 * n; ++i) {
        int x = rand();
        fwrite(&x, sizeof(x), 1, stdout);
    }
    return 0;
}
