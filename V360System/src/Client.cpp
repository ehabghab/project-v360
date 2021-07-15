/*
 * Client.cpp
 *
 *  Created on: May 2, 2021
 *      Author: eghabash
 */

#include "Client.h"

#include <thread>

#include "AbrAlgorithm.h"
#include "ClientNetworkLayer.h"
#include "Decoder.h"
#include "VideoPlayer.h"

Client::Client() {
  TilePredictor *tilePredictor = new TilePredictor();

  BandwidthPredictor *bandwidthPredictor = new BandwidthPredictor();

  VideoPlayer *videoPlayer = new VideoPlayer();

  AbrAlgorithm *abr = new AbrAlgorithm();

  Decoder *decoder = new Decoder();

  ClientNetworkLayer *clientNetworkLayer = new ClientNetworkLayer();

  std::thread recvThread(ClientNetworkLayer::receiver, clientNetworkLayer,
                         videoPlayer, bandwidthPredictor);

  std::thread videoPlayerThread(VideoPlayer::start, videoPlayer, tilePredictor);

  std::thread abrThread(AbrAlgorithm::runAbr, abr, tilePredictor, nullptr,
                        clientNetworkLayer);

  std::thread videoPlayerDecoderThread(VideoPlayer::decode, videoPlayer,
                                       decoder);

  std::thread senderThread(ClientNetworkLayer::sender, clientNetworkLayer);

  videoPlayerThread.join();
  abrThread.join();
  senderThread.join();
  recvThread.join();
  videoPlayerDecoderThread.join();
  /*

  ClientNetworkLayer *clientNetworkLayer = new ClientNetworkLayer();

  std::thread videoPlayerThread(VideoPlayer::start, videoPlayer,
                  tilePredictor);


  std::thread senderThread(ClientNetworkLayer::sender, clientNetworkLayer);

  std::thread recvThread(ClientNetworkLayer::receiver, clientNetworkLayer,
                  videoPlayer, bandwidthPredictor);


  std::thread abrThread(AbrAlgorithm::runAbr,
  tilePredictor,bandwidthPredictor,clientNetworkLayer);

  senderThread.join();

  recvThread.join();

  videoPlayerThread.join();

  videoPlayerDecoderThread.join();*/
}

Client::~Client() {}
