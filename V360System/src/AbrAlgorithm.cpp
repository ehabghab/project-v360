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
                          ClientNetworkLayer *clientNetworkLayer) {
  // every 100ms, update tile list.
  long stime = Util::getTime();
  float videoTime = 0;

  uint8_t numOfQualities = abrAlgorithm->getNumberOfQualities();
  uint8_t numOfClasses;
  auto &tileChunkSizePerQuality = abrAlgorithm->getTileChunkSizePerQuality();
  // frameId, set, quality (index), sum size of all set with <quality>.
  std::map<int, std::map<uint8_t, std::vector<uint64_t>>>
      FrameIdSetQualitySizeSum;
  std::vector<std::string> tilesRequest;
  while (true) {
    // get the predicted tiles every ABR_FREQ(100ms).
    // we will have mutliple sets (e.g. viewport tiles, viewport edge tiles ,
    // further tiles, rest of tiles)
    auto tileClassesOfFutureFrames = tilePredictor->getPredictedTilesLR();
    if (tileClassesOfFutureFrames.size() == 0) {
      break;
    }
    numOfClasses = 0;

    // per frame Id, per class, find the sum sizes of all tiles per different
    // qualities.
    for (auto const &tileClassesSingleFrame :
         tileClassesOfFutureFrames) { // per chunkId
      auto frameId = tileClassesSingleFrame.first;
      auto chunkId = ((frameId - 1) / 25) + 1;

      if (FrameIdSetQualitySizeSum.find(frameId) ==
          FrameIdSetQualitySizeSum.end()) {
        std::map<uint8_t, std::vector<uint64_t>> setQualitySizeSum;
        FrameIdSetQualitySizeSum.insert(
            std::make_pair(frameId, setQualitySizeSum));
      }

      auto &setQualitySizeSum = FrameIdSetQualitySizeSum.find(frameId)->second;
      for (auto const &SetOftilesInClass :
           tileClassesSingleFrame.second) { // per class of tiles
        auto classRank = SetOftilesInClass.first;
        numOfClasses = numOfClasses < classRank ? classRank : numOfClasses;
        std::string tiles =
            std::to_string(frameId) + ":" + std::to_string(classRank) + ":";
        bool setHasTiles = false;
        // first tile in set.
        // We have viewport set, and multiple out of sight sets.
        if (setQualitySizeSum.find(classRank) == setQualitySizeSum.end()) {
          std::vector<uint64_t> qualitySizeSumVec(numOfQualities);
          setQualitySizeSum.insert(
              std::make_pair(classRank, qualitySizeSumVec));
        }

        auto &qualitySizeSumVec = setQualitySizeSum.find(classRank)->second;
        for (uint8_t qualityIdx = 0; qualityIdx < numOfQualities;
             qualityIdx++) { // per quality

          for (auto const &tile : SetOftilesInClass.second) { // per tile
            // if tile chunk is recevied then do not count it.
            if (!clientNetworkLayer->isReceived(frameId, tile)) {
              if (qualityIdx == 0) {
                tiles += std::to_string(tile) + ",";
                setHasTiles = true;
              }

              qualitySizeSumVec[qualityIdx] +=
                  tileChunkSizePerQuality.find(qualityIdx + 1)
                      ->second.find(tile)
                      ->second[chunkId - 1];
            }
          }
        }
        // only add if this set has tiles needed.
        if (setHasTiles) {
          tiles.pop_back();
          tilesRequest.push_back(tiles);
        }
        if (VLOG_IS_ON(1)) {
          VLOG(1) << "FrameId[" << static_cast<int>(frameId) << "] - "
                  << "set[" << static_cast<int>(classRank) << "] : " << tiles
                  << std::endl;
        }
      }
    }

    // per quality HH --> HL --> LL
    // per tileClasses
    // total download time is viable?

    // first make sure we can delive viewport set on time, the other sets.
    // do all.
    // multiple sets we could assign different quality to each but in decsing
    // order.
    // H H 2
    // H L 1
    // L L 0
    // chunk id.
    // set1 set2 set3
    // qulity1 quality2

    float predictedBw =
        (bandwidthPredictor->getMpcBandwidthPrediction() * 1e6) /
        8.0; // Bytes Per Second

    auto qualitiesAssignments = abrAlgorithm->getPossibleQualityAssignment(
        numOfQualities, numOfClasses + 1);

    float currentVideoTime = ((tilePredictor->getFrameId() - 1) * 40.0) / 1e3;
    int qIdx = 2;
    bool qualityFound;
    // current video time.
    for (int quality = numOfQualities; quality > 0; quality--) {
      // for all possible solutions
      for (auto const &solution : qualitiesAssignments.find(quality)->second) {
        // try the solution: calculate the timing for all sets in all frames
        float timeCascade = currentVideoTime;
        qualityFound = true;
        // go through all classes in all frames one by one based on render
        // deadline.
        for (auto const &tileClassesSingleFrame : FrameIdSetQualitySizeSum) {
          // size sum of set of tiles in all classes for this frame
          uint64_t totalFrameTileSizes = 0;
          for (auto const &tileClass : tileClassesSingleFrame.second) {
            int qualityIdx = int(solution[tileClass.first * 2]) - 49;
            totalFrameTileSizes += tileClass.second[qualityIdx];
          }
          // can we get all frame tiles before render deadline?
          auto downloadTime = totalFrameTileSizes / predictedBw;
          auto frameTilesDeadline = (tileClassesSingleFrame.first - 1) * 40;
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
    std::cout << qIdx << std::endl;

    /*

    // chunkId, set, quality (index), sum size of all set with <quality>.
    // chunk id, size <LL, HL, HH>
    std::map<int, std::vector<uint64_t>> allCombinations;
    for (auto const &chunkSet : FrameIdSetQualitySizeSum) {
      std::vector<uint64_t> qualityComb = {0, 0, 0};
      for (auto const &setQuality : chunkSet.second) {
        if (setQuality.first == 0) {  // viewport set
          qualityComb[0] += setQuality.second[0];
          qualityComb[1] += setQuality.second[1];
          qualityComb[2] += setQuality.second[1];
        } else {  // edge set
          qualityComb[0] += setQuality.second[0];
          qualityComb[1] += setQuality.second[0];
          qualityComb[2] += setQuality.second[1];
        }
      }
      allCombinations.insert(std::make_pair(chunkSet.first, qualityComb));
    }

    std::cout << "BW:" << std::to_string(predictedBw * 8 / 1e6) << std::endl;
    std::cout << videoTime << std::endl;
    for (auto const &chunkComb : allCombinations) {
      std::cout << chunkComb.first << ":[";
      for (auto const &q : chunkComb.second) {
        std::cout << std::to_string(q) << ",";
      }
      std::cout << "]\n";
    }

    int qIdx = 2;
    if (predictedBw == 0 || std::isnan(predictedBw)) {
      qIdx = 0;
    } else {
      // try all different quality options (i.e. H_H:2, H_L:1, L_L:0)
      bool qualityFound;
      for (; qIdx >= 0; qIdx--) {
        float timeCascade = (videoTime / 1e3);
        qualityFound = true;
        // chunkComb.first = chunkId
        // chunkComb.second = {0: size(L_L),1:size(H_L), 2:size(H_H)}
        for (auto const &chunkComb : allCombinations) {
          // time in sec to get the set of quality[qIdx]
          auto downloadTime = chunkComb.second[qIdx] / predictedBw;
          if (downloadTime + timeCascade < chunkComb.first) {
            timeCascade += downloadTime;
          } else {
            qualityFound = false;
            break;
          }
        }
        if (qualityFound) {
          // all sets are recevied by their deadline, so qIdx is the best
          // quality.
          break;
        }
      }
    }
    */
    qIdx = qIdx == -1 ? 0 : qIdx;
    std::string req = "Tiles\n";
    for (auto const &tileSet : tilesRequest) {
      req += tileSet + "\n";
    }
    req += "Quality\n" + std::to_string(qIdx);
    std::cout << req << std::endl;
    clientNetworkLayer->setRequest(req);

    tilesRequest.clear();
    FrameIdSetQualitySizeSum.clear();
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
