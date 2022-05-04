/*
 * LinearRegression.cpp
 *
 *  Created on: Sep 15, 2021
 *      Author: cbothra
 */
#include "LinearRegression.h"

#include <stdio.h>

#include <algorithm>
#include <fstream>
#include <functional>
#include <iostream>
#include <numeric>

#include "Util.h"

void LinearRegression::predict(
    std::vector<std::pair<float, float>> &lrPredictions,
    std::vector<std::pair<float, float>> &input, int length) {
  if (!initalized) {
    init(std::ref(input));
    initalized = true;
  }

  std::vector<float> pitchError; // for storing the pitch error values
  std::vector<float> yawError;   // for storing the yaw error values

  lrPredictions.push_back(
      std::make_pair(input[length - 1].first, input[length - 1].second));
  /*Intialization Phase*/
  for (size_t i = 1; i <= hw_; i++) {
    // Assuming the ground truth is [1,2,3,4,5,6] with 6 being most recent.
    yawInput_[hw_ - i] = input[length - i].first;
    pitchInput_[hw_ - i] = input[length - i].second;
    timeSampleInput_[i - 1] = i;
  }
  // std::cout << "=========" << std::endl;
  /*std::string yawInput = "";
  for (int i = 0; i < hw_; i++) {
    yawInput += std::to_string(yawInput_[i]) + ",";
  }
  yawInput.pop_back();*/
  // std::cout << yawInput << std::endl;
  /*Training Phase*/
  // Since there are {hw_} values in our dataset and we want to run for 4*HW
  // epochs.
  int idx;
  float pred;
  float yawErr;
  for (int i = 0; i < (4 * hw_); i++) {
    idx = i % hw_; // for accessing index after every epoch
    pred = yawB0 + yawB1 * timeSampleInput_[idx]; // making the prediction
    yawErr = pred - yawInput_[idx];               // calculating the error
    yawB0 = yawB0 - kYawAlpha_ * yawErr;          // updating b0
    yawB1 = yawB1 - kYawAlpha_ * yawErr * timeSampleInput_[idx]; // updating b1
    if (yawB1 < kLowerBound_)
      yawB1 = 0;
    if (yawB0 < kLowerBound_)
      yawB0 = 0;
    yawError.push_back(yawErr);
  }

  float pitchErr; // for calculating pitch error on each stage
  for (int i = 0; i < (4 * hw_); i++) {
    idx = i % hw_; // for accessing index after every epoch
    pred = pitchB0 + pitchB1 * timeSampleInput_[idx]; // making the prediction
    pitchErr = pred - pitchInput_[idx];               // calculating the error
    pitchB0 = pitchB0 - kPitchAlpha_ * pitchErr;      // updating b0
    pitchB1 = pitchB1 -
              kPitchAlpha_ * pitchErr * timeSampleInput_[idx]; // updating b1
    if (pitchB1 < kLowerBound_)
      pitchB1 = 0;
    if (pitchB0 < kLowerBound_)
      pitchB0 = 0;
    pitchError.push_back(pitchErr);
  }

  std::string results = "";
  for (size_t i = hw_ + 1; i < pw_ + hw_ + 1; i++) {
    float predYaw = yawB0 + yawB1 * i;
    float predPitch = pitchB0 + pitchB1 * i;

    if (predYaw > 360)
      predYaw -= int(predYaw / 360) * 360;
    if (predPitch > 180)
      predPitch -= int(predPitch / 180) * 180;
    results +=
        "(" + std::to_string(predYaw) + "," + std::to_string(predPitch) + ")--";
    lrPredictions.push_back(std::make_pair(predYaw, predPitch));
  }
  std::string frameOut = std::to_string(length) + "(" +
                         std::to_string(input[length - 1].first) + "," +
                         std::to_string(input[length - 1].second) + ")";
  fprintf(predictionLog_, "%-50s %-20s\n", frameOut.c_str(), results.c_str());
}

