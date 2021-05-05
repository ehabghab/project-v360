/*
 * Client.cpp
 *
 *  Created on: May 2, 2021
 *      Author: eghabash
 */

#include "Client.h"

#include <thread>

Client::Client()
{
	decoder_ = new Decoder();

	videoPlayer_ = new VideoPlayer(decoder_);

	clientNetworkLayer_ = new ClientNetworkLayer(videoPlayer_);

	std::thread videoPlayerThread(VideoPlayer::start, videoPlayer_);

	std::thread videoPlayerDecoderThread(VideoPlayer::decode, videoPlayer_);

	std::thread senderThread(ClientNetworkLayer::sender,clientNetworkLayer_);

	std::thread recvThread(ClientNetworkLayer::receiver,clientNetworkLayer_);


	senderThread.join();

	recvThread.join();

	videoPlayerThread.join();

	videoPlayerDecoderThread.join();
}

Client::~Client()
{

}

