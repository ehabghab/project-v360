/*
 * TilePredictor.cpp
 *
 *  Created on: May 5, 2021
 *      Author: eghabash
 */

#include "TilePredictor.h"

#include <glog/logging.h>
#include <unistd.h>

#include <algorithm>
#include <chrono>
#include <cstdlib>
#include <iostream>
#include <set>
#include <thread>
#include <utility>

void TilePredictor::getViewportSquares(
    std::vector<SquareCoordinates> &vpSquares,
    std::pair<float, float> viewportCenter,
    std::pair<int, int> viewportResolution) {
  // find viewport coordinates.
  float baseX1 = viewportCenter.first - (viewportResolution.first / 2.0);
  float baseX2 = viewportCenter.first + (viewportResolution.first / 2.0);

  // 0: viewport is not wrapping.
  int horizontalFlip = 0;

  // 0: viewport is not wrapping, 1: wrapping over y = 0; 2: wrapping over y =
  // 180.
  int verticalFlip = 0;

  // frame in degrees [0 - 360] in width, and [0-180] in height.

  // viewport is wrapping over x = 0.
  if (baseX1 < 0) {
    baseX1 += 360;
  }

  // viewport is wrapping over x = 360.
  if (baseX2 > 360) {
    baseX2 -= 360;
  }

  float x1 = baseX1;
  float x2 = baseX2;
  float y1 = viewportCenter.second - (viewportResolution.second / 2.0);

  // viewport is wrapping over y = 0.
  if (y1 < 0) {
    y1 = 180 - (y1 + 180);
    x1 = baseX1 + 180;
    x2 = baseX2 + 180;
    if (x1 > 360) {
      x1 = x1 - 360;
    }
    if (x2 > 360) {
      x2 = x2 - 360;
    }
  }

  float x3 = baseX1;
  float x4 = baseX2;
  float y2 = viewportCenter.second + (viewportResolution.second / 2.0);

  // viewport is wrapping over y = 180.
  if (y2 > 180) {
    y2 = 180 - (y2 - 180);
    x3 = baseX1 + 180;
    x4 = baseX2 + 180;
    if (x3 > 360) {
      x3 = x3 - 360;
    }

    if (x4 > 360) {
      x4 = x4 - 360;
    }
  }

  if (x1 > x2 || x3 > x4) {
    // left edge x coordinate > right edge x coordinate
    horizontalFlip = 1;
  }

  if (x1 != x3) {
    // left edges are not aligned.
    if ((180 - viewportCenter.second) > (viewportCenter.second)) {
      // the center y coor. is closer to y = 0, than y = 180!
      verticalFlip = 1;
    } else {
      verticalFlip = 2;
    }
  }

  // 6 cases of overlapping, get viewport squares.
  if (horizontalFlip == 0 && verticalFlip == 0) {
    // only one square.
    SquareCoordinates vp = {std::make_pair(x3, y2), std::make_pair(x4, y2),
                            std::make_pair(x1, y1), std::make_pair(x2, y1)};
    vpSquares = {vp};
  } else if (horizontalFlip == 0 && verticalFlip == 1) {
    // viewport has two squares due to overlapping over y = 0.
    SquareCoordinates vpPart1 = {
        std::make_pair(x3, y2),
        std::make_pair(x4, // @suppress("Invalid arguments")
                       y2),
        std::make_pair(x3, 0), std::make_pair(x4, 0)};

    SquareCoordinates vpPart2 = {
        std::make_pair(x1, y1),
        std::make_pair(x2, // @suppress("Invalid arguments")
                       y1),
        std::make_pair(x1, 0), std::make_pair(x2, 0)};
    vpSquares = {vpPart1, vpPart2};
  } else if (horizontalFlip == 0 && verticalFlip == 2) {
    // viewport has two squares due to overlapping over y = 180.
    SquareCoordinates vpPart1 = {
        std::make_pair(x3, 180), std::make_pair(x4, 180),
        std::make_pair(x3, y2), std::make_pair(x4, y2)};

    SquareCoordinates vpPart2 = {
        std::make_pair(x1, 180), std::make_pair(x2, 180),
        std::make_pair(x1, y1), std::make_pair(x2, y1)};
    vpSquares = {vpPart1, vpPart2};
  } else if (horizontalFlip == 1 && verticalFlip == 0) {
    // viewport has two squares due to overlapping over x = 0 or x = 360.
    SquareCoordinates vpPart1 = {std::make_pair(0, y2), std::make_pair(x4, y2),
                                 std::make_pair(0, y1), std::make_pair(x2, y1)};

    SquareCoordinates vpPart2 = {
        std::make_pair(x3, y2), std::make_pair(360, y2), std::make_pair(x1, y1),
        std::make_pair(360, y1)};
    vpSquares = {vpPart1, vpPart2};
  } else if (horizontalFlip == 1 && verticalFlip == 1) {
    // viewport has three squares due to nested overlapping over x = 0 or x =
    // 360 and y = 0.

    if (x2 < x1) {
      SquareCoordinates vpPart1 = {std::make_pair(0, y1),
                                   std::make_pair(x2, y1), std::make_pair(0, 0),
                                   std::make_pair(x2, 0)};

      SquareCoordinates vpPart2 = {
          std::make_pair(x3, y2), std::make_pair(x4, y2), std::make_pair(x3, 0),
          std::make_pair(x4, 0)};

      SquareCoordinates vpPart3 = {
          std::make_pair(x1, y1), std::make_pair(360, y1),
          std::make_pair(x1, 0), std::make_pair(360, 0)};
      vpSquares = {vpPart1, vpPart2, vpPart3};
    } else if (x4 < x3) {
      SquareCoordinates vpPart1 = {std::make_pair(0, y2),
                                   std::make_pair(x4, y2), std::make_pair(0, 0),
                                   std::make_pair(x4, 0)};

      SquareCoordinates vpPart2 = {
          std::make_pair(x1, y1), std::make_pair(x2, y1), std::make_pair(x1, 0),
          std::make_pair(x2, 0)};

      SquareCoordinates vpPart3 = {
          std::make_pair(x3, y2), std::make_pair(360, y2),
          std::make_pair(x3, 0), std::make_pair(360, 0)};
      vpSquares = {vpPart1, vpPart2, vpPart3};
    }

  } else if (horizontalFlip == 1 && verticalFlip == 2) {
    // viewport has three squares due to nested overlapping over x = 0 or x =
    // 360 and y = 180.

    if (x2 < x1) {
      SquareCoordinates vpPart1 = {
          std::make_pair(0, 180), std::make_pair(x2, 180),
          std::make_pair(0, y1), std::make_pair(x2, y1)};

      SquareCoordinates vpPart2 = {
          std::make_pair(x3, 180), std::make_pair(x4, 180),
          std::make_pair(x3, y2), std::make_pair(x4, y2)};

      SquareCoordinates vpPart3 = {
          std::make_pair(x1, 180), std::make_pair(360, 180),
          std::make_pair(x1, y1), std::make_pair(360, y1)};
      vpSquares = {vpPart1, vpPart2, vpPart3};
    } else if (x4 < x3) {
      SquareCoordinates vpPart1 = {
          std::make_pair(0, 180), std::make_pair(x4, 180),
          std::make_pair(0, y2), std::make_pair(x4, y2)};

      SquareCoordinates vpPart2 = {
          std::make_pair(x1, 180), std::make_pair(x2, 180),
          std::make_pair(x1, y1), std::make_pair(x2, y1)};

      SquareCoordinates vpPart3 = {
          std::make_pair(x3, 180), std::make_pair(360, 180),
          std::make_pair(x3, y2), std::make_pair(360, y2)};
      vpSquares = {vpPart1, vpPart2, vpPart3};
    }
  }
}

