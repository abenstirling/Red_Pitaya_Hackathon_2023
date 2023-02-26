#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <stdlib.h>

#define MAX     256
#define BASE    0x40300000  // Proc address base
#define regOut  0x60        // Offset for reading binary input
#define regIn   0x64        // Offset for writing binary output

#define DOT     0   // .
#define DASH    1   // -
#define SPC     2   // Space between dot/dash
#define BREAK   3   // Space between words

char tokentochar(int tok) {
    switch (tok) {
        case DOT:   return '.'; break;
        case DASH:  return '-'; break;
        case SPC:   return ' '; break;
        case BREAK: return ' '; break;
        default:    return '?'; 
    }

}

void Out32(void *adr, int offset, int value) {
    *((uint32_t *)(adr+offset)) = value;
}

int In32(void *adr, int offset) {
    return *((uint32_t *)(adr+offset));
}

int In16(void *adr, int offset) {
    int r;
    r= *((uint32_t *)(adr+offset));
    if (r > 32767) return r-65536;
    return r;
}

/* The main function */
int main(int argc, char **argv) {
  int fd;
  void *adr;
  char *name = "/dev/mem";
  int i,d;
  
  /* open memory device */
  if((fd = open(name, O_RDWR)) < 0) {
    perror("open");
    return 1;
  }

  /* map the memory, start from BASE address, size: _SC_PAGESIZE = 4k */
  adr = mmap(NULL, sysconf(_SC_PAGESIZE), PROT_READ|PROT_WRITE, MAP_SHARED, fd, BASE);


  /* ADD YOUR CODE HERE */
  //int arr[] = {1,0,1,0,1,0,0,0,1,1,1,0,0,0,1,0,1,0,1,0,0,0,0,0,0,0};
  int arr[MAX];
  int out[MAX];
  int count = 0;
  

  /* enable scope, wait 1s and read & print samples */ /* SAMPLE CODE */
  Out32(adr, 0x50, 1);
  
  sleep(1);

  printf("x, y\n");
  for (i = 0; i < MAX; i++) {
	  d = In16(adr, 0x60);
	  printf("%d, %d\n",i,d);

    arr[i] = d;
  }

  for (i = 0; i < MAX; i++) {

    // if current zero, it could be 000 or 0000000
    if (!arr[i]) {
      if (!arr[i+1] && !arr[i+2] && !arr[i+3] && !arr[i+4] && !arr[i+5] && !arr[i+6]) {
        out[count] = BREAK;
        count++;
        i += 6;
      }
      else if (!arr[i+1] && !arr[i+2]) {
        out[count] = SPC;
        count++;
        i += 2;
      }
    }
    // if current 1, it could be 10 or 1110
    else {
      if (arr[i+1] && arr[i+2] && !arr[i+3]) {
        out[count] = DASH;
        count++;
        i += 3;
      }
      if (!arr[i+1]) {
        out[count] = DOT;
        count++;
        i += 1;
      }
    }
  }

  printf("-------------------------------------------------\n");
  for (i = 0; i < count; i++) {
      int tok = out[i];
      char c = tokentochar(tok);
      if (tok != SPC)
        printf("%c", c);
  }
  printf("\n");

  munmap(adr, sysconf(_SC_PAGESIZE));
  return 0;
}

