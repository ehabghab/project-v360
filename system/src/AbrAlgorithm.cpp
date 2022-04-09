/*
 * AbrAlgorithm.cpp
 *
 *  Created on: Jun 6, 2021
 *      Author: eghabash
 */

#include "AbrAlgorithm.h"

#include <unistd.h>

#include <chrono>
#include <limits>
#include <thread>

#include "Util.h"
#include "folly/String.h"
#include "glog/logging.h"

#define ABR_FREQ 100

AbrAlgorithm::AbrAlgorithm(std::string tileChunkSizesPath,
                           std::string tileChunksQaulityPath,
                           std::string backgroundDisplacementPath) {
  std::ifstream infile1(tileChunkSizesPath);
  std::string line;
  uint8_t quality = -1;
  while (std::getline(infile1, line)) {
    line.pop_back();
    auto pos = line.find(":");
    std::vector<int> TileIdQualityPair;
    std::vector<uint64_t> tileChunkSizes;
    try {
      folly::split("-", line.substr(0, pos), TileIdQualityPair);
      folly::split(",", line.substr(pos + 2), tileChunkSizes);
      uint8_t qualityIdx = QUALITYMAP_.find(TileIdQualityPair[1])->second;
      if (tileChunkSizePerQuality_.find(qualityIdx) ==
          tileChunkSizePerQuality_.end()) {
        std::map<uint16_t, std::vector<uint64_t>> tileChunksSizesMap;
        tileChunksSizesMap.insert({TileIdQualityPair[0], tileChunkSizes});
        tileChunkSizePerQuality_.insert({qualityIdx, tileChunksSizesMap});
      } else {
        tileChunkSizePerQuality_[qualityIdx].insert(
            {TileIdQualityPair[0], tileChunkSizes});
      }
    } catch (std::invalid_argument &e) {
      LOG(ERROR) << "AbrAlgorithm::AbrAlgorithm(): cannot read line :" << line;
    }
  }

  std::ifstream infile2(tileChunksQaulityPath);
  while (std::getline(infile2, line)) {
    line.pop_back();
    auto pos = line.find(":");
    std::vector<int> TileIdQualityPair;
    std::vector<float> tileChunkQuality;
    try {
      folly::split("-", line.substr(0, pos), TileIdQualityPair);
      folly::split(",", line.substr(pos + 2), tileChunkQuality);
      uint8_t qualityIdx = QUALITYMAP_.find(TileIdQualityPair[1])->second;
      if (TileIdQualityPair[1] == 42) {
        continue;
      }
      if (tileChunkPSNRPerQuality_.find(qualityIdx) ==
          tileChunkPSNRPerQuality_.end()) {
        std::map<uint16_t, std::vector<float>> tileChunksQualityMap;
        tileChunksQualityMap.insert({TileIdQualityPair[0], tileChunkQuality});
        tileChunkPSNRPerQuality_.insert({qualityIdx, tileChunksQualityMap});
      } else {
        tileChunkPSNRPerQuality_[qualityIdx].insert(
            {TileIdQualityPair[0], tileChunkQuality});
      }
    } catch (std::invalid_argument &e) {
      LOG(ERROR) << "AbrAlgorithm::AbrAlgorithm(): cannot read line :" << line;
    }
  }

  numberOfQualities_ = tileChunkPSNRPerQuality_.size();

  std::ifstream infile3(backgroundDisplacementPath);
  while (std::getline(infile3, line)) {
    std::vector<float> displacements;
    folly::split(",", line, displacements);
    backgroundDisplacement_.push_back({{displacements[0], displacements[1]},
                                       {displacements[2], displacements[3]}});
  }
}

void AbrAlgorithm::getTileSetSizePerQuality(
    std::map<int, std::map<uint8_t, std::vector<uint64_t>>>
        &frameIdSetQualitySizeSumToReturn,
    std::map<uint8_t, std::vector<std::pair<int, uint16_t>>>
        &tilesRequestToReturn,
    TilePredictor *tilePredictor, ClientNetworkLayer *clientNetworkLayer,
    uint32_t frameIdToRender, uint8_t numOfQualities) {
  std::set<std::string> tilesInPrevSets;

  // get all tiles need per frame in each class.
  // frame[i] needs M tiles for Class C1, and N tiles for Class C2
  // note that M ∩ N = Φ, tiles in class M cannot be in N (not duplicate tiles)
  auto tileClassesOfFutureFrames = tilePredictor->getPredictedTilesFlareLR();
  if (tileClassesOfFutureFrames.size() == 0) {
    return;
  }
  uint8_t numOfClasses = 0;

  for (auto const &tileClassesSingleFrame :
       tileClassesOfFutureFrames) { // A- per frame
    auto frameId = tileClassesSingleFrame.first;
    if (frameId < frameIdToRender) {
      continue;
    }
    auto chunkId = ((frameId - 1) / 25);

    if (frameIdSetQualitySizeSumToReturn.find(frameId) ==
        frameIdSetQualitySizeSumToReturn.end()) {
      std::map<uint8_t, std::vector<uint64_t>> setQualitySizeSum;
      frameIdSetQualitySizeSumToReturn.insert(
          std::make_pair(frameId, setQualitySizeSum));
    }
    bool frameHasTiles = false;

    auto &classQualitySizeSum =
        frameIdSetQualitySizeSumToReturn.find(frameId)->second;
    for (auto const &SetOftilesInClass :
         tileClassesSingleFrame.second) { // B- tiles per class

      auto classRank = SetOftilesInClass.first;

      //============================================
      // This line to determine how many classes to go over next.
      numOfClasses = numOfClasses < classRank ? classRank : numOfClasses;
      //============================================

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
           qualityIdx++) { // C- per quality

        for (auto const &tile : SetOftilesInClass.second) { // D- per tile
          // if tile chunk is recevied then do not count it.
          std::string tileKey =
              std::to_string(chunkId) + "_" + std::to_string(tile);
          // if the tile already included in earlier frame of higher rank
          // class, then skip (no duplicates)
          if (tilesInPrevSets.find(tileKey) != tilesInPrevSets.end()) {
            continue;
          }
          tilesInSet.insert(tileKey);
          if (clientNetworkLayer->isReceived(chunkId + 1, tile) == -1) {
            if (qualityIdx == 0) {
              if (tilesRequestToReturn.find(classRank) ==
                  tilesRequestToReturn.end()) {
                tilesRequestToReturn.insert({classRank, {}});
              }
              tilesRequestToReturn.find(classRank)->second.push_back(
                  {chunkId, tile});
              tiles += std::to_string(tile) + ",";
              classHasTiles = true;
              frameHasTiles = true;
            }

            qualitySizeSumVec[qualityIdx] +=
                tileChunkSizePerQuality_.find(qualityIdx + 1)
                    ->second.find(tile)
                    ->second[chunkId];
          }
        }
      }
      if (classHasTiles) {
        // if this class has tiles, then add tiles to request
        tiles.pop_back();
        // tilesRequestToReturn.push_back(tiles);
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
      frameIdSetQualitySizeSumToReturn.erase(frameId);
    }
  }
}

