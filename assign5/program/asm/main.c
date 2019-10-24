#include <stdio.h>

extern int mystery(int);

int main() {
  printf("3: %d\n", mystery(3));
  printf("1: %d\n", mystery(1));
  printf("100: %d\n", mystery(100));
  return 0;
}
