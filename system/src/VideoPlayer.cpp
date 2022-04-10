/*
 * VideoPlayer.cpp
 *
 *  Created on: May 1, 2021
 *      Author: eghabash
 */

#include "VideoPlayer.h"

#include <stdio.h>
#include <sys/stat.h>

#include <boost/algorithm/string.hpp>
#include <boost/algorithm/string/regex.hpp>
#include <chrono>
#include <iostream>
#include <string>
#include <thread>

#include "Util.h"
#include "glog/logging.h"

VideoPlayer::VideoPlayer(std::string tilesPerFrameTracePath,
                         std::string vpCorrPerFrameTracePath) {
  // read ground truth.
  std::ifstream infile(tilesPerFrameTracePath);

  std::string line;
  int pos;
  uint32_t sec;
  std::string tiles;
  std::vector<std::string> tilesVec;
  while (std::getline(infile, line)) {
    pos = line.find(":");
    try {
      sec = static_cast<uint32_t>(std::stoi(line.substr(0, pos)));
    } catch (std::invalid_argument &e) {
      std::cout << "Error reading ground truth\n" << line << std::endl;
    }
    tiles = line.substr(pos + 2, line.size() - (pos + 3));

    boost::algorithm::split(tilesVec, tiles, boost::is_any_of(","));
    std::vector<uint16_t> t;
    for (auto &tile : tilesVec) {
      try {
        t.push_back(static_cast<uint16_t>(stoi(tile)));
      } catch (std::invalid_argument &e) {
        std::cout << "Error pushing ground truth\n" << line << std::endl;
      }
    }
    groundTruth_.insert(std::make_pair(sec, t));
  }

  std::ifstream infile2(vpCorrPerFrameTracePath);
  while (std::getline(infile2, line)) {
    auto pos = line.find(",");
    try {
      auto yaw = std::stof(line.substr(0, pos));
      auto pitch = std::stof(line.substr(pos + 1));
      groundTruthCoordinates_.push_back(std::make_pair(yaw, pitch));
    } catch (std::invalid_argument &e) {
      std::cout << "Error reading ground truth\n" << line << std::endl;
    }
  }
  std::string dirName = "yuv_frames_" + Util::getLogTimestamp();

  //+Util::getLogTimestamp().c_str()
  if (mkdir(dirName.c_str(), 0777) != 0) {
    LOG(ERROR) << "could not create directory for yuv frames";
  }

  frameId_ = 1;
  FPS_ = 25;
  userVpCorr.open("/home/ehab/Desktop/Project-V360/system/log_w.txt");
}

void VideoPlayer::addChunk(uint8_t *chunkPointer, uint32_t chunkSize,
                           uint32_t tileChunkIdx, uint16_t tileIdx,
                           uint8_t qualityIdx) {
  // We take 4 bytes to exclude the "\r\n\r\n" out of chunk bytes.
  Chunk chunk = {chunkPointer, chunkSize - 4, qualityIdx};
  // comment to turn off decoder.
  auto pair = chunks_.find(tileChunkIdx);
  if (pair != chunks_.end()) {
    recvChunKMutex_.lock();
    pair->second.insert(std::make_pair(tileIdx, chunk));
    recvChunKMutex_.unlock();
  } else {
    std::map<uint16_t, struct Chunk> tileIdxChunkMap;
    tileIdxChunkMap.insert(std::make_pair(tileIdx, chunk));
    chunks_.insert(std::make_pair(tileChunkIdx, tileIdxChunkMap));
  }

  // uncomment to turn off decoder.
  /*auto pair = decodedTileChunks_.find(tileChunkIdx);
  std::vector<uint8_t *> temp;
  if (pair != decodedTileChunks_.end()) {
    pair->second.insert(std::make_pair(tileIdx, temp));
  } else {
    std::map<uint16_t, std::vector<uint8_t *>> tileIdxChunkMap;
    tileIdxChunkMap.insert(std::make_pair(tileIdx, temp));
    decodedTileChunks_.insert(std::make_pair(tileChunkIdx, tileIdxChunkMap));
  }*/
}

