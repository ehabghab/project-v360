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
  float bandwidthSum_;
  int numOfChunks_;
  std::mutex bandwidthMutex_;
  std::vector<std::pair<int, float>> avgBandwidths_;

  std::pair<int, float> getAvgDownloadTime();

public:
  BandwidthPredictor();
  virtual ~BandwidthPredictor();
  void addTileBandwidth(float downloadTime);
  float getMpcBandwidthPrediction();
};

#endif /* BANDWIDTHPREDICTOR_H_ */
