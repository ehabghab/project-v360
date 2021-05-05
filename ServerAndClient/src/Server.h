/*
 * Server.h
 *
 *  Created on: Apr 24, 2021
 *      Author: eghabash
 */

#ifndef SERVER_H_
#define SERVER_H_

#include <cstdint>

#include <boost/algorithm/string/regex.hpp>
#include <boost/asio.hpp>


#define PORT 7717
#define REQUEST_MAX_LENGTH 1024

class Server {

	std::string videoRootDir_;

	std::vector<std::string> requests_;


	std::mutex reqMutex_;

	uint8_t initializeSocket();
	uint8_t listenToSocket(uint8_t socketFileDescriptor);

	void static reciever(Server* server,uint8_t socket);

	void static sender(Server* server,uint8_t socket);


	std::string getResponseHeader(std::string httpVersion,
			std::string statusCode,std::string acceptRange,
			int contentLength,std::string contentType, std::string tileIdx);


	void addReq(std::string request);
	std::string getReq();
public:
	Server();
	virtual ~Server();
};

#endif /* SERVER_H_ */