void VideoPlayer::decode(VideoPlayer *videoPlayer, Decoder *decoder) {
  // TODO clear chunks of previous second from map.
  // TODO decode based on priority
  // TODO use list/set instead of map. Not sure!
  uint32_t startChunk;
  std::vector<std::string> chunksDecoded;
  bool first = true;
  std::unordered_set<int> freedChunk;
  while (true) {
    bool decode_frame = false;
    startChunk = ((videoPlayer->frameId_ - 1) / videoPlayer->FPS_) + 1;

    // free raw frames from previous chunks.
    for (auto freeIdx = startChunk - 2; freeIdx < startChunk; freeIdx++) {
      if (videoPlayer->decodedTileChunks_.find(freeIdx) ==
          videoPlayer->decodedTileChunks_.end()) {
        continue;
      }
      auto &decodedChunk = videoPlayer->decodedTileChunks_[freeIdx];
      for (auto &tile : decodedChunk) {
        if (tile.second.first.size() == 0) {
          continue;
        }
        for (auto &ptr : tile.second.first) {
          free(ptr);
        }
        tile.second.first.clear();
      }
    }

    for (uint32_t idx = startChunk; idx < startChunk + 2; idx++) {
      // chunks have presentation time first, and map<tile index, encoded tile
      // frames> second.
      auto chunks = videoPlayer->chunks_.find(idx);
      if (chunks != videoPlayer->chunks_.end()) {
        // tileInfo has tileIndex first, and encoded tile frames second.
        while (chunks->second.size() != 0) {
          auto tileInfo = chunks->second.begin();
          std::vector<uint8_t *> rawTileFrames;
          // std::vector<AVFrame *> rawTileFrames;

          if (first) {
            first = false;
            rawTileFrames.clear();
            decoder->decodeNotOptimized(tileInfo->second.chunk,
                                        tileInfo->second.chunkSize,
                                        rawTileFrames);
          }

          // call decoder
          /*std::cout << "------\n"
                    << "decoding time [" << chunks->first << "_"
                    << tileInfo->first << "]\n";*/
          // auto decodeStart = Util::getTime();
          decoder->decodeNotOptimized(tileInfo->second.chunk,
                                      tileInfo->second.chunkSize,
                                      rawTileFrames);
          /*std::cout << "Total Decoding :" << Util::getTime() - decodeStart
                    << "\n";*/
          /*std::cout << "Decoded:" << idx << "_"
                    << std::to_string(tileInfo->first) << "_"
                    << std::to_string(tileInfo->second.qualityIdx) <<
             std::endl;*/
          // insert to decodedTileChunks_

          auto tileQuality = tileInfo->second.qualityIdx;

          videoPlayer->decodedTileChunksMutex_.lock();
          if (videoPlayer->decodedTileChunks_.find(chunks->first) !=
              videoPlayer->decodedTileChunks_.end()) {

            auto &chunkTilesInfo =
                videoPlayer->decodedTileChunks_.find(chunks->first)->second;
            // tile already recieved in bg quality.
            // so update it.
            if (chunkTilesInfo.find(tileInfo->first) != chunkTilesInfo.end()) {

              auto rawFramesToFree = chunkTilesInfo[tileInfo->first].first;

              chunkTilesInfo.find(tileInfo->first)->second = {rawTileFrames,
                                                              tileQuality};
              // free raw bg tiles
              for (auto &ptr : rawFramesToFree) {
                free(ptr);
              }

              /*std::cout << "Qupdate:" << std::to_string(chunks->first) << "_"
                        << std::to_string(tileInfo->first) << "_"
                        << std::to_string(tileQuality) << "\n";*/
            } else {
              // first time tile is received.
              videoPlayer->decodedTileChunks_.find(chunks->first)
                  ->second.insert(
                      {tileInfo->first, {rawTileFrames, tileQuality}});
            }
            /*std::cout << std::to_string(videoPlayer->decodedTileChunks_
                                            .find(chunks->first)
                                            ->second.find(tileInfo->first)
                                            ->second.second)
                      << std::endl;*/

          } else {
            std::map<uint16_t, std::pair<std::vector<uint8_t *>, uint8_t>> temp;
            temp.insert({tileInfo->first, {rawTileFrames, tileQuality}});

            videoPlayer->decodedTileChunks_.insert(
                std::make_pair(chunks->first, temp));
          }
          videoPlayer->decodedTileChunksMutex_.unlock();

          // free chunks.
          auto &encodedFrameStruct = tileInfo->second;
          free(encodedFrameStruct.chunk);
          videoPlayer->recvChunKMutex_.lock();
          chunks->second.erase(tileInfo->first);
          videoPlayer->recvChunKMutex_.unlock();
          decode_frame = true;
          break;
        }
      }
      if (decode_frame) {
        break;
      }

      // delete tiles that will not be uses.
      /*for (auto &chunk : videoPlayer->chunks_) {
        if (chunk.first < startChunk) {
          for (auto &tile : chunk.second) {
            if (tile.second.chunk != nullptr) {
              free(tile.second.chunk);
            }
          }
        }
      }*/
    }
  }
}

