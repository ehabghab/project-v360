/*
 * Client.h
 *
 *  Created on: Apr 24, 2021
 *      Author: eghabash
 */

#ifndef CLIENT_H_
#define CLIENT_H_

#include "ClientNetworkLayer.h"
#include "VideoPlayer.h"
#include "Decoder.h"

class Client {

	ClientNetworkLayer* clientNetworkLayer_;
	VideoPlayer* videoPlayer_;
	Decoder* decoder_;

public:
	Client();
	virtual ~Client();
};

#endif /* CLIENT_H_ */
