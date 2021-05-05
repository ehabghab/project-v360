/*
 * ClientNetworkLayer.cpp
 *
 *  Created on: May 1, 2021
 *      Author: eghabash
 */

#include "ClientNetworkLayer.h"

#include <arpa/inet.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/socket.h>
#include <unistd.h>

#include <fstream>
#include <iostream>


#include <boost/algorithm/string/regex.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/asio.hpp>
#include <boost/format.hpp>


ClientNetworkLayer::ClientNetworkLayer(VideoPlayer* vp) {


	videoPlayer_ = vp;

	std::string tracePath = "/Users/eghabash/Desktop/360 Video/Project-V360"
			"/split/tiles_per_second_user_3.txt";
	std::ifstream infile(tracePath);

	std::string line;
	int pos;
	int sec;
	std::string tiles;
	std::vector<std::string> tilesVec;
	while (std::getline(infile, line))
	{

		pos = line.find(":");
		sec = std::stoi(line.substr(0,pos));
		tiles = line.substr(pos+2,line.size()-(pos+3));

		boost::algorithm::split(tilesVec, tiles, boost::is_any_of(","));
		predTemp_.insert(std::pair< int,std::vector<std::string> >(sec,tilesVec));
	}


	//socketfd = initSocket();
//
//	requests_[2].push_back("3/1.h264");
//	requests_[2].push_back("4/1.h264");
//	requests_[2].push_back("5/1.h264");
//	requests_[2].push_back("3/2.h264");
//	requests_[2].push_back("4/2.h264");
//	requests_[2].push_back("5/2.h264");
//	requests_[2].push_back("3/3.h264");
//	requests_[2].push_back("4/3.h264");
//	requests_[2].push_back("5/3.h264");
//	requests_[2].push_back("3/4.h264");
//	requests_[2].push_back("4/4.h264");
//	requests_[2].push_back("5/4.h264");
//	requests_[2].push_back("3/5.h264");
//	requests_[2].push_back("4/6.h264");
//	requests_[2].push_back("5/7.h264");
//	requests_[2].push_back("3/51.h264");
//	requests_[2].push_back("4/12.h264");
//	requests_[2].push_back("5/31.h264");
//	requests_[2].push_back("3/21.h264");


	socket_ = connectToServer();

	//To compile use -std=c++11
	//To send chunk/frame requests based on the request priority.
	//cout<<this->getRequest();

	//close(socketfd);

}

int ClientNetworkLayer::connectToServer()
{
	int sock = -1;
	struct sockaddr_in serv_addr;
	if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
	{
		printf("\n Socket creation error \n");
		return -1;
	}

	serv_addr.sin_family = AF_INET;
	serv_addr.sin_port = htons(PORT);

	// Convert IPv4 and IPv6 addresses from text to binary form
	if(inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr)<=0)
	{
		printf("\nInvalid address/ Address not supported \n");
		return -1;
	}

	if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
	{
		printf("\nConnection Failed \n");
		return -1;
	}
	return sock;
}

void ClientNetworkLayer::sender(ClientNetworkLayer * client)
{

	//std::cout<<"EHAB";
	std::string request;
	std::string reqHeader;
	long time = std::chrono::duration_cast<std::chrono::milliseconds>
	(std::chrono::system_clock::now().time_since_epoch()).count();
	int chunkId = 1;
	client->fillRequest(chunkId);
	long etime;
	while(true)
	{
		request = client->getRequest();

		etime = std::chrono::duration_cast<std::chrono::milliseconds>
		(std::chrono::system_clock::now().time_since_epoch()).count();

		if(etime - time >= 1000)
		{
			if(chunkId + 1 == 60)
			{
				return;
			}
			client->fillRequest(++chunkId);
			time = etime;
		}

		if(request == "")
		{
			continue;
		}

		reqHeader = client->getRequestHeader(request);
		//std::cout<<reqHeader<<std::endl;
		send(client->socket_, reqHeader.c_str() , reqHeader.size() , 0 );

	}


}