void VideoPlayer::startVideoWithSkip(VideoPlayer *videoPlayer,
                                     TilePredictor *tilePredictor) {
  long renderTime;

  long frameGap = (1000.0 / videoPlayer->FPS_);

  uint32_t playSecond;
  // tileIndex, raw-tile-frame.
  std::map<uint16_t, uint8_t *> viewport;

  FILE *playLog;
  std::string filename = "play_log_" + Util::getLogTimestamp() + ".txt";
  playLog = fopen(filename.c_str(), "wb");
  fprintf(playLog, "%-20s %-20s %-20s %-20s %10s\n", "frame id", "deadline",
          "render time", "skipped tiles", "tiles_quality");
  // list of all tiles we had to skip for the current frame.
  std::string skippedTiles;
  // For the first frame in the video, we don't skip any tiles (allow join time)
  bool firstFrame = true;

  // if the tile is not received by its deadline, then skip it.
  bool skipTile;

  // if no tile-chunks have been received, then skip them all.
  bool haveTilesForCurrentSecond;

  // if the needed tile has not been received, the skip it.
  bool haveReceivedTile;

  // this will log all tiles along with their quality (tileIdx_tileQuality),
  // separated by a comma.
  std::string tilesQuality;

  while (true) {
    long frameDeadline = Util::getTime();
    // videoPlayer->getVpCorrInRealTime();
    // add current user's coordinate to ground truth.
    tilePredictor->addVpCoordinate(
        videoPlayer->groundTruthCoordinates_[videoPlayer->frameId_ - 1]);

    // all tiles needed to construct current frame.
    auto tiles = videoPlayer->groundTruth_.find(videoPlayer->frameId_);
    if (tiles == videoPlayer->groundTruth_.end()) {
      // no more frames;
      LOG(INFO) << "No more frames to play!";
      break;
    }

    tilesQuality = "";

    skippedTiles = "";
    // for each tile.
    for (auto tileIdx : tiles->second) {

      skipTile = false;
      haveTilesForCurrentSecond = false;
      haveReceivedTile = false;
      playSecond = ((videoPlayer->frameId_ - 1) / videoPlayer->FPS_) + 1;

      // first, check if any tile-chunk that correspond to current second has
      // been received or not. If not, and this is the first frame in the video,
      // then wait. Otherwise, skip.
      while (!haveTilesForCurrentSecond && !skipTile) {
        videoPlayer->decodedTileChunksMutex_.lock();
        if (videoPlayer->decodedTileChunks_.find(playSecond) !=
            videoPlayer->decodedTileChunks_.end()) {
          haveTilesForCurrentSecond = true;
        }
        videoPlayer->decodedTileChunksMutex_.unlock();
        if (!firstFrame && !haveTilesForCurrentSecond) {
          skipTile = true;
        }
      }

      // check if the tile has been received, if so add the raw tile-frame to
      // final viewport list for stitching. If not, and this is not the first
      // frame, then wait until tile-chunk is receieved.
      if (videoPlayer->decodedTileChunks_.find(playSecond) !=
              videoPlayer->decodedTileChunks_.end() &&
          !skipTile) {
        auto &rawTilesChunks =
            videoPlayer->decodedTileChunks_.find(playSecond)->second;

        // get all frames in tile-chunk.
        while (!haveReceivedTile && !skipTile) {
          videoPlayer->decodedTileChunksMutex_.lock();
          if (rawTilesChunks.find(tileIdx) != rawTilesChunks.end()) {
            haveReceivedTile = true;
          }
          videoPlayer->decodedTileChunksMutex_.unlock();
          if (!firstFrame && !haveReceivedTile) {
            skipTile = true;
          }
        }

        // if the tile-frame received, then add it to viewport.
        if (!skipTile && rawTilesChunks.find(tileIdx) != rawTilesChunks.end()) {
          auto &framePtrQualityPair = rawTilesChunks.find(tileIdx)->second;
          auto &frame =
              framePtrQualityPair
                  .first[(videoPlayer->frameId_ - 1) % videoPlayer->FPS_];
          tilesQuality += std::to_string(tileIdx) + "_" +
                          std::to_string(framePtrQualityPair.second) + ",";
          viewport.insert(std::make_pair(tileIdx, frame));
        }
      }

      if (skipTile) {
        viewport.insert(std::make_pair(tileIdx, nullptr));
        skippedTiles += std::to_string(tileIdx) + ",";
        // LOG(INFO) << "Skip: <" << videoPlayer->frameId_ << "," << tileIdx
        //        << ">";
      }
    }
    firstFrame = false;
    LOG(INFO) << "Stitching F#" << videoPlayer->frameId_ << "\n====";

    // stichFrames.
    renderTime = Util::getTime();
    skippedTiles.pop_back();
    fprintf(playLog, "%-20s %-20s %-20s %-20s %10s\n",
            std::to_string(videoPlayer->frameId_).c_str(),
            std::to_string(frameDeadline).c_str(),
            std::to_string(renderTime).c_str(), skippedTiles.c_str(),
            tilesQuality.c_str());

    fflush(playLog);
    videoPlayer->stitchTileFrame(viewport, videoPlayer->frameId_);
    // if (videoPlayer->frameId_ % videoPlayer->FPS_ == 0) {
    //   if (videoPlayer->decodedTileChunks_.find(playSecond) !=
    //       videoPlayer->decodedTileChunks_.end()) {
    //     for (auto &tileInfo :
    //          videoPlayer->decodedTileChunks_.find(playSecond)->second) {
    //       for (auto &tileRawFramePtr : tileInfo.second.first) {
    //         free(tileRawFramePtr);
    //       }
    //     }
    //   }
    // }
    Util::setFramePlayTime(renderTime);
    videoPlayer->freeSkipTileMapCurrentFrame();
    videoPlayer->frameId_++;
    viewport.clear();
    if (videoPlayer->frameId_ == 1476) {
      LOG(INFO) << "Video Ended!";
      return;
    }
    Util::sleep(renderTime, frameGap);
  }
}

