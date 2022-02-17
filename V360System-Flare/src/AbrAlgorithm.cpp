/*
 * AbrAlgorithm.cpp
 *
 *  Created on: Jun 6, 2021
 *      Author: eghabash
 */

#include "AbrAlgorithm.h"

#include <unistd.h>

#include <chrono>
#include <thread>

#include "Util.h"
#include "folly/String.h"
#include "glog/logging.h"

#define ABR_FREQ 100

AbrAlgorithm::AbrAlgorithm(std::string tileChunkSizesTracePath) {
  std::ifstream infile(tileChunkSizesTracePath);
  std::string line;
  uint8_t quality = -1;
  while (std::getline(infile, line)) {
    auto pos = line.find(":");
    std::vector<int> qualityTileId;
    std::vector<uint64_t> tileChunkSizes;
    try {
      folly::split("_", line.substr(0, pos), qualityTileId);
      folly::split(",", line.substr(pos + 1), tileChunkSizes);
      if (tileChunkSizePerQuality_.find(qualityTileId[0]) ==
          tileChunkSizePerQuality_.end()) {
        std::map<uint16_t, std::vector<uint64_t>> tileChunksSizesMap;
        tileChunksSizesMap.insert(
            std::make_pair(qualityTileId[1], tileChunkSizes));
        tileChunkSizePerQuality_.insert(
            std::make_pair(qualityTileId[0], tileChunksSizesMap));
      } else {
        tileChunkSizePerQuality_.find(qualityTileId[0])
            ->second.insert(std::make_pair(qualityTileId[1], tileChunkSizes));
      }
    } catch (std::invalid_argument &e) {
      LOG(ERROR) << "AbrAlgorithm::AbrAlgorithm(): cannot read line :" << line;
    }
  }
  numberOfQualities_ = tileChunkSizePerQuality_.size();
}

