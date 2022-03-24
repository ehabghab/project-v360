/*
 * Client.cpp
 *
 *  Created on: May 2, 2021
 *      Author: eghabash
 */

#include "Client.h"

#include <thread>

#include <gflags/gflags.h>
#include <glog/logging.h>

#include "AbrAlgorithm.h"
#include "ClientNetworkLayer.h"
#include "Decoder.h"
#include "VideoPlayer.h"
DEFINE_bool(utilityAbr, true, "true : utility, false : flare");
DEFINE_bool(skipModel, true, "true : skip model, false : rebuffer model");

Client::Client(std::string tilesPerFrameTracePath,
               std::string vpCorrPerFrameTracePath,
               std::string tileChunkSizesTracePath,
               std::string backgroundDisplacementTrace, std::string serverIp) {
  // Initiate all instances to create threads.
  // 1- Network layer (sender and receiver).
  // 2- Video player along with the decoder.
  // 3- ABR algorithm along with tile and bandwidth predictors.
  ClientNetworkLayer *clientNetworkLayer = new ClientNetworkLayer(serverIp);
  VideoPlayer *videoPlayer =
      new VideoPlayer(tilesPerFrameTracePath, vpCorrPerFrameTracePath);
  Decoder *decoder = new Decoder();
  AbrAlgorithm *abr =
      new AbrAlgorithm(tileChunkSizesTracePath, backgroundDisplacementTrace);
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

  std::thread videoPlayerThread;
  if (FLAGS_skipModel) {
    videoPlayerThread = std::thread(VideoPlayer::startVideoWithSkip,
                                    videoPlayer, tilePredictor);
  } else if (!FLAGS_skipModel && !FLAGS_utilityAbr) {
    videoPlayerThread = std::thread(VideoPlayer::startVideoWithRebuffer,
                                    videoPlayer, tilePredictor);
  } else {
    LOG(ERROR) << "Utility ABR does not support rebuffering.";
    return;
  }

  std::thread videoPlayerDecoderThread(VideoPlayer::decode, videoPlayer,
                                       decoder);

  std::thread senderThread(ClientNetworkLayer::sender, clientNetworkLayer);
  std::thread abrThread;
  if (FLAGS_utilityAbr) {
    abrThread =
        std::thread(AbrAlgorithm::utilityAbr, abr, tilePredictor,
                    bandwidthPredictor, clientNetworkLayer, videoPlayer);
    LOG(INFO) << "Utility";
  } else {
    abrThread =
        std::thread(AbrAlgorithm::flareAbr, abr, tilePredictor,
                    bandwidthPredictor, clientNetworkLayer, videoPlayer);
    LOG(INFO) << "Flare";
  }

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
                  "<vp_corrdinates_per_frame> <tile_chunk_sizes> "
                  "<background_displacement> <server_ip>";
    return -1;
  }
  google::SetLogDestination(google::INFO, "client_log.txt");
  google::InitGoogleLogging(argv[0]);
  gflags::ParseCommandLineFlags(&argc, &argv, true);

  Client *client = new Client(argv[1], argv[2], argv[3], argv[4], argv[5]);
  // to suppress warning
  assert(client != nullptr);
  return 0;
}