int AbrAlgorithm::getQualityIdx(
    std::map<int, std::map<uint8_t, std::vector<uint64_t>>>
        &frameIdSetQualitySizeSum,
    std::map<int, std::vector<std::string>> qualitiesAssignments,
    uint32_t frameIdToRender, uint8_t numOfQualities, float predictedBw,
    float baseTime) {
  // find the quality that we can get all tiles within each frame before
  // frame deadline (avoid rebuffering at all costs).

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

  // current video time is the time of the last played frame + time
  // passed since last frame was rendered.
  int qIdx = numOfQualities;
  bool qualityFound;
  float currentVideoTime =
      (((frameIdToRender - 1) * 40.0) + Util::getTimePassedSinceLastFrame()) /
      1e3; // current video time.

  currentVideoTime += baseTime;

  for (int quality = numOfQualities; quality > 0; quality--) {
    // for all possible solutions
    for (auto const &solution : qualitiesAssignments.find(quality)->second) {
      // try the solution: calculate the timing for all sets in all frames
      float timeCascade = currentVideoTime;
      qualityFound = true;
      // go through all classes in all frames one by one based on render
      // deadline.
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
  qIdx = qIdx == -1 ? 0 : qIdx;
  return qIdx;
}

// ToDo fix how flare send tiles, it now needs to be chunkidx_tileidx_quality
// try and be consistent with how utility does it.
void AbrAlgorithm::flareAbr(AbrAlgorithm *abrAlgorithm,
                            TilePredictor *tilePredictor,
                            BandwidthPredictor *bandwidthPredictor,
                            ClientNetworkLayer *clientNetworkLayer,
                            VideoPlayer *videoPlayer) {
  // every 100ms, update tile list.
  long stime = Util::getTime();
  float videoTime = 0;

  uint8_t numOfQualities = abrAlgorithm->getNumberOfQualities();
  uint8_t numOfClasses;
  // This set will contain all tiles in prev sets (to contain duplicates)
  // tilechunk_tileIdx
  std::vector<std::pair<float, float>> predictedCorr;

  std::map<int, std::map<uint8_t, std::vector<uint64_t>>>
      frameIdSetQualitySizeSum;
  std::map<uint8_t, std::vector<std::pair<int, uint16_t>>> tilesRequest;
  while (true) {
    // get the predicted tiles every ABR_FREQ(100ms).
    // we will have mutliple sets (e.g. viewport tiles, viewport edge tiles ,
    // further tiles, rest of tiles)

    // all frameId must be >= frameIdToRender, to ensure we don't request data
    // for old frames.
    auto frameIdToRender = videoPlayer->getFrameToRenderId();
    tilePredictor->getPredictedCorr(predictedCorr);
    abrAlgorithm->getTileSetSizePerQuality(
        frameIdSetQualitySizeSum, tilesRequest, tilePredictor,
        clientNetworkLayer, frameIdToRender, numOfQualities);

    float predictedBw =
        (bandwidthPredictor->getMpcBandwidthPrediction()); // Bytes Per Second

    // generate a list of all required background tiles.
    std::map<float, std::vector<uint16_t>> urgentTiles;
    tilePredictor->getUrgetTilesList(urgentTiles, predictedCorr);
    auto urgentTileRequestAndSize =
        abrAlgorithm->buildBackgroundUrgentTilesRequest(
            frameIdToRender, clientNetworkLayer, urgentTiles);

    auto lessUrgentBGTilesInfo = abrAlgorithm->getBackgroundLessUrgentTilesInfo(
        frameIdToRender, clientNetworkLayer, urgentTiles);

    float baseTime =
        predictedBw == 0 ? 0 : (urgentTileRequestAndSize.second * 1e3) /
                                   predictedBw; // in MS

    auto qualityAssignments = abrAlgorithm->getPossibleQualityAssignment(
        numOfQualities, numOfClasses + 1);
    auto qIdx = abrAlgorithm->getQualityIdx(
        frameIdSetQualitySizeSum, qualityAssignments, frameIdToRender,
        numOfQualities, predictedBw, baseTime);

    std::string req = "Tiles\n" + urgentTileRequestAndSize.first;
    // class rank --> tiles <chunkId, tileId>
    for (auto &classTilesPair : tilesRequest) {
      auto &classRank = classTilesPair.first;
      auto &tilesInClass = classTilesPair.second;
      for (auto &tilePair : tilesInClass) {
        req += std::to_string(tilePair.first) + "_" +
               std::to_string(tilePair.second) + "_2,";
        continue;
        if (qIdx == 0) {
          req += "_1,";
        } else if (qIdx == 1) {
          if (classRank == 0) {
            req += "_2,";
          } else {
            req += "_1,";
          }
        } else {
          req += "_2,";
        }
      }
    }
    req.pop_back();

    req += "\nQuality\n" + std::to_string(0);
    // std::cout << req << std::endl;
    clientNetworkLayer->setRequest(req);
    tilesRequest.clear();
    frameIdSetQualitySizeSum.clear();
    Util::sleep(stime, ABR_FREQ);
    videoTime += (Util::getTime() - stime);
    stime += 100;
  }
}

std::pair<std::string, int> AbrAlgorithm::buildBackgroundUrgentTilesRequest(
    uint32_t frameIdToRender, ClientNetworkLayer *clientNetworkLayer,
    std::map<float, std::vector<uint16_t>> &urgetTiles) {

  // Objective: get all urgent tiles in lowest quality for the next two seconds

  // find the chunk ids correspond to the next two seconds.
  int stChunkId = (((frameIdToRender)-1) / 25);
  int enChunkId = stChunkId; //+ 1;
  if ((frameIdToRender - 1) % 25 != 0) {
    enChunkId++;
  }

  std::string finalRequest = "";

  int size = 0;
  for (auto idx = stChunkId; idx <= enChunkId; idx++) {
    for (auto &tileSet : urgetTiles) {
      if (tileSet.first == 1) {
        continue;
      }
      for (auto &tile : tileSet.second) {
        if (clientNetworkLayer->isReceived(idx + 1, tile) == -1) {
          // the one at the end corresponds to quality; 1 == lowest quality
          finalRequest +=
              std::to_string(idx) + "_" + std::to_string(tile) + "_1,";
          size +=
              tileChunkSizePerQuality_.find(1)->second.find(tile)->second[idx];
        }
      }
    }
  }

  std::pair<std::string, int> reqSize = {finalRequest, size};
  return reqSize;
}

std::vector<std::pair<int, uint16_t>>
AbrAlgorithm::getBackgroundLessUrgentTilesInfo(
    uint32_t frameIdToRender, ClientNetworkLayer *clientNetworkLayer,
    std::map<float, std::vector<uint16_t>> &urgetTiles) {

  // Less urgent chunk corresponds to future-seconds 2-4.
  // So, it starts at sec =  urgent_chunkId + 2
  int stChunkId = (((frameIdToRender)-1) / 25) + 1;
  int enChunkId = stChunkId + 1;
  if ((frameIdToRender - 1) % 25 != 0) {
    stChunkId++;
  }
  // tileId, tile size --> size will be used by tiles scheduler.
  std::vector<std::pair<int, uint16_t>> tilesInfo;

  int size = 0;
  for (auto chunkIdx = stChunkId; chunkIdx <= enChunkId; chunkIdx++) {
    for (auto &tileSet : urgetTiles) {
      if (tileSet.first == 1) {
        continue;
      }
      for (auto &tile : tileSet.second) {
        if (clientNetworkLayer->isReceived(chunkIdx + 1, tile) == -1) {
          std::string tileKey =
              std::to_string(chunkIdx) + "_" + std::to_string(tile);
          tilesInfo.push_back({chunkIdx, tile});
        }
      }
    }
  }

  return tilesInfo;
}

void AbrAlgorithm::updateTilesAndgetTotalSize(
    long &totalSize, std::vector<std::pair<int, uint16_t>> &updatedTiles,
    std::map<float, std::vector<uint16_t>> &tilesMap, int chunkId,
    ClientNetworkLayer *clientNetworkLayer) {
  updatedTiles.clear();
  totalSize = 0;
  for (auto &fracTiles : tilesMap) {
    if (fracTiles.first == 1) {
      continue;
    }
    for (auto &tile : fracTiles.second) {
      if (clientNetworkLayer->isReceived(chunkId + 1, tile) > 0) {
        // std::cout << "tile:" << tile << "_" << (chunkId + 1)
        //      << " --> not received!\n";
        continue;
      }
      totalSize += tileChunkSizePerQuality_[1][tile][chunkId];
      updatedTiles.push_back({chunkId, tile});
    }
  }
}

void AbrAlgorithm::updateTilesAndgetTotalSize(
    long &totalSize, std::vector<std::pair<int, uint16_t>> &tilesToUpdate,
    ClientNetworkLayer *clientNetworkLayer) {
  totalSize = 0;
  std::vector<std::pair<int, uint16_t>> updatedTiles;
  for (auto &tileInfo : tilesToUpdate) {
    if (clientNetworkLayer->isReceived(tileInfo.first + 1, tileInfo.second) >
        0) {
      continue;
    }
    totalSize += tileChunkSizePerQuality_[1][tileInfo.second][tileInfo.first];
    updatedTiles.push_back({tileInfo.first, tileInfo.second});
  }
  tilesToUpdate = updatedTiles;
}

std::string AbrAlgorithm::scheduler(
    std::vector<std::vector<std::pair<int, uint16_t>>> &backgroundTiles,
    std::vector<int> chunkIdxs, float bgBw,
    std::vector<std::pair<std::pair<int, uint16_t>, uint8_t>> &fgTiles,
    float fgBw) {
  std::string request;
  float totalBw = bgBw + fgBw;
  float fgMsShare = (fgBw / totalBw) * 100.0;
  float bgMsShare = 100 - fgMsShare;
  int bgTileIdx = 0;
  int bgchunkIdx = chunkIdxs[0];
  float fgMsTarget = fgMsShare;
  float bgMsTarget;
  for (int fgIdx = 0; fgIdx < fgTiles.size(); fgIdx++) {
    // <tileId, chunkId>
    auto &fgTileInfo = fgTiles[fgIdx].first;
    auto tileQuality = fgTiles[fgIdx].second;
    float dtime = (tileChunkSizePerQuality_[tileQuality][fgTileInfo.second]
                                           [fgTileInfo.first] *
                   1e3) /
                  totalBw;

    std::string fgTile = std::to_string(fgTileInfo.first) + "_" +
                         std::to_string(fgTileInfo.second) + "_" +
                         std::to_string(tileQuality) + ",";
    if (fgMsTarget - dtime >= 0) { // fg tile fits in the FG slot
      request += fgTile;
      fgMsTarget -= dtime;
    } else { // fg tile spills to bg slot

      // by how much it overspilled.
      float fgExtraMs = std::abs(fgMsTarget - dtime) / fgMsShare;
      // reconfigure BG share accordingly.
      bgMsTarget = (1 + fgExtraMs) * bgMsShare;
      // fill the BG tiles
      for (; bgchunkIdx <= chunkIdxs[chunkIdxs.size() - 1]; bgchunkIdx++) {
        for (; bgTileIdx < backgroundTiles[bgchunkIdx].size(); bgTileIdx++) {
          auto &bgTileInfo = backgroundTiles[bgchunkIdx][bgTileIdx];
          float dtime = (tileChunkSizePerQuality_[1][bgTileInfo.second]
                                                 [bgTileInfo.first] *
                         1e3) /
                        totalBw;
          request += std::to_string(bgTileInfo.first) + "_" +
                     std::to_string(bgTileInfo.second) + "_1,";
          bgMsTarget -= dtime;
          if (bgMsTarget < 0) { // bg tile spills to fg slot
            request += fgTile;
            float bgExtraMs = std::abs(bgMsTarget) / bgMsShare;
            fgMsTarget = (1 + bgExtraMs) * fgMsShare;
            break;
          }
        }
        if (bgTileIdx < backgroundTiles[bgchunkIdx].size()) {
          break;
        }
        bgTileIdx = 0;
      }
      if (bgMsTarget > 0) { // all bg tiles are scheduled.
        request += fgTile;
        fgMsTarget = 100;
      }
    }
  }

  return request;
}

void AbrAlgorithm::utilityAbr(AbrAlgorithm *abrAlgorithm,
                              TilePredictor *tilePredictor,
                              BandwidthPredictor *bandwidthPredictor,
                              ClientNetworkLayer *clientNetworkLayer,
                              VideoPlayer *videoPlayer) {
  // every 100ms, update tile list.
  long stime = Util::getTime();
  float videoTime = 0;

  uint8_t numOfQualities = abrAlgorithm->getNumberOfQualities();
  uint8_t numOfClasses;

  // This set will contain all tiles in prev sets (to contain duplicates)
  // tilechunk_tileIdx
  std::vector<std::pair<float, float>> predictedCorr;
  std::vector<std::pair<int, int>> vpResolutions = {{100, 100}, {120, 120}};
  int chunkId;

  const int backgroundHorizonInSec = 3;

  std::vector<std::vector<std::pair<int, uint16_t>>> backgroundTiles(
      backgroundHorizonInSec);
  std::vector<long> backgroundTilesSizes(backgroundHorizonInSec);
  while (true) {

    // retrieve the predicted tiles using linear regression.
    predictedCorr.clear();
    tilePredictor->getPredictedCorr(predictedCorr);
    auto frameIdToRender = videoPlayer->getFrameToRenderId();

    float predictedBw =
        (bandwidthPredictor->getMpcBandwidthPrediction()); // Bytes Per Second
    // get the background tiles for the next 3 seconds.
    // for the current second, since we have the vp groundtruth for the first
    // frame; we only do it once.
    chunkId = (frameIdToRender - 1) / 25;
    if (chunkId == 60) {
      break;
    }
    abrAlgorithm->backgroundDisplacement_[chunkId];
    for (auto idx = chunkId; idx < chunkId + backgroundHorizonInSec; idx++) {
      if (idx >= 60) {
        backgroundTiles[idx - chunkId] = {};
        continue;
      }
      std::map<float, std::vector<uint16_t>> tempBgTiles;
      if (frameIdToRender % 25 == 1 || idx != chunkId) {
        tilePredictor->getBackgroundTiles(
            tempBgTiles, abrAlgorithm->backgroundDisplacement_[idx]);
        abrAlgorithm->updateTilesAndgetTotalSize(
            std::ref(backgroundTilesSizes[idx - chunkId]),
            std::ref(backgroundTiles[idx - chunkId]), tempBgTiles, idx,
            clientNetworkLayer);
      } else {
        abrAlgorithm->updateTilesAndgetTotalSize(
            std::ref(backgroundTilesSizes[idx - chunkId]),
            std::ref(backgroundTiles[idx - chunkId]), clientNetworkLayer);
      }

      // get the size of the background tiles, and remove tiles that have been
      // recieved already.
    }

    // High priority tiles correspond to the [0-2) seconds.
    float downloadTimeBgHPInMS =
        predictedBw == 0
            ? 0
            : ((backgroundTilesSizes[0] + backgroundTilesSizes[1]) * 1e3) /
                  predictedBw;
    // Medium priority tiles correspond to the [2-3) second.
    float downloadTimeBgMPInMS =
        predictedBw == 0 ? 0 : (backgroundTilesSizes[2] * 1e3) / predictedBw;

    std::vector<std::pair<std::pair<int, uint16_t>, uint8_t>> foregroundTiles;
    float bandwidthBgMP = predictedBw;
    float bandwidthFg = 0;
    // std::cout << "time remaining in ms :"
    //          << 1000 - (downloadTimeBgHPInMS + downloadTimeBgMPInMS) << "\n";

    // improve quality of tiles (foreground tiles)
    if (downloadTimeBgHPInMS + downloadTimeBgMPInMS < 1000) {
      // generate the utility matrix for predicted-to-render tiles in the next
      // 25 frames (1sec).
      auto utilityMatrix =
          tilePredictor->buildUtilityMatrix(predictedCorr, vpResolutions, 25);
      // sort tiles by their max utility.
      auto orderedUtilityMatrix =
          abrAlgorithm->orderTilesByMaxUtility(utilityMatrix, frameIdToRender);
      bandwidthBgMP = backgroundTilesSizes[2] /
                      (1 - (downloadTimeBgHPInMS / 1e3)); // Bytes per Second
      bandwidthFg = predictedBw == 0 ? 0 : (predictedBw - bandwidthBgMP);
      // std::cout << (predictedBw * 8 / 1e6) << ":" << (bandwidthBgMP * 8 /
      // 1e6)
      //        << "-" << (bandwidthFg * 8 / 1e6) << "\n";

      /*foregroundTiles = abrAlgorithm->getTilesWithMaxOverallUtility(
          utilityMatrix, orderedUtilityMatrix, frameIdToRender,
          bandwidthFg > 0 ? bandwidthFg : 2.5 * 1e6, downloadTimeBgHPInMS,
          clientNetworkLayer);*/
      foregroundTiles =
          abrAlgorithm->qualityABR(utilityMatrix, frameIdToRender,
                                   bandwidthFg > 0 ? bandwidthFg : 2.5 * 1e6,
                                   downloadTimeBgHPInMS, clientNetworkLayer);
      auto foregroundTilesSize = abrAlgorithm->getTilesSizes(foregroundTiles);
      float downloadTimeFgInMS =
          predictedBw == 0 ? 0 : (foregroundTilesSize * 1e3) / predictedBw;
      // std::cout << foregroundTilesSize << ":" << downloadTimeFgInMS << "\n"
      //        << foregroundTiles.size() << "\n=====\n";

      if (downloadTimeBgHPInMS + downloadTimeBgMPInMS + downloadTimeFgInMS <
          1000) {
        // ToDo
        // extra Tiles
      }
    }

    std::string req = "";
    for (auto bgChunkIdx : {0, 1}) {
      for (auto &tile : backgroundTiles[bgChunkIdx]) {
        req += std::to_string(tile.first) + "_" + std::to_string(tile.second) +
               "_1,";
      }
    }
    std::string reqScheduled;

    if (foregroundTiles.size() > 0) {
      reqScheduled = abrAlgorithm->scheduler(
          backgroundTiles, {2}, bandwidthBgMP, foregroundTiles, bandwidthFg);
      req += reqScheduled;
    } else {
      for (auto &tile : backgroundTiles[2]) {
        req += std::to_string(tile.first) + "_" + std::to_string(tile.second) +
               "_1,";
      }
    }

    /*std::cout << "frame:" << videoPlayer->getFrameToRenderId()
    << std::endl;
    std::cout << "baseTime:" << baseTime << std::endl;
    std::cout << "size:" << urgentTileRequestAndSize.second <<
    std::endl;*/

    if (req.size()) {
      req.pop_back();
    }
    std::string finalReq = "Tiles\n" + req;
    finalReq += "\nQuality\n" + std::to_string(0);
    clientNetworkLayer->setRequest(finalReq);
    Util::sleep(stime, ABR_FREQ);
    videoTime += (Util::getTime() - stime);
    stime += 100;
  }
}

std::map<float, std::vector<std::pair<int, uint16_t>>>
AbrAlgorithm::orderTilesByMaxUtility(
    std::map<std::pair<int, uint16_t>, std::vector<float>> utilityMatrix,
    uint16_t frameIdToRender) {
  // base frame id.
  float frameIdSt = utilityMatrix.find({-1, -1})->second[0];

  std::map<float, std::vector<std::pair<int, uint16_t>>> sortedUtilityMatrix;
  for (auto const tileChunk : utilityMatrix) {
    if (tileChunk.first.first == -1) { // base frame id.
      continue;
    }
    // 50 = number of frames in the future (25) * number of classes (2)
    auto maxUtility = 50.0 - tileChunk.second[24];
    // deduct the utility of the frames that have already passed deadline.

    if (frameIdToRender > frameIdSt && frameIdToRender != 1) {
      maxUtility -= tileChunk.second[frameIdToRender - frameIdSt];
    }
    if (sortedUtilityMatrix.find(maxUtility) == sortedUtilityMatrix.end()) {
      std::vector<std::pair<int, uint16_t>> tileChunks;
      sortedUtilityMatrix.insert(std::make_pair(maxUtility, tileChunks));
    }
    sortedUtilityMatrix.find(maxUtility)->second.push_back(tileChunk.first);
  }

  // debug log, print utility matrix before and after sorting.
  if (VLOG_IS_ON(1)) {
    LOG(INFO) << "=== Utility Matrix [" << frameIdSt << "]===";

    for (auto const tileChunk : utilityMatrix) {
      std::string p = std::to_string(tileChunk.first.first) + "_" +
                      std::to_string(tileChunk.first.second) + ":";
      for (auto const utility : tileChunk.second) {
        p += std::to_string(utility) + ",";
      }
      p.pop_back();
      LOG(INFO) << p;
    }
    LOG(INFO) << "=== Sorted Utility Matrix [" << frameIdSt << "]===";
    for (auto const utilityChunks : sortedUtilityMatrix) {
      std::string p = std::to_string(50 - utilityChunks.first) + ":";
      for (auto const tile : utilityChunks.second) {
        p += std::to_string(tile.first) + "_" + std::to_string(tile.second) +
             ",";
      }
      p.pop_back();
      LOG(INFO) << p;
    }
  }
  return sortedUtilityMatrix;
}

std::vector<std::pair<int, uint16_t>>
AbrAlgorithm::getTilesWithMaxOverallUtility(
    std::map<std::pair<int, uint16_t>, std::vector<float>> utilityMatrix,
    std::map<float, std::vector<std::pair<int, uint16_t>>> sortedTilesByUtility,
    uint16_t frameIdToRender, float estimatedBw, float baseTime,
    ClientNetworkLayer *clientNetworkLayer) {
  /*std::cout << baseTime << std::endl;
  std::cout << "BW: " << estimatedBw * 8 / 1e6 << std::endl;
  std::cout << "Frame Id: " << std::to_string(frameIdToRender) << std::endl;*/
  /*
  case 1: simple 5 tiles, all same utility.
  utilityMatrix = {
      {{0,102}, {2,  4,  6,  8,  10, 12, 14, 16, 18, 20, 22, 24, 26,
                 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50}},
      {{0,103}, {2,  4,  6,  8,  10, 12, 14, 16, 18, 20, 22, 24, 26,
                 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50}},
      {{0,42}, {2,  4,  6,  8,  10, 12, 14, 16, 18, 20, 22, 24, 26,
                28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50}},
      {{0,43}, {2,  4,  6,  8,  10, 12, 14, 16, 18, 20, 22, 24, 26,
                28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50}},
      {{0,44}, {2,  4,  6,  8,  10, 12, 14, 16, 18, 20, 22, 24, 26,
                28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50}}};

  sortedUtilityMatrix = {{0, {{0,102}, {0,103},{0,42}, {0,43}, {0,44}}}};
  */

  // ToDo: create a test unit for this function.
  /*
  case 2: 5 tiles, 42 has higher utilization but later deadline in compare to
  43.
          so, 43 should be requested first.

  utilityMatrix = {
      {"0_102", {2,  4,  6,  8,  10, 12, 14, 16, 18, 20, 22, 24, 26,
                 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50}},
      {"0_103", {2,  4,  6,  8,  10, 12, 14, 16, 18, 20, 22, 24, 26,
                 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50}},
      {"0_42", {0,  0,  0,  4,  6,  8,  10, 12, 14, 16, 18, 20, 22,
                24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46}},
      {"0_43", {1.2, 3.2, 4.6, 6,  7.9, 9.5, 11, 12, 14, 16,   18, 20,  22,
                24,  26,  28,  30, 32,  34,  36, 38, 40, 41.5, 42, 43.5}},
      {"0_44", {1.2, 3.2, 4.6, 6,  7.9, 9.5, 11, 12, 14, 16,   18, 20,  22,
                24,  26,  28,  30, 32,  34,  36, 38, 40, 41.5, 42, 43.5}}};

  sortedUtilityMatrix = {
      {0, {"0_102", "0_103"}}, {4, {"0_42"}}, {6.5, {"0_43", "0_44"}}};
  */

  /*utilityMatrix = {
      {"0_102", {0,  0,  0,  8,  10, 12, 14, 16, 18, 20, 22, 24, 26,
                 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50}},
      {"0_103", {0,  0,  0,  8,  10, 12, 14, 16, 18, 20, 22, 24, 26,
                 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50}},
      {"0_42", {0,  0,  0,  4,  6,  8,  10, 12, 14, 16, 18, 20, 22,
                24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46}},
      {"0_43", {1.2, 3.2, 4.6, 6,  7.9, 9.5, 11, 12, 14, 16,   18, 20,  22,
                24,  26,  28,  30, 32,  34,  36, 38, 40, 41.5, 42, 43.5}},
      {"0_44", {1.2, 3.2, 4.6, 6,  7.9, 9.5, 11, 12, 14, 16,   18, 20,  22,
                24,  26,  28,  30, 32,  34,  36, 38, 40, 41.5, 42, 43.5}}};

  sortedUtilityMatrix = {
      {50, {"0_102", "0_103"}}, {46, {"0_42"}}, {43.5, {"0_43", "0_44"}}};*/

  // all times in this function are in ms.
  struct tileNode {
    // tileChunk_tileId
    std::pair<int, uint16_t> tile;
    // expected time to recv tile.
    float EstArrivalTime;
    // expected time to transmit tile.
    float EstDownloadTime;
    tileNode *nextTile;
    tileNode *prevTile;
  };

  // tile with highest priority.
  tileNode *headTile = new tileNode();
  // tile with lowest priority.
  tileNode *tailTile = headTile;
  // total utility of all tiles to be downloaded.
  // Our goal is to maximize this.
  float overallUtility = 0;

  // This is the current time (base time).
  float curTime = ((frameIdToRender - 1) * 40.0);

  if (frameIdToRender != 1) {
    curTime += Util::getTimePassedSinceLastFrame();
  }
  curTime += baseTime;
  // base frame id.
  int frameIdSt = utilityMatrix.find({-1, -1})->second[0];

  // We start by choosing the lowest quality.
  // This would maximize the number of tiles we can get.

  // Tiles with highest priority first.
  // utilityTilesPair<utility, set of tiles with this utility>
  for (auto const &utilityTilesPair : sortedTilesByUtility) {
    for (auto const tile : utilityTilesPair.second) {
      uint16_t tileId = tile.second;
      int chunkId = tile.first;

      // -1 means not recieved, and 1: that's background quality.
      // so, let's try and improve the quality.
      if (clientNetworkLayer->isReceived(chunkId + 1, tileId) > 1) {
        continue;
      }
      // estimated time to download the tile chunk in lowest quality possible.
      float estDownloadTime = 1e3 * (tileChunkSizePerQuality_.find(2)
                                         ->second.find(tileId)
                                         ->second[chunkId] /
                                     estimatedBw); //

      // estimated arrival time of the tile = its download time + time of being
      // last in list.
      float estArrivalTime = estDownloadTime + curTime;
      // map the estimated arrival time of the tile to frame to cal. actual
      // utility.
      int arrvFrameId = int(estArrivalTime / 40) - frameIdSt;

      float actualUtility = 0;
      // if we expect to receive the tile within 1 sec from now, then we can
      // estimate its utility. We don't skip if arrvFrameId >= 25 as we can
      // place it early.
      if (arrvFrameId < 25) {
        actualUtility =
            utilityMatrix[tile][24] - utilityMatrix[tile][arrvFrameId];
      }
      overallUtility += actualUtility;

      // this the first tile to add (highest priority/utility)
      if (tailTile->tile.first == 0 && tailTile->tile.second == 0) {

        // This should rarely happen.
        if (arrvFrameId > 25) {
          // LOG(ERROR)
          //  << "Tile with highest priorty needs > 1 second to be received.";
          continue;
        }
        tailTile->tile = tile;
        tailTile->EstArrivalTime = estArrivalTime;
        tailTile->EstDownloadTime = estDownloadTime;
        tailTile->prevTile = nullptr;
        tailTile->nextTile = nullptr;
      } else {
        // this pointer is used to trace over the request doubly-linkedlist
        tileNode *trace = tailTile;
        // this points at the best location at which the new tile can be
        // placed before. newtile_location = potentialPosition -> prev_tile
        tileNode *potentialPosition = nullptr;
        //  this keeps track of the new utility while as we are trying to find
        //  the best location for the tile.
        float updatedUtility = overallUtility;

        while (trace != nullptr) {
          // UTILITY LOSS \\

          // cumlative utility vector for tile to be pushed further.
          auto const &utilityNxtTile = utilityMatrix[trace->tile];
          // its estimated arrival frame Id before push.
          float oldEstArrNxtTileFrameId =
              int((trace->EstArrivalTime) / 40) - frameIdSt;
          // its newly estimated arrival frame Id after push.
          float newEstArrvNxtTileFrameId =
              int((trace->EstArrivalTime + estDownloadTime) / 40) - frameIdSt;
          // how much utility is expected to be lost becuase of push.
          float utilityLoss;
          // if its estimated to be received after 1 sec, then max utility is
          // upper bound.
          if (newEstArrvNxtTileFrameId >= 25) {
            utilityLoss =
                utilityNxtTile[24] - utilityNxtTile[oldEstArrNxtTileFrameId];
          } else {
            // otherwise, it will be the new estimated arrival time.
            utilityLoss = utilityNxtTile[newEstArrvNxtTileFrameId] -
                          utilityNxtTile[oldEstArrNxtTileFrameId];
          }

          // UTILITY GAIN \\
          // cumlative utility vector for current tile.
          auto const &utilitycurrTile = utilityMatrix[tile];
          // its estimated arrival frame Id before.
          float oldEstArrCurrTileFrameId = newEstArrvNxtTileFrameId;
          // its newly estimated arrival frame Id after push.

          float newEstArrvCurrTileFrameId =
              int(((trace->EstArrivalTime - trace->EstDownloadTime) +
                   estDownloadTime) /
                  40) -
              frameIdSt;
          // how much utility is expected to be lost becuase of push.
          float utilityGain;
          // if previously its estimated to be received after 1 sec, then max
          // utility is
          // upper bound.
          if (oldEstArrCurrTileFrameId >= 25) {
            utilityGain = utilitycurrTile[24] -
                          utilitycurrTile[newEstArrvCurrTileFrameId];
          } else {
            // otherwise, it will be the new estimated arrival time.
            utilityGain = utilitycurrTile[oldEstArrCurrTileFrameId] -
                          utilitycurrTile[newEstArrvCurrTileFrameId];
          }
          updatedUtility = updatedUtility + utilityGain - utilityLoss;

          if (updatedUtility >= overallUtility) {
            overallUtility = updatedUtility;
            potentialPosition = trace;
          }
          trace = trace->prevTile;
        }

        tileNode *currTileNode = new tileNode();
        currTileNode->tile = tile;
        // it's best place could be the end of list.
        if (potentialPosition == nullptr) {
          currTileNode->EstArrivalTime =
              tailTile->EstArrivalTime + estDownloadTime;
          currTileNode->prevTile = tailTile;
          currTileNode->nextTile = nullptr;

        } else {
          currTileNode->EstArrivalTime = (potentialPosition->EstArrivalTime -
                                          potentialPosition->EstDownloadTime) +
                                         estDownloadTime;
          currTileNode->prevTile = potentialPosition->prevTile;
          currTileNode->nextTile = potentialPosition;
          currTileNode->nextTile->prevTile = currTileNode;
          if (potentialPosition == headTile) {
            headTile = currTileNode;
          }
        }
        currTileNode->EstDownloadTime = estDownloadTime;
        if (currTileNode->prevTile != nullptr) { // it is not the head.
          currTileNode->prevTile->nextTile = currTileNode;
        }
        trace = currTileNode;
        tailTile = currTileNode;
        // remove all tiles node with estimated arrival frame Id >=25;
        // if tile in middle dropped then we have to update overall utility.
        bool tileDropped = false;
        while (trace != nullptr) {
          if (trace->prevTile != nullptr) {
            trace->EstArrivalTime =
                trace->prevTile->EstArrivalTime + trace->EstDownloadTime;
          }

          auto estArrvTileFrameId = int(trace->EstArrivalTime / 40) - frameIdSt;

          if (estArrvTileFrameId >= 25) {
            if (trace == headTile) {
              headTile = nullptr;
              break;
            }
            tailTile = trace->prevTile;
            trace->prevTile->nextTile = nullptr;
            trace->prevTile = nullptr;
            trace = nullptr;
            break;
          }
          auto const &utilityNxtTile = utilityMatrix[trace->tile];
          float utilityDiff =
              utilityNxtTile[24] - utilityNxtTile[estArrvTileFrameId];
          bool dontAdvance = false;
          if (utilityDiff == 0) {
            tileDropped = true;
            if (trace->prevTile != nullptr) {
              trace->prevTile->nextTile = trace->nextTile;
              if (trace->nextTile != nullptr) {
                trace->nextTile->prevTile = trace->prevTile;
              }
              tileNode *temp = trace;
              trace = trace->prevTile;
              temp->nextTile = nullptr;
              temp->prevTile = nullptr;
            } else {
              dontAdvance = true;
              trace = trace->nextTile;
              trace->prevTile->nextTile = nullptr;
            }
          }
          if (dontAdvance) {
            continue;
          }
          tailTile = trace;
          trace = trace->nextTile;
        }

        if (tileDropped) { // recalcuate utility as it might improve.
          trace = headTile;
          float newUtility = 0;
          while (trace != nullptr) {
            auto &tileUtilityVector = utilityMatrix[trace->tile];
            newUtility +=
                tileUtilityVector[24] -
                tileUtilityVector[int(trace->EstArrivalTime / 40) - frameIdSt];
            trace = trace->nextTile;
          }
          overallUtility = newUtility;
        }
      }

      curTime = tailTile->EstArrivalTime;
    }
  }
  std::cout << overallUtility << "\n";
  std::vector<std::pair<int, uint16_t>> tilesToRequest;
  while (headTile != nullptr) {
    tilesToRequest.push_back(headTile->tile);
    headTile = headTile->nextTile;
  }
  if (tilesToRequest.size() == 1 && tilesToRequest[0].first == 0 &&
      tilesToRequest[0].second == 0) {
    return {};
  }
  return tilesToRequest;
}

std::vector<std::pair<int, uint16_t>>
AbrAlgorithm::sortTilesByUtilityAndQuality(
    uint8_t quality,
    std::map<std::pair<int, uint16_t>, std::vector<float>> utilityMatrix,
    tileNode *headRequest) {
  // quality * utility, <chunkid,tileid>
  // this is sorted such that tiles
  std::map<float, std::pair<int, uint16_t>, std::greater<float>>
      tilesUtilitySum;
  if (quality == 2) {
    for (auto &tileUtilityPair : utilityMatrix) {
      auto &tile = tileUtilityPair.first;
      float tileValueDiff =
          utilityMatrix[tile][24] *
          (tileChunkPSNRPerQuality_[quality][tile.second][tile.first] -
           tileChunkPSNRPerQuality_[1][tile.second][tile.first]);
      tilesUtilitySum.insert({tileValueDiff, tile});
    }
  } else {
    tileNode *trace = headRequest;
    while (trace != nullptr) {
      auto &tile = trace->tile;
      float tileValueDiff =
          utilityMatrix[tile][24] *
          (tileChunkPSNRPerQuality_[quality][tile.second][tile.first] -
           tileChunkPSNRPerQuality_[trace->quality][tile.second][tile.first]);
      tilesUtilitySum.insert({tileValueDiff, tile});
      trace = trace->nextTile;
    }
  }
  std::vector<std::pair<int, uint16_t>> tilesSortedByUtilitySum;
  for (auto qualityTileChunkPair : tilesUtilitySum) {
    if (qualityTileChunkPair.first == 0) {
      continue;
    }
    tilesSortedByUtilitySum.push_back(qualityTileChunkPair.second);
  }
  return tilesSortedByUtilitySum;
}

std::vector<std::pair<std::pair<int, uint16_t>, uint8_t>>
AbrAlgorithm::qualityABR(
    std::map<std::pair<int, uint16_t>, std::vector<float>> utilityMatrix,
    uint16_t frameIdToRender, float estimatedBw, float baseTime,
    ClientNetworkLayer *clientNetworkLayer) {

  std::map<std::pair<int, uint16_t>, tileNode *> tilesNodeMap;
  // tile with highest priority.
  tileNode *headTile = nullptr;
  // tile with lowest priority.
  tileNode *tailTile = nullptr;
  // total utility of all tiles to be downloaded.
  // Our goal is to maximize this.
  float overallValue = 0;

  // This is the current time (base time).
  // todo: this should be updated to newest frameIdToRender
  float curTime = ((frameIdToRender - 1) * 40.0);

  if (frameIdToRender != 1) {
    curTime += Util::getTimePassedSinceLastFrame();
  }
  curTime += baseTime;
  // base frame id.
  int frameIdSt = utilityMatrix.find({-1, -1})->second[0];
  utilityMatrix.erase({-1, -1});
  tileNode *trace;
  for (int qualityIdx = 2; qualityIdx <= numberOfQualities_; qualityIdx++) {
    auto sortedTiles =
        sortTilesByUtilityAndQuality(qualityIdx, utilityMatrix, headTile);
    for (auto &tile : sortedTiles) {
      // create tile node and add to the linked list.
      if (tilesNodeMap.find(tile) == tilesNodeMap.end()) {
        float estDownloadTime =
            1e3 * (tileChunkSizePerQuality_[1][tile.second][tile.first] /
                   estimatedBw);
        tileNode *tileN =
            new tileNode{tile, 0, estDownloadTime, 1, nullptr, nullptr};
        tilesNodeMap.insert({tile, tileN});
      }
      auto tileN = tilesNodeMap[tile];
      auto &tileUtilityVec = utilityMatrix[tile];
      auto tileOldPsnr =
          tileChunkPSNRPerQuality_[tileN->quality][tile.second][tile.first];
      auto tileNewPsnr =
          tileChunkPSNRPerQuality_[qualityIdx][tile.second][tile.first];

      // calc the old value of the tile.
      float tileOldValue = 0;
      if (tileN->EstArrivalTime != 0) { // this node already in the linkedlist
        tileOldValue =
            (tileUtilityVec[24] -
             tileUtilityVec[int(tileN->EstArrivalTime / 40) - frameIdSt]) *
            tileOldPsnr;
      } else {                     // new tile node, if so place at the end.
        if (tailTile == nullptr) { // first node in the request.
          tailTile = tileN;
          headTile = tileN;
          tileN->EstArrivalTime = tileN->EstDownloadTime + curTime;
        } else { // if not then place at the end.
          tailTile->nextTile = tileN;
          tileN->prevTile = tailTile;
          tailTile = tileN;
          tileN->EstArrivalTime =
              tileN->prevTile->EstArrivalTime + tileN->EstDownloadTime;
        }
      }

      float overallValueUpdated = overallValue - tileOldValue;
      float downloadTimeUpdated =
          1e3 * (tileChunkSizePerQuality_[qualityIdx][tile.second][tile.first] /
                 estimatedBw);

      // find the new arrival time after updating the tile quality.
      // start by placing the tile at the tail, calc the new arrival time.
      float estArrTimeUpdated = 0;
      if (tileN != tailTile) {
        estArrTimeUpdated =
            ((tailTile->EstArrivalTime - tileN->EstDownloadTime) +
             downloadTimeUpdated);
      } else {
        estArrTimeUpdated = (tileN->EstArrivalTime - tileN->EstDownloadTime) +
                            downloadTimeUpdated;
      }

      int arrFrmId = int(estArrTimeUpdated / 40) - frameIdSt;
      float tileValueUpdated = 0;

      if (arrFrmId < 25) {
        tileValueUpdated =
            (utilityMatrix[tile][24] - utilityMatrix[tile][arrFrmId]) *
            tileNewPsnr;
      }
      // if adding the tile to tail improves the overall value of the request,
      // then set placeAtTail to true
      bool placeAtTail = false;
      if (tileValueUpdated + overallValueUpdated > overallValue) {
        overallValueUpdated += tileValueUpdated;
        overallValue = overallValueUpdated;
        placeAtTail = true;
      }
      tileNode *potentionalPos = returnBestPosition(
          utilityMatrix, tailTile, tileN, frameIdSt, downloadTimeUpdated,
          tileNewPsnr, overallValueUpdated, overallValue);

      ////// TILE PLACEMENT \\\\
      // Place tile in its potention new place if exists.
      if (!placeAtTail && potentionalPos == nullptr) {
        continue;
      } else if (potentionalPos != nullptr) {
        placeAtTail = false;
      }

      if (placeAtTail && tailTile == tileN) {
        tailTile->EstArrivalTime =
            (tailTile->EstArrivalTime - tailTile->EstDownloadTime) +
            downloadTimeUpdated;
        tailTile->EstDownloadTime = downloadTimeUpdated;
        tailTile->quality = qualityIdx;
        continue;
      }

      updateArrivalTimeOfSuccessorNodes(tailTile, tileN, potentionalPos,
                                        downloadTimeUpdated, placeAtTail);

      moveAndUpdateTile(headTile, tailTile, tileN, potentionalPos,
                        downloadTimeUpdated, curTime, qualityIdx, placeAtTail);

      checkTilesUtility(utilityMatrix, headTile, tailTile, frameIdSt,
                        estimatedBw, curTime);

      // check the updated utility.
      tilesNodeMap.clear();
      trace = headTile;
      overallValue = 0;
      while (trace != nullptr) {
        tilesNodeMap.insert({trace->tile, trace});
        auto tile = trace->tile;
        auto tileUtilityVec = utilityMatrix[tile];
        auto tilePsnr =
            tileChunkPSNRPerQuality_[trace->quality][tile.second][tile.first];
        auto tileUtility =
            tileUtilityVec[24] -
            tileUtilityVec[int(trace->EstArrivalTime / 40) - frameIdSt];
        overallValue += tileUtility * tilePsnr;
        trace = trace->nextTile;
      }
    }
  }
  std::vector<std::pair<std::pair<int, uint16_t>, uint8_t>> tilesToReturn;
  while (headTile != nullptr) {
    tilesToReturn.push_back({headTile->tile, headTile->quality});
    auto temp = headTile;
    headTile = headTile->nextTile;
    if (temp != nullptr) {
      delete temp;
    }
  }
  return tilesToReturn;
  // return request.
}

AbrAlgorithm::tileNode *AbrAlgorithm::returnBestPosition(
    std::map<std::pair<int, uint16_t>, std::vector<float>> utilityMatrix,
    tileNode *&tailTile, tileNode *&tileN, int frameIdSt,
    float downloadTimeUpdated, float tileNewPsnr, float overallValueUpdated,
    float &overallValue) {
  // Since tile might be already in the linkedlist of tileNodes, so instead
  // of remvoing the tile and update the utility and download time for all
  // successor nodes. We set this bool to true once we reach the tile, and
  // stop updating DT and utility of its predecessor.
  bool tileFound = false;
  tileNode *potentionalPos = nullptr;
  tileNode *trace = tailTile;
  // try and find the best position for this tile,
  // if none exist, then keep it where it is.
  while (trace != nullptr) {
    // start tile_quality_update_loop

    if (trace->tile == tileN->tile) {
      trace = trace->prevTile;
      tileFound = true;
      continue;
    }

    // UTILITY LOSS
    // tile to switch position with.
    int toSwitchTileArrvFrameId = int(trace->EstArrivalTime / 40) - frameIdSt;
    float toSwitchTileArrvTimeUpdated =
        (trace->EstArrivalTime) + downloadTimeUpdated;
    if (!tileFound) {
      toSwitchTileArrvTimeUpdated -= tileN->EstDownloadTime;
    }
    int toSwitchTileArrvFrameIdUpdated =
        int(toSwitchTileArrvTimeUpdated / 40) - frameIdSt;
    auto toSwitchTilePsnr =
        tileChunkPSNRPerQuality_[trace->quality][trace->tile.second]
                                [trace->tile.first];

    float utilityLoss = toSwitchTilePsnr;
    // it the estimated new arrival frame Id is beyond 1 sec;
    // then upper bound is the max frmae id possible == 24.
    if (toSwitchTileArrvFrameIdUpdated >= 25) {
      utilityLoss *= (utilityMatrix[trace->tile][24] -
                      utilityMatrix[trace->tile][toSwitchTileArrvFrameId]);
    } else {
      utilityLoss *=
          (utilityMatrix[trace->tile][toSwitchTileArrvFrameIdUpdated] -
           utilityMatrix[trace->tile][toSwitchTileArrvFrameId]);
    }
    // HERE
    // UTILITY GAIN
    int tileArrvFrameIdOld = int(tileN->EstArrivalTime / 40) - frameIdSt;
    int tileArrvFrameIdUpdated =
        int((toSwitchTileArrvTimeUpdated - trace->EstDownloadTime) / 40) -
        frameIdSt;

    // the new arrv time can be > old arrv time
    float utilityGain = tileNewPsnr;
    // this happens becuase we place the tile at the end when we start looking
    // for new position
    if (tileArrvFrameIdOld >= 25 && tileArrvFrameIdUpdated < 25) {
      utilityGain *= utilityMatrix[tileN->tile][24] -
                     utilityMatrix[tileN->tile][tileArrvFrameIdUpdated];
    } else if (tileArrvFrameIdOld < 25 && tileArrvFrameIdUpdated < 25) {
      // this might be negative now.
      utilityGain *= utilityMatrix[tileN->tile][tileArrvFrameIdOld] -
                     utilityMatrix[tileN->tile][tileArrvFrameIdUpdated];
    } else if (tileArrvFrameIdUpdated >= 25 && tileArrvFrameIdOld < 25) {
      // this definitely negative as new arrv time is > old arrv time.
      utilityGain *= (utilityMatrix[tileN->tile][tileArrvFrameIdOld] -
                      utilityMatrix[tileN->tile][24]);
    }
    if (utilityGain > 1e7 || utilityGain < -1e7 || utilityLoss > 1e7 ||
        utilityLoss < -1e7) {
      std::cout << tileN->tile.first << ":" << tileN->tile.second << "\n";
      std::cout << frameIdSt << ":" << tileN->EstArrivalTime << "\n";
      std::cout << utilityGain << "= " << tileArrvFrameIdOld << " vs "
                << tileArrvFrameIdUpdated << "\n";
      std::cout << utilityLoss << "= " << toSwitchTileArrvFrameId << " vs "
                << toSwitchTileArrvFrameIdUpdated << "\n";
      std::cout << "------\n";
    }
    overallValueUpdated += utilityGain - utilityLoss;
    if (overallValueUpdated >= overallValue) {
      potentionalPos = trace;
      overallValue = overallValueUpdated;
    }
    trace = trace->prevTile;
  } // end tile_quality_update_loop
  return potentionalPos;
}

void AbrAlgorithm::updateArrivalTimeOfSuccessorNodes(tileNode *&tailTile,
                                                     tileNode *&tileN,
                                                     tileNode *&potentionalPos,
                                                     float downloadTimeUpdated,
                                                     bool placeAtTail) {
  tileNode *trace;
  float tileStartOld =
      tileN->prevTile != nullptr ? tileN->prevTile->EstArrivalTime : 0;

  float tileStartUpdated = placeAtTail
                               ? tailTile->EstArrivalTime
                               : (potentionalPos->prevTile != nullptr
                                      ? potentionalPos->prevTile->EstArrivalTime
                                      : 0);
  float diffInDT = downloadTimeUpdated - tileN->EstDownloadTime;

  // determine whether tile will be moving early in request or not.
  // if early, the update the estimated arrival times for all tiles after
  // potentionalPos. If late,  then the update should start from the tileN

  bool left = false;
  if (tileStartOld <= tileStartUpdated) {
    trace = tileN;
  } else {
    trace = potentionalPos;
    left = true;
  }

  bool found = false;
  // update arrival times for successor tiles.
  while (trace != nullptr) {
    // start  while: update EstArrivalTime

    // if left, should check whether if I reached the tileN
    // otherwise the potentional pos.
    if (left && trace == tileN) {
      found = true;
      trace = trace->nextTile;
      continue;
    } else if (!left && trace == potentionalPos) {
      found = true;
    }

    if (!found) {
      if (left) {
        trace->EstArrivalTime += downloadTimeUpdated;
      } else if (!left) {
        trace->EstArrivalTime -= tileN->EstDownloadTime;
      }
    } else {
      trace->EstArrivalTime += diffInDT;
    }
    trace = trace->nextTile;
  } // end while: update EstArrivalTime
}

void AbrAlgorithm::moveAndUpdateTile(tileNode *&headTile, tileNode *&tailTile,
                                     tileNode *&tileN,
                                     tileNode *&potentionalPos,
                                     float downloadTimeUpdated, float currTime,
                                     uint8_t qualityIdx, bool placeAtTail) {
  // change tile position and update its download time, estArrtivalTime, and
  // quality.
  tileN->quality = qualityIdx;

  if (placeAtTail) {
    if (tailTile != tileN) {
      if (tileN->prevTile == nullptr) {
        headTile = tileN->nextTile;
      } else {
        tileN->prevTile->nextTile = tileN->nextTile;
      }
      tileN->nextTile->prevTile = tileN->prevTile;
      tileN->nextTile = nullptr;
      tileN->prevTile = tailTile;
      tailTile->nextTile = tileN;
      tailTile = tileN;
    }
    tileN->EstArrivalTime = downloadTimeUpdated;
    if (tileN->prevTile != nullptr) {
      tileN->EstArrivalTime += tileN->prevTile->EstArrivalTime;
    } else {
      tileN->EstArrivalTime += currTime;
    }
  } else if (potentionalPos->prevTile == tileN) { // keep in the same position
    tileN->EstArrivalTime =
        (tileN->EstArrivalTime - tileN->EstDownloadTime) + downloadTimeUpdated;
  } else { // move the tileN to potentional Postition -> prev.

    if (potentionalPos->prevTile == nullptr) { // move to head.
      if (tileN->nextTile == nullptr) {
        // move tail to head.
        tileN->prevTile->nextTile = nullptr;
        tailTile = tileN->prevTile;
      } else {
        // move node (not tail) to head
        tileN->prevTile->nextTile = tileN->nextTile;
        tileN->nextTile->prevTile = tileN->prevTile;
      }
      tileN->nextTile = potentionalPos;
      potentionalPos->prevTile = tileN;
      tileN->prevTile = nullptr;
      headTile = tileN;
      tileN->EstArrivalTime = currTime + downloadTimeUpdated;

    } else {
      // move anywhere but not the head nor tail.
      if (tileN->nextTile == nullptr) { // move tail
        tileN->prevTile->nextTile = nullptr;
        tailTile = tileN->prevTile;
      } else if (tileN->prevTile == nullptr) { // move the head.
        tileN->nextTile->prevTile = nullptr;
        headTile = tileN->nextTile;
      } else {
        tileN->prevTile->nextTile = tileN->nextTile;
        tileN->nextTile->prevTile = tileN->prevTile;
      }
      tileN->nextTile = potentionalPos;
      tileN->prevTile = potentionalPos->prevTile;
      potentionalPos->prevTile = tileN;
      tileN->prevTile->nextTile = tileN; // cannot this if I am the head.
      tileN->EstArrivalTime =
          tileN->prevTile->EstArrivalTime + downloadTimeUpdated;
    }
  }
  tileN->EstDownloadTime = downloadTimeUpdated;
}

void AbrAlgorithm::checkTilesUtility(
    std::map<std::pair<int, uint16_t>, std::vector<float>> utilityMatrix,
    tileNode *&headTile, tileNode *&tailTile, int frameIdSt, float estimatedBw,
    float currTime) {
  // check tiles with 0 utility, if quality > 2, drop quality if still fit,
  // then keep
  tileNode *trace = headTile;
  float timeDiff;
  while (trace != nullptr) {
    auto estArrFrameId = int(trace->EstArrivalTime / 40) - frameIdSt;
    auto tileUtilityVec = utilityMatrix[trace->tile];
    float tileUtility = 0;
    if (estArrFrameId < 25) {
      tileUtility = tileUtilityVec[24] - tileUtilityVec[estArrFrameId];
    }
    if (tileUtility != 0) {
      trace = trace->nextTile;
      continue;
    }
    bool removeTile = true;
    if (tileUtility == 0) {
      while (trace->quality > 2) {
        trace->quality -= 1;
        auto EstDownloadTimeUpdated =
            1e3 * (tileChunkSizePerQuality_[trace->quality][trace->tile.second]
                                           [trace->tile.first] /
                   estimatedBw);
        auto estArrTime = EstDownloadTimeUpdated;
        if (trace->prevTile != nullptr) {
          estArrTime += trace->prevTile->EstArrivalTime;
        } else {
          estArrTime += currTime;
        }
        estArrFrameId = int(estArrTime / 40) - frameIdSt;
        tileUtility = 0;
        if (estArrFrameId < 25) {
          tileUtility = tileUtilityVec[24] - tileUtilityVec[estArrFrameId];
        }
        if (tileUtility != 0) {
          trace->EstDownloadTime = EstDownloadTimeUpdated;
          trace->EstArrivalTime = estArrTime;
          removeTile = false;
          break;
        }
      }
    }

    // remove tile.
    tileNode *temp = nullptr;
    if (removeTile) {
      if (trace->prevTile == nullptr) { // remove head;
        headTile = trace->nextTile;
        if (headTile != nullptr) { // this is the only node in linkedlist
          headTile->prevTile = nullptr;
          headTile->EstArrivalTime = headTile->EstDownloadTime + currTime;
          temp = headTile->nextTile;
        }
      } else {
        trace->prevTile->nextTile = trace->nextTile;
        if (trace->nextTile != nullptr) {
          trace->nextTile->prevTile = trace->prevTile;
        } else {
          tailTile = tailTile->prevTile;
        }
        temp = trace->nextTile;
      }
      auto tileRemovedNode = trace;
      trace = trace->nextTile;
      tileRemovedNode->prevTile = nullptr;
      tileRemovedNode->nextTile = nullptr;
      delete tileRemovedNode;
    } else { // if tile is not to remove.
      temp = trace->nextTile;
      trace = trace->nextTile;
    }

    // update the estimated time for successor tiles.
    while (temp != nullptr) {

      temp->EstArrivalTime = temp->EstDownloadTime;
      if (temp->prevTile != nullptr) {
        temp->EstArrivalTime += temp->prevTile->EstArrivalTime;
      }
      temp = temp->nextTile;
    }
  } // end while
}

uint8_t AbrAlgorithm::getNumberOfQualities() { return numberOfQualities_; }

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

long AbrAlgorithm::getTilesSizes(
    std::vector<std::pair<std::pair<int, uint16_t>, uint8_t>> &fgTiles) {
  long totalSize = 0;
  for (auto &tile : fgTiles) {
    totalSize += tileChunkSizePerQuality_.find(tile.second)
                     ->second.find(tile.first.second)
                     ->second[tile.first.first];
  }
  return totalSize;
}

/***********************PANO*****************************/

// this uses alpha - beta pruning to
// find the highest overall psnr
// and lowest size (size that matches bitrate).

// prune if lower PSNR or if similar PSNR and smaller size.
// if no possible assignment it is lowest quality for all.

void AbrAlgorithm::panoAbr(AbrAlgorithm *abrAlgorithm,
                           TilePredictor *tilePredictor,
                           BandwidthPredictor *bandwidthPredictor,
                           ClientNetworkLayer *clientNetworkLayer,
                           VideoPlayer *videoPlayer) {
  // every 100ms, update tile list.
  long stime = Util::getTime();
  float videoTime = 0;
  std::map<uint8_t, std::vector<std::pair<int, uint16_t>>> tilesRequest;
  abrAlgorithm->buildQualityAssigment({}, 3);

  while (true) {
    // std::cout << req << std::endl;
    // clientNetworkLayer->setRequest(req);
    auto frameToRenderId = videoPlayer->getFrameToRenderId();
    auto chunksBitrates = abrAlgorithm->mpc(
        bandwidthPredictor, clientNetworkLayer, frameToRenderId);

    tilesRequest.clear();
    Util::sleep(stime, ABR_FREQ);
    videoTime += (Util::getTime() - stime);
    stime += 100;
  }
}

std::vector<uint64_t> AbrAlgorithm::mpc(BandwidthPredictor *bandwidthPredictor,
                                        ClientNetworkLayer *clientNetworkLayer,
                                        uint32_t frameId) {

  // determine buffer occupancy
  auto bufferStat = getBufferStatus(clientNetworkLayer, frameId);
  int chunkId = ((frameId - 1) / 25);
  int stChunkId = chunkId;
  // (first frame in next chunk - current frame) * <frame duration in sec>
  uint32_t timeLeftInCurrChunk = (((chunkId + 1) * 25) - (frameId - 1)) * 0.04;
  int buff = bufferStat[0] == 144 ? timeLeftInCurrChunk : -timeLeftInCurrChunk;

  for (auto const numRecvTiles : bufferStat) {
    if (numRecvTiles == 144) {
      stChunkId++;
    }
  }

  float predictedBw = bandwidthPredictor->getMpcBandwidthPrediction();
  float highestPSNR =
      qualityChunkPSNR_.find(qualityChunkPSNR_.size() - 1)->second[chunkId];

  int currRebuffer;
  int bufferCal;
  int bitrateSum;
  float smoothnessDiff;
  float prevPSNR;
  std::vector<uint8_t> bestAssignment;
  float reward;
  float maxReward = std::numeric_limits<float>::min();
  for (auto const &qulityAssignment : qualityAssignments_) {
    currRebuffer = 0;
    bufferCal = buff;
    bitrateSum = 0;
    smoothnessDiff = 0;
    prevPSNR = getAvgPSNR(clientNetworkLayer, chunkId);
    for (uint8_t qIdx = 0; qulityAssignment.size(); qIdx++) {
      auto qualityForchunkId = chunkId + qIdx;
      // if chunk is received, then skip finding quality for it.
      if (qualityForchunkId < stChunkId) {
        // add 1 second to buffer if not the first chunk
        // if it is the first, then we already timeLeftInCurrChunk
        // to buffer
        if (qualityForchunkId != chunkId) {
          bufferCal += 1;
        }
        continue;
      }

      int chunkSize = qualityChunkSize_.find(qulityAssignment[qIdx])
                          ->second[qualityForchunkId];
      float downloadTime = chunkSize / predictedBw; // seconds.
      if (downloadTime > bufferCal) {
        currRebuffer += (downloadTime - bufferCal);
        bufferCal = 0;
      } else {
        bufferCal -= downloadTime;
      }
      bufferCal += 1; // length of chunk
      auto const chunkPSNR = qualityChunkPSNR_.find(qulityAssignment[qIdx])
                                 ->second[qualityForchunkId];
      smoothnessDiff += std::abs(prevPSNR - chunkPSNR);
      bitrateSum += chunkPSNR;
      prevPSNR = chunkPSNR;
    }
    reward = bitrateSum - smoothnessDiff - (currRebuffer * highestPSNR);
    if (reward > maxReward) {
      maxReward = reward;
      bestAssignment = qulityAssignment;
    }
  }

  // bitrate per chunk.
  // 0 means chunk recieved.
  std::vector<uint64_t> chunksBitrate;
  for (uint8_t qIdx = 0; bestAssignment.size(); qIdx++) {
    auto qualityForchunkId = chunkId + qIdx;
    if (qualityForchunkId < stChunkId) {
      chunksBitrate.push_back(0);
      continue;
    }
    chunksBitrate.push_back(qualityChunkSize_.find(bestAssignment[qIdx])
                                ->second[qualityForchunkId]);
  }
  return chunksBitrate;
}

float AbrAlgorithm::getAvgPSNR(ClientNetworkLayer *clientNetworkLayer,
                               int chunkId) {
  int tilesPSNR = 0;
  int tilesCount = 0;
  for (uint16_t tileId = 0; tileId <= 144; tileId++) {
    auto tileQuality = clientNetworkLayer->isReceived(chunkId, tileId);
    if (tileQuality > 0) {
      tilesPSNR += tilesPSNR;
      tilesCount++;
    }
  }
  return (tilesPSNR * 1.0) / tilesCount;
}

std::vector<uint16_t>
AbrAlgorithm::getBufferStatus(ClientNetworkLayer *clientNetworkLayer,
                              uint32_t frameId) {
  std::vector<uint16_t> numOfTilesRecvPerChunk;
  int stChunkId = ((frameId - 1) / 25) + 1; // server adds one.
  for (auto chunkId = stChunkId; chunkId < stChunkId + 3; chunkId++) {
    uint16_t numberOfTilesRecieved = 0;
    for (u_int16_t tileId = 1; tileId <= 144; tileId++) {
      if (clientNetworkLayer->isReceived(chunkId, tileId) >= 1) {
        numberOfTilesRecieved++;
      }
    }
    numOfTilesRecvPerChunk.push_back(numberOfTilesRecieved);
  }
  return numOfTilesRecvPerChunk;
}

void AbrAlgorithm::buildQualityAssigment(std::vector<uint8_t> assignment,
                                         int numOfChunkInHorizon) {
  if (numOfChunkInHorizon == 0) {
    qualityAssignments_.push_back(assignment);
    return;
  }
  for (uint8_t quality = 1; quality <= numberOfQualities_; quality++) {
    assignment.push_back(quality);
    buildQualityAssigment(assignment, numOfChunkInHorizon - 1);
    assignment.pop_back();
  }
}