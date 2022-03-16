// This is adapted from:
// https://www.analyticsvidhya.com/blog/2020/04/machine-learning-using-c-linear-logistic-regression/

/*
 * LinearRegression.h
 *
 *  Created on: Sep 15, 2021
 *      Author: cbothra
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <map>
#include <vector>

class LinearRegression {
private:
  static constexpr size_t kHW = 13;
  static constexpr size_t kPW = 25;
  static constexpr float kLowerBound_ = 1e-5;
  static constexpr float kYawAlpha_ = 0.01;   // initializing our learning rate
  static constexpr float kPitchAlpha_ = 0.01; // initializing our learning rate

  // ToDo initialize with slope function.

  float pitchB0; // initializing pitch b0
  float pitchB1; // initializing pitch b1
  float yawB0;
  float yawB1;
  bool initalized = false;

  size_t hw_{kHW};
  size_t pw_{kPW};

  float yawInput_[kHW];
  float pitchInput_[kHW];
  float timeSampleInput_[kHW];

  std::string vpCorrPerFrameTracePath_;

  FILE *predictionLog_;

  std::vector<std::pair<float, float>> groundTruthCoordinates_;

  void init(std::vector<std::pair<float, float>> &input);

  void initPerfect();

public:
  LinearRegression(std::string vpCorrPerFrameTracePath);

  /**
   * @brief It takes the histroy --half second-- of the user vp coordinates, and
   * predict where the user will be looking for the next second.
   *
   * @param @return lrPredictions: predicted 1-second of future vp coordinates
   * @param input: user coordinates as vector of pairs <yaw,pitch>.
   * @param length: this is the length of the vector (frameId)
   */
  void predict(std::vector<std::pair<float, float>> &lrPredictions,
               std::vector<std::pair<float, float>> &input, int length);

  /**
   * @brief This returns where the user will be looking without prediction
   * --ground truth--.
   *
   * @param @return ground truth future vp coordinates
   * @param length: current frame Id.
   */
  void predictPerfect(std::vector<std::pair<float, float>>, int length);
};
