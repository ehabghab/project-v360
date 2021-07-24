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

VideoPlayer::VideoPlayer() {
  // read ground truth.
  std::string tracePath =
      "/Users/eghabash/Desktop/360 Video/Project-V360"
      "/split/tiles_per_frame_synthetic_user_1.txt";
  std::ifstream infile(tracePath);

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

  tracePath =
      "/Users/eghabash/Desktop/360 Video/Project-V360"
      "/split/vp_corr_per_frame_synthetic_user_1.txt";
  std::ifstream infile2(tracePath);
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

  auto pair = chunks_.find(tileChunkIdx);
  if (pair != chunks_.end()) {
    pair->second.insert(std::make_pair(tileIdx, chunk));
  } else {
    std::map<uint16_t, struct Chunk> tileIdxChunkMap;
    tileIdxChunkMap.insert(std::make_pair(tileIdx, chunk));
    chunks_.insert(std::make_pair(tileChunkIdx, tileIdxChunkMap));
  }
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

          // call decoder
          auto xs = Util::getTime();
          decoder->decode(tileInfo->second.chunk, tileInfo->second.chunkSize,
                          rawTileFrames);

          // std::cout << chunks->first << ":" << tileInfo->first << ":"
          //        << Util::getTime() - xs << std::endl;

          /*if (first) {
            auto xs = Util::getTime();
            first = false;
            rawTileFrames.clear();
            decoder->decode(tileInfo->second.chunk, tileInfo->second.chunkSize,
                            rawTileFrames);
            std::cout << chunks->first << ":" << tileInfo->first << ":"
                      << Util::getTime() - xs << std::endl;
          }*/
          // insert to decodedTileChunks_
          videoPlayer->decodedTileChunksMutex_.lock();
          if (videoPlayer->decodedTileChunks_.find(chunks->first) !=
              videoPlayer->decodedTileChunks_.end()) {
            videoPlayer->decodedTileChunks_.find(chunks->first)
                ->second.insert(std::make_pair(tileInfo->first, rawTileFrames));
            // std::cout<<"Added,"<<chunks->first<<":"<<tileInfo->first<<std::endl;
          } else {
            std::map<uint16_t, std::vector<uint8_t *>> temp;
            temp.insert(std::make_pair(tileInfo->first, rawTileFrames));

            videoPlayer->decodedTileChunks_.insert(
                std::make_pair(chunks->first, temp));
            // std::cout<<"Added,"<<chunks->first<<":"<<tileInfo->first<<std::endl;
            // return;
          }
          videoPlayer->decodedTileChunksMutex_.unlock();

          // free chunks.
          auto &encodedFrameStruct = tileInfo->second;
          free(encodedFrameStruct.chunk);
          chunks->second.erase(tileInfo->first);
          decode_frame = true;
          break;
        }
      }
      if (decode_frame) {
        break;
      }
      // std::cout<<"-----"<<std::endl;
    }
    // startChunk += 2;
    // videoPlayer->frameId_ += videoPlayer->FPS_*2;
    // sleep(100);
  }

  // FPS
  // 1000 second.
}

void VideoPlayer::start(VideoPlayer *videoPlayer,
                        TilePredictor *tilePredictor) {
  long stime;

  long frameGap = (1000.0 / videoPlayer->FPS_);

  uint32_t playSecond;
  // tileIndex, raw-tile-frame.
  std::map<uint16_t, uint8_t *> viewport;
  while (true) {
    long pt = Util::getTime();
    LOG(INFO) << "Playing Frame#" << videoPlayer->frameId_;
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
          std::cout << "MISS:" << rawTilesChunks.find(tileIdx)->first
                    << std::endl;
          // tile is missing. or not decoded.
        }

      } else {
        // schedule urgent request.
        // all tiles are needed.
      }
    }
    if ((Util::getTime() - pt) > 5) {
      LOG(INFO) << "-------------";
    }
    LOG(INFO) << "Stitching F#" << videoPlayer->frameId_ << "\n===";

    // stichFrames.
    stime = Util::getTime();
    auto rawViewPort = videoPlayer->stitchTileFrames(viewport);
    free(rawViewPort);

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
    }
    Util::sleep(stime, frameGap);
    // stime += frameGap;
    videoPlayer->frameId_++;
  }
}

