/*
 * Server.cpp
 *
 *  Created on: Apr 24, 2021
 *      Author: eghabash
 */

#include "Server.h"

#include <folly/String.h>
#include <glog/logging.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#include <algorithm>
#include <boost/algorithm/string.hpp>
#include <boost/format.hpp>
#include <ctime>
#include <fstream>
#include <iostream>
#include <map>
#include <thread>
#include <vector>

Server::Server() {
  videoRootDir_ =
      "/Users/eghabash/Desktop/System-github/Project-V360/split/YuvW12H12";

  // videoRootDir_ =
  //  "/Users/eghabash/Desktop/360 Video/Project-V360"
  //"/split/YuvW12H12";

  uint8_t socketFD = initializeSocket();
  uint8_t socket = listenToSocket(socketFD);
  std::thread recieverThread(reciever, this, socket);
  std::thread senderThread(sender, this, socket);
  recieverThread.join();
  senderThread.join();
}

uint8_t Server::initializeSocket() {
  uint8_t socketFileDescriptor;
  struct sockaddr_in address;
  int opt = 1;

  // Creating socket file descriptor
  if ((socketFileDescriptor = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
    perror("socket failed");
    exit(EXIT_FAILURE);
  }

  if (setsockopt(socketFileDescriptor, SOL_SOCKET, SO_REUSEADDR, &opt,
                 sizeof(opt))) {
    perror("setsockopt - Reuse-Address");
    exit(EXIT_FAILURE);
  }

  if (setsockopt(socketFileDescriptor, SOL_SOCKET, SO_REUSEPORT, &opt,
                 sizeof(opt))) {
    perror("setsockopt - Reuse-Port");
    exit(EXIT_FAILURE);
  }

  address.sin_family = AF_INET;
  address.sin_addr.s_addr = INADDR_ANY;
  address.sin_port = htons(PORT);

  if (bind(socketFileDescriptor, (struct sockaddr *)&address, sizeof(address)) <
      0) {
    perror("bind failed");
    exit(EXIT_FAILURE);
  }

  return socketFileDescriptor;
}

uint8_t Server::listenToSocket(uint8_t socketFileDescriptor) {
  LOG(INFO) << "Listening @ PORT:" << PORT;
  struct sockaddr_in address;
  int addrlen = sizeof(address);
  uint8_t newSocket;

  if (listen(socketFileDescriptor, 3) < 0) {
    perror("listen");
    exit(EXIT_FAILURE);
  }
  if ((newSocket = accept(socketFileDescriptor, (struct sockaddr *)&address,
                          (socklen_t *)&addrlen)) < 0) {
    perror("accept");
    exit(EXIT_FAILURE);
  }
  LOG(INFO) << "Connected!";
  return newSocket;
}

void Server::reciever(Server *server, uint8_t socket) {
  // whether last request was received fully or not.
  bool leftover = false;

  // if the last request is incomplete, this will hold the incomplete part.
  std::string leftoverString = "";

  // if we receive multiple request at a time, this vector will hold each one of
  // them. Some of the request maybe incomplete.
  std::vector<std::string> requestsVecTemp;

  // this buffer will hold the received bytes at socket.
  char *data = (char *)malloc(sizeof(char) * REQUEST_MAX_LENGTH);

  while (true) {
    bzero(data, REQUEST_MAX_LENGTH);
    read(socket, data, REQUEST_MAX_LENGTH);

    /**
     *	if there was incomplete request,
     *	then add the incomplete part of it
     *	to the beginning of received data (leftoverString + data).
     * */
    if (leftover) {
      boost::algorithm::split_regex(requestsVecTemp, leftoverString + data,
                                    boost::regex("\r\n\r\n"));
      leftoverString = "";
      leftover = false;
    } else {
      boost::algorithm::split_regex(requestsVecTemp, data,
                                    boost::regex("\r\n\r\n"));
    }

    // loop over the requests.
    for (uint8_t idx = 0; idx < requestsVecTemp.size(); idx++) {
      if (requestsVecTemp[idx].size() != 0 &&
          idx == requestsVecTemp.size() - 1) {
        // If the last request is not empty, then it is  incomplete request
        // as it does not end with \r\n\r\n.

        leftoverString = requestsVecTemp[idx];
        leftover = true;
      } else if (requestsVecTemp[idx].size() != 0) {
        /**
         * if the request is empty, skip it.
         * Otherwise, add it. read more about boost::algorithm::split_regex:
         * https://www.boost.org/doc/libs/1_51_0/doc/html/boost/algorithm/split_regex.html
         * */

        auto tiles = server->parseRequestIntoTiles(requestsVecTemp[idx]);
        auto quality = server->parseRequestIntoQuality(requestsVecTemp[idx]);
        server->addTileList(tiles, quality);
      }
    }
    // TODO check http version
    //	   check that it is a get

    // add -lboost_regex
    //		std::vector<std::string> requestRows;
    //		boost::algorithm::split_regex(requestRows, request,
    // boost::regex("\r\n"));
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
    //			uint8_t * buffer = (uint8_t *) malloc(size *
    // sizeof(uint8_t));
    //			// Read in the entire file.
    //			fread(buffer, size, 1, p_file);
    //			// Close the file
    //			fclose(p_file);
    //
    //			//ToDo Make sure they don't get out of order.
    //			//send HTTP header.
    //			std::string header(this->getResponseHeader("1.1","200
    // OK","Bytes",size,"video/m4s",url));
    //			send(newSocket,header.c_str(),header.size(),0);
    //
    //			//send HTTP file.
    //			send(newSocket,buffer,size,0);
    //			free(buffer);
    //
    //
    //		}
    // GET 6/1.h264 HTTP/1.1\r\n",req+"?quality=720p&chunk_scheme=3
  }
}

void Server::sender(Server *server, uint8_t socket) {
  int fileSize;
  uint8_t *buffer;

  // quality, tile chunks (chunkId, tileId) vector ordered by priority to send.
  std::pair<uint8_t, std::vector<std::string>> tileLists;
  // we use tile index to keep track which tile from the list to send next.
  uint32_t tileIdx;
  // Tile Info contains chunkId, setId, and tileId
  std::vector<std::string> tileInfo;
  std::string q = "";
  while (true) {
    auto tileListsTemp = server->getTileList();

    // if new tile list received update current one.
    if (tileListsTemp.second.size() != 0) {
      tileLists = tileListsTemp;
      tileIdx = 0;
    }

    if (std::to_string(tileLists.first) != q) {
      q = std::to_string(tileLists.first);
    }
    // if tile list is empty then skip or all tiles have been sent.
    if (tileLists.second.size() == 0 || tileIdx >= tileLists.second.size()) {
      continue;
    }

    // find a non duplicate tile to send.
    for (; tileIdx < tileLists.second.size(); tileIdx++) {
      // LOG(INFO) << tileIdx << ":" << tileLists.second.size() << " = "
      //          << tileLists.second[tileIdx];
      boost::algorithm::split_regex(tileInfo, tileLists.second[tileIdx],
                                    boost::regex("_"));
      try {
        auto chunkId = ((stoi(tileInfo[0]) - 1) / 25) + 1;
        auto tileId = static_cast<uint16_t>(stoi(tileInfo[2]));
        // check if the tile has already been sent or not.
        if (server->tilesSent_.find(std::make_pair(chunkId, tileId)) ==
            server->tilesSent_.end()) {
          // mark as sent since we are going to send it.
          server->tilesSent_.insert(std::make_pair(chunkId, tileId));
          break;
        }
      } catch (std::invalid_argument &e) {
        LOG(ERROR) << "Error: failed to extract tileInfo:\n"
                   << tileInfo[0] << ":" << tileInfo[2] << "-->"
                   << tileLists.second[tileIdx] << std::endl;
      }
    }

    // all tiles have been sent.
    if (tileIdx >= tileLists.second.size()) {
      continue;
    }
    // advance tile Index to next tile in the list.
    tileIdx++;
    // build tile path based on quality per set.
    // for path start with quality 1:low, 2: high.
    std::string qualityPathIdx;
    // quality tileLists.first;
    // sets.

    // 0:LL, 1:HL, 2:HH
    if (tileLists.first == 0) { // LL
      qualityPathIdx = "1";
    } else if (tileLists.first == 1) { // HL
      if (tileInfo[1] == "0") {        // Set 0: viewport set
        qualityPathIdx = "2";
      } else { // Set 1: viewport edge set
        qualityPathIdx = "1";
      }
    } else { // HH
      qualityPathIdx = "2";
    }

    std::string chunkId = std::to_string(((stoi(tileInfo[0]) - 1) / 25) + 1);

    // quality/tileId/chunkId
    std::string tilePath = server->videoRootDir_ + "/" + qualityPathIdx + "/" +
                           tileInfo[2] + "/" + chunkId + ".h264";
    char *filePath = new char[tilePath.length() + 1];
    strcpy(filePath, tilePath.c_str());
    FILE *p_file = NULL;
    p_file = fopen(filePath, "r");
    if (!p_file) {
      LOG(ERROR) << "Server::sender(): chunk file not found!" << std::endl;
      // ToDo check error code.
      // send to user 404 or other error status.
      continue;
    }
    delete[] filePath;

    fseek(p_file, 0, SEEK_END);
    fileSize = ftell(p_file);
    fseek(p_file, 0, SEEK_SET);
    // Enough memory for the file
    buffer = (uint8_t *)malloc((fileSize + 4) * sizeof(uint8_t));
    if (buffer == NULL) {
      LOG(ERROR) << "Server::sender(): malloc buffer did not succeed!";
    }
    // Read in the entire file.
    fread(buffer, fileSize, 1, p_file);
    // Close the file
    fclose(p_file);
    // mark response end.
    buffer[fileSize] = '\r';
    buffer[fileSize + 1] = '\n';
    buffer[fileSize + 2] = '\r';
    buffer[fileSize + 3] = '\n';

    // send header
    std::string header(server->getResponseHeader(
        "1.1", "200 OK", "Bytes", fileSize, "video/m4s",
        chunkId + "_" + tileInfo[2], qualityPathIdx));
    VLOG(1) << "\n" << header << "-------";
    send(socket, header.c_str(), header.size(), 0);

    // send file.
    send(socket, buffer, fileSize + 4, 0);
    free(buffer);
  }
}

std::string
Server::getResponseHeader(std::string httpVersion, std::string statusCode,
                          std::string acceptRange, int contentLength,
                          std::string contentType, std::string tileIdx,
                          std::string quality) {
  std::stringstream header;

  time_t now = time(0);
  tm *gmtm = gmtime(&now);
  std::string dt(asctime(gmtm));

  header << boost::format("HTTP%s %s\r\n") % httpVersion % statusCode;
  header << boost::format("Tile-Index: %s\r\n") % tileIdx;
  header << boost::format("Tile-Quality:%s\r\n") % quality;
  header << boost::format("Date: %s\r\n") % dt.erase(dt.size() - 1);
  header << boost::format("Accept-Ranges: %s\r\n") % acceptRange;
  header << boost::format("Content-Length: %d\r\n") % contentLength;
  header << boost::format("Content-Type: %s\r\n") % contentType;
  header << "\r\n";
  return header.str();
}

std::vector<std::string> Server::parseRequestIntoTiles(std::string request) {
  std::vector<std::string> tempVec1;
  std::vector<std::string> tempVec2;
  boost::algorithm::split_regex(tempVec1, request, boost::regex("Tiles"));

  boost::algorithm::split_regex(tempVec2, tempVec1[1], boost::regex("Quality"));

  std::vector<std::string> tiles;
  std::vector<std::string> tileSets;
  boost::algorithm::split_regex(tileSets, tempVec2[0], boost::regex("\n"));
  for (auto const &tileSet : tileSets) {
    if (tileSet == "") {
      continue;
    }
    // get chunk/set Id
    boost::algorithm::split_regex(tempVec2, tileSet, boost::regex(":"));
    std::string FrameSetId = tempVec2[0] + "_" + tempVec2[1] + "_";
    boost::algorithm::split_regex(tempVec1, tempVec2[2], boost::regex(","));

    for (auto const &tileId : tempVec1) {
      tiles.push_back(FrameSetId + tileId);
    }
  }
  return tiles;
}

uint8_t Server::parseRequestIntoQuality(std::string request) {
  std::vector<std::string> tempVec;
  boost::algorithm::split_regex(tempVec, request, boost::regex("Quality"));
  boost::algorithm::split_regex(tempVec, tempVec[1], boost::regex("HTTP/1.1"));
  boost::algorithm::split_regex(tempVec, tempVec[0], boost::regex("\n"));
  try {
    uint8_t quality = static_cast<uint8_t>(stoi(tempVec[1]));
    return quality;
  } catch (std::invalid_argument &e) {
    LOG(ERROR) << "Error: failed to extract quality:\n"
               << tempVec[1] << std::endl;
    return 100;
  }
}

void Server::addTileList(std::vector<std::string> tiles, uint8_t quality) {
  reqMutex_.lock();
  request_ = std::make_pair(quality, tiles);
  reqMutex_.unlock();
}

std::pair<uint8_t, std::vector<std::string>> Server::getTileList() {
  std::pair<uint8_t, std::vector<std::string>> requestToReturn;
  reqMutex_.lock();
  requestToReturn = request_;
  request_.second = {};
  reqMutex_.unlock();
  return requestToReturn;
}

Server::~Server() {
  // TODO Auto-generated destructor stub
}

void start() {
  Server *server = new Server();
  // to suppress warning
  assert(server != nullptr);
}

int main(int argc, const char **argv) {
  std::thread serverThread(start);
  serverThread.join();
  return 0;
}