void VideoPlayer::startVideoWithRebuffer(VideoPlayer *videoPlayer,
                                         TilePredictor *tilePredictor) {
  long renderTime;

  long frameGap = (1000.0 / videoPlayer->FPS_);

  uint32_t playSecond;
  // tileIndex, raw-tile-frame.
  std::map<uint16_t, uint8_t *> viewport;

  FILE *playLog;
  std::string filename = "play_log_" + Util::getLogTimestamp() + ".txt";
  playLog = fopen(filename.c_str(), "wb");
  fprintf(playLog, "%-20s %-20s %-20s %-20s\n", "frame id", "deadline",
          "render time", "tiles_quality");

  std::string tilesQuality;
  while (true) {
    long frameDeadline = Util::getTime();
    tilesQuality = "";
    // LOG(INFO) << "Playing Frame#" << videoPlayer->frameId_;
    bool check1 = true;
    bool check2 = true;
    tilePredictor->addVpCoordinate(
        videoPlayer->groundTruthCoordinates_[videoPlayer->frameId_ - 1]);

    // all tiles to present in the current frame.
    auto tiles = videoPlayer->groundTruth_.find(videoPlayer->frameId_);
    if (tiles == videoPlayer->groundTruth_.end()) {
      // no more frames;
      LOG(INFO) << "No frames";
      break;
    }

    // for each tile.
    for (auto tileIdx : tiles->second) {
      playSecond = ((videoPlayer->frameId_ - 1) / videoPlayer->FPS_) + 1;
      while (check1) {
        videoPlayer->decodedTileChunksMutex_.lock();
        if (videoPlayer->decodedTileChunks_.find(playSecond) !=
            videoPlayer->decodedTileChunks_.end()) {
          check1 = false;
        }
        videoPlayer->decodedTileChunksMutex_.unlock();
      }
      check1 = true;
      // decoded chunks with frames belong to current presentation time.
      // this gets all the raw chunks for all tiles at chunk = play-second.

      if (videoPlayer->decodedTileChunks_.find(playSecond) !=
          videoPlayer->decodedTileChunks_.end()) {
        auto &rawTilesChunks =
            videoPlayer->decodedTileChunks_.find(playSecond)->second;

        // get all frames of chunk.
        while (check2) {
          videoPlayer->decodedTileChunksMutex_.lock();
          if (rawTilesChunks.find(tileIdx) != rawTilesChunks.end()) {
            check2 = false;
          }
          videoPlayer->decodedTileChunksMutex_.unlock();
        }
        check2 = true;

        if (rawTilesChunks.find(tileIdx) != rawTilesChunks.end()) {
          auto &framePtrQualityPair = rawTilesChunks.find(tileIdx)->second;
          auto &frame =
              framePtrQualityPair
                  .first[(videoPlayer->frameId_ - 1) % videoPlayer->FPS_];

          viewport.insert(std::make_pair(tileIdx, frame));

          tilesQuality += std::to_string(tileIdx) + "_" +
                          std::to_string(framePtrQualityPair.second) + ",";

        } else {
          // tile is missing. or not decoded.
          VLOG(2) << "MISS:" << rawTilesChunks.find(tileIdx)->first;
        }
      } else {
        // schedule urgent request.
        // all tiles are needed.
      }
    }
    LOG(INFO) << "Stitching F#" << videoPlayer->frameId_ << "\n====";

    // stichFrames.
    tilesQuality.pop_back();
    renderTime = Util::getTime();
    fprintf(playLog, "%-20s %-20s %-20s %-20s\n",
            std::to_string(videoPlayer->frameId_).c_str(),
            std::to_string(frameDeadline).c_str(),
            std::to_string(renderTime).c_str(), tilesQuality.c_str());

    fflush(playLog);
    videoPlayer->stitchTileFrame(viewport, videoPlayer->frameId_);
    Util::setFramePlayTime(renderTime);
    videoPlayer->frameId_++;
    viewport.clear();
    if (videoPlayer->frameId_ == 1476) {
      LOG(INFO) << "Video Ended!";
      return;
    }
    Util::sleep(renderTime, frameGap);
  }
}

