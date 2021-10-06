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
#include "Util.h"
#include "VideoPlayer.h"

Client::Client() {
  // Initiate all instances to create threads.
  // 1- Network layer (sender and receiver).
  // 2- Video player along with the decoder.
  // 3- ABR algorithm along with tile and bandwidth predictors.

  ClientNetworkLayer *clientNetworkLayer = new ClientNetworkLayer();
  VideoPlayer *videoPlayer = new VideoPlayer();
  Decoder *decoder = new Decoder();
  AbrAlgorithm *abr = new AbrAlgorithm();
  TilePredictor *tilePredictor = new TilePredictor();
  BandwidthPredictor *bandwidthPredictor = new BandwidthPredictor();

  // For logging consistency, we pass log timestamp to both:
  // 1- Video player to log rebuffering.
  // 2- Network layet to log info (quality, idx) for all tiles recevied.
  std::string logsTimestamp = Util::getCurrentDateTime();
  videoPlayer->setPlayLogTimestamp(logsTimestamp);
  clientNetworkLayer->setRecvLogTimestamp(logsTimestamp);

  // Start all threads:
  // 1- receiver thread: to recive tiles.
  // 2- video player thread: to stitch and play viewport frames.
  // 3- decoder thread: to decode tiles.
  // 4- sender thread: to send requests for the wanted tiles.
  // 5- abr thread: to estimate what tiles to request and in what quality.
  std::thread recvThread(ClientNetworkLayer::receiver, clientNetworkLayer,
                         videoPlayer, bandwidthPredictor);

  std::thread videoPlayerThread(VideoPlayer::start, videoPlayer, tilePredictor);

  std::thread videoPlayerDecoderThread(VideoPlayer::decode, videoPlayer,
                                       decoder);

  std::thread senderThread(ClientNetworkLayer::sender, clientNetworkLayer);

  std::thread abrThread(AbrAlgorithm::runAbr, abr, tilePredictor, bandwidthPredictor,
                        clientNetworkLayer);

  videoPlayerThread.join();


  //abrThread.join();
  //senderThread.join();
  //recvThread.join();
  //videoPlayerDecoderThread.join();
}

Client::~Client() {}

int main(int argc, const char **argv) {
  Client *client = new Client();
  // to suppress warning
  assert(client != nullptr);
  return 0;
}