void ClientNetworkLayer::receiver(ClientNetworkLayer * client)
{

	bool leftover = false;

	//if the last request is incomplete, this will hold the incomplete part.
	std::string leftoverString = "";

	//if we receive multiple request at a time, this vector will hold each one of them.
	//Some of the request maybe incomplete.
	std::vector<std::string> responsesVecTemp;

	//this buffer will hold the received bytes at socket.
	char * data = (char *) malloc(sizeof(char) * RESPONSE_MAX_LENGTH);

	std::map<std::string, std::string> respHeader;

	uint8_t respHeaderFileBoarderIndex = -1;

	int bytesRead = 0;
	//int count = 1;
	while(true)
	{
		//each response contains header followed by file.
		//both header and file end with \r\n\r\n.
		//RESPONSE_MAX_LENGTH must be less than header.

		//Mainly each response will end \r\n\r\n.
		//file must be uint8_t*.

		bzero(data,RESPONSE_MAX_LENGTH);
		bytesRead = read(client->socket_, data, RESPONSE_MAX_LENGTH);

		if(leftover)
		{

			//this finds if data buffer contains
			//part the response and file altogether
			//we assume that data buffer can only have either full response or
			//part of res header, part of file.
			int headerPosEndLimit = (leftoverString + data).find("\r\n\r\n");
			if(headerPosEndLimit != std::string::npos)
			{
				respHeaderFileBoarderIndex = (headerPosEndLimit + 4)
												- leftoverString.size();
			}
			boost::algorithm::split_regex(responsesVecTemp,
										leftoverString + data, boost::regex("\r\n\r\n"));
			leftoverString = "";
			leftover = false;
		}
		else
		{
			boost::algorithm::split_regex(responsesVecTemp, data,
					boost::regex("\r\n\r\n"));
		}

		if(responsesVecTemp.size() > 2)
		{
			//Error
			std::cout<<"Error: client receiver side,"
					" received multiple response headers!"<<std::endl;
			std::cout<<"Quick fix reduce the RESPONSE_MAX_LENGTH to 1"<<std::endl;
			return;
		}


		//the response is not complete.
		if(responsesVecTemp[0].size() != 0 && responsesVecTemp.size() == 1)
		{
			leftoverString = responsesVecTemp[0];
			leftover = true;

		}
		else
		{
			//cout<<responsesVecTemp[0]<<endl<<"---"<<endl;
			respHeader = client->parseHeader(responsesVecTemp[0]);
			int chunkSize = std::stoi(respHeader["Content-Length"]) + 4;
			uint8_t * chunk = (uint8_t*) malloc(chunkSize * sizeof(uint8_t));
			//read file part in data;

			//			for(auto pair: respHeader)
			//			{
			//				//cout<<pair.first<<":"<<pair.second<<endl;
			//			}

			memcpy(chunk,data+respHeaderFileBoarderIndex,
					bytesRead - respHeaderFileBoarderIndex);
			//read the remaining part of the file.

			int bufferPos = bytesRead - respHeaderFileBoarderIndex;
			int remainingBytes = chunkSize - bufferPos;
			do
			{
				bytesRead = read(client->socket_, chunk + bufferPos, remainingBytes);
				bufferPos += bytesRead;
				remainingBytes -= bytesRead;
			}
			while(remainingBytes != 0);
			//std::cout<<responsesVecTemp[0]<<std::endl<<"---"<<std::endl;
			client->videoPlayer_->addChunk(chunk, chunkSize, respHeader["Tile-Index"]);
			//			std::cout<<respHeader["Tile-Index"]<<std::endl;
			//			std::ofstream myfile;
			//			std::string filename("_"+std::to_string(count++));
			//			myfile.open(filename);
			//			for(int i = 0; i < chunkSize; i++)
			//			{
			//				myfile << chunk[i];
			//
			//			}
			//			myfile.close();
			//

		}



	}



}

std::string ClientNetworkLayer::getRequest()
{
	int priorityLvl;
	for(priorityLvl = 0; priorityLvl < PRIORITY_LEVELS; priorityLvl++)
	{
		auto & reqsVec = requests_[priorityLvl];
		reqMutex_.lock();
		if (reqsVec.size() > 0)
		{
			std::string request(reqsVec[0]);
			reqsVec.erase(requests_[priorityLvl].begin());
			reqMutex_.unlock();
			return request;
		}
		reqMutex_.unlock();

	}

	return "";
}

std::string ClientNetworkLayer::getRequestHeader(std::string request)
{

	std::stringstream  reqHeader;
	reqHeader << boost::format("GET /%s HTTP/1.1\r\n") % request;
	reqHeader << boost::format("accept-encoding: %s\r\n") % "gzip, deflate";
	reqHeader << boost::format("accept-language: %s\r\n") % "en-us";
	reqHeader << boost::format("\r\n");

	return reqHeader.str();

}

std::map<std::string, std::string> ClientNetworkLayer::parseHeader(std::string responseHeader)
{


	std::map<std::string, std::string> header;
	std::vector<std::string> headersVec;
	std::vector<std::string> splitVec;

	//get response header rows.
	boost::algorithm::split_regex(headersVec, responseHeader,
			boost::regex("\r\n"));

	//parse the first row [http version and status code]
	boost::algorithm::split_regex(splitVec, headersVec[0],
			boost::regex(" "));

	header.insert(std::pair<std::string,std::string>("HTTP version",splitVec[0]));
	header.insert(std::pair<std::string,std::string>("Status Code",splitVec[1]+" "+ splitVec[2]));


	for(uint8_t headerIdx = 1; headerIdx < headersVec.size(); headerIdx++)
	{
		const auto splitIdx = headersVec[headerIdx].find(':');
		if (std::string::npos != splitIdx)
		{
			const auto key = headersVec[headerIdx].substr(0, splitIdx);
			const auto value = headersVec[headerIdx].substr(splitIdx + 1);
			header.insert(std::pair<std::string,std::string>(key,value));

		}

	}






	return header;

}

void ClientNetworkLayer::fillRequest(int chunkId)
{
	for(auto& tile : predTemp_.find(chunkId)->second)
	{
		requests_[2].push_back(std::to_string(stoi(tile))+"/"+std::to_string(chunkId)+".h264");
	}



}


ClientNetworkLayer::~ClientNetworkLayer() {
	// TODO free class variables.
}

