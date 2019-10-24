#include <stdio.h>

extern int _mystery(int);

int main() {
  printf("3: %d\n", _mystery(3));
  printf("1: %d\n", _mystery(1));
  printf("100: %d\n", _mystery(100));
  return 0;
}