float TilePredictor::getFractionOfTileInVP(
    std::vector<SquareCoordinates> &partialVPs,
    std::pair<float, float> tileCorrdinates,
    std::pair<float, float> tileDimensions) {
  float fracOfTileInVP = 0.0;

  for (auto const &sqrCoor : partialVPs) {
    float xOverlap = std::max(
        (float)0, std::min(sqrCoor.upperRight.first,
                           tileCorrdinates.first + tileDimensions.first) -
                      std::max(sqrCoor.upperLeft.first, tileCorrdinates.first));

    float yOverlap = std::max(
        (float)0, std::min(sqrCoor.upperRight.second, tileCorrdinates.second) -
                      std::max(sqrCoor.lowerRight.second,
                               tileCorrdinates.second - tileDimensions.second));

    fracOfTileInVP += (xOverlap * yOverlap) /
                      float(tileDimensions.first * tileDimensions.second);
  }

  return fracOfTileInVP;
}

std::map<uint16_t, std::map<uint8_t, std::vector<uint16_t>>>
TilePredictor::getPredictedTilesLR() {
  std::map<uint16_t, std::map<uint8_t, std::vector<uint16_t>>>
      tileClassAllFrames;

  // video join time as it only happens at the start of video sessions.
  while (frameId_ == 0)
    ;
  std::vector<std::pair<int, int>> vpResolutions = {{100, 100}, {120, 120}};

  std::vector<std::pair<float, float>> predictedCorr;
  if (frameId_ >= 13) {
    predictedCorr =
        linearRegressor_->predict(std::ref(vpGroundTruth_), frameId_);
  }

  // predictedCorr = linearRegressor_->predictPerfect(frameId_);

  uint16_t frameId = frameId_;

  for (uint16_t idx = 0; idx < 25; idx++) { // per frame
    if (frameId >= 1475) {
      break;
    }
    int chunkId = ((frameId + idx) - 1) / 25;

    std::pair<float, float> viewportCenter;
    // use static predictor.
    if (predictedCorr.size() == 0) {
      viewportCenter = vpGroundTruth_[frameId_ - 1];
    } else {
      viewportCenter = predictedCorr[idx];
    }
    // Key: tile-class (i.e. rank).
    // Value: all tiles with that class.
    std::map<uint8_t, std::vector<uint16_t>> fillingMap;

    // Key: frame id
    // Value: all predicted tiles sorted based on rank into sets.
    //        and, tiles within the set are sorted based on area overlapped with
    //        viewport.
    tileClassAllFrames.insert(std::make_pair(frameId + idx, fillingMap));
    auto &tileClassMap = tileClassAllFrames.find(frameId + idx)->second;

    // Two classes: 0 (VP--> highest_class), and 1 (Edge)
    uint8_t tileClass = 0;

    for (auto &vpResolution : vpResolutions) { // per vp-class
      // find viewport squares.
      std::vector<SquareCoordinates> vpSqrs;
      getViewportSquares(vpSqrs, viewportCenter, vpResolution);

      // key: fraction area of tile that overlaps with viewport.
      // value: list of all tiles.

      std::map<float, std::vector<uint16_t>> tilesSortedByArea;
      sortTileSetByArea(tilesSortedByArea, vpSqrs,
                        vpResolution.first * vpResolution.second);
      for (auto const &tileSet : tilesSortedByArea) {
        // if the tiles do not overlap with viewport then skip.
        if ((1 - tileSet.first) == 0) {
          continue;
        }

        // go over all tiles in the set.
        for (auto const &tile : tileSet.second) {
          if (tileClassMap.find(tileClass) == tileClassMap.end()) {
            std::vector<uint16_t> tileSet;
            tileClassMap.insert(std::make_pair(tileClass, tileSet));
          }
          tileClassMap.find(tileClass)->second.push_back(tile);
        }
        if (VLOG_IS_ON(1)) {
          VLOG(1) << "Fraction of area in viewport:" << (1 - tileSet.first);
          std::string vLogTiles;
          for (auto const &tile : tileSet.second) {
            vLogTiles += std::to_string(tile) + ",";
          }
          VLOG(1) << vLogTiles;
        }
      }
      tileClass++;
    }
    if (tileClassAllFrames.find(frameId + idx)->second.size() == 0) {
      tileClassAllFrames.erase(frameId + idx);
    }
  }
  // print tiles in sets
  if (VLOG_IS_ON(1)) {
    for (auto const &chunkSet : tileClassAllFrames) {
      for (auto const &setTiles : chunkSet.second) {
        LOG(INFO) << static_cast<int>(chunkSet.first) << ":"
                  << static_cast<int>(setTiles.first);
        std::string tiles;
        for (auto const &tile : setTiles.second) {
          tiles += std::to_string(tile) + ",";
        }
        LOG(INFO) << tiles;
      }
    }
    LOG(INFO) << "==================";
  }
  return tileClassAllFrames;
}