template <typename T>
void VideoPlayer::orderTilesToLinkedList(
    std::map<uint16_t, T *> &viewport,
    std::vector<Node<T> *> &viewportLinkedList) {
  int tileWidth = 360 / 30;
  int tileHeight = 180 / 15;
  int prevRow = -1;
  int prevCol = -1;
  // this points to where to place next tiles in the linkedlist.
  Node<T> *nextTile;
  // this points to the first frame in row.
  Node<T> *head;

  // loop over all tiles
  for (auto tilePair : viewport) {
    int tileRow = ((tilePair.first - 1) / tileHeight) + 1; // 1--> 12 same row.
    int tileCol = ((tilePair.first - 1) % tileWidth) + 1;  // 1--> 12
    if (tileRow != prevRow) {
      // first tile in the row, then create row linkedlist.
      Node<T> *tileNode = new Node<T>;
      tileNode->tile = tilePair.second;
      tileNode->nextTile = nullptr;
      nextTile = tileNode;
      head = tileNode;
      viewportLinkedList.push_back(tileNode);
    } else if (tileRow == prevRow && tileCol - 1 != prevCol) {
      // An overlap in row-tiles.
      Node<T> *tileNode = new Node<T>;
      tileNode->tile = tilePair.second;
      tileNode->nextTile = head;
      nextTile = tileNode;
      viewportLinkedList.pop_back();
      viewportLinkedList.push_back(tileNode);
    } else {
      // Another tile in the row.
      Node<T> *tileNode = new Node<T>;
      tileNode->tile = tilePair.second;
      tileNode->nextTile = nullptr;
      if (nextTile->nextTile != nullptr) {
        // there is an overlap in this row.
        tileNode->nextTile = nextTile->nextTile;
        nextTile->nextTile = tileNode;
        nextTile = tileNode;
      } else {
        // there is no overlap yet.
        nextTile->nextTile = tileNode;
        nextTile = tileNode;
      }
    }
    prevRow = tileRow;
    prevCol = tileCol;
  }
}

