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

AbrAlgorithm::AbrAlgorithm() {
  // std::string tracePath =
  //    "/home/ehab/Desktop/traces/quality_tile_sizes.txt";
  std::string tracePath =
      "/Users/eghabash/Desktop/360 Video/Project-V360"
      "/split/quality_tile_sizes.txt";
  std::ifstream infile(tracePath);
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
  auto &tileChunkSizePerQuality = abrAlgorithm->getTileChunkSizePerQuality();
  // chunkId, set, quality (index), sum size of all set with <quality>.
  std::map<int, std::map<uint8_t, std::vector<uint64_t>>>
      chunkIdSetQualitySizeSum;
  std::vector<std::string> tilesRequest;
  while (true) {
    // get the predicted tiles every ABR_FREQ(100ms).
    // we will have mutliple sets (e.g. viewport tiles, viewport edge tiles ,
    // further tiles, rest of tiles)
    auto tilesPerFrame = tilePredictor->getPredictedTiles();
    if (tilesPerFrame.size() == 0) {
      break;
    }
    // per chunk Id, per set, find the sum sizes of all tiles per different
    // qualities.
    for (auto const &frameTilesPair : tilesPerFrame) {  // per chunkId
      int tileChunk = ((frameTilesPair.first - 1) / 25) + 1;
      // first tile with chunkId == tileChunk, then init map.
      if (chunkIdSetQualitySizeSum.find(tileChunk) ==
          chunkIdSetQualitySizeSum.end()) {
        std::map<uint8_t, std::vector<uint64_t>> setQualitySizeSum;
        chunkIdSetQualitySizeSum.insert(
            std::make_pair(tileChunk, setQualitySizeSum));
      }

      auto &setQualitySizeSum =
          chunkIdSetQualitySizeSum.find(tileChunk)->second;
      for (auto const &tileSet : frameTilesPair.second) {  // per tile set
        std::string tiles = std::to_string(tileChunk) + ":" +
                            std::to_string(tileSet.first) + ":";
        bool setHasTiles = false;
        // first tile in set.
        // We have viewport set, and multiple out of sight sets.
        if (setQualitySizeSum.find(tileSet.first) == setQualitySizeSum.end()) {
          std::vector<uint64_t> qualitySizeSumVec(numOfQualities);
          setQualitySizeSum.insert(
              std::make_pair(tileSet.first, qualitySizeSumVec));
        }

        auto &qualitySizeSumVec = setQualitySizeSum.find(tileSet.first)->second;
        for (uint8_t qualityIdx = 0; qualityIdx < numOfQualities;
             qualityIdx++) {  // per quality

          for (auto const &tile : tileSet.second) {  // per tile
            // if tile chunk is recevied then do not count it.
            if (!clientNetworkLayer->isReceived(tileChunk, tile)) {
              if (qualityIdx == 0) {
                tiles += std::to_string(tile) + ",";
                setHasTiles = true;
              }

              qualitySizeSumVec[qualityIdx] +=
                  tileChunkSizePerQuality.find(qualityIdx + 1)
                      ->second.find(tile)
                      ->second[tileChunk - 1];
            }
          }
        }
        // only add if this set has tiles needed.
        if (setHasTiles) {
          tiles.pop_back();
          tilesRequest.push_back(tiles);
        }
        if (VLOG_IS_ON(1)) {
          VLOG(1) << "ChunkId[" << static_cast<int>(tileChunk) << "] - "
                  << "set[" << static_cast<int>(tileSet.first)
                  << "] : " << tiles << std::endl;
        }
      }
    }

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
    // TODO: This need to be generalized.
    // chunk id, size <LL, HL, HH>
    std::map<int, std::vector<uint64_t>> allCombinations;
    for (auto const &chunkSet : chunkIdSetQualitySizeSum) {
      std::vector<uint64_t> qualityComb = {0, 0, 0};
      for (auto const &setQuality : chunkSet.second) {
        if (setQuality.first == 0) {
          qualityComb[0] += setQuality.second[0];
          qualityComb[1] += setQuality.second[1];
          qualityComb[2] += setQuality.second[1];
        } else {
          qualityComb[0] += setQuality.second[0];
          qualityComb[1] += setQuality.second[0];
          qualityComb[2] += setQuality.second[1];
        }
      }
      allCombinations.insert(std::make_pair(chunkSet.first, qualityComb));
    }

    float predictedBw = 1000.0 * 1e6 / 8.0;  // 5mpbs to bytes/second.
    // bandwidthPredictor->getMpcBandwidthPrediction();

    int qIdx = 2;
    // assuming that bandwidth is 5mbps.
    for (; qIdx >= 0; qIdx--) {
      float tcascade = 0;
      for (auto const &chunkComb : allCombinations) {
        // time in sec to get the set of quality[qIdx]
        auto downloadTime = chunkComb.second[qIdx] / predictedBw;
        // time by which this set is needed if not to face rebuffering.
        auto chunkDeadline = ((chunkComb.first) - (videoTime / 1e3));
        tcascade = (chunkDeadline - downloadTime) + tcascade;
        VLOG(1) << chunkComb.first << " : " << videoTime / 1e3 << " : "
                << ((chunkComb.first) - (videoTime / 1e3))
                << " == " << chunkComb.second[qIdx] << " = " << downloadTime
                << "/" << tcascade;
        if (tcascade < 0) {
          break;
        }
      }
      if (tcascade > 0) {
        break;
      }
    }
    qIdx = qIdx == -1 ? 0 : qIdx;
    std::string req = "Tiles\n";
    for (auto const &tileSet : tilesRequest) {
      req += tileSet + "\n";
    }
    req += "Quality\n" + std::to_string(qIdx);
    clientNetworkLayer->setRequest(req);

    tilesRequest.clear();
    chunkIdSetQualitySizeSum.clear();
    Util::sleep(stime, ABR_FREQ);
    videoTime += (Util::getTime() - stime);
    stime += 100;
  }
}

uint8_t AbrAlgorithm::getNumberOfQualities() { return numberOfQualities_; }

std::map<uint8_t, std::map<uint16_t, std::vector<uint64_t>>>
    &AbrAlgorithm::getTileChunkSizePerQuality() {
  return tileChunkSizePerQuality_;
}