std::map<uint16_t, std::map<uint8_t, std::vector<uint16_t>>>
TilePredictor::getPredictedTilesStatic() {
  std::map<uint16_t, std::map<uint8_t, std::vector<uint16_t>>>
      tileClassAllFrames;

  // video join time as it only happens at the start of video sessions.
  while (frameId_ == 0)
    ;
  std::vector<std::pair<int, int>> vpCorrs = {{100, 100}, {120, 120}};

  // Todo fix
  uint16_t frameId = frameId_;

  int lastFrame = frameId + 25 * 3;
  // TODO: think how the prediction algorithm would fit.
  for (; frameId < lastFrame; frameId += 25) {
    if (frameId >= 1475) {
      break;
    }
    std::map<uint8_t, std::vector<uint16_t>> fillingMap;
    tileClassAllFrames.insert(std::make_pair(frameId, fillingMap));
    auto &viewportCenter = vpGroundTruth_[frameId_ - 1];
    auto &tileClassMap = tileClassAllFrames.find(frameId)->second;

    /*
     * key is rank where 0(highest rank), and so on.
     * value is list of tiles with the same rank (key),
     * ordered by fraction of area overlapping with viewport.
     * For instance, first tile (index 0) with key = 0,
     * will be the highly ranked tile.
     */
    uint8_t tileClass = 0;

    // This set will contain all tiles in prev set. all tiles in set are
    // unique.
    std::set<uint16_t> tilesInPrevSets;
    for (auto &vpCorr : vpCorrs) {
      // find viewport squares.
      std::vector<SquareCoordinates> vpSqrs;
      getViewportSquares(vpSqrs, viewportCenter, vpCorr);

      // key: fraction area of tile that overlaps with viewport.
      // value: all tiles with fraction of area overlapping with viewport
      // equals to key.
      std::map<float, std::vector<uint16_t>> tileRanksByArea;
      sortTileSetByArea(tileRanksByArea, vpSqrs, vpCorr.first * vpCorr.second);

      for (auto const &tiles : tileRanksByArea) {
        // if the tiles do not overlap with viewport then skip.
        if ((1 - tiles.first) == 0) {
          continue;
        }

        for (auto const &tile : tiles.second) {
          // if the tile already included in previous higher rank sets, no
          // need to include it in the lower sets
          if (tilesInPrevSets.find(tile) != tilesInPrevSets.end()) {
            continue;
          }
          tilesInPrevSets.insert(tile);

          if (tileClassMap.find(tileClass) == tileClassMap.end()) {
            std::vector<uint16_t> tileSet;
            tileClassMap.insert(std::make_pair(tileClass, tileSet));
          }

          tileClassMap.find(tileClass)->second.push_back(tile);
        }

        if (VLOG_IS_ON(1)) {
          VLOG(1) << "Fraction of area in viewport:" << (1 - tiles.first);
          std::string vLogTiles;
          for (auto const &tile : tiles.second) {
            vLogTiles += std::to_string(tile) + ",";
          }
          VLOG(1) << vLogTiles;
        }
      }
      tileClass++;
    }
  }
  // print tiles in sets
  if (VLOG_IS_ON(1)) {
    for (auto const &tileClassesSingleFrame : tileClassAllFrames) {
      for (auto const &tileClass : tileClassesSingleFrame.second) {
        LOG(INFO) << static_cast<int>(tileClassesSingleFrame.first) << ":"
                  << static_cast<int>(tileClass.first);
        std::string tiles;
        for (auto const &tile : tileClass.second) {
          tiles += std::to_string(tile) + ",";
        }
        LOG(INFO) << tiles;
      }
    }
    LOG(INFO) << "==================";
  }

  return tileClassAllFrames;
}

