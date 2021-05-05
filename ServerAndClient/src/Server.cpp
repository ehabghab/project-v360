/*
 * Server.cpp
 *
 *  Created on: Apr 24, 2021
 *      Author: eghabash
 */

#include "Server.h"

#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <boost/algorithm/string.hpp>
#include <boost/format.hpp>

#include <algorithm>
#include <fstream>
#include <ctime>
#include <iostream>
#include <thread>
#include <vector>
#include <map>

#include "Client.h"


Server::Server()
{
	videoRootDir_ = "/Users/eghabash/Desktop/360 Video/Project-V360"
			"/split/YuvW12H12/encoded_payloadExtractChunks";

	//	auto socket = listenToSocket();
	//	serve(socket);
	uint8_t socketFD = initializeSocket();
	uint8_t socket = listenToSocket(socketFD);
	std::thread recieverThread(reciever,this,socket);
	std::thread senderThread(sender,this,socket);
	recieverThread.join();
	senderThread.join();
}

uint8_t Server::initializeSocket()
{
	uint8_t socketFileDescriptor;
	struct sockaddr_in address;
	int opt = 1;

	// Creating socket file descriptor
	if ((socketFileDescriptor = socket(AF_INET, SOCK_STREAM, 0)) == 0)
	{
		perror("socket failed");
		exit(EXIT_FAILURE);
	}

	if (setsockopt(socketFileDescriptor, SOL_SOCKET, SO_REUSEADDR,
			&opt, sizeof(opt)))
	{
		perror("setsockopt - Reuse-Address");
		exit(EXIT_FAILURE);
	}

	if (setsockopt(socketFileDescriptor, SOL_SOCKET, SO_REUSEPORT,
			&opt, sizeof(opt)))
	{
		perror("setsockopt - Reuse-Port");
		exit(EXIT_FAILURE);
	}


	address.sin_family = AF_INET;
	address.sin_addr.s_addr = INADDR_ANY;
	address.sin_port = htons( PORT );

	if (bind(socketFileDescriptor, (struct sockaddr *)&address,
			sizeof(address))<0)
	{
		perror("bind failed");
		exit(EXIT_FAILURE);
	}

	return socketFileDescriptor;

}

uint8_t Server::listenToSocket(uint8_t socketFileDescriptor)
{

	std::cout<<"ListenToSocket"<<std::endl;
	struct sockaddr_in address;
	int addrlen = sizeof(address);
	uint8_t newSocket;

	if (listen(socketFileDescriptor, 3) < 0)
	{
		perror("listen");
		exit(EXIT_FAILURE);
	}
	if ((newSocket = accept(socketFileDescriptor, (struct sockaddr *)&address,
			(socklen_t*)&addrlen))<0)
	{
		perror("accept");
		exit(EXIT_FAILURE);
	}

	return newSocket;

}

void Server::reciever(Server* server,uint8_t socket)
{

	//whether last request was received fully or not.
	bool leftover = false;

	//if the last request is incomplete, this will hold the incomplete part.
	std::string leftoverString = "";

	//if we receive multiple request at a time, this vector will hold each one of them.
	//Some of the request maybe incomplete.
	std::vector<std::string> requestsVecTemp;

	//this buffer will hold the received bytes at socket.
	char * data = (char *) malloc(sizeof(char) * REQUEST_MAX_LENGTH);

	while(true)
	{

		bzero(data,REQUEST_MAX_LENGTH);
		read(socket , data, REQUEST_MAX_LENGTH);

		/**
		 *	if there was incomplete request,
		 *	then add the incomplete part of it
		 *	to the beginning of received data (leftoverString + data).
		 * */
		if(leftover)
		{
			boost::algorithm::split_regex(requestsVecTemp, leftoverString + data,
					boost::regex("\r\n\r\n"));
			leftoverString = "";
			leftover = false;
		}
		else
		{
			boost::algorithm::split_regex(requestsVecTemp, data,
					boost::regex("\r\n\r\n"));
		}

		//loop over the requests.
		for (uint8_t idx = 0; idx < requestsVecTemp.size();idx++)
		{

			if(requestsVecTemp[idx].size() != 0 && idx == requestsVecTemp.size()-1)
			{
				//If the last request is not empty, then it is  incomplete request
				//as it does not end with \r\n\r\n.

				leftoverString = requestsVecTemp[idx];
				leftover = true;
			}
			else if(requestsVecTemp[idx].size() != 0)
			{
				/**
				 * if the request is empty, skip it.
				 * Otherwise, add it. read more about boost::algorithm::split_regex:
				 * https://www.boost.org/doc/libs/1_51_0/doc/html/boost/algorithm/split_regex.html
				 * */

				server->addReq(requestsVecTemp[idx]);
			}

		}
		//TODO check http version
		//	   check that it is a get

		//add -lboost_regex
		//		std::vector<std::string> requestRows;
		//		boost::algorithm::split_regex(requestRows, request, boost::regex("\r\n"));
		//
		//		//TODO parse request.
		//
		//		//Get request URL
		//		int httpIdx = requestRows[0].find("HTTP");
		//		std::string url = requestRows[0].substr(4,httpIdx-5);
		//		//ToDo clear warning
		//		const char * filePath = (this->videoRootDir+url).c_str();
		//
		//		FILE *p_file = NULL;
		//		p_file = fopen(filePath,"rb");
		//
		//		if (!p_file)
		//		{
		//			//ToDo check error code.
		//			//send to user 404 or other error status.
		//		}
		//		else
		//		{
		//			//To get the file size skip to its EOF.
		//			//ToDo check time performance.
		//			fseek(p_file,0,SEEK_END);
		//			int size = ftell(p_file);
		//			fseek(p_file,0,SEEK_SET);
		//			// Enough memory for the file
		//			uint8_t * buffer = (uint8_t *) malloc(size * sizeof(uint8_t));
		//			// Read in the entire file.
		//			fread(buffer, size, 1, p_file);
		//			// Close the file
		//			fclose(p_file);
		//
		//			//ToDo Make sure they don't get out of order.
		//			//send HTTP header.
		//			std::string header(this->getResponseHeader("1.1","200 OK","Bytes",size,"video/m4s",url));
		//			send(newSocket,header.c_str(),header.size(),0);
		//
		//			//send HTTP file.
		//			send(newSocket,buffer,size,0);
		//			free(buffer);
		//
		//
		//		}
		//GET 6/1.h264 HTTP/1.1\r\n",req+"?quality=720p&chunk_scheme=3

	}}

