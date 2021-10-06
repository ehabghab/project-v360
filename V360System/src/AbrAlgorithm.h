/*
 * AbrAlgorithm.h
 *
 *  Created on: Jun 6, 2021
 *      Author: eghabash
 */

#ifndef ABRALGORITHM_H_
#define ABRALGORITHM_H_

#include "BandwidthPredictor.h"
#include "ClientNetworkLayer.h"
#include "TilePredictor.h"

class AbrAlgorithm {
 public:
  AbrAlgorithm();
  static void runAbr(AbrAlgorithm *abrAlgorithm, TilePredictor *tilePredictor,
                     BandwidthPredictor *bandwidthPredictor,
                     ClientNetworkLayer *clientNetworkLayer);
  uint8_t getNumberOfQualities();
  std::map<uint8_t, std::map<uint16_t, std::vector<uint64_t>>>
      &getTileChunkSizePerQuality();

 private:
  // quality --> tiles --> tile chunk sizes.
  std::map<uint8_t, std::map<uint16_t, std::vector<uint64_t>>>
      tileChunkSizePerQuality_;
  uint8_t numberOfQualities_;

};

#endif /* ABRALGORITHM_H_ */