void LinearRegression::predictPerfect(
    std::vector<std::pair<float, float>> vpTruth, int length) {
  if (!initalized) {
    initPerfect();
    initalized = true;
  }
  std::string results = "";
  for (int i = length; i < length + 25; i++) {
    vpTruth.push_back(std::make_pair(groundTruthCoordinates_[i - 1].first,
                                     groundTruthCoordinates_[i - 1].second));
    results += "(" + std::to_string(groundTruthCoordinates_[i - 1].first) +
               "," + std::to_string(groundTruthCoordinates_[i - 1].second) +
               ")--";
  }
  std::string frameOut =
      std::to_string(length) + "(" +
      std::to_string(groundTruthCoordinates_[length - 1].first) + "," +
      std::to_string(groundTruthCoordinates_[length - 1].second) + ")";
  fprintf(predictionLog_, "%-50s %-20s\n", frameOut.c_str(), results.c_str());
}

void LinearRegression::init(std::vector<std::pair<float, float>> &input) {
  std::vector<float> yawInputDep;
  std::vector<float> pitchInputDep;
  std::vector<float> indep;
  for (int idx = 0; idx < hw_; idx++) {
    yawInputDep.push_back(input[idx].first);
    pitchInputDep.push_back(input[idx].second);
    indep.push_back(idx + 1);
  }
  float n = yawInputDep.size() * 1.0;
  auto yawMean =
      std::accumulate(yawInputDep.begin(), yawInputDep.end(), 0.0) / n;
  auto pitchMean =
      std::accumulate(pitchInputDep.begin(), pitchInputDep.end(), 0.0) / n;
  auto indepMean = std::accumulate(indep.begin(), indep.end(), 0.0) / n;

  auto indepVecMult =
      std::inner_product(indep.begin(), indep.end(), indep.begin(), 0.0);
  auto indepYawVecMult =
      std::inner_product(indep.begin(), indep.end(), yawInputDep.begin(), 0.0);
  auto indepPitchVecMult = std::inner_product(indep.begin(), indep.end(),
                                              pitchInputDep.begin(), 0.0);

  auto indepYaw = indepYawVecMult - (n * yawMean * indepMean);
  auto indepPitch = indepPitchVecMult - (n * pitchMean * indepMean);
  auto indepIndep = indepVecMult - (n * indepMean * indepMean);

  yawB1 = indepYaw / indepIndep;
  yawB0 = yawMean - (yawB1 * indepMean);

  pitchB1 = indepPitch / indepIndep;
  pitchB0 = pitchMean - (pitchB1 * indepMean);

  std::string filename = "prediction_log_" + Util::getLogTimestamp() + ".txt";
  predictionLog_ = fopen(filename.c_str(), "wb");
  fprintf(predictionLog_, "%-50s %s \n", "frame id (yaw,pitch)", "predictions");
  // std::cout << "init" << std::endl;
  // std::cout << "(yawB0,yawB1) = (" << yawB0 << "," << yawB1 << ")\n";
  // std::cout << "(pitchB0,pitchB1) = (" << pitchB0 << "," << pitchB1 << ")\n";
}

void LinearRegression::initPerfect() {
  std::string line;
  std::ifstream infile(vpCorrPerFrameTracePath_);
  while (std::getline(infile, line)) {
    auto pos = line.find(",");
    try {
      auto yaw = std::stof(line.substr(0, pos));
      auto pitch = std::stof(line.substr(pos + 1));
      groundTruthCoordinates_.push_back(std::make_pair(yaw, pitch));
    } catch (std::invalid_argument &e) {
      std::cout << "Error reading ground truth\n" << line << std::endl;
    }
  }

  std::string filename = "prediction_log_" + Util::getLogTimestamp() + ".txt";
  predictionLog_ = fopen(filename.c_str(), "wb");
  fprintf(predictionLog_, "%-50s %s \n", "frame id (yaw,pitch)", "predictions");
}

LinearRegression::LinearRegression(std::string vpCorrPerFrameTracePath,
                                   std::string model) {
  vpCorrPerFrameTracePath_ = vpCorrPerFrameTracePath;
  pw_ = model == "Pano" ? 75 : 25;
}