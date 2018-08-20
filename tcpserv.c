#include <netinet/in.h>    // for sockaddr_in
#include <sys/types.h>    // for socket
#include <sys/socket.h>    // for socket
#include <stdio.h>        // for printf
#include <stdlib.h>        // for exit
#include <string.h>        // for bzero
#include <arpa/inet.h>     // inet_ntoa

#define LISTENQ 20
#define MAXLINE 10000
int SERV_PORT=6666;

void
str_echo(int sockfd)
{
	long		arg1, arg2;
	ssize_t		n;
	char		line[MAXLINE];

	for ( ; ; ) {
		if ( (n = recv(sockfd, line, MAXLINE, 0)) == 0)
			return;		/* connection closed by other end */
		n = strlen(line);
        printf("len: %d \n", n);
		printf("data: %s", line);
		send(sockfd, line, n, 0);
		memset(line, 0, MAXLINE);
	}
}

int
main(int argc, char **argv)
{
	int					listenfd, connfd;
	pid_t				childpid;
	socklen_t			clilen;
	struct sockaddr_in	cliaddr, servaddr;
  
  if (argc > 2){
    printf("usage: tcpserv [port]\n");
    exit(0);
  }
  if (argc == 2){
    printf("listening on port:%s\n", argv[1]);
    SERV_PORT = atoi(argv[1]);
  }

	listenfd = socket(AF_INET, SOCK_STREAM, 0);

	bzero(&servaddr, sizeof(servaddr));
	servaddr.sin_family      = AF_INET;
	servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
	servaddr.sin_port        = htons(SERV_PORT);

	bind(listenfd, (struct sockaddr*) &servaddr, sizeof(servaddr));

	listen(listenfd, LISTENQ);

	for ( ; ; ) {
		clilen = sizeof(cliaddr);
		connfd = accept(listenfd, (struct sockaddr*) &cliaddr, &clilen);
		printf("connected from:%s, port:%d \n\n", inet_ntoa(cliaddr.sin_addr), ntohs(cliaddr.sin_port));
		if ( (childpid = fork()) == 0) {	/* child process */
			close(listenfd);	/* close listening socket */
			str_echo(connfd);	/* process the request */
			exit(0);
		}
		close(connfd);			/* parent closes connected socket */
	}
	return 0;
}
