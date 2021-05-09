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
	std::cout<<"A";
	std::thread videoPlayerThread(VideoPlayer::start, videoPlayer_);
	std::cout<<"B";

	std::thread videoPlayerDecoderThread(VideoPlayer::decode, videoPlayer_);
	std::cout<<"C";

	std::thread senderThread(ClientNetworkLayer::sender,clientNetworkLayer_);
	std::cout<<"D";

	std::thread recvThread(ClientNetworkLayer::receiver,clientNetworkLayer_);
	std::cout<<"E"<<std::endl;


	senderThread.join();

	recvThread.join();

	//videoPlayerThread.join();

	//videoPlayerDecoderThread.join();
}

Client::~Client()
{

}

