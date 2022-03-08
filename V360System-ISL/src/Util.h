/*
 * Util.h
 *
 *  Created on: Jun 6, 2021
 *      Author: eghabash
 */


#include <cstdlib>
#include <string>
#include <map>
#include <set>
#include <vector>

class Util {
  static long videoPlayTime;
  static std::string logTimestamp;
  static std::map<uint16_t, std::pair<float, float>> tileCoordinates;
  static std::map<uint16_t, std::pair<float, float>> tileResolutions;

  // key is <yaw_pitch,vp_xsize,vp_ysize> --> value: sorted tiles based on their area of overlapping.
  static std::map<std::string,std::map<float,std::vector<uint16_t>>> corrdinatesToTilesTable;

  struct SqCoordinates {
    std::pair<float, float> upperLeft;
    std::pair<float, float> upperRight;
    std::pair<float, float> lowerLeft;
    std::pair<float, float> lowerRight;
  };

  static void getViewportSquares(
    std::vector<SqCoordinates> &vpSquares,
    std::pair<float, float> viewportCenter,
    std::pair<int, int> viewportResolution);
  
  static float getFractionOfTileInVP(
    std::vector<SqCoordinates> &partialVPs,
    std::pair<float, float> tileCorrdinates,
    std::pair<float, float> tileDimensions);

  static void constructCorrdinatesToTilesTable();

public:
  static const std::string getCurrentDateTime();
  static long getTime();
  static void sleep(long currentTime, long millisecondsToSleep);
  static long getTimePassedSinceLastFrame();
  static void setFramePlayTime(long FramePlayTimeInMs);
  static std::string getLogTimestamp();
  static void init();
  static void getViewportTilesSortedByArea(
    std::map<float, std::vector<uint16_t>> &tileRanksByArea,
    std::pair<float, float> viewportCenter,std::pair<int, int> viewportResolution);
};