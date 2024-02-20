#include <stdio.h>

int main() {
    int i;

    // Printable ASCII characters start from 32 up to 126
    for(i = 32; i < 127; i++) {
        printf("%c", i);
        // Print a new line for every 16 characters to match the format in the image
        if ((i - 31) % 16 == 0) {
            printf("\n");
        }
    }

    printf("\n");

    return 0;
}
