/*
 * BandwidthPredictor.h
 *
 *  Created on: Jun 2, 2021
 *      Author: eghabash
 */

#ifndef BANDWIDTHPREDICTOR_H_
#define BANDWIDTHPREDICTOR_H_

#include <map>
#include <mutex>
#include <vector>

class BandwidthPredictor {

  // TODO keep track of the time instead of relying on abr.
  // whenever we add new chunk check the time.
  // tiles within the same second will have their own sum/avg.

  // keep track of the bandwidth for the latest download tiles.
  int numOfChunks_;
  uint32_t tileSizesSum_;
  int totalDownloadTimeInMS_;
  std::vector<std::pair<uint32_t, int>> tilesHistory_;
  std::pair<uint32_t, int> getCurrentTilesInfo();
  std::mutex tileInfoMutex_;

public:
  BandwidthPredictor();
  void addTileInfo(uint32_t tileSize, int downloadTimeInMS);
  float getMpcBandwidthPrediction();
};

#endif /* BANDWIDTHPREDICTOR_H_ */
