#include "IT8951.h"
#include <unistd.h>

int main (int argc, char *argv[])
{
  // Kill process after 2 minutes always
  alarm(120);
  printf("Setup alarm\n");
	/*
	printf("ReadReg = 0x%x\n",IT8951ReadReg(LISAR));
	IT8951WriteReg(LISAR,0x1234);
	printf("ReadReg = 0x%x\n",IT8951ReadReg(LISAR));
	*/
	if(IT8951_Init())
	{
		printf("IT8951_Init error \n");
		return 1;
	}
	
	//IT8951DisplayExample();
	//IT8951DisplayExample2();
	//printf("IT8951_GUI_Example\n");
	//IT8951_GUI_Example();
	
	
	if (argc != 4)
	{
		printf("Error: argc!=4.\n");
		exit(1);
	}

	uint32_t x,y;
	sscanf(argv[1],"%d",&x);
	sscanf(argv[2],"%d",&y);
	//IT8951DisplayWhite();
	IT8951_BMP_Example(x,y,argv[3]);
	
	//IT8951_Cancel();
	IT8951StandBy();
	return 0;
}