template <typename T>
void VideoPlayer::stitchTileFrame(std::map<uint16_t, T *> &viewport,
                                  int frameId) {
  std::vector<Node<T> *> viewportLinkedList;
  orderTilesToLinkedList(viewport, viewportLinkedList);
  if (viewportLinkedList.size() == 0) {
    LOG(ERROR) << "NO tiles to stitch!";
    return;
  }
  if (!std::is_same<T, uint8_t>::value && !std::is_same<T, AVFrame>::value) {
    LOG(ERROR) << "Invalid raw frame type!";
    return;
  }

  // the number of tiles in a single row.
  int tilesInRow = 0;
  // the total number of tiles in stitched frame.
  int numberOfTiles = 0;

  auto rowHead = viewportLinkedList[0];
  while (rowHead != nullptr) {
    rowHead = rowHead->nextTile;
    tilesInRow++;
  }
  numberOfTiles = tilesInRow * viewportLinkedList.size();
  // size of raw tile in YUV420P format.
  uint32_t tileSize = (320 * 160 * 12) / 8;

  // size of raw viewport.
  uint8_t *rawViewPort =
      (uint8_t *)malloc(sizeof(uint8_t) * viewport.size() * tileSize);

  // the length of a single row in Y plane
  int rowLengthY = 320 * tilesInRow;
  int rowLengthUV = 160 * tilesInRow;

  // Where is the first U value address in stitched frame.
  int uBaseAddressInFrame = 320 * 160 * numberOfTiles;
  int vBaseAddressInFrame = uBaseAddressInFrame + uBaseAddressInFrame / 4;

  int uBaseAddressInTile = 320 * 160;
  int vBaseAddressInTile = uBaseAddressInTile + uBaseAddressInTile / 4;
  // Y loc
  // number of rows * tiles per row.
  // loc of tile in row.
  int numOfRows = 0;
  for (auto &row : viewportLinkedList) { // start of stitching loop
    if (row == nullptr) {
      LOG(ERROR) << "Row of tiles starts with null";
      return;
    }
    int tileCountInRow = 0;
    while (row != nullptr) {
      // Y-plane
      // The base memory location of the tile Y values.
      // This mainly equals to the number of tiles in all previous rows
      // [tileInRow * numOfRows * 320 * 160] + number of pixels in the same row
      // [tileCountInRow * 320]
      int yBaseTileAddress =
          (tilesInRow * numOfRows * 320 * 160) + (tileCountInRow * 320);
      for (int c = 0; c < 160; c++) {
        auto destAddress = rawViewPort + yBaseTileAddress + (rowLengthY * c);
        if (row->tile != nullptr) {
          auto srcAddress = row->tile + (320 * c);
          // AVFrame uncomment
          // auto srcAddress =  (row->tile->data[0] + (384 * c))
          memcpy(destAddress, srcAddress, 320);
        } else {
          // skip tile, set color to black (Y:0, U:128, V:128)
          memset(destAddress, 0, 320);
        }
      }

      // U-plane
      // The base memory location of the tile U values.
      int uTileBaseAddress = uBaseAddressInFrame +
                             ((tilesInRow * numOfRows * 320 * 160) / 4) +
                             tileCountInRow * 160;
      for (int c = 0; c < 80; c++) {
        auto destAddress = rawViewPort + uTileBaseAddress + (rowLengthUV * c);
        if (row->tile != nullptr) {
          auto srcAddress = row->tile + (160 * c) + uBaseAddressInTile;
          // AVFrame uncomment
          // auto srcAddress = (row->tile->data[1] + (192 * c))
          memcpy(destAddress, srcAddress, 160);
        } else {
          // skip tile, set color to black (Y:0, U:128, V:128)
          memset(destAddress, 128, 160);
        }
      }

      // V-plane
      // The base memory location of the tile V values.
      int vTileBaseAddress = vBaseAddressInFrame +
                             ((tilesInRow * numOfRows * 320 * 160) / 4) +
                             tileCountInRow * 160;
      for (int c = 0; c < 80; c++) {
        auto destAddress = rawViewPort + vTileBaseAddress + (rowLengthUV * c);
        if (row->tile != nullptr) {
          auto srcAddress = row->tile + (160 * c) + vBaseAddressInTile;
          // AVFrame uncomment
          // auto srcAddress = (row->tile->data[2] + (192 * c))
          memcpy(destAddress, srcAddress, 160);
        } else {
          // skip tile, set color to black (Y:0, U:128, V:128)
          memset(destAddress, 128, 160);
        }
      }

      row = row->nextTile;
      tileCountInRow++;
    }
    numOfRows++;
  } // end of stitching loop

  FILE *myfile;

  std::string filename =
      "yuv_frames_" + Util::getLogTimestamp() + "/" + std::to_string(frameId) +
      "_" + std::to_string(tilesInRow * 320) + "X" +
      std::to_string(viewportLinkedList.size() * 160) + ".yuv";

  myfile = fopen(filename.c_str(), "wb");

  fwrite(rawViewPort, sizeof(uint8_t), numberOfTiles * tileSize, myfile);

  fclose(myfile);
}

