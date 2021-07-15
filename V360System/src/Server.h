/*
 * Server.h
 *
 *  Created on: Apr 24, 2021
 *      Author: eghabash
 */

#ifndef SERVER_H_
#define SERVER_H_

#include <boost/algorithm/string/regex.hpp>
#include <boost/asio.hpp>
#include <boost/functional/hash.hpp>
#include <cstdint>
#include <unordered_set>

#define PORT 7717
#define REQUEST_MAX_LENGTH 1024

class Server {
  std::string videoRootDir_;

  std::pair<uint8_t, std::vector<std::string>> request_;

  std::mutex reqMutex_;

  // this is a hashset for tiles already sent,
  // used to avoid sending duplicate tiles.
  std::unordered_set<std::pair<int, uint16_t>,
                     boost::hash<std::pair<int, uint16_t>>>
      tilesSent_;

  uint8_t initializeSocket();

  uint8_t listenToSocket(uint8_t socketFileDescriptor);

  void static reciever(Server* server, uint8_t socket);

  void static sender(Server* server, uint8_t socket);

  std::string getResponseHeader(std::string httpVersion, std::string statusCode,
                                std::string acceptRange, int contentLength,
                                std::string contentType, std::string tileIdx);

  /**
   * This function takes as input the request as one string, and returns
   * vector of the tiles in the following format "chunkId_setId_tileId" ordered
   * by priority where tile at index 0 has the highest priority.
   */
  std::vector<std::string> parseRequestIntoTiles(std::string request);

  // retrun the quality from request.
  uint8_t parseRequestIntoQuality(std::string request);

  void addTileList(std::vector<std::string> tiles, uint8_t quality);

  std::pair<uint8_t, std::vector<std::string>> getTileList();

 public:
  Server();
  virtual ~Server();
};

#endif /* SERVER_H_ */
