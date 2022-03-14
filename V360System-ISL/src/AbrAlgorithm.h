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
  static void flareAbr(AbrAlgorithm *abrAlgorithm, TilePredictor *tilePredictor,
                       BandwidthPredictor *bandwidthPredictor,
                       ClientNetworkLayer *clientNetworkLayer,
                       VideoPlayer *videoPlayer);

  static void utilityAbr(AbrAlgorithm *abrAlgorithm,
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

  std::map<float, std::vector<std::pair<int, uint16_t>>> orderTilesByMaxUtility(
      std::map<std::pair<int, uint16_t>, std::vector<float>> utilityMatrix,
      uint16_t frameIdToRender);

  std::vector<std::pair<int, uint16_t>> getTilesWithMaxOverallUtility(
      std::map<std::pair<int, uint16_t>, std::vector<float>> utilityMatrix,
      std::map<float, std::vector<std::pair<int, uint16_t>>>
          sortedTilesByUtility,
      uint16_t frameIdToRender, float estimatedBw, float base1Time,
      std::map<uint8_t, std::map<uint16_t, std::vector<uint64_t>>>
          tileChunkSizes,
      ClientNetworkLayer *clientNetworkLayer);

  /**
   * @brief This function will take all urgent tiles that user may view in the
   *        future (next two seconds). Then, it will check if the client
   *        received the tile already or not. If not, then add to request.
   *
   * @param frameIdToRender: this the frame the client player will play next.
   * @param clientNetworkLayer: this checks whether tile has been received in
   *        the buffer or not.
   * @param urgetTiles: list of critical tiles to the user for the next 2-sec
   * @return std::pair<std::string, int>, it returns all tiles in one string
   *         along with their total size
   */
  std::pair<std::string, int> buildBackgroundUrgentTilesRequest(
      uint32_t frameIdToRender, ClientNetworkLayer *clientNetworkLayer,
      std::map<float, std::vector<uint16_t>> &urgetTiles);

  std::vector<std::pair<std::string, int>> getBackgroundLessUrgentTilesInfo(
      uint32_t frameIdToRender, ClientNetworkLayer *clientNetworkLayer,
      std::map<float, std::vector<uint16_t>> &urgetTiles);
};

#endif /* ABRALGORITHM_H_ */