uint32_t VideoPlayer::getFrameToRenderId() { return frameId_; }

VideoPlayer::~VideoPlayer() {
  // TODO Auto-generated destructor stub
}

void VideoPlayer::setTileToSkip(uint32_t frameId, uint16_t tile) {
  skipTileMutex_.lock();
  if (tilesInFrameToSkip.find(frameId) == tilesInFrameToSkip.end()) {
    std::unordered_set<uint16_t> initSet;
    tilesInFrameToSkip.insert(std::make_pair(frameId, initSet));
  }
  tilesInFrameToSkip.find(frameId)->second.insert(tile);
  skipTileMutex_.unlock();
}

bool VideoPlayer::skipThisTile(uint16_t tileId) {
  auto skippedTiles = tilesInFrameToSkip.find(frameId_);
  if (skippedTiles != tilesInFrameToSkip.end()) {
    if (skippedTiles->second.find(tileId) != skippedTiles->second.end()) {
      return true;
    }
  }
  return false;
}

void VideoPlayer::freeSkipTileMapCurrentFrame() {
  skipTileMutex_.lock();
  if (tilesInFrameToSkip.find(frameId_) != tilesInFrameToSkip.end()) {
    tilesInFrameToSkip.erase(frameId_);
  }
  skipTileMutex_.unlock();
}

std::pair<float, float> VideoPlayer::getVpCorrInRealTime() {

  // limit the number of char per line.
  std::string line = "";
  while (line.size() != 20) {
    getline(userVpCorr, line);
  }
  std::cout << Util::getTime() << "   : " << line << std::endl;
  return {180, 90};
}

std::vector<uint16_t> VideoPlayer::getTiles(TilePredictor *tilePredictor,
                                            std::pair<float, float> vpCorr) {
  std::vector<uint16_t> tilesInViewport;
  std::map<float, std::vector<uint16_t>> sortedTilesMap;
  std::pair<int, int> viewportResolution = {100, 100};
  tilePredictor->sortTileSetByArea(sortedTilesMap, vpCorr, viewportResolution);

  for (auto &fracTileSet : sortedTilesMap) {
    if (fracTileSet.first == 1) {
      continue;
    }
    for (auto &tile : fracTileSet.second) {
      tilesInViewport.push_back(tile);
    }
  }
  return tilesInViewport;
}