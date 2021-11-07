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
#include "glog/logging.h"

Client::Client(std::string tilesPerFrameTracePath,
               std::string vpCorrPerFrameTracePath,
               std::string tileChunkSizesTracePath, std::string serverIp) {
  // Initiate all instances to create threads.
  // 1- Network layer (sender and receiver).
  // 2- Video player along with the decoder.
  // 3- ABR algorithm along with tile and bandwidth predictors.

  ClientNetworkLayer *clientNetworkLayer = new ClientNetworkLayer(serverIp);
  VideoPlayer *videoPlayer =
      new VideoPlayer(tilesPerFrameTracePath, vpCorrPerFrameTracePath);
  Decoder *decoder = new Decoder();
  AbrAlgorithm *abr = new AbrAlgorithm(tileChunkSizesTracePath);
  TilePredictor *tilePredictor = new TilePredictor(vpCorrPerFrameTracePath);
  BandwidthPredictor *bandwidthPredictor = new BandwidthPredictor();

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

  std::thread abrThread(AbrAlgorithm::runAbr, abr, tilePredictor,
                        bandwidthPredictor, clientNetworkLayer, videoPlayer);

  videoPlayerThread.join();

  // abrThread.join();
  // senderThread.join();
  // recvThread.join();
  // videoPlayerDecoderThread.join();
}

Client::~Client() {}

int main(int argc, char **argv) {
  if (argc < 5) {
    LOG(ERROR) << "Usage: ./client <tiles_per_frame_trace> "
                  "<vp_corrdinates_per_frame> <tile_chunk_sizes> <server_ip>";
    return -1;
  }

  Client *client = new Client(argv[1], argv[2], argv[3], argv[4]);
  // to suppress warning
  assert(client != nullptr);
  return 0;
}
