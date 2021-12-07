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
#include "VideoPlayer.h"

class AbrAlgorithm {
public:
  AbrAlgorithm(std::string tileChunkSizesTracePath);
  static void runAbr(AbrAlgorithm *abrAlgorithm, TilePredictor *tilePredictor,
                     BandwidthPredictor *bandwidthPredictor,
                     ClientNetworkLayer *clientNetworkLayer,
                     VideoPlayer *videoPlayer);

  static void runAbrUtilityMatrix(AbrAlgorithm *abrAlgorithm,
                                  TilePredictor *tilePredictor,
                                  BandwidthPredictor *bandwidthPredictor,
                                  ClientNetworkLayer *clientNetworkLayer,
                                  VideoPlayer *videoPlayer);

private:
  // quality --> tiles --> tile chunk sizes.
  std::map<uint8_t, std::map<uint16_t, std::vector<uint64_t>>>
      tileChunkSizePerQuality_;
  uint8_t numberOfQualities_;

  /**
   * this will all return all possible quality assignments per tile class using
   * DP. Input:
   *       - number of chunk qualities (Q)
   *       - number of classes (C)
   * Return:
   * - map<quality, all possible assignments starting with quality>
   * e.g.  for Q=3 and C=3, the map would look like this
   *       {
   *          3: ["3,3,3","3,3,2","3,3,1","3,2,2","3,2,1","3,1,1"],
   *          2: ["2,2,2","2,2,1","2,1,1"],
   *          1: ["1,1,1"]
   *       }
   *        with "3,3,3" being highest quality, and "1,1,1" the lowest.
   * */

  std::map<int, std::vector<std::string>>
  getPossibleQualityAssignment(int quality, int tileClass);

  uint8_t getNumberOfQualities();
  std::map<uint8_t, std::map<uint16_t, std::vector<uint64_t>>> &
  getTileChunkSizePerQuality();

  std::map<float, std::vector<std::string>> orderTilesByMaxUtility(
      std::map<std::string, std::vector<float>> utilityMatrix,
      uint16_t frameIdToRender);

  std::vector<std::string> getTilesWithMaxOverallUtility(
      std::map<std::string, std::vector<float>> utilityMatrix,
      std::map<float, std::vector<std::string>> sortedUtilityMatrix,
      uint16_t frameIdToRender, float estimatedBw,
      std::map<uint8_t, std::map<uint16_t, std::vector<uint64_t>>>
          tileChunkSizes,
      ClientNetworkLayer *clientNetworkLayer);
};

#endif /* ABRALGORITHM_H_ */
