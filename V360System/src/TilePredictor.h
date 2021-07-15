/*
 * ABR.h
 *
 *  Created on: May 5, 2021
 *      Author: eghabash
 */

#ifndef TILEPREDICTOR_H_
#define TILEPREDICTOR_H_

#include <map>
#include <mutex>
#include <utility>
#include <vector>

class TilePredictor {
 public:
  void addVpCoordinate(std::pair<float, float> coordinate);

  // returns frameId --> tile class --> set of tiles.
  std::map<uint16_t, std::map<uint8_t, std::vector<uint16_t>>>
  getPredictedTiles();

  TilePredictor();

 private:
  struct SquareCoordinates {
    std::pair<float, float> upperLeft;
    std::pair<float, float> upperRight;
    std::pair<float, float> lowerLeft;
    std::pair<float, float> lowerRight;
  };

  // Assuming the video is only 2000 frames. otherwise,
  // increase the size of vectors.
  // ToDo use manifest to determine, based on video size and FPS.
  std::vector<std::pair<float, float>> vpPredictions_;
  std::vector<std::pair<float, float>> vpGroundTruth_;
  uint16_t frameId_;

  // TODO: build manifest to fill from.
  std::map<uint16_t, std::pair<float, float>> tileCoordinates_;
  std::map<uint16_t, std::pair<float, float>> tileResolutions_;

  /*
   * This return the viewport as input,
   * and returns it as multiple squares in case of overlapping.
   */
  void getViewportSquares(std::vector<SquareCoordinates>& vpSquares,
                          std::pair<float, float> viewportCenter,
                          std::pair<int, int> viewportResolution);

  /*
   *  This takes tile coordinates, and viewport squares as input,
   *  and returns the fraction of tile that overlap with viewport as output.
   */
  float getFractionOfTileInVP(std::vector<SquareCoordinates>& partialVPs,
                              std::pair<float, float> tileCorrdinates,
                              std::pair<float, float> tileDimensions);

  void getTileSet(std::map<float, std::vector<uint16_t>>& tileRanksByArea,
                  std::vector<SquareCoordinates>& vpSqrs, int vpArea);

  std::pair<float, float> getVpCoordinate();
};

#endif /* TILEPREDICTOR_H_ */
