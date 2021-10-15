/*
 * VideoPlayer.cpp
 *
 *  Created on: May 1, 2021
 *      Author: eghabash
 */

#include "VideoPlayer.h"

#include <stdio.h>

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

  frameId_ = 1;
  FPS_ = 25;
}

void VideoPlayer::addChunk(uint8_t *chunkPointer, uint32_t chunkSize,
                           uint32_t tileChunkIdx, uint16_t tileIdx) {
  // We take 4 bytes to exclude the "\r\n\r\n" out of chunk bytes.
  Chunk chunk = {chunkPointer, chunkSize - 4};

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
  while (true) {
    bool decode_frame = false;
    startChunk = ((videoPlayer->frameId_ - 1) / videoPlayer->FPS_) + 1;
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

          // insert to decodedTileChunks_
          videoPlayer->decodedTileChunksMutex_.lock();
          if (videoPlayer->decodedTileChunks_.find(chunks->first) !=
              videoPlayer->decodedTileChunks_.end()) {
            videoPlayer->decodedTileChunks_.find(chunks->first)
                ->second.insert(std::make_pair(tileInfo->first, rawTileFrames));

          } else {
            std::map<uint16_t, std::vector<uint8_t *>> temp;
            temp.insert(std::make_pair(tileInfo->first, rawTileFrames));

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
    }
  }
}

void VideoPlayer::start(VideoPlayer *videoPlayer,
                        TilePredictor *tilePredictor) {
  long renderTime;

  long frameGap = (1000.0 / videoPlayer->FPS_);

  uint32_t playSecond;
  // tileIndex, raw-tile-frame.
  std::map<uint16_t, uint8_t *> viewport;

  FILE *playLog;
  std::string filename = "play_log_" + videoPlayer->playLogTimestamp_ + ".txt";
  playLog = fopen(filename.c_str(), "wb");
  fprintf(playLog, "%-20s %-20s %-20s\n", "frame id", "deadline",
          "render time");

  while (true) {
    long frameDeadline = Util::getTime();

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
          auto &frame = rawTilesChunks.find(tileIdx)
                            ->second[videoPlayer->frameId_ % videoPlayer->FPS_];
          viewport.insert(std::make_pair(tileIdx, frame));
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
    renderTime = Util::getTime();
    fprintf(playLog, "%-20s %-20s %-20s\n",
            std::to_string(videoPlayer->frameId_).c_str(),
            std::to_string(frameDeadline).c_str(),
            std::to_string(renderTime).c_str());

    fflush(playLog);
    videoPlayer->stitchTileFrame(viewport, videoPlayer->frameId_);
    // free all tile-frames belonging to current frameId
    if (videoPlayer->frameId_ % videoPlayer->FPS_ == 0) {
      for (auto &pair :
           videoPlayer->decodedTileChunks_.find(playSecond)->second) {
        for (auto &pointer : pair.second) {
          free(pointer);
        }
      }
    }

    viewport.clear();
    if (videoPlayer->frameId_ == 1475) {
      LOG(INFO) << "Video Ended!";
      return;
    }
    Util::sleep(renderTime, frameGap);
    videoPlayer->frameId_++;
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
        auto srcAddress = row->tile + (320 * c);
        // AVFrame uncomment
        // auto srcAddress =  (row->tile->data[0] + (384 * c))
        memcpy(destAddress, srcAddress, 320);
      }

      // U-plane
      // The base memory location of the tile U values.
      int uTileBaseAddress = uBaseAddressInFrame +
                             ((tilesInRow * numOfRows * 320 * 160) / 4) +
                             tileCountInRow * 160;
      for (int c = 0; c < 80; c++) {
        auto destAddress = rawViewPort + uTileBaseAddress + (rowLengthUV * c);
        auto srcAddress = row->tile + (160 * c) + uBaseAddressInTile;
        // AVFrame uncomment
        // auto srcAddress = (row->tile->data[1] + (192 * c))
        memcpy(destAddress, srcAddress, 160);
      }

      // V-plane
      // The base memory location of the tile V values.
      int vTileBaseAddress = vBaseAddressInFrame +
                             ((tilesInRow * numOfRows * 320 * 160) / 4) +
                             tileCountInRow * 160;
      for (int c = 0; c < 80; c++) {
        auto destAddress = rawViewPort + vTileBaseAddress + (rowLengthUV * c);
        auto srcAddress = row->tile + (160 * c) + vBaseAddressInTile;
        // AVFrame uncomment
        // auto srcAddress = (row->tile->data[2] + (192 * c))
        memcpy(destAddress, srcAddress, 160);
      }

      row = row->nextTile;
      tileCountInRow++;
    }
    numOfRows++;
  } // end of stitching loop

  /*FILE *myfile;

  std::string filename =
      std::to_string(frameId) + "_" + std::to_string(tilesInRow * 320) + "X" +
      std::to_string(viewportLinkedList.size() * 160) + ".yuv";

  myfile = fopen(filename.c_str(), "wb");

  fwrite(rawViewPort, sizeof(uint8_t), numberOfTiles * tileSize, myfile);

  fclose(myfile);*/
}

void VideoPlayer::setPlayLogTimestamp(std::string playLogTimestamp) {
  playLogTimestamp_ = playLogTimestamp;
}

VideoPlayer::~VideoPlayer() {
  // TODO Auto-generated destructor stub
}
