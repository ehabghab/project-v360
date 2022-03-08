#include "Util.h"

#include <chrono>
#include <functional>
#include <iostream>

#include <gflags/gflags.h>
#include <glog/logging.h>

long Util::videoPlayTime = getTime();
std::string Util::logTimestamp = getCurrentDateTime();
std::map<uint16_t, std::pair<float, float>> Util::tileCoordinates;
std::map<uint16_t, std::pair<float, float>> Util::tileResolutions;
std::map<std::string, std::map<float, std::vector<uint16_t>>>
    Util::corrdinatesToTilesTable;

const std::string Util::getCurrentDateTime() {
  time_t now = time(0);
  struct tm tstruct;
  char buf[80];
  tstruct = *localtime(&now);
  strftime(buf, sizeof(buf), "%Y-%m-%d_%H_%M_%S", &tstruct);
  return buf;
}

long Util::getTime() {
  return std::chrono::duration_cast<std::chrono::milliseconds>(
             std::chrono::system_clock::now().time_since_epoch())
      .count();
}

void Util::sleep(long currentTime, long millisecondsToSleep) {
  while (getTime() - currentTime < millisecondsToSleep)
    ;
}

long Util::getTimePassedSinceLastFrame() {
  auto currentTime = getTime();
  auto timeDiffInMs = currentTime - Util::videoPlayTime;
  return timeDiffInMs;
}

void Util::setFramePlayTime(long FramePlayTimeInMs) {
  Util::videoPlayTime = FramePlayTimeInMs;
}

std::string Util::getLogTimestamp() { return Util::logTimestamp; }

void Util::init() {
  uint16_t c = 1;
  for (float y = 180; y > 0; y -= 15) {
    for (float x = 0; x < 360; x += 30) {
      Util::tileCoordinates.insert(std::make_pair(c, std::make_pair(x, y)));
      Util::tileResolutions.insert(std::make_pair(c, std::make_pair(30, 15)));
      c++;
    }
  }
  // Util::constructCorrdinatesToTilesTable();
}

void Util::getViewportSquares(std::vector<SqCoordinates> &vpSquares,
                              std::pair<float, float> viewportCenter,
                              std::pair<int, int> viewportResolution) {
  // find viewport coordinates.
  float baseX1 = viewportCenter.first - (viewportResolution.first / 2.0);
  float baseX2 = viewportCenter.first + (viewportResolution.first / 2.0);

  // 0: viewport is not wrapping.
  bool horizontalFlip = false;

  // 0: viewport is not wrapping, 1: wrapping over y = 0; 2: wrapping over y =
  // 180.
  int verticalFlip = false;

  // frame in degrees [0 - 360] in width, and [0-180] in height.

  // viewport is wrapping over x = 0.
  if (baseX1 < 0) {
    baseX1 += 360;
    horizontalFlip = true;
  }

  // viewport is wrapping over x = 360.
  if (baseX2 > 360) {
    baseX2 -= 360;
    horizontalFlip = true;
  }

  float x1 = baseX1;
  float x2 = baseX2;
  float y1 = viewportCenter.second - (viewportResolution.second / 2.0);

  // viewport is wrapping over y = 0.
  if (y1 < 0) {
    y1 = y1 + 180;
    verticalFlip = true;
  }

  float x3 = baseX1;
  float x4 = baseX2;
  float y2 = viewportCenter.second + (viewportResolution.second / 2.0);

  // viewport is wrapping over y = 180.
  if (y2 > 180) {
    y2 = y2 - 180;
    verticalFlip = true;
  }

  if (!horizontalFlip && !verticalFlip) {
    // only one square.
    SqCoordinates vp = {std::make_pair(x3, y2), std::make_pair(x4, y2),
                        std::make_pair(x1, y1), std::make_pair(x2, y1)};
    vpSquares = {vp};
  } else if (!horizontalFlip && verticalFlip) {
    // viewport has two squares due to overlapping over y = 0.
    SqCoordinates vpPart1 = {
        std::make_pair(x3, y2),
        std::make_pair(x4, // @suppress("Invalid arguments")
                       y2),
        std::make_pair(x3, 0), std::make_pair(x4, 0)};

    SqCoordinates vpPart2 = {
        std::make_pair(x1, 180),
        std::make_pair(x2, // @suppress("Invalid arguments")
                       180),
        std::make_pair(x1, y1), std::make_pair(x2, y1)};
    vpSquares = {vpPart1, vpPart2};
  } else if (horizontalFlip && !verticalFlip) {
    // viewport has two squares due to overlapping over x = 0 or x = 360.
    SqCoordinates vpPart1 = {std::make_pair(0, y2), std::make_pair(x4, y2),
                             std::make_pair(0, y1), std::make_pair(x2, y1)};

    SqCoordinates vpPart2 = {std::make_pair(x3, y2), std::make_pair(360, y2),
                             std::make_pair(x1, y1), std::make_pair(360, y1)};
    vpSquares = {vpPart1, vpPart2};
  } else if (horizontalFlip && verticalFlip) {
    // viewport has three squares due to nested overlapping over x = 0 or x =
    // 360 and y = 0.

    SqCoordinates vpPart1 = {std::make_pair(0, 180), std::make_pair(x2, 180),
                             std::make_pair(0, y1), std::make_pair(x2, y1)};

    SqCoordinates vpPart2 = {std::make_pair(x1, 180), std::make_pair(360, 180),
                             std::make_pair(x1, y1), std::make_pair(360, y1)};

    SqCoordinates vpPart3 = {std::make_pair(0, y2), std::make_pair(x4, y2),
                             std::make_pair(0, 0), std::make_pair(x4, 0)};

    SqCoordinates vpPart4 = {std::make_pair(x3, y2), std::make_pair(360, y2),
                             std::make_pair(x3, 0), std::make_pair(360, 0)};
    vpSquares = {vpPart1, vpPart2, vpPart3, vpPart4};
  }
}

