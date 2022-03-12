/*
 * BandwidthPredictor.cpp
 *
 *  Created on: Jun 2, 2021
 *      Author: eghabash
 */

#include "BandwidthPredictor.h"

#include <cmath>
#include <iostream>

BandwidthPredictor::BandwidthPredictor() {
  numOfChunks_ = 0;
  tileSizesSum_ = 0;
  totalDownloadTimeInMS_ = 0;
  tilesHistory_ = {};
}

void BandwidthPredictor::addTileInfo(uint32_t tileSize, int downloadTimeInMS) {
  tileInfoMutex_.lock();
  tileSizesSum_ += tileSize;
  totalDownloadTimeInMS_ += downloadTimeInMS;
  numOfChunks_ += 0;
  tileInfoMutex_.unlock();
}

std::pair<uint32_t, int> BandwidthPredictor::getCurrentTilesInfo() {
  tileInfoMutex_.lock();
  std::pair<uint32_t, int> avgParameters = {tileSizesSum_,
                                            totalDownloadTimeInMS_};
  tileSizesSum_ = 0;
  totalDownloadTimeInMS_ = 0;
  tileInfoMutex_.unlock();
  return avgParameters;
}

float BandwidthPredictor::getMpcBandwidthPrediction() {

  // ToDo return mpc avg.
  tilesHistory_.push_back(getCurrentTilesInfo());

  int timeStartIdx = tilesHistory_.size() < 50 ? 0 : tilesHistory_.size() - 50;
  long totalTimeMS = 0;
  uint64_t totalNumOfChunks = 0;
  for (timeStartIdx; timeStartIdx < tilesHistory_.size(); timeStartIdx++) {
    totalNumOfChunks += tilesHistory_[timeStartIdx].first;
    totalTimeMS += tilesHistory_[timeStartIdx].second;
  }
  // Bytes / MS
  return totalTimeMS == 0 ? 0 : totalNumOfChunks * 1e3 / totalTimeMS;
}