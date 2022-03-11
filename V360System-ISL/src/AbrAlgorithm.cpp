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
  std::vector<std::pair<float, float>> predictedCorr;

  while (true) {
    tilesInPrevSets.clear();
    // get the predicted tiles every ABR_FREQ(100ms).
    // we will have mutliple sets (e.g. viewport tiles, viewport edge tiles ,
    // further tiles, rest of tiles)

    // key: high quality (HQ)/ low quality (LQ)
    // value: list of urgent tiles sorted by their overlapping area with
    // viewport.
    std::map<std::string, std::map<float, std::vector<uint16_t>>> urgentTiles;
    // tilePredictor->getPredictedCorr(predictedCorr);
    // tilePredictor->getUrgetTilesLists(urgentTiles, predictedCorr);
    auto tileClassesOfFutureFrames = tilePredictor->getPredictedTilesFlareLR();
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
             qualityIdx++) { // per quality

          for (auto const &tile : SetOftilesInClass.second) { // per tile
            // if tile chunk is recevied then do not count it.
            std::string tileKey =
                std::to_string(chunkId) + "_" + std::to_string(tile);
            // if the tile already included in earlier frame of higher rank
            // class, then skip (no duplicates)
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
    // LOG(INFO) << "Bandwidth: " << (predictedBw * 8 / 1e6)
    //        << " , Next frame: " << frameIdToRender;

    for (int quality = numOfQualities; quality > 0; quality--) {
      // for all possible solutions
      for (auto const &solution : qualitiesAssignments.find(quality)->second) {
        // try the solution: calculate the timing for all sets in all frames
        float timeCascade = currentVideoTime;
        qualityFound = true;
        // go through all classes in all frames one by one based on render
        // deadline.
        // LOG(INFO) << "Solution = " << solution;
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
                    << " , size= " << totalFrameTileSizes
                    << "(currentTime : " << timeCascade
                    << ", frame deadline : " << frameTilesDeadline
                    << " , download time : " << downloadTime << ")";*/
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

std::pair<std::string, int> AbrAlgorithm::buildBackgroundTilesRequest(
    uint32_t frameIdToRender, ClientNetworkLayer *clientNetworkLayer,
    std::map<float, std::vector<uint16_t>> &urgetTiles) {

  // Objective: get all urgent tiles in lowest quality for the next two seconds

  // find the chunk ids correspond to the next two seconds.
  int chunkId = (((frameIdToRender)-1) / 25);
  std::vector<int> chunkIds = {chunkId, chunkId + 1};
  if ((frameIdToRender - 1) % 25 != 0) {
    chunkIds.push_back(chunkId + 2);
  }

  std::vector<std::string> tilesReq(chunkIds.size());

  int size = 0;
  int idx;
  for (auto &tileSet : urgetTiles) {
    if (tileSet.first == 1) {
      continue;
    }
    for (auto &tile : tileSet.second) {
      for (idx = 0; idx < chunkIds.size(); idx++) {
        if (!clientNetworkLayer->isReceived(chunkIds[idx] + 1, tile)) {
          tilesReq[idx] +=
              std::to_string(chunkIds[idx]) + "_" + std::to_string(tile) + ",";
          size += tileChunkSizePerQuality_.find(1)
                      ->second.find(tile)
                      ->second[chunkIds[idx]];
        }
      }
    }
  }

  std::string finalRequest = "";
  for (auto &request : tilesReq) {
    finalRequest += request;
  }
  std::pair<std::string, int> reqSize = {finalRequest, size};
  return reqSize;
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
  auto &tileChunkSizePerQuality = abrAlgorithm->getTileChunkSizePerQuality();

  // This set will contain all tiles in prev sets (to contain duplicates)
  // tilechunk_tileIdx
  std::vector<std::pair<float, float>> predictedCorr;
  std::vector<std::pair<int, int>> vpResolutions = {{100, 100}, {120, 120}};
  while (true) {

    // retrieve the predicted tiles using linear regression.
    predictedCorr.clear();
    tilePredictor->getPredictedCorr(predictedCorr);
    auto frameIdToRender = videoPlayer->getFrameToRenderId();

    // generate a list of all required background tiles.
    std::map<float, std::vector<uint16_t>> urgentTiles;
    tilePredictor->getUrgetTilesList(urgentTiles, predictedCorr);
    auto urgentTileRequestAndSize = abrAlgorithm->buildBackgroundTilesRequest(
        frameIdToRender, clientNetworkLayer, urgentTiles);

    // generate the utility matrix for predicted-to-render tiles in the next 25
    // frames (1sec).
    auto utilityMatrix =
        tilePredictor->buildUtilityMatrix(predictedCorr, vpResolutions, 25);

    // sort tiles by their max utility.
    auto orderedUtilityMatrix =
        abrAlgorithm->orderTilesByMaxUtility(utilityMatrix, frameIdToRender);

    float predictedBw =
        (bandwidthPredictor->getMpcBandwidthPrediction() * 1e6) /
        8.0; // Bytes Per Second

    // pick tiles that would acheive the highest overall maximum utility.
    auto request = abrAlgorithm->getTilesWithMaxOverallUtility(
        utilityMatrix, orderedUtilityMatrix, frameIdToRender,
        predictedBw == 0 ? 2.5 * 1e6 : predictedBw, tileChunkSizePerQuality,
        clientNetworkLayer);

    /*std::cout << std::to_string(frameIdToRender) << "----"
              << urgentTileRequestAndSize.second << std::endl;
    std::cout << urgentTileRequestAndSize.first << std::endl;*/
    std::string req = "Tiles\n" + urgentTileRequestAndSize.first;
    /*for (auto const &tile : request) {
      req += tile + ",";
    }*/
    req.pop_back();
    req += "\nQuality\n" + std::to_string(0);
    clientNetworkLayer->setRequest(req);
    Util::sleep(stime, ABR_FREQ);
    videoTime += (Util::getTime() - stime);
    stime += 100;
  }
}

std::map<float, std::vector<std::string>> AbrAlgorithm::orderTilesByMaxUtility(
    std::map<std::string, std::vector<float>> utilityMatrix,
    uint16_t frameIdToRender) {
  float frameIdSt = utilityMatrix.find("frameIdAtCol0")->second[0];

  std::map<float, std::vector<std::string>> sortedUtilityMatrix;
  for (auto const tileChunk : utilityMatrix) {
    if (tileChunk.first == "frameIdAtCol0") {
      continue;
    }
    // 50 = number of frames in the future (25) * number of classes (2)
    auto maxUtility = 50.0 - tileChunk.second[24];
    // deduct the utility of the frames that have already passed deadline.

    if (frameIdToRender > frameIdSt && frameIdToRender != 1) {
      maxUtility -= tileChunk.second[frameIdToRender - frameIdSt];
    }
    if (sortedUtilityMatrix.find(maxUtility) == sortedUtilityMatrix.end()) {
      std::vector<std::string> tileChunks;
      sortedUtilityMatrix.insert(std::make_pair(maxUtility, tileChunks));
    }
    sortedUtilityMatrix.find(maxUtility)->second.push_back(tileChunk.first);
  }
  if (VLOG_IS_ON(1)) {
    LOG(INFO) << "=== Utility Matrix [" << frameIdSt << "]===";

    for (auto const tileChunk : utilityMatrix) {
      std::string p = tileChunk.first + ":";
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
        p += tile + ",";
      }
      p.pop_back();
      LOG(INFO) << p;
    }
  }
  return sortedUtilityMatrix;
}

std::vector<std::string> AbrAlgorithm::getTilesWithMaxOverallUtility(
    std::map<std::string, std::vector<float>> utilityMatrix,
    std::map<float, std::vector<std::string>> sortedUtilityMatrix,
    uint16_t frameIdToRender, float estimatedBw,
    std::map<uint8_t, std::map<uint16_t, std::vector<uint64_t>>> tileChunkSizes,
    ClientNetworkLayer *clientNetworkLayer) {
  // std::cout << "BW: " << estimatedBw * 8 / 1e6 << std::endl;
  // std::cout << "Frame Id: " << std::to_string(frameIdToRender) << std::endl;
  /*
  case 1: simple 5 tiles, all same utility.
  utilityMatrix = {
      {"0_102", {2,  4,  6,  8,  10, 12, 14, 16, 18, 20, 22, 24, 26,
                 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50}},
      {"0_103", {2,  4,  6,  8,  10, 12, 14, 16, 18, 20, 22, 24, 26,
                 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50}},
      {"0_42", {2,  4,  6,  8,  10, 12, 14, 16, 18, 20, 22, 24, 26,
                28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50}},
      {"0_43", {2,  4,  6,  8,  10, 12, 14, 16, 18, 20, 22, 24, 26,
                28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50}},
      {"0_44", {2,  4,  6,  8,  10, 12, 14, 16, 18, 20, 22, 24, 26,
                28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50}}};

  sortedUtilityMatrix = {{0, {"0_102", "0_103", "0_42", "0_43", "0_44"}}};
  */

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
    std::string tile;
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

  // Utility at column 0 corresponds to which frame.
  int frameIdSt = utilityMatrix.find("frameIdAtCol0")->second[0];

  // We start by choosing the lowest quality.
  // This would maximize the number of tiles we can get.

  // Tiles with highest priority first.
  // utilityTilesPair<utility, set of tiles with this utility>
  for (auto const &utilityTilesPair : sortedUtilityMatrix) {
    for (auto const tile : utilityTilesPair.second) {
      // chunk Id _ tile Id
      std::size_t pos = tile.find("_");
      uint16_t tileId = static_cast<uint16_t>(std::stoi(tile.substr(pos + 1)));
      int chunkId = std::stoi(tile.substr(0, pos));
      if (clientNetworkLayer->isReceived(chunkId + 1, tileId)) {
        continue;
      }
      // estimated time to download the tile chunk in lowest quality possible.
      float estDownloadTime =
          1e3 * (tileChunkSizes.find(2)->second.find(tileId)->second[chunkId] /
                 estimatedBw); //

      // estimated arrival time of the tile.
      float estArrivalTime = estDownloadTime + curTime;
      // map the estimated arrival time of the tile to frame to cal. actual
      // utility.
      int arrvFrameId = int(estArrivalTime / 40) - frameIdSt;

      float actualUtility = 0;
      // if we expect to receive the tile within 1 sec from now, then we can
      // estimate its utility.
      if (arrvFrameId < 25) {
        actualUtility =
            utilityMatrix[tile][24] - utilityMatrix[tile][arrvFrameId];
      }
      overallUtility += actualUtility;

      // this the first tile to add (highest priority/utility)
      if (tailTile->tile == "") {

        // This should rarely happen.
        if (arrvFrameId > 25) {
          LOG(ERROR)
              << "Tile with highest priorty needs > 1 second to be received.";
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
        // this points at the best location the tile can be received at/after.
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
        if (currTileNode->prevTile != nullptr) {
          currTileNode->prevTile->nextTile = currTileNode;
        }
        trace = currTileNode;
        tailTile = currTileNode;
        // remove all tiles node with estimated arrival frame Id >=25;
        while (trace->nextTile != nullptr) {
          trace->nextTile->EstArrivalTime =
              trace->EstArrivalTime + trace->nextTile->EstDownloadTime;
          auto estArrvNxtTileFrameId =
              int(trace->nextTile->EstArrivalTime / 40) - frameIdSt;
          if (estArrvNxtTileFrameId >= 25) {
            tailTile = trace;
            trace->nextTile->prevTile = nullptr;
            trace->nextTile = nullptr;
            break;
          }
          trace = trace->nextTile;
          tailTile = trace;
        }
      }
      curTime = tailTile->EstArrivalTime;
      // std::cout << curTime << std::endl;
    }
  }

  std::vector<std::string> tilesToRequest;
  while (headTile != nullptr) {
    tilesToRequest.push_back(headTile->tile);
    headTile = headTile->nextTile;
  }
  return tilesToRequest;
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