void AbrAlgorithm::runAbr(AbrAlgorithm *abrAlgorithm,
                          TilePredictor *tilePredictor,
                          BandwidthPredictor *bandwidthPredictor,
                          ClientNetworkLayer *clientNetworkLayer,
                          VideoPlayer *videoPlayer) {
  // every 100ms, update tile list.
  long stime = Util::getTime();
  float videoTime = 0;

  uint8_t numOfQualities = abrAlgorithm->getNumberOfQualities();
  uint8_t numOfClasses;
  auto &tileChunkSizePerQuality = abrAlgorithm->getTileChunkSizePerQuality();

  // frame has multiple classes, each class has set of tiles, tiles can be of
  // different qualities. frameId --> classes --> <tiles_q0, tiles_q1>, where
  // tiles_q0: is the sum of all tiles in lowest qaulity.
  std::map<int, std::map<uint8_t, std::vector<uint64_t>>>
      frameIdSetQualitySizeSum;
  std::vector<std::string> tilesRequest;
  // This set will contain all tiles in prev sets (to contain duplicates)
  // tilechunk_tileIdx
  std::set<std::string> tilesInPrevSets;
  while (true) {
    tilesInPrevSets.clear();
    // get the predicted tiles every ABR_FREQ(100ms).
    // we will have mutliple sets (e.g. viewport tiles, viewport edge tiles ,
    // further tiles, rest of tiles)
    auto tileClassesOfFutureFrames = tilePredictor->getPredictedTilesLR();
    if (tileClassesOfFutureFrames.size() == 0) {
      break;
    }
    numOfClasses = 0;
    // all frameId must be >= frameIdToRender, to ensure we don't request data
    // for old frames.
    auto frameIdToRender = videoPlayer->getFrameToRenderId();

    // per frame Id, per class, find the sum sizes of all tiles per different
    // qualities.
    for (auto const &tileClassesSingleFrame :
         tileClassesOfFutureFrames) { // per chunkId
      auto frameId = tileClassesSingleFrame.first;
      if (frameId < frameIdToRender) {
        continue;
      }
      auto chunkId = ((frameId - 1) / 25) + 1;

      if (frameIdSetQualitySizeSum.find(frameId) ==
          frameIdSetQualitySizeSum.end()) {
        std::map<uint8_t, std::vector<uint64_t>> setQualitySizeSum;
        frameIdSetQualitySizeSum.insert(
            std::make_pair(frameId, setQualitySizeSum));
      }
      bool frameHasTiles = false;

      auto &classQualitySizeSum =
          frameIdSetQualitySizeSum.find(frameId)->second;
      for (auto const &SetOftilesInClass :
           tileClassesSingleFrame.second) { // per class of tiles

        auto classRank = SetOftilesInClass.first;
        numOfClasses = numOfClasses < classRank ? classRank : numOfClasses;
        std::string tiles =
            std::to_string(frameId) + ":" + std::to_string(classRank) + ":";
        bool classHasTiles = false;
        // first tile in set.
        // We have viewport set, and multiple out of sight sets.
        if (classQualitySizeSum.find(classRank) == classQualitySizeSum.end()) {
          std::vector<uint64_t> qualitySizeSumVec(numOfQualities);
          classQualitySizeSum.insert(
              std::make_pair(classRank, qualitySizeSumVec));
        }
        std::unordered_set<std::string> tilesInSet;
        auto &qualitySizeSumVec = classQualitySizeSum.find(classRank)->second;
        for (uint8_t qualityIdx = 0; qualityIdx < numOfQualities;
             qualityIdx++) { // per quality

          for (auto const &tile : SetOftilesInClass.second) { // per tile
            // if tile chunk is recevied then do not count it.
            std::string tileKey =
                std::to_string(chunkId) + "_" + std::to_string(tile);
            // if the tile already included in previous higher rank sets, no
            // need to include it in the lower sets
            if (tilesInPrevSets.find(tileKey) != tilesInPrevSets.end()) {
              continue;
            }
            tilesInSet.insert(tileKey);
            if (!clientNetworkLayer->isReceived(chunkId, tile)) {
              if (qualityIdx == 0) {
                tiles += std::to_string(tile) + ",";
                classHasTiles = true;
                frameHasTiles = true;
              }

              qualitySizeSumVec[qualityIdx] +=
                  tileChunkSizePerQuality.find(qualityIdx + 1)
                      ->second.find(tile)
                      ->second[chunkId - 1];
            }
          }
        }
        if (classHasTiles) {
          // if this class has tiles, then add tiles to request
          tiles.pop_back();
          tilesRequest.push_back(tiles);
          for (auto tile : tilesInSet) {
            tilesInPrevSets.insert(tile);
          }

          if (VLOG_IS_ON(1)) {
            VLOG(1) << "FrameId[" << static_cast<int>(frameId) << "] - "
                    << "set[" << static_cast<int>(classRank) << "] : " << tiles
                    << std::endl;
          }
        } else {
          classQualitySizeSum.erase(classRank);
        }
      }
      if (!frameHasTiles) {
        frameIdSetQualitySizeSum.erase(frameId);
      }
    }

    // find the quality that we can get all tiles within each frame before frame
    // deadline (avoid rebuffering at all costs).
    // Constraints:
    // 1- all tiles for frame[i] must arrive before tiles of frame[i+1]
    // 2- all tiles in one class will be of the same quality across frames.
    // 3- quality of high class must be equal or greater than low classes.
    // For instance if you have 2 classes, and 3 qualities, then possible
    // quality assignment would be given that class1 has higher rank than
    // class2, and 3 being the highest quality):
    // class_1  class_2
    //    3       3
    //    3       2
    //    3       1
    //    2       2
    //    2       1
    //    1       1
    float predictedBw =
        (bandwidthPredictor->getMpcBandwidthPrediction() * 1e6) /
        8.0; // Bytes Per Second

    auto qualitiesAssignments = abrAlgorithm->getPossibleQualityAssignment(
        numOfQualities, numOfClasses + 1);
    // current video time is the time of the last played frame + time
    // passed since last frame was rendered.
    int qIdx = 2;
    bool qualityFound;
    float currentVideoTime =
        (((frameIdToRender - 1) * 40.0) + Util::getTimePassedSinceLastFrame()) /
        1e3; // current video time.
    //LOG(INFO) << "Bandwidth: " << (predictedBw * 8 / 1e6)
      //        << " , Next frame: " << frameIdToRender;

    for (int quality = numOfQualities; quality > 0; quality--) {
      // for all possible solutions
      for (auto const &solution : qualitiesAssignments.find(quality)->second) {
        // try the solution: calculate the timing for all sets in all frames
        float timeCascade = currentVideoTime;
        qualityFound = true;
        // go through all classes in all frames one by one based on render
        // deadline.
        //LOG(INFO) << "Solution = " << solution;
        for (auto const &tileClassesSingleFrame : frameIdSetQualitySizeSum) {
          if (tileClassesSingleFrame.first < frameIdToRender) {
            continue;
          }
          // size sum of set of tiles in all classes for this frame
          uint64_t totalFrameTileSizes = 0;
          for (auto const &tileClass : tileClassesSingleFrame.second) {
            int qualityIdx = int(solution[tileClass.first * 2]) - 49;
            totalFrameTileSizes += tileClass.second[qualityIdx];
          }
          // can we get all frame tiles before render deadline?
          auto downloadTime = totalFrameTileSizes / predictedBw;
          auto frameTilesDeadline =
              ((tileClassesSingleFrame.first - 1.0) * 40.0) / 1e3;

          /*LOG(INFO) << "Frame : " << tileClassesSingleFrame.first
                    << " , size= " << totalFrameTileSizes;
          LOG(INFO) << "currentTime : " << currentVideoTime
                    << ", frame deadline : " << frameTilesDeadline
                    << " , download time : " << downloadTime;*/
          if (downloadTime + timeCascade < frameTilesDeadline) {
            timeCascade += downloadTime;
          } else {
            qualityFound = false;
            qIdx--;
            break;
          }
        }
        if (qualityFound) {
          break;
        }
      }
      if (qualityFound) {
        break;
      }
    }
    // std::cout << qIdx << std::endl;

    qIdx = qIdx == -1 ? 0 : qIdx;
    std::string req = "Tiles\n";
    for (auto const &tileSet : tilesRequest) {
      req += tileSet + "\n";
    }
    req += "Quality\n" + std::to_string(qIdx);
    // std::cout << req << std::endl;
    clientNetworkLayer->setRequest(req);

    tilesRequest.clear();
    frameIdSetQualitySizeSum.clear();
    Util::sleep(stime, ABR_FREQ);
    videoTime += (Util::getTime() - stime);
    stime += 100;
  }
}

uint8_t AbrAlgorithm::getNumberOfQualities() { return numberOfQualities_; }

std::map<uint8_t, std::map<uint16_t, std::vector<uint64_t>>> &
AbrAlgorithm::getTileChunkSizePerQuality() {
  return tileChunkSizePerQuality_;
}

std::map<int, std::vector<std::string>>
AbrAlgorithm::getPossibleQualityAssignment(int quality, int tileClass) {
  std::map<int, std::vector<std::string>> returnMap;
  if (tileClass == 1) {
    for (int q = quality; q > 0; q--) {
      std::vector<std::string> qualityVec{std::to_string(q)};
      returnMap.insert(std::make_pair(q, qualityVec));
    }
    return returnMap;
  }

  auto result = getPossibleQualityAssignment(quality, tileClass - 1);
  for (int q1 = quality; q1 > 0; q1--) {
    std::vector<std::string> solution;
    for (int q2 = q1; q2 > 0; q2--) {
      for (auto sol : result.find(q2)->second) {
        solution.push_back(std::to_string(q1) + "," + sol);
      }
    }
    returnMap.insert(std::make_pair(q1, solution));
  }

  return returnMap;
}