void Server::sender(Server* server,uint8_t socket)
{
	std::vector<std::string> reqRows;
	int fileSize;
	uint8_t * buffer;
	std::string req;
	while(true)
	{

		req = server->getReq();
		//cout<<req<<endl<<"--"<<endl;
		if(req == "")
		{
			continue;
		}

		boost::algorithm::split_regex(reqRows, req,
				boost::regex("\r\n"));
		//cout<<reqRows[0]<<endl<<++c<<endl<<"---"<<endl;
		boost::algorithm::split_regex(reqRows, reqRows[0],
				boost::regex(" "));
		char *filePath = new char[(server->videoRootDir_+reqRows[1]).length() + 1];
		strcpy(filePath, (server->videoRootDir_+reqRows[1]).c_str());
		FILE *p_file = NULL;
		p_file = fopen(filePath,"r");
		if (!p_file)
		{
			std::cout<<"file issue"<<std::endl;
			//ToDo check error code.
			//send to user 404 or other error status.
			continue;
		}
		delete [] filePath;

		fseek(p_file,0,SEEK_END);
		fileSize = ftell(p_file);
		fseek(p_file,0,SEEK_SET);
		// Enough memory for the file
		buffer = (uint8_t *) malloc((fileSize+4) * sizeof(uint8_t));
		// Read in the entire file.
		fread(buffer, fileSize, 1, p_file);
		// Close the file
		fclose(p_file);
		//mark response end.
		buffer[fileSize] = '\r';
		buffer[fileSize + 1] = '\n';
		buffer[fileSize + 2] = '\r';
		buffer[fileSize + 3] = '\n';
		//cout<<3<<endl;


		//send header
		std::string header(server->getResponseHeader("1.1","200 OK","Bytes",fileSize,"video/m4s",reqRows[1]));
		send(socket,header.c_str(),header.size(),0);
		//cout<<4<<endl;

		//send file.
		send(socket,buffer,fileSize + 4,0);
		free(buffer);
		//			cout<<reqRows[1]<<" Send!"<<endl;
		//			cout<<"---"<<endl;
		//cout<<++count<<endl;

	}
}

std::string Server::getResponseHeader(std::string httpVersion, std::string statusCode,
		std::string acceptRange, int contentLength,
		std::string contentType, std::string tileIdx){

	std::stringstream  header;

	time_t now = time(0);
	tm *gmtm = gmtime(&now);
	std::string dt(asctime(gmtm));

	header << boost::format("HTTP%s %s\r\n") % httpVersion % statusCode;
	header << boost::format("Date: %s\r\n") % dt.erase(dt.size()-1);
	header << boost::format("Accept-Ranges: %s\r\n") % acceptRange;
	header << boost::format("Content-Length: %d\r\n") % contentLength;
	header << boost::format("Content-Type: %s\r\n") %  contentType;
	header << boost::format("Server: %s\r\n") % "nginx 1.18.0";
	header << boost::format("Tile-Index: %s\r\n") % tileIdx;
	header << "\r\n";

	return header.str();


}

void Server::addReq(std::string request)
{
	reqMutex_.lock();
	requests_.push_back(request);
	reqMutex_.unlock();
}

std::string Server::getReq()
{
	std::string request = "";
	reqMutex_.lock();

	if(requests_.size() > 0)
	{
		request = requests_[0];
		requests_.erase(requests_.begin());
	}
	reqMutex_.unlock();
	return request;
}

Server::~Server() {
	// TODO Auto-generated destructor stub
}

void start()
{
	Server * server = new Server();
	//waiting for connection



}

std::map<int,std::map<int, std::string>> mm;

static void t()
{



}

int main(int argc, const char** argv)
{

//	std::map<int, std::string> l;
//	l.insert(std::pair<int,std::string>(1,"x"));
//	mm.insert(std::pair<int,std::map<int, std::string>>(2,l));
//
//	std::thread x(t);
//
//	auto& m = mm.find(2)->second;
//	for(int i = 0; i < 10; i++)
//	{
//
//
//	}

	std::thread serverThread(start);
	sleep(2);
	Client* client = new Client();
	serverThread.join();




}
