#include <netinet/in.h>    // for sockaddr_in
#include <sys/types.h>    // for socket
#include <sys/socket.h>    // for socket
#include <stdio.h>        // for printf
#include <stdlib.h>        // for exit
#include <string.h>        // for bzero
#include <arpa/inet.h>     // inet_ntoa

int SERV_PORT1 = 6666;
#define MAXLINE 10000

void
str_cli(FILE *fp, int sockfd)
{
	char	sendline[MAXLINE], recvline[MAXLINE];

	while (fgets(sendline, MAXLINE, fp) != NULL) {

		send(sockfd, sendline, strlen(sendline), 0);

		memset(sendline, 0, MAXLINE);
		memset(recvline, 0, MAXLINE);

		if (recv(sockfd, recvline, MAXLINE, 0) == 0){
			printf("str_cli: server terminated prematurely");
//			exit(0);
//				continue;
		}

		fputs(recvline, stdout);
	}
}


int
main(int argc, char **argv)
{
	int					sockfd;
	struct sockaddr_in	servaddr;

	if (argc < 2){
		printf("usage: tcpcli <IPaddress> [port]\n");
		exit(0);
	}
  if (argc >= 3){
		printf("target %s:%s\n", argv[1], argv[2]);
		SERV_PORT1 = atoi(argv[2]);
	}

	sockfd = socket(AF_INET, SOCK_STREAM, 0);

	bzero(&servaddr, sizeof(servaddr));
	servaddr.sin_family = AF_INET;
	servaddr.sin_port = htons(SERV_PORT1);
	inet_pton(AF_INET, argv[1], &servaddr.sin_addr);

	connect(sockfd, (struct sockaddr*) &servaddr, sizeof(servaddr));

	str_cli(stdin, sockfd);		/* do it all */

	exit(0);
}
