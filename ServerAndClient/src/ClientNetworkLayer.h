/*
 * ClientNetworkLayer.h
 *
 *  Created on: May 1, 2021
 *      Author: eghabash
 */

#ifndef CLIENTNETWORKLAYER_H_
#define CLIENTNETWORKLAYER_H_


#include <map>
#include <mutex>
#include <vector>

#include "VideoPlayer.h"

#define RESPONSE_MAX_LENGTH 150
#define PORT 7717
#define PRIORITY_LEVELS 10

class ClientNetworkLayer {

	/**
	 * map has all requests,
	 * with key of requests priorities [lower number --> higher priority],
	 * and value of indices of all chunks/frames with priority == key.
	 * Note: priority zero reserved for urgent chunks/frames.
	 */
	std::map <int, std::vector<std::string> > requests_;

	//To synchronize put and get requests from map.
	std::mutex reqMutex_;

	//This is temp until we have our own predictor.
	std::map <int, std::vector<std::string> > predTemp_;

	VideoPlayer* videoPlayer_;
	//TODO document what each function does.

	int socket_;

	int connectToServer();


	void fillRequest(int chunkId);

	std::string getRequest();

	std::string getRequestHeader(std::string request);

	std::map<std::string, std::string> parseHeader(std::string responseHeader);

public:
	ClientNetworkLayer(VideoPlayer* vp);

	void static sender(ClientNetworkLayer* client);

	void static receiver(ClientNetworkLayer* client);

	virtual ~ClientNetworkLayer();
};

#endif /* CLIENTNETWORKLAYER_H_ */