float Util::getFractionOfTileInVP(std::vector<SqCoordinates> &partialVPs,
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

void Util::getViewportTilesSortedByArea(
    std::map<float, std::vector<uint16_t>> &tileRanksByArea,
    std::pair<float, float> viewportCenter,
    std::pair<int, int> viewportResolution) {
  // per tile in frame get the fraction of its area that overlaps with
  // viewport.
  std::vector<SqCoordinates> vpSqrs;
  Util::getViewportSquares(std::ref(vpSqrs), viewportCenter,
                           viewportResolution);
  int vpArea = viewportResolution.first * viewportResolution.second;

  float vpSize = 0;
  for (auto const &tileId : Util::tileCoordinates) {
    float frac = getFractionOfTileInVP(std::ref(vpSqrs), tileId.second,
                                       Util::tileResolutions[tileId.first]);
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

void Util::constructCorrdinatesToTilesTable() {

  std::pair<float, float> viewportCenter;
  std::pair<int, int> viewportResolution;

  // vp classes [360-100]x[180-100] (all tiles)
  for (int vpResolutionD1 = 100; vpResolutionD1 >= 100; vpResolutionD1 -= 10) {
    for (int vpResolutionD2 = 100; vpResolutionD2 >= 100;
         vpResolutionD2 -= 10) {
      viewportResolution.first = vpResolutionD1;
      viewportResolution.second = vpResolutionD2;
      for (int y = 180; y > 0; y -= 15) {
        for (int x = 0; x < 360; x += 30) {
          std::vector<SqCoordinates> vpSquares;
          std::map<float, std::vector<uint16_t>> tileRanksByArea;
          viewportCenter.first = x;
          viewportCenter.second = y;
          Util::getViewportTilesSortedByArea(
              std::ref(tileRanksByArea), viewportCenter, viewportResolution);
          std::string key = std::to_string(x) + "_" + std::to_string(y) + "," +
                            std::to_string(vpResolutionD1) + "_" +
                            std::to_string(vpResolutionD2);
          Util::corrdinatesToTilesTable.insert(
              std::make_pair(key, tileRanksByArea));
        }
      }
    }
  }
}