void TilePredictor::sortTileSetByArea(
    std::map<float, std::vector<uint16_t>> &tileRanksByArea,
    std::vector<SquareCoordinates> &vpSqrs, int vpArea) {
  // per tile in frame get the fraction of its area that overlaps with
  // viewport.
  float vpSize = 0;
  for (auto const &tileId : tileCoordinates_) {
    float frac = getFractionOfTileInVP(std::ref(vpSqrs), tileId.second,
                                       tileResolutions_[tileId.first]);
    vpSize += frac;

    // (1.0 - frac) will sort tiles in the map by area
    // (tiles with higher fraction of overlapping will come first)
    if (tileRanksByArea.find(1.0 - frac) == tileRanksByArea.end()) {
      std::vector<uint16_t> tiles;
      tileRanksByArea.insert(std::make_pair(1.0 - frac, tiles));
    }
    tileRanksByArea.find(1.0 - frac)->second.push_back(tileId.first);
  }
  // Sanity check that getFractionOfTileInVP is working properly.
  vpSize = vpSize * 30 * 15;
  if (vpSize <= vpArea - .1 || vpSize >= vpArea + .1) {
    LOG(ERROR) << "Fraction of tiles covering viewport"
                  " does not match with viewport true size "
               << vpSize;
  }
}

void TilePredictor::addVpCoordinate(std::pair<float, float> coordinate) {
  vpGroundTruth_[frameId_] = coordinate;
  frameId_++;
}

TilePredictor::TilePredictor(std::string vpCorrPerFrameTracePath) {
  vpGroundTruth_.reserve(2000);
  vpPredictions_.reserve(2000);
  frameId_ = 0;

  linearRegressor_ = new LinearRegression(vpCorrPerFrameTracePath);

  // fill
  uint16_t c = 1;
  for (float y = 180; y > 0; y -= 15) {
    for (float x = 0; x < 360; x += 30) {
      tileCoordinates_.insert(std::make_pair(c, std::make_pair(x, y)));
      tileResolutions_.insert(std::make_pair(c, std::make_pair(30, 15)));
      c++;
    }
  }
}

uint16_t TilePredictor::getFrameId() { return frameId_; }