int frm = 1;
uint8_t *VideoPlayer::stitchTileFrames(
    std::map<uint16_t, uint8_t *> &viewport) {
  // assume that tile scheme is 12x12.
  uint32_t tileSize = 320 * 160 * 4;
  // assume that frame is in ARGB format.
  uint8_t *rawViewPort =
      (uint8_t *)malloc(sizeof(uint8_t) * viewport.size() * tileSize);

  // number of tiles in col.
  // number of rows.
  // start index.

  int tileWidth = 360 / 30;
  int tileHeight = 180 / 15;

  uint16_t startIdx;
  int row;
  int col;
  int prevRow = -1;
  int prevCol = -1;
  int numOfRows = 1;
  int numOfCols = 1;
  bool colScanned = false;
  std::string _all;
  for (auto &pair : viewport) {
    row = ((pair.first - 1) / tileHeight) + 1;  // 1--> 12 same row.
    col = ((pair.first - 1) % tileWidth) + 1;   // 1--> 12
    _all += std::to_string(pair.first) + ",";
    if (prevRow == -1 && prevCol == -1) {
      startIdx = pair.first;
    }

    if (prevRow != row && prevRow != -1) {
      if (prevRow != row - 1) {
        startIdx = pair.first;
        colScanned = false;

      } else {
        colScanned = true;
      }
      numOfRows++;
    } else if (prevCol != -1) {
      if (prevCol != col - 1 && !colScanned) {
        startIdx = pair.first;
      }
      numOfCols = colScanned ? numOfCols : numOfCols + 1;
    }
    prevRow = row;
    prevCol = col;
  }

  // LOG(INFO) << numOfCols * 320 << "x" << numOfRows * 160 << "\n------";

  std::string _order = "";
  int t1 = std::chrono::duration_cast<std::chrono::milliseconds>(
               std::chrono::system_clock::now().time_since_epoch())
               .count();
  int tileIdx;
  int currRow;
  // row is 160 * 4.
  // loop from 0 to 320
  // row * 320 * 160 * 4. is my base.
  int baseBytes;
  int colBytes;
  int count = 0;
  int stepSize = 320 * 4;
  for (int row = 0; row < numOfRows; row++) {
    baseBytes = tileSize * count;
    if (startIdx + tileWidth * row > tileWidth * tileHeight) {
      startIdx = ((startIdx - 1) % tileWidth) + 1;
      numOfRows -= row;
      row = 0;
    }
    tileIdx = startIdx + tileWidth * row;

    for (int col = 0; col < numOfCols; col++) {
      colBytes = baseBytes + stepSize * col;
      int tempRow = ((tileIdx + col - 1) / tileHeight) + 1;
      if (col != 0 && tempRow != currRow) {
        _order += std::to_string(tileIdx + col - tileWidth) + " ,";
        for (int ij = 0; ij < 160; ij++) {
          memcpy(rawViewPort + (colBytes + ij * numOfCols * stepSize),
                 viewport.find(tileIdx + col - tileWidth)->second +
                     (ij * stepSize),
                 stepSize);
        }

      } else {
        for (int ij = 0; ij < 160; ij++) {
          memcpy(rawViewPort + (colBytes + ij * numOfCols * stepSize),
                 viewport.find(tileIdx + col)->second + (ij * stepSize),
                 stepSize);
        }
        _order += std::to_string(tileIdx + col) + " ,";
        currRow = tempRow;
      }

      count++;
    }
    // check if I went outside.
  }

  int t2 = std::chrono::duration_cast<std::chrono::milliseconds>(
               std::chrono::system_clock::now().time_since_epoch())
               .count();

  // std::cout<<frm<<":"<<t2-t1<<std::endl;
  FILE *myfile;

  std::string filename = std::to_string(frm++) + ".yuv";

  myfile = fopen(filename.c_str(), "wb");

  fwrite(rawViewPort, sizeof(uint8_t), viewport.size() * tileSize, myfile);

  fclose(myfile);

  return rawViewPort;
}

VideoPlayer::~VideoPlayer() {
  // TODO Auto-generated destructor stub
}
