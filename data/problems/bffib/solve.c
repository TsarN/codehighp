#include <stdio.h>

int main() {
    int x;
    scanf("%d", &x);
    int a = 1, b = 1;
    while (x-->1) {
        int t = a;
        a += b;
        b = t;
    }
    printf("%d", a);
    return 0;
}
