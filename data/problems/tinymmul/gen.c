#include <stdio.h>
#include <stdlib.h>

int main()
{
    srand(atoi(getenv("RAND_SEED")));
    freopen(NULL, "wb", stdout);
    unsigned int n = atoi(getenv("N"));
    fwrite(&n, sizeof(n), 1, stdout);
    for (unsigned int i = 0; i < 2 * n * n; ++i) {
        unsigned int x = rand();
        fwrite(&x, sizeof(x), 1, stdout);
    }
    return 0;
}
